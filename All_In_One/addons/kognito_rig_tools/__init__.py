bl_info = {
    "name":        "Kognito Rig Tools",
    "description":
                   "A set of tools to aid in the generation of"
                   " effective rigs for Unity characters",
    "author":      "Jonathan Williamson, Bassam Kurdali",
    "version":     (0, 0, 2),
    "blender":     (2, 7, 8),
    "location":    "View 3D > Properties",
    "warning":     "",  # used for warning icon and text in addons panel
    "wiki_url":    "",
    "tracker_url": "",
    "category":    "Rigging"
    }

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(tools)

else:
    from . import ui
    from . import tools

import bpy


def register():
    """ Just use register functions from the various submodules """
    ui.register()
    tools.register()



def unregister():
    """ Just use unregister functions from the various submodules """
    tools.unregister()
    ui.unregister()
