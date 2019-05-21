# Copyright (c) 2017 The Khronos Group Inc.
# Modifications Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#
# Imports
#

import bmesh
import bpy
import copy
import mathutils
import mathutils.geometry
import math
import os
import tempfile

from .gltf2_debug import *
from .gltf2_get import *
from .utils import *

#
# Globals
#

GLTF_MAX_COLORS = 8
CURVE_DATA_SIZE = 256;

#
# Functions
#

def convert_swizzle_location(loc):
    """
    Converts a location from Blender coordinate system to glTF coordinate system.
    """
    return mathutils.Vector((loc[0], loc[2], -loc[1]))


def convert_swizzle_tangent(tan, sign):
    """
    Converts a tangent from Blender coordinate system to glTF coordinate system.
    """
    return mathutils.Vector((tan[0], tan[2], -tan[1], sign))


def convert_swizzle_rotation(rot):
    """
    Converts a quaternion rotation from Blender coordinate system to glTF coordinate system.
    'w' is still at first position.
    """
    return mathutils.Quaternion((rot[0], rot[1], rot[3], -rot[2]))


def convert_swizzle_scale(scale):
    """
    Converts a scale from Blender coordinate system to glTF coordinate system.
    """
    return mathutils.Vector((scale[0], scale[2], scale[1]))

def decompose_transform_swizzle(matrix):
    translation, rotation, scale = matrix.decompose()
    """
    Decompose a matrix and convert transforms from Blender coordinate system to glTF coordinate system.
    """

    translation = convert_swizzle_location(translation)
    rotation = convert_swizzle_rotation(rotation)
    scale = convert_swizzle_scale(scale)

    return translation, rotation, scale

def convert_swizzle_matrix(matrix):
    """
    Converts a matrix from Blender coordinate system to glTF coordinate system.
    """
    translation, rotation, scale = decompose_transform_swizzle(matrix)

    mat_trans = mathutils.Matrix.Translation(translation)
    mat_rot = mathutils.Quaternion(rotation).to_matrix().to_4x4()
    mat_sca = mathutils.Matrix()
    mat_sca[0][0] = scale[0]
    mat_sca[1][1] = scale[1]
    mat_sca[2][2] = scale[2]

    if bpy.app.version < (2,80,0):
        return mat_trans * mat_rot * mat_sca
    else:
        return mat_trans @ mat_rot @ mat_sca

def extract_primitive_floor(a, indices, use_tangents):
    """
    Shift indices, that the first one starts with 0. It is assumed, that the indices are packed.
    """

    attributes = {
        'POSITION' : [],
        'NORMAL' : []
    }

    if use_tangents:
        attributes['TANGENT'] = []

    result_primitive = {
        'material' : a['material'],
        'useNodeAttrs' : a['useNodeAttrs'],
        'indices' : [],
        'attributes' : attributes
    }

    source_attributes = a['attributes']

    #

    texcoord_index = 0
    process_texcoord = True
    while process_texcoord:
        texcoord_id = 'TEXCOORD_' + str(texcoord_index)

        if source_attributes.get(texcoord_id) is not None:
            attributes[texcoord_id] = []
            texcoord_index += 1
        else:
            process_texcoord = False

    texcoord_max = texcoord_index

    #

    color_index = 0
    process_color = True
    while process_color:
        color_id = 'COLOR_' + str(color_index)

        if source_attributes.get(color_id) is not None:
            attributes[color_id] = []
            color_index += 1
        else:
            process_color = False

    color_max = color_index

    #

    bone_index = 0
    process_bone = True
    while process_bone:
        joint_id = 'JOINTS_' + str(bone_index)
        weight_id = 'WEIGHTS_' + str(bone_index)

        if source_attributes.get(joint_id) is not None:
            attributes[joint_id] = []
            attributes[weight_id] = []
            bone_index += 1
        else:
            process_bone = False

    bone_max = bone_index

    #

    morph_index = 0
    process_morph = True
    while process_morph:
        morph_position_id = 'MORPH_POSITION_' + str(morph_index)
        morph_normal_id = 'MORPH_NORMAL_' + str(morph_index)
        morph_tangent_id = 'MORPH_TANGENT_' + str(morph_index)

        if source_attributes.get(morph_position_id) is not None:
            attributes[morph_position_id] = []
            attributes[morph_normal_id] = []
            if use_tangents:
                attributes[morph_tangent_id] = []
            morph_index += 1
        else:
            process_morph = False

    morph_max = morph_index

    #

    min_index = min(indices)
    max_index = max(indices)

    for old_index in indices:
        result_primitive['indices'].append(old_index - min_index)

    for old_index in range(min_index, max_index + 1):
        for vi in range(0, 3):
            attributes['POSITION'].append(source_attributes['POSITION'][old_index * 3 + vi])
            attributes['NORMAL'].append(source_attributes['NORMAL'][old_index * 3 + vi])

        if use_tangents:
            for vi in range(0, 4):
                attributes['TANGENT'].append(source_attributes['TANGENT'][old_index * 4 + vi])

        for texcoord_index in range(0, texcoord_max):
            texcoord_id = 'TEXCOORD_' + str(texcoord_index)
            for vi in range(0, 2):
                attributes[texcoord_id].append(source_attributes[texcoord_id][old_index * 2 + vi])

        for color_index in range(0, color_max):
            color_id = 'COLOR_' + str(color_index)
            for vi in range(0, 4):
                attributes[color_id].append(source_attributes[color_id][old_index * 4 + vi])

        for bone_index in range(0, bone_max):
            joint_id = 'JOINTS_' + str(bone_index)
            weight_id = 'WEIGHTS_' + str(bone_index)
            for vi in range(0, 4):
                attributes[joint_id].append(source_attributes[joint_id][old_index * 4 + vi])
                attributes[weight_id].append(source_attributes[weight_id][old_index * 4 + vi])

        for morph_index in range(0, morph_max):
            morph_position_id = 'MORPH_POSITION_' + str(morph_index)
            morph_normal_id = 'MORPH_NORMAL_' + str(morph_index)
            morph_tangent_id = 'MORPH_TANGENT_' + str(morph_index)
            for vi in range(0, 3):
                attributes[morph_position_id].append(source_attributes[morph_position_id][old_index * 3 + vi])
                attributes[morph_normal_id].append(source_attributes[morph_normal_id][old_index * 3 + vi])
            if use_tangents:
                for vi in range(0, 4):
                    attributes[morph_tangent_id].append(source_attributes[morph_tangent_id][old_index * 4 + vi])

    return result_primitive


def extract_primitive_pack(a, indices, use_tangents):
    """
    Packs indices, that the first one starts with 0. Current indices can have gaps.
    """

    attributes = {
        'POSITION' : [],
        'NORMAL' : []
    }

    if use_tangents:
        attributes['TANGENT'] = []

    result_primitive = {
        'material' : a['material'],
        'useNodeAttrs' : a['useNodeAttrs'],
        'indices' : [],
        'attributes' : attributes
    }

    source_attributes = a['attributes']

    #

    texcoord_index = 0
    process_texcoord = True
    while process_texcoord:
        texcoord_id = 'TEXCOORD_' + str(texcoord_index)

        if source_attributes.get(texcoord_id) is not None:
            attributes[texcoord_id] = []
            texcoord_index += 1
        else:
            process_texcoord = False

    texcoord_max = texcoord_index

    #

    color_index = 0
    process_color = True
    while process_color:
        color_id = 'COLOR_' + str(color_index)

        if source_attributes.get(color_id) is not None:
            attributes[color_id] = []
            color_index += 1
        else:
            process_color = False

    color_max = color_index

    #

    bone_index = 0
    process_bone = True
    while process_bone:
        joint_id = 'JOINTS_' + str(bone_index)
        weight_id = 'WEIGHTS_' + str(bone_index)

        if source_attributes.get(joint_id) is not None:
            attributes[joint_id] = []
            attributes[weight_id] = []
            bone_index += 1
        else:
            process_bone = False

    bone_max = bone_index

    #

    morph_index = 0
    process_morph = True
    while process_morph:
        morph_position_id = 'MORPH_POSITION_' + str(morph_index)
        morph_normal_id = 'MORPH_NORMAL_' + str(morph_index)
        morph_tangent_id = 'MORPH_TANGENT_' + str(morph_index)

        if source_attributes.get(morph_position_id) is not None:
            attributes[morph_position_id] = []
            attributes[morph_normal_id] = []
            if use_tangents:
                attributes[morph_tangent_id] = []
            morph_index += 1
        else:
            process_morph = False

    morph_max = morph_index

    #

    old_to_new_indices = {}
    new_to_old_indices = {}

    new_index = 0
    for old_index in indices:
        if old_to_new_indices.get(old_index) is None:
            old_to_new_indices[old_index] = new_index
            new_to_old_indices[new_index] = old_index
            new_index += 1

        result_primitive['indices'].append(old_to_new_indices[old_index])

    end_new_index = new_index

    for new_index in range(0, end_new_index):
        old_index = new_to_old_indices[new_index]

        for vi in range(0, 3):
            attributes['POSITION'].append(source_attributes['POSITION'][old_index * 3 + vi])
            attributes['NORMAL'].append(source_attributes['NORMAL'][old_index * 3 + vi])

        if use_tangents:
            for vi in range(0, 4):
                attributes['TANGENT'].append(source_attributes['TANGENT'][old_index * 4 + vi])

        for texcoord_index in range(0, texcoord_max):
            texcoord_id = 'TEXCOORD_' + str(texcoord_index)
            for vi in range(0, 2):
                attributes[texcoord_id].append(source_attributes[texcoord_id][old_index * 2 + vi])

        for color_index in range(0, color_max):
            color_id = 'COLOR_' + str(color_index)
            for vi in range(0, 4):
                attributes[color_id].append(source_attributes[color_id][old_index * 4 + vi])

        for bone_index in range(0, bone_max):
            joint_id = 'JOINTS_' + str(bone_index)
            weight_id = 'WEIGHTS_' + str(bone_index)
            for vi in range(0, 4):
                attributes[joint_id].append(source_attributes[joint_id][old_index * 4 + vi])
                attributes[weight_id].append(source_attributes[weight_id][old_index * 4 + vi])

        for morph_index in range(0, morph_max):
            morph_position_id = 'MORPH_POSITION_' + str(morph_index)
            morph_normal_id = 'MORPH_NORMAL_' + str(morph_index)
            morph_tangent_id = 'MORPH_TANGENT_' + str(morph_index)
            for vi in range(0, 3):
                attributes[morph_position_id].append(source_attributes[morph_position_id][old_index * 3 + vi])
                attributes[morph_normal_id].append(source_attributes[morph_normal_id][old_index * 3 + vi])
            if use_tangents:
                for vi in range(0, 4):
                    attributes[morph_tangent_id].append(source_attributes[morph_tangent_id][old_index * 4 + vi])

    return result_primitive


def check_use_node_attrs(bl_mat):
    mat_type = get_material_type(bl_mat)

    if mat_type == 'NODE' or mat_type == 'CYCLES' or (mat_type == 'BASIC' and bpy.app.version < (2,80,0) and bl_mat.use_shadeless):
        return True
    else:
        return False

def extract_primitives(glTF, blender_mesh, blender_vertex_groups,
        blender_joint_indices, export_settings):
    """
    Extracting primitives from a mesh. Polygons are triangulated and sorted by material.
    Furthermore, primitives are splitted up, if the indices range is exceeded.
    Finally, triangles are also splitted up/dublicatted, if face normals are used instead of vertex normals.
    """

    need_skin_attributes = export_settings['gltf_skins'] and len(blender_joint_indices) > 0

    printLog('INFO', 'Extracting primitive')

    if blender_mesh.has_custom_normals:
        blender_mesh.calc_normals_split()

    use_tangents = False
    if blender_mesh.uv_layers.active and len(blender_mesh.uv_layers) > 0:
        try:
            blender_mesh.calc_tangents()
            use_tangents = True
        except:
            printLog('WARNING', 'Could not calculate tangents. Please try to triangulate the mesh first.')

    #
    # Gathering position, normal and texcoords.
    #
    primitive_attributes = {
        'POSITION' : [],
        'NORMAL' : []
    }
    if use_tangents:
        primitive_attributes['TANGENT'] = []

    def_mat_primitive = {
        'material' : DEFAULT_MAT_NAME,
        'useNodeAttrs' : False,
        'indices' : [],
        'attributes' : copy.deepcopy(primitive_attributes)
    }

    # NOTE: don't use a dictionary here, because if several slots have the same
    # material it leads to processing their corresponding geometry as a one
    # primitive thus making it a problem to assign separately different Object-linked
    # materials later
    material_primitives = []
    for bl_material in blender_mesh.materials:
        if bl_material is None:
            material_primitives.append(copy.deepcopy(def_mat_primitive))
        else:
            material_primitives.append({
                'material' : bl_material.name,
                'useNodeAttrs' : check_use_node_attrs(bl_material),
                'indices' : [],
                'attributes' : copy.deepcopy(primitive_attributes)
            })
    # explicitly add the default primitive for exceptional cases
    material_primitives.append(copy.deepcopy(def_mat_primitive))

    material_vertex_map = [{} for prim in material_primitives]


    texcoord_max = 0
    if blender_mesh.uv_layers.active:
        texcoord_max = len(blender_mesh.uv_layers)

    #

    vertex_colors = {}

    color_max = 0
    color_index = 0
    for vertex_color in blender_mesh.vertex_colors:
        vertex_color_name = 'COLOR_' + str(color_index)
        vertex_colors[vertex_color_name] = vertex_color

        color_index += 1
        if color_index >= GLTF_MAX_COLORS:
            break
    color_max = color_index

    #

    bone_max = 0
    if need_skin_attributes:
        for blender_polygon in blender_mesh.polygons:
            for loop_index in blender_polygon.loop_indices:
                vertex_index = blender_mesh.loops[loop_index].vertex_index

                # any vertex should be skinned to at least one bone - to the
                # armature itself if no groups are specified
                bones_count = max(len(blender_mesh.vertices[vertex_index].groups), 1)
                if bones_count % 4 == 0:
                    bones_count -= 1
                bone_max = max(bone_max, bones_count // 4 + 1)

    #

    morph_max = 0

    blender_shape_keys = []

    if blender_mesh.shape_keys is not None:
        morph_max = len(blender_mesh.shape_keys.key_blocks) - 1

        for blender_shape_key in blender_mesh.shape_keys.key_blocks:
            if blender_shape_key != blender_shape_key.relative_key:
                blender_shape_keys.append(blender_shape_key)

    #
    # Convert polygon to primitive indices and eliminate invalid ones. Assign to material.
    #

    bm_tri = bmesh.new()

    for blender_polygon in blender_mesh.polygons:

        if blender_polygon.material_index < 0 or blender_polygon.material_index >= len(blender_mesh.materials):
            # use default material
            primitive = material_primitives[-1]
            vertex_index_to_new_indices = material_vertex_map[-1]
        else:
            primitive = material_primitives[blender_polygon.material_index]
            vertex_index_to_new_indices = material_vertex_map[blender_polygon.material_index]

        export_color = primitive['material'] not in export_settings['gltf_use_no_color']

        attributes = primitive['attributes']

        face_normal = blender_polygon.normal
        face_tangent = mathutils.Vector((0.0, 0.0, 0.0))
        face_bitangent_sign = 1.0
        if use_tangents:
            for loop_index in blender_polygon.loop_indices:
                temp_vertex = blender_mesh.loops[loop_index]
                face_tangent += temp_vertex.tangent
                face_bitangent_sign = temp_vertex.bitangent_sign

            face_tangent.normalize()

        #

        indices = primitive['indices']

        loop_index_list = []



        if len(blender_polygon.loop_indices) == 3:
            loop_index_list.extend(blender_polygon.loop_indices)
        elif len(blender_polygon.loop_indices) > 3:
            # Triangulation of polygon. Using internal function, as non-convex polygons could exist.

            if bpy.app.version < (2,80,0):
                bm_tri.clear()

                for loop_index in blender_polygon.loop_indices:
                    vertex_index = blender_mesh.loops[loop_index].vertex_index
                    bm_tri.verts.new(blender_mesh.vertices[vertex_index].co)
                bm_tri.faces.new(bm_tri.verts)

                bm_tri.normal_update()
                bm_tri.verts.index_update()
                bm_tri.edges.index_update()
                bm_tri.faces.index_update()

                # use calc_tessafce instead of mathutils.geometry.tessellate_polygon
                # because the latter can produce incorrect results in some specific cases
                face_tuples = bm_tri.calc_tessface()
                for ft in face_tuples:
                    loop_index_list.append(blender_polygon.loop_indices[ft[0].vert.index])
                    loop_index_list.append(blender_polygon.loop_indices[ft[1].vert.index])
                    loop_index_list.append(blender_polygon.loop_indices[ft[2].vert.index])
            else:
                # old method, using it since bmesh.calc_tessface() was removed
                polyline = []

                for loop_index in blender_polygon.loop_indices:
                    vertex_index = blender_mesh.loops[loop_index].vertex_index
                    v = blender_mesh.vertices[vertex_index].co
                    polyline.append(mathutils.Vector((v[0], v[1], v[2])))

                triangles = mathutils.geometry.tessellate_polygon((polyline,))

                for triangle in triangles:
                    loop_index_list.append(blender_polygon.loop_indices[triangle[0]])
                    loop_index_list.append(blender_polygon.loop_indices[triangle[2]])
                    loop_index_list.append(blender_polygon.loop_indices[triangle[1]])

        else:
            continue

        for loop_index in loop_index_list:
            vertex_index = blender_mesh.loops[loop_index].vertex_index

            if vertex_index_to_new_indices.get(vertex_index) is None:
                vertex_index_to_new_indices[vertex_index] = []

            #

            v = None
            n = None
            t = None
            uvs = []
            colors = []
            joints = []
            weights = []

            target_positions = []
            target_normals = []
            target_tangents = []

            vertex = blender_mesh.vertices[vertex_index]

            v = convert_swizzle_location(vertex.co)
            if blender_polygon.use_smooth:

                if blender_mesh.has_custom_normals:
                    n = convert_swizzle_location(blender_mesh.loops[loop_index].normal)
                else:
                    n = convert_swizzle_location(vertex.normal)
                if use_tangents:
                    t = convert_swizzle_tangent(blender_mesh.loops[loop_index].tangent, blender_mesh.loops[loop_index].bitangent_sign)
            else:
                n = convert_swizzle_location(face_normal)
                if use_tangents:
                    t = convert_swizzle_tangent(face_tangent, face_bitangent_sign)

            if blender_mesh.uv_layers.active:
                for texcoord_index in range(0, texcoord_max):
                    uv = blender_mesh.uv_layers[texcoord_index].data[loop_index].uv
                    # NOTE: to comply with glTF spec [0,0] upper left angle
                    uvs.append([uv.x, 1.0 - uv.y])

            #

            if color_max > 0 and export_color:
                for color_index in range(0, color_max):
                    color_name = 'COLOR_' + str(color_index)
                    color = vertex_colors[color_name].data[loop_index].color
                    colors.append([color[0], color[1], color[2], 1.0])

            #

            if need_skin_attributes:

                bone_count = 0

                if vertex.groups is not None and len(vertex.groups) > 0:
                    joint = []
                    weight = []
                    for group_element in vertex.groups:

                        if len(joint) == 4:
                            bone_count += 1
                            joints.append(joint)
                            weights.append(weight)
                            joint = []
                            weight = []

                        #

                        vertex_group_index = group_element.group

                        vertex_group_name = blender_vertex_groups[vertex_group_index].name

                        #

                        joint_index = 0
                        joint_weight = 0.0

                        if blender_joint_indices.get(vertex_group_name) is not None:
                            joint_index = blender_joint_indices[vertex_group_name]
                            joint_weight = group_element.weight

                        #

                        joint.append(joint_index)
                        weight.append(joint_weight)

                    if len(joint) > 0:
                        bone_count += 1

                        for fill in range(0, 4 - len(joint)):
                            joint.append(0)
                            weight.append(0.0)

                        joints.append(joint)
                        weights.append(weight)

                for fill in range(0, bone_max - bone_count):
                    joints.append([0, 0, 0, 0])
                    weights.append([0.0, 0.0, 0.0, 0.0])

                #

                # use the armature (the last joint) with the unity weight
                # if no joints influence a vertex
                weight_sum = 0
                for bone_index in range(0, bone_max):
                    weight_sum += sum(weights[bone_index])

                if weight_sum == 0:
                    joints = [[0, 0, 0, 0] for i in range(0, bone_max)]
                    weights = [[0, 0, 0, 0] for i in range(0, bone_max)]

                    # there will be a joint representing the armature itself,
                    # which will be placed at the end of the joint list in the glTF data
                    joints[0][0] = len(blender_joint_indices)
                    weights[0][0] = 1.0


            if morph_max > 0 and export_settings['gltf_morph']:
                for morph_index in range(0, morph_max):
                    blender_shape_key = blender_shape_keys[morph_index]

                    v_morph = convert_swizzle_location(blender_shape_key.data[vertex_index].co)

                    # Store delta.
                    v_morph -= v

                    target_positions.append(v_morph)

                    #

                    n_morph = None

                    if blender_polygon.use_smooth:
                        temp_normals = blender_shape_key.normals_vertex_get()
                        n_morph = (temp_normals[vertex_index * 3 + 0], temp_normals[vertex_index * 3 + 1], temp_normals[vertex_index * 3 + 2])
                    else:
                        temp_normals = blender_shape_key.normals_polygon_get()
                        n_morph = (temp_normals[blender_polygon.index * 3 + 0], temp_normals[blender_polygon.index * 3 + 1], temp_normals[blender_polygon.index * 3 + 2])

                    n_morph = convert_swizzle_location(n_morph)

                    # Store delta.
                    n_morph -= n

                    target_normals.append(n_morph)

                    #

                    if use_tangents:
                        rotation = n_morph.rotation_difference(n)

                        t_morph = mathutils.Vector((t[0], t[1], t[2]))

                        t_morph.rotate(rotation)

                        target_tangents.append(t_morph)

            #
            #

            create = True

            for current_new_index in vertex_index_to_new_indices[vertex_index]:
                found = True

                for i in range(0, 3):
                    if attributes['POSITION'][current_new_index * 3 + i] != v[i]:
                        found = False
                        break

                    if attributes['NORMAL'][current_new_index * 3 + i] != n[i]:
                        found = False
                        break

                if use_tangents:
                    for i in range(0, 4):
                        if attributes['TANGENT'][current_new_index * 4 + i] != t[i]:
                            found = False
                            break

                if not found:
                    continue

                for texcoord_index in range(0, texcoord_max):
                    uv = uvs[texcoord_index]

                    texcoord_id = 'TEXCOORD_' + str(texcoord_index)
                    for i in range(0, 2):
                        if attributes[texcoord_id][current_new_index * 2 + i] != uv[i]:
                            found = False
                            break

                if export_color:
                    for color_index in range(0, color_max):
                        color = colors[color_index]

                        color_id = 'COLOR_' + str(color_index)
                        for i in range(0, 3):
                            # Alpha is always 1.0 - see above.
                            if attributes[color_id][current_new_index * 4 + i] != color[i]:
                                found = False
                                break

                if need_skin_attributes:
                    for bone_index in range(0, bone_max):
                        joint = joints[bone_index]
                        weight = weights[bone_index]

                        joint_id = 'JOINTS_' + str(bone_index)
                        weight_id = 'WEIGHTS_' + str(bone_index)
                        for i in range(0, 4):
                            if attributes[joint_id][current_new_index * 4 + i] != joint[i]:
                                found = False
                                break
                            if attributes[weight_id][current_new_index * 4 + i] != weight[i]:
                                found = False
                                break

                if export_settings['gltf_morph']:
                    for morph_index in range(0, morph_max):
                        target_position = target_positions[morph_index]
                        target_normal = target_normals[morph_index]
                        if use_tangents:
                            target_tangent = target_tangents[morph_index]

                        target_position_id = 'MORPH_POSITION_' + str(morph_index)
                        target_normal_id = 'MORPH_NORMAL_' + str(morph_index)
                        target_tangent_id = 'MORPH_TANGENT_' + str(morph_index)
                        for i in range(0, 3):
                            if attributes[target_position_id][current_new_index * 3 + i] != target_position[i]:
                                found = False
                                break
                            if attributes[target_normal_id][current_new_index * 3 + i] != target_normal[i]:
                                found = False
                                break
                            if use_tangents:
                                if attributes[target_tangent_id][current_new_index * 3 + i] != target_tangent[i]:
                                    found = False
                                    break

                if found:
                    indices.append(current_new_index)

                    create = False
                    break

            if not create:
                continue

            new_index = 0

            if primitive.get('max_index') is not None:
                new_index = primitive['max_index'] + 1

            primitive['max_index'] = new_index

            vertex_index_to_new_indices[vertex_index].append(new_index)

            #
            #

            indices.append(new_index)

            #

            attributes['POSITION'].extend(v)
            attributes['NORMAL'].extend(n)
            if use_tangents:
                attributes['TANGENT'].extend(t)

            if blender_mesh.uv_layers.active:
                for texcoord_index in range(0, texcoord_max):
                    texcoord_id = 'TEXCOORD_' + str(texcoord_index)

                    if attributes.get(texcoord_id) is None:
                        attributes[texcoord_id] = []

                    attributes[texcoord_id].extend(uvs[texcoord_index])

            if export_color:
                for color_index in range(0, color_max):
                    color_id = 'COLOR_' + str(color_index)

                    if attributes.get(color_id) is None:
                        attributes[color_id] = []

                    attributes[color_id].extend(colors[color_index])

            if need_skin_attributes:
                for bone_index in range(0, bone_max):
                    joint_id = 'JOINTS_' + str(bone_index)

                    if attributes.get(joint_id) is None:
                        attributes[joint_id] = []

                    attributes[joint_id].extend(joints[bone_index])

                    weight_id = 'WEIGHTS_' + str(bone_index)

                    if attributes.get(weight_id) is None:
                        attributes[weight_id] = []

                    attributes[weight_id].extend(weights[bone_index])

            if export_settings['gltf_morph']:
                for morph_index in range(0, morph_max):
                    target_position_id = 'MORPH_POSITION_' + str(morph_index)

                    if attributes.get(target_position_id) is None:
                        attributes[target_position_id] = []

                    attributes[target_position_id].extend(target_positions[morph_index])

                    target_normal_id = 'MORPH_NORMAL_' + str(morph_index)

                    if attributes.get(target_normal_id) is None:
                        attributes[target_normal_id] = []

                    attributes[target_normal_id].extend(target_normals[morph_index])

                    if use_tangents:
                        target_tangent_id = 'MORPH_TANGENT_' + str(morph_index)

                        if attributes.get(target_tangent_id) is None:
                            attributes[target_tangent_id] = []

                        attributes[target_tangent_id].extend(target_tangents[morph_index])

    bm_tri.free()

    #
    # Add primitive plus split them if needed.
    #

    result_primitives = []

    for primitive in material_primitives:
        export_color = True
        if primitive['material'] in export_settings['gltf_use_no_color']:
            export_color = False

        #

        indices = primitive['indices']

        if len(indices) == 0:
            continue

        position = primitive['attributes']['POSITION']
        normal = primitive['attributes']['NORMAL']
        if use_tangents:
            tangent = primitive['attributes']['TANGENT']
        texcoords = []
        for texcoord_index in range(0, texcoord_max):
            texcoords.append(primitive['attributes']['TEXCOORD_' + str(texcoord_index)])
        colors = []
        if export_color:
            for color_index in range(0, color_max):
                texcoords.append(primitive['attributes']['COLOR_' + str(color_index)])
        joints = []
        weights = []
        if need_skin_attributes:
            for bone_index in range(0, bone_max):
                joints.append(primitive['attributes']['JOINTS_' + str(bone_index)])
                weights.append(primitive['attributes']['WEIGHTS_' + str(bone_index)])

        target_positions = []
        target_normals = []
        target_tangents = []
        if export_settings['gltf_morph']:
            for morph_index in range(0, morph_max):
                target_positions.append(primitive['attributes']['MORPH_POSITION_' + str(morph_index)])
                target_normals.append(primitive['attributes']['MORPH_NORMAL_' + str(morph_index)])
                if use_tangents:
                    target_tangents.append(primitive['attributes']['MORPH_TANGENT_' + str(morph_index)])

        #

        count = len(indices)

        if count == 0:
            continue

        max_index = max(indices)

        #

        range_indices = 65536
        if export_settings['gltf_indices'] == 'UNSIGNED_BYTE':
            range_indices = 256
        elif export_settings['gltf_indices'] == 'UNSIGNED_INT':
            range_indices = 4294967296

        #

        if max_index >= range_indices:
            #
            # Spliting result_primitives.
            #

            # At start, all indicees are pending.
            pending_attributes = {
                'POSITION' : [],
                'NORMAL' : []
            }

            if use_tangents:
                pending_attributes['TANGENT'] = []

            pending_primitive = {
                'material' : primitive['material'],
                'useNodeAttrs' : primitive['useNodeAttrs'],
                'indices' : [],
                'attributes' : pending_attributes
            }

            pending_primitive['indices'].extend(indices)


            pending_attributes['POSITION'].extend(position)
            pending_attributes['NORMAL'].extend(normal)
            if use_tangents:
                pending_attributes['TANGENT'].extend(tangent)
            texcoord_index = 0
            for texcoord in texcoords:
                pending_attributes['TEXCOORD_' + str(texcoord_index)] = texcoord
                texcoord_index += 1
            if export_color:
                color_index = 0
                for color in colors:
                    pending_attributes['COLOR_' + str(color_index)] = color
                    color_index += 1
            if need_skin_attributes:
                joint_index = 0
                for joint in joints:
                    pending_attributes['JOINTS_' + str(joint_index)] = joint
                    joint_index += 1
                weight_index = 0
                for weight in weights:
                    pending_attributes['WEIGHTS_' + str(weight_index)] = weight
                    weight_index += 1
            if export_settings['gltf_morph']:
                morph_index = 0
                for target_position in target_positions:
                    pending_attributes['MORPH_POSITION_' + str(morph_index)] = target_position
                    morph_index += 1
                morph_index = 0
                for target_normal in target_normals:
                    pending_attributes['MORPH_NORMAL_' + str(morph_index)] = target_normal
                    morph_index += 1
                if use_tangents:
                    morph_index = 0
                    for target_tangent in target_tangents:
                        pending_attributes['MORPH_TANGENT_' + str(morph_index)] = target_tangent
                        morph_index += 1

            pending_indices = pending_primitive['indices']

            # Continue until all are processed.
            while len(pending_indices) > 0:

                process_indices = pending_primitive['indices']

                pending_indices = []

                #
                #

                all_local_indices = []

                for i in range(0, (max(process_indices) // range_indices) + 1):
                    all_local_indices.append([])

                #
                #

                # For all faces ...
                for face_index in range(0, len(process_indices), 3):

                    written = False

                    face_min_index = min(process_indices[face_index + 0], process_indices[face_index + 1], process_indices[face_index + 2])
                    face_max_index = max(process_indices[face_index + 0], process_indices[face_index + 1], process_indices[face_index + 2])

                    # ... check if it can be but in a range of maximum indices.
                    for i in range(0, (max(process_indices) // range_indices) + 1):
                        offset = i * range_indices

                        # Yes, so store the primitive with its indices.
                        if face_min_index >= offset and face_max_index < offset + range_indices:
                            all_local_indices[i].extend([process_indices[face_index + 0], process_indices[face_index + 1], process_indices[face_index + 2]])

                            written = True
                            break

                    # If not written, the triangel face has indices from different ranges.
                    if not written:
                        pending_indices.extend([process_indices[face_index + 0], process_indices[face_index + 1], process_indices[face_index + 2]])

                # Only add result_primitives, which do have indices in it.
                for local_indices in all_local_indices:
                    if len(local_indices) > 0:
                        current_primitive = extract_primitive_floor(pending_primitive, local_indices, use_tangents)

                        result_primitives.append(current_primitive)

                        printLog('DEBUG', 'Adding primitive with splitting. Indices: ' + str(len(current_primitive['indices'])) + ' Vertices: ' + str(len(current_primitive['attributes']['POSITION']) // 3))

                # Process primitive faces having indices in several ranges.
                if len(pending_indices) > 0:
                    pending_primitive = extract_primitive_pack(pending_primitive, pending_indices, use_tangents)

                    pending_attributes = pending_primitive['attributes']

                    printLog('DEBUG', 'Creating temporary primitive for splitting')

        else:
            #
            # No splitting needed.
            #
            result_primitives.append(primitive)

            printLog('DEBUG', 'Adding primitive without splitting. Indices: ' + str(len(primitive['indices'])) + ' Vertices: ' + str(len(primitive['attributes']['POSITION']) // 3))

    printLog('INFO', 'Primitives created: ' + str(len(result_primitives)))

    return result_primitives


def extract_line_primitives(glTF, blender_mesh, export_settings):
    """
    Extracting line primitives from a mesh.
    Furthermore, primitives are splitted up, if the indices range is exceeded.
    """

    printLog('INFO', 'Extracting line primitive')

    # material property currently isn't used for line meshes in the engine
    mat_name = (blender_mesh.materials[0].name if blender_mesh.materials
            and blender_mesh.materials[0] is not None else '')

    primitive = {
        'material' : mat_name,
        'useNodeAttrs' : False,
        'indices' : [],
        'attributes' : { 'POSITION': [] }
    }

    orig_indices = primitive['indices']
    orig_positions = primitive['attributes']['POSITION']

    vertex_index_to_new_index = {}

    for blender_edge in blender_mesh.edges:
        for vertex_index in blender_edge.vertices:
            vertex = blender_mesh.vertices[vertex_index]

            new_index = vertex_index_to_new_index.get(vertex_index, -1)
            if new_index == -1:
                orig_positions.extend(convert_swizzle_location(vertex.co))
                new_index = len(orig_positions) // 3 - 1
                vertex_index_to_new_index[vertex_index] = new_index

            orig_indices.append(new_index)


    result_primitives = []

    range_indices = 65536
    if export_settings['gltf_indices'] == 'UNSIGNED_BYTE':
        range_indices = 256
    elif export_settings['gltf_indices'] == 'UNSIGNED_INT':
        range_indices = 4294967296

    if len(set(orig_indices)) >= range_indices:
        # Splitting the bunch of a primitive's edges into several parts.
        split_parts = []

        # Process every edge.
        for i in range(0, len(orig_indices), 2):
            edge = orig_indices[i:i+2]

            part_count = len(split_parts)
            part_suitabilities = [0]*part_count

            # Define which split_part is more suitable for a particular edge.
            # The best case is when the both edge indices are already contained
            # in a split_part, so we won't increase the number of the part's
            # unique indices by adding the edge into it.
            for i in range(0, part_count):
                if edge[0] in split_parts[i]:
                    part_suitabilities[i] += 1
                if edge[1] in split_parts[i]:
                    part_suitabilities[i] += 1

            # Sort split_parts by their suitability, e.g. 2,1,1,1,0,0.
            split_part_order = sorted(range(part_count),
                    key=lambda i: part_suitabilities[i], reverse=True)

            # Trying to find the first most suitable split_part with free space.
            need_new_part = True
            for i in split_part_order:
                if len(set(split_parts[i] + edge)) <= range_indices:
                    split_parts[i].extend(edge)
                    need_new_part = False
                    break

            # Create new split_part if no existed part can contain an edge.
            if need_new_part:
                split_parts.append(edge)

        # Create new primitives based on the calculated split_parts.
        for old_indices in split_parts:

            part_primitive = {
                'material' : mat_name,
                'useNodeAttrs' : False,
                'indices' : [],
                'attributes' : { 'POSITION': [] }
            }

            sorted_indices = sorted(set(old_indices))
            for i in sorted_indices:
                part_primitive['attributes']['POSITION'].extend(orig_positions[i*3:i*3+3])

            part_primitive['indices'] = [sorted_indices.index(i) for i in old_indices]

            result_primitives.append(part_primitive)

    else:
        # No splitting needed.
        result_primitives.append(primitive)

    return result_primitives

def extract_vec(vec):
    return [i for i in vec]

def extract_mat(mat):
    """
    Return matrix in glTF column-major order
    """
    return [mat[0][0], mat[1][0], mat[2][0], mat[3][0],
            mat[0][1], mat[1][1], mat[2][1], mat[3][1],
            mat[0][2], mat[1][2], mat[2][2], mat[3][2],
            mat[0][3], mat[1][3], mat[2][3], mat[3][3]]

def extract_node_graph(node_tree, export_settings, glTF):

    nodes = []
    edges = []

    bl_nodes = node_tree.nodes

    for bl_node in bl_nodes:
        node = {
            'name': bl_node.name,
            'type': bl_node.type
        }

        nodes.append(node);

        if bl_node.type == 'ATTRIBUTE':
            # rename for uniformity with GEOMETRY node
            node['colorLayer'] = bl_node.attribute_name

        elif bl_node.type == 'BSDF_REFRACTION':
            node['distribution'] = bl_node.distribution

        elif bl_node.type == 'BUMP':
            node['invert'] = bl_node.invert
        elif bl_node.type == 'CURVE_RGB':
            node['curveData'] = extract_curve_mapping(bl_node.mapping, (0,1))
        elif bl_node.type == 'CURVE_VEC':
            node['curveData'] = extract_curve_mapping(bl_node.mapping, (-1,1))

        elif bl_node.type == 'GEOMETRY':
            # reproducing ShaderNodeGeometry
            # https://docs.blender.org/api/current/bpy.types.ShaderNodeGeometry.html

            node['colorLayer'] = bl_node.color_layer
            node['uvLayer'] = bl_node.uv_layer

        elif bl_node.type == 'GROUP':
            node['nodeGraph'] = get_node_graph_index(glTF,
                    bl_node.node_tree.name)

        elif bl_node.type == 'LAMP':
            # TODO
            pass

        elif bl_node.type == 'MAPPING':
            # reproducing ShaderNodeMapping
            # https://docs.blender.org/api/current/bpy.types.ShaderNodeMapping.html

            node['rotation'] = extract_vec(bl_node.rotation)
            node['scale'] = extract_vec(bl_node.scale)
            node['translation'] = extract_vec(bl_node.translation)

            node['max'] = extract_vec(bl_node.max)
            node['min'] = extract_vec(bl_node.min)

            node['useMax'] = bl_node.use_max
            node['useMin'] = bl_node.use_min

            node['vectorType'] = bl_node.vector_type

        elif bl_node.type == 'MATERIAL' or bl_node.type == 'MATERIAL_EXT':
            # reproducing ShaderNodeMaterial
            # https://docs.blender.org/api/current/bpy.types.ShaderNodeMaterial.html

            mat = bl_node.material

            if mat:
                node['materialName'] = mat.name

                node['specularIntensity'] = mat.specular_intensity
                node['specularHardness'] = mat.specular_hardness

                node['useShadeless'] = mat.use_shadeless

                # encoded inside inputs in MATERIAL_EXT:
                if bl_node.type == 'MATERIAL':
                    node['ambient'] = mat.ambient
                    node['emit'] = mat.emit
                    node['alpha'] = mat.alpha
                    # specularAlpha for simple material node is not supported in Blender
            else:
                printLog('ERROR', 'No material in node')

            node['useDiffuse'] = bl_node.use_diffuse
            node['useSpecular'] = bl_node.use_specular
            node['invertNormal'] = bl_node.invert_normal

        elif bl_node.type == 'MATH':
            # reproducing ShaderNodeMath
            # https://docs.blender.org/api/current/bpy.types.ShaderNodeMath.html

            node['operation'] = bl_node.operation
            node['useClamp'] = bl_node.use_clamp

        elif bl_node.type == 'MIX_RGB':
            # reproducing ShaderNodeMixRGB
            # https://docs.blender.org/api/current/bpy.types.ShaderNodeMixRGB.html

            node['blendType'] = bl_node.blend_type
            node['useClamp'] = bl_node.use_clamp

        elif bl_node.type == 'NORMAL_MAP' or bl_node.type == 'UVMAP':
            # rename for uniformity with GEOMETRY node
            node['uvLayer'] = bl_node.uv_map

        elif bl_node.type == 'TEX_ENVIRONMENT':
            index = get_texture_index(glTF, get_texture_name(bl_node)) if get_tex_image(bl_node) else -1

            if index == -1:
                node['type'] = 'TEX_ENVIRONMENT_NONE'
            else:
                node['texture'] = index

        elif bl_node.type == 'TEX_IMAGE':
            index = get_texture_index(glTF, get_texture_name(bl_node)) if get_tex_image(bl_node) else -1

            if index == -1:
                node['type'] = 'TEX_IMAGE_NONE'
            else:
                node['texture'] = index

        elif bl_node.type == 'TEX_GRADIENT':
            node['gradientType'] = bl_node.gradient_type

        elif bl_node.type == 'TEX_NOISE':
            node['falloffFactor'] = bl_node.v3d.falloff_factor
            node['dispersionFactor'] = bl_node.v3d.dispersion_factor

        elif bl_node.type == 'TEX_SKY':
            node['skyType'] = bl_node.sky_type
            node['sunDirection'] = extract_vec(bl_node.sun_direction)
            node['turbidity'] = bl_node.turbidity
            node['groundAlbedo'] = bl_node.ground_albedo

        elif bl_node.type == 'TEX_VORONOI':
            node['coloring'] = bl_node.coloring
            if bpy.app.version < (2, 80, 0):
                # backwards compatibility for old 2.79b builds without the 'distance'
                # and 'feature' parameters
                node['distance'] = bl_node.distance if hasattr(bl_node, 'distance') else 'DISTANCE'
                node['feature'] = bl_node.feature if hasattr(bl_node, 'feature') else 'F1'
            else:
                node['distance'] = bl_node.distance
                node['feature'] = bl_node.feature

        elif bl_node.type == 'TEX_WAVE':
            node['waveType'] = bl_node.wave_type
            node['waveProfile'] = bl_node.wave_profile

        elif bl_node.type == 'TEXTURE':
            # NOTE: using get_texture_index_by_texture() may result in wrong colorSpace if the texture is shared
            # need to find out possible side effects when using this function
            index = get_texture_index(glTF, get_texture_name(bl_node.texture)) if bl_node.texture else -1

            if index == -1:
                node['type'] = 'TEXTURE_NONE'
            else:
                node['texture'] = index

        elif bl_node.type == 'VALTORGB':
            node['curve'] = extract_color_ramp(bl_node.color_ramp)

        elif bl_node.type == 'VECT_MATH':
            node['operation'] = bl_node.operation

        elif bl_node.type == 'VECT_TRANSFORM':
            # reproducing ShaderNodeVectorTransform
            # https://docs.blender.org/api/current/bpy.types.ShaderNodeVectorTransform.html

            node['vectorType'] = bl_node.vector_type
            node['convertFrom'] = bl_node.convert_from
            node['convertTo'] = bl_node.convert_to

        node['inputs'] = []
        for bl_input in bl_node.inputs:
            bl_inp_type = bl_input.rna_type.identifier
            if (bl_inp_type == 'NodeSocketColor' or
                    bl_inp_type == 'NodeSocketVector' or
                    bl_inp_type == 'NodeSocketVectorDirection'):
                node['inputs'].append(extract_vec(bl_input.default_value))
            elif bl_inp_type == 'NodeSocketVirtual':
                # NOTE: last in the list should be safe to omit it
                pass
            elif bl_inp_type == 'NodeSocketShader':
                # Cycles shader has no default value
                node['inputs'].append([0, 0, 0, 0])
            else:
                # NOTE: the roughness value for the Glossy BSDF node is squared
                # prior to 2.80
                if (bpy.app.version < (2, 80, 0) and bl_node.type == 'BSDF_GLOSSY'
                        and bl_input.identifier == 'Roughness'):
                    node['inputs'].append(math.sqrt(bl_input.default_value))
                else:
                    node['inputs'].append(bl_input.default_value)

        if bpy.app.version < (2, 80, 0):
            # backwards compatibility for old 2.79b builds without the hidden
            # 'exponent' input
            if bl_node.type == 'TEX_VORONOI' and len(bl_node.inputs) == 2:
                node['inputs'].append(0.5)

        node['outputs'] = []
        for bl_output in bl_node.outputs:
            bl_out_type = bl_output.rna_type.identifier
            if (bl_out_type == 'NodeSocketColor' or
                    bl_out_type == 'NodeSocketVector' or
                    bl_out_type == 'NodeSocketVectorDirection'):
                node['outputs'].append(extract_vec(bl_output.default_value))
            elif bl_out_type == 'NodeSocketVirtual':
                # NOTE: last in the list should be safe to omit it
                pass
            elif bl_out_type == 'NodeSocketShader':
                # Cycles shader has no default value
                node['outputs'].append([0, 0, 0, 0])
            else:
                node['outputs'].append(bl_output.default_value)

        # "is_active_output" exists on both tree outputs and group outputs
        node["is_active_output"] = (hasattr(bl_node, "is_active_output")
                and bl_node.is_active_output)


    for bl_link in node_tree.links:
        if not bl_link.is_valid:
            printLog('ERROR', 'Invalid edge')
            continue

        # indices
        from_node = bl_nodes.find(bl_link.from_node.name)
        to_node = bl_nodes.find(bl_link.to_node.name)

        if from_node < 0 or to_node < 0:
            printLog('ERROR', 'Invalid edge connection')
            continue

        edge = {
            'fromNode' : from_node,
            'fromOutput' : find_node_socket_num(bl_nodes[from_node].outputs,
                    bl_link.from_socket.identifier),

            'toNode' : to_node,
            'toInput' : find_node_socket_num(bl_nodes[to_node].inputs,
                    bl_link.to_socket.identifier)
        }

        edges.append(edge)

    return { 'nodes' : nodes, 'edges' : edges }


def extract_curve_mapping(mapping, x_range):
    """Extract curve points data from CurveMapping data"""

    mapping.initialize()

    data = []

    # first pixel = x_range[0], last pixel = x_range[1]
    pix_size = (x_range[1] - x_range[0]) / (CURVE_DATA_SIZE - 1)

    for i in range(CURVE_DATA_SIZE):

        x = x_range[0] + pix_size * i

        for curve_map in mapping.curves:
            data.append(curve_map.evaluate(x))

    return data

def extract_color_ramp(color_ramp):
    """Make a curve from color ramp data"""

    # for uniformity looks like a glTF animation sampler
    curve = {
        'input' : [],
        'output' : [],
        'interpolation' : 'LINEAR'
    }

    for e in color_ramp.elements:
        curve['input'].append(e.position)

        for i in range(4):
            curve['output'].append(e.color[i])

    return curve

def find_node_socket_num(socket_list, identifier):
    for i in range(len(socket_list)):
        sock = socket_list[i]
        if sock.identifier == identifier:
            return i
    return -1

def composeNodeGraph(bl_mat, export_settings, glTF):

    graph = { 'nodes' : [], 'edges' : [] }

    if bpy.app.version < (2,80,0):
        appendNode(graph, {
            'name': 'Output',
            'type': 'OUTPUT',
            'inputs': [
                [1,1,1,1],
                1,
            ],
            'outputs': [],
            'is_active_output': True
        })

        appendNode(graph, {
            'name': 'Material',
            'type': 'MATERIAL_EXT',
            'materialName': 'Material',
            'useDiffuse': True,
            'useSpecular': True,
            'invertNormal': False,
            'specularHardness': bl_mat.specular_hardness,
            'specularIntensity': bl_mat.specular_intensity,
            'useShadeless': bl_mat.use_shadeless,
            'inputs': [
                extract_vec(bl_mat.diffuse_color) + [1],
                extract_vec(bl_mat.specular_color) + [1],
                bl_mat.diffuse_intensity,
                [0, 0, 0],
                [0, 0, 0, 0],
                bl_mat.ambient,
                bl_mat.emit,
                bl_mat.specular_alpha,
                0,
                bl_mat.alpha,
                0
            ],
            'outputs': [
                [0, 0, 0, 0],
                0,
                [0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        }, 0, [(0, 0), (1, 1)])

        texNodes = []

        for bl_tex_slot in bl_mat.texture_slots:
            if (bl_tex_slot and bl_tex_slot.texture and
                bl_tex_slot.texture.type == 'IMAGE' and
                get_tex_image(bl_tex_slot.texture) is not None):

                blendType = bl_tex_slot.blend_type

                # Diffuse texture

                if bl_tex_slot.use_map_color_diffuse:
                    index = get_texture_index_by_texture(export_settings,
                            glTF, bl_tex_slot.texture)
                    if index >= 0:
                        mixIdx = appendMixRGBNode(graph, 'DiffuseMix', blendType,
                                bl_tex_slot.diffuse_color_factor, 1, (0,0))
                        texNodes.append(appendTextureNode(graph, 'Diffuse', index, mixIdx, [(1,2)]))

                # Alpha texture

                if bl_tex_slot.use_map_alpha:
                    index = get_texture_index_by_texture(export_settings,
                            glTF, bl_tex_slot.texture)
                    if index >= 0:
                        mixIdx = appendMixRGBNode(graph, 'AlphaMix', blendType,
                                bl_tex_slot.alpha_factor, 1, (0,9))
                        texNodes.append(appendTextureNode(graph, 'Alpha', index, mixIdx, [(1,2)]))

                # Specular intensity texture
                # NOTE: this one connected as color but interpreted as intensity
                if bl_tex_slot.use_map_color_spec:
                    index = get_texture_index_by_texture(export_settings,
                            glTF, bl_tex_slot.texture)
                    if index >= 0:
                        mixIdx = appendMixRGBNode(graph, 'SpecularMix', blendType,
                                bl_tex_slot.specular_color_factor, 1, (0,1))
                        texNodes.append(appendTextureNode(graph, 'Specular', index, mixIdx, [(1,2)]))

                # Emissive texture

                if bl_tex_slot.use_map_emit:
                    index = get_texture_index_by_texture(export_settings,
                            glTF, bl_tex_slot.texture)
                    if index >= 0:
                        mixIdx = appendMixRGBNode(graph, 'EmissiveMix', blendType,
                                bl_tex_slot.emit_factor, 1, (0,6))
                        texNodes.append(appendTextureNode(graph, 'Emissive', index, mixIdx, [(1,2)]))

                # Normal texture

                if bl_tex_slot.use_map_normal:
                    index = get_texture_index_by_texture(export_settings,
                            glTF, bl_tex_slot.texture)
                    if index >= 0:
                        normalIdx = appendNode(graph, {
                            'name': 'NormalMap',
                            'type': 'NORMAL_MAP',
                            'uvLayer': '',
                            'inputs': [
                                1,
                                [1,1,1,1],
                            ],
                            'outputs': [[1,1,1]],
                        }, 1, [(0,3)])

                        texNodes.append(appendTextureNode(graph, 'NormalTex', index, normalIdx, [(1,1)]))

        geometry = {
            'name': 'Geometry',
            'type': 'GEOMETRY',
            'uvLayer': '',
            'colorLayer': '',
            'inputs': [],
            'outputs': [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0,0], 0, 0]
        }

        # connect geometry node
        for idx in texNodes:
            appendNode(graph, geometry, idx, [(4, 0)])

    else: # blender 2.80

        appendNode(graph, {
            'name': 'Output',
            'type': 'OUTPUT_MATERIAL',
            'inputs': [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0]
            ],
            'outputs': [],
            'is_active_output': True
        })

        # backwards compatibility with old blender 2.80 beta builds
        diff_color = extract_vec(bl_mat.diffuse_color)
        if len(diff_color) == 3:
            diff_color += [1]

        appendNode(graph, {
            'name': 'Principled',
            'type': 'BSDF_PRINCIPLED',
            'inputs': [
                diff_color,
                0.0,
                [1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 1.0],
                bl_mat.metallic,
                bl_mat.specular_intensity,
                0.0,
                bl_mat.roughness,
                0.0,
                0.0,
                0.0,
                0.5,
                0.0,
                0.03,
                1.45,
                0.0,
                0.0,
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0]
            ],
            'outputs': [[0, 0, 0, 0]]
        }, 0)

    return graph

def appendNode(nodeGraph, node, toNode=-1, connections=[(0, 0)]):

    if node not in nodeGraph['nodes']:
        nodeGraph['nodes'].append(node)

    nodeIndex = nodeGraph['nodes'].index(node)

    if toNode > -1:
        for conn in connections:
            nodeGraph['edges'].append({
                'fromNode' : nodeIndex,
                'fromOutput' : conn[0],
                'toNode' : toNode,
                'toInput' : conn[1]
            })

    return nodeIndex

def appendMixRGBNode(nodeGraph, name, blendType, factor, toNode, connection=(0, 0)):

    mixedColor = nodeGraph['nodes'][toNode]['inputs'][connection[1]]

    # float connection
    if isinstance(mixedColor, (int, float)):
        mixedColor = [mixedColor, mixedColor, mixedColor, 1]

    return appendNode(nodeGraph, {
        'name' : name,
        'type' : 'MIX_RGB',
        'blendType': blendType,
        'useClamp': False,  # ?
        'inputs' : [factor, mixedColor, [0,0,0,0]],
        'outputs': [[0,0,0,0]]
    }, toNode, [connection])


def appendTextureNode(nodeGraph, name, index, toNode=-1, connections=[(0, 0)]):

    return appendNode(nodeGraph, {
        'name' : name,
        'type' : 'TEXTURE',
        'texture': index,
        'inputs' : [[0,0,0]],
        'outputs': [0, [0,0,0,0], [0,0,0]]
    }, toNode, connections)


def getView3DSpaceProp(prop):
    # screen -> area -> space
    #for area in bpy.data.screens[bpy.context.screen.name].areas:
    for area in bpy.context.screen.areas:
        if area.type != 'VIEW_3D':
            continue

        for space in area.spaces:
            if space.type == 'VIEW_3D':
                return getattr(space, prop)

    return None


def extract_material_node_trees(node_tree):

    out = [node_tree]

    for bl_node in node_tree.nodes:
        if isinstance(bl_node, bpy.types.ShaderNodeGroup):
            out += extract_material_node_trees(bl_node.node_tree)

    return out

def extract_constraints(glTF, bl_obj):
    bl_constraints = bl_obj.constraints

    constraints = []

    for bl_cons in bl_constraints:

        if not bl_cons.is_valid:
            continue

        cons = { 'name': bl_cons.name, 'mute': bl_cons.mute }
        target = (get_node_index(glTF, bl_cons.target.name)
                if getattr(bl_cons, 'target', None) is not None else -1)

        if bl_cons.type == 'COPY_LOCATION':
            if target >= 0:
                constraints.append(dict(cons, **{ 'type': 'copyLocation', 'target': target }))

        elif bl_cons.type == 'COPY_ROTATION':
            if target >= 0:
                constraints.append(dict(cons, **{ 'type': 'copyRotation', 'target': target }))

        elif bl_cons.type == 'COPY_SCALE':
            if target >= 0:
                constraints.append(dict(cons, **{ 'type': 'copyScale', 'target': target }))

        elif bl_cons.type == 'COPY_TRANSFORMS':
            if target >= 0:
                constraints.append(dict(cons, **{ 'type': 'copyLocation', 'target': target }))
                constraints.append(dict(cons, **{ 'type': 'copyRotation', 'target': target }))
                constraints.append(dict(cons, **{ 'type': 'copyScale', 'target': target }))

        elif bl_cons.type == 'LIMIT_LOCATION':
            constraints.append(dict(cons, **{ 'type': 'limitLocation',
                'minX': bl_cons.min_x if bl_cons.use_min_x else '-Infinity',
                'maxX': bl_cons.max_x if bl_cons.use_max_x else 'Infinity',
                'minY': bl_cons.min_z if bl_cons.use_min_z else '-Infinity',
                'maxY': bl_cons.max_z if bl_cons.use_max_z else 'Infinity',
                'minZ': -bl_cons.max_y if bl_cons.use_max_y else '-Infinity',
                'maxZ': -bl_cons.min_y if bl_cons.use_min_y else 'Infinity',
            }))

        elif bl_cons.type == 'LIMIT_ROTATION':
            if bl_cons.use_limit_x:
                constraints.append(dict(cons, **{ 'type': 'limitRotation',
                        'axis': 'X', 'min': bl_cons.min_x, 'max': bl_cons.max_x }))
            if bl_cons.use_limit_y:
                constraints.append(dict(cons, **{ 'type': 'limitRotation',
                        'axis': 'Z', 'min': -bl_cons.max_y, 'max': -bl_cons.min_y }))
            if bl_cons.use_limit_z:
                constraints.append(dict(cons, **{ 'type': 'limitRotation',
                        'axis': 'Y', 'min': bl_cons.min_z, 'max': bl_cons.max_z }))


        elif bl_cons.type == 'LIMIT_SCALE':
            constraints.append(dict(cons, **{ 'type': 'limitScale',
                'minX': max(bl_cons.min_x, 0) if bl_cons.use_min_x else 0,
                'maxX': max(bl_cons.max_x, 0) if bl_cons.use_max_x else 'Infinity',
                'minY': max(bl_cons.min_z, 0) if bl_cons.use_min_z else 0,
                'maxY': max(bl_cons.max_z, 0) if bl_cons.use_max_z else 'Infinity',
                'minZ': max(bl_cons.min_y, 0) if bl_cons.use_min_y else 0,
                'maxZ': max(bl_cons.max_y, 0) if bl_cons.use_max_y else 'Infinity',
            }))

        elif bl_cons.type == 'LOCKED_TRACK':
            if target >= 0:
                constraints.append(dict(cons, **{
                    'type': 'lockedTrack',
                    'target': target,
                    'trackAxis': extract_axis_param(bl_cons.track_axis, 'TRACK_', True),
                    'lockAxis': extract_axis_param(bl_cons.lock_axis, 'LOCK_', False),
                }))

        elif bl_cons.type == 'TRACK_TO':
            if target >= 0:
                constraints.append(dict(cons, **{
                    'type': 'trackTo',
                    'target': target,
                    'trackAxis': extract_axis_param(bl_cons.track_axis, 'TRACK_', True),
                    'upAxis': extract_axis_param(bl_cons.up_axis, 'UP_', True),
                }))

        elif bl_cons.type == 'CHILD_OF':
            if target >= 0:
                if bpy.app.version < (2, 80, 0):
                    constraints.append(dict(cons, **{
                        'type': 'childOf',
                        'target': target,
                        'offsetMatrix': extract_mat(convert_swizzle_matrix(
                                bl_cons.inverse_matrix * bl_obj.matrix_basis))
                    }))
                else:
                    constraints.append(dict(cons, **{
                        'type': 'childOf',
                        'target': target,
                        'offsetMatrix': extract_mat(convert_swizzle_matrix(
                                bl_cons.inverse_matrix @ bl_obj.matrix_basis))
                    }))

        elif bl_cons.type == 'FLOOR':
            if target >= 0:
                floorLocation = extract_axis_param(bl_cons.floor_location, 'FLOOR_', True)
                constraints.append(dict(cons, **{
                    'type': 'floor',
                    'target': target,
                    'offset': -bl_cons.offset if floorLocation in ['Z', '-Z'] else bl_cons.offset,
                    'floorLocation': floorLocation
                }))

    return constraints

def extract_axis_param(param, prefix, use_negative):
    param = param.replace(prefix, '')

    if 'NEGATIVE_' in param:
        param = param.replace('NEGATIVE_', '')
        param = '-' + param

    # param = param.lower()

    if param == 'X':
        return 'X'
    elif param == 'Y':
        return '-Z' if use_negative else 'Z'
    elif param == 'Z':
        return 'Y'
    elif param == '-X':
        return '-X'
    elif param == '-Y':
        return 'Z'
    elif param == '-Z':
        return '-Y'
    else:
        printLog('ERROR', 'Incorrect axis param: ' + param)
        return ''

def extract_image_bindata(bl_image, scene):

    if bl_image.file_format == 'JPEG':
        return extract_image_bindata_jpeg(bl_image, scene)
    elif bl_image.file_format == 'BMP':
        return extract_image_bindata_bmp(bl_image, scene)
    elif bl_image.file_format == 'HDR':
        return extract_image_bindata_hdr(bl_image, scene)
    else:
        return extract_image_bindata_png(bl_image, scene)

def extract_image_bindata_png(bl_image, scene):

    if not bl_image.is_dirty:
        # it's much faster to access packed file data if no conversion is needed
        if bl_image.packed_file is not None and bl_image.file_format == 'PNG':
            return bl_image.packed_file.data

    tmp_img = tempfile.NamedTemporaryFile(delete=False)

    img_set = scene.render.image_settings

    file_format = img_set.file_format
    color_mode = img_set.color_mode
    color_depth = img_set.color_depth
    compression = img_set.compression

    img_set.file_format = 'PNG'
    img_set.color_mode = 'RGBA'
    img_set.color_depth = '16'
    img_set.compression = 90

    bl_image.save_render(tmp_img.name, scene=scene)

    img_set.file_format = file_format
    img_set.color_mode = color_mode
    img_set.color_depth = color_depth
    img_set.compression = compression

    bindata = tmp_img.read()

    tmp_img.close()
    os.unlink(tmp_img.name)

    return bindata

def extract_image_bindata_jpeg(bl_image, scene):

    if not bl_image.is_dirty:
        # it's much faster to access packed file data if no conversion is needed
        if bl_image.packed_file is not None and bl_image.file_format == 'JPEG':
            return bl_image.packed_file.data

    tmp_img = tempfile.NamedTemporaryFile(delete=False)

    img_set = scene.render.image_settings

    file_format = img_set.file_format
    color_mode = img_set.color_mode
    quality = img_set.quality

    img_set.file_format = 'JPEG'
    img_set.color_mode = 'RGB'
    img_set.quality = 90

    bl_image.save_render(tmp_img.name, scene=scene)

    img_set.file_format = file_format
    img_set.color_mode = color_mode
    img_set.quality = quality

    bindata = tmp_img.read()
    tmp_img.close()
    os.unlink(tmp_img.name)

    return bindata

def extract_image_bindata_bmp(bl_image, scene):

    if not bl_image.is_dirty:
        # it's much faster to access packed file data if no conversion is needed
        if bl_image.packed_file is not None and bl_image.file_format == 'BMP':
            return bl_image.packed_file.data

    tmp_img = tempfile.NamedTemporaryFile(delete=False)

    img_set = scene.render.image_settings

    file_format = img_set.file_format
    color_mode = img_set.color_mode

    img_set.file_format = 'BMP'
    img_set.color_mode = 'RGB'

    bl_image.save_render(tmp_img.name, scene=scene)

    img_set.file_format = file_format
    img_set.color_mode = color_mode

    bindata = tmp_img.read()
    tmp_img.close()
    os.unlink(tmp_img.name)

    return bindata

def extract_image_bindata_hdr(bl_image, scene):

    if not bl_image.is_dirty:
        # it's much faster to access packed file data if no conversion is needed
        if bl_image.packed_file is not None and bl_image.file_format == 'HDR':
            return bl_image.packed_file.data

    tmp_img = tempfile.NamedTemporaryFile(delete=False)

    img_set = scene.render.image_settings

    file_format = img_set.file_format
    color_mode = img_set.color_mode

    img_set.file_format = 'HDR'
    img_set.color_mode = 'RGB'

    bl_image.save_render(tmp_img.name, scene=scene)

    img_set.file_format = file_format
    img_set.color_mode = color_mode

    bindata = tmp_img.read()
    tmp_img.close()
    os.unlink(tmp_img.name)

    return bindata

def extractColorSpace(bl_tex):
    if (isinstance(bl_tex, (bpy.types.ShaderNodeTexImage,
            bpy.types.ShaderNodeTexEnvironment))):

        if bl_tex.color_space == 'COLOR':
            colorSpace = 'srgb'
        else:
            colorSpace = 'non-color'
    else:
        # possible c/s values:
        # 'Filmic Log', 'Linear', 'Linear ACES', 'Non-Color', 'Raw', 'sRGB', 'VD16', 'XYZ'
        colorSpace = get_tex_image(bl_tex.texture).colorspace_settings.name.lower()

    return colorSpace

def getPtr(blEntity):
    return blEntity.as_pointer()
