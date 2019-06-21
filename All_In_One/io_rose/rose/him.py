import math
from .utils import *

class HimPatch:
    def __init__(self):
        minimum = 0
        maximum = 0

class Him:
    def __init__(self, filepath=None):
        self.width = 0
        self.length = 0
        self.grid_count = 0
        self.patch_scale = 0.0

        # Two dimensional array for height data
        self.heights = [] 
        self.max_height = 0.0
        self.min_height = 0.0
        
        self.patches = []
        self.quad_patches = []

        if filepath:
            self.load(filepath)

    def load(self, filepath):
        with open(filepath, 'rb') as f:
            self.width = read_i32(f)
            self.length = read_i32(f)
            self.grid_count = read_i32(f)
            self.patch_scale = read_f32(f)
            
            self.heights = list_2d(self.width, self.length, 0)
            for y in range(self.length):
                for x in range(self.width):
                    h = read_f32(f)
                    self.heights[y][x] = h

                    if h > self.max_height: self.max_height = h
                    if h < self.min_height: self.min_height = h
                    
            
            name = read_bstr(f)
            patch_count = read_i32(f)
            patch_sqrt = int(math.sqrt(patch_count))

            for h in range(patch_sqrt):
                row = []
                for w in range(patch_sqrt):
                    p = HimPatch()
                    p.maximum = read_f32(f)
                    p.minimum = read_f32(f)

                    row.append(p)

                self.patches.append(row)
            
            quad_count = read_i32(f)
            for i in range(quad_count):
                p = HimPatch()
                p.maximum = read_f32(f)
                p.minimum = read_f32(f)

                self.quad_patches.append(p)
