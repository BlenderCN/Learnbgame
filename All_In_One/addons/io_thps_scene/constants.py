__reload_order_index__ = -108
ADDON_NAME = "io_thps_scene"
ADDON_VERSION = '1.0'

CRCTable = [  # CRC polynomial 0xedb88320
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba,
    0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
    0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
    0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
    0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de,
    0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec,
    0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
    0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172,
    0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
    0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940,
    0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116,
    0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
    0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924,
    0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
    0x76dc4190, 0x01db7106, 0x98d220bc, 0xefd5102a,
    0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
    0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818,
    0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01,
    0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e,
    0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
    0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c,
    0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
    0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2,
    0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
    0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0,
    0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
    0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086,
    0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
    0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4,
    0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
    0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a,
    0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683,
    0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8,
    0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
    0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe,
    0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
    0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc,
    0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
    0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252,
    0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
    0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60,
    0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
    0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236,
    0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
    0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04,
    0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
    0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a,
    0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713,
    0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38,
    0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21,
    0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e,
    0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
    0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c,
    0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
    0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2,
    0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
    0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0,
    0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
    0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6,
    0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
    0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94,
    0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d
]

D3DFVF_XYZ = 0x002
D3DFVF_NORMAL = 0x010
D3DFVF_DIFFUSE = 0x040
D3DFVF_TEX0 = 0x000
D3DFVF_TEX1 = 0x100
D3DFVF_TEX2 = 0x200
D3DFVF_TEX3 = 0x300
D3DFVF_TEX4 = 0x400

COMPRESSED_RGB_S3TC_DXT1_EXT  =                0x83F0
COMPRESSED_RGBA_S3TC_DXT1_EXT =                0x83F1
COMPRESSED_RGBA_S3TC_DXT3_EXT =                0x83F2
COMPRESSED_RGBA_S3TC_DXT5_EXT =                0x83F3

SECFLAGS_BILLBOARD_PRESENT = 0x00800000
SECFLAGS_SHADOW_VOLUME = 0x200000
SECFLAGS_HAS_TEXCOORDS = 0x01
SECFLAGS_HAS_VERTEX_COLORS = 0x02
SECFLAGS_HAS_VERTEX_COLOR_WIBBLES = 0x800
SECFLAGS_HAS_VERTEX_NORMALS = 0x04
SECFLAGS_HAS_VERTEX_WEIGHTS = 0x10

FACE_FLAGS = {
    "mFD_SKATABLE": 0x00000001,
    "mFD_NOT_SKATABLE": 0x00000002,
    "mFD_WALL_RIDABLE": 0x00000004,
    "mFD_VERT": 0x00000008,
    "mFD_NON_COLLIDABLE": 0x00000010,
    "mFD_DECAL": 0x00000020,
    "mFD_TRIGGER": 0x00000040,
    "mFD_CAMERA_COLLIDABLE": 0x00000080,
    "mFD_NO_SKATER_SHADOW": 0x00000100,
    "mFD_SKATER_SHADOW": 0x00000200,
    "mFD_NO_SKATER_SHADOW_WALL": 0x00000400,
    "mFD_UNDER_OK": 0x00000800,
    "mFD_INVISIBLE": 0x00001000,
    "mFD_CASFACEFLAGSEXIST": 0x00002000,
    "mFD_PASS_1_DISABLED": 0x00004000,
    "mFD_PASS_2_ENABLED": 0x00008000,
    "mFD_PASS_3_ENABLED": 0x00010000,
    "mFD_PASS_4_ENABLED": 0x00020000,
    "mFD_RENDER_SEPARATE": 0x00040000,
    "mFD_LIGHTMAPPED": 0x00080000,
    "mFD_NON_WALL_RIDABLE": 0x00100000,
    "mFD_NON_CAMERA_COLLIDABLE": 0x00200000,
    "mFD_EXPORT_COLLISION": 0x00400000,
}
SETTABLE_FACE_FLAGS = [
    "mFD_VERT", "mFD_WALL_RIDABLE",
    "mFD_NON_COLLIDABLE", "mFD_NO_SKATER_SHADOW",
    "mFD_NO_SKATER_SHADOW_WALL", "mFD_TRIGGER",
    # Adding these, hope nothing breaks!
    "mFD_SKATABLE", "mFD_NOT_SKATABLE", "mFD_UNDER_OK", "mFD_INVISIBLE"
]

mSD_INVISIBLE           = 0x0001  # Invisible in primary viewport
mSD_NON_COLLIDABLE      = 0x0002
mSD_KILLED              = 0x0004
mSD_DONT_FOG            = 0x0008
mSD_ALWAYS_FACE         = 0x0010
mSD_NO_SKATER_SHADOW    = 0x0020  # This is set at runtime for sectors with every face flagged mFD_SKATER_SHADOW.
mSD_INVISIBLE2          = 0x0040  # Invisible in secondary viewport (Mick)
mSD_OCCLUDER            = 0x0080  # Occluder (it's a single plane that hides stuff)
mSD_CLONE               = 0x8000  # Cloned collision object (Garrett)

TERRAIN_TYPES = [
    "DEFAULT",
    "CONCSMOOTH",
    "CONCROUGH",
    "METALSMOOTH",
    "METALROUGH",
    "METALCORRUGATED",
    "METALGRATING",
    "METALTIN",
    "WOOD",
    "WOODMASONITE",
    "WOODPLYWOOD",
    "WOODFLIMSY",
    "WOODSHINGLE",
    "WOODPIER",
    "BRICK",
    "TILE",
    "ASPHALT",
    "ROCK",
    "GRAVEL",
    "SIDEWALK",
    "GRASS",
    "GRASSDRIED",
    "DIRT",
    "DIRTPACKED",
    "WATER",
    "ICE",
    "SNOW",
    "SAND",
    "PLEXIGLASS",
    "FIBERGLASS",
    "CARPET",
    "CONVEYOR",
    "CHAINLINK",
    "METALFUTURE",
    "GENERIC1",
    "GENERIC2",
    "WHEELS",  # K: Used only by the skateboard wheels, as a means of identifying them so their color can be changed.
    "WETCONC",
    "METALFENCE",
    "GRINDTRAIN",
    "GRINDROPE",
    "GRINDWIRE",
    "GRINDCONC",  # New as of 7/29/03
    "GRINDROUNDMETALPOLE",
    "GRINDCHAINLINK",
    "GRINDMETAL",
    "GRINDWOODRAILING",
    "GRINDWOODLOG",
    "GRINDWOOD",
    "GRINDPLASTIC",
    "GRINDELECTRICWIRE",
    "GRINDCABLE",
    "GRINDCHAIN",
    "GRINDPLASTICBARRIER",
    "GRINDNEONLIGHT",
    "GRINDGLASSMONSTER",
    "GRINDBANYONTREE",
    "GRINDBRASSRAIL",
    "GRINDCATWALK",
    "GRINDTANKTURRET",
    "GRINDRUSTYRAIL",
]

TERRAIN_TYPE_TO_GRIND = {
    "ASPHALT": "GRINDCONC",
    "ROCK": "GRINDCONC",
    "CONCSMOOTH": "GRINDCONC",
    "CONCROUGH": "GRINDCONC",
    "SIDEWALK": "GRINDCONC",
    "TILE": "GRINDCONC",
    "GRAVEL": "GRINDCONC",
    "BRICK": "GRINDCONC",
    "WETCONC": "GRINDCONC",

    "CHAINLINK": "GRINDCHAINLINK",

    "PLEXIGLASS": "GRINDGLASSMONSTER",
    "FIBERGLASS": "GRINDGLASSMONSTER",

    "CONVEYOR": "GRINDMETAL",
    "METALFENCE": "GRINDMETAL",
    "METALFUTURE": "GRINDMETAL",
    "METALSMOOTH": "GRINDMETAL",
    "METALROUGH": "GRINDMETAL",
    "METALCORRUGATED": "GRINDMETAL",
    "METALGRATING": "GRINDMETAL",
    "METALTIN": "GRINDMETAL",

    "WOOD": "GRINDWOOD",
    "WOODMASONITE": "GRINDWOOD",
    "WOODPLYWOOD": "GRINDWOOD",
    "WOODFLIMSY": "GRINDWOOD",
    "WOODSHINGLE": "GRINDWOOD",
    "WOODSHINGLE": "GRINDWOOD",
}


MATFLAG_UV_WIBBLE =                (1 << 0)
MATFLAG_VC_WIBBLE =                (1 << 1)
MATFLAG_TEXTURED =                 (1 << 2)
MATFLAG_ENVIRONMENT =              (1 << 3)
MATFLAG_DECAL =                    (1 << 4)
MATFLAG_SMOOTH =                   (1 << 5)
MATFLAG_TRANSPARENT =              (1 << 6)
MATFLAG_PASS_COLOR_LOCKED =        (1 << 7)
MATFLAG_SPECULAR =                 (1 << 8)  # Specular lighting is enabled on this material (Pass0).
MATFLAG_BUMP_SIGNED_TEXTURE =      (1 << 9)  # This pass uses an offset texture which needs to be treated as signed data.
MATFLAG_BUMP_LOAD_MATRIX =         (1 << 10)  # This pass requires the bump mapping matrix elements to be set up.
MATFLAG_PASS_TEXTURE_ANIMATES =    (1 << 11)  # This pass has a texture which animates.
MATFLAG_PASS_IGNORE_VERTEX_ALPHA = (1 << 12)  # This pass should not have the texel alpha modulated by the vertex alpha.
MATFLAG_EXPLICIT_UV_WIBBLE =       (1 << 14)  # Uses explicit uv wibble (set via script) rather than calculated.
MATFLAG_WATER_EFFECT =             (1 << 27)  # This material should be processed to provide the water effect.
MATFLAG_NO_MAT_COL_MOD =           (1 << 28)  # No material color modulation required (all passes have m.rgb = 0.5).
MATFLAG_NORMAL_TEST =              (1 << 29)    # TEST

vBLEND_MODE_DIFFUSE = 0                                # ( 0 - 0 ) * 0 + Src
vBLEND_MODE_ADD = 1                                    # ( Src - 0 ) * Src + Dst
vBLEND_MODE_ADD_FIXED = 2                              # ( Src - 0 ) * Fixed + Dst
vBLEND_MODE_SUBTRACT = 3                               # ( 0 - Src ) * Src + Dst
vBLEND_MODE_SUB_FIXED = 4                              # ( 0 - Src ) * Fixed + Dst
vBLEND_MODE_BLEND = 5                                  # ( Src * Dst ) * Src + Dst
vBLEND_MODE_BLEND_FIXED = 6                            # ( Src * Dst ) * Fixed + Dst
vBLEND_MODE_MODULATE = 7                               # ( Dst - 0 ) * Src + 0
vBLEND_MODE_MODULATE_FIXED = 8                         # ( Dst - 0 ) * Fixed + 0
vBLEND_MODE_BRIGHTEN = 9                               # ( Dst - 0 ) * Src + Dst
vBLEND_MODE_BRIGHTEN_FIXED = 10                         # ( Dst - 0 ) * Fixed + Dst
vBLEND_MODE_GLOSS_MAP = 11              # Specular = Specular * Src    - special mode for gloss mapping
vBLEND_MODE_BLEND_PREVIOUS_MASK = 12                    # ( Src - Dst ) * Dst + Dst
vBLEND_MODE_BLEND_INVERSE_PREVIOUS_MASK = 13            # ( Dst - Src ) * Dst + Src
vBLEND_MODE_MODULATE_COLOR = 15  # ( Dst - 0 ) * Src(col) + 0   - special mode for the shadow.
vBLEND_MODE_ONE_INV_SRC_ALPHA = 17  #                           - special mode for imposter rendering.
vBLEND_MODE_OVERLAY = 18  #                           - special mode for imposter rendering.

BLEND_MODES = {
    0: "vBLEND_MODE_DIFFUSE",
    1: "vBLEND_MODE_ADD",
    2: "vBLEND_MODE_ADD_FIXED",
    3: "vBLEND_MODE_SUBTRACT",
    4: "vBLEND_MODE_SUB_FIXED",
    5: "vBLEND_MODE_BLEND",
    6: "vBLEND_MODE_BLEND_FIXED",
    7: "vBLEND_MODE_MODULATE",
    8: "vBLEND_MODE_MODULATE_FIXED",
    9: "vBLEND_MODE_BRIGHTEN",
    10: "vBLEND_MODE_BRIGHTEN_FIXED",
    11: "vBLEND_MODE_GLOSS_MAP",
    12: "vBLEND_MODE_BLEND_PREVIOUS_MASK",
    13: "vBLEND_MODE_BLEND_INVERSE_PREVIOUS_MASK",
    15: "vBLEND_MODE_MODULATE_COLOR",
    17: "vBLEND_MODE_ONE_INV_SRC_ALPHA",
    18: "vBLEND_MODE_OVERLAY",
}

BILLBOARD_TYPES = {
    'SCREEN': 1,
    'AXIS': 2
}

THUG_DefaultGameObjects = {
    "Combo_C": "gameobjects\\combo\\goal_combo_c\\goal_combo_c.mdl"
    ,"Combo_O": "gameobjects\\combo\\goal_combo_o\\goal_combo_o.mdl"
    ,"Combo_M": "gameobjects\\combo\\goal_combo_m\\goal_combo_m.mdl"
    ,"Combo_B": "gameobjects\\combo\\goal_combo_b\\goal_combo_b.mdl"
    ,"Secret_Tape": "gameobjects\\secret_tape\\secret_tape.mdl"
    ,"Team_Blue": "gameobjects\\flags\\flag_blue\\flag_blue.mdl"
    ,"Team_Red": "gameobjects\\flags\\flag_red\\flag_red.mdl"
    ,"Team_Green": "gameobjects\\flags\\flag_green\\flag_green.mdl"
    ,"Team_Yellow": "gameobjects\\flags\\flag_yellow\\flag_yellow.mdl"
    ,"Flag_Blue": "gameobjects\\flags\\flag_blue\\flag_blue.mdl"
    ,"Flag_Blue_Base": "gameobjects\\flags\\flag_blue_base\\flag_blue_base.mdl"
    ,"Team_Blue_Base": "gameobjects\\flags\\flag_blue_base\\flag_blue_base.mdl"
    ,"Flag_Red": "gameobjects\\flags\\flag_red\\flag_red.mdl"
    ,"Flag_Red_Base": "gameobjects\\flags\\flag_red_base\\flag_red_base.mdl"
    ,"Team_Red_Base": "gameobjects\\flags\\flag_red_base\\flag_red_base.mdl"
    ,"Flag_Green": "gameobjects\\flags\\flag_green\\flag_green.mdl"
    ,"Flag_Green_Base": "gameobjects\\flags\\flag_green_base\\flag_green_base.mdl"
    ,"Team_Green_Base": "gameobjects\\flags\\flag_green_base\\flag_green_base.mdl"
    ,"Flag_Yellow": "gameobjects\\flags\\flag_yellow\\flag_yellow.mdl"
    ,"Flag_Yellow_Base": "gameobjects\\flags\\flag_yellow_base\\flag_yellow_base.mdl"
    ,"Team_Yellow_Base": "gameobjects\\flags\\flag_yellow_base\\flag_yellow_base.mdl"
    ,"Ghost": "none"
}

# Used for collision exporting!
SIZEOF_SECTOR_HEADER = 8 * 4
SIZEOF_SECTOR_OBJ = 64
SIZEOF_FLOAT_VERT = 3 * 4
SIZEOF_FLOAT_VERT_THPS4 = 4 * 4
SIZEOF_FIXED_VERT = 3 * 2
SIZEOF_LARGE_FACE = 2 * 2 + 2 * 3
SIZEOF_LARGE_FACE_THPS4 = 2 * 2 + 2 * 4
SIZEOF_SMALL_FACE = 2 * 2 + 1 * 3
SIZEOF_SMALL_FACE_THPS4 = 8
SIZEOF_BSP_NODE = 2 * 4