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

import bpy, time

from ...outputs import LuxManager, LuxLog
from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidLuxCoreName

# TODO: remove refactoring state comments
from .camera import CameraExporter      # finished
from .config import ConfigExporter      # finished
from .duplis import DupliExporter       # needs testing
from .lights import LightExporter       # ported to new interface, but crucial refactoring/cleanup still missing
from .materials import MaterialExporter # some features missing
from .meshes import MeshExporter        # finished
from .objects import ObjectExporter     # some features missing
from .textures import TextureExporter   # finished
from .volumes import VolumeExporter     # finished


class LuxCoreExporter(object):
    def __init__(self, blender_scene, renderengine, is_viewport_render=False, context=None):
        """
        Main exporter class. Only one instance should be used per rendering session.
        To update the rendering on the fly, convert the needed objects/materials etc., then get all updated properties
        with pop_updated_scene_properties() and parse them into the luxcore scene
        """
        LuxManager.SetCurrentScene(blender_scene)

        self.blender_scene = blender_scene
        self.renderengine = renderengine
        self.is_viewport_render = is_viewport_render
        self.context = context

        self.config_properties = pyluxcore.Properties()
        self.scene_properties = pyluxcore.Properties()
        # All property changes since last pop_updated_scene_properties()
        self.updated_scene_properties = pyluxcore.Properties()

        # Permanent caches, structure: {element: ElementExporter}
        self.dupli_cache = {}
        self.light_cache = {}
        self.material_cache = {}
        self.mesh_cache = {}
        self.object_cache = {}
        self.texture_cache = {}
        self.volume_cache = {}

        # Namecache to map an ascending number to each lightgroup name
        self.lightgroup_cache = {}

        # Temporary caches to avoid multiple exporting
        self.temp_material_cache = set()
        self.temp_texture_cache = set()
        self.temp_volume_cache = set()

        # Special exporters that are not stored in caches (because there's only one camera and config)
        self.config_exporter = ConfigExporter(self, self.blender_scene, self.is_viewport_render)
        self.camera_exporter = CameraExporter(self.blender_scene, self.is_viewport_render, self.context)


    def pop_updated_scene_properties(self):
        """
        Get changed scene properties since last call of this function
        """
        updated_properties = pyluxcore.Properties(self.updated_scene_properties)
        self.updated_scene_properties = pyluxcore.Properties()

        # Clear temporary caches
        self.temp_material_cache = set()
        self.temp_texture_cache = set()
        self.temp_volume_cache = set()

        return updated_properties


    def convert(self, film_width, film_height, luxcore_scene=None):
        """
        Convert the whole scene
        """

        start_time = time.time()

        self.convert_camera()
        self.__convert_all_volumes()

        # Materials, textures, lights and meshes are all converted by their respective Blender object
        object_amount = len(self.blender_scene.objects)
        object_counter = 0
        if luxcore_scene is None:
            luxcore_scene = pyluxcore.Scene(self.blender_scene.luxcore_scenesettings.imageScale)

        for blender_object in self.blender_scene.objects:
            if self.renderengine.test_break():
                print('EXPORT CANCELLED BY USER')
                break

            object_counter += 1
            self.renderengine.update_stats('Exporting...', 'Object: ' + blender_object.name)
            self.renderengine.update_progress(object_counter / object_amount)

            self.convert_object(blender_object, luxcore_scene)

        # Convert config at last so all lightgroups and passes are defined
        self.convert_config(film_width, film_height)

        # Debug output
        if self.blender_scene.luxcore_translatorsettings.print_config:
            print(self.config_properties)
            print(self.scene_properties)

        # Show message in Blender UI
        export_time = time.time() - start_time
        print('Export took %.1fs' % export_time)
        engine = self.blender_scene.luxcore_enginesettings.renderengine_type
        message = 'Compiling OpenCL Kernels...' if 'OCL' in engine else 'Starting LuxRender...'
        self.renderengine.update_stats('Export Finished (%.1fs)' % export_time, message)

        # Create luxcore scene and config
        luxcore_scene.Parse(self.pop_updated_scene_properties())
        luxcore_config = pyluxcore.RenderConfig(self.config_properties, luxcore_scene)

        return luxcore_config


    def convert_camera(self):
        camera_props_keys = self.camera_exporter.properties.GetAllNames()
        self.scene_properties.DeleteAll(camera_props_keys)

        self.camera_exporter.convert()
        self.__set_scene_properties(self.camera_exporter.properties)


    def convert_config(self, film_width, film_height):
        config_props_keys = self.config_exporter.properties.GetAllNames()
        self.config_properties.DeleteAll(config_props_keys)

        self.config_exporter.convert(film_width, film_height)
        self.config_properties.Set(self.config_exporter.properties)


    def convert_object(self, blender_object, luxcore_scene, update_mesh=True, update_material=True):
        cache = self.object_cache
        exporter = ObjectExporter(self, self.blender_scene, self.is_viewport_render, blender_object)

        if blender_object in cache:
            exporter = cache[blender_object]
            old_properties = exporter.properties.GetAllNames()

            # Delete old scene properties
            self.scene_properties.DeleteAll(old_properties)
            self.updated_scene_properties.DeleteAll(old_properties)

        new_properties = exporter.convert(update_mesh, update_material, luxcore_scene)
        self.__set_scene_properties(new_properties)

        cache[blender_object] = exporter


    def convert_mesh(self, blender_object, luxcore_scene):
        exporter = MeshExporter(self.blender_scene, self.is_viewport_render, blender_object)
        self.__convert_element(blender_object.data, self.mesh_cache, exporter, luxcore_scene)


    def convert_material(self, material):
        if material in self.temp_material_cache:
            return
        else:
            self.temp_material_cache.add(material)

        exporter = MaterialExporter(self, self.blender_scene, material)
        self.__convert_element(material, self.material_cache, exporter)


    def convert_texture(self, texture):
        if texture in self.temp_texture_cache:
            return
        else:
            self.temp_texture_cache.add(texture)

        exporter = TextureExporter(self, self.blender_scene, texture)
        self.__convert_element(texture, self.texture_cache, exporter)


    def convert_light(self, blender_object, luxcore_scene):
        exporter = LightExporter(self, self.blender_scene, blender_object)
        self.__convert_element(blender_object, self.light_cache, exporter, luxcore_scene)


    def convert_volume(self, volume):
        if volume in self.temp_volume_cache:
            return
        else:
            self.temp_volume_cache.add(volume)

        exporter = VolumeExporter(self, self.blender_scene, volume)
        self.__convert_element(volume, self.volume_cache, exporter)


    def convert_duplis(self, luxcore_scene, duplicator, dupli_system=None):
        exporter = DupliExporter(self, self.blender_scene, duplicator, dupli_system, self.is_viewport_render)
        self.__convert_element((duplicator, dupli_system), self.dupli_cache, exporter, luxcore_scene)


    def __convert_element(self, element, cache, exporter, luxcore_scene=None):
        if element in cache:
            exporter = cache[element]
            old_properties = exporter.properties.GetAllNames()

            # Delete old scene properties
            self.scene_properties.DeleteAll(old_properties)
            self.updated_scene_properties.DeleteAll(old_properties)

        new_properties = exporter.convert(luxcore_scene) if luxcore_scene else exporter.convert()
        self.__set_scene_properties(new_properties)

        cache[element] = exporter


    def __set_scene_properties(self, properties):
        self.updated_scene_properties.Set(properties)
        self.scene_properties.Set(properties)


    def __convert_all_volumes(self):
        self.__convert_world_volume()

        # Convert volumes from all scenes (necessary for material preview rendering)
        for scn in bpy.data.scenes:
            for volume in scn.luxrender_volumes.volumes:
                self.convert_volume(volume)


    def __convert_world_volume(self):
        # Camera exterior is the preferred volume for world default, fallback is the world exterior
        properties = pyluxcore.Properties()
        volumes = self.blender_scene.luxrender_volumes.volumes

        if self.blender_scene.camera is not None:
            cam_exterior_name = self.blender_scene.camera.data.luxrender_camera.Exterior_volume

            if cam_exterior_name in volumes:
                cam_exterior = volumes[cam_exterior_name]
                self.convert_volume(cam_exterior)

                volume_exporter = self.volume_cache[cam_exterior]
                properties.Set(pyluxcore.Property('scene.world.volume.default', volume_exporter.luxcore_name))
                self.__set_scene_properties(properties)
                return

        # No valid camera volume found, try world exterior
        world_exterior_name = self.blender_scene.luxrender_world.default_exterior_volume

        if world_exterior_name in volumes:
            world_exterior = volumes[world_exterior_name]
            self.convert_volume(world_exterior)

            volume_exporter = self.volume_cache[world_exterior]
            properties.Set(pyluxcore.Property('scene.world.volume.default', volume_exporter.luxcore_name))
            self.__set_scene_properties(properties)
            return

        # Fallback: no valid world default volume found, delete old world default
        self.scene_properties.Delete('scene.world.volume.default')
