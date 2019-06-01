# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli, Jens Verwiebe, Tom Bech, Simon Wendsche
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#

from ...extensions_framework import util as efutil
from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidLuxCoreName
from ...export import is_obj_visible
from ...export import get_worldscale
from ...export import object_anim_matrices
from ...export import matrix_to_list

from .utils import calc_shutter


class ExportedObject(object):
    def __init__(self, name, shape_name, material_name):
        self.luxcore_object_name = name
        self.luxcore_shape_name = shape_name
        self.luxcore_material_name = material_name


class ObjectExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, is_viewport_render=False, blender_object=None,
                 dupli_name_suffix=''):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        self.blender_object = blender_object
        self.dupli_name_suffix = dupli_name_suffix

        self.properties = pyluxcore.Properties()
        self.exported_objects = []


    def convert(self, update_mesh, update_material, luxcore_scene, anim_matrices=None, matrix=None, is_dupli=False):
        self.properties = pyluxcore.Properties()

        self.__convert_object(luxcore_scene, update_mesh, update_material, anim_matrices, matrix, is_dupli)

        return self.properties


    def __convert_object(self, luxcore_scene, update_mesh, update_material, anim_matrices, matrix, is_dupli):
        obj = self.blender_object
        is_visible = is_obj_visible(self.blender_scene, obj, is_dupli=is_dupli)

        if obj is None or obj.type == 'CAMERA' or not is_visible:
            return

        if obj.type == 'LAMP':
            self.luxcore_exporter.convert_light(self.blender_object, luxcore_scene)
            return

        # Transformation
        if matrix is not None:
            transform = matrix_to_list(matrix, apply_worldscale=True)
        else:
            transform = matrix_to_list(obj.matrix_world, apply_worldscale=True)

        # Motion Blur (duplis get their anim_matrices passed as argument)
        if not is_dupli:
            anim_matrices = self.__calc_motion_blur()

        # Check if object should be converted
        convert_object = True

        # Check if object is proxy
        if obj.luxrender_object.append_proxy and obj.luxrender_object.proxy_type == 'plymesh':
            convert_object = not obj.luxrender_object.hide_proxy_mesh
            self.__convert_proxy(update_material, anim_matrices, convert_object, transform)

        # Check if object is duplicator (particle/hair emitter or using dupliverts/frames/...)
        if len(obj.particle_systems) > 0:
            convert_object = False

            for psys in obj.particle_systems:
                convert_object |= psys.settings.use_render_emitter
                self.luxcore_exporter.convert_duplis(luxcore_scene, obj, psys)
        elif obj.is_duplicator:
            self.luxcore_exporter.convert_duplis(luxcore_scene, obj)

        # Some dupli types should hide the original
        if obj.is_duplicator and obj.dupli_type in ('VERTS', 'FACES', 'GROUP'):
            convert_object = False

        # Check if object is used as camera clipping plane (don't do this for duplis because they can never be
        # selected as clipping plane)
        if not is_dupli and self.blender_scene.camera is not None:
            if obj.name == self.blender_scene.camera.data.luxrender_camera.clipping_plane_obj:
                convert_object = False

        if not convert_object or obj.data is None:
            return

        ##################################
        # Real object export starts here #
        ##################################

        if not is_dupli:
            print('Converting object %s' % obj.name)

        # TODO: dupli handling

        # Check if mesh is in cache
        if obj.data in self.luxcore_exporter.mesh_cache:
            # Check if object is in cache
            if obj in self.luxcore_exporter.object_cache and not is_dupli:
                #print('[%s] object and mesh already in cache' % obj.name)

                if update_mesh:
                    self.luxcore_exporter.convert_mesh(obj, luxcore_scene)
                    mesh_exporter = self.luxcore_exporter.mesh_cache[obj.data]
                    self.__create_luxcore_objects(mesh_exporter.exported_shapes, transform, update_material, anim_matrices)
                else:
                    mesh_exporter = self.luxcore_exporter.mesh_cache[obj.data]
                    self.__create_luxcore_objects(mesh_exporter.exported_shapes, transform, update_material, anim_matrices)
            else:
                # Mesh is in cache, but not this object
                #print('[%s] mesh in cache, but not object' % obj.name)
                mesh_exporter = self.luxcore_exporter.mesh_cache[obj.data]

                self.__create_luxcore_objects(mesh_exporter.exported_shapes, transform, update_material, anim_matrices)
        else:
            # Mesh not in cache
            #print('[%s] mesh and object not in cache' % obj.name)
            self.luxcore_exporter.convert_mesh(obj, luxcore_scene)

            mesh_exporter = self.luxcore_exporter.mesh_cache[obj.data]
            self.__create_luxcore_objects(mesh_exporter.exported_shapes, transform, update_material, anim_matrices)


    def __convert_proxy(self, update_material, anim_matrices, convert_object, transform):
        path = efutil.filesystem_path(self.blender_object.luxrender_object.external_mesh)
        name = ToValidLuxCoreName(self.blender_object.name)

        # Convert material
        if update_material or self.blender_object.active_material not in self.luxcore_exporter.material_cache:
            self.luxcore_exporter.convert_material(self.blender_object.active_material)
        material_exporter = self.luxcore_exporter.material_cache[self.blender_object.active_material]
        luxcore_material_name = material_exporter.luxcore_name

        # Create shape definition
        name_shape = 'Mesh-' + name
        self.properties.Set(pyluxcore.Property('scene.shapes.' + name_shape + '.type', 'mesh'))
        self.properties.Set(pyluxcore.Property('scene.shapes.' + name_shape + '.ply', path))
        self.__create_object_properties(name, name_shape, luxcore_material_name, transform, anim_matrices)


    def __create_luxcore_objects(self, exported_shapes, transform, update_material, anim_matrices):
        self.exported_objects = []

        for shape in exported_shapes:
            name = ToValidLuxCoreName(self.blender_object.name + str(shape.material_index) + self.dupli_name_suffix)

            try:
                material = self.blender_object.material_slots[shape.material_index].material
            except IndexError:
                material = None
                print('WARNING: material slot %d on object "%s" is unassigned!' % (shape.material_index + 1, self.blender_object.name))

            # Convert material
            if update_material or material not in self.luxcore_exporter.material_cache:
                self.luxcore_exporter.convert_material(material)
            material_exporter = self.luxcore_exporter.material_cache[material]
            luxcore_material_name = material_exporter.luxcore_name

            self.__create_object_properties(name, shape.luxcore_shape_name, luxcore_material_name, transform, anim_matrices)


    def __create_object_properties(self, luxcore_object_name, luxcore_shape_name, luxcore_material_name, transform, anim_matrices):
        # Insert a pointiness shape if a pointiness texture is used in one of the materials/textures
        use_pointiness = False
        for mat_slot in self.blender_object.material_slots:
            for tex_slot in mat_slot.material.texture_slots:
                if tex_slot and tex_slot.texture and tex_slot.texture.luxrender_texture.type == 'pointiness':
                    use_pointiness = True
                    break

        if use_pointiness:
            pointiness_shape = luxcore_shape_name + '_pointiness'
            self.properties.Set(pyluxcore.Property('scene.shapes.' + pointiness_shape + '.type', 'pointiness'))
            self.properties.Set(pyluxcore.Property('scene.shapes.' + pointiness_shape + '.source', luxcore_shape_name))
            luxcore_shape_name = pointiness_shape

        self.exported_objects.append(ExportedObject(luxcore_object_name, luxcore_shape_name, luxcore_material_name))

        prefix = 'scene.objects.' + luxcore_object_name

        self.properties.Set(pyluxcore.Property(prefix + '.material', luxcore_material_name))
        self.properties.Set(pyluxcore.Property(prefix + '.shape', luxcore_shape_name))

        if transform is not None:
            self.properties.Set(pyluxcore.Property(prefix + '.transformation', transform))

        # Motion blur (needs at least 2 matrices in anim_matrices)
        if anim_matrices and len(anim_matrices) > 1:
            shutter_open, shutter_close = calc_shutter(self.blender_scene, self.blender_scene.camera.data.luxrender_camera)
            step = (shutter_close - shutter_open) / self.blender_scene.camera.data.luxrender_camera.motion_blur_samples

            for i in range(len(anim_matrices)):
                time = i * step
                matrix = matrix_to_list(anim_matrices[i], apply_worldscale=True, invert=True)
                self.properties.Set(pyluxcore.Property('%s.motion.%d.time' % (prefix, i), time))
                self.properties.Set(pyluxcore.Property('%s.motion.%d.transformation' % (prefix, i), matrix))


    def __calc_motion_blur(self):
        if self.blender_scene.camera is None:
            return None

        lux_camera = self.blender_scene.camera.data.luxrender_camera

        if lux_camera.usemblur and lux_camera.objectmblur:
            steps = lux_camera.motion_blur_samples
            return object_anim_matrices(self.blender_scene, self.blender_object, steps=steps)
        else:
            return None