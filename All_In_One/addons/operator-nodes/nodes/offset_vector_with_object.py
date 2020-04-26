import bpy
from bpy.props import *
from .. base_node_types import FunctionalNode
from .. dependencies import AttributeDependency

class OffsetVectorWithObjectNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_OffsetVectorWithObjectNode"
    bl_label = "Offset Vector With Object"

    offset_object: PointerProperty(type = bpy.types.Object)

    def create(self):
        self.new_input("en_VectorSocket", "Vector", "vector_in")
        self.new_output("en_VectorSocket", "Vector", "vector_out")

    def draw(self, layout):
        layout.prop(self, "offset_object", text = "")

    def get_code(self, required):
        yield "vector_out = self.execute(vector_in)"

    def execute(self, vector):
        if self.offset_object is None:
            return vector.copy()
        else:
            return vector + self.offset_object.location

    def get_external_dependencies(self, external_values, required):
        if self.offset_object is not None:
            yield AttributeDependency(self.offset_object, "location")