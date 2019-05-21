##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

import struct, math
from mathutils import Vector, Quaternion

global is_debug
is_debug = True


def PrintDeb(*args, end="\n"):
    if is_debug:
        print(*args, end=end)


def ReadChar(f):
    return int.from_bytes(f.read(1), 'little')


def ReadUInt16(f):
    return int.from_bytes(f.read(2), 'little')


def ReadUInt32(f):
    return int.from_bytes(f.read(4), 'little')


def ReadInt32(f):
    return int.from_bytes(f.read(4), 'little', signed=True)


def ReadUInt64(f):
    return int.from_bytes(f.read(8), 'little')


def ReadFloat(f):
    return struct.unpack('f', f.read(4))[0]


def ReadUInt16Vector(f):
    return (ReadUInt16(f), ReadUInt16(f), ReadUInt16(f))


def ReadFloatVector2(f):
    return ((ReadFloat(f), ReadFloat(f)))


def ReadFloatVector(f):
    return ((ReadFloat(f), ReadFloat(f), ReadFloat(f)))


def ReadFloatVector4(f):
    return ((ReadFloat(f), ReadFloat(f), ReadFloat(f), ReadFloat(f)))


def ReadFloatQuaternion(f):
    return ((ReadFloat(f), ReadFloat(f), ReadFloat(f), ReadFloat(f)))


def ReadCharVector4(f):
    return ((ReadChar(f), ReadChar(f), ReadChar(f), ReadChar(f)))


def CharToByts(val):
    return val.to_bytes(1, 'little')


def CharVec4ToByts(vec):
    return CharToByts(vec[0]) + CharToByts(vec[1]) + CharToByts(vec[2]) + CharToByts(vec[3])


def FloatToByts(val):
    return struct.pack('f', val)


def FloatVec2ToByts(vec):
    return struct.pack('2f', vec[0], vec[1])


def FloatVecToByts(vec):
    return struct.pack('3f', vec[0], vec[1], vec[2])


def FloatQuatToByts(vec):
    return struct.pack('4f', vec[0], vec[1], vec[2], vec[3])


def UInt16VecToByts(vec):
    return UInt16ToByts(vec[0]) + UInt16ToByts(vec[1]) + UInt16ToByts(vec[2])


def UInt64ToByts(val):
    return val.to_bytes(8, 'little')


def UInt16ToByts(val):
    return val.to_bytes(2, 'little')


def UInt32ToByts(val):
    return val.to_bytes(4, 'little')


def Int32ToByts(val):
    return val.to_bytes(4, 'little', signed=True)


def ConvertSCSMatrix(matrix):
    m = matrix.copy()
    for i in range(0, 4):
        for j in [0, 2]:
            m[i][j + (i + 1) % 2] *= -1
    return m


def ConvertSCSQuat(quaternion):
    q = Quaternion(quaternion)
    q.x *= -1
    q.z *= -1
    return q


def ConvertSCSVec(vector):
    v = Vector(vector)
    v.x *= -1
    v.z *= -1
    return v


def DecodeNameCRC(val):
    i = 1
    ret = ""
    while val > 0:
        curr_fact = int(math.pow(38, i))
        temp = val % curr_fact
        curr_ch = __get_ch[int(temp / (curr_fact / 38))]
        i += 1
        ret += curr_ch
        val -= int(temp)
    return ret


def EncodeNameCRC(word):
    i = 0
    res = 0
    for ch in word:
        curr_no = __get_int[ch]
        res += int(math.pow(38, i)) * int(curr_no)
        i += 1
    return res


def IsWordValid(word):
    if len(word) > 12:
        return 1, "Given name '" + word + "' is to long!(Max length 12)"
    word = word.lower()
    for ch in word:
        if not ch in __get_int:
            return 1, "Character '" + ch + "' is invalid for name '" + word + "'!"
    return 0, ""


__get_int = {'0': 1, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10, 'a': 11, 'b': 12,
             'c': 13, 'd': 14, 'e': 15, 'f': 16, 'g': 17, 'h': 18, 'i': 19, 'j': 20, 'k': 21, 'l': 22, 'm': 23, 'n': 24,
             'o': 25, 'p': 26, 'q': 27, 'r': 28, 's': 29, 't': 30, 'u': 31, 'v': 32, 'w': 33, 'x': 34, 'y': 35, 'z': 36,
             '_': 37}

__get_ch = { 1: '0', 2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: 'A', 12: 'B',
            13: 'C', 14: 'D', 15: 'E', 16: 'F', 17: 'G', 18: 'H', 19: 'I', 20: 'J', 21: 'K', 22: 'L', 23: 'M', 24: 'N',
            25: 'O', 26: 'P', 27: 'Q', 28: 'R', 29: 'S', 30: 'T', 31: 'U', 32: 'V', 33: 'W', 34: 'X', 35: 'Y', 36: 'Z',
            37: '_'}