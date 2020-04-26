# -*- coding: utf-8 -*-
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

# Common Swappers
# By Matti 'Menithal' Lahtinen


from mathutils import Quaternion, Vector, Euler, Matrix
from math import sqrt, acos, pow, sin, cos

NEAREST_DIGIT = 10000
'x,y,z'
ZERO_VECTOR = (0,0,0)
'x,y,z'
PIVOT_VECTOR = (0.5,0.5,0.5)
'w,x,y,z'
ZERO_QUAT = (1,0,0,0)


# Utility to round to nearest digit. Hifi exports some times so fairly erroronious floats, so truncating them can help
## TODO: Allow scene to set to what digit should everything be rouded to
def round_nearest(val):
    return round(val * NEAREST_DIGIT)/NEAREST_DIGIT

# Utility to make sure a tuple is returned from a dict
def parse_dict_vector(entity, index, default = ZERO_VECTOR):
    if index in entity:
        vect = entity[index]
        return (round_nearest(vect['x']), round_nearest(vect['y']), round_nearest(vect['z']))
    else:
        return default

# Utility to make sure tuple quaternion is returned from a dict
def parse_dict_quaternion(entity, index):
    if index in entity:
        quat = entity[index]
        return (quat['w'],quat['x'],quat['y'],quat['z'])
    else:
        return ZERO_QUAT

# Utility to swap y and z and reduce vector(0.5) of all values, as default blender center pivot is 0 not 0.5
def swap_pivot(v):
    return Vector(((v[0] - PIVOT_VECTOR[0]), (v[2] - PIVOT_VECTOR[1]), -(v[1] - PIVOT_VECTOR[2])))
    
# Utility to swap y and z, and return a VEctor
def swap_yz(v):
    return Vector((v[0], v[2], v[1]))


# Utility to swap y and -z
def swap_nyz(vector):
    return Vector((vector[0], -vector[2], vector[1]))

def swap_nzy(vector):
    return Vector((vector[0], vector[2], -vector[1]))

def matrix4_to_dict(m):
    return [vec4_to_list(m[0]),
        vec4_to_list(m[1]),
        vec4_to_list(m[2]),
        vec4_to_list(m[3])]

def vec4_to_list(v):
    return [v[0],v[1],v[2],v[3]]


def vec_to_list(v):
    return [v.x,v.y,v.z]

# Utility to swap quaternion axis to -zy
def quat_swap_nyz(q):
    q1 = Quaternion(q)
        
    factor = sqrt(2)/2
    
    axis = q1.axis
    angle = q1.angle
    
    temp = axis.z
    axis.z = axis.y
    axis.y = -temp
    return Quaternion(axis, angle)


def quat_swap_nzy(q):
    q1 = Quaternion(q)
        
    factor = sqrt(2)/2
    
    axis = q1.axis
    angle = q1.angle
    
    temp = axis.z
    axis.z = -axis.y
    axis.y = temp
    return Quaternion(axis, angle)


def list_tuple(l):
    if len(l) == 4:
        return(l[0], l[1], l[2], l[3])

    return (l[0], l[1], l[2])

def list_vector(l):
    t = list_tuple(l)
    return Vector(t)

def list_matrix(v):
    return Matrix((v[0], v[1], v[2], v[3]))

def bone_length(bone):
    return (bone.head - bone.tail).magnitude

def get_sides(bone, theta):
    h = bone_length(bone)
    return [h, h * cos(theta), h * sin(theta)]
