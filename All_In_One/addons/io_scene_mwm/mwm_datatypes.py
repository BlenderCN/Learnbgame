#!/usr/bin/env python


class VertexData(object):

    def __init__(self, positions, normals, uv_coords, binormals, tangents, tex_coords):
        self.positions = positions
        self.normals = normals
        self.uv_coords = uv_coords
        self.binormals = binormals
        self.tangents = tangents
        self.tex_coords = tex_coords


class Dummy(object):

    def __init__(self, name, matrix, params):
        self.name = name
        self.matrix = matrix
        self.params = params


class BoundingBox(object):

    def __init__(self, min, max):
        self.min = min
        self.max = max


class BoundingSphere(object):

    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class MeshPart(object):

    def __init__(self, faces, material):
        self.faces = faces
        self.material = material


class Material(object):

    def __init__(self, name, params, glossiness, diffuse_color, specular_color, technique):
        self.name = name
        self.params = params
        self.glossiness = glossiness
        self.diffuse_color = diffuse_color
        self.specular_color = specular_color
        self.technique = technique