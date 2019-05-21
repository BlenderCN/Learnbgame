import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class BonesScaleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BonesScaleNode"
    bl_label = "Bone(s) Transform Scale"
    bl_width_default = 180

    use_s = BoolProperty(name = "Single Bone", default = True, update = AnimationNode.refresh)

    def create(self):
        if self.use_s:
            self.newInput("Bone", "Single Bone", "bone")
            self.newOutput("Bone", "Single Bone", "bone")
        else:
            self.newInput("Bone List", "Bones List", "bones")
            self.newOutput("Bone List", "Bones List", "bones")
        self.newInput("Vector", "Scale", "sclV")

    def draw(self, layout):
        layout.prop(self, "use_s")

    def getExecutionFunctionName(self):
        if self.use_s:
            return "execute_bone"
        else:
            return "execute_bones"

    def execute_bone(self, bone, sclV):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if bone:
            bone.scale = sclV
            return bone
        else:
            return None

    def execute_bones(self, bones, sclV):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if bones:
            for b in bones:
                b.scale = sclV
            return bones
        else:
            return None
