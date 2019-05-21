# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
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
import collections
from collections import defaultdict
from functools import reduce
from itertools import chain

import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils import geometry as geom

from ..localutils.memoize import Memoize

from . import vamath as vam


class _Void:
    def __bool__(self):
        return False

_void = _Void()


#==============================================================================
# LoopTri
#==============================================================================
class LoopTri(collections.abc.MutableSequence):
    def __init__(self, loops, normal=None, area=None, sort=False):
        self.loops = list(loops)
        if normal is not None:
            self.normal = Vector(normal)
        else:
            self.normal = self.calc_normal()
        if area is not None:
            self.area = area
        else:
            self.area = self.calc_area()
        if sort:
            self.sort()

    def __getitem__(self, key):  # __getitem__はリストへの型変換も可
        return self.loops.__getitem__(key)  # int, slice

    def __setitem__(self, key, value):
        self.loops.__setitem__(key, value)

    def __delitem__(self, key):
        self.loops.__delitem__(key)

    def __len__(self):
        return len(self.loops)

    def insert(self, i, x):
        self.loops.insert(i, x)

    def __str__(self):
        return 'LoopTri\n    {}\n    {}\n    {}\n'.format(
            str(self.loops[0]), str(self.loops[1]), str(self.loops[2]))

    def copy(self):
        """:rtype: LoopTri"""
        return self.__class__(self.loops, self.normal, self.area, False)

    def sort(self, head=None):
        """面と法線が同じになるように並び替える
        :type head: BMLoop | BMVert
        """
        face_loops = list(self[0].face.loops)
        self.loops.sort(key=lambda loop: face_loops.index(loop))
        if head:
            # headが先頭に来るように並び替える
            for i in range(3):
                if self[i] == head or self[i].vert == head:
                    self[:] = self[i:] + self[:i]
                    break

    def is_border(self, index):
        """self[index]とself[index + 1]が成す辺がfaceの辺である
        :param index: triの辺のインデックス
        :type index: int
        :rtype: bool
        """
        l1 = self[index]
        l2 = self[(index + 1) % 3]
        return l1.link_loop_next == l2 or l1.link_loop_prev == l2

    def loops_of_edges(self):
        """loop.edgeが辺に相当するloopのリスト
        :rtype: list[BMLoop]
        """
        ls = []
        for i in range(3):
            loop1 = self[i]
            loop2 = self[(i + 1) % 3]
            if loop1.link_loop_next == loop2:
                ls.append(loop1)
            elif loop1.link_loop_prev == loop2:
                ls.append(loop2)
            else:
                ls.append(None)
        return ls

    def calc_normal(self):
        """:rtype: Vector"""
        return geom.normal(*self.coords)

    def calc_area(self):
        """:rtype: float"""
        return geom.area_tri(*self.coords)

    def update_normal(self):
        self.normal = self.calc_normal()

    def update_area(self):
        self.area = self.calc_area()

    @property
    def coords(self):
        """:rtype: list[Vector]"""
        return [loop.vert.co for loop in self]

    @property
    def verts(self):
        """:rtype: list[BMVert]"""
        return [loop.vert for loop in self]

    @property
    def edge_keys(self):
        """
        :return: [(BMVert, BMVert), (BMVert, BMVert), (BMVert, BMVert)]
            各要素はhash(BMVert)でソートしてある
        :rtype: list[(BMVert, BMVert)]
        """
        return [tuple(sorted([self[i].vert, self[(i + 1) % 3].vert], key=hash))
                for i in range(3)]


class LoopTris(list):
    memoize = Memoize(key=lambda *args: id(args[0]),
                      use_instance=True)

    ANGLE_THRESHOLD = math.radians(1.0)
    DIST_THRESHOLD = 1e-6
    AREA_THRESHOLD = 1e-6

    # init --------------------------------------------------------------------
    def __init__(self, bmesh_or_looptris, sort=False):
        """
        :param bmesh_or_looptris: BMeshかLoopTris、若しくはLoopTriのシーケンス
        :type bmesh_or_looptris: BMesh | LoopTris | list | tuple
        :param sort: Bmesh以外を受け取った場合にソートする
        :type sort: bool
        """
        super().__init__()

        # キャッシュ。デフォルトでは無効。
        self.memoize.read = self.memoize.write = False

        if not bmesh_or_looptris:
            return

        if isinstance(bmesh_or_looptris, bmesh.types.BMesh):
            bm = bmesh_or_looptris
            vert_indices = [v.index for v in bm.verts]
            face_indices = [f.index for f in bm.faces]
            self.index_update(bm, verts=True, edges=False, faces=True,
                              loops=False)

            # 頂点と面のインデックスからLoopを求める辞書
            vi_fi_to_loop = {}
            for face in bm.faces:
                for loop in face.loops:
                    vi_fi_to_loop[(loop.vert.index, face.index)] = loop

            # bmeshからmesh生成後、tessfaceを計算
            mesh = bpy.data.meshes.new("tmp")
            bm.to_mesh(mesh)
            for polygon in mesh.polygons:
                polygon.select = False
            mesh.calc_tessface()  # Cubeを分割して8万ポリにしても0.003s

            polygons = tuple(mesh.polygons)

            # 頂点インデックスから面インデックスを参照する辞書
            vi_polys = defaultdict(set)
            for i, polygon in enumerate(polygons):
                for vi in polygon.vertices:
                    vi_polys[vi].add(i)

            for index, tessface in enumerate(mesh.tessfaces):
                # ３つの頂点を共有するpolyを求める
                seq = (vi_polys[i] for i in tessface.vertices)
                poly_indices = reduce(lambda a, b: a & b, seq)

                if len(poly_indices) == 1:
                    poly_index = poly_indices.pop()
                else:
                    # tessfaceがどのpolyに属するか求める
                    for poly_index in poly_indices:
                        polygons[poly_index].select = True
                        mesh.calc_tessface()
                        polygons[poly_index].select = False
                        if mesh.tessfaces[index].select:
                            break
                loops = []
                for vert_index in tessface.vertices:
                    loop = vi_fi_to_loop.get((vert_index, poly_index))
                    if loop:
                        loops.append(loop)
                    else:
                        print('Error')  # 原因不明
                # NOTE: vertices_rawの長さはは必ず4。末尾が0ならverticesの
                # 長さは3となる。
                normal = tessface.normal
                area = tessface.area
                if len(loops) == 3:
                    self.append(LoopTri(loops, normal, area))  # sort不要
                elif len(loops) == 4:
                    t1, t2 = self.tessellate(loops)
                    self.append(LoopTri([loops[i] for i in t1]))
                    self.append(LoopTri([loops[i] for i in t2]))

            # indexの復帰
            for v, i in zip(bm.verts, vert_indices):
                v.index = i
            for f, i in zip(bm.faces, face_indices):
                f.index = i

            # meshを削除
            bpy.data.meshes.remove(mesh)

        else:
            looptris = bmesh_or_looptris
            self.extend(looptris)
            if len(self) > 0 and not isinstance(self[0], LoopTri):
                for i, tri in enumerate(self):
                    self[i] = LoopTri(tri, sort=sort)
            if sort:
                self.sort(key=lambda tri: tri[0].face.index)


    # Generate ----------------------------------------------------------------
    @classmethod
    def from_faces(cls, faces):
        """BMFaceのリストからLoopTrisを生成する。
        :rtype: LoopTris
        """
        triloop_list = []
        for face in faces:
            tri_indices = cls.tessellate(face.loops)
            triloop_list.extend([[face.loops[i] for i in tri]
                                 for tri in tri_indices])
        return cls(triloop_list)

    # Tessellate Polyline -----------------------------------------------------
    @classmethod
    def tessellate(cls, polyline, correct=False):
        """三角形に分割する
        :param polyline: BMLoopかVectorのリスト
        :param correct: ほぼ直線になっている三点に貼られている面を置換する。
        :return: ソート済みのインデックスの二次元リストを返す。
        :rtype: list[(int, int, int)]
        """
        if not polyline or len(polyline) < 3:
            return

        is_loop = isinstance(polyline[0], bmesh.types.BMLoop)

        if len(polyline) == 3:
            tri_indices = [(0, 1, 2)]
        elif len(polyline) == 4:
            if is_loop:
                # 元の面が4頂点だと、歪みが大きくても分割してくれない
                # 1-3で分割した場合 (0, 1, 3), (1, 2, 3)
                d1 = polyline[0].vert.normal.dot(polyline[2].vert.normal)
                # 0-2で分割した場合 (0, 1, 2), (0, 2, 3)
                d2 = polyline[1].vert.normal.dot(polyline[3].vert.normal)
                # 法線の差が大きい方を採用する
                if d1 < d2:
                    tri_indices = [(0, 1, 3), (1, 2, 3)]
                else:
                    tri_indices = [(0, 1, 2), (0, 2, 3)]
            else:
                v1, v2, v3, v4 = polyline
                if (v2 - v4).length < (v1 - v3).length:
                    tri_indices = [(0, 1, 3), (1, 2, 3)]
                else:
                    tri_indices = [(0, 1, 2), (0, 2, 3)]
        else:
            if is_loop:
                seq = [[loop.vert.co for loop in polyline]]
            else:
                seq = [polyline]
            # geom.tessellate_polygon()は 2D list を要求する。
            tri_indices = geom.tessellate_polygon(seq)  # これの精度は不明
            # 順番が無茶苦茶になっているのでソートする
            tri_indices = [tuple(sorted(tri)) for tri in tri_indices]
            tri_indices.sort(key=lambda tri: tri[0])

        if correct:
            tri_indices = cls.correct_tessellate(polyline, tri_indices, True)

        return tri_indices

    # Correct -----------------------------------------------------------------
    @classmethod
    def correct_tessellate(cls, polyline, tri_indices, sort=False):
        """不正な面の修正。
          v4----v        v4-------v
          /      \      /          \
         /        \   v1----v2     v3
        v1---v2---v3         \     /
                              v---v
        v1-v2-3がほぼ直線の場合でもv1-v2-v3に面が貼られる場合が有るので、
        v1-v2-v4, v2-v3-v4で貼り直す。

        :param polyline: １つの面を構成するBMLoopかVectorのリスト
        :type polyline: list[BMLoop | Vector] | tuple[BMLoop | Vector]
        :param tri_indices: polylineにおいて三角形を構成するインデックスの
            二次元リスト。
        :type tri_indices: list[(int, int, int)] | tuple[(int, int, int)]
        :param sort: triの先頭要素でソートする
        :type sort: bool
        :return: インデックスの二次元リスト。
        :rtype: list[(int, int, int)]
        """
        n = len(polyline)
        if n <= 3:
            return [(0, 1, 2)]
        is_loop = isinstance(polyline[0], bmesh.types.BMLoop)
        if is_loop:
            vectors = [loop.vert.co for loop in polyline]
        else:
            vectors = polyline

        new_tris = []
        removed_tris = set()
        corrected_faces_num = 0

        for tri in tri_indices:
            v1, v2, v3 = tri

            if tri in removed_tris:
                continue
            if is_loop:
                area = geom.area_tri(polyline[v1].vert.co,
                                     polyline[v2].vert.co,
                                     polyline[v3].vert.co)
            else:
                area = geom.area_tri(polyline[v1], polyline[v2], polyline[v3])
            if area > cls.AREA_THRESHOLD:
                continue

            # a-bが連続しているように並び替え
            if (v1 + 1) % n == v2:
                if (v1 - 1) % n == v3:
                    v1, v2, v3 = v3, v1, v2
            elif (v2 + 1) % n == v3:
                v1, v2, v3 = v2, v3, v1
            elif (v3 + 1) % n == v1:
                if (v3 - 1) % n == v2:
                    v1, v2, v3 = v2, v3, v1
                else:
                    v1, v2, v3 = v3, v1, v2
            else:
                # 修正が必要な構造ではない
                continue

            vec1 = vectors[v1]
            vec2 = vectors[v2]
            vec3 = vectors[v3]

            if (v2 + 1) % n == v3:
                # v----v---------v
                #  \            /
                #  v1 -- v2 -- v3
                v5, v6 = v1, v3
                fill_143 = False
            else:
                if (vec2 - vec1).dot(vec3 - vec1) < 0:
                    #   v--------v
                    #  /          \
                    # v3      v1---v2
                    #  \     /
                    #   v---v
                    v5, v6 = v3, v2
                    fill_143 = True
                else:
                    #   v---------v
                    #  /           \
                    # v1---v2      v3
                    #        \     /
                    #         v---v
                    v5, v6 = v1, v3
                    fill_143 = False

            for link_tri in tri_indices:
                if link_tri != tri:
                    if v5 in link_tri and v6 in link_tri:
                        break
            else:
                link_tri = None

            if link_tri:
                v4 = link_tri[link_tri.index(v5) - 1]
                tri1 = (v1, v2, v4)
                if fill_143:
                    tri2 = (v1, v4, v3)
                else:
                    tri2 = (v2, v3, v4)
                new_tris.append(tri1)
                new_tris.append(tri2)
                removed_tris.add(tri)
                removed_tris.add(link_tri)

                corrected_faces_num += 1

        r_tri_indices = [tuple(tri) for tri in tri_indices]
        for tri in removed_tris:
            r_tri_indices.remove(tri)
        for tri in new_tris:
            r_tri_indices.append(tri)
        if sort:
            for tri in r_tri_indices:
                tri.sort()
            r_tri_indices.sort(key=lambda tri: tri[0])
        return r_tri_indices

    def correct(self):
        """不正な面の修正。詳細はcorrect_tessellate()。完了後にソートを行う"""
        face_tris_dict = self.face_dict()
        corrected_tris = []
        for face, looptris in face_tris_dict.items():
            polyline = list(face.loops)
            tri_indices = {
                tuple([polyline.index(loop) for loop in looptri]): looptri
                for looptri in looptris}
            result = self.correct_tessellate(polyline, list(tri_indices))

            for tri_index in result:
                # 元のLoopTriをそのまま追加
                if tri_index in tri_indices:
                    corrected_tris.append(tri_indices[tri_index])
                # 新規LoopTriを追加
                else:
                    tri = [polyline[i] for i in tri_index]
                    corrected_tris.append(LoopTri(tri))
        self[:] = corrected_tris
        for tri in self:
            tri.sort()
        self.sort(key=lambda tri: tri[0].face.index)

    # Generate from self ------------------------------------------------------
    def copy(self):
        """全てのLoopTriを複製
        :rtype: LoopTris
        """
        other = self.__class__()
        for tri in self:
            other.append(tri.copy())
        return other

    def filter(self, verts=(), faces=(), loops=(), mode='or'):
        """各要素で絞り込んだ新しいインスタンスを返す。
        :type verts: tuple[BMVert] | list[BMVert]
        :type faces: tuple[BMFace] | list[BMFace]
        :type loops: tuple[BMLoop] | list[BMLoop]
        :param mode: 'or' or 'and'
        :type mode: str
        :rtype: LoopTris
        """
        if not verts and not faces and not loops:
            return None

        verts = set(verts) if verts else set()
        faces = set(faces) if faces else set()
        loops = set(loops) if loops else set()

        tris = []

        for tri in self:
            if mode == 'or':
                exist = False
                if verts:
                    for loop in tri:
                        exist |= loop.vert in verts
                if not exist and faces:
                    exist |= tri[0].face in faces
                if not exist and loops:
                    for loop in tri:
                        exist |= loop in loops
            else:
                exist = True
                if verts:
                    verts_in_tri = [loop.vert for loop in tri]
                    for vert in verts:
                        exist &= vert in verts_in_tri
                if exist and faces:
                    exist &= tri[0].face in faces
                if exist and loops:
                    for loop in loops:
                        exist &= loop in tri
            if exist:
                tris.append(tri)

        return self.__class__(tris)

    # Utils -------------------------------------------------------------------
    @staticmethod
    def index_update(bm, verts=True, edges=True, faces=True, loops=True):
        """BMeshの各インデックスをまとめて更新"""
        if verts:
            bm.verts.index_update()
        if edges:
            bm.edges.index_update()
        if faces:
            bm.faces.index_update()
        if loops:
            for i, loop in enumerate(
                    chain.from_iterable((f.loops for f in bm.faces))):
                loop.index = i

    @staticmethod
    def hash_sorted(objects):
        """hash()を使ってソート
        :rtype: list | tuple
        """
        sorted_items = sorted(objects, key=hash)
        if isinstance(objects, tuple):
            sorted_items = tuple(sorted_items)
        return sorted_items

    # Generator: list of LoopTri of Face Corner -------------------------------
    def tris_of_face_ccw(self, face, face_dict=None):
        """
        ジェネレータ。BMFaceに属するLoopTriを頂点毎に順番にリストで返す。
        LoopTriの要素はその頂点が先頭になるようにその都度並び替える。
        (e.g.)
        0-3   1st [LoopTri:(0, 2, 3), LoopTri:(0, 1, 2))]
        |\|   2nd [LoopTri:(1, 2, 0)]
        1-2   3rd [LoopTri:(2, 0, 1), LoopTri:(2, 3, 0)]
              4th [LoopTri:(3, 0, 2)]
        :type face: BMFace
        :type face_dict: dict | None
        :rtype list[LoopTri]
        """
        if face_dict:
            face_tris = face_dict[face]
        else:
            face_tris = [tri for tri in self if tri[0].face == face]
        num = len(face.loops)
        pos = {loop: i for i, loop in enumerate(face.loops)}
        for loop in face.loops:
            tris = [tri for tri in face_tris if loop in tri]
            d = {}
            for tri in tris:
                d[tri] = sum(((pos[l] - pos[loop] + num) % num for l in tri))
                tri.sort(head=loop)
            tris.sort(key=lambda tri: d[tri], reverse=True)
            yield tris

    # Loop Tangent ------------------------------------------------------------
    @classmethod
    def vert_tangent(cls, vert, vert_prev, vert_next, looptris,
                     fallback=Vector((0, 0, 0))):
        """
        vertと接続するvert_prevとvert_nextが有り、その間にlooptrisが貼られている。
        vert-vert_prevをe1、vert-vert_nextをe2とする場合、
        e1とe2の二等分線上で、looptris上に有るような相対ベクトルを求める。
        なおe1,e2との距離が1.0になるようにベクトルの長さは調節してある。
        vert_prevとvert_nextが逆でも結果は変わらない。
        :type vert: BMVert
        :type vert_prev: BMVert
        :type vert_next: BMVert
        :type looptris: list[LoopTri] | tuple[LoopTri]
        :type fallback: Vector | object
        :rtype: Vector | object
        """
        co = vert.co
        co_prev = vert_prev.co
        co_next = vert_next.co
        v_prev = co_prev - co
        v_next = co_next - co

        if v_prev.length > 0.0 and v_next.length > 0.0:
            v_prev.normalize()
            v_next.normalize()

            # 両ベクトルの向きが同じ
            if v_prev == v_next:
                return v_next

            # 平面生成
            no = (-v_prev + v_next).normalized()
            plane = vam.PlaneVector(co, no)

            for tri in looptris:
                head = tri[0]
                tri.sort(head=vert)
                v1 = tri[1].vert.co
                v2 = tri[2].vert.co
                tri.sort(head=head)  # 戻しておく
                if (v1 - v2).length > 0.0:
                    if plane.distance(v1) * plane.distance(v2) <= 0.0:
                        v_inter = plane.intersect(v1, v2)
                        if v_inter:
                            v = (v_inter - co).normalized()
                            # 長さ調整
                            if v.length > 0:
                                a1 = v.angle(v_prev)
                                a2 = v.angle(v_next)
                                f = abs(math.sin((a1 + a2) / 2))
                                if f > math.sin(cls.ANGLE_THRESHOLD):
                                    v /= f
                                return v
        if isinstance(fallback, Vector):
            return fallback.copy()
        else:
            return fallback

    def loop_tangent(self, loop, looptris=None, fallback=Vector((0, 0, 0))):
        """loopのtangentを計算する
        :type loop: BMLoop
        :type looptris: list[BMLoop] | tuple[BMLoop]
        :type fallback: Vector | object
        :rtype: Vector | object
        """
        vert = loop.vert
        vert_prev = loop.link_loop_prev.vert
        vert_next = loop.link_loop_next.vert
        if looptris is None:
            looptris = self.loop_dict()[loop]
        return self.vert_tangent(vert, vert_prev, vert_next, looptris,
                                 fallback)

    def loop_tangents(self, fallback=Vector((0, 0, 0))):
        """全loopのtangentを計算してその辞書を返す。
        :type fallback: Vector
        :rtype: dict[BMLoop, list[Vector | object]]
        """
        loop_dict = self.loop_dict()
        tangents = {}
        for loop in self.loops:
            vert = loop.vert
            vert_prev = loop.link_loop_prev.vert
            vert_next = loop.link_loop_next.vert
            tangents[loop] = self.vert_tangent(vert, vert_prev, vert_next,
                                               loop_dict[loop], fallback)
        return tangents

    # 各キーからLoopTriを参照する辞書 -----------------------------------------
    @memoize()
    def vert_dict(self):
        """BMVertからLoopTriを参照する辞書を返す
        :rtype: dict[BMVert, list[LoopTri]]
        """
        d = defaultdict(list)
        for tri in self:
            for loop in tri:
                d[loop.vert].append(tri)
        return d

    @memoize()
    def edge_dict(self):
        """BMEdgeからLoopTriを参照する辞書を返す
        :rtype: dict[BMEdge, list[LoopTri]]
        """
        d = defaultdict(list)
        for tri in self:
            for i in range(3):
                loop = tri[i - 1]
                if loop.link_loop_next == tri[i]:
                    d[loop.edge].append(tri)
        return d

    @memoize()
    def face_dict(self):
        """BMFaceからLoopTriを参照する辞書を返す
        :rtype: dict[BMFace, list[LoopTri]]
        """
        d = defaultdict(list)
        for tri in self:
            d[tri[0].face].append(tri)
        return d

    @memoize()
    def loop_dict(self):
        """BMLoopからLoopTriを参照する辞書を返す
        :rtype: dict[BMLoop, list[LoopTri]]
        """
        d = defaultdict(list)
        for tri in self:
            for loop in tri:
                d[loop].append(tri)
        return d

    @memoize()
    def vert_pair_dict(self):
        """(BMVert, BMVert)からLoopTriを参照する辞書を返す
        :rtype: dict[(BMVert, BMVert), list[LoopTri]]
        """
        d = defaultdict(list)
        for tri in self:
            for i in range(3):
                key = self.hash_sorted((tri[i].vert, tri[i - 1].vert))
                d[key].append(tri)
        return d

    @memoize()
    def loop_pair_dict(self):
        """(BMLoop, BMLoop)からLoopTriを参照する辞書を返す
        :rtype: dict[(BMLoop, BMLoop), list[LoopTri]]
        """
        d = defaultdict(list)
        for tri in self:
            for i in range(3):
                key = self.hash_sorted((tri[i], tri[i - 1]))
                d[key].append(tri)
        return d

    def cache_clear(self, *names):
        """:param names: 関数オブジェクトか関数名のリスト"""
        if names:
            for function, cache in self._cache.items():
                for name_or_func in names:
                    if isinstance(name_or_func, str):
                        if function.__name__ == name_or_func:
                            cache.clear()
                    else:
                        if function == name_or_func._function:
                            cache.clear()
        else:
            self._cache.clear()

    # LoopTrisから各要素を抜き出してリストにして返す --------------------------
    @property
    @memoize()
    def verts(self):
        """:rtype: list[BMVert]"""
        ls = list(set(chain.from_iterable(
            ((loop.vert for loop in tri) for tri in self))))
        ls.sort(key=lambda v: v.index)
        return ls

    @property
    @memoize()
    def edges(self):
        """:rtype: list[BMEdge]"""
        ls = list(set(chain.from_iterable(
            ((loop.edge for loop in tri) for tri in self))))
        ls.sort(key=lambda e: e.index)
        return ls

    @property
    @memoize()
    def faces(self):
        """:rtype: list[BMFace]"""
        ls = list(set(chain.from_iterable(
            ((loop.face for loop in tri) for tri in self))))
        ls.sort(key=lambda f: f.index)
        return ls

    @property
    @memoize()
    def loops(self):
        """:rtype: list[BMLoop]"""
        ls = list(set(chain.from_iterable(
            ((loop for loop in tri) for tri in self))))
        ls.sort(key=lambda l: l.index)
        return ls
