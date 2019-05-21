# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####
import bpy, bmesh
import struct

def get_raw_object_name(meshname):
    return meshname.upper().replace("_VL", "").replace("_L", "").replace("_M", "").replace("_H", "")

    
def get_material_offset(mtl):
    # :( hack
    coffset = 0
    for mat in bpy.data.materials:
        if mtl.name == mat.name:
            return coffset
        coffset += 1
    return -1


def get_used_materials(ob, modifiers):
    """search for used materials at object level"""
    used_materials = []
    
    # create temp mesh
    temp_mesh = ob.to_mesh(bpy.context.scene, modifiers, 'PREVIEW')
    
    # get bmesh
    bm = bmesh.new()
    bm.from_mesh(temp_mesh)
    
    # look for used materials
    for f in bm.faces:
      if not f.material_index in used_materials and f.material_index >= 0 and f.material_index < len(ob.material_slots) and ob.material_slots[f.material_index].material is not None:
        used_materials.append(f.material_index)
    
    # finish off
    bpy.data.meshes.remove(temp_mesh)
    bm.free()
    
    return used_materials
 
 
def bounds(obj):
    """get the bounds of an object"""
    local_coords = obj.bound_box[:]
    om = obj.matrix_world
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

    
def write_matrix(meshname, object, pkg_path):
    """write a *.mtx file"""
    mesh_name_parsed = get_raw_object_name(meshname)
    find_path = pkg_path[:-4] + '_' + mesh_name_parsed + ".mtx"
    # get bounds
    bnds = bounds(object)
    mtxfile = open(find_path, 'wb')
    mtxfile.write(struct.pack('ffffffffffff', bnds.x.min,
                                              bnds.z.min,
                                              bnds.y.min * -1,
                                              bnds.x.max,
                                              bnds.z.max,
                                              bnds.y.max * -1,
                                              # export location twice :/
                                              # since Blender seems to use that for Location and origin
                                              object.location.x,
                                              object.location.z,
                                              object.location.y * -1,
                                              object.location.x,
                                              object.location.z,
                                              object.location.y * -1))
    mtxfile.close()
    return

    
def prepare_materials(modifiers):
  """find used materials on a global level, and prepare a remap dictionary"""
  material_list =[]
  material_idx_list = []
  material_reorder = {}
  
  # prepare mat list
  for ob in bpy.data.objects:
    # don't export bound materials
    if ob.name.upper() == "BOUND":
      continue
    
    if ob.type == 'MESH' and len(ob.material_slots) > 0:
      # get idx's of used mats (local)
      idx_list = get_used_materials(ob, modifiers)
      
      # remap to global
      for x in range(len(idx_list)):
        idx_list[x] = get_material_offset(ob.material_slots[idx_list[x]].material)
        
      material_idx_list.extend(idx_list)
  
  material_idx_list.sort()
  
  # prepare remap dict & material list
  for x in range(len(material_idx_list)):
    # remap
    cidx = material_idx_list[x]
    if not cidx in material_reorder and cidx >= 0:
      material_reorder[cidx] = len(material_list)
      material_list.append(bpy.data.materials[cidx])
      
  return (material_list, material_reorder)
      
    
def prepare_mesh_data(mesh, material_index, tessface):
  """build mesh data for a PKG file"""
  # initialize lists for conversion
  cmtl_tris = []
  cmtl_indices = []
  cmtl_verts = []
  cmtl_uvs = []
  cmtl_cols = []
  
  # build the mesh data we need
  uv_layer = mesh.loops.layers.uv.active
  vc_layer = mesh.loops.layers.color.active

  # build tris that are in this material pass
  for lt in tessface:
      if lt[0].face.material_index == material_index:
        cmtl_tris.append(lt)

  # convert per face to per vertex indices
  index_remap_table = {}
  for lt in cmtl_tris:
      #funstuff :|
      indices = [-1, -1, -1]
      for x in range(3):
          l = lt[x]
          # prepare our hash entry
          uv_hash = "NOUV"
          col_hash = "NOCOL"
          pos_hash = str(l.vert.co)
          nrm_hash = str(l.vert.normal)
          if uv_layer is not None:
              uv_hash = str(l[uv_layer].uv)
          if vc_layer is not None:
              col_hash = str(l[vc_layer])
          index_hash = uv_hash + "|" + col_hash + "|" + pos_hash + "|" + nrm_hash

          # do we already have a vertex for this?
          if index_hash in index_remap_table:
              indices[x] = index_remap_table[index_hash]
          else:
              # get what our next index will be and append to remap table
              next_index = len(cmtl_verts)
              index_remap_table[index_hash] = next_index
              indices[x] = next_index

              # add neccessary data to remapping tables
              cmtl_verts.append(l.vert)

              if uv_layer is not None:
                  cmtl_uvs.append(l[uv_layer].uv)
              else:
                  cmtl_uvs.append((0,0))

              if vc_layer is not None:
                  cmtl_cols.append(l[vc_layer])
              else:
                  cmtl_cols.append((0,0,0,0))

      # finally append this triangle                
      cmtl_indices.append(indices)  
  
  # return mesh data :)
  return (cmtl_indices, cmtl_verts, cmtl_uvs, cmtl_cols)
  