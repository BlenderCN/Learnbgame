import bpy
from bpy.props import *
from ... base_types import AnimationNode

class boneTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_boneTransformNode"
    bl_label = "Bone World Transforms Input"
    bl_width_default = 180

    def create(self):
        self.newInput("Bone", "Bone", "bone")
        self.newOutput("Bone", "Bone", "bone")
        self.newOutput("Vector", "W-Location", "loc")
        self.newOutput("Quaternion", "W-Rotation", "rot")
        self.newOutput("Vector", "W-Scale", "scale")

    def execute(self, bone):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if bone:
            loc, rot, scale = bone.matrix.decompose()
        else:
            loc = None
            rot = None
            scale = None
        return bone, loc, rot, scale
