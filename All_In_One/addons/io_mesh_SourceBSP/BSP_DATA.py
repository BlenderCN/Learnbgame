# struct dheader_t
# {
# 	int	ident;                // BSP file identifier
# 	int	version;              // BSP file version
# 	lump_t	lumps[HEADER_LUMPS];  // lump directory array
# 	int	mapRevision;          // the map's revision (iteration, version) number
# };
import io
import struct
from enum import IntEnum
from typing import List
from pprint import pformat

from math import sqrt

import cstruct

HEADER_LUMPS    = 64
SURF_LIGHT      = 0x1            #value will hold the light strength
SURF_SKY2D      = 0x2            #don't draw, indicates we should skylight + draw 2d sky but not draw the 3D skybox
SURF_SKY        = 0x4              #don't draw, but add to skybox
SURF_WARP       = 0x8             #turbulent water warp
SURF_TRANS      = 0x10           #texture is translucent
SURF_NOPORTAL   = 0x20        #the surface can not have a portal placed on it
SURF_TRIGGER    = 0x40         #FIXME: This is an xbox hack to work around elimination of trigger surfaces, which breaks occluders
SURF_NODRAW     = 0x80          #don't bother referencing the texture
SURF_HINT       = 0x100           #make a primary bsp splitter
SURF_SKIP       = 0x200           #completely ignore, allowing non-closed brushes
SURF_NOLIGHT    = 0x400        #Don't calculate light
SURF_BUMPLIGHT  = 0x800      #calculate three lightmaps for the surface for bumpmapping
SURF_NOSHADOWS  = 0x1000     #Don't receive shadows
SURF_NODECALS   = 0x2000      #Don't receive decals
SURF_NOCHOP     = 0x4000        #Don't subdivide patches on this surface
SURF_HITBOX     = 0x8000        #surface is part of a hitbox
class LUMP_ENUM(IntEnum):
    LUMP_ENTITIES =                         0
    LUMP_PLANES =                           1
    LUMP_TEXDATA =                          2
    LUMP_VERTEXES =                         3
    LUMP_VISIBILITY =                       4
    LUMP_NODES =                            5
    LUMP_TEXINFO =                          6
    LUMP_FACES =                            7
    LUMP_LIGHTING =                         8
    LUMP_OCCLUSION =                        9
    LUMP_LEAFS =                            10
    LUMP_FACEIDS =                          11
    LUMP_EDGES =                            12
    LUMP_SURFEDGES =                        13
    LUMP_MODELS =                           14
    LUMP_WORLDLIGHTS =                      15
    LUMP_LEAFFACES =                        16
    LUMP_LEAFBRUSHES =                      17
    LUMP_BRUSHES =                          18
    LUMP_BRUSHSIDES =                       19
    LUMP_AREAS =                            20
    LUMP_AREAPORTALS =                      21
    LUMP_PROPCOLLISION =                    22
    LUMP_PROPHULLS =                        23
    LUMP_PROPHULLVERTS =                    24
    LUMP_PROPTRIS =                         25
    LUMP_DISPINFO =                         26
    LUMP_ORIGINALFACES =                    27
    LUMP_PHYSDISP =                         28
    LUMP_PHYSCOLLIDE =                      29
    LUMP_VERTNORMALS =                      30
    LUMP_VERTNORMALINDICES =                31
    LUMP_DISP_LIGHTMAP_ALPHAS =             32
    LUMP_DISP_VERTS =                       33
    LUMP_DISP_LIGHTMAP_SAMPLE_POSITIONS =   34
    LUMP_GAME_LUMP =                        35
    LUMP_LEAFWATERDATA =                    36
    LUMP_TEXDATA_STRING_DATA =              43
    LUMP_TEXDATA_STRING_TABLE =             44
class dheader_t:
    def __init__(self):
        self.ident = ''
        self.version = 0
        self.lump_t = []  # type: List[lump_t]
        self.mapRevision = 0
        self.LUMPS = []

    def __str__(self):
        return self.__dict__

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)


# struct lump_t
# {
# 	int	fileofs;	// offset into file (bytes)
# 	int	filelen;	// length of lump (bytes)
# 	int	version;	// lump format version
# 	char	fourCC[4];	// lump ident code
# };

class lump_t:
    def __init__(self):
        self.fileofs = 0
        self.filelen = 0
        self.version = 0
        self.fourCC = []  # type: List[str]*4

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)


# struct dplane_t
# {
# 	Vector	normal;	// normal vector
# 	float	dist;	// distance from origin
# 	int	type;	// plane axis identifier
# };


class dplane_t:
    size = 20

    def __init__(self):
        self.normal = Vector()
        self.dist = 0.0
        self.type = 0

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)


#
# struct Vector
# {
#     float x;
#     float y;
#     float z;
# };
class Vector:
    size = 12

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def __str__(self):
        
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def gen(self,data):
        self.x = round(struct.unpack('f',data.read(4))[0],15)
        self.y = round(struct.unpack('f',data.read(4))[0],15)
        self.z = round(struct.unpack('f',data.read(4))[0],15)
        return self
    @property
    def asList(self):
        return [self.x,self.y,self.z]
# struct dedge_t
# {
# 	unsigned short	v[2];	// vertex indices
# };
class dedge_t:
    size = 4

    def __init__(self):
        self.v = []  # type: List[int]

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)


class Surfedge:
    size = 4

    def __init__(self):
        self.surfedge = 0

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)


class dface_t(cstruct.CStruct):

    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        unsigned short	    planenum;		
        unsigned char		side;			
        unsigned char		onNode;			
        int		            firstedge;		
        short		        numedges;		
        short		        texinfo;	
        short		        dispinfo;		
        short		        surfaceFogVolumeID;
        unsigned char		styles[4];		
        int		            lightofs;		
        float	            area;		
        int		            LightmapTextureMinsInLuxels[2];	
        int		            LightmapTextureSizeInLuxels[2];
        int		            origFace;		
        unsigned short	    numPrims;		
        unsigned short	    firstPrimID;
        unsigned int	    smoothingGroups;"""
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class dbrush_t(cstruct.CStruct):

    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = """
        int	firstside;
        int	numsides;
        int	contents;"""
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class dbrushside_t(cstruct.CStruct):

    __struct__ = """
        unsigned short	planenum;
        short		    texinfo;
        short		    dispinfo;
        short		    bevel;	"""
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class dnode_t(cstruct.CStruct):

    __struct__ = """
        int		        planenum;	
        int		        children[2];
        short		    mins[3];	
        short		    maxs[3];
        unsigned short	firstface;	
        unsigned short	numfaces;	
        short		    area;		
        short		    paddding;"""

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class dleaf_t(cstruct.CStruct):

    __struct__ = """
    int				    contents;
    short			    cluster;
    short	            area:9;	
    short	            flags:7;
    short			    mins[3];
    short			    maxs[3];
    unsigned short		firstleafface;
    unsigned short		numleaffaces;
    unsigned short		firstleafbrush;
    unsigned short		numleafbrushes;
    short			    leafWaterDataID;    """
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class dleafface_t(cstruct.CStruct):

    __struct__ = """unsigned short leafface;"""
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class dleafbrush_t(cstruct.CStruct):

    __struct__ = """unsigned short leafbrush;"""
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class textureVec:
    """struct texinfo_t
{
    float	textureVecs[2][4];	// [s/t][xyz offset]
    float	lightmapVecs[2][4];	// [s/t][xyz offset] - length is in units of texels/area
    int	flags;			// miptex flags	overrides
    int	texdata;		// Pointer to texture name, size, etc.
}"""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.offset = 0
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
    @staticmethod
    def readtextureVec(data):
        tVec = textureVec()
        tVec.x = struct.unpack('f',data.read(struct.calcsize('f')))[0]
        tVec.y = struct.unpack('f',data.read(struct.calcsize('f')))[0]
        tVec.z = struct.unpack('f',data.read(struct.calcsize('f')))[0]
        tVec.offset = struct.unpack('f',data.read(struct.calcsize('f')))[0]
        return tVec
class texinfo_t:
    size = 72
    __struct__ = """
        float	textureVecs[2][4];	
        float	lightmapVecs[2][4];	
        int	    flags;
        int	    texdata;"""
    def __init__(self):
        self.textureVecs = [] #type: List[textureVec]
        self.lightmapVecs = [] #type: List[textureVec]
        self.flags = 0
        self.texdata = 0
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class CVector(cstruct.CStruct):

    __struct__ = """
    float x;
    float y;
    float z;"""
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class dtexdata_t(cstruct.CStruct):

    __struct__ = """
    struct CVector	reflectivity;		
    int	    nameStringTableID;	
    int	    width;
    int     height;		
    int	    view_width;
    int     view_height;"""

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class TexdataStringData(cstruct.CStruct):
    __struct__ = """
    int TexdataStringData;"""

class dmodel_t(cstruct.CStruct):
    __struct__ = """
    struct CVector	mins;
    struct CVector maxs;     
    struct CVector	origin;
    int	headnode;
    int	firstface;
    int numfaces;"""





class ddispinfo_t:

    size = 176
    def __init__(self):
        self.startPosition = Vector()
        self.DispVertStart = 0
        self.DispTriStart = 0
        self.power = 0
        self.minTess = 0
        self.smoothingAngle = .0
        self.contents = 0
        self.MapFace = 0
        self.LightmapAlphaStart = 0
        self.LightmapSamplePositionStart = 0
        self.CDispNeighbor = [] #type: List[CDispNeighbor]
        self.DisplaceCornerNeighbors = [] #type: List[DisplaceCornerNeighbors]
        self.AllowedVerts = [] #type: List[int]
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
    @property
    def getPowerSize(self):
        return 1 << self.power
    @property
    def VertexCount(self):
        return (self.getPowerSize + 1) * (self.getPowerSize + 1)

    @property
    def TriangleTagCount(self):
        return 2 * self.power * self.power

class CDispVert:
    size = 20
    # {
    # public:
    # 	DECLARE_BYTESWAP_DATADESC();
    # 	Vector		m_vVector;		// Vector field defining displacement volume.
    # 	float		m_flDist;		// Displacement distances.
    # 	float		m_flAlpha;		// "per vertex" alpha values.
    # };
    def __init__(self):
        self.m_vVector = Vector()
        self.m_flDist = 0.0
        self.m_flAlpha = 0.0

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class CDispSubNeighbor:
    size = 5
    # struct CDispSubNeighbor
    # {
    # public:
    # 	DECLARE_BYTESWAP_DATADESC();
    # 	unsigned short		GetNeighborIndex() const		{ return m_iNeighbor; }
    # 	NeighborSpan		GetSpan() const					{ return (NeighborSpan)m_Span; }
    # 	NeighborSpan		GetNeighborSpan() const			{ return (NeighborSpan)m_NeighborSpan; }
    # 	NeighborOrientation	GetNeighborOrientation() const	{ return (NeighborOrientation)m_NeighborOrientation; }
    #
    # 	bool				IsValid() const				{ return m_iNeighbor != 0xFFFF; }
    # 	void				SetInvalid()				{ m_iNeighbor = 0xFFFF; }
    #
    #
    # public:
    # 	unsigned short		m_iNeighbor;		// This indexes into ddispinfos.
    # 											// 0xFFFF if there is no neighbor here.
    #
    # 	unsigned char		m_NeighborOrientation;		// (CCW) rotation of the neighbor wrt this displacement.
    #
    # 	// These use the NeighborSpan type.
    # 	unsigned char		m_Span;						// Where the neighbor fits onto this side of our displacement.
    # 	unsigned char		m_NeighborSpan;				// Where we fit onto our neighbor.
    # };
    def __init__(self):
        self.iNeighbor = 0
        self.NeighborOrientation = 0
        self.Span = 0
        self.NeighborSpan = 0

    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class CDispNeighbor:
    def __init__(self):
        self.m_SubNeighbors = []  # type: List[CDispSubNeighbor]
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class DisplaceCornerNeighbors:
    def __init__(self):
        self.neighbor_indices = [None]*4  # type: List[int]
        self.neighbor_count = 0
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class VertNormal:
    size = 12
    def __init__(self):
        self.x , self.y , self.z = 0,0,0
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)
class VertNormal_indexes:
    size = 2
    def __init__(self):
        self.indexes = [] #type: List[VertNormal]
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class dgamelumpheader_t:
    # struct dgamelumpheader_t
    # {
    # 	int lumpCount;	// number of game lumps
    # 	dgamelump_t gamelump[lumpCount];
    # };
    def __init__(self):
        self.lumpCount = 0
        self.gamelump = [] #type: List[dgamelump_t]
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class dgamelump_t:
    # struct dgamelump_t
    # {
    # 	int		id;		// gamelump ID
    # 	unsigned short	flags;		// flags
    # 	unsigned short	version;	// gamelump version
    # 	int		fileofs;	// offset to this gamelump
    # 	int		filelen;	// length
    # };
    def __init__(self):
        self.id = 0
        self.flags = 0
        self.version = 0
        self.fileofs = 0
        self.filelen = 0
        self.PropDict = StaticPropDictLump_t
        self.PropLeaf = StaticPropLeafLump_t
        self.PropData = []
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)


class StaticPropDictLump_t:
    # struct StaticPropDictLump_t
    # {
    # 	int	dictEntries;
    # 	char	name[dictEntries];	// model name
    # };
    def __init__(self):
        self.dictEntries = 0
        self.name = []
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class StaticPropLeafLump_t:
    # struct StaticPropLeafLump_t
    # {
    # 	int leafEntries;
    # 	unsigned short	leaf[leafEntries];
    # };
    def __init__(self):
        self.leafEntries = 0
        self.leaf = []


class color32:
    def __init__(self):
        self.r,self.g,self.b,self.a = 1, 1, 1, 1
    @staticmethod
    def fromArray(rgba:tuple):
        color = color32()
        if len(rgba) >= 4:
            color.r, color.g, color.b, color.a = rgba
        color.r, color.g, color.b = rgba
        return color
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def gen(self,data):
        self.r = struct.unpack('f',data.read(4))[0]
        self.g = struct.unpack('f',data.read(4))[0]
        self.b = struct.unpack('f',data.read(4))[0]
        return self

    def magnitude(self):
        magn = sqrt(self.r**2+self.g**2+self.b**2)
        return magn


    def normalize(self):
        magn = self.magnitude()
        if magn==0:
            return self
        self.r = self.r/magn
        self.g = self.g/magn
        self.b = self.b/magn
        return self

    @property
    def toArrayRGBA(self):
        return self.r,self.g,self.b,self.a

    @property
    def toArrayRGB(self):
        return self.r,self.g,self.b

class StaticPropLump_t:
    # struct StaticPropLump_t
    # {
    # 	// v4
    # 	Vector		Origin;		 // origin
    # 	QAngle		Angles;		 // orientation (pitch roll yaw)
    # 	unsigned short	PropType;	 // index into model name dictionary
    # 	unsigned short	FirstLeaf;	 // index into leaf array
    # 	unsigned short	LeafCount;
    # 	unsigned char	Solid;		 // solidity type
    # 	unsigned char	Flags;
    # 	int		Skin;		 // model skin numbers
    # 	float		FadeMinDist;
    # 	float		FadeMaxDist;
    # 	Vector		LightingOrigin;  // for lighting
    # 	// since v5
    # 	float		ForcedFadeScale; // fade distance scale
    # 	// v6 and v7 only
    # 	unsigned short  MinDXLevel;      // minimum DirectX version to be visible
    # 	unsigned short  MaxDXLevel;      // maximum DirectX version to be visible
    #         // since v8
    # 	unsigned char   MinCPULevel;
    # 	unsigned char   MaxCPULevel;
    # 	unsigned char   MinGPULevel;
    # 	unsigned char   MaxGPULevel;
    #         // since v7
    #         color32         DiffuseModulation; // per instance color and alpha modulation
    #         // since v10
    #         float           unknown;
    #         // since v9
    #         bool            DisableX360;     // if true, don't show on XBox 360
    # };
    def __init__(self):
        self.Origin = Vector()
        self.Angles = Vector()
        self.PropType = 0
        self.FirstLeaf = 0
        self.LeafCount = 0
        self.Solid = 0
        self.Flags = 0
        self.Skin = 0
        self.FadeMinDist = 0
        self.FadeMaxDist = 0
        self.LightingOrigin = Vector()
        self.ForcedFadeScale = 0
        self.MinDXLevel = 0
        self.MaxDXLevel = 0
        self.MinCPULevel = 0
        self.MaxCPULevel = 0
        self.MinGPULevel = 0
        self.MaxGPULevel = 0
        self.DiffuseModulation = color32
        self.unknown = 0
        self.DisableX360 = 0
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

class emittype_t(IntEnum):

    emit_surface = 0	        # 90 degree spotlight
    emit_point = 1              # simple point light source
    emit_spotlight = 2	        # spotlight with penumbra
    emit_skylight = 3	        # directional light with no falloff (surface must trace to SKY texture)
    emit_quakelight = 4	        # linear falloff, non-lambertian
    emit_skyambient = 5	        # spherical light source with no falloff (surface must trace to SKY texture)

class dworldlight_t:
    # struct dworldlight_t
    # {
    # 	DECLARE_BYTESWAP_DATADESC();
    # 	Vector		origin;
    # 	Vector		intensity;
    # 	Vector		normal;			// for surfaces and spotlights
    # 	int			cluster;
    # 	emittype_t	type;
    #   int			style;
    # 	float		stopdot;		// start of penumbra for emit_spotlight
    # 	float		stopdot2;		// end of penumbra for emit_spotlight
    # 	float		exponent;		//
    # 	float		radius;			// cutoff distance
    # 	// falloff for emit_spotlight + emit_point:
    # 	// 1 / (constant_attn + linear_attn * dist + quadratic_attn * dist^2)
    # 	float		constant_attn;
    # 	float		linear_attn;
    # 	float		quadratic_attn;
    # 	int			flags;			// Uses a combination of the DWL_FLAGS_ defines.
    # 	int			texinfo;		//
    # 	int			owner;			// entity that this light it relative to
    # };
    def __init__(self):
        self.origin = Vector()
        self.intensity = color32()
        self.normal = Vector()
        self.cluster = 0
        self.type = []
        self.style = 0
        self.stopdot = 0.0
        self.stopdot2 = 0.0
        self.exponent = 0.0
        self.radius = 0.0
        self.constant_attn = 0.0
        self.linear_attn = 0.0
        self.quadratic_attn = 0.0
        self.flags = 0
        self.texinfo = 0
        self.owner = 0
    def __str__(self):
        return pformat(self.__dict__,width = 250,depth = 8)

    def __repr__(self):
        return pformat(self.__dict__,width = 250,depth = 8)