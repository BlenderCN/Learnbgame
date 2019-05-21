from .exception import URDFException

class JointLimit:
    def __init__(self, effort, velocity, lower=None, upper=None):
      self.effort = effort
      self.velocity = velocity
      self.lower = lower
      self.upper = upper

    @staticmethod
    def parse(node):
      jl = JointLimit( float( node.getAttribute('effort') ) ,
        float( node.getAttribute('velocity')))
      if node.hasAttribute('lower'):
        jl.lower = float( node.getAttribute('lower') )
      if node.hasAttribute('upper'):
        jl.upper = float( node.getAttribute('upper') )
        
      return jl

    def to_xml(self, doc):
      xml = doc.createElement('limit')
      set_attribute(xml, 'effort', self.effort) 
      set_attribute(xml, 'velocity', self.velocity) 
      set_attribute(xml, 'lower', self.lower) 
      set_attribute(xml, 'upper', self.upper) 
      
      return xml

    def __str__(self):
      if self.lower is not None:
        return "[%f, %f]"%(self.lower, self.upper)
      else:
        return "limit"
