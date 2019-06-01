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

import mathutils, time
from ...outputs.luxcore_api import pyluxcore

from .objects import ObjectExporter


class DupliExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, duplicator, dupli_system=None, is_viewport_render=False):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        self.duplicator = duplicator
        self.dupli_system = dupli_system

        self.properties = pyluxcore.Properties()
        self.dupli_number = 0
        self.dupli_amount = 1


    def convert(self, luxcore_scene):
        self.properties = pyluxcore.Properties()

        if self.dupli_system is None:
            # Dupliverts/faces/frames (no particle/hair system)
            if self.duplicator.dupli_type in ['FACES', 'GROUP', 'VERTS']:
                self.__convert_duplis(luxcore_scene)
        elif self.dupli_system.settings.render_type in ['OBJECT', 'GROUP'] and self.blender_scene.luxcore_translatorsettings.export_particles:
            self.__convert_particles(luxcore_scene)
        elif self.dupli_system.settings.render_type == 'PATH' and self.blender_scene.luxcore_translatorsettings.export_hair:
            self.__convert_hair()

        return self.properties

    def __convert_duplis(self, luxcore_scene):
        """
        Converts duplis and OBJECT and GROUP particle systems
        """
        print('[%s] Exporting duplis' % self.duplicator.name)

        try:
            time_start = time.time()

            mode = 'VIEWPORT' if self.is_viewport_render else 'RENDER'
            self.duplicator.dupli_list_create(self.blender_scene, settings=mode)
            self.dupli_amount = len(self.duplicator.dupli_list)

            for dupli_ob in self.duplicator.dupli_list:
                dupli_object = dupli_ob.object

                # Check for group layer visibility, if the object is in a group
                group_visible = len(dupli_object.users_group) == 0

                for group in dupli_object.users_group:
                    group_visible |= True in [a & b for a, b in zip(dupli_object.layers, group.layers)]

                if not group_visible:
                    continue

                # Convert dupli object
                dupli_name_suffix = '_%s_%d' % (self.duplicator.name, self.dupli_number)
                self.dupli_number += 1

                object_exporter = ObjectExporter(self.luxcore_exporter, self.blender_scene, self.is_viewport_render,
                                                 dupli_object, dupli_name_suffix)
                properties = object_exporter.convert(update_mesh=True, update_material=True, luxcore_scene=luxcore_scene,
                                                     matrix=dupli_ob.matrix.copy(), is_dupli=True)
                self.properties.Set(properties)

            self.duplicator.dupli_list_clear()

            time_elapsed = time.time() - time_start
            print('[%s] Dupli export finished (%.3fs)' % (self.duplicator.name, time_elapsed))
        except Exception as err:
            print('Error in ConvertDuplis for object %s: %s' % (self.duplicator.name, err))
            import traceback
            traceback.print_exc()


    def __convert_particles(self, luxcore_scene):
        obj = self.duplicator
        particle_system = self.dupli_system

        print('[%s: %s] Exporting particle system' % (self.duplicator.name, particle_system.name))

        try:
            time_start = time.time()

            if (self.blender_scene.camera is not None and self.blender_scene.camera.data.luxrender_camera.usemblur
                and self.blender_scene.camera.data.luxrender_camera.objectmblur):
                steps = self.blender_scene.camera.data.luxrender_camera.motion_blur_samples + 1
            else:
                steps = 1

            old_subframe = self.blender_scene.frame_subframe
            current_frame = self.blender_scene.frame_current

            # Collect particles that should be visible
            particles = [p for p in particle_system.particles if p.alive_state == 'ALIVE' or (
                p.alive_state == 'UNBORN' and particle_system.settings.show_unborn) or (
                             p.alive_state in ['DEAD', 'DYING'] and particle_system.settings.use_dead)]

            mode = 'VIEWPORT' if self.is_viewport_render else 'RENDER'
            obj.dupli_list_create(self.blender_scene, settings=mode)
            self.dupli_amount = len(obj.dupli_list)

            dupli_objects = [dupli.object for dupli in obj.dupli_list]
            particle_dupliobj_pairs = list(zip(particles, dupli_objects))

            # dict of the form {particle: [dupli_object, []]} (the empty list will contain the matrices)
            particle_dupliobj_dict = {pair[0]: [pair[1], []] for pair in particle_dupliobj_pairs}

            for i in range(steps):
                self.blender_scene.frame_set(current_frame, subframe=i / steps)

                # Calculate matrix for each particle
                # I'm not using obj.dupli_list[i].matrix because it contains wrong positions
                for particle in particle_dupliobj_dict:
                    dupli_object = particle_dupliobj_dict[particle][0]

                    scale = dupli_object.scale * particle.size
                    scale_matrix = mathutils.Matrix()
                    scale_matrix[0][0] = scale.x
                    scale_matrix[1][1] = scale.y
                    scale_matrix[2][2] = scale.z

                    rotation_matrix = particle.rotation.to_matrix()
                    rotation_matrix.resize_4x4()

                    transform_matrix = mathutils.Matrix()
                    transform_matrix[0][3] = particle.location.x
                    transform_matrix[1][3] = particle.location.y
                    transform_matrix[2][3] = particle.location.z

                    transform = transform_matrix * rotation_matrix * scale_matrix

                    # Only use motion blur for living particles
                    if particle.alive_state == 'ALIVE':
                        # Don't append matrix if it is identical to the previous one
                        if particle_dupliobj_dict[particle][1][-1:] != transform:
                            particle_dupliobj_dict[particle][1].append(transform)
                    else:
                        # Overwrite old matrix
                        particle_dupliobj_dict[particle][1] = [transform]

            obj.dupli_list_clear()
            self.blender_scene.frame_set(current_frame, subframe=old_subframe)

            # Export particles
            for particle in particle_dupliobj_dict:
                dupli_object = particle_dupliobj_dict[particle][0]
                anim_matrices = particle_dupliobj_dict[particle][1]

                # TODO: remove old code
                #self.ConvertObject(dupli_object, matrix=anim_matrices[0], is_dupli=True,
                #                   duplicator=particle_system, anim_matrices=anim_matrices)

                dupli_name_suffix = '_%s_%d' % (self.dupli_system.name, self.dupli_number)
                self.dupli_number += 1
                object_exporter = ObjectExporter(self.luxcore_exporter, self.blender_scene, self.is_viewport_render,
                                                 dupli_object, dupli_name_suffix)
                properties = object_exporter.convert(update_mesh=True, update_material=True, luxcore_scene=luxcore_scene,
                                                     matrix=anim_matrices[0], is_dupli=True, anim_matrices=anim_matrices)
                self.properties.Set(properties)

            time_elapsed = time.time() - time_start
            print('[%s: %s] Particle export finished (%.3fs)' % (self.duplicator.name, particle_system.name, time_elapsed))
        except Exception as err:
            print('Could not convert particle system %s of object %s: %s' % (particle_system.name, obj.name, err))
            import traceback
            traceback.print_exc()


    def __convert_hair(self):
        """
        Converts PATH type particle systems (hair systems)
        """
        print('Hair export not supported yet')