# -*- coding: utf-8 -*-


bl_info= {
    "name": "g_tools",
    "author": "garbage",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool Shelf > G Tools",
    "description": "Utility tools for systematic high level failure.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}
    
import bpy

import g_tools.add_fs.curve_ui as curve_ui
import g_tools.add_fs.bone_ui as bone_ui

curve_ui.register()
bone_ui.register()

def register():
    pass