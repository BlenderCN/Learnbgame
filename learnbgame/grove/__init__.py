
"""
if "bpy" in locals():
    import importlib

    importlib.reload(Translation)
    importlib.reload(Languages)
    importlib.reload(Preferences)
    importlib.reload(Operator)
    importlib.reload(Grove)
    importlib.reload(Branch)
    importlib.reload(Node)
    importlib.reload(TwigInstance)
    importlib.reload(Presets)
    importlib.reload(Twigs)
    importlib.reload(Textures)
    importlib.reload(Utils)
else:
    from . import Grove_Preferences
    from . import Grove_Operator

import bpy
from os.path import join, dirname

icons = None
language = 'English'


def add_operator_to_mesh_menu(self, context):
    self.layout.operator(Grove_Operator.TheGrove6.bl_idname, text="The Grove 6", icon_value=icons["IconLogo"].icon_id)


def register():
    global icons
    icons = bpy.utils.previews.new()
    icons_directory = join(dirname(__file__), "Icons")
    icons.load("IconLogo",  join(icons_directory, "IconLogo.png"),  'IMAGE')

    bpy.utils.register_class(Grove_Operator.TheGrove6)
    bpy.utils.register_class(Grove_Preferences.TheGrove6Preferences)
    bpy.context.preferences.addons[__package__].preferences.show_refresh_warning = False
    bpy.types.VIEW3D_MT_mesh_add.append(add_operator_to_mesh_menu)


def unregister():
    bpy.utils.previews.remove(icons)
    bpy.utils.previews.remove(Operator.icons)

    bpy.utils.unregister_class(Grove_Operator.TheGrove6)
    bpy.utils.unregister_class(Grove_Preferences.TheGrove6Preferences)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_operator_to_mesh_menu)
"""