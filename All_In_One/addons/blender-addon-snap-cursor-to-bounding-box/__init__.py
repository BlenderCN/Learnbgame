bl_info = {
    "name": "Snap Cursor to Bounding Box",
    "author": "Toda Shuta",
    "version": (1, 2, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Shift-S (Snap Menu)",
    "description": "Snap Cursor to Bounding Box (Top, Center, Bottom)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


if "bpy" in locals():
    import importlib
    importlib.reload(snap_cursor_to_bounding_box)
else:
    from . import snap_cursor_to_bounding_box


import bpy


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_snap.append(snap_cursor_to_bounding_box.snap_menu_func)
    bpy.types.VIEW3D_MT_object_specials.append(snap_cursor_to_bounding_box.special_menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_snap.remove(snap_cursor_to_bounding_box.snap_menu_func)
    bpy.types.VIEW3D_MT_object_specials.remove(snap_cursor_to_bounding_box.special_menu_func)


if __name__ == "__main__":
    register()
