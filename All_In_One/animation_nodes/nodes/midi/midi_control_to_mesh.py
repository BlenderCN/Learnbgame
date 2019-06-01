import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class MidiCTMNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiCTMNode"
    bl_label = "MIDI Control To Mesh"
    bl_width_default = 220

    message = StringProperty()

    def draw(self,layout):
        if (self.message != ""):
            layout.label(self.message, icon = "ERROR")

    def create(self):
        self.newInput("Object", "Control", "control")
        self.newInput("Text", "Suffix", "suff")
        self.newInput("Float", "Multiplier", "multV")
        self.newOutput("Object", "Mesh Object", "m_obj")
        self.newOutput("Float", "Control Z", "z_cont")

    def execute(self, control, suff, multV):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)
        # Check for correct inputs
        if suff == '':
            self.message = 'No Suffix Specified'
            return None, 0
        elif control is None:
            self.message = 'No Control Mesh'
            return None, 0
        elif control.name.find('_') == -1:
            self.message = 'Not a Valid Control Mesh'
            return None, 0
        elif multV == 0:
            self.message = 'Multiplier is 0; not a good idea!'
            return None, 0
        else:
            c_nam = control.name.split('_')[0]
            m_nam = c_nam+'_'+suff
            self.message = ''
            m_obj = bpy.data.objects.get(m_nam)
            if m_obj is None:
                self.message = 'Mesh Object Not Found'+m_nam
                return None, 0
            else:
                z_cont = control.location.z * multV
            return m_obj, z_cont
