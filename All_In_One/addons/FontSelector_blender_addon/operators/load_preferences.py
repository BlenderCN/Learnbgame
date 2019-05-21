import bpy
import os

from ..preferences import get_addon_preferences
from ..functions.misc_functions import absolute_path, clear_collection
from ..functions.json_functions import read_json

from ..global_variable import json_font_folders
from ..global_messages import fontfolder_loaded, fontfolder_not_loaded


class FontSelectorLoadFPPrefs(bpy.types.Operator):
    bl_idname = "fontselector.load_fpprefs"
    bl_label = "Load Font Folders"
    bl_description = "Load Font Folders Paths from external Font Selector preferences File"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = absolute_path(addon_preferences.prefs_folderpath)
        json_path = os.path.join(prefs, json_font_folders)
        return os.path.isfile(json_path)
    
    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        font_folders_list = addon_preferences.font_folders
        prefs = addon_preferences.prefs_folderpath
        prefpath = absolute_path(prefs)
        json_path = os.path.join(prefpath, json_font_folders)
        
        #remove existing folder list
        clear_collection(font_folders_list)
        
        #load json file
        folders_count = 0
        datas = read_json(json_path)
        for folder in datas['fonfolders'] :
            folders_count += 1
            newfolder = font_folders_list.add()
            newfolder.folderpath = folder['folder_path']

        # inform user
        if folders_count > 0 :
            self.report({'INFO'}, fontfolder_loaded)
        else :
            self.report({'WARNING'}, fontfolder_not_loaded)
            
        return {'FINISHED'}