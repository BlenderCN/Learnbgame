import bpy
import mathutils
import math
import urllib.parse as urp
from collections import namedtuple

vtree_entry = namedtuple ('vtree_entry', ['ancestor', 'matrix'])

def get_parent_in (obj, parents):
  """get an ancestor object of obj, that is a member of parents.
  """
  parent = obj.parent
  while parent:
    if parent in parents:
      return parent
    else:
      parent = parent.parent
  return None

def make_url (file, id):
  if file:
    file_url = urp.quote (file)
  else:
    file_url = ""
  if id:
    url = file_url + "#" + urp.quote (id)
  else:
    url = file_url
  return url

def make_vtree (objs):
  """create a ancestor-relationship for all objects in objs.
     Returns a dictionary object->{ancestor, transformation}
  """
  obj_set = set (objs)
  def walk_up_hierarchy (obj, matrix):
    while obj and obj not in obj_set:
      matrix = obj.matrix_local * matrix
      obj = obj.parent
    return vtree_entry (obj, matrix)
  anc_dic = {}
  for obj in obj_set:
    if obj not in anc_dic:
      matrix = obj.matrix_local
      entry = walk_up_hierarchy (obj.parent, matrix)
      anc_dic[obj] = entry
  return anc_dic

class scene_writer (object):
  """write scene subset files.
  """
  def __init__ (self, transform, objmap):
    """initialize with a transformation (blender-to-ds-space).
       objmap maps objects to their geometry-definitions.
    """
    self.transform = transform
    self.transform_inv = transform.inverted ()
    self.objmap = objmap

  def make_transformations (self, matrix):
    """create the transformation entries for the given matrix.
    """
    mat = self.transform * matrix * self.transform_inv
    euler = mat.to_euler ("XYZ")
    rotation = [
      { "id": axis,
        "current_value": getattr (euler, axis) * 180 / math.pi }
      for axis in ["x", "y", "z"]
    ]
    pos = mat.translation
    translation = [
      { "id": axis,
        "current_value": getattr (pos, axis) }
      for axis in ["x", "y", "z"]
    ]
    data = {
      "rotation": rotation,
      "translation": translation
    }
    return data

  def create_node_ref (self, obj, vtree):
    """get the node geometry instantiation for an object.
    """
    hier_entry = vtree[obj]
    data_name = self.objmap[obj.data]
    obj_id = obj.name
    data = {
      "url": data_name,
      "name": obj_id,
      "id": obj_id,
      "geometries": [
        {
          "url": data_name
        }
      ]
    }
    if hier_entry.ancestor:
      parent = hier_entry.ancestor
      data['parent'] = make_url (None, parent.name)
    data.update (self.make_transformations (hier_entry.matrix))
    return data

  def create_scene_file (self, objs):
    """create a scene-subset with the given objects.
    """
    vtree = make_vtree (objs)
    scene_nodes = [self.create_node_ref (obj, vtree) for obj in objs]
    data = {
      "asset_info": {},
      "scene": {
        "nodes": scene_nodes
      }
    }
    return data

