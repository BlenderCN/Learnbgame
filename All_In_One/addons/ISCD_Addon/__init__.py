bl_info = {
    'name': 'ISCD Addon',
    'category': 'Import-Export',
    'version': (1, 0, 0),
    'blender': (2, 78, 0),
    "description": "Imports and exports 3d  meshes and interfaces with ISCD tools",
    "author": "Loïc NORGEOT",
    "warning": "Needs the installation of exterior software!"
}

import bpy
from . import addon
from . import layout

#register and unregister
def register():
    bpy.utils.register_module(__name__)
def unregister():
    bpy.utils.unregister_module(__name__)
if __name__ == "__main__":
    register()
