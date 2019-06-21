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
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
from .. functions import *

class ChangeZOrdering(bpy.types.Operator):
    bl_idname = "coa_tools.change_z_ordering"
    bl_label = "Change Zordering"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    active_sprite = StringProperty()
    all_sprites = StringProperty()
    index = IntProperty()
    direction = StringProperty() ## UP - DOWN
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        active_sprite = scene.objects[self.active_sprite]
        
        all_sprites = []
        for name in eval(self.all_sprites):
            all_sprites.append(scene.objects[name])
            
        if self.direction == "UP":
            next_index = max(self.index - 1 , 0)
        elif self.direction == "DOWN":
            next_index = min(self.index + 1 , len(all_sprites)-1)
               
        next_sprite = all_sprites[next_index]
        
        if active_sprite.coa_z_value == next_sprite.coa_z_value:
            for i,child in enumerate(all_sprites):
                if child == active_sprite:
                    child.coa_z_value = child.coa_z_value
                if self.direction == "DOWN":
                    if i > self.index:
                        child.coa_z_value -= 1
                if self.direction == "UP":
                    if i < self.index:
                        child.coa_z_value += 1
                
        
        active_loc_y = active_sprite.location[1]
        next_loy_y = next_sprite.location[1]
        active_sprite.location[1] = next_loy_y
        next_sprite.location[1] = active_loc_y
        active_z = active_sprite.coa_z_value
        next_z = next_sprite.coa_z_value
        active_sprite.coa_z_value = next_z
        next_sprite.coa_z_value = active_z
        
        return {"FINISHED"}
        

class ViewSprite(bpy.types.Operator):
    bl_idname = "coa_tools.view_sprite"
    bl_label = "View Sprite"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    type = StringProperty(default="VIEW_SELECTED")
    name = StringProperty(default="")
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        active_object = bpy.data.objects[context.active_object.name]
        active_object_mode = active_object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        
        sprite_object = get_sprite_object(context.scene.objects[self.name])
        children = get_children(context,sprite_object,ob_list=[])
        selected_objects = []
        
        
        if self.type == "VIEW_ALL":
            for obj in context.selected_objects:
                selected_objects.append(obj)
                
                
            for obj in context.scene.objects:
                obj.select = False
                
            context.scene.objects.active = context.scene.objects[self.name]
            context.scene.objects[self.name].select = True
            
            for obj in children:    
                obj.select = True
            bpy.ops.view3d.view_selected()
            
            for obj in context.selected_objects:
                if obj not in selected_objects:
                    obj.select = False
            context.scene.objects.active = active_object
            active_object.select = True        
            
        bpy.ops.object.mode_set(mode=active_object_mode)
        return {"FINISHED"}
        