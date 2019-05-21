import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

enum = [('1','1','Number of Divisions','',0),
    ('2','2','Number of Divisions','',1),
    ('3','3','Number of Divisions','',2),
    ('4','4','Number of Divisions','',3),
    ('5','5','Number of Divisions','',4),
    ('6','6','Number of Divisions','',5),
    ('7','7','Number of Divisions','',6),
    ('8','8','Number of Divisions','',7),
    ('9','9','Number of Divisions','',8),
    ('10','10','Number of Divisions','',9)
    ]

class echoSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_echoSound"
    bl_label = "SOUND 10 Channel Echo Unit"
    bl_width_default = 180

    mode    = EnumProperty(name = "Echos", items = enum, update = AnimationNode.refresh)
    delay1  = FloatProperty(name="Delay 1",default=0.1,min=0.001)
    delay2  = FloatProperty(name="Delay 2",default=0.1,min=0.001)
    delay3  = FloatProperty(name="Delay 3",default=0.1,min=0.001)
    delay4  = FloatProperty(name="Delay 4",default=0.1,min=0.001)
    delay5  = FloatProperty(name="Delay 5",default=0.1,min=0.001)
    delay6  = FloatProperty(name="Delay 6",default=0.1,min=0.001)
    delay7  = FloatProperty(name="Delay 7",default=0.1,min=0.001)
    delay8  = FloatProperty(name="Delay 8",default=0.1,min=0.001)
    delay9  = FloatProperty(name="Delay 9",default=0.1,min=0.001)
    delay10 = FloatProperty(name="Delay 10",default=0.1,min=0.001)
    baseV   = FloatProperty(name="Base Volume",default=1,min=0.01,max=1)
    stepV   = FloatProperty()
    volF    = FloatProperty(name="Volume Factor",default=0.9,min=0.01,max=1)

    def draw(self,layout):
        layout.prop(self, "mode")
        layout.prop(self, "baseV")
        layout.prop(self,"volF")
        layout.prop(self, "delay1")
        if int(self.mode) >= 2:
            for i in range(1,int(self.mode)):
                layout.prop(self,"delay"+str(i+1))

    def create(self):
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        sndO = snd
        if snd is not None:
            snd = snd.volume(self.baseV)
            sndT = snd.delay(self.delay1)
            sndT = sndT.volume(self.baseV)
            sndO = sndO.mix(sndT)
            if int(self.mode) > 1:
                vol = self.baseV*self.volF
                sndT = snd.delay(self.delay2)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 2:
                vol = vol*self.volF
                sndT = snd.delay(self.delay3)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 3:
                vol = vol*self.volF
                sndT = snd.delay(self.delay4)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 4:
                vol = vol*self.volF
                sndT = snd.delay(self.delay5)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 5:
                vol = vol*self.volF
                sndT = snd.delay(self.delay6)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 7:
                vol = vol*self.volF
                sndT = snd.delay(self.delay8)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 8:
                vol = vol*self.volF
                sndT = snd.delay(self.delay9)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)
            if int(self.mode) > 9:
                vol = vol*self.volF
                sndT = snd.delay(self.delay10)
                sndT = sndT.volume(vol)
                sndO = sndO.mix(sndT)

        return sndO
