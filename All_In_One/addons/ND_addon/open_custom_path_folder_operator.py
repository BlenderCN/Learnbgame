import bpy
import os

from .prefs import get_addon_preferences
from .misc_functions import open_folder

#open cache folder
class NDOpenCustomPathFolder(bpy.types.Operator):
    bl_idname = "nd.open_custom_path_folder"
    bl_label = "Open Custom Path Folder"
    bl_description = ""
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        prefs=get_addon_preferences()
        path=prefs.prefs_folderpath
        dirpath=os.path.join(path, 'folders')
        
        open_folder(dirpath)
                
        return {'FINISHED'}