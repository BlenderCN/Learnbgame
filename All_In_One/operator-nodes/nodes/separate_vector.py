import bpy
from .. base_node_types import FunctionalNode

class SeparateVectorNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_SeparateVectorNode"
    bl_label = "Separate Vector"

    def create(self):
        self.new_input("en_VectorSocket", "Vector", "vector")

        self.new_output("en_FloatSocket", "X", "x")
        self.new_output("en_FloatSocket", "Y", "y")
        self.new_output("en_FloatSocket", "Z", "z")

    def get_code(self, required):
        yield "x, y, z = vector"