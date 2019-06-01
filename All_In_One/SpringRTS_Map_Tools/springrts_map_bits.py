# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy,mathutils

def export_objects_as_features(context, filepath):
    smp = context.scene.smp

    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')

    for obj in bpy.context.selected_objects:
        print("{ name = '"+ obj.data.name + "', x =", int(obj.location.x * 512 + smp.width * 256), ", z =", int(obj.location.y * -512 + smp.length * 256),", rot = \"" + str(int((obj.rotation_euler.z / 6.141592) * 65536)) + "\"},", file=f )

    f.close()

    return {'FINISHED'}

def export_particles_as_features(context):

# Pseudo Code
    for system in context.active_object.particle_systems:
        name =  system.settings.dupli_object.name
        for particle in system.particles:
            print(name,particle.location,particle.rotation)
