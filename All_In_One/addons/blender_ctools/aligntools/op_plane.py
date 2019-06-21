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


from collections import OrderedDict
import importlib
import itertools
import os
import math
import time

import bpy
import bpy.utils.previews
import bmesh
import bgl
import mathutils
from mathutils import Matrix, Vector

from . import utils
from . import localutils
from . import va
from . import enums
from . import funcs
from . import grouping
from . import memocoords
from . import tooldata

from .localutils.checkargs import CheckArgs
from .va import vaoperator as vaop
from .va import vaarmature as vaarm
from .va import vamath as vam
from .va import convexhull
from .va import vagl
from .va import unitsystem
from .va import manipulatormatrix
from .va import vaview3d as vav
from .enums import *
from .op_template import *


tool_data = tooldata.tool_data
memoize = tool_data.memoize
checkargs = CheckArgs(True)


@checkargs(segment_mode=['normal', 'normal2d', 'tangent2d'])
def make_plane(context, segment_mode='normal'):
    """OBJECT, EDIT_MESHのみで有効"""
    rv3d = context.region_data
    selobs = context.selected_objects
    actob = context.active_object
    actobmat = actob.matrix_world
    normal = rotation = active_co = None

    coords = []
    if context.mode == 'OBJECT':
        coords = [ob.matrix_world.to_translation() for ob in selobs]
        if len(coords) == 1:
            normal = selobs[0].matrix_world.col[2].to_3d().normalized()
            rotation = selobs[0].matrix_world.to_quaternion()

        if actob and actob in selobs:
            active_co = actob.matrix_world.to_translation()

    elif context.mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(actob.data)
        verts = [v for v in bm.verts if v.select]
        coords = [actobmat * v.co for v in verts]
        if len(coords) == 1:
            # TODO: 面を一つ選択している場合等に法線方向が真逆になる場合がある
            normal = (actobmat.to_3x3() * verts[0].normal).normalized()
            rotation = normal.to_track_quat('Z', 'Y')

        bmactive = bm.select_history.active
        if bmactive:
            if isinstance(bmactive, bmesh.types.BMVert):
                active_co = bmactive.co.copy()
            elif isinstance(bmactive, bmesh.types.BMEdge):
                active_co = (bmactive.verts[0].co + bmactive.verts[1].co) / 2
            else:
                active_co = bmactive.calc_center_median()
            active_co = actobmat * active_co

    elif context.mode == 'EDIT_ARMATURE':
        selected_bones = []
        for edit_bone in vaarm.get_visible_bones(actob):
            if edit_bone.select_head:
                # 親と接続していて、親のtailが選択状態なら追加しない
                add = True
                parent = edit_bone.parent
                if parent and edit_bone.use_connect:
                    if vaarm.bone_is_visible(actob, parent):
                        if parent.select_tail:
                            add = False
                if add:
                    coords.append(actobmat * edit_bone.head)
            if edit_bone.select_tail:
                coords.append(actobmat * edit_bone.tail)
            if edit_bone.select:
                selected_bones.append(edit_bone)
        if len(coords) == 2 and segment_mode == 'normal':
            if len(selected_bones) == 1:
                edit_bone = selected_bones[0]
                m = actobmat.to_3x3() * edit_bone.matrix.to_3x3()
                normal = m.col[1].normalized()
                rotation = m.to_quaternion()
                rotation.normalize()

    elif context.mode == 'POSE':
        selected_bones = []
        for pose_bone in vaarm.get_visible_bones(actob):
            bone = pose_bone.bone
            if bone.select_head:
                # 親と接続していて、親のtailが選択状態なら追加しない
                add = True
                parent = bone.parent
                if parent and bone.use_connect:
                    if vaarm.bone_is_visible(actob, parent):
                        if parent.select_tail:
                            add = False
                if add:
                    coords.append(actobmat * pose_bone.head)
            if bone.select_tail:
                coords.append(actobmat * pose_bone.tail)
            if bone.select:
                selected_bones.append(pose_bone)
        if len(coords) == 2 and segment_mode == 'normal':
            if len(selected_bones) == 1:
                pose_bone = selected_bones[0]
                m = actobmat.to_3x3() * pose_bone.matrix.to_3x3()
                normal = m.col[1].normalized()
                rotation = m.to_quaternion()
                rotation.normalize()

    plane = None

    if coords and normal and rotation:
        plane = vam.PlaneVector(coords[0], normal, rotation)

    elif len(coords) == 2:
        if coords[1] == active_co:
            coords.reverse()
        if segment_mode == 'normal':
            normal = (coords[1] - coords[0])
            if normal.length > 0.0:
                if active_co:
                    plane = vam.PlaneVector(active_co, normal)
                else:
                    loc = (coords[0] + coords[1]) / 2
                    plane = vam.PlaneVector(loc, normal)
        else:
            vmat3 = rv3d.view_matrix.to_3x3()
            vquat = vmat3.to_quaternion()
            viewvec = -vmat3.inverted().col[2]  # 画面手前から
            # cvec: 画面に平行で(vecs[1] - vecs[0])と垂直
            cvec = (coords[1] - coords[0]).cross(viewvec)
            if cvec.length > 0.0:
                if active_co:
                    loc = active_co
                else:
                    loc = (coords[0] + coords[1]) / 2
                if segment_mode == 'tangent2d':
                    normal = cvec
                else:  # 'normal2d'
                    vec = coords[1] - coords[0]
                    normal = vec - vec.project(viewvec)
                rotation = (vmat3 * normal).to_track_quat('Z', 'Y') * vquat
                plane = vam.PlaneVector(loc, normal, rotation)

    elif len(coords) >= 3:
        obb_mat, _obb_scale = convexhull.OBB(coords)
        if active_co:
            loc = active_co
        else:
            loc = obb_mat.col[3][:3]
        normal = obb_mat.col[2][:3]
        rotation = obb_mat.to_quaternion()
        plane = vam.PlaneVector(loc, normal, rotation)

    return plane


class OperatorPlaneDraw(bpy.types.Operator):
    """at.set_plane, at.set_axis実行の際に、確認用に一定時間planeを表示する"""
    bl_idname = 'at.plane_draw'
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = 'Plane Drawe'

    time = bpy.props.FloatProperty(default=3.0)

    handle = timer = start_time = plane = None

    location = bpy.props.FloatVectorProperty(
        name='Location',
        description='plane location',
        step=10,
        precision=3,
        subtype='XYZ')
    normal = bpy.props.FloatVectorProperty(
        name='Normal',
        description='Plane normal',
        default=(0.0, 0.0, 1.0),
        step=10,
        precision=3,
        subtype='XYZ')

    def modal(self, context, event):
        if event.type in {'INBETWEEN_MOUSEMOVE', 'NONE'}:
            return {'PASS_THROUGH'}

        fin = False
        if self.time != 0.0:
            if time.perf_counter() - self.strat_time > self.time:
                fin = True
        if not event.type.startswith('TIMER'):
            if event.type not in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE',
                                  'WINDOW_DEACTIVATE'}:
                for t in {'LEFT_CTRL', 'LEFT_ALT', 'LEFT_SHIFT', 'RIGHT_ALT',
                          'RIGHT_CTRL', 'RIGHT_SHIFT', 'OSKEY'}:
                    if event.type == t:
                        break
                else:
                    if 'MOUSE' not in event.type:
                        if event.value != 'RELEASE':  # pie menu用
                            fin = True
        if fin:
            cls = self.__class__
            bpy.types.SpaceView3D.draw_handler_remove(
                self.handle, 'WINDOW')
            context.window_manager.event_timer_remove(self.timer)
            cls.handle = cls.timer = cls.start_times = None
            context.area.tag_redraw()
            return {'PASS_THROUGH', 'FINISHED'}

        return {'PASS_THROUGH'}

    @classmethod
    def draw_handler(cls, context):
        glsettings = vagl.GLSettings(context)
        glsettings.push()

        us = unitsystem.UnitSystem(context)

        radius = 100
        verts_num = 32
        length = 50
        line_color = (1.0, 1.0, 1.0, 1.0)
        bgl.glColor4f(*line_color)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)

        r = us.bupd * radius
        with glsettings.region_view3d_space():
            bgl.glBegin(bgl.GL_LINE_LOOP)
            coords = cls.plane.same_radius_vectors(r, verts_num)
            for co in coords:
                bgl.glVertex3f(*co)
            bgl.glEnd()

            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex3f(*cls.plane.location)
            co = cls.plane.location + cls.plane.normal * us.bupd * length
            bgl.glVertex3f(*co)
            bgl.glEnd()

        glsettings.pop()

    def invoke(self, context, event):
        cls = self.__class__
        if cls.handle:
            cls.start_time = time.perf_counter()
            cls.plane = vam.PlaneVector(self.location, self.normal)
            context.area.tag_redraw()
            return {'FINISHED'}
        wm = context.window_manager
        wm.modal_handler_add(self)
        cls.handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_handler, (context,), 'WINDOW', 'POST_PIXEL')
        cls.strat_time = time.perf_counter()
        cls.timer = wm.event_timer_add(0.2, context.window)
        cls.plane = vam.PlaneVector(self.location, self.normal)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


class _OperatorSetPlane(OperatorTemplate):
    _target = 'plane'  # 'plane' or 'axis'

    segment_mode = bpy.props.EnumProperty(
        name='Segment Mode',
        items=(('normal', 'Normal', 'Plane Normal'),
               ('normal2d', 'Normal 2D', 'Plane Normal (Ignore Z depth)'),
               ('tangent2d', 'Tangent 2D', 'Plane Tangent (Ignore Z depth)')),
        default='tangent2d')
    location = bpy.props.FloatVectorProperty(
        name='Location',
        description='plane location',
        step=10,
        precision=3,
        subtype='XYZ')
    normal = bpy.props.FloatVectorProperty(
        name='Normal',
        description='Plane normal',
        default=(0.0, 0.0, 1.0),
        step=10,
        precision=3,
        subtype='XYZ')
    set_location = bpy.props.BoolProperty(
        name='Set Location',
        default=True)
    set_normal = bpy.props.BoolProperty(
        name='Set Normal',
        default=True)
    edit = bpy.props.BoolProperty(
        name='Edit',
        description='When enable, can edit location and normal',
        default=False)

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE', 'POSE'}

    def __init__(self):
        super().__init__()
        target = getattr(tool_data, self._target)
        self.plane_bak = target.copy()

    def execute(self, context):
        bpy.ops.at.fix()
        target = getattr(tool_data, self._target)
        self.plane_bak.copy_to(target)
        if not self.edit:
            plane = make_plane(context, self.segment_mode)
            if plane:
                self.location = plane.location
                self.normal = plane.normal
        if self.set_location:
            target.location = self.location
        if self.set_normal:
            target.normal = self.normal

        bpy.ops.at.plane_draw('INVOKE_DEFAULT', location=self.location,
                              normal=self.normal)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        for attr in ('segment_mode', 'location', 'normal', 'set_location',
                     'set_normal', 'edit'):
            self.draw_property(attr, layout)


class OperatorSetPlane(_OperatorSetPlane, bpy.types.Operator):
    bl_idname = 'at.set_plane'
    bl_label = 'Set Plane'
    bl_description = 'Set plane'
    bl_options = {'REGISTER', 'UNDO'}

    _target = 'plane'

    segment_mode = bpy.props.EnumProperty(
        name='Segment Mode',
        items=(('normal', 'Normal', 'Plane Normal'),
               ('normal2d', 'Normal 2D', 'Plane Normal (Ignore Z depth)'),
               ('tangent2d', 'Tangent 2D', 'Plane Tangent (Ignore Z depth)')),
        default='tangent2d')


class OperatorSetAxis(_OperatorSetPlane, bpy.types.Operator):
    bl_idname = 'at.set_axis'
    bl_label = 'Set Axis'
    bl_description = 'Set axis'
    bl_options = {'REGISTER', 'UNDO'}

    _target = 'axis'

    segment_mode = bpy.props.EnumProperty(
        name='Segment Mode',
        items=(('normal', 'Normal', 'Plane Normal'),
               ('normal2d', 'Vertical', 'Plane Normal (Ignore Z depth)'),
               ('tangent2d', 'Horizontal', 'Plane Tangent (Ignore Z depth)')),
        default='normal2d')


classes = [
    OperatorPlaneDraw,
    OperatorSetPlane,
    OperatorSetAxis,
]
