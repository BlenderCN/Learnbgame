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
import random
import time
import numpy as np

# Blender imports
from mathutils import Vector, Matrix

# Addon imports
from .mesh_generators import *
from .get_brick_dimensions import *
from ...functions import *

class Bricks:
    @staticmethod
    def new_mesh(dimensions:list, brickType:str, size:list=[1,1,3], type:str="BRICK", flip:bool=False, rotate90:bool=False, loopCut:bool=False, logo=False, logoType="NONE", logoScale=1, logoInset=None, all_vars=False, logo_details=None, undersideDetail:str="FLAT", stud:bool=True, circleVerts:int=16):
        """ create unlinked Brick at origin """
        # create brick mesh
        if type in ("BRICK", "PLATE") or "CUSTOM" in type:
            brickBM = makeStandardBrick(dimensions, size, type, brickType, loopCut, circleVerts=circleVerts, detail=undersideDetail, stud=stud)
        elif type in getRoundBrickTypes():
            brickBM = makeRound1x1(dimensions, brickType, loopCut, circleVerts=circleVerts, type=type, detail=undersideDetail)
        elif type in ("TILE", "TILE_GRILL"):
            brickBM = makeTile(dimensions, brickType, loopCut, brickSize=size, circleVerts=circleVerts, type=type, detail=undersideDetail)
        elif type in ("SLOPE", "SLOPE_INVERTED", "TALL_SLOPE"):
            # determine brick direction
            directions = ["X+", "Y+", "X-", "Y-"]
            maxIdx = size.index(max(size[:2]))
            maxIdx -= 2 if flip else 0
            maxIdx += 1 if rotate90 else 0
            # make slope brick bmesh
            if type == "SLOPE_INVERTED":
                brickBM = makeInvertedSlope(dimensions, size, brickType, loopCut, circleVerts=circleVerts, direction=directions[maxIdx], detail=undersideDetail, stud=stud)
            else:
                brickBM = makeSlope(dimensions, size, brickType, loopCut, circleVerts=circleVerts, direction=directions[maxIdx], detail=undersideDetail, stud=stud)
        else:
            raise ValueError("'new_mesh' function received unrecognized value for parameter 'type': '" + str(type) + "'")

        # create list of brick bmesh variations
        if logo and stud and (type in ("BRICK", "PLATE", "STUD", "SLOPE_INVERTED") or type == "SLOPE" and max(size[:2]) != 1):
            bms = makeLogoVariations(dimensions, size, brickType, directions[maxIdx] if type.startswith("SLOPE") else "", all_vars, logo, logo_details, logoInset, logoType, logoScale)
        else:
            bms = [bmesh.new()]

        # add brick mesh to bm mesh
        junkMesh = bpy.data.meshes.get('Bricker_junkMesh')
        if junkMesh is None:
            junkMesh = bpy.data.meshes.new('Bricker_junkMesh')
        brickBM.to_mesh(junkMesh)
        for bm in bms:
            bm.from_mesh(junkMesh)

        # return bmesh objects
        return bms

    @staticmethod
    def splitAll(bricksDict, zStep, keys=None):
        keys = keys or list(bricksDict.keys())
        for key in keys:
            # set all bricks as unmerged
            if bricksDict[key]["draw"]:
                bricksDict[key]["parent"] = "self"
                bricksDict[key]["size"] = [1, 1, zStep]

    def split(bricksDict, key, zStep, brickType, loc=None, v=True, h=True):
        """split brick vertically and/or horizontally

        Keyword Arguments:
        bricksDict -- Matrix of bricks in model
        key        -- key for brick in matrix
        loc        -- xyz location of brick in matrix
        v          -- split brick vertically
        h          -- split brick horizontally
        """
        # set up unspecified paramaters
        loc = loc or getDictLoc(bricksDict, key)
        # initialize vars
        size = bricksDict[key]["size"]
        newSize = [1, 1, size[2]]
        if flatBrickType(brickType):
            if not v:
                zStep = 3
            else:
                newSize[2] = 1
        if not h:
            newSize[0] = size[0]
            newSize[1] = size[1]
            size[0] = 1
            size[1] = 1
        # split brick into individual bricks
        keysInBrick = getKeysInBrick(bricksDict, size, zStep, loc=loc)
        for curKey in keysInBrick:
            bricksDict[curKey]["size"] = newSize.copy()
            bricksDict[curKey]["type"] = "BRICK" if newSize[2] == 3 else "PLATE"
            bricksDict[curKey]["parent"] = "self"
            bricksDict[curKey]["top_exposed"] = bricksDict[key]["top_exposed"]
            bricksDict[curKey]["bot_exposed"] = bricksDict[key]["bot_exposed"]
        return keysInBrick

    @staticmethod
    def get_dimensions(height=1, zScale=1, gap_percentage=0.01):
        return get_brick_dimensions(height, zScale, gap_percentage)


def getNumRots(direction, size):
    return 1 if direction != "" else (4 if size[0] == 1 and size[1] == 1 else 2)


def getRotAdd(direction, size):
    if direction != "":
        directions = ["X+", "Y+", "X-", "Y-"]
        rot_add = 90 * (directions.index(direction) + 1)
    else:
        rot_add = 180 if (size[0] == 2 and size[1] > 2) or (size[0] == 1 and size[1] > 1) else 90
    return rot_add


def makeLogoVariations(dimensions, size, brickType, direction, all_vars, logo, logo_details, logoInset, logoType, logoScale):
    # get logo rotation angle based on size of brick
    rot_vars = getNumRots(direction, size)
    rot_mult = 90 if size[0] == 1 and size[1] == 1 else 180
    rot_add = getRotAdd(direction, size)
    # set zRot to random rotation angle
    if all_vars:
        zRots = [i * rot_mult + rot_add for i in range(rot_vars)]
    else:
        randomSeed = int(time.time()*10**6) % 10000
        randS0 = np.random.RandomState(randomSeed)
        zRots = [randS0.randint(0,rot_vars) * rot_mult + rot_add]
    # get duplicate of logo mesh
    m = logo.data.copy()

    # create new bmeshes for each logo variation
    bms = [bmesh.new() for zRot in zRots]
    # get loc offsets
    zOffset = dimensions["logo_offset"] + (dimensions["height"] if flatBrickType(brickType) and size[2] == 3 else 0)
    lw = dimensions["logo_width"] * (0.78 if logoType == "LEGO" else logoScale)
    distMax = max(logo_details.dist.xy)
    zOffset += ((logo_details.dist.z * (lw / distMax)) / 2) * (1 - logoInset * 2)
    xyOffset = dimensions["width"] + dimensions["gap"]
    # cap x/y ranges so logos aren't created over slopes
    xR0 = size[0] - 1 if direction == "X-" else 0
    yR0 = size[1] - 1 if direction == "Y-" else 0
    xR1 = 1 if direction == "X+" else size[0]
    yR1 = 1 if direction == "Y+" else size[1]
    # add logos on top of each stud
    for i,zRot in enumerate(zRots):
        m0 = m.copy()
        # rotate logo around stud
        if zRot != 0: m0.transform(Matrix.Rotation(math.radians(zRot), 4, 'Z'))
        # create logo for each stud and append to bm
        gap_base = dimensions["gap"] * Vector(((xR1 - xR0 - 1) / 2, (yR1 - yR0 - 1) / 2))
        for x in range(xR0, xR1):
            for y in range(yR0, yR1):
                # create duplicate of rotated logo
                m1 = m0.copy()
                # adjust gap based on distance from first stud
                gap = gap_base + dimensions["gap"] * Vector((x / xR1, y / yR1))
                # translate logo into place
                m1.transform(Matrix.Translation((x * xyOffset - gap.x, y * xyOffset - gap.y, zOffset)))
                # add transformed mesh to bm mesh
                bms[i].from_mesh(m1)
                bpy.data.meshes.remove(m1)
        bpy.data.meshes.remove(m0)
    return bms
