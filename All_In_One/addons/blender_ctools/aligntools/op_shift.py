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
import itertools

import bpy
from mathutils import Matrix, Vector
import mathutils.geometry as geom
import bmesh

from .va import vaprops as vap
from .va import vamath as vam
from .va import vabmesh as vabm
from .va import vaoperator as vaop
from .va import modalmouse
from .va.looptris import LoopTris

from . import tooldata

tool_data = tooldata.tool_data
memoize = tool_data.memoize


EPS = 1e-5


###############################################################################
# BMesh: Shift (Shift Outline & Solidify)
###############################################################################
class OperatorShift(vaop.OperatorTemplate, bpy.types.Operator):
    bl_idname = 'at.shift'
    bl_label = 'Shift'
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING', 'GRAB_CURSOR'}
    p = bpy.types.Operator.bl_rna.properties['bl_options']

    # --- Shift Outline ---
    offset_tangent = vap.FP('Tangent Offset', options={'SKIP_SAVE'}, step=1)
    use_even_offset_tangent = vap.BP(
        'Offset Even', 'Scale the offset to give more even thickness',
        default=True)
    tangent_calculation = vap.EP(
        'Tangent Calculation',
        items=(('selected', 'Selected', ''),
               ('deselected', 'Deselected', ''),
               ('individual', 'Individual',
                'Used for extrude individual')),
        default='selected')
    align_edges = vap.BP('Align Edges', default=False)
    align_edges_position = vap.FP(
        'Align Edges Factor', min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        default=0.5, subtype='FACTOR')

    # --- Solidify ---
    offset_normal = vap.FP('Normal Offset', options={'SKIP_SAVE'}, step=1)
    use_even_offset_normal = vap.BP(
        'Offset Even', 'Scale the offset to give more even thickness',
        default=True)
    normal_calculation = vap.EP(
        'Normal Calculation',
        items=(('all', 'All', ''),
               ('selected', 'Selected', ''),
               ('deselected', 'Deselected', ''),
               ('individual', 'Individual',
                'Used for extrude individual')),
        default='selected')
    tri_angle_threshold = vap.FP(
        'Tri Angle Threshold', '三角形同士の角度がこれ以下なら平面と見做す',
        default=math.radians(0.1), min=0.0, precision=6, subtype='ANGLE')

    intersect_angle_threshold = math.radians(0.1)  # 固定でいいはず

    # --- Common ---
    use_world_coords = vap.BP('Use World Coordinates', default=False)
    extrude = vap.EP(
        'Extrude',
        items=(('none', 'None', ''),
               ('extrude', 'Extrude', ''),
               ('individual', 'Individual', 'Extrude individual'),),
        default='none')
    extrude_move_original = vap.BP(
        'Move Original Verts', "Used for 'extrude' and 'individual'",
        default=False)
    use_mirror_modifiers = vap.BP('Use Mirror Modifiers', default=True)

    mode = vap.EP('Mode',
                  items=(('tangent', 'Tangent', ''),
                         ('normal', 'Normal', ''),
                         ('none', 'None', '')),
                  default='none',
                  options={'HIDDEN'})

    cursor_to_center = vap.BP(
        'Cursor to Center', 'Set cursor position at region center',
        default=False, options={'SKIP_SAVE'})

    WIRE = 1
    BORDER = 1 << 1  # WIREとBORDERのフラグが両方立つことはない

    def __init__(self):
        super().__init__()

        # init()を一度でも呼ぶと真になる
        self.init_called = [False, False]  # [local, world]

        # LoopTris
        self._loop_tris = LoopTris([])
        self._loop_tris_world = LoopTris([])

        # 編集中のbmeshの頂点インデックスから、modifier適用後のbmeshの頂点を
        # 参照する
        # self.derived_vert_from_original_index = {}
        # self.derived_face_from_original_index = {}
        # self.WIRE, self.BORDEのフラグ
        # self.vflags = {}
        # self.eflags = {}

    @property
    def loop_tris(self):
        if self.use_world_coords:
            return self._loop_tris_world
        else:
            return self._loop_tris

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def init(self, context):
        if self.use_world_coords:
            if self.init_called[1]:
                return
        else:
            if self.init_called[0]:
                return

        bm = vabm.from_object(
            context.active_object,
            apply_modifiers=self.use_mirror_modifiers,
            settings='PREVIEW',
            modifier_types={'MIRROR'},
            layer_name='original',
            add_faces_layers=True)
        vabm.LoopTris.index_update(bm)
        if self.use_world_coords:
            bm.transform(context.active_object.matrix_world)
            bm.normal_update()  # 必要か？

        # LoopTris。要素の変更は無いのでキャッシュを有効にする
        loop_tris = LoopTris(bm)
        loop_tris.bm = bm
        loop_tris.vert_verts = vabm.vert_verts_dict(bm)
        memo = loop_tris.memoize
        memo.read = memo.write = True
        loop_tris.correct()

        # 編集中のbmeshの頂点インデックスから、modifier適用後のbmeshの頂点を
        # 参照する
        # vert用
        loop_tris.derived_vert_from_original_index = d = {}
        layer = bm.verts.layers.int['original']
        indices = set()
        for eve in bm.verts:
            i = eve[layer]
            if i != -1 and i not in indices:
                d[i] = eve
                indices.add(i)
        # face用
        loop_tris.derived_face_from_original_index = d = {}
        layer = bm.faces.layers.int['original']
        indices = set()
        for efa in bm.faces:
            i = efa[layer]
            if i != -1 and i not in indices:
                d[i] = efa
                indices.add(i)

        # --- Shift Outline ---
        loop_tris.eflags = eflags = {}
        for eed in bm.edges:
            flag = 0
            selected = deselected = 0
            for efa in eed.link_faces:
                if not efa.hide:
                    if efa.select:
                        selected += 1
                    else:
                        deselected += 1
            if eed.select and not eed.hide:
                if selected == 0 and deselected <= 2:
                    flag = self.WIRE
                elif selected == 1 and deselected <= 1:
                    flag = self.BORDER
            eflags[eed] = flag

        loop_tris.vflags = vflags = {}
        for eve in bm.verts:
            flag = 0
            wire_num = border_num = 0
            for eed in eve.link_edges:
                f = eflags[eed]
                if f & self.WIRE:
                    wire_num += 1
                elif f & self.BORDER:
                    border_num += 1
            if 1 <= wire_num <= 2 and border_num == 0:
                flag = self.WIRE
            elif wire_num == 0 and border_num == 2:
                flag = self.BORDER
            vflags[eve] = flag

        # --- Solidify ---
        # 頂点のhideとtriの面積により、法線計算に使えるか否かのフラグを付ける
        for eve in bm.verts:
            eve.tag = not eve.hide
        for tri in loop_tris:
            tri.tag = not tri[0].face.hide and tri.area > EPS

        if self.use_world_coords:
            self.init_called[1] = True
            self._loop_tris_world = loop_tris
        else:
            self._loop_tris = loop_tris
            self.init_called[0] = True

    def calc_loop_tangents(self):
        """self.dbmの選択中の面に属するloopのtangentを計算。
        self.extrudeが'individual'の場合に用いる。
        :rtype: dict[BMLoop, Vector]
        """
        loop_tris = self.loop_tris
        loop_tangents = loop_tris.loop_tangents()
        tangents = {}
        for efa in loop_tris.bm.faces:
            if efa.select:
                for loop in efa.loops:
                    tangents[loop] = loop_tangents[loop]
        return tangents

    def calc_vert_tangents(self):
        """self.loop_tris.bmのBORDERフラグが立っている頂点のtangentを計算。
        :return: キーがBMVert, 値が[tangent, tangent(min), tangent(max)]の
            辞書を返す。tangentはself.align_edgesが偽の場合に、tangent(min)と
            tangent(max)はself.align_edgesが真の場合に利用する。
            fallbackはVector((0, 0, 0))とする。
        :rtype: dict[BMVert, list[Vector]]
        """
        WIRE = self.WIRE
        BORDER = self.BORDER

        loop_tris = self.loop_tris
        vert_dict = loop_tris.vert_dict()

        vert_tangents = {}  # eve: Vector

        for eve in loop_tris.bm.verts:
            if not loop_tris.vflags[eve] & BORDER:
                continue

            # eveに接続する二頂点(vert_next, vert_prev)を求める
            eve_next, eve_prev = [eed.other_vert(eve) for eed in eve.link_edges
                                  if loop_tris.eflags[eed] & BORDER]

            # tangent (used when self.align_edges is False)
            tris = []
            for tri in vert_dict[eve]:
                efa = tri[0].face
                if not efa.hide:
                    # if not self.use_outside_calculation and efa.select or \
                    #    self.use_outside_calculation and not efa.select:
                    #     tris.append(tri)
                    if self.tangent_calculation in ('selected', 'individual') and efa.select or \
                       self.tangent_calculation == 'deselected' and not efa.select:
                        tris.append(tri)
            tangent = LoopTris.vert_tangent(
                eve, eve_prev, eve_next, tris, fallback=Vector((0, 0, 0)))

            # tangent_min, tangent_max (used when self.align_edges is True)
            edges = []
            for eed in eve.link_edges:
                if eed.hide or loop_tris.eflags[eed] & (WIRE | BORDER):
                    continue
                # if not self.use_outside_calculation and eed.select or \
                #    self.use_outside_calculation and not eed.select:
                #     edges.append(eed)
                if self.tangent_calculation in ('selected', 'individual') and eed.select or \
                   self.tangent_calculation == 'deselected' and not eed.select:
                    edges.append(eed)
            tangent_min_max = []
            if len(edges) == 1:
                eed = edges[0]
                vec = eed.other_vert(eve).co - eve.co
                if vec.length > 0:
                    vec.normalize()
                    vec1 = eve_prev.co - eve.co
                    if vec1.length > 0:
                        vec1.normalize()
                        f1 = vec1.cross(vec).length
                        if f1 > EPS:
                            tangent_min_max.append(vec / f1)
                    vec2 = eve_next.co - eve.co
                    if vec2.length > 0:
                        vec2.normalize()
                        f2 = vec2.cross(vec).length
                        if f2 > EPS:
                            tangent_min_max.append(vec / f2)
            tangent_min_max.sort(key=lambda v: v.length)

            if len(tangent_min_max) == 0:
                tangents = [tangent] * 3
            elif len(tangent_min_max) == 1:
                tangents = [tangent] + tangent_min_max * 2
            else:
                tangents = [tangent] + tangent_min_max
            vert_tangents[eve] = tangents

        return vert_tangents

    def calc_vert_tangents_wire(self, obmat, viewmat):
        """self.loop_tris.bmのWIREフラグが立っている頂点のtangentを計算。
        """
        WIRE = self.WIRE
        loop_tris = self.loop_tris

        vert_tangents = {}  # eve: Vector

        if viewmat:
            obmat3 = obmat.to_3x3()
            vmat3 = viewmat.to_3x3()
        else:
            obmat3 = Matrix.Identity(3)
            vmat3 = Matrix.Identity(3)

        edges = [eed for eed in loop_tris.bm.edges
                 if loop_tris.eflags[eed] & WIRE]
        paths = vabm.make_paths_from_edges(edges=edges)
        for path in paths:
            verts = path[:]
            if verts[0] == verts[-1]:
                verts = verts[:-1]
            vecs = [v.co for v in verts]

            bbmat, bbscale = vam.get_obb(vecs)
            bbmat3 = bbmat.to_3x3()

            # 点
            if bbscale[0] < EPS:
                pass

            # 直線。tangentの方向はview_matrixに依存
            elif bbscale[1] < EPS:
                axis = vmat3 * obmat3 * bbmat3.col[0]
                axis.normalize()
                ax = Vector((-axis[1], axis[0], 0))
                vec = obmat3.inverted() * (vmat3.inverted() * ax)
                vec.normalize()
                # vec: 画面と平行でpathと垂直なベクトル
                for eve in verts:
                    if loop_tris.vflags[eve] & WIRE:
                        vert_tangents[eve] = [vec.copy() for i in range(3)]
            else:
                # 平面、立体
                imat3 = bbmat3.inverted()
                vecs2d = [(imat3 * v).to_2d() for v in vecs]  # obb座標
                # しばらくVectorを2Dで処理
                tangents = []  # 内側のベクトル。最初は左回りを想定した計算を行う
                angles = []  # vec1からvec2への差。合計が負なら右回り
                rmat = Matrix.Rotation(math.pi / 2, 2)
                for i in range(len(vecs2d)):
                    # .______________.______________.
                    # v  -(vec1)->  vec  -(vec2)->  v
                    vec = vecs2d[i]
                    vec1 = vec - vecs2d[i - 1]
                    vec2 = vecs2d[(i + 1) % len(vecs2d)] - vec

                    # 先頭・末尾
                    if not path.cyclic and (i == 0 or i == len(vecs2d) - 1):
                        if i == 0 and vec2.length > 0.0:
                            tangents.append(rmat * vec2.normalized())
                        elif i == len(vecs2d) - 1 and vec1.length > 0.0:
                            tangents.append(rmat * vec1.normalized())
                        else:
                            tangents.append(Vector((0, 0)))
                        angles.append(0.0)

                    # 他
                    else:
                        if vec1.length > 0.0 or vec2.length > 0.0:
                            if vec1.length > 0.0:
                                vec1.normalize()
                            if vec2.length > 0.0:
                                vec2.normalize()
                            if vec1.length > 0.0 and vec2.length > 0.0:
                                v = (rmat * ((vec1 + vec2) / 2)).normalized()
                                f = abs(vam.cross2d(vec2, v))
                                if f > EPS:
                                    tangents.append(v / f)
                                else:
                                    tangents.append(Vector((0, 0)))
                                f = vam.cross2d(vec1, vec2)
                                f = max(-1.0, min(f, 1.0))
                                angles.append(math.asin(f))
                            else:
                                if vec1.length > 0.0:
                                    v = (rmat * vec1).normalized()
                                else:
                                    v = (rmat * vec2).normalized()
                                f = abs(vam.cross2d(vec2, v))
                                if f > EPS:
                                    tangents.append(v / f)
                                else:
                                    tangents.append(Vector((0, 0)))
                                angles.append(0.0)
                        else:
                            tangents.append(Vector((0, 0)))
                            angles.append(0.0)

                # エッジが右回りだったならベクトルを反転する
                if sum(angles) < 0.0:
                    for v in tangents:
                        v.negate()

                for eve, vec in zip(verts, tangents):
                    if loop_tris.vflags[eve] & WIRE:
                        v = bbmat3 * vec.to_3d()
                        vert_tangents[eve] = [v.copy() for i in range(3)]
        return vert_tangents

    def calc_loop_normals(self):
        loop_tris = self.loop_tris
        face_dict = loop_tris.face_dict()
        loop_normals = {}
        for efa in loop_tris.bm.faces:
            if not efa.select:
                continue
            for tris in loop_tris.tris_of_face_ccw(efa, face_dict):
                normals = []
                for tri in tris:
                    normals.append(tri.normal)
                normal = sum(normals, Vector()) / len(normals)
                loop_normals[tris[0][0]] = normal
        return loop_normals

    def calc_vert_normals(self):
        """eve.selectとeve.tagが真の頂点だけ計算する"""
        loop_tris = self.loop_tris
        vert_pair_dict = loop_tris.vert_pair_dict()
        vert_normals = {}
        for eve in loop_tris.bm.verts:
            if not eve.select or not eve.tag:
                continue
            edge_normals = {}
            edge_normals_all = {}
            for eve_other in loop_tris.vert_verts[eve]:
                # other_vert
                #     \          / edge_normal
                #      \  tri   /
                # tri  eve ------- other_vert
                #      /
                #     /    tri
                # other_vert
                #
                tris = []
                vert_pair = (eve, eve_other)
                key = loop_tris.hash_sorted(vert_pair)
                for tri in vert_pair_dict[key]:
                    if tri.tag:
                        if self.normal_calculation in ('all', 'deselected'):
                            tris.append(tri)
                        else:
                            if tri[0].face.select:
                                tris.append(tri)

                if len(tris) == 1:
                    if self.normal_calculation != 'deselected':
                        edge_normals[vert_pair] = tris[0].normal
                    edge_normals_all[vert_pair] = tris[0].normal
                elif len(tris) == 2:
                    n1 = tris[0].normal
                    n2 = tris[1].normal
                    normal = (n1 + n2).normalized()
                    angle = n1.angle(n2)
                    # x * cos(angle / 2) = 1.0
                    f = math.cos(angle / 2)
                    if f != 0.0:
                        normal /= f
                    if angle > self.tri_angle_threshold:
                        if self.normal_calculation == 'deselected':
                            if tris[0][0].face.select ^ tris[1][0].face.select:
                                # n1: sel, n2: desel
                                # deselをselに投影
                                if tris[1][0].face.select:
                                    n1, n2 = n2, n1
                                normal = (n1 - n1.project(n2)).normalized()
                                f = math.cos(n1.angle(normal))
                                if f != 0.0:
                                    normal /= f
                                edge_normals[vert_pair] = normal
                        else:
                            edge_normals[vert_pair] = normal
                    edge_normals_all[vert_pair] = normal

            normal = None

            for _ in range(2):
                if len(edge_normals) == 1:
                    normal = list(edge_normals.values())[0].copy()
                elif len(edge_normals) >= 2:
                    normals = []
                    v0 = eve.co
                    for k1, k2 in itertools.combinations(
                            edge_normals.keys(), 2):
                        #       v3 v5    v6
                        #     v4  \|_____|   |n2
                        # \n1   \ / v0   v2
                        #       v1
                        v1 = k1[1].co
                        v2 = k2[1].co
                        n1 = edge_normals[k1]
                        n2 = edge_normals[k2]
                        if (v0 - v1).angle(v2 - v0) >= \
                                self.intersect_angle_threshold:
                            v3 = v0 + n1
                            v4 = v1 + n1
                            v5 = v0 + n2
                            v6 = v2 + n2
                            i1, i2 = geom.intersect_line_line(v3, v4, v5, v6)
                            normals.append((i1 + i2) / 2 - v0)
                        else:
                            l = (n1.length + n2.length) / 2
                            normals.append((n1 + n2).normalized() * l)
                    if normals:
                        normal = Vector()
                        for v in normals:
                            normal += v
                        normal /= len(normals)
                if normal:
                    break
                else:
                    edge_normals = edge_normals_all

            if normal:
                vert_normals[eve] = normal

        return vert_normals

    def execute_tangent(self, context, bm):
        if self.offset_tangent == 0.0:
            return
        loop_tris = self.loop_tris
        mat = context.active_object.matrix_world
        imat = mat.inverted()

        offset = self.offset_tangent
        if self.tangent_calculation in ('selected', 'individual'):
            offset *= -1

        use_loop_tangents = (self.extrude == 'individual' and
                             not self.extrude_move_original and
                             self.tangent_calculation == 'individual')
        if use_loop_tangents:
            loop_tangents = self.calc_loop_tangents()
            layer_loop = bm.loops.layers.int['at_shift_outline_extrude']
            face_dict = loop_tris.derived_face_from_original_index
            for i, efa in enumerate(bm.faces):
                if efa.hide or not efa.select:
                    continue
                for j, loop in enumerate(efa.loops):
                    index = loop[layer_loop] - 1  # extrude前のfaceインデックス
                    derived_face = face_dict[index]
                    derived_loop = derived_face.loops[j]
                    if derived_loop in loop_tangents:
                        vec = loop_tangents[derived_loop]
                        if not self.use_even_offset_tangent:
                            vec = vec.normalized()
                        if self.use_world_coords:
                            v = loop.vert.co
                            loop.vert.co = imat * (mat * v + vec * offset)
                        else:
                            loop.vert.co += vec * offset

        obmat = context.active_object.matrix_world
        if context.region_data:
            vmat = context.region_data.view_matrix
        else:
            vmat = None
        vert_tangents_wire = self.calc_vert_tangents_wire(obmat, vmat)
        if not use_loop_tangents:
            vert_tangents = self.calc_vert_tangents()
        else:
            vert_tangents = {}

        layer = bm.verts.layers.int['at_shift_outline_extrude']
        for i, eve in enumerate(bm.verts):
            if eve.hide:
                continue
            if self.extrude != 'none' and self.extrude_move_original:
                if eve.select:
                    continue
            else:
                if not eve.select:
                    continue
            index = eve[layer] - 1  # extrude前のインデックス
            derived_vert = loop_tris.derived_vert_from_original_index[index]
            is_solid = derived_vert in vert_tangents
            is_wire = derived_vert in vert_tangents_wire
            if is_solid or is_wire:
                if is_solid:
                    t, tmin, tmax = vert_tangents[derived_vert]
                    ofs = offset
                else:
                    t, tmin, tmax = vert_tangents_wire[derived_vert]
                    ofs = -self.offset_tangent
                if self.align_edges:
                    vec = tmin * (1 - self.align_edges_position) + \
                          tmax * self.align_edges_position
                else:
                    vec = t
                if not self.use_even_offset_tangent:
                    vec = vec.normalized()
                if self.use_world_coords:
                    eve.co = imat * (mat * eve.co + vec * ofs)
                else:
                    eve.co += vec * ofs

    def execute_normal(self, context, bm):
        if self.offset_normal == 0.0:
            return
        loop_tris = self.loop_tris
        mat = context.active_object.matrix_world
        imat = mat.inverted()

        moved_verts = set()
        use_loop_normals = (self.extrude == 'individual' and
                            not self.extrude_move_original and
                            self.normal_calculation == 'individual')
        if use_loop_normals:
            loop_normals = self.calc_loop_normals()
            layer_loop = bm.loops.layers.int['at_shift_outline_extrude']
            for i, efa in enumerate(bm.faces):
                if efa.hide or not efa.select:
                    continue
                for j, loop in enumerate(efa.loops):
                    index = loop[layer_loop] - 1  # extrude前のfaceインデックス
                    derived_face = loop_tris.derived_face_from_original_index[index]
                    derived_loop = derived_face.loops[j]
                    if derived_loop in loop_normals:
                        vec = loop_normals[derived_loop]
                        if not self.use_even_offset_tangent:
                            vec = vec.normalized()
                        offset = self.offset_normal
                        if self.use_world_coords:
                            v = loop.vert.co
                            loop.vert.co = imat * (mat * v + vec * offset)
                        else:
                            loop.vert.co += vec * offset
                        moved_verts.add(loop.vert)

        vert_normals = self.calc_vert_normals()
        layer = bm.verts.layers.int['at_shift_outline_extrude']
        for eve in bm.verts:
            if eve in moved_verts:
                continue
            if eve.hide:
                continue
            if self.extrude != 'none' and self.extrude_move_original:
                if eve.select:
                    continue
            else:
                if not eve.select:
                    continue
            index = eve[layer] - 1  # extrude前のインデックス
            derived_vert = loop_tris.derived_vert_from_original_index[index]
            if derived_vert in vert_normals:
                normal = vert_normals[derived_vert]
                if not self.use_even_offset_normal:
                    normal = normal.normalized()
                offset = self.offset_normal
                if self.use_world_coords:
                    eve.co = imat * (mat * eve.co + normal * offset)
                else:
                    eve.co += normal * offset

    def execute(self, context):
        self.init(context)

        ob = context.active_object
        bm = bmesh.from_edit_mesh(ob.data)

        # Add Layers
        layer = bm.verts.layers.int.new('at_shift_outline_extrude')
        for i, eve in enumerate(bm.verts):
            # 完全新規の頂点の値は0になるので、それと被らないように +1
            eve[layer] = i + 1

        layer_loop = bm.loops.layers.int.new('at_shift_outline_extrude')
        for i, efa in enumerate(bm.faces):
            for loop in efa.loops:
                loop[layer_loop] = i + 1

        # Extrude
        if self.extrude == 'individual':
            # 面の選択状態を確保
            selected_faces = [i for i, f in enumerate(bm.faces)
                              if f.select]
            # 全ての面を非選択
            for efa in bm.faces:
                efa.select = False
            # 頂点・辺のみ押し出し
            bpy.ops.mesh.extrude_region(False, mirror=False)
            # 頂点・辺の選択状態を確保
            selected_verts = [i for i, v in enumerate(bm.verts)
                              if v.select]
            selected_edges = [i for i, e in enumerate(bm.edges)
                              if e.select]
            # 面再選択、押し出し
            bm.faces.ensure_lookup_table()
            for i in selected_faces:
                bm.faces[i].select = True
            bpy.ops.mesh.extrude_faces_indiv(False, mirror=False)
            # 頂点・辺を再選択
            for i in selected_verts:
                bm.verts[i].select = True
            for i in selected_edges:
                bm.edges[i].select = True
            # select_flush_mode()はしなくても大丈夫か
        elif self.extrude == 'extrude':
            bpy.ops.mesh.extrude_region(False, mirror=False)

        # Translate
        self.execute_tangent(context, bm)
        self.execute_normal(context, bm)

        # Remove Layers
        bm.verts.layers.int.remove(layer)
        bm.loops.layers.int.remove(layer_loop)

        # Update
        bm.normal_update()
        bmesh.update_edit_mesh(ob.data, True, True)
        context.area.tag_redraw()

        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        actob = context.active_object
        mat = actob.matrix_world
        bm = bmesh.from_edit_mesh(actob.data)
        bm.clear()
        bm.from_mesh(self.mesh)

        retval = self.modal_mouse.modal(context, event)

        if self.modal_mouse.orientation.orientation == 'GLOBAL':
            self.use_world_coords = True
        else:
            self.use_world_coords = False

        if retval == {'PASS_THROUGH'}:
            if event.value == 'PRESS':
                if event.type == 'E':
                    ls = ['none', 'extrude', 'individual']
                    i = ls.index(self.extrude)
                    self.extrude = ls[(i + 1) % 3]
                elif event.type == 'V':
                    if self.use_even_offset_tangent:
                        self.use_even_offset_tangent = False
                        self.use_even_offset_normal = False
                    else:
                        self.use_even_offset_tangent = True
                        self.use_even_offset_normal = True
                elif event.type == 'C':
                    ls = ['all', 'selected', 'deselected', 'individual']
                    i = ls.index(self.normal_calculation)
                    s = ls[(i + 1) % 4]
                    self.tangent_calculation = ls[1] if s == 'all' else s
                    self.normal_calculation = s

        result = self.modal_mouse.result
        translation = result['translation']
        self.offset_tangent = translation[0]
        self.offset_normal = translation[1]

        self.execute(context)

        if event.type in ('SPACE', 'RET', 'NUMPAD_ENTER', 'LEFTMOUSE'):
            self.modal_mouse.draw_handler_remove(context)
            bpy.data.meshes.remove(self.mesh)
            context.area.tag_redraw()
            return {'FINISHED'}
        elif event.type in ('ESC', 'RIGHTMOUSE'):
            self.modal_mouse.draw_handler_remove(context)
            bm.clear()
            bm.from_mesh(self.mesh)
            bm.normal_update()
            bmesh.update_edit_mesh(actob.data, True, True)
            bpy.data.meshes.remove(self.mesh)
            context.area.tag_redraw()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)

        class ShiftOpMode(modalmouse.Translation2DMode):
            orientations = [
                ['GLOBAL', 'VIEW', modalmouse.CONST.XYZ],
                [modalmouse.CONST.CURRENT, 'VIEW', modalmouse.CONST.XYZ]]

            def header_string(self, context, owner):
                op = owner.owner
                txt = ''

                t1 = 'ON' if op.use_world_coords else 'OFF'
                txt += 'WorldCoords(W): {}, '.format(t1)

                txt += 'Extrude(E): {}, '.format(op.extrude.title())

                t1 = 'ON' if op.use_even_offset_normal else 'OFF'
                t2 = 'ON' if op.use_even_offset_tangent else 'OFF'
                if t1 == t2:
                    txt += 'EvenOffset(V): {}, '.format(t1)
                else:
                    txt += 'EvenOffset(V): {}/{}, '.format(t1, t2)

                t1 = op.tangent_calculation.title()
                t2 = op.normal_calculation.title()
                if t1 == t2:
                    txt += 'Calculation(C): {}'.format(t1)
                else:
                    txt += 'Calculation(C): {}/{}'.format(t1, t2)

                return txt

        self.modal_mouse = modalmouse.ModalMouse(
            context, event, self,
            mode='TRANSLATION_2D',
            modes=(ShiftOpMode(),),
            use_normalized=False, view_location=None)
        self.modal_mouse.shortcuts = {
            'reset': 'P',
            'constraint': 'MIDDLEMOUSE',
            'orientation': 'W',
            # 'normalize': 'N',
            'x': 'X',
            'y': 'Y',
        }
        if self.mode == 'tangent':
            self.modal_mouse.const_axis = modalmouse.CONST.X
        elif self.mode == 'normal':
            self.modal_mouse.const_axis = modalmouse.CONST.Y

        if self.cursor_to_center:
            region = context.region
            wh = region.width / 2
            hh = region.height / 2
            context.window.cursor_warp(region.x + wh, region.y + hh)
            self.modal_mouse.set_origin((wh, hh))

        actob = context.active_object
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.mode_set(mode='EDIT')
        # # bmesh.update_edit_mesh(actob.data, True, True)
        # self.mesh = actob.data.copy()

        self.mesh = actob.data.copy()
        bm = bmesh.from_edit_mesh(actob.data)
        bm.to_mesh(self.mesh)

        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout

        # Shift Outline Options
        col = layout.column(align=True)
        col.label('Tangent Options:')
        box = col.box()
        self.draw_property('offset_tangent', box)
        self.draw_property('use_even_offset_tangent', box)
        self.draw_property('tangent_calculation', box)
        self.draw_property('align_edges', box)
        prop = self.draw_property('align_edges_position', box)
        prop.active = self.align_edges and self.use_even_offset_tangent

        # Solidify Options
        col = layout.column(align=True)
        col.label('Normal Options:')
        box = col.box()
        self.draw_property('offset_normal', box)
        self.draw_property('use_even_offset_normal', box)
        self.draw_property('normal_calculation', box)
        self.draw_property('tri_angle_threshold', box)

        # Common Options
        col = layout.column(align=True)
        col.label('Common Options:')
        box = col.box()
        self.draw_property('use_world_coords', box)
        self.draw_property('extrude', box)
        prop = self.draw_property('extrude_move_original', box)
        prop.active = self.extrude != 'none'
        prop = self.draw_property('use_mirror_modifiers', box)
        prop.active = False
        if context.active_object:
            for mod in context.active_object.modifiers:
                if mod.type == 'MIRROR':
                    prop.active = True

    def check(self, context):
        return True


classes = [
    OperatorShift,
]
