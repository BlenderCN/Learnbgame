import bpy
import os

from .prefs import get_addon_preferences
from .misc_functions import clear_coll_prop, create_custom_path_props, create_prop

class NDReloadCustomPath(bpy.types.Operator):
    bl_idname = "nd.reload_custom_path"
    bl_label = "Reload Custom Path"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        prefs=get_addon_preferences()
        path=prefs.prefs_folderpath
        dirpath=os.path.join(path, 'folders')
        
        #get or create prop
        prop=create_prop()
        
        #clean custom path
        custompath=clear_coll_prop(prop.dirpath_coll)
        
        #create new path
        create_custom_path_props(dirpath, prop.dirpath_coll)
        
        print('ND custom path reloaded')
        return {"FINISHED"}
        