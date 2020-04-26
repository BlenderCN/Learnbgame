import array
import struct

class NodeMesh:
    def __init__(self):
        NODE_MESH = 2
        self.buffer = bytearray(4)
        self.buffer[0] = NODE_MESH
        self.geometryId = -1
        self.skeletonId = -1

    def setGeometryId(self, val):
        self.geometryId = val

    def setSkeletonId(self, val):
        self.skeletonId = val

    def serialize(self):
        MESH_PARAM_GEOMETRY = 1
        MESH_PARAM_SKELETON = 2
        if self.geometryId > -1:
            self.buffer.append(MESH_PARAM_GEOMETRY & 0xFF)
            self.buffer.append(MESH_PARAM_GEOMETRY >> 8)
            self.buffer.append(self.geometryId & 0xFF)
            self.buffer.append(self.geometryId >> 8)
        if self.skeletonId > -1:
            self.buffer.append(MESH_PARAM_SKELETON & 0xFF)
            self.buffer.append(MESH_PARAM_SKELETON >> 8)
            self.buffer.append(self.skeletonId & 0xFF)
            self.buffer.append(self.skeletonId >> 8)
        nodeLength = len(self.buffer)
        buf = struct.pack("<I",nodeLength)
        self.buffer[1] = buf[0]
        self.buffer[2] = buf[1]
        self.buffer[3] = buf[2]
        return self.buffer
