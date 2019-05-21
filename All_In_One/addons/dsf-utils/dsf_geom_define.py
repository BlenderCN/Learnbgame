import bpy, bmesh
import logging
from array import array

class dsf_geom_define (object):
  """utility class for inserting mesh data into blender.
  """
  log = logging.getLogger ('dsf_geom_define')

  @classmethod
  def create_vertex_groups (self, geom):
    """convert the face-groups to a map of vertex-groups.
    """
    gmap = dict ()
    for fidx, g in enumerate (geom['g']):
      fvs = geom['f'][fidx]
      if g not in gmap:
        gmap[g] = array ('i')
      if fvs[0] != 0:
        gmap[g].extend (fvs)
      else:
        gmap[g].extend (fvs)
    gnmap = dict ()
    for (gidx, gname) in enumerate (geom['gm']):
      if gidx in gmap:
        gnmap[gname] = gmap[gidx]
    return gnmap

  @classmethod
  def define_geom (self, name, geom):
    """load the vertices and faces into blender.
    """
    bmesh_dat = bmesh.new ()
    v = geom['v']
    # insert vertices. qmod.v is a list of triples (x,y,z), so there are a
    # third of them verts.
    n_verts = len (v) // 3
    for vert_idx in range (n_verts):
      vert_coords = v[3*vert_idx : 3*vert_idx+3]
      bmesh_dat.verts.new (vert_coords)
    # each face has exactly 4 vertex indices.
    f = geom['f']
    for (face_idx, face_vis) in enumerate (f):
      bmesh_dat.faces.new ([bmesh_dat.verts[vi] for vi in face_vis])
    # convert the bmesh to a mesh
    mesh_dat = bpy.data.meshes.new (name)
    mesh_obj = bpy.data.objects.new (name, mesh_dat)
    bmesh_dat.to_mesh (mesh_dat)
    bpy.context.scene.objects.link (mesh_obj)
    bpy.context.scene.update ()
    if 'id_path' in geom:
      mesh_obj['id_path'] = geom['id_path']
    bmesh_dat.free ()
    return mesh_obj

  @classmethod
  def define_materials (self, mesh, geom, use = True, **kwarg):
    """assign material indices based on the objects materials.
       This works only, if the object has no materials assigned to it.
       - use: if set, an existing material of the same
         name is used, otherwise a new material is created.
    """
    # material index is the index within the mesh, not the obj-file.
    # Two save material-indexes, assign materials only if there are
    # actual faces using them.
    m = geom['m']
    bmesh_dat = bmesh.new ()
    bmesh_dat.from_mesh (mesh.data)
    material_index = 0
    for (mat_id, mat_name) in enumerate (geom['mm']):
      # get a list of all faces with the given material id.
      fset = array ('i', filter (lambda idx: m[idx] == mat_id, range (len (m))))
      # only create a material if there are actually faces using it.
      # This is just by taste and should probably be user-selectable.
      if len (fset) > 0:
        if use and mat_name in bpy.data.materials:
          # re-use the existing material
          blender_mat = bpy.data.materials[mat_name]
        else:
          blender_mat = bpy.data.materials.new (mat_name)
        # if the material already exists, force the name by explicitly assigning
        # it. Otherwise the new material would get a new name with a suffix.
        # this should probably be configurable, but this default-behavior is
        # slightly more predictable (old materials get renamed).
        blender_mat.name = mat_name
        mesh.data.materials.append (blender_mat)
        for fidx in fset:
          bmesh_dat.faces[fidx].material_index = material_index
        material_index += 1
    # todo: find out if these updates are necessary.
    bmesh_dat.to_mesh (mesh.data)
    bmesh_dat.free ()
    mesh.data.update ()
    bpy.context.scene.update ()

  @classmethod
  def define_weight_by_name (self, mesh, group, verts):
    """weight-paint a mesh. group is given by name and created if not
       existant. otherwise the same as define_weight().
       Helper function for define_groups.
    """
    if group in mesh.vertex_groups:
      bgroup = mesh.vertex_groups[group]
    else:
      bgroup = mesh.vertex_groups.new (group)
    bgroup.add (verts, 1, 'REPLACE')

  @classmethod
  def define_groups (self, mesh, geom):
    """assign vertex groups based on the object face-groups.
    """
    # the model only contains a map containing group-sets and their ids.
    # So first split this into single groups.
    gnmap = self.create_vertex_groups (geom)
    for (gname, vidxs) in gnmap.items ():
      if len (vidxs) > 0:
        self.define_weight_by_name (mesh, gname, vidxs)

  @classmethod
  def define_model (self,  geom, use_mat = True, define_groups = True):
    """build a blender object from the model.
       kwarg use_mat: do not create material if already exists.
       returns the created object.
    """
    # insert the vertices and basic faces into the model.
    mesh_obj = self.define_geom ('Mesh', geom)
    if define_groups and 'g' in geom:
      self.log.info ("define groups")
      self.define_groups (mesh_obj, geom)
    if 'm' in geom:
      self.log.info ("define materials")
      self.define_materials (mesh_obj, geom, use = use_mat)
    mesh_obj.data.update ()
    bpy.context.scene.update ()
    return mesh_obj
