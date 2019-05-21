bl_info = {
    "name": "How many triangles",
    "description": 'count polygon in your mesh',
    "author": "sititou70",
    "version": (2, 0),
    "blender": (2, 71, 0),
    "location": "View3D > Edit Mode > Tool Shelf > How many triangles Panel",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}

import bpy
from bpy.props import *
from . import ui

def register():
    bpy.utils.register_module(__name__)
    ui.init_scene_properties()

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
