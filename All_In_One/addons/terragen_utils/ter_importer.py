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


def import_ter(operator, context, filepath, triangulate, custom_properties,
               custom_scale, baseH, heightS):
    start_time = time.process_time()

    # variables initialization
    size = 0
    xpts = 0
    ypts = 0
    scalx = 0
    scaly = 0
    scalz = 0
    crad = 0
    crvm = 0
    heightscale = 0
    baseheight = 0

    try:
        ter = open(filepath, 'rb')
        print('start...\n')
    except IOError:
        if terfile == "":
            print("Terragen ter file does not exist!")
            Exit()
        else:
            print(terfile + " does not exist!")
    else:

        if ter.read(8).decode() == "TERRAGEN":

            if ter.read(8).decode() == "TERRAIN ":

                print("Terragen terrain file: found -> continue...\n")
            else:
                print("TERRAIN keyword not found")
                return None
        else:
            print("TERRAGEN keyword not found")
            return None

        keys = ['SIZE', 'XPTS', 'YPTS', 'SCAL', 'CRAD', 'CRVM', 'ALTW']

        totest = ter.read(4).decode()

        while 1:
            if totest in keys:
                if totest == "SIZE":
                    print('reading SIZE')
                    (size,) = struct.unpack('h', ter.read(2))
                    # garbage = ter.read(2).decode()
                    garbage = ter.read(2)
                    print('garbage :', garbage)

                if totest == 'XPTS':
                    print('reading XPTS')
                    (xpts,) = struct.unpack('h', ter.read(2))
                    garbage = ter.read(2).decode()

                if totest == 'YPTS':
                    print('reading YPTS')
                    (ypts,) = struct.unpack('h', ter.read(2))
                    garbage = ter.read(2).decode()

                if totest == 'SCAL':
                    print('reading SCAL')
                    (scalx,) = struct.unpack('f', ter.read(4))
                    (scaly,) = struct.unpack('f', ter.read(4))
                    (scalz,) = struct.unpack('f', ter.read(4))

                if totest == 'CRAD':
                    print('reading CRAD')
                    (crad,) = struct.unpack('f', ter.read(4))

                if totest == 'CRVM':
                    print('reading CRVM')
                    (crvm,) = struct.unpack('H', ter.read(2))
                    garbage = ter.read(2).decode()

                if totest == 'ALTW':
                    print('reading ALTW')
                    (heightscale,) = struct.unpack('h', ter.read(2))
                    (baseheight,) = struct.unpack('h', ter.read(2))
                    break
                totest = ter.read(4).decode()
            else:
                break

        if xpts == 0:
            xpts = size + 1
        if ypts == 0:
            ypts = size + 1

        print('\n-----------------\n')
        print('size is: {0} x {0}'.format(size))
        print('scale is: {0}, {1}, {2}'.format(scalx, scaly, scalz))
        print('number x points are: ', xpts)
        print('number y points are: ', ypts)
        print('baseheight is: ', baseheight)
        print('heightscale is: ', heightscale)
        print('\n-----------------\n')

        terrainName = bmesh.new()
        # Create vertices
        # ---------------
        # read them all...
        x0 = 0.0
        y0 = 0.0
        z0 = 0.0
        for y in range(0, ypts):
            for x in range(0, xpts):
                (h,) = struct.unpack('h', ter.read(2))
                # adding custom values
                if custom_properties is True:
                    x0 = x * custom_scale[0]
                    y0 = y * custom_scale[1]
                    baseheight = baseH
                    heightscale = heightS
                    z0 = custom_scale[2] * (baseheight + (h * heightscale / 65536.0))
                else:
                    # from VTP SetFValue(i, j, scale.z * (BaseHeight + ((float)svalue * HeightScale / 65536.0f)));
                    # see: https://github.com/kalwalt/terragen_utils/issues/2
                    x0 = x * scalx
                    y0 = y * scaly
                    z0 = scalz * (baseheight + (h * heightscale / 65536.0))

                terrainName.verts.new((x0, y0, z0))

                xmax = x + 1
                ymax = y + 1

        ter.close()

        # Create faces
        # ------------

        for y in range(0, ymax - 1):
            for x in range(0, xmax - 1):

                a = x + y * (ymax)

                terrainName.verts.ensure_lookup_table()

                v1 = terrainName.verts[a]
                v2 = terrainName.verts[a + ymax]
                v3 = terrainName.verts[a + ymax + 1]
                v4 = terrainName.verts[a + 1]

                terrainName.faces.new((v1, v2, v3, v4))

        if triangulate is True:
            args = bmesh.ops.triangulate(terrainName, faces=terrainName.faces)
            print('Terrain mesh triangulated!')

        mesh = bpy.data.meshes.new("Terrain_mesh")
        terrainName.to_mesh(mesh)
        terrainName.free()

        # Add the mesh to the scene
        scene = bpy.context.scene
        obj = bpy.data.objects.new("Terrain_obj", mesh)
        scene.objects.link(obj)
        print('Terrain imported in %.4f sec.' % (time.process_time() - start_time))

    return {'FINISHED'}

    if __name__ == "__main__":
        register()
