import bpy
from bpy.props import *
from ... base_types import AnimationNode

class GetBoneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetBoneNode"
    bl_label = "Bone From Armature Object"
    bl_width_default = 220

    Search = StringProperty(name = "Search String")
    message1 = StringProperty()

    def draw(self, layout):
        layout.prop(self, "Search")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def create(self):
        self.newInput("Object", "Armature", "arm")
        self.newOutput("Bone", "Single Bone", "bone_ob")

    def execute(self, arm):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if arm is None:
             None

        if arm.type == "ARMATURE":
            if self.Search != "":
                boneList = [item for item in arm.pose.bones if item.name.startswith(self.Search)]
            else:
                boneList = arm.pose.bones
            self.message1 = "First Bone of " + str(len(boneList)) + " match(es)"
            if len(boneList) > 0:
                bone_ob = boneList[0]
                return bone_ob
            else:
                self.message1 = "No Matches"
                return None
        else:
            return None
