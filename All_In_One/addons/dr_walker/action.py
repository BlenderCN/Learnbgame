# Create an offsetting version of a non-offsetting action
# Copyright (C) 2012  Bassam Kurdali
#
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

# <pep8-80 compliant>

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
else:
    from . import utils

import bpy
from mathutils import Vector


def location_curves(channel, action):
    """ return a list of location curves for the given channel in an action """
    return sorted((
        cu for cu in action.fcurves
        if '["{}"].location'.format(channel) in cu.data_path),
        key=lambda x:x.array_index)


def get_local_value(curves, index):
    """ return a Vector from some curves at a given index """
    values = []
    for i in range(3):
        curves_axis = [cu for cu in curves if cu.array_index == i]
        if curves_axis:
            values.append(curves_axis[0].keyframe_points[index].co[1])
        else:
            values.append(0.0)
    return Vector(values)


def get_value(channel, curves, index, obj):
    """ return a Vector from some curves at a given index """
    value = get_local_value(curves, index)
    return utils.bone_to_object(value, obj, channel, True)


def offset_length(channel, action, obj):
    """ return offset in location of channel during the action """
    curves = location_curves(channel, action)
    return (
        get_value(channel, curves, -1, obj) -
        get_value(channel, curves, 0, obj)).length


def get_stride(stride, action, obj):
    """ return the stride offset of an action based on the stride bone """
    return offset_length(stride, action, obj)


def check_keframe_count(curves):
    """ raise an error if keyframes don't line up! """
    # TODO stub


def sample_curves(channel, curves, frame, obj):
    """ return the value of the curves at a given frame """
    values = []
    for i in range(3):
        curves_axis = [cu for cu in curves if cu.array_index == i]
        if curves_axis:
            values.append(curves_axis[0].evaluate(frame))
        else:
            values.append(0.0)
    return utils.bone_to_object(Vector(values), obj, channel, True)


def offset_frame(channel, curves, frame, obj):
    """ return the offset of curves from first kp at frame frame """
    return sample_curves(channel, curves, frame, obj) - get_value(channel, curves, 0, obj)


def create_offset(channel, action, stride, rig_object):
    """ offset a channel by the amount of striding in the stride bone """
    curves = location_curves(channel, action)
    check_keframe_count(curves)
    stride_curves = location_curves(stride, action)
    values = (
        get_value(channel, curves, index, rig_object) for
        index, dummy in enumerate(curves[0].keyframe_points))
    initial_value = values.__next__()
    for index, value in enumerate(values):
        frame = curves[0].keyframe_points[index + 1].co[0]
        fixed = value - offset_frame(stride, stride_curves, frame, rig_object)
        fixed = utils.object_to_bone_generic(fixed, rig_object, channel, True)
        print(channel, "frame", frame, value, fixed)
        for array_index, curve in enumerate(curves):
            offset = fixed[array_index] - curve.keyframe_points[index + 1].co[1]
            curve.keyframe_points[index + 1].co[1] = fixed[array_index]
            try:
                curve.keyframe_points[index + 1].handle_left[1] += offset
                curve.keyframe_points[index + 1].handle_right[1] += offset
            except:
                pass
    for curve in curves:
        curve.update()


def offset_bones(bones, action, stride, rig_object):
    """ offset all the channels for bone locations based on the stride """
    for bone in bones:
        create_offset(bone, action, stride, rig_object)


def reference_action(bones, action, delta, rig_object, stride=None):
    """ returns reference action duplicating and offsetting if needed """
    offsets = [offset_length(bone, action, rig_object) for bone in bones]
    if all(offset > delta for offset in offsets):
        return action
    elif any(offset > delta for offset in offsets):
        return None  # all or nothing       
    else:
        offset_action = action.copy()
        print(offset_action.name)
        if stride:
            offset_bones(bones, offset_action, stride, rig_object)
            return offset_action
        else:
            return None


def time_offset(action, limits, frames):
    """ returns a time offset version of the action """
    scale = (frames[1] - frames[0]) / (limits[1] - limits[0])
    offset = frames[0]
    center = limits[0]
    def frame_offset(frame):
        return scale * (frame - center) + offset
    offset_action = action.copy()
    for fcurve in offset_action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.co[0] = frame_offset(kp.co[0])
            kp.handle_left[0] = frame_offset(kp.handle_left[0])
            kp.handle_right[0] = frame_offset(kp.handle_right[0])
        fcurve.update() 
    return offset_action          
    
