import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from . midi_functions import getNote

class MidiNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiNameNode"
    bl_label = "MIDI Name Object(s)"
    bl_width_default = 180

    # Setup variables
    mid_c = BoolProperty(name = "Middle C = C4", default = True, update = propertyChanged)
    procI = BoolProperty(name = "Index Process", default = False, update = propertyChanged)
    procL = BoolProperty(name = "Name List Process", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Integer"     , "Start Note Index", "start_i")
        self.newInput("Text"        , "Suffix"          , "suff")
        self.newInput("Text List", "Notes Played", "noteL")
        self.newInput("Object List" , "Selected Objects", "objs")

    def draw(self,layout):
        layout.prop(self,"procI")
        layout.prop(self,"procL")
        layout.prop(self,"mid_c")
        layout.label("Check Process to Start/Stop", icon = "INFO")

    def execute(self, start_i, suff, noteL, objs):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        if self.procI and len(objs) > 0 and start_i is not 0:
            Idx = start_i
            for i in objs:
                if self.mid_c:
                    note_name = getNote(Idx, -12)
                else:
                    note_name = getNote(Idx, 0)
                if suff != '':
                    note_name = note_name +'_'+ suff
                i.name = note_name
                Idx = Idx + 1

            self.procI = False
        elif self.procL and len(objs) == len(noteL):
            ind = 0
            for ob in objs:
                ob.name = noteL[ind]
                ind = ind + 1
            self.procL = False
