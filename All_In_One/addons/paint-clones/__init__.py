import bpy
from .paint_clones import *


bl_info = {
    "name": "Paint Clones",
    "author": "Stephen Leger",
    "version": (0, 1, 1),
    "blender": (2, 77, 0),
    "location": "3D View -> Tool Shelf -> Object Tools Panel (at the bottom)",
    "description": "Paint Clones",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/mifth/mifthtools/edit/master/blender/addons/paint_clones/",
    "category": "Object"
}


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.paintClonesTools = bpy.props.PointerProperty(
        name="Paint Clones Variables",
        type=PaintClonesProperties,
        description="Paint Clones Properties"
    )


def unregister():
    del bpy.types.Scene.paintClonesTools
    bpy.utils.unregister_module(__name__)
