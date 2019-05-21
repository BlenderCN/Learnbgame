### BEGIN GPL LICENSE BLOCK #####
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

# <pep8 compliant>

import math, mathutils
from symbol import *
from converter import Expression
from blender_data import *


### Scalar Math ###

def radians(x):
    return math.radians(x)

def degrees(x):
    return math.degrees(x)

def sin(x):
    return math.sin(x)

def cos(x):
    return math.cos(x)

def tan(x):
    return math.tan(x)

def sincos(x):
    return math.sin(x), math.cos(x)

def asin(x):
    return math.asin(x)

def acos(x):
    return math.acos(x)

def atan(x):
    return math.atan(x)

def atan2(y, x):
    return math.atan2(y, x)

def sinh(x):
    return math.sinh(x)

def cosh(x):
    return math.cosh(x)

def tanh(x):
    return math.tanh(x)

def pow(x, y):
    return math.pow(x, y) if x >= 0.0 else 0.0

def exp(x):
    return math.exp(x)

def exp2(x):
    return math.pow(2, x)

def expm1(x):
    return math.expm1(x, y)

def log(x):
    if x <= 0.0:
        return 0.0
    else:
        return math.log(x)

def log2(x):
    if x <= 0.0:
        return 0.0
    else:
        return math.log(x, 2)

def log10(x):
    if x <= 0.0:
        return 0.0
    else:
        return math.log(x, 10)

def log_var(x, b):
    if x <= 0.0 or b <= 0.0:
        return 0.0
    else:
        return math.log(x, b)

def logb(x):
    if x <= 0.0:
        return 0.0
    else:
        return math.frexp(x)[1]

def floor(x):
    return math.floor(x)

def ceil(x):
    return math.ceil(x)

def round(x):
    return math.floor(x + 0.5)

def trunc(x):
    return math.trunc(x)

def fmod(x, y):
    return math.fmod(x, y)

def mod(x, y):
    return x % y

def sqrt(x):
    return math.sqrt(x)

def inversesqrt(x):
    return 1.0 / math.sqrt(x)

def hypot2(x, y):
    return math.hypot(x)

def hypot3(x, y, z):
    return math.sqrt(x*x + y*y + z*z)

def abs(x):
    return math.fabs(x)

def sign(x):
    return 1 if x > 0.0 else (0 if x == 0.0 else -1)

def blang_min(x, y):
    return min(x, y)

def blang_max(x, y):
    return max(x, y)

def clamp(x, a, b):
    return min(max(x, a), b)

def mix(x, y, a):
    return x*(1.0-a) + y*a

### Vector Math ###

def dot(a, b):
    return a.dot(b)

def cross(a, b):
    return a.cross(b)

def length(v):
    return v.length

def distance(a, b):
    return (b-a).length

### Blender Data ###

import bpy
from grammar import rna_path_parser
from driver import object_add_driver
from modgrammar import ParseError


def bdata(__object__, path):
    try:
        result = rna_path_parser.parse_text(path, reset=True, eof=True)
    except ParseError as err:
        print("Error: line %d: %s" % (err.line, err.message))
        split_buffer = err.buffer.split('\n')
        print(split_buffer[err.line])
        if err.col > 0:
            print("%s^" % (" " * (err.col-1) if err.col > 0 else "",))
        result = None
    if result is None:
        return None

    object_add_driver(__object__, result.base, result.struct_path, result.prop, result.prop_index)

    path = rna_path_value(result.base, result.struct_path, result.prop, result.prop_index)
    value = eval(str(path))
    return value
