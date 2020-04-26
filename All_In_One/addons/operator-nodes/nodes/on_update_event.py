import bpy
from bpy.props import *
from .. base_node_types import DeclarativeNode

class OnUpdateEventNode(DeclarativeNode, bpy.types.Node):
    bl_idname = "en_OnUpdateEventNode"
    bl_label = "On Update Event"

    def create(self):
        self.new_output("en_ControlFlowSocket", "Next")