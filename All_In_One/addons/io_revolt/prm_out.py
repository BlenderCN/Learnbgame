"""
Name:    prm_out
Purpose: Exports Probe mesh files (.prm)

Description:
Meshes used for cars, game objects and track instances.

"""


if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(rvstruct)
    imp.reload(img_in)
    imp.reload(layers)

import os
import bpy
import bmesh
from mathutils import Color, Vector, Matrix
from . import common
from . import rvstruct
from . import img_in
from . import layers

from .common import *
from .layers import *


def export_file(filepath, scene):
    obj = scene.objects.active
    print("Exporting PRM for {}...".format(obj.name))
    meshes = []

    # Checks if other LoDs are present
    if "|q" in obj.data.name:
        dprint("LODs present.")
        meshes = get_all_lod(obj.data.name.split('|')[0])
        print([m.name for m in meshes])
    else:
        dprint("No LOD present.")
        meshes.append(obj.data)

    # Exports all meshes to the PRM file
    with open(filepath, "wb") as file:
        for me in meshes:
            print("Exporting mesh {} of {}".format(
                meshes.index(me), len(meshes)))
            # Exports the mesh as a PRM object
            prm = export_mesh(me, obj, scene, filepath)
            # Writes the PRM object to a file
            if prm:
                prm.write(file)


def export_mesh(me, obj, scene, filepath, world=None):
    """
    This exports an object to an rvstruct object. This is also used for .w
    meshes since they're pretty much the same as PRM. The only additions are
    boundaries and the per-face environment color.
    If an rvstruct world object is provided, this will return an rvstruct.mesh
    instead of an rvstruct.PRM.
    """
    props = scene.revolt
    # Creates a bmesh from the supplied mesh
    bm = bmesh.new()
    bm.from_mesh(me)

    if world is None:
        # Applies the object scale if enabled
        if props.apply_scale:
            bmesh.ops.scale(
                bm,
                vec=obj.scale,
                verts=bm.verts
            )
        # Applies the object rotation if enabled
        if props.apply_rotation:
            bmesh.ops.rotate(
                bm,
                cent=obj.location,
                matrix=obj.rotation_euler.to_matrix(),
                space=obj.matrix_basis,
                verts=bm.verts
            )
    else:

        # Removes the parent for exporting
        parent = obj.parent
        if parent:
            mat = obj.matrix_world.copy()
            old_mat = obj.matrix_basis.copy()
            obj.parent = None
            obj.matrix_world = mat

        spc = obj.matrix_basis
        bmesh.ops.scale(
            bm,
            vec=obj.scale,
            space=spc,
            verts=bm.verts
        )
        bmesh.ops.transform(
            bm,
            matrix=Matrix.Translation(obj.location),
            space=spc,
            verts=bm.verts
        )
        bmesh.ops.rotate(
            bm,
            cent=obj.location,
            matrix=obj.rotation_euler.to_matrix(),
            space=spc,
            verts=bm.verts
        )

        # Restores the parent relationship
        if parent and not obj.parent:
            obj.parent = parent
            obj.matrix_basis = old_mat

    if props.triangulate_ngons:
        num_ngons = triangulate_ngons(bm)
        if scene.revolt.triangulate_ngons > 0:
            print("Triangulated {} n-gons".format(num_ngons))

    # Gets layers
    uv_layer = bm.loops.layers.uv.get("UVMap")
    tex_layer = bm.faces.layers.tex.get("UVMap")
    vc_layer = (bm.loops.layers.color.get("Col") or 
                bm.loops.layers.color.new("Col"))
    env_layer = (bm.loops.layers.color.get("Env") or
                 bm.loops.layers.color.new("Env"))
    env_alpha_layer = (bm.faces.layers.float.get("EnvAlpha") or
                       bm.faces.layers.float.new("EnvAlpha"))
    va_layer = (bm.loops.layers.color.get("Alpha") or
                bm.loops.layers.color.new("Alpha"))
    texnum_layer = bm.faces.layers.int.get("Texture Number")
    type_layer = (bm.faces.layers.int.get("Type") or
                  bm.faces.layers.int.new("Type"))

    # Creates an empty PRM or Mesh structure
    if world is None:
        prm = rvstruct.PRM()
    else:
        prm = rvstruct.Mesh()

    prm.polygon_count = len(bm.faces)
    if prm.polygon_count > 32767:
        queue_error(
            "exporting mesh",
            "Too many polygons, try splitting up your mesh."
        )
        return None
    prm.vertex_count = len(bm.verts)
    if prm.vertex_count > 32767:
        queue_error(
            "exporting mesh",
            "Too many vertices, try splitting up your mesh."
        )
        return None
    for face in bm.faces:
        poly = rvstruct.Polygon()
        is_quad = len(face.verts) == 4

        poly.type = face[type_layer] & FACE_PROP_MASK

        # Sets the quad flag on the polygon
        if is_quad:
            poly.type |= FACE_QUAD

        # Gets the texture number from the integer layer if setting enabled
        # use_tex_num is the only way to achieve no texture
        if scene.revolt.use_tex_num and texnum_layer:
            poly.texture = face[texnum_layer]
        # Falls back to texture if not enabled or texnum layer not found
        elif tex_layer and face[tex_layer] and face[tex_layer].image:
            poly.texture = texture_to_int(face[tex_layer].image.name)
        else:
            poly.texture = -1

        # Sets vertex indices for the polygon
        vert_order = [2, 1, 0, 3] if not is_quad else [3, 2, 1, 0]
        for i in vert_order:
            if i < len(face.verts):
                poly.vertex_indices.append(face.verts[i].index)
            else:
                # Fills up unused indices with 0s
                poly.vertex_indices.append(0)

        # write the vertex colors
        for i in vert_order:
            if i < len(face.verts):
                # Gets color from the channel or falls back to a default value
                white = Color((1, 1, 1))
                color = face.loops[i][vc_layer] if vc_layer else white
                alpha = face.loops[i][va_layer] if va_layer else white
                col = rvstruct.Color(color=(int(color[0] * 255),
                                            int(color[1] * 255),
                                            int(color[2] * 255)),
                                     alpha=255-int(((alpha[0] + alpha[1] + alpha[2]) * 255)  / 3))
                poly.colors.append(col)
            else:
                # Writes white
                col = rvstruct.Color(color=(255, 255, 255), alpha=255)
                poly.colors.append(col)

        # Writes the UV
        for i in vert_order:
            if i < len(face.verts) and uv_layer:
                uv = face.loops[i][uv_layer].uv
                poly.uv.append(rvstruct.UV(uv=(uv[0], 1 - uv[1])))
            else:
                poly.uv.append(rvstruct.UV())

        if world is not None:
            if (poly.type & FACE_ENV):
                rgb = [int(c * 255) for c in get_average_vcol2([face], env_layer)]
                alpha = int(face[env_alpha_layer] * 255)
                col = rvstruct.Color(color=rgb, alpha=alpha)
                world.env_list.append(col)

        prm.polygons.append(poly)

    # export vertex positions and normals
    for vertex in bm.verts:
        coord = to_revolt_coord(vertex.co)
        normal = to_revolt_axis(vertex.normal)
        rvvert = rvstruct.Vertex()
        rvvert.position = rvstruct.Vector(data=coord)
        rvvert.normal = rvstruct.Vector(data=normal)
        prm.vertices.append(rvvert)

    # World extras
    if world is not None:
        rvbbox = rvbbox_from_bm(bm)
        center = center_from_rvbbox(rvbbox)
        radius = radius_from_bmesh(bm, center)
        prm.bound_ball_center = rvstruct.Vector(data=center)
        prm.bound_ball_radius = radius
        prm.bbox = rvstruct.BoundingBox(data=rvbbox)

    bm.free()
    return prm
