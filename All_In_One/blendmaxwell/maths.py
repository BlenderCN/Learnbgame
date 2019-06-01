# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import math
from mathutils import Matrix, Vector, Quaternion
from bpy_extras import io_utils


def normalize(v, vmin, vmax):
    """Fits a value between minimum and maximum."""
    return (v - vmin) / (vmax - vmin)


def interpolate(nv, vmin, vmax):
    """Fit normalized value to range between minumum and maximum."""
    return vmin + (vmax - vmin) * nv


def map(v, min1, max1, min2, max2):
    """Converts one range definded by value, minimum and maximum (min1, max1) to different range definded by minimum and maximum (min2, max2)."""
    # return interpolate(normalize(v, min1, max1), min2, max2)
    return remap(v, min1, max1, min2, max2)


def remap(v, min1, max1, min2, max2):
    """Converts one range definded by value, minimum and maximum (min1, max1) to different range definded by minimum and maximum (min2, max2).
    Also this one solves a few errors, like value out of min1 - max1 range.."""
    v = clamp(v, min1, max1)
    r = interpolate(normalize(v, min1, max1), min2, max2)
    r = clamp(r, min2, max2)
    return r


def clamp(v, vmin, vmax):
    """Clamp value between min and max."""
    if(vmax <= vmin):
        raise ValueError("Maximum value is smaller than or equal to minimum.")
    if(v <= vmin):
        return vmin
    if(v >= vmax):
        return vmax
    return v


def maprange(v, ar, br, ):
    # http://rosettacode.org/wiki/Map_range#Python
    (a1, a2), (b1, b2) = ar, br
    return b1 + ((v - a1) * (b2 - b1) / (a2 - a1))


def rotation_to(a, b):
    """Calculates shortest Quaternion from Vector a to Vector b"""
    # a - up vector
    # b - direction to point to
    
    # http://stackoverflow.com/questions/1171849/finding-quaternion-representing-the-rotation-from-one-vector-to-another
    # https://github.com/toji/gl-matrix/blob/f0583ef53e94bc7e78b78c8a24f09ed5e2f7a20c/src/gl-matrix/quat.js#L54
    
    a = a.normalized()
    b = b.normalized()
    q = Quaternion()
    
    tmpvec3 = Vector()
    xUnitVec3 = Vector((1, 0, 0))
    yUnitVec3 = Vector((0, 1, 0))
    
    dot = a.dot(b)
    if(dot < -0.999999):
        # tmpvec3 = cross(xUnitVec3, a)
        tmpvec3 = xUnitVec3.cross(a)
        if(tmpvec3.length < 0.000001):
            tmpvec3 = yUnitVec3.cross(a)
        tmpvec3.normalize()
        # q = Quaternion(tmpvec3, Math.PI)
        q = Quaternion(tmpvec3, math.pi)
    elif(dot > 0.999999):
        q.x = 0
        q.y = 0
        q.z = 0
        q.w = 1
    else:
        tmpvec3 = a.cross(b)
        q.x = tmpvec3[0]
        q.y = tmpvec3[1]
        q.z = tmpvec3[2]
        q.w = 1 + dot
        q.normalize()
    return q


def eye_target_up_from_matrix(matrix, distance=1.0, ):
    eye = matrix.to_translation()
    target = matrix * Vector((0.0, 0.0, -distance))
    up = matrix * Vector((0.0, 1.0, 0.0)) - eye
    return eye, target, up


def shift_vert_along_normal(tco, tno, v):
    """Shifts Vector along Normal Vector"""
    co = Vector(tco)
    no = Vector(tno)
    return co + (no.normalized() * v)


def distance_vectors(a, b, ):
    """Distance between two 3d Vectors"""
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2) ** 0.5


def real_length_to_relative(matrix, length):
    """From matrix_world and desired real size length in meters, calculate relative length
    without matrix applied. Apply matrix, and you will get desired length."""
    l, r, s = matrix.decompose()
    ms = Matrix.Scale(s.x, 4)
    l = Vector((length, 0, 0))
    v = ms.inverted() * l
    return v.x


def apply_matrix(points, matrix):
    matrot = matrix.decompose()[1].to_matrix().to_4x4()
    r = [None] * len(points)
    for i, p in enumerate(points):
        co = matrix * Vector((p[0], p[1], p[2]))
        no = matrot * Vector((p[3], p[4], p[5]))
        r[i] = (co.x, co.y, co.z, no.x, no.y, no.z, p[6], p[7], p[8])
    return r


def unapply_matrix(points, matrix):
    m = matrix.inverted()
    return apply_matrix(points, m)
