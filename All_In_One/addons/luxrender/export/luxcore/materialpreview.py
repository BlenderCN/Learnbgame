# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche
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

import bpy
from mathutils import Matrix

from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidLuxCoreName
from ...export import matrix_to_list

from . import LuxCoreExporter
from .objects import ObjectExporter


class MaterialPreviewExporter(object):
    cached_preview_properties = ''

    def __init__(self, blender_scene, renderengine, is_thumbnail, preview_type, preview_material,
                 preview_texture, preview_object):
        self.blender_scene = blender_scene
        self.renderengine = renderengine

        self.is_thumbnail = is_thumbnail
        self.preview_type = preview_type
        self.preview_material = preview_material
        self.preview_texture = preview_texture
        self.preview_object = preview_object


    def convert(self, film_width, film_height):
        luxcore_exporter = LuxCoreExporter(self.blender_scene, self.renderengine)
        luxcore_config = luxcore_exporter.convert(film_width, film_height)

        # Check if we even have to render a new preview (only when something changed)
        # Blender spams many unnecessary updates. The cache has to be static because each preview update
        # creates its own instance of RENDERENGINE_luxrender (and thus MaterialPreviewExporter).
        new_preview_properties = str(luxcore_exporter.scene_properties)

        if MaterialPreviewExporter.cached_preview_properties == new_preview_properties:
            print('Skipping preview render, type:', self.preview_type, 'is_thumbnail:', self.is_thumbnail)
            return
        else:
            MaterialPreviewExporter.cached_preview_properties = new_preview_properties

        # Custom config for preview
        luxcore_config.Parse(self.__create_preview_config())

        # Custom scene for preview
        luxcore_scene = luxcore_config.GetScene()

        # Delete Blender default objects from the scene
        self.__delete_default_objects(luxcore_scene)

        scn_props = pyluxcore.Properties()

        if self.preview_type == 'MATERIAL':
            if self.preview_object.name == 'preview.004' and not self.is_thumbnail:
                # Scene setup for the "World sphere" preview object, should be lit by sun + sky
                self.__create_setup_worldsphere(scn_props)
            else:
                # Scene setup for all other preview objects
                self.__create_setup_material_preview(luxcore_scene, scn_props)### Texture preview ###
        else:
            # Scene setup for texture preview
            self.__create_setup_texture_preview(luxcore_exporter, scn_props)

        luxcore_scene.Parse(scn_props)

        # TODO: remove debug output
        #print(str(luxcore_scene.GetProperties()))

        return luxcore_config


    def __create_setup_worldsphere(self, scn_props):
        scn_props.Set(pyluxcore.Property('scene.lights.sky.type', 'sky'))
        scn_props.Set(pyluxcore.Property('scene.lights.sky.gain', [.00003] * 3))

        scn_props.Set(pyluxcore.Property('scene.lights.sun.type', 'sun'))
        scn_props.Set(pyluxcore.Property('scene.lights.sun.dir', [-0.6, -1, 0.9]))
        scn_props.Set(pyluxcore.Property('scene.lights.sun.gain', [.00003] * 3))


    def __create_setup_material_preview(self, luxcore_scene, scn_props):
        # Add custom elements to the scene (lights, floor)
        # Axis:
        # x: + right, - left
        # y: + back,  - front
        # z: + up,    - down

        # Key light
        color_key = [70] * 3
        position_key = [-10, -15, 10]
        rotation_key = Matrix(((0.8578430414199829, 0.22907057404518127, -0.4600348174571991),
                               (-0.5139118432998657, 0.3823741674423218, -0.7679092884063721),
                               (2.1183037546279593e-09, 0.8951629400253296, 0.44573909044265747)))
        scale_key = 2
        self.__create_area_light(luxcore_scene, scn_props, 'key', color_key, position_key, rotation_key, scale_key)

        # Fill light
        color_fill = [1.5] * 3
        position_fill = [20, -30, 12]
        rotation_fill = Matrix(((0.6418147087097168, -0.3418193459510803, 0.6864644289016724),
                                (0.766859769821167, 0.2860819101333618, -0.5745287537574768),
                                (2.1183037546279593e-09, 0.8951629400253296, 0.44573909044265747)))
        scale_fill = 12
        self.__create_area_light(luxcore_scene, scn_props, 'fill', color_fill, position_fill, rotation_fill, scale_fill)

        # Ground plane
        size = 70
        zpos = -2.00001
        vertices = [
            (size, size, zpos),
            (size, -size, zpos),
            (-size, -size, zpos),
            (-size, size, zpos)
        ]
        faces = [
            (0, 1, 2),
            (2, 3, 0)
        ]
        self.__create_checker_plane(luxcore_scene, scn_props, 'ground_plane', vertices, faces)

        # Plane behind preview object
        size = 70
        ypos = 20
        vertices = [
            (-size, ypos, size),
            (size, ypos, size),
            (size, ypos, -size),
            (-size, ypos, -size)
        ]
        faces = [
            (0, 1, 2),
            (2, 3, 0)
        ]
        self.__create_checker_plane(luxcore_scene, scn_props, 'plane_behind_object', vertices, faces)


    def __create_setup_texture_preview(self, luxcore_exporter, scn_props):
        # Export preview texture and get name
        luxcore_exporter.convert_texture(self.preview_texture)
        scn_props.Set(luxcore_exporter.pop_updated_scene_properties())
        tex_name = luxcore_exporter.texture_cache[self.preview_texture].luxcore_name
        # Create matte material to preview the texture
        mat_name = 'texture_preview_mat'
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.type', 'matte'))
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.kd', tex_name))
        # Assign material to the preview object
        exported_object = luxcore_exporter.object_cache[self.preview_object].exported_objects[0]
        obj_name = exported_object.luxcore_object_name
        shape_name = exported_object.luxcore_shape_name
        # move the preview plane slightly up to avoid numerical precison problems at center (dark speck)
        transform = [1, 0, 0, 0,
                     0, 1, 0, 0,
                     0, 0, 1, 0,
                     0, 0, 1, 1]
        scn_props.Set(pyluxcore.Property('scene.objects.' + obj_name + '.material', mat_name))
        scn_props.Set(pyluxcore.Property('scene.objects.' + obj_name + '.shape', shape_name))
        scn_props.Set(pyluxcore.Property('scene.objects.' + obj_name + '.transformation', transform))
        # Different camera settings are necessary
        scn_props.Set(pyluxcore.Property('scene.camera.lookat.target', [0, 0, 0]))
        scn_props.Set(pyluxcore.Property('scene.camera.lookat.orig', [0, 0, 4]))
        scn_props.Set(pyluxcore.Property('scene.camera.up', [0, 1, 0]))
        # Light for the texture preview
        scn_props.Set(pyluxcore.Property('scene.lights.' + 'distant' + '.type', 'sharpdistant'))
        scn_props.Set(pyluxcore.Property('scene.lights.' + 'distant' + '.direction', [0, 0, -1]))
        scn_props.Set(pyluxcore.Property('scene.lights.' + 'distant' + '.color', [3.1] * 3))


    def __create_checker_plane(self, luxcore_scene, scn_props, name, vertices, faces, light=False):
        mesh_name = name + '_mesh'
        mat_name = name + '_mat'
        tex_name = name + '_tex'

        # Mesh
        luxcore_scene.DefineMesh(mesh_name, vertices, faces, None, None, None, None)
        # Texture
        checker_size = 0.3
        checker_trans = [checker_size, 0, 0, 0, 0, checker_size, 0, 0, 0, 0, checker_size, 0, 0, 0, 0, 1]
        scn_props.Set(pyluxcore.Property('scene.textures.' + tex_name + '.type', 'checkerboard3d'))
        scn_props.Set(pyluxcore.Property('scene.textures.' + tex_name + '.texture1', 0.7))
        scn_props.Set(pyluxcore.Property('scene.textures.' + tex_name + '.texture2', 0.2))
        scn_props.Set(pyluxcore.Property('scene.textures.' + tex_name + '.mapping.type', 'globalmapping3d'))
        scn_props.Set(pyluxcore.Property('scene.textures.' + tex_name + '.mapping.transformation', checker_trans))
        # Material
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.type', 'matte'))
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.kd', tex_name))
        # Invisible for indirect diffuse rays to eliminate fireflies
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.visibility.indirect.diffuse.enable', False))

        if light:
            scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.emission', tex_name))
        # Object
        scn_props.Set(pyluxcore.Property('scene.objects.' + name + '.shape', mesh_name))
        scn_props.Set(pyluxcore.Property('scene.objects.' + name + '.material', mat_name))
        

    def __create_area_light(self, luxcore_scene, scn_props, name, color, position, rotation_matrix, scale):
        mat_name = name + '_mat'
        mesh_name = name + '_mesh'

        # Material
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.type', ['matte']))
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.kd', [0.0] * 3))
        scn_props.Set(pyluxcore.Property('scene.materials.' + mat_name + '.emission', color))

        # assign material to object
        scn_props.Set(pyluxcore.Property('scene.objects.' + name + '.material', [mat_name]))

        # add mesh
        vertices = [
            (1, 1, 0),
            (1, -1, 0),
            (-1, -1, 0),
            (-1, 1, 0)
        ]
        faces = [
            (0, 1, 2),
            (2, 3, 0)
        ]
        luxcore_scene.DefineMesh(mesh_name, vertices, faces, None, None, None, None)
        # assign mesh to object
        scn_props.Set(pyluxcore.Property('scene.objects.' + name + '.shape', [mesh_name]))

        # copy transformation of area lamp object
        scale_matrix = Matrix()
        scale_matrix[0][0] = scale
        scale_matrix[1][1] = scale
        rotation_matrix.resize_4x4()
        transform_matrix = Matrix()
        transform_matrix[0][3] = position[0]
        transform_matrix[1][3] = position[1]
        transform_matrix[2][3] = position[2]

        transform = matrix_to_list(transform_matrix * rotation_matrix * scale_matrix, apply_worldscale=True)
        scn_props.Set(pyluxcore.Property('scene.objects.' + name + '.transformation', transform))


    def __create_preview_config(self):
        cfg_props = pyluxcore.Properties()
        cfg_props.Set(pyluxcore.Property('film.imagepipeline.0.type', 'TONEMAP_LINEAR'))
        cfg_props.Set(pyluxcore.Property('film.imagepipeline.0.scale', 1.0))
        cfg_props.Set(pyluxcore.Property('film.filter.type', 'BLACKMANHARRIS'))

        if self.preview_type == 'MATERIAL':
            cfg_props.Set(pyluxcore.Property('film.filter.width', 1.5))
            cfg_props.Set(pyluxcore.Property('renderengine.type', 'BIASPATHCPU'))
            cfg_props.Set(pyluxcore.Property('tile.size', 16))
            cfg_props.Set(pyluxcore.Property('tile.multipass.enable', 1))
            cfg_props.Set(pyluxcore.Property('tile.multipass.convergencetest.threshold', 0.045))
            cfg_props.Set(pyluxcore.Property('tile.multipass.convergencetest.threshold.reduction', 0))
            cfg_props.Set(pyluxcore.Property('biaspath.sampling.aa.size', 1))
            cfg_props.Set(pyluxcore.Property('biaspath.sampling.diffuse.size', 1))
            cfg_props.Set(pyluxcore.Property('biaspath.sampling.glossy.size', 1))
            cfg_props.Set(pyluxcore.Property('biaspath.sampling.specular.size', 1))
            cfg_props.Set(pyluxcore.Property('biaspath.pathdepth.total', 8))
            cfg_props.Set(pyluxcore.Property('biaspath.pathdepth.diffuse', 3))
            cfg_props.Set(pyluxcore.Property('biaspath.pathdepth.glossy ', 1))
            cfg_props.Set(pyluxcore.Property('biaspath.pathdepth.specular', 4))
            cfg_props.Set(pyluxcore.Property('biaspath.clamping.radiance.maxvalue', 3))
        else:
            cfg_props.Set(pyluxcore.Property('film.filter.width', 2.5))
            cfg_props.Set(pyluxcore.Property('renderengine.type', 'PATHCPU'))
            cfg_props.Set(pyluxcore.Property('path.maxdepth', 1))

        return cfg_props


    def __delete_default_objects(self, luxcore_scene):
        if self.preview_type == 'TEXTURE':
            luxcore_scene.DeleteObject('checkers_0191')
            luxcore_scene.DeleteObject('checkers_0190')
            luxcore_scene.DeleteObject('checkers_0221')
            luxcore_scene.DeleteObject('checkers_0220')
            luxcore_scene.DeleteObject('checkers_0171')
            luxcore_scene.DeleteObject('checkers_0170')
            luxcore_scene.DeleteObject('checkers_0141')
            luxcore_scene.DeleteObject('checkers_0140')
            luxcore_scene.DeleteObject('checkers_0131')
            luxcore_scene.DeleteObject('checkers_0130')
            luxcore_scene.DeleteObject('checkers_0101')
            luxcore_scene.DeleteObject('checkers_0100')
            luxcore_scene.DeleteObject('checkers_031')
            luxcore_scene.DeleteObject('checkers_030')

        luxcore_scene.DeleteObject('checkers_0080')
        luxcore_scene.DeleteObject('checkers_0081')
        luxcore_scene.DeleteObject('checkers_0070')
        luxcore_scene.DeleteObject('checkers_0071')
        luxcore_scene.DeleteObject('checkers_0040')
        luxcore_scene.DeleteObject('checkers_0041')
        luxcore_scene.DeleteObject('checkers_0020')
        luxcore_scene.DeleteObject('checkers_0021')
        luxcore_scene.DeleteLight('Lamp')
        luxcore_scene.DeleteLight('Lamp_001')
        luxcore_scene.DeleteLight('Lamp_002')
        luxcore_scene.DeleteLight('Lamp_008_sky')
        luxcore_scene.DeleteLight('Lamp_008_sun')



