import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getIndex, getFreq, getChord

class PlayNote(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlayNote"
    bl_label = "DAW Play Note"
    bl_width_default = 180

    store    = {}
    chordB   = BoolProperty(name="Play Chord",default=False)
    message  = StringProperty()

    def create(self):
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_FloatSocket","Square Value","squaV",default=0,minValue=-0.99,maxValue=0.99)
        self.newInput("an_FloatSocket","Duration (s)","duration",default=1,minValue=0.1)
        self.newInput("an_FloatSocket","Volume","volume",default=0.2,minValue=0.001,maxValue=1)
        self.newInput("an_FloatSocket","Samples","samples",default=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Process","process",default = True)
        self.newOutput("an_GenericSocket","Stored Information","store")

    def draw(self,layout):
        layout.prop(self,"chordB")
        if self.message is not '':
            layout.label(self.message,icon="NONE")

    def execute(self,noteName,squaV,duration,volume,samples,process):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        frameC = bpy.context.scene.frame_current
        fps = bpy.context.scene.render.fps
        dev = aud.device()

        if frameC == 1:
            self.store.clear()
            stopF = 1
            dev.stopAll()
            self.color = (0.9,0.7,0.8)
            return self.store

        if '.' in self.name:
            name = 'Handle_'+self.name.split('.')[1]
        else:
            name = 'Handle_000'

        if name in self.store:
            stopF = self.store[name+'_stop']
        else:
            stopF = bpy.context.scene.frame_start

        # Only process if last note finished
        self.message = ''
        freq = 0
        if process and frameC > stopF:
            indX = getIndex(noteName)
            if indX in range(0,107):
                freq = getFreq(indX)
            else:
                self.message = 'Note Invalid'
                return self.store

            snd = aud.Factory.sine(freq,samples)

            if self.chordB:
                idxList = getChord(noteName)
                if len(idxList) == 3:
                    # Make 3 Notes and Joi them
                    snd1 = aud.Factory.sine(idxList[0],samples)
                    snd2 = aud.Factory.sine(idxList[1],samples)
                    snd3 = aud.Factory.sine(idxList[2],samples)
                    snd = snd1.mix(snd2)
                    snd = snd.mix(snd3)
                else:
                    self.message = 'Invalid Input Note Name'
                    return self.store
            if squaV != 0:
                snd = snd.square(squaV)
            snd = snd.limit(0,duration)
            handle = dev.play(snd)
            self.store[name]=handle
            self.store[name+'_start']=int(frameC)
            self.store[name+'_stop']=int(frameC + (duration*fps))

        return self.store
