import bpy
from bpy.props import *
from .. base_node_types import FunctionalNode

operator_items = [
    ("ADD", "Add", ""),
    ("MULTIPLY", "Multiply", "element-wise multiplication")
]

class VectorMathNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_VectorMathNode"
    bl_label = "Vector Math"

    operator: EnumProperty(name = "Operator", default = "ADD",
        items = operator_items, update = FunctionalNode.code_changed)

    def create(self):
        self.new_input("en_VectorSocket", "A", "a")
        self.new_input("en_VectorSocket", "B", "b")
        self.new_output("en_VectorSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operator", text = "")

    def get_code(self, required):
        if self.operator == "ADD":
            yield "result = a + b"
        elif self.operator == "MULTIPLY":
            yield "result = mathutils.Vector((a.x*b.x, a.y*b.y, a.z*b.z))"