import bpy
from bpy.props import *
from math import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class tickingSecondsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_tickingSecondsNode"
    bl_label = "Maths Functions Node"
    bl_width_default = 220

    tick = IntProperty()
    tic_t = FloatProperty(name = "Tick Speed (sec)", default = 1, min = 0.01)
    Speed = FloatProperty(name = "Speed (fpc)", default = 1, min = 1)
    Amplitude = FloatProperty(default = 1, min = 0.01)
    sin_w = FloatProperty()
    cos_w = FloatProperty()
    tan_w = FloatProperty()
    pul_s = FloatProperty()
    pul_c = FloatProperty()
    pul_a = FloatProperty(name = "Pulse Trigger", default = 0.95, min = 0.001)
    trig = BoolProperty(name = "Produce Trig Waves", default = False, update = propertyChanged)
    rpm = FloatProperty(name = "Revs per min", default = 1, min = 0.001)
    Max_t = FloatProperty(name = "Tangent Max", default = 1000, min = 10)

    def create(self):
        self.newOutput("Integer", "Seconds Tick", "tick")
        self.newOutput("Float", "RPM (Revolutions)", "rpm_w")
        self.newOutput("Float", "Sine Wave", "sin_w")
        self.newOutput("Float", "Cosine Wave", "cos_w")
        self.newOutput("Float", "Tangent Wave", "tan_w")
        self.newOutput("Float", "Sine Pulse", "pul_s")
        self.newOutput("Float", "Cosine Pulse", "pul_c")

    def draw(self, layout):
        layout.prop(self, "tic_t")
        layout.prop(self, "rpm")
        layout.prop(self, "trig")
        layout.prop(self, "Speed")
        layout.prop(self, "Amplitude")
        layout.prop(self, "pul_a")
        layout.prop(self, "Max_t")


    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        frm = bpy.context.scene.frame_start
        tick = int(bpy.context.scene.frame_current / (bpy.context.scene.render.fps * self.tic_t))
        rpm_w = ((bpy.context.scene.frame_current - frm) * self.rpm) / (bpy.context.scene.render.fps * 60)
        if self.trig:
            sin_w = sin((bpy.context.scene.frame_current - frm) * 2 * pi / self.Speed) * self.Amplitude
            cos_w = cos((bpy.context.scene.frame_current - frm) * 2 * pi / self.Speed) * self.Amplitude
            tan_w = tan((bpy.context.scene.frame_current - frm) * 2 * pi / self.Speed) * self.Amplitude
            if tan_w > self.Max_t: tan_w = self.Max_t
            if tan_w < -self.Max_t: tan_w = -self.Max_t
            pul_s = (sin_w > (self.Amplitude * self.pul_a)) * self.Amplitude
            pul_c = (cos_w > (self.Amplitude * self.pul_a)) * self.Amplitude
        else:
            sin_w = 0
            cos_w = 0
            tan_w = 0
            pul_s = 0
            pul_c = 0

        return tick, rpm_w, sin_w, cos_w, tan_w, pul_s, pul_c
