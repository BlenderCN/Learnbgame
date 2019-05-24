bl_info = {
	"name": "Panda3D Real Time Engine",
	"author": "Daniel Stokes",
	"blender": (2, 71, 0),
	"location": "Info header, render engine menu",
	"description": "Panda3D integration",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": 'TESTING',
	"category": "Learnbgame",
}


import bpy

from . import engine
print(dir(engine))


def register():
	bpy.utils.register_module(__name__)


def unregister():
	bpy.utils.unregister_module(__name__)
