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

import os
import shutil
import struct
import sys


class MXSBinMeshWriter():
    def __init__(self, path, name, num_positions, vertices, normals, triangles, triangle_normals, uv_channels, num_materials, triangle_materials, ):
        """
        name                sting
        num_positions       int
        vertices            [[(float x, float y, float z), ..., ], [...], ]
        normals             [[(float x, float y, float z), ..., ], [...], ]
        triangles           [(int iv0, int iv1, int iv2, int in0, int in1, int in2, ), ..., ], ]   # (3x vertex index, 3x normal index)
        triangle_normals    [[(float x, float y, float z), ..., ], [...], ]
        uv_channels         [[(float u1, float v1, float w1, float u2, float v2, float w2, float u3, float v3, float w3, ), ..., ], ..., ] or None      # ordered by uv index and ordered by triangle index
        num_materials       int
        triangle_materials  [(int tri_id, int mat_id), ..., ] or None
        """
        o = "@"
        with open("{0}.tmp".format(path), 'wb') as f:
            p = struct.pack
            fw = f.write
            # header
            fw(p(o + "7s", 'BINMESH'.encode('utf-8')))
            fw(p(o + "?", False))
            # name 250 max length
            fw(p(o + "250s", name.encode('utf-8')))
            # number of steps
            fw(p(o + "i", num_positions))
            # number of vertices
            lv = len(vertices[0])
            fw(p(o + "i", lv))
            # vertex positions
            for i in range(num_positions):
                fw(p(o + "{}d".format(lv * 3), *[f for v in vertices[i] for f in v]))
            # vertex normals
            for i in range(num_positions):
                fw(p(o + "{}d".format(lv * 3), *[f for v in normals[i] for f in v]))
            # number triangle normals
            ltn = len(triangle_normals[0])
            fw(p(o + "i", ltn))
            # triangle normals
            for i in range(num_positions):
                fw(p(o + "{}d".format(ltn * 3), *[f for v in triangle_normals[i] for f in v]))
            # number of triangles
            lt = len(triangles)
            fw(p(o + "i", lt))
            # triangles
            fw(p(o + "{}i".format(lt * 6), *[f for v in triangles for f in v]))
            # number of uv channels
            luc = len(uv_channels)
            fw(p(o + "i", luc))
            # uv channels
            for i in range(luc):
                fw(p(o + "{}d".format(lt * 9), *[f for v in uv_channels[i] for f in v]))
            # number of materials
            fw(p(o + "i", num_materials))
            # triangle materials
            fw(p(o + "{}i".format(lt * 2), *[f for v in triangle_materials for f in v]))
            # end
            fw(p(o + "?", False))
        # swap files
        if(os.path.exists(path)):
            os.remove(path)
        shutil.move("{0}.tmp".format(path), path)
        self.path = path


class MXSBinMeshReader():
    def __init__(self, path):
        def r(f, b, o):
            d = struct.unpack_from(f, b, o)
            o += struct.calcsize(f)
            return d, o
        
        def r0(f, b, o):
            d = struct.unpack_from(f, b, o)[0]
            o += struct.calcsize(f)
            return d, o
        
        offset = 0
        with open(path, "rb") as bf:
            buff = bf.read()
        # endianness?
        signature = 20357755437992258
        l, _ = r0("<q", buff, 0)
        b, _ = r0(">q", buff, 0)
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            order = ">"
        else:
            raise AssertionError("{}: not a MXSBinMesh file".format(self.__class__.__name__))
        o = order
        # magic
        magic, offset = r0(o + "7s", buff, offset)
        magic = magic.decode(encoding="utf-8")
        if(magic != 'BINMESH'):
            raise RuntimeError()
        # throwaway
        _, offset = r(o + "?", buff, offset)
        # name
        name, offset = r0(o + "250s", buff, offset)
        name = name.decode(encoding="utf-8").replace('\x00', '')
        # number of steps
        num_positions, offset = r0(o + "i", buff, offset)
        # number of vertices
        lv, offset = r0(o + "i", buff, offset)
        # vertex positions
        vertices = []
        for i in range(num_positions):
            vs, offset = r(o + "{}d".format(lv * 3), buff, offset)
            vs3 = [vs[i:i + 3] for i in range(0, len(vs), 3)]
            vertices.append(vs3)
        # vertex normals
        normals = []
        for i in range(num_positions):
            ns, offset = r(o + "{}d".format(lv * 3), buff, offset)
            ns3 = [ns[i:i + 3] for i in range(0, len(ns), 3)]
            normals.append(ns3)
        # number of triangle normals
        ltn, offset = r0(o + "i", buff, offset)
        # triangle normals
        triangle_normals = []
        for i in range(num_positions):
            tns, offset = r(o + "{}d".format(ltn * 3), buff, offset)
            tns3 = [tns[i:i + 3] for i in range(0, len(tns), 3)]
            triangle_normals.append(tns3)
        # number of triangles
        lt, offset = r0(o + "i", buff, offset)
        # triangles
        ts, offset = r(o + "{}i".format(lt * 6), buff, offset)
        triangles = [ts[i:i + 6] for i in range(0, len(ts), 6)]
        # number uv channels
        num_channels, offset = r0(o + "i", buff, offset)
        # uv channels
        uv_channels = []
        for i in range(num_channels):
            uvc, offset = r(o + "{}d".format(lt * 9), buff, offset)
            uv9 = [uvc[i:i + 9] for i in range(0, len(uvc), 9)]
            uv_channels.append(uv9)
        # number of materials
        num_materials, offset = r0(o + "i", buff, offset)
        # triangle materials
        tms, offset = r(o + "{}i".format(2 * lt), buff, offset)
        triangle_materials = [tms[i:i + 2] for i in range(0, len(tms), 2)]
        # throwaway
        _, offset = r(o + "?", buff, offset)
        # and now.. eof
        if(offset != len(buff)):
            raise RuntimeError("expected EOF")
        # collect data
        self.data = {'name': name,
                     'num_positions': num_positions,
                     'vertices': vertices,
                     'normals': normals,
                     'triangles': triangles,
                     'triangle_normals': triangle_normals,
                     'uv_channels': uv_channels,
                     'num_materials': num_materials,
                     'triangle_materials': triangle_materials, }


class MXSBinHairWriter():
    def __init__(self, path, data):
        d = data
        o = "@"
        with open("{0}.tmp".format(path), 'wb') as f:
            p = struct.pack
            fw = f.write
            # header
            fw(p(o + "7s", 'BINHAIR'.encode('utf-8')))
            fw(p(o + "?", False))
            # number of floats
            n = len(d)
            fw(p(o + "i", n))
            # floats
            fw(p(o + "{}d".format(n), *d))
            # end
            fw(p(o + "?", False))
        if(os.path.exists(path)):
            os.remove(path)
        shutil.move("{0}.tmp".format(path), path)
        self.path = path


class MXSBinHairReader():
    def __init__(self, path):
        self.offset = 0
        with open(path, "rb") as bf:
            self.bindata = bf.read()
        
        def r(f):
            d = struct.unpack_from(f, self.bindata, self.offset)
            self.offset += struct.calcsize(f)
            return d
        
        # endianness?
        signature = 23161492825065794
        l = r("<q")[0]
        self.offset = 0
        b = r(">q")[0]
        self.offset = 0
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            self.order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            self.order = ">"
        else:
            raise AssertionError("{}: not a MXSBinHair file".format(self.__class__.__name__))
        o = self.order
        # magic
        self.magic = r(o + "7s")[0].decode(encoding="utf-8")
        if(self.magic != 'BINHAIR'):
            raise RuntimeError()
        _ = r(o + "?")
        # number floats
        self.num = r(o + "i")[0]
        self.data = r(o + "{}d".format(self.num))
        e = r(o + "?")
        if(self.offset != len(self.bindata)):
            raise RuntimeError("expected EOF")


class MXSBinParticlesWriter():
    def __init__(self, path, data):
        d = data
        o = "@"
        with open("{0}.tmp".format(path), 'wb') as f:
            p = struct.pack
            fw = f.write
            # header
            fw(p(o + "7s", 'BINPART'.encode('utf-8')))
            fw(p(o + "?", False))
            # 'PARTICLE_POSITIONS'
            n = len(d['PARTICLE_POSITIONS'])
            fw(p(o + "i", n))
            fw(p(o + "{}d".format(n), *d['PARTICLE_POSITIONS']))
            # 'PARTICLE_SPEEDS'
            n = len(d['PARTICLE_SPEEDS'])
            fw(p(o + "i", n))
            fw(p(o + "{}d".format(n), *d['PARTICLE_SPEEDS']))
            # 'PARTICLE_RADII'
            n = len(d['PARTICLE_RADII'])
            fw(p(o + "i", n))
            fw(p(o + "{}d".format(n), *d['PARTICLE_RADII']))
            # 'PARTICLE_NORMALS'
            n = len(d['PARTICLE_NORMALS'])
            fw(p(o + "i", n))
            fw(p(o + "{}d".format(n), *d['PARTICLE_NORMALS']))
            # 'PARTICLE_IDS'
            n = len(d['PARTICLE_IDS'])
            fw(p(o + "i", n))
            fw(p(o + "{}i".format(n), *d['PARTICLE_IDS']))
            # 'PARTICLE_UVW'
            n = len(d['PARTICLE_UVW'])
            fw(p(o + "i", n))
            fw(p(o + "{}d".format(n), *d['PARTICLE_UVW']))
            # end
            fw(p(o + "?", False))
        if(os.path.exists(path)):
            os.remove(path)
        shutil.move("{0}.tmp".format(path), path)
        self.path = path


class MXSBinParticlesReader():
    def __init__(self, path):
        self.offset = 0
        with open(path, "rb") as bf:
            self.bindata = bf.read()
        
        def r(f):
            d = struct.unpack_from(f, self.bindata, self.offset)
            self.offset += struct.calcsize(f)
            return d
        
        # endianness?
        signature = 23734338517354818
        l = r("<q")[0]
        self.offset = 0
        b = r(">q")[0]
        self.offset = 0
        
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            self.order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            self.order = ">"
        else:
            raise AssertionError("{}: not a MXSBinParticles file".format(self.__class__.__name__))
        o = self.order
        # magic
        self.magic = r(o + "7s")[0].decode(encoding="utf-8")
        if(self.magic != 'BINPART'):
            raise RuntimeError()
        _ = r(o + "?")
        # 'PARTICLE_POSITIONS'
        n = r(o + "i")[0]
        self.PARTICLE_POSITIONS = r(o + "{}d".format(n))
        # 'PARTICLE_SPEEDS'
        n = r(o + "i")[0]
        self.PARTICLE_SPEEDS = r(o + "{}d".format(n))
        # 'PARTICLE_RADII'
        n = r(o + "i")[0]
        self.PARTICLE_RADII = r(o + "{}d".format(n))
        # 'PARTICLE_NORMALS'
        n = r(o + "i")[0]
        self.PARTICLE_NORMALS = r(o + "{}d".format(n))
        # 'PARTICLE_IDS'
        n = r(o + "i")[0]
        self.PARTICLE_IDS = r(o + "{}i".format(n))
        # 'PARTICLE_UVW'
        n = r(o + "i")[0]
        self.PARTICLE_UVW = r(o + "{}d".format(n))
        # eof
        e = r(o + "?")
        if(self.offset != len(self.bindata)):
            raise RuntimeError("expected EOF")


class MXSBinWireWriter():
    def __init__(self, path, data):
        d = data
        o = "@"
        with open("{0}.tmp".format(path), 'wb') as f:
            p = struct.pack
            fw = f.write
            # header
            fw(p(o + "7s", 'BINWIRE'.encode('utf-8')))
            fw(p(o + "?", False))
            # number of wires
            n = len(d)
            fw(p(o + "i", n))
            fw(p(o + "?", False))
            # data
            for base, pivot, loc, rot, sca in data:
                base = tuple(sum(base, ()))
                pivot = tuple(sum(pivot, ()))
                w = base + pivot + loc + rot + sca
                fw(p(o + "33d", *w))
            # end
            fw(p(o + "?", False))
        if(os.path.exists(path)):
            os.remove(path)
        shutil.move("{0}.tmp".format(path), path)
        self.path = path


class MXSBinWireReader():
    def __init__(self, path):
        self.offset = 0
        with open(path, "rb") as bf:
            self.bindata = bf.read()
        
        def r(f):
            d = struct.unpack_from(f, self.bindata, self.offset)
            self.offset += struct.calcsize(f)
            return d
        
        # endianness?
        signature = 19512248343873858
        l = r("<q")[0]
        self.offset = 0
        b = r(">q")[0]
        self.offset = 0
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            self.order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            self.order = ">"
        else:
            raise AssertionError("{}: not a MXSBinWire file".format(self.__class__.__name__))
        o = self.order
        # magic
        self.magic = r(o + "7s")[0].decode(encoding="utf-8")
        if(self.magic != 'BINWIRE'):
            raise RuntimeError()
        _ = r(o + "?")
        # number floats
        self.num = r(o + "i")[0]
        _ = r(o + "?")
        self.data = []
        for i in range(self.num):
            w = r(o + "33d")
            base = w[0:12]
            base = [base[i * 3:(i + 1) * 3] for i in range(4)]
            pivot = w[12:24]
            pivot = [pivot[i * 3:(i + 1) * 3] for i in range(4)]
            loc = w[24:27]
            rot = w[27:30]
            sca = w[30:33]
            self.data.append((base, pivot, loc, rot, sca, ))
        e = r(o + "?")
        if(self.offset != len(self.bindata)):
            raise RuntimeError("expected EOF")


class MXSBinRefVertsWriter():
    def __init__(self, path, data, ):
        o = "@"
        with open("{0}.tmp".format(path), 'wb') as f:
            p = struct.pack
            fw = f.write
            # header
            fw(p(o + "7s", 'BINREFV'.encode('utf-8')))
            fw(p(o + "?", False))
            # number of objects
            fw(p(o + "i", len(data)))
            for i in range(len(data)):
                d = data[i]
                name = d['name']
                base = d['base']
                pivot = d['pivot']
                vertices = d['vertices']
                # name
                fw(p(o + "250s", name.encode('utf-8')))
                # base and pivot
                fw(p(o + "12d", *[a for b in base for a in b]))
                fw(p(o + "12d", *[a for b in pivot for a in b]))
                # number of vertices
                fw(p(o + "i", len(vertices) * 3))
                # vertices
                lv = len(vertices)
                fw(p(o + "{}d".format(lv * 3), *[f for v in vertices for f in v]))
            fw(p(o + "?", False))
        # swap files
        if(os.path.exists(path)):
            os.remove(path)
        shutil.move("{0}.tmp".format(path), path)
        self.path = path


class MXSBinRefVertsReader():
    def __init__(self, path):
        def r(f, b, o):
            d = struct.unpack_from(f, b, o)
            o += struct.calcsize(f)
            return d, o
        
        def r0(f, b, o):
            d = struct.unpack_from(f, b, o)[0]
            o += struct.calcsize(f)
            return d, o
        
        offset = 0
        with open(path, "rb") as bf:
            buff = bf.read()
        # endianness?
        signature = 24284111544666434
        l, _ = r0("<q", buff, 0)
        b, _ = r0(">q", buff, 0)
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            order = ">"
        else:
            raise AssertionError("{}: not a MXSBinRefVerts file".format(self.__class__.__name__))
        o = order
        # magic
        magic, offset = r0(o + "7s", buff, offset)
        magic = magic.decode(encoding="utf-8")
        if(magic != 'BINREFV'):
            raise RuntimeError()
        # throwaway
        _, offset = r(o + "?", buff, offset)
        # number of objects
        num_objects, offset = r0(o + "i", buff, offset)
        self.data = []
        for i in range(num_objects):
            name, offset = r0(o + "250s", buff, offset)
            name = name.decode(encoding="utf-8").replace('\x00', '')
            b, offset = r(o + "12d", buff, offset)
            base = [b[i:i + 3] for i in range(0, len(b), 3)]
            p, offset = r(o + "12d", buff, offset)
            pivot = [p[i:i + 3] for i in range(0, len(p), 3)]
            lv, offset = r0(o + "i", buff, offset)
            vs, offset = r(o + "{}d".format(lv), buff, offset)
            vertices = [vs[i:i + 3] for i in range(0, len(vs), 3)]
            self.data.append({'name': name,
                              'base': base,
                              'pivot': pivot,
                              'vertices': vertices, })
        # throwaway
        _, offset = r(o + "?", buff, offset)
        # and now.. eof
        if(offset != len(buff)):
            raise RuntimeError("expected EOF")
