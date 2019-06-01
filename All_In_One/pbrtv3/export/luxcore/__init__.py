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

import bpy, time, os

from ...outputs import PBRTv3Manager
from ...outputs.luxcore_api import pyluxcore
from ...extensions_framework import util as efutil
from ...export.volumes import SmokeCache

from .camera import CameraExporter
from .config import ConfigExporter
from .duplis import DupliExporter
from .lights import LightExporter       # ported to new interface, but crucial refactoring/cleanup still missing
from .materials import MaterialExporter
from .meshes import MeshExporter
from .objects import ObjectExporter
from .textures import TextureExporter
from .volumes import VolumeExporter
from .utils import get_elem_key, LightgroupCache, is_lightgroup_opencl_compatible, ErrorCache


class PBRTv3CoreExporter(object):
    def __init__(self, blender_scene, renderengine, is_viewport_render=False, context=None, is_material_preview=False):
        """
        Main exporter class. Only one instance should be used per rendering session.
        To update the rendering on the fly, convert the needed objects/materials etc., then get all updated properties
        with pop_updated_scene_properties() and parse them into the luxcore scene
        """
        PBRTv3Manager.SetCurrentScene(blender_scene)

        self.blender_scene = blender_scene
        self.renderengine = renderengine
        self.is_viewport_render = is_viewport_render
        self.context = context
        self.is_material_preview = is_material_preview

        self.config_properties = pyluxcore.Properties()
        self.scene_properties = pyluxcore.Properties()
        # All property changes since last pop_updated_scene_properties()
        self.updated_scene_properties = pyluxcore.Properties()

        # List of objects that are distributed via particle systems or dupliverts/frames/...
        self.instanced_duplis = set()

        # Permanent (for one viewport session or one final render) caches, structure: {element: ElementExporter}
        self.dupli_cache = {}
        self.light_cache = {}
        self.material_cache = {}
        self.mesh_cache = {}
        self.object_cache = {}
        self.texture_cache = {}
        self.volume_cache = {}

        # Namecache to map an ascending number to each lightgroup name
        self.lightgroup_cache = LightgroupCache(self.blender_scene.pbrtv3_lightgroups)
        # Cache defined passes to avoid multiple definitions
        self.passes_cache = set()

        # Temporary (only used during export) caches to avoid multiple exporting
        self.temp_material_cache = set()
        self.temp_texture_cache = set()
        self.temp_volume_cache = set()

        # Special exporters that are not stored in caches (because there's only one camera and config)
        self.config_exporter = ConfigExporter(self, self.blender_scene, self.is_viewport_render)
        self.camera_exporter = CameraExporter(self.blender_scene, self.is_viewport_render, self.context)

        # If errors happen during export they are added to this cache and printed after the export completes.
        # The summary is printed in core/__init__.py in luxcore_render(), because otherwise it is drowned in a flood
        # of PBRTv3Core-SDL related messages.
        self.error_cache = ErrorCache()


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
        print('\nStarting export...')
        start_time = time.time()

        if luxcore_scene is None:
            image_scale = self.blender_scene.luxcore_scenesettings.imageScale / 100.0
            if image_scale < 0.99:
                print('All textures will be scaled down by factor %.2f' % image_scale)
            else:
                image_scale = 1

            luxcore_scene = pyluxcore.Scene(image_scale)

        # Convert camera and add it to the scene. This needs to be done before object conversion because e.g.
        # hair export needs a valid defined camera object in case it is view-dependent
        self.convert_camera()
        luxcore_scene.Parse(self.pop_updated_scene_properties())

        SmokeCache.reset()
        self.convert_all_volumes()

        if self.is_viewport_render and self.context.space_data.local_view:
            # In local view, only export "local" objects and add a white background light
            for blender_object in self.context.visible_objects:
                self.convert_object(blender_object, luxcore_scene)

            background_props = pyluxcore.Properties()
            background_props.Set(pyluxcore.Property('scene.lights.LOCALVIEW_BACKGROUND.type', 'constantinfinite'))

            self.__set_scene_properties(background_props)
        else:
            # Materials, textures, lights and meshes are all converted by their respective Blender object
            object_amount = len(self.blender_scene.objects)
            object_counter = 0

            for blender_object in self.blender_scene.objects:
                if self.renderengine.test_break():
                    print('EXPORT CANCELLED BY USER')
                    return None

                object_counter += 1
                self.renderengine.update_stats('Exporting...', 'Object: ' + blender_object.name)
                self.renderengine.update_progress(object_counter / object_amount)

                self.convert_object(blender_object, luxcore_scene)

        # Convert config at last because all lightgroups and passes have to be already defined
        self.convert_config(film_width, film_height)
        self.convert_imagepipeline()
        self.convert_lightgroup_scales(verbose=True)

        # Debug output
        if self.blender_scene.luxcore_translatorsettings.print_cfg:
            print('\nConfig Properties:')
            print(self.config_properties)
        if self.blender_scene.luxcore_translatorsettings.print_scn:
            print('\nScene Properties:')
            print(self.scene_properties)

        # Show message in Blender UI
        export_time = time.time() - start_time
        print('Export finished (%.1fs)' % export_time)

        if self.blender_scene.luxcore_translatorsettings.export_type == 'luxcoreui':
            message = 'Starting PBRTv3CoreUI...'
        elif self.config_exporter.get_engine().endswith('CPU'):
            message = 'Starting PBRTv3...'
        else:
            message = 'Compiling OpenCL Kernels...'
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


    def convert_imagepipeline(self):
        """
        This method is not part of the config exporter because it works on the session rather than the scene,
        so it can be updated without restarting the rendering
        """
        temp_properties = pyluxcore.Properties()

        if self.blender_scene.camera is None:
            return temp_properties

        imagepipeline_settings = self.blender_scene.camera.data.pbrtv3_camera.luxcore_imagepipeline
        export_to_luxcoreui = self.blender_scene.luxcore_translatorsettings.export_type == 'luxcoreui'
        index = 0
        prefix = 'film.imagepipeline.'

        # Output switcher
        if imagepipeline_settings.output_switcher_pass != 'disabled':
            channel = imagepipeline_settings.output_switcher_pass
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'OUTPUT_SWITCHER'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.channel', channel))
            index += 1

        # Tonemapper
        tonemapper = imagepipeline_settings.tonemapper_type

        if tonemapper == 'TONEMAP_LINEAR' and imagepipeline_settings.use_auto_linear:
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'TONEMAP_AUTOLINEAR'))
            index += 1

        temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', tonemapper))

        if tonemapper == 'TONEMAP_LINEAR':
            # With autogain final render exposure is too bright for blender. I use the same factor empirically
            # found for lux_camera.exposure_time(). This will nearly match viewport and final render, but while
            # the viewport gain is calculated from the whole area not filmsize, differences are expected.
            # TODO: find out reason for color diffences, which colorspace is Blender expecting ?
            if not (self.is_viewport_render or export_to_luxcoreui) and imagepipeline_settings.use_auto_linear:
                scale = imagepipeline_settings.linear_scale / 2.25
            else:
                scale = imagepipeline_settings.linear_scale

            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.scale', scale))
        elif tonemapper == 'TONEMAP_REINHARD02':
            prescale = imagepipeline_settings.reinhard_prescale
            postscale = imagepipeline_settings.reinhard_postscale
            burn = imagepipeline_settings.reinhard_burn
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.prescale', prescale))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.postscale', postscale))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.burn', burn))
        elif tonemapper == 'TONEMAP_LUXLINEAR':
            lux_camera = self.blender_scene.camera.data.pbrtv3_camera
            sensitivity = lux_camera.sensitivity
            #exposure = lux_camera.exposure_time() if not self.is_viewport_render else lux_camera.exposure_time() * 2.25
            fstop = lux_camera.fstop

            if self.is_viewport_render or export_to_luxcoreui:
                exposure = lux_camera.exposure_time()
            else:
                exposure = lux_camera.exposure_time() / 2.25

            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.sensitivity', sensitivity))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.exposure', exposure))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.fstop', fstop))
        index += 1

        # Premultiply Alpha
        if imagepipeline_settings.transparent_film and not export_to_luxcoreui and 'ALPHA' in self.passes_cache:
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'PREMULTIPLY_ALPHA'))
            index += 1

        # Background image
        if imagepipeline_settings.use_background_image:
            path = efutil.filesystem_path(imagepipeline_settings.background_image)
            gamma = imagepipeline_settings.background_image_gamma

            if self.is_viewport_render and imagepipeline_settings.background_camera_view_only:
                show_in_view = self.context.region_data.view_perspective == 'CAMERA'
            else:
                show_in_view = True

            if os.path.exists(path) and os.path.isfile(path) and show_in_view:
                temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'BACKGROUND_IMG'))
                temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.file', path))
                temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.gamma', gamma))
                temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.storage', 'byte'))
                index += 1

        # Mist
        if imagepipeline_settings.use_mist:
            color = list(imagepipeline_settings.mist_color)
            amount = imagepipeline_settings.mist_amount
            start = imagepipeline_settings.mist_startdistance
            end = imagepipeline_settings.mist_enddistance
            exclude_background = imagepipeline_settings.mist_excludebackground

            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'MIST'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.color', color))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.amount', amount))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.startdistance', start))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.enddistance', end))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.excludebackground', exclude_background))
            index += 1

        # Bloom
        if imagepipeline_settings.use_bloom:
            # radius and weight are in percent (0-100) in Blender, PBRTv3Core needs range 0..1
            radius = imagepipeline_settings.bloom_radius / 100
            weight = imagepipeline_settings.bloom_weight / 100
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'BLOOM'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.radius', radius))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.weight', weight))
            index += 1

        # Color aberration
        if imagepipeline_settings.use_color_aberration:
            amount = imagepipeline_settings.color_aberration_amount
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'COLOR_ABERRATION'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.amount', amount))
            index += 1

        # Vignetting
        if imagepipeline_settings.use_vignetting:
            scale = imagepipeline_settings.vignetting_scale
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'VIGNETTING'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.scale', scale))
            index += 1

        # Camera response function
        if imagepipeline_settings.crf_type != 'NONE':
            if imagepipeline_settings.crf_type == 'PRESET' and imagepipeline_settings.crf_preset != 'None':
                crf_name = imagepipeline_settings.crf_preset
            elif imagepipeline_settings.crf_file != '':
                crf_name = imagepipeline_settings.crf_file
            else:
                crf_name = False

            if crf_name:
                temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'CAMERA_RESPONSE_FUNC'))
                temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.name', crf_name))
                index += 1

        # Contour lines for IRRADIANCE pass
        if imagepipeline_settings.output_switcher_pass == 'IRRADIANCE':
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'CONTOUR_LINES'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.range', imagepipeline_settings.contour_range))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.scale', imagepipeline_settings.contour_scale))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.steps', imagepipeline_settings.contour_steps))
            temp_properties.Set(
                pyluxcore.Property(prefix + str(index) + '.zerogridsize', imagepipeline_settings.contour_zeroGridSize))
            index += 1

        # Gamma correction: Blender expects gamma corrected image in realtime preview, but not in final render
        if self.is_viewport_render or export_to_luxcoreui:
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.type', 'GAMMA_CORRECTION'))
            temp_properties.Set(pyluxcore.Property(prefix + str(index) + '.value', 2.2))
            index += 1

        self.config_properties.Set(temp_properties)
        # For tonemapping update during rendering
        return temp_properties


    def convert_lightgroup_scales(self, verbose=False):
        """
        This method is not part of the config exporter because it works on the session rather than the scene,
        so it can be updated without restarting the rendering

        This method has to be called after all lights and materials have been exported since it assumes that the
        lightgroup_cache already contains all lightgroups used in the scene
        """
        temp_properties = pyluxcore.Properties()
        prefix = 'film.radiancescales.'

        if not self.blender_scene.pbrtv3_lightgroups.ignore:
            for lg, id in self.lightgroup_cache.get_lightgroup_id_pairs():
                if is_lightgroup_opencl_compatible(self, id):
                    if verbose:
                        print('Converting lightgroup "%s" (ID: %d)' % (lg.name, id))

                    temp_properties.Set(pyluxcore.Property(prefix + str(id) + '.enabled', lg.lg_enabled))
                    temp_properties.Set(pyluxcore.Property(prefix + str(id) + '.globalscale', lg.gain))

                    if lg.use_rgb_gain:
                        temp_properties.Set(pyluxcore.Property(prefix + str(id) + '.rgbscale', list(lg.rgb_gain)))

                    if lg.use_temperature:
                        temp_properties.Set(pyluxcore.Property(prefix + str(id) + '.temperature', lg.temperature))
                elif verbose:
                    print('NOT converting lightgroup "%s" (ID: %d) (max. 8 lightgroups in OpenCL engines)' % (lg.name, id))

            self.config_properties.Set(temp_properties)

        # For lightgroup update during rendering
        return temp_properties


    def convert_object(self, blender_object, luxcore_scene, update_mesh=True, update_material=True):
        cache = self.object_cache
        exporter = ObjectExporter(self, self.blender_scene, self.is_viewport_render, blender_object)

        obj_key = get_elem_key(blender_object)

        if obj_key in cache:
            exporter = cache[obj_key]
            old_properties = exporter.properties.GetAllNames()

            # Delete old scene properties
            self.scene_properties.DeleteAll(old_properties)
            self.updated_scene_properties.DeleteAll(old_properties)

        new_properties = exporter.convert(update_mesh, update_material, luxcore_scene)
        self.__set_scene_properties(new_properties)

        cache[obj_key] = exporter


    def convert_mesh(self, blender_object, luxcore_scene, use_instancing, transformation):
        exporter = MeshExporter(self.blender_scene, self.is_viewport_render, blender_object, use_instancing,
                                transformation)
        key = MeshExporter.get_mesh_key(blender_object, self.is_viewport_render, use_instancing)
        self.__convert_element(key, self.mesh_cache, exporter, luxcore_scene)


    def convert_material(self, material):
        mat_key = get_elem_key(material)

        if mat_key in self.temp_material_cache:
            return

        self.temp_material_cache.add(mat_key)
        exporter = MaterialExporter(self, self.blender_scene, material)
        self.__convert_element(mat_key, self.material_cache, exporter)


    def convert_texture(self, texture):
        tex_key = get_elem_key(texture)

        if tex_key in self.temp_texture_cache:
            return

        self.temp_texture_cache.add(tex_key)
        exporter = TextureExporter(self, self.blender_scene, texture)
        self.__convert_element(tex_key, self.texture_cache, exporter)


    def convert_light(self, blender_object, luxcore_scene):
        exporter = LightExporter(self, self.blender_scene, blender_object)
        self.__convert_element(get_elem_key(blender_object), self.light_cache, exporter, luxcore_scene)


    def convert_volume(self, volume):
        vol_key = get_elem_key(volume)

        if vol_key in self.temp_volume_cache:
            return

        self.temp_volume_cache.add(vol_key)
        exporter = VolumeExporter(self, self.blender_scene, volume)
        self.__convert_element(vol_key, self.volume_cache, exporter)


    def convert_duplis(self, luxcore_scene, duplicator, dupli_system=None):
        exporter = DupliExporter(self, self.blender_scene, duplicator, self.is_viewport_render)
        self.__convert_element(get_elem_key(duplicator), self.dupli_cache, exporter, luxcore_scene)


    def convert_all_volumes(self):
        self.__convert_world_volume()

        # Convert volumes from all scenes (necessary for material preview rendering)
        for scn in bpy.data.scenes:
            for volume in scn.pbrtv3_volumes.volumes:
                self.convert_volume(volume)


    def __convert_element(self, cache_key, cache, exporter, luxcore_scene=None):
        if cache_key in cache:
            exporter = cache[cache_key]
            old_properties = exporter.properties.GetAllNames()

            # Delete old scene properties
            self.scene_properties.DeleteAll(old_properties)
            self.updated_scene_properties.DeleteAll(old_properties)

        new_properties = exporter.convert(luxcore_scene) if luxcore_scene else exporter.convert()
        self.__set_scene_properties(new_properties)

        cache[cache_key] = exporter


    def __set_scene_properties(self, properties):
        self.updated_scene_properties.Set(properties)
        self.scene_properties.Set(properties)


    def __convert_world_volume(self):
        # Camera exterior is the preferred volume for world default, fallback is the world exterior
        properties = pyluxcore.Properties()
        volumes = self.blender_scene.pbrtv3_volumes.volumes

        if self.blender_scene.camera is not None:
            cam_exterior_name = self.blender_scene.camera.data.pbrtv3_camera.Exterior_volume

            if cam_exterior_name in volumes:
                cam_exterior = volumes[cam_exterior_name]
                self.convert_volume(cam_exterior)

                volume_exporter = self.volume_cache[cam_exterior]
                properties.Set(pyluxcore.Property('scene.world.volume.default', volume_exporter.luxcore_name))
                self.__set_scene_properties(properties)
                return

        # No valid camera volume found, try world exterior
        world_exterior_name = self.blender_scene.pbrtv3_world.default_exterior_volume

        if world_exterior_name in volumes:
            world_exterior = volumes[world_exterior_name]
            self.convert_volume(world_exterior)

            volume_exporter = self.volume_cache[world_exterior]
            properties.Set(pyluxcore.Property('scene.world.volume.default', volume_exporter.luxcore_name))
            self.__set_scene_properties(properties)
            return

        # Fallback: no valid world default volume found, delete old world default
        self.scene_properties.Delete('scene.world.volume.default')
