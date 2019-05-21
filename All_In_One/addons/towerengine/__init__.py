# coding=utf-8

bl_info = {
	"name":			"TowerEngine Support for Blender",
	"author":		"Florian Märkl",
	"blender":		(2, 7, 8),
	"version":		(0, 1, 0),
	"location":		"File > Import-Export",
	"description":	"Support for exporting TowerEngine Meshes and Scenes and Engine Viewport",
	"category":		"Game Engine"
}

__all__ = ["mesh_exporter", "scene_exporter", "ui", "props", "renderer"]

from . import mesh_exporter
from . import scene_exporter
from . import ui
from . import props
from . import renderer

def register():
	props.register()
	ui.register()
	mesh_exporter.register()
	scene_exporter.register()
	renderer.register()

def unregister():
	props.unregister()
	ui.unregister()
	mesh_exporter.unregister()
	scene_exporter.unregister()
	renderer.unregister()
	
if __name__ == "__main__":
	register()
