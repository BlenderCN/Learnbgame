import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
import pygame.midi

class MidiInitNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiInitNode"
    bl_label = "MIDI RealTime Data"
    bl_width_default = 150

    message_e = StringProperty()
    pygame.midi.init()
    isPyGameInit = BoolProperty(name = "Pygame Output", default = True, update = propertyChanged)

    # Check number of devices and check they are MID Inputs, not Outputs
    mid1Valid = True
    MidiDevicesNbr = pygame.midi.get_count()
    if MidiDevicesNbr == 1:
        m_info1 = str(pygame.midi.get_device_info(0))
        message = 'Dev 1: ' + m_info1
        if m_info1.split(',')[2].strip() == '1':
            midiInput = pygame.midi.Input(0)
        else:
            # Reduce MidiDevicesNbr by 1 - this will now be 0 and trapped in the execute function
            MidiDevicesNbr = MidiDevicesNbr - 1
    elif MidiDevicesNbr == 2:
        m_info1 = str(pygame.midi.get_device_info(0))
        message = 'Dev 1: ' + m_info1
        m_info2 = str(pygame.midi.get_device_info(1))
        message1 = 'Dev 2: ' + m_info2
        if m_info1.split(',')[2].strip() == '1':
            midiInput = pygame.midi.Input(0)
        else:
            # Reduce MidiDevicesNbr by 1 and set midiInput 1 to invalid
            MidiDevicesNbr = MidiDevicesNbr - 1
            mid1Valid = False
        if m_info2.split(',')[2].strip() == '1':
            if mid1Valid: # Set second midiInput to this pygame input
                midiInput1 = pygame.midi.Input(1)
            else: # Set first midiInput to this pygame input (only this is valid)
                midiInput = pygame.midi.Input(1)
        else:
            # Reduce MidiDevicesNbr by 1
            MidiDevicesNbr = MidiDevicesNbr - 1
    else:
        # We only handle up to 2 interfaces for now
        message = 'None or More than 2, MIDI Interface(s)'
        # By now we should have a number for valid Midi Inputs
        # If both were Ouputs, we have none, this is trapped in the execute function.

    def create(self):
        # New Input to set number of packets to read:
        self.newInput("Integer", "MIDI Packets To Read", "num_p")
        self.newOutput("Vector List", "MIDI Buffer", "m_buff")
        if self.MidiDevicesNbr == 2:
            self.newOutput("Vector List", "MIDI Buffer 2", "m_buff2")
        self.newOutput("Integer", "MIDI Device Count", "m_num")

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.5
        layout.prop(self, "isPyGameInit")
        if self.message != '':
            layout.label(self.message, icon = "INFO")
        if self.MidiDevicesNbr == 2:
            if self.message1 != '':
                layout.label(self.message1, icon = "INFO")
        if self.message_e != '':
            layout.label(self.message_e, icon = "CANCEL")
        self.invokeFunction(col, "quitMidi", icon = "CANCEL",
            text = "Stop MIDI Feed")

    def execute(self, num_p):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        if self.MidiDevicesNbr == 0 or self.MidiDevicesNbr > 2:
             return [],[],self.MidiDevicesNbr
        buffer = []
        if self.MidiDevicesNbr == 2:
            buffer2 = []
        # Check Num Packets is greater than 0
        if num_p < 1:
            self.message_e = 'Set MIDI Packets!'
            if self.MidiDevicesNbr == 1:
                return [], self.MidiDevicesNbr
            elif self.MidiDevicesNbr == 2:
                return [], [], self.MidiDevicesNbr
        else:
            self.message_e = ''

        if self.isPyGameInit and pygame.midi.Input.poll(self.midiInput):
        # messages are formatted this way: [[message type, note / parameter ID, velocity / parameter value, ?], TimeStamp]
            buffer = pygame.midi.Input.read(self.midiInput, num_p)
        # Read second midi input
        if self.MidiDevicesNbr == 2:
            buffer2 = pygame.midi.Input.read(self.midiInput2, num_p)
        # Return for 1 input
        if self.MidiDevicesNbr == 1:
            return buffer, self.MidiDevicesNbr
        # Return for 2 inputs
        elif self.MidiDevicesNbr == 2:
            return buffer, buffer2, self.MidiDevicesNbr
        else:
            # Return for no, or more than 2 inputs
            return [], [], self.MidiDevicesNbr

    def quitMidi(self):
        if self.isPyGameInit:
            self.midiInput.close()
            # Close second input
            if self.MidiDevicesNbr == 2:
                self.midiInput2.close()
            #pygame.midi.quit() This causes error and is actioned by quiting Blender, I think...
            self.isPyGameInit = False
            self.message_e = 'Restart Blender to Restart MIDI Feed'

    # def __del__(self):
    #     self.quitMidi()
