'''
Copyright (C) 2015 Pistiwique, Pitiwazou
 
Created by Pistiwique, Pitiwazou
 
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
from . function_utils.get_path import get_library_path
from os.path import join, isdir, isfile, basename
from os import listdir
from . icons.icons import load_icons
from .function_utils.get_path import (get_directory,
                                      get_addon_path,
                                      get_library_path,
                                      get_addon_preferences,
                                      )
from .assets_scenes.assets_functions import (get_groups,
                                             get_scripts,
                                             )
from .materials.materials_functions import (get_custom_material_render_scene,
                                            get_valid_materials,
                                            )
from .operators import settings

from .assets_scenes.assets_scene_op import *
from .ibl.ibl_op import *
from .materials.materials_op import *
from .operators import *
from .library.operators import *

# -----------------------------------------------------------------------------
#    POPUP MENU OPTIONS
# -----------------------------------------------------------------------------

class PropertiesMenu(bpy.types.Operator):
    bl_idname = "view3d.properties_menu"
    bl_label = "Properties Menu"
 
    def execute(self, context):
        return {'FINISHED'}
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        self.dpi_value = bpy.context.user_preferences.system.dpi
 
        return context.window_manager.invoke_props_dialog(self, width=self.dpi_value*5, height=100)
 
    def draw(self, context):
        layout = self.layout
        AM = context.window_manager.asset_m
        addon_prefs = get_addon_preferences()
        thumbnails_path = get_directory('icons')
        extentions = (".jpg", ".jpeg", ".png")
        thumbnail_list = [f.rsplit(".", 1)[0] for f in listdir(thumbnails_path) if f.endswith(extentions)]
        
        row = layout.row(align = True)
        row.prop(AM, "option_choise", expand = True)
        
        if AM.option_choise == 'tools':
            layout.separator()
            row = layout.row(align = True)
            row.prop(AM, "tools_options", expand = True)
            layout.separator()
            if AM.tools_options == 'assets':
                layout.label("RENAME ASSET")
                split = layout.split(percentage = 0.1)
                split.separator()
                row = split.row(align=True)
                row.prop(AM, "new_name", text="New name")
                #Check icon List
                if AM.new_name:
                    if AM.new_name in thumbnail_list:
                        split = layout.split(percentage = 0.1)
                        split.separator()
                        split.label("\" {} \" already exist".format(AM.new_name), icon='ERROR')
                    else:
                        row.operator("object.change_name_asset", text="", icon='FILE_TICK')
                
                layout.label("MOVE ASSET")
                split = layout.split(percentage = 0.1)
                split.separator()
                row = split.row()
                row.prop(AM, "new_lib", text = "Libraries")
                split = layout.split(percentage = 0.1)
                split.separator()
                row = split.row()
                row.prop(AM, "new_cat", text = "Categories")
                layout.separator()
                split = layout.split(percentage = 0.12)
                split.separator()
                row = split.row()
                row.operator("object.move_asset", text = "Move asset")
                layout.separator()
                
            else:
                layout.separator()
                layout.operator("object.debug_preview", text = "Debug")
                layout.separator()
            
        elif AM.option_choise == 'import':
            if AM.library_type == 'materials':
                if AM.libraries == "Render Scenes":
                    layout.prop(AM, "active_layer", text="Use Active layer")
                layout.prop(AM, "existing_material", text="Use Existing Materials")
            else:
                layout.prop(AM, "active_layer", text="Use Active layer")
                layout.prop(AM, "existing_material", text="Use Existing Materials")
                layout.prop(AM, "existing_group", text="Use Existing Groups")
                if AM.import_choise == 'link':
                    layout.prop(AM, "run_script", text="run script when imported")
                layout.prop(AM, "snap_enabled", text="Snap to faces")
            
        elif AM.option_choise == 'display':
            layout.prop(addon_prefs, "show_name_assets", text="Show Preview's names")
            layout.prop(addon_prefs, "show_labels", text="Show labels in the preview")
        
# -----------------------------------------------------------------------------
#    ASSETS ADDING OPTIONS PANEL
# -----------------------------------------------------------------------------
        
def asset_adding_panel(self, context):
    """ Sub panel for the adding assets """
    
    AM = context.window_manager.asset_m
    layout = self.layout
    box = layout.box()
    act_obj = context.active_object
    obj_list = [obj for obj in context.scene.objects if obj.select]
    thumbnails_path = get_directory('icons')
    is_subsurf = False
    view = context.space_data
    fx_settings = view.fx_settings
    ssao_settings = fx_settings.ssao
    extentions = (".jpg", ".jpeg", ".png")
    thumb_list = [thumb.rsplit(".", 1)[0] for thumb in listdir(thumbnails_path) if thumb.endswith(extentions)]
    
    if len(obj_list) >= 2:
        asset_name = AM.group_name
    
    else:
        asset_name = act_obj.name
        if act_obj.modifiers:
            for mod in act_obj.modifiers:
                if mod.type == 'SUBSURF':
                    is_subsurf = True
    
    if asset_name not in thumb_list or asset_name in thumb_list and AM.replace_rename == 'replace':
        if asset_name in thumb_list and AM.replace_rename == 'replace':
            box.label("\" {} \" already exist".format(asset_name), icon='ERROR')
            box.separator()
            row = box.row(align=True)
            row.prop(AM, "replace_rename", text=" ", expand=True)
            if AM.replace_rename == 'rename':
                if multi_object:
                    box.prop(AM, "group_name", text="")
                else:
                    ob = context.object
                    box.prop(ob, "name", text="")         
        
        else:
            if len(obj_list) >= 2:
                row = box.row()
                box.label("Choose the asset name")
                box.prop(AM, "group_name", text = "")
            
            else:
                ob = context.object
                box.prop(ob, "name", text="Name")
            
        row = box.row(align = True)
        row.prop(AM, "render_type", text = " ", expand = True)
        row = box.row()
        row.label("Thumbnail extention:")
        row = box.row(align = True)
        row.prop(AM, "thumb_ext", expand = True)
        
        # ---------------------- #          
        #   RENNDER THUMBNAIL    #
        # ---------------------- #
 
        if AM.render_type == 'render':
            if len(obj_list) == 1 and not is_subsurf:
                box.prop(AM, "add_subsurf", text = "Subsurf")
                box.prop(AM, "add_smooth", text = "Smooth")  
 
            box.prop(AM, "material_render", text="Addon material")
        
        # --------------------- #          
        #   OPENGL THUMBNAIL    #
        # --------------------- #
 
        elif AM.render_type == 'opengl':
            row = box.row(align=True)
            row.operator("object.setup_ogl_render", text="Setup OGL render" if not "AM_OGL_Camera" in [obj.name for obj in context.scene.objects] else "View camera", icon='ZOOMIN')
            row.operator("object.remove_ogl_render", text="", icon='ZOOMOUT')
            row = layout.column()
            row = box.row(align=True) 
            row.label("Background:")
            row.prop(AM, "background_alpha", text="")
            row = box.row(align=True)
            row.prop(view, "show_only_render")
            row = box.row(align=True)
            row.prop(view, "use_matcap")
            if view.use_matcap :
                row.prop(AM, "matcap_options", text="", icon='TRIA_UP' if AM.matcap_options else 'TRIA_DOWN')    
                if AM.matcap_options:
                    row = box.row(align=True)
                    row.template_icon_view(view, "matcap_icon")
            row = box.row(align=True)
            row.prop(fx_settings, "use_ssao", text="Ambient Occlusion")
            if fx_settings.use_ssao:
                row.prop(AM, "ao_options", text="", icon='TRIA_UP' if AM.ao_options else 'TRIA_DOWN')    
                if AM.ao_options:
                    subcol = box.column(align=True)
                    subcol.prop(ssao_settings, "factor")
                    subcol.prop(ssao_settings, "distance_max")
                    subcol.prop(ssao_settings, "attenuation")
                    subcol.prop(ssao_settings, "samples")
                    subcol.prop(ssao_settings, "color")
 
        # -------------------- #          
        #   IMAGE THUMBNAIL    #
        # -------------------- #
 
        elif AM.render_type == 'image':
            row = box.row(align=True)
            row.prop(AM, "image_type", text=" ", expand=True)
            if AM.image_type == 'disk':
                box.label("Choose your thumbnail")
                box.prop(AM, "custom_thumbnail_path", text="")
            else:
                box.prop_search(AM, "render_name", bpy.data, "images", text="") 
 
        row = box.row(align=True)
        if len(obj_list) == 1:
            if (asset_name not in thumb_list or AM.replace_rename == 'replace') and (AM.render_type in ['opengl', 'render'] or AM.render_type == 'image' and (AM.image_type == 'disk' and AM.custom_thumbnail_path or AM.image_type == 'rendered' and AM.render_name)):
                row.operator("object.add_asset_in_library", text="OK", icon='FILE_TICK') 
        else:
            if AM.group_name and (asset_name not in thumb_list or AM.replace_rename == 'replace') and (AM.render_type in ['opengl', 'render'] or AM.render_type == 'image' and (AM.image_type == 'disk' and AM.custom_thumbnail_path or AM.image_type == 'rendered' and AM.render_name)):
 
                row.operator("object.add_asset_in_library", text="OK", icon='FILE_TICK') 
        row.operator("object.cancel_panel_choise", text="Cancel", icon='X')
    
    else:
        box.label("\" {} \" already exist".format(asset_name), icon='ERROR')
        box.separator()
        row = box.row(align=True)
        row.prop(AM, "replace_rename", text=" ", expand=True)
        if AM.replace_rename == 'rename':
            if len(obj_list) >= 2:
                box.prop(AM, "group_name", text="")
            else:
                ob = context.object
                box.prop(ob, "name", text="")
            row = box.row()
            row.operator("object.cancel_panel_choise", text="Cancel", icon='X')
            
# -----------------------------------------------------------------------------
#    MATERIALS ADDING OPTIONS PANEL
# -----------------------------------------------------------------------------    
 
def materials_adding_panel(self, context):
    """ Sub panel for the adding materials """
    
    AM = context.window_manager.asset_m
    layout = self.layout
    box = layout.box()
    view = context.space_data
    thumbnails_path = get_directory('icons')
    library_path = get_library_path()
    extentions = (".jpg", ".jpeg", ".png")
    thumb = [thumb.rsplit(".", 1)[0] for thumb in listdir(thumbnails_path) if thumb.endswith(extentions)]
    if AM.as_mat_scene:
        thumb_list = thumb + ["AM_Cloth", "AM_Sphere"]
    else:   
        thumb_list = thumb

    cam_is_valid = False
    obj_is_valid = False
    
    
    if not AM.as_mat_scene and not bpy.context.object:
        box.prop(AM, "as_mat_scene", text = "Save as material scene")
        box.label("No active_object in the scene", icon='ERROR')
        box.operator("object.cancel_panel_choise", text="Cancel", icon='X')
     
    elif not AM.as_mat_scene and not bpy.context.active_object.active_material:
        box.prop(AM, "as_mat_scene", text = "Save as material scene")
        box.label("The object have no material", icon='ERROR')
        box.operator("object.cancel_panel_choise", text="Cancel", icon='X')
    
    else:
        if AM.as_mat_scene and not isdir(join(library_path, 'materials', "Render Scenes")):
            box.operator("object.create_rder_scn_lib", text = "Create render scene library", icon = 'FILESEL')
            box.operator("object.cancel_panel_choise", text="Cancel", icon='X')
        
        else:
   
            if AM.as_mat_scene:
                asset_name = AM.scene_name
            else:
                active_mat = context.active_object.active_material
                asset_name = active_mat.name
                
            if len(bpy.context.active_object.material_slots) == 1:
                AM.multi_materials = False
                
            if AM.as_mat_scene and (not asset_name in thumb_list or asset_name in thumb_list and AM.replace_rename == 'replace') or\
               not AM.as_mat_scene and (AM.multi_materials and get_valid_materials() or not AM.multi_materials and asset_name not in thumb_list or asset_name in thumb_list and AM.replace_rename == 'replace'):  
                if not AM.multi_materials:
                    if asset_name in thumb_list and AM.replace_rename == 'replace':
                        box.label("\" {} \" already exist".format(asset_name), icon='ERROR')
                        box.separator()
                        if len(bpy.context.active_object.material_slots) >= 2 and AM.replace_rename == 'rename':
                            box.prop(AM, "multi_materials", text = "All materials")
                        row = box.row(align=True)
                        row.prop(AM, "replace_rename", text=" ", expand=True)
                        if AM.replace_rename == 'rename':
                            if AM.as_mat_scene:
                                box.prop(AM, "scene_name", text = "")
                            else:
                                box.prop(AM, "rename_mat", text="")
     
                box.prop(AM, "as_mat_scene", text = "Save as material scene")
                if not AM.as_mat_scene and len(bpy.context.active_object.material_slots) >= 2:
                    if len(get_valid_materials()) != len(bpy.context.active_object.material_slots) and AM.multi_materials:
                        box.label("Some materials wont be added", icon = 'ERROR')
                        box.label("     because there already exist")
                    row = box.row()
                    row.prop(AM, "multi_materials", text = "All materials")
                if AM.as_mat_scene:
                    row = box.row(align = True)
                    row.label("Scene name:")
                    row.prop(AM, "scene_name", text = "")
                     
                row = box.row(align = True)
                row.prop(AM, "render_type", text = " ", expand = True)
                row = box.row()
                row.label("Thumbnail extention:")
                row = box.row(align = True)
                row.prop(AM, "thumb_ext", expand = True)
                
                if AM.as_mat_scene:
                    for obj in context.scene.objects:
                        if obj.type == 'CAMERA':
                            cam_is_valid = True
                    
                    if len([obj for obj in context.selected_objects if obj.type != 'CAMERA' and bpy.context.active_object == obj]) == 1:
                        obj_is_valid = True
                        
                    row = box.row()
                    row.label("Selected object rendering", icon = 'FILE_TICK' if obj_is_valid else 'CANCEL')
                    row = box.row()
                    row.label("Camera in the scene", icon = 'FILE_TICK' if cam_is_valid else 'CANCEL')
                    if not cam_is_valid:
                        row = box.row()
                        row.operator("object.camera_add", text = "Add camera", icon = 'OUTLINER_OB_CAMERA')
                
                if not AM.as_mat_scene:
                    # --------------------- #          
                    #   RENDER THUMBNAIL    #
                    # --------------------- #
                    
                    if AM.render_type == 'render':
                        row = box.row(align = True)
                        row.label("Thumbnail:")
                        row.prop(AM, "mat_thumb_type", text = "")
                    
                # --------------------- #          
                #   OPENGL THUMBNAIL    #
                # --------------------- #
         
                if AM.render_type == 'opengl':
                    row = box.row(align=True)
                    row.operator("object.setup_ogl_render", text="Setup OGL render" if not "AM_OGL_Camera" in [obj.name for obj in context.scene.objects] else "View camera", icon='ZOOMIN')
                    row.operator("object.remove_ogl_render", text="", icon='ZOOMOUT')
                    row = layout.column()
                    row = box.row(align=True) 
                    row.label("Background:")
                    row.prop(AM, "background_alpha", text="")
                    row = box.row(align=True)
                    row.prop(view, "show_only_render")

                # -------------------- #          
                #   IMAGE THUMBNAIL    #
                # -------------------- #
         
                elif AM.render_type == 'image':
                    row = box.row(align=True)
                    row.prop(AM, "image_type", text=" ", expand=True)
                    if AM.image_type == 'disk':
                        box.label("Choose your thumbnail")
                        box.prop(AM, "custom_thumbnail_path", text="")
                    else:
                        box.prop_search(AM, "render_name", bpy.data, "images", text="") 
         
                row = box.row(align=True)
                if (AM.as_mat_scene and AM.scene_name and cam_is_valid and obj_is_valid or not AM.as_mat_scene) and (AM.render_type == 'render' or (asset_name  not in thumb_list or AM.replace_rename == 'replace') and AM.render_type == 'opengl' or AM.render_type == 'image' and (AM.image_type == 'disk' and AM.custom_thumbnail_path or AM.image_type == 'rendered' and AM.render_name)):
                    if AM.as_mat_scene:
                        row.operator("object.add_scene_in_library", text="OK", icon='FILE_TICK')
                    else:
                        row.operator("object.add_material_in_library", text="OK", icon='FILE_TICK')
                row.operator("object.cancel_panel_choise", text="Cancel", icon='X')
     
            else:
                if AM.multi_materials and not get_valid_materials():
                    box.label("All materials already exist".format(asset_name), icon='ERROR')
                    box.separator()
                    if len(bpy.context.active_object.material_slots) >= 2:
                        box.prop(AM, "multi_materials", text = "All materials")
                    
                else:
                    box.label("\" {} \" already exist".format(asset_name), icon='ERROR')
                    box.separator()
                    if len(bpy.context.active_object.material_slots) >= 2:
                        box.prop(AM, "multi_materials", text = "All materials")
                    else:
                        AM.multi_materials = False
                    row = box.row(align=True)
                    row.prop(AM, "replace_rename", text=" ", expand=True)
                    if AM.replace_rename == 'rename':
                        if AM.as_mat_scene:
                            box.prop(AM, "scene_name", text = "")
                        else:
                            box.prop(AM, "rename_mat", text="")
                        
                row = box.row()
                row.operator("object.cancel_panel_choise", text="Cancel", icon='X')

# -----------------------------------------------------------------------------
#    SCENES ADDING OPTIONS PANEL
# -----------------------------------------------------------------------------
 
def scene_adding_panel(self, context):
    """ Sub panel for the adding scenes """
    
    AM = context.window_manager.asset_m
    layout = self.layout
    box = layout.box()
    view = context.space_data
    fx_settings = view.fx_settings
    ssao_settings = fx_settings.ssao
    thumbnails_path = get_directory('icons')
    extentions = (".jpg", ".jpeg", ".png")
    thumb_list = [thumb.rsplit(".", 1)[0] for thumb in listdir(thumbnails_path) if thumb.endswith(extentions)]
    
    if AM.scene_name not in thumb_list or AM.scene_name in thumb_list and AM.replace_rename == 'replace':
        if AM.scene_name in thumb_list and AM.replace_rename == 'replace':
            box.label("\" {} \" already exist".format(AM.scene_name), icon='ERROR')
            box.separator()
            row = box.row(align=True)
            row.prop(AM, "replace_rename", text=" ", expand=True)
            if AM.replace_rename == 'rename':
                box.prop(AM, "scene_name", text="")
        
        row = box.row(align = True)
        row.label("Scene name:")
        row.prop(AM, "scene_name", text = "")
        row = box.row(align = True)
        row.prop(AM, "render_type", text = " ", expand = True)
        row = box.row()
        row.label("Thumbnail extention:")
        row = box.row(align = True)
        row.prop(AM, "thumb_ext", expand = True)

        # --------------------- #          
        #   OPENGL THUMBNAIL    #
        # --------------------- #
 
        if AM.render_type == 'opengl':
            row = box.row(align=True)
            row.operator("object.setup_ogl_render", text="Setup OGL render" if not "AM_OGL_Camera" in [obj.name for obj in context.scene.objects] else "View camera", icon='ZOOMIN')
            row.operator("object.remove_ogl_render", text="", icon='ZOOMOUT')
            row = layout.column()
            row = box.row(align=True) 
            row.label("Background:")
            row.prop(AM, "background_alpha", text="")
            row = box.row(align=True)
            row.prop(view, "show_only_render")
            row = box.row(align=True)
            row.prop(view, "use_matcap")
            if view.use_matcap :
                row.prop(AM, "matcap_options", text="", icon='TRIA_UP' if AM.matcap_options else 'TRIA_DOWN')    
                if AM.matcap_options:
                    row = box.row(align=True)
                    row.template_icon_view(view, "matcap_icon")
            row = box.row(align=True)
            row.prop(fx_settings, "use_ssao", text="Ambient Occlusion")
            if fx_settings.use_ssao:
                row.prop(AM, "ao_options", text="", icon='TRIA_UP' if AM.ao_options else 'TRIA_DOWN')    
                if AM.ao_options:
                    subcol = box.column(align=True)
                    subcol.prop(ssao_settings, "factor")
                    subcol.prop(ssao_settings, "distance_max")
                    subcol.prop(ssao_settings, "attenuation")
                    subcol.prop(ssao_settings, "samples")
                    subcol.prop(ssao_settings, "color")
 
        # -------------------- #          
        #   IMAGE THUMBNAIL    #
        # -------------------- #
 
        elif AM.render_type == 'image':
            row = box.row(align=True)
            row.prop(AM, "image_type", text=" ", expand=True)
            if AM.image_type == 'disk':
                box.label("Choose your thumbnail")
                box.prop(AM, "custom_thumbnail_path", text="")
            else:
                box.prop_search(AM, "render_name", bpy.data, "images", text="") 
 
        row = box.row(align=True)
        
        if AM.scene_name and ((AM.scene_name not in thumb_list or AM.replace_rename == 'replace') and AM.render_type == 'opengl' or AM.render_type == 'image' and (AM.image_type == 'disk' and AM.custom_thumbnail_path or AM.image_type == 'rendered' and AM.render_name)):
 
            row.operator("object.add_scene_in_library", text="OK", icon='FILE_TICK') 
        row.operator("object.cancel_panel_choise", text="Cancel", icon='X')
 
    else:
        box.label("\" {} \" already exist".format(AM.scene_name), icon='ERROR')
        box.separator()
        row = box.row(align=True)
        row.prop(AM, "replace_rename", text=" ", expand=True)
        if AM.replace_rename == 'rename':
            box.prop(AM, "scene_name", text="")
            row = box.row()
            row.operator("object.cancel_panel_choise", text="Cancel", icon='X')

# -----------------------------------------------------------------------------
#    HDRI ADDING OPTIONS PANEL
# -----------------------------------------------------------------------------
 
def hdri_adding_panel(self, context):
    """ Sub panel for the adding HDRI """
    
    AM = context.window_manager.asset_m
    layout = self.layout
    
    box = layout.box()
    row = box.row()
    row.prop(AM,  "existing_thumb", text = "Use existing Thumbnails")
    
    row = box.row()
    row.label("Thumbnail extention:")
    row = box.row(align = True)
    row.prop(AM, "thumb_ext", expand = True)
    
    row = box.row(align = True)
        
    row.operator("wm.ibl_importer", text="OK", icon='FILE_TICK')
    row.operator("object.cancel_panel_choise", text="Cancel", icon='X')
                    
# -----------------------------------------------------------------------------
#    IBL OPTIONS PANEL
# -----------------------------------------------------------------------------
 
def ibl_options_panel(self, context):
    """ Sub panel for the ibl options """
    
    AM = context.window_manager.asset_m
    node_group = bpy.context.scene.world.node_tree.nodes
    layout = self.layout
    
    box = layout.box()
    row = box.row()
    row.alignment = 'CENTER'
    row.label("IMAGE")
    row = box.row(align = True)
    row.label("Rotation:")
    col = row.column()
    col.prop(node_group["Mapping"], "rotation", text = "")
    row = box.row(align = True)
    row.label("Projection:")
    row.prop(AM, "projection", text = "")
    row = box.row(align = True)
    row.label("Blur:")
    row.prop(node_group["ImageBlur"].inputs[1], "default_value", text = "")
    row = box.row(align = True)
    row.label("Visible:")
    row.prop(bpy.context.scene.world.cycles_visibility, "camera")
    row = box.row(align = True)
    row.label("Transparent:")
    row.prop(bpy.context.scene.cycles, "film_transparent")
    
    
    
    box = layout.box()
    row = box.row(align = True)
    row.label("Gamma:")
    row.prop(node_group["AM_IBL_Tool"].inputs[0], "default_value", text = "")
    
    box = layout.box()
    row = box.row()
    row.alignment = 'CENTER'
    row.label("LIGHT")
    row = box.row(align = True)
    row.label("Strength:")
    row.prop(node_group["AM_IBL_Tool"].inputs[2], "default_value", text = "")
    row = box.row(align = True)
    row.label("Saturation:")
    row.prop(node_group["AM_IBL_Tool"].inputs[3], "default_value", text = "")
    row = box.row(align = True)
    row.label("Hue:")
    row.prop(node_group["AM_IBL_Tool"].inputs[4], "default_value", text = "")
    row = box.row(align = True)
    row.label("Mix Hue:")
    row.prop(node_group["AM_IBL_Tool"].inputs[5], "default_value", text = "")
    
    box = layout.box()
    row = box.row()
    row.alignment = 'CENTER'
    row.label("GLOSSY")
    row = box.row(align = True)
    row.label("Strength:")
    row.prop(node_group["AM_IBL_Tool"].inputs[7], "default_value", text = "")
    row = box.row(align = True)
    row.label("Saturation:")
    row.prop(node_group["AM_IBL_Tool"].inputs[8], "default_value", text = "")
    row = box.row(align = True)
    row.label("Hue:")
    row.prop(node_group["AM_IBL_Tool"].inputs[9], "default_value", text = "")
    row = box.row(align = True)
    row.label("Mix Hue:")
    row.prop(node_group["AM_IBL_Tool"].inputs[10], "default_value", text = "")
    
    layout.operator("wm.save_ibl_settings", text = "Save settings", icon = 'FILE_TICK')        
    
# -----------------------------------------------------------------------------
#    DRAW TOOLS PANEL
# -----------------------------------------------------------------------------
           
class VIEW3D_PT_tools_AM_Tools(bpy.types.Panel):
    bl_label = "Asset Management"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
 
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        AM = wm.asset_m
        library_path = get_library_path()
        addon_prefs = get_addon_preferences()
        thumbnails_path = get_directory('icons')
        favourites_path = get_directory("Favorites")
        
        
        if library_path:
            
            icons = load_icons()
            rename = icons.get("rename_asset")
            no_rename = icons.get("no_rename_asset")
            favourites = icons.get("favorites_asset")
            no_favourites = icons.get("no_favorites_asset")
            h_ops = icons.get("hardops_asset")
            
            row = layout.row(align = True)
            row.prop(AM, "library_type", text=" ", expand = True)
            #layout.operator("my_operator.debug_operator", text = "debug")
            
            if not AM.library_type in listdir(library_path):
                layout.operator("object.create_lib_type_folder", text = "Create {} folder".format(AM.library_type)).lib_type = AM.library_type
            
            # -----------------------------------------------------------------------------
            #    LIBRARIES
            # -----------------------------------------------------------------------------
            
            else:
                row = layout.row(align = True)
                row.prop(AM, "libraries")
                row.prop(AM, "show_prefs_lib", text = "", icon = 'TRIA_UP' if AM.show_prefs_lib else 'SCRIPTWIN')
                
                if AM.show_prefs_lib:
                    box = layout.box()
                    row = box.row(align = True)
                    row.operator("object.add_asset_library", text = "Add")
                    row.operator("object.remove_asset_m_library", text = "Remove")
                    row.prop(AM, "rename_library", text = "", icon_value = rename.icon_id if AM.rename_library else no_rename.icon_id )
                    if AM.rename_library:
                        row = box.row()
                        if AM.libraries == "Render Scenes":
                            row.label("This library don't", icon = 'CANCEL')
                            row = box.row()
                            row.label("have to change name")
                        else:
                            row.prop(AM, "change_library_name")
                            
                            if AM.change_library_name:
                                if AM.change_library_name in [lib for lib in listdir(join(library_path, AM.library_type)) if isdir(join(library_path, AM.library_type))]:
                                    row = layout.row()
                                    row.label("\"{}\" already exist".format(AM.change_library_name), icon = 'ERROR')
                                
                                else:
                                    row.operator("object.asset_m_rename_library", text = "", icon = 'FILE_TICK')
                
                # -----------------------------------------------------------------------------
                #    CATEGORIES
                # -----------------------------------------------------------------------------
                row = layout.row(align = True)
                row.prop(AM, "categories")
                row.prop(AM, "show_prefs_cat", text = "", icon = 'TRIA_UP' if AM.show_prefs_cat else 'SCRIPTWIN')
                
                if AM.show_prefs_cat:
                    box = layout.box()
                    row = box.row(align = True)
                    row.operator("object.add_asset_category", text = "Add")
                    row.operator("object.remove_asset_m_category", text = "Remove")
                    row.prop(AM, "rename_category", text = "", icon_value = rename.icon_id if AM.rename_category else no_rename.icon_id )
                    if AM.rename_category:
                        row = box.row()
                        row.prop(AM, "change_category_name")
                        
                        if AM.change_category_name:
                            if AM.change_category_name in [cat for cat in listdir(join(library_path, AM.library_type, AM.libraries)) if isdir(join(library_path, AM.library_type, AM.libraries))]:
                                row = layout.row()
                                row.label("\"{}\" already exist".format(AM.change_category_name), icon = 'ERROR')
                            
                            else:
                                row.operator("object.asset_m_rename_category", text = "", icon = 'FILE_TICK')

                # -----------------------------------------------------------------------------
                #   ADDING MENU
                # -----------------------------------------------------------------------------
                if AM.adding_options:
                    if AM.library_type == 'assets':
                        asset_adding_panel(self, context)
                    
                    elif AM.library_type == 'materials':
                        materials_adding_panel(self, context)
                    
                    elif AM.library_type == 'scenes':
                        scene_adding_panel(self, context)
                    
                    elif AM.library_type == 'hdri':
                        hdri_adding_panel(self, context)
                    
                
                # -----------------------------------------------------------------------------
                #   DRAW PANEL
                # -----------------------------------------------------------------------------
                else:
                    if AM.library_type in ["assets", "materials"]:
                        row = layout.row(align = True)
                        row.prop(AM, "import_choise", expand = True)
                        row.operator("object.edit_asset", text = "", icon = 'LOAD_FACTORY')
                    
                    elif AM.library_type == "scenes":
                        layout.operator("object.edit_asset", text = "Edit Scene", icon = 'LOAD_FACTORY')
                    
                    # Show only Favourites sheck box
                    if len(listdir(favourites_path)):
                        row = layout.row()
                        row.prop(AM, "favourites_enabled", text = "Show Only Favourites")
                    
                    # Asset Preview  
                    row = layout.row(align = True)
                    row.prop
                    row = layout.row()
                    col = row.column()
                    col.scale_y = 1.17
                    col.template_icon_view(wm, "AssetM_previews", show_labels = True if addon_prefs.show_labels else False)
                    col = row.column(align = True)
                    
                    # Add/Remove asset from the library
                    if AM.library_type in ['scenes', 'hdri'] or AM.library_type in ['assets', 'materials'] and context.selected_objects and not AM.render_running:
                        col.prop(AM, "adding_options", text = "", icon = 'ZOOMIN')
                    col.operator("object.remove_asset_from_lib", text = "", icon = 'ZOOMOUT')
                    
                    # Favourites
                    if len(listdir(favourites_path)):
                        if isfile(join(favourites_path, wm.AssetM_previews)):       
                            col.operator("object.remove_from_favourites", text="", icon_value=favourites.icon_id)
                        else:
                            col.operator("object.add_to_favourites", text="", icon_value=no_favourites.icon_id)   
                    else:
                        col.operator("object.add_to_favourites", text="", icon_value=no_favourites.icon_id)
                    
                    # Custom import
                    if AM.library_type in ['assets', 'scenes']:
                        col.prop(AM, "custom_data_import", icon = 'FILE_TEXT', icon_only=True)
                    
                    # Popup options
                    col.operator("view3d.properties_menu", text="", icon='SCRIPTWIN')
                    
                    # Without import
                    if AM.without_import:
                        col.prop(AM, "without_import", icon='LOCKED', icon_only=True)
                    else:
                        col.prop(AM, "without_import", icon='UNLOCKED', icon_only=True)
                    
                    # Tool options
                    if AM.library_type != 'scenes':
                        col.prop(AM, "display_tools", text = "", icon = 'TRIA_UP' if AM.display_tools else 'MODIFIER')
                    
                    # Render Thumbnail 
                    if AM.asset_adding_enabled:
                        layout.label("Adding asset...", icon='RENDER_STILL')
                        layout.label("Please wait... ")
                        layout.operator("wm.console_toggle", text="Check/Hide Console")
                    
                    elif AM.render_running:
                        if AM.material_rendering:
                            layout.label("Rendering: %s" % (AM.material_rendering[0]), icon='RENDER_STILL')
                        else:
                            layout.label("Thumbnail rendering", icon='RENDER_STILL')
                        layout.label("Please wait... ")
                        layout.operator("wm.console_toggle", text="Check/Hide Console")
                    
                    else: 
                        if settings["file_to_edit"] != "" and settings["file_to_edit"] == bpy.data.filepath:
                            row = layout.row(align=True)
                            row.operator("wm.back_to_original", text = "Save", icon = 'SAVE_COPY')
                            row.operator("wm.cancel_changes", text = "Cancel", icon = 'X')
                            if AM.display_tools:
                                box = layout.box()
                                if AM.library_type == 'assets':
                                    box.operator("object.rename_objects", text = "Correct Name", icon = 'SAVE_COPY')
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
                                    box.separator()
                                    box = layout.box()
                                    box.operator("object.asset_m_add_to_selection", text = "Asset to selection", icon = 'MOD_MULTIRES')
                                    row = box.row(align = True)
                                    row.operator("object.asset_m_link", text = "Link", icon = 'CONSTRAINT')
                                    row.operator("object.asset_m_unlink", text = "Unlink", icon = 'UNLINKED')
                                    row = box.row()
                                    row.alignment = 'CENTER'
                                    row.label("Prepare asset")
                                    row = box.row(align = True)
                                    row.operator("object.prepare_asset", text = "AM", icon = 'OBJECT_DATA').type = 'AM'
                                    row.operator("object.prepare_asset", text = "H_Ops", icon_value = h_ops.icon_id).type = 'H_Ops'
                                elif AM.library_type == 'materials':
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')

                        else:   
                            # Asset name
                            if addon_prefs.show_name_assets:
                                row = layout.row(align = True)
                                row.label("Name :")
                                sub = row.row()
                                sub.scale_x = 2.0
                                sub.label(context.window_manager.AssetM_previews.rsplit(".", 1)[0])
                            
                            if AM.library_type in ['assets', 'scenes'] and AM.custom_data_import:
                                layout.prop(AM, "datablock", text = "") 
                            
                            # Replace
                            if context.object is not None and context.object.mode == 'OBJECT' and AM.library_type == 'assets' and context.selected_objects:
                                row = layout.row(align=True)
                                row.prop(AM, "replace_asset", text="Replace Asset")
                                if AM.replace_asset:
                                    row.prop(AM, "replace_multi", text="Multi")
                                else:
                                    AM.replace_multi = False
     
                            else:
                                AM.replace_asset=False
                            
                            
                            row = layout.row(align=True)
                            row.scale_y = 1.1
                            row.scale_x = 1.5
                            row.operator("object.next_asset", text="", icon='TRIA_LEFT').selection = -1
                            row.scale_x = 1
                            if AM.library_type == 'scenes' and not AM.custom_data_import:
                                row.operator("wm.open_active_preview", text = "Click to open")
                            elif AM.library_type in ['assets', 'scenes'] and AM.custom_data_import:
                                row.operator("wm.assetm_custom_browser", text = "Custom import")
                            else:
                                row.operator("object.import_active_preview", text="Replace Asset" if AM.replace_asset else "Click to import")
                            row.scale_x = 1.5
                            row.operator("object.next_asset", text="", icon='TRIA_RIGHT').selection = 1
                            
                            if AM.display_tools:
                                box = layout.box()
                                if AM.library_type == 'hdri':
                                    if "AM_IBL_WORLD" in bpy.data.worlds:
                                        ibl_options_panel(self, context)
                                    else:
                                        box.label("No setup IBL", icon = 'ERROR')
                                elif AM.library_type == 'assets':
                                    box.operator("object.rename_objects", text = "Correct Name", icon = 'SAVE_COPY')
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
                                    box.separator()
                                    box = layout.box()
                                    box.operator("object.asset_m_add_to_selection", text = "Asset to selection", icon = 'MOD_MULTIRES')
                                    row = box.row(align = True)
                                    row.operator("object.asset_m_link", text = "Link", icon = 'CONSTRAINT')
                                    row.operator("object.asset_m_unlink", text = "Unlink", icon = 'UNLINKED')
                                    row = box.row()
                                    row.alignment = 'CENTER'
                                    row.label("Prepare asset")
                                    row = box.row(align = True)
                                    row.operator("object.prepare_asset", text = "AM", icon = 'OBJECT_DATA').type = 'AM'
                                    row.operator("object.prepare_asset", text = "H_Ops", icon_value = h_ops.icon_id).type = 'H_Ops'
                                elif AM.library_type == 'materials':
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
                            
                            # Link
                            if AM.library_type == 'assets' and AM.import_choise == 'link':
                                groups = get_groups(context.window_manager.AssetM_previews.rsplit(".", 1)[0])
                                if groups[0] != "empty":
                                    box = layout.box()
                                    box.label("Group to link")
                                    for group in groups:
                                        box.operator("object.import_active_preview", text=group, icon='LINK_BLEND').group_name = group
                                        
                                else:
                                    box = layout.box()
                                    box.label("Group to link")
                                    box.label("There's no group to link")
                                    box.label("Use custom import to link objects")
                            
                                #Script
                                scripts = get_scripts(context.window_manager.AssetM_previews.rsplit(".", 1)[0])
                                if scripts[0] != "empty":
                                    box = layout.box()
                                    box.label("Script:")
                                    for txt in scripts:
                                        box.operator("text.import_script", text=txt).script = txt
           
        
        else:
            layout.label("Define the library path", icon='ERROR')
            layout.label("in the addon preferences please.")
            layout.operator("screen.userpref_show", icon='PREFERENCES')



# -----------------------------------------------------------------------------
#    DRAW UI PANEL
# -----------------------------------------------------------------------------
 
class VIEW3D_PT_view_3d_AM_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Asset Management"
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        AM = wm.asset_m
        library_path = get_library_path()
        addon_prefs = get_addon_preferences()
        thumbnails_path = get_directory('icons')
        favourites_path = get_directory("Favorites")
     
     
        if library_path:
     
            icons = load_icons()
            rename = icons.get("rename_asset")
            no_rename = icons.get("no_rename_asset")
            favourites = icons.get("favorites_asset")
            no_favourites = icons.get("no_favorites_asset")
            h_ops = icons.get("hardops_asset")
     
            row = layout.row(align = True)
            row.prop(AM, "library_type", text=" ", expand = True)
            #layout.operator("my_operator.debug_operator", text = "debug")
     
            if not AM.library_type in listdir(library_path):
                layout.operator("object.create_lib_type_folder", text = "Create {} folder".format(AM.library_type)).lib_type = AM.library_type
     
            # -----------------------------------------------------------------------------
            #    LIBRARIES
            # -----------------------------------------------------------------------------
     
            else:
                row = layout.row(align = True)
                row.prop(AM, "libraries")
                row.prop(AM, "show_prefs_lib", text = "", icon = 'TRIA_UP' if AM.show_prefs_lib else 'SCRIPTWIN')
     
                if AM.show_prefs_lib:
                    box = layout.box()
                    row = box.row(align = True)
                    row.operator("object.add_asset_library", text = "Add")
                    row.operator("object.remove_asset_m_library", text = "Remove")
                    row.prop(AM, "rename_library", text = "", icon_value = rename.icon_id if AM.rename_library else no_rename.icon_id )
                    if AM.rename_library:
                        row = box.row()
                        if AM.libraries == "Render Scenes":
                            row.label("This library don't", icon = 'CANCEL')
                            row = box.row()
                            row.label("have to change name")
                        else:
                            row.prop(AM, "change_library_name")
     
                            if AM.change_library_name:
                                if AM.change_library_name in [lib for lib in listdir(join(library_path, AM.library_type)) if isdir(join(library_path, AM.library_type))]:
                                    row = layout.row()
                                    row.label("\"{}\" already exist".format(AM.change_library_name), icon = 'ERROR')
     
                                else:
                                    row.operator("object.asset_m_rename_library", text = "", icon = 'FILE_TICK')
     
                # -----------------------------------------------------------------------------
                #    CATEGORIES
                # -----------------------------------------------------------------------------
                row = layout.row(align = True)
                row.prop(AM, "categories")
                row.prop(AM, "show_prefs_cat", text = "", icon = 'TRIA_UP' if AM.show_prefs_cat else 'SCRIPTWIN')
     
                if AM.show_prefs_cat:
                    box = layout.box()
                    row = box.row(align = True)
                    row.operator("object.add_asset_category", text = "Add")
                    row.operator("object.remove_asset_m_category", text = "Remove")
                    row.prop(AM, "rename_category", text = "", icon_value = rename.icon_id if AM.rename_category else no_rename.icon_id )
                    if AM.rename_category:
                        row = box.row()
                        row.prop(AM, "change_category_name")
     
                        if AM.change_category_name:
                            if AM.change_category_name in [cat for cat in listdir(join(library_path, AM.library_type, AM.libraries)) if isdir(join(library_path, AM.library_type, AM.libraries))]:
                                row = layout.row()
                                row.label("\"{}\" already exist".format(AM.change_category_name), icon = 'ERROR')
     
                            else:
                                row.operator("object.asset_m_rename_category", text = "", icon = 'FILE_TICK')
     
                # -----------------------------------------------------------------------------
                #   ADDING MENU
                # -----------------------------------------------------------------------------
                if AM.adding_options:
                    if AM.library_type == 'assets':
                        asset_adding_panel(self, context)
     
                    elif AM.library_type == 'materials':
                        materials_adding_panel(self, context)
     
                    elif AM.library_type == 'scenes':
                        scene_adding_panel(self, context)
     
                    elif AM.library_type == 'hdri':
                        hdri_adding_panel(self, context)
     
     
                # -----------------------------------------------------------------------------
                #   DRAW PANEL
                # -----------------------------------------------------------------------------
                else:
                    if AM.library_type in ["assets", "materials"]:
                        row = layout.row(align = True)
                        row.prop(AM, "import_choise", expand = True)
                        row.operator("object.edit_asset", text = "", icon = 'LOAD_FACTORY')
     
                    elif AM.library_type == "scenes":
                        layout.operator("object.edit_asset", text = "Edit Scene", icon = 'LOAD_FACTORY')
     
                    # Show only Favourites sheck box
                    if len(listdir(favourites_path)):
                        row = layout.row()
                        row.prop(AM, "favourites_enabled", text = "Show Only Favourites")
     
                    # Asset Preview  
                    row = layout.row(align = True)
                    row.prop
                    row = layout.row()
                    col = row.column()
                    col.scale_y = 1.17
                    col.template_icon_view(wm, "AssetM_previews", show_labels = True if addon_prefs.show_labels else False)
                    col = row.column(align = True)
     
                    # Add/Remove asset from the library
                    if AM.library_type in ['scenes', 'hdri'] or AM.library_type in ['assets', 'materials'] and context.selected_objects and not AM.render_running:
                        col.prop(AM, "adding_options", text = "", icon = 'ZOOMIN')
                    col.operator("object.remove_asset_from_lib", text = "", icon = 'ZOOMOUT')
     
                    # Favourites
                    if len(listdir(favourites_path)):
                        if isfile(join(favourites_path, wm.AssetM_previews)):       
                            col.operator("object.remove_from_favourites", text="", icon_value=favourites.icon_id)
                        else:
                            col.operator("object.add_to_favourites", text="", icon_value=no_favourites.icon_id)   
                    else:
                        col.operator("object.add_to_favourites", text="", icon_value=no_favourites.icon_id)
     
                    # Custom import
                    if AM.library_type in ['assets', 'scenes']:
                        col.prop(AM, "custom_data_import", icon = 'FILE_TEXT', icon_only=True)
     
                    # Popup options
                    col.operator("view3d.properties_menu", text="", icon='SCRIPTWIN')
     
                    # Without import
                    if AM.without_import:
                        col.prop(AM, "without_import", icon='LOCKED', icon_only=True)
                    else:
                        col.prop(AM, "without_import", icon='UNLOCKED', icon_only=True)
     
                    # Tool options
                    if AM.library_type != 'scenes':
                        col.prop(AM, "display_tools", text = "", icon = 'TRIA_UP' if AM.display_tools else 'MODIFIER')
     
                    # Render Thumbnail 
                    if AM.asset_adding_enabled:
                        layout.label("Adding asset...", icon='RENDER_STILL')
                        layout.label("Please wait... ")
                        layout.operator("wm.console_toggle", text="Check/Hide Console")
     
                    elif AM.render_running:
                        if AM.material_rendering:
                            layout.label("Rendering: %s" % (AM.material_rendering[0]), icon='RENDER_STILL')
                        else:
                            layout.label("Thumbnail rendering", icon='RENDER_STILL')
                        layout.label("Please wait... ")
                        layout.operator("wm.console_toggle", text="Check/Hide Console")
     
                    else: 
                        if settings["file_to_edit"] != "" and settings["file_to_edit"] == bpy.data.filepath:
                            row = layout.row(align=True)
                            row.operator("wm.back_to_original", text = "Save", icon = 'SAVE_COPY')
                            row.operator("wm.cancel_changes", text = "Cancel", icon = 'X')
                            if AM.display_tools:
                                box = layout.box()
                                if AM.library_type == 'assets':
                                    box.operator("object.rename_objects", text = "Correct Name", icon = 'SAVE_COPY')
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
                                    box.separator()
                                    box = layout.box()
                                    box.operator("object.asset_m_add_to_selection", text = "Asset to selection", icon = 'MOD_MULTIRES')
                                    row = box.row(align = True)
                                    row.operator("object.asset_m_link", text = "Link", icon = 'CONSTRAINT')
                                    row.operator("object.asset_m_unlink", text = "Unlink", icon = 'UNLINKED')
                                    row = box.row()
                                    row.alignment = 'CENTER'
                                    row.label("Prepare asset")
                                    row = box.row(align = True)
                                    row.operator("object.prepare_asset", text = "AM", icon = 'OBJECT_DATA').type = 'AM'
                                    row.operator("object.prepare_asset", text = "H_Ops", icon_value = h_ops.icon_id).type = 'H_Ops'
                                elif AM.library_type == 'materials':
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
     
                        else:   
                            # Asset name
                            if addon_prefs.show_name_assets:
                                row = layout.row(align = True)
                                row.label("Name :")
                                sub = row.row()
                                sub.scale_x = 2.0
                                sub.label(context.window_manager.AssetM_previews.rsplit(".", 1)[0])
     
                            if AM.library_type in ['assets', 'scenes'] and AM.custom_data_import:
                                layout.prop(AM, "datablock", text = "") 
     
                            # Replace
                            if context.object is not None and context.object.mode == 'OBJECT' and AM.library_type == 'assets' and context.selected_objects:
                                row = layout.row(align=True)
                                row.prop(AM, "replace_asset", text="Replace Asset")
                                if AM.replace_asset:
                                    row.prop(AM, "replace_multi", text="Multi")
                                else:
                                    AM.replace_multi = False
     
                            else:
                                AM.replace_asset=False
     
     
                            row = layout.row(align=True)
                            row.scale_y = 1.1
                            row.scale_x = 1.5
                            row.operator("object.next_asset", text="", icon='TRIA_LEFT').selection = -1
                            row.scale_x = 1
                            if AM.library_type == 'scenes' and not AM.custom_data_import:
                                row.operator("wm.open_active_preview", text = "Click to open")
                            elif AM.library_type in ['assets', 'scenes'] and AM.custom_data_import:
                                row.operator("wm.assetm_custom_browser", text = "Custom import")
                            else:
                                row.operator("object.import_active_preview", text="Replace Asset" if AM.replace_asset else "Click to import")
                            row.scale_x = 1.5
                            row.operator("object.next_asset", text="", icon='TRIA_RIGHT').selection = 1
     
                            if AM.display_tools:
                                box = layout.box()
                                if AM.library_type == 'hdri':
                                    if "AM_IBL_WORLD" in bpy.data.worlds:
                                        ibl_options_panel(self, context)
                                    else:
                                        box.label("No setup IBL", icon = 'ERROR')
                                elif AM.library_type == 'assets':
                                    box.operator("object.rename_objects", text = "Correct Name", icon = 'SAVE_COPY')
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
                                    box.separator()
                                    box = layout.box()
                                    box.operator("object.asset_m_add_to_selection", text = "Asset to selection", icon = 'MOD_MULTIRES')
                                    row = box.row(align = True)
                                    row.operator("object.asset_m_link", text = "Link", icon = 'CONSTRAINT')
                                    row.operator("object.asset_m_unlink", text = "Unlink", icon = 'UNLINKED')
                                    row = box.row()
                                    row.alignment = 'CENTER'
                                    row.label("Prepare asset")
                                    row = box.row(align = True)
                                    row.operator("object.prepare_asset", text = "AM", icon = 'OBJECT_DATA').type = 'AM'
                                    row.operator("object.prepare_asset", text = "H_Ops", icon_value = h_ops.icon_id).type = 'H_Ops'
                                elif AM.library_type == 'materials':
                                    box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                                    box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
     
                            # Link
                            if AM.library_type == 'assets' and AM.import_choise == 'link':
                                groups = get_groups(context.window_manager.AssetM_previews.rsplit(".", 1)[0])
                                if groups[0] != "empty":
                                    box = layout.box()
                                    box.label("Group to link")
                                    for group in groups:
                                        box.operator("object.import_active_preview", text=group, icon='LINK_BLEND').group_name = group
     
                                else:
                                    box = layout.box()
                                    box.label("Group to link")
                                    box.label("There's no group to link")
                                    box.label("Use custom import to link objects")
     
                                #Script
                                scripts = get_scripts(context.window_manager.AssetM_previews.rsplit(".", 1)[0])
                                if scripts[0] != "empty":
                                    box = layout.box()
                                    box.label("Script:")
                                    for txt in scripts:
                                        box.operator("text.import_script", text=txt).script = txt
     
     
        else:
            layout.label("Define the library path", icon='ERROR')
            layout.label("in the addon preferences please.")
            layout.operator("screen.userpref_show", icon='PREFERENCES')
                
                
# -----------------------------------------------------------------------------
#    DRAW POPUP PANEL
# -----------------------------------------------------------------------------
 
class WM_OT_am_popup(bpy.types.Operator):
    bl_idname = "view3d.asset_m_pop_up_preview"
    bl_label = "Asset preview"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.mode in ['OBJECT', 'EDIT_MESH']
    
    def execute(self, context):
        return {'FINISHED'}
   
    def check(self, context):
        return True
         
    def invoke(self, context, event):
        self.library_path = get_library_path()
        self.addon_prefs = get_addon_preferences()
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value*2.5, height=100)
   
    def draw(self, context):
        WM = context.window_manager
        AM = WM.asset_m
        thumbnails_path = get_directory('icons')
        favourites_path = get_directory("Favorites")
        
        icons = load_icons()
        favourites = icons.get("favorites_asset")
        no_favourites = icons.get("no_favorites_asset")
        h_ops = icons.get("hardops_asset")
        
        layout = self.layout
        row = layout.row(align = True)
        row.prop(AM, "library_type", text=" ", expand = True)
         
        if not AM.library_type in listdir(self.library_path):
            layout.operator("object.create_lib_type_folder", text = "Create {} folder".format(AM.library_type)).lib_type = AM.library_type
        row = layout.row(align = True)
        row.prop(AM, "libraries")
         
        row = layout.row(align = True)
        row.prop(AM, "categories")
        
        # Show only Favourites sheck box
        if len(listdir(favourites_path)):
            row = layout.row()
            row.prop(AM, "favourites_enabled", text = "Show Only Favourites")
         
        # Asset Preview  
        row = layout.row(align = True)
        row.prop
        row = layout.row()
        col = row.column()
        col.scale_y = 1.17
        col.template_icon_view(WM, "AssetM_previews", show_labels = True if self.addon_prefs.show_labels else False)
        col = row.column(align = True)
        # Favourites
        if len(listdir(favourites_path)):
            if isfile(join(favourites_path, WM.AssetM_previews)):       
                col.operator("object.remove_from_favourites", text="", icon_value=favourites.icon_id)
            else:
                col.operator("object.add_to_favourites", text="", icon_value=no_favourites.icon_id)   
        else:
            col.operator("object.add_to_favourites", text="", icon_value=no_favourites.icon_id)
         
        # Popup options
        col.operator("view3d.properties_menu", text="", icon='SCRIPTWIN')
         
        # Without import
        if AM.without_import:
            col.prop(AM, "without_import", icon='LOCKED', icon_only=True)
        else:
            col.prop(AM, "without_import", icon='UNLOCKED', icon_only=True)
        
        # Asset name
        if self.addon_prefs.show_name_assets:
            row = layout.row(align = True)
            row.label("Name :")
            sub = row.row()
            sub.scale_x = 2.0
            sub.label(WM.AssetM_previews.rsplit(".", 1)[0])
        
        # Tool options
        if AM.library_type in ['assets', 'hdri']:
            col.prop(AM, "display_tools", text = "", icon = 'TRIA_UP' if AM.display_tools else 'MODIFIER')
        
        # Replace
        if context.object is not None and context.object.mode == 'OBJECT' and AM.library_type == 'assets':
            row = layout.row(align=True)
            row.prop(AM, "replace_asset", text="Replace Asset")
            if AM.replace_asset:
                row.prop(AM, "replace_multi", text="Multi")
            else:
                AM.replace_multi = False
        else:
            AM.replace_asset=False
         
        row = layout.row(align=True)
        row.scale_y = 1.1
        row.scale_x = 1.5
        row.operator("object.next_asset", text="", icon='TRIA_LEFT').selection = -1
        row.scale_x = 1
        if AM.library_type == 'scenes':
            row.operator("wm.open_active_preview", text = "Click to open")
        else:
            row.operator("object.append_active_preview", text="Replace Asset" if AM.replace_asset else "Click to import")
        row.scale_x = 1.5
        row.operator("object.next_asset", text="", icon='TRIA_RIGHT').selection = 1
        
        if AM.display_tools:
            box = layout.box()
            if AM.library_type == 'hdri':
                if "AM_IBL_WORLD" in bpy.data.worlds:
                    ibl_options_panel(self, context)
                else:
                    box.label("No setup IBL", icon = 'ERROR')
            elif AM.library_type == 'assets':
                box.operator("object.rename_objects", text = "Correct Name", icon = 'SAVE_COPY')
                box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
                box.separator()
                box = layout.box()
                box.operator("object.asset_m_add_to_selection", text = "Asset to selection", icon = 'MOD_MULTIRES')
                row = box.row(align = True)
                row.operator("object.asset_m_link", text = "Link", icon = 'CONSTRAINT')
                row.operator("object.asset_m_unlink", text = "Unlink", icon = 'UNLINKED')
                row = box.row()
                row.alignment = 'CENTER'
                row.label("Prepare asset")
                row = box.row(align = True)
                row.operator("object.prepare_asset", text = "AM", icon = 'OBJECT_DATA').type = 'AM'
                row.operator("object.prepare_asset", text = "H_Ops", icon_value = h_ops.icon_id).type = 'H_Ops'
            elif AM.library_type == 'materials':
                box.operator("material.link_to_base_names", text="Materials to base name", icon = 'MATERIAL')
                box.operator("object.clean_unused_data", text="Clean unused datas", icon = 'MESH_DATA')
            