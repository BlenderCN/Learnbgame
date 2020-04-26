"""
    Copyright (C) 2019 Bricks Brought to Life
    http://bblanimation.com/
    chris@bblanimation.com

    Created by Christopher Gearhart

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """

# System imports
import bmesh
import math

# Blender imports
import bpy
import bgl
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d, region_2d_to_origin_3d, region_2d_to_vector_3d
from bpy.types import Operator, SpaceView3D, bpy_struct
from bpy.props import *

# Addon imports
from .drawAdjacent import *
from ..functions import *
from ...brickify import *
from ....lib.Brick import *
from ....functions import *
from ....operators.delete_object import OBJECT_OT_delete_override


class bricksculpt_tools:

    #############################################

    def addBrick(self, cm, n, curKey, curLoc, objSize):
        # get difference between intersection loc and object loc
        locDiff = self.loc - transformToWorld(Vector(self.bricksDict[curKey]["co"]), self.parent.matrix_world, self.junk_bme)
        locDiff = transformToLocal(locDiff, self.parent.matrix_world)
        nextLoc = getNearbyLocFromVector(locDiff, curLoc, self.dimensions, cm.zStep, width_divisor=3.2 if self.brickType in getRoundBrickTypes() else 2.05)
        if self.layerSolod is not None and nextLoc[2] not in range(self.layerSolod, self.layerSolod + 3 // cm.zStep):
            return
        # draw brick at nextLoc location
        nextKey, adjBrickD = BRICKER_OT_draw_adjacent.getBrickD(self.bricksDict, nextLoc)
        if not adjBrickD or self.bricksDict[nextKey]["val"] == 0:
            self.adjDKLs = getAdjDKLs(cm, self.bricksDict, curKey, self.obj)
            # add brick at nextKey location
            status = BRICKER_OT_draw_adjacent.toggleBrick(cm, n, self.bricksDict, self.adjDKLs, [[False]], self.dimensions, nextLoc, curKey, curLoc, objSize, self.brickType, 0, 0, self.keysToMergeOnCommit, temporaryBrick=True)
            if not status["val"]:
                self.report({status["report_type"]}, status["msg"])
            self.addedBricks.append(self.bricksDict[nextKey]["name"])
            self.keysToMergeOnRelease.append(nextKey)
            self.allUpdatedKeys.append(curKey)
            # draw created bricks
            drawUpdatedBricks(cm, self.bricksDict, [nextKey], action="adding new brick", selectCreated=False, tempBrick=True)

    def removeBrick(self, cm, n, event, curKey, curLoc, objSize):
        shallowDelete = curKey in self.keysToMergeOnRelease and self.mode == "DRAW"
        deepDelete = event.shift and self.mode == "DRAW" and self.obj.name not in self.addedBricksFromDelete
        if shallowDelete or deepDelete:
            # split bricks and update adjacent brickDs
            brickKeys, curKey = self.splitBrickAndGetNearest1x1(cm, n, curKey, curLoc, objSize)
            curLoc = getDictLoc(self.bricksDict, curKey)
            keysToUpdate, onlyNewKeys = OBJECT_OT_delete_override.updateAdjBricksDicts(self.bricksDict, cm.zStep, curKey, curLoc, [])
            if deepDelete:
                self.addedBricksFromDelete += [self.bricksDict[k]["name"] for k in onlyNewKeys]
            # reset bricksDict values
            self.bricksDict[curKey]["draw"] = False
            self.bricksDict[curKey]["val"] = 0
            self.bricksDict[curKey]["parent"] = None
            self.bricksDict[curKey]["created_from"] = None
            self.bricksDict[curKey]["flipped"] = False
            self.bricksDict[curKey]["rotated"] = False
            self.bricksDict[curKey]["top_exposed"] = False
            self.bricksDict[curKey]["bot_exposed"] = False
            brick = bpy.data.objects.get(self.bricksDict[curKey]["name"])
            if brick is not None:
                delete(brick)
            tag_redraw_areas("VIEW_3D")
            # draw created bricks
            drawUpdatedBricks(cm, self.bricksDict, uniquify(brickKeys + keysToUpdate), action="updating surrounding bricks", selectCreated=False, tempBrick=True)
            self.keysToMergeOnCommit += brickKeys + onlyNewKeys

    def changeMaterial(self, cm, n, curKey, curLoc, objSize):
        if max(objSize[:2]) > 1 or objSize[2] > cm.zStep:
            brickKeys, curKey = self.splitBrickAndGetNearest1x1(cm, n, curKey, curLoc, objSize)
        else:
            brickKeys = [curKey]
        self.bricksDict[curKey]["mat_name"] = self.matName
        self.bricksDict[curKey]["custom_mat_name"] = True
        self.addedBricks.append(self.bricksDict[curKey]["name"])
        self.keysToMergeOnCommit += brickKeys
        # draw created bricks
        drawUpdatedBricks(cm, self.bricksDict, brickKeys, action="updating material", selectCreated=False, tempBrick=True)

    def splitBrick(self, cm, event, curKey, curLoc, objSize):
        brick = bpy.data.objects.get(self.bricksDict[curKey]["name"])
        if (event.alt and max(self.bricksDict[curKey]["size"][:2]) > 1) or (event.shift and self.bricksDict[curKey]["size"][2] > 1):
            brickKeys = Bricks.split(self.bricksDict, curKey, cm.zStep, cm.brickType, loc=curLoc, v=event.shift, h=event.alt)
            self.allUpdatedKeys += brickKeys
            # remove large brick
            brick = bpy.data.objects.get(self.bricksDict[curKey]["name"])
            delete(brick)
            # draw split bricks
            drawUpdatedBricks(cm, self.bricksDict, brickKeys, action="splitting bricks", selectCreated=True, tempBrick=True)
        else:
            select(brick)

    def mergeBrick(self, cm, source_name, curKey=None, curLoc=None, objSize=None, mode="DRAW", state="DRAG"):
        if state == "DRAG":
            # TODO: Light up bricks as they are selected to be merged
            self.parentLocsToMergeOnRelease.append(curLoc)
            self.addedBricks.append(self.bricksDict[curKey]["name"])
            select(self.obj)
        elif state == "RELEASE":
            # assemble keysToMergeOnRelease
            for pl in self.parentLocsToMergeOnRelease:
                brickKeys = getKeysInBrick(self.bricksDict, self.bricksDict[pk]["size"], cm.zStep, loc=pl)
                self.keysToMergeOnRelease += brickKeys
            self.parentLocsToMergeOnRelease = []
            self.keysToMergeOnRelease = uniquify(self.keysToMergeOnRelease)
            # merge those keys
            if len(self.keysToMergeOnRelease) > 1:
                # delete outdated bricks
                for key in self.keysToMergeOnRelease:
                    brickName = "Bricker_%(source_name)s__%(key)s" % locals()
                    delete(bpy.data.objects.get(brickName))
                # split up bricks
                Bricks.splitAll(self.bricksDict, cm.zStep, keys=self.keysToMergeOnRelease)
                # merge bricks after they've been split
                mergedKeys = BRICKER_OT_merge_bricks.mergeBricks(self.bricksDict, self.keysToMergeOnRelease, cm, anyHeight=True)
                self.allUpdatedKeys += mergedKeys
                # draw merged bricks
                drawUpdatedBricks(cm, self.bricksDict, mergedKeys, action="merging bricks", selectCreated=False, tempBrick=True)
                # re-solo layer
                if self.layerSolod is not None:
                    zStep = cm.zStep
                    for key in mergedKeys:
                        loc = getDictLoc(self.bricksDict, key)
                        self.hideIfOnLayer(key, loc, self.layerSolod, zStep)
            else:
                deselectAll()
            # reset lists
            if mode == "MERGE/SPLIT":
                self.keysToMergeOnRelease = []
            self.addedBricks = []

    def soloLayer(self, cm, curKey, curLoc, objSize):
        brickKeys = getKeysInBrick(self.bricksDict, objSize, cm.zStep, loc=curLoc)
        assert type(brickKeys) is list
        curKey = self.getNearestLocToCursor(brickKeys)
        curZ = getDictLoc(self.bricksDict, curKey)[2]
        zStep = cm.zStep
        for key in self.bricksDict.keys():
            if self.bricksDict[key]["parent"] != "self":
                continue
            loc = getDictLoc(self.bricksDict, key)
            self.hideIfOnLayer(key, loc, curZ, zStep)
        return curZ

    def hideIfOnLayer(self, key, loc, curZ, zStep):
        if loc[2] > curZ or loc[2] + self.bricksDict[key]["size"][2] / zStep <= curZ:
            brick = bpy.data.objects.get(self.bricksDict[key]["name"])
            if brick is None:
                return
            hide(brick, render=False)
            self.hiddenBricks.append(brick)

    def unSoloLayer(self):
        [unhide(brick) for brick in self.hiddenBricks]
        self.hiddenBricks = []

    def splitBrickAndGetNearest1x1(self, cm, n, curKey, curLoc, objSize):
        brickKeys = Bricks.split(self.bricksDict, curKey, cm.zStep, cm.brickType, loc=curLoc, v=True, h=True)
        brick = bpy.data.objects.get(self.bricksDict[curKey]["name"])
        delete(brick)
        curKey = self.getNearestLocToCursor(brickKeys)
        return brickKeys, curKey

    def getNearestLocToCursor(self, keys):
        # get difference between intersection loc and object loc
        minDiff = None
        for k in keys:
            brickLoc = transformToWorld(Vector(self.bricksDict[k]["co"]), self.parent.matrix_world, self.junk_bme)
            locDiff = abs(self.loc[0] - brickLoc[0]) + abs(self.loc[1] - brickLoc[1]) + abs(self.loc[2] - brickLoc[2])
            if minDiff is None or locDiff < minDiff:
                minDiff = locDiff
                curKey = k
        return curKey

    def commitChanges(self):
        scn, cm, _ = getActiveContextInfo()
        # deselect any objects left selected, and show all objects
        deselectAll()
        self.unSoloLayer()
        # attempt to merge bricks queued for merge on commit
        self.keysToMergeOnCommit = uniquify(self.keysToMergeOnCommit)
        if mergableBrickType(self.brickType) and len(self.keysToMergeOnCommit) > 1:
            # split up bricks
            Bricks.splitAll(self.bricksDict, cm.zStep, keys=self.keysToMergeOnCommit)
            # merge split bricks
            mergedKeys = BRICKER_OT_merge_bricks.mergeBricks(self.bricksDict, self.keysToMergeOnCommit, cm, targetType="BRICK" if cm.brickType == "BRICKS AND PLATES" else self.brickType, anyHeight=cm.brickType == "BRICKS AND PLATES")
        else:
            mergedKeys = self.keysToMergeOnCommit
        # remove 1x1 bricks merged into another brick
        for k in self.keysToMergeOnCommit:
            delete(None if k in mergedKeys else bpy.data.objects.get(self.bricksDict[k]["name"]))
        # set exposure of created/updated bricks
        keysToUpdate = uniquify(mergedKeys + self.allUpdatedKeys)
        for k in keysToUpdate:
            setAllBrickExposures(self.bricksDict, cm.zStep, k)
        # draw updated bricks
        drawUpdatedBricks(cm, self.bricksDict, keysToUpdate, action="committing changes", selectCreated=False)

    #############################################
