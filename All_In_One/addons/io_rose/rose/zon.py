from .utils import *

class BlockType:
    Info = 0
    Spawns = 1
    Textures = 2
    Tiles = 3
    Economy = 4

class ZoneType:
    Grass = 0
    Mountain = 1
    MountainVillage = 2
    BoatVillage = 3
    Login = 4
    MountainGorge = 5
    Beach = 6
    JunonDungeon = 7
    LunaSnow = 8
    Birth = 9
    JunonField = 10
    LunaDungeon = 11
    EldeonField = 12
    EldeonField2 = 13
    JunonPyramids = 14

class Position:
    def __init__(self):
        self.is_used = False
        self.position = Vector2()

    def __repr__(self):
        return "Position ({},{})[{}]".format(
                self.position.x,
                self.position.y,
                "Used" if self.used else "Not Used")

class Spawn:
    def __init__(self):
        self.position = Vector3()
        self.name = ""

    def __repr__(self):
        return "Spawn '{}'".format(self.name)

class Tile:
    def __init__(self): 
        self.layer1 = 0
        self.layer2 = 0
        self.offset1 = 0
        self.offset2 = 0
        self.blending = False
        self.rotation = 0
        self.tile_type = 0

class Zon:
    def __init__(self, filepath=None):
        self.zone_type = None
        self.width = 0
        self.length = 0
        self.grid_count = 0
        self.grid_size = 0.0
        self.start_position = Vector2()
        self.positions = []
        self.spawns = []
        self.textures = []
        self.tiles = []

        self.name = ""
        self.is_underground = False
        self.background_music_path = ""
        self.sky_path = ""
        self.economy_check_rate = 50
        self.population_base = 100
        self.population_growth_rate = 10
        self.metal_consumption = 50
        self.stone_consumption = 50
        self.wood_consumption = 50
        self.leather_consumption = 50
        self.cloth_consumption = 50
        self.alchemy_consumption = 50
        self.chemical_consumption = 50
        self.industrial_consumption = 50
        self.medicine_consumption = 50
        self.food_consumption = 50

        if filepath:
            self.load(filepath)
    
    def __repr__(self):
        return "{} zone".format(self.zone_type)

    def load(self, filepath):
        with open(filepath, "rb") as f:
            block_count = read_i32(f)
            
            for i in range(block_count):
                block_type = read_i32(f)
                block_offset = read_i32(f)

                next_block = f.tell()
                f.seek(block_offset)

                if block_type == BlockType.Info:
                    self.zone_type = read_i32(f)
                    self.width = read_i32(f)
                    self.length = read_i32(f)
                    self.grid_count = read_i32(f)
                    self.grid_size = read_f32(f)

                    self.start_position.x = read_i32(f)
                    self.start_position.y = read_i32(f)
                    
                    self.positions = list_2d(self.width, self.length)
                    for y in range(self.width):
                        for x in range(self.length):
                            p = Position()
                            p.is_used = read_bool(f)
                            p.position.x = read_f32(f)
                            p.position.y = read_f32(f)
                            self.positions[y][x] = p

                elif block_type == BlockType.Spawns:
                    spawn_count = read_i32(f)

                    for j in range(spawn_count):
                        s = Spawn()
                        s.position.x = read_f32(f)
                        s.position.y = read_f32(f)
                        s.position.z = read_f32(f)
                        s.name = read_bstr(f)
                        
                        self.spawns.append(s)
                    
                elif block_type == BlockType.Textures:
                    texture_count = read_i32(f)

                    for j in range(texture_count):
                        self.textures.append(read_bstr(f))

                elif block_type == BlockType.Tiles:
                    tile_count = read_i32(f)

                    for j in range(tile_count):
                        t = Tile()
                        t.layer1 = read_i32(f)
                        t.layer2 = read_i32(f)
                        t.offset1 = read_i32(f)
                        t.offset2 = read_i32(f)
                        t.blending = (read_i32(f) != 0)
                        t.rotation = read_i32(f)
                        t.tile_type = read_i32(f)

                        self.tiles.append(t)

                elif block_type == BlockType.Economy:
                    self.name = read_bstr(f)
                    self.is_underground = (read_i32(f) != 0)
                    self.background_music_path = read_bstr(f)
                    self.sky_path = read_bstr(f)
                    self.economy_check_rate = read_i32(f)
                    self.population_base = read_i32(f)
                    self.population_growth_rate = read_i32(f)
                    self.metal_consumption = read_i32(f)
                    self.stone_consumption = read_i32(f)
                    self.wood_consumption = read_i32(f)
                    self.leather_consumption = read_i32(f)
                    self.cloth_consumption = read_i32(f)
                    self.alchemy_consumption = read_i32(f)
                    self.chemical_consumption = read_i32(f)
                    self.industrial_consumption = read_i32(f)
                    self.medicine_consumption = read_i32(f)
                    self.food_consumption = read_i32(f)

                if i < (block_count - 1):
                    f.seek(next_block)
