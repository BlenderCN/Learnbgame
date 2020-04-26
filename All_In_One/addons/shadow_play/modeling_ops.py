import os
import sys
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import bpy
from bgl import *
import bpy.utils.previews
import bmesh
from rna_prop_ui import PropertyPanel
from bpy.app.handlers import persistent
from bpy.types import (Panel, Operator, PropertyGroup, UIList, Menu)
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_extras.view3d_utils import region_2d_to_location_3d, region_2d_to_vector_3d
from bpy.props import FloatVectorProperty
from bpy.app.handlers import persistent

# depends on sklean
import numpy as np
import random
import copy
from numpy import linalg as LA
from sklearn.decomposition import PCA

class ModelingOperatorInterpreteContour(bpy.types.Operator):
    bl_idname = "modeling.interpret_contour"
    bl_label = "Interprete contour stroke"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.grease_pencil!=None)

    def invoke(self, context, event):
        gp = context.scene.grease_pencil

        obj = context.active_object
        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes
        if (strokes==None) or (len(strokes)<1):
            return {'FINISHED'}

        contour_stroke = strokes[-1]

        camera = context.scene.camera
        if camera==None:
            return {'FINISHED'}

        render = context.scene.render
        modelview_matrix = camera.matrix_world.inverted()
        projection_matrix = camera.calc_matrix_camera(render.resolution_x,render.resolution_y,render.pixel_aspect_x,render.pixel_aspect_y)

        M = projection_matrix*modelview_matrix

        points_image = []
        np_M = np.array(M)
        for point in contour_stroke.points:
            co = list(point.co)
            co.append(1.0)
            co = np.array(co)
            res = np.dot(np_M, co)
            res /= res[3]
            points_image.append(res)

        if gp.palettes:
            gp_palette = gp.palettes.active
        else:
            gp_palette = gp.palettes.new('mypalette')

        if 'black' in gp_palette.colors:
            black_col = gp_palette.colors['black']
        else:
            black_col = gp_palette.colors.new()
            black_col.name = 'black'
            black_col.color = (0.0,0.0,0.0)

        M.invert()
        np_M = np.array(M)
        res_points = []
        for i, point in enumerate(points_image):
            first = np.dot(np_M[:,0:2], point[0:2]) + np_M[:,3]
            second = np_M[:,2]
            d = -first[2]/second[2]
            res = first + d*second
            res /= res[3]
            res_points.append(res[0:3])

        points_nb = min(10, len(res_points))

        strokes.remove(contour_stroke)
        stroke = af.strokes.new(colorname=black_col.name)
        stroke.draw_mode = '3DSPACE'
        stroke.line_width = 6
        stroke.points.add(count = points_nb)

        if len(res_points)<points_nb:
            for idx in range(points_nb):
                stroke.points[idx].co = res_points[idx]
        else:
            for idx in range(points_nb):
                stroke.points[idx].co = res_points[idx*int(len(res_points)/points_nb)]

        return {'FINISHED'}

class ModelingOperatorGenerateSurface(bpy.types.Operator):
    bl_idname = "modeling.generate_surface"
    bl_label = "Generate Surface"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.grease_pencil!=None)

    def invoke(self, context, event):
        gp = context.scene.grease_pencil

        obj = context.active_object
        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes
        if (strokes==None) or (len(strokes)<1):
            return {'FINISHED'}

        contour_stroke = strokes[-1]
        contour_stroke.select = True
        bpy.ops.gpencil.convert(type='PATH')
        strokes.remove(contour_stroke)
        objs = bpy.data.objects

        select_obj = None
        for obj in objs:
            if obj.name[0:8]=='GP_Layer':
                select_obj = obj
                break

        if select_obj==None:
            return {'FINISHED'}

        bpy.context.scene.objects.active = select_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.view3d.edit_mesh_extrude_move_normal()

        return {'FINISHED'}

class ModelingOperatorOnSurface(bpy.types.Operator):
    bl_idname = "modeling.on_surface"
    bl_label = "Grease pencil on surface or 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')
        if context.scene.on_surface==True:
            context.scene.tool_settings.gpencil_stroke_placement_view3d='CURSOR'
        else:
            context.scene.tool_settings.gpencil_stroke_placement_view3d='SURFACE'

        context.scene.on_surface = not context.scene.on_surface
        return {'FINISHED'}

class ModelingOperatorInstancing(bpy.types.Operator):
    bl_idname = "modeling.instancing"
    bl_label = "Instancing"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.grease_pencil!=None) and (context.active_object!=None)

    def invoke(self, context, event):
        gp = context.scene.grease_pencil

        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes

        random.seed()

        try:
            stroke = strokes[-1]
        except IndexError:
            pass
        else:
            verts = []
            points = stroke.points
            for i in range(len(stroke.points)):
                verts.append(points[i].co)

            sampling_nb = min(context.scene.instance_nb, len(verts))
            sampling_step = len(verts)/sampling_nb

            shift = []
            for i in range(sampling_nb):
                idx = int(i*sampling_step)
                if idx<len(verts):
                    x = verts[idx].x
                    y = verts[idx].y
                    z = verts[idx].z
                    shift.append((x,y,z))

            model_obj = context.active_object

            for i in range(sampling_nb):
                new_obj = model_obj.copy()
                if (model_obj.animation_data!=None) and (model_obj.animation_data.action!=None):
                    model_fcurve_x = model_obj.animation_data.action.fcurves[0]
                    model_fcurve_y = model_obj.animation_data.action.fcurves[1]
                    model_fcurve_z = model_obj.animation_data.action.fcurves[2]
                    N = len(model_fcurve_x.keyframe_points)

                    new_obj.animation_data_create()
                    new_obj.animation_data.action = bpy.data.actions.new(name="LocationAnimation")

                    fcurve_x = new_obj.animation_data.action.fcurves.new(data_path='location', index=0)
                    fcurve_y = new_obj.animation_data.action.fcurves.new(data_path='location', index=1)
                    fcurve_z = new_obj.animation_data.action.fcurves.new(data_path='location', index=2)

                    x_pre = 0
                    z_pre = 0

                    step = max(1, int(random.gauss(0, 5)))
                    if context.scene.add_noise==True:
                        noise_t = 0.6 + random.gauss(0, 0.4)
                    else:
                        noise_t = 1.0
                    k = 0
                    while k<N:
                        frame_idx = model_fcurve_x.keyframe_points[k].co[0]
                        if k==0:
                            delta_x_cur = shift[i][0]
                            delta_y_cur = shift[i][1]
                            delta_z_cur = shift[i][2]
                        else:
                            delta_x_cur = model_fcurve_x.keyframe_points[k].co[1]-x_pre
                            delta_y_cur = model_fcurve_y.keyframe_points[k].co[1]-y_pre
                            delta_z_cur = model_fcurve_z.keyframe_points[k].co[1]-z_pre

                        if k==0:
                            x_cur = delta_x_cur
                            y_cur = delta_y_cur
                            z_cur = delta_z_cur
                        else:
                            x_cur = x_pre2 + noise_t*delta_x_cur
                            y_cur = y_pre2 + noise_t*delta_y_cur
                            z_cur = z_pre2 + noise_t*delta_z_cur
                        
                        fcurve_x.keyframe_points.insert(frame_idx, x_cur, {'FAST'})
                        fcurve_y.keyframe_points.insert(frame_idx, y_cur, {'FAST'})
                        fcurve_z.keyframe_points.insert(frame_idx, z_cur, {'FAST'})

                        x_pre = model_fcurve_x.keyframe_points[k].co[1]
                        y_pre = model_fcurve_y.keyframe_points[k].co[1]
                        z_pre = model_fcurve_z.keyframe_points[k].co[1]

                        x_pre2 = x_cur
                        y_pre2 = y_cur
                        z_pre2 = z_cur

                        k+=step
                else:
                    new_obj.location[0] = shift[i][0]
                    new_obj.location[1] = shift[i][1]
                    new_obj.location[2] = shift[i][2]
                context.scene.objects.link(new_obj)

            bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}
