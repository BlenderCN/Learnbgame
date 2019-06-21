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
from operator import itemgetter

import bpy
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector
import bpy.props

from . import vawm as vawm


code = """
cdef struct BoundBox:
    pass
cdef struct bGPdata:
    pass
cdef struct RegionView3D:
    pass
cdef struct RenderInfo:
    pass
cdef struct RenderEngine:
    pass
cdef struct ViewDepths:
    pass
cdef struct SmoothView3DStore:
    pass
cdef struct wmTimer:
    pass
cdef:
    struct RegionView3D:
        float winmat[4][4]         # /* GL_PROJECTION matrix */
        float viewmat[4][4]        # /* GL_MODELVIEW matrix */
        float viewinv[4][4]        # /* inverse of viewmat */
        float persmat[4][4]        # /* viewmat*winmat */  # 逆！！ persmat = winmat * viewmat
        float persinv[4][4]        # /* inverse of persmat */

        # /* viewmat/persmat multiplied with object matrix, while drawing and selection */
        float viewmatob[4][4]
        float persmatob[4][4]


        # /* user defined clipping planes */
        float clip[6][4]
        float clip_local[6][4]       # /* clip in object space, means we can test for clipping in editmode without first going into worldspace */
        struct BoundBox *clipbb

        struct bGPdata *gpd          # /* Grease-Pencil Data (annotation layers) */

        struct RegionView3D *localvd # /* allocated backup of its self while in localview */
        struct RenderInfo *ri
        struct RenderEngine *render_engine
        struct ViewDepths *depths
        void *gpuoffscreen

        # /* animated smooth view */
        struct SmoothView3DStore *sms
        struct wmTimer *smooth_timer


        # /* transform widget matrix */
        float twmat[4][4]

        float viewquat[4]          # /* view rotation, must be kept normalized */
        float dist                 # /* distance from 'ofs' along -viewinv[2] vector, where result is negative as is 'ofs' */
        float camdx, camdy         # /* camera view offsets, 1.0 = viewplane moves entire width/height */
        float pixsize              # /* runtime only */
        float ofs[3]               # /* view center & orbit pivot, negative of worldspace location,
                                   # * also matches -viewinv[3][0:3] in ortho mode.*/
        float camzoom              # /* viewport zoom on the camera frame, see BKE_screen_view3d_zoom_to_fac */
        char is_persp              # /* check if persp/ortho view, since 'persp' cant be used for this since
                                   # * it can have cameras assigned as well. (only set in setwinmatrixview3d) */
        char persp
        char view
        char viewlock
        char viewlock_quad         # /* options for quadview (store while out of quad view) */
        char pad[3]
        float ofs_lock[2]          # /* normalized offset for locked view: (-1, -1) bottom left, (1, 1) upper right */

        short twdrawflag
        short rflag


        # /* last view (use when switching out of camera view) */
        float lviewquat[4];
        short lpersp, lview; # /* lpersp can never be set to 'RV3D_CAMOB' */

        float gridview;
        float twangle[3];


        # /* active rotation from NDOF or elsewhere */
        float rot_angle;
        float rot_axis[3];
"""

def cython_test():
    import Cython.Build.Inline
    result = Cython.Build.Inline.cython_inline(code, locals=globals(), globals=globals())
    print('result', result)

def axis_angle_to_quat(axis, angle):
    """source/blender/blenlib/intern/math_rotation.c: 690
    axis_angle_to_quat()

    Axis angle to Quaternions
    :type axis: Vector
    :param angle: radian
    :type angle: float
    """
    if axis.length == 0.0:
        return Quaternion((1, 0, 0, 0))
    nor = axis.normalized()
    phi = angle / 2
    si = math.sin(phi)
    return Quaternion((math.cos(phi), nor[0] * si, nor[1] * si, nor[2] * si))


def eulO_to_gimbal_axis(eul):
    """source/blender/blenlib/intern/math_rotation.c: 1378
    eulO_to_gimbal_axis()

    the matrix is written to as 3 axis vectors
    :type eul: Euler
    """
    gmat = Matrix.Identity(3)
    R_axis = [('X', 'Y', 'Z').index(i) for i in eul.order]

    # first axis is local
    mat = eul.to_matrix()
    gmat.col[R_axis[0]][:] = mat.col[R_axis[0]][:]

    # second axis is local minus first rotation
    teul = eul.copy()
    teul[R_axis[0]] = 0.0
    mat = teul.to_matrix()
    gmat.col[R_axis[1]][:] = mat.col[R_axis[1]][:]

    # Last axis is global
    gmat.col[R_axis[2]][:] = (0.0, 0.0, 0.0)
    gmat.col[R_axis[2]][R_axis[2]] = 1.0

    return gmat


def axis_angle_to_gimbal_axis(rotation_axis_angle):
    """source/blender/editors/transform/transform_manipulator.c: 165
    axis_angle_to_gimbal_axis()

    could move into BLI_math however this is only useful for display/editing
    purposes

    :param rotation_axis_angle: [angle(radian), x, y, z]
    :type rotation_axis_angle: list[float]
    """
    gmat = Matrix.Identity(3)
    angle = rotation_axis_angle[0]
    axis = Vector(rotation_axis_angle[1:])
    cross_vec = Vector((axis[1], axis[2], axis[0]))

    # X-axis
    v = cross_vec.cross(axis)
    v.normalize()
    quat = axis_angle_to_quat(axis, angle)
    gmat.col[0][:] = quat * v

    # Y-axis
    quat = axis_angle_to_quat(axis, math.pi / 2)
    gmat.col[1][:] = quat * gmat.col[0]

    # Z-axis
    gmat.col[2][:] = axis

    for i in range(3):
        gmat.col[i].normalize()

    return gmat


def bone_is_visible(bone, ignore_hide=False):
    """Boneが表示中であるか。
    :type bone: bpy.types.Bone | bpy.types.EditBone | bpy.types.PoseBone
    :param ignore_hide: レイヤーのチェックのみ行う
    :type ignore_hide: bool
    :rtype: bool
    """
    if isinstance(bone, bpy.types.PoseBone):
        arm = bone.id_data.data  # id_dada: bpy.types.Object
        bone = bone.bone  # bpy.types.Bone
    else:
        arm = bone.id_data  # id_data: bpy.types.Armature
    if not ignore_hide and bone.hide:
        return False
    return any([a and b for a, b in zip(arm.layers, bone.layers)])


def vecs_aabb_center(vecs):
    """複数のVectorのAABBを求めてその中心を返す。
    :type vecs: list[Vector]
    """
    minvec = Vector([min(vecs, key=itemgetter(i))[i] for i in range(3)])
    maxvec = Vector([max(vecs, key=itemgetter(i))[i] for i in range(3)])
    return (minvec + maxvec) / 2


def vecs_average(vecs):
    """平均を求める。
    :type vecs: list[Vector]
    """
    return sum(vecs, Vector()) / len(vecs)


def gimbal_axis(context, active_object=None, active_pose_bone=None):
    """source/blender/editors/transform/transform_manipulator.c: 201
    gimbal_axis()
    これがNoneを返す場合は、GIMBALの代替としてNORMALを使う。
    :return: 3x3 Matrix か None を返す。
    :rtype: Matrix | None
    """
    actob = active_object or context.active_object
    if not actob:
        return None

    gmat = None
    if actob.mode == 'POSE' or active_pose_bone:
        if active_pose_bone:
            pose_bone = active_pose_bone
            actob = pose_bone.id_data
        else:
            arm = actob.data
            active_bone = arm.bones.active
            pose_bone = None
            for pbone in actob.pose.bones:
                if pbone.bone == active_bone:
                    # hideについて考慮しないのはソースでそうなっているから
                    if bone_is_visible(pbone, ignore_hide=True):
                        pose_bone = pbone
                        break
        if pose_bone:
            if pose_bone.rotation_mode in \
                    ('XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'):
                mat = eulO_to_gimbal_axis(pose_bone.rotation_euler)
            elif pose_bone.rotation_mode == 'AXIS_ANGLE':
                mat = axis_angle_to_gimbal_axis(pose_bone.rotation_axis_angle)
            else:
                return None

            # apply bone transformation
            tmat = pose_bone.bone.matrix * mat

            if pose_bone.parent:
                mat = pose_bone.parent.matrix.to_3x3() * tmat
                # needed if object transformation isn't identity
                gmat = actob.matrix_world.to_3x3() * mat
            else:
                gmat = actob.matrix_world.to_3x3() * tmat

            for i in range(3):
                gmat.col[i].normalize()
    else:
        if actob.rotation_mode in ('XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'):
            gmat = eulO_to_gimbal_axis(actob.rotation_euler)

        elif actob.rotation_mode == 'AXIS_ANGLE':
            gmat = axis_angle_to_gimbal_axis(actob.rotation_axis_angle)

        else:  # 'QUATERNION'
            return None

        if actob.parent:
            parent_mat = actob.parent.matrix_world.to_3x3()
            for i in range(3):
                parent_mat.col[i].normalize()
            gmat = parent_mat * gmat

    return gmat


###############################################################################
# Calc Active Normal (Incomplete. Don't use)
###############################################################################
def _createSpaceNormal(mat, normal):
    """transform_orientations.c: 238"""
    normal = normal.normalized()
    if normal.length == 0.0:
        return False
    tangent = Vector([0, 0, 1])
    mat.col[2][:] = normal
    mat.col[0][:] = mat.col[2].cross(tangent)
    if mat.col[0].length_squared == 0.0:
        tangent[:] = [1, 0, 0]
        mat.col[0][:] = tangent.cross(mat.col[2])
    mat.col[1][:] = mat.col[2].cross(mat.col[0])
    for i in range(3):
        mat.col[i].normalize()
    return True


def _createSpaceNormalTangent(mat, normal, tangent):
    """transform_orientations.c: 266"""
    normal = normal.normalized()
    if normal.length == 0.0:
        return False
    mat.col[2][:] = normal
    mat.col[1][:] = -tangent
    if mat.col[1].to_tuple() == (0.0, 0.0, 0.0):
        mat.col[1][2] = 1.0
    mat.col[0][:] = mat.col[2].cross(mat.col[1])
    mat.col[0].normalize()
    if mat.col[0].length == 0.0:
        return False
    mat.col[1] = mat.col[2].cross(mat.col[0])
    mat.col[1].normalize()
    return  True


def _BM_editselection_normal(active_elem, r_normal):
    """bmesh_marking.c: 769"""
    if isinstance(active_elem, bmesh.types.BMVert):
        normal = active_elem.normal
    elif isinstance(active_elem, bmesh.types.BMEdge):
        v1, v2 = active_elem.verts
        normal = v1.normal + v2.normal
        plane = v2.co - v1.co
        vec = normal.cross(plane)
        normal = plane.cross(vec)
        normal.normalize()
    else:
        normal = active_elem.normal
    r_normal[:] = normal


def _BM_editselection_plane(bm, active_elem, r_plane):
    """bmesh_marking.c: 737"""
    if isinstance(active_elem, bmesh.types.BMVert):
        if len(bm.select_history) > 1:
            prev = bm.select_history[-2]
            # 721: BM_editselection_center()
            if isinstance(prev, bmesh.types.BMVert):
                vec = prev.co
            elif isinstance(prev, bmesh.types.BMEdge):
                v1, v2 = prev.verts
                vec = (v1.co + v2.co) / 2
            else:
                vec = prev.calc_center_median()

            plane = vec - active_elem.co
        else:
            vec = Vector()
            if active_elem.normal[0] < 0.5:
                vec[0] = 1.0
            elif active_elem.normal[1] < 0.5:
                vec[1] = 1.0
            else:
                vec[2] = 1.0
            plane = active_elem.normal.cross(vec)
        plane.normalize()

    elif isinstance(active_elem, bmesh.types.BMEdge):
        if active_elem.is_boundary:
            loop = active_elem.link_loops[0]
            loop_r_next = loop.link_loop_radial_next
            plane = loop.vert.co - loop_r_next.vert.co
        else:
            v1, v2 = active_elem.verts
            if v2.co[1] > v1.co[1]:
                plane = v2.co - v1.co
            else:
                plane = v1.co - v2.co
        plane.normalize()
    else:
        # bmesh_polygon.c: 277: BM_face_calc_plane()
        verts = active_elem.verts
        if len(verts) == 3:
            lens = Vector()
            for i in range(3):
                lens[i] = (verts[i] - verts[(i + 1) % 3]).length
            difs = [0, 0, 0]
            for i in range(3):
                difs[i] = abs(lens[(i + 1) % 3] - lens[(i + 2) % 3])
            order = list(enumerate(difs))
            order.sort(key=lambda i, f: f)
            i1 = order[0][0]
            i2 = order[0][0] + 1
            plane = verts[i1].co - verts[i2].co
        elif len(verts) == 4:
            vec_a = verts[3].co - verts[2].co
            vec_b = verts[0].co - verts[1].co
            plane = vec_a + vec_b
            vec_a = verts[0].co - verts[3].co
            vec_b = verts[1].co - verts[2].co
            vec = vec_a + vec_b
            if plane.length < vec.length:
                plane = vec
        else:
            # bmesh_queries.c: 1339: BM_face_find_longest_loop()
            longest_loop = None
            veclen = 0.0
            for loop in active_elem.loops:
                vec = loop.next.vert.co - loop.vert.co
                if vec.length >= veclen:
                    longest_loop = loop
                    veclen = vec.length

            plane = longest_loop.vert.co - longest_loop.next.vert.co
        plane.normalize()

    r_plane[:] = plane


# def _calc_orientation_active_normal(self, context):
#     actob = context.active_object
#     # trainsform_orientations.c: 949: ED_getTransformOrientationMatrix()
#     # 537: getTransformOrientation()
#     if context.mode == 'EDIT_MESH':
#         bm = bmesh.from_edit_mesh(actob.data)
#         active = bm.select_history.active
#         if not active:
#             return
#         normal = Vector()
#         self._BM_editselection_normal(active, normal)
#         plane = Vector()
#         self._BM_editselection_plane(bm, active, plane)
#
#         normal.negate()  # 739: not needed but this matches 2.68 ...
#
#         # 868: Vectors from edges don't need the special transpose ...
#         # if (result == ORIENTATION_EDGE) {
#         #     mul_mat3_m4_v3(ob->obmat, normal);
#         #     mul_mat3_m4_v3(ob->obmat, plane);
#         # }
#         # else {
#         #     mul_m3_v3(mat, normal);
#         #     mul_m3_v3(mat, plane);
#         # }
#
#         mat = Matrix.Identity(3)
#         if isinstance(active, bmesh.types.BMVert):
#             result = self._createSpaceNormal(mat, normal)
#         else:
#             result = self._createSpaceNormalTangent(mat, normal, plane)
#         return mat


###############################################################################
# ManipulatorMatrix
###############################################################################
class OrientationMatrix(Matrix):
    def __new__(cls, name, mat):
        """
        :param name: 'GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'GIMBAL',
            'VIEW', 'CUSTOM', "Face", "Bone.001", ...
        :type name: str
        :param mat: 3x3 matrix
        :type mat: Matrix
        """
        inst = super().__new__(cls, mat.to_3x3())
        inst.name = name
        return inst

    def copy(self):
        return self.__class__(self.name, self)

    def normalize_3x3(self):
        for i in range(3):
            self.col[i][:3] = self.col[i].to_3d().normalized()

    def normalized_3x3(self):
        mat = self.copy()
        mat.normalize_3x3()
        return mat


class ManipulatorMatrix(Matrix):
    """3DViewのManipulatorを表す行列。
    Contex.modeが 'EDIT_MESH', 'EDIT_ARMATURE', 'EDIT_CURVE', 'EDIT_SURFACE',
    'EDIT_LATTICE', 'POSE', 'OBJECT' の場合に利用可。

    'NORMAL'と'ACTIVE_ELEMENT'の組み合わせの際は、self.orientationは'NORMAL'を
    維持したままで3x3部分を'NORMAL_ACTIVE'の行列で置き換える。
    これはself.orientation、self.pivot_pointのいずれの属性を変更しても行われる
    """

    # ORIENTATIONS = ['GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'NORMAL_ACTIVE',
    #                 'GIMBAL', 'VIEW', 'CUSTOM']
    # PIVOT_POINTS = ['BOUNDING_BOX_CENTER', 'CURSOR', 'INDIVIDUAL_ORIGINS',
    #                 'INDIVIDUAL_ORIGINS_VISUAL', 'MEDIAN_POINT',
    #                 'ACTIVE_ELEMENT', 'ACTIVE_ELEMENT_VISUAL']

    def __new__(cls, context, orientation=None, pivot_point=None,
                default_location=(0, 0, 0), use_normalized=True,
                use_visual=True, use_pose_normal=False, size=4):
        return super().__new__(cls, Matrix.Identity(size))

    def __init__(self, context, orientation=None, pivot_point=None,
                 default_location=(0, 0, 0), use_normalized=True,
                 use_visual=True, use_pose_normal=False, size=4):
        """
        :type context: Context | None
        :param orientation: 'GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'GIMBAL',
            'VIEW', 'CUSTOM'
        :type orientation: str
        :param pivot_point: 'BOUNDING_BOX_CENTER', 'CURSOR',
            'INDIVIDUAL_ORIGINS', 'MEDIAN_POINT', 'ACTIVE_ELEMENT'
        :type pivot_point: str
        :param default_location: pivot_pointが計算できなかった場合に使用
        :type default_location: Vector | list[float]
        :param use_normalized: 真ならself.orientationが更新された際に
            self.normalize_3x3()を呼ぶ。その際にself.orientationsの値は
            変更しない
        :type use_normalized: bool
        :param use_visual: EDIT_ARMATURE+ACTIVE_ELEMENTの場合、manipulatorは
            選択Boneの中心に表示されているが、transform時のpivotはheadの
            位置になる。この引数が偽の場合はtransform時のpivotの座標を用いる
        :type use_visual: bool
        :param use_pose_normal: Poseモードの際orientationにLOCALを指定しても
            実際にはNORMALが使われる。引数を真にする事でこれを有効にする
        """
        self._orientation = 'GLOBAL'
        self._pivot_point = 'BOUNDING_BOX_CENTER'

        # {orientation <str>: <OrientationMatrix>, ...}
        # 'LOCAL','CUSTOM'系以外は正規化してある。
        # 'CUSTOM'のみ値がNoneになる場合が有る
        self.orientations = {}
        # {pivot_point <str>: <Vector> or <None>, ...}
        # 選択要素が無いと値がNoneになる
        self.pivot_points = {}

        self.default_location = Vector(default_location)
        self._use_normalized = use_normalized
        self._use_visual = use_visual
        self._use_pose_normal = use_pose_normal

        self._area_type_bak = None
        self._mode = 'OBJECT'  # bpy.context.mode, self.update()でのみ更新

        if context:
            self.update(context, orientation, pivot_point)

    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_MESH', 'EDIT_ARMATURE', 'EDIT_CURVE',
                                'EDIT_SURFACE', 'EDIT_LATTICE', 'POSE',
                                'OBJECT'}

    # ManipulatorMatrix.orientation -------------------------------------------
    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, name):
        """自身の3x3部分を更新
        :param name: 'GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'GIMBAL',
            'VIEW', 'CUSTOM', "Face", "Bone.001", ...
        :type name: str
        """
        if name not in self.orientations:
            msg = "'{}' not in {}".format(name, list(self.orientations))
            raise ValueError(msg)
        if name == 'NORMAL_ACTIVE':
            name = 'NORMAL'
        self._orientation = name
        use_pose_normal = self.use_pose_normal and self._mode == 'POSE'
        if ((name == 'NORMAL' or name == 'LOCAL' and use_pose_normal) and
                self.pivot_point == 'ACTIVE_ELEMENT'):
            mat = self.orientations['NORMAL_ACTIVE']
        elif name == 'LOCAL' and use_pose_normal:
            mat = self.orientations['NORMAL']
        else:
            mat = self.orientations[name]
        if not mat:  # 'CUSTOM'でNoneになる場合がある
            mat = Matrix.Identity(3)
        for i in range(3):
            self.col[i][:3] = mat.col[i]
        if self.use_normalized:
            self.normalize_3x3()

    def orientation_matrix(self, orientation=None):
        """rtype: Matrix"""
        if orientation is None:
            orientation = self.orientation
        mat = self.orientations[orientation].to_3x3()
        if self.use_normalized:
            mat.normalize_3x3()
        return mat

    # ManipulatorMatrix.pivot_point -------------------------------------------
    @property
    def pivot_point(self):
        return self._pivot_point

    @pivot_point.setter
    def pivot_point(self, name):
        """自身のlocation部分(col[3][:3])を更新
        :param name: 'BOUNDING_BOX_CENTER', 'CURSOR', 'INDIVIDUAL_ORIGINS',
            'MEDIAN_POINT', 'ACTIVE_ELEMENT'
        :type name: str
        """
        if name not in self.pivot_points:
            raise ValueError("'{}' not in {}".format(name, self.pivot_points))
        if name == 'ACTIVE_ELEMENT_VISUAL':
            name = 'ACTIVE_ELEMENT'
        elif name == 'INDIVIDUAL_ORIGINS_VISUAL':
            name = 'INDIVIDUAL_ORIGINS'
        use_pose_normal = self.use_pose_normal and self._mode == 'POSE'
        update_3x3 = (
            (self.orientation == 'NORMAL' or
             self.orientation == 'LOCAL' and use_pose_normal) and
            self.pivot_point == 'ACTIVE_ELEMENT' or name == 'ACTIVE_ELEMENT')
        if len(self.col) == 4:
            self._pivot_point = name
            if name == 'ACTIVE_ELEMENT' and self.use_visual:
                loc = self.pivot_points['ACTIVE_ELEMENT_VISUAL']
            elif name == 'INDIVIDUAL_ORIGINS' and self.use_visual:
                loc = self.pivot_points['INDIVIDUAL_ORIGINS_VISUAL']
            else:
                loc = self.pivot_points[name]
            if loc is None:
                loc = self.default_location
            self.col[3][:3] = loc
        if update_3x3:
            self.orientation = self._orientation

    # ManipulatorMatrix.use_normalized ----------------------------------------
    @property
    def use_normalized(self):
        return self._use_normalized

    @use_normalized.setter
    def use_normalized(self, value):
        """自身の3x3部分も更新する。
        :type value: bool
        """
        self._use_normalized = value
        self.orientation = self._orientation

    # ManipulatorMatrix.use_visual --------------------------------------------
    @property
    def use_visual(self):
        return self._use_visual

    @use_visual.setter
    def use_visual(self, value):
        self._use_visual = value
        self.pivot_point = self._pivot_point

    # ManipulatorMatrix.use_pose_normal ---------------------------------------
    @property
    def use_pose_normal(self):
        return self._use_pose_normal

    @use_pose_normal.setter
    def use_pose_normal(self, value):
        self._use_pose_normal = value
        self.orientation = self._orientation

    # Copy --------------------------------------------------------------------
    def copy(self, size=None):
        """要素をコピーしたインスタンスを返す。
        sizeを指定すると3x3か4x4にリサイズする。
        :type size: int
        :rtype: ManipulatorMatrix
        """
        def cp(value):
            if isinstance(value, (Vector, Matrix)):
                return value.copy()
            else:
                return value

        if size is None:
            if size not in (3, 4):
                raise ValueError('ManipulatorMatrix size must be 3 or 4')
            size = len(self.col)
        inst = self.__class__(None, size=size)
        inst.orientations = {
            t: cp(mat) for t, mat in self.orientations.items()}
        inst.pivot_points = {t: cp(v) for t, v in self.pivot_points.items()}
        inst._orientation = self._orientation
        inst._pivot_point = self._pivot_point
        for i in range(size):
            inst.col[i][:] = self.col[i]
        if size > len(self.col):
            inst.pivot_point = self.pivot_point
        inst.default_location = cp(self.default_location)
        inst._use_normalized = self._use_normalized
        # inst._area_type_bak = self._area_type_bak
        return inst

    # Normalize ---------------------------------------------------------------
    def normalize_3x3(self):
        for i in range(3):
            self.col[i][:3] = self.col[i].to_3d().normalized()

    def normalized_3x3(self):
        mat = self.copy()
        mat.normalize_3x3()
        return mat

    # Utils -------------------------------------------------------------------
    @classmethod
    def _scale_zero_active(cls, context):
        with vawm.AreaExist(context, 'VIEW_3D') as ae:
            area, region = ae.area, ae.region
            v3d = area.spaces.active
            pivot_point = v3d.pivot_point
            v3d.pivot_point = 'ACTIVE_ELEMENT'

            context_dict = bpy.context.copy()
            del context_dict['space_data']
            del context_dict['region_data']
            context_dict['area'] = area
            context_dict['region'] = region
            bpy.ops.transform.resize(context_dict, False, value=(0, 0, 0),
                                     proportional='DISABLED')
            v3d.pivot_point = pivot_point

    # Calc orientations -------------------------------------------------------
    @classmethod
    def _calc_orientation_normal(cls, context, active_object=None):
        """orientationの'NORMAL'を計算する。fallbackとしてNoneを返す"""
        with vawm.AreaExist(context, 'VIEW_3D') as ae:
            area, region = ae.area, ae.region
            override_context = context.copy()
            override_context['area'] = area
            override_context['region'] = region
            if active_object:
                override_context['active_object'] = active_object
                override_context['object'] = active_object
                if active_object.mode == 'EDIT':
                    override_context['edit_object'] = active_object
                else:
                    override_context['edit_object'] = None
            v3d = area.spaces.active
            orient_bak = v3d.transform_orientation
            bpy.ops.transform.create_orientation(override_context, False,
                                                 name='Normal', use=True)
            if v3d.current_orientation:
                mat = v3d.current_orientation.matrix.copy()
                bpy.ops.transform.delete_orientation(override_context, False)
                v3d.transform_orientation = orient_bak
            else:
                mat = None
        return mat

    @classmethod
    def _calc_orientation_normal_active(cls, context, active_object=None):
        """orientationの'NORMAL_ACTIVE'を計算する。fallbackとしてNoneを返す"""
        mat = None
        actob = active_object or context.active_object
        if not actob:
            return mat
        if actob.type == 'MESH' and actob.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(actob.data)
            active = bm.select_history.active
            if active:
                select_verts = [v for v in bm.verts if v.select]
                select_edges = [e for e in bm.edges if e.select]
                select_faces = [f for f in bm.faces if f.select]
                for v in select_verts:
                    v.select = False
                for e in select_edges:
                    e.select = False
                for f in select_faces:
                    f.select = False
                active.select = True
                mat = cls._calc_orientation_normal(context)
                for v in select_verts:
                    v.select = True
                for e in select_edges:
                    e.select = True
                for f in select_faces:
                    f.select = True
                # EdgeがActiveの場合、Yが法線、ZがEdge方向を向いているので、
                # Zを法線、YをEdge方向に修正する
                if isinstance(active, bmesh.types.BMEdge):
                    y = mat.col[1].copy()
                    mat.col[1] = mat.col[2]
                    mat.col[2] = y
                    mat.col[0] = -mat.col[0]

        elif actob.type == 'ARMATURE' and actob.mode == 'EDIT':
            arm = actob.data
            active = arm.edit_bones.active
            if active and bone_is_visible(active):
                if active.select or active.select_head or active.select_tail:
                    flags = [(b.select, b.select_head, b.select_tail)
                             for b in arm.edit_bones]
                    for b in arm.edit_bones:
                        if b == active:
                            b.select = True
                        else:
                            b.select = False
                    mat = cls._calc_orientation_normal(context)
                    for b, sel in zip(arm.edit_bones, flags):
                        select, select_head, select_tail = sel
                        b.select = select
                        b.select_head = select_head
                        b.select_tail = select_tail

        elif actob.mode == 'POSE':
            active = context.active_pose_bone
            if active and bone_is_visible(active):
                pose_bones = actob.pose.bones
                flags = [b.bone.select for b in pose_bones]
                for b in pose_bones:
                    if b == active:
                        b.bone.select = True
                    else:
                        b.bone.select = False
                mat = cls._calc_orientation_normal(context)
                for b, select in zip(pose_bones, flags):
                    b.bone.select = select

        return mat

    @classmethod
    def calc_orientation(cls, context, orientation, active_object=None,
                         active_pose_bone=None,
                         cache=None):
        if context.area.type == 'VIEW_3D':
            v3d = context.space_data
            rv3d = context.region_data
        else:
            v3d = rv3d = None

        if orientation == 'GLOBAL':
            mat = Matrix.Identity(3)
        elif orientation == 'GRID':
            if v3d and hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
                mat = v3d.local_grid_rotation.to_matrix()
            else:
                mat = Matrix.Identity(3)
        elif orientation == 'LOCAL':
            if active_object:
                mat = active_object.matrix_world.to_3x3()
            else:
                selobs = context.selected_objects
                actob = context.active_object
                mat = Matrix.Identity(3)
                if context.mode == 'OBJECT':
                    if len(selobs) == 1:
                        mat = selobs[0].matrix_world.to_3x3()
                    elif actob and actob in selobs:
                        mat = actob.matrix_world.to_3x3()
                elif actob:
                    mat = actob.matrix_world.to_3x3()
        elif orientation == 'NORMAL':
            mat = cls._calc_orientation_normal(context, active_object)
            if not mat:
                if cache and 'LOCAL' in cache:
                    mat = cache['LOCAL'].copy()
                else:
                    mat = cls.calc_orientation(context, 'LOCAL')
        elif orientation == 'NORMAL_ACTIVE':
            mat = cls._calc_orientation_normal_active(context, active_object)
            if not mat:
                if cache and 'NORMAL' in cache:
                    mat = cache['NORMAL'].copy()
                else:
                    mat = cls.calc_orientation(context, 'NORMAL')
        elif orientation == 'GIMBAL':
            mat = gimbal_axis(context, active_object, active_pose_bone)
            if not mat:
                if cache and 'NORMAL' in cache:
                    mat = cache['NORMAL'].copy()
                else:
                    mat = cls.calc_orientation(context, 'NORMAL')
        elif orientation == 'VIEW':
            if rv3d:
                mat = rv3d.view_matrix.to_3x3().inverted()
            else:
                mat = Matrix.Identity(3)
        elif orientation == 'CUSTOM':
            mat = None  # 'CUSTOM'のみNoneを返す場合が有る
            if v3d and v3d.current_orientation:
                for transform_orientation in context.scene.orientations:
                    name = transform_orientation.name
                    if name == v3d.current_orientation.name:
                        mat = transform_orientation.matrix.copy()
                        break
        else:
            mat = None
            for transform_orientation in context.scene.orientations:
                if transform_orientation.name == orientation:
                    mat = transform_orientation.matrix.copy()
                    break
        return mat

    def calc_orientations(self, context):
        """オリエンテーションの行列の辞書を返す。
        ユーザー定義のオリエンテーションの名前が組み込みの 'GLOBAL', 'LOCAL'
        等と被った場合は組み込みの方を優先する。
        source/blender/editors/transform/transform_manipulator.c: 270
        int calc_manipulator_stats(const bContext *C)
        :rtype: dict
        """
        orientations = {}

        # Custom (All)
        for transform_orientation in context.scene.orientations:
            name = transform_orientation.name
            mat = transform_orientation.matrix.copy()
            orientations[name] = OrientationMatrix(name, mat)

        for key in ('GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'NORMAL_ACTIVE',
                    'GIMBAL', 'VIEW', 'CUSTOM'):
            orientations[key] = self.calc_orientation(
                context, key, cache=orientations)

        return orientations

    # calc pivot_points -------------------------------------------------------
    def calc_pivot_points(self, context):
        """
        source/blender/editors/transform/transform_manipulator.c: 270
        int calc_manipulator_stats(const bContext *C)
        EDIT_MESH, EDIT_ARMATURE, EDIT_CURVE, EDIT_SURFACE, EDIT_LATTICE, POSE,
        OBJECT のみ。
        選択要素が無い場合等、値がNoneになる可能性有り。

        EDIT_ARMATUREでACTIVE_ELEMENTの場合、transform時と表示とで差があるので
        表示の際の座標をACTIVE_ELEMENT_VISUALとして辞書に追加する。その他の場合は
        ACTIVE_ELEMENTをACTIVE_ELEMENT_VISUALにコピーする。
        INDIVIDUAL_ORIGINSとINDIVIDUAL_ORIGINS_VISUALも同様。

        :rtype: dict
        """

        selobs = context.selected_objects
        if context.active_object:
            actob = context.active_object
            mat = actob.matrix_world
        else:
            actob = mat = None

        locations = {}

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(actob.data)
            vecs = [v.co for v in bm.verts if v.select]
            if vecs:
                locations['BOUNDING_BOX_CENTER'] = mat * vecs_aabb_center(vecs)
                locations['MEDIAN_POINT'] = mat * vecs_average(vecs)
            active = bm.select_history.active
            if active:
                if isinstance(active, bmesh.types.BMVert):
                    loc = active.co
                elif isinstance(active, bmesh.types.BMEdge):
                    v1, v2 = active.verts
                    loc = (v1.co + v2.co) / 2
                else:
                    loc = active.calc_center_median()
                locations['ACTIVE_ELEMENT'] = mat * loc
                # elif bm.faces.active:
                #     # 履歴のactiveが無い場合、bm.faces.activeを参照する。
                #     # faceが非選択・非表示でも有効。
                #     # 独特の挙動なので将来修正される可能性あり。
                #     loc = bm.faces.active.calc_center_bounds()
                #     locations['ACTIVE_ELEMENT'] = mat * loc

        elif context.mode == 'EDIT_ARMATURE':
            vecs = []
            arm = actob.data
            bones = [bone for bone in arm.edit_bones if bone_is_visible(bone)]
            for edit_bone in bones:
                if edit_bone.select_head:
                    # 親と接続していて、親のtailが選択状態なら追加しない
                    add = True
                    parent = edit_bone.parent
                    if parent and edit_bone.use_connect:
                        if bone_is_visible(parent) and parent.select_tail:
                            add = False
                    if add:
                        vecs.append(edit_bone.head)
                if edit_bone.select_tail:
                    vecs.append(edit_bone.tail)
            if vecs:
                locations['BOUNDING_BOX_CENTER'] = mat * vecs_aabb_center(vecs)
                locations['MEDIAN_POINT'] = mat * vecs_average(vecs)

            # INDIVIDUAL_ORIGINS
            # transform時のpivot: headかtailが選択状態ならheadを対象とし、その
            # 全ての平均を求める
            vecs = []
            for edit_bone in bones:
                if edit_bone.select_head or edit_bone.select_tail:
                    vecs.append(edit_bone.head)
            if vecs:
                locations['INDIVIDUAL_ORIGINS'] = mat * vecs_average(vecs)

            # ピボットをactive elementにしていても
            # transformの際にはActiveBoneのHeadがピボットになる
            active = arm.edit_bones.active
            if active and bone_is_visible(active):
                if active.select:
                    loc = (active.head + active.tail) / 2
                elif active.select_tail:
                    loc = active.tail
                else:
                    loc = active.head
                locations['ACTIVE_ELEMENT_VISUAL'] = mat * loc
                locations['ACTIVE_ELEMENT'] = mat * active.head

        elif context.mode in ('EDIT_CURVE', 'EDIT_SURFACE'):
            vecs = []
            for spline in actob.data.splines:
                for bezt in spline.bezier_points:
                    if not bezt.hide:
                        if bezt.select_control_point:
                            vecs.append(bezt.co)
                        elif actob.data.show_handles:
                            if bezt.select_left_handle:
                                vecs.append(bezt.handle_left)
                            if bezt.select_right_handle:
                                vecs.append(bezt.handle_right)
                for point in spline.points:
                    if point.select and not point.hide:
                        vecs.append(point.co.to_3d())
            if vecs:
                locations['BOUNDING_BOX_CENTER'] = mat * vecs_aabb_center(vecs)
                locations['MEDIAN_POINT'] = mat * vecs_average(vecs)

                # calc active
                # backup
                point_coords = {}
                for spline in actob.data.splines:
                    for bezt in spline.bezier_points:
                        tri = (bezt.co.copy(),
                               bezt.handle_left.copy(),
                               bezt.handle_right.copy())
                        point_coords[bezt] = tri
                    for point in spline.points:
                        point_coords[point] = point.co.copy()
                # scale (0, 0, 0)
                self._scale_zero_active(context)
                # get selected
                loc = None
                for spline in actob.data.splines:
                    for bezt in spline.bezier_points:
                        if not bezt.hide:
                            if bezt.select_control_point:
                                loc = bezt.co
                            elif actob.data.show_handles:
                                if bezt.select_left_handle:
                                    loc = bezt.handle_left
                                if bezt.select_right_handle:
                                    loc = bezt.handle_right
                            if loc:
                                break
                    for point in spline.points:
                        if point.select and not point.hide:
                            loc = point.co.to_3d()
                            break
                if loc:
                    locations['ACTIVE_ELEMENT'] = mat * loc
                # restore
                for point, value in point_coords.items():
                    if isinstance(point, bpy.types.BezierSplinePoint):
                        point.co, point.handle_left, point.handle_right = value
                    else:
                        point.co = value

        elif context.mode == 'EDIT_METABALL':
            # MetaElement.selectが無いので無理！！
            # vecs = []
            # for elem in actob.data.elements:
            #     if elem.select and not elem.hide:
            #         vecs.append(elem.co)
            # if vecs:
            #     locations['BOUNDING_BOX_CENTER'] = \
            #         mat * vecs_aabb_center(vecs)
            #     locations['MEDIAN_POINT'] = mat * vecs_average(vecs)
            # active = actob.data.elements.active
            # if active and active.select and not active.hide:
            #     locations['ACTIVE_ELEMENT'] = mat * active.co
            pass

        elif context.mode == 'EDIT_LATTICE':
            vecs = []
            for point in actob.data.points:
                if point.select:
                    vecs.append(point.co_deform)
            if vecs:
                locations['BOUNDING_BOX_CENTER'] = mat * vecs_aabb_center(vecs)
                locations['MEDIAN_POINT'] = mat * vecs_average(vecs)

                # active
                point_coords = {}
                for point in actob.data.points:
                    point_coords[point] = point.co_deform.copy()
                self._scale_zero_active(context)
                for point in actob.data.points:
                    if point.select:
                        locations['ACTIVE_ELEMENT'] = mat * point.co_deform
                        break
                # restore
                for point, value in point_coords.items():
                    point.co_deform = value

        elif context.mode == 'POSE':
            pose_bones = []
            for pose_bone in actob.pose.bones:
                if bone_is_visible(pose_bone) and pose_bone.bone.select:
                    parent = pose_bone.parent
                    while parent:
                        if bone_is_visible(parent) and parent.bone.select:
                            break
                        parent = parent.parent
                    else:
                        pose_bones.append(pose_bone)
            vecs = []
            for pose_bone in pose_bones:
                vecs.append(pose_bone.matrix.to_translation())
            if vecs:
                locations['BOUNDING_BOX_CENTER'] = mat * vecs_aabb_center(vecs)
                locations['MEDIAN_POINT'] = mat * vecs_average(vecs)

            active = actob.data.bones.active
            if active and bone_is_visible(active) and active.select:
                pose_bone = actob.pose.bones[active.name]
                loc = pose_bone.matrix.to_translation()
                locations['ACTIVE_ELEMENT'] = mat * loc

        elif context.mode == 'PARTICLE':
            pass

        elif context.mode == 'OBJECT':
            if selobs:
                vecs = [ob.matrix_world.to_translation() for ob in selobs]
                locations['BOUNDING_BOX_CENTER'] = vecs_aabb_center(vecs)
                locations['MEDIAN_POINT'] = vecs_average(vecs)
            if actob and actob in selobs:
                locations['ACTIVE_ELEMENT'] = mat.to_translation()

        locations['CURSOR'] = context.scene.cursor_location.copy()

        def cp(value):
            return value.copy() if isinstance(value, Vector) else value

        if 'BOUNDING_BOX_CENTER' not in locations:
            locations['BOUNDING_BOX_CENTER'] = None
        if 'MEDIAN_POINT' not in locations:
            locations['MEDIAN_POINT'] = None
        if 'ACTIVE_ELEMENT' not in locations:
            locations['ACTIVE_ELEMENT'] = cp(locations['BOUNDING_BOX_CENTER'])
        if 'ACTIVE_ELEMENT_VISUAL' not in locations:
            locations['ACTIVE_ELEMENT_VISUAL'] = cp(locations['ACTIVE_ELEMENT'])
        if 'INDIVIDUAL_ORIGINS' not in locations:
            locations['INDIVIDUAL_ORIGINS'] = cp(locations['MEDIAN_POINT'])
        if 'INDIVIDUAL_ORIGINS_VISUAL' not in locations:
            locations['INDIVIDUAL_ORIGINS_VISUAL'] = \
                cp(locations['MEDIAN_POINT'])

        return locations

    def update_orientations(self, context, view_only=False):
        """self.orientationを更新する。
        :param view_only: 'VIEW' のみを更新する。
        """
        if view_only and self.orientations:
            if context.region_data:
                mat = context.region_data.view_matrix.to_3x3().inverted()
            else:
                mat = Matrix.Identity(3)
            self.orientations['VIEW'] = OrientationMatrix('VIEW', mat)
        else:
            self.orientations = self.calc_orientations(context)
        self.orientation = self.orientation

    def update_pivot_points(self, context, cursor_only=False):
        """self.pivot_pointsを更新する。
        :param cursor_only: 'CURSOR' のみを更新する。
        """
        if cursor_only and self.pivot_points:
            self.pivot_points['CURSOR'] = context.scene.cursor_location.copy()
        else:
            self.pivot_points = self.calc_pivot_points(context)
        self.pivot_point = self.pivot_point

    def update(self, context, orientation=None, pivot_point=None,
               view_only=False, cursor_only=False):
        """contextの要素を参照・計算し、自身を更新する。
        :param orientation: enum in ['GLOBAL', 'LOCAL', 'GRID', 'NORMAL',
            'GIMBAL', 'VIEW', 'CUSTOM']
        :type orientation: str
        :param pivot_point: enum in ['BOUNDING_BOX_CENTER', 'CURSOR',
            'INDIVIDUAL_ORIGINS', 'MEDIAN_POINT', 'ACTIVE_ELEMENT']
        :type pivot_point: str
        :param view_only: orientationsの内の 'VIEW' のみを更新する
        :param cursor_only: pivot_pointsの内の 'CURSOR' のみを更新する
        """
        if context.space_data.type == 'VIEW_3D':
            v3d = context.space_data
        else:
            v3d = None
        self._mode = context.mode

        self.update_orientations(context, view_only)
        self.update_pivot_points(context, cursor_only)

        if orientation:
            self.orientation = orientation
        elif v3d:
            self.orientation = v3d.transform_orientation
        else:
            self.orientation = 'GLOBAL'

        if pivot_point:
            self.pivot_point = pivot_point
        elif v3d:
            self.pivot_point = v3d.pivot_point
        else:
            self.pivot_point = 'BOUNDING_BOX_CENTER'

    # Transform Orientation ---------------------------------------------------
    @classmethod
    def transform_orientation(cls, context,
                              use_current_orientation=False,
                              orientation=None):
        """適切なorientationを返す。
        :type use_current_orientation: bool
        :param orientation: enum in ['GLOBAL', 'LOCAL', 'GRID', 'NORMAL',
            'GIMBAL', 'VIEW', 'CUSTOM']
        :type orientation: str
        :rtype: str | None
        """
        v3d = context.space_data
        if v3d.type != 'VIEW_3D':
            return None

        if orientation:
            v3d_orientation = orientation
        else:
            v3d_orientation = v3d.transform_orientation

        if not use_current_orientation:
            if (hasattr(v3d, 'use_local_grid') and v3d.use_local_grid and
                    v3d_orientation != 'GLOBAL'):
                orient = 'GRID'
            else:
                orient = 'GLOBAL'
        else:
            if v3d_orientation in ('GLOBAL', 'GRID'):
                orient = 'LOCAL'
            else:
                orient = v3d_orientation
        return orient

    # def transform_orientation_matrix(
    #         self, context, use_current_orientation=False, orientation=None):
    #     orient = self.transform_orientation(
    #         context, use_current_orientation, orientation)
    #     return self.orientation_matrix(orient)


def test_register():
    """Test Operator"""
    import time
    import bgl

    class data:
        handle = None
        time = 0.0
        mat = None


    def draw_callback(self, context):
        loc = data.mat.col[3].to_3d()
        depth = bgl.Buffer(bgl.GL_BYTE, 1)
        bgl.glGetBooleanv(bgl.GL_DEPTH_TEST, depth)
        linewidth = bgl.Buffer(bgl.GL_FLOAT, 1)
        bgl.glGetFloatv(bgl.GL_LINE_WIDTH, linewidth)
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glLineWidth(6)
        for i in range(3):
            vec = data.mat.col[i].to_3d()
            color = [0, 0, 0]
            color[i] = 1
            bgl.glColor3f(*color)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex3f(*loc)
            bgl.glVertex3f(*(loc + vec))
            bgl.glEnd()

        if depth[0]:
            bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glLineWidth(linewidth[0])

        if time.time() - data.time > 10:
            bpy.types.SpaceView3D.draw_handler_remove(data.handle, 'WINDOW')
            data.handle = None


    class VIEW3D_OT_calc_manipulator(bpy.types.Operator):
        bl_description = 'test'
        bl_idname = 'view3d.calc_manipulator'
        bl_label = 'Calc 3D Manipulator'
        bl_options = {'REGISTER', 'UNDO'}

        def _orientation_items(self, context):
            items = [
                ('GLOBAL', 'Global', '', 'NONE', 0),
                ('LOCAL', 'Local', '', 'NONE', 1)
            ]
            if 'use_local_grid' in bpy.types.SpaceView3D.bl_rna.properties:
                items.append(('GRID', 'Grid', '', 'NONE', 2))
            items.extend(
                [('NORMAL', 'Normal', '', 'NONE', 3),
                 ('GIMBAL', 'Gimbal', '', 'NONE', 4),
                 ('VIEW', 'View', '', 'NONE', 5),
                 ('CUSTOM', 'Custom', '', 'NONE', 6)
                ])
            for i, orient in enumerate(context.scene.orientations, 7):
                name = orient.name
                items.append((name, name, '', 'NONE', i))
            return items
        orientation = bpy.props.EnumProperty(
            name='Orientation',
            items=_orientation_items)
        pivot_point = bpy.props.EnumProperty(
            name='Pivot Point',
            items=(('BOUNDING_BOX_CENTER', 'Bounding Box Center', ''),
                   ('CURSOR', '3D Cursor', ''),
                   ('INDIVIDUAL_ORIGINS', 'Individual Origins', ''),
                   ('MEDIAN_POINT', 'Median Point', ''),
                   ('ACTIVE_ELEMENT', 'Active Element', ''),
                   ('ACTIVE_ELEMENT_VISUAL', 'Active Element View', ''),
            ),
            default='BOUNDING_BOX_CENTER')
        recalc = bpy.props.BoolProperty('Recalc', default=True)

        def __init__(self):
            self.mat = ManipulatorMatrix(bpy.context)

        def execute(self, context):
            mat = self.mat
            if self.recalc:
                mat.update(context)
            mat.orientation = self.orientation
            mat.pivot_point = self.pivot_point
            print(mat)

            if context.area.type == 'VIEW_3D':
                v3d = context.space_data
                if self.orientation != 'CUSTOM':
                    if self.orientation == 'NORMAL_ACTIVE':
                        o = 'NORMAL'
                    else:
                        o = self.orientation
                    v3d.transform_orientation = o
                if self.pivot_point == 'ACTIVE_ELEMENT_VISUAL':
                    p = 'ACTIVE_ELEMENT'
                else:
                    p = self.pivot_point
                v3d.pivot_point = p
            data.mat = mat
            data.time = time.time()
            if not data.handle:
                data.handle = bpy.types.SpaceView3D.draw_handler_add(
                    draw_callback, (self, context), 'WINDOW', 'POST_VIEW')
            context.region.tag_redraw()

            return {'FINISHED'}

        def invoke(self, context, event):
            if context.area.type == 'VIEW_3D':
                v3d = context.space_data
                self.orientation = v3d.transform_orientation
                self.pivot_point = v3d.pivot_point
            self.execute(context)
            return {'FINISHED'}

    bpy.utils.register_class(VIEW3D_OT_calc_manipulator)


if __name__ == '__main__':
    test_register()
