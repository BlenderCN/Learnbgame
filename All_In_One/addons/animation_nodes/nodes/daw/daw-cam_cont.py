import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class SeqCamControl(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeqCamControl"
    bl_label = "SEQ Control Cam"
    bl_width_default = 200

    def create(self):
        self.newInput("Integer","Start Frame","sFrame",minValue=0)
        self.newInput("Float","Y Shift","sShift")
        self.newInput("Float","Zoom","cZoom",minValue=0.2)
        self.newOutput("Integer","Start Frame","osFrame")

    def execute(self, sFrame, sShift, cZoom):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        camObj = bpy.data.objects.get('Cam-Seq')
        camCam = bpy.data.cameras.get('Cam_Seq')
        #scObjs = [ob for ob in bpy.data.objects if ob.name.startswith('Scale')]
        frameC = bpy.context.scene.frame_current - sFrame
        if camObj is not None and camCam is not None:
            camObj.location.x =  -0.05 if frameC < 0 else (frameC*0.1) -0.05
            camObj.location.y = sShift
            camCam.ortho_scale = cZoom
        #for ob in scObjs:
        #    ob.location.x = -0.1 if frameC < 0 else (frameC*0.1) -0.1
        return sFrame
