import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class passFilter(bpy.types.Node, AnimationNode):
    bl_idname = "an_passFilter"
    bl_label = "SOUND High/LowPass Filter"
    bl_width_default = 180

    typeB = BoolProperty(name="High/Low Pass",default=True)

    def draw(self,layout):
        layout.prop(self,"typeB")

    def create(self):
        self.newInput("an_FloatSocket","Frequency","frequency",minValue=15,maxValue=20000)
        self.newInput("an_FloatSocket","Q Factor","qfactor",default=0.5,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,frequency,qfactor,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd is not None:
            if self.typeB:
                snd = snd.highpass(frequency,qfactor)
            else:
                snd = snd.lowpass(frequency,qfactor)
        return snd

#Alko TCS Duotec 2500
