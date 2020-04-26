import bpy
from bpy.props import *
from mathutils import Vector
from ... base_types import AnimationNode
from ... events import propertyChanged

class rollerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_rollerNode"
    bl_label = "Roller Node"
    bl_width_default = 200

    val_x = FloatProperty(name = "Datum X", default = 0, precision = 2)
    val_y = FloatProperty(name = "Datum Y", default = 0, precision = 2)
    val_z = FloatProperty(name = "Datum Z", default = 0, precision = 2)
    cum_d = FloatProperty(name = "Cum Dist", default = 0, precision = 2)
    message1 = StringProperty("")

    def create(self):
        self.newInput("Object","Parent","obj")
        self.newOutput("Float","Delta Offset","dist")

    def draw(self,layout):
        layout.prop(self, "val_x")
        layout.prop(self, "val_y")
        layout.prop(self, "val_z")
        layout.prop(self, "cum_d")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "ERROR")

    def execute(self,obj):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if obj is None:
            return
        if len(obj.animation_data.action.fcurves) < 3:
            self.message1 = 'Too few Keyframes XY&Z'
            return
        frm = bpy.context.scene.frame_current
        if frm <= 1:
            self.message1 = ''
            self.cum_d = 0
        for i in obj.animation_data.action.fcurves[0].keyframe_points:
            key = i.co
            if key[0] == frm:
                self.val_x = key[1]
        for i in obj.animation_data.action.fcurves[1].keyframe_points:
            key = i.co
            if key[0] == frm:
                self.val_y = key[1]
        for i in obj.animation_data.action.fcurves[2].keyframe_points:
            key = i.co
            if key[0] == frm:
                self.val_z = key[1]
        return (obj.location - Vector((self.val_x,self.val_y,self.val_z)) ).length
