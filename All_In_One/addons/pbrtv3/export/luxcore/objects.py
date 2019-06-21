# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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

import os

from ...extensions_framework import util as efutil
from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidPBRTv3CoreName
from ...export import is_obj_visible
from ...export import object_anim_matrices
from ...export import matrix_to_list
from ...properties import find_node

from .utils import calc_shutter, get_elem_key, log_exception
from .meshes import MeshExporter


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
        self.is_dupli = len(dupli_name_suffix) > 0

        self.properties = pyluxcore.Properties()
        self.exported_objects = []


    def convert(self, update_mesh, update_material, luxcore_scene, anim_matrices=None, matrix=None):
        self.properties = pyluxcore.Properties()

        self.__convert_object(luxcore_scene, update_mesh, update_material, anim_matrices, matrix)

        return self.properties


    def __use_instancing(self, anim_matrices):
        """
        Adapted from ../geometry.py line 611
        Find out if the object should be instanced (use .transformation property on the object instead of the shape)
        """
        obj = self.blender_object

        # If the object uses motion blur, the transformation must not be baked into the mesh, that's why we return True
        if anim_matrices and len(anim_matrices) > 1:
           return True

        # Use instancing on every object when in viewport render, to be able to transform them without re-exporting
        # the mesh
        if self.is_viewport_render:
            return True

        # Duplis and proxies are always instanced
        if self.is_dupli or (obj.pbrtv3_object.append_proxy and obj.pbrtv3_object.proxy_type == 'plymesh'):
            return True

        # If the mesh is only used once, instancing is a waste of memory
        # However, duplis don't increase the users count, so we count those separately
        if (not ((obj.parent and obj.parent.is_duplicator) or
                         obj in self.luxcore_exporter.instanced_duplis)) and \
                         obj.data.users == 1:
            return False

        # Only allow instancing for normal objects if the object has certain modifiers applied against
        # the same shared base mesh.
        if hasattr(obj, 'modifiers') and len(obj.modifiers) > 0 and obj.data.users > 1:
            instance = False

            for mod in obj.modifiers:
                # Allow non-deforming modifiers
                instance |= mod.type in ('COLLISION', 'PARTICLE_INSTANCE', 'PARTICLE_SYSTEM', 'SMOKE')

            return instance
        else:
            return True


    def __convert_object(self, luxcore_scene, update_mesh, update_material, anim_matrices, matrix):
        obj = self.blender_object
        is_visible = is_obj_visible(self.blender_scene, obj, self.is_dupli, self.is_viewport_render)

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
        if not self.is_dupli:
            anim_matrices = self.__calc_motion_blur()

        # Check if object should be converted
        convert_object = True

        # Check if object is proxy
        export_proxies = self.blender_scene.luxcore_translatorsettings.export_proxies

        if export_proxies and obj.pbrtv3_object.append_proxy and obj.pbrtv3_object.proxy_type == 'plymesh':
            convert_object = not obj.pbrtv3_object.hide_proxy_mesh
            self.__convert_proxy(update_material, anim_matrices, convert_object, transform)

        # Check if object is duplicator (particle/hair emitter or using dupliverts/frames/...)
        if (len(obj.particle_systems) > 0 or obj.is_duplicator) and not self.is_dupli:
            if get_elem_key(obj) not in self.luxcore_exporter.dupli_cache:
                if obj.parent and obj.parent.is_duplicator:
                    # Go all the way up to the highest duplicator
                    if get_elem_key(obj.parent) not in self.luxcore_exporter.dupli_cache:
                        self.luxcore_exporter.convert_object(obj.parent, luxcore_scene, update_mesh, update_material)
                        return
                else:
                    self.luxcore_exporter.convert_duplis(luxcore_scene, obj)

                convert_object = False
                for psys in obj.particle_systems:
                    convert_object |= psys.settings.use_render_emitter

        # Some dupli types should hide the original
        if obj.is_duplicator and obj.dupli_type in ('VERTS', 'FACES', 'GROUP'):
            convert_object = False

        # Check if object is used as camera clipping plane (don't do this for duplis because they can never be
        # selected as clipping plane)
        if not self.is_dupli and self.blender_scene.camera is not None:
            if obj.name == self.blender_scene.camera.data.pbrtv3_camera.clipping_plane_obj:
                convert_object = False

        if not convert_object or obj.data is None:
            return

        ##################################
        # Real object export starts here #
        ##################################

        use_instancing = self.__use_instancing(anim_matrices)

        if not self.is_dupli:
            print('Converting object %s %s' % (obj.name, 'as instance' if use_instancing else ''))

        # Check if mesh is in cache
        if MeshExporter.get_mesh_key(obj, self.is_viewport_render, use_instancing) in self.luxcore_exporter.mesh_cache:
            # Check if object is in cache
            if get_elem_key(obj) in self.luxcore_exporter.object_cache and update_mesh and not self.is_dupli:
                self.luxcore_exporter.convert_mesh(obj, luxcore_scene, use_instancing, transform)

            self.__update_props(anim_matrices, obj, transform, update_material)
        else:
            # Mesh not in cache
            self.luxcore_exporter.convert_mesh(obj, luxcore_scene, use_instancing, transform)
            self.__update_props(anim_matrices, obj, transform, update_material)


    def __update_props(self, anim_matrices, obj, transform, update_material):
        mesh_exporter = self.luxcore_exporter.mesh_cache[MeshExporter.get_mesh_key(obj, self.is_viewport_render,
                                                                                   self.__use_instancing(anim_matrices))]
        self.__create_luxcore_objects(mesh_exporter.exported_shapes, transform, update_material, anim_matrices)


    def __convert_proxy(self, update_material, anim_matrices, convert_object, transform):
        raw_path = self.blender_object.pbrtv3_object.external_mesh
        path = efutil.filesystem_path(raw_path)
        name = ToValidPBRTv3CoreName(self.blender_object.name + self.dupli_name_suffix)

        if not os.path.exists(path) or len(raw_path) == 0:
            message = 'Invalid path set for proxy "%s"!' % self.blender_object.name
            log_exception(self.luxcore_exporter, message)
            return

        # Convert material
        if update_material or get_elem_key(self.blender_object.active_material) not in self.luxcore_exporter.material_cache:
            self.luxcore_exporter.convert_material(self.blender_object.active_material)

        material_exporter = self.luxcore_exporter.material_cache[get_elem_key(self.blender_object.active_material)]
        luxcore_material_name = material_exporter.luxcore_name

        # Create shape definition (always instanciate proxies)
        name_shape = ToValidPBRTv3CoreName(os.path.basename(path) + '_luxblendproxy')
        self.properties.Set(pyluxcore.Property('scene.shapes.' + name_shape + '.type', 'mesh'))
        self.properties.Set(pyluxcore.Property('scene.shapes.' + name_shape + '.ply', path))
        self.__create_object_properties(name, name_shape, luxcore_material_name, transform, anim_matrices)


    def __create_luxcore_objects(self, exported_shapes, transform, update_material, anim_matrices):
        self.exported_objects = []

        for shape in exported_shapes:
            name = self.blender_object.name + str(shape.material_index) + self.dupli_name_suffix

            if self.blender_object.library:
                name += self.blender_object.library.name

            name = ToValidPBRTv3CoreName(name)

            try:
                material = self.blender_object.material_slots[shape.material_index].material
            except IndexError:
                material = None
                if not self.is_dupli:
                    print('WARNING: material slot %d on object "%s" is unassigned' % (shape.material_index + 1,
                                                                                      self.blender_object.name))

            # Convert material
            if update_material or get_elem_key(material) not in self.luxcore_exporter.material_cache:
                self.luxcore_exporter.convert_material(material)
            material_exporter = self.luxcore_exporter.material_cache[get_elem_key(material)]
            luxcore_material_name = material_exporter.luxcore_name

            self.__create_object_properties(name, shape.luxcore_shape_name, luxcore_material_name, transform, anim_matrices)


    def __handle_pointiness(self, luxcore_shape_name):
        use_pointiness = False

        for mat_slot in self.blender_object.material_slots:
            if mat_slot.material:
                if mat_slot.material.pbrtv3_material.nodetree:
                    # Material with nodetree, check the nodes for pointiness node
                    use_pointiness = find_node(mat_slot.material, 'pbrtv3_texture_pointiness_node')
                else:
                    # Material without nodetree, check its textures for pointiness texture
                    for tex_slot in mat_slot.material.texture_slots:
                        if tex_slot and tex_slot.texture and tex_slot.texture.pbrtv3_texture.type == 'pointiness':
                            use_pointiness = True
                            break

        if use_pointiness:
            pointiness_shape = luxcore_shape_name + '_pointiness'
            self.properties.Set(pyluxcore.Property('scene.shapes.' + pointiness_shape + '.type', 'pointiness'))
            self.properties.Set(pyluxcore.Property('scene.shapes.' + pointiness_shape + '.source', luxcore_shape_name))
            luxcore_shape_name = pointiness_shape

        return luxcore_shape_name


    def __create_object_properties(self, luxcore_object_name, luxcore_shape_name, luxcore_material_name, transform, anim_matrices):
        # Insert a pointiness shape if a pointiness texture is used in one of the materials/textures
        luxcore_shape_name = self.__handle_pointiness(luxcore_shape_name)

        self.exported_objects.append(ExportedObject(luxcore_object_name, luxcore_shape_name, luxcore_material_name))

        prefix = 'scene.objects.' + luxcore_object_name

        self.properties.Set(pyluxcore.Property(prefix + '.material', luxcore_material_name))
        self.properties.Set(pyluxcore.Property(prefix + '.shape', luxcore_shape_name))

        use_motion_blur = anim_matrices and len(anim_matrices) > 1

        if transform is not None and self.__use_instancing(anim_matrices) and not use_motion_blur:
            # In case of motion blur, the object is only transformed by the .motion.n.transformation properties
            self.properties.Set(pyluxcore.Property(prefix + '.transformation', transform))

        # Motion blur (needs at least 2 matrices in anim_matrices)
        if use_motion_blur:
            shutter_open, shutter_close = calc_shutter(self.blender_scene, self.blender_scene.camera.data.pbrtv3_camera)
            step = (shutter_close - shutter_open) / self.blender_scene.camera.data.pbrtv3_camera.motion_blur_samples

            for i in range(len(anim_matrices)):
                time = i * step
                matrix = matrix_to_list(anim_matrices[i], apply_worldscale=True, invert=True)
                self.properties.Set(pyluxcore.Property('%s.motion.%d.time' % (prefix, i), time))
                self.properties.Set(pyluxcore.Property('%s.motion.%d.transformation' % (prefix, i), matrix))


    def __calc_motion_blur(self):
        if self.blender_scene.camera is None:
            return None

        lux_camera = self.blender_scene.camera.data.pbrtv3_camera

        if lux_camera.usemblur and lux_camera.objectmblur:
            steps = lux_camera.motion_blur_samples
            return object_anim_matrices(self.blender_scene, self.blender_object, steps=steps)
        else:
            return None