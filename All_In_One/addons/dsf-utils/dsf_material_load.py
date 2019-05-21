import json, logging, random, itertools
from array import array

log = logging.getLogger ('import_uvset')

class dsf_material (dict):
  """collects information about a material.
  """
  def __init__ (self, jdata):
    """initialize with a material jdata.
       basically a material is a collection of channels.
    """
    pass
