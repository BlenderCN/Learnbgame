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
from mathutils import Vector

from .constants import Constants
from .utils import duplicate_bone
from .utils import bone_settings
from .utils import prop_to_drive_constraint
from .utils import prop_to_drive_layer
from .utils import get_ik_group_name
from .utils import bone_visibility
from .utils import translate_bone_local

def ik_prop_bone(bvh_tree, shape_collection, name, source_bone_name, parent_name):
    
    duplicate_bone(source_name=source_bone_name, 
                   new_name=name, 
                   parent_name=parent_name
                   )
    bone_settings(bvh_tree=bvh_tree,
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.ik_prop_layer, 
                  group_name=Constants.ik_prop_group, 
                  lock_scale=True,  
                  bone_shape_name='cube_outer', 
                  bone_shape_pos='HEAD',
                  bone_type=Constants.ik_prop_type
                  )

def touch_bone(bvh_tree, shape_collection, module, source_bone_name, ik_bone_name, side, bone_shape_up):
    
    rig = bpy.context.object
    
    group = get_ik_group_name(side)

    name = 'touch_' + source_bone_name
    duplicate_bone(source_name=source_bone_name, 
                   new_name=name, 
                   parent_name=''
                   )
    
    bpy.ops.object.mode_set(mode='POSE')
    
    bone_settings(bvh_tree=bvh_tree,
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.touch_layer, 
                  group_name=group, 
                  lock_scale=True,  
                  bone_shape_name='twist_target', 
                  bone_shape_pos='HEAD',
                  bone_shape_manual_scale=rig.pose.bones[ik_bone_name].custom_shape_scale,
                  bone_shape_up=bone_shape_up,
                  bone_type=Constants.touch_type
                  )
    
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbone = pbones[name]
    c = pbone.constraints.new('CHILD_OF')
    c.name = 'Touch Bone'
    c.target = rig
    # set inverse matrix
    rig.data.bones.active = rig.data.bones[name]
    context_copy = bpy.context.copy()
    context_copy["constraint"] = pbone.constraints['Touch Bone']
    bpy.ops.constraint.childof_set_inverse(context_copy, constraint='Touch Bone', owner='BONE')

    # ik bone copy touch bone transforms
    pbone = pbones[ik_bone_name]
    c = pbone.constraints.new('COPY_TRANSFORMS')
    c.name = 'Copy Touch Bone'
    c.target = rig
    c.subtarget = name
    c.mute = False

    prop_to_drive_constraint(prop_bone_name=ik_bone_name, 
                             bone_name=ik_bone_name, 
                             constraint_name='Copy Touch Bone',
                             prop_name='touch_active_' + module, 
                             attribute='influence', 
                             prop_min=0.0,
                             prop_max=1.0, 
                             prop_default=0.0, 
                             description='', 
                             expression='v1'
                             )

    # visibility
    bone_visibility(prop_bone_name='module_props__' + module, 
                    module=module, 
                    relevant_bone_names=[name], 
                    ik_ctrl='touch'
                    )

    # for ui
    pbone = pbones[name]
    pbone['module'] = module


def chain_target(bvh_tree, shape_collection, fk_chain, ik_chain, chain_target_distance, chain_target_size, target_name, bone_shape_name, use_copy_loc, copy_loc_target_bone_name, add_constraint_to_layer, module, prop_name):
    
    rig = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT')
    ebone = rig.data.edit_bones.new(name=target_name)
    ebone.head = rig.data.edit_bones[fk_chain[-1]].head + Vector((0, -chain_target_distance, 0))
    ebone.tail = ebone.head + Vector((0, 0, chain_target_size))
    ebone.roll = 0
    bone_settings(bvh_tree=bvh_tree,
                  shape_collection=shape_collection,
                  bone_name=target_name, 
                  layer_index=Constants.target_layer, 
                  group_name=Constants.target_group, 
                  lock_rot=True, 
                  lock_scale=True,
                  bone_shape_name=bone_shape_name,
                  bone_shape_manual_scale=chain_target_size / 4
                  )

    # servants
    def create_servants(layer, source_bones):
        servants = []
        for name in source_bones:
            bpy.ops.object.mode_set(mode='EDIT')
            servant = 'target_servant_' + name
            duplicate_bone(source_name=name, 
                           new_name=servant, 
                           parent_name='', 
                           half_long=True
                           )
            ebones = rig.data.edit_bones
            ebone = ebones[servant]
            ebone.roll = 0
            ebone.parent = ebones[target_name]
            
            translate_bone_local(name=servant, 
                                 vector=(0, 0, chain_target_distance)
                                 )
            bone_settings(bone_name=servant, 
                          layer_index=layer,
                          lock_loc=True,
                          lock_rot=True, 
                          lock_scale=True
                          )
            servants.append(servant)
        return servants

    servants = create_servants(layer=Constants.fk_extra_layer, 
                               source_bones=fk_chain
                               )

    # CONSTRAINT TO TARGET
    def constraint_to_target(servants, constraint_bones):
        bpy.ops.object.mode_set(mode='POSE')
        pbones = rig.pose.bones
        for index, name in enumerate(constraint_bones):
            c = pbones[name].constraints.new('TRACK_TO')
            c.target = rig
            c.subtarget = servants[index]
            c.up_axis = 'UP_Y'
            c.track_axis = 'TRACK_Z'
            c.influence = 0
            c.name = target_name

            prop_to_drive_constraint(prop_bone_name=name, 
                                     bone_name=name, 
                                     constraint_name=c.name,
                                     prop_name=name + '_to_' + target_name, 
                                     attribute='influence',
                                     prop_min=0.0, 
                                     prop_max=1.0, 
                                     prop_default=0.0, 
                                     description='',
                                     expression='v1'
                                     )

    constraint_to_target(servants=servants, 
                         constraint_bones=fk_chain
                         )

    if use_copy_loc:
        bpy.ops.object.mode_set(mode='POSE')
        pbones = rig.pose.bones
        c = pbones[target_name].constraints.new('COPY_LOCATION')
        c.name = 'Copy ' + copy_loc_target_bone_name
        c.target = rig
        c.subtarget = copy_loc_target_bone_name
        c.use_offset = True
        c.target_space = 'LOCAL'
        c.owner_space = 'LOCAL'

        prop_to_drive_constraint(prop_bone_name=target_name, 
                                 bone_name=target_name, 
                                 constraint_name=c.name,
                                 prop_name='stick_to_' + copy_loc_target_bone_name, 
                                 attribute='influence',
                                 prop_min=0.0, 
                                 prop_max=1.0, 
                                 prop_default=0.0, 
                                 description='',
                                 expression='v1'
                                 )

    if add_constraint_to_layer:
        prop_to_drive_layer(prop_bone_name='module_props__' + module, 
                            layer_index=Constants.target_layer,
                            prop_name=prop_name, 
                            prop_min=0, 
                            prop_max=1, 
                            prop_default=0, 
                            description='',
                            expression='v1'
                            )

    # CONSTRAINT CTRL RIG TO CHEST TARGET
    servants = create_servants(layer=Constants.ctrl_ik_extra_layer, 
                               source_bones=ik_chain
                               )
    constraint_to_target(servants=servants, 
                         constraint_bones=ik_chain
                         )
