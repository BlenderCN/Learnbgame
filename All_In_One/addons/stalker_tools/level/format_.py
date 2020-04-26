
class Chunks:
    class LevelVersion12:
        SHADERS = 0x2
        VISUALS = 0x3
        PORTALS = 0x4
        LIGHT_DYNAMIC = 0x6
        GLOWS = 0x7
        SECTORS = 0x8
        IB = 0x9
        VB = 0xa
        SWIS = 0xb

    class LevelVersion13(LevelVersion12):
        VB = 0x9
        IB = 0xa

    class LevelVersion14(LevelVersion13):
        pass

    class Sector:
        PORTALS = 0x1
        ROOT = 0x2

    HEADER = 0x1


# format versions
XRLC_VERSION_11 = 11
XRLC_VERSION_12 = 12
XRLC_VERSION_13 = 13
XRLC_VERSION_14 = 14
XRLC_SUPPORT_VERSIONS = [
    XRLC_VERSION_11,
    XRLC_VERSION_12,
    XRLC_VERSION_13,
    XRLC_VERSION_14
]

# others
PORTAL_SIZE = 80
PORTAL_VERTEX_COUNT = 6
LIGHT_DYNAMIC_SIZE = 108
GLOW_SIZE = 18
SECTOR_PORTAL_SIZE = 2
CHUNKS_TABLE = {
    11: Chunks.LevelVersion12,
    12: Chunks.LevelVersion12,
    13: Chunks.LevelVersion13,
    14: Chunks.LevelVersion14
}
