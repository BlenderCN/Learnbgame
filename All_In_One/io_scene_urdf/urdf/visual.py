from .exception import URDFException
from .geometry import Geometry
from .pose import Pose
from .material import Material

class Visual:
  def __init__(self, geometry=None, material=None, origin=None):
    self.geometry = geometry
    self.material = material
    self.origin = origin

  @staticmethod
  def parse(node):
    v = Visual()
    for child in children(node):
      if child.localName == 'geometry':
        v.geometry = Geometry.parse(child)
      elif child.localName == 'origin':
        v.origin = Pose.parse(child)
      elif child.localName == 'material':
        v.material = Material.parse(child)
      else:
        raise URDFException("Unknown visual element '%s'"%child.localName)
      
    return v

  def to_xml(self, doc):
    xml = doc.createElement("visual")
    add( doc, xml, self.geometry )
    add( doc, xml, self.origin )
    add( doc, xml, self.material )
    
    return xml
