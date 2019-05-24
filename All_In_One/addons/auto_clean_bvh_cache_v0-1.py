######################################################################################################
# Automatically clean your BVH cache at startup                                                      #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me.                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (used by Blender)

bl_info = {
    "name": "Auto Clean BVH Cache",
    "description": 'Automatically clean the BVH cache after starting Blende/loading a file',
    "author": "Lapineige",
    "version": (0, 1),
    "blender": (2, 75, 0),
    "location": "Auto Launch - See Preferences Below",
    "warning": "Experimental Version - Use it at your own risk (be sure to check the cache path)",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

##############
import bpy
import os
from bpy.app.handlers import persistent
import atexit
##############

class AutoCleanBVHCachePreferencesPanel(bpy.types.AddonPreferences):
    """ """
    bl_idname = __name__

    # = StringProperty()

    def draw(self, context):
        user_path = bpy.utils.resource_path('USER')
        config_path = os.path.join(user_path, "cache")

        layout = self.layout

        layout.label(text="BVH cache directory: {0}".format(config_path))
        layout.operator("file.clean_bvh_cache")

        #layout.prop(self, "")
        return {'FINISHED'}

class CleanBVHCache(bpy.types.Operator):
    bl_idname = "file.clean_bvh_cache"
    bl_label = "Clean BVH Cache"

    def execute(self, context):
        user_path = bpy.utils.resource_path('USER')
        config_path = os.path.join(user_path, "cache")

        for file in os.listdir(config_path):
            print(os.path.join(config_path, file))
            os.remove(os.path.join(config_path, file))

        return {'FINISHED'}

@persistent
def clean_bvh_cache_handler(dummy):
    bpy.ops.file.clean_bvh_cache()
    

"""
def clean_on_exit():
    bpy.ops.file.clean_bvh_cache()
atexit.register(clean_on_exit)
"""

##############

def register():
    bpy.utils.register_class(CleanBVHCache)
    bpy.utils.register_class(AutoCleanBVHCachePreferencesPanel)
    bpy.app.handlers.load_post.append(clean_bvh_cache_handler)


def unregister():
    bpy.utils.unregister_class(CleanBVHCache)
    bpy.utils.unregister_class(AutoCleanBVHCachePreferencesPanel)
    bpy.app.handlers.load_post.remove(clean_bvh_cache_handler)


if __name__ == "__main__":
    register()
