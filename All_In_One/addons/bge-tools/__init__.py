import bpy
from . import ops

bl_info = {
	"name": "Raco's BGE Tools",
	"author": "Raf Colson",
	"version": (0, 0, 1),
	"blender": (2, 79, 2),
	"location": "SpaceBar Search -> BGE-Tools: UV Scroll / UV Transform / LOD Sections",
	"description": "Tools for the Blender Game Engine",
	"warning": "Requires Blender version prior to 2.8",
	"wiki_url": "https://github.com/rafcolson/bge-tools/wiki",
	"tracker_url": "https://github.com/rafcolson/bge-tools/issues",
	"category": "Learnbgame",
}

def register():
	for m in ops.modules:
		m.register()
		
def unregister():
	for m in ops.modules:
		m.unregister()
		