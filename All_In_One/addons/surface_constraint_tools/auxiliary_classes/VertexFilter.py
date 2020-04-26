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

# <pep8-80 compliant>

import bpy
from math import sqrt
from mathutils import Matrix, Vector

class VertexFilter():
    def __init__(self):
        self.coordinate_map = None
        self.indices = list()
        self.mesh_object = None

        # NOTE: Each filtration step reassigns the "indices" attribute; any
        #       previously aliased sequence is not altered.

    def discard_backfacing(self, direction_vector, space):
        # Discard each vertex with a normal pointing away from the direction
        # vector.
        vertices = self.mesh_object.data.vertices
        if space == 'OBJECT':
            self.indices = {
                index : vertices[index].normal
                for index in self.indices
                if vertices[index].normal.dot(direction_vector) > 0
            }
        elif space == 'WORLD':
            model_matrix = self.mesh_object.matrix_world
            self.indices = {
                index : model_matrix * vertices[index].normal
                for index in self.indices
                if (model_matrix * vertices[index].normal).dot(
                    direction_vector
                ) > 0
            }

    def discard_backfacing_from_view(self, view):
        coordinate_map = self.coordinate_map
        vertices = mesh_object.data.vertices

        # If the view is a perspective projection, discard each vertex with a
        # normal pointing away from a vector between the vertex and the view
        # origin.
        if view.view_is_perspective:
            view_origin = view.origin
            indices = self.indices
            self.indices = [
                index
                for index in indices
                if vertices[index].normal.dot(
                    coordinate_map[index] - view_origin
                ) < 0
            ]

        # If the view is a parallel projection, discard  each vertex with a
        # normal pointing away from the view direction.
        else:
            view_direction = view.direction
            indices = self.indices
            self.indices = [
                index
                for index in indices
                if vertices[index].normal.dot(view_direction) < 0
            ]

    def discard_indices(self, indices_to_discard):
        # Discard indices that are present in the specified collection.
        if indices_to_discard:
            if type(indices_to_discard) is not set:
                indices_to_discard = set(indices_to_discard)
            self.indices = [
                index
                for index in self.indices
                if index not in indices_to_discard
            ]

    def discard_outside_of_circle(self, center, radius): 
        # Determine if the distance between each vertex and the circle's
        # center, in region space, is less than the circle's radius.  Only
        # retain the indices of vertices that are within the circle.
        region_space_map = self.coordinate_map
        distance_map = dict()
        indices = self.indices
        inside = list()
        radius_squared = radius ** 2
        for index in indices:
            distance_squared =\
                (region_space_map[index] - center).length_squared
            if distance_squared < radius_squared:
                distance_map[index] = sqrt(distance_squared)
                inside.append(index)
        self.indices = inside
        return distance_map

        # NOTE: This approach, by virtue of invoking method calls to C
        #       routines, is faster than using a python algorithm to exclude
        #       coordinates that are outside of the circle's bounding area,
        #       include those that are inside of the circle's circumscribed
        #       diamond, and include all else that satisfy the Pythagorean
        #       theorem for a hypotenuse less than the circle's radius.  

    def discard_outside_of_sphere(self, center, radius): 
        # Determine if the distance between each vertex and the sphere's
        # center, in object space, is less than the sphere's radius.  Only
        # retain the indices of vertices that are within the sphere.  
        coordinate_map = self.coordinate_map
        distance_map = dict()
        indices = self.indices
        inside = list()
        radius_squared = radius ** 2
        for index in indices:
            distance_squared = (coordinate_map[index] - center).length_squared
            if distance_squared < radius_squared:
                distance_map[index] = sqrt(distance_squared)
                inside.append(index)
        self.indices = inside
        return distance_map

    def discard_outside_of_view(self, view): 
        # Assume that the mesh object's bounding box is fully contained in the
        # view projection, and test this assumption.
        bounding_box = mesh_object.bound_box
        bounding_box_contained_in_projection = True

        # Transform the coordinates of each vertex of the bounding box from
        # object space to clip space.  As soon as any single vertex is
        # found to be outside of the view projection, duly indicate, and exit
        # the loop.
        projection_matrix = view.projection_matrix
        for vertex in bounding_box:
            co = Vector(vertex)
            co.resize(4)
            co.w = 1
            co.xyzw = projection_matrix * co
            w = co.w

            # Determine if the coordinates are within the view projection.
            if abs(co.x) > w or\
               abs(co.y) > w or\
               abs(co.z) > w:
                bounding_box_contained_in_projection = False
                break

        # If the bounding box is not entirely contained within the view
        # projection then some vertices may exist outside of the view
        # projection.
        if not bounding_box_contained_in_projection: 
            clip_space_map = self.coordinate_map

            # Retain each clip space vertex that is inside of the view
            # projection.
            indices = self.indices
            self.indices = [
                index
                for index in indices
                if abs(clip_space_map[index].x) < clip_space_map[index].w and\
                   abs(clip_space_map[index].y) < clip_space_map[index].w and\
                   abs(clip_space_map[index].z) < clip_space_map[index].w
            ] 

    def discard_raycast_occluded(self, view):
        object_space_map = self.coordinate_map
        polygons = mesh_object.data.polygons
        vertices = mesh_object.data.vertices

        # A mesh object's raycast data is not accessible in Edit mode.
        if mesh_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # A mesh object's raycast method is valid only if polygons are present.
        if polygons:
            indices = self.indices
            offset = 0.001
            unoccluded = list()

            # If the view is a perspective projection, cast, from each vertex,
            # a ray in the direction of the view origin.  Discard all rays that
            # intersect with the mesh object before terminating at the near
            # clipping plane.
            if view.view_is_perspective:
                clip_start = bpy.context.space_data.clip_start
                view_direction = view.direction
                view_origin = view.origin
                for index in indices:
                    co = object_space_map[index]
                    ray = view_origin - co
                    ray_direction = ray.normalized()
                    distance =\
                        ray.magnitude + (
                            clip_start / ray_direction.dot(view_direction)
                        )
                    ray_origin = co + ray_direction * offset
                    ray_target = co + ray_direction * distance
                    if bpy.app.version < (2, 77, 0):
                        location, normal, face_index =\
                            mesh_object.ray_cast(ray_origin, ray_target)
                    else:
                        hit, location, normal, face_index =\
                            mesh_object.ray_cast(ray_origin, ray_direction)
                    if face_index == -1:
                        unoccluded.append(index)

            # If the view is a parallel projection, cast, from each vertex, a
            # ray antiparallel to the view plane's normal. Discard all rays
            # that intersect with the mesh object before terminating at the
            # near clipping plane.
            else:
                ray_direction = view.direction * -1
                for index in indices:
                    co = object_space_map[index]
                    ray_origin = co + ray_direction * offset
                    ray_target = co + ray_direction * 1000
                    if bpy.app.version < (2, 77, 0):
                        location, normal, face_index =\
                            mesh_object.ray_cast(ray_origin, ray_target)
                    else:
                        hit, location, normal, face_index =\
                            mesh_object.ray_cast(ray_origin, ray_direction)
                    if face_index == -1:
                        unoccluded.append(index)

            self.indices = unoccluded

    def reset(self):
        self.__init__()

    def retain_indices(self, indices_to_retain):
        # Retain indices that are present in the specified collection.
        if indices_to_retain:
            if type(indices_to_retain) is not set:
                indices_to_retain = set(indices_to_retain)
            self.indices = [
                index
                for index in self.indices
                if index in indices_to_retain
        ]
        else:
            self.indices = list()
