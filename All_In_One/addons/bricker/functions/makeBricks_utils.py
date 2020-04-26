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
import copy
import numpy as np

# Blender imports
import bpy
from mathutils import Vector, Matrix

# Addon imports
from .hashObject import hash_object
from ..lib.Brick import Bricks
from ..lib.bricksDict import *
from .common import *
from .mat_utils import *
from .wrappers import *
from .general import *
from ..lib.caches import bricker_mesh_cache


def drawBrick(cm_id, bricksDict, key, loc, seedKeys, parent, dimensions, zStep, brickSize, brickType, split, lastSplitModel, customObject1, customObject2, customObject3, matDirty, customData, brickScale, bricksCreated, allMeshes, logo, logo_details, mats, brick_mats, internalMat, brickHeight, logoResolution, logoDecimate, loopCut, buildIsDirty, materialType, customMat, randomMatSeed, studDetail, exposedUndersideDetail, hiddenUndersideDetail, randomRot, randomLoc, logoType, logoScale, logoInset, circleVerts, instanceBricks, randS1, randS2, randS3):
    brickD = bricksDict[key]
    # check exposure of current [merged] brick
    if brickD["top_exposed"] is None or brickD["bot_exposed"] is None or buildIsDirty:
        topExposed, botExposed = setAllBrickExposures(bricksDict, zStep, key)
    else:
        topExposed, botExposed = isBrickExposed(bricksDict, zStep, key)

    # get brick material
    mat = getMaterial(bricksDict, key, brickSize, zStep, materialType, customMat, randomMatSeed, matDirty, seedKeys, brick_mats=brick_mats)

    # set up arguments for brick mesh
    useStud = (topExposed and studDetail != "NONE") or studDetail == "ALL"
    logoToUse = logo if useStud else None
    undersideDetail = exposedUndersideDetail if botExposed else hiddenUndersideDetail

    ### CREATE BRICK ###

    # add brick with new mesh data at original location
    if brickD["type"].startswith("CUSTOM"):
        m = customData[int(brickD["type"][-1]) - 1]
    else:
        # get brick mesh
        m = getBrickData(brickD, randS3, dimensions, brickSize, brickType, brickHeight, logoResolution, logoDecimate, circleVerts, loopCut, undersideDetail, logoToUse, logoType, logo_details, logoScale, logoInset, useStud)
    # duplicate data if cm.instanceBricks is disabled
    m = m if instanceBricks else m.copy()
    # apply random rotation to edit mesh according to parameters
    randomRotMatrix = getRandomRotMatrix(randomRot, randS2, brickSize) if randomRot > 0 else None
    # get brick location
    locOffset = getRandomLoc(randomLoc, randS2, dimensions["width"], dimensions["height"]) if randomLoc > 0 else Vector((0, 0, 0))
    brickLoc = getBrickCenter(bricksDict, key, zStep, loc) + locOffset

    if split:
        brick = bpy.data.objects.get(brickD["name"])
        edgeSplit = useEdgeSplitMod(brickD, customObject1, customObject2, customObject3)
        if brick:
            # NOTE: last brick object is left in memory (faster)
            # set brick.data to new mesh (resets materials)
            brick.data = m
            # add/remove edge split modifier if necessary
            eMod = brick.modifiers.get('Edge Split')
            if not eMod and edgeSplit:
                addEdgeSplitMod(brick)
            elif eMod and not edgeSplit:
                brick.modifiers.remove(eMod)
        else:
            # create new object with mesh data
            brick = bpy.data.objects.new(brickD["name"], m)
            brick.cmlist_id = cm_id
            # add edge split modifier
            if edgeSplit:
                addEdgeSplitMod(brick)
        # rotate brick by random rotation
        if randomRotMatrix is not None:
            # resets rotation_euler in case object is reused
            brick.rotation_euler = Euler((0, 0, 0), "XYZ")
            brick.rotation_euler.rotate(randomRotMatrix)
        # set brick location
        brick.location = brickLoc
        # set brick material
        setMaterial(brick, mat or internalMat)
        if mat or internalMat:
            keysInBrick = getKeysInBrick(bricksDict, brickSize, zStep, loc)
            for k in keysInBrick:
                bricksDict[k]["mat_name"] = (mat or internalMat).name
        # append to bricksCreated
        bricksCreated.append(brick)
    else:
        # duplicates mesh – prevents crashes (TODO: test without this line in 2.8)
        m = m.copy()
        # apply rotation matrices to edit mesh
        if randomRotMatrix is not None:
            m.transform(randomRotMatrix)
        # transform brick mesh to coordinate on matrix
        m.transform(Matrix.Translation(brickLoc))

        # set to internal mat if material not set
        internal = False
        if mat is None:
            mat = internalMat
            internal = True

        # keep track of mats already used
        if mat in mats:
            matIdx = mats.index(mat)
        elif mat is not None:
            mats.append(mat)
            matIdx = len(mats) - 1

        # set material
        if mat is not None:
            # set material name in dictionary
            if not internal:
                brickD["mat_name"] = mat.name
            # point all polygons to target material (index will correspond in allMeshes object)
            for p in m.polygons:
                p.material_index = matIdx

        # append mesh to allMeshes bmesh object
        allMeshes.from_mesh(m)

        # remove duplicated mesh (TODO: test without this line in 2.8)
        bpy.data.meshes.remove(m)
        # NOTE: The following lines clean up the mesh if not duplicated
        # # reset polygon material mapping
        # if mat is not None:
        #     for p in m.polygons:
        #         p.material_index = 0
        #
        # # reset transformations for reference mesh
        # m.transform(Matrix.Translation(-brickLoc))
        # if randomRotMatrix is not None:
        #     randomRotMatrix.invert()
        #     m.transform(randomRotMatrix)

    return bricksDict


def useEdgeSplitMod(brickD, customObject1, customObject2, customObject3):
    typ = brickD["type"]
    if ("CUSTOM" not in brickD["type"] or
        (typ == "CUSTOM 1" and customObject1 and customObject1.name.startswith("Bricker_")) or
        (typ == "CUSTOM 2" and customObject2 and customObject2.name.startswith("Bricker_")) or
        (typ == "CUSTOM 3" and customObject3 and customObject3.name.startswith("Bricker_"))):
        return True
    else:
        return False


def addEdgeSplitMod(obj):
    """ Add edge split modifier """
    eMod = obj.modifiers.new('Edge Split', 'EDGE_SPLIT')
    eMod.split_angle = math.radians(44)


def mergeWithAdjacentBricks(brickD, bricksDict, key, loc, keysNotChecked, defaultSize, zStep, randS1, buildIsDirty, brickType, maxWidth, maxDepth, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, mergeVertical=True):
    if brickD["size"] is None or buildIsDirty:
        preferLargest = brickD["val"] > 0 and brickD["val"] < 1
        brickSize, keysInBrick = attemptMerge(bricksDict, key, keysNotChecked, defaultSize, zStep, randS1, brickType, maxWidth, maxDepth, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, loc=loc, preferLargest=preferLargest, mergeVertical=mergeVertical, height3Only=brickD["type"] in getBrickTypes(height=3))
    else:
        brickSize = brickD["size"]
        keysInBrick = getKeysInBrick(bricksDict, brickSize, zStep, loc=loc)
    return brickSize, keysInBrick


def skipThisRow(timeThrough, lowestZ, z, offsetBrickLayers):
    if timeThrough == 0:  # first time
        if (z - offsetBrickLayers - lowestZ) % 3 in (1, 2):
            return True
    else:  # second time
        if (z - offsetBrickLayers - lowestZ) % 3 == 0:
            return True
    return False


def getRandomLoc(randomLoc, rand, width, height):
    """ get random location between (0,0,0) and (width/2, width/2, height/2) """
    loc = Vector((0,0,0))
    loc.xy = [rand.uniform(-(width/2) * randomLoc, (width/2) * randomLoc)]*2
    loc.z = rand.uniform(-(height/2) * randomLoc, (height/2) * randomLoc)
    return loc


def getRandomRotMatrix(randomRot, rand, brickSize):
    """ get rotation matrix randomized by randomRot """
    denom = 0.75 if max(brickSize) == 0 else brickSize[0] * brickSize[1]
    mult = randomRot / denom
    # calculate rotation angles in radians
    x = rand.uniform(-math.radians(11.25) * mult, math.radians(11.25) * mult)
    y = rand.uniform(-math.radians(11.25) * mult, math.radians(11.25) * mult)
    z = rand.uniform(-math.radians(45)    * mult, math.radians(45)    * mult)
    # get rotation matrix
    x_mat = Matrix.Rotation(x, 4, 'X')
    y_mat = Matrix.Rotation(y, 4, 'Y')
    z_mat = Matrix.Rotation(z, 4, 'Z')
    combined_mat = mathutils_mult(x_mat, y_mat, z_mat)
    return combined_mat


def prepareLogoAndGetDetails(scn, logo, detail, scale, dimensions):
    """ duplicate and normalize custom logo object; return logo and bounds(logo) """
    if logo is None:
        return None, logo
    # duplicate logo object
    logo = duplicate(logo, link_to_scene=True)
    if detail != "LEGO":
        # disable modifiers for logo object
        for mod in logo.modifiers:
            mod.show_viewport = False
        # apply logo object transformation
        logo.parent = None
        apply_transform(logo)
    safeUnlink(logo)
    # get logo details
    logo_details = bounds(logo)
    m = logo.data
    # select all verts in logo
    for v in m.vertices:
        v.select = True
    # create transform and scale matrices
    t_mat = Matrix.Translation(-logo_details.mid)
    distMax = max(logo_details.dist.xy)
    lw = dimensions["logo_width"] * (0.78 if detail == "LEGO" else scale)
    s_mat = Matrix.Scale(lw / distMax, 4)
    # run transformations on logo mesh
    m.transform(t_mat)
    m.transform(s_mat)
    return logo_details, logo


def getBrickData(brickD, rand, dimensions, brickSize, brickType, brickHeight, logoResolution, logoDecimate, circleVerts, loopCut, undersideDetail, logoToUse, logoType, logo_details, logoScale, logoInset, useStud):
    # get bm_cache_string
    bm_cache_string = ""
    if "CUSTOM" not in brickType:
        custom_logo_used = logoToUse is not None and logoType == "CUSTOM"
        bm_cache_string = json.dumps((brickHeight, brickSize, undersideDetail,
                                      logoResolution if logoToUse is not None else None,
                                      logoDecimate if logoToUse is not None else None,
                                      logoInset if logoToUse is not None else None,
                                      hash_object(logoToUse) if custom_logo_used else None,
                                      logoScale if custom_logo_used else None,
                                      logoType, useStud, circleVerts,
                                      brickD["type"], loopCut, dimensions["gap"],
                                      brickD["flipped"] if brickD["type"] in ("SLOPE", "SLOPE_INVERTED") else None,
                                      brickD["rotated"] if brickD["type"] in ("SLOPE", "SLOPE_INVERTED") else None))

    # NOTE: Stable implementation for Blender 2.79
    # check for bmesh in cache
    bms = bricker_mesh_cache.get(bm_cache_string)
    # if not found create new brick mesh(es) and store to cache
    if bms is None:
        # create new brick bmeshes
        bms = Bricks.new_mesh(dimensions, brickType, size=brickSize, type=brickD["type"], flip=brickD["flipped"], rotate90=brickD["rotated"], loopCut=loopCut, logo=logoToUse, logoType=logoType, logoScale=logoScale, logoInset=logoInset, all_vars=logoToUse is not None, logo_details=logo_details, undersideDetail=undersideDetail, stud=useStud, circleVerts=circleVerts)
        # store newly created meshes to cache
        if brickType != "CUSTOM":
            bricker_mesh_cache[bm_cache_string] = bms
    # create edit mesh for each bmesh
    meshes = []
    for i,bm in enumerate(bms):
        # check for existing edit mesh in blendfile data
        bmcs_hash = hash_str(bm_cache_string)
        meshName = "%(bmcs_hash)s_%(i)s" % locals()
        m = bpy.data.meshes.get(meshName)
        # create new edit mesh and send bmesh data to it
        if m is None:
            m = bpy.data.meshes.new(meshName)
            bm.to_mesh(m)
            # center mesh origin
            centerMeshOrigin(m, dimensions, brickSize)
        meshes.append(m)
    # # TODO: Try the following code instead in Blender 2.8 – see if it crashes with the following steps:
    # #     Open new file
    # #     Create new bricker model and Brickify with default settings
    # #     Delete the brickified model with the 'x > OK?' shortcut
    # #     Undo with 'ctrl + z'
    # #     Enable 'Update Model' button by clicking on and off of 'Gap Between Bricks'
    # #     Press 'Update Model'
    # # check for bmesh in cache
    # meshes = bricker_mesh_cache.get(bm_cache_string)
    # # if not found create new brick mesh(es) and store to cache
    # if meshes is None:
    #     # create new brick bmeshes
    #     bms = Bricks.new_mesh(dimensions, brickType, size=brickSize, type=brickD["type"], flip=brickD["flipped"], rotate90=brickD["rotated"], loopCut=loopCut, logo=logoToUse, logoType=logoType, logoScale=logoScale, logoInset=logoInset, all_vars=logoToUse is not None, logo_details=logo_details, undersideDetail=undersideDetail, stud=useStud, circleVerts=circleVerts)
    #     # create edit mesh for each bmesh
    #     meshes = []
    #     for i,bm in enumerate(bms):
    #         # check for existing edit mesh in blendfile data
    #         bmcs_hash = hash_str(bm_cache_string)
    #         meshName = "%(bmcs_hash)s_%(i)s" % locals()
    #         m = bpy.data.meshes.get(meshName)
    #         # create new edit mesh and send bmesh data to it
    #         if m is None:
    #             m = bpy.data.meshes.new(meshName)
    #             bm.to_mesh(m)
    #             # center mesh origin
    #             centerMeshOrigin(m, dimensions, brickSize)
    #         meshes.append(m)
    #     # store newly created meshes to cache
    #     if brickType != "CUSTOM":
    #         bricker_mesh_cache[bm_cache_string] = meshes

    # pick edit mesh randomly from options
    m0 = meshes[rand.randint(0, len(meshes))] if len(meshes) > 1 else meshes[0]

    return m0


def getMaterial(bricksDict, key, size, zStep, materialType, customMat, randomMatSeed, matDirty, seedKeys, brick_mats=None):
    mat = None
    highestVal = 0
    matsL = []
    if bricksDict[key]["custom_mat_name"] and not matDirty:
        mat = bpy.data.materials.get(bricksDict[key]["mat_name"])
    elif materialType == "CUSTOM":
        mat = customMat
    elif materialType == "SOURCE":
        # get most frequent material in brick size
        matName = ""
        keysInBrick = getKeysInBrick(bricksDict, size, zStep, key=key)
        for key0 in keysInBrick:
            curBrickD = bricksDict[key0]
            if curBrickD["val"] >= highestVal:
                highestVal = curBrickD["val"]
                matName = curBrickD["mat_name"]
                if curBrickD["val"] == 1:
                    matsL.append(matName)
        # if multiple shell materials, use the most frequent one
        if len(matsL) > 1:
            matName = most_common(matsL)
        mat = bpy.data.materials.get(matName)
    elif materialType == "RANDOM" and brick_mats is not None and len(brick_mats) > 0:
        if len(brick_mats) > 1:
            randState = np.random.RandomState(0)
            seedInc = seedKeys.index(key)  # keeps materials consistent accross all calculations regardless of where material is set
            randState.seed(randomMatSeed + seedInc)
            randIdx = randState.randint(0, len(brick_mats))
        else:
            randIdx = 0
        matName = brick_mats[randIdx]
        mat = bpy.data.materials.get(matName)
    return mat

def updateBrickSizesAndTypesUsed(cm, sz, typ):
    bsu = cm.brickSizesUsed
    btu = cm.brickTypesUsed
    cm.brickSizesUsed += sz if bsu == "" else ("|%(sz)s" % locals() if sz not in bsu else "")
    cm.brickTypesUsed += typ if btu == "" else ("|%(typ)s" % locals() if typ not in btu else "")
