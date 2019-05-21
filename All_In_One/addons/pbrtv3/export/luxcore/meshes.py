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

import time

import bpy

from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidPBRTv3CoreName


class ExportedShape(object):
    def __init__(self, mesh_definition):
        self.luxcore_object_name = mesh_definition[0]
        self.luxcore_shape_name = 'Mesh-' + self.luxcore_object_name
        self.material_index = mesh_definition[1]


class MeshExporter(object):
    def __init__(self, blender_scene, is_viewport_render=False, blender_object=None, use_instancing=False,
                 transformation=None):
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        self.blender_object = blender_object
        self.use_instancing = use_instancing
        self.transformation = transformation

        self.properties = pyluxcore.Properties()
        self.exported_shapes = []


    @staticmethod
    def get_mesh_key(blender_object, is_viewport_render, use_instancing):
        # We have to account for different modifiers being used on shared geometry
        # If the object has any active deforming modifiers we have to give the mesh a unique key
        key = tuple([blender_object.data, blender_object.type, use_instancing])

        if MeshExporter.has_active_modifiers(blender_object, is_viewport_render):
            key += tuple([blender_object])

        if blender_object.library:
            key += tuple([blender_object, blender_object.library])

        if blender_object.data.library:
            key += tuple([blender_object.data, blender_object.data.library])

        return key


    @staticmethod
    def has_active_modifiers(blender_object, is_viewport_render):
        if hasattr(blender_object, 'modifiers') and len(blender_object.modifiers) > 0 and blender_object.data.users > 1:
            for modifier in blender_object.modifiers:
                # Allow non-deforming modifiers
                if modifier.type not in ('COLLISION', 'PARTICLE_INSTANCE', 'PARTICLE_SYSTEM', 'SMOKE'):
                    # Test if the modifier will be visible
                    if (is_viewport_render and modifier.show_viewport) or (not is_viewport_render and modifier.show_render):
                        return True
        return False


    def convert(self, luxcore_scene):
        # Remove old properties
        self.properties = pyluxcore.Properties()

        self.__convert_object_geometry(luxcore_scene)

        return self.properties


    def __convert_object_geometry(self, luxcore_scene):
        start_time = time.time()

        obj = self.blender_object

        if (obj.data is None) or (obj.type not in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']) or (
                        obj.data.pbrtv3_mesh is not None and obj.data.pbrtv3_mesh.portal):
            return

        prepared_mesh = self.__prepare_export_mesh()

        if prepared_mesh is None or len(prepared_mesh.tessfaces) == 0:
            return

        luxcore_shape_name = self.__generate_shape_name()
        self.__export_mesh_to_shape(luxcore_shape_name, prepared_mesh, luxcore_scene)

        bpy.data.meshes.remove(prepared_mesh, do_unlink=False)

        end_time = time.time() - start_time
        if end_time > 0.5:
            print('Export of mesh %s took %.3fs' % (self.blender_object.data.name, end_time))


    def __prepare_export_mesh(self):
        modifier_mode = 'PREVIEW' if self.is_viewport_render else 'RENDER'

        mesh = self.blender_object.to_mesh(self.blender_scene, True, modifier_mode)

        if mesh is not None:
            mesh.update(calc_tessface=True)

        return mesh


    def __export_mesh_to_shape(self, name, mesh, luxcore_scene):
        faces = mesh.tessfaces[0].as_pointer()
        vertices = mesh.vertices[0].as_pointer()

        uv_textures = mesh.tessface_uv_textures
        if len(uv_textures) > 0 and mesh.uv_textures.active and uv_textures.active.data:
            texCoords = uv_textures.active.data[0].as_pointer()
        else:
            texCoords = 0

        vertex_color = mesh.tessface_vertex_colors.active
        if vertex_color:
            vertexColors = vertex_color.data[0].as_pointer()
        else:
            vertexColors = 0

        transformation = None if self.use_instancing else self.transformation

        mesh_definitions = luxcore_scene.DefineBlenderMesh(name, len(mesh.tessfaces), faces, len(mesh.vertices),
                                                                 vertices, texCoords, vertexColors, transformation)

        self.exported_shapes = []
        for entry in mesh_definitions:
            self.exported_shapes.append(ExportedShape(entry))


    def __generate_shape_name(self, matIndex=-1):
        mesh_key = MeshExporter.get_mesh_key(self.blender_object, self.is_viewport_render, self.use_instancing)
        shape_name = self.blender_scene.name

        for elem in mesh_key:
            if hasattr(elem, 'name'):
                shape_name += '_' + elem.name
            else:
                shape_name += str(elem)

        if matIndex != -1:
            shape_name += '_%d' % matIndex

        return ToValidPBRTv3CoreName(shape_name)




