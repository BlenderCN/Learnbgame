bl_info = {
    "name": "Development Display",
    "author": "Florian Felix Meyer (tstscr)",
    "version": (0, 1, 0),
    "blender": (2, 76, 0),
    "location": "View3D",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "User",
}


if "bpy" in locals():
    import importlib
    importlib.reload(display_class)
    if 'Display' in locals():
        del(Display)
        from .display_class import Display
    importlib.reload(operators)
    importlib.reload(ui)

else:
    from . import display_class
    from . import operators
    from . import ui
    from .display_class import Display

import bpy


def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.display_settings = bpy.props.PointerProperty(type=ui.DisplaySettings)
    bpy.types.WindowManager.display = Display()

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.WindowManager.display.draw_stop()
    del(bpy.types.WindowManager.display)
    del(bpy.types.WindowManager.display_settings)
