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
from .utils import set_bone_shape


def fingers(bvh_tree, shape_collection, module, finger_names, side):
    
    rig = bpy.context.object
    
    fk_prefix = Constants.fk_prefix
    ik_prefix = Constants.ik_prefix
    ctrl_prefix = Constants.ctrl_prefix
    
    bend_axis = '-X'
    
    ik_group = get_ik_group_name(side)

    # bones that should be used for animation
    relevant_bone_names = []

    # bone that holds all properties of the module
    prop_bone_name = create_module_prop_bone(module=module)

    # set parent
    first_parent_name = get_parent_name(finger_names[0] + '_1' + side)

    # BASE
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    for finger in finger_names:
        for n in range(1, 4):
            name = finger + '_' + str(n) + side
            ebone = ebones[name]
            if n == 1:
                ebone.parent = ebones[first_parent_name]
            else:
                ebone.parent = ebones[finger + '_' + str(n - 1) + side]
    for finger in finger_names:
        for n in range(1, 4):
            name = finger + '_' + str(n) + side
            bone_settings(bone_name=name, 
                          layer_index=Constants.base_layer, 
                          group_name=Constants.base_group, 
                          use_deform=True, 
                          lock_loc=True, 
                          lock_scale=True,
                          bone_type=Constants.base_type
                          )
            relevant_bone_names.append(name)

    def create_finger_bones(prefix, set_shape, layer, group, constraint_name, type):
        bpy.ops.object.mode_set(mode='EDIT')
        for finger in finger_names:
            for n in range(1, 4):
                name = prefix + finger + '_' + str(n) + side
                source_name = finger + '_' + str(n) + side
                
                duplicate_bone(source_name=source_name, 
                               new_name=name, 
                               parent_name=first_parent_name if n == 1 else prefix + finger + '_' + str(n - 1) + side,
                               )
        for finger in finger_names:
            for n in range(1, 4):
                name = prefix + finger + '_' + str(n) + side
                bone_settings(bone_name=name, 
                              layer_index=layer, 
                              group_name=group, 
                              lock_loc=True, 
                              lock_scale=True,
                              bone_type=type
                              )
                if set_shape:
                    set_bone_shape(shape_collection=shape_collection,
                                   bone_name=name,
                                   bone_shape_name='sphere',
                                   bone_shape_scale=Constants.finger_shape_size
                                   )
                relevant_bone_names.append(name)

        # BIND RIG TO FK RIG constraints
        bpy.ops.object.mode_set(mode='POSE')
        pbones = rig.pose.bones

        for finger in finger_names:
            for n in range(1, 4):
                name = finger + '_' + str(n) + side
                c = pbones[name].constraints.new('COPY_ROTATION')
                c.name = constraint_name
                c.target = rig
                c.subtarget = prefix + name
                c.mute = True

    # FK
    create_finger_bones(prefix=fk_prefix, 
                        set_shape=True, 
                        layer=Constants.fk_layer, 
                        group=Constants.fk_group,
                        constraint_name='bind_to_fk_1', 
                        type=Constants.fk_type
                        )

    # IK
    create_finger_bones(prefix=ik_prefix, 
                        set_shape=False, 
                        layer=Constants.ctrl_ik_extra_layer, 
                        group='',
                        constraint_name='bind_to_ik_1', 
                        type=''
                        )

    # finger ctrl bones
    for index, finger in enumerate(finger_names):
        ctrl_name = ctrl_prefix + finger + side
        if index == 0:
            source_name = ik_prefix + finger + '_2' + side
        else:
            source_name = ik_prefix + finger + '_1' + side
    
        duplicate_bone(source_name=source_name, 
                       new_name=ctrl_name, 
                       parent_name=first_parent_name,
                       )
        bone_settings(shape_collection=shape_collection,
                      bone_name=ctrl_name, 
                      layer_index=Constants.ctrl_ik_layer, 
                      group_name=ik_group,
                      lock_loc=index != 0,
                      lock_scale=(True, False, True),
                      bone_shape_name='cube', 
                      bone_shape_pos='HEAD', 
                      bone_shape_manual_scale=Constants.finger_shape_size,
                      bone_type=Constants.ctrl_type
                      )
        relevant_bone_names.append(ctrl_name)

    # constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    for index, finger in enumerate(finger_names):

        # constraint ik finger bones to finger ctrl bones
        if index == 0:
            name = ik_prefix + finger + '_2' + side
        else:
            name = ik_prefix + finger + '_1' + side
        pbone = pbones[name]
        c = pbone.constraints.new('COPY_ROTATION')
        c.name = 'copy ctrl finger'
        c.target = rig
        c.subtarget = 'ctrl_' + finger + side
        c.use_x = True
        c.use_y = True
        c.use_z = True
        c.invert_x = False
        c.invert_y = False
        c.invert_z = False
        c.use_offset = False
        c.target_space = 'LOCAL'
        c.owner_space = 'LOCAL'
        c.influence = 1

        # ctrl finger scale to finger rot
        def add_c(pbone, scale_fwd, rot_fwd, scale_bwd, rot_bwd):
            c = pbone.constraints.new('TRANSFORM')
            c.name = 'ctrl finger scale to bend fwd'
            c.use_motion_extrapolate = False
            c.target = rig
            c.subtarget = 'ctrl_' + finger + side
            c.map_from = 'SCALE'
            c.map_to = 'ROTATION'
            c.map_to_x_from = 'Y'
            c.map_to_y_from = 'Y'
            c.map_to_z_from = 'Y'
            c.from_min_x_scale = 1
            c.from_max_x_scale = 1
            c.from_min_y_scale = scale_fwd
            c.from_max_y_scale = 1
            c.from_min_z_scale = 1
            c.from_max_z_scale = 1

            if bend_axis == '-X':
                c.to_min_x_rot = radians(rot_fwd)
                c.to_max_x_rot = 0

            c.target_space = 'LOCAL'
            c.owner_space = 'LOCAL'
            c.influence = 1

            c = pbone.constraints.new('TRANSFORM')
            c.name = 'ctrl finger scale to bend bwd'
            c.use_motion_extrapolate = False
            c.target = rig
            c.subtarget = 'ctrl_' + finger + side
            c.map_from = 'SCALE'
            c.map_to = 'ROTATION'
            c.map_to_x_from = 'Y'
            c.map_to_y_from = 'Y'
            c.map_to_z_from = 'Y'
            c.from_min_x_scale = 1
            c.from_max_x_scale = 1
            c.from_min_y_scale = 1
            c.from_max_y_scale = scale_bwd
            c.from_min_z_scale = 1
            c.from_max_z_scale = 1

            if bend_axis == '-X':
                c.to_min_x_rot = 0
                c.to_max_x_rot = radians(rot_bwd)

            c.target_space = 'LOCAL'
            c.owner_space = 'LOCAL'
            c.influence = 1

        if index == 0:
            add_c(pbone=pbones[ik_prefix + finger + '_3' + side], 
                  scale_fwd=Constants.ctrl_finger_scale__to_finger_2_3_bend_fwd__scale,
                  rot_fwd=Constants.ctrl_finger_scale__to_thumb_2_bend_fwd__rot,
                  scale_bwd=Constants.ctrl_finger_scale__to_finger_2_3_bend_bwd__scale,
                  rot_bwd=Constants.ctrl_finger_scale__to_thumb_2_bend_bwd__rot
                  )

            pbone = pbones[ik_prefix + finger + '_1' + side]
            c = pbone.constraints.new('DAMPED_TRACK')
            c.name = 'track to ctrl_finger.head'
            c.target = rig
            c.subtarget = 'ctrl_' + finger + side
            c.head_tail = 0
            c.track_axis = 'TRACK_Y'
            c.influence = 1

        else:
            for n in range(2, 4):
                add_c(pbone=pbones[ik_prefix + finger + '_' + str(n) + side], 
                      scale_fwd=Constants.ctrl_finger_scale__to_finger_2_3_bend_fwd__scale,
                      rot_fwd=Constants.ctrl_finger_scale__to_finger_2_3_bend_fwd__rot,
                      scale_bwd=Constants.ctrl_finger_scale__to_finger_2_3_bend_bwd__scale,
                      rot_bwd=Constants.ctrl_finger_scale__to_finger_2_3_bend_bwd__rot
                      )

        # limit ctrl finger bone scale
        pbone = pbones['ctrl_' + finger + side]
        c = pbone.constraints.new('LIMIT_SCALE')
        c.name = 'limit scale'
        c.owner_space = 'LOCAL'
        c.influence = 1
        c.use_transform_limit = True
        c.use_min_x = True
        c.use_min_y = True
        c.use_min_z = True
        c.use_max_x = True
        c.use_max_y = True
        c.use_max_z = True
        c.min_x = 1
        c.max_x = 1
        c.min_y = Constants.ctrl_finger_scale__to_finger_2_3_bend_fwd__scale
        c.max_y = Constants.ctrl_finger_scale__to_finger_2_3_bend_bwd__scale
        c.min_z = 1
        c.max_z = 1

    # BIND RIG TO (0:fk, 1:ik, 2:bind)
    for finger in finger_names:
        for n in range(1, 4):
            name = finger + '_' + str(n) + side
            prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                                     bone_name=name, 
                                     constraint_name='bind_to_fk_1',
                                     prop_name='switch_' + module, 
                                     attribute='mute', 
                                     prop_min=0,
                                     prop_max=2, 
                                     prop_default=0, 
                                     description='0:fk, 1:ctrl, 2:bind',
                                     expression='1 - (v1 < 1)'
                                     )
            prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                                     bone_name=name, 
                                     constraint_name='bind_to_ik_1',
                                     prop_name='switch_' + module, 
                                     attribute='mute', 
                                     prop_min=0,
                                     prop_max=2, 
                                     prop_default=0, 
                                     description='0:fk, 1:ctrl, 2:bind',
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
