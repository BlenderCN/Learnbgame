import os
import bpy
import bge_netlogic
from bge_netlogic.ops.file_text_buffer import FileTextBuffer
from bge_netlogic.ops.uid_map import UIDMap

class TreeCodeGenerator(object):
    def get_netlogic_module_for_node(self, node):
        try:
            netlogic_class = node.get_netlogic_class_name()
            lastdot = netlogic_class.rfind(".")
            if lastdot < 0: return None#assuming basicnodes
            return netlogic_class[0:lastdot]
        except AttributeError:
            print("Not a netlogic node", node)
            return None
        pass

    def list_user_modules_needed_by_tree(self, tree):
        result = set()
        for node in tree.nodes:
            module_name = self.get_netlogic_module_for_node(node)
            if module_name is not None:#if none assume is one in bgelogic.py
                if module_name != "bgelogic":
                    result.add(module_name)
        return result

    def create_text_file(self, buffer_name):
        file_path = bpy.path.abspath("//{}".format(buffer_name))
        return FileTextBuffer(file_path)

    def write_code_for_tree(self, tree):
        buffer_name = bge_netlogic.utilities.py_module_filename_for_tree(tree)
        print("Updating tree code...", buffer_name)
        line_writer = self.create_text_file("bgelogic/"+buffer_name)
        line_writer.write_line("#MACHINE GENERATED")
        line_writer.write_line("import bge")
        line_writer.write_line("import mathutils")
        line_writer.write_line("import bgelogic")
        line_writer.write_line("import math")
        user_modules = self.list_user_modules_needed_by_tree(tree)
        for module in user_modules:
            line_writer.write_line('{} = bgelogic.load_user_logic("{}")', module, module)
        line_writer.write_line("")
        line_writer.write_line("def _initialize(owner):")
        line_writer.set_indent_level(1)
        line_writer.write_line("network = bgelogic.LogicNetwork()")
        cell_var_names, uid_map = self._write_tree(tree, line_writer)
        for varname in self._sort_cellvarnames(cell_var_names, uid_map):
            if not uid_map.is_removed(varname): line_writer.write_line("network.add_cell({})", varname)
        line_writer.write_line('owner["{}"] = network', tree.name)
        line_writer.write_line("network._owner = owner")
        line_writer.write_line("network.setup()")
        line_writer.write_line("network.stopped = not owner.get('{}')", bge_netlogic.utilities.get_key_network_initial_status_for_tree(tree))
        line_writer.write_line("return network")
        line_writer.set_indent_level(0)
        line_writer.write_line("")
        line_writer.write_line("def pulse_network(controller):")
        line_writer.set_indent_level(1)
        line_writer.write_line("owner = controller.owner")
        line_writer.write_line('network = owner.get("{}")', tree.name)
        line_writer.write_line("if network is None:")
        line_writer.set_indent_level(2)
        line_writer.write_line("network = _initialize(owner)")
        line_writer.set_indent_level(1)
        line_writer.write_line("if network.stopped: return")
        line_writer.write_line("shutdown = network.evaluate()")
        line_writer.write_line("if shutdown is True:")
        line_writer.set_indent_level(2)
        line_writer.write_line("controller.sensors[0].repeat = False")
        line_writer.close()
        #write the bgelogic.py module source in the directory of the current blender file
        this_module_dir = os.path.dirname(__file__)
        bge_netlogic_dir = os.path.dirname(this_module_dir)
        game_dir = os.path.join(bge_netlogic_dir, "game")
        bgelogic_input_file = os.path.join(game_dir, "bgelogic.py")
        bgelogic_source_code = None
        with open(bgelogic_input_file, "r") as f:
            bgelogic_source_code = f.read()
        assert (bgelogic_source_code is not None)
        bgelogic_output_writer = self.create_text_file("bgelogic/__init__.py")
        bgelogic_output_writer.write_line("#MACHINE GENERATED")
        bgelogic_output_writer.write_line(bgelogic_source_code)
        bgelogic_output_writer.close()
        pass

    def _write_tree(self, tree, line_writer):
        uid_map = UIDMap()
        cell_uid = 0
        node_cellvar_list = []
        for node in tree.nodes:
            prefix = None
            if not isinstance(node, bge_netlogic.basicnodes.NetLogicStatementGenerator):
                print("Skipping TreeNode of type {} because it is not an instance of NetLogicStatementGenerator".format(node.__class__.__name__))
                continue
            if isinstance(node, bge_netlogic.basicnodes.NLActionNode):
                prefix = "ACT"
            elif isinstance(node, bge_netlogic.basicnodes.NLConditionNode):
                prefix = "CON"
            elif isinstance(node, bge_netlogic.basicnodes.NLParameterNode):
                prefix = "PAR"
            else:
                raise ValueError(
                        "netlogic node {} must extend one of NLActionNode, NLConditionNode or NLParameterNode".format(
                                node.__class__.__name__))
            varname = "{0}{1:04d}".format(prefix, cell_uid)
            uid_map._register(varname, cell_uid, node)
            node.write_cell_declaration(varname, line_writer)
            cell_uid += 1
        for uid in range(0, cell_uid):
            tree_node = uid_map._get_node_for_uid(uid)
            cell_varname = uid_map._get_varname_for_uid(uid)
            tree_node.write_cell_fields_initialization(cell_varname, uid_map, line_writer)
        return uid_map._list_cell_names(), uid_map

    def _sort_cellvarnames(self, node_cellvar_list, uid_map):
        #sorting is effective only in serial execution context. Because the python vm is basically a serial only
        #machine, we force a potentially parallel network to work as a serial one. Shame on GIL.
        available_cells = list(node_cellvar_list)
        added_cells = []
        while available_cells:
            for cell_name in available_cells:
                node = uid_map.get_node_for_varname(cell_name)
                #if all the links of node are either constant or cells in added_cells, then this node can be put in the list
                if self._test_node_links(node, added_cells, uid_map):
                    available_cells.remove(cell_name)
                    added_cells.append(cell_name)
                else:
                    pass
        return added_cells

    def _test_node_links(self, node, added_cell_names, uid_map):
        for input in node.inputs:
            if input.is_linked:
                linked_node = input.links[0].from_socket.node
                linked_node_varname = uid_map.get_varname_for_node(linked_node)
                if not (linked_node_varname in added_cell_names): return False#node is linked to a cell that has not been resolved
                pass
        #all inputs are constant expressions or linked to resolved cells
        return True
    pass