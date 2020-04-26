import bpy
import aud
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from . daw_functions import getNote, getIndex, getFreq, getChord

class PlayScale(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlayScale"
    bl_label = "DAW Play Basic Scales"
    bl_width_default = 180

    store    = {}
    revS     = BoolProperty(name="Reverse",default=False)
    message  = StringProperty()
    nextExec = IntProperty()

    def create(self):
        self.newInput("an_TextSocket","Note","noteName")
        self.newInput("an_FloatSocket","Square Value","squaV",default=0,minValue=-0.99,maxValue=0.99)
        self.newInput("an_FloatSocket","Duration (s)","duration",default=1,minValue=0.1)
        self.newInput("an_FloatSocket","Volume","volume",default=0.2,minValue=0.001,maxValue=1)
        self.newInput("an_FloatSocket","Samples","samples",default=44100,minValue=5000)
        self.newInput("an_BooleanSocket","Process","process",default = True)
        self.newOutput("an_GenericSocket","Stored Information","store")
        self.newOutput("an_TextSocket","Last Note Played","lastNote")

    def draw(self,layout):
        layout.prop(self,"revS")
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
            self.nextExec = 0
            return self.store, ''

        if '.' in self.name:
            name = 'Handle_'+self.name.split('.')[1]
        else:
            name = 'Handle_000'

        if name in self.store:
            stopF = self.store[name+'_stop']
        else:
            stopF = bpy.context.scene.frame_start
            self.nextExec = 0

        # Only process if last note finished
        # Reverses scale if self.revS set to True
        self.message = ''
        freq = 0
        if process and frameC > stopF and self.nextExec <= 7:
            indX = 50
            if self.revS:
                if self.nextExec == 0:
                    indX = getIndex(noteName)
                elif self.nextExec == 1 or self.nextExec == 5:
                    indX = self.store[name+'_last']-1
                else:
                    indX = self.store[name+'_last']-2
            else:
                if self.nextExec == 0:
                    indX = getIndex(noteName)
                elif self.nextExec == 3 or self.nextExec == 7:
                    indX = self.store[name+'_last']+1
                else:
                    indX = self.store[name+'_last']+2

            if indX in range(0,107):
                freq = getFreq(indX)
            else:
                self.message = 'Note Invalid'
                return self.store

            self.store[name+'_last']=indX
            freq = getFreq(indX)
            snd = aud.Factory.sine(freq,samples)
            self.nextExec = self.nextExec + 1
            if squaV != 0:
                snd = snd.square(squaV)
            snd = snd.limit(0,duration)
            handle = dev.play(snd)
            handle.volume = volume
            self.store[name]=handle
            self.store[name+'_start']=int(frameC)
            self.store[name+'_stop']=int(frameC + (duration*fps))

        if name+'_last' in self.store:
            indLast = self.store[name+'_last']
            noteLast = getNote(indLast,0)
        else:
            noteLast = ''

        return self.store, noteLast
