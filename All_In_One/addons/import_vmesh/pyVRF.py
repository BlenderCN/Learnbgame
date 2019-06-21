import struct
import io
import numpy as np

class BinaryReader:
    # Map well-known type names into struct format characters.
    typeNames = {
        'bool'   :'?',
        'int8'   :'b',
        'uint8'  :'B',
        'int16'  :'h',
        'uint16' :'H',
        'int32'  :'i',
        'uint32' :'I',
        'int64'  :'q',
        'uint64' :'Q',
        'float'  :'f',
        'double' :'d',
        'char'   :'s'}

    def __init__(self, file, isFile=True):
        if isFile:
            self.stream = open( file, 'br' )
        else:
            self.stream = io.BytesIO( file )

    def readBytes(self, num):
        return self.stream.read(num)

    def readString(self, length):
        value = self.stream.read(length)
        return value.decode('utf-8', 'ignore')
        
    def read(self, typeName):
        typeFormat = BinaryReader.typeNames[typeName.lower()]
        typeSize = struct.calcsize(typeFormat)
        value = self.stream.read(typeSize)
        return struct.unpack(typeFormat, value)[0]

    def seek(self, offset):
        self.stream.seek(offset, 1)

    def goto(self, pos):
        self.stream.seek(pos, 0)

    def getPos(self):
        return self.stream.tell()

    def close(self):
        self.stream.close()

    def __del__(self):
        self.stream.close()

def readBlocks( path ):
    reader = BinaryReader( path )

    #read file header
    fileSize = reader.read('uint32')
    headerVersion = reader.read('uint16')
    version = reader.read('uint16')

    blockOffset = reader.read('uint32')
    blockCount = reader.read('uint32')

    #Seek to the first block
    reader.seek(blockOffset - 8)

    todo = []
    for n in range(blockCount):
        #Read the type (string identifier)
        blockType = reader.readString(4)

        #Offset in the file
        offset = reader.getPos() + reader.read('uint32')

        #Block size
        size = reader.read('uint32')

        todo.append((blockType, offset, size))

    blocks = {}
    for block in todo:
        reader.goto( block[1] )

        name = block[0]

        if name == 'DATA':
            blocks[name] = readBinaryKV3( reader, block[2] )
        elif name == 'VBIB':
            blocks[name] = readVBIB( reader, block[2] )
        else:
            blocks[name] = reader.readBytes( block[2] )

    reader.close()

    return blocks

def readBinaryKV3( reader, totalSize ):
    sig = reader.readString(4)
    encoding = reader.readBytes(16)
    kvFormat = reader.readBytes(16)
    flags = reader.readBytes(4)

    endPos = reader.getPos() + totalSize
    out = b''
    outPos = 0

    if (flags[3] & 0x80) > 0:
        out = reader.readBytes( endPos - reader.getPos() )
    else:
        running = True
        while running and reader.getPos() < endPos:
            blockMask = reader.read('uint16')
            for i in range(16):
                if blockMask & (1 << i) > 0:
                    offsetSize = reader.read('uint16')
                    offset = ((offsetSize & 0xFFF0) >> 4) + 1
                    size = (offsetSize & 0x000F) + 3

                    lookupSize = offset if (offset < size) else size

                    readBack = out[-offset:-offset+lookupSize]
                    if lookupSize - offset < 1:
                        readBack = out[-offset:]

                    while size > 0:
                        writeLength = lookupSize if (lookupSize < size) else size
                        size = size - lookupSize
                        out = out + readBack[:writeLength]
                        outPos = outPos + writeLength
                else:
                    data = reader.readBytes(1)
                    out = out + data
                    outPos = outPos + 1

                if outPos >= (flags[2] << 16) + (flags[1] << 8) + flags[0]:
                    running = False
                    break
    return parseBinaryKV3( out )

def parseBinaryKV3( kvBytes ):
    reader = BinaryReader( kvBytes, False )

    #Read all strings
    stringTable = []
    numStrings = reader.read('uint32')

    for _ in range(numStrings):
        stringTable.append( readNullTermString(reader) )

    #Parse the rest
    root = parseNode( reader, None, True, stringTable )
    return root

def parseNode( reader, parent, inArray, stringTable ):
    #Get the name
    name = ''
    if not inArray:
        stringID = reader.read('int32')
        name = stringTable[stringID] if stringID != -1 else ''
    elif parent != None:
        name = len(parent)
        parent.append(0)

    #Read type
    datatype = reader.readBytes(1)[0]
    flags = 0
    if (datatype & 0x80) > 0:
        datatype = datatype & 0x7F
        flags = reader.readBytes(1)[0]

    #Read data
    #NULL
    if datatype == 1:
        parent[name] = None
        pass
    #Boolean
    elif datatype == 2:
        parent[name] = reader.read('bool')
    #Integer
    elif datatype == 3:
        parent[name] = reader.read('int64')
    #Double
    elif datatype == 5:
        parent[name] = reader.read('double')
    #String
    elif datatype == 6:
        stringID = reader.read('int32')
        parent[name] = stringTable[stringID] if stringID != -1 else ''
    #Array
    elif datatype == 8:
        length = reader.read('uint32')
        array = []
        for _ in range(length):
            parseNode( reader, array, True, stringTable )

        parent[name] = array
    #Object
    elif datatype == 9:
        length = reader.read('uint32')
        newObject = {}
        for _ in range(length):
            parseNode( reader, newObject, False, stringTable )

        if parent == None:
            parent = newObject
        else:
            parent[name] = newObject

    return parent

def readNullTermString( reader ):
    string = b''
    c = reader.readBytes(1)
    while c != b'\x00':
        string = string + c
        c = reader.readBytes(1)
    return string.decode('utf-8', 'ignore')

def readVBIB(reader, totalSize):
    results = {}
    pos = reader.getPos()
    header = {}
    header["vertexHOffset"] = reader.read('uint32')
    header["vertexHLink"] = pos + header["vertexHOffset"]
    header["vertexHCount"] = reader.read('uint32')
    pos = reader.getPos()
    header["indexHOffset"] = reader.read('uint32')
    header["indexHLink"] = pos + header["indexHOffset"]
    header["indexHCount"] = reader.read('uint32')

    attributes = readAttributes(reader, header["vertexHLink"], header["vertexHCount"])
    print(attributes)
    results["vertexdata"] = readVertexAttributeData(reader,  header["vertexHLink"], header["vertexHCount"], attributes)
    results["indexdata"] = readIndices(reader, header["indexHLink"], header["indexHCount"])
    return results
    
def readAttributes(reader, offset, count):
    attributes = {}
    for x in range(0, count):
        reader.goto(offset +  x * 24 + 12)
        acount = reader.read("uint32")
        # print acount 
        reader.goto(offset + 24 * x + 8)
        pos = reader.read("uint32")
        # print pos
        link = offset + 24 * x + 8 + pos
        # print link
        for y in range (acount):
            here = link + y *56
            reader.goto(here)
            name = readNullTermString(reader)
           # print name
            reader.goto(here + 40)
            attributes[name] = reader.read("uint32")
    return attributes

def readIndices(reader, offset, count):
    indexgroups = []
    for x in range(0, count):
        indices = []
        reader.goto(offset + x * 24)
        icount = reader.read('uint32')
        reader.goto(offset + x * 24 + 16)
        link =  offset + x * 24 + 16 + reader.read('uint32')
        reader.goto(link)
        for q in range(int(icount / 3)):
            a = reader.read("uint16")
            b = reader.read("uint16")
            c = reader.read("uint16")
            #print(a,b,c)
            indices.append((a,b,c))
        indexgroups.append(indices)

    return indexgroups

def readVertexAttributeData(reader, offset, count,attributes):
    vertexgroups = []
    for x in range(count):
        vertices = {}
        vertices["vertex"] = []
        reader.goto(offset + x * 24)
        vcount = reader.read('uint32')
        reader.goto(offset + x * 24 + 16)
        link =  offset + x * 24 + 16 + reader.read('uint32')
        reader.goto(offset +  x * 24 + 4)
        size =  reader.read('uint32');

        reader.goto(link)
        for q in range(0, vcount):
            for key, value in attributes.items():
                reader.goto(link + q * size + value)
                if key == "POSITION":
                    #read vertex positions
                    x = reader.read("float")
                    y = reader.read("float")
                    z = reader.read("float")
                    #if q < 10:
                    #print(x,y,z)
                    vertices["vertex"].append((x,y,z))

                if key == "TEXCOORD":
                    #read texture (uv) coordinates
                    qbuffer = reader.readBytes(2)
                    u = np.frombuffer(qbuffer, dtype=np.float16)[0]
                    qbuffer = reader.readBytes(2)
                    v = 1 - np.frombuffer(qbuffer, dtype=np.float16)[0]

                    if not "texcoords" in vertices:
                        vertices["texcoords"] = []
                    vertices["texcoords"].append((u % 1, v % 1))

                if key == "NORMAL":
                    #read normals, not sure how to unpack pls helperino RGBA8?
                    normal = reader.read('uint32')

                    if not "normals" in vertices:
                        vertices["normals"] = []
                    vertices["normals"].append(normal)

                if key == "BLENDINDICES":
                    #read bone indices
                    a = reader.read("uint8")
                    b = reader.read("uint8")
                    c = reader.read("uint8")
                    d = reader.read("uint8") #bone num? unused? bullshit? you decide

                    if not "blendindices" in vertices:
                        vertices["blendindices"] = []
                    vertices["blendindices"].append((a,b,c,d))
                    #print(a,b,c,d)

                if key == "BLENDWEIGHT":
                    #read bone weights
                    a = reader.read("uint8")
                    b = reader.read("uint8")
                    c = reader.read("uint8")

                    if not "blendweights" in vertices:
                        vertices["blendweights"] = []
                    vertices["blendweights"].append((a,b,c))



        vertexgroups.append(vertices)

    return vertexgroups
