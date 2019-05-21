# Orox uses Animated or MoCap walkcycles to generate footstep driven walks
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
TODO

2- generate footsteps compatible with path parenting and use feet directly
   in first pose rather than target bones (means disable animation temporarily
   then re-enable) - make sure this is an option (for instance, future workflow
   could be to animate locations, generate footsteps, and then use a reference)
3- ???
4- profit
"""

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    importlib.reload(rig)
    importlib.reload(action)

else:
    from . import action
    from . import utils
    from . import rig

import bpy
import imp
from pprint import pprint
from mathutils import Vector, Quaternion, Matrix, Euler, Color
from .utils import *

DEBUG = True

def body_location_optimize(
        body_average, average_distance_cycle,
        average_step, locations, old_values=[]):
    """
    recursively get better distance to things
    """
    labda = .0001
    average_dist = average_distance(body_average, locations)
    if old_values == []:
        old_values.append(average_step)
    old_values.append(body_average)
    name = "x_{}_{}".format(int(average_step.length), len(old_values))
    old_values.sort(key=lambda x: (x - average_step).length)
    my_rank = old_values.index(body_average)

    if average_dist > average_distance_cycle + labda:
        if my_rank == 0:
            return body_average
        else:
            new_average = average((body_average, old_values[my_rank - 1]))

    elif average_dist < average_distance_cycle - labda:
        if my_rank < len(old_values) - 1:
            new_average = average((body_average, old_values[my_rank + 1]))

        else:

            new_average = body_average + body_average - average_step
    else:
        new_average = body_average

    if (new_average - body_average).length <= 2 * labda:
        body_average = new_average
        return body_average
    else:
        new_average = body_location_optimize(
            new_average, average_distance_cycle,
            average_step, locations, old_values)
        body_average = new_average
        return body_average


class Parambulator(object):
    """ we likely have to modify this, but we need to inherit rig params """
    
    def __init__(self, rig_data, walker_object, action, reference=None):
        self.object = walker_object
        self.rig_data = rig_data
        if type(action) == str:
            self.action = action
        else:
            self.action = action.name
        self.set_stride()
        self.in_air_start = 0.2 # defaults.in_air_start
        self.in_air_end = 0.8 # defaults.in_air_end
        self.flip = False
        self.walk_data = {}
        self.injest_action()
        self.walkcycles_curves = {}
        self.prep_action(blank=False)
        self.footstep_stride_multiplier = 1.0
 
    def set_action(self, action):
        """ add a reference action to a parambulator """
        if type(action) == str:
            self.action = action
        else:
            self.action = action.name
        self.set_stride()
        self.injest_action()
        self.prep_action(blank=True)

    def get_offset(self, foot, offmat):
        """
        calculate an initial offset per bone
        """
        obj = self.object
        action = self.action
        walk_data = self.walk_data[action]

        transform = walk_data['offsets'][foot.name]
        bone_world_mat = Matrix.Translation(transform)
        offset_inv = bone_world_mat.inverted() * obj.matrix_world * offmat
        return offset_inv.inverted().to_translation()   

    def offset_targets(self):
        """
        create the initial conditions we need for a smooth walk
        feet are data structures
        targets are pose bones
        """
        feet = self.rig_data.feet
        bones = self.object.pose.bones
        stride = self.actions[self.action]
        walk_data = self.walk_data[self.action]
        for foot in feet:
            target = bones[foot.target]
            mat = walk_data['mats'][foot.name]
            offset = world_location_to_bone(
                walk_data['offsets'][foot.name],
                target.id_data, target.name)
            scale = mat.to_scale().length
            new_offset = (scale / stride) * offset
            # target.location = new_offset  let's try being dumb instead:
            # FIXME needs to take stride multiplier into account
            target.location = offset
           
    def set_stride(self):
        """ get the stride from the reference action """
        obj = self.object
        act = bpy.data.actions[self.action]
        body_name = self.rig_data.feet[0].name  # XXX  assumes one body
        prop_holder = obj.pose.bones[self.rig_data.properties]
        self.stride = action.get_stride(
            self.rig_data.feet[0].name,
            bpy.data.actions[self.action], obj)       

    def calculate_body(self, body, steps):
        """
        get the body location and frame based on it's foot-steps
        """
        data = self.walk_data[self.action]
        frames = [step['frame'] for step in steps]
        frame = int(average(frames))
        locations = [step['location'] for step in steps]
        originals = []
        for i in range(len(steps)):
            footbone = self.rig_data.feet[body.deps[i]].name
            originals.append(data['offsets'][footbone])
        # step 1 find the average location.
        average_step = average(locations)
        # step 2 for each location find the walkcycle warped body location
        body_original = data['offsets'][body.name]
        warped_locations = []
        for index, location in enumerate(locations):
            original = data['offsets'][self.rig_data.feet[body.deps[index]].name]
            warped_locations.append(location + body_original - original)
        # step 3 average the results of step 2
        body_average = average(warped_locations)
        # step 4 find the average body-foot distance in the walkcycle
        average_distance_cycle = average_distance(body_original, originals)
        # step 5 find the average body-foot distance currently
        average_distance_step = average_distance(body_average, locations)
        # step 6 move the position on the line between step 3
        # and step 1 to minimize step 5

        #average_distance_cycle *= 1.3

        result = body_location_optimize(
            body_average, average_distance_cycle,
            average_step, locations, [])

        #result = body_average
        scene = bpy.context.scene
        new_name = "_B{}_{}_{}".format(
            self.object.name, self.rig_data.feet.index(body), frame)
        props = {'frame': frame, 'name': body.name}
        return({'frame': frame, 'location': result})

    def blank_action_copy(self, nuevo, curveset=None):
        """
        copy curves from an action into a nuevo action, optionally restrict by
        curveset, exact implementation of restriction TBD
        """
        action = bpy.data.actions[self.action]
        #copy channels from action
        for group in action.groups:
            if not group.name in nuevo.groups:
                nuevo.groups.new(name=group.name)
        for fcurve in action.fcurves:
            try:
                    nuevo.fcurves.new(
                        data_path=fcurve.data_path,
                        index=fcurve.array_index,
                        action_group=\
                            "" if not fcurve.group else fcurve.group.name)
            except RuntimeError:
                old_curve = [
                    fc for fc in nuevo.fcurves if
                    fc.data_path == fcurve.data_path and
                    fc.array_index == fcurve.array_index][0]
                nuevo.fcurves.remove(old_curve)
                nuevo.fcurves.new(
                    data_path=fcurve.data_path,
                    index=fcurve.array_index,
                    action_group=\
                        "" if not fcurve.group else fcurve.group.name)
        return nuevo

    def injest_action(self):
        """
        get the walk matrixes time limits out of the reference action
        """
        print("self.action = ",self.action)
        if self.action in self.walk_data:
            return
        flip = self.flip
        source_walkcycle = bpy.data.actions[self.action]
        walkcycle_curves = group_curves(source_walkcycle.fcurves)
        old_frames = [int(frame) for frame in source_walkcycle.frame_range]

        # now we need the old offsets for any bone in feet or main target track
        walkcycle_mats = {}
        offsets = {}
        contacts = {}
        for foot in self.rig_data.feet:
            # we assume contacts are at the first and last frame
            # start and end location are important to us
            location_curves = walkcycle_curves[foot.name]['location']
            start_location = Vector([
                curve.evaluate(old_frames[0]) for curve in location_curves])
            end_location = Vector([
                curve.evaluate(old_frames[1]) for curve in location_curves])
            distance = (end_location - start_location).length
            # find out where the foot is off the ground
            # evaluate the curve and set frame percentages:
            start = old_frames[0]
            end = old_frames[1]
            for frame in range(old_frames[0], old_frames[1]):
                location = Vector([
                    curve.evaluate(frame) for curve in location_curves])
                percentage = (location - start_location).length / distance
                if percentage < self.in_air_start:
                    start = frame
                elif percentage < self.in_air_end:
                    end = frame
                else:
                    break
            # FIXME The above essentially assumes monotonically increasing
            # distance which is not neccessarily true: something bad might
            # happen foroff-beat walkcycles
            # now put everything in world coordinates for sanity
            start_location = bone_to_world(
                start_location, self.object, foot.name, True)
            end_location = bone_to_world(
                end_location, self.object, foot.name, True)
            # stuff our actual data in
            walkcycle_mats[foot.name] = offset_matrix(
                start_location, end_location,
                flip_axis(foot.forward, flip), foot.up)
            offsets[foot.name] = start_location
            contacts[foot.name] = (start, end)
        self.walk_data[self.action] = {'limits': old_frames,
            'mats': walkcycle_mats,
            'offsets': offsets,
            'contacts': contacts}

    def prep_action(self, blank=True):
        """
        prep our blank action for a good go
        """
        source_walkcycle = bpy.data.actions[self.action]
        if not self.action in self.walkcycles_curves.keys():
            walkcycle_curves = group_curves(source_walkcycle.fcurves)
            self.walkcycles_curves[self.action] = walkcycle_curves
        else:
            walkcycle_curves = self.walkcycles_curves[self.action]
        obj = self.object
        if not obj.animation_data:
            obj.animation_data_create()
        if obj.animation_data.action:
            # XXX Insure walker actions are unique!!!!
            target_walk = obj.animation_data.action
            if blank:
                self.blank_action_copy(target_walk)
        else:
            target_walk = bpy.data.actions.new(name="forward")
            obj.animation_data.action = target_walk
            self.blank_action_copy(target_walk)
        self.walk_curves = group_curves(target_walk.fcurves)
        body_tracks = set([
            bone for bone in self.walk_curves if bone not in [
                foot.name for foot in self.rig_data.feet]])
        for foot in self.rig_data.feet[-1:]:
            body_tracks = body_tracks.difference(set(foot.tracks))
        for bone in list(body_tracks):
            self.rig_data.feet[0].tracks.append(bone) # XXX only one body!!!!

    def copy_transforms(
            self, 
            context, pose_bone, loc_list,
            time_map, step_rots, step_mat, time_ramp, foot):
        """
        make walk keyframes in the new curves based on the old curves.
        """
        #assume that keyframes line up
        walk_data = self.walk_data[self.action]
        old_curves = self.walkcycles_curves[self.action]
        new_curves = self.walk_curves
        walk_mat = walk_data['mats'][foot.name]
        contacts = walk_data['contacts'][foot.name]
        limits = walk_data['limits']

        scene = context.scene
        bone = pose_bone.name
        rotation_mode = pose_bone.rotation_mode
        obj = pose_bone.id_data  # ok to just grab this rather than pass it?
        data_bone = obj.data.bones[bone]
        rest_mat = obj.matrix_world * data_bone.matrix_local

        for transform in old_curves[bone]:

            length = 4 if transform in [
                'rotation_quaternion', 'rotation_axis_angle'] else 3
            offmult = [
                Vector((0 for i in range(length))),
                Vector((1 for i in range(length)))]

            for param in pose_bone.autowalkparams:
                if param.tform == transform:
                    scaler = param_value(scene, param.name, obj.data.name)
                    if param.multiplier:
                        mapped = 1 + abs(scaler) * 9
                        mult_scaler = mapped if scaler >= 0 else 1 / mapped
                        value = vectorize_param_value(
                            length, mult_scaler, param, True)
                        offmult[1] = Vector([
                            offmult[1][n]*value[n] for n in range(length)])
                    else:
                        value = vectorize_param_value(
                            length, scaler, param, False)
                        offmult[0] = offmult[0] + value

            old_keyframes = keyframes_from_curves(old_curves[bone][transform])
            new_transform = new_curves[bone][transform]
            use_deform = pose_bone.walkdeform and any([
                trigger in transform for trigger in ('location', 'rotation')])

            for keyframe_set in old_keyframes:
                if use_deform and 'location' in transform:
                    local_location = pose_bone.id_data.data.bones[
                        bone].use_local_location
                    overrides = warp_core_location(
                        keyframe_set, time_ramp, offmult, limits,
                        step_mat, walk_mat, rest_mat,
                        local_location)
                elif use_deform and 'rotation' in transform:
                    flip = False# context.scene.flip_walker
                    overrides = warp_core_rotation(
                        keyframe_set, time_ramp, offmult, limits, flip, foot,
                        rotation_mode, step_rots, step_mat, walk_mat, rest_mat,
                        contacts)
                else:
                    overrides = warp_core_nodeform(
                        keyframe_set, time_ramp, offmult, limits)
                for curve in new_transform:
                    curve.keyframe_points.add()
                new_keyframes = [
                    curve.keyframe_points[-1] for curve in new_transform]
                for old_keyframe, new_keyframe, override in zip(
                        keyframe_set, new_keyframes, overrides):
                    copy_coords(old_keyframe, new_keyframe, override)

    def bake_steps(
        self, context, foot, anim_bones):
        """
        bake the steps from a foot that has steps onto anim_bones
        """
        walk_data = self.walk_data[self.action]
        flip = self.flip
        old_start = walk_data['limits'][0]
        old_end = walk_data['limits'][1]
        cycle_len = old_end - old_start
        penultimate_step = len(foot.steps) - 2
        for index, footstep in enumerate(foot.steps[:-1]):
            nextstep = foot.steps[index + 1]
            loc_list = [footstep['location'], nextstep['location']]
            step_mat = offset_matrix(
                loc_list[0], loc_list[1],
                flip_axis(foot.forward, flip), foot.up)
            step_rots = (
                footstep['rotation'], foot.steps[index + 1]['rotation'])
            if index < penultimate_step:
                loc_list.append(foot.steps[index + 2]['location'])
            time_map = (footstep['frame'], nextstep['frame'])
            step_time = time_map[1] - time_map[0]
            multiplier = step_time / cycle_len
            offset = time_map[0] - multiplier * old_start
            for bone in anim_bones:
                print(step_rots)

                self.copy_transforms(
                    context,
                    bone, loc_list, time_map,
                    step_rots, step_mat, (offset, multiplier), foot)

    def bake_walk(self, context):
        """
        This populates each walker action with it's new modified curves.
        """

        pbones = self.object.pose.bones
        for foot in self.rig_data.feet:  # copy each foot's steps individually
            footbones = [bone for bone in foot.tracks] + [foot.name]
            bones = [
                bone for bone in self.walkcycles_curves[self.action]
                if bone in footbones]
            anim_bones = [bone for bone in pbones if bone.name in bones]
            self.bake_steps(context, foot, anim_bones)
      
    
        
