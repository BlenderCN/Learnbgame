from enum import Enum


# Maps the hash id of each file type that the format accept
# and its corresponding extension. If the type is used throughout
# This list was provided by users in the Xentax forums.
# To do: search the users and credit them.

FILE_ID_TO_EXTENSION = {
    0x22fa09: "hpe",
    0x26e7ff: "ccl",
    0x86b80f: "plexp",
    0xfda99b: "ntr",
    0x2358e1a: "spkg",
    0x2373ba7: "spn",
    0x2833703: "efs",
    0x58a15856: "mod",
    0x315e81f: "sds",
    0x437bcf2: "grw",
    0x4b4be62: "tmd",
    0x525aee2: "wfp",
    0x5a36d08: "qif",
    0x69a1911: "olp",
    0x737e28b: "rst",
    0x7437cce: "base",
    0x79b5f3e: "pci",
    0x7b8bcde: "fca",
    0x7f768af: "gii",
    0x89bef2c: "sap",
    0xa74682f: "rnp",
    0xc4fcae4: "PldefendParam",
    0xd06be6b: "tmn",
    0xecd7df4: "sca",
    0x11c35522: "gr2",
    0x12191ba1: "epv",
    0x12688d38: "pjp",
    0x12c3bfa7: "cpl",
    0x133917ba: "mss",
    0x14428eae: "gce",
    0x15302ef4: "lot",
    0x157388d3: "itl",
    0x15773620: "nmr",
    0x167dbbff: "stq",
    0x1823137d: "mlm",
    0x19054795: "nml",
    0x199c56c0: "ocl",
    0x1b520b68: "zon",
    0x1bcc4966: "srq",
    0x1c2b501f: "atr",
    0x1eb3767c: "spr",
    0x2052d67e: "sn2",
    0x215896c2: "statusparam",
    0x2282360d: "jex",
    0x22948394: "gui",
    0x22b2a2a2: "PlNeckPos",
    0x232e228c: "rev",
    0x241f5deb: "tex",
    0x242bb29a: "gmd",
    0x257d2f7c: "swm",
    0x2749c8a8: "mrl",
    0x271d08fe: "ssq",
    0x272b80ea: "prp",
    0x276de8b7: "e2d",
    0x2a37242d: "gpl",
    0x2a4f96a8: "rbd",
    0x2b0670a5: "map",
    0x2b303957: "gop",
    0x2b40ae8f: "equ",
    0x2ce309ab: "joblvl",
    0x2d12e086: "srd",
    0x2d462600: "gfd",
    0x30fc745f: "smx",
    0x312607a4: "bll",
    0x31b81aa5: "qr",
    0x325aaca5: "shl",
    0x32e2b13b: "edp",
    0x33b21191: "esp",
    0x354284e7: "lvl",
    0x358012e8: "vib",
    0x36019854: "bed",
    0x39a0d1d6: "sms",
    0x39c52040: "lcm",
    0x3a947ac1: "cql",
    0x3bba4e33: "qct",
    0x3d97ad80: "amr",
    0x3e356f93: "stc",
    0x3e363245: "chn",
    0x3fb52996: "imx",
    0x4046f1e1: "ajp",
    0x437662fc: "oml",
    0x4509fa80: "itemlv",
    0x456b6180: "cnsshake",
    0x472022df: "aIPlactParam",
    0x48538ffd: "ist",
    0x48c0af2d: "msl",
    0x49b5a885: "ssc",
    0x4b704cc0: "mia",
    0x4c0db839: "sdl",
    0x4ca26828: "bmse",
    0x4e397417: "ean",
    0x4e44fb6d: "fpe",
    0x4ef19843: "nav",
    0x4fb35a95: "aor",
    0x50f3d713: "skl",
    0x5175c242: "geo2",
    0x51fc779f: "sbc",
    0x522f7a3d: "fcp",
    0x52dbdcd6: "rdd",
    0x535d969f: "ctc",
    0x5802b3ff: "ahc",
    0x59d80140: "ablparam",
    0x5a61a7c8: "fed",
    0x5a7fea62: "ik",
    0x5b334013: "bap",
    0x5ea7a3e9: "sky",
    0x5f36b659: "way",
    0x5f88b715: "epd",
    0x60bb6a09: "hed",
    0x6186627d: "wep",
    0x619d23df: "shp",
    0x628dfb41: "gr2s",
    0x63747aa7: "rpi",
    0x63b524a7: "ltg",
    0x64387ff1: "qlv",
    0x65b275e5: "sce",
    0x66b45610: "fsm",
    0x671f21da: "stp",
    0x69a5c538: "dwm",
    0x6d0115ed: "prt",
    0x6d5ae854: "efl",
    0x6db9fa5f: "cmc",
    0x6ee70eff: "pcf",
    0x6f302481: "plw",
    0x6fe1ea15: "spl",
    0x72821c38: "stm",
    0x73850d05: "arc",
    0x754b82b4: "ahs",
    0x76820d81: "lmt",
    0x76de35f6: "rpn",
    0x7808ea10: "rtex",
    0x7817ffa5: "fbik_human",
    0x7aa81cab: "eap",
    0x7bec319a: "sps",
    0x7da64808: "qmk",
    0x7e1c8d43: "pcs",
    0x7e33a16c: "spc",
    0x7e4152ff: "stg",
    0x17a550d: "lom",
    0x253f147: "hit",
    0x39d71f2: "rvt",
    0xdadab62: "oba",
    0x10c460e6: "msg",
    0x176c3f95: "los",
    0x19a59a91: "lnk",
    0x1ba81d3c: "nck",
    0x1ed12f1b: "glp",
    0x1efb1b67: "adh",
    0x2447d742: "idm",
    0x266e8a91: "lku",
    0x2c4666d1: "smh",
    0x2dc54131: "cdf",
    0x30ed4060: "pth",
    0x36e29465: "hkx",
    0x38f66fc3: "seg",
    0x430b4ff4: "ptl",
    0x46810940: "egv",
    0x4d894d5d: "cmi",
    0x4e2fef36: "mtg",
    0x4f16b7ab: "hri",
    0x50f9db3e: "bfx",
    0x5204d557: "shp",
    0x538120de: "eng",
    0x557ecc08: "aef",
    0x585831aa: "pos",
    0x5898749c: "bgm",
    0x60524fbb: "shw",
    0x60dd1b16: "lsp",
    0x758b2eb7: "cef",
    0x7d1530c2: "sngw",
    0x46fb08ba: "bmt",
    0x285a13d9: "vzo",
    0x4323d83a: "stex",
    0x6a5cdd23: "occ",
    }

EXTENSION_TO_FILE_ID = {ext_desc: h for h, ext_desc in FILE_ID_TO_EXTENSION.items()}


class Mod156BoneAnimationMapping(Enum):
    """
    Mod156.bones_animation_mapping is an array of 256 bytes. Each index
    correspond to a certain predefined bone type, and it's used to be able to
    transfer animations between models.
    """
    ROOT = 0
    LOWER_SPINE = 1
    UPPER_SPINE = 2
    NECK = 3
    HEAD = 4
    RIGHT_SHOULDER = 5
    RIGHT_UPPER_ARM = 6
    RIGHT_ARM = 7
    RIGHT_WRIST = 8
    RIGHT_HAND = 9
    LEFT_SHOULDER = 10
    LEFT_UPPER_ARM = 11
    LEFT_ARM = 12
    LEFT_WRIST = 13
    LEFT_HAND = 14
    HIPS = 15
    RIGHT_UPPER_LEG = 16
    RIGHT_LEG = 17
    RIGHT_FOOT = 18
    RIGHT_TOE = 19
    LEFT_UPPER_LEG = 20
    LEFT_LEG = 21
    LEFT_FOOT = 22
    LEFT_TOE = 23
    RIGHT_UPPER_THUMB = 24
    RIGHT_MIDDLE_THUMB = 25
    RIGHT_LOWER_THUMB = 26
    RIGHT_UPPER_INDEX_FINGER = 27
    RIGHT_MIDDLE_INDEX_FINGER = 28
    RIGHT_LOWER_INDEX_FINGER = 29
    RIGHT_UPPER_MIDDLE_FINGER = 30
    RIGHT_MIDDLE_MIDDLE_FINGER = 31
    RIGHT_LOWER_MIDDLE_FINGER = 32
    RIGHT_PALM = 33
    RIGHT_UPPER_RING_FINGER = 34
    RIGHT_MIDDLE_RING_FINGER = 35
    RIGHT_LOWER_RING_FINGER = 36
    RIGHT_UPPER_PINKY_FINGER = 37
    RIGHT_MIDDLE_PINKY_FINGER = 38
    RIGHT_LOWER_PINKY_FINGER = 39
    LEFT_UPPER_THUMB = 40
    LEFT_MIDDLE_THUMB = 41
    LEFT_LOWER_THUMB = 42
    LEFT_UPPER_INDEX_FINGER = 43
    LEFT_MIDDLE_INDEX_FINGER = 44
    LEFT_LOWER_INDEX_FINGER = 45
    LEFT_UPPER_MIDDLE_FINGER = 46
    LEFT_MIDDLE_MIDDLE_FINGER = 47
    LEFT_LOWER_MIDDLE_FINGER = 48
    LEFT_PALM = 49
    LEFT_UPPER_RING_FINGER = 50
    LEFT_MIDDLE_RING_FINGER = 51
    LEFT_LOWER_RING_FINGER = 52
    LEFT_UPPER_PINKY_FINGER = 53
    LEFT_MIDDLE_PINKY_FINGER = 54
    LEFT_LOWER_PINKY_FINGER = 55
    RIGHT_EYE = 56
    LEFT_EYE = 57
    RIGHT_EYELID = 58
    LEFT_EYELID = 59
    JAW = 60
    UNK_61 = 61
    RIGHT_SHOULDER_DEFORM = 62
    RIGHT_ELBOW_DEFORM = 63
    LEFT_SHOULDER_DEFORM = 64
    LEFT_ELBOW_DEFORM = 65
    RIGHT_BUTT_CHEEK = 66
    LEFT_BUTT_CHEEK = 67
    RIGHT_KNEE = 68
    LEFT_KNEE = 69
    RIGHT_UPPER_ARM_DEFORM_1 = 70
    RIGHT_UPPER_ARM_DEFORM_2 = 71
    RIGHT_UPPER_ARM_DEFORM_3 = 72
    RIGHT_UPPER_ARM_DEFORM_4 = 73
    RIGHT_ARM_DEFORM_1 = 74
    RIGHT_ARM_DEFORM_2 = 75
    LEFT_UPPER_ARM_DEFORM_1 = 76
    LEFT_UPPER_ARM_DEFORM_2 = 77
    LEFT_UPPER_ARM_DEFORM_3 = 78
    LEFT_UPPER_ARM_DEFORM_4 = 79
    LEFT_ARM_DEFORM_1 = 80
    LEFT_ARM_DEFORM_2 = 81
    UNK_82 = 82
    UNK_83 = 83
    UNK_84 = 84
    UNK_85 = 85
    UNK_86 = 86
    UNK_87 = 87
    UNK_88 = 88
    UNK_89 = 89
    UNK_90 = 90
    UNK_91 = 91
    UNK_92 = 92
    UNK_93 = 93
    UNK_94 = 94
    UNK_95 = 95
    UNK_96 = 96
    UNK_97 = 97
    UNK_98 = 98
    UNK_99 = 99
    RIGHT_THUMB = 100
    LEFT_THUMB = 101
    RIGHT_BACKPACK_STRIP = 102
    LEFT_BACKPACK_STRIP = 103
    UNK_104 = 104
    UNK_105 = 105
    UNK_106 = 106
    UNK_107 = 107
    BACK_ACCESORIES_PARENT = 108
    BACK_ACCESORIES = 109
    RIGHT_BACK_ACCESORY_1_PARENT = 110
    RIGHT_BACK_ACCESORY_1 = 111
    RIGHT_BACK_ACCESORY_2_PARENT = 112
    RIGHT_BACK_ACCESORY_2 = 113
    BACK_LEFT_KNIFE_PARENT = 114
    BACK_LEFT_KNIFE = 115
    RIGHT_BACKPACK_STRIP_BACK_1_PARENT = 116
    RIGHT_BACKPACK_STRIP_BACK_1 = 117
    HAIR_FOREHEAD_LEFT_PARENT = 118
    HAIR_FOREHEAD_LEFT = 119
    HAIR_FOREHAD_RIGHT_PARENT = 120
    HAIR_FOREHAD_RIGHT = 121
    HAIR_NAPE_PARENT = 122
    HAIR_NAPE = 123
    HAIR_BACK_PARENT = 124
    HAIR_BACK = 125
    HAIR_UP_1_PARENT = 126
    HAIR_UP_1 = 127
    HAIR_UP_2_PARENT = 128
    HAIR_UP_2 = 129
    HAIR_FOREHEAD = 130
    UNK_131 = 131
    UNK_132 = 132
    UNK_133 = 133
    UNK_134 = 134
    UNK_135 = 135
    UNK_136 = 136
    UNK_137 = 137
    UNK_138 = 138
    UNK_139 = 139
    UNK_140 = 140
    UNK_141 = 141
    UNK_142 = 142
    UNK_143 = 143
    UNK_144 = 144
    UNK_145 = 145
    UNK_146 = 146
    UNK_147 = 147
    UNK_148 = 148
    UNK_149 = 149
    UNK_150 = 150
    UNK_151 = 151
    UNK_152 = 152
    UNK_153 = 153
    UNK_154 = 154
    UNK_155 = 155
    UNK_156 = 156
    UNK_157 = 157
    UNK_158 = 158
    UNK_159 = 159
    UNK_160 = 160
    UNK_161 = 161
    UNK_162 = 162
    UNK_163 = 163
    UNK_164 = 164
    UNK_165 = 165
    UNK_166 = 166
    UNK_167 = 167
    UNK_168 = 168
    UNK_169 = 169
    UNK_170 = 170
    UNK_171 = 171
    UNK_172 = 172
    UNK_173 = 173
    UNK_174 = 174
    UNK_175 = 175
    UNK_176 = 176
    UNK_177 = 177
    UNK_178 = 178
    UNK_179 = 179
    RIGHT_INNER_EYEBROW = 180
    RIGHT_OUTER_EYEBROW = 181
    LEFT_INNER_EYEBROW = 182
    LEFT_OUTER_EYEBROW = 183
    RIGHT_LOWER_EYELID = 184
    LEFT_LOWER_EYELID = 185
    RIGHT_UPPER_CHEEK = 186
    LEFT_UPPER_CHEEK = 187
    RIGHT_UPPER_OUTER_CHEEK = 188
    LEFT_UPPER_OUTER_CHEEK = 189
    RIGHT_NOSE = 190
    LEFT_NOSE = 191
    RIGHT_OUTER_LIP = 192
    RIGHT_UPPER_LIP = 193
    UPPER_LIP = 194
    LEFT_UPPER_LIP = 195
    LEFT_OUTER_LIP = 196
    LEFT_OUTER_LOWER_LIP = 197
    LOWER_LIP = 198
    LEFT_LOWER_LIP = 199
    RIGHT_LOWER_CHEEK = 200
    LEFT_LOWER_CHEEK = 201
    UNK_202 = 202
    UNK_203 = 203
    UNK_204 = 204
    UNK_205 = 205
    UNK_206 = 206
    UNK_207 = 207
    UNK_208 = 208
    UNK_209 = 209
    UNK_210 = 210
    UNK_211 = 211
    UNK_212 = 212
    UNK_213 = 213
    UNK_214 = 214
    UNK_215 = 215
    UNK_216 = 216
    UNK_217 = 217
    UNK_218 = 218
    UNK_219 = 219
    UNK_220 = 220
    UNK_221 = 221
    UNK_222 = 222
    UNK_223 = 223
    UNK_224 = 224
    UNK_225 = 225
    UNK_226 = 226
    UNK_227 = 227
    UNK_228 = 228
    UNK_229 = 229
    UNK_230 = 230
    UNK_231 = 231
    UNK_232 = 232
    UNK_233 = 233
    UNK_234 = 234
    UNK_235 = 235
    UNK_236 = 236
    UNK_237 = 237
    UNK_238 = 238
    UNK_239 = 239
    UNK_240 = 240
    UNK_241 = 241
    UNK_242 = 242
    UNK_243 = 243
    UNK_244 = 244
    UNK_245 = 245
    UNK_246 = 246
    UNK_247 = 247
    UNK_248 = 248
    UNK_249 = 249
    UNK_250 = 250
    UNK_251 = 251
    UNK_252 = 252
    UNK_253 = 253
    UNK_254 = 254
    UNK_255 = 255

BONE_GROUP_MAIN = {
    'ROOT',
    'LOWER_SPINE',
    'UPPER_SPINE',
    'NECK',
    'HEAD',
    'RIGHT_SHOULDER',
    'RIGHT_UPPER_ARM',
    'RIGHT_ARM',
    'RIGHT_WRIST',
    'RIGHT_HAND',
    'LEFT_SHOULDER',
    'LEFT_UPPER_ARM',
    'LEFT_ARM',
    'LEFT_WRIST',
    'LEFT_HAND',
    'HIPS',
    'RIGHT_UPPER_LEG',
    'RIGHT_LEG',
    'RIGHT_FOOT',
    'RIGHT_TOE',
    'LEFT_UPPER_LEG',
    'LEFT_LEG',
    'LEFT_FOOT',
    'LEFT_TOE',
}

BONE_GROUP_ARMS = {
    'RIGHT_SHOULDER_DEFORM',
    'RIGHT_ELBOW_DEFORM',
    'LEFT_SHOULDER_DEFORM',
    'LEFT_ELBOW_DEFORM',
    'RIGHT_UPPER_ARM_DEFORM_1',
    'RIGHT_UPPER_ARM_DEFORM_2',
    'RIGHT_UPPER_ARM_DEFORM_3',
    'RIGHT_UPPER_ARM_DEFORM_4',
    'RIGHT_ARM_DEFORM_1',
    'RIGHT_ARM_DEFORM_2',
    'LEFT_UPPER_ARM_DEFORM_1',
    'LEFT_UPPER_ARM_DEFORM_2',
    'LEFT_UPPER_ARM_DEFORM_3',
    'LEFT_UPPER_ARM_DEFORM_4',
    'LEFT_ARM_DEFORM_1',
    'LEFT_ARM_DEFORM_2',
}

BONE_GROUP_LEGS = {
    'RIGHT_BUTT_CHEEK',
    'LEFT_BUTT_CHEEK',
    'RIGHT_KNEE',
    'LEFT_KNEE',
}


BONE_GROUP_HANDS = {
    'RIGHT_THUMB',
    'LEFT_THUMB',
    'RIGHT_UPPER_THUMB',
    'RIGHT_MIDDLE_THUMB',
    'RIGHT_LOWER_THUMB',
    'RIGHT_UPPER_INDEX_FINGER',
    'RIGHT_MIDDLE_INDEX_FINGER',
    'RIGHT_LOWER_INDEX_FINGER',
    'RIGHT_UPPER_MIDDLE_FINGER',
    'RIGHT_MIDDLE_MIDDLE_FINGER',
    'RIGHT_LOWER_MIDDLE_FINGER',
    'RIGHT_PALM',
    'RIGHT_UPPER_RING_FINGER',
    'RIGHT_MIDDLE_RING_FINGER',
    'RIGHT_LOWER_RING_FINGER',
    'RIGHT_UPPER_PINKY_FINGER',
    'RIGHT_MIDDLE_PINKY_FINGER',
    'RIGHT_LOWER_PINKY_FINGER',
    'LEFT_UPPER_THUMB',
    'LEFT_MIDDLE_THUMB',
    'LEFT_LOWER_THUMB',
    'LEFT_UPPER_INDEX_FINGER',
    'LEFT_MIDDLE_INDEX_FINGER',
    'LEFT_LOWER_INDEX_FINGER',
    'LEFT_UPPER_MIDDLE_FINGER',
    'LEFT_MIDDLE_MIDDLE_FINGER',
    'LEFT_LOWER_MIDDLE_FINGER',
    'LEFT_PALM',
    'LEFT_UPPER_RING_FINGER',
    'LEFT_MIDDLE_RING_FINGER',
    'LEFT_LOWER_RING_FINGER',
    'LEFT_UPPER_PINKY_FINGER',
    'LEFT_MIDDLE_PINKY_FINGER',
    'LEFT_LOWER_PINKY_FINGER',
}

BONE_GROUP_FACIAL_BASIC = {
    'RIGHT_EYE',
    'LEFT_EYE',
    'RIGHT_EYELID',
    'LEFT_EYELID',
    'JAW',
}

BONE_GROUP_HAIR = {
    'HAIR_FOREHEAD_LEFT_PARENT',
    'HAIR_FOREHEAD_LEFT',
    'HAIR_FOREHAD_RIGHT_PARENT',
    'HAIR_FOREHAD_RIGHT',
    'HAIR_NAPE_PARENT',
    'HAIR_NAPE',
    'HAIR_BACK_PARENT',
    'HAIR_BACK',
    'HAIR_UP_1_PARENT',
    'HAIR_UP_1',
    'HAIR_UP_2_PARENT',
    'HAIR_UP_2',
    'HAIR_FOREHEAD',
}

BONE_GROUP_FACIAL = {
    'RIGHT_INNER_EYEBROW',
    'RIGHT_OUTER_EYEBROW',
    'LEFT_INNER_EYEBROW',
    'LEFT_OUTER_EYEBROW',
    'RIGHT_LOWER_EYELID',
    'LEFT_LOWER_EYELID',
    'RIGHT_UPPER_CHEEK',
    'LEFT_UPPER_CHEEK',
    'RIGHT_UPPER_OUTER_CHEEK',
    'LEFT_UPPER_OUTER_CHEEK',
    'RIGHT_NOSE',
    'LEFT_NOSE',
    'RIGHT_OUTER_LIP',
    'RIGHT_UPPER_LIP',
    'UPPER_LIP',
    'LEFT_UPPER_LIP',
    'LEFT_OUTER_LIP',
    'LEFT_OUTER_LOWER_LIP',
    'LOWER_LIP',
    'LEFT_LOWER_LIP',
    'RIGHT_LOWER_CHEEK',
    'LEFT_LOWER_CHEEK',
}

BONE_GROUP_ACCESORIES = {
    'RIGHT_BACKPACK_STRIP',
    'LEFT_BACKPACK_STRIP',
    'BACK_ACCESORIES_PARENT',
    'BACK_ACCESORIES',
    'RIGHT_BACK_ACCESORY_1_PARENT',
    'RIGHT_BACK_ACCESORY_1',
    'RIGHT_BACK_ACCESORY_2_PARENT',
    'RIGHT_BACK_ACCESORY_2',
    'BACK_LEFT_KNIFE_PARENT',
    'BACK_LEFT_KNIFE',
    'RIGHT_BACKPACK_STRIP_BACK_1_PARENT',
    'RIGHT_BACKPACK_STRIP_BACK_1',
}

# Iterate over all BONE_GROUP_* sets and create a dict
# with bone_indices as keys and group_name as value
BONE_INDEX_TO_GROUP = {}
for group_name, set_of_strings in dict(vars()).items():
    if not group_name.startswith('BONE_GROUP_'):
        continue
    # verify that groups use a correct enum
    bone_enums = {getattr(Mod156BoneAnimationMapping, field_name) for field_name in set_of_strings}
    # check if more than one group share a bone index
    assert all(bone_enum.value not in BONE_INDEX_TO_GROUP for bone_enum in bone_enums)
    for bone_enum in bone_enums:
        BONE_INDEX_TO_GROUP[bone_enum.value] = group_name
