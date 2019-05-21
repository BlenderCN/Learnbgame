import bpy

from blendmotion import operators, preference, panel, core
from blendmotion.logger import configure_logger, get_logger

bl_info = {
    "name": "blendmotion",
    "author": "coord.e <me@coord-e.com>",
    "version": (0, 1),
    "blender": (2, 7, 9),
    "location": "somewhere",
    "description": "convert animation to robot motion",
    "wiki_url": "https://github.com/DeepL2/blendmotion/wiki",
    "tracker_url": "https://github.com/DeepL2/blendmotion/issues",
    "category": "Development",
}

def register():
    core.register()
    operators.register()
    preference.register()
    panel.register()

    configure_logger(__name__).info("BlendMotion is successfully registered")

def unregister():
    operators.unregister()
    preference.unregister()
    panel.unregister()
    core.unregister()

    get_logger().info("BlendMotion is successfully unregistered")
