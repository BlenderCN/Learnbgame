
bl_info = {
    "name": "BlenderSFM",
    "author": "Apoorva Joshi",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "location": "View3D > Add > Mesh",
    "description": "Construct point cloud from photographs",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    imp.reload(PointCloud)
else:
    from blenderSFM import PointCloud

import bpy
import sys


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
