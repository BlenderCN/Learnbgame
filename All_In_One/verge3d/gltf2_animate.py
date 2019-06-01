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

import bpy
import math
import mathutils

from .gltf2_debug import *
from .gltf2_extract import *

#
# Globals
#

#
# Functions
#

def animate_get_interpolation(export_settings, blender_fcurve_list):
    """
    Retrieves the glTF interpolation, depending on a fcurve list.
    Blender allows mixing and more variations of interpolations.
    In such a case, a conversion is needed.
    """

    if export_settings['gltf_force_sampling']:
        return 'CONVERSION_NEEDED'

    #

    prev_times = None
    for blender_fcurve in blender_fcurve_list:
        if blender_fcurve is None:
            continue

        curr_times = [p.co[0] for p in blender_fcurve.keyframe_points]
        if prev_times is not None and curr_times != prev_times:
            return 'CONVERSION_NEEDED'
        prev_times = curr_times


    interpolation = None

    for blender_fcurve in blender_fcurve_list:
        if blender_fcurve is None:
            continue

        #

        currentKeyframeCount = len(blender_fcurve.keyframe_points)

        if currentKeyframeCount > 0 and blender_fcurve.keyframe_points[0].co[0] < 0:
            return 'CONVERSION_NEEDED'

        #

        for blender_keyframe in blender_fcurve.keyframe_points:
            if interpolation is None:
                if blender_keyframe.interpolation == 'BEZIER':
                    interpolation = 'CUBICSPLINE'
                elif blender_keyframe.interpolation == 'LINEAR':
                    interpolation = 'LINEAR'
                elif blender_keyframe.interpolation == 'CONSTANT':
                    interpolation = 'STEP'
                else:
                    interpolation = 'CONVERSION_NEEDED'
                    return interpolation
            else:
                if blender_keyframe.interpolation == 'BEZIER' and interpolation != 'CUBICSPLINE':
                    interpolation = 'CONVERSION_NEEDED'
                    return interpolation
                elif blender_keyframe.interpolation == 'LINEAR' and interpolation != 'LINEAR':
                    interpolation = 'CONVERSION_NEEDED'
                    return interpolation
                elif blender_keyframe.interpolation == 'CONSTANT' and interpolation != 'STEP':
                    interpolation = 'CONVERSION_NEEDED'
                    return interpolation
                elif blender_keyframe.interpolation != 'BEZIER' and blender_keyframe.interpolation != 'LINEAR' and blender_keyframe.interpolation != 'CONSTANT':
                    interpolation = 'CONVERSION_NEEDED'
                    return interpolation

    if interpolation is None:
        interpolation = 'CONVERSION_NEEDED'

    # NOTE: make curve conversion since CUBICSPLINE isn't supported in the
    # engine at the moment
    if interpolation == 'CUBICSPLINE':
        interpolation = 'CONVERSION_NEEDED'

    return interpolation


def animate_convert_rotation_axis_angle(axis_angle):
    """
    Converts an axis angle to a quaternion rotation.
    """
    q = mathutils.Quaternion((axis_angle[1], axis_angle[2], axis_angle[3]), axis_angle[0])

    return [q.x, q.y, q.z, q.w]


def animate_convert_rotation_euler(euler, rotation_mode):
    """
    Converts an euler angle to a quaternion rotation.
    """
    rotation = mathutils.Euler((euler[0], euler[1], euler[2]), rotation_mode).to_quaternion()

    return [rotation.x, rotation.y, rotation.z, rotation.w]


def animate_convert_keys(key_list):
    """
    Converts Blender key frames to glTF time keys depending on the applied frames per second.
    """
    times = []

    for key in key_list:
        times.append(key / bpy.context.scene.render.fps)

    return times


def animate_gather_keys(export_settings, fcurve_list, interpolation):
    """
    Merges and sorts several key frames to one set.
    If an interpolation conversion is needed, the sample key frames are created as well.
    """
    keys = []

    if interpolation == 'CONVERSION_NEEDED':
        start = None
        end = None

        for blender_fcurve in fcurve_list:
            if blender_fcurve is None:
                continue

            if start == None:
                start = blender_fcurve.range()[0]
            else:
                start = min(start, blender_fcurve.range()[0])

            if end == None:
                end = blender_fcurve.range()[1]
            else:
                end = max(end, blender_fcurve.range()[1])

            #

            add_epsilon_keyframe = False
            for blender_keyframe in blender_fcurve.keyframe_points:
                if add_epsilon_keyframe:
                    key = blender_keyframe.co[0] - 0.001

                    if key not in keys:
                        keys.append(key)

                    add_epsilon_keyframe = False

                if blender_keyframe.interpolation == 'CONSTANT':
                    add_epsilon_keyframe = True

            if add_epsilon_keyframe:
                key = end - 0.001

                if key not in keys:
                    keys.append(key)

        key = start
        while key <= end:
            if not export_settings['gltf_frame_range'] or (export_settings['gltf_frame_range'] and key >= bpy.context.scene.frame_start and key <= bpy.context.scene.frame_end):
                keys.append(key)
            key += 1.0

        keys.sort()

    else:
        for blender_fcurve in fcurve_list:
            if blender_fcurve is None:
                continue

            for blender_keyframe in blender_fcurve.keyframe_points:
                key = blender_keyframe.co[0]
                if not export_settings['gltf_frame_range'] or (export_settings['gltf_frame_range'] and key >= bpy.context.scene.frame_start and key <= bpy.context.scene.frame_end):
                    if key not in keys:
                        keys.append(key)

        keys.sort()

    return keys


def animate_location(export_settings, location, interpolation, node_type, node_name, matrix_correction, matrix_basis):
    """
    Calculates/gathers the key value pairs for location transformations.
    """
    if not export_settings['gltf_joint_cache'].get(node_name):
        export_settings['gltf_joint_cache'][node_name] = {}

    keys = animate_gather_keys(export_settings, location, interpolation)

    times = animate_convert_keys(keys)

    result = {}
    result_in_tangent = {}
    result_out_tangent = {}

    keyframe_index = 0
    for time in times:
        translation = [0.0, 0.0, 0.0]
        in_tangent = [0.0, 0.0, 0.0]
        out_tangent = [0.0, 0.0, 0.0]

        if node_type == 'JOINT':
            if export_settings['gltf_joint_cache'][node_name].get(keys[keyframe_index]):
                translation, tmp_rotation, tmp_scale = export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]]
            else:
                bpy.context.scene.frame_set(keys[keyframe_index])

                if bpy.app.version < (2,80,0):
                    matrix = matrix_correction * matrix_basis
                else:
                    matrix = matrix_correction @ matrix_basis

                translation, tmp_rotation, tmp_scale = decompose_transform_swizzle(matrix)

                export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]] = [translation, tmp_rotation, tmp_scale]
        else:
            channel_index = 0
            for blender_fcurve in location:

                if blender_fcurve is not None:

                    if interpolation == 'CUBICSPLINE':
                        blender_key_frame = blender_fcurve.keyframe_points[keyframe_index]

                        translation[channel_index] = blender_key_frame.co[1]

                        in_tangent[channel_index] = 3.0 * (blender_key_frame.co[1] - blender_key_frame.handle_left[1])
                        out_tangent[channel_index] = 3.0 * (blender_key_frame.handle_right[1] - blender_key_frame.co[1])
                    else:
                        value = blender_fcurve.evaluate(keys[keyframe_index])

                        translation[channel_index] = value

                channel_index += 1

            translation = convert_swizzle_location(translation)
            in_tangent = convert_swizzle_location(in_tangent)
            out_tangent = convert_swizzle_location(out_tangent)

        result[time] = translation
        result_in_tangent[time] = in_tangent
        result_out_tangent[time] = out_tangent

        keyframe_index += 1

    return result, result_in_tangent, result_out_tangent


def animate_rotation_axis_angle(export_settings, rotation_axis_angle, interpolation, node_type, node_name, matrix_correction, matrix_basis):
    """
    Calculates/gathers the key value pairs for axis angle transformations.
    """
    if not export_settings['gltf_joint_cache'].get(node_name):
        export_settings['gltf_joint_cache'][node_name] = {}

    keys = animate_gather_keys(export_settings, rotation_axis_angle, interpolation)

    times = animate_convert_keys(keys)

    result = {}

    keyframe_index = 0
    for time in times:
        axis_angle_rotation = [1.0, 0.0, 0.0, 0.0]

        rotation = [1.0, 0.0, 0.0, 0.0]

        if node_type == 'JOINT':
            if export_settings['gltf_joint_cache'][node_name].get(keys[keyframe_index]):
                tmp_location, rotation, tmp_scale = export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]]
            else:
                bpy.context.scene.frame_set(keys[keyframe_index])

                if bpy.app.version < (2,80,0):
                    matrix = matrix_correction * matrix_basis
                else:
                    matrix = matrix_correction @ matrix_basis

                tmp_location, rotation, tmp_scale = decompose_transform_swizzle(matrix)

                export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]] = [tmp_location, rotation, tmp_scale]
        else:
            channel_index = 0
            for blender_fcurve in rotation_axis_angle:
                if blender_fcurve is not None:
                    value = blender_fcurve.evaluate(keys[keyframe_index])

                    axis_angle_rotation[channel_index] = value

                channel_index += 1

            rotation = animate_convert_rotation_axis_angle(axis_angle_rotation)

            # Bring back to internal Quaternion notation.
            rotation = convert_swizzle_rotation([rotation[3], rotation[0], rotation[1], rotation[2]])

            if node_type == 'NODE_X_90':
                if bpy.app.version < (2,80,0):
                    rotation = rotation * mathutils.Quaternion((1.0, 0.0, 0.0), -math.pi/2)
                else:
                    rotation = rotation @ mathutils.Quaternion((1.0, 0.0, 0.0), -math.pi/2)

        # Bring back to glTF Quaternion notation.
        rotation = [rotation[1], rotation[2], rotation[3], rotation[0]]

        result[time] = rotation

        keyframe_index += 1

    return result


def animate_rotation_euler(export_settings, rotation_euler, rotation_mode, interpolation, node_type, node_name, matrix_correction, matrix_basis):
    """
    Calculates/gathers the key value pairs for euler angle transformations.
    """
    if not export_settings['gltf_joint_cache'].get(node_name):
        export_settings['gltf_joint_cache'][node_name] = {}

    keys = animate_gather_keys(export_settings, rotation_euler, interpolation)

    times = animate_convert_keys(keys)

    result = {}

    keyframe_index = 0
    for time in times:
        euler_rotation = [0.0, 0.0, 0.0]

        rotation = [1.0, 0.0, 0.0, 0.0]

        if node_type == 'JOINT':
            if export_settings['gltf_joint_cache'][node_name].get(keys[keyframe_index]):
                tmp_location, rotation, tmp_scale = export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]]
            else:
                bpy.context.scene.frame_set(keys[keyframe_index])

                if bpy.app.version < (2,80,0):
                    matrix = matrix_correction * matrix_basis
                else:
                    matrix = matrix_correction @ matrix_basis

                tmp_location, rotation, tmp_scale = decompose_transform_swizzle(matrix)

                export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]] = [tmp_location, rotation, tmp_scale]
        else:
            channel_index = 0
            for blender_fcurve in rotation_euler:
                if blender_fcurve is not None:
                    value = blender_fcurve.evaluate(keys[keyframe_index])

                    euler_rotation[channel_index] = value

                channel_index += 1

            rotation = animate_convert_rotation_euler(euler_rotation, rotation_mode)

            # Bring back to internal Quaternion notation.
            rotation = convert_swizzle_rotation([rotation[3], rotation[0], rotation[1], rotation[2]])

            if node_type == 'NODE_X_90':
                if bpy.app.version < (2,80,0):
                    rotation = rotation * mathutils.Quaternion((1.0, 0.0, 0.0), -math.pi/2)
                else:
                    rotation = rotation @ mathutils.Quaternion((1.0, 0.0, 0.0), -math.pi/2)

        # Bring back to glTF Quaternion notation.
        rotation = [rotation[1], rotation[2], rotation[3], rotation[0]]

        result[time] = rotation

        keyframe_index += 1

    return result


def animate_rotation_quaternion(export_settings, rotation_quaternion, interpolation, node_type, node_name, matrix_correction, matrix_basis):
    """
    Calculates/gathers the key value pairs for quaternion transformations.
    """
    if not export_settings['gltf_joint_cache'].get(node_name):
        export_settings['gltf_joint_cache'][node_name] = {}

    keys = animate_gather_keys(export_settings, rotation_quaternion, interpolation)

    times = animate_convert_keys(keys)

    result = {}
    result_in_tangent = {}
    result_out_tangent = {}

    keyframe_index = 0
    for time in times:
        rotation = [1.0, 0.0, 0.0, 0.0]
        in_tangent = [1.0, 0.0, 0.0, 0.0]
        out_tangent = [1.0, 0.0, 0.0, 0.0]

        if node_type == 'JOINT':
            if export_settings['gltf_joint_cache'][node_name].get(keys[keyframe_index]):
                tmp_location, rotation, tmp_scale = export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]]
            else:
                bpy.context.scene.frame_set(keys[keyframe_index])

                if bpy.app.version < (2,80,0):
                    matrix = matrix_correction * matrix_basis
                else:
                    matrix = matrix_correction @ matrix_basis

                tmp_location, rotation, tmp_scale = decompose_transform_swizzle(matrix)

                export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]] = [tmp_location, rotation, tmp_scale]
        else:
            channel_index = 0
            for blender_fcurve in rotation_quaternion:

                if blender_fcurve is not None:
                    if interpolation == 'CUBICSPLINE':
                        blender_key_frame = blender_fcurve.keyframe_points[keyframe_index]

                        rotation[channel_index] = blender_key_frame.co[1]

                        in_tangent[channel_index] = 3.0 * (blender_key_frame.co[1] - blender_key_frame.handle_left[1])
                        out_tangent[channel_index] = 3.0 * (blender_key_frame.handle_right[1] - blender_key_frame.co[1])
                    else:
                        value = blender_fcurve.evaluate(keys[keyframe_index])

                        rotation[channel_index] = value

                channel_index += 1

            # NOTE: fcurve.evaluate() requires normalization
            q = mathutils.Quaternion((rotation[0],rotation[1], rotation[2], rotation[3])).normalized()
            rotation = [q[0], q[1], q[2], q[3]]

            rotation = convert_swizzle_rotation(rotation)

            in_tangent = convert_swizzle_rotation(in_tangent)
            out_tangent = convert_swizzle_rotation(out_tangent)

            if node_type == 'NODE_X_90':
                quat_x90 = mathutils.Quaternion((1.0, 0.0, 0.0), -math.pi/2)

                if bpy.app.version < (2,80,0):
                    rotation = rotation * quat_x90
                    in_tangent = in_tangent * quat_x90
                    out_tangent = out_tangent * quat_x90
                else:
                    rotation = rotation @ quat_x90
                    in_tangent = in_tangent @ quat_x90
                    out_tangent = out_tangent @ quat_x90


        # Bring to glTF Quaternion notation.
        rotation = [rotation[1], rotation[2], rotation[3], rotation[0]]
        in_tangent = [in_tangent[1], in_tangent[2], in_tangent[3], in_tangent[0]]
        out_tangent = [out_tangent[1], out_tangent[2], out_tangent[3], out_tangent[0]]

        result[time] = rotation
        result_in_tangent[time] = in_tangent
        result_out_tangent[time] = out_tangent

        keyframe_index += 1

    return result, result_in_tangent, result_out_tangent


def animate_scale(export_settings, scale, interpolation, node_type, node_name, matrix_correction, matrix_basis):
    """
    Calculates/gathers the key value pairs for scale transformations.
    """
    if not export_settings['gltf_joint_cache'].get(node_name):
        export_settings['gltf_joint_cache'][node_name] = {}

    keys = animate_gather_keys(export_settings, scale, interpolation)

    times = animate_convert_keys(keys)

    result = {}
    result_in_tangent = {}
    result_out_tangent = {}

    keyframe_index = 0
    for time in times:
        scale_data = [1.0, 1.0, 1.0]
        in_tangent = [0.0, 0.0, 0.0]
        out_tangent = [0.0, 0.0, 0.0]

        if node_type == 'JOINT':
            if export_settings['gltf_joint_cache'][node_name].get(keys[keyframe_index]):
                tmp_location, tmp_rotation, scale_data = export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]]
            else:
                bpy.context.scene.frame_set(keys[keyframe_index])

                if bpy.app.version < (2,80,0):
                    matrix = matrix_correction * matrix_basis
                else:
                    matrix = matrix_correction @ matrix_basis

                tmp_location, tmp_rotation, scale_data = decompose_transform_swizzle(matrix)

                export_settings['gltf_joint_cache'][node_name][keys[keyframe_index]] = [tmp_location, tmp_rotation, scale_data]
        else:
            channel_index = 0
            for blender_fcurve in scale:

                if blender_fcurve is not None:
                    if interpolation == 'CUBICSPLINE':
                        blender_key_frame = blender_fcurve.keyframe_points[keyframe_index]

                        scale_data[channel_index] = blender_key_frame.co[1]

                        in_tangent[channel_index] = 3.0 * (blender_key_frame.co[1] - blender_key_frame.handle_left[1])
                        out_tangent[channel_index] = 3.0 * (blender_key_frame.handle_right[1] - blender_key_frame.co[1])
                    else:
                        value = blender_fcurve.evaluate(keys[keyframe_index])

                        scale_data[channel_index] = value

                channel_index += 1

            scale_data = convert_swizzle_scale(scale_data)
            in_tangent = convert_swizzle_scale(in_tangent)
            out_tangent = convert_swizzle_scale(out_tangent)

        result[time] = scale_data
        result_in_tangent[time] = in_tangent
        result_out_tangent[time] = out_tangent

        keyframe_index += 1

    return result, result_in_tangent, result_out_tangent


def animate_value(export_settings, value_parameter, interpolation, node_type, node_name, matrix_correction, matrix_basis):
    """
    Calculates/gathers the key value pairs for scalar anaimations.
    """
    keys = animate_gather_keys(export_settings, value_parameter, interpolation)

    times = animate_convert_keys(keys)

    result = {}
    result_in_tangent = {}
    result_out_tangent = {}

    keyframe_index = 0
    for time in times:
        value_data = []
        in_tangent = []
        out_tangent = []

        for blender_fcurve in value_parameter:

            if blender_fcurve is not None:
                if interpolation == 'CUBICSPLINE':
                    blender_key_frame = blender_fcurve.keyframe_points[keyframe_index]

                    value_data.append(blender_key_frame.co[1])

                    in_tangent.append(3.0 * (blender_key_frame.co[1] - blender_key_frame.handle_left[1]))
                    out_tangent.append(3.0 * (blender_key_frame.handle_right[1] - blender_key_frame.co[1]))
                else:
                    value = blender_fcurve.evaluate(keys[keyframe_index])

                    value_data.append(value)

        result[time] = value_data
        result_in_tangent[time] = in_tangent
        result_out_tangent[time] = out_tangent

        keyframe_index += 1

    return result, result_in_tangent, result_out_tangent

def animate_default_value(export_settings, default_value, interpolation):
    """
    Calculate/gather the key value pairs for node material animation.
    """

    keys = animate_gather_keys(export_settings, default_value, interpolation)

    times = animate_convert_keys(keys)

    result = {}
    result_in_tangent = {}
    result_out_tangent = {}

    keyframe_index = 0
    for time in times:
        def_value_data = [1.0, 1.0, 1.0, 1.0]
        in_tangent = [0.0, 0.0, 0.0, 0.0]
        out_tangent = [0.0, 0.0, 0.0, 0.0]

        channel_index = 0
        for bl_fcurve in default_value:

            if bl_fcurve is not None:
                if interpolation == 'CUBICSPLINE':
                    blender_key_frame = bl_fcurve.keyframe_points[keyframe_index]

                    def_value_data[channel_index] = blender_key_frame.co[1]
                    in_tangent[channel_index] = 3.0 * (blender_key_frame.co[1] - blender_key_frame.handle_left[1])
                    out_tangent[channel_index] = 3.0 * (blender_key_frame.handle_right[1] - blender_key_frame.co[1])
                else:
                    value = bl_fcurve.evaluate(keys[keyframe_index])

                    def_value_data[channel_index] = value

            channel_index += 1

        result[time] = def_value_data
        result_in_tangent[time] = in_tangent
        result_out_tangent[time] = out_tangent

        keyframe_index += 1

    return result, result_in_tangent, result_out_tangent

def animate_energy(export_settings, energy, interpolation):
    """
    Calculate/gather the key value pairs for node material animation.
    """

    keys = animate_gather_keys(export_settings, energy, interpolation)

    times = animate_convert_keys(keys)

    result = {}
    result_in_tangent = {}
    result_out_tangent = {}

    keyframe_index = 0
    for time in times:
        energy_data = [1.0]
        in_tangent = [0.0]
        out_tangent = [0.0]

        channel_index = 0
        for bl_fcurve in energy:

            if bl_fcurve is not None:
                if interpolation == 'CUBICSPLINE':
                    blender_key_frame = bl_fcurve.keyframe_points[keyframe_index]

                    energy_data[channel_index] = blender_key_frame.co[1]
                    in_tangent[channel_index] = 3.0 * (blender_key_frame.co[1] - blender_key_frame.handle_left[1])
                    out_tangent[channel_index] = 3.0 * (blender_key_frame.handle_right[1] - blender_key_frame.co[1])
                else:
                    value = bl_fcurve.evaluate(keys[keyframe_index])

                    energy_data[channel_index] = value

            channel_index += 1

        result[time] = energy_data
        result_in_tangent[time] = in_tangent
        result_out_tangent[time] = out_tangent

        keyframe_index += 1

    return result, result_in_tangent, result_out_tangent
