import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from . midi_functions import getNote, getIndex

class MidiInitNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NoteValueToName"
    bl_label = "MIDI Note-Name Converter"
    bl_width_default = 180

    # Setup variables
    mid_c = BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)

    def draw(self, layout):
        layout.prop(self,"mid_c")

    def create(self):
        self.newInput("Integer", "Input Note Value", "NoteValue",minValue = 0)
        self.newInput("Text", "Input Note Name", "NoteNme")
        self.newInput("Text", "Suffix", "suff")
        self.newOutput("Text", "Note Name", "NoteName")
        self.newOutput("Integer", "Note Index", "NoteIdx")

    def execute(self, NoteValue, NoteNme, suff):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)

        if NoteNme is not '':
            NoteIdx = getIndex(NoteNme)
        else:
            NoteIdx = 0

        if self.mid_c:
            NoteValue = NoteValue - 12
            NoteIdx = NoteIdx + 12

        if NoteValue in range(0,128):
            NoteName = getNote(NoteValue, 0)
        else:
            NoteName = 'Out Of Range'

        if suff is not '':
            NoteName = NoteName +'_'+ suff

        return NoteName, NoteIdx
