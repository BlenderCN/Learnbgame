import bpy
from .. base_node_types import FunctionalNode

class CombineVectorNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_CombineVectorNode"
    bl_label = "Combine Vector"

    def create(self):
        self.new_input("en_FloatSocket", "X", "x")
        self.new_input("en_FloatSocket", "Y", "y")
        self.new_input("en_FloatSocket", "Z", "z")

        self.new_output("en_VectorSocket", "Vector", "vector")

    def get_code(self, required):
        yield "vector = mathutils.Vector((x, y, z))"