import bpy
from bpy.props import *
from .. base_node_types import DeclarativeNode

class KeyPressEventNode(DeclarativeNode, bpy.types.Node):
    bl_idname = "en_KeyPressEventNode"
    bl_label = "Key Press Event"

    key_type: StringProperty(name = "Key Type", default = "W")

    def create(self):
        self.new_output("en_ControlFlowSocket", "Next")

    def draw(self, layout):
        layout.prop(self, "key_type", text = "")