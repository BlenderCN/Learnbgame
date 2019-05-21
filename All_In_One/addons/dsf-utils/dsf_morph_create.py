import posixpath

class dsf_morph_create (object):
  """utility class to create various dsf-objects.
  """
  def __init__ (self):
    pass

  @classmethod
  def fill_default_vars (self, defs, vals):
    """return a new dictionary that contains a merged version of defs and vals.
    """
    attrs = dict ()
    for (k, v) in defs.items ():
      if k in vals:
        attrs[k] = vals[k]
      elif v is None:
        raise Exception ("attribute '%s' required" % k)
      else:
        attrs[k] = defs[k]
    return attrs

  @classmethod
  def make_units (self, **kwarg):
    default_attrs = {
      'length': 100,
      'angle': 'degrees',
      'time': 4800
    }
    return self.fill_default_vars (default_attrs, kwarg)

  @classmethod
  def make_modifier (self, **kwarg):
    """create a modifier entry for a modifier_library.
       kwarg supported:
       channel - required; a channel for the modifier.
       parent - required; parent id
       presentation - presentation object
       region - body part
       group - group name of the modifier
       formulas - dependent parameters
       morph - for a morph
    """
    default_attrs = {
      'id': None,
      'region': 'Actor',
      'parent': "/data/DAZ%203D/Genesis/Base/Genesis.dsf#Genesis",
      'presentation': None,
      # a channel for dialing in this modifier.
      'channel': None,
      # the region (body part)
      'region': None,
      # path of a group to sort it into menus
      'group': None,
      # morph data (deltas)
      'morph': None,
      # drivers for other values in the figure.
      'formulas': [],
    }
    return self.fill_default_vars (default_attrs, kwarg)

  @classmethod
  def make_presentation (self, **kwarg):
    """create a presentation object.
    """
    default_attrs = {
      'label': None,
      'type': 'Modifier/Shape',
      'description': 'description of this modifier',
      'icon_large': '',
      'colors': [[0.5, 0.5, 0.5], [1, 1, 1]]
    }
    return self.fill_default_vars (default_attrs, kwarg)

  @classmethod
  def make_channel (self, **kwarg):
    """create a named channel
    """
    default_attrs = {
      'id': None,
      'label': None,
      'visible': True,
      'locked': False,
      'min': 0, 'max': 1,
      'clamped': True,
      'display_as_percent': True,
      'step_size': 0.01,
      'value': 0,
      'auto_follow': False
    }
    attrs = self.fill_default_vars (default_attrs, kwarg)
    return attrs

  @classmethod
  def make_morph (self, **kwarg):
    """make a morph-entry. kwarg required: vertex_count, deltas.
       deltas must be a map vertex_id->xyz.
    """
    if 'deltas' not in kwarg:
      raise Exception ("attribute 'deltas' required")
    values = [[i, v[0], v[1], v[2]] for i, v in kwarg['deltas'].items ()]
    values.sort ()
    morph_default_attrs = {
      'vertex_count': None,
      'deltas': None
    }
    kwarg['deltas'] = {
      'count': len (values),
      'values': values
    }
    attrs = self.fill_default_vars (morph_default_attrs, kwarg)
    return attrs

  @classmethod
  def make_morph_file (self, shape_key = None, **kwarg):
    """required kwarg:
       shape_key - internalized shape-key-data.
    """
    (group, id) = posixpath.split (shape_key['id'])
    if group in ['', '/']:
      group = '/Universal'
    modifier_data = {
      'id': id,
      'channel': self.make_channel\
        (id = id, label = id, min = shape_key['min'], max = shape_key['max']),
      'presentation': self.make_presentation (label = id),
      'region': 'Actor',
      'group': group,
      'parent': shape_key['id_path'],
      'morph': self.make_morph\
        (deltas = shape_key['deltas'], vertex_count = shape_key['vertex_count'])
    }
    modifier = self.make_modifier (**modifier_data)
    scene_data = {
      'modifiers': [
        {
          'id': id + '_0',
          'url': '#' + id
        }
      ]
    }
    file_data = {
      'file_version': '1.0',
      'units': self.make_units (),
      'pedigree': [],
      'modifier_library': [ modifier ],
      'scene': scene_data
    }
    return file_data
