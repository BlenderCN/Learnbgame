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
import shutil
from os import rename, makedirs, listdir
from os.path import join, isdir
from bpy.types import Operator
from ..function_utils.get_path import (get_addon_path,
                                       get_library_path
                                       )
from ..function_utils.update import (library_type_updater,
                                     category_updater
                                     )


class CreatLibraryTypeFolder(Operator):
    """ Create the library type folder in your library """
    bl_idname = "object.create_lib_type_folder"
    bl_label = "Create library type Folder"

    lib_type = bpy.props.StringProperty()

    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
        addon_path = get_addon_path()
        empty_icon_path = join(addon_path, "icons", "EMPTY.png")
        
        # creating a asset type folder
        makedirs(join(library_path, self.lib_type))
        
        # creating a library folder in the asset type folder
        makedirs(join(library_path, self.lib_type, "My_library"))
         
        # creating a category folder in the My_library folder
        makedirs(join(library_path, self.lib_type, "My_library", "My_category"))
         
        # creating the "blends" or "IBL", "Favorites" and "icons" folder in the My_category folder
        folders = ["Favorites", "icons"]
        if AM.library_type == 'hdri':
            folders.append("IBL")
        else:
            folders.append("blends")
            
        for f in folders:
            makedirs(join(library_path, self.lib_type, "My_library", "My_category", f))
         
        # adding the thumbnails
        shutil.copy(empty_icon_path, join(library_path, self.lib_type, "My_library", "My_category", "icons", "EMPTY.png"))
         
        library_type_updater(self, context) #function called from "fonction_utils" module, update_utils.py
        return {"FINISHED"}

# -----------------------------------------------------------------------------
#    LIBRARY OPERATORS
# -----------------------------------------------------------------------------

class AddAssetLibrary(Operator):
    """ Add a new library in your Asset Management library"""
    bl_idname = "object.add_asset_library"
    bl_label = "Add Asset Library"
    
    def execute(self, context):
        AM = bpy.context.window_manager.asset_m
        addon_path = get_addon_path()
        empty_icon_path = join(addon_path, "icons", "EMPTY.png")
        library_type = AM.library_type
        
        # if the library name already exist or if there's no defined name, the operator will be call again 
        if AM.lib_name in self.libraries or not AM.lib_name:
            bpy.ops.object.add_asset_library('INVOKE_DEFAULT')
        
        else:
            # creating a library folder in the Assets folder
            makedirs(join(self.library_path, library_type, AM.lib_name))
             
            # creating a category folder in the My_library folder
            makedirs(join(self.library_path, library_type, AM.lib_name, "My_category"))
             
            # creating the "blends" or "IBL", "Favorites" and "icons" folder in the My_category folder
            folders = ["Favorites", "icons"]
            if AM.library_type == 'hdri':
                folders.append("IBL")
            else:
                folders.append("blends")
            
            for f in folders:
                makedirs(join(self.library_path, library_type, AM.lib_name, "My_category", f))
             
            # adding the thumbnails
            shutil.copy(empty_icon_path, join(self.library_path, library_type, AM.lib_name, "My_category", "icons", "EMPTY.png"))
        
        library_type_updater(self, context) #function called from "fonction_utils" module, update_utils.py
        
        AM.show_prefs_lib = False
        return {"FINISHED"}
    
    def invoke(self, context, event):
        AM = bpy.context.window_manager.asset_m
        AM.lib_name = ""
        self.library_path = get_library_path()
        self.libraries = [lib for lib in listdir(join(self.library_path, AM.library_type)) if isdir(join(self.library_path, AM.library_type, lib))]
        dpi_value = context.user_preferences.system.dpi
        
        return context.window_manager.invoke_props_dialog(self, width = dpi_value*3, height = 100)
    
    def draw(self, context):
        AM = context.window_manager.asset_m
        layout = self.layout
        
        layout.label("Choose your library name:")
        layout.prop(AM, "lib_name")

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

class RemoveAssetLibrary(Operator):
    ''' Remove the library from your Asset management library '''
    bl_idname = "object.remove_asset_m_library"
    bl_label = "Remove Library"
    
    @classmethod
    def poll(cls, context):
        AM = context.window_manager.asset_m
        return len(AM.library_list) >= 2
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
        
        if AM.delete_library_choise == 'yes':
            shutil.rmtree(join(library_path, AM.library_type, AM.libraries))
            library_type_updater(self, context)
            AM.show_prefs_lib = False
            return {'FINISHED'}
        
        else:
            AM.show_prefs_lib = False
            return {'FINISHED'}
        
    
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        AM.delete_library_choise = 'no'
        dpi_value = bpy.context.user_preferences.system.dpi
        
        return context.window_manager.invoke_props_dialog(self, width = dpi_value*3, height = 100)
    
    def draw(self, context):
        layout = self.layout
        AM = context.window_manager.asset_m
        
        layout.label("Delete library \" {} \".".format(AM.libraries), icon = 'ERROR')
        layout.label("  All the categories will be deleted")
        layout.label("  Are you sure ?")
        row = layout.row(align = True)
        row.prop(AM, "delete_library_choise", expand = True)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

class RenameLibrary(Operator):
    ''' Rename the current library '''
    bl_idname = "object.asset_m_rename_library"
    bl_label = "Rename Library"
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
 
        rename(join(library_path, AM.library_type, AM.libraries), join(library_path, AM.library_type, AM.change_library_name)) 

        AM.change_library_name = ""
        AM.rename_library = False
        AM.show_prefs_lib = False
        library_type_updater(self, context)
        return {'FINISHED'}

    
# -----------------------------------------------------------------------------
#    CATEGORY OPERATORS
# -----------------------------------------------------------------------------

class AddAssetCategory(Operator):
    """ Add a new category in your Asset Management library"""
    bl_idname = "object.add_asset_category"
    bl_label = "Add Asset Category"
 
    def execute(self, context):
        AM = bpy.context.window_manager.asset_m
        addon_path = get_addon_path()
        empty_icon_path = join(addon_path, "icons", "EMPTY.png")
        library_type = AM.library_type
 
        # if the category name already exist or if there's no defined name, the operator will be call again 
        if AM.cat_name in self.categories or not AM.cat_name:
            bpy.ops.object.add_asset_category('INVOKE_DEFAULT')
 
        else:
            # creating the category folder in the library folder
            makedirs(join(self.library_path, library_type, AM.libraries, AM.cat_name))
 
            # creating the "blends" or "IBL", "Favorites" and "icons" folder in the My_category folder
            folders = ["Favorites", "icons"]
            if AM.library_type == 'hdri':
                folders.append("IBL")
            else:
                folders.append("blends")
            
            for f in folders:
                makedirs(join(self.library_path, library_type, AM.libraries, AM.cat_name, f))
 
            # adding the thumbnails
            shutil.copy(empty_icon_path, join(self.library_path, library_type, AM.libraries, AM.cat_name, "icons", "EMPTY.png"))
 
        category_updater(self, context) #function called from "fonction_utils" module, update_utils.py
        AM.show_prefs_cat = False
        return {"FINISHED"}
 
    def invoke(self, context, event):
        AM = bpy.context.window_manager.asset_m
        AM.cat_name = ""
        self.library_path = get_library_path()
        self.categories = [cat for cat in listdir(join(self.library_path, AM.library_type, AM.libraries)) if isdir(join(self.library_path, AM.library_type, AM.libraries, cat))]
        dpi_value = context.user_preferences.system.dpi
 
        return context.window_manager.invoke_props_dialog(self, width = dpi_value*3, height = 100)
 
    def draw(self, context):
        AM = context.window_manager.asset_m
        layout = self.layout
 
        layout.label("Choose your category name:")
        layout.prop(AM, "cat_name")

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
class RemoveAssetCategory(Operator):
    ''' Remove the category from your Asset management library '''
    bl_idname = "object.remove_asset_m_category"
    bl_label = "Remove Category"
 
    @classmethod
    def poll(cls, context):
        AM = context.window_manager.asset_m
        return len(AM.category_list) >= 2
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
 
        if AM.delete_category_choise == 'yes':
            shutil.rmtree(join(library_path, AM.library_type, AM.libraries, AM.categories))
            category_updater(self, context)
            AM.show_prefs_cat = False
            return {'FINISHED'}
 
        else:
            AM.show_prefs_cat = False
            return {'FINISHED'}
 
 
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        AM.delete_category_choise = 'no'
        dpi_value = bpy.context.user_preferences.system.dpi
 
        return context.window_manager.invoke_props_dialog(self, width = dpi_value*3, height = 100)
 
    def draw(self, context):
        layout = self.layout
        AM = context.window_manager.asset_m
 
        layout.label("Delete category \" {} \".".format(AM.categories), icon = 'ERROR')
        layout.label("  All the assets will be deleted")
        layout.label("  Are you sure ?")
        row = layout.row(align = True)
        row.prop(AM, "delete_category_choise", expand = True)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
class RenameCategory(Operator):
    ''' Rename the current category '''
    bl_idname = "object.asset_m_rename_category"
    bl_label = "Rename Category"
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
 
        rename(join(library_path, AM.library_type, AM.libraries, AM.categories), join(library_path, AM.library_type, AM.libraries, AM.change_category_name)) 
 
        AM.change_category_name = ""
        AM.rename_category = False
        AM.show_prefs_cat = False
        category_updater(self, context)
        return {'FINISHED'}