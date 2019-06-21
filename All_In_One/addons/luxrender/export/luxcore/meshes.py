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

import time

import bpy

from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidLuxCoreName


class ExportedShape(object):
    def __init__(self, mesh_definition):
        self.luxcore_object_name = mesh_definition[0]
        self.luxcore_shape_name = 'Mesh-' + self.luxcore_object_name
        self.material_index = mesh_definition[1]


class MeshExporter(object):
    def __init__(self, blender_scene, is_viewport_render=False, blender_object=None):
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        self.blender_object = blender_object

        self.properties = pyluxcore.Properties()
        self.exported_shapes = []


    def convert(self, luxcore_scene):
        # Remove old properties
        self.properties = pyluxcore.Properties()

        self.__convert_object_geometry(luxcore_scene)

        return self.properties


    def __convert_object_geometry(self, luxcore_scene):
        start_time = time.time()

        obj = self.blender_object

        if obj.data is None or obj.type not in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']:
            return

        prepared_mesh = self.__prepare_export_mesh()

        if prepared_mesh is None or len(prepared_mesh.tessfaces) == 0:
            return

        luxcore_shape_name = self.__generate_shape_name()
        self.__export_mesh_to_shape(luxcore_shape_name, prepared_mesh, luxcore_scene)

        bpy.data.meshes.remove(prepared_mesh)

        end_time = time.time() - start_time
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

        mesh_definitions = luxcore_scene.DefineBlenderMesh(name, len(mesh.tessfaces), faces, len(mesh.vertices),
                                                                 vertices, texCoords, vertexColors)

        self.exported_shapes = []
        for entry in mesh_definitions:
            self.exported_shapes.append(ExportedShape(entry))


    def __generate_shape_name(self, matIndex=-1):
        indexString = ('%03d' % matIndex) if matIndex != -1 else ''
        shape_name = '%s-%s%s' % (self.blender_scene.name, self.blender_object.data.name, indexString)

        return ToValidLuxCoreName(shape_name)




