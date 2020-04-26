import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class CopyBoneLocationWithOffsetNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyBoneLocationWithOffsetNode"
    bl_label = "Bones Copy Location with Offset"
    bl_width_default = 180

    useX = BoolProperty(name = "Use X", default = False, update = propertyChanged)
    useY = BoolProperty(name = "Use Y", default = False, update = propertyChanged)
    useZ = BoolProperty(name = "Use Z", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Bone", "Source Bone", "source")
        self.newInput("Bone List", "Target Bone(s) List", "targets")
        self.newInput("Vector", "Offset", "offset")

    def draw(self, layout):
        layout.prop(self, "useX")
        layout.prop(self, "useY")
        layout.prop(self, "useZ")

    def execute(self, source, targets, offset):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if source is None or targets is None:
            return

        for target in targets:
            if self.useX: target.location.x = source.location.x + offset.x
            if self.useY: target.location.y = source.location.y + offset.y
            if self.useZ: target.location.z = source.location.z + offset.z
