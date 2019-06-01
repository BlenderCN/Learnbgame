# get a shapekey
class dsf_skey_fetch (object):
  """utility class to get morph data from an object.
  """
  def __init__ (self):
    pass

  @classmethod
  def convert (self, obj):
    """collect the required data from the shape-key.
    """
    skey = obj.active_shape_key
    if skey is None:
      raise Exception ("no active shape-key")
    key_data = skey.data
    rel_data = skey.relative_key.data
    deltas = [key_data[i].co - rel_data[i].co for i in range (len (key_data))]
    skey_data = {
      'min': skey.slider_min,
      'max': skey.slider_max,
      'id': skey.name,
      'vertex_count': len (skey.data),
      'deltas': {
        i: v.to_tuple ()
        for i, v in enumerate (deltas) if v.length > 0
      },
      'id_path': self.get_id_path (obj)
    }
    return skey_data

  @classmethod
  def get_id_path (self, obj):
    """retrieve a stored path from the obj.
    """
    if 'id_path' in obj:
      return obj['id_path']
    else:
      raise Exception ("could not find property 'id_path' in object")

