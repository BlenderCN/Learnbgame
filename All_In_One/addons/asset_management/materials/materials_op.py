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
from bpy.types import Operator
from os import remove, listdir, makedirs
from os.path import join, isfile, isdir
from ..function_utils.get_path import *
from .materials_functions import (add_material_library,
                                  generate_thumbnail_material,
                                  get_valid_materials,
                                  )
from ..function_utils.update import library_type_updater
from ..function_utils.utils import (get_asset_name,
                                    save_tmp,
                                    )
 
 
class AddMaterialInLibrary(Operator):
    """ Add the active material in the asset library """
    bl_idname = "object.add_material_in_library"
    bl_label = "Add material in library"
    bl_options = {'REGISTER'}
 
    def modal(self, context, event): 
        AM = context.window_manager.asset_m
        library_path = get_library_path()
 
        if AM.is_deleted:
            
            save_tmp() # for more security , creating a backup of the scene in case the addition goes wrong
            
            for mat in AM.material_rendering:
                shutil.copy(join(self.addon_path, "blend_tools", "material", "base_mat.blend"), join(self.directory_path, mat + ".blend"))
                
                add_material_library(join(self.directory_path, mat + ".blend"), mat, self.pack)

            if isfile(join(self.directory_path, AM.material_rendering[-1] + ".blend")):
 
                AM.adding_options = False
 
                bpy.ops.object.run_generate_thumbnails('INVOKE_DEFAULT')
 
                return {'FINISHED'}
            else:
                return {'PASS_THROUGH'} 
        else:
            return {'PASS_THROUGH'}   
 
 
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        self.addon_prefs = get_addon_preferences()
        self.directory_path = get_directory("blends")
        self.addon_path = get_addon_path()
        self.pack = "pack" if self.addon_prefs.pack_image == 'pack' else ""
        
        if AM.multi_materials:
            for mat in get_valid_materials():
                AM.material_rendering.append(mat)
        else:
            AM.material_rendering.append(bpy.context.active_object.active_material.name)
 
        if not AM.multi_materials and AM.replace_rename == 'replace':
            bpy.ops.object.remove_asset_from_lib()
 
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class CreateRenderSceneLib(Operator):
    """ Create the  tree folder for the render scene lybrary """
    bl_idname = "object.create_rder_scn_lib"
    bl_label = "Create Render Scene Library"
    bl_options = {'REGISTER', 'UNDO'}
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
        addon_path = get_addon_path()
        empty_icon_path = join(addon_path, "icons", "EMPTY.png")
 
        makedirs(join(library_path, AM.library_type, "Render Scenes"))
 
        # creating a category folder in the My_library folder
        makedirs(join(library_path, AM.library_type, "Render Scenes", "My_category"))
 
        # creating the "blends" or "IBL", "Favorites" and "icons" folder in the My_category folder
        folders = ["blends", "Favorites", "icons"]
 
        for f in folders:
            makedirs(join(library_path, AM.library_type, "Render Scenes", "My_category", f))
 
        # adding the thumbnails
        shutil.copy(empty_icon_path, join(library_path, AM.library_type, "Render Scenes", "My_category", "icons", "EMPTY.png"))
 
        library_type_updater(self, context) #function called from "fonction_utils" module, update.py
 
        AM.libraries = "Render Scenes"
        return {'FINISHED'}
