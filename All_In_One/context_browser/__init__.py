bl_info = {
    "name": "Context Browser",
    "category": "Learnbgame",
    "author": "roaoao",
    "version": (1, 2, 1),
    "blender": (2, 80, 0),
    "tracker_url": "http://blenderartists.org/forum/showthread.php?447962",
    "wiki_url": (
        "https://wiki.blender.org/index.php/User:Raa/Addons/Context_Browser"),
}

use_reload = "addon" in locals()
if use_reload:
    import importlib
    importlib.reload(locals()["addon"])
    del importlib

from . import addon
addon.init_addon(
    [
        "constants",
        "utils.property_utils",
        "utils.ui_utils",
        "utils.",
        "ops.",
        "",
    ],
    use_reload=use_reload,
    background=False,
)


def register():
    addon.register_modules()


def unregister():
    addon.unregister_modules()
