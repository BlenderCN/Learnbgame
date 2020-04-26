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


import collections.abc
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
from . import op_stubs
from . import custom_icons

tool_data = tooldata.tool_data
memoize = tool_data.memoize
checkargs = CheckArgs(True)


def calc_group_to_plane_vector(
        context, groups, space, axis, individual_orientation=None,
        trans_axis_offset=0.0, influence=0.0, eps=1e-5, plane=None,
        plane_attr=None):
    """各GroupのpivotからplaneへのVectorを求める
    :type context: bpy.types.Context
    :type groups: Groups
    :type space: str | Space
    :type axis: str | Axis
    :type individual_orientation: bool | None
    :type trans_axis_offset: float
    :type influence: float
    :param eps: 計算誤差としての閾値
    :type eps: int | float
    :param plane: 指定されなければtool_data.planeを用いる
    :type plane: vam.PlaneVector | None
    :param plane_attr: planeの代わりにGroupの属性を参照する
    :type plane_attr: str
    :rtype: dict[Group, Vector]
    """

    def calc_tvec(plane, trans_axis, loc):
        location_bak = plane.location.copy()
        plane.location += trans_axis * trans_axis_offset
        isect = plane.intersect(loc, loc + trans_axis)
        plane.location = location_bak
        return (isect - loc) * influence

    if plane is None:
        plane = tool_data.plane

    axis = Axis.get(axis)

    group_tvec = {}
    for group in groups:
        """:type: Group"""
        if plane_attr:
            plane = getattr(group, plane_attr)
        orientation = group.get_orientation(
            context, space, True, individual_orientation)
        if not orientation:
            continue
        trans_axis = orientation.col[axis.value - 1]
        if abs(plane.normal.dot(trans_axis)) < eps:
            continue
        if group.pivot is None:
            continue
        vec = calc_tvec(plane, trans_axis, group.pivot)
        group_tvec[group] = vec

    return group_tvec


def groups_align_to_plane(
        context, groups, space, axis, individual_orientation=None,
        trans_axis_offset=0.0, influence=0.0, eps=1e-5, plane=None,
        plane_attr=None):
    """各Groupのpivotを基準にplaneへ移動する。pivotはあらかじめ計算して
    pivot属性に代入しておくこと
    :type context: bpy.types.Context
    :type groups: Groups
    :type space: str | Space
    :type axis: str | Axis
    :type individual_orientation: bool | None
    :type trans_axis_offset: float
    :type influence: float
    :param eps: 計算誤差としての閾値
    :type eps: int | float
    :param plane: 指定されなければtool_data.planeを用いる
    :type plane: vam.PlaneVector | None
    :param plane_attr: planeの代わりにGroupの属性を参照する
    :type plane_attr: str
    :rtype: None
    """

    group_tvec = calc_group_to_plane_vector(
        context, groups, space, axis, individual_orientation,
        trans_axis_offset, influence, eps, plane, plane_attr)

    groups.translate(context, group_tvec)
    if context.mode == 'OBJECT':
        objects = [bpy.data.objects[name]
                   for name in itertools.chain.from_iterable(groups)]
    else:
        objects = None
    funcs.update_tag(context, objects)


class OperatorAlignToPlane(OperatorTemplateGroup,
                           OperatorTemplateModeSave,
                           OperatorTemplateTranslation,
                           bpy.types.Operator):
    bl_idname = 'at.align_to_plane'
    bl_label = 'Align to Plane'
    bl_description = 'Align to plane'
    bl_options = {'REGISTER', 'UNDO'}

    plane_offset = bpy.props.FloatProperty(
        name='Plane Offset',
        subtype='DISTANCE')
    axis_offset = bpy.props.FloatProperty(
        name='Axis Offset',
        subtype='DISTANCE')
    influence = bpy.props.FloatProperty(
        name='Influence',
        default=1.0,
        step=1,
        precision=3,
        soft_min=0.0,
        soft_max=1.0,
        subtype='NONE')

    use_event = bpy.props.BoolProperty(options={'HIDDEN', 'SKIP_SAVE'})

    show_expand_others = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE', 'POSE'}

    def execute(self, context):
        bpy.ops.at.fix()
        memocoords.cache_init(context)
        if self.space == 'AXIS':
            self.axis = 'Z'
        groups = self.groups = self.make_groups(context)
        plane = tool_data.plane.copy()
        plane.location += plane.normal * self.plane_offset

        groups_align_to_plane(
            context, groups, self.space, self.axis, None, self.axis_offset,
            self.influence, EPS, plane)

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.use_event:
            if event.shift:
                if self.space == 'GLOBAL':
                    self.space = 'LOCAL'
        return self.execute(context)

    def draw(self, context):
        op_stubs.OperatorResetProperties.set_operator(self)

        # Axis
        attrs = ['space', 'axis', 'individual_orientation']
        box = self.draw_box(self.layout, 'Axis', '',
                            reset_attrs=attrs)
        column = box.column(align=True)
        # if self.show_expand_axis:
        self.draw_property('space', column, text='')
        prop = self.draw_property(
            'axis', column, text='', row=True, expand=True)
        if self.space == 'AXIS':
            prop.active = False
        column = box.column()
        column.active = self.is_valid_individual_orientation(
            self.space, self.groups.Group)
        self.draw_property('individual_orientation', column)

        # Group
        self.draw_group_boxes(context, self.layout)

        # Others
        attrs = ['plane_offset', 'axis_offset', 'influence']
        box = self.draw_box(self.layout, 'Others', 'show_expand_others',
                            reset_attrs=attrs)
        column = box.column()
        if self.show_expand_others:
            self.draw_property('plane_offset', column)
            self.draw_property('axis_offset', column)
        self.draw_property('influence', column)


class _OperatorTemplateAlign(OperatorTemplateGroup,
                             OperatorTemplateModeSave,
                             OperatorTemplateTranslation):
    auto_axis = bpy.props.BoolProperty(
        name='Auto Axis',
        default=True
    )
    relative_to = bpy.props.EnumProperty(
        name='Relative To',
        items=(('ACTIVE_GROUP', 'Active Group', 'Active Group'),
               ('ACTIVE', 'Active', 'Active object / bone / vertex'),
               ('CENTER', 'Center', 'Bounding box center'),
               ('CURSOR', '3D Cursor', ''),
               ('SCENE', 'Scene Origin', '')),
        default='ACTIVE_GROUP',
    )
    influence = bpy.props.FloatProperty(
        name='Influence',
        default=1.0,
        step=1,
        precision=3,
        soft_min=0.0,
        soft_max=1.0,
        subtype='NONE'
    )

    use_event = bpy.props.BoolProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def __init__(self):
        super().__init__()
        self.groups_all = None

    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE', 'POSE')

    def recalc_group_pivots(self, context, groups, mode, space, axis):
        """self.align_mode,self.align_axisによりpivotを再計算"""
        axis_index = ('X', 'Y', 'Z').index(axis)
        for group in groups:
            if mode == 'PIVOT':
                group.pivot = group.calc_pivot(
                    context, self.pivot_point, self.pivot_point_bb_position,
                    self.head_tail, tool_data.plane,
                    self.pivot_point_target_distance,
                    fallback=PivotPoint.CENTER)
            else:
                group.bb_type = BoundingBox.AABB
                group.bb_space = space
                group.individual_orientation = False
                position = [0.0, 0.0, 0.0]  # 'CENTER', 'DIMENSION'はこのまま
                if mode == 'NEGATIVE':
                    position[axis_index] = -1.0
                elif mode == 'POSITIVE':
                    position[axis_index] = 1.0
                group.pivot = group.calc_pivot(
                    context, PivotPoint.BOUNDING_BOX, position=position)
                group.individual_orientation = self.individual_orientation
        return True

    def _calc_groups_all_bb_center(self, context, space):
        """全ての要素でGroupsを作成してAABBの中心を返す"""
        if self.groups_all is None:
            self.groups_all = groups = grouping.context_groups(
                context, GroupType.ALL, ObjectData[self.object_data],
                BoundingBox.AABB, Space[space])
        else:
            groups = self.groups_all
            groups.object_data = ObjectData[self.object_data]
            groups.bb_space = Space[space]
            groups.update(context)
        if not groups:
            return None
        loc = groups[0].bb_mat.col[3].to_3d()
        if space == 'REGION':
            vav.unproject(context.region, context.region_data, loc)
        else:
            return loc

    def _calc_pivots_center(self, context, groups):
        """各GroupのpivotでAABBを求め、その中心を返す"""
        pivots = [g.pivot for g in groups]
        min_vec = Vector([min(pivots, key=lambda v: v[i])[i]
                          for i in range(3)])
        max_vec = Vector([max(pivots, key=lambda v: v[i])[i]
                          for i in range(3)])
        return (min_vec + max_vec) / 2

    def calc_relative_to(self, context, groups, space):
        """self.relative_toから移動時のpivotを求める"""
        if self.relative_to == 'ACTIVE_GROUP':  # group_typeがALLだと移動しない
            group = groups.get_active(context)
            if group:
                if isinstance(group, (list, tuple)):
                    loc = self._calc_pivots_center(context, group)
                else:
                    loc = group.pivot.copy()
            else:
                loc = self._calc_pivots_center(context, groups)
        elif self.relative_to == 'ACTIVE':
            loc = funcs.get_active_coord(context, self.head_tail)
            if not loc:
                loc = self._calc_pivots_center(context, groups)
        elif self.relative_to == 'CENTER':
            loc = self._calc_groups_all_bb_center(context, space)
        elif self.relative_to == 'CURSOR':
            loc = context.scene.cursor_location
        elif self.relative_to == 'SCENE':
            loc = Vector((0, 0, 0))
        else:
            loc = tool_data.plane.location.copy()
        return loc


class OperatorAlign(_OperatorTemplateAlign, bpy.types.Operator):
    bl_idname = 'at.align'
    bl_label = 'Align'
    bl_description = 'Align'
    bl_options = {'REGISTER', 'UNDO'}

    align_space = bpy.props.EnumProperty(
        name='Align Space',
        items=orientation_enum_items(),
        default='GLOBAL',
    )
    align_axis = bpy.props.EnumProperty(
        name='Align Axis',
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', '')),
        default={'X'},
        options={'ENUM_FLAG'},
    )

    def align_mode_items(self, context):
        pcol = custom_icons.preview_collections['icon32']
        items = (('NEGATIVE', 'Negative Sides', '',
                  pcol['mode_negative'].icon_id, 1),
                 ('CENTER', 'Centers', '',
                  pcol['mode_center'].icon_id, 0),  # 0: default
                 ('POSITIVE', 'Positive Sides', '',
                  pcol['mode_positive'].icon_id, 2),
                 ('PIVOT', 'Group Pivot', '',
                  pcol['mode_pivot'].icon_id, 3))
        OperatorAlign._align_mode_items = items
        return items

    align_mode = bpy.props.EnumProperty(
        name='Align Mode',
        items=align_mode_items
    )

    # show_expand_others = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.at.fix()
        memocoords.cache_init(context)

        if not self.align_axis:
            return {'FINISHED'}

        if self.align_space == 'AXIS':
            self.align_axis |= {'Z'}
        if self.space == 'AXIS':
            self.axis = 'Z'
        groups = self.groups = self.make_groups(context)
        if not groups:
            return {'FINISHED'}

        # 整列対象の平面
        omat = funcs.get_orientation(context, self.align_space)
        if not omat:
            return {'CANCELLED'}

        group_trans_vectors = {}
        for i, ax in enumerate(['X', 'Y', 'Z']):
            if ax not in self.align_axis:
                continue

            # pivotの再計算
            self.recalc_group_pivots(context, groups, self.align_mode,
                                     self.align_space, ax)

            plane_normal = omat.col[i]
            plane_loc = self.calc_relative_to(context, groups,
                                              self.align_space)
            plane = vam.PlaneVector(plane_loc, plane_normal)

            if self.auto_axis or len(self.align_axis) > 1:
                space = self.align_space
                axis = ax
            else:
                space = self.space
                axis = self.axis

            group_tvec = calc_group_to_plane_vector(
                context, groups, space, axis, None, 0.0, self.influence, EPS,
                plane)
            for g, v in group_tvec.items():
                if g in group_trans_vectors:
                    group_trans_vectors[g] = group_trans_vectors[g] + v
                else:
                    group_trans_vectors[g] = v

        groups.translate(context, group_trans_vectors)
        if context.mode == 'OBJECT':
            objects = [bpy.data.objects[name]
                       for name in itertools.chain.from_iterable(groups)]
        else:
            objects = None
        funcs.update_tag(context, objects)

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.use_event:
            if event.shift:
                if self.align_space == 'GLOBAL':
                    self.align_space = 'LOCAL'
        return self.execute(context)

    def draw(self, context):
        op_stubs.OperatorResetProperties.set_operator(self)

        # Align
        # box = self.draw_box(self.layout, 'Align', 'show_expand_align')
        attrs = ['align_space', 'align_axis', 'align_mode', 'relative_to']
        box = self.draw_box(self.layout, 'Align', '', reset_attrs=attrs)
        column = box.column(align=True)
        self.draw_property('align_space', column, text='')
        prop = self.draw_property(
            'align_axis', column, text='', row=True, expand=True)
        if self.align_space == 'AXIS':
            prop.active = False
        column = box.column(align=True)
        self.draw_property('align_mode', column, text='Mode')
        self.draw_property('relative_to', column)

        # Translation Axis
        attrs = ['auto_axis', 'space', 'axis', 'individual_orientation']
        box = self.draw_box(self.layout, 'Translation Axis',
                            '', reset_attrs=attrs)
        column = box.column()
        if len(self.align_axis) > 1:
            column.active = False
        self.draw_property('auto_axis', column)
        if not self.auto_axis:
            column = box.column(align=True)
            if len(self.align_axis) > 1:
                column.active = False
            self.draw_property('space', column, text='')
            prop = self.draw_property(
                'axis', column, text='', row=True, expand=True)
            if self.space == 'AXIS':
                prop.active = False

        column = box.column()
        column.active = self.groups and self.is_valid_individual_orientation(
            self.space, self.groups.Group)
        self.draw_property('individual_orientation', column)

        # Group
        self.draw_group_boxes(context, self.layout)

        # Others
        # box = self.draw_box(self.layout, 'Others', 'show_expand_others')
        attrs = ['influence']
        box = self.draw_box(self.layout, 'Others', '', reset_attrs=attrs)
        column = box.column()
        self.draw_property('influence', column)


###############################################################################
# Distribute Objects
###############################################################################
class OperatorDistribute(_OperatorTemplateAlign, bpy.types.Operator):
    bl_idname = 'at.distribute'
    bl_label = 'Distribute'
    bl_description = 'オブジェクトの分布'
    bl_options = {'REGISTER', 'UNDO'}

    distribution_space = bpy.props.EnumProperty(
        name='Distribution Space',
        items=orientation_enum_items(),
        default='GLOBAL',
    )
    distribution_axis = bpy.props.EnumProperty(
        name='Distribution Axis',
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', '')),
        default={'X'},
        options={'ENUM_FLAG'},
    )

    def distribution_mode_items(self, context):
        pcol = custom_icons.preview_collections['icon32']
        items = (('DIMENSION', 'Dimension', 'Use Group dimensions',
                  pcol['mode_dimension'].icon_id, 1),
                 ('NEGATIVE', 'Negative Sides', '',
                  pcol['mode_negative'].icon_id, 2),
                 ('CENTER', 'Centers', '',
                  pcol['mode_center'].icon_id, 0),  # 0: default
                 ('POSITIVE', 'Positive Sides', '',
                  pcol['mode_positive'].icon_id, 3),
                 ('PIVOT', 'Group Pivot', '',
                  pcol['mode_pivot'].icon_id, 4))
        OperatorDistribute._distribution_mode_items = items
        return items

    distribution_mode = bpy.props.EnumProperty(
        name='Distribution Mode',
        description='',
        items=distribution_mode_items,
    )
    use_auto_spacing = bpy.props.BoolProperty(
        name='Auto Spacing',
        default=True)
    spacing = bpy.props.FloatProperty(
        name='Spacing',
        description='use_auto_spacingがFalseの場合に使用')

    use_threshold = bpy.props.BoolProperty(
        name='Use Threshold',
        description='距離が近い物同士を纏める',
        default=True)
    threshold = bpy.props.FloatProperty(
        name='Threshold',
        default=1e-4,
        precision=6,
        step=0.01,
        min=0.0,
        soft_min=0.0)

    show_expand_distribution = bpy.props.BoolProperty()

    show_expand_others = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return True

    def calc_tvec(self, plane, trans_axis, center):
        """移動用のVectorを求める"""
        isect = plane.intersect(center, center + trans_axis)
        return (isect - center) * self.influence

    def execute(self, context):
        bpy.ops.at.fix()
        memocoords.cache_init(context)

        if not self.distribution_axis:
            return {'FINISHED'}

        if self.distribution_space == 'AXIS':
            self.distribution_axis |= {'Z'}
        if self.space == 'AXIS':
            self.axis = 'Z'
        groups = self.groups = self.make_groups(context)
        if len(groups) <= 2:
            return {'FINISHED'}

        omat = funcs.get_orientation(context, self.distribution_space)
        if not omat:
            return {'CANCELLED'}

        group_trans_vectors = {}
        for i, ax in enumerate(['X', 'Y', 'Z']):
            if ax not in self.distribution_axis:
                continue
            # 移動軸用のPlane作成
            distribution_axis = omat.col[i]
            plane = vam.PlaneVector((0, 0, 0), distribution_axis)

            # pivot再計算
            self.recalc_group_pivots(
                context, groups, self.distribution_mode,
                self.distribution_space, ax)

            # 全てのGroupのpivotが直線(distribution_axis)になるように修正する
            vec = groups[0].pivot
            for group in groups:
                v = group.pivot - vec
                group.pivot = v.project(distribution_axis) + vec

            # 分割数の計算: group.temp_position
            for group in groups:
                group.temp_dist = plane.distance(group.pivot)
            groups.sort(key=lambda group: group.temp_dist)
            if self.use_threshold:
                i = 0  # group間の空間の数
                distance = groups[0].temp_dist
                for group in groups:
                    if abs(distance - group.temp_dist) > self.threshold:
                        i += 1
                    distance = group.temp_dist
                    group.temp_position = i
                if i == 0:
                    return {'FINISHED'}
            else:
                for i, group in enumerate(groups):
                    group.temp_position = i

            # 各groupの大きさを求める: group.temp_dimensions
            dimensions = OrderedDict()  # {position: dimension, ...}
            plane_bak = tool_data.plane
            tool_data.plane = plane
            for group in groups:
                position = group.temp_position
                if self.distribution_mode == 'DIMENSION':
                    _mat, scale = group.calc_bb(
                        context, BoundingBox.AABB, Space.PLANE)
                    dimension = max(dimensions.get(position, 0.0), scale[2])
                else:
                    dimension = 0.0
                dimensions[position] = dimension
            tool_data.plane = plane_bak
            for group in groups:
                group.temp_dimension = dimensions[group.temp_position]

            # spacingの計算
            if self.use_auto_spacing:
                length = abs(groups[0].temp_dist - groups[-1].temp_dist)
                if self.distribution_mode == 'DIMENSION':
                    for p, f in dimensions.items():
                        if p == 0 or p == groups[-1].temp_position:
                            f *= 0.5
                        length -= f
                spacing = length / groups[-1].temp_position
                self.spacing = spacing
            else:
                spacing = self.spacing

            # 整列対象のplaneを求める
            planes = OrderedDict()  # {position: plane, ...}
            vec = groups[0].pivot - distribution_axis * dimensions[0] / 2
            for p, f in dimensions.items():
                v = vec + distribution_axis * f / 2
                planes[p] = vam.PlaneVector(v, distribution_axis)
                vec += distribution_axis * (spacing + f)
            for group in groups:
                group.temp_plane = planes[group.temp_position].copy()

            # planeの修正（spacingを手動にしていた場合）
            if not self.use_auto_spacing:
                pivot = self.calc_relative_to(
                    context, groups, self.distribution_space)
                g1, g2 = groups[0], groups[-1]
                v1 = g2.pivot - g1.pivot
                v2 = g2.temp_plane.location - g1.temp_plane.location
                scale = v2.length / v1.length
                if v1.dot(v2) < 0:
                    scale *= -1
                if scale != 0.0:
                    v0 = g1.pivot
                    for group in groups:
                        # g1.temp_centerを基準にscalingを元に戻す
                        loc = group.temp_plane.location
                        v = (loc - v0) / scale + v0
                        # pivotを基準にscalingを適用
                        v = (v - pivot) * scale + pivot
                        group.temp_plane.location = v
                else:
                    for group in groups:
                        group.temp_plane.location = pivot.copy()

            if self.auto_axis or len(self.distribution_axis) > 1:
                space = self.distribution_space
                axis = ax
            else:
                space = self.space
                axis = self.axis

            group_tvec = calc_group_to_plane_vector(
                context, groups, space, axis, None, 0.0, self.influence, EPS,
                plane, 'temp_plane')
            for g, v in group_tvec.items():
                if g in group_trans_vectors:
                    group_trans_vectors[g] = group_trans_vectors[g] + v
                else:
                    group_trans_vectors[g] = v

        groups.translate(context, group_trans_vectors)
        if context.mode == 'OBJECT':
            objects = [bpy.data.objects[name]
                       for name in itertools.chain.from_iterable(groups)]
        else:
            objects = None
        funcs.update_tag(context, objects)

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.use_event:
            if event.shift:
                if self.distribution_space == 'GLOBAL':
                    self.distribution_space = 'LOCAL'
        return self.execute(context)

    def draw(self, context):
        op_stubs.OperatorResetProperties.set_operator(self)

        # Distribution
        attrs = ['distribution_space', 'distribution_axis',
                 'distribution_mode', 'use_auto_spacing', 'spacing',
                 'relative_to', 'use_threshold', 'threshold']
        box = self.draw_box(self.layout, 'Distribution',
                            'show_expand_distribution', reset_attrs=attrs)
        column = box.column(align=True)
        self.draw_property('distribution_space', column, text='')
        prop = self.draw_property(
            'distribution_axis', column, text='', row=True, expand=True)
        if self.distribution_space == 'AXIS':
            prop.active = False
        column = box.column()
        self.draw_property('distribution_mode', column, text='Mode')
        self.draw_property('use_auto_spacing', column)
        if not self.use_auto_spacing:
            self.draw_property('spacing', column)
            self.draw_property('relative_to', column)
        if self.show_expand_distribution:
            self.draw_property('use_threshold', column)
            if self.use_threshold:
                self.draw_property('threshold', column)

        # Translation Axis
        attrs = ['auto_axis', 'space', 'axis', 'individual_orientation']
        box = self.draw_box(self.layout, 'Translation Axis',
                            '', reset_attrs=attrs)
        column = box.column()
        if len(self.distribution_axis) > 1:
            column.active = False
        self.draw_property('auto_axis', column)
        if not self.auto_axis:
            column = box.column(align=True)
            if len(self.distribution_axis) > 1:
                column.active = False
            self.draw_property('space', column, text='')
            prop = self.draw_property(
                'axis', column, text='', row=True, expand=True)
            if self.space == 'AXIS':
                prop.active = False

        column = box.column()
        column.active = self.groups and self.is_valid_individual_orientation(
            self.space, self.groups.Group)
        self.draw_property('individual_orientation', column)

        # Group関連
        self.draw_group_boxes(context, self.layout)

        # Others
        # box = self.draw_box(self.layout, 'Others', '')
        attrs = ['influence']
        box = self.draw_box(self.layout, 'Others', 'show_expand_others',
                            reset_attrs=attrs)
        column = box.column()
        self.draw_property('influence', column)


classes = [
    OperatorAlignToPlane,
    OperatorAlign,
    OperatorDistribute,
]
