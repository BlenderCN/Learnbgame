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
import bpy
import imp

from pprint import pprint
from mathutils import Vector, Quaternion, Matrix, Euler, Color

try:
    from .utils import *
except:
    import utils
    imp.reload(utils)
    from utils import *
import duplicate_group

DEBUG = True

def body_location_optimize(
        body_average, average_distance_cycle,
        average_step, locations, old_values=[]):
    '''
    recursively get better distance to things
    '''
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

class _Defaults:
    __slots__ = (
        "in_air_start",
        "in_air_end",
        )

    def __init__(self):
        '''
        We can rotate a foot when it is in the air, with the idea that 
        the foot is in air between the contact poses + some buffer, so
        if we consider first contact to be 0.0 and second 1.0 :
        in_air_start (Float from 0.0 to in_air_end)
        in_air_end (Float from in_air_start to 1.0)
        '''
        in_air_start = 0.2  # default rotate foot safe from this...
        in_air_end = 0.8  # ... up until this.

defaults = _Defaults()


class RigSettings(object):
    '''stupid class to generate data for the autowalker'''
    def __init__(self, in_dict):
        for val in in_dict:
            if type(in_dict[val]) == dict:
                self.__dict__.update({val: RigSettings(in_dict[val])})
            elif type(in_dict[val]) in (list, tuple):
                in_list = []
                for itm in in_dict[val]:
                    if type(itm) in (list, tuple, dict):
                        in_list.append(RigSettings(itm))
                    else:
                        in_list.append(itm)
                self.__dict__.update({val: in_list})
            else:
                self.__dict__.update({val: in_dict[val]})


class Parambulator(object):
    ''' we likely have to modify this, but we need to inherit rig params '''
    
    def __init__(self, walker_params, walker_object=None, reference=None):
        for foot in walker_params['feet']:
            foot['steps'] = []
        if walker_object:
            walker_params['object'] = walker_object
        else: # create the walker objects and rig first..
            original_group = walker_params['group']
            new_group = duplicate_group.make_new_group(
                bpy.data.groups[original_group], link_data=True)
            walker_params['group'] = new_group
            obj = [
                ob for ob in bpy.data.groups[new_group].objects
                if ob.data and ob.data.name == walker_params['rig']][0]
            walker_params['object']= obj
            if obj.animation_data and obj.animation_data.action:
                obj.animation_data.action = obj.animation_data.action.copy()
        try:
            walker_params['action'] = walker_params['actions'][0]
        except:
            walker_params['action'] = ""
        actions = {action:0 for action in walker_params['actions']}
        walker_params.pop('actions')
        walker_params['locked'] = False    
        RigSettings.__init__(self, walker_params)
        self.actions = actions
        for action in self.actions:
            self.actions[action] = self.set_stride(action)
        self.in_air_start = 0.2 # defaults.in_air_start
        self.in_air_end = 0.8 # defaults.in_air_end
        self.flip = False
        self.walk_data = {}
        self.injest_action()
        self.walkcycles_curves = {}
        self.prep_action(blank=False)
        self.footstep_stride_multiplier = 1.0
        self.reference_object = reference
        if not reference:
            if 'OROX_reference' in self.object.keys():
                self.reference_object = bpy.data.objects[self.object['OROX_reference']]
        else:
            self.object['OROX_reference'] = reference.name

        self.reference_offset = Matrix.Translation(bpy.context.scene.offset_loc)

    def append_action(self, action):
        ''' add a reference action to a parambulator '''
        if type(action) == String:
            self.actions[action] = self.set_stride(action)
        else:
            self.actions[action.name] = self.set_stride(action.name)

    def add_footstep_rotations(self):
        '''
        add rotations into footstep series
        '''
        for foot in self.feet:
            for index, step in enumerate(foot.steps):
                current = step['location']
                vector = foot.steps[
                    min(len(foot.steps) - 1, index + 1)]['location'] -\
                    foot.steps[max(0, index - 1)]['location']

                step['rotation'] = vector.to_track_quat('Y','Z')


    def make_footsteps_object(self, ref_object, frames):
        '''
        Create footsteps over frames for posebones,
        Use reference object locations as starting point
        '''
        pass
           
    @framepreserve
    def make_footsteps(self, scene, frames):
        '''
        makes a list of footsteps over frames for a list of pose bones
        scene: current scene of type bpy.types.Scene
        frames: integer list of frames
        targets: list of pose bones that are foot-target bones
        strides: list of stride lengths per target
        '''
        feet = self.feet
        bones = self.object.pose.bones
        targets = [bones[foot.target] for foot in feet]
        stride = self.actions[self.action] * self.footstep_stride_multiplier
        for foot in feet:
            foot.steps = []
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
        self.add_footstep_rotations()

    def get_offset(self, foot, offmat):
        '''
        calculate an initial offset per bone
        '''
        obj = self.object
        action = self.action
        walk_data = self.walk_data[action]

        transform = walk_data['offsets'][foot.name]
        bone_world_mat = Matrix.Translation(transform)
        offset_inv = bone_world_mat.inverted() * obj.matrix_world * offmat
        return offset_inv.inverted().to_translation()   

    def make_footsteps(self, ref_object, frames):
        '''
        make foosteps offset from a reference object locations... 
        '''
        # ref_object = bpy.data.objects['stilton']
 
        # setup some variables:
        feet = self.feet
        bones = self.object.pose.bones
        stride = self.actions[self.action] * self.footstep_stride_multiplier
        offmat = self.reference_offset
        offsets = [self.get_offset(foot, offmat) for foot in feet]
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
        self.add_footstep_rotations()

    def draw_footsteps(self, scene):
        '''
        draw the footsteps as empty objects on screen for editing
        '''
        self.remove_walker_footsteps(scene)
        feet = self.feet
        rig = bpy.data.armatures[self.rig]
        indie_feet = [foot for foot in feet if foot.deps == []]
        total = len(indie_feet)
        draw_feet = feet if DEBUG else indie_feet
        for foot_no, foot in enumerate(draw_feet):
            footmat_name = '_atmn_{}_{}'.format(self.object.name, foot_no)
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
                stride = self.object.pose.bones[self.properties]['stride']
                foot_size = stride / 12
            except:
                foot_size = (bone.head - bone.tail).length * 2
            for index, footstep in enumerate(footsteps):
                stepname = "_S{}_{}_{}".format(
                    self.object.name,
                    feet.index(foot), footstep['frame'])
                groupname = "_SG{}_{}".format(
                    self.object.name,
                    footstep['frame'])
                props = {'frame': footstep['frame'], 'foot': name}
                make_marker(
                    bpy.context, stepname,
                    footstep['location'], footstep['rotation'], props,
                    foot_size * scene.footstep_scale, footmat, groupname)

    def remove_walker_footsteps(self, scene):
        '''
        remove visible footsteps from one walker XXX
        '''

        #windex = walkers.index(walker)
        names = [
            "_S{}_{}_".format(
                self.object.name,
                self.feet.index(foot)) for foot in self.feet]
        obs = [
            ob for ob in scene.objects if
            ob.name.rstrip("0123456789") in names]
        for ob in obs:
            scene.objects.unlink(ob)

    def offset_targets(self):
        '''
        create the initial conditions we need for a smooth walk
        feet are data structures
        targets are pose bones
        '''
        feet = self.feet
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
           
    def set_stride(self, reference_action):
        ''' get the stride from the reference action '''
        object = self.object
        action = bpy.data.actions[reference_action]
        body_name = self.feet[0].name  # XXX  assumes one body
        prop_holder = object.pose.bones[self.properties]
        body_curves = [
            crv for crv in action.fcurves if body_name in crv.data_path and
            'location' in crv.data_path]
        body_curves.sort(key=lambda x: x.array_index)
        # XXX should really use the markers:
        initial_location = [
            crv.keyframe_points[0].co[1] for crv in body_curves]
        final_location = [
            crv.keyframe_points[-1].co[1] for crv in body_curves]
        initial_location = bone_to_world(
            Vector(initial_location), object, body_name, True)
        final_location = bone_to_world(
            Vector(final_location), object, body_name, True)
        stride = (final_location - initial_location).length
        prop_holder['stride'] = stride
        return stride        

    def calculate_body(self, body, steps):
        '''
        get the body location and frame based on it's foot-steps
        '''
        data = self.walk_data[self.action]
        frames = [step['frame'] for step in steps]
        frame = int(average(frames))
        locations = [step['location'] for step in steps]
        originals = []
        for i in range(len(steps)):
            footbone = self.feet[body.deps[i]].name
            originals.append(data['offsets'][footbone])
        # step 1 find the average location.
        average_step = average(locations)
        # step 2 for each location find the walkcycle warped body location
        body_original = data['offsets'][body.name]
        warped_locations = []
        for index, location in enumerate(locations):
            original = data['offsets'][self.feet[body.deps[index]].name]
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
            self.object.name, self.feet.index(body), frame)
        props = {'frame': frame, 'name': body.name}
        return({'frame': frame, 'location': result})

    def injest_footsteps(self, scene):
        '''
        swallow the drawn steps as footsteps, presumably after user editing
        '''
        data = self.walk_data[self.action]
        feet = self.feet
        prefix = "_S{}_".format(self.object.name)
        obs = [ob for ob in scene.objects if ob.name.startswith(prefix)]
        for foot in feet:
            foot.steps = []
        steps = {}

        for ob in obs:
            frame = ob['frame']
            foot = ob['foot']
            location = ob.location
            rotation = ob.rotation_quaternion
            try:
                steps[foot].append({
                    'frame': frame, 'location': location, 'rotation': rotation})
            except:
                steps[foot] = [{
                    'frame': frame, 'location': location, 'rotation': rotation}]

        indie_feet = [foot for foot in self.feet if foot.deps == []]
        bodies = [foot for foot in self.feet if foot not in indie_feet]
        for foot in indie_feet:
            foot.steps = sorted(steps[foot.name], key=lambda x: x['frame'])
            step_no = len(foot.steps)
        for body in bodies:
            bodyfeet = [feet[index] for index in body.deps]

            step_groups = [
                [foot.steps[i] for foot in bodyfeet] for i in range(step_no)]
            bodysteps = [
                self.calculate_body(body, s) for s in step_groups]
            body.steps = bodysteps
            self.add_footstep_rotations()

    def blank_action_copy(self, nuevo, curveset=None):
        '''
        copy curves from an action into a nuevo action, optionally restrict by
        curveset, exact implementation of restriction TBD
        '''
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
        '''
        get the walk matrixes time limits out of the reference action
        '''
        print("self.action = ",self.action)
        if self.action in self.walk_data:
            return
        flip = self.flip
        source_walkcycle = bpy.data.actions[self.action]
        walkcycle_curves = group_curves(source_walkcycle.fcurves)
        marked_poses = [
            pose_marker.frame for pose_marker in source_walkcycle.pose_markers]
        old_frames = (min(marked_poses), max(marked_poses))
        # XXX The above assumes at least two pose markers, and doesn't fail
        # gracefully, we should probably at least have an action prep stage
        # or use the first and last keyframe if no markers...

        # now we need the old offsets for any bone in feet or main target track
        walkcycle_mats = {}
        offsets = {}
        contacts = {}
        for foot in self.feet:
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
        '''
        prep our blank action for a good go
        '''
        source_walkcycle = bpy.data.actions[self.action]
        if not self.action in self.walkcycles_curves.keys():
            walkcycle_curves = group_curves(source_walkcycle.fcurves)
            self.walkcycles_curves[self.action] = walkcycle_curves
        else:
            walkcycle_curves = self.walkcycles_curves[self.action]
        object = self.object
        if not object.animation_data:
            object.animation_data_create()
        if object.animation_data.action:
            # XXX Insure walker actions are unique!!!!
            target_walk = object.animation_data.action
            if blank:
                self.blank_action_copy(target_walk)
        else:
            target_walk = bpy.data.actions.new(name="forward")
            object.animation_data.action = target_walk
            self.blank_action_copy(target_walk)
        self.walk_curves = group_curves(target_walk.fcurves)
        body_tracks = set([
            bone for bone in self.walk_curves if bone not in [
                foot.name for foot in self.feet]])
        for foot in self.feet[-1:]:
            body_tracks = body_tracks.difference(set(foot.tracks))
        for bone in list(body_tracks):
            self.feet[0].tracks.append(bone) # XXX only one body!!!!

    def copy_transforms(
            self, 
            context, pose_bone, loc_list,
            time_map, step_rots, step_mat, time_ramp, foot):
        '''
        make walk keyframes in the new curves based on the old curves.
        '''
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
                    flip = context.scene.flip_walker
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
        '''
        bake the steps from a foot that has steps onto anim_bones
        '''
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
        '''
        This populates each walker action with it's new modified curves.
        '''

        pbones = self.object.pose.bones
        for foot in self.feet:  # copy each foot's steps individually
            footbones = [bone for bone in foot.tracks] + [foot.name]
            bones = [
                bone for bone in self.walkcycles_curves[self.action]
                if bone in footbones]
            anim_bones = [bone for bone in pbones if bone.name in bones]
            self.bake_steps(context, foot, anim_bones)
      
    
        
