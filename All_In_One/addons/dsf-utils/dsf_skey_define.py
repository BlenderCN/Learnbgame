from mathutils import Vector

def define_shape_key (obj, base, name, deltas):
  """define a new shapekey for mesh.
     obj is the object of a mesh.
     base is the base shapekey from which the new shapekey is derived.
     name is the name for the new shapekey.
     deltas is an iterable returning pairs of (vertex index, delta).
  """
  shape_key = obj.shape_key_add (name)
  shape_key_data = shape_key.data
  shape_key_values = shape_key_data.values ()
  for (delta_idx, delta_val) in deltas:
    # add the deltas to their respective shape-key coordinates.
    shape_key_values[delta_idx].co += Vector (delta_val)
  return shape_key

def define_morph (obj, base, morph):
  """create a new shapekey for obj, based on the modifier morph
     relative to base.
  """
  shape_key_name = morph.name ()
  shape_key = define_shape_key (obj, base, shape_key_name, morph.deltas ())
  return shape_key

def get_base_shape_key (obj):
  """get or create the base shapekey for object.
  """
  if obj.data.shape_keys is None:
    base_shape_key = obj.shape_key_add ('base')
  else:
    base_shape_key = obj.data.shape_keys.reference_key
  return base_shape_key

def define_shapekeys (obj, morphlib):
  """define all morphs of morphlib as shapekeys. A new base shapekey is
     automatically created of none exists yet.
  """
  modifier = morphlib.find_modifier (None)
  base_shape_key = get_base_shape_key (obj)
  define_morph (obj, base_shape_key, modifier)
