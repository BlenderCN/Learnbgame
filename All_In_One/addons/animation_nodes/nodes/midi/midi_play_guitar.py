import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged
from math import sin
from . midi_functions import getIndex, getFretS, getFretB

class guitarPlayNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_guitarPlayNode"
    bl_label = "MIDI Play Guitar"
    bl_width_default = 200

    mess = StringProperty()
    suffix = StringProperty(name = 'String Suffix', update = propertyChanged)
    octS = IntProperty(name = 'Octave Shift', default = 0, min = -2, max = 2)
    sFrm = IntProperty(name = 'Note Change Frame', update = propertyChanged)
    cIdx = IntProperty(update = propertyChanged)

    def draw(self,layout):
        layout.prop(self, "suffix")
        layout.prop(self, "octS")
        if self.mess is not '':
            layout.label(self.mess, icon = 'INFO')

    def create(self):
        self.newInput("Boolean", "6 String (4 String if False)", "sixBool", default = True)
        self.newInput("Object", "Finger Object", "finger")
        self.newInput("Object", "Plectrum Object", "plectrum")
        self.newInput("Float", "Nut Scale", "nutScale", minVaue = 0.7, maxValue = 1)
        self.newInput("Object List", "Control Objects", "contObjs")
        self.newInput("Generic", "String Material", "strMat")
        self.newInput("Generic", "Play Material", "plyMat")
        self.newOutput("Text", "Note, Fret & Idx", "noteFret")

    def execute(self, sixBool, finger, plectrum, nutScale, contObjs, strMat, plyMat):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        noteFret = 'None,None,0,None'
        brObj = bpy.data.objects.get('Bridge')
        nuObj = bpy.data.objects.get('NUT')
        if brObj is not None and nuObj is not None:
            dist = abs(brObj.location.x - nuObj.location.x)
        else:
            dist = 1
        if len(contObjs) == 0:
            self.mess = 'No Control Objects'
        else:
            self.mess = ''
            if sixBool:
                for ob in [bpy.data.objects.get('El'+'_'+self.suffix),bpy.data.objects.get('A'+'_'+self.suffix),
                        bpy.data.objects.get('D'+'_'+self.suffix),bpy.data.objects.get('G'+'_'+self.suffix),
                            bpy.data.objects.get('B'+'_'+self.suffix),bpy.data.objects.get('Et'+'_'+self.suffix)]:
                    if ob is not None:
                        ob.material_slots[0].material = strMat
                    else:
                        self.mess = 'Some Strings are Missing'
                        return 'String,Error,0'
            else:
                for ob in [bpy.data.objects.get('El'+'_'+self.suffix),bpy.data.objects.get('A'+'_'+self.suffix),
                        bpy.data.objects.get('D'+'_'+self.suffix),bpy.data.objects.get('G'+'_'+self.suffix)]:
                    if ob is not None:
                        ob.material_slots[0].material = strMat
                    else:
                        self.mess = 'Some Strings are Missing!'
                        return 'String,Error,0'

            for obj in contObjs:
                zLoc = obj.location.z
                noteName = obj.name.split('_')[1]
                Idx = getIndex(noteName)
                Idx = Idx + 12 + (self.octS * 12)
                if sixBool:
                    # Use 6 Strings Lead
                    if Idx >= 52 and Idx < 57:
                        string = 'El'+'_'+self.suffix
                    elif Idx >= 57 and Idx < 62:
                        string = 'A'+'_'+self.suffix
                    elif Idx >= 62 and Idx < 67:
                        string = 'D'+'_'+self.suffix
                    elif Idx >= 67 and Idx < 71:
                        string = 'G'+'_'+self.suffix
                    elif Idx >= 71 and Idx < 76:
                        string = 'B'+'_'+self.suffix
                    elif Idx >= 76 and Idx < 101:
                        string = 'Et'+'_'+self.suffix
                    else:
                        string = 'null'
                        fret = 'null'
                    # Get the Fret
                    if string is not 'null':
                        fret = getFretS(Idx, -52)
                else:
                    # Use 4 Strings Bass
                    if Idx >= 40 and Idx < 45:
                        string = 'El'+'_'+self.suffix
                    elif Idx >= 45 and Idx < 50:
                        string = 'A'+'_'+self.suffix
                    elif Idx >= 50 and Idx < 55:
                        string = 'D'+'_'+self.suffix
                    elif Idx >= 55 and Idx < 80:
                        string = 'G'+'_'+self.suffix
                    else:
                        string = 'null'
                        fret = 'null'
                    # Get the Fret
                    if string is not 'null':
                        fret = getFretB(Idx, -40)

                if string == 'null':
                    # Note is off guitar
                    strgObj = None
                    fretObj = None
                else:
                    # Move Plectrum
                    if string.split('_')[0] == 'El':
                        pObj = bpy.data.objects.get('elsP')
                    elif string.split('_')[0] == 'A':
                        pObj = bpy.data.objects.get('asP')
                    elif string.split('_')[0] == 'D':
                        pObj = bpy.data.objects.get('dsP')
                    elif string.split('_')[0] == 'G':
                        pObj = bpy.data.objects.get('gsP')
                    elif string.split('_')[0] == 'B':
                        pObj = bpy.data.objects.get('bsP')
                    elif string.split('_')[0] == 'Et':
                        pObj = bpy.data.objects.get('etsP')
                    # Set String Objects
                    strgObj = bpy.data.objects.get(string)
                    fretObj = bpy.data.objects.get(fret)

                if zLoc > 0:
                    if strgObj is not None and fretObj is not None:
                        yLoc = strgObj.location.y * nutScale
                        xLoc = fretObj.location.x
                        if fret is not 'NUT':
                            finger.location = (xLoc,yLoc,(0.008* dist))
                        else:
                            finger.location.z = (0.012 * dist)
                        if pObj is not None and plectrum is not None:
                            plectrum.location = pObj.matrix_world.decompose()[0]
                            if Idx is not self.cIdx:
                                self.cIdx = Idx
                                self.sFrm = bpy.context.scene.frame_current
                            if bpy.context.scene.frame_current in range((self.sFrm +1), (self.sFrm + 2)):
                                plectrum.location.z = pObj.matrix_world.decompose()[0].z - (0.0015 * dist)
                            elif bpy.context.scene.frame_current == (self.sFrm + 3):
                                plectrum.location.z = pObj.matrix_world.decompose()[0].z

                        strgObj.material_slots[0].material = plyMat
                        noteFret = string+','+fret+',' + str(Idx)+','+noteName

                    elif string == 'null':
                        noteFret = 'Info,Note off Guitar,' + str(Idx)+','+noteName
                        self.cIdx = 0

        if noteFret == 'None,None,0,None':
            self.cIdx = 0
        return noteFret
