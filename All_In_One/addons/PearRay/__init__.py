bl_info = {
    "name": "PearRay",
    "description": "Basic PearRay integration for blender.",
    "author": "Ömercan Yazici",
    "version": (0, 4),
    "blender": (2, 70, 0),
    "location": "Render > Engine > PearRay",
    "warning": "experimental",
    "tracker_url": "https://github.com/PearCoding/PearRay/issues/new",
    "category": "Learnbgame",
    }


if "bpy" in locals():
    import importlib
    importlib.reload(core)
    importlib.reload(export)
    importlib.reload(properties)
    importlib.reload(ui)
else:
    import bpy
    from . import (
            core,
            export,
            properties,
            ui,
            )


## Initialization
def register():
    bpy.utils.register_module(__name__)
    properties.register()
    ui.register()


def unregister():
    ui.unregister()
    properties.unregister()
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
