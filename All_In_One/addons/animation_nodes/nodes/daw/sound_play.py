import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class PlaySound(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlaySound"
    bl_label = "SOUND Play"
    bl_width_default = 150

    def create(self):
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd is not None:
            dev = aud.device()
            handle = dev.play(snd)
        return snd
