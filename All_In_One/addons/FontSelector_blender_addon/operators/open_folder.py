import bpy
import os
import platform
import subprocess

from ..functions.misc_functions import absolute_path, open_folder_in_explorer

class FontSelectorOpenSubdirectory(bpy.types.Operator):
    bl_idname = "fontselector.open_subdirectory"
    bl_label = "Open Subdirectory"
    bl_description = "Open selected Subdirectory in Explorer"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bpy.data.window_managers['WinMan'].fontselector_subdirectories != 'All'
        #return True
    
    def execute(self, context):
        subdir = bpy.data.window_managers['WinMan'].fontselector_subdirectories
        #path = ""
        collection_subdir_list = bpy.data.window_managers['WinMan'].fontselector_sub

        if subdir != "All" :
            #find subdir
            for sub in collection_subdir_list :
                if sub.name == subdir :
                    path = absolute_path(sub.filepath)
                    break
            try :
                open_folder_in_explorer(path)
            except FileNotFoundError :
                bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 2)

        return {'FINISHED'}