import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class CopyBoneRotationWithOffsetNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyBoneRotationWithOffsetNode"
    bl_label = "Copy Bone Rotation with Offset"
    bl_width_default = 180

    useW = BoolProperty(name = "Use W", default = False, update = propertyChanged)
    useX = BoolProperty(name = "Use X", default = False, update = propertyChanged)
    useY = BoolProperty(name = "Use Y", default = False, update = propertyChanged)
    useZ = BoolProperty(name = "Use Z", default = False, update = propertyChanged)
    message1 = StringProperty("")

    def create(self):
        self.newInput("Bone", "Source Bone", "source")
        self.newInput("Bone List", "Target Bone(s) List", "targets")
        self.newInput("Euler", "Offset Euler", "offset_e")
        self.newInput("Quaternion", "Offset Quaternion", "offset_q")

    def draw(self, layout):
        layout.prop(self, "useW")
        layout.prop(self, "useX")
        layout.prop(self, "useY")
        layout.prop(self, "useZ")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self, source, targets, offset_e, offset_q):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if source is None or targets is None:
            return

        for target in targets:
            if source.rotation_mode == target.rotation_mode:
                self.message1 = ""
                if  target.rotation_mode == 'QUATERNION':
                    if self.useW: target.rotation_quaternion[0] = source.rotation_quaternion[0] + offset_q[0]
                    if self.useX: target.rotation_quaternion[1] = source.rotation_quaternion[1] + offset_q[1]
                    if self.useY: target.rotation_quaternion[2] = source.rotation_quaternion[2] + offset_q[2]
                    if self.useZ: target.rotation_quaternion[3] = source.rotation_quaternion[3] + offset_q[3]
                else:
                    if self.useX: target.rotation_euler[0] = source.rotation_euler[0] + offset_e[0]
                    if self.useY: target.rotation_euler[1] = source.rotation_euler[1] + offset_e[1]
                    if self.useZ: target.rotation_euler[2] = source.rotation_euler[2] + offset_e[2]
            else:
                self.message1 = "Miss-matched Rotations"
