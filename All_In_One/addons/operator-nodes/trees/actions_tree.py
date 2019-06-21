import re
import bpy
from . base import NodeTree
from .. utils.code import code_to_function
from .. base_socket_types import DataFlowSocket, ControlFlowBaseSocket

from . data_flow_group import (
    iter_import_lines,
    generate_function_code,
    replace_local_identifiers
)

class ActionsTree(NodeTree, bpy.types.NodeTree):
    bl_idname = "en_ActionsTree"
    bl_icon = "PMARKER_ACT"
    bl_label = "Actions"

    def internal_data_socket_changed(self):
        pass

    def external_data_socket_changed(self):
        pass

    def print_event_code(self):
        for node in self.get_event_nodes():
            generate_action(self, node.outputs[0])

    def handle_event(self, event):
        if event.value == "PRESS":
            for node in self.graph.get_nodes_by_idname("en_KeyPressEventNode"):
                if event.type == node.key_type.upper():
                    generate_action(self, node.outputs[0])()

            for node in self.graph.get_nodes_by_idname("en_MouseClickEventNode"):
                if event.type == node.mouse_button:
                    generate_action(self, node.outputs[0])()

        if event.type == "TIMER":
            for node in self.graph.get_nodes_by_idname("en_OnUpdateEventNode"):
                generate_action(self, node.outputs[0])()


@code_to_function()
def generate_action(tree, start_socket):
    yield from iter_import_lines(tree)
    yield "def main():"
    yield "    pass"
    for line in generate_action_code(tree.graph, start_socket):
        yield "    " + line

def generate_action_code(graph, socket):
    if socket.is_output:
        linked_sockets = graph.get_linked_sockets(socket)
        if len(linked_sockets) == 1:
            yield from generate_action_code(graph, next(iter(linked_sockets)))
    else:
        node = graph.get_node_by_socket(socket)

        yield ""
        yield "#"
        yield "# " + repr(node.name)
        yield "#"

        sockets_to_calculate = {s for s in node.inputs if isinstance(s, DataFlowSocket)}
        variables = dict()
        yield from generate_function_code(graph, sockets_to_calculate, variables)

        yield ""
        yield "# Execute actual node"

        control_outputs = {s.identifier : s for s in node.outputs if isinstance(s, ControlFlowBaseSocket)}

        for line in node.get_code():
            for identifier, out_socket in control_outputs.items():
                if is_word_in_text(line, identifier):
                    indentation = " " * line.index(identifier)
                    yield indentation + "pass"
                    for next_line in generate_action_code(graph, out_socket):
                        yield indentation + next_line
                    break
            else:
                yield replace_local_identifiers(line, node, sockets_to_calculate, variables)

def is_word_in_text(text, word):
    pattern = r"\b{}\b".format(word)
    match = re.search(pattern, text)
    return match is not None