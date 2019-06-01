# coding: utf-8


class Face(object):
    __slots__=[
            "vertex_references"
            ]
    def __init__(self):
        self.vertex_references=[]

    def __str__(self):
        return ("<obj.Face: {vertex_count}>".format(
            vertex_count=len(self.vertex_references)
            ))


class Material(object):
    __slots__=[
            "name",
            "faces",
            "s",

            "Ns",
            "Ka",
            "Kd",
            "Ks",
            "Ni",
            "d",
            "illum",
            ]
    def __init__(self, name):
        self.name=name
        self.faces=[]
        self.s=None
        self.Ns=None
        self.Ka=None
        self.Kd=None
        self.Ks=None
        self.Ni=None
        self.d=None
        self.illum=None


class Model(object):
    __slots__=[
            "path",
            "comment",
            "vertices",
            "uv",
            "normals",
            "materials",
            "mtl",
            "order",
            ]
    def __init__(self):
        self.path=""
        self.comment=b""
        self.vertices=[]
        self.uv=[]
        self.normals=[]
        self.materials=[]
        self.mtl=None
        self.order=[]

    def __str__(self):
        return ('<obj %s: %s %d vertices, %d materials %s>' % (
            self.comment.decode("cp932"),
            self.order,
            len(self.vertices),
            len(self.materials),
            (self.mtl)
            ))

    def add_v(self, v):
        if len(self.vertices)==0:
            self.order.append("v")
        self.vertices.append(v)

    def add_vt(self, vt):
        if len(self.uv)==0:
            self.order.append("vt")
        self.uv.append(v)

    def add_vn(self, vn):
        if len(self.normals)==0:
            self.order.append("vn")
        self.normals.append(vn)

    def get_or_create_material(self, name):
        for material in self.materials:
            if material.name==name:
                return material

        material=Material(name)
        self.materials.append(material)
        return material

    def get_vertex(self, ref):
        return (self.vertices[ref[0]-1], 
                ref[1] and self.uv[ref[1]-1],
                ref[2] and self.normals[ref[2]-1]
                )

