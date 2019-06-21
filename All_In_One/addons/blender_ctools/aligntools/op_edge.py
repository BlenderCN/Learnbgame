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
from mathutils import geometry as geom

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
from .va import vabmesh as vabm
from .enums import *
from .op_template import *
from . import custom_icons

tool_data = tooldata.tool_data
memoize = tool_data.memoize
checkargs = CheckArgs(True)


def subdivide_edge_or_add_edge(bm, eve1, eve2, ivec, eps=1e-5):
    """
    eve1とeve2の直線上にisectが有るとして、
    線分上に有るならeve1とeve2の間の辺を分割する。
    外側にあるなら頂点を追加して辺を張る。
    thresholdは頂点と同座標と見做して処理を行わない為の閾値
    return:
        新規頂点, 新規辺, 状態(-2: eve1側, -1: eve1とcoが同座標, 0: eve1-eve2間,
                              1: eve2とcoが同座標, 2: eve2側)
    """
    eve = eed = None  # New
    for eed1 in eve1.link_edges:
        if eed1.other_vert(eve1) == eve2:
            break
    v = eve2.co - eve1.co
    l = v.length
    v.normalize()
    f = v.dot(ivec - eve1.co)
    if f < -eps:
        eve = bm.verts.new(ivec, eve1)
        eed = bm.edges.new((eve1, eve), eed1)
        status = -2
    elif f <= eps:
        # eve = eve1
        status = -1
    elif f < l - eps:
        fac = (ivec - eve1.co).length / l
        eed, eve = bmesh.utils.edge_split(eed1, eve1, fac)
        status = 0
    elif f <= l + eps:
        # eve = eve2
        status = 1
    else:
        eve = bm.verts.new(ivec, eve2)
        eed = bm.edges.new((eve2, eve), eed1)
        status = 2
    return eve, eed, status


class OperatorEdgeAlignToPlane(OperatorTemplate, bpy.types.Operator):
    bl_idname = 'at.edge_align_to_plane'
    bl_label = 'Edge Align to Plane'
    bl_description = 'Align edge to plane'
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.EnumProperty(
        name='Mode',
        items=(('expand', 'Expand', 'Move one side vert'),
               ('move', 'Move', 'Move both verts'),
               ('add', 'Add Verts', 'Add Verts'),
               ('subdivide', 'Add Verts & Edges',
                'Add Verts & Edges / Subdivide Edges')),
        default='expand')

    plane_offset = bpy.props.FloatProperty(
        name='Plane Offset'
    )
    axis_offset = bpy.props.FloatProperty(
        name='Axis Offset'
    )
    influence = bpy.props.FloatProperty(
        name='Influence',
        default=1.0,
        precision=3,
        step=1,
        soft_min=0.0,
        soft_max=1.0,
        subtype='NONE'
    )

    show_expand_others = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        actob = context.active_object
        mat = actob.matrix_world
        imat = mat.inverted()
        mesh = actob.data
        bm = bmesh.from_edit_mesh(mesh)

        vert_verts = vabm.vert_verts_dict(bm, select=None, hide=False)
        verts_linked = vabm.linked_vertices_list(bm, select=True, hide=False)

        plane = tool_data.plane.copy()
        plane.location += plane.normal * self.plane_offset

        for verts in verts_linked:
            # eve1: expand and move, eve2: move
            if len(verts) == 1:
                eve1 = verts[0]
                others = vert_verts[eve1]
                if len(others) == 1:
                    eve2 = others[0]
                else:
                    continue
                v1 = mat * eve1.co
                v2 = mat * eve2.co
            elif len(verts) == 2:
                eve1, eve2 = verts
                # planeに近い方をeve1とする
                v1 = mat * eve1.co
                v2 = mat * eve2.co
                if abs(plane.distance(v1)) > abs(plane.distance(v2)):
                    eve1, eve2 = eve2, eve1
                    v1, v2 = v2, v1
            else:
                continue

            if (v2 - v1).length == 0.0:
                continue
            if abs(plane.normal.dot((v2 - v1).normalized())) < EPS:
                continue

            location_bak = plane.location.copy()
            plane.location += (v1 - v2).normalized() * self.axis_offset
            vec = plane.intersect(v1, v2)
            plane.location = location_bak

            if vec:
                if self.mode == 'expand':
                    eve1.co += (imat * vec - eve1.co) * self.influence
                elif self.mode == 'move':
                    eve1.co += (imat * vec - eve1.co) * self.influence
                    eve2.co += (imat * (
                    vec - v1 + v2) - eve2.co) * self.influence
                elif self.mode == 'add':
                    v = eve1.co + (imat * vec - eve1.co) * self.influence
                    eve = bm.verts.new(v, eve1)
                    eve.select = True
                elif self.mode == 'subdivide':
                    v = eve1.co + (imat * vec - eve1.co) * self.influence
                    eve, _eed, _status = subdivide_edge_or_add_edge(
                        bm, eve1, eve2, v, EPS)
                    if eve:
                        eve.select = True

        bm.select_flush(True)
        bm.normal_update()
        bmesh.update_edit_mesh(actob.data, True, True)
        return {'FINISHED'}

    def draw(self, context):
        # Align
        box = self.draw_box(self.layout, 'Mode', '')
        column = box.column()
        self.draw_property('mode', column, text='')

        # Others
        box = self.draw_box(self.layout, 'Others', 'show_expand_others')
        column = box.column()
        if self.show_expand_others:
            self.draw_property('plane_offset', column)
            self.draw_property('axis_offset', column)
        self.draw_property('influence', column)

    def check(self, context):
        return True


class OperatorEdgeIntersect(OperatorTemplate, bpy.types.Operator):
    bl_idname = 'at.edge_intersect'
    bl_label = 'Edge Intersect'
    bl_description = 'Intersect edges'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    mode = bpy.props.EnumProperty(
        name='Mode',
        items=(('expand', 'Expand', 'Move one side vert'),
               ('add', 'Add Verts', 'Add Verts'),
               ('subdivide', 'Add Verts & Edges',
                'Add Verts & Edges / Subdivide Edges')),
        default='expand'
    )
    use_view = bpy.props.BoolProperty(
        name='Use View',
        default=True
    )
    merge = bpy.props.BoolProperty(
        name='Merge',
        default=False
    )

    def execute(self, context):
        actob = context.active_object
        mat = actob.matrix_world
        mesh = actob.data
        bm = bmesh.from_edit_mesh(mesh)

        vert_verts = vabm.vert_verts_dict(bm, select=None, hide=False)
        verts_linked = vabm.linked_vertices_list(bm, select=True, hide=False)

        vert_pairs = []
        for verts in verts_linked:
            # eve1: expand and move, eve2: move
            if len(verts) == 1:
                eve1 = verts[0]
                others = vert_verts[eve1]
                if len(others) == 1:
                    eve2 = others[0]
                    vert_pairs.append((eve1, eve2))
            elif len(verts) == 2:
                vert_pairs.append(tuple(verts))
            else:
                continue

        if len(vert_pairs) == 2:
            (eve1, eve2), (eve3, eve4) = vert_pairs
            isect1 = isect2 = None  # local coordinate system

            # geom.intersect_line_line(v1, v2, v3, v4)
            # v1-v2, v3-v4何れかの長さが0なら
            # 結果はVector((nan, nan, nan))のタプルになる

            if self.use_view and context.region_data:
                rv3d = context.region_data
                vmat = rv3d.view_matrix
                m = vmat * mat
                v1 = m * eve1.co
                v2 = m * eve2.co
                v3 = m * eve3.co
                v4 = m * eve4.co
                if (v1 - v2).length > 0.0 and (v3 - v4).length > 0.0:
                    zvec = Vector((0, 0, 1))
                    v1_z0 = Vector((v1[0], v1[1], 0))
                    v2_z0 = Vector((v2[0], v2[1], 0))
                    v3_z0 = Vector((v3[0], v3[1], 0))
                    v4_z0 = Vector((v4[0], v4[1], 0))
                    # result = geom.intersect_line_line(v1_z0, v2_z0,
                    #                                   v3_z0, v4_z0)
                    result = vam.intersect_line_line(v1_z0, v2_z0,
                                                     v3_z0, v4_z0)
                    if result is not None:
                        r1, r2 = result
                        m = mat.inverted() * vmat.inverted()
                        r = geom.intersect_line_line(v1, v2,
                                                     r1, r1 + zvec)
                        if r is not None:
                            isect1 = m * r[0]
                        r = geom.intersect_line_line(v3, v4,
                                                     r2, r2 + zvec)
                        if r is not None:
                            isect2 = m * r[0]
            else:
                v1 = eve1.co
                v2 = eve2.co
                v3 = eve3.co
                v4 = eve4.co
                if (v1 - v2).length > 0.0 and (v3 - v4).length > 0.0:
                    # result = geom.intersect_line_line(v1, v2, v3, v4)
                    result = vam.intersect_line_line(v1, v2, v3, v4)
                    if result is not None:
                        isect1, isect2 = result

            if isect1 and isect2:
                if eve1.select and eve2.select:
                    if (eve1.co - isect1).length > (eve2.co - isect1).length:
                        eve1, eve2 = eve2, eve1
                elif eve2.select:
                    eve1, eve2 = eve2, eve1

                if eve3.select and eve4.select:
                    if (eve3.co - isect2).length > (eve4.co - isect2).length:
                        eve3, eve4 = eve4, eve3
                elif eve4.select:
                    eve3, eve4 = eve4, eve3

                verts = tuple(bm.verts)
                if self.mode == 'expand':
                    eve1.co = isect1
                    eve3.co = isect2
                elif self.mode == 'add':
                    eve5 = bm.verts.new(isect1, eve1)
                    eve6 = bm.verts.new(isect2, eve3)
                elif self.mode == 'subdivide':
                    # eve1-eve2
                    eve, eed, status = subdivide_edge_or_add_edge(
                        bm, eve1, eve2, isect1, EPS)
                    if eve:
                        eve5 = eve
                    else:
                        if status == -1:
                            eve5 = eve1
                        elif status == 1:
                            eve5 = eve2
                    # eve3-eve4
                    eve, eed, status = subdivide_edge_or_add_edge(
                        bm, eve3, eve4, isect2, EPS)
                    if eve:
                        eve6 = eve
                    else:
                        if status == -1:
                            eve6 = eve3
                        elif status == 1:
                            eve6 = eve4

                if self.merge:
                    selected = []
                    for eve in verts:
                        if eve.select and not eve.hide:
                            selected.append(eve)
                            eve.select = False
                    if self.mode == 'expand':
                        eve1.select = True
                        eve3.select = True
                    elif self.mode in ('add', 'subdivide'):
                        if eve5:
                            eve5.select = True
                        if eve6:
                            eve6.select = True
                    bpy.ops.mesh.merge(False, type='CENTER', uvs=True)
                    for eve in selected:
                        if eve.is_valid:
                            eve.select = True
                else:
                    if self.mode in ('add', 'subdivide'):
                        if eve5:
                            eve5.select = True
                        if eve6:
                            eve6.select = True

        bm.normal_update()
        bmesh.update_edit_mesh(actob.data, True, True)
        return {'FINISHED'}

    def check(self, context):
        return True


class OperatorEdgeUnbend(OperatorTemplate, bpy.types.Operator):
    bl_idname = 'at.edge_unbend'
    bl_label = 'Edge Unbend'
    bl_description = 'Unbend selected edges'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    mode = bpy.props.EnumProperty(
        name='Mode',
        items=(('unbend', 'Unbend', '伸ばす。間隔は各Edgeの長さに比例'),
               ('even', 'Even', '伸ばした後、等間隔に整列する'),
               ('squash', 'Squash', '潰すように一直線にする')),
        default='unbend'
    )
    influence = bpy.props.FloatProperty(
        name='Influence',
        default=1.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        step=1,
        subtype='NONE'
    )

    def execute(self, context):
        actob = context.active_object
        bm = bmesh.from_edit_mesh(actob.data)
        edges = [e for e in bm.edges if e.select and not e.hide]
        vert_vector = {}
        paths = vabm.make_paths_from_edges(edges)
        for path in paths:
            if path[0] == path[-1] or len(path) <= 2:
                continue

            positions = [0.0]
            for eve1, eve2 in zip(path, path[1:]):
                positions.append(positions[-1] + (eve1.co - eve2.co).length)

            v1 = path[0].co
            v2 = path[-1].co
            ray = v2 - v1
            for i in range(1, len(path)):
                co = path[i].co
                if self.mode == 'squash':
                    tagvec = v1 + (co - v1).project(ray)
                elif self.mode == 'unbend':
                    position = positions[i]
                    tagvec = v1 + ray * (position / positions[-1])
                elif self.mode == 'even':
                    tagvec = v1 + ray / (len(path) - 1) * i
                vert_vector[path[i]] = tagvec - co

        for eve, v in vert_vector.items():
            eve.co += v * self.influence

        bm.normal_update()
        bmesh.update_edit_mesh(actob.data, True, True)
        return {'FINISHED'}

    def draw(self, context):
        # Align
        box = self.draw_box(self.layout, 'Mode', '')
        column = box.column()
        self.draw_property('mode', column, text='')

        # Others
        box = self.draw_box(self.layout, 'Others', '')
        column = box.column()
        self.draw_property('influence', column)

    def check(self, context):
        return True


classes = [
    OperatorEdgeAlignToPlane,
    OperatorEdgeIntersect,
    OperatorEdgeUnbend,
]
