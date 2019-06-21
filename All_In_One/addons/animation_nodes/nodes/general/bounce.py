import bpy
from bpy.props import *
from math import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class bounceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_bounceNode"
    bl_label = "Bounce Generator"
    bl_width_default = 200

    frm_s = IntProperty(name = "Start Frame", default = 2, min = 2)
    frm_e = IntProperty(name = "End Frame", default = 10, min = 10)
    speed = FloatProperty(name = "Cycle Speed", default = 4, min = 4)
    spd_d = FloatProperty(name = "Speed Decay Factor", default = 1, precision = 3, min = 0.8, max = 1)
    spd_v = FloatProperty(name = "Compute Factor", default = 1, precision = 2)
    hgt_s = FloatProperty(name = "Start Height", default = 1)
    hgt_b = FloatProperty(name = "Base Height",default = 0)
    message1 = StringProperty("")

    def create(self):
        self.newOutput("Float", "Output Height", "cos_w")

    def draw(self, layout):
        layout.prop(self, "frm_s")
        layout.prop(self, "frm_e")
        layout.prop(self, "speed")
        layout.prop(self, "spd_d")
        layout.prop(self, "hgt_s")
        layout.prop(self, "hgt_b")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        frm_c = bpy.context.scene.frame_current
        if self.hgt_s <= (self.hgt_b + 0.1):
            self.message1 = "Height Errors!"
            cos_w = 0
        elif self.frm_s <= bpy.context.scene.frame_start:
            self.message1 = "Start Frame Error!"
            cos_w = 0
        else:
            self.message1 = ""
            len_m = self.frm_e - self.frm_s
            if frm_c == (self.frm_s - 1):
                self.spd_v = self.speed
            if frm_c >= self.frm_s and frm_c <= self.frm_e:
                if self.spd_d == 1:
                    speed = self.speed
                else:
                    speed = self.spd_v
                    if speed <= 4:
                        speed = 4
                fac_m = len_m - (frm_c - self.frm_s)
                cos_w = abs(cos((frm_c - self.frm_s) * 2 * pi / (speed * 2)))
                cos_w = (cos_w * fac_m * self.hgt_s / (self.frm_e - self.frm_s)) + self.hgt_b
                self.spd_v = self.spd_v * (0.99 + (self.spd_d / 100))
            elif frm_c < self.frm_s:
                cos_w = self.hgt_s + self.hgt_b
            else:
                cos_w = self.hgt_b

        return cos_w
