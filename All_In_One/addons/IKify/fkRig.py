import bpy
from .utils import *

PI = 3.14159

def addOneFKControl(context, object, deform_bone_name, gizmo_obj, layer_number, scale, 
    new_bone_parent, parent_connected = True):    
    # Make sure we are in pose mode
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    # If a bone with the same name as new FK control bone already exists,
    # return
    new_bone_name = deform_bone_name + "_FK"

    # if deformation bone is a left/right bone, then maintain the naming scheme such that
    # last 2 letters are '_L' or '_R'. This is required for copy pasting mirrored poses.
    l_r_bone = (deform_bone_name[-1] == 'L' or deform_bone_name[-1] == 'R')
    if l_r_bone:
        new_bone_name = deform_bone_name[:-1] + 'FK_' + deform_bone_name[-1]
        
    if new_bone_name in object.data.edit_bones:
        return new_bone_name
    
    # In case of the upper arm bone, create the arm socket bone.
    L_R = deform_bone_name[-1]
    MCH_CLAVICLE_CHILD = 'MCH-clavicle_child_FK_' + L_R
    MCH_ARM_SOCKET = 'MCH-arm_socket_FK_' + L_R
    CLAVICLE_BONE_NAME = 'clavicle_' + L_R
    if deform_bone_name.startswith('upperarm'):
        # Create the clavicle child bone
        clavicle = object.data.edit_bones[CLAVICLE_BONE_NAME]
        head = clavicle.tail.copy()
        tail = head.copy()
        tail.z += 0.1
        createNewBone(object, MCH_CLAVICLE_CHILD, CLAVICLE_BONE_NAME, False, head, tail, 0, 25)
        
        # Create the arm socket bone        
        head = clavicle.tail.copy()
        tail = head.copy()
        tail.z += 0.05
        createNewBone(object, MCH_ARM_SOCKET, 'root', False, head, tail, 0, 25)
        new_bone_parent = MCH_ARM_SOCKET
        parent_connected = False
        
        # Put clavicle bones in an UI layer
        object.data.edit_bones[CLAVICLE_BONE_NAME].layers[layer_number] = True
        
    copyDeformationBone(object, new_bone_name, deform_bone_name, new_bone_parent, 
        parent_connected, layer_number)

    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    pose_bone = object.pose.bones[deform_bone_name]
    new_bone = object.pose.bones[new_bone_name]    

    # Set the custom shape
    setCustomShape(object, new_bone_name, 'GZM_Circle', scale)
    
    # Apply copy transforms constraint
    constraint = addCopyConstraint(object, pose_bone, 'COPY_ROTATION', 'FK', 1.0, new_bone_name)
    
    # add driver for leg FK --> IK control
    if (deform_bone_name.startswith('thigh') or deform_bone_name.startswith('calf') or
        deform_bone_name.startswith('foot') or deform_bone_name.startswith('toes')):
        L_R = deform_bone_name[-1]
        addDriver(constraint, 'influence', object, '["LegIk_' + L_R + '"]', True)

    # add driver for arm FK --> IK control
    if (deform_bone_name.startswith('upperarm') or deform_bone_name.startswith('lowerarm') or
        deform_bone_name.startswith('hand')):
        L_R = deform_bone_name[-1]
        addDriver(constraint, 'influence', object, '["ArmIk_' + L_R + '"]', True)
        
    # add constraints and a driver for arm socket rig
    if deform_bone_name.startswith('upperarm'):
        pose_socket_bone = object.pose.bones[MCH_ARM_SOCKET]
        addCopyConstraint(object, pose_socket_bone, 'COPY_LOCATION', 'SOCKET_LOCATION', 1.0, 
            MCH_CLAVICLE_CHILD)
        
        rotation_constraint = addCopyConstraint(object, pose_socket_bone, 'COPY_ROTATION',
            'SOCKET_ROTATION', 0.0, MCH_CLAVICLE_CHILD)
        if rotation_constraint:
            addDriver(rotation_constraint, 'influence', object, '["ArmRotationIk_' + L_R + '"]')
        
        # lock upper arm transforms
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_location = [True, True, True]
        
        # Add custom shape for clavicle bone
        setCustomShape(object, CLAVICLE_BONE_NAME, 'GZM_shoulder', 1.0)

    # lock some transforms for various bones
    if deform_bone_name.startswith('lowerarm'):
        new_bone.rotation_mode = 'XYZ'
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_rotation = [False, True, True]
        
    if deform_bone_name.startswith('thigh'):
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_location = [True, True, True]
        
    if deform_bone_name.startswith('calf'):
        new_bone.rotation_mode = 'XYZ'
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_rotation = [False, True, True]

    if deform_bone_name.startswith('toes'):
        new_bone.rotation_mode = 'YZX'
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_rotation = [False, True, True]
                        
    return new_bone_name
    
def addHeadNeckRig(context, object, gizmo_obj):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)       

    MCH_NECK_PARENT = 'MCH-neck_parent_FK'
    MCH_HEAD_PARENT = 'MCH-head_parent_FK'
    MCH_BODY_CHILD = 'MCH-body_child_FK'
    MCH_HEAD_SOCKET = 'MCH-head_socket_FK'
    HEAD_FK = 'head_FK'
    
    # create neck parent bone
    neck_bone = object.data.edit_bones['neck']
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_NECK_PARENT, 'spine03', False, head, tail, 0, 25)
    neck_parent_bone = object.data.edit_bones[MCH_NECK_PARENT]
    
    # set neck bone's parent to MCH_NECK_PARENT
    neck_bone.use_connect = False
    neck_bone.parent = neck_parent_bone
    neck_bone.layers[3] = True  # not creating another control for neck, using this bone as control
    
    # create head parent bone
    head_bone = object.data.edit_bones['head']
    head = head_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_HEAD_PARENT, 'neck', True, head, tail, 0, 25)
    head_parent_bone = object.data.edit_bones[MCH_HEAD_PARENT]
    
    # set head bone's parent to MCH_HEAD_PARENT
    head_bone.use_connect = False
    head_bone.parent = head_parent_bone
    
    # Create body child bone for head socket rig
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.07
    createNewBone(object, MCH_BODY_CHILD, 'spine03', False, head, tail, 0, 25)
    
    # create head socket bone
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.05
    createNewBone(object, MCH_HEAD_SOCKET, 'root', False, head, tail, 0, 25)
        
    # create head fk control bone, with head socket as the parent
    head = head_bone.head.copy()
    tail = head.copy()
    tail.z += 0.08
    createNewBone(object, HEAD_FK, MCH_HEAD_SOCKET, False, head, tail, 0, 3)
    
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # add copy rotation constraints for neck and head parents
    pose_neck_parent = object.pose.bones[MCH_NECK_PARENT]
    # this has influence of 0.5 so that it follows head rotation half way
    addCopyConstraint(object, pose_neck_parent, 'COPY_ROTATION', 'FK', 0.5, HEAD_FK)
    
    pose_head_parent = object.pose.bones[MCH_HEAD_PARENT]
    addCopyConstraint(object, pose_head_parent, 'COPY_ROTATION', 'FK', 1.0, HEAD_FK)
    
    # create constraints for head socket
    pose_head_socket = object.pose.bones[MCH_HEAD_SOCKET]
    addCopyConstraint(object, pose_head_socket, 'COPY_LOCATION', 'SOCKET_LOCATION', 1.0, 
        MCH_BODY_CHILD)
    rotation_constraint = addCopyConstraint(object, pose_head_socket, 'COPY_ROTATION', 
        'SOCKET_ROTATION', 0.0, MCH_BODY_CHILD)
    if rotation_constraint:
        addDriver(rotation_constraint, 'influence', object, '["HeadRotationIk"]')

    # limit transforms for control bones
    pose_neck = object.pose.bones['neck']
    pose_neck.lock_location = [True, True, True]
    pose_neck.lock_scale = [True, True, True]
    
    pose_head_fk = object.pose.bones[HEAD_FK]
    pose_head_fk.lock_location = [True, True, True]
    pose_head_fk.lock_scale = [True, True, True]
        
    # add custom shapes for neck and head fk bones
    setCustomShape(object, 'neck', 'GZM_Circle', 1.5)
    setCustomShape(object, HEAD_FK, 'GZM_Circle', 5.0)
    pose_head_fk.custom_shape_transform = object.pose.bones['head']    
       
def addTorsoRig(context, object, gizmo_obj):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    MCH_PELVIS_PARENT = 'MCH-pelvis_parent'
    MCH_SPINE01_PARENT = 'MCH-spine01_parent'
    MCH_SPINE01_FK_PARENT = 'MCH-spine01_FK_parent'
    MCH_SPINE02_PARENT = 'MCH-spine02_parent'
    MCH_SPINE03_PARENT = 'MCH-spine03_parent'    
    PELVIS_FK = 'pelvis_FK'
    SPINE01_FK = 'spine01_FK'
    SPINE02_FK = 'spine02_FK'    
    
    # Create parent bones for 4 torso bones
    pelvis_bone = object.data.edit_bones['pelvis']
    head = pelvis_bone.tail.copy()
    tail = head.copy()
    tail.z += 0.05
    createNewBone(object, MCH_PELVIS_PARENT, 'root', False, head, tail, 0, 25)
    pelvis_bone.use_connect = False
    pelvis_bone.parent = object.data.edit_bones[MCH_PELVIS_PARENT]
    
    spine01_bone = object.data.edit_bones['spine01']
    # Move the spine01 bone up a bit, because otherwise gaming engines think that pelvis bone's
    # length is 0 (as pelvis and spine01 will have same head position when pelvis is flipped).
    spine01_bone.head.z += 0.02
    
    head = spine01_bone.head.copy()
    tail = head.copy()
    tail.z += 0.06
    createNewBone(object, MCH_SPINE01_PARENT, 'pelvis', False, head, tail, 0, 25)
        
    spine01_bone.use_connect = False
    spine01_bone.parent = object.data.edit_bones[MCH_SPINE01_PARENT]
    spine01_bone.use_inherit_scale = True  # We will allow scaling of chest and stomach of the body
    
    spine02_bone = object.data.edit_bones['spine02']
    head = spine02_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_SPINE02_PARENT, 'spine01', True, head, tail, 0, 25)
    spine02_bone.use_connect = False
    spine02_bone.parent = object.data.edit_bones[MCH_SPINE02_PARENT]
    spine02_bone.use_inherit_scale = True  # We will allow scaling of chest and stomach of the body

    spine03_bone = object.data.edit_bones['spine03']
    head = spine03_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_SPINE03_PARENT, 'spine02', False, head, tail, 0, 25)    
    spine03_bone.use_connect = False
    spine03_bone.parent = object.data.edit_bones[MCH_SPINE03_PARENT]
    spine02_bone.use_inherit_scale = True
    
    # For female characters, move breast bones to torso layer
    if 'breast_L' in object.data.edit_bones:
        object.data.edit_bones['breast_L'].layers[3] = True
        object.data.edit_bones['breast_R'].layers[3] = True
    
    # Flip the pelvis deformation bone
    pelvis_head = pelvis_bone.head.copy()
    pelvis_bone.head = pelvis_bone.tail.copy()  
    pelvis_bone.tail = pelvis_head
        
    # Create the FK control bones, with pelvis bone as parent to make sure they all move along when
    # the pelvis bone is translated
    head = pelvis_bone.tail.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, PELVIS_FK, 'root', False, head, tail, 0, 3)

    head = spine01_bone.head.copy()
    tail = head.copy()
    tail.z += 0.07
    createNewBone(object, MCH_SPINE01_FK_PARENT, 'pelvis', False, head, tail, 0, 25)
    
    head = spine01_bone.head.copy()
    tail = head.copy()
    tail.z += 0.08
    createNewBone(object, SPINE01_FK, MCH_SPINE01_FK_PARENT, False, head, tail, 0, 3)    

    head = spine02_bone.head.copy()
    tail = head.copy()
    tail.z += 0.12
    createNewBone(object, SPINE02_FK, 'root', False, head, tail, 0, 3)
        
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # Add constraints for copy rotation/location/transforms
    pose_pelvis_parent = object.pose.bones[MCH_PELVIS_PARENT]
    addCopyConstraint(object, pose_pelvis_parent, 'COPY_ROTATION', 'FK_ROT', 1.0, PELVIS_FK)
    location_constraint = addCopyConstraint(object, pose_pelvis_parent, 'COPY_LOCATION', 'FK_LOC',
        1.0, PELVIS_FK)
    if location_constraint:
        location_constraint.owner_space = 'LOCAL'
        location_constraint.target_space = 'LOCAL'
        
    pose_spine01_parent = object.pose.bones[MCH_SPINE01_PARENT]
    addCopyConstraint(object, pose_spine01_parent, 'COPY_TRANSFORMS', 'FK', 1.0, SPINE01_FK)
    
    pose_spine01_fk_parent = object.pose.bones[MCH_SPINE01_FK_PARENT]    
    addCopyConstraint(object, pose_spine01_fk_parent, 'COPY_ROTATION', 'FK2', 0.5, SPINE02_FK)
    
    pose_spine02_parent = object.pose.bones[MCH_SPINE02_PARENT]
    addCopyConstraint(object, pose_spine02_parent, 'COPY_TRANSFORMS', 'FK', 1.0, SPINE02_FK)
    
    # This is required to make sure that spine02 follows pelvis movement, so that there is no
    # torso stretch
    pose_spine02_fk = object.pose.bones[SPINE02_FK]
    location_constraint = addCopyConstraint(object, pose_spine02_fk, 'COPY_LOCATION', 'FK', 1.0,
        PELVIS_FK)
    if location_constraint:
        location_constraint.owner_space = 'LOCAL'
        location_constraint.target_space = 'LOCAL'

    # Spine 03 bone allows for bending in torso in the rib cage region. The influence is low
    # because there is very limited bending of torso in the rib cage in humans.
    pose_spine03_parent = object.pose.bones[MCH_SPINE03_PARENT]
    rot_constraint = addCopyConstraint(object, pose_spine03_parent, 'COPY_ROTATION', 'FK_ROT', 0.15,
        SPINE02_FK)
    if rot_constraint:
        rot_constraint.owner_space = 'LOCAL'
        rot_constraint.target_space = 'LOCAL'
    addCopyConstraint(object, pose_spine03_parent, 'COPY_SCALE', 'FK_SCALE', 1.0, SPINE02_FK)
    
    # Lock location for spine01 and spine02 FK bones
    pose_pelvis_fk = object.pose.bones[PELVIS_FK]
    pose_pelvis_fk.lock_scale = [True, True, True]
    
    pose_spine01_fk = object.pose.bones[SPINE01_FK]
    pose_spine01_fk.lock_location = [True, True, True]
    
    pose_spine02_fk = object.pose.bones[SPINE02_FK]
    pose_spine02_fk.lock_location = [True, True, True]
    
    # Add custom shapes for torso bones
    setCustomShape(object, PELVIS_FK, 'GZM_pelvis', 1.0)
    setCustomShape(object, SPINE01_FK, 'GZM_spine', 1.0)
    setCustomShape(object, SPINE02_FK, 'GZM_chest', 1.0)
    pose_spine02_fk.custom_shape_transform = object.pose.bones['spine02']
    
    # If breasts are present, lock scaling and location transforms and add custom shapes
    if 'breast_L' in object.pose.bones:
        pose_breast_L = object.pose.bones['breast_L']
        pose_breast_L.lock_location = [True, True, True]
        pose_breast_L.lock_scale = [True, True, True]
        
        pose_breast_R = object.pose.bones['breast_R']
        pose_breast_R.lock_location = [True, True, True]
        pose_breast_R.lock_scale = [True, True, True]

        setCustomShape(object, 'breast_L', 'GZM_breasts', 1.0)
        setCustomShape(object, 'breast_R', 'GZM_breasts', 1.0)

def addFingerBendDriver(object, source, target_bone):
    driver = source.driver_add('rotation_euler', 0).driver
    
    var = driver.variables.new()
    var.type = 'TRANSFORMS'
    var.name = 'x'
    var.targets[0].id = object
    var.targets[0].bone_target = target_bone
    var.targets[0].transform_type = 'SCALE_Y'
    var.targets[0].transform_space = 'LOCAL_SPACE'
    
    driver.expression = '(x - 1) * ' + str(PI)
    
def addOneFingerRig(context, object, finger, L_R, gizmo_obj):
    VIEW_LAYER = 6
    TWEAK_VIEW_LAYER = 7
    MCH_LAYER = 25

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    MCH_FINGER02_parent = 'MCH-' + finger + '02_parent_FK_' + L_R
    MCH_FINGER03_parent = 'MCH-' + finger + '03_parent_FK_' + L_R
    FINGER_FK = finger + '_FK_' + L_R
    FINGER01 = finger + '01_' + L_R
    FINGER02 = finger + '02_' + L_R
    FINGER03 = finger + '03_' + L_R
    
    # Create bones which will act as parents for rotation
    copyDeformationBone(object, MCH_FINGER02_parent, FINGER02, FINGER01, False, MCH_LAYER)
    copyDeformationBone(object, MCH_FINGER03_parent, FINGER03, FINGER02, False, MCH_LAYER)
    
    # Set deform bones' parents to new bones created above
    finger02_bone = object.data.edit_bones[FINGER02]
    finger02_bone.use_connect = False
    finger02_bone.parent = object.data.edit_bones[MCH_FINGER02_parent]
    finger02_bone.layers[TWEAK_VIEW_LAYER] = True

    finger03_bone = object.data.edit_bones[FINGER03]
    finger03_bone.use_connect = False
    finger03_bone.parent = object.data.edit_bones[MCH_FINGER03_parent]
    finger03_bone.layers[TWEAK_VIEW_LAYER] = True
    
    # Create the finger FK control bone
    finger01_bone = object.data.edit_bones[FINGER01]
    head = finger01_bone.head.copy()
    tail = finger03_bone.tail.copy()
    roll = finger01_bone.roll
    createNewBone(object, FINGER_FK, finger01_bone.parent.name, False, head, tail, roll, VIEW_LAYER)
    
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # Create rotation constraint
    pose_finger01 = object.pose.bones[FINGER01]
    rotation_constraint = addCopyConstraint(object, pose_finger01, 'COPY_ROTATION', 'FK', 1.0,
        FINGER_FK)
    if rotation_constraint:
        rotation_constraint.owner_space = 'LOCAL'
        rotation_constraint.target_space = 'LOCAL'
    
    # Create drivers to bend fingers on scale
    pose_finger02_parent = object.pose.bones[MCH_FINGER02_parent]
    pose_finger02_parent.rotation_mode = 'YZX'
    addFingerBendDriver(object, pose_finger02_parent, FINGER_FK)
    
    pose_finger03_parent = object.pose.bones[MCH_FINGER03_parent]
    pose_finger03_parent.rotation_mode = 'YZX'
    addFingerBendDriver(object, pose_finger03_parent, FINGER_FK)
    
    pose_finger_fk = object.pose.bones[FINGER_FK]
    pose_finger_fk.lock_scale = [True, False, True]
    pose_finger_fk.lock_location = [True, True, True]
    
    # Custom shapes for main finger control
    if finger == 'thumb':
        setCustomShape(object, FINGER_FK, 'GZM_Thumb', 1.0)
    else:
        setCustomShape(object, FINGER_FK, 'GZM_Finger', 1.0)    
    
    # Custom shapes for finger tweak controls
    setCustomShape(object, FINGER02, 'GZM_Circle', 1.0)
    setCustomShape(object, FINGER03, 'GZM_Circle', 1.5)
    
def addPalmRig(context, object, L_R):
    PINKY = 'pinky00_' + L_R
    RING = 'ring00_' + L_R
    MIDDLE = 'middle00_' + L_R    

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    pinky_palm_bone = object.data.edit_bones[PINKY]
    pinky_palm_bone.layers[6] = True
    
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    pose_ring_palm = object.pose.bones[RING]
    rot_constraint = addCopyConstraint(object, pose_ring_palm, 'COPY_ROTATION', 'PALM', 0.42,
        PINKY)
    if rot_constraint:
        rot_constraint.owner_space = 'LOCAL'
        rot_constraint.target_space = 'LOCAL'

    pose_middle_palm = object.pose.bones[MIDDLE]
    rot_constraint = addCopyConstraint(object, pose_middle_palm, 'COPY_ROTATION', 'PALM', 0.17,
        PINKY)
    if rot_constraint:
        rot_constraint.owner_space = 'LOCAL'
        rot_constraint.target_space = 'LOCAL'
    
    pose_pinky_palm = object.pose.bones[PINKY]
    pose_pinky_palm.rotation_mode = 'XYZ'
    pose_pinky_palm.lock_rotation = [False, True, True]
    pose_pinky_palm.lock_scale = [True, True, True]
    
    # Set custom shape
    setCustomShape(object, PINKY, "GZM_Palm_" + L_R, 1.0)
    
    
    

