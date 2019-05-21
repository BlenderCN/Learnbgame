import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class triggerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_triggerNode"
    bl_label = "Periodic Trigger"
    bl_width_default = 150

    def create(self):
        self.newInput("Integer", "Cycle Length", "cycLen", minValue = 1)
        self.newInput("Integer", "Phase", "offset", minvalue = 0)
        self.newOutput("Boolean", "Process", "condition")

    def execute(self, cycLen, offset):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if offset >= cycLen:
            offset = offset % cycLen
        return bpy.context.scene.frame_current % cycLen == offset
