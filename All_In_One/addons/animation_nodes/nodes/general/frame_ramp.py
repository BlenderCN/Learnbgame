import bpy
from bpy.props import *
from math import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class frameRampNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_frameRampNode"
    bl_label = "Frame Ramp"
    bl_width_default = 200

    message1 = StringProperty("")
    useEX = BoolProperty(name = "Expo Function", default = False, update = propertyChanged)
    exp_v = IntProperty(name = "Exp Factor", default = 0, min = 1, max = 10)

    def create(self):
        self.newInput("Float", "Input Value", "inp_v",minValue = 0,maxValue = 1)
        self.newInput("Integer", "Start Frame", "frm_s",minValue = 10)
        self.newInput("Integer", "End Frame", "frm_e",minValue = 20)
        self.newOutput("Float", "Output Value", "out_v")

    def draw(self,layout):
        layout.prop(self, "useEX")
        layout.prop(self, "exp_v")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self, inp_v, frm_s, frm_e):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        self.message1 = ""
        rng_v = frm_e - frm_s
        frm_c = bpy.context.scene.frame_current
        if frm_c >= frm_s:
            if inp_v == 1:
                out_v = 1 - ((frm_c - frm_s) / rng_v)
                if out_v < 0:
                    out_v = 0
                else:
                    if self.useEX:
                        for i in range(0,self.exp_v):
                            out_v = (exp(out_v) -  1 ) / (exp(1) - 1)
            elif inp_v == 0:
                out_v = 0 + ((frm_c - frm_s) / rng_v)
                if out_v > 1:
                    out_v = 1
                else:
                    if self.useEX:
                        for i in range(0,self.exp_v):
                            out_v = (exp(out_v) -  1 ) / (exp(1) - 1)
            else:
                out_v = 0
        else:
            if inp_v == 0:
                out_v = 0
            elif inp_v == 1:
                out_v = 1
            else:
                out_v = inp_v

        return out_v
