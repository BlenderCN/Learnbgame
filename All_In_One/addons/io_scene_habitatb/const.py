FACE_QUAD = 1               # 0x1
FACE_DOUBLE = 2             # 0x2
FACE_TRANSLUCENT = 4        # 0x4
FACE_MIRROR = 128           # 0x80
FACE_TRANSL_TYPE = 256      # 0x100
FACE_TEXANIM = 512          # 0x200
FACE_NOENV = 1024           # 0x400
FACE_ENV = 2048             # 0x800
FACE_CLOTH = 4096           # 0x1000
FACE_SKIP = 8192            # 0x2000

FACE_PROPS = [FACE_QUAD, 
              FACE_DOUBLE, 
              FACE_TRANSLUCENT, 
              FACE_MIRROR, 
              FACE_TRANSL_TYPE, 
              FACE_TEXANIM, 
              FACE_NOENV, 
              FACE_ENV, 
              FACE_CLOTH, 
              FACE_SKIP]

materials = [
    ("MATERIAL_NONE", "None", "None", "", -1),
    ("MATERIAL_DEFAULT", "Default", "None", "", 0),
    ("MATERIAL_MARBLE", "Marble", "None", "", 1),
    ("MATERIAL_STONE", "Stone", "None", "", 2),
    ("MATERIAL_WOOD", "Wood", "None", "", 3),
    ("MATERIAL_SAND", "Sand", "None", "", 4),
    ("MATERIAL_PLASTIC", "Plastic", "None", "", 5),
    ("MATERIAL_CARPETTILE", "Carpet tile", "None", "", 6),
    ("MATERIAL_CARPETSHAG", "Carpet shag", "None", "", 7),
    ("MATERIAL_BOUNDARY", "Boundary", "None", "", 8),
    ("MATERIAL_GLASS", "Glass", "None", "", 9),
    ("MATERIAL_ICE1", "Ice 1", "None", "", 10),
    ("MATERIAL_METAL", "Metal", "None", "", 11),
    ("MATERIAL_GRASS", "Grass", "None", "", 12),
    ("MATERIAL_BUMPMETAL", "Bump metal", "None", "", 13),
    ("MATERIAL_PEBBLES", "Pebbles", "None", "", 14),
    ("MATERIAL_GRAVEL", "Gravel", "None", "", 15),
    ("MATERIAL_CONVEYOR1", "Conveyor 1", "None", "", 16),
    ("MATERIAL_CONVEYOR2", "Conveyor 2", "None", "", 17),
    ("MATERIAL_DIRT1", "Dirt 1", "None", "", 18),
    ("MATERIAL_DIRT2", "Dirt 2", "None", "", 19),
    ("MATERIAL_DIRT3", "Dirt 3", "None", "", 20),
    ("MATERIAL_ICE2", "Ice 2", "None", "", 21),
    ("MATERIAL_ICE3", "Ice 3", "None", "", 22)
    ]

object_types = [
    ("OBJECT_TYPE_CAR", "Car", "Car", "", -1),
    ("OBJECT_TYPE_BARREL", "Barrel", "Barrel", "", 1),
    ("OBJECT_TYPE_BEACHBALL", "Beachball", "Beachball", "", 2),
    ("OBJECT_TYPE_PLANET", "Planet", "Planet", "", 3),
    ("OBJECT_TYPE_PLANE", "Plane", "Plane", "", 4),
    ("OBJECT_TYPE_COPTER", "Copter", "Copter", "", 5),
    ("OBJECT_TYPE_DRAGON", "Dragon", "Dragon", "", 6),
    ("OBJECT_TYPE_WATER", "Water", "Water", "", 7),
    ("OBJECT_TYPE_TROLLEY", "Trolley", "Trolley", "", 8),
    ("OBJECT_TYPE_BOAT", "Boat", "Boat", "", 9),
    ("OBJECT_TYPE_SPEEDUP", "Speedup", "Speedup", "", 10),
    ("OBJECT_TYPE_RADAR", "Radar", "Radar", "", 11),
    ("OBJECT_TYPE_BALLOON", "Balloon", "Balloon", "", 12),
    ("OBJECT_TYPE_HORSE", "Horse", "Horse", "", 13),
    ("OBJECT_TYPE_TRAIN", "Train", "Train", "", 14),
    ("OBJECT_TYPE_STROBE", "Strobe", "Strobe", "", 15),
    ("OBJECT_TYPE_FOOTBALL", "Football", "Football", "", 16),
    ("OBJECT_TYPE_SPARKGEN", "Sparkgen", "Sparkgen", "", 17),
    ("OBJECT_TYPE_SPACEMAN", "Spaceman", "Spaceman", "", 18),
    ("OBJECT_TYPE_SHOCKWAVE", "Shockwave", "Shockwave", "", 19),
    ("OBJECT_TYPE_FIREWORK", "Firework", "Firework", "", 20),
    ("OBJECT_TYPE_PUTTYBOMB", "Puttybomb", "Puttybomb", "", 21),
    ("OBJECT_TYPE_WATERBOMB", "Waterbomb", "Waterbomb", "", 22),
    ("OBJECT_TYPE_ELECTROPULSE", "Electropulse", "Electropulse", "", 23),
    ("OBJECT_TYPE_OILSLICK", "Oilslick", "Oilslick", "", 24),
    ("OBJECT_TYPE_OILSLICK_DROPPER", "Oilslick dropper", "Oilslick dropper", "", 25),
    ("OBJECT_TYPE_CHROMEBALL", "Chromeball", "Chromeball", "", 26),
    ("OBJECT_TYPE_CLONE", "Clone", "Clone", "", 27),
    ("OBJECT_TYPE_TURBO", "Turbo", "Turbo", "", 28),
    ("OBJECT_TYPE_ELECTROZAPPED", "Electrozapped", "Electrozapped", "", 29),
    ("OBJECT_TYPE_SPRING", "Spring", "Spring", "", 30),
    ("OBJECT_TYPE_PICKUP", "Pickup", "Pickup", "", 31),
    ("OBJECT_TYPE_DISSOLVEMODEL", "Dissolve model", "Dissolve model", "", 32),
    ("OBJECT_TYPE_FLAP", "Flap", "Flap", "", 33),
    ("OBJECT_TYPE_LASER", "Laser", "Laser", "", 34),
    ("OBJECT_TYPE_SPLASH", "Splash", "Splash", "", 35),
    ("OBJECT_TYPE_BOMBGLOW", "Bombglow", "Bombglow", "", 36),
    ("OBJECT_TYPE_MAX", "Max", "Max", "", 37),
    ]