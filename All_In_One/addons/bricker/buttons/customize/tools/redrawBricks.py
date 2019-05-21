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
from ....functions import *


class BRICKER_OT_redraw_bricks(Operator):
    """redraw selected bricks from bricksDict"""
    bl_idname = "bricker.redraw_bricks"
    bl_label = "Redraw Bricks"
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
            if obj.isBrick:
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
                # get bricksDict from cache
                bricksDict, _ = self.bricksDicts[cm_id]
                keysToUpdate = []

                # add keys for updated objects to simple bricksDict for drawing
                keysToUpdate = [getDictKey(obj.name) for obj in self.objNamesD[cm_id]]

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
        try:
            self.objNamesD, self.bricksDicts = createObjNamesAndBricksDictsDs(selected_objects)
        except:
            bricker_handle_exception()

    ###################################################
    # class variables

    # vars
    bricksDicts = {}
    objNamesD = {}

    #############################################
