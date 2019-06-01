import array
import struct

class NodeSkeleton:
    def __init__(self, nodeId):
        self.id = nodeId
        NODE_SKELETON = 3
        self.buffer = bytearray(4)
        self.buffer[0] = NODE_SKELETON
        self.name = ""
        self.boneNumbers = {}

    def loadArmature(self, armature):
        self.name = armature.name
        self.bones = armature.bones
        for i in range(0, len(self.bones)):
            self.boneNumbers[self.bones[i].name] = i

    def setGeometryId(self, val):
        self.geometryId = val

    def getBoneNumber(self, boneName):
        if boneName in self.boneNumbers:
            return self.boneNumbers[boneName]
        return -1

    def serialize(self):
        for bone in self.bones:
            parent = 0xFFFF
            if bone.parent and bone.parent.name in self.boneNumbers:
                parent = self.boneNumbers[bone.parent.name]
            boneVector = bone.tail_local - bone.head_local
            boneTail = bone.head + boneVector
            buf = struct.pack("<eeeeeeH", bone.head[0], bone.head[1], bone.head[2],
            boneTail[0], boneTail[1], boneTail[2], parent)
            self.buffer.extend(buf)
        nodeLength = len(self.buffer)
        buf = struct.pack("<I",nodeLength)
        self.buffer[1] = buf[0]
        self.buffer[2] = buf[1]
        self.buffer[3] = buf[2]
        return self.buffer
