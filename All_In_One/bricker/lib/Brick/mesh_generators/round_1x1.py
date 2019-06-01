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


def makeRound1x1(dimensions:dict, brickType:str, loopCut:bool, circleVerts:int=None, type:str="CYLINDER", detail:str="LOW", bme:bmesh=None):
    """
    create round 1x1 brick with bmesh

    Keyword Arguments:
        dimensions  -- dictionary containing brick dimensions
        brickType   -- cm.brickType
        loopCut     -- loop cut cylinders so bevels can be cleaner
        circleVerts -- number of vertices per circle of cylinders
        type        -- type of round 1x1 brick in ("CONE", "CYLINDER", "STUD", "STUD_HOLLOW")
        detail      -- level of brick detail (options: ("FLAT", "LOW", "MEDIUM", "HIGH"))
        bme         -- bmesh object in which to create verts

    """
    # ensure type argument passed is valid
    assert type in ("CONE", "CYLINDER", "STUD", "STUD_HOLLOW")
    # create new bmesh object
    bme = bmesh.new() if not bme else bme

    # store original detail amount
    origDetail = detail
    # cap detail level to medium detail
    detail = "MEDIUM" if "HIGH" else detail
    # if making cone, detail should always be high
    detail = "MEDIUM" if type == "CONE" else detail
    # if making stud, detail should never get beyond low
    detail = "LOW" if type == "STUD" and detail == "MEDIUM" else detail
    # if making hollow stud, detail should never get below medium
    detail = "MEDIUM" if type == "STUD_HOLLOW" else detail

    # set brick height and thickness
    height = dimensions["height"] if not flatBrickType(brickType) or "STUD" in type else dimensions["height"] * 3
    thick = Vector([dimensions["thickness"]] * 3)

    # create outer cylinder
    r = dimensions["width"] / 2
    h = height - dimensions["stud_height"]
    z = dimensions["stud_height"] / 2
    bme, vertsOuterCylinder = makeCylinder(r, h, circleVerts, co=Vector((0, 0, z)), botFace=False, topFace=False, loopCut=loopCut, bme=bme)
    # update upper cylinder verts for cone shape
    if type == "CONE":
        new_radius = dimensions["stud_radius"] * 1.075
        factor = new_radius / (dimensions["width"] / 2)
        for vert in vertsOuterCylinder["top"]:
            vert.co.xy = vec_mult(vert.co.xy, [factor]*2)
        if loopCut:
            new_radius0 = new_radius * (dimensions["width"] / (new_radius * 4) + 0.5)
            factor0 = new_radius0 / (dimensions["width"] / 2)
            for vert in vertsOuterCylinder["mid"]:
                vert.co.xy = vec_mult(vert.co.xy, [factor0]*2)
    # select verts for exclusion from vert group
    selectVerts(vertsOuterCylinder["mid" if loopCut else "bottom"])

    # create lower cylinder
    r = dimensions["stud_radius"]
    h = dimensions["stud_height"]
    t = (dimensions["width"] / 2 - r) / 2
    z = - (height / 2) + (dimensions["stud_height"] / 2)
    if detail == "FLAT":
        bme, lowerCylinderVerts = makeCylinder(r + t, h, circleVerts, co=Vector((0, 0, z)), topFace=False, loopCut=loopCut, bme=bme)
        # select verts for exclusion from vert group
        selectVerts(lowerCylinderVerts["mid" if loopCut else "top"])
    else:
        bme, lowerTubeVerts = makeTube(r, h, t, circleVerts, co=Vector((0, 0, z)), topFace=False, loopCut=loopCut, bme=bme)
        # remove unnecessary upper inner verts from tube
        for vert in lowerTubeVerts["inner"]["top"]:
            bme.verts.remove(vert)
        lowerTubeVerts["inner"]["top"] = []
        # select verts for exclusion from vert group
        selectVerts(lowerTubeVerts["outer"]["mid" if loopCut else "top"] + lowerTubeVerts["inner"]["mid" if loopCut else "top"])

    # add stud
    # studVerts = addStuds(dimensions, height, [1, 1, 1], type, circleVerts, bme, hollow=detail in ("MEDIUM", "HIGH"), loopCut=False)
    studVerts = addStuds(dimensions, height, [1, 1, 1], type, circleVerts, bme, hollow=detail in ("MEDIUM", "HIGH"), botFace=not loopCut, loopCut=loopCut)

    # make pointers to appropriate vertex lists
    studVertsOuter = studVerts if detail in ("FLAT", "LOW") else studVerts["outer"]
    studVertsInner = studVerts if detail in ("FLAT", "LOW") else studVerts["inner"]
    lowerTubeVertsOuter = lowerCylinderVerts if detail == "FLAT" else lowerTubeVerts["outer"]

    # create faces connecting bottom of stud to top of outer cylinder
    connectCircles(vertsOuterCylinder["top"], studVertsOuter["bottom"][::-1], bme)

    # create faces connecting bottom of outer cylinder with top of lower tube
    connectCircles(lowerTubeVertsOuter["top"], vertsOuterCylinder["bottom"][::-1], bme)

    # add detailing inside brick
    if detail != "FLAT":
        # create faces for cylinder inside brick
        botOutStudVerts = [bme.verts.new(v.co) for v in studVertsOuter["bottom"]] if loopCut else studVertsOuter["bottom"]
        _,faces = connectCircles(lowerTubeVerts["inner"]["mid" if loopCut else "bottom"][::-1 if loopCut else 1], botOutStudVerts, bme)
        smoothBMFaces(faces)
        # create small inner cylinder inside stud for medium/high detail
        if type == "STUD" and origDetail in ("MEDIUM", "HIGH"):
            # make small inner cylinders
            r = dimensions["stud_radius"]-(2 * thick.x)
            h = thick.z * 0.99
            z = thick.z + h / 2
            bme, innerCylinderVerts = makeCylinder(r, h, circleVerts, co=Vector((0, 0, z)), botFace=False, flipNormals=True, bme=bme)
            # create faces connecting bottom of inner cylinder with bottom of stud
            botInStudVerts = [bme.verts.new(v.co) for v in studVertsInner["bottom"]] if loopCut else studVertsInner["bottom"]
            connectCircles(botInStudVerts, innerCylinderVerts["bottom"], bme, offset=circleVerts // 2)
        # create face at top of cylinder inside brick
        elif detail == "LOW":
            bme.faces.new(botOutStudVerts)
        # connect bottom of inner hollow stud
        elif loopCut:
            connectCircles(botOutStudVerts, studVertsInner["bottom"], bme)

    return bme
