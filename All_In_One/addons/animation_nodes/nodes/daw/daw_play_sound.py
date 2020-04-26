import bpy
import aud
import os
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class PlayFile(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlayFile"
    bl_label = "DAW Play File"
    bl_width_default = 150

    soundFile = StringProperty()
    soundName = StringProperty()
    message1  = StringProperty()
    message2  = StringProperty()

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.2
        self.invokeSelector(col, "PATH", "loadFile",
            text = "Load Sound File", icon = "NEW")
        self.invokeFunction(col, "stopAll", icon = "RADIO",
            text = "Shut Up!!")
        if self.message1 is not '':
            layout.label(self.message1,icon="NONE")
        if self.message2 is not '':
            layout.label(self.message2,icon="NONE")

    def create(self):
        self.newInput("an_FloatSocket","Volume","volume",default=0.2,minValue=0.001,maxValue=1)
        self.newInput("an_FloatSocket","Duration (s)","duration",default=1,minValue=0)
        self.newInput("an_BooleanSocket","Process","process",default = True)
        self.newInput("an_BooleanSocket","Reverse","revB",default = False)

    def loadFile(self,path):
        self.soundFile = str(path)
        self.soundName = str(os.path.basename(path))
        self.message1 = 'File Loaded: '+self.soundName

    def stopAll(self):
        dev = aud.device()
        dev.stopAll()
        self.message2 = 'All Stopped'

    def execute(self,volume,duration,process,revB):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        dev = aud.device()
        if process and self.soundFile is not '':
            snd = aud.Factory(self.soundFile)
            if revB:
                snd = snd.reverse()
            if duration != 0:
                snd = snd.limit(0,duration)
            handle = dev.play(snd)
            handle.volume = volume
        if self.soundFile is '':
            self.message2 = 'Load Sound File'
        else:
            self.message2 = ''
