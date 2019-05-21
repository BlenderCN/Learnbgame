import math, mathutils

class node_creator (object):
  """create node instances for scene content.
  """
  def __init__ (self, transform = None):
    """initialize with an object to resolve references.
       an optional transformation is applied to translations.
    """
    if transform is None:
      self.transform = mathutils.Matrix.Identity (3)
    else:
      self.transform = transform
  def get_pose_rot (self, obj):
    """return xyz for the rotation of obj.
    """
    (x,y,z) = obj.rotation_euler
    return [
      { "id" : "x", "current_value" : math.degrees (x) },
      { "id" : "y", "current_value" : math.degrees (y) },
      { "id" : "z", "current_value" : math.degrees (z) }
    ]
  def get_pose_trans (self, obj):
    """get the xyz translation of the object.
    """
    (x,y,z) = self.transform * obj.location
    return [
      { "id" : "x", "current_value" : x },
      { "id" : "y", "current_value" : y },
      { "id" : "z", "current_value" : z }
    ]
  def get_orientation (self, obj):
    """get the orientation of the object.
    """
    (ex, ey, ez) = self.transform.to_euler ()
    return [
      { "id" : "x", "current_value" : math.degrees (ex) },
      { "id" : "y", "current_value" : math.degrees (ey) },
      { "id" : "z", "current_value" : math.degrees (ez) }
    ]
  def get_pose_general_scale (self, obj):
    """get the general part of the scale.
    """
    return {
      "id" : "general_scale",
      "current_value" : 1
    }
  def get_pose_scale (self, obj):
    """get the axis-specific scale of the object.
    """
    (x,y,z) = obj.scale
    return [
      { "id" : "x", "current_value" : x },
      { "id" : "y", "current_value" : y },
      { "id" : "z", "current_value" : z }
    ]
  def get_geometries (self, obj):
    """get the geometries section of a scene (contains only references).
       generate those tags:
       { id, url, name, label, type }
    """
    jdata = {
      'name': obj.name,
      'label': obj.name,
      'type': 'polygon_mesh',
      'id': obj.name + "-g",
    }
    return jdata
  def create_node_instance (self, obj, gurl, nurl):
    """create an instantiated node for the object.
       So that this will work correctly, the node should have
       a default orientation and axes named x,y,z.
       the id the node is given is the object name.
    """
    geom_reference = self.get_geometries (obj)
    geom_reference['url'] = gurl
    jdata = {
      'name': obj.name,
      'label': obj.name,
      'geometries': [ geom_reference ],
      'rotation': self.get_pose_rot (obj),
      'translation': self.get_pose_trans (obj),
      'orientation': self.get_orientation (obj),
      'scale': self.get_pose_scale (obj),
      'general_scale': self.get_pose_general_scale (obj),
      'id': obj.name,
      'url': nurl
    }
    return jdata
