# coding: utf-8
"""
obj reader
"""
import io
import os
import sys
from .. import obj
from .. import common


class Reader(common.TextReader):
    """obj reader
    """
    __slots__=[
            ]
    def __init__(self, ios):
        super(Reader, self).__init__(ios)

    def read(self):
        model=obj.Model()
        material=model.get_or_create_material(b"default")
        while True:
            line=self.getline()
            if line==None:
                break

            line=line.strip()
            if line==b"":
                continue

            if line[0]==ord("#"):
                if model.comment=="":
                    model.comment=line[1:].strip()
                continue

            token=line.split()
            if token[0]==b"v":
                model.add_v(common.Vector3(
                    float(token[1]),
                    float(token[2]),
                    float(token[3])
                    ))
            elif token[0]==b"vt":
                model.add_vt(common.Vector2(
                    float(token[1]),
                    float(token[2]),
                    ))
            elif token[0]==b"vn":
                model.add_vn(common.Vector3(
                    float(token[1]),
                    float(token[2]),
                    float(token[3])
                    ))
            elif token[0]==b"g":
                pass
            elif token[0]==b"f":
                material.faces.append(self.parseFace(*token[1:]))
            elif token[0]==b"mtllib":
                model.mtl=token[1]
            elif token[0]==b"usemtl":
                material=model.get_or_create_material(token[1])
            elif token[0]==b"s":
                material.s=token[1]
            else:
                print(b"unknown key: "+line)

        if len(model.materials[0].faces)==0:
            del model.materials[0]

        return model
    
    def parseFace(self, *faces):
        face=obj.Face()
        for f in faces:
            vertex_reference=[(len(t)>0 and int(t) or None) for t in f.split(b"/")]
            #print(vertex_reference)
            face.vertex_references.append(vertex_reference)
        return face


def read_from_file(path):
    """
    read from file path, then return the pymeshio.mqo.Model.

    :Parameters:
      path
        file path
    """
    with io.open(path, 'rb') as ios:
        model=read(ios)
        if model:
            model.path=path
            if model.mtl:
                obj_dir=os.path.dirname(model.path)
                path=os.path.join(
                    obj_dir, model.mtl.decode("utf-8"))
                #print(path)
                material_from_file(path, model)
            return model


def read(ios):
    """
    read from ios, then return the pymeshio.mqo.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)
    """
    assert(isinstance(ios, io.IOBase))
    return Reader(ios).read()


class MaterialReader(common.TextReader):
    """obj reader
    """
    __slots__=[
            ]
    def __init__(self, ios):
        super(MaterialReader, self).__init__(ios)

    def read(self, obj_model):
        material=None
        while True:
            line=self.getline()
            if line==None:
                break

            line=line.strip()
            if line==b"":
                continue

            if line[0]==ord("#"):
                continue

            token=line.split()
            #print(token)
            if token[0]==b"newmtl":
                material=obj_model.get_or_create_material(token[1])

            elif token[0]==b'Ns':
                material.Ns=token[1]

            elif token[0]==b'Ka':
                material.Ka=common.RGB(*(float(t) for t in token[1:]))

            elif token[0]==b'Kd':
                material.Kd=common.RGB(*(float(t) for t in token[1:]))

            elif token[0]==b'Ks':
                material.Ks=common.RGB(*(float(t) for t in token[1:]))

            elif token[0]==b'Ni':
                material.Ni=token[1]

            elif token[0]==b'd':
                material.d=token[1]

            elif token[0]==b'illum':
                material.illum=token[1]

            else:
                print("unknown line: "+line)


def material_from_file(path, obj_model):
    with io.open(path, 'rb') as ios:
        return read_material(ios, obj_model)


def read_material(ios, obj_model):
    assert(isinstance(ios, io.IOBase))
    return MaterialReader(ios).read(obj_model)

