import bpy
from bpy.props import *
from math import atan2, hypot, pi, cos
from ... base_types import AnimationNode
from ... events import propertyChanged

modeItems = [
    ("X-Y", "X-Y", "Use X-Y Plane", "", 0),
    ("X-Z", "X-Z", "Use X-Z Plane", "", 1),
    ("Y-Z", "Y-Z", "Use Y-Z Plane", "", 2)
]

class angleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_angleNode"
    bl_label = "Angle/Cord/Radius"
    bl_width_default = 260

    mode = EnumProperty(name = "Active Plane", default = "X-Y",
        items = modeItems, update = AnimationNode.refresh)

    message1 = StringProperty("")
    use_t = BoolProperty(name = "Use Transform Space", default = True, update = propertyChanged)

    def create(self):
        self.newInput("Object", "Fulcrum Object", "ob0")
        self.newInput("Object", "First Object", "ob1")
        self.newInput("Object", "Second Object", "ob2")
        self.newOutput("Float", "Acute/Obtuse Angle", "ang_1")
        self.newOutput("Float", "Reflex Angle", "ang_2")
        self.newOutput("Float", "Radius", "radius")
        self.newOutput("Float", "Length F-2nd", "dist")
        self.newOutput("Float", "Chord Length", "chord")

    def draw(self,layout):
        layout.prop(self, "mode")
        layout.prop(self, "use_t")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def execute(self, ob0, ob1, ob2):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if ob0 == None or ob1 == None or ob2 == None:
            return 0, 0, 0, 0, 0

        ang_1 = 0
        ang_2 = 0
        chord = 0
        radius = 0
        dist = 0

        if self.use_t:
            v0 = ob0.matrix_world.decompose()[0]
            v1 = ob1.matrix_world.decompose()[0]
            v2 = ob2.matrix_world.decompose()[0]
        else:
            v0 = ob0.location
            v1 = ob1.location
            v2 = ob2.location

        if self.mode == "X-Y":
            v1_theta = atan2( (v1.y - v0.y) , (v1.x - v0.x) )
            v2_theta = atan2( (v2.y - v0.y) , (v2.x - v0.x) )
            dist = hypot( (v2.y - v0.y) , (v2.x - v0.x) )
        elif self.mode == "X-Z":
            v1_theta = atan2( (v1.z - v0.y) , (v1.x - v0.x) )
            v2_theta = atan2( (v2.z - v0.y) , (v2.x - v0.x) )
            dist = hypot( (v2.z - v0.z) , (v2.x - v0.x) )
        elif self.mode == "Y-Z":
            v1_theta = atan2( (v1.z - v0.z) , (v1.y - v0.y) )
            v2_theta = atan2( (v2.z - v0.z) , (v2.y - v0.y) )
            dist = hypot( (v2.z - v0.z) , (v2.y - v0.y) )

        ang_0 = (v2_theta - v1_theta) * (180.0 / pi)

        if ang_0 < 0:
            ang_0 += 360.0

        if ang_0 < 180:
            ang_1 = ang_0
            ang_2 = 360 - ang_1
        else:
            ang_2 = ang_0
            ang_1 = 360 - ang_2

        if ang_1 >= 89.9999 and ang_1 < 179.99:
            radius = (dist / cos((ang_1 - 90) * (pi / 180))) / 2
            chord = (2 * pi * radius) / (360 / (180 - (2 * (ang_1 - 90))))
            self.message1 = ""
        else:
            self.message1 = "Radius/Chord only for Obtuse Angles"

        return ang_1, ang_2, radius, dist, chord
