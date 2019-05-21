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
from mathutils import Matrix, Vector
from math import pi
from .Brush import Brush
from .MapManager import MapManager
from .RayCaster import RayCaster
from .VertexFilter import VertexFilter

class Brushes():
    def __init__(self):
        # The brushes are evaluated in world space, so as to avoid distortion
        # caused by a nonuniform object space.
        self.derived_brushes = list()
        self.primary_brush = Brush()

        self.symmetry_axes = list()
        self.symmetry_center = Vector()

    def derive_radial(self, count):
        derived_brushes = self.derived_brushes
        primary_brush = self.primary_brush
        primary_brush_center = primary_brush.center
        primary_brush_normal = primary_brush.normal
        primary_brush_radius = primary_brush.radius

        # Derive radially symmetrical brushes around each axis of symmetry.
        for axis in self.symmetry_axes:
            # Create a translation matrix to account for an axis of symmetry
            # that is offset from the world origin.
            symmetry_axis_offset = Matrix.Translation(self.symmetry_center)

            for i in range(1, count):
                # Create a rotation matrix to rotate a point around the axis of
                # symmetry that is centered at the world origin.
                rotation_matrix =\
                    Matrix.Rotation(2 * pi * i / count, 4, axis)

                # Create a transformation matrix to rotate a point around the
                # axis of symmetry that may be offset from the world origin.
                transformation_matrix = symmetry_axis_offset * (
                    rotation_matrix * symmetry_axis_offset.inverted()
                )

                # Derive the radial brush, and append it to the list of
                # derived brushes.
                derived_brush = Brush()
                derived_brush.center =\
                    transformation_matrix * primary_brush_center
                derived_brush.normal = ((
                        transformation_matrix * primary_brush_normal - (
                            transformation_matrix * Vector((0, 0, 0))
                        )
                    ).normalized()
                )
                derived_brush.radius = primary_brush_radius
                derived_brush.transformation_matrix = transformation_matrix
                derived_brushes.append(derived_brush)

    def derive_mirrored(self):
        derived_brushes = self.derived_brushes
        primary_brush = self.primary_brush

        # Derive symmetrical brushes across each plane of symmetry.  This
        # process generates b * 2 ** p - b derived brushes, where "b" is the
        # number of brushes (primary and derived) prior to calling this method,
        # and "p" is the number of symmetry planes.
        for axis in self.symmetry_axes:
            # Create a scaling matrix to mirror a point across the plane of
            # symmetry centered at the world origin.
            symmetry_mirror = Matrix.Scale(-1, 4, axis)

            # Create a translation matrix to account for a plane of symmetry
            # that is offset from the world origin.
            symmetry_plane_offset = Matrix.Translation(
                2 * self.symmetry_center.project(axis)
            )

            # Create a transformation matrix to mirror a point across the
            # plane of symmetry that may be offset from the world origin.
            transformation_matrix = symmetry_plane_offset * symmetry_mirror

            # Create the mirror image of each brush, and append it to the list
            # of derived brushes.
            for brush in [primary_brush] + derived_brushes:
                derived_brush = Brush()
                derived_brush.center = transformation_matrix * brush.center
                derived_brush.normal = ((
                        transformation_matrix * brush.normal - (
                            transformation_matrix * Vector((0, 0, 0))
                        )
                    ).normalized()
                )
                derived_brush.radius = brush.radius
                derived_brush.transformation_matrix = transformation_matrix * (
                    brush.transformation_matrix
                )
                derived_brushes.append(derived_brush)

    def determine_influence(self, octree, falloff_curve,
                            ignore_backfacing = False, mesh_object = None):
        coordinate_map = octree.coordinate_map
        map_manager = MapManager()
        primary_brush = self.primary_brush
        vertex_filter = VertexFilter()
        vertex_filter.mesh_object = mesh_object

        # Determine the primary brush's influence.
        center = primary_brush.center
        radius = primary_brush.radius
        vertex_filter.indices = octree.get_indices_in_box(center, radius)
        vertex_filter.coordinate_map = coordinate_map
        distance_map = vertex_filter.discard_outside_of_sphere(center, radius)
        primary_brush.indices = vertex_filter.indices

        # Only proceed if at least one vertex is within the primary brush's
        # influence.
        if primary_brush.indices:
            # Create the falloff map for the vertex indices that are within the
            # primary brush's influence.
            map_manager.map_ = distance_map
            map_manager.clip_domain(primary_brush.indices, 'RETAIN')
            primary_brush.falloff_map =\
                falloff_curve.get_falloff_map_from_distance_map(
                distance_map, radius
            )

            # Calculate the primary brush's normal.
            primary_brush_falloff_map = primary_brush.falloff_map
            primary_brush_normal = primary_brush.normal
            normal = Vector((0, 0, 0))
            normal_sampling_radius = 0.333 * radius
            model_matrix = bpy.context.active_object.matrix_world
            vertices = bpy.context.active_object.data.vertices
            for vertex_index, distance in distance_map.items():
                # Only vertices within the normal sampling radius contribute to
                # the primary brush's normal.
                if distance <= normal_sampling_radius:
                    # Disregard vertices that face away from the primary
                    # brush's initial normal.
                    vertex_normal = model_matrix * (
                        vertices[vertex_index].normal
                    ).normalized()
                    if vertex_normal.dot(primary_brush_normal) > 0:
                        # Each vertex normal contributes in proportion to its
                        # falloff value.
                        normal += vertex_normal * (
                            primary_brush_falloff_map[vertex_index]
                        )
            normal.normalize()
            if normal.length_squared > 0:
                primary_brush.normal = normal.normalized()

            # Discard vertices facing away from the primary brush, if
            # necessary.
            if ignore_backfacing:
                vertex_filter.indices = primary_brush.indices
                vertex_filter.discard_backfacing(primary_brush.normal, 'WORLD')
                primary_brush.indices = vertex_filter.indices

        # Determine each derived brush's influence.
        self.update_derived()
        for brush in self.derived_brushes:
            # Determine which vertex indices are within the brush's influence.
            center = brush.center
            radius = brush.radius
            vertex_filter.indices = octree.get_indices_in_box(center, radius)
            vertex_filter.coordinate_map = octree.coordinate_map
            distance_map =\
                vertex_filter.discard_outside_of_sphere(center, radius)
            if ignore_backfacing:
                vertex_filter.discard_backfacing(brush.normal, 'WORLD')
            brush.indices = vertex_filter.indices

            # Only proceed if at least one vertex is within the brush's
            # influence.
            if primary_brush.indices:
                # Create the falloff map for the vertex indices that are within
                # the brush's influence.
                map_manager.map_ = distance_map
                map_manager.clip_domain(brush.indices, 'RETAIN')
                brush.falloff_map =\
                    falloff_curve.get_falloff_map_from_distance_map(
                        distance_map, radius
                    )

    def generate_color_maps(self, color_ramp):
        primary_brush = self.primary_brush
        derived_brushes = self.derived_brushes

        # Clear any existing data from the color maps.
        for brush in [primary_brush] + derived_brushes:
            brush.color_map = dict()

        # With multiple brushes, brush volumes can overlap, and one or more
        # indices may have multiple falloff values associated with it.
        if derived_brushes:
            # Create a combined falloff map from the brushes, ensuring that
            # each index maps to its most intense falloff value.
            combined_falloff_map = dict()
            for brush in [primary_brush] + derived_brushes:
                falloff_map = brush.falloff_map
                for index in falloff_map:
                    if index not in combined_falloff_map or\
                       combined_falloff_map[index] < falloff_map[index]:
                        combined_falloff_map[index] = falloff_map[index]

            # Create a combined color map from the combined falloff map.
            combined_color_map = color_ramp.get_color_map_from_falloff_map(
                combined_falloff_map
            )

            # Create each brush's color map from the combined color map.
            for brush in [primary_brush] + derived_brushes:
                brush.color_map = {
                    index : combined_color_map[index]
                    for index in brush.indices
                }

        # Brush volume overlap is not a concern if only the primary brush
        # exists.
        else:
            # Create the primary brush's color map from its falloff map.
            primary_brush.color_map =\
                color_ramp.get_color_map_from_falloff_map(
                    primary_brush.falloff_map
                )

    def ray_cast_primary_brush_onto_mesh(self, region_x,
                                         region_y, mesh_object,
                                         ignore_backfacing = False):
        context = bpy.context
        primary_brush = self.primary_brush

        # Set the primary brush's parameters by casting a ray from the region
        # space coordinates onto the mesh object.
        ray_caster = RayCaster()
        ray_caster.coordinate_system = 'WORLD'
        ray_caster.mesh_object = mesh_object
        ray_caster.set_ray_from_region(region_x, region_y)
        location, normal, face_index = ray_caster.ray_cast()

        # Indicate that the primary brush is not on the mesh if no intersection
        # occurred.
        if face_index == -1:
            primary_brush.is_on_mesh = False

        # Otherwise, if an intersection occurred, determine if it is valid.
        else:
            # Ignore ray cast hits on backfacing polygons, if specified.
            ray_direction =\
                (ray_caster.ray_target - ray_caster.ray_origin).normalized()
            if ignore_backfacing and ray_direction.dot(normal) > 0:
                primary_brush.is_on_mesh = False

            # For a valid ray cast hit, indicate that the primary brush is on
            # the mesh at the point of intersection and oriented to the mesh's
            # surface normal at this location.
            else:
                primary_brush.is_on_mesh = True
                primary_brush.center = location
                primary_brush.normal = normal

    def resize_primary_brush(self, radius):
        context = bpy.context
        primary_brush = self.primary_brush
        region_height = context.region.height
        region_width = context.region.width

        # Determine the world space radius of the primary brush necessary to
        # project a circle onto the view plane with the specified region space
        # radius.

        # Determine the z-depth of the primary brush's center in normalized
        # device coordinates.
        projection_matrix = context.region_data.perspective_matrix
        co = primary_brush.center.copy()
        co.resize(4)
        co.w = 1
        co.xyzw = projection_matrix * co
        w = co.w
        co.xyz /= w
        NDC_z_depth = co.z

        # Determine the region space coordinates of the primary brush's center.
        region_x = (co.x + 1) * region_width / 2
        region_y = (co.y + 1) * region_height / 2

        # Determine the NDC coordinates of a point on the edge of the
        # circle that should result from projecting the brush onto the view
        # plane.
        co = Vector((region_x, region_y)) + Vector((radius, 0))

        co.x = co.x * 2 / region_width - 1
        co.y = co.y * 2 / region_height - 1
        co.resize(3)
        co.z = NDC_z_depth

        # Calculate the world space radius of the primary brush.
        co.resize(4)
        co.w = 1
        co.xyzw = projection_matrix.inverted() * co
        w = co.w
        co.resize(3)
        co.xyz /= w
        primary_brush.radius = (co - primary_brush.center).length

    def reset(self):
        self.__init__()

    def set_symmetry_from_object(self, mesh_object, object_axes = set()):
        # Set the center of symmetry to the mesh object's world space center.
        self.symmetry_center = mesh_object.location

        # Set the brushes' world space axes of symmetry to the specified axes
        # of the mesh object.
        model_matrix = mesh_object.matrix_world
        symmetry_axes = self.symmetry_axes
        if 'X' in object_axes:
            symmetry_axes.append((
                    model_matrix * Vector((1, 0, 0)) -(
                        model_matrix * Vector((-1, 0, 0))
                    )
                ).normalized()
            )
        if 'Y' in object_axes:
            symmetry_axes.append((
                    model_matrix * Vector((0, 1, 0)) -(
                        model_matrix * Vector((0, -1, 0))
                    )
                ).normalized()
            )
        if 'Z' in object_axes:
            symmetry_axes.append((
                    model_matrix * Vector((0, 0, 1)) -(
                        model_matrix * Vector((0, 0, -1))
                    )
                ).normalized()
            )

    def update_derived(self):
        # Update the parameters of each derived brush according to the current
        # state of the primary brush.
        primary_brush = self.primary_brush
        primary_brush_center = primary_brush.center
        primary_brush_normal = primary_brush.normal
        primary_brush_radius = primary_brush.radius
        for brush in self.derived_brushes:
            transformation_matrix = brush.transformation_matrix
            brush.center = transformation_matrix * primary_brush_center
            brush.normal = ((
                    transformation_matrix * primary_brush_normal - (
                        transformation_matrix * Vector((0, 0, 0))
                    )
                ).normalized()
            )
            brush.radius = primary_brush_radius
