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
from mathutils import Vector

# Addon imports
from .geometric_shapes import *
from .generator_utils import *
from ....functions import *


def makeTile(dimensions:dict, brickType:str, loopCut:bool, brickSize:list, circleVerts:int=None, type:str=None, detail:str="LOW", bme:bmesh=None):
    """
    create inverted slope brick with bmesh

    Keyword Arguments:
        dimensions  -- dictionary containing brick dimensions
        brickType   -- cm.brickType
        loopCut     -- loop cut cylinders so bevels can be cleaner
        brickSize   -- size of brick (e.g. standard 2x4 -> [2, 4, 3])
        circleVerts -- number of vertices per circle of cylinders
        type        -- type of round 1x1 brick in ("CONE", "CYLINDER", "STUD", "STUD_HOLLOW")
        detail      -- level of brick detail (options: ("FLAT", "LOW", "MEDIUM", "HIGH"))
        bme         -- bmesh object in which to create verts

    """
    # create new bmesh object
    bme = bmesh.new() if not bme else bme

    # get halfScale
    d = Vector((dimensions["width"] / 2, dimensions["width"] / 2, dimensions["height"] / 2))
    d.z = d.z * (brickSize[2] if flatBrickType(brickType) else 1)
    # get scalar for d in positive xyz directions
    scalar = Vector((brickSize[0] * 2 - 1,
                     brickSize[1] * 2 - 1,
                     1))
    d_scaled = vec_mult(d, scalar)
    # get thickness of brick from inside to outside
    thickXY = dimensions["thickness"] - (dimensions["tick_depth"] if "High" in detail and min(brickSize) != 1 else 0)
    thick = Vector((thickXY, thickXY, dimensions["thickness"]))

    # create cube
    if "GRILL" in type:
        coord1 = -d
        coord1.z += dimensions["slit_height"]
        coord2 = d_scaled
        coord2.z = coord1.z
        v1, v4, v3, v2 = makeSquare(coord1, coord2, face=False, bme=bme)
    else:
        sides = [1, 1 if detail == "FLAT" else 0, 1, 1, 1, 1]
        coord1 = -d
        coord1.z += dimensions["slit_height"]
        coord2 = d_scaled
        v1, v2, v3, v4, v5, v6, v7, v8 = makeCube(coord1, coord2, sides, bme=bme)

    # make verts for slit
    slit_depth = Vector([dimensions["slit_depth"]]*2)
    coord1 = -d
    coord1.xy += slit_depth
    coord2 = Vector((d_scaled.x, d_scaled.y, -d.z + dimensions["slit_height"]))
    coord2.xy -= slit_depth
    v9, v10, v11, v12, v13, v14, v15, v16 = makeCube(coord1, coord2, [0, 1 if detail == "FLAT" and "GRILL" not in type else 0, 1, 1, 1, 1], bme=bme)
    # connect slit to outer cube
    bme.faces.new((v14, v4, v1, v13))
    bme.faces.new((v15, v3, v4, v14))
    bme.faces.new((v16, v2, v3, v15))
    bme.faces.new((v13, v1, v2, v16))

    # add details
    if "GRILL" in type:
        if brickSize[0] < brickSize[1]:
            addGrillDetails(dimensions, brickSize, thick, scalar, d, v4, v1, v2, v3, v9, v10, v11, v12, bme)
        else:
            addGrillDetails(dimensions, brickSize, thick, scalar, d, v1, v2, v3, v4, v9, v10, v11, v12, bme)

    elif detail != "FLAT":
        # making verts for hollow portion
        coord1 = -d + Vector((thick.x, thick.y, 0))
        coord2 = vec_mult(d, scalar) - thick
        v17, v18, v19, v20, v21, v22, v23, v24 = makeCube(coord1, coord2, [1, 0, 1, 1, 1, 1], flipNormals=True, bme=bme)
        # connect hollow portion to verts for slit
        bme.faces.new((v18, v17, v9, v10))
        bme.faces.new((v19, v18, v10, v11))
        bme.faces.new((v20, v19, v11, v12))
        bme.faces.new((v17, v20, v12, v9))

        # add supports
        if max(brickSize[:2]) > 2:
            addSupports(dimensions, dimensions["height"], brickSize, brickType, loopCut, circleVerts, type, detail, d, scalar, thick, bme)

    return bme
