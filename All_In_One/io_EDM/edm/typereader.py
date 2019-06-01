"""
Allows registration of type-readers by name, and retrieval of those readers.

Each reader function takes a single argument; a BaseReader object

"""
from inspect import isclass

from collections import namedtuple

_typeReaders = {}


Property = namedtuple("Property", ["name", "value"])
AnimatedProperty = namedtuple("AnimatedProperty", ["name", "argument", "keys"])
ArgumentProperty = namedtuple("ArgumentProperty", ["name", "argument"])
Keyframe = namedtuple("Keyframe", ("frame", "value"))

def get_type_reader(typeName):
  try:
    return _typeReaders[typeName]
  except KeyError:
    raise KeyError("No reader defined for stream type '{}'".format(typeName)) from None

def generate_property_reader(generic_type):
  def _read_property(data):
    name = data.read_string()
    data = get_type_reader(generic_type)(data)
    return Property(name, data)
  return _read_property

def generate_keyframe_reader(generic_type):
  def _read_keyframe(stream):
    frame = stream.read_double()
    value = get_type_reader(generic_type)(stream)
    return Keyframe(frame=frame, value=value)
  return _read_keyframe

def generate_animated_property_reader(keyframe_type):
  def _read_animatedproperty(stream):
    name = stream.read_string()
    argument = stream.read_uint()
    count = stream.read_uint()
    reader = get_type_reader(keyframe_type)
    keys = [reader(stream) for _ in range(count)]
    return AnimatedProperty(name=name, argument=argument, keys=keys)
  return _read_animatedproperty

def reads_type(withName):
  """Simple registration function to read named type objects"""
  def wrapper(fn):
    if not isclass(fn):
      _typeReaders[withName] = fn
    elif hasattr(fn, "read"):
      _typeReaders[withName] = fn.read
    else:
      raise RuntimeError("Unrecognised type reader {}".format(fn))
    fn.forTypeName = withName
    return fn
  return wrapper

def allow_properties(w):
  """Decorator to generate type-readers for type-as-property values"""
  name = "model::Property<{}>".format(w.forTypeName)
  _typeReaders[name] = generate_property_reader(w.forTypeName)
  return w

def animatable(keyname):
  def _wrapper(fn):
    keyframe_type = "model::Key<{}>".format(keyname)
    prop_type = "model::AnimatedProperty<{}>".format(fn.forTypeName)
    _typeReaders[keyframe_type] = generate_keyframe_reader(fn.forTypeName)
    _typeReaders[prop_type] = generate_animated_property_reader(keyframe_type)
    return fn
  return _wrapper
# Vector2 = namedtuple("Vector2", ["x", "y"])
# Vector3 = namedtuple("Vector3", ["x", "y", "z"])

@allow_properties
@reads_type("unsigned int")
def _read_uint(data):
  return data.read_uint()

@animatable(keyname="key::FLOAT")
@allow_properties
@reads_type("float")
def read_prop_float(data):
  return data.read_float()

@animatable(keyname="key::VEC2F")
@allow_properties
@reads_type("osg::Vec2f")
def readVec2f(data):
  return data.read_vec2f()

@animatable(keyname="key::VEC3F")
@allow_properties
@reads_type("osg::Vec3f")
def readVec3f(data):
  return data.read_vec3f()

@allow_properties
@reads_type("osg::Vec3d")
def readVec3d(data):
  return data.read_vec3d()

@reads_type("osg::Matrixf")
def readMatrixf(stream):
  return stream.read_matrixf()

@reads_type("osg::Matrixd")
def readMatrixd(stream):
  return stream.read_matrixd()

@reads_type("osg::Quat")
def readQuaternion(stream):
  return stream.read_quaternion()

@allow_properties
@reads_type("const char*")
def readConstChar(stream):
  assert stream.version != 10, "Need manual verification as to how v10 string properties are written"
  return stream.read_string()

@reads_type("model::ArgumentProperty")
def read_argproperty(stream):
  name = stream.read_string()
  arg = stream.read_uint()
  return ArgumentProperty(name, arg)
