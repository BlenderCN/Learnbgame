import bpy
import os

from ..preferences import get_addon_preferences
from ..functions.misc_functions import create_dir, absolute_path
from ..functions.json_functions import initialize_json_fontfolders_datas, add_fontfolders_json, create_json_file

from ..global_variable import json_font_folders
from ..global_messages import fontfolder_saved


class FontSelectorSaveFPPrefs(bpy.types.Operator):
    bl_idname = "fontselector.save_fpprefs"
    bl_label = "Save Font Folders"
    bl_description = "Save Font Folders Paths in external Font Selector preference file"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        fplist = addon_preferences.font_folders
        prefs = addon_preferences.prefs_folderpath
        return len(fplist)>0 and prefs!=''
    
    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        font_folders_list = addon_preferences.font_folders
        prefs = addon_preferences.prefs_folderpath
        prefpath = absolute_path(prefs)
        json_path = os.path.join(prefpath, json_font_folders)
        fontfolder_ok = []
        deleted = []
        
        # check if folder exist and create it if not
        create_dir(prefpath)

        # remove previous json
        if os.path.isfile(json_path) :
            os.remove(json_path)

        chk_folder_exist = 0
        idx = 0
        for folder in font_folders_list :
            folder_path = absolute_path(folder.folderpath)
            if os.path.isdir(folder_path) :
                chk_folder_exist = 1
                # check dupe
                fontfolder_ok.append(folder_path)
            else :
                # delete font folder
                font_folders_list.remove(idx)
                deleted.append(folder_path)
            idx += 1
        
        # format json
        if chk_folder_exist == 1 :
            datas = initialize_json_fontfolders_datas()
            for folder in fontfolder_ok :
                datas = add_fontfolders_json(datas, folder)

            # write json
            create_json_file(datas, json_path)

            # inform user
            if len(deleted) > 0 :
                deleted_list = str(deleted).strip("[]")
                bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 3, customstring = deleted_list)
            else :
                self.report({'INFO'}, fontfolder_saved)
        else :
            if len(deleted) > 0 :
                # inform user
                deleted_list = str(deleted).strip("[]")
                bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 4, customstring = deleted_list)

        return {'FINISHED'}