from .exception import URDFException
from .box import Box
from .cylinder import Cylinder
from .sphere import Sphere
from .mesh import Mesh

class Geometry:
  def __init__(self):
    None

  @staticmethod
  def parse(node):
    shape = children(node)[0]
    if shape.localName=='box':
      return Box.parse(shape)
    elif shape.localName=='cylinder':
      return Cylinder.parse(shape)
    elif shape.localName=='sphere':
      return Sphere.parse(shape)
    elif shape.localName=='mesh':
      return Mesh.parse(shape)
    else:
      raise URDFException("Unknown shape %s"%child.localName)
