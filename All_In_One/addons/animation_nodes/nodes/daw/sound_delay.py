import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class DelaySound(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelaySound"
    bl_label = "SOUND Single Delay"
    bl_width_default = 150

    def create(self):
        self.newInput("an_FloatSocket","Delay (s)","delayT",minValue=0.001)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,delayT,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd is not None and delayT > 0:
            snd = snd.delay(delayT)
        return snd
