import bpy
import os
import shutil

from ..functions.get_subdirectory_for_install import get_subdirectories_items_for_installation, get_subdirectories_filepath_installation
from ..functions.json_functions import read_json
from ..preferences import get_addon_preferences
from ..functions.misc_functions import absolute_path

from ..global_variable import json_file
from ..global_messages import font_already_installed


class FontSelectorInstallFont(bpy.types.Operator):
    bl_idname = "fontselector.install_font"
    bl_label = "Install Font"
    bl_description = "Install selected Font in specific Font Folder"
    bl_options = {'REGISTER'}

    dupe = False
    subdir = ""
    subdirectories_list = bpy.props.EnumProperty(items = get_subdirectories_items_for_installation, 
                                                name = "Target Subdirectory",
                                                description = "Install selected Font in this Subdirectory")

    @classmethod
    def poll(cls, context) :
        wm = bpy.data.window_managers['WinMan']
        fontlist = wm.fontselector_list
        try :
            os.path.isfile(fontlist[bpy.context.active_object.data.fontselector_override_index].filepath)
            chk_error = 0
        except :
            chk_error = 1
        return wm.fontselector_folder_override != "" and wm.fontselector_override and chk_error == 0

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True

    def __init__(self) :
        addon_preferences = get_addon_preferences()
        prefspath = absolute_path(addon_preferences.prefs_folderpath)
        jsonfile = os.path.join(prefspath, json_file)
        fontlist = bpy.data.window_managers['WinMan'].fontselector_list
        
        font_name = fontlist[bpy.context.active_object.data.fontselector_override_index].name
        datas = read_json(jsonfile)

        for font in datas['fonts'] :
            if font_name == font['name'] :
                self.dupe = True
                self.subdir = font['subdirectory']
 
    def draw(self, context) :
        layout = self.layout
        if not self.dupe :
            layout.prop(self, 'subdirectories_list')
        else :
            layout.label(font_already_installed + self.subdir, icon = 'INFO')

    def execute(self, context) :
        if not self.dupe :
            wm = bpy.data.window_managers['WinMan']
            fontlist = wm.fontselector_list

            font_path = fontlist[bpy.context.active_object.data.fontselector_override_index].filepath

            for sub in get_subdirectories_filepath_installation() :
                if sub[0] == self.subdirectories_list :
                    subdir_path = sub[1]
                    break

            new_font_path = os.path.join(subdir_path, os.path.basename(font_path))

            try :
                #copy
                shutil.copy2(font_path, new_font_path)
                shutil.copystat(font_path, new_font_path)
                # user report
                bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 5)
            except PermissionError :
                bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 6, customstring = subdir_path)

        
        else :
            # user report
            self.report({'INFO'}, font_already_installed + self.subdir)

        return {'FINISHED'}
 