import bpy
from mathutils import Euler

from blendmotion.logger import get_logger
from blendmotion.error import OperatorError
from blendmotion.core.effector import is_effector

import math
import json
import flom

def dictzip(d1, d2):
    for k, v in d1.items():
        yield k, (v, d2[k])

LOOP_TYPES = ('wrap', 'none')

def extract_bone_pose(bone):
    """
        bone: PoseBone
    """

    assert is_axis_available(bone.bm_axis)

    x, y, z = bone.rotation_quaternion.to_euler()
    a_x, a_y, a_z = bone.bm_axis
    if a_x != 0:
        return x * a_x
    elif a_y != 0:
        return y * a_y
    elif a_z != 0:
        return z * a_z

def get_decomposed_pose(obj):
    """
        obj: Object
    """

    local = (obj.matrix_world - obj.parent.matrix_world).decompose()
    world = obj.matrix_world.decompose()
    return local, world


def extract_effector_pose(mesh):
    """
        mesh: Object(Mesh)
    """

    effector = flom.Effector()

    # Effector types stored in properties
    type_loc = mesh.data.bm_location_effector
    type_rot = mesh.data.bm_rotation_effector

    (local_loc, local_rot, _), (world_loc, world_rot, _) = get_decomposed_pose(mesh)

    def select_space(effector_type, world, local):
        # Select world or local value depends on effector type
        if effector_type == 'world':
            return world
        elif effector_type == 'local':
            return local
        elif effector_type == 'none':
            return None

    # Here, if effector_type is none, the value is set to None
    if type_loc != 'none':
        loc = flom.Location(select_space(type_loc, world_loc, local_loc))
        effector.location = loc

    if type_rot != 'none':
        rot = flom.Rotation(*select_space(type_rot, world_rot, local_rot))
        effector.rotation = rot

    return effector

def is_axis_available(axis):
    return tuple(axis) != (0,0,0)

def get_frame_at(index, amt):
    """
        index: int
        amt: Object(Armature)
    """

    bpy.context.scene.frame_set(index)
    positions = {name: extract_bone_pose(b) for name, b in amt.pose.bones.items() if is_axis_available(b.bm_axis)}
    effectors = {obj.name: extract_effector_pose(obj) for obj in amt.children if is_effector(obj)}
    timepoint = index * (1 / bpy.context.scene.render.fps)
    return timepoint, positions, effectors

def extract_effector_type(obj):
    loc_effector = obj.data.bm_location_effector
    if loc_effector == 'world':
        location = flom.CoordinateSystem.World
    elif loc_effector == 'local':
        location = flom.CoordinateSystem.Local
    else:
        location = None

    rot_effector = obj.data.bm_rotation_effector
    if rot_effector == 'world':
        rotation = flom.CoordinateSystem.World
    elif rot_effector == 'local':
        rotation = flom.CoordinateSystem.Local
    else:
        rotation = None

    return flom.EffectorType(location, rotation)

def export_animation(amt, path, loop_type='wrap'):
    if amt.type != 'ARMATURE':
        raise OperatorError('Armature object must be selected (selected: {})'.format(amt.type))

    assert loop_type in LOOP_TYPES

    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end

    bpy.ops.object.mode_set(mode='POSE')

    frames = [get_frame_at(i, amt) for i in range(start, end+1)]
    first_ts, first_p, first_e = frames[0]

    effector_types = {obj.name: extract_effector_type(obj) for obj in amt.children if is_effector(obj)}

    motion = flom.Motion(set(first_p.keys()), effector_types, amt.name)

    if loop_type == 'wrap':
        motion.set_loop(flom.LoopType.Wrap)
    elif loop_type == 'none':
        motion.set_loop(flom.LoopType.None_)
    else:
        assert False  # unreachable

    for obj in amt.children:
        if not is_effector(obj):
            continue

        loc_weight = obj.data.bm_location_effector_weight
        rot_weight = obj.data.bm_rotation_effector_weight

        motion.set_effector_weight(obj.name, flom.EffectorWeight(loc_weight, rot_weight))

    for t, p, e in frames:
        frame = motion.new_keyframe()
        frame.positions = p
        frame.effectors = e
        motion.insert_keyframe(t - first_ts, frame)

    motion.dump(path)

def timepoint_to_frame_index(timepoint):
    """
        timepoint: float
    """
    return int(timepoint * bpy.context.scene.render.fps)

def import_animation(amt, path):
    motion = flom.load(path)

    if amt.name != motion.model_id():
        raise OperatorError('Model name mismatch: {} and {}'.format(amt.name, motion.model_id()))

    bpy.context.scene.frame_start = timepoint_to_frame_index(0)
    bpy.context.scene.frame_end = timepoint_to_frame_index(motion.length())

    for timepoint, frame in motion.keyframes():
        positions = frame.positions
        effectors = frame.effectors

        bpy.context.scene.frame_set(timepoint_to_frame_index(timepoint))

        for _, (pos, bone) in dictzip(positions, amt.pose.bones):
            if 'blendmotion_joint' not in bone:
                continue

            a_x, a_y, a_z = bone.bm_axis
            if a_x != 0:
                euler = (pos * a_x, 0, 0)
            elif a_y != 0:
                euler = (0, pos * a_y, 0)
            elif a_z != 0:
                euler = (0, 0, pos * a_z)

            bone.rotation_quaternion = Euler(euler, 'XYZ').to_quaternion()
            bone.keyframe_insert(data_path='rotation_quaternion')

    for link_name in motion.effector_names():
        obj = next(c for c in amt.children if c.name == link_name)
        assert obj.type == 'MESH'

        def extract_effector_type(ty):
            if ty == flom.CoordinateSystem.World:
                return 'world'
            elif ty == flom.CoordinateSystem.Local:
                return 'local'
            else:
                return 'none'

        ty = motion.effector_type(link_name)
        obj.data.bm_location_effector = extract_effector_type(ty.location)
        obj.data.bm_rotation_effector = extract_effector_type(ty.rotation)

        weight = motion.effector_weight(link_name)
        obj.data.bm_rotation_effector_weight = weight.rotation
        obj.data.bm_location_effector_weight = weight.location

def register():
    pass

def unregister():
    pass
