import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class joinSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_joinSound"
    bl_label = "SOUND Join"
    bl_width_default = 150

    def create(self):
        self.newInput("an_SoundSocket","Sound 1","snd1")
        self.newInput("an_SoundSocket","Sound 2","snd2")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,snd1,snd2):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd1 is not None and snd2 is not None:
            snd1 = snd1.join(snd2)
        return snd1
