#!/usr/bin/env python

bl_info = {
    "name": "wxBlender",
    "author": "Metallicow",
    "version": (0, 0, 2),
    "blender": (2, 65, 0),
    "location": "View3D -> Properties -> wxPython",
    "description": "Provides a simple demo on how to use wxPython widgets in Blender.",
    "wiki_url": "http://wxpython.org/Phoenix/snapshot-builds/",
    "tracker_url": "https://github.com/Metallicow/wxBlender/issues",
    "warning": "Requirements: http://wxpython.org/Phoenix/snapshot-builds/ >>> blender's site packages.",
    "category": "Learnbgame",
    }

import bpy
from .wxblender import *

def register():
    bpy.utils.register_class(wxPythonFrameInBlender)
    bpy.utils.register_class(wxPythonMenuInBlender)
    bpy.utils.register_class(wxBlenderPanel)

def unregister():
    bpy.utils.unregister_class(wxBlenderPanel)
    bpy.utils.unregister_class(wxPythonMenuInBlender)
    bpy.utils.unregister_class(wxPythonFrameInBlender)

if __name__ == "__main__":
    register()
