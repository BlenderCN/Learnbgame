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

import bpy
import bmesh
import math
from mathutils import Vector
from ....functions import *


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
        v1, v2, v3, v4 = [bme.verts.new((coord1.x, y, z)) for y in (coord1.y, coord2.y) for z in (coord1.z, coord2.z)]
    # create square with normal facing +y direction
    elif coord1.y == coord2.y:
        v1, v2, v3, v4 = [bme.verts.new((x, coord1.y, z)) for x in (coord1.x, coord2.x) for z in (coord1.z, coord2.z)]
    # create square with normal facing +z direction
    else:
        v1, v2, v3, v4 = [bme.verts.new((x, y, coord1.z)) for x in (coord1.x, coord2.x) for y in (coord1.y, coord2.y)]
    vList = [v1, v3, v4, v2]

    # create face
    if face:
        bme.faces.new(vList[::-1] if flipNormal else vList)

    return vList


def makeCube(coord1:Vector, coord2:Vector, sides:list=[False]*6, flipNormals:bool=False, seams:bool=False, bme:bmesh=None):
    """
    create a cube with bmesh

    Keyword Arguments:
        coord1      -- back/left/bottom corner of the cube (furthest negative in all three axes)
        coord2      -- front/right/top  corner of the cube (furthest positive in all three axes)
        sides       -- draw sides [+z, -z, +x, -x, +y, -y]
        flipNormals -- flip the normals of the cube
        seams       -- make all edges seams
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
    vList = [bme.verts.new((x, y, z)) for x in (coord1.x, coord2.x) for y in (coord1.y, coord2.y) for z in (coord1.z, coord2.z)]

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
        newF = bme.faces.new(f)
        # if seams:
        #     for e in newF.edges:
        #         e.seam = True

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


def makeCylinder(r:float, h:float, N:int, co:Vector=Vector((0,0,0)), botFace:bool=True, topFace:bool=True, flipNormals:bool=False, loopCut:bool=False, seams:bool=True, bme:bmesh=None):
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
        loopCut     -- loop cut the cylinder in the center
        seams       -- make horizontal edges seams
        bme         -- bmesh object in which to create verts

    """
    # initialize vars
    bme = bme or bmesh.new()
    topVerts = []
    botVerts = []
    midVerts = []
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
        if loopCut:
            coordM = co + Vector((x, y, 0))
            midVerts.append(bme.verts.new(coordM))

    # if seams:
    #     for i in range(len(topVerts)):
    #         v1 = topVerts[i]
    #         v2 = topVerts[(i-1)]
    #         v3 = botVerts[i]
    #         v4 = botVerts[(i-1)]
    #         bme.edges.new((v1, v2)).seam = True
    #         bme.edges.new((v3, v4)).seam = True
    #     bme.edges.new((topVerts[0], botVerts[0])).seam = True

    # create faces on the sides
    if loopCut:
        _, sideFaces1 = connectCircles(topVerts if flipNormals else midVerts, midVerts if flipNormals else topVerts, bme)
        _, sideFaces2 = connectCircles(midVerts if flipNormals else botVerts, botVerts if flipNormals else midVerts, bme)
        smoothBMFaces(sideFaces1 + sideFaces2)
    else:
        _, sideFaces = connectCircles(topVerts if flipNormals else botVerts, botVerts if flipNormals else topVerts, bme)
        smoothBMFaces(sideFaces)

    # create top and bottom faces
    if topFace:
        bme.faces.new(topVerts if not flipNormals else topVerts[::-1])
    if botFace:
        bme.faces.new(botVerts[::-1] if not flipNormals else botVerts)

    # return bme & dictionary with lists of top and bottom vertices
    return bme, {"bottom":botVerts[::-1], "top":topVerts, "mid":midVerts}


def makeTube(r:float, h:float, t:float, N:int, co:Vector=Vector((0,0,0)), topFace:bool=True, botFace:bool=True, topFaceInner:bool=False, botFaceInner:bool=False, loopCut:bool=False, loopCutTop:bool=False, flipNormals:bool=False, seams:bool=True, bme:bmesh=None):
    """
    create a tube with bmesh

    Keyword Arguments:
        r            -- radius of inner cylinder
        h            -- height of cylinder
        t            -- thickness of tube
        N            -- number of verts per circle
        co           -- coordinate of cylinder's center
        botFace      -- create face on bottom of cylinder
        topFace      -- create face on top of cylinder
        botFaceInner -- create inner circle on bottom of cylinder
        topFaceInner -- create inner circle on top of cylinder
        loopCut      -- Add loop cut to cylinders
        loopCutTop   -- Add loop cut to top/bottom connected circles
        flipNormals  -- flip normals of cylinder
        seams       -- make horizontal edges seams
        bme          -- bmesh object in which to create verts

    """
    # create new bmesh object
    if bme == None:
        bme = bmesh.new()

    # create upper and lower circles
    bme, innerVerts = makeCylinder(r, h, N, co=co, botFace=False, topFace=False, flipNormals=not flipNormals, loopCut=loopCut, bme=bme)
    bme, outerVerts = makeCylinder(r + t, h, N, co=co, botFace=False, topFace=False, flipNormals=flipNormals, loopCut=loopCut, bme=bme)
    if topFace:
        if loopCutTop:
            circleVerts = makeCircle(r + (t / 2), N, co=Vector((co.x, co.y, co.z + h / 2)), face=False, bme=bme)
            connectCircles(outerVerts["top"], circleVerts[::-1], bme, flipNormals=flipNormals)
            connectCircles(circleVerts[::-1], innerVerts["top"], bme, flipNormals=flipNormals)
            selectVerts(circleVerts)
        else:
            connectCircles(outerVerts["top"], innerVerts["top"], bme, flipNormals=flipNormals)
    if botFace:
        if loopCutTop:
            circleVerts = makeCircle(r + (t / 2), N, co=Vector((co.x, co.y, co.z - h / 2)), face=False, bme=bme)
            connectCircles(outerVerts["bottom"], circleVerts[::-1], bme, flipNormals=flipNormals)
            connectCircles(circleVerts[::-1], innerVerts["bottom"], bme, flipNormals=flipNormals)
            selectVerts(circleVerts)
        else:
            connectCircles(outerVerts["bottom"], innerVerts["bottom"], bme, flipNormals=flipNormals)
    if botFaceInner:
        bme.faces.new(innerVerts["bottom"])
    if topFaceInner:
        bme.faces.new(innerVerts["top"][::-1])
    # return bmesh
    return bme, {"outer":outerVerts, "inner":innerVerts}


def connectCircles(circle1, circle2, bme, offset=0, flipNormals=False, smooth=True):
    assert offset < len(circle1) - 1 and offset >= 0
    faces = []
    for v in range(len(circle1)):
        v1 = circle1[v - offset]
        v2 = circle2[v]
        v3 = circle2[(v-1)]
        v4 = circle1[(v-1) - offset]
        f = bme.faces.new([v1, v2, v3, v4][::-1 if flipNormals else 1])
        f.smooth = smooth
        faces.append(f)
    return bme, faces
