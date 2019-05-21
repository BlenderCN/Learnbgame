import array
import struct

class NodeGeometry:
    def __init__(self, nodeId):
        self.id = nodeId
        NODE_GEOMETRY = 1
        self.buffer = bytearray(4)
        self.buffer[0] = NODE_GEOMETRY
        self.vertices = array.array('d')
        self.faces3 = array.array('L')
        self.skinIndices = array.array('B')
        self.skinWeights = array.array('B')

    def pushVertex(self, x, y, z):
        self.vertices.append(x)
        self.vertices.append(y)
        self.vertices.append(z)

    def pushFace(self, a, b, c):
        self.faces3.append(a)
        self.faces3.append(b)
        self.faces3.append(c)

    def pushSkinIndices(self, a, b, c, d):
        self.skinIndices.append(a)
        self.skinIndices.append(b)
        self.skinIndices.append(c)
        self.skinIndices.append(d)

    def pushSkinWeights(self, a, b, c, d):
        self.pushSkinWeight(a)
        self.pushSkinWeight(b)
        self.pushSkinWeight(c)
        self.pushSkinWeight(d)

    def pushSkinWeight(self, value):
        w = int (value * 255)
        if (w>255):
            w = 255
        if (w < 0):
            w = 0
        self.skinWeights.append(w)

    def serialize(self):
        ATTRIB_HEADER_LENGTH = 4
        GEOMETRY_ATTR_VERTICES = 1
        GEOMETRY_ATTR_TRIANGLE_FACES = 2
        GEOMETRY_ATTR_SKIN_INDICES = 3
        GEOMETRY_ATTR_SKIN_WEIGHTS = 4
        if len(self.vertices) >0:
            self.buffer.append(GEOMETRY_ATTR_VERTICES)
            attr_length = ATTRIB_HEADER_LENGTH + 2 * len(self.vertices)
            buf = struct.pack("<I",attr_length)
            self.buffer.append(buf[0])
            self.buffer.append(buf[1])
            self.buffer.append(buf[2])
            for vert in self.vertices:
                f16value = struct.pack("<e",vert)
                self.buffer.append(f16value[0])
                self.buffer.append(f16value[1])
        if len(self.faces3) > 0:
            self.buffer.append(GEOMETRY_ATTR_TRIANGLE_FACES)
            attr_length = ATTRIB_HEADER_LENGTH + 2 * len(self.faces3)
            buf = struct.pack("<I",attr_length)
            self.buffer.append(buf[0])
            self.buffer.append(buf[1])
            self.buffer.append(buf[2])
            for vertexIndex in self.faces3:
                self.buffer.append(vertexIndex & 0xFF)
                self.buffer.append((vertexIndex>>8) & 0xFF)
        if len(self.skinIndices) > 0:
            self.buffer.append(GEOMETRY_ATTR_SKIN_INDICES)
            attr_length = ATTRIB_HEADER_LENGTH + len(self.skinIndices)
            buf = struct.pack("<I",attr_length)
            self.buffer.append(buf[0])
            self.buffer.append(buf[1])
            self.buffer.append(buf[2])
            for val in self.skinIndices:
                self.buffer.append(val)
        if len(self.skinWeights) > 0:
            self.buffer.append(GEOMETRY_ATTR_SKIN_WEIGHTS)
            attr_length = ATTRIB_HEADER_LENGTH + len(self.skinWeights)
            buf = struct.pack("<I",attr_length)
            self.buffer.append(buf[0])
            self.buffer.append(buf[1])
            self.buffer.append(buf[2])
            for val in self.skinWeights:
                self.buffer.append(val)
        nodeLength = len(self.buffer)
        buf = struct.pack("<I",nodeLength)
        self.buffer[1] = buf[0]
        self.buffer[2] = buf[1]
        self.buffer[3] = buf[2]
        return self.buffer
