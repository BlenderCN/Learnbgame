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
from math import radians

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


def biped_torso(bvh_tree, shape_collection, module, chain, first_parent_name):

    # chain length should be exactly 4
    
    fk_prefix = Constants.fk_prefix
    ik_prefix = Constants.ik_prefix
    rig = bpy.context.object
    
    # bones that should be used for animation
    relevant_bone_names = []

    # bone that holds all properties of the module
    prop_bone_name = create_module_prop_bone(module=module)

    # LOW-LEVEL BONES
    set_parent_chain(bone_names=chain, 
                     first_parent_name=first_parent_name
                     )

    # format bones
    for index, name in enumerate(chain):            
        bone_settings(bone_name=name, 
                      layer_index=Constants.base_layer, 
                      group_name=Constants.base_group, 
                      use_deform=True, 
                      lock_loc=index != 0, 
                      lock_scale=True,
                      bone_type=Constants.base_type
                      )    
        relevant_bone_names.append(name)

    # FK BONES
    for index, name in enumerate(chain):
        if index == 0:
            lock_loc = False
            parent_name = first_parent_name
            shape_name = 'torso_2'
            shape_up = True
        else:
            lock_loc = True
            parent_name = fk_prefix + chain[index - 1]
            shape_name = 'inner_circle'
            shape_up = False
            
        duplicate_bone(source_name=name, 
                       new_name=fk_prefix + name, 
                       parent_name=parent_name
                       )            
        bone_settings(bvh_tree=bvh_tree, 
                      shape_collection=shape_collection, 
                      bone_name=fk_prefix + name, 
                      layer_index=Constants.fk_layer, 
                      group_name=Constants.fk_group, 
                      lock_loc=lock_loc, 
                      lock_scale=True,  
                      bone_shape_name=shape_name, 
                      bone_shape_pos='HEAD',  
                      bone_shape_up=shape_up,
                      bone_type=''
                      )
        relevant_bone_names.append(fk_prefix + name)

    # LOW-LEVEL TO FK RIG CONSTRAINTS
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    for index, name in enumerate(chain):
        pbone = pbones[name]
        cs = pbone.constraints

        c = cs.new('COPY_ROTATION')
        c.name = 'bind_to_fk_1'
        c.target = rig
        c.subtarget = fk_prefix + name
        c.mute = True

        if index == 0:
            c = cs.new('COPY_LOCATION')
            c.name = 'bind_to_fk_2'
            c.target = rig
            c.subtarget = fk_prefix + name
            c.head_tail = 0
            c.mute = True

    # IK BONES
    # create torso bone
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ctrl_torso = 'ctrl_torso'
    ebone = ebones.new(name=ctrl_torso)
    ebone.head = ebones[chain[0]].tail

    # get hips length
    length = get_distance(ebones[chain[0]].head, ebones[chain[0]].tail)

    ebone.tail = ebone.head + Vector((0, length, 0))
    ebone.parent = ebones[first_parent_name]

    # format torso bone
    bone_settings(bvh_tree=bvh_tree,
                  shape_collection=shape_collection,
                  bone_name=ctrl_torso, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=Constants.central_ik_group, 
                  lock_scale=True,
                  bone_shape_name='torso',
                  bone_shape_pos='HEAD',
                  bone_shape_up=True,
                  bone_shape_up_only_for_ray_casting=True,
                  bone_type=Constants.ctrl_type
                  )

    relevant_bone_names.append(ctrl_torso)
    
    # create control bones
    def spine_control(ctrl_name, length_multiplier, parent_name, is_on_extra_layer, group, use_custom_shape, bone_shape_bone):
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        ctrl_spine_name = 'ctrl_' + ctrl_name
        ebone = ebones.new(name=ctrl_spine_name)
        ebone.head = ebones[chain[0]].tail
        ebone.tail = ebone.head + Vector((0, 0, length * length_multiplier))
        ebone.parent = ebones[parent_name]
        
        bone_settings(bvh_tree=bvh_tree,
                      shape_collection=shape_collection,
                      bone_name=ctrl_spine_name, 
                      layer_index=Constants.ctrl_ik_extra_layer if is_on_extra_layer else Constants.ctrl_ik_layer, 
                      group_name=group,  
                      lock_loc=True,  
                      lock_scale=True,
                      bone_shape_name='inner_circle' if use_custom_shape else '',
                      bone_shape_pos='HEAD',
                      bone_shape_bone=bone_shape_bone,
                      bone_type=Constants.ctrl_type
                      )
        return (ctrl_spine_name)

    ctrl_hips = spine_control(ctrl_name='hips', 
                              length_multiplier=1, 
                              parent_name=ctrl_torso, 
                              is_on_extra_layer=False, 
                              group=Constants.central_ik_group,
                              use_custom_shape=True,
                              bone_shape_bone=chain[1]
                              )
    ctrl_waist_parent = spine_control(ctrl_name='waist_parent', 
                                      length_multiplier=2.5, 
                                      parent_name=ctrl_hips, 
                                      is_on_extra_layer=True, 
                                      group='',
                                      use_custom_shape=False,
                                      bone_shape_bone=''
                                      )
    ctrl_waist = spine_control(ctrl_name='waist', 
                               length_multiplier=2, 
                               parent_name=ctrl_waist_parent, 
                               is_on_extra_layer=False, 
                               group=Constants.central_ik_group,
                               use_custom_shape=True,
                               bone_shape_bone=chain[2]
                               )
    ctrl_chest = spine_control(ctrl_name='chest', 
                               length_multiplier=3, 
                               parent_name=ctrl_torso, 
                               is_on_extra_layer=False, 
                               group=Constants.central_ik_group,
                               use_custom_shape=True,
                               bone_shape_bone=chain[3]
                               )

    relevant_bone_names.append(ctrl_hips)
    relevant_bone_names.append(ctrl_waist)
    relevant_bone_names.append(ctrl_chest)

    # ctrl_waist_parent constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[ctrl_waist_parent]
    cs = pbone.constraints

    # constraints
    c = cs.new('COPY_ROTATION')
    c.name = 'copy ' + ctrl_chest
    c.target = rig
    c.subtarget = ctrl_chest
    c.influence = Constants.ctrl_waist__copy__ctrl_chest

    prop_to_drive_constraint(prop_bone_name=ctrl_waist, 
                             bone_name=ctrl_waist_parent, 
                             constraint_name=c.name,
                             prop_name='ctrl_waist_copy_chest', 
                             attribute='influence', 
                             prop_min=0.0,
                             prop_max=1.0, 
                             prop_default=Constants.ctrl_waist__copy__ctrl_chest, 
                             description='',
                             expression='v1'
                             )

    c = cs.new('COPY_ROTATION')
    c.name = 'copy ' + ctrl_hips
    c.target = rig
    c.subtarget = ctrl_hips
    c.influence = Constants.ctrl_waist__copy__ctrl_hips

    prop_to_drive_constraint(prop_bone_name=ctrl_waist,
                             bone_name=ctrl_waist_parent, 
                             constraint_name=c.name,
                             prop_name='ctrl_waist_copy_hips', 
                             attribute='influence', 
                             prop_min=0.0,
                             prop_max=1.0, 
                             prop_default=Constants.ctrl_waist__copy__ctrl_hips, 
                             description='',
                             expression='v1'
                             )

    for index, name in enumerate(chain):
        # create distributor bone
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        dist_bone_name = ik_prefix + name + '_dist'
        ebone = ebones.new(name=dist_bone_name)
        ebone.head = ebones[name].head
        ebone.tail = ebone.head + Vector((0, 0, length / 2))
        if index == 0:
            parent_name = ctrl_torso
        else:
            parent_name = ik_prefix + 'fwd_' + chain[index - 1]
        ebone.parent = ebones[parent_name]

        # format distributor bone
        bone_settings(bone_name=dist_bone_name, 
                      layer_index=Constants.ctrl_ik_extra_layer,  
                      lock_loc=True,  
                      lock_scale=True
                      )

        # create ik fwd bone
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        ik_bone_name = ik_prefix + 'fwd_' + name
        
        duplicate_bone(source_name=name, 
                       new_name=ik_bone_name, 
                       parent_name=dist_bone_name,
                       roll=ebones[name].roll + radians(180) if index == 0 else 'SOURCE_ROLL'
                       )
                       
        # format ik bone
        bone_settings(bone_name=ik_bone_name, 
                      layer_index=Constants.ctrl_ik_extra_layer,  
                      lock_loc=True,  
                      lock_scale=True
                      )

    # reverse hips
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ik_hips_name = ik_prefix + 'fwd_' + chain[0]
    ebones[ik_hips_name].head = ebones[chain[0]].tail
    ebones[ik_hips_name].tail = ebones[chain[0]].head
    # adjust hips distributor
    ik_hips_distributor_name = ik_prefix + chain[0] + '_dist'
    ebones[ik_hips_distributor_name].head = ebones[chain[0]].tail
    ebones[ik_hips_distributor_name].tail = ebones[ik_hips_distributor_name].head + Vector((0, 0, length / 3))
    # reset parents
    ebones[ik_hips_distributor_name].parent = ebones[ctrl_torso]
    ebones[ik_prefix + chain[1] + '_dist'].parent = ebones[ctrl_torso]

    # distributor constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones

    def simple_spine_constraint(chain_index, ctrl_bone_name):
        pbone = pbones[ik_prefix + chain[chain_index] + '_dist']
        cs = pbone.constraints
        c = cs.new('COPY_ROTATION')
        c.name = 'copy ' + ctrl_bone_name
        c.target = rig
        c.subtarget = ctrl_bone_name
        c.influence = 1

    # 0, 1, 3
    simple_spine_constraint(0, ctrl_hips)
    simple_spine_constraint(1, ctrl_waist)
    simple_spine_constraint(3, ctrl_chest)

    # 2
    pbone = pbones[ik_prefix + chain[2] + '_dist']
    cs = pbone.constraints

    c = cs.new('COPY_ROTATION')
    c.name = 'copy ' + ctrl_waist
    c.target = rig
    c.subtarget = ctrl_waist
    c.influence = Constants.ik_spine_2__copy__ctrl_waist

    prop_to_drive_constraint (prop_bone_name=ctrl_waist, 
                              bone_name=pbone.name, 
                              constraint_name=c.name, 
                              prop_name='ctrl_spine_2_copy_waist', 
                              attribute='influence', 
                              prop_min=0.0, 
                              prop_max=1.0, 
                              prop_default=Constants.ik_spine_2__copy__ctrl_waist, 
                              description='', 
                              expression='v1'
                              )

    c = cs.new('COPY_ROTATION')
    c.name = 'copy ' + ctrl_chest
    c.target = rig
    c.subtarget = ctrl_chest
    c.influence = Constants.ik_spine_2__copy__ctrl_waist

    prop_to_drive_constraint(prop_bone_name=ctrl_chest, 
                             bone_name=pbone.name, 
                             constraint_name=c.name,
                             prop_name='ctrl_spine_2_copy_chest', 
                             attribute='influence', 
                             prop_min=0.0,
                             prop_max=1.0, 
                             prop_default=Constants.ik_spine_2__copy__ctrl_waist, 
                             description='',
                             expression='v1'
                             )

    # create ik bones (that will slide on reverse bones)
    for index, name in enumerate(chain):
        if index == 0:
            parent_name = ctrl_torso
        else:
            parent_name = ik_prefix + chain[index - 1]
        
        duplicate_bone(source_name=name, 
                       new_name=ik_prefix + name, 
                       parent_name=parent_name
                       )
        bone_settings(bone_name=ik_prefix + name, 
                      layer_index=Constants.ctrl_ik_extra_layer, 
                      lock_loc=True, 
                      lock_scale=True
                      )

        if index != 0:
            # constrain it to ik_fwd bones
            bpy.ops.object.mode_set(mode='POSE')
            bone_name = ik_prefix + name
            pbone = rig.pose.bones[bone_name]
            cs = pbone.constraints

            c = cs.new('COPY_ROTATION')
            c.target = rig
            c.subtarget = ik_prefix + 'fwd_' + name

    # reverse hips
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ik_hips_name = ik_prefix + chain[0]
    ebones[ik_hips_name].head = ebones[chain[0]].tail
    ebones[ik_hips_name].tail = ebones[chain[0]].head
    ebones[ik_hips_name].roll = 0 + radians(180)
    ebones[ik_prefix + chain[1]].parent = None
    ebones[ik_hips_name].parent = ebones[ik_prefix + chain[1]]
    ebones[ik_prefix + chain[1]].parent = ebones[ctrl_torso]

    # ik_hips copies ik_fwd_hips' rot
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[ik_hips_name]
    cs = pbone.constraints

    c = cs.new('COPY_ROTATION')
    c.target = rig
    c.subtarget = ik_prefix + 'fwd_' + chain[0]

    # PIVOT SLIDER
    # reverse spine chain from above hips
    for index, name in enumerate(chain):
        if index > 0:
            parent_name = ik_prefix + 'fwd_' + name
            rev_bone_name = ik_prefix + 'rev_' + name
            
            duplicate_bone(source_name=name, 
                           new_name=rev_bone_name, 
                           parent_name=parent_name
                           )
            mirror_bone_to_point(bone_name=rev_bone_name, 
                                 point=ebones[ctrl_torso].head
                                 )       
            bone_settings(bone_name=rev_bone_name, 
                          layer_index=Constants.ctrl_ik_extra_layer, 
                          lock_loc=True, 
                          lock_scale=True
                          )

            # stick rev bones together
            if index > 1:
                bpy.ops.object.mode_set(mode='POSE')
                pbone = rig.pose.bones[rev_bone_name]
                cs = pbone.constraints
                c = cs.new('COPY_LOCATION')
                c.target = rig
                c.subtarget = ik_prefix + 'rev_' + chain[index - 1]
                c.head_tail = 1

    # constraints
    bpy.ops.object.mode_set(mode='POSE')
    bone_name = ik_prefix + chain[1]
    pbone = rig.pose.bones[bone_name]
    cs = pbone.constraints

    for index, name in enumerate(chain):
        if index > 0:
            c = cs.new('COPY_LOCATION')
            c.name = 'pivot_slide_' + str(index)
            c.target = rig
            c.subtarget = ik_prefix + 'rev_' + name
            c.head_tail = 1
            c.influence = 0

            # constraint driven by prop
            prop_to_drive_constraint(prop_bone_name=ctrl_torso, 
                                     bone_name=bone_name, 
                                     constraint_name=c.name,
                                     prop_name='ctrl_spine_pivot_slide', 
                                     attribute='influence',
                                     prop_min=0.25, 
                                     prop_max=1.0, 
                                     prop_default=0.25, 
                                     description='',
                                     expression='(v1 - 0.25 * ' + str(index) + ') * 4'
                                     )
                                     
    # ctrl bone shape transform
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbones[ctrl_hips].custom_shape_transform = pbones[ik_prefix + chain[1]]                 
    pbones[ctrl_waist].custom_shape_transform = pbones[ik_prefix + chain[2]]                   
    pbones[ctrl_chest].custom_shape_transform = pbones[ik_prefix + chain[3]]  

    # LOW-LEVEL TO IK RIG CONSTRAINTS
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    for index, name in enumerate(chain):
        pbone = pbones[name]
        cs = pbone.constraints
        if index > 0:
            c = cs.new('COPY_ROTATION')
            c.name = 'bind_to_ik_1'
            c.target = rig
            c.subtarget = ik_prefix + name
            c.mute = True

        else:
            c = cs.new('COPY_LOCATION')
            c.name = 'bind_to_ik_2'
            c.target = rig
            c.subtarget = ik_prefix + name
            c.head_tail = 1
            c.mute = True

            c = cs.new('TRACK_TO')
            c.name = 'bind_to_ik_1'
            c.target = rig
            c.subtarget = ik_prefix + name
            c.track_axis = 'TRACK_Y'
            c.head_tail = 0
            c.use_target_z = True
            c.mute = True

    # BIND TO (0: FK, 1: IK, 2:BIND)
    for index, name in enumerate(chain):
        constraint_count = 2 if index == 0 else 1
        for n in range(1, constraint_count + 1):
            n = str(n)
            prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                                     bone_name=chain[index], 
                                     constraint_name='bind_to_fk_' + n,
                                     prop_name='switch_' + module, attribute='mute', 
                                     prop_min=0, 
                                     prop_max=2,
                                     prop_default=0, 
                                     description='0:fk, 1:ctrl, 2:base',
                                     expression='1 - (v1 < 1)'
                                     )
            prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                                     bone_name=chain[index], 
                                     constraint_name='bind_to_ik_' + n,
                                     prop_name='switch_' + module, attribute='mute', 
                                     prop_min=0, 
                                     prop_max=2,
                                     prop_default=0, 
                                     description='0:fk, 1:ctrl, 2:base',
                                     expression='1 - (v1 > 0 and v1 < 2)'
                                     )

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
    pbone['snapinfo_simpletobase_0'] = chain

    pbone['snap_n_key__should_snap'] = 0

    sm = 'snappable_modules'
    if sm in rig.data:
        rig.data[sm] += [module]
    else:
        rig.data[sm] = [module]
