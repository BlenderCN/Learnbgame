
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

# Helper script for Extrating details of the Armature data

import json
import bpy

def build_armature(bone, bones, tree): 
    regular_bone = bones[bone.name] 
    current_tree = {
        "name": bone.name,
        "matrix": bone.matrix,
        "matrix_local": regular_bone.matrix_local,
        "head": bone.head,
        "tail": bone.tail,
        "connect": bone.use_connect,
        "children": []
    }
    for child in bone.children:
        build_armature(child, bones, current_tree["children"])
    tree.append(current_tree)
    return tree    


def build_world_rotations(bone, world_matrix, list):
    parent_rotation = world_matrix.to_quaternion()
    matrix = bone.matrix
    current_rotation = matrix.to_quaternion()
    current_node = {
        "name": bone.name,
        "rotation": parent_rotation * current_rotation,
        "local": bone.matrix_local.to_quaternion()
    }
    list.append(current_node)
    for child in bone.children:
        build_world_rotations(child, world_matrix, list)
    return list

def armature_debug():
    print("|||||||||||||||||||||||||||")
    print("---------------------------")
    print("---------POSE DATA---------")
    print("---------------------------")
    print("|||||||||||||||||||||||||||")

    armature = bpy.context.object

    world_matrix = armature.matrix_world
            
    if bpy.context.active_object:
        bpy.ops.object.mode_set(mode = 'EDIT')
        print(armature.data.edit_bones[0].name)
        if len(armature.data.edit_bones) > 0:
            edit_armature = build_armature( armature.data.edit_bones[0], armature.data.bones, [])
            print("structure =", edit_armature)
            print("#-----------------------------")

    bpy.ops.object.mode_set(mode = 'OBJECT')

#for bone in armature.bones:
#    rotation = quat_to_dict(bone.matrix.to_4x4().to_quaternion())
#    
#    head = vec_to_dict(bone.head)
#    tail = vec_to_dict(bone.tail)
    
#    print(bone.name, rotation, head, tail)
    
