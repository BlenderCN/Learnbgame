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
from bpy.props import *
from bpy.types import UIList

# Addon imports
from ..functions import *
from .matlist_utils import *


# ui list item actions
class BRICKER_OT_matlist_actions(bpy.types.Operator):
    bl_idname = "bricker.mat_list_action"
    bl_label = "Mat Slots List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    # @classmethod
    # def poll(self, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     scn = context.scene
    #     for cm in scn.matlist:
    #         if cm.animated:
    #             return False
    #     return True

    def execute(self, context):
        try:
            scn, cm, n = getActiveContextInfo()
            matObj = getMatObject(cm.id, typ="RANDOM" if cm.materialType == "RANDOM" else "ABS")
            idx = matObj.active_material_index

            if self.action == 'REMOVE':
                self.removeItem(cm, matObj, idx)

            elif self.action == 'DOWN' and idx < len(scn.cmlist) - 1:
                self.navigateDown(item)

            elif self.action == 'UP' and idx >= 1:
                self.moveUp(item)
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    def removeItem(self, cm, matObj, idx):
        if idx >= len(matObj.data.materials) or idx < 0 or len(matObj.data.materials) == 0:
            return
        mat = matObj.data.materials.pop(index=idx)
        if not cm.lastSplitModel:
            cm.materialIsDirty = True
