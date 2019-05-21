import bpy
from .. base_node_types import ImperativeNode

class RotateViewNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_RotateViewNode"
    bl_label = "Rotate View"

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        self.new_input("en_FloatSocket", "Angle", "angle")

        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def get_code(self):
        yield "bpy.context.space_data.region_3d.view_rotation.rotate(mathutils.Euler((0, 0, angle)))"
        yield "NEXT"