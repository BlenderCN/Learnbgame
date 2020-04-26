import bpy
from bpy.props import *
from ... base_types import AnimationNode

class sequenceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_sequenceNode"
    bl_label = "Multi-Channel Sequencer"
    bl_width_default = 180

    message1 = StringProperty("")

    def create(self):
        self.newInput("Integer", "Start Frame", "start")
        self.newInput("Integer", "End Frame", "endf")
        self.newInput("Integer", "Number of Steps", "st_n")
        self.newInput("Float", "Step Value", "step")
        self.newOutput("Integer List", "Output as IntegerList", "out_l")
        self.newOutput("Integer", "Current Pulse Index", "idx")

    def draw(self,layout):
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self, start, endf, st_n, step):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        frame = bpy.context.scene.frame_current

        if endf < (start + (step * st_n)) or step < 0.01 or st_n < 2:
            self.message1 = "Check Input Values"
            out_l = None
            idx = None
        else:
            self.message1 = ""
            out_l = []
            idx = 0
            for i in range(0,st_n):
                out_l.append(0)

            if frame in range(start,endf):
                frm = (frame - start) % (step * st_n)
                idx = int(frm // step)
                out_l[idx] = step

        return out_l, idx
