import bpy
from .. base_node_types import DeclarativeNode

class GroupInputNode(DeclarativeNode, bpy.types.Node):
    bl_idname = "en_GroupInputNode"
    bl_label = "Group Input"

    def draw(self, layout):
        self.invoke_socket_type_chooser(layout, "add_socket", "Add")

    def add_socket(self, idname):
        self.new_output(idname, idname)