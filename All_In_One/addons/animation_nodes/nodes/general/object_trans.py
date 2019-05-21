import bpy
from bpy.props import *
from ... base_types import AnimationNode

class objectTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_objectTransformNode"
    bl_label = "Object World Transforms"
    bl_width_default = 180

    def create(self):
        self.newInput("Object", "Object", "obj")
        self.newOutput("Object", "Object", "obj")
        self.newOutput("Vector", "W-Location", "loc")
        self.newOutput("Quaternion", "W-Rotation", "rot")
        self.newOutput("Vector", "W-Scale", "scale")

    def execute(self, obj):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if obj:
            loc, rot, scale = obj.matrix_world.decompose()
        else:
            loc = None
            rot = None
            scale = None
        return obj, loc, rot, scale
