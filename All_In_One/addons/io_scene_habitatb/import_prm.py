# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy, struct, bmesh, re, os, glob
import time, struct
from mathutils import Vector, Color
 
from . import const, parameters

export_filename = None

######################################################
# IMPORT MAIN FILES
######################################################
def load_prm_file(file, matrix, texfile):
    path = file.name.split(os.sep)
    scn = bpy.context.scene
    
    # get mesh name
    mesh_name = bpy.path.basename(export_filename)
    
    # add a mesh and link it to the scene
    me = bpy.data.meshes.new(mesh_name)
    ob = bpy.data.objects.new(mesh_name, me)

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(me)

    # create layers and set names
    uv_layer = bm.loops.layers.uv.new("uv")    
    vc_layer = bm.loops.layers.color.new("color")
    va_layer = bm.loops.layers.color.new("alpha")
    flag_layer = bm.faces.layers.int.new("flags")
    texture_layer = bm.faces.layers.int.new("texture")
    texturefile_layer = bm.faces.layers.tex.active or bm.faces.layers.tex.new("uv")
    
    scn.objects.link(ob)
    scn.objects.active = ob
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # read prm header
    poly_count, vertex_count = struct.unpack('<HH', file.read(4))
    poly_offset = file.tell()
    
    # skip polys real quick
    file.seek(60 * poly_count, 1)
    
    # read vertices
    print("reading verts at " + str(file.tell()))
    for vert in range(vertex_count):
        location = struct.unpack('fff', file.read(12))
        normal = struct.unpack('fff', file.read(12))

        # create vertices multiplied by rv matrix
        bm.verts.new(Vector((location[0], location[1], location[2])) * matrix)
    
    # ensure lookup table before continuing
    bm.verts.ensure_lookup_table()
    
    # read faces
    file.seek(poly_offset, 0)
    for poly in range(poly_count):
        flags, texture = struct.unpack('<Hh', file.read(4))
        indices = struct.unpack('<HHHH', file.read(8))

        # read colors and uvs
        colors = struct.unpack('<BBBBBBBBBBBBBBBB', file.read(16))
        uvs = struct.unpack('ffffffff', file.read(32))

        # check if we have a quad
        is_quad = (flags & const.FACE_QUAD)
        num_loops = 4 if is_quad else 3

        # is this quad actually a triangle?
        if is_quad and len(set(indices)) == 3:
            is_quad = False

        # check if it's a valid face
        if len(set(indices)) < 2:
            continue

        # faces are reversed also
        try:
            face = None
            if is_quad:
                face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]], bm.verts[indices[3]]))
            else:
                face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]])) 
              
            # set layer properties
            for loop in range(num_loops):
                # set uvs
                uv = (uvs[loop * 2], 1 - uvs[loop * 2 + 1])
                face.loops[loop][uv_layer].uv = uv
              
                # set colors
                color_idx = loop * 4
                color_b = float(colors[color_idx]) / 255
                color_g = float(colors[color_idx + 1]) / 255
                color_r = float(colors[color_idx + 2]) / 255
                color_a = 1.0 - (float(colors[color_idx + 3]) / 255)
              
                # apply colors and alpha to layers
                face.loops[loop][vc_layer] = Color((color_r, color_g, color_b))
                face.loops[loop][va_layer] = Color((color_a, color_a, color_a))
              
            # setup face
            face[flag_layer] = flags
            face[texture_layer] = texture
            if texfile:
                face[texturefile_layer].image = texfile
            else:
                texture_name = path[-2].lower() + chr(97 + texture) + ".bmp"
                image = bpy.data.images.get(texture_name)
                if not image:
                    texture_path = os.sep.join([*path[:-1], texture_name])
                    if os.path.exists(texture_path):
                        image = bpy.data.images.load(texture_path)
                    else:
                        print("Texture not found: ", texture_path, "Number", texture)
                face[texturefile_layer].image = image


            face.smooth = True
            face.normal_flip()

        except ValueError as e:
            print(e)
            # set existing face as double-sided
            #existing_face = bm.faces.get([bm.verts[i] for i in (indices if is_quad else indices[:3])])
            #existing_face[flag_layer] |= 0x002
      
    # calculate normals
    bm.normal_update()
    
    # free resources
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bm.free()

    # set new object type to mesh
    ob.revolt.rv_type = "MESH"

    # if it's a car, mark it to not use the texture number from level textures
    if texfile:
        ob.revolt.use_tex_num = True
    

      

######################################################
# IMPORT
######################################################
def load_prm(filepath, context, matrix, texture):

    print("importing PRM: %r..." % (filepath))

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading the prm file
    load_prm_file(file, matrix, texture)

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()

# for cars
def load_texture(filepath):
    path = filepath.split(os.sep)
    path = os.sep.join(path[:-1])

    # check if it's a car
    parampath = os.sep.join([path, "parameters.txt"])
    if os.path.exists(parampath):
        params = parameters.read_parameters(parampath)
        if '/' in params["tpage"]: 
            img = params["tpage"].split("/")[-1]
        elif '\\' in params["tpage"]:
            img = params["tpage"].split("\\")[-1]
        texture_path = os.sep.join([path, img])
        image = bpy.data.images.load(texture_path)
        image.use_fake_user = True
        return image
    else:
        return None

def load(operator, filepath, context, matrix):

    global export_filename
    export_filename = filepath
    
    texture = load_texture(filepath)

    load_prm(filepath, context, matrix, texture)

    return {'FINISHED'}
