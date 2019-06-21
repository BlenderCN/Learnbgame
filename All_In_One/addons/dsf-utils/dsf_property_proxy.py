
class property_proxy_base (object):
  """a class that acts as a proxy for setting values when
     reading pose-files.
     instances are responsible for setting values when given a value
     and a path (the property_path from a uri-reference).
  """
  def __init__ (self, obj = None, name = None):
    """initialize the base. Optionally sets the blender object delegate
       and the name to the given arguments.
    """
    self.obj = obj
    self.name = name
  def set (self, path, value):
    """set the property value with the given path to the given value.
    """
    raise NotImplementedError\
        ("set property '%s' base implementation" % path)

class pose_bone_proxy (property_proxy_base):
  """a setter class for pose bones.
  """
  def __init__ (self, pbone, **kwarg):
    """create a proxy for the given pose bone.
    """
    super (pose_bone_proxy, self).__init__ (obj = pbone, name = pbone.name)
  def axis_num (self, axis):
    """return the index of an axis.
    """
    return 'xyz'.index (axis.lower ())
  def (self, path, value):
    """set a value on the bone.
       known paths are: {translation,rotation,scale}/{x,y,z}, scale/general
    """
    (category, _, axis) = path.partition ('/')
    if category == 'scale':
      # todo: axis can by 'xyz' or 'general'. have to decide on how to mix
      # these (order dependent? multiply?)
      pass
    elif category == 'translation':
      new_value = self.obj.location
      new_value[self.axis_num (axis)] = value
      self.obj.location = new_value
    elif category == 'rotation':
      new_value = self.obj.rotation_euler
      new_value[self.axis_num (axis)] = value
      self.obj.rotation_euler = new_value
    else:
      raise NotImplementedError ("cannot set property '%s' on bone" % path)

