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

import bpy
import bmesh
from mathutils import Matrix

from . import localutils
from .localutils.checkargs import CheckArgs

from .va import vaview3d as vav
from .va import vaarmature as vaarm
from .va import manipulatormatrix as vamanipul

from . import tooldata
from .enums import *


checkargs = CheckArgs(True)

tool_data = tooldata.tool_data
memoize = tool_data.memoize


def flatten(seq):
    if isinstance(seq, Matrix):
        return tuple([tuple(row) for row in seq])
    else:
        return tuple(seq)


def project_v3_list(context, coords):
    """world座標からregion座標へ。ジェネレーター"""
    region = context.region
    rv3d = context.region_data
    sx, sy = region.width, region.height
    mat = rv3d.perspective_matrix
    func = vav.project_v3
    return (func(sx, sy, mat, v) for v in coords)


def plane_to_tuple(plane):
    return (tuple(plane.location) + tuple(plane.normal) +
            tuple(plane.rotation))


def memo_append_mat(key, context, space, ob=None):
    """
    :type key: tuple
    :type context: bpy.types.Context
    :type space: Space
    :type ob: bpy.types.Object
    :return:
    """
    if ob and space != Space.LOCAL:
        key += (flatten(ob.matrix_world),)
    if space == Space.VIEW:
        key += (flatten(context.region_data.view_matrix),)
    elif space == Space.REGION:
        mat = flatten(context.region_data.perspective_matrix)
        key += (context.region.width, context.region.height, mat)
    elif space == Space.PLANE:
        key += plane_to_tuple(tool_data.plane)
    return key


###############################################################################
# Object
###############################################################################
def _memo_object_coords(context, space=Space.GLOBAL, select=None):
    space = Space.get(space)
    key = (context.scene.name, space, select)
    if space != Space.LOCAL:
        key += tuple((flatten(ob.matrix_world) for ob in bpy.data.objects
                      if select is None or
                      ob.is_visible(context.scene) and ob.select == select))
    key = memo_append_mat(key, context, space)
    return key


@memoize(_memo_object_coords)
def object_coords(context, space=Space.GLOBAL, select=None):
    """複数のObjectの座標を返す。
    spaceがSpace.LOCALの場合、全てのオブジェクトの座標は[0, 0, 0]となる。
    :type context: bpy.types.Context
    :param space: GLOBAL, LOCAL, VIEW, REGION, PLANE
    :type space: Space | str
    :param select: 真なら選択要素のみ返す。偽なら表示中の非選択要素
    :rtype: OrderedDict
    """
    space = Space.get(space)
    coords = OrderedDict(
        ((ob.name, ob.matrix_world.to_translation())
         for ob in bpy.data.objects
         if select is None or
         ob.is_visible(context.scene) and ob.select == select)
    )
    if space == Space.GLOBAL:
        pass
    elif space == Space.LOCAL:
        for v in coords.values():
            v[:] = [0, 0, 0]
    elif space == Space.VIEW:
        mat = context.region_data.view_matrix
        for v in coords.values():
            v[:] = mat * v
    elif space == Space.REGION:
        sx, sy = context.region.width, context.region.height
        mat = context.region_data.perspective_matrix
        for v in coords.values():
            v[:] = vav.project_v3(sx, sy, mat, v)
    elif space == Space.PLANE:
        mat = tool_data.plane.to_matrix().inverted()
        for v in coords.values():
            v[:] = mat * v
    else:
        raise ValueError()
    return coords


@memoize(_memo_object_coords)
def object_matrices(context, space=Space.GLOBAL, select=None):
    """複数のObjectの行列を返す。
    coordinate_systemが'local'の場合、
    全てのオブジェクトの行列は単位行列となる。
    :type context: bpy.types.Context
    :param space: GLOBAL, LOCAL, VIEW, PLANE
    :type space: Space | str
    :param select: 真なら選択要素のみ返す。偽なら表示中の非選択要素
    :rtype: OrderedDict
    """
    space = Space.get(space)
    matrices = OrderedDict(
        ((ob.name, ob.matrix_world.copy()) for ob in bpy.data.objects
         if select is None or
            ob.is_visible(context.scene) and ob.select == select))
    if space == Space.GLOBAL:
        pass
    elif space == Space.LOCAL:
        for mat in matrices.values():
            mat.identity()
    elif space in (Space.VIEW, Space.PLANE):
        if space == Space.VIEW:
            mat = context.region_data.view_matrix
        else:
            mat = tool_data.plane.to_matrix().inverted()
        matrices = OrderedDict([(n, mat * m) for n, m in matrices.items()])
    else:
        raise ValueError()
    return matrices


###############################################################################
# Derived Mesh
###############################################################################
def _memo_dm_vert_coords_ex(context, ob, space=Space.GLOBAL,
                            apply_modifiers=True, settings='PREVIEW',
                            calc_tessface=True, calc_undeformed=False):
    space = Space.get(space)
    key = (context.scene.name, ob.name, space, apply_modifiers,
           settings, calc_tessface, calc_undeformed)
    key = memo_append_mat(key, context, space, ob)
    return key


@memoize(_memo_dm_vert_coords_ex)
def dm_vert_coords_ex(context, ob, space=Space.GLOBAL,
                      apply_modifiers=True, settings='PREVIEW',
                      calc_tessface=True, calc_undeformed=False):
    """指定ObjectのMesh頂点座標を返す。
    :type context: bpy.types.Context
    :type ob: bpy.types.Object
    :param space: GLOBAL, LOCAL, VIEW, REGION, PLANE
    :type space: Space | str
    :param apply_modifiers:
    :param settings: 'PREVIEW' or 'RENDER'
    :param calc_tessface: Calculate Tessellation, Calculate tessellation faces
    :param calc_undeformed: Calculate Undeformed, Calculate undeformed vertex
        coordinates
    :rtype: OrderedDict
    """
    if ob.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
        return None

    space = Space.get(space)
    if space in {Space.VIEW, Space.REGION, Space.PLANE}:
        coords = dm_vert_coords_ex(context, ob, Space.GLOBAL, apply_modifiers,
                                   settings, calc_tessface, calc_undeformed)
        if space == Space.VIEW:
            mat = context.region_data.view_matrix
            vecs = (mat * v for v in coords.values())
        elif space == Space.REGION:
            vecs = project_v3_list(context, coords.values())
        else:
            mat = tool_data.plane.to_matrix().inverted()
            vecs = (mat * v for v in coords.values())
        coords = OrderedDict(zip(coords, vecs))
    elif space in {Space.GLOBAL, Space.LOCAL}:
        mesh = ob.to_mesh(context.scene, apply_modifiers, settings,
                          calc_tessface, calc_undeformed)
        if space == Space.GLOBAL:
            mesh.transform(ob.matrix_world)
        coords = OrderedDict(((i, v.co.copy())
                              for i, v in enumerate(mesh.vertices)))
        bpy.data.meshes.remove(mesh)
    else:
        raise ValueError()

    return coords


def _memo_dm_vert_coords(context, ob, space=Space.GLOBAL,
                         settings='PREVIEW'):
    space = Space.get(space)
    key = (context.scene.name, ob.name, space, settings)
    key = memo_append_mat(key, context, space, ob)
    return key


@memoize(_memo_dm_vert_coords)
def dm_vert_coords(context, ob, space=Space.GLOBAL, settings='PREVIEW'):
    """
    :type context: bpy.types.Context
    :type ob: bpy.types.Object
    :type space: Space | str
    :type settings: str
    :rtype: OrderedDict
    """
    return dm_vert_coords_ex(context, ob, space, True, settings)


###############################################################################
# BMesh
###############################################################################
def _memo_bm_vert_coords(context, ob, space=Space.GLOBAL, select=None):
    space = Space.get(space)
    key = (ob.name, space, select)
    key = memo_append_mat(key, context, space, ob)
    return key


@memoize(_memo_bm_vert_coords)
def bm_vert_coords(context, ob, space=Space.GLOBAL, select=None):
    """BMeshの頂点の座標を返す。
    :type context: bpy.types.Context
    :type ob: bpy.types.Object
    :param space: GLOBAL, LOCAL, VIEW, REGION, PLANE
    :type space: Space | str
    :param select: 真なら選択要素のみ返す。偽なら表示中の非選択要素
    :return: 辞書のキーはBMVert.indexではなくBMVertSeqでの並び順に拠る
    :rtype: OrderedDict
    """
    space = Space.get(space)
    if space in {Space.VIEW, Space.REGION, Space.PLANE}:
        coords = bm_vert_coords(context, ob, Space.GLOBAL, select)
        if space == Space.VIEW:
            mat = context.region_data.view_matrix
            coords = OrderedDict(((i, mat * v) for i, v in coords.items()))
        elif space == Space.REGION:
            vecs = project_v3_list(context, coords.values())
            coords = OrderedDict(zip(coords, vecs))
        else:
            mat = tool_data.plane.to_matrix().inverted()
            coords = OrderedDict(((i, mat * v) for i, v in coords.items()))
    elif space in {Space.GLOBAL, Space.LOCAL}:
        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(ob.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(ob.data, face_normals=True, use_shape_key=False,
                         shape_key_index=0)
        coords = OrderedDict(((i, v.co.copy()) for i, v in enumerate(bm.verts)
                              if select is None or
                              v.select == select and not v.hide))
        if space == Space.GLOBAL:
            mat = ob.matrix_world
            for v in coords.values():
                v[:] = mat * v
        if context.mode != 'EDIT_MESH':
            bm.free()
    else:
        raise ValueError()
    return coords


def _memo_bm_vert_normals(context, ob, space=Space.GLOBAL,
                          select=None):
    space = Space.get(space)
    key = (ob.name, space, select)
    key = memo_append_mat(key, context, space, ob)
    return key


@memoize(_memo_bm_vert_normals)
def bm_vert_normals(context, ob, space=Space.GLOBAL, select=None):
    """BMeshの頂点の法線を返す。
    :type context: bpy.types.Context
    :type ob: bpy.types.Object
    :param space: GLOBAL, LOCAL, VIEW, PLANE
    :type space: Space | str
    :param select: 真なら選択要素のみ返す。偽なら表示中の非選択要素
    :return: 辞書のキーはBMVert.indexではなくBMVertSeqでの並び順に拠る
    :rtype: OrderedDict
    """
    space = Space.get(space)
    if space in {Space.VIEW, Space.PLANE}:
        coords = bm_vert_normals(context, ob, Space.GLOBAL, select)
        if space == Space.VIEW:
            mat = context.region_data.view_matrix.to_3x3()
        else:
            mat = tool_data.plane.to_matrix().to_3x3().inverted()
        coords = OrderedDict(((i, mat * v) for i, v in coords.items()))
    else:
        if space not in {Space.GLOBAL, Space.LOCAL}:
            raise ValueError()
        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(ob.data)
            # bm.verts.index_update()
        else:
            bm = bmesh.new()
            bm.from_mesh(ob.data, face_normals=True, use_shape_key=False,
                         shape_key_index=0)
        coords = OrderedDict(
            ((i, v.normal.copy()) for i, v in enumerate(bm.verts)
             if select is None or v.select == select and not v.hide))
        if space == Space.WORLD:
            mat = ob.matrix_world.to_3x3()
            for v in coords.values():
                v[:] = mat * v
        if context.mode != 'EDIT_MESH':
            bm.free()

    for v in coords.values():
        v.normalize()

    return coords


###############################################################################
# Armature
###############################################################################
def get_bones(ob, mode=None, filter=BoneFilter.ALL):
    """
    :type ob: bpy.types.Object
    :param mode: 'OBJECT', 'POSE', 'EDIT'
    :type mode: str
    :type filter: BoneFilter
    :rtype: OrderedDict
    """
    with vaarm.CustomProperty():
        if not mode:
            mode = ob.mode
        if mode == 'OBJECT':
            bone_seq = ob.data.bones
        elif mode == 'POSE':
            bone_seq = ob.pose.bones
        else:  # 'EDIT'
            bone_seq = ob.data.edit_bones
        layers = ob.data.layers

        if filter == BoneFilter.ALL:
            bones = list(bone_seq)

        elif filter == BoneFilter.LAYER:
            bones = []
            for bone in bone_seq:
                if any([a and b for a, b in zip(layers, bone.layers)]):
                    bones.append(bone)

        else:
            bones = []
            for bone in bone_seq:
                if not any([a and b for a, b in zip(layers, bone.layers)]):
                    continue
                if bone.hide:
                    continue
                if filter == BoneFilter.SELECT and bone.select:
                    bones.append(bone)
                elif filter == BoneFilter.SELECT_HEAD and bone.select_head:
                    bones.append(bone)
                elif filter == BoneFilter.SELECT_TAIL and bone.select_tail:
                    bones.append(bone)
                elif filter in {BoneFilter.SELECT_ANY,
                                BoneFilter.SELECT_ANY_OPTIMIZED}:
                    if bone.select or bone.select_head or bone.select_tail:
                        bones.append(bone)

        if filter == BoneFilter.SELECT_ANY_OPTIMIZED:
            bone_flags = {b: True for b in bones}
            for bone in bones:
                if bone.select:
                    pass
                elif bone.select_head:
                    # この親がリストの中に在りtailか全体を選択しているならFalse
                    if bone.use_connect and bone.parent:
                        parent = bone.parent
                        if parent in bones:
                            if parent.select or parent.select_tail:
                                bone_flags[bone] = False
                elif bone.select_tail:
                    # この子がリストの中に在り全体を選択しているならFalse
                    for child in bone.children:
                        if child in bones:
                            if child.use_connect and child.select:
                                bone_flags[bone] = False
            bones = [b for b, f in bone_flags.items() if f]

    return OrderedDict([(bone.name, bone) for bone in bones])


def _memo_arm_bone_coords(context, ob, space=Space.GLOBAL, mode=None,
                          filter=BoneFilter.ALL):
    space = Space.get(space)
    if mode is None:
        mode = ob.mode
    key = (ob.name, space, mode, filter)
    key = memo_append_mat(key, context, space, ob)
    return key


@memoize(_memo_arm_bone_coords)
def arm_bone_coords(context, ob, space=Space.GLOBAL, mode=None,
                    filter=BoneFilter.ALL):
    """Boneのheadとtailの座標を返す。
    :type context: bpy.types.Context
    :type ob: bpy.types.Object
    :param space: GLOBAL, LOCAL, VIEW, REGION, PLANE, BONE
    :type space: Space | str
    :param mode: 'OBJECT', 'POSE', 'EDIT'
    :type mode: str
    :type filter: BoneFilter
    :return: {name: (head, tail), ...}
    :rtype: OrderedDict
    """
    space = Space.get(space)
    with vaarm.CustomProperty():
        if mode is None:
            mode = ob.mode
        if mode == 'OBJECT':
            def get_co(bone):
                return bone.head_local.copy(), bone.tail_local.copy()
            def get_mat(bone):
                return bone.matrix_local
            # NOTE: Bone.head, Bone.tali は Bone Space。
            #       Bone.matrix は 3x3 で Bone Space
        elif mode == 'POSE':
            # NOTE: psoe.location は boneSpace
            #       head, tail はposemodeでは変化しない
            def get_co(bone):
                return bone.head.copy(), bone.tail.copy()
            def get_mat(bone):
                return bone.matrix
            # NOTE: constraint適用後の座標。
            #       constraint適用前のmatrixが欲しいならPoseBone.matrix_channel。
        else:  # 'EDIT'
            def get_co(bone):
                return bone.head.copy(), bone.tail.copy()
            def get_mat(bone):
                return bone.matrix

        bones = get_bones(ob, mode, filter)

        if space == Space.BONE:
            coords = OrderedDict()
            for bone in bones.values():
                imat = get_mat(bone).invented()
                head_tail = get_co(bone)
                if bone.parent:
                    head_tail = (imat * head_tail[0], imat * head_tail[1])
                coords[bone.name] = head_tail

        elif space in {Space.GLOBAL, Space.LOCAL}:
            coords = OrderedDict(
                [(name, get_co(bone)) for name, bone in bones.items()])
            if space == Space.GLOBAL:
                mat = ob.matrix_world
                for head_tail in coords.values():
                    for i in range(2):
                        v = head_tail[i]
                        v[:] = mat * v

        elif space in {Space.VIEW, Space.REGION, Space.PLANE}:
            coords = arm_bone_coords(context, ob, Space.GLOBAL, mode, filter)
            if space == Space.VIEW:
                mat = context.region_data.view_matrix
                coords = OrderedDict(
                    [(name, (mat * ht[0], mat * ht[1]))
                     for name, ht in coords.items()])
            elif space == Space.REGION:
                coords = OrderedDict(
                    [(name, tuple(project_v3_list(context, head_tail)))
                     for name, head_tail in coords.items()])
            else:
                mat = tool_data.plane.to_matrix().inverted()
                coords = OrderedDict(
                    [(name, (mat * head_tail[0], mat * head_tail[1]))
                     for name, head_tail in coords.items()])

        else:
            raise ValueError()

    return coords


def _memo_arm_bone_matrices(context, ob, space=Space.GLOBAL, mode=None,
                            filter=BoneFilter.ALL):
    space = Space.get(space)
    if mode is None:
        mode = ob.mode
    key = (ob.name, space, mode, filter)
    key = memo_append_mat(key, context, space, ob)
    return key


@memoize(_memo_arm_bone_matrices)
def arm_bone_matrices(context, ob, space=Space.GLOBAL, mode=None,
                      filter=BoneFilter.ALL):
    """Boneのmatrixの辞書を返す。
    :type context: bpy.types.Context
    :type ob: bpy.types.Object
    :param space: GLOBAL, LOCAL, VIEW, PLANE, BONE
    :type space: Space | str
    :param mode: 'OBJECT', 'POSE', 'EDIT'
    :type filter: BoneFilter
    :return: {name: Matrix, ...}
    :rtype: OrderedDict[str, Matrix]
    """
    space = Space.get(space)
    with vaarm.CustomProperty():
        if mode is None:
            mode = ob.mode
        if mode == 'OBJECT':
            def get_mat(bone):
                return bone.matrix_local
        elif mode == 'POSE':
            def get_mat(bone):
                return bone.matrix
        else:  # 'EDIT'
            def get_mat(bone):
                return bone.matrix

        bones = get_bones(ob, mode, filter)

        if space == Space.BONE:
            matrices = OrderedDict()
            for bone in bones.values():
                mat = get_mat(bone).copy()
                if bone.parent:
                    mat = get_mat(bone.parent).inverted() * mat
                matrices[bone.name] = mat

        elif space in {Space.GLOBAL, Space.LOCAL}:
            matrices = OrderedDict(
                [(name, get_mat(bone).copy()) for name, bone in bones.items()])
            if space == Space.GLOBAL:
                mat = ob.matrix_world
                for name in list(matrices.keys()):
                    matrices[name] = mat * matrices[name]

        elif space in {Space.VIEW, Space.PLANE}:
            matrices = arm_bone_matrices(context, ob, Space.GLOBAL, mode,
                                         filter)
            if space == Space.VIEW:
                mat = context.region_data.view_matrix
            else:
                mat = tool_data.plane.to_matrix().inverted()
            matrices = OrderedDict([(n, mat * m) for n, m in matrices.items()])
        else:
            raise ValueError()

    return matrices


###############################################################################
# Initialize cache
###############################################################################
def cache_init(context):
    ob = context.active_object
    if context.mode == 'OBJECT':
        object_coords(context, Space.GLOBAL, None)
        object_matrices(context, Space.GLOBAL, None)
    elif context.mode == 'EDIT_MESH':
        bm_vert_coords(context, ob, Space.GLOBAL, None)
        bm_vert_normals(context, ob, Space.GLOBAL, None)
    elif context.mode in {'EDIT_ARMATURE', 'POSE'}:
        arm_bone_coords(context, ob, Space.GLOBAL, filter=BoneFilter.ALL)
        arm_bone_matrices(context, ob, Space.GLOBAL, filter=BoneFilter.ALL)
    # manipulatorは視点とカーソルだけは更新する
    mmat = manipulator_matrix(context)
    mmat.update(context, view_only=True, cursor_only=True)


###############################################################################
# Manipulator Matrix
###############################################################################
def _memo_manipulator_matrix(context):
    v3d = context.space_data
    if v3d:
        orientation = v3d.transform_orientation
        pivot_point = v3d.pivot_point
    else:
        orientation = 'GLOBAL'
        pivot_point = 'BOUNDING_BOX_CENTER'

    if orientation == 'VIEW' and context.region_data:
        vmat = flatten(context.region_data.view_matrix)
    else:
        vmat = None
    if pivot_point == 'CURSOR':
        cursor = tuple(context.scene.cursor_location)
    else:
        cursor = None
    return orientation, pivot_point, vmat, cursor


# @memoize(_memo_manipulator_matrix)
@memoize(lambda context: True)
def manipulator_matrix(context):
    return vamanipul.ManipulatorMatrix(context)
