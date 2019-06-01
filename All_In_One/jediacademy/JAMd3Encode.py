import math, struct

MAX_QPATH         = 64

MD3_IDENT         = "IDP3"
MD3_VERSION       = 15
MD3_MAX_TAGS      = 16
MD3_MAX_SURFACES  = 32
MD3_MAX_FRAMES    = 1024
MD3_MAX_SHADERS   = 256
MD3_MAX_VERTICES  = 4096
MD3_MAX_TRIANGLES = 8192
MD3_XYZ_SCALE     = 64.0

class md3Vert:
    binaryFormat = "<3hH"
    
    def __init__( self ):
        self.xyz    = [ 0.0, 0.0, 0.0 ]
        self.normal = 0
        
    def GetSize( self ):
        return struct.calcsize( self.binaryFormat )
    
    # copied from PhaethonH <phaethon@linux.ucla.edu> md3.py
    def Decode( self, latlng ):
        lat  = ( latlng >> 8 ) & 0xFF;
        lng  = ( latlng ) & 0xFF;
        lat *= math.pi / 128;
        lng *= math.pi / 128;
        x    = math.cos( lat ) * math.sin( lng )
        y    = math.sin( lat ) * math.sin( lng )
        z    =                   math.cos( lng )
        return [ x, y, z ]
    
    # copied from PhaethonH <phaethon@linux.ucla.edu> md3.py
    def Encode( self, normal ):
        x = normal[ 0 ]
        y = normal[ 1 ]
        z = normal[ 2 ]
        # normalize
        l = math.sqrt( ( x * x ) + ( y * y ) + ( z * z ) )
        if l == 0:
            return 0
        x = x/l
        y = y/l
        z = z/l
        
        if ( x == 0.0 ) and ( y == 0.0 ):
            if z > 0.0:
                return 0
            else:
                return (128 << 8)
        
        lng    = math.acos( z ) * 255 / ( 2 * math.pi )
        lat    = math.atan2( y, x ) * 255 / ( 2 * math.pi )
        retval = ( ( int( lat ) & 0xFF) << 8 ) | ( int( lng ) & 0xFF )
        return retval
        
    def Save( self, file ):
        data = struct.pack(
            self.binaryFormat,
            int( self.xyz[0] * MD3_XYZ_SCALE ),
            int( self.xyz[1] * MD3_XYZ_SCALE ),
            int( self.xyz[2] * MD3_XYZ_SCALE ),
            self.normal
            )
        file.write(data)
        
class md3TexCoord:
    binaryFormat = "<2f"

    def __init__( self ):
        self.u = 0.0
        self.v = 0.0
        
    def GetSize( self ):
        return struct.calcsize( self.binaryFormat )

    def Save( self, file ):
        data = struct.pack(
            self.binaryFormat,
            self.u,
            1.0 - self.v
            )
        file.write( data )

class md3Triangle:
    binaryFormat = "<3i"

    def __init__( self ):
        self.indexes = [ 0, 0, 0 ]
        
    def GetSize( self ):
        return struct.calcsize( self.binaryFormat )

    def Save( self, file ):
        data = struct.pack(
            self.binaryFormat, 
            self.indexes[ 0 ],
            self.indexes[ 2 ], # reverse
            self.indexes[ 1 ]
            )
        file.write(data)

class md3Shader:
    binaryFormat = "<%dsi" % MAX_QPATH

    def __init__( self ):
        self.name  = ""
        self.index = 0
        
    def GetSize( self ):
        return struct.calcsize( self.binaryFormat )

    def Save(self, file):
        data         = struct.pack(
            self.binaryFormat,
            self.name.encode( 'utf-8' ),
            self.index
            )
        file.write( data )

class md3Surface:
    binaryFormat = "<4s%ds10i" % MAX_QPATH  # 1 int, name, then 10 ints
    
    def __init__(self):
        self.ident        = ""
        self.name         = ""
        self.flags        = 0
        self.numFrames    = 0
        self.numShaders   = 0
        self.numVerts     = 0
        self.numTriangles = 0
        self.ofsTriangles = 0
        self.ofsShaders   = 0
        self.ofsUV        = 0
        self.ofsVerts     = 0
        self.ofsEnd       = 0
        self.shaders      = []
        self.triangles    = []
        self.uv           = []
        self.verts        = []
        
    def GetSize( self ):
        sz              = struct.calcsize( self.binaryFormat )
        self.ofsShaders = sz
        for s in self.shaders:
            sz += s.GetSize()
        self.ofsTriangles = sz
        for t in self.triangles:
            sz += t.GetSize()
        self.ofsUV = sz
        for u in self.uv:
            sz += u.GetSize()
        self.ofsVerts = sz
        for v in self.verts:
            sz += v.GetSize()
        self.ofsEnd = sz
        return self.ofsEnd
    
    def Save(self, file):
        self.GetSize()
        data = struct.pack(
            self.binaryFormat,
            self.ident.encode( 'utf-8' ),
            self.name.encode( 'utf-8' ),
            self.flags,
            self.numFrames,
            self.numShaders,
            self.numVerts,
            self.numTriangles,
            self.ofsTriangles,
            self.ofsShaders,
            self.ofsUV,
            self.ofsVerts,
            self.ofsEnd
            )
        file.write( data )

        # save the shader coordinates
        for s in self.shaders:
            s.Save( file )

        # write the tri data
        for t in self.triangles:
            t.Save( file )

        # save the uv info
        for u in self.uv:
            u.Save( file )

        # save the verts
        for v in self.verts:
            v.Save( file )

class md3Tag:
    binaryFormat="<%ds3f9f" % MAX_QPATH
    
    def __init__( self ):
        self.name   = ""
        self.origin = [ 0, 0, 0 ]
        self.axis   = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        
    def GetSize( self ):
        return struct.calcsize( self.binaryFormat )
        
    def Save( self, file ):
        data = struct.pack(
            self.binaryFormat,
            self.name.encode('utf-8'),
            float( self.origin[ 0 ] ),
            float( self.origin[ 1 ] ),
            float( self.origin[ 2 ] ),
            float(   self.axis[ 0 ] ),
            float(   self.axis[ 1 ] ),
            float(   self.axis[ 2 ] ),
            float(   self.axis[ 3 ] ),
            float(   self.axis[ 4 ] ),
            float(   self.axis[ 5 ] ),
            float(   self.axis[ 6 ] ),
            float(   self.axis[ 7 ] ),
            float(   self.axis[ 8 ] )
            )
        file.write( data )
    
class md3Frame:
    binaryFormat="<3f3f3ff16s"
    
    def __init__( self ):
        self.mins        = [ 0, 0, 0 ]
        self.maxs        = [ 0, 0, 0 ]
        self.localOrigin = [ 0, 0, 0 ]
        self.radius      = 0.0
        self.name        = ""
        
    def GetSize( self ):
        return struct.calcsize(self.binaryFormat)

    def Save(self, file):
        data = struct.pack(
            self.binaryFormat,
            self.mins[ 0 ],
            self.mins[ 1 ],
            self.mins[ 2 ],
            self.maxs[ 0 ],
            self.maxs[ 1 ],
            self.maxs[ 2 ],
            self.localOrigin[ 0 ],
            self.localOrigin[ 1 ],
            self.localOrigin[ 2 ],
            self.radius,
            self.name.encode('utf-8')
            )
        file.write( data )

class md3Object:

    binaryFormat="<4si%ds9i" % MAX_QPATH  # little-endian (<), 4 bytes, 1 ints, 64 bytes, 9 ints

    def __init__(self):
		# header structure
        self.ident       = 0 # this is used to identify the file (must be IDP3)
        self.version     = 0 # the version number of the file (Must be 15)
        self.name        = ""
        self.flags       = 0
        self.numFrames   = 0
        self.numTags     = 0
        self.numSurfaces = 0
        self.numSkins    = 0
        self.ofsFrames   = 0
        self.ofsTags     = 0
        self.ofsSurfaces = 0
        self.ofsEnd      = 0
        self.frames      = []
        self.tags        = []
        self.surfaces    = []

    def GetSize(self):
        # frames start after header
        self.ofsFrames = struct.calcsize( self.binaryFormat )
        # tags start after frames
        self.ofsTags = self.ofsFrames
        for f in self.frames:
            self.ofsTags += f.GetSize()
        # surfaces start after tags
        self.ofsSurfaces = self.ofsTags
        for t in self.tags:
            self.ofsSurfaces += t.GetSize()
        # end starts after surfaces
        self.ofsEnd = self.ofsSurfaces
        for s in self.surfaces:
            self.ofsEnd += s.GetSize()
        return self.ofsEnd
        
    def Save(self, file):
        self.GetSize()

        data = struct.pack(
            self.binaryFormat,
            self.ident.encode('utf-8'),
            self.version,
            self.name.encode('utf-8'),
            self.flags,
            self.numFrames,
            self.numTags,
            self.numSurfaces,
            # always 0
            self.numSkins,
            # calculated in self.GetSize()
            self.ofsFrames,
            self.ofsTags,
            self.ofsSurfaces,
            self.ofsEnd
            )
        file.write( data )

        for f in self.frames:
            f.Save( file )
            
        for t in self.tags:
            t.Save( file )
            
        for s in self.surfaces:
            s.Save( file )
