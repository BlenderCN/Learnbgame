# general utility functions for Orox
# Copyright (C) 2014  Bassam Kurdali
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
from mathutils import Vector, Quaternion, Matrix, Euler, Color
try:
    from . import make_stepshape
except:
    import make_stepshape

def average(things):
    '''
    find the average thing
    '''
    added = things[0]
    for i in things[1:]: added = added + i
    return added / len(things)


def average_distance(center, points):
    '''
    find the average distance from the center of all the points
    '''
    distances = [(point - center).length for point in points]
    return average(distances)


def bone_rest_mat(bone, location=False):
    '''
    get the rest matrix for a data bone, keep in mind local location option
    '''
    if location and not bone.use_local_location:
        comps = bone.matrix_local.decompose()
        return Matrix.Translation(comps[0]) * Matrix.Scale(1.0, 4, comps[2])
    else:
        return bone.matrix_local


def bone_to_world(transform, obj, bone, location=False):
    '''
    convert bone local transfrom into world coordinate
    '''
    data_bone = obj.data.bones[bone]
    return obj.matrix_world * bone_rest_mat(data_bone, location) * transform


def world_to_bone_generic(transform, obj, bone, is_location):
    '''
    Place a world space transformation into bone space, checks location
    '''
    data_bone = obj.data.bones[bone]
    return bone_rest_mat(data_bone, is_location).inverted() *\
        obj.matrix_world.inverted() * transform


def world_location_to_bone(transform, obj, bone):
    '''
    Place a world space location into a bone space
    '''
    return world_to_bone_generic(transform, obj, bone, True)


def world_to_bone(transform, obj, bone):
    '''
    Place a world space transformation into bone space
    '''
    return world_to_bone_generic(transform, obj, bone, False)


def keyframes_from_curves(curves):
    '''
    return list of frame ordered keyframes from fcurves
    X, Y, Z or W, X, Y, Z where each curve is the fcurve of
    a particular axis.
    looks like:
    [[x, y, z],[x, y, z], ......]
    or
    [[w, x, y, z],[w, x, y, z], ....] in case of quats
    where each x, y, z is a keyframe.
    '''

    keyframe_lists = []
    for curve in curves:
        keyframe_lists.append(
            sorted([
                kp for kp in curve.keyframe_points], key=lambda x: x.co[0]))
    keyframes = []
    for i in range(len(keyframe_lists[0])):
        keyframes.append(
            [keyframe_lists[j][i] for j in range(len(keyframe_lists))])
    return keyframes


def framepreserve(fn):
    '''
    Decorator to preserve current frames in frame-changing functions
    '''
    def wrapped(*args, **kwargs):
        scene = bpy.context.scene
        frame_original = scene.frame_current
        retval = fn(*args, **kwargs)
        scene.frame_set(frame_original)
        return retval
    return wrapped


def progress(A, B, fraction):
    '''
    give the location at fraction of B - A
    '''
    return fraction * B + (1 - fraction) * A


def dist_get(source, target):
    '''
    get distance between two locations.
    '''
    dist = source - target
    return abs(dist.length)


def offset_matrix(location_1, location_2, track, up):
    '''
    return a transform matrix based on the steps
    '''
    diff = location_2 - location_1
    quat = diff.to_track_quat(track, up)
    rotation = quat.to_matrix()
    offset = Matrix.Translation(location_1)
    scale = Matrix.Scale(diff.length, 4)
    return offset * rotation.to_4x4() * scale



def warp_matrix(walk_mat, step_mat, rest_mat):
    '''
    the step warp matrix
    '''
    return rest_mat.inverted() * step_mat * walk_mat.inverted() * rest_mat


def global_location_warp_matrix(walk_mat, step_mat, rest_mat):
    '''
    XXX local location off!!! the step warp matrix
    '''
    # we need to construct a rest mat based on the object rotation
    # and the rest mat location....
    components = rest_mat.decompose()
    fake_mat = Matrix.Translation(components[0]) *\
        Matrix.Scale(1.0, 4, components[2])
    return fake_mat.inverted() * step_mat * walk_mat.inverted() * fake_mat


def warp_location(transform, warp):
    '''
    this is creating the deformed location keyframe for the walk
    '''
    warped = warp * Vector(transform)

    return [axis for axis in warped]


def warp_rotation(transform, warp):
    '''
    this is creating the deformed rotation keyframe for the walk
    takes its rotation as a mathutils type that has a .rotate method
    '''

    final_quat = warp.to_quaternion()
    transform.rotate(final_quat)
    # transform.rotate(Quaternion((0,0,1,0)))
    return [axis for axis in transform]


def progress(A, B, fraction):
    '''
    give the location at fraction of B - A
    '''
    return fraction * B + (1 - fraction) * A


def space_time(keyframe_set, limits, attr, time_ramp):
    '''
    return space and time numbers for the keyframe handles/co
    '''
    space = [getattr(keyframe, attr)[1] for keyframe in keyframe_set]
    times = [getattr(keyframe, attr)[0] for keyframe in keyframe_set]
    new_times = [time_ramp[0] + time_ramp[1] * time for time in times]
    frame = sum(times)//len(times)
    frame = max(min(frame, limits[1]), limits[0])  # clip to 0,1 range
    return (space, new_times, frame)


def warp_core(space, times, offmult, attr, ret_val):
    '''
    stuff the return values in the correct attr similar to the keyframe set
    '''
    space = [
        offmult[0][i] + space[i] * offmult[1][i] for i in range(len(space))]
    for index, ret_item in enumerate(ret_val):
        ret_item[attr] = (times[index], space[index])


def warp_core_loop(fn):
    ''' decorate functions that are in the warp core for all cases '''

    def wrapped(keyframe_set, time_ramp, offmult, limits, *args, **kwargs):
        ret_val = [{} for i in keyframe_set]
        for attr in ['co', 'handle_left', 'handle_right']:
            space, new_times, frame = space_time(
                keyframe_set, limits, attr, time_ramp)

            space = fn(space, frame, *args, **kwargs)
            warp_core(space, new_times, offmult, attr, ret_val)
        return ret_val
    return wrapped


@warp_core_loop
def warp_core_nodeform(space, frame):
    '''
    Only warp the time, but leave the coordinates intact
    '''
    return space


@warp_core_loop
def warp_core_location(
        space, frame, step_mat, walk_mat, rest_mat, local_location):
    '''
    pull out coord stuff from the keyframe set as vectors/frames, spacewarp it,
    and pull out the times and timeramp them, then stuff them back into a dict.
    '''
    if local_location:
        warp_mat = warp_matrix(walk_mat, step_mat, rest_mat)
    else:
        warp_mat = global_location_warp_matrix(walk_mat, step_mat, rest_mat)
    return warp_location(space, warp_mat)


@warp_core_loop
def warp_core_rotation(
        space, frame, flip, foot, rotation_mode,
        step_rots, step_mat, walk_mat,
        rest_mat, contacts):
    '''
    pull out coord stuff from the keyframe set as vectors/frames, spacewarp it,
    and pull out the times and timeramp them, then stuff them back into a dict.
    '''

    if 'QUATERNION' in rotation_mode:
        space_vec = Quaternion(space)
    elif 'AXIS_ANGLE' in rotation_mode:
        space_vec = Quaternion(space)  # XXX Axis Angle not handled
    else:
        space_vec = Euler(space, rotation_mode)

    # figure out rotation percentage based on frame:
    if frame < contacts[0]:
        step_rot = step_rots[0]
    elif frame > contacts[1]:
        step_rot = step_rots[1]
    else:
        factor = (frame - contacts[0]) / (contacts[1] - contacts[0])
        step_rot = step_rots[0].slerp(step_rots[1], factor)

    warp_mat = warp_matrix(walk_mat, step_rot.to_matrix().to_4x4(), rest_mat)

    #return [axis for axis in space_vec]
    return warp_rotation(space_vec, warp_mat)


def group_curves(fcurves):
    '''
    group curves in action by rna path, index. Don't trust groups!!!
    returns a dict indexed by rna path (or maybe just bone?) and values
    are an array of curves, sorted by index no.
    '''
    retval = {}
    for curve in fcurves:
        data_path = curve.data_path
        index = curve.array_index

        data = data_path.split('pose.bones["')

        bone = data[1].split('"]')[0]
        remainder = data[1].replace(bone, '')
        if remainder.startswith('"].'):
            transform = remainder[3:]
        else:
            transform = remainder[2:]

        if bone in retval:
            if transform in retval[bone]:
                retval[bone][transform].append(curve)
            else:
                retval[bone][transform] = [curve]
        else:
            retval[bone] = {transform: [curve]}
    for bone in retval:
        for transform in retval[bone]:
            retval[bone][transform].sort(key=lambda curve: curve.array_index)
    return retval


def flip_axis(axis, flip):
    '''
    kludgy way to fllip the axis
    '''
    if axis:
        flipped = axis[1:] if axis.startswith('-') else '-{}'.format(axis)
    else:
        flipped = axis
    return flipped


def copy_coords(old_keyframe, new_keyframe, overrides):
    '''
    copy the coords from the old keyframe to the new, with a mod
    '''
    base_attrs = [
        'co', 'handle_left', 'handle_left_type', 'handle_right',
        'handle_right_type', 'interpolation', 'type']
    old_attrs = [attr for attr in base_attrs if not attr in overrides]
    for attr in old_attrs:
        setattr(new_keyframe, attr, getattr(old_keyframe, attr))
    for attr in overrides:
        setattr(new_keyframe, attr, overrides[attr])


def keyframes_from_curves(curves):
    '''
    return list of frame ordered keyframes from fcurves
    X, Y, Z or W, X, Y, Z where each curve is the fcurve of
    a particular axis.
    looks like:
    [[x, y, z],[x, y, z], ......]
    or
    [[w, x, y, z],[w, x, y, z], ....] in case of quats
    where each x, y, z is a keyframe.
    '''

    keyframe_lists = []
    for curve in curves:
        keyframe_lists.append(
            sorted([
                kp for kp in curve.keyframe_points], key=lambda x: x.co[0]))
    keyframes = []
    for i in range(len(keyframe_lists[0])):
        keyframes.append(
            [keyframe_lists[j][i] for j in range(len(keyframe_lists))])
    return keyframes


def vectorize_param_value(length, scaler, param, multiplier=False):
    '''
    map the scaler value into our parameter on the bone
    '''
    axes = ['w', 'x', 'y', 'z'][4 - length:]
    return Vector([
        getattr(param, axis) * scaler + multiplier *
        (not getattr(param, axis)) for axis in axes])


def param_value(scene, param, rig):
    '''
    return value of parameter in scene for given rig type
    '''
    parameter = [
        item for item in scene.autowalker_params if
        (param, rig) == (item.name, item.autorig)][0]
    return parameter.value


def make_marker(
        context, name, location, rotation, props,
        size=1.0, material=None, group=""):
    '''
    Chris Marker made La Jette and San Soleil among others. watch them!
    name: string, name of marker
    rotation is a quaternion
    props get added to the marker
    '''
    stepshape = make_stepshape.makedemesh()
    scene = context.scene
    try:
        newob = bpy.data.objects[name]
    except:
        newob = bpy.data.objects.new(name=name, object_data=stepshape)
    if not newob.name in scene.objects:
        scene.objects.link(newob)
    newob.layers = scene.layers
    newob.location = location
    newob.rotation_mode = 'QUATERNION'
    newob.rotation_quaternion = rotation
    newob.scale = Vector((size, size, size))
    for prop in props:
        newob[prop] = props[prop]
    if group:
        if group not in bpy.data.groups:
            bpy.data.groups.new(name=group)
        try:
            bpy.data.groups[group].objects.link(newob)
        except:
            pass
    if material:
        try:
            slot = newob.material_slots[0]
        except IndexError:
            #override context
            #override = {'active_base':newob}
            active = context.active_object
            scene.objects.active = newob
            #add the slot
            bpy.ops.object.material_slot_add()
            scene.objects.active = active
            slot = newob.material_slots[0]
        slot.link = 'OBJECT'
        slot.material = material


def get_params():
    '''
    injest autorigdesc.py, for now only one...
    '''
    try:
        raw_data = bpy.data.texts['auto_rig_desc.py'].as_string()
    except:
        return False
    rig_params = eval(raw_data.replace("rig_params = ", ""))
    exec(raw_data)
    return rig_params         
    
