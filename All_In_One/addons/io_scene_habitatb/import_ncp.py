# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh, mathutils
import os
from mathutils import Vector, Matrix, Euler
import time, struct
from . import helpers
from .helpers import *
if 'bpy' in locals():
    import imp
    imp.reload(helpers)


export_filename = None

######################################################
# IMPORT MAIN FILES
######################################################
def load_ncp_file(file, matrix):
    scn = bpy.context.scene

    filepath = file.name
    name = os.path.basename(filepath)

    # add a mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, mesh)

    scn.objects.link(ob)
    scn.objects.active = ob

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    # Returns None if the file doesn't exist or if its filesize is 0 byte.
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return None
        
    # Creates bmesh, opens file and reads the number of polyhedrons.
    bm = bmesh.new()
    file = open(filepath, "rb")

    polyhedron_count = struct.unpack("<h", file.read(2))[0]
    material_layer = bm.faces.layers.int.new("revolt_material")
    
    # Loops through each polyhedron.
    for i in range(polyhedron_count):
        type, surface = struct.unpack("<ll", file.read(8))

        # Read some data.
        plane_data = [struct.unpack("<ffff", file.read(16)) for n in range(5)]
        bbox = struct.unpack("<ffffff", file.read(24))
        v = [Vector(plane[0:3]) for plane in plane_data]
        d = [plane[3] for plane in plane_data]
        
        # If first bit in type is 0 it's a tris otherwise it's a quad.
        plane_count = 3 if type % 2 == 0 else 4
        
        # Loops through each plane.
        vertices = []
        for n in range(plane_count):
            a = n + 1
            b = (n + 1) % plane_count + 1
            
            # calculating plane-plane intersection as explained by ali
            determinant = Matrix([v[0], v[a], v[b]]).determinant()
            if determinant != 0:
                pos = determinant**-1 * (-d[0] * v[a].cross(v[b]) + -d[a] * v[b].cross(v[0]) + -d[b] * v[0].cross(v[a]))
                vert = bm.verts.new(Vector(pos) * matrix)
                vertices.insert(0, vert)
        
        # createa a face if tehre are 3 or more vertices.
        if len(vertices) >= 3:
            face = bm.faces.new(vertices)
            face[material_layer] = surface
            
    file.close();
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(mesh)
    bm.free()

    # set new object type to ncp
    ob.revolt.rv_type = "NCP"
    return ob

      

######################################################
# IMPORT
######################################################
def load_ncp(filepath, context, matrix):

    print("importing ncp: %r..." % (filepath))

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading our pkg file
    load_ncp_file(file, matrix)

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()


def load(operator, filepath, context, matrix):

    global export_filename
    export_filename = filepath
    
    load_ncp(filepath,
             context,
             matrix)

    return {'FINISHED'}
