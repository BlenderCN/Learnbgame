'''
Copyright (C) 2018 Jean Da Costa machado.
Jean3dimensional@gmail.com

Created by Jean Da Costa machado

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bmesh
from mathutils import Vector, bvhtree, Matrix, geometry
from random import random



class HitInfo:
    def __init__(self, location, normal, face_index, distance, field):
        self.co = location
        face = field.bm.faces[face_index]
        verts = [vert.co for vert in face.verts]
        mask = [Vector((0, 0, field.mask.get(vert.index, 0))) for vert in field.bm.faces[face_index].verts]
        normals = [vert.normal for vert in field.bm.faces[face_index].verts]
        self.normal = geometry.barycentric_transform(location, *verts, *normals)
        self.mask = geometry.barycentric_transform(location, *verts, *mask).z
        try:
            co = face.verts[0]
            vec = field.vert_field[co.index].u
            vecs = [field.vert_field[vert.index].get_nearest_vec(vec) for vert in face.verts]
            vec = geometry.barycentric_transform(location, *verts, *vecs)
        except KeyError:
            vec = Vector((random(), random(), random())).cross(self.normal).normalized()
        self.frame = CrossFrame(vec, self.normal)

        self.face = face_index


class CrossFrame:
    def __init__(self, u, normal, strength=1.):
        if u.dot(normal) == 1 or u.length_squared == 0:
            u = normal.orthogonal()
        self.strength = strength
        self.normal = normal
        self.v = (u / u.length).cross(normal)
        self.u = self.v.cross(normal)

    def get_nearest_vec(self, vec):
        u_d = vec.dot(self.u)
        v_d = vec.dot(self.v)
        if u_d * u_d > v_d * v_d:
            return self.u if u_d > 0 else -self.u
        else:
            return self.v if v_d > 0 else -self.v

    def calc_alignment(self, vec):
        vec = vec.normalized()
        dv = self.v.dot(vec)
        du = self.u.dot(vec)
        return max(dv * dv, du * du)

    def select_4_edges(self, vert):
        edge_vecs = [(edge, edge.other_vert(vert).co - vert.co) for edge in vert.link_edges]
        u_edges = []
        v_edges = []
        edge_vecs = sorted(edge_vecs,
                           key=lambda v: self.u.dot(v[1].normalized()))
        u_edges.append(edge_vecs.pop(-1))
        u_edges.append(edge_vecs.pop(0))
        edge_vecs = sorted(edge_vecs,
                           key=lambda v: self.v.dot(v[1].normalized()), )
        v_edges.append(edge_vecs.pop(-1))
        v_edges.append(edge_vecs.pop(0))
        return u_edges, v_edges

    def get_matrix(self):
        return Matrix((self.u, self.v, self.normal)).transposed().to_4x4()


class FrameField:

    def __init__(self, obj):
        self.bm = bmesh.new()
        self.bm.from_mesh(obj.data)
        self.mask = {}
        if obj.get("Density Mask", None):
            try:
                mask_vg = obj.vertex_groups[obj.get("Density Mask")]
                for vert in self.bm.verts:
                    try:
                        self.mask[vert.index] = mask_vg.weight(vert.index)
                    except RuntimeError:
                        pass
            except KeyError:
                pass

        bmesh.ops.triangulate(self.bm, faces=self.bm.faces)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()
        self.tree = bvhtree.BVHTree.FromBMesh(self.bm)
        self.vert_field = {}
        self.sharpness_field = {}
        self.face_field = {}

    def build_major_curvatures(self):
        for vert in self.bm.verts:
            if len(vert.link_edges) == 0:
                continue
            best_normal = Vector()
            best_value = -10
            for edge in vert.link_edges:
                other_vert = edge.other_vert(vert)
                value = other_vert.normal.angle(vert.normal)
                if value > best_value:
                    best_normal = other_vert.normal
                    best_value = value
            self.vert_field[vert.index] = CrossFrame(best_normal.cross(vert.normal), vert.normal, best_value)
            self.sharpness_field[vert.index] = best_value
        self.ready = True

    def from_grease_pencil(self, gp_frame, mat, x_mirror=False):

        new_field = {}
        for stroke in gp_frame.strokes:
            for i in range(len(stroke.points) - 1):
                p0 = mat @ stroke.points[i].co
                p1 = mat @ stroke.points[i + 1].co
                p_avg = (p0 + p1) / 2
                d = (p0 - p1).normalized()
                location, normal, face_index, distance = self.tree.find_nearest(p_avg)
                for vert in self.bm.faces[face_index].verts:
                    i = vert.index
                    new_field[i] = CrossFrame(d, vert.normal)

                if x_mirror:
                    p_avg.x = -p_avg.x
                    location, normal, face_index, distance = self.tree.find_nearest(p_avg)
                    for vert in self.bm.faces[face_index].verts:
                        i = vert.index
                        new_field[i] = CrossFrame(d.reflect(Vector((1, 0, 0))), normal)
        if new_field:
            self.vert_field = new_field

    def erase_part(self, factor=3):
        target_size = 1 + len(self.vert_field) / factor
        for item in (sorted(self.vert_field.items(), key=lambda i: i[1].strength)):
            del self.vert_field[item[0]]
            if len(self.vert_field) <= target_size:
                break

    def marching_growth(self):
        seen_verts = set(self.bm.verts[i] for i in self.vert_field.keys())
        current_front = set()
        for vert in seen_verts:
            for edge in vert.link_edges:
                other_vert = edge.other_vert(vert)
                if other_vert not in seen_verts:
                    current_front.add(other_vert)

        while True:
            new_front = set()
            for vert in current_front:
                u = Vector()
                connected_frames = 0
                for edge in vert.link_edges:
                    other_vert = edge.other_vert(vert)
                    if other_vert in seen_verts:
                        if not connected_frames:
                            u += self.vert_field[other_vert.index].u
                            connected_frames += 1
                        else:
                            u += self.vert_field[other_vert.index].get_nearest_vec(u)
                            connected_frames += 1
                    else:
                        new_front.add(other_vert)
                if connected_frames:
                    self.vert_field[vert.index] = CrossFrame(u / connected_frames, vert.normal)
                    seen_verts.add(vert)
            current_front = new_front
            if len(new_front) == 0:
                break

    def smooth(self, iterations=2):
        for _ in range(iterations):
            new_vert_field = {}
            for index in self.vert_field.keys():
                vert = self.bm.verts[index]
                count = 1
                u = Vector()
                c = 0
                for edge in vert.link_edges:
                    i = edge.other_vert(vert).index
                    if i in self.vert_field:
                        u += self.vert_field[i].get_nearest_vec(u)
                        count += 1
                u /= count
                c /= count
                new_vert_field[index] = CrossFrame(u, vert.normal)
            self.vert_field = new_vert_field

    def mirror_field(self):
        new_field = {}
        for vert in self.bm.verts:
            if vert.co.x < 0:
                new_field[vert.index] = self.vert_field[vert.index]
            else:
                vec = self.sample_point(vert.co).frame.u
                new_field[vert.index] = CrossFrame(vec, vert.normal)
        self.vert_field = new_field

    def sample_point(self, point):
        hit = self.tree.find_nearest(point)
        if None not in hit:
            return HitInfo(*hit, self)
        else:
            return None