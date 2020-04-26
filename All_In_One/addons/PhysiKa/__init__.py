bl_info = {
    "name" : "PhysiKa",
    "description": "A FLIP Fluid Simulation Tool for Blender",
    "author" : "Ryan Guy <ryan.l.guy[at]gmail.com>, Dennis Fassbaender <info[at]df-videos.de>",
    "version" : (0, 0, 1),
    "blender" : (2, 7, 8),
    "location" : "Properties > Physics > PhysiKa",
    "warning" : "Still developing",
    "wiki_url" : "",
    "tracker_url" : "",
    "category": "Learnbgame",
}
if "bpy" in locals():
    import importlib
    reloadable_modules = [
        'utils',
        'objects',
        'materials',
        'properties',
        'operators',
        'ui',
        'presets',
        'export',
        'bake',
        'render',
        'global_vars'
    ]
    for module_name in reloadable_modules:
        if module_name in locals():
            importlib.reload(locals()[module_name])

import bpy

from . import(
    states,
    ui,
    properties,
    operators
)

def register():

    properties.register()
    operators.register()
    ui.register()
    states.register()
    

def unregister():
    
    properties.unregister()
    operators.unregister()
    ui.unregister()
    states.unregister()
