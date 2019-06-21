from .exception import URDFException

class Color:
  def __init__(self, r=0.0, g=0.0, b=0.0, a=0.0):
    self.rgba=(r,g,b,a)

  @staticmethod
  def parse(node):
    rgba = node.getAttribute("rgba").split()
    (r,g,b,a) = [ float(x) for x in rgba ]
    
    return Color(r,g,b,a)

  def to_xml(self, doc):
    xml = doc.createElement("color")
    set_attribute(xml, "rgba", self.rgba)
    
    return xml
