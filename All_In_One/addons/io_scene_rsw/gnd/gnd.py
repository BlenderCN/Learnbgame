
class Gnd(object):

    class Lightmap(object):
        def __init__(self):
            self.luminosity = None
            self.color = None

    class Texture(object):
        def __init__(self, path=''):
            self.path = path
            self.data = None

    class Tile(object):
        def __init__(self):
            self.heights = None
            self.face_indices = (-1, -1, -1)

        def __getitem__(self, item):
            return self.heights[item]

    class Face(object):
        def __init__(self):
            self.texcoords = None
            self.texture_index = 0
            self.lightmap_index = 0
            self.lighting = None

        @property
        def uvs(self):
            for i in range(4):
                yield (self.texcoords[i], self.texcoords[i + 4])

    def __init__(self):
        self.lightmaps = []
        self.textures = []
        self.tiles = []
        self.faces = []
        self.width = 0
        self.height = 0
        self.scale = (1, 1, 1)
