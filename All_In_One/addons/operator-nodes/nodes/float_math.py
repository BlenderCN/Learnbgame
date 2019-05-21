import bpy
from bpy.props import *
from .. base_node_types import FunctionalNode

operator_items = [
    ("ADD", "Add", ""),
    ("MULTIPLY", "Multiply", "")
]

class FloatMathNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_FloatMathNode"
    bl_label = "Float Math"

    operator: EnumProperty(name = "Operator", default = "ADD",
        items = operator_items, update = FunctionalNode.code_changed)

    def create(self):
        self.new_input("en_FloatSocket", "A", "a")
        self.new_input("en_FloatSocket", "B", "b")
        self.new_output("en_FloatSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operator", text = "")

    def get_code(self, required):
        if self.operator == "ADD":
            yield "result = a + b"
        elif self.operator == "MULTIPLY":
            yield "result = a * b"