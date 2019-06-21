# This file is part of Hypermesh.
#
# Hypermesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hypermesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hypermesh.  If not, see <http://www.gnu.org/licenses/>.

from mathutils import Vector
import numpy

# variable names: h   for hypersettings
#                 p,q for points in 4-space
#                 a,b for points in 3-space


# input is a HyperPreset object, and a Vector
def map4to3(h, p):
    if h.perspective:
        direction = p - Vector(h.viewcenter) - Vector(h.cameraoffset)
    else:
        direction = Vector(h.cameraoffset)
    m = numpy.matrix(
        [Vector(h.xvec),
         Vector(h.yvec),
         Vector(h.zvec),
         direction])
    m = m.transpose()
    result = numpy.linalg.solve(m, p - Vector(h.viewcenter))
    result = result[:3]
    return Vector(result)


# input is a HyperPreset object, and a Vector
def map3to4(h, a):
    vc = Vector(h.viewcenter)
    xv = Vector(h.xvec)
    yv = Vector(h.yvec)
    zv = Vector(h.zvec)
    return vc + a.x * xv + a.y * yv + a.z * zv


# input is a HyperPreset object, the 3-dimensional position
# and the previous 4-dimensional position
def map4to4(h, a, p):
    a4 = map3to4(h, a)
    q = map3to4(h, map4to3(h, p))
    if h.perspective:
        cam = Vector(h.viewcenter) + Vector(h.cameraoffset)
        factor = (p - cam).length / (q - cam).length
    else:
        factor = 1.0
    return p + factor * (a4 - q)
