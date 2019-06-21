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
from mathutils import Vector, Matrix, Quaternion, Euler
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent

def set_uv_image(obj):
    data = obj.data
    if len(data.materials) > 0:
        mat = data.materials[0]
        tex = [slot.texture for slot in mat.texture_slots if slot != None and slot.texture.type == "IMAGE"][0]
        img = tex.image if tex.image != None else None   
        if img != None:
            for uv_vert in obj.data.uv_textures[0].data:
                uv_vert.image = img

def draw_sculpt_ui(self,context,layout):
    obj = context.active_object
    if obj != None and obj.mode == "SCULPT":
        layout = layout.column()
        toolsettings = context.tool_settings
        settings = toolsettings.sculpt
        brush = settings.brush
        
        col = layout.column(align=True)
        col.separator()
        if obj.data.shape_keys == None:
            col.label(text="No Shapekeys available yet.",icon="ERROR")
        subrow = col.row(align=True)
        subrow.prop(obj,"coa_selected_shapekey",text="")
        op = subrow.operator("coa_tools.shapekey_add",icon="NEW",text="")
        
        if obj.data.shape_keys != None and len(obj.data.shape_keys.key_blocks) > 0:
            op = subrow.operator("coa_tools.shapekey_rename",icon="OUTLINER_DATA_FONT",text="")
            op = subrow.operator("coa_tools.shapekey_remove",icon="X",text="")
            
        if obj.data.shape_keys != None:
            shapekey_index = int(obj.coa_selected_shapekey)
            if shapekey_index > 0:
                active_shapekey = obj.data.shape_keys.key_blocks[shapekey_index]
                col.prop(active_shapekey,"value")        
        
        col = layout.column(align=False)
        subrow = col.row(align=True)
        subrow.prop(obj,"show_wire",toggle=True,icon="MESH_DATA")
        subrow.prop(obj,"show_all_edges",toggle=True)
        
        if not context.particle_edit_object:
            col = layout.split().column()
            col.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)
            
        row = layout.row(align=True)
        settings = toolsettings.unified_paint_settings if toolsettings.unified_paint_settings.use_unified_size else toolsettings.sculpt.brush
        
        if settings.use_locked_size:
            icon = "UNLOCKED"
        elif not settings.use_locked_size:
            icon = "LOCKED"
        
        col = layout.column(align=True)
        
        subrow = col.row(align=True)        
        subrow.prop(settings,"use_locked_size",text="",toggle=True,icon=icon)
        subrow.prop(settings,"size",slider=True)    
        subrow.prop(settings,"use_pressure_size",text="")
        col.prop(settings,"strength")
        
        
        row = layout.row(align=True)
        row.label(text="Symmetry:")
        row = layout.row(align=True)
        row.prop(toolsettings.sculpt,"use_symmetry_x",text="X",toggle=True)
        row.prop(toolsettings.sculpt,"use_symmetry_y",text="Y",toggle=True)
        row.prop(toolsettings.sculpt,"use_symmetry_z",text="Z",toggle=True)
        

        brush = toolsettings.sculpt.brush

        layout.template_curve_mapping(brush, "curve", brush=True)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
        row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
        row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
        row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
        row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'
         

def operator_exists(idname):
    op_name = idname.split(".")
    name = op_name[0].upper()+"_OT_"+op_name[1]
    return hasattr(bpy.types,name)

def remove_base_mesh(obj):
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    verts = []
        
    if "coa_base_sprite" in obj.vertex_groups:
        v_group_idx = obj.vertex_groups["coa_base_sprite"].index
        for i,vert in enumerate(obj.data.vertices):
            for g in vert.groups:
                if g.group == v_group_idx:
                    verts.append(bm.verts[i])
                    break

    bmesh.ops.delete(bm,geom=verts,context=1)
    bm = bmesh.update_edit_mesh(obj.data) 
    bpy.ops.object.mode_set(mode="OBJECT")

def fix_bone_roll(armature):
    mode = armature.mode
    bpy.ops.object.mode_set(mode="EDIT")
    
    ### show all bone layers
    layers = []
    for i,layer in enumerate(armature.data.layers):
        layers.append(layer)
        armature.data.layers[i] = True
    
    ### store bone selection and store intial state
    hidden_bones = []
    locked_bones = []
    selected_edit_bones = []
    for bone in armature.data.edit_bones:
        if bone.hide:
            hidden_bones.append(bone)
        bone.hide = False
        
        if bone.hide_select:
            locked_bones.append(bone)    
        bone.hide_select = False
            
        if bone.select and bone.select_head and bone.select_tail:
            selected_edit_bones.append(bone)
        
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
    
    ### align bone roll    
    bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')
    
    ### restore bone selection, hide and hide_select
    for bone in armature.data.edit_bones:
        if bone in hidden_bones:
            bone.hide = True
        if bone in locked_bones:
            bone.hide_select = True    
        
        if bone not in selected_edit_bones:
            bone.select = False
            bone.select_head = False
            bone.select_tail = False
    
    ### restore bone layer visibility
    for i,layer in enumerate(layers):
        armature.data.layers[i] = layer
    
    ### change back to previous mode        
    bpy.ops.object.mode_set(mode=mode)
    

def set_weights(self,context,obj):
    if len(context.selected_bones) == 0:
        return {'RUNNING_MODAL'}
    
    self.set_waits = True
    bone_data = []
    orig_armature = self.armature#context.active_object
    ### remove bone vertex_groups
    for weight in obj.vertex_groups:
        if weight.name in orig_armature.data.bones:
            obj.vertex_groups.remove(weight)
    ###         
    use_deform = []
    bone_pos = {}
    selected_bones = []
    
    for i,bone in enumerate(orig_armature.data.edit_bones):
        if bone.select and (bone.select_head or bone.select_tail):
            selected_bones.append(bone)
        use_deform.append(orig_armature.data.bones[i].use_deform)
        if bone.select and (bone.select_head or bone.select_tail):
            bone_pos[bone] = {"tail":bone.tail[1],"head":bone.head[1]}
            bone.tail[1] = 0
            bone.head[1] = 0
            orig_armature.data.bones[i].use_deform = True
        else:
            orig_armature.data.bones[i].use_deform = False
    orig_armature.select = True     
    obj.select = True       
    
    #return{'FINISHED'}
    
    parent = bpy.data.objects[obj.parent.name]
    obj_orig_location = Vector(obj.location)
    obj.location[1] = 0.00001
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    obj.location = obj_orig_location
    
    for bone in bone_pos:
        bone.tail[1] = bone_pos[bone]["tail"]
        bone.head[1] = bone_pos[bone]["head"]
    for i,bone in enumerate(orig_armature.data.edit_bones):
        orig_armature.data.bones[i].use_deform = use_deform[i]
    i = 0
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            i += 1
    if i > 1:
        obj.modifiers.remove(obj.modifiers[len(obj.modifiers)-1])
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            modifier.object = orig_armature
    obj.parent = orig_armature
    #obj.parent = parent
    orig_armature.select = True
    context.scene.objects.active = orig_armature
    obj.select = False
    
    bpy.ops.object.mode_set(mode='EDIT')
    self.set_waits = False
    
    return {'RUNNING_MODAL'} 

def hide_base_sprite(obj):
    context = bpy.context
    selected_object = bpy.data.objects[context.active_object.name]
    if "coa_sprite" in obj and obj.type == "MESH":
        orig_mode = obj.mode
        context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        
        vertex_idxs = []
        if "coa_base_sprite" in obj.vertex_groups:
            v_group_idx = obj.vertex_groups["coa_base_sprite"].index
            for i,vert in enumerate(obj.data.vertices):
                for g in vert.groups:
                    if g.group == v_group_idx:
                        vertex_idxs.append(i)
                    
        for idx in vertex_idxs:
            vert = bm.verts[idx]
            vert.hide = True
            vert.select = False
            for edge in vert.link_edges:
                edge.hide = True
                edge.select = False
            for face in vert.link_faces:
                face.hide = obj.data.coa_hide_base_sprite
                face.select = False
                
        if "coa_base_sprite" in obj.modifiers:
            mod = obj.modifiers["coa_base_sprite"]
            mod.show_viewport = obj.data.coa_hide_base_sprite
            mod.show_render = obj.data.coa_hide_base_sprite
            
        bmesh.update_edit_mesh(me)               
        bpy.ops.object.mode_set(mode=orig_mode)                      
    context.scene.objects.active = selected_object
    
def get_uv_from_vert(uv_layer, v):
    for l in v.link_loops:
        if v.select:
            uv_data = l[uv_layer]
            return uv_data
            
def update_uv_unwrap(context):
    obj = context.active_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    ### pin uv boundary vertex
    uv_layer = bm.loops.layers.uv.active
    for vert in bm.verts:
        
        uv_vert = get_uv_from_vert(uv_layer, vert)
        if uv_vert != None:
            pass

    bmesh.update_edit_mesh(me)      
    


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def b_version_bigger_than(version):
    if bpy.app.version > version:
        return True
    else:
        return False

def check_region(context,event):
    in_view_3d = False
    if context.area != None:
        if context.area.type == "VIEW_3D":
            t_panel = context.area.regions[1]
            n_panel = context.area.regions[3]
            
            view_3d_region_x = Vector((context.area.x + t_panel.width, context.area.x + context.area.width - n_panel.width))
            view_3d_region_y = Vector((context.region.y, context.region.y+context.region.height))
            
            if event.mouse_x > view_3d_region_x[0] and event.mouse_x < view_3d_region_x[1] and event.mouse_y > view_3d_region_y[0] and event.mouse_y < view_3d_region_y[1]:
                in_view_3d = True
            else:
                in_view_3d = False
        else:
            in_view_3d = False
    return in_view_3d        

def unwrap_with_bounds(obj,uv_idx):
    bpy.ops.object.mode_set(mode="EDIT")
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv[uv_idx]
    scale_x = 1.0 / get_local_dimension(obj)[0] * obj.coa_tiles_x
    scale_z = 1.0 / get_local_dimension(obj)[1] * obj.coa_tiles_y
    offset = [get_local_dimension(obj)[2][0] * scale_x , get_local_dimension(obj)[2][1] * scale_z]
    for i,v in enumerate(bm.verts):
        for l in v.link_loops:
            uv_data = l[uv_layer]
            uv_data.uv[0] = (bm.verts[i].co[0] * scale_x) - offset[0]
            uv_data.uv[1] = (bm.verts[i].co[2] * scale_z)+1 - offset[1]
   
    bmesh.update_edit_mesh(me)
    bm.free()
    bpy.ops.object.mode_set(mode="OBJECT")

def get_local_dimension(obj):
    if obj.type == "MESH":
        x0 = 10000000000*10000000000
        x1 = -10000000000*10000000000
        y0 = 10000000000*10000000000
        y1 = -100000000000*10000000000
        
        for vert in obj.data.vertices:
            if vert.co[0] < x0:
                x0 = vert.co[0]
            if vert.co[0] > x1:
                x1 = vert.co[0]
            if vert.co[2] < y0:
                y0 = vert.co[2]
            if vert.co[2] > y1:
                y1 = vert.co[2]
                
        offset = [x0,y1]        
        return [(x1-x0)*obj.coa_tiles_x,(y1-y0)*obj.coa_tiles_y,offset]

def get_addon_prefs(context):
    addon_name = __name__.split(".")[0]
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[addon_name].preferences
    return addon_prefs

def get_local_view(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            return area.spaces.active.local_view

def check_name(name_array,name):
    if name in name_array:
        counter = 1
        check_name = name
        while check_name + ".{0:03d}".format(counter) in name_array:
            counter+=1
        name = name+".{0:03d}".format(counter)
        return name
        if counter > 999:
            return name
    else:
        return name


def create_action(context,item=None,obj=None):
    sprite_object = get_sprite_object(context.active_object)
    
    if len(sprite_object.coa_anim_collections) < 3:
        bpy.ops.coa_tools.add_animation_collection()
    
    if item == None:
        item = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]
    if obj == None:
        obj = context.active_object
        
    action_name = item.name + "_" + obj.name
    
    if action_name not in bpy.data.actions:
        action = bpy.data.actions.new(action_name)
    else:
        action = bpy.data.actions[action_name]
        
    action.use_fake_user = True
    if obj.animation_data == None:
        obj.animation_data_create()
    obj.animation_data.action = action
    context.scene.update()

def clear_pose(obj):
    if obj.type == "ARMATURE":
        for bone in obj.pose.bones:
            bone.scale = Vector((1,1,1))
            bone.location = Vector((0,0,0))
            bone.rotation_euler = Euler((0,0,0),"XYZ")
            bone.rotation_quaternion = Euler((0,0,0),"XYZ").to_quaternion()
    elif obj.type == "MESH":
        obj.coa_sprite_frame = 0
        obj.coa_alpha = 1.0
        obj.coa_modulate_color = (1.0,1.0,1.0)
        #obj["coa_slot_index"] = max(0,len(obj.coa_slot)-1)
        #obj["coa_slot_index"] = obj.coa_slot_reset_index
        obj.coa_slot_index = 0

def set_direction(obj):
    if obj.coa_flip_direction:
        if obj.scale.x > 0:
            obj.scale.x *= -1
    else:
        if obj.scale.x < 0:
            obj.scale.x *= -1
        
def set_action(context,item=None):
    sprite_object = get_sprite_object(context.active_object)
    if item == None:
        item = sprite_object.coa_anim_collections[sprite_object.coa_anim_collections_index]
    
    children = get_children(context,sprite_object,ob_list=[])

    animation_objects = []
    if sprite_object.type == "ARMATURE":
        animation_objects.append(sprite_object)
    for child in children:
        animation_objects.append(child)

    for child in animation_objects:
        clear_pose(child)
        if child.animation_data != None:
            child.animation_data.action = None
            
        if child.type == "ARMATURE" and item.name == "Restpose":
            for bone in child.pose.bones:
                bone.scale = Vector((1,1,1))
                bone.location = Vector((0,0,0))
                bone.rotation_euler = Euler((0,0,0),"XYZ")
                bone.rotation_quaternion = Euler((0,0,0),"XYZ").to_quaternion()
        if child.type == "MESH" and item.name == "Restpose":
            child.coa_sprite_frame = 0
            child.coa_alpha = 1.0
            child.coa_modulate_color = (1.0,1.0,1.0)
            #child["coa_slot_index"] = len(child.coa_slot)-1#child.coa_slot_reset_index
            #print(child["coa_slot_index"])
        elif not (child.type == "MESH" and item.name == "Restpose") and context.scene.coa_nla_mode == "ACTION":
            action_name = item.name + "_" + child.name
            action = None
            if action_name in bpy.data.actions:
                action = bpy.data.actions[action_name]
            if action != None:    
                action.use_fake_user = True    
                if child.animation_data == None:
                    child.animation_data_create()
                child.animation_data.action = action
    context.scene.frame_set(context.scene.frame_current)
    context.scene.update()        

def create_armature_parent(context):
    sprite = context.active_object
    armature = get_armature(get_sprite_object(sprite))
    armature.select = True
    context.scene.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_NAME')
    context.scene.objects.active = sprite

def set_local_view(local):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            override = bpy.context.copy()
            override["area"] = area
            if local:
                if area.spaces.active.local_view == None:
                    bpy.ops.view3d.localview(override)
            else:
                if area.spaces.active.local_view != None:
                    bpy.ops.view3d.localview(override)
                        

def actions_callback(self,context):
    actions = []
    actions.append(("New Action...","New Action...","New Action","NEW",0))
    actions.append(("Clear Action","Clear Action","Clear Action","RESTRICT_SELECT_ON",1))
    i = 2
    for action in bpy.data.actions:
        actions.append((action.name,action.name,action.name,'ACTION',i))
        i+=1
    return actions

def create_armature(context):
    obj = bpy.context.active_object
    sprite_object = get_sprite_object(obj)
    armature = get_armature(sprite_object)
    
    if armature != None:
        context.scene.objects.active = armature
        armature.select = True
        return armature
    else:
        amt = bpy.data.armatures.new("Armature")
        armature = bpy.data.objects.new("Armature",amt)
        armature.parent = sprite_object
        context.scene.objects.link(armature)
        context.scene.objects.active = armature
        armature.select = True
        amt.draw_type = "BBONE"
        return armature

def set_alpha(obj,context,alpha):
    sprite_object = get_sprite_object(obj)
    
    for mat in obj.material_slots:
        if mat != None:
            for i,tex_slot in enumerate(mat.material.texture_slots):
                if tex_slot != None:
                    tex_slot.alpha_factor = alpha
                    

def lock_view(screen,lock):
    for area in screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    region = space.region_3d
                    if lock:
                        region.view_rotation = Quaternion((0.7071,0.7071,-0.0,-0.0))                        
                        region.lock_rotation = True
                    else:
                        region.lock_rotation = False    
                    
def set_view(screen,mode):
    if mode == "2D":
        active_space_data = bpy.context.space_data
        if active_space_data != None:
            if hasattr(active_space_data,"region_3d"):
                region_3d = active_space_data.region_3d
                bpy.ops.view3d.viewnumpad(type='FRONT')
                if region_3d.view_perspective != "ORTHO":
                    bpy.ops.view3d.view_persportho()  
    elif mode == "3D":
        active_space_data = bpy.context.space_data
        if active_space_data != None:
            if hasattr(active_space_data,"region_3d"):
                region_3d = active_space_data.region_3d
                if region_3d.view_perspective == "ORTHO":
                    bpy.ops.view3d.view_persportho()        


def set_middle_mouse_move(enable):
    km = bpy.context.window_manager.keyconfigs.addon.keymaps["3D View"]
    km.keymap_items["view3d.move"].active = enable
    
def assign_tex_to_uv(image,uv):
    for i,data in enumerate(uv.data):
        uv.data[i].image = image
        
def set_bone_group(self, armature, pose_bone,group = "ik_group" ,theme = "THEME09"):
    new_group = None
    if group not in armature.pose.bone_groups:
        new_group = armature.pose.bone_groups.new(group)
        new_group.color_set = theme
    else:
        new_group = armature.pose.bone_groups[group]
    pose_bone.bone_group = new_group

last_sprite_object = None        
def get_sprite_object(obj):
    global last_sprite_object
    
    context = bpy.context
    if obj != None:
        if "sprite_object" in obj:
            last_sprite_object = obj.name
            return obj
        elif obj.parent != None:
            return get_sprite_object(obj.parent)
    
    if last_sprite_object != None and last_sprite_object in bpy.data.objects:
        return bpy.data.objects[last_sprite_object]
    return None 
        
def get_armature(obj):
    if obj != None and obj.type != "ARMATURE":
        for child in obj.children:
            if child.type == "ARMATURE":
                return child
    else:
        return obj        
    return None 

def get_bounds_and_center(obj):
    sprite_center = Vector((0,0,0))
    bounds = []
    for i,corner in enumerate(obj.bound_box):
        world_corner = obj.matrix_world * Vector(corner)
        sprite_center += world_corner
        if i in [0,1,4,5]:
            bounds.append(world_corner)
    sprite_center = sprite_center*0.125
    return[sprite_center,bounds]
    
    
def ray_cast(start,end,list=[]):
    if b_version_bigger_than((2,76,0)):
        end = end - start
    result = bpy.context.scene.ray_cast(start,end)
    
    if b_version_bigger_than((2,76,0)):
        result = [result[0],result[4],result[5],result[1],result[2]]
    
    if result[0]:
        if result not in list:
            list.append(result)
        else:
            return list    
        
        dir_vec = (end - start).normalized()
        new_start = result[3] + (dir_vec*0.000001)
        return ray_cast(new_start,end,list)
    else:
        return list
    
def lock_sprites(context, obj, lock):
    for child in obj.children:
        if child.type == "MESH":
            if lock:
                child.hide_select = True
                child.select = False
                if child == context.scene.objects.active:
                    context.scene.objects.active = child.parent
            else:
                child.hide_select = False   
        if len(child.children) > 0:
            return lock_sprites(context,child,lock)
    return      


def get_children(context,obj,ob_list=[]):
    if obj != None:
        for child in obj.children:
            ob_list.append(child)
            if len(child.children) > 0:
                get_children(context,child,ob_list)
    return ob_list  

def handle_uv_items(context,obj):
    uv_coords = obj.data.uv_layers[obj.data.uv_layers.active.name].data
    ### add uv items
    for i in range(len(uv_coords)-len(obj.coa_uv_default_state)):
        item = obj.coa_uv_default_state.add()
    ### remove unneeded uv items    
    if len(uv_coords) < len(obj.coa_uv_default_state):
        for i in range(len(obj.coa_uv_default_state) - len(uv_coords)):
            obj.coa_uv_default_state.remove(0)

def set_uv_default_coords(context,obj):
    uv_coords = obj.data.uv_layers[obj.data.uv_layers.active.name].data
    ### add uv items
    for i in range(len(uv_coords)-len(obj.coa_uv_default_state)):
        item = obj.coa_uv_default_state.add()
    ### remove unneeded uv items    
    if len(uv_coords) < len(obj.coa_uv_default_state):
        for i in range(len(obj.coa_uv_default_state) - len(uv_coords)):
            obj.coa_uv_default_state.remove(0)

    ### set default uv coords
    frame_size = Vector((1 / obj.coa_tiles_x,1 / obj.coa_tiles_y))
    pos_x = frame_size.x * (obj.coa_sprite_frame % obj.coa_tiles_x)
    pos_y = frame_size.y *  -int(int(obj.coa_sprite_frame) / int(obj.coa_tiles_x))
    frame = Vector((pos_x,pos_y))
    offset = Vector((0,1-(1/obj.coa_tiles_y)))
    
    
    for i,coord in enumerate(uv_coords):    
        uv_vec_x = (coord.uv[0] - frame[0]) * obj.coa_tiles_x 
        uv_vec_y = (coord.uv[1] - offset[1] - frame[1]) * obj.coa_tiles_y
        uv_vec = Vector((uv_vec_x,uv_vec_y)) 
        obj.coa_uv_default_state[i].uv = uv_vec   
                        
def update_uv(context,obj):
    return
    if "coa_sprite" in obj and obj.mode == "OBJECT":
        sprite_object = get_sprite_object(obj)
        
        frame_size = Vector((1 / obj.coa_tiles_x,1 / obj.coa_tiles_y))
        pos_x = frame_size.x * (obj.coa_sprite_frame % obj.coa_tiles_x)
        pos_y = frame_size.y *  -int(int(obj.coa_sprite_frame) / int(obj.coa_tiles_x))
        frame = Vector((pos_x,pos_y))
        offset = Vector((0,1-(1/obj.coa_tiles_y)))
        
        for i,coord in enumerate(obj.data.uv_layers[obj.data.uv_layers.active.name].data):
            if i < len(obj.coa_uv_default_state):
                coord.uv = Vector((obj.coa_uv_default_state[i].uv[0] / obj.coa_tiles_x , obj.coa_uv_default_state[i].uv[1]/ obj.coa_tiles_y)) + frame + offset     
        
def update_verts(context,obj):
    return
    if "coa_sprite" in obj:
        sprite_object = get_sprite_object(obj)
        armature = get_armature(sprite_object)
        if armature != None:
            armature_pose_position = armature.data.pose_position
            armature.data.pose_position = "REST"
            armature.update_tag()
            bpy.context.scene.update()
        
        mode_prev = obj.mode
        
        
        hide = bool(obj.data.coa_hide_base_sprite)
        obj.data.coa_hide_base_sprite = False
        obj.coa_dimensions_old = Vector(obj.dimensions)
        obj.data.coa_hide_base_sprite = hide    
        
        
        spritesheet = obj.material_slots[0].material.texture_slots[0].texture.image
        assign_tex_to_uv(spritesheet,obj.data.uv_textures[0])
        
        sprite_sheet_width = obj.data.uv_textures[0].data[0].image.size[0]
        sprite_sheet_height = obj.data.uv_textures[0].data[0].image.size[1]
        
        scale_x = round(obj.coa_sprite_dimension[0] / sprite_sheet_width,5)
        scale_y = round(obj.coa_sprite_dimension[2] / sprite_sheet_height,5)
        
        sprite_object = get_sprite_object(obj)
        
        for vert in obj.data.vertices:
            vert.co[0] = (vert.co[0] / obj.coa_dimensions_old[0] * sprite_sheet_width / obj.coa_tiles_x * scale_x * obj.matrix_local.to_scale()[0])
            vert.co[2] = (vert.co[2] / obj.coa_dimensions_old[2] * sprite_sheet_height / obj.coa_tiles_y * scale_y * obj.matrix_local.to_scale()[2])
            
        bpy.ops.object.mode_set(mode=mode_prev)    
        
        if armature != None:
            armature.data.pose_position = armature_pose_position

def set_z_value(context,obj,z):
    scale = get_addon_prefs(context).sprite_import_export_scale
    obj.location[1] = -z  * scale

def set_modulate_color(obj,context,color):
    r_engine = context.scene.render.engine
    if r_engine in ["BLENDER_INTERNAL","BLENDER_GAME"]:
        if obj.type == "MESH":
            if not obj.material_slots[0].material.use_object_color:
                obj.material_slots[0].material.use_object_color = True
            obj.color[:3] = color
    elif r_engine in ["CYCLES"]:
        if obj.type == "MESH":
            node_color_modulate = None
            node_tree = obj.active_material.node_tree
            if node_tree != None:
                for node in node_tree.nodes:
                    if "coa_modulate_color" in node:
                        node_color_modulate = node
                        break
            if node_color_modulate != None:
                node_color_modulate.outputs[0].default_value[:3] = color        
            

def change_slot_mesh_data(context,obj):
    if len(obj.coa_slot) > 0:
        slot_len = len(obj.coa_slot)-1
        obj["coa_slot_index"] = min(obj.coa_slot_index,max(0,len(obj.coa_slot)-1))
        
        idx = max(min(obj.coa_slot_index,len(obj.coa_slot)-1),0)
        
        slot = obj.coa_slot[idx]
        obj = slot.id_data
        obj.data = slot.mesh
        set_alpha(obj,context,obj.coa_alpha)
        for slot2 in obj.coa_slot:
            if slot != slot2:
                slot2["active"] = False
            else:
                slot2["active"] = True 
        if "coa_base_sprite" in obj.modifiers:
            if slot.mesh.coa_hide_base_sprite:
                obj.modifiers["coa_base_sprite"].show_render = True
                obj.modifiers["coa_base_sprite"].show_viewport = True
            else:
                obj.modifiers["coa_base_sprite"].show_render = False
                obj.modifiers["coa_base_sprite"].show_viewport = False

def display_children(self, context, obj):
    obj = get_sprite_object(obj)
    if obj != None:
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        if context.scene.coa_display_all:
            row.prop(context.scene,"coa_display_all",text="",toggle=True,icon="DISCLOSURE_TRI_RIGHT")
        else:    
            row.prop(context.scene,"coa_display_all",text="",toggle=True,icon="DISCLOSURE_TRI_DOWN")
            row.prop(context.scene,"coa_display_length",text="Length")
            row.prop(context.scene,"coa_display_page",text="Page")
        box = col.box()
        col = box.column(align=True)
        sprite_object = get_sprite_object(obj)
        children = get_children(context,sprite_object,ob_list=[])
        
        list1 = []
        list2 = []
        for child in children:
            if child.type != "CAMERA":
                list1.append(child)
            else:
                list2.append(child)
        children = list1
        children += list2
        row = col.row(align=True)
        row.label(text="",icon="OOPS")
        row.prop(obj,"coa_filter_names",text="",icon="VIEWZOOM")
        if sprite_object != None:
            if sprite_object.coa_favorite:
                row.prop(sprite_object,"coa_favorite",text="",icon="SOLO_ON")
            else:
                row.prop(sprite_object,"coa_favorite",text="",icon="SOLO_OFF")
        
        col = box.column(align=True)
        
        current_display_item = 0
        ### Sprite Objects display for all that are in active Scene
        disable_list = sprite_object.coa_edit_mesh or sprite_object.coa_edit_armature or sprite_object.coa_edit_weights or sprite_object.coa_edit_shapekey
        
        for obj2 in context.scene.objects:
            if get_sprite_object(obj2) == obj2:
                in_range = current_display_item in range(context.scene.coa_display_page * context.scene.coa_display_length , context.scene.coa_display_page * context.scene.coa_display_length + context.scene.coa_display_length)
                
                if in_range or context.scene.coa_display_all:
                    row = col.row(align=True)
                    subrow = row.row(align=True)
                    if disable_list:
                        subrow.enabled = False
                    icon = "LAYER_USED"
                    if obj2.select:
                        icon = "LAYER_ACTIVE"
                    subrow.label(text="",icon=icon)
                    if obj2.type == "EMPTY":
                        subrow.label(text="",icon="EMPTY_DATA")
                    elif obj2.type == "ARMATURE":
                        subrow.label(text="",icon="ARMATURE_DATA")
                    if get_sprite_object(obj2) == sprite_object:
                        if obj2.coa_show_children and get_sprite_object(obj2) == sprite_object:
                            subrow.prop(obj2,"coa_show_children",text="",icon="TRIA_DOWN",emboss=False)
                        else:
                            subrow.prop(obj2,"coa_show_children",text="",icon="TRIA_RIGHT",emboss=False) 
                    op = subrow.operator("object.coa_select_child",text=obj2.name,emboss=False)
                    op.mode = "object"
                    op.ob_name = obj2.name
                    
                    op = subrow.operator("coa_tools.view_sprite",icon="ZOOM_SELECTED",text="",emboss=False)
                    op.type = "VIEW_ALL"
                    op.name = obj2.name
                    
                    row2 = subrow.row()
                    if not obj2.coa_change_z_ordering:
                        row2.active = False
                    row2.prop(obj2,"coa_change_z_ordering",text="",icon="SORTALPHA",emboss=False)
                
                current_display_item += 1
                if obj2 == sprite_object:
                    draw_children(self,context,sprite_object,layout,box,row,col,children,obj,current_display_item, disable_list)
            

def favorite_bones(armature):
    for bone in armature.data.bones:
        if bone.coa_favorite:
            return True
    return False
            
def filter_bone_name(armature,filter):
    for bone in armature.data.bones:
        if filter.upper() in bone.name.upper():
            return True
    return False

def draw_children(self,context,sprite_object,layout,box,row,col,children,obj,current_display_item, disable_list):    
    obj = get_sprite_object(obj)
    ### Sprite Object Children Display
    
    if disable_list:
        if sprite_object.coa_edit_mesh:
            box.row().prop(sprite_object, "coa_edit_mesh", text="", toggle=True, icon="LOOP_BACK")
        if sprite_object.coa_edit_armature:
            box.row().prop(sprite_object, "coa_edit_armature", text="", toggle=True, icon="LOOP_BACK")
        if sprite_object.coa_edit_weights:
            box.row().prop(sprite_object, "coa_edit_weights", text="", toggle=True, icon="LOOP_BACK")
        if sprite_object.coa_edit_shapekey:
            box.row().prop(sprite_object, "coa_edit_shapekey", text="", toggle=True, icon="LOOP_BACK")

    
        
    if sprite_object != None and sprite_object.coa_show_children:
        children = sorted(children, key=lambda x: x.location[1] if type(x) == bpy.types.Object else x.name,reverse=False)
        children = sorted(children, key=lambda x: x.type if type(x) == bpy.types.Object else x.name,reverse=False)
        if len(children) > 1 and type(children[1]) == bpy.types.Object and children[1].type == "CAMERA":
            children.insert(0,children.pop(1))
        for i,child in enumerate(children):
                
            child_obj = child
            in_range = current_display_item in range(context.scene.coa_display_page * context.scene.coa_display_length , context.scene.coa_display_page * context.scene.coa_display_length + context.scene.coa_display_length)
            
            name_found = obj.coa_filter_names.upper() in child.name.upper() and not obj.coa_filter_names == ""
            current_display_item += 1
            if in_range or context.scene.coa_display_all or name_found:
                if (sprite_object.coa_favorite and child.coa_favorite) or not sprite_object.coa_favorite or (child.type == "ARMATURE" and (favorite_bones(child))):
                    if obj.coa_filter_names.upper() in child.name.upper():
                        
                        row = col.row(align=True)
                        subrow2 = row.row(align=True)
                        subrow3 = row.row(align=True)
                        if disable_list:
                            subrow2.enabled = False
                        
                        if child.type == "MESH" and len(child.data.vertices) > 4 and child.data.coa_hide_base_sprite == False and "coa_base_sprite" in child.vertex_groups and "coa_base_sprite" in child.modifiers:
                            subrow = row.row()
                            subrow.alignment = "LEFT"
                            subrow.prop(child.data,'coa_hide_base_sprite',text="",icon="ERROR",emboss=False)
                        else:
                            subrow2.separator()
                            subrow2.separator()
                            subrow2.separator()
                        name = child.name
                        icon = "LAYER_USED"
                        if child.select:# and not child.hide:
                            icon = "LAYER_ACTIVE"
                        subrow2.label(text="",icon=icon)
                        if child.type == "ARMATURE":
                            subrow2.label(text="",icon="ARMATURE_DATA")
                        elif child.type == "MESH":
                            #row.label(text="",icon="TEXTURE")
                            op = subrow2.operator("coa_tools.advanced_settings",text="",icon="TEXTURE",emboss=False)
                            op.obj_name = child.name
                        elif child.type == "CAMERA":
                            
                            subrow2.label(text="",icon="CAMERA_DATA")
                        
                        
                        op = subrow2.operator("object.coa_select_child",text=name,emboss=False)
                        op.mode = "object"
                        op.ob_name = child.name
                        
                        if child.type == "ARMATURE":
                            if child.coa_show_bones:
                                subrow2.prop(child,"coa_show_bones",text="",icon="TRIA_DOWN",emboss=False)
                            else:
                                subrow2.prop(child,"coa_show_bones",text="",icon="TRIA_LEFT",emboss=False) 
                        
                        if child.type == "MESH" and child.coa_type == "SLOT":
                            if child.coa_slot_show:
                                subrow2.prop(child,"coa_slot_show",text="",icon="TRIA_DOWN",emboss=False)
                            else:
                                subrow2.prop(child,"coa_slot_show",text="",icon="TRIA_LEFT",emboss=False)    
                            
                            if sprite_object.coa_edit_armature:
                                op = subrow2.operator("coa_tools.bind_mesh_to_bones", text="", icon="BONE_DATA", emboss=False)
                                op.ob_name = child.name
    #                    if child.type == "MESH":
    #                        op = row.operator("import.coa_reimport_sprite",text="",icon="FILE_REFRESH",emboss=False)
    #                        op.name = child.name
                        
                        if not sprite_object.coa_change_z_ordering:
                            if child.coa_favorite:
                                subrow2.prop(child,"coa_favorite",emboss=False,text="",icon="SOLO_ON")
                            else:
                                subrow2.prop(child,"coa_favorite",emboss=False,text="",icon="SOLO_OFF")
                                
                                
                            if child.coa_hide:
                                icon = "VISIBLE_IPO_OFF"
                                if not child.hide:
                                    icon = "VISIBLE_IPO_ON"
                                subrow2.prop(child,"coa_hide",emboss=False,text="",icon=icon)
                            else:   
                                subrow2.prop(child,"coa_hide",emboss=False,text="",icon="VISIBLE_IPO_ON")
                            if child.coa_hide_select:   
                                subrow2.prop(child,"coa_hide_select",emboss=False,text="",icon="RESTRICT_SELECT_ON")
                            else:   
                                subrow2.prop(child,"coa_hide_select",emboss=False,text="",icon="RESTRICT_SELECT_OFF")   
                        else:
                            children_names = []
                            for child in children:
                                children_names.append(child.name)
                            
                            if child_obj.type == "MESH":      
                                op = subrow2.operator("coa_tools.change_z_ordering",text="",icon="TRIA_DOWN")
                                op.index = i
                                op.direction = "DOWN"
                                op.active_sprite = children[i].name
                                op.all_sprites = str(children_names)
                                op = row.operator("coa_tools.change_z_ordering",text="",icon="TRIA_UP")
                                op.index = i
                                op.direction = "UP"
                                op.active_sprite = children[i].name
                                op.all_sprites = str(children_names)
                            
                        #row.prop(child,"hide_select",emboss=False,text="")
                        
                        if child.type == "MESH" and child.coa_type == "SLOT" and child.coa_slot_show:
                            for i,slot in enumerate(child.coa_slot):
                                row = col.row()
                                subrow = row.row(align=True)
                                subrow.alignment = "LEFT"
                                subrow.separator()
                                subrow.separator()
                                subrow.separator()
                                subrow.separator()
                                subrow.separator()
                                subrow.separator()
                                    
                                if slot.mesh != None:
                                    name = slot.mesh.name
                                else:
                                    name = "No Data found"    
                                    subrow.label(text="",icon="ERROR")
                                if slot.active:
                                    subrow.prop(slot,"active",text=name,icon="RADIOBUT_ON",emboss=False)
                                else:
                                    subrow.prop(slot,"active",text=name,icon="RADIOBUT_OFF",emboss=False)
                                
                                subrow = row.row(align=True)
                                
                                op = subrow.operator("coa_tools.move_slot_item",icon="TRIA_DOWN",emboss=False,text="")
                                op.idx = i
                                op.ob_name = child.name
                                op.mode = "DOWN"
                                op = subrow.operator("coa_tools.move_slot_item",icon="TRIA_UP",emboss=False,text="")
                                op.idx = i
                                op.ob_name = child.name
                                op.mode = "UP"
                                
                                subrow.alignment = "RIGHT"
                                op = subrow.operator("coa_tools.remove_from_slot",icon="PANEL_CLOSE",emboss=False,text="")
                                op.idx = i
                                op.ob_name = child.name
                        
                        if child.type == "MESH" and sprite_object.coa_edit_armature:
                            op = subrow3.operator("coa_tools.bind_mesh_to_bones", text="", icon="BONE_DATA", emboss=False)
                            op.ob_name = child.name
                        
                        if child.type == "ARMATURE":
                            if (not sprite_object.coa_favorite and child.coa_show_bones) or sprite_object.coa_favorite:
                                for bone in child.data.bones:
                                    if (sprite_object.coa_favorite and bone.coa_favorite or not sprite_object.coa_favorite):
                                        draw_bone_entry(self,bone,subrow2,col,child)
                        
                                        
                                            
def draw_bone_entry(self,bone,row,col,child,indentation_level=0):
    row = col.row(align=True)
    row.separator()
    row.separator()
    row.separator()
    row.separator()
    row.separator()
    row.separator()
    icon = "LAYER_USED"
    if bone.select:
        icon = "LAYER_ACTIVE"   
    row.label(text="",icon=icon)
    row.label(text="",icon="BONE_DATA")
    bone_name = ""+bone.name
    op = row.operator("object.coa_select_child",text=bone_name,emboss=False)
    op.mode = "bone"
    op.ob_name = child.name
    op.bone_name = bone.name
    if bone.coa_favorite:
        row.prop(bone,"coa_favorite",emboss=False,text="",icon="SOLO_ON")
    else:
        row.prop(bone,"coa_favorite",emboss=False,text="",icon="SOLO_OFF")
    if bone.hide:
        row.prop(bone,"coa_hide",text="",emboss=False,icon="VISIBLE_IPO_OFF")
    else:   
        row.prop(bone,"coa_hide",text="",emboss=False,icon="VISIBLE_IPO_ON")
    if bone.hide_select:
        row.prop(bone,"coa_hide_select",text="",emboss=False,icon="RESTRICT_SELECT_ON")
    else:   
        row.prop(bone,"coa_hide_select",text="",emboss=False,icon="RESTRICT_SELECT_OFF")          
