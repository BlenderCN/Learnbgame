# coding: utf-8
import os
import sys


FS_ENCODING=sys.getfilesystemencoding()
if os.path.exists(os.path.dirname(sys.argv[0])+"/utf8"):
    INTERNAL_ENCODING='utf-8'
else:
    INTERNAL_ENCODING=FS_ENCODING


"""
custom property keys
"""
MMD_SHAPE_GROUP_NAME='_MMD_SHAPE'

MMD_MB_NAME='mb_name'
MMD_ENGLISH_NAME='english_name'

MMD_MB_COMMENT='mb_comment'
MMD_COMMENT='comment'
MMD_ENGLISH_COMMENT='english_comment'

BONE_ENGLISH_NAME='english_name'
BONE_USE_TAILOFFSET='bone_use_tailoffset'
BONE_CAN_TRANSLATE='bone_can_translate'
IK_UNITRADIAN='ik_unit_radian'

BASE_SHAPE_NAME='Basis'
RIGID_NAME='rigid_name'
RIGID_SHAPE_TYPE='rigid_shape_type'
RIGID_PROCESS_TYPE='rigid_process_type'
RIGID_BONE_NAME='rigid_bone_name'
RIGID_GROUP='ribid_group'
RIGID_INTERSECTION_GROUP='rigid_intersection_group'
RIGID_WEIGHT='rigid_weight'
RIGID_LINEAR_DAMPING='rigid_linear_damping'
RIGID_ANGULAR_DAMPING='rigid_angular_damping'
RIGID_RESTITUTION='rigid_restitution'
RIGID_FRICTION='rigid_friction'
CONSTRAINT_NAME='const_name'
CONSTRAINT_A='const_a'
CONSTRAINT_B='const_b'
CONSTRAINT_POS_MIN='const_pos_min'
CONSTRAINT_POS_MAX='const_pos_max'
CONSTRAINT_ROT_MIN='const_rot_min'
CONSTRAINT_ROT_MAX='const_rot_max'
CONSTRAINT_SPRING_POS='const_spring_pos'
CONSTRAINT_SPRING_ROT='const_spring_rot'
TOON_TEXTURE_OBJECT='ToonTextures'

MATERIALFLAG_BOTHFACE='material_flag_bothface'
MATERIALFLAG_GROUNDSHADOW='material_flag_groundshadow'
MATERIALFLAG_SELFSHADOWMAP='material_flag_selfshadowmap'
MATERIALFLAG_SELFSHADOW='material_flag_drawselfshadow'
MATERIALFLAG_EDGE='material_flag_drawedge'
MATERIAL_SHAREDTOON='material_shared_toon'
MATERIAL_SPHERE_MODE='material_sphere_mode'
TEXTURE_TYPE='texture_type'

