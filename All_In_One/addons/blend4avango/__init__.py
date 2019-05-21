bl_info = {
    "name": "Blend4Avango",
    "author": "Bauhaus-Universität Weimar",
    "version": (1, 0, 0),
    "blender": (2, 72, 0),
    "b4a_format_version": "1.00",
    "location": "File > Import-Export",
    "description": "Blend4Avango is a Blender Extinsion",
    "warning": "",
    "category": "Import-Export"
}
    
if "bpy" in locals():
    import imp
    imp.reload(properties)
    imp.reload(interface)
    imp.reload(exporter)
    imp.reload(export_threejs)
    imp.reload(nla_script)
else:
    from . import properties
    from . import interface
    from . import exporter
    from . import export_threejs
    from . import nla_script

import bpy
import os

def register(): 
    exporter.register()
    properties.register()
    interface.register()
    nla_script.register()

def unregister():
    exporter.unregister() 
    properties.unregister() 
    interface.unregister() 
    nla_script.unregister() 
    

if __name__ == "__main__":
    register()