from .exception import URDFException
from .pose import Pose
from .dynamics import Dynamics
from .joint_limit import JointLimit
from .joint_calibration import JointCalibration
from .joint_mimic import JointMimic
from .safety_controller import SafetyController

class Joint:
  def __init__(self, name, parent, child, joint_type, axis=None, origin=None,
        limits=None, dynamics=None, safety=None, calibration=None, mimic=None):
    self.name = name
    self.parent = parent
    self.child = child
    self.joint_type = joint_type
    self.axis = axis
    self.origin = origin
    self.limits = limits
    self.dynamics = dynamics
    self.safety = safety
    self.calibration = calibration
    self.mimic = mimic

  @staticmethod
  def parse(node):
    joint = Joint(node.getAttribute('name'), None, None,
      node.getAttribute('type'))
    for child in children(node):
      if child.localName == 'parent':
        joint.parent = child.getAttribute('link')
      elif child.localName == 'child':
        joint.child = child.getAttribute('link')
      elif child.localName == 'axis':
        joint.axis = child.getAttribute('xyz')
      elif child.localName == 'origin':
        joint.origin = Pose.parse(child)
      elif child.localName == 'limit':
        joint.limits = JointLimit.parse(child)
      elif child.localName == 'dynamics':
        joint.dynamics = Dynamics.parse(child)
      elif child.localName == 'safety_controller':
        joint.safety = SafetyController.parse(child)
      elif child.localName == 'calibration':
        joint.calibration = JointCalibration.parse(child)
      elif child.localName == 'mimic':
        joint.mimic = JointMimic.parse(child)
      else:
        raise URDFException("Unknown joint element '%s'"%child.localName)
          
    return joint

  def to_xml(self, doc):
    xml = doc.createElement("joint")
    set_attribute(xml, "name", self.name)
    set_attribute(xml, "type", self.joint_type)
    xml.appendChild( short(doc, "parent", "link", self.parent) )
    xml.appendChild( short(doc, "child" , "link", self.child ) )
    add(doc, xml, self.origin)
    if self.axis is not None:
      xml.appendChild( short(doc, "axis", "xyz", self.axis) )
    add(doc, xml, self.limits)
    add(doc, xml, self.dynamics)
    add(doc, xml, self.safety)
    add(doc, xml, self.calibration)
    
    return xml
