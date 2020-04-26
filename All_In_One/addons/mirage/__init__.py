'''
Copyright (C) 2015 Diego Gangl
<diego@sinestesia.co>

Created by Diego Gangl. This file is part of Mirage.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Mirage",
    "description": "Landscape Generator",
    "author": "Diego Gangl",
    "version": (2, 0, 0),
    "blender": (2, 75, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }
    
    
import os
import pkgutil
import importlib

import bpy      
import traceback

icons_storage = {}


# Handle module loading and re-loading
# ----------------------------------------------------------------------------
def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon. 
    
    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    def get_submodule_names(path = path[0], root = ""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else: 
                module_names.append(root + module_name)
        return module_names 

    def import_submodules(names):
        modules = []
        for name in names:
            modules.append(importlib.import_module("." + name, package_name))
        return modules
        
    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)
    
    bpy.utils.refresh_script_paths()
    importlib.invalidate_caches()

    names = get_submodule_names()
    modules = import_submodules(names)        

    if reload: 
        reload_modules(modules) 
        
    return modules
    
    
# Load and reload submodules
modules = setup_addon_modules(__path__, __name__, "bpy" in locals())


import bpy.utils.previews

# Icons
# ----------------------------------------------------------------------------
icon_paths = [
                'header_terrain',  # file is icons/header_terrain.png
                'header_tools',
                'header_tree_dist',
                'edge_none',
                'edge_smoothed',
                'edge_straight',
                'edge_island',
                'initial_heights',
             ]


def register():

    try: 
        bpy.utils.register_module(__name__)
    except: 
        traceback.print_exc()
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

    from . import ui, data, presets
    data.panel_category_hack(None, bpy.context)

    icons_storage['main'] = bpy.utils.previews.new()
    icons_storage['heightmap'] = bpy.utils.previews.new() 

    source_dir = os.path.join(os.path.dirname(__file__), "icons")
     
    for name in icon_paths:
        icon_name = os.path.join(source_dir, name + '.png') 
        icons_storage['main'].load(name, icon_name, 'IMAGE')

    
    data.heightmap_icons = icons_storage['heightmap']
    data.heightmap_icons.cache = ()
    data.heightmap_icons.paths = []
    
    bpy.types.WindowManager.mirage = bpy.props.PointerProperty(type = data.MG_PROP_Main)
    bpy.types.Object.mirage = bpy.props.PointerProperty(type = data.MG_OBJ_Terrain)

    data.register_terrain_features()
    presets.load_all_presets()


def unregister():
    for icon_collection in icons_storage.values():
        bpy.utils.previews.remove(icon_collection)

    icons_storage.clear()

    bpy.context.window_manager.mirage.terrain.features.clear()
    bpy.context.window_manager.mirage.presets.preset_list.clear()
    del bpy.types.WindowManager.mirage
    del bpy.types.Object.mirage

    bpy.utils.unregister_module(__name__)
    
    print("Unregistered {}".format(bl_info["name"]))
