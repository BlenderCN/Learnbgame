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

# <pep8 compliant>

import bpy, bmesh, mathutils
from mathutils import *


class ClassPropertyDescriptor(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

# decorator to define a read-only class property
def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


#def bmesh_layer_insert_float(layers, layers_from, offset):
#    for layer in from_layers:
        

# Utility function to insert a copy of bm_from data into bm
def bmesh_insert(bm, bm_from):
    # make sure indices are valid
    bm_from.verts.index_update()
    # remember this as offset for new vertices
    vert_offset = len(bm.verts)

    verts = []
    edges = []
    faces = []
    for v in bm_from.verts:
        verts.append(bm.verts.new(v.co, v))
    for e in bm_from.edges:
        v1 = bm.verts[e.verts[0].index + vert_offset]
        v2 = bm.verts[e.verts[1].index + vert_offset]
        edges.append(bm.edges.new((v1, v2), e))
    for f in bm_from.faces:
        faces.append(bm.faces.new([ bm.verts[v.index + vert_offset] for v in f.verts ], f))

    # merge custom data layers
    # XXX TODO
#    for layer_coll in [bm_from

    return verts, edges, faces


def matrix_uniform_scale(scale):
    return Matrix(((scale, 0.0, 0.0, 0.0),
                   (0.0, scale, 0.0, 0.0),
                   (0.0, 0.0, scale, 0.0),
                   (0.0, 0.0, 0.0,   1.0)))


def matrix_vector_scale(scale):
    return Matrix(((scale[0], 0.0, 0.0, 0.0),
                   (0.0, scale[1], 0.0, 0.0),
                   (0.0, 0.0, scale[2], 0.0),
                   (0.0, 0.0, 0.0,      1.0)))


import random
random.seed(83742)
noise_map_size = 1024
noise_map = [random.random() for i in range(noise_map_size)]

def random_noise_f(f):
    import struct
    s = struct.pack('>f', f)
    h = 5381
    for c in s:
        h = ((h << 5) + h) ^ ord(c)      # (h * 33) ^ c
    return noise_map[h % noise_map_size]


def strhash16(s, base=5381):
    h = base
    for c in s:
        h = ((h << 5) + h) ^ ord(c)  # (h * 33) ^ c
    # separator '\0' character, to avoid ambiguity from concatenated strings
    h = (h << 5) + h            # h * 33
    return h % 65536

def strhash32(s, base=5381):
    h = base
    for c in s:
        h = ((h << 5) + h) ^ ord(c)  # (h * 33) ^ c
    # separator '\0' character, to avoid ambiguity from concatenated strings
    h = (h << 5) + h            # h * 33
    return h
