import bpy
from .. base_node_types import DeclarativeNode

class GroupOutputNode(DeclarativeNode, bpy.types.Node):
    bl_idname = "en_GroupOutputNode"
    bl_label = "Group Output"

    def draw(self, layout):
        self.invoke_socket_type_chooser(layout, "add_socket", "Add")

    def add_socket(self, idname):
        self.new_input(idname, idname)