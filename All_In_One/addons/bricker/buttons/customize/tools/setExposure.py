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


class BRICKER_OT_set_exposure(Operator):
    """Set exposure of bricks to correct insideness calculation (consider setting ‘Advanced > Insideness Ray Cast Direction’ to ‘XYZ’ instead)"""
    bl_idname = "bricker.set_exposure"
    bl_label = "Set Exposure"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns False) """
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
        try:
            scn = bpy.context.scene
            selected_objects = bpy.context.selected_objects
            active_obj = bpy.context.active_object
            initial_active_obj_name = active_obj.name if active_obj else ""
            objsToSelect = []

            # iterate through cm_ids of selected objects
            for cm_id in self.objNamesD.keys():
                cm = getItemByID(scn.cmlist, cm_id)
                self.undo_stack.iterateStates(cm)
                bricksDict = json.loads(self.cached_bfm[cm_id])
                keysToUpdate = []
                cm.customized = True
                zStep = cm.zStep

                # iterate through names of selected objects
                for obj_name in self.objNamesD[cm_id]:
                    # get dict key details of current obj
                    dictKey = getDictKey(obj_name)
                    # get size of current brick (e.g. [2, 4, 1])
                    objSize = bricksDict[dictKey]["size"]

                    keysInBrick = getKeysInBrick(bricksDict, objSize, zStep, key=dictKey)
                    for key in keysInBrick:
                        # set top as exposed
                        if self.side in ("TOP", "BOTH"):
                            bricksDict[key]["top_exposed"] = not bricksDict[key]["top_exposed"]
                        # set bottom as exposed
                        if self.side in ("BOTTOM", "BOTH"):
                            bricksDict[key]["bot_exposed"] = not bricksDict[key]["bot_exposed"]
                    # add curKey to keysToUpdate
                    keysToUpdate.append(dictKey)

                # draw modified bricks
                drawUpdatedBricks(cm, bricksDict, keysToUpdate)
                # add selected objects to objects to select at the end
                objsToSelect += bpy.context.selected_objects
            # select the new objects created
            select(objsToSelect)
            orig_obj = bpy.data.objects.get(initial_active_obj_name)
            setActiveObj(orig_obj)
        except:
            bricker_handle_exception()
        return {"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn = bpy.context.scene
        # initialize bricksDicts
        selected_objects = bpy.context.selected_objects
        self.objNamesD, self.bricksDicts = createObjNamesAndBricksDictsDs(selected_objects)
        # push to undo stack
        self.undo_stack = UndoStack.get_instance()
        self.cached_bfm = self.undo_stack.undo_push('exposure', affected_ids=list(self.objNamesD.keys()))

    ###################################################
    # class variables

    # variables
    bricksDicts = {}
    objNamesD = {}

    # properties
    side = bpy.props.EnumProperty(
        items=(("TOP", "Top", ""),
               ("BOTTOM", "Bottom", ""),
               ("BOTH", "Both", ""),),
        default="TOP")

    #############################################
