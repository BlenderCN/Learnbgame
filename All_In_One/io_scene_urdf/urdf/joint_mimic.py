from .exception import URDFException

class JointMimic:
  def __init__(self, joint_name, multiplier=None, offset=None):
    self.joint_name = joint_name
    self.multiplier = multiplier
    self.offset = offset

  @staticmethod
  def parse(node):
    mimic = JointMimic( node.getAttribute('joint') ) 
    if node.hasAttribute('multiplier'):
      mimic.multiplier = float( node.getAttribute('multiplier') )
    if node.hasAttribute('offset'):
      mimic.offset = float( node.getAttribute('offset') )
      
    return mimic

  def to_xml(self, doc):
    xml = doc.createElement('mimic')
    set_attribute(xml, 'joint', self.joint_name) 
    set_attribute(xml, 'multiplier', self.multiplier) 
    set_attribute(xml, 'offset', self.offset) 
    
    return xml
