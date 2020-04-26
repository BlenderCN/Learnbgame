
def make_lookup (obj):
  """create a lookup function that takes a vertex index and
     returns the coordinate of that vertex in obj.
  """
  vertices = obj.data.vertices
  def get_co (index):
    return vertices[index].co
  return get_co

def make_vertex_group (obj, gname):
  """create a new, empty, named vertex group.
  """
  if gname in obj.vertex_groups:
    vg = obj.vertex_groups[gname]
    obj.vertex_groups.remove (vg)
  vg = obj.vertex_groups.new (name = gname)
  return vg

def paint_group (wmap, mshobj, gname):
  """paint vertices is the mesh data object mshobj.
     This creates or redefines the group named gname.
  """
  domain = wmap.get_domain ()
  num_verts = len (mshobj.data.vertices)
  vert_end = min (domain[1], num_verts)
  vert_beg = max (domain[0], 0)
  if vert_beg < vert_end:
    vg = make_vertex_group (mshobj, gname)
    for vert_idx in range (vert_beg, vert_end):
      weight = wmap.get_weight (vert_idx)
      if weight == 0:
        vg.remove ([vert_idx])
      else:
        vg.add (index = [vert_idx], weight = weight, type = 'REPLACE')
    return vg
