import json, mathutils
from array import array

class dsf_geom_load (object):
  def __init__ (self):
    pass

  @classmethod
  def intern_geometry (self, jdata):
    """jdata is an entry within a geometry-library.
       returns an internal representation of the geometry.
      result contains:
        v=vertices, f=faces
        g=group-indices, m=material-indices,
        gm=group-names, m=material-names
    """
    id = jdata['id']
    v = array ('f')
    f = list ()
    m = array ('i')
    g = array ('i')
    for vertex in jdata['vertices']['values']:
      v.extend (vertex)
    group_list = jdata['polygon_groups']['values']
    mat_list = jdata['polygon_material_groups']['values']
    for polygon in jdata['polylist']['values']:
      (gidx, midx, verts) = (polygon[0], polygon[1], polygon[2:])
      f.append (verts)
      m.append (midx)
      g.append (gidx)
    return {
      'v': v,
      'g': g,
      'm': m,
      'f': f,
      'gm': group_list,
      'mm': mat_list
    }

  @classmethod
  def intern_geometry_library (self, jdata):
    """load all geometries from the geometry_library (must be a list).
       returns a list of all geometries.
    """
    return [self.intern_geometry (gitem) for gitem in jdata]

  @classmethod
  def load_node_lib_entry (self, jdata):
    """get a node library entry."""
    return jdata

  @classmethod
  def load_node_lib (self, jdata):
    return [self.load_node_lib_entry (jd) for jd in jdata]

  @classmethod
  def load_geometry (self, filename):
    """create a model from the json-data in jdata."""
    from . import dsf_io
    jdata = dsf_io.read_json_data (filename, encoding = 'latin1')
    geo_lib = self.intern_geometry_library (jdata['geometry_library'])
    if len (geo_lib) > 0:
      return geo_lib[0]
    else:
      return None

  @classmethod
  def load_file (self, filename):
    geom_data = self.load_geometry (filename)
    return geom_data
  genesis = '/images/winshare/dsdata4/data/DAZ 3D/Genesis/Base/Genesis.dsf'

