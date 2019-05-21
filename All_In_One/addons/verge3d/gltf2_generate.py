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

import base64
import bpy
import copy
import json
import pathlib
import os.path
import shutil

join = os.path.join
norm = os.path.normpath

from .gltf2_animate import *
from .gltf2_create import *
from .gltf2_debug import *
from .gltf2_extract import *
from .gltf2_filter import *
from .gltf2_get import *
from .utils import *


# Blender default grey color
DEFAULT_COLOR = [0.041, 0.041, 0.041]
PRIMITIVE_MODE_LINES = 1
PRIMITIVE_MODE_TRIANGLES = 4

PROXY_NODE_PREFIX = 'v3d_Proxy_Node_{idx}_{name}'

SPOT_SHADOW_MIN_NEAR = 0.01

CAM_ANGLE_EPSILON = math.pi / 180

# some small offset to be added to the alphaCutoff option, it's needed bcz
# Blender uses the "less or equal" condition for clipping values, but the engine
# uses just "less"
ALPHA_CUTOFF_EPS = 1e-4

def generateAsset(operator, context, export_settings, glTF):
    """
    Generates the top level asset entry.
    """

    asset = {}

    asset['version'] = '2.0'
    asset['generator'] = 'Soft8Soft Verge3D for Blender add-on'

    if export_settings['gltf_copyright'] != "":
        asset['copyright'] = export_settings['gltf_copyright']

    glTF['asset'] = asset


def generateAnimationsParameter(operator,
                  context,
                  export_settings,
                  glTF,
                  action,
                  channels,
                  samplers,
                  bl_object,
                  blender_bone_name,
                  blender_mat_node_name,
                  rotation_mode,
                  matrix_correction,
                  matrix_basis,
                  is_morph_data):
    """
    Helper function for storing animation parameters.
    """

    blender_node_name = bl_object.name

    prefix = ""
    postfix = ""

    location = [None, None, None]
    rotation_axis_angle = [None, None, None, None]
    rotation_euler = [None, None, None]
    rotation_quaternion = [None, None, None, None]
    scale = [None, None, None]
    value = []
    # for material node animation
    default_value = [None]
    energy = [None]

    data = {
        'location' : location,
        'rotation_axis_angle' : rotation_axis_angle,
        'rotation_euler' : rotation_euler,
        'rotation_quaternion' : rotation_quaternion,
        'scale' : scale,
        'value' : value,
        'default_value': default_value,
        'energy': energy
    }

    node_type = 'NODE'
    used_node_name = blender_node_name

    # LAMP 2.79, LIGHT 2.80
    if bl_object.type == 'CAMERA' or bl_object.type == 'LAMP' or bl_object.type == 'LIGHT' or bl_object.type == 'CURVE':
        node_type = 'NODE_X_90'

    if blender_bone_name != None:
        node_type = 'JOINT'
        used_node_name = blender_bone_name
    elif blender_mat_node_name != None:
        node_type = 'MAT_NODE'
        used_node_name = blender_mat_node_name
        default_value *= get_anim_param_dim(action.fcurves, used_node_name)

    # gather fcurves in data dict
    for bl_fcurve in action.fcurves:
        node_name = get_name_in_brackets(bl_fcurve.data_path)

        if node_name != None and not is_morph_data:
            if (node_type == 'JOINT' or node_type == 'MAT_NODE') and used_node_name != node_name:
                continue
            elif node_type == 'NODE' or node_type == 'NODE_X_90':
                continue
            else:
                prefix = node_name + "_"
                postfix = "_"  + node_name

        data_path = get_anim_param(bl_fcurve.data_path)

        if (data_path not in ['location', 'rotation_axis_angle', 'rotation_euler',
                'rotation_quaternion', 'scale', 'value', 'default_value', 'energy']):
            continue

        if data_path != 'value':
            data[data_path][bl_fcurve.array_index] = bl_fcurve
        else:
            data[data_path].append(bl_fcurve)


    # create location sampler

    if location.count(None) < 3:

        sampler_name = prefix + action.name + "_translation"

        if get_index(samplers, sampler_name) == -1:

            sampler = {}

            interpolation = animate_get_interpolation(export_settings, location)
            if interpolation == 'CUBICSPLINE' and node_type == 'JOINT':
                interpolation = 'CONVERSION_NEEDED'

            sampler['interpolation'] = interpolation
            if interpolation == 'CONVERSION_NEEDED':
                sampler['interpolation'] = 'LINEAR'

            translation_data, in_tangent_data, out_tangent_data = animate_location(
                    export_settings, location, interpolation, node_type, used_node_name,
                    matrix_correction, matrix_basis)


            keys = sorted(translation_data.keys())
            values = []
            final_keys = []

            key_offset = 0.0
            if len(keys) > 0 and export_settings['gltf_move_keyframes']:
                key_offset = bpy.context.scene.frame_start / bpy.context.scene.render.fps

            for key in keys:
                if key - key_offset < 0.0:
                    continue

                final_keys.append(key - key_offset)

                if interpolation == 'CUBICSPLINE':
                    for i in range(0, 3):
                        values.append(in_tangent_data[key][i])
                for i in range(0, 3):
                    values.append(translation_data[key][i])
                if interpolation == 'CUBICSPLINE':
                    for i in range(0, 3):
                        values.append(out_tangent_data[key][i])


            componentType = "FLOAT"
            count = len(final_keys)
            type = "SCALAR"

            input = create_accessor(operator, context, export_settings, glTF,
                    final_keys, componentType, count, type, "")

            sampler['input'] = input


            componentType = "FLOAT"
            count = len(values) // 3
            type = "VEC3"

            output = create_accessor(operator, context, export_settings, glTF,
                    values, componentType, count, type, "")

            sampler['output'] = output
            sampler['name'] = sampler_name

            samplers.append(sampler)

    # create rotation sampler

    rotation_data = None
    rotation_in_tangent_data = [0.0, 0.0, 0.0, 0.0]
    rotation_out_tangent_data = [0.0, 0.0, 0.0, 0.0]
    interpolation = None

    sampler_name = prefix + action.name + "_rotation"

    if get_index(samplers, sampler_name) == -1:
        if rotation_axis_angle.count(None) < 4:
            interpolation = animate_get_interpolation(export_settings, rotation_axis_angle)
            # conversion required in any case
            if interpolation == 'CUBICSPLINE':
                interpolation = 'CONVERSION_NEEDED'
            rotation_data = animate_rotation_axis_angle(export_settings, rotation_axis_angle, interpolation, node_type, used_node_name, matrix_correction, matrix_basis)

        if rotation_euler.count(None) < 3:
            interpolation = animate_get_interpolation(export_settings, rotation_euler)
            # conversion required in any case
            # also for linear interpolation to fix issues with e.g 2*PI keyframe differences
            if interpolation == 'CUBICSPLINE' or interpolation == 'LINEAR':
                interpolation = 'CONVERSION_NEEDED'
            rotation_data = animate_rotation_euler(export_settings, rotation_euler, rotation_mode, interpolation, node_type, used_node_name, matrix_correction, matrix_basis)

        if rotation_quaternion.count(None) < 4:
            interpolation = animate_get_interpolation(export_settings, rotation_quaternion)
            if interpolation == 'CUBICSPLINE' and node_type == 'JOINT':
                interpolation = 'CONVERSION_NEEDED'
            rotation_data, rotation_in_tangent_data, rotation_out_tangent_data = animate_rotation_quaternion(export_settings, rotation_quaternion, interpolation, node_type, used_node_name, matrix_correction, matrix_basis)

    if rotation_data is not None:
        keys = sorted(rotation_data.keys())
        values = []
        final_keys = []

        key_offset = 0.0
        if len(keys) > 0 and export_settings['gltf_move_keyframes']:
            key_offset = bpy.context.scene.frame_start / bpy.context.scene.render.fps

        for key in keys:
            if key - key_offset < 0.0:
                continue

            final_keys.append(key - key_offset)

            if interpolation == 'CUBICSPLINE':
                for i in range(0, 4):
                    values.append(rotation_in_tangent_data[key][i])
            for i in range(0, 4):
                values.append(rotation_data[key][i])
            if interpolation == 'CUBICSPLINE':
                for i in range(0, 4):
                    values.append(rotation_out_tangent_data[key][i])


        sampler = {}

        componentType = "FLOAT"
        count = len(final_keys)
        type = "SCALAR"

        input = create_accessor(operator, context, export_settings, glTF, final_keys, componentType, count, type, "")

        sampler['input'] = input

        componentType = "FLOAT"
        count = len(values) // 4
        type = "VEC4"

        output = create_accessor(operator, context, export_settings, glTF, values, componentType, count, type, "")

        sampler['output'] = output

        sampler['interpolation'] = interpolation
        if interpolation == 'CONVERSION_NEEDED':
            sampler['interpolation'] = 'LINEAR'

        sampler['name'] = sampler_name

        samplers.append(sampler)

    # create scale sampler

    if scale.count(None) < 3:
        sampler_name = prefix + action.name + "_scale"

        if get_index(samplers, sampler_name) == -1:

            sampler = {}

            #

            interpolation = animate_get_interpolation(export_settings, scale)
            if interpolation == 'CUBICSPLINE' and node_type == 'JOINT':
                interpolation = 'CONVERSION_NEEDED'

            sampler['interpolation'] = interpolation
            if interpolation == 'CONVERSION_NEEDED':
                sampler['interpolation'] = 'LINEAR'

            scale_data, in_tangent_data, out_tangent_data = animate_scale(export_settings, scale, interpolation, node_type, used_node_name, matrix_correction, matrix_basis)

            #

            keys = sorted(scale_data.keys())
            values = []
            final_keys = []

            key_offset = 0.0
            if len(keys) > 0 and export_settings['gltf_move_keyframes']:
                key_offset = bpy.context.scene.frame_start / bpy.context.scene.render.fps

            for key in keys:
                if key - key_offset < 0.0:
                    continue

                final_keys.append(key - key_offset)

                if interpolation == 'CUBICSPLINE':
                    for i in range(0, 3):
                        values.append(in_tangent_data[key][i])
                for i in range(0, 3):
                    values.append(scale_data[key][i])
                if interpolation == 'CUBICSPLINE':
                    for i in range(0, 3):
                        values.append(out_tangent_data[key][i])

            #

            componentType = "FLOAT"
            count = len(final_keys)
            type = "SCALAR"

            input = create_accessor(operator, context, export_settings, glTF, final_keys, componentType, count, type, "")

            sampler['input'] = input

            #

            componentType = "FLOAT"
            count = len(values) // 3
            type = "VEC3"

            output = create_accessor(operator, context, export_settings, glTF, values, componentType, count, type, "")

            sampler['output'] = output

            #

            sampler['name'] = sampler_name

            samplers.append(sampler)

    # create morph target sampler

    if len(value) > 0 and is_morph_data:
        sampler_name = prefix + action.name + "_weights"

        if get_index(samplers, sampler_name) == -1:

            sampler = {}

            #

            interpolation = animate_get_interpolation(export_settings, value)
            if interpolation == 'CUBICSPLINE' and node_type == 'JOINT':
                interpolation = 'CONVERSION_NEEDED'

            sampler['interpolation'] = interpolation
            if interpolation == 'CONVERSION_NEEDED':
                sampler['interpolation'] = 'LINEAR'

            value_data, in_tangent_data, out_tangent_data = animate_value(export_settings, value, interpolation, node_type, used_node_name, matrix_correction, matrix_basis)

            #

            keys = sorted(value_data.keys())
            values = []
            final_keys = []

            key_offset = 0.0
            if len(keys) > 0 and export_settings['gltf_move_keyframes']:
                key_offset = bpy.context.scene.frame_start / bpy.context.scene.render.fps

            for key in keys:
                if key - key_offset < 0.0:
                    continue

                final_keys.append(key - key_offset)

                if interpolation == 'CUBICSPLINE':
                    for i in range(0, len(in_tangent_data[key])):
                        values.append(in_tangent_data[key][i])
                for i in range(0, len(value_data[key])):
                    values.append(value_data[key][i])
                if interpolation == 'CUBICSPLINE':
                    for i in range(0, len(out_tangent_data[key])):
                        values.append(out_tangent_data[key][i])

            #

            componentType = "FLOAT"
            count = len(final_keys)
            type = "SCALAR"

            input = create_accessor(operator, context, export_settings, glTF, final_keys, componentType, count, type, "")

            sampler['input'] = input

            #

            componentType = "FLOAT"
            count = len(values)
            type = "SCALAR"

            output = create_accessor(operator, context, export_settings, glTF, values, componentType, count, type, "")

            sampler['output'] = output

            #

            sampler['name'] = sampler_name

            samplers.append(sampler)

    # create material node anim sampler
    def_val_dim = len(default_value)

    # NOTE: only value/colors supported for now
    if (def_val_dim == 1 or def_val_dim == 4) and default_value.count(None) < def_val_dim:
        sampler_name = prefix + action.name + "_mat_node_anim"

        if get_index(samplers, sampler_name) == -1:

            sampler = {}

            interpolation = animate_get_interpolation(export_settings, default_value)
            sampler['interpolation'] = interpolation

            if interpolation == 'CONVERSION_NEEDED':
                sampler['interpolation'] = 'LINEAR'

            def_val_data, in_tangent_data, out_tangent_data = animate_default_value(export_settings,
                    default_value, interpolation)

            keys = sorted(def_val_data.keys())
            values = []
            final_keys = []

            key_offset = 0.0
            if len(keys) > 0 and export_settings['gltf_move_keyframes']:
                key_offset = bpy.context.scene.frame_start / bpy.context.scene.render.fps

            for key in keys:
                if key - key_offset < 0.0:
                    continue

                final_keys.append(key - key_offset)

                if interpolation == 'CUBICSPLINE':
                    for i in range(0, def_val_dim):
                        values.append(in_tangent_data[key][i])
                for i in range(0, def_val_dim):
                    values.append(def_val_data[key][i])
                if interpolation == 'CUBICSPLINE':
                    for i in range(0, def_val_dim):
                        values.append(out_tangent_data[key][i])

            componentType = "FLOAT"
            count = len(final_keys)
            type = "SCALAR"

            input = create_accessor(operator, context, export_settings, glTF,
                    final_keys, componentType, count, type, "")

            sampler['input'] = input


            componentType = "FLOAT"
            count = len(values) // def_val_dim
            if def_val_dim == 1:
                type = "SCALAR"
            else:
                type = "VEC4"

            output = create_accessor(operator, context, export_settings, glTF,
                    values, componentType, count, type, "")

            sampler['output'] = output
            sampler['name'] = sampler_name

            samplers.append(sampler)

    if energy.count(None) < 1:
        sampler_name = prefix + action.name + '_energy'

        if get_index(samplers, sampler_name) == -1:

            sampler = {}

            interpolation = animate_get_interpolation(export_settings, energy)
            sampler['interpolation'] = interpolation

            if interpolation == 'CONVERSION_NEEDED':
                sampler['interpolation'] = 'LINEAR'

            energy_data, in_tangent_data, out_tangent_data = animate_energy(export_settings,
                    energy, interpolation)

            keys = sorted(energy_data.keys())
            values = []
            final_keys = []

            key_offset = 0.0
            if len(keys) > 0 and export_settings['gltf_move_keyframes']:
                key_offset = bpy.context.scene.frame_start / bpy.context.scene.render.fps

            for key in keys:
                if key - key_offset < 0.0:
                    continue

                final_keys.append(key - key_offset)

                if interpolation == 'CUBICSPLINE':
                    values.append(in_tangent_data[key][0])
                values.append(energy_data[key][0])
                if interpolation == 'CUBICSPLINE':
                    values.append(out_tangent_data[key][0])

            componentType = "FLOAT"
            count = len(final_keys)
            type = "SCALAR"

            input = create_accessor(operator, context, export_settings, glTF,
                    final_keys, componentType, count, type, "")

            sampler['input'] = input

            componentType = "FLOAT"
            count = len(values)
            type = "SCALAR"

            output = create_accessor(operator, context, export_settings, glTF,
                    values, componentType, count, type, "")

            sampler['output'] = output
            sampler['name'] = sampler_name

            samplers.append(sampler)

    #

    processed_paths = []

    # gather fcurves in data dict
    for bl_fcurve in action.fcurves:
        node_name = get_name_in_brackets(bl_fcurve.data_path)

        if node_name != None and not is_morph_data:
            if (node_type == 'JOINT' or node_type == 'MAT_NODE') and used_node_name != node_name:
                continue
            elif node_type == 'NODE' or node_type == 'NODE_X_90':
                continue
            else:
                prefix = node_name + "_"
                postfix = "_"  + node_name

        data_path = get_anim_param(bl_fcurve.data_path)

        if data_path == 'location':
            path = 'translation'
            if path in processed_paths:
                continue
            processed_paths.append(path)

            sampler_name = prefix + action.name + '_' + path
            create_anim_channel(glTF, bl_object, sampler_name, path, blender_node_name + postfix, samplers, channels)
        elif (data_path == 'rotation_axis_angle' or data_path == 'rotation_euler' or
                data_path == 'rotation_quaternion'):
            path = 'rotation'
            if path in processed_paths:
                continue
            processed_paths.append(path)

            sampler_name = prefix + action.name + '_'  + path
            create_anim_channel(glTF, bl_object, sampler_name, path, blender_node_name + postfix, samplers, channels)
        elif data_path == 'scale':
            path = 'scale'
            if path in processed_paths:
                continue
            processed_paths.append(path)

            sampler_name = prefix + action.name + '_'  + path
            create_anim_channel(glTF, bl_object, sampler_name, path, blender_node_name + postfix, samplers, channels)
        elif data_path == 'value':
            path = 'weights'
            if path in processed_paths:
                continue
            processed_paths.append(path)

            sampler_name = prefix + action.name + '_'  + path
            create_anim_channel(glTF, bl_object, sampler_name, path, blender_node_name + postfix, samplers, channels)
        elif data_path == 'default_value':
            if def_val_dim == 1:
                path = 'material.nodeValue["' + used_node_name + '"]'
            else:
                path = 'material.nodeRGB["' + used_node_name + '"]'
            if path in processed_paths:
                continue
            processed_paths.append(path)
            sampler_name = prefix + action.name + '_mat_node_anim'

            create_anim_channel(glTF, bl_object, sampler_name, path, blender_node_name, samplers, channels)

        elif data_path == 'energy':
            path = 'intensity'
            if path in processed_paths:
                continue
            processed_paths.append(path)

            sampler_name = prefix + action.name + '_energy'
            create_anim_channel(glTF, bl_object, sampler_name, path, blender_node_name, samplers, channels)



#
# Property: animations
#
def generateAnimations(operator, context, export_settings, glTF):
    """
    Generates the top level animations, channels and samplers entry.
    """

    animations = []
    channels = []
    samplers = []

    filtered_objects_with_dg = export_settings['filtered_objects_with_dg']

    blender_backup_action = {}

    if export_settings['gltf_bake_armature_actions']:

        start = None
        end = None

        for current_blender_action in bpy.data.actions:
            # filter out non-object actions
            if current_blender_action.id_root != 'OBJECT':
                continue
            for current_blender_fcurve in current_blender_action.fcurves:
                if current_blender_fcurve is None:
                    continue

                if start == None:
                    start = current_blender_fcurve.range()[0]
                else:
                    start = min(start, current_blender_fcurve.range()[0])

                if end == None:
                    end = current_blender_fcurve.range()[1]
                else:
                    end = max(end, current_blender_fcurve.range()[1])

        if start is None or end is None or export_settings['gltf_frame_range']:
            start = bpy.context.scene.frame_start
            end = bpy.context.scene.frame_end

        #

        for bl_object in filtered_objects_with_dg:
            if bl_object.animation_data is not None:
                blender_backup_action[bl_object.name] = bl_object.animation_data.action

            if bl_object.pose is None:
                continue

            obj_scene = get_scene_by_object(bl_object)
            if obj_scene is not None:

                prev_active_scene = bpy.context.scene
                if bpy.app.version < (2,80,0):
                    bpy.context.screen.scene = obj_scene
                else:
                    bpy.context.window.scene = obj_scene

                setSelectedObject(bl_object)

                bpy.ops.nla.bake(frame_start=start, frame_end=end,
                        only_selected=False, visual_keying=True)

                restoreSelectedObjects()

                if bpy.app.version < (2,80,0):
                    bpy.context.screen.scene = prev_active_scene
                else:
                    bpy.context.window.scene = prev_active_scene

    #
    #

    for bl_object in filtered_objects_with_dg:
        if bl_object.animation_data is None:
            continue

        blender_action = bl_object.animation_data.action

        if blender_action is None:
            continue

        generateAnimationsParameter(operator, context, export_settings, glTF, blender_action,
                channels, samplers, bl_object, None, None, bl_object.rotation_mode,
                mathutils.Matrix.Identity(4),  mathutils.Matrix.Identity(4), False)

        if export_settings['gltf_skins']:
            if bl_object.type == 'ARMATURE' and len(bl_object.pose.bones) > 0:

                #

                # Precalculate joint animation data.

                start = None
                end = None

                for current_blender_action in bpy.data.actions:
                    # filter out non-object actions
                    if current_blender_action.id_root != 'OBJECT':
                        continue

                    for current_blender_fcurve in current_blender_action.fcurves:
                        if current_blender_fcurve is None:
                            continue

                        if start == None:
                            start = current_blender_fcurve.range()[0]
                        else:
                            start = min(start, current_blender_fcurve.range()[0])

                        if end == None:
                            end = current_blender_fcurve.range()[1]
                        else:
                            end = max(end, current_blender_fcurve.range()[1])

                if start is None or end is None:
                    start = bpy.context.scene.frame_start
                    end = bpy.context.scene.frame_end

                #

                for frame in range(int(start), int(end) + 1):
                    bpy.context.scene.frame_set(frame)

                    for blender_bone in bl_object.pose.bones:

                        matrix_basis = blender_bone.matrix_basis

                        #

                        correction_matrix_local = blender_bone.bone.matrix_local.copy()

                        if blender_bone.parent is not None:
                            if bpy.app.version < (2,80,0):
                                correction_matrix_local = blender_bone.parent.bone.matrix_local.inverted() * correction_matrix_local
                            else:
                                correction_matrix_local = blender_bone.parent.bone.matrix_local.inverted() @ correction_matrix_local

                        #
                        if not export_settings['gltf_joint_cache'].get(blender_bone.name):
                            export_settings['gltf_joint_cache'][blender_bone.name] = {}

                        if export_settings['gltf_bake_armature_actions']:
                            matrix_basis = bl_object.convert_space(pose_bone=blender_bone, matrix=blender_bone.matrix, from_space='POSE', to_space='LOCAL')

                        if bpy.app.version < (2,80,0):
                            matrix = correction_matrix_local * matrix_basis
                        else:
                            matrix = correction_matrix_local @ matrix_basis

                        tmp_location, tmp_rotation, tmp_scale = decompose_transform_swizzle(matrix)

                        export_settings['gltf_joint_cache'][blender_bone.name][float(frame)] = [tmp_location, tmp_rotation, tmp_scale]

                #

                for blender_bone in bl_object.pose.bones:

                    matrix_basis = blender_bone.matrix_basis

                    #

                    correction_matrix_local = blender_bone.bone.matrix_local.copy()

                    if blender_bone.parent is not None:
                        if bpy.app.version < (2,80,0):
                            correction_matrix_local = blender_bone.parent.bone.matrix_local.inverted() * correction_matrix_local
                        else:
                            correction_matrix_local = blender_bone.parent.bone.matrix_local.inverted() @ correction_matrix_local

                    #

                    if export_settings['gltf_bake_armature_actions']:
                        matrix_basis = bl_object.convert_space(pose_bone=blender_bone, matrix=blender_bone.matrix, from_space='POSE', to_space='LOCAL')

                    generateAnimationsParameter(operator, context, export_settings, glTF,
                            blender_action, channels, samplers, bl_object, blender_bone.name,
                            None, blender_bone.rotation_mode, correction_matrix_local, matrix_basis, False)



    # export morph targets animation data

    processed_meshes = []
    for bl_object in filtered_objects_with_dg:


        if bl_object.type != 'MESH' or bl_object.data is None:
            continue

        bl_mesh = bl_object.data

        if bl_mesh in processed_meshes:
            continue

        if bl_mesh.shape_keys is None or bl_mesh.shape_keys.animation_data is None:
            continue

        blender_action = bl_mesh.shape_keys.animation_data.action

        if blender_action is None:
            continue

        #

        generateAnimationsParameter(operator, context, export_settings, glTF, blender_action,
                channels, samplers, bl_object, None, None, bl_object.rotation_mode,
                mathutils.Matrix.Identity(4), mathutils.Matrix.Identity(4), True)

        processed_meshes.append(bl_mesh)

    # export light animation

    for bl_object in filtered_objects_with_dg:

        if bl_object.type != 'LAMP' and bl_object.type != 'LIGHT' or bl_object.data is None:
            continue

        bl_light = bl_object.data

        if bl_light.animation_data is None:
            continue

        bl_action = bl_light.animation_data.action

        if bl_action is None:
            continue

        generateAnimationsParameter(operator, context, export_settings, glTF, bl_action,
                channels, samplers, bl_object, None, None, bl_object.rotation_mode,
                mathutils.Matrix.Identity(4), mathutils.Matrix.Identity(4), True)


    # export material animation

    for bl_object in filtered_objects_with_dg:

        # export morph targets animation data.

        if bl_object.type != 'MESH' or bl_object.data is None:
            continue

        bl_mesh = bl_object.data

        for bl_material in bl_mesh.materials:
            if bl_material == None:
                continue

            if bl_material.node_tree == None or bl_material.node_tree.animation_data == None:
                continue

            bl_action = bl_material.node_tree.animation_data.action

            if bl_action == None:
                continue

            correction_matrix_local = mathutils.Matrix.Identity(4)
            matrix_basis = mathutils.Matrix.Identity(4)

            node_names = [n.name for n in bl_material.node_tree.nodes]

            for name in node_names:
                generateAnimationsParameter(operator, context, export_settings, glTF,
                        bl_action, channels, samplers, bl_object, None, name,
                        bl_object.rotation_mode, correction_matrix_local, matrix_basis, False)


    if export_settings['gltf_bake_armature_actions']:
        for bl_object in filtered_objects_with_dg:
            if blender_backup_action.get(bl_object.name) is not None:
                bl_object.animation_data.action = blender_backup_action[bl_object.name]


    if len(channels) > 0 or len(samplers) > 0:

        # collect channel/samplers by node

        anim_data = {}

        for channel in channels:
            bl_object = channel['bl_object']
            name = bl_object.name

            # shallow copy (might be repetitions, need to find out why)
            sampler = samplers[channel['sampler']].copy()

            if not name in anim_data:
                anim_data[name] = [[], [], None]

            # fix sampler index in new array
            channel['sampler'] = len(anim_data[name][1])

            # sampler 'name' is used to gather the index. However, 'name' is
            # no property of sampler and has to be removed.
            del sampler['name']

            anim_data[name][0].append(channel)
            anim_data[name][1].append(sampler)
            anim_data[name][2] = bl_object

            del channel['bl_object']

        for name, data in anim_data.items():

            animation = {
                'name': name,
                'channels' : data[0],
                'samplers' : data[1]
            }

            v3d_data = {}
            animation['extensions'] = { 'S8S_v3d_animation_data' : v3d_data }

            createExtensionsUsed(operator, context, export_settings, glTF, 'S8S_v3d_animation_data')

            bl_object = data[2]
            v3d_data['auto'] = bl_object.v3d.anim_auto
            v3d_data['loop'] = bl_object.v3d.anim_loop
            v3d_data['repeatInfinite'] = bl_object.v3d.anim_repeat_infinite
            v3d_data['repeatCount'] = bl_object.v3d.anim_repeat_count
            # frame to sec
            v3d_data['offset'] = animate_convert_keys([bl_object.v3d.anim_offset])[0]

            animations.append(animation)


    if len(animations) > 0:
        glTF['animations'] = animations


def generateCameras(operator, context, export_settings, glTF):
    """
    Generates the top level cameras entry.
    """

    cameras = []

    filtered_cameras = export_settings['filtered_cameras']

    activeCam = None
    for bl_camera in filtered_cameras:
        camera = generateCamera(bl_camera, glTF)
        if camera:
            cameras.append(camera)
            if (bpy.app.version < (2,80,0) and bpy.context.screen.scene.camera and
                    bpy.context.screen.scene.camera.data == bl_camera):
                activeCam = camera
            elif (bpy.app.version >= (2,80,0) and bpy.context.window.scene.camera and
                    bpy.context.window.scene.camera.data == bl_camera):
                activeCam = camera

    if not len(cameras):
        camera = generateCameraFromView(1)
        if camera:
            cameras.append(camera)

    # ensure that the active scene camera will be used for rendering (first one)
    cameras = sorted(cameras, key=lambda cam: cam==activeCam, reverse=True)

    if len(cameras) > 0:
        glTF['cameras'] = cameras

        createExtensionsUsed(operator, context, export_settings, glTF,
                'S8S_v3d_camera_data')

def generateCamera(bl_camera, glTF):
    camera = {}

    # NOTE: should use a scene where the camera is located for proper calculation
    vf = bl_camera.view_frame(scene=bpy.context.scene)
    aspectRatio = (vf[0].x - vf[2].x) / (vf[0].y - vf[2].y)

    if bl_camera.type == 'PERSP':
        camera['type'] = 'perspective'

        perspective = {}

        perspective['aspectRatio'] = aspectRatio

        yfov = None

        if aspectRatio >= 1:
            if bl_camera.sensor_fit != 'VERTICAL':
                yfov = 2.0 * math.atan(math.tan(bl_camera.angle * 0.5) / aspectRatio)
            else:
                yfov = bl_camera.angle
        else:
            if bl_camera.sensor_fit != 'HORIZONTAL':
                yfov = bl_camera.angle
            else:
                yfov = 2.0 * math.atan(math.tan(bl_camera.angle * 0.5) / aspectRatio)

        perspective['yfov'] = yfov
        perspective['znear'] = bl_camera.clip_start
        perspective['zfar'] = bl_camera.clip_end

        camera['perspective'] = perspective
    elif bl_camera.type == 'ORTHO':
        camera['type'] = 'orthographic'

        orthographic = {}

        orthographic['xmag'] = (vf[0].x - vf[2].x) / 2
        orthographic['ymag'] = (vf[0].y - vf[2].y) / 2

        orthographic['znear'] = bl_camera.clip_start
        orthographic['zfar'] = bl_camera.clip_end

        camera['orthographic'] = orthographic
    else:
        return None


    camera['name'] = bl_camera.name

    v3d_data = {
        'controls' : bl_camera.v3d.controls
    }

    v3d_data['enablePan'] = bl_camera.v3d.enable_pan
    v3d_data['rotateSpeed'] = bl_camera.v3d.rotate_speed
    v3d_data['moveSpeed'] = bl_camera.v3d.move_speed

    v3d_data['viewportFitType'] = bl_camera.sensor_fit
    v3d_data['viewportFitInitialAspect'] = aspectRatio

    # optional orbit params
    if bl_camera.v3d.controls == 'ORBIT':
        target_point = (bl_camera.v3d.orbit_target if bl_camera.v3d.orbit_target_object is None
                else bl_camera.v3d.orbit_target_object.matrix_world.to_translation())

        v3d_data['orbitTarget'] = extract_vec(convert_swizzle_location(target_point))
        v3d_data['orbitMinDistance'] = bl_camera.v3d.orbit_min_distance
        v3d_data['orbitMaxDistance'] = bl_camera.v3d.orbit_max_distance

        v3d_data['orbitMinPolarAngle'] = bl_camera.v3d.orbit_min_polar_angle
        v3d_data['orbitMaxPolarAngle'] = bl_camera.v3d.orbit_max_polar_angle

        min_azim_angle = bl_camera.v3d.orbit_min_azimuth_angle
        max_azim_angle = bl_camera.v3d.orbit_max_azimuth_angle

        # export only when needed
        if abs(2 * math.pi - (max_azim_angle - min_azim_angle)) > CAM_ANGLE_EPSILON:
            v3d_data['orbitMinAzimuthAngle'] = bl_camera.v3d.orbit_min_azimuth_angle
            v3d_data['orbitMaxAzimuthAngle'] = bl_camera.v3d.orbit_max_azimuth_angle

    elif bl_camera.v3d.controls == 'FIRST_PERSON':
        v3d_data['fpsGazeLevel'] = bl_camera.v3d.fps_gaze_level
        v3d_data['fpsStoryHeight'] = bl_camera.v3d.fps_story_height

    camera['extensions'] = { 'S8S_v3d_camera_data' : v3d_data }

    return camera

def generateCameraFromView(aspectRatio):

    printLog('INFO', 'Generating default camera')

    region3D = getView3DSpaceProp('region_3d')
    if region3D == None:
        return None

    camera = {}

    camera['name'] = '__DEFAULT__'

    lens = getView3DSpaceProp('lens')
    near = getView3DSpaceProp('clip_start')
    far = getView3DSpaceProp('clip_end')

    if region3D.is_perspective:
        camera['type'] = 'perspective'

        perspective = {}
        camera['perspective'] = perspective

        perspective['aspectRatio'] = aspectRatio
        # NOTE: decent default value
        perspective['yfov'] = math.pi / 4

        perspective['znear'] = near
        perspective['zfar'] = far
    else:
        camera['type'] = 'orthographic'

        orthographic = {}
        camera['orthographic'] = orthographic

        # NOTE: not quite right since far is the range around view point but OK in most cases
        orthographic['znear'] = -far
        orthographic['zfar'] = far

        xmag = 1/region3D.window_matrix[0][0]
        ymag = 1/region3D.window_matrix[1][1]

        orthographic['xmag'] = xmag
        orthographic['ymag'] = ymag

    v3d_data = {}
    camera['extensions'] = { 'S8S_v3d_camera_data' : v3d_data }

    v3d_data['viewportFitType'] = 'VERTICAL'
    v3d_data['viewportFitInitialAspect'] = aspectRatio

    v3d_data['enablePan'] = True
    v3d_data['rotateSpeed'] = 1
    v3d_data['moveSpeed'] = 1

    v3d_data['controls'] = 'ORBIT'

    v3d_data['orbitTarget'] = extract_vec(convert_swizzle_location(region3D.view_location))
    v3d_data['orbitMinDistance'] = 0
    v3d_data['orbitMaxDistance'] = 10000
    v3d_data['orbitMinPolarAngle'] = 0
    v3d_data['orbitMaxPolarAngle'] = math.pi

    return camera

def generateLights(operator, context, export_settings, glTF):
    """
    Generates the top level lights entry.
    """

    lights = []

    filtered_lights = export_settings['filtered_lights']

    for bl_light in filtered_lights:

        light = {}
        light['profile'] = 'blender'

        if bl_light.type == 'SUN':
            light['type'] = 'directional'
            useShadows = (bl_light.shadow_method != 'NOSHADOW') if bpy.app.version < (2,80,0) else bl_light.use_shadow
        elif bl_light.type == 'POINT':
            light['type'] = 'point'
            useShadows = (bl_light.shadow_method != 'NOSHADOW') if bpy.app.version < (2,80,0) else bl_light.use_shadow
        elif bl_light.type == 'SPOT':
            light['type'] = 'spot'
            useShadows = (bl_light.shadow_method != 'NOSHADOW') if bpy.app.version < (2,80,0) else bl_light.use_shadow
        elif bl_light.type == 'HEMI':
            # Cycles does not suppport HEMI lights (EEVEE does!)
            if isCyclesRender(context):
                light['type'] = 'directional'
            else:
                light['type'] = 'hemisphere'
            useShadows = False
        else:
            continue

        if not export_settings['gltf_use_shadows']:
            useShadows = False

        if useShadows and bpy.app.version < (2,80,0):
            cameraNear = bl_light.v3d.shadow.camera_near
            # usability improvement
            if (bl_light.type == 'SPOT' or bl_light.type == 'POINT') and cameraNear < SPOT_SHADOW_MIN_NEAR:
                cameraNear = SPOT_SHADOW_MIN_NEAR

            cameraFar = bl_light.v3d.shadow.camera_far

            light['shadow'] = {
                'mapSize': int(bl_light.v3d.shadow.map_size),
                'cameraSize': bl_light.v3d.shadow.camera_size,
                'cameraFov': bl_light.v3d.shadow.camera_fov,
                'cameraNear': cameraNear,
                'cameraFar': cameraFar,
                'radius': bl_light.v3d.shadow.radius,
                # NOTE: negate bias since the negative is more appropriate in most cases
                # but keeping it positive in the UI is more user-friendly
                'bias': -bl_light.v3d.shadow.bias
            }
        elif useShadows:
            cameraNear = bl_light.shadow_buffer_clip_start
            # usability improvement
            if (bl_light.type == 'SPOT' or bl_light.type == 'POINT') and cameraNear < SPOT_SHADOW_MIN_NEAR:
                cameraNear = SPOT_SHADOW_MIN_NEAR
            cameraFar = bl_light.shadow_buffer_clip_end

            if bl_light.type == 'SPOT':
                cameraFov = bl_light.spot_size
            else :
                cameraFov = bl_light.v3d.shadow.camera_fov

            light['shadow'] = {
                'mapSize': int(context.scene.eevee.shadow_cascade_size),
                'cameraSize': bl_light.v3d.shadow.camera_size,
                'cameraFov': cameraFov,
                'cameraNear': cameraNear,
                'cameraFar': cameraFar,
                'radius': bl_light.shadow_buffer_soft,
                # NOTE: negate bias since the negative is more appropriate in most cases
                # but keeping it positive in the UI is more user-friendly
                'bias': -bl_light.shadow_buffer_bias * 0.0015
            }


        if bl_light.type == 'POINT' or bl_light.type == 'SPOT':

            # simplified model
            light['distance'] = bl_light.distance;

            if isCyclesRender(context):
                light['decay'] = 2
            else:
                light['decay'] = 1

            # unused "standard" model
            light['constantAttenuation'] = 1.0
            light['linearAttenuation'] = 0.0
            light['quadraticAttenuation'] = 0.0

            if bl_light.falloff_type == 'CONSTANT':
                pass
            elif bl_light.falloff_type == 'INVERSE_LINEAR':
                light['linearAttenuation'] = 1.0 / bl_light.distance
            elif bl_light.falloff_type == 'INVERSE_SQUARE':
                light['quadraticAttenuation'] = 1.0 / bl_light.distance
            elif bl_light.falloff_type == 'LINEAR_QUADRATIC_WEIGHTED':
                light['linearAttenuation'] = bl_light.linear_attenuation * (1 / bl_light.distance)
                light['quadraticAttenuation'] = bl_light.quadratic_attenuation * (1 /
                        (bl_light.distance * bl_light.distance))
            elif bl_light.falloff_type == 'INVERSE_COEFFICIENTS':
                light['constantAttenuation'] = bl_light.constant_coefficient
                light['linearAttenuation'] = bl_light.linear_coefficient * (1.0 / bl_light.distance)
                light['quadraticAttenuation'] = bl_light.quadratic_coefficient * (1.0 /
                        bl_light.distance)
            else:
                pass


            if bl_light.type == 'SPOT':
                # simplified model
                light['angle'] = bl_light.spot_size / 2;
                light['penumbra'] = bl_light.spot_blend;

                # unused "standard" model
                light['fallOffAngle'] = bl_light.spot_size
                light['fallOffExponent'] = 128.0 * bl_light.spot_blend

        if isCyclesRender(context):
            light['color'] = getLightCyclesColor(bl_light)
            light['intensity'] = getLightCyclesStrength(bl_light)
        else:
            light['color'] = [bl_light.color[0], bl_light.color[1], bl_light.color[2]]
            light['intensity'] = bl_light.energy

        light['name'] = bl_light.name

        lights.append(light)


    for bl_scene in bpy.data.scenes:

        light = {}
        light['profile'] = 'blender'

        light['type'] = 'ambient'
        light['color'] = [0, 0, 0]

        if bl_scene.world and not isCyclesRender(context):
            light_set = bl_scene.world.light_settings

            if light_set.use_environment_light:
                # NOTE: only white supported
                energy = light_set.environment_energy
                light['color'] = [energy, energy, energy]

        light['name'] = 'Ambient_' + bl_scene.name

        lights.append(light)

    if len(lights) > 0:
        ext = createAssetExtension(operator, context, export_settings, glTF, 'S8S_v3d_data')
        ext['lights'] = lights


def generateMeshes(operator, context, export_settings, glTF):
    """
    Generates the top level meshes entry.
    """

    meshes = []

    filtered_meshes = export_settings['filtered_meshes']

    filtered_vertex_groups = export_settings['filtered_vertex_groups']

    joint_indices = export_settings['joint_indices']

    for blender_mesh in filtered_meshes:

        srcDatablock = (blender_mesh.get(TO_MESH_SOURCE_CUSTOM_PROP).data
                if blender_mesh.get(TO_MESH_SOURCE_CUSTOM_PROP) else blender_mesh)
        srcName = srcDatablock.name
        srcPtr = getPtr(srcDatablock)
        is_line = obj_data_uses_line_rendering(srcDatablock)

        if is_line:
            internal_primitives = extract_line_primitives(glTF, blender_mesh,
                    export_settings)
        else:
            internal_primitives = extract_primitives(glTF, blender_mesh,
                    filtered_vertex_groups[srcPtr], joint_indices.get(srcName, {}),
                    export_settings)

        if len(internal_primitives) == 0:
            continue

        #
        # Property: mesh
        #

        mesh = {}

        v3d_data = {}
        mesh['extensions'] = { 'S8S_v3d_mesh_data' : v3d_data }

        createExtensionsUsed(operator, context, export_settings, glTF, 'S8S_v3d_mesh_data')

        if is_line:
            line_settings = srcDatablock.v3d.line_rendering_settings
            v3d_data['lineColor'] = extract_vec(line_settings.color)
            v3d_data['lineWidth'] = line_settings.width

        primitives = []

        for internal_primitive in internal_primitives:

            primitive = {}

            primitive['mode'] = PRIMITIVE_MODE_LINES if is_line else PRIMITIVE_MODE_TRIANGLES

            material = get_material_index(glTF, internal_primitive['material'])

            # Meshes/primitives without material are allowed.
            if material >= 0:
                primitive['material'] = material
            elif internal_primitive['material'] == DEFAULT_MAT_NAME:
                primitive['material'] = get_or_create_default_material_index(glTF)
                # it's possible that there were no materials in the scene, so
                # the default one should 'register' the v3d material extension
                createExtensionsUsed(operator, context, export_settings, glTF, 'S8S_v3d_material_data')
            else:
                printLog('WARNING', 'Material ' + internal_primitive['material'] + ' not found')
            indices = internal_primitive['indices']

            componentType = "UNSIGNED_BYTE"

            max_index = max(indices)

            if max_index < 256:
                componentType = "UNSIGNED_BYTE"
            elif max_index < 65536:
                componentType = "UNSIGNED_SHORT"
            elif max_index < 4294967296:
                componentType = "UNSIGNED_INT"
            else:
                printLog('ERROR', 'Invalid max_index: ' + str(max_index))
                continue

            if export_settings['gltf_force_indices']:
                componentType = export_settings['gltf_indices']

            count = len(indices)

            type = "SCALAR"

            indices_index = create_accessor(operator, context, export_settings,
                    glTF, indices, componentType, count, type, "ELEMENT_ARRAY_BUFFER")

            if indices_index < 0:
                printLog('ERROR', 'Could not create accessor for indices')
                continue

            primitive['indices'] = indices_index

            # Attributes

            attributes = {}

            #

            internal_attributes = internal_primitive['attributes']

            #
            #

            internal_position = internal_attributes['POSITION']

            componentType = "FLOAT"

            count = len(internal_position) // 3

            type = "VEC3"

            position = create_accessor(operator, context, export_settings,
                    glTF, internal_position, componentType, count, type, "ARRAY_BUFFER")

            if position < 0:
                printLog('ERROR', 'Could not create accessor for position')
                continue

            attributes['POSITION'] = position

            #
            if internal_attributes.get('NORMAL') is not None:
                internal_normal = internal_attributes['NORMAL']

                componentType = "FLOAT"

                count = len(internal_normal) // 3

                type = "VEC3"

                normal = create_accessor(operator, context, export_settings, glTF,
                        internal_normal, componentType, count, type, "ARRAY_BUFFER")

                if normal < 0:
                    printLog('ERROR', 'Could not create accessor for normal')
                    continue

                attributes['NORMAL'] = normal

            #

            if internal_attributes.get('TANGENT') is not None:
                internal_tangent = internal_attributes['TANGENT']

                componentType = "FLOAT"

                count = len(internal_tangent) // 4

                type = "VEC4"

                tangent = create_accessor(operator, context, export_settings,
                        glTF, internal_tangent, componentType, count, type, "ARRAY_BUFFER")

                if tangent < 0:
                    printLog('ERROR', 'Could not create accessor for tangent')
                    continue

                attributes['TANGENT'] = tangent

            # texture coords

            v3d_data['uvLayers'] = {}

            texcoord_index = 0
            process_texcoord = True
            while process_texcoord:
                texcoord_id = 'TEXCOORD_' + str(texcoord_index)

                if internal_attributes.get(texcoord_id) is not None:
                    internal_texcoord = internal_attributes[texcoord_id]

                    componentType = "FLOAT"

                    count = len(internal_texcoord) // 2

                    type = "VEC2"

                    texcoord = create_accessor(operator, context, export_settings,
                            glTF, internal_texcoord, componentType, count, type, "ARRAY_BUFFER")

                    if texcoord < 0:
                        process_texcoord = False
                        printLog('ERROR', 'Could not create accessor for ' + texcoord_id)
                        continue

                    if internal_primitive['useNodeAttrs']:
                        uv_layer_name = blender_mesh.uv_layers[texcoord_index].name
                        v3d_data['uvLayers'][uv_layer_name] = texcoord_id;

                    attributes[texcoord_id] = texcoord

                    texcoord_index += 1
                else:
                    process_texcoord = False

            # vertex colors

            v3d_data['colorLayers'] = {}

            color_index = 0

            process_color = True
            while process_color:
                color_id = 'COLOR_' + str(color_index)

                if internal_attributes.get(color_id) is not None:
                    internal_color = internal_attributes[color_id]

                    componentType = "FLOAT"

                    count = len(internal_color) // 4

                    type = "VEC4"

                    color = create_accessor(operator, context, export_settings,
                            glTF, internal_color, componentType, count, type, "ARRAY_BUFFER")

                    if color < 0:
                        process_color = False
                        printLog('ERROR', 'Could not create accessor for ' + color_id)
                        continue

                    if internal_primitive['useNodeAttrs']:
                        vc_layer_name = blender_mesh.vertex_colors[color_index].name
                        v3d_data['colorLayers'][vc_layer_name] = color_id;

                    attributes[color_id] = color

                    color_index += 1
                else:
                    process_color = False

            #

            if export_settings['gltf_skins']:
                bone_index = 0

                process_bone = True
                while process_bone:
                    joint_id = 'JOINTS_' + str(bone_index)
                    weight_id = 'WEIGHTS_' + str(bone_index)

                    if (internal_attributes.get(joint_id) is not None and
                            internal_attributes.get(weight_id) is not None):
                        internal_joint = internal_attributes[joint_id]

                        componentType = "UNSIGNED_SHORT"

                        count = len(internal_joint) // 4

                        type = "VEC4"

                        joint = create_accessor(operator, context, export_settings,
                                glTF, internal_joint, componentType, count, type, "ARRAY_BUFFER")

                        if joint < 0:
                            process_bone = False
                            printLog('ERROR', 'Could not create accessor for ' + joint_id)
                            continue

                        attributes[joint_id] = joint

                        #
                        #

                        internal_weight = internal_attributes[weight_id]

                        componentType = "FLOAT"

                        count = len(internal_weight) // 4

                        type = "VEC4"

                        weight = create_accessor(operator, context, export_settings,
                                glTF, internal_weight, componentType, count, type, "ARRAY_BUFFER")

                        if weight < 0:
                            process_bone = False
                            printLog('ERROR', 'Could not create accessor for ' + weight_id)
                            continue

                        attributes[weight_id] = weight

                        #
                        #

                        bone_index += 1
                    else:
                        process_bone = False

            #

            if export_settings['gltf_morph']:
                if blender_mesh.shape_keys is not None:
                    targets = []

                    morph_index = 0
                    for blender_shape_key in blender_mesh.shape_keys.key_blocks:
                        if blender_shape_key != blender_shape_key.relative_key:

                            target_position_id = 'MORPH_POSITION_' + str(morph_index)
                            target_normal_id = 'MORPH_NORMAL_' + str(morph_index)
                            target_tangent_id = 'MORPH_TANGENT_' + str(morph_index)

                            if internal_attributes.get(target_position_id) is not None:
                                internal_target_position = internal_attributes[target_position_id]

                                componentType = "FLOAT"

                                count = len(internal_target_position) // 3

                                type = "VEC3"

                                target_position = create_accessor(operator, context, export_settings, glTF, internal_target_position, componentType, count, type, "")

                                if target_position < 0:
                                    printLog('ERROR', 'Could not create accessor for ' + target_position_id)
                                    continue

                                #

                                target = {
                                    'POSITION' : target_position
                                }

                                #

                                if export_settings['gltf_morph_normal'] and internal_attributes.get(target_normal_id) is not None:

                                    internal_target_normal = internal_attributes[target_normal_id]

                                    componentType = "FLOAT"

                                    count = len(internal_target_normal) // 3

                                    type = "VEC3"

                                    target_normal = create_accessor(operator, context, export_settings, glTF, internal_target_normal, componentType, count, type, "")

                                    if target_normal < 0:
                                        printLog('ERROR', 'Could not create accessor for ' + target_normal_id)
                                        continue

                                    target['NORMAL'] = target_normal
                                #

                                if export_settings['gltf_morph_tangent'] and internal_attributes.get(target_tangent_id) is not None:

                                    internal_target_tangent = internal_attributes[target_tangent_id]

                                    componentType = "FLOAT"

                                    count = len(internal_target_tangent) // 3

                                    type = "VEC3"

                                    target_tangent = create_accessor(operator, context, export_settings, glTF, internal_target_tangent, componentType, count, type, "")

                                    if target_tangent < 0:
                                        printLog('ERROR', 'Could not create accessor for ' + target_tangent_id)
                                        continue

                                    target['TANGENT'] = target_tangent

                                #
                                #

                                targets.append(target)

                                morph_index += 1

                    if len(targets) > 0:
                        primitive['targets'] = targets

            #
            #

            primitive['attributes'] = attributes
            primitives.append(primitive)

        #

        if export_settings['gltf_morph']:
            if blender_mesh.shape_keys is not None:
                morph_max = len(blender_mesh.shape_keys.key_blocks) - 1
                if morph_max > 0:
                    weights = []

                    for blender_shape_key in blender_mesh.shape_keys.key_blocks:
                        if blender_shape_key != blender_shape_key.relative_key:
                            weights.append(blender_shape_key.value)

                    mesh['weights'] = weights


        #

        if export_settings['gltf_custom_props']:
            props = create_custom_property(blender_mesh)

            if props is not None:
                if 'extras' not in mesh:
                    mesh['extras'] = {}
                mesh['extras']['custom_props'] = props

        #

        mesh['primitives'] = primitives

        mesh['name'] = srcName
        # also a pointer to object.data
        mesh['id'] = srcPtr

        meshes.append(mesh)


    if len (meshes) > 0:
        glTF['meshes'] = meshes


def generateDuplicateMesh(operator, context, export_settings, glTF, bl_object):
    """
    Helper function for dublicating meshes with linked object materials.
    """

    if bl_object is None:
        return -1

    mesh_index = getMeshIndex(glTF, getPtr(bl_object.data))

    if mesh_index == -1:
        return False

    new_mesh = copy.deepcopy(glTF['meshes'][mesh_index])

    #

    primitives = new_mesh['primitives']

    primitive_index = 0
    for blender_material_slot in bl_object.material_slots:
        if blender_material_slot.link == 'OBJECT':

            primitives[primitive_index]['material'] = (get_or_create_default_material_index(glTF)
                    if blender_material_slot.material is None
                    else get_material_index(glTF, blender_material_slot.material.name))
        primitive_index += 1

    #

    new_name = bl_object.data.name + '_' + bl_object.name

    new_mesh['name'] = new_name

    glTF['meshes'].append(new_mesh)

    return getMeshIndex(glTF, new_name)


def generateNodeParameter(matrix, node):
    """
    Helper function for storing node parameters.
    """

    translation, rotation, scale = decompose_transform_swizzle(matrix)
    # Put w at the end.
    rotation = mathutils.Quaternion((rotation[1], rotation[2], rotation[3], rotation[0]))

    if translation[0] != 0.0 or translation[1] != 0.0 or translation[2] != 0.0:
        node['translation'] = [translation[0], translation[1], translation[2]]

    if rotation[0] != 0.0 or rotation[1] != 0.0 or rotation[2] != 0.0 or rotation[3] != 1.0:
        node['rotation'] = [rotation[0], rotation[1], rotation[2], rotation[3]]

    if scale[0] != 1.0 or scale[1] != 1.0 or scale[2] != 1.0:
        node['scale'] = [scale[0], scale[1], scale[2]]


def getMeshIndexDupliCheck(operator, context, export_settings, glTF, bl_object):

    mesh = getMeshIndex(glTF, getPtr(bl_object.data))
    is_line = obj_data_uses_line_rendering(bl_object.data)

    if mesh >= 0 and not is_line:
        need_dublicate = False

        if bl_object.material_slots:
            for blender_material_slot in bl_object.material_slots:
                if blender_material_slot.link == 'OBJECT':
                    need_dublicate = True
                    break

        if need_dublicate:
            mesh = generateDuplicateMesh(operator, context, export_settings, glTF,
                    bl_object)

    return mesh


def generateNodeInstance(operator, context, export_settings, glTF, bl_object):
    """
    Helper function for storing node instances.
    """

    #
    # Property: node
    #

    node = {}

    bl_obj_type = bl_object.type

    # the parent inverse matrix is considered later when generating scene
    # hierarchy
    node_matrix = bl_object.matrix_basis
    generateNodeParameter(node_matrix, node)

    v3d_data = {}
    node['extensions'] = { 'S8S_v3d_node_data' : v3d_data }

    if bl_obj_type in ['MESH', 'CURVE', 'SURFACE']:

        mesh = getMeshIndexDupliCheck(operator, context, export_settings, glTF, bl_object)
        if mesh >= 0:
            node['mesh'] = mesh

    elif bl_obj_type == 'FONT':

        if export_settings['gltf_bake_text']:
            mesh = getMeshIndexDupliCheck(operator, context, export_settings, glTF, bl_object)
            if mesh >= 0:
                node['mesh'] = mesh
        else:
            curve = get_curve_index(glTF, bl_object.data.name)
            if curve >= 0:
                v3d_data['curve'] = curve

    elif bl_obj_type == 'CAMERA':
        # NOTE: possible issues with libraries
        camera = get_camera_index(glTF, bl_object.data.name)
        if camera >= 0:
            node['camera'] = camera

    # LAMP 2.79, LIGHT 2.80
    elif bl_obj_type == 'LAMP' or bl_obj_type == 'LIGHT':
        light = get_light_index(glTF, bl_object.data.name)
        if light >= 0:
            v3d_data['light'] = light

    v3d_data['hidden'] = bl_object.hide_render
    v3d_data['renderOrder'] = bl_object.v3d.render_order
    v3d_data['frustumCulling'] = bl_object.v3d.frustum_culling

    if (bpy.app.version >= (2,80,0) and bl_obj_type in ['MESH', 'CURVE', 'SURFACE', 'FONT'] and
            export_settings['gltf_use_shadows']):
        v3d_data['useShadows'] = bl_object.v3d.use_shadows
        v3d_data['useCastShadows'] = bl_object.display.show_shadows

    if bpy.app.version < (2,80,0) and len(bl_object.users_group):
        v3d_data['groupNames'] = []
        for group in bl_object.users_group:
            v3d_data['groupNames'].append(group.name)
    elif bpy.app.version >= (2,80,0) and len(bl_object.users_collection):

        collections = getObjectAllCollections(bl_object)
        v3d_data['groupNames'] = [coll.name for coll in collections]
        for coll in collections:
            if coll is not None and coll.hide_render:
                v3d_data['hidden'] = True
                break

    if export_settings['gltf_custom_props']:
        props = create_custom_property(bl_object)

        if props is not None:
            if 'extras' not in node:
                node['extras'] = {}
            node['extras']['custom_props'] = props

    node['name'] = bl_object.name

    return node

def generateCameraNodeFromView(glTF):
    printLog('INFO', 'Generating default camera node')

    node = {}

    node['name'] = '__DEFAULT_CAMERA__'

    # checked in generateCameraFromView()
    region3D = getView3DSpaceProp('region_3d')

    if region3D.is_perspective:
        matrix = region3D.view_matrix.inverted()
        generateNodeParameter(matrix, node)
    else:
        # ortho: calculate based on view location and rotation
        q = region3D.view_rotation
        if bpy.app.version < (2,80,0):
            t = q * mathutils.Vector((0, 0, region3D.view_distance)) + region3D.view_location
        else:
            t = q @ mathutils.Vector((0, 0, region3D.view_distance)) + region3D.view_location

        node['translation'] = [t[0], t[2], -t[1]]
        node['rotation'] = [q[1], q[3], -q[2], q[0]]
        node['scale'] = [1, 1, 1]

    camera = get_camera_index(glTF, '__DEFAULT__')
    if camera >= 0:
        node['camera'] = camera

    return node


def generateProxyNodes(operator, context, glTF, node, bl_object):
    """
    Generate additional nodes for objects with the non-identity (for applying
    animations properly) and even non-decomposable parent inverse matrix (to
    ensure that the exported node matrix is a TRS matrix).
    """

    if bl_object.parent is None:
        return []

    proxy_nodes = []


    parInvMats = list(filter(lambda mat: not mat4_is_identity(mat),
            mat4ToTRSMatrices(bl_object.matrix_parent_inverse)))
    if parInvMats:
        printLog('WARNING', 'Object "' + bl_object.name
                + '" has a non-identity parent inverse matrix. Creating proxy nodes.')

    relBoneMats = []
    if bl_object.parent is not None and bl_object.parent_type == 'BONE':
        pose_bone = bl_object.parent.pose.bones.get(bl_object.parent_bone)
        if pose_bone is not None:
            if pose_bone.bone.use_relative_parent:
                relBoneMats = list(filter(lambda mat: not mat4_is_identity(mat),
                        mat4ToTRSMatrices(pose_bone.bone.matrix_local.inverted())))
                if relBoneMats:
                    printLog('WARNING', 'Object "' + bl_object.name
                            + '" has a non-identity parent bone relative matrix. '
                            + 'Creating proxy nodes.')
            else:
                # objects parented to a bone without the "Relative Parent"
                # option will have their node['translation'] modified later
                bone_len = (pose_bone.bone.tail_local - pose_bone.bone.head_local).length
                relBoneMats = [mathutils.Matrix.Translation((0, bone_len, 0))]

    proxyMats = relBoneMats + parInvMats
    proxyMats.reverse()

    for i in range(len(proxyMats)):
        proxy_node = {}
        proxy_node['name'] = PROXY_NODE_PREFIX.format(idx=str(i), name=node['name'])
        generateNodeParameter(proxyMats[i], proxy_node)
        proxy_nodes.append(proxy_node)

    return proxy_nodes


def mat4ToTRSMatrices(mat4):
    """
    Represent the given matrix in a form of a product of TRS-decomposable matrices.
    """

    if mat4_is_trs_decomposable(mat4):
        return [mat4]

    result = mat4_svd_decompose_to_mats(mat4)
    if result is None:
        # fallback to the original matrix
        return [mat4]

    return [result[0], result[1]]

def generateNodes(operator, context, export_settings, glTF):
    """
    Generates the top level nodes entry.
    """

    nodes = []

    skins = []

    #
    #

    filtered_objects_shallow = export_settings['filtered_objects_shallow']
    filtered_objects_with_dg = export_settings['filtered_objects_with_dg']

    for bl_object in filtered_objects_shallow:
        node = generateNodeInstance(operator, context, export_settings, glTF, bl_object)
        nodes.append(node)
        proxy_nodes = generateProxyNodes(operator, context, glTF, node, bl_object)
        nodes.extend(proxy_nodes)

    if get_camera_index(glTF, '__DEFAULT__') >= 0:
        nodes.append(generateCameraNodeFromView(glTF))

    for bl_obj in filtered_objects_shallow:
        if bpy.app.version >= (2,80,0):

            if (bl_obj.instance_type == 'COLLECTION'
                    and bl_obj.instance_collection != None
                    and bl_obj.instance_collection.v3d.enable_export):

                for bl_instance_obj in bl_obj.instance_collection.objects:

                    node = generateNodeInstance(operator, context, export_settings, glTF, bl_instance_obj)
                    node['name'] = 'Instance_' + bl_obj.name + '_' + bl_instance_obj.name
                    nodes.append(node)
                    proxy_nodes = generateProxyNodes(operator, context, glTF, node, bl_instance_obj)
                    nodes.extend(proxy_nodes)

                node = {}
                node['name'] = 'Instance_Offset_' + bl_obj.name

                translation = convert_swizzle_location(bl_obj.instance_collection.instance_offset)
                node['translation'] = [-translation[0], -translation[1], -translation[2]]
                nodes.append(node)

        else:
            if bl_obj.dupli_type == 'GROUP' and bl_obj.dupli_group != None:

                for blender_dupli_object in bl_obj.dupli_group.objects:

                    if not is_dupli_obj_visible_in_group(bl_obj.dupli_group,
                            blender_dupli_object):
                        continue

                    node = generateNodeInstance(operator, context, export_settings, glTF, blender_dupli_object)
                    node['name'] = 'Duplication_' + bl_obj.name + '_' + blender_dupli_object.name
                    nodes.append(node)
                    proxy_nodes = generateProxyNodes(operator, context, glTF, node, blender_dupli_object)
                    nodes.extend(proxy_nodes)

                node = {}
                node['name'] = 'Duplication_Offset_' + bl_obj.name

                translation = convert_swizzle_location(bl_obj.dupli_group.dupli_offset)
                node['translation'] = [-translation[0], -translation[1], -translation[2]]
                nodes.append(node)

    if len(nodes) > 0:
        glTF['nodes'] = nodes

        createExtensionsUsed(operator, context, export_settings, glTF,
                'S8S_v3d_node_data')

    if export_settings['gltf_skins']:
        for bl_object in filtered_objects_with_dg:
            if bl_object.type != 'ARMATURE' or len(bl_object.pose.bones) == 0:
                continue

            temp_action = None

            if export_settings['gltf_bake_armature_actions'] and not export_settings['gltf_animations']:
                if bl_object.animation_data is not None:
                    temp_action = bl_object.animation_data.action

                obj_scene = get_scene_by_object(bl_object)
                if obj_scene is not None:

                    prev_active_scene = bpy.context.scene
                    if bpy.app.version < (2,80,0):
                        bpy.context.screen.scene = obj_scene
                    else:
                        bpy.context.window.scene = obj_scene

                    setSelectedObject(bl_object)

                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.nla.bake(frame_start=bpy.context.scene.frame_current,
                            frame_end=bpy.context.scene.frame_current,
                            only_selected=False, visual_keying=True)

                    restoreSelectedObjects()

                    if bpy.app.version < (2,80,0):
                        bpy.context.screen.scene = prev_active_scene
                    else:
                        bpy.context.window.scene = obj_scene

            joints = []

            joints_written = False

            #

            children_list = list(bl_object.children)

            for blender_check_object in filtered_objects_with_dg:
                blender_check_armature = find_armature(blender_check_object)

                if blender_check_armature == bl_object and blender_check_object not in children_list:
                    children_list.append(blender_check_object)

            #

            for blender_object_child in children_list:
                #
                # Property: skin and node
                #

                inverse_matrices = []

                for blender_bone in bl_object.pose.bones:

                    if not joints_written:
                        node = {}

                        correction_matrix_local = blender_bone.bone.matrix_local.copy()

                        if blender_bone.parent is not None:
                            if bpy.app.version < (2,80,0):
                                correction_matrix_local = blender_bone.parent.bone.matrix_local.inverted() * correction_matrix_local
                            else:
                                correction_matrix_local = blender_bone.parent.bone.matrix_local.inverted() @ correction_matrix_local

                        matrix_basis = blender_bone.matrix_basis

                        if export_settings['gltf_bake_armature_actions']:
                            matrix_basis = bl_object.convert_space(pose_bone=blender_bone, matrix=blender_bone.matrix, from_space='POSE', to_space='LOCAL')

                        if bpy.app.version < (2,80,0):
                            generateNodeParameter(correction_matrix_local * matrix_basis, node)
                        else:
                            generateNodeParameter(correction_matrix_local @ matrix_basis, node)

                        node['name'] = bl_object.name + "_" + blender_bone.name

                        joints.append(len(nodes))

                        nodes.append(node)

                    if bpy.app.version < (2,80,0):
                        bind_shape_matrix = bl_object.matrix_world.inverted() * blender_object_child.matrix_world
                        inverse_bind_matrix = convert_swizzle_matrix(blender_bone.bone.matrix_local.inverted() * bind_shape_matrix)
                    else:
                        bind_shape_matrix = bl_object.matrix_world.inverted() @ blender_object_child.matrix_world
                        inverse_bind_matrix = convert_swizzle_matrix(blender_bone.bone.matrix_local.inverted() @ bind_shape_matrix)

                    for column in range(0, 4):
                        for row in range(0, 4):
                            inverse_matrices.append(inverse_bind_matrix[row][column])

                # add data for the armature itself at the end
                skeleton = get_node_index(glTF, bl_object.name)

                if not joints_written:
                    joints.append(skeleton)

                if bpy.app.version < (2,80,0):
                    armature_inverse_bind_matrix = convert_swizzle_matrix(
                            bl_object.matrix_world.inverted() * blender_object_child.matrix_world)
                else:
                    armature_inverse_bind_matrix = convert_swizzle_matrix(
                            bl_object.matrix_world.inverted() @ blender_object_child.matrix_world)

                for column in range(0, 4):
                    for row in range(0, 4):
                        inverse_matrices.append(armature_inverse_bind_matrix[row][column])

                joints_written = True

                skin = {}

                skin['skeleton'] = skeleton

                skin['joints'] = joints

                componentType = "FLOAT"
                count = len(inverse_matrices) // 16
                type = "MAT4"

                inverseBindMatrices = create_accessor(operator, context, export_settings, glTF, inverse_matrices, componentType, count, type, "")

                skin['inverseBindMatrices'] = inverseBindMatrices

                skins.append(skin)

            if temp_action is not None:
                bl_object.animation_data.action = temp_action


    if len (skins) > 0:
        glTF['skins'] = skins

    #
    # Resolve children etc.
    #

    for bl_object in filtered_objects_shallow:
        node_index = get_node_index(glTF, bl_object.name)

        node = nodes[node_index]

        if export_settings['gltf_skins']:
            blender_armature = find_armature(bl_object)
            if blender_armature is not None:
                index_offset = 0

                if bl_object in blender_armature.children:
                    index_offset = blender_armature.children.index(bl_object)
                else:
                    index_local_offset = 0

                    for blender_check_object in filtered_objects_shallow:
                        blender_check_armature = find_armature(blender_check_object)
                        if blender_check_armature == blender_armature:
                            index_local_offset += 1

                        if bl_object == blender_check_object:
                            index_local_offset -= 1
                            break

                    index_offset = len(blender_armature.children) + index_local_offset

                node['skin'] = get_skin_index(glTF, blender_armature.name, index_offset)

        # constraints

        v3d_data = get_asset_extension(node, 'S8S_v3d_node_data')
        if v3d_data and export_settings['gltf_export_constraints'] and len(bl_object.constraints):
            v3d_data['constraints'] = extract_constraints(glTF, bl_object)

        # first-person camera link to collision material

        if (bl_object.type == 'CAMERA' and
                bl_object.data and
                bl_object.data.v3d.controls == 'FIRST_PERSON' and
                bl_object.data.v3d.fps_collision_material):

            v3d_cam_data = get_asset_extension(glTF['cameras'][node['camera']], 'S8S_v3d_camera_data')
            if v3d_cam_data:
                mat = get_material_index(glTF, bl_object.data.v3d.fps_collision_material.name)
                if mat >= 0:
                    v3d_cam_data['fpsCollisionMaterial'] = mat


        # Nodes
        for child_obj in bl_object.children:

            if child_obj.parent_type == 'BONE' and export_settings['gltf_skins']:
                continue

            nodeAppendChildFromObj(glTF, node, child_obj)

        # Instancing / Duplications
        if bpy.app.version >= (2,80,0):

            if bl_object.instance_type == 'COLLECTION' and bl_object.instance_collection != None:
                child_index = get_node_index(glTF, 'Instance_Offset_' + bl_object.name)
                if child_index >= 0:
                    if not 'children' in node:
                        node['children'] = []
                    node['children'].append(child_index)

                    instance_node = nodes[child_index]
                    for bl_instance_obj in bl_object.instance_collection.objects:
                        nodeAppendChildFromObj(glTF, instance_node,
                                bl_instance_obj, 'Instance_' + bl_object.name
                                + '_' + bl_instance_obj.name)

        else:
            if bl_object.dupli_type == 'GROUP' and bl_object.dupli_group != None:
                child_index = get_node_index(glTF, 'Duplication_Offset_' + bl_object.name)
                if child_index >= 0:
                    if not 'children' in node:
                        node['children'] = []
                    node['children'].append(child_index)

                    duplication_node = nodes[child_index]
                    for blender_dupli_object in bl_object.dupli_group.objects:
                        nodeAppendChildFromObj(glTF, duplication_node,
                                blender_dupli_object, 'Duplication_' + bl_object.name
                                + '_' + blender_dupli_object.name)

        #

        if export_settings['gltf_skins']:
            # Joint
            if bl_object.type == 'ARMATURE' and len(bl_object.pose.bones) > 0:

                # parent root bones to the node of the armature object
                for blender_bone in bl_object.pose.bones:

                    if blender_bone.parent:
                        continue

                    child_index = get_node_index(glTF, bl_object.name + "_" + blender_bone.name)
                    if child_index < 0:
                        continue

                    if not 'children' in node:
                        node['children'] = []
                    node['children'].append(child_index)

                # process the bone's children: objects parented to the bone and child bones
                for blender_bone in bl_object.pose.bones:

                    bone_index = get_node_index(glTF, bl_object.name + "_" + blender_bone.name)
                    if bone_index == -1:
                        continue

                    bone_node = nodes[bone_index]

                    for child_obj in bl_object.children:
                        if (child_obj.parent_type == 'BONE'
                                and child_obj.parent_bone == blender_bone.name):
                            nodeAppendChildFromObj(glTF, bone_node, child_obj)

                    for child_bone in blender_bone.children:
                        child_bone_index = get_node_index(glTF, bl_object.name + "_" + child_bone.name)

                        if child_bone_index > -1:
                            if not 'children' in bone_node:
                                bone_node['children'] = []
                            bone_node['children'].append(child_bone_index)

    # NOTE: possible breakage of the children's animation
    preprocessCamLampNodes(nodes)


def nodeAppendChildFromObj(glTF, parent_node, child_obj, child_node_name=None):

    if child_node_name is None:
        child_node_name = child_obj.name

    child_index = get_node_index(glTF, child_node_name)
    if child_index < 0:
        return -1

    if not 'children' in parent_node:
        parent_node['children'] = []

    i = 0
    index_to_append = child_index
    while True:
        proxy_name = PROXY_NODE_PREFIX.format(idx=str(i), name=child_node_name)
        proxy_idx = get_node_index(glTF, proxy_name)
        i += 1

        if proxy_idx >= 0:
            proxy_node = glTF['nodes'][proxy_idx]
            if not 'children' in proxy_node:
                proxy_node['children'] = []
            proxy_node['children'].append(index_to_append)
            index_to_append = proxy_idx
        else:
            break

    parent_node['children'].append(index_to_append)

def preprocessCamLampNodes(nodes):
    """
    Rotate cameras and lamps by 90 degrees around the X local axis, apply the
    inverted rotation to their children.
    """

    rot_x_90 = mathutils.Quaternion((1.0, 0.0, 0.0), -math.pi/2).to_matrix().to_4x4()
    rot_x_90_inv = mathutils.Quaternion((1.0, 0.0, 0.0), math.pi/2).to_matrix().to_4x4()

    # rotate cameras and lamps by 90 around X axis prior(!) to applying their TRS,
    # the matrix is still decomposable after such operation
    for node in nodes:
        if nodeIsCamera(node) or nodeIsLamp(node) or nodeIsCurve(node):
            mat = nodeComposeMatrix(node)

            if bpy.app.version < (2,80,0):
                trans, rot, sca = (mat * rot_x_90).decompose()
            else:
                trans, rot, sca = (mat @ rot_x_90).decompose()
            node['translation'] = list(trans)
            node['rotation'] = [rot[1], rot[2], rot[3], rot[0]]
            node['scale'] = list(sca)

            if 'children' in node:
                for child_index in node['children']:
                    child_node = nodes[child_index]
                    child_mat = nodeComposeMatrix(child_node)

                    if bpy.app.version < (2,80,0):
                        trans, rot, sca = (rot_x_90_inv * child_mat).decompose()
                    else:
                        trans, rot, sca = (rot_x_90_inv @ child_mat).decompose()
                    child_node['translation'] = list(trans)
                    child_node['rotation'] = [rot[1], rot[2], rot[3], rot[0]]
                    child_node['scale'] = list(sca)

def nodeComposeMatrix(node):
    if 'translation' in node:
        mat_trans = mathutils.Matrix.Translation(node['translation'])
    else:
        mat_trans = mathutils.Matrix.Identity(4)

    if 'rotation' in node:
        rot = node['rotation']
        # Put w to the start
        mat_rot = mathutils.Quaternion((rot[3], rot[0], rot[1], rot[2])).to_matrix().to_4x4()
    else:
        mat_rot = mathutils.Matrix.Identity(4)

    mat_sca = mathutils.Matrix()
    if 'scale' in node:
        mat_sca[0][0] = node['scale'][0]
        mat_sca[1][1] = node['scale'][1]
        mat_sca[2][2] = node['scale'][2]

    if bpy.app.version < (2,80,0):
        return mat_trans * mat_rot * mat_sca
    else:
        return mat_trans @ mat_rot @ mat_sca


def nodeIsCamera(node):
    return 'camera' in node

def nodeIsLamp(node):
    return ('extensions' in node and 'S8S_v3d_node_data' in node['extensions']
            and 'light' in node['extensions']['S8S_v3d_node_data'])

def nodeIsCurve(node):
    return ('extensions' in node and 'S8S_v3d_node_data' in node['extensions']
            and 'curve' in node['extensions']['S8S_v3d_node_data'])


def generateImages(operator, context, export_settings, glTF):
    """
    Generates the top level images entry.
    """

    filtered_images = export_settings['filtered_images']

    images = []

    #
    #

    for bl_image in filtered_images:
        #
        # Property: image
        #

        image = {}

        uri = get_image_exported_uri(export_settings, bl_image)

        if export_settings['gltf_format'] == 'ASCII':

            if export_settings['gltf_embed_images']:
                # embed image as Base64

                img_data = extract_image_bindata(bl_image, context.scene)

                image['uri'] = ('data:' + get_image_exported_mime_type(bl_image)
                        + ';base64,'
                        + base64.b64encode(img_data).decode('ascii'))

            else:
                # use external file

                old_path = bl_image.filepath_from_user()
                new_path = norm(export_settings['gltf_filedirectory'] + uri)

                if (bl_image.is_dirty or bl_image.packed_file is not None
                        or not os.path.isfile(old_path)):
                    # always extract data for dirty/packed/missing images,
                    # because they can differ from an external source's data

                    img_data = extract_image_bindata(bl_image, context.scene)

                    with open(new_path, 'wb') as f:
                        f.write(img_data)

                elif old_path != new_path:
                    # copy an image to a new location

                    if (bl_image.file_format != "JPEG" and bl_image.file_format != "PNG"
                            and bl_image.file_format != "BMP" and bl_image.file_format != 'HDR'):
                        # need conversion to PNG

                        img_data = extract_image_bindata_png(bl_image, context.scene)

                        with open(new_path, 'wb') as f:
                            f.write(img_data)
                    else:
                        shutil.copyfile(old_path, new_path)

                image['uri'] = uri

        else:
            # store image in glb

            img_data = extract_image_bindata(bl_image, context.scene)

            bufferView = create_bufferView(operator, context, export_settings,
                    glTF, img_data, 0, 0)

            image['mimeType'] = get_image_exported_mime_type(bl_image)
            image['bufferView'] = bufferView

        export_settings['gltf_uri_data']['uri'].append(uri)
        export_settings['gltf_uri_data']['bl_datablocks'].append(bl_image)

        images.append(image)

    if len (images) > 0:
        glTF['images'] = images


def generateTextures(operator, context, export_settings, glTF):
    """
    Generates the top level textures entry.
    """

    filtered_textures = export_settings['filtered_textures']

    textures = []

    v3d_data_used = False

    # shader node textures or texture slots
    for blender_texture in filtered_textures:

        texture = {
            'name' : get_texture_name(blender_texture)
        }

        v3d_data = {}

        v3d_data['colorSpace'] = extractColorSpace(blender_texture)

        if isinstance(blender_texture, bpy.types.ShaderNodeTexEnvironment):
            magFilter = WEBGL_FILTERS['LINEAR']
            if blender_texture.interpolation == 'Closest':
                magFilter = WEBGL_FILTERS['NEAREST']
            wrap = WEBGL_WRAPPINGS['REPEAT']

            uri = get_image_exported_uri(export_settings, get_tex_image(blender_texture))

        elif isinstance(blender_texture, bpy.types.ShaderNodeTexImage):
            magFilter = WEBGL_FILTERS['LINEAR']
            if blender_texture.interpolation == 'Closest':
                magFilter = WEBGL_FILTERS['NEAREST']
            wrap = WEBGL_WRAPPINGS['REPEAT']
            if blender_texture.extension == 'CLIP':
                wrap = WEBGL_WRAPPINGS['CLAMP_TO_EDGE']

            uri = get_image_exported_uri(export_settings, get_tex_image(blender_texture))

            anisotropy = int(blender_texture.v3d.anisotropy)
            if anisotropy > 1:
                v3d_data['anisotropy'] = anisotropy

        else:

            if isinstance(blender_texture.texture, bpy.types.EnvironmentMapTexture):
                magFilter = WEBGL_FILTERS['LINEAR']
                wrap = WEBGL_WRAPPINGS['CLAMP_TO_EDGE']
                v3d_data['isCubeTexture'] = True
            else:
                magFilter = WEBGL_FILTERS['LINEAR']
                wrap = WEBGL_WRAPPINGS['REPEAT']

                if blender_texture.texture.extension == 'CLIP':
                    wrap = WEBGL_WRAPPINGS['CLAMP_TO_EDGE']

            anisotropy = int(blender_texture.texture.v3d.anisotropy)
            if anisotropy > 1:
                v3d_data['anisotropy'] = anisotropy

            uri = get_image_exported_uri(export_settings, get_tex_image(blender_texture.texture))

        texture['sampler'] = create_sampler(operator, context, export_settings, glTF, magFilter, wrap)

        # 'source' isn't required but must be >=0 according to GLTF 2.0 spec.
        img_index = get_image_index(export_settings, uri)
        if img_index >= 0:
            texture['source'] = img_index

        texture['extensions'] = { 'S8S_v3d_texture_data' : v3d_data }
        v3d_data_used = True

        textures.append(texture)

    if v3d_data_used:
        createExtensionsUsed(operator, context, export_settings, glTF,
                'S8S_v3d_texture_data')

    if len (textures) > 0:
        glTF['textures'] = textures



def generateNodeGraphs(operator, context, export_settings, glTF):
    """
    Generates the top level node graphs entry.
    """

    filtered_node_groups = export_settings['filtered_node_groups']

    if len(filtered_node_groups) > 0:
        ext = createAssetExtension(operator, context, export_settings, glTF, 'S8S_v3d_data')
        graphs = ext['nodeGraphs'] = []

        # store group names prior to processing them in case of group multiple
        # nesting
        for bl_node_group in filtered_node_groups:
            graphs.append({ 'name': bl_node_group.name })

        for bl_node_group in filtered_node_groups:
            graph = extract_node_graph(bl_node_group, export_settings, glTF)

            index = filtered_node_groups.index(bl_node_group)
            graphs[index].update(graph)

def generateCurves(operator, context, export_settings, glTF):
    """
    Generates the top level curves entry.
    """

    curves = []

    filtered_curves = export_settings['filtered_curves']

    for bl_curve in filtered_curves:

        curve = {}

        curve['name'] = bl_curve.name

        # curve, surface, font
        # NOTE: currently only font curves supported
        curve['type'] = 'font'

        if curve['type'] == 'font':
            base_dir = os.path.dirname(os.path.abspath(__file__))

            curve['text'] = bl_curve.body

            if bl_curve.font.filepath == '<builtin>':
                font_path_json = join(base_dir, 'fonts', 'bfont.json')
            else:
                font_path = os.path.normpath(bpy.path.abspath(bl_curve.font.filepath))
                font_path_json = os.path.splitext(font_path)[0] + '.json'

                if not os.path.isfile(font_path_json):
                    printLog('ERROR', 'Unable to load .json font file ' + font_path_json)
                    font_path_json = join(base_dir, 'fonts', 'bfont.json')

            with open(font_path_json, 'r', encoding='utf-8') as f:
                # inline
                curve['font'] = json.load(f)

            # NOTE: 0.72 for bfont only
            curve['size'] = bl_curve.size * 0.72
            curve['height'] = bl_curve.extrude
            curve['curveSegments'] = max(bl_curve.resolution_u - 1, 1)

            curve['bevelThickness'] = bl_curve.bevel_depth
            curve['bevelSize'] = bl_curve.bevel_depth
            curve['bevelSegments'] = bl_curve.bevel_resolution + 1

            align_x = bl_curve.align_x

            if align_x == 'LEFT' or align_x == 'JUSTIFY' or align_x == 'FLUSH':
                curve['alignX'] = 'left'
            elif align_x == 'CENTER':
                curve['alignX'] = 'center'
            elif align_x == 'RIGHT':
                curve['alignX'] = 'right'

            align_y = bl_curve.align_y

            if align_y == 'TOP_BASELINE' or align_x == 'BOTTOM':
                curve['alignY'] = 'bottom'
            elif align_y == 'TOP':
                curve['alignY'] = 'top'
            elif align_y == 'CENTER':
                curve['alignY'] = 'center'

            # optional
            if len(bl_curve.materials):
                material = get_material_index(glTF, bl_curve.materials[0].name)

                if material >= 0:
                    curve['material'] = material
                else:
                    printLog('WARNING', 'Material ' + bl_curve.materials[0].name + ' not found')

        curves.append(curve)

    if len(curves) > 0:
        ext = createAssetExtension(operator, context, export_settings, glTF, 'S8S_v3d_data')
        ext['curves'] = curves

def generateMaterials(operator, context, export_settings, glTF):
    """
    Generates the top level materials entry.
    """

    filtered_materials = export_settings['filtered_materials']

    materials = []

    S8S_v3d_data_used = False

    for bl_mat in filtered_materials:
        material = {}

        v3d_data = {}
        material['extensions'] = { 'S8S_v3d_material_data' : v3d_data }
        S8S_v3d_data_used = True

        mat_type = get_material_type(bl_mat)

        # PBR Materials

        if mat_type == 'PBR':
            for blender_node in bl_mat.node_tree.nodes:
                if isinstance(blender_node, bpy.types.ShaderNodeGroup):

                    alpha = 1.0

                    if blender_node.node_tree.name.startswith('Verge3D PBR'):
                        #
                        # Property: pbrMetallicRoughness
                        #

                        material['pbrMetallicRoughness'] = {}

                        pbrMetallicRoughness = material['pbrMetallicRoughness']

                        #
                        # Base color texture
                        #
                        index = get_texture_index_node(export_settings, glTF, 'BaseColor', blender_node)
                        if index >= 0:
                            baseColorTexture = {
                                'index' : index
                            }

                            texCoord = get_texcoord_index(glTF, 'BaseColor', blender_node)
                            if texCoord > 0:
                                baseColorTexture['texCoord'] = texCoord

                            pbrMetallicRoughness['baseColorTexture'] = baseColorTexture

                        #
                        # Base color factor
                        #
                        baseColorFactor = get_vec4(blender_node.inputs['BaseColorFactor'].default_value, [1.0, 1.0, 1.0, 1.0])
                        if baseColorFactor[0] != 1.0 or baseColorFactor[1] != 1.0 or baseColorFactor[2] != 1.0 or baseColorFactor[3] != 1.0:
                            pbrMetallicRoughness['baseColorFactor'] = baseColorFactor
                            alpha = baseColorFactor[3]

                        #
                        # Metallic factor
                        #
                        metallicFactor = get_scalar(blender_node.inputs['MetallicFactor'].default_value, 1.0)
                        if metallicFactor != 1.0:
                            pbrMetallicRoughness['metallicFactor'] = metallicFactor

                        #
                        # Roughness factor
                        #
                        roughnessFactor = get_scalar(blender_node.inputs['RoughnessFactor'].default_value, 1.0)
                        if roughnessFactor != 1.0:
                            pbrMetallicRoughness['roughnessFactor'] = roughnessFactor

                        #
                        # Metallic roughness texture
                        #
                        index = get_texture_index_node(export_settings, glTF, 'MetallicRoughness', blender_node)
                        if index >= 0:
                            metallicRoughnessTexture = {
                                'index' : index
                            }

                            texCoord = get_texcoord_index(glTF, 'MetallicRoughness', blender_node)
                            if texCoord > 0:
                                metallicRoughnessTexture['texCoord'] = texCoord

                            pbrMetallicRoughness['metallicRoughnessTexture'] = metallicRoughnessTexture


                    #
                    # Emissive texture
                    #
                    index = get_texture_index_node(export_settings, glTF, 'Emissive', blender_node)
                    if index >= 0:
                        emissiveTexture = {
                            'index' : index
                        }

                        texCoord = get_texcoord_index(glTF, 'Emissive', blender_node)
                        if texCoord > 0:
                            emissiveTexture['texCoord'] = texCoord

                        material['emissiveTexture'] = emissiveTexture

                    #
                    # Emissive factor
                    #
                    emissiveFactor = get_vec3(blender_node.inputs['EmissiveFactor'].default_value, [0.0, 0.0, 0.0])
                    if emissiveFactor[0] != 0.0 or emissiveFactor[1] != 0.0 or emissiveFactor[2] != 0.0:
                        material['emissiveFactor'] = emissiveFactor

                    #
                    # Normal texture
                    #
                    index = get_texture_index_node(export_settings, glTF, 'Normal', blender_node)
                    if index >= 0:
                        normalTexture = {
                            'index' : index
                        }

                        texCoord = get_texcoord_index(glTF, 'Normal', blender_node)
                        if texCoord > 0:
                            normalTexture['texCoord'] = texCoord

                        scale = get_scalar(blender_node.inputs['NormalScale'].default_value, 1.0)

                        if scale != 1.0:
                            normalTexture['scale'] = scale

                        material['normalTexture'] = normalTexture

                    #
                    # Occlusion texture
                    #
                    if len(blender_node.inputs['Occlusion'].links) > 0:
                        index = get_texture_index_node(export_settings, glTF, 'Occlusion', blender_node)
                        if index >= 0:
                            occlusionTexture = {
                                'index' : index
                            }

                            texCoord = get_texcoord_index(glTF, 'Occlusion', blender_node)
                            if texCoord > 0:
                                occlusionTexture['texCoord'] = texCoord

                            strength = get_scalar(blender_node.inputs['OcclusionStrength'].default_value, 1.0)

                            if strength != 1.0:
                                occlusionTexture['strength'] = strength

                            material['occlusionTexture'] = occlusionTexture

                    #
                    # Alpha
                    #
                    index = get_texture_index_node(export_settings, glTF, 'Alpha', blender_node)
                    if index >= 0 or alpha < 1.0:
                        alphaMode = 'BLEND'
                        if get_scalar(blender_node.inputs['AlphaMode'].default_value, 0.0) >= 0.5:
                            alphaMode = 'MASK'

                            material['alphaCutoff'] = (
                                    get_scalar(blender_node.inputs['AlphaCutoff'].default_value, 0.5)
                                    + ALPHA_CUTOFF_EPS)

                        material['alphaMode'] = alphaMode

                    if bpy.app.version < (2,80,0):
                        # NOTE: implementation of BGE "Backface Culling"
                        if not bl_mat.game_settings.use_backface_culling:
                            material['doubleSided'] = True
                    else:
                        if bl_mat.v3d.render_side == 'DOUBLE':
                            material['doubleSided'] = True

                    #
                    # Use Color_0
                    #

                    if get_scalar(blender_node.inputs['Use COLOR_0'].default_value, 0.0) < 0.5:
                        export_settings['gltf_use_no_color'].append(bl_mat.name)


        else:
            # Basic and Node-based materials

            alphaMode = 'OPAQUE'

            if bpy.app.version < (2,80,0):
                if bl_mat.use_transparency:
                    if bl_mat.transparency_method == 'MASK':
                        alphaMode = 'MASK'
                    else:
                        alphaMode = 'BLEND'
            else:
                if bl_mat.blend_method == 'CLIP':
                    alphaMode = 'MASK'
                    material['alphaCutoff'] = bl_mat.alpha_threshold + ALPHA_CUTOFF_EPS
                elif bl_mat.blend_method != 'OPAQUE':
                    alphaMode = 'BLEND'

            if alphaMode != 'OPAQUE':
                material['alphaMode'] = alphaMode

            if bpy.app.version < (2,80,0):
                # NOTE: implementation of BGE "Alpha Add"
                if bl_mat.game_settings.alpha_blend == 'ADD':
                    v3d_data['depthWrite'] = False

                # NOTE: implementation of BGE "Backface Culling"
                if not bl_mat.game_settings.use_backface_culling:
                    material['doubleSided'] = True
                    v3d_data['renderSide'] = 'DOUBLE'
            else:
                if material_has_blend_backside(bl_mat):
                    v3d_data['depthWrite'] = False
                    material['doubleSided'] = True
                    v3d_data['renderSide'] = 'DOUBLE'
                else:
                    if bl_mat.v3d.render_side == 'DOUBLE':
                        material['doubleSided'] = True
                    if bl_mat.v3d.render_side != 'FRONT':
                        v3d_data['renderSide'] = bl_mat.v3d.render_side
                    if bl_mat.blend_method != 'OPAQUE' and bl_mat.v3d.depth_write == False:
                        v3d_data['depthWrite'] = bl_mat.v3d.depth_write

            if bl_mat.v3d.dithering == True:
                v3d_data['dithering'] = bl_mat.v3d.dithering

            if mat_type == 'NODE' or mat_type == 'CYCLES':
                v3d_data['nodeGraph'] = extract_node_graph(bl_mat.node_tree,
                        export_settings, glTF)
            else:
                v3d_data['nodeGraph'] = composeNodeGraph(bl_mat, export_settings, glTF)

        material['name'] = bl_mat.name

        blend_mode = create_blend_mode(bl_mat)
        if blend_mode is not None:
            v3d_data['blendMode'] = blend_mode

        # receive
        if bpy.app.version < (2,80,0) and export_settings['gltf_use_shadows']:
            v3d_data['useShadows'] = bl_mat.use_shadows
            v3d_data['useCastShadows'] = bl_mat.use_cast_shadows

        if export_settings['gltf_custom_props']:
            props = create_custom_property(bl_mat)

            if props is not None:
                if 'extras' not in material:
                    material['extras'] = {}
                material['extras']['custom_props'] = props

        materials.append(material)


    if len (materials) > 0:
        if S8S_v3d_data_used:
            createExtensionsUsed(operator, context, export_settings, glTF,
                    'S8S_v3d_material_data')


        glTF['materials'] = materials


def generateScenes(operator, context, export_settings, glTF):
    """
    Generates the top level scenes entry.
    """

    scenes = []

    #

    for bl_scene in bpy.data.scenes:
        #
        # Property: scene
        #

        scene = {}
        scene['extras'] = {}

        #

        nodes = []

        scene_objects = bl_scene.objects if bpy.app.version < (2,80,0) else bl_scene.collection.all_objects

        for bl_object in scene_objects:
            if bl_object.parent is None:
                node_index = get_node_index(glTF, bl_object.name)

                if node_index < 0:
                    continue

                nodes.append(node_index)

        # TODO: need it only on the main scene
        if get_camera_index(glTF, '__DEFAULT__') >= 0:
            nodes.append(get_node_index(glTF, '__DEFAULT_CAMERA__'))

        if len(nodes) > 0:
            scene['nodes'] = nodes

        v3d_data = {}
        scene['extensions'] = { 'S8S_v3d_scene_data' : v3d_data }

        light = get_light_index(glTF, 'Ambient_' + bl_scene.name)

        v3d_data['light'] = light

        if bl_scene.world and export_settings['gltf_format'] != 'FB':
            world_mat = get_material_index(glTF, WORLD_NODE_MAT_NAME.substitute(
                    name=bl_scene.world.name))
            if world_mat >= 0:
                v3d_data['worldMaterial'] = world_mat

            if isCyclesRender(context):
                v3d_data['physicallyCorrectLights'] = True

        if export_settings['gltf_use_shadows']:
            v3d_data['shadowMap'] = {
                'type' : export_settings['gltf_shadow_map_type'],
                'renderReverseSided' : True if export_settings['gltf_shadow_map_side'] == 'BACK' else False,
                'renderSingleSided' : False if export_settings['gltf_shadow_map_side'] == 'BOTH' else True
            }

        v3d_data['aaMethod'] = export_settings['gltf_aa_method']

        if export_settings['gltf_use_hdr']:
            v3d_data['useHDR'] = True

        outline = bl_scene.v3d.outline

        if bpy.app.version < (2,80,0):
            fx_settings = getView3DSpaceProp('fx_settings')
        else:
            fx_settings = bl_scene.eevee

        use_dof = fx_settings.use_dof if fx_settings and bl_scene.camera else False
        use_ssao = False
        if fx_settings:
            if bpy.app.version < (2,80,0) and fx_settings.use_ssao:
                use_ssao = True
            elif bpy.app.version >= (2,80,0) and fx_settings.use_gtao:
                use_ssao = True

        #use_bloom = False if bpy.app.version <= (2,80,0) else fx_settings.use_bloom

        # NOTE: disable all postprocessing except outline
        use_bloom = False
        use_dof = False
        use_ssao = False

        if outline.enabled or use_dof or use_ssao or use_bloom:
            v3d_data['postprocessing'] = []

            if outline.enabled:
                effect = {
                    'type': 'outline',
                    'edgeStrength': outline.edge_strength,
                    'edgeGlow': outline.edge_glow,
                    'edgeThickness': outline.edge_thickness,
                    'pulsePeriod': outline.pulse_period,
                    'visibleEdgeColor': extract_vec(outline.visible_edge_color),
                    'hiddenEdgeColor': extract_vec(outline.hidden_edge_color)
                }

                v3d_data['postprocessing'].append(effect)

            if use_ssao:
                effect = {
                    'type': 'ssao'
                }

                v3d_data['postprocessing'].append(effect)

            if use_dof:
                camera = bl_scene.camera.data
                if camera.dof_object:
                    focus = (camera.dof_object.location - bl_scene.camera.location).length
                else:
                    focus = camera.dof_distance

                effect = {
                    'type': 'dof',
                    'focus': focus
                }

                v3d_data['postprocessing'].append(effect)

            if use_bloom:
                effect = {
                    'type': 'bloom',
                    'threshold': fx_settings.bloom_threshold,
                    'radius': fx_settings.bloom_radius,
                    'strength': fx_settings.bloom_intensity
                }

                v3d_data['postprocessing'].append(effect)

        scene['extras']['animFrameRate'] = bl_scene.render.fps

        if export_settings['gltf_custom_props']:
            props = create_custom_property(bl_scene.world)

            if props is not None:
                scene['extras']['custom_props'] = props


        scene['name'] = bl_scene.name

        scenes.append(scene)

    if len(scenes) > 0:
        glTF['scenes'] = scenes

        createExtensionsUsed(operator, context, export_settings, glTF,
                'S8S_v3d_scene_data')

def generateScene(operator, context, export_settings, glTF):
    """
    Generates the top level scene entry.
    """

    if bpy.app.version < (2,80,0):
        index = get_scene_index(glTF, bpy.context.screen.scene.name)
    else:
        index = get_scene_index(glTF, bpy.context.window.scene.name)

    if index >= 0:
        glTF['scene'] = index


def generateGLTF(operator,
                  context,
                  export_settings,
                  glTF):
    """
    Generates the main glTF structure.
    """

    profile_start()
    generateAsset(operator, context, export_settings, glTF)
    profile_end('asset')
    bpy.context.window_manager.progress_update(5)

    profile_start()
    generateImages(operator, context, export_settings, glTF)
    profile_end('images')
    bpy.context.window_manager.progress_update(10)

    profile_start()
    generateTextures(operator, context, export_settings, glTF)
    profile_end('textures')
    bpy.context.window_manager.progress_update(20)

    profile_start()
    generateNodeGraphs(operator, context, export_settings, glTF)
    profile_end('node_graphs')
    bpy.context.window_manager.progress_update(25)

    profile_start()
    generateMaterials(operator, context, export_settings, glTF)
    profile_end('materials')
    bpy.context.window_manager.progress_update(30)

    profile_start()
    generateCurves(operator, context, export_settings, glTF)
    profile_end('curves')
    bpy.context.window_manager.progress_update(35)

    profile_start()
    generateCameras(operator, context, export_settings, glTF)
    profile_end('cameras')
    bpy.context.window_manager.progress_update(40)

    profile_start()
    generateLights(operator, context, export_settings, glTF)
    profile_end('lights')
    bpy.context.window_manager.progress_update(50)

    profile_start()
    generateMeshes(operator, context, export_settings, glTF)
    profile_end('meshes')
    bpy.context.window_manager.progress_update(60)

    profile_start()
    generateNodes(operator, context, export_settings, glTF)
    profile_end('nodes')
    bpy.context.window_manager.progress_update(70)

    if export_settings['gltf_animations']:
        profile_start()
        generateAnimations(operator, context, export_settings, glTF)
        profile_end('animations')
        bpy.context.window_manager.progress_update(80)

    bpy.context.window_manager.progress_update(80)

    profile_start()
    generateScenes(operator, context, export_settings, glTF)
    profile_end('scenes')

    bpy.context.window_manager.progress_update(95)

    profile_start()
    generateScene(operator, context, export_settings, glTF)
    profile_end('scene')

    bpy.context.window_manager.progress_update(100)



    byteLength = len(export_settings['gltf_binary'])

    if byteLength > 0:
        glTF['buffers'] = []

        buffer = {
            'byteLength' : byteLength
        }

        if export_settings['gltf_format'] == 'ASCII':
            uri = export_settings['gltf_binaryfilename']

            if export_settings['gltf_embed_buffers']:
                uri = 'data:application/octet-stream;base64,' + base64.b64encode(export_settings['gltf_binary']).decode('ascii')

            buffer['uri'] = uri

        glTF['buffers'].append(buffer)
