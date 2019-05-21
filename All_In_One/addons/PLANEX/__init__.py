bl_info = {
    "name": "PLANEX",
    "description": "Display the stroke points intersect with the plane across the 3d cursor",
    "author": "V Ven",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    }


import bpy
import blf
from mathutils import (
            Quaternion,
            Vector,
            )
            
from math import (
            radians,
            sqrt,
            pi,
            sin,
            cos,
            )

            
from bpy_extras import view3d_utils

from bpy_extras.view3d_utils import location_3d_to_region_2d 

g_handle = None
threshold = 0.03
font_id = 0

def draw_callback_px(self, context):
    #context.object.location.x = self.value / 100.0
    v3d = context.space_data
    rv3d = v3d.region_3d
    cursor_co = bpy.context.scene.cursor_location
    strokes = getVisibleStrokes()
    draw_plane_normal = rv3d.view_rotation
    vn = Vector((0,0,1))
    vn.rotate(draw_plane_normal)
    view_dir = vn
    if(rv3d.is_perspective):
        view_dir = rv3d.view_location + rv3d.view_distance * view_dir - cursor_co


    for stroke in strokes:
        if(len(stroke) <= 1): continue
        for line in getLineFromPoints(stroke):
            coord = None
            subN = line[1] - line[0]
            t_N = -((line[0].x - cursor_co.x)* view_dir.x + (line[0].y - cursor_co.y) * view_dir.y + (line[0].z - cursor_co.z) * view_dir.z)
            t_D = subN.x * view_dir.x + subN.y * view_dir.y + subN.z * view_dir.z
            if (t_D == 0):
                coord = line[0]
                continue
            elif abs(t_N) < abs(t_D):
                t = t_N/t_D
                coord = line[0] + subN * t
            if(coord != None):
                pos = location_3d_to_region_2d(context.region,rv3d,coord)
                draw_text_in_view(pos)
            

def getLineFromPoints(points):
    p1 = None
    lines = []
    for point_co in points:
        if(p1 == None):
            p1 = point_co
            continue
        else :
            p2 = point_co
            lines.append((p1,p2))
            p1 = p2
    return lines

def draw_text_in_view(position2d):
    global font_id
    if(position2d == None):
        return
    blf.position(font_id, position2d.x - 7, position2d.y - 7, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, "X")
    

def getVisibleStrokes():
    strokeCollection = []
    for obj in bpy.data.objects:
        if obj.visible_get() == False:
            continue
        if obj.type == 'GPENCIL':
            strokes = obj.data.layers.active.active_frame.strokes
            for stroke in strokes:
                points = []
                for point in stroke.points:
                    points.append(point.co + obj.location)
                strokeCollection.append(points)
    return strokeCollection


class PlaneXOperator(bpy.types.Operator):
    bl_idname = "object.gpencil_planex"
    bl_label = "Planex"

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.value = 1
        args = (self, context)
        global g_handle
        if g_handle == None:
            g_handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        else :
            bpy.types.SpaceView3D.draw_handler_remove(g_handle, 'WINDOW')
            g_handle = None

        #context.window_manager.modal_handler_add(self)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PlaneXOperator)
def unregister():
    bpy.utils.unregister_class(PlaneXOperator)