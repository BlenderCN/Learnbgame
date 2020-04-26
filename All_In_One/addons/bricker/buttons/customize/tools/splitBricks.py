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
from bpy.types import Operator

# Addon imports
from ..undo_stack import *
from ..functions import *
from ...brickify import *
from ...brickify import *
from ....lib.bricksDict.functions import getDictKey
from ....functions import *


class BRICKER_OT_split_bricks(Operator):
    """Split selected bricks into 1x1 bricks"""
    bl_idname = "bricker.split_bricks"
    bl_label = "Split Brick(s)"
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
            if cm.lastBrickType != "CUSTOM":
                return True
        return False

    def execute(self, context):
        self.splitBricks(deepCopyMatrix=True)
        return{"FINISHED"}

    def invoke(self, context, event):
        """invoke props popup if conditions met"""
        scn = context.scene
        # iterate through cm_ids of selected objects
        for cm_id in self.objNamesD.keys():
            cm = getItemByID(scn.cmlist, cm_id)
            if not flatBrickType(cm.brickType):
                continue
            bricksDict = self.bricksDicts[cm_id]
            # iterate through names of selected objects
            for obj_name in self.objNamesD[cm_id]:
                dictKey = getDictKey(obj_name)
                size = bricksDict[dictKey]["size"]
                if size[2] <= 1:
                    continue
                if size[0] + size[1] > 2:
                    return context.window_manager.invoke_props_popup(self, event)
                else:
                    self.vertical = True
                    self.splitBricks()
                    return {"FINISHED"}
        self.horizontal = True
        self.splitBricks()
        return {"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn = bpy.context.scene
        self.undo_stack = UndoStack.get_instance()
        self.orig_undo_stack_length = self.undo_stack.getLength()
        self.vertical = False
        self.horizontal = False
        self.cached_bfm = {}
        # get copy of objNamesD and bricksDicts
        selected_objects = bpy.context.selected_objects
        self.objNamesD, self.bricksDicts = createObjNamesAndBricksDictsDs(selected_objects)

    ###################################################
    # class variables

    # variables
    objNamesD = {}
    bricksDicts = {}

    # properties
    vertical = bpy.props.BoolProperty(
        name="Vertical (plates)",
        description="Split bricks into plates",
        default=False)
    horizontal = bpy.props.BoolProperty(
        name="Horizontal",
        description="Split bricks into smaller bricks with minimum width and depth",
        default=False)

    #############################################
    # class methods

    def splitBricks(self, deepCopyMatrix=False):
        try:
            # revert to last bricksDict
            self.undo_stack.matchPythonToBlenderState()
            # push to undo stack
            if self.orig_undo_stack_length == self.undo_stack.getLength():
                self.cached_bfm = self.undo_stack.undo_push('split', affected_ids=list(self.objNamesD.keys()))
            # initialize vars
            scn = bpy.context.scene
            objsToSelect = []
            # iterate through cm_ids of selected objects
            for cm_id in self.objNamesD.keys():
                cm = getItemByID(scn.cmlist, cm_id)
                self.undo_stack.iterateStates(cm)
                bricksDict = json.loads(self.cached_bfm[cm_id]) if deepCopyMatrix else self.bricksDicts[cm_id]
                keysToUpdate = set()
                cm.customized = True

                # iterate through names of selected objects
                for obj_name in self.objNamesD[cm_id]:
                    # get dict key details of current obj
                    dictKey = getDictKey(obj_name)
                    dictLoc = getDictLoc(bricksDict, dictKey)
                    x0, y0, z0 = dictLoc
                    # get size of current brick (e.g. [2, 4, 1])
                    brickSize = bricksDict[dictKey]["size"]
                    bricksDict[dictKey]["type"] = "BRICK" if brickSize == 3 else "PLATE"

                    # skip 1x1 bricks
                    if brickSize[0] + brickSize[1] + brickSize[2] / cm.zStep == 3:
                        continue

                    if self.vertical or self.horizontal:
                        # split the bricks in the matrix and set size of active brick's bricksDict entries to 1x1x[lastZSize]
                        splitKeys = Bricks.split(bricksDict, dictKey, cm.zStep, cm.brickType, loc=dictLoc, v=self.vertical, h=self.horizontal)
                        # append new splitKeys to keysToUpdate
                        keysToUpdate |= set(splitKeys)
                    else:
                        keysToUpdate.add(dictKey)

                # draw modified bricks
                drawUpdatedBricks(cm, bricksDict, list(keysToUpdate))

                # add selected objects to objects to select at the end
                objsToSelect += bpy.context.selected_objects
            # select the new objects created
            select(objsToSelect)
        except:
            bricker_handle_exception()

    #############################################
