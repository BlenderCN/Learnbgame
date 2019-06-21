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
# NONE!

# Blender imports
import bpy

# Addon imports
from .functions import *
from ...functions import *


def updateMaterials(bricksDict, source, uv_images, keys, curFrame=None):
    """ sets all matNames in bricksDict based on near_face """
    scn, cm, n = getActiveContextInfo()
    useUVMap = cm.useUVMap and (len(source.data.uv_layers) > 0 or cm.uvImage is not None)
    if not useUVMap:
        uv_images = None
    elif len(uv_images) == 0:
        useUVMap = False
    rgba_vals = []
    # initialize variables
    if keys == "ALL": keys = list(bricksDict.keys())
    isSmoke = cm.isSmoke
    materialType = cm.materialType
    colorSnap = cm.colorSnap
    uvImage = cm.uvImage
    includeTransparency = cm.includeTransparency
    transWeight = cm.transparentWeight
    sss = cm.colorSnapSubsurface
    sssSat = cm.colorSnapSubsurfaceSaturation
    sat_mat = getSaturationMatrix(sssSat)
    specular = cm.colorSnapSpecular
    roughness = cm.colorSnapRoughness
    ior = cm.colorSnapIOR
    transmission = cm.colorSnapTransmission
    colorSnapAmount = cm.colorSnapAmount
    cm_id = cm.id
    # clear materials
    mat_name_start = "Bricker_{n}{f}".format(n=n, f="f_%(curFrame)s" % locals() if curFrame else "")
    for mat in bpy.data.materials:
        if mat.name.startswith(mat_name_start):
            bpy.data.materials.remove(mat)
    # get original matNames, and populate rgba_vals
    for key in keys:
        # skip irrelevant bricks
        nf = bricksDict[key]["near_face"]
        if not bricksDict[key]["draw"] or (nf is None and not isSmoke) or bricksDict[key]["custom_mat_name"]:
            continue
        # get RGBA value at nearest face intersection
        if isSmoke:
            rgba = bricksDict[key]["rgba"]
            matName = ""
        else:
            ni = Vector(bricksDict[key]["near_intersection"])
            rgba, matName = getBrickRGBA(scn, source, nf, ni, uv_images, uvImage)

        if materialType == "SOURCE":
            # get material with snapped RGBA value
            if rgba is None and useUVMap:
                matName = ""
            elif colorSnap == "ABS":
                # if original material was ABS plastic, keep it
                if rgba is None and matName in getColors().keys():
                    pass
                # otherwise, find nearest ABS plastic material to rgba value
                else:
                    matObj = getMatObject(cm_id, typ="ABS")
                    assert len(matObj.data.materials) > 0
                    matName = findNearestBrickColorName(rgba, transWeight, matObj=matObj)
            elif colorSnap == "RGB" or isSmoke or useUVMap:
                matName = createNewMaterial(n, rgba, rgba_vals, sss, sat_mat, specular, roughness, ior, transmission, colorSnap, colorSnapAmount, includeTransparency, curFrame)
            if rgba is not None:
                rgba_vals.append(rgba)
        elif materialType == "CUSTOM":
            matName = cm.customMat.name
        bricksDict[key]["mat_name"] = matName
    return bricksDict


def updateBrickSizes(bricksDict, key, availableKeys, loc, brickSizes, zStep, maxL, height3Only, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, mergeInconsistentMats=False, mergeVertical=False, tallType="BRICK", shortType="PLATE"):
    """ update 'brickSizes' with available brick sizes surrounding bricksDict[key] """
    if not mergeVertical:
        maxL[2] = 1
    newMax1 = maxL[1]
    newMax2 = maxL[2]
    breakOuter1 = False
    breakOuter2 = False
    # iterate in x direction
    for i in range(maxL[0]):
        # iterate in y direction
        for j in range(maxL[1]):
            # break case 1
            if j >= newMax1: break
            # break case 2
            key1 = listToStr((loc[0] + i, loc[1] + j, loc[2]))
            if not brickAvail(bricksDict, key, key1, mergeInternalsH, materialType, mergeInconsistentMats) or key1 not in availableKeys:
                if j == 0: breakOuter2 = True
                else:      newMax1 = j
                break
            # else, check vertically
            for k in range(0, maxL[2], zStep):
                # break case 1
                if k >= newMax2: break
                # break case 2
                key2 = listToStr((loc[0] + i, loc[1] + j, loc[2] + k))
                if not brickAvail(bricksDict, key, key2, mergeInternalsV, materialType, mergeInconsistentMats) or key2 not in availableKeys:
                    if k == 0: breakOuter1 = True
                    else:      newMax2 = k
                    break
                # bricks with 2/3 height can't exist
                elif k == 1: continue
                # else, append current brick size to brickSizes
                else:
                    newSize = [i+1, j+1, k+zStep]
                    if newSize in brickSizes:
                        continue
                    if not (newSize[2] == 1 and height3Only) and (not legalBricksOnly or legalBrickSize(size=newSize, type=tallType if newSize[2] == 3 else shortType)):
                        brickSizes.append(newSize)
            if breakOuter1: break
        breakOuter1 = False
        if breakOuter2: break


def attemptMerge(bricksDict, key, availableKeys, defaultSize, zStep, randState, brickType, maxWidth, maxDepth, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, loc=None, mergeInconsistentMats=False, preferLargest=False, mergeVertical=True, targetType=None, height3Only=False):
    """ attempt to merge bricksDict[key] with adjacent bricks """
    # get loc from key
    loc = loc or getDictLoc(bricksDict, key)
    brickSizes = [defaultSize]
    tallType = getTallType(bricksDict[key], targetType)
    shortType = getShortType(bricksDict[key], targetType)

    if brickType != "CUSTOM":
        # check width-depth and depth-width
        for i in (1, -1) if maxWidth != maxDepth else [1]:
            # iterate through adjacent locs to find available brick sizes
            updateBrickSizes(bricksDict, key, availableKeys, loc, brickSizes, zStep, [maxWidth, maxDepth][::i] + [3], height3Only, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, mergeInconsistentMats, mergeVertical=mergeVertical, tallType=tallType, shortType=shortType)
        # sort brick types from smallest to largest
        order = randState.randint(0,2)
        brickSizes.sort(key=lambda x: (x[0] * x[1] * x[2]) if preferLargest else (x[2], x[order], x[(order+1)%2]))

    # grab the biggest brick size and store to bricksDict
    brickSize = brickSizes[-1]
    bricksDict[key]["size"] = brickSize

    # set attributes for merged brick keys
    keysInBrick = getKeysInBrick(bricksDict, brickSize, zStep, loc=loc)
    for k in keysInBrick:
        bricksDict[k]["attempted_merge"] = True
        bricksDict[k]["parent"] = "self" if k == key else key
        # set brick type if necessary
        if flatBrickType(brickType):
            bricksDict[k]["type"] = shortType if brickSize[2] == 1 else tallType
    # set flipped and rotated
    setFlippedAndRotated(bricksDict, key, keysInBrick)
    if bricksDict[key]["type"] == "SLOPE" and brickType == "SLOPES":
        setBrickTypeForSlope(bricksDict, key, keysInBrick)

    return brickSize, keysInBrick


def getNumAlignedEdges(bricksDict, size, key, loc, bricksAndPlates=False):
    numAlignedEdges = 0
    locs = getLocsInBrick(bricksDict, size, 1, loc)
    gotOne = False

    for l in locs:
        # factor in height of brick (encourages)
        if bricksAndPlates and False:
            k0 = listToStr(l)
            try:
                p_brick0 = bricksDict[k0]["parent"]
            except KeyError:
                continue
            if p_brick0 == "self":
                p_brick0 = k
            if p_brick0 is None:
                continue
            p_brick_sz0 = bricksDict[p_brick0]["size"]
            numAlignedEdges -= p_brick_sz0[2] / 3
        # check number of aligned edges
        l[2] -= 1
        k = listToStr(l)
        try:
            p_brick_key = bricksDict[k]["parent"]
        except KeyError:
            continue
        if p_brick_key == "self":
            p_brick_key = k
        if p_brick_key is None:
            continue
        gotOne = True
        p_brick_sz = bricksDict[p_brick_key]["size"]
        p_brick_loc = getDictLoc(bricksDict, p_brick_key)
        # -X side
        if l[0] == loc[0] and p_brick_loc[0] == l[0]:
            numAlignedEdges += 1
        # -Y side
        if l[1] == loc[1] and p_brick_loc[1] == l[1]:
            numAlignedEdges += 1
        # +X side
        if l[0] == loc[0] + size[0] - 1 and p_brick_loc[0] + p_brick_sz[0] - 1 == l[0]:
            numAlignedEdges += 1
        # +Y side
        if l[1] == loc[1] + size[1] - 1 and p_brick_loc[1] + p_brick_sz[1] - 1 == l[1]:
            numAlignedEdges += 1

    if not gotOne:
        numAlignedEdges = size[0] * size[1] * 4

    return numAlignedEdges


def brickAvail(bricksDict, sourceKey, targetKey, mergeWithInternals, materialType, mergeInconsistentMats):
    """ check brick is available to merge """
    brick = bricksDict.get(targetKey)
    if brick is None:
        return False
    sourceBrick = bricksDict[sourceKey]
    # checks if brick materials can be merged (same material or one of the mats is "" (internal)
    matsMergable = sourceBrick["mat_name"] == brick["mat_name"] or (mergeWithInternals and "" in (sourceBrick["mat_name"], brick["mat_name"])) or mergeInconsistentMats
    # returns True if brick is present, brick isn't drawn already, and brick materials can be merged
    return brick["draw"] and not brick["attempted_merge"] and matsMergable and mergableBrickType(brick["type"], up=False)


def getMostCommonDir(i_s, i_e, norms):
    return most_common([n[i_s:i_e] for n in norms])

def setBrickTypeForSlope(bricksDict, key, keysInBrick):
    norms = [bricksDict[k]["near_normal"] for k in keysInBrick if bricksDict[k]["near_normal"] is not None]
    dir0 = getMostCommonDir(0, 1, norms) if len(norms) != 0 else ""
    if (dir0 == "^" and legalBrickSize(size=bricksDict[key]["size"], type="SLOPE") and bricksDict[key]["top_exposed"]):
        typ = "SLOPE"
    elif (dir0 == "v" and legalBrickSize(size=bricksDict[key]["size"], type="SLOPE_INVERTED") and bricksDict[key]["bot_exposed"]):
        typ = "SLOPE_INVERTED"
    else:
        typ = "BRICK"
    bricksDict[key]["type"] = typ


def setFlippedAndRotated(bricksDict, key, keysInBrick):
    norms = [bricksDict[k]["near_normal"] for k in keysInBrick if bricksDict[k]["near_normal"] is not None]

    dir1 = getMostCommonDir(1, 3, norms) if len(norms) != 0 else ""
    flip, rot = getFlipRot(dir1)

    # set flipped and rotated
    bricksDict[key]["flipped"] = flip
    bricksDict[key]["rotated"] = rot
