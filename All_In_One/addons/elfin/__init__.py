#
# Elfin's GUI Front-end as a Blender addon
# 
# Author: Joy Yeh 
# Email: joyyeh.tw@gmail.com
#

# Addon design notes
#   * Each separate object is a separate chain
#   * There should be no faces in any design spec object
#       * Code simply ignores faces
#       x Provide a face delete operator 
#   * There should be no discontinuities in an object
#       * Code should verify this
#   x Unit conversion: 1 blender unit is 10 A, or 1 nm
#       x 1 blender unit === 10 pymol units
#   * Module avatar generation:
#       * How to do avatars in viewport elegantly? 
#           * Use links so none of the models can be edited
#

bl_info = {
    'name': 'Elfin UI', 
    'category': 'Elfin',
    'author': 'Joy Yeh',
    'version': (0, 1, 0),
    'blender': (2, 79, 0),
    'description': 'Addon for assembling proteins',
    'wiki_url': 'https://github.com/joy13975/elfin-ui'
}

import sys
import importlib
import re
import os


# Dyanmic import and reload ----------------------

print('--------------------- Elfin UI Addon import/reload')

# Addons don't have control over panel order, but can set them initially by
# explicit registration. The user would still be able to re-arrange them, so
# there is little point in trying to sort them by code.
modules_to_import = [ 
    'addon_paths',
    'debug',
    'livebuild_helper',
    'livebuild', 
    'obj_processing',
    'module_lifetime_watcher',
    'elfin_scene_properties',
    'elfin_object_properties',
    'export',
    'import',
]
root_module = sys.modules[__name__]

for mod in modules_to_import:
    # Support 'reload' case.
    if mod in locals():
        importlib.reload(getattr(root_module, mod))
        print('Reloaded ', mod)
    else:
        setattr(root_module, mod, importlib.import_module('.' + mod, 'elfin'))
        print('Imported ', mod)

import bpy
from bpy.app.handlers import persistent

# Handlers --------------------------------------

def remove_handler(handler_list, handler):
    handler_list[:] = [h for h in handler_list if h is not handler]

def remove_then_add_handler(handler_list, handler):
    """Remove a handler before adding it to prevent duplicates."""
    remove_handler(handler_list, handler)
    handler_list.append(handler)

mod_life_watcher = module_lifetime_watcher.ModuleLifetimeWatcher()
mlw_handler_list = bpy.app.handlers.scene_update_post

@persistent
def remove_watcher(scene):
    remove_handler(mlw_handler_list,
        mod_life_watcher)

@persistent
def add_watcher(scene):
    """Makes a new instance of ModuleLifetimeWatcher and sets that as the new
    watcher globally"""
    global mod_life_watcher
    mod_life_watcher = module_lifetime_watcher.ModuleLifetimeWatcher()
    mlw_handler_list.append(mod_life_watcher)

def watch_movement(scene):
    # obj = bpy.context.active_object
    # if obj and obj.is_updated:
    #     print('obj updated: {}, {}'.format(obj, obj.location))
    ...

# Registration ----------------------------------

def register():
    """Registers PropertyGroups and handlers"""
    print('--------------------- Elfin Front Addon register()')
    bpy.utils.register_module(__name__)

    bpy.types.Scene.elfin = bpy.props.PointerProperty(type=elfin_scene_properties.ElfinSceneProperties)
    bpy.types.Object.elfin = bpy.props.PointerProperty(type=elfin_object_properties.ElfinObjectProperties)

    # Handlers 

    # Module Lifetime Watcher needs to be unloaded if the current file is
    # getting unloaded. Add the watcher back when new file is loaded so that
    # the watcher initializes correctly on the new already-existing objects in
    # the scene without considering them as new entrances.
    remove_then_add_handler(bpy.app.handlers.load_pre,
        remove_watcher)
    remove_then_add_handler(bpy.app.handlers.load_post,
        add_watcher)
    remove_then_add_handler(bpy.app.handlers.scene_update_pre,
        watch_movement)

    # Watcher needs to be hooked up in register() as well, because on addon
    # reload the load_pre and load_post handlers won't get called.
    remove_watcher(None)
    add_watcher(None)

    bpy.types.INFO_MT_add.append(livebuild_helper.module_menu)

    print('--------------------- Elfin Front Addon registered')
    
def unregister():
    """Unregisters PropertyGroups and handlers"""
    print('------------------- Elfin Front Addon unregister()')
    bpy.utils.unregister_module(__name__)

    # Also remove any attributes added by Elfin. Blender does not
    # automatically remove them.
    types = [bpy.types.Scene, bpy.types.Object]
    for t in types:
        for k in dir(t):
            if k.startswith('elfin'):
                delattr(t, k)

    # Handlers
    remove_watcher(None)
    remove_handler(bpy.app.handlers.load_pre,
        remove_watcher)
    remove_handler(bpy.app.handlers.load_post,
        add_watcher)
    remove_handler(bpy.app.handlers.scene_update_pre,
        watch_movement)

    bpy.types.INFO_MT_add.remove(livebuild_helper.module_menu)
                
    print('------------------- Elfin Front Addon unregistered')

if __name__ == '__main__':
    register()
