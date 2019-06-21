

# from .typereader import Property, allow_properties, reads_type
# from collections import namedtuple

from .typereader import reads_type
from .typereader import get_type_reader as _tr_get_type_reader
from .basereader import BaseReader

from .material_types import VertexFormat, Material, Texture
from .propertiesset import PropertiesSet

from collections import namedtuple, OrderedDict, Counter
import itertools
import struct

from .mathtypes import Vector, sequence_to_matrix, Matrix, Quaternion

from abc import ABC
from enum import Enum
import math

import logging
logger = logging.getLogger(__name__)

class NodeCategory(Enum):
  """Enum to describe what file-category the node is in"""
  transform = "transform"
  connector = "CONNECTORS"
  render = "RENDER_NODES"
  shell = "SHELL_NODES"
  light = "LIGHT_NODES"

class AnimatingNode(ABC):
  """Abstract base class for all nodes that animate the object"""


# All possible entries for indexA and indexB
_all_IndexA = {'model::TransformNode', 'model::FakeOmniLightsNode', 'model::SkinNode', 'model::Connector', 'model::ShellNode', 'model::SegmentsNode', 'model::FakeSpotLightsNode', 'model::BillboardNode', 'model::ArgAnimatedBone', 'model::RootNode', 'model::Node', 'model::ArgAnimationNode', 'model::LightNode', 'model::LodNode', 'model::Bone', 'model::RenderNode', 'model::ArgVisibilityNode'}
_all_IndexB = {'model::Key<key::ROTATION>', 'model::Property<float>', 'model::ArgAnimationNode::Position', '__pointers', 'model::FakeOmniLight', 'model::Key<key::SCALE>', 'model::AnimatedProperty<osg::Vec3f>', 'model::Key<key::VEC3F>', 'model::Property<osg::Vec2f>', 'model::Property<osg::Vec3f>', 'model::ArgAnimationNode::Rotation', 'model::ArgVisibilityNode::Range', 'model::Key<key::POSITION>', 'model::AnimatedProperty<osg::Vec2f>', 'model::Key<key::FLOAT>', '__ci_bytes', '__gv_bytes', 'model::ArgVisibilityNode::Arg', 'model::AnimatedProperty<float>', 'model::RNControlNode', 'model::SegmentsNode::Segments', '__gi_bytes', '__cv_bytes', 'model::Property<unsigned int>', 'model::Key<key::VEC2F>', 'model::ArgAnimationNode::Scale', 'model::LodNode::Level', 'model::PropertiesSet', 'model::FakeSpotLight'}


def get_type_reader(name):
  _readfun = _tr_get_type_reader(name)
  def _reader(reader):
    reader.typecount[name] += 1
    return _readfun(reader)
  return _reader

class TrackingReader(BaseReader):
  def __init__(self, *args, **kwargs):
    self.typecount = Counter()
    self.autoTypeCount = Counter()
    super(TrackingReader, self).__init__(*args, **kwargs)

  def mark_type_read(self, name, amount=1):
    self.typecount[name] += amount

  def read_named_type(self, selfOrNone=None):
    assert selfOrNone is None or selfOrNone is self
    typeName = self.read_string()
    try:
      return get_type_reader(typeName)(self)
    except KeyError:
      print("Error at position {}".format(self.tell()))
      raise

def _read_index(stream):
  """Reads a dictionary of type String : uint"""
  length = stream.read_uint()
  data = OrderedDict()
  for _ in range(length):
    key = stream.read_string()
    value = stream.read_uint()
    data[key] = value
  return data

def _write_index(writer, data):
  writer.write_uint(len(data))
  keys = sorted(data.keys())
  for key in keys:
    writer.write_string(key)
    writer.write_uint(data[key])


def _read_main_object_dictionary(stream):
  count = stream.read_uint()
  objects = {}
  for _ in range(count):
    name = stream.read_string()
    objects[name] = stream.read_list(stream.read_named_type)
  return objects

class EDMFile(object):
  def __init__(self, filename=None):
    if filename:
      reader = TrackingReader(filename)
      try:
        self._read(reader)
      except:
        print("ERROR at {}".format(reader.tell()))
        raise
    else:
      self.version = 8
      self.indexA = {}
      self.indexB = {}
      self.root = None
      self.nodes = []
      self.connectors = []
      self.renderNodes = []
      self.lightNodes = []
      self.shellNodes = []

  def _read(self, reader):
    reader.read_constant(b'EDM')
    self.version = reader.read_ushort()
    assert self.version in [8, 10], "Unexpected .EDM file version = {}".format(self.version)
    if self.version == 10:
      print("Warning: Version 10 not as well understood")
    reader.version = self.version

    if reader.v10:
      stringsize = reader.read_uint()
      sdata = reader.read(stringsize).split(bytes(1))
      reader.strings = [x.decode("windows-1251") for x in sdata]
    else:
      reader.strings = None

    # Read the two indexes
    self.indexA = _read_index(reader)
    self.indexB = _read_index(reader)
    self.root = reader.read_named_type()

    self.nodes = reader.read_list(reader.read_named_type)
    self.transformRoot = self.nodes[0]

    # Read the node parenting data
    for (node, parent) in zip(self.nodes, reader.read_ints(len(self.nodes))):
      if parent == -1:
        node.parent = None
        continue
      if parent > len(self.nodes):
        raise IOError("Invalid node parent data")

      node.set_parent(self.nodes[parent])

    # Read the renderable objects
    objects = _read_main_object_dictionary(reader)
    self.connectors = objects.get("CONNECTORS", [])
    self.shellNodes = objects.get("SHELL_NODES", [])
    self.lightNodes = objects.get("LIGHT_NODES", [])
    self.renderNodes = []
    # Split any renderNodes as one may contain several objects
    for node in objects.get("RENDER_NODES", []):
      if isinstance(node, RenderNode):
        for splitNode in node.split():
          self.renderNodes.append(splitNode)
      else:
        self.renderNodes.append(node)

    # Verify we are at the end of the file without unconsumed data.
    endPos = reader.tell()
    if len(reader.read(1)) != 0:
      print("Warning: Ended parse at {} but still have data remaining".format(endPos))
    reader.close()

    # Set up parents and other links (e.g. material, bone...)
    for node in itertools.chain(self.connectors, self.shellNodes, self.lightNodes, self.renderNodes):
      if hasattr(node, "parent") and node.parent is not None:
        node.set_parent(self.nodes[node.parent])
      if hasattr(node, "material"):
        node.material = self.root.materials[node.material]
      if hasattr(node, "bones"):
        node.bones = [self.nodes[x] for x in node.bones]
        # If we have bones we have no single 'parent'. Stick it on the root.
        node.set_parent(self.nodes[0])

    # Validate against the index
    self.selfCount = self.audit()
    rems = Counter(self.indexA)
    rems.subtract(Counter({x: c for (x,c) in reader.typecount.items() if x in self.indexA}))
    for k in [x for x in rems.keys() if rems[x] == 0]:
      del rems[k]

    if rems:
      print("IndexA items remaining before RENDER_NODES/CONNECTORS: {}".format(rems))
    cB = Counter({x: c for (x,c) in reader.typecount.items() if x in self.indexB})
    remBs = Counter(self.indexB)
    remBs.subtract(cB)
    for k in [x for x in remBs.keys() if remBs[x] == 0]:
      del remBs[k]
    if remBs:
      print("IndexB items remaining before RENDER_NODES/CONNECTORS: {}".format(remBs))

  def audit(self):
    _index = Counter()
    _index[RootNode.forTypeName] += 1
    _index += self.root.audit()
    for node in self.nodes:
      _index[node.forTypeName] += 1
      _index += node.audit()
    for rn in itertools.chain(self.renderNodes, self.shellNodes, self.lightNodes, self.connectors):
      _index[rn.forTypeName] += 1
      try:
        _index += rn.audit()
      except:
        raise RuntimeError("Trouble reading audit from {}".format(type(rn)))

    return _index

  def write(self, writer):
    # Generate the file index with an audit
    _allIndex = self.audit()
    indexA = {k: v for k, v in _allIndex.items() if k in _all_IndexA}
    indexB = {k: v for k, v in _allIndex.items() if k in _all_IndexB}

    # Do the writing
    writer.write(b'EDM')
    writer.write_ushort(8)
    _write_index(writer, indexA)
    _write_index(writer, indexB)

    # Write the Root node
    writer.write_named_type(self.root)
    
    # For each parent node, set it's index
    for i, node in enumerate(self.nodes):
      node.index = i

    writer.write_uint(len(self.nodes))
    for node in self.nodes:
      writer.write_named_type(node)

    # Write the parent data for the nodes
    writer.write_int(-1)
    # Everything without a parent has 0 as it's parent
    for node in self.nodes[1:]:
      if node.parent:
        writer.write_uint(node.parent.index)
      else:
        writer.write_uint(0)

    # Now do the render objects dictionary
    objects = {}
    if self.renderNodes:
      objects["RENDER_NODES"] = self.renderNodes
    if self.connectors:
      objects["CONNECTORS"] = self.connectors
    if self.shellNodes:
      objects["SHELL_NODES"] = self.shellNodes
    if self.lightNodes:
      objects["LIGHT_NODES"] = self.lightNodes
    writer.write_uint(len(objects))
    for key, nodes in objects.items():
      writer.write_string(key)
      writer.write_uint(len(nodes))
      for node in nodes:
        writer.write_named_type(node)

class GraphNode(object):
  def __init__(self):
    self.parent = None
    self.children = []

  def set_parent(self, parent):
    if self.parent is parent:
      return
    # If we have a parent, unregister from it (special case: Reassigning an indexed parent value)
    if self.parent and not isinstance(self.parent, int):
      self.parent.children.remove(self)
    self.parent = parent
    self.parent.children.append(self)

  def add_child(self, child):
    if child in self.children:
      return
    if child.parent:
      child.parent.children.remove(child)
    child.parent = self
    self.children.append(child)

@reads_type("model::BaseNode")
class BaseNode(GraphNode):
  def __init__(self, name=None):
    super(BaseNode, self).__init__()

    self.name = name or ""
    self.version = 0
    self.props = PropertiesSet()

  @classmethod
  def read(cls, stream):
    node = cls()
    node.name = stream.read_string(lookup=False)
    node.version = stream.read_uint()
    node.props = PropertiesSet.read(stream, count=False)
    return node

  def audit(self):
    c = Counter()
    if self.props:
      c += self.props.audit()
    return c

  def write(self, writer):
    writer.write_string(self.name)
    writer.write_uint(self.version)
    self.props.write(writer)

  def __repr__(self):
    if not self.name:
      return "<{}>".format(type(self).__name__)
    else:
      return "<{} \"{}\">".format(type(self).__name__, self.name)

@reads_type("model::RootNode")
class RootNode(BaseNode):
  def __init__(self):
    super(RootNode, self).__init__()
    self.name = "Scene Root"
    self.props["__VERSION__"] = 2
    self.unknown_parts = []

  @classmethod
  def read(cls, stream):
    self = super(RootNode, cls).read(stream)
    self.unknownA = stream.read_uchar()
    self.boundingBoxMin = stream.read_vec3d()
    self.boundingBoxMax = stream.read_vec3d()
    self.unknownB = [stream.read_vec3d() for _ in range(4)]
    self.materials = stream.read_list(Material.read)
    stream.materials = self.materials
    self.unknownD = stream.read_uints(2)
    return self

  def audit(self):
    c = super(RootNode, self).audit()
    for material in self.materials:
      c += material.audit()
    return c

  def write(self, writer):
    super(RootNode, self).write(writer)

    writer.write_uchar(0)
    writer.write_vecd(self.boundingBoxMin)
    writer.write_vecd(self.boundingBoxMax)
    # Don't fully understand this bit; seems to sometimes be min, max again then high, low.
    # Try those
    writer.write_vecd(self.boundingBoxMin)
    writer.write_vecd(self.boundingBoxMax)
    # Most seem to have this exact set of data; 3.4e38 * 3, -3.4e38*3
    for _ in range(3):
      writer.write(b'\x00\x00\x00\xe0\xff\xff\xefG')
    for _ in range(3):
      writer.write(b'\x00\x00\x00\xe0\xff\xff\xef\xc7')

    writer.write_uint(len(self.materials))
    for mat in self.materials:
      mat.write(writer)
    writer.write_uint(0)
    writer.write_uint(0)


@reads_type("model::Node")
class Node(BaseNode):
  category = NodeCategory.transform

@reads_type("model::TransformNode")
class TransformNode(Node):
  @classmethod
  def read(cls, stream):
    self = super(TransformNode, cls).read(stream)
    self.matrix = stream.read_matrixd()
    return self

  def write(self, stream):
    super(TransformNode, self).write(stream)
    stream.write_matrixd(self.matrix)

@reads_type("model::Bone")
class Bone(Node):
  @classmethod
  def read(cls, reader):
    self = super(Bone, cls).read(reader)
    self.data = [reader.read_matrixd(), reader.read_matrixd()]
    return self

class ArgAnimationBase(object):
  def __init__(self, matrix=None, position=None, quat_1=None, quat_2=None, scale=None):
    self.matrix = matrix or Matrix()
    self.position = position or Vector()
    self.quat_1 = quat_1 or Quaternion((1,0,0,0))
    self.quat_2 = quat_2 or Quaternion((1,0,0,0))
    self.scale = scale or Vector((1,1,1))
  @classmethod
  def read(cls, stream):
    self = cls()
    self.matrix = stream.read_matrixd()
    self.position = stream.read_vec3d()
    self.quat_1 = stream.read_quaternion()
    self.quat_2 = stream.read_quaternion()
    self.scale = stream.read_vec3d()
    return self
  def write(self, stream):
    stream.write_matrixd(self.matrix)
    stream.write_vec3d(self.position)
    stream.write_quaternion(self.quat_1)
    stream.write_quaternion(self.quat_2)
    stream.write_vec3d(self.scale)

@reads_type("model::ArgAnimationNode")
class ArgAnimationNode(Node, AnimatingNode):
  def __init__(self, *args, **kwargs):
    super(ArgAnimationNode, self).__init__(*args, **kwargs)
    self.base = ArgAnimationBase()
    self.posData = []
    self.rotData = []
    self.scaleData = []
    self.parent = None

  def __repr__(self):
    if self.posData and not self.rotData and not self.scaleData:
      nodeName = "ArgPositionNode"
    elif self.rotData and not self.posData and not self.scaleData:
      nodeName = "ArgRotationNode"
    elif self.scaleData and not self.posData and not self.rotData:
      nodeName = "ArgScaleNode"
    else:
      nodeName = "ArgAnimationNode"

    return "<{} {:}{:}{:}{}>".format(nodeName,
      len(self.posData), len(self.rotData), len(self.scaleData),
      " "+self.name if self.name else "")

  @classmethod
  def read(cls, stream):
    self = super(ArgAnimationNode, cls).read(stream)
    self.base = ArgAnimationBase.read(stream)
    self.posData = stream.read_list(ArgPositionNode._read_AANPositionArg)
    self.rotData = stream.read_list(ArgRotationNode._read_AANRotationArg)
    self.scaleData = stream.read_list(ArgScaleNode._read_AANScaleArg)
    return self

  def write(self, stream):
    super(ArgAnimationNode, self).write(stream)
    self.base.write(stream)
    # Write the positional animation data
    stream.write_uint(len(self.posData))
    for arg, keyframes in self.posData:
      stream.write_uint(arg)
      stream.write_uint(len(keyframes))
      for frame in keyframes:
        stream.write_double(frame.frame)
        stream.write_vec3d(frame.value)

    stream.write_uint(len(self.rotData))
    for arg, keyframes in self.rotData:
      stream.write_uint(arg)
      stream.write_uint(len(keyframes))
      for frame in keyframes:
        stream.write_double(frame.frame)
        stream.write_quaternion(frame.value)

    stream.write_uint(len(self.scaleData))
    assert not self.scaleData, "Not implemented"


  def audit(self):
    c = super(ArgAnimationNode, self).audit()
    if not type(self) is ArgAnimationNode:
      c["model::ArgAnimationNode"] += 1
    c["model::ArgAnimationNode::Rotation"] = len(self.rotData)
    c["model::ArgAnimationNode::Position"] = len(self.posData)
    c["model::ArgAnimationNode::Scale"] = len(self.scaleData)

    rotKeys = sum([len(x[1]) for x in self.rotData])
    posKeys = sum([len(x[1]) for x in self.posData])
    scaKeys = sum([len(x[1][0])+len(x[1][1]) for x in self.scaleData])
    c["model::Key<key::ROTATION>"] = rotKeys
    c["model::Key<key::POSITION>"] = posKeys
    c["model::Key<key::SCALE>"] = scaKeys
    return c

  def get_all_args(self):
    "Return a list of all arguments that this object represents"
    all_args = set()
    for dataset in [self.posData, self.rotData, self.scaleData]:
      all_args = all_args | set(x[0] for x in dataset)
    return all_args

@reads_type("model::ArgAnimatedBone")
class ArgAnimatedBone(ArgAnimationNode):
  @classmethod
  def read(cls, stream):
    self = super(ArgAnimatedBone, cls).read(stream)
    self.boneTransform = stream.read_matrixd()
    return self

@reads_type("model::ArgRotationNode")
class ArgRotationNode(ArgAnimationNode):
  """A special case of ArgAnimationNode with only rotational data.
  Despite this, it is written and read from disk in exactly the same way."""
  @classmethod
  def read(cls, stream):
    stream.mark_type_read("model::ArgAnimationNode")
    return super(ArgRotationNode, cls).read(stream)

  @classmethod
  def _read_AANRotationArg(cls, stream):
    stream.mark_type_read("model::ArgAnimationNode::Rotation")
    arg = stream.read_uint()
    count = stream.read_uint()
    keys = [get_type_reader("model::Key<key::ROTATION>")(stream) for _ in range(count)]
    return (arg, keys)

@reads_type("model::ArgPositionNode")
class ArgPositionNode(ArgAnimationNode):
  """A special case of ArgAnimationNode with only positional data.
  Despite this, it is written and read from disk in exactly the same way."""
  @classmethod
  def read(cls, stream):
    stream.mark_type_read("model::ArgAnimationNode")
    return super(ArgPositionNode, cls).read(stream)

  @classmethod
  def _read_AANPositionArg(cls, stream):
    stream.mark_type_read("model::ArgAnimationNode::Position")
    arg = stream.read_uint()
    count = stream.read_uint()
    keys = [get_type_reader("model::Key<key::POSITION>")(stream) for _ in range(count)]
    return (arg, keys)

@reads_type("model::ArgScaleNode")
class ArgScaleNode(ArgAnimationNode):
  @classmethod
  def read(cls, stream):
    stream.mark_type_read("model::ArgAnimationNode")
    return super(ArgScaleNode, cls).read(stream)

  @classmethod
  def _read_AANScaleArg(cls, stream):
    stream.mark_type_read("model::ArgAnimationNode::Scale")
    arg = stream.read_uint()
    count = stream.read_uint()
    # Weirdly seems to be two sets of keys; one with 4-components and one with three
    # keys = [get_type_reader("model::Key<key::SCALE>")(stream) for _ in range(count)]
    keys = [ScaleKey.read(stream, 4) for _ in range(count)]
    count2 = stream.read_uint()
    # Second set of keys only has three components...?
    key2s = [ScaleKey.read(stream, 3) for _ in range(count2)]
    # print("Edn of scale arg at ", steam.tell())
    return (arg, (keys, key2s))


@reads_type("model::Key<key::ROTATION>")
class RotationKey(object):
  def __init__(self, frame=None, value=None):
    self.frame = frame
    self.value = value
  @classmethod
  def read(cls, stream):
    self = cls()
    self.frame = stream.read_double()
    self.value = stream.read_quaternion()
    return self

  def __repr__(self):
    return "Key(frame={}, value={})".format(self.frame, repr(self.value))

@reads_type("model::Key<key::POSITION>")
class PositionKey(object):
  def __init__(self, frame=None, value=None):
    self.frame = frame
    self.value = value
  @classmethod
  def read(cls, stream):
    self = cls()
    self.frame = stream.read_double()
    self.value = Vector(stream.read_doubles(3))
    return self
  def __repr__(self):
    return "Key(frame={}, value={})".format(self.frame, repr(self.value))

@reads_type("model::Key<key::SCALE>")
class ScaleKey(object):
  @classmethod
  def read(cls, stream, entrylength):
    self = cls()
    self.frame = stream.read_double()
    self.value = Vector(stream.read_doubles(entrylength))
    return self
  def __repr__(self):
    return "Key(frame={}, value={})".format(self.frame, repr(self.value))

@reads_type("model::ArgVisibilityNode")
class ArgVisibilityNode(Node, AnimatingNode):
  @classmethod
  def read(cls, stream):
    self = super(ArgVisibilityNode, cls).read(stream)
    self.visData = stream.read_list(cls._read_AANVisibilityArg)
    return self

  @classmethod
  def _read_AANVisibilityArg(cls, stream):
    stream.mark_type_read("model::ArgVisibilityNode::Arg")
    arg = stream.read_uint()
    count = stream.read_uint()
    data = [stream.read_doubles(2) for _ in range(count)]
    stream.mark_type_read("model::ArgVisibilityNode::Range", count)
    return (arg, data)

  def audit(self):
    c = super(ArgVisibilityNode, self).audit()
    c["model::ArgVisibilityNode::Arg"] += len(self.visData)
    c["model::ArgVisibilityNode::Range"] += sum(len(x[1]) for x in self.visData)
    return c

@reads_type("model::LodNode")
class LodNode(Node):
  @classmethod
  def read(cls, stream):
    self = super(LodNode, cls).read(stream)
    count = stream.read_uint()
    self.level = [tuple(math.sqrt(x) for x in stream.read_doubles(2)) for x in range(count)]
    stream.mark_type_read("model::LodNode::Level", count)
    return self
  def audit(self):
    c = super(LodNode, self).audit()
    c["model::LodNode::Level"] += len(self.level)
    return c
  def write(self, stream):
    super(LodNode, self).write(stream)
    stream.write_uint(len(self.level))
    for low, high in self.level:
      stream.write_double(low**2)
      stream.write_double(high**2)

@reads_type("model::Connector")
class Connector(BaseNode):
  category = NodeCategory.connector
  def __init__(self):
    super(Connector, self).__init__()
    self.data = 0

  @classmethod
  def read(cls, stream):
    self = super(Connector, cls).read(stream)
    self.parent = stream.read_uint()
    self.data = stream.read_uint()
    return self

  def write(self, stream):
    super(Connector, self).write(stream)
    stream.write_uint(self.parent.index)
    stream.write_uint(self.data)


def _read_index_data(stream, classification=None):
  "Performs the common index-reading operation"
  dtPos = stream.tell()
  dataType = stream.read_uchar()
  entries = stream.read_uint()
  unknown = stream.read_uint()

  if dataType == 0:
    data = stream.read_uchars(entries)
    _bytes = entries
  elif dataType == 1:
    data = stream.read_ushorts(entries)
    _bytes = entries * 2
  elif dataType == 2:
    data = stream.read_uints(entries)
    _bytes = entries * 4
  else:
    raise IOError("Don't know how to read index data type {} @ {}".format(int(dataType), dtPos))

  if classification:
    stream.mark_type_read(classification, _bytes)

  return (unknown, data)

def _write_index_data(indexData, vertexDataLength, writer):
  # Index data
  if vertexDataLength < 256:
    writer.write_uchar(0)
    iWriter = writer.write_uchars
  elif vertexDataLength < 2**16:
    writer.write_uchar(1)
    iWriter = writer.write_ushorts
  elif vertexDataLength < 2**32:
    writer.write_uchar(2)
    iWriter = writer.write_uints
  else:
    raise IOError("Do not know how to write index arrays with {} members".format(vertexDataLength))

  writer.write_uint(len(indexData))
  writer.write_uint(5)
  iWriter(indexData)

def _read_vertex_data(stream, classification=None):
  count = stream.read_uint()
  stride = stream.read_uint()
  vtxData = stream.read_floats(count*stride)

  # If given a classification, mark it off
  if classification:
    stream.mark_type_read(classification, count*stride*4)

  # Group the vertex data according to stride
  vtxData = [vtxData[i:i+stride] for i in range(0, len(vtxData), stride)]
  return vtxData

def _write_vertex_data(data, writer):
  writer.write_uint(len(data))
  writer.write_uint(len(data[0]))
  flat_data = list(itertools.chain(*data))
  writer.write_floats(flat_data)

def _read_parent_data(stream):
    # Read the parent section
  parentCount = stream.read_uint()
  stream.mark_type_read("model::RNControlNode", parentCount-1)

  if parentCount == 1:
    return [[stream.read_uint(), stream.read_int()]]
  else:
    parentData = []
    for _ in range(parentCount):
      node = stream.read_uint()
      ranges = list(stream.read_ints(2))
      parentData.append((node, ranges[0], ranges[1]))
    return parentData

def _render_audit(self, verts="__gv_bytes", inds="__gi_bytes"):
  c = Counter()
  c[verts] += 4 * len(self.vertexData) * len(self.vertexData[0])
  # c["__gi_bytes"] += 
  if len(self.vertexData) < 256:
    c[inds] += len(self.indexData)
  elif len(self.vertexData) < 2**16:
    c[inds] += len(self.indexData) * 2
  elif len(self.vertexData) < 2**32:
    c[inds] += len(self.indexData) * 4
  else:
    raise IOError("Do not know how to write index arrays with {} members".format(len(self.indexData)))
  return c

@reads_type("model::RenderNode")
class RenderNode(BaseNode):
  category = NodeCategory.render

  def __init__(self, name=None):
    super(RenderNode, self).__init__(name)
    self.version = 1
    self.children = []
    self.unknown_start = 0
    self.material = None
    self.parentData = None
    self.parent = None
    self.vertexData = []
    self.unknown_indexPrefix = 5
    self.indexData = []
    # If e.g. split then we don't know the real name
    self.name_unknown = False

  def __repr__(self):
    return "<RenderNode \"{}\">".format(self.name)

  @classmethod
  def read(cls, stream):
    self = super(RenderNode, cls).read(stream)
    self.unknown_start = stream.read_uint()
    self.material = stream.read_uint()

    self.parentData = _read_parent_data(stream)

    # Read the vertex and index data
    self.vertexData = _read_vertex_data(stream, "__gv_bytes")
    self.unknown_indexPrefix, self.indexData = _read_index_data(stream, classification="__gi_bytes")

    return self

  def write(self, writer):
    super(RenderNode, self).write(writer)
    writer.write_uint(0)
    if not isinstance(self.material, int):
      self.material = self.material.index
    writer.write_uint(self.material)

    # Rebuild the parentdata
    writer.write_uint(1)
    writer.write_uint(self.parent.index)
    writer.write_int(-1)

    _write_vertex_data(self.vertexData, writer)
    _write_index_data(self.indexData, len(self.vertexData), writer)

  def audit(self):
    c = _render_audit(self)
    # We may, or may not, have any extra parent data at the moment.
    if self.parentData and len(self.parentData) > 1:
      c["model::RNControlNode"] += len(self.parentData)-1
    return c

  def split(self):
    """Returns an array of renderNode objects. If there is no splitting to be
    done, it will just return [self]. Otherwise, each entry is to be counted
    as a separate renderNode object. Attempting to resplit is undefined."""

    if self.parentData is None:
      raise RuntimeError("Attempting to split renderNode without parent data - has it already been split?")
    assert len(self.parentData) >= 1, "Should never have a RenderNode without parent data"
    
    # If one parent, no splitting to be done. Just assign our parent index.
    if len(self.parentData) == 1:
      self.parent = self.parentData[0][0]
      self.damage_argument = self.parentData[0][1]
      return [self]

    # We have more than one parent object. Do some splitting.
    # Make sure we cover the full length of the index array
    assert self.parentData[-1][-2] == len(self.indexData), "Split rendernode does not cover whole index range"

    start = 0
    children = []
    for i, (parent, idxTo, damageArg) in enumerate(self.parentData):
      node = RenderNode()
      node.version = self.version
      node.name = "{}_{}".format(self.name, i)
      node.name_unknown = True
      node.props = self.props
      node.material = self.material
      node.parent = parent
      node.indexData = self.indexData[start:idxTo]
      node.damage_argument = damageArg
      # Give them all the whole vertex subarray for now
      node.vertexData = self.vertexData
      start = idxTo
      children.append(node)

    return children

@reads_type("model::ShellNode")
class ShellNode(BaseNode):
  category = NodeCategory.shell
  @classmethod
  def read(cls, stream):
    self = super(ShellNode, cls).read(stream)
    self.parent = stream.read_uint()
    self.vertex_format = VertexFormat.read(stream)

    # Read the vertex and index data
    self.vertexData = _read_vertex_data(stream, "__cv_bytes")
    self.unknown_indexPrefix, self.indexData = _read_index_data(stream, classification="__ci_bytes")

    return self
  
  def audit(self):
    return _render_audit(self, verts="__cv_bytes", inds="__ci_bytes")

  def write(self, writer):
    super(ShellNode, self).write(writer)
    writer.write_uint(self.parent.index)
    self.vertex_format.write(writer)
    _write_vertex_data(self.vertexData, writer)
    _write_index_data(self.indexData, len(self.vertexData), writer)

  
@reads_type("model::SkinNode")
class SkinNode(BaseNode):
  category = NodeCategory.render
  @classmethod
  def read(cls, stream):
    self = super(SkinNode, cls).read(stream)
    self.unknown = stream.read_uint()
    self.material = stream.read_uint()

    boneCount = stream.read_uint()
    self.bones = stream.read_uints(boneCount)
    self.post_bone = stream.read_uint()

    # Read the vertex and index data
    self.vertexData = _read_vertex_data(stream, "__gv_bytes")
    self.unknown_indexPrefix, self.indexData = _read_index_data(stream, classification="__gi_bytes")

    return self

  def prepare(self, nodes, materials):
    self.bones = [nodes[x] for x in self.bones]

  def audit(self):
    return _render_audit(self)
  
@reads_type("model::SegmentsNode")
class SegmentsNode(BaseNode):
  category = NodeCategory.shell
  @classmethod
  def read(cls, stream):
    self = super(SegmentsNode, cls).read(stream)
    self.unknown = stream.read_uint()
    count = stream.read_uint()
    self.data = [stream.read_floats(6) for x in range(count)]
    stream.mark_type_read("model::SegmentsNode::Segments", count)
    return self

  def audit(self):
    c = super(SegmentsNode, self).audit()
    c["model::SegmentsNode::Segments"] += len(self.data)
    return c

@reads_type("model::BillboardNode")
class BillboardNode(Node):
  @classmethod
  def read(cls, stream):
    self = super(BillboardNode, cls).read(stream)
    self.data = stream.read(154)
    return self

@reads_type("model::LightNode")
class LightNode(BaseNode):
  category = NodeCategory.light
  @classmethod
  def read(cls, stream):
    self = super(LightNode, cls).read(stream)
    self.parent = stream.read_uint()
    self.unknown = [stream.read_uchar()]
    self.lightProps = PropertiesSet.read(stream, count=False)
    self.unknown.append(stream.read_uchar())
    return self

@reads_type("model::FakeSpotLightsNode")
class FakeSpotLightsNode(BaseNode):
  category = NodeCategory.render
  @classmethod
  def read(cls, stream):
    self = super(FakeSpotLightsNode, cls).read(stream)

    # Seems to start relatively similar to renderNode
    self.unknown_start = stream.read_uint()
    self.material_ish = stream.read_uint()

    # We have parent-like blocks of two uints + three floats
    controlNodeCount = stream.read_uint()

    self.parentData = []
    for _ in range(controlNodeCount):
      self.parentData.append([
          stream.read_uint(),
          stream.read_uint(),
          stream.read_floats(3)
        ])
    # Control node seems to follow same rules as RenderNode
    if controlNodeCount:
      stream.mark_type_read('model::FSLNControlNode', controlNodeCount-1)

    dataCount = stream.read_uint()
    self.data = [stream.read(65) for _ in range(dataCount)]
    stream.mark_type_read("model::FakeSpotLight", dataCount)

    # print(dataCount)
    return self

  def prepare(self, nodes, materials):
    pass

@reads_type("model::FakeOmniLightsNode")
class FakeOmniLightsNode(BaseNode):
  category = NodeCategory.render
  @classmethod
  def read(cls, stream):
    self = super(FakeOmniLightsNode, cls).read(stream)
    self.data_start = stream.read_uints(5)
    count = stream.read_uint()
    self.data = [stream.read_doubles(6) for _ in range(count)]
    stream.mark_type_read("model::FakeOmniLight", count)
    return self
  def prepare(self, nodes, materials):
    pass

@reads_type("model::FakeALSNode")
class FakeALSNode(BaseNode):
  category = NodeCategory.render
  @classmethod
  def read(cls, stream):
    self = super(FakeALSNode, cls).read(stream)
    # batumi.edm 1138915 x 340
    stream.read_uints(3)
    count = stream.read_uint()
    self.data = [stream.read(80) for _ in range(count)]
    stream.mark_type_read("model::FakeALSLight", count)
    return self

  def prepare(self, nodes, materials):
    pass