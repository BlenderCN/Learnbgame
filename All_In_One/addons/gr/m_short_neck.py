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
from .utils import bone_settings
from .utils import duplicate_bone
from .utils import snappable_module
from .utils import create_module_prop_bone
from .utils import set_module_on_relevant_bones
from .utils import prop_to_drive_constraint
from .utils import bone_visibility
from .utils import get_parent_name
from .utils import create_leaf_bone
from .utils import set_bone_only_layer


def short_neck(bvh_tree, shape_collection, module, bone_name, distributor_parent_name, ik_rot_bone_name, ik_loc_bone_name, use_twist):
    
    rig = bpy.context.object
    
    fk_prefix = Constants.fk_prefix
    ik_prefix = Constants.ik_prefix

    # bones that should be used for animation
    relevant_bone_names = []

    # bone that holds all properties of the module
    prop_bone_name = create_module_prop_bone(module=module)

    # set parent
    parent = get_parent_name(name=bone_name)

    # LOW-LEVEL BONES

    neck_name = bone_name
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebones[neck_name].parent = ebones[parent]
    
    bone_settings(bone_name=neck_name, 
                  layer_index=Constants.base_layer, 
                  group_name=Constants.base_group, 
                  use_deform=True, 
                  lock_loc=True, 
                  lock_scale=True, 
                  bone_type=Constants.base_type
                  )
    relevant_bone_names.append(neck_name)

    # _____________________________________________________________________________________________________

    # FK BONES

    bpy.ops.object.mode_set(mode='EDIT')
    name = fk_prefix + neck_name
    ebone = rig.data.edit_bones.new(name=name)
    ebones = rig.data.edit_bones
    ebone.head = ebones[neck_name].head
    ebone.tail = ebones[neck_name].tail
    ebone.roll = ebones[neck_name].roll
    ebone.parent = ebones[fk_prefix + parent]
    
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.fk_layer, 
                  group_name=Constants.fk_group,  
                  lock_loc=True,  
                  lock_scale=True, 
                  hide_select=False, 
                  bone_shape_name='inner_circle', 
                  bone_shape_pos='MIDDLE',
                  bone_type=Constants.fk_type
                  )
    relevant_bone_names.append(name)

    # LOW-LEVEL TO FK RIG constraint
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[neck_name]
    cs = pbone.constraints

    c = cs.new('COPY_ROTATION')
    c.name = 'bind_to_fk_1'
    c.target = rig
    c.subtarget = fk_prefix + neck_name
    c.mute = True

    # _____________________________________________________________________________________________________

    # TWIST BONES

    if use_twist == True:

        neck_twist_name = 'twist_1_' + neck_name
        
        duplicate_bone(source_name=neck_name, 
                       new_name=neck_twist_name, 
                       parent_name=neck_name, 
                       half_long=True
                       )
        bone_settings(bone_name=neck_twist_name, 
                      layer_index=Constants.twist_layer, 
                      group_name=Constants.twist_group, 
                      use_deform=True, 
                      lock_loc=True,  
                      lock_scale=True,
                      bone_type=Constants.twist_type
                      )

        # neck_mediator
        neck_mediator_name = 'neck_mediator'
        
        duplicate_bone(source_name=neck_name, 
                       new_name=neck_mediator_name, 
                       parent_name=rig.data.bones[neck_name].parent.name
                       )
        bone_settings(bone_name=neck_mediator_name, 
                      layer_index=Constants.misc_layer, 
                      lock_loc=True,  
                      lock_scale=True
                      )

        # constraints (neck_twist)
        pbone = rig.pose.bones[neck_twist_name]

        c = pbone.constraints.new('TRACK_TO')
        c.target = rig
        c.subtarget = 'head'
        c.head_tail = 0
        c.track_axis = 'TRACK_Y'
        c.up_axis = 'UP_Z'
        c.use_target_z = True
        c.target_space = 'POSE'
        c.owner_space = 'POSE'
        c.influence = Constants.neck_twist_track_to_head

        c = pbone.constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.use_limit_x = True
        c.use_limit_y = False
        c.use_limit_z = True
        c.min_x = 0
        c.max_x = 0
        c.min_z = 0
        c.max_z = 0
        c.use_transform_limit = True
        c.influence = 1

        c = pbone.constraints.new('COPY_ROTATION')
        c.target = rig
        c.subtarget = 'neck_mediator'
        c.use_x = True
        c.use_y = True
        c.use_z = True
        c.invert_x = False
        c.invert_y = False
        c.invert_z = False
        c.use_offset = False
        c.target_space = 'POSE'
        c.owner_space = 'POSE'
        c.influence = Constants.neck_twist_rotate_back

        c = pbone.constraints.new('LIMIT_ROTATION')
        c.owner_space = 'LOCAL'
        c.influence = 1
        c.use_limit_x = False
        c.use_limit_y = False
        c.use_limit_z = True
        c.min_x = 0
        c.max_x = 0
        c.min_y = 0
        c.max_y = 0
        c.min_z = radians(Constants.neck_twist_min_y)
        c.max_z = 0
        c.use_transform_limit = True

    # _____________________________________________________________________________________________________

    # IK BONES
    bpy.ops.object.mode_set(mode='EDIT')
    
    # distributor
    distributor_name = Constants.ctrl_prefix + neck_name
    ebone = rig.data.edit_bones.new(name=distributor_name)
    ebones = rig.data.edit_bones
    ebone.head = ebones[neck_name].head
    ebone.tail = ebone.head + Vector((0, 0, Constants.general_bone_size))
    ebone.parent = ebones[distributor_parent_name]
    
    bone_settings(bone_name=distributor_name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=Constants.central_ik_group, 
                  lock_loc=True,  
                  lock_scale=True,
                  bone_type=Constants.ctrl_type
                  )
    # ctrl neck shape transform bone
    shape_bone_name = 'shape_' + distributor_name
    create_leaf_bone(bone_name=shape_bone_name, 
                     source_bone_name=neck_name, 
                     start_middle=True, 
                     parent_name=distributor_name
                     )
    set_bone_only_layer(bone_name=shape_bone_name, 
                        layer_index=Constants.misc_layer
                        )
    # use fk_neck's bone scale
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbones[distributor_name].custom_shape_transform = pbones[shape_bone_name]
    pbones[distributor_name].custom_shape = pbones[fk_prefix + neck_name].custom_shape
    pbones[distributor_name].custom_shape_scale = pbones[fk_prefix + neck_name].custom_shape_scale
    pbones[distributor_name].use_custom_shape_bone_size = pbones[fk_prefix + neck_name].use_custom_shape_bone_size
    
    # ik_neck
    name = ik_prefix + neck_name
    
    duplicate_bone(source_name=neck_name, 
                   new_name=name, 
                   parent_name=distributor_name
                   )
    bone_settings(bone_name=name, 
                  layer_index=Constants.ctrl_ik_extra_layer, 
                  use_deform=True,
                  lock_loc=True,  
                  lock_scale=True
                  )
                  
    # costraints
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[distributor_name]

    c = pbone.constraints.new('COPY_ROTATION')
    c.name = 'inherit_rot'
    c.target = rig
    c.subtarget = ik_rot_bone_name
    c.use_x = True
    c.use_y = True
    c.use_z = True
    c.invert_x = False
    c.invert_y = False
    c.invert_z = False
    c.use_offset = True
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = Constants.fixate_ctrl_neck

    c = pbone.constraints.new('COPY_LOCATION')
    c.target = rig
    c.subtarget = ik_loc_bone_name
    c.head_tail = 1
    c.use_x = True
    c.use_y = True
    c.use_z = True
    c.invert_x = False
    c.invert_y = False
    c.invert_z = False
    c.use_offset = False
    c.target_space = 'WORLD'
    c.owner_space = 'WORLD'
    c.influence = 1
                  
    prop_to_drive_constraint(prop_bone_name=distributor_name, 
                             bone_name=distributor_name, 
                             constraint_name='inherit_rot',
                             prop_name='fixate_ctrl_' + neck_name, 
                             attribute='influence', 
                             prop_min=0.0,
                             prop_max=1.0, 
                             prop_default=Constants.fixate_ctrl_neck, 
                             description='', 
                             expression='1-v1'
                             )

    # LOW-LEVEL TO IK RIG constraint
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[neck_name]
    cs = pbone.constraints

    c = cs.new('COPY_ROTATION')
    c.name = 'bind_to_ik_1'
    c.target = rig
    c.subtarget = ik_prefix + neck_name
    c.mute = True

    # BIND TO (0: FK, 1: IK, 2:BIND)
    prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                             bone_name=neck_name, 
                             constraint_name='bind_to_fk_1',
                             prop_name='switch_' + module, 
                             attribute='mute', 
                             prop_min=0, 
                             prop_max=2,
                             prop_default=0, 
                             description='0:fk, 1:ctrl, 2:base', 
                             expression='1 - (v1 < 1)'
                             )
    prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                             bone_name=neck_name, 
                             constraint_name='bind_to_ik_1',
                             prop_name='switch_' + module, 
                             attribute='mute', 
                             prop_min=0, 
                             prop_max=2,
                             prop_default=0, 
                             description='0:fk, 1:ctrl, 2:base',
                             expression='1 - (v1 > 0 and v1 < 2)'
                             )

    relevant_bone_names.append(Constants.ctrl_prefix + neck_name)

    bone_visibility(prop_bone_name=prop_bone_name, 
                    module=module, 
                    relevant_bone_names=relevant_bone_names, 
                    ik_ctrl='ctrl'
                    )

    # set module name on relevant bones (used by the 'N-panel' interface)
    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )

    # snap_info
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbone = pbones[prop_bone_name]
    si = 'snapinfo_simpletobase_0'
    if si in pbone:
        pbone[si] = pbone[si] + [neck_name]
