# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
import bmesh
import math
from numpy import interp
from mathutils import noise, Vector, kdtree
from mathutils.bvhtree import BVHTree
from .ribbons_operations import HT_OT_CurvesUVRefresh
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
from .resample2d import get2dInterpol, interpol_Catmull_Rom, get_strand_proportions
from .helper_functions import calc_power, get_obj_mesh_bvht
from .hair_curve_helpers import HT_OT_EmbedRoots,  HT_OT_CurvesTiltAlign

import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils


addon_keymaps = []

def change_draw_keymap(draw_hair):
    global addon_keymaps
    if draw_hair:
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new('object.draw_hair_surf', 'LEFTMOUSE', 'PRESS', key_modifier='D')
        addon_keymaps.append((km, kmi))
        if 'Grease Pencil' in bpy.context.window_manager.keyconfigs.user.keymaps.keys():
            bpy.context.window_manager.keyconfigs.user.keymaps['Grease Pencil'].keymap_items['gpencil.annotate'].active = False
    else:
        wm = bpy.context.window_manager
        for km,kmi in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)
            if km in wm.keyconfigs.addon.keymaps.values():
                wm.keyconfigs.addon.keymaps.remove(km)
        addon_keymaps.clear()
        if 'Grease Pencil' in bpy.context.window_manager.keyconfigs.user.keymaps.keys():
            bpy.context.window_manager.keyconfigs.user.keymaps['Grease Pencil'].keymap_items['gpencil.annotate'].active = True

class ModalGPSettings(bpy.types.PropertyGroup):
    def modalHairCheck(self, context):
        change_draw_keymap(self['runModalHair'])
    
    def update_width(self, context):
        obj = context.active_object
        if obj.type !='CURVE':
            return
        if obj.ribbon_settings:  # use init settings if  they are != defaults, else use stored values
            strandResU = obj.ribbon_settings.strandResU
            strandResV = obj.ribbon_settings.strandResV
            strandPeak = obj.ribbon_settings.strandPeak
            strandUplift = obj.ribbon_settings.strandUplift
            bpy.ops.object.generate_ribbons(strandResU=strandResU, strandResV=strandResV,
                                            strandWidth=self.strand_width, strandPeak=strandPeak,
                                            strandUplift=strandUplift)
        else:
            bpy.ops.object.generate_ribbons(strandWidth=self.strand_width, alignToSurface=False)

    runModalHair: BoolProperty(name="Draw Curve Ribbons",
                               description="Draw Curve Ribbons on mesh surface, while holding D - key", default=False, update=modalHairCheck)
    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                     items=(("BEZIER", "Bezier", ""),
                                            ("NURBS", "Nurbs", ""),
                                            ("POLY", "Poly", "")))
    t_in_y: IntProperty(name="Strand Segments", default=6, min=3, max=20)
    offset_fallof: FloatProperty(name="Offset falloff", description="Offset influence over strand lenght", default=-0.85,
                                min=-1, max=1)
    offset_above: FloatProperty(name="Offset Strands", description="Offset strands above surface", default=0.2,
                               soft_min=0.01, max=1.0)
    embedValue: FloatProperty(name="Embed Roots Depth", description="Embed curve ribbons roots depth", default=0, min=0, max=10)
    use_pressure: BoolProperty(name="Use Pressure", description="Use pen pressure if available", default=True)
    alignToSurface: BoolProperty(name="Align tilt", description="Align tilt to Surface", default=True)
    strand_width: FloatProperty(name="Strand width", description="Strand width", default=0.5, min=0.0, soft_max=10, update=update_width)


class HT_PT_GP_Hair_Panel(bpy.types.Panel):
    bl_label = "Draw Hair on mesh"
    bl_idname = "gp_hair_tool"  
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hair Tool'
    bl_context = 'objectmode'

    def draw(self, context):
        modal_hair_settings = context.scene.modal_gp_curves
        layout = self.layout
        layout.prop(modal_hair_settings, 'runModalHair')
        col = layout.column(align=True)
        col.prop(modal_hair_settings, 'hairType')
        col.prop(modal_hair_settings, 't_in_y')
        col.prop(modal_hair_settings, 'strand_width')

        # if context.active_object.targetObjPointer:
        col = layout.column(align=True)
        col.prop(modal_hair_settings, 'embedValue')
        col.prop(modal_hair_settings, 'offset_fallof')
        col.prop(modal_hair_settings, 'offset_above')

        layout.prop(modal_hair_settings, 'use_pressure')
        layout.prop(modal_hair_settings, 'alignToSurface')

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

def draw_text(self, context):
    font_id = 0 
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 12, 72)
    blf.draw(font_id, "ray_origin " + str(len(self.stored_points)))

def draw_lines_callback_po(self, context):
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(3.0)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glDepthRange(0, 0.998)

    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": self.stored_points})
    shader.bind()
    shader.uniform_float("color", (1, 0.5, 0, 1))
    batch.draw(shader)

    bgl.glDepthRange(0, 1)
    bgl.glDisable(bgl.GL_DEPTH_TEST)
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)



class HT_OT_ModalDrawHair(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "object.draw_hair_surf"
    bl_label = "Draw Hair on mesh"
    bl_description = "Draw Hair on mesh surface. \\n" \
                     "If you have curve object selected strokes will be appended to this curve \\n" \
                     "otherwise new curve hair will be created."
    bl_options = {"REGISTER", "UNDO"}

    def create_curve_hair(self, context):
        modal_hair_settings = context.scene.modal_gp_curves

        Curve = self.curve_hair
        matInvCurve = Curve.matrix_world.inverted()

        t_ins = [i / (modal_hair_settings.t_in_y - 1) for i in range(modal_hair_settings.t_in_y)]  # defines output len
        t_rad = [i / (len(self.stored_pressure) - 1) for i in range(len(self.stored_pressure))]
        interpolRadList = interp(t_ins, t_rad, self.stored_pressure)
        points_resampled = interpol_Catmull_Rom([self.stored_points], modal_hair_settings.t_in_y, True)[0]
        cpow = calc_power(modal_hair_settings.offset_fallof)
        curve_length = len(points_resampled)

        for spl in Curve.data.splines:
            if modal_hair_settings.hairType == 'BEZIER':
                for p in spl.bezier_points:
                    p.select_control_point = False
            else:
                for p in spl.points:
                    p.select = False

        polyline = Curve.data.splines.new(modal_hair_settings.hairType)
        if modal_hair_settings.hairType == 'BEZIER':
            polyline.bezier_points.add(curve_length - 1)
        elif modal_hair_settings.hairType == 'POLY' or modal_hair_settings.hairType == 'NURBS':
            polyline.points.add(curve_length - 1)
        if modal_hair_settings.hairType == 'NURBS':
            polyline.order_u = 3  # like bezier thing
            polyline.use_endpoint_u = True

        for i, point in enumerate(points_resampled):
            x, y, z = matInvCurve @ Vector(point)
            if self.snap_surface_BVHT:
                snappedPoint, normalSourceSurf, index, distance = self.snap_surface_BVHT.find_nearest(point, 100)
                offset_fallof = math.pow(i / curve_length, cpow)  # 0.1 to give 1% of influence on root
                offset_above = Vector(point) + modal_hair_settings.offset_above * normalSourceSurf * offset_fallof 
                x, y, z = matInvCurve @ offset_above
            if modal_hair_settings.hairType == 'BEZIER':
                polyline.bezier_points[i].co = (x, y, z)
                polyline.bezier_points[i].handle_left_type = 'AUTO'
                polyline.bezier_points[i].handle_right_type = 'AUTO'
                polyline.bezier_points[i].select_control_point = True
            else:
                polyline.points[i].co = (x, y, z, 1)
                polyline.points[i].select = True
        if modal_hair_settings.hairType == 'BEZIER':
            polyline.bezier_points.foreach_set('radius', interpolRadList.tolist())
        else:
            polyline.points.foreach_set('radius', interpolRadList.tolist())

        
        Curve.data.resolution_u = 3
        if modal_hair_settings.embedValue > 0:
            HT_OT_EmbedRoots.embed_strands_roots(context, Curve, self.snap_surface_BVHT,  embed=modal_hair_settings.embedValue, onlySelection=True)
        if Curve.data.bevel_object == None:
            bpy.ops.object.generate_ribbons(strandWidth=modal_hair_settings.strand_width, alignToSurface=False)
        HT_OT_CurvesUVRefresh.uvCurveRefresh(Curve)
        if modal_hair_settings.alignToSurface and self.snap_surface is not None:
            HT_OT_CurvesTiltAlign.align_curve_tilt(context, Curve, self.snap_surface_BVHT, resetTilt=True, onlySelection=True)


    def hit_object(self, context, event):
        """Run this function on left mouse, execute the ray cast"""
        # get the context arguments
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        # get the ray from the viewport and mouse
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        # ray_target = ray_origin + view_vector

        def obj_ray_cast():
            # ray_direction = ray_origin - ray_target
            location, normal, face_index, depth = self.snap_surface_BVHT.ray_cast(ray_origin, view_vector)
            # success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj) #works in local space
            if location:
                return location, normal, face_index
            else:
                depth_location =  self.stored_points[-1] if self.stored_points else Vector((0, 0, 0))
                location_from_2d = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, depth_location)
                return location_from_2d, None, None

        # cast rays and find the closest object
        hit_loc_world, normal, face_index = obj_ray_cast()

        self.stored_points.append(hit_loc_world)  # save as vec
        self.stored_pressure.append(event.pressure if context.scene.modal_gp_curves.use_pressure else 1)  # save as vec
        self.step_count = 0
        

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            self.mouse_coord = event.mouse_region_x, event.mouse_region_y
            self.step_count +=1
            if self.lmb:
                self.hit_object(context, event)

        elif event.type == 'LEFTMOUSE':
            # we could handle PRESS and RELEASE individually if necessary
            # self.lmb = event.value == 'PRESS'
            if event.value == 'RELEASE':
                if len(self.stored_points) > 3:
                    self.create_curve_hair(context)
                self.stored_points.clear()
                self.stored_pressure.clear()
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self._text_handle, 'WINDOW')
                return {'FINISHED'}

        elif event.ctrl and event.type == 'Z' and event.value == 'PRESS':
            self.curve_hair.data.splines.remove(self.curve_hair.data.splines[-1])
            self.curve_hair.update_tag()

        elif event.type in {'RET'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._text_handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._text_handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        selObj = context.active_object if context.active_object else None
        if not selObj:
            self.report({'INFO'}, 'Select curve or mesh object first!')
            return {"CANCELLED"}

        if context.area.type == 'VIEW_3D':

            self.stored_points = []
            self.stored_pressure = []
            self.lmb = True
            self.step_count = 0 #get mose co, every 10 step, so that curve has less points

            modal_hair_settings = context.scene.modal_gp_curves
            if selObj.type == 'MESH':  # snap to this mesh, create curve hair
                curveData = bpy.data.curves.new('CurveFromGP', type='CURVE')
                curveData.dimensions = '3D'
                curveData.fill_mode = 'FULL'
                curveData.bevel_depth = 0.004 
                curveData.bevel_resolution = 2
                Curve = bpy.data.objects.new('CurveFromGP', curveData)
                curveData.resolution_u = 3
                context.scene.collection.objects.link(Curve)
                context.view_layer.objects.active = Curve
                # Curve.select_set(True)
                Curve.matrix_world = selObj.matrix_world
                # bpy.context.scene.update()
                Curve.targetObjPointer = selObj.name

            if selObj.type == 'CURVE':  # curve is selected so use it
                Curve = context.active_object
                if not Curve.targetObjPointer:
                    self.report({'INFO'}, 'Select curve has not target to snap to!  Cancelling!')
                    return {"CANCELLED"}

            
            snapSurface = None
            if Curve.targetObjPointer and Curve.targetObjPointer in bpy.data.objects.keys():
                snapSurface = bpy.data.objects[Curve.targetObjPointer]
            else:
                if selObj and selObj.type == 'MESH':
                    snapSurface = selObj
                    Curve.targetObjPointer = selObj.name
            if snapSurface is None:
                self.report({'INFO'}, 'There is no target to draw strokes on! Cancelling!')
                print('There is no target to draw strokes on! Select mesh obj, or hair curve ribbons with target object set')
                return {"CANCELLED"}

            self.curve_hair = Curve
            self.snap_surface = snapSurface
            self.snap_surface_BVHT = get_obj_mesh_bvht(snapSurface, context.depsgraph, applyModifiers=True, world_space=True)


            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_lines_callback_po, args, 'WINDOW', 'POST_VIEW')
            self._text_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}








