import os.path, itertools

# uv-data:
#   "layer-name": name of the blender uv-layer
#   "map-name": name of the blender uv-texture
#   "long-id": external id of the uv; must be unique within file.
#   "short-id": only the local id part (same as map-name?).
# geom-data:
#   "mesh-name": name of the mesh contained in the geometry-lib.
#   "node-name": name of the node contained in the geometry-lib.
#   +materials
# object-inst:
#   "dsf-name": name of the object in the scene-subset
#   "blender-name": name of the object in blender.
#   "geometry': geometry record to use (node + geometry).
#   "uvs": name of the uvs (first is default/active).
# modifier-data:
#

def create_object_ids (objs):
  """create an id for each object suitable for usage in a scene-subset."""
  obj_ids = { obj: obj.name for obj in objs }
  return obj_ids

def get_uvs_for_object (obj):
  """create a list of uv-information for the given object.
     obj is a blender object (must be a mesh).
     returns a map id->uvlib-entry
  """
  mesh_name = obj.data.name
  layer_names = [uvl.name for uvl in obj.data.uv_layers]
  map_names = [uvt.name for uvt in obj.data.uv_textures]
  assert (len (layer_names) == len (map_names))
  uvs = []
  for (uvl, uvt) in itertools.zip_longest (layer_names, map_names):
    uv_record = {
      'type': 'uv',
      'layer_name': uvl,
      'map_name': uvt,
      'long_id': "%s-%s" % (obj.data.name, uvt),
      'short_id': uvt
    }
    uvs.append (uv_record)
  active_name = obj.data.uv_textures.active.name
  uvs.sort (key = lambda u: u['map_name'] != active_name)
  return uvs

def get_geom_for_object (obj):
  """return information about the data for the object obj (must be mesh)."""
  geom_rec = {
    'type': 'geom',
    'mesh_name': obj.data.name + '-g',
    'node_name': obj.data.name + '-n',
  }
  return geom_rec

def get_instances (group_dic):
  insts = []
  for (cand, objs) in group_dic.items ():
    geom_rec = get_geom_for_object (cand)
    uvs_recs = get_uvs_for_object (cand)
    for obj in objs:
      inst_rec = {
        'dsf_name': obj.name,
        'blender_name': obj.name,
        'geometry': geom_rec,
        'uvs': uvs_recs,
      }
      insts.append (inst_rec)
  return insts
        
def group_objects_by_mesh (objs):
  """group the objects by their equivalent meshes.
     within each group objects are guaranteed to have the same mesh.
     returns a dictionary: distinguished-object => list of objects
  """
  # dic: list of all objects
  dic = {}
  for obj in objs:
    if obj.type == 'MESH':
      key = (obj.data, len (obj.vertex_groups), len (obj.modifiers))
      # objects that have the same mesh, same number of vertex groups
      # and same number of modifiers go into the same group.
      if key not in dic:
        dic[key] = [obj]
      else:
        dic[key].append (obj)
  obj_dic = {}
  for (k, v) in dic.items ():
    obj_dic[v[0]] = v
  return obj_dic

class planner (object):
  def __init__ (self, scenefile = 'test.duf', category = None, **kwarg):
    self.scenefile = scenefile
    self.category = category
    self.opts = kwarg
    if self.category is None:
      self.data_ldir = '/data'
    else:
      self.data_ldir = os.path.join ('/data', self.category)
    self.data_lpath = os.path.join (self.data_ldir, "test.dsf")
  def get_shape_keys (self, obj):
    """return the exportable shape keys of object."""
    if obj.data.shape_keys is None:
      return []
    else:
      return [kb.name for kb in obj.data.shape_keys.key_blocks]
  def get_uv_layers (self, obj):
    """return the exportable uv-names of object."""
    pass
  def get_material_names (self, obj):
    """return material names for the material indices of the object."""
    index = 0
    mats = []
    for mat in obj.data.materials:
      mats.append ("Material_%d" % (index))
    return mats
      
  def collect_object_data1 (self, obj):
    """return a dictionary id->info for a single object, keys:
       geoms, uvs, nodes, mods"""
    rec = {
      'geoms': [obj.name +'-g'],
      'nodes': [obj.name + '-n'],
      # uvs are indexed by number (names based on uv_texture)
      'uvs': [uvt.name for uvt in obj.data.uv_textures],
      # mods are indexed by key
      'mods': self.get_shape_keys (obj),
      # materials are indexed by number
      'mats': self.get_material_names (obj)
    }
    return rec
  def collect_object_data (self, objs):
    """get object data info for each object in objs (returns a dict)."""
    od_dic = {}
    for obj in objs:
      od_dic[obj] = self.collect_object_data1 (obj)
    return od_dic
  def plan (self, context):
    scene = context.scene
    objs = context.selected_objects
    # map a mesh-object to the list of object-instances:
    obj_group_dic = group_objects_by_mesh (objs)
    # determining file names:
    #   scene files (per object)
    #   geometry files (per mesh)
    #   modifier files (per mesh)
    #   uvset files (per mesh)
    return {
      'g': obj_group_dic,
      'dpath': self.data_lpath,
    }
