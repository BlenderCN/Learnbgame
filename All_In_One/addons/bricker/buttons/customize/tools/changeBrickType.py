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

# Addon imports
from ..undo_stack import *
from ..functions import *
from ...brickify import *
from ...brickify import *
from ....lib.bricksDict.functions import getDictKey
from ....lib.Brick.legal_brick_sizes import *
from ....functions import *


class BRICKER_OT_change_brick_type(Operator):
    """Change brick type of active brick"""
    bl_idname = "bricker.change_brick_type"
    bl_label = "Change Brick Type"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns False) """
        if not bpy.props.bricker_initialized:
            return False
        scn = bpy.context.scene
        objs = bpy.context.selected_objects
        # check that at least 1 selected object is a brick
        for obj in objs:
            if not obj.isBrick:
                continue
            # get cmlist item referred to by object
            cm = getItemByID(scn.cmlist, obj.cmlist_id)
            return True
        return False

    def execute(self, context):
        wm = bpy.context.window_manager
        wm.Bricker_runningBlockingOperation = True
        try:
            self.changeType()
        except:
            bricker_handle_exception()
        wm.Bricker_runningBlockingOperation = False
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

    ################################################
    # initialization method

    def __init__(self):
        try:
            self.undo_stack = UndoStack.get_instance()
            self.orig_undo_stack_length = self.undo_stack.getLength()
            self.aboveKeysParented = []
            scn = bpy.context.scene
            selected_objects = bpy.context.selected_objects
            # initialize self.flipBrick, self.rotateBrick, and self.brickType
            for obj in selected_objects:
                if not obj.isBrick:
                    continue
                # get cmlist item referred to by object
                cm = getItemByID(scn.cmlist, obj.cmlist_id)
                # get bricksDict from cache
                bricksDict = getBricksDict(cm)
                dictKey = getDictKey(obj.name)
                # initialize properties
                curBrickType = bricksDict[dictKey]["type"]
                curBrickSize = bricksDict[dictKey]["size"]
                try:
                    self.flipBrick = bricksDict[dictKey]["flipped"]
                    self.rotateBrick = bricksDict[dictKey]["rotated"]
                    self.brickType = curBrickType or ("BRICK" if curBrickSize[2] == 3 else "PLATE")
                except TypeError:
                    pass
                break
            self.objNamesD, self.bricksDicts = createObjNamesAndBricksDictsDs(selected_objects)
        except:
            bricker_handle_exception()

    ###################################################
    # class variables

    # vars
    bricksDicts = {}
    bricksDict = {}
    objNamesD = {}

    # get items for brickType prop
    def get_items(self, context):
        items = getAvailableTypes(by="SELECTION")
        return items


    # properties
    brickType = bpy.props.EnumProperty(
        name="Brick Type",
        description="Choose what type of brick should be drawn at this location",
        items=get_items,
        default=None)
    flipBrick = bpy.props.BoolProperty(
        name="Flip Brick Orientation",
        description="Flip the brick about the non-mirrored axis",
        default=False)
    rotateBrick = bpy.props.BoolProperty(
        name="Rotate 90 Degrees",
        description="Rotate the brick about the Z axis (brick width & depth must be equivalent)",
        default=False)

    ###################################################
    # class methods

    def changeType(self):
        # revert to last bricksDict
        self.undo_stack.matchPythonToBlenderState()
        # push to undo stack
        if self.orig_undo_stack_length == self.undo_stack.getLength():
            self.undo_stack.undo_push('change_type', affected_ids=list(self.objNamesD.keys()))
        scn = bpy.context.scene
        legalBrickSizes = bpy.props.Bricker_legal_brick_sizes
        # get original active and selected objects
        active_obj = bpy.context.active_object
        initial_active_obj_name = active_obj.name if active_obj else ""
        selected_objects = bpy.context.selected_objects
        objNamesToSelect = []
        bricksWereGenerated = False
        # only reference self.brickType once (runs get_items)
        targetBrickType = self.brickType

        # iterate through cm_ids of selected objects
        for cm_id in self.objNamesD.keys():
            cm = getItemByID(scn.cmlist, cm_id)
            self.undo_stack.iterateStates(cm)
            # initialize vars
            bricksDict = deepcopy(self.bricksDicts[cm_id])
            keysToUpdate = set()
            updateHasCustomObjs(cm, targetBrickType)
            cm.customized = True
            brickType = cm.brickType
            brickHeight = cm.brickHeight
            gap = cm.gap

            # iterate through names of selected objects
            for obj_name in self.objNamesD[cm_id]:
                # initialize vars
                dictKey = getDictKey(obj_name)
                dictLoc = getDictLoc(bricksDict, dictKey)
                x0, y0, z0 = dictLoc
                # get size of current brick (e.g. [2, 4, 1])
                size = bricksDict[dictKey]["size"]
                typ = bricksDict[dictKey]["type"]

                # skip bricks that are already of type self.brickType
                if (typ == targetBrickType
                    and (not typ.startswith("SLOPE")
                         or (bricksDict[dictKey]["flipped"] == self.flipBrick
                             and bricksDict[dictKey]["rotated"] == self.rotateBrick))):
                    continue
                # skip bricks that can't be turned into the chosen brick type
                if size[:2] not in legalBrickSizes[3 if targetBrickType in getBrickTypes(height=3) else 1][targetBrickType]:
                    continue

                # verify locations above are not obstructed
                if targetBrickType in getBrickTypes(height=3) and size[2] == 1:
                    aboveKeys = [listToStr((x0 + x, y0 + y, z0 + z)) for z in range(1, 3) for y in range(size[1]) for x in range(size[0])]
                    obstructed = False
                    for curKey in aboveKeys:
                        if curKey in bricksDict and bricksDict[curKey]["draw"]:
                            self.report({"INFO"}, "Could not change to type {brickType}; some locations are occupied".format(brickType=targetBrickType))
                            obstructed = True
                            break
                    if obstructed: continue

                # set type of parent brick to targetBrickType
                lastType = bricksDict[dictKey]["type"]
                bricksDict[dictKey]["type"] = targetBrickType
                bricksDict[dictKey]["flipped"] = self.flipBrick
                bricksDict[dictKey]["rotated"] = False if min(size[:2]) == 1 and max(size[:2]) > 1 else self.rotateBrick

                # update height of brick if necessary, and update dictionary accordingly
                if flatBrickType(brickType):
                    dimensions = Bricks.get_dimensions(brickHeight, cm.zStep, gap)
                    size = updateBrickSizeAndDict(dimensions, getSourceName(cm), bricksDict, size, dictKey, dictLoc, curHeight=size[2], targetType=targetBrickType)

                # check if brick spans 3 matrix locations
                bAndPBrick = flatBrickType(brickType) and size[2] == 3

                # verify exposure above and below
                brickLocs = getLocsInBrick(bricksDict, size, cm.zStep, dictLoc)
                for curLoc in brickLocs:
                    bricksDict = verifyBrickExposureAboveAndBelow(scn, cm.zStep, curLoc, bricksDict, decriment=3 if bAndPBrick else 1)
                    # add bricks to keysToUpdate
                    keysToUpdate |= set([getParentKey(bricksDict, listToStr((x0 + x, y0 + y, z0 + z))) for z in (-1, 0, 3 if bAndPBrick else 1) for y in range(size[1]) for x in range(size[0])])
                objNamesToSelect += [bricksDict[listToStr(loc)]["name"] for loc in brickLocs]

            # remove null keys
            keysToUpdate = [x for x in keysToUpdate if x != None]
            # if something was updated, set bricksWereGenerated
            bricksWereGenerated = bricksWereGenerated or len(keysToUpdate) > 0

            # draw updated brick
            drawUpdatedBricks(cm, bricksDict, keysToUpdate, selectCreated=False)
        # select original bricks
        orig_obj = bpy.data.objects.get(initial_active_obj_name)
        if orig_obj is not None: setActiveObj(orig_obj)
        objsToSelect = [bpy.data.objects.get(obj_n) for obj_n in objNamesToSelect if bpy.data.objects.get(obj_n) is not None]
        select(objsToSelect)
        # store current bricksDict to cache when re-run with original brick type so bricksDict is updated
        if not bricksWereGenerated:
            cacheBricksDict("CREATE", cm, bricksDict)
        # print helpful message to user in blender interface
        if bricksWereGenerated:
            self.report({"INFO"}, "Changed bricks to type '{targetType}'".format(size=listToStr(size).replace(",", "x"), targetType=targetBrickType))

    #############################################
