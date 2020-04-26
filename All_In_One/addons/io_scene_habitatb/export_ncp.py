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
from math import sqrt, pow, ceil, floor, pi
import bpy, bmesh, mathutils
from mathutils import Matrix
from . import helpers, const



######################################################
# EXPORT MAIN FILES
######################################################

def save_ncp_file(file, ob, matrix):
    scn = bpy.context.scene

    bm = bmesh.new() # big mesh for all ncp objects

    # merge all objects into one mesh
    for obj in scn.objects:
        if obj.data and (obj.revolt.rv_type == "NCP" or obj.revolt.export_as_ncp == True):
            tempmesh = bpy.data.meshes.new("temp") # create a temporary mesh
            bmtemp = bmesh.new() # temporary mesh to add to the bm
            bmtemp.from_mesh(obj.data) # fill temp mesh with object data
            
            # apply scale, position and rotation
            bmesh.ops.scale(bm, vec=ob.scale, space=ob.matrix_basis, verts=bm.verts)
            bmesh.ops.transform(bm, matrix=Matrix.Translation(ob.location), space=ob.matrix_world, verts=bm.verts)
            bmesh.ops.rotate(bm, cent=ob.location, matrix=ob.rotation_euler.to_matrix(), space=ob.matrix_world, verts=bm.verts)
            
            bmtemp.to_mesh(tempmesh) # save temp bmesh into mesh
            bmtemp.free()
            bm.from_mesh(tempmesh) # add temp mesh to the big mesh

    file.write(struct.pack("<h", len(bm.faces)))
    material_layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    
    print(file.name)
    
    for face in bm.faces:
        # write face type (tris / quad) and material.
        file.write(struct.pack("<ll", 0 if len(face.verts) < 4 else 1, face[material_layer]))
        
        # write the floor plane
        normal = face.normal * matrix
        normal.length = 1
        point = face.verts[0].co * matrix
        distance = -point.x * normal.x - point.y * normal.y - point.z * normal.z
        file.write(struct.pack("<4f", normal[0], normal[1], normal[2], distance))
        
        # write each cutting plane.
        vertex_count = len(face.verts[:4])
        for i in range(vertex_count - 1, -1, -1):
            a = face.verts[i].co * matrix
            b = face.verts[(i + 1) % vertex_count].co * matrix
            normal2 = normal.cross(a - b)
            normal2.length = 1
            distance = -a.x * normal2.x - a.y * normal2.y - a.z * normal2.z
            file.write(struct.pack("<4f", normal2[0], normal2[1], normal2[2], distance))
            
        # write the rest of the cutting planes if the number of edges is lower than four.
        for i in range(4 - vertex_count):
            file.write(struct.pack("<4f", 0, 0, 0, 0))
        
        # write bounding box.
        verts = [v.co * matrix for v in face.verts]
        min_point = [min([v.x for v in verts]), min([v.y for v in verts]), min([v.z for v in verts])]
        max_point = [max([v.x for v in verts]), max([v.y for v in verts]), max([v.z for v in verts])]
        file.write(struct.pack("<6f", min_point[0], max_point[0], min_point[1], max_point[1], min_point[2], max_point[2]))
        
    # write the lookup grid.
    grid_size = 1024
    x_coords = [(v.co * matrix).x for v in bm.verts]
    z_coords = [(v.co * matrix).z for v in bm.verts]
    min_x = min(x_coords)
    max_x = max(x_coords)
    min_z = min(z_coords)
    max_z = max(z_coords)
    x_size = ceil((max_x - min_x) / grid_size)
    z_size = ceil((max_z - min_z) / grid_size)
    lookup_table = [[] for n in range(x_size * z_size)]
    
    for face in bm.faces:
        verts = [v.co * matrix for v in face.verts]
        from_x = floor((min([v.x for v in verts]) - min_x) / grid_size)
        to_x = ceil((max([v.x for v in verts]) - min_x) / grid_size)
        from_z = floor((min([v.z for v in verts]) - min_z) / grid_size)
        to_z = ceil((max([v.z for v in verts]) - min_z) / grid_size)
        for x in range(from_x, to_x):
            for z in range(from_z, to_z):
                lookup_table[x + z * x_size].append(face.index)
    
    file.write(struct.pack("<5f", min_x, min_z, x_size, z_size, grid_size))
    for list in lookup_table:
        file.write(struct.pack("<l", len(list)))
        for index in list:
            file.write(struct.pack("<l", index))
        
    file.close()
    bm.free()



######################################################
# EXPORT
######################################################
def save_ncp(filepath, context, matrix):
             
    time1 = time.clock()

    ob = bpy.context.active_object
    print("exporting ncp: {} as {}...".format(str(ob), filepath))

    # write the actual data
    file = open(filepath, 'wb')
    save_ncp_file(file, ob, matrix)
    file.close()
     
    # ncp export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator, filepath, context, matrix):
    
    # save ncp file
    save_ncp(filepath,
             context, matrix
             )

    return {'FINISHED'}