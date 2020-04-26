import bpy
from bpy.props import *
from ... base_types import AnimationNode

class GetBonesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetBonesNode"
    bl_label = "Bones From Armature Object"
    bl_width_default = 220

    Search = StringProperty(name = "Search String")
    message1 = StringProperty()

    def draw(self, layout):
        layout.prop(self, "Search")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def create(self):
        self.newInput("Object", "Armature", "arm")
        self.newOutput("Bone List", "Bones List", "boneList")

    def execute(self, arm):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if arm is None:
            return

        if arm.type == "ARMATURE":
            if self.Search != "":
                boneList = [item for item in arm.pose.bones if item.name.startswith(self.Search)]
            else:
                boneList = arm.pose.bones
            self.message1 = str(len(boneList)) + " bone(s) in list"
            if len(boneList) == 0:
                return None
            else:
                return boneList
        else:
            return None
