# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import time, struct, math
import os.path as path

import bpy, bmesh
from mathutils import Color, Vector, Matrix
from . import helpers, const

######################################################
# EXPORT MAIN FILES
######################################################

def save_prm_file(file, ob, matrix):
    scn = bpy.context.scene

    # get mesh name
    mesh = ob.data

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # transform
    bmesh.ops.scale(bm, vec=ob.scale, space=ob.matrix_basis, verts=bm.verts)


    # bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    # write amount of polygons and vertices
    poly_count = len(bm.faces)
    vertex_count = len(bm.verts)
    file.write(struct.pack("<HH", poly_count, vertex_count))

    # get layers
    uv_layer = bm.loops.layers.uv.active
    vc_layer = bm.loops.layers.color.get("color")
    va_layer = bm.loops.layers.color.get("alpha")
    flag_layer = bm.faces.layers.int.get("flags") or bm.faces.layers.int.new("flags")
    texture_layer = bm.faces.layers.int.get("texture") or bm.faces.layers.int.new("texture")
    texturefile_layer = bm.faces.layers.tex.active or bm.faces.layers.tex.new("uv")


    # go through all polygons
    for face in bm.faces:
        # get flags
        # figure out whether the face is quad
        is_quad = len(face.verts) > 3

        # set the quad-flag if the poly is quadratic
        if is_quad:
            face[flag_layer] |= const.FACE_QUAD

        # write the flags
        flags = face[flag_layer] if flag_layer else 0
        file.write(struct.pack("<H", flags))

        # write the texture
        if face[texturefile_layer].image and not ob.revolt.use_tex_num:
            texnum = helpers.texture_to_int(face[texturefile_layer].image.name)
        elif texture_layer:
            texnum = face[texture_layer]
        else:
            texnum = -1

        file.write(struct.pack("<h", texnum))

        # get vertex order
        vert_order = [2, 1, 0, 3] if not is_quad else [3, 2, 1, 0]

        # write indices
        for i in vert_order:
            if i < len(face.verts):
                file.write(struct.pack("<H", face.verts[i].index))
            else:
                file.write(struct.pack("<H", 0))

        # write the vertex colors
        for i in vert_order:
            if i < len(face.verts):
                # get color from the channel or fall back to a default valueCA
                color = face.loops[i][vc_layer] if vc_layer else Color((1, 1, 1))
                alpha = face.loops[i][va_layer] if va_layer else Color((1, 1, 1))
                file.write(struct.pack("<BBBB", int(color.b * 255), int(color.g * 255), int(color.r * 255), int((alpha.v) * 255)))
            else:
                file.write(struct.pack("<BBBB", 1, 1, 1, 1)) # write opaque white as default

        # write the uv
        for i in vert_order:
            if i < len(face.verts) and uv_layer:
                uv = face.loops[i][uv_layer].uv
                file.write(struct.pack("<ff", uv[0], 1 - uv[1]))
            else:
                file.write(struct.pack("<ff", 0, 0))

    # export vertex positions and normals
    for vertex in bm.verts:
        coord = Vector((vertex.co[0], vertex.co[1], vertex.co[2])) * matrix
        normal = Vector((vertex.normal[0], -vertex.normal[2], vertex.normal[1]))
        file.write(struct.pack("<fff", *coord))
        file.write(struct.pack("<fff", *normal))

    # free the bmesh
    bm.free()



######################################################
# EXPORT
######################################################
def save_prm(filepath, context, matrix):

    time1 = time.clock()

    ob = bpy.context.active_object
    print("exporting PRM: {} as {}...".format(str(ob), filepath))

    # write the actual data
    file = open(filepath, 'wb')
    save_prm_file(file, ob, matrix)
    file.close()

    # prm export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator, filepath, context, matrix):

    # save PRM file
    save_prm(filepath, context, matrix)

    return {'FINISHED'}
