#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------

bl_info = \
    {
        "name": "Display Header buttons",
        "author" : "Walid Shouman <eng.walidshouman@gmail.com>",
        "version" : (1, 0, 0),
        "blender" : (2, 7, 9),
        "location" : "All Editor Headers",
        "description" :
            "Add a button to each editor header.",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category": "Learnbgame",
    }

#
# support reloading script
#

if "bpy" in locals():
    # Reloaded multifiles
    import importlib

    importlib.reload(header_buttons)

else:
    # Imported multifiles
    from .src import header_buttons

import bpy
from .src import header_buttons_registration

#
#  Registration
#

def register():
    # register_module is responsible for registering the operators
    bpy.utils.register_module(__name__)
    header_buttons_registration.register()

def unregister():
    header_buttons_registration.unregister()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

