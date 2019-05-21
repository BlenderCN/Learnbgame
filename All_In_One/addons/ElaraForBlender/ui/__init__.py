import bpy
import bl_ui

from . import world
from . import lamp
from . import material

def register():
    world.register()
    lamp.register()
    material.register()

def unregister():
    world.unregister()
    lamp.unregister()
    material.unregister()