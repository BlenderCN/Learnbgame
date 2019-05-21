# read morphs from a dsf data file.
import json
from . import dsf_io

class modifier_lib (object):
  """class to represent on modifier library element from a dsf file.
  """
  def __init__ (self, node):
    """node is to be the modifier_library node.
    """
    self.node = node
  def get_modifiers (self):
    """get list of the modifiers of this lib.
    """
    return list (map (modifier, self.node))

  def find_modifier (self, name):
    """get a modifier by name. If name is None, the first modifier is returned.
    """
    if name is None:
      return modifier (self.node[0])
    else:
      for modifier_node in self.node:
        if mname == modifier_node['id']:
          return modifier (modifier_node)
      raise ValueError ("not found: %s" % (mname))

class modifier (object):
  """class to represent a single morph modifier.
  """
  def __init__ (self, node):
    """node must be a single modifier library entry.
    """
    self.node = node

  def name (self):
    """returns the name (id) of the modifier.
    """
    return self.node['id']
  def deltas (self):
    """return an iterator that iterates over the index/offset pairs
       of the morph-node.
    """
    # node.morph.deltas.values is a list containing indexes and offsets.
    values = self.node['morph']['deltas']['values']
    for id_pair in values:
      yield (id_pair[0], id_pair[1:])
    return

def get_modifier_lib (root):
  """get the modifer-library from a dsf data object.
  """
  return modifier_lib (root['modifier_library'])

def read_dsf_data (filename):
  """return a dsf file and (for now return the modifier lib.
  """
  jdata = dsf_io.read_json_data (filename, encoding = 'latin1')
  return modifier_lib (jdata['modifier_library'])
