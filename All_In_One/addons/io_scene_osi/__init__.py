bl_info = {
    "name": "Super Mario Odyssey Stage Importer",
    "description": "Import Super Mario Odyssey Stages",
    "author": "Philippus229, bymlv2 (v1.0.3) by leoetlino, SARCExtract (v0.5) by aboood40091, Sorted Containers (v2.0.4), PyYAML (v3.10)",
    "version": (0, 4, 0),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "warning": "This add-on is under development.",
    "wiki_url": "https://github.com/Philippus229/io_scene_osi/wiki",
    "tracker_url": "https://github.com/Philippus229/io_scene_osi/issues",
    "category": "Import-Export"
}

# Reload the package modules when reloading add-ons in Blender with F8.
if "bpy" in locals():
    import importlib
    if "addon" in locals():
        importlib.reload(addon)
    if "importing" in locals():
        importlib.reload(importing)
    if "byml" in locals():
        importlib.reload(byml)
    if "sortedcontainers" in locals():
        importlib.reload(sortedcontainers)

import bpy
from . import addon
from . import importing
from . import byml
from . import sortedcontainers

def register():
    bpy.utils.register_module(__name__)
    # Addon
    bpy.types.UILayout.osi_colbox = addon.osi_colbox
    # Importing
    bpy.types.INFO_MT_file_import.append(importing.ImportOperator.menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    # Addon
    del bpy.types.UILayout.osi_colbox
    # Importing
    bpy.types.INFO_MT_file_import.remove(importing.ImportOperator.menu_func)
