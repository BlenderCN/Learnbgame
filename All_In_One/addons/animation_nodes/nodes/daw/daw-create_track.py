import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class SeqCreateTrack(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeqCreateTrack"
    bl_label = "SEQ Create Track"
    bl_width_default = 250

    timS = StringProperty(name = "Time Signature", default = '4,4')
    ranV = IntProperty(name = "Octaves", min = 1)
    strN = StringProperty(name = "Start Note", default = 'c0')
    offF = IntProperty(name = "Sequencer Start Frame",min = 0)
    bpmV = IntProperty(name = "Beats Per Minute", min = 60, default = 120)
    seqL = IntProperty(name = "Number of Bars", min = 1, default = 10)
    makN = BoolProperty(name = "Process Notes", default = False)
    makT = BoolProperty(name = "Process Labels", default = False)
    mess = StringProperty()

    def draw(self,layout):
        layout.prop(self,"timS")
        layout.prop(self,"ranV")
        layout.prop(self,"strN")
        layout.prop(self,"offF")
        layout.prop(self,"bpmV")
        layout.prop(self,"seqL")
        layout.prop(self,"makN")
        layout.prop(self,"makT")
        col = layout.column()
        col.scale_y = 1.5
        self.invokeFunction(col, "createTrack", icon = "NEW",
            text = "Create Sequencer Track")
        if self.mess is not '':
            layout.label(self.mess, icon='INFO')

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)

    def createTrack(self):
        numV = int(self.timS.split(',')[0])     # Sig Numerator
        denV = int(self.timS.split(',')[1])     # Sig Denominator
        matO = bpy.data.materials['open']       # Open Material
        matL = bpy.data.materials['label']      # Label Material
        # Make list of standard MIDI note range
        note_list = [
            'c0','cs0','d0','ds0','e0','f0','fs0','g0','gs0','a0','as0','b0',
            'c1','cs1','d1','ds1','e1','f1','fs1','g1','gs1','a1','as1','b1',
            'c2','cs2','d2','ds2','e2','f2','fs2','g2','gs2','a2','as2','b2',
            'c3','cs3','d3','ds3','e3','f3','fs3','g3','gs3','a3','as3','b3',
            'c4','cs4','d4','ds4','e4','f4','fs4','g4','gs4','a4','as4','b4',
            'c5','cs5','d5','ds5','e5','f5','fs5','g5','gs5','a5','as5','b5',
            'c6','cs6','d6','ds6','e6','f6','fs6','g6','gs6','a6','as6','b6',
            'c7','cs7','d7','ds7','e7','f7','fs7','g7','gs7','a7','as7','b7',
            'c8','cs8','d8','ds8','e8','f8','fs8','g8','gs8','a8','as8','b8',
            'c9','cs9','d9','ds9','e9','f9','fs9','g9']
        colN = self.seqL * numV
        bpy.data.scenes['Scene'].render.fps = (self.bpmV / 60)
        bpy.data.scenes['Scene'].frame_start = 0
        bpy.data.scenes['Scene'].frame_end = colN + self.offF
        bpy.data.scenes['Scene'].render.resolution_x = 1080
        bpy.data.scenes['Scene'].render.resolution_y = 1080
        if self.makN:
            # MAke the Note Plane ojects for Time Sig and Bars
            for r in range(0,(self.ranV*12)):
                for c in range(0,colN):
                    bpy.ops.mesh.primitive_plane_add(radius=0.045,location=((c*0.1),(r*0.05),0))
                    ob = bpy.context.active_object
                    ob.scale = (1,0.5,1)
                    bpy.ops.object.transform_apply(scale=True)
                    ob.name = 'Note'
                    ob.data.materials.append(matO)
        if self.makT:
            #  Label the Bars
            for t in range(0,(self.seqL+1)):
                bpy.ops.object.text_add(radius=0.04,location=(((t*numV*0.1)-0.06),-0.08,0))
                ob = bpy.context.active_object
                ob.name = 'Bar'
                ob.data.body = str(t)
                ob.data.materials.append(matL)
                ob.select = False

            # Label the Notes, get low note index first
            ind = note_list.index(self.strN)
            for t in range(0,(self.ranV *12)):
                bpy.ops.object.text_add(radius=0.03,location=(-0.1,((t*0.05)-0.01),0.05))
                ob = bpy.context.active_object
                ob.name = 'Scale'
                ob.data.body = note_list[(ind+t)]
                ob.data.materials.append(matL)
                ob.select = False
        self.mess = 'Processed '+str(self.seqL)+' Bars & '+str(self.ranV*12)+' Notes'
