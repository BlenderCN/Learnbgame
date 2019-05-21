import bpy
import os
import inspect
from bpy.utils import register_class, unregister_class
from . import ui

bl_info = {
    'name': 'Tex Batch Adder',
    'author': 'Botmasher (Joshua R)',
    'blender': (2, 79, 0),
    'version': (1, 0, 0),
    'location': 'View3D',
    'description': 'Bulk load and configure image textures on one object',
    'category': 'Textures'
}

def register_modules(modules, unregister=False):
    for module in modules:
        for member in inspect.getmembers(module, inspect.isclass):
            memberClass = member[1]
            try:
                registration = unregister_class(memberClass) if unregister else register_class(memberClass)
            except RuntimeError:
                print("Failed to load module member class {0}. Skipping for now.".format(memberClass))
    return

def register():
	register_modules([ui])

def unregister():
	register_modules(reversed([ui]), unregister=True)

__name__ == '__main__' and register()
