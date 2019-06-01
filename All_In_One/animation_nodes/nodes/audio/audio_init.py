import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
import sounddevice as sd

class AudioSDNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AudioSDNode"
    bl_label = "AUDIO Server"
    bl_width_default = 200

    # Get Devices and build Devices Options
    ssDevs = sd.query_devices()
    # Set variables
    devINames = []
    devONames = []
    enumI = []
    enumO = []
    chans = IntProperty(update = propertyChanged)
    runSD = BoolProperty(name = "Open SoundDevice Stream", default = False, update = propertyChanged)
    multI = IntProperty(name = "Output Multiplier", default = 50, update = propertyChanged)
    message = StringProperty()

    id = 0
    for bit in ssDevs:
        if bit.get('max_input_channels') > 0:
            devINames.append(str(id)+','+bit.get('name'))
        elif bit.get('max_output_channels') > 0:
            devONames.append(str(id)+','+bit.get('name'))
        id = id+1

    indI = 0
    indO = 0
    for bit in devINames:
        devID = bit.split(',')[0]
        enumI.append((devID,bit,"Device"+str(indI),"",indI))
        indI = indI+1
    for bit in devONames:
        devID = bit.split(',')[0]
        enumO.append((devID,bit,"Device"+str(indO),"",indO))
        indO = indO + 1

    modeI = EnumProperty(name = "Inputs", items = enumI, update = AnimationNode.refresh)
    modeO = EnumProperty(name = "Outputs", items = enumO, update = AnimationNode.refresh)

    def draw(self,layout):
        if len(self.devINames) > 0:
            layout.prop(self, "modeI")
        else:
            layout.label("No Input Devices:", icon = "ERROR")
        if len(self.devONames) > 0:
            layout.prop(self, "modeO")
        else:
            layout.label("No Output Devices:", icon = "ERROR")
        layout.prop(self, "multI")
        layout.prop(self, "runSD")
        if self.message != '':
            layout.label(self.message, icon = "INFO")
        layout.label('Number of Input Channels: '+str(self.chans), icon = "INFO")

    def create(self):
        self.newOutput("Float", "Left Channel", "l_chan")
        self.newOutput("Float", "Right Channel", "r_chan")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,1,0.85)
        inpDev = int(self.modeI)
        outDev = int(self.modeO)
        channI = sd.query_devices(int(inpDev)).get('max_input_channels')
        channO = sd.query_devices(int(outDev)).get('max_output_channels')
        streamI = sd.InputStream(device=inpDev,latency='low')
        self.chans = streamI.channels
        if self.runSD:
            if not streamI.active:
                streamI.start()
            self.message = str(streamI)
            myTuple = streamI.read(1)
            l_chan = round(myTuple[0][0][0] * self.multI,5)
            if self.chans == 2:
                r_chan = round(myTuple[0][0][1] * self.multI,5)
            else:
                r_chan = 0
        else:
            if streamI.active:
                # Shtdown Stream and close SD
                streamI.abort(ignore_errors=True)
                sd.stop(ignore_errors=True)
            self.message = 'Input Stream Closed'
            l_chan = 0
            r_chan = 0

        return l_chan, r_chan
