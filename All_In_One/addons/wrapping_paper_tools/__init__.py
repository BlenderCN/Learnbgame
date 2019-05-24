bl_info= {
    "name": "Wrapping Paper Tools",
    "author": "Takosuke",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Tools Panel",
    "description": "Wrapping Paper Tools.",
    "support": "COMMUNITY",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(properties)
    imp.reload(exporter)
else:
    from . import properties, exporter

import bpy
import logging

logger = logging.getLogger("wrapping_paper_tools")

if not logger.handlers:
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)-7s %(asctime)s %(message)s (%(module)s %(funcName)s)", datefmt="%H:%M:%S")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL

logger.debug("init logger") # debug, info, warning, error, critical

def register():
    bpy.utils.register_module(__name__)
    properties.register()

def unregister():
    properties.unregister()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
