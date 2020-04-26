# Footstep Generation independent from walk
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


"""
Footsteps from path (object is parented to path
1- temporarily disable all NLA animation
2- pose feet and body based on first frame of action
3- get stride percentages from path.
4- store world step position at each stride

"""

if "bpy" in locals():
    import importlib
    importlib.reload(action)
    importlib.reload(path)
    importlib.reload(utils)
else:
    from . import action
    from . import path
    from . import utils

import bpy
from .utils import *
from mathutils import Vector, Quaternion, Matrix, Euler, Color
        
def add_footstep_rotations(feet):
    '''
    add rotations into footstep series
    '''
    for foot in feet:
        for index, step in enumerate(foot.steps):
            current = step['location']
            vector = foot.steps[
                min(len(foot.steps) - 1, index + 1)]['location'] -\
                foot.steps[max(0, index - 1)]['location']
            step['rotation'] = vector.to_track_quat('Y','Z')


@framepreserve
def steps_from_path(context, parambulator):
    """ generate steps from path """
    scene = context.scene
    feet = parambulator.rig_data.feet
    obj = parambulator.object
    act = bpy.data.actions[parambulator.action]
    stride_length = parambulator.stride
    curve_path = obj.parent
    if obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if any(foot.name in fcurve.data_path for foot in feet):
                fcurve.mute = True
    bones = obj.pose.bones
    for foot in feet:
        obj.pose.bones[foot.name].location = action.get_local_value(
            action.location_curves(foot.name, act), 0)
    stride = parambulator.stride   
    print(stride)
    cycle_frames = path.get_cycle_frames(scene, curve_path, stride_length)
    print(cycle_frames)
    targets = [bones[foot.name] for foot in feet]
    for frame in cycle_frames:
        scene.frame_set(frame)
        for index, bone in enumerate(targets):
            feet[index].steps.append(
                {'location': obj.matrix_world * bone.matrix.to_translation(),
                'frame': frame})
    add_footstep_rotations(feet)
    if obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            fcurve.mute = False
    return cycle_frames # we'll use them later
    


@framepreserve
def steps_from_feet(parambulator, scene, frames):
    '''
    makes a list of footsteps over frames for a list of pose bones
    scene: current scene of type bpy.types.Scene
    frames: integer list of frames
    targets: list of pose bones that are foot-target bones
    strides: list of stride lengths per target
    '''
    feet = parambulator.rig_data.feet
    obj = parambulator.object
    stride = parambulator.stride * parambulator.footstep_stride_multiplier
    
    for foot in feet:
        del foot.steps[:]
    bones = obj.pose.bones
    targets = [bones[foot.name] for foot in feet]
    scene.frame_set(frames[0])

    original_locations = [
        bone.id_data.matrix_world * bone.matrix.to_translation() for
        bone in targets]

    for frame in frames:
        scene.frame_set(frame)
        current_locations = [
            bone.id_data.matrix_world * bone.matrix.to_translation() for
            bone in targets]
        distances = (
            dist_get(original_location, current_location) for
            original_location, current_location in
            zip(original_locations, current_locations))

        for index, distance in enumerate(distances):
            if distance >= stride or frame in [frames[0]]:
                feet[index].steps.append(
                    {'location': current_locations[index], 'frame': frame})
                original_locations[index] = current_locations[index]

    fewest_steps = min([len(foot.steps) for foot in feet])
    for foot in feet:
        if len(foot.steps) > fewest_steps:
            del foot.steps[fewest_steps:]
    for index in range(fewest_steps):
        frames = [foot.steps[index]['frame'] for foot in feet]
        average = int((sum(frames) + 0.5) / len(frames))
        for foot in feet:
            foot.steps[index]['frame'] = average
    add_footstep_rotations(feet)


def steps_from_reference(parambulator, ref_object, frames, offmat):
    '''
    make foosteps offset from a reference object locations... 
    '''

    feet = parambulator.rig_data.feet
    obj = parambulator.objec
    stride = parambulator.stride * parambulator.footstep_stride_multiplier 

   # ref_object = bpy.data.objects['stilton']

    # setup some variables:
    bones = obj.pose.bones

    offsets = [parambulator.get_offset(foot, offmat) for foot in feet]
    for foot in feet:
        foot.steps = []

    # get animation data from our reference:
    curves = [
        curve for curve in ref_object.animation_data.action.fcurves
        if 'location' in curve.data_path]
    curves.sort(key = lambda x: x.array_index)
    
    # Initial conditions:
    original_location = Vector(
        [curve.evaluate(frames[0]) for curve in curves])
    original_frame = frames[0]

    # loop over frames, carving out footsteps...
    for frame in frames:
        current_location = Vector(
            [curve.evaluate(frame) for curve in curves])
        distance = dist_get(original_location, current_location)
        if distance >= stride or frame == frames[-1]:
            vector = current_location - original_location
            stepmat = vector.to_track_quat('-Y','Z').to_matrix()

            for foot, offset in zip(feet, offsets):
               
                foot.steps.append({
                    'location': stepmat * offset + original_location,
                    'frame': original_frame})
            original_location = current_location
            original_frame = frame
    
    # do some housekeeping, rotations, etc...
    add_footstep_rotations(feet)


def remove_walker_footsteps(parambulator, scene):
    '''
    remove visible footsteps from one walker XXX
    '''

    #windex = walkers.index(walker)
    feet = parambulator.rig_data.feet
    names = [
        "_S{}_{}_".format(
            parambulator.object.name,
            feet.index(foot)) for foot in feet]
    obs = [
        ob for ob in scene.objects if
        ob.name.rstrip("0123456789") in names]
    for ob in obs:
        scene.objects.unlink(ob)


def draw_footsteps(parambulator, scene):
    '''
    draw the footsteps as empty objects on screen for editing
    '''
    remove_walker_footsteps(parambulator, scene)
    feet = parambulator.rig_data.feet
    rig = parambulator.rig_data.rig
    obj = parambulator.object
    indie_feet = [foot for foot in feet if foot.deps == []]
    total = len(indie_feet)
    draw_feet = indie_feet
    for foot_no, foot in enumerate(draw_feet):
        footmat_name = '_atmn_{}_{}'.format(obj.name, foot_no)
        try:
            footmat = bpy.data.materials[footmat_name]
        except:
            footmat = bpy.data.materials.new(name=footmat_name)
        scale = .1 + 1.8 * ((foot_no + .5) // 2) / total
        g = .3 * (scale - .1)
        if foot_no % 2:
            r = scale
            b = 0
        else:
            b = scale
            r = 0
        footmat.diffuse_color = Color((r, g, b))
        footsteps = foot.steps
        name = foot.name
        bone = rig.bones[name]
        try:
            stride = obj.pose.bones[parambulator.rig_data.properties]['stride']
            foot_size = stride / 12
        except:
            foot_size = (bone.head - bone.tail).length * 2
        for index, footstep in enumerate(footsteps):
            stepname = "_S{}_{}_{}".format(
                obj.name,
                feet.index(foot), footstep['frame'])
            groupname = "_SG{}_{}".format(
                obj.name,
                footstep['frame'])
            props = {'frame': footstep['frame'], 'foot': name}
            try:
                factor = scene.footstep_scale
            except AttributeError:
                factor = 1
            make_marker(
                bpy.context, stepname,
                footstep['location'], footstep['rotation'], props,
                foot_size * factor, footmat, groupname)
      
        
