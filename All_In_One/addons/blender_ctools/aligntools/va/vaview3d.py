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
from collections import OrderedDict, namedtuple
import numpy as np

import bpy
from bpy.props import *
import mathutils
from mathutils import Matrix, Vector, Quaternion

from ..localutils.checkargs import CheckArgs

from . import vautils as vau
from . import vawm as vawm


#Matrix = Matrix
#Quaternion = Quaternion
#Vector = Vector

try:
    import mathutilsd as db
except:
    db = None

def use_double(use:"bool"):
    if use and db:
        Euler = db.Euler
        Matrix = db.Matrix
        Quaternion = db.Quaternion
        Vector = db.Vector
        return use
    else:
        Euler = mathutils.Euler
        Matrix = mathutils.Matrix
        Quaternion = mathutils.Quaternion
        Vector = mathutils.Vector
        return not use


MIN_NUMBER = 1E-8
PROJECT_MIN_NUMBER = 1E-5  # FlyNavigationModeでこのくらいの誤差が出る
GRID_MIN_PX = 6.0

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
del m_sqrt1_2


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


def quat_to_axis_view_context(context):
    """rv3dのViewTypeを求める
    :return: 'front', 'back', 'left', 'right', 'top', 'bottom', 'user' or None
    :rtype: str | None
    """
    if context.area.type != 'VIEW_3D':
        return None

    v3d = context.space_data
    rv3d = context.region_data
    if not rv3d:  # toolパネル上にマウス
        rv3d_list = vawm.find(bpy.types.RegionView3D, context.area)
        # quad viewでも可とする
        if rv3d_list:
            rv3d = rv3d_list[0]
    if not rv3d:
        return None

    if hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
        local_grid_quat = v3d.local_grid_rotation
    else:
        local_grid_quat = None

    quat = rv3d.view_rotation.inverted()
    view = quat_to_axis_view(quat, local_grid_quat)
    return view


def project(region, rv3d, vec):
    """World Coords (3D) -> Window Coords (3D).
    Window座標は左手系で、Zのクリッピング範囲は0~1。
    """
    v = rv3d.perspective_matrix * vec.to_4d()
    if abs(v[3]) > PROJECT_MIN_NUMBER:
        v /= v[3]
    x = (1 + v[0]) * region.width * 0.5
    y = (1 + v[1]) * region.height * 0.5
    z = (1 + v[2]) * 0.5
    return Vector((x, y, z))


def unproject(region, rv3d, vec, depth_location:"world coords"=None):
    """Window Coords (2D / 3D) -> World Coords (3D).
    Window座標は左手系で、Zのクリッピング範囲は0~1。
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


def project_np(region, rv3d, array):
    """numpyを用いる。
    World Coords (3D) -> Window Coords (3D).
    Window座標は左手系で、Zのクリッピング範囲は0~1。
    :type region: bpy.types.Rgeion
    :type rv3d: bpy.types.RegionView3D
    :param array: 4次まで
    :type array: numpy.ndarray
    """
    # shapeを(N,4)に変更する
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    shape = shape_bak = array.shape
    if len(shape) > 2:
        raise ValueError()
    if len(shape) == 1:
        array = array.reshape((1, shape[0]))
        shape = array.shape
    if shape[1] > 4:
        raise ValueError()
    if shape[1] != 4:
        arr = np.zeros((shape[0], 4))
        arr[:, 3] = 1.0
        arr[:, :shape[1]] = array
        array = arr

    mat = np.array(rv3d.perspective_matrix)
    # arr = np.dot(mat, array.transpose()).transpose()
    # 上記の方法だと結果は正しいけどarr.baseの要素の並び順が転置されている
    arr = np.dot(array, mat.transpose())

    flags = abs(arr[:, 3]) > PROJECT_MIN_NUMBER
    arr[flags] /= arr[flags][:, 3].reshape((-1, 1))

    arr += 1.0
    arr[:, 0] *= region.width * 0.5
    arr[:, 1] *= region.height * 0.5
    arr[:, 2] *= 0.5

    if len(shape_bak) == 1:
        arr.shape = (-1,)
        return arr[0][:3]
    else:
        return arr[:, :3]


def test_project_np(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            break
    else:
        raise ValueError('3D View が無いのでテスト不可')
    space = area.spaces.active
    region = area.regions[-1]
    rv3d = space.region_3d

    arr = np.array([[10, 10, 0, 1], [-2, 2, 99, 1]])
    result_np = project_np(region, rv3d, arr)

    result_bl = []
    for v in arr:
        v = Vector(v)
        result_bl.append(project(region, rv3d, v))

    for a, v in zip(result_np, result_bl):
        for f1, f2 in zip(a, v):
            if abs(f1 - f2) > 1e-4:
                raise ValueError('エラー')
    print('ok')


def unproject_np(region, rv3d, array, depth_location=None):
    """Window Coords (2D / 3D) -> World Coords (3D).
    Window座標は左手系で、Zのクリッピング範囲は0~1。
    :type region: bpy.types.Rgeion
    :type rv3d: bpy.types.RegionView3D
    :param array: 3次まで
    :type array: numpy.ndarray
    :type depth_location: numpy.ndarray
    """
    # shapeを(N,4)に変更する
    do_copy = True
    if not isinstance(array, np.ndarray):
        array = np.array(array)
        do_copy = False
    shape = shape_bak = array.shape
    if len(shape) > 2:
        raise ValueError()
    if len(shape) == 1:
        array = array.reshape((1, shape[0]))
        shape = array.shape
    if shape[1] > 3:
        raise ValueError()
    if shape[1] != 4:
        arr = np.zeros((shape[0], 4))
        arr[:, 3] = 1.0
        arr[:, :shape[1]] = array
        array = arr
        do_copy = False
    if do_copy:
        array = array.copy()

    array[:, 0] *= 2.0 / region.width
    array[:, 1] *= 2.0 / region.height
    if depth_location is not None:
        v = project_np(region, rv3d, depth_location)
        array[:, 2] = v[:, 2] * 2.0
    else:
        array[:, 2] *= 2.0
    array[:, :3] -= 1.0
    if shape_bak[-1] == 2:
        array[:, 2] = 0.0

    mat = np.array(rv3d.perspective_matrix)
    m = np.linalg.inv(mat)
    arr = np.dot(array, m.transpose())
    flags = abs(arr[:, 3]) > PROJECT_MIN_NUMBER
    arr[flags] /= arr[flags][:, 3].reshape((-1, 1))

    if len(shape_bak) == 1:
        arr.shape = (-1,)
        return arr[0][:3]
    else:
        return arr[:, :3]


def test_unproject_np(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            break
    else:
        raise ValueError('3D View が無いのでテスト不可')
    space = area.spaces.active
    region = area.regions[-1]
    rv3d = space.region_3d

    arr = np.array([[10, 10, 0, 1], [-2, 2, 99, 1]], dtype=np.float64)
    result_np = unproject_np(region, rv3d, arr)

    result_bl = []
    for v in arr:
        v = Vector(v)
        result_bl.append(unproject(region, rv3d, v))

    for a, v in zip(result_np, result_bl):
        for f1, f2 in zip(a, v):
            if abs(f1 - f2) > 1e-3:  # 誤差が大きい
                raise ValueError('エラー')
    print('ok')


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


# 使わないだろうからコメントアウト
#def unproject_persp(region, vec:'2D or 3D'):
#    '''region座標系から投資投影座標系に変換'''
#    sx2 = region.width / 2.0
#    sy2 = region.height / 2.0
#    v = vec.to_3d()
#    v[0] = (v[0] - sx2) / sx2
#    v[1] = (v[1] - sy2) / sy2
#    return v
#
#
#def project_persp(region, vec:'2D or 3D'):
#    '''投資投影座標系からregion座標系に変換'''
#    sx2 = region.width / 2.0
#    sy2 = region.height / 2.0
#    v = vec.to_3d()
#    v[0] = v[0] * sx2 + sx2
#    v[1] = v[1] * sy2 + sy2
#    return v


def get_camera_conversion_matrix(scn, camobj, to_camera=True):
    def cot(angle):
        return 1.0 / math.tan(angle)

    render = scn.render
    cam = camobj.data
    obmat = camobj.matrix_world.to_euler().to_matrix().to_4x4()
    #%obmat[3][:3] = camobj.matrix_world[3][:3]
    obmat.translation = camobj.matrix_world.translation
    obimat = obmat.inverted()
    rx = render.resolution_x
    ry = render.resolution_y
    if rx > ry:
        sx = 1.0
        sy = ry / rx
    else:
        sx = rx / ry
        sy = 1.0

    if to_camera:
        m = Matrix()
        m[0][0] = cot(cam.angle / 2) / sx
        m[1][1] = cot(cam.angle / 2) / sy
        #%m[2][2] = m[2][3] = 1.0  # Z値は変更しない
        m[2][2] = m[3][2] = 1.0
        m[3][3] = 0
        mat = m * obimat  # カメラ座標 = mat * ワールド座標
        return mat
    else:
        m = Matrix()
        m[0][0] = 1.0 / (cot(cam.angle / 2) / sx)
        m[1][1] = 1.0 / (cot(cam.angle / 2) / sy)
        m[2][2] = 1.0
        m[3][3] = 1.0
        imat = obmat * m  # ワールド座標 = imat * カメラ座標
        return imat


def get_world_to_camera_matrix(scn, camobj):
    return get_camera_conversion_matrix(scn, camobj, True)


def get_camera_to_world_matrix(scn, camobj):
    return get_camera_conversion_matrix(scn, camobj, False)


def world_to_camera(vec, mat):
    v = mat * vec.to_4d()
    w = abs(v[3])
    return Vector((v[0] / w, v[1] / w, v[2]))


def camera_to_world(vec, imat):
    z = abs(vec[2])
    v = Vector((vec[0] * z, vec[1] * z, vec[2], 1.0))
    return (imat * v).to_3d()


def world_to_screen(vec, scn, mat):
    rx = scn.render.resolution_x
    ry = scn.render.resolution_y
    v = world_to_camera(vec, mat)
    return Vector(((v[0] + 1.0) / 2 * rx, (v[1] + 1.0) / 2 * ry, v[2]))


def screen_to_world(vec, scn, imat):
    rx = scn.render.resolution_x
    ry = scn.render.resolution_y
    v = Vector((vec[0] / rx * 2 - 1.0, vec[1] / ry * 2 - 1.0, vec[2]))
    return camera_to_world(v, imat)


def get_DPBU_dx_unit_pow(region, scale_length=1.0, system_grid=False):
    '''画面中心pと、そこからBlenderUnit分だけ画面と平行に移動したqを
    それぞれwindow座標に変換(p,qは共にworld座標)
    scale_length: context.scene.unit_settings.scale_length
    return:
        dot_per_blender_unit: 1ドット分のblender_unit
        dx: 1グリッド分のblender_unit
        unit_pow: dx = 10 ** (unit_pow)
    '''

    sx = region.width
    sy = region.height
    rv3d = region.region_data
    viewinvmat = rv3d.view_matrix.inverted()
    viewloc = rv3d.view_location
    p = viewloc
    if sx >= sy:
        q = viewloc + Vector(viewinvmat.col[0][:3])
    else:
        q = viewloc + Vector(viewinvmat.col[1][:3])
    dp = project(region, rv3d, p)
    dq = project(region, rv3d, q)
    l = (dp - dq).to_2d().length
    dot_per_blender_unit = dx = l / scale_length

    #unit = 1.0
    unit_pow = 0
    grid_min_px = GRID_MIN_PX * 2 if system_grid else GRID_MIN_PX
    if dx < grid_min_px:
        while dx < grid_min_px:
            dx *= 10
            unit_pow += 1
    else:
        while dx > grid_min_px * 10:
            dx /= 10
            unit_pow -= 1
    return dot_per_blender_unit, dx, unit_pow


#==============================================================================
# Shortcut
#==============================================================================
class Shortcut:
    @CheckArgs.checkargs(type=list(vau.event_types) + [None])
    def __init__(self, type='NONE', press=True,
                 shift=False, ctrl=False, alt=False, oskey=False,
                 draw_shortcut=True, name='', **kw):
        self.type = type  # or None
        self.press = press  # True:押す, False:離す, None:判定しない
        self.shift = shift  # 一応引数にint型も使えるように
        self.ctrl = ctrl
        self.alt = alt
        self.oskey = oskey
        self.draw_shortcut = draw_shortcut  # circular_menuで使うんだけど全部True……
        self.name = name
        for k, v in kw.items():
            setattr(self, k, v)

    def check(self, event):
        if (self.type is None or event.type == self.type):
            value_to = {'PRESS': True, 'RELEASE': False, 'NOTHING': None}
            if value_to[event.value] == self.press:
                if ((self.shift is None or self.shift is event.shift) and
                    (self.ctrl is None or self.ctrl is event.ctrl) and
                    (self.alt is None or self.alt is event.alt) and
                    (self.oskey is None or self.oskey is event.oskey)):
                    return True
        return False

    def label(self):
        if self.draw_shortcut:
            l = []
            if self.shift:
                l.append('Shift + ')
            if self.ctrl:
                l.append('Ctrl + ')
            if self.alt:
                l.append('Alt + ')
            if self.oskey:
                l.append('Oskey + ')
            l.append(self.type.title())
            return ''.join(l)
        else:
            return ''


def check_shortcuts(shortcuts, event, name:'type:str'=None):
    '''nameを指定するとその名前に限定'''
    for shortcut in shortcuts:
        if shortcut.check(event):
            if name is not None:
                if name == shortcut.name:
                    return shortcut
            else:
                return shortcut
    return None


#==============================================================================
# Snap
#==============================================================================
def make_snap_matrix(sx, sy, persmat, snap_to='selected', \
                     snap_to_origin='selected', apply_modifiers=True, \
                     objects=None, subdivide=100):
    '''
    snap_to: ('active', 'selected', 'visible') # snap to mesh & bone
    snap_to_origin: (None, 'none', 'active', 'selected', 'visible', 'objects')\
                                                         #snap to object origin
    apply_modifiers: (True, False)
    '''
    scn = bpy.context.scene
    actob = bpy.context.active_object
    if objects is None:
        if snap_to == 'active':
            obs = [actob] if actob else []
        elif snap_to == 'selected':
            obs = [ob for ob in bpy.context.selected_objects]
            if actob and actob.mode == 'EDIT' and actob not in obs:
                obs.append(actob)
        else:
            obs = [ob for ob in scn.objects if ob.is_visible(scn)]
    else:
        obs = objects
    # window座標(ドット)に変換したベクトルの二次元配列
    #vmat = [[[] for j in range(subdivide)] for i in range(subdivide)]
    colcnt = int(math.ceil(subdivide * sx / max(sx, sy)))
    rowcnt = int(math.ceil(subdivide * sy / max(sx, sy)))
    vmat = [[[] for c in range(colcnt)] for r in range(rowcnt)]

    for ob in obs:
        obmode = ob.mode
        if obmode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if ob.type == 'MESH':
            if ob == actob:
                if obmode == 'EDIT' and apply_modifiers and ob.modifiers:
                    me = ob.to_mesh(bpy.context.scene, 1, 'PREVIEW')
                    meshes = [ob.data, me]
                elif obmode == 'EDIT':
                    meshes = [ob.data]
                else:
                    meshes = [ob.to_mesh(bpy.context.scene, 1, 'PREVIEW')]
            else:
                meshes = [ob.to_mesh(bpy.context.scene, 1, 'PREVIEW')]
            # ※meshes == local座標
            #me.transform(ob.matrix_world)
            for me in meshes:
                for v in me.vertices:
                    if obmode == 'EDIT' and v.hide:
                        continue
                    wldvec = ob.matrix_world * v.co
                    vec = project_v3(sx, sy, persmat, wldvec)
                    if 0 <= vec[0] < sx and 0 <= vec[1] < sy:
                        #row = int(vec[1] / sy * subdivide)
                        #col = int(vec[0] / sx * subdivide)
                        row = int(vec[1] / max(sx, sy) * subdivide)
                        col = int(vec[0] / max(sx, sy) * subdivide)
                        #if 0 <= row < subdivide and 0 <= col < subdivide:
                        vmat[row][col].append(vec)

        elif ob.type == 'ARMATURE':
            if obmode == 'EDIT':
                bones = ob.data.bones
            else:
                bones = ob.pose.bones
            for bone in bones:
                if obmode == 'EDIT':
                    head = bone.head_local
                    tail = bone.tail_local
                else:
                    head = bone.head
                    tail = bone.tail
                for v in (head, tail):
                    wldvec = ob.matrix_world * v
                    vec = project_v3(sx, sy, persmat, wldvec)
                    if 0 <= vec[0] < sx and 0 <= vec[1] < sy:
                        #row = int(vec[1] / sy * subdivide)
                        #col = int(vec[0] / sx * subdivide)
                        row = int(vec[1] / max(sx, sy) * subdivide)
                        col = int(vec[0] / max(sx, sy) * subdivide)
                        #if 0 <= row < subdivide and 0 <= col < subdivide:
                        vmat[row][col].append(vec)

        if obmode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

    # object origins
    if snap_to_origin in (None, 'none'):
        obs_snap_origin = []  # 無し
    elif snap_to_origin == 'active':
        obs_snap_origin = [actob]
    elif snap_to_origin == 'selected':
        obs_snap_origin = [ob for ob in bpy.context.selected_objects]
        if actob and actob.mode == 'EDIT' and actob not in obs:
            obs.append(actob)
    elif snap_to_origin == 'visible':
        obs_snap_origin = [ob for ob in scn.objects if ob.is_visible(scn)]
    else:  # snap_to_origin == 'objects'
        obs_snap_origin = objects
    for ob in obs_snap_origin:
        origin = Vector(ob.matrix_world.translation)
        vec = project_v3(sx, sy, persmat, origin)
        if 0 <= vec[0] < sx and 0 <= vec[1] < sy:
            #row = int(vec[1] / sy * subdivide)
            #col = int(vec[0] / sx * subdivide)
            row = int(vec[1] / max(sx, sy) * subdivide)
            col = int(vec[0] / max(sx, sy) * subdivide)
            #if 0 <= row < subdivide and 0 <= col < subdivide:
            vmat[row][col].append(vec)

    return vmat


def get_vector_from_snap_maxrix(mouseco, max_size, subdivide, snap_vmat, \
                                snap_range):
    # max_size: max(sx, sy)
    snap_vec = snap_vec_len = None
    center = (int(mouseco[1] / max_size * subdivide), \
              int(mouseco[0] / max_size * subdivide))
    #find_before_loop = 0
    r = 0
    find = 0
    #while i <= math.ceil(snap_range / max_size * subdivide)
    #for r in range(int(math.ceil(snap_range / subdivide)) + 1):
    while True:
        for l in vau.get_matrix_element_square(snap_vmat, center, r):
            if not l:
                continue
            for v in l:
                vec = Vector([v[0] - mouseco[0], v[1] - mouseco[1]])
                vec_len = vec.length
                if vec_len <= snap_range:
                    if snap_vec_len is None:
                        snap_vec_len = vec_len
                        snap_vec = v
                        #break
                        find = max(find, 1)
                    elif vec_len < snap_vec_len:
                        snap_vec_len = vec_len
                        snap_vec = v
                        find = max(find, 1)
            #if snap_vec:
            #    break
        if r > snap_range / max_size * subdivide:
            break
        if find == 1:
            find = 2
        elif find == 2:
            break
        r += 1
    return snap_vec

"""
def get_viewmat_and_viewname(context):
    # viewmat not has location

    '''
    viewmat <- invert() -> emptymat
    1.world-coordinate: me.transform(ob.matrix)
    2a.empty-base-coordinate: me.transform(viewmat)
    2b.empty-base-coordinate: me.transform(emptymat.invert())
    2Dvecs = [v.co.copy().resize2D() for v in me.vertices]
    '''

    '''
    # 蛇使い
    view_mat = context.space_data.region_3d.perspective_matrix # view matrix
    ob_mat = context.active_object.matrix # object world space matrix
    total_mat = view_mat*ob_mat # combination of both matrices

    loc = v.co.copy().resize4D() # location vector resized to 4 dimensions
    vec = loc*total_mat # multiply vector with matrix
    vec = mathutils.((vec[0]/vec[3],vec[1]/vec[3],vec[2]/vec[3])) # dehomogenise vector

    # result (after scaling to viewport)
    x = int(mid_x + vec[0]*width/2.0)
    y = int(mid_y + vec[1]*height/2.0)
    #mid_x and mid_y are the center points of the viewport, width and height are the sizes of the viewport.
    '''

    scn = context.scene
    ob = context.active_object
    ob_selected = ob.select

    # add empty object
    l = [True for i in range(32)]
    bpy.ops.object.add(type='EMPTY', view_align=True,
                       location = (0,0,0), layer=l)  # 原点
    ob_empty = context.active_object

    # check localgrid
    space3dview = context.space_data  # Space3DView
    try:
        use_local_grid = space3dview.use_local_grid
    except:
        use_local_grid = False
    if use_local_grid:
        local_grid_rotation = space3dview.local_grid_rotation
        local_grid_location = space3dview.local_grid_location
    else:
        local_grid_rotation = local_grid_location = None

    # check view
    mat = ob_empty.matrix_world.to_3x3().transpose()
    quat = mat.to_quaternion()
    view = quat_to_axis_view(quat, local_grid_rotation)

    # cleanup
    scn.objects.unlink(ob_empty)
    scn.objects.active = ob
    ob.select = ob_selected
    scn.update()

    return mat, view
"""

"""
void ED_view3d_update_viewmat(Scene *scene, View3D *v3d, ARegion *ar, float viewmat[4][4], float winmat[4][4])
{
	RegionView3D *rv3d = ar->regiondata;

	/* setup window matrices */
	if (winmat)
		copy_m4_m4(rv3d->winmat, winmat);
	else
		setwinmatrixview3d(ar, v3d, NULL);

	/* setup view matrix */
	if (viewmat)
		copy_m4_m4(rv3d->viewmat, viewmat);
	else
		setviewmatrixview3d(scene, v3d, rv3d);  /* note: calls BKE_object_where_is_calc for camera... */

	/* update utilitity matrices */
	mul_m4_m4m4(rv3d->persmat, rv3d->winmat, rv3d->viewmat);
	invert_m4_m4(rv3d->persinv, rv3d->persmat);
	invert_m4_m4(rv3d->viewinv, rv3d->viewmat);

	/* calculate pixelsize factor once, is used for lamps and obcenters */
	{
		/* note:  '1.0f / len_v3(v1)'  replaced  'len_v3(rv3d->viewmat[0])'
		 * because of float point precision problems at large values [#23908] */
		float v1[3], v2[3];
		float len_px, len_sc;

		v1[0] = rv3d->persmat[0][0];
		v1[1] = rv3d->persmat[1][0];
		v1[2] = rv3d->persmat[2][0];

		v2[0] = rv3d->persmat[0][1];
		v2[1] = rv3d->persmat[1][1];
		v2[2] = rv3d->persmat[2][1];

		len_px = 2.0f / sqrtf(min_ff(len_squared_v3(v1), len_squared_v3(v2)));
		len_sc = (float)MAX2(ar->winx, ar->winy);

		rv3d->pixsize = len_px / len_sc;
	}
}

MINLINE float len_squared_v3(const float v[3])
{
	return v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
}

MAX2 -> ((ar->winx) > (ar->winy) ? (ar->winx) : (ar->winy))

"""