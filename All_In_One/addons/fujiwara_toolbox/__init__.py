import bpy


bl_info = {
    "name": "Fujiwara Toolbox",
    "description": "",
    "author": "Yusuke Fujiwara",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "View3D",
    "wiki_url": "",
    "category": "Learnbgame"
}


import sys, os
sys.path.append(os.path.dirname(__file__))


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    for module in modules:
        if hasattr( module, "sub_registration" ):
            module.sub_registration()
        

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    for module in modules:
        if hasattr( module, "sub_unregistration" ):
            module.sub_unregistration()

    print("Unregistered {}".format(bl_info["name"]))
