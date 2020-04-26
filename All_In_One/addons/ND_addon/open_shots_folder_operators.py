import bpy
import os

from .prefs import get_addon_preferences
from .misc_functions import open_folder, return_shot_infos_from_path

class ND_open_settings_folder(bpy.types.Operator):
    bl_idname = "nd.open_settings_folder"
    bl_label = "Open Settings Folder"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved==True

    def execute(self, context):
        prefs=get_addon_preferences()
        path=prefs.prefs_folderpath
        renderpath=os.path.join(path, 'render_settings')
        
        if os.path.isdir(renderpath):
            open_folder(renderpath)
        else:
            inf="ND - no settings folder"
            print(inf)
            self.report({'WARNING'}, inf)
        return {"FINISHED"}

class ND_open_shot_folder(bpy.types.Operator):
    bl_idname = "nd.open_shot_folder"
    bl_label = "Open Shot Folder"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved==True

    def execute(self, context):
        filepath=bpy.data.filepath
        shot, cat, dir=return_shot_infos_from_path(filepath)
        
        if os.path.isdir(dir):
            open_folder(dir)
        else:
            inf="ND - no settings folder"
            print(inf)
            self.report({'WARNING'}, inf)
        return {"FINISHED"}