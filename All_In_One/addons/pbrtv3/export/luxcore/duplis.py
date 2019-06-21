# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli, Jens Verwiebe, Tom Bech, Doug Hammond, Daniel Genrich, Michael Klemm, Simon Wendsche
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

import math, mathutils, time
from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidPBRTv3CoreName
from ...export import matrix_to_list, is_obj_visible

from .objects import ObjectExporter
from .lights import LightExporter
from .utils import log_exception


class DupliExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, duplicator, is_viewport_render=False):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        self.duplicator = duplicator

        self.properties = pyluxcore.Properties()
        self.dupli_number = 0
        self.dupli_amount = 1


    def convert(self, luxcore_scene):
        self.properties = pyluxcore.Properties()
        export_settings = self.blender_scene.luxcore_translatorsettings

        try:
            is_duplicator_without_psys = len(self.duplicator.particle_systems) == 0 and self.duplicator.is_duplicator
            has_particle_systems = False

            # The hair convert function converts one hair system at a time
            for particle_system in self.duplicator.particle_systems:
                if particle_system.settings.render_type in ['OBJECT', 'GROUP']:
                    has_particle_systems = True
                elif particle_system.settings.render_type == 'PATH' and export_settings.export_hair:
                    self.__convert_hair(luxcore_scene, particle_system)

            # The particle convert function converts all particle systems and duplis of one emitter at once
            if (has_particle_systems or is_duplicator_without_psys) and export_settings.export_particles:
                self.__convert_particles(luxcore_scene)

        except Exception:
            log_exception(self.luxcore_exporter, 'Could not convert particle systems of object %s' % self.duplicator.name)
        finally:
            return self.properties


    def __report_progress(self, particle_system=None):
        """
        Show information about the export progress in the UI
        """
        if particle_system is not None:
            name = 'Hair' if particle_system.settings.type == 'HAIR' else 'Particle'
            particle_system_string = ' | %s System: %s' % (name, particle_system.name)
        else:
            particle_system_string = ''

        percentage = (self.dupli_number / self.dupli_amount) * 100
        progress_string = ' (%d%%)' % percentage

        message = 'Object: %s%s%s' % (self.duplicator.name, particle_system_string, progress_string)
        self.luxcore_exporter.renderengine.update_stats('Exporting...', message)


    def __convert_particles(self, luxcore_scene):
        """
        Ported from export/geometry.py (classic export)
        This function always exports with correct rotation, but does not support particle motion blur
        """
        obj = self.duplicator

        print('[%s] Exporting particle systems/duplis' % obj.name)
        time_start = time.time()

        mode = 'VIEWPORT' if self.is_viewport_render else 'RENDER'
        obj.dupli_list_create(self.blender_scene, settings=mode)
        if not obj.dupli_list:
            raise Exception('cannot create dupli list for object %s' % obj.name)

        self.dupli_amount = len(self.duplicator.dupli_list)

        # Create our own DupliOb list to work around incorrect layers
        # attribute when inside create_dupli_list()..free_dupli_list()
        duplis = []
        non_invertible_count = 0
        for dupli_ob in obj.dupli_list:
            if not is_obj_visible(self.blender_scene, dupli_ob.object, True, self.is_viewport_render):
                continue

            # metaballs are omitted from this function intentionally.
            if dupli_ob.object.type not in ['MESH', 'SURFACE', 'FONT', 'CURVE', 'LAMP']:
                continue

            if dupli_ob.matrix.determinant() == 0:
                # Objects with non-invertible matrices cannot be loaded by PBRTv3Core (RuntimeError)
                non_invertible_count += 1
                continue

            if dupli_ob.object not in self.luxcore_exporter.instanced_duplis:
                self.luxcore_exporter.instanced_duplis.add(dupli_ob.object)

            duplis.append(
                (
                    dupli_ob.object,
                    dupli_ob.matrix.copy(),
                    dupli_ob.particle_system.name if dupli_ob.particle_system else obj.name,
                    dupli_ob.persistent_id[:]
                )
            )

        if non_invertible_count > 0:
            print('WARNING: %d particles with non-invertible matrix were skipped.' % non_invertible_count)

        obj.dupli_list_clear()

        # Preprocessing step to speed up particle export below.
        # Export all unique objects used by particle systems once, then only use their luxcore names in the main loop below
        unique_objs = {}
        for do, dm, psys_name, persistent_id in duplis:
            if do.name not in unique_objs:
                # Note: the dupli_suffix does not matter here, we just have to pass anything so the visibility test works
                object_exporter = ObjectExporter(self.luxcore_exporter, self.blender_scene, self.is_viewport_render, do, 'dupli')
                object_exporter.convert(False, False, luxcore_scene, None, dm)
                unique_objs[do.name] = object_exporter.exported_objects

        # dupli object, dupli matrix
        for do, dm, psys_name, persistent_id in duplis:
            # Increment dupli number for progress display
            self.dupli_number += 1

            # Check for group layer visibility, if the object is in a group
            gviz = len(do.users_group) == 0

            for grp in do.users_group:
                gviz |= True in [a & b for a, b in zip(do.layers, grp.layers)]

            if not gviz:
                continue

            # Make it possible to interrupt the export process and report status in the UI
            # (only every 10000 loop iterations for performance reasons)
            if self.dupli_number % 10000 == 0:
                self.__report_progress()

                if self.luxcore_exporter.renderengine.test_break():
                    return

            persistent_id_str = '_'.join([str(elem) for elem in persistent_id])
            dupli_name_suffix = '%s_%s_%s' % (self.duplicator.name, psys_name, persistent_id_str)

            if do.type == 'LAMP':
                light_exporter = LightExporter(self.luxcore_exporter, self.blender_scene, do, dupli_name_suffix)
                self.properties.Set(light_exporter.convert(luxcore_scene, dm))
            else:
                exported_objects = unique_objs[do.name]

                name = do.name + dupli_name_suffix
                if do.library:
                    name += do.library.name
                name = ToValidPBRTv3CoreName(name)

                transform = matrix_to_list(dm, apply_worldscale=True)

                for mat_index, exp_obj in enumerate(exported_objects):
                    prefix = 'scene.objects.%s%d' % (name, mat_index)
                    self.properties.Set(pyluxcore.Property(prefix + '.shape', exp_obj.luxcore_shape_name))
                    self.properties.Set(pyluxcore.Property(prefix + '.material', exp_obj.luxcore_material_name))
                    self.properties.Set(pyluxcore.Property(prefix + '.transformation', transform))

        del duplis

        time_elapsed = time.time() - time_start
        print('[%s] Particle export finished (%.3fs)' % (obj.name, time_elapsed))


    def __convert_hair(self, luxcore_scene, particle_system):
        """
        Converts PATH type particle systems (hair systems)
        """
        obj = self.duplicator
        psys = particle_system

        for mod in obj.modifiers:
            if mod.type == 'PARTICLE_SYSTEM':
                if mod.particle_system.name == psys.name:
                    break

        if not mod.type == 'PARTICLE_SYSTEM':
            return
        elif not mod.particle_system.name == psys.name or not mod.show_render:
            return

        print('[%s: %s] Exporting hair' % (self.duplicator.name, psys.name))
        time_start = time.time()

        # Export code copied from export/geometry (line 947)

        settings = psys.settings.pbrtv3_hair

        hair_size = settings.hair_size
        root_width = settings.root_width
        tip_width = settings.tip_width
        width_offset = settings.width_offset

        if not self.is_viewport_render:
            psys.set_resolution(self.blender_scene, obj, 'RENDER')
        steps = 2 ** psys.settings.render_step
        num_parents = len(psys.particles)
        num_children = len(psys.child_particles)

        if num_children == 0:
            start = 0
        else:
            # Number of virtual parents reduces the number of exported children
            num_virtual_parents = math.trunc(
                0.3 * psys.settings.virtual_parents * psys.settings.child_nbr * num_parents)
            start = num_parents + num_virtual_parents

        segments = []
        points = []
        thickness = []
        colors = []
        uv_coords = []
        total_segments_count = 0
        uv_tex = None
        colorflag = 0
        uvflag = 0
        thicknessflag = 0
        image_width = 0
        image_height = 0
        image_pixels = []

        modifier_mode = 'PREVIEW' if self.is_viewport_render else 'RENDER'
        mesh = obj.to_mesh(self.blender_scene, True, modifier_mode)
        uv_textures = mesh.tessface_uv_textures
        vertex_color = mesh.tessface_vertex_colors

        has_vertex_colors = vertex_color.active and vertex_color.active.data

        if settings.export_color == 'vertex_color':
            if has_vertex_colors:
                colorflag = 1

        if uv_textures.active and uv_textures.active.data:
            uv_tex = uv_textures.active.data
            if settings.export_color == 'uv_texture_map':
                if uv_tex[0].image:
                    image_width = uv_tex[0].image.size[0]
                    image_height = uv_tex[0].image.size[1]
                    image_pixels = uv_tex[0].image.pixels[:]
                    colorflag = 1
            uvflag = 1

        transform = obj.matrix_world.inverted()
        total_strand_count = 0

        if root_width == tip_width:
            thicknessflag = 0
            hair_size *= root_width
        else:
            thicknessflag = 1

        self.dupli_amount = num_parents + num_children

        for pindex in range(start, num_parents + num_children):
            self.dupli_number += 1
            # Make it possible to interrupt the export process
            if self.dupli_number % 10000 == 0:
                self.__report_progress(psys)

                if self.luxcore_exporter.renderengine.test_break():
                    return

            point_count = 0
            i = 0

            if num_children == 0:
                i = pindex

            # A small optimization in order to speedup the export
            # process: cache the uv_co and color value
            uv_co = None
            col = None
            seg_length = 1.0

            for step in range(0, steps):
                co = psys.co_hair(obj, pindex, step)
                if step > 0:
                    seg_length = (co - obj.matrix_world * points[len(points) - 1]).length_squared

                if not (co.length_squared == 0 or seg_length == 0):
                    points.append(transform * co)

                    if thicknessflag:
                        if step > steps * width_offset:
                            thick = (root_width * (steps - step - 1) + tip_width * (
                                        step - steps * width_offset)) / (
                                        steps * (1 - width_offset) - 1)
                        else:
                            thick = root_width

                        thickness.append(thick * hair_size)

                    point_count += + 1

                    if uvflag:
                        if not uv_co:
                            uv_co = psys.uv_on_emitter(mod, psys.particles[i], pindex, uv_textures.active_index)

                        uv_coords.append(uv_co)

                    if settings.export_color == 'uv_texture_map' and not len(image_pixels) == 0:
                        if not col:
                            x_co = round(uv_co[0] * (image_width - 1))
                            y_co = round(uv_co[1] * (image_height - 1))

                            pixelnumber = (image_width * y_co) + x_co

                            r = image_pixels[pixelnumber * 4]
                            g = image_pixels[pixelnumber * 4 + 1]
                            b = image_pixels[pixelnumber * 4 + 2]
                            col = (r, g, b)

                        colors.append(col)
                    elif settings.export_color == 'vertex_color' and has_vertex_colors:
                        if not col:
                            col = psys.mcol_on_emitter(mod, psys.particles[i], pindex, vertex_color.active_index)

                        colors.append(col)

            if point_count == 1:
                points.pop()

                if thicknessflag:
                    thickness.pop()
                point_count -= 1
            elif point_count > 1:
                segments.append(point_count - 1)
                total_strand_count += 1
                total_segments_count = total_segments_count + point_count - 1

        # PBRTv3Core needs tuples, not vectors
        points_as_tuples = [tuple(point) for point in points]

        if not thicknessflag:
            thickness = hair_size

        if not colorflag:
            colors = (1.0, 1.0, 1.0)

        if not uvflag:
            uvs_as_tuples = None
        else:
            # PBRTv3Core needs tuples, not vectors
            uvs_as_tuples = [tuple(uv) for uv in uv_coords]

        luxcore_shape_name = ToValidPBRTv3CoreName(obj.name + '_' + psys.name)

        self.luxcore_exporter.renderengine.update_stats('Exporting...', 'Refining Hair System %s' % psys.name)
        # Documentation: http://www.luxrender.net/forum/viewtopic.php?f=8&t=12116&sid=03a16c5c345db3ee0f8126f28f1063c8#p112819
        luxcore_scene.DefineStrands(luxcore_shape_name, total_strand_count, len(points), points_as_tuples, segments,
                                    thickness, 0.0, colors, uvs_as_tuples,
                                    settings.tesseltype, settings.adaptive_maxdepth, settings.adaptive_error,
                                    settings.solid_sidecount, settings.solid_capbottom, settings.solid_captop,
                                    True)

        # For some reason this index is not starting at 0 but at 1 (Blender is strange)
        material_index = psys.settings.material - 1

        try:
            material = obj.material_slots[material_index].material
        except IndexError:
            material = None
            print('WARNING: material slot %d on object "%s" is unassigned!' % (material_index + 1, obj.name))

        # Convert material
        self.luxcore_exporter.convert_material(material)
        material_exporter = self.luxcore_exporter.material_cache[material]
        luxcore_material_name = material_exporter.luxcore_name

        # The hair shape is located at world origin and implicitly instanced, so we have to
        # move it to the correct position
        transform = matrix_to_list(obj.matrix_world, apply_worldscale=True)

        prefix = 'scene.objects.' + luxcore_shape_name
        self.properties.Set(pyluxcore.Property(prefix + '.material', luxcore_material_name))
        self.properties.Set(pyluxcore.Property(prefix + '.shape', luxcore_shape_name))
        self.properties.Set(pyluxcore.Property(prefix + '.transformation', transform))

        if not self.is_viewport_render:
            # Resolution was changed to 'RENDER' for final renders, change it back
            psys.set_resolution(self.blender_scene, obj, 'PREVIEW')

        time_elapsed = time.time() - time_start
        print('[%s: %s] Hair export finished (%.3fs)' % (obj.name, psys.name, time_elapsed))
