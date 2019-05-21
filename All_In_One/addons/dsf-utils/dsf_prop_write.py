import logging, json, os

log = logging.getLogger ('write-prop-dsf')

from . import dsf_linker
from . import dsf_geom_create
from . import dsf_scene_create
from . import dsf_asset_create
from . import dsf_io

def create_geometry_content (obj, linker, filename, **kwarg):
  """create the geometry content for a single object.
     creates a node_library, geometry_library
  """
  geom_creator = dsf_geom_create.geom_creator (linker, **kwarg)
  node_creator = dsf_geom_create.node_creator (linker, **kwarg)
  linker.push_context (filename)
  geom_jdata = geom_creator.create_geometry (obj)
  node_jdata = node_creator.create_node (obj)
  linker.pop_context ()
  return {
    'node_library': [ node_jdata ],
    'geometry_library': [ geom_jdata ]
  }

def create_node_instance_content (obj, linker, filename, **kwarg):
  """create a scene node instance for the given object.
  """
  scene_creator = dsf_scene_create.node_creator (linker, **kwarg)
  linker.push_context (filename)
  scene_jdata = scene_creator.create_node_instance (obj)
  linker.pop_context ()
  return scene_jdata

def create_geometry_data (objs, linker, filename, **kwarg):
  """create the content for the data file of each object.
     contains the node_library and geometry_library.
  """
  contents = []
  for obj in objs:
    contents.append (create_geometry_content (obj, linker, filename, **kwarg))
  return contents

def create_scene_content (objs, linker, filename, **kwarg):
  """create the content of the scene file as a list of entries
     into the scene's node-list.
  """
  contents = []
  for obj in objs:
    contents.append\
      (create_node_instance_content (obj, linker, filename, **kwarg))
  return contents

def create_export_assets (export_dic):
  scene_by_id = {}
  data_by_id = {}
  print ("export_dic: ", export_dic)
  for ((type, obj), id) in export_dic.items ():
    if type == 'geometry':
      data_by_id.setdefault (id, []).append (obj)
    elif type == 'instance':
      scene_by_id.setdefault (id, []).append (obj)
  return (data_by_id, scene_by_id)

def create_json_asset (assets, linker, id):
  """merge multiple *_libraries into one and gives them a common id.
     It simply joins the entries of the given list of dictionaries.
  """
  asset_creator = dsf_asset_create.asset_creator (linker)
  joined = {}
  for asset in assets:
    for lib_key, lib_ents in asset.items ():
      assert (lib_key.endswith ("_library"))
      entries = joined.setdefault (lib_key, [])
      entries.extend (lib_ents)
  joined['asset_info'] = asset_creator.create_asset_info (id, type = 'prop')
  joined['file_version'] = '0.6.0.0'
  return joined

def create_json_scene (nodes, linker, id):
  """create a json scene containing the given nodes.
  """
  asset_creator = dsf_asset_create.asset_creator (linker)
  jdata = {
    'asset_info': asset_creator.create_asset_info (id, type = 'scene_subset'),
    'file_version': '0.6.0.0',
    'scene': {
      'nodes': nodes
    }
  }
  return jdata

def create_assets (export_dic, **kwarg):
  """create assets for the given objects.
     export_dic lists the objects that are to be exported, its keys are
     composed of tuples (type, blender-object), values is the dataid.
     kwargs can contain additional properties for exporting.
  """
  export_opts = kwarg
  data_ids, scene_ids = create_export_assets (export_dic)
  linker = dsf_linker.linker ()
  # 1 create assets for datafiles and scene
  d_jdata = {}
  for (dataid, objs) in data_ids.items ():
    entry = create_geometry_data (objs, linker, dataid, **kwarg)
    merged_entries = create_json_asset (entry, linker, dataid)
    d_jdata[dataid] = merged_entries
  # 2 create the scene files
  s_jdata = {}
  for (sceneid, objs) in scene_ids.items ():
    nodes = create_scene_content (objs, linker, sceneid, **kwarg)
    s_jdata[sceneid] = create_json_scene (nodes, linker, sceneid)
  # 3 link assets
  linker.resolve ()
  # 4 write files
  log.info ("data: %s", str (d_jdata))
  log.info ("scene: %s", str (s_jdata))
  s_jdata.update (d_jdata)
  return s_jdata

def write_assets (asset_dic, libdir):
  """write assets to the lib-directory.
  """
  for id, data in asset_dic.items ():
    filepath = os.path.join (libdir, os.path.normpath ('.' + id))
    log.info ("writing: %s", filepath)
    dsf_io.write_json_data (data, filepath, mkdir = True)
