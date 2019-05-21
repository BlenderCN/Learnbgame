import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class CopyLocationWithOffsetNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyLocationWithOffsetNode"
    bl_label = "Copy Location with Offset"
    bl_width_default = 180

    useX = BoolProperty(name = "Use X", default = False, update = propertyChanged)
    useY = BoolProperty(name = "Use Y", default = False, update = propertyChanged)
    useZ = BoolProperty(name = "Use Z", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Object", "Source", "source")
        self.newInput("Object", "Target", "target")
        self.newInput("Vector", "Offset", "offset")

    def draw(self, layout):
        layout.prop(self, "useX")
        layout.prop(self, "useY")
        layout.prop(self, "useZ")

    def execute(self, source, target, offset):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if source is None or target is None:
            return

        if self.useX: target.location.x = source.location.x + offset.x
        if self.useY: target.location.y = source.location.y + offset.y
        if self.useZ: target.location.z = source.location.z + offset.z
