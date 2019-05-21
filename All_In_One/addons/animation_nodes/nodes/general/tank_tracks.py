import bpy
from bpy.props import *
from ... events import propertyChanged
from math import pi, cos
from ... base_types import AnimationNode

class tankTrackNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_tankTrackNode"
    bl_label = "Caterpillar Tracks"
    bl_width_default = 240

    message1 = StringProperty("")
    message2 = StringProperty("")
    rev_b = BoolProperty(name = "Reverse Tracks", default = False, update = propertyChanged)

    def create(self):
        self.newInput("Object", "Fixer Object", "fix_o")
        self.newInput("Object", "Target Object", "trg_o")
        self.newInput("Float", "Steer Spacing", "str_s")
        self.newInput("Object", "Left track", "trk_l")
        self.newInput("Object", "Right track", "trk_r")
        self.newInput("Float", "Track Spacing", "spc")
        self.newInput("Boolean", "Reverse Track Directions", "rev_b")
        self.newInput("Float", "Location Delta", "delta")
        self.newInput("Float", "Rotation Delta", "hull_d")
        self.newInput("Float", "Steer Angle", "str_a")
        self.newInput("Float", "Fix Angle", "fix_a")
        self.newOutput("Float", "Turn Radius", "radius")

    def draw(self, layout):
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")
        if (self.message2 != ""):
            layout.label(self.message2, icon = "ERROR")

    def execute(self, fix_o, trg_o, str_s, trk_l, trk_r, spc, rev_b, delta, hull_d, str_a, fix_a):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if fix_o is None or trg_o is None or trk_l is None or trk_r is None:
            self.message2 = 'Set the Objects...'
            self.message1 = ''
            return None
        if str_s <= 0 or spc <= 0:
            self.message2 = 'Set the Variables...'
            self.message1 = ''
            return None

        self.message2 = ''
        trg_o.location.x = fix_o.location.x + str_s
        radius = 0
        res_a = abs(str_a) - abs(fix_a)
        frm = bpy.context.scene.frame_current
        if frm <= 2:
            # Zero tracks at the start.
            trk_l.location.x = 0
            trk_r.location.x = 0

        if rev_b:
            delta = delta * -1
            hull_d = hull_d * -1

        if hull_d != 0:
            # Spinning on its centre.
            self.message1 = 'Spinning on Axis'
            trk_r.location.x = trk_r.location.x - (hull_d * spc)
            trk_l.location.x = trk_l.location.x + (hull_d * spc)
        else:
            if abs(res_a) > 0.001:
                radius = (str_s / cos((pi / 2) -res_a)) / 2
            if radius < 0:
                # Left turn.
                self.message1 = 'Left Turn, Rad: ' + str(round(radius,2))
                fac = (abs(radius) - spc) / abs(radius)
                trk_l.location.x = trk_l.location.x - (delta * fac)
                trk_r.location.x = trk_r.location.x - (delta * (1/fac))
            elif radius > 0:
                # Right Turn.
                self.message1 = 'Right Turn, Rad: ' + str(round(radius,2))
                fac = (abs(radius) - spc) / abs(radius)
                trk_l.location.x = trk_l.location.x - (delta * (1/fac))
                trk_r.location.x = trk_r.location.x - (delta * fac)
            else:
                # Going straight.
                self.message1 = 'Straight'
                trk_l.location.x = trk_l.location.x - delta
                trk_r.location.x = trk_r.location.x - delta

        return radius
