# * Copyright (c) Contributors
# * See CONTRIBUTORS.TXT for a full list of copyright holders.
# *
# * Redistribution and use in source and binary forms, with or without
# * modification, are permitted provided that the following conditions are met:
# *     * Redistributions of source code must retain the above copyright
# *       notice, this list of conditions and the following disclaimer.
# *     * Redistributions in binary form must reproduce the above copyright

# *       documentation and/or other materials provided with the distribution.
# *     * Neither the name of the OpenSimulator Project nor the
# *       names of its contributors may be used to endorse or promote products
# *       derived from this software without specific prior written permission.
# *
# * THIS SOFTWARE IS PROVIDED BY THE DEVELOPERS ``AS IS'' AND ANY
# * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# * DISCLAIMED. IN NO EVENT SHALL THE CONTRIBUTORS BE LIABLE FOR ANY
# * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import io
import os
import copy
import math
import traceback
#from System import *
#from System.Collections.Generic import *
#from System.Text import *
#from System.IO import *

Single=float

class ProfileShape(object):
    Circle = 0
    Square = 1
    IsometricTriangle = 2
    EquilateralTriangle = 3
    RightTriangle = 4
    HalfCircle = 5

class Extrusion(object):
    Straight = 16
    Curve1 = 32
    Curve2 = 48
    Flexible = 128

class HollowShape(object):
    Same = 0
    Circle = 16
    Square = 32
    Triangle = 48

class ListEnumerator(object):
    def __init__(self, parent):
        self._parent = parent
        self._idx = -1
    def MoveNext(self):
        self._idx += 1
        if len(self._parent) > self._idx:
            return True
        else:
            return False
    def _get_current(self):
        return self._parent[self._idx]
    Current = property(_get_current)

class List(object):
    def __init__(self, cls, values=[]):
        self._cls = cls
        self._values = list(values)
    def __iter__(self):
        return iter(self._values)
    def __len__(self):
        return len(self._values)
    def GetEnumerator(self):
        return ListEnumerator(self)
    def __getitem__(self, nitem):
        return self._values[int(nitem)]
    def __setitem__(self, nitem, value):
        self._values[nitem] = value
    def get_len(self):
        return len(self._values)
    def Reverse(self):
        self._values = list(reversed(self._values))
        return self
    def AddRange(self, values):
        for val in values:
            self._values.append(copy.copy(val))
    def ToString(self):
        return ",".join(map(lambda s: str(s), self._values))
    Count = property(get_len)
    Length = property(get_len)
    def Add(self, obj):
        self._values.append(copy.copy(obj))

class Quat(object):
    # <summary>X value</summary>
    # <summary>Y value</summary>
    # <summary>Z value</summary>
    # <summary>W value</summary>
    def __init__(self, *args):
        if len(args) == 2:
            self.__init2__(*args)
        else:
            self.__init4__(*args)

    def __init4__(self, X, Y, Z, W):
        self._X = X
        self._Y = Y
        self._Z = Z
        self._W = W

    def __init2__(self, axis, angle):
        axis = axis.Normalize()
        angle *= 0.5
        c = math.cos(angle)
        s = math.sin(angle)
        self._X = axis.X * s
        self._Y = axis.Y * s
        self._Z = axis.Z * s
        self._W = c
        self.Normalize()

    def __getattr__(self, name):
        if not name.startswith('_'):
            return getattr(self, '_'+name)
        else:
            raise Exception()


    def __mul__(self, q2):
        q1 = self
        x = q1.W * q2.X + q1.X * q2.W + q1.Y * q2.Z - q1.Z * q2.Y
        y = q1.W * q2.Y - q1.X * q2.Z + q1.Y * q2.W + q1.Z * q2.X
        z = q1.W * q2.Z + q1.X * q2.Y - q1.Y * q2.X + q1.Z * q2.W
        w = q1.W * q2.W - q1.X * q2.X - q1.Y * q2.Y - q1.Z * q2.Z
        return Quat(x, y, z, w)

    def Length(self):
        return math.sqrt(self._X * self._X + self._Y * self._Y + self._Z * self._Z + self._W * self._W)

    def Normalize(self):
        MAG_THRESHOLD = 0.0000001
        mag = self.Length()
        # Catch very small rounding errors when normalizing
        if mag > MAG_THRESHOLD:
            oomag = 1 / mag
            self._X *= oomag
            self._Y *= oomag
            self._Z *= oomag
            self._W *= oomag
        else:
            self._X = 0
            self._Y = 0
            self._Z = 0
            self._W = 1
        return self

    def ToString(self):
        return "< X: " + self._X.ToString() + ", Y: " + self._Y.ToString() + ", Z: " + self._Z.ToString() + ", W: " + self._W.ToString() + ">"

class Coord(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self._X = x
        self._Y = y
        self._Z = z

    def _get_x(self):
        return self._X
    def _get_y(self):
        return self._Y
    def _get_z(self):
        return self._Z
    def _set_x(self, value):
        self._X = value
    def _set_y(self, value):
        self._Y = value
    def _set_z(self, value):
        self._Z = value

    def __repr__(self):
        return "Coord(%s, %s, %s)" %(self._X, self._Y, self._Z)

    X = property(_get_x, _set_x)
    Y = property(_get_y, _set_y)
    Z = property(_get_z, _set_z)

    def Length(self):
        return math.sqrt(self._X * self._X + self._Y * self._Y + self._Z * self._Z)

    def Invert(self):
        self._X = -self._X
        self._Y = -self._Y
        self._Z = -self._Z
        return self

    def Normalize(self):
        MAG_THRESHOLD = 0.0000001
        mag = float(self.Length())
        # Catch very small rounding errors when normalizing
        if mag > MAG_THRESHOLD:
            oomag = 1.0 / mag
            self._X *= oomag
            self._Y *= oomag
            self._Z *= oomag
        else:
            self._X = 0.0
            self._Y = 0.0
            self._Z = 0.0
        return self

    def ToString(self):
        return str(self._X) + " " + str(self._Y) + " " + str(self._Z)

    def __mul__(self, b):
        if isinstance(b, Coord):
            return Coord(self.X * b.X, self.Y * b.Y, self.Z * b.Z)
        else:
            return self.mulquat(b)

    def __sum__(self, a):
        v = self
        return Coord(v.X + a.X, v.Y + a.Y, v.Z + a.Z)

    def mulquat(self, q):
        v = self
        # From http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/transforms/
        c2 = Coord(0.0, 0.0, 0.0)
        c2.X = q.W * q.W * v.X + \
                2.0 * q.Y * q.W * v.Z - \
                2.0 * q.Z * q.W * v.Y + \
                     q.X * q.X * v.X + \
                2.0 * q.Y * q.X * v.Y + \
                2.0 * q.Z * q.X * v.Z - \
                     q.Z * q.Z * v.X - \
                     q.Y * q.Y * v.X

        c2.Y =  2.0 * q.X * q.Y * v.X + \
             q.Y * q.Y * v.Y + \
        2.0 * q.Z * q.Y * v.Z + \
        2.0 * q.W * q.Z * v.X - \
             q.Z * q.Z * v.Y + \
             q.W * q.W * v.Y - \
        2.0 * q.X * q.W * v.Z - \
             q.X * q.X * v.Y

        c2.Z = 2.0 * q.X * q.Z * v.X + \
        2.0 * q.Y * q.Z * v.Y + \
             q.Z * q.Z * v.Z - \
        2.0 * q.W * q.Y * v.X - \
             q.Y * q.Y * v.Z + \
        2.0 * q.W * q.X * v.Y - \
             q.X * q.X * v.Z + \
             q.W * q.W * v.Z

        return c2

    def Cross(c1, c2):
        return Coord(c1.Y * c2.Z - c2.Y * c1.Z, c1.Z * c2.X - c2.Z * c1.X, c1.X * c2.Y - c2.X * c1.Y)

    Cross = staticmethod(Cross)

# From http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions/transforms/
class UVCoord(object):
    def __init__(self, u=0.0, v=0.0):
        self.U = u
        self.V = v
    def asList(self):
        return self.U, self.V

class Face(object):
    # vertices
    #normals
    # uvs
    def __init__(self, v1=0, v2=0, v3=0, n1=0, n2=0, n3=0):
        self._primFace = 0
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3

        self.uv1 = 0
        self.uv2 = 0
        self.uv3 = 0

    def __str__(self):
        return "Face(%s,%s,%s)"%(self.v1, self.v2, self.v3)
    def __repr__(self):
        return "Face(%s,%s,%s)"%(self.v1, self.v2, self.v3)

    def SurfaceNormal(self, coordList):
        c1 = coordList[self.v1]
        c2 = coordList[self.v2]
        c3 = coordList[self.v3]
        edge1 = Coord(c2.X - c1.X, c2.Y - c1.Y, c2.Z - c1.Z)
        edge2 = Coord(c3.X - c1.X, c3.Y - c1.Y, c3.Z - c1.Z)
        return Coord.Cross(edge1, edge2).Normalize()

class ViewerFace(object):
    def __init__(self, primFaceNumber):
        self.primFaceNumber = primFaceNumber
        self.v1 = Coord()
        self.v2 = Coord()
        self.v3 = Coord()
        self.coordIndex1 = self.coordIndex2 = self.coordIndex3 = -1 # -1 means not assigned yet
        self.n1 = Coord()
        self.n2 = Coord()
        self.n3 = Coord()
        self.uv1 = UVCoord()
        self.uv2 = UVCoord()
        self.uv3 = UVCoord()

    def Scale(self, x, y, z):
        self.v1.X *= x
        self.v1.Y *= y
        self.v1.Z *= z
        self.v2.X *= x
        self.v2.Y *= y
        self.v2.Z *= z
        self.v3.X *= x
        self.v3.Y *= y
        self.v3.Z *= z

    def AddPos(self, x, y, z):
        self.v1.X += self.x
        self.v2.X += self.x
        self.v3.X += self.x
        self.v1.Y += self.y
        self.v2.Y += self.y
        self.v3.Y += self.y
        self.v1.Z += self.z
        self.v2.Z += self.z
        self.v3.Z += self.z

    def AddRot(self, q):
        self.v1 *= q
        self.v2 *= q
        self.v3 *= q
        self.n1 *= q
        self.n2 *= q
        self.n3 *= q

    def CalcSurfaceNormal(self):
        edge1 = Coord(self.v2.X - self.v1.X, self.v2.Y - self.v1.Y, self.v2.Z - self.v1.Z)
        edge2 = Coord(self.v3.X - self.v1.X, self.v3.Y - self.v1.Y, self.v3.Z - self.v1.Z)
        self.n1 = self.n2 = self.n3 = Coord.Cross(edge1, edge2).Normalize()

class Angle(object):
    def __init__(self, angle, x, y):
        self._angle = angle
        self._X = x
        self._Y = y
    def __getattr__(self, name):
        if not name.startswith('_'):
            return getattr(self, '_'+name)
        else:
            raise AttributeError

class AngleList(object):
    _angles3 = List(Angle,
                    [Angle(0.0, 1.0, 0.0),
                     Angle(0.33333333333333333, -0.5, 0.86602540378443871),
                     Angle(0.66666666666666667, -0.5, -0.86602540378443837),
                     Angle(1.0, 1.0, 0.0)])
    _normals3 = List(Coord,
                    [Coord(0.25, 0.4330127019, 0.0).Normalize(),
                     Coord(-0.5, 0.0, 0.0).Normalize(),
                     Coord(0.25, -0.4330127019, 0.0).Normalize(),
                     Coord(0.25, 0.4330127019, 0.0).Normalize()])
    _angles4 = List(Angle,
                    [Angle(0.0, 1.0, 0.0),
                     Angle(0.25, 0.0, 1.0),
                     Angle(0.5, -1.0, 0.0),
                     Angle(0.75, 0.0, -1.0),
                     Angle(1.0, 1.0, 0.0)])
    _normals4 = List(Coord,
                [Coord(0.5, 0.5, 0.0).Normalize(),
                Coord(-0.5, 0.5, 0.0).Normalize(),
                Coord(-0.5, -0.5, 0.0).Normalize(),
                Coord(0.5, -0.5, 0.0).Normalize(),
                Coord(0.5, 0.5, 0.0).Normalize()])

    _angles24 = List(Angle,
                    [Angle(0.0, 1.0, 0.0),
                Angle(0.041666666666666664, 0.96592582628906831, 0.25881904510252074),
                Angle(0.083333333333333329, 0.86602540378443871, 0.5),
                Angle(0.125, 0.70710678118654757, 0.70710678118654746),
                Angle(0.16666666666666667, 0.5, 0.8660254037844386),
                Angle(0.20833333333333331, 0.25881904510252096, 0.9659258262890682),
                Angle(0.25, 0.0, 1.0),
                Angle(0.29166666666666663, -0.25881904510252063, 0.96592582628906831),
                Angle(0.33333333333333333, -0.5, 0.86602540378443871),
                Angle(0.375, -0.70710678118654746, 0.70710678118654757),
                Angle(0.41666666666666663, -0.86602540378443849, 0.5),
                Angle(0.45833333333333331, -0.9659258262890682, 0.25881904510252102),
                Angle(0.5, -1.0, 0.0),
                Angle(0.54166666666666663, -0.96592582628906842, -0.25881904510252035),
                Angle(0.58333333333333326, -0.86602540378443882, -0.5),
                Angle(0.62499999999999989, -0.70710678118654791, -0.70710678118654713),
                Angle(0.66666666666666667, -0.5, -0.86602540378443837),
                Angle(0.70833333333333326, -0.25881904510252152, -0.96592582628906809),
                Angle(0.75, 0.0, -1.0),
                Angle(0.79166666666666663, 0.2588190451025203, -0.96592582628906842),
                Angle(0.83333333333333326, 0.5, -0.86602540378443904),
                Angle(0.875, 0.70710678118654735, -0.70710678118654768),
                Angle(0.91666666666666663, 0.86602540378443837, -0.5),
                Angle(0.95833333333333326, 0.96592582628906809, -0.25881904510252157),
                Angle(1.0, 1.0, 0.0)])

    def __getattr__(self, name):
        if not name.startswith('_'):
            return getattr(self, '_'+name)
        else:
            raise Exception()

    def interpolatePoints(self, newPoint, p1, p2):
        m = (newPoint - p1.angle) / (p2.angle - p1.angle)
        return Angle(newPoint, p1.X + m * (p2.X - p1.X), p1.Y + m * (p2.Y - p1.Y))

    def intersection(self, x1, y1, x2, y2, x3, y3, x4, y4): # ref: http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        uaNumerator = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
        if denom != 0.0:
            ua = uaNumerator / denom
            self._iX = (x1 + ua * (x2 - x1))
            self._iY = (y1 + ua * (y2 - y1))

    def makeAngles(self, sides, startAngle, stopAngle):
        self._angles = List(Angle)
        self._normals = List(Coord)
        twoPi = math.pi * 2.0
        twoPiInv = 1.0 / twoPi
        if sides < 1:
            raise Exception("number of sides not greater than zero")
        if stopAngle <= startAngle:
            raise Exception("stopAngle not greater than startAngle")
        if (sides == 3 or sides == 4 or sides == 24):
            startAngle *= twoPiInv
            stopAngle *= twoPiInv
            if sides == 3:
                sourceAngles = self._angles3
            elif sides == 4:
                sourceAngles = self._angles4
            else:
                sourceAngles = self._angles24
            startAngleIndex = int(startAngle * sides)
            endAngleIndex = sourceAngles.Length - 1
            if stopAngle < 1.0:
                endAngleIndex = int(stopAngle * sides) + 1
            if endAngleIndex == startAngleIndex:
                endAngleIndex += 1
            angleIndex = startAngleIndex
            while angleIndex < endAngleIndex + 1:
                self._angles.Add(sourceAngles[angleIndex])
                if sides == 3:
                    self._normals.Add(self._normals3[angleIndex])
                elif sides == 4:
                    self._normals.Add(self._normals4[angleIndex])
                angleIndex += 1
            if startAngle > 0.0:
                self._angles[0] = self.interpolatePoints(startAngle, self._angles[0], self._angles[1])
            if stopAngle < 1.0:
                lastAngleIndex = self._angles.Count - 1
                self._angles[lastAngleIndex] = self.interpolatePoints(stopAngle, self._angles[lastAngleIndex - 1], self._angles[lastAngleIndex])
        else:
            stepSize = twoPi / float(sides)
            startStep = int(startAngle / stepSize)
            angle = stepSize * startStep
            step = startStep
            stopAngleTest = stopAngle
            if stopAngle < twoPi:
                stopAngleTest = stepSize * (int(stopAngle / stepSize) + 1)
                if stopAngleTest < stopAngle:
                    stopAngleTest += stepSize
                if stopAngleTest > twoPi:
                    stopAngleTest = twoPi
            while angle <= stopAngleTest:
                newAngle  = Angle(angle, math.cos(angle), math.sin(angle))
                self._angles.Add(newAngle)
                step += 1
                angle = stepSize * step
            if startAngle > self._angles[0].angle:
                self.intersection(self._angles[0].X, self._angles[0].Y, self._angles[1].X, self._angles[1].Y, 0.0, 0.0, math.cos(startAngle), math.sin(startAngle))
                newAngle  = Angle(startAngle, self._iX, self._iY)
                self._angles[0] = newAngle
            index = self._angles.Count - 1
            if stopAngle < self._angles[index].angle:
                self.intersection(self._angles[index - 1].X, self._angles[index - 1].Y, self._angles[index].X, self._angles[index].Y, 0.0, 0.0, math.cos(stopAngle), math.sin(stopAngle))
                newAngle  = Angle(stopAngle, self._iX, self._iY)
                newAngle.angle = stopAngle
                newAngle.X = self._iX
                newAngle.Y = self._iY
                self._angles[index] = newAngle

class Profile(object):
    """ <summary>
     generates a profile for extrusion
     </summary>
    """
    # use these for making individual meshes for each prim face
    def __init__(self, *args):
        self.__init0__()
        if len(args):
            self.__initargs__(*args)

    def __init0__(self):
        self._coords = List(Coord);
        self._faces = List(Face);
        self._vertexNormals = List(Coord);
        self._calcVertexNormals = False
        self._us = List(float);
        self._faceUVs = List(UVCoord);
        self._faceNumbers = List(int);
        self._faceNormal = Coord(0.0, 0.0, 1.0)
        self._cutNormal1 = Coord()
        self._cutNormal2 = Coord()
        self._numOuterVerts = 0
        self._numHollowVerts = 0
        self._twoPi = 2.0 * math.pi
        self._errorMessage = None
        self._outerCoordIndices = None
        self._hollowCoordIndices = None
        self._cut1CoordIndices = None
        self._cut2CoordIndices = None
        self._bottomFaceNumber = 0
        self._numPrimFaces = 0

    def __getattr__(self, name):
        if not name.startswith('_'):
            return getattr(self, '_'+name)
        else:
            print("cant find",name)
            raise Exception()

    def _get_faces(self):
        return self._faces
    faces = property(_get_faces)
    def _get_coords(self):
        return self._coords
    coords = property(_get_coords)
    def _get_faceuvs(self):
        return self._faceUVs
    faceUVs = property(_get_faceuvs)

    def __initargs__(self, sides, profileStart, profileEnd, hollow, hollowSides, createFaces, calcVertexNormals):
        self._calcVertexNormals = calcVertexNormals
        center = Coord(0.0, 0.0, 0.0)
        #bool hasCenter = false;
        hollowCoords = List(Coord)
        hollowNormals = List(Coord)
        hollowUs = List(Single)
        if calcVertexNormals:
            self._outerCoordIndices = List(int)
            self._hollowCoordIndices = List(int)
            self._cut1CoordIndices = List(int)
            self._cut2CoordIndices = List(int)
        hasHollow = (hollow > 0.0)
        hasProfileCut = (profileStart > 0.0 or profileEnd < 1.0)
        angles = AngleList()
        hollowAngles = AngleList()
        xScale = 0.5
        yScale = 0.5
        if sides == 4: # corners of a square are sqrt(2) from center
            xScale = 0.707
            yScale = 0.707
        startAngle = profileStart * self._twoPi
        stopAngle = profileEnd * self._twoPi
        try:
            angles.makeAngles(sides, startAngle, stopAngle)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            self._errorMessage = "makeAngles failed: Exception: " + str(ex) + "\nsides: " + str(sides) + " startAngle: " + str(startAngle) + " stopAngle: " + str(stopAngle)
            return
        self._numOuterVerts = angles.angles.Count
        # flag to create as few triangles as possible for 3 or 4 side profile
        simpleFace = (sides < 5 and not hasHollow and not hasProfileCut)
        if hasHollow:
            if sides == hollowSides:
                hollowAngles = angles
            else:
                try:
                    hollowAngles.makeAngles(hollowSides, startAngle, stopAngle)
                except Exception as ex:
                    print(ex)
                    traceback.print_exc()
                    self._errorMessage = "makeAngles failed: Exception: " + str(ex) + "\nsides: " + str(sides) + " startAngle: " + str(startAngle) + " stopAngle: " + str(stopAngle)
                    return
            self._numHollowVerts = hollowAngles.angles.Count
        elif not simpleFace:
            self._coords.Add(center)
            #hasCenter = true;
            if self._calcVertexNormals:
                self._vertexNormals.Add(Coord(0.0, 0.0, 1.0))
            self._us.Add(0.0)
        z = 0.0
        newVert = Coord()
        if hasHollow and hollowSides != sides:
            numHollowAngles = hollowAngles.angles.Count
            i = 0
            while i < numHollowAngles:
                angle = hollowAngles.angles[i]
                newVert.X = hollow * xScale * angle.X
                newVert.Y = hollow * yScale * angle.Y
                newVert.Z = z
                hollowCoords.Add(newVert)
                if self._calcVertexNormals:
                    if hollowSides < 5:
                        hollowNormals.Add(hollowAngles.normals[i].Invert())
                    else:
                        hollowNormals.Add(Coord(-angle.X, -angle.Y, 0.0))
                    hollowUs.Add(angle.angle * hollow)
                i += 1
        index = 0
        numAngles = angles.angles.Count
        i = 0
        while i < numAngles:
            angle = angles.angles[i]
            newVert.X = angle.X * xScale
            newVert.Y = angle.Y * yScale
            newVert.Z = z
            self._coords.Add(newVert)
            if self._calcVertexNormals:
                self._outerCoordIndices.Add(self._coords.Count - 1)
                if sides < 5:
                    self._vertexNormals.Add(angles.normals[i])
                    u = angle.angle
                    self._us.Add(u)
                else:
                    self._vertexNormals.Add(Coord(angle.X, angle.Y, 0.0))
                    self._us.Add(angle.angle)
            if hasHollow:
                if hollowSides == sides:
                    newVert.X *= hollow
                    newVert.Y *= hollow
                    newVert.Z = z
                    hollowCoords.Add(newVert)
                    if self._calcVertexNormals:
                        if sides < 5:
                            hollowNormals.Add(angles.normals[i].Invert())
                        else:
                            hollowNormals.Add(Coord(-angle.X, -angle.Y, 0.0))
                        hollowUs.Add(angle.angle * hollow)
            elif not simpleFace and createFaces and angle.angle > 0.0001:
                newFace = Face()
                newFace.v1 = 0
                newFace.v2 = index
                newFace.v3 = index + 1
                self._faces.Add(newFace)
            index += 1
            i += 1
        if hasHollow:
            hollowCoords.Reverse()
            if self._calcVertexNormals:
                hollowNormals.Reverse()
                hollowUs.Reverse()
            if createFaces:
                #int numOuterVerts = this.coords.Count;
                #numOuterVerts = this.coords.Count;
                #int numHollowVerts = hollowCoords.Count;
                numTotalVerts = self._numOuterVerts + self._numHollowVerts
                if self._numOuterVerts == self._numHollowVerts:
                    newFace = Face()
                    coordIndex = 0
                    while coordIndex < self._numOuterVerts - 1:
                        newFace.v1 = coordIndex
                        newFace.v2 = coordIndex + 1
                        newFace.v3 = numTotalVerts - coordIndex - 1
                        self._faces.Add(newFace)
                        newFace.v1 = coordIndex + 1
                        newFace.v2 = numTotalVerts - coordIndex - 2
                        newFace.v3 = numTotalVerts - coordIndex - 1
                        self._faces.Add(newFace)
                        coordIndex += 1
                else:
                    if self._numOuterVerts < self._numHollowVerts:
                        newFace = Face()
                        j = 0 # j is the index for outer vertices
                        maxJ = self._numOuterVerts - 1
                        i = 0
                        while i < self._numHollowVerts: # i is the index for inner vertices
                            if j < maxJ:
                                if angles.angles[j + 1].angle - hollowAngles.angles[i].angle < hollowAngles.angles[i].angle - angles.angles[j].angle + 0.000001:
                                    newFace.v1 = numTotalVerts - i - 1
                                    newFace.v2 = j
                                    newFace.v3 = j + 1
                                    self._faces.Add(newFace)
                                    j += 1
                            newFace.v1 = j
                            newFace.v2 = numTotalVerts - i - 2
                            newFace.v3 = numTotalVerts - i - 1
                            self._faces.Add(newFace)
                            i += 1
                    else: # numHollowVerts < numOuterVerts
                        newFace = Face()
                        j = 0 # j is the index for inner vertices
                        maxJ = self._numHollowVerts - 1
                        i = 0
                        while i < self._numOuterVerts:
                            if j < maxJ:
                                if hollowAngles.angles[j + 1].angle - angles.angles[i].angle < angles.angles[i].angle - hollowAngles.angles[j].angle + 0.000001:
                                    newFace.v1 = i
                                    newFace.v2 = numTotalVerts - j - 2
                                    newFace.v3 = numTotalVerts - j - 1
                                    self._faces.Add(newFace)
                                    j += 1
                            newFace.v1 = numTotalVerts - j - 1
                            newFace.v2 = i
                            newFace.v3 = i + 1
                            self._faces.Add(newFace)
                            i += 1
            if calcVertexNormals:
                enumerator = hollowCoords.GetEnumerator()
                while enumerator.MoveNext():
                    hc = enumerator.Current
                    self._coords.Add(hc)
                    self._hollowCoordIndices.Add(self._coords.Count - 1)
            else:
                self._coords.AddRange(hollowCoords)
            if self._calcVertexNormals:
                self._vertexNormals.AddRange(hollowNormals)
                self._us.AddRange(hollowUs)
        if simpleFace and createFaces:
            if sides == 3:
                self._faces.Add(Face(0, 1, 2))
            elif sides == 4:
                self._faces.Add(Face(0, 1, 2))
                self._faces.Add(Face(0, 2, 3))
        if calcVertexNormals and hasProfileCut:
            lastOuterVertIndex = self._numOuterVerts - 1
            if hasHollow:
                self._cut1CoordIndices.Add(0)
                self._cut1CoordIndices.Add(self._coords.Count - 1)
                self._cut2CoordIndices.Add(lastOuterVertIndex + 1)
                self._cut2CoordIndices.Add(lastOuterVertIndex)
                self._cutNormal1.X = self._coords[0].Y - self._coords[self._coords.Count - 1].Y
                self._cutNormal1.Y = -(self._coords[0].X - self._coords[self._coords.Count - 1].X)
                self._cutNormal2.X = self._coords[lastOuterVertIndex + 1].Y - self._coords[lastOuterVertIndex].Y
                self._cutNormal2.Y = -(self._coords[lastOuterVertIndex + 1].X - self._coords[lastOuterVertIndex].X)
            else:
                self._cut1CoordIndices.Add(0)
                self._cut1CoordIndices.Add(1)
                self._cut2CoordIndices.Add(lastOuterVertIndex)
                self._cut2CoordIndices.Add(0)
                self._cutNormal1.X = self._vertexNormals[1].Y
                self._cutNormal1.Y = -self._vertexNormals[1].X
                self._cutNormal2.X = -self._vertexNormals[self._vertexNormals.Count - 2].Y
                self._cutNormal2.Y = self._vertexNormals[self._vertexNormals.Count - 2].X
            self._cutNormal1.Normalize()
            self._cutNormal2.Normalize()
        self.MakeFaceUVs()
        hollowCoords = None
        hollowNormals = None
        hollowUs = None
        if calcVertexNormals: # calculate prim face numbers
            # face number order is top, outer, hollow, bottom, start cut, end cut
            # I know it's ugly but so is the whole concept of prim face numbers
            faceNum = 1 # start with outer faces
            if hasProfileCut and not hasHollow:
                startVert = 1
            else:
                startVert = 0
            if startVert > 0:
                self._faceNumbers.Add(-1)
            i = 0
            while i < self._numOuterVerts - 1:
                self._faceNumbers.Add(faceNum)
                if sides < 5 and i < sides:
                    faceNum += 1
                i += 1
            #if (!hasHollow && !hasProfileCut)
            #    this.bottomFaceNumber = faceNum++;
            if hasProfileCut:
                self._faceNumbers.Add(-1)
            else:
                self._faceNumbers.Add(faceNum)
                faceNum += 1
            if sides > 4 and (hasHollow or hasProfileCut):
                faceNum += 1
            if sides < 5 and (hasHollow or hasProfileCut) and self._numOuterVerts < sides:
                faceNum += 1
            if hasHollow:
                i = 0
                while i < self._numHollowVerts:
                    self._faceNumbers.Add(faceNum)
                    i += 1
                self._hollowFaceNumber = faceNum
                faceNum += 1
            #if (hasProfileCut || hasHollow)
            #    this.bottomFaceNumber = faceNum++;
            self._bottomFaceNumber = faceNum
            faceNum += 1
            if hasHollow and hasProfileCut:
                self._faceNumbers.Add(faceNum)
                faceNum += 1
            i = 0
            while i < self._faceNumbers.Count:
                if self._faceNumbers[i] == -1:
                    self._faceNumbers[i] = faceNum
                    faceNum += 1
                i += 1
            self._numPrimFaces = faceNum

    def MakeFaceUVs(self):
        self._faceUVs = List(UVCoord)
        enumerator = self._coords.GetEnumerator()
        while enumerator.MoveNext():
            c = enumerator.Current
            self._faceUVs.Add(UVCoord(0.5 + c.X, 0.5 - c.Y))

    def Copy(self, needFaces=True):
        copy = Profile()
        copy._coords.AddRange(self._coords)
        copy._faceUVs.AddRange(self._faceUVs)
        if needFaces:
            copy._faces.AddRange(self._faces)
        copy._calcVertexNormals = self._calcVertexNormals
        if copy._calcVertexNormals == True:
            copy._vertexNormals.AddRange(self._vertexNormals)
            copy._faceNormal = self._faceNormal
            copy._cutNormal1 = self._cutNormal1
            copy._cutNormal2 = self._cutNormal2
            copy._us.AddRange(self._us)
            copy._faceNumbers.AddRange(self._faceNumbers)
            copy._cut1CoordIndices = List(int, self._cut1CoordIndices)
            copy._cut2CoordIndices = List(int, self._cut2CoordIndices)
            copy._hollowCoordIndices = List(int, self._hollowCoordIndices)
            copy._outerCoordIndices = List(int, self._outerCoordIndices)
        copy._numOuterVerts = self._numOuterVerts
        copy._numHollowVerts = self._numHollowVerts
        return copy

    def AddPos(self, *args):
        if len(args) == 3:
            self.AddPos3(*args)
        else:
            self.AddPos1(*args)

    def AddPos1(self, v):
        self.AddPos(v.X, v.Y, v.Z)

    def AddPos3(self, x, y, z):
        numVerts = self._coords.Count
        i = 0
        while i < numVerts:
            vert = self._coords[i]
            vert.X += x
            vert.Y += y
            vert.Z += z
            self._coords[i] = vert
            i += 1

    def AddRot(self, q):
        numVerts = self._coords.Count
        i = 0
        while i < numVerts:
            self._coords[i] *= q
            i += 1
        if self._calcVertexNormals:
            numNormals = self._vertexNormals.Count
            i = 0
            while i < numNormals:
                self._vertexNormals[i] *= q
                i += 1
            self._faceNormal *= q
            self._cutNormal1 *= q
            self._cutNormal2 *= q

    def Scale(self, x, y):
        numVerts = self._coords.Count
        i = 0
        while i < numVerts:
            vert = self._coords[i]
            vert.X *= x
            vert.Y *= y
            self._coords[i] = vert
            i += 1

    def FlipNormals(self):
        """ <summary>
         Changes order of the vertex indices and negates the center vertex normal. Does not alter vertex normals of radial vertices
         </summary>
        """
        numFaces = self._faces.Count
        i = 0
        while i < numFaces:
            tmpFace = self._faces[i]
            tmp = tmpFace.v3
            tmpFace.v3 = tmpFace.v1
            tmpFace.v1 = tmp
            self._faces[i] = tmpFace
            i += 1
        if self._calcVertexNormals:
            normalCount = self._vertexNormals.Count
            if normalCount > 0:
                n = self._vertexNormals[normalCount - 1]
                n.Z = -n.Z
                self._vertexNormals[normalCount - 1] = n
        self._faceNormal.X = -self._faceNormal.X
        self._faceNormal.Y = -self._faceNormal.Y
        self._faceNormal.Z = -self._faceNormal.Z
        numfaceUVs = self._faceUVs.Count
        i = 0
        while i < numfaceUVs:
            uv = self._faceUVs[i]
            uv.V = 1.0 - uv.V
            i += 1

    def AddValue2aceVertexIndices(self, num):
        numFaces = self._faces.Count
        i = 0
        while i < numFaces:
            tmpFace = self._faces[i]
            tmpFace.v1 += num
            tmpFace.v2 += num
            tmpFace.v3 += num
            i += 1

    def AddValue2aceNormalIndices(self, num):
        if self._calcVertexNormals:
            numFaces = self._faces.Count
            i = 0
            while i < numFaces:
                tmpFace = self._faces[i]
                tmpFace.n1 += num
                tmpFace.n2 += num
                tmpFace.n3 += num
                i += 1

    def DumpRaw(self, path, name, title):
        if path == None:
            return
        fileName = name + "_" + title + ".raw"
        completePath = System.IO.Path.Combine(path, fileName)
        sw = StreamWriter(completePath)
        i = 0
        while i < self._faces.Count:
            s = self._coords[self._faces[i].v1].ToString()
            s += " " + self._coords[self._faces[i].v2].ToString()
            s += " " + self._coords[self._faces[i].v3].ToString()
            sw.WriteLine(s)
            i += 1
        sw.Close()

class PathNode(object):
    def __init__(self):
        pass

class PathType(object):
    Linear = 0
    Circular = 1
    Flexible = 2

class Path(object):
    def __init__(self):
        self._pathNodes = List(PathNode)
        self._twistBegin = 0.0
        self._twistEnd = 0.0
        self._topShearX = 0.0
        self._topShearY = 0.0
        self._pathCutBegin = 0.0
        self._pathCutEnd = 1.0
        self._dimpleBegin = 0.0
        self._dimpleEnd = 1.0
        self._skew = 0.0
        self._holeSizeX = 1.0 # called pathScaleX in pbs
        self._holeSizeY = 0.25
        self._taperX = 0.0
        self._taperY = 0.0
        self._radius = 0.0
        self._revolutions = 1.0
        self._stepsPerRevolution = 24
        self._twoPi = 2.0 * math.pi

    def _get_pathNodes(self):
        return self._pathNodes

    pathNodes = property(_get_pathNodes)

    def Create(self, pathType, steps):
        if pathType == PathType.Linear or pathType == PathType.Flexible:
            step = 0
            length = self._pathCutEnd - self._pathCutBegin
            twistTotal = self._twistEnd - self._twistBegin
            twistTotalAbs = abs(twistTotal)
            if twistTotalAbs > 0.01:
                steps += int(twistTotalAbs * 3.66) #  dahlia's magic number
            start = -0.5
            stepSize = length / steps
            percentOfPathMultiplier = stepSize
            xOffset = 0.0
            yOffset = 0.0
            zOffset = start
            xOffsetStepIncrement = self._topShearX / steps
            yOffsetStepIncrement = self._topShearY / steps
            percentOfPath = self._pathCutBegin
            zOffset += percentOfPath
            # sanity checks
            done = False
            while not done:
                newNode = PathNode()
                newNode.xScale = 1.0
                if self._taperX == 0.0:
                    newNode.xScale = 1.0
                elif self._taperX > 0.0:
                    newNode.xScale = 1.0 - percentOfPath * self._taperX
                else:
                    newNode.xScale = 1.0 + (1.0 - percentOfPath) * self._taperX
                newNode.yScale = 1.0
                if self._taperY == 0.0:
                    newNode.yScale = 1.0
                elif self._taperY > 0.0:
                    newNode.yScale = 1.0 - percentOfPath * self._taperY
                else:
                    newNode.yScale = 1.0 + (1.0 - percentOfPath) * self._taperY
                twist = self._twistBegin + twistTotal * percentOfPath
                newNode.rotation = Quat(Coord(0.0, 0.0, 1.0), twist)
                newNode.position = Coord(xOffset, yOffset, zOffset)
                newNode.percentOfPath = percentOfPath
                self._pathNodes.Add(newNode)
                if step < steps:
                    step += 1
                    percentOfPath += percentOfPathMultiplier
                    xOffset += xOffsetStepIncrement
                    yOffset += yOffsetStepIncrement
                    zOffset += stepSize
                    if percentOfPath > self._pathCutEnd:
                        done = True
                else:
                    done = True
        else: # end of linear path code # pathType == Circular
            twistTotal = self._twistEnd - self._twistBegin
            # if the profile has a lot of twist, add more layers otherwise the layers may overlap
            # and the resulting mesh may be quite inaccurate. This method is arbitrary and doesn't
            # accurately match the viewer
            twistTotalAbs = abs(twistTotal)
            if twistTotalAbs > 0.01:
                if twistTotalAbs > math.pi * 1.5:
                    steps *= 2
                if twistTotalAbs > math.pi * 3.0:
                    steps *= 2
            yPathScale = self._holeSizeY * 0.5
            pathLength = self._pathCutEnd - self._pathCutBegin
            totalSkew = self._skew * 2.0 * pathLength
            skewStart = self._pathCutBegin * 2.0 * self._skew - self._skew
            xOffsetTopShearXFactor = self._topShearX * (0.25 + 0.5 * (0.5 - self._holeSizeY))
            yShearCompensation = 1.0 + abs(self._topShearY) * 0.25
            # It's not quite clear what pushY (Y top shear) does, but subtracting it from the start and end
            # angles appears to approximate it's effects on path cut. Likewise, adding it to the angle used
            # to calculate the sine for generating the path radius appears to approximate it's effects there
            # too, but there are some subtle differences in the radius which are noticeable as the prim size
            # increases and it may affect megaprims quite a bit. The effect of the Y top shear parameter on
            # the meshes generated with this technique appear nearly identical in shape to the same prims when
            # displayed by the viewer.
            startAngle = (self._twoPi * self._pathCutBegin * self._revolutions) - self._topShearY * 0.9
            endAngle = (self._twoPi * self._pathCutEnd * self._revolutions) - self._topShearY * 0.9
            stepSize = self._twoPi / float(self._stepsPerRevolution)
            step = int(startAngle / stepSize)
            angle = startAngle
            done = False
            while not done: # loop through the length of the path and add the layers
                newNode = PathNode()
                xProfileScale = (1.0 - abs(self._skew)) * self._holeSizeX
                yProfileScale = self._holeSizeY
                percentOfPath = angle / (self._twoPi * self._revolutions)
                percentOfAngles = (angle - startAngle) / (endAngle - startAngle)
                if self._taperX > 0.01:
                    xProfileScale *= 1.0 - percentOfPath * self._taperX
                elif self._taperX < -0.01:
                    xProfileScale *= 1.0 + (1.0 - percentOfPath) * self._taperX
                if self._taperY > 0.01:
                    yProfileScale *= 1.0 - percentOfPath * self._taperY
                elif self._taperY < -0.01:
                    yProfileScale *= 1.0 + (1.0 - percentOfPath) * self._taperY
                newNode.xScale = xProfileScale
                newNode.yScale = yProfileScale
                radiusScale = 1.0
                if self._radius > 0.001:
                    radiusScale = 1.0 - self._radius * percentOfPath
                elif self._radius < 0.001:
                    radiusScale = 1.0 + self._radius * (1.0 - percentOfPath)
                twist = self._twistBegin + twistTotal * percentOfPath
                xOffset = 0.5 * (skewStart + totalSkew * percentOfAngles)
                xOffset += math.sin(angle) * xOffsetTopShearXFactor
                yOffset = yShearCompensation * math.cos(angle) * (0.5 - yPathScale) * radiusScale
                zOffset = math.sin(angle + self._topShearY) * (0.5 - yPathScale) * radiusScale
                newNode.position = Coord(xOffset, yOffset, zOffset)
                # now orient the rotation of the profile layer relative to it's position on the path
                # adding taperY to the angle used to generate the quat appears to approximate the viewer
                newNode.rotation = Quat(Coord(1.0, 0.0, 0.0), angle + self._topShearY)
                # next apply twist rotation to the profile layer
                if twistTotal != 0.0 or self._twistBegin != 0.0:
                    newNode.rotation *= Quat(Coord(0.0, 0.0, 1.0), twist)
                newNode.percentOfPath = percentOfPath
                self._pathNodes.Add(newNode)
                # calculate terms for next iteration
                # calculate the angle for the next iteration of the loop
                if angle >= endAngle - 0.01:
                    done = True
                else:
                    step += 1
                    angle = stepSize * step
                    if angle > endAngle:
                        angle = endAngle

class PrimMesh(object): # called pathScaleX in pbs
    def ParamsToDisplayString(self):
        """ <summary>
         Human readable string representation of the parameters used to create a mesh.
         </summary>
         <returns></returns>
        """
        s = ""
        s += "sides..................: " + str(self._sides)
        s += "\nhollowSides..........: " + str(self._hollowSides)
        s += "\nprofileStart.........: " + str(self._profileStart)
        s += "\nprofileEnd...........: " + str(self._profileEnd)
        s += "\nhollow...............: " + str(self._hollow)
        s += "\ntwistBegin...........: " + str(self._twistBegin)
        s += "\ntwistEnd.............: " + str(self._twistEnd)
        s += "\ntopShearX............: " + str(self._topShearX)
        s += "\ntopShearY............: " + str(self._topShearY)
        s += "\npathCutBegin.........: " + str(self._pathCutBegin)
        s += "\npathCutEnd...........: " + str(self._pathCutEnd)
        s += "\ndimpleBegin..........: " + str(self._dimpleBegin)
        s += "\ndimpleEnd............: " + str(self._dimpleEnd)
        s += "\nskew.................: " + str(self._skew)
        s += "\nholeSizeX............: " + str(self._holeSizeX)
        s += "\nholeSizeY............: " + str(self._holeSizeY)
        s += "\ntaperX...............: " + str(self._taperX)
        s += "\ntaperY...............: " + str(self._taperY)
        s += "\nradius...............: " + str(self._radius)
        s += "\nrevolutions..........: " + str(self._revolutions)
        s += "\nstepsPerRevolution...: " + str(self._stepsPerRevolution)
        return s

    def __init__(self, sides, profileStart, profileEnd, hollow, hollowSides):
        """ <summary>
         Constructs a PrimMesh object and creates the profile for extrusion.
         </summary>
         <param name="sides"></param>
         <param name="profileStart"></param>
         <param name="profileEnd"></param>
         <param name="hollow"></param>
         <param name="hollowSides"></param>
        """
        self._errorMessage = ""
        self._twoPi = 2.0 * math.pi
        self._sides = 4
        self._hollowSides = 4
        self._profileStart = 0.0
        self._profileEnd = 1.0
        self._hollow = 0.0
        self._twistBegin = 0
        self._twistEnd = 0
        self._topShearX = 0.0
        self._topShearY = 0.0
        self._pathCutBegin = 0.0
        self._pathCutEnd = 1.0
        self._dimpleBegin = 0.0
        self._dimpleEnd = 1.0
        self._skew = 0.0
        self._holeSizeX = 1.0
        self._holeSizeY = 0.25
        self._taperX = 0.0
        self._taperY = 0.0
        self._radius = 0.0
        self._revolutions = 1.0
        self._stepsPerRevolution = 24
        self._hasProfileCut = False
        self._hasHollow = False
        self._calcVertexNormals = False
        self._normalsProcessed = False
        self._viewerMode = False
        self._numPrimFaces = 0
        self._coords = List(Coord)
        self._faces = List(Face)
        self._sides = sides
        self._profileStart = profileStart
        self._profileEnd = profileEnd
        self._hollow = hollow
        self._hollowSides = hollowSides
        if sides < 3:
            self._sides = 3
        if hollowSides < 3:
            self._hollowSides = 3
        if profileStart < 0.0:
            self._profileStart = 0.0
        if profileEnd > 1.0:
            self._profileEnd = 1.0
        if profileEnd < 0.02:
            self._profileEnd = 0.02
        if profileStart >= profileEnd:
            self._profileStart = profileEnd - 0.02
        if hollow > 0.99:
            self._hollow = 0.99
        if hollow < 0.0:
            self._hollow = 0.0
        self._hasProfileCut = (self._profileStart > 0.0 or self._profileEnd < 1.0)
        self._hasHollow = (self._hollow > 0.001)

    def Extrude(self, pathType):
        """ <summary>
         Extrudes a profile along a path.
         </summary>
        """
        needEndFaces = False
        self._coords = List(Coord)
        self._faces = List(Face)
        if self._viewerMode:
            self._viewerFaces = List(ViewerFace)
            self._calcVertexNormals = True
        if self._calcVertexNormals:
            self._normals = List(Coord)
        steps = 1
        length = self._pathCutEnd - self._pathCutBegin
        self._normalsProcessed = False
        if self._viewerMode and self._sides == 3:
            # prisms don't taper well so add some vertical resolution
            # other prims may benefit from this but just do prisms for now
            if abs(self._taperX) > 0.01 or abs(self._taperY) > 0.01:
                steps = int(steps * 4.5 * length)
        twistBegin = self._twistBegin / 360.0 * self._twoPi
        twistEnd = self._twistEnd / 360.0 * self._twoPi
        twistTotal = self._twistEnd - self._twistBegin
        twistTotalAbs = abs(twistTotal)
        if twistTotalAbs > 0.01:
            steps += int(twistTotalAbs * 3.66) #  dahlia's magic number
        hollow = self._hollow
        # sanity checks
        initialProfileRot = 0.0
        if pathType == PathType.Circular:
            if self._sides == 3:
                initialProfileRot = math.pi
                if self._hollowSides == 4:
                    if hollow > 0.7:
                        hollow = 0.7
                    hollow *= 0.707
                else:
                    hollow *= 0.5
            elif self._sides == 4:
                initialProfileRot = 0.25 * math.pi
                if self._hollowSides != 4:
                    hollow *= 0.707
            elif self._sides > 4:
                initialProfileRot = math.pi
                if self._hollowSides == 4:
                    if hollow > 0.7:
                        hollow = 0.7
                    hollow /= 0.7
        else:
            if self._sides == 3:
                if self._hollowSides == 4:
                    if hollow > 0.7:
                        hollow = 0.7
                    hollow *= 0.707
                else:
                    hollow *= 0.5
            elif self._sides == 4:
                initialProfileRot = 1.25 * math.pi
                if self._hollowSides != 4:
                    hollow *= 0.707
            elif self._sides == 24 and self._hollowSides == 4:
                hollow *= 1.414
        profile = Profile(self._sides, self._profileStart, self._profileEnd, hollow, self._hollowSides, True, self._calcVertexNormals)
        self._errorMessage = profile._errorMessage
        self._numPrimFaces = profile._numPrimFaces

        cut1Vert = -1
        cut2Vert = -1
        if self._hasProfileCut:
            cut1Vert = profile.coords.Count - 1 if self._hasHollow else 0
            cut2Vert = profile.numOuterVerts - 1 if self._hasHollow else profile.numOuterVerts
        if initialProfileRot != 0.0:
            profile.AddRot(Quat(Coord(0.0, 0.0, 1.0), initialProfileRot))
            if self._viewerMode:
                profile.MakeFaceUVs()
        lastCutNormal1 = Coord()
        lastCutNormal2 = Coord()
        lastV = 1.0
        path = Path()
        path._twistBegin = self._twistBegin
        path._twistEnd = self._twistEnd
        path._topShearX = self._topShearX
        path._topShearY = self._topShearY
        path._pathCutBegin = self._pathCutBegin
        path._pathCutEnd = self._pathCutEnd
        path._dimpleBegin = self._dimpleBegin
        path._dimpleEnd = self._dimpleEnd
        path._skew = self._skew
        path._holeSizeX = self._holeSizeX
        path._holeSizeY = self._holeSizeY
        path._taperX = self._taperX
        path._taperY = self._taperY
        path._radius = self._radius
        path._revolutions = self._revolutions
        path._stepsPerRevolution = self._stepsPerRevolution
        path.Create(pathType, steps)
        needEndFaces = False
        if pathType == PathType.Circular:
            needEndFaces = False
            if self._pathCutBegin != 0.0 or self._pathCutEnd != 1.0:
                needEndFaces = True
            elif self._taperX != 0.0 or self._taperY != 0.0:
                needEndFaces = True
            elif self._skew != 0.0:
                needEndFaces = True
            elif twistTotal != 0.0:
                needEndFaces = True
            elif self._radius != 0.0:
                needEndFaces = True
        else:
            needEndFaces = True
        nodeIndex = 0
        while nodeIndex < path.pathNodes.Count:
            node = path.pathNodes[nodeIndex]
            newLayer = profile.Copy()
            newLayer.Scale(node.xScale, node.yScale)
            newLayer.AddRot(node.rotation)
            newLayer.AddPos(node.position)
            if needEndFaces and nodeIndex == 0:
                newLayer.FlipNormals()
                # add the top faces to the viewerFaces list here
                if self._viewerMode:
                    faceNormal = newLayer.faceNormal
                    newViewerFace = ViewerFace(profile.bottomFaceNumber)
                    numFaces = newLayer.faces.Count
                    faces = newLayer.faces
                    i = 0
                    while i < numFaces:
                        newViewerFace = ViewerFace(profile.bottomFaceNumber)
                        face = faces[i]
                        #print(len(newLayer.coords), face.v3, len(profile.coords), i, numFaces)
                        newViewerFace.v1 = newLayer.coords[face.v1]
                        newViewerFace.v2 = newLayer.coords[face.v2]
                        newViewerFace.v3 = newLayer.coords[face.v3]
                        newViewerFace.coordIndex1 = face.v1
                        newViewerFace.coordIndex2 = face.v2
                        newViewerFace.coordIndex3 = face.v3
                        newViewerFace.n1 = faceNormal
                        newViewerFace.n2 = faceNormal
                        newViewerFace.n3 = faceNormal
                        newViewerFace.uv1 = newLayer.faceUVs[face.v1]
                        newViewerFace.uv2 = newLayer.faceUVs[face.v2]
                        newViewerFace.uv3 = newLayer.faceUVs[face.v3]
                        self._viewerFaces.Add(newViewerFace)
                        i += 1 # if (nodeIndex == 0)
            # append this layer
            coordsLen = self._coords.Count
            newLayer.AddValue2aceVertexIndices(coordsLen)
            self._coords.AddRange(newLayer.coords)
            if self._calcVertexNormals:
                newLayer.AddValue2aceNormalIndices(self._normals.Count)
                self._normals.AddRange(newLayer.vertexNormals)
            if node.percentOfPath < self._pathCutBegin + 0.01 or node.percentOfPath > self._pathCutEnd - 0.01:
                self._faces.AddRange(newLayer.faces)
            # fill faces between layers
            numVerts = newLayer.coords.Count
            newFace = Face()
            if nodeIndex > 0:
                startVert = coordsLen + 1
                endVert = self._coords.Count
                if self._sides < 5 or self._hasProfileCut or hollow > 0.0:
                    startVert -= 1
                i = startVert
                while i < endVert:
                    iNext = i + 1
                    if i == endVert - 1:
                        iNext = startVert
                    whichVert = i - startVert
                    newFace.v1 = i
                    newFace.v2 = i - numVerts
                    newFace.v3 = iNext - numVerts
                    self._faces.Add(newFace)
                    newFace.v2 = iNext - numVerts
                    newFace.v3 = iNext
                    self._faces.Add(newFace)
                    if self._viewerMode:
                        # add the side faces to the list of viewerFaces here
                        primFaceNum = profile.faceNumbers[whichVert]
                        if not needEndFaces:
                            primFaceNum -= 1
                        newViewerFace1 = ViewerFace(primFaceNum)
                        newViewerFace2 = ViewerFace(primFaceNum)
                        u1 = newLayer.us[whichVert]
                        u2 = 1.0
                        if whichVert < newLayer.us.Count - 1:
                            u2 = newLayer.us[whichVert + 1]
                        if whichVert == cut1Vert or whichVert == cut2Vert:
                            u1 = 0.0
                            u2 = 1.0
                        elif self._sides < 5:
                            if whichVert < profile.numOuterVerts: # boxes and prisms have one texture face per side of the prim, so the U values have to be scaled
                                # to reflect the entire texture width
                                u1 *= self._sides
                                u2 *= self._sides
                                u2 -= u1
                                u1 -= u1
                                if u2 < 0.1:
                                    u2 = 1.0
                            elif whichVert > profile.coords.Count - profile.numHollowVerts - 1:
                                u1 *= 2.0
                                u2 *= 2.0
                        newViewerFace1.uv1.U = u1
                        newViewerFace1.uv2.U = u1
                        newViewerFace1.uv3.U = u2
                        newViewerFace1.uv1.V = 1.0 - node.percentOfPath
                        newViewerFace1.uv2.V = lastV
                        newViewerFace1.uv3.V = lastV
                        newViewerFace2.uv1.U = u1
                        newViewerFace2.uv2.U = u2
                        newViewerFace2.uv3.U = u2
                        newViewerFace2.uv1.V = 1.0 - node.percentOfPath
                        newViewerFace2.uv2.V = lastV
                        newViewerFace2.uv3.V = 1.0 - node.percentOfPath
                        newViewerFace1.v1 = self._coords[i]
                        newViewerFace1.v2 = self._coords[i - numVerts]
                        newViewerFace1.v3 = self._coords[iNext - numVerts]
                        newViewerFace2.v1 = self._coords[i]
                        newViewerFace2.v2 = self._coords[iNext - numVerts]
                        newViewerFace2.v3 = self._coords[iNext]
                        newViewerFace1.coordIndex1 = i
                        newViewerFace1.coordIndex2 = i - numVerts
                        newViewerFace1.coordIndex3 = iNext - numVerts
                        newViewerFace2.coordIndex1 = i
                        newViewerFace2.coordIndex2 = iNext - numVerts
                        newViewerFace2.coordIndex3 = iNext
                        # profile cut faces
                        if whichVert == cut1Vert:
                            newViewerFace1.n1 = newLayer.cutNormal1
                            newViewerFace1.n2 = newViewerFace1.n3 = lastCutNormal1
                            newViewerFace2.n1 = newViewerFace2.n3 = newLayer.cutNormal1
                            newViewerFace2.n2 = lastCutNormal1
                        elif whichVert == cut2Vert:
                            newViewerFace1.n1 = newLayer.cutNormal2
                            newViewerFace1.n2 = newViewerFace1.n3 = lastCutNormal2
                            newViewerFace2.n1 = newViewerFace2.n3 = newLayer.cutNormal2
                            newViewerFace2.n2 = lastCutNormal2
                        else: # outer and hollow faces
                            if (self._sides < 5 and whichVert < newLayer.numOuterVerts) or (self._hollowSides < 5 and whichVert >= newLayer.numOuterVerts): # looks terrible when path is twisted... need vertex normals here
                                newViewerFace1.CalcSurfaceNormal()
                                newViewerFace2.CalcSurfaceNormal()
                            else:
                                newViewerFace1.n1 = self._normals[i]
                                newViewerFace1.n2 = self._normals[i - numVerts]
                                newViewerFace1.n3 = self._normals[iNext - numVerts]
                                newViewerFace2.n1 = self._normals[i]
                                newViewerFace2.n2 = self._normals[iNext - numVerts]
                                newViewerFace2.n3 = self._normals[iNext]
                        self._viewerFaces.Add(newViewerFace1)
                        self._viewerFaces.Add(newViewerFace2)
                    i += 1
            lastCutNormal1 = newLayer.cutNormal1
            lastCutNormal2 = newLayer.cutNormal2
            lastV = 1.0 - node.percentOfPath
            if needEndFaces and nodeIndex == (path.pathNodes.Count - 1) and self._viewerMode:
                # add the top faces to the viewerFaces list here
                faceNormal = newLayer.faceNormal
                newViewerFace = ViewerFace(0)
                numFaces = newLayer.faces.Count
                faces = newLayer.faces
                i = 0
                while i < numFaces:
                    newViewerFace = ViewerFace(0)
                    face = faces[i]
                    newViewerFace.v1 = newLayer.coords[face.v1 - coordsLen]
                    newViewerFace.v2 = newLayer.coords[face.v2 - coordsLen]
                    newViewerFace.v3 = newLayer.coords[face.v3 - coordsLen]
                    newViewerFace.coordIndex1 = face.v1
                    newViewerFace.coordIndex2 = face.v2
                    newViewerFace.coordIndex3 = face.v3
                    newViewerFace.n1 = faceNormal
                    newViewerFace.n2 = faceNormal
                    newViewerFace.n3 = faceNormal
                    newViewerFace.uv1 = newLayer.faceUVs[face.v1 - coordsLen]
                    newViewerFace.uv2 = newLayer.faceUVs[face.v2 - coordsLen]
                    newViewerFace.uv3 = newLayer.faceUVs[face.v3 - coordsLen]
                    self._viewerFaces.Add(newViewerFace)
                    i += 1
            nodeIndex += 1
 # for (int nodeIndex = 0; nodeIndex < path.pathNodes.Count; nodeIndex++)
    def ExtrudeLinear(self):
        """ <summary>
         DEPRICATED - use Extrude(PathType.Linear) instead
         Extrudes a profile along a straight line path. Used for prim types box, cylinder, and prism.
         </summary>

        """
        self.Extrude(PathType.Linear)

    def ExtrudeCircular(self):
        """ <summary>
         DEPRICATED - use Extrude(PathType.Circular) instead
         Extrude a profile into a circular path prim mesh. Used for prim types torus, tube, and ring.
         </summary>

        """
        self.Extrude(PathType.Circular)

    def SurfaceNormal(self, c1, c2, c3):
        edge1 = Coord(c2.X - c1.X, c2.Y - c1.Y, c2.Z - c1.Z)
        edge2 = Coord(c3.X - c1.X, c3.Y - c1.Y, c3.Z - c1.Z)
        normal = Coord.Cross(edge1, edge2)
        normal.Normalize()
        return normal

    def SurfaceNormal(self, face):
        return self.SurfaceNormal(self._coords[face.v1], self._coords[face.v2], self._coords[face.v3])

    def SurfaceNormal(self, faceIndex):
        """ <summary>
         Calculate the surface normal for a face in the list of faces
         </summary>
         <param name="faceIndex"></param>
         <returns></returns>
        """
        numFaces = self._faces.Count
        if faceIndex < 0 or faceIndex >= numFaces:
            raise Exception("faceIndex out of range")
        return self.SurfaceNormal(self._faces[faceIndex])

    def Copy(self):
        """ <summary>
         Duplicates a PrimMesh object. All object properties are copied by value, including lists.
         </summary>
         <returns></returns>
        """
        copy = PrimMesh(self._sides, self._profileStart, self._profileEnd, self._hollow, self._hollowSides)
        copy._twistBegin = self._twistBegin
        copy._twistEnd = self._twistEnd
        copy._topShearX = self._topShearX
        copy._topShearY = self._topShearY
        copy._pathCutBegin = self._pathCutBegin
        copy._pathCutEnd = self._pathCutEnd
        copy._dimpleBegin = self._dimpleBegin
        copy._dimpleEnd = self._dimpleEnd
        copy._skew = self._skew
        copy._holeSizeX = self._holeSizeX
        copy._holeSizeY = self._holeSizeY
        copy._taperX = self._taperX
        copy._taperY = self._taperY
        copy._radius = self._radius
        copy._revolutions = self._revolutions
        copy._stepsPerRevolution = self._stepsPerRevolution
        copy._calcVertexNormals = self._calcVertexNormals
        copy._normalsProcessed = self._normalsProcessed
        copy._viewerMode = self._viewerMode
        copy._numPrimFaces = self._numPrimFaces
        copy._errorMessage = self._errorMessage
        copy._coords = List(Coord, self._coords)
        copy._faces = List(Face, self._faces)
        copy._viewerFaces = List(ViewerFace, self._viewerFaces)
        copy._normals = List(Coord, self._normals)
        return copy

    def CalcNormals(self):
        """ <summary>
         Calculate surface normals for all of the faces in the list of faces in this mesh
         </summary>
        """
        if self._normalsProcessed:
            return
        self._normalsProcessed = True
        numFaces = self._faces.Count
        if not self._calcVertexNormals:
            self._normals = List(Coord)
        i = 0
        while i < numFaces:
            face = self._faces[i]
            self._normals.Add(self.SurfaceNormal(i).Normalize())
            normIndex = self._normals.Count - 1
            face.n1 = normIndex
            face.n2 = normIndex
            face.n3 = normIndex
            self._faces[i] = face
            i += 1

    def AddPos(self, x, y, z):
        """ <summary>
         Adds a value to each XYZ vertex coordinate in the mesh
         </summary>
         <param name="x"></param>
         <param name="y"></param>
         <param name="z"></param>
        """
        numVerts = self._coords.Count
        i = 0
        while i < numVerts:
            vert = self._coords[i]
            vert.X += self.x
            vert.Y += self.y
            vert.Z += self.z
            self._coords[i] = vert
            i += 1
        if self._viewerFaces != None:
            numViewerFaces = self._viewerFaces.Count
            i = 0
            while i < numViewerFaces:
                v = self._viewerFaces[i]
                v.AddPos(x, y, z)
                self._viewerFaces[i] = v
                i += 1

    def AddRot(self, q):
        """ <summary>
         Rotates the mesh
         </summary>
         <param name="q"></param>
        """
        numVerts = self._coords.Count
        i = 0
        while i < numVerts:
            self._coords[i] *= q
            i += 1
        if self._normals != None:
            numNormals = self._normals.Count
            i = 0
            while i < numNormals:
                self._normals[i] *= q
                i += 1
        if self._viewerFaces != None:
            numViewerFaces = self._viewerFaces.Count
            i = 0
            while i < numViewerFaces:
                v = self._viewerFaces[i]
                v.v1 *= q
                v.v2 *= q
                v.v3 *= q
                v.n1 *= q
                v.n2 *= q
                v.n3 *= q
                self._viewerFaces[i] = v
                i += 1

    def GetVertexIndexer(self):
        if self._viewerMode and self._viewerFaces.Count > 0:
            return VertexIndexer(self)
        return None

    def Scale(self, x, y, z):
        """ <summary>
         Scales the mesh
         </summary>
         <param name="x"></param>
         <param name="y"></param>
         <param name="z"></param>
        """
        numVerts = self._coords.Count
        #Coord vert;
        m = Coord(x, y, z)
        i = 0
        while i < numVerts:
            self._coords[i] *= m
            i += 1
        if self._viewerFaces != None:
            numViewerFaces = self._viewerFaces.Count
            i = 0
            while i < numViewerFaces:
                v = self._viewerFaces[i]
                v.v1 *= m
                v.v2 *= m
                v.v3 *= m
                self._viewerFaces[i] = v
                i += 1

    def DumpRaw(self, path, name, title):
        """ <summary>
         Dumps the mesh to a Blender compatible "Raw" format file
         </summary>
         <param name="path"></param>
         <param name="name"></param>
         <param name="title"></param>
        """
        if path == None:
            return
        fileName = name + "_" + title + ".raw"
        completePath = os.path.join(path, fileName)
        sw = open(completePath, "w")
        i = 0
        while i < self._faces.Count:
            s = self._coords[self._faces[i].v1].ToString()
            s += " " + self._coords[self._faces[i].v2].ToString()
            s += " " + self._coords[self._faces[i].v3].ToString()
            sw.write(s+"\n")
            i += 1
        sw.close()

if __name__ == "__main__":
    sides = 3
    profileStart = 0.0
    profileEnd = 0.6
    hollow = 0.0
    hollowSides = 3
    p = PrimMesh(sides, profileStart, profileEnd, hollow, hollowSides)
    p._viewerMode = True
    p._radius = 2.0
    p._skew = 0.81
    p._hollow = 0.0
    p._holeSizeX = 0.05
    p._dimpleEnd = 0.0
    p._holeSizeY = 0.05
    p._stepsPerRevolution = 1
    p.Extrude(PathType.Circular)
    p.DumpRaw('/tmp', 'test', 'test')
    print(p.ParamsToDisplayString())
