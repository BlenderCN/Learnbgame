bl_info = {
    "name": "Doge Auto Model",
    "description": "Addon para realizar a automoção da modelagem de avatares a partir de uma imagem",
    "autor": "MYH Nihongo Dev",
    "version": (0, 5),
    "blender": (2, 7, 1),
    "location": "View 3D > Tools > Auto Model",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

modules = ('script_main', 'script_aux', 'user_interface', 'util_funcs')
if "bpy" in locals() :
    import imp
    for mod in modules:
        exec("imp.reload(%s)" % mod)
else:
    for mod in modules:
        exec("from . import %s" % mod)

import bpy



def register() :
    user_interface.register();
    script_main.register();
    script_aux.register();

def unregister() :
    user_interface.unregister();
    script_main.unregister();
    script_aux.unregister();