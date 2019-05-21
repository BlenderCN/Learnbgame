# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Module: mdc_file.py
# Description: read/write .mdc file. Some encoding and decoding functions.

import struct
import math

from .util import Util
from .anormals import ANormal
from .options import ImportOptions, ExportOptions

'''
================================================================================
MDCFrameCompFrame

Description: data type without operations. Stores index into
MDCSurface::frameCompFrames[]. This is used to find where in frameCompFrames the
compressed data can be found for a given frame.
================================================================================
'''

class MDCFrameCompFrame:

    format = '<h'

    def __init__(self, index):

        self.index = index


'''
================================================================================
MDCFrameBaseFrame

Description: data type without operations. Stores index into
MDCSurface::frameBaseFrames[]. This is used to find where in frameBaseFrames the
non-compressed data can be found for a given frame.
================================================================================
'''

class MDCFrameBaseFrame:

    format = '<h'

    def __init__(self, index):

        self.index = index


'''
================================================================================
MDCXyznCompressed

Description: primarily a data type. Provides class operations for encoding and
decoding. Stores compressed vertex location and normal.

For xyz: three bytes of the offset vector are describing location. These
locations are relative to a baseframe. MAX_DIST is the main criteria used to
determine if a frame is compressed or not. Converted to float, no x, y, z value
should exceed a distance of 6.35 relative to its base value coordinates. The
"+/-MAX_OFS" in the decoding and encoding formulas is used to bring an unsigned
byte into a signed number. The "XYZC_SCALE * 0.5" in the encoding is to prevent
a negative effect when integer casting is applied. It sort of brings the float
into a better range of numbers which are mapped to int.

For normal: this is described in detail in "The MDC File Format" by Wolfgang
Prinz. Briefly: there are 15 possible latitude values. Each of these 15
latitudes is assigned a number of longitudes ranging from 4 to 32. For example,
if lat=90, then someone said there are 32 longitude values on this latitude.
The further up or down one goes, then for each latitude the number of longitudes
shrinks by 4 each step until 32 - 7 * 4 = 4 is reached. So near the "poles"
(lat~0 or lat~180), there are only 4 longitude values. The reason for this
uneven distribution of longitudes over the latitudes is that near the poles one
does not need much detail in longitude, as the values there hardly change the
normals overall direction (they would still be pointing mostly north or south).
In total, there are 256 normals encoded into the last byte of the offset vector.
This value can be read as an index into an array with 256 precalculated normals
(see ANormals module).

typedef struct {
	unsigned int ofsVec; // offset direction from the last base frame
} mdcXyzCompressed_t;
================================================================================
'''

MAX_OFS = 127.0
XYZC_SCALE = 1.0 / 20
MAX_DIST = MAX_OFS * XYZC_SCALE # 6,35
MAX_COMPRESSION_DELTA = 0.1

class MDCXyznCompressed:

    format = '<I' # xyzn compressed in 4 bytes

    aNormals = ANormal.buildNormals()

    def __init__(self, ofsVec):

        self.ofsVec = ofsVec


    def decode(ofsVec):

        # xyz delta - byte to float
        delta_x = ((ofsVec & 255) - MAX_OFS) * XYZC_SCALE
        delta_y = (((ofsVec >> 8) & 255) - MAX_OFS) * XYZC_SCALE
        delta_z = (((ofsVec >> 16) & 255) - MAX_OFS) * XYZC_SCALE

        # normal
        normal = MDCXyznCompressed.aNormals[(ofsVec >> 24) & 255]

        return delta_x, delta_y, delta_z, \
               normal[0], normal[1], normal[2]


    def encode(delta, normal):

        ofsVec = 0

        # xyz delta - float to byte
        for i in range(0, 3):
            tmp = int( ( abs( ( delta[i] + XYZC_SCALE * 0.5 ) * ( 1.0 / XYZC_SCALE ) + MAX_OFS ) ) )
            ofsVec = ofsVec + (tmp << i*8)

        if normal != None:

            bestNormal = 0

            # find best z group
            zGroupStart = 0
            bestDiff = 999
            for i in range(0, len(MDCXyznCompressed.aNormals)):

                diff = abs(normal[2] - MDCXyznCompressed.aNormals[i][2])
                if diff < bestDiff:
                    bestDiff = diff
                    zGroupStart = i

            # within z group find best normal
            zGroupVal = MDCXyznCompressed.aNormals[zGroupStart][2]
            bestDiff = -999
            for i in range(zGroupStart, len(MDCXyznCompressed.aNormals)):

                if MDCXyznCompressed.aNormals[i][2] != zGroupVal:
                    break

                diff = normal[0] * MDCXyznCompressed.aNormals[i][0] + \
                       normal[1] * MDCXyznCompressed.aNormals[i][1] + \
                       normal[2] * MDCXyznCompressed.aNormals[i][2]

                if diff > bestDiff:
                    bestDiff = diff
                    bestNormal = i

            ofsVec = ofsVec + (bestNormal << 24)

        return ofsVec


    def canEncode(oldPos, newPos):

        delta_x = newPos[0] - oldPos[0]
        delta_y = newPos[1] - oldPos[1]
        delta_z = newPos[2] - oldPos[2]
        delta = (delta_x, delta_y, delta_z)

        for i in range(0, len(delta)):
            if abs(delta[i]) >= MAX_DIST:
                return False

        ofsVec = MDCXyznCompressed.encode(delta, None)
        cDelta_x, cDelta_y, cDelta_z, \
        delta_normal_x, delta_normal_y, delta_normal_z \
        = MDCXyznCompressed.decode(ofsVec)

        cNewPos_x = oldPos[0] + cDelta_x
        cNewPos_y = oldPos[1] + cDelta_y
        cNewPos_z = oldPos[2] + cDelta_z
        cNewPos = (cNewPos_x, cNewPos_y, cNewPos_z)

        distance = Util.calcDistance(cNewPos, newPos)

        if distance > MAX_COMPRESSION_DELTA:
            return False

        return True


'''
================================================================================
MDCXyzn

Description: primarily a data type. Provides class operations for encoding and
decoding. Stores base vertex location and normal.

For xyz: a linear mapping from all short values to float values is done (see
XYZ_SCALE).

For normal: a latitude ([0, 180]) and longitude ([0 , 360]) value in spherical
coordinates is given. Rotation order is z-unit vector (0, 0, 1) by latitude
around y. Then longitude around z. Note: right-hand rule.

typedef struct {
	short xyz[3];
	short normal;
} md3XyzNormal_t;
================================================================================
'''

XYZ_SCALE = 1.0 / 64

class MDCXyzn:

    format = '<hhhH'
    maxVerts = 4096

    shortMin = -2**15
    shortMax = 2**15 - 1

    floatMin = shortMin * XYZ_SCALE
    floatMax = shortMax * XYZ_SCALE

    def __init__(self, xyz1, xyz2, xyz3, normal):

        self.xyz = (xyz1, xyz2, xyz3)
        self.normal = normal


    def decode(xyz1, xyz2, xyz3, normal):

        # xyz - short to float
        x = xyz1 * XYZ_SCALE
        y = xyz2 * XYZ_SCALE
        z = xyz3 * XYZ_SCALE

        # normal:
        # short to byte
        lon = normal & 255
        lat = (normal >> 8) & 255

        # byte range to float range
        lon = lon * (360 / 255)
        lat = lat * (360 / 255)

        # degree to radians
        lon = math.radians(lon)
        lat = math.radians(lat)

        # lat, lon to dir
        nx = math.cos(lat) *  math.sin(lon)
        ny = math.sin(lat) *  math.sin(lon)
        nz = math.cos(lon)

        return x, y, z, nx, ny, nz


    def encode(x, y, z, nx, ny, nz):

        # xyz - float to short
        xyz1 = int(x / XYZ_SCALE)
        xyz2 = int(y / XYZ_SCALE)
        xyz3 = int(z / XYZ_SCALE)

        # normal:
        # dir to lat, lon
        lat = 0
        lon = 0

        if nx == 0 and ny == 0:

            if nz > 0:
                lat = 0
                lon = 0
            else:
                lon = 128
                lat = 0

        lat = int(math.atan2(ny, nx) * 255 / (2 * math.pi))
        lon = int(math.acos(nz) * 255 / (2 * math.pi))

        # bytes to short
        normal = lon & 255
        normal += ((lat & 255) << 8)

        return xyz1, xyz2, xyz3, normal


'''
================================================================================
MDCSt

Description: data type without operations. Stores uv-map for a vertex.

typedef struct {
	float st[2];
} md3St_t;
================================================================================
'''

class MDCSt:

    format = '<ff'

    def __init__(self, st1, st2):

        self.st = (st1, st2)


'''
================================================================================
MDCShader

Description: data type without operations. Stores path to a skin, shader or
texture file. Path is relative to game directory.

typedef struct {
	char name[MAX_QPATH];
	int shaderIndex;                // for in-game use
} md3Shader_t;
================================================================================
'''

class MDCShader:

    format = '<64si'
    nameLen = 64
    maxShaders = 256

    def __init__(self, name):

        self.name = name
        self.shaderIndex = 0


'''
================================================================================
MDCTriangle

Description: data type without operations. Stores triangles. Indexes point to
the list of vertices.

typedef struct {
	int indexes[3];
} md3Triangle_t;
================================================================================
'''

class MDCTriangle:

    format = '<iii'
    maxTriangles = 8192

    def __init__(self, index1, index2, index3):

        self.indexes = (index1, index2, index3)


'''
================================================================================
MDCSurfaceHeader

Description: data type without operations. Stores surface header.

typedef struct {
	int ident;                  //

	char name[MAX_QPATH];       // polyset name

	int flags;
	int numCompFrames;          // all surfaces in a model should have the same
	int numBaseFrames;          // ditto

	int numShaders;             // all surfaces in a model should have the same
	int numVerts;

	int numTriangles;
	int ofsTriangles;

	int ofsShaders;             // offset from start of md3Surface_t
	int ofsSt;                  // texture coords are common for all frames
	int ofsXyzNormals;          // numVerts * numBaseFrames
	int ofsXyzCompressed;       // numVerts * numCompFrames

	int ofsFrameBaseFrames;     // numFrames
	int ofsFrameCompFrames;     // numFrames

	int ofsEnd;                 // next surface follows
} mdcSurface_t;
================================================================================
'''

class MDCSurfaceHeader:

    format = '<4s64siiiiiiiiiiiiii'
    ident = b'\x07\x00\x00\x00'
    nameLen = 64

    def __init__(self, ident, name, flags, numCompFrames, numBaseFrames, \
                 numShaders, numVerts, numTriangles, \
                 ofsTriangles, ofsShaders, ofsSt, ofsXyzns, ofsXyznCompressed, \
                 ofsFrameBaseFrames, ofsFrameCompFrames, ofsEnd):

        self.ident = ident
        self.name = name
        self.flags = flags
        self.numCompFrames = numCompFrames
        self.numBaseFrames = numBaseFrames
        self.numShaders = numShaders
        self.numVerts = numVerts
        self.numTriangles = numTriangles
        self.ofsTriangles = ofsTriangles
        self.ofsShaders = ofsShaders
        self.ofsSt = ofsSt
        self.ofsXyzns = ofsXyzns
        self.ofsXyznCompressed = ofsXyznCompressed
        self.ofsFrameBaseFrames = ofsFrameBaseFrames
        self.ofsFrameCompFrames = ofsFrameCompFrames
        self.ofsEnd = ofsEnd


'''
================================================================================
MDCSurface

Description: holds references to all surface data.

read(file, ofsSurface): constructs an MDCSurface object.
================================================================================
'''

class MDCSurface:

    maxSurfaces = 32

    def __init__(self):

        self.header = {}            # MDCSurfaceHeader
        self.triangles = []         # MDCTriangle (numTriangles)
        self.shaders = []           # MDCShader (numShaders)
        self.st = []                # MDCSt (numVerts)
        self.xyzns = []             # MDCXyzn (numBaseFrames)
        self.xyznCompressed = []    # MDCXyznCompressed (numCompFrames)
        self.frameBaseFrames = []   # MDCFrameBaseFrame (numFrames)
        self.frameCompFrames = []   # MDCFrameCompFrame (numFrames)


    def read(file, ofsSurface):

        surface = MDCSurface()

        # header
        file.seek(ofsSurface)

        format = MDCSurfaceHeader.format
        formatSize = struct.calcsize(format)

        ident, name, flags, numCompFrames, numBaseFrames, numShaders, \
        numVerts, numTriangles, ofsTriangles, ofsShaders, ofsSt, \
        ofsXyzns, ofsXyznCompressed, ofsFrameBaseFrames, ofsFrameCompFrames, \
        ofsEnd \
        = struct.unpack(format, file.read(formatSize))

        surface.header = MDCSurfaceHeader(ident, name, flags, numCompFrames, \
                             numBaseFrames, numShaders, numVerts, \
                             numTriangles, ofsTriangles, ofsShaders, ofsSt, \
                             ofsXyzns, ofsXyznCompressed, ofsFrameBaseFrames, \
                             ofsFrameCompFrames, ofsEnd)

        # triangles
        file.seek(ofsSurface + surface.header.ofsTriangles)

        format = MDCTriangle.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numTriangles):

            index1, index2, index3 \
            = struct.unpack(format, file.read(formatSize))

            surface.triangles.append(MDCTriangle(index1, index2, index3))

        # shaders
        file.seek(ofsSurface + surface.header.ofsShaders)

        format = MDCShader.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numShaders):

            name, shaderIndex = struct.unpack(format, file.read(formatSize))

            surface.shaders.append(MDCShader(name))

        # st
        file.seek(ofsSurface + surface.header.ofsSt)

        format = MDCSt.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numVerts):

            st1, st2 = struct.unpack(format, file.read(formatSize))

            surface.st.append(MDCSt(st1, st2))

        # xyzns
        file.seek(ofsSurface + surface.header.ofsXyzns)

        format = MDCXyzn.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numBaseFrames):

            baseFrameVerts = []

            for j in range(0, surface.header.numVerts):

                xyz1, xyz2, xyz3, normal \
                = struct.unpack(format, file.read(formatSize))

                baseFrameVerts.append(MDCXyzn(xyz1, xyz2, xyz3, normal))

            surface.xyzns.append(baseFrameVerts)

        # xyznCompressed
        file.seek(ofsSurface + surface.header.ofsXyznCompressed)

        format = MDCXyznCompressed.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numCompFrames):

            compFrameVerts = []

            for j in range(0, surface.header.numVerts):

                ofsVec = struct.unpack(format, file.read(formatSize))

                compFrameVerts.append(MDCXyznCompressed(ofsVec[0]))

            surface.xyznCompressed.append(compFrameVerts)

        # frameBaseFrames
        file.seek(ofsSurface + surface.header.ofsFrameBaseFrames)

        format = MDCFrameBaseFrame.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numBaseFrames + surface.header.numCompFrames):

            index = struct.unpack(format, file.read(formatSize))

            surface.frameBaseFrames.append(MDCFrameBaseFrame(index[0]))

        # frameCompFrames
        file.seek(ofsSurface + surface.header.ofsFrameCompFrames)

        format = MDCFrameCompFrame.format
        formatSize = struct.calcsize(format)

        for i in range(0, surface.header.numBaseFrames + surface.header.numCompFrames):

            index = struct.unpack(format, file.read(formatSize))

            surface.frameCompFrames.append(MDCFrameCompFrame(index[0]))

        return surface


    def write(self, file, ofsSurface):

        # header
        file.seek(ofsSurface)

        file.write(struct.pack(MDCSurfaceHeader.format, \
                               self.header.ident, \
                               self.header.name, \
                               self.header.flags, \
                               self.header.numCompFrames, \
                               self.header.numBaseFrames, \
                               self.header.numShaders, \
                               self.header.numVerts, \
                               self.header.numTriangles, \
                               self.header.ofsTriangles, \
                               self.header.ofsShaders, \
                               self.header.ofsSt, \
                               self.header.ofsXyzns, \
                               self.header.ofsXyznCompressed, \
                               self.header.ofsFrameBaseFrames, \
                               self.header.ofsFrameCompFrames, \
                               self.header.ofsEnd))

        # triangles
        file.seek(ofsSurface + self.header.ofsTriangles)

        for i in range(0, self.header.numTriangles):

            file.write(struct.pack(MDCTriangle.format, \
                                   self.triangles[i].indexes[0], \
                                   self.triangles[i].indexes[1], \
                                   self.triangles[i].indexes[2]))

        # shaders
        file.seek(ofsSurface + self.header.ofsShaders)

        for i in range(0, self.header.numShaders):

            file.write(struct.pack(MDCShader.format, \
                       self.shaders[i].name, \
                       self.shaders[i].shaderIndex))

        # st
        file.seek(ofsSurface + self.header.ofsSt)

        for i in range(0, self.header.numVerts):

            file.write(struct.pack(MDCSt.format, self.st[i].st[0], \
                                                 self.st[i].st[1]))

        # xyzns
        file.seek(ofsSurface + self.header.ofsXyzns)

        for i in range(0, self.header.numBaseFrames):

            for j in range(0, self.header.numVerts):

                file.write(struct.pack(MDCXyzn.format, \
                           self.xyzns[i][j].xyz[0], \
                           self.xyzns[i][j].xyz[1], \
                           self.xyzns[i][j].xyz[2], \
                           self.xyzns[i][j].normal))

        # xyzCompressed
        file.seek(ofsSurface + self.header.ofsXyznCompressed)

        for i in range(0, self.header.numCompFrames):

            for j in range(0, self.header.numVerts):

                file.write(struct.pack(MDCXyznCompressed.format, \
                           self.xyznCompressed[i][j].ofsVec))

        # frameBaseFrames
        file.seek(ofsSurface + self.header.ofsFrameBaseFrames)

        for i in range(0, self.header.numBaseFrames + self.header.numCompFrames):

            file.write(struct.pack(MDCFrameBaseFrame.format, \
                       self.frameBaseFrames[i].index))

        # frameCompFrames
        file.seek(ofsSurface + self.header.ofsFrameCompFrames)

        for i in range(0, self.header.numBaseFrames + self.header.numCompFrames):

            file.write(struct.pack(MDCFrameCompFrame.format, \
                       self.frameCompFrames[i].index))


'''
================================================================================
MDCTag

Description: tags describe a location (xyz) and orientation (angles) in model
space. They are used by other models for attachment. When such a model attaches
itself to this tag, its origin gets aligned with the tags location and
orientation. Attachment is done via external scripts or hardcoded into source
code.

Tags can be animated. They exist once per frame. Tagnames are stored seperately
to save space (see MDCTagname).

typedef struct {
	short xyz[3];
	short angles[3];
} mdcTag_t;
================================================================================
'''

TAG_ANGLE_SCALE = 360.0 / 32700.0

class MDCTag:

    format = '<hhhhhh'
    maxTags = 16

    def __init__(self, x, y, z, anglesX, anglesY, anglesZ):

        self.xyz = (x, y, z)
        self.angles = (anglesX, anglesY, anglesZ)

    def decode(x, y, z, anglesX, anglesY, anglesZ):

        # xyz
        x = x * XYZ_SCALE
        y = y * XYZ_SCALE
        z = z * XYZ_SCALE

        # angles
        yaw = math.radians(anglesY * TAG_ANGLE_SCALE)
        pitch = math.radians(anglesX * TAG_ANGLE_SCALE)
        roll = math.radians(anglesZ * TAG_ANGLE_SCALE)

        return x, y, z, yaw, pitch, roll

    def encode(x, y, z, yaw, pitch, roll):

        # xyz
        x = int( x / XYZ_SCALE )
        y = int( y / XYZ_SCALE )
        z = int( z / XYZ_SCALE )

        # angles
        anglesY = int( math.degrees(yaw / TAG_ANGLE_SCALE) )
        anglesX = int( math.degrees(pitch / TAG_ANGLE_SCALE) )
        anglesZ = int( math.degrees(roll / TAG_ANGLE_SCALE) )

        return x, y, z, anglesX, anglesY, anglesZ


'''
================================================================================
MDCTagname

Description: data type without operations. Stores tagnames. Tagnames are
related to tags (see MDCTag), but are stored seperately and only once.

typedef struct {
	char name[MAX_QPATH]; // tag name
} mdcTagName_t;
================================================================================
'''

class MDCTagname:

    format = '<64s'
    nameLen = 64

    def __init__(self, name):

        self.name = name


'''
================================================================================
MDCFrame

Description: data type without operations. Stores frame info.

typedef struct md3Frame_s {
	vec3_t bounds[2];
	vec3_t localOrigin;
	float radius;
	char name[16];
} md3Frame_t;
================================================================================
'''

class MDCFrame:

    format = '<ffffffffff16s'
    nameLen = 16
    maxFrames = 1024

    def __init__(self, minBoundX, minBoundY, minBoundZ, \
                 maxBoundX, maxBoundY, maxBoundZ, \
                 localOriginX, localOriginY, localOriginZ, \
                 radius, \
                 name):

        self.minBound = (minBoundX, minBoundY, minBoundZ)
        self.maxBound = (maxBoundX, maxBoundY, maxBoundZ)

        self.localOrigin = (localOriginX, localOriginY, localOriginZ)

        self.radius = radius

        self.name = name


'''
================================================================================
MDCFileHeader

Description: data type without operations. Stores file header.

typedef struct {
	int ident;
	int version;

	char name[MAX_QPATH];           // model name

	int flags;

	int numFrames;
	int numTags;
	int numSurfaces;

	int numSkins;

	int ofsFrames;   // offset for first frame, stores the bounds and localOrigin
	int ofsTagNames; // numTags
	int ofsTags;     // numFrames * numTags
	int ofsSurfaces; // first surface, others follow

	int ofsEnd;      // end of file
} mdcHeader_t;
================================================================================
'''

class MDCFileHeader:

    format = '<4si64siiiiiiiiii'
    ident = b'IDPC'
    version = 2
    nameLen = 64

    def __init__(self, ident, version, name, flags, numFrames, numTags, \
                 numSurfaces, numSkins, ofsFrames, ofsTagNames, ofsTags, \
                 ofsSurfaces, ofsEnd):

        self.ident = ident
        self.version = version
        self.name = name
        self.flags = flags

        self.numFrames = numFrames
        self.numTags = numTags
        self.numSurfaces = numSurfaces
        self.numSkins = numSkins

        self.ofsFrames = ofsFrames
        self.ofsTagNames = ofsTagNames
        self.ofsTags = ofsTags
        self.ofsSurfaces = ofsSurfaces
        self.ofsEnd = ofsEnd


'''
================================================================================
MDCFile

Description: holds references to all file data. File data is read 'as-is' and
is left untouched. Interface to other modules.

read(mdcFilepath): reads an mdc file and constructs an MDCFile object from it.

write(self, mdcFilepath): writes MDCFile object data to file.
================================================================================
'''

class MDCFile:

    def __init__(self):

        self.header = {}        # MDCFileHeader
        self.frames = []        # MDCFrame (numFrames)
        self.tagNames = []      # MDCTagName (numTags)
        self.tags = []          # MDCTag (numFrames * numTags)
        self.surfaces = []      # MDCSurface (numSurfaces)


    def read(importOptions):
        with open(importOptions.mdcFilepath, 'rb') as file:

            mdcFile = MDCFile()

            # header
            file.seek(0)

            format = MDCFileHeader.format
            formatSize = struct.calcsize(format)

            ident, version, name, flags, numFrames, numTags, numSurfaces, \
            numSkins, ofsFrames, ofsTagNames, ofsTags, ofsSurfaces, ofsEnd \
            = struct.unpack(format, file.read(formatSize))

            mdcFile.header = MDCFileHeader(ident, version, name, flags, \
                                           numFrames, numTags, numSurfaces, \
                                           numSkins, ofsFrames, ofsTagNames, \
                                           ofsTags, ofsSurfaces, ofsEnd)

            # frames
            file.seek(mdcFile.header.ofsFrames)

            format = MDCFrame.format
            formatSize = struct.calcsize(format)

            for i in range(0, mdcFile.header.numFrames):

                minBoundX, minBoundY, minBoundZ, \
                maxBoundX, maxBoundY, maxBoundZ, \
                localOriginX, localOriginY, localOriginZ, \
                radius, \
                name \
                = struct.unpack(format, file.read(formatSize))

                frame = MDCFrame(minBoundX, minBoundY, minBoundZ, \
                                 maxBoundX, maxBoundY, maxBoundZ, \
                                 localOriginX, localOriginY, localOriginZ, \
                                 radius, \
                                 name)
                mdcFile.frames.append(frame)

            # tagNames
            file.seek(mdcFile.header.ofsTagNames)

            format = MDCTagname.format
            formatSize = struct.calcsize(format)

            for i in range(0, mdcFile.header.numTags):
                name = struct.unpack(format, file.read(formatSize))
                mdcFile.tagNames.append(MDCTagname(name[0]))

            # tags
            file.seek(mdcFile.header.ofsTags)

            format = MDCTag.format
            formatSize = struct.calcsize(format)

            for i in range(0, mdcFile.header.numFrames):

                frameTags = []

                for j in range(0, mdcFile.header.numTags):

                    x, y, z, anglesX, anglesY, anglesZ \
                    = struct.unpack(format, file.read(formatSize))

                    tag = MDCTag(x, y, z, anglesX, anglesY, anglesZ)
                    frameTags.append(tag)

                mdcFile.tags.append(frameTags)

            # surfaces
            ofsSurface = mdcFile.header.ofsSurfaces

            for i in range(0, mdcFile.header.numSurfaces):

                surface = MDCSurface.read(file, ofsSurface)

                mdcFile.surfaces.append(surface)

                ofsSurface = ofsSurface + surface.header.ofsEnd

            return mdcFile


    def write(self, exportOptions):
        with open(exportOptions.mdcFilepath, 'wb') as file:

            # header
            file.seek(0)

            file.write(struct.pack(MDCFileHeader.format, \
                                   self.header.ident, \
                                   self.header.version, \
                                   self.header.name, \
                                   self.header.flags, \

                                   self.header.numFrames, \
                                   self.header.numTags, \
                                   self.header.numSurfaces, \
                                   self.header.numSkins, \

                                   self.header.ofsFrames, \
                                   self.header.ofsTagNames, \
                                   self.header.ofsTags, \
                                   self.header.ofsSurfaces, \
                                   self.header.ofsEnd))

            # frames
            file.seek(self.header.ofsFrames)

            for i in range(0, self.header.numFrames):

                file.write(struct.pack(MDCFrame.format, \
                                       self.frames[i].minBound[0], \
                                       self.frames[i].minBound[1], \
                                       self.frames[i].minBound[2], \

                                       self.frames[i].maxBound[0], \
                                       self.frames[i].maxBound[1], \
                                       self.frames[i].maxBound[2], \

                                       self.frames[i].localOrigin[0], \
                                       self.frames[i].localOrigin[1], \
                                       self.frames[i].localOrigin[2], \

                                       self.frames[i].radius, \

                                       self.frames[i].name))

            # tagNames
            file.seek(self.header.ofsTagNames)

            for i in range(0, self.header.numTags):

                file.write(struct.pack(MDCTagname.format, \
                                       self.tagNames[i].name))

            # tags
            file.seek(self.header.ofsTags)

            for i in range(0, self.header.numFrames):

                for j in range(0, self.header.numTags):

                    file.write(struct.pack(MDCTag.format, \
                                           self.tags[i][j].xyz[0], \
                                           self.tags[i][j].xyz[1], \
                                           self.tags[i][j].xyz[2], \

                                           self.tags[i][j].angles[0], \
                                           self.tags[i][j].angles[1], \
                                           self.tags[i][j].angles[2]))

            # surfaces
            ofsSurface = self.header.ofsSurfaces

            for i in range(0, self.header.numSurfaces):

                self.surfaces[i].write(file, ofsSurface)

                ofsSurface = ofsSurface + self.surfaces[i].header.ofsEnd
