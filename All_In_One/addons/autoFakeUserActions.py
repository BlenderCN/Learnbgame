
bl_info = {
    "name": "Save unused Actions",
    "author": "CoDEmanX",
    "version": (1, 0, 0),
    "blender": (2, 63, 0),
    "location": "(none)",
    "description": "Enable fake user to rescue Actions automatically before saving",
    "warning": "Make sure this addon is enabled by default!",
    "wiki_url": "http://blender.stackexchange.com/q/9289/935",
    "category": "Learnbgame",
}

# Slight modification of code shown on wiki_url
# this version saves actions instead of materials

import bpy
from bpy.app.handlers import persistent

@persistent
def enable_fakeuser_actions(scene):
    for datablock in bpy.data.actions:
        datablock.use_fake_user = True

def register():
    bpy.app.handlers.save_pre.append(enable_fakeuser_actions)

def unregister():
    bpy.app.handlers.save_pre.remove(enable_fakeuser_actions)

if __name__ == "__main__":
    register()
