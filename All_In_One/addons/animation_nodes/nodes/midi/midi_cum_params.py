import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class midiStoreParamsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_midiStoreParamsNode"
    bl_label = "MIDI Store Params"
    bl_width_default = 150

    modul = IntProperty(name = "Last Modulo")
    after = IntProperty(name = "Aftertouch")
    pedal = IntProperty(name = "last Pedal")

    def create(self):
        self.newInput("Vector List", "Midi Buffer", "MidiBuffer")
        self.newOutput("Integer", "Modulator", "modul")
        self.newOutput("Integer", "Aftertouch", "after")
        self.newOutput("Integer", "Pedal", "pedal")

    def draw(self, layout):
        layout.prop(self, "modul")
        layout.prop(self, "after")
        layout.prop(self, "pedal")

    def execute(self, MidiBuffer):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        cleanBuffer = []
        for data in MidiBuffer:
            cleanBuffer.append(data)
            for data in cleanBuffer:
                if data[0][0] == 176 and data[0][1] == 1:
                    self.modul = data[0][2]
                elif data[0][0] == 176 and data[0][1] == 3:
                    self.after = data[0][2]
                elif data[0][0] == 176 and data[0][1] == 64:
                    self.pedal = data[0][2]

        return self.modul, self.after, self.pedal
