import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class fadeSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_fadeSound"
    bl_label = "SOUND Fader"
    bl_width_default = 180

    def create(self):
        self.newInput("an_FloatSocket","Start","start",minValue=0)
        self.newInput("an_FloatSocket","Length","length",default=1,minValue=0)
        self.newInput("an_BooleanSocket","Fade In/out","fade",default = True)
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,start,length,fade,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd is not None:
            if fade:
                snd = snd.fadein(start,length)
            else:
                snd = snd.fadeout(start,length)
        return snd
