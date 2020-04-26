try:
    import bpy
except ImportError:
    bpy = None


# TODO: remove and use something like app.init()
if bpy:
    from albam.registry import register, unregister
    import albam.ui.blender
    from albam.engines.mtframework import blender_import,  blender_export


bl_info = {
    "name": "Albam",
    "author": "Sebastian Brachi",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "location": "Properties Panel",
    "description": "Import-Export multiple video game formats",
    "wiki_url": "https://github.com/Brachi/albam",
    "tracker_url": "https://github.com/Brachi/albam/issues",
    "category": "Learnbgame",
}
