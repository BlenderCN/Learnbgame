import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class an_iirFirFilter(bpy.types.Node, AnimationNode):
    bl_idname = "an_iirFirFilter"
    bl_label = "SOUND IIR/FIR Filter"
    bl_width_default = 220

    typeB = BoolProperty(name="IIR/FIR",default=True)
    a = FloatProperty(name='B1')
    b = FloatProperty(name='B2')
    c = FloatProperty(name='B3')
    d = FloatProperty(name='B4')
    e = FloatProperty(name='B5')
    f = FloatProperty(name='B6')

    g = IntProperty(name='A1',default=0,min=0,max=1)
    h = FloatProperty(name='A2')
    i = FloatProperty(name='A3')
    j = FloatProperty(name='A4')
    k = FloatProperty(name='A5')
    l = FloatProperty(name='A6')

    def draw(self,layout):
        layout.prop(self,"typeB")
        colm = layout.column()
        row = colm.row()
        col = row.column()
        col.prop(self,"a")
        col = row.column()
        col.prop(self,"b")
        row = colm.row()
        col = row.column()
        col.prop(self,"c")
        col = row.column()
        col.prop(self,"d")
        row = colm.row()
        col = row.column()
        col.prop(self,"e")
        col = row.column()
        col.prop(self,"f")
        row = colm.row()
        row.label("FIR Sequence")
        row = colm.row()
        col = row.column()
        col.prop(self,"g")
        col = row.column()
        col.prop(self,"h")
        row = colm.row()
        col = row.column()
        col.prop(self,"i")
        col = row.column()
        col.prop(self,"j")
        row = colm.row()
        col = row.column()
        col.prop(self,"k")
        col = row.column()
        col.prop(self,"l")
        row = colm.row()
        row.label("IIR Sequence")


    def create(self):
        self.newInput("an_SoundSocket","Sound I","snd")
        self.newOutput("an_SoundSocket","Sound O","sound")

    def execute(self,snd):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if snd is not None:
            if self.typeB:
                snd = snd.filter((self.a,self.b,self.c,self.d,self.e,self.f),(self.g,self.h,self.i,self.j,self.k,self.l))
            else:
                snd = snd.filter((self.a,self.b,self.c,self.d,self.e,self.f))
        return snd
