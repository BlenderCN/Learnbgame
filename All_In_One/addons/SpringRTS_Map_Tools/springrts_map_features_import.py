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

import bpy,re

def load(context, filepath, width, length):
    print("running read_some_data...")
    f = open(filepath, 'r', encoding='utf-8')

    # would normally load the data here
    count = 0
    
    for line in f:
        k = re.split("\W+", line)
        if k[1] == "name":
            print("Object Name:\tfeature")
            print("Mesh Name:\t" + k[2] )
            print("Location:\t" + k[4] +"," + k[6] )
            print("rotation:\t" + k[8]  + "\n")
            
            if k[2] in bpy.data.meshes:
                print("mesh exists\n")
                mesh = bpy.data.meshes[k[2]]
            else:
                mesh = bpy.data.meshes.new(name=k[2])
            
            object = bpy.data.objects.new(name="feature", object_data = mesh)
            object.location.x = int(k[4])/512 - width/2
            object.location.y = int(k[6])/-512 + length/2
            object.rotation_euler.z = int(k[8]) / 65535.0 * 6.283184
            scene = bpy.context.scene
            scene.objects.link(object)
            count += 1

    print(count ," feature locations loaded")

    f.close()

    return {'FINISHED'}
