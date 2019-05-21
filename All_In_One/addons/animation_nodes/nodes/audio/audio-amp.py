import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

enum = [('2','2','Number of Divisions','',0),
    ('3','3','Number of Divisions','',1),
    ('4','4','Number of Divisions','',2),
    ('5','5','Number of Divisions','',3),
    ('6','6','Number of Divisions','',4),
    ('7','7','Number of Divisions','',5),
    ('8','8','Number of Divisions','',6),
    ('9','9','Number of Divisions','',7),
    ('10','10','Number of Divisions','',8)
    ]

class AudioAMPNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AudioAMPNode"
    bl_label = "AUDIO Amplitude Splitter"
    bl_width_default = 200

    maxAmp = FloatProperty(name = "Max Amplitude",default = 1, min = 0.01, update = propertyChanged)
    minAmp = FloatProperty(name = "Min Amplitude",default = 0, min = 0, update = propertyChanged)
    sigFig = IntProperty(name = "Output Sig. Figures",default = 0, min = 0,update = propertyChanged)
    negVal = BoolProperty(name = "Process Negative Values", default = False, update = propertyChanged)
    mode = EnumProperty(name = "Divisions", items = enum, update = AnimationNode.refresh)


    def draw(self,layout):
        layout.prop(self, "mode")
        layout.prop(self, "maxAmp")
        layout.prop(self, "minAmp")
        layout.prop(self, "sigFig")
        layout.prop(self, "negVal")
        layout.label("0 Sig. Figs. means Don't Apply", icon = "INFO")

    def create(self):
        self.newInput("Float", "Input", "input")
        self.newOutput("Float List", "Output List", "output")

    def execute(self,input):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.85,1,0.85)
        addRem = True
        negInp = False
        if input < 0:
            negInp = True
        input = abs(input)
        if input >= self.maxAmp:
            input = self.maxAmp
            addRem = False
        elif input < self.minAmp:
            input = self.minAmp
        divAmp = self.maxAmp / int(self.mode)
        if self.sigFig > 0:
            divAmp = float(str(divAmp)[0:(self.sigFig+1)])
        outAmps = []
        divInt = int(input // divAmp)
        rem = input % divAmp
        if self.sigFig > 0:
            rem = float(str(rem)[0:(self.sigFig+1)])
        for i in range(0,divInt):
            if self.negVal and negInp:
                outAmps.append(-divAmp)
            else:
                outAmps.append(divAmp)
        if addRem:
            if rem > self.minAmp:
                if self.negVal and negInp:
                    outAmps.append(-rem)
                else:
                    outAmps.append(rem)
            else:
                if self.negVal and negInp:
                    outAmps.append(float(str(-self.minAmp)[0:(self.sigFig+1)]))
                else:
                    outAmps.append(float(str(self.minAmp)[0:(self.sigFig+1)]))
        for i in range(0,(int(self.mode)-len(outAmps))):
            if self.negVal and negInp and self.minAmp != 0:
                outAmps.append(float(str(-self.minAmp)[0:(self.sigFig+1)]))
            else:
                outAmps.append(float(str(self.minAmp)[0:(self.sigFig+1)]))

        return outAmps
