import bpy
from bpy.props import *
from ... base_types import AnimationNode

class tankSuspensionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_tankSuspensionNode"
    bl_label = "Suspension Wheel Tracker"
    bl_width_default = 200

    message1 = StringProperty("")
    message2 = StringProperty("")

    def create(self):
        self.newInput("Object", "Wheel Control", "wheel")
        self.newInput("Float", "Height Offset", "z_off")
        self.newInput("Float", "Shrink Height", "s_high")
        self.newInput("Float", "Fix Longitudinal", "f_long")
        self.newInput("Float", "Fix Height", "base_h")
        self.newInput("Float", "Trip Value", "max_v")

    def draw(self, layout):
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")
        if (self.message2 != ""):
            layout.label(self.message2, icon = "ERROR")

    def execute(self, wheel, z_off, s_high, f_long, base_h, max_v):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if wheel is None or max_v == 0:
            self.message2 = 'Set Parameters'
        else:
            self.message2 = ''
            if z_off < -max_v:
                wheel.location.x = f_long
                wheel.location.z = (base_h - max_v)
            else:
                wheel.location.x = f_long
                wheel.location.z = s_high
