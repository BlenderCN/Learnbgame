from .exception import URDFException

class Dynamics:
  def __init__(self, damping=None, friction=None):
    self.damping = damping
    self.friction = friction

  @staticmethod
  def parse(node):
    d = Dynamics()
    if node.hasAttribute('damping'):
      d.damping = node.getAttribute('damping')
    if node.hasAttribute('friction'):
      d.friction = node.getAttribute('friction')
        
    return d

  def to_xml(self, doc):
    xml = doc.createElement('dynamics')
    set_attribute(xml, 'damping', self.damping)
    set_attribute(xml, 'friction', self.friction)
    
    return xml
