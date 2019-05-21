from .exception import URDFException
from .color import Color

class Material:
  def __init__(self, name=None, color=None, texture=None):
    self.name = name
    self.color = color
    self.texture = texture

  @staticmethod
  def parse(node):
    material = Material()
    if node.hasAttribute('name'):
      material.name = node.getAttribute('name')
    for child in children(node):
      if child.localName == 'color':
        material.color = Color.parse(child)
      elif child.localName == 'texture':
        material.texture = child.getAttribute('filename')
      else:
        raise URDFException("Unknown material element '%s'"%child.localName)

    return material

  def to_xml(self, doc):
    xml = doc.createElement("material")
    set_attribute(xml, "name", self.name)
    add( doc, xml, self.color )

    if self.texture is not None:
      text = doc.createElement("texture")
      text.setAttribute('filename', self.texture)
      xml.appendChild(text)
        
    return xml
