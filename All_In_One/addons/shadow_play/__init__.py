# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>


bl_info = {
    "name": "ShadowPlay2.5D",
    "author": "Zhenjie Zhao",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "3D View",
    "description": "Sketch-based Shadow Play Animation Tools in 2.5D (depends on io_import_images_as_meshes.py). Attention: DO NOT import it into macOS!",
    "wiki_url": "https://zhaozj89.github.io/ShadowPlay2.5D/",
    "support": "TESTING",
    "category": "Learnbgame",
}


if "bpy" in locals():
    import importlib
    importlib.reload(view3d_ops)
    importlib.reload(modeling_ops)
    importlib.reload(sketch_ops)
    importlib.reload(subview_ops)
    improtlib.reload(backgroundcolor_ops)
else:
    from . import view3d_ops, modeling_ops, sketch_ops, subview_ops, backgroundcolor_ops

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

################################################################################
# Handlers
################################################################################
@persistent
def cursor_handler(dummy):
    cam = bpy.data.objects['Camera']
    matrix_world = cam.matrix_world
    angle = cam.rotation_euler[2]
    location = matrix_world * ( mathutils.Matrix.Rotation(angle, 4, 'Z') * mathutils.Matrix.Rotation(math.radians(-90), 4, 'X') * Vector((0,2.5,0,1)) )
    bpy.context.scene.cursor_location = location.xyz

################################################################################
# Global
################################################################################

class MySettingsProperty(PropertyGroup):
    enum_mode = EnumProperty(name='Mode',
                             description='Different drawing mode',
                             items=[('IMPORT_MODE','Import',''),
                                    ('MODELING_MODE','Modeling',''),
                                    ('ANIMATION_MODE','Animation',''),
                                    ('LIGHTING_MODE','Lighting','')],
                             default='IMPORT_MODE')

class MySettingsOperatorReset(bpy.types.Operator):
    bl_idname = 'mysettings.reset'
    bl_label = 'MySettings Reset'
    bl_options = {'REGISTER','UNDO'}

    def invoke(self, context, event):
        bpy.ops.wm.read_homefile()
        bpy.ops.wm.addon_refresh()
        return {'FINISHED'}

class MySettingsOperatorRender(bpy.types.Operator):
    bl_idname = 'mysettings.render'
    bl_label = 'MySettings Render'
    bl_options = {'REGISTER','UNDO'}

    def invoke(self, context, event):
        scene = context.scene
        scene.frame_start = 1
        scene.frame_end = context.scene.current_frame+context.scene.frame_block_nb-1

        bpy.ops.render.render(animation=True)
        return {'FINISHED'}

################################################################################
# Animation
################################################################################
# Operator
# https://wiki.blender.org/index.php/Dev:IT/2.5/Py/Scripts/Cookbook/Code_snippets/Armatures
class AnimationOperatorPuppetAddBone(bpy.types.Operator):
    bl_idname = 'animation.animation_puppet_add_bone'
    bl_label = 'Animation Puppet Add Bone'
    bl_options = {'REGISTER','UNDO'}

    def _createRig(self, name, origin, boneTable):
        bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=origin)
        ob = bpy.context.object
        ob.show_x_ray = True
        ob.name = name
        amt = ob.data
        amt.draw_type = 'STICK'
        amt.name = name+'Amt'
        amt.show_axes = True

        # Create bones
        bpy.ops.object.mode_set(mode='EDIT')
        for (bname, pname, head, tail) in boneTable:
            bone = amt.edit_bones.new(bname)
            if pname:
                parent = amt.edit_bones[pname]
                bone.use_connect = False

            bone.head = head
            bone.tail = tail
        bpy.ops.object.mode_set(mode='OBJECT')
        return ob

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None) and (context.scene.grease_pencil!=None)

    def invoke(self, context, event):
        self.obj = context.active_object
        gp = context.scene.grease_pencil

        if gp.layers==None:
            return {'FINISHED'}
        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes

        if (strokes==None):
            return {'FINISHED'}

        pre_name = None
        boneTable = []
        origin = self.obj.location
        for idx, stroke in enumerate(strokes):
            points = stroke.points
            if len(points)==0:
                continue
            else:
                tail = points[-1].co - origin
                head = points[0].co - origin

            current_name = 'bone' + str(idx)
            item = (current_name, pre_name, head, tail)
            boneTable.append(item)
            pre_name = current_name

        bent = self._createRig(self.obj.name, origin, boneTable)

        self.obj.select = True
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")

        for stroke in strokes:
            strokes.remove(stroke)
        return {'FINISHED'}

# https://blender.stackexchange.com/questions/7598/rotation-around-the-cursor-with-low-level-python-no-bpy-ops/7603#7603
class AnimationOperatorPuppetBoneDeform(bpy.types.Operator):
    bl_idname = 'animation.animation_puppet_bone_deform'
    bl_label = 'Animation Puppet Bone Deform'
    bl_options = {'REGISTER','UNDO'}

    def __init__(self):
        # print('start')
        self.counter = 0
        self.left_pressed = False
        bpy.ops.object.mode_set(mode='POSE')

    # # potential bug, be careful about it
    # def __del__(self):
    #     # print('delete')
        # bpy.ops.object.mode_set(mode='OBJECT')

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None) and (type(context.active_object.data)==bpy.types.Armature)

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                x, y = event.mouse_region_x, event.mouse_region_y
                loc = region_2d_to_location_3d(context.region, context.space_data.region_3d, (x, y), self.obj.location)
                self.pre_loc = loc

                bones = context.active_object.pose.bones
                min_dist = sys.float_info.max
                for bone in bones:
                    dist = LA.norm(np.array((loc-bone.center-self.obj.location)), 2)
                    if dist<min_dist:
                        min_dist = dist
                        self.bone = bone
                        # bone.select = True
                self.left_pressed = True
                return {'RUNNING_MODAL'}

            if event.value == 'RELEASE':
                if self.counter > context.scene.frame_block_nb:
                    context.scene.frame_block_nb = self.counter
                return {'FINISHED'}
        if (event.type == 'MOUSEMOVE') and (self.left_pressed==True):
            x, y = event.mouse_region_x, event.mouse_region_y
            loc = region_2d_to_location_3d(context.region, context.space_data.region_3d, (x, y), self.obj.location)
            self.bone.rotation_mode = 'QUATERNION'

            pivot_loc = self.bone.head + self.obj.location
            vec1 = loc - pivot_loc
            vec2 = self.pre_loc - pivot_loc
            angle = vec1.angle(vec2)
            normal = -np.cross(np.array(vec1), np.array(vec2))

            cam = bpy.data.objects['Camera']
            axis = Vector((normal[0],normal[1],normal[2])).normalized()
            quat = mathutils.Quaternion(axis, angle)
            # print(quat)

            mat = (Matrix.Translation(pivot_loc) *
                   quat.to_matrix().to_4x4() *
                   Matrix.Translation(-pivot_loc))

            self.bone.matrix = self.obj.matrix_world.inverted() * mat * self.obj.matrix_world * self.bone.matrix

            self.pre_loc = loc

            self.bone.keyframe_insert(data_path="rotation_quaternion",frame=(self.current_frame+self.counter))

            self.counter += 1

            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.obj = context.active_object
        self.current_frame = context.scene.current_frame
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class AnimationOperatorComicARAP(bpy.types.Operator):
    bl_idname = 'animation.animation_comic_arap'
    bl_label = 'Animation Comic ARAP'
    bl_options = {'REGISTER','UNDO'}

    def __init__(self):
        # print("Start Invoke")
        self.counter = 0
        self.cp_before = []
        self.cp_after = []
        self.seleted_cp = [None]
        self.leftmouse_pressed = False

    # def __del__(self):
    #     print("End Invoke")

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None) and (context.scene.grease_pencil!=None)

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                x, y = event.mouse_region_x, event.mouse_region_y
                loc = region_2d_to_location_3d(context.region, context.space_data.region_3d, (x, y), context.active_object.location)
                if len(self.cp_after)<=0:
                    return {'FINISHED'}
                min_dist = sys.float_info.max

                matrix_object = self.obj.matrix_world.inverted()
                loc_obj = np.array(matrix_object * loc)

                for co in self.cp_after:
                    cp_obj = np.array(matrix_object * co)
                    dist = LA.norm(np.array((loc_obj[0:2]-cp_obj[0:2])), 2)
                    if dist<=min_dist:
                        self.seleted_cp[0] = co
                        min_dist = dist

                if min_dist<0.05:
                    self.leftmouse_pressed = True
                return {'RUNNING_MODAL'}
            if event.value == 'RELEASE':
                if self.counter>context.scene.frame_block_nb:
                    context.scene.frame_block_nb = self.counter
                return {'FINISHED'}
        if (event.type == 'MOUSEMOVE') and (self.leftmouse_pressed==True):
            if self.seleted_cp[0]==None:
                return {'RUNNING_MODAL'}

            x, y = event.mouse_region_x, event.mouse_region_y
            loc = region_2d_to_location_3d(context.region, context.space_data.region_3d, (x, y), context.active_object.location)

            self.seleted_cp[0][0] = loc[0]
            self.seleted_cp[0][1] = loc[1]
            self.seleted_cp[0][2] = loc[2]

            # Image Deformation Using Moving Least Squares
            ncp = len(self.cp_before)
            assert(ncp==len(self.cp_after))
            matrix_object = self.obj.matrix_world.inverted()

            # compute q
            q = []
            for i in range(ncp):
                cp_obj = matrix_object * self.cp_after[i]
                q.append(np.array(cp_obj[0:2]))

            # compute q_star
            q_star = {}
            for vert in self.mesh.vertices:
                idx = vert.index
                numerator = np.zeros(2)
                w_sum = 0
                for i in range(ncp):
                    numerator += (self.weight_list[i][idx]*q[i])
                    w_sum += self.weight_list[i][idx]
                q_star[idx] = numerator / w_sum

            # compute new positions
            frame = self.current_frame+self.counter
            for vert in self.mesh.vertices:
                idx = vert.index
                f_hat = np.zeros(2)
                for i in range(ncp):
                    q_hat = q[i] - q_star[idx]
                    f_hat += np.dot(q_hat, self.A_list[i][idx])
                f_hat /= self.mu[idx]
                f_hat = f_hat/LA.norm(f_hat, 2)
                vco_new = self.res_length[idx]*f_hat + q_star[idx]
                self.mesh.vertices[idx].co[0] = vco_new[0]
                self.mesh.vertices[idx].co[1] = vco_new[1]

                if self.fcurve_x[vert.index]==None:
                    self.fcurve_x[vert.index] = self.action.fcurves.new('vertices[%d].co'%vert.index, index=0)
                self.fcurve_x[vert.index].keyframe_points.insert(frame, vco_new[0], {'FAST'})
                if self.fcurve_y[vert.index]==None:
                    self.fcurve_y[vert.index] = self.action.fcurves.new('vertices[%d].co'%vert.index, index=1)
                self.fcurve_y[vert.index].keyframe_points.insert(frame, vco_new[1], {'FAST'})

            self.counter+=1
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        gp = context.scene.grease_pencil

        if gp.layers==None:
            return {'FINISHED'}
        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes

        if (strokes==None):
            return {'FINISHED'}

        cp_after = []
        for stroke in strokes:
            points = stroke.points
            if len(points)==0:
                continue
            cp = [0,0,0]
            for point in points:
                cp[0] += point.co[0]
                cp[1] += point.co[1]
                cp[2] += point.co[2]
            cp[0] /= len(points)
            cp[1] /= len(points)
            cp[2] /= len(points)

            cp_after.append(cp)

        for stroke in strokes:
            strokes.remove(stroke)

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

        for cp in cp_after:
            stroke = af.strokes.new(colorname=black_col.name)
            stroke.draw_mode = '3DSPACE'
            stroke.line_width = 10
            stroke.points.add(count = 1)
            stroke.points[0].co = cp
            self.cp_after.append(stroke.points[0].co)

        self.cp_before = copy.deepcopy(self.cp_after)

        self.obj = context.active_object
        self.mesh = self.obj.data

        # ADD animation data
        if self.mesh.animation_data==None:
            self.mesh.animation_data_create()
            action = bpy.data.actions.new(name='PUPPET_Animation')
            self.mesh.animation_data.action = action

        self.fcurve_x = {}
        self.fcurve_y = {}
        for i in range(len(self.mesh.vertices)):
            self.fcurve_x[i] = None
            self.fcurve_y[i] = None
        self.action = self.mesh.animation_data.action

        # Image Deformation Using Moving Least Squares
        self.p = []

        ncp = len(self.cp_before)
        assert(ncp==len(self.cp_after))
        matrix_object = self.obj.matrix_world.inverted()

        for i in range(ncp):
            cp_obj = matrix_object * self.cp_before[i]
            self.p.append(np.array(cp_obj[0:2]))

        self.weight_list = []
        for i in range(ncp):
            weight = {}
            for vert in self.mesh.vertices:
                idx = vert.index
                dist = LA.norm(self.p[i]-np.array(vert.co[0:2]), 2)
                weight[idx] = 1/(dist*dist+1e-18)
                weight[idx] = min(weight[idx], 9999.0)
            self.weight_list.append(weight)

        # pre-computing p_star
        self.p_star = {}
        self.res_length = {}
        for vert in self.mesh.vertices:
            idx = vert.index
            numerator = np.zeros(2)
            w_sum = 0
            for i in range(ncp):
                numerator += (self.weight_list[i][idx]*self.p[i])
                w_sum += self.weight_list[i][idx]
            self.p_star[idx] = numerator / w_sum
            self.res_length[idx] = LA.norm(np.array(vert.co[0:2]) - self.p_star[idx], 2)

        # pre-compute mu
        self.mu = {}
        for vert in self.mesh.vertices:
            idx = vert.index
            mu = 0.0
            for i in range(ncp):
                p_hat = self.p[i] - self.p_star[idx]
                mu = mu+(self.weight_list[i][idx]*np.dot(p_hat, p_hat))
            self.mu[idx] = mu

        # pre-computing A
        self.A_list = []
        for i in range(ncp):
            A = {}
            for vert in self.mesh.vertices:
                idx = vert.index
                vo = np.array(vert.co[0:2])
                p_hat = self.p[i] - self.p_star[idx]
                v_pstar = vo - self.p_star[idx]

                m_left = np.zeros((2,2))
                m_left[0,0] = p_hat[0]
                m_left[0,1] = p_hat[1]
                m_left[1,0] = p_hat[1]
                m_left[1,1] = -p_hat[0]

                m_right = np.zeros((2,2))
                m_right[0,0] = v_pstar[0]
                m_right[0,1] = v_pstar[1]
                m_right[1,0] = v_pstar[1]
                m_right[1,1] = -v_pstar[0]

                A[idx] = np.dot(m_left,m_right.transpose())
                A[idx] = self.weight_list[i][idx]*A[idx]
            self.A_list.append(A)

        self.current_frame = context.scene.current_frame

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class AnimationOperatorComicSoft(bpy.types.Operator):
    bl_idname = 'animation.animation_comic_soft'
    bl_label = 'Animation Comic Soft'
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None) and (context.scene.grease_pencil!=None)

    def invoke(self, context, event):
        # import pdb; pdb.set_trace()
        gp = context.scene.grease_pencil

        obj = context.active_object
        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes

        if (strokes==None):
            return {'FINISHED'}

        self.current_frame = context.scene.current_frame
        mesh = obj.data
        mesh.animation_data_create()
        action = bpy.data.actions.new(name='COMIC_Animation')
        mesh.animation_data.action = action

        # Point handler
        pca = PCA(n_components=2)

        try:
            stroke = strokes[-1]
        except IndexError:
            pass
        else:
            phandler = stroke.points[0].co.xyz
            ppath = [p.co.xz for p in stroke.points]
            phandler = np.array(phandler)
            ppath = np.array(ppath) # the size is correct, amazing

            #PCA
            res = pca.fit(ppath).transform(ppath)
            res[:,1] = 0.0
            new_ppath = pca.inverse_transform(res)
            new_phandler = phandler

            # proportional based linear blend skinning
            (nframe, ndim) = new_ppath.shape
            delta_list = []
            max_val = 0.01
            def clamp(val, max_val):
                sign = np.sign(val)
                abs_val = abs(val)
                abs_val = min(abs_val, max_val)
                return sign*abs_val

            for i in range(1, nframe):
                t0 = clamp(new_ppath[i, 0] - new_ppath[i-1, 0], max_val)
                t1 = clamp(new_ppath[i, 1] - new_ppath[i-1, 1], max_val)
                delta_list.append((t0, t1))

            weight = {}
            matrix_world = obj.matrix_world
            for vert in mesh.vertices:
                v_co_world = np.array(matrix_world*vert.co)
                dist = LA.norm(v_co_world-new_phandler, 2)
                weight[vert.index] = np.exp(-dist)

            self.current_frame = context.scene.current_frame

            for vert in mesh.vertices:
                fcurve_x = action.fcurves.new('vertices[%d].co'%vert.index, index=0)
                fcurve_y = action.fcurves.new('vertices[%d].co'%vert.index, index=1)
                co_kf_x = vert.co[0]
                co_kf_y = vert.co[1]
                for i, val in enumerate(delta_list):
                    co_kf_x += weight[vert.index]*val[0]
                    co_kf_y += weight[vert.index]*val[1]
                    frame = self.current_frame + i
                    fcurve_x.keyframe_points.insert(frame, co_kf_x, {'FAST'})
                    fcurve_y.keyframe_points.insert(frame, co_kf_y, {'FAST'})

            N = len(delta_list)
            if N>context.scene.frame_block_nb:
                context.scene.frame_block_nb = N

        return {'FINISHED'}

class AnimationOperatorFollowPath(bpy.types.Operator):
    bl_idname = 'animation.animation_follow_path'
    bl_label = 'Animation Follow Path'
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object!=None) and (context.scene.grease_pencil!=None)

    def invoke(self, context, event):
        # import pdb; pdb.set_trace()
        gp = context.scene.grease_pencil

        obj = context.active_object
        ly = gp.layers.active
        if ly==None:
            return {'FINISHED'}
        af = ly.active_frame
        if af==None:
            return {'FINISHED'}
        strokes = af.strokes

        if (strokes==None):
            return {'FINISHED'}

        self.current_frame = context.scene.current_frame
        try:
            stroke = strokes[-1]
        except IndexError:
            pass
        else:
            if obj.animation_data==None:
                obj.animation_data_create()
                obj.animation_data.action = bpy.data.actions.new(name="LocationAnimation")
                len_fcurve = 0

            N = len(stroke.points)

            fcurve_x = obj.animation_data.action.fcurves.new(data_path='location', index=0)
            fcurve_y = obj.animation_data.action.fcurves.new(data_path='location', index=1)
            fcurve_z = obj.animation_data.action.fcurves.new(data_path='location', index=2)

            for i in range(N):
                frame = self.current_frame + i
                position = stroke.points[i].co
                fcurve_x.keyframe_points.insert(frame, position[0], {'FAST'})
                fcurve_y.keyframe_points.insert(frame, position[1], {'FAST'})
                fcurve_z.keyframe_points.insert(frame, position[2], {'FAST'})

            if N>context.scene.frame_block_nb:
                context.scene.frame_block_nb = N
        return {'FINISHED'}

class AnimationOperatorPreview(bpy.types.Operator):
    bl_idname = 'animation.preview'
    bl_label = 'Animation Preview'
    bl_options = {'REGISTER','UNDO'}

    def invoke(self, context, event):
        scene = context.scene
        scene.frame_start = context.scene.current_frame
        scene.frame_end = context.scene.current_frame+context.scene.frame_block_nb-1

        bpy.ops.screen.animation_play()
        if context.screen.is_animation_playing==False:
            scene.frame_current = context.scene.current_frame

        return {'FINISHED'}

################################################################################
# Recording
################################################################################
class RecordingPropertyItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name='Name', default='')
    index = bpy.props.IntProperty(name='Index', default=0)
    start_frame = bpy.props.IntProperty(name='Startframe', default=0)
    end_frame = bpy.props.IntProperty(name='Endframe', default=0)

    camera_position0 = bpy.props.FloatProperty(name='camera_position0', default=0.0)
    camera_position1 = bpy.props.FloatProperty(name='camera_position1', default=0.0)
    camera_rotation_euler = bpy.props.FloatProperty(name='camera_rotation_euler', default=0.0)

class RecordingUIListItem(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.prop(item, "name", text="", emboss=False, icon='CLIP')
        split.label('Start: %d' % item.start_frame)
        split.label('End: %d' % item.end_frame)

class RecordingOperatorListActionEdit(bpy.types.Operator):
    bl_idname = 'recording.edit'
    bl_label = 'List Action Edit'

    def invoke(self, context, event):
        index = context.scene.recording_index
        context.scene.frame_current = context.scene.recording_array[index].start_frame
        context.scene.current_frame = context.scene.recording_array[index].start_frame
        context.scene.frame_block_nb = context.scene.recording_array[index].end_frame-context.scene.recording_array[index].start_frame+1
        return {'FINISHED'}

# https://blender.stackexchange.com/questions/30444/create-an-interface-which-is-similar-to-the-material-list-box
class RecordingOperatorListActionAdd(bpy.types.Operator):
    bl_idname = 'recording.add'
    bl_label = 'List Action Add'

    def invoke(self, context, event):
        scene = context.scene

        item = scene.recording_array.add()
        item.id = len(scene.recording_array)
        item.name = 'Recording-%d'%len(scene.recording_array)
        item.index = len(scene.recording_array)
        scene.recording_index = (len(scene.recording_array)-1)

        # add camera animation
        obj = bpy.data.objects['Camera']
        if obj.animation_data==None:
            obj.animation_data_create()
            obj.animation_data.action = bpy.data.actions.new(name='LocationAnimation')
            camera_fcurve_x = obj.animation_data.action.fcurves.new(data_path='location', index=0)
            camera_fcurve_y = obj.animation_data.action.fcurves.new(data_path='location', index=1)
            camera_fcurve_rotation = obj.animation_data.action.fcurves.new(data_path='rotation_euler', index=2)
        else:
            camera_fcurve_x = obj.animation_data.action.fcurves[0]
            camera_fcurve_y = obj.animation_data.action.fcurves[1]
            camera_fcurve_rotation = obj.animation_data.action.fcurves[2]

        position = obj.location
        item.camera_position0 = position[0]
        item.camera_position1 = position[1]
        item.camera_rotation_euler = obj.rotation_euler[2]

        camera_fcurve_x.keyframe_points.insert(context.scene.current_frame, position[0], {'FAST'})
        camera_fcurve_y.keyframe_points.insert(context.scene.current_frame, position[1], {'FAST'})
        camera_fcurve_rotation.keyframe_points.insert(context.scene.current_frame, obj.rotation_euler[2], {'FAST'})

        item.start_frame = context.scene.current_frame
        item.end_frame = context.scene.current_frame+context.scene.frame_block_nb-1
        context.scene.current_frame+=context.scene.frame_block_nb
        context.scene.frame_block_nb = 100
        context.scene.frame_current = context.scene.current_frame

        return {"FINISHED"}

################################################################################
# UIs:
################################################################################
class SingleViewAnimationUIPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    bl_idname = 'OBJECT_PT_2.5d_animation'
    bl_label = 'Single View Animation'
    bl_category = 'Play2.5D'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        my_settings = scene.my_settings
        box.prop(my_settings, 'enum_mode', text='')

        if my_settings.enum_mode == 'IMPORT_MODE':
            box.operator('import_image.to_grid', text='Import', icon='FILE_FOLDER')
        elif my_settings.enum_mode == 'MODELING_MODE':
            row = box.row(align=True)
            row.prop(context.scene, 'add_noise')
            row.prop(context.scene, 'instance_nb')
            box.operator('modeling.instancing', text='Instancing', icon='BOIDS')
        elif my_settings.enum_mode == 'ANIMATION_MODE':
            box.prop(context.scene, 'enum_brushes', text='Brushes')
            box.separator()
            if (scene.enum_brushes=='FOLLOWPATH'):
                box.operator('animation.animation_follow_path', text='Update', icon='ANIM')
            elif (scene.enum_brushes=='COMIC'):
                row = box.row(align=True)
                row.operator('animation.animation_comic_soft', text='Soft', icon='ANIM')
                row.operator('animation.animation_comic_arap', text='ARAP', icon='OUTLINER_DATA_MESH')
            elif scene.enum_brushes=='PUPPET':
                row = box.row(align=True)
                row.operator('animation.animation_puppet_add_bone', text='Bone Interprete', icon='BONE_DATA')
                row.operator('animation.animation_puppet_bone_deform', text='Bone Deform', icon='OUTLINER_DATA_MESH')
        elif my_settings.enum_mode == 'LIGHTING_MODE':
            row = box.row(align=True)
            row.prop(context.scene.world, 'use_sky_paper', text='Background Color')
            # row.prop(world, 'use_sky_blend', text='Ground Color')
            # row = box.row()
            row.prop(context.scene.world, "horizon_color", text="Ground Color")
            # row.column().prop(world, "zenith_color", text='Sky Color')
            box.operator('background_color.insert', text='Insert', icon='MATCAP_13')

        layout.split()

        box = layout.box()
        box.label('Sketch Tools')
        row=box.row(align=True)
        row.operator('gpencil.draw', text='Draw', icon='BRUSH_DATA').mode='DRAW'
        row.operator('gpencil.draw', text='Eraser', icon='FORCE_CURVE').mode='ERASER'
        row=box.row(align=True)
        row.operator('modeling.interpret_contour', text='Interprete', icon='PARTICLE_DATA')
        row.operator('modeling.generate_surface', text='Generate Surface', icon='MOD_SOFT')
        row=box.row(align=True)
        if context.scene.on_surface==True:
            row.operator('modeling.on_surface', text='Surface', icon='SURFACE_NSURFACE')
        else:
            row.operator('modeling.on_surface', text='Cursor', icon='LAYER_ACTIVE')
        row.operator('sketch.cleanstrokes', text='Clean Strokes', icon='MESH_CAPSULE')

        layout.split()

        box = layout.box()
        box.label('3D Tools')
        box.prop(context.space_data, "show_floor", text="Show Floor")
        row=box.row(align=True)
        row.operator('transform.translate', text='Translate', icon='NDOF_TRANS')
        row.operator('transform.rotate', text='Rotate', icon='NDOF_TURN')
        row.operator('transform.resize', text='Scale', icon='VIEWZOOM')
        row=box.row(align=True)
        row.operator('view3d.view3d_side', text='Side View', icon='EMPTY_DATA')
        row.operator('view3d.view3d_camera', text='Camera View', icon='SCENE')
        box.operator('view3d.offscreen_draw', text='Show OverView', icon='MESH_UVSPHERE')
        # box.prop(context.active_object, "location", text="Depth", index=1)

        layout.split()

        box = layout.box()
        box.label('Utility Tools')
        # row=col.row(align=True)
        # row.prop(context.scene, "edit_mode", text="Mode")
        row=box.row(align=True)
        row.operator('object.delete', text='Delete', icon='X')
        row.operator('mysettings.reset', text='Reset', icon='HAND')
        row=box.row(align=True)
        row.operator('ed.undo', text='Undo', icon='BACK')
        row.operator('ed.redo', text='Redo', icon='FORWARD')

class MultiViewCameraUIPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    bl_idname = 'OBJECT_PT_camera_path'
    bl_label = 'Camera Path for Multi-View'
    bl_category = 'Play2.5D'

    def draw(self, context):
        layout = self.layout
        camera = context.scene.objects['Camera']

        box = layout.box()
        box.prop(camera, 'location', text='LF/RT', index=0)
        box.prop(camera, 'location', text='FWD/BWD', index=1)
        box.prop(camera, 'rotation_euler', text='Rotation', index=2)

        box.label('Recording')
        row = box.row(align=True)
        col = row.column()
        col.template_list('RecordingUIListItem', '', context.scene, 'recording_array', context.scene, 'recording_index', rows=2)
        row = box.row(align=True)
        row.operator('recording.add', icon='ZOOMIN', text='Add')
        row.operator('recording.edit', icon='SEQ_SEQUENCER', text='Edit')

        row = box.row(align=True)
        row.prop(context.scene, 'current_frame', text='Start')
        row.prop(context.scene, 'frame_block_nb', text='Number')
        box.prop(context.scene, 'frame_current', text='Current')
        if context.screen.is_animation_playing==True:
            box.operator("animation.preview", text="Pause", icon='PAUSE')
        else:
            box.operator('animation.preview', text='Preview', icon='RIGHTARROW')

class RenderingUIPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    bl_idname = 'OBJECT_PT_rendering'
    bl_label = 'Rendering'
    bl_category = 'Play2.5D'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column()
        col.operator('mysettings.render', text='Rendering', icon='COLORSET_03_VEC')
        col.separator()
        col.prop(context.scene.render, "filepath", text="")

################################################################################
# Logic:
################################################################################

def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.my_settings = PointerProperty(type=MySettingsProperty)

    # modeling
    bpy.types.Scene.on_surface = bpy.props.BoolProperty(name='on_surface', default=False)
    bpy.types.Scene.add_noise = bpy.props.BoolProperty(name='Animation Noise', default=False)
    bpy.types.Scene.instance_nb = bpy.props.IntProperty(name='Number', default=6)
    bpy.types.Scene.plane_modeling_smalldepth = bpy.props.FloatProperty(name='small_depth', default=0.0)

    # Animation
    bpy.types.Scene.enum_brushes = bpy.props.EnumProperty(name='Brushes',
                                                description='Stylized Brushes',
                                                items=[('','',''),
                                                       ('FOLLOWPATH','Following Path',''),
                                                       ('COMIC','Comic Style',''),
                                                       ('PUPPET','Shadow Puppet Style','')],
                                                default='')
    bpy.types.Scene.current_frame = bpy.props.IntProperty(name="current_frame", default=1)
    bpy.types.Scene.frame_block_nb = bpy.props.IntProperty(name='frame_block_nb', default=100)

    # Recording
    bpy.types.Scene.recording_array = bpy.props.CollectionProperty(type=RecordingPropertyItem)
    bpy.types.Scene.recording_index = bpy.props.IntProperty()

    bpy.app.handlers.scene_update_post.append(cursor_handler)

def unregister():
    del bpy.types.Scene.my_settings

    # modeling
    del bpy.types.Scene.on_surface
    del bpy.types.Scene.add_noise
    del bpy.types.Scene.instance_nb
    del bpy.types.Scene.plane_modeling_smalldepth

    # Animation
    del bpy.types.Scene.enum_brushes
    del bpy.types.Scene.current_frame
    del bpy.types.Scene.frame_block_nb

    # Recording
    del bpy.types.Scene.recording_array
    del bpy.types.Scene.recording_index

    bpy.app.handlers.scene_update_post.remove(cursor_handler)

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__" :
    register()
