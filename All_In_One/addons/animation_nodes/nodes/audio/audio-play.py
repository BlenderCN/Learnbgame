import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
import pygame.mixer as pgm
pgm.init()

class AudioPlayNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AudioPlayNode"
    bl_label = "AUDIO Play Music File"
    bl_width_default = 200

    message = StringProperty()

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.5
        self.invokeSelector(col ,"PATH", "loadFile", icon = "NEW",
            text = "Select Sound File")
        layout.label(self.message)
        self.invokeFunction(col, "playFile", icon = "NEW",
            text = "Play File")
        self.invokeFunction(col, "pauseFile", icon = "NEW",
            text = "Pause Playback")
        self.invokeFunction(col, "resumeFile", icon = "NEW",
            text = "Resume Playback")
        self.invokeFunction(col, "stopFile", icon = "NEW",
            text = "Stop Playback")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,1,0.85)

    def loadFile(self,path):
        pgm.music.load(path)
        self.message = str(path)

    def playFile(self):
        pgm.music.play()

    def pauseFile(self):
        pgm.music.pause()

    def resumeFile(self):
        pgm.music.unpause()

    def stopFile(self):
        pgm.music.stop()
