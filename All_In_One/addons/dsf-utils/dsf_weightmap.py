import logging
from . import dsf_io
from .rig import weight_map

log = logging.getLogger ('dsf-wm')

class weightmap (object):
  """contains a single weightmap input data as it occurs in the dsf.
  """
  def __init__ (self, jdata):
    """initialize a weightmap from the object containing the map data.
    """
    idxs = []
    wgts = []
    if jdata['count'] == 0:
      self.map = weight_map.weight_map ()
    else:
      for [idx, wgt] in jdata['values']:
        idxs.append (int (idx))
        wgts.append (float (wgt))
      self.map = weight_map.table_map (idxs, wgts)
  def get_paint_map (self):
    """returns the paintable map representing self.
    """
    return self.map

class joint_map (object):
  """aggregate the different weight maps of a single joint. Contains
     only the maps that i understand (ie no bulges).
  """
  def __init__ (self, jdata):
    """initialize the joints weights from the entry in a skin-binding.
       use the scale-weights and local-weights sections.
    """
    self.maps = dict ()
    if 'scale_weights' in jdata:
      self.maps['s'] = weightmap (jdata['scale_weights'])
    if 'local_weights' in jdata:
      local_weights = jdata['local_weights']
      for axis in ['x', 'y', 'z']:
        if axis in local_weights:
          self.maps[axis] = weightmap (local_weights[axis])
    # new with DS4.5: scale_weights/local_weights may be replaced by
    # a single weightmap named node_weights.
    if 'node_weights' in jdata:
      log.info ("detected new style generic map.")
      self.maps['n'] = weightmap (jdata['node_weights'])
  def is_generic (self):
    """return True, if this is a generic map only.
    """
    return self.maps.keys () == ['n']
  def get (self, key):
    """get a stored map. currently supported keys:
       's' (for scale), 'x', 'y', 'z'.
       returns None if the requested map is not there.
    """
    return self.maps.get (key)
  def get_paint_map (self, key):
    """return a paintable map for the given axis.
       Returns a normalized paintable weight map.
    """
    if key in self.maps:
      log.info ("joint_map: key %s found.", key)
      paintable_map = self.maps[key].get_paint_map ()
      log.info ("paintable_map: %s", paintable_map)
      return paintable_map
    else:
      return None
  def get_paint_map_mix (self, keys):
    """for the given list of keys, create a paintable map that mixes
       the given keys using a simple average.
    """
    pmaps = []
    for key in keys:
      pmap = self.get_paint_map (key)
      if pmap is not None:
        pmaps.append (pmap)
    if len (pmaps) == 0:
      return None
    elif len (pmaps) == 1:
      return pmaps[0]
    else:
      avg_map = weight_map.average_map (pmaps)
      return avg_map
  def get_paint_map_groups (self, groups):
    """get a set of paint maps for this joint. groups is a list where
       each member is a set of map-axes. Returns a dictionary where the
       keys are the groups. if groups is None or empty, returns only a
       generic group.
    """
    group_dic = dict ()
    if groups is None or len (groups) == 0:
      log.warn ("todo: nyi")
    for group in groups:
      pmap = self.get_paint_map_mix (group)
      if pmap is not None:
        group_dic[group] = pmap
    return group_dic

  def collect_paint_maps (self):
    """return a dictionary containing every paintable map of self.
       key is simply the axis. No averaging is done.
    """
    return {
      axis: pmap.get_paint_map ()
      for (axis, pmap) in self.maps.items ()
    }

class skin (object):
  """collect all weightmaps for a figure.
  """
  def __init__ (self, jdata):
    """scan the jdata which is the skin-node for weight-maps and make them
       retrievable by id.
    """
    self.joint_dic = dict ()
    joints = jdata['joints']
    for joint in joints:
      jid = joint['id']
      jmap = joint_map (joint)
      self.joint_dic[jid] = jmap
  def get_joint_names (self):
    """return a list of all joints this skin has.
    """
    return self.joint_dic.keys ()
  def get (self, name):
    """return the maps for the given bone name. This function returns
       the appropriate joint_map instance.
    """
    return self.joint_dic.get (name)
  def get_single_paint_map (self, joint, axes):
    """convenience function for returning a mix of maps for a
       single body part.
    """
    joint = self.joint_dic[joint]
    return joint.get_paint_map_mix (axes)
  def canonicalize_map_name (self, joint, group):
    """build a simple string from a joint name and a group of axes.
       This name can be used to create a vertex group of it.
    """
    if group == '':
      return "def-%s" % (joint)
    else:
      return "def-%s.%s" % (joint, group)
  def collect_paint_maps (self, groups):
    """get all paintable maps in groups for all joints. Each group is averaged,
       in general that means the results are not normalized to the number
       of groups.
       if groups is empty, only considers generic maps.
       Returns a mapping name->weightmap
    """
    all_map_dic = dict ()
    # loop through every bone (joint) from the joint dictionary.
    for (jname, joint) in self.joint_dic.items ():
      if joint.is_generic ():
        pmap_dic = joint.get_paint_map_groups (xxx)
      pmap_dic = joint.get_paint_map_groups (groups)
      # returns some weightmaps, based on the requested groups and available
      # groups.
      for (pmap_name, pmap_group) in pmap_dic.items ():
        canonical_name = self.canonicalize_map_name (jname, pmap_name)
        all_map_dic[canonical_name] = pmap_group
    return all_map_dic
  def collect_all_paint_maps (self, scale = False, local = 'merged'):
    """return a dictionary containing every defined weight map in the skin.
       grouping and generation of maps depends on the kwarg:
       merge: if True, the 3 rotation axes get merged into a single map.
       scale: if True, a separate map for scaling is generated (otherwise
         no scaling information is used).
    """
    if local == 'merged':
      groups = ['xyz']
    elif local == 'generic':
      groups = ['n']
    else:
      groups = ['x', 'y', 'z']
    if scale:
      groups.append ('s')
    return self.collect_paint_maps (groups)

def load_mod_lib (filepath):
  """load the dsf file and return the modifier-library.
  """
  jdata = dsf_io.read_json_data (filepath)
  if 'modifier_library' in jdata:
    # return the first modifier library.
    return jdata['modifier_library'][0]
  else:
    raise KeyError ("data does not contain modifier-library.")

def load_skin (filepath):
  """load the dsf file and return a skin.
  """
  jdata = load_mod_lib (filepath)
  return skin (jdata['skin'])

