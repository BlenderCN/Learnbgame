import re
import bpy
from . base import NodeTree
from functools import lru_cache
from collections import defaultdict
from .. utils.code import code_to_function
from .. base_socket_types import ExternalDataFlowSocket

function_by_tree = {}

class FunctionDataCache:
    def __init__(self):
        self.function = None
        self.signature = None
        self.property_state = 0
        self.reset_dependencies()

    def reset_dependencies(self):
        self.dependencies = dict()

cache = defaultdict(FunctionDataCache)

class DataFlowGroupTree(NodeTree, bpy.types.NodeTree):
    bl_idname = "en_DataFlowGroupTree"
    bl_icon = "MOD_DATA_TRANSFER"
    bl_label = "Data Flow Group"

    def update(self):
        super().update()
        self.reset_cache()

    def internal_data_socket_changed(self):
        pass

    def external_data_socket_changed(self):
        self.cache.reset_dependencies()

    @property
    def is_valid_function(self):
        if self.graph.count_idname("en_GroupInputNode") > 1:
            return False
        if self.graph.count_idname("en_GroupOutputNode") != 1:
            return False
        return True

    @property
    def input_node(self):
        nodes = self.graph.get_nodes_by_idname("en_GroupInputNode")
        if len(nodes) == 0:
            return None
        elif len(nodes) == 1:
            return nodes[0]
        else:
            raise Exception("there is more than one input node")

    @property
    def output_node(self):
        nodes = self.graph.get_nodes_by_idname("en_GroupOutputNode")
        if len(nodes) == 0:
            return None
        elif len(nodes) == 1:
            return nodes[0]
        else:
            raise Exception("there is more than one output node")

    @property
    def cache(self):
        return cache[self]

    @property
    def signature(self):
        if self.cache.signature is None:
            input_node = self.input_node
            if input_node is None:
                inputs = []
            else:
                inputs = list(input_node.outputs)
            outputs = list(self.output_node.inputs)
            self.cache.signature = FunctionSignature(inputs, outputs)
        return self.cache.signature

    @property
    def function(self):
        if not self.is_valid_function:
            raise Exception("the node tree is in an invalid state")
        if self.cache.function is None:
            self.cache.function = generate_function(self)
        return self.cache.function

    def reset_cache(self):
        if self in cache:
            del cache[self]

    def get_dependencies(self, external_inputs):
        key = str(external_inputs)
        if key not in self.cache.dependencies:
            signature = self.signature

            possible_external_values = {socket : {value} for socket, value in external_inputs.items()}
            find_possible_external_values(self.graph, possible_external_values)

            required_sockets = find_required_sockets(self.graph, signature.inputs, signature.outputs)
            dependencies = find_dependencies(self.graph, required_sockets, possible_external_values, signature.inputs, signature.outputs)
            self.cache.dependencies[key] = dependencies
        return self.cache.dependencies[key]

class FunctionSignature:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        in_names = [socket.data_type for socket in self.inputs]
        out_names = [socket.data_type for socket in self.outputs]
        return "<In: ({}), Out: ({})>".format(
            ", ".join(in_names), ", ".join(out_names)
        )

    def match_input(self, pattern):
        if len(pattern) != len(self.inputs):
            return False
        return all(s.data_type == t for s, t in zip(self.inputs, pattern))

    def match_output(self, pattern):
        if len(pattern) != len(self.outputs):
            return False
        return all(s.data_type == t for s, t in zip(self.outputs, pattern))

@code_to_function()
def generate_function(tree):
    yield from iter_import_lines(tree)
    signature = tree.signature

    variables = {}
    for i, socket in enumerate(signature.inputs):
        variables[socket] = "input_" + str(i)

    input_string = ", ".join(variables[socket] for socket in signature.inputs)
    yield f"def main({input_string}):"

    for line in generate_function_code(tree.graph, signature.outputs, variables):
        yield "    " + line

    output_string = ", ".join(variables[socket] for socket in signature.outputs)
    yield "    return " + output_string

def iter_import_lines(tree):
    yield "import bpy, mathutils, random, math"
    yield f"nodes = bpy.data.node_groups[{repr(tree.name)}].nodes"

def find_possible_external_values(graph, values):
    def find_possible_values(socket):
        if socket in values:
            return
        if not isinstance(socket, ExternalDataFlowSocket):
            return

        if socket.is_output:
            node = graph.get_node_by_socket(socket)
            for input_socket in node.inputs:
                if isinstance(input_socket, ExternalDataFlowSocket):
                    find_possible_values(input_socket)
            values.update(node.execute_external(values))
        else:
            linked_sockets = graph.get_linked_sockets(socket)
            if len(linked_sockets) == 0:
                values[socket] = {socket.get_value()}
            elif len(linked_sockets) == 1:
                source_socket = next(iter(linked_sockets))
                find_possible_values(source_socket)
                values[socket] = values[source_socket]

    for node in graph.iter_nodes():
        for socket in node.sockets:
            find_possible_values(socket)

def find_dependencies(graph, required_sockets, external_values, input_sockets, output_sockets):
    dependencies = set()
    found_sockets = set(input_sockets)

    def find_for(socket):
        if socket in found_sockets:
            return
        found_sockets.add(socket)

        if socket.is_output:
            node = graph.get_node_by_socket(socket)
            dependencies.update(node.get_external_dependencies(external_values, required_sockets))
            for input_socket in node.inputs:
                find_for(input_socket)
        else:
            linked_sockets = graph.get_linked_sockets(socket)
            if len(linked_sockets) == 0:
                dependencies.update(socket.get_dependencies())
            elif len(linked_sockets) == 1:
                find_for(next(iter(linked_sockets)))

    for socket in output_sockets:
        find_for(socket)

    return dependencies

def find_required_sockets(graph, input_sockets, output_sockets):
    required_sockets = set()

    def find_for(socket):
        if socket in required_sockets:
            return
        required_sockets.add(socket)

        if socket in input_sockets:
            return

        if socket.is_output:
            node = graph.get_node_by_socket(socket)
            for input_socket in node.get_required_inputs([socket]):
                find_for(input_socket)
        else:
            for linked_socket in graph.get_linked_sockets(socket):
                find_for(linked_socket)

    for socket in output_sockets:
        find_for(socket)

    return required_sockets

def generate_function_code(graph, sockets_to_calculate, variables):
    required_sockets = find_required_sockets(graph, set(), sockets_to_calculate)
    yield from _generate_function_code(graph, sockets_to_calculate, variables, required_sockets)


def _generate_function_code(graph, output_sockets, variables, required_sockets):
    def calculate_socket(socket):
        if socket in variables:
            return

        if socket.is_output:
            node = graph.get_node_by_socket(socket)

            for input_socket in node.inputs:
                yield from calculate_socket(input_socket)

            for output_socket in node.outputs:
                variables[output_socket] = get_new_socket_name(graph, output_socket)

            yield ""
            yield "# " + repr(node.name)
            for line in node.get_code(required_sockets):
                yield replace_local_identifiers(line, node, node.sockets, variables)
        else:
            linked_sockets = graph.get_linked_sockets(socket)
            if len(linked_sockets) == 0:
                yield from generate_unlinked_input_code(graph, socket, variables)
            elif len(linked_sockets) == 1:
                source_socket = next(iter(linked_sockets))
                yield from calculate_socket(source_socket)
                variables[socket] = variables[source_socket]

    for socket in output_sockets:
        yield from calculate_socket(socket)

def generate_unlinked_input_code(graph, socket, variables):
    name = get_new_socket_name(graph, socket)
    node = graph.get_node_by_socket(socket)
    variables[socket] = name
    yield "{} = nodes['{}'].inputs[{}].get_value()".format(
        name, node.name, socket.get_index(node)
    )

def generate_self_expression(node):
    return f"nodes[{repr(node.name)}]"

def replace_local_identifiers(code, node, sockets, variables):
    for socket in sockets:
        code = replace_variable_name(code, socket.identifier, variables[socket])
    code = replace_variable_name(code, "self", generate_self_expression(node))
    return code

counter = 0

def get_new_socket_name(graph, socket):
    global counter
    counter += 1
    return "_" + str(counter)

@lru_cache(maxsize = 2**15)
def replace_variable_name(code, oldName, newName):
    pattern = r"([^\.\"']|^)\b{}\b".format(oldName)
    return re.sub(pattern, r"\1{}".format(newName), code)