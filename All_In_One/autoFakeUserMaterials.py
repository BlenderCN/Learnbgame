
bl_info = {
    "name": "Save unused Materials and Textures",
    "author": "CoDEmanX",
    "version": (1, 0, 0),
    "blender": (2, 63, 0),
    "location": "(none)",
    "description": "Enable fake user to rescue unused materials / textures automatically before saving",
    "warning": "Make sure this addon is enabled by default!",
    "wiki_url": "http://blender.stackexchange.com/q/9289/935",
    "category": "Learnbgame",
}

import bpy
from bpy.app.handlers import persistent
from itertools import chain

@persistent
def enable_fakeuser_materials(scene):
    for datablock in chain(bpy.data.materials, bpy.data.textures):
        datablock.use_fake_user = True

def register():
    bpy.app.handlers.save_pre.append(enable_fakeuser_materials)

def unregister():
    bpy.app.handlers.save_pre.remove(enable_fakeuser_materials)

if __name__ == "__main__":
    register()
