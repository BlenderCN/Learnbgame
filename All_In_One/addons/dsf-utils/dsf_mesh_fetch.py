
class dsf_mesh_fetch (object):
  """fetch the export data for a geometry from a mesh object.
  """
  def __init__ (self):
    pass
  @classmethod
  def build_group_list (self, msh):
    """build a mapping from polygon to group index for the given mesh.
       If the mesh has no groups a default group is created.
    """
    pass
  @classmethod
  def build_mat_list (self, msh):
    """build a mapping from polygon to material index for the given mesh.
       if the mesh has no materials a default material is assigned.
    """
    mats = [p.material_index for p in msh.data.polygons]
    return mats

  @classmethod
  def get_polygon_vidxs (self, msh):
    """return a list of lists containing vertex indices (one for each polygon).
    """
    pvidxs = []
    for polygon in msh.polygons:
      pvidxs.append (list (polygon.vertices))
    return pvidxs

  @classmethod
  def convert_polylist (self, msh, groups, mats):
    """create the polylist data block from the mesh given the
       mapping of groups and the mapping of materials.
    """
    pass

  @classmethod
  def convert_vertices (self, msh):
    """get the list of vertex coordinates from the mesh.
       returns a vertices-object.
    """
    values = []
    for vertex in msh.vertices:
      values.append ([vertex.co.x, vertex.co.y, vertex.co.z])
    count = len (values)
    return {
      'count': count,
      'values': values
    }

  @classmethod
  def convert (self, obj):
    """get the data from a blender object (which must be a mesh)
       and generate intermediate data.
    """
    msh = obj.data
    vertices = self.convert_vertices (msh)
    return vertices
