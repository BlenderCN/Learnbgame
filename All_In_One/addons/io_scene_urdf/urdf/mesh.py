from .exception import URDFException
from .geometry import Geometry

class Mesh(Geometry):
  def __init__(self, filename=None, scale=None):
    self.filename = filename
    self.scale = scale

  @staticmethod
  def parse(node):
    fn = node.getAttribute('filename')
    s = node.getAttribute('scale')
    if s == "":
      s = None
    else:
      xyz = node.getAttribute('scale').split()
      scale = list(map(float, xyz))
        
    return Mesh(fn, s)

  def to_xml(self, doc):
    xml = doc.createElement("mesh")
    set_attribute(xml, "filename", self.filename)
    set_attribute(xml, "scale", self.scale)
    geom = doc.createElement('geometry')
    geom.appendChild(xml)
    
    return geom
