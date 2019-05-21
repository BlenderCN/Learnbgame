bl_info = {
    "name": "elara",
    "author": "mefalo",
    "version": (0, 0, 1),
    "blender": (2, 7, 8),
    "location": "Info Header (Render Engine Menu)",
    "description": "Elara Renderer",
    "warning": "",
    "wiki_url": "http://rendease.com",
    "tracker_url": "http://rendease.com",
    "category": "Learnbgame"
}

import bpy
from . import render
from . import ui

class ElaraAddonPanel(bpy.types.AddonPreferences):
    bl_idname = __package__

    elara_directory = bpy.props.StringProperty(name="Elara SDK Directory", subtype='DIR_PATH', default="")

    def draw(self, context):
        self.layout.prop(self, "elara_directory", text="Elara SDK Directory")

def register():
    bpy.utils.register_class(ElaraAddonPanel)
    render.register()
    ui.register()

def unregister():
    bpy.utils.unregister_class(ElaraAddonPanel)
    render.unregister()
    ui.unregister()