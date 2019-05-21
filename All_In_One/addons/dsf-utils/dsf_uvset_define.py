import itertools

def create_uv_layer (msh, name):
  """create a new uv layer and return its name.
  """
  uvt = msh.uv_textures.new (name = name)
  uvl = msh.uv_layers[-1]
  return uvl

def fill_uv_coords (uvlib, msh, uvl):
  """uvlib is an object that returns uv-coordinates.
     msh is a mesh data object.
     uvl is a uv-layer data object.
     uvl must have the same length as mesh.faces.
  """
  uv_data = uvl.data
  uvoff = 0
  for mshpoly in msh.polygons:
    # mshpoly.vertices contains the list of vertices, like [0, 1, 2, 3, 4]
    # get the vertices from the uvlib
    uvcoords = uvlib.get_uvs (mshpoly.index, mshpoly.vertices)
    for uv_rel_idx in range (len (mshpoly.vertices)):
      uv_pair = uvcoords[2*uv_rel_idx:2*uv_rel_idx+2]
      uv_abs_idx = uvoff + uv_rel_idx
      uv_data[uv_abs_idx].uv = uv_pair
    uvoff += len (mshpoly.vertices)
  msh.update ()

class dsf_uvset_define (object):
  """class to define uvsets; mainly the define_uvset function is exported.
  """
  @classmethod
  def define_uvset (self, obj, uvlib):
    """uvlib is the object returned by the loader.
       uvlib must implement get_name() and get_uvs (face, verts).
    """
    msh = obj.data
    uvl = create_uv_layer (msh, uvlib.get_name ())
    fill_uv_coords (uvlib, msh, uvl)
