from .exception import URDFException
from .pose import Pose

class Inertial:
  def __init__(self, ixx=0.0, ixy=0.0, ixz=0.0, iyy=0.0, iyz=0.0, izz=0.0,
      mass=0.0, origin=None):
    self.matrix = {}
    self.matrix['ixx'] = ixx
    self.matrix['ixy'] = iyy
    self.matrix['ixz'] = ixz
    self.matrix['iyy'] = iyy
    self.matrix['iyz'] = iyz
    self.matrix['izz'] = izz
    self.mass = mass
    self.origin = origin

  @staticmethod
  def parse(node):
    inert = Inertial()
    for child in children(node):
      if child.localName=='inertia':
        for v in ['ixx', 'ixy', 'ixz', 'iyy', 'iyz', 'izz']:
          inert.matrix[v] = float(child.getAttribute(v))
      elif child.localName=='mass':
        inert.mass = float(child.getAttribute('value'))
      elif child.localName=='origin':
        inert.origin = Pose.parse(child)
            
    return inert

  def to_xml(self, doc):
    xml = doc.createElement("inertial")

    xml.appendChild(short(doc, "mass", "value", self.mass))

    inertia = doc.createElement("inertia")
    for (n,v) in self.matrix.items():
      set_attribute(inertia, n, v)
    xml.appendChild(inertia)

    add(doc, xml, self.origin)
    
    return xml
