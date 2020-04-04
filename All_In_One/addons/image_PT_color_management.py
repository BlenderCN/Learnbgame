# -*- coding: utf-8 -*-

# <pep8 compliant>

bl_info = {
    "name": "Color Management Panel in Image Editor/Node Editor",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "location": "Image Editor -> Preview Region (T-KEY) - Node Editor -> UI Region (N-KEY)",
    "description": "Display the Color Management Panel in Image Editor Preview Region",
    "warning": "",
    "category": "Learnbgame",
}

"""Color Management Panel in Image Editor/Node Editor"""

import bpy
from bpy.types import Panel

from bl_ui.properties_scene import SCENE_PT_color_management

class ColorManagementPanel(Panel):
    bl_label = "Color Management"
    bl_options = {'DEFAULT_CLOSED'}
    draw = SCENE_PT_color_management.draw

class IMAGE_PT_color_management(ColorManagementPanel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'PREVIEW'

class NODE_PT_color_management(ColorManagementPanel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

def register():
    bpy.utils.register_class(IMAGE_PT_color_management)
    bpy.utils.register_class(NODE_PT_color_management)

def unregister():
    bpy.utils.unregister_class(IMAGE_PT_color_management)
    bpy.utils.unregister_class(NODE_PT_color_management)

if __name__ == "__main__":
    register()

