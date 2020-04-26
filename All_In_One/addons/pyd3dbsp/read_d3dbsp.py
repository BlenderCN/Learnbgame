import struct
import os
import re

from collections import namedtuple
from enum import Enum

"""
D3DBSPHeader type definition. Used to store file header information.

Fields:
-------
magic   - 4 byte string - file magic (IBSP) 
version - integer       - file version (4)  
-------

"""
D3DBSPHeader = namedtuple('D3DBSPHeader', 'magic, version')
fmt_D3DBSPHeader = '<4si' # D3DBSPHeader format

"""
D3DBSPLump type definition. Used to store lump information.

Fields:
-------
length - unsigned integer - lump length
offset - unsigned integer - lump offset (from the beginning of the file)
-------

"""
D3DBSPLump = namedtuple('D3DBSPLump', 'length, offset')
fmt_D3DBSPLump = '<2I' # D3DBSPLump format

"""
D3DBSPMaterial type definition. Used to store material information.

Fields:
-------
name    - 64 byte string        - material name
flags   - unsigned long long    - material flags
-------

"""
D3DBSPMaterial = namedtuple('D3DBSPMaterial', 'name, flags')
fmt_D3DBSPMaterial = '<64sQ' # D3DBSPMaterial format

"""
D3DBSPTriangle type definition. Used to store triangle information.

Fields:
-------
v1 - unsigned short - first index
v2 - unsigned short - second index
v3 - unsigned short - third index
-------

"""
D3DBSPTriangle = namedtuple('D3DBSPTriangle', 'v1, v2, v3')
fmt_D3DBSPTriangle = '<3H' # D3DBSPTriangle format

"""
D3DBSPTriangleSoup type definition. Used to store trianglesoup information.

Fields:
-------
material_id     - unsigned short    - material id
draw_order      - unsigned short    - draw order
vertex_offset   - unsigned integer  - vertex offset
vertex_length   - unsigned short    - vertex length
triangle_length - unsigned short    - triangle length
triangle_offset - unsigned integer  - triangle offset
-------

"""
D3DBSPTriangleSoup = namedtuple('D3DBSPTriangleSoup', 
    ('material_id, draw_order,'
    'vertex_offset, vertex_length,'
    'triangle_length, triangle_offset')
    )
fmt_D3DBSPTriangleSoup = '<HHIHHI' # D3DBSPTriangleSoup format


"""
D3DBSPVertex type definition. Used to store vertex information.

Fields:
-------
pos_x       - float         - Position X
pos_y       - float         - Position Y
pos_z       - float         - Position Z
norm_x      - float         - Normal X
norm_y      - float         - Normal Y
norm_z      - float         - Normal Z
clr_r       - unsigned char - Color red
clr_g       - unsigned char - Color green
clr_b       - unsigned char - Color blue
clr_a       - unsigned char - Color alpha
uv_u        - float         - UV U
uv_v        - float         - UV V
st_s        - float         - ST S
st_t        - float         - ST T
unknwn_1    - float         - Unknown 1
unknwn_2    - float         - Unknown 2
unknwn_3    - float         - Unknown 3
unknwn_4    - float         - Unknown 4
unknwn_5    - float         - Unknown 5
unknwn_6    - float         - Unknown 6
-------

"""
D3DBSPVertex = namedtuple('D3DBSPVertex',
    ('pos_x, pos_y, pos_z,'
    'norm_x, norm_y, norm_z,'
    'clr_r, clr_g, clr_b, clr_a,'
    'uv_u, uv_v,'
    'st_s, st_t,'
    'unknwn_1, unknwn_2, unknwn_3, unknwn_4, unknwn_5, unknwn_6')
    )
fmt_D3DBSPVertex = '<3f3f4B2f2f6f' # D3DBSPVertex format

class LUMP(Enum):
    """
    LUMP Enum class to store the lumps and their indexes represented in the D3DBSP file.
    """
    
    MATERIALS = 0
    LIGHTMAPS = 1
    LIGHT_GRID_HASH = 2
    LIGHT_GRID_VALUES = 3
    PLANES = 4
    BRUSHSIDES = 5
    BRUSHES = 6
    TRIANGLESOUPS = 7
    VERTICES = 8
    TRIANGLES = 9
    CULL_GROUPS = 10
    CULL_GROUP_INDEXES = 11
    PORTAL_VERTS = 17
    OCCLUDER = 18
    OCCLUDER_PLANES = 19
    OCCLUDER_EDGES = 20
    OCCLUDER_INDEXES = 21
    AABB_TREES = 22
    CELLS = 23
    PORTALS = 24
    NODES = 25
    LEAFS = 26
    LEAF_BRUSHES = 27
    COLLISION_VERTS = 29
    COLLISION_EDGES = 30
    COLLISION_TRIS = 31
    COLLISION_BORDERS = 32
    COLLISION_PARTS = 33
    COLLISION_AABBS = 34
    MODELS = 35
    VISIBILITY = 36
    ENTITIES = 37
    PATHS = 38

class D3DBSP:
    """
    D3DBSP class for reading and storing data of Call of Duty 2 .d3dbsp files.
    """

    def __init__(self):
        """
        Class constructor to initialize the class properties.

        Properties:
        -----------
        header          - D3DBSPHeader  - header information 
        lumps           - list          - list of D3DBSPLump
        materials       - list          - list of D3DBSPMaterial 
        trianglesoups   - list          - list of D3DBSPTriangleSoup
        vertices        - list          - list of D3DBSPVertex
        triangles       - list          - list of D3DBSPTriangle
        entities        - list          - list of dictionaries containing entity info
        -----------

        """

        self.header = None
        self.lumps = []
        self.materials = []
        self.trianglesoups = []
        self.vertices = []
        self.triangles = []
        self.entities = []

    def _read_header(self, file):
        """
        Read header data from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_D3DBSPHeader))
        self.header = D3DBSPHeader._make(struct.unpack(fmt_D3DBSPHeader, header_data))
        # decode header magic to string
        self.header = self.header._replace(magic = self.header.magic.decode('utf-8'))
    
    def _read_lumps(self, file):
        """
        Read lump list from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """
        file.seek(struct.calcsize(fmt_D3DBSPHeader), os.SEEK_SET)
        
        for i in range(39): # there are 39 lumps in the CoD2 .d3dbsp file
            lump_data = file.read(struct.calcsize(fmt_D3DBSPLump))
            lump = D3DBSPLump._make(struct.unpack(fmt_D3DBSPLump, lump_data))
            self.lumps.append(lump)

    def _read_materials(self, file):
        """
        Read materials from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """

        material_lump = self.lumps[LUMP.MATERIALS.value]
        
        file.seek(material_lump.offset, os.SEEK_SET)
        for i in range(0, material_lump.length, struct.calcsize(fmt_D3DBSPMaterial)):
            material_data = file.read(struct.calcsize(fmt_D3DBSPMaterial))
            material = D3DBSPMaterial._make(struct.unpack(fmt_D3DBSPMaterial, material_data))
            # decode material names and remove pad bytes
            material = material._replace(name = material.name.decode('utf-8').rstrip('\x00'))
            self.materials.append(material)

    def _read_trianglesoups(self, file):
        """
        Read trianglesoups from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """

        trianglesoups_lump = self.lumps[LUMP.TRIANGLESOUPS.value]

        file.seek(trianglesoups_lump.offset, os.SEEK_SET)
        for i in range(0, trianglesoups_lump.length, struct.calcsize(fmt_D3DBSPTriangleSoup)):
            trianglesoup_data = file.read(struct.calcsize(fmt_D3DBSPTriangleSoup))
            trianglesoup = D3DBSPTriangleSoup._make(struct.unpack(fmt_D3DBSPTriangleSoup, trianglesoup_data))
            self.trianglesoups.append(trianglesoup)

    def _read_vertices(self, file):
        """
        Read vertices from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """

        vertices_lump = self.lumps[LUMP.VERTICES.value]

        file.seek(vertices_lump.offset, os.SEEK_SET)
        for i in range(0, vertices_lump.length, struct.calcsize(fmt_D3DBSPVertex)):
            vertex_data = file.read(struct.calcsize(fmt_D3DBSPVertex))
            vertex = D3DBSPVertex._make(struct.unpack(fmt_D3DBSPVertex, vertex_data))
            self.vertices.append(vertex)

    def _read_triangles(self, file):
        """
        Read triangles from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------

        """

        triangles_lump = self.lumps[LUMP.TRIANGLES.value]

        file.seek(triangles_lump.offset, os.SEEK_SET)
        for i in range(0, triangles_lump.length, struct.calcsize(fmt_D3DBSPTriangle)):
            triangle_data = file.read(struct.calcsize(fmt_D3DBSPTriangle))
            triangle = D3DBSPTriangle._make(struct.unpack(fmt_D3DBSPTriangle, triangle_data))
            self.triangles.append(triangle)

    def _read_entities(self, file):
        """
        Read entities from file.

        Parameters:
        -----------
        file - file object - File to read from
        -----------
        """

        entities_lump = self.lumps[LUMP.ENTITIES.value]

        file.seek(entities_lump.offset, os.SEEK_SET)
        entity_data = file.read(entities_lump.length)
        # decode the whole entity data into a single string and remove pad bytes
        entity_str = entity_data.decode('utf-8').rstrip('\x00')
        for i in range(0, len(entity_str)):
            entity_substr = ''
            # split up entity string into single entity substrings
            if(entity_str[i] == '{' and entity_str[i+1] == '\n'):
                i += 2
                while(entity_str[i] != '}'):
                    entity_substr += entity_str[i]
                    i += 1
                # make a dictionary out of key value pairs
                entity = dict(re.findall('\"(.*?)\"\s\"(.*?)\"\n', entity_substr))
                # if the value of the key contains x, y, z coordinate values
                # then make a list out of it, so its easier to access those values
                for k, v in entity.items():
                    if(re.match('([-.0-9]+\s[-.0-9]+\s[-.0-9]+)', v)):
                        entity[k] = v.split(' ')
                self.entities.append(entity)

    def load_d3dbsp(self, filepath):
        """
        Load a Call of Duty 2 .d3dbsp file and read all the necessary data from it.

        Parameters:
        -----------
        filepath - string - Path to the file
        -----------

        Returns:
        --------
        Boolean - True/False wether the file reading was successful or not
        --------

        """

        with open(filepath, 'rb') as file:
            self._read_header(file)
            # validate CoD2 .d3dbsp format
            if(self.header.magic == 'IBSP' and self.header.version == 4):
                self._read_lumps(file)
                self._read_materials(file)
                self._read_trianglesoups(file)
                self._read_vertices(file)
                self._read_triangles(file)
                self._read_entities(file)
                return True
            else:
                return False