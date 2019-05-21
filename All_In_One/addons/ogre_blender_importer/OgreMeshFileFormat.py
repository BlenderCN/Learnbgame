from enum import IntEnum;

class OgreMeshChunkID(IntEnum):
    """
    Definition of the OGRE .mesh file format

    .mesh files are binary files (for read efficiency at runtime) and are arranged into chunks
    of data, very like 3D Studio's format.
    A chunk always consists of:
        unsigned short CHUNK_ID        : one of the following chunk ids identifying the chunk
        unsigned long  LENGTH          : length of the chunk in bytes, including this header
        void*          DATA            : the data, which may contain other sub-chunks (various data types)

    A .mesh file can contain both the definition of the Mesh itself, and optionally the definitions
    of the materials is uses (although these can be omitted, if so the Mesh assumes that at runtime the
    Materials referred to by name in the Mesh are loaded/created from another source)

    A .mesh file only contains a single mesh, which can itself have multiple submeshes.
    """

    M_HEADER = 0x1000;
    M_MESH = 0x3000;
    M_SUBMESH = 0x4000;
    M_SUBMESH_OPERATION = 0x4010;
    M_SUBMESH_BONE_ASSIGNMENT = 0x4100;
    M_SUBMESH_TEXTURE_ALIAS = 0x4200;
    M_GEOMETRY = 0x5000;
    M_GEOMETRY_VERTEX_DECLARATION = 0x5100;
    M_GEOMETRY_VERTEX_ELEMENT = 0x5110;
    M_GEOMETRY_VERTEX_BUFFER = 0x5200;
    M_GEOMETRY_VERTEX_BUFFER_DATA = 0x5210;
    M_MESH_SKELETON_LINK = 0x6000;
    M_MESH_BONE_ASSIGNMENT = 0x7000;
    M_MESH_LOD_LEVEL = 0x8000;
    M_MESH_LOD_USAGE = 0x8100;
    M_MESH_LOD_MANUAL = 0x8110;
    M_MESH_LOD_GENERATED = 0x8120;
    M_MESH_BOUNDS = 0x9000;
    M_SUBMESH_NAME_TABLE = 0xA000;
    M_SUBMESH_NAME_TABLE_ELEMENT = 0xA100;
    M_EDGE_LISTS = 0xB000;
    M_EDGE_LIST_LOD = 0xB100;
    M_EDGE_GROUP = 0xB110;
    M_POSES = 0xC000;
    M_POSE = 0xC100;
    M_POSE_VERTEX = 0xC111;
    M_ANIMATIONS = 0xD000;
    M_ANIMATION = 0xD100;
    M_ANIMATION_BASEINFO = 0xD105;
    M_ANIMATION_TRACK = 0xD110;
    M_ANIMATION_MORPH_KEYFRAME = 0xD111;
    M_ANIMATION_POSE_KEYFRAME = 0xD112;
    M_ANIMATION_POSE_REF = 0xD113;
    M_TABLE_EXTREMES = 0xE000;
    M_GEOMETRY_NORMALS = 0x5100;
    M_GEOMETRY_COLOURS = 0x5200;
    M_GEOMETRY_TEXCOORDS = 0x5300;
