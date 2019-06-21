from .exception import URDFException

class JointCalibration:
  def __init__(self, rising=None, falling=None, reference=None):
    self.rising = rising
    self.falling = falling
    self.reference = reference

  @staticmethod
  def parse(node):
    jc = JointCalibration()
    if node.hasAttribute('rising'):
      jc.rising = float( node.getAttribute('rising') )
    if node.hasAttribute('falling'):
      jc.falling = float( node.getAttribute('falling') )
    if node.hasAttribute('reference'):
      jc.reference = float( node.getAttribute('reference') )
        
    return jc

  def to_xml(self, doc):
    xml = doc.createElement('calibration')
    set_attribute(xml, 'rising', self.rising)
    set_attribute(xml, 'falling', self.falling)
    set_attribute(xml, 'reference', self.reference)
    
    return xml
