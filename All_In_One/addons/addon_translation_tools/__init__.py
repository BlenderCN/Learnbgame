# -*- coding: utf-8 -*-
import bpy
from bpy.props import *
import importlib

try:
    importlib.reload(translation_tools_panel)
    importlib.reload(translation_tools_operator)
    importlib.reload(translation_tools_translation_ja)
except:
    from . import translation_tools_panel
    from . import translation_tools_operator
    from . import translation_tools_translation_ja

bl_info = {
    "name": "Addon Translation Tools",
    "version": (0, 1, 0),
    "author": "nagadomi@nurs.or.jp",
    "category": "Learnbgame",
    "location": "Text Editor > Tools Panel > Addon Translation .+",
}

def register():
    bpy.utils.register_module(__package__)
    bpy.types.Text.translation_tools = PointerProperty(type=translation_tools_panel.TextTranslationProperty)
    bpy.types.Scene.translation_tools = PointerProperty(type=translation_tools_panel.PanelProperty)
    translation_tools_translation_ja.register(__package__)

def unregister():
    del bpy.types.Scene.translation_tools
    del bpy.types.Text.translation_tools
    bpy.utils.unregister_module(__package__)
    translation_tools_translation_ja.unregister(__package__)
