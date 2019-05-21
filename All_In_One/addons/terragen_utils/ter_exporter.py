'''
Copyright (C) 2017 Walter Perdan
info@kalwaltart.it

Created by WALTER PERDAN

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import bpy
import sys
import string
import struct
import os  # glob
from os import path, name, sep
from math import *
import bmesh
import time


# from sverchok
def pydata_from_bmesh(bm):
    v = [v.co[:] for v in bm.verts]
    e = [[i.index for i in e.verts] for e in bm.edges]
    p = [[i.index for i in p.verts] for p in bm.faces]
    return v, e, p


# function (modified version) to get verts, from Sverchok addon
def pydata_from_obj():
    obj = bpy.context.scene.objects.active
    mesh = obj.data
    # must take also max dim from bmesh!!!
    new = bmesh.new()
    new.from_mesh(mesh)
    verts, edges, faces = pydata_from_bmesh(new)
    # print('verts from bmesh: ', verts)
    # print(len(verts))
    length_v = len(verts)
    size_points = int(sqrt(length_v))
    vertices = [v[2] for v in verts]
    return vertices, size_points


def get_grid_spacing(size):
    obj = bpy.context.scene.objects.active
    dim = obj.dimensions
    spacing = dim[0] / float(size)
    return float(spacing)


# function (modified version) to map values, from Sverchok addon
def map_range(x_list, old_min, old_max, new_min, new_max):
    old_d = old_max - old_min
    new_d = new_max - new_min
    scale = new_d / old_d

    def f(x):
        return new_min + (x - old_min) * scale

    return min(new_max, max(new_min, f(x_list)))


## from terragen_utils.ter_exporter import export_ter
## export_ter(0,'/tmp/txt',0,0,0,0)
def export_ter(operator, context, filepath, custom_properties,
               custom_scale, baseH, heightS):
    start_time = time.process_time()
    # start to set all the tags and values needed for the .ter file
    ter_header = 'TERRAGENTERRAIN '
    size_tag = 'SIZE'
    size = 0
    scal_tag = 'SCAL'
    scalx = 1.0
    scaly = 1.0
    scalz = 1.0
    altw_tag = 'ALTW'
    # HeightScale = 80
    HeightScale = 16384
    BaseHeight = 0
    if custom_properties is True:
        HeightScale = heightS
        BaseHeight = baseH
    # values are packed as short (i.e = integers max 32767)
    values, size_points = pydata_from_obj()
    # print('z_val from pydata_func: ', values)
    print('size_points of mesh is: ', size_points)
    size = size_points - 1
    # calculate the X,Y scale factor
    scalx = scaly = get_grid_spacing(size)
    if custom_properties is True:
        scalx, scaly, scalz = custom_scale

    z_val = [int(p * 4.0) for p in values]
    eof_tag = 'EOF'  # end of file tag

    with open(filepath, "wb") as file:
        # write the header
        file.write(ter_header.encode('ascii'))
        # write the size of the terrain
        file.write(size_tag.encode('ascii'))
        file.write(struct.pack('h', size))
        # padding byte needed after SIZE
        file.write(struct.pack('xx'))  # padding -> b'\x00\x00'
        # write the scale tag = SCAL
        file.write(scal_tag.encode('ascii'))
        # pack the scaling values as floats
        file.write(struct.pack('fff', scalx, scaly, scalz))
        # write the altitude ALTW tag
        file.write(altw_tag.encode('ascii'))
        # pack heightScale and baseHeight
        file.write(struct.pack('h', HeightScale))
        file.write(struct.pack('h', BaseHeight))
        # pack as shorts the elvetions values
        for v in z_val:
            file.write(struct.pack('h', v))
        # EOF = end of file
        file.write(eof_tag.encode('ascii'))
        file.close()

        print('Terrain exported in %.4f sec.' % (time.process_time() - start_time))

    return {'FINISHED'}

    if __name__ == "__main__":
        register()
