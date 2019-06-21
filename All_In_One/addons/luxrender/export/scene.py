# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# System Libs
import os
import tempfile
import bpy

# Extensions_Framework Libs
from ..extensions_framework import util as efutil

# LuxRender libs
from ..export import get_worldscale, object_anim_matrices
from ..export import lights        as export_lights
from ..export import materials    as export_materials
from ..export import geometry        as export_geometry
from ..export import volumes        as export_volumes
from ..export import fix_matrix_order
from ..export import is_obj_visible
from ..outputs import LuxManager, LuxLog
from ..outputs.file_api import Files
from ..outputs.pure_api import LUXRENDER_VERSION
from ..properties import find_node


class SceneExporterProperties(object):
    """
    Mimics the properties member contained within EXPORT_OT_LuxRender operator
    """
    filename = ''
    directory = ''
    api_type = ''
    write_files = True
    write_all_files = True


class SceneExporter(object):
    properties = SceneExporterProperties()

    def set_properties(self, properties):
        self.properties = properties
        return self

    def set_scene(self, scene):
        self.scene = scene
        return self

    def set_report(self, report):
        self.report = report
        return self

    def report(self, type, message):
        LuxLog('%s: %s' % ('|'.join([('%s' % i).upper() for i in type]), message))

    def object_is_lit(self, GE, obj):

        have_lamp = False
        have_emitter = False

        if obj.type == 'LAMP' and is_obj_visible(self.scene, obj):
            lamp_enabled = export_lights.checkLightEnabled(self.scene, obj.data)
            lamp_enabled &= obj.data.energy > 0.0

            if obj.data.type == 'POINT':
                lamp_enabled &= obj.data.luxrender_lamp.luxrender_lamp_point.L_color.v > 0.0

            if obj.data.type == 'SPOT':
                lamp_enabled &= obj.data.luxrender_lamp.luxrender_lamp_spot.L_color.v > 0.0

            if obj.data.type == 'HEMI':
                lamp_enabled &= obj.data.luxrender_lamp.luxrender_lamp_hemi.L_color.v > 0.0

            if obj.data.type == 'AREA':
                lamp_enabled &= obj.data.luxrender_lamp.luxrender_lamp_area.L_color.v > 0.0
                lamp_enabled &= obj.data.luxrender_lamp.luxrender_lamp_area.power > 0.0
                lamp_enabled &= obj.data.luxrender_lamp.luxrender_lamp_area.efficacy > 0.0

            have_lamp |= lamp_enabled

        if obj.type in ['MESH', 'SURFACE', 'CURVE', 'FONT', 'META'] and is_obj_visible(self.scene, obj):
            for ms in obj.material_slots:
                mat = ms.material

                if mat and mat.luxrender_emission.use_emission:
                    emit_enabled = self.scene.luxrender_lightgroups.is_enabled(mat.luxrender_emission.lightgroup)
                    emit_enabled &= (mat.luxrender_emission.L_color.v * mat.luxrender_emission.gain) > 0.0
                    have_emitter |= emit_enabled

                    if have_emitter:
                        break

                if mat.luxrender_material.nodetree:
                    output_node = find_node(mat, 'luxrender_material_output_node')

                    if output_node is not None:
                        light_socket = output_node.inputs[3]

                        if light_socket.is_linked:
                            have_emitter = light_socket.is_linked

        if have_lamp or have_emitter:
            return True

        return False

    def scene_is_lit(self, GE):

        for obj in self.scene.objects:
            if self.object_is_lit(GE, obj):
                return True

        for grp in bpy.data.groups:
            for obj in list(grp.objects):
                if self.object_is_lit(GE, obj):
                    return True

        return False

    def export(self):
        scene = self.scene

        try:
            if scene is None:
                raise Exception('Scene is not valid for export to %s' % self.properties.filename)

            # Force scene update; NB, scene.update() doesn't work
            scene.frame_set(scene.frame_current)

            # Set up the rendering context
            self.report({'INFO'}, 'Creating LuxRender context')
            created_lux_manager = False
            if LuxManager.GetActive() is None:
                LM = LuxManager(
                    scene.name,
                    api_type=self.properties.api_type,
                )
                LuxManager.SetActive(LM)
                created_lux_manager = True

            LuxManager.SetCurrentScene(scene)
            lux_context = LuxManager.GetActive().lux_context

            GE = export_geometry.GeometryExporter(lux_context, scene)

            if not self.scene_is_lit(GE):
                raise Exception('Scene is not lit!')

            if self.properties.filename.endswith('.lxs'):
                self.properties.filename = self.properties.filename[:-4]

            if self.properties.api_type == 'FILE':
                try:
                    # unfortunately os.access() isn't reliable
                    # only way to test if dir is writable is to actually create
                    # a file in the directory
                    tempfile.TemporaryFile(dir=self.properties.directory).close()
                except EnvironmentError as e:
                    if e.errno == os.errno.EACCES:
                        self.report({'WARNING'},
                                    'Output path "%s" is not writable, using temp directory' % os.path.normpath(
                                        self.properties.directory))
                        self.properties.directory = tempfile.gettempdir()
                    else:
                        raise

            lxs_filename = '/'.join([
                self.properties.directory,
                self.properties.filename
            ])

            if self.properties.directory[-1] not in ('/', '\\'):
                self.properties.directory += '/'

            efutil.export_path = self.properties.directory

            if self.properties.api_type == 'FILE':

                lux_context.set_filename(
                    scene,
                    lxs_filename,
                )

            if not lux_context:
                raise Exception('Lux context is not valid for export to %s' % self.properties.filename)

            export_materials.ExportedMaterials.clear()
            export_materials.ExportedTextures.clear()

            self.report({'INFO'}, 'Exporting render settings')

            if self.properties.api_type == 'FILE':
                lux_context.set_output_file(Files.MAIN)

            # Set up render engine parameters
            lux_context.renderer(*scene.luxrender_rendermode.api_output())
            lux_context.sampler(*scene.luxrender_sampler.api_output())
            lux_context.accelerator(*scene.luxrender_accelerator.api_output())
            lux_context.surfaceIntegrator(*scene.luxrender_integrator.api_output(scene))
            lux_context.volumeIntegrator(*scene.luxrender_volumeintegrator.api_output())
            lux_context.pixelFilter(*scene.luxrender_filter.api_output())

            # Set up camera, view and film
            is_cam_animated = False

            if scene.camera.data.luxrender_camera.usemblur and scene.camera.data.luxrender_camera.cammblur:

                STEPS = scene.camera.data.luxrender_camera.motion_blur_samples
                anim_matrices = object_anim_matrices(scene, scene.camera, steps=STEPS)

                if anim_matrices:
                    num_steps = len(anim_matrices) - 1
                    fsps = float(num_steps) * scene.render.fps / scene.render.fps_base
                    step_times = [(i) / fsps for i in range(0, num_steps + 1)]
                    lux_context.motionBegin(step_times)

                    for m in anim_matrices:
                        lux_context.lookAt(*scene.camera.data.luxrender_camera.lookAt(scene.camera, m))

                    lux_context.motionEnd()
                    is_cam_animated = True

            if not is_cam_animated:
                lux_context.lookAt(*scene.camera.data.luxrender_camera.lookAt(scene.camera))

            lux_context.camera(*scene.camera.data.luxrender_camera.api_output(scene, is_cam_animated))
            lux_context.film(*scene.camera.data.luxrender_camera.luxrender_film.api_output())

            lux_context.worldBegin()
            lights_in_export = False

            # Find linked 'background_set' scenes
            geom_scenes = [scene]
            s = scene

            while s.background_set is not None:
                s = s.background_set
                geom_scenes.append(s)

            # Make sure lamp textures go back into main file, not geom file
            if self.properties.api_type in ['FILE']:
                lux_context.set_output_file(Files.MAIN)

            # Export all data in linked 'background_set' scenes
            for geom_scene in geom_scenes:
                if len(geom_scene.luxrender_volumes.volumes) > 0:
                    self.report({'INFO'}, 'Exporting volume data')
                    if self.properties.api_type == 'FILE':
                        lux_context.set_output_file(Files.MATS)

                    for volume in geom_scene.luxrender_volumes.volumes:
                        lux_context.makeNamedVolume(volume.name, *volume.api_output(lux_context))

                self.report({'INFO'}, 'Exporting geometry')
                if self.properties.api_type == 'FILE':
                    lux_context.set_output_file(Files.GEOM)

                lights_in_export |= GE.iterateScene(geom_scene)

            for geom_scene in geom_scenes:
                # Make sure lamp textures go back into main file, not geom file
                if self.properties.api_type in ['FILE']:
                    lux_context.set_output_file(Files.MAIN)

                self.report({'INFO'}, 'Exporting lights')
                lights_in_export |= export_lights.lights(lux_context, geom_scene, scene, GE.ExportedMeshes)

            if not lights_in_export:
                raise Exception('No lights in exported data!')

            # Default 'Camera' Exterior
            if scene.camera.data.luxrender_camera.Exterior_volume:
                lux_context.exterior(scene.camera.data.luxrender_camera.Exterior_volume)
            elif scene.luxrender_world.default_exterior_volume:
                lux_context.exterior(scene.luxrender_world.default_exterior_volume)

            if self.properties.write_all_files:
                lux_context.worldEnd()

            if created_lux_manager:
                LM.reset()

            self.report({'INFO'}, 'Export finished')
            return {'FINISHED'}

        except Exception as err:
            self.report({'ERROR'}, 'Export aborted: %s' % err)
            import traceback

            traceback.print_exc()

            if scene.luxrender_testing.re_raise:
                raise err

            return {'CANCELLED'}
