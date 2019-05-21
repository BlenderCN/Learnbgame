bl_info = {
    "name": "Smart UV",
    "category": "UV",
    "author": "Jimmy Livefjord, roaoao, Diego Quevedo, Nicholas Anderson",
    "version": (1, 0, 3),
    "blender": (2, 76, 0),
}


import importlib
import sys
import bpy


MODULES = (
    "addon",
    "overlay",
    "dynamic_property_group",
    "hotkeys",
    "uv_utils",
    "ui_utils",
    "uv_island_align",
    "uv_align_by_edge",
    "uv_rotate",
    "uv_snap",
    "uv_reunwrap",
    "ui_panels",
    "ui_pie_menus",
    "preferences",
)

for mod in MODULES:
    if mod in locals():
        importlib.reload(locals()[mod])
    else:
        importlib.import_module("%s.%s" % (__name__, mod))


def register():
    bpy.utils.register_module(__name__)

    for mod in MODULES:
        m = sys.modules["%s.%s" % (__name__, mod)]
        if hasattr(m, "register"):
            m.register()


def unregister():
    for mod in reversed(MODULES):
        m = sys.modules["%s.%s" % (__name__, mod)]
        if hasattr(m, "unregister"):
            m.unregister()

    bpy.utils.unregister_module(__name__)