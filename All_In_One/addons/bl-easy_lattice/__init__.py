import bpy

from . import easy_lattice

bl_info = {
            "name": "Easy Lattice",
            "author": "Kursad Karatas, Adam Wolski",
            "version": ( 0, 6 ),
            "blender": ( 2, 77, 0 ),
            "location": "View3D > Easy Lattice",
            "description": "Create a lattice for shape editing",
            "warning": "",
            "tracker_url": "https://bitbucket.org/kursad/blender_addons_easylattice/src",
            "category": "Mesh"
}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
