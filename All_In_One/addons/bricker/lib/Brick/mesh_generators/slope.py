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


def makeSlope(dimensions:dict, brickSize:list, brickType:str, loopCut:bool, direction:str=None, circleVerts:int=None, detail:str="LOW", stud:bool=True, bme:bmesh=None):
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
    if max(brickSize[:2]) == 1:
        coord1 = Vector((-d.x, -d.y, -d.z + dimensions["slit_height"]))
        coord2 = Vector((-d.x,  d.y,  d.z * (4 / 3) - d.z))
        v1, v2, v7, v6 = makeSquare(coord1, coord2, face=True, flipNormal=True, bme=bme)
    else:
        coord1 = -d
        coord2 = vec_mult(d, [1, scalar.y, 1])
        v1, v2, d0, d1, v5, v6, v7, v8 = makeCube(coord1, coord2, [0 if stud else 1, 1 if detail == "FLAT" else 0, 0, 0, 1, 1], bme=bme)
        # remove bottom verts on slope side
        bme.verts.remove(d0)
        bme.verts.remove(d1)
        # add face to opposite side from slope
        bme.faces.new((v1, v5, v8, v2))
        # create stud
        if stud: addStuds(dimensions, height, [1] + adjustedBrickSize[1:], "CONE", circleVerts, bme, edgeXp=[v7, v6], edgeXn=[v8, v5], edgeYp=[v7, v8], edgeYn=[v6, v5], hollow=brickSize[2] > 3, loopCut=loopCut)

    # make square at end of slope
    coord1 = Vector((d.x * scalar.x, -d.y, -d.z + (dimensions["slit_height"] if max(brickSize[:2]) == 1 else 0)))
    coord2 = vec_mult(d, [scalar.x, scalar.y, -1])
    coord2.z += thick.z
    v9, v10, v11, v12 = makeSquare(coord1, coord2, bme=bme)

    # connect square to body cube
    bme.faces.new([v7, v11, v10, v2] + ([v8] if max(brickSize[:2]) != 1 else []))
    bme.faces.new([v1, v9, v12, v6] + ([v5] if max(brickSize[:2]) != 1 else []))
    bme.faces.new((v12, v11, v7, v6))

    # add underside details
    if max(brickSize[:2]) == 1:
        # make slit for 1x1 slope
        coord1 = -d
        coord1.xy += Vector([dimensions["slit_depth"]]*2)
        coord2 = Vector((d.x * scalar.x, d.y * scalar.y, -d.z + dimensions["slit_height"]))
        coord2.xy -= Vector([dimensions["slit_depth"]]*2)
        v13, v14, v15, v16, v17, v18, v19, v20 = makeCube(coord1, coord2, [0, 1 if detail == "FLAT" else 0, 1, 1, 1, 1], bme=bme)
        # connect slit to outer cube
        bme.faces.new((v18, v10, v9, v17))
        bme.faces.new((v19, v2, v10, v18))
        bme.faces.new((v20, v1, v2, v19))
        bme.faces.new((v17, v9, v1, v20))
        # add underside detail
        if detail != "FLAT":
            # add inside verts of slope
            coord1 = -d
            coord1.xy += thick.xy
            coord2 = Vector(( d.x - thick.x,
                              d.y - thick.y,
                              -thick.z * 0.2))
            v19, v20, v21, v22, v23, v24, v25, v26 = makeCube(coord1, coord2, [1, 0, 1, 1, 1, 1], flipNormals=True, bme=bme)
            # adjust z height of top verts at end of inner slope
            v24.co.z = -d.z + thick.z
            v25.co.z = -d.z + thick.z
            # connect inner and outer verts
            bme.faces.new((v19, v22, v16, v13))
            bme.faces.new((v20, v19, v13, v14))
            bme.faces.new((v21, v20, v14, v15))
            bme.faces.new((v22, v21, v15, v16))
    elif detail == "FLAT":
        bme.faces.new((v10, v9, v1, v2))
    else:
        addBlockSupports = adjustedBrickSize[0] in (3, 4) and adjustedBrickSize[1] == 1
        # add inside square at end of slope
        coord1 = Vector(( d.x * scalar.x - thick.x,
                         -d.y + thick.y,
                         -d.z))
        coord2 = Vector(( d.x * scalar.x - thick.x,
                          d.y * scalar.y - thick.y,
                         -d.z + thick.z))
        v13, v14, v15, v16 = makeSquare(coord1, coord2, flipNormal=True, bme=bme)
        # add verts next to inside square at end of slope
        if adjustedBrickSize[0] in (3, 4):
            x = d.x * scalar.x + (thick.x * (adjustedBrickSize[0] - 3))
            x -= (dimensions["tube_thickness"] + dimensions["stud_radius"]) * (adjustedBrickSize[0] - 2)
            v17 = bme.verts.new((x, coord1.y, coord2.z))
            v18 = bme.verts.new((x, coord2.y, coord2.z))
            bme.faces.new((v17, v18, v15, v16))
        else:
            v17 = v16
            v18 = v15
        # add inside verts cube at deepest section
        coord1 = -d
        coord1.xy += thick.xy
        coord2 = vec_mult(d, [1, scalar.y, 1])
        coord2.yz -= thick.yz
        v19, v20, v21, v22, v23, v24, v25, v26 = makeCube(coord1, coord2, [1 if detail not in ("MEDIUM", "HIGH") and not addBlockSupports else 0, 0, 0, 1, 0, 0], flipNormals=True, bme=bme)
        # connect side faces from verts created above
        bme.faces.new((v18, v25, v21))
        bme.faces.new((v22, v24, v17))
        if adjustedBrickSize[0] in (3, 4):
            bme.faces.new((v14, v15, v18, v21))
            bme.faces.new((v16, v13,  v22, v17))
        else:
            bme.faces.new((v14, v18, v21))
            bme.faces.new((v13,  v22, v17))
        # connect face for inner slope
        bme.faces.new((v24, v25, v18, v17))

        # add block supports under certain slopes
        if addBlockSupports:
            # add longer support
            coord1 = Vector((d.x - thick.x, -d.y + thick.y, -d.z))
            coord2 = Vector((d.x,            d.y - thick.y,  d.z - thick.z))
            v27, v28, d0, d1, v31, d2, d3, v34 = makeCube(coord1, coord2, [0, 0, 0, 1, 0, 0], bme=bme)
            # remove v32, v33, v29, v30 (same location as v24, v25, v21, v22)
            bme.verts.remove(d0)
            bme.verts.remove(d1)
            bme.verts.remove(d2)
            bme.verts.remove(d3)
            # add short tick support
            coord1 = Vector((d.x,          -thick.y / 2, -d.z))
            coord2 = Vector((d.x + thick.x, thick.y / 2,  d.z - thick.z))
            v35, v36, v37, v38, v39, v40, v41, v42 = makeCube(coord1, coord2, [0, 1, 1, 0, 1, 1], bme=bme)
            # connect the two supports
            bme.faces.new((v27, v28, v21, v36, v35, v22))
            bme.faces.new((v24, v22, v35, v39))
            bme.faces.new((v21, v25, v42, v36))
            # connect inner and outer verts sides
            bme.faces.new([v20, v2, v10, v14] + [v21, v28])
            bme.faces.new([v13, v9, v1, v19] + [v27, v22])
            # connect inner cube with block support
            bme.faces.new((v19, v23, v31, v27))
            bme.faces.new((v28, v34, v26, v20))
            if detail == "LOW":
                bme.faces.new((v23, v26, v34, v31))
        else:
            # connect inner and outer verts sides
            bme.faces.new((v20, v2, v10, v14))
            bme.faces.new((v13, v9, v1, v19))
            # connect inner cube to itself
            bme.faces.new((v19, v23, v24, v22))
            bme.faces.new((v21, v25, v26, v20))

        # connect inner and outer verts front/back
        bme.faces.new((v13, v14, v10, v9))
        bme.faces.new((v1, v2, v20, v19))

        # add supports
        addSupports(dimensions, height, adjustedBrickSize, brickType, loopCut, circleVerts, "SLOPE", detail, d, scalar, thick, bme, add_beams=False, hollow=brickSize[:2] not in ([1, 2], [2, 1]))
        # add inner cylinders
        if detail in ("MEDIUM", "HIGH"):
            edgeXp = [v34 if addBlockSupports else v25, v31 if addBlockSupports else v24]
            edgeXn = [v26, v23]
            edgeYp = [v34 if addBlockSupports else v25, v26]
            edgeYn = [v31 if addBlockSupports else v24, v23]
            addInnerCylinders(dimensions, [1] + adjustedBrickSize[1:], circleVerts, d, edgeXp, edgeXn, edgeYp, edgeYn, bme, loopCut=loopCut)


    # translate slope to adjust for flipped brick
    for v in bme.verts:
        v.co.y -= d.y * (scalar.y - 1) if direction in ("X-", "Y+") else 0
        v.co.x -= d.x * (scalar.x - 1) if direction in ("X-", "Y-") else 0
    # rotate slope to the appropriate orientation
    mult = directions.index(direction)
    bmesh.ops.rotate(bme, verts=bme.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90) * mult, 3, 'Z'))

    return bme
