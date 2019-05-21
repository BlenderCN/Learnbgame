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
import copy

# Blender imports
import bpy
from bpy.types import Operator
from bpy.props import *

# Addon imports
from .mergeBricks import *
from ..undo_stack import *
from ..functions import *
from ...brickify import *
from ...brickify import *
from ....lib.bricksDict.functions import getDictKey
from ....lib.Brick.legal_brick_sizes import *
from ....functions import *


class BRICKER_OT_draw_adjacent(Operator):
    """Draw new brick(s) adjacent to active brick"""
    bl_idname = "bricker.draw_adjacent"
    bl_label = "Draw Adjacent Bricks"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns False) """
        scn = bpy.context.scene
        active_obj = bpy.context.active_object
        # check active object is not None
        if active_obj is None:
            return False
        # check that active_object is brick
        if not active_obj.isBrick:
            return False
        return True

    def execute(self, context):
        try:
            # only reference self.brickType once (runs get_items)
            targetType = self.brickType
            # store enabled/disabled values
            createAdjBricks = [self.xPos, self.xNeg, self.yPos, self.yNeg, self.zPos, self.zNeg]
            # if no sides were and are selected, don't execute (i.e. if only brick type changed)
            if [False]*6 == [createAdjBricks[i] or self.adjBricksCreated[i][0] for i in range(6)]:
                return {"CANCELLED"}
            scn, cm, n = getActiveContextInfo()
            # revert to last bricksDict
            self.undo_stack.matchPythonToBlenderState()
            # push to undo stack
            if self.orig_undo_stack_length == self.undo_stack.getLength():
                self.undo_stack.undo_push('draw_adjacent', affected_ids=[cm.id])
            scn.update()
            self.undo_stack.iterateStates(cm)
            # get fresh copy of self.bricksDict
            self.bricksDict = getBricksDict(cm)
            # initialize vars
            obj = bpy.context.active_object
            initial_active_obj_name = obj.name
            cm.customized = True
            keysToMerge = []
            updateHasCustomObjs(cm, targetType)

            # get dict key details of current obj
            dictKey = getDictKey(obj.name)
            dictLoc = getDictLoc(self.bricksDict, dictKey)
            x0,y0,z0 = dictLoc
            # get size of current brick (e.g. [2, 4, 1])
            objSize = self.bricksDict[dictKey]["size"]

            decriment = 0
            # check all 6 directions for action to be executed
            for i in range(6):
                # if checking beneath obj, check 3 keys below instead of 1 key below
                if i == 5 and flatBrickType(cm.brickType):
                    newBrickHeight = self.getNewBrickHeight(targetType)
                    decriment = newBrickHeight - 1
                # if action should be executed (value changed in direction prop)
                if (createAdjBricks[i] or (not createAdjBricks[i] and self.adjBricksCreated[i][0])):
                    # add or remove bricks in all adjacent locations in current direction
                    for j,adjDictLoc in enumerate(self.adjDKLs[i]):
                        if decriment != 0:
                            adjDictLoc = adjDictLoc.copy()
                            adjDictLoc[2] -= decriment
                        status = self.toggleBrick(cm, n, self.bricksDict, self.adjDKLs, self.adjBricksCreated, self.dimensions, adjDictLoc, dictKey, dictLoc, objSize, targetType, i, j, keysToMerge, addBrick=createAdjBricks[i])
                        if not status["val"]:
                            self.report({status["report_type"]}, status["msg"])
                        if status["dirBool"] is not None:
                            self.setDirBool(status["dirBool"][0], status["dirBool"][1])
                    # after ALL bricks toggled, check exposure of bricks above and below new ones
                    for j,adjDictLoc in enumerate(self.adjDKLs[i]):
                        self.bricksDict = verifyBrickExposureAboveAndBelow(scn, cm.zStep, adjDictLoc.copy(), self.bricksDict, decriment=decriment + 1, zNeg=self.zNeg, zPos=self.zPos)

            # recalculate val for each bricksDict key in original brick
            brickLocs = [[x, y, z] for z in range(z0, z0 + objSize[2], cm.zStep) for y in range(y0, y0 + objSize[1]) for x in range(x0, x0 + objSize[0])]
            for curLoc in brickLocs:
                setCurBrickVal(self.bricksDict, curLoc)

            # attempt to merge created bricks
            keysToUpdate = BRICKER_OT_merge_bricks.mergeBricks(self.bricksDict, keysToMerge, cm, targetType=targetType)

            # if bricks created on top or bottom, set exposure of original brick
            if self.zPos or self.zNeg:
                setAllBrickExposures(self.bricksDict, cm.zStep, dictKey)
                keysToUpdate.append(dictKey)

            # draw created bricks
            drawUpdatedBricks(cm, self.bricksDict, keysToUpdate, selectCreated=False)

            # select original brick
            orig_obj = bpy.data.objects.get(initial_active_obj_name)
            if orig_obj: select(orig_obj, active=True)
        except:
            bricker_handle_exception()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

    ################################################
    # initialization method

    def __init__(self):
        try:
            self.undo_stack = UndoStack.get_instance()
            self.orig_undo_stack_length = self.undo_stack.getLength()
            scn, cm, _ = getActiveContextInfo()
            obj = bpy.context.active_object
            dictKey = getDictKey(obj.name)

            # initialize self.bricksDict
            self.bricksDict = getBricksDict(cm)
            # initialize direction bools
            self.zPos, self.zNeg, self.yPos, self.yNeg, self.xPos, self.xNeg = [False] * 6
            # initialize self.dimensions
            self.dimensions = Bricks.get_dimensions(cm.brickHeight, cm.zStep, cm.gap)
            # initialize self.adjDKLs
            self.adjDKLs = getAdjDKLs(cm, self.bricksDict, dictKey, obj)
            # initialize self.adjBricksCreated
            self.adjBricksCreated = [[False] * len(self.adjDKLs[i]) for i in range(6)]
            # initialize self.brickType
            objType = self.bricksDict[dictKey]["type"]
            try:
                self.brickType = objType or ("BRICK" if objSize[2] == 3 else "PLATE")
            except TypeError:
                pass
        except:
            bricker_handle_exception()

    ###################################################
    # class variables

    # vars
    bricksDict = {}
    adjDKLs = []

    # get items for brickType prop
    def get_items(self, context):
        items = getAvailableTypes(by="ACTIVE", includeSizes="ALL")
        return items

    # define props for popup
    brickType = EnumProperty(
        name="Brick Type",
        description="Type of brick to draw adjacent to current brick",
        items=get_items,
        default=None)
    zPos = BoolProperty(name="+Z (Top)", default=False)
    zNeg = BoolProperty(name="-Z (Bottom)", default=False)
    xPos = BoolProperty(name="+X (Front)", default=False)
    xNeg = BoolProperty(name="-X (Back)", default=False)
    yPos = BoolProperty(name="+Y (Right)", default=False)
    yNeg = BoolProperty(name="-Y (Left)", default=False)

    #############################################
    # class methods

    def setDirBool(self, idx, val):
        if idx == 0: self.xPos = val
        elif idx == 1: self.xNeg = val
        elif idx == 2: self.yPos = val
        elif idx == 3: self.yNeg = val
        elif idx == 4: self.zPos = val
        elif idx == 5: self.zNeg = val

    @staticmethod
    def getBrickD(bricksDict, dkl):
        """ set up adjBrickD """
        adjacent_key = listToStr(dkl)
        try:
            brickD = bricksDict[adjacent_key]
            return adjacent_key, brickD
        except:
            return adjacent_key, False

    @staticmethod
    def getNewBrickHeight(targetType):
        newBrickHeight = 1 if targetType in getBrickTypes(height=1) else 3
        return newBrickHeight

    @staticmethod
    def getNewCoord(cm, bricksDict, origKey, origLoc, newKey, newLoc, dimensions):
        full_d = [dimensions["width"], dimensions["width"], dimensions["height"]]
        cur_co = bricksDict[origKey]["co"]
        new_co = Vector(cur_co)
        loc_diff = (newLoc[0] - origLoc[0], newLoc[1] - origLoc[1], newLoc[2] - origLoc[2])
        new_co.x += full_d[0] * loc_diff[0]
        new_co.y += full_d[1] * loc_diff[1]
        new_co.z += full_d[2] * loc_diff[2]
        new_co.x += dimensions["gap"] * (loc_diff[0] - (0 if loc_diff[0] == 0 else 1)) + (0 if loc_diff[0] == 0 else dimensions["gap"])
        new_co.y += dimensions["gap"] * (loc_diff[1] - (0 if loc_diff[1] == 0 else 1)) + (0 if loc_diff[1] == 0 else dimensions["gap"])
        new_co.z += dimensions["gap"] * (loc_diff[2] - (0 if loc_diff[2] == 0 else 1)) + (0 if loc_diff[2] == 0 else dimensions["gap"])
        return tuple(new_co)

    @staticmethod
    def isBrickAlreadyCreated(adjDKLs, adjBricksCreated, brickNum, side):
        return not (brickNum == len(adjDKLs[side]) - 1 and
                    not any(adjBricksCreated[side])) # evaluates True if all values in this list are False

    @staticmethod
    def toggleBrick(cm, n, bricksDict, adjDKLs, adjBricksCreated, dimensions, adjacent_loc, dictKey, dictLoc, objSize, targetType, side, brickNum, keysToMerge, temporaryBrick=False, addBrick=True):
        # if brick height is 3 and 'Plates' in cm.brickType
        newBrickHeight = BRICKER_OT_draw_adjacent.getNewBrickHeight(targetType)
        checkTwoMoreAbove = "PLATES" in cm.brickType and newBrickHeight == 3
        dirBool = None

        adjacent_key, adjBrickD = BRICKER_OT_draw_adjacent.getBrickD(bricksDict, adjacent_loc)

        # get duplicate of nearest_intersection tuple
        ni = bricksDict[dictKey]["near_intersection"]
        ni = tuple(ni) if type(ni) in [tuple, list] else ni
        # if key doesn't exist in bricksDict, create it
        if not adjBrickD:
            co = BRICKER_OT_draw_adjacent.getNewCoord(cm, bricksDict, dictKey, dictLoc, adjacent_key, adjacent_loc, dimensions)
            bricksDict[adjacent_key] = createBricksDictEntry(
                name=              'Bricker_%(n)s__%(adjacent_key)s' % locals(),
                loc=               adjacent_loc,
                co=                co,
                near_face=         bricksDict[dictKey]["near_face"],
                near_intersection= ni,
                mat_name=          bricksDict[dictKey]["mat_name"],
                custom_mat_name=   bricksDict[dictKey]["custom_mat_name"]
            )
            adjBrickD = bricksDict[adjacent_key]
            # dirBool = [side, False]
            # return {"val":False, "dirBool":dirBool, "report_type":"WARNING", "msg":"Matrix not available at the following location: %(adjacent_key)s" % locals()}

        # if brick exists there
        if adjBrickD["draw"] and not (addBrick and adjBricksCreated[side][brickNum]):
            # if attempting to add brick
            if addBrick:
                # reset direction bool if no bricks could be added
                if not BRICKER_OT_draw_adjacent.isBrickAlreadyCreated(adjDKLs, adjBricksCreated, brickNum, side):
                    dirBool = [side, False]
                return {"val":False, "dirBool":dirBool, "report_type":"INFO", "msg":"Brick already exists in the following location: %(adjacent_key)s" % locals()}
            # if attempting to remove brick
            elif adjBrickD["created_from"] == dictKey:
                # update bricksDict values for brick being removed
                x0, y0, z0 = adjacent_loc
                brickKeys = [listToStr((x0, y0, z0 + z)) for z in range((cm.zStep + 2) % 4 if side in (4, 5) else 1)]
                for k in brickKeys:
                    bricksDict[k]["draw"] = False
                    setCurBrickVal(bricksDict, getDictLoc(bricksDict, k), k, action="REMOVE")
                    bricksDict[k]["size"] = None
                    bricksDict[k]["parent"] = None
                    bricksDict[k]["bot_exposed"] = None
                    bricksDict[k]["top_exposed"] = None
                    bricksDict[k]["created_from"] = None
                adjBricksCreated[side][brickNum] = False
                return {"val":True, "dirBool":dirBool, "report_type":None, "msg":None}
        # if brick doesn't exist there
        else:
            # if attempting to remove brick
            if not addBrick:
                return {"val":False, "dirBool":dirBool, "report_type":"INFO", "msg":"Brick does not exist in the following location: %(adjacent_key)s" % locals()}
            # check if locs above current are available
            curType = adjBricksCreated[side][brickNum] if adjBricksCreated[side][brickNum] else "PLATE"
            if checkTwoMoreAbove:
                x0, y0, z0 = adjacent_loc
                for z in range(1, 3):
                    newKey = listToStr((x0, y0, z0 + z))
                    # if brick drawn in next loc and not just rerunning based on new direction selection
                    if (newKey in bricksDict and bricksDict[newKey]["draw"] and
                        (not BRICKER_OT_draw_adjacent.isBrickAlreadyCreated(adjDKLs, adjBricksCreated, brickNum, side) or
                         curType not in getBrickTypes(height=3)) and not
                         (z == 2 and curType in getBrickTypes(height=1) and targetType not in getBrickTypes(height=1))):
                        # reset values at failed location, in case brick was previously drawn there
                        adjBricksCreated[side][brickNum] = False
                        adjBrickD["draw"] = False
                        dirBool = [side, False]
                        return {"val":False, "dirBool":dirBool, "report_type":"INFO", "msg":"Brick already exists in the following location: %(newKey)s" % locals()}
                    elif side in (4, 5):
                        keysToMerge.append(newKey)
            # update dictionary of locations above brick
            if flatBrickType(cm.brickType) and side in (4, 5):
                updateBrickSizeAndDict(dimensions, n, bricksDict, [1, 1, newBrickHeight], adjacent_key, adjacent_loc, dec=2 if side == 5 else 0, curType=curType, targetType=targetType, createdFrom=dictKey)
            # update dictionary location of adjacent brick created
            adjBrickD["draw"] = True
            adjBrickD["type"] = targetType
            adjBrickD["flipped"] = bricksDict[dictKey]["flipped"]
            adjBrickD["rotated"] = bricksDict[dictKey]["rotated"]
            setCurBrickVal(bricksDict, adjacent_loc, adjacent_key)
            adjBrickD["size"] = [1, 1, newBrickHeight if side in (4, 5) else cm.zStep]
            adjBrickD["parent"] = "self"
            adjBrickD["mat_name"] = bricksDict[dictKey]["mat_name"] if adjBrickD["mat_name"] == "" else adjBrickD["mat_name"]
            adjBrickD["custom_mat_name"] = bricksDict[dictKey]["custom_mat_name"]
            adjBrickD["near_face"] = adjBrickD["near_face"] or bricksDict[dictKey]["near_face"]
            adjBrickD["near_intersection"] = adjBrickD["near_intersection"] or ni
            if temporaryBrick:
                adjBrickD["top_exposed"] = True
                adjBrickD["bot_exposed"] = False
            else:
                setAllBrickExposures(bricksDict, cm.zStep, adjacent_key)
            adjBrickD["created_from"] = dictKey
            keysToMerge.append(adjacent_key)
            # set adjBricksCreated to target brick type for current side
            adjBricksCreated[side][brickNum] = targetType

            return {"val":True, "dirBool":dirBool, "report_type":None, "msg":None}

    #############################################
