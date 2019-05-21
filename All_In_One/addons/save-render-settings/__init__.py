import bpy
from .render_settings_ui import *


bl_info = {
    "name": "Render Settings",
    "description": "Export and import JSON render settings",
    "category": "Render"
}


def register():
    bpy.utils.register_class(SaveRenderSettingsOperator)
    bpy.utils.register_class(LoadRenderSettingsOperator)
    bpy.utils.register_class(RenderSettingsPanel)


def unregister():
    bpy.utils.unregister_class(SaveRenderSettingsOperator)
    bpy.utils.unregister_class(LoadRenderSettingsOperator)
    bpy.utils.unregister_class(RenderSettingsPanel)
