import bpy
from bpy.props import *
from .. base_node_types import DeclarativeNode

mouse_button_items = [
    ("LEFTMOUSE", "Left", ""),
    ("RIGHTMOUSE", "Right", "")
]

class MouseClickEventNode(DeclarativeNode, bpy.types.Node):
    bl_idname = "en_MouseClickEventNode"
    bl_label = "Mouse Click Event"

    mouse_button: EnumProperty(name = "Mouse Button", default = "LEFTMOUSE",
        items = mouse_button_items)

    def create(self):
        self.new_output("en_ControlFlowSocket", "Next")

    def draw(self, layout):
        layout.prop(self, "mouse_button", text = "")