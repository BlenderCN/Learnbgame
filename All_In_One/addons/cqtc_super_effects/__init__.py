bl_info = {
	"name": "CQTC Super Efectos",
	"description": "Plugin para hacer efectos varios",
	"location": "Properties > Render > Añadir Super Efectos",
	"category": "CosoQueTeCoso",
	"version": (1, 0),
	"blender": (2, 78, 0),
}

if "bpy" in locals():
	import imp
	imp.reload(blender_addon)
else:
	from . import blender_addon

def register():
	blender_addon.register()

def unregister():
	blender_addon.unregister()

if __name__ == "__main__":
	register()
