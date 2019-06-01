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
from .. functions_draw import *
import traceback
    
class EditWeights(bpy.types.Operator):
    bl_idname = "object.coa_edit_weights"
    bl_label = "Select Child"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def __init__(self):
        self.sprite_object_name = None
        self.obj_name = None
        self.shadeless = False
        self.armature_name = None
        self.active_object_name = None
        self.selected_objects = []
        self.object_color_settings = {}
        self.use_unified_strength = False
        self.non_deform_bones = []
        self.deform_bones = []

    def armature_set_mode(self,context,mode,select):
        armature = bpy.data.objects[self.armature_name]
        armature.select = select
        active_object_name = context.scene.objects.active.name
        context.scene.objects.active = armature
        bpy.ops.object.mode_set(mode=mode)

        context.scene.objects.active = bpy.data.objects[active_object_name]

    def select_bone(self):
        armature = bpy.data.objects[self.armature_name]
        for bone in armature.data.bones:
            bone.select = False
        armature.data.bones.active = None

        for i,vertex_group in enumerate(bpy.data.objects[self.obj_name].vertex_groups):
            if vertex_group.name in armature.data.bones:
                bpy.data.objects[self.obj_name].vertex_groups.active_index = i
                bone = armature.data.bones[vertex_group.name]
                armature.data.bones.active = bone
                break

    def exit_edit_weights(self,context):
        tool_settings = context.scene.tool_settings
        tool_settings.unified_paint_settings.use_unified_strength = self.use_unified_strength
        set_local_view(False)
        obj = bpy.data.objects[self.obj_name]
        obj.hide = False
        obj.select = True
        context.scene.objects.active = obj
        armature = get_armature(get_sprite_object(obj))
        armature.hide = False
        bpy.ops.object.mode_set(mode="OBJECT")
        for i,bone_layer in enumerate(bone_layers):
            armature.data.layers[i] = bone_layer

        for name in self.selected_objects:
            obj = bpy.data.objects[name]
            obj.select = True
        context.scene.objects.active = bpy.data.objects[self.active_object_name]
        self.unhide_non_deform_bones(context)

    def exit_edit_mode(self,context):
        ### remove draw call
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")

        sprite_object = bpy.data.objects[self.sprite_object_name]

        self.exit_edit_weights(context)
        sprite_object.coa_edit_weights = False
        sprite_object.coa_edit_mode = "OBJECT"
        bpy.ops.ed.undo_push(message="Exit Edit Weights")
        self.disable_object_color(False)
        context.active_object.active_material.use_shadeless = self.shadeless
        return {"FINISHED"}

    def modal(self, context, event):
        try:
            if get_local_view(context) == None or (context.active_object != None and context.active_object.mode != "WEIGHT_PAINT") or context.active_object == None:
                return self.exit_edit_mode(context)
        except Exception as e:
            traceback.print_exc()
            self.report({"ERROR"},"An Error occured, please check console for more Information.")
            self.exit_edit_mode(context)

        return {"PASS_THROUGH"}

    def disable_object_color(self,disable):
        sprite_object = get_sprite_object(bpy.context.active_object)
        children = get_children(bpy.context,sprite_object,ob_list=[])
        for obj in children:
            if obj.type == "MESH":
                if len(obj.material_slots) > 0:
                    if disable:
                        self.object_color_settings[obj.name] = obj.material_slots[0].material.use_object_color
                        obj.material_slots[0].material.use_object_color = not disable
                    else:
                        obj.material_slots[0].material.use_object_color = self.object_color_settings[obj.name]

    def unhide_deform_bones(self,context):
        armature = bpy.data.objects[self.armature_name]
        for bone in armature.data.bones:
            if bone.hide and bone.use_deform:
                self.deform_bones.append(bone)
                bone.hide = False

    def hide_deform_bones(self,context):
        for bone in self.deform_bones:
            bone.hide = True

    def hide_non_deform_bones(self,context):
        armature = bpy.data.objects[self.armature_name]
        for bone in armature.data.bones:
            if not bone.hide and not bone.use_deform:
                self.non_deform_bones.append(bone)
                bone.hide = True

    def unhide_non_deform_bones(self,context):
        for bone in self.non_deform_bones:
            bone.hide = False


    def create_armature_modifier(self,context,obj,armature):
        for mod in obj.modifiers:
            if mod.type == "ARMATURE":
                return mod
        mod = obj.modifiers.new("Armature","ARMATURE")
        mod.object = armature
        return mod

    def invoke(self, context, event):
        if context.active_object == None or context.active_object.type != "MESH":
            self.report({"ERROR"},"Sprite is not selected. Cannot go in Edit Mode.")
            return{"CANCELLED"}
        obj = bpy.data.objects[context.active_object.name]
        self.obj_name = context.active_object.name
        self.sprite_object_name = get_sprite_object(context.active_object).name
        sprite_object = bpy.data.objects[self.sprite_object_name]
        if get_armature(sprite_object) == None or get_armature(sprite_object) not in context.visible_objects:
            self.report({'WARNING'},'No Armature Available or Visible')
            return{"CANCELLED"}
        self.armature_name = get_armature(sprite_object).name
        armature = bpy.data.objects[self.armature_name]

        self.shadeless = context.active_object.active_material.use_shadeless
        context.active_object.active_material.use_shadeless = True

        self.create_armature_modifier(context,obj,armature)

        scene = context.scene
        tool_settings = scene.tool_settings
        self.use_unified_strength = tool_settings.unified_paint_settings.use_unified_strength
        tool_settings.unified_paint_settings.use_unified_strength = True

        self.disable_object_color(True)
        context.window_manager.modal_handler_add(self)

        self.active_object_name = context.active_object.name
        
        for obj in context.selected_objects:
            self.selected_objects.append(obj.name)
        
        sprite_object.coa_edit_weights = True
        sprite_object.coa_edit_mode = "WEIGHTS"
        
        
        self.hide_non_deform_bones(context)
        self.unhide_deform_bones(context)
            
        if armature != None:
            self.armature_set_mode(context,"POSE",True)
            global bone_layers
            bone_layers = []
            for i,bone_layer in enumerate(armature.data.layers):
                bone_layers.append(bone_layer)
                armature.data.layers[i] = True
            self.select_bone()
            
        sprite = context.active_object
        if sprite.parent != get_armature(sprite_object):
            create_armature_parent(context)

        set_local_view(True)
        
        context.scene.tool_settings.use_auto_normalize = True
        
        ### zoom to selected mesh/sprite
        for obj in bpy.context.selected_objects:
            obj.select = False
        obj = bpy.data.objects[self.obj_name]    
        obj.select = True
        context.scene.objects.active = obj
        bpy.ops.view3d.view_selected()
        
        ### set uv image
        bpy.context.space_data.viewport_shade = 'TEXTURED'
        set_uv_image(obj)
        
        ### enter weights mode
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        
        
        ### start draw call
        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        return {"RUNNING_MODAL"}
    
    
    def draw_callback_px(self):
        draw_edit_mode(self,bpy.context,color=[0.367356, 1.000000, 0.632293, 1.000000],text="Edit Weights Mode",offset=-5)
            