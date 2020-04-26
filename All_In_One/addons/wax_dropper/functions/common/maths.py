# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
from mathutils import Matrix, Vector

# module imports
from .wrappers import blender_version_wrapper


@blender_version_wrapper('<=','2.79')
def mathutils_mult(*argv):
    """ elementwise multiplication for vectors, matrices, etc. """
    result = argv[0]
    for arg in argv[1:]:
        result = arg * result
    return result
@blender_version_wrapper('>=','2.80')
def mathutils_mult(*argv):
    """ elementwise multiplication for vectors, matrices, etc. """
    result = argv[0]
    for arg in argv[1:]:
        result = arg @ result
    return result


def vec_mult(v1:Vector, v2:Vector):
    """ componentwise multiplication for vectors """
    return Vector(e1 * e2 for e1, e2 in zip(v1, v2))


def vec_div(v1:Vector, v2:Vector):
    """ componentwise division for vectors """
    return Vector(e1 / e2 for e1, e2 in zip(v1, v2))


def vec_remainder(v1:Vector, v2:Vector):
    """ componentwise remainder for vectors """
    return Vector(e1 % e2 for e1, e2 in zip(v1, v2))


def vec_abs(v1:Vector):
    """ componentwise absolute value for vectors """
    return Vector(abs(e1) for e1 in v1)


def vec_conv(v1, innerType:type=int, outerType:type=Vector):
    """ convert type of items in iterable """
    return outerType([innerType(x) for x in v1])


def vec_round(v1:Vector, precision:int=0):
    """ round items in vector """
    return Vector(round(e1, precision) for e1 in v1)


def mean(lst:list):
    """ mean of a list """
    return sum(lst)/len(lst)


def round_nearest(num:float, divisor:int):
    """ round to nearest multiple of 'divisor' """
    rem = num % divisor
    if rem > divisor / 2:
        return round_up(num, divisor)
    else:
        return round_down(num, divisor)


def round_up(num:float, divisor:int):
    """ round up to nearest multiple of 'divisor' """
    return num + divisor - (num % divisor)


def round_down(num:float, divisor:int):
    """ round down to nearest multiple of 'divisor' """
    return num - (num % divisor)
