import bpy
from .utils import *

PI = 3.14159
    
def addOneLegIK(context, object, L_R):    
    VIEW_LAYER = 4
    MCH_LAYER = 24
    # create all the bones we need. These are created in a topologically sorted manner,
    # so that parents can be set correctly during creation of bones themselves.
    # MCH bones are mechanism bones which will be hidden from the user
    
    MCH_THIGH = 'MCH-thigh_IK_' + L_R
    MCH_CALF = 'MCH-calf_IK_' + L_R
    MCH_FOOT = 'MCH-foot_IK_' + L_R
    MCH_FOOT_ROLL_PARENT = 'MCH-foot_roll_parent_IK_' + L_R
    MCH_FOOT_ROCKER = 'MCH-foot_rocker_IK_' + L_R
    FOOT_IK = 'foot_IK_' + L_R
    TOES_IK = 'toes_IK_' + L_R
    FOOT_ROLL_IK = 'foot_roll_IK_' + L_R
    KNEE_TARGET_IK = 'knee_target_IK_' + L_R
        
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    copyDeformationBone(object, MCH_THIGH, 'thigh_' + L_R, 'pelvis', False, MCH_LAYER)
    copyDeformationBone(object, MCH_CALF, 'calf_' + L_R, MCH_THIGH, True, MCH_LAYER)    
    copyDeformationBone(object, FOOT_IK, 'foot_' + L_R, 'root', False, VIEW_LAYER)
    
    # Create the foot roll parent
    foot = object.data.edit_bones['foot_' + L_R]
    head = foot.tail.copy()
    tail = foot.head.copy()
    head.y = tail.y
    createNewBone(object, MCH_FOOT_ROLL_PARENT, FOOT_IK, False, head, tail, 0, MCH_LAYER)
    
    # Create the foot rocker Bone
    foot = object.data.edit_bones['foot_' + L_R]
    head = foot.tail.copy()
    tail = foot.head.copy()
    tail.z = head.z
    createNewBone(object, MCH_FOOT_ROCKER,  MCH_FOOT_ROLL_PARENT, False, head, tail, 0, MCH_LAYER)
    
    copyDeformationBone(object, MCH_FOOT, 'foot_' + L_R, MCH_FOOT_ROCKER, False, MCH_LAYER)    
    copyDeformationBone(object, TOES_IK, 'toes_' + L_R, MCH_FOOT_ROLL_PARENT, False, VIEW_LAYER)

    # Create the foot roll control
    head = foot.tail.copy()
    head.y += 0.2
    tail = head.copy()
    tail.z += 0.08
    tail.y += 0.02
    createNewBone(object, FOOT_ROLL_IK, FOOT_IK, False, head, tail, 0, VIEW_LAYER)
        
    # Create knee target IK control bone
    calf = object.data.edit_bones['calf_' + L_R]
    head = calf.head.copy()  # knee position
    head.y -= 0.7
    tail = head.copy()
    tail.y -= 0.1
    createNewBone(object, KNEE_TARGET_IK, MCH_FOOT, False, head, tail, 0, VIEW_LAYER)
    
    # Switch to pose mode to add all the constraints
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # first, set copy rotation constraints on deformation bones, to copy IK bones' rotations
    # also add drivers for FK --> IK Control
    DRIVER_TARGET = '["LegIk_' + L_R + '"]'
    
    pose_thigh = object.pose.bones['thigh_' + L_R]
    constraint = addCopyConstraint(object, pose_thigh, 'COPY_ROTATION', 'IK', 0.0, MCH_THIGH)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_calf = object.pose.bones['calf_' + L_R]
    constraint = addCopyConstraint(object, pose_calf, 'COPY_ROTATION', 'IK', 0.0, MCH_CALF)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_foot = object.pose.bones['foot_' + L_R]
    constraint = addCopyConstraint(object, pose_foot, 'COPY_ROTATION', 'IK', 0.0, MCH_FOOT)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)

    pose_toes = object.pose.bones['toes_' + L_R]
    constraint = addCopyConstraint(object, pose_toes, 'COPY_ROTATION', 'IK', 0.0, TOES_IK)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    # next, add the IK constraint itself
    pose_calf_IK = object.pose.bones[MCH_CALF]
    if 'IK' not in pose_calf_IK.constraints:
        constraint = pose_calf_IK.constraints.new('IK')
        constraint.name = 'IK'
        constraint.influence = 1.0
        constraint.target = object
        constraint.subtarget = MCH_FOOT
        constraint.pole_target = object
        constraint.pole_subtarget = KNEE_TARGET_IK
        constraint.pole_angle = PI / 2.0
        constraint.chain_count = 2
        pose_calf_IK.lock_ik_y = True
        pose_calf_IK.lock_ik_z = True

    # Create the foot roll mechanism
    pose_mch_foot_rocker = object.pose.bones[MCH_FOOT_ROCKER]
    copyConstraint = addCopyConstraint(object, pose_mch_foot_rocker, 'COPY_ROTATION', 'FOOT_ROLL',
        1.0, FOOT_ROLL_IK)
    if copyConstraint:
        copyConstraint.owner_space = 'LOCAL'
        copyConstraint.target_space = 'LOCAL'

    limitConstraint = addLimitConstraint(pose_mch_foot_rocker, 'LIMIT_ROTATION', 'FOOT_ROLL_LIMIT',
        1.0, [True, 0, PI / 2.0])
    if limitConstraint:
        limitConstraint.owner_space = 'LOCAL'
    
    pose_foot_roll_parent = object.pose.bones[MCH_FOOT_ROLL_PARENT]
    copyConstraint = addCopyConstraint(object, pose_foot_roll_parent, 'COPY_ROTATION', 'FOOT_ROLL',
        1.0, FOOT_ROLL_IK)
    if copyConstraint:        
        copyConstraint.owner_space = 'LOCAL'
        copyConstraint.target_space = 'LOCAL'
    
    limitConstraint = addLimitConstraint(pose_foot_roll_parent, 'LIMIT_ROTATION', 'FOOT_ROLL_LIMIT',
        1.0, [True, -1.0 * (PI / 2.0), 0])
    if limitConstraint:
        limitConstraint.owner_space = 'LOCAL'
    
    # Limit transformations
    pose_foot_ik = object.pose.bones[FOOT_IK]
    pose_foot_ik.lock_scale = [True, True, True]

    pose_knee_target_ik = object.pose.bones[KNEE_TARGET_IK]
    pose_knee_target_ik.lock_scale = [True, True, True]
    pose_knee_target_ik.rotation_mode = 'XYZ'
    pose_knee_target_ik.lock_rotation = [True, True, True]
    
    pose_foot_roll = object.pose.bones[FOOT_ROLL_IK]
    pose_foot_roll.rotation_mode = 'XYZ'
    pose_foot_roll.lock_scale = [True, True, True]
    pose_foot_roll.lock_location = [True, True, True]
    pose_foot_roll.lock_rotation = [False, True, True]
        
    pose_toes_IK = object.pose.bones[TOES_IK]
    pose_toes_IK.rotation_mode = 'YZX'
    pose_toes_IK.lock_scale = [True, True, True]
    pose_toes_IK.lock_location = [True, True, True]
    pose_toes_IK.lock_rotation = [False, True, True]
    
    # Set custom shapes
    setCustomShape(object, FOOT_IK, 'GZM_Foot_IK', 1.0)
    setCustomShape(object, FOOT_ROLL_IK, 'GZM_Foot_Roll_IK', 1.0)
    pose_foot_roll.custom_shape_transform = object.pose.bones[MCH_FOOT]
    setCustomShape(object, TOES_IK, 'GZM_Toes_IK', 1.0)       
    L_R_flip = 'L' if L_R == 'R' else 'R'    
    setCustomShape(object, KNEE_TARGET_IK, 'GZM_Elbow_' + L_R_flip, 1.5)
    
def addOneArmIK(context, object, L_R):    
    VIEW_LAYER = 5
    MCH_LAYER = 24

    MCH_UPPERARM = 'MCH-upperarm_IK_' + L_R
    MCH_LOWERARM = 'MCH-lowerarm_IK_' + L_R
    HAND_IK = 'hand_IK_' + L_R
    ELBOW_TARGET_IK = 'elbow_target_IK_' + L_R

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    copyDeformationBone(object, MCH_UPPERARM, 'upperarm_' + L_R, 'clavicle_' + L_R, True, MCH_LAYER)
    copyDeformationBone(object, MCH_LOWERARM, 'lowerarm_' + L_R, MCH_UPPERARM, True, MCH_LAYER)    
    copyDeformationBone(object, HAND_IK, 'hand_' + L_R, 'root', False, VIEW_LAYER)

    # Create knee target IK control bone
    lowerarm = object.data.edit_bones['lowerarm_' + L_R]
    head = lowerarm.head.copy()  # elbow position
    head.y += 0.5
    tail = head.copy()
    tail.y += 0.1
    createNewBone(object, ELBOW_TARGET_IK, HAND_IK, False, head, tail, 0, VIEW_LAYER)
        
    # Switch to pose mode to add all the constraints
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # first, set copy rotation constraints on deformation bones, to copy IK bones' rotations
    # also add drivers for FK --> IK Control
    DRIVER_TARGET = '["ArmIk_' + L_R + '"]'
    
    pose_upperarm = object.pose.bones['upperarm_' + L_R]
    constraint = addCopyConstraint(object, pose_upperarm, 'COPY_ROTATION', 'IK', 0.0, MCH_UPPERARM)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_lowerarm = object.pose.bones['lowerarm_' + L_R]
    constraint = addCopyConstraint(object, pose_lowerarm, 'COPY_ROTATION', 'IK', 0.0, MCH_LOWERARM)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_hand = object.pose.bones['hand_' + L_R]
    constraint = addCopyConstraint(object, pose_hand, 'COPY_ROTATION', 'IK', 0.0, HAND_IK)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    # next, add the IK constraint itself
    pose_lowerarm = object.pose.bones[MCH_LOWERARM]
    if 'IK' not in pose_lowerarm.constraints:
        constraint = pose_lowerarm.constraints.new('IK')
        constraint.name = 'IK'
        constraint.influence = 1.0
        constraint.target = object
        constraint.subtarget = HAND_IK
        constraint.pole_target = object
        constraint.pole_subtarget = ELBOW_TARGET_IK
        constraint.pole_angle = -PI / 2.0
        constraint.chain_count = 2
        pose_lowerarm.lock_ik_y = True
        pose_lowerarm.lock_ik_z = True

    # limit transformations
    pose_hand_ik = object.pose.bones[HAND_IK]
    pose_hand_ik.lock_scale = [True, True, True]

    pose_hand_target_ik = object.pose.bones[ELBOW_TARGET_IK]
    pose_hand_target_ik.lock_scale = [True, True, True]
    pose_hand_target_ik.rotation_mode = 'XYZ'
    pose_hand_target_ik.lock_rotation = [True, True, True]

    # set custom shapes
    setCustomShape(object, HAND_IK, 'GZM_Hand_' + L_R + '_IK', 1.0)
    setCustomShape(object, ELBOW_TARGET_IK, 'GZM_Elbow_' + L_R, 1.0)






