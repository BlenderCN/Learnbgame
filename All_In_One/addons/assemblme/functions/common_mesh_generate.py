# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import math
import numpy as np

# Blender imports
import bpy
import bmesh
from mathutils import Matrix, Vector

# Addon imports
from .common import *

def makeSquare(coord1:Vector, coord2:Vector, face:bool=True, flipNormal:bool=False, bme:bmesh=None):
    """
    create a square with bmesh

    Keyword Arguments:
        coord1     -- back/left/bottom corner of the square (furthest negative in all three axes)
        coord2     -- front/right/top  corner of the square (furthest positive in all three axes)
        face       -- draw face connecting cube verts
        flipNormal -- flip the normals of the cube
        bme        -- bmesh object in which to create verts
    NOTE: if coord1 and coord2 are different on all three axes, z axis will stay consistent at coord1.z

    Returns:
        vList      -- list of vertices with normal facing in positive direction (right hand rule)

    """
    # create new bmesh object
    bme = bme or bmesh.new()

    # create square with normal facing +x direction
    if coord1.x == coord2.x:
        v1, v2, v3, v4 = [bme.verts.new((coord1.x, y, z)) for y in [coord1.y, coord2.y] for z in [coord1.z, coord2.z]]
    # create square with normal facing +y direction
    elif coord1.y == coord2.y:
        v1, v2, v3, v4 = [bme.verts.new((x, coord1.y, z)) for x in [coord1.x, coord2.x] for z in [coord1.z, coord2.z]]
    # create square with normal facing +z direction
    else:
        v1, v2, v3, v4 = [bme.verts.new((x, y, coord1.z)) for x in [coord1.x, coord2.x] for y in [coord1.y, coord2.y]]
    vList = [v1, v3, v4, v2]

    # create face
    if face:
        bme.faces.new(vList[::-1] if flipNormal else vList)

    return vList


def makeCube(coord1:Vector, coord2:Vector, sides:list=[False]*6, flipNormals:bool=False, bme:bmesh=None):
    """
    create a cube with bmesh

    Keyword Arguments:
        coord1      -- back/left/bottom corner of the cube (furthest negative in all three axes)
        coord2      -- front/right/top  corner of the cube (furthest positive in all three axes)
        sides       -- draw sides [+z, -z, +x, -x, +y, -y]
        flipNormals -- flip the normals of the cube
        bme         -- bmesh object in which to create verts

    Returns:
        vList       -- list of vertices in the following x,y,z order: [---, -+-, ++-, +--, --+, +-+, +++, -++]

    """

    # ensure coord1 is less than coord2 in all dimensions
    assert coord1.x < coord2.x
    assert coord1.y < coord2.y
    assert coord1.z < coord2.z

    # create new bmesh object
    bme = bme or bmesh.new()

    # create vertices
    vList = [bme.verts.new((x, y, z)) for x in [coord1.x, coord2.x] for y in [coord1.y, coord2.y] for z in [coord1.z, coord2.z]]

    # create faces
    v1, v2, v3, v4, v5, v6, v7, v8 = vList
    newFaces = []
    if sides[0]:
        newFaces.append([v6, v8, v4, v2])
    if sides[1]:
        newFaces.append([v3, v7, v5, v1])
    if sides[4]:
        newFaces.append([v4, v8, v7, v3])
    if sides[3]:
        newFaces.append([v2, v4, v3, v1])
    if sides[2]:
        newFaces.append([v8, v6, v5, v7])
    if sides[5]:
        newFaces.append([v6, v2, v1, v5])

    for f in newFaces:
        if flipNormals:
            f.reverse()
        bme.faces.new(f)

    return [v1, v3, v7, v5, v2, v6, v8, v4]


def makeCircle(r:float, N:int, co:Vector=Vector((0,0,0)), face:bool=True, flipNormals:bool=False, bme:bmesh=None):
    """
    create a circle with bmesh

    Keyword Arguments:
        r           -- radius of circle
        N           -- number of verts on circumference
        co          -- coordinate of cylinder's center
        face        -- create face between circle verts
        flipNormals -- flip normals of cylinder
        bme         -- bmesh object in which to create verts

    """
    # initialize vars
    bme = bme or bmesh.new()
    verts = []

    # create verts around circumference of circle
    for i in range(N):
        circ_val = ((2 * math.pi) / N) * i
        x = r * math.cos(circ_val)
        y = r * math.sin(circ_val)
        coord = co + Vector((x, y, 0))
        verts.append(bme.verts.new(coord))
    # create face
    if face:
        bme.faces.new(verts if not flipNormals else verts[::-1])

    return verts


def makeCylinder(r:float, h:float, N:int, co:Vector=Vector((0,0,0)), botFace:bool=True, topFace:bool=True, flipNormals:bool=False, bme:bmesh=None):
    """
    create a cylinder with bmesh

    Keyword Arguments:
        r           -- radius of cylinder
        h           -- height of cylinder
        N           -- number of verts per circle
        co          -- coordinate of cylinder's center
        botFace     -- create face on bottom of cylinder
        topFace     -- create face on top of cylinder
        flipNormals -- flip normals of cylinder
        bme         -- bmesh object in which to create verts

    """
    # initialize vars
    bme = bme or bmesh.new()
    topVerts = []
    botVerts = []
    sideFaces = []

    # create upper and lower circles
    for i in range(N):
        circ_val = ((2 * math.pi) / N) * i
        x = r * math.cos(circ_val)
        y = r * math.sin(circ_val)
        z = h / 2
        coordT = co + Vector((x, y, z))
        coordB = co + Vector((x, y, -z))
        topVerts.append(bme.verts.new(coordT))
        botVerts.append(bme.verts.new(coordB))

    # create faces on the sides
    _, sideFaces = connectCircles(topVerts if flipNormals else botVerts, botVerts if flipNormals else topVerts, bme)
    smoothBMFaces(sideFaces)

    # create top and bottom faces
    if topFace:
        bme.faces.new(topVerts if not flipNormals else topVerts[::-1])
    if botFace:
        bme.faces.new(botVerts[::-1] if not flipNormals else botVerts)

    # return bme & dictionary with lists of top and bottom vertices
    return bme, {"bottom":botVerts[::-1], "top":topVerts}


def makeTube(r:float, h:float, t:float, N:int, co:Vector=Vector((0,0,0)), topFace:bool=True, botFace:bool=True, bme:bmesh=None):
    """
    create a tube with bmesh

    Keyword Arguments:
        r       -- radius of inner cylinder
        h       -- height of cylinder
        t       -- thickness of tube
        N       -- number of verts per circle
        co      -- coordinate of cylinder's center
        botFace -- create face on bottom of cylinder
        topFace -- create face on top of cylinder
        bme     -- bmesh object in which to create verts

    """
    # create new bmesh object
    if bme == None:
        bme = bmesh.new()

    # create upper and lower circles
    bme, innerVerts = makeCylinder(r, h, N, co=co, botFace=False, topFace=False, flipNormals=True, bme=bme)
    bme, outerVerts = makeCylinder(r + t, h, N, co=co, botFace=False, topFace=False, bme=bme)
    if topFace:
        connectCircles(outerVerts["top"], innerVerts["top"], bme)
    if botFace:
        connectCircles(outerVerts["bottom"], innerVerts["bottom"], bme)
    # return bmesh
    return bme, {"outer":outerVerts, "inner":innerVerts}


def makeTetra():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    v1 = bme.verts.new((0, 1, -1))
    v2 = bme.verts.new((0.86603, -0.5, -1))
    v3 = bme.verts.new((-0.86603, -0.5, -1))
    bme.faces.new((v1, v2, v3))
    v4 = bme.verts.new((0, 0, 1))
    bme.faces.new((v4, v3, v2))
    bme.faces.new((v4, v1, v3))
    bme.faces.new((v4, v2, v1))

    # return bmesh
    return bme


# r = radius, N = numVerts
def makeCone(r, N):
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    topV = bme.verts.new((0, 0, 1))
    # create bottom circle
    vertList = []
    for i in range(N):
        vertList.append(bme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), -1)))
    bme.faces.new(vertList)

    bme.faces.new((vertList[-1], vertList[0], topV))
    for v in range(N-1):
        bme.faces.new((vertList.pop(0), vertList[0], topV))


    # return bmesh
    return bme


def makeOcta():
    # create new bmesh object
    bme = bmesh.new()

    # make vertices
    topV = bme.verts.new((0, 0, 1.5))
    botV = bme.verts.new((0, 0,-1.5))

    v1 = bme.verts.new(( 1, 1, 0))
    v2 = bme.verts.new((-1, 1, 0))
    v3 = bme.verts.new((-1,-1, 0))
    v4 = bme.verts.new(( 1,-1, 0))

    # make faces
    bme.faces.new((topV, v1, v2))
    bme.faces.new((botV, v2, v1))
    bme.faces.new((topV, v2, v3))
    bme.faces.new((botV, v3, v2))
    bme.faces.new((topV, v3, v4))
    bme.faces.new((botV, v4, v3))
    bme.faces.new((topV, v4, v1))
    bme.faces.new((botV, v1, v4))

    # return bmesh
    return bme


def makeDodec():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    q = 1.618
    bme.verts.new((   1,   1,   1))
    bme.verts.new((  -1,  -1,  -1))
    bme.verts.new((  -1,   1,   1))
    bme.verts.new((   1,  -1,   1))
    bme.verts.new((   1,   1,  -1))
    bme.verts.new((   1,  -1,  -1))
    bme.verts.new((  -1,  -1,   1))
    bme.verts.new((  -1,   1,  -1))
    bme.verts.new((   0, 1/q,   q))
    bme.verts.new((   0,-1/q,   q))
    bme.verts.new((   0, 1/q,  -q))
    bme.verts.new((   0,-1/q,  -q))
    bme.verts.new(( 1/q,   q,   0))
    bme.verts.new(( 1/q,  -q,   0))
    bme.verts.new((-1/q,   q,   0))
    bme.verts.new((-1/q,  -q,   0))
    bme.verts.new((   q,   0, 1/q))
    bme.verts.new((  -q,   0, 1/q))
    bme.verts.new((   q,   0,-1/q))
    bme.verts.new((  -q,   0,-1/q))


    # return bmesh
    return bme


# r = radius, V = numVerticalCircles, H = numHorizontalCircles
def makeUVSphere(r, V, H):
    # create new bmesh object
    bme = bmesh.new()
    testBme = bmesh.new()

    # create vertices
    vertListV = []
    vertListH = []
    for i in range(int(V/4), int((3*V)/4)+1):
        v = testBme.verts.new((r * math.cos(((2 * math.pi) / V) * i), 0, r * math.sin(((2 * math.pi) / V) * i)))
        vertListV.append(v)
        nextVertListH = []
        if i != int(V/4) and i != int((3*V)/4):
            for j in range(H):
                # replace 'r' with x value of 'v'
                nextVertListH.append(bme.verts.new((v.co.x * math.cos(((2 * math.pi) / H) * j), v.co.x * math.sin(((2 * math.pi) / H) * j), v.co.z)))
            vertListH.append(nextVertListH)
        elif i == int(V/4):
            topV = bme.verts.new((v.co))
        elif i == int((3*V)/4):
            botV = bme.verts.new((v.co))

    # create faces
    for l in range(len(vertListH)-1):
        for m in range(-1, len(vertListH[l])-1):
            bme.faces.new((vertListH[l][m], vertListH[l+1][m], vertListH[l+1][m+1], vertListH[l][m+1]))

    # create top and bottom faces
    for n in range(-1,H-1):
        bme.faces.new((vertListH[0][n], vertListH[0][n+1], topV))
        bme.faces.new((vertListH[-1][n+1], vertListH[-1][n], botV))


    # return bmesh
    return bme


def makeIco():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    topV = bme.verts.new((0, 0, 1))
    r1a = bme.verts.new((0.28, 0.85, 0.45))
    r1b = bme.verts.new((-0.72, 0.53, 0.45))
    bme.faces.new((r1a, r1b, topV))
    r1c = bme.verts.new((-0.72, -0.53, 0.45))
    bme.faces.new((r1b, r1c, topV))
    r1d = bme.verts.new((0.28, -0.85, 0.45))
    bme.faces.new((r1c, r1d, topV))
    r1e = bme.verts.new((0.89, 0, 0.45))
    bme.faces.new((r1d, r1e, topV))
    bme.faces.new((r1e, r1a, topV))
    botV = bme.verts.new((0, 0,-1))
    r2a = bme.verts.new((0.72, 0.53, -0.45))
    r2b = bme.verts.new((-0.28, 0.85, -0.45))
    bme.faces.new((r2b, r2a, botV))
    r2c = bme.verts.new((-0.89, 0, -0.45))
    bme.faces.new((r2c, r2b, botV))
    r2d = bme.verts.new((-0.28, -0.85, -0.45))
    bme.faces.new((r2d, r2c, botV))
    r2e = bme.verts.new((0.72, -0.53, -0.45))
    bme.faces.new((r2e, r2d, botV))
    bme.faces.new((r2a, r2e, botV))

    bme.faces.new((r2a, r2b, r1a))
    bme.faces.new((r2b, r2c, r1b))
    bme.faces.new((r2c, r2d, r1c))
    bme.faces.new((r2d, r2e, r1d))
    bme.faces.new((r2e, r2a, r1e))

    bme.faces.new((r1a, r2b, r1b))
    bme.faces.new((r1b, r2c, r1c))
    bme.faces.new((r1c, r2d, r1d))
    bme.faces.new((r1d, r2e, r1e))
    bme.faces.new((r1e, r2a, r1a))

    # return bmesh
    return bme


def makeTruncIco(layer):
    newObjFromBmesh(layer, makeIco(), "truncated icosahedron")
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.bevel(offset=0.35, vertex_only=True)
    bpy.ops.object.editmode_toggle()


def makeTorus():
    # create new bmesh object
    bme = bmesh.new()
    testBme = bmesh.new()

    # create reference circle
    vertList = []
    # for i in range(N):
    #     vertList.append(testBme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), z)))




    # return bmesh
    return bme


def tupleAdd(p1, p2):
    """ returns linear sum of two given tuples """
    return tuple(x+y for x,y in zip(p1, p2))


def makeLattice(vertDist:Vector, scale:Vector, offset:Vector=Vector((0, 0, 0))):
    """ return lattice coordinate matrix surrounding object of size 'scale'

    Keyword arguments:
    vertDist  -- distance between lattice verts in 3D space
    scale     -- lattice scale in 3D space
    offset    -- offset lattice center from origin

    """

    # shift offset to ensure lattice surrounds object
    offset = offset - vec_remainder(offset, vertDist)
    # calculate res of lattice
    res = Vector((round(scale.x / vertDist.x),
                  round(scale.y / vertDist.y),
                  round(scale.z / vertDist.z)))
    # populate coord matrix
    nx, ny, nz = int(res.x), int(res.y), int(res.z)
    create_coord = lambda v: vec_mult(v - res / 2, vertDist) + offset
    coordMatrix = [[[create_coord(Vector((x, y, z))) for z in range(nz)] for y in range(ny)] for x in range(nx)]

    # create bmesh
    bme = bmesh.new()
    vertMatrix = np.zeros((len(coordMatrix), len(coordMatrix[0]), len(coordMatrix[0][0]))).tolist()
    # add vertex for each coordinate
    for x in range(len(coordMatrix)):
        for y in range(len(coordMatrix[0])):
            for z in range(len(coordMatrix[0][0])):
                vertMatrix[x][y][z] = bme.verts.new(coordMatrix[x][y][z])
                # create new edges from vert
                if x != 0: bme.edges.new((vertMatrix[x][y][z], vertMatrix[x-1][y][z]))
                if y != 0: bme.edges.new((vertMatrix[x][y][z], vertMatrix[x][y-1][z]))
                if z != 0: bme.edges.new((vertMatrix[x][y][z], vertMatrix[x][y][z-1]))
    # draw bmesh verts in 3D space
    # drawBMesh(bme)

    return bme
