# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

# Scene Logic for Exporting Blender Scenes
# By Matti 'Menithal' Lahtinen

import bpy
import uuid
import re
import os
import json

from mathutils import Quaternion
from math import sqrt
from hashlib import md5, sha256
from copy import copy, deepcopy

from hifi_tools.utils.helpers import *

EXPORT_VERSION = 84

def center_all(blender_object):
    for child in blender_object.children:
        select(child)
            
    blender_object.select = True
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    blender_object.select = False   


def select(blender_object):
    for child in blender_object.children:
        select(child)            
                
    blender_object.select = True

# Can't use name to define the unique id as this is not shared between instancing, instead going to go through 
# Each modifier in order and hope the order is the same
# TODO: Separate to utility perhaps?
def generate_unique_id_modifier(modifiers):
    unique_name = ""
    for index, modifier in enumerate(modifiers):
        print(str(index), "Iterating", modifier.name, modifier.type)
        # for use only 
        old_unique = unique_name + "|name>" + modifier.name
       
        unique_name = unique_name + "|" + str(index) + "|m:" + modifier.type
        if modifier.type == 'EDGE_SPLIT':
            print("Edge split")
            unique_name = unique_name + "|sa:" + str(modifier.split_angle)
            if modifier.use_apply_on_spline:
                unique_name = unique_name + "|uaos"
            if modifier.use_edge_angle:
                unique_name = unique_name + "|ua"
            if modifier.use_edge_sharp:
                unique_name = unique_name + "|us"
        elif modifier.type == 'MIRROR':
            print("Mirror")
            if modifier.mirror_object:
                unique_name = unique_name + '|m:' + modifier.mirror_object.name      
            if modifier.use_x:
                unique_name = unique_name + "|x"
            if modifier.use_y:
                unique_name = unique_name + "|y"
            if modifier.use_z:
                unique_name = unique_name + "|z"
            if modifier.use_mirror_u:
                unique_name = unique_name + "|u"
            if modifier.use_mirror_v:
                unique_name = unique_name + "|v"
            if modifier.use_clip:
                unique_name = unique_name + "|c"
            if modifier.use_mirror_vertex_groups:
                unique_name = unique_name + "|mvg"
            if modifier.use_mirror_merge:
                unique_name = unique_name + "|mm:" + str(modifier.merge_threshold)
        elif modifier.type == 'ARRAY':

            print("Array")
            if modifier.fit_type == 'FIXED_COUNT':
                unique_name = unique_name + '|c:' + str(modifier.count)
            if modifier.fit_type == 'FIT_LENGTH':
                unique_name = unique_name + '|fl:' + str(modifier.fit_length)
            if modifier.fit_type == 'FIT_CURVE' and modifier.curve:
                unique_name = unique_name + '|cr:' + str(modifier.curve.name)
            if modifier.use_merge_vertices:
                unique_name = unique_name + '|mt:' + str(modifier.merge_threshold)
            if modifier.use_constant_offset:
                unique_name = unique_name + '|cod:' + str(modifier.constant_offset_display.to_tuple())
            # This one behaves differently than above in blender, so custom method
            if modifier.use_relative_offset:
                rod = (modifier.relative_offset_displace[0], modifier.relative_offset_displace[1], modifier.relative_offset_displace[2])
                unique_name = unique_name + '|rod:' + str(rod)

            if modifier.start_cap:
                unique_name = unique_name + '|sc:' + modifier.start_cap.name
            if modifier.end_cap:
                unique_name = unique_name + '|ec:' + modifier.end_cap.name
            if modifier.use_object_offset and modifier.offset_object:
                unique_name = unique_name + '|oo:' + modifier.offset_object.name
        else:
            # TODO: Add Support to subsurface / solidify
            unique_name = old_unique
            print( 'Unsupported modifier ', modifier.name, modifier.type, ' Skipping')
    
    print(unique_name)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_name))


def apply_all_modifiers(modifiers):
     for modifier in modifiers:
        #Apply all but Armature
        if modifier.type != 'ARMATURE':
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)

def set_relative_to_parent(blender_object, json_data):
    if blender_object.parent:
        parent = blender_object.parent
        
        parent_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, parent.name)
        
        parent_orientation = quat_swap_nzy(relative_rotation(blender_object))
        parent_position = swap_nzy(relative_position(blender_object))
        
        json_data["position"] = {
            'x': parent_position.x,
            'y': parent_position.y,
            'z': parent_position.z
        }
        
        json_data["rotation"] = {
            'x': parent_orientation.x,
            'y': parent_orientation.y,
            'z': parent_orientation.z,
            'w': parent_orientation.w
        }
        
        json_data["parentID"] = str(parent_uuid)

    return json_data
        

def parse_object(blender_object, path, options):  
    # Store existing rotation mode, just in case.
    json_data = None
    # Make sure context is quaternion for the models
    if options.remove_trailing:
        name = re.sub(r'\.\d{3}$', '', blender_object.name)
    else:
        name = blender_object.name

    # If you ahve an object thats the same mesh, but different object: All Objects will use this as reference allowing for instancing.
    uuid_gen = uuid.uuid5(uuid.NAMESPACE_DNS, blender_object.name)
    scene_id = str(uuid_gen)
    
    bo_type = blender_object.type
    
    stored_rotation_mode = str(blender_object.rotation_mode)
    blender_object.rotation_mode = 'QUATERNION'
    orientation = quat_swap_nzy(blender_object.rotation_quaternion) 
    position = swap_nzy(blender_object.location)
    
    if bo_type == 'MESH':  
        original_object = None
        blender_object.select = True      
        uid = ""
        reference_name = blender_object.data.name
        
        # TODO: If Child of armature, skip logic

        # Here comes the fun part: Apply all modifiers prior to using them in the instance
        if len(blender_object.modifiers) > 0: 
            # Lets do a LOW-LEVEL duplicate, too much automation in duplicate         
            clone = blender_object.copy()
            original_object = blender_object
            clone.data = blender_object.data.copy()
            bpy.context.scene.objects.link(clone)
            clone.select = True
            original_object.select = False
            
            uid = "-" + generate_unique_id_modifier(clone.modifiers)
            print(uid)
            bpy.context.scene.objects.active = clone
            apply_all_modifiers(clone.modifiers)
            blender_object = clone

            clone.select = True

        #temp_dimensions = Vector(blender_object.dimensions)
        dimensions = swap_yz(blender_object.dimensions)
        
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        print("Storing existing rotation")
        temp_rotation = Quaternion(blender_object.rotation_quaternion)
        # Temporary Rotate Model to a zero rotation so that the exported model rotation is normalized.
        blender_object.rotation_quaternion = Quaternion((1,0,0,0))
        
        #blender_object.dimensions = Vector((1,1,1))

        # TODO: Option to also export via gltf instead of fbx
        # TODO: Add Option to not embedtextures / copy paths
        file_path = path + reference_name + uid + ".fbx"

        atp_enabled = options.atp

        bpy.ops.export_scene.fbx(filepath=file_path, version='BIN7400', embed_textures=True, path_mode='COPY',
                            use_selection=True, axis_forward='-Z', axis_up='Y')

        # Restore earlier rotation
        # blender_object.dimensions = temp_dimensions
        blender_object.rotation_quaternion = temp_rotation      
             
        if options.atp:
            if options.use_folder:
                last_folder_re = re.search(r"(?:=\/|\\)?([a-zA-Z0-9_\-]+)(?:\/|\\)?$", path)
                start = last_folder_re.start(0)+1
                end = last_folder_re.end(0)

                last_folder = path[start:end]
            else:
                last_folder = ""               
                
            model_url = "atp:/"+ last_folder + reference_name + uid + '.fbx'
        else:
            model_url = options.url_override + reference_name +  uid + '.fbx'


        json_data = {
            'name': name,
            'id': scene_id,
            'type': 'Model',
            'modelURL': model_url,
            'position': {
                'x': position.x,
                'y': position.y,
                'z': position.z
            },
            'rotation': {
                'x': orientation.x,
                'y': orientation.y,
                'z': orientation.z,
                'w': orientation.w
            },
            'dimensions':{
                'x': dimensions.x,
                'y': dimensions.y,
                'z': dimensions.z
            },           
            "shapeType": "static-mesh",
            'userData': '{"blender_export":"' + scene_id +'"}, "grabbable_key":["grabbable":false]}'
        }         
        
        json_data = set_relative_to_parent(blender_object, json_data)

        if original_object:
            bpy.ops.object.delete()
            blender_object = original_object
            blender_object.select = True
            
    elif bo_type == 'LAMP':
        print(name, 'is Light')
        
        # Hifi 5, Blender 3.3
        light = blender_object.data
        color = blender_object.color
        falloff = sqrt(light.distance)
        distance = light.distance
        
        json_data = {
            'name': name,
            'id': scene_id,
            'type': 'Light',
            'position': {
                'x': position.x,
                'y': position.y,
                'z': position.z
            },
            'color':{
                'blue': int(color[2] * 255),
                'green': int(color[1] * 255),
                'red': int(color[0] * 255)
            },
            'dimensions':{
                'x': distance,
                'y': distance,
                'z': distance,
            },
            'falloffRadius': falloff,
            'rotation': {
                'x': orientation.x,
                'y': orientation.y,
                'z': orientation.z,
                'w': orientation.w
            },

            'intensity': light.energy,
            'userData': '{"blender_export":"' + scene_id +'", "grabbable_key":["grabbable":false]}'
        }   
            
        if light.type is 'POINT':
            blender_object.select = True 
        
        # TODO: Spot Lights require rotation by 90 degrees to get pointing in the right direction        
    elif bo_type == 'ARMATURE': # Same as Mesh actually.
        # Get all children export as a single file.
        print(name, 'is armature. Not Supported as of the moment')

    elif bo_type == 'EMPTY':
        print(name, 'Adding an Empty')

        json_data = { 
            'id': scene_id,
            'visible': False,
            'collisionless': True,
            'ignoreForCollisions': True,
            'position': {
                'x': position.x,
                'y': position.y,
                'z': position.z
            },
            'dimensions':{
                'x': 1,
                'y': 1,
                'z': 1,
            },
            'name': 'EMPTY-' + name,
            "color": {
                "blue": 128,
                "green": 0,
                "red": 255
            },
            "shape": "Cube",
            "type": "Box",
            'userData': '{"blender_export":"' + scene_id +'", "grabbableKey":{"grabbable":false,"ignoreIK":false}}',
        }

        json_data = set_relative_to_parent(blender_object, json_data)

    else:
        print('Skipping unsupported feature', name, bo_type)
    
    
    # Restore object's rotation mode
    print(blender_object)
    if blender_object:
        blender_object.rotation_mode = stored_rotation_mode
    
    bpy.ops.object.select_all(action = 'DESELECT')
    return json_data

# Rotation is based on the rotaiton of the parent and self. 
def relative_rotation(parent_object):
    if not parent_object.parent:
        return parent_object.rotation_quaternion
    else:
        rotation = relative_rotation( parent_object.parent)
        current = parent_object.rotation_quaternion
        current.invert() 
        print('rotation test', current)
       
        return rotation * current


def relative_position(parent_object):
    if parent_object.parent is not None:
        return relative_rotation(parent_object.parent) * parent_object.location - relative_position(parent_object.parent)
    else:
        return parent_object.location



def write_file(context):
    current_scene = bpy.context.scene
    read_scene = current_scene

    # Creating a temp copy to do the changes in.
    if context.clone_scene:
        bpy.ops.scene.new(type='FULL_COPY')
        read_scene = bpy.context.scene # sets the new scene as the new scene
        read_scene.name = 'Hifi_Export_Scene'
    
    # Make sure we are in Object mode    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Deselect all objects
    bpy.ops.object.select_all(action = 'DESELECT')

    # Clone Scene. Then select scene. After done delete scene
    path = os.path.dirname(os.path.realpath(context.filepath)) + '/'
    
    ## Parse the marketplace url
    url = ""

    if not context.atp:
        url = context.url_override
        if "https://highfidelity.com/marketplace/items/" in url:
            
            marketplace_id = url.replace("https://highfidelity.com/marketplace/items/", "").replace("/edit","").replace("/","")
            
            url = "http://mpassets.highfidelity.com/" + marketplace_id + "-v1/"
        
        if not url.endswith('/'):    
            url = url + "/"
    
    entities = []

    # Duplicate list to break reference as we may do updates to the scene
    current_scene_objects = list(read_scene.objects)
    for blender_object in current_scene_objects:
        print(len(current_scene_objects))
        parsed = parse_object(blender_object, path, context)
        
        if parsed:
            entities.append(parsed)        

    # Delete Cloned scene
    #     
    if context.clone_scene:
        bpy.ops.scene.delete()
    
    hifi_scene = {
        'Version': EXPORT_VERSION,
        'Entities': entities
    }
    
    data = json.dumps(hifi_scene, indent=4)
    
    file = open(context.filepath, "w")
    
    try: 
        file.write(data)
    except e:
        print('Could not write to file.', e)
    finally:
        file.close()