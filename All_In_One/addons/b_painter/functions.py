'''
Copyright (C) 2017 Andreas Esau
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
import os
from shutil import copyfile
from mathutils import Vector
import math

def generate_combine_alpha_node_group(context):
    if "BPainterCombineAlpha" not in bpy.data.node_groups:
        node_group = bpy.data.node_groups.new("BPainterCombineAlpha","ShaderNodeTree")
        
        group_input = node_group.nodes.new("NodeGroupInput")
        group_input.select = False
        group_output = node_group.nodes.new("NodeGroupOutput")
        group_output.select = False
        math_subtract = node_group.nodes.new("ShaderNodeMath")
        math_subtract.operation = "SUBTRACT"
        math_subtract.inputs[0].default_value = 1.0
        math_subtract.select = False
        math_multiply = node_group.nodes.new("ShaderNodeMath")
        math_multiply.operation = "MULTIPLY"
        math_multiply.select = False
        math_add = node_group.nodes.new("ShaderNodeMath")
        math_add.operation = "ADD"
        math_add.select = False
        
        group_input.location = [0,0]
        group_output.location = [460,0]
        math_subtract.location = [160,-20]
        math_multiply.location = [260,-20]
        math_add.location = [360,0]
        
        math_subtract.hide = True
        math_multiply.hide = True
        math_add.hide = True
        
        a1 = node_group.inputs.new("NodeSocketFloat","Alpha1")
        a1.max_value = 1.0
        a1.min_value = 0.0
        a2 = node_group.inputs.new("NodeSocketFloat","Alpha2")
        a2.max_value = 1.0
        a2.min_value = 0.0
        a = node_group.outputs.new("NodeSocketFloat","Alpha")
        a.max_value = 1.0
        a.min_value = 0.0
        
        node_group.links.new(group_input.outputs["Alpha1"],math_subtract.inputs[1])
        node_group.links.new(group_input.outputs["Alpha1"],math_add.inputs[0])
        node_group.links.new(group_input.outputs["Alpha2"],math_multiply.inputs[1])
        node_group.links.new(math_subtract.outputs["Value"],math_multiply.inputs[0])
        node_group.links.new(math_multiply.outputs["Value"],math_add.inputs[1])
        node_group.links.new(math_add.outputs["Value"],group_output.inputs["Alpha"])
    return bpy.data.node_groups["BPainterCombineAlpha"]  

def generate_paint_channel_alpha(context,node_group):
    generate_combine_alpha_node_group(context)
    nodes = node_group.nodes
    
    layers = []
    for node in nodes:
        if "BPainterAlpha" in node:
            node_group.nodes.remove(node)
            continue
        
        if node.type == "MIX_RGB" and node.label != "BPaintMask" and node.blend_type == "MIX":
            layer = {"mix_node":node,"mask_node":None}
            if len(node.outputs["Color"].links) == 1:
                next_node = node.outputs["Color"].links[0].to_node
                if next_node.label == "BPaintMask":
                    layer["mask_node"] = next_node
                
                
            layers.append(layer)
    layers.sort(key=lambda x:x["mix_node"].location[0])
    
    alpha1 = None
    for i,layer in enumerate(layers):
        if i + 1 <= len(layers)-1:
            next_layer = layers[i+1]
            next_layer_2 = layers[i+2] if i + 2 <= len(layers)-1 else None
            alpha1 = layer["mix_node"].inputs["Fac"].links[0].from_node if alpha1 == None else alpha1
            alpha2 = next_layer["mix_node"].inputs["Fac"].links[0].from_node
            
            alpha_mix = node_group.nodes.new("ShaderNodeGroup")
            alpha_mix["BPainterAlpha"] = True
            alpha_mix.node_tree = bpy.data.node_groups["BPainterCombineAlpha"]
            alpha_mix.location[0] = next_layer["mix_node"].location[0]
            alpha_mix.location[1] = next_layer["mix_node"].location[1] -280
            alpha_mix.hide = True
            alpha_mix.select = False
            
            subtract_node = None
            if next_layer["mask_node"] != None:
                subtract_node = node_group.nodes.new("ShaderNodeMath")
                subtract_node["BPainterAlpha"] = True
                subtract_node.location[0] = next_layer["mix_node"].location[0]
                subtract_node.location[1] = next_layer["mix_node"].location[1] -240
                subtract_node.operation = "SUBTRACT"
                subtract_node.hide = True
                subtract_node.select = False
            
                
            ### link nodes    
            if subtract_node != None:
                node_group.links.new(next_layer["mask_node"].inputs["Fac"].links[0].from_node.outputs["Color"],subtract_node.inputs[1])
                node_group.links.new(alpha2.outputs["Value"],subtract_node.inputs[0])
                alpha2 = subtract_node
                
            
            node_group.links.new(alpha1.outputs[0],alpha_mix.inputs["Alpha2"])
            node_group.links.new(alpha2.outputs[0],alpha_mix.inputs["Alpha1"])
            
            if next_layer_2 == None:
                if len(node_group.nodes["Group Output"].inputs["Alpha"].links) > 0:
                    node_group.links.remove(node_group.nodes["Group Output"].inputs["Alpha"].links[0])
                node_group.links.new(alpha_mix.outputs[0],node_group.nodes["Group Output"].inputs["Alpha"],verify_limits=False)
            alpha1 = alpha_mix
        elif len(layers) == 1:
            alpha1 = layer["mix_node"].inputs["Fac"].links[0].from_node
            node_group.links.new(alpha1.outputs[0],node_group.nodes["Group Output"].inputs["Alpha"])
            
def set_brush_alpha_lock(context,mat):
    prefs = get_addon_prefs(context)
    
    if prefs.use_layer_alpha_lock:
        brush = context.tool_settings.image_paint.brush if context.tool_settings != None and context.tool_settings.image_paint != None else None
        layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index] if mat != None and len(mat.b_painter.paint_layers) > 0 and mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1 else None
        if brush != None and layer != None:
            img = None
            if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
                img = bpy.data.images[layer.name] if layer.name in bpy.data.images else None
            elif context.scene.render.engine in ["CYCLES"]:
                img = bpy.data.images[layer.img_name] if layer.img_name in bpy.data.images else None
            if img != None:
                brush.use_alpha = not(img.b_painter.lock_alpha)

def get_node_group_recursive(node_tree):
    list = []
    if node_tree != None:
        for node in node_tree.nodes: 
            if node.type == "GROUP" and node.label == "BPaintLayer" and node not in list:
                list.append(node)
            if node.type == "GROUP" and node.label != "BPaintLayer":
                list += get_node_group_recursive(node.node_tree)
    return list

def check_paint_channels_count(context,obj,mat):
    node_tree = mat.node_tree
    length = 0
    if node_tree != None:
        for group in get_node_group_recursive(node_tree):
            length += 1       
    return length   

def check_layer_stack_cycles(context,obj,mat):
    layer_stack = []
    if mat.b_painter.paint_channel_active != "Unordered Images":
        node_tree = bpy.data.node_groups[mat.b_painter.paint_channel_active] if mat.b_painter.paint_channel_active in bpy.data.node_groups else None
        
        if node_tree != None:
            all_layer_nodes = get_layer_nodes(node_tree)
            
            for node in all_layer_nodes:
                if node[1] in ["PAINT_LAYER","ADJUSTMENT_LAYER","PROCEDURAL_TEXTURE"]:
                    layer_stack.append(node)
    else:
        node_tree = mat.node_tree
        tex_nodes = get_tex_recursive(node_tree)             
        for node in tex_nodes:
            if node.image != None:
                layer_stack.append(node)
    return len(layer_stack)

def check_layer_stack_bi(context,obj,mat):
    for i,layer in enumerate(mat.b_painter.paint_layers):
        tex_slot = mat.texture_slots[layer.index]
        tex = tex_slot.texture if tex_slot != None else None
        if tex_slot == None:
            return "UPDATE"
        elif tex == None:
            return "UPDATE"
        elif tex.image == None:
            return "UPDATE"
        elif tex.image.name != layer.name:
            return "UPDATE"
    return "PASS_THROUGH" 

def linear_to_srgb(c):
    if (c < 0.0031308):
        c = 0.0 if c < 0.0 else c * 12.92
        return c
    else:
        return 1.055 * math.pow(c, 1.0 / 2.4) - 0.055

def srgb_to_linear(c):
    if (c < 0.04045):
        c = 0.0 if c < 0.0 else c * (1.0 / 12.92)
        return c
    else:
        return math.pow((c + 0.055) * (1.0 / 1.055), 2.4)

### setup blendfile when loaded first time. 
def setup_b_painter():
    context = bpy.context
    settings = context.tool_settings
    unified_paint_settings = settings.unified_paint_settings
    image_paint = settings.image_paint
    
    unified_paint_settings.use_unified_size = True
    unified_paint_settings.use_unified_strength = True
    unified_paint_settings.use_unified_color = True
    unified_paint_settings.strength = 1.0
    
    unified_paint_settings.use_pressure_size = True
    unified_paint_settings.use_pressure_strength = True
    unified_paint_settings.color = [0,0,0]
    unified_paint_settings.secondary_color = [1,1,1]
    
    image_paint.seam_bleed = 4
    image_paint.normal_angle = 90
    
    try:
        bpy.context.scene.b_painter_brush = "Brush Default"
    except:
        pass    
    
    try:
        bpy.context.scene.b_painter_tex_stencil_categories = "Stencil Shapes"
    except:
        pass 

def get_addon_prefs(context):
    addon_name = __name__.split(".")[0]
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[addon_name].preferences
    return addon_prefs

def set_material_shading(self,obj,shadeless=True,ignore_prop=False):
    for slot in obj.material_slots:
        if slot.material != None:
            mats = get_materials_recursive(slot.material,slot.material.node_tree)
            for mat in mats:
                if shadeless == True:
                    if ignore_prop:
                        mat["shading_mode"] = bool(mat.use_shadeless)
                    mat.use_shadeless = True
                else:
                    if "shading_mode" in mat:    
                        mat.use_shadeless = mat["shading_mode"]
                        del(mat["shading_mode"])
                    else:
                        mat.use_shadeless = False    

def set_active_uv_layout(self,context):
    ob = context.active_object
    mat = ob.active_material
    if ob.mode == "TEXTURE_PAINT" and mat != None:
        if len(mat.b_painter.paint_layers) > 0:
            if "paint_layers_index" not in mat.b_painter:
                mat.b_painter["paint_layers_index"] = 0    
            mat.b_painter["paint_layers_index"] = min(mat.b_painter["paint_layers_index"], len(mat.b_painter.paint_layers)-1)
            active_paint_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
            if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
                active_tex = mat.texture_slots[active_paint_layer.index]
                active_uv_layer = active_tex.uv_layer
                
                if active_uv_layer != "":
                    ob.data.uv_textures.active = ob.data.uv_textures[active_uv_layer]
                else:    
                    ob.data.uv_textures.active = ob.data.uv_textures[0]
            elif context.scene.render.engine in ["CYCLES"] and active_paint_layer.layer_type == "PAINT_LAYER":
                active_paint_channel = mat.b_painter.paint_channel_active
                if active_paint_channel != "Unordered Images":
                    node_tree = bpy.data.node_groups[active_paint_channel]
                else:
                    node_tree = mat.node_tree
                    
                if node_tree != None:    
                    if active_paint_layer.tex_node_name in node_tree.nodes:
                        tex_node = node_tree.nodes[active_paint_layer.tex_node_name]
                        if len(tex_node.inputs["Vector"].links) > 0:
                            if tex_node.inputs["Vector"].links[0].from_node.type == "UVMAP":
                                uv_map_node = tex_node.inputs["Vector"].links[0].from_node
                                if uv_map_node.uv_map == "":
                                    ob.data.uv_textures.active = ob.data.uv_textures[0]
                                else:
                                    if uv_map_node.uv_map in ob.data.uv_textures:
                                        ob.data.uv_textures.active = ob.data.uv_textures[uv_map_node.uv_map]
                        elif len(tex_node.inputs["Vector"].links) == 0:
                            ob.data.uv_textures.active = ob.data.uv_textures[0]

def copy_dir(src,dst,overwrite=False):
    for subdir, dirs, files in os.walk(src):
        subdir_relpath = os.path.relpath(subdir,src)
        dst_dir = os.path.join(dst,subdir_relpath)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file in files:
            src_file = os.path.join(subdir, file)
            dst_file = os.path.join(dst_dir,file)
            if os.path.exists(dst_file) and overwrite:
                os.remove(dst_file)
            elif not os.path.exists(dst_file):
                copyfile(src_file,dst_file)

def get_context_node_tree(context):
    for area in context.screen.areas:
        if area.type == "NODE_EDITOR":
            node_editor = area.spaces[0]
            return node_editor.edit_tree

def b_version_bigger_than(version):
    if bpy.app.version > version:
        return True
    else:
        return False
    
def b_version_smaller_than(version):
    if bpy.app.version < version:
        return True
    else:
        return False

def set_active_paint_layer(self,obj):
    context = bpy.context
    update_all_paint_layers(self,context)
    mat = obj.active_material
    if mat != None:
        mat.b_painter.paint_layers_index = min(mat.b_painter.paint_layers_index,len(mat.b_painter.paint_layers)-1)

def get_node_recursive(node_tree,group_list=[],type="GROUP"): ### replace this function by get_tex_recursive in the future and adapt all code to it -> remove list argument
    for node in node_tree.nodes:
        if node.type == type:
            group_list.append(node)     
        if node.type == "GROUP":
            get_node_recursive(node.node_tree,group_list,type=type)
    return group_list
    
def get_tex_recursive(node_tree,exclude_label="-1"):
    list = []
    if node_tree != None:
        for node in node_tree.nodes:          
            if node.type == "TEX_IMAGE" and node.image != None and exclude_label not in node.label:
                list.append(node)
            if node.type == "GROUP":
                list += get_tex_recursive(node.node_tree,exclude_label)
    return list

def get_materials_recursive(mat,node_tree):
    list = []
    if node_tree != None and mat.use_nodes and bpy.context.scene.render.engine in ["BLENDER_GAME","BLENDER_RENDER"]:
        for node in node_tree.nodes:          
            if node.type in ["MATERIAL","MATERIAL_EXT"] and node.material != None:
                list.append(node.material)
            if node.type == "GROUP":
                list += get_materials_recursive(mat,node.node_tree)
        return list
    else:
        if mat not in list:
            return list + [mat]
        else:
            return list  
        
def get_paint_channel_info(mat,context):
    node_tree = mat.node_tree
    channel_info = mat.b_painter.paint_channel_info
    
    for i in range(len(channel_info)):
        channel_info.remove(0)
    
    if node_tree != None:
        paint_groups = get_node_recursive(node_tree,[]) 
        for group in paint_groups:
            if group.label == "BPaintLayer":
                item = channel_info.add()
                item.name = group.node_tree.name
                item.group_name = group.name 

def get_layer_nodes(node_tree):
    MIX_NODES = []
    group_input_node = [node for node in node_tree.nodes if node.type == "GROUP_INPUT"][0]
    
    node = group_input_node
    if len(node.outputs["Background Color"].links) > 1:
        output_socket = node.outputs["Background Color"].links[0].to_socket if node.outputs["Background Color"].links[0].to_node.label != "BPaintMask" else node.outputs["Background Color"].links[1].to_socket
    else:
        output_socket = node.outputs["Background Color"].links[0].to_socket if len(node.outputs["Background Color"].links) > 0 else None
            
    while output_socket != None:
        node = output_socket.node
        if node.type in ["MIX_RGB","CURVE_RGB","INVERT","HUE_SAT"]:
            if node.type == "MIX_RGB" and node.label not in ["BPaintMask","BPaintProcTex"]:
                MIX_NODES.append([node,"PAINT_LAYER"])
            elif node.type == "MIX_RGB" and node.label == "BPaintMask":        
                MIX_NODES.append([node,"MASK_LAYER"])
            elif node.type != "MIX_RGB" and node.label not in ["BPaintMask","BPaintProcTex"]:    
                MIX_NODES.append([node,"ADJUSTMENT_LAYER"])
            elif node.type == "MIX_RGB" and node.label == "BPaintProcTex":
                MIX_NODES.append([node,"PROCEDURAL_TEXTURE"])
                
        if "Color" in node.outputs and len(node.outputs["Color"].links) > 1:
            output_socket = node.outputs["Color"].links[0].to_socket if node.outputs["Color"].links[0].to_node.label != "BPaintMask" else node.outputs["Color"].links[1].to_socket
        else:    
            output_socket = node.outputs["Color"].links[0].to_socket if "Color" in node.outputs and len(node.outputs["Color"].links) > 0 else None    
                
    return MIX_NODES

    
def update_paint_layers(self,context,mat):
    ob = context.active_object
    if ob != None:
        if mat != None:
            paint_layers = mat.b_painter.paint_layers
            for i in range(len(paint_layers)):
                paint_layers.remove(0)
            
            layer_item = None
            if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
                for i,tex_slot in enumerate(mat.texture_slots):
                    if tex_slot != None:
                        tex = tex_slot.texture
                        if tex != None and tex.type == "IMAGE":
                            img = tex.image
                            if img != None:
                                layer_item = paint_layers.add()
                                layer_item.name = img.name
                                layer_item.index = i
                                layer_item.mat_name = mat.name
                                layer_item.tex_node_name = ""
                                layer_item.layer_type = "PAINT_LAYER"
                                            
            elif bpy.context.scene.render.engine == 'CYCLES':
                if mat.b_painter.paint_channel_active in bpy.data.node_groups and mat.b_painter.paint_channel_active != "Unordered Images":
                    node_tree = bpy.data.node_groups[mat.b_painter.paint_channel_active]
                    layer_nodes = get_layer_nodes(node_tree)
                    for i,layer_data in enumerate(layer_nodes):
                        layer_node = layer_data[0]
                        layer_type = layer_data[1]
                        if layer_type == "PAINT_LAYER":
                            tex_node = layer_node.inputs["Color2"].links[0].from_node if layer_node.inputs["Color2"].links[0].from_node.type == "TEX_IMAGE" else None
                            if tex_node != None and tex_node.image != None:
                                img = tex_node.image
                                layer_item = paint_layers.add()
                                layer_item.name = img.name
                                layer_item.index = i
                                layer_item.mat_name = mat.name
                                layer_item.tex_node_name = tex_node.name
                                layer_item.img_name = img.name
                                layer_item.mix_node_name = layer_node.name
                                layer_item.layer_type = "PAINT_LAYER"
                                layer_item.node_tree_name = tex_node.id_data.name
                                
                                ### get layer mask node and image
                                if len(layer_node.outputs["Color"].links) == 1 and layer_node.outputs["Color"].links[0].to_node.type == "MIX_RGB" and layer_node.outputs["Color"].links[0].to_node.label == "BPaintMask":
                                    mask_node = layer_node.outputs["Color"].links[0].to_node
                                    mask_invert_node = mask_node.inputs["Fac"].links[0].from_node
                                    mask_tex_node = mask_invert_node.inputs["Color"].links[0].from_node
                                    mask_img = mask_tex_node.image
                                    
                                    layer_item.mask_mix_node_name = mask_node.name
                                    layer_item.mask_tex_node_name = mask_tex_node.name
                                    layer_item.mask_img_name = mask_img.name
                                    
                                
                        elif layer_type in ["ADJUSTMENT_LAYER","PROCEDURAL_TEXTURE"]:
                            layer_item = paint_layers.add()
                            layer_item.name = layer_node.name
                            layer_item.index = i
                            layer_item.mat_name = mat.name
                            layer_item.layer_type = layer_type
                            layer_item.node_tree_name = layer_node.id_data.name
                            layer_item.mix_node_name = layer_node.name if layer_type == "PROCEDURAL_TEXTURE" else ""
                            if layer_type == "PROCEDURAL_TEXTURE":
                                proc_ramp_node = layer_node.inputs["Color2"].links[0].from_node
                                proc_tex_node = proc_ramp_node.inputs["Fac"].links[0].from_node
                                layer_item.proc_ramp_node_name = proc_ramp_node.name
                                layer_item.proc_tex_node_name = proc_tex_node.name
                                
                                
                                
                            ### get layer mask node and image
                            if len(layer_node.outputs["Color"].links) == 1 and layer_node.outputs["Color"].links[0].to_node.type == "MIX_RGB" and layer_node.outputs["Color"].links[0].to_node.label == "BPaintMask":
                                mask_node = layer_node.outputs["Color"].links[0].to_node
                                mask_invert_node = mask_node.inputs["Fac"].links[0].from_node
                                mask_tex_node = mask_invert_node.inputs["Color"].links[0].from_node
                                mask_img = mask_tex_node.image
                                
                                layer_item.mask_mix_node_name = mask_node.name
                                layer_item.mask_tex_node_name = mask_tex_node.name
                                layer_item.tex_node_name = mask_tex_node.name
                                layer_item.mask_img_name = mask_img.name
                                 
                elif mat.b_painter.paint_channel_active == "Unordered Images":
                    node_tree = mat.node_tree
                    
                    if node_tree != None:
                        tex_nodes = get_tex_recursive(node_tree)
                        tex_nodes.sort(key= lambda x: x.image.name) 
                        for i,tex_node in enumerate(tex_nodes):
                            if tex_node.type == "TEX_IMAGE" and tex_node.image != None and tex_node.label not in ["BPaintLayer","BPaintMask"]:
                                img = tex_node.image
                                layer_item = paint_layers.add()
                                layer_item.name = img.name
                                layer_item.index = i
                                layer_item.mat_name = mat.name
                                layer_item.tex_node_name = tex_node.name
                                layer_item.mix_node_name = ""
                                layer_item.node_tree_name = tex_node.id_data.name
                                layer_item.layer_type = "PAINT_LAYER"
                                layer_item.img_name = img.name
                
                get_paint_channel_info(mat,context)
                context.scene.update()
                
                ### update channel alpha
                if mat.b_painter.paint_channel_active in bpy.data.node_groups:
                    generate_paint_channel_alpha(context,bpy.data.node_groups[mat.b_painter.paint_channel_active]) 
                
            set_active_uv_layout(self,context)        
            
            ### set active mask/paint-layer and alpha lock
            if "layer_information" not in mat.b_painter:
                mat.b_painter["layer_information"] = {}
            for layer_item in mat.b_painter.paint_layers:
                if layer_item.name not in mat.b_painter["layer_information"]:
                    mat.b_painter["layer_information"][layer_item.name] = [1,0]
                elif layer_item.name in mat.b_painter["layer_information"] and len(mat.b_painter["layer_information"][layer_item.name]) == 2:
                    settings = list(mat.b_painter["layer_information"][layer_item.name])
                    settings.append(False)
                    mat.b_painter["layer_information"][layer_item.name] = settings
                else:
                    layer_item["mask_layer_active"] = mat.b_painter["layer_information"][layer_item.name][1]
                    layer_item["paint_layer_active"] = mat.b_painter["layer_information"][layer_item.name][0]
            for item in mat.b_painter["layer_information"].keys():
                if item not in mat.b_painter.paint_layers:
                    del(mat.b_painter["layer_information"][item])
                    
            #### set brush alpha settings
            set_brush_alpha_lock(context,mat)
            

def update_all_paint_layers(self,context):
    ob = context.active_object
    if ob != None:
        for mat_slot in ob.material_slots:
            
            if mat_slot.material != None:
                mat = mat_slot.material
                
                if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
                    update_paint_layers(self,context,mat)
                    
                    if mat.node_tree != None:
                        for node in mat.node_tree.nodes:
                            if node.type in ["MATERIAL","MATERIAL_EXT"]:# and node.material != None:
                                update_paint_layers(self,context,node.material)
                else:
                    if mat.node_tree != None:
                        update_paint_layers(self,context,mat)
            
def id_from_string(my_string):
    id = int(hash(my_string)/1000000000000)
    return id

def save_external(context,external_path,image):
    if os.path.splitext(image.name)[1] != ".png":
        path = os.path.join(external_path,image.name+".png")
    else:    
        path = os.path.join(external_path,image.name)
    
    if len(image.pixels) > 0:
        area = context.area
        area_type = area.type
        area.type = "IMAGE_EDITOR"
        area.spaces[0].image = image
        bpy.ops.image.save_as(filepath=path,check_existing=False)
        area.type = area_type
        if image.packed_file != None:
            image.unpack(method="WRITE_LOCAL")
        image.filepath = path
    else:
        msg = '"'+image.name+'"' + " Layer not found. Cannot be saved."
        bpy.ops.b_painter.report_message('INVOKE_SCREEN',type="WARNING",message=msg)
    
def save_images():
    context = bpy.context
    blend_path = bpy.data.filepath
    tex_dir_path = os.path.join(os.path.dirname(blend_path), "textures")
    
    if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:    
        for mat in bpy.data.materials:
            for layer in mat.b_painter.paint_layers:
                if layer.name in bpy.data.images:
                    image = bpy.data.images[layer.name]
                    external_path = bpy.path.abspath(mat.b_painter.external_path)
                    if bpy.data.images[layer.name].is_dirty  or (os.path.exists(external_path) and not os.path.exists(image.filepath)):
                        if not os.path.exists(external_path):
                            image.pack(as_png=True)
                        else:
                            save_external(context,external_path,image)
                        
    elif context.scene.render.engine in ["CYCLES"]:
        for mat in bpy.data.materials:
            if len(mat.b_painter.paint_layers) > 0:
                node_tree = mat.node_tree
                if node_tree != None:
                    tex_nodes = get_tex_recursive(node_tree)
                    for tex_node in tex_nodes:
                        image = tex_node.image
                        
                        external_path = bpy.path.abspath(mat.b_painter.external_path)
                        if image != None and image.is_dirty or (os.path.exists(external_path) and not os.path.exists(image.filepath)):
                            if not os.path.exists(external_path):
                                image.pack(as_png=True)
                            else:
                                save_external(context,external_path,image)
                

def clear_brush_textures():
    for brush in bpy.data.brushes:
        if "b_painter" in brush:
            brush.texture = None
            brush.texture = None
            
def setup_brush_tex(img_path,tex_type="BRUSH"):
    if tex_type == "BRUSH":
        if "b_painter_brush_img" not in bpy.data.images:
            brush_img = bpy.data.images.new("b_painter_brush_img",1024,1024)
            if brush_img.packed_file != None:
                brush_img.unpack()
            brush_img.filepath = img_path
            brush_img.source = "FILE"
        else:
            brush_img = bpy.data.images["b_painter_brush_img"]
            if brush_img.packed_file != None:
                brush_img.unpack()
            brush_img.filepath = img_path
            brush_img.source = "FILE"
        
        if "b_painter_brush_tex" not in bpy.data.textures:
            brush_tex = bpy.data.textures.new("b_painter_brush_tex",type="IMAGE")
        else:
            brush_tex = bpy.data.textures["b_painter_brush_tex"]
        brush_tex.b_painter_invert_mask = brush_tex.b_painter_invert_mask
    elif tex_type == "STENCIL":
        if "b_painter_stencil_img" not in bpy.data.images:
            brush_img = bpy.data.images.new("b_painter_stencil_img",1024,1024)
            if brush_img.packed_file != None:
                brush_img.unpack()
            brush_img.filepath = img_path
            brush_img.source = "FILE"
        else:
            brush_img = bpy.data.images["b_painter_stencil_img"]
            if brush_img.packed_file != None:
                brush_img.unpack()
            brush_img.filepath = img_path
            brush_img.source = "FILE"

        if "b_painter_stencil_tex" not in bpy.data.textures:
            brush_tex = bpy.data.textures.new("b_painter_stencil_tex",type="IMAGE")
        else:
            brush_tex = bpy.data.textures["b_painter_stencil_tex"]
        brush_tex.b_painter_invert_mask = brush_tex.b_painter_invert_mask
    
    brush_tex.use_nodes = True
    node_tree = brush_tex.node_tree
    
    if "Image" not in node_tree.nodes:    
        image_node = node_tree.nodes.new('TextureNodeImage')    
    else:
        image_node = node_tree.nodes['Image']
    image_node.location = [0,0]
    image_node.image = brush_img
    
    if "ColorRamp" not in node_tree.nodes:    
        ramp_node = node_tree.nodes.new('TextureNodeValToRGB')
        
    else:
        ramp_node = node_tree.nodes['ColorRamp']
        
    if "invert_color" not in ramp_node:
        ramp_node["invert_color"] = False    
        
    ramp_node.location = [200,0]
    if tex_type == "BRUSH":
        if brush_tex.b_painter_invert_mask:
            ramp_node.color_ramp.elements[0].color = [1,1,1,0]
            ramp_node.color_ramp.elements[1].color = [1,1,1,1]
        else:    
            ramp_node.color_ramp.elements[0].color = [1,1,1,1]
            ramp_node.color_ramp.elements[1].color = [1,1,1,0]
    else:
        if brush_tex.b_painter_invert_stencil_mask:
            ramp_node.color_ramp.elements[0].color = [1,1,1,1]
            ramp_node.color_ramp.elements[1].color = [0,0,0,1]
        else:    
            ramp_node.color_ramp.elements[0].color = [0,0,0,1]
            ramp_node.color_ramp.elements[1].color = [1,1,1,1]
                
    
    if "Output" not in node_tree.nodes:
        output_node = node_tree.nodes.new('TextureNodeOutput')
    else:
        output_node = node_tree.nodes['Output']
    output_node.location = [500,0]
    
    node_tree.links.new(ramp_node.inputs['Fac'],image_node.outputs['Image'])
    node_tree.links.new(output_node.inputs['Color'],ramp_node.outputs['Color'])   
    
    return brush_tex


################################################################################################### Texture Manipulation 
def _invert_ramp(self,context,tex_type="BRUSH"):
    if ("b_painter_brush_tex" in bpy.data.textures and tex_type == "BRUSH") or ("b_painter_stencil_tex" in bpy.data.textures and tex_type == "STENCIL"):
        
        if tex_type == "BRUSH":
            node_tree = bpy.data.textures["b_painter_brush_tex"].node_tree
            tmp_color_01 = Vector((1,1,1,1))
            tmp_color_02 = Vector((1,1,1,0))
        elif tex_type == "STENCIL":
            node_tree = bpy.data.textures["b_painter_stencil_tex"].node_tree
            tmp_color_01 = Vector((1,1,1,1))
            tmp_color_02 = Vector((0,0,0,1))
        
        if node_tree != None:
            ramp_node = node_tree.nodes["ColorRamp"]
            
            if tex_type == "BRUSH":      
                if self.b_painter_invert_mask:
                    ramp_node.color_ramp.elements[0].color = tmp_color_01
                    ramp_node.color_ramp.elements[1].color = tmp_color_02
                else:
                    ramp_node.color_ramp.elements[0].color = tmp_color_02
                    ramp_node.color_ramp.elements[1].color = tmp_color_01    
            elif tex_type == "STENCIL":
                if self.b_painter_invert_stencil_mask:
                    ramp_node.color_ramp.elements[0].color = tmp_color_01
                    ramp_node.color_ramp.elements[1].color = tmp_color_02
                else:
                    ramp_node.color_ramp.elements[0].color = tmp_color_02
                    ramp_node.color_ramp.elements[1].color = tmp_color_01    

        
def _tonemap(self,context,tex_type="BRUSH"):
    
    if (tex_type == "BRUSH" and "b_painter_brush_tex" in bpy.data.textures) or (tex_type == "STENCIL" and "b_painter_stencil_tex" in bpy.data.textures):
        if tex_type == "BRUSH":
            node_tree = bpy.data.textures["b_painter_brush_tex"].node_tree
            if node_tree != None:
                ramp_node = node_tree.nodes["ColorRamp"]
                ramp_node.color_ramp.elements[0].position = context.tool_settings.image_paint.brush.b_painter_ramp_tonemap_l
                ramp_node.color_ramp.elements[1].position = context.tool_settings.image_paint.brush.b_painter_ramp_tonemap_r
        elif tex_type == "STENCIL":
            node_tree = bpy.data.textures["b_painter_stencil_tex"].node_tree
            if node_tree != None:
                ramp_node = node_tree.nodes["ColorRamp"]
                ramp_node.color_ramp.elements[0].position = context.tool_settings.image_paint.brush.b_painter_stencil_ramp_tonemap_l
                ramp_node.color_ramp.elements[1].position = context.tool_settings.image_paint.brush.b_painter_stencil_ramp_tonemap_r

def _mute_ramp(self,context):    
    if "b_painter_brush_tex" in bpy.data.textures: 
        node_tree = bpy.data.textures["b_painter_brush_tex"].node_tree
        ramp_node = node_tree.nodes["ColorRamp"]
        ramp_node.mute = not(self.b_painter_use_mask)
    brush = context.tool_settings.image_paint.brush
    if brush != None:    
        brush.b_painter_brush_texture = brush.b_painter_brush_texture
    