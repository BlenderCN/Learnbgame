import bpy
import shutil
import os
import time

from .prefs import get_addon_preferences

class ND_deploy_addon(bpy.types.Operator):
    bl_idname = "nd.deploy_addon"
    bl_label = "Deploy Addon"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        prefs=get_addon_preferences()
        src=prefs.source
        dest=prefs.destination
        
        if os.path.isdir(src):
            if os.path.isdir(dest):
                #delete entire folder
                print("ND - Deleting Previous Addon")
                shutil.rmtree(dest)
                print("ND - Sleep")
                time.sleep(2)
            #copy
            print("ND - Copying addon")
            shutil.copytree(src, dest)
            #delete cache
            print("ND - Deleting cache")
            cache=os.path.join(dest, "__pycache__")
            if os.path.isdir(cache):
                shutil.rmtree(cache)
            print("ND - Done")
                
        return {"FINISHED"}
        