from collections import namedtuple
from functools import lru_cache
from math import ceil, floor

from vgio.quake.bsp import Bsp as BspFile
from vgio.quake.bsp import is_bspfile
from vgio.quake import map as Map


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def sub2(a, b):
    return a[0] - b[0], a[1] - b[1]


LightMapImage = namedtuple('LightMapImage', 'size pixels')


class Face:
    def __init__(self, bsp, face):
        self._bsp_file = bsp
        self._face = face

    @property
    @lru_cache(maxsize=1)
    def edges(self):
        return self._bsp_file.surf_edges[self._face.first_edge:self._face.first_edge + self._face.number_of_edges]

    @property
    @lru_cache(maxsize=1)
    def vertices(self):
        verts = []
        for edge in self.edges:
            v = self._bsp_file.edges[abs(edge)].vertexes

            # Flip edges with negative ids
            v0, v1 = v if edge > 0 else reversed(v)

            if len(verts) == 0:
                verts.append(v0)

            if v1 != verts[0]:
                verts.append(v1)

        # Ignore degenerate faces
        if len(verts) < 3:
            return None

        # Convert Vertexes to three-tuples and reverse their order
        return tuple(tuple(self._bsp_file.vertexes[i][:]) for i in reversed(verts))

    @property
    @lru_cache(maxsize=1)
    def uvs(self):
        texture_info = self._bsp_file.texture_infos[self._face.texture_info]
        miptex = self._bsp_file.miptextures[texture_info.miptexture_number]
        s, t = texture_info.s, texture_info.t
        ds, dt = texture_info.s_offset, texture_info.t_offset
        w, h = miptex.width, miptex.height

        return tuple(((dot3(v, s) + ds) / w, -(dot3(v, t) + dt) / h) for v in self.vertices)

    @property
    @lru_cache(maxsize=1)
    def lightmap_sts(self):
        plane = self._bsp_file.planes[self._face.plane_number]
        axis = plane.type % 3
        projected_verts = [v[:axis] + v[axis + 1:] for v in self.vertices]

        return projected_verts

    @property
    @lru_cache(maxsize=1)
    def lightmap_uvs(self):
        #texture_info = self._bsp_file.texture_infos[self._face.texture_info]
        #miptex = self._bsp_file.miptextures[texture_info.miptexture_number]
        #w, h = miptex.width, miptex.height
        #sts = self.lightmap_sts
        w, h = 16, 16
        return [(st[0] / w, st[1] / h) for st in self.lightmap_sts]

    @property
    @lru_cache(maxsize=1)
    def lightmap_image(self):
        min_x, min_y = self.lightmap_sts[0]
        max_x, max_y = self.lightmap_sts[0]

        for v in self.lightmap_sts[1:]:
            min_x = min(min_x, v[0])
            min_y = min(min_y, v[1])
            max_x = max(max_x, v[0])
            max_y = max(max_y, v[1])

        top_left = ceil(min_x / 16), floor(min_y / 16)
        bottom_right = ceil(max_x / 16), floor(max_y / 16)
        scale = sub2(bottom_right, top_left)
        size = scale[0] + 1, scale[1] + 1
        length = size[0] * size[1]

        offset = self._face.light_offset
        pixels = []

        if offset >= 0:
            light_data = self._bsp_file.lighting[offset:offset + length]
            for luxel in light_data:
                r = g = b = luxel / 255
                pixels += r, g, b, 1.0

        else:
            pixels = (0, 0, 0, 1.0) * length

        return LightMapImage(size, pixels)

    @property
    @lru_cache(maxsize=1)
    def texture_name(self):
        texture_info = self._bsp_file.texture_infos[self._face.texture_info]
        miptex = self._bsp_file.miptextures[texture_info.miptexture_number]

        return miptex.name


class Model:
    def __init__(self, bsp, model):
        self._bsp_file = bsp
        self._model = model
        self._faces = bsp.faces[model.first_face:model.first_face + model.number_of_faces]

    def get_face(self, face_index):
        return Face(self._bsp_file, self._faces[face_index])

    @property
    def faces(self):
        for face in self._faces:
            if face:
                yield Face(self._bsp_file, face)


class Bsp:
    def __init__(self, file):
        self._bsp_file = BspFile.open(file)
        self._bsp_file.close()

    def get_model(self, model_index):
        return Model(self._bsp_file, self._bsp_file.models[model_index])

    @property
    def models(self):
        for model in self._bsp_file.models:
            yield Model(self._bsp_file, model)

    @property
    def images(self):
        return self._bsp_file.images()

    @property
    def miptextures(self):
        return self._bsp_file.miptextures[:]

    @property
    @lru_cache(maxsize=1)
    def entities(self):
        return Map.loads(self._bsp_file.entities)
