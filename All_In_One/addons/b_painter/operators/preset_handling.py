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
from distutils.dir_util import copy_tree
import bpy
from bpy.props import StringProperty, BoolProperty
from .. functions import id_from_string
import json
from collections import OrderedDict
import mathutils

addon_path = os.path.join(bpy.utils.user_resource("SCRIPTS","addons"),"b_painter")
presets_path = os.path.join(addon_path,"presets")
user_path = os.path.join(os.path.expanduser("~"),".BPainter")
presets_user_path = os.path.join(user_path,"presets")
texture_path = os.path.join(presets_user_path,"textures")
brush_icons_path = os.path.join(presets_path,"brush_icons")
brush_icons_path_user = os.path.join(presets_user_path,"brush_icons")
ext = ".blend"
preview_collections = {}

def get_brush_data(brush):
    brush_data = OrderedDict()
    
    exported_props = []
    exported_props.append("blend")
    exported_props.append("color")
    exported_props.append("secondary_color")
    exported_props.append("use_pressure_size")
    exported_props.append("use_pressure_strength")
    exported_props.append("use_alpha")
    exported_props.append("stroke_method")
    exported_props.append("spacing")
    exported_props.append("use_pressure_spacing")
    exported_props.append("use_relative_jitter")
    exported_props.append("jitter")
    exported_props.append("use_pressure_jitter")
    exported_props.append("use_smooth_stroke")
    exported_props.append("smooth_stroke_radius")
    exported_props.append("smooth_stroke_factor")
    exported_props.append("curve")
    exported_props.append("use_cursor_overlay")
    exported_props.append("cursor_overlay_alpha")
    exported_props.append("use_cursor_overlay_override")
    exported_props.append("use_primary_overlay")
    exported_props.append("texture_overlay_alpha")
    exported_props.append("use_primary_overlay_override")
    exported_props.append("use_custom_icon")
    exported_props.append("icon_filepath")
    exported_props.append("stroke_method")
    exported_props.append("texture_slot")
    exported_props.append("mask_texture_slot")
    exported_props.append("image_tool")
    exported_props.append("use_gradient")
    exported_props.append("gradient")
    exported_props.append("gradient_fill_mode")
    
    texture_slot_props = []
    texture_slot_props.append("tex_paint_map_mode")
    texture_slot_props.append("random_angle")
    texture_slot_props.append("angle")
    texture_slot_props.append("use_rake")
    texture_slot_props.append("use_random")
    
    mask_texture_slot_props = []
    mask_texture_slot_props.append("mask_map_mode")
    
    
    
    for prop_name in dir(brush):
        if "b_painter" in prop_name or prop_name in exported_props and prop_name != "b_painter_stencil_tex_name":
                
            
            prop = getattr(brush,prop_name)
            
            if prop_name == "icon_filepath":
                name = os.path.basename(getattr(brush,prop_name))
                brush_data[prop_name] = name
            elif prop_name == "gradient" and brush.image_tool == "FILL":
                gradient = {}
                colors = []
                for element in prop.elements:
                    colors.append([list(element.color),element.position])
                gradient["colors"] = colors
                gradient["color_mode"] = prop.color_mode
                gradient["hue_interpolation"] = prop.hue_interpolation
                brush_data[prop_name] = gradient
                
                
            elif type(prop) != mathutils.Color and type(prop) != bpy.types.CurveMapping and type(prop) != bpy.types.BrushTextureSlot:
                brush_data[prop_name] = getattr(brush,prop_name)
            
            elif type(prop) == mathutils.Color:
                color = getattr(brush,prop_name)
                brush_data[prop_name] = [color[0],color[1],color[2]]
            
            elif type(prop) == bpy.types.CurveMapping:
                curves = getattr(brush,prop_name)
                for curve in curves.curves:
                    curve_points = []
                    for point in curve.points:
                        curve_points.append([point.location[0],point.location[1]])
                    brush_data[prop_name] = curve_points
            elif type(prop) == bpy.types.BrushTextureSlot:
                if prop_name == "texture_slot":
                    tex_slot_props = {}
                    for tex_slot_prop_name in dir(prop):
                        if tex_slot_prop_name in texture_slot_props:
                            tex_slot_props[tex_slot_prop_name] = getattr(prop,tex_slot_prop_name)
                        
                    brush_data[prop_name] = tex_slot_props
                            
                                
                        
                elif prop_name == "mask_texture_slot":
                    mask_tex_slot_props = {}
                    for mask_tex_slot_prop_name in dir(prop):
                        if mask_tex_slot_prop_name in mask_texture_slot_props:
                            mask_tex_slot_props[mask_tex_slot_prop_name] = getattr(prop,mask_tex_slot_prop_name)
                            
                    brush_data[prop_name] = mask_tex_slot_props        
                    
    return brush_data



def save_brush_data(path, brush_settings = OrderedDict()):
    json_file = json.dumps(brush_settings, indent="\t", sort_keys=False)
    
    file_path = os.path.join(path,"brushes.json")
        
    text_file = open(file_path, "w")
    text_file.write(json_file)
    text_file.close()                
    

def load_brush_data(path):
    brush_data = os.path.join(path,"brushes.json")
    with open(brush_data) as data_file:    
        data = json.load(data_file)
    return data    


def import_brush(brush_name, brush_data):
    context = bpy.context
    brush = None
    if brush_name in bpy.data.brushes:
        brush = bpy.data.brushes[brush_name]
    else:
        brush = bpy.data.brushes.new(name=brush_name,mode="TEXTURE_PAINT")
    
    if True:
        brush.use_fake_user = False
        brush["b_painter"] = True
        if brush_name in brush_data:
            for i,prop_name in enumerate(brush_data[brush_name]):
                prop_type = type(brush_data[brush_name][prop_name])
                prop_value = brush_data[brush_name][prop_name]

                if prop_name in dir(brush):    
                    if prop_type != list and prop_type != dict:
                        if prop_name == "icon_filepath":
                            prop_value = os.path.join(brush_icons_path_user,prop_value)
                        try:       
                            setattr(brush,prop_name,prop_value)
                        except Exception as e:
                            pass
                    elif prop_type == dict:
                        if prop_name != "gradient":
                            for slot_key in prop_value:
                                slot_prop = prop_value[slot_key]
                                setattr(getattr(brush,prop_name),slot_key,slot_prop)
                        
                        elif prop_name == "gradient":
                            if brush.gradient != None:
                                while len(brush.gradient.elements) >= 2:
                                    brush.gradient.elements.remove(brush.gradient.elements[0])
                                for key in prop_value:    
                                    if key == "colors":
                                        
                                        for i,color in enumerate(prop_value["colors"]):
                                            if i > 0:
                                                brush.gradient.elements.new(color[1] )
                                            
                                            brush.gradient.elements[i].color = color[0]
                                            brush.gradient.elements[i].position = color[1]
                                    else:
                                        setattr(getattr(brush,prop_name),key,prop_value[key])
                    elif prop_type == list:
                        if "color" in prop_name:
                            setattr(brush,prop_name,prop_value)
                        elif "curve" in prop_name:
                            
                            points_len = len(brush.curve.curves[0].points)
                            for i in range(points_len):
                                if len(brush.curve.curves[0].points) > 2:
                                    point = brush.curve.curves[0].points[0]
                                    brush.curve.curves[0].points.remove(point)
                                    brush.curve.curves[0].points.update()
                                    brush.curve.update()
                                    
                            for i,point in enumerate(prop_value):
                                if i > len(brush.curve.curves[0].points)-2:
                                    brush.curve.curves[0].points.new(point[0],point[1])
                                else:
                                    brush.curve.curves[0].points[i].location = point
                                brush.curve.curves[0].points.update()
                                brush.curve.update()
        bpy.context.scene.update()



class ImportBrushFromJson(bpy.types.Operator):
    bl_idname = "b_painter.import_brush_from_json"
    bl_label = "Import Brush From Json"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    brush_name = StringProperty()
    all_brushes = BoolProperty(default=False)
    show_info_msg = BoolProperty(default=True)
    restore_default = BoolProperty(default=False)
    force_restore = BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        brush_data = load_brush_data(presets_path)
        
        ### get brush data
        if not self.restore_default:
            brush_data_user = load_brush_data(presets_user_path)
        else:
            brush_data_user = load_brush_data(presets_path)
        
        ### if addon brush data not in user brush data. copy into user brush data and save
        for key in brush_data:
            if key not in brush_data_user or self.force_restore:
                brush_data_user[key] = brush_data[key]
        save_brush_data(presets_user_path,brush_data_user)
        
            
        if context.tool_settings.image_paint.brush != None:
            active_brush_name = str(context.tool_settings.image_paint.brush.name)
        else:
            active_brush_name = "None"
            
        if self.all_brushes:
            for i,brush_name in enumerate(brush_data_user):
                if brush_name != active_brush_name  or self.force_restore:
                    import_brush(brush_name, brush_data_user)
                
            try:
                bpy.context.scene.b_painter_brush = bpy.context.scene.b_painter_brush
            except:
                pass    

        else:
            import_brush(self.brush_name, brush_data_user)
            msg = self.brush_name + " has been reset."
            if self.show_info_msg:
                self.report({'INFO'}, msg)
        
        wm.b_painter_update_brushes = True
        
        if self.restore_default:
            bpy.ops.b_painter.export_brush_as_json(brush_name=self.brush_name)
        return {"FINISHED"}
        

class ExportBrushAsJson(bpy.types.Operator):
    bl_idname = "b_painter.export_brush_as_json"
    bl_label = "Export Brush As Json Data"
    bl_description = "Save Custom Brush Settings."
    bl_options = {"REGISTER"}

    brush_name = StringProperty()
    store_in_addon_dir = BoolProperty()
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        brush_data = load_brush_data(presets_path)
        brush_data_user = load_brush_data(presets_user_path)
        
        brush_data_user[self.brush_name] = get_brush_data(bpy.data.brushes[self.brush_name])
        save_brush_data(presets_user_path,brush_data_user)
        
        if event.ctrl or self.store_in_addon_dir:
            brush_data[self.brush_name] = brush_data_user[self.brush_name]
            save_brush_data(presets_path,brush_data)
            
            
        msg = self.brush_name + " has been saved as Preset."
        self.report({'INFO'}, msg)
        if event.ctrl or self.store_in_addon_dir:
            return wm.invoke_confirm(self,event)
        else:    
            return {"FINISHED"}
    
class AddNewBrush(bpy.types.Operator):
    bl_idname = "b_painter.add_new_brush"
    bl_label = "Add New Brush"
    bl_description = ""
    bl_options = {"REGISTER"}

    brush_name = StringProperty(default="")

    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self,context):
        layout = self.layout
        layout.prop(self,"brush_name",text="Brush Name")
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        wm = context.window_manager
        wm.b_painter_update_brushes = True
        
        brush_data = load_brush_data(presets_path)
        brush_data_user = load_brush_data(presets_user_path)
        
        bpy.ops.brush.add()
        brush = context.tool_settings.image_paint.brush
        brush.name = self.brush_name
        context.scene.b_painter_brush = brush.name
        bpy.ops.b_painter.export_brush_as_json("INVOKE_DEFAULT",brush_name=brush.name,store_in_addon_dir=True)
        return {"FINISHED"}

BRUSHES = []
def get_brushes(self,context):
    wm = context.window_manager
    global BRUSHES
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
    
class DeleteBrush(bpy.types.Operator):
    bl_idname = "b_painter.delete_brush"
    bl_label = "Delete Brush"
    bl_description = ""
    bl_options = {"REGISTER"}

    brush_name = StringProperty(default="")

    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self,context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete this Brush?",icon="ERROR")
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        wm = context.window_manager
        wm.b_painter_update_brushes = True
        
        if context.scene.b_painter_brush in bpy.data.brushes:
            brush = bpy.data.brushes[context.scene.b_painter_brush]
            
            brush_data = load_brush_data(presets_path)
            brush_data_user = load_brush_data(presets_user_path)
            
            if brush.name in brush_data:
                del(brush_data[brush.name])
            if brush.name in brush_data_user:
                del(brush_data_user[brush.name])
            
            save_brush_data(presets_path,brush_data)
            save_brush_data(presets_user_path,brush_data_user)
            
            bpy.data.brushes.remove(brush,do_unlink=True)
            brushes = get_brushes(self,context)
            
            wm.b_painter_update_brushes = True
            context.tool_settings.image_paint.brush = bpy.data.brushes[brushes[0][0]]
            context.scene.b_painter_brush = brushes[0][0]
        
        return {"FINISHED"}    

##################################################################################################################################################################

def get_palette_data(palette):
    
    colors = []
    for color in palette.colors:
        colors.append(list(color.color))
    
    return colors

def save_palette_data(path, palette_items = OrderedDict()):
    json_file = json.dumps(palette_items, indent="\t", sort_keys=False)
    
    text_file = open(os.path.join(path,"palettes.json"), "w")
    text_file.write(json_file)
    text_file.close()      
    
def load_palette_data(path):
    palette_data = os.path.join(path,"palettes.json")
    with open(palette_data) as data_file:    
        data = json.load(data_file)
    return data    

def import_palette(palette_name, palette_data):
    context = bpy.context
    if palette_name in bpy.data.palettes and "b_painter" in bpy.data.palettes[palette_name]:
        palette = bpy.data.palettes[palette_name]
        palette.use_fake_user = False
        palette.user_clear()
        bpy.data.palettes.remove(palette)
        
    if palette_name not in bpy.data.palettes:
        palette = bpy.data.palettes.new(name=palette_name)
        palette.use_fake_user = False
        palette["b_painter"] = True
        
        for color in palette_data[palette_name]:
            new_color = palette.colors.new()
            new_color.color = color
    return palette        

    
class ExportPaletteAsJson(bpy.types.Operator):
    bl_idname = "b_painter.export_palette_as_json"
    bl_label = "Export Palette As Json Data"
    bl_description = ""
    bl_options = {"REGISTER"}

    palette_name = StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        palette_data = load_palette_data(presets_user_path)
        
        palette_data[self.palette_name] = get_palette_data(bpy.data.palettes[self.palette_name])
        
        save_palette_data(presets_user_path,palette_data)
        return {"FINISHED"}
    
class ImportPaletteFromJson(bpy.types.Operator):
    bl_idname = "b_painter.import_palette_from_json"
    bl_label = "Import Palette From Json"
    bl_description = ""
    bl_options = {"REGISTER"}

    palette_name = StringProperty()
    all_palettes = BoolProperty(default=False)
    restore_default = BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        if self.restore_default:
            palette_data = load_palette_data(presets_path)
        else:    
            palette_data = load_palette_data(presets_user_path)
        
        if self.all_palettes:
            for palette_name in palette_data:
                import_palette(palette_name, palette_data)
            if context.tool_settings.image_paint.palette == None:
                context.tool_settings.image_paint.palette = bpy.data.palettes["BPainter_Default_Palette"]
        else:
            import_palette(self.palette_name, palette_data)
        
        
        if self.restore_default:
            bpy.ops.b_painter.export_palette_as_json(palette_name=self.palette_name)
        
        if bpy.context.tool_settings.image_paint.palette != None and bpy.context.tool_settings.image_paint.palette.colors.active != None:
            context.scene["current_palette_color"] = list(bpy.context.tool_settings.image_paint.palette.colors.active.color)    
        return {"FINISHED"}
            


##################################################################################################################################################################################################################

    
def get_tex_previews(self, context,tex_type="BRUSH"):
    
    misc_icons = preview_collections["b_painter_misc_icons"]
    icon_id = misc_icons["icon_none"].icon_id
    
    enum_items = []
    enum_items.append(("None","","None",icon_id,0))    
    
    
    brush = context.tool_settings.image_paint.brush
    
    category = brush.b_painter_tex_brush_categories 
    if brush.b_painter_multi_layer_brush:
        pass
    
    if brush != None:
        # Get the preview collection (defined in register func).
        if tex_type == "BRUSH":
            pcoll = preview_collections["b_painter_tex_previews"]
            final_texture_path = os.path.join(texture_path, category)
        elif tex_type == "STENCIL":
            pcoll = preview_collections["b_painter_stencil_previews"]
            final_texture_path = os.path.join(texture_path, context.scene.b_painter_tex_stencil_categories)   
        if os.path.exists(final_texture_path):
            # Scan the directory for png files
            image_paths = []
            for name in os.listdir(final_texture_path):
                if name.lower().endswith(".png") or name.lower().endswith(".jpg"):
                    image_paths.append(name)
            for i, name in enumerate(image_paths):
                
                # generates a thumbnail preview for a file.
                filepath = os.path.join(final_texture_path, name)
                
                if filepath not in pcoll:
                    thumb = pcoll.load(filepath, filepath, 'IMAGE')
            
            ### sort list of pathes with substring of the filename
            sorted_list = []
            for key in pcoll:
                sorted_list.append(key)
            sorted_list.sort(key= lambda x: os.path.basename(x))   
            
            for i,key in enumerate(sorted_list):
                if os.path.exists(key):
                    preview = pcoll[key]
                    icon_id = preview.icon_id
                    file_name = os.path.basename(key)
                    if tex_type == "BRUSH":        
                        if "b_painter_brush_img" in bpy.data.images and "b_painter_brush_tex" in bpy.data.textures:
                            img = bpy.data.images["b_painter_brush_img"]
                            tex = bpy.data.textures["b_painter_brush_tex"]
                            if file_name in img.filepath:
                                icon_id = bpy.types.UILayout.icon(tex)
                    
                        if category in key:# and category not in file_name:
                            enum_items.append((file_name, file_name, file_name, icon_id, id_from_string(file_name)))
                    
                    elif tex_type == "STENCIL":        
                        if "b_painter_stencil_img" in bpy.data.images and "b_painter_stencil_tex" in bpy.data.textures:
                            img = bpy.data.images["b_painter_stencil_img"]
                            tex = bpy.data.textures["b_painter_stencil_tex"]
                            if file_name in img.filepath:
                                icon_id = bpy.types.UILayout.icon(tex)
                                
                        if context.scene.b_painter_tex_stencil_categories:# in key and context.scene.b_painter_tex_stencil_categories not in file_name:
                            enum_items.append((file_name, file_name, file_name, icon_id, id_from_string(file_name)))
                            
                else:
                    del(pcoll[key])    
           
    pcoll.my_previews = enum_items
    loaded_previews = []
    pcoll.my_previews_dir = final_texture_path
        
    return pcoll.my_previews
    
def get_brush_tex_previews(self,context):
    pcoll = preview_collections["b_painter_tex_previews"]
    if not context.window_manager.b_painter_brush_textures_loaded:
        context.window_manager.b_painter_brush_textures_loaded = True
        return get_tex_previews(self,context)
    else:
        return pcoll.my_previews
    
def get_stencil_tex_previews(self,context):
    pcoll = preview_collections["b_painter_stencil_previews"]
    if not context.window_manager.b_painter_stencil_textures_loaded:
        context.window_manager.b_painter_stencil_textures_loaded = True
        return get_tex_previews(self,context,tex_type="STENCIL")
    else:
        return pcoll.my_previews
    

def refresh_previews():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    register_previews()

def unregister_previews():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
        
def register_previews():
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    
    
    pcoll2 = bpy.utils.previews.new()
    pcoll2.my_previews_dir = ""
    pcoll2.my_previews = ()
    
    pcoll3 = bpy.utils.previews.new()
    pcoll3.my_previews_dir = ""
    pcoll3.my_previews = ()
    pcoll3.load("icon_none", os.path.join(brush_icons_path,"none.png"), 'IMAGE')
    
    
    preview_collections["b_painter_tex_previews"] = pcoll
    preview_collections["b_painter_stencil_previews"] = pcoll2
    preview_collections["b_painter_misc_icons"] = pcoll3
    
class RefreshPreviews(bpy.types.Operator):
    bl_idname = "b_painter.refresh_previews"
    bl_label = "Refresh Previews"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        refresh_previews()
        context.window_manager.b_painter_brush_textures_loaded = False
        context.window_manager.b_painter_stencil_textures_loaded = False
        return {"FINISHED"}
    
class OpenTextureFolder(bpy.types.Operator):
    bl_idname = "b_painter.open_texture_folder"
    bl_label = "Open Texture Folder"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.wm.path_open(filepath = texture_path)
        return {"FINISHED"}
            
            
