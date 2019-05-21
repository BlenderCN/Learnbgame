# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2018
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh, mathutils
import os, time, struct, math

######################################################
# IMPORT
######################################################
def read_indices(file, chunk_offset_list, chunk_vxcount_list, spans, output_index_list):
  for span in spans:
    chunk_idx = span[0]
    num_indices = span[1]
    
    index_type = 'B'if chunk_vxcount_list[chunk_idx] <= 255 else 'H'
    index_size = 1 if chunk_vxcount_list[chunk_idx] <= 255 else 2
    
    # read span
    for idx in range(num_indices):
      output_index_list.append(struct.unpack(index_type, file.read(index_size))[0] + chunk_offset_list[chunk_idx])
      
def import_cmf(path, context):
    # create a bmesh 
    scn = context.scene
    me = bpy.data.meshes.new("CMFImportMesh")
    ob = bpy.data.objects.new("CMFImport", me)
    
    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.new()
    
    # link to scene
    scn.objects.link(ob)
    scn.objects.active = ob
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # cmf vars
    read_vertices = []
    chunk_vertex_counts = []
    chunk_vertex_offsets = []
    triangle_indices = []
    quad_indices = []
    
    # read header
    file = open(path, "rb")
    header_magic = struct.unpack('L', file.read(4))[0]
    
    # verify header
    if header_magic != 1179012419:
      file.close()
      raise Exception("CMF header magic incorrect")

    # read version and flags
    version, flags = struct.unpack('BB', file.read(2))
    
    # verify version
    if version != 1:
      file.close()
      raise Exception("CMF version incorrect. Expected 1, got " + str(version))
    
    # read and apply mesh name
    mesh_name_len = struct.unpack('B', file.read(1))[0]
    mesh_name = file.read(mesh_name_len).decode("utf-8")
    ob.name = mesh_name
    
    # read chunk size
    chunk_size = struct.unpack('f', file.read(4))[0]
    
    # read bounds and chunk count
    bounds_min_x, bounds_min_y, bounds_min_z = struct.unpack('fff', file.read(12))
    chunk_count_x, chunk_count_y, chunk_count_z = struct.unpack('HHH', file.read(6))
    
    # read vertex and material count
    vertex_count, material_count = struct.unpack('HH', file.read(4))
    
    # read in chunks
    chunks = []
    for cx in range(chunk_count_x):
        for cy in range(chunk_count_y):
            for cz in range(chunk_count_z):
                # read vertex count
                chunk_vertex_count = struct.unpack('H', file.read(2))[0]

                # add vertex offset
                chunk_vertex_offsets.append(len(read_vertices))
                chunk_vertex_counts.append(chunk_vertex_count)
                
                # skip if not needed
                if chunk_vertex_count == 0:
                  continue
                
                # calculate origin
                chunk_origin_x = cx * chunk_size;
                chunk_origin_y = cy * chunk_size;
                chunk_origin_z = cz * chunk_size;
                
                # read in vertices
                for vert in range(chunk_vertex_count):
                  # read compact stuff
                  compact_xpos, compact_ypos, compact_zpos = struct.unpack('BBB', file.read(3))
                  compact_xnorm, compact_ynorm, compact_znorm = struct.unpack('bbb', file.read(3))
                  compact_u, compact_v = struct.unpack('HH', file.read(4))
                  
                  # init our vertex struct
                  vert_struct = dict.fromkeys(["co", "normal", "uv"])
                  
                  # unpack into the struct
                  vert_struct["co"] = (((compact_xpos / 255) * chunk_size) + bounds_min_x + chunk_origin_x, ((compact_ypos / 255) * chunk_size) + bounds_min_y + chunk_origin_y, ((compact_zpos / 255) * chunk_size) + bounds_min_z + chunk_origin_z)
                  vert_struct["normal"] = (compact_xnorm / 127, compact_ynorm / 127, compact_znorm / 127)
                  vert_struct["uv"] = (compact_u / 65535, compact_v / 65535)
                  
                  # add to verts list
                  read_vertices.append(vert_struct)

    # read face lists
    for mat in range(material_count):
        # create material
        mtl = bpy.data.materials.new(name=mesh_name + "_material_" + str(mat))
        ob.data.materials.append(mtl)
        
        # get total tri/quad counts & change counts
        num_tris, num_quads = struct.unpack('HH', file.read(4))
        tri_span_count, quad_span_count = struct.unpack('HH', file.read(4))
      
        # read spans
        tri_spans = []
        quad_spans = []
        
        for tri_span in range(tri_span_count):
          tri_spans.append(struct.unpack('HH', file.read(4)))
          
        for quad_span in range(quad_span_count):
          quad_spans.append(struct.unpack('HH', file.read(4)))
        
        # read indices
        mat_triangle_indices = []
        mat_quad_indices = []

        read_indices(file, chunk_vertex_offsets, chunk_vertex_counts, tri_spans, mat_triangle_indices)
        read_indices(file, chunk_vertex_offsets, chunk_vertex_counts, quad_spans, mat_quad_indices)
        
        # append to global lists
        triangle_indices.append(mat_triangle_indices)
        quad_indices.append(mat_quad_indices)
        
    # finally, push the data into a bmesh
    for vert in read_vertices:
      vtx = bm.verts.new(vert["co"])
      vtx.normal = mathutils.Vector(vert["normal"])
    
    # verify verts and read faces
    bm.verts.ensure_lookup_table()
    for mtl_idx in range(len(triangle_indices)):
      index_list = triangle_indices[mtl_idx]
      
      for i in range(0,len(index_list),3):
        indices = (bm.verts[index_list[i]], bm.verts[index_list[i + 1]], bm.verts[index_list[i + 2]])
        face = bm.faces.new(indices)
        face.smooth = True
        face.material_index = mtl_idx
        
        for uv_set_loop in range(3):
          face.loops[uv_set_loop][uv_layer].uv = read_vertices[index_list[uv_set_loop + i]]["uv"]
        
    for mtl_idx in range(len(quad_indices)):
      index_list = quad_indices[mtl_idx]
      
      for i in range(0,len(index_list),4):
        indices = (bm.verts[index_list[i]], bm.verts[index_list[i + 1]], bm.verts[index_list[i + 2]], bm.verts[index_list[i + 3]])
        face = bm.faces.new(indices)
        face.smooth = True
        face.material_index = mtl_idx
        
        for uv_set_loop in range(4):
          face.loops[uv_set_loop][uv_layer].uv = read_vertices[index_list[uv_set_loop + i]]["uv"]
      
    # free resources
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bm.free()
    file.close()
    return


def load(operator,
         context,
         filepath="",
         ):
         
    import_cmf(filepath,
             context,
             )

    return {'FINISHED'}
