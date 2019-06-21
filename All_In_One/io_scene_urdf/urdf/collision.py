from .exception import URDFException
from .visual import Visual
from .geometry import Geometry
from .pose import Pose

class Collision:
  def __init__(self, geometry=None, origin=None):
    self.geometry = geometry
    self.origin = origin

  @staticmethod
  def parse(node):
    c = Collision()
    for child in children(node):
      if child.localName == 'geometry':
        c.geometry = Geometry.parse(child)
      elif child.localName == 'origin':
        c.origin = Pose.parse(child)
      else:
        raise URDFException("Unknown collision element '%s'"%child.localName)
          
    return c

  def to_xml(self, doc):
    xml = doc.createElement("collision")
    add(doc, xml, self.geometry)
    add(doc, xml, self.origin)
    
    return xml
