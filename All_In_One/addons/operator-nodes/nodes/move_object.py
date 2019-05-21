import bpy
from bpy.props import *
from .. base_node_types import ImperativeNode

class MoveObjectNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_MoveObjectNode"
    bl_label = "Move Object"

    local_axis: BoolProperty(name = "Local Axis", default = False,
        update = ImperativeNode.code_changed)

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        self.new_input("en_ObjectSocket", "Object", "object")
        self.new_input("en_VectorSocket", "Offset", "offset")

        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def draw(self, layout):
        layout.prop(self, "local_axis")

    def get_code(self):
        yield "if object is not None:"
        if self.local_axis:
            yield "    object.location += object.rotation_euler.to_matrix() * offset"
        else:
            yield "    object.location += offset"
        yield "NEXT"