"""
Name:    rim_out
Purpose: Exports mirror plane files

Description:
Mirror planes are used to determine reflective surfaces.

"""

import bmesh

if "common" in locals():
    import imp
    imp.reload(common)
    imp.reload(rvstruct)

from . import common
from . import rvstruct

from .common import *

def export_file(filepath, scene):
    props = scene.revolt

    objs = [obj for obj in scene.objects if obj.revolt.is_mirror_plane]

    rim = rvstruct.RIM()

    for obj in objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Applies translation, rotation and scale
        apply_trs(obj, bm, transform=True)

        for face in bm.faces:

            mirror_plane = rvstruct.MirrorPlane()

            bm.faces.ensure_lookup_table()

            normal = rvstruct.Vector(data=to_revolt_axis(face.normal))
            normal.normalize()
            normal = normal * -1

            vec = rvstruct.Vector(data=to_revolt_coord(face.verts[0].co))
            distance = -normal.dot(vec)

            mirror_plane.plane.normal = normal
            mirror_plane.plane.distance = distance

            mirror_plane.bounding_box = rvstruct.BoundingBox(data=rvbbox_from_verts(face.verts))
            for vert in face.verts:
                mirror_plane.vertices.insert(0, rvstruct.Vector(data=to_revolt_coord(vert.co)))

            rim.mirror_planes.append(mirror_plane)
            rim.num_mirror_planes += 1

    dprint("Mirror planes:", rim.num_mirror_planes)

    f = open(filepath, "wb")

    rim.write(f)

    f.close()

    