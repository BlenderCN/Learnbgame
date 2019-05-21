from .node import Node
from .exception import URDFException
from .geometry import Geometry

class Sphere(Geometry):
  def __init__(self, radius=0.0):
    self.radius = radius

  @staticmethod
  def parse(node):
    r = node.getAttribute('radius')    
    return Sphere(float(r))

  def to_xml(self, doc):
    xml = doc.createElement("sphere")
    set_attribute(xml, "radius", self.radius)
    geom = doc.createElement('geometry')
    geom.appendChild(xml)
    
    return geom
