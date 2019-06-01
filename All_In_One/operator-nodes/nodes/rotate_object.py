import bpy
from bpy.props import *
from .. base_node_types import ImperativeNode

axis_items = [
    ("X", "X", ""),
    ("Y", "Y", ""),
    ("Z", "Z", "")
]

class RotateObjectNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_RotateObjectNode"
    bl_label = "Rotate Object"

    axis: EnumProperty(name = "Axis", default = "Z",
        items = axis_items, update = ImperativeNode.code_changed)

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        self.new_input("en_ObjectSocket", "Object", "object")
        self.new_input("en_FloatSocket", "Angle", "angle")

        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def draw(self, layout):
        layout.prop(self, "axis")

    def get_code(self):
        yield "if object is not None:"
        yield "    object.rotation_euler.{} += angle".format(self.axis.lower())
        yield "NEXT"