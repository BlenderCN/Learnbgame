
from collections import OrderedDict, namedtuple, Counter

from .typereader import AnimatedProperty, ArgumentProperty

from .mathtypes import Vector
from .propertiesset import PropertiesSet

# The known vertex channels
_vertex_channels = {"position": 0, "normal": 1, "tex0": 4, "bones": 21}

Texture = namedtuple("Texture", ["index", "name", "matrix"])

class VertexFormat(object):
  """Represents the vertex format for an array of vertices"""

  def __init__(self, channelData=None):
    """Initialise vertex format. takes a byte array, numeric per-channel string, 
    or a dictionary naming each count."""
    if isinstance(channelData, str):
      if len(channelData) < 26:
        channelData = channelData + "0"*(26-len(channelData))
      self.data = bytes(int(x) for x in channelData)
    elif isinstance(channelData, bytes):
      self.data = channelData
    elif isinstance(channelData, dict):
      assert all(x in _vertex_channels for x in channelData.keys())
      data = bytearray(26)
      for name, count in channelData.items():
        data[_vertex_channels[name]] = count
      self.data = bytes(data)
    elif channelData is None:
      self.data = bytes(26)
    else:
      self.data = channelData

    self.nposition = int(self.data[0])
    self.nnormal = int(self.data[1])
    self.ntexture = int(self.data[4])
  
  def __hash__(self):
    return hash(self.data)
  
  def __eq__(self, other):
    return self.data == other.data

  @property
  def position_indices(self):
    return [0,1,2]

  @property
  def normal_indices(self):
    start = self.data[0]
    return list(range(start, start+self.nnormal))

  @property
  def texture_indices(self):
    start = sum(self.data[:4])
    return list(range(start, start+self.ntexture))

  def __repr__(self):
    assert all(x < 10 for x in self.data)
    return "VertexFormat('{}')".format("".join(str(x) for x in self.data))

  @classmethod
  def read(cls, reader):
    channels = reader.read_uint()
    data = reader.read_uchars(channels)

    # Which channels have data?
    knownChannels = set(_vertex_channels.values())
    dataChannels = {i: x for i, x in enumerate(data) if x != 0 and not i in knownChannels} 
    if dataChannels:
      print("Warning: Vertex channel data in unrecognised channels: {}".format(dataChannels))
    return cls(data)

  def write(self, writer):
    writer.write_uint(len(self.data))
    writer.write(self.data)

def _read_material_texture(reader):
  index = reader.read_uint()
  assert (reader.read_int() == -1)
  name = reader.read_string()
  assert reader.read_uints(4) == (2,2,10,6)
  matrix = reader.read_matrixf()
  return Texture(index, name, matrix)

def _read_animateduniforms(stream):
  length = stream.read_uint()
  data = OrderedDict()
  for _ in range(length):
    prop = stream.read_named_type()
    data[prop.name] = prop
  return data

def _read_texture_coordinates_channels(stream):
  count = stream.read_uint()
  return stream.read_ints(count)

# Lookup table for material reading types
_material_entry_lookup = {
  "BLENDING": lambda x: x.read_uchar(),
  "CULLING" : lambda x: x.read_uchar(),
  "DEPTH_BIAS": lambda x: x.read_uint(),
  "TEXTURE_COORDINATES_CHANNELS": _read_texture_coordinates_channels,
  "MATERIAL_NAME": lambda x: x.read_string(),
  "NAME": lambda x: x.read_string(),
  "SHADOWS": lambda x: ShadowSettings(x.read_uchar()),
  "VERTEX_FORMAT": VertexFormat.read,
  "UNIFORMS": PropertiesSet.read,
  "ANIMATED_UNIFORMS": _read_animateduniforms,
  "TEXTURES": lambda x: x.read_list(_read_material_texture)
}

class ShadowSettings(object):
  def __init__(self, value=None, **kwargs):
    if value is not None:
      assert value <= 7, "Only understand first three shadow flags"
      self.cast = bool(value & 1)
      self.receive = bool(value & 2)
      self.cast_only = bool(value & 4)
    else:
      self.cast = kwargs.get("cast", False)
      self.receive = kwargs.get("receive", False)
      self.cast_only = kwargs.get("cast_only", False)

  @property
  def value(self):
    return (1 if self.cast else 0) + \
           (2 if self.recieve else 0) + \
           (4 if self.cast_only else 0)

  def __repr__(self):
    args = []
    if self.cast:
      args.append("cast=True")
    if self.receive:
      args.append("recieve=True")
    if self.cast_only:
      args.append("cast_only=True")
    return "ShadowSettings(" + ", ".join(args) + ")"

class Material(object):
  def __init__(self):
    self.blending = 0
    self.culling = 0
    self.depth_bias = 0
    self.texture_coordinates_channels = None
    self.material_name = ""
    self.name = ""
    self.shadows = ShadowSettings()
    self.vertex_format = None
    self.uniforms = PropertiesSet()
    self.animated_uniforms = PropertiesSet()
    self.textures = []

  @classmethod
  def read(cls, stream):
    self = cls()
    props = OrderedDict()
    for _ in range(stream.read_uint()):
      name = stream.read_string()
      props[name] = _material_entry_lookup[name](stream)
    for k, i in props.items():
      setattr(self, k.lower(), i)
    self.props = props
    return self

  def write(self, writer):
    #  'TEXTURES', 'UNIFORMS', 'ANIMATED_UNIFORMS'])
    writer.write_uint(10)
    writer.write_string("BLENDING")
    writer.write_uchar(self.blending)
    # writer.write_string("CULLING")
    # writer.write_uchar(self.culling)
    writer.write_string("DEPTH_BIAS")
    writer.write_uint(self.depth_bias)
    if self.vertex_format:
      writer.write_string("VERTEX_FORMAT")
      self.vertex_format.write(writer)
    writer.write_string("TEXTURE_COORDINATES_CHANNELS")
    tcc = (0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
    writer.write_uint(len(tcc))
    writer.write_ints(tcc)
    writer.write_string("MATERIAL_NAME")
    writer.write_string(self.material_name)
    writer.write_string("NAME")
    writer.write_string(self.name.replace(".", "_"))
    writer.write_string("SHADOWS")
    writer.write_uchar(self.shadows.value)
    writer.write_string("TEXTURES")
    writer.write_uint(len(self.textures))
    for texture in self.textures:
      writer.write_uint(texture.index)
      writer.write_int(-1)
      writer.write_string(texture.name.lower())
      writer.write_uints([2,2,10,6])
      writer.write_matrixf(texture.matrix)
    writer.write_string("UNIFORMS")
    self.uniforms.write(writer)
    writer.write_string("ANIMATED_UNIFORMS")
    assert not self.animated_uniforms
    self.animated_uniforms.write(writer)

  def audit(self):
    c = Counter()
    if self.uniforms:
      c["model::PropertiesSet"] = 1
      c += self.uniforms.audit()
    if self.animated_uniforms:
      for entry in self.animated_uniforms.values():
        if isinstance(entry, AnimatedProperty):
          typeEntry = entry.keys[0].value
          if isinstance(typeEntry, float):
            c["model::AnimatedProperty<float>"] += 1
            c["model::Key<key::FLOAT>"] += len(entry.keys)
          elif isinstance(typeEntry, Vector):
            vLen = len(typeEntry)
            c["model::AnimatedProperty<osg::Vec{}f>".format(vLen)] += 1
            c["model::Key<key::VEC{}F>".format(vLen)] += len(entry.keys)
          else:
            raise IOError("Have not encountered writing animated property of type {}/{}".format(entry, type(entry)))          
        elif isinstance(entry, ArgumentProperty):
          c["model::ArgumentProperty"] += 1
    return c
