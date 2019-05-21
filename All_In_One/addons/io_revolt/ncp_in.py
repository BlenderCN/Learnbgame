"""
Name:    ncp_in
Purpose: Imports Re-Volt collisision files (.ncp)

Description:
Imports collision files.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(rvstruct)

import bpy
import bmesh
import mathutils

from . import common
from . import rvstruct

from .rvstruct import NCP, Vector
from .common import *
from mathutils import Color


def intersect(d1, n1, d2, n2, d3, n3):
    """ Intersection of three planes
    "If three planes are each specified by a point x and a unit normal vec n":
    http://mathworld.wolfram.com/Plane-PlaneIntersection.html """
    det = n1.scalar(n2.cross(n3))

    # If det is too small, there is no intersection
    if abs(det) < 1e-100:
        return None

    # Returns intersection point
    return (d1 * n2.cross(n3) +
            d2 * n3.cross(n1) +
            d3 * n1.cross(n2)
            ) / det


def import_file(filepath, scene):
    props = scene.revolt

    with open(filepath, 'rb') as file:
        filename = os.path.basename(filepath)
        ncp = NCP(file)
        dprint("Imported NCP file.")

    filename = os.path.basename(filepath)
    # Creates a new mesh and bmesh
    me = bpy.data.meshes.new(filename)
    bm = bmesh.new()

    material_layer = bm.faces.layers.int.new("Material")
    type_layer = bm.faces.layers.int.new("NCPType")
    vc_layer = bm.loops.layers.color.new("NCPPreview")

    # Goes through all polyhedra and creates faces from them
    for poly in ncp.polyhedra:
        # distances
        ds = [-to_blender_scale(p.distance) for p in poly.planes]
        # normals
        ns = [Vector(data=to_blender_axis(p.normal)) for p in poly.planes]
        verts = []

        if poly.type & NCP_QUAD:
            verts.append(intersect(ds[0], ns[0], ds[1], ns[1], ds[2], ns[2]))
            verts.append(intersect(ds[0], ns[0], ds[2], ns[2], ds[3], ns[3]))
            verts.append(intersect(ds[0], ns[0], ds[3], ns[3], ds[4], ns[4]))
            verts.append(intersect(ds[0], ns[0], ds[4], ns[4], ds[1], ns[1]))
            face = (0, 3, 2, 1)
        else:
            verts.append(intersect(ds[0], ns[0], ds[1], ns[1], ds[2], ns[2]))
            verts.append(intersect(ds[0], ns[0], ds[2], ns[2], ds[3], ns[3]))
            verts.append(intersect(ds[0], ns[0], ds[3], ns[3], ds[1], ns[1]))
            face = (0, 2, 1)

        # Skips the poly if no intersection was found
        if None in verts:
            dprint('Skipping polyhedron (no intersection).')
            continue

        # Creates the bmverts and face
        bmverts = []
        for x in face:
            bmverts.append(bm.verts.new(verts[x]))
        face = bm.faces.new(bmverts)

        # Assigns the material and type
        face[material_layer] = poly.material
        face[type_layer] = poly.type

        # Sets preview colors
        for lnum in range(len(face.loops)):
            one = (1.0)
            # face.loops[lnum][vc_layer] = COLORS[poly.material] + (1.0, )
            face.loops[lnum][vc_layer] = COLORS[poly.material]

        bm.verts.ensure_lookup_table()

    # Converts the bmesh back to a mesh and frees resources
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()

    print("Creating Blender object for {}...".format(filename))
    ob = bpy.data.objects.new(filename, me)
    # ob.show_wire = True
    # ob.show_all_edges = True
    scene.objects.link(ob)
    scene.objects.active = ob
