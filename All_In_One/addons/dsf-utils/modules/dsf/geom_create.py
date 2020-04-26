import itertools, copy, logging
from collections import namedtuple
import math, mathutils

geometry_data = namedtuple ('geometry_data', ['geometry', 'uvs'])

log = logging.getLogger ('geom-create')

class uv_creator (object):
  """create uv library entries.
  """
  def __init__ (self):
    pass
  def create_uvlayer (self, msh, uv_layer):
    """create a single uv-library entry for the given uv-layer.
       The id, name and label are the name of the uv-layer.
    """
    uv_data = uv_layer.data
    # list of all polygon/vertex pairs, should be the same size as the
    # upv_pairs := list of all (uv_idx, (poly_idx, vert_idx))
    pvs = [[(poly.index, vi) for vi in poly.vertices] for poly in msh.polygons]
    upv_pairs = list (enumerate (itertools.chain (*pvs)))
    assert (len (upv_pairs) == len (uv_data))
    # sort by vertex number
    upv_pairs.sort (key = lambda x: x[1][1])
    uvs = []
    tail = []
    d = {}
    for (v, upvs) in itertools.groupby (upv_pairs, lambda x: x[1][1]):
      # generate a list for the vertex v, containing each adjacent face
      # along with the corresponding uv coordinate:
      v_uvs = [(uv_data[u].uv, p) for (u, (p, v)) in upvs]
      # sort the list by uv-coordinates
      v_uvs.sort (key = lambda x: x[0])
      # create a mapping giving the list of polygons for a uv-coordinate
      # uv_p contains a list of tuples: (uv-coord, list of polygons)
      uv_p = [(uv, [p for (uv, p) in ups])
              for (uv, ups) in itertools.groupby (v_uvs, lambda x: x[0])]
      # sort this list by the number of polygons
      uv_p.sort (key = lambda x: len (x[1]))
      (last_uv, last_ps) = uv_p.pop ()
      uvs.append (tuple (last_uv))
      tail.extend (itertools.chain
                   (*[[(uv, (v, p)) for p in ps] for (uv, ps) in uv_p]))
    assert (len (uvs) == len (msh.vertices))
    polygon_vertex_indices = []
    uv_index = len (uvs)
    for (uv, uvps) in itertools.groupby (tail, lambda x: x[0]):
      uvs.append (tuple (uv))
      for (uv, (v, p)) in uvps:
        polygon_vertex_indices.append ((p, v, uv_index))
      uv_index += 1
    uv_lib = {
      'id': uv_layer.name,
      'label': uv_layer.name,
      'vertex_count': len (msh.vertices),
      'uvs': {
        'count': len (uvs),
        'values': uvs,
      },
      'polygon_vertex_indices': polygon_vertex_indices,
    }
    return uv_lib
  def create_uvs (self, obj, msh):
    # get all layers
    layers = list (msh.uv_layers)
    # make the active layer the first one.
    layers.sort (key = lambda x: x != msh.uv_layers.active)
    # create uv lib entries for the uv layers.
    jdata = []
    for uvl in layers:
      uvlib = self.create_uvlayer (msh, uvl)
      jdata.append (uvlib)
    return jdata

class geom_data_creator (object):
  """helper class to create geometry data for a single mesh.
  """
  def __init__ (self, obj, msh, transform):
    self.obj = obj
    self.msh = msh
    self.transform = transform
  def get_vertices (self):
    """get the vertices object from the mesh.
    """
    vs = [tuple (self.transform * v.co) for v in self.msh.vertices]
    data = {
      'count': len (vs),
      'values': vs
    }
    return data
  def get_face_groups (self):
    """returns two objects: the polygon_groups-block of the dsf
       and a list containing the group-indices (one for each face).
       obj is the mesh object (which holds the groups).
    """
    obj = self.obj
    msh = self.msh
    def get_common_group (vidxs):
      """get the smallest group index that is a common group index of
         all vertexes whose indices are given in vidxs.
         If there is no common index, return 0.
      """
      # list of group-objects, one for each vertex
      groups = [msh.vertices[vidx].groups for vidx in vidxs]
      # create a list of lists of group-indices
      group_idxs = [[vg.group for vg in vgroups] for vgroups in groups]
      # build the intersection of all groups
      intersection = set (group_idxs.pop ())
      for group in group_idxs:
        intersection.intersection_update (group)
      if len (intersection) == 0:
        return 0
      else:
        return min (intersection)
    # pgroups is the list of group indices to use, one for each face.
    pgroups = [get_common_group (poly.vertices) for poly in msh.polygons]
    if len (obj.vertex_groups) == 0:
      group_names = ['default']
    else:
      group_names = [group.name for group in obj.vertex_groups]
    jdata = {
      'count': len (obj.vertex_groups),
      'values': group_names
    }
    return (jdata, pgroups)
  def get_face_materials (self):
    """returns two objects: the polygon_material_groups as an object
       and a list of material indices, one for each face.
    """
    obj = self.obj
    msh = self.msh
    def get_material_name (material):
      """get a sensible name for the material
      """
      if material is None:
        return 'default'
      else:
        return material.name
    mgroups = [poly.material_index for poly in msh.polygons]
    if len (msh.materials) == 0:
      material_names = ['default']
    else:
      material_names = [get_material_name (mat) for mat in msh.materials]
    jdata = {
      'count': len (material_names),
      'values': material_names
    }
    return (jdata, mgroups)
  def create_polygon_data (self):
    """create the polygon vertex list. Returns a list of lists
       where each element is a polygon (a list of vertex indices).
    """
    msh = self.msh
    # todo: the winding of the vertices with respect to the normal must be ccw.
    poly_vidx_list = [list (poly.vertices) for poly in msh.polygons]
    return poly_vidx_list
  def create_face_data (self):
    """create the polygon data of the object.
       this returns a dictionary with the keys:
       polygon_groups, polygon_material_groups, polylist, vertices
    """
    obj = self.obj
    msh = self.msh
    (pg_jdata, pg_idxs) = self.get_face_groups ()
    (pm_jdata, pm_idxs) = self.get_face_materials ()
    assert len (pg_idxs) == len (pm_idxs) == len (msh.polygons)
    def create_poly_tuple (g, m, vs):
      return [g, m] + vs
    # poly_vidx_list contains the actual polygon data.
    # Each element of poly_vidx_list is a list of vertex-indices.
    poly_vidx_list = self.create_polygon_data ()
    # enhance each polygon with an index to the group and material.
    gm_poly_vidx_list = list (map (create_poly_tuple,
                                   pg_idxs, pm_idxs, poly_vidx_list))
    polylist_jdata ={
      'count': len (gm_poly_vidx_list),
      'values': gm_poly_vidx_list
    }
    vertices = self.get_vertices ()
    jdata = {
      'vertices': vertices,
      'polygon_groups': pg_jdata,
      'polygon_material_groups': pm_jdata,
      'polylist': polylist_jdata
    }
    return jdata
  def create_uvs (self):
    """convert the uv-layers of the object to a list of uv-library entries.
       the id of the entries is the name of the uv-layer.
       the active uv-layer always comes first.
    """
    uvcreator = uv_creator ()
    return uvcreator.create_uvs (self.obj, self.msh)
  def create_geometry (self):
    """create a geometry_library entry from a blender object.
       The mesh name is used for the id of the geometry.
    """
    obj = self.obj
    jdata = self.create_face_data ()
    jdata['id'] = obj.data.name
    # required contents:
    # id, name, type, vertices, polygon_groups, polygon_material_groups,
    # polylist, default_uv_set (if available),
    # extra (optional): geometry_channels (for subdivision)
    return jdata

class geom_creator (object):
  """class to create dsf-geometry items from meshes.
  """
  def __init__ (self, transform = None, **kwarg):
    """using transform to transform vertices.
    """
    self.transform = transform or mathutils.Matrix.Identity (3)
  def create_geometry_and_uvs (self, obj, msh):
    """create the geometry library entry and a list of uv-set-library entries.
       Returns a geometry_data object.
    """
    gdcreator = geom_data_creator (obj, msh, self.transform)
    geometry_entry = gdcreator.create_geometry ()
    uvset_entries = gdcreator.create_uvs ()
    return geometry_data (geometry_entry, uvset_entries)

def group_objects_by_data (objs):
  """group the objects by their data.
     within each group objects are guaranteed to have the same data.
     returns a list of lists of objects.
  """
  dic = {}
  for obj in objs:
    key = (obj.data, len (obj.vertex_groups), len (obj.modifiers))
    # objects that have the same mesh, same number of vertex groups
    # and same number of modifiers go into the same group.
    dic.setdefault (key, []).append (obj)
  return list (dic.values ())

