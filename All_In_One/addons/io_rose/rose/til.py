from .utils import *

class TilPatch:
    def __init__(self):
        self.brush = 0
        self.tile_index = 0
        self.tile_set = 0
        self.tile = 0

class Til:
    def __init__(self, filepath=None):
        self.width = 0
        self.length = 0
        self.tiles = []

        if filepath:
            self.load(filepath)

    def load(self, filepath):
        with open(filepath, 'rb') as f:
            self.width = read_i32(f)
            self.length = read_i32(f)
            
            self.tiles = list_2d(self.width, self.length)

            for l in range(self.length-1, -1, -1):
                for w in range(self.width):
                    t = TilPatch()
                    t.brush = read_i8(f)
                    t.tile_index = read_i8(f)
                    t.tile_set = read_i8(f)
                    t.tile = read_i32(f)

                    self.tiles[l][w] = t


