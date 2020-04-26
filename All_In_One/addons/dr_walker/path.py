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
# Copyright 2015 Bassam Kurdali 

if "bpy" in locals():
    import importlib
    importlib.reload(action)

else:
    from . import action

import bpy


def get_path_eval_curve(curve_ob):
    """ return the evaluation time curve of a path """
    eval_time_curve = None
    if curve_ob and curve_ob.data and curve_ob.data.animation_data and\
            curve_ob.data.animation_data.action:
        eval_times = [
            cu for cu in curve_ob.data.animation_data.action.fcurves
            if cu.data_path == 'eval_time']
        if eval_times:
            eval_time_curve = eval_times[0]
    return eval_time_curve


def eval_time_activate(curve_ob, flag):
    """ Mute and zero or enable eval_time curve """
    eval_time_curve = get_path_eval_curve(curve_ob)
    if eval_time_curve:
        eval_time_curve.mute = not flag
        if not flag:
            curve_ob.data.eval_time = 0   


def location_at_frame(scene, ob, frame, fraction=0.0):
    """ return the location of an object at frame frame """
    scene.frame_set(scene, frame, fraction)
    return ob.matrix_world.to_translation()


def get_curve_length(scene, curve):
    """ return the length of a curve """
    m = curve.to_mesh(scene, True, 'PREVIEW')
    return sum(
        (m.vertices[e.vertices[0]].co - m.vertices[e.vertices[1]].co).length
        for e in m.edges)


def frame_from_value(value, fcurve, limits=None):
    """ return the first frame fcurve reaches a value 
        assumes monotonically increasing values
    """
    limits = fcurve.range() if not limits else limits
    samples = 200  # more samples means less recursion
    delta = 0.001  # accuracy limit for recursion
    for idx in range(0, samples + 1):
        frame = limits[0] + (limits[1] - limits[0]) * idx / samples
        result = fcurve.evaluate(frame)
        if result >= value:
            if idx == 0 or result - delta < value: return frame
            prev = limits[0] + (limits[1] - limits[0]) * (idx - 1) / samples
            frame = frame_from_value(value, fcurve, (prev, frame))
            return frame

    
def stride_segments(stride_length, length):
    """ puts out stride lengths up to total curve length """
    current = 0
    while current < length:
        yield current
        current += stride_length


def get_cycle_frames(scene, curve, stride_length):
    """ cut up walk into stride-times """
    curve_length = get_curve_length(scene, curve)
    fcurve = get_path_eval_curve(curve)
    duration = curve.data.path_duration
    return [
        frame_from_value(duration * val/curve_length, fcurve)
        for val in stride_segments(stride_length, curve_length)]


def frame_remapper(action_frame, action_limits, fcurve, fcurve_limits):
    """ map a frame based on a curve segment """
    eval_start = fcurve.evaluate(fcurve_limits[0])
    eval_end = fcurve.evaluate(fcurve_limits[1])
    range_total = eval_end - eval_start
    fraction = (action_frame - action_limits[0]) / (action_limits[1] - action_limits[0])
    return frame_from_value(
        range_total * fraction + eval_start, fcurve, fcurve_limits)


def frame_mapper(frame, action_limits, fcurve, stride_frames):
    """ for a given real frame withing the fcurve limits, get the right frame
        from the action to sample
    """
    eval_frame = fcurve.evaluate(frame)
    start_frame = fcurve.range()[0]
    for end_frame in stride_frames:
        if end_frame >= eval_frame:
            percent = (eval_frame - start_frame) / (end_frame - start_frame)
            return action_limits[0] + percent * (action_limits[1] - action_limits[0])
        else:
            start_frame = end_frame



