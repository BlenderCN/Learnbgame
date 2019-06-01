'''Math Types & Utilities (mathutils)
   This module provides access to math operations.
   .. note::
   Classes, methods and attributes that accept vectors also accept other numeric sequences,
   such as tuples, lists.
   Submodules:
   .. toctree::
   :maxdepth: 1
   mathutils.geometry.rst
   mathutils.bvhtree.rst
   mathutils.kdtree.rst
   mathutils.interpolate.rst
   mathutils.noise.rst
   The :mod:mathutils module provides the following classes:
   - Color,
   - Euler,
   - Matrix,
   - Quaternion,
   - Vector,
   
'''


class Color:
   '''.. class:: Color(rgb)
      This object gives access to Colors in Blender.
      :param rgb: (r, g, b) color values
      
   '''

   def copy():
      '''Returns a copy of this color.
         
         @returns (mathutils.Color): A copy of the color.
         Note: use this to get a copy of a wrapped color withno reference to the original data.
         
      '''
   
      return mathutils.Color
   

   def freeze():
      '''Make this object immutable.
         After this the object can be hashed, used in dictionaries & sets.
         
         @returns: An instance of this object.
      '''
   
      pass
   

   b = float
   '''Blue color channel.
      
   '''
   

   g = float
   '''Green color channel.
      
   '''
   

   h = float
   '''HSV Hue component in [0, 1].
      
   '''
   

   hsv = (float, float, float)
   '''HSV Values in [0, 1].
      
   '''
   

   is_frozen = bool
   '''True when this object has been frozen (read-only).
      
   '''
   

   is_wrapped = bool
   '''True when this object wraps external data (read-only).
      
   '''
   

   owner = None
   '''The item this is wrapping or None  (read-only).
      
   '''
   

   r = float
   '''Red color channel.
      
   '''
   

   s = float
   '''HSV Saturation component in [0, 1].
      
   '''
   

   v = float
   '''HSV Value component in [0, 1].
      
   '''
   



class Euler:
   '''.. class:: Euler(angles, order='XYZ')
      This object gives access to Eulers in Blender.
      :param angles: Three angles, in radians.
      :param order: Optional order of the angles, a permutation of XYZ.
      
   '''

   def copy():
      '''Returns a copy of this euler.
         
         @returns (mathutils.Euler): A copy of the euler.
         Note: use this to get a copy of a wrapped euler withno reference to the original data.
         
      '''
   
      return mathutils.Euler
   

   def freeze():
      '''Make this object immutable.
         After this the object can be hashed, used in dictionaries & sets.
         
         @returns: An instance of this object.
      '''
   
      pass
   

   def make_compatible(other):
      '''Make this euler compatible with another,
         so interpolating between them works as intended.
         
         Note: the rotation order is not taken into account for this function.
      '''
   
      pass
   

   def rotate(other):
      '''Rotates the euler by another mathutils value.
         
         Arguments:
         @other (Euler, Quaternion or Matrix): rotation component of mathutils value
   
      '''
   
      pass
   

   def rotate_axis(axis, angle):
      '''Rotates the euler a certain amount and returning a unique euler rotation
         (no 720 degree pitches).
         
         Arguments:
         @axis (string): single character in ['X, 'Y', 'Z'].
         @angle (float): angle in radians.
   
      '''
   
      pass
   

   def to_matrix():
      '''Return a matrix representation of the euler.
         
         @returns (mathutils.Matrix): A 3x3 roation matrix representation of the euler.
      '''
   
      return mathutils.Matrix
   

   def to_quaternion():
      '''Return a quaternion representation of the euler.
         
         @returns (mathutils.Quaternion): Quaternion representation of the euler.
      '''
   
      return mathutils.Quaternion
   

   def zero():
      '''Set all values to zero.
         
      '''
   
      pass
   

   is_frozen = bool
   '''True when this object has been frozen (read-only).
      
   '''
   

   is_wrapped = bool
   '''True when this object wraps external data (read-only).
      
   '''
   

   order = str #in ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']
   '''Euler rotation order.
      
   '''
   

   owner = None
   '''The item this is wrapping or None  (read-only).
      
   '''
   

   x = float
   '''Euler axis angle in radians.
      
   '''
   

   y = float
   '''Euler axis angle in radians.
      
   '''
   

   z = float
   '''Euler axis angle in radians.
      
   '''
   



class Matrix:
   '''.. class:: Matrix([rows])
      This object gives access to Matrices in Blender, supporting square and rectangular
      matrices from 2x2 up to 4x4.
      :param rows: Sequence of rows.
      When ommitted, a 4x4 identity matrix is constructed.
      
   '''

   @classmethod
   def Identity(size):
      '''Create an identity matrix.
         
         Arguments:
         @size (int): The size of the identity matrix to construct [2, 4].
   
         @returns (mathutils.Matrix): A new identity matrix.
      '''
   
      return mathutils.Matrix
   

   @classmethod
   def OrthoProjection(axis, size):
      '''Create a matrix to represent an orthographic projection.
         
         Arguments:
         @axis (string or Vector): Can be any of the following: ['X', 'Y', 'XY', 'XZ', 'YZ'],where a single axis is for a 2D matrix.
         Or a vector for an arbitrary axis
         
         @size (int): The size of the projection matrix to construct [2, 4].
   
         @returns (mathutils.Matrix): A new projection matrix.
      '''
   
      return mathutils.Matrix
   

   @classmethod
   def Rotation(angle, size, axis):
      '''Create a matrix representing a rotation.
         
         Arguments:
         @angle (float): The angle of rotation desired, in radians.
         @size (int): The size of the rotation matrix to construct [2, 4].
         @axis (string or Vector): a string in ['X', 'Y', 'Z'] or a 3D Vector Object(optional when size is 2).
         
   
         @returns (mathutils.Matrix): A new rotation matrix.
      '''
   
      return mathutils.Matrix
   

   @classmethod
   def Scale(factor, size, axis):
      '''Create a matrix representing a scaling.
         
         Arguments:
         @factor (float): The factor of scaling to apply.
         @size (int): The size of the scale matrix to construct [2, 4].
         @axis (Vector): Direction to influence scale. (optional).
   
         @returns (mathutils.Matrix): A new scale matrix.
      '''
   
      return mathutils.Matrix
   

   @classmethod
   def Shear(plane, size, factor):
      '''Create a matrix to represent an shear transformation.
         
         Arguments:
         @plane (string): Can be any of the following: ['X', 'Y', 'XY', 'XZ', 'YZ'],where a single axis is for a 2D matrix only.
         
         @size (int): The size of the shear matrix to construct [2, 4].
         @factor (float or float pair): The factor of shear to apply. For a 3 or 4 *size* matrixpass a pair of floats corresponding with the *plane* axis.
         
   
         @returns (mathutils.Matrix): A new shear matrix.
      '''
   
      return mathutils.Matrix
   

   @classmethod
   def Translation(vector):
      '''Create a matrix representing a translation.
         
         Arguments:
         @vector (Vector): The translation vector.
   
         @returns (mathutils.Matrix): An identity matrix with a translation.
      '''
   
      return mathutils.Matrix
   

   def adjugate():
      '''Set the matrix to its adjugate.
         
         Note: When the matrix cannot be adjugated a ValueError exception is raised.
         (seealso Adjugate matrix <https://en.wikipedia.org/wiki/Adjugate_matrix> on Wikipedia.)
         
      '''
   
      pass
   

   def adjugated():
      '''Return an adjugated copy of the matrix.
         
         @returns (mathutils.Matrix): the adjugated matrix.
         Note: When the matrix cant be adjugated a ValueError exception is raised.
      '''
   
      return mathutils.Matrix
   

   def copy():
      '''Returns a copy of this matrix.
         
         @returns (mathutils.Matrix): an instance of itself
      '''
   
      return mathutils.Matrix
   

   def decompose():
      '''Return the translation, rotation and scale components of this matrix.
         
         @returns ((Vector, Quaternion, Vector)): trans, rot, scale triple.
      '''
   
      return (Vector, Quaternion, Vector)
   

   def determinant():
      '''Return the determinant of a matrix.
         
         @returns (float): Return the determinant of a matrix.
         (seealso Determinant <https://en.wikipedia.org/wiki/Determinant> on Wikipedia.)
         
      '''
   
      return float
   

   def freeze():
      '''Make this object immutable.
         After this the object can be hashed, used in dictionaries & sets.
         
         @returns: An instance of this object.
      '''
   
      pass
   

   def identity():
      '''Set the matrix to the identity matrix.
         
         Note: An object with a location and rotation of zero, and a scale of onewill have an identity matrix.
         
         (seealso Identity matrix <https://en.wikipedia.org/wiki/Identity_matrix> on Wikipedia.)
         
      '''
   
      pass
   

   def invert(fallback=None):
      '''Set the matrix to its inverse.
         
         Arguments:
         @fallback (Matrix): Set the matrix to this value when the inverse cannot be calculated(instead of raising a ValueError exception).
         
   
         (seealso Inverse matrix <https://en.wikipedia.org/wiki/Inverse_matrix> on Wikipedia.)
         
      '''
   
      pass
   

   def invert_safe():
      '''Set the matrix to its inverse, will never error.
         If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
         If tweaked matrix is still degenerated, set to the identity matrix instead.
         
         (seealso Inverse Matrix <https://en.wikipedia.org/wiki/Inverse_matrix> on Wikipedia.)
         
      '''
   
      pass
   

   def inverted(fallback=None):
      '''Return an inverted copy of the matrix.
         
         Arguments:
         @fallback (any): return this when the inverse can't be calculated(instead of raising a ValueError).
         
   
         @returns (mathutils.Matrix): the inverted matrix or fallback when given.
      '''
   
      return mathutils.Matrix
   

   def inverted_safe():
      '''Return an inverted copy of the matrix, will never error.
         If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
         If tweaked matrix is still degenerated, return the identity matrix instead.
         
         @returns (mathutils.Matrix): the inverted matrix.
      '''
   
      return mathutils.Matrix
   

   def lerp(other, factor):
      '''Returns the interpolation of two matrices.
         
         Arguments:
         @other (Matrix): value to interpolate with.
         @factor (float): The interpolation value in [0.0, 1.0].
   
         @returns (mathutils.Matrix): The interpolated matrix.
      '''
   
      return mathutils.Matrix
   

   def normalize():
      '''Normalize each of the matrix columns.
         
      '''
   
      pass
   

   def normalized():
      '''Return a column normalized matrix
         
         @returns (mathutils.Matrix): a column normalized matrix
      '''
   
      return mathutils.Matrix
   

   def resize_4x4():
      '''Resize the matrix to 4x4.
         
      '''
   
      pass
   

   def rotate(other):
      '''Rotates the matrix by another mathutils value.
         
         Arguments:
         @other (Euler, Quaternion or Matrix): rotation component of mathutils value
   
         Note: If any of the columns are not unit length this may not have desired results.
      '''
   
      pass
   

   def to_3x3():
      '''Return a 3x3 copy of this matrix.
         
         @returns (mathutils.Matrix): a new matrix.
      '''
   
      return mathutils.Matrix
   

   def to_4x4():
      '''Return a 4x4 copy of this matrix.
         
         @returns (mathutils.Matrix): a new matrix.
      '''
   
      return mathutils.Matrix
   

   def to_euler(order, euler_compat):
      '''Return an Euler representation of the rotation matrix
         (3x3 or 4x4 matrix only).
         
         Arguments:
         @order (string): Optional rotation order argument in['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'].
         
         @euler_compat (Euler): Optional euler argument the new euler will be madecompatible with (no axis flipping between them).
         Useful for converting a series of matrices to animation curves.
         
   
         @returns (mathutils.Euler): Euler representation of the matrix.
      '''
   
      return mathutils.Euler
   

   def to_quaternion():
      '''Return a quaternion representation of the rotation matrix.
         
         @returns (mathutils.Quaternion): Quaternion representation of the rotation matrix.
      '''
   
      return mathutils.Quaternion
   

   def to_scale():
      '''Return the scale part of a 3x3 or 4x4 matrix.
         
         @returns (mathutils.Vector): Return the scale of a matrix.
         Note: This method does not return a negative scale on any axis because it is not possible to obtain this data from the matrix alone.
      '''
   
      return mathutils.Vector
   

   def to_translation():
      '''Return the translation part of a 4 row matrix.
         
         @returns (mathutils.Vector): Return the translation of a matrix.
      '''
   
      return mathutils.Vector
   

   def transpose():
      '''Set the matrix to its transpose.
         
         (seealso Transpose <https://en.wikipedia.org/wiki/Transpose> on Wikipedia.)
         
      '''
   
      pass
   

   def transposed():
      '''Return a new, transposed matrix.
         
         @returns (mathutils.Matrix): a transposed matrix
      '''
   
      return mathutils.Matrix
   

   def zero():
      '''Set all the matrix values to zero.
         
      '''
   
      return mathutils.Matrix
   

   col = Matrix Access
   '''Access the matix by colums, 3x3 and 4x4 only, (read-only).
      
   '''
   

   is_frozen = bool
   '''True when this object has been frozen (read-only).
      
   '''
   

   is_negative = bool
   '''True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).
      
   '''
   

   is_orthogonal = bool
   '''True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).
      
   '''
   

   is_orthogonal_axis_vectors = bool
   '''True if this matrix has got orthogonal axis vectors, 3x3 and 4x4 only, (read-only).
      
   '''
   

   is_wrapped = bool
   '''True when this object wraps external data (read-only).
      
   '''
   

   median_scale = float
   '''The average scale applied to each axis (read-only).
      
   '''
   

   owner = None
   '''The item this is wrapping or None  (read-only).
      
   '''
   

   row = Matrix Access
   '''Access the matix by rows (default), (read-only).
      
   '''
   

   translation = mathutils.Vector
   '''The translation component of the matrix.
      
   '''
   



class Quaternion:
   '''.. class:: Quaternion([seq, [angle]])
      This object gives access to Quaternions in Blender.
      :param seq: size 3 or 4
      :param angle: rotation angle, in radians
      The constructor takes arguments in various forms:
      (), *no args*
      Create an identity quaternion
      (*wxyz*)
      Create a quaternion from a (w, x, y, z) vector.
      (*exponential_map*)
      Create a quaternion from a 3d exponential map vector.
      
      (seealso :meth:to_exponential_map(*axis, angle*)
      Create a quaternion representing a rotation of *angle* radians over *axis*.
      )
      
   '''

   def conjugate():
      '''Set the quaternion to its conjugate (negate x, y, z).
         
      '''
   
      pass
   

   def conjugated():
      '''Return a new conjugated quaternion.
         
         @returns (mathutils.Quaternion): a new quaternion.
      '''
   
      return mathutils.Quaternion
   

   def copy():
      '''Returns a copy of this quaternion.
         
         @returns (mathutils.Quaternion): A copy of the quaternion.
         Note: use this to get a copy of a wrapped quaternion withno reference to the original data.
         
      '''
   
      return mathutils.Quaternion
   

   def cross(other):
      '''Return the cross product of this quaternion and another.
         
         Arguments:
         @other (Quaternion): The other quaternion to perform the cross product with.
   
         @returns (mathutils.Quaternion): The cross product.
      '''
   
      return mathutils.Quaternion
   

   def dot(other):
      '''Return the dot product of this quaternion and another.
         
         Arguments:
         @other (Quaternion): The other quaternion to perform the dot product with.
   
         @returns (mathutils.Quaternion): The dot product.
      '''
   
      return mathutils.Quaternion
   

   def freeze():
      '''Make this object immutable.
         After this the object can be hashed, used in dictionaries & sets.
         
         @returns: An instance of this object.
      '''
   
      pass
   

   def identity():
      '''Set the quaternion to an identity quaternion.
         
      '''
   
      return mathutils.Quaternion
   

   def invert():
      '''Set the quaternion to its inverse.
         
      '''
   
      pass
   

   def inverted():
      '''Return a new, inverted quaternion.
         
         @returns (mathutils.Quaternion): the inverted value.
      '''
   
      return mathutils.Quaternion
   

   def negate():
      '''Set the quaternion to its negative.
         
      '''
   
      return mathutils.Quaternion
   

   def normalize():
      '''Normalize the quaternion.
         
      '''
   
      pass
   

   def normalized():
      '''Return a new normalized quaternion.
         
         @returns (mathutils.Quaternion): a normalized copy.
      '''
   
      return mathutils.Quaternion
   

   def rotate(other):
      '''Rotates the quaternion by another mathutils value.
         
         Arguments:
         @other (Euler, Quaternion or Matrix): rotation component of mathutils value
   
      '''
   
      pass
   

   def rotation_difference(other):
      '''Returns a quaternion representing the rotational difference.
         
         Arguments:
         @other (Quaternion): second quaternion.
   
         @returns (mathutils.Quaternion): the rotational difference between the two quat rotations.
      '''
   
      return mathutils.Quaternion
   

   def slerp(other, factor):
      '''Returns the interpolation of two quaternions.
         
         Arguments:
         @other (Quaternion): value to interpolate with.
         @factor (float): The interpolation value in [0.0, 1.0].
   
         @returns (mathutils.Quaternion): The interpolated rotation.
      '''
   
      return mathutils.Quaternion
   

   def to_axis_angle():
      '''Return the axis, angle representation of the quaternion.
         
         @returns ((Vector, float) pair): axis, angle.
      '''
   
      return (Vector, float) pair
   

   def to_euler(order, euler_compat):
      '''Return Euler representation of the quaternion.
         
         Arguments:
         @order (string): Optional rotation order argument in['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'].
         
         @euler_compat (Euler): Optional euler argument the new euler will be madecompatible with (no axis flipping between them).
         Useful for converting a series of matrices to animation curves.
         
   
         @returns (mathutils.Euler): Euler representation of the quaternion.
      '''
   
      return mathutils.Euler
   

   def to_exponential_map():
      '''Return the exponential map representation of the quaternion.
         This representation consist of the rotation axis multiplied by the rotation angle.   Such a representation is useful for interpolation between multiple orientations.
         
         @returns (Vector of size 3): exponential map.To convert back to a quaternion, pass it to the Quaternion constructor.
         
      '''
   
      return Vector of size 3
   

   def to_matrix():
      '''Return a matrix representation of the quaternion.
         
         @returns (mathutils.Matrix): A 3x3 rotation matrix representation of the quaternion.
      '''
   
      return mathutils.Matrix
   

   angle = float
   '''Angle of the quaternion.
      
   '''
   

   axis = mathutils.Vector
   '''Quaternion axis as a vector.
      
   '''
   

   is_frozen = bool
   '''True when this object has been frozen (read-only).
      
   '''
   

   is_wrapped = bool
   '''True when this object wraps external data (read-only).
      
   '''
   

   magnitude = float
   '''Size of the quaternion (read-only).
      
   '''
   

   owner = None
   '''The item this is wrapping or None  (read-only).
      
   '''
   

   w = float
   '''Quaternion axis value.
      
   '''
   

   x = float
   '''Quaternion axis value.
      
   '''
   

   y = float
   '''Quaternion axis value.
      
   '''
   

   z = float
   '''Quaternion axis value.
      
   '''
   



class Vector:
   '''.. class:: Vector(seq)
      This object gives access to Vectors in Blender.
      :param seq: Components of the vector, must be a sequence of at least two
      
   '''

   @classmethod
   def Fill(size, fill=0.0):
      '''Create a vector of length size with all values set to fill.
         
         Arguments:
         @size (int): The length of the vector to be created.
         @fill (float): The value used to fill the vector.
   
      '''
   
      pass
   

   @classmethod
   def Linspace(start, stop, size):
      '''Create a vector of the specified size which is filled with linearly spaced values between start and stop values.
         
         Arguments:
         @start (int): The start of the range used to fill the vector.
         @stop (int): The end of the range used to fill the vector.
         @size (int): The size of the vector to be created.
   
      '''
   
      pass
   

   @classmethod
   def Range(start=0, stop, step=1):
      '''Create a filled with a range of values.
         
         Arguments:
         @start (int): The start of the range used to fill the vector.
         @stop (int): The end of the range used to fill the vector.
         @step (int): The step between successive values in the vector.
   
      '''
   
      pass
   

   @classmethod
   def Repeat(vector, size):
      '''Create a vector by repeating the values in vector until the required size is reached.
         
         Arguments:
         @tuple (mathutils.Vector): The vector to draw values from.
         @size (int): The size of the vector to be created.
   
      '''
   
      pass
   

   def angle(other, fallback=None):
      '''Return the angle between two vectors.
         
         Arguments:
         @other (Vector): another vector to compare the angle with
         @fallback (any): return this when the angle can't be calculated (zero length vector),(instead of raising a ValueError).
         
   
         @returns (float): angle in radians or fallback when given
      '''
   
      return float
   

   def angle_signed(other, fallback):
      '''Return the signed angle between two 2D vectors (clockwise is positive).
         
         Arguments:
         @other (Vector): another vector to compare the angle with
         @fallback (any): return this when the angle can't be calculated (zero length vector),(instead of raising a ValueError).
         
   
         @returns (float): angle in radians or fallback when given
      '''
   
      return float
   

   def copy():
      '''Returns a copy of this vector.
         
         @returns (mathutils.Vector): A copy of the vector.
         Note: use this to get a copy of a wrapped vector withno reference to the original data.
         
      '''
   
      return mathutils.Vector
   

   def cross(other):
      '''Return the cross product of this vector and another.
         
         Arguments:
         @other (Vector): The other vector to perform the cross product with.
   
         @returns (Vector or float when 2D vectors are used): The cross product.
         Note: both vectors must be 2D or 3D
      '''
   
      return Vector or float when 2D vectors are used
   

   def dot(other):
      '''Return the dot product of this vector and another.
         
         Arguments:
         @other (Vector): The other vector to perform the dot product with.
   
         @returns (mathutils.Vector): The dot product.
      '''
   
      return mathutils.Vector
   

   def freeze():
      '''Make this object immutable.
         After this the object can be hashed, used in dictionaries & sets.
         
         @returns: An instance of this object.
      '''
   
      pass
   

   def lerp(other, factor):
      '''Returns the interpolation of two vectors.
         
         Arguments:
         @other (Vector): value to interpolate with.
         @factor (float): The interpolation value in [0.0, 1.0].
   
         @returns (mathutils.Vector): The interpolated vector.
      '''
   
      return mathutils.Vector
   

   def negate():
      '''Set all values to their negative.
         
      '''
   
      pass
   

   def normalize():
      '''Normalize the vector, making the length of the vector always 1.0.
         .. warning:: Normalizing a vector where all values are zero has no effect.
         
         Note: Normalize works for vectors of all sizes,however 4D Vectors w axis is left untouched.
         
      '''
   
      pass
   

   def normalized():
      '''Return a new, normalized vector.
         
         @returns (mathutils.Vector): a normalized copy of the vector
      '''
   
      return mathutils.Vector
   

   def orthogonal():
      '''Return a perpendicular vector.
         
         @returns (mathutils.Vector): a new vector 90 degrees from this vector.
         Note: the axis is undefined, only use when any orthogonal vector is acceptable.
      '''
   
      return mathutils.Vector
   

   def project(other):
      '''Return the projection of this vector onto the *other*.
         
         Arguments:
         @other (Vector): second vector.
   
         @returns (mathutils.Vector): the parallel projection vector
      '''
   
      return mathutils.Vector
   

   def reflect(mirror):
      '''Return the reflection vector from the *mirror* argument.
         
         Arguments:
         @mirror (Vector): This vector could be a normal from the reflecting surface.
   
         @returns (mathutils.Vector): The reflected vector matching the size of this vector.
      '''
   
      return mathutils.Vector
   

   def resize(size=3):
      '''Resize the vector to have size number of elements.
         
      '''
   
      pass
   

   def resize_2d():
      '''Resize the vector to 2D  (x, y).
         
      '''
   
      pass
   

   def resize_3d():
      '''Resize the vector to 3D  (x, y, z).
         
      '''
   
      pass
   

   def resize_4d():
      '''Resize the vector to 4D (x, y, z, w).
         
      '''
   
      pass
   

   def resized(size=3):
      '''Return a resized copy of the vector with size number of elements.
         
         @returns (mathutils.Vector): a new vector
      '''
   
      return mathutils.Vector
   

   def rotate(other):
      '''Rotate the vector by a rotation value.
         
         Arguments:
         @other (Euler, Quaternion or Matrix): rotation component of mathutils value
   
      '''
   
      pass
   

   def rotation_difference(other):
      '''Returns a quaternion representing the rotational difference between this
         vector and another.
         
         Arguments:
         @other (Vector): second vector.
   
         @returns (mathutils.Quaternion): the rotational difference between the two vectors.
         Note: 2D vectors raise an AttributeError.
      '''
   
      return mathutils.Quaternion
   

   def slerp(other, factor, fallback=None):
      '''Returns the interpolation of two non-zero vectors (spherical coordinates).
         
         Arguments:
         @other (Vector): value to interpolate with.
         @factor (float): The interpolation value typically in [0.0, 1.0].
         @fallback (any): return this when the vector can't be calculated (zero length vector or direct opposites),(instead of raising a ValueError).
         
   
         @returns (mathutils.Vector): The interpolated vector.
      '''
   
      return mathutils.Vector
   

   def to_2d():
      '''Return a 2d copy of the vector.
         
         @returns (mathutils.Vector): a new vector
      '''
   
      return mathutils.Vector
   

   def to_3d():
      '''Return a 3d copy of the vector.
         
         @returns (mathutils.Vector): a new vector
      '''
   
      return mathutils.Vector
   

   def to_4d():
      '''Return a 4d copy of the vector.
         
         @returns (mathutils.Vector): a new vector
      '''
   
      return mathutils.Vector
   

   def to_track_quat(track, up):
      '''Return a quaternion rotation from the vector and the track and up axis.
         
         Arguments:
         @track (string): Track axis in ['X', 'Y', 'Z', '-X', '-Y', '-Z'].
         @up (string): Up axis in ['X', 'Y', 'Z'].
   
         @returns (mathutils.Quaternion): rotation from the vector and the track and up axis.
      '''
   
      return mathutils.Quaternion
   

   def to_tuple(precision=-1):
      '''Return this vector as a tuple with.
         
         Arguments:
         @precision (int): The number to round the value to in [-1, 21].
   
         @returns (tuple): the values of the vector rounded by *precision*
      '''
   
      return tuple
   

   def zero():
      '''Set all values to zero.
         
      '''
   
      pass
   

   is_frozen = bool
   '''True when this object has been frozen (read-only).
      
   '''
   

   is_wrapped = bool
   '''True when this object wraps external data (read-only).
      
   '''
   

   length = float
   '''Vector Length.
      
   '''
   

   length_squared = float
   '''Vector length squared (v.dot(v)).
      
   '''
   

   magnitude = float
   '''Vector Length.
      
   '''
   

   owner = None
   '''The item this is wrapping or None  (read-only).
      
   '''
   

   w = float
   '''Vector W axis (4D Vectors only).
      
   '''
   

   ww = None
   
   

   www = None
   
   

   wwww = None
   
   

   wwwx = None
   
   

   wwwy = None
   
   

   wwwz = None
   
   

   wwx = None
   
   

   wwxw = None
   
   

   wwxx = None
   
   

   wwxy = None
   
   

   wwxz = None
   
   

   wwy = None
   
   

   wwyw = None
   
   

   wwyx = None
   
   

   wwyy = None
   
   

   wwyz = None
   
   

   wwz = None
   
   

   wwzw = None
   
   

   wwzx = None
   
   

   wwzy = None
   
   

   wwzz = None
   
   

   wx = None
   
   

   wxw = None
   
   

   wxww = None
   
   

   wxwx = None
   
   

   wxwy = None
   
   

   wxwz = None
   
   

   wxx = None
   
   

   wxxw = None
   
   

   wxxx = None
   
   

   wxxy = None
   
   

   wxxz = None
   
   

   wxy = None
   
   

   wxyw = None
   
   

   wxyx = None
   
   

   wxyy = None
   
   

   wxyz = None
   
   

   wxz = None
   
   

   wxzw = None
   
   

   wxzx = None
   
   

   wxzy = None
   
   

   wxzz = None
   
   

   wy = None
   
   

   wyw = None
   
   

   wyww = None
   
   

   wywx = None
   
   

   wywy = None
   
   

   wywz = None
   
   

   wyx = None
   
   

   wyxw = None
   
   

   wyxx = None
   
   

   wyxy = None
   
   

   wyxz = None
   
   

   wyy = None
   
   

   wyyw = None
   
   

   wyyx = None
   
   

   wyyy = None
   
   

   wyyz = None
   
   

   wyz = None
   
   

   wyzw = None
   
   

   wyzx = None
   
   

   wyzy = None
   
   

   wyzz = None
   
   

   wz = None
   
   

   wzw = None
   
   

   wzww = None
   
   

   wzwx = None
   
   

   wzwy = None
   
   

   wzwz = None
   
   

   wzx = None
   
   

   wzxw = None
   
   

   wzxx = None
   
   

   wzxy = None
   
   

   wzxz = None
   
   

   wzy = None
   
   

   wzyw = None
   
   

   wzyx = None
   
   

   wzyy = None
   
   

   wzyz = None
   
   

   wzz = None
   
   

   wzzw = None
   
   

   wzzx = None
   
   

   wzzy = None
   
   

   wzzz = None
   
   

   x = float
   '''Vector X axis.
      
   '''
   

   xw = None
   
   

   xww = None
   
   

   xwww = None
   
   

   xwwx = None
   
   

   xwwy = None
   
   

   xwwz = None
   
   

   xwx = None
   
   

   xwxw = None
   
   

   xwxx = None
   
   

   xwxy = None
   
   

   xwxz = None
   
   

   xwy = None
   
   

   xwyw = None
   
   

   xwyx = None
   
   

   xwyy = None
   
   

   xwyz = None
   
   

   xwz = None
   
   

   xwzw = None
   
   

   xwzx = None
   
   

   xwzy = None
   
   

   xwzz = None
   
   

   xx = None
   
   

   xxw = None
   
   

   xxww = None
   
   

   xxwx = None
   
   

   xxwy = None
   
   

   xxwz = None
   
   

   xxx = None
   
   

   xxxw = None
   
   

   xxxx = None
   
   

   xxxy = None
   
   

   xxxz = None
   
   

   xxy = None
   
   

   xxyw = None
   
   

   xxyx = None
   
   

   xxyy = None
   
   

   xxyz = None
   
   

   xxz = None
   
   

   xxzw = None
   
   

   xxzx = None
   
   

   xxzy = None
   
   

   xxzz = None
   
   

   xy = None
   
   

   xyw = None
   
   

   xyww = None
   
   

   xywx = None
   
   

   xywy = None
   
   

   xywz = None
   
   

   xyx = None
   
   

   xyxw = None
   
   

   xyxx = None
   
   

   xyxy = None
   
   

   xyxz = None
   
   

   xyy = None
   
   

   xyyw = None
   
   

   xyyx = None
   
   

   xyyy = None
   
   

   xyyz = None
   
   

   xyz = None
   
   

   xyzw = None
   
   

   xyzx = None
   
   

   xyzy = None
   
   

   xyzz = None
   
   

   xz = None
   
   

   xzw = None
   
   

   xzww = None
   
   

   xzwx = None
   
   

   xzwy = None
   
   

   xzwz = None
   
   

   xzx = None
   
   

   xzxw = None
   
   

   xzxx = None
   
   

   xzxy = None
   
   

   xzxz = None
   
   

   xzy = None
   
   

   xzyw = None
   
   

   xzyx = None
   
   

   xzyy = None
   
   

   xzyz = None
   
   

   xzz = None
   
   

   xzzw = None
   
   

   xzzx = None
   
   

   xzzy = None
   
   

   xzzz = None
   
   

   y = float
   '''Vector Y axis.
      
   '''
   

   yw = None
   
   

   yww = None
   
   

   ywww = None
   
   

   ywwx = None
   
   

   ywwy = None
   
   

   ywwz = None
   
   

   ywx = None
   
   

   ywxw = None
   
   

   ywxx = None
   
   

   ywxy = None
   
   

   ywxz = None
   
   

   ywy = None
   
   

   ywyw = None
   
   

   ywyx = None
   
   

   ywyy = None
   
   

   ywyz = None
   
   

   ywz = None
   
   

   ywzw = None
   
   

   ywzx = None
   
   

   ywzy = None
   
   

   ywzz = None
   
   

   yx = None
   
   

   yxw = None
   
   

   yxww = None
   
   

   yxwx = None
   
   

   yxwy = None
   
   

   yxwz = None
   
   

   yxx = None
   
   

   yxxw = None
   
   

   yxxx = None
   
   

   yxxy = None
   
   

   yxxz = None
   
   

   yxy = None
   
   

   yxyw = None
   
   

   yxyx = None
   
   

   yxyy = None
   
   

   yxyz = None
   
   

   yxz = None
   
   

   yxzw = None
   
   

   yxzx = None
   
   

   yxzy = None
   
   

   yxzz = None
   
   

   yy = None
   
   

   yyw = None
   
   

   yyww = None
   
   

   yywx = None
   
   

   yywy = None
   
   

   yywz = None
   
   

   yyx = None
   
   

   yyxw = None
   
   

   yyxx = None
   
   

   yyxy = None
   
   

   yyxz = None
   
   

   yyy = None
   
   

   yyyw = None
   
   

   yyyx = None
   
   

   yyyy = None
   
   

   yyyz = None
   
   

   yyz = None
   
   

   yyzw = None
   
   

   yyzx = None
   
   

   yyzy = None
   
   

   yyzz = None
   
   

   yz = None
   
   

   yzw = None
   
   

   yzww = None
   
   

   yzwx = None
   
   

   yzwy = None
   
   

   yzwz = None
   
   

   yzx = None
   
   

   yzxw = None
   
   

   yzxx = None
   
   

   yzxy = None
   
   

   yzxz = None
   
   

   yzy = None
   
   

   yzyw = None
   
   

   yzyx = None
   
   

   yzyy = None
   
   

   yzyz = None
   
   

   yzz = None
   
   

   yzzw = None
   
   

   yzzx = None
   
   

   yzzy = None
   
   

   yzzz = None
   
   

   z = float
   '''Vector Z axis (3D Vectors only).
      
   '''
   

   zw = None
   
   

   zww = None
   
   

   zwww = None
   
   

   zwwx = None
   
   

   zwwy = None
   
   

   zwwz = None
   
   

   zwx = None
   
   

   zwxw = None
   
   

   zwxx = None
   
   

   zwxy = None
   
   

   zwxz = None
   
   

   zwy = None
   
   

   zwyw = None
   
   

   zwyx = None
   
   

   zwyy = None
   
   

   zwyz = None
   
   

   zwz = None
   
   

   zwzw = None
   
   

   zwzx = None
   
   

   zwzy = None
   
   

   zwzz = None
   
   

   zx = None
   
   

   zxw = None
   
   

   zxww = None
   
   

   zxwx = None
   
   

   zxwy = None
   
   

   zxwz = None
   
   

   zxx = None
   
   

   zxxw = None
   
   

   zxxx = None
   
   

   zxxy = None
   
   

   zxxz = None
   
   

   zxy = None
   
   

   zxyw = None
   
   

   zxyx = None
   
   

   zxyy = None
   
   

   zxyz = None
   
   

   zxz = None
   
   

   zxzw = None
   
   

   zxzx = None
   
   

   zxzy = None
   
   

   zxzz = None
   
   

   zy = None
   
   

   zyw = None
   
   

   zyww = None
   
   

   zywx = None
   
   

   zywy = None
   
   

   zywz = None
   
   

   zyx = None
   
   

   zyxw = None
   
   

   zyxx = None
   
   

   zyxy = None
   
   

   zyxz = None
   
   

   zyy = None
   
   

   zyyw = None
   
   

   zyyx = None
   
   

   zyyy = None
   
   

   zyyz = None
   
   

   zyz = None
   
   

   zyzw = None
   
   

   zyzx = None
   
   

   zyzy = None
   
   

   zyzz = None
   
   

   zz = None
   
   

   zzw = None
   
   

   zzww = None
   
   

   zzwx = None
   
   

   zzwy = None
   
   

   zzwz = None
   
   

   zzx = None
   
   

   zzxw = None
   
   

   zzxx = None
   
   

   zzxy = None
   
   

   zzxz = None
   
   

   zzy = None
   
   

   zzyw = None
   
   

   zzyx = None
   
   

   zzyy = None
   
   

   zzyz = None
   
   

   zzz = None
   
   

   zzzw = None
   
   

   zzzx = None
   
   

   zzzy = None
   
   

   zzzz = None
   
   



