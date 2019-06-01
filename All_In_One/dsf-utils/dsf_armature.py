import operator, math, logging

log = logging.getLogger ('dsf-arm')

def get_channel_value (channel):
  """retrieve the initial value from a channel.
  """
  return float (channel['value'])
def get_vchannel_value (channels, names, default = None):
  """get the value tuple from a list of channels with the given names.
  """
  vdic = dict ()
  for channel in channels:
    channel_name = channel['id']
    channel_value = get_channel_value (channel)
    vdic[channel_name] = channel_value
  values = []
  for name in names:
    if name in vdic:
      values.append (vdic[name])
    else:
      values.append (default)
  return tuple (values)

class bone (object):
  """prepresent a bone from an armature.
  """
  def __init__ (self, jdata, arm):
    """initialize a bone from a json representation (an entry in a
       node-library section).
       arm is the armature object this bone belongs to.
    """
    self.jdata = jdata
    self.arm = arm

  def get_id (self):
    """return the internal name of the bone.
    """
    return self.jdata['id']
  def get_orientation (self):
    """return the rest orientation in xyz.
    """
    vchannel = self.jdata['orientation']
    return get_vchannel_value (vchannel, "xyz")
  def get_origin (self):
    """return the rest position.
    """
    vchannel = self.jdata['center_point']
    return get_vchannel_value (vchannel, "xyz")
  def get_rotation_order (self):
    """return the rotation order as a permutation of 'XYZ'.
    """
    return self.jdata['rotation_order']
  def get_length (self):
    """return an approximate length of the bone (only for display).
    """
    start = self.get_origin ()
    end = self.get_endpoint ()
    return math.sqrt (sum ([d ** 2 for d in map (operator.sub, start, end)]))
  def get_endpoint (self):
    """return the endpoint, to whatever it might be good for.
    """
    vchannel = self.jdata['end_point']
    return get_vchannel_value (vchannel, "xyz", 0)
  def get_parent (self):
    """return the canonical parent name of self.
    """
    if 'parent' in self.jdata:
      pname = self.jdata['parent']
      if pname.startswith ('#'):
        return pname[1:]
      else:
        return pname
    else:
      return None
  attr_mapping = {
    'id': get_id,
    'parent': get_parent,
    'origin': get_origin,
    'orientation': get_orientation,
    'rotation_order': get_rotation_order,
    'length': get_length,
    'endpoint': get_endpoint,
  }
  def get (self, name):
    """return the named attribute from self.
    """
    if name in self.attr_mapping:
      return self.attr_mapping[name] (self)
    else:
      raise KeyError ("unknown key '%s'" % (name))

class armature (object):
  """proxy object for an armature defined from a dsf file.
     provides essentially this functionality:
     - can get bones by name.
     - can identify roots.
  """
  def __init__ (self, jdata):
    """initialize the armature object with the json data of the node-library
       entry of the figures dsf data.
    """
    self.bone_dic = dict ()
    for node in jdata:
      # node is a node entry which corresponds more or less to a bone
      # in blender.
      dsf_bone = bone (node, self)
      self.bone_dic[dsf_bone.get ('id')] = dsf_bone
  def get_bone (self, name):
    """get a bone by its name.
    """
    return self.bone_dic[name]
  def get_children (self, parent):
    """return all bones that are children of the bone named parent.
       returns roots for parent = None.
    """
    log.info ("retrieve children of %s", parent)
    for (name, bone) in self.bone_dic.items ():
      if bone.get ('parent') == parent:
        yield bone
    return
