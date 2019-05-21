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

# system imports
import time

# Blender imports
import bpy
from bpy.props import StringProperty

# Addon imports
from ..functions import *
from ..buttons.customize.functions import *


class BRICKER_OT_redraw_custom_bricks(bpy.types.Operator):
    """Redraw custom bricks with current custom object"""
    bl_idname = "bricker.redraw_custom_bricks"
    bl_label = "Redraw Custom Bricks"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        try:
            scn, cm, n = getActiveContextInfo()
        except IndexError:
            return False
        if cm.matrixIsDirty:
            return False
        return cm.modelCreated or cm.animated

    def execute(self, context):
        try:
            self.redrawCustomBricks()
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    target_prop = StringProperty(default="")

    #############################################
    # class methods

    def redrawCustomBricks(self):
        cm = getActiveContextInfo()[1]
        bricksDict = getBricksDict(cm)
        if bricksDict is None:
            return
        keysToUpdate = [k for k in bricksDict if bricksDict[k]["type"] == "CUSTOM " + self.target_prop[-1]]
        if len(keysToUpdate) != 0:
            drawUpdatedBricks(cm, bricksDict, keysToUpdate)

    #############################################
