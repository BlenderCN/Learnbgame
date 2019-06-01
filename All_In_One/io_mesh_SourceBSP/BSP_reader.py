import os
import re
import struct
import sys
def getpath() -> str:
    """

    Returns:
        str: path to current file
    """
    return os.path.dirname(os.path.abspath(__file__))
sys.path.append(getpath())
sys.path.append('E:\\PYTHON\\BSP_reader')
from  pprint import pprint
from BSP_DATA import *
from LIBS import KeyValue_parser
import zipfile
class BSPreader:

    def parseGameInfo(self,path_to_GI):
        # print('path_to_GI',path_to_GI)
        if 'gameinfo.txt' not in path_to_GI:
            path_to_GI = os.path.join(path_to_GI,'gameinfo.txt')
        gameinfo = open(path_to_GI,'r').read()
        commendstripper = re.compile(r'Game[ \t]+(?P<path>[\w+|.]+)')
        gameinfo = commendstripper.findall(gameinfo)
        return gameinfo


    def readASCII(self,len_):
        return ''.join([self.readACSIIChar() for _ in range(len_)])

    def readByte(self):
        type_ = 'b'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readBytes(self,len_):
        type_ = 'b'
        return [struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0] for _ in range(len_)]

    def readUByte(self):
        type_ = 'B'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readInt32(self):
        type_ = 'i'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readUInt32(self):
        type_ = 'I'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readInt16(self):
        type_ = 'h'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readUInt16(self):
        type_ = 'H'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readFloat(self):
        type_ = 'f'
        return struct.unpack(type_,self.data.read(struct.calcsize(type_)))[0]

    def readACSIIChar(self):
        a = self.readUByte()
        return chr(a)

    def readNullString(self,len_):
        string = self.readASCII(len_)

        return string.split('\0', 1)[0]


    def __init__(self,fileUrl,gameInfo_path = None):
        if gameInfo_path !=None:
            self.gameInfo_path = gameInfo_path if 'gameinfo.txt' in gameInfo_path else gameInfo_path.replace('gameinfo.txt','')
            self.gameInfo = self.parseGameInfo(gameInfo_path)
        else:
            self.gameInfo_path = None
            self.gameInfo = None
        self.data = open(fileUrl,'rb')
        self.BSP = self.readHeader()

        self.readPlanes()
        self.readVertexs()
        self.readEdges()
        self.readSurfedges()
        self.readFaces()
        self.readOrigFaces()
        self.readBrushes()
        self.readBrusheSides()
        self.readNodes()
        self.readLeafs()
        self.readLeaffaces()
        self.readLeafbrush()
        self.readTexinfo()
        self.TexdataStringTable()
        self.readTexdata()
        self.readTexdataStringData()
        self.readModel()
        self.readEntities()
        self.readPak()
        self.readVertNormals()
        self.readVertNormalsIndexes()
        self.readDispinfo()
        self.readDispVert()
        self.readdgamelumpheader_t()
        self.readStatic_props()
        self.readWorldLights()
        # for vertex in self.BSP.LUMPS[3]:
        #     print(vertex)
        if __name__ == '__main__':
            pass
            # pprint(['Entities',self.BSP.LUMPS[0]])
            # pprint(['PLANES',self.BSP.LUMPS[LUMP_ENUM.LUMP_PLANES]])
            # pprint(['Texdatas',self.BSP.LUMPS[LUMP_ENUM.LUMP_TEXDATA]])
            # pprint(['VERTEXES',self.BSP.LUMPS[LUMP_ENUM.LUMP_VERTEXES]])
            # pprint(['Nodes',self.BSP.LUMPS[LUMP_ENUM.LUMP_NODES]])
            # pprint(['Texinfo',self.BSP.LUMPS[LUMP_ENUM.LUMP_TEXINFO]])
            # pprint(['FACE',self.BSP.LUMPS[LUMP_ENUM.LUMP_FACES]])
            # pprint(['EDGES',self.BSP.LUMPS[LUMP_ENUM.LUMP_EDGES]])
            for face in self.BSP.LUMPS[LUMP_ENUM.LUMP_FACES]:  # type: dface_t
                if face.dispinfo !=-1:
                    print(face)
                    D = self.BSP.LUMPS[LUMP_ENUM.LUMP_DISPINFO][face.dispinfo]  # type: ddispinfo_t
                    pprint(D)
                    print('VERT NUM', D.VertexCount)
            # pprint(['Surfedge',self.BSP.LUMPS[LUMP_ENUM.LUMP_SURFEDGES]])
            # pprint(['Models',self.BSP.LUMPS[LUMP_ENUM.LUMP_MODELS]])
            # pprint(['Leaffaces',self.BSP.LUMPS[LUMP_ENUM.LUMP_LEAFFACES]])
            # pprint(['LEAFBRUSHES',self.BSP.LUMPS[LUMP_ENUM.LUMP_LEAFBRUSHES]])
            # pprint(['Brushes',self.BSP.LUMPS[LUMP_ENUM.LUMP_BRUSHES]])
            # pprint(['BrusheSides',self.BSP.LUMPS[LUMP_ENUM.LUMP_BRUSHSIDES]])
            # print('Dispinfo')
            # pprint(self.BSP.LUMPS[LUMP_ENUM.LUMP_DISPINFO])
            print('DispVert')
            pprint(self.BSP.LUMPS[LUMP_ENUM.LUMP_DISP_VERTS])
            # pprint(['VERTNORMALS',self.BSP.LUMPS[LUMP_ENUM.LUMP_VERTNORMALS]])
            # pprint(['VERTNORMALINDICES',self.BSP.LUMPS[LUMP_ENUM.LUMP_VERTNORMALINDICES]])
            # pprint(['TexdataStringTable',self.BSP.LUMPS[43]])
            # pprint(['TexdataStringData',self.BSP.LUMPS[44]])
            # pprint([LUMP_ENUM.LUMP_GAME_LUMP,self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP]])
            # pprint([LUMP_ENUM.LUMP_WORLDLIGHTS])
            # pprint([self.BSP.LUMPS[LUMP_ENUM.LUMP_WORLDLIGHTS]])
            # print(len(self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP].gamelump[0].PropDict.name),len(self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP].gamelump[0].PropData))
            # for gamelump in self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP].gamelump:  # type: dgamelump_t
            #     print('gamelump.version',gamelump.version)
            #     for PropData in gamelump.PropData:  # type: StaticPropLump_t
            #         sys.stderr.write(str(PropData.PropType)+' '+str(len(gamelump.PropDict.name))+'\n')
            #         try:
            #             print(gamelump.PropDict.name[PropData.PropType])
            #         except:
            #             sys.stderr.write(str(PropData.__dict__))
            #         pprint(PropData.__dict__)
            # for model in self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP].gamelump[0].PropDict.name:
            #
            #     a = self.getStaticPropsFile(model)
            #     print(a)
            # for tex in self.BSP.LUMPS[LUMP_ENUM.LUMP_TEXDATA_STRING_DATA]:
            #
            #     a = self.getTextureFile(tex)
            #     print(a)
    def readHeader(self):
        header = dheader_t()
        header.ident = self.readASCII(4)
        header.version = self.readInt32()
        for num in range(HEADER_LUMPS):
            header.lump_t.append(self.readLump_t())
        header.mapRevision = self.readInt32()
        header.LUMPS = [None]*64
        return header
    def readLump_t(self):
        lump = lump_t()
        lump.fileofs = self.readInt32()
        lump.filelen = self.readInt32()
        lump.version = self.readInt32()
        lump.fourCC = self.readBytes(4)
        return lump

    def readPlanes(self):
        PLANES = []
        lump_data = self.BSP.lump_t[1]
        self.data.seek(lump_data.fileofs,0)
        for _ in range(lump_data.filelen//dplane_t.size):
            plane = dplane_t()
            plane.normal.x = self.readFloat()
            plane.normal.y = self.readFloat()
            plane.normal.z = self.readFloat()
            plane.dist = self.readFloat()
            plane.type = self.readInt32()
            PLANES.append(plane)
        self.BSP.LUMPS[1] = PLANES

    def readVertexs(self):
        VERTEXES = []
        vertex_data = self.BSP.lump_t[3]
        self.data.seek(vertex_data.fileofs)
        for _ in range(vertex_data.filelen//Vector.size):
            vertex = Vector()
            vertex.x = self.readFloat()
            vertex.y = self.readFloat()
            vertex.z = self.readFloat()
            VERTEXES.append(vertex)
        self.BSP.LUMPS[3] = VERTEXES

    def readEdges(self):
        EDGES = []
        edge_data = self.BSP.lump_t[12]
        self.data.seek(edge_data.fileofs,0)
        for _ in range(edge_data.filelen//dedge_t.size):
            edge = dedge_t()
            edge.v = [self.readUInt16(),self.readUInt16()]
            EDGES.append(edge)
        self.BSP.LUMPS[12] = EDGES
    def readSurfedges(self):
        SEDGES = []
        sedge_data = self.BSP.lump_t[13]
        self.data.seek(sedge_data.fileofs)
        for _ in range(sedge_data.filelen//Surfedge.size):
            sedge = Surfedge()
            sedge.surfedge = self.readInt32()
            SEDGES.append(sedge)
        self.BSP.LUMPS[13] = SEDGES

    def readFaces(self):
        FACES = []
        face_data = self.BSP.lump_t[27]
        self.data.seek(face_data.fileofs)
        for _ in range(face_data.filelen//dface_t.size):
            face = dface_t()
            face.unpack(self.data.read(face.size))
            FACES.append(face)
        self.BSP.LUMPS[27] = FACES

    def readOrigFaces(self):
        FACES = []
        face_data = self.BSP.lump_t[7]
        self.data.seek(face_data.fileofs)
        for _ in range(face_data.filelen//dface_t.size):
            face = dface_t()
            face.unpack(self.data.read(face.size))
            FACES.append(face)
        self.BSP.LUMPS[7] = FACES

    def readBrushes(self):
        BRUSHES = []
        brush_data = self.BSP.lump_t[18]
        self.data.seek(brush_data.fileofs)
        for _ in range(brush_data.filelen//dbrush_t.size):
            brush = dbrush_t()
            brush.unpack(self.data.read(brush.size))
            BRUSHES.append(brush)
        self.BSP.LUMPS[18] = BRUSHES
    def readBrusheSides(self):
        BRUSHESIDE = []
        brushside_data = self.BSP.lump_t[19]
        self.data.seek(brushside_data.fileofs)
        for _ in range(brushside_data.filelen//dbrush_t.size):
            brushside = dbrushside_t()
            brushside.unpack(self.data.read(brushside.size))
            BRUSHESIDE.append(brushside)
        self.BSP.LUMPS[19] = BRUSHESIDE
    def readNodes(self):
        NODES = []
        node_data = self.BSP.lump_t[5]
        self.data.seek(node_data.fileofs)
        for _ in range(node_data.filelen//dnode_t.size):
            node = dnode_t()
            node.unpack(self.data.read(node.size))
            NODES.append(node)
        self.BSP.LUMPS[5] = NODES
    def readLeafs(self):
        LEAFS = []
        leaf_data = self.BSP.lump_t[10]
        self.data.seek(leaf_data.fileofs)
        for _ in range(leaf_data.filelen//dleaf_t.size):
            leaf = dleaf_t()
            leaf.unpack(self.data.read(leaf.size))
            LEAFS.append(leaf)
        self.BSP.LUMPS[10] = LEAFS

    def readLeaffaces(self):
        LEAFFACE = []
        leafface_data = self.BSP.lump_t[16]
        self.data.seek(leafface_data.fileofs)
        for _ in range(leafface_data.filelen // dleafface_t.size):
            leafface = dleafface_t()
            leafface.unpack(self.data.read(leafface.size))
            LEAFFACE.append(leafface)
        self.BSP.LUMPS[16] = LEAFFACE
    def readLeafbrush(self):
        LEAFBRUSH = []
        leafbrush_data = self.BSP.lump_t[17]
        self.data.seek(leafbrush_data.fileofs)
        for _ in range(leafbrush_data.filelen // dleafbrush_t.size):
            leafbrush = dleafbrush_t()
            leafbrush.unpack(self.data.read(leafbrush.size))
            LEAFBRUSH.append(leafbrush)
        self.BSP.LUMPS[17] = LEAFBRUSH
    def readTexinfo(self):
        ARRAY = []
        data = self.BSP.lump_t[6]
        self.data.seek(data.fileofs,0)
        for _ in range(data.filelen // texinfo_t.size):
            struct_data = texinfo_t()
            struct_data.textureVecs = [textureVec.readtextureVec(self.data),textureVec.readtextureVec(self.data)]
            struct_data.lightmapVecs = [textureVec.readtextureVec(self.data),textureVec.readtextureVec(self.data)]
            struct_data.flags = self.readInt32()
            struct_data.texdata = self.readInt32()
            ARRAY.append(struct_data)
        self.BSP.LUMPS[6] = ARRAY
    def readTexdata(self):
        ARRAY = []
        data = self.BSP.lump_t[2]
        self.data.seek(data.fileofs,0)
        for _ in range(data.filelen // dtexdata_t.size):
            struct_data = dtexdata_t()
            struct_data.unpack(self.data.read(struct_data.size))
            struct_data.__dict__['name'] = self.BSP.LUMPS[43][struct_data.nameStringTableID]
            ARRAY.append(struct_data)
        self.BSP.LUMPS[2] = ARRAY

    def readTexdataStringData(self):
        ARRAY = []
        data = self.BSP.lump_t[44]
        self.data.seek(data.fileofs)

        for _ in range(data.filelen // TexdataStringData.size):
            struct_data = TexdataStringData()
            struct_data.unpack(self.data.read(struct_data.size))
            ARRAY.append(struct_data)
        self.BSP.LUMPS[44] = ARRAY

    def TexdataStringTable(self):
        data = self.BSP.lump_t[43]
        self.data.seek(data.fileofs)
        strings = self.data.read(data.filelen).decode().split('\x00')
        self.BSP.LUMPS[43] = strings
    def readModel(self):
        ARRAY = []
        type_ = dmodel_t
        data = self.BSP.lump_t[14]
        self.data.seek(data.fileofs)

        for _ in range(data.filelen // type_.size):
            struct_data = type_()
            struct_data.unpack(self.data.read(struct_data.size))

            ARRAY.append(struct_data)
        self.BSP.LUMPS[14] = ARRAY

    def readEntities(self):
        data = self.BSP.lump_t[0]
        self.data.seek(data.fileofs,0)
        st = self.data.read(data.filelen-1).decode()
        string = io.StringIO(st)

        kv = KeyValue_parser.KeyValues(string)

        self.BSP.LUMPS[0] = kv.dump()

    def readDispinfo(self):
        ARRAY = []
        type_ = ddispinfo_t
        data = self.BSP.lump_t[26]
        self.data.seek(data.fileofs)

        for _ in range(data.filelen // type_.size):
            struct_data = type_()
            struct_data.startPosition.gen(self.data)
            struct_data.DispVertStart = self.readInt32()
            struct_data.DispTriStart = self.readInt32()
            struct_data.power = self.readInt32()
            struct_data.minTess = self.readInt32()
            struct_data.smoothingAngle = self.readFloat()
            struct_data.contents = self.readInt32()
            struct_data.MapFace = self.readUInt16()
            struct_data.LightmapAlphaStart = self.readInt32()
            struct_data.LightmapSamplePositionStart = self.readInt32()
            # struct_data.CDispNeighbor = self.readBytes(90)
            struct_data.CornerNeighbors = []
            start = self.data.tell()
            for _ in range(4):
                cdn = CDispNeighbor()
                neib = []
                for _ in range(2):
                    b = CDispSubNeighbor()
                    b.iNeighbor = self.readUInt16()
                    b.NeighborOrientation = self.readByte()
                    b.Span = self.readByte()
                    self.readByte()
                    b.NeighborSpan = self.readByte()
                    neib.append(b)
                cdn.m_SubNeighbors =neib
                struct_data.CornerNeighbors.append(cdn)
            for _ in range(4):
                cdn2 = DisplaceCornerNeighbors()
                cdn2.neighbor_indices = [self.readUInt16() for _ in range(4)]
                cdn2.neighbor_count = self.readUByte()
                struct_data.CornerNeighbors.append(cdn2)

            self.readBytes(6)
            struct_data.AllowedVerts = [self.readUInt32() for _ in range(10)]


            ARRAY.append(struct_data)
        self.BSP.LUMPS[26] = ARRAY

    def readDispVert(self):
        ar = []
        data = self.BSP.lump_t[LUMP_ENUM.LUMP_DISP_VERTS]
        self.data.seek(data.fileofs)
        for _ in range(data.filelen//CDispVert.size):
            vert = CDispVert()
            vert.m_vVector.gen(self.data)
            vert.m_flDist = self.readFloat()
            vert.m_flAlpha = self.readFloat()
            ar.append(vert)
        self.BSP.LUMPS[LUMP_ENUM.LUMP_DISP_VERTS] = ar
    def readPak(self):

        data = self.BSP.lump_t[40]
        self.data.seek(data.fileofs)
        self.PAK = zipfile.ZipFile(io.BytesIO(self.data.read(data.filelen)),'r')
        self.data.seek(data.fileofs)
        if __name__ == '__main__':
            with open('test.zip','wb') as zp:
                zp.write(self.data.read(data.filelen))

    def readVertNormals(self):
        ARRAY = []
        type_ = VertNormal
        data = self.BSP.lump_t[30]
        self.data.seek(data.fileofs)

        for _ in range(data.filelen // type_.size):
            struct_data = type_()
            struct_data.x = self.readFloat()
            struct_data.y = self.readFloat()
            struct_data.z = self.readFloat()

            ARRAY.append(struct_data)
        self.BSP.LUMPS[30] = ARRAY
    def readVertNormalsIndexes(self):
        type_ = VertNormal_indexes
        data = self.BSP.lump_t[31]
        self.data.seek(data.fileofs)
        struct_data = type_()

        for _ in range(data.filelen // type_.size):
            struct_data.indexes.append(self.readInt16())

        self.BSP.LUMPS[31] = struct_data

    def readWorldLights(self):
        data = self.BSP.lump_t[LUMP_ENUM.LUMP_WORLDLIGHTS]
        print(data)
        ar = []
        self.data.seek(data.fileofs)
        for i in range(data.filelen//100):
            start = self.data.tell()
            worldlight = dworldlight_t()
            worldlight.origin.gen(self.data)
            worldlight.intensity.gen(self.data)
            worldlight.normal.gen(self.data)
            worldlight.cluster = self.readInt32()
            self.readInt32()
            self.readInt32()
            self.readInt32()
            worldlight.type = self.readInt32()
            worldlight.style = self.readInt32()
            worldlight.stopdot = self.readFloat()
            worldlight.stopdot2 = self.readFloat()
            worldlight.exponent = self.readFloat()
            worldlight.radius = self.readFloat()
            worldlight.constant_attn = self.readFloat()
            worldlight.linear_attn = self.readFloat()
            worldlight.quadratic_attn = self.readFloat()
            worldlight.flags = self.readInt32()
            worldlight.texinfo = self.readInt32()
            worldlight.owner = self.readInt32()
            ar.append(worldlight)
            # pprint(worldlight.__dict__)
        self.BSP.LUMPS[LUMP_ENUM.LUMP_WORLDLIGHTS] = ar




    def readdgamelumpheader_t(self):
        data = self.BSP.lump_t[LUMP_ENUM.LUMP_GAME_LUMP]

        self.data.seek(data.fileofs)
        gamelumpheader = dgamelumpheader_t()
        gamelumpheader.lumpCount = self.readInt32()

        for n in range(gamelumpheader.lumpCount): #type: dgamelump_t
            gameLump = dgamelump_t()
            gameLump.id = self.readInt32()
            gameLump.flags = self.readUInt16()
            gameLump.version = self.readUInt16()
            gameLump.fileofs = self.readInt32()
            gameLump.filelen = self.readInt32()
            gamelumpheader.gamelump.append(gameLump)
        self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP] = gamelumpheader

    def readStatic_props(self):
        data = self.BSP.LUMPS[LUMP_ENUM.LUMP_GAME_LUMP].gamelump
        for gameL in data: #type: dgamelump_t
            if gameL.id == 1936749168:
                self.data.seek(gameL.fileofs)
                StaticPropDict = StaticPropDictLump_t()
                StaticPropDict.dictEntries = self.readInt32()
                for i in range(StaticPropDict.dictEntries):
                    StaticPropDict.name.append(self.readNullString(128))
                gameL.PropDict = StaticPropDict
                StaticPropLeaf = StaticPropLeafLump_t()
                StaticPropLeaf.leafEntries = self.readInt32()
                for i in range(StaticPropLeaf.leafEntries):
                    StaticPropLeaf.leaf.append(self.readInt16())
                gameL.PropLeaf = StaticPropLeaf
                PropNumber = self.readInt32()
                for i in range(PropNumber):
                    gameL.PropData.append(self.readStaticProp(gameL))
    def readStaticProp(self,GameLump:dgamelump_t):
        StaticProp = StaticPropLump_t()
        if GameLump.version>=4:
            StaticProp.Origin.gen(self.data)
            StaticProp.Angles.gen(self.data)
            StaticProp.PropType = self.readUInt16()
            StaticProp.FirstLeaf = self.readUInt16()
            StaticProp.LeafCount = self.readUInt16()
            StaticProp.Solid = self.readUByte()
            StaticProp.Flags = self.readUByte()
            StaticProp.Skin = self.readInt32()
            StaticProp.FadeMinDist = self.readFloat()
            StaticProp.FadeMaxDist = self.readFloat()
            StaticProp.LightingOrigin.gen(self.data)
        if GameLump.version>=5:
            StaticProp.FadeMaxDist = self.readFloat()
        if GameLump.version == 6 or GameLump.version == 7:
            StaticProp.MinDXLevel = self.readUInt16()
            StaticProp.MaxDXLevel = self.readUInt16()
        if GameLump.version >= 8:
            StaticProp.MinCPULevel = self.readUByte()
            StaticProp.MaxCPULevel = self.readUByte()
            StaticProp.MinGPULevel = self.readUByte()
            StaticProp.MaxGPULevel = self.readUByte()
        if GameLump.version >= 7:
            color = color32()
            color.r = self.readUByte()
            color.g = self.readUByte()
            color.b = self.readUByte()
            color.a = self.readUByte()
            StaticProp.DiffuseModulation = color
        if GameLump.version >= 10:
            StaticProp.unknown = self.readFloat()
        if GameLump.version >= 9:
            StaticProp.DisableX360 = self.readUInt32()

        return StaticProp

    def findFiles(self, model_path:str,type_:str = ''):
        model_path = type_ + model_path
        # if model_path.lower() in self.PAK.namelist():
        #     return 'PAK',model_path

        for game in self.gameInfo:
            if game == '|gameinfo_path|.':
                if os.path.isfile(os.path.join(self.gameInfo_path,model_path)):
                    return 'FILE',os.path.join(self.gameInfo_path,model_path)
            else:
                if os.path.isfile(os.path.join(self.gameInfo_path,'..',game,model_path)):
                    return 'FILE', os.path.join(self.gameInfo_path,'..',game,model_path)
        print('Can\'t find',model_path)
        return 'ERROR','ERROR'
    def getStaticPropsFile(self,model_path):
        FILES = {}

        type_, path = self.findFiles(model_path)
        if type_ == 'ERROR':
            return 'ERROR'
        # if type_ == 'PAK':
        #     MDL = self.PAK.open(path,'r')
        #     VVD = self.PAK.open(path.replace('.MDL','.VVD'),'r')
        #     FILES['VVD'] = VVD
        #     FILES['MDL'] = MDL
        #     try:
        #         VTX = self.PAK.open(path.replace('.MDL','.dx90.vtx'),'r')
        #     except:
        #         try:
        #             VTX = self.PAK.open(path.replace('.MDL','.VTX'),'r')
        #         except:
        #             return 'ERROR'
        #     FILES['VTX'] = VTX
        #     return FILES
        else:

            MDL = open(path,'rb')
            VVD = open(path.replace('.MDL', '.VVD'),'rb')
            try:
                VTX = open(path.replace('.MDL','.dx90.vtx'),'rb')
            except:
                try:
                    VTX = open(path.replace('.MDL','.VTX'),'rb')
                except:
                    return 'ERROR'
            FILES['VVD'] = VVD
            FILES['MDL'] = MDL
            FILES['VTX'] = VTX
            return FILES
    def getTextureFile(self,tex_path):
        if tex_path.startswith('maps/'):
            path = os.path.join(*tex_path.split('/')[2:-1])
            tex_path = tex_path.split('/')[-1]
            tex_path = '_'.join(tex_path.split('_')[:-3])
            tex_path = os.path.join(path,tex_path).replace('\\','/')

        type_, path = self.findFiles(tex_path+'.vmt','materials/')
        return path if type_!='ERROR' else None
    def finish(self):
        self.PAK.close()
        del self.PAK


import sys

if __name__ == '__main__':
    with open('log.log', "w") as f:
       with f as sys.stdout:
            a = BSPreader(r'sfm_campsite_night.bsp',r'D:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\usermod')

