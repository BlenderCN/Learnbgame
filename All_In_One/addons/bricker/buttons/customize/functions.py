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
import time

# Blender imports
import bpy
from bpy.types import Operator

# Addon imports
from ...functions import *
from ..brickify import *
from ..brickify import *
from ...lib.bricksDict.functions import getDictKey
from ...lib.Brick.legal_brick_sizes import *
from .undo_stack import *


def drawUpdatedBricks(cm, bricksDict, keysToUpdate, action="redrawing", selectCreated=True, tempBrick=False):
    if len(keysToUpdate) == 0: return
    if not isUnique(keysToUpdate): raise ValueError("keysToUpdate cannot contain duplicate values")
    if action is not None:
        print("[Bricker] %(action)s..." % locals())
    # get arguments for createNewBricks
    source = cm.source_obj
    source_details, dimensions = getDetailsAndBounds(source, cm)
    n = source.name
    parent = cm.parent_obj
    logo_details, refLogo = [None, None] if tempBrick else BRICKER_OT_brickify.getLogo(bpy.context.scene, cm, dimensions)
    action = "UPDATE_MODEL"
    # actually draw the bricks
    _, bricksCreated = BRICKER_OT_brickify.createNewBricks(source, parent, source_details, dimensions, refLogo, logo_details, action, cm=cm, bricksDict=bricksDict, keys=keysToUpdate, clearExistingCollection=False, selectCreated=selectCreated, printStatus=False, tempBrick=tempBrick, redraw=True)
    # link new bricks to scene
    if not b280():
        for brick in bricksCreated:
            safeLink(brick)
    # add bevel if it was previously added
    if cm.bevelAdded and not tempBrick:
        bricks = getBricks(cm)
        BRICKER_OT_bevel.runBevelAction(bricks, cm)


def getAdjKeysAndBrickVals(bricksDict, loc=None, key=None):
    assert loc or key
    x, y, z = loc or getDictLoc(bricksDict, key)
    adjKeys = [listToStr((x+1, y, z)),
               listToStr((x-1, y, z)),
               listToStr((x, y+1, z)),
               listToStr((x, y-1, z)),
               listToStr((x, y, z+1)),
               listToStr((x, y, z-1))]
    adjBrickVals = []
    for k in adjKeys.copy():
        try:
            adjBrickVals.append(bricksDict[k]["val"])
        except KeyError:
            remove_item(adjKeys, k)
    return adjKeys, adjBrickVals


def setCurBrickVal(bricksDict, loc, key=None, action="ADD"):
    key = key or listToStr(loc)
    _, adjBrickVals = getAdjKeysAndBrickVals(bricksDict, loc=loc)
    if action == "ADD" and (0 in adjBrickVals or len(adjBrickVals) < 6 or min(adjBrickVals) == 1):
        newVal = 1
    elif action == "REMOVE":
        newVal = 0 if 0 in adjBrickVals or len(adjBrickVals) < 6 else max(adjBrickVals)
    else:
        newVal = max(adjBrickVals) - 0.01
    bricksDict[key]["val"] = newVal


def verifyBrickExposureAboveAndBelow(scn, zStep, origLoc, bricksDict, decriment=0, zNeg=False, zPos=False):
    dictLocs = []
    if not zNeg:
        dictLocs.append((origLoc[0], origLoc[1], origLoc[2] + decriment))
    if not zPos:
        dictLocs.append((origLoc[0], origLoc[1], origLoc[2] - 1))
    # double check exposure of bricks above/below new adjacent brick
    for dictLoc in dictLocs:
        k = listToStr(dictLoc)
        junk1 = k not in bricksDict
        try:
            junk2 = bricksDict[k]
        except:
            pass
        if k not in bricksDict:
            continue
        parent_key = k if bricksDict[k]["parent"] == "self" else bricksDict[k]["parent"]
        if parent_key is not None:
            setAllBrickExposures(bricksDict, zStep, parent_key)
    return bricksDict


def getUsedSizes():
    scn = bpy.context.scene
    items = [("NONE", "None", "")]
    for cm in scn.cmlist:
        if not cm.brickSizesUsed:
            continue
        sortBy = lambda k: (strToList(k)[2], strToList(k)[0], strToList(k)[1])
        items += [(s, s, "") for s in sorted(cm.brickSizesUsed.split("|"), reverse=True, key=sortBy) if (s, s, "") not in items]
    return items


def getUsedTypes():
    scn = bpy.context.scene
    items = [("NONE", "None", "")]
    for cm in scn.cmlist:
        items += [(t.upper(), t.title(), "") for t in sorted(cm.brickTypesUsed.split("|")) if (t.upper(), t.title(), "") not in items]
    return items


def getAvailableTypes(by="SELECTION", includeSizes=[]):
    items = []
    legalBS = bpy.props.Bricker_legal_brick_sizes
    scn = bpy.context.scene
    objs = bpy.context.selected_objects if by == "SELECTION" else [bpy.context.active_object]
    objNamesD, bricksDicts = createObjNamesAndBricksDictsDs(objs)
    invalidItems = []
    for cm_id in objNamesD.keys():
        cm = getItemByID(scn.cmlist, cm_id)
        brickType = cm.brickType
        bricksDict = bricksDicts[cm_id]
        objSizes = []
        # check that customObjects are valid
        for idx in range(3):
            targetType = "CUSTOM " + str(idx + 1)
            warningMsg = customValidObject(cm, targetType=targetType, idx=idx)
            if warningMsg is not None and itemFromType(targetType) not in invalidItems:
                invalidItems.append(itemFromType(targetType))
        # build items list
        for obj_name in objNamesD[cm_id]:
            dictKey = getDictKey(obj_name)
            objSize = bricksDict[dictKey]["size"]
            if objSize in objSizes:
                continue
            objSizes.append(objSize)
            if objSize[2] not in (1, 3): raise Exception("Custom Error Message: objSize not in (1, 3)")
            # build items
            items += [itemFromType(typ) for typ in legalBS[3] if includeSizes == "ALL" or objSize[:2] in legalBS[3][typ] + includeSizes]
            if flatBrickType(brickType):
                items += [itemFromType(typ) for typ in legalBS[1] if includeSizes == "ALL" or objSize[:2] in legalBS[1][typ] + includeSizes]
    # uniquify items
    items = uniquify2(items, innerType=tuple)
    # remove invalid items
    for item in invalidItems:
        remove_item(items, item)
    # sort items
    items.sort(key=lambda k: k[0])
    # return items, or null if items was empty
    return items if len(items) > 0 else [("NULL", "Null", "")]


def itemFromType(typ):
    return (typ.upper(), typ.title().replace("_", " "), "")

def updateBrickSizeAndDict(dimensions, source_name, bricksDict, brickSize, key, loc, dec=0, curHeight=None, curType=None, targetHeight=None, targetType=None, createdFrom=None):
    brickD = bricksDict[key]
    assert targetHeight is not None or targetType is not None
    targetHeight = targetHeight or (1 if targetType in getBrickTypes(height=1) else 3)
    assert curHeight is not None or curType is not None
    curHeight = curHeight or (1 if curType in getBrickTypes(height=1) else 3)
    # adjust brick size if changing type from 3 tall to 1 tall
    if curHeight == 3 and targetHeight == 1:
        brickSize[2] = 1
        for x in range(brickSize[0]):
            for y in range(brickSize[1]):
                for z in range(1, curHeight):
                    newLoc = [loc[0] + x, loc[1] + y, loc[2] + z - dec]
                    newKey = listToStr(newLoc)
                    bricksDict[newKey]["parent"] = None
                    bricksDict[newKey]["draw"] = False
                    setCurBrickVal(bricksDict, newLoc, newKey, action="REMOVE")
    # adjust brick size if changing type from 1 tall to 3 tall
    elif curHeight == 1 and targetHeight == 3:
        brickSize[2] = 3
        full_d = Vector((dimensions["width"], dimensions["width"], dimensions["height"]))
        # update bricks dict entries above current brick
        for x in range(brickSize[0]):
            for y in range(brickSize[1]):
                for z in range(1, targetHeight):
                    newLoc = [loc[0] + x, loc[1] + y, loc[2] + z]
                    newKey = listToStr(newLoc)
                    # create new bricksDict entry if it doesn't exist
                    if newKey not in bricksDict:
                        bricksDict = createAddlBricksDictEntry(source_name, bricksDict, key, newKey, full_d, x, y, z)
                    # update bricksDict entry to point to new brick
                    bricksDict[newKey]["parent"] = key
                    bricksDict[newKey]["created_from"] = createdFrom
                    bricksDict[newKey]["draw"] = True
                    bricksDict[newKey]["mat_name"] = brickD["mat_name"] if bricksDict[newKey]["mat_name"] == "" else bricksDict[newKey]["mat_name"]
                    bricksDict[newKey]["near_face"] = bricksDict[newKey]["near_face"] or brickD["near_face"]
                    bricksDict[newKey]["near_intersection"] = bricksDict[newKey]["near_intersection"] or tuple(brickD["near_intersection"])
                    if bricksDict[newKey]["val"] == 0:
                        setCurBrickVal(bricksDict, newLoc, newKey)
    return brickSize


def createAddlBricksDictEntry(source_name, bricksDict, source_key, key, full_d, x, y, z):
    brickD = bricksDict[source_key]
    newName = "Bricker_%(source_name)s__%(key)s" % locals()
    newCO = (Vector(brickD["co"]) + vec_mult(Vector((x, y, z)), full_d)).to_tuple()
    bricksDict[key] = createBricksDictEntry(
        name=              newName,
        loc=               strToList(key),
        co=                newCO,
        near_face=         brickD["near_face"],
        near_intersection= tuple(brickD["near_intersection"]),
        mat_name=          brickD["mat_name"],
    )
    return bricksDict

def createObjNamesD(objs):
    scn = bpy.context.scene
    # initialize objNamesD
    objNamesD = {}
    # fill objNamesD with selected_objects
    for obj in objs:
        if obj is None or not obj.isBrick:
            continue
        # get cmlist item referred to by object
        cm = getItemByID(scn.cmlist, obj.cmlist_id)
        if cm is None: continue
        # add object to objNamesD
        if cm.id not in objNamesD:
            objNamesD[cm.id] = [obj.name]
        else:
            objNamesD[cm.id].append(obj.name)
    return objNamesD


def createObjNamesAndBricksDictsDs(objs):
    bricksDicts = {}
    objNamesD = createObjNamesD(objs)
    # initialize bricksDicts
    scn = bpy.context.scene
    for cm_id in objNamesD.keys():
        cm = getItemByID(scn.cmlist, cm_id)
        if cm is None: continue
        # get bricksDict from cache
        bricksDict = getBricksDict(cm)
        # add to bricksDicts
        bricksDicts[cm_id] = bricksDict
    return objNamesD, bricksDicts


def selectBricks(objNamesD, bricksDicts, brickSize="NULL", brickType="NULL", allModels=False, only=False, include="EXT"):
    scn = bpy.context.scene
    # split all bricks in objNamesD[cm_id]
    for cm_id in objNamesD.keys():
        cm = getItemByID(scn.cmlist, cm_id)
        if not (cm.idx == scn.cmlist_index or allModels):
            continue
        bricksDict = bricksDicts[cm_id]
        selectedSomething = False

        for obj_name in objNamesD[cm_id]:
            # get dict key details of current obj
            dictKey = getDictKey(obj_name)
            dictLoc = getDictLoc(bricksDict, dictKey)
            siz = bricksDict[dictKey]["size"]
            typ = bricksDict[dictKey]["type"]
            onShell = isOnShell(bricksDict, dictKey, loc=dictLoc, zStep=cm.zStep)

            # get current brick object
            curObj = bpy.data.objects.get(obj_name)
            # if curObj is None:
            #     continue
            # select brick
            sizeStr = listToStr(sorted(siz[:2]) + [siz[2]])
            if (sizeStr == brickSize or typ == brickType) and (include == "BOTH" or (include == "INT" and not onShell) or (include == "EXT" and onShell)):
                selectedSomething = True
                select(curObj)
            elif only:
                deselect(curObj)

        # if no brickSize bricks exist, remove from cm.brickSizesUsed or cm.brickTypesUsed
        removeUnusedFromList(cm, brickType=brickType, brickSize=brickSize, selectedSomething=selectedSomething)


def removeUnusedFromList(cm, brickType="NULL", brickSize="NULL", selectedSomething=True):
    item = brickType if brickType != "NULL" else brickSize
    # if brickType/brickSize bricks exist, return None
    if selectedSomething or item == "NULL":
        return None
    # turn brickTypesUsed into list of sizes
    lst = (cm.brickTypesUsed if brickType != "NULL" else cm.brickSizesUsed).split("|")
    # remove unused item
    if item in lst:
        remove_item(lst, item)
    # convert bTU back to string of sizes split by '|'
    newLst = listToStr(lst, separate_by="|")
    # store new list to current cmlist item
    if brickSize != "NULL":
        cm.brickSizesUsed = newLst
    else:
        cm.brickTypesUsed = newLst


def getAdjDKLs(cm, bricksDict, dictKey, obj):
    # initialize vars for self.adjDKLs setup
    x,y,z = getDictLoc(bricksDict, dictKey)
    objSize = bricksDict[dictKey]["size"]
    sX, sY, sZ = objSize[0], objSize[1], objSize[2] // cm.zStep
    adjDKLs = [[],[],[],[],[],[]]
    # initialize ranges
    rgs = [range(x, x + sX),
           range(y, y + sY),
           range(z, z + sZ)]
    # set up self.adjDKLs
    adjDKLs[0] += [[x + sX, y0, z0] for z0 in rgs[2] for y0 in rgs[1]]
    adjDKLs[1] += [[x - 1, y0, z0]  for z0 in rgs[2] for y0 in rgs[1]]
    adjDKLs[2] += [[x0, y + sY, z0] for z0 in rgs[2] for x0 in rgs[0]]
    adjDKLs[3] += [[x0, y - 1, z0]  for z0 in rgs[2] for x0 in rgs[0]]
    adjDKLs[4] += [[x0, y0, z + sZ] for y0 in rgs[1] for x0 in rgs[0]]
    adjDKLs[5] += [[x0, y0, z - 1]  for y0 in rgs[1] for x0 in rgs[0]]
    return adjDKLs


def installBrickSculpt():
    if not hasattr(bpy.props, "bricksculpt_module_name"):
        return False
    addonsPath = bpy.utils.user_resource('SCRIPTS', "addons")
    Bricker = bpy.props.bricker_module_name
    BrickSculpt = bpy.props.bricksculpt_module_name
    bricksculptPathOld = "%(addonsPath)s/%(BrickSculpt)s/bricksculpt_framework.py" % locals()
    bricksculptPathNew = "%(addonsPath)s/%(Bricker)s/buttons/customize/tools/bricksculpt_framework.py" % locals()
    fOld = open(bricksculptPathOld, "r")
    fNew = open(bricksculptPathNew, "w")
    # write META commands
    lines = fOld.readlines()
    fNew.truncate(0)
    print(lines)
    fNew.writelines(lines)
    fOld.close()
    fNew.close()
    return True
