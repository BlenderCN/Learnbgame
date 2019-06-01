import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class ClockMidiHandlerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ClockMidiHandlerNode"
    bl_label = "MIDI Multi-Event Handler"
    bl_width_default = 150

    note_buff = []
    param_buff = []
    time_s = FloatProperty()

    def create(self):
        self.newInput("Vector List"	, "Midi Buffer"	        , "MidiBuffer")
        #If Velocity is set at -1, the midi input velocity is used, otherwise the specified value is used.
        #This should be set at -1 when using an Aftertouch capable keyboard, otherwise you'll get 64 (127//2) everytime
        self.newInput("Integer"		, "Velocity"			, "Velocity")
        self.newOutput("Vector List", "Note Buffer"			, "m_buff")
        self.newOutput("Vector List", "Param Buffer"		, "p_buff")
        self.newOutput("Float"      , "MIDI Timer"          , "time_s")

    def execute(self, MidiBuffer, Velocity):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        cleanBuffer = []
        for data in MidiBuffer:
            #if there is data
            if len(data) > 0 and len(data[0]) > 0 and data[0][1]:
                self.time_s = data[1]
                cleanBuffer.append(data)
                if data[0][0] == 144: # Note
                    del self.note_buff[:] #Empty list rather than create new one, keeps data.
                if data[0][0] == 176: # Parameter
                    del self.param_buff[:] #Empty list.
                if len(cleanBuffer) > 0:
                    for b in cleanBuffer:
                        if data[0][0] == 144: # Note
                            if Velocity == -1:
                                self.note_buff.append([b[0][1],b[0][2]])
                            else:
                                if b[0][2] == 0:
                                    self.note_buff.append([b[0][1],0])
                                else:
                                    self.note_buff.append([b[0][1], Velocity])
                        elif data[0][0] == 176: # Parameter
                            self.param_buff.append([b[0][1],b[0][2]])
                        # Add other elif to cater for other values of data[0][0]
        return self.note_buff, self.param_buff, self.time_s
