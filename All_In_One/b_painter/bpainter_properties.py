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
    
import os
import bpy
from bpy.props import CollectionProperty, StringProperty, PointerProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, FloatVectorProperty, IntVectorProperty
from mathutils import Vector
import math
from . functions import _tonemap, _invert_ramp, _mute_ramp, setup_brush_tex, id_from_string, set_active_paint_layer, update_all_paint_layers, get_materials_recursive, set_material_shading, set_brush_alpha_lock
from . operators.preset_handling import texture_path, get_tex_previews, get_brush_tex_previews, get_stencil_tex_previews

def set_paint_layer(self,context):
    update_all_paint_layers(self,context)
    if len(self.paint_layers) > 0:
        self["paint_layers_index"] = min(self.paint_layers_index,len(self.paint_layers)-1)
        active_layer = self.paint_layers[self.paint_layers_index]
        
        if active_layer.layer_type == "PAINT_LAYER":
            
            
            if self.paint_layers_index < len(self.paint_layers) and len(self.paint_layers) > 0:
                if context.scene.render.engine in ["BLENDER_RENDER","BLENDER_GAME"] and len(self.paint_layers) > 0: 
                    paint_layer = self.paint_layers[self.paint_layers_index]
                    if paint_layer.layer_type == "PAINT_LAYER":
                        context.tool_settings.image_paint.canvas = bpy.data.images[paint_layer.name]
                        context.tool_settings.image_paint.mode = "IMAGE"
                    
                elif context.scene.render.engine in ['CYCLES']:
                    paint_layer = self.paint_layers[self.paint_layers_index]
                    if paint_layer.layer_type == "PAINT_LAYER":
                        if paint_layer.paint_layer_active:
                            context.tool_settings.image_paint.canvas = bpy.data.images[paint_layer.img_name]
                        elif paint_layer.mask_layer_active:
                            context.tool_settings.image_paint.canvas = bpy.data.images[paint_layer.mask_img_name]
                        context.tool_settings.image_paint.mode = "IMAGE"
                    
                    update_all_paint_layers(self,context)
#                    if self.paint_layers_index <= len(self.paint_layers)-1:
#                        layer = self.paint_layers[self.paint_layers_index]
#                        if self.paint_channel_active == "Unordered Images":
#                            if layer.node_tree_name in bpy.data.node_groups:
#                                node_tree = bpy.data.node_groups[layer.node_tree_name]
#                            else:
#                                node_tree = self.id_data.node_tree
#                            if node_tree != None:      
#                                node = node_tree.nodes[layer.tex_node_name]
#                        else:
#                            print(self.id_data,"------------>")
#                            node_tree = self.id_data.node_tree
#                            if node_tree != None:
#                                node = node_tree.nodes[self.paint_channel_info[0].group_name]
                                
        elif active_layer.layer_type in ["ADJUSTMENT_LAYER","PROCEDURAL_TEXTURE"]:
            paint_layer = self.paint_layers[self.paint_layers_index]
            if active_layer.mask_tex_node_name == "":
                context.tool_settings.image_paint.canvas = None
                context.tool_settings.image_paint.mode = "IMAGE"
            else:
                context.tool_settings.image_paint.canvas = bpy.data.images[paint_layer.mask_img_name]
                context.tool_settings.image_paint.mode = "IMAGE"
                                
        
def invert_ramp(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    _invert_ramp(self,context,tex_type="BRUSH")
    
def invert_stencil_ramp(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    _invert_ramp(self,context,tex_type="STENCIL")
        
def tonemap(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    _tonemap(self,context)

def tonemap_stencil(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    _tonemap(self,context,tex_type="STENCIL")

def mute_ramp(self,context): 
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    _mute_ramp(self,context)   

BRUSHES = []
def get_brushes(self,context):
    wm = context.window_manager
    global BRUSHES
    if wm.b_painter_update_brushes:
        BRUSHES = []
        for i,brush in enumerate(bpy.data.brushes):
            if brush.use_paint_image and "b_painter" in brush:
                if wm.b_painter_brush_filter == "" or wm.b_painter_brush_filter.lower() in brush.name.lower():
                    icon_id = bpy.types.UILayout.icon(brush)
                    BRUSHES.append((str(brush.name),str(brush.name),str(brush.name),icon_id,i))
        BRUSHES.sort(key= lambda x: bpy.data.brushes[x[0]].b_painter_brush_order)
        wm.b_painter_update_brushes = False
    if len(BRUSHES) == 0:
        BRUSHES.append(("","",""))
    return BRUSHES
    
IMAGES = []
def get_brush_textures(self,context):
    global IMAGES
    IMAGES = []
    IMAGES.append(("None","None","None","NONE",0))
    for i,image in enumerate(bpy.data.images):
        if "b_painter" in image:
            icon_id = bpy.types.UILayout.icon(image)    
            IMAGES.append((image.name,image.name,image.name,icon_id,i+1))
    return IMAGES


CATEGORIES = []
def get_category_dirs(self,context):
    global CATEGORIES
    CATEGORIES = [] 
    i = 0 
    for name in os.listdir(texture_path):
        if os.path.isdir(os.path.join(texture_path,name)):
            i += 1
            CATEGORIES.append((name,name,name,"None",id_from_string(name)))
    if i == 0:
        CATEGORIES.append(("Default Category","Default Category","Default Category"))        
    return CATEGORIES

def set_brush(self,context):
    wm = context.window_manager
    wm.b_painter_update_brushes = True
    
    brush = context.tool_settings.image_paint.brush
    if brush != None and self.b_painter_brush in bpy.data.brushes:
        if brush.mask_texture != None:
            tex = bpy.data.textures[brush.mask_texture.name]
        else:
            tex = None    
          
        stencil_trans = {}
        stencil_trans["dimension"] = brush.mask_stencil_dimension
        stencil_trans["pos"] = brush.mask_stencil_pos
        stencil_trans["offset"] = brush.mask_texture_slot.offset
        stencil_trans["scale"] = brush.mask_texture_slot.scale
        stencil_trans["angle"] = brush.mask_texture_slot.angle
        #stencil_trans["category"] = context.scene.b_painter_tex_stencil_categories
        stencil_trans["stenci_texture"] = brush.b_painter_stencil_texture
        stencil_trans["invert_mask"] = brush.b_painter_invert_stencil_mask
        stencil_trans["stencil_ramp_r"] = brush.b_painter_stencil_ramp_tonemap_r
        stencil_trans["stencil_ramp_l"] = brush.b_painter_stencil_ramp_tonemap_l
        stencil_trans["mask_map_mode"] = brush.mask_texture_slot.mask_map_mode
        stencil_trans["use_secondary_overlay"] = brush.use_secondary_overlay
        stencil_trans["mask_overlay_alpha"] = brush.mask_overlay_alpha
        stencil_trans["use_secondary_overlay_override"] = brush.use_secondary_overlay_override
          
        context.tool_settings.image_paint.brush = bpy.data.brushes[self.b_painter_brush]
    
        ### set stencil texture
        brush = context.tool_settings.image_paint.brush
        brush.mask_texture = tex
        brush.mask_stencil_dimension = stencil_trans["dimension"]
        brush.mask_stencil_pos = stencil_trans["pos"]
        brush.mask_texture_slot.offset = stencil_trans["offset"]
        brush.mask_texture_slot.scale = stencil_trans["scale"]
        brush.mask_texture_slot.angle = stencil_trans["angle"]
        brush.b_painter_stencil_texture = stencil_trans["stenci_texture"]
        brush.b_painter_invert_stencil_mask = stencil_trans["invert_mask"]
        brush.b_painter_stencil_ramp_tonemap_r = stencil_trans["stencil_ramp_r"]
        brush.b_painter_stencil_ramp_tonemap_l =  stencil_trans["stencil_ramp_l"]
        brush.mask_texture_slot.mask_map_mode = stencil_trans["mask_map_mode"]
        brush.use_secondary_overlay = stencil_trans["use_secondary_overlay"]
        brush.mask_overlay_alpha = stencil_trans["mask_overlay_alpha"]
        brush.use_secondary_overlay_override = stencil_trans["use_secondary_overlay_override"]
        
        context.tool_settings.image_paint.brush.b_painter_use_mask = context.tool_settings.image_paint.brush.b_painter_use_mask
        context.tool_settings.image_paint.brush.b_painter_invert_mask = context.tool_settings.image_paint.brush.b_painter_invert_mask
        context.tool_settings.image_paint.brush.b_painter_ramp_tonemap_l = context.tool_settings.image_paint.brush.b_painter_ramp_tonemap_l
        context.tool_settings.image_paint.brush.b_painter_ramp_tonemap_r = context.tool_settings.image_paint.brush.b_painter_ramp_tonemap_r
    #### set brush alpha settings
    mat = context.active_object.active_material if context.active_object != None else None
    set_brush_alpha_lock(context,mat)     

def set_texture(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    brush = context.tool_settings.image_paint.brush
    
    if brush != None:  
        context.scene.b_painter_active_tex_brush = str(self.b_painter_brush_texture)
        category = brush.b_painter_tex_brush_categories
        if self.b_painter_brush_texture != "None":
            img_path = os.path.join(texture_path,category,self.b_painter_brush_texture)
            brush_tex = setup_brush_tex(img_path)
            context.tool_settings.image_paint.brush.texture = brush_tex  
        else:
            context.tool_settings.image_paint.brush.texture = None
        
    _invert_ramp(context.tool_settings.image_paint.brush,context) 
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False

def set_stencil_texture(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    
    brush = context.tool_settings.image_paint.brush
    if brush != None:

        category = context.scene.b_painter_tex_stencil_categories
        if self.b_painter_stencil_texture != "None":
            img_path = os.path.join(texture_path,category,self.b_painter_stencil_texture)
            brush_tex = setup_brush_tex(img_path,tex_type="STENCIL")
            context.tool_settings.image_paint.brush.mask_texture = brush_tex  
        else:
            context.tool_settings.image_paint.brush.mask_texture = None
    
    if brush.mask_texture != None:
        img = brush.mask_texture.node_tree.nodes["Image"].image
        ratio = img.size[1]/img.size[0]
        brush.mask_stencil_dimension = [256,256*ratio]
        
    _invert_ramp(context.tool_settings.image_paint.brush,context,tex_type="STENCIL")        
                  


def refresh_brush_category(self,context):
    context.window_manager.b_painter_brush_textures_loaded = False
    context.window_manager.b_painter_stencil_textures_loaded = False
    
    
    brush = context.tool_settings.image_paint.brush
    
    if brush != None:
        context.scene.b_painter_active_tex_brush_category = brush.b_painter_tex_brush_categories
        category = brush.b_painter_tex_brush_categories
        if self.b_painter_brush_texture != "None":
            img_path = os.path.join(texture_path,category,self.b_painter_brush_texture)
            brush_tex = setup_brush_tex(img_path)
            context.tool_settings.image_paint.brush.texture = brush_tex  
        else:
            context.tool_settings.image_paint.brush.texture = None  
    bpy.ops.b_painter.refresh_previews()
        
def refresh_stencil_category(self,context):
    context.window_manager.b_painter_stencil_textures_loaded = False
    context.window_manager.b_painter_brush_textures_loaded = False
    
    context.scene.b_painter_active_stencil_category = context.scene.b_painter_tex_stencil_categories
    
    brush = context.tool_settings.image_paint.brush
    
    if brush != None:
        category = context.scene.b_painter_tex_stencil_categories
        if brush.b_painter_stencil_texture != "None":
            img_path = os.path.join(texture_path,category,brush.b_painter_stencil_texture)
            brush_tex = setup_brush_tex(img_path,tex_type="STENCIL")
            context.tool_settings.image_paint.brush.mask_texture = brush_tex  
        else:
            context.tool_settings.image_paint.brush.mask_texture = None
            
    bpy.ops.b_painter.refresh_previews()
            

PAINT_CHANNELS = []
def get_paint_channel(self,context):
    global PAINT_CHANNELS
    PAINT_CHANNELS = []
    mat = self.id_data

    PAINT_CHANNELS.append(("Unordered Images","Unordered Images","Unordered Images","None",0))
    for i,item in enumerate(mat.b_painter.paint_channel_info):
        PAINT_CHANNELS.append((item.name,item.group_name,item.group_name,"",i+1))

    PAINT_CHANNELS.sort(key= lambda x: x[0])
    return PAINT_CHANNELS
        
def update_paint_channel(self,context):
    update_all_paint_layers(self,context)
    self.paint_layers_index = self.paint_layers_index
    
###
def set_show_hide(self,context):
    self.mute = self.b_painter_layer_hide
    if self.type == "MIX_RGB":
        if len(self.inputs["Color2"].links) > 0:
            from_node = self.inputs["Color2"].links[0].from_node
            math_node = self.inputs["Fac"].links[0].from_node
            if from_node.type == "TEX_IMAGE":
                from_node.mute = self.b_painter_layer_hide
            if math_node.type == "MATH":
                math_node.mute = self.b_painter_layer_hide

def set_b_painter_opacity(self,context):
    if self.type == "MATH":
        self.inputs[1].default_value = self.b_painter_opacity
    else:
        self.inputs["Fac"].default_value = self.b_painter_opacity
    
def update_brush_filter(self,context):
    wm = context.window_manager
    wm.b_painter_update_brushes = True
    try:
        context.scene.b_painter_brush = context.scene.b_painter_brush
    except:
        pass    
 
def set_brush_hardness(self,context):
    brush = self
    points_len = len(brush.curve.curves[0].points)
    for i in range(points_len):
        if len(brush.curve.curves[0].points) > 3:
            point = brush.curve.curves[0].points[0]
            brush.curve.curves[0].points.remove(point)
            brush.curve.curves[0].points.update()
            brush.curve.update()       
    while len(brush.curve.curves[0].points) <= 2:
        brush.curve.curves[0].points.new(.5,.5)
        brush.curve.curves[0].points.update()
        brush.curve.update()
        
    brush.curve.curves[0].points[0].location = [0,1]
    brush.curve.curves[0].points[2].location = [1,0]
    hardness = min(0.99,(self.b_painter_hardness*.8)+.2)
    hardness = max(0.2,hardness)
    x = (self.b_painter_hardness * .65) + 0.35
    y = (self.b_painter_hardness * .4) + 0.35
    
    x = min(0.999,x)
    brush.curve.curves[0].points[1].location = [x,y]
    
    brush.curve.curves[0].points.update()
    brush.curve.update()


MATERIALS = []
def get_object_materials(self,context):
    global MATERIALS
    MATERIALS = []
    ob = context.active_object
    if ob != None:
        x = 0
        for i,slot in enumerate(ob.material_slots):
            x+=1
            if slot.material != None:
                mat = slot.material
                mats = get_materials_recursive(mat,mat.node_tree)
                for j,mat in enumerate(mats):
                    x+=1
                    icon = bpy.types.UILayout.icon(mat)
                    MATERIALS.append((mat.name,mat.name,mat.name,icon,x))
    if len(MATERIALS) == 0:
        MATERIALS.append(("","",""))
    return MATERIALS      

def set_active_material(self,context):
    wm = context.window_manager
    mat = bpy.data.materials[self.b_painter_active_material] if self.b_painter_active_material in bpy.data.materials else None
    if mat != None:
        for i,slot in enumerate(context.active_object.material_slots):
            if slot.material != None and slot.material == mat:
                context.active_object.active_material_index = i
                break
        mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index

def set_mat_shading(self,context):
    if self.b_painter_shadeless:
        set_material_shading(self,self,shadeless=True)
    else:    
        set_material_shading(self,self,shadeless=False)

def set_hotkeys(self,context):
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps['Image Paint']
    for item in keymap.keymap_items:
        if item.name == "Set Absolute Brush Size":
            item.active = self.b_painter_use_absolute_size
            
##############################

class BPainterImageSettings(bpy.types.PropertyGroup):
    def set_brush_lock_alpha(self,context):
        brush = context.tool_settings.image_paint.brush if context.tool_settings != None and context.tool_settings.image_paint != None else None
        brush.use_alpha = not(self.lock_alpha)
    
    lock_alpha = BoolProperty(default=False,update=set_brush_lock_alpha)
    active = BoolProperty(default=False)
    color = FloatVectorProperty(subtype="COLOR_GAMMA",min=0.0,max=1.0)    


class PaintChannels(bpy.types.PropertyGroup):
    name = StringProperty()
    group_name = StringProperty()

class PaintLayers(bpy.types.PropertyGroup):
    def rename(self,context):
        if self.mat_name in bpy.data.materials:
            mat = bpy.data.materials[self.mat_name]
            tex = mat.texture_slots[self.index].texture
            tex.name = self.name
            tex.image.name = self.name
            mat.b_painter.paint_layers_index = mat.b_painter.paint_layers_index
    
    def set_paint_layer_active(self,context):
        self["mask_layer_active"] = False
        self["paint_layer_active"] = True
        
        self.id_data.b_painter["layer_information"][self.name] = [1,0]
        self.id_data.b_painter.paint_layers_index = self.id_data.b_painter.paint_layers_index
        
    def set_mask_layer_active(self,context):
        self["paint_layer_active"] = False
        self["mask_layer_active"] = True
        
        self.id_data.b_painter["layer_information"][self.name] = [0,1]
        self.id_data.b_painter.paint_layers_index = self.id_data.b_painter.paint_layers_index

    name = StringProperty(update=rename)
    index = IntProperty()
    layer_type = StringProperty()
    mat_name = StringProperty()
    tex_node_name = StringProperty()
    mix_node_name = StringProperty()
    mask_mix_node_name = StringProperty()
    mask_tex_node_name = StringProperty()
    mask_img_name = StringProperty()
    img_name = StringProperty()
    merge_layer = BoolProperty(default=False)
    paint_layer_index = IntProperty()
    node_tree_name = StringProperty()
    
    ### procedural tex
    proc_tex_node_name = StringProperty()
    proc_ramp_node_name = StringProperty()
    
    ### mask and paint bool
    paint_layer_active = BoolProperty(default=True,update=set_paint_layer_active)
    mask_layer_active = BoolProperty(default=False,update=set_mask_layer_active)


class BPainterProperties(bpy.types.PropertyGroup):
    def set_merge_layers_index(self,context):
        self["merge_layers_index"] = -1
    
    paint_layers = CollectionProperty(type=PaintLayers)
    paint_layers_index = IntProperty(update=set_paint_layer)
    paint_channel_active = EnumProperty(name="Paint Channel",items=get_paint_channel,update=update_paint_channel)
    paint_channel_info = CollectionProperty(type=PaintChannels)
    node_tree_name = StringProperty()
    merge_layers = CollectionProperty(type=PaintLayers)
    merge_layers_index = IntProperty(default=-1,update=set_merge_layers_index)
    expanded = BoolProperty(default=True)
    external_path = StringProperty(name="External Image Path",description="If this path is set, images will be exported on blendfile save.")
    preview_aspect_ratio = IntVectorProperty(default=(1,1),size=2)
    
class BPainterBrushSettings(bpy.types.PropertyGroup):
    hardness = FloatProperty(min=0.0,max=1.0)
    
def register():
    
    bpy.types.WindowManager.b_painter_restart_needed = BoolProperty(default=False)  
    bpy.types.WindowManager.b_painter_modal_update = BoolProperty(default=False)
    bpy.types.WindowManager.b_painter_in_view_3d = BoolProperty(default=False)
    bpy.types.WindowManager.b_painter_brush_textures_loaded = BoolProperty(default=False)
    bpy.types.WindowManager.b_painter_stencil_textures_loaded = BoolProperty(default=False)
    bpy.types.WindowManager.b_painter_update_brushes = BoolProperty(default=True)
    bpy.types.WindowManager.b_painter_brush_filter = StringProperty(default="",update=update_brush_filter,options={'TEXTEDIT_UPDATE'})
    bpy.types.Scene.b_painter_texture_preview = BoolProperty(default=False)
    
    bpy.types.Image.b_painter = PointerProperty(type=BPainterImageSettings)
    
    bpy.types.Object.b_painter_active_material = EnumProperty(name="Active Material",items=get_object_materials,update=set_active_material)
    bpy.types.Object.b_painter_shadeless = BoolProperty(name="Shading Mode",description="Make all Materials shadeless.",default=False,update=set_mat_shading)
    
    bpy.types.Material.b_painter = PointerProperty(type=BPainterProperties)
    bpy.types.ShaderNodeMaterial.b_painter = PointerProperty(type=BPainterProperties)
    bpy.types.ShaderNodeMixRGB.b_painter_layer_hide = BoolProperty(default=False,update=set_show_hide)
    bpy.types.ShaderNodeRGBCurve.b_painter_layer_hide = BoolProperty(default=False,update=set_show_hide)
    bpy.types.ShaderNodeHueSaturation.b_painter_layer_hide = BoolProperty(default=False,update=set_show_hide)
    bpy.types.ShaderNodeInvert.b_painter_layer_hide = BoolProperty(default=False,update=set_show_hide)
    
    
    bpy.types.ShaderNodeMath.b_painter_opacity = FloatProperty(default=1.0,min=0.0,max=1.0,update=set_b_painter_opacity)
    bpy.types.ShaderNodeHueSaturation.b_painter_opacity = FloatProperty(default=1.0,min=0.0,max=1.0,update=set_b_painter_opacity)
    bpy.types.ShaderNodeRGBCurve.b_painter_opacity = FloatProperty(default=1.0,min=0.0,max=1.0,update=set_b_painter_opacity)
    bpy.types.ShaderNodeInvert.b_painter_opacity = FloatProperty(default=1.0,min=0.0,max=1.0,update=set_b_painter_opacity)
    
    bpy.types.Brush.b_painter_hardness = FloatProperty(min=0.0,max=1.0,update=set_brush_hardness)
    bpy.types.Scene.b_painter_absolute_size = FloatProperty(default=50,min=1,max=10000,soft_max=500,subtype="PIXEL")
    bpy.types.Scene.b_painter_use_absolute_size = BoolProperty(default=False,update=set_hotkeys,description="Constraint Brush Size to Zoom.")
    bpy.types.Scene.b_painter_flip_template_list = BoolProperty(name="Flip Layer Stack",default=True)
    
    bpy.types.Texture.b_painter_use_mask = BoolProperty(default=False,update=mute_ramp)
    bpy.types.Texture.b_painter_invert_mask = BoolProperty(default=False,update=invert_ramp)
    bpy.types.Texture.b_painter_invert_stencil_mask = BoolProperty(default=False,update=invert_stencil_ramp)
    bpy.types.Texture.b_painter_edit_tex = BoolProperty(default=False)

    bpy.types.Brush.b_painter_use_mask = BoolProperty(default=True,update=mute_ramp)
    bpy.types.Brush.b_painter_invert_mask = BoolProperty(default=True,update=invert_ramp)
    bpy.types.Brush.b_painter_invert_stencil_mask = BoolProperty(default=True,update=invert_stencil_ramp)
    bpy.types.Brush.b_painter_ramp_tonemap_l = FloatProperty(default=0.0,min=0.0,max=1.0,update=tonemap)
    bpy.types.Brush.b_painter_ramp_tonemap_r = FloatProperty(default=1.0,min=0.0,max=1.0,update=tonemap)
    bpy.types.Brush.b_painter_stencil_ramp_tonemap_l = FloatProperty(default=0.0,min=0.0,max=1.0,update=tonemap_stencil)
    bpy.types.Brush.b_painter_stencil_ramp_tonemap_r = FloatProperty(default=1.0,min=0.0,max=1.0,update=tonemap_stencil)
    bpy.types.Brush.b_painter_brush_order = IntProperty(default=0)
    
    
    bpy.types.Scene.b_painter_layer_mode = EnumProperty(items=(("Paint Layer","Paint Layer","Paint Layer"),("Mask Layer","Mask Layer","Mask Layer")))
    bpy.types.Scene.b_painter_show_stencil_settings = BoolProperty(default=True)
    bpy.types.Scene.b_painter_show_brush_settings = BoolProperty(default=True)
    bpy.types.Scene.b_painter_show_brush = BoolProperty(default=True)
    bpy.types.Scene.b_painter_show_layer_settings = BoolProperty(default=True)
    bpy.types.Scene.b_painter_show_color_settings = BoolProperty(default=True)
    bpy.types.Scene.b_painter_show_color_wheel = BoolProperty(default=False)
    bpy.types.Scene.b_painter_show_color_palette = BoolProperty(default=True)
        
    bpy.types.Scene.b_painter_brush = EnumProperty(items=get_brushes,update=set_brush)
    
    #####
    bpy.types.Brush.b_painter_brush_texture = EnumProperty(items=get_brush_tex_previews,update=set_texture)
    bpy.types.Brush.b_painter_stencil_texture = EnumProperty(items=get_stencil_tex_previews,update=set_stencil_texture)
    bpy.types.Brush.b_painter_tex_brush_categories = EnumProperty(items=get_category_dirs,name="Texture Categories",update=refresh_brush_category)
    bpy.types.Scene.b_painter_tex_stencil_categories = EnumProperty(items=get_category_dirs,name="Stencil Categories",update=refresh_stencil_category)
    bpy.types.Scene.b_painter_active_stencil_category = StringProperty(default="None")
    bpy.types.Scene.b_painter_active_tex_brush_category = StringProperty(default="None")
    bpy.types.Scene.b_painter_active_tex_brush = StringProperty(default="None")
    
    bpy.types.Brush.b_painter_multi_layer_brush = BoolProperty(default=False)
    
    
    bpy.types.Scene.b_painter_load_first_time = BoolProperty(default=True)
    