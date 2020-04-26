import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class MidiInitNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ZodiacMidiHandlerNode"
    bl_label = "MIDI Single-Event Handler"
    bl_width_default = 150

    out_buff = []
    noteID = IntProperty(name = "Midi Note", default = 0, update = propertyChanged)
    noteVelocity = IntProperty(name = "Note Velocity", default = 0, update = propertyChanged)
    paramID = IntProperty(name = "Midi Parameter", default = 0, update = propertyChanged)
    paramValue = IntProperty(name = "Parameter Value", default = 0, update = propertyChanged)
    time_s = FloatProperty()

    def create(self):
        self.newInput("Vector List"	, "Midi Buffer"	        , "MidiBuffer")
        #If Velocity is set at -1, the midi input velocity is used, otherwise the specified value is used.
        #This should be set at -1 when using an Aftertouch capable keyboard, otherwise you'll get 64 (127//2) everytime
        self.newInput("Integer"		, "Velocity"			, "Velocity")
        self.newOutput("Integer"	, "Note ID"             , "NoteID")
        self.newOutput("Integer"	, "Note Velocity"		, "NoteVelocity")
        self.newOutput("Integer"	, "Parameter ID"		, "ParameterID")
        self.newOutput("Integer"	, "Parameter Value"		, "ParameterValue")
        self.newOutput("Float"      , "MIDI Timer"          , "time_s")

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.5

    def execute(self, MidiBuffer, Velocity):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        cleanBuffer = []
        notesBuffer = []
        paramsBuffer = []
        for data in MidiBuffer:
            #if there is data
            if len(data) > 0 and len(data[0]) > 0 and data[0][1]:
                self.time_s = data[1]
                #if the message is a parameter data
                if data[0][0] == 176:
                    self.paramID = data[0][1]
                    self.paramValue = data[0][2]
                #else the message is a note
                else:
                    self.noteID = data[0][1]
                    #I separated the "value to note name" function for more readability
                    # the if is here to prevent note ending message's velocity to be taken into account,
                    # we will need an option for keyboards with aftertouch to modify this
                    if data[0][0] == 144:
                        if Velocity == -1:
                            self.noteVelocity = data[0][2]
                        else:
                            if data[0][2] == 0:
                                self.noteVelocity = 0
                            else:
                                self.noteVelocity = Velocity
        return self.noteID, self.noteVelocity, self.paramID, self.paramValue,self.time_s
