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
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty, PointerProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent
from . functions import *
from . import addon_updater_ops
#from . import preview_collections

bone_layers = []
armature_mode = None
armature_select = False

class ChangeShadingMode(bpy.types.Operator):
    bl_idname = "coa_tools.change_shading_mode"
    bl_label = "Change Shading Mode"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        return {"FINISHED"}
    

class UVData(bpy.types.PropertyGroup):
    uv = FloatVectorProperty(default=(0,0),size=2)

class SlotData(bpy.types.PropertyGroup):
    def change_slot_mesh(self,context):
        obj = self.id_data
        self["active"] = True
        if self.active:
            obj.coa_slot_index = self.index
            hide_base_sprite(obj)
            for slot in obj.coa_slot:
                if slot != self:
                    slot["active"] = False
    
    mesh = bpy.props.PointerProperty(type=bpy.types.Mesh)
    offset = FloatVectorProperty()               
    name = StringProperty()
    active = BoolProperty(update=change_slot_mesh)
    index = IntProperty()

class Event(bpy.types.PropertyGroup):
    name = StringProperty()
    type = EnumProperty(name="Object Type",default="SOUND",items=(("SOUND","Sound","Sound","SOUND",0),("EVENT","Event","Event","PHYSICS",1)))
    value = StringProperty(description="Define which sound or event key is triggered.")

class TimelineEvent(bpy.types.PropertyGroup):
    def change_event_order(self, context):
        timeline_events = self.id_data.coa_anim_collections[self.id_data.coa_anim_collections_index].timeline_events
        for i, event in enumerate(timeline_events):
            event_next = None
            if i < len(timeline_events)-1:
                event_next = timeline_events[i+1]
            if event_next != None and event_next.frame < event.frame:
                timeline_events.move(i+1, i)

    event = CollectionProperty(type=Event)
    frame = IntProperty(default=0, min=0, update=change_event_order)
    collapsed = BoolProperty(default=False)

class AnimationCollections(bpy.types.PropertyGroup):
    def set_frame_start(self,context):
        bpy.context.scene.frame_start = self.frame_start
    def set_frame_end(self,context):
        bpy.context.scene.frame_end = self.frame_end
    
    def check_name(self,context):
        sprite_object = get_sprite_object(context.active_object)
        
        if self.name_old != "" and self.name_change_to != self.name:
            name_array = []
            for item in sprite_object.coa_anim_collections:
                name_array.append(item.name_old)
            self.name_change_to = check_name(name_array,self.name)
            self.name = self.name_change_to

        children = get_children(context,sprite_object,ob_list=[])
        objs = []
        if sprite_object.type == "ARMATURE":
            objs.append(sprite_object)
        for child in children:
            objs.append(child)

        for child in objs:
            action_name = self.name_old + "_" + child.name
            action_name_new = self.name + "_" + child.name

            # if action_name_new in bpy.data.actions:
            #     bpy.data.actions.remove(bpy.data.actions[action_name])
            if action_name_new in bpy.data.actions:
                print(child.name,"",action_name_new , " -- ",action_name_new in bpy.data.actions)
            if action_name_new not in bpy.data.actions and action_name in bpy.data.actions:
                action = bpy.data.actions[action_name]
                action.name = action_name_new
        self.name_old = self.name
        self.id_data.coa_anim_collections_index = self.id_data.coa_anim_collections_index

    name = StringProperty(update=check_name)
    name_change_to = StringProperty()
    name_old = StringProperty()
    action_collection = BoolProperty(default=False)
    frame_start = IntProperty(default=0 ,update=set_frame_start)
    frame_end = IntProperty(default=250 ,min=1,update=set_frame_end)
    timeline_events = CollectionProperty(type=TimelineEvent)
    event_index = IntProperty(default=-1,max=-1)
        

class CutoutAnimationInfo(bpy.types.Panel):
    bl_idname = "cutout_animation_social"
    bl_label = "Info Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Cutout Animation"
    
    @classmethod
    def poll(cls, context):
        ignore_update = addon_updater_ops.updater.json["ignore"] if "ignore" in addon_updater_ops.updater.json else False
        if (addon_updater_ops.updater.update_ready and not ignore_update) or get_addon_prefs(context).show_donate_icon:
            return context
        
    
    def draw(self, context):
        #addon_updater_ops.check_for_update_background()
        
        layout = self.layout
        
        if get_addon_prefs(context).show_donate_icon:
            row = layout.row()
            row.alignment = "CENTER"
            
            pcoll = preview_collections["main"]
            donate_icon = pcoll["donate_icon"]
            twitter_icon = pcoll["twitter_icon"]
            row.operator("coa_operator.coa_donate",text="Show Your Love",icon_value=donate_icon.icon_id,emboss=True)
            row = layout.row()
            row.alignment = "CENTER"
            row.scale_x = 1.75
            op = row.operator("coa_operator.coa_tweet",text="Tweet",icon_value=twitter_icon.icon_id,emboss=True)
            op.link = "https://www.youtube.com/ndee85"
            op.text = "Check out CutoutAnimation Tools Addon for Blender by Andreas Esau."
            op.hashtags = "b3d,coatools"
            op.via = "ndee85"
        
        addon_updater_ops.update_notice_box_ui(self, context)


def enum_sprite_previews(self, context):
    """EnumProperty callback"""
    enum_items = []
    if context is None:
        return enum_items
    if self.coa_type == "MESH":

        # Get the preview collection (defined in register func).
        coa_pcoll = preview_collections["coa_thumbs"]
        
        #thumb_dir_path = bpy.utils.user_resource("DATAFILES","coa_thumbs")
        thumb_dir_path = os.path.join(context.user_preferences.filepaths.temporary_directory,"coa_thumbs")
        
        if os.path.exists(thumb_dir_path):
            # Scan the directory for png files
            image_paths = []
            for fn in os.listdir(thumb_dir_path):
                if fn.lower().endswith(".png") and self.name in fn:
                    image_paths.append(fn)      
            for i, name in enumerate(image_paths):
                if i < self.coa_tiles_x * self.coa_tiles_y:
                    filepath = os.path.join(thumb_dir_path, name)

                    if name in coa_pcoll:
                        thumb = coa_pcoll[name]
                    else:    
                        thumb = coa_pcoll.load(name, filepath, 'IMAGE')
                    enum_items.append((str(i), name, "", thumb.icon_id, i))
    elif self.coa_type == "SLOT":
        for i,slot in enumerate(self.coa_slot):
            if slot.mesh != None:
                img = slot.mesh.materials[0].texture_slots[0].texture.image
                icon = bpy.types.UILayout.icon(img)
                enum_items.append((str(i), slot.mesh.name, "", icon, i))
 
    return enum_items


last_obj = None    
class CutoutAnimationObjectProperties(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Object Properties"
    bl_category = "Cutout Animation"
    
    @classmethod
    def poll(cls, context):
        return True# (context.active_object)
    
    def hide_bone(self,context):
        self.hide = self.coa_hide
    
    def hide_select_bone(self,context):
        self.hide_select = self.coa_hide_select
    
    def hide(self,context):
        if self.hide != self.coa_hide:
            self.hide = self.coa_hide
    def hide_select(self,context):
        if self.coa_hide_select:
            self.select = False
            if context.scene.objects.active == self:
                context.scene.objects.active = self.parent
        self.hide_select = self.coa_hide_select
    
    def update_uv(self,context):
        self.coa_sprite_frame_last = -1
        if self.coa_sprite_frame >= (self.coa_tiles_x * self.coa_tiles_y):
            self.coa_sprite_frame = (self.coa_tiles_x * self.coa_tiles_y) - 1
        update_uv(context,context.active_object)
    
        
    def change_tilesize(self,context):
        obj = context.active_object
        frame = self.coa_sprite_frame
        self.coa_sprite_frame = 0

        update_verts(context,obj)
        update_uv(context,obj)
        
        self.coa_sprite_frame = frame
        self.coa_tiles_changed = True
        
    
    def set_z_value(self,context):
        #obj = context.active_object
        
        if context.scene.objects.active == self:
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":
                    if obj != self:
                        obj.coa_z_value = self.coa_z_value
                    set_z_value(context,obj,self.coa_z_value)
                
            
    def set_alpha(self,context):
        if context.scene.objects.active == self:
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":
                    if obj != self:
                        obj.coa_alpha = self.coa_alpha
                    set_alpha(obj,context,self.coa_alpha)
    
    def set_modulate_color(self,context):
        if context.scene.objects.active == self:
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":
                    if obj != self:
                        obj.coa_modulate_color = self.coa_modulate_color
                    set_modulate_color(obj,context,self.coa_modulate_color)
            
    def set_sprite_frame(self,context):
        if self.coa_type == "MESH":
            self.coa_sprite_frame_last = -1
            self.coa_sprite_frame = int(self.coa_sprite_frame_previews)
            if context.scene.tool_settings.use_keyframe_insert_auto:
                bpy.ops.coa_tools.add_keyframe(prop_name="coa_sprite_frame",interpolation="CONSTANT")
        elif self.coa_type == "SLOT":
            self.coa_slot_index = int(self.coa_sprite_frame_previews)
    
    
    def exit_edit_weights(self,context):
        if not self.coa_edit_weights:
            obj = context.active_object
            if obj != None and obj.mode == "WEIGHT_PAINT":
                bpy.ops.object.mode_set(mode="OBJECT")
    
    def hide_base_sprite(self,context):
        #hide_base_sprite(self)
        hide_base_sprite(context.active_object)
    
    def change_slot_mesh(self,context):
        self.coa_slot_index_last = -1
        self.coa_slot_index_last = self.coa_slot_index
        change_slot_mesh_data(context,self)
        self.data.coa_hide_base_sprite = self.data.coa_hide_base_sprite
    
    def change_edit_mode(self,context):
        if self.coa_edit_mesh == False:
            bpy.ops.object.mode_set(mode="OBJECT")
            set_local_view(False)
    
    def update_filter(self,context):
        pass
    
    def change_direction(self,context):
        set_direction(self)
        self.coa_flip_direction_last = self.coa_flip_direction

    def get_shapekeys(self,context):
        SHAPEKEYS = []
        obj = context.active_object
        if obj.data.shape_keys != None:
            for i,shape in enumerate(obj.data.shape_keys.key_blocks):
                SHAPEKEYS.append((str(i),shape.name,shape.name,"SHAPEKEY_DATA",i))
        return SHAPEKEYS
    
    def select_shapekey(self,context):
        if self.data.shape_keys != None:
            self.active_shape_key_index = int(self.coa_selected_shapekey)
        
    bpy.types.Mesh.coa_hide_base_sprite = BoolProperty(default=False,update=hide_base_sprite,description="Make sure to hide base sprite when adding a custom mesh.")
    
    bpy.types.Object.coa_dimensions_old = FloatVectorProperty()
    bpy.types.Object.coa_sprite_dimension = FloatVectorProperty()
    bpy.types.Object.coa_tiles_x = IntProperty(description="X Tileset",default = 1,min=1,update=change_tilesize)
    bpy.types.Object.coa_tiles_y = IntProperty(description="Y Tileset",default = 1,min=1,update=change_tilesize)
    bpy.types.Object.coa_sprite_frame = IntProperty(description="Frame",default = 0,min=0,update=update_uv)
    bpy.types.Object.coa_sprite_frame_last = IntProperty(description="Frame")
    bpy.types.Object.coa_z_value = IntProperty(description="Z Depth",default=0,update=set_z_value)
    bpy.types.Object.coa_z_value_last = IntProperty(default=0)
    bpy.types.Object.coa_alpha = FloatProperty(default=1.0,min=0.0,max=1.0,update=set_alpha)
    bpy.types.Object.coa_alpha_last = FloatProperty(default=1.0,min=0.0,max=1.0)
    bpy.types.Object.coa_show_bones = BoolProperty()
    bpy.types.Object.coa_filter_names = StringProperty(update=update_filter,options={'TEXTEDIT_UPDATE'})
    bpy.types.Object.coa_favorite = BoolProperty()
    bpy.types.Object.coa_hide_base_sprite = BoolProperty(default=False,update=hide_base_sprite)
    bpy.types.Object.coa_animation_loop = BoolProperty(default=False,description="Sets the Timeline frame to 0 when it reaches the end of the animation. Also works for changing frame with cursor keys.")
    bpy.types.Object.coa_hide = BoolProperty(default=False,update=hide)
    bpy.types.Object.coa_hide_select = BoolProperty(default=False,update=hide_select)
    bpy.types.Object.coa_data_path = StringProperty()
    bpy.types.Object.coa_show_children = BoolProperty(default=True)
    bpy.types.Object.coa_show_export_box = BoolProperty()
    bpy.types.Object.coa_sprite_frame_previews = EnumProperty(items = enum_sprite_previews,update=set_sprite_frame)
    bpy.types.Object.coa_tiles_changed = BoolProperty(default=False)
    bpy.types.Object.coa_sprite_updated = BoolProperty(default=False)
    bpy.types.Object.coa_modulate_color = FloatVectorProperty(name="Modulate Color",description="Modulate color for sprites. This will tint your sprite with given color.",default=(1.0,1.0,1.0),min=0.0,max=1.0,soft_min=0.0,soft_max=1.0,size=3,subtype="COLOR",update=set_modulate_color)
    bpy.types.Object.coa_modulate_color_last = FloatVectorProperty(default=(1.0,1.0,1.0),min=0.0,max=1.0,soft_min=0.0,soft_max=1.0,size=3,subtype="COLOR")
    bpy.types.Object.coa_type = EnumProperty(name="Object Type",default="MESH",items=(("SPRITE","Sprite","Sprite"),("MESH","Mesh","Mesh"),("SLOT","Slot","Slot")))
    bpy.types.Object.coa_slot_index = bpy.props.IntProperty(default=0,update=change_slot_mesh,min=0)
    bpy.types.Object.coa_slot_index_last = bpy.props.IntProperty()
    bpy.types.Object.coa_slot_reset_index = bpy.props.IntProperty(default=0,min=0)
    bpy.types.Object.coa_slot_show = bpy.props.BoolProperty(default=False)
    bpy.types.Object.coa_flip_direction = bpy.props.BoolProperty(default=False,update=change_direction)
    bpy.types.Object.coa_flip_direction_last = bpy.props.BoolProperty(default=False)
    bpy.types.Object.coa_change_z_ordering = bpy.props.BoolProperty(default=False)
    bpy.types.Object.coa_selected_shapekey = bpy.props.EnumProperty(items=get_shapekeys,update=select_shapekey,name="Active Shapkey")
    
    bpy.types.Object.coa_edit_mode = EnumProperty(name="Edit Mode",items=(("OBJECT","Object","Object"),("MESH","Mesh","Mesh"),("ARMATURE","Armature","Armature"),("WEIGHTS","Weights","Weights"),("SHAPEKEY","Shapkey","Shapekey")))
    bpy.types.Object.coa_edit_weights = BoolProperty(default=False,update=exit_edit_weights)
    bpy.types.Object.coa_edit_armature = BoolProperty(default=False)
    bpy.types.Object.coa_edit_shapekey = BoolProperty(default=False)
    bpy.types.Object.coa_edit_mesh = BoolProperty(default=False,update=change_edit_mode)
    
    bpy.types.Bone.coa_favorite = BoolProperty()
    bpy.types.Bone.coa_draw_bone = BoolProperty(default=False)
    bpy.types.Bone.coa_z_value = IntProperty(description="Z Depth",default=0)
    bpy.types.Bone.coa_data_path = StringProperty()
    bpy.types.Bone.coa_hide_select = BoolProperty(default=False, update=hide_select_bone)
    bpy.types.Bone.coa_hide = BoolProperty(default=False,update=hide_bone)
    
    bpy.types.Scene.coa_display_all = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.coa_display_page = bpy.props.IntProperty(default=0,min=0,name="Display Page",description="Defines which page is displayed")
    bpy.types.Scene.coa_display_length = bpy.props.IntProperty(default=10,min=0,name="Page Length",description="Defines how Many Items are displayed")
    bpy.types.Area.coa_anim_window = bpy.props.BoolProperty(default=False)
    
    bpy.types.WindowManager.coa_running_modal = BoolProperty(default=False)
              
    def draw(self, context):
        global last_obj
        addon_updater_ops.check_for_update_background()

        layout = self.layout
        obj = context.active_object
        if obj != None:
            last_obj = obj.name
        elif obj == None and last_obj != None and last_obj in bpy.data.objects:
            obj = bpy.data.objects[last_obj] if last_obj in bpy.data.objects else None
        sprite_object = get_sprite_object(obj)
        scene = context.scene
            
        if context.space_data.viewport_shade not in ['MATERIAL','RENDERED','TEXTURED']:
            layout.operator("coa_tools.change_shading_mode",text="Set Proper Shading Mode",icon="ERROR")
        display_children(self,context,obj)
        
        if sprite_object != None and obj != None:
            row = layout.row(align=True)
            
            col = row.column(align=True)
            
            icon = "NONE"
            if obj.type == "ARMATURE":
                icon = "ARMATURE_DATA"
            elif obj.type == "MESH":
                icon = "OBJECT_DATA"
            elif obj.type == "LAMP":
                icon="LAMP"
                
            col.prop(obj,"name",text="",icon=icon)
            if obj.type == "MESH" and obj.coa_type == "SLOT":
                col.prop(obj.coa_slot[obj.coa_slot_index].mesh,"name",text="",icon="OUTLINER_DATA_MESH")
            if obj.type == "ARMATURE":
                row = layout.row(align=True)
                if context.active_bone != None:

                    col.prop(context.active_bone,'name',text="",icon="BONE_DATA")
                    if obj.mode != "EDIT" and get_addon_prefs(context).json_export:
                        box = layout.box()
                        row = box.row(align=True)
                        if sprite_object.coa_show_export_box:
                            row.prop(sprite_object,"coa_show_export_box",text="Json Export Properties",icon="TRIA_DOWN",emboss=False)
                            row = box.row(align=True)
                            row.prop(context.active_bone,"coa_draw_bone",text="Draw Bone on export")
                            row = box.row(align=True)
                        else:
                            row.prop(sprite_object,"coa_show_export_box",text="Json Export Properties",icon="TRIA_RIGHT",emboss=False)    
                    
                    
                    ### remove bone ik constraints
                    pose_bone = context.active_pose_bone
                    if pose_bone != None:
                        for bone in context.active_object.pose.bones:
                            for const in bone.constraints:
                                if const.type == "IK":
                                    if const.subtarget == pose_bone.name:
                                        row = col.row()
                                        row.operator("coa_tools.remove_ik",text="Remove Bone IK", icon="CONSTRAINT_BONE")
                            
                            
                            
                    ### remove bone stretch ik constraints            
                    if context.active_pose_bone != None and "coa_stretch_ik_data" in context.active_pose_bone:
                        col = layout.box().column(align=True)
        
                        for bone in obj.pose.bones:
                            if "coa_stretch_ik_data" in bone:
                                if eval(bone["coa_stretch_ik_data"])[0] == eval(context.active_pose_bone["coa_stretch_ik_data"])[0]:
                                    if "c_bone_ctrl" == eval(bone["coa_stretch_ik_data"])[1]:
                                        row = col.row()
                                        row.label(text="Stretch IK Constraint",icon="CONSTRAINT_BONE")
                                        op = row.operator("coa_tools.remove_stretch_ik",icon="X",emboss=False, text="")
                                        op.stretch_ik_name = eval(bone["coa_stretch_ik_data"])[0]
                                    elif eval(bone["coa_stretch_ik_data"])[1] in ["ik_bone_ctrl","p_bone_ctrl"]:
                                        col.prop(bone,"ik_stretch",text=bone.name)
                    
            if obj != None and obj.type == "MESH" and obj.mode == "OBJECT":
                row = layout.row(align=True)
                row.label(text="Sprite Properties:")
                
            if obj != None and obj.type == "MESH" and "coa_sprite" in obj and "coa_base_sprite" in obj.modifiers:
                row = layout.row(align=True)
                row.prop(obj.data,'coa_hide_base_sprite',text="Hide Base Sprite")
                if len(obj.data.vertices) > 4 and obj.data.coa_hide_base_sprite == False:
                    row.prop(obj.data,'coa_hide_base_sprite',text="",icon="ERROR",emboss=False)
            
            if obj != None and obj.type == "MESH" and obj.mode == "OBJECT":
                row = layout.row(align=True)
                if obj.coa_type == "MESH":
                    text = str(obj.coa_tiles_x * obj.coa_tiles_y) + " Frame(s) total"
                    row.label(text=text)
                elif obj.coa_type == "SLOT":    
                    text = str(len(obj.coa_slot)) + " Slot(s) total"
                    row.label(text=text)
                    
                if obj.coa_type == "MESH" and get_addon_prefs(context).enable_spritesheets:    
                    row = layout.row(align=True)
                    row.prop(obj,'coa_tiles_x',text="Tiles X")
                    row.prop(obj,'coa_tiles_y',text="Tiles Y")
                    
                    row = layout.row(align=True)
                    row.prop(obj,'coa_sprite_frame',text="Frame Index",icon="UV_FACESEL")
                    if obj.coa_tiles_x * obj.coa_tiles_y > 1:                    
                        op = row.operator("coa_tools.select_frame_thumb",text="",icon="IMAGE_COL")
                        op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE2")
                        op.prop_name = "coa_sprite_frame"
                        op.add_keyframe = True
                        op.default_interpolation = "CONSTANT"
                        op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE3")
                        op.prop_name = "coa_sprite_frame"
                        op.add_keyframe = False
                        #row.template_icon_view(obj, "coa_sprite_frame_previews")
                elif obj.coa_type == "SLOT" and len(obj.coa_slot) > 0:
                    row = layout.row(align=True)
                    slot_text = "Slot Index (" + str(len(obj.coa_slot)) + ")"
                    row.prop(obj,'coa_slot_index',text="Slot Index") 
                    op = row.operator("coa_tools.select_frame_thumb",text="",icon="IMAGE_COL")
                    op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE2")
                    op.prop_name = "coa_slot_index"
                    op.add_keyframe = True
                    op.default_interpolation = "CONSTANT"
                    op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE3")
                    op.prop_name = "coa_slot_index"
                    op.add_keyframe = False   
            
            if obj != None and obj.type == "MESH" and obj.mode == "OBJECT":
                
                
                row = layout.row(align=True)
                row.prop(obj,'coa_z_value',text="Z Depth")
                op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE2")
                op.prop_name = "coa_z_value"
                op.add_keyframe = True
                op.default_interpolation = "CONSTANT"
                op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE3")
                op.prop_name = "coa_z_value"
                op.add_keyframe = False
                
                row = layout.row(align=True)
                row.prop(obj,'coa_alpha',text="Alpha",icon="TEXTURE")
                op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE2")
                op.prop_name = "coa_alpha"
                op.add_keyframe = True
                op.default_interpolation = "BEZIER"
                op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE3")
                op.prop_name = "coa_alpha"
                op.add_keyframe = False
                
                row = layout.row(align=True)
                row.prop(obj,'coa_modulate_color',text="")
                op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE2")
                op.prop_name = "coa_modulate_color"
                op.add_keyframe = True
                op.default_interpolation = "LINEAR"
                op = row.operator("coa_tools.add_keyframe",text="",icon="SPACE3")
                op.prop_name = "coa_modulate_color"
                op.add_keyframe = False  
            
        if obj != None and obj.type == "CAMERA":
            row = layout.row(align=True)
            row.label(text="Camera Properties:")
            row = layout.row(align=True)
            row.prop(obj.data,"ortho_scale",text="Camera Zoom")
            row = layout.row(align=True)
            rd = context.scene.render
            col = row.column(align=True)
            col.label(text="Resolution:")
            col.prop(rd, "resolution_x", text="X")
            col.prop(rd, "resolution_y", text="Y")
            col.prop(rd, "resolution_percentage", text="")
            
            col.label(text="Path:")
            col.prop(rd, "filepath", text="")
            
            row = layout.row(align=True)
            col = row.column(align=True)
            col.prop(obj, "location")

######################################################################################################################################### Cutout Animation Tools Panel
class CutoutAnimationTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Cutout Tools"
    bl_category = "Cutout Animation"
    
    def snapping(self,context):
        if bpy.context.scene.coa_surface_snap:
            bpy.context.scene.tool_settings.use_snap = True
            bpy.context.scene.tool_settings.snap_element = 'FACE'
        else:
            bpy.context.scene.tool_settings.use_snap = False
    
    def lock_view(self,context):
        screen = context.screen
        if "-nonnormal" in self.name:
            bpy.data.screens[context.screen.name.split("-nonnormal")[0]].coa_view = self.coa_view
        if screen.coa_view == "3D":
            set_middle_mouse_move(False)
            set_view(screen,"3D")
        elif screen.coa_view == "2D":
            set_middle_mouse_move(True)
            set_view(screen,"2D")
    
    def update_stroke_distance(self,context):
        mult = bpy.context.space_data.region_3d.view_distance*.05
        if self.coa_distance_constraint:
            context.scene.coa_distance /= mult
        else:
            context.scene.coa_distance *= mult
    
    bpy.types.Scene.coa_distance = FloatProperty(description="Set the asset distance for each Paint Stroke",default = 1.0,min=-.0, max=30.0)
    bpy.types.Scene.coa_detail = FloatProperty(description="Detail",default = .3,min=0,max=1.0)
    bpy.types.Scene.coa_snap_distance = FloatProperty(description="Snap Distance",default = 0.01,min=0)
    bpy.types.Scene.coa_surface_snap = BoolProperty(default=True,description="Snap Vertices on Surface",update=snapping)
    bpy.types.Scene.coa_automerge = BoolProperty(default=False)
    bpy.types.Scene.coa_distance_constraint = BoolProperty(default=False,description="Constraint Distance to Viewport", update=update_stroke_distance)
    bpy.types.Scene.coa_lock_to_bounds = BoolProperty(default=True,description="Lock Cursor to Object Bounds")
    bpy.types.Scene.coa_frame_last = IntProperty(description="Stores last frame Number",default=0)
    
    bpy.types.Screen.coa_view = EnumProperty(default="3D",items=(("3D","3D View","3D","MESH_CUBE",0),("2D","2D View","2D","MESH_PLANE",1)),update=lock_view)
    bpy.types.WindowManager.coa_show_help = BoolProperty(default=False,description="Hide Help")
    
    
    def draw(self, context):
        global last_obj
        wm = context.window_manager
        layout = self.layout
        obj = context.active_object
        if obj == None and last_obj != None and last_obj in bpy.data.objects:
            obj = bpy.data.objects[last_obj]
            
        sprite_object = get_sprite_object(obj)
        scene = context.scene    
        screen = context.screen
        
        pcoll = preview_collections["main"]
        db_icon = pcoll["db_icon"]
        
        row = layout.row(align=True)
        row.prop(screen,"coa_view",expand=True)
        
        if not wm.coa_show_help:
            row.operator("coa_tools.show_help",text="",icon="INFO")
        else:
            row.prop(wm,"coa_show_help",text="",icon="INFO")    
        
        
        if obj!= None and sprite_object != None:            
            ### draw Edit Mode Operator
            if obj.mode in ["OBJECT","POSE"]:
                row = layout.row()
                row.label(text="Edit Modes:")
            
            if sprite_object.coa_edit_mesh == False and sprite_object.coa_edit_shapekey == False and sprite_object.coa_edit_armature == False and sprite_object.coa_edit_weights == False and obj.mode not in ["SCULPT"]:
                row = layout.row(align=True)
                row.operator("object.coa_edit_mesh",text="Edit Mesh",icon="GREASEPENCIL")
                
            if sprite_object.coa_edit_mesh == False and sprite_object.coa_edit_shapekey == False and sprite_object.coa_edit_armature == False and sprite_object.coa_edit_weights == False and not(obj.type == "MESH" and obj.mode in ["EDIT","SCULPT"]):  
                row = layout.row(align=True)
                row.operator("scene.coa_quick_armature",text="Edit Armature",icon="ARMATURE_DATA")
            elif sprite_object.coa_edit_armature:
                row = layout.row(align=True)
                row.prop(sprite_object,"coa_edit_armature", text="Finish Edit Armature",icon="ARMATURE_DATA")
                
            if sprite_object.coa_edit_mesh == False and sprite_object.coa_edit_shapekey == False and sprite_object.coa_edit_armature == False and sprite_object.coa_edit_weights == False and obj.mode not in ["SCULPT"]:    
                row = layout.row(align=True)
                row.operator("coa_tools.edit_shapekey",text="Edit Shapekey",icon="SHAPEKEY_DATA")     
            
            if sprite_object.coa_edit_mesh == False and sprite_object.coa_edit_shapekey == False and sprite_object.coa_edit_armature == False and sprite_object.coa_edit_weights == False and not(obj.type == "MESH" and obj.mode in ["EDIT","SCULPT"]) and (sprite_object) != None:
                row = layout.row(align=True)
                row.operator("object.coa_edit_weights",text="Edit Weights",icon="MOD_VERTEX_WEIGHT")
            elif sprite_object.coa_edit_weights:
                row = layout.row(align=True)
                row.prop(sprite_object,"coa_edit_weights", text="Finish Edit Weights", toggle=True, icon="MOD_VERTEX_WEIGHT")
            ###
        
        no_edit_mode_active = sprite_object != None and sprite_object.coa_edit_shapekey == False and sprite_object.coa_edit_mesh == False and sprite_object.coa_edit_armature == False and sprite_object.coa_edit_weights == False
        if obj == None or (obj != None):
            if sprite_object != None and sprite_object.coa_edit_mesh:
                row = layout.row(align=True)
                row.prop(sprite_object,"coa_edit_mesh", text="Finish Edit Mesh", toggle=True, icon="GREASEPENCIL")
            elif sprite_object != None and sprite_object.coa_edit_shapekey:    
                row = layout.row(align=True)
                row.prop(sprite_object,"coa_edit_shapekey", text="Finish Edit Shapekey", toggle=True, icon="SHAPEKEY_DATA")
            
            
            if obj != None and obj.mode in ["OBJECT","POSE"] and no_edit_mode_active:
                row = layout.row(align=True)
                row.label(text="General Operator:")
            
                row = layout.row(align=True)
                op = row.operator("wm.coa_create_ortho_cam",text="Create Camera", icon="OUTLINER_DATA_CAMERA")
                op.create = True
        if obj != None and obj.type == "CAMERA":    
            row = layout.row(align=True)
            op = row.operator("wm.coa_create_ortho_cam",text="Reset Camera Resolution",icon="OUTLINER_DATA_CAMERA")
            op.create = False
            
        
        if obj == None or (obj != None and obj.mode not in ["EDIT","WEIGHT_PAINT","SCULPT"]):
            row = layout.row(align=True)
            row.operator("wm.coa_create_sprite_object",text="Create new Sprite Object",icon="TEXTURE_DATA")
        
        if get_sprite_object(obj) != None:            
            if obj != None and obj.mode in ["OBJECT","SCULPT","POSE"]:
                if operator_exists("object.create_driver_constraint") and len(context.selected_objects)>1:
                    row = layout.row()
                    row.operator("object.create_driver_constraint",text="Driver Constraint",icon="DRIVER")
                    
            
            if sprite_object.coa_edit_weights == False and sprite_object.coa_edit_shapekey == False:
                if sprite_object != None and ((obj != None and obj.mode not in ["EDIT","WEIGHT_PAINT","SCULPT"]) or obj == None):
                    row = layout.row(align=True)
                    row.operator("coa_tools.coa_import_sprites",text="Re / Import Sprites",icon="IMASEL")
                        
                    if get_addon_prefs(context).json_export:
                        row = layout.row()
                        row.operator("object.export_to_json",text="Export Json",icon="EXPORT",emboss=True)
                    
                    row = layout.row(align=True)
                    row.operator("coa_tools.create_slot_object",text="Merge to Slot Object",icon="IMASEL",emboss=True)  
                    if obj != None and obj.coa_type == "SLOT":
                        row.operator("coa_tools.extract_slots",text="Extract Slots",icon="EXPORT",emboss=True)  
                    
                    if operator_exists("object.create_driver_constraint") and len(context.selected_objects)>1:
                        row = layout.row()
                        row.operator("object.create_driver_constraint",text="Driver Constraint",icon="DRIVER")
                    
                    if get_addon_prefs(context).dragon_bones_export:
                        row = layout.row()
                        row.operator("coa_tools.export_dragon_bones",text="Export Dragonbones",icon_value=db_icon.icon_id,emboss=True)
                
                if obj != None:
                    if obj.type == "ARMATURE" and obj.mode == "POSE":
                        row = layout.row(align=True)
                        row.operator("bone.coa_draw_bone_shape",text="Draw Bone Shape",icon="BONE_DATA")
                    
                    if obj != None and obj.mode == "POSE":
                        row = layout.row(align=True)
                        row.label(text="Bone Constraint Operator:")
                        row = layout.row(align=True)
                        row.operator("object.coa_set_ik",text="Create IK Bone",icon="CONSTRAINT_BONE")
                        row = layout.row(align=True)
                        row.operator("bone.coa_set_stretch_bone",text="Create Stretch Bone",icon="CONSTRAINT_BONE")
                        
                        row = layout.row(align=True)
                        row.operator("coa_tools.create_stretch_ik",text="Create Stretch IK",icon="CONSTRAINT_BONE")
                    
            if obj != None and obj.type == "MESH":
                
                if obj != None and obj.mode == "SCULPT":
                    if not sprite_object.coa_edit_shapekey:
                        row = layout.row(align=True)
                        row.operator("coa_tools.leave_sculptmode",text="Finish Edit Shapekey",icon="SHAPEKEY_DATA")  
                    row = layout.row(align=True)
                    draw_sculpt_ui(self, context, row)
                    
                if sprite_object.coa_edit_mesh == False and sprite_object.coa_edit_shapekey == False and sprite_object.coa_edit_armature == False and sprite_object.coa_edit_weights == False and not(obj.type == "MESH" and obj.mode in ["EDIT","SCULPT"]) and (sprite_object) != None:
                    pass
                elif sprite_object.coa_edit_weights:                    
                    col = layout.split().column()
                    tool_settings = scene.tool_settings
                    brush_data = tool_settings.weight_paint
                    
                    col.template_ID_preview(brush_data, "brush", new="brush.add", rows=3, cols=8)
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.prop(tool_settings.unified_paint_settings,"weight")
                    row = col.row(align=True)
                    row.prop(tool_settings.unified_paint_settings,"size")
                    row.prop(tool_settings.unified_paint_settings,"use_pressure_size",text="")
                    row = col.row(align=True)
                    row.prop(tool_settings.unified_paint_settings,"strength")
                    row.prop(tool_settings.unified_paint_settings,"use_pressure_strength",text="")
                    row = col.row(align=True)
                    row.prop(tool_settings,"use_auto_normalize",text="Auto Normalize")
                   
        if obj != None and ("coa_sprite" in obj or "coa_bone_shape" in obj) and obj.mode == "EDIT" and obj.type == "MESH" and sprite_object.coa_edit_mesh:
            row = layout.row(align=True)
            row.label(text="Mesh Tools:")
            
            if "coa_sprite" in obj:
                
                
                row = layout.row(align=True)
                operator = row.operator("coa_tools.generate_mesh_from_edges_and_verts",text="Generate Mesh",icon="OUTLINER_OB_SURFACE")
                
                row = layout.row(align=True)
                operator = row.operator("coa_tools.fill_edge_loop",text="Normal Fill",icon="OUTLINER_OB_SURFACE")
                operator.triangulate = False
                
                row = layout.row(align=True)
                operator = row.operator("coa_tools.fill_edge_loop",text="Triangle Fill",icon="OUTLINER_OB_SURFACE")
                operator.triangulate = True
            
            
            col = layout.column(align=True)
            
            row2 = col.row(align=True)
            row2.prop(scene,'coa_distance',text="Stroke Distance")
            row2.operator("coa_tools.pick_edge_length",text="",icon="EYEDROPPER")
            
            row2 = col.row(align=True)
            row2.prop(scene,'coa_snap_distance',text="Snap Distance")
            row2 = col.row(align=True)
            if scene.coa_surface_snap:
                row2.prop(scene,'coa_surface_snap',text="Snap Vertices",icon="SNAP_ON")
            else:
                row2.prop(scene,'coa_surface_snap',text="Snap Vertices",icon="SNAP_OFF")    
            
            col = layout.column(align=True)
            operator = col.operator("mesh.knife_tool", text="Knife")
            if "coa_sprite" in obj:
                operator = col.operator("coa_tools.reproject_sprite_texture", text="Reproject Sprite")

### Custom template_list look
class UIListAnimationCollections(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = data
        slot = item
        col = layout.row(align=True)
        if item.name not in ["NO ACTION","Restpose"]:
            col.label(icon="ACTION")
            col.prop(item,"name",emboss=False,text="")
        elif item.name == "NO ACTION":
            col.label(icon="RESTRICT_SELECT_ON")    
            col.label(text=item.name)
        elif item.name == "Restpose":
            col.label(icon="ARMATURE_DATA")    
            col.label(text=item.name)
        
        if context.scene.coa_nla_mode == "NLA" and item.name not in ["NO ACTION","Restpose"]:    
            col = layout.row(align=False)
            op = col.operator("coa_operator.create_nla_track",icon="NLA",text="")
            op.anim_collection_name = item.name

### Custom template_list look for event lists            
class UIListEventCollection(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = data
        slot = item
        # col = layout.column(align=False)
        box = layout.box()
        col = box.column(align=False)

        row = col.row(align=False)
        # row.label(text="", icon="TIME")
        if item.collapsed:
            row.prop(item,"collapsed",emboss=False, text="", icon="TRIA_RIGHT")
        else:
            row.prop(item, "collapsed", emboss=False, text="", icon="TRIA_DOWN")
        row.prop(item, "frame", emboss=True, text="Frame")
        op = row.operator("coa_tools.remove_timeline_event", text="", icon="PANEL_CLOSE", emboss=False)
        op.index = index


        # row = col.row(align=True)
        if not item.collapsed:
            row = col.row(align=True)
            # row.alignment = "RIGHT"
            op = row.operator("coa_tools.add_event", icon="ZOOMIN", text="Add new Event", emboss=True)
            op.index = index
            for i, event in enumerate(item.event):
                row = col.row(align=True)
                row.prop(event, "type",text="")
                row.prop(event, "value",text="")
                op = row.operator("coa_tools.remove_event", icon="PANEL_CLOSE", text="", emboss=True)
                op.index = index
                op.event_index = i
        
        


######################################################################################################################################### Select Child Operator
class SelectChild(bpy.types.Operator):
    bl_idname = "object.coa_select_child"
    bl_label = "select_child"
    
    ob_name = StringProperty()
    bone_name = StringProperty()
    
    def __init__(self):
        self.sprite_object = None
    
    mode = EnumProperty(items=(("object","object","object"),("bone","bone","bone")))
    armature = None
    
    def change_object_mode(self,context):
        obj = context.active_object
        if obj != None and self.ob_name != obj.name:
            if obj.mode == "EDIT" and obj.type == "MESH":
                bpy.ops.object.mode_set(mode="OBJECT")
            elif obj.mode == "EDIT" and obj.type == "ARMATURE":
                bpy.ops.object.mode_set(mode="POSE")    
            
    
    def select_child(self,context,event):
        global last_obj
        self.change_object_mode(context)
        
        if self.mode == "object":
            ob = bpy.data.objects[self.ob_name]
            ob.select = True
            context.scene.objects.active = ob
            if ob != None:
                last_obj = ob.name
            
            if not event.ctrl and not event.shift:
                for obj in context.scene.objects:
                    if obj != ob:
                        obj.select = False
                
        elif self.mode == "bone":
            armature_ob = bpy.data.objects[self.ob_name]
            armature = bpy.data.armatures[armature_ob.data.name]
            bone = armature.bones[self.bone_name]
            bone.select = not bone.select
            bone.select_tail = not bone.select_tail
            bone.select_head = not bone.select_head
            if bone.select == True:
                armature.bones.active = bone
            else:
                armature.bones.active = None
        
    def shift_select_child(self,context,event):
        self.change_object_mode(context)
        
        sprite_object = get_sprite_object(context.active_object)
        children = []
        armature = None
        if self.mode == "object":
            children = get_children(context,sprite_object,ob_list=[])
            ### sort children
            children = sorted(children, key=lambda x: x.location[1] if type(x) == bpy.types.Object else x.name,reverse=False)
            children = sorted(children, key=lambda x: x.type if type(x) == bpy.types.Object else x.name,reverse=False)
            if len(children) > 1 and type(children[1]) == bpy.types.Object and children[1].type == "CAMERA":
                children.insert(0,children.pop(1))
        else:
            armature = bpy.data.armatures[self.ob_name]
            for bone in  armature.bones:
                children.append(bone)
        
                
        from_index = 0
        to_index = 0
        for i,child in enumerate(children):
            if self.mode == "object":
                if child.name == self.ob_name:
                    to_index = i
            elif self.mode == "bone":
                if child.name == self.bone_name:
                    to_index = i
            if child.select == True:
                from_index = i

        select_range = []
        if from_index < to_index:
            for i in range(from_index,to_index+1):
                select_range.append(i)
        else:
            for i in range(to_index,from_index):
                select_range.append(i)  
        for i,child in enumerate(children):
            if i in select_range:
                child.select = True
                
        if self.mode == "object":
            context.scene.objects.active = bpy.data.objects[self.ob_name]
        elif self.mode == "bone":
            context.scene.objects.active = bpy.data.objects[self.ob_name]
            armature.bones.active  = armature.bones[self.bone_name]
        
    def change_weight_mode(self,context,mode):
        if self.sprite_object.coa_edit_weights:
            armature = get_armature(self.sprite_object)
            armature.select = True
            bpy.ops.view3d.localview()
            bpy.context.space_data.viewport_shade = 'TEXTURED'

            ### zoom to selected mesh/sprite
            for obj in bpy.context.selected_objects:
                obj.select = False
            obj = bpy.data.objects[context.active_object.name]    
            obj.select = True
            context.scene.objects.active = obj
            bpy.ops.view3d.view_selected()
            
            ### set uv image
            set_uv_image(obj)
        
            
            bpy.ops.object.mode_set(mode=mode)
            
    def invoke(self,context,event):
        self.sprite_object = get_sprite_object(context.active_object)
        self.armature = get_armature(self.sprite_object)
        
        if self.sprite_object.coa_edit_mesh:
            obj = bpy.data.objects[self.ob_name]
            obj.hide = False
        
        if self.sprite_object != None:
            self.change_weight_mode(context,"OBJECT")
        
        if self.sprite_object != None:
            if context.active_object != None and context.active_object.type == "ARMATURE" and context.active_object.mode == "EDIT" and event.alt:
                obj = bpy.data.objects[self.ob_name]
                if obj.type == "MESH":
                    set_weights(self,context,obj)
                    msg = '"'+self.ob_name+'"' + " has been bound to selected Bones."
                    self.report({'INFO'},msg)
                else:
                    self.report({'WARNING'},"Can only bind Sprite Meshes to Bones")
                return{"FINISHED"}
            
            if event.shift and not self.sprite_object.coa_edit_weights:
                self.shift_select_child(context,event)
            if not self.sprite_object.coa_edit_weights or ( self.sprite_object.coa_edit_weights and bpy.data.objects[self.ob_name].type == "MESH"):
                if not event.ctrl and not event.shift:
                    if self.mode == "bone":
                        for bone in bpy.data.objects[self.ob_name].data.bones:
                            bone.select = False
                            bone.select_head = False
                            bone.select_tail = False
                if not event.shift:
                    self.select_child(context,event)
                    
            if self.sprite_object.coa_edit_weights:     
                create_armature_parent(context)
            self.change_weight_mode(context,"WEIGHT_PAINT")    
        else:
            self.shift_select_child(context,event)
                        
        return{'FINISHED'}
    
class CutoutAnimationCollections(bpy.types.Panel):
    bl_idname = "cutout_animation_collections"
    bl_label = "Cutout Animations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Cutout Animation"
    
    
    def set_actions(self,context):
        scene = context.scene
        sprite_object = get_sprite_object(context.active_object)
        
        if context.scene.coa_nla_mode == "ACTION":
            scene.frame_start = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index].frame_start
            scene.frame_end = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index].frame_end
            set_action(context)
        for obj in context.visible_objects:
            if obj.type == "MESH" and "coa_sprite" in obj:
                update_uv(context,obj)
                set_alpha(obj,bpy.context,obj.coa_alpha)
                set_z_value(context,obj,obj.coa_z_value)
                set_modulate_color(obj,context,obj.coa_modulate_color)
        
        ### set export name
        if scene.coa_nla_mode == "ACTION":
            action_name = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index].name    
            if action_name in ["Restpose","NO ACTION"]:
                action_name = ""
            else:
                action_name += "_"
            path = context.scene.render.filepath.replace("\\","/")
            dirpath = path[:path.rfind("/")]
            final_path = dirpath + "/" + action_name
            context.scene.render.filepath = final_path

    
    def set_nla_mode(self,context):
        sprite_object = get_sprite_object(context.active_object)
        children = get_children(context,sprite_object,ob_list=[])
        if self.coa_nla_mode == "NLA":
            for child in children:
                if child.animation_data != None:
                    child.animation_data.action = None
            context.scene.frame_start = context.scene.coa_frame_start
            context.scene.frame_end = context.scene.coa_frame_end        
            
            for child in children:
                if child.animation_data != None:
                    for track in child.animation_data.nla_tracks:
                        track.mute = False
        else:
            if len(sprite_object.coa_anim_collections) > 0:
                anim_collection = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]
                context.scene.frame_start = anim_collection.frame_start
                context.scene.frame_end = anim_collection.frame_end
                set_action(context)            
                for obj in context.visible_objects:
                    if obj.type == "MESH" and "coa_sprite" in obj:
                        update_uv(context,obj)
                        set_alpha(obj,bpy.context,obj.coa_alpha)
                        set_z_value(context,obj,obj.coa_z_value)
                        set_modulate_color(obj,context,obj.coa_modulate_color)
                for child in children:
                    if child.animation_data != None:
                        for track in child.animation_data.nla_tracks:
                            track.mute = True
        
        bpy.ops.coa_tools.toggle_animation_area(mode="UPDATE")
                
    
    
    
    def update_frame_range(self,context):
        sprite_object = get_sprite_object(context.active_object)
        if len(sprite_object.coa_anim_collections) > 0:
            anim_collection = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]
        
        if context.scene.coa_nla_mode == "NLA" or len(sprite_object.coa_anim_collections) == 0:
            context.scene.frame_start = self.coa_frame_start
            context.scene.frame_end = self.coa_frame_end
    
    bpy.types.Object.coa_anim_collections_index = IntProperty(update=set_actions)
    bpy.types.Scene.coa_nla_mode = EnumProperty(description="Animation Mode. Can be set to NLA or Action to playback all NLA Strips or only Single Actions",items=(("ACTION","ACTION","ACTION","ACTION",0),("NLA","NLA","NLA","NLA",1)),update=set_nla_mode)
    bpy.types.Scene.coa_frame_start = IntProperty(name="Frame Start",default=0,min=0,update=update_frame_range)
    bpy.types.Scene.coa_frame_end = IntProperty(name="Frame End",default=250,min=1,update=update_frame_range)
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        scene = context.scene
        sprite_object = get_sprite_object(obj)
        if sprite_object != None:

            
            row = layout.row()
            row.prop(sprite_object,"coa_animation_loop",text="Wrap Animation Playback")
            
            row = layout.row()
            row.prop(scene,"coa_nla_mode",expand=True)
            
            if scene.coa_nla_mode == "NLA":
                row = layout.row(align=True)
                row.prop(scene,"coa_frame_start")
                row.prop(scene,"coa_frame_end")
            
            row = layout.row()
            row.template_list("UIListAnimationCollections","dummy",sprite_object, "coa_anim_collections", sprite_object, "coa_anim_collections_index",rows=2,maxrows=10,type='DEFAULT')
            col = row.column(align=True)
            col.operator("coa_tools.add_animation_collection",text="",icon="ZOOMIN")
            col.operator("coa_tools.remove_animation_collection",text="",icon="ZOOMOUT")
            
            if len(sprite_object.coa_anim_collections) > 2 and sprite_object.coa_anim_collections_index > 1:
                col.operator("coa_tools.duplicate_animation_collection",text="",icon="COPY_ID")
            
            if not "-nonnormal" in context.screen.name:
                col.operator("coa_tools.toggle_animation_area",text="",icon="ACTION")            
            
            if  len(sprite_object.coa_anim_collections) > 0 and sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index].action_collection:
                row = layout.row(align=True)
                item = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]
                row.prop(item,"frame_end",text="Animation Length")
                
                
                # if get_addon_prefs(context).dragon_bones_export:
                row = layout.row(align=True)
                row.label(text="Timeline Events",icon="TIME")
                row = layout.row(align=False)
                row.template_list("UIListEventCollection","dummy",item, "timeline_events", item, "event_index",rows=1,maxrows=10,type='DEFAULT')
                col = row.column(align=True)
                col.operator("coa_tools.add_timeline_event",text="",icon="ZOOMIN")
            
            row = layout.row(align=True)
            if context.scene.coa_nla_mode == "ACTION":

                operator = row.operator("coa_tools.batch_render",text="Batch Render Animations",icon="RENDER_ANIMATION")
            else:
                operator = row.operator("render.render",text="Render Animation",icon="RENDER_ANIMATION")
                operator.animation = True
                
preview_collections = {}
