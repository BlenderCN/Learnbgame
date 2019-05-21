# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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

import math
from mathutils import Vector, Matrix

#-------------------------------------------------------------------------------
#   Utilities
#-------------------------------------------------------------------------------

def m2b(vec):
    return Vector((vec[0], -vec[2], vec[1]))

def b2m(vec):
    return Vector((vec[0], vec[2], -vec[1]))

def getUnitVector(vec):
    length = math.sqrt(vec.dot(vec))
    return vec/length


def splitBoneName(bone):
    words = bone.rsplit(".", 1)
    if len(words) > 1:
        return words[0], "."+words[1]
    else:
        return words[0], ""


def getFkName(base, ext):
    return (base + ".fk" + ext)


def getIkName(base, ext):
    return (base + ".ik" + ext)


def splitBonesNames(base, ext, prefix, numAfter):
    if numAfter:
        defname1 = prefix+base+ext+".01"
        defname2 = prefix+base+ext+".02"
        defname3 = prefix+base+ext+".03"
    else:
        defname1 = prefix+base+".01"+ext
        defname2 = prefix+base+".02"+ext
        defname3 = prefix+base+".03"+ext
    return defname1, defname2, defname3


def csysBoneName(bname, infix):
    base,ext = splitBoneName(bname)
    return ("CSYS-" + base + infix + ext)


def addDict(dict, struct):
    for key,value in dict.items():
        struct[key] = value


def safeAppendToDict(struct, key, value):
    try:
        struct[key] = list(struct[key])
    except KeyError:
        struct[key] = []
    struct[key].append(value)


def mergeDicts(dicts):
    struct = {}
    for dict in dicts:
        addDict(dict, struct)
    return struct


def safeGet(dict, key, default):
    try:
        return dict[key]
    except KeyError:
        return default


def copyTransform(target, cnsname, inf=1):
    return ('CopyTrans', 0, inf, [cnsname, target, 0])


def checkOrthogonal(mat):
    prod = mat * mat.transposed()
    diff = prod - Matrix.Identity(3)
    sum = 0
    for i in range(3):
        for j in range(3):
            if abs(diff[i][j]) > 1e-5:
                raise NameError("Not ortho: diff[%d,%d] = %g\n%s\n\%s" % (i, j, diff[i][j], mat, prod))
    return True


def computeRoll(head, tail, normal, bone=None):
    if normal is None:
        return 0

    p1 = m2b(head)
    p2 = m2b(tail)
    xvec = normal
    pvec = getUnitVector(p2-p1)
    xy = xvec.dot(pvec)
    yvec = getUnitVector(pvec-xy*xvec)
    zvec = getUnitVector(xvec.cross(yvec))
    if zvec is None:
        return 0
    else:
        mat = Matrix((xvec,yvec,zvec))

    checkOrthogonal(mat)
    quat = mat.to_quaternion()
    if abs(quat[0]) < 1e-4:
        return 0
    else:
        roll = math.pi - 2*math.atan(quat[2]/quat[0])

    if roll < -math.pi:
        roll += 2*math.pi
    elif roll > math.pi:
        roll -= 2*math.pi
    return roll

    if bone and bone.name in ["forearm.L", "forearm.R"]:
        print("B  %s" % bone.name)
        print(" H  %.4g %.4g %.4g" % tuple(head))
        print(" T  %.4g %.4g %.4g" % tuple(tail))
        print(" N  %.4g %.4g %.4g" % tuple(normal))
        print(" P  %.4g %.4g %.4g" % tuple(pvec))
        print(" X  %.4g %.4g %.4g" % tuple(xvec))
        print(" Y  %.4g %.4g %.4g" % tuple(yvec))
        print(" Z  %.4g %.4g %.4g" % tuple(zvec))
        print(" Q  %.4g %.4g %.4g %.4g" % tuple(quat))
        print(" R  %.4g" % roll)

    return roll


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

def mergeWeights(vgroup):
    vgroup.sort()
    ngroup = []
    vn0 = -1
    w0 = 0
    for vn,w in vgroup:
        if vn == vn0:
            w0 += w
        else:
            ngroup.append([vn0,w0])
            vn0 = vn
            w0 = w
    if vn0 >= 0:
        ngroup.append([vn0,w0])
    if ngroup != [] and ngroup[0][0] < 0:
        ngroup = ngroup[1:]
    return ngroup

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

XUnit = Vector((1,0,0))
YUnit = Vector((0,1,0))
ZUnit = Vector((0,0,1))

YZRotation = Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
ZYRotation = Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))

def m2b3(vec):
    return ZYRotation.to_3x3() * vec

def b2m4(mat):
    return YZRotation * mat

def getMatrix(head, tail, roll):
    vector = m2b3(tail - head)
    length = math.sqrt(vector.dot(vector))
    vector = vector/length
    yproj = vector.dot(YUnit)

    if yproj > 1-1e-6:
        axis = YUnit
        angle = 0
    elif yproj < -1+1e-6:
        axis = YUnit
        angle = math.pi
    else:
        axis = YUnit.cross(vector)
        axis = axis / math.sqrt(axis.dot(axis))
        angle = math.acos(yproj)
    mat = Matrix.Rotation(angle, 3, axis)
    if roll:
        mat = mat * Matrix.Rotation(roll, 3, YUnit)
    mat = b2m4(mat)
    mat.col[3][:3] = head
    return length, mat


def normalizeQuaternion(quat):
    r2 = quat[1]*quat[1] + quat[2]*quat[2] + quat[3]*quat[3]
    if r2 > 1:
        r2 = 1
    if quat[0] >= 0:
        sign = 1
    else:
        sign = -1
    quat[0] = sign*math.sqrt(1-r2)


def checkPoints(vec1, vec2):
    return ((abs(vec1[0]-vec2[0]) < 1e-6) and
            (abs(vec1[1]-vec2[1]) < 1e-6) and
            (abs(vec1[2]-vec2[2]) < 1e-6))


