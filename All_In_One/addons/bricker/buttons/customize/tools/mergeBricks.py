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
from ..undo_stack import *
from ..functions import *
from ...brickify import *
from ...brickify import *
from ....lib.bricksDict.functions import getDictKey
from ....lib.Brick.legal_brick_sizes import *
from ....functions import *


class BRICKER_OT_merge_bricks(Operator):
    """Merge selected bricks (auto-converts brick type to 'BRICK' or 'PLATE')"""
    bl_idname = "bricker.merge_bricks"
    bl_label = "Merge Bricks"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns False) """
        scn = bpy.context.scene
        objs = bpy.context.selected_objects
        i = 0
        # check that at least 2 objects are selected and are bricks
        for obj in objs:
            if not obj.isBrick:
                continue
            # get cmlist item referred to by object
            cm = getItemByID(scn.cmlist, obj.cmlist_id)
            if cm.lastBrickType == "CUSTOM" or cm.buildIsDirty:
                continue
            i += 1
            if i == 2:
                return True
        return False

    def execute(self, context):
        try:
            scn = bpy.context.scene
            objsToSelect = []
            # iterate through cm_ids of selected objects
            for cm_id in self.objNamesD.keys():
                cm = getItemByID(scn.cmlist, cm_id)
                self.undo_stack.iterateStates(cm)
                # initialize vars
                bricksDict = self.bricksDicts[cm_id]
                allSplitKeys = list()
                cm.customized = True
                brickType = cm.brickType

                # iterate through cm_ids of selected objects
                for obj_name in self.objNamesD[cm_id]:
                    # initialize vars
                    dictKey = getDictKey(obj_name)

                    # split brick in matrix
                    splitKeys = Bricks.split(bricksDict, dictKey, cm.zStep, brickType)
                    allSplitKeys += splitKeys
                    # delete the object that was split
                    delete(bpy.data.objects.get(obj_name))

                # run self.mergeBricks
                keysToUpdate = BRICKER_OT_merge_bricks.mergeBricks(bricksDict, allSplitKeys, cm, anyHeight=True, mergeInconsistentMats=self.mergeInconsistentMats)

                # draw modified bricks
                drawUpdatedBricks(cm, bricksDict, keysToUpdate)

                # add selected objects to objects to select at the end
                objsToSelect += bpy.context.selected_objects
            # select the new objects created
            select(objsToSelect)
            bpy.props.bricker_last_selected = [obj.name for obj in bpy.context.selected_objects]
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn = bpy.context.scene
        # initialize vars
        selected_objects = bpy.context.selected_objects
        self.objNamesD, self.bricksDicts = createObjNamesAndBricksDictsDs(selected_objects)
        # push to undo stack
        self.undo_stack = UndoStack.get_instance()
        self.undo_stack.undo_push('merge', list(self.objNamesD.keys()))
        # set mergeInconsistentMats
        self.mergeInconsistentMats = bpy.props.bricker_last_selected == [obj.name for obj in selected_objects]

    ###################################################
    # class variables

    # variables
    bricksDicts = {}
    objNamesD = {}

    #############################################
    # class methods

    @staticmethod
    def mergeBricks(bricksDict, keys, cm, targetType="BRICK", anyHeight=False, mergeInconsistentMats=False):
        # initialize vars
        updatedKeys = []
        brickType = cm.brickType
        maxWidth = cm.maxWidth
        maxDepth = cm.maxDepth
        legalBricksOnly = cm.legalBricksOnly
        mergeInternalsH = cm.mergeInternals in ["BOTH", "HORIZONTAL"]
        mergeInternalsV = cm.mergeInternals in ["BOTH", "VERTICAL"]
        materialType = cm.materialType
        randState = np.random.RandomState(cm.mergeSeed)
        mergeVertical = targetType in getBrickTypes(height=3) and "PLATES" in brickType
        height3Only = mergeVertical and not anyHeight

        # sort keys
        keys.sort(key=lambda k: (strToList(k)[0] * strToList(k)[1] * strToList(k)[2]))

        for key in keys:
            # skip keys already merged to another brick
            if bricksDict[key]["parent"] not in (None, "self"):
                continue
            # attempt to merge current brick with other bricks in keys, according to available brick types
            brickSize,_ = attemptMerge(bricksDict, key, keys, bricksDict[key]["size"], cm.zStep, randState, brickType, maxWidth, maxDepth, legalBricksOnly, mergeInternalsH, mergeInternalsV, materialType, mergeInconsistentMats=mergeInconsistentMats, preferLargest=True, mergeVertical=mergeVertical, targetType=targetType, height3Only=height3Only)
            updatedKeys.append(key)
        return updatedKeys

    #############################################
