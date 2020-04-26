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
from .utils import create_module_prop_bone
from .utils import bone_settings
from .utils import duplicate_bone
from .utils import get_distance
from .utils import prop_to_drive_constraint
from .utils import mirror_bone_to_point
from .utils import bone_visibility
from .utils import set_module_on_relevant_bones
from .utils import three_bone_limb
from .utils import get_parent_name
from .utils import create_no_twist_bone
from .utils import set_bone_only_layer
from .utils import set_bone_shape


def face_base(bvh_tree, shape_collection, module, use_jaw, parent_name):
    
    rig = bpy.context.object
    
    sides = Constants.sides
    
    prop_bone_name = create_module_prop_bone(module)
    relevant_bone_names = []

    # create face parent bone
    duplicate_bone(source_name='head', 
                   new_name='face_parent', 
                   parent_name=parent_name, 
                   half_long=True
                   )

    first_parent_name = parent_name
    parent_name = 'face_parent'

    # create look target bones
    bpy.ops.object.mode_set(mode='EDIT')
    # eye_targets
    for side in sides:
        ebone = rig.data.edit_bones.new(name='target_eye' + side)
        ebone.head = rig.data.edit_bones['eye' + side].head + Vector((0, -Constants.look_target_offset, 0))
        ebone.tail = rig.data.edit_bones['eye' + side].tail + Vector((0, -Constants.look_target_offset, 0))
        ebone.roll = 0
    # look bone
    look = 'target_look'
    ebone = rig.data.edit_bones.new(name=look)
    ebones = rig.data.edit_bones
    ebone.head = (ebones['target_eye' + sides[0]].head + ebones['target_eye' + sides[1]].head) * .5
    ebone.tail = ebone.head + Vector((0, 0, Constants.general_bone_size))
    ebone.roll = 0
    ebone.parent = ebones[parent_name]
    # parent eye targets to look bone
    for side in sides:
        ebones['target_eye' + side].parent = ebones[look]

    # name, parent, deform, lock location, lock rotation, shape
    bone_table = [
        ['face_parent', first_parent_name, False, True, True, None, '', Constants.face_shape_size, Constants.face_group, ''],
        ['eye_l', parent_name, True, True, False, 'sphere', 'REVERSE_RAYCAST', Constants.face_shape_size, Constants.face_group, ''],
        ['eye_r', parent_name, True, True, False, 'sphere', 'REVERSE_RAYCAST', Constants.face_shape_size, Constants.face_group, ''],
        ['upperlid_l', parent_name, True, True, False, 'small_cube_r', 'REVERSE_RAYCAST', Constants.face_shape_size, Constants.face_group, 'head'],
        ['upperlid_r', parent_name, True, True, False, 'small_cube_r', 'REVERSE_RAYCAST', Constants.face_shape_size, Constants.face_group, 'head'],
        ['lowerlid_l', parent_name, True, True, False, 'small_cube_l', 'REVERSE_RAYCAST', Constants.face_shape_size, Constants.face_group, 'head'],
        ['lowerlid_r', parent_name, True, True, False, 'small_cube_l', 'REVERSE_RAYCAST', Constants.face_shape_size, Constants.face_group, 'head'],
        [look, parent_name, False, False, True, 'eye_target', '', Constants.look_target_size, Constants.target_group, ''],
        ['target_eye_l', look, False, False, False, None, '', Constants.face_shape_size, Constants.face_group, ''],
        ['target_eye_r', look, False, False, False, None, '', Constants.face_shape_size, Constants.face_group, '']
    ]

    extra_bones = ['target_eye_l', 'target_eye_r', 'face_parent']
    shape_bone_layer = []

    if use_jaw == True:
        bone_table_jaw = [
            ['jaw', parent_name, True, True, False, 'brick2', 'chin', Constants.face_shape_size, Constants.face_group, ''],
            ['teeth_lower', parent_name, True, True, False, None, '', Constants.face_shape_size, Constants.face_group, ''],
            ['chin', 'jaw', False, True, True, None, '', Constants.face_shape_size, Constants.face_group, '']
        ]
        bone_table += bone_table_jaw
        extra_bones.append('teeth_lower')
        shape_bone_layer.append('chin')

    for name, bone_parent, use_deform, lock_loc, lock_rot, bone_shape, transform_bone_name, scale, group, shape_parent_override in bone_table:
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        ebones[name].parent = ebones[bone_parent]
        ebones[name].roll = 0
            
        bone_settings(bone_name=name, 
                      layer_index=Constants.face_layer, 
                      group_name=group, 
                      use_deform=use_deform, 
                      lock_loc=lock_loc, 
                      lock_rot=lock_rot, 
                      lock_scale=True,
                      bone_type=Constants.face_type
                      )
        if bone_shape is not None:
            set_bone_shape(shape_collection=shape_collection, 
                           bone_name=name, 
                           bone_shape_name=bone_shape, 
                           bone_shape_scale=scale, 
                           transform_bone_name=transform_bone_name,
                           transform_bone_parent_override=shape_parent_override,
                           bvh_tree=bvh_tree
                           )
        if name in extra_bones:
            set_bone_only_layer(bone_name=name, 
                                layer_index=Constants.face_extra_layer
                                )

        if name in shape_bone_layer:
            set_bone_only_layer(bone_name=name, 
                    layer_index=30
                    )

        relevant_bone_names.append(name)

    # eye no twist
    for side in sides:
        create_no_twist_bone(source_bone_name='eye' + side)

    # constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones

    if use_jaw == True:
        c = pbones['teeth_lower'].constraints.new('COPY_ROTATION')
        c.name = 'Copy Jaw'
        c.target = rig
        c.subtarget = 'jaw'
        c.influence = Constants.teeth_lower_copy_jaw_rot

        prop_to_drive_constraint(prop_bone_name='jaw', 
                                 bone_name='teeth_lower', 
                                 constraint_name='Copy Jaw',
                                 prop_name='teeth_lower_follow_jaw', 
                                 attribute='influence',
                                 prop_min=0.0, 
                                 prop_max=1.0, 
                                 prop_default=Constants.teeth_lower_copy_jaw_rot,
                                 description='', 
                                 expression='v1'
                                 )

    # eye constraints
    for side in sides:
        c = pbones['eye' + side].constraints.new('TRACK_TO')
        c.name = 'Eye Target'
        c.target = rig
        c.subtarget = 'target_eye' + side
        c.track_axis = 'TRACK_Z'
        c.up_axis = 'UP_Y'
        c.mute = True

        c = pbones['upperlid' + side].constraints.new('COPY_ROTATION')
        c.name = 'Copy Eye'
        c.target = rig
        c.subtarget = 'no_twist_eye' + side
        c.influence = Constants.upperlid_copy_eye_rot

        c = pbones['lowerlid' + side].constraints.new('COPY_ROTATION')
        c.name = 'Copy Eye'
        c.target = rig
        c.subtarget = 'no_twist_eye' + side
        c.influence = Constants.lowerlid_copy_eye_rot

        prop_to_drive_constraint(prop_bone_name=look, 
                                 bone_name='eye' + side, 
                                 constraint_name='Eye Target',
                                 prop_name='active_look_target', 
                                 attribute='mute', 
                                 prop_min=0,
                                 prop_max=1, 
                                 prop_default=0, 
                                 description='', 
                                 expression='1-v1'
                                 )
        prop_to_drive_constraint(prop_bone_name='upperlid' + side, 
                                 bone_name='upperlid' + side,
                                 constraint_name='Copy Eye', 
                                 prop_name='upperlid_follow_eye',
                                 attribute='influence', 
                                 prop_min=0.0, 
                                 prop_max=1.0,
                                 prop_default=Constants.upperlid_copy_eye_rot, 
                                 description='', 
                                 expression='v1'
                                 )
        prop_to_drive_constraint(prop_bone_name='lowerlid' + side, 
                                 bone_name='lowerlid' + side,
                                 constraint_name='Copy Eye', 
                                 prop_name='lowerlid_follow_eye',
                                 attribute='influence', 
                                 prop_min=0.0, 
                                 prop_max=1.0,
                                 prop_default=Constants.lowerlid_copy_eye_rot, 
                                 description='', 
                                 expression='v1'
                                 )

    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )


def face_detail(bvh_tree, shape_collection, module):
    
    rig = bpy.context.object

    prop_bone_name = create_module_prop_bone(module)
    relevant_bone_names = []

    # set parent
    parent_name = "face_parent"

    # create lowerlip parent bone
    duplicate_bone(source_name='jaw', 
                   new_name='lowerlip', 
                   parent_name=parent_name, 
                   half_long=True
                   )

    # name, parent, deform, lock location, lock rotation
    bone_table = [
        ['innerbrow_l', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['innerbrow_r', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['outerbrow_l', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['outerbrow_r', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['cheek_l', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['cheek_r', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['nostril_l', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['nostril_r', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['upperlip_l', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['upperlip_r', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['upperlip_m', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['mouth_corner_l', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['mouth_corner_r', parent_name, True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['lowerlip', parent_name, False, True, False, None, 'REVERSE_RAYCAST'],
        ['lowerlip_l', 'lowerlip', True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['lowerlip_r', 'lowerlip', True, False, False, 'sphere', 'REVERSE_RAYCAST'],
        ['tongue_back', 'teeth_lower', True, True, False, 'sphere', ''],
        ['tongue_tip', 'tongue_back', True, True, False, 'sphere', '']
    ]

    extra_bones = ['lowerlip']

    for name, bone_parent, use_deform, lock_loc, lock_rot, bone_shape, shape_transform_bone_name in bone_table:
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        ebones[name].parent = ebones[bone_parent]
        ebones[name].roll = 0
        
        bone_settings(bone_name=name, 
                      layer_index=Constants.face_layer, 
                      group_name=Constants.face_group, 
                      use_deform=use_deform, 
                      lock_loc=lock_loc, 
                      lock_rot=lock_rot, 
                      lock_scale=True, 
                      bone_type=Constants.face_type
                      )

        if bone_shape != None:
            set_bone_shape(shape_collection=shape_collection, 
                           bone_name=name, 
                           bone_shape_name=bone_shape, 
                           bone_shape_scale=Constants.face_shape_size, 
                           transform_bone_name=shape_transform_bone_name, 
                           bvh_tree=bvh_tree
                           )

        if name in extra_bones:
            set_bone_only_layer(bone_name=name, 
                                layer_index=Constants.face_extra_layer
                                )

        relevant_bone_names.append(name)

    # constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones

    c = pbones['lowerlip'].constraints.new('COPY_ROTATION')
    c.name = 'Copy Jaw'
    c.target = rig
    c.subtarget = 'jaw'
    c.influence = Constants.lowerlip_copy_jaw_rot

    prop_to_drive_constraint(prop_bone_name='jaw', 
                             bone_name='lowerlip', 
                             constraint_name='Copy Jaw',
                             prop_name='lowerlip_follow_jaw', 
                             attribute='influence', 
                             prop_min=0.0,
                             prop_max=1.0, 
                             prop_default=Constants.lowerlip_copy_jaw_rot, 
                             description='',
                             expression='v1'
                             )

    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )
