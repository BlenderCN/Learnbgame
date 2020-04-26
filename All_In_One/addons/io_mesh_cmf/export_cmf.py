# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2018
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh
import struct, math
from mathutils import Vector

# globals
CMF_CHUNK_SIZE = 1.275
CMF_COMPRESSION_ERROR_MARGIN = 0.00000001

######################################################
# EXPORT HELPERS
######################################################
def bounds(obj, local=False):

    local_coords = obj.bound_box[:]
    om = obj.matrix_world

    if not local:    
        worldify = lambda p: om * Vector(p[:]) 
        coords = [worldify(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])

    push_axis = []
    for (axis, _list) in zip('xyz', rotated):
        info = lambda: None
        info.max = max(_list)
        info.min = min(_list)
        info.distance = info.max - info.min
        push_axis.append(info)

    import collections

    originals = dict(zip(['x', 'y', 'z'], push_axis))

    o_details = collections.namedtuple('object_details', 'x y z')
    return o_details(**originals)

def make_flags_byte(has_verts, has_normals, has_uvs, has_colors):
    flags_byte = 0
    if has_verts: flags_byte |= 1
    if has_normals: flags_byte |= 2
    if has_uvs: flags_byte |= 4
    if has_colors: flags_byte |= 8
    return flags_byte

######################################################
# EXPORT
######################################################
def export_cmf(name, obj, scene, apply_modifiers, path):
    # get a bmesh 
    bm = bmesh.new()
    bm.from_mesh(obj.to_mesh(scene, apply_modifiers, 'PREVIEW'))
    bm.verts.ensure_lookup_table()
    
    # cmf vars
    vertex_chunk_map = [[-1, -1] for x in range(len(bm.verts))]
    chunk_vertex_counts = None
    current_chunk = 0
    uv_layer = bm.loops.layers.uv.active
    
    # write header
    file = open(path, "wb")
    file.write("CMFF".encode("ascii"))

    # version and flags
    file.write(struct.pack('B', 1))
    file.write(struct.pack('B', make_flags_byte(True, True, True, False)))
    
    # mesh name
    file.write(struct.pack('B', len(name)))
    file.write(name.encode("ascii"))
    
    #chunk size
    file.write(struct.pack('f', CMF_CHUNK_SIZE))
    
    # get bounds
    cmf_bounds = bounds(obj, True)
    
    # write bounds
    file.write(struct.pack('fff', cmf_bounds.x.min, cmf_bounds.y.min, cmf_bounds.z.min))
    
    # write chunk count
    num_nx_chunks = max(1, int(math.ceil(cmf_bounds.x.distance / CMF_CHUNK_SIZE)))
    num_ny_chunks = max(1, int(math.ceil(cmf_bounds.y.distance / CMF_CHUNK_SIZE)))
    num_nz_chunks = max(1, int(math.ceil(cmf_bounds.z.distance / CMF_CHUNK_SIZE)))
    file.write(struct.pack('HHH', num_nx_chunks, num_ny_chunks, num_nz_chunks))
    
    chunk_vertex_counts = [0] * (num_nx_chunks * num_ny_chunks * num_nz_chunks)
    
    # write vertex and material count
    file.write(struct.pack('HH',  len(bm.verts), len(obj.material_slots)))
    
    # fucking RIP nesting
    for cx in range(num_nx_chunks):
        for cy in range(num_ny_chunks):
            for cz in range(num_nz_chunks):
                # write 0 verts here for now
                vertex_count_ptr = file.tell()
                file.write(struct.pack('H', 0))
                
                # initialize a clusterfuck of variables
                num_verts_written = 0
                chunk_xmin = (cmf_bounds.x.min - CMF_COMPRESSION_ERROR_MARGIN) + (cx * CMF_CHUNK_SIZE)
                chunk_ymin = (cmf_bounds.y.min - CMF_COMPRESSION_ERROR_MARGIN) + (cy * CMF_CHUNK_SIZE)
                chunk_zmin = (cmf_bounds.z.min - CMF_COMPRESSION_ERROR_MARGIN) + (cz * CMF_CHUNK_SIZE)
                chunk_xmax = chunk_xmin + CMF_CHUNK_SIZE + CMF_COMPRESSION_ERROR_MARGIN
                chunk_ymax = chunk_ymin + CMF_CHUNK_SIZE + CMF_COMPRESSION_ERROR_MARGIN
                chunk_zmax = chunk_zmin + CMF_CHUNK_SIZE + CMF_COMPRESSION_ERROR_MARGIN
                
                # gather vertices
                for vxidx in range(len(bm.verts)):
                    vert = bm.verts[vxidx]
                    
                    # check if this vert is within bounds
                    if (vert.co.x < chunk_xmin or vert.co.y < chunk_ymin or vert.co.z < chunk_zmin
                    or vert.co.x > chunk_xmax or vert.co.y > chunk_ymax or vert.co.z > chunk_zmax):
                        continue
                    
                    # we want this!
                    # add it to the chunk map
                    if vertex_chunk_map[vxidx][0] >= 0:
                        raise Exception("ERROR: Trying to map a vertex twice :(")
                    vertex_chunk_map[vxidx][0] = current_chunk
                    vertex_chunk_map[vxidx][1] = num_verts_written
                    # print("mapped " + str(vxidx) + " to " + str(current_chunk))
                    
                    # write vertex data
                    file.write(struct.pack('B', int(((vert.co.x - chunk_xmin) / CMF_CHUNK_SIZE) * 255)))
                    file.write(struct.pack('B', int(((vert.co.y - chunk_ymin) / CMF_CHUNK_SIZE) * 255)))
                    file.write(struct.pack('B', int(((vert.co.z - chunk_zmin) / CMF_CHUNK_SIZE) * 255)))
                    
                    file.write(struct.pack('b', int(min(vert.normal.x, 1) * 127)))
                    file.write(struct.pack('b', int(min(vert.normal.y, 1) * 127)))
                    file.write(struct.pack('b', int(min(vert.normal.z, 1) * 127)))
                    
                    # UVS, pretty crappy code but it works
                    found_uv = False
                    if uv_layer is not None:
                        for face in bm.faces:
                            if found_uv:
                              break
                            for loop in face.loops:
                                if loop.vert.index == vert.index:
                                    uv_u = max(loop[uv_layer].uv[0], 0)
                                    uv_v = max(loop[uv_layer].uv[1], 0)
                                    file.write(struct.pack('H', int(min(uv_u * 65535, 65535))))
                                    file.write(struct.pack('H', int(min(uv_v * 65535, 65535))))
                                    found_uv = True
                                    break
                    if not found_uv:
                        file.write(struct.pack('H', 21827))
                        file.write(struct.pack('H', 21582))
                    
                    # increment
                    num_verts_written += 1
                
                # seek back and rewrite vert count
                file.seek(vertex_count_ptr, 0)
                file.write(struct.pack('H', num_verts_written))
                file.seek(0, 2)
                
                # after gather verts
                chunk_vertex_counts[current_chunk] = num_verts_written
                current_chunk += 1
                        
    
    # verify we've mapped everything to a chunk
    for vert_data in vertex_chunk_map:
        if vert_data[0] < 0 or vert_data[1] < 0:
            raise Exception("One or more vertices is not mapped to a cluster.")
    
    # gather faces
    bm.faces.ensure_lookup_table()
    face_indices_accomodated = {}
    face_lists = {}
    
    # initialize face_lists
    for mat in range(len(obj.material_slots)):
      face_lists[mat] = []
      
    # first gather faces by chunk index, this will create large spans if possible
    for chunk_idx in range(num_nx_chunks * num_ny_chunks * num_nz_chunks):
      for face in bm.faces:
          refcount = 0
          for loop in face.loops:
            if vertex_chunk_map[loop.vert.index][0] == chunk_idx:
              refcount += 1
          
          if refcount == len(face.loops):
            face_lists[face.material_index].append(face)   
            face_indices_accomodated[face.index] = True
    
    # gather the rest of the faces
    for face in bm.faces:
      if not face.index in face_indices_accomodated:
        face_lists[face.material_index].append(face)   
    
    # write faces
    for mat in range(len(obj.material_slots)):
        # gather quads and tris
        tri_list = []
        quad_list = []
        for face in face_lists[mat]:
            if len(face.loops) == 4: quad_list.append(face)
            if len(face.loops) == 3: tri_list.append(face)
        
        # write counts
        file.write(struct.pack('HH', len(tri_list), len(quad_list)))
        
        # determine chunk_changes for tris and quads
        tri_chunk_changes = []
        quad_chunk_changes = []
        tri_chunk_spans_temp = []
        quad_chunk_spans_temp = []
        
        current_tri_chunk = -1
        current_quad_chunk = -1
        last_tri_chunk_span  = 0
        last_quad_chunk_span = 0
        
        for face in tri_list:
            for loop in face.loops:
                vert_data = vertex_chunk_map[loop.vert.index]
                if current_tri_chunk != vert_data[0]:
                    current_tri_chunk = vert_data[0]
                    tri_chunk_changes.append([vert_data[0], 0])
                    tri_chunk_spans_temp.append(last_tri_chunk_span)
                    last_tri_chunk_span = 0
                last_tri_chunk_span += 1
        tri_chunk_spans_temp.append(last_tri_chunk_span)
                    
        for face in quad_list:
            for loop in face.loops:
                vert_data = vertex_chunk_map[loop.vert.index]
                if current_quad_chunk != vert_data[0]:
                    current_quad_chunk = vert_data[0]
                    quad_chunk_changes.append([vert_data[0], 0])
                    quad_chunk_spans_temp.append(last_quad_chunk_span)
                    last_quad_chunk_span = 0
                last_quad_chunk_span += 1
        quad_chunk_spans_temp.append(last_quad_chunk_span)
        
        # finalize chunk spans (TODO : find a better way to handle this??)
        for idx in range(len(tri_chunk_spans_temp) - 1):
            tri_chunk_changes[idx][1] = tri_chunk_spans_temp[idx+1]
        
        for idx in range(len(quad_chunk_spans_temp) - 1):
            quad_chunk_changes[idx][1] = quad_chunk_spans_temp[idx+1]
            
        # write change counts
        file.write(struct.pack('HH', len(tri_chunk_changes), len(quad_chunk_changes)))
        print("CHUNK CHANGES")
        print(len(tri_chunk_changes))
        print(len(quad_chunk_changes))
        
        # write tri, then quad chunk span lists
        for tri_change in tri_chunk_changes:
            file.write(struct.pack('HH', tri_change[0], tri_change[1]))

        for quad_change in quad_chunk_changes:
            file.write(struct.pack('HH', quad_change[0], quad_change[1]))
        
        # write tri and quad indices
        for face in tri_list:
            for loop in face.loops:
                vert_data = vertex_chunk_map[loop.vert.index]
                pack_type = 'B' if chunk_vertex_counts[vert_data[0]] <= 255 else 'H'
                
                # write the local chunk index
                file.write(struct.pack(pack_type, vert_data[1]))
                
        for face in quad_list:
            for loop in face.loops:
                vert_data = vertex_chunk_map[loop.vert.index]
                pack_type = 'B' if chunk_vertex_counts[vert_data[0]] <= 255 else 'H'
                
                # write the local chunk index
                file.write(struct.pack(pack_type, vert_data[1]))

    # free resources
    bm.free()
    file.close()
    return


def save(operator,
         context,
         filepath="",
         apply_modifiers=False
         ):
    
    
    # save CMF
    obj = bpy.context.scene.objects.active
    
    # check if we have a mesh
    if obj.type != 'MESH':
        print("Aborting, need MESH type.")
        return
        
    export_cmf(obj.name, obj, context.scene, apply_modifiers, filepath)

    return {'FINISHED'}
