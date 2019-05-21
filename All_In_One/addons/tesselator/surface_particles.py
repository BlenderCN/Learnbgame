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
from . import vector_fields
from . import draw_3d
from mathutils import Vector
from mathutils.kdtree import KDTree
from random import choice, random


def get_gp_frame(context):
    frame = None
    gp = context.scene.grease_pencil
    if gp:
        if gp.layers:
            if gp.layers.active:
                if gp.layers.active.active_frame:
                    frame = gp.layers.active.active_frame
                    print(frame)
    return frame


class ParticleManager:
    def __init__(self, obj):
        self.min_resolution = 0
        self.max_resolution = 0
        self.particles = []
        self.obj = obj
        self.field = vector_fields.FrameField(obj)

        self.inv_mat = obj.matrix_world.inverted()

        self.bm = self.field.bm
        self.kd_tree = KDTree(0)
        self.kd_tree.balance()
        self.draw_obj = draw_3d.DrawObject()

        self.triangle_mode = False

    def build_field(self, context, use_gp, x_mirror):
        self.field.build_major_curvatures()
        frame = get_gp_frame(context)
        if frame and use_gp:
            self.field.from_grease_pencil(frame, mat=self.inv_mat, x_mirror=x_mirror)
            self.field.marching_growth()
            self.field.smooth(2)

        else:
            self.field.erase_part(3)
            self.field.marching_growth()
            self.field.smooth()
            self.field.smooth()
            self.field.smooth()
            self.field.smooth()
            self.field.smooth()

    def build_kdtree(self):
        tree = KDTree(len(self.particles))
        for id, p in enumerate(self.particles):
            tree.insert(p.location, id)
        tree.balance()
        self.kd_tree = tree

    def initialize_particles_from_gp(self, resolution, context):
        scale = max(self.obj.dimensions) / max(self.obj.scale)
        frame = get_gp_frame(context)
        created_particles = 0
        if not frame:
            return created_particles
        for stroke in frame.strokes:
            co = self.inv_mat @ stroke.points[0].co
            last_particle = self.create_particle(Partile, co)
            last_particle.update_radius()
            created_particles += 1
            for point in stroke.points:
                co = self.inv_mat @ point.co
                if (co - last_particle.location).length >= last_particle.radius * 2:
                    last_particle = self.create_particle(Partile, co)
                    last_particle.update_radius()
                    created_particles += 1
        return created_particles

    def initialize_from_features(self, verts, resolution=20, count=50):
        scale = max(self.obj.dimensions) / max(self.obj.scale)
        verts = sorted(self.field.bm.verts, key=lambda v: self.field.sharpness_field.get(v.index, float("inf")),
                       reverse=True)
        for i in range(min(count, len(self.field.bm.verts))):
            vert = verts[i]
            co = vert.co.copy()
            p1 = self.create_particle(Partile, co)
            p1.update_radius()

    def initialize_from_verts(self, verts):
        for vert in verts:
            p = self.create_particle(Partile, vert.co)

    def initialize_grid(self, verts, resolution=20, use_x_mirror=True):
        particle_locations = set()
        scale = max(self.obj.dimensions)
        for vert in verts:
            co = vert.co.copy()
            co /= scale
            co *= resolution
            x = int(co.x)
            y = int(co.y)
            z = int(co.z)
            if use_x_mirror:
                if x > 0:
                    particle_locations.add((x, y, z))
            else:
                particle_locations.add((x, y, z))

        for location in particle_locations:
            co = Vector(location)
            co *= scale
            co /= resolution
            hit = self.sample_surface(co)
            p1 = self.create_particle(Partile, hit.co)
            p1.update_radius()
            if use_x_mirror:
                hit.co.x *= -1
                p2 = self.create_particle(Partile, hit.co)
                p2.update_radius()
                p1.counter_pair, p2.counter_pair = p2, p1

    def mirror_particles(self, any_side=False):
        new_particles = []
        for particle in self.particles:
            if particle.location.x > particle.radius or any_side:
                co = particle.location.copy()
                co.x *= -1
                p1 = particle
                p2 = Partile(co, self)
                p2.radius = p1.radius
                p2.tag = p1.tag
                p1.counter_pair, p2.counter_pair = p2, p1
                new_particles.append(p2)
                new_particles.append(p1)

            elif -particle.radius * 0.5 < particle.location.x < particle.radius * 0.5:
                new_particles.append(particle)
                particle.lock_x = True

        self.particles = new_particles
        self.build_kdtree()

    def create_particle(self, type, location, prepend=False):
        p = type(location, self)
        if not prepend:
            self.particles.append(p)
        else:
            self.particles.insert(0, p)
        return p

    def remove_particle(self, particle):
        self.particles.remove(particle)

    def step(self, speed, ):
        new_tree = KDTree(len(self.particles))
        self.draw_obj.reset()
        for id, particle in enumerate(self.particles):
            particle.step(speed)
            particle.draw()
            new_tree.insert(particle.location, id)
        new_tree.balance()
        self.kd_tree = new_tree

    def spread_step(self):
        count = 0
        new_particles = []
        self.draw_obj.reset()

        for particle in self.particles:
            new_particles += particle.spread()
            count += len(new_particles)

        for particle in self.particles:
            if not particle.tag == "REMOVE":
                new_particles.append(particle)
        self.particles = new_particles

        new_tree = KDTree(len(self.particles))
        for id, particle in enumerate(self.particles):
            particle.draw()
            new_tree.insert(particle.location, id)
        new_tree.balance()
        self.kd_tree = new_tree

        return count

    def get_nearest(self, location, n):
        for location, index, dist in self.kd_tree.find_n(location, n):
            yield self.particles[index], dist

    def sample_surface(self, location):
        return self.field.sample_point(location)

    def draw(self):
        self.draw_obj.reset()
        for particle in self.particles:
            particle.draw()

    def simplify_mesh(self, bm):

        class Ownership:
            def __init__(self, particle, dist):
                self.particle = particle
                self.distance = dist
                self.valid = False

        bmesh.ops.triangulate(bm, faces=bm.faces)
        last_edges = float("+inf")
        while True:
            edges = set()
            for edge in bm.edges:
                le = (edge.verts[0].co - edge.verts[1].co).length_squared
                center = edge.verts[0].co + edge.verts[1].co
                center /= 2
                for p, dist in self.get_nearest(center, 1):
                    if p.radius ** 2 < le:
                        edges.add(edge)
            if not len(edges) < last_edges:
                break
            last_edges = len(edges)
            bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1)
            bmesh.ops.triangulate(bm, faces=bm.faces)

        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        tree = KDTree(len(bm.verts))
        for vert in bm.verts:
            tree.insert(vert.co, vert.index)
        tree.balance()

        ownership_mapping = {}
        ownership_validation_front = set()

        for vert in bm.verts:
            for p, dist in self.get_nearest(vert.co, 1):
                ownership_mapping[vert] = Ownership(p, dist)

        for particle in self.particles:
            location, index, dist = tree.find(particle.location)
            vert = bm.verts[index]
            if vert in ownership_mapping:
                if ownership_mapping[vert].particle == particle:
                    ownership_mapping[vert].valid = True
                    ownership_validation_front.add(vert)

        while True:
            new_front = set()
            for vert in ownership_validation_front:
                for edge in vert.link_edges:
                    other_vert = edge.other_vert(vert)
                    if other_vert not in ownership_mapping:
                        continue
                    if ownership_mapping[other_vert].valid:
                        continue
                    if other_vert in ownership_mapping:
                        if ownership_mapping[vert].particle is ownership_mapping[other_vert].particle:
                            new_front.add(other_vert)
                            ownership_mapping[other_vert].valid = True
            ownership_validation_front = new_front
            if not new_front:
                break

        new_bm = bmesh.new()
        for particle in self.particles:
            particle.vert = new_bm.verts.new(particle.location)

        for face in bm.faces:
            connections = set()
            for vert in face.verts:
                if vert in ownership_mapping:
                    if ownership_mapping[vert].valid:
                        p = ownership_mapping[vert].particle
                        connections.add(p)
            if len(connections) == 3:
                try:
                    new_bm.faces.new([particle.vert for particle in connections])
                except ValueError:
                    pass
        while True:
            stop = True
            for vert in new_bm.verts:
                if len(vert.link_edges) < 3:
                    new_bm.verts.remove(vert)
                    stop = False
            if stop:
                break

        bmesh.ops.holes_fill(new_bm, edges=new_bm.edges)
        bmesh.ops.triangulate(new_bm, faces=new_bm.faces)
        bmesh.ops.recalc_face_normals(new_bm, faces=new_bm.faces)
        if not self.triangle_mode:
            bmesh.ops.join_triangles(new_bm, faces=new_bm.faces, angle_face_threshold=1.0, angle_shape_threshold=3.14)

        return new_bm


class Partile:
    def __init__(self, location, manager):
        self.last_hit = manager.sample_surface(location)
        self.location = self.last_hit.co
        self.normal = self.last_hit.normal
        self.manager = manager
        self.radius = 0.05
        self.loc_history = [location] * 3
        self.counter_pair = None
        self.lock_x = False
        self.tag = False
        self.parent = None

    def update_radius(self):
        mask = self.last_hit.mask
        self.radius = (self.manager.max_resolution * mask) + (self.manager.min_resolution * (1 - mask))

    def cubic_decay(self, x, d):
        x = x / d
        x = max(min(x, 1), 0)
        return (2 * (x * x * x)) - (3 * (x * x)) + 1

    def force_vector(self, target):
        d = self.location - target
        le = d.length_squared
        if le == 0:
            return Vector()
        d /= le * le
        return d

    def quad_force(self, neighbor):
        angle = max(neighbor.normal.dot(self.normal), 0)
        if angle < 0:
            return Vector()
        d = self.force_vector(neighbor.location) * 2

        if not self.manager.triangle_mode:
            u = neighbor.last_hit.frame.get_nearest_vec(d) * neighbor.radius
            v = u.cross(neighbor.last_hit.frame.normal)
            for vec in ((u + v), (u - v)):
                d += self.force_vector(vec + neighbor.location) * 0.2 * angle

        return d


    def step(self, speed):

        if self.counter_pair and self.location.x < 0:
            return

        hit = self.last_hit
        movement = Vector()
        count = 0
        avg_dist = 0

        for neighbor, dist in self.manager.get_nearest(self.location, 9):
            if dist <= 0:
                self.velocity = Vector((random() - 0.5, random() - 0.5, random() - 0.5)).normalized().cross(
                    self.normal) * 16 * self.radius
                continue

            avg_dist += dist
            movement += self.quad_force(neighbor)
            count += 1

        if not count:
            return

        if self.parent:
            if (self.parent.location - self.location).length_squared > ((self.radius + self.parent.radius) * 1.2) ** 2:
                movement -= self.force_vector(self.parent.location)

        self.radius = (avg_dist / count) / 2.1
        movement.normalize()
        self.last_hit = self.manager.sample_surface(self.location + (movement * self.radius * speed))
        self.location = self.last_hit.co
        self.update_radius()
        self.loc_history.pop(0)
        self.loc_history.append(self.location)
        self.normal = self.last_hit.normal

        if self.counter_pair:
            co = self.location.copy()
            co.x *= -1
            self.counter_pair.location = co
            self.counter_pair.update_radius()
        elif self.lock_x:
            self.location.x = 0

    def spread(self):
        new_particles = []

        if self.tag not in {"REMOVE", "DONE"}:
            for p, dist in self.manager.get_nearest(self.location, 2):
                if p is self:
                    continue
                if p.tag in {"REMOVE"}:
                    continue
                if p is self.parent:
                    continue

                if dist < ((self.radius + p.radius) / 2) * 1.5:
                    self.tag = "REMOVE"
                    p.location += self.location
                    p.location /= 2
                    return new_particles
            u = self.last_hit.frame.u
            v = self.last_hit.frame.v

            for vec in (u, v, -u, -v):
                hit = self.manager.sample_surface(vec * self.radius * 2 + self.location)
                free = True
                for p, dist in self.manager.get_nearest(hit.co, 1):
                    if dist < self.radius * 1.5:
                        free = False
                if free:
                    p1 = Partile(hit.co, self.manager)
                    new_particles.append(p1)
                    p1.update_radius()
                    p1.parent = self
                    self.tag = "DONE"
        return new_particles

    def draw(self):
        cyan = (0, 0.7, 0.7, 1)
        blue = (0, 0.2, 1, 1)
        green = (0.1, 0.7, 0.1, 1)

        mat = self.last_hit.frame.get_matrix()

        lines = [
            (
                mat @ Vector((-1, 1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                mat @ Vector((-1, -1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                blue
            ),
            (
                mat @ Vector((1, 1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                mat @ Vector((1, -1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                cyan
            ),
            (
                mat @ Vector((-1, 1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                mat @ Vector((1, 1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                blue
            ),
            (
                mat @ Vector((-1, -1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                mat @ Vector((1, -1, 0)) * self.radius * 0.9 + self.location + (0.3 * self.radius * self.normal),
                cyan
            ),
        ]
        if self.parent:
            lines.append(
                (
                    self.location + (0.3 * self.radius * self.normal),
                    self.parent.location + (0.3 * self.radius * self.normal),
                    green
                )
            )
        for a, b, color in lines:
            mat = self.manager.obj.matrix_world
            self.manager.draw_obj.add_line(mat @ a, mat @ b, color=color)
