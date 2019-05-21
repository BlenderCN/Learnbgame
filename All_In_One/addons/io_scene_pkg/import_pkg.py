# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh, mathutils
import os, time, struct

import os.path as path
from mathutils import*
from io_scene_pkg.fvf import FVF

import io_scene_pkg.binary_helper as bin
import io_scene_pkg.import_helper as helper

pkg_path = None

######################################################
# IMPORT MAIN FILES
######################################################
def read_shaders_file(file, length, offset):
    shadertype_raw, shaders_per_paintjob = struct.unpack('2L', file.read(8))
    shader_type = "float"
    num_paintjobs = shadertype_raw
    # determine real shader type
    if shadertype_raw > 128:
        # byte shader. also we need to do some math
        num_paintjobs -= 128
        shader_type = "byte"

    # debug
    print('\tloading ' + str(shaders_per_paintjob) + ' shaders')

    for num in range(shaders_per_paintjob):
        # read in only ONE set of shaders. No need for more
        texture_name = bin.read_angel_string(file)
        if texture_name == '':
            # matte material
            texture_name = "age:notexture"
        
        # initialize these
        diffuse_color = None
        specular_color = None
        if shader_type == "float":
            diffuse_color = bin.read_color4f(file)
            file.seek(16,1) # seek past ""diffuse""
            specular_color = bin.read_color4f(file)
            file.seek(16,1) # seek past unused reflective color
        elif shader_type == "byte":
            diffuse_color = bin.read_color4d(file)
            file.seek(4,1) # seek past ""diffuse""            
            specular_color = bin.read_color4d(file)
        shininess = bin.read_float(file)

        # insert this data
        mtl = bpy.data.materials.get(str(num))
        if mtl is not None:
            # setup colors
            mtl.diffuse_color = (diffuse_color[0], diffuse_color[1], diffuse_color[2])
            mtl.specular_color = (specular_color[0], specular_color[1], specular_color[2])
            mtl.specular_intensity = 0.1
            mtl.raytrace_mirror.reflect_factor = shininess
            
            # have alpha?
            mtl_alpha_test = diffuse_color[3]
            if mtl_alpha_test < 1:
                mtl.use_transparency = True
                mtl.alpha = mtl_alpha_test
                
            # look for a texture
            tex_result = helper.try_load_texture(texture_name, pkg_path)
            if tex_result is not False:
                cTex = bpy.data.textures.new(texture_name, type='IMAGE')
                cTex.image = tex_result
                
                mtex = mtl.texture_slots.add()
                mtex.texture = cTex
                mtex.blend_type = 'MULTIPLY'
            mtl.name = texture_name

    # skip to the end of this FILE
    file.seek(length - (file.tell() - offset), 1)
    return


def read_xrefs(file):
    scn = bpy.context.scene
    # read xrefs
    num_xrefs = struct.unpack('L', file.read(4))[0]
    for num in range(num_xrefs):
        # skip matrix for now :(
        mtx = bin.read_matrix3x4(file)

        # read in xref name, and remove junk Angel Studios didn't null
        xref_name_bytes = bytearray(file.read(32))
        for b in range(len(xref_name_bytes)):
          if xref_name_bytes[b] > 126:
            xref_name_bytes[b] = 0
        
        # setup object
        xref_name = xref_name_bytes.decode("utf-8")
        ob = bpy.data.objects.new("xref:" + xref_name, None)
        
        # set matrix
        ob.matrix_basis = mtx
        
        ob.show_name = True
        ob.show_axis = True
        scn.objects.link(ob)


def read_geometry_file(file, meshname):
    scn = bpy.context.scene
    # add a mesh and link it to the scene
    me = bpy.data.meshes.new(meshname+'Mesh')
    ob = bpy.data.objects.new(meshname, me)

    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    
    # create layers for this object
    uv_layer = bm.loops.layers.uv.new()
    tex_layer = bm.faces.layers.tex.new()
    vc_layer = bm.loops.layers.color.new()
    
    # link to scene
    scn.objects.link(ob)
    scn.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # read geometry FILE data
    num_sections, num_vertices_tot, num_indices_tot, num_sections_dupe, fvf = struct.unpack('5L', file.read(20))

    # mesh data holders
    current_vert_offset = 0
    custom_normals = []
    ob_current_material = -1
    
    # read sections
    for num in range(num_sections):
        num_strips, strip_flags = struct.unpack('HH', file.read(4))
        
        # strip flags
        FLAG_compact_strips = ((strip_flags & (1 << 8)) != 0)
        
        # fvf flags
        FVF_FLAGS = FVF(fvf)

        shader_offset = 0
        if FLAG_compact_strips:
            shader_offset = struct.unpack('H', file.read(2))[0]
        else:
            shader_offset = struct.unpack('L', file.read(4))[0]
        
        # do we have this material?
        if bpy.data.materials.get(str(shader_offset)) is None:
            # we must make it!
            bpy.data.materials.new(name=str(shader_offset))
        
        ob.data.materials.append(bpy.data.materials.get(str(shader_offset)))
        ob_current_material += 1
        
        # read strip data
        if FLAG_compact_strips:
            current_vert_offset, section_normals = helper.read_compact_section(file, bm, FVF_FLAGS, num_strips, current_vert_offset, ob_current_material, uv_layer, vc_layer)
        else:
            current_vert_offset, section_normals = helper.read_full_section(file, bm, FVF_FLAGS, num_strips, current_vert_offset, ob_current_material, uv_layer, vc_layer)
        custom_normals += section_normals

    # apply bmesh data to object
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bm.free()
    
    # set custom normals (if applicable)
    if FVF_FLAGS.has_flag("D3DFVF_NORMAL"):
      me.normals_split_custom_set(custom_normals)
      me.use_auto_smooth = True
    else:
      me.calc_normals()
      
    # lastly, look for a MTX file. Don't grab an MTX for FNDR_M/L/VL though
    # as the FNDR lods are static and don't use the mtx
    if not ("fndr" in meshname.lower() and not "_h" in meshname.lower()):
      helper.find_matrix(meshname, ob, pkg_path)
      
    return

######################################################
# IMPORT
######################################################
def load_pkg(filepath,
             context,
             from_self = False):
    # set the PKG path, used for finding textures
    global pkg_path
    pkg_path = filepath

    print("importing PKG: %r..." % (filepath))

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading our pkg file
    pkg_version = file.read(4).decode("utf-8")
    if pkg_version != "PKG3" and pkg_version != "PKG2":
        print('\tFatal Error:  PKG file is wrong format : ' + pkg_version)
        file.close()
        return
        
    pkg_version_id = int(pkg_version[-1:])

    # read pkg FILE's
    pkg_size = path.getsize(filepath)
    while file.tell() != pkg_size:
        file_header = file.read(4).decode("utf-8")

        # check for an invalid header
        if file_header != "FILE":
            print('\tFatal Error: PKG file is corrupt, missing FILE header at ' + str(file.tell()))
            file.close()
            return

        # found a proper FILE header
        file_name = bin.read_angel_string(file)
        file_length = 0 if pkg_version_id == 2 else struct.unpack('L', file.read(4))[0]
        
        # Angel released a very small batch of corrupt PKG files
        # this is here just in case someone tries to import one
        if file_length == 0 and pkg_version_id == 3:
            raise Exception("Invalid PKG3 file : cannot have file length of 0")
            
        print('\t[' + str(round(time.clock() - time1, 3)) + '] processing : ' + file_name)
        if file_name == "shaders":
            # load shaders file
            read_shaders_file(file, file_length, file.tell())
        elif file_name == "offset":
            # skip over this, seems it's meta
            if pkg_version_id == 3:
               file.seek(file_length, 1)
            else:
              file.seek(12, 1)
        elif file_name == "xrefs":
            read_xrefs(file)
        else:
            # assume geometry
            read_geometry_file(file, file_name)
    # END READ PKG FILE DATA

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()


def load(operator,
         context,
         filepath="",
         ):
         
    load_pkg(filepath,
             context,
             )

    return {'FINISHED'}
