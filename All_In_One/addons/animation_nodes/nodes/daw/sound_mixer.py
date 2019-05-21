import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class mixSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_mixSound"
    bl_label = "SOUND 5 Channel Mixer"
    bl_width_default = 180

    def create(self):
        self.newInput("an_SoundSocket","Sound 1","snd1")
        self.newInput("an_FloatSocket","Vol 1","vol1",default=1,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound 2","snd2")
        self.newInput("an_FloatSocket","Vol 2","vol2",default=1,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound 3","snd3")
        self.newInput("an_FloatSocket","Vol 3","vol3",default=1,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound 4","snd4")
        self.newInput("an_FloatSocket","Vol 4","vol4",default=1,minValue=0,maxValue=1)
        self.newInput("an_SoundSocket","Sound 5","snd5")
        self.newInput("an_FloatSocket","Vol 5","vol5",default=1,minValue=0,maxValue=1)
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,snd1,vol1,snd2,vol2,snd3,vol3,snd4,vol4,snd5,vol5):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        snd = None
        if snd1 is not None and snd2 is not None:
            snd1 = snd1.volume(vol1)
            snd2 = snd2.volume(vol2)
            snd = snd1.mix(snd2)
            if snd3 is not None:
                snd3 = snd3.volume(vol3)
                snd = snd.mix(snd3)
                if snd4 is not None:
                    snd4 = snd4.volume(vol4)
                    snd = snd.mix(snd4)
                    if snd5 is not None:
                        snd5 = snd5.volume(vol5)
                        snd = snd.mix(snd5)
        return snd
