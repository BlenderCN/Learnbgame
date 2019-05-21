
import os

bl_info = {
    "name"       : "CustomeRender",
    "description": "Exporter for custome Render",
    "author"     : "abhilash" ,
    "version"    : (0, 0, 1),
    "blender"    : (2, 67, 0),
    "api"        : 57908,
    "category"   : "Render",
    "location"   : "Info header > render engine menu",
    "warning"    : "Development version, may crash",
    "wiki_url"   : "",
    "tracker_url": "",
    "tooltip"    : "Custome Render Exporter",
    "license"    : "GPL Version 2"
    }

def plugin_path():
    return os.path.dirname(os.path.realpath(__file__))

if 'core' in locals():
    import imp
    imp.reload(core)
else:
    import bpy
    
    from extensions_framework import Addon
    CustomeRenderAddon = Addon(bl_info)
    register, unregister = CustomeRenderAddon.init_functions()
    
    # Importing the core package causes extensions_framework managed
    # RNA class registration via @CustomeRenderAddon.addon_register_class
    from . import core

