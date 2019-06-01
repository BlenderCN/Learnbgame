import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getIndex, getFreq, getChord

class GenrerateSound(bpy.types.Node, AnimationNode):
    bl_idname = "an_GenrerateSound"
    bl_label = "SOUND Generate"
    bl_width_default = 150

    message = StringProperty()
    soundFile = StringProperty()
    soundName = StringProperty()

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadFile",
            text = "Load Sound File", icon = "NEW")
        if self.message is not '':
            layout.label(self.message,icon="NONE")

    def create(self):
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_FloatSocket","Frequency","frequency",default=440,minValue=0)
        self.newInput("an_FloatSocket","Volume","volume",default=0.2,minValue=0.001,maxValue=1)
        self.newInput("an_FloatSocket","Start Offset (s)","startoff",default=0,minValue=0)
        self.newInput("an_FloatSocket","Duration (s)","duration",default=1,minValue=0)
        self.newInput("an_FloatSocket","Square Value","squaV",default=0,minValue=-0.99,maxValue=0.99)
        self.newInput("an_FloatSocket","Samples","samples",default=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Reverse","revB",default = False)
        self.newInput("an_BooleanSocket","Process","process",default = True)
        self.newOutput("an_SoundSocket","Sound","sound")

    def loadFile(self,path):
        self.inputs[0].value = ''
        self.inputs[1].value = 0
        self.soundFile = str(path)
        self.soundName = str(os.path.basename(path))
        self.message = 'File Loaded: '+self.soundName

    def execute(self,noteName,frequency,volume,startoff,duration,squaV,samples,revB,process):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,0.5)
        if process:
            if noteName is not '':
                self.soundFile = ''
                self.message = ''
                indX = getIndex(noteName)
                if indX in range(0,107):
                    freq = getFreq(indX)
                else:
                    self.message = 'Note Invalid'
                    return snd
                snd = aud.Factory.sine(freq,samples)
            elif frequency > 16.35160:
                self.soundFile = ''
                self.message = ''
                snd = aud.Factory.sine(frequency,samples)
            elif self.soundFile is not '':
                snd = aud.Factory(self.soundFile)
                if revB:
                    snd = snd.reverse()
                squaV = 0
            else:
                return None
            if squaV != 0:
                snd = snd.square(squaV)
            snd = snd.limit(startoff,duration)
        else:
            snd = None
        return snd
