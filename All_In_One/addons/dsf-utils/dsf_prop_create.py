import math, mathutils, collections, logging, json, os.path

from . import dsf_asset_create
from . import dsf_geom_create
from . import dsf_scene_create
from . import dsf_io

log = logging.getLogger ('prop-create')

class prop_exporter (object):
  """exporting props.
  """
  def __init__ (self, scene_path = None, data_path = None, scale = None,
                scene = None, base_dir = None):
    """initialize with two files to store the props in, and a scale
       value. If scale != 1, applies not only scale but also a reorientation
       on the exported geometry.
       scene is optional; if given, to-mesh is used to create meshes.
    """
    assert (scene_path is not None)
    assert (data_path is not None)
    assert (scale is not None)
    assert (base_dir is not None)
    self.scene_path = scene_path
    self.data_path = data_path
    self.scene = scene
    self.base_dir = base_dir
    if scale == 1:
      self.transform = mathutils.Matrix.Identity (3)
    else:
      log.info ("creating transform")
      self.transform = scale\
        * mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ').to_matrix ()
  @classmethod
  def create_data_ids (self, objs):
    """create data ids for the meshes of objs. returns a mapping
       obj->(geom-id, node-id).
    """
    id_dic = {}
    for obj in objs:
      geom_id = "%s-g" % (obj.name,)
      node_id = "%s-n" % (obj.name,)
      id_dic[obj] = (geom_id, node_id)
    return id_dic

  def create_geometry_libs (self, obj_map):
    """create the node-library and geometry-library for the objects.
       The objects are given as the keys of the obj_map.
       for each object in obj_map contains a tuple:
         (the id of the mesh, the id of the node)."""
    geom_creator = dsf_geom_create.geom_creator\
      (scene = self.scene, transform = self.transform)
    node_creator = dsf_geom_create.node_creator (transform = self.transform)
    geoms = []
    nodes = []
    for (obj, ids) in obj_map.items ():
      geom_id, node_id = ids
      geoms.append (geom_creator.create_geometry (obj, geom_id))
      nodes.append (node_creator.create_node (obj, node_id))
    jdata = {
      'node_library': nodes,
      'geometry_library': geoms
    }
    acreator = dsf_asset_create.asset_creator ()
    asset_info = acreator.create_asset_info (self.data_path)
    jdata['asset_info'] = asset_info
    return jdata

  def create_instances (self, obj_map):
    """create the scene-entries for objects.
       obj map contains a mapping obj->url.
    """
    nodes = []
    ncreator = dsf_scene_create.node_creator (transform = self.transform)
    for obj, urls in obj_map.items ():
      (geom_url, node_url) = urls
      scene_node = ncreator.create_node_instance (obj, geom_url, node_url)
      nodes.append (scene_node)
    acreator = dsf_asset_create.asset_creator ()
    asset_info = acreator.create_asset_info\
      (self.scene_path, type = "scene_subset")
    jdata = {
      'scene': { "nodes": nodes },
      'asset_info': asset_info,
    }
    return jdata

  def create_data_urls (self, id_dic):
    url_dic = {}
    for (obj, ids) in id_dic.items ():
      (geom_id, node_id) = ids
      geom_url = "%s#%s" % (self.data_path, geom_id)
      node_url = "%s#%s" % (self.data_path, node_id)
      url_dic[obj] = (geom_url, node_url)
    return url_dic

  def write_assets (self, assets, base_dir = None):
    """write the assets to a common base directory.
    """
    for asset in assets:
      path = asset['asset_info']['id']
      # force the path to be relative
      if os.path.isabs (path):
        abspath = os.path.join (base_dir, '.' + path)
      else:
        abspath = os.path.join (base_dir, path)
      dsf_io.write_json_data (asset, abspath, mkdir = True)

  def export_props (self, objs):
    """export the given list of objects.
    """
    # group the objects
    objs_grouped = dsf_geom_create.group_objects_by_mesh (objs)
    # choose a candidate for the geometry for each group.
    candic = {}
    for objs in objs_grouped:
      candic.update ({ obj: objs[0] for obj in objs })
    canset = set (candic.values ())
    log.info ("canset: %s", canset)
    # generate ids for the candidates
    id_dic = self.create_data_ids (canset)
    log.info ("id-dic: %s", id_dic)
    # create the data(geometry/nodes) for the candidates
    geom_jdata = self.create_geometry_libs (id_dic)
    # create the instance poses for each object (linking to their candidates)
    url_dic = self.create_data_urls (id_dic)
    jurl_dic = {
      obj: url_dic[candic[obj]] for obj in objs
    }
    scene_jdata = self.create_instances (jurl_dic)
    # write the data.
    assets = [geom_jdata, scene_jdata]
    self.write_assets (assets, self.base_dir)
    return
