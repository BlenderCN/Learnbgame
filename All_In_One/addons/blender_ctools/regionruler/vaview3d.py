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


import math
from collections import OrderedDict

from mathutils import Quaternion, Vector


PROJECT_MIN_NUMBER = 1E-5  # FlyNavigationModeでこのくらいの誤差が出る
m_sqrt1_2 = 1 / math.sqrt(2)
FRONT = Quaternion((m_sqrt1_2, -m_sqrt1_2, 0.0, 0.0))
BACK = Quaternion((0.0, 0.0, -m_sqrt1_2, -m_sqrt1_2))
LEFT = Quaternion((0.5, -0.5, 0.5, 0.5))
RIGHT = Quaternion((0.5, -0.5, -0.5, -0.5))
TOP = Quaternion((1.0, 0.0, 0.0, 0.0))
BOTTOM = Quaternion((0.0, -1.0, 0.0, 0.0))
QUAT_AXIS = OrderedDict(
    (('front', FRONT),
     ('back', BACK),
     ('left', LEFT),
     ('right', RIGHT),
     ('top', TOP),
     ('bottom', BOTTOM)
    ))


def quat_to_axis_view(quat, local_grid_rotation=None, epsilon=1e-6):
    """QuaternionからViewを求める。
    source/blender/editors/space_view3d/view3d_view.c:
    ED_view3d_quat_to_axis_view()を参照。
    :param quat: such as rv3d.view_matrix.to_quaternion() or
                 rv3d.view_rotation.inverted()
    :type quat: Quaternion
    :param local_grid_rotation: 必要ならview3d.local_grid_rotationを指定する
    :type local_grid_rotation: Quaternion
    """
    quat = quat.normalized()
    if local_grid_rotation:
        inv_lg = local_grid_rotation.normalized().inverted()
    else:
        inv_lg = None
    for view, view_quat in QUAT_AXIS.items():
        if inv_lg:
            view_quat = view_quat * inv_lg
        if view_quat.rotation_difference(quat).angle < epsilon:
            return view
    return 'user'


def project(region, rv3d, vec):
    """World Coords (3D) -> Region Coords (3D).
    Region座標は左手系で、Zのクリッピング範囲は0~1。
    :type region: bpy.types.Region
    :type rv3d: bpy.types.RegionView3D
    :type vec: mathutils.Vector | collections.abc.Sequence
    """
    v = rv3d.perspective_matrix * Vector(vec).to_4d()
    if abs(v[3]) > PROJECT_MIN_NUMBER:
        v /= v[3]
    x = (1 + v[0]) * region.width * 0.5
    y = (1 + v[1]) * region.height * 0.5
    z = (1 + v[2]) * 0.5
    return Vector((x, y, z))


def unproject(region, rv3d, vec, depth_location:"world coords"=None):
    """Region Coords (2D / 3D) -> World Coords (3D).
    Region座標は左手系で、Zのクリッピング範囲は0~1。
    :type region: bpy.types.Region
    :type rv3d: bpy.types.RegionView3D
    :type vec: mathutils.Vector | collections.abc.Sequence
    :type depth_location: mathutils.Vector | collections.abc.Sequence
    """
    x = vec[0] * 2.0 / region.width - 1.0
    y = vec[1] * 2.0 / region.height - 1.0
    if depth_location:
        z = (project(region, rv3d, depth_location)[2] - 0.5) * 2
    else:
        z = 0.0 if len(vec) == 2 else (vec[2] - 0.5) * 2
    v = rv3d.perspective_matrix.inverted() * Vector((x, y, z, 1.0))
    if abs(v[3]) > PROJECT_MIN_NUMBER:
        v /= v[3]
    return v.to_3d()


def project_v3(sx, sy, persmat, vec) -> "3D Vector":
    """World Coords -> Window Coords. projectより少しだけ速い。"""
    v = persmat * vec.to_4d()
    if abs(v[3]) > PROJECT_MIN_NUMBER:
        v /= v[3]
    x = (1 + v[0]) * sx * 0.5
    y = (1 + v[1]) * sy * 0.5
    z = (1 + v[2]) * 0.5
    return Vector((x, y, z))


def unproject_v3(sx, sy, persmat, vec, depth_location:"world coords"=None,
                 inverted=False) -> "3D Vector":
    """Window Coords -> World Coords. unprojectより少しだけ速い。"""
    invpmat = persmat if inverted else persmat.inverted()
    x = vec[0] * 2.0 / sx - 1.0
    y = vec[1] * 2.0 / sy - 1.0
    if depth_location:
        if inverted:
            z = project_v3(sx, sy, persmat.inverted(), depth_location)[2] * 2 \
                - 1.0
        else:
            z = project_v3(sx, sy, persmat, depth_location)[2] * 2 - 1.0
    else:
        z = vec[2] * 2 - 1.0
    v = invpmat * Vector((x, y, z, 1.0))
    if abs(v[3]) > PROJECT_MIN_NUMBER:
        v /= v[3]
    return v.to_3d()
