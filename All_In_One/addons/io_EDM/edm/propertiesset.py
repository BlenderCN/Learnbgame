

from collections import OrderedDict, Counter
from .mathtypes import Vector

class PropertiesSet(OrderedDict):
  @classmethod
  def read(cls, stream, count=True):
    data = cls()
    length = stream.read_uint()
    for _ in range(length):
      prop = stream.read_named_type()
      # Handle regular and animated properties sets the same
      if hasattr(prop, "keys"):
        data[prop.name] = prop.keys
      else:
        data[prop.name] = prop.value
    # This only counts towards the general count if we had data
    if data and count:
      stream.mark_type_read("model::PropertiesSet")

    return data

  def write(self, writer):
    writer.write_uint(len(self))
    for key, value in self.items():
      if type(value) == float:
        writer.write_string("model::Property<float>")
        writer.write_string(key)
        writer.write_float(value)
      elif type(value) == int:
        writer.write_string("model::Property<unsigned int>")
        writer.write_string(key)
        writer.write_uint(value)
      elif type(value) == Vector:
        typeName = "model::Property<osg::Vec{}f>".format(len(value))
        writer.write_string(typeName)
        writer.write_string(key)
        writer.write_vecf(value)
      else:
        raise IOError("Don't know how to write property {}/{}".format(value, type(value)))

  def audit(self):
    c = Counter()
    for entry in self.values():
      if isinstance(entry, Vector):
        c["model::Property<osg::Vec{}f>".format(len(entry))] += 1
      elif isinstance(entry, int):
        c["model::Property<unsigned int>"] += 1
      elif isinstance(entry, float):
        c["model::Property<float>"] += 1
      elif isinstance(entry, str):
        c["model::Property<const char*>"] += 1
      else:
        raise IOError("Do not know how to audit uniform property {}".format(entry))
    return c
