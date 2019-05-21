import io
from .gnd import Gnd
from ..io.reader import BinaryFileReader
from itertools import islice
from ..semver.version import Version


# https://stackoverflow.com/a/22045226/2209008
def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class GndReader(object):
    def __init__(self):
        pass

    @staticmethod
    def from_file(path):
        with open(path, 'rb') as f:
            return GndReader.from_stream(f)

    @staticmethod
    def from_stream(f):
        reader = BinaryFileReader(f)
        magic = reader.read('4s')[0]
        if magic != b'GRGN':
            raise RuntimeError('Unrecognized file format.')
        gnd = Gnd()
        version = Version(*reader.read('2B'))
        gnd.width, gnd.height = reader.read('2I')
        gnd.scale = reader.read('f')[0]
        texture_count = reader.read('I')[0]
        texture_name_length = reader.read('I')[0]
        for i in range(texture_count):
            texture = Gnd.Texture()
            texture.path = reader.read_fixed_length_null_terminated_string(texture_name_length)
            gnd.textures.append(texture)
        lightmap_count = reader.read('I')[0]
        gnd.lightmap_size = reader.read('3I')
        print(gnd.lightmap_size)
        # this is related, in some way, to the tile faces
        for i in range(lightmap_count):
            lightmap = Gnd.Lightmap()
            lightmap.luminosity = reader.read('64B')
            lightmap.color = list(chunk(reader.read('192B'), 3))
            gnd.lightmaps.append(lightmap)
        face_count = reader.read('I')[0]
        for i in range(face_count):
            face = Gnd.Face()
            face.texcoords = reader.read('8f')
            face.texture_index = reader.read('H')[0]
            face.lightmap_index = reader.read('H')[0]
            face.lighting = reader.read('4B')  # not confirmed, but this is likely vertex lighting info
            gnd.faces.append(face)
        # Tiles
        for i in range(gnd.width):
            for j in range(gnd.height):
                k = i * gnd.height + j
                tile = Gnd.Tile()
                tile.heights = reader.read('4f')
                tile.face_indices = reader.read('3i')
                gnd.tiles.append(tile)
        return gnd
