# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any laTter version.
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


##########################################################################################################
##########################################################################################################

import bpy
from math import radians
from mathutils import Vector

from .constants import Constants
from .utils import create_module_prop_bone
from .utils import bone_settings
from .utils import duplicate_bone
from .utils import get_distance
from .utils import set_parent_chain
from .utils import prop_to_drive_constraint
from .utils import mirror_bone_to_point
from .utils import bone_visibility
from .utils import set_module_on_relevant_bones
from .utils import three_bone_limb
from .utils import isolate_rotation
from .utils import get_parent_name
from .utils import set_bone_only_layer
from .utils import get_ik_group_name
from .utils import prop_to_drive_pbone_attribute_with_array_index
from .utils import prop_to_drive_pbone_attribute_with_array_index
from .utils import create_twist_bones
from .utils import snappable_module


def biped_leg(bvh_tree, shape_collection, module, chain, pole_target_name, shin_bend_back_limit, ik_foot_parent_name, pole_target_parent_name, side, thigh_twist_count, shin_twist_count):
    
    # chain length should be exactly 4
    
    rig = bpy.context.object    
    ik_group_name = get_ik_group_name(side)

    thigh_name = chain[0]    
    shin_name = chain[1]    
    foot_name = chain[2]    
    toes_name = chain[3]
    
    first_parent_name = get_parent_name(thigh_name)
    
    fk_prefix = Constants.fk_prefix
    ik_prefix = Constants.ik_prefix
    ik_group_name = get_ik_group_name(side=side)
    
    toes_bend_axis = '-X'
    shin_bend_axis = '-X'
    
    # bones that should be used for animation
    relevant_bone_names = []

    # bone that holds all properties of the module
    prop_bone_name = create_module_prop_bone(module=module)

    # set parent
    first_parent_name = get_parent_name(thigh_name)

    # LOW-LEVEL BONES
    # set parents
    for index, name in enumerate(chain):
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        if index == 0:
            ebones[name].parent = ebones[first_parent_name]
        else:
            ebones[name].parent = ebones[chain[index - 1]]

        relevant_bone_names.append(name)
        
        bone_settings(bone_name=name, 
                      layer_index=Constants.base_layer, 
                      group_name=Constants.base_group, 
                      use_deform=True, 
                      lock_loc=True,
                      lock_scale=True,
                      bone_type=Constants.base_type
                      )
    # _____________________________________________________________________________________________________
    
    # three bone limb set-up
    three_bone_limb(bvh_tree=bvh_tree, 
                    shape_collection=shape_collection, 
                    module=module, 
                    b1=thigh_name, 
                    b2=shin_name, 
                    b3=foot_name, 
                    pole_target_name=pole_target_name, 
                    parent_pole_target_to_ik_target=True,
                    b2_bend_axis='-X',
                    b2_bend_back_limit=shin_bend_back_limit, 
                    first_parent_name=first_parent_name,
                    ik_b3_parent_name=ik_foot_parent_name, 
                    pole_target_parent_name=pole_target_parent_name, 
                    b3_shape_up=True,
                    side=side
                    )
    isolate_rotation(module=module, 
                     parent_bone_name=fk_prefix + first_parent_name, 
                     first_bone_name=fk_prefix + thigh_name
                     )

    # TOES BONE:
    # FK
    name = fk_prefix + toes_name
    duplicate_bone(source_name=toes_name, 
                   new_name=name, 
                   parent_name=fk_prefix + foot_name
                   )
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.fk_layer, 
                  group_name=Constants.fk_group, 
                  lock_loc=True, 
                  lock_scale=True,
                  bone_shape_name='sphere', 
                  bone_shape_pos='MIDDLE',
                  bone_shape_up=True,
                  bone_shape_up_only_for_transform=True,
                  bone_type=Constants.fk_type
                  )
    relevant_bone_names.append(name)

    # bind low-level bones to FK constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[toes_name]

    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'bind_to_fk_1'
    c.target = rig
    c.subtarget = fk_prefix + toes_name
    c.mute = True

    # lock toe axes
    if toes_bend_axis == 'X' or toes_bend_axis == '-X':
        lock_1 = 1
        lock_2 = 2

    for ai in [lock_1, lock_2]:
        prop_to_drive_pbone_attribute_with_array_index(prop_bone_name=name, 
                                                       bone_name=name,
                                                       prop_name='limit_fk_toes' + side,
                                                       attribute='lock_rotation', 
                                                       array_index=ai,
                                                       prop_min=0, 
                                                       prop_max=1, 
                                                       prop_default=0,
                                                       description='limit toes to single axis rotation',
                                                       expression='v1'
                                                       )

    # filler bones (needed for GYAZ retargeter)
    bpy.ops.object.mode_set(mode='EDIT')
    filler_name = 'fk_filler_' + thigh_name
    ebone = rig.data.edit_bones.new(name=filler_name)
    ebones = rig.data.edit_bones
    ebone.head = ebones[first_parent_name].head
    ebone.tail = ebones[thigh_name].head
    ebone.roll = 0
    ebone.parent = ebones[first_parent_name]
    set_bone_only_layer(bone_name=filler_name, 
                        layer_index=Constants.fk_extra_layer
                        )

    # IK
    name = ik_prefix + toes_name
    duplicate_bone(source_name=toes_name, 
                   new_name=name, 
                   parent_name=ik_prefix + foot_name
                   )
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=ik_group_name,
                  lock_loc=True,
                  lock_scale=True, 
                  bone_shape_name='cube', 
                  bone_shape_pos='MIDDLE',
                  bone_shape_up=True,
                  bone_shape_up_only_for_transform=True,
                  bone_type=Constants.ik_type
                  )
    relevant_bone_names.append(name)

    # lock toe axes
    if toes_bend_axis == 'X' or toes_bend_axis == '-X':
        lock_1 = 1
        lock_2 = 2

    for ai in [lock_1, lock_2]:
        prop_to_drive_pbone_attribute_with_array_index(prop_bone_name=name, 
                                                       bone_name=name,
                                                       prop_name='limit_ik_toes' + side,
                                                       attribute='lock_rotation', 
                                                       array_index=ai,
                                                       prop_min=0, 
                                                       prop_max=1, 
                                                       prop_default=1,
                                                       description='limit toes to single axis rotation',
                                                       expression='v1'
                                                       )

    # bind low-level bones to IK constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[toes_name]

    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'bind_to_ik_1'
    c.target = rig
    c.subtarget = ik_prefix + toes_name
    c.mute = True

    # BIND TO (0: FK, 1: IK, 2:BIND)
    prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                             bone_name=toes_name, 
                             constraint_name='bind_to_fk_1',
                             prop_name='switch_' + module, 
                             attribute='mute', 
                             prop_min=0, 
                             prop_max=2,
                             prop_default=0, 
                             description='0:fk, 1:ik, 2:base', 
                             expression='1 - (v1 < 1)'
                             )
    prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                             bone_name=toes_name, 
                             constraint_name='bind_to_ik_1',
                             prop_name='switch_' + module, 
                             attribute='mute', 
                             prop_min=0, 
                             prop_max=2,
                             prop_default=0, 
                             description='0:fk, 1:ik, 2:base',
                             expression='1 - (v1 > 0 and v1 < 2)'
                             )

    # SNAP INFO
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[prop_bone_name]
    pbone['snapinfo_singlebone_0'] = [fk_prefix + toes_name, ik_prefix + toes_name]

    # FOOT ROLL:
    # get heel position
    bpy.ops.object.mode_set(mode='EDIT')

    # set ray start and direction
    ray_start = rig.data.edit_bones[toes_name].head
    ray_direction = (0, 1, 0)
    ray_distance = 1

    # cast ray
    hit_loc, hit_nor, hit_index, hit_dist = bvh_tree.ray_cast(ray_start, 
                                                              ray_direction, 
                                                              ray_distance
                                                              )

    # third-point of toes.head and hit_loc(heel)
    difference = ray_start - hit_loc
    difference /= 3
    third_point = hit_loc + difference

    # ik foot main
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ik_foot_main_name = ik_prefix + 'main_' + foot_name
    ebone = ebones.new(name=ik_foot_main_name)
    ik_foot_name = ik_prefix + foot_name
    ik_foot_ebone = ebones[ik_foot_name]
    foot_length = get_distance(ik_foot_ebone.head, ik_foot_ebone.tail)
    ebone.head = ik_foot_ebone.head
    ebone.tail = (ik_foot_ebone.head[0], ik_foot_ebone.head[1] - foot_length, ik_foot_ebone.head[2])
    ebone.roll = radians(-180) if side == '_l' else radians(180)
    ebone.parent = ebones[ik_foot_parent_name]
    
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=ik_foot_main_name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=ik_group_name, 
                  lock_scale=True,
                  bone_shape_name='cube', 
                  bone_shape_pos='HEAD',
                  bone_shape_up=True,
                  bone_type=Constants.ik_type
                  )
    relevant_bone_names.append(ik_foot_main_name)

    # ik foot snap target
    snap_target_foot_name = 'snap_target_' + foot_name
    duplicate_bone(source_name=ik_foot_main_name, 
                   new_name=snap_target_foot_name, 
                   parent_name=fk_prefix + foot_name,
                   )
    bone_settings(bone_name=snap_target_foot_name, 
                  layer_index=Constants.fk_extra_layer, 
                  lock_loc=True, 
                  lock_rot=True, 
                  lock_scale=True
                  )

    # foot roll back
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    foot_roll_back_name = 'roll_back_' + foot_name
    ebone = ebones.new(name=foot_roll_back_name)
    ebone.head = hit_loc
    ebone.tail = third_point
    ebone.roll = ebones[foot_name].roll
    ebone.parent = ebones[ik_foot_main_name]
    
    bone_settings(bone_name=foot_roll_back_name, 
                  layer_index=Constants.ctrl_ik_extra_layer, 
                  group_name=ik_group_name, 
                  lock_loc=True, 
                  lock_scale=True
                  )

    # foot roll front
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    foot_roll_front_name = 'roll_front_' + foot_name
    ebone = ebones.new(name=foot_roll_front_name)
    ebone.head = ebones[toes_name].head
    ebone.tail = third_point
    ebone.roll = ebones[foot_name].roll
    ebone.parent = ebones[foot_roll_back_name]
    ebones[ik_prefix + foot_name].parent = ebones[foot_roll_front_name]
    
    bone_settings(bone_name=foot_roll_front_name, 
                  layer_index=Constants.ctrl_ik_extra_layer, 
                  group_name=ik_group_name, 
                  lock_loc=True, 
                  lock_scale=True
                  )

    # foot roll main
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    foot_roll_main_name = 'roll_main_' + foot_name
    ebone = ebones.new(name=foot_roll_main_name)
    ebone.head = ebones[foot_name].head
    length = get_distance(ebones[foot_name].head, ebones[foot_name].tail)
    ebone.tail = ebone.head + Vector((0, length, 0))
    ebone.roll = ebones[foot_name].roll
    ebone.parent = ebones[ik_foot_main_name]
    
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=foot_roll_main_name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=ik_group_name, 
                  lock_loc=True,
                  lock_scale=True,
                  bone_shape_name='foot_roll', 
                  bone_shape_pos='TAIL', 
                  bone_shape_manual_scale=Constants.target_shape_size,
                  bone_type=Constants.ik_type
                  )
    relevant_bone_names.append(foot_roll_main_name)

    # parent pole target to foot_roll_main_name
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebones['target_' + pole_target_name].parent = ebones[ik_foot_main_name]

    # ik_toes parent
    ik_toes_parent_name = ik_prefix + 'parent_' + toes_name
    duplicate_bone(source_name=ik_prefix + toes_name, 
                   new_name=ik_toes_parent_name, 
                   parent_name=ik_prefix + foot_name
                   )
    bone_settings(bone_name=ik_toes_parent_name, 
                  layer_index=Constants.ctrl_ik_extra_layer, 
                  lock_loc=True,
                  lock_scale=True
                  )
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebones[ik_prefix + toes_name].parent = ebones[ik_toes_parent_name]

    # relegate old ik_foot bone
    set_bone_only_layer(bone_name=ik_prefix + foot_name, 
                        layer_index=Constants.ctrl_ik_extra_layer
                        )
    # update snap_info
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    old_snap_info = pbones['module_props__' + module]["snapinfo_3bonelimb_0"]
    old_snap_info[9], old_snap_info[10], old_snap_info[11] = snap_target_foot_name, ik_foot_main_name, foot_roll_main_name
    pbones['module_props__' + module]["snapinfo_3bonelimb_0"] = old_snap_info

    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    # foot roll constraints:
    # foot roll front
    if toes_bend_axis == '-X':
        use_x = True
        use_z = False

    pbone = pbones[foot_roll_front_name]
    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'copy foot_roll_main'
    c.target = rig
    c.subtarget = foot_roll_main_name
    c.use_x = use_x
    c.use_y = False
    c.use_z = use_z
    c.invert_x = False
    c.invert_y = False
    c.invert_z = False
    c.use_offset = False
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    if toes_bend_axis == '-X':
        min_x = 0
        max_x = radians(180)
        min_z = 0
        max_z = 0

    c = pbone.constraints.new('LIMIT_ROTATION')
    c.name = 'limit rotation'
    c.owner_space = 'LOCAL'
    c.use_transform_limit = True
    c.influence = 1
    c.use_limit_x = True
    c.use_limit_y = True
    c.use_limit_z = True
    c.min_x = min_x
    c.max_x = max_x
    c.min_y = 0
    c.min_y = 0
    c.min_z = min_z
    c.max_z = max_z

    if toes_bend_axis == '-X':
        use_x = True
        use_z = False

    # foot roll back
    pbone = pbones[foot_roll_back_name]
    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'copy foot_roll_main_name'
    c.target = rig
    c.subtarget = foot_roll_main_name
    c.use_x = use_x
    c.use_y = False
    c.use_z = use_z
    c.invert_x = use_x
    c.invert_y = False
    c.invert_z = use_z
    c.use_offset = False
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    if toes_bend_axis == '-X':
        min_x = 0
        max_x = radians(180)
        min_z = 0
        max_z = 0

    c = pbone.constraints.new('LIMIT_ROTATION')
    c.name = 'limit rotation'
    c.owner_space = 'LOCAL'
    c.use_transform_limit = True
    c.influence = 1
    c.use_limit_x = True
    c.use_limit_y = True
    c.use_limit_z = True
    c.min_x = min_x
    c.max_x = max_x
    c.min_y = 0
    c.min_y = 0
    c.min_z = min_z
    c.max_z = max_z

    # foot roll main
    if toes_bend_axis == '-X':
        min_x = radians(-180)
        max_x = radians(180)
        min_z = 0
        max_z = 0

    pbone = pbones[foot_roll_main_name]
    c = pbone.constraints.new('LIMIT_ROTATION')
    c.name = 'limit rotation'
    c.owner_space = 'LOCAL'
    c.use_transform_limit = True
    c.influence = 1
    c.use_limit_x = True
    c.use_limit_y = True
    c.use_limit_z = True
    c.min_x = min_x
    c.max_x = max_x
    c.min_y = 0
    c.min_y = 0
    c.min_z = min_z
    c.max_z = max_z

    # ik_toes_parent
    if toes_bend_axis == '-X':
        use_x = True
        use_z = False

    pbone = pbones[ik_toes_parent_name]
    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'copy foot_roll_front'
    c.target = rig
    c.subtarget = foot_roll_front_name
    c.use_x = use_x
    c.use_y = False
    c.use_z = use_z
    c.invert_x = True
    c.invert_y = False
    c.invert_z = True
    c.use_offset = True
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    bone_visibility(prop_bone_name=prop_bone_name, 
                    module=module, 
                    relevant_bone_names=relevant_bone_names, 
                    ik_ctrl='ik'
                    )

    # set module name on relevant bones (used by the 'N-panel' interface)
    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )

    # make the 'Snap&Key' operator recognize this module
    snappable_module(module=module)

    # TWIST BONES
    create_twist_bones(bvh_tree=bvh_tree, 
                       shape_collection=shape_collection, 
                       source_bone_name=thigh_name, 
                       count=thigh_twist_count,
                       upper_or_lower_limb='UPPER', 
                       twist_target_distance=Constants.twist_target_distance, 
                       end_affector_name='', 
                       influences=Constants.forearm_twist_influences, 
                       is_thigh=True
                       )
    create_twist_bones(bvh_tree=bvh_tree, 
                       shape_collection=shape_collection, 
                       source_bone_name=shin_name, 
                       count=shin_twist_count,
                       upper_or_lower_limb='LOWER', 
                       twist_target_distance=Constants.twist_target_distance, 
                       end_affector_name=foot_name, 
                       influences=Constants.shin_twist_influences, 
                       is_thigh=False
                       )
                       