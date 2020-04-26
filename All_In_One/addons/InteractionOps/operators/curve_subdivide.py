import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import blf
from bpy.props import (IntProperty,
                       FloatProperty,
                       BoolProperty,
                       StringProperty,
                       FloatVectorProperty)
import bmesh
import math
from math import radians, degrees
from mathutils import Vector, Matrix, Euler


def draw_curve_pts(self, context):
    coords = self.get_curve_pts() # <- sequence
    shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "POINTS", {"pos": coords})
    shader.bind()
    shader.uniform_float("color", (1, 0, 0, 1))
    batch.draw(shader)
    # pass

def draw_ui(self, context,_uidpi, _uifactor):
    prefs = bpy.context.preferences.addons['InteractionOps'].preferences
    tColor = prefs.text_color
    tKColor = prefs.text_color_key
    tCSize = prefs.text_size
    tCPosX = prefs.text_pos_x
    tCPosY = prefs.text_pos_y
    tShadow = prefs.text_shadow_toggle           
    tSColor = prefs.text_shadow_color    
    tSBlur = prefs.text_shadow_blur
    tSPosX = prefs.text_shadow_pos_x
    tSPosY = prefs.text_shadow_pos_y  
    
    iops_text = (
        ("Number of cuts", str(self.points_num)),
        )

    # FontID    
    font = 0
    blf.color(font, tColor[0], tColor[1], tColor[2], tColor[3]) 
    blf.size(font, tCSize, _uidpi)
    if tShadow:
        blf.enable(font, blf.SHADOW)
        blf.shadow(font, int(tSBlur),tSColor[0], tSColor[1], tSColor[2], tSColor[3])
        blf.shadow_offset (font, tSPosX, tSPosY)
    else:
        blf.disable(0, blf.SHADOW)

    textsize = tCSize    
    # get leftbottom corner
    offset = tCPosY
    columnoffs = (textsize * 9) * _uifactor 
    for line in reversed(iops_text):         
        blf.color(font, tColor[0], tColor[1], tColor[2], tColor[3])
        blf.position(font, tCPosX * _uifactor, offset, 0)
        blf.draw(font, line[0])               

        blf.color(font, tKColor[0], tKColor[1], tKColor[2], tKColor[3])
        textdim = blf.dimensions(0, line[1])
        coloffset = columnoffs - textdim[0] + tCPosX     
        blf.position(0, coloffset, offset, 0)
        blf.draw(font, line[1])
        offset += (tCSize + 5) * _uifactor


class IOPS_OT_CurveSubdivide(bpy.types.Operator):
    """ Subdivide Curve """
    bl_idname = "iops.curve_subdivide"
    bl_label = "CURVE: Subdivide"
    bl_options = {"REGISTER", "UNDO"}

    pairs = []

    points_num : IntProperty(
    name = "Number of cuts",
    description = "",
    default = 1
    )

    @classmethod
    def poll(self, context):
         return (context.view_layer.objects.active.type == "CURVE" and context.view_layer.objects.active.mode == "EDIT")

    def execute(self, context):
        self.subdivide(self.points_num)
        return {"FINISHED"}

    def subdivide(self, points):
        obj = bpy.context.view_layer.objects.active
        self.points_num = points
        bpy.ops.curve.subdivide(number_cuts=self.points_num)

    def get_curve_pts(self):
        obj = bpy.context.view_layer.objects.active
        pts = []
        sequence = []

        # Store selected curve points
        if obj.type == "CURVE":
            for s in obj.data.splines:
                for b in s.bezier_points:
                    if b.select_control_point:
                        pts.append(b)

        # P = (0.5)**3 * A + 3(0.5)**3 * Ha + 3(0.5) ** 3 * Hb + 0.5**3 * B

        for idx in range(len(pts) - 1):
            A   = pts[idx].co @ obj.matrix_world + obj.location
            Ahl = pts[idx].handle_left @ obj.matrix_world + obj.location 
            Ahr = pts[idx].handle_right @ obj.matrix_world + obj.location  # Ha
    
            B   = pts[idx+1].co @ obj.matrix_world + obj.location
            Bhl = pts[idx+1].handle_left @ obj.matrix_world + obj.location  # Hb
            Bhr = pts[idx+1].handle_right @ obj.matrix_world + obj.location    

            for ip in range(self.points_num):
                p = 1 / (self.points_num + 1) * (ip + 1)
                point = ((1 - p) ** 3 * A 
                        + 3 * (1 - p) ** 2 * p * Ahr 
                        + 3 * (1 - p) * p ** 2 * Bhl 
                        + p ** 3 * B)
                sequence.append(point)
        return sequence

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'MIDDLEMOUSE'}:
            # Allow navigation
            return {'PASS_THROUGH'}

        elif event.type == "WHEELDOWNMOUSE":
                if self.points_num > 1:
                    self.points_num -= 1
                self.report({"INFO"}, event.type)

        elif event.type == "WHEELUPMOUSE":
                self.points_num += 1
                self.report({"INFO"}, event.type)

        elif event.type in {"LEFTMOUSE", "SPACE"} and event.value == "PRESS":
            self.execute(context)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_curve, "WINDOW")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_ui, "WINDOW")
            return {"FINISHED"}

        elif event.type in {"RIGHTMOUSE", "ESC"}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_ui, "WINDOW")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_curve, "WINDOW")
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        preferences = context.preferences
        if context.object and context.area.type == "VIEW_3D":
            self.points_num = 1

            # Add drawing handler for text overlay rendering
            uidpi = int((72 * preferences.system.ui_scale))
            args = (self, context, uidpi, preferences.system.ui_scale)
            self._handle_ui = bpy.types.SpaceView3D.draw_handler_add(
                            draw_ui,
                            args,
                            'WINDOW',
                            'POST_PIXEL')
            args_line = (self, context)
            self._handle_curve = bpy.types.SpaceView3D.draw_handler_add(
                            draw_curve_pts,
                            args_line,
                            'WINDOW',
                            'POST_VIEW')

            self.pairs = self.get_curve_pts()
            print("----------------------------------------")
            print(self.pairs)

            # Add modal handler to enter modal mode
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "No active object, could not finish")
            return {"CANCELLED"}