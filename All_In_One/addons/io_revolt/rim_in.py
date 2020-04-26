"""
Name:    rim_in
Purpose: Imports mirror plane files

Description:
Mirror planes are used to determine reflective surfaces.

"""

if "common" in locals():
    import imp
    imp.reload(common)
    imp.reload(rvstruct)

from . import common
from . import rvstruct

from .common import *

def import_file(filepath, scene):
    props = scene.revolt

    with open(filepath, "rb") as f:
        rim = rvstruct.RIM(f)

    dprint("Mirror planes:", rim.num_mirror_planes)

    filename = filepath.rsplit(os.sep, 1)[1]

    if rim.num_mirror_planes == 0 or rim.mirror_planes == []:
        queue_error(
            "importing mirror file", 
            "File contains 0 mirror planes"
        )
        return

    for mirror_plane in rim.mirror_planes:
        me = bpy.data.meshes.new(filename)
        bm = bmesh.new()

        verts = []
        for v in mirror_plane.vertices[::-1]:
            verts.append(bm.verts.new(to_blender_coord(v)))
            bm.verts.ensure_lookup_table()

        # Creates a face from the reversed list of vertices
        bm.faces.new(verts)

        bm.to_mesh(me)
        bm.free()

        ob = bpy.data.objects.new(filename, me)
        ob.revolt.is_mirror_plane = True
        scene.objects.link(ob)

    # flag, plane and BBox information will be ignored

    scene.objects.active = ob