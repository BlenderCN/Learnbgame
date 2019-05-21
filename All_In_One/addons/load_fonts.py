bl_info = {
    "name": "Load Fonts",
    "author": "Chebhou",
    "version": (1, 0),
    "blender": (2, 72, 0),
    "description": "load all fonts from fonts directory",
    "category": "Learnbgame"
}

import os
import bpy
from bpy.app.handlers import persistent

@persistent
def load_fonts(scene):
    font_dir = bpy.context.user_preferences.filepaths.font_directory
    for file in os.listdir(font_dir):
        if file.endswith(".ttf"):  
            bpy.data.fonts.load(font_dir+file)

def register():
    bpy.app.handlers.load_post.append(load_fonts)

def unregister():
    bpy.app.handlers.load_post.remove(load_fonts)
    
if __name__ == "__main__":
    register()
