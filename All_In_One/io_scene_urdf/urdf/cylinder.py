from .exception import URDFException
from .geometry import Geometry

class Cylinder(Geometry):
  def __init__(self, radius=0.0, length=0.0):
    self.radius = radius
    self.length = length

  @staticmethod
  def parse(node):
    r = node.getAttribute('radius')
    l = node.getAttribute('length')
    
    return Cylinder(float(r), float(l))

  def to_xml(self, doc):
    xml = doc.createElement("cylinder")
    set_attribute(xml, "radius", self.radius)
    set_attribute(xml, "length", self.length)
    geom = doc.createElement('geometry')
    geom.appendChild(xml)
    
    return geom
