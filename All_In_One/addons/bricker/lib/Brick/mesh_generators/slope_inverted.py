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
import bpy
import bmesh
import math
import numpy as np

# Blender imports
from mathutils import Vector, Matrix

# Addon imports
from .geometric_shapes import *
from .generator_utils import *
from ....functions import *


def makeInvertedSlope(dimensions:dict, brickSize:list, brickType:str, loopCut:bool, direction:str=None, circleVerts:int=None, detail:str="LOW", stud:bool=True, bme:bmesh=None):
    # TODO: Add support for loopCut
    """
    create slope brick with bmesh

    NOTE: brick created with slope facing +X direction, then translated/rotated as necessary

    Keyword Arguments:
        dimensions  -- dictionary containing brick dimensions
        brickSize   -- size of brick (e.g. 2x3 slope -> [2, 3, 3])
        brickType   -- cm.brickType
        loopCut     -- loop cut cylinders so bevels can be cleaner
        direction   -- direction slant faces in ("X+", "X-", "Y+", "Y-")
        circleVerts -- number of vertices per circle of cylinders
        detail      -- level of brick detail (options: ("FLAT", "LOW", "MEDIUM", "HIGH"))
        stud        -- create stud on top of brick
        bme         -- bmesh object in which to create verts

    """
    # create new bmesh object
    bme = bmesh.new() if not bme else bme

    # set direction to longest side if None (defaults to X if sides are the same)
    maxIdx = brickSize.index(max(brickSize[:2]))
    directions = ["X+", "Y+", "X-", "Y-"]
    # default to "X+" if X is larger, "Y+" if Y is larger
    direction = direction or directions[maxIdx]
    # verify direction is valid
    assert direction in directions

    # get halfScale
    bAndPBrick = flatBrickType(brickType) and brickSize[2] == 3
    height = dimensions["height"] * (3 if bAndPBrick else 1)
    d = Vector((dimensions["width"] / 2, dimensions["width"] / 2, height / 2))
    # get scalar for d in positive xyz directions
    adjustedBrickSize = (brickSize[:2] if "X" in direction else brickSize[1::-1]) + brickSize[2:]
    scalar = Vector((adjustedBrickSize[0] * 2 - 1,
                     adjustedBrickSize[1] * 2 - 1,
                     1))
    # get thickness of brick from inside to outside
    thick = Vector([dimensions["thickness"]] * 3)

    # make brick body cube
    coord1 = -d
    coord2 = vec_mult(d, [1, scalar.y, 1])
    v1, v2, v3, v4, v5, v6, v7, v8 = makeCube(coord1, coord2, [0 if stud else 1, 1 if detail == "FLAT" else 0, 0, 0, 1, 1], bme=bme)
    if adjustedBrickSize[0] > 1:
        # remove bottom verts on slope side
        bme.verts.remove(v6)
        bme.verts.remove(v7)
    # add face to opposite side from slope
    bme.faces.new((v1, v5, v8, v2))

    # make square at end of slope
    coord1 = vec_mult(d, [scalar.x, -1, 1])
    coord2 = vec_mult(d, [scalar.x, scalar.y, 1])
    coord1.z -= thick.z
    v9, v10, v11, v12 = makeSquare(coord1, coord2, bme=bme)

    # connect square to body cube
    bme.faces.new([v8, v11, v10, v3, v2])
    bme.faces.new([v9, v12, v5, v1, v4])
    if max(brickSize[:2]) == 2 or detail in ["FLAT", "LOW"]:
        bme.faces.new((v4, v3, v10, v9))
    else:
        pass
        # TODO: Draw inset half-cylinder

    # add details on top
    if not stud:
        bme.faces.new((v12, v11, v8, v5))
    else:
        if adjustedBrickSize[0] > 1:
            # make upper square over slope
            coord1 = Vector((d.x, -d.y + thick.y / 2, -d.z * (0.5 if max(adjustedBrickSize[:2]) == 2 else 0.625)))
            coord2 = Vector((d.x * scalar.x - thick.x, d.y * scalar.y - thick.y / 2, d.z))
            # v13, v14, v15, v16, v17, v18, v19, v20 = makeCube(coord1, coord2, [0, 0, 1, 0 if sum(adjustedBrickSize[:2]) == 5 else 1, 1, 1], flipNormals=True, bme=bme)
            # TODO: replace the following line with line above to add support details later
            v13, v14, v15, v16, v17, v18, v19, v20 = makeCube(coord1, coord2, [0, 0, 1, 1, 1, 1], flipNormals=True, bme=bme)
            v15.co.z += (d.z * 2 - thick.z) * (0.9 if max(adjustedBrickSize[:2]) == 3 else 0.8)
            v16.co.z = v15.co.z
            # make faces on edges of new square
            bme.faces.new((v18, v17, v5, v12))
            bme.faces.new((v19, v18, v12, v11))
            bme.faces.new((v20, v19, v11, v8))
            addSlopeStuds(dimensions, height, adjustedBrickSize, brickType, circleVerts, bme, edgeXp=[v14, v13], edgeXn=[v16, v15], edgeYp=[v13, v16], edgeYn=[v15, v14], loopCut=loopCut)
        else:
            v17, v20 = v6, v7

        addStuds(dimensions, height, [1, adjustedBrickSize[1], adjustedBrickSize[2]], brickType, circleVerts, bme, edgeXp=[v20, v17], edgeXn=[v8, v5], edgeYp=[v20, v8], edgeYn=[v17, v5], hollow=False, loopCut=loopCut)
        pass

    # add details underneath
    if detail != "FLAT":
        # making verts for hollow portion
        coord1 = -d + Vector((thick.x, thick.y, 0))
        coord2 = Vector((d.x + (dimensions["tick_depth"] if detail == "HIGH" else 0), d.y * scalar.y, d.z * scalar.z)) - thick
        sides = [1 if detail == "LOW" else 0, 0, 0 if detail == "HIGH" else 1, 1, 1, 1]
        v21, v22, v23, v24, v25, v26, v27, v28 = makeCube(coord1, coord2, sides, flipNormals=True, bme=bme)
        # make faces on bottom edges of brick
        bme.faces.new((v1,  v21,  v24, v4))
        bme.faces.new((v1,  v2,  v22, v21))
        bme.faces.new((v23, v22, v2,  v3))

        # make tick marks inside
        if detail == "HIGH":
            bottomVertsD = addTickMarks(dimensions, [1, min(adjustedBrickSize[:2]), adjustedBrickSize[2]], circleVerts, detail, d, thick, bme, nno=v1, npo=v2, ppo=v3, pno=v4, nni=v21, npi=v22, ppi=v23, pni=v24, nnt=v25, npt=v28, ppt=v27, pnt=v26, inverted_slope=True, sideMarks=False)
            bottomVerts = bottomVertsD["X+"][::-1]
        else:
            bme.faces.new((v23, v3, v4, v24))
            bottomVerts = []

        # add supports
        if detail in ("MEDIUM", "HIGH") and min(adjustedBrickSize[:2]) == 2:
            addOblongSupport(dimensions, height, loopCut, circleVerts, "SLOPE_INVERTED", detail, d, scalar, thick, bme) # [v27] + bottomVerts + [v26], [v28, v25], [v27, v28], [v26, v25], bme)

        # add small inner cylinders inside brick
        if detail in ("MEDIUM", "HIGH"):
            addInnerCylinders(dimensions, [1, min(adjustedBrickSize[:2]), adjustedBrickSize[2]], circleVerts, d, [v27] + bottomVerts + [v26], [v28, v25], [v27, v28], [v26, v25], bme, loopCut=loopCut)

        # add half-cylinder insets on slope underside
        if detail in ("MEDIUM", "HIGH") and max(adjustedBrickSize[:2]) == 3:
            # TODO: Rewrite this as dedicated function
            # TODO: Add loopCut functionality for half-cylinder insets
            addSlopeStuds(dimensions, height, [2, min(adjustedBrickSize[:2]), adjustedBrickSize[2]], brickType, circleVerts, bme, edgeXp=[v3, v4], edgeXn=[v9, v10], edgeYp=[v4, v9], edgeYn=[v10, v3], underside=True, loopCut=loopCut)

    # translate slope to adjust for flipped brick
    for v in bme.verts:
        v.co.y -= d.y * (scalar.y - 1) if direction in ("X-", "Y+") else 0
        v.co.x -= d.x * (scalar.x - 1) if direction in ("X-", "Y-") else 0
    # rotate slope to the appropriate orientation
    mult = directions.index(direction)
    bmesh.ops.rotate(bme, verts=bme.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90) * mult, 3, 'Z'))

    return bme
