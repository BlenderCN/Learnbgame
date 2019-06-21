# -*- coding: utf-8 -*-
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
# Created by Matti 'Menithal' Lahtinen
import bpy
import copy



def get_mesh_from(selected):
    meshes = []
    
    for select in selected:
        if select.type == "MESH":
            meshes.append(select)

    return meshes


def mix_weights(a, b):
    print("  Mixing", a, b)
    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
    
    bpy.context.object.modifiers["VertexWeightMix"].vertex_group_a = a
    bpy.context.object.modifiers["VertexWeightMix"].vertex_group_b = b
    bpy.context.object.modifiers["VertexWeightMix"].mix_mode = 'ADD'
    bpy.context.object.modifiers["VertexWeightMix"].mix_set = 'OR'
    
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="VertexWeightMix")


def clean_unused_vertex_groups(obj):
    # This part is generic:
    bpy.ops.object.mode_set(mode='OBJECT')
    vertex_groups = copy.copy(obj.vertex_groups.values())

    empty_vertex = []

    for vertex in obj.data.vertices:
        if len(vertex.groups) < 0:
            empty_vertex.append(vertex)

        index = vertex.index

        has_use = []
        for group in vertex_groups:
            try:
                obj.vertex_groups[group.name].weight(index)
                if group not in has_use:
                    has_use.append(group)
            except RuntimeError:
                pass

        for used in has_use:
            vertex_groups.remove(used)

    print(" Removing Unused Bones")

    parent = obj.parent
    _to_remove_bones = []
    if parent is not None and parent.type == "ARMATURE":

        obj.select = False

        bpy.context.scene.objects.active = parent
        parent.select = True
        mapped = [(x.name) for x in vertex_groups]

        bpy.ops.object.mode_set(mode='EDIT')
        print(" Iterating edit bones", len(parent.data.edit_bones))
        for edit_bone in parent.data.edit_bones:
            if edit_bone.name in mapped and edit_bone.name != "HeadTop":
                print("  - Removing Unused Bone", edit_bone.name)
                _to_remove_bones.append(edit_bone)

        for bone_to_remove in _to_remove_bones:
            parent.data.edit_bones.remove(bone_to_remove)

    print(" Found ", len(vertex_groups),
          " without weights, cleaning up", obj.parent)
    for group in vertex_groups:
        print("  - Removing Vertex Groups ", group)
        obj.vertex_groups.remove(group)

    bpy.ops.object.mode_set(mode='OBJECT')
    print(" Found", len(empty_vertex), " Unused Vertices")

    bpy.context.scene.objects.active = obj
