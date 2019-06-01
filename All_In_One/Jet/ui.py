import bpy
from . import process, list

def register():
    list.register()
    process.register()

def unregister():
    list.unregister()
    process.unregister()


