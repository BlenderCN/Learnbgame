import json, logging, random, itertools
from array import array

log = logging.getLogger ('import_uvset')

#format:
# 'uvs' { 'count': int, 'values': [ (triples) ] }
# 'polygon_vertex_indices' [ (triple: fidx, vidx, uvidx) ]
# 'vertex_indices': [ int ]
# 'id': string
# assumption: vertex_indices contains indices into uvs-array for each vertex.
# @todo: check, if this is true.

class dsf_uvset (object):
  """class to get uv-coordinates from the dsf-data.
  """
  def __init__ (self, uvlib):
    """initialize with a given uv-library (a single item
       from the uv-set-library in the dsf.
    """
    self.name = uvlib['id']
    if 'polygon_vertex_indices' in uvlib:
      # stuff all border uvs into a map[face,vert->uv]
      self.separate = {
        (t[0], t[1]): t[2] for t in uvlib['polygon_vertex_indices']
      }
    else:
      self.separate = { }
    self.uvs = array\
        ('f', itertools.chain.from_iterable (uvlib['uvs']['values']))
  def get_name (self):
    """returns the name of the uvset.
    """
    return self.name
  def get_uvs (self, face, verts):
    """return a list of 2*len(verts) numbers representing
       the uv-coordinates of the given face.
    """
    uvlist = []
    for v in verts:
      if (face, v) in self.separate:
        uvidx = self.separate[(face, v)]
      else:
        uvidx = v
      uvlist.append (self.uvs[2*uvidx])
      uvlist.append (self.uvs[2*uvidx+1])
    return uvlist

class dsf_uvset_load (object):
  """class to load data for definition of uvsets.
  """
  @classmethod
  def read_dsf_data (self, filename):
    """load the given filename, check it for a uvset and return
       the contents in some form usable for the definition function.
    """
<<<<<<< HEAD
    from . import dsf_io
    jdata = dsf_io.read_json_data (filename)
=======
    import dsf.dsf_io
    jdata = dsf.dsf_io.read_json_data (filename)
>>>>>>> 64d1a8da577389e9f24c88afd6ababff31e37f34
    if 'uv_set_library' not in jdata:
      raise TypeError ('file does not contain a uv set library.')
    uvlibs = jdata['uv_set_library']
    if len (uvlibs) == 0:
      raise TypeError ('file does contain at least one uv set.')
    log.info ("found %d uv sets in %s", len (uvlibs), filename)
    return dsf_uvset (uvlibs[0])
