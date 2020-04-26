import bpy
from .. base_node_types import FunctionalNode

class GetObjectParentNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_GetObjectParentNode"
    bl_label = "Get Object Parent"

    def create(self):
        self.new_input("en_ObjectSocket", "Object", "object")
        self.new_output("en_ObjectSocket", "Object", "parent")

    def get_code(self, required):
        yield "parent = object.parent if object is not None else None"

    def execute_external(self, possible_values_per_socket):
        possible_outputs = set()
        for object in possible_values_per_socket[self.inputs[0]]:
            possible_outputs.add(object.parent if object is not None else None)
        return {self.outputs[0] : possible_outputs}