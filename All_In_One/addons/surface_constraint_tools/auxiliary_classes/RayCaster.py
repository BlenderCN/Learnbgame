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
from bpy_extras import view3d_utils
from mathutils import Vector

class RayCaster():
    '''
    This class is an extension of a mesh object's ray cast method to make it
    more convenient, specifically for the purpose of casting a ray from region
    space coordinates such as the mouse cursor.
    '''

    def __init__(self):
        self.coordinate_system = 'OBJECT'
        self.mesh_object = None
        self.ray_origin = Vector()
        self.ray_target = Vector()

    def set_ray_from_region(self, x, y):
        context = bpy.context
        mesh_object = self.mesh_object
        region = context.region
        region_co = Vector((x, y))
        rv3d = context.region_data
        sv3d = context.space_data

        # Determine the view's clipping distances.
        if rv3d.view_perspective == 'CAMERA':
            camera_data = sv3d.camera.data
            clip_start = camera_data.clip_start
            clip_end = camera_data.clip_end
        else:
            clip_start = sv3d.clip_start
            clip_end = sv3d.clip_end

        # Determine the ray's direction in world space.
        ray_direction = view3d_utils.region_2d_to_vector_3d(
            region, rv3d, region_co
        )

        # For orthographic projections in Blender versions prior to 2.72, the
        # ray's direction needs to be inverted to point into the scene.
        if bpy.app.version < (2, 72, 0):
            if rv3d.view_perspective == 'ORTHO' or (
                   rv3d.view_perspective == 'CAMERA' and
                   sv3d.camera.data.type == 'ORTHO'
               ):
                ray_direction *= -1

        # Determine the ray's origin in world space.
        ray_origin =\
            view3d_utils.region_2d_to_origin_3d(region, rv3d, region_co)

        # Determine the ray's target in world space.
        ray_target = ray_origin + clip_end * ray_direction

        # If the view is an orthographic projection, the ray's origin may exist
        # behind the mesh object.  Therefore, it is necessary to move the ray's
        # origin a sufficient distance antiparallel to the ray's direction to
        # ensure that the ray's origin is in front of the mesh object.
        if rv3d.view_perspective == 'ORTHO':
            ray_origin -= 10000 * ray_direction

        # Otherwise, if the view is a perspective projection or projected from
        # a camera then advance the ray's origin to the near clipping plane.
        else:
            ray_origin += clip_start * ray_direction

        # Convert the ray's origin and target from world space to object space,
        # if necessary.
        if self.coordinate_system == 'OBJECT':
            inverse_model_matrix = mesh_object.matrix_world.inverted()
            for co in ray_origin, ray_target:
                co.xyz = inverse_model_matrix * co

        # Set the ray caster object's ray attributes.
        self.ray_origin = ray_origin
        self.ray_target = ray_target

    def ray_cast(self):
        mesh_object = self.mesh_object
        polygons = mesh_object.data.polygons

        # The mesh object's ray cast method is valid only if polygons are
        # present.
        if not polygons:
            raise Exception((
                    "'{0}' has no polygons available for ray intersection " + 
                    "testing."
                ).format(mesh_object.name)
            )

        # The mesh object's ray cast data is not accessible in Edit mode.
        if mesh_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Convert the ray's origin and target from world space to object space,
        # if necessary.
        if self.coordinate_system == 'WORLD':
            inverse_model_matrix = mesh_object.matrix_world.inverted()
            ray_origin = self.ray_origin.copy()
            ray_target = self.ray_target.copy()
            for co in ray_origin, ray_target:
                co.xyz = inverse_model_matrix * co
        else:
            ray_origin = self.ray_origin
            ray_target = self.ray_target

        # Perform the ray cast intersection test.
        if bpy.app.version < (2, 77, 0):
            location, normal, face_index =\
                mesh_object.ray_cast(ray_origin, ray_target)
        else:
            ray_direction = (ray_target - ray_origin).normalized()
            hit, location, normal, face_index =\
                mesh_object.ray_cast(ray_origin, ray_direction)

        # Convert the object space intersection information to world space, if
        # necessary.
        if self.coordinate_system == 'WORLD':
            model_matrix = mesh_object.matrix_world
            for co in location, normal:
                co.xyz = model_matrix * co
            normal = (normal - mesh_object.location).normalized()

        # Return the intersection information.
        return (location, normal, face_index)
