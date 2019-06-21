import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class speedAccNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_speedAccNode"
    bl_label = "Object Speed & Acceleration"
    bl_width_default = 180

    message1 = StringProperty("")
    mod_g = BoolProperty(name = "Metric Units", default = True, update = propertyChanged)

    def create(self):
        self.newInput("Integer", "Decimal Places", "dec_n")
        self.newInput("Float", "Current", "loc_c")
        self.newInput("Float", "Frame - 1", "loc_o")
        self.newInput("Float", "Frame - 2", "loc_t")
        self.newOutput("Float", "Speed units/sec", "spd_u")
        self.newOutput("Float", "Acceleration units/sec/sec", "acc_u")
        self.newOutput("Float", "Acceleration - g", "acc_g")

    def draw(self,layout):
        layout.prop(self, "mod_g")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self, dec_n, loc_c, loc_o, loc_t):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        fps = bpy.context.scene.render.fps
        if loc_c == 0 and loc_o == 0 and loc_t ==0:
            spd_u = 0
            acc_u = 0
            acc_g = 0
        else:
            spd_c = abs(loc_c - loc_o) * fps
            spd_o = abs(loc_o - loc_t) * fps
            acc_u = round((spd_c - spd_o) * fps,dec_n)
            spd_u = round(spd_c,dec_n)
        if self.mod_g:
            acc_g = round(acc_u / 9.81,dec_n)
        else:
            acc_g = round(acc_u / 32,dec_n)

        return spd_u, acc_u, acc_g
