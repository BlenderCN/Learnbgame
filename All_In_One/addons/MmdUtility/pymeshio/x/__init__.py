#!/usr/bin/env python
# coding: utf-8
"""
========================
DirectX format
========================
"""

class Material(object):
    __slots__=[
            'diffuse',
            'specular',
            'shininess',
            'emit',
            ]
    def __init__(self):
        pass


class Model(object):
    __slots__=[
            'templates',
            'vertices',
            'faces',
            'face_materials',
            'materials',
            'normals',
            'face_normals',
            'uvs',
            ]
    def __init__(self):
        self.templates=[]
        self.vertices=[]
        self.faces=[]
        self.face_materials=[]
        self.materials=[]
        self.normals=[]
        self.face_normals=[]
        self.uvs=[]

    def __str__(self):
        return ('<x vertices: {vertices}, faces: {faces}, materials: {materials}>'.format(
            vertices=len(self.vertices),
            faces=len(self.faces),
            materials=len(self.materials)
            ))

