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
from bpy.types import Menu, Panel, UIList
from bpy.props import CollectionProperty, EnumProperty, StringProperty
from . functions import setup_brush_tex, id_from_string, _invert_ramp, get_context_node_tree, get_materials_recursive, check_layer_stack_cycles, check_layer_stack_bi, check_paint_channels_count, get_tex_recursive, get_addon_prefs
from . operators.preset_handling import texture_path, brush_icons_path
import os

class BPainterNodePanel(bpy.types.Panel):
    bl_idname = "bpainter_node_panel"
    bl_label = "BPainter"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls,context):
        if context.scene.render.engine == 'CYCLES':
            return True
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        
        obj = context.active_object
        if obj != None:
            mat = obj.active_material
            if mat != None:
                node_tree = get_context_node_tree(context)
                if node_tree != None:
                    selected_nodes = []
                    for node in node_tree.nodes:
                        if node.select and (node.type == "TEX_IMAGE" or (node.type == "GROUP" and node.label == "BPaintLayer")):
                            selected_nodes.append(node)
                    
                    if len(selected_nodes) > 0:
                        if node_tree.nodes.active != None and ((node.type == "TEX_IMAGE" and node.image != None) or node.type == "GROUP" and node.label == "BPaintLayer"):
                            col.operator("b_painter.set_node_as_paintlayer",text="Paint Node",icon="BRUSH_DATA")
                            
                    
                        col.operator("b_painter.create_stencil_layer",text="Create Stencil Layer",icon="IMAGE_ZDEPTH")    
                        
        
                        
        
class BPAINTER_TextureSlot(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        misc_icons = preview_collections["b_painter_misc_icons"]
        icon_mask_inactive = misc_icons["icon_mask_inactive"].icon_id
        icon_mask_active = misc_icons["icon_mask_active"].icon_id
        icon_alpha_locked = misc_icons["icon_alpha_locked"].icon_id
        prefs = get_addon_prefs(context)
        
        self.use_filter_sort_reverse = context.scene.b_painter_flip_template_list
        ob = context.active_object
        col = layout.column()
        row = col.row(align=True)
        mat = None
        if item.mat_name in bpy.data.materials:
            mat = bpy.data.materials[item.mat_name]
        tex_node_name = item.tex_node_name
        mix_node = None
        tex_node = None
        mask_node = None
        mask_tex_node = None
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
                if item.mask_mix_node_name in node_tree.nodes:
                    mask_node = node_tree.nodes[item.mask_mix_node_name]
                if item.mask_tex_node_name in node_tree.nodes:
                    mask_tex_node = node_tree.nodes[item.mask_tex_node_name]
                  
            tex_slot = mat.texture_slots[item.index] if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME'] else None
            tex = None
            if tex_slot != None:
                tex = tex_slot.texture
        
        if mat != None and context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
            if item.name in bpy.data.images:
                img = bpy.data.images[item.name]
            else:
                img = None    
        
            if mat.use_textures[item.index]:
                vis_icon = "VISIBLE_IPO_ON"
            else:
                vis_icon = "VISIBLE_IPO_OFF" 
            row.prop(mat, "use_textures", text="",icon=vis_icon, index=item.index,emboss=False)
        
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
                if tex_node != None:  
                    img = tex_node.image
                    icon_id = bpy.types.UILayout.icon(img) if img != None else 0
                    
                    if mix_node != None:    
                        vis_icon = "VISIBLE_IPO_OFF" if mix_node.b_painter_layer_hide else "VISIBLE_IPO_ON" 
                        row.prop(mix_node, "b_painter_layer_hide", text="",icon=vis_icon, index=item.index,emboss=False)
                        row.active = True if not mix_node.b_painter_layer_hide else False
                    else:
                        vis_icon = "VISIBLE_IPO_OFF" if tex_node.mute else "VISIBLE_IPO_ON"
                        row.prop(tex_node, "mute", text="",icon=vis_icon, index=item.index,emboss=False)    
                        row.active = True if not tex_node.mute else False
#                    row.separator()
#                    row.separator()
#                    row.separator()
                    
                    row2 = row.row()
                    row2.scale_x = .3
                    row2.alert = True if (item.paint_layer_active and mat.b_painter.paint_layers_index == index and item.mask_tex_node_name != "")else False
                    row2.prop(item, "paint_layer_active", text="",icon="NONE", index=item.index,emboss=False)
                    
                    row2 = row.row()
                    row2.active = True if item.paint_layer_active else False
                    emboss = True if item.paint_layer_active else False
                    row2.prop(item,"paint_layer_active",text="",icon_value=icon_id,emboss=False)
                    row.prop(img, "name", text="", emboss=False)
                    
                    if mask_node != None:
                        mask_img = mask_tex_node.image
                        
                        row2 = row.row()
                        row2.scale_x = .3
                        row2.alert = True if (item.mask_layer_active and mat.b_painter.paint_layers_index == index)else False
                        row2.prop(item, "mask_layer_active", text="",icon="NONE", index=item.index,emboss=False)
                        
                        
                        emboss = True if item.mask_layer_active else False
                        row2 = row.row()
                        row2.active = True if item.mask_layer_active else False
                        op = row2.operator("b_painter.invert_layer_mask",text="",icon_value=bpy.types.UILayout.icon(mask_img),emboss=False)
                        op.mat_name = mat.name
                        op.index = index
                        
                        vis_icon = icon_mask_active if not mask_node.b_painter_layer_hide else icon_mask_inactive
                        row2 = row.row()
                        row2.scale_x = .5
                        row2.prop(mask_node, "b_painter_layer_hide", text="",icon_value=vis_icon, index=item.index,emboss=False)
                    
            elif item.layer_type in ["ADJUSTMENT_LAYER","PROCEDURAL_TEXTURE"]:
                if node_tree != None and item.name in node_tree.nodes:
                    adjustment_node = node_tree.nodes[item.name]
                    proc_tex_node = node_tree.nodes[item.proc_tex_node_name] if item.proc_tex_node_name in  node_tree.nodes else None
                    
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
                        
                    row.prop(adjustment_node, "b_painter_layer_hide", text="",icon=vis_icon, index=item.index,emboss=False)
                    row.separator()
#                    row.separator()
#                    row.separator()
#                    row.separator()
                    
                    if item.layer_type == "ADJUSTMENT_LAYER":
                        op = row.operator("b_painter.configure_adjustment_layer",text="",icon=adj_icon,emboss=False)
                        op.node_tree_name = node_tree.name
                        op.node_name = adjustment_node.name
                        op.index = index
                        op.mat_name = mat.name   
                    elif item.layer_type == "PROCEDURAL_TEXTURE"    :
                        op = row.operator("b_painter.configure_procedural_texture",text="",icon=adj_icon,emboss=False)
                        op.node_tree_name = node_tree.name
                        op.proc_tex_node_name = item.proc_tex_node_name
                        op.proc_ramp_node_name = item.proc_ramp_node_name
                        op.index = index
                        op.mat_name = mat.name
                    if item.layer_type == "ADJUSTMENT_LAYER":       
                        row.prop(adjustment_node, "name", text="", emboss=False)
                    elif item.layer_type == "PROCEDURAL_TEXTURE":
                        row.prop(proc_tex_node, "name", text="", emboss=False)
                    
                    if mask_node != None:
                        mask_img = mask_tex_node.image
                        
                        row2 = row.row()
                        row2.scale_x = .3
                        row2.alert = True if (item.mask_layer_active and mat.b_painter.paint_layers_index == index)else False
                        row2.prop(item, "mask_layer_active", text="",icon="NONE", index=item.index,emboss=False)
                        
                        
                        emboss = True if item.mask_layer_active else False
                        row2 = row.row()
                        row2.active = True if item.mask_layer_active else False
                        op = row2.operator("b_painter.invert_layer_mask",text="",icon_value=bpy.types.UILayout.icon(mask_img),emboss=False)
                        op.mat_name = mat.name
                        op.index = index
                        
                        vis_icon = icon_mask_active if not mask_node.b_painter_layer_hide else icon_mask_inactive
                        row2 = row.row()
                        row2.scale_x = .5
                        row2.prop(mask_node, "b_painter_layer_hide", text="",icon_value=vis_icon, index=item.index,emboss=False)
        
        
        img = None
        if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
            img = bpy.data.images[item.name] if item.name in bpy.data.images else None
        elif context.scene.render.engine in ["CYCLES"]:
            img = bpy.data.images[item.img_name] if item.img_name in bpy.data.images else None
            
        if img != None:
            subrow = row.row()
            if img.b_painter.lock_alpha and prefs.use_layer_alpha_lock:
                subrow.prop(img.b_painter,"lock_alpha",text="",icon_value=icon_alpha_locked,emboss=False)
            else:
                subrow.enabled=False
                subrow.prop(img.b_painter,"lock_alpha",text="",icon="NONE",emboss=False)

def draw_color_panel(self,context,wm,scene,layout,ob,settings,brush,ipaint,pie=False):
    ############################################################################# Color Settings
    col = layout.column()
    if not pie:
        box = layout.box()
        col.separator()
    
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene,"b_painter_show_color_settings",text="Color",icon="COLOR",emboss=False)
        
        if context.scene.b_painter_show_color_settings:
            row.prop(context.scene,"b_painter_show_color_settings",text="",icon="LAYER_ACTIVE",emboss=False)
        else:
            row.prop(context.scene,"b_painter_show_color_settings",text="",icon="LAYER_USED",emboss=False) 
        
        
        row.operator("b_painter.advanced_color_settings",text="",icon="SCRIPTWIN",emboss=False)
    
    if context.scene.b_painter_show_color_settings:
        
        row = col.row(align=True)
        if brush.image_tool == "FILL" and "b_painter" in brush and len(brush.gradient.elements) > 1:
            subcol = row.column()
            subcol.template_color_ramp(brush, "gradient", expand=True)
            subcol.prop(brush,"gradient_fill_mode",text="")
        else:    
            if settings.use_unified_color:
                if bpy.data.scenes[0].b_painter_show_color_wheel:
                    row.template_color_picker(settings, "color", value_slider=True)
                    row = col.row(align=True)
                row.operator("b_painter.set_default_colors",text="",icon="IMAGE_ALPHA")
                if brush.image_tool != "FILL":
                    row.prop(settings,"color",text="")
                    row.prop(settings,"secondary_color",text="")
                else:
                    row.prop(brush.gradient.elements[0],"color",text="")
                    row.operator("b_painter.add_gradient_color_stop",text="",icon="COLOR")
            else:
                if bpy.data.scenes[0].b_painter_show_color_wheel:
                    row.template_color_picker(brush, "color", value_slider=True)
                    row = col.row(align=True)
                row.operator("b_painter.set_default_colors",text="",icon="IMAGE_ALPHA")
                if brush.image_tool != "FILL":
                    row.prop(brush,"color",text="")
                    row.prop(brush,"secondary_color",text="")
                else:
                    row.prop(brush.gradient.elements[0],"color",text="") 
                    row.operator("b_painter.add_gradient_color_stop",text="",icon="COLOR")   
            
            row.operator("paint.brush_colors_flip",text="",icon="ARROW_LEFTRIGHT")
            op = row.operator("b_painter.color_pipette",text="",icon="EYEDROPPER")
            op.pick_mode = "PRESS"
        if bpy.data.scenes[0].b_painter_show_color_palette:    
            draw_color_palette(self,context,col,row)
    col = layout.column()
    
def draw_color_palette(self,context,col,row):
    layout = self.layout
    ob = context.active_object
    settings = context.scene.tool_settings.image_paint
    col.separator()
    col.template_palette(settings,"palette", color=True)

def draw_brush_panel(self,context,wm,scene,layout,ob,settings,brush,ipaint,pie=False):
    ############################################################################# Brush Settings
    col = layout.column()
    if not pie:
        box = layout.box()
        col.separator()
        
        col = layout.column(align=True)
        row = col.row()

        if context.scene.b_painter_brush != "":
            row.prop(context.scene,"b_painter_show_brush",text=context.scene.b_painter_brush,icon="BRUSH_DATA",emboss=False)
        else:
            row.prop(context.scene,"b_painter_show_brush",text="Not Found",icon="BRUSH_DATA",emboss=False)
        
        if context.scene.b_painter_show_brush:
            row.prop(context.scene,"b_painter_show_brush",text="",icon="LAYER_ACTIVE",emboss=False)
        else:
            row.prop(context.scene,"b_painter_show_brush",text="",icon="LAYER_USED",emboss=False) 
        
        row.operator("b_painter.advanced_brush_settings",text="",icon="SCRIPTWIN",emboss=False)
    
    if context.scene.b_painter_show_brush and brush != None:
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(wm,"b_painter_brush_filter",text="",icon="VIEWZOOM",toggle=True)
        row.operator("b_painter.remove_brush_filter",icon="PANEL_CLOSE",text="")
        
        col = layout.column(align=True)
        
        col.template_icon_view(context.scene,"b_painter_brush",show_labels=True,scale=6.0)
        col.scale_y = .7
        col.alignment = "CENTER"
        
        col = layout.column(align=True)
        row = col.row(align=True)
        icon = "UNLOCKED" if not scene.b_painter_use_absolute_size else "LOCKED"
            
        if settings.use_unified_size:
            row.prop(settings,"size",text="Size",slider=True)
        else:    
            row.prop(brush,"size",text="Size",slider=True)
             
        if settings.use_unified_size:    
            row.prop(settings,"use_pressure_size",text="",icon="STYLUS_PRESSURE")
        else:
            row.prop(brush,"use_pressure_size",text="",icon="STYLUS_PRESSURE")
        
        row = col.row(align=True)
        if settings.use_unified_strength:    
            row.prop(settings,"strength",text="Opacity",slider=True)
        else:
            row.prop(brush,"strength",text="Opacity",slider=True) 
        if settings.use_unified_strength:    
            row.prop(settings,"use_pressure_strength",text="",icon="STYLUS_PRESSURE")
        else:
            row.prop(brush,"use_pressure_strength",text="",icon="STYLUS_PRESSURE")
        
        row = col.row(align=True)
        subrow = row.row(align=True)
        if brush.use_smooth_stroke:
            subrow.active = True
        else:
            subrow.active = False       
        subrow.prop(brush,"smooth_stroke_radius",text="Radius",slider=True)
        subrow.prop(brush,"smooth_stroke_factor",text="Factor",slider=True) 
        row.prop(brush, "use_smooth_stroke", text="",icon="MOD_SMOOTH",toggle=True)         
        ###########################################
                    
        row = layout.row(align=True)

        col = row.column(align=True)
        col.label(text="Brush Curve")
        col.operator("b_painter.set_brush_curve",text="",icon="SMOOTHCURVE")
        
        col = row.column(align=True)
        col.label(text="Use Alpha")
        col.prop(brush, "use_alpha", text="",icon="IMAGE_RGB_ALPHA",emboss=True)
        
        col = row.column(align=True)
        col.label(text="Brush Mode")
        col.prop(brush, "blend", text="")
    col = layout.column()
        

def draw_texture_panel(self,context,wm,scene,layout,ob,settings,brush,ipaint,pie=False):
    if brush != None and brush.image_tool == "FILL":
        layout.active = False
    ############################################################################# Brush Texture Settings       
    col = layout.column()
    if not pie:
        box = layout.box()
        col.separator()
        
        col = layout.column(align=True)
        row = col.row()
        
        row.prop(context.scene,"b_painter_show_brush_settings",text="Brush Texture",icon="TPAINT_HLT",emboss=False)
        
        if context.scene.b_painter_show_brush_settings:
            row.prop(context.scene,"b_painter_show_brush_settings",text="",icon="LAYER_ACTIVE",emboss=False)
        else:
            row.prop(context.scene,"b_painter_show_brush_settings",text="",icon="LAYER_USED",emboss=False) 
        
        row.operator("b_painter.advanced_brush_texture_settings",text="",icon="SCRIPTWIN",emboss=False)
    
    if context.scene.b_painter_show_brush_settings and layout.active:
        row = layout.row(align=False)
        col = layout.column(align=False)
        
        subrow = col.row(align=True)
        subrow.prop(brush,"b_painter_tex_brush_categories",text="")
        subrow.operator("b_painter.refresh_previews",text="",icon="FILE_REFRESH")
        subrow.operator("b_painter.open_texture_folder",text="",icon="IMASEL")
        
        col = layout.column(align=False)
        col.scale_y = .7
        col.template_icon_view(brush,"b_painter_brush_texture",show_labels=True)

        tex = None
        if "b_painter_brush_tex" in bpy.data.textures:
            tex = bpy.data.textures["b_painter_brush_tex"]
        
        if brush.b_painter_brush_texture != "None":
            col = layout.column(align=True)
            color_ramp = tex.node_tree.nodes["ColorRamp"]
            
            subrow = col.row()
            subrow.prop(brush,"b_painter_use_mask",text="Use as Mask",toggle=False)
            subrow.prop(brush,"use_primary_overlay",text="Show Texture",toggle=False)
            
            if brush.b_painter_use_mask:
                col.prop(brush,"b_painter_invert_mask",text="Invert Mask",toggle=True,icon="IMAGE_ALPHA")
                col.prop(brush,"b_painter_ramp_tonemap_l",text="Tonemap L",slider=True)
                col.prop(brush,"b_painter_ramp_tonemap_r",text="Tonemap R",slider=True)
    col = layout.column()

def draw_stencil_panel(self,context,wm,scene,layout,ob,settings,brush,ipaint,pie=False):
    if brush != None and brush.image_tool == "FILL":
        layout.active = False
    ############################################################################## Stencil Texture Settings    
    col = layout.column()
    if not pie:
        box = layout.box()
        col.separator()
        
        col = layout.column(align=True)
        row = col.row()

        row.prop(context.scene,"b_painter_show_stencil_settings",text="Stencil Texture",icon="IMAGE_RGB_ALPHA",emboss=False)
        
        if context.scene.b_painter_show_stencil_settings:
            row.prop(context.scene,"b_painter_show_stencil_settings",text="",icon="LAYER_ACTIVE",emboss=False)
        else:
            row.prop(context.scene,"b_painter_show_stencil_settings",text="",icon="LAYER_USED",emboss=False)    
        
        row.operator("b_painter.advanced_stencil_texture_settings",text="",icon="SCRIPTWIN",emboss=False)        
    
    if context.scene.b_painter_show_stencil_settings and layout.active:
        row = layout.row(align=False)
        col = layout.column(align=False)
        
        subrow = col.row(align=True)
        subrow.prop(context.scene,"b_painter_tex_stencil_categories",text="")
        subrow.operator("b_painter.refresh_previews",text="",icon="FILE_REFRESH")
        subrow.operator("b_painter.open_texture_folder",text="",icon="IMASEL")        
            
        col = layout.column(align=False)
        col.scale_y = .7
        col.template_icon_view(brush,"b_painter_stencil_texture",show_labels=True)
        if brush.b_painter_stencil_texture != "None":
            col = layout.column(align=True)
            col.prop(brush,"b_painter_invert_stencil_mask",text="Invert Mask",toggle=True,icon="IMAGE_ALPHA")
            col.prop(brush,"b_painter_stencil_ramp_tonemap_l",text="Tonemap L",slider=True)
            col.prop(brush,"b_painter_stencil_ramp_tonemap_r",text="Tonemap R",slider=True)
            if brush.mask_texture_slot.mask_map_mode == "STENCIL":
                op = col.operator("brush.stencil_reset_transform",text="Reset Stencil Transformation",icon="LOOP_BACK")
                op.mask = True
        
        row = layout.row(align=True)
        row.prop(context.tool_settings.image_paint,"use_cavity",text="Use Cavity Mask",toggle=True)
        row.operator("b_painter.set_cavity_curve",text="",icon="SMOOTHCURVE")   
    col = layout.column()

def draw_layer_panel(self,context,wm,scene,layout,ob,settings,brush,ipaint,pie=False):
    ############################################################################# Layer Settings        
    col = layout.column()
    if not pie:
        box = layout.box()
        col.separator()
        
        col = layout.column(align=True)
        row = col.row()
        row.prop(context.scene,"b_painter_show_layer_settings",text="Paint Layer",icon="RENDERLAYERS",emboss=False)
        
        if context.scene.b_painter_show_layer_settings:
            row.prop(context.scene,"b_painter_show_layer_settings",text="",icon="LAYER_ACTIVE",emboss=False)
        else:
            row.prop(context.scene,"b_painter_show_layer_settings",text="",icon="LAYER_USED",emboss=False) 
        
        row.operator("b_painter.layer_settings",text="",icon="SCRIPTWIN",emboss=False)
    
    ### force update layer stack
    if context.scene.render.engine == "CYCLES":
        obj = context.active_object
        if obj.b_painter_active_material in bpy.data.materials:
            mat = bpy.data.materials[obj.b_painter_active_material]
            stack_length = check_layer_stack_cycles(context,obj,mat)
            paint_channels_length = check_paint_channels_count(context,obj,mat)
            image_textures_length = get_tex_recursive(mat.node_tree,"BPaintLayer")
            if (mat.b_painter.paint_channel_active != "Unordered Images" and stack_length != len(mat.b_painter.paint_layers)) or (mat.b_painter.paint_channel_active == "Unordered Images" and len(mat.b_painter.paint_layers) != len(image_textures_length)) or paint_channels_length != len(mat.b_painter.paint_channel_info):
                row.operator("b_painter.force_layer_update",text="",icon="RECOVER_LAST",emboss=False)
    elif context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
        obj = context.active_object
        if obj.b_painter_active_material in bpy.data.materials:
            mat = bpy.data.materials[obj.b_painter_active_material]
            stack_length = check_layer_stack_bi(context,obj,mat)
            if stack_length == "UPDATE":
                row.operator("b_painter.force_layer_update",text="",icon="RECOVER_LAST",emboss=False)
            
            
    if context.scene.b_painter_show_layer_settings:
        col.separator()
        row = col.row(align=True)
        if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"]:
            if ob.b_painter_shadeless:
                row.prop(ob,"b_painter_shadeless",text="",icon="POTATO",emboss=True)
            else:
                row.prop(ob,"b_painter_shadeless",text="",icon="SMOOTH",emboss=True)
        
        if not scene.b_painter_texture_preview:
            row.operator("b_painter.plane_texture_preview",text="",icon="MESH_CUBE")
        else:
            row.operator("b_painter.plane_texture_preview",text="",icon="MESH_PLANE")
             
        row.prop(context.active_object,"b_painter_active_material",text="")
        col.separator()
    
    if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
        if ob != None:
            if ob.b_painter_active_material in bpy.data.materials:
                mat = bpy.data.materials[ob.b_painter_active_material]
            else:
                mat = None    
            draw_material_layer(self,context,layout,col,row,mat,ob)

            if mat == None:
                row = col.row(align=True)
                row.template_ID(ob, "active_material", new="material.new")
    elif context.scene.render.engine == 'CYCLES':
        if ob != None:
            if ob.active_material != None and ob.active_material.node_tree != None:
                mat = bpy.data.materials[ob.b_painter_active_material]
                draw_material_layer(self,context,layout,col,row,mat,ob)
            if ob.active_material== None:
                row = layout.row()
                row.template_ID(ob, "active_material", new="material.new")
            elif ob.active_material.use_nodes == False:
                row = layout.row()
                row.prop(ob.active_material,"use_nodes",text="Use Nodes",icon="NODETREE")
    col = layout.column()
        
class BPainter(bpy.types.Panel):
    bl_idname = "bpainter"
    bl_label = "BPainter 1.0"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BPainter"
    
    prefs = None
    
    @classmethod
    def poll(cls, context):
        return True
#        if  context.active_object != None and context.active_object.mode == "TEXTURE_PAINT":
#            return True
    
#    def draw_header(self,context):
#        layout = self.layout
#        layout.label(text="",icon="COLOR")

                    
    def draw(self, context):
        self.prefs = get_addon_prefs(context)
        wm = context.window_manager
        scene = context.scene
        layout = self.layout
        ob = context.active_object
        settings = context.scene.tool_settings.unified_paint_settings
        brush = context.scene.tool_settings.image_paint.brush
        ipaint = context.scene.tool_settings.image_paint
        col = None
        
        if context.space_data.viewport_shade in ["SOLID","TEXTURED","WIREFRAME","BOUNDBOX"]:
            layout.label(text="Wrong Shading Mode Set",icon="ERROR")
            layout.column().operator("b_painter.change_material_mode",text="Set Material Mode",icon="MATERIAL")
        if ob != None and ob.mode == "OBJECT":
            layout.column().operator("paint.texture_paint_toggle",text="Start Painting",icon="BRUSH_DATA")
        
        if "b_painter_panels" in scene and ob != None:
            for panel in scene["b_painter_panels"]:
                if panel.upper() == "COLOR" and ob.mode == "TEXTURE_PAINT":
                    #self.draw_color_panel(context,wm,scene,layout.column(),ob,settings,brush,ipaint)
                    draw_color_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint)
                elif panel.upper() == "BRUSH" and ob.mode == "TEXTURE_PAINT":
                    draw_brush_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint)
                elif panel.upper() == "TEXTURE" and ob.mode == "TEXTURE_PAINT":
                    draw_texture_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint)
                elif panel.upper() == "STENCIL" and ob.mode == "TEXTURE_PAINT":    
                    draw_stencil_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint)
                elif panel.upper() == "LAYER":
                    draw_layer_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint)
            

def draw_material_layer(self,context,layout,col,row,mat,ob):
    misc_icons = preview_collections["b_painter_misc_icons"]
    icon_layer_new = misc_icons["icon_layer_new"].icon_id
    icon_mask = misc_icons["icon_mask"].icon_id
    icon_adjustment_layer = misc_icons["icon_adjustment_layer"].icon_id
    icon_proc_tex = misc_icons["icon_proc_tex"].icon_id
    icon_alpha_unlocked = misc_icons["icon_alpha_unlocked"].icon_id
    icon_alpha_locked = misc_icons["icon_alpha_locked"].icon_id
    
    prefs = get_addon_prefs(context)
    
    if context.scene.b_painter_show_layer_settings:
        if mat:
            row2 = col.row()
            row3 = row2.row()
            row3.alignment = "LEFT"

            if mat.b_painter.expanded:
                if (mat.b_painter.paint_channel_active in bpy.data.node_groups or mat.b_painter.paint_channel_active == "Unordered Images") and context.scene.render.engine in ["CYCLES"]:
                    row = col.row(align=True)
                    if mat.node_tree != None and "BPainterPreview" in mat.node_tree.nodes:
                        icon = "POTATO"    
                    else:
                        icon = "SMOOTH"
                    op = row.operator("b_painter.separate_paint_channel",text="",icon=icon)
                    op.mat_name = mat.name
                    row.prop(mat.b_painter,"paint_channel_active",expand=False,text="")
                    op = row.operator("b_painter.create_new_paint_channel",text="",icon="ZOOMIN")
                    op.mat_name = mat.name
                    if mat.b_painter.paint_channel_active in mat.b_painter.paint_channel_info:
                        op = row.operator("b_painter.delete_paint_channel",text="",icon="ZOOMOUT")
                        op.mat_name = mat.name
                        op.group_name = mat.b_painter.paint_channel_info[mat.b_painter.paint_channel_active].group_name
                    
                col.separator()        
                if len(mat.b_painter.paint_layers) > 0:
                    if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
                        paint_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index] if mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1 else None
                        try:
                            tex_slot = mat.texture_slots[mat.b_painter.paint_layers[mat.b_painter.paint_layers_index].index]
                        except:
                            tex_slot = None    
                        row = col.row(align=True)
                        if tex_slot != None:
                            img = bpy.data.images[paint_layer.name] if paint_layer.name in bpy.data.images else None
                            if img != None and not img.b_painter.lock_alpha:
                                row.prop(img.b_painter,"lock_alpha",text="",icon_value=icon_alpha_unlocked)
                            elif img != None and img.b_painter.lock_alpha:
                                row.prop(img.b_painter,"lock_alpha",text="",icon_value=icon_alpha_locked)
                                
                            if tex_slot.use_map_color_diffuse:
                                row.prop(tex_slot,"blend_type",text="")
                            else:
                                row2 = row.row(align=True)
                                row2.prop(tex_slot,"blend_type",text="")
                                row2.enabled = False
                            if tex_slot.use_map_color_diffuse:
                                row.prop(tex_slot,"diffuse_color_factor",text="Opacity",slider=True)
                            elif tex_slot.use_map_normal:
                                row.prop(tex_slot,"normal_factor",text="Strength",slider=True)
                            elif tex_slot.use_map_specular:
                                row.prop(tex_slot,"specular_factor",text="Strength",slider=True)
                            elif tex_slot.use_map_hardness:
                                row.prop(tex_slot,"hardness_factor",text="Strength",slider=True)
                    elif context.scene.render.engine in ['CYCLES'] and mat.node_tree != None:
                        if mat.b_painter.paint_channel_active in bpy.data.node_groups:
                            node_tree = bpy.data.node_groups[mat.b_painter.paint_channel_active]
                            
                            paint_layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index] if mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1 else None
                            
                            row = col.row(align=True)
                            if paint_layer != None and paint_layer.layer_type not in ["ADJUSTMENT_LAYER","PROCEDURAL_LAYER"] and prefs.use_layer_alpha_lock:
                                img = bpy.data.images[paint_layer.img_name] if paint_layer.img_name in bpy.data.images else None
                                if img != None and not img.b_painter.lock_alpha:
                                    row.prop(img.b_painter,"lock_alpha",text="",icon_value=icon_alpha_unlocked)
                                elif img != None and img.b_painter.lock_alpha:
                                    row.prop(img.b_painter,"lock_alpha",text="",icon_value=icon_alpha_locked)
                                    
                            if mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1 and paint_layer != None and paint_layer.layer_type in ["PAINT_LAYER","PROCEDURAL_TEXTURE"]:
                                node_name = paint_layer.mix_node_name 
                                
                                if node_name in node_tree.nodes:
                                    mix_node = node_tree.nodes[node_name]
                                else:
                                    mix_node = None    
                                
                                math_node = None
                                if mix_node != None:
                                    if mix_node.inputs["Fac"].links[0].from_node.type == "MATH":
                                        math_node = mix_node.inputs["Fac"].links[0].from_node
                                    #row = col.row(align=True)  
                                    row.prop(mix_node,"blend_type",text="")
                                    
                                if math_node != None:
                                    row.prop(math_node,"b_painter_opacity",text="Opacity",slider=True)
                            elif mat.b_painter.paint_layers_index <= len(mat.b_painter.paint_layers)-1 and paint_layer.layer_type in ["ADJUSTMENT_LAYER"]:
                                node_name = paint_layer.name
                                if node_name in node_tree.nodes:
                                    adjustment_node = node_tree.nodes[node_name]
                                else:
                                    adjustment_node = None  
                                if adjustment_node != None:
                                    #row = col.row(align=True)
                                    row.prop(adjustment_node,"b_painter_opacity",text="Opacity",slider=True)    
                
                col.template_list("BPAINTER_TextureSlot", "",mat.b_painter, "paint_layers", mat.b_painter, "paint_layers_index", rows=2)
                
                row = col.row(align=True)
                row2 = row.row(align=True)
                row2.alignment = "LEFT"
                row2.scale_x = 1.2
                row2.scale_y = 1.2
                op = row2.operator("b_painter.new_paint_layer",icon_value=icon_layer_new,text="")
                op.layer_type_cycles = "PAINT_LAYER"
                op.mat_name = mat.name
                if context.scene.render.engine == "CYCLES":
                    op = row2.operator("b_painter.new_paint_layer",icon_value=icon_adjustment_layer,text="")
                    op.mat_name = mat.name
                    op.layer_type_cycles = "ADJUSTMENT_LAYER"
                    
                    op = row2.operator("b_painter.new_paint_layer",icon_value=icon_proc_tex,text="")
                    op.mat_name = mat.name
                    op.layer_type_cycles = "PROCEDURAL_LAYER"
                    
                    op = row2.operator("b_painter.create_layer_mask",icon_value=icon_mask,text="")
                    op.mat_name = mat.name
                
                row2 = row.row(align=True)
                row2.alignment = "RIGHT"
                row2.scale_x = 1.2
                row2.scale_y = 1.2
                
                op = row2.operator("b_painter.merge_material_layers",icon="AUTOMERGE_OFF",text="")#Merge Layer
                op.mat_name = mat.name
                
                op = row2.operator("b_painter.move_paint_layer",icon="TRIA_UP",text="")
                op.type = "UP" if not context.scene.b_painter_flip_template_list else "DOWN"
                op.mat_name = mat.name
                
                op = row2.operator("b_painter.move_paint_layer",icon="TRIA_DOWN",text="")
                op.type = "DOWN" if not context.scene.b_painter_flip_template_list else "UP"
                op.mat_name = mat.name
                
                op = row2.operator("b_painter.delete_paint_layer",icon="X",text="")#Delete Layer
                op.mat_name = mat.name
                if context.scene.render.engine in ['BLENDER_RENDER','BLENDER_GAME']:
                    
                    if len(mat.b_painter.paint_layers) > 0:
                        try:
                            layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                        except:
                            layer = None
                                    
                        if layer != None and layer.name in bpy.data.images:
                            img = bpy.data.images[layer.name]
                            if img.b_painter.active:
                                row = layout.row(align=False)
                                layer = mat.b_painter.paint_layers[mat.b_painter.paint_layers_index]
                                row.prop(img.b_painter_channel,"color")
    col.separator()

class ChangePanelOrder(bpy.types.Operator):
    bl_idname = "b_painter.change_panel_order"
    bl_label = "Change Panel Order"
    bl_description = "Change Panel Order"
    bl_options = {"REGISTER"}
    
    panel_name = StringProperty()
    mode = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True

    def get_item(self,name,list):
        for i,item in enumerate(list):
            if item.upper() == name.upper():
                return [item.upper(), i]
            
    def execute(self, context):
        scene = context.scene
        if "b_painter_panels" in scene:
            panels = scene["b_painter_panels"]
            item = self.get_item(self.panel_name,panels)
            
            if self.mode == "UP":
                new_index = max(0,item[1] - 1)
                
            elif self.mode == "DOWN":
                new_index = min(len(panels)-1, item[1] + 1)
            panels.insert(new_index,panels.pop(item[1]))
            
            for i,item in enumerate(panels):
                panels[i] = item.upper()
            scene["b_painter_panels"] = panels
        return {"FINISHED"}
        


preview_collections = {}    
def unregister_previews():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
        
def register_previews():
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    pcoll.load("icon_layer_new", os.path.join(brush_icons_path,"icon_layer_new.png"), 'IMAGE')
    pcoll.load("icon_mask", os.path.join(brush_icons_path,"icon_mask.png"), 'IMAGE')
    pcoll.load("icon_adjustment_layer", os.path.join(brush_icons_path,"icon_adjustment_layer.png"), 'IMAGE')
    pcoll.load("icon_mask_active", os.path.join(brush_icons_path,"icon_mask_active.png"), 'IMAGE')
    pcoll.load("icon_mask_inactive", os.path.join(brush_icons_path,"icon_mask_inactive.png"), 'IMAGE')
    pcoll.load("icon_proc_tex", os.path.join(brush_icons_path,"icon_proc_tex.png"), 'IMAGE')
    pcoll.load("icon_alpha_unlocked", os.path.join(brush_icons_path,"icon_alpha_unlocked.png"), 'IMAGE')
    pcoll.load("icon_alpha_locked", os.path.join(brush_icons_path,"icon_alpha_locked.png"), 'IMAGE')
    
    
    preview_collections["b_painter_misc_icons"] = pcoll   