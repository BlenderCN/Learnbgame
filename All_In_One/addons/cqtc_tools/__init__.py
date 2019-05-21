bl_info = {
	"name": "CQTC Herramientas",
	"description": "Herramientas varias",
	"location": "Properties > Render > CQTC Herramientas",
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
