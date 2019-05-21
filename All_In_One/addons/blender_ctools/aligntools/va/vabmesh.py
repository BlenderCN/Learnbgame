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


import time
import math
from functools import reduce
from collections import OrderedDict, Counter, defaultdict
from itertools import combinations, chain

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Matrix, Euler, Vector, Quaternion
import mathutils.geometry as geom
import bmesh

from .. import localutils
from ..localutils.checkargs import CheckArgs

from . import vaview3d as vav
from . import vautils as vau
from . import vamath as vam


"""
NOTE:

頂点・辺・面のselect属性は、変更すると属する頂点と辺のselect属性にも影響を及ぼす。

BMesh.select_flush(True):
    表示中の辺と面に於いて、それに属する全ての頂点が選択されていたら辺と面も
    選択状態になる。条件を満たさないものは変更されない。
BMesh.select_flush(False):
    表示中の辺に於いて、それに属する何れかの頂点が非選択なら辺も非選択となり、
    その辺を共有する全ての面も非選択となる。条件を満たさないものは変更されない。
BMesh.select_flush_mode():
    頂点選択が有効:
        表示中の辺と面に於いて、それに属する全ての頂点が選択されていたら辺と面も
        選択状態になり、そうでないなら非選択となる。
    辺選択が有効:
        表示中の面に於いて、それに属する全ての辺が選択されていたら面も選択状態に
        なり、そうでないなら非選択となる。
"""

#==============================================================================
# Dict
#==============================================================================
def vert_verts_dict(bm=None, select=None, hide=None, verts=None, edges=None):
    """
    selectとhideは接続する辺で判別する。辺が選択されていたらその両端の頂点をキーとして追加する。
    select:  True:選択中, False:非選択, None:全て
    hide:    True:非表示, False:表示, None:全て
    verts:   処理するBMVert
             これを指定した場合はbmとselectとhideとedgesは無視される。
             [BMVert, ...]
    edges:   処理するBMEdge
             これを指定した場合はbmとselectとhideは無視される。
             [BMEdge, ...] or [(BMVert, BMVert), ...] or [(3, 1), (7, 3), ...]
    
    return:     type:dict. key:BMVert value:接続するBMVertのリスト。
    """

    if verts:
        verts = set(verts)
        vert_verts = {eve: [] for eve in verts}
        for eve in verts:
            for eed in eve.link_edges:
                eve2 = eed.other_vert(eve)
                if eve2 in verts:
                    vert_verts[eve].append(eve2)
        return vert_verts
    
    if edges is None:
        vert_pairs = [tuple(eed.verts) for eed in bm.edges
                      if (select is None or eed.select == select) and
                         (hide is None or eed.hide == hide)]
        vert_verts = {eve: [] for eve in bm.verts
                      if (select is None or eve.select == select) and
                         (hide is None or eve.hide == hide)}
    else:
        if len(edges) == 0:
            return {}
        elif isinstance(edges[0], bmesh.types.BMEdge):
            vert_pairs = [tuple(eed.verts) for eed in edges]
        else:
            vert_pairs = [tuple(edge) for edge in edges]  # 念の為変換

        vert_verts = {v: [] for v in set(chain(*vert_pairs))}
    for v1, v2 in vert_pairs:
        vert_verts[v1].append(v2)
        vert_verts[v2].append(v1)
    return vert_verts


def edge_edges_dict(bm=None, select=None, hide=None, edges=None):
    """
    
    接続する辺の状態で判別する。check()が真となるものだけがキーとして挿入される。
    select:     True:選択中, False:非選択, None:全て
    hide:       True:非表示, False:表示, None:全て
    edges:      処理するBMEdgeのリスト。これを指定した場合はbmとselectとhideは無視される。
                [BMEdge, ...] or [(BMVert, BMVert), ...] or [(3, 1), ...]
    
    return:     type:dict. key:BMEdge value:接続するBMEdgeのリスト。
    """

    # 処理対象のedgeリスト生成
    if edges is None:
        edges = [eed for eed in bm.edges
                 if (select is None or eed.select == select) and
                         (hide is None or eed.hide == hide)]
    elif len(edges) == 0:
        return {}
    elif not isinstance(edges[0], bmesh.types.BMEdge):
        edges = [tuple(edge) for edge in edges]  # 辞書のキーにする為tupleに変換

    # vertからedgeを参照する辞書を作る
    vert_edges = defaultdict(list)
    if isinstance(edges[0], bmesh.types.BMEdge):
        for eed in edges:
            for eve in eed.verts:
                vert_edges[eve].append(eed)
    else:
        for edge in edges:
            for vert in edge:
                vert_edges[vert].append(edge)

    # edgeからedgeを参照する辞書を作る
    edge_edges = {edge: [] for edge in edges}
    for edge_list in vert_edges.values():
        for e1, e2 in combinations(edge_list, 2):
            edge_edges[e1].append(e2)
            edge_edges[e2].append(e1)

    return edge_edges


def face_faces_dict(bm=None, select=None, hide=None, faces=None,
                    connect_vert=False):
    """
    check()が真となるものだけがキーとして挿入される。
    select:       True:選択中, False:非選択, None:全て
    hide:         True:非表示, False:表示, None:全て
    faces:        処理するBMFaceのリスト。これを指定した場合はbmとselectとhideは無視される。
    connect_vert: Trueなら頂点を共有している面同士は隣接しているとみなす。
                  Falseなら辺を共有している面のみ対象。
    
    return: type:dict. key:BMFace value:接続するBMFaceのリスト。
    """

    if faces is None:
        faces = [efa for efa in bm.faces
                 if (select is None or efa.select == select) and
                    (hide is None or efa.hide == hide)]
    face_faces = {efa: [] for efa in faces}

    if connect_vert:
        vert_faces = defaultdict(list)
        for efa in faces:
            for eve in efa.verts:
                vert_faces[eve].append(efa)
        for bmfaces in vert_faces.values():
            for bmf1, bmf2 in combinations(bmfaces, 2):
                # 辺で接続していたら重複するのでifを付ける
                if bmf2 not in face_faces[bmf1]:
                    face_faces[bmf1].append(bmf2)
                if bmf1 not in face_faces[bmf2]:
                    face_faces[bmf2].append(bmf1)
    else:
        edge_faces = defaultdict(list)
        for efa in faces:
            for eed in efa.edges:
                edge_faces[eed].append(efa)
        for bmfaces in edge_faces.values():
            for bmf1, bmf2 in combinations(bmfaces, 2):
                face_faces[bmf1].append(bmf2)
                face_faces[bmf2].append(bmf1)

    return face_faces


#==============================================================================
# Connect
#==============================================================================
def linked_vertices_list(bm=None, select=None, hide=None,
                         verts=None, edges=None):
    """辺で繋がった頂点の二次元リストを返す"""
    vert_verts = vert_verts_dict(bm, select=select, hide=hide,
                                 verts=verts, edges=edges)
    def key(v1, v2, data):
        return v1 in data[v2] or v2 in data[v1]
    return localutils.utils.groupwith(vert_verts.keys(), key, vert_verts)



def linked_faces_list(bm=None, select=None, hide=None, faces=None,
                      connect_vert=False):
    """繋がった面の二次元のリストを返す。"""
    face_faces = face_faces_dict(bm, select, hide, faces=faces,
                                 connect_vert=connect_vert)
    def key(f1, f2, data):
        return f1 in data[f2] or f2 in data[f1]
    return localutils.utils.groupwith(face_faces.keys(), key, face_faces)


#==============================================================================
# Path
#==============================================================================
class Path(list):
        def __init__(self, arg=(), cyclic=False):
            super().__init__(arg)
            self.cyclic = cyclic


def make_paths_from_edges(edges):
    """Pathのリストを返す。
    [i1, i2, i3, i4, i1].cyclic = False  # 四角形、i1に別の辺が接続
    [i1, i2, i3, i4, i1].cyclic = True  # 四角形
    :param edges: 処理するBMEdgeのリスト。 (BMEdge, ...)
        ((BMVert, BMVert), ...) 若しくは ((1, 3), (7, 3), ...)といった形式でも可。
        BMVertなら返り値のPathの中身もBMVert, intならint
    :type edges: list[BMEdge] | list[(BMVert, BMVert)] | list[(int, int)]
    :return: Pathのリスト。引数がBMedgeかBMVertのタプルならPathの要素はBMVertになる
    :rtype: list[Path]
    """
    paths = []

    vert_verts = vert_verts_dict(edges=edges)
    end_flags = {vert: len(verts) != 2 for vert, verts in vert_verts.items()}
    for vert in vert_verts.keys():
        verts = vert_verts[vert]
        while verts:
            vprev = vert
            vnext = verts.pop()
            vert_verts[vnext].remove(vprev)
            path = Path([vprev, vnext])
            while True:
                if end_flags[vnext]:
                    # if end_flags[vert]:  # 開始点、終了点が共に端
                    if end_flags[path[0]]:  # 開始点、終了点が共に端
                        break
                    else:
                        path.reverse()  # 逆に回る
                        vprev = vert
                elif vnext == vert:  # 周状
                    path.cyclic = True
                    break
                else:
                    vprev = vnext
                vnext = vert_verts[vprev].pop()
                vert_verts[vnext].remove(vprev)
                path.append(vnext)
            paths.append(path)

    return paths


def make_face_outline_paths(bm=None, select=None, hide=None, faces=None,
                            connect_vert=False):
    """
    接続する面が一つだけの辺を外周とみなす。
    select:       True:選択中, False:非選択, None:全て
    hide:         True:非表示, False:表示, None:全て
    faces:        処理するBMFaceのリスト。
                  これを指定した場合はbmとselectとhideは無視される。
    connect_vert: Trueなら頂点を共有している面同士は隣接しているとみなす。
                  Falseなら辺を共有している面のみ対象。
    
    return:       Pathのリスト。
    """

    face_groups = linked_faces_list(bm, select, hide, faces=faces,
                                    connect_vert=connect_vert)

    outline_paths = []
    for face_group in face_groups:
        edge_faces = defaultdict(list)
        for efa in face_group:
            for eed in efa.edges:
                edge_faces[eed].append(efa)

        edges = []
        for eed, bmfaces in edge_faces.items():
            if len(bmfaces) == 1:
                edges.append(eed)
        outline_paths.extend(make_paths_from_edges(edges))

    return outline_paths


#==============================================================================
# LoopTri
#==============================================================================
class LoopTri:
    def __init__(self, loops: "sequence or LoopTri", sort=False):
        self.loops = list(loops)
        if sort:
            self.sort()
#        self.i = 0

    def __getitem__(self, key):  # __getitem__はリストへの型変換も可
        return self.loops.__getitem__(key)  # int, slice

    def __setitem__(self, key, value):
        self.loops.__setitem__(key, value)

    def __contains__(self, item):
        return item in self.loops

    def __iter__(self):
        return self.loops.__iter__()

    def __str__(self):
        text = 'LoopTri\n    {}\n    {}\n    {}\n'
        return text.format(str(self.loops[0]),
                           str(self.loops[1]),
                           str(self.loops[2]))

    def index(self, key):
        return self.loops.index(key)

    def copy(self):
        return self.__class__(self.loops, False)

    def sort(self, head: "BMLoop or BMVert"=None):
        """面と法線が同じになるように並び替える"""
        face_loops = list(self[0].face.loops)
        self.loops.sort(key=lambda loop: face_loops.index(loop))
        if head:
            # headが先頭に来るように並び替える
            for i in range(3):
                if self[i] == head or self[i].vert == head:
                    self[:] = self[i:] + self[:i]
                    break

    def is_border(self, index: "triの辺のインデックス"):
        """self[index]とself[index + 1]が成す辺がfaceの辺である"""
        return self[index].link_loop_next == self[(index + 1) % 3] or \
               self[index].link_loop_prev == self[(index + 1) % 3]

    def loops_of_edges(self):
        """loop.edgeが辺に相当するloopのリスト"""
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

    def calc_area(self):
        return geom.area_tri(*self.coords)

    def calc_normal(self):
        return geom.normal(*self.coords)

    def _coords_get(self):
        return [loop.vert.co for loop in self]

    coords = property(_coords_get)

    def _verts_get(self):
        return [loop.vert for loop in self]

    verts = property(_verts_get)

    def _edge_keys_get(self):
        return [tuple(sorted([self[i].vert, self[(i + 1) % 3].vert], key=hash))
                for i in range(3)]

    edge_keys = property(_edge_keys_get)


#==============================================================================
# LoopTris
#==============================================================================
class LoopTris(list):
    """
    このクラスの各ソートはBMeshを参照せず、各要素のindexでソートする為、
    インスタンス作成前にLoopTris.index_update()の実行を推奨する。
    
    """
    CORRECT_ANGLE_THRESHOLD = math.radians(179.0)
    CORRECT_DIST_THRESHOLD = 1e-6
    CORRECT_AREA_THRESHOLD = 1e-6

    # Init --------------------------------------------------------------------
    def __init__(self,
                 bmesh_or_looptris:"BMeshか((BMLoop, BMLoop, BMLoop), ...)",
                 sort:"BMLoop.face.indexでソート"
                      "bmesh_or_looptrisでBMeshを受け取った時はTrue扱い"=True):
        if isinstance(bmesh_or_looptris, bmesh.types.BMesh):
            bm = bmesh_or_looptris
            # looptris = bm.calc_tessellation()
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
            tessfaces = tuple(mesh.tessfaces)
            
            # 頂点インデックスから面インデックスを参照する辞書
            vi_faces = defaultdict(set)
            for i, polygon in enumerate(polygons):
                for vi in polygon.vertices:
                    vi_faces[vi].add(i)
            
            for index, tessface in enumerate(tessfaces):
                seq = (vi_faces[i] for i in tessface.vertices)
                face_indices = reduce(lambda a, b: a & b, seq)
                if len(face_indices) == 1:
                    face_index = face_indices.pop()
                else:
                    for face_index in face_indices:
                        polygons[face_index].select = True
                        mesh.calc_tessface()
                        polygons[face_index].select = False
                        if mesh.tessfaces[index].select:
                            break
                loops = []
                for vert_index in tessface.vertices:
                    loop = vi_fi_to_loop.get((vert_index, face_index))
                    if loop:
                        loops.append(loop)
                    else:
                        print("Error")  # 原因不明
                if len(loops) == 3:
                    self.append(LoopTri(loops))  # sort不要
                elif len(loops) == 4:
                    self.append(LoopTri(loops[:3]))
                    self.append(LoopTri((loops[2], loops[3], loops[0])))
            
            # meshを削除
            bpy.data.meshes.remove(mesh)

        else:
            looptris = bmesh_or_looptris
            super().__init__(looptris)  # ジェネレータに対応する為、先に処理
            if len(self) > 0 and not isinstance(self[0], LoopTri):
                for i, tri in enumerate(self):
                    self[i] = LoopTri(tri, sort)
            if sort:
                self.sort(key=lambda tri: tri[0].face.index)

    # Generate ----------------------------------------------------------------
    def copy(self):
        """全てのLoopTriを複製"""
        inst = self.__class__()
        for tri in self:
            inst.append(tri.copy())
        return inst

    def filter(self, verts=(), faces=(), loops=(), mode:"or/and"='or'):
        if not verts and not faces and not loops:
            return self.__class__(None, ())

        tris = []
        if verts:
            verts = set(verts)
        if faces:
            faces = set(faces)
        if loops:
            loops = set(loops)

        for tri in self:
            if mode == 'or':
                exist = False
                if faces:
                    exist |= tri[0].face in faces
                if verts and not exist:
                    for loop in tri:
                        exist |= loop.vert in verts
                if loops and not exist:
                    for loop in tri:
                        exist |= loop in loops
            else:
                exist = True
                if faces:
                    exist &= tri[0].face in faces
                if verts and exist:
                    verts_in_tri = [loop.vert for loop in tri]
                    for vert in verts:
                        exist &= vert in verts_in_tri
                if loops and exist:
                    for loop in loops:
                        exist &= loop in tri
            if exist:
                tris.append(tri)

        inst = self.__class__(None, tris, False)
        return inst

    @classmethod
    def from_faces(cls, faces):
        """BMFaceのリストからLoopTrisを生成する。"""
        looptris_tmp = []
        for face in faces:
            loops = face.loops
            # tri_indices = geom.tessellation([loop.vert.co for loop in loops])
            # geom.tessellationのパッチを消したので
            tri_indices = geom.tessellate_polygon(
                [[loop.vert.co for loop in loops]])
            tris = [tuple([loops[i] for i in i3]) for i3 in tri_indices]
            looptris_tmp.extend(tris)
        return cls(looptris_tmp, True)

    # Sort, Update ------------------------------------------------------------
    @classmethod
    def index_update(cls, bm, verts=True, edges=True, faces=True, loops=True):
        if verts:
            bm.verts.index_update()
        if edges:
            bm.edges.index_update()
        if faces:
            bm.faces.index_update()
        if loops:
#            i = 0
#            for face in bm.faces:
#                for loop in face.loops:
#                    loop.index = i
#                    i += 1
            for i, loop in enumerate(chain(*(f.loops for f in bm.faces))):
                loop.index = i

    @classmethod
    def hash_sorted(cls, objects):
        """hash()を使ってソート"""
        sorted_items = sorted(objects, key=hash)
        if isinstance(objects, tuple):
            sorted_items = tuple(sorted_items)
        return sorted_items

#    @classmethod
#    def sorted_loops(cls, loops):
#        """loopsをBMFace.loopsでの位置によりソートしたものを返す"""
#        def key_func(loop):
#            for i, l in enumerate(loop.face.loops):
#                if l == loop:
#                    return i
#        sorted_items = sorted(loops, key=key_func)
#        if isinstance(loops, tuple):
#            sorted_items = tuple(sorted_items)
#        return sorted_items

    # Correct -----------------------------------------------------------------
    @classmethod
    def correct_vectors(cls, vecs):
        """
        要パッチ
        vecs: 単一面の外周を構成するベクトルのリスト。
        """

        # tesstris = geom.tessellation(vecs)
        tesstris = geom.tessellate_polygon([vecs])

        if len(vecs) <= 3:
            return tesstris

        tesstris = list(tesstris)

        removed_tris = set()
        new_tris = []
        corrected_num = 0
        for tri in tesstris:
            if tri in removed_tris:
                continue
            i1, i2, i3 = tri

            # v3 <- v2 <- v1
            if i1 + 1 == i2 and i2 + 1 == i3:
                v1, v2, v3 = vecs[i1], vecs[i2], vecs[i3]
            elif i2 + 1 == i3 and i3 + 1 == i1:
                v1, v2, v3 = vecs[i2], vecs[i3], vecs[i1]
            elif i3 + 1 == i1 and i1 + 1 == i2:
                v1, v2, v3 = vecs[i3], vecs[i1], vecs[i2]
            else:
                continue
            vec1 = v1 - v2
            vec2 = v3 - v2
            angle = vec1.angle(vec2, 0.0)
            if angle >= cls.CORRECT_ANGLE_THRESHOLD:
                # i1とi3を持つ面を探す
                for link_tri in tesstris:
                    if link_tri != tri:
                        if i1 in link_tri and i3 in link_tri:
                            break
                else:
                    link_tri = None
                if link_tri:
                    i4 = link_tri[link_tri.index(i1) - 1]
                    vec3 = vecs[i4] - v2
                    if vec3.length > cls.CORRECT_DIST_THRESHOLD:
                        tri1 = (i1, i2, i4)
                        tri2 = (i2, i3, i4)
                        new_tris.extend((tri1, tri2))
                        removed_tris.add(tri)
                        removed_tris.add(link_tri)
                        corrected_num += 1

        for tri in removed_tris:
            tesstris.remove(tri)
        for tri in new_tris:
            tesstris.append(tri)

        # print('Corrected {0} faces.'.format(corrected_num))

        return tesstris

    @classmethod
    def correct_face(cls, face):
        return cls.correct_vectors([v.co for v in face.verts])


#    def correct(self, sort=True):
#        """
#        v4--v5--------v6
#          /    \     
#         /       \   
#        v1 - v2 ---v3
#        v1-v2-3がほぼ直線の時、v1-v2-v3でtriが生成される場合があるので、
#        v1-v2-5, v2-v3-v5で貼り直す。
#        """
#        face_tris_dict = self.face_dict()
#        removed_tris = set()
#
#        corrected_faces_num = 0
#        for tri in self:
#            if tri in removed_tris or len(tri[0].face.verts) == 3:
#                continue
#
#            l1, l2, l3 = tri
#
#            # loop1 -(next)-> loop2 -(next)-> loop3
#            if l1.link_loop_next == l2 and l2.link_loop_next == l3:
#                loop1, loop2, loop3 = l1, l2, l3
#            elif l2.link_loop_next == l3 and l3.link_loop_next == l1:
#                loop1, loop2, loop3 = l2, l3, l1
#            elif l3.link_loop_next == l1 and l1.link_loop_next == l2:
#                loop1, loop2, loop3 = l3, l1, l2
#            else:
#                continue
#            v1 = loop1.vert.co - loop2.vert.co
#            v2 = loop3.vert.co - loop2.vert.co
#            angle = v1.angle(v2, 0.0)
#            if angle >= self.ANGLE_THRESHOLD:
#                # loop1とloop3を持つ面を探す
#                for link_tri in face_tris_dict[loop1.face]:
#                    if link_tri != tri:
#                        if loop1 in link_tri and loop3 in link_tri:
#                            break
#                else:
#                    link_tri = None
#                if link_tri:
#                    loop4 = link_tri[link_tri.index(loop1) - 1]
#                    v3 = loop4.vert.co - loop2.vert.co
#                    if v3.length > self.DIST_THRESHOLD:
#                        tri1 = LoopTri((loop1, loop2, loop4))
#                        tri2 = LoopTri((loop2, loop3, loop4))
#
#                        face_tris_dict[loop1.face].append(tri1)
#                        face_tris_dict[loop1.face].append(tri2)
#
#                        face_tris_dict[loop1.face].remove(tri)
#                        face_tris_dict[loop1.face].remove(link_tri)
#                        removed_tris.add(tri)
#                        removed_tris.add(link_tri)
#
#                        corrected_faces_num += 1
#
#        self[:] = []
#        for tris in face_tris_dict.values():
#            self.extend(tris)
#
#        if sort:
#            self.sort(key=lambda tri: tri[0].face.index)
#            for tri in self:
#                tri.sort()
#
#        return corrected_faces_num  # 確認用

    def correct(self, sort=True):
        """
        v4--v5--------v6
          /    \     
         /       \   
        v1 - v2 ---v3
        v1-v2-3がほぼ直線の時、v1-v2-v3でtriが生成される場合があるので、
        v1-v2-5, v2-v3-v5で貼り直す。
        """
        face_tris_dict = self.face_dict()
        face_areas = {efa: efa.calc_area() for efa in face_tris_dict}
        removed_tris = set()

        corrected_faces_num = 0
        for tri in self:
            if tri in removed_tris or len(tri[0].face.verts) == 3:
                continue
            elif face_areas[tri[0].face] < self.CORRECT_AREA_THRESHOLD:
                continue
            elif tri.calc_area() > self.CORRECT_AREA_THRESHOLD:
                continue
            
            loop1, loop2, loop3 = tri
            if loop1.link_loop_next == loop2:
                if loop1.link_loop_prev == loop3:
                    tri.sort(head=loop3)
                else:
                    tri.sort(head=loop1)
            elif loop2.link_loop_next == loop3:
                if loop2.link_loop_prev == loop1:
                    tri.sort(head=loop1)
                else:
                    tri.sort(head=loop2)
            elif loop3.link_loop_next == loop1:
                if loop3.link_loop_prev == loop2:
                    tri.sort(head=loop2)
                else:
                    tri.sort(head=loop3)
            else:
                # 修正が必要な構造ではない
                continue
            
            loop1, loop2, loop3 = tri
            v1 = loop1.vert.co
            v2 = loop2.vert.co
            v3 = loop3.vert.co
            
            if loop2.link_loop_next == loop3:
                # v----v---------v
                #  \            /
                #  v1 -- v2 -- v3
                loop_pair = (loop1, loop3)
                correct_type = 0
            else:
                #   v--------v
                #  /          \
                # v3      v1---v2
                #  \     /
                #   v---v
                d = (v2 - v1).dot(v3 - v1)
                if d < 0:  # v3がv2の反対側
                    loop_pair = (loop3, loop2)
                    correct_type = 1
                else:  # v3がv2側
                    loop_pair = (loop1, loop3)
                    correct_type = 2
            
            l1, l2 = loop_pair
            for link_tri in face_tris_dict[l1.face]:
                if link_tri != tri:
                    if l1 in link_tri and l2 in link_tri:
                        break
            else:
                link_tri = None

            if link_tri:
                loop4 = link_tri[link_tri.index(l1) - 1]
                if correct_type in (0, 2):
                    tri1 = LoopTri((loop1, loop2, loop4))
                    tri2 = LoopTri((loop2, loop3, loop4))
                elif correct_type == 1:
                    tri1 = LoopTri((loop1, loop2, loop4))
                    tri2 = LoopTri((loop3, loop1, loop4))
                face_tris_dict[loop1.face].append(tri1)
                face_tris_dict[loop1.face].append(tri2)

                face_tris_dict[loop1.face].remove(tri)
                face_tris_dict[loop1.face].remove(link_tri)
                removed_tris.add(tri)
                removed_tris.add(link_tri)

                corrected_faces_num += 1

        self[:] = []
        for tris in face_tris_dict.values():
            self.extend(tris)

        if sort:
            self.sort(key=lambda tri: tri[0].face.index)
            for tri in self:
                tri.sort()

        return corrected_faces_num  # 確認用

    # Generator: list of LoopTri of Face Corner -------------------------------
    def tris_of_face_ccw(self, face, face_dict=None):
        """
        ジェネレータ。BMFaceに属するLoopTriを頂点毎に順番にリストで返す。
        LoopTriの要素はその都度並び替える。
        
        e.g.
        
        0-3   1st [LoopTri:(0, 2, 3), LoopTri:(0, 1, 2))]
        |\|   2nd [LoopTri:(1, 2, 0)]
        1-2   3rd [LoopTri:(2, 0, 1), LoopTri:(2, 3, 0)]
              4th [LoopTri:(3, 0, 2)]
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

    def tris_of_loops(self, face_dict=None):
        if face_dict is None:
            face_dict = self.face_dict()
        faces = sorted(face_dict.keys(), key=lambda face: face.index)
        for face in faces:
            for tris in self.tris_of_face_ccw(face, face_dict):
                yield tris

#    # Generator: LoopTri around BMVert ----------------------------------------
#    def tris_of_vert_ccw(self):
#        pass

    # Loop Tangent ------------------------------------------------------------
    @classmethod
    def calc_vert_tangent(cls, vert, vert_prev, vert_next, looptris,
                          fallback=Vector((0, 0, 0)),
                          threshold=1e-6):
        """
        vertと接続するvert_prevとvert_nextが有り、その間にlooptrisが貼られている。
        vert-vert_prevをe1、vert-vert_nextをe2とする場合、
        e1とe2の二等分線上で、looptris上に有るような相対ベクトルを求める。
        なおe1,e2との距離が1.0になるようにベクトルの長さは調節してある。
        """
        
        no_copy = not isinstance(fallback, Vector)
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
                tri.sort(head=vert)
                v1 = tri[1].vert.co
                v2 = tri[2].vert.co
                if (v1 - v2).length > 0.0:
                    if plane.distance(v1) * plane.distance(v2) <= 0.0:
                        v_inter = plane.intersect(v1, v2)
                        if v_inter:
                            v = (v_inter - co).normalized()
                            # 長さ調整
                            if v.length > threshold:
                                a1 = v.angle(co_prev - co)
                                a2 = v.angle(co_next - co)
                                f = abs(math.sin((a1 + a2) / 2))
                                if f != 0:
                                    v /= f
                                return v
        return fallback if no_copy else fallback.copy()

    def loop_tangents(self, fallback=Vector((0, 0, 0))):
        loop_dict = self.loop_dict()
        tangents = {}
        for loop in self.loops:
            vert = loop.vert
            vert_prev = loop.link_loop_prev.vert
            vert_next = loop.link_loop_next.vert
            tangents[loop] = self.calc_vert_tangent(vert, vert_prev, vert_next,
                                                    loop_dict[loop], fallback)
        return tangents

    # Normal -----------------------------------------------------------------
    @classmethod
    def calc_vert_normal(self, vert, looptris, fallback=Vector((0, 0, 0))):
        normal = Vector()
        num = 0
        for tri in looptris:
            normal += geom.normal(*[loop.vert.co for loop in tri])
            num += 1
        return normal / num

    def loop_normals(self, fallback=Vector((0, 0, 0))):
        loop_dict = self.loop_dict()
        normals = {}
        for loop in self.loops:
            normals[loop] = self.calc_vert_normal(loop.vert, loop_dict[loop],
                                                  fallback)
        return normals

    # Dict --------------------------------------------------------------------
    def vert_dict(self):
        d = defaultdict(list)
        for tri in self:
            for loop in tri:
                d[loop.vert].append(tri)
        return d

    def face_dict(self):
        d = defaultdict(list)
        for tri in self:
            d[tri[0].face].append(tri)
        return d

    def loop_dict(self):
        d = defaultdict(list)
        for tri in self:
            for loop in tri:
                d[loop].append(tri)
        return d

    def edge_dict(self):
        # keyはBMEdge
        d = defaultdict(list)
        for tri in self:
            for i in range(3):
                loop = tri[i - 1]
                if loop.link_loop_next == tri[i]:
                    d[loop.edge].append(tri)
        return d

    def vert_pair_dict(self):
        # keyは(BMVert, BMVert)
        d = defaultdict(list)
        for tri in self:
            for i in range(3):
                key = self.hash_sorted((tri[i].vert, tri[i - 1].vert))
                d[key].append(tri)
        return d

    def loop_pair_dict(self):
        d = defaultdict(list)
        for tri in self:
            for i in range(3):
                key = self.hash_sorted((tri[i], tri[i - 1]))
                d[key].append(tri)
        return d

    # verts, edges, faces, loops ----------------------------------------------
    """
    LoopTrisから各要素を抜き出してリストにして返す
    """
    def _verts_get(self):
        ls = list(set(chain(*((loop.vert for loop in tri) for tri in self))))
        ls.sort(key=lambda v: v.index)
        return ls
    verts = property(_verts_get)

    def _edges_get(self):
        ls = list(set(chain(*((loop.edge for loop in tri) for tri in self))))
        ls.sort(key=lambda e: e.index)
        return ls
    edges = property(_edges_get)

    def _faces_get(self):
        ls = list(set(chain(*((loop.face for loop in tri) for tri in self))))
        ls.sort(key=lambda f: f.index)
        return ls
    faces = property(_faces_get)

    def _loops_get(self):
        ls = list(set(chain(*((loop for loop in tri) for tri in self))))
        ls.sort(key=lambda l: l.index)
        return ls
    loops = property(_loops_get)


#==============================================================================
# Calc Tangent
#==============================================================================
def calc_loop_tangent_vector(co_prev, co, co_next, tris):
    """
    calc_loop_tangent()と違い、Vectorを受け取る。
    return: Vector
            BMLoop.calc_tangent()と違い、面を三角形に分割して、ベクトルがその面上に来る
            Noneは返さない
    """

    # co_prev -[v_prev]-> co -[v_next]-> co_next
    v_prev = (co - co_prev).normalized()
    v_next = (co_next - co).normalized()

    # 頂点座標が同じ場合
    if v_prev.length == 0.0:
        if v_next.length == 0.0:
            return Vector((0, 0, 0))
        else:
            return v_next
    elif v_next.length == 0.0:
        return -v_prev
    if -v_prev == v_next:  # co_prev - co - co_next の成す角度が0
        return v_next

    # 平面生成
    no = (v_prev + v_next).normalized()
    plane = vam.PlaneVector(co, no)
    for tri in tris:
        for i, loop_co in enumerate(tri):
            if loop_co == co:
                break
        v1 = tri[i - 1]
        v2 = tri[i - 2]
        if plane.distance(v1) * plane.distance(v2) <= 0.0:
            v_inter = plane.intersect(v1, v2)
            if v_inter:
                return (v_inter - co).normalized()

    return Vector((0, 0, 0))


def calc_loop_tangent(vert_prev, vert, vert_next, tris,
                      vert_coords:'dict. {BMVert: co}'=None):
    """
    vertからvert_prevとvert_nextが伸びていて、その間はtrisで繋がっている事。
    vert_coordsが渡されたらその座標を参照する。
    return: Vector
            BMLoop.calc_tangent()と違い、面を三角形に分割して、ベクトルがその面上に来る
            Noneは返さない
    """
    if vert_coords:
        co_prev = vert_coords[vert_prev]
        co = vert_coords[vert]
        co_next = vert_coords[vert_next]
    else:
        co_prev = vert_prev.co
        co = vert.co
        co_next = vert_next.co

    # co_prev -[v_prev]-> co -[v_next]-> co_next
    v_prev = (co - co_prev).normalized()
    v_next = (co_next - co).normalized()

    # 頂点座標が同じ場合
    if v_prev.length == 0.0:
        if v_next.length == 0.0:
            return Vector((0, 0, 0))
        else:
            return v_next
    elif v_next.length == 0.0:
        return -v_prev
    if -v_prev == v_next:  # co_prev - co - co_next の成す角度が0
        return v_next

    # 平面生成
    no = (v_prev + v_next).normalized()
    plane = vam.PlaneVector(co, no)
    """print(vert.index, plane.location, plane.normal)
    for i, tri in enumerate(tris):
        print(tri[0].vert.index, tri[1].vert.index, tri[2].vert.index)
    """
    for tri in tris:
        for index, loop in enumerate(tri):
            if loop.vert == vert:
                break
        else:
            index = None
        for i in range(3):
            if index is None or index == i:
                if vert_coords:
                    v1 = vert_coords[tri[index - 1].vert]
                    v2 = vert_coords[tri[index - 2].vert]
                else:
                    v1 = tri[index - 1].vert.co
                    v2 = tri[index - 2].vert.co
                if (v1 - v2).length > 0.0:
                    if index is None:
                        if (co - v1).length == 0.0 or (co - v2).length == 0.0:
                            continue
                    if plane.distance(v1) * plane.distance(v2) <= 0.0:
                        v_inter = plane.intersect(v1, v2)
                        if v_inter:
                            return (v_inter - co).normalized()
    return Vector((0, 0, 0))


def calc_loop_tangents(bm, looptris=None):
    """
    return: dict {BMLoop: Vector}
            BMLoop.calc_tangent()と違い、面を三角形に分割して、ベクトルがその面上に来る
    """
    if looptris is None:
        looptris = bm.calc_tessellation()

    looptris_dict = defaultdict(list)
    for tri in looptris:
        for i in range(3):
            looptris_dict[tri[i]].append(tri)

    tangents = {}
    for efa in bm.faces:
        for loop in efa.loops:
            tris = looptris_dict[loop]
            vert_prev = loop.link_loop_prev.vert
            vert = loop.vert
            vert_next = loop.link_loop_next.vert
            v = calc_loop_tangent(vert_prev, vert, vert_next, tris)
            tangents[loop] = v
    return tangents


#==============================================================================
# Apply Modifiers
#==============================================================================
object_modifier_types = {
    'UV_PROJECT', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_MIX',
    'VERTEX_WEIGHT_PROXIMITY', 'ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD',
    'DECIMATE', 'EDGE_SPLIT', 'MASK', 'MIRROR', 'MULTIRES', 'REMESH', 'SCREW',
    'SOLIDIFY', 'SUBSURF', 'ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK',
    'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH', 'WARP',
    'WAVE', 'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'EXPLODE',
    'FLUID_SIMULATION', 'OCEAN', 'PARTICLE_INSTANCE', 'PARTICLE_SYSTEM',
    'SMOKE', 'SOFT_BODY', 'SURFACE'}


@CheckArgs.checkargs(modifier_types=(None, set, object_modifier_types,
                                     '{} or {} and {}'),
                     settings=['PREVIEW', 'RENDER'])
def from_object(ob, apply_modifiers=True, settings='PREVIEW',
                modifier_types=None, layer_name='original',
                add_verts_layers=True, add_edges_layers=False,
                add_faces_layers=False):
    """対象のObjectがEditModeでも正常に動作する"""
    if ob.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(ob.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(ob.data)

    # カスタムレイヤの追加先
    def layer_add_to(bm):
        ls = []
        if add_verts_layers:
            ls.append(bm.verts)
        if add_edges_layers:
            ls.append(bm.edges)
        if add_faces_layers:
            ls.append(bm.faces)
        return ls

    for elem_seq in layer_add_to(bm):
        layer = elem_seq.layers.int.new(layer_name)
        for i, elem in enumerate(elem_seq):
            elem[layer] = i + 1

    mesh = bpy.data.meshes.new("tmp")
    bm.to_mesh(mesh)

    if ob.mode == 'EDIT':
        for elem_seq in layer_add_to(bm):
            layer = elem_seq.layers.int[layer_name]
            elem_seq.layers.int.remove(layer)

    obj = ob.copy()
    obj.data = mesh
    if apply_modifiers and modifier_types is not None:
        for mod in obj.modifiers:
            if mod.type not in modifier_types:
                mod.show_viewport = False

    dmesh = obj.to_mesh(bpy.context.scene, apply_modifiers, settings)
    bm = bmesh.new()
    bm.from_mesh(dmesh)

    for elem_seq in layer_add_to(bm):
        layer = elem_seq.layers.int[layer_name]
        for elem in elem_seq:
            elem[layer] -= 1

    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    bpy.data.meshes.remove(dmesh)

    return bm


#==============================================================================
# Face Angle
#==============================================================================
# def tri_angles(vectors):
#     """三角形の各頂点の角度を求める"""
#     angles = []
#     for i in range(3):
#         vp = vectors[i - 1]
#         v0 = vectors[i]
#         if i == 2:
#             vn = vectors[0]
#         else:
#             vn = vectors[i + 1]
#         v1 = vp - v0
#         v2 = vn - v0
#         angle = v1.angle(v2, 0.0)  # apiに変更があった。 angle(other, fallback)
#         angles.append(angle)
#     return angles
#
# def quad_angles(vectors):
#     """四角形の各頂点の角度を求める
#     対角の距離が小さい方で分割
#     """
#     angles = []
#     for i in range(4):
#         pass
#     return angles


#==============================================================================
# Duplicate
#==============================================================================

def duplicate_elements(context, verts=(), edges=(), faces=(),
                       normal_update=False, redraw=False):
    """
    頂点、辺、面を複製。
    context:       bpy.types.Context
    verts:         list of bmesh.types.BMVert
    edges:         list of bmesh.types.BMEdge
    faces:         list of bmesh.types.BMFace
    normal_update: bool. 法線を再計算する。
    redraw:        bool. 全Areaを再描画。
    
    return:        (old_new, new_old)
    """

    if context.mode != 'EDIT_MESH':
        return None

    bm = bmesh.from_edit_mesh(context.active_object.data)
    vnum = len(bm.verts)
    enum = len(bm.edges)
    fnum = len(bm.faces)

    old_new = OrderedDict()
    new_old = OrderedDict()

    # Disable flags
    for v in bm.verts:
        v.tag = False
    for e in bm.edges:
        e.tag = False
    for f in bm.faces:
        f.tag = False

    # Enable flags
    for f in faces:
        f.tag = True
        for e in f.edges:
            e.tag = True
        for v in f.verts:
            v.tag = True
    for e in edges:
        e.tag = True
        for v in e.verts:
            v.tag = True
    for v in verts:
        v.tag = True

    # 頂点複製
    dupliverts = (v for v in bm.verts[:vnum] if v.tag)
    for v in dupliverts:
        new_vert = bm.verts.new(v.co, v)
        old_new[v] = new_vert
        new_old[new_vert] = v
    # 辺複製
    dupliedges = (e for e in bm.edges[:enum] if e.tag)
    for e in dupliedges:
        v1 = old_new[e.verts[0]]
        v2 = old_new[e.verts[1]]
        new_edge = bm.edges.new((v1, v2), e)
        old_new[e] = new_edge
        new_old[new_edge] = e
    # 面複製
    duplifaces = (f for f in bm.faces[:fnum] if f.tag)
    for f in duplifaces:
        verts = [old_new[v] for v in f.verts]
        new_face = bm.faces.new(verts, f)
        old_new[f] = new_face
        new_old[new_face] = f

    # 法線再計算
    if normal_update:
        bm.normal_update()

    # 全Areaの再描画
    if redraw:
        for wm in bpy.data.window_managers:
            for win in wm.windows:
                for area in win.screen.areas:
                    area.tag_redraw()

    return old_new, new_old


#==============================================================================
# Snap
#==============================================================================
# def snap(context, event):
#     if context.mode != 'EDIT_MESH':
#         return None
#     actob = context.active_object
#     mat = actob.matrix_world
#     imat = mat.inverted()
#     bm = bmesh.from_edit_mesh(actob.data)
#
#     vflags = [v.select for v in bm.verts]
#     eflags = [e.select for e in bm.edges]
#     fflags = [f.select for f in bm.faces]
#     for v in bm.verts:
#         v.select = False
#     for e in bm.edges:
#         e.select = False
#     for f in bm.faces:
#         f.select = False
#
#     mco = Vector((event.mouse_region_x, event.mouse_region_y, 0))
#     co = vav.unproject(context.region, context.region_data, mco)
#
#     tmp_vert = bm.verts.new(imat * co)
#     tmp_vert.select = True
#     tmp_vert.hide = False
#     print(0, tmp_vert.co)
#     bpy.ops.transform.translate(
#                                 snap=True, snap_target='CLOSEST',
#                                 )#, snap_normal=(0.0, 0.0, 0.0))
#     print(1, tmp_vert.co)
#     for v, flag in zip(bm.verts, vflags):
#         v.select = flag
#     for e, flag in zip(bm.edges, eflags):
#         e.select = flag
#     for f, flag in zip(bm.faces, fflags):
#         f.select = flag
#
#     context.scene.cursor_location = mat * tmp_vert.co
#
#     bm.verts.remove(tmp_vert)


#==============================================================================
# Test
#==============================================================================
# def quads_convert_to_tris(context, offset=(0, 0, 0)):
#     """
#     選択要素を複製後、三角ポリゴンに分割。
#     """
#
#     if context.mode != 'EDIT_MESH':
#         return None
#
#     bm = bmesh.from_edit_mesh(context.active_object.data)
#     vnum = len(bm.verts)
#     enum = len(bm.edges)
#     fnum = len(bm.faces)
#     ofs = Vector(offset)
#     new_verts = []
#     new_edges = []
#     new_faces = []
#     old_and_new_connection = {}
#
#     #bm.select_flush_mode()
#
#     # 頂点複製
#     for eve in bm.verts[:vnum]:
#         if eve.select and not eve.hide:
#             new_vert = bm.verts.new(eve.co + ofs, eve)
#             new_verts.append(new_vert)
#             old_and_new_connection[new_vert] = eve
#             old_and_new_connection[eve] = new_vert
#     # 辺複製
#     for eed in bm.edges[:enum]:
#         if eed.select and not eed.hide:
#             v1 = old_and_new_connection[eed.verts[0]]
#             v2 = old_and_new_connection[eed.verts[1]]
#             new_edge = bm.edges.new((v1, v2), eed)
#             new_edges.append(new_edge)
#             old_and_new_connection[new_edge] = eed
#             old_and_new_connection[eed] = new_edge
#     # 面複製
#     for efa in bm.faces[:fnum]:
#         if efa.select and not efa.hide:
#             verts = [old_and_new_connection[eve] for eve in efa.verts]
#             new_face = bm.faces.new(verts, efa)
#             new_faces.append(new_face)
#             old_and_new_connection[new_face] = efa
#             old_and_new_connection[efa] = new_face
#
#     # 元の要素を非選択にする
#     select_flags = {}
#     select_flags.update({eve: eve.select for eve in bm.verts})
#     select_flags.update({eed: eed.select for eed in bm.edges})
#     select_flags.update({efa: efa.select for efa in bm.faces})
#     for eve in (eve for eve in bm.verts[:vnum] if not eve.hide):
#         eve.select = False
#     for eed in (eed for eed in bm.edges[:enum] if not eed.hide):
#         eed.select = False
#     for efa in (efa for efa in bm.faces[:fnum] if not efa.hide):
#         efa.select = False
#
#     # 三角ポリゴンに分割
#     bpy.ops.mesh.quads_convert_to_tris()
#
#     # 法線再計算
#     bm.normal_update()
#
#     # 全Areaの再描画
#     for wm in bpy.data.window_managers:
#         for win in wm.windows:
#             for area in win.screen.areas:
#                 area.tag_redraw()
#
#     return (new_verts, new_edges, new_faces,
#             old_and_new_connection, select_flags)

