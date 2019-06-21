
class Chunks:
    class File:
        BODY = 0x7777

    class Object:
        VERSION = 0x0900
        FLAGS = 0x0903
        MATERIALS = 0x0907
        MESHES = 0x0910
        USER_DATA = 0x0912
        MOTIONS = 0x0916
        ACTOR_TRANSFORM = 0x0920
        BONES = 0x0921
        AUTHORS = 0x0922
        BONE_PARTITIONS = 0x0923
        MOTION_REFERENCE = 0x0924
        LOD_REFERENCE = 0x0925

    class Mesh:
        VERSION = 0x1000
        MESH_NAME = 0x1001
        FLAGS = 0x1002
        BOUNDING_BOX = 0x1004
        VERTICES = 0x1005
        TRIANGLES = 0x1006
        VMAP_REFERENCES = 0x1008
        MATERIALS = 0x1009
        OPTIONS = 0x1010
        UV_MAPS = 0x1012
        SMOOTH_GROUPS = 0x1013

    class Bone:
        VERSION = 0x0001
        DEF = 0x0002
        BIND_POSE = 0x0003
        MATERIAL = 0x0004
        SHAPE = 0x0005
        IK_JOINT = 0x0006
        MASS_PARAMS = 0x0007
        IK_FLAGS = 0x0008
        BREAK_PARAMS = 0x0009
        FRICTION = 0x0010


CURRENT_OBJECT_VERSION = 0x0010
CURRENT_MESH_VERSION = 0x0011
CURRENT_BONE_VERSION = 0x0002
CURRENT_MOTION_VERSION = 0x0006
OBJECT_TYPES = {
    0x00: 'STATIC',
    0x01: 'DYNAMIC',
    0x03: 'PROGRESSIVE_DYNAMIC',
    0x08: 'HOM',
    0x14: 'MULTIPLE_USAGE',
    0x20: 'SOUND_OCCLUDER'
    }
