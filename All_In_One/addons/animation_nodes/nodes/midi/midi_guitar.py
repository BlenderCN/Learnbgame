import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from . midi_functions import getFretS, getFretB

class MidiGuitarNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiGuitarNode"
    bl_label = "MIDI Guitar Strings/Frets"
    bl_width_default = 150

    mid_c = BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    suffix = StringProperty(name = "Suffix", update = propertyChanged)

    def draw(self,layout):
        layout.prop(self, "mid_c")
        layout.prop(self, "suffix")

    def create(self):
        self.newInput("Integer", "Input Note index", "Idx")
        self.newOutput("Text List", "6 String", "sixS")
        self.newOutput("Text List", "Bass", "bass")

    def execute(self,Idx):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        if not self.mid_c:
            Idx = Idx + 12
        # 6 string
        if Idx >= 52 and Idx < 57:
            string = 'El'+'_'+self.suffix
        elif Idx >= 57 and Idx < 62:
            string = 'A'+'_'+self.suffix
        elif Idx >= 62 and Idx < 67:
            string = 'D'+'_'+self.suffix
        elif Idx >= 67 and Idx < 71:
            string = 'G'+'_'+self.suffix
        elif Idx >= 71 and Idx < 76:
            string = 'B'+'_'+self.suffix
        elif Idx >= 76 and Idx < 101:
            string = 'Et'+'_'+self.suffix
        else:
            string = 'null'
            fret = 'null'
        # Get Fret
        if string is not 'null':
            fret = getFretS(Idx, -52)
        # Bass
        if Idx >= 40 and Idx < 45:
            stringb = 'El'+'_'+self.suffix
        elif Idx >= 45 and Idx < 50:
            stringb = 'A'+'_'+self.suffix
        elif Idx >= 50 and Idx < 55:
            stringb = 'D'+'_'+self.suffix
        elif Idx >= 55 and Idx < 80:
            stringb = 'G'+'_'+self.suffix
        else:
            stringb = 'null'
            fretb = 'null'
        # Get Fret
        if stringb is not 'null':
            fretb = getFretB(Idx, -40)
        # Set Output List
        sixS = [string,fret]
        bass = [stringb,fretb]

        return sixS, bass
