import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from math import pi

class BoneInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BoneInputNode"
    bl_label = "Bone Transforms Input"
    bl_width_default = 180

    def create(self):
        self.newInput("Bone", "Bone", "bone")
        self.newOutput("Bone", "Bone", "bone")
        self.newOutput("Vector", "Location", "locations")
        self.newOutput("Quaternion", "Rotation", "rotations")
        self.newOutput("Vector", "Scale", "scales")

    def execute(self, bone):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if bone:
            locations = bone.location
            rotations = bone.rotation_quaternion
            scales = bone.scale
        else:
            locations = None
            rotations = None
            scales = None

        return bone, locations, rotations, scales
