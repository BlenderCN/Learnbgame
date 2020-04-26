'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    
import bpy
import bpy_extras
import bpy_extras.view3d_utils
from math import radians
import mathutils
from mathutils import Vector, Matrix, Quaternion, Euler
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent
from collections import OrderedDict

def get_addon_prefs(context):
    addon_name = __name__.split(".")[0]
    user_preferences = context.preferences
    addon_prefs = user_preferences.addons[addon_name].preferences
    return addon_prefs

def get_categories(self,context):
    list = []
    item = ("DEFAULT","All Assets - Category","Displays all Assets","GROUP",0)
    list.append(item)
    for i,category in enumerate(self.categories):
        item = (category.name.upper(),category.name + " - Category",category.name,"",i+1)
        list.append(item)
    return list    

def get_thumbnails_in_folder(self,context):
    filename = os.path.basename(bpy.data.filepath.split(".blend")[0])+".thumbs"
    preview_path = os.path.join(os.path.dirname(bpy.data.filepath),filename)
    image_paths = []
    if os.path.isdir(preview_path):
        for fn in os.listdir(preview_path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn.split(".png")[0])
    return image_paths

def update_category_display(self,context):
    wm = bpy.context.window_manager
    scene = context.scene
    for i in range(len(self.display_asset_list)):
        self.display_asset_list.remove(0)
    
    
    for i, asset_item in enumerate(self.asset_list):
        if self.categories_enum in asset_item.categories or self.categories_enum == "DEFAULT":
            item = self.display_asset_list.add()
            item.name = asset_item.name
            item.type = asset_item.type
            
    if self.display_asset_list_index > len(self.display_asset_list)-1:
        self.display_asset_list_index = max(len(self.display_asset_list)-1,0)
    if len(self.display_asset_list) > 0 and self.display_asset_list_index < 0:
        self.display_asset_list_index = 0  
    
    update_asset_list_index(self,context)
    
    #if self.categories_enum_prev != self.categories_enum:
    wm.asset_previews_loaded = False
    if len(get_thumbnails_in_folder(self,context)) > 0 and len(wm.asset_sketcher.display_asset_list) > 0:
        if wm.asset_preview_icon in get_thumbnails_in_folder(self,context):
            wm.asset_preview_icon = wm.asset_preview_icon
            
    
    self.categories_enum_prev = self.categories_enum
    context.scene.asset_sketcher.categories_enum_prev = self.categories_enum
        
def update_asset_list_index(self,context):
    wm = context.window_manager
    asset_list_len = len(self.display_asset_list)
    if asset_list_len > 0 and self.display_asset_list_index < asset_list_len and self.display_asset_list_index != -1:
        display_item_name = self.display_asset_list[self.display_asset_list_index].name
        
        for i,item in enumerate(self.asset_list):
            if item.name == display_item_name:
                self.asset_list_index = i
                if item.name in get_thumbnails_in_folder(self,context):
                    wm.asset_preview_icon = item.name


### blender version check function. needed for raycast function because the api changed for 2.77
def b_version_bigger_than(version):
    return bpy.app.version > version

### snap value to a given grid
def snap_value(value,grid=1):
    return round(value/grid) *grid

#raycast that behaves the same in "every" blender version
def ray_cast_any_version(start,end):
    result= None
    if b_version_bigger_than((2,76,0)):
        delta = (end-start)
        ray_data = bpy.context.scene.ray_cast(start,delta.normalized(),delta.length)
        result = [ray_data[0],ray_data[4],ray_data[5],ray_data[1],ray_data[2],ray_data[3]]
    else:
        delta = end-start
        ray_data = bpy.context.scene.ray_cast(start,start+delta.normalized()*distance)
        result = [ray_data[0],ray_data[1],ray_data[2],ray_data[3],ray_data[4],None]
    return result

#raycast that penetrates through multiple objects
def xray_cast2(start, end, depth = -1, delta = 0.0001, obj=None):
    hit_dict = OrderedDict()
    ray_delta = (end-start).normalized()*delta
    ray_start = start
    #check if ray_start hasn't passed the endpoint
    while (end-start).dot(end-ray_start) > 0 and len(hit_dict) != depth:
        ray_data = ray_cast_any_version(ray_start, end)
        if ray_data[0]:
            if ray_data[1].name not in hit_dict:
                hit_dict[ray_data[1].name] = ray_data
            ray_start = ray_data[3]+ray_delta
        else:
            break
    return list(hit_dict.values())

def xray_cast(start, end, depth = -1, delta = 0.0001, obj=None, ignore_assets=True):
    hit_dict = OrderedDict()
    ray_delta = (end-start).normalized()*delta
    ray_start = start
    #check if ray_start hasn't passed the endpoint
    depth2 = 0
    while (end-start).dot(end-ray_start) > 0 and len(hit_dict) != depth and depth2 < 15:
        ray_data = ray_cast_any_version(ray_start, end)
        if ray_data[0]:
            if str(ray_data[3]) not in hit_dict and "as_preview" not in ray_data[1]:
                if "as_asset" not in ray_data[1] or not ignore_assets:
                    hit_dict[str(ray_data[3])] = ray_data
            ray_start = ray_data[3]+ray_delta
        else:
            break
        depth2 += 1
    return list(hit_dict.values())

def get_zoom(self,context):
    if hasattr(context.space_data,"region_3d"):
        return context.space_data.region_3d.view_distance
    else:
        return 1.0

### function to shoot a raycast from mouse position    
def project_cursor(self,context,event,depth,custom_position=None,ignore_assets=True):
    if event.ctrl:
        ignore_assets = False
    view_ray = get_view_ray(self,context,event)
    if view_ray != None:
        return xray_cast(view_ray[0],view_ray[1],depth=depth,ignore_assets=ignore_assets)
    else:
        return []            

def get_view_ray(self,context,event):
    scene = context.scene
    wm = context.window_manager
    
    mouse_coord = Vector((event.mouse_region_x, event.mouse_region_y))
    
    transform = bpy_extras.view3d_utils.region_2d_to_location_3d
    region = context.region
    space_data = context.space_data
    if hasattr(space_data,"region_3d"):
        rv3d = space_data.region_3d
        
        ray_start = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_coord)
        
        ray_end = transform(region, rv3d, mouse_coord, rv3d.view_location)
        ray_end = ray_start+(ray_end-ray_start).normalized()*10000   
        
        return ray_start,ray_end
    else:
        return None
    

### load and save function to load properties into window manager and save them always in scene[0]
### that way properties can be accesses globally in the window manager and be apparent in all scenes.
def save_load_asset_list(context,mode="SAVE",src_custom=None,dst_custom=None,clean_collection_props=True):
    wm = context.window_manager
    scene = bpy.data.scenes[0]
    
    exclude_properties = ["merge_object"]
    
    ### set src and destination properties
    if mode == "SAVE":
        src_asset_sketcher = wm.asset_sketcher
        dst_asset_sketcher = scene.asset_sketcher
    elif mode == "LOAD": 
        src_asset_sketcher = scene.asset_sketcher
        dst_asset_sketcher = wm.asset_sketcher
    elif mode == "IMPORT":
        src_asset_sketcher = src_custom
        dst_asset_sketcher = dst_custom
                    
    for attr in src_asset_sketcher.bl_rna.properties.keys():
        ### feed dst properties with src properties
        src_prop = getattr(src_asset_sketcher,attr)
        if str(type(src_prop)) != "<class 'bpy_prop_collection_idprop'>" and mode != "IMPORT" and attr not in exclude_properties:
            if attr != "rna_type":
                #setattr(dst_asset_sketcher, attr, src_prop)
                dst_asset_sketcher[attr] = src_prop
        ### if property is asset list, iterate over items in asset list and copy    
        elif str(type(src_prop)) == "<class 'bpy_prop_collection_idprop'>" and attr != "rna_type" and attr not in exclude_properties:
            src_prop
            dst_prop = getattr(dst_asset_sketcher,attr)
            
            if clean_collection_props: ### clean old list. needed if appending is not used
                for i in range(len(dst_prop)):
                    dst_prop.remove(0)
                    
            for src_item in src_prop:
                if src_item.name not in dst_prop: ### only add new item if name does not exist
                    dst_item = dst_prop.add()
                    
                    for key,value in src_item.items():
                        dst_item[key] = value
    
    ### update display template list with resetting the categories enum prop                
    wm.asset_sketcher.categories_enum = wm.asset_sketcher.categories_enum                