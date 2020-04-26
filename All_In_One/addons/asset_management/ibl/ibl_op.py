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
 
import bpy, shutil, pickle
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from os import remove, listdir
from os.path import join, isfile, dirname
from ..function_utils.get_path import (get_directory,
                                       get_library_path,
                                       )
from ..preview.preview_utils import update_pcoll_preview
 
class ImportFilesCollection(bpy.types.PropertyGroup):
    name = StringProperty(
        name = "File Path",
        description = "Filepath used for importing the file",
        maxlen = 1024,
        subtype = 'FILE_PATH',
        )
 
bpy.utils.register_class(ImportFilesCollection)
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class IblImporter(Operator, ImportHelper):
    """ Add the selected hdri with the .hdr ext in your library """
    bl_idname = "wm.ibl_importer"
    bl_label = "IBL Importer"
 
    filter_glob = StringProperty(
        default = "*.hdr;*.exr;*.jpg;*.jpeg;*.png;*.tif",
        options = {'HIDDEN'},
        )
 
    filepath = StringProperty(
        name = "File Path",
        maxlen = 1024,
        subtype = 'FILE_PATH',
        )
 
    files = bpy.props.CollectionProperty(type = ImportFilesCollection)
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        IBL = get_directory("IBL")
        icons = get_directory("icons")
        path = dirname(self.filepath)
        ibl_ext = (".hdr", ".exr", ".jpg", ".jpeg", ".png", ".tif")
        extentions = (".jpg", ".jpeg", ".png")
 
        # thumbnail list present in the source ibl folder to import
        existing_thumb = [f for f in listdir(path) if f.endswith(extentions)]
        # list of ibl names
        IBL_names = [f.name for f in self.files]
        # thumbnail list of ibl library
        Thumb_list = [f.rsplit(".", 1)[0] for f in listdir(icons) if f.endswith(extentions)]
        # ensures the ibl we want to add was not already in the library
        valid_IBL = [f for f in IBL_names if f.rsplit(".", 1)[0] not in Thumb_list]
 
        for ibl in valid_IBL:
            # ensures the ibl we want to add was not already added since "valid_IBL" with a different file extention
            if ibl.rsplit(".", 1)[0] not in [f.rsplit(".", 1)[0] for f in listdir(IBL) if f.endswith(ibl_ext)]:
                shutil.copy(join(path, ibl), join(IBL, ibl))
 
                if not AM.existing_thumb:
                    AM.ibl_to_thumb.append(ibl)
                else:
                    thumb = [f for f in existing_thumb if f.rsplit(".", 1)[0] == ibl.rsplit(".", 1)[0]]
 
                    if thumb:
                        shutil.copy(join(path, thumb[0]), join(icons, thumb[0]))
 
                    else:
                        AM.ibl_to_thumb.append(ibl)
                        
        if AM.ibl_to_thumb:
            bpy.ops.object.run_generate_thumbnails('INVOKE_DEFAULT')
 
        else:
            if isfile(join(icons, "EMPTY.png")):
                remove(join(icons, "EMPTY.png"))
            
            update_pcoll_preview()
 
        AM.adding_options = False
        return {"FINISHED"}

# ------------------------------------------------------------------
#
# ------------------------------------------------------------------

class SaveIblSettings(Operator):
    """ Save the settings of the current IBL """
    bl_idname = "wm.save_ibl_settings"
    bl_label = "Save Ibl Settings"
    bl_options = {"REGISTER"}

    def execute(self, context):
        WM = context.window_manager
        AM = WM.asset_m
        library_path = get_library_path()
        
        ibl_name = WM.AssetM_previews.rsplit(".", 1)[0]
        filename = ibl_name + "_settings"
        
        world = bpy.data.worlds['AM_IBL_WORLD']
        node = world.node_tree.nodes

        setting = {"rotation": tuple(node['Mapping'].rotation),\
                   "projection": AM.projection,\
                   "blur": node['ImageBlur'].inputs[1].default_value,\
                   "visible": world.cycles_visibility.camera,\
                   "transparent": context.scene.cycles.film_transparent,\
                   "gamma": node['AM_IBL_Tool'].inputs[0].default_value,\
                   "L_strengh": node['AM_IBL_Tool'].inputs[2].default_value,\
                   "L_saturation": node['AM_IBL_Tool'].inputs[3].default_value,\
                   "L_hue": tuple(node['AM_IBL_Tool'].inputs[4].default_value),\
                   "L_mix": node['AM_IBL_Tool'].inputs[5].default_value,\
                   "G_strengh": node['AM_IBL_Tool'].inputs[7].default_value,\
                   "G_saturation": node['AM_IBL_Tool'].inputs[8].default_value,\
                   "G_hue": tuple(node['AM_IBL_Tool'].inputs[9].default_value),\
                   "G_mix": node['AM_IBL_Tool'].inputs[10].default_value
                   }
        
        with open(join(library_path, AM.library_type, AM.libraries, AM.categories, "IBL", filename), "wb") as file:
            pkl_save = pickle.Pickler(file)
            pkl_save.dump(setting)
            
        return {"FINISHED"}

# ------------------------------------------------------------------
#
# ------------------------------------------------------------------

class LoadIblSettings(Operator):
    """ Load the settings of the current IBL """
    bl_idname = "wm.load_ibl_settings"
    bl_label = "Load Ibl Settings"
    bl_options = {"REGISTER"}

    def execute(self, context):
        WM = context.window_manager
        AM = WM.asset_m
        library_path = get_library_path()
         
        ibl_name = WM.AssetM_previews.rsplit(".", 1)[0]
        filename = ibl_name + "_settings"
        world = bpy.data.worlds['AM_IBL_WORLD']
        node = world.node_tree.nodes
        
        with open(join(library_path, AM.library_type, AM.libraries, AM.categories, "IBL", filename), "rb") as file:
            pkl_load = pickle.Unpickler(file)
            setting = pkl_load.load()
            
        node['Mapping'].rotation = setting["rotation"]
        AM.projection = setting["projection"]
        node['ImageBlur'].inputs[1].default_value = setting["blur"]
        world.cycles_visibility.camera = setting["visible"]
        bpy.context.scene.cycles.film_transparent = setting["transparent"]
        node['AM_IBL_Tool'].inputs[0].default_value = setting["gamma"]
        node['AM_IBL_Tool'].inputs[2].default_value = setting["L_strengh"]
        node['AM_IBL_Tool'].inputs[3].default_value = setting["L_saturation"]
        node['AM_IBL_Tool'].inputs[4].default_value = setting["L_hue"]
        node['AM_IBL_Tool'].inputs[5].default_value = setting["L_mix"]
        node['AM_IBL_Tool'].inputs[7].default_value = setting["G_strengh"]
        node['AM_IBL_Tool'].inputs[8].default_value = setting["G_saturation"]
        node['AM_IBL_Tool'].inputs[9].default_value = setting["G_hue"]
        node['AM_IBL_Tool'].inputs[10].default_value = setting["G_mix"]
        
        return {"FINISHED"}