import itertools
from llvmlite import ir
import llvmlite.binding as llvm
from . utils.timing import measureTime
from . utils.nodes import iter_base_nodes_in_tree, iter_compute_node_trees
from . tree_info import iter_unlinked_inputs, get_data_origin_socket, get_nodes_by_type, get_node_by_socket, iter_all_unlinked_inputs
from pprint import pprint

class TreeExecutionData:
    '''
    As soon as one of the following things changes, an instance of this class invalidates:
        - new/removed/changed link
        - new/removed node/socket
    '''
    def __init__(self, tree):
        self.tree = tree
        self._find_interface_nodes()
        self._create_target_and_engine()
        self._create_globals_module()

        self.py_function = None
        self.compute_module = None

    def _find_interface_nodes(self):
        inputs = get_nodes_by_type(self.tree, "cn_InputNode")
        outputs = get_nodes_by_type(self.tree, "cn_OutputNode")

        if len(inputs) > 1 or len(outputs) != 1:
            raise Exception("a tree must have at most one input and exactly one output node")

        self.input_node = None if len(inputs) == 0 else inputs[0]
        self.output_node = outputs[0]

    def _create_target_and_engine(self):
        empty_module = llvm.parse_assembly("")
        llvm_target = llvm.Target.from_default_triple()
        self.target_machine = llvm_target.create_target_machine()
        self.engine = llvm.create_mcjit_compiler(empty_module, self.target_machine)

    def _create_globals_module(self):
        module_ir = self._generate_globals_module()
        self.globals_module = self._compile_ir_module(module_ir)

    def _compile_ir_module(self, ir_module):
        module = llvm.parse_assembly(str(ir_module))
        module.name = ir_module.name
        module.verify()
        self.engine.add_module(module)
        self.engine.finalize_object()

        pmb = llvm.PassManagerBuilder()
        pmb.opt_level = 0
        pm = llvm.ModulePassManager()
        pmb.populate(pm)
        #pm.add_dead_code_elimination_pass()
        pm.run(module)

        return module

    def _generate_globals_module(self):
        module_ir = ir.Module("Globals")
        for node, socket in iter_all_unlinked_inputs(self.tree):
            name = get_global_input_name(node, socket)
            variable = ir.GlobalVariable(module_ir, socket.ir_type, name)
            variable.linkage = "internal"
        return module_ir

    def get_function(self):
        if self.py_function is None:
            self.ensure_compute_module()
            address = self.engine.get_function_address("Main")

            from ctypes import CFUNCTYPE, POINTER, pointer
            output_sockets = self.get_all_output_sockets()
            input_types = [s.c_type for s in self.get_all_input_sockets()]
            output_types = [s.c_type for s in output_sockets]
            output_pointer_types = [POINTER(t) for t in output_types]

            func_type = CFUNCTYPE(None, *(input_types + output_pointer_types))
            function = func_type(address)

            def pywrapper(*args):
                if len(args) != len(input_types):
                    raise Exception("wrong argument amount")

                inputs = [t(v) for t, v in zip(input_types, args)]
                outputs = [t() for t in output_types]
                output_refs = [pointer(v) for v in outputs]
                self.update_globals()
                function(*args, *output_refs)
                results = tuple(s.value_from_cvalue(v) for v, s in zip(outputs, output_sockets))
                return results

            self.py_function = pywrapper

        return self.py_function


    def ensure_compute_module(self):
        if self.compute_module is None:
            output_amount = len(self.get_all_output_sockets())
            module = self.create_partial_compute_module([True] * output_amount)
            self.compute_module = module

    def create_partial_compute_module(self, output_mask):
        output_mask = tuple(output_mask)

        used_inputs = self.get_all_input_sockets()
        all_outputs = self.get_all_output_sockets()

        if len(output_mask) != len(all_outputs):
            raise Exception("invalid output mask")

        used_outputs = list(itertools.compress(all_outputs, output_mask))

        module_name = "module {}".format(output_mask)
        function_name = "Main"
        module_ir = generate_compute_module(module_name, function_name, used_inputs, used_outputs)
        module = self._compile_ir_module(module_ir)

        return module

    def get_all_input_sockets(self):
        return list(getattr(self.input_node, "outputs", []))

    def get_all_output_sockets(self):
        return list(self.output_node.inputs)

    def update_globals(self):
        for node, socket in iter_all_unlinked_inputs(self.tree):
            name = get_global_input_name(node, socket)
            address = self.engine.get_global_value_address(name)
            socket.update_at_address(address)

    def print_modules(self):
        print(self.globals_module)
        print(self.compute_module)

    def print_module_assembly(self):
        print(self.target_machine.emit_assembly(self.compute_module))


def generate_compute_module(module_name, function_name, input_sockets, output_sockets):
    assert len(output_sockets) > 0

    module = ir.Module(module_name)

    input_types = [s.ir_type for s in input_sockets]
    output_pointer_types = [s.ir_type.as_pointer() for s in output_sockets]
    function_type = ir.FunctionType(ir.VoidType(), input_types + output_pointer_types)

    function = ir.Function(module, function_type, name = function_name)
    input_args = function.args[:len(input_types)]
    output_args = function.args[len(input_types):]

    block = function.append_basic_block("entry")
    builder = ir.IRBuilder(block)

    input_vregisters = {}
    tree = output_sockets[0].id_data
    for node, socket in iter_all_unlinked_inputs(tree):
        name = get_global_input_name(node, socket)
        source_variable = ir.GlobalVariable(module, socket.ir_type, name)
        source_variable.linkage = "available_externally"
        vregister = builder.load(source_variable)
        input_vregisters[socket] = vregister

    for socket, vregister in zip(input_sockets, input_args):
        input_vregisters[socket] = vregister

    outputs = generate_function_code(builder, input_vregisters, output_sockets)
    for vregister, pointer_vregister in zip(outputs, output_args):
        builder.store(vregister, pointer_vregister)

    builder.ret_void()

    return module


def generate_function_code(builder, input_vregisters, required_sockets):
    vregisters = dict()
    vregisters.update(input_vregisters)

    for socket in required_sockets:
        builder = insert_code_to_calculate_socket(socket, builder, vregisters)

    outputs = [vregisters[s] for s in required_sockets]
    return outputs

def insert_code_to_calculate_socket(socket, builder, vregisters):
    if socket in vregisters:
        return builder

    if socket.is_output:
        node = get_node_by_socket(socket)
        for input_socket in node.inputs:
            builder = insert_code_to_calculate_socket(input_socket, builder, vregisters)

        input_vregisters = [vregisters[s] for s in node.inputs]
        builder, *output_vregisters = node.create_llvm_ir(builder, *input_vregisters)

        for socket, vregister in zip(node.outputs, output_vregisters):
            vregisters[socket] = vregister
    else:
        origin_socket = get_data_origin_socket(socket)
        builder = insert_code_to_calculate_socket(origin_socket, builder, vregisters)
        vregisters[socket] = vregisters[origin_socket]

    return builder


def get_global_input_name(node, socket):
    return validify_name(node.name) + " - " + validify_name(socket.identifier)

def validify_name(name):
    return name.replace('"', "")
