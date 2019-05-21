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
from .utils import bone_settings
from .utils import duplicate_bone
from .utils import create_module_prop_bone
from .utils import set_module_on_relevant_bones
from .utils import create_leaf_bone
from .utils import subdivide_bone
from .utils import rotate_bone_local
from .utils import create_no_twist_bone
from .utils import set_bone_shape


def spring_belly(bvh_tree, shape_collection, module, waist_bone_names, loc_pelvis_front, loc_sternum_lower):
    
    rig = bpy.context.object
    
    # bones that should be used for animation
    relevant_bone_names = []

    # target belly
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebone = ebones.new(name='target_belly')
    ebone.head = (ebones[loc_sternum_lower].head + ebones[loc_pelvis_front].head) * .5
    ebone.tail = (ebone.head - ebones[waist_bone_names[0]].tail) + ebone.head
    ebone.parent = ebones[waist_bone_names[0]]

    # spring belly
    ebone = ebones.new(name='spring_belly')
    ebone.head = ebones[waist_bone_names[0]].tail
    ebone.tail = ebones['target_belly'].head
    ebone.parent = ebones[waist_bone_names[0]]

    belly_bones = subdivide_bone(name='spring_belly', 
                                 number=2, 
                                 number_to_keep=2,
                                 reverse_naming=False, 
                                 prefix='', 
                                 parent_all_to_source=False,
                                 delete_source=True
                                 )
    ebones[belly_bones[0]].name = 'spring_belly'
    ebones[belly_bones[1]].name = 'belly'

    relevant_bone_names.append('spring_belly')

    # waist_mediator
    ebone = rig.data.edit_bones.new(name='waist_mediator')
    ebones = rig.data.edit_bones
    ebone.head = ebones[waist_bone_names[0]].head
    ebone.tail = ebones[waist_bone_names[-1]].tail
    ebone.roll = 0
    ebone.parent = ebones[waist_bone_names[0]]

    # tracker_belly
    ebone = rig.data.edit_bones.new(name='tracker_belly')
    ebones = rig.data.edit_bones
    ebone.head = ebones['spring_belly'].head
    ebone.tail = ebones['belly'].tail
    ebone.parent = ebones[waist_bone_names[0]]

    # constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones

    pbone = pbones['waist_mediator']
    c = pbone.constraints.new('DAMPED_TRACK')
    c.name = 'track to waist_upper.tail'
    c.target = rig
    c.subtarget = waist_bone_names[-1]
    c.head_tail = 1
    c.track_axis = 'TRACK_Y'
    c.influence = 1

    pbone = pbones['target_belly']
    cs = pbone.constraints
    c = cs.new('COPY_LOCATION')
    c.name = 'mean: sternum, hips 1'
    c.target = rig
    c.subtarget = loc_sternum_lower
    c.use_x = True
    c.use_y = True
    c.use_z = True
    c.invert_x = False
    c.invert_y = False
    c.invert_z = False
    c.use_offset = False
    c.head_tail = 0
    c.target_space = 'WORLD'
    c.owner_space = 'WORLD'
    c.influence = 1

    c = cs.new('COPY_LOCATION')
    c.name = 'mean: sternum, hips 2'
    c.target = rig
    c.subtarget = loc_pelvis_front
    c.use_x = True
    c.use_y = True
    c.use_z = True
    c.invert_x = False
    c.invert_y = False
    c.invert_z = False
    c.use_offset = False
    c.head_tail = 0
    c.target_space = 'WORLD'
    c.owner_space = 'WORLD'
    c.influence = 0.5

    pbone = pbones['spring_belly']
    cs = pbone.constraints
    c = cs.new('TRANSFORM')
    c.name = 'waist_lower rot to scale'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = 'waist_mediator'
    c.map_from = 'ROTATION'
    c.map_to = 'SCALE'
    c.map_to_x_from = 'X'
    c.map_to_y_from = 'X'
    c.map_to_z_from = 'X'
    c.from_min_x_rot = 0
    c.from_max_x_rot = radians(Constants.spring_belly__waist_lower_rot_to_scale__waist_lower_rot)
    c.to_min_y_scale = 1
    c.to_max_y_scale = Constants.spring_belly__waist_lower_rot_to_scale__scale
    c.to_min_x_scale = 1
    c.to_max_x_scale = Constants.spring_belly__waist_lower_rot_to_scale__scale
    c.to_min_z_scale = 1
    c.to_max_z_scale = Constants.spring_belly__waist_lower_rot_to_scale__scale
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    c = cs.new('COPY_ROTATION')
    c.name = 'copy tracker_belly'
    c.target = rig
    c.subtarget = 'tracker_belly'
    c.use_x = True
    c.use_y = True
    c.use_z = True
    c.invert_x = False
    c.invert_y = False
    c.invert_z = False
    c.use_offset = True
    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    pbone = pbones['tracker_belly']
    c = pbone.constraints.new('TRACK_TO')
    c.name = 'track to target belly'
    c.target = rig
    c.subtarget = 'target_belly'
    c.head_tail = 0
    c.track_axis = 'TRACK_Y'
    c.up_axis = 'UP_Z'
    c.use_target_z = True
    c.target_space = 'WORLD'
    c.owner_space = 'WORLD'
    c.influence = 1

    pbone = pbones['belly']
    c = pbone.constraints.new('LIMIT_SCALE')
    c.name = 'keep scale 1'
    c.use_min_x = True
    c.use_max_x = True
    c.use_min_y = True
    c.use_max_y = True
    c.use_min_z = True
    c.use_max_z = True
    c.min_x = 1
    c.max_x = 1
    c.min_y = 1
    c.max_y = 1
    c.min_z = 1
    c.max_z = 1
    c.use_transform_limit = True
    c.owner_space = 'POSE'
    c.influence = 1

    # format bones
    bpy.ops.object.mode_set(mode='POSE')
    
    bone_settings(bone_name='spring_belly', 
                  layer_index=Constants.spring_layer, 
                  group_name=Constants.spring_group, 
                  lock_loc=True, 
                  bone_type=Constants.spring_type
                  )
                  
    # shape transform bone
    create_leaf_bone(bone_name='shape_spring_belly', 
                     source_bone_name='belly',
                     parent_name='SOURCE_BONE'
                     )
    bone_settings(bone_name='shape_spring_belly', 
                  layer_index=Constants.misc_layer, 
                  lock_loc=True, 
                  lock_rot=True, 
                  lock_scale=True, 
                  bone_type=Constants.spring_type
                  )
    set_bone_shape(shape_collection=shape_collection,
                   bone_name='spring_belly', 
                   bone_shape_name='sphere',
                   bone_shape_scale=Constants.target_shape_size, 
                   transform_bone_name='shape_spring_belly'
                   ) 
                  
    bone_settings(bone_name='belly', 
                  layer_index=Constants.misc_layer,
                  use_deform=True,
                  lock_loc=True,
                  bone_type=Constants.spring_type
                  )

    for name in [loc_sternum_lower, loc_pelvis_front, 'target_belly', 'waist_mediator', 'tracker_belly']:
        bone_settings(bone_name=name, 
                      layer_index=Constants.misc_layer, 
                      lock_loc=True
                      )
    # set module name on relevant bones (used by the 'N-panel' interface)
    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )


def spring_chest(bvh_tree, shape_collection, module, chest_name, shoulder_name):
    
    rig = bpy.context.object
    
    # bones that should be used for animation
    relevant_bone_names = []

    # bone settings
    name = chest_name
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.spring_layer, 
                  group_name=Constants.spring_group, 
                  use_deform=True,
                  lock_loc=True, 
                  bone_shape_name='sphere', 
                  bone_shape_pos='TAIL',
                  bone_shape_manual_scale=Constants.target_shape_size,
                  bone_type=Constants.spring_type
                  )
    relevant_bone_names.append(chest_name)

    # constraints
    left_suffix = Constants.sides[0]
    side = 'left' if chest_name.endswith(left_suffix) else 'right'

    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbone = pbones[chest_name]
    c = pbone.constraints.new('TRANSFORM')
    c.name = 'move shoulder up'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = shoulder_name
    c.map_from = 'ROTATION'
    c.map_to = 'ROTATION'
    c.map_to_x_from = 'Z'
    c.map_to_y_from = 'Z'
    c.map_to_z_from = 'Z'

    if side == 'left':
        c.from_min_z_rot = 0
        c.from_max_z_rot = radians(Constants.spring_chest__shoulder_up__shoulder_rot)
        c.to_min_x_rot = 0
        c.to_max_x_rot = radians(Constants.spring_chest__shoulder_up__rot)
    else:
        c.from_min_z_rot = radians(Constants.spring_chest__shoulder_up__shoulder_rot) * -1
        c.from_max_z_rot = 0
        c.to_min_x_rot = radians(Constants.spring_chest__shoulder_up__rot)
        c.to_max_x_rot = 0

    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    c = pbone.constraints.new('TRANSFORM')
    c.name = 'move shoulder down'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = shoulder_name
    c.map_from = 'ROTATION'
    c.map_to = 'ROTATION'
    c.map_to_x_from = 'Z'
    c.map_to_y_from = 'Z'
    c.map_to_z_from = 'Z'

    if side == 'left':
        c.from_min_z_rot = radians(Constants.spring_chest__shoulder_down__shoulder_rot)
        c.from_max_z_rot = 0
        c.to_min_x_rot = radians(Constants.spring_chest__shoulder_down__rot)
        c.to_max_x_rot = 0
    else:
        c.from_min_z_rot = 0
        c.from_max_z_rot = radians(Constants.spring_chest__shoulder_down__shoulder_rot) * -1
        c.to_min_x_rot = 0
        c.to_max_x_rot = radians(Constants.spring_chest__shoulder_down__rot)

    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 1

    # set module name on relevant bones (used by the 'N-panel' interface)
    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )


def spring_bottom(bvh_tree, shape_collection, module, source_bone_name, parent_name, side):
    
    source_bone_bend_axis = '-X'
        
    rig = bpy.context.object

    relevant_bone_names = []

    # create spring bottom
    bpy.ops.object.mode_set(mode='EDIT')
    bottom_raw_name = 'bottom_raw' + side 
    duplicate_bone(source_name=source_bone_name,
                   new_name=bottom_raw_name, 
                   parent_name='SOURCE_PARENT',
                   )
    
    # rotate it
    if source_bone_bend_axis == '-X':
        angle = -90
        axis = 'X'

    rotate_bone_local(name=bottom_raw_name, 
                      angle=angle, 
                      axis=axis
                      )

    # set ray start and direction
    ebones = rig.data.edit_bones
    ray_start = ebones[source_bone_name].head
    ray_direction = ebones[bottom_raw_name].tail - ray_start
    bpy.ops.object.mode_set(mode='OBJECT')
    ray_distance = 10

    # cast ray
    hit_loc, hit_nor, hit_index, hit_dist = bvh_tree.ray_cast(ray_start, 
                                                              ray_direction, 
                                                              ray_distance
                                                              )

    # adjust tail
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebone = ebones[bottom_raw_name]
    ebone.tail = hit_loc
    ebone.parent = ebones[parent_name]
    # subdivide it
    bottom_bones = subdivide_bone(name=bottom_raw_name, 
                                  number=2, 
                                  number_to_keep=2,
                                  reverse_naming=False, 
                                  prefix='', 
                                  parent_all_to_source=False,
                                  delete_source=True
                                  )
    bottom_name = 'bottom' + side
    spring_bottom_name = 'spring_bottom' + side
    ebones[bottom_bones[0]].name = spring_bottom_name
    ebones[bottom_bones[1]].name = bottom_name

    # thigh no twist
    no_twist_name = create_no_twist_bone(source_bone_name=source_bone_name)
    
    bone_settings(bone_name=spring_bottom_name, 
                  layer_index=Constants.spring_layer, 
                  group_name=Constants.spring_group, 
                  lock_loc=True,
                  bone_type=Constants.spring_type
                  )
    # shape transform bone
    shape_transform_name = 'shape_' + spring_bottom_name
    create_leaf_bone(bone_name=shape_transform_name, 
                     source_bone_name=bottom_name,
                     parent_name='SOURCE_BONE'
                     )
    bone_settings(bone_name=shape_transform_name, 
                  layer_index=Constants.misc_layer, 
                  lock_loc=True, 
                  lock_rot=True, 
                  lock_scale=True, 
                  bone_type=Constants.spring_type
                  )
    set_bone_shape(shape_collection=shape_collection,
                   bone_name=spring_bottom_name, 
                   bone_shape_name='sphere',
                   bone_shape_scale=Constants.target_shape_size, 
                   transform_bone_name=shape_transform_name
                   )     
                  
    bone_settings(bone_name=bottom_name, 
                  layer_index=Constants.misc_layer, 
                  use_deform=True,
                  lock_loc=True,
                  bone_type=Constants.spring_type
                  )
                  
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbone = pbones[spring_bottom_name]
    c = pbone.constraints.new('TRANSFORM')
    c.name = 'thigh bend fwd to scale'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = no_twist_name
    c.map_from = 'ROTATION'
    c.map_to = 'SCALE'

    if source_bone_bend_axis == '-X':
        c.map_to_x_from = 'X'
        c.map_to_y_from = 'X'
        c.map_to_z_from = 'X'
        c.from_min_x_rot = 0
        c.from_max_x_rot = radians(Constants.spring_bottom__thigh_bend_fwd_to_scale__thigh_rot)
        c.to_min_x_scale = 1
        c.to_max_x_scale = Constants.spring_bottom__thigh_bend_fwd_to_scale__scale
        c.to_min_y_scale = 1
        c.to_max_y_scale = Constants.spring_bottom__thigh_bend_fwd_to_scale__scale
        c.to_min_z_scale = 1
        c.to_max_z_scale = Constants.spring_bottom__thigh_bend_fwd_to_scale__scale

    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 0.5

    c = pbone.constraints.new('TRANSFORM')
    c.name = 'thigh bend fwd to rot'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = no_twist_name
    c.map_from = 'ROTATION'
    c.map_to = 'ROTATION'

    if source_bone_bend_axis == '-X':
        c.map_to_x_from = 'X'
        c.map_to_y_from = 'X'
        c.map_to_z_from = 'X'
        c.from_min_x_rot = 0
        c.from_max_x_rot = radians(Constants.spring_bottom__thigh_bend_fwd_to_rot__thigh_rot)
        c.to_min_x_rot = 0
        c.to_max_x_rot = radians(Constants.spring_bottom__thigh_bend_fwd_to_rot__rot)

    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 0.5

    c = pbone.constraints.new('TRANSFORM')
    c.name = 'thigh bend bwd to scale'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = no_twist_name
    c.map_from = 'ROTATION'
    c.map_to = 'SCALE'

    if source_bone_bend_axis == '-X':
        c.map_to_x_from = 'X'
        c.map_to_y_from = 'X'
        c.map_to_z_from = 'X'
        c.from_min_x_rot = radians(Constants.spring_bottom__thigh_bend_bwd_to_scale__thigh_rot)
        c.from_max_x_rot = 0
        c.to_min_x_scale = Constants.spring_bottom__thigh_bend_bwd_to_scale__scale
        c.to_max_x_scale = 1
        c.to_min_y_scale = Constants.spring_bottom__thigh_bend_bwd_to_scale__scale
        c.to_max_y_scale = 1
        c.to_min_z_scale = Constants.spring_bottom__thigh_bend_bwd_to_scale__scale
        c.to_max_z_scale = 1

    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 0.5

    c = pbone.constraints.new('TRANSFORM')
    c.name = 'thigh bend bwd to rot'
    c.use_motion_extrapolate = False
    c.target = rig
    c.subtarget = no_twist_name
    c.map_from = 'ROTATION'
    c.map_to = 'ROTATION'

    if source_bone_bend_axis == '-X':
        c.map_to_x_from = 'X'
        c.map_to_y_from = 'X'
        c.map_to_z_from = 'X'
        c.from_min_x_rot = radians(Constants.spring_bottom__thigh_bend_bwd_to_scale__thigh_rot)
        c.from_max_x_rot = 0
        c.to_min_x_rot = radians(Constants.spring_bottom__thigh_bend_bwd_to_rot__rot)
        c.to_max_x_rot = 0

    c.target_space = 'LOCAL'
    c.owner_space = 'LOCAL'
    c.influence = 0.5

    pbone = pbones[bottom_name]
    c = pbone.constraints.new('LIMIT_SCALE')
    c.name = 'keep scale 1'
    c.use_min_x = True
    c.use_max_x = True
    c.use_min_y = True
    c.use_max_y = True
    c.use_min_z = True
    c.use_max_z = True
    c.min_x = 1
    c.max_x = 1
    c.min_y = 1
    c.max_y = 1
    c.min_z = 1
    c.max_z = 1
    c.use_transform_limit = True
    c.owner_space = 'POSE'
    c.influence = 1

    # set module name on relevant bones (used by the 'N-panel' interface)
    set_module_on_relevant_bones(relevant_bone_names=[spring_bottom_name, bottom_name], 
                                 module=module
                                 )
