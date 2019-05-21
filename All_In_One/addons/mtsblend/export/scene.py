# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

# System Libs
import os

# Extensions_Framework Libs
from ..extensions_framework import util as efutil

# Mitsuba libs
from ..export.environment import get_environment_trafo, export_world_environment
from ..export.cameras import export_camera_instance
from ..export.lamps import export_lamp_instance
from ..export.materials import ExportedMaterials, ExportedTextures
from ..export.geometry import GeometryExporter
from ..export import Instance, is_object_visible, is_light, is_mesh, is_deforming, object_render_hide, object_render_hide_duplis
from ..outputs import MtsManager, MtsLog


def get_subframes(segs, shutter):
    if segs == 0:
        return [0]

    return [i * shutter / segs for i in range(segs + 1)]


def get_obj_unique_id(b_ob, duplicator):
    if duplicator is not None:
        obj = b_ob.object
        persistent_id = ['%X' % i for i in b_ob.persistent_id if i < 0x7fffffff]
        unique_id = '%s_%s_Dupli(%s)' % (duplicator.name, obj.name, 'x'.join(persistent_id))

    else:
        obj = b_ob
        unique_id = b_ob.name

    return (obj, unique_id)


class SceneExporterProperties:
    """
    Mimics the properties member contained within EXPORT_OT_Mitsuba operator
    """

    filename = ''
    directory = ''
    api_type = ''
    write_files = True
    write_all_files = True


class SceneExporter:

    properties = SceneExporterProperties()
    shape_instances = {}

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
        MtsLog('%s: %s' % ('|'.join([('%s' % i).upper() for i in type]), message))

    def sync_light(self, instances, b_ob, duplicator=None, trafo=None, base_frame=0, seq=0.0):
        (obj, unique_id) = get_obj_unique_id(b_ob, duplicator)

        try:
            instances[unique_id].append_motion(trafo, seq)

        except:
            instances[unique_id] = Instance(
                obj,
                trafo,
            )

    def sync_object(self, instances, b_ob, duplicator=None, trafo=None, hide_mesh=False, base_frame=0, seq=0.0):
        (obj, unique_id) = get_obj_unique_id(b_ob, duplicator)

        # light is handled separately */
        if is_light(obj):
            self.sync_light(instances, b_ob, duplicator, trafo, base_frame, seq)
            return

        # only interested in object that we can create meshes from */
        if not is_mesh(obj):
            return

        if not hide_mesh:
            if duplicator is not None:
                self.GE.objects_used_as_duplis.add(obj)

            if unique_id in instances:
                instance = instances[unique_id]
                is_deform = is_deforming(obj)

                instance.append_motion(trafo, seq, is_deform)

                if is_deform:
                    instance.mesh.append(self.GE.writeMesh(obj, base_frame=base_frame, seq=seq))

            else:
                instances[unique_id] = Instance(
                    obj,
                    trafo,
                    mesh=self.GE.buildMesh(obj, seq=seq),
                )

        number_psystems = len(obj.particle_systems)

        if number_psystems > 0:
            for psys in obj.particle_systems:
                if psys.settings.render_type in 'PATH':
                    hair_id = '%s_%s' % (unique_id, psys.name)

                    if hair_id in instances:
                        instances[hair_id].append_motion(trafo, seq)

                    else:
                        filename = self.GE.handler_Duplis_PATH(obj, psys)

                        if filename:
                            instances[hair_id] = Instance(
                                obj,
                                trafo,
                                mesh=[(
                                    'hair',
                                    psys.settings.material - 1,
                                    'hair',
                                    {
                                        'filename': filename,
                                        'radius': psys.settings.mitsuba_hair.hair_width / 2.0
                                    },
                                    seq
                                )],
                            )

    # Create two lists, one of data blocks to export and one of instances to export
    # Collect and store motion blur transformation data in a pre-process.
    # More efficient, and avoids too many frame updates in blender.
    def cache_motion(self, scene):
        origframe = scene.frame_current
        scene_motion_segments = scene.render.motion_blur_samples if scene.render.use_motion_blur else 0
        segs = {}
        b_sce = scene

        while b_sce is not None:
            # get a de-duplicated set of all possible numbers of motion segments
            # from renderable objects in the scene, and global scene settings
            segs[b_sce.name] = {}
            segs[b_sce.name][scene_motion_segments] = []
            self.shape_instances[b_sce.name] = {}

            for b_ob in b_sce.objects:
                if is_object_visible(scene, b_ob):
                    if scene.render.use_motion_blur and b_ob.mitsuba_object.motion_samples_override:
                        ob_segments = b_ob.mitsuba_object.motion_blur_samples

                        try:
                            segs[b_sce.name][ob_segments].append(b_ob)

                        except:
                            segs[b_sce.name][ob_segments] = [b_ob]

                    else:
                        segs[b_sce.name][scene_motion_segments].append(b_ob)

            b_sce = b_sce.background_set

        # now get a full list of subframes and the corresponding segment groups
        subframes = {}
        for scene_segs in segs.values():
            for num_segs in scene_segs.keys():
                for sub in get_subframes(num_segs, scene.render.motion_blur_shutter):
                    try:
                        subframes[sub].append(num_segs)

                    except:
                        subframes[sub] = [num_segs]

        # the aim here is to do only a minimal number of scene updates,
        # so we go through all subframes and process objects pertaining to
        # segment groups included in the subframe
        while subframes:
            sub = min(subframes.keys())
            seq = sub / scene.render.motion_blur_shutter
            seq_groups = subframes.pop(sub)
            isub, fsub = int(sub), sub - int(sub)
            scene.frame_set(origframe + isub, fsub)

            cam = scene.camera.data
            cam_trafo = (scene.camera.matrix_world.copy(),
                cam.ortho_scale / 2.0 if cam.type == 'ORTHO' else None)

            self.scene_camera.append_motion(cam_trafo, seq)

            env_trafo = get_environment_trafo(scene.world)

            if env_trafo is not None:
                self.world_environment.append_motion(env_trafo, seq)

            b_sce = scene

            while b_sce is not None:
                self.GE.geometry_scene = b_sce
                instances = self.shape_instances[b_sce.name]

                while seq_groups:
                    try:
                        num_segs = seq_groups.pop()
                        scene_obs = segs[b_sce.name][num_segs]

                    except:
                        continue

                    for b_ob in scene_obs:
                        if scene.mitsuba_testing.object_analysis:
                            MtsLog('Analysing object %s : %s' % (b_ob, b_ob.type))

                        if b_ob.is_duplicator and not object_render_hide_duplis(b_ob):
                            if scene.mitsuba_testing.object_analysis:
                                MtsLog("Dupli object", b_ob.name)

                            # dupli objects
                            b_ob.dupli_list_create(scene, 'RENDER')

                            for b_dup in b_ob.dupli_list:
                                b_dup_ob = b_dup.object
                                dup_hide = b_dup_ob.hide_render
                                in_dupli_group = b_dup.type == 'GROUP'
                                (hide_obj, hide_mesh) = object_render_hide(b_dup_ob, False, in_dupli_group)

                                if not (b_dup.hide or dup_hide or hide_obj):
                                    # /* sync object and mesh or light data */
                                    trafo = b_dup.matrix.copy()
                                    self.sync_object(instances, b_dup, b_ob, trafo, hide_mesh, origframe, seq)

                            b_ob.dupli_list_clear()

                        (hide_obj, hide_mesh) = object_render_hide(b_ob, True, True)

                        if not hide_obj:
                            if scene.mitsuba_testing.object_analysis:
                                MtsLog("Synchronizing object", b_ob.name)

                            # object itself
                            trafo = b_ob.matrix_world.copy()
                            self.sync_object(instances, b_ob, None, trafo, hide_mesh, origframe, seq)

                b_sce = b_sce.background_set

        scene.frame_set(origframe, 0)
        return True

    def export(self):
        scene = self.scene
        self.shape_instances = {}

        try:
            if scene is None:
                raise Exception('Scene is not valid for export to %s' % self.properties.filename)

            # Set up the rendering context
            self.report({'INFO'}, 'Creating Mitsuba context')
            created_mts_manager = False

            if MtsManager.GetActive() is None:
                MM = MtsManager(
                    scene.name,
                    api_type=self.properties.api_type,
                )
                MtsManager.SetActive(MM)
                created_mts_manager = True

            MtsManager.SetCurrentScene(scene)
            export_ctx = MtsManager.GetActive().export_ctx

            mts_filename = os.path.join(
                self.properties.directory,
                self.properties.filename
            )

            if self.properties.directory[-1] not in {'/', '\\'}:
                self.properties.directory += '/'

            efutil.export_path = self.properties.directory

            if self.properties.api_type == 'FILE':
                export_ctx.set_filename(
                    scene,
                    mts_filename,
                )

            ExportedMaterials.clear()
            ExportedTextures.clear()

            export_ctx.data_add(scene.mitsuba_integrator.api_output(), 'integrator')

            self.GE = GeometryExporter(export_ctx, scene)
            self.world_environment = Instance(scene.world, None)
            self.scene_camera = Instance(scene.camera, None)
            self.cache_motion(scene)

            # Export world environment
            export_world_environment(export_ctx, self.world_environment)

            export_camera_instance(export_ctx, self.scene_camera, scene)

            cancel = False
            b_sce = scene

            while b_sce is not None and not cancel:
                self.GE.geometry_scene = b_sce

                for name, instance in self.shape_instances[b_sce.name].items():
                    if cancel:
                        break

                    if instance.mesh is not None:
                        self.GE.exportShapeInstances(instance, name)

                    elif instance.obj.type == 'LAMP':
                        export_lamp_instance(export_ctx, instance, name)

                    # cancel = progress.get_cancel();
                b_sce = b_sce.background_set

            self.GE.objects_used_as_duplis.clear()

            # update known exported objects for partial export
            GeometryExporter.KnownModifiedObjects -= GeometryExporter.NewExportedObjects
            GeometryExporter.KnownExportedObjects |= GeometryExporter.NewExportedObjects
            GeometryExporter.NewExportedObjects = set()

            export_ctx.configure()

            if created_mts_manager:
                MM.reset()

            self.report({'INFO'}, 'Export finished')

            return {'FINISHED'}

        except Exception as err:
            self.report({'ERROR'}, 'Export aborted: %s' % err)

            import traceback
            traceback.print_exc()

            if scene.mitsuba_testing.re_raise:
                raise err

            return {'CANCELLED'}
