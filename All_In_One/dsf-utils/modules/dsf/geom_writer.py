import bpy
import dsf.geom_create
import urllib.parse as urp

class geom_writer (object):
  """class to write geometry definitions.
     also writes uvs.
  """
  def __init__ (self, lib, scene, transform):
    """lib: used for creating actual files.
       scene: used for applying modifiers.
       transform: applied to vertices.
    """
    self.lib = lib
    self.scene = scene
    self.transform = transform

  def create_geom_file_content (self, obj, msh):
    """write an objects data as a mesh and return the json content.
       obj is required for the vertex groups and materials.
    """
    gcreator = dsf.geom_create.geom_creator (self.transform)
    geo_data = gcreator.create_geometry_and_uvs (obj, msh)
    geo = geo_data.geometry
    uvs = geo_data.uvs
    if uvs:
      geo['default_uv_set'] = '#' + urp.quote (uvs[0]['id'])
    data = {
      "asset_info": {},
      "geometry_library": [geo],
      "uv_set_library": uvs
    }
    return data

  def write_mesh_content (self, data):
    """write the geometry data to a file and return a
       url that references the geometry within.
    """
    geo_id = data['geometry_library'][0]['id']
    filepath = self.lib.write_geometry_data (geo_id, data)
    quoted_id = urp.quote (geo_id)
    quoted_filepath = urp.quote (filepath)
    url = "%s#%s" % (quoted_filepath, quoted_id)
    return url

  def write_meshes_for_objects (self, objs):
    """write mesh definitions for the given objects.
    """
    url_dic = {}
    groups = dsf.geom_create.group_objects_by_data (objs)
    for group in groups:
      obj = group[0]
      key = obj.data
      msh = obj.to_mesh (self.scene, True, 'PREVIEW')
      file_content = self.create_geom_file_content (obj, msh)
      url_dic[obj.data] = self.write_mesh_content (file_content)
    return url_dic
