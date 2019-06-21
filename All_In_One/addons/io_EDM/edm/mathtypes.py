"""
Simple math types to represent Vector, Matrix, Quaternion

If the blender mathutils module is available, the blender API types are
used, but otherwise a (minimally) compatible internal type is used instead.

Also included are tools to create from simple lists, and convert between the
EDM and blender axis interpretations.
"""

import itertools

try:
  from mathutils import Matrix, Vector, Quaternion
except ImportError:
  # We don't have mathutils. Make some very basic replacements.
  class Vector(tuple):
    def __repr__(self):
      return "Vector({})".format(super(Vector, self).__repr__())
  class Matrix(tuple):
    def transposed(self):
      cols = [[self[j][i] for j in range(len(self))] for i in range(len(self))]
      return Matrix(cols)
    def __repr__(self):
      return "Matrix({})".format(super(Matrix, self).__repr__())

  class Quaternion(tuple):
    def ___repr__(self):
      return "Quaternion({})".format(super(Quaternion, self).__repr__())

def MatrixScale(vector):
  mat = Matrix.Scale(1,4)
  mat[0][0], mat[1][1], mat[2][2] = vector[:3]
  return mat

def sequence_to_matrix(seq):
  return Matrix([seq[:4], seq[4:8], seq[8:12], seq[12:16]]).transposed()

def matrix_to_sequence(mat):
  xp = mat.transposed()
  return tuple(itertools.chain(xp[0], xp[1], xp[2], xp[3]))

def sequence_to_quaternion(seq):
  return Quaternion((seq[3], seq[0], seq[1], seq[2]))

def matrix_to_blender(matrix):
  return Matrix([matrix[0], -matrix[2], matrix[1], matrix[3]])

def matrix_to_edm(matrix):
  return Matrix([matrix[0], matrix[2], -matrix[1], matrix[3]])

def vector_to_blender(v):
  return Vector([v[0], -v[2], v[1]])

def vector_to_edm(v):
  return Vector([v[0], v[2], -v[1]])
