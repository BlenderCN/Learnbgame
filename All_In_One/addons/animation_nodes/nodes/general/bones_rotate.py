import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from math import pi

class BonesRotateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BonesRotateNode"
    bl_label = "Bone(s) Transform Rotate"
    bl_width_default = 180

    use_d = BoolProperty(name = "Use Degrees", default = False, update = propertyChanged)
    use_s = BoolProperty(name = "Single Bone", default = True, update = AnimationNode.refresh)

    def create(self):
        if self.use_s:
            self.newInput("Bone", "Single Bone", "bone")
            self.newOutput("Bone", "Single Bone", "bone")
        else:
            self.newInput("Bone List", "Bones List", "bones")
            self.newOutput("Bone List", "Bones List", "bones")
        self.newInput("Float", "W Rot", "loc_w")
        self.newInput("Float", "X Rot", "loc_x")
        self.newInput("Float", "Y Rot", "loc_y")
        self.newInput("Float", "Z Rot", "loc_z")

    def draw(self, layout):
        layout.prop(self, "use_d")
        layout.prop(self, "use_s")

    def getExecutionFunctionName(self):
        if self.use_s:
            return "execute_bone"
        else:
            return "execute_bones"

    def execute_bone(self, bone, loc_w, loc_x, loc_y, loc_z):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if bone:
            if bone.rotation_mode == 'QUATERNION':
                bone.rotation_quaternion.w = loc_w
                if self.use_d:
                    bone.rotation_quaternion.x = (loc_x * pi /180)
                    bone.rotation_quaternion.y = (loc_y * pi /180)
                    bone.rotation_quaternion.z = (loc_z * pi /180)
                else:
                    bone.rotation_quaternion.x = loc_x
                    bone.rotation_quaternion.y = loc_y
                    bone.rotation_quaternion.z = loc_z
            else:
                if self.use_d:
                    bone.rotation_euler.x = (loc_x * pi /180)
                    bone.rotation_euler.y = (loc_y * pi /180)
                    bone.rotation_euler.z = (loc_z * pi /180)
                else:
                    bone.rotation_euler.x = loc_x
                    bone.rotation_euler.y = loc_y
                    bone.rotation_euler.z = loc_z

        return bone

    def execute_bones(self, bones, loc_w, loc_x, loc_y, loc_z):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if bones:
            for b in bones:
                if b.rotation_mode == 'QUATERNION':
                    b.rotation_quaternion.w = loc_w
                    if self.use_d:
                        b.rotation_quaternion.x = (loc_x * pi /180)
                        b.rotation_quaternion.y = (loc_y * pi /180)
                        b.rotation_quaternion.z = (loc_z * pi /180)
                    else:
                        b.rotation_quaternion.x = loc_x
                        b.rotation_quaternion.y = loc_y
                        b.rotation_quaternion.z = loc_z
                else:
                    if self.use_d:
                        b.rotation_euler.x = (loc_x * pi /180)
                        b.rotation_euler.y = (loc_y * pi /180)
                        b.rotation_euler.z = (loc_z * pi /180)
                    else:
                        b.rotation_euler.x = loc_x
                        b.rotation_euler.y = loc_y
                        b.rotation_euler.z = loc_z

        return bones
