import bpy
from .. base_node_types import FunctionalNode
from .. dependencies import AttributeDependency

class ObjectTransformsNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_ObjectTransformsNode"
    bl_label = "Object Transforms"

    def create(self):
        self.new_input("en_ObjectSocket", "Object", "object")
        self.new_output("en_VectorSocket", "Location", "location")
        self.new_output("en_VectorSocket", "Scale", "scale")

    def get_code(self, required):
        needsLocation = self.outputs["Location"] in required
        needsScale = self.outputs["Scale"] in required
        if not any((needsLocation, needsScale)):
            return

        yield "if object is None:"
        if needsLocation: yield "    location = mathutils.Vector((0, 0, 0))"
        if needsScale:    yield "    scale = mathutils.Vector((1, 1, 1))"
        yield "else:"
        if needsLocation: yield "    location = object.location.copy()"
        if needsScale:    yield "    scale = object.scale.copy()"

    def get_external_dependencies(self, external_values, required):
        for object in external_values[self.inputs[0]]:
            if object is None:
                continue
            if self.outputs["Location"] in required:
                yield AttributeDependency(object, "location")
            if self.outputs["Scale"] in required:
                yield AttributeDependency(object, "scale")