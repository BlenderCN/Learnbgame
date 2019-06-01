from .exception import URDFException
from .visual import Visual
from .collsion import Collision
from .inertial import Inertial

class Link:
  def __init__(self, name, visual=None, inertial=None, collision=None):
    self.name = name
    self.visual = visual
    self.inertial=inertial
    self.collision=collision

  @staticmethod
  def parse(node):
    link = Link(node.getAttribute('name'))
    for child in children(node):
      if child.localName == 'visual':
        link.visual = Visual.parse(child)
      elif child.localName == 'collision':
        link.collision = Collision.parse(child)
      elif child.localName == 'inertial':
        link.inertial = Inertial.parse(child)
      else:
        raise URDFException("Unknown link element '%s'"%child.localName)
          
    return link

  def to_xml(self, doc):
    xml = doc.createElement("link")
    xml.setAttribute("name", self.name)
    add( doc, xml, self.visual)
    add( doc, xml, self.collision)
    add( doc, xml, self.inertial)
    
    return xml
