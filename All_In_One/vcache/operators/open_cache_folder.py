import bpy
import os
import platform
import subprocess

from ..preferences import get_addon_preferences
from ..misc_functions import create_cache_folder, absolute_path

#open cache folder
class VCacheOpenCacheFolder(bpy.types.Operator):
    bl_idname = "vcache.open_cache"
    bl_label = "Open Cache Folder"
    bl_description = "Open Viewport Cache Folder in Explorer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        cachefolder = addon_preferences.prefs_folderpath
        path=absolute_path(cachefolder)
        
        create_cache_folder()
                
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return {'FINISHED'}