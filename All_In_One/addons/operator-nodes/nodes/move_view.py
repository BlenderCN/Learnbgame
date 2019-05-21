import bpy
from .. base_node_types import ImperativeNode

class MoveViewNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_MoveViewNode"
    bl_label = "Move View"

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        self.new_input("en_VectorSocket", "Offset", "offset")

        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def get_code(self):
        yield "bpy.context.space_data.region_3d.view_location += offset"
        yield "NEXT"