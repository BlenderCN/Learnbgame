# https://wiki.blender.org/index.php/Dev:Py/Scripts/Guidelines/Addons/metainfo
bl_info = {
    "name": "pezcode script collection",
    'description': 'Miscellaneous scripts',
    "author": "pezcode",
    "version": (0, 0, 0, 2),
    "blender": (2, 79, 0),
    'support': 'COMMUNITY',
    'tracker_url': 'https://github.com/pezcode/blender-scripts/issues',
    'category': 'Misc'
}

# https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
    import importlib
    importlib.reload(batch_rename)
    importlib.reload(bounds_mesh)
    importlib.reload(copy_custom_properties)
    print("Reloaded multifiles")
else:
    from . import batch_rename, bounds_mesh, copy_custom_properties
    print("Imported multifiles")

import bpy

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
