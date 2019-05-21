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
import time
import sys
import random
import json
import numpy as np

# Blender imports
import bpy
from mathutils import Vector, Matrix

# Addon imports
from .hashObject import hash_object
from ..lib.Brick import Bricks
from ..lib.bricksDict import *
from .common import *
from .wrappers import *
from .general import bounds
from ..lib.caches import bricker_mesh_cache
from .makeBricks_utils import *
from .mat_utils import *


@timed_call('Time Elapsed')
def makeBricks(source, parent, logo, logo_details, dimensions, bricksDict, action, cm=None, split=False, brickScale=None, customData=None, coll_name=None, clearExistingCollection=True, frameNum=None, cursorStatus=False, keys="ALL", printStatus=True, tempBrick=False, redraw=False):
    # set up variables
    scn, cm, n = getActiveContextInfo(cm=cm)

    # reset brickSizes/TypesUsed
    if keys == "ALL":
        cm.brickSizesUsed = ""
        cm.brickTypesUsed = ""
    # initialize cm.zStep
    cm.zStep = getZStep(cm)

    mergeVertical = (keys != "ALL" and "PLATES" in cm.brickType) or cm.brickType == "BRICKS AND PLATES"

    # get brick collection
    coll_name = coll_name or 'Bricker_%(n)s_bricks' % locals()
    bColl = bpy_collections().get(coll_name)
    # create new collection if no existing collection found
    if bColl is None:
        bColl = bpy_collections().new(coll_name)
    # else, replace existing collection
    elif clearExistingCollection:
        for obj0 in bColl.objects:
            bColl.objects.unlink(obj0)

    # get bricksDict keys in sorted order
    if keys == "ALL":
        keys = list(bricksDict.keys())
    if len(keys) == 0:
        return False, None
    # get dictionary of keys based on z value
    keysDict = getKeysDict(bricksDict, keys)
    denom = sum([len(keysDict[z0]) for z0 in keysDict.keys()])
    # store first key to active keys
    if cm.activeKey[0] == -1 and len(keys) > 0:
        loc = getDictLoc(bricksDict, keys[0])
        cm.activeKey = loc

    # initialize cmlist attributes (prevents 'update' function from running every time)
    cm_id = cm.id
    alignBricks = cm.alignBricks
    buildIsDirty = cm.buildIsDirty
    brickHeight = cm.brickHeight
    brickType = cm.brickType
    bricksAndPlates = brickType == "BRICKS AND PLATES"
    circleVerts = min(16, cm.circleVerts) if tempBrick else cm.circleVerts
    customObject1 = cm.customObject1
    customObject2 = cm.customObject2
    customObject3 = cm.customObject3
    matDirty = cm.materialIsDirty or cm.matrixIsDirty or cm.buildIsDirty
    customMat = cm.customMat
    exposedUndersideDetail = "FLAT" if tempBrick else cm.exposedUndersideDetail
    hiddenUndersideDetail = "FLAT" if tempBrick else cm.hiddenUndersideDetail
    instanceBricks = cm.instanceBricks
    lastSplitModel = cm.lastSplitModel
    legalBricksOnly = cm.legalBricksOnly
    logoType = "NONE" if tempBrick else cm.logoType
    logoScale = cm.logoScale
    logoInset = cm.logoInset
    logoResolution = cm.logoResolution
    logoDecimate = cm.logoDecimate
    loopCut = False if tempBrick else cm.loopCut
    maxWidth = cm.maxWidth
    maxDepth = cm.maxDepth
    mergeInternalsH = cm.mergeInternals in ["BOTH", "HORIZONTAL"]
    mergeInternalsV = cm.mergeInternals in ["BOTH", "VERTICAL"]
    mergeType = cm.mergeType
    mergeSeed = cm.mergeSeed
    materialType = cm.materialType
    offsetBrickLayers = cm.offsetBrickLayers
    randomMatSeed = cm.randomMatSeed
    randomRot = 0 if tempBrick else cm.randomRot
    randomLoc = 0 if tempBrick else cm.randomLoc
    studDetail = "ALL" if tempBrick else cm.studDetail
    zStep = cm.zStep
    # initialize random states
    randS1 = None if tempBrick else np.random.RandomState(cm.mergeSeed)  # for brickSize calc
    randS2 = None if tempBrick else np.random.RandomState(cm.mergeSeed+1)
    randS3 = None if tempBrick else np.random.RandomState(cm.mergeSeed+2)
    # initialize other variables
    brick_mats = getBrickMats(cm.materialType, cm.id)
    brickSizeStrings = {}
    mats = []
    allMeshes = bmesh.new()
    lowestZ = -1
    availableKeys = []
    bricksCreated = []
    maxBrickHeight = 1 if cm.zStep == 3 else max(legalBricks.keys())
    connectThresh = cm.connectThresh if mergableBrickType(brickType) and mergeType == "RANDOM" else 1
    # set up internal material for this object
    internalMat = None if len(source.data.materials) == 0 else cm.internalMat or bpy.data.materials.get("Bricker_%(n)s_internal" % locals()) or bpy.data.materials.new("Bricker_%(n)s_internal" % locals())
    if internalMat is not None and cm.materialType == "SOURCE" and cm.matShellDepth < cm.shellThickness:
        mats.append(internalMat)
    # set number of times to run through all keys
    numIters = 2 if brickType == "BRICKS AND PLATES" else 1
    i = 0
    # if merging unnecessary, simply update bricksDict values
    if not cm.customized and not (mergableBrickType(brickType, up=cm.zStep == 1) and (maxDepth != 1 or maxWidth != 1)):
        size = [1, 1, cm.zStep]
        if len(keys) > 0:
            updateBrickSizesAndTypesUsed(cm, listToStr(size), bricksDict[keys[0]]["type"])
        availableKeys = keys
        for key in keys:
            bricksDict[key]["parent"] = "self"
            bricksDict[key]["size"] = size.copy()
            setAllBrickExposures(bricksDict, zStep, key)
            setFlippedAndRotated(bricksDict, key, [key])
            if bricksDict[key]["type"] == "SLOPE" and brickType == "SLOPES":
                setBrickTypeForSlope(bricksDict, key, [key])
    else:
        # initialize progress bar around cursor
        old_percent = updateProgressBars(printStatus, cursorStatus, 0, -1, "Merging")
        # run merge operations (twice if flat brick type)
        for timeThrough in range(numIters):
            # iterate through z locations in bricksDict (bottom to top)
            for z in sorted(keysDict.keys()):
                # skip second and third rows on first time through
                if numIters == 2 and alignBricks:
                    # initialize lowestZ if not done already
                    if lowestZ == -0.1:
                        lowestZ = z
                    if skipThisRow(timeThrough, lowestZ, z, offsetBrickLayers):
                        continue
                # get availableKeys for attemptMerge
                availableKeysBase = []
                for ii in range(maxBrickHeight):
                    if ii + z in keysDict:
                        availableKeysBase += keysDict[z + ii]
                # get small duplicate of bricksDict for variations
                if connectThresh > 1:
                    bricksDictsBase = {}
                    for k4 in availableKeysBase:
                        bricksDictsBase[k4] = bricksDict[k4]
                    bricksDicts = [deepcopy(bricksDictsBase) for j in range(connectThresh)]
                    numAlignedEdges = [0 for idx in range(connectThresh)]
                else:
                    bricksDicts = [bricksDict]
                # calculate build variations for current z level
                for j in range(connectThresh):
                    availableKeys = availableKeysBase.copy()
                    numBricks = 0
                    if mergeType == "RANDOM":
                        random.seed(mergeSeed + i)
                        random.shuffle(keysDict[z])
                    # iterate through keys on current z level
                    for key in keysDict[z]:
                        i += 1 / connectThresh
                        brickD = bricksDicts[j][key]
                        # skip keys that are already drawn or have attempted merge
                        if brickD["attempted_merge"] or brickD["parent"] not in (None, "self"):
                            # remove ignored key if it exists in availableKeys (for attemptMerge)
                            remove_item(availableKeys, key)
                            continue

                        # initialize loc
                        loc = getDictLoc(bricksDict, key)

                        # merge current brick with available adjacent bricks
                        brickSize, keysInBrick = mergeWithAdjacentBricks(brickD, bricksDicts[j], key, loc, availableKeys, [1, 1, zStep], zStep, randS1, buildIsDirty, brickType, maxWidth, maxDepth, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, mergeVertical=mergeVertical)
                        brickD["size"] = brickSize
                        # iterate number aligned edges and bricks if generating multiple variations
                        if connectThresh > 1:
                            numAlignedEdges[j] += getNumAlignedEdges(bricksDict, brickSize, key, loc, bricksAndPlates)
                            numBricks += 1

                        # print status to terminal and cursor
                        cur_percent = (i / denom)
                        old_percent = updateProgressBars(printStatus, cursorStatus, cur_percent, old_percent, "Merging")

                        # remove keys in new brick from availableKeys (for attemptMerge)
                        for k in keysInBrick:
                            remove_item(availableKeys, k)

                    if connectThresh > 1:
                        # if no aligned edges / bricks found, skip to next z level
                        if numAlignedEdges[j] == 0:
                            i += (len(keysDict[z]) * connectThresh - 1) / connectThresh
                            break
                        # add double the number of bricks so connectivity threshold is weighted towards larger bricks
                        numAlignedEdges[j] += numBricks * 2

                # choose optimal variation from above for current z level
                if connectThresh > 1:
                    optimalTest = numAlignedEdges.index(min(numAlignedEdges))
                    for k3 in bricksDicts[optimalTest]:
                        bricksDict[k3] = bricksDicts[optimalTest][k3]

        # update cm.brickSizesUsed and cm.brickTypesUsed
        for key in keys:
            if bricksDict[key]["parent"] not in (None, "self"):
                continue
            brickSize = bricksDict[key]["size"]
            if brickSize is None:
                continue
            brickSizeStr = listToStr(sorted(brickSize[:2]) + [brickSize[2]])
            updateBrickSizesAndTypesUsed(cm, brickSizeStr, bricksDict[key]["type"])

        # end 'Merging' progress bar
        updateProgressBars(printStatus, cursorStatus, 1, 0, "Merging", end=True)

    # begin 'Building' progress bar
    old_percent = updateProgressBars(printStatus, cursorStatus, 0, -1, "Building")

    # draw merged bricks
    seedKeys = sorted(list(bricksDict.keys())) if materialType == "RANDOM" else None
    for z in sorted(keysDict.keys()):
        for k2 in keysDict[z]:
            if bricksDict[k2]["parent"] != "self" or not bricksDict[k2]["draw"]:
                continue
            loc = getDictLoc(bricksDict, k2)
            # create brick based on the current brick info
            drawBrick(cm_id, bricksDict, k2, loc, seedKeys, parent, dimensions, zStep, bricksDict[k2]["size"], brickType, split, lastSplitModel, customObject1, customObject2, customObject3, matDirty, customData, brickScale, bricksCreated, allMeshes, logo, logo_details, mats, brick_mats, internalMat, brickHeight, logoResolution, logoDecimate, loopCut, buildIsDirty, materialType, customMat, randomMatSeed, studDetail, exposedUndersideDetail, hiddenUndersideDetail, randomRot, randomLoc, logoType, logoScale, logoInset, circleVerts, instanceBricks, randS1, randS2, randS3)
            # print status to terminal and cursor
            old_percent = updateProgressBars(printStatus, cursorStatus, i/len(bricksDict.keys()), old_percent, "Building")

    # end progress bars
    updateProgressBars(printStatus, cursorStatus, 1, 0, "Building", end=True)

    # remove duplicate of original logo
    if logoType != "LEGO" and logo is not None:
        bpy.data.objects.remove(logo)

    # combine meshes, link to scene, and add relevant data to the new Blender MESH object
    if split:
        # iterate through keys
        old_percent = 0
        for i, key in enumerate(keys):
            if bricksDict[key]["parent"] != "self" or not bricksDict[key]["draw"]:
                continue
            # print status to terminal and cursor
            old_percent = updateProgressBars(printStatus, cursorStatus, i/len(bricksDict), old_percent, "Linking to Scene")
            # get brick
            name = bricksDict[key]["name"]
            brick = bpy.data.objects.get(name)
            # create vert group for bevel mod (assuming only logo verts are selected):
            vg = brick.vertex_groups.get("%(name)s_bvl" % locals())
            if vg:
                brick.vertex_groups.remove(vg)
            vg = brick.vertex_groups.new(name="%(name)s_bvl" % locals())
            vertList = [v.index for v in brick.data.vertices if not v.select]
            vg.add(vertList, 1, "ADD")
            # set up remaining brick info if brick object just created
            if clearExistingCollection or brick.name not in bColl.objects.keys():
                bColl.objects.link(brick)
            brick.parent = parent
            if not brick.isBrick:
                brick.isBrick = True
        # end progress bars
        updateProgressBars(printStatus, cursorStatus, 1, 0, "Linking to Scene", end=True)
    else:
        name = 'Bricker_%(n)s_bricks' % locals()
        if frameNum is not None:
            name = "%(name)s_f_%(frameNum)s" % locals()
        m = bpy.data.meshes.new(name)
        allMeshes.to_mesh(m)
        allBricksObj = bpy.data.objects.get(name)
        if allBricksObj:
            allBricksObj.data = m
        else:
            allBricksObj = bpy.data.objects.new(name, m)
            allBricksObj.cmlist_id = cm_id
            # add edge split modifier
            if brickType != "CUSTOM":
                addEdgeSplitMod(allBricksObj)
        if brickType != "CUSTOM":
            # create vert group for bevel mod (assuming only logo verts are selected):
            vg = allBricksObj.vertex_groups.get("%(name)s_bvl" % locals())
            if vg:
                allBricksObj.vertex_groups.remove(vg)
            vg = allBricksObj.vertex_groups.new(name="%(name)s_bvl" % locals())
            vertList = [v.index for v in allBricksObj.data.vertices if not v.select]
            vg.add(vertList, 1, "ADD")
        if materialType in ("CUSTOM", "NONE"):
            setMaterial(allBricksObj, customMat)
        elif materialType == "SOURCE" or (materialType == "RANDOM" and len(brick_mats) > 0):
            for mat in mats:
                setMaterial(allBricksObj, mat, overwrite=False)
        # set parent
        allBricksObj.parent = parent
        # add bricks obj to scene and bricksCreated
        if allBricksObj.name not in bColl.objects.keys():
            bColl.objects.link(allBricksObj)
        bricksCreated.append(allBricksObj)
        # protect allBricksObj from being deleted
        allBricksObj.isBrickifiedObject = True

    # reset 'attempted_merge' for all items in bricksDict
    for key0 in bricksDict:
        bricksDict[key0]["attempted_merge"] = False

    return bricksCreated, bricksDict
