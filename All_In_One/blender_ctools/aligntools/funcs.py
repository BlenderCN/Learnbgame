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


import bpy
from mathutils import Matrix, Vector
import bmesh

from .localutils.checkargs import CheckArgs

from .va import vaarmature as vaarm

from . import tooldata
from . import memocoords
from .enums import *


tool_data = tooldata.tool_data

checkargs = CheckArgs(True)


# def _is_iterable(x):
#     iterable = (collections.abc.Sequence, Euler, Matrix, Quaternion, Vector)
#     return isinstance(x, iterable) and \
#         not isinstance(x, (str, bytes, bytearray, memoryview))
#
#
# def flatten(seq):
#     return tuple(localutils.utils.flatten(seq, _is_iterable))

def normalize_m3(mat):
    """3x3のmatrixを正規化する。
    :type mat: Matrix
    """
    # TODO: 要テスト
    mat.normalize()
    axes = list(mat.col)
    """:type: list[Vector]"""
    valid = [v.length > 0.0 for v in axes]
    if all(valid):
        pass
    elif not any(valid):
        mat.identity()
    elif valid.count(False) == 1:
        for i in range(3):
            if valid[i]:
                continue
            axes[i][:] = vec = axes[i - 2].cross(axes[i - 1])
            if vec.length == 0.0:  # 他二つが直線
                vec[:] = axes[i - 2].orthogonal()
            vec.normalize()
    else:
        for i in range(3):
            if not valid[i]:
                continue
            v = Vector([0.0, 0.0, 0.0])
            v[i - 2] = 1.0
            axes[i - 1][:] = vec = axes[i].cross(v)
            """:type: Vector"""
            if vec.length > 0:
                vec.normalize()
            else:
                vec.zero()
                vec[i - 1] = 1.0
            axes[i - 2][:] = vec = axes[i - 1].cross(axes[0])
            vec.normalize()


def get_orientation(context, space, normalize=True):
    """座標系を表す3x3の行列を返す"""
    manipulator_matrix = memocoords.manipulator_matrix(context)
    space_name = space if isinstance(space, str) else space.name
    if space_name in manipulator_matrix.orientations:
        if space_name == 'NORMAL':
            # pivot_pointによりNORMALとACTIVE_NORMALを切り替える
            o = manipulator_matrix.orientation
            manipulator_matrix.orientation = 'NORMAL'
            mat = manipulator_matrix.to_3x3()
            manipulator_matrix.orientation = o
        else:
            mat = manipulator_matrix.orientations[space_name]
            if not mat:
                return None
    else:
        space = Space.get(space)
        if space == Space.MANIPULATOR:
            mat = manipulator_matrix.to_3x3()
        elif space == Space.WORLD:
            return Matrix.Identity(3)
        elif space == Space.REGION:
            return manipulator_matrix.orientations['VIEW'].copy()
        elif space == Space.PLANE:
            return tool_data.plane.to_matrix(True).to_3x3()
        elif space == Space.AXIS:
            return tool_data.axis.to_matrix(True).to_3x3()
        else:
            return None
    if normalize:
        normalize_m3(mat)
    return mat


_bm = None


def get_active(context):
    global _bm
    actob = context.active_object
    if context.mode == 'EDIT_MESH':
        bm = _bm = bmesh.from_edit_mesh(actob.data)
        active = bm.select_history.active
    elif context.mode == 'EDIT_ARMATURE':
        active = context.active_bone
        with vaarm.CustomProperty():
            if not active.is_visible:
                active = None
    elif context.mode == 'POSE':
        active = context.active_pose_bone
        with vaarm.CustomProperty():
            if not active.is_visible:
                active = None
    else:
        if actob and actob.is_visible(context.scene):
            active = actob
        else:
            active = None
    return active


def get_active_coord(context, head_tail=0.0):
    """activeな要素のworld座標を返す"""
    active = get_active(context)
    if active:
        actob = context.active_object
        mat = actob.matrix_world
        if context.mode == 'OBJECT':
            return active.matrix_world.to_translation()
        elif context.mode == 'EDIT_MESH':
            if isinstance(active, bmesh.types.BMVert):
                v = active.co
            elif isinstance(active, bmesh.types.BMEdge):
                v = (active.verts[0].co + active.verts[1].co) / 2
            else:
                v = active.calc_center_median()
            return mat * v
        elif context.mode in ('EDIT_ARMATURE', 'POSE'):
            v = active.head * (1.0 - head_tail) + active.tail * head_tail
            return mat * v


def update_tag(context, objects=None):
    if objects:
        for ob in objects:
            ob.update_tag({'OBJECT'})
    else:
        ob = context.active_object
        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(ob.data)
            bm.normal_update()
            bmesh.update_edit_mesh(ob.data, True, True)
        # elif ob.mode == 'EDIT':
        #     ob.data.update_tag({'DATA'})


def is_support_grid_orientation():
    p = bpy.types.SpaceView3D.bl_rna.properties['transform_orientation']
    return 'GRID' in p.enum_items