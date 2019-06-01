# Change an action from using eval curves to world space
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
    import importlib
    importlib.reload(utils)
else:
    from . import utils
    from . import path

import bpy
from .utils import *
from mathutils import Matrix, Vector, Quaternion
 
def get_bone_channels(action):
    """ return channels that have bones """
    channels = {}
    for fcurve in action.fcurves:
        path = fcurve.data_path
        if path.startswith('pose.bones["') and not path.endswith('scale'):
            bone = fcurve.data_path[12:].split('"')[0]
            if bone in channels:
                channels[bone].append(fcurve)
            else:
                channels[bone] = [fcurve]
    # now group and sort channels

    for bone in channels:
        channels[bone].sort(key=lambda x:(x.data_path, x.array_index))
        data_paths = set()
        for cu in channels[bone]:
            data_paths.add(cu.data_path)
        grouped_curves = {
            path.split('.')[-1]: [
                cu for cu in channels[bone] if cu.data_path == path]
            for path in data_paths}
        channels[bone] = grouped_curves
    return channels


def check_parent(bone, bones):
    """ True if bone has a parent in bones, False otherwise """
    if not bone.parent in bones:
        return False
    elif bone.parent in bones:
        return True
    else:
        return check_parent(bone, bones) 


def topmost_level(channels, ob, special_bones=None):
    """ we only need consider parent channels """
    channel_keys = [bone for bone in channels]
    all_bones = []
    for bone in channel_keys:
        if not special_bones or bone in special_bones:
            try:
                all_bones.append(ob.data.bones[bone])
            except KeyError:
                channels.pop(bone)
        else:
            channels.pop(bone)
    for bone in all_bones:
        if check_parent(bone, all_bones):
            channels.pop(bone.name)
    return channels


def evaluate_curves(channels, limits):
    """ store evaluated values of curves before clearing """
    values = {}
    for bone, groups in channels.items():
        values[bone] = {data_path: [] for data_path in groups}
        for frame in range(limits[0], limits[1]):
            for data_path in values[bone]:
                values[bone][data_path].append(Vector(
                    cu.evaluate(frame) for cu in groups[data_path]))
    return values


def get_path_offset(context, curve_path, ob, offset):
    """ get the path offset at required value """
    scene = context.scene
    fcurve = path.get_path_eval_curve(curve_path)
    frame = path.frame_from_value(offset, fcurve)
    scene.frame_set(frame)
    return ob.matrix_world



def get_path_offset_at_frame(context, curve_path, ob, frame):
    """ get the path offset at required value """
    scene = context.scene
    scene.frame_set(frame)
    return ob.matrix_world

    
@framepreserve
def bake_path_offsets(context, cu_path, ob, action, specials):
    """ bake path offsets into an action """
    channels = get_bone_channels(action)
    channels = topmost_level(channels, ob, specials)
    limits = (int(action.frame_range[0]), 2  + int(action.frame_range[1]))
    values = evaluate_curves(channels, limits)
    zero_offset = get_path_offset(context, cu_path, ob, 0).copy()
    for bone, groups in channels.items():

        for data_path, curves in groups.items():
            data = [(cu.data_path, cu.array_index, cu.group.name) for cu in curves]
            while curves:
                cu = curves.pop(-1)
                action.fcurves.remove(cu)
            for datum in data:
                cu = action.fcurves.new(datum[0], datum[1], datum[2])
                curves.append(cu)
    for frame in range(limits[0], limits[1]):
        context.scene.frame_set(frame)
        current_offset = ob.matrix_world
        print(ob.name, current_offset.to_translation() , zero_offset.to_translation())
        for bone, groups in channels.items():
            for transforms in 'location', 'rotation_quaternion':
                if 'location' in groups:
                    old_loc = values[bone]['location'][frame - limits[0]]
                else:
                    old_loc = Vector((0,0,0))
                if 'rotation_quaternion' in groups:
                    old_rot = Quaternion(values[bone]['rotation_quaternion'][frame - limits[0]])
                else:
                    old_rot = Quaternion((1, 0, 0, 0))
            old_trans = Matrix.Translation(old_loc).to_4x4() * old_rot.to_matrix().to_4x4()
            rest_mat = ob.data.bones[bone].matrix_local
            old_trans_world = current_offset * rest_mat * old_trans
            new_trans =\
                rest_mat.inverted() * zero_offset.inverted() * old_trans_world
            new_loc, new_rot, sca = new_trans.decompose()
            for group, curves in groups.items():
                for array_index, curve in enumerate(curves):
                    if curve.data_path.endswith('location'):
                        insert_keyframe_curve(
                            curve, frame, new_loc[array_index], 'LINEAR')
                    else:
                        insert_keyframe_curve(
                            curve, frame, new_rot[array_index], 'LINEAR')

        
        



    

    
