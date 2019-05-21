# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    

:description:
    

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

bl_info = {
    "name": "bPyNodes Library",
    "author": "Jared Webber - Blender One",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "",
    "description": "Blender Python Nodes extension that provides a python library for creating Python Node systems",
    "category": "System",
    "tracker_url": "",
    "wiki_url": ""
}

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#

from . import base_structs, utils

# Check for Blender
try:
    import bpy
except ImportError:
    from .utils.io import IO
    IO.info("Unable to import bpy module. Setting bpy to None for non-blender environment")
    bpy = None

try:
    from .utils import developer_utils
except:
    pass
if "developer_utils" not in globals():
    message = ("\n\n"
               "bPyNodes Library cannot be registered correctly\n"
               "Troubleshooting:\n"
               "  1. Try installing the addon in the newest official Blender version.\n"
               "  2. Try installing the newest bPyNodes Library version from Gitlab.\n")
    raise Exception(message)

# Import and Reload Submodules
import importlib
from . import developer_utils

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def register_addon():
    """
    Blender specific registration function
    :return:
    """
    # Register Blender Properties and Handlers

    try:
        import pip
    except ImportError:
        IO.info("pip python package not found. Installing.")
        try:
            import ensurepip
            ensurepip.bootstrap(upgrade=True, default_pip=True)
        except ImportError:
            IO.info("pip cannot be configured or installed. ")


def unregister_addon():
    """
    Blender specific un-register function
    :return:
    """
    IO.info("Unregistered bPyNodes Library")


def register():
    """
    Blender specific registration function
    :return: 
    """
    register_addon()
    bpy.utils.register_module(__name__)
    for module in modules:
        if hasattr(module, "register"):
            module.register()
            # Register Blender Properties and Handlers
            # addon_updater_ops.register_updater(bl_info)
            # conf.register()


def unregister():
    """
    Blender specific un-register function
    :return: 
    """
    bpy.utils.unregister_module(__name__)
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
    # Unregister Blender Properties and Handlers
    # conf.unregister()
    # addon_updater_ops.unregister_updater()
    unregister_addon()

# if __name__ == "__main__":
#     register()

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

