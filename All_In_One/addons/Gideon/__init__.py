import bpy

bl_info = {
    "name" : "Gideon Render Engine",
    "description" : "Fully functional raytracer easily extendible for experimenting with new rendering features.",
    "author" : "Curtis Andrus",
    "version": (1, 0),  
    "blender": (2, 6, 6),  
    "category": "Render"
}

from . import render, ui, properties

def register():
    properties.register()
    ui.register()
    bpy.utils.register_module(__name__)


def unregister():
    ui.unregister()
    properties.unregister()
    bpy.utils.unregister_module(__name__)
