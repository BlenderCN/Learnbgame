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
from mathutils.bvhtree import BVHTree
from mathutils import Vector

from .constants import Constants
from .utils import create_module_prop_bone
from .utils import bone_settings
from .utils import link_collection
from .utils import prop_to_drive_layer
from .utils import duplicate_bone
from .utils import set_bone_only_layer


def prepare():
    
    rig = bpy.context.object

    # remove all drivers
    rig.animation_data_clear()
    rig.data.animation_data_clear()

    # GYAZ stamp
    rig.data['GYAZ_rig'] = True
    
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    for bone in rig.data.bones:
        set_bone_only_layer(bone_name=bone.name, 
                            layer_index=Constants.source_layer
                            )

    # make all bone layers visible
    for n in range(0, 32):
        rig.data.layers[n] = True

    # visualization
    rig.display_type = 'WIRE'
    rig.data.display_type = 'OCTAHEDRAL'

    rig.data.show_names = False
    rig.data.show_axes = False
    rig.data.show_bone_custom_shapes = True
    rig.data.show_group_colors = True
    rig.show_in_front = False
    rig.data.use_deform_delay = False

    create_module_prop_bone(module='general')

    # delete constraints from all bones, should any exist
    bpy.ops.object.mode_set(mode='POSE')
    pbones = rig.pose.bones
    for pbone in pbones:
        cs = pbone.constraints
        if len(cs) > 0:
            for c in cs:
                cs.remove(c)

    # lock mesh transforms
    for child in rig.children:
        if child.type == 'MESH':
            child.lock_location[0] = True
            child.lock_location[1] = True
            child.lock_location[2] = True
            child.lock_rotation[0] = True
            child.lock_rotation[1] = True
            child.lock_rotation[2] = True
            child.lock_scale[0] = True
            child.lock_scale[1] = True
            child.lock_scale[2] = True
            
    # MESH FOR RAY CASTING:
    # create new object from character meshes and make a BVHTree from it
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for mesh in rig.children:
        if mesh.type == 'MESH':
            mesh.hide_select = False
            mesh.select_set(True)
    bpy.context.view_layer.objects.active = rig.children[0]
    bpy.ops.object.duplicate_move()
    bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    merged_character_mesh = bpy.context.active_object

    bvh_tree = BVHTree.FromObject(bpy.context.scene.objects[merged_character_mesh.name], bpy.context.depsgraph)

    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
        
    # SHAPE COLLECTION
    link_collection('GYAZ_game_rigger_widgets', Constants.source_path)
    
    # BONE GROUPS
    bpy.ops.object.mode_set(mode='POSE')
    bgroups = rig.pose.bone_groups

    bg = bgroups.new(name=Constants.base_group)
    bg.color_set = Constants.base_group_color_set

    bg = bgroups.new(name=Constants.fk_group)
    bg.color_set = Constants.fk_group_color_set

    bg = bgroups.new(name=Constants.central_ik_group)
    bg.color_set = Constants.central_ik_group_color_set

    bg = bgroups.new(name=Constants.left_ik_group)
    bg.color_set = Constants.left_ik_group_color_set

    bg = bgroups.new(name=Constants.right_ik_group)
    bg.color_set = Constants.right_ik_group_color_set

    bg = bgroups.new(name=Constants.twist_group)
    bg.color_set = Constants.twist_group_color_set

    bg = bgroups.new(name=Constants.spring_group)
    bg.color_set = Constants.spring_group_color_set

    bg = bgroups.new(name=Constants.ik_prop_group)
    bg.color_set = Constants.ik_prop_group_color_set

    bg = bgroups.new(name=Constants.face_group)
    bg.color_set = Constants.face_group_color_set

    bg = bgroups.new(name=Constants.target_group)
    bg.color_set = Constants.target_group_color_set
            

    return bvh_tree, bpy.data.collections['GYAZ_game_rigger_widgets'], merged_character_mesh



def finalize(merged_character_mesh):
    
    rig = bpy.context.object

    # Add prop to toggle low-level rig's visibility
    prop_bone_name = 'module_props__general'
    
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.base_layer, 
                        prop_name='visible_base_bones', 
                        prop_min=0,
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.twist_layer, 
                        prop_name='visible_twist_bones', 
                        prop_min=0,
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.spring_layer, 
                        prop_name='visible_spring_bones', 
                        prop_min=0,
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.face_layer, 
                        prop_name='visible_face_bones', 
                        prop_min=0,
                        prop_max=1, 
                        prop_default=1, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.face_extra_layer, 
                        prop_name='visible_extra_face_bones',
                        prop_min=0, 
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.root_layer, 
                        prop_name='visible_root_bone', 
                        prop_min=0,
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.ik_prop_layer, 
                        prop_name='visible_prop_bones', 
                        prop_min=0,
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )
    prop_to_drive_layer(prop_bone_name=prop_bone_name, 
                        layer_index=Constants.twist_target_layer, 
                        prop_name='visible_twist_targets',
                        prop_min=0, 
                        prop_max=1, 
                        prop_default=0, 
                        description='', 
                        expression='v1'
                        )

    visible_layers = set()
    visible_layers = visible_layers.union({Constants.fk_layer, Constants.ctrl_ik_layer, Constants.touch_layer})
    all_layers = set(n for n in range(32))
    hidden_layers = all_layers - visible_layers

    for n in visible_layers:
        rig.data.layers[n] = True

    for n in hidden_layers:
        rig.data.layers[n] = False

    bpy.data.objects.remove(merged_character_mesh, do_unlink=True)

    rig.show_in_front = False

    bpy.ops.object.mode_set(mode='POSE')

    rig['snap_start'] = 1
    rig['snap_end'] = 250

    if "_RNA_UI" not in rig:
        rig["_RNA_UI"] = {}

    rig["_RNA_UI"]['snap_start'] = {"min": 0}
    rig["_RNA_UI"]['snap_end'] = {"min": 0}
    
    if 'snappable_modules' in rig.data:
        list = rig.data['snappable_modules']
        if len(list) > 0:
            list.sort()
            rig.data['snappable_modules'] = list

    pbones = rig.pose.bones
    for pbone in pbones:
        prop_list = pbone.keys()
        prop_list.sort()

    if 'temp' in rig.data:
        del rig.data['temp']

    # save default values of all props
    prop_info = []

    for pbone in pbones:
        for key in pbone.keys():
            if key != '_RNA_UI':
                info = {'bone': pbone.name, 'key': key, 'value': pbone[key]}
                prop_info.append(info)

    rig.data['prop_defaults'] = prop_info

    # rig has been generated successfuly
    rig.data['GYAZ_rig_generated'] = 1


def root_bone(shape_collection):
    
    rig = bpy.context.object

    name = 'root'
    bpy.ops.object.mode_set(mode='EDIT')
    ebone = rig.data.edit_bones.new(name=name)
    ebone.head = Vector((0, 0, 0))
    ebone.tail = ebone.head + Vector((0, Constants.root_size, 0))
    
    bone_settings(shape_collection=shape_collection, 
                  bone_name=name, 
                  layer_index=Constants.root_layer, 
                  lock_scale=True,  
                  bone_shape_name='master', 
                  bone_shape_pos='HEAD',
                  bone_shape_manual_scale=1
                  )

    name = 'root_extract'
    bpy.ops.object.mode_set(mode='EDIT')
    ebone = rig.data.edit_bones.new(name=name)
    ebone.head = Vector((0, 0, 0))
    ebone.tail = ebone.head + Vector((0, Constants.root_extract_size, 0))
    ebone.parent = rig.data.edit_bones['root']
                  
    bone_settings(bone_name=name, 
                  layer_index=Constants.misc_layer, 
                  lock_loc=True,
                  lock_rot=True,
                  lock_scale=True
                  )
