WEIGHTS3_BONES4 = 1
WEIGHTS7_BONES8 = 2
WEIGHTS0_BONES0 = 3
WEIGHT_MULTIPLIER = 1.0/1023
WEIGHT_MULTIPLIER2 = 1.0/255.0
BIT_LENGTH_10 = 0x3ff

x64 = 64

MIN_BONE_LENGTH = 0.0001
MESH_PART_SIZE = 80
MESH_PART_VERTEX_COUNT_REL_OFFSET = 0x02
MESH_PART_FACE_COUNT_REL_OFFSET = 0x20
FMT_BONE = "Bone.%04d"
FMT_VERTEX_BUFFER = "mod3.MODVertexBuffer%08x"
CLONE_SUFFIX = ".clone"
CLONE_SUFFIX_FMT ="%04d" + CLONE_SUFFIX

MAIN_ARMATURE = "MainArmature"
AMATRICES_ARMATURE = "AmatriceArmature"
EMBED_MODE_NONE = "embed_none"
EMBED_MODE_REFERENCE = "embed_reference"
EMBED_MODE_DATA = "embed_data"

LAYER_MODE_NONE = "layer_none"
LAYER_MODE_PARTS = "layer_parts"
LAYER_MODE_LOD = "layer_lod"

ENUM_EMBED_MODE_NONE = (EMBED_MODE_NONE,'None', 'do not embed anything at all.')
ENUM_EMBED_MODE_REFERENCE = (EMBED_MODE_REFERENCE,'Reference original data.','Instead of embedding all data just add the path to the file. This is faster than embed data, but you need to make shure the file never gets deleted,changed or moved.')
ENUM_EMBED_MODE_DATA = (EMBED_MODE_DATA,'Embed original data.','Use this if you share the .blend file with others.')

ENUM_LAYER_MODE_NONE = (LAYER_MODE_NONE,'None', '')
ENUM_LAYER_MODE_PARTS = (LAYER_MODE_PARTS,'mesh parts','Try to move mesh parts evenly accross the layers')
ENUM_LAYER_MODE_LOD = (LAYER_MODE_LOD,'lod-level','Try group mesh parts based on their lod-level evenly accross the layers')