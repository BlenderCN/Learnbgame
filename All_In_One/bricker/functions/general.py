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
import collections
import json
import math
import numpy as np
import bmesh

# Blender imports
import bpy
from mathutils import Vector, Euler, Matrix
from bpy.types import Object

# Addon imports
from .common import *


def getActiveContextInfo(cm=None, cm_id=None):
    scn = bpy.context.scene
    cm = cm or scn.cmlist[scn.cmlist_index]
    return scn, cm, getSourceName(cm)


def getSourceName(cm):
    return cm.source_obj.name if cm.source_obj is not None else ""


def centerMeshOrigin(m, dimensions, size):
    # get half width
    d0 = Vector((dimensions["width"] / 2, dimensions["width"] / 2, 0))
    # get scalar for d0 in positive xy directions
    scalar = Vector((size[0] * 2 - 1,
                     size[1] * 2 - 1,
                     0))
    # calculate center
    center = (vec_mult(d0, scalar) - d0) / 2
    # apply translation matrix to center mesh
    m.transform(Matrix.Translation(-Vector(center)))


def getAnimAdjustedFrame(frame, startFrame, stopFrame):
    if frame < startFrame:
        curFrame = startFrame
    elif frame > stopFrame:
        curFrame = stopFrame
    else:
        curFrame = frame
    return curFrame


def getBricks(cm=None, typ=None):
    """ get bricks in 'cm' model """
    scn, cm, n = getActiveContextInfo(cm=cm)
    typ = typ or ("MODEL" if cm.modelCreated else "ANIM")
    bricks = list()
    if typ == "MODEL":
        bColl = bpy_collections().get("Bricker_%(n)s_bricks" % locals())
        if bColl:
            bricks = list(bColl.objects)
    elif typ == "ANIM":
        for cf in range(cm.lastStartFrame, cm.lastStopFrame+1):
            bColl = bpy_collections().get("Bricker_%(n)s_bricks_f_%(cf)s" % locals())
            if bColl:
                bricks += list(bColl.objects)
    return bricks


def getCollections(cm=None, typ=None):
    """ get bricks collections in 'cm' model """
    scn, cm, n = getActiveContextInfo(cm=cm)
    typ = typ or ("MODEL" if cm.modelCreated else "ANIM")
    if typ == "MODEL":
        cn = "Bricker_%(n)s_bricks" % locals()
        bColls = [bpy_collections()[cn]]
    if typ == "ANIM":
        bColls = list()
        for cf in range(cm.lastStartFrame, cm.lastStopFrame+1):
            cn = "Bricker_%(n)s_bricks_f_%(cf)s" % locals()
            bColl = bpy_collections().get(cn)
            if bColl:
                bColls.append(bColl)
    return bColls


def getMatObject(cm_id, typ="RANDOM"):
    mat_n = cm_id
    Bricker_mat_on = "Bricker_%(mat_n)s_%(typ)s_mats" % locals()
    matObj = bpy.data.objects.get(Bricker_mat_on)
    return matObj


def getBrickTypes(height):
    return bpy.props.Bricker_legal_brick_sizes[height].keys()


def flatBrickType(typ):
    return type(typ) == str and ("PLATE" in typ or "STUD" in typ)


def mergableBrickType(typ, up=False):
    return type(typ) == str and ("PLATE" in typ or "BRICK" in typ or "SLOPE" in typ or (up and typ == "CYLINDER"))


def getTallType(brickD, targetType=None):
    tallTypes = getBrickTypes(height=3)
    return targetType if targetType in tallTypes else (brickD["type"] if brickD["type"] in tallTypes else "BRICK")


def getShortType(brickD, targetType=None):
    shortTypes = getBrickTypes(height=1)
    return targetType if targetType in shortTypes else (brickD["type"] if brickD["type"] in shortTypes else "PLATE")


def brick_materials_installed():
    return hasattr(bpy.ops, "abs") and hasattr(bpy.ops.abs, "append_materials")


def getABSMatNames(all:bool=True):
    """ returns list of ABS Plastic Material names """
    if not brick_materials_installed():
        return []
    scn = bpy.context.scene
    materials = list()
    # get common names (different properties for different versions)
    materials += bpy.props.abs_mats_common if hasattr(bpy.props, "abs_mats_common") else bpy.props.abs_plastic_materials
    # get transparent/uncommon names
    if all or scn.include_transparent:
        materials += bpy.props.abs_mats_transparent
    if all or scn.include_uncommon:
        materials += bpy.props.abs_mats_uncommon
    return materials


def brick_materials_loaded():
    scn = bpy.context.scene
    # make sure abs_plastic_materials addon is installed
    if not brick_materials_installed():
        return False
    # check if any of the colors haven't been loaded
    mats = bpy.data.materials.keys()
    for mat_name in getABSMatNames():
        if mat_name not in mats:
            return False
    return True


def getMatrixSettings(cm=None):
    cm = cm or getActiveContextInfo()[1]
    # TODO: Maybe remove custom objects from this?
    regularSettings = [round(cm.brickHeight, 6),
                       round(cm.gap, 6),
                       cm.brickType,
                       cm.distOffset[0],
                       cm.distOffset[1],
                       cm.distOffset[2],
                       cm.includeTransparency,
                       cm.customObject1.name if cm.customObject1 is not None else "",
                       cm.customObject2.name if cm.customObject2 is not None else "",
                       cm.customObject3.name if cm.customObject3 is not None else "",
                       cm.useNormals,
                       cm.verifyExposure,
                       cm.insidenessRayCastDir,
                       cm.castDoubleCheckRays,
                       cm.brickShell,
                       cm.calculationAxes]
    smokeSettings = [round(cm.smokeDensity, 6),
                     round(cm.smokeQuality, 6),
                     round(cm.smokeBrightness, 6),
                     round(cm.smokeSaturation, 6),
                     round(cm.flameColor[0], 6),
                     round(cm.flameColor[1], 6),
                     round(cm.flameColor[2], 6),
                     round(cm.flameIntensity, 6)] if cm.lastIsSmoke else []
    return listToStr(regularSettings + smokeSettings)


def matrixReallyIsDirty(cm, include_lost_matrix=True):
    return (cm.matrixIsDirty and cm.lastMatrixSettings != getMatrixSettings()) or (cm.matrixLost and include_lost_matrix)


def vecToStr(vec, separate_by=","):
    return listToStr(list(vec), separate_by=separate_by)


def listToStr(lst, separate_by=","):
    assert type(lst) in (list, tuple)
    return separate_by.join(map(str, lst))



def strToList(string, item_type=int, split_on=","):
    lst = string.split(split_on)
    assert type(string) is str and type(split_on) is str
    lst = list(map(item_type, lst))
    return lst


def strToTuple(string, item_type=int, split_on=","):
    return tuple(strToList(string, item_type, split_on))


def getZStep(cm):
    return 1 if flatBrickType(cm.brickType) else 3


def getKeysDict(bricksDict, keys=None):
    """ get dictionary of bricksDict keys based on z value """
    keys = keys or list(bricksDict.keys())
    keys.sort(key=lambda x: (getDictLoc(bricksDict, x)[0], getDictLoc(bricksDict, x)[1]))
    keysDict = {}
    for k0 in keys:
        z = getDictLoc(bricksDict, k0)[2]
        if bricksDict[k0]["draw"]:
            try:
                keysDict[z].append(k0)
            except KeyError:
                keysDict[z] = [k0]
    return keysDict


def getParentKey(bricksDict, key):
    if key not in bricksDict:
        return None
    parent_key = key if bricksDict[key]["parent"] in ("self", None) else bricksDict[key]["parent"]
    return parent_key


def createdWithUnsupportedVersion(cm):
    return cm.version[:3] != bpy.props.bricker_version[:3]


def createdWithNewerVersion(cm):
    modelVersion = cm.version.split(".")
    brickerVersion = bpy.props.bricker_version.split(".")
    return (int(modelVersion[0]) > int(brickerVersion[0])) or (int(modelVersion[0]) == int(brickerVersion[0]) and int(modelVersion[1]) > int(brickerVersion[1]))


# loc is more efficient than key, but one or the other must be passed
def getLocsInBrick(bricksDict, size, zStep, loc:list=None, key:str=None):
    x0, y0, z0 = loc or getDictLoc(bricksDict, key)
    return [[x0 + x, y0 + y, z0 + z] for z in range(0, size[2], zStep) for y in range(size[1]) for x in range(size[0])]


# loc is more efficient than key, but one or the other must be passed
def getKeysInBrick(bricksDict, size, zStep:int, loc:list=None, key:str=None):
    x0, y0, z0 = loc or getDictLoc(bricksDict, key)
    return [listToStr((x0 + x, y0 + y, z0 + z)) for z in range(0, size[2], zStep) for y in range(size[1]) for x in range(size[0])]


def isOnShell(bricksDict, key, loc=None, zStep=None, shellDepth=1):
    """ check if any locations in brick are on the shell """
    size = bricksDict[key]["size"]
    loc = loc or getDictLoc(bricksDict, key)
    brickKeys = getKeysInBrick(bricksDict, size, zStep, loc=loc)
    for k in brickKeys:
        if bricksDict[k]["val"] >= 1 - (shellDepth - 1) / 100:
            return True
    return False


def getDictKey(name):
    """ get dict key details of obj """
    dictKey = name.split("__")[-1]
    return dictKey

def getDictLoc(bricksDict, key):
    try:
        loc = bricksDict[key]["loc"]
    except KeyError:
        loc = strToList(key)
    return loc


def getBrickCenter(bricksDict, key, zStep, loc=None):
    loc = loc or getDictLoc(bricksDict, key)
    brickKeys = getKeysInBrick(bricksDict, bricksDict[key]["size"], zStep, loc=loc)
    coords = [bricksDict[k0]["co"] for k0 in brickKeys]
    coord_ave = Vector((mean([co[0] for co in coords]), mean([co[1] for co in coords]), mean([co[2] for co in coords])))
    return coord_ave


def getNearbyLocFromVector(locDiff, curLoc, dimensions, zStep, width_divisor=2.05, height_divisor=2.05):
    d = Vector((dimensions["width"] / width_divisor, dimensions["width"] / width_divisor, dimensions["height"] / height_divisor))
    nextLoc = Vector(curLoc)
    if locDiff.z > d.z - dimensions["stud_height"]:
        nextLoc.z += math.ceil((locDiff.z - d.z) / (d.z * 2))
    elif locDiff.z < -d.z:
        nextLoc.z -= 1
    if locDiff.x > d.x:
        nextLoc.x += math.ceil((locDiff.x - d.x) / (d.x * 2))
    elif locDiff.x < -d.x:
        nextLoc.x += math.floor((locDiff.x + d.x) / (d.x * 2))
    if locDiff.y > d.y:
        nextLoc.y += math.ceil((locDiff.y - d.y) / (d.y * 2))
    elif locDiff.y < -d.y:
        nextLoc.y += math.floor((locDiff.y + d.y) / (d.y * 2))
    return [int(nextLoc.x), int(nextLoc.y), int(nextLoc.z)]


def getNormalDirection(normal, maxDist=0.77, slopes=False):
    # initialize vars
    minDist = maxDist
    minDir = None
    # skip normals that aren't within 0.3 of the z values
    if normal is None or ((normal.z > -0.2 and normal.z < 0.2) or normal.z > 0.8 or normal.z < -0.8):
        return minDir
    # set Vectors for perfect normal directions
    if slopes:
        normDirs = {"^X+":Vector((1, 0, 0.5)),
                    "^Y+":Vector((0, 1, 0.5)),
                    "^X-":Vector((-1, 0, 0.5)),
                    "^Y-":Vector((0, -1, 0.5)),
                    "vX+":Vector((1, 0, -0.5)),
                    "vY+":Vector((0, 1, -0.5)),
                    "vX-":Vector((-1, 0, -0.5)),
                    "vY-":Vector((0, -1, -0.5))}
    else:
        normDirs = {"X+":Vector((1, 0, 0)),
                    "Y+":Vector((0, 1, 0)),
                    "Z+":Vector((0, 0, 1)),
                    "X-":Vector((-1, 0, 0)),
                    "Y-":Vector((0, -1, 0)),
                    "Z-":Vector((0, 0, -1))}
    # calculate nearest
    for dir,v in normDirs.items():
        dist = (v - normal).length
        if dist < minDist:
            minDist = dist
            minDir = dir
    return minDir


def getFlipRot(dir):
    flip = dir in ("X-", "Y-")
    rot = dir in ("Y+", "Y-")
    return flip, rot


def legalBrickSize(size, type):
     return size[:2] in bpy.props.Bricker_legal_brick_sizes[size[2]][type]


def getExportPath(fn, ext, basePath, frame=-1, subfolder=False):
    # TODO: support PC with os.path.join instead of strings and support backslashes
    path = os.path.dirname(basePath)
    blendPath = bpy.path.abspath("//")[:-1] or os.path.join(root_path(), "tmp")
    blendPathSplit = splitpath(blendPath)
    # if relative path, construct path from user input
    if path.startswith("//"):
        splitPath = splitpath(path[2:])
        while len(splitPath) > 0 and splitPath[0] == "..":
            splitPath.pop(0)
            blendPathSplit.pop()
        newPath = os.path.join(*splitPath) if len(splitPath) > 0 else ""
        fullBlendPath = os.path.join(*blendPathSplit) if len(blendPathSplit) > 1 else root_path()
        path = os.path.join(fullBlendPath, newPath)
    # if path is blank at this point, use default render location
    if path == "":
        path = blendPath
    # check to make sure path exists on local machine
    if not os.path.exists(path):
        return path, "Blender could not find the following path: '%(path)s'" % locals()
    # get full filename
    fn0 = os.path.split(basePath)[1] or fn
    frame_num = "_%(frame)s" % locals() if frame >= 0 else ""
    full_fn = fn0 + frame_num + ext
    # create subfolder
    if subfolder:
        path = os.path.join(path, fn0)
        if not os.path.exists(path):
            os.makedirs(path)
    # create full export path
    fullPath = os.path.join(path, full_fn)
    # ensure target folder has write permissions
    try:
        f = open(fullPath, "w")
        f.close()
    except PermissionError:
        return path, "Blender does not have write permissions for the following path: '%(path)s'" % locals()
    return fullPath, None


def shortenName(string:str, max_len:int=30):
    """shortens string while maintaining uniqueness"""
    if len(string) <= max_len:
        return string
    else:
        return string[:math.ceil(max_len * 0.65)] + str(hash_str(string))[:math.floor(max_len * 0.35)]


def customValidObject(cm, targetType="Custom 0", idx=None):
    for i, customInfo in enumerate([[cm.hasCustomObj1, cm.customObject1], [cm.hasCustomObj2, cm.customObject2], [cm.hasCustomObj3, cm.customObject3]]):
        hasCustomObj, customObj = customInfo
        if idx is not None and idx != i:
            continue
        elif not hasCustomObj and not (i == 0 and cm.brickType == "CUSTOM") and int(targetType.split(" ")[-1]) != i + 1:
            continue
        if customObj is None:
            warningMsg = "Custom brick type object {} could not be found".format(i + 1)
            return warningMsg
        elif customObj.name == getSourceName(cm) and (not (cm.animated or cm.modelCreated) or customObj.protected):
            warningMsg = "Source object cannot be its own custom brick."
            return warningMsg
        elif customObj.type != "MESH":
            warningMsg = "Custom object {} is not of type 'MESH'. Please select another object (or press 'ALT-C to convert object to mesh).".format(i + 1)
            return warningMsg
        custom_details = bounds(customObj)
        zeroDistAxes = ""
        if custom_details.dist.x < 0.00001:
            zeroDistAxes += "X"
        if custom_details.dist.y < 0.00001:
            zeroDistAxes += "Y"
        if custom_details.dist.z < 0.00001:
            zeroDistAxes += "Z"
        if zeroDistAxes != "":
            axisStr = "axis" if len(zeroDistAxes) == 1 else "axes"
            warningMsg = "Custom brick type object is to small along the '%(zeroDistAxes)s' %(axisStr)s (<0.00001). Please select another object or extrude it along the '%(zeroDistAxes)s' %(axisStr)s." % locals()
            return warningMsg
    return None


def updateHasCustomObjs(cm, typ):
    # update hasCustomObj
    if typ == "CUSTOM 1":
        cm.hasCustomObj1 = True
    if typ == "CUSTOM 2":
        cm.hasCustomObj2 = True
    if typ == "CUSTOM 3":
        cm.hasCustomObj3 = True


def getBrickMats(materialType, cm_id):
    brick_mats = []
    if materialType == "RANDOM":
        matObj = getMatObject(cm_id, typ="RANDOM")
        brick_mats = list(matObj.data.materials.keys())
    return brick_mats


def bricker_handle_exception():
    handle_exception(log_name="Bricker log", report_button_loc="Bricker > Brick Models > Report Error")


def createMatObjs(idx):
    """ create new matObjs for current cmlist id """
    matObjNames = ["Bricker_{}_RANDOM_mats".format(idx), "Bricker_{}_ABS_mats".format(idx)]
    for obj_n in matObjNames:
        matObj = bpy.data.objects.get(obj_n)
        if matObj is None:
            matObj = bpy.data.objects.new(obj_n, bpy.data.meshes.new(obj_n + "_mesh"))
            matObj.use_fake_user = True


def removeMatObjs(idx):
    """ remove matObjs for current cmlist id """
    matObjNames = ["Bricker_{}_RANDOM_mats".format(idx), "Bricker_{}_ABS_mats".format(idx)]
    for obj_n in matObjNames:
        matObj = bpy.data.objects.get(obj_n)
        if matObj is not None:
            bpy.data.objects.remove(matObj, do_unlink=True)


def getBrickType(modelBrickType):
    return "PLATE" if modelBrickType == "BRICKS AND PLATES" else (modelBrickType[:-1] if modelBrickType.endswith("S") else ("CUSTOM 1" if modelBrickType == "CUSTOM" else modelBrickType))


def getRoundBrickTypes():
    return ("CYLINDER", "CONE", "STUD", "STUD_HOLLOW")


def brickifyShouldRun(cm):
    if ((cm.animated and (not updateCanRun("ANIMATION") and not cm.animIsDirty))
       or (cm.modelCreated and not updateCanRun("MODEL"))):
        return False
    return True


def updateCanRun(type):
    scn, cm, n = getActiveContextInfo()
    if createdWithUnsupportedVersion(cm):
        return True
    elif scn.cmlist_index == -1:
        return False
    else:
        commonNeedsUpdate = (cm.logoType != "NONE" and cm.logoType != "LEGO") or cm.brickType == "CUSTOM" or cm.modelIsDirty or cm.matrixIsDirty or cm.internalIsDirty or cm.buildIsDirty or cm.bricksAreDirty
        if type == "ANIMATION":
            return commonNeedsUpdate or (cm.materialType != "CUSTOM" and cm.materialIsDirty)
        elif type == "MODEL":
            return commonNeedsUpdate or (cm.collection is not None and len(cm.collection.objects) == 0) or (cm.materialType != "CUSTOM" and (cm.materialType != "RANDOM" or cm.splitModel or cm.lastMaterialType != cm.materialType or cm.materialIsDirty) and cm.materialIsDirty) or cm.hasCustomObj1 or cm.hasCustomObj2 or cm.hasCustomObj3
