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
import bmesh
import math

# Blender imports
from mathutils import Vector, Matrix
from bpy.types import Object

# Addon imports
from .geometric_shapes import *
from .generator_utils import *
from ....functions import *


def makeStandardBrick(dimensions:dict, brickSize:list, type:str, brickType:str, loopCut:bool, circleVerts:int=16, detail:str="LOW", logo:Object=None, stud:bool=True, bme:bmesh=None):
    """
    create brick with bmesh

    Keyword Arguments:
        dimensions  -- dictionary containing brick dimensions
        brickSize   -- size of brick (e.g. standard 2x4 -> [2, 4, 3])
        type        -- type of brick (e.g. BRICK, PLATE, CUSTOM)
        brickType   -- cm.brickType
        loopCut     -- loop cut cylinders so bevels can be cleaner
        circleVerts -- number of vertices per circle of cylinders
        detail      -- level of brick detail (options: ["FLAT", "LOW", "MEDIUM", "HIGH"])
        logo        -- logo object to create on top of studs
        stud        -- create stud on top of brick
        bme         -- bmesh object in which to create verts

    """
    assert detail in ("FLAT", "LOW", "MEDIUM", "HIGH")
    # create new bmesh object
    bme = bmesh.new() if not bme else bme
    bAndPBrick = flatBrickType(brickType) and brickSize[2] == 3
    height = dimensions["height"] * (3 if bAndPBrick else 1)

    # get halfScale
    d = Vector((dimensions["width"] / 2, dimensions["width"] / 2, dimensions["height"] / 2))
    d.z = d.z * (brickSize[2] if flatBrickType(brickType) else 1)
    # get scalar for d in positive xyz directions
    scalar = Vector((brickSize[0] * 2 - 1,
                     brickSize[1] * 2 - 1,
                     1))
    # get thickness of brick from inside to outside
    thickXY = dimensions["thickness"] - (dimensions["tick_depth"] if "High" in detail and min(brickSize) != 1 else 0)
    thick = Vector((thickXY, thickXY, dimensions["thickness"]))

    # create cube
    coord1 = -d
    coord2 = vec_mult(d, scalar)
    v1, v2, v3, v4, v5, v6, v7, v8 = makeCube(coord1, coord2, [0 if stud else 1, 1 if detail == "FLAT" else 0, 1, 1, 1, 1], seams=True, bme=bme)

    # add studs
    if stud: addStuds(dimensions, height, brickSize, brickType, circleVerts, bme, edgeXp=[v7, v6], edgeXn=[v8, v5], edgeYp=[v7, v8], edgeYn=[v6, v5], hollow=brickSize[2] > 3 or "HOLES" in type, loopCut=loopCut)

    # add details
    if detail != "FLAT":
        drawTickMarks = detail == "HIGH" and ((brickSize[0] == 2 and brickSize[1] > 1) or (brickSize[1] == 2 and brickSize[0] > 1)) and brickSize[2] != 1
        # making verts for hollow portion
        coord1 = -d + Vector((thick.x, thick.y, 0))
        coord2 = vec_mult(d, scalar) - thick
        sides = [1 if detail == "LOW" else 0, 0] + ([0]*4 if drawTickMarks else [1]*4)
        v9, v10, v11, v12, v13, v14, v15, v16 = makeCube(coord1, coord2, sides, flipNormals=True, seams=True, bme=bme)
        # make tick marks inside 2 by x bricks
        if drawTickMarks:
            bottomVerts = addTickMarks(dimensions, brickSize, circleVerts, detail, d, thick, bme, nno=v1, npo=v2, ppo=v3, pno=v4, nni=v9, npi=v10, ppi=v11, pni=v12, nnt=v13, npt=v16, ppt=v15, pnt=v14)
        else:
            # make faces on bottom edges of brick
            bme.faces.new((v1,  v9,  v12, v4))
            bme.faces.new((v1,  v2,  v10, v9))
            bme.faces.new((v11, v3,  v4,  v12))
            bme.faces.new((v11, v10, v2,  v3))


        # add supports
        if max(brickSize[:2]) > 1:
            addSupports(dimensions, height, brickSize, brickType, loopCut, circleVerts, type, detail, d, scalar, thick, bme)
        # add small inner cylinders inside brick
        if detail in ("MEDIUM", "HIGH"):
            edgeXp = [v15] + (bottomVerts["X+"][::-1] if drawTickMarks else []) + [v14]
            edgeXn = [v16] + (bottomVerts["X-"][::-1] if drawTickMarks else []) + [v13]
            edgeYp = [v15] + (bottomVerts["Y+"][::-1] if drawTickMarks else []) + [v16]
            edgeYn = [v14] + (bottomVerts["Y-"][::-1] if drawTickMarks else []) + [v13]
            addInnerCylinders(dimensions, brickSize, circleVerts, d, edgeXp, edgeXn, edgeYp, edgeYn, bme, loopCut=loopCut)

    # transform final mesh
    gap = Vector([dimensions["gap"]] * 2)
    numer = vec_mult(d.xy * 2 + gap, brickSize[:2]) - gap
    denom = vec_mult(d.xy * 2,       brickSize[:2])
    if brickSize[0] != 1 or brickSize[1] != 1:
        bmesh.ops.scale(bme, verts=bme.verts, vec=(numer.x / denom.x, numer.y / denom.y, 1.0))
        if brickSize[0] > 1:
            for v in bme.verts:
                v.co.x -= (gap.x * brickSize[0] - gap.x) / 2
        if brickSize[1] > 1:
            for v in bme.verts:
                v.co.y -= (gap.y * brickSize[1] - gap.y) / 2

    # return bmesh
    return bme
