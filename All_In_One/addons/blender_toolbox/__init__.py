bl_info = {
    "name": "todashuta_toolbox",
    "author": "todashuta",
    "version": (1, 1, 0),
    "blender": (2, 60, 0),
    "location": "command menu (spacebar)",
    "description": "todashuta_toolbox",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}


if "bpy" in locals():
    import importlib
    importlib.reload(todashuta_toolbox)
else:
    from . import todashuta_toolbox


import bpy


def register():
    bpy.utils.register_module(__name__)
    todashuta_toolbox.enable_my_keymaps()


def unregister():
    bpy.utils.unregister_module(__name__)
    todashuta_toolbox.disable_my_keymaps()


if __name__ == "__main__":
    register()
