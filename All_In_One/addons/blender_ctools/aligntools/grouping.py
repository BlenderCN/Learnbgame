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


import collections
from collections import abc
import itertools
from itertools import chain
import logging

import bpy
from mathutils import Matrix, Vector
import bmesh

from . import localutils
from .localutils import utils
from .localutils.checkargs import CheckArgs

from .va import convexhull
from .va import vabmesh as vabm
from .va import vamath as vam
from .va import vaview3d as vav
from .va import vaarmature as vaarm
from .va import vaobject as vaob

from . import tooldata
from . import memocoords
from . import funcs
from .enums import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
handler = logging.StreamHandler()
handler.setLevel(logging.NOTSET)
formatter = logging.Formatter(
    '[%(levelname)s: %(name)s.%(funcName)s()]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

tool_data = tooldata.tool_data
memoize = tool_data.memoize
checkargs = CheckArgs()


def flatten(seq):
    if not seq:
        return ()
    else:
        if isinstance(seq, Matrix):
            return tuple([tuple(row) for row in seq])
        else:
            return tuple(seq)


def memo_plane(plane=None):
    if not plane:
        plane = tool_data.plane
    return (tuple(plane.location) + tuple(plane.normal) +
            tuple(plane.rotation))


def memo_axis(axis=None):
    if not axis:
        axis = tool_data.axis
    return (tuple(axis.location) + tuple(axis.normal) +
            tuple(axis.rotation))


def memo_bb_type(context, bb_type, bb_space, individual_orientation):
    if bb_space == Space.VIEW:
        key = (flatten(context.region_data.view_matrix),)
    elif bb_space == Space.REGION:
        mat = flatten(context.region_data.perspective_matrix)
        key = (context.region.width, context.region.height, mat)
    elif bb_space == Space.PLANE:
        key = memo_plane()
    elif bb_space == Space.AXIS:
        key = memo_axis()
    else:
        key = ()
    if bb_space in {Space.VIEW, Space.REGION}:
        mmat = memocoords.manipulator_matrix(context)
        key += flatten(mmat.orientations['VIEW'])
    return (bb_type, bb_space, individual_orientation) + key


###############################################################################
# Group
###############################################################################
class Group(collections.abc.Sequence):
    # オペレーターからUI表示の際に参照する
    valid_individual_orientations = ()

    def __init__(self, context, elements,
                 bb_type=BoundingBox.AABB, bb_space=Space.GLOBAL,
                 individual_orientation=False):
        """Group of objects or vertices or bones
        :type context: bpy.types.Context
        :param elements: EDIT_MESHなら要素はintに、OBJECTならstrになる
        :type  elements: collections.abc.Iterable[int | str | tuple]
        :type bb_type: BoundingBox
        :type bb_space: Space
        :type individual_orientation: str
        """
        self._elements = list(elements)  # 並び換えは可。追加と削除は禁止。

        # bb_space座標系基準でのBoundingBoxを表す。update_bb()で更新。
        self.bb_type = bb_type
        self.bb_space = bb_space

        # matrixとscaleの直接の編集禁止。編集したいならcopyしてから使う事
        # mat: 4x4, scale: 3D
        # bb_mat, bb_scaleは共にworld座標系だが、bb_spaceがSpace.REGIONの
        # 場合にのみregion座標系になる。これはbb_mat3x3, bb_scale2dも同じ
        self.bb_mat = Matrix.Identity(4)
        self.bb_scale = Vector()
        # mat: 3x3, scale: 2D (bb_mat,bb_scaleを元に生成。主にregion座標用)
        self.bb_mat3x3 = Matrix.Identity(3)
        self.bb_scale2d = Vector([0, 0])

        self.individual_orientation = individual_orientation

        if context:
            self.update(context)

    def __getitem__(self, key):
        return self._elements[key]

    def __len__(self):
        return len(self._elements)

    # Get Coordinates ---------------------------------------------------------
    def get_coords(self, context, space=Space.GLOBAL):
        """グループの頂点座標のリストを返す
        :param space: Space.LOCAL, Space.GLOBAL, Space.VIEW, Space.REGION,
                      Space.PLANE
        :type space: Space | str
        :rtype: list[Vector]
        """
        if Space.get(space) not in {Space.GLOBAL, Space.LOCAL, Space.VIEW,
                                    Space.REGION, Space.PLANE}:
            raise ValueError()
        return []

    def get_orientation(self, context, space, normalize=True,
                        individual_orientation=None):
        """座標系を表す3x3の行列を返す
        :type context: bpy.types.Context
        :type space: Space | str
        :type normalize: bool
        :type individual_orientation: bool
        :rtype: Matrix
        """
        return funcs.get_orientation(context, space, normalize)

    # Sort --------------------------------------------------------------------
    @memoize(lambda self: None, use_instance=True)
    def sort_dependence(self):
        """親子関係,constraint,modifierによって並び替える。
        root寄りの物が先になる。
        """
        pass

    # Bounding Box ------------------------------------------------------------
    def calc_aabb(self, context, space, individual_orientation=None):
        """AABBを返す。Space.REGIONの場合はregion座標系、それ以外は全て
        World座標系
        :type context: bpy.types.Context
        :type space: Space | str
        :type individual_orientation: bool
        :return: return (4x4 matrix, 3D vector)
        :rtype: (Matrix, Vector)
        """
        if Space.get(space) == Space.REGION:
            # REGIONの場合のみbb_matは単位行列を元にする
            vecs = self.get_coords(context, Space.REGION)
            v_min = Vector([min((v[i] for v in vecs)) for i in range(3)])
            v_max = Vector([max((v[i] for v in vecs)) for i in range(3)])
            bb_mat = Matrix.Identity(4)
            bb_mat.col[3][:3] = (v_min + v_max) / 2
            bb_scale = v_max - v_min
        else:
            vecs = self.get_coords(context, Space.GLOBAL)
            mat = self.get_orientation(context, space, individual_orientation)
            imat = mat.inverted()
            vecs = [imat * v for v in vecs]
            v_min = Vector([min((v[i] for v in vecs)) for i in range(3)])
            v_max = Vector([max((v[i] for v in vecs)) for i in range(3)])
            center = (v_min + v_max) / 2
            bb_center = mat * center
            bb_mat = mat.to_4x4()
            bb_mat.col[3][:3] = bb_center
            bb_scale = v_max - v_min
        return bb_mat, bb_scale

    def calc_obb(self, context, space):
        """OBBを返す。Space.REGIONの場合はregion座標系、それ以外は全てWorld座標系
        :type context: bpy.types.Context
        :type space: Space | str
        :return: return (4x4 matrix, 3D vector)
        :rtype: (Matrix, Vector)
        """
        if space == Space.REGION:
            vecs = self.get_coords(context, Space.REGION)
            vecs_2d = [v.to_2d() for v in vecs]
            mat, scale = convexhull.OBB(vecs_2d)
            z_min = min(vecs, key=lambda v: v[2])
            z_max = max(vecs, key=lambda v: v[2])
            mat = mat.to_4x4()
            mat.col[3][:2] = mat.col[2][:2]
            mat.col[2][:3] = [0, 0, 1]
            mat.col[3][2] = (z_min[2] + z_max[2]) / 2
            scale = scale.to_3d()
            scale[2] = z_max[2] - z_min[2]
        else:
            vecs = self.get_coords(context, Space.GLOBAL)
            mat, scale = convexhull.OBB(vecs)
        return mat, scale

    def _memo_calc_bb(self, context, bb_type=None,
                      bb_space=None, individual_orientation=None):
        bb_type = bb_type or self.bb_type
        bb_space = bb_space or self.bb_space
        individual_orientation = (individual_orientation or
                                  self.individual_orientation)
        return memo_bb_type(context, bb_type, bb_space, individual_orientation)

    @memoize(_memo_calc_bb, use_instance=True)
    def calc_bb(self, context, bb_type=None, bb_space=None,
                individual_orientation=None):
        """
        :type context: bpy.types.Context
        :type bb_type: BoundingBox | str
        :type bb_space: Space | str
        :type individual_orientation: bool
        :return: return (4x4 matrix, 3D vector)
        :rtype: (Matrix, Vector)
        """
        bb_type = BoundingBox.get(bb_type or self.bb_type)
        bb_space = Space.get(bb_space or self.bb_space)
        if bb_type == BoundingBox.AABB:
            mat, scale = self.calc_aabb(
                context, bb_space, individual_orientation)
        else:
            mat, scale = self.calc_obb(context, bb_space)
        return mat, scale

    def update_bb(self, context):
        """self.bb_mat, self.bb_scale, self.bb_mat3x3, self.bb_scale2d の更新
        :type context: bpy.types.Context
        """
        self.bb_mat, self.bb_scale = self.calc_bb(context)
        for i in range(2):
            self.bb_mat3x3.col[i][:2] = self.bb_mat.col[i][:2]
        self.bb_mat3x3.col[2][:2] = self.bb_mat.col[3][:2]
        self.bb_mat3x3.row[2][:] = [0, 0, 1]
        self.bb_scale2d[:] = self.bb_scale[:2]

    # Pivot -------------------------------------------------------------------
    def calc_pivot_active(self, context, head_tail=0.0):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :rtype: Vector
        """
        return funcs.get_active_coord(context, head_tail)

    def calc_pivot_root(self, context, head_tail=0.0):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :rtype: Vector
        """
        return None

    def calc_pivot_head_tail(self, context, head_tail=0.0, root_only=False):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :type root_only: bool
        :rtype: Vector
        """
        return None

    def calc_pivot_bb(self, context, position=None):
        """注: BoundingBoxの大きさが0ならpositionの変更は無意味
        :param context:
        :param position: [x, y, z] 各要素は0.0~1.0の範囲でBoundingBoxを表す
        :type position: Vector
        :rtype: Vector
        """
        mat, scale = self.calc_bb(context)
        loc = mat.to_translation()
        if position:
            for i in range(3):
                loc += mat.col[i].to_3d() * position[i] * scale[i] * 0.5
        if self.bb_space == Space.REGION:
            loc = vav.unproject(context.region, context.region_data, loc)
        return loc

    def calc_pivot_target(self, context, target, distance):
        """
        :type context: bpy.types.Context
        :type target: Vector | vam.PlaneVector
        :type distance: Distance
        :rtype: Vector
        """
        if isinstance(target, vam.PlaneVector):
            plane_bak = tool_data.plane
            tool_data.plane = target
            coords = self.get_coords(context, Space.PLANE)
            tool_data.plane = plane_bak
            if distance == Distance.CLOSEST:
                loc = min(coords, key=lambda v: abs(v[2]))
            elif distance == Distance.MIN:
                loc = min(coords, key=lambda v: v[2])
            elif distance == Distance.MAX:
                loc = max(coords, key=lambda v: v[2])
            elif distance == Distance.CENTER:
                mat, scale = self.calc_bb(context, BoundingBox.AABB,
                                          Space.PLANE)
                loc = mat.to_translation()
            else:
                raise ValueError()
            if distance != Distance.CENTER:
                loc = target.to_matrix() * loc
        elif isinstance(target, Vector):
            coords = self.get_coords(context, Space.GLOBAL)
            if distance in {Distance.CLOSEST, Distance.MIN}:
                loc = min(coords, key=lambda v: (target - v).length)
            elif distance == Distance.MAX:
                loc = max(coords, key=lambda v: (target - v).length)
            else:
                raise ValueError()
        else:
            raise ValueError()
        return loc

    def _memo_calc_pivot(self, context, pivot_point, position=None,
                         head_tail=0.0, target=None, distance=Distance.CLOSEST,
                         fallback=PivotPoint.CENTER):
        pivot_point = PivotPoint.get(pivot_point)
        distance = Distance.get(distance)
        if fallback is not None:
            fallback = PivotPoint.get(fallback)
        key = [pivot_point, fallback]
        if isinstance(self, (EditBoneGroup, PoseBoneGroup)):
            key.append(head_tail)
        if pivot_point == PivotPoint.BOUNDING_BOX:
            k = memo_bb_type(context, self.bb_type, self.bb_space,
                             self.individual_orientation)
            key.append(k)
            key.append(flatten(position))
        elif pivot_point == PivotPoint.TARGET:
            if isinstance(target, vam.PlaneVector):
                key.append(memo_plane(target))
            elif isinstance(target, Vector):
                key.append(flatten(target))
            key.append(distance)
        elif pivot_point == PivotPoint.CURSOR:
            key.append(tuple(context.scene.cursor_location))
        return tuple(key)

    @memoize(_memo_calc_pivot, use_instance=True)
    def calc_pivot(self, context, pivot_point, position=None, head_tail=0.0,
                   target=None, distance=Distance.CLOSEST,
                   fallback=PivotPoint.CENTER):
        """
        :type context: bpy.types.Context
        :type pivot_point: PivotPoint | str
        :type position: Vector
        :type head_tail: float
        :type target: Vector | vam.PlaneVector
        :type distance: Distance | str
        :param fallback: pivot_pointが計算できなかった時に代わりにこれを
            使って計算し直す
        :type fallback: PivotPoint | None
        :rtype: Vector
        """
        pivot_point = PivotPoint.get(pivot_point)
        distance = Distance.get(distance)
        if fallback is not None:
            fallback = PivotPoint.get(fallback)
        if pivot_point == PivotPoint.CENTER:
            pivot = self.calc_bb(context, BoundingBox.AABB)[0].to_translation()
        elif pivot_point == PivotPoint.MEDIAN:
            coords = self.get_coords(context, Space.GLOBAL)
            pivot = sum(coords, Vector()) / len(coords)
        elif pivot_point == PivotPoint.ACTIVE:
            pivot = self.calc_pivot_active(context, head_tail)
        elif pivot_point == PivotPoint.CURSOR:
            pivot = context.scene.cursor_location.copy()
        elif pivot_point == PivotPoint.ROOT:
            pivot = self.calc_pivot_root(context, head_tail)
        elif pivot_point == PivotPoint.HEAD_TAIL:
            pivot = self.calc_pivot_head_tail(context, head_tail)
        elif pivot_point == PivotPoint.BOUNDING_BOX:
            pivot = self.calc_pivot_bb(context, position)
        elif pivot_point == PivotPoint.TARGET:
            distance = Distance.get(distance)
            pivot = self.calc_pivot_target(context, target, distance)
        else:
            pivot = None
        if pivot is None and pivot_point != fallback and fallback is not None:
            pivot = self.calc_pivot(context, fallback, position, head_tail,
                                    target, distance, fallback)
        return pivot

    # Update ------------------------------------------------------------------
    def update(self, context, groups=None):
        if groups is not None:
            self.bb_type = groups.bb_type
            self.bb_space = groups.bb_space
            self.individual_orientation = groups.individual_orientation
        self.sort_dependence()
        self.update_bb(context)

    def translate(self, context, vec):
        """各要素を移動する
        :type context: bpy.types.Context
        :type vec: Vector
        """
        for elem in self:
            pass

    def transform(self, context, matrix):
        """
        :type context: bpy.types.Context
        :type matrix: Matrix
        """
        for elem in self:
            pass


class ObjectGroup(Group):
    valid_individual_orientations = (Space.LOCAL, Space.NORMAL, Space.GIMBAL)

    def get_coords(self, context, space=Space.GLOBAL):
        """
        :type context: bpy.types.Context
        :param space: Space.LOCAL, Space.GLOBAL, Space.VIEW, Space.REGION,
                      Space.PLANE
        :type space: Space | str
        :rtype: list[Vector]
        """
        if Space.get(space) not in {Space.GLOBAL, Space.LOCAL, Space.VIEW,
                                    Space.REGION, Space.PLANE}:
            raise ValueError()
        vecs = memocoords.object_coords(context, space)
        return [vecs[name] for name in self]

    def get_orientation(self, context, space, normalize=True,
                        individual_orientation=None):
        """要素が１の場合のみ、matrix_woldをそのまま使う。他は一旦Quaternionに
        変換する。
        :type context: bpy.types.Context
        :type space: Space | str
        :type normalize: bool
        :type individual_orientation: bool
        :rtype: Matrix
        """
        if individual_orientation is None:
            individual_orientation = self.individual_orientation
        if individual_orientation:
            sp = Space.get(space)
            if sp in {Space.LOCAL, Space.NORMAL}:
                if len(self) == 1:
                    mat = bpy.data.objects[self[0]].matrix_world.to_3x3()
                    if normalize:
                        funcs.normalize_m3(mat)
                else:
                    quats = [
                        bpy.data.objects[name].matrix_world.to_quaternion()
                        for name in self]
                    quat = vam.interp_quats(quats)
                    mat = quat.to_matrix()
                return mat
            elif sp == Space.GIMBAL:
                mmat = memocoords.manipulator_matrix(context)
                mat = mmat.calc_orientation(
                    context, 'GIMBAL', active_object=bpy.data.objects[self[0]])
                return mat
        return super().get_orientation(context, space)

    def sort_dependence(self):
        """親子関係,constraint,modifierによって並び替える。
        root寄りの物が先になる。
        """
        elements = [bpy.data.objects[name] for name in self]
        elements = vaob.sorted_dependency(elements)
        self._elements[:] = [ob.name for ob in elements]

    def calc_pivot_root(self, context, head_tail='UNUSED'):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :rtype: Vector
        """
        self.sort_dependence()
        coords = self.get_coords(context, Space.GLOBAL)
        return coords[0].copy()

    def translate(self, context, vec):
        """
        :type context: bpy.types.Context
        :type vec: Vector
        """
        coords = memocoords.object_coords(context, Space.GLOBAL)
        objects = [bpy.data.objects[name] for name in self]
        for ob in vaob.sorted_dependency(objects):
            ob.matrix_world.col[3][:3] = coords[ob.name] + vec

    def transform(self, context, matrix):
        """
        :type context: bpy.types.Context
        :type matrix: Matrix
        """
        matrices = memocoords.object_matrices(context, Space.GLOBAL)
        objects = [bpy.data.objects[name] for name in self]
        for ob in vaob.sorted_dependency(objects):
            mat = matrix * matrices[ob.name]
            for i in range(4):
                ob.matrix_world.col[i][:] = mat.col[i]


class ObjectMeshGroup(ObjectGroup):
    _dm_vert_coords_ex_kwargs = {'apply_modifiers': False}

    def get_coords(self, context, space=Space.GLOBAL):
        """
        :type context: bpy.types.Context
        :param space: Space.LOCAL, Space.GLOBAL, Space.VIEW, Space.REGION,
                      Space.PLANE
        :type space: Space | str
        :rtype: list[Vector]
        """
        if Space.get(space) not in {Space.GLOBAL, Space.LOCAL, Space.VIEW,
                                    Space.REGION, Space.PLANE}:
            raise ValueError()
        vecs = []
        for name in self:
            ob = bpy.data.objects[name]
            d = memocoords.dm_vert_coords_ex(context, ob, space,
                                             **self._dm_vert_coords_ex_kwargs)
            if d:
                vecs.append(d.values())
            else:
                # mesh が生成出来無いならオブジェクト座標を使う
                d = memocoords.object_coords(context, space)
                vecs.append((d[ob.name],))
        return list(chain.from_iterable(vecs))


class ObjectDMPreviewGroup(ObjectMeshGroup):
    _dm_vert_coords_ex_kwargs = {'apply_modifiers': True,
                                 'settings': 'PREVIEW'}


class ObjectDMRenderGroup(ObjectMeshGroup):
    _dm_vert_coords_ex_kwargs = {'apply_modifiers': True,
                                 'settings': 'RENDER'}


class BMeshGroup(Group):
    valid_individual_orientations = (Space.NORMAL,)

    def get_coords(self, context, space=Space.GLOBAL):
        """
        :type context: bpy.types.Context
        :param space: Space.LOCAL, Space.GLOBAL, Space.VIEW, Space.REGION,
                      Space.PLANE
        :type space: Space | str
        :rtype: list[Vector]
        """
        if Space.get(space) not in {Space.GLOBAL, Space.LOCAL, Space.VIEW,
                                    Space.REGION, Space.PLANE}:
            raise ValueError()
        actob = context.active_object
        vecs = memocoords.bm_vert_coords(context, actob, space)
        return [vecs[i] for i in self]

    def get_orientation(self, context, space, normalize=True,
                        individual_orientation=None):
        """
        :type context: bpy.types.Context
        :type space: Space | str
        :type normalize: bool
        :type individual_orientation: bool
        :rtype: Matrix
        """
        if individual_orientation is None:
            individual_orientation = self.individual_orientation
        if individual_orientation:
            sp = Space.get(space)
            if sp == Space.NORMAL:
                normals_all = memocoords.bm_vert_normals(
                    context, context.active_object, Space.GLOBAL, None)
                normals = [normals_all[i] for i in self]
                normal = sum(normals, Vector()) / len(normals)
                """:type: Vector"""
                normal.normalize()
                q = Vector([0, 0, 1]).rotation_difference(normal)
                if len(self) == 1:
                    return q.to_matrix()
                else:
                    coords_all = memocoords.bm_vert_coords(
                        context, context.active_object, Space.GLOBAL)
                    coords = [coords_all[i] for i in self]
                    qi = q.inverted()
                    coords2d = [(qi * v).to_2d() for v in coords]
                    mat2d, scale2d = convexhull.OBB(coords2d)
                    mat = Matrix.Identity(3)
                    for i in range(2):
                        mat[i][:2] = mat2d[i][:2]
                    mat = q.to_matrix() * mat
                    return mat
        return super().get_orientation(context, space)

    def translate(self, context, vec):
        """
        :type context: bpy.types.Context
        :type vec: Vector
        """
        ob = context.active_object
        obimat = ob.matrix_world.inverted()
        bm = bmesh.from_edit_mesh(ob.data)
        verts = list(bm.verts)  # インデックスアクセスはこの方が速い(今はどうか知らない)
        coords = memocoords.bm_vert_coords(
            context, context.active_object, Space.GLOBAL)
        for i in self:
            verts[i].co = obimat * (coords[i] + vec)

    def transform(self, context, matrix):
        """
        :type context: bpy.types.Context
        :type matrix: Matrix
        """
        ob = context.active_object
        obimat = ob.matrix_world.inverted()
        bm = bmesh.from_edit_mesh(ob.data)
        verts = list(bm.verts)  # インデックスアクセスはこの方が速い(今はどうか知らない)
        coords = memocoords.bm_vert_coords(
            context, context.active_object, Space.GLOBAL)
        m = obimat * matrix
        for i in self:
            verts[i].co = m * coords[i]


class EditBoneGroup(Group):
    valid_individual_orientations = (Space.NORMAL,)

    def _elements_remove_doubles(self, context):
        """重複箇所の複数の要素を１つだけに絞る。現在get_coords()でのみ使用。
        ※ Head側 <- -> Tail側。(*): 選択、( ): 非選択。
        ( )BoneA(*)-----(*)BoneB(*)
                    `---(*)BoneC( )
        この状態ならBoneAのTailとBoneBのTailのみを有効とする。
        """
        bones = context.active_object.data.edit_bones
        elements = []
        for elem in self:
            name, p = elem
            append = True
            if p == 0:
                bone = bones[name]
                parent = bone.parent
                if parent and bone.use_connect and (parent.name, 1) in self:
                    append = False
            if append:
                elements.append(elem)
        return elements

    def elements_remove_invalid(self, context):
        """head,tailが選択されているboneAがあり、それとuse_connectが真で接続
        されているboneBが片側(BoneA側)しか選択されていない場合、その箇所を
        非選択と見做す。

        ( )B(*)-----(*)A(*)-----(*)C(*)     <- 全てのuse_connectが真とする
                            |---(*)D( )
                            `---( )E(*)
           [(A, 0), (A, 1), (B, 1), (C, 0), (C, 1), (D, 0), (E, 1)]
        -> [(A, 0), (A, 1), (C, 0), (C, 1), (E, 1)]

        :rtype: list[(str, int)]
        """
        d = {name: [False, False] for name, _ in self}
        for name, p in self:
            d[name][p] = True
        bones = context.active_object.data.edit_bones
        for name, head_tail in d.items():
            bone = bones[name]
            parent = bone.parent
            if parent and parent.name in d and bone.use_connect:
                if head_tail == [True, True]:
                    if d[parent.name] == [False, True]:
                        d[parent.name] = [False, False]
                elif head_tail == [True, False]:
                    if d[parent.name] == [True, True]:
                        d[name] = [False, False]
        elements = []
        for elem in self:
            name, p = elem
            if d[name][p]:
                elements.append(elem)
        return elements

    def get_coords(self, context, space=Space.GLOBAL):
        """
        :type context: bpy.types.Context
        :param space: Space.LOCAL, Space.GLOBAL, Space.VIEW, Space.REGION,
                      Space.PLANE
        :type space: Space | str
        :rtype: list[Vector]
        """
        if Space.get(space) not in {Space.GLOBAL, Space.LOCAL, Space.VIEW,
                                    Space.REGION, Space.PLANE}:
            raise ValueError()
        coords = []
        with vaarm.CustomProperty():
            ob = context.active_object
            bone_coords = memocoords.arm_bone_coords(
                context, ob, space, ob.mode, filter=BoneFilter.ALL)
            elements = self._elements_remove_doubles(context)
            for name, p in elements:
                head_co, tail_co = bone_coords[name]
                if p == 0:
                    coords.append(head_co)
                else:
                    coords.append(tail_co)
        return coords

    def get_orientation(self, context, space, normalize=True,
                        individual_orientation=None):
        """
        :type context: bpy.types.Context
        :type space: Space | str
        :type normalize: bool
        :type individual_orientation: bool
        :rtype: Matrix
        """
        if individual_orientation is None:
            individual_orientation = self.individual_orientation
        if individual_orientation:
            if Space.get(space) == Space.NORMAL:
                ob = context.active_object
                arm_bone_matrices = memocoords.arm_bone_matrices(
                    context, ob, Space.GLOBAL, filter=BoneFilter.ALL)
                elems = self.elements_remove_invalid(context)
                quats = [arm_bone_matrices[name].to_quaternion()
                         for name in {n for n, _ in elems}]
                quat = vam.interp_quats(quats)
                """:type: Quaternion"""
                mat = quat.to_matrix()
                return mat
        return super().get_orientation(context, space)

    def sort_dependence(self):
        with vaarm.CustomProperty():
            bones = bpy.context.active_object.data.edit_bones
            bones = [b.name for b in vaob.sorted_dependency(bones)]
            self._elements[:] = sorted(
                self, key=lambda x: (bones.index(x[0]), x[1]))

    def calc_pivot_root(self, context, head_tail=0.0):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :rtype: Vector
        """
        return self.calc_pivot_head_tail(context, head_tail, True)

    def calc_pivot_head_tail(self, context, head_tail=0.0, root_only=False):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :type root_only: bool
        :rtype: Vector
        """
        ob = context.active_object
        bones = ob.data.edit_bones
        vecs = []
        with vaarm.CustomProperty():
            elems = self.elements_remove_invalid(context)
            d = {n: [False, False] for n, _ in elems}
            for name, p in elems:
                d[name][p] = True
            f = 0.0 if not head_tail else head_tail
            for name, (head, tail) in d.items():
                bone = bones[name]
                if root_only:
                    parent = bone.parent
                    if parent and parent.name in d:
                        if head and d[parent.name][1]:
                            continue
                if head and tail:
                    v = bone.head * (1.0 - f) + bone.tail * f
                elif head:
                    v = bone.head
                else:  # tail
                    v = bone.tail
                vecs.append(ob.matrix_world * v)
        return sum(vecs, Vector()) / len(vecs)

    def translate(self, context, vec):
        """
        :type context: bpy.types.Context
        :type vec: Vector
        """
        ob = context.active_object
        coords = memocoords.arm_bone_coords(context, ob, Space.GLOBAL)
        obimat = ob.matrix_world.inverted()
        bones = ob.data.edit_bones
        with vaarm.CustomProperty():
            for name, p in self:
                bone = bones[name]
                head, tail = coords[name]
                if p == 0:
                    bone.head = obimat * (head + vec)
                    parent = bone.parent
                    if parent and bone.use_connect:
                        parent.tail = bone.head
                        for child in parent.children:
                            if child != bone and child.use_connect:
                                child.head = bone.head
                else:
                    bone.tail = obimat * (tail + vec)
                    for child in bone.children:
                        if child.use_connect:
                            child.head = bone.tail

    def transform(self, context, matrix, roll=True):
        """headとtailの両方がselfに存在していた場合のみroll引数が有効になる
        :type context: bpy.types.Context
        :type matrix: Matrix
        :type roll: bool
        """
        ob = context.active_object
        bone_coords = memocoords.arm_bone_coords(context, ob, Space.GLOBAL)
        bone_matrixes = memocoords.arm_bone_matrices(context, ob, Space.LOCAL)
        obimat = ob.matrix_world.inverted()
        bones = ob.data.edit_bones
        trans_mat_local = obimat * matrix

        # Bone.transform()の為、一旦use_connectを切る
        use_connect_flags = {bone: bone.use_connect for bone in bones}
        for bone in bones:
            bone.use_connect = False

        with vaarm.CustomProperty():
            for name, p in self:
                bone = bones[name]
                head, tail = bone_coords[name]
                if p == 0:
                    if (name, 1) in self:
                        trans_mat_local = obimat * matrix * obmat
                        bone.matrix = bone_matrixes[name]
                        m = trans_mat_local * bone.matrix
                        zvec = m.col[2].to_3d()
                        bone.transform(trans_mat_local, scale=True,
                                       roll=roll)
                        # roll=Trueだけでは不正確になる場合があるので
                        bone.align_roll(zvec)
                    else:
                        bone.head = obimat * matrix * head
                else:
                    if (name, 0) in self:
                        continue
                    else:
                        bone.tail = obimat * matrix * tail
            # 親と子のheadとtailを修正する
            for name, p in self:
                bone = bones[name]
                if p == 0:
                    parent = bone.parent
                    if use_connect_flags[bone] and parent:
                        parent.tail = bone.head
                        for child in parent.children:
                            if child != bone and use_connect_flags[child]:
                                child.head = bone.head
                else:
                    for child in bone.children:
                        if use_connect_flags[child]:
                            child.head = bone.tail
            # use_connectを戻す
            for bone, flag in use_connect_flags.items():
                bone.use_connect = flag


class PoseBoneGroup(Group):
    valid_individual_orientations = (Space.NORMAL, Space.GIMBAL)

    def get_coords(self, context, space=Space.GLOBAL):
        """
        :type context: bpy.types.Context
        :param space: Space.LOCAL, Space.GLOBAL, Space.VIEW, Space.REGION,
                      Space.PLANE
        :type space: Space | str
        :rtype: list[Vector]
        """
        if Space.get(space) not in {Space.GLOBAL, Space.LOCAL, Space.VIEW,
                                    Space.REGION, Space.PLANE}:
            raise ValueError()
        coords = []
        with vaarm.CustomProperty():
            ob = context.active_object
            bones = ob.pose.bones
            bone_coords = memocoords.arm_bone_coords(
                context, ob, space, ob.mode, filter=BoneFilter.ALL)
            for name in self:
                bone = bones[name]
                head_co, tail_co = bone_coords[name]
                parent = bone.parent
                if parent and bone.use_connect:
                    if parent.name not in self:
                        coords.append(head_co)
                else:
                    coords.append(head_co)
                coords.append(tail_co)
        return coords

    def get_orientation(self, context, space, normalize=True,
                        individual_orientation=None):
        """
        :type context: bpy.types.Context
        :type space: Space | str
        :type normalize: bool
        :type individual_orientation: bool
        :rtype: Matrix
        """
        if individual_orientation is None:
            individual_orientation = self.individual_orientation
        if individual_orientation:
            ob = context.active_object
            sp = Space.get(space)
            if sp == Space.NORMAL:
                arm_bone_matrices = memocoords.arm_bone_matrices(
                    context, ob, Space.GLOBAL, filter=BoneFilter.ALL)
                if len(self) == 1:
                    mat = arm_bone_matrices[self[0]].to_3x3()
                    if normalize:
                        funcs.normalize_m3(mat)
                else:
                    quats = [arm_bone_matrices[name].to_quaternion()
                             for name in self]
                    quat = vam.interp_quats(quats)
                    """:type: Quaternion"""
                    mat = quat.to_matrix()
                return mat
            elif sp == Space.GIMBAL:
                mmat = memocoords.manipulator_matrix(context)
                mat = mmat.calc_orientation(
                    context, 'GIMBAL', active_pose_bone=ob.pose.bones[self[0]])
                return mat
        return super().get_orientation(context, space)

    def sort_dependence(self):
        with vaarm.CustomProperty():
            bones = bpy.context.active_object.pose.bones
            bones = [b.name for b in vaob.sorted_dependency(bones)]
            self._elements[:] = sorted(self, key=lambda x: bones.index(x))

    def calc_pivot_root(self, context, head_tail=0.0):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :rtype: Vector
        """
        return self.calc_pivot_head_tail(context, head_tail, True)

    def calc_pivot_head_tail(self, context, head_tail=0.0, root_only=False):
        """
        :type context: bpy.types.Context
        :type head_tail: float
        :type root_only: bool
        :rtype: Vector
        """
        ob = context.active_object
        bones = ob.pose.bones
        vecs = []
        with vaarm.CustomProperty():
            f = 0.0 if not head_tail else head_tail
            for name in self:
                bone = bones[name]
                if root_only:
                    parent = bone.parent
                    if parent and parent.name in self:
                        continue
                v = bone.head * (1.0 - f) + bone.tail * f
                vecs.append(ob.matrix_world * v)
        return sum(vecs, Vector()) / len(vecs)

    def translate(self, context, vec):
        """
        :type context: bpy.types.Context
        :type vec: Vector
        """
        ob = context.active_object
        matrices = memocoords.arm_bone_matrices(context, ob, Space.GLOBAL)
        obimat = ob.matrix_world.inverted()
        bones = [ob.pose.bones[name] for name in self]
        with vaarm.CustomProperty():
            for bone in vaob.sorted_dependency(bones):
                parent = bone.parent
                if parent and bone.use_connect:  # 移動不可
                    continue
                loc = matrices[bone.name].col[3].to_3d()
                bone.matrix.col[3][:3] = obimat * (loc + vec)

    def transform(self, context, matrix):
        """
        :type context: bpy.types.Context
        :type matrix: Matrix
        """
        ob = context.active_object
        matrices = memocoords.arm_bone_matrices(context, ob, Space.GLOBAL)
        obimat = ob.matrix_world.inverted()
        bones = [ob.pose.bones[name] for name in self]
        with vaarm.CustomProperty():
            for bone in vaob.sorted_dependency(bones):
                # parent = bone.parent
                # if parent and bone.use_connect:  # 移動不可
                #     continue
                mat = obimat * matrix * matrices[bone.name]
                for i in range(4):
                    bone.matrix.col[i][:] = mat.col[i]


###############################################################################
# Groups
###############################################################################
@checkargs(
    group_type=GroupType,
    object_data=ObjectData,
    bb_type=BoundingBox,
    bb_space=((Space, str),),
    shrink_fatten=((int, float),),
    individual_orientation=bool,
    )
def context_groups(
        context, group_type, object_data, bb_type, bb_space,
        shrink_fatten=0.0, individual_orientation=False):
    """
    :type context: bpy.types.Context
    :type group_type: GroupType
    :type bb_type: BoundingBox
    :type object_data: ObjectData
    :type bb_space: Space
    :type shrink_fatten: float
    :type individual_orientation: bool
    :rtype: Groups
    """

    kwargs = dict(locals())
    if context.mode == 'OBJECT':
        groups = ObjectGroups(**kwargs)
    elif context.mode == 'EDIT_MESH':
        groups = BMeshGroups(**kwargs)
    elif context.mode == 'EDIT_ARMATURE':
        groups = EditBoneGroups(**kwargs)
    elif context.mode == 'POSE':
        groups = PoseBoneGroups(**kwargs)
    else:
        groups = None
    return groups


class Groups(collections.abc.Sequence):
    def __init__(self, context, group_type, object_data, bb_type,
                 bb_space, shrink_fatten=0.0, individual_orientation=False):
        """
        :type context: bpy.types.Context
        :type group_type: GroupType
        :type object_data: ObjectData
        :type bb_type: BoundingBox
        :type bb_space: Space
        :type shrink_fatten: float
        :type individual_orientation: bool
        """
        self._groups = []

        # Groups options
        if context.mode == 'OBJECT':
            self.object_data = ObjectData(object_data)
        else:
            self.object_data = ObjectData.ORIGIN
        self.group_type = GroupType.get(group_type)
        self.bb_type = BoundingBox.get(bb_type)
        self.bb_space = Space.get(bb_space)
        self.shrink_fatten = shrink_fatten
        # individual_orientationはLOCALかNORMALで有効
        self.individual_orientation = individual_orientation

        # キャッシュの確保
        ob = context.active_object
        if self.Group == BMeshGroup:
            memocoords.bm_vert_coords(context, ob, Space.GLOBAL)
        elif self.Group in {EditBoneGroup, PoseBoneGroup}:
            memocoords.arm_bone_coords(context, ob, Space.GLOBAL)

        # self._groups更新
        self.update(context)

    def __getitem__(self, key):
        return self._groups[key]

    def __len__(self):
        return len(self._groups)

    def sort(self, key=None, reverse=False):
        self._groups.sort(key=key, reverse=reverse)

    context_mode = 'OBJECT'
    Group = ObjectGroup

    def _make_groups_bb(self, context, groups):
        """_make_groups()から呼び出す"""
        Group = self.Group

        if not groups:
            return groups

        for group in groups:
            group.update(context, groups=self)

        fatten_vec = Vector([self.shrink_fatten * 2] * 3)
        fatten_vec_2d = fatten_vec.to_2d()

        # バウンディングボックスでの交差判定。
        # 面倒なのでAABBもOBBと同じように処理
        def key(g1, g2):
            if self.bb_space == Space.REGION:
                return vam.check_obb_intersection(
                    g1.bb_mat3x3, g1.bb_scale2d + fatten_vec_2d,
                    g2.bb_mat3x3, g2.bb_scale2d + fatten_vec_2d)
            else:
                return vam.check_obb_intersection(
                    g1.bb_mat, g1.bb_scale + fatten_vec,
                    g2.bb_mat, g2.bb_scale + fatten_vec)

        intersected_groups = localutils.utils.groupwith(groups, key)  # 2d list
        groups = [Group(context, chain.from_iterable(group_list))
                  for group_list in intersected_groups]

        return groups

    def _memo_make_groups(self, context, group_type=None):
        if not group_type:
            group_type = self.group_type
        key = (self.Group, group_type)
        if group_type == GroupType.BOUNDING_BOX:
            key += (context.scene.name, self.object_data,
                    self.shrink_fatten)
            key += memo_bb_type(context, self.bb_type, self.bb_space,
                                self.individual_orientation)
        return key

    @memoize(_memo_make_groups, use_instance=True)
    def _make_groups(self, context, group_type=None):
        """
        :type group_type: GroupType
        :rtype: list[Group]
        """
        return []

    def update(self, context):
        if context.mode != self.context_mode:
            print('cannot update')
            return

        groups = self._make_groups(context)
        for group in groups:
            group.update(context, groups=self)
        self._groups = groups[:]

    def get_active(self, context):
        """activeな要素が含まれるGroupを返す。
        Activeな要素が複数のGroupに跨がる場合はその全てのGroupを返す。
        :rtype: Group | list[Group] | None
        """
        return None

    def translate(self, context, vectors):
        """各Groupの要素を移動する
        :param vectors:
        :type vectors: dict[str, Vector] | list[Vector]
        """

    def transform(self, context, matrices, reverse=False):
        """各Groupの要素に対して行列を適用する
        :type matrices: dict[str, Matrix] | list[Matrix]
        :param reverse: 逆順に適用する
        """
        pass


class ObjectGroups(Groups):
    context_mode = 'OBJECT'

    @property
    def Group(self):
        if self.object_data == ObjectData.ORIGIN:
            return ObjectGroup
        elif self.object_data == ObjectData.MESH:
            return ObjectMeshGroup
        elif self.object_data == ObjectData.DM_PREVIEW:
            return ObjectDMPreviewGroup
        else:
            return ObjectDMRenderGroup

    @memoize(Groups._memo_make_groups, use_instance=True)
    def _make_groups(self, context, group_type=None):
        if not group_type:
            group_type = self.group_type
        Group = self.Group

        if group_type == GroupType.NONE:
            groups = [Group(context, (ob.name,))
                      for ob in context.selected_objects]

        elif group_type == GroupType.ALL:
            groups = [Group(context,
                            (ob.name for ob in context.selected_objects))]

        elif group_type == GroupType.PARENT_CHILD:
            def key(a, b):
                return (a.parent == b or b.parent == a or
                        b in a.children or a in b.children)
            objects = localutils.utils.groupwith(context.selected_objects, key)
            groups = [Group(context, (ob.name for ob in obs))
                      for obs in objects]

        elif group_type == GroupType.GROUP:
            seq = [(ob.name, set(ob.users_group))
                   for ob in context.selected_objects]
            # def key(a, b):
            #     return a[1] & b[1]
            ob_list = localutils.utils.groupwith(seq, lambda a, b: a[1] & b[1])
            groups = [Group(context, [elem[0] for elem in ls])
                      for ls in ob_list]

        elif group_type == GroupType.BOUNDING_BOX:
            linked_groups = self._make_groups(
                context, group_type=GroupType.PARENT_CHILD)
            groups = self._make_groups_bb(context, linked_groups)

        else:
            raise ValueError(group_type)

        return groups

    def get_active(self, context):
        active = funcs.get_active(context)
        if active:
            for group in self:
                if active.name in group:
                    return group

    def translate(self, context, vectors):
        if isinstance(vectors, list):
            vectors = dict(zip(self, vectors))

        coords = memocoords.object_coords(context, Space.GLOBAL)
        ob_vec = {}  # {Object: Vector, ...}
        for group, vec in vectors.items():
            for name in group:
                ob_vec[bpy.data.objects[name]] = vec

        for ob in vaob.sorted_dependency(ob_vec.keys()):
            ob.matrix_world.col[3][:3] = coords[ob.name] + ob_vec[ob]

    def transform(self, context, matrices, reverse=False):
        if isinstance(matrices, list):
            matrices = dict(zip(self, matrices))
        current_matrices = memocoords.object_matrices(context, Space.GLOBAL)
        ob_mat = {}  # {Object: Matrix, ...}
        for group, mat in matrices.items():
            for name in group:
                ob_mat[bpy.data.objects[name]] = mat
        objects = vaob.sorted_dependency(ob_mat.keys())
        if reverse:
            objects.reverse()
        for ob in objects:
            mat = ob_mat[ob] * current_matrices[ob.name]
            for i in range(4):
                ob.matrix_world.col[i][:] = mat.col[i]


class BMeshGroups(Groups):
    """
    NONE: 頂点毎
    ALL: 全てを一塊とする
    LINKED: Edgeで繋がっているもの
    CONNECTED: LINKEDと同じ
    GROUP: VertexGroupで纏める
    BOUNDING_BOX: BoundingBoxを使う
    """
    context_mode = 'EDIT_MESH'
    Group = BMeshGroup

    @memoize(Groups._memo_make_groups, use_instance=True)
    def _make_groups(self, context, group_type=None):
        if not group_type:
            group_type = self.group_type
        Group = self.Group
        ob = context.active_object
        bm = bmesh.from_edit_mesh(ob.data)

        if group_type == GroupType.NONE:
            groups = [Group(context, (i,))
                      for i, v in enumerate(bm.verts) if v.select]

        elif group_type == GroupType.ALL:
            groups = [Group(context,
                            (i for i, v in enumerate(bm.verts) if v.select))]

        elif group_type == GroupType.LINKED:
            seq = vabm.linked_vertices_list(bm, select=True, hide=False)
            d = {v: i for i, v in enumerate(bm.verts)}
            groups = [Group(context, (d[v] for v in verts))
                      for verts in seq]

        elif group_type == GroupType.GROUP:
            layer = bm.verts.layers.deform.verify()
            # def key(a, b):
            #     return a[1] & b[1]
            seq = [(i, set(v[layer].keys()))
                   for i, v in enumerate(bm.verts) if v.select and not v.hide]
            v_list = localutils.utils.groupwith(seq, lambda a, b: a[1] & b[1])
            groups = [Group(context, [elem[0] for elem in ls])
                      for ls in v_list]

        elif group_type == GroupType.BOUNDING_BOX:
            linked_groups = self._make_groups(
                context, group_type=GroupType.LINKED)
            groups = self._make_groups_bb(context, linked_groups)

        else:
            raise ValueError()

        return groups

    def get_active(self, context):
        active = funcs.get_active(context)
        if active:
            bm = bmesh.from_edit_mesh(context.active_object.data)
            bm.verts.index_update()
            if isinstance(active, bmesh.types.BMVert):
                elem = active.index
                for group in self:
                    if elem in group:
                        return group
            else:
                elem = {v.index for v in active.verts}
                result = []
                for group in self:
                    if set(group) & elem:
                        result.append(group)
                if result:
                    return result

    def translate(self, context, vectors):
        if isinstance(vectors, list):
            vectors = dict(zip(self, vectors))
        if 0:  # 遅くなりそうなので
            for group, vec in vectors.items():
                group.translate(context, vec)
        else:
            ob = context.active_object
            obimat = ob.matrix_world.inverted()
            bm = bmesh.from_edit_mesh(ob.data)
            verts = list(bm.verts)
            coords = memocoords.bm_vert_coords(
                context, context.active_object, Space.GLOBAL)
            for group, vec in vectors.items():
                for i in group:
                    verts[i].co = obimat * (coords[i] + vec)

    def transform(self, context, matrices, reverse=False):
        if isinstance(matrices, list):
            matrices = dict(zip(self, matrices))
        ob = context.active_object
        obimat = ob.matrix_world.inverted()
        bm = bmesh.from_edit_mesh(ob.data)
        verts = list(bm.verts)
        coords = memocoords.bm_vert_coords(
            context, context.active_object, Space.GLOBAL)
        for group, mat in matrices.items():
            m = obimat * mat
            for i in group:
                verts[i].co = m * coords[i]


class EditBoneGroups(Groups):
    """
    NONE: Head,Tail毎
    ALL: 全てを一塊とする
    BONE: Bone毎
    LINKED: 同一Bone又は親子関係
    CONNECTED: 同一Bone又は親子関係。但しuse_connectが真の場合のみ
    GROUP: PoseBoneGroupで纏める
    BOUNDING_BOX: BoundingBoxを使う
    """

    context_mode = 'EDIT_ARMATURE'
    Group = EditBoneGroup

    def _make_bone_groups(self, context, group_type):
        Group = self.Group

        with vaarm.CustomProperty():
            ob = context.active_object

            elems = []
            for bone in ob.data.edit_bones:
                if bone.is_visible:
                    if bone.select_head:
                        elems.append((bone, 0))
                    if bone.select_tail:
                        elems.append((bone, 1))

            def is_same_bone(elem1, elem2):
                return elem1[0] == elem2[0]

            def is_parent_child(elem1, elem2):
                bone1, p1 = elem1
                bone2, p2 = elem2
                if bone1.parent == bone2 and p1 == 0 and p2 == 1:
                    return True
                if bone2.parent == bone1 and p2 == 0 and p1 == 1:
                    return True
                return False

            def is_connected(elem1, elem2):
                bone1, p1 = elem1
                bone2, p2 = elem2
                if bone1.parent == bone2 and p1 == 0 and p2 == 1:
                    if bone1.use_connect:
                        return True
                if bone2.parent == bone1 and p2 == 0 and p1 == 1:
                    if bone2.use_connect:
                        return True
                return False

            if group_type == GroupType.ALL:
                bones_list = [elems]

            elif group_type == GroupType.NONE:
                bones_list = localutils.utils.groupwith(elems, is_connected)

            elif group_type == GroupType.BONE:
                bones_list = localutils.utils.groupwith(elems, is_same_bone)

            elif group_type == GroupType.PARENT_CHILD:
                def key(elem1, elem2):
                    if is_same_bone(elem1, elem2):
                        return True
                    else:
                        return is_parent_child(elem1, elem2)
                bones_list = localutils.utils.groupwith(elems, key)

            elif group_type == GroupType.PARENT_CHILD_CONNECTED:
                def key(elem1, elem2):
                    if is_same_bone(elem1, elem2):
                        return True
                    else:
                        return is_connected(elem1, elem2)
                bones_list = localutils.utils.groupwith(elems, key)

            elif group_type == GroupType.GROUP:
                def key(elem1, elem2):
                    pose_bones = context.active_object.pose.bones
                    g1 = pose_bones[elem1[0].name].bone_group
                    g2 = pose_bones[elem2[0].name].bone_group
                    if g1 == g2:
                        return True
                    else:
                        return is_connected(elem1, elem2)
                bones_list = localutils.utils.groupwith(elems, key)

            else:
                raise ValueError()

            group_list = [Group(context, ((b.name, i) for b, i in ls))
                          for ls in bones_list]

        return group_list

    @memoize(Groups._memo_make_groups, use_instance=True)
    def _make_groups(self, context, group_type=None):
        if not group_type:
            group_type = self.group_type

        if group_type == GroupType.BOUNDING_BOX:
            groups = self._make_bone_groups(context, GroupType.PARENT_CHILD)
            groups = self._make_groups_bb(context, groups)
        elif group_type in {
                GroupType.NONE, GroupType.ALL, GroupType.BONE,
                GroupType.PARENT_CHILD, GroupType.PARENT_CHILD_CONNECTED,
                GroupType.GROUP}:
            groups = self._make_bone_groups(context, group_type)
        else:
            raise ValueError()
        return groups

    def get_active(self, context):
        # group_type == GroupType.NONE の際、二つのGroupを含むリストを返す場合がある
        active = funcs.get_active(context)
        if active:
            result = []
            for group in self:
                names = {n for n, _ in group.elements_remove_invalid(context)}
                if active.name in names:
                    result.append(group)
            if result:
                return result

    def translate(self, context, vectors):
        if isinstance(vectors, list):
            vectors = dict(zip(self, vectors))
        for group, vec in vectors.items():
            group.translate(context, vec)

    def transform(self, context, matrices, reverse=False, roll=True):
        if isinstance(matrices, list):
            matrices = dict(zip(self, matrices))

        ob = context.active_object
        bone_coords = memocoords.arm_bone_coords(context, ob, Space.GLOBAL)
        bone_matrixes = memocoords.arm_bone_matrices(context, ob, Space.LOCAL)
        obmat = ob.matrix_world
        obimat = obmat.inverted()
        bones = ob.data.edit_bones

        # Bone.transform()の為、一旦use_connectを切る
        use_connect_flags = {bone: bone.use_connect for bone in bones}
        for bone in bones:
            bone.use_connect = False

        used_bones = set()
        all_keys = []
        for group in self:
            for name, p in group:
                used_bones.add(bones[name])
                all_keys.append((group, bones[name], p))
        sorted_bones = vaob.sorted_dependency(list(used_bones))
        all_keys.sort(key=lambda x: (sorted_bones.index(x[1]), x[2]))

        with vaarm.CustomProperty():
            for group, bone, p in all_keys:
                matrix = matrices[group]
                matrix = matrix.to_4x4()
                name = bone.name
                head, tail = bone_coords[name]
                if p == 0:
                    if (name, 1) in group:
                        trans_mat_local = obimat * matrix * obmat
                        bone.matrix = bone_matrixes[name]
                        m = trans_mat_local * bone.matrix
                        zvec = m.col[2].to_3d()
                        bone.transform(trans_mat_local, scale=True,
                                       roll=roll)
                        # roll=Trueだけでは不正確になる場合があるので
                        bone.align_roll(zvec)
                    else:
                        bone.head = obimat * matrix * head
                else:
                    if (name, 0) in group:
                        continue
                    else:
                        bone.tail = obimat * matrix * tail

            # 親と子のheadとtailを修正する
            for name, p in itertools.chain.from_iterable(self):
                bone = bones[name]
                if p == 0:
                    parent = bone.parent
                    if use_connect_flags[bone] and parent:
                        parent.tail = bone.head
                        for child in parent.children:
                            if child != bone and use_connect_flags[child]:
                                child.head = bone.head
                else:
                    for child in bone.children:
                        if use_connect_flags[child]:
                            child.head = bone.tail
        # use_connectを戻す
        for bone, flag in use_connect_flags.items():
            bone.use_connect = flag


class PoseBoneGroups(Groups):
    """
    NONE: PoseBone毎
    ALL: 全てを一塊とする
    BONE: NONEと同じ
    LINKED: 親子関係
    CONNECTED: 親子関係。但しuse_connectが真の場合のみ
    GROUP: PoseBoneGroupで纏める
    BOUNDING_BOX: BoundingBoxを使う
    """

    context_mode = 'POSE'
    Group = PoseBoneGroup

    def _make_bone_groups(self, context, group_type):
        Group = self.Group

        with vaarm.CustomProperty():
            ob = context.active_object

            elems = [b for b in ob.pose.bones if b.is_visible and b.select]

            def is_parent_child(bone1, bone2):
                return bone1.parent == bone2 or bone2.parent == bone1

            def is_connected(bone1, bone2):
                if bone1.parent == bone2:
                    if bone1.use_connect:
                        return True
                if bone2.parent == bone1:
                    if bone2.use_connect:
                        return True
                return False

            if group_type == GroupType.ALL:
                bones_list = [elems]

            elif group_type in {GroupType.NONE, GroupType.BONE}:
                bones_list = [[elem] for elem in elems]

            elif group_type == GroupType.PARENT_CHILD:
                bones_list = localutils.utils.groupwith(elems, is_parent_child)

            elif group_type == GroupType.PARENT_CHILD_CONNECTED:
                bones_list = localutils.utils.groupwith(elems, is_connected)

            elif group_type == GroupType.GROUP:
                def key(bone1, bone2):
                    pose_bones = context.active_object.pose.bones
                    g1 = pose_bones[bone1.name].bone_group
                    g2 = pose_bones[bone2.name].bone_group
                    if g1 == g2:
                        return True
                    else:
                        return is_connected(bone1, bone2)
                bones_list = localutils.utils.groupwith(elems, key)

            else:
                raise ValueError()

            group_list = [Group(context, (b.name for b in ls))
                          for ls in bones_list]

        return group_list

    @memoize(Groups._memo_make_groups, use_instance=True)
    def _make_groups(self, context, group_type=None):
        if not group_type:
            group_type = self.group_type
        Group = self.Group

        if group_type == GroupType.BOUNDING_BOX:
            groups = self._make_bone_groups(context, GroupType.PARENT_CHILD)
            groups = self._make_groups_bb(context, groups)
        elif group_type in {
                GroupType.NONE, GroupType.ALL, GroupType.BONE,
                GroupType.PARENT_CHILD, GroupType.PARENT_CHILD_CONNECTED,
                GroupType.GROUP}:
            groups = self._make_bone_groups(context, group_type)
        else:
            raise ValueError()

        return groups

    def get_active(self, context):
        active = funcs.get_active(context)
        if active:
            for group in self:
                if active.name in group:
                    return group

    def translate(self, context, vectors):
        if isinstance(vectors, list):
            vectors = dict(zip(self, vectors))

        ob = context.active_object
        matrices = memocoords.arm_bone_matrices(context, ob, Space.GLOBAL)
        obimat = ob.matrix_world.inverted()
        bones = ob.pose.bones

        bone_vec = {}  # {PoseBone: Vector, ...}
        for group, vec in vectors.items():
            for name in group:
                bone_vec[bones[name]] = vec

        with vaarm.CustomProperty():
            for bone in vaob.sorted_dependency(bone_vec.keys()):
                parent = bone.parent
                if parent and bone.use_connect:  # 移動不可
                    continue
                loc = matrices[bone.name].col[3].to_3d()
                bone.matrix.col[3][:3] = obimat * (loc + bone_vec[bone])

    def transform(self, context, matrices, reverse=False):
        if isinstance(matrices, list):
            matrices = dict(zip(self, matrices))

        ob = context.active_object
        current_matrices = memocoords.arm_bone_matrices(
            context, ob, Space.GLOBAL)
        obimat = ob.matrix_world.inverted()
        bones = ob.pose.bones

        bone_mat = {}  # {PoseBone: Matrix, ...}
        for group, mat in matrices.items():
            for name in group:
                bone_mat[bones[name]] = mat

        with vaarm.CustomProperty():
            sorted_bones = vaob.sorted_dependency(bone_mat.keys())
            if reverse:
                sorted_bones.reverse()
            for bone in sorted_bones:
                # parent = bone.parent
                # if parent and bone.use_connect:  # 移動不可
                #     continue
                mat = obimat * bone_mat[bone] * current_matrices[bone.name]
                # for i in range(4):
                #     bone.matrix.col[i][:] = mat.col[i]
                bone.matrix = mat  # スライスだと上手くいかなかった
