from . import mst_blender

bl_info = {
    "name": "Minimum Spanning Tree (MST)",
    "description": "Addon for creating minimum spanning trees",
    "category": "Add Curve",
    "author": "Patrick Herbers"
}

def register():
	mst_blender.register()

def unregister():
	mst_blender.unregister()