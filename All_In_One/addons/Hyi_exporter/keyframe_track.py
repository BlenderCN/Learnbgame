import array
import struct
import mathutils

TRACK_BONE_POSITION_KEYFRAMES = 1
TRACK_BONE_ROTATION_KEYFRAMES = 2

class KeyframeTrack:
    def __init__(self, boneNumber, stringType, boneName, boneMatrix):
        self.buffer = bytearray(4)
        self.boneNumber = boneNumber
        self.boneName = boneName
        self.boneMatrix =  [row[:] for row in boneMatrix]
        self.timePoints = []
        self.values = []
        self.type = 0
        if stringType == "location":
            self.type = TRACK_BONE_POSITION_KEYFRAMES
        if stringType == "rotation_euler" or stringType == "rotation_quaternion":
            self.type = TRACK_BONE_ROTATION_KEYFRAMES
            self.rotationType = stringType
        self.buffer[0] = self.type
        self.buffer.append(self.boneNumber & 0xFF)
        self.buffer.append(self.boneNumber >> 8 )

    def parseKeyframeData(self, timePoint, pose):
        bone = pose.bones[self.boneName]
        if self.type == TRACK_BONE_POSITION_KEYFRAMES:
            value = mathutils.Vector(self.convertToParallelBasis(bone.location))
        elif self.type == TRACK_BONE_ROTATION_KEYFRAMES:
            if self.rotationType == "rotation_quaternion":
                rotQuaternion = bone.rotation_quaternion
            else:
                rotQuaternion = bone.rotation_euler.to_quaternion()
            rotQuaternion.axis = self.convertToParallelBasis(rotQuaternion.axis)
            value = rotQuaternion.normalized()
            if value.w < 0:
                value = value.inverted()
        else:
            return
        self.timePoints.append(timePoint)
        self.values.append(value)

    def convertToParallelBasis(self, vector):
        return [\
        vector[0]*self.boneMatrix[0][0] + vector[1]*self.boneMatrix[0][1] + vector[2]*self.boneMatrix[0][2], \
        vector[0]*self.boneMatrix[1][0] + vector[1]*self.boneMatrix[1][1] + vector[2]*self.boneMatrix[1][2], \
        vector[0]*self.boneMatrix[2][0] + vector[1]*self.boneMatrix[2][1] + vector[2]*self.boneMatrix[2][2], \
        ]

    def serialize(self):
        if self.type == TRACK_BONE_POSITION_KEYFRAMES or \
        self.type == TRACK_BONE_ROTATION_KEYFRAMES:
            prevTimePoint = 0
            for i in range(0, len(self.values)):
                dt = self.timePoints[i] - prevTimePoint
                prevTimePoint = self.timePoints[i]
                value = self.values[i]
                buf = struct.pack("<eeee", dt, value.x, value.y, value.z)
                self.buffer.extend(buf)
        trackLength = len(self.buffer)
        buf = struct.pack("<I",trackLength)
        self.buffer[1] = buf[0]
        self.buffer[2] = buf[1]
        self.buffer[3] = buf[2]
        return self.buffer
