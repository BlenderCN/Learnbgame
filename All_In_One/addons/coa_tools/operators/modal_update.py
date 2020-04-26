'''
Copyright (C) 2015 Andreas Esau
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
from mathutils import Vector, Matrix, Quaternion
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent
from .. functions import *


######################################################################################################################################### Cutout Animatin Tools Modal Operator    
class COAModal(bpy.types.Operator):
    bl_idname = "wm.coa_modal"
    bl_label = "Cutout Animation Tools Modal"
    bl_options = {"REGISTER","INTERNAL"}
    
    
    def __init__(self):
        self.sprite_object = None
        self.value = ""
        self.value_hist = ""
        self.type_hist = ""
        self.value_pressed = False
        self.scaling = False
        self.obj_mode_hist = "OBJECT"
        self.bone_transformation = False
        
    def set_frame_bounds_and_actions(self,context):
        scene = context.scene
        if len(self.sprite_object.coa_anim_collections) > 2:
            scene.frame_start = self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index].frame_start
            scene.frame_end = self.sprite_object.coa_anim_collections[self.sprite_object.coa_anim_collections_index].frame_end
        #set_action(context)
    
    
    def check_event_value(self,event):
        if event.value == "PRESS" and self.value_hist != "PRESS":#and self.value_hist in ["RELEASE","NOTHING"]:
            self.value_pressed = True
            return "JUST_PRESSED"
        elif event.value != "RELEASE" and self.value_pressed:
            return "PRESSED"
        elif event.value == "RELEASE" and (self.value_hist == "PRESS" or self.value_hist == "NOTHING"):
            self.value_pressed = False
            return "JUST_RELEASED"
        else:
            return "RELEASED"
    
    def set_scaling(self,obj,event):
        if obj != None and obj.mode == "EDIT":
            if event.type == "S":
                self.scaling = True
    def check_scaling(self,obj,event):
        if self.scaling:
            if event.value == "RELEASE":
                if event.type == "LEFTMOUSE":
                    self.scaling = False
                    return "SCALE_APPLIED"
                elif event.type in ["RIGHTMOUSE","ESC"]:
                    self.scaling = False
                    return "SCALE_CANCELLED"
                
    def set_view_front(self,context):
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        region = space.region_3d
                        region.view_rotation = Quaternion((0.7071,0.7071,-0.0,-0.0))
    
    def update_bone_group_color(self,context):
        active_object = context.active_object
        suffix = "_group_color"
        if active_object != None and active_object.type == "ARMATURE":
            for bone in active_object.pose.bones:
                custom_shape = bone.custom_shape
                if custom_shape != None and bone.bone_group != None:
                    mat_name = bone.bone_group.name+"_group_color"
                    if mat_name in bpy.data.materials:
                        material = bpy.data.materials[mat_name]
                    else:
                        material = bpy.data.materials.new(mat_name)
                            
                    if len(custom_shape.material_slots) == 0:
                        custom_shape.data.materials.append(material)
                    else:
                        custom_shape.material_slots[0].material = material    
                    
                    material.diffuse_color = bone.bone_group.colors.normal
                elif custom_shape != None:
                    if len(custom_shape.material_slots) > 0:
                        custom_shape.material_slots[0].material = None
            
            for bone_group in active_object.pose.bone_groups:
                if (bone_group.name+suffix) in bpy.data.materials:
                    material = bpy.data.materials[bone_group.name+suffix]
                    if material.diffuse_color != bone_group.colors.normal:
                        material.diffuse_color = bone_group.colors.normal
    
            
    def modal(self,context,event):
        ### execute only if an event pressed is triggered
        active_object = context.active_object

        if self.check_event_value(event) == "JUST_PRESSED":
            wm = context.window_manager
            self.sprite_object = get_sprite_object(context.active_object)
            
            self.set_scaling(active_object,event)
            
            screen = context.screen
            if screen.coa_view == "2D":
                set_middle_mouse_move(True)
                self.set_view_front(context)
            elif screen.coa_view == "3D":
                set_middle_mouse_move(False)
                
        elif self.check_event_value(event) == "JUST_RELEASED":
            obj = active_object
            self.update_bone_group_color(context)
            
            screen = context.screen
            if "coa_init_fullscreen" not in screen:
                if "-nonnormal" in context.screen.name:
                    context.screen.coa_view = bpy.data.screens[context.screen.name.split("-nonnormal")[0]].coa_view
                if screen.coa_view == "2D":
                    set_middle_mouse_move(True)
                    self.set_view_front(context)
                elif screen.coa_view == "3D":
                    set_middle_mouse_move(False)
                screen["coa_init_fullscreen"] = True    
                
                
            if active_object != None and "coa_sprite" in active_object and active_object.mode == "OBJECT":
                if obj.coa_alpha != obj.coa_alpha_last:
                    set_alpha(obj,bpy.context,obj.coa_alpha)
                    obj.coa_alpha_last = obj.coa_alpha
                if obj.coa_z_value != obj.coa_z_value_last:
                    set_z_value(context,obj,obj.coa_z_value)
                    obj.coa_z_value_last = obj.coa_z_value
                if obj.coa_modulate_color != obj.coa_modulate_color_last:
                    set_modulate_color(obj,context,obj.coa_modulate_color)
                    obj.coa_modulate_color_last = obj.coa_modulate_color
                
                ### leaving object edit mode
#                if obj.type == "MESH" and self.obj_mode_hist == "EDIT" and obj.mode == "OBJECT":
#                    set_uv_default_coords(context,obj)
#                    ### Store sprite dimension in coa_sprite_dimension when mesh is rescaled
#                    for obj in context.selected_objects:
#                        if obj != None and "coa_sprite":
#                            local_dimensions = get_local_dimension(obj)
#                            if local_dimensions != None:
#                                obj.coa_sprite_dimension = Vector((local_dimensions[0],0,local_dimensions[1]))
            
            ### will be executed when leaving armature edit mode                
            if get_sprite_object(obj)!= None and obj != None and obj.type == "ARMATURE" and self.obj_mode_hist == "EDIT" and obj.mode != "EDIT":
                ### fix bone roll to properly export
                if obj.hide == False:
                    fix_bone_roll(obj)
            
            if obj != None:        
                self.obj_mode_hist = str(obj.mode)
                
        if active_object != None and (self.check_event_value(event) in ["JUST_PRESSED","PRESSED"] and event.type == "G") and active_object.type == "ARMATURE" and active_object.mode == "POSE":
            bpy.context.window_manager.coa_update_uv = True
        elif self.check_event_value(event) == "JUST_RELEASED" and bpy.context.window_manager.coa_update_uv:  
            bpy.context.window_manager.coa_update_uv = False
                    
        #print("value = ",event.value,"value_hist = ",self.value_hist)
            
        if self.check_scaling(active_object,event) == "SCALE_APPLIED" and active_object != None:
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")
            if get_local_dimension(active_object) != None:
                active_object.coa_sprite_dimension = Vector((get_local_dimension(active_object)[0],0,get_local_dimension(active_object)[1]))
        ###
        self.value_hist = str(event.value)
        self.type_hist = str(event.type)
        
        return{'PASS_THROUGH'}
        
    def execute(self,context):
        wm = context.window_manager
        if not context.window_manager.coa_running_modal:
            context.window_manager.coa_running_modal = True
            wm.modal_handler_add(self)
        return{'RUNNING_MODAL'} 


