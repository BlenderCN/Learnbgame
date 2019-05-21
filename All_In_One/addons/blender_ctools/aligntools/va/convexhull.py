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


"""
Convex Hull:
    indices = convex_hull(vectors, eps=1e-6)  # 2D/3D

OBB:
    obb_matrix, obb_size = OBB(vectors, eps=1e-6)  # 2D/3D
"""

import math
from collections import defaultdict
from functools import reduce
from itertools import chain
import random

import bpy
import mathutils
from mathutils import Matrix, Vector
import mathutils.geometry as geom
import bmesh


__all__ = ['convex_hull', 'OBB']


def _cross_2d(v1, v2):
    return v1.x * v2.y - v1.y * v2.x


class _Vert:
    __slots__ = ['index', 'co']

    def __init__(self, index, co):
        self.index = index
        self.co = co


###############################################################################
# Convex Hull 2D
###############################################################################
def convex_hull_2d(vecs, eps:'距離がこれ以下なら同一平面と見做す'=1e-6):
    """二次元の凸包を求める。反時計回りになる"""
    if len(vecs) <= 1:
        return list(range(len(vecs)))

    verts = [_Vert(i, v) for i, v in enumerate(vecs)]

    # なるべく離れている二頂点を求める
    medium = reduce(lambda a, b: a + b, vecs) / len(vecs)
    v1 = max(verts, key=lambda v: (v.co - medium).length)
    v2 = max(verts, key=lambda v: (v.co - v1.co).length)
    line = v2.co - v1.co
    if line.length <= eps:
        # 全ての頂点が重なる
        return [0]

    verts.remove(v1)
    verts.remove(v2)
    if not verts:
        return [v1.index, v2.index]

    # 三角形を構成する為の頂点を求める
    line.normalize()
    verts.sort(key=lambda v: abs(_cross_2d(line, v.co - v1.co)))
    v3 = verts[-1]
    dist = _cross_2d(line, v3.co - v1.co)
    if abs(dist) <= eps:
        # 全ての頂点が同一線上にある
        return [v1.index, v2.index]
    elif dist < 0:
        v1, v2 = v2, v1

    verts.remove(v3)

    loop = [v1, v2, v3]  # 反時計回り
    edge_verts = [[], [], []]  # 各辺の外側にある頂点 [v1-v2, v2-v3, v3-v1]
    edge_lines = [(loop[(i + 1) % 3].co - loop[i].co).normalized()
                  for i in range(3)]
    for v in verts:
        for i in range(3):
            line = edge_lines[i]
            if _cross_2d(line, v.co - loop[i].co) < -eps:
                edge_verts[i].append(v)
                break

    num = len(loop)
    i = 0
    while True:
        if i > num - 1:
            break
        if not edge_verts[i]:
            i += 1
            continue

        v1 = loop[i]
        v2 = loop[(i + 1) % num]

        line = (v2.co - v1.co).normalized()
        v3 = min(edge_verts[i], key=lambda v: _cross_2d(line, v.co - v1.co))
        if _cross_2d(line, v3.co - v1.co) < -eps:
            loop.insert(i + 1, v3)
            ed_verts = edge_verts[i][:]
            ed_verts.remove(v3)
            edge_verts[i] = []
            edge_verts.insert(i + 1, [])
            line1 = (v3.co - v1.co).normalized()
            line2 = (v2.co - v3.co).normalized()
            for v in ed_verts:
                if _cross_2d(line1, v.co - v1.co) < -eps:
                    edge_verts[i].append(v)
                elif _cross_2d(line2, v.co - v3.co) < -eps:
                    edge_verts[i + 1].append(v)
            num += 1
        else:
            edge_verts[i] = []
            i += 1

    return [v.index for v in loop]


###############################################################################
# Convex Hull 3D
###############################################################################
class _Face:
    __slots__ = ['verts', 'normal', 'edge_keys', 'outer_verts']

    def __init__(self, v1, v2, v3):
        self.verts = [v1, v2, v3]
        self.normal = geom.normal(v1.co, v2.co, v3.co)
        self.edge_keys = [tuple(sorted((self.verts[i - 1], self.verts[i]),
                                       key=lambda v: v.index))
                          for i in range(3)]
        self.outer_verts = []

    def distance(self, v):
        return geom.distance_point_to_plane(v, self.verts[0].co, self.normal)


def _divide_outer_verts(faces, verts, eps):
    """vertsを各面に分配する"""
    for v in verts:
        for face in faces:
            if face.distance(v.co) > eps:
                face.outer_verts.append(v)
                break


def _find_remove_faces_re(remove_faces, vec, face, edge_faces, eps):
    """vecから見えている面をremove_facesに追加していく"""
    remove_faces.add(face)
    for ekey in face.edge_keys:
        pair = edge_faces[ekey]
        f = pair[1] if pair[0] == face else pair[0]
        if f not in remove_faces:
            if f.distance(vec) > eps:
                _find_remove_faces_re(remove_faces, vec, f, edge_faces, eps)


def convex_hull_3d(vecs, eps:'距離がこれ以下なら同一平面と見做す'=1e-6):
    """三次元又は二次元の凸包を求める"""
    if len(vecs) <= 1:
        return list(range(len(vecs)))

    verts = [_Vert(i, v) for i, v in enumerate(vecs)]

    # なるべく離れている二頂点を求める
    medium = reduce(lambda a, b: a + b, vecs) / len(vecs)
    v1 = max(verts, key=lambda v: (v.co - medium).length)
    v2 = max(verts, key=lambda v: (v.co - v1.co).length)
    line = v2.co - v1.co
    if line.length <= eps:
        # 全ての頂点が重なる
        return [0]

    verts.remove(v1)
    verts.remove(v2)
    if not verts:
        return [v1.index, v2.index]

    # 三角形を構成する為の頂点を求める
    v3 = max(verts, key=lambda v: line.cross(v.co - v1.co).length)
    if line.normalized().cross(v3.co - v1.co).length <= eps:
        # 全ての頂点が同一線上にある
        return [v1.index, v2.index]
    
    verts.remove(v3)
    if not verts:
        return [v1.index, v2.index, v3.index]

    # 四面体を構成する為の頂点を求める
    normal = geom.normal(v1.co, v2.co, v3.co)
    def key_func(v):
        return abs(geom.distance_point_to_plane(v.co, v1.co, normal))
    v4 = max(verts, key=key_func)
    if key_func(v4) <= eps:
        # 全ての頂点が平面上にある
        quat = normal.rotation_difference(Vector((0, 0, 1)))
        vecs_2d = [(quat * v).to_2d() for v in vecs]
        return convex_hull_2d(vecs_2d, eps)

    verts.remove(v4)

    # 四面体作成
    #       ^ normal
    #    v3 |
    #     / |\
    # v1 /____\v2
    #    \    /
    #     \  /
    #     v4

    if geom.distance_point_to_plane(v4.co, v1.co, normal) < 0.0:
        faces = [_Face(v1, v2, v3),
                 _Face(v1, v4, v2), _Face(v2, v4, v3), _Face(v3, v4, v1)]
    else:
        faces = [_Face(v1, v3, v2),
                 _Face(v1, v2, v4), _Face(v2, v3, v4), _Face(v3, v1, v4)]

    # 残りの頂点を各面に分配
    _divide_outer_verts(faces, verts, eps)

    # edge_faces作成
    edge_faces = defaultdict(list)
    for face in faces:
        for ekey in face.edge_keys:
            edge_faces[ekey].append(face)

    while True:
        added = False
        for i in range(len(faces)):
            try:
                face = faces[i]
            except:
                break
            if not face.outer_verts:
                continue

            v1 = max(face.outer_verts, key=lambda v: face.distance(v.co))
            if face.distance(v1.co) > eps:
                # 凸包になるようにv1から放射状に面を貼る
                added = True

                # 隠れて不要となる面を求める
                remove_faces = set()
                _find_remove_faces_re(remove_faces, v1.co, face, edge_faces,
                                      eps)

                # remove_facesを多面体から除去して穴を開ける
                for f in remove_faces:
                    for ekey in f.edge_keys:
                        edge_faces[ekey].remove(f)
                    faces.remove(f)

                # 穴に面を貼る
                new_faces = []
                ekey_count = defaultdict(int)
                for f in remove_faces:
                    for ekey in f.edge_keys:
                        ekey_count[ekey] += 1
                for ekey, cnt in ekey_count.items():
                    if cnt != 1:
                        continue
                    linkface = edge_faces[ekey][0]
                    v2, v3 = ekey
                    if linkface.verts[linkface.verts.index(v2) - 1] != v3:
                        v2, v3 = v3, v2
                    new_face = _Face(v1, v2, v3)
                    for key in new_face.edge_keys:
                        edge_faces[key].append(new_face)
                    new_faces.append(new_face)
                faces.extend(new_faces)

                # 頂点の再分配
                outer_verts = reduce(lambda a, b: a + b,
                                     (f.outer_verts for f in remove_faces))
                if v1 in outer_verts:
                    outer_verts.remove(v1)
                _divide_outer_verts(new_faces, outer_verts, eps)

            else:
                face.outer_verts = []

        if not added:
            break

    return [[v.index for v in f.verts] for f in faces]


###############################################################################
# Convex Hull 3D
###############################################################################
def convex_hull(vecs, eps=1e-6):
    """三次元又は二次元の凸包を求める
    :param vecs: list of 2D/3D array
    :type vecs: list | tuple | numpy.ndarray
    :param eps: 距離がこれ以下なら同一平面と見做す
    """
    n = len(vecs)
    if n == 0:
        return []
    elif n == 1:
        return [0]

    if len(vecs[0]) == 2:
        return convex_hull_2d(vecs, eps)
    else:
        return convex_hull_3d(vecs, eps)

###############################################################################
# CHBB
###############################################################################
def _closest_axis_on_plane(vecs, indices):
    """
    calc_OBBから呼び出す。
    2D/3Dどちらでも可。3Dの場合は全て同一平面上にあるとする
    """
    if not vecs:
        return None
    dim = len(vecs[0])
    axis = None
    dist = 0.0
    for i in range(len(indices)):
        idx1 = indices[i - 1]
        idx2 = indices[i]
        v1 = vecs[idx1]
        v2 = vecs[idx2]
        line = (v2 - v1).normalized()
        dist_tmp = None
        for idx3 in indices:
            if idx3 == idx1 or idx3 == idx2:
                continue
            v3 = vecs[idx3]
            v13 = v3 - v1
            if dim == 3:
                d = line.cross(v13).length
            else:
                d = abs(_cross_2d(line, v13))
            if dist_tmp is None or d > dist_tmp:
                dist_tmp = d
                axis_tmp = v13 - v13.project(line)
                axis_tmp.normalize()
        if axis is None or dist_tmp < dist:
            dist = dist_tmp
            axis = axis_tmp
    return axis


def OBB(vecs, r_indices=None, eps=1e-6):
    """Convex hull を用いたOBBを返す。
    Z->Y->Xの順で長さが最少となる軸を求める。
    :param vecs: list of Vector
    :type vecs: list | tuple
    :param r_indices: listを渡すとconvexhullの結果を格納する
    :type r_indices: None | list
    :param eps: 種々の計算の閾値
    :return:
        (matrix, obb_size)
        matrix:
            type: Matrx
            OBBの回転と中心を表す。vecsが二次元ベクトルの場合は3x3, 三次元なら4x4。
        obb_size:
            type: Vector
            OBBの各軸の長さ。vecsと同じ次元。
    :rtype: (Matrix, Vector)
    """

    if not vecs:
        return None, None

    # 2D ----------------------------------------------------------------------
    if len(vecs[0]) == 2:
        mat = Matrix.Identity(3)
        bb_size = Vector((0, 0))

        indices = convex_hull_2d(vecs, eps)
        if r_indices:
            r_indices[:] = indices

        if len(indices) == 1:
            mat.col[2][:2] = vecs[0]
        elif len(indices) == 2:
            v1 = vecs[indices[0]]
            v2 = vecs[indices[1]]
            xaxis = (v2 - v1).normalized()
            angle = math.atan2(xaxis[1], xaxis[0])
            mat2 = Matrix.Rotation(angle, 2)
            mat.col[0][:2] = mat2.col[0]
            mat.col[1][:2] = mat2.col[1]
            mat.col[2][:2] = (v1 + v2) / 2
            bb_size[0] = (v2 - v1).length
        else:
            yaxis = _closest_axis_on_plane(vecs, indices)
            angle = math.atan2(yaxis[1], yaxis[0]) - math.pi / 2  # X軸
            mat2 = Matrix.Rotation(angle, 2)
            imat2 = Matrix.Rotation(-angle, 2)
            rotvecs = [imat2 * v for v in vecs]
            loc = Vector((0, 0))
            for i in range(2):
                rotvecs.sort(key=lambda v: v[i])
                bb_size[i] = rotvecs[-1][i] - rotvecs[0][i]
                loc[i] = (rotvecs[0][i] + rotvecs[-1][i]) / 2
            mat.col[0][:2] = mat2.col[0]
            mat.col[1][:2] = mat2.col[1]
            mat.col[2][:2] = mat2 * loc
        return mat, bb_size

    # 3D ----------------------------------------------------------------------
    mat = Matrix.Identity(4)
    bb_size = Vector((0, 0, 0))

    indices = convex_hull(vecs, eps)

    if r_indices:
        r_indices[:] = indices

    if isinstance(indices[0], int):  # 2d
        if len(indices) == 1:
            mat.col[3][:3] = vecs[0]
            return mat, bb_size
        
        elif len(indices) == 2:
            # 同一線上
            v1 = vecs[indices[0]]
            v2 = vecs[indices[1]]
            xaxis = (v2 - v1).normalized()
            quat = Vector((1, 0, 0)).rotation_difference(xaxis)
            mat = quat.to_matrix().to_4x4()
            mat.col[3][:3] = (v1 + v2) / 2
            bb_size[0] = (v2 - v1).length
            return mat, bb_size

        else:
            # 同一平面上
            medium = reduce(lambda a, b: a + b, vecs) / len(vecs)
            v1 = max(vecs, key=lambda v: (v - medium).length)
            v2 = max(vecs, key=lambda v: (v - v1).length)
            line = v2 - v1
            v3 = max(vecs, key=lambda v: line.cross(v - v1).length)
            zaxis = geom.normal(v1, v2, v3)
            if zaxis[2] < 0.0:
                zaxis.negate()

            quat = zaxis.rotation_difference(Vector((0, 0, 1)))
            rotvecs = [quat * v for v in vecs]
            indices_2d = indices

    else:  # 3d
        indices_set = set(chain(*indices))
        zaxis = None
        dist = 0.0
        # 最も距離の近い面（平面）と頂点を求める
        for tri in indices:
            v1, v2, v3 = [vecs[i] for i in tri]
            normal = geom.normal(v1, v2, v3)
            d = 0.0
            for v4 in (vecs[i] for i in indices_set if i not in tri):
                f = abs(geom.distance_point_to_plane(v4, v1, normal))
                d = max(f, d)
            if zaxis is None or d < dist:
                zaxis = -normal
                dist = d

        quat = zaxis.rotation_difference(Vector((0, 0, 1)))
        rotvecs = [(quat * v).to_2d() for v in vecs]
        indices_2d = convex_hull_2d(rotvecs, eps)

    yaxis = _closest_axis_on_plane(rotvecs, indices_2d)
    yaxis = quat.inverted() * yaxis.to_3d()

    xaxis = yaxis.cross(zaxis)
    xaxis.normalize()  # 不要？

    mat.col[0][:3] = xaxis
    mat.col[1][:3] = yaxis
    mat.col[2][:3] = zaxis

    # OBBの大きさと中心を求める
    imat = mat.inverted()
    rotvecs = [imat * v for v in vecs]
    loc = Vector()
    for i in range(3):
        rotvecs.sort(key=lambda v: v[i])
        bb_size[i] = rotvecs[-1][i] - rotvecs[0][i]
        loc[i] = (rotvecs[0][i] + rotvecs[-1][i]) / 2
    mat.col[3][:3] = mat * loc
    return mat, bb_size


###############################################################################
# Test
###############################################################################
def test(use_random=True, random_count=10, lifetime=3.0):
    import bpy_extras
    import bgl
    from . import testops

    import localutils
    from localutils import convexhull
    # convexhull = localutils.convexhull

    context = bpy.context
    if context.mode != 'EDIT_MESH':
        return
    ob = context.active_object

    bm = bmesh.from_edit_mesh(ob.data)
    if use_random:
        bm.clear()

        for i in range(random_count):
            bm.verts.new([random.uniform(-1, 1) for i in range(3)])
        # bmesh.update_edit_mesh(ob.data)

    mat = ob.matrix_world
    coords = [mat * v.co for v in bm.verts]

    # convex_hull (3D)
    indices = convex_hull(coords)
    indices = convexhull.convex_hull(coords)
    if indices:
        for tri in indices:
            verts = [bm.verts[i] for i in tri]
            bm.faces.new(verts)
        bm.normal_update()
        bmesh.update_edit_mesh(ob.data)

    # obb (3D)
    obb_mat, obb_scale = OBB(coords)
    obb_mat, obb_scale = convexhull.OBB(coords)
    obb_mat = Matrix(obb_mat)
    obb_scale = Vector(obb_scale)

    def draw(context, event, glsettings):
        if context.mode != 'EDIT_MESH':
            return
        ob = context.active_object
        bm = bmesh.from_edit_mesh(ob.data)

        # convex_hull (2D)
        convex_hull_2d_coords = []
        project = bpy_extras.view3d_utils.location_3d_to_region_2d
        mat = ob.matrix_world
        region_coords = []
        for eve in bm.verts:
            v = project(context.region, context.region_data, mat * eve.co)
            region_coords.append(v)
        indices = convex_hull(region_coords)
        indices = convexhull.convex_hull(region_coords)
        for i in indices:
            convex_hull_2d_coords.append(region_coords[i])

        # obb (2D)
        obb_mat_2d, obb_scale_2d = OBB(region_coords)
        obb_mat_2d, obb_scale_2d = convexhull.OBB(region_coords)
        obb_mat_2d = Matrix(obb_mat_2d)
        obb_scale_2d = Vector(obb_scale_2d)

        # draw 3d obb
        cm = glsettings.region_view3d_space().enter()
        x, y, z = obb_scale / 2
        vecs = [obb_mat * Vector(v) for v in
                [(-x, -y, -z),
                 (x, -y, -z),
                 (x, y, -z),
                 (-x, y, -z),
                 (-x, -y, z),
                 (x, -y, z),
                 (x, y, z),
                 (-x, y, z)]
        ]
        def draw_line(v1, v2):
            if len(v1) == 3:
                bgl.glVertex3f(*v1)
                bgl.glVertex3f(*v2)
            else:
                bgl.glVertex2f(*v1)
                bgl.glVertex2f(*v2)

        bgl.glLineWidth(2.0)
        # X
        bgl.glColor3f(1.0, 0.0, 0.0)
        bgl.glBegin(bgl.GL_LINES)
        for v in vecs:
            bgl.glVertex3f(*v)
        bgl.glEnd()

        # Y
        bgl.glColor3f(0.0, 1.0, 0.0)
        bgl.glBegin(bgl.GL_LINES)
        draw_line(vecs[1], vecs[2])
        draw_line(vecs[3], vecs[0])
        draw_line(vecs[5], vecs[6])
        draw_line(vecs[7], vecs[4])
        bgl.glEnd()

        # Z
        bgl.glColor3f(0.0, 0.0, 1.0)
        bgl.glBegin(bgl.GL_LINES)
        for i in range(4):
            draw_line(vecs[i], vecs[i + 4])
        bgl.glEnd()

        cm.exit()

        # draw 2d
        bgl.glLineWidth(1.0)
        bgl.glColor3f(1.0, 1.0, 1.0)
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for v in convex_hull_2d_coords:
            bgl.glVertex2f(*v)
        bgl.glEnd()

        # draw 2d obb
        bgl.glColor3f(0.0, 1.0, 0.0)
        x, y = obb_scale_2d / 2
        m = Matrix.Identity(4)
        m.col[0][:2] = obb_mat_2d.col[0][:2]
        m.col[1][:2] = obb_mat_2d.col[1][:2]
        m.col[3][:2] = obb_mat_2d.col[2][:2]
        vecs = [(m * Vector(v).to_3d()).to_2d() for v in
                [(-x, -y),
                 (x, -y),
                 (x, y),
                 (-x, y)]
        ]
        # X
        bgl.glColor3f(1.0, 0.0, 0.0)
        bgl.glBegin(bgl.GL_LINES)
        draw_line(vecs[0], vecs[1])
        draw_line(vecs[2], vecs[3])
        bgl.glEnd()
        # Y
        bgl.glColor3f(0.0, 1.0, 0.0)
        bgl.glBegin(bgl.GL_LINES)
        draw_line(vecs[1], vecs[2])
        draw_line(vecs[3], vecs[0])
        bgl.glEnd()

    testops.add_callback(draw, lifetime, 'POST_PIXEL')


if __name__ == '__main__':
    test()