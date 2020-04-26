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
from mathutils import Vector, Matrix
from math import radians, sqrt
from .constants import Constants


def report (self, item, error_or_info):
    self.report({error_or_info}, item)



def popup (item, icon):
    def draw(self, context):
        self.layout.label(text=item)
    bpy.context.window_manager.popup_menu(draw, title="GYAZ Game Rigger", icon=icon)
   
    
def get_active_action (obj):
    if obj.animation_data != None:
        action = obj.animation_data.action
    else:
        action = None
    return action


def link_collection(collection_name, path):
    # path to the blend
    filepath = path
    # link or append
    link = True

    with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
        data_to.collections = [name for name in data_from.collections if name.endswith(collection_name)]
    

def vis_point(loc):
    v = bpy.data.objects.new('fwd', None)
    v.empty_display_size = .05
    v.location = loc
    bpy.context.scene.collection.objects.link(v)
    

def get_distance(A, B):
    return sqrt(((B[0] - A[0]) ** 2) + ((B[1] - A[1]) ** 2) + ((B[2] - A[2]) ** 2))

    
def translate_bone_local(name, vector):
    ebone = bpy.context.object.data.edit_bones[name]
    
    mat = ebone.matrix
    mat.invert()

    vec = Vector(vector) @ mat

    ebone.head += vec
    ebone.tail += vec


# angle: degrees, axis: 'X', 'Y', 'Z'
def rotate_bone_local(name, angle, axis):
    ebone = bpy.context.object.data.edit_bones[name]
    
    saved_roll = ebone.roll
    saved_pos = ebone.head.copy()

    mat = ebone.matrix
    eul = mat.to_euler()
    eul.rotate_axis(axis, radians(angle))
    mat = eul.to_matrix().to_4x4()
    mat.translation = saved_pos[0], saved_pos[1], saved_pos[2]
    ebone.matrix = mat

    ebone.roll = saved_roll


def subdivide_bone(name, number, number_to_keep, reverse_naming, prefix, parent_all_to_source, delete_source):
    ebones = bpy.context.object.data.edit_bones
    ebone = ebones[name]
    
    new_ebones = []

    prev_pos = ebone.head
    prev_ebone = ebone
    for n in range(number):
        next_pos = (ebone.tail - ebone.head) * ((1 / number) * (n + 1)) + ebone.head

        new_ebone = ebones.new(
            name=prefix + '_' + str(n + 1) + '_' + ebone.name if not reverse_naming else prefix + '_' + str(
                number - n) + '_' + ebone.name)
        new_ebone.head = prev_pos
        new_ebone.tail = next_pos
        new_ebone.roll = ebone.roll
        new_ebone.use_connect = False
        new_ebone.parent = ebone if parent_all_to_source else prev_ebone

        new_ebones.append(new_ebone)

        prev_pos = next_pos
        prev_ebone = new_ebone

    if delete_source:
        ebones.remove(ebone)

    new_ebones_copy = new_ebones.copy()

    if not reverse_naming:
        for n in range(number - number_to_keep):
            ebone = new_ebones_copy[-(n + 1)]
            ebones.remove(ebone)
            new_ebones.remove(ebone)
    else:
        for n in range(number - number_to_keep):
            ebone = new_ebones_copy[n]
            ebones.remove(ebone)
            new_ebones.remove(ebone)

    return [ebone.name for ebone in new_ebones]


# parent_name: 'SOURCE_BONE', any bone name, ''
def create_leaf_bone(bone_name, source_bone_name, start_middle=False, parent_name='SOURCE_BONE'):
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    rig = bpy.context.object
    leaf_ebone = rig.data.edit_bones.new(name=bone_name)
    source_ebone = rig.data.edit_bones[source_bone_name]
    if start_middle:
        leaf_ebone.head = (source_ebone.head + source_ebone.tail) * .5
        leaf_ebone.tail = source_ebone.tail
    else:
        leaf_ebone.head = source_ebone.tail
        leaf_ebone.tail = source_ebone.tail + (source_ebone.tail - source_ebone.head) * .5
    leaf_ebone.roll = source_ebone.roll
    if parent_name != '':
        if parent_name == 'SOURCE_BONE':
            leaf_ebone.parent = source_ebone
        else:
            leaf_ebone.parent = rig.data.edit_bones[parent_name]


# bone_shape_pos: 'HEAD', 'MIDDLE', 'TAIL'
# lock_loc... expects bool or container of 3 bools
# bvh_tree is needed if a bone_shape_name != '' and bone_shape_manual_scale is not None
def bone_settings(bvh_tree=None, shape_collection=None, bone_name='', layer_index=0, group_name='', use_deform=False, lock_loc=False, lock_rot=False, lock_scale=False, hide_select=False, bone_shape_name='', bone_shape_pos='MIDDLE', bone_shape_manual_scale=None, bone_shape_up=False, bone_shape_up_only_for_ray_casting=False, bone_shape_up_only_for_transform=False, bone_shape_dynamic_size=False, bone_shape_bone='', bone_type=''):
    
    rig = bpy.context.object
    
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    bones = rig.data.bones
    pbone = pbones[bone_name]
    bone = bones[bone_name]
    
    # LAYER:
    bools = [False] * 32
    bools[layer_index] = True
    bone.layers = bools
    
    # GROUP:
    if group_name != '':
        pbone.bone_group = rig.pose.bone_groups[group_name]
    else:
        pbone.bone_group = None
        
    # USE_DEFORM:
    bone.use_deform = use_deform
    
    # TRANSFORM LOCKS:
    if type(lock_loc) == bool:
        pbone.lock_location[0] = lock_loc
        pbone.lock_location[1] = lock_loc
        pbone.lock_location[2] = lock_loc  
    else:
        pbone.lock_location[0] = lock_loc[0]
        pbone.lock_location[1] = lock_loc[1]
        pbone.lock_location[2] = lock_loc[2]
    if type(lock_rot) == bool:
        pbone.lock_rotation[0] = lock_rot
        pbone.lock_rotation[1] = lock_rot
        pbone.lock_rotation[2] = lock_rot  
    else:
        pbone.lock_rotation[0] = lock_rot[0]
        pbone.lock_rotation[1] = lock_rot[1]
        pbone.lock_rotation[2] = lock_rot[2]
    if type(lock_scale) == bool:
        pbone.lock_scale[0] = lock_scale
        pbone.lock_scale[1] = lock_scale
        pbone.lock_scale[2] = lock_scale  
    else:
        pbone.lock_scale[0] = lock_scale[0]
        pbone.lock_scale[1] = lock_scale[1]
        pbone.lock_scale[2] = lock_scale[2]
        
    # HIDE SELECT
    bone.hide_select = hide_select        
    
    # BONE TYPE:
    if bone_type != '':
        pbone['bone_type'] = bone_type
    
    # ELSE:
    bone = bones[bone_name]
    bone.hide = False
    bone.use_inherit_rotation = True
    bone.use_local_location = True
    bone.use_inherit_scale = True
    
    # BONE SHAPE:
    if bone_shape_name != '':
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if bone_shape_manual_scale is None:
            
            # choose a point to cast rays around
            ebones = rig.data.edit_bones
            if bone_shape_bone == '':
                source_ebone = ebones[bone_name]
            else:
                source_ebone = ebones[bone_shape_bone]
            
            if bone_shape_pos == 'HEAD':
                ray_start = source_ebone.head
            elif bone_shape_pos == 'TAIL':
                ray_start = source_ebone.tail
            else:
                """MIDDLE"""
                ray_start = (source_ebone.head + source_ebone.tail) * .5
                    
            # get check points around bone
            number_of_checks = 4
            
            if bone_shape_up and not bone_shape_up_only_for_transform:
                mat = Matrix(((1.0, 0.0, 0.0, 0.3396),
                             (0.0, 0.0, -1.0, 0.4289),
                             (0.0, 1.0, 0.0, 0.1819),
                             (0.0, 0.0, 0.0, 1.0)))
                mat.invert()
            else:
                mat = source_ebone.matrix
                mat.invert()

            check_points = []

            for n in range(number_of_checks):
                v = Vector((0, 0, 1))
                rot_mat = Matrix.Rotation(radians((360 / number_of_checks) * n), 4, 'Y') @ mat
                v = v @ rot_mat
                v += ray_start
                
                check_points.append(v)
        
            # cast rays -> look for geo
            hit_distances = []
            for p in check_points:
                dir = p - ray_start
                dir.normalize()
                hit_loc, hit_nor, hit_index, hit_dist = bvh_tree.ray_cast(ray_start, 
                                                                          dir,
                                                                          10
                                                                          )
                if hit_dist is not None:
                    hit_distances.append(hit_dist)
        
            final_shape_scale = max(hit_distances) * Constants.bone_shape_scale_multiplier if len(hit_distances) > 0 else fallback_shape_size
            
        else:
            final_shape_scale = bone_shape_manual_scale
        
        bpy.ops.object.mode_set(mode='POSE')
    
        pbone.custom_shape_scale = final_shape_scale
        
        wgt = shape_collection.objects['GYAZ_game_rigger_WIDGET__' + bone_shape_name]
        pbone.custom_shape = wgt
        pbone.use_custom_shape_bone_size = bone_shape_dynamic_size
        
        shape_bone_name = 'shape_' + bone_name
        
        if not bone_shape_up:
            if bone_shape_pos != 'HEAD':
                # create shape bone
                create_leaf_bone(bone_name=shape_bone_name,
                                 source_bone_name=bone_name, 
                                 start_middle=bone_shape_pos == 'MIDDLE'
                                 )   
        else:
            if not bone_shape_up_only_for_ray_casting:
                # create shape bone pointing straight up
                bpy.ops.object.mode_set(mode='EDIT')
                ebone = rig.data.edit_bones.new(shape_bone_name)
                ebones = rig.data.edit_bones
                ebone.head = ebones[bone_name].head
                ebone.tail = ebones[bone_name].head + Vector((0, 0, Constants.general_bone_size))
                ebone.roll = 0
                ebone.parent = ebones[bone_name]
        
        if not bone_shape_up_only_for_ray_casting:
            if 'shape_' + bone_name in rig.data.edit_bones:
                # use shape bone as transform of shape
                bpy.ops.object.mode_set(mode='POSE')
                pbones = rig.pose.bones
                shape_pbone = pbones[shape_bone_name]
                pbone.custom_shape_transform = shape_pbone
                # shape bone settings:
                bone = rig.data.bones['shape_' + bone_name]
                pbone = pbones['shape_' + bone_name]
                # layer
                bools = [False] * 32
                bools[Constants.shape_layer] = True
                bones['shape_' + bone_name].layers = bools
                # use deform
                bone.use_deform = False
                # lock transforms
                pbone.lock_location[0] = True
                pbone.lock_location[1] = True
                pbone.lock_location[2] = True
                pbone.lock_rotation[0] = True
                pbone.lock_rotation[1] = True
                pbone.lock_rotation[2] = True
                pbone.lock_scale[0] = True
                pbone.lock_scale[1] = True
                pbone.lock_scale[2] = True
            
    else:
        pbone.custom_shape = None
        

# transform_bone_parent_override is only used if transform_bone_name == REVERSE_RAYCAST
def set_bone_shape(shape_collection, bone_name, bone_shape_name, bone_shape_scale, transform_bone_name='', transform_bone_parent_override='', bvh_tree=None):
    rig = bpy.context.object
    
    if transform_bone_name == 'REVERSE_RAYCAST' or transform_bone_name == 'UP_RAYCAST':
        if bpy.context.mode != 'ARMATURE_EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bone_pos = rig.data.edit_bones[bone_name].head
        
        if transform_bone_name == 'REVERSE_RAYCAST':
            hit_loc, hit_nor, hit_index, hit_dist = bvh_tree.ray_cast(bone_pos + Vector((0, -5, 0)), 
                                                                      Vector((0, 1, 0)), 
                                                                      10
                                                                      )
        elif transform_bone_name == 'UP_RAYCAST':
            hit_loc, hit_nor, hit_index, hit_dist = bvh_tree.ray_cast(bone_pos, 
                                                                      Vector((0, 0, 1)), 
                                                                      10
                                                                      )            
            
        if hit_loc is not None:
            ebone = rig.data.edit_bones.new('shape_' + bone_name)
            new_shape_bone_name = ebone.name
            ebones = rig.data.edit_bones
            ebone.head = hit_loc
            ebone.tail = hit_loc + Vector((0, 0, Constants.face_shape_size))
            ebone.roll = 0
            ebone.parent = ebones[bone_name] if transform_bone_parent_override == '' else ebones[transform_bone_parent_override]
            
            bpy.ops.object.mode_set(mode='POSE')
            bools = [False] * 32
            bools[Constants.shape_layer] = True
            rig.data.bones[new_shape_bone_name].layers = bools
    
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    pbones = bpy.context.object.pose.bones
    wgt = shape_collection.objects['GYAZ_game_rigger_WIDGET__' + bone_shape_name]
    pbones[bone_name].custom_shape = wgt
    if transform_bone_name != '':
        if transform_bone_name == 'REVERSE_RAYCAST' or transform_bone_name == 'UP_RAYCAST':
            pbones[bone_name].custom_shape_transform = pbones[new_shape_bone_name] 
        else:
            pbones[bone_name].custom_shape_transform = pbones[transform_bone_name]              
    pbones[bone_name].use_custom_shape_bone_size = False
    pbones[bone_name].custom_shape_scale = bone_shape_scale


# parent_name: bone name, 'SOURCE_PARENT', ''
# roll: 'SOURCE_ROLL', float
def duplicate_bone(source_name, new_name, parent_name='', half_long=False, roll='SOURCE_ROLL'):
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    rig = bpy.context.object
    ebones = rig.data.edit_bones
    # transform
    ebone = ebones.new(name=new_name)
    source_ebone = rig.data.edit_bones[source_name]
    ebone.head = source_ebone.head
    ebone.tail = (source_ebone.head + source_ebone.tail) * .5 if half_long else source_ebone.tail
    if roll == 'SOURCE_ROLL':
        ebone.roll = ebones[source_name].roll
    else:
        ebone.roll = roll
    # parent
    if parent_name == 'SOURCE_PARENT':
        ebone.parent = ebones[source_name].parent
    elif parent_name != '':
        ebone.parent = rig.data.edit_bones[parent_name]


# point: Vector
def mirror_bone_to_point(bone_name, point):
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    ebones = bpy.context.object.data.edit_bones
    ebone = ebones[bone_name]

    new_head = (point - ebone.head) + point
    new_tail = (point - ebone.tail) + point

    ebone.head = new_head
    ebone.tail = new_tail


def nth_point(A, B, alpha):
    return ((B - A) * alpha) + A


def create_no_twist_bone(source_bone_name):
    # used with twist_targets
    rig = bpy.context.object
    no_twist_name = 'no_twist_' + source_bone_name
    if no_twist_name not in rig.data.bones:
    
        duplicate_bone(source_name=source_bone_name, 
                       new_name=no_twist_name, 
                       parent_name='SOURCE_PARENT', 
                       half_long=True
                       )
        bpy.ops.object.mode_set(mode='POSE')
        pbone = rig.pose.bones[no_twist_name]
        c = pbone.constraints.new('DAMPED_TRACK')
        c.target = rig
        c.subtarget = source_bone_name
        c.head_tail = 1
        bone_settings(bone_name=no_twist_name, 
                      layer_index=Constants.misc_layer, 
                      lock_loc=True, 
                      lock_scale=True
                      )
    
    return no_twist_name


def set_parent_chain(bone_names, first_parent_name):
    rig = bpy.context.object
    if bpy.context.mode != 'ARMATURE_EDIT':    
        bpy.ops.object.mode_set(mode='EDIT')
    for index, name in enumerate(bone_names):
        ebones = rig.data.edit_bones
        if index == 0:
            if first_parent_name != None:
                parent = ebones[first_parent_name]
        else:
            parent = ebones[bone_names[index - 1]]
        ebones[name].parent = parent


def prop_to_drive_constraint(prop_bone_name, bone_name, constraint_name, prop_name, attribute, prop_min, prop_max, prop_default, description, expression):
    
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
        
    rig = bpy.context.object
    
    # prop
    rig.pose.bones[prop_bone_name][prop_name] = prop_default

    # min, max soft_min, soft_max, description on properties
    if "_RNA_UI" not in rig.pose.bones[prop_bone_name]:
        rig.pose.bones[prop_bone_name]["_RNA_UI"] = {}

    rig.pose.bones[prop_bone_name]["_RNA_UI"][prop_name] = {"min": prop_min,
                                                       "max": prop_max,
                                                       "soft_min": prop_min, 
                                                       "soft_max": prop_max,
                                                       "description": description
                                                       }
    # driver
    d = rig.driver_add('pose.bones["' + bone_name + '"].constraints["' + constraint_name + '"].' + attribute).driver
    v1 = d.variables.new()
    v1.name = 'v1'
    v1.type = 'SINGLE_PROP'
    t = v1.targets[0]
    t.id = rig
    t.data_path = 'pose.bones["' + prop_bone_name + '"]["' + prop_name + '"]'
    d.expression = expression


def prop_to_drive_layer(prop_bone_name, layer_index, prop_name, prop_min, prop_max, prop_default, description, expression):
    
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
        
    rig = bpy.context.object
        
    # prop
    rig.pose.bones[prop_bone_name][prop_name] = prop_default

    # min, max soft_min, soft_max, description on properties
    if "_RNA_UI" not in rig.pose.bones[prop_bone_name]:
        rig.pose.bones[prop_bone_name]["_RNA_UI"] = {}

    rig.pose.bones[prop_bone_name]["_RNA_UI"][prop_name] = {"min": prop_min, 
                                                       "max": prop_max,
                                                       "soft_min": prop_min, 
                                                       "soft_max": prop_max,
                                                       "description": description
                                                       }
    # driver
    d = rig.data.driver_add('layers', layer_index).driver
    v1 = d.variables.new()
    v1.name = 'v1'
    v1.type = 'SINGLE_PROP'
    t = v1.targets[0]
    t.id = rig
    t.data_path = 'pose.bones["' + prop_bone_name + '"]["' + prop_name + '"]'
    d.expression = expression


def prop_to_drive_bone_attribute(prop_bone_name, bone_name, bone_type, prop_name, attribute, prop_min, prop_max, prop_default, description, expression):

    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
        
    rig = bpy.context.object

    # prop
    rig.pose.bones[prop_bone_name][prop_name] = prop_default

    # min, max soft_min, soft_max, description on properties
    if "_RNA_UI" not in rig.pose.bones[prop_bone_name]:
        rig.pose.bones[prop_bone_name]["_RNA_UI"] = {}

    rig.pose.bones[prop_bone_name]["_RNA_UI"][prop_name] = {"min": prop_min, 
                                                       "max": prop_max,
                                                       "soft_min": prop_min, 
                                                       "soft_max": prop_max,
                                                       "description": description
                                                       }
    # driver
    if bone_type == 'PBONE':
        d = rig.driver_add('pose.bones["' + bone_name + '"].' + attribute).driver
    elif bone_type == 'BONE':
        d = rig.data.driver_add('bones["' + bone_name + '"].' + attribute).driver
    v1 = d.variables.new()
    v1.name = 'v1'
    v1.type = 'SINGLE_PROP'
    t = v1.targets[0]
    t.id = rig
    t.data_path = 'pose.bones["' + prop_bone_name + '"]["' + prop_name + '"]'
    d.expression = expression


def prop_to_drive_pbone_attribute_with_array_index(prop_bone_name, bone_name, prop_name, attribute, array_index, prop_min, prop_max, prop_default, description, expression):

    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
        
    rig = bpy.context.object

    # prop
    rig.pose.bones[prop_bone_name][prop_name] = prop_default

    # min, max soft_min, soft_max, description on properties
    if "_RNA_UI" not in rig.pose.bones[prop_bone_name]:
        rig.pose.bones[prop_bone_name]["_RNA_UI"] = {}

    rig.pose.bones[prop_bone_name]["_RNA_UI"][prop_name] = {"min": prop_min, 
                                                       "max": prop_max,
                                                       "soft_min": prop_min, 
                                                       "soft_max": prop_max,
                                                       "description": description
                                                       }
    # driver
    d = rig.driver_add('pose.bones["' + bone_name + '"].' + attribute, array_index).driver
    v1 = d.variables.new()
    v1.name = 'v1'
    v1.type = 'SINGLE_PROP'
    t = v1.targets[0]
    t.id = rig
    t.data_path = 'pose.bones["' + prop_bone_name + '"]["' + prop_name + '"]'
    d.expression = expression


def separate_relevant_bones(relevant_bone_names):
    # separate relevant bones into fk and no-fk groups
    bpy.ops.object.mode_set(mode='POSE')
    pbones = bpy.context.object.pose.bones
    fk_bones = []
    non_fk_bones = []
    touch_bones = []
    for name in relevant_bone_names:
        pbone = pbones[name]
        if 'bone_type' in pbone:
            if pbone['bone_type'] == 'fk':
                fk_bones.append(name)
            elif pbone['bone_type'] == 'ik' or pbone['bone_type'] == 'ctrl':
                non_fk_bones.append(name)
            elif pbone['bone_type'] == 'touch':
                touch_bones.append(name)
    return fk_bones, non_fk_bones, touch_bones


# fk, ik visibility
def bone_visibility(prop_bone_name, module, relevant_bone_names, ik_ctrl):
    fk_bones, non_fk_bones, touch_bones = separate_relevant_bones(relevant_bone_names=relevant_bone_names)
    for bone in fk_bones:
        prop_to_drive_bone_attribute(prop_bone_name=prop_bone_name, 
                                     bone_name=bone, 
                                     bone_type='BONE',
                                     prop_name='visible_fk_' + module, 
                                     attribute='hide', prop_min=0,
                                     prop_max=1, 
                                     prop_default=1, 
                                     description='', 
                                     expression='1-v1'
                                     )
    if ik_ctrl != None:
        for bone in non_fk_bones:
            prop_to_drive_bone_attribute(prop_bone_name=prop_bone_name, 
                                         bone_name=bone, 
                                         bone_type='BONE',
                                         prop_name='visible_' + ik_ctrl + '_' + module, 
                                         attribute='hide',
                                         prop_min=0, 
                                         prop_max=1, 
                                         prop_default=1, 
                                         description='',
                                         expression='1-v1'
                                         )
    if len(touch_bones) > 0:
        for bone in touch_bones:
            prop_to_drive_bone_attribute(prop_bone_name=prop_bone_name, 
                                         bone_name=bone, 
                                         bone_type='BONE',
                                         prop_name='visible_touch_' + module, 
                                         attribute='hide', 
                                         prop_min=0,
                                         prop_max=1, 
                                         prop_default=1, 
                                         description='', 
                                         expression='1-v1'
                                         )
    

def create_module_prop_bone(module):
    
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    rig = bpy.context.object
    
    name = 'module_props__' + module
    ebones = rig.data.edit_bones
    # create module bone if it does not exist
    if ebones.get(name) == None:
        ebone = ebones.new(name=name)
        ebone.head = Vector((0, 0, 0))
        ebone.tail = Vector((0, 0, 0.5))
        bone_settings(bone_name=name, 
                      layer_index=Constants.module_prop_layer, 
                      use_deform=False
                      )
    return name


def set_module_on_relevant_bones(relevant_bone_names, module):
    # set module name on relevant bones (used by the 'N-panel' interface)
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    
    rig = bpy.context.object
    
    for name in relevant_bone_names:
        rig.pose.bones[name]['module'] = module
        

# for registering modules for the 'Snap&Key' operator
def snappable_module(module):
    rig = bpy.context.object
    if 'snappable_modules' not in rig.data:
        rig.data['snappable_modules'] = []
    list = [item for item in rig.data['snappable_modules']]
    list.append(module)
    rig.data['snappable_modules'] = list

    rig.pose.bones['module_props__' + module]["snap_n_key__fk_ik"] = 1
    rig.pose.bones['module_props__' + module]["snap_n_key__should_snap"] = 1


def signed_angle(vector_u, vector_v, normal):
    # normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle
    return angle


def get_pole_angle(base_bone_name, ik_bone_name, pole_bone_name):
    
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        
    ebones = bpy.context.object.data.edit_bones
    
    base_bone = ebones[base_bone_name]
    ik_bone = ebones[ik_bone_name]
    pole_bone = ebones[pole_bone_name]
    
    pole_location = pole_bone.head
    pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)


def calculate_pole_target_location(b1, b2, b3, pole_target_distance):
    
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    rig = bpy.context.object
    ebones = rig.data.edit_bones

    midpoint = (ebones[b1].head + ebones[b3].head) * .5
    difference = ebones[b2].head - midpoint
    # calculate multiplier for desired target distance
    current_distance = get_distance(Vector((0, 0, 0)), difference)
    multiplier = pole_target_distance / current_distance
    
    return difference * multiplier + ebones[b2].head


def calculate_pole_target_location_pbone (b1, b2, b3, pole_target_distance):
    pbones = bpy.context.object.pose.bones
    midpoint = ( pbones[b1].matrix.translation + pbones[b3].matrix.translation ) * .5
    difference = pbones[b2].matrix.translation - midpoint
    # calculate multiplier for desired target distance
    current_distance = get_distance (Vector ((0, 0, 0)), difference)
    multiplier = pole_target_distance / current_distance
    return difference * multiplier + pbones[b2].matrix.translation


def lerp (A, B, alpha):    
    return A*(1-alpha)+B*(alpha)     


def calculate_pole_target_location_2(b1, b2, b3, pole_target_distance, b2_bend_axis):
    
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    rig = bpy.context.object
    ebones = rig.data.edit_bones

    pole_bone = 'pole_pos_' + b2
    duplicate_bone(source_name=b2, 
                   new_name=pole_bone
                   )

    if b2_bend_axis == 'X':
        v = 0, 0, -pole_target_distance
    elif b2_bend_axis == '-X':
        v = 0, 0, pole_target_distance

    translate_bone_local(name=pole_bone, vector=v)

    pole_pos = ebones[pole_bone].head
    rig.data['temp'] = pole_pos
    ebones.remove(ebones[pole_bone])

    return Vector((rig.data['temp']))


def get_ik_group_name(side):
    # set group
    if side == Constants.sides[0]:
        ik_group_name = Constants.left_ik_group
    elif side == Constants.sides[1]:
        ik_group_name = Constants.right_ik_group
    elif side == '_c':
        ik_group_name = Constants.central_ik_group
    return ik_group_name


# upper_or_lower_limb: 'UPPER', 'LOWER'
# end_affector_name is used if 
def create_twist_bones(bvh_tree, shape_collection, source_bone_name, count, upper_or_lower_limb, twist_target_distance, end_affector_name, influences, is_thigh):
    
    source_bone_bend_axis = '-X'
    
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    rig = bpy.context.object

    twist_bone_names = subdivide_bone (name=source_bone_name, 
                                       number=3, 
                                       number_to_keep=count, 
                                       reverse_naming=True if upper_or_lower_limb == 'LOWER' else False, 
                                       prefix='twist', 
                                       parent_all_to_source=True,
                                       delete_source=False
                                       )

    # twist target bones
    if upper_or_lower_limb == 'UPPER':
        no_twist_name = create_no_twist_bone(source_bone_name=source_bone_name)

        # duplicate source bone
        twist_target_name = 'twist_target_' + source_bone_name
        duplicate_bone(source_name=source_bone_name, 
                       new_name=twist_target_name, 
                       parent_name=no_twist_name
                       )
                       
        # twist target
        if source_bone_bend_axis == '-X':
            vector = 0, 0, -twist_target_distance

        translate_bone_local(name=twist_target_name, 
                             vector=vector
                             )
        ebones = rig.data.edit_bones
        ebone = ebones[twist_target_name]
        ebone.tail = ebone.head + Vector((0, 0, Constants.general_bone_size))
        
        bone_settings(bvh_tree=bvh_tree, 
                      shape_collection=shape_collection, 
                      bone_name=twist_target_name, 
                      layer_index=Constants.twist_target_layer, 
                      group_name=Constants.twist_group,
                      lock_rot=True,
                      lock_scale=True,
                      bone_shape_name='twist_target',
                      bone_shape_pos='HEAD',
                      bone_shape_manual_scale=Constants.target_shape_size
                      )

        # twist target line
        bpy.ops.object.mode_set(mode='EDIT')
        ebones = rig.data.edit_bones
        tt_ebone = ebones[twist_target_name]
        twist_target_line_name = 'twist_target_line_' + source_bone_name
        ttl_ebone = ebones.new(name=twist_target_line_name)
        ttl_ebone.head = ebones[source_bone_name].head
        ttl_ebone.tail = tt_ebone.head
        ttl_ebone.parent = ebones[source_bone_name]
        
        bone_settings(bvh_tree=bvh_tree, 
                      shape_collection=shape_collection, 
                      bone_name=twist_target_line_name, 
                      layer_index=Constants.twist_target_layer, 
                      group_name=Constants.twist_group,
                      lock_loc=True,
                      lock_rot=True, 
                      lock_scale=True,
                      hide_select=True,
                      bone_shape_name='line',
                      bone_shape_pos='HEAD',
                      bone_shape_manual_scale=1,
                      bone_shape_dynamic_size=True
                      )

    elif upper_or_lower_limb == 'LOWER':
        
        if end_affector_name != '':
            twist_target_name = 'twist_target_' + source_bone_name
            create_leaf_bone(bone_name=twist_target_name, 
                             source_bone_name=source_bone_name, 
                             start_middle=False, 
                             parent_name=''
                             )
            
            # 'Child Of' parent it to end affector (hand or foot) - the use of constraint is needed for the twist constraints to work
            bpy.ops.object.mode_set(mode='POSE')
            pbone = rig.pose.bones[twist_target_name]
            c = pbone.constraints.new('CHILD_OF')
            c.name = 'Copy End Affector'
            c.target = rig
            c.subtarget = end_affector_name
            # set inverse matrix
            rig.data.bones.active = rig.data.bones[twist_target_name]
            context_copy = bpy.context.copy()
            context_copy["constraint"] = pbone.constraints['Copy End Affector']
            bpy.ops.constraint.childof_set_inverse(context_copy, 
                                                   constraint='Copy End Affector',
                                                   owner='BONE'
                                                   )
            bone_settings(bvh_tree=bvh_tree, 
                          shape_collection=shape_collection, 
                          bone_name=twist_target_name, 
                          layer_index=Constants.twist_target_layer, 
                          group_name=Constants.twist_group, 
                          lock_loc=True, 
                          lock_rot=(True, False, True),
                          lock_scale=True, 
                          bone_shape_name='twist_target',
                          bone_shape_pos='HEAD',
                          bone_shape_manual_scale=Constants.target_shape_size
                          )
    # bone settings
    for name in twist_bone_names:
        bone_settings(bvh_tree=bvh_tree, 
                      shape_collection=shape_collection, 
                      bone_name=name, 
                      layer_index=Constants.twist_layer, 
                      group_name=Constants.twist_group,
                      use_deform=True,
                      lock_loc=True,
                      lock_rot=(True, False, True),
                      lock_scale=True,
                      bone_type=Constants.twist_type
                      )
    
    # CONSTRAINTS
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    
    pbones = rig.pose.bones
    influences = influences[count - 1]
    
    for n in range(1, count + 1):
        pbone = pbones['twist_' + str(n) + '_' + source_bone_name]

        if upper_or_lower_limb == 'UPPER':
            c = pbone.constraints.new('LOCKED_TRACK')
            c.name = 'twist'
            c.target = rig
            c.subtarget = twist_target_name
            c.head_tail = 0

            if source_bone_bend_axis == '-X':
                c.track_axis = 'TRACK_NEGATIVE_Z'

            c.lock_axis = 'LOCK_Y'
            c.influence = influences[n - 1]

        elif upper_or_lower_limb == 'LOWER':
            c = pbone.constraints.new('TRACK_TO')
            c.name = 'twist'
            c.target = rig
            c.subtarget = twist_target_name
            c.head_tail = 0
            c.track_axis = 'TRACK_Y'
            c.up_axis = 'UP_Z'
            c.use_target_z = True
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'
            c.influence = influences[n - 1]

            c = pbone.constraints.new('LIMIT_ROTATION')
            c.name = 'limit rotation'
            c.owner_space = 'LOCAL'
            c.influence = 1
            c.use_limit_x = True
            c.use_limit_y = False
            c.use_limit_z = True
            c.use_transform_limit = True
            c.min_x = 0
            c.max_x = 0
            c.min_z = 0
            c.max_z = 0

    # twist target line
    if upper_or_lower_limb == 'UPPER':
        pbone = pbones['twist_target_line_' + source_bone_name]
        c = pbone.constraints.new('STRETCH_TO')
        c.name = 'twist target line'
        c.target = rig
        c.subtarget = 'twist_target_' + source_bone_name
        c.head_tail = 0
        c.bulge = 1
        c.use_bulge_min = False
        c.use_bulge_max = False
        c.volume = 'VOLUME_XZX'
        c.keep_axis = 'PLANE_X'
        c.influence = 1

    # twist target thigh
    if is_thigh == True:
        pbone = pbones['twist_target_' + source_bone_name]
        c = pbone.constraints.new('TRANSFORM')
        c.name = 'thigh rotation to location'
        c.use_motion_extrapolate = True
        c.target = rig
        c.subtarget = source_bone_name
        c.map_from = 'ROTATION'
        c.map_to = 'LOCATION'

        if source_bone_bend_axis == '-X':
            c.map_to_x_from = 'X'
            c.map_to_y_from = 'X'
            c.map_to_z_from = 'X'
            c.from_min_x_rot = radians(-180)
            c.from_max_x_rot = radians(180)

        c.to_min_y = 1
        c.to_max_y = -1
        c.target_space = 'LOCAL'
        c.owner_space = 'LOCAL'
        c.influence = 1
        
        
def three_bone_limb(bvh_tree, shape_collection, module, b1, b2, b3, pole_target_name, parent_pole_target_to_ik_target, b2_bend_axis, b2_bend_back_limit, first_parent_name, ik_b3_parent_name, pole_target_parent_name, b3_shape_up, side):
    
    rig = bpy.context.object
    
    fk_prefix = Constants.fk_prefix
    ik_prefix = Constants.ik_prefix
    ik_group = get_ik_group_name(side=side)
    
    limit_ik_b2 = True
    b2_bend_axis = b2_bend_axis
    b2_max_bend_bwrd = b2_bend_back_limit
    limit_fk_b2 = False
    inable_stretch = False
    module_prop_layer = 30

    bone_names = (b1, b2, b3)

    # bones that should be used for animation
    relevant_bone_names = []

    # for module properties
    prop_bone_name = create_module_prop_bone(module=module)

    # AXIS LOCKS
    if b2_bend_axis == 'X' or '-X':
        axis_locks_string = ['y', 'z']
        axis_locks_int = [1, 2]

    # _____________________________________________________________________________________________________

    # LOW-LEVEL RIG
    for name in bone_names:
        bone_settings(bone_name=name, 
                      layer_index=Constants.base_layer, 
                      group_name=Constants.base_group, 
                      use_deform=True, 
                      lock_loc=True,  
                      lock_scale=True, 
                      bone_type=Constants.base_type
                      )
        relevant_bone_names.append(name)

    # _____________________________________________________________________________________________________

    # FK
    for index, name in enumerate(bone_names):
        if index == 0:
            parent_name = first_parent_name
        else:
            parent_name = fk_prefix + bone_names[index - 1]
        
        full_name = fk_prefix + name
        
        duplicate_bone(source_name=name, 
                       new_name=full_name, 
                       parent_name=parent_name
                       )
        bone_settings(bvh_tree=bvh_tree,
                      shape_collection=shape_collection,
                      bone_name=full_name, 
                      layer_index=Constants.fk_layer, 
                      group_name=Constants.fk_group, 
                      lock_loc=True, 
                      lock_scale=True,
                      bone_shape_name='sphere' if index == 2 else 'inner_circle', 
                      bone_shape_pos='HEAD' if index == 2 else 'MIDDLE',
                      bone_shape_up=index == 2 and b3_shape_up,
                      bone_type=Constants.fk_type
                      )

        relevant_bone_names.append(full_name)

    # FK LIMITS:
    # limit fk_b2 to single-axis rotation
    for axis in axis_locks_int:
        prop_to_drive_pbone_attribute_with_array_index(prop_bone_name=fk_prefix + b2, 
                                                       bone_name=fk_prefix + b2, 
                                                       prop_name='limit_fk_' + module, 
                                                       attribute='lock_rotation', 
                                                       array_index=axis, 
                                                       prop_min=0, 
                                                       prop_max=1, 
                                                       prop_default=limit_fk_b2, 
                                                       description='', 
                                                       expression='v1'
                                                       )

    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[fk_prefix + b2]
    c = pbone.constraints.new('LIMIT_ROTATION')
    c.name = 'Limit rotation'
    c.owner_space = 'LOCAL'
    c.use_limit_x = True
    c.use_limit_y = True
    c.use_limit_z = True
    c.use_transform_limit = True
    if 0 in axis_locks_int:
        c.min_x = 0
        c.max_x = 0
    if 1 in axis_locks_int:
        c.min_y = 0
        c.max_y = 0
    if 2 in axis_locks_int:
        c.min_z = 0
        c.max_z = 0

    # limits
    if b2_bend_axis == 'X':
        bend_axis = 'x'
        b2_min = 0 - radians(b2_max_bend_bwrd)
        b2_max = radians(180) - abs(b2_min)
    elif b2_bend_axis == '-X':
        bend_axis = 'x'
        b2_max = 0 + radians(b2_max_bend_bwrd)
        b2_min = abs(b2_max) - radians(180)

    if bend_axis == 'x':
        axis = 0
        c.min_x = b2_min
        c.max_x = b2_max

    prop_to_drive_constraint(prop_bone_name=fk_prefix + b2, 
                             bone_name=fk_prefix + b2, 
                             constraint_name='Limit rotation',
                             prop_name='limit_fk_' + module, 
                             attribute='mute', 
                             prop_min=0, 
                             prop_max=1,
                             prop_default=limit_fk_b2, 
                             description='', 
                             expression='1-v1'
                             )

    # BIND RIG TO FK RIG constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones

    for index, name in enumerate(bone_names):
        c = pbones[name].constraints.new('COPY_ROTATION')
        c.name = 'bind_to_fk_1'
        c.target = rig
        c.subtarget = fk_prefix + name
        c.mute = True

    # _____________________________________________________________________________________________________

    # IK
    for index, name in enumerate(bone_names):
        if index == 0:
            parent_name = first_parent_name
        elif index == 1:
            parent_name = ik_prefix + bone_names[index - 1]
        else:
            """index == 2"""
            parent_name = ik_b3_parent_name
        
        final_name = ik_prefix + name
        
        duplicate_bone(source_name=name, 
                       new_name=final_name, 
                       parent_name=parent_name
                       )

        if index == 2:
            layer = Constants.ctrl_ik_layer
            lock_loc = False
        else:
            layer = Constants.ctrl_ik_extra_layer
            lock_loc = True
        
        bone_settings(bvh_tree=bvh_tree, 
                      shape_collection=shape_collection, 
                      bone_name=final_name, 
                      layer_index=layer, 
                      group_name=ik_group, 
                      lock_loc=lock_loc, 
                      lock_scale=True,
                      bone_shape_name='cube' if index == 2 else '', 
                      bone_shape_pos='HEAD', 
                      bone_shape_up=index == 2 and b3_shape_up, 
                      bone_type=Constants.ik_type
                      )

    relevant_bone_names.append(ik_prefix + b3)

    # pole target:
    
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    
    pole_pos = calculate_pole_target_location_2(b1=b1, 
                                                b2=b2, 
                                                b3=b3, 
                                                pole_target_distance=Constants.pole_target_distance, 
                                                b2_bend_axis=b2_bend_axis
                                                )

    # create pole_target
    pole_target_name = 'target_' + pole_target_name
    ebone = ebones.new(name=pole_target_name)
    ebone.head = pole_pos
    ebone.tail = pole_pos + Vector((0, 0, Constants.general_bone_size))

    relevant_bone_names.append(pole_target_name)

    # parent it to ik_target
    if pole_target_parent_name != '':
        if parent_pole_target_to_ik_target:
            ebone.parent = ebones[ik_prefix + b3]
        else:
            ebone.parent = ebones[pole_target_parent_name]
        
    bone_settings(bvh_tree=bvh_tree, 
                  shape_collection=shape_collection, 
                  bone_name=pole_target_name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=ik_group, 
                  lock_scale=False, 
                  bone_shape_name='sphere', 
                  bone_shape_pos='HEAD', 
                  bone_shape_manual_scale=Constants.target_shape_size, 
                  bone_shape_up=True, 
                  bone_type=Constants.ik_type
                  )

    # constraint
    pole_angle = get_pole_angle(base_bone_name=b1, 
                                ik_bone_name=b2, 
                                pole_bone_name=pole_target_name
                                )

    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    pbone = pbones[ik_prefix + b2]

    c = pbone.constraints.new('IK')
    c.target = rig
    c.subtarget = ik_prefix + b3
    c.pole_target = rig
    c.pole_subtarget = pole_target_name
    c.pole_angle = pole_angle
    c.chain_count = 2
    c.use_stretch = inable_stretch

    # pole target line
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    pole_target_line_name = 'target' + '_line_' + pole_target_name

    ebone = ebones.new(name=pole_target_line_name)
    ebone.head = ebones[ik_prefix + b2].head
    ebone.tail = ebones[pole_target_name].head
    ebone.parent = ebones[ik_prefix + b2]
    
    bone_settings(bvh_tree=bvh_tree,
                  shape_collection=shape_collection,
                  bone_name=pole_target_line_name, 
                  layer_index=Constants.ctrl_ik_layer, 
                  group_name=ik_group, 
                  lock_loc=True, 
                  lock_rot=True, 
                  lock_scale=True,
                  hide_select=True, 
                  bone_shape_name='line', 
                  bone_shape_pos='HEAD',
                  bone_shape_manual_scale=1,
                  bone_shape_dynamic_size=True,
                  bone_type=Constants.ik_type
                  )
    # contraint              
    pbone = rig.pose.bones[pole_target_line_name]
    c = pbone.constraints.new('STRETCH_TO')
    c.target = rig
    c.subtarget = pole_target_name

    relevant_bone_names.append(pole_target_line_name)

    # pole target snap position bone
    # when snapping ik to fk, the pole target copies the location of this bone
    # this bone is parented to fk bone 2 (forearm, shin)
    snap_target_pole_name = 'snap_' + pole_target_name
    
    duplicate_bone(source_name=pole_target_name, 
                   new_name=snap_target_pole_name, 
                   parent_name=fk_prefix + bone_names[1]
                   )
    bone_settings(bone_name=snap_target_pole_name, 
                  layer_index=Constants.ctrl_ik_extra_layer, 
                  group_name=ik_group, 
                  lock_loc=True, 
                  lock_rot=True, 
                  lock_scale=True,
                  bone_type=Constants.ik_type
                  )

    # IK LIMITS:
    default = 1 if limit_ik_b2 else 0
    
    # lock ik axes
    pbone = pbones[ik_prefix + b2]
    for axis in axis_locks_string:
        setattr(pbone, 'lock_ik_' + axis, limit_ik_b2)
        prop_to_drive_bone_attribute (prop_bone_name=prop_bone_name, 
                                      bone_name=ik_prefix+b2, 
                                      bone_type='PBONE', 
                                      prop_name='limit_ik_'+module, 
                                      attribute='lock_ik_'+axis, 
                                      prop_min=0, 
                                      prop_max=1, 
                                      prop_default=default, 
                                      description='', 
                                      expression='v1'
                                      )

    # limit rot
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[ik_prefix + b2]
    if b2_bend_axis == 'X':
        pbone.ik_min_x = b2_min
    elif b2_bend_axis == '-X':
        pbone.ik_max_x = b2_max

    setattr(pbone, 'use_ik_limit_' + bend_axis, limit_ik_b2)
    prop_to_drive_bone_attribute (prop_bone_name=prop_bone_name, 
                                  bone_name=ik_prefix+b2, 
                                  bone_type='PBONE', 
                                  prop_name='limit_ik_'+module, 
                                  attribute='use_ik_limit_'+bend_axis, 
                                  prop_min=0, 
                                  prop_max=1, 
                                  prop_default=default, 
                                  description='', 
                                  expression='v1'
                                  )

    # BIND RIG TO IK RIG constraints
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones

    for index, name in enumerate(bone_names):
        c = pbones[name].constraints.new('COPY_ROTATION')
        c.name = 'bind_to_ik_1'
        c.target = rig
        c.subtarget = ik_prefix + name
        c.mute = True

    # BIND RIG TO (0:fk, 1:ik, 2:bind)
    for name in bone_names:
        prop_to_drive_constraint(prop_bone_name=prop_bone_name, 
                                 bone_name=name, 
                                 constraint_name='bind_to_fk_1',
                                 prop_name='switch_' + module, 
                                 attribute='mute', 
                                 prop_min=0, 
                                 prop_max=2,
                                 prop_default=0, 
                                 description='0:fk, 1:ik, 2:bind',
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
                                 description='0:fk, 1:ik, 2:bind',
                                 expression='1 - (v1 > 0 and v1 < 2)'
                                 )

    # visibility
    bone_visibility(prop_bone_name=prop_bone_name, 
                    module=module, 
                    relevant_bone_names=relevant_bone_names, 
                    ik_ctrl='ik'
                    )

    # set module name on relevant bones (used by the interface)
    set_module_on_relevant_bones(relevant_bone_names=relevant_bone_names, 
                                 module=module
                                 )

    # prop that stores bone names for fk/ik snapping
    bpy.ops.object.mode_set(mode='POSE')
    pbone = rig.pose.bones[prop_bone_name]

    stem = 'snapinfo_3bonelimb_'
    index_is_free = False
    index = 0
    while not index_is_free:
        for n in range(0, 1000):
            prop_name_candidate = stem + str(index + n)
            if prop_name_candidate not in pbone:
                pbone[prop_name_candidate] = [fk_prefix + b1, 
                                              fk_prefix + b2, 
                                              fk_prefix + b3,
                                              ik_prefix + b1, 
                                              ik_prefix + b2, 
                                              ik_prefix + b3, 
                                              pole_target_name,
                                              str(Constants.pole_target_distance), 
                                              snap_target_pole_name, 
                                              fk_prefix + b3,
                                              ik_prefix + b3, 
                                              'None'
                                              ]
            # stop for loop
            break
        # stop while_loop
        index_is_free = True


#bvh_tree = BVHTree.FromObject(bpy.context.object.children[0], bpy.context.depsgraph)
#shape_collection = bpy.data.collections['GYAZ_game_rigger_widgets']

# should only be used to affect FK BONES
def isolate_rotation(module, parent_bone_name, first_bone_name):
    
    rig = bpy.context.object 
    
    prop_bone_name = create_module_prop_bone(module)

    if bpy.context.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    # delete parent relationship tween parent_bone and first bone
    # create intermediate bones
    # one that's parented to 'parent bone'
    ebones = rig.data.edit_bones
    first_intermeidate_bone_name = 'isolate_rot_' + first_bone_name + '_parent'
    ebone = ebones.new(name=first_intermeidate_bone_name)
    ebone.head = ebones[first_bone_name].head
    ebone.tail = ebone.head + Vector((0, 0, Constants.general_bone_size))
    ebones = rig.data.edit_bones
    ebone.parent = ebones[parent_bone_name]
    
    bone_settings(bone_name=first_intermeidate_bone_name, 
                  layer_index=Constants.fk_extra_layer, 
                  lock_loc=True, 
                  lock_scale=True
                  )

    # bone that becomes the parent of 'first_bone_name'
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    second_intermediate_bone_name = 'isolate_rot_' + first_bone_name + '_child'
    ebone = ebones.new(name=second_intermediate_bone_name)
    ebone.head = ebones[first_bone_name].head
    ebone.tail = ebone.head + Vector((0, 0, Constants.general_bone_size))
    ebones = rig.data.edit_bones
    ebone.parent = ebones['root_extract']

    bone_settings(bone_name=second_intermediate_bone_name, 
                  layer_index=Constants.fk_extra_layer, 
                  lock_loc=True, 
                  lock_scale=True
                  )

    # parent first bone to this bone
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig.data.edit_bones
    ebones[first_bone_name].parent = ebones[second_intermediate_bone_name]

    # constraint second itermediate bone to the first one
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    cs = pbones[second_intermediate_bone_name].constraints

    c = cs.new('COPY_LOCATION')
    c.target = rig
    c.subtarget = first_intermeidate_bone_name

    c = cs.new('COPY_SCALE')
    c.target = rig
    c.subtarget = first_intermeidate_bone_name

    c = cs.new('COPY_ROTATION')
    c.name = 'isolate_rot_1'
    c.target = rig
    c.subtarget = first_intermeidate_bone_name

    prop_to_drive_constraint(prop_bone_name=first_bone_name, 
                             bone_name=second_intermediate_bone_name,
                             constraint_name='isolate_rot_1', 
                             prop_name='fixate_' + first_bone_name,
                             attribute='influence', 
                             prop_min=0.0, 
                             prop_max=1.0, 
                             prop_default=0.0,
                             description='', 
                             expression='1-v1'
                             )
                        
def get_parent_name(name):
    if bpy.context.mode != 'ARMATURE_EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    return bpy.context.object.data.edit_bones[name].parent.name

def set_bone_only_layer(bone_name, layer_index):
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bools = [False] * 32
    bools[layer_index] = True
    bpy.context.object.data.bones[bone_name].layers = bools
