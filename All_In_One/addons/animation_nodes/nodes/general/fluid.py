import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged
from math import hypot,asin,pi,cos

class fluidNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_fluidNode"
    bl_label = "Fluid Symulator"
    bl_width_default = 200

    # Force stored variables:
    x_1 = FloatProperty(name = 'X1', default = 0)
    x_2 = FloatProperty(name = 'X2', default = 0)
    x_3 = FloatProperty(name = 'X3', default = 0)
    y_1 = FloatProperty(name = 'Y1', default = 0)
    y_2 = FloatProperty(name = 'Y2', default = 0)
    y_3 = FloatProperty(name = 'Y3', default = 0)

    # Decay stored variables:
    c_f = IntProperty(name = "DSF", default = 0) # Start frame for decay cycle
    d_s = FloatProperty(name = "DSV", default = 0) # Last/Decayed Accel Value
    a_f = FloatProperty(name = 'DSA', default = 0) # Last Angle of fluid obj

    # Message String:
    message1 = StringProperty("")

    def draw(self, layout):
        layout.prop(self, "x_1")
        layout.prop(self, "x_2")
        layout.prop(self, "x_3")
        layout.prop(self, "y_1")
        layout.prop(self, "y_2")
        layout.prop(self, "y_3")
        layout.prop(self, "dec")
        layout.prop(self, "c_f")
        layout.prop(self, "d_s")
        layout.prop(self, "a_f")
        if self.message1 != "":
            layout.label(self.message1, icon = "ERROR")

    def create(self):
        self.newInput("Object", "Input Object", "obj")
        self.newInput("Object", "Boolean Object", "obb")
        self.newInput("Boolean", "Process Decay", "dec")
        self.newInput("Float", "Scale Factor (> 0.1)", "s_f")
        self.newInput("Integer", "Cycle Length (Frames)", "cyc")
        self.newInput("Float", "Decay Factor (0.8 - 1)", "d_f")
        self.newOutput("Float", "Acceleration Amplitude", "com")
        self.newOutput("Float", "Acceleration Angle", "ang")
        self.newOutput("Float", "X Acceleration", "ax1")
        self.newOutput("Float", "Y Acceleration", "ay1")

    def execute(self, obj, obb, dec, s_f, cyc, d_f):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if obj is None or cyc == 0 or d_f < 0.79 or d_f > 1 or s_f < 0.1:
            self.message1 = 'No Input Object/Bad Parameters'
            return 0,0,0,0
        if obb is None:
            if obj.data.shape_keys.key_blocks.find("Fluid") < 0:
                self.message1 = 'No "Fluid" Shapekey for Object'
                return 0,0,0,0

        self.message1 = ""
        frm_c = bpy.context.scene.frame_current
        inx = obj.matrix_world.decompose()[0][0]
        iny = obj.matrix_world.decompose()[0][1]
        inz = obj.matrix_world.decompose()[0][2]

        if frm_c <= (bpy.context.scene.frame_start + 2):
            # Zero everything at the start:
            self.x_1 = inx
            self.x_2 = inx
            self.x_3 = inx
            self.y_1 = iny
            self.y_2 = iny
            self.y_3 = iny
            com = 0
            ang = 0
            ax1 = 0
            ay1 = 0
            self.a_f = 0
            self.d_s = 0
            self.c_f = 0
            obj.rotation_euler.z = 0
            if obb is None:
                obj.data.shape_keys.key_blocks["Fluid"].value = 0
            else:
                obb.rotation_euler.z = 0
                obb.rotation_euler.y = 0
        else:
            self.x_3 = self.x_2
            self.x_2 = self.x_1
            self.x_1 = inx
            self.y_3 = self.y_2
            self.y_2 = self.y_1
            self.y_1 = iny
            sx1 = self.x_1 - self.x_2
            sx2 = self.x_2 - self.x_3
            ax1 = sx1 - sx2
            sy1 = self.y_1 - self.y_2
            sy2 = self.y_2 - self.y_3
            ay1 = sy1 - sy2
            if ax1 != 0 or ay1 != 0:
                com = hypot(ax1,ay1)
                ang = round(asin(abs(ay1)/com),4)
                if ax1 < 0 and ay1 >= 0:
                    ang = pi - ang
                elif ax1 < 0 and ay1 < 0:
                    ang = (pi - ang) * -1
                elif ax1 >= 0 and ay1 < 0:
                    ang = ang * -1
                elif ax1 >= 0 and ay1 >= 0:
                    ang = ang
                self.a_f = ang
                com = com * s_f
            else:
                com = 0
                ang = self.a_f

            if dec:
                # Process decay cycles:
                if self.c_f == 0:
                    self.c_f = frm_c
                else:
                    frm = frm_c - self.c_f
                    com = self.d_s * cos((frm * pi) / cyc)
                    if com < 0:
                        ang = ang - pi
                        com = abs(com)
                    self.d_s = self.d_s * d_f
            else:
                self.d_s = com
                self.c_f = 0

            if obb is None:
                obj.rotation_euler.z = ang
                obj.data.shape_keys.key_blocks["Fluid"].value = com
            else:
                obb.rotation_euler.z = ang
                obb.rotation_euler.y = com * s_f

        return com,ang,ax1,ay1
