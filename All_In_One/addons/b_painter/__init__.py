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

bl_info = {
    "name": "BPainter",
    "description": "BPainter is a powerfull painting addon for blender.",
    "author": "Andreas Esau",
    "version": (1, 1),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "http://bpainter.artbyndee.de/introduction",
    "category": "Paint" }


import bpy
from bpy.app.handlers import persistent

# load and reload submodules
##################################

import importlib
from . import developer_utils
from . import bpainter_properties as paint_props
from . functions import save_images, clear_brush_textures, b_version_bigger_than, copy_dir, setup_b_painter, get_addon_prefs, update_all_paint_layers
from . operators.preset_handling import brush_icons_path_user, register_previews, unregister_previews, user_path, presets_path, presets_user_path, addon_path
from . import ui
import os
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
##################################

import traceback

class ExampleAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    def inform_restart(self,context):
        context.window_manager.b_painter_restart_needed = True
        
    auto_set_viewport_shading = bpy.props.BoolProperty(name="Auto Set Viewport Shading", description="This will automatically set the Viewport Shading to Material when entering the Texture Paint.",default=True)
    override_buildin_colorpicker = bpy.props.BoolProperty(name="Override Buildin Colorpicker", description="This will override the buildin colorpicker that can be trigger with the S key.",default=True,update=inform_restart)
    use_alt_as_colorpicker = bpy.props.BoolProperty(name="Use Alt as Colorpicker", description="That way alt will be used as Colorpicker.",default=True, update=inform_restart)
    use_layer_alpha_lock = bpy.props.BoolProperty(name="Use Layer Alpha Lock",description='If used, the Brush "Use Alpha" setting is overwritten by the layer Alpha Lock setting.',default=True)
    
    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        row = layout.row()    
        #row.prop(self, "auto_set_viewport_shading")
        if wm.b_painter_restart_needed:
            row.label(text="Save User Settings and restart Blender.",icon="ERROR")
        row = layout.row()
        row.prop(self, "use_alt_as_colorpicker")
        row = layout.row()
        row.prop(self, "override_buildin_colorpicker")
        row = layout.row()
        row.prop(self, "use_layer_alpha_lock")
        
        row = layout.row()
        op = row.operator("b_painter.import_brush_from_json",text="Load Brush Factory Settings",icon="LOAD_FACTORY")
        op.force_restore = True
        op.all_brushes = True
        

addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    if "Image Paint" not in addon_keymaps:
        km = addon.keymaps.new(name = "Image Paint", space_type = "EMPTY")
    else:
        km = addon.keymaps["Image Paint"]       
    # insert keymap items here
    if get_addon_prefs(bpy.context).use_alt_as_colorpicker:
        kmi = km.keymap_items.new("b_painter.color_pipette", type = "LEFTMOUSE", value = "PRESS", alt = True)
    kmi = km.keymap_items.new("b_painter.set_brush_hardness", type = "F", value = "PRESS", alt = True)
    kmi = km.keymap_items.new("b_painter.toggle_eraser", type = "E", value = "PRESS")
    kmi = km.keymap_items.new("b_painter.multi_layer_paint", type = "LEFTMOUSE", value = "PRESS", shift = True)
    kmi = km.keymap_items.new("b_painter.plane_texture_preview", type = "L", value = "PRESS")
    
    kmi = km.keymap_items.new("b_painter.set_absolute_brush_size", type = "F", value = "PRESS")
    kmi.active = False
    
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "A", value = "PRESS")
    kmi.properties.name = "view3d.b_painter_pie_menu"
    
    if get_addon_prefs(bpy.context).override_buildin_colorpicker:
        kmi = km.keymap_items.new("b_painter.color_pipette", type = "S", value = "PRESS")
        kmi.properties.pick_mode = "HOTKEY"
    
    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    ui.register_previews()
    register_previews()
    
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    paint_props.register()
    bpy.app.handlers.scene_update_post.append(start_modal_update)
    bpy.app.handlers.load_post.append(b_painter_startup)
    bpy.app.handlers.save_pre.append(save_pre_operations)
    
    register_keymaps()
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    copy_dir(presets_path, presets_user_path)

def unregister():
    ui.unregister_previews()
    unregister_previews()
    
    unregister_keymaps()
    
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    bpy.app.handlers.load_post.remove(b_painter_startup)
    bpy.app.handlers.save_pre.remove(save_pre_operations)
    
    print("Unregistered {}".format(bl_info["name"]))


def check_if_addon_loads_first_time():
    file = os.path.join(addon_path,"addon_initialized")
    if not os.path.isfile(file):
        bpy.ops.b_painter.import_brush_from_json(all_brushes=True,force_restore=True)
        file = open(file, 'w+')

def start_modal_update(dummy):
    if bpy.context != None:
        bpy.context.window_manager["b_painter_startup_done"] = True
        bpy.data.scenes[0].b_painter_use_absolute_size = bpy.data.scenes[0].b_painter_use_absolute_size ### set shortcut for brush size
        
        bpy.app.handlers.scene_update_post.remove(start_modal_update)
        
        #################################
        context = bpy.context
        scene = context.scene
        context.window_manager.b_painter_brush_textures_loaded = False
        active_object = context.active_object
        active_stencil_category = str(bpy.context.scene.b_painter_active_stencil_category)
        active_tex_brush_category = str(bpy.context.scene.b_painter_active_tex_brush_category)
        active_brush_tex = str(bpy.context.scene.b_painter_active_tex_brush)
        active_brush = str(context.scene.b_painter_brush)
        if "b_painter_panels" not in bpy.context.scene:
            bpy.context.scene["b_painter_panels"] = ["BRUSH","COLOR","TEXTURE","STENCIL","LAYER"]    
        ###
        if active_object != None:
            if active_object.b_painter_active_material != "":
                active_object.b_painter_active_material = active_object.b_painter_active_material
        
        ### load brushes and presets
        bpy.ops.b_painter.import_brush_from_json(all_brushes=True)
        bpy.ops.b_painter.import_palette_from_json(all_palettes=True)
        
        for brush in bpy.data.brushes:
            if "b_painter" in brush and brush != context.tool_settings.image_paint.brush:
                context.scene.b_painter_brush = brush.name
                bpy.ops.b_painter.import_brush_from_json(all_brushes=False,brush_name=brush.name,show_info_msg=False)    
        
        ### set brush icons to addons path
        for brush in bpy.data.brushes:
            if "b_painter" in brush and brush.use_custom_icon and not os.path.isfile(brush.icon_filepath):
                icon_name = os.path.basename(brush.icon_filepath)
                icon_filepath = os.path.join(brush_icons_path_user,icon_name)
                if os.path.isfile(icon_filepath):
                    brush.icon_filepath = icon_filepath
        
        if context.tool_settings.image_paint.brush != None and context.tool_settings.image_paint.brush.mask_texture_slot.mask_map_mode == "STENCIL":
            if context.active_object != None and context.active_object.mode == "TEXTURE_PAINT":
                bpy.ops.brush.stencil_reset_transform(mask=True)
        
        if bpy.context.scene.b_painter_load_first_time: 
            setup_b_painter()
            bpy.context.scene.b_painter_load_first_time = False
        else:  
            try:
                if "b_painter_active_brush" in scene:
                    if bpy.context.scene["b_painter_active_brush"] == "":
                        bpy.context.scene.b_painter_brush = "Brush Default"
                    else:
                        bpy.context.scene.b_painter_brush = scene["b_painter_active_brush"]
            except:
                pass    
            try:
                bpy.context.scene.b_painter_tex_stencil_categories = active_stencil_category
            except:
                pass
            try:
                brush = bpy.context.tool_settings.image_paint.brush
                brush.b_painter_tex_brush_categories = active_tex_brush_category
            except:
                pass
            try:
                brush = bpy.context.tool_settings.image_paint.brush
                brush.b_painter_brush_texture = active_brush_tex
            except:
                pass
        check_if_addon_loads_first_time()    

@persistent
def b_painter_startup(dummy):
    context = bpy.context
    bpy.app.handlers.scene_update_post.append(start_modal_update)
        
        
### save pre operations    
@persistent
def save_pre_operations(dummy):
    save_images() 
    scene = bpy.context.scene
    if "b_painter_active_brush" not in scene:
        scene["b_painter_active_brush"] = ""
    if scene["b_painter_active_brush"] != scene.b_painter_brush:
        scene["b_painter_active_brush"] = scene.b_painter_brush
 
