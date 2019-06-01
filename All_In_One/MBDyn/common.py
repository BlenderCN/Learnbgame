# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

import bpy
from math import sqrt
import bmesh
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from struct import pack, unpack
from threading import Thread
from collections import OrderedDict
from time import sleep

class Tree(OrderedDict):
    def get_leaves(self):
        ret = list()
        for key, value in self.items():
            if isinstance(value, Tree):
                ret.extend(value.get_leaves())
            else:
                ret.append(key)
        return ret

FORMAT = "{:.6g}".format

def safe_name(name):
    return "_".join("_".join(name.split(".")).split())

def create_stream_socket(host_name, port_number):
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((host_name, port_number))
        sock.listen(5)
        sock.settimeout(1.)
        try:
            streaming_socket, address = sock.accept()
            return streaming_socket
        except OSError as err:
            print(err)

class StreamSender:
    def __init__(self, host_name=None, port_number=None):
        self.socket = create_stream_socket(host_name if host_name is not None else "127.0.0.1", port_number if port_number is not None else 9012)
    def send(self, floats):
        self.socket.send(pack('d'*len(floats), *floats))
    def close(self):
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as err:
            if err.errno != 107:
                print(err)
        self.socket.close()
        del self.socket

class StreamReceiver(Thread):
    def __init__(self, fmt, initial_data=None, host_name=None, port_number=None):
        Thread.__init__(self)
        self.daemon = True
        self.fmt = fmt
        self.packed_data = pack(self.fmt, *initial_data)
        self.recv_size = len(self.packed_data)
        self.receiving = True
        self.socket = create_stream_socket(host_name if host_name is not None else "127.0.0.1", port_number if port_number is not None else 9011)
    def run(self):
        try:
            while self.receiving:
                self.packed_data += self.socket.recv(self.recv_size)
                self.packed_data = self.packed_data[( (len(self.packed_data) // self.recv_size) - 1) * self.recv_size : ]
        except Exception as e:
            sleep(1)
            if self.receiving:
                raise Exception(e)
        try:
            self.socket.shutdown(SHUT_RDWR)
        except OSError as err:
            if err.errno != 107:
                print(err)
        self.socket.close()
        del self.socket
    def get_data(self):
        return unpack(self.fmt, self.packed_data[:self.recv_size])
    def close(self):
        self.receiving = False

def write_vector(f, v, prepend=True):
    f.write((", " if prepend else "") + ", ".join([FORMAT(round(x, 6) if round(x, 6) != -0. else 0) for x in v]))

def write_orientation(f, m, pad=""):
    f.write(",\n" + pad + "euler")
    write_vector(f, m.to_euler('ZYX'))
    #f.write(",\n" + pad +"matr,\n" + ",\n\t".join([pad + ", ".join(FORMAT(round(x, 6) if round(x, 6) != -0. else 0) for x in r) for r in m]))

def subsurf(obj):
    subsurf = [m for m in obj.modifiers if m.type == 'SUBSURF']
    subsurf = subsurf[0] if subsurf else obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 3

def Ellipsoid(obj, mass, mat):
    def v_or_1(value):
        return value if isinstance(value, (int, float)) else 1.0
    diag, scale = 3*[1.0], 1.0
    if mat is not None:
        if mat.subtype != "eye":
            diag = [v_or_1(mat.floats[4*i]) for i in range(3)]
        scale = v_or_1(mat.scale)
    s = [0.5*sqrt(x*scale/v_or_1(mass)) for x in diag]
    bm = bmesh.new()
    for v in [(x*s[0],y*s[1],z*s[2]) for z in [-1., 1.] for y in [-1., 1.] for x in [-1., 1.]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 0.184
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def Sphere(obj):
    bm = bmesh.new()
    for v in [(x, y, z) for z in [-0.5, 0.5] for y in [-0.5, 0.5] for x in [-0.5, 0.5]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def Cube(obj):
    bm = bmesh.new()
    for v in [(x, y, z) for z in [-0.5, 0.5] for y in [-0.5, 0.5] for x in [-0.5, 0.5]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def RhombicPyramid(obj):
    bm = bmesh.new()
    for v in [(.333,0.,0.),(0.,.666,0.),(-.333,0.,0.),(0.,-.666,0.),(0.,0.,1.)]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(3,2,1,0),(0,1,4),(1,2,4),(2,3,4),(3,0,4)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def TriPyramid(obj):
    bm = bmesh.new()
    for v in [(0.,0.,0.),(.333,0.,0.),(0.,.666,0.),(0.,0.,1.)]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(0,1,2),(0,1,3),(0,2,3),(1,2,3)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def Octahedron(obj):
    bm = bmesh.new()
    for v in [(.5,0.,0.),(0.,.5,0.),(-.5,0.,0.),(0.,-.5,0.),(0.,0.,.5),(0.,0.,-.5)]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,1,5),(1,2,5),(2,3,5),(3,0,5)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()

def Teardrop(obj):
    bm = bmesh.new()
    for v in [(x, y, -.5) for y in [-.5, .5] for x in [-.5, .5]] + [(0.,0.,0.)]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for q in [(2,3,1,0),(0,1,4),(1,3,4),(3,2,4),(2,0,4)]:
        bm.faces.new([bm.verts[i] for i in q])
    crease = bm.edges.layers.crease.new()
    if hasattr(bm.edges, "ensure_lookup_table"):
        bm.edges.ensure_lookup_table()
    for i in range(4,8):
        bm.edges[i][crease] = 1.0
    bm.to_mesh(obj.data)
    bm.free()
    subsurf(obj)

def Cylinder(obj):
    bm = bmesh.new()
    scale = .5
    for z in [-1., 1.]:
        for y in [-1., 1.]:
            for x in [-1., 1.]:
                bm.verts.new((scale*x,scale*y,scale*z))
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for q in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in q])
    crease = bm.edges.layers.crease.new()
    for v0, v1 in ([(0,1),(0,2),(2,3),(3,1),(4,5),(4,6),(6,7),(7,5)]):
        bm.edges.get((bm.verts[v0], bm.verts[v1]))[crease] = 1.0
    bm.to_mesh(obj.data)
    bm.free()
    subsurf(obj)

def RectangularCuboid(obj):
    bm = bmesh.new()
    for v in [(x, y, z) for z in [-0.2, 0.2] for y in [-0.1, 0.1] for x in [-0.3, 0.3]]:
        bm.verts.new(v)
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
    for f in [(1,0,2,3),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]:
        bm.faces.new([bm.verts[i] for i in f])
    crease = bm.edges.layers.crease.new()
    for e in bm.edges:
        e[crease] = 1.0
    bm.to_mesh(obj.data)
    subsurf(obj)
    bm.free()
