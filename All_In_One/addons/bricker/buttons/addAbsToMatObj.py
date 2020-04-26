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

# Addon imports
from ..functions import *


class BRICKER_OT_add_abs_to_mat_obj(bpy.types.Operator):
    """Add all ABS Plastic Materials to the list of materials to use for Brickifying object"""
    bl_idname = "bricker.add_abs_plastic_materials"
    bl_label = "Add ABS Plastic Materials"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.cmlist_index == -1:
            return False
        return True

    def execute(self, context):
        try:
            scn, cm, _ = getActiveContextInfo()
            matObj = getMatObject(cm.id, typ="RANDOM" if cm.materialType == "RANDOM" else "ABS")
            cm.materialIsDirty = True
            for mat_name in getABSMatNames(all=False):
                mat = bpy.data.materials.get(mat_name)
                if mat is not None and mat_name not in matObj.data.materials:
                    matObj.data.materials.append(mat)

        except:
            bricker_handle_exception()
        return{"FINISHED"}

    ################################################
