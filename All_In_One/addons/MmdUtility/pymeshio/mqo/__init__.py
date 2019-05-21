# coding: utf-8
""" 
======================
Metasequioa MQO format
======================

file format
~~~~~~~~~~~
* http://www.metaseq.net/metaseq/format.html

specs
~~~~~
* textencoding: bytes(cp932)
* coordinate: right handed y-up
* uv origin: 
* face: edge(2), triangle(3), quadrangle(4)
* backculling: enable

"""

import os
import sys
import math
import warnings
from .. import common


"""
MQO loader
"""
class Material(object):
    """mqo material

    Attributes:
        name: cp932
        shader: 
        color: rgba
        diffuse:
        ambient:
        emit:
        specular:
        power:
        tex: cp932 windows file path
    """
    __slots__=[
            "name", "shader", "color", "diffuse", 
            "ambient", "emit", "specular", "power",
            "tex",
            ]
    def __init__(self, name):
        self.name=name
        self.shader=3
        self.color=common.RGBA(0.5, 0.5, 0.5, 1.0)
        self.diffuse=1.0
        self.ambient=0.0
        self.emit=0.0
        self.specular=0.0
        self.power=5.0
        self.tex=b""

    def getName(self): return self.name
    def getTexture(self): return self.tex

    def parse(self, line):
        offset=0
        while True:
            leftParenthesis=line.find(b"(", offset)
            if leftParenthesis==-1:
                break
            key=line[offset:leftParenthesis]
            rightParenthesis=line.find(b")", leftParenthesis+1)
            if rightParenthesis==-1:
                raise ValueError("assert")

            param=line[leftParenthesis+1:rightParenthesis]
            if key==b"shader":
                self.shader=int(param)
            elif key==b"col":
                self.color=common.RGBA(*[float(e) for e in param.split()])
            elif key==b"dif":
                self.diffuse=float(param)
            elif key==b"amb":
                self.ambient=float(param)
            elif key==b"emi":
                self.emit=float(param)
            elif key==b"spc":
                self.specular=float(param)
            elif key==b"power":
                self.power=float(param)
            elif key==b"tex":
                self.tex=param[1:-1]
            else:
                print(
                        "%s#parse" % self.name, 
                        "unknown key: %s" %  key
                        )

            offset=rightParenthesis+2

    def __str__(self):
        return "<Material %s shader: %d [%f, %f, %f, %f] %f>" % (
                self.name, self.shader,
                self.color[0], self.color[1], self.color[2], self.color[3],
                self.diffuse)


class Obj(object):
    """mqo object

    Attributes:
        name: cp932
        depth: object hierarchy 
        folding: 
        scale:
        rotation:
        translation:
        visible:
        locking:
        shading:
        facet: smoothing threshold
        color:
        color_type:
        mirror: mirroring
        mirror_axis:
        vertices:
        faces:
        edges:
        smoothing:
    """
    __slots__=["name", "depth", "folding", 
            "scale", "rotation", "translation",
            "visible", "locking", "shading", "facet",
            "color", "color_type", "mirror", "mirror_axis",
            "vertices", "faces", "edges", "smoothing",
            ]

    def __init__(self, name):
        self.name=name
        self.vertices=[]
        self.faces=[]
        self.edges=[]
        self.depth=0
        self.folding=0
        self.scale=[1, 1, 1]
        self.rotation=[0, 0, 0]
        self.translation=[0, 0, 0]
        self.visible=15
        self.locking=0
        self.shading=0
        self.facet=59.5
        self.color=[1, 1, 1]
        self.color_type=0
        self.mirror=0
        self.smoothing=0

    def getName(self): return self.name

    def addVertex(self, x, y, z):
        self.vertices.append(common.Vector3(x, y, z))

    def addFace(self, face):
        if face.index_count==2:
            self.edges.append(face)
        else:
            self.faces.append(face)

    def __str__(self):
        return "<Object %s, %d vertices, %d faces>" % (
                self.name, len(self.vertices), len(self.faces))


class Face(object):
    """mqo face

    Attributes:
        index_count: 2 or 3 or 4
        indices: index x index_count
        material_index:
        col: vertex_color x index_count
        uv: Vector2 x index_count
    """
    __slots__=[
            "index_count",
            "indices", "material_index", "col", "uv",
            ]
    def __init__(self, index_count, line):
        if index_count<2 or index_count>4:
            raise ValueError("invalid vertex count: %d" % index_count)
        self.material_index=0
        self.col=[]
        self.uv=[common.Vector2(0, 0)]*4
        self.index_count=index_count
        offset=0
        while True:
            leftParenthesis=line.find(b"(", offset)
            if leftParenthesis==-1:
                break
            key=line[offset:leftParenthesis]
            rightParenthesis=line.find(b")", leftParenthesis+1)
            if rightParenthesis==-1:
                raise ValueError("assert")
            params=line[leftParenthesis+1:rightParenthesis].split()
            if key==b"V":
                self.indices=[int(e) for e in params]
            elif key==b"M":
                self.material_index=int(params[0])
            elif key==b"UV":
                uv_list=[float(e) for e in params]
                self.uv=[]
                for i in range(0, len(uv_list), 2):
                    self.uv.append(common.Vector2(uv_list[i], uv_list[i+1]))
            elif key==b"COL":
                for n in params:
                    d=int(n)
                    # R
                    d, m=divmod(d, 256)
                    self.col.append(m)
                    # G
                    d, m=divmod(d, 256)
                    self.col.append(m)
                    # B
                    d, m=divmod(d, 256)
                    self.col.append(m)
                    # A
                    d, m=divmod(d, 256)
                    self.col.append(m)
            else:
                print("Face#__init__:unknown key: %s" % key)

            offset=rightParenthesis+2

    def getIndex(self, i): return self.indices[i]
    def getUV(self, i): return self.uv[i] if i<len(self.uv) else common.Vector2(0, 0)


class Model(object):
    def __init__(self):
        self.has_mikoto=False
        self.materials=[]
        self.objects=[]


