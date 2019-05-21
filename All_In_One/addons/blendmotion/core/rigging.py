import bpy
from mathutils import Euler, Matrix, Vector

from blendmotion.logger import get_logger
from blendmotion.error import OperatorError

import math

def make_armature(name, location):
    """
        name: str
    """
    bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=location)
    amt = bpy.context.object
    amt.name = name
    return amt

def calc_pos(o):
    """
        o: Object
    """
    return o.data.bones[0].head + o.matrix_world.translation

def make_bone(o, amt):
    """
        o: Object
        amt: Armature
    """

    is_parent_joint = o.parent is not None and 'joint/name' in o.parent
    joint_name = o.parent['joint/name'] if is_parent_joint else 'root'

    get_logger().debug('make_bone: {}'.format(joint_name))

    b = amt.data.edit_bones.new(joint_name)
    if o.parent is not None:
        b.head = calc_pos(o.parent)
    b.tail = calc_pos(o)

    if is_parent_joint:
        b['blendmotion_joint'] = o.parent.name

    return b

def attach_bones(parent, child):
    """
        parent: EditBone
        child: EditBone
    """
    child.parent = parent

def attach_mesh_bone(o, amt, bone):
    """
        o: Object
        amt: Armature
        bone: EditBone
    """

    o.parent = amt
    o.parent_type = 'BONE'
    o.parent_bone = bone.name

def make_tip(bone, name, amt):
    """
        bone: EditBone
        name: str
        amt: Armature
    """

    get_logger().debug('make_tip: {}'.format(name))

    # make a bone which has the same shape with parent bone
    b = amt.data.edit_bones.new(name)
    b.head = bone.tail
    b.tail = b.head + bone.vector

    return b

def make_handle(bone, amt):
    """
        bone: EditBone
        amt: Armature
    """

    # make a bone which has the same shape with parent bone
    # but rotated for 90 deg
    handle = amt.data.edit_bones.new('handle_{}'.format(bone.name))
    handle.head = bone.tail
    v = bone.vector.copy()
    v.rotate(Euler((0.0, - math.pi / 2, 0.0), 'XYZ'))
    handle.tail = handle.head + v

    return handle

def set_ik(bone_name, target_armature, target_bone_name):
    """
        bone: str
        target_armature: Armature
        target_bone_name: str
    """

    bone = target_armature.pose.bones[bone_name]
    ik = bone.constraints.new(type='IK')
    name = ik.name
    bone.constraints[name].target = target_armature
    bone.constraints[name].subtarget = target_bone_name

def limit_bone(bone, x, y, z, ik=True):
    """
        bone: PoseBone
        x: (float, float)
        y: (float, float)
        z: (float, float)
        ik: bool
    """

    # Bone Constraints
    limit = bone.constraints.new(type='LIMIT_ROTATION')
    limit.use_limit_x = True
    limit.use_limit_y = True
    limit.use_limit_z = True
    limit.min_x, limit.max_x = x
    limit.min_y, limit.max_y = y
    limit.min_z, limit.max_z = z
    limit.owner_space = 'LOCAL'

    if ik:
        # IK Constraints
        bone.use_ik_limit_x = True
        bone.use_ik_limit_y = True
        bone.use_ik_limit_z = True
        bone.ik_min_x, bone.ik_max_x = x
        bone.ik_min_y, bone.ik_max_y = y
        bone.ik_min_z, bone.ik_max_z = z

def lock_bone(bone, ik=True):
    """
        bone: PoseBone
        ik: bool
    """

    limit_bone(bone, (0, 0), (0, 0), (0, 0), ik)

def limit_and_add_axis_with_joint(bone, joint, ik=True):
    """
        bone: PoseBone
        joint: Object
        amt: Armature
        ik: bool
    """

    joint_type = joint.get('joint/type')

    limit_x = (0, 0)
    limit_y = (0, 0)
    limit_z = (0, 0)
    if joint_type is None or joint_type == 'fixed':
        pass
    elif joint_type == 'revolute':
        # Make sure the joint is phobos' joint
        assert len(joint.pose.bones) == 1
        joint_constraint = joint.pose.bones[0].constraints['Limit Rotation']

        # Make sure limit is only applied to Y axis
        assert joint_constraint.use_limit_x
        assert joint_constraint.use_limit_y
        assert joint_constraint.use_limit_z
        assert joint_constraint.min_x == 0 and joint_constraint.max_x == 0
        assert joint_constraint.min_z == 0 and joint_constraint.max_z == 0

        # So Y axis represents joint limits
        joint_limit = (joint_constraint.min_y, joint_constraint.max_y)

        bone_vector = bone.vector.copy()
        joint_vector = joint.pose.bones[0].vector
        diff = bone_vector.rotation_difference(joint_vector)
        x, y, z = tuple(int(i) for i in diff.to_euler('XYZ'))

        # Set axis
        # TODO: What's going on here
        bone.bm_axis = (- y, - z, x)

        if x != 0:
            limit_z = joint_limit
        elif y != 0:
            limit_x = joint_limit
        elif z != 0:
            limit_y = joint_limit
    elif joint_type == 'floating':
        limit_x = (-math.pi, math.pi)
        limit_y = (-math.pi, math.pi)
        limit_z = (-math.pi, math.pi)
    else:
        raise OperatorError('joint type "{}" is not supported'.format(joint_type))

    limit_bone(bone, limit_x, limit_y, limit_z, ik)

def rename_object(object, name):
    """
        object: Object(Mesh)
        name: str
    """

    object.name = name
    return object

def change_origin(obj, origin):
    """
        From stack exchange:
        https://blender.stackexchange.com/questions/35825/changing-object-origin-to-arbitrary-point-without-origin-set
        Authors:
        - [Jabberwock](https://blender.stackexchange.com/users/9771/jabberwock)
        - [zeffii](https://blender.stackexchange.com/users/1363/codemanx)

        obj: Object(ID)
        origin: Vector
    """

    obj.data.transform(Matrix.Translation(-origin))
    obj.matrix_world.translation += origin
    return obj

def center_of_geometry(obj):
    """
        From stack exchange:
        https://blender.stackexchange.com/questions/62040/get-center-of-geometry-of-an-object
        Authors:
        - [tea](https://blender.stackexchange.com/users/2100/tea)
        - [batFINGER](https://blender.stackexchange.com/users/15543/batfinger)

        obj: Object(ID)
    """

    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    return obj.matrix_world * local_bbox_center

def fix_parented_location(obj):
    """
        obj: Object(ID)
    """
    obj.matrix_world = obj.matrix_parent_inverse

def get_geometry_origin_mesh(obj):
    """
        Get the mesh which is most suitable for origin of visual mesh.

        obj: Object(ID)
    """

    # TODO: Use better way than this in finding relative inertial mesh
    inertia_meshes = [c for c in obj.parent.children if c.phobostype == 'inertial' and 'inertial_' + obj.name ==  c.name]
    if len(inertia_meshes) == 0:
        return obj
    else:
        assert len(inertia_meshes) == 1
        fix_parented_location(inertia_meshes[0])
        return inertia_meshes[0]

def make_bones_recursive(o, amt, with_handle=True):
    """
        o: Object
        amt: Armature
        with_handle: bool
    """
    get_logger().debug('make_bone_recursive: {}'.format(o.name))
    link_name = o.name

    parent_bone = make_bone(o, amt)

    armature_children = [child for child in o.children if child.type == 'ARMATURE']
    mesh_children = [child for child in o.children if child.type == 'MESH']

    # rename visual meshes to the real link name
    for mesh in mesh_children:
        if mesh.phobostype == 'visual':
            rename_object(mesh, link_name)

    if len(armature_children) == 1:
        # Single bone
        child_bone = make_bones_recursive(armature_children[0], amt, with_handle)
        attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_bone(child, amt, child_bone)
    elif len(armature_children) == 0:
        # The tip
        child_bone = make_tip(parent_bone, o['joint/name'], amt)
        attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_bone(child, amt, child_bone)

        # Mark a tip bone to use them later
        child_bone['blendmotion_joint'] = o.name

        # Make a handle bone to use with IK
        if with_handle:
            handle_bone = make_handle(child_bone, amt)
            child_bone['blendmotion_tip'] = handle_bone.name
        else:
            child_bone['blendmotion_tip'] = True

    else:
        # Where bones are branching off
        for child in armature_children:
            child_bone = make_bones_recursive(child, amt, with_handle)
            attach_bones(parent_bone, child_bone)
        for child in mesh_children:
            attach_mesh_bone(child, amt, parent_bone)

    return parent_bone

def add_bones(obj, with_ik=True):
    if obj.type != 'ARMATURE':
        raise OperatorError('Armature object must be selected (selected: {})'.format(obj.type))

    model_name = obj.get('model/name')
    if model_name is None:
        raise OperatorError('"model/name" property not set. base link of phobos model must be selected.')

    bpy.ops.object.mode_set(mode='OBJECT')

    # visual meshes, inertia meshes and joints are visible
    bpy.context.scene.layers[:4] = [True, True, True, False]

    # Apply transforms
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')

    # visual meshes and joints are visible
    bpy.context.scene.layers[:4] = [True, False, True, False]

    amt = make_armature(model_name, obj.matrix_world.translation)

    bpy.ops.object.mode_set(mode='EDIT')
    make_bones_recursive(obj, amt, with_handle=with_ik)

    # Fix the location and origin of meshes
    bpy.context.scene.layers[1] = True  # inertia layer
    bpy.ops.object.mode_set(mode='OBJECT')
    for o in amt.children:
        if o.type == 'MESH':
            fix_parented_location(o)
            change_origin(o, center_of_geometry(get_geometry_origin_mesh(o)))
    bpy.context.scene.layers[1] = False  # inertia layer

    bpy.ops.object.mode_set(mode='EDIT')

    bone_and_joints = [(name, b['blendmotion_joint']) for name, b in amt.data.bones.items() if 'blendmotion_joint' in b]
    non_joint_bone = [name for name, b in amt.data.bones.items() if 'blendmotion_joint' not in b]
    tip_bones = [(name, b['blendmotion_tip']) for name, b in amt.data.bones.items() if 'blendmotion_tip' in b]

    bpy.ops.object.mode_set(mode='POSE')

    # Find tip bones and apply IK constraint on it
    if with_ik:
        for bone_name, handle_bone_name in tip_bones:
            set_ik(bone_name, amt, handle_bone_name)

    for bone_name, joint_name in bone_and_joints:

        # Set 'blendmotion_joint' to distinguish joint bones and non-joint bones
        bone = amt.pose.bones[bone_name]
        bone['blendmotion_joint'] = joint_name

        # Set bone constraints
        joint = bpy.data.objects[joint_name]
        limit_and_add_axis_with_joint(bone, joint, ik=with_ik)

    # Lock non-joint bones
    for bone_name in non_joint_bone:
        bone = amt.pose.bones[bone_name]
        lock_bone(bone, ik=with_ik)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Joints, collision meshes and intertia meshes are visible here
    bpy.context.scene.layers[:5] = [True, True, False, True, False]

    # Delete visible things (= joints, collision and inertia)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # All layers are visible
    bpy.context.scene.layers[:5] = [True] * 5

def register():
    bpy.types.PoseBone.bm_axis = bpy.props.IntVectorProperty(name='Joint Axis')

def unregister():
    pass
