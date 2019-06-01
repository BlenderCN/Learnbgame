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
from .utils import get_ik_group_name
from .utils import snappable_module
from .utils import create_twist_bones
from .utils import get_parent_name


def biped_arm(bvh_tree, shape_collection, module, chain, pole_target_name, forearm_bend_back_limit, ik_hand_parent_name, pole_target_parent_name, side, upperarm_twist_count, forearm_twist_count):
    
    rig = bpy.context.object
    
    # chain length should be exactly 4
    shoulder_name = chain[0]
    upperarm_name = chain[1]
    forearm_name = chain[2]
    hand_name = chain[3]
    
    first_parent_name = get_parent_name(chain[0])
    
    fk_prefix = Constants.fk_prefix
    ik_prefix = Constants.ik_prefix
    
    # bones that should be used for animation
    relevant_bone_names = []

    # bone that holds all properties of the module
    prop_bone_name = create_module_prop_bone(module=module)

    # LOW-LEVEL BONES
    # set parents
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebones[shoulder_name].parent = ebones[first_parent_name]
    ebones[upperarm_name].parent = ebones[shoulder_name]
    ebones[forearm_name].parent = ebones[upperarm_name]
    ebones[hand_name].parent = ebones[forearm_name]
    
    for name in chain:
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

    # SHOULDER BONE:
    # FK
    name = fk_prefix + shoulder_name
    duplicate_bone(source_name=shoulder_name, 
                   new_name=name, 
                   parent_name=first_parent_name
                   )
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.fk_layer, 
                  group_name=Constants.fk_group,  
                  lock_loc=True, 
                  lock_scale=True,  
                  bone_shape_name='sphere', 
                  bone_shape_pos='TAIL',
                  bone_type=Constants.fk_type
                  )
    relevant_bone_names.append(name)

    # bind low-level bones to FK constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[shoulder_name]

    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'bind_to_fk_1'
    c.target = rig
    c.subtarget = fk_prefix + shoulder_name
    c.mute = True

    # filler bones (needed for GYAZ retargeter)
    bpy.ops.object.mode_set(mode='EDIT')
    filler_name = 'fk_filler_' + shoulder_name
    ebone = rig.data.edit_bones.new(filler_name)
    ebones = rig.data.edit_bones
    ebone.head = ebones[first_parent_name].head
    ebone.tail = ebones[shoulder_name].head
    ebone.roll = 0
    ebone.parent = ebones[first_parent_name]
    
    bone_settings(bone_name=filler_name, 
                  layer_index=Constants.fk_extra_layer, 
                  )
    
    # _____________________________________________________________________________________________________

    # IK
    ik_group_name = get_ik_group_name(side)
    name = ik_prefix + shoulder_name
    
    duplicate_bone(source_name=shoulder_name, 
                   new_name=name, 
                   parent_name=first_parent_name
                   )
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=ik_group_name,  
                  lock_loc=True, 
                  lock_scale=True,  
                  bone_shape_name='cube', 
                  bone_shape_pos='TAIL', 
                  bone_type=Constants.ik_type
                  )
    relevant_bone_names.append(name)

    # bind low-level bones to IK constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[shoulder_name]

    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'bind_to_ik_1'
    c.target = rig
    c.subtarget = ik_prefix + shoulder_name
    c.mute = True

    # BIND TO (0: FK, 1: IK, 2:BIND)
    prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                             bone_name=shoulder_name, 
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
                             bone_name=shoulder_name, 
                             constraint_name='bind_to_ik_1',
                             prop_name='switch_' + module, 
                             attribute='mute', 
                             prop_min=0, 
                             prop_max=2,
                             prop_default=0, 
                             description='0:fk, 1:ik, 2:base',
                             expression='1 - (v1 > 0 and v1 < 2)'
                             )
    bone_visibility(prop_bone_name=prop_bone_name, 
                    module=module, 
                    relevant_bone_names=relevant_bone_names, 
                    ik_ctrl='ik'
                    )

    # SNAP INFO
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[prop_bone_name]
    pbone['snapinfo_singlebone_0'] = [fk_prefix + shoulder_name, ik_prefix + shoulder_name]

    # three bone limb set-up
    three_bone_limb(bvh_tree, 
                    shape_collection, 
                    module=module, 
                    b1=upperarm_name, 
                    b2=forearm_name, 
                    b3=hand_name, 
                    pole_target_name=pole_target_name, 
                    parent_pole_target_to_ik_target=False,
                    b2_bend_axis='X',
                    b2_bend_back_limit=forearm_bend_back_limit, 
                    first_parent_name=shoulder_name, 
                    ik_b3_parent_name=ik_hand_parent_name, 
                    pole_target_parent_name=pole_target_parent_name, 
                    b3_shape_up=False,
                    side=side
                    )
    isolate_rotation(module=module, 
                     parent_bone_name=fk_prefix + shoulder_name, 
                     first_bone_name=fk_prefix + upperarm_name
                     )

    # set module name on relevant bones (used by the 'N-panel' interface)
    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )

    # make the 'Snap&Key' operator recognize this module
    snappable_module(module)
    
    # TWIST BONES
    create_twist_bones(bvh_tree=bvh_tree, 
                       shape_collection=shape_collection, 
                       source_bone_name=upperarm_name, 
                       count=upperarm_twist_count,
                       upper_or_lower_limb='UPPER', 
                       twist_target_distance=Constants.twist_target_distance, 
                       end_affector_name='', 
                       influences=Constants.upperarm_twist_influences, 
                       is_thigh=False
                       )
    create_twist_bones(bvh_tree=bvh_tree, 
                       shape_collection=shape_collection, 
                       source_bone_name=forearm_name, 
                       count=forearm_twist_count,
                       upper_or_lower_limb='LOWER', 
                       twist_target_distance=Constants.twist_target_distance, 
                       end_affector_name=hand_name, 
                       influences=Constants.forearm_twist_influences, 
                       is_thigh=False
                       )
