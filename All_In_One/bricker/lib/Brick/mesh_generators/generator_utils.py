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


def addSupports(dimensions, height, brickSize, brickType, loopCut, circleVerts, type, detail, d, scalar, thick, bme, hollow=None, add_beams=None):
    # initialize vars
    if hollow is None:
        add_beams = brickSize[2] == 3 and (sum(brickSize[:2]) > 4 or min(brickSize[:2]) == 1 and max(brickSize[:2]) == 3) and detail in ("MEDIUM", "HIGH")
        hollow = brickSize[2] == 1 or min(brickSize[:2]) != 1
    bAndPBrick = flatBrickType(brickType) and brickSize[2] == 3
    minS = min(brickSize[:2])
    sides = [0, 1] + ([0, 0, 1, 1] if brickSize[0] < brickSize[1] else [1, 1, 0, 0])
    sides2 = [0, 1] + ([1, 1, 0, 0] if brickSize[0] < brickSize[1] else [0, 0, 1, 1])
    z1 = d.z - height * 0.99975 if minS > 2 else (d.z - thick.z - dimensions["support_height_triple" if bAndPBrick else "support_height"])
    z2 = d.z - thick.z
    r = dimensions["stud_radius"] if min(brickSize[:2]) != 1 else dimensions["bar_radius"] - (dimensions["tube_thickness"] if hollow else 0)
    h = height - thick.z
    t = dimensions["tube_thickness"]
    tubeZ = -(thick.z / 2)
    allTopVerts = []
    startX = -1 if brickSize[0] == 1 else 0
    startY = -1 if brickSize[1] == 1 else 0
    startX = 1 if type == "SLOPE" and brickSize[:2] in ([3, 1], [4, 1]) else startX
    startY = 1 if type == "SLOPE" and brickSize[:2] in ([1, 3], [1, 4]) else startY
    # add supports for each appropriate underside location
    for xNum in range(startX, brickSize[0] - 1):
        for yNum in range(startY, brickSize[1] - 1):
            if minS > 2 and (xNum + yNum) % 2 == 1:
                continue
            # add support tubes
            tubeX = (xNum * d.x * 2) + d.x * (2 if brickSize[0] == 1 else 1)
            tubeY = (yNum * d.y * 2) + d.y * (2 if brickSize[1] == 1 else 1)
            if hollow:
                bme, tubeVerts = makeTube(r, h, t, circleVerts, co=Vector((tubeX, tubeY, tubeZ)), botFace=True, topFace=False, loopCutTop=loopCut, bme=bme)
                selectVerts(tubeVerts["outer"]["top"] + tubeVerts["inner"]["top"])
                allTopVerts += tubeVerts["outer"]["top"] + tubeVerts["inner"]["top"]
            else:
                bme, tubeVerts = makeCylinder(r, h, circleVerts, co=Vector((tubeX, tubeY, tubeZ)), botFace=True, topFace=False, bme=bme)
                selectVerts(tubeVerts["top"])
                allTopVerts += tubeVerts["top"]
            # add support beams next to odd tubes
            if not add_beams:
                continue
            if minS % 2 == 0 and (brickSize[0] > brickSize[1] or minS > 2):
                if brickSize[0] == 3 or xNum % 2 == 1 or (brickSize == [8, 1, 3] and xNum in (0, brickSize[0] - 2)):
                    # initialize x, y
                    x1 = tubeX - (dimensions["support_width"] / 2)
                    x2 = tubeX + (dimensions["support_width"] / 2)
                    y1 = tubeY + r
                    y2 = tubeY + d.y * min([minS, 4]) - thick.y - (0 if yNum >= brickSize[1] - 3 else dimensions["tube_thickness"])
                    y3 = tubeY - d.y * min([minS, 4]) + thick.y
                    y4 = tubeY - r
                    # create support beam
                    curSides = sides if brickSize[0] > brickSize[1] else sides2
                    if minS == 1:
                        cubeVerts = makeCube(Vector((x1, y3, z1)), Vector((x2, y2, z2)), sides=curSides, bme=bme)
                        allTopVerts += cubeVerts[4:]
                    else:
                        cubeVerts1 = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), sides=curSides, bme=bme)
                        allTopVerts += cubeVerts1[4:]
                        if yNum <= 1:
                            cubeVerts2 = makeCube(Vector((x1, y3, z1)), Vector((x2, y4, z2)), sides=curSides, bme=bme)
                            allTopVerts += cubeVerts2[4:]
            if minS % 2 == 0 and (brickSize[1] > brickSize[0] or minS > 2):
                if brickSize[1] == 3 or yNum % 2 == 1 or (brickSize == [1, 8, 3] and yNum in (0, brickSize[1] - 2)):
                    # initialize x, y
                    x1 = tubeX + r
                    x2 = tubeX + d.x * min([minS, 4]) - thick.x - (0 if xNum >= brickSize[0] - 3 else dimensions["tube_thickness"])
                    x3 = tubeX - d.x * min([minS, 4]) + thick.x
                    x4 = tubeX - r
                    y1 = tubeY - (dimensions["support_width"] / 2)
                    y2 = tubeY + (dimensions["support_width"] / 2)
                    curSides = sides if brickSize[1] > brickSize[0] else sides2
                    # create support beam
                    if minS == 1:
                        cubeVerts = makeCube(Vector((x3, y1, z1)), Vector((x2, y2, z2)), sides=curSides, bme=bme)
                        allTopVerts += cubeVerts[4:]
                    else:
                        cubeVerts1 = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), sides=curSides, bme=bme)
                        allTopVerts += cubeVerts1[4:]
                        if xNum <= 1:
                            cubeVerts2 = makeCube(Vector((x3, y1, z1)), Vector((x4, y2, z2)), sides=curSides, bme=bme)
                            allTopVerts += cubeVerts2[4:]
    if type == "SLOPE":
        cutVerts(dimensions, height, brickSize, allTopVerts, d, scalar, thick, bme)


def addOblongSupport(dimensions, height, loopCut, circleVerts, type, detail, d, scalar, thick, bme):
    # round circleVerts to multiple of 4
    circleVerts = round_up(circleVerts, 4)
    # initialize innerVerts
    innerVerts = {"top":{"-":[], "+":[]}, "mid":{"-":[], "+":[]}, "bottom":{"-":[], "+":[]}}
    # get support tube dimensions
    tubeX = 0
    tubeY1 = round(d.y - dimensions["oblong_support_dist"], 8)
    tubeY2 = round(d.y + dimensions["oblong_support_dist"], 8)
    tubeZ = -(thick.z - dimensions["slit_depth"]) / 2
    r = dimensions["oblong_support_radius"]
    h = height - (thick.z + dimensions["slit_depth"])
    # generate parallel cylinders
    bme, tubeVerts1 = makeCylinder(r, h, circleVerts, co=Vector((tubeX, tubeY1, tubeZ)), botFace=True, topFace=False, loopCut=loopCut, bme=bme)
    bme, tubeVerts2 = makeCylinder(r, h, circleVerts, co=Vector((tubeX, tubeY2, tubeZ)), botFace=True, topFace=False, loopCut=loopCut, bme=bme)
    selectVerts((tubeVerts1["mid"] + tubeVerts2["mid"]) if loopCut else (tubeVerts1["top"] + tubeVerts2["top"]))
    # remove half of cylinders and populate 'innerVerts'
    for side in ["top", "bottom"] + (["mid"] if loopCut else []):
        halfCircs1 = []
        halfCircs2 = []
        for v in tubeVerts1[side]:
            co_y = round(v.co.y, 8)
            if co_y > tubeY1:
                bme.verts.remove(v)
            else:
                halfCircs1.append(v)
            if co_y == tubeY1:
                innerVerts[side]["-"].append(v)
        for v in tubeVerts2[side]:
            co_y = round(v.co.y, 8)
            if co_y < tubeY2:
                bme.verts.remove(v)
            else:
                halfCircs2.append(v)
            if co_y == tubeY2:
                innerVerts[side]["+"].append(v)
        if side == "bottom":
            bme.faces.new(sorted(halfCircs1, key=lambda x: -x.co.x) + sorted(halfCircs2, key=lambda x: x.co.x))
    # connect half-cylinders
    if loopCut:
        bme.faces.new((innerVerts["top"]["+"][0], innerVerts["top"]["-"][0], innerVerts["mid"]["-"][0], innerVerts["mid"]["+"][0]))
        bme.faces.new((innerVerts["top"]["-"][1], innerVerts["top"]["+"][1], innerVerts["mid"]["+"][1], innerVerts["mid"]["-"][1]))
        bme.faces.new((innerVerts["mid"]["+"][0], innerVerts["mid"]["-"][0], innerVerts["bottom"]["-"][1], innerVerts["bottom"]["+"][1]))
        bme.faces.new((innerVerts["mid"]["-"][1], innerVerts["mid"]["+"][1], innerVerts["bottom"]["+"][0], innerVerts["bottom"]["-"][0]))
    else:
        bme.faces.new((innerVerts["top"]["+"][0], innerVerts["top"]["-"][0], innerVerts["bottom"]["-"][1], innerVerts["bottom"]["+"][1]))
        bme.faces.new((innerVerts["top"]["-"][1], innerVerts["top"]["+"][1], innerVerts["bottom"]["+"][0], innerVerts["bottom"]["-"][0]))
    # add low beam next to oblong support
    support_width = dimensions["slope_support_width"]
    support_height = dimensions["slope_support_height"]
    cubeY1 = round(d.y - support_width/2, 8)
    cubeY2 = round(d.y + support_width/2, 8)
    coord1 = Vector((r, cubeY1, d.z - thick.z - support_height))
    coord2 = Vector((d.x - thick.x + (dimensions["tick_depth"] if detail == "HIGH" else 0), cubeY2, d.z - thick.z))
    makeCube(coord1, coord2, sides=[0,1,0,0,1,1], bme=bme)
    coord1 = Vector((-d.x + thick.x, cubeY1, d.z - thick.z - support_height))
    coord2 = Vector((-r, cubeY2, d.z - thick.z))
    makeCube(coord1, coord2, sides=[0,1,0,0,1,1], bme=bme)



def addSlopeStuds(dimensions, height, brickSize, brickType, circleVerts, bme, edgeXp=None, edgeXn=None, edgeYp=None, edgeYn=None, underside=False, loopCut=False):
    r = dimensions["stud_radius"] if underside else dimensions["bar_radius"]
    h = dimensions["stud_height"]
    t = dimensions["stud_radius"] - dimensions["bar_radius"]
    z = (dimensions["stud_height"] + (-height if underside else height)) / 2
    sMin = edgeYp[0].co
    sMax = edgeYp[1].co
    sDistX = sMax.x - sMin.x
    sDistZ = sMax.z - sMin.z
    endVerts = []
    allSemiCircleVerts = []
    # round circleVerts if underside
    if underside: circleVerts = round_up(circleVerts, 4)
    # make studs
    topVertsDofDs = {}
    # for xNum in range(1, max(brickSize[:2])):
    #     for yNum in range(min(brickSize[:2])):
    for xNum in range(1, brickSize[0]):
        for yNum in range(brickSize[1]):
            x = dimensions["width"] * xNum
            y = dimensions["width"] * yNum
            if underside:
                _, studVerts = makeCylinder(r, h, circleVerts, co=Vector((x, y, z)), botFace=False, flipNormals=True, bme=bme)
                # move bottom verts of tubes to slope plane
                for v in studVerts["bottom"]:
                    curRatio = (v.co.x - sMin.x) / sDistX
                    v.co.z = sMin.z + sDistZ * curRatio
                # move top verts of tubes to middle of bottom verts
                zAve = sum([v.co.z for v in studVerts["bottom"]]) / len(studVerts["bottom"])
                for v in studVerts["top"]:
                    v.co.z = zAve
                # remove half of cylinder
                for v in studVerts["bottom"]:
                    if round(v.co.x, 8) > x:
                        bme.verts.remove(v)
                for v in studVerts["top"]:
                    if round(v.co.x, 8) >= x:
                        bme.verts.remove(v)
                f0 = bme.faces.new((studVerts["bottom"][circleVerts // 4 - 1], studVerts["bottom"][circleVerts // 4], studVerts["top"][(circleVerts // 4) * 3 - 1]))
                f1 = bme.faces.new((studVerts["bottom"][(circleVerts // 4) * 3 - 2], studVerts["bottom"][(circleVerts // 4) * 3 - 1], studVerts["top"][circleVerts // 4 + 1]))
                f0.smooth = True
                f1.smooth = True
                bme.faces.new([v for v in studVerts["top"][::-1] if v.is_valid] + [studVerts["bottom"][(circleVerts // 4) * 3 - 1], studVerts["bottom"][circleVerts // 4 - 1]])
                if yNum == 0:
                    bme.faces.new((edgeXn[0], edgeXp[1], studVerts["bottom"][circleVerts // 4 - 1]))
                if yNum == min(brickSize[:2]) - 1:
                    bme.faces.new((edgeXp[0], edgeXn[1], studVerts["bottom"][(circleVerts // 4) * 3 - 1]))
                endVerts += [studVerts["bottom"][circleVerts // 4 - 1], studVerts["bottom"][(circleVerts // 4) * 3 - 1]]
                allSemiCircleVerts += [v for v in studVerts["bottom"] if v.is_valid]
            else:
                _, studVerts = makeTube(r, h, t, circleVerts, co=Vector((x, y, z)), botFace=False, bme=bme)
                # move bottom verts of tubes to slope plane
                for key in studVerts:
                    for v in studVerts[key]["bottom"]:
                        curRatio = (v.co.x - sMin.x) / sDistX
                        v.co.z = sMin.z + sDistZ * curRatio
                if edgeXp is not None: bme.faces.new(studVerts["inner"]["bottom"][::1 if underside else -1])
                selectVerts(studVerts["inner"]["mid" if loopCut else "bottom"] + studVerts["outer"]["mid" if loopCut else "bottom"])
                if edgeXp is not None:
                    adjXNum = xNum - 1
                    topVertsD = createVertListDict2(studVerts["bottom"] if underside else studVerts["outer"]["bottom"])
                    topVertsDofDs["%(adjXNum)s,%(yNum)s" % locals()] = topVertsD
    if edgeXp is not None and not underside:
        connectCirclesToSquare(dimensions, [brickSize[0] - 1, brickSize[1], brickSize[2]], circleVerts, edgeXn[::-1], edgeXp, edgeYn, edgeYp[::-1], topVertsDofDs, xNum - 1, yNum, bme, flipNormals=not underside)
    if underside:
        bme.faces.new((edgeXp + allSemiCircleVerts)[::-1])
        bme.faces.new(edgeXn[::-1] + endVerts)
    return studVerts


def cutVerts(dimensions, height, brickSize, verts, d, scalar, thick, bme):
    minZ = -(height / 2) + thick.z
    for v in verts:
        numer = v.co.x - d.x
        denom = d.x * (scalar.x - 1) - (dimensions["tube_thickness"] + dimensions["stud_radius"]) * (brickSize[0] - 2) + (thick.z * (brickSize[0] - 3))
        fac = numer / denom
        if fac < 0:
            continue
        v.co.z = fac * minZ + (1-fac) * v.co.z


def addInnerCylinders(dimensions, brickSize, circleVerts, d, edgeXp, edgeXn, edgeYp, edgeYn, bme, loopCut=False):
    thickZ = dimensions["thickness"]
    # make small cylinders
    botVertsDofDs = {}
    r = dimensions["stud_radius"]-(2 * thickZ)
    N = circleVerts
    h = thickZ * 0.99
    for xNum in range(brickSize[0]):
        for yNum in range(brickSize[1]):
            bme, innerCylinderVerts = makeCylinder(r, h, N, co=Vector((xNum*d.x*2,yNum*d.y*2,d.z - thickZ + h/2)), loopCut=loopCut, botFace=False, flipNormals=True, bme=bme)
            if loopCut:
                selectVerts(innerCylinderVerts["mid"])
            botVertsD = createVertListDict(innerCylinderVerts["bottom"])
            botVertsDofDs["%(xNum)s,%(yNum)s" % locals()] = botVertsD
    connectCirclesToSquare(dimensions, brickSize, circleVerts, edgeXp, edgeXn, edgeYp, edgeYn, botVertsDofDs, xNum, yNum, bme)


def addStuds(dimensions, height, brickSize, brickType, circleVerts, bme, edgeXp=None, edgeXn=None, edgeYp=None, edgeYn=None, hollow=False, botFace=True, loopCut=False):
    r = dimensions["bar_radius" if hollow else "stud_radius"]
    h = dimensions["stud_height"]
    t = dimensions["stud_radius"] - dimensions["bar_radius"]
    z = height / 2 + dimensions["stud_height"] / 2
    # make studs
    topVertsDofDs = {}
    for xNum in range(brickSize[0]):
        for yNum in range(brickSize[1]):
            x = dimensions["width"] * xNum
            y = dimensions["width"] * yNum
            if hollow:
                _, studVerts = makeTube(r, h, t, circleVerts, co=Vector((0, 0, z)), loopCut=loopCut, botFace=botFace, bme=bme)
                if edgeXp is not None: bme.faces.new(studVerts["inner"]["bottom"])
                selectVerts(studVerts["inner"]["mid" if loopCut else "bottom"] + studVerts["outer"]["mid" if loopCut else "bottom"])
            else:
                # split stud at center by creating cylinder and circle and joining them (allows Bevel to work correctly)
                _, studVerts = makeCylinder(r, h, circleVerts, co=Vector((x, y, z)), botFace=False, loopCut=loopCut, bme=bme)
                selectVerts(studVerts["mid" if loopCut else "bottom"])
            if edgeXp is not None:
                topVertsD = createVertListDict2(studVerts["outer"]["bottom"] if hollow else studVerts["bottom"])
                topVertsDofDs["%(xNum)s,%(yNum)s" % locals()] = topVertsD
    if edgeXp is not None:
        connectCirclesToSquare(dimensions, brickSize, circleVerts, edgeXp, edgeXn, edgeYp, edgeYn, topVertsDofDs, xNum, yNum, bme, flipNormals=True)
    return studVerts


def connectCirclesToSquare(dimensions, brickSize, circleVerts, edgeXp, edgeXn, edgeYp, edgeYn, vertsDofDs, xNum, yNum, bme, flipNormals=False):
    # joinVerts = {"Y+":[v7, v8], "Y-":[v6, v5], "X+":[v7, v6], "X-":[v8, v5]}
    thickZ = dimensions["thickness"]
    sX = brickSize[0]
    sY = brickSize[1]
    step = -1 if flipNormals else 1
    # Make corner faces if few cylinder verts
    v5 = edgeYn[-1]
    v6 = edgeYn[0]
    v7 = edgeYp[0]
    v8 = edgeYp[-1]
    l = "0,0"
    if len(vertsDofDs[l]["--"]) == 0:
        vList = bme.faces.new((vertsDofDs[l]["y-"][0], vertsDofDs[l]["x-"][0], v5)[::-step])
    l = "%(xNum)s,0" % locals()
    if len(vertsDofDs[l]["+-"]) == 0:
        vList = bme.faces.new((vertsDofDs[l]["x+"][0], vertsDofDs[l]["y-"][0], v6)[::-step])
    l = "%(xNum)s,%(yNum)s" % locals()
    if len(vertsDofDs[l]["++"]) == 0:
        vList = bme.faces.new((vertsDofDs[l]["y+"][0], vertsDofDs[l]["x+"][0], v7)[::-step])
    l = "0,%(yNum)s" % locals()
    if len(vertsDofDs[l]["-+"]) == 0:
        vList = bme.faces.new((vertsDofDs[l]["x-"][0], vertsDofDs[l]["y+"][0], v8)[::-step])

    # Make edge faces
    joinVerts = {"Y+":edgeYp, "Y-":edgeYn, "X+":edgeXp, "X-":edgeXn}
    # Make edge faces on Y- and Y+ sides
    for xNum in range(sX):
        vertDpos = vertsDofDs[str(xNum) + "," + str(yNum)]
        vertDneg = vertsDofDs[str(xNum) + "," + str(0)]
        for sign, vertD, dir, func in (["+", vertDpos, 1, math.ceil], ["-", vertDneg, -1, math.floor]):
            side = "Y%(sign)s" % locals()
            verts = vertD["-%(sign)s" % locals()]
            if xNum > 0:
                joinVerts[side].append(vertD["x-"][0])
                for v in verts[::dir]:
                    joinVerts[side].append(v)
            else:
                for v in verts[::dir][func(len(verts)/2) - (1 if dir == 1 else 0):]:
                    joinVerts[side].append(v)
            joinVerts[side].append(vertD["y%(sign)s" % locals()][0])
            verts = vertD["+%(sign)s" % locals()]
            if xNum < sX - 1:
                for v in verts[::dir]:
                    joinVerts[side].append(v)
                joinVerts[side].append(vertD["x+"][0])
            else:
                for v in verts[::dir][:func(len(verts)/2) + (1 if dir == -1 else 0)]:
                    joinVerts[side].append(v)
    # Make edge faces on X- and X+ sides
    for yNum in range(sY):
        vertDpos = vertsDofDs[str(xNum) + "," + str(yNum)]
        vertDneg = vertsDofDs[str(0) + "," + str(yNum)]
        for sign, vertD, dir, func in (["+", vertDpos, -1, math.floor], ["-", vertDneg, 1, math.ceil]):
            side = "X%(sign)s" % locals()
            verts = vertD["%(sign)s-" % locals()]
            if yNum > 0:
                joinVerts[side].append(vertD["y-"][0])
                for v in verts[::dir]:
                    joinVerts[side].append(v)
            else:
                for v in verts[::dir][func(len(verts)/2) - (1 if dir == 1 else 0):]:
                    joinVerts[side].append(v)
            joinVerts[side].append(vertD["x%(sign)s" % locals()][0])
            verts = vertD["%(sign)s+" % locals()]
            if yNum < sY - 1:
                for v in verts[::dir]:
                    joinVerts[side].append(v)
                joinVerts[side].append(vertD["y+"][0])
            else:
                for v in verts[::dir][:func(len(verts)/2) + (1 if dir == -1 else 0)]:
                    joinVerts[side].append(v)
    for item in joinVerts:
        step0 = -step if item in ("Y+", "X-") else step
        bme.faces.new(joinVerts[item][::step0])

    if 1 in brickSize[:2]:
        return

    # Make center faces
    for yNum in range(sY - 1):
        for xNum in range(sX - 1):
            verts = []
            l = str(xNum) + "," + str(yNum)
            verts += vertsDofDs[l]["y+"]
            verts += vertsDofDs[l]["++"]
            verts += vertsDofDs[l]["x+"]
            l = str(xNum + 1) + "," + str(yNum)
            verts += vertsDofDs[l]["x-"]
            verts += vertsDofDs[l]["-+"]
            verts += vertsDofDs[l]["y+"]
            l = str(xNum + 1) + "," + str(yNum + 1)
            verts += vertsDofDs[l]["y-"]
            verts += vertsDofDs[l]["--"]
            verts += vertsDofDs[l]["x-"]
            l = str(xNum) + "," + str(yNum + 1)
            verts += vertsDofDs[l]["x+"]
            verts += vertsDofDs[l]["+-"]
            verts += vertsDofDs[l]["y-"]
            bme.faces.new(verts[::-step])


def addTickMarks(dimensions, brickSize, circleVerts, detail, d, thick, bme, nno=None, npo=None, ppo=None, pno=None, nni=None, npi=None, ppi=None, pni=None, nnt=None, npt=None, ppt=None, pnt=None, inverted_slope=False, sideMarks=True):
    # for edge vert refs, n=negative, p=positive, o=outer, i=inner, t=top
    joinVerts = {"X-":[npi, npo, nno, nni], "X+":[ppi, ppo, pno, pni], "Y-":[pni, pno, nno, nni], "Y+":[ppi, ppo, npo, npi]}
    lastSideVerts = {"X-":[nnt, nni], "X+":[pni, pnt], "Y-":[nni, nnt], "Y+":[npt, npi]}
    bottomVerts = {"X-":[], "X+":[], "Y-":[], "Y+":[]}
    tick_depth = dimensions["slope_tick_depth"] if inverted_slope else dimensions["tick_depth"]
    tick_width = dimensions["support_width"] if inverted_slope else dimensions["tick_width"]
    # make tick marks
    for xNum in range(brickSize[0]):
        for yNum in range(brickSize[1]):
            # initialize z
            z1 = -d.z
            z2 = d.z - thick.z
            if xNum == 0 and sideMarks:
                # initialize x, y
                x1 = -d.x + thick.x
                x2 = -d.x + thick.x + tick_depth
                y1 = yNum * d.y * 2 - tick_width / 2
                y2 = yNum * d.y * 2 + tick_width / 2
                # CREATING SUPPORT BEAM
                v1, v2, _, _, v5, v6, v7, v8 = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), sides=[0, 1, 1, 0, 1, 1], bme=bme)
                joinVerts["X-"] += [v1, v2]
                bme.faces.new([v1, v5] + lastSideVerts["X-"])
                lastSideVerts["X-"] = [v8, v2]
                bottomVerts["X-"] += [v5, v6, v7, v8]
            elif xNum == brickSize[0]-1:
                # initialize x, y
                x1 = xNum * d.x * 2 + d.x - thick.x - tick_depth
                x2 = xNum * d.x * 2 + d.x - thick.x
                y1 = yNum * d.y * 2 - tick_width / 2
                y2 = yNum * d.y * 2 + tick_width / 2
                # CREATING SUPPORT BEAM
                _, _, v3, v4, v5, v6, v7, v8 = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), sides=[0, 1, 0, 1, 1, 1], bme=bme)
                joinVerts["X+"] += [v4, v3]
                bme.faces.new([v6, v4] + lastSideVerts["X+"])
                lastSideVerts["X+"] = [v3, v7]
                bottomVerts["X+"] += [v6, v5, v8, v7]
            if yNum == 0 and sideMarks:
                # initialize x, y
                y1 = -d.y + thick.y
                y2 = -d.y + thick.y + tick_depth
                x1 = xNum * d.x * 2 - tick_width / 2
                x2 = xNum * d.x * 2 + tick_width / 2
                # CREATING SUPPORT BEAM
                v1, _, _, v4, v5, v6, v7, v8 = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), sides=[0, 1, 1, 1, 1, 0], bme=bme)
                joinVerts["Y-"] += [v1, v4]
                bme.faces.new([v5, v1] + lastSideVerts["Y-"])
                lastSideVerts["Y-"] = [v4, v6]
                bottomVerts["Y-"] += [v5, v8, v7, v6]
            elif yNum == brickSize[1]-1 and sideMarks:
                # initialize x, y
                x1 = xNum * d.x * 2 - tick_width / 2
                x2 = xNum * d.x * 2 + tick_width / 2
                y1 = yNum * d.y * 2 + d.y - thick.y - tick_depth
                y2 = yNum * d.y * 2 + d.y - thick.y
                # CREATING SUPPORT BEAM
                _, v2, v3, _, v5, v6, v7, v8 = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), sides=[0, 1, 1, 1, 0, 1], bme=bme)
                # select bottom connecting verts for exclusion from vertex group
                joinVerts["Y+"] += [v2, v3]
                bme.faces.new([v2, v8] + lastSideVerts["Y+"])
                lastSideVerts["Y+"] = [v7, v3]
                bottomVerts["Y+"] += [v8, v5, v6, v7]

    # draw faces between ticks and base
    bme.faces.new(joinVerts["X+"])
    bme.faces.new([ppt, ppi] + lastSideVerts["X+"])
    if sideMarks:
        bme.faces.new(joinVerts["X-"][::-1])
        bme.faces.new([npi, npt] + lastSideVerts["X-"])
        bme.faces.new(joinVerts["Y-"])
        bme.faces.new(joinVerts["Y+"][::-1])
        bme.faces.new([pnt, pni] + lastSideVerts["Y-"])
        bme.faces.new([ppi, ppt] + lastSideVerts["Y+"])

    return bottomVerts


def createVertListDict(verts):
    idx1 = int(round(len(verts) * 1 / 4)) - 1
    idx2 = int(round(len(verts) * 2 / 4)) - 1
    idx3 = int(round(len(verts) * 3 / 4)) - 1
    idx4 = int(round(len(verts) * 4 / 4)) - 1

    vertListBDict = {"++":[verts[idx] for idx in range(idx1 + 1, idx2)],
                     "+-":[verts[idx] for idx in range(idx2 + 1, idx3)],
                     "--":[verts[idx] for idx in range(idx3 + 1, idx4)],
                     "-+":[verts[idx] for idx in range(0,        idx1)],
                     "y+":[verts[idx1]],
                     "x+":[verts[idx2]],
                     "y-":[verts[idx3]],
                     "x-":[verts[idx4]]}

    return vertListBDict


def createVertListDict2(verts):
    idx1 = int(round(len(verts) * 1 / 4)) - 1
    idx2 = int(round(len(verts) * 2 / 4)) - 1
    idx3 = int(round(len(verts) * 3 / 4)) - 1
    idx4 = int(round(len(verts) * 4 / 4)) - 1

    vertListBDict = {"--":[verts[idx] for idx in range(idx1 + 1, idx2)],
                     "-+":[verts[idx] for idx in range(idx2 + 1, idx3)],
                     "++":[verts[idx] for idx in range(idx3 + 1, idx4)],
                     "+-":[verts[idx] for idx in range(0,        idx1)],
                     "y-":[verts[idx1]],
                     "x-":[verts[idx2]],
                     "y+":[verts[idx3]],
                     "x+":[verts[idx4]]}

    return vertListBDict


def addGrillDetails(dimensions, brickSize, thick, scalar, d, v1, v2, v3, v4, v9, v10, v11, v12, bme):
    # NOTE: n=negative, p=positive, m=middle
    # inner support in middle
    x1 = dimensions["stud_radius"]
    x2 = dimensions["stud_radius"] + (d.x - dimensions["stud_radius"]) * 2
    y1 = -dimensions["thickness"] / 2
    y2 =  dimensions["thickness"] / 2
    z1 = -d.z
    z2 = d.z - dimensions["thickness"]
    mms = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), [0, 1, 1, 1, 1, 1], bme=bme)

    z1 = d.z - dimensions["thickness"]
    z2 = d.z
    # upper middle x- grill
    x1 = -d.x
    x2 = -d.x + dimensions["thickness"]
    nmg = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), [1, 0, 0, 1, 1, 1], bme=bme)
    # upper y- x- grill
    y3 = y1 - dimensions["thickness"] * 2
    y4 = y2 - dimensions["thickness"] * 2
    nng = makeCube(Vector((x1, y3, z1)), Vector((x2, y4, z2)), [1, 0, 0, 1, 1, 1], bme=bme)
    bme.verts.remove(nng[3])
    nng[3] = None
    # upper y+ x- grill
    y3 = y1 + dimensions["thickness"] * 2
    y4 = y2 + dimensions["thickness"] * 2
    npg = makeCube(Vector((x1, y3, z1)), Vector((x2, y4, z2)), [1, 0, 0, 1, 1, 1], bme=bme)
    bme.verts.remove(npg[2])
    npg[2] = None

    # upper middle x+ grill
    x1 = d.x * 3 - dimensions["thickness"]
    x2 = d.x * 3
    pmg = makeCube(Vector((x1, y1, z1)), Vector((x2, y2, z2)), [1, 0, 1, 0, 1, 1], bme=bme)
    # upper y- x+ grill
    y3 = y1 - dimensions["thickness"] * 2
    y4 = y2 - dimensions["thickness"] * 2
    png = makeCube(Vector((x1, y3, z1)), Vector((x2, y4, z2)), [1, 0, 1, 0, 1, 1], bme=bme)
    bme.verts.remove(png[0])
    png[0] = None
    # upper y+ x+ grill
    y3 = y1 + dimensions["thickness"] * 2
    y4 = y2 + dimensions["thickness"] * 2
    ppg = makeCube(Vector((x1, y3, z1)), Vector((x2, y4, z2)), [1, 0, 1, 0, 1, 1], bme=bme)
    bme.verts.remove(ppg[1])
    ppg[1] = None

    # connect grill tops
    bme.faces.new((pmg[4], pmg[7], nmg[6], nmg[5]))
    bme.faces.new((png[4], png[7], nng[6], nng[5]))
    bme.faces.new((ppg[4], ppg[7], npg[6], npg[5]))
    # connect outer sides
    bme.faces.new((v4, png[3], png[5], nng[4], nng[0], v1))
    bme.faces.new((v2, npg[1], npg[7], ppg[6], ppg[2], v3))
    bme.faces.new((v3, ppg[2], ppg[3], pmg[2], pmg[3], png[2], png[3], v4))
    bme.faces.new((v1, nng[0], nng[1], nmg[0], nmg[1], npg[0], npg[1], v2))
    # connect grills together
    bme.faces.new((nng[1], nng[2], nmg[3], nmg[0]))
    bme.faces.new((nmg[1], nmg[2], npg[3], npg[0]))
    bme.faces.new((png[1], png[2], pmg[3], pmg[0]))
    bme.faces.new((pmg[1], pmg[2], ppg[3], ppg[0]))
    bme.faces.new((nmg[5], nmg[3], mms[4], mms[5], pmg[0], pmg[4]))
    bme.faces.new((pmg[7], pmg[1], mms[6], mms[7], nmg[2], nmg[6]))
    # connect grill to base
    bme.faces.new((nmg[2], mms[7], mms[4], nmg[3]))
    bme.faces.new((pmg[0], mms[5], mms[6], pmg[1]))
    # create square at inner base
    coord1 = -d + Vector((thick.x, thick.y, 0))
    coord2 = vec_mult(d, scalar) - thick
    coord2.z = -d.z
    v17, v18, v19, v20 = makeSquare(coord1, coord2, face=False, bme=bme)
    # connect inner base to outer base
    bme.faces.new((v17, v9, v10, v20))
    bme.faces.new((v20, v10, v11, v19))
    bme.faces.new((v19, v11, v12, v18))
    bme.faces.new((v18, v12, v9, v17))
    # create inner faces
    if brickSize[0] < brickSize[1]:
        bme.faces.new((v17, v20, ppg[0], ppg[4], npg[5], npg[4]))
        bme.faces.new((v19, v18, nng[2], nng[6], png[7], png[1]))
        bme.faces.new((v20, v19, png[1], pmg[0], pmg[1], ppg[0]))
        bme.faces.new((v18, v17, npg[3], nmg[2], nmg[3], nng[2]))
    else:
        bme.faces.new((v20, v19, ppg[0], ppg[4], npg[5], npg[4]))
        bme.faces.new((v18, v17, nng[2], nng[6], png[7], png[1]))
        bme.faces.new((v19, v18, png[1], pmg[0], pmg[1], ppg[0]))
        bme.faces.new((v17, v20, npg[3], nmg[2], nmg[3], nng[2]))

    # rotate created vertices in to place if necessary
    if brickSize[0] < brickSize[1]:
        vertsCreated = nng + nmg + npg + png + pmg + ppg + mms
        vertsCreated = [v for v in vertsCreated if v is not None]
        bmesh.ops.rotate(bme, verts=vertsCreated, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Z'))
