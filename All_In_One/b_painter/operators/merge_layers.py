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
from mathutils import Vector
from bpy.props import StringProperty, EnumProperty, IntVectorProperty, BoolProperty
from bpy.types import Menu, Panel, UIList
import math
from .. functions import update_paint_layers, update_all_paint_layers, set_active_paint_layer, get_layer_nodes, srgb_to_linear, linear_to_srgb
import os
import time

### this is a hack to fix the cycles bake operator called from script. It may happen, that the operator does not work when it was aborted. rerunning it in invoke mode seems to fix it again.
class MergeFix(bpy.types.Operator):
    bl_idname = "b_painter.merge_fix"
    bl_label = "Merge Fix"
    bl_description = ""
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self,context):
        ### setup bake options
        samples_default = int(context.scene.cycles.samples)
        bake_type_default = str(context.scene.cycles.bake_type)
        use_pass_direct_default = bool(context.scene.render.bake.use_pass_direct)
        use_pass_indirect_default = bool(context.scene.render.bake.use_pass_indirect)
        use_pass_color_default = bool(context.scene.render.bake.use_pass_color)
        
        context.scene.cycles.samples = 1
        context.scene.cycles.bake_type = "DIFFUSE"
        context.scene.render.bake.use_pass_direct = False
        context.scene.render.bake.use_pass_indirect = False
        context.scene.render.bake.use_pass_color = True
        
        obj_init = bpy.data.objects[bpy.context.active_object.name]
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)
        bpy.ops.object.mode_set(mode="OBJECT")
        tmp_mat = bpy.data.materials.new("tmp_mat")
        tmp_mat.use_nodes = True
        node_tree = tmp_mat.node_tree
        obj.active_material = tmp_mat
        
        ### generate Bake Diffuse Texture and select
        tmp_img = bpy.data.images.new("tmp_img",4,4,alpha=True)
        tmp_img.generated_color = [0,0,0,0]
        
        for node in node_tree.nodes:
            node.select = False
        
        bake_node = node_tree.nodes.new("ShaderNodeTexImage")
        bake_node.image = tmp_img
        bake_node.select = True
        node_tree.nodes.active = bake_node
        bpy.ops.object.bake("INVOKE_DEFAULT",type="DIFFUSE")
        time.sleep(1)
        bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.materials.remove(tmp_mat,do_unlink=True)
        bpy.data.images.remove(tmp_img,do_unlink=True)
        bpy.context.scene.objects.active = obj_init
        obj_init.select = True
        
        
        ### restore bake options
        context.scene.cycles.samples = samples_default
        context.scene.cycles.bake_type = bake_type_default
        context.scene.render.bake.use_pass_direct = use_pass_direct_default
        context.scene.render.bake.use_pass_indirect = use_pass_indirect_default
        context.scene.render.bake.use_pass_color = use_pass_color_default
        return {"FINISHED"}
        

class BPAINTER_MERGE_TextureSlot(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        ob = context.active_object
        col = layout.column()
        row = col.row(align=True)
        mat = None
        if item.mat_name in bpy.data.materials:
            mat = bpy.data.materials[item.mat_name]
        tex_node_name = item.tex_node_name
        mix_node = None
        tex_node = None
        node_tree = None
        
        if mat != None:
            if mat.b_painter.paint_channel_active in bpy.data.node_groups and mat.b_painter.paint_channel_active != "Unordered Images":
                node_tree = bpy.data.node_groups[mat.b_painter.paint_channel_active]
            elif mat.b_painter.paint_channel_active == "Unordered Images":
                node_tree = mat.node_tree
                if item.node_tree_name not in ["Shader Nodetree",""]:
                    node_tree = bpy.data.node_groups[item.node_tree_name]
            if node_tree != None:
                if item.tex_node_name in node_tree.nodes:
                    tex_node = node_tree.nodes[item.tex_node_name]
                if item.mix_node_name in node_tree.nodes:
                    mix_node = node_tree.nodes[item.mix_node_name]
            
            tex = None
            if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
                tex_slot = mat.texture_slots[item.index]
                if tex_slot != None:
                    tex = tex_slot.texture
        
        if mat != None and context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
            if mat.use_textures[item.index]:
                row.prop(item,"merge_layer",text="")
            else:
                row.separator()
                row.separator()
                row.separator()
                row.separator()   
            
            if item.name in bpy.data.images:
                img = bpy.data.images[item.name]
            else:
                img = None    
        
            if mat.use_textures[item.index]:
                vis_icon = "VISIBLE_IPO_ON"
            else:
                vis_icon = "VISIBLE_IPO_OFF" 
            row.label(text="",icon=vis_icon)
        
            if tex_slot != None and  tex_slot.use_stencil:
                row.separator()
                row.separator()
                row.separator()
            if img != None and tex != None:
                if tex.image != None:
                    icon_id = bpy.types.UILayout.icon(tex.image)
                else:
                    icon_id = bpy.types.UILayout.icon(tex)
                
                row.prop(item, "name", text="", emboss=False,icon_value=icon_id)
                row = layout.row(align=False)
            
                if tex_slot.use_stencil:
                    row.label(text="",icon="IMAGE_ZDEPTH")

        elif mat != None and context.scene.render.engine == 'CYCLES':
            if item.layer_type == "PAINT_LAYER":
                if mix_node != None and not mix_node.b_painter_layer_hide:
                    row.prop(item,"merge_layer",text="")
                else:
                    row.separator()
                    row.separator()
                    row.separator()
                    row.separator()
                
                if tex_node != None:
                    img = tex_node.image
                    icon_id = bpy.types.UILayout.icon(img)
                    
                    if mix_node != None:    
                        if mix_node.b_painter_layer_hide:
                            vis_icon = "VISIBLE_IPO_OFF"
                        else:
                            vis_icon = "VISIBLE_IPO_ON" 
                        row.label(text="",icon=vis_icon)
                    else:
                        if tex_node.mute:
                            vis_icon = "VISIBLE_IPO_OFF"
                        else:
                            vis_icon = "VISIBLE_IPO_ON" 
                        row.label(text="",icon=vis_icon)
#                    row.separator()
#                    row.separator()
#                    row.separator()
                    row.prop(img, "name", text="", emboss=False,icon_value=icon_id)
            elif item.layer_type in ["ADJUSTMENT_LAYER","PROCEDURAL_TEXTURE"]:
                    
                if item.name in node_tree.nodes:
                    adjustment_node = node_tree.nodes[item.name]
                    proc_tex_node = node_tree.nodes[item.proc_tex_node_name] if item.proc_tex_node_name in  node_tree.nodes else None
                    if not adjustment_node.b_painter_layer_hide:
                        row.prop(item,"merge_layer",text="")
                    else:
                        row.separator()
                        row.separator()
                        row.separator()
                        row.separator()
                   
                    if adjustment_node.b_painter_layer_hide:
                        vis_icon = "VISIBLE_IPO_OFF"
                    else:
                        vis_icon = "VISIBLE_IPO_ON" 
                    
                    adj_icon = "NONE"    
                    if adjustment_node.type == "CURVE_RGB":
                        adj_icon = "IPO_EASE_IN_OUT"
                    elif adjustment_node.type == "HUE_SAT":
                        adj_icon = "SEQ_CHROMA_SCOPE"
                    elif adjustment_node.type == "INVERT":
                        adj_icon = "IMAGE_ALPHA"
                    elif item.layer_type == "PROCEDURAL_TEXTURE" and adjustment_node.type == "MIX_RGB":
                        adj_icon = "TEXTURE"
                    
                        
                    row.label(text="",icon=vis_icon)
#                    row.separator()
#                    row.separator()
#                    row.separator()
                    
                    row.label(text="",icon=adj_icon)
                    if item.layer_type == "ADJUSTMENT_LAYER":
                        row.prop(adjustment_node, "name", text="", emboss=False)
                    elif item.layer_type == "PROCEDURAL_TEXTURE":
                        row.prop(proc_tex_node, "name", text="", emboss=False)
                        
                
        row = layout.row()
        
def transfer_alpha(diffuse_img,alpha_img):
    diffuse_pixels = list(diffuse_img.pixels)
    alpha_pixels = list(alpha_img.pixels)
    
    for i in range(0,len(alpha_pixels),4):
        diffuse_pixels[i+3] = alpha_pixels[i]
    
    diffuse_img.pixels[:] = diffuse_pixels
    diffuse_img.update()
              
def fix_alpha_color(img):
    pixels = list(img.pixels) # create an editable copy (list)

    # Use the tuple object, which is way faster than direct access to Image.pixels
    for i in range(0, len(pixels), 4):
        alpha=pixels[i+3]
        alpha_div = 0.0
        if(alpha>0.0):
            alpha_div = math.sqrt(1.0/alpha)
            
        pixels[i+0] = pixels[i+0]*alpha_div
        pixels[i+1] = pixels[i+1]*alpha_div
        pixels[i+2] = pixels[i+2]*alpha_div

    # Write back to image.
    # Slice notation here means to replace in-place, not sure if it's faster...
    img.pixels[:] = pixels

    # Should probably update image
    img.update()
    

class MergeMaterialLayers(bpy.types.Operator):
    bl_idname = "b_painter.merge_material_layers"
    bl_label = "Merge Material Layers"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    
    def get_merge_layers(self,context):
        update_all_paint_layers(self,context)
        paint_mat = bpy.data.materials[self.mat_name]
        paint_layers = paint_mat.b_painter.paint_layers
        merge_layers = paint_mat.b_painter.merge_layers
        
        size_x = 0
        size_y = 0
        
        for layer in merge_layers:
            merge_layers.remove(0)
            
        if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
            for i,layer in enumerate(paint_layers):
                slot = paint_mat.texture_slots[layer.index]
                layer_item = None
                if paint_mat.use_textures[layer.index]:
                    if self.mode == "Diffuse" and slot.use_map_color_diffuse:
                        layer_item = merge_layers.add()
                    elif self.mode == "Bump" and slot.use_map_normal:
                        layer_item = merge_layers.add()
                    elif self.mode == "Specular" and slot.use_map_specular:
                        layer_item = merge_layers.add()
                    elif self.mode == "Glossy" and slot.use_map_hardness:
                        layer_item = merge_layers.add()
                    elif self.mode == "Alpha" and slot.use_map_alpha:
                        layer_item = merge_layers.add()
                if layer_item != None:    
                    layer_item.name = layer.name
                    layer_item.index = layer.index
                    layer_item.mat_name = layer.mat_name
                    layer_item.tex_node_name = layer.tex_node_name
                    layer_item.paint_layer_index = i
                    layer_item.layer_type = "PAINT_LAYER"
                                
        elif context.scene.render.engine in ["CYCLES"]:
            obj = context.active_object
            mat = bpy.data.materials[obj.b_painter_active_material]
            node_tree = bpy.data.node_groups[mat.b_painter.paint_channel_info[mat.b_painter.paint_channel_active].name]
            layer_nodes = get_layer_nodes(node_tree)
            for layer in mat.b_painter.paint_layers:
                layer_item = merge_layers.add()
                layer_item.name = layer.name
                layer_item.index = layer.index
                layer_item.mat_name = layer.mat_name
                layer_item.tex_node_name = layer.tex_node_name
                layer_item.mix_node_name = layer.mix_node_name
                layer_item.layer_type = layer.layer_type
                layer_item.proc_tex_node_name = layer.proc_tex_node_name
    
    images = []
    merge_layers = []
    mat_name = StringProperty()
    merge_size = IntVectorProperty(default=[1024,1024],size=2,subtype="XYZ")
    mode = EnumProperty(items=(("Diffuse","Diffuse","Diffuse"),("Bump","Bump","Bump"),("Specular","Specular","Specular"),("Glossy","Glossy","Glossy"),("Alpha","Alpha","Alpha")),update=get_merge_layers)
    replace_layer = BoolProperty(default=True)
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True
    
    def draw(self,context):
        settings = context.tool_settings.image_paint

        layout = self.layout
        row = layout.row()
        row.label(text="Be aware, this Operator may take awhile based on the layer size.",icon="ERROR")
        if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
            row = layout.row()
            row.prop(self,"mode",expand=True)
        
        col = layout.column()
        col.prop(self,"merge_size",text="New Layer Size")
        mat = bpy.data.materials[self.mat_name]
        col.template_list("BPAINTER_MERGE_TextureSlot", "",mat.b_painter, "merge_layers", mat.b_painter, "merge_layers_index", rows=15)
    
    def invoke(self,context,event):
        self.merge_layers = []
        self.get_merge_layers(context)
        
        paint_mat = bpy.data.materials[self.mat_name]
        paint_layers = paint_mat.b_painter.paint_layers
        merge_layers = paint_mat.b_painter.merge_layers
        paint_mat.b_painter.merge_layers_index = -1
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def bi_bake(self,context):
        paint_obj = context.active_object
        paint_mat = bpy.data.materials[self.mat_name]
        
        merge_layer_available = 0
        for layer in paint_mat.b_painter.merge_layers:
            if layer.merge_layer:
                merge_layer_available += 1
        
        if merge_layer_available < 2:
            self.report({'INFO'}, "Select at least 2 layers you would like to merge!")
            return{'FINISHED'}
        
        obj = None
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=True)
        bpy.ops.uv.unwrap(method='ANGLE_BASED',margin=0.0)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj = context.active_object
        obj.name = "merge_layers_tmp_obj"
        mat = bpy.data.materials.new("merge_layers_tmp_mat")
        mat.diffuse_color = [0,0,0]#paint_mat.diffuse_color
        mat.use_shadeless = True
        obj.active_material = mat
        
        
        for layer in paint_mat.b_painter.merge_layers:
            if layer.merge_layer:
                tex_slot1 = paint_mat.texture_slots[layer.index]
                tex_slot2 = mat.texture_slots.add()
                
                
                for prop in dir(tex_slot1):
                    try:
                        setattr(tex_slot2,prop,getattr(tex_slot1,prop))
                    except:
                        pass
                tex_slot2.texture.filter_type = "BOX"  
                tex_slot2.texture.use_filter_size_min = True
                if tex_slot2.blend_type == "MIX":
                    tex_slot_alpha = mat.texture_slots.add()
                    tex_slot_alpha.texture = tex_slot1.texture
                    tex_slot_alpha.use_map_alpha = True
                    tex_slot_alpha.use_map_color_diffuse = False
                mat.use_transparency = True
                mat.alpha = 0
                #mat.use_textures[layer.index] = paint_mat.use_textures[layer.index]
        new_image = bpy.data.images.new("merged_layers",self.merge_size[0],self.merge_size[1],alpha=True)  
        new_image.pack(as_png=True)
        
        new_tex = bpy.data.textures.new("merged_layers","IMAGE")
        new_tex.image = new_image
        for uv in obj.data.uv_textures.active.data:
            uv.image = new_image
            
        ### setup bake
        if self.mode == "Diffuse":
            context.scene.render.bake_type = "TEXTURE"
        elif self.mode == "Bump":
            new_tex.use_normal_map = True
            context.scene.render.bake_type = "NORMALS"
        elif self.mode == "Specular":
            context.scene.render.bake_type = "SPEC_INTENSITY"
        context.scene.render.use_bake_selected_to_active = False
        context.scene.render.use_bake_clear = True

        bpy.ops.object.bake_image()
        
        bpy.data.objects.remove(obj,do_unlink=True)
        context.scene.objects.active = paint_obj
        
        if self.replace_layer:
            first_merge_layer_found = False
            for i,layer in enumerate(paint_mat.b_painter.merge_layers):
                tex = paint_mat.texture_slots[layer.index].texture
                if layer.merge_layer and not first_merge_layer_found:
                    paint_mat.texture_slots[layer.index].texture = new_tex
                    first_merge_layer_found = True
                elif layer.merge_layer:    
                    paint_mat.texture_slots.clear(layer.index)
        else:
            tex_slot = paint_mat.texture_slots.add()
            tex_slot.texture = new_tex
                
        fix_alpha_color(new_image)
        
        update_all_paint_layers(self,context)
        mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index

    def generate_math_node(self,default_value1 , default_value2 , node_tree , use_clamp = True, hide = True , operation = "ADD" , label = "", location=Vector((0,0))):
        math_node = node_tree.nodes.new("ShaderNodeMath")
        math_node.hide = hide
        math_node.use_clamp = use_clamp
        math_node.inputs[0].default_value = default_value1
        math_node.inputs[1].default_value = default_value2
        math_node.operation = operation
        math_node.location = location
        math_node.label = label
        return math_node

    def create_paint_channel_alpha_output(self,node_tree):
        alpha_nodes = []
        for node in node_tree.nodes:
            if node.type == "MATH":
                if len(node.inputs[0].links) > 0 and not node.inputs[0].links[0].from_node.mute:
                    if len(node.outputs[0].links) > 0 and node.outputs[0].links[0].to_node.blend_type == "MIX":
                        alpha_nodes.append(node)
              
        alpha_nodes.sort(key= lambda x: x.location[0]) 
        input1 = None
        math_prev = None
        group_output = [node for node in node_tree.nodes if node.type == "GROUP_OUTPUT"][0]
        alpha_prev = None
        for i,alpha_node in enumerate(alpha_nodes):
            node1 = alpha_node
            node2 = alpha_nodes[i+1] if i < len(alpha_nodes)-1 else None
            input1 = node1 if input1 == None else input1

            alpha = self.generate_math_node(0,2,node_tree,operation="POWER",label=("Alpha"+str(i)),location=node1.location + Vector((0,-40)))
            node_tree.links.new(node1.outputs[0],alpha.inputs[0])
            
            if alpha_prev != None:
                math_sub = self.generate_math_node(1,1,node_tree,operation="SUBTRACT",location=alpha.location + Vector((0,-40)))
                math_mult = self.generate_math_node(1,1,node_tree,operation="MULTIPLY",location=math_sub.location + Vector((0,-40)))
                math_add = self.generate_math_node(1,1,node_tree,operation="ADD",location=math_mult.location + Vector((0,-40)))
            
            if i > 0:
                ### Alpha Node
                node_tree.links.new(alpha.outputs[0],math_mult.inputs[1])
                
                ### Subtract Node
                node_tree.links.new(math_sub.inputs[1],alpha_prev.outputs[0])
                node_tree.links.new(math_sub.outputs[0],math_mult.inputs[0])
                
                ### Multiply Node
                node_tree.links.new(math_mult.outputs[0],alpha_prev.outputs[0])
                
                ### Add Node
                node_tree.links.new(math_add.inputs[0],math_mult.outputs[0])
                node_tree.links.new(math_add.inputs[1],alpha_prev.outputs[0])
                
                        
            if i == 0:
                alpha_prev = alpha
            else:
                alpha_prev = math_add  
                             
            if i == len(alpha_nodes)-1:
                node_tree.links.new(alpha_prev.outputs[0],group_output.inputs["Alpha"])
   
    def cycles_bake(self,context):
        obj_init = context.active_object
        #obj.select = True
        
        mat = bpy.data.materials[obj_init.b_painter_active_material]
        
        obj = None
        #bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=True)
        obj_data = obj_init.data.copy()
        obj = bpy.data.objects.new("merge_layers_tmp_obj",obj_data)
        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.select = True
        
        node_tree = mat.node_tree
        group_tree = bpy.data.node_groups[mat.b_painter.paint_channel_info[mat.b_painter.paint_channel_active].name]
        node_group = mat.node_tree.nodes[mat.b_painter.paint_channel_info[mat.b_painter.paint_channel_active].group_name]
        
        output_node = [node for node in node_tree.nodes if node.type == "OUTPUT_MATERIAL"][0]
        
        if len(output_node.inputs["Surface"].links) > 0 and output_node.inputs["Surface"].links[0].from_node != None:
            output_node["original_shader"] = output_node.inputs["Surface"].links[0].from_node.name
        
        if len(node_group.outputs["Color"].links) > 0:
            node_group["to_node"] = node_group.outputs["Color"].links[0].to_node.name
        

        if len(output_node.inputs["Surface"].links) > 0:
            output_node["from_node"] = output_node.inputs["Surface"].links[0].from_node.name
        
        ### create temporary diffuse shader 
        tmp_diffuse_shader = node_tree.nodes.new("ShaderNodeBsdfDiffuse")
        tmp_diffuse_shader.location = output_node.location - Vector((0,-160))
        
        
        ### create temporary paint group with layers shown that are going to be baked/merged
        tmp_group = node_tree.nodes.new("ShaderNodeGroup")
        tmp_group.node_tree = group_tree.copy()
        tmp_group.inputs["Background Color"].default_value = [0,0,0,1]
        tmp_group.location = tmp_diffuse_shader.location - Vector((160,0))

        for layer in mat.b_painter.merge_layers:
            if layer.layer_type == "PAINT_LAYER":
                mix_node = tmp_group.node_tree.nodes[layer.mix_node_name]
                mix_node.b_painter_layer_hide = not(layer.merge_layer)
            elif layer.layer_type == "ADJUSTMENT_LAYER":
                adj_layer = tmp_group.node_tree.nodes[layer.name]
                adj_layer.b_painter_layer_hide = not(layer.merge_layer)
                
        self.create_paint_channel_alpha_output(tmp_group.node_tree)
        
        ### wire up emmision shader with paint group and Material Output
        node_tree.links.new(tmp_diffuse_shader.inputs["Color"],tmp_group.outputs["Color"])
        node_tree.links.new(tmp_diffuse_shader.outputs["BSDF"],output_node.inputs["Surface"])
        
        ### generate Bake Diffuse Texture and select
        bake_image_diffuse = bpy.data.images.new("bake_image_diffuse",self.merge_size[0],self.merge_size[1],alpha=True)
        bake_image_diffuse.generated_color = [0,0,0,0]
        bake_image_diffuse.pack(as_png=True)
        
        bake_image_alpha = bpy.data.images.new("bake_image_alpha",self.merge_size[0],self.merge_size[1],alpha=True)
        bake_image_alpha.generated_color = [0,0,0,0]
        bake_image_alpha.pack(as_png=True)
        for node in node_tree.nodes:
            node.select = False
        
        bake_node = node_tree.nodes.new("ShaderNodeTexImage")
        bake_node.image = bake_image_diffuse
        bake_node.location = output_node.location + Vector((200,0))
        bake_node.select = True
        node_tree.nodes.active = bake_node
        
        
        ### setup bake options
        samples_default = int(context.scene.cycles.samples)
        bake_type_default = str(context.scene.cycles.bake_type)
        use_pass_direct_default = bool(context.scene.render.bake.use_pass_direct)
        use_pass_indirect_default = bool(context.scene.render.bake.use_pass_indirect)
        use_pass_color_default = bool(context.scene.render.bake.use_pass_color)
        
        context.scene.cycles.samples = 1
        context.scene.cycles.bake_type = "DIFFUSE"
        context.scene.render.bake.use_pass_direct = False
        context.scene.render.bake.use_pass_indirect = False
        context.scene.render.bake.use_pass_color = True
        ### bake Diffuse Texture
    
        bpy.ops.object.bake('EXEC_DEFAULT',type="DIFFUSE")
        bake_image_diffuse.pack(as_png=True)
        
        ### setup and bake Alpha Textrue
        bake_node.select = True
        node_tree.nodes.active = bake_node
        bake_node.image = bake_image_alpha
        node_tree.links.new(tmp_group.outputs["Alpha"],tmp_diffuse_shader.inputs["Color"])
        
        bpy.ops.object.bake('EXEC_DEFAULT',type="DIFFUSE")
        bake_image_alpha.pack(as_png=True)

        ### transfer alpha from alpha bake to diffuse bake
        transfer_alpha(bake_image_diffuse,bake_image_alpha)
        
        fix_alpha_color(bake_image_diffuse)
        
        bake_image_diffuse.name = "Merged Layer"
        bpy.data.images.remove(bake_image_alpha, do_unlink=True)
        
        ### delete tmp_group and tmp_diffuse_shader
        node_tree.nodes.remove(tmp_group)
        node_tree.nodes.remove(tmp_diffuse_shader)
        node_tree.nodes.remove(bake_node)
        
        ### reconnect original node_group to shader
        if output_node["original_shader"] != None:
            node_tree.links.new(node_tree.nodes[output_node["original_shader"]].outputs[0],output_node.inputs["Surface"])
            
        ### remove layers and insert new baked/merged layer
        remove_layers = []
        replace_layer_name = None
        for i,layer in enumerate(mat.b_painter.merge_layers):
            if layer.merge_layer:
                if replace_layer_name == None and layer.layer_type == "PAINT_LAYER":
                    replace_layer_name = layer.name
                else:    
                    remove_layers.append(mat.b_painter.paint_layers[i].name)
        for name in remove_layers:
            if name in mat.b_painter.paint_layers:
                index = get_layer_index(mat,name)
                if mat.b_painter.paint_layers[index].mask_mix_node_name != "":
                    bpy.ops.b_painter.delete_paint_layer(mat_name=mat.name,index=index)
                bpy.ops.b_painter.delete_paint_layer(mat_name=mat.name,index=index)
                
                update_all_paint_layers(self,context)
            
        replace_layer =  mat.b_painter.merge_layers[replace_layer_name]
        
        final_layer = mat.b_painter.paint_layers[replace_layer.name]
        if final_layer.mask_mix_node_name != "":
            final_layer.mask_layer_active = True
            index = get_layer_index(mat,final_layer.name)
            bpy.ops.b_painter.delete_paint_layer(mat_name=mat.name,index=index)
            
        node_group.node_tree.nodes[replace_layer.tex_node_name].image = bake_image_diffuse
        
        update_all_paint_layers(self,context)
        mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index
        
        
        ### restore bake options
        context.scene.cycles.samples = samples_default
        context.scene.cycles.bake_type = bake_type_default
        context.scene.render.bake.use_pass_direct = use_pass_direct_default
        context.scene.render.bake.use_pass_indirect = use_pass_indirect_default
        context.scene.render.bake.use_pass_color = use_pass_color_default
    
        bpy.data.objects.remove(obj,do_unlink=True)
        context.scene.objects.active = obj_init
        obj_init.select = True
    
    def execute(self, context):
        mat = bpy.data.materials[self.mat_name]
        i = 0
        for layer in mat.b_painter.merge_layers:
            if layer.merge_layer and layer.layer_type == "PAINT_LAYER":
                i += 1
        if i == 0:
            self.report({'INFO'}, "Select at least one Paint Layer")
            return{'FINISHED'}        
            
        if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
            self.bi_bake(context)
            self.get_merge_layers(context)
        elif context.scene.render.engine in ["CYCLES"]:
            bpy.ops.b_painter.merge_fix()
            self.cycles_bake(context)
            self.get_merge_layers(context)
        
        self.report({'INFO'}, "Layer Merged.")
        
        return {"FINISHED"}
        
def get_layer_index(mat,layer_name):
    for i,l in enumerate(mat.b_painter.paint_layers):
        if l.name == layer_name:
            return i
        