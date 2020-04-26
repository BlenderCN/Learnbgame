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
import bpy
import os
import time
from mathutils import Matrix, Vector

# Blender imports
# NONE!

# Addon imports
from ..functions import *


class ABS_OT_mark_outdated(bpy.types.Operator):
    """Mark ABS Plastic Materials as outdated"""                                # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "abs.mark_outdated"                                             # unique identifier for buttons and menu items to reference.
    bl_label = "Mark ABS Plastic Materials Outdated"                            # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    # @classmethod
    # def poll(self, context):
    #     # TODO: Speed this up
    #     matNames = getMatNames()
    #     for mat in bpy.data.materials:
    #         if mat.name in matNames:
    #             return True
    #     return False

    def execute(self, context):
        for mat_n in getMatNames():
            m = bpy.data.materials.get(mat_n)
            if m is None:
                continue
            cur_version = [int(v) for v in m.abs_plastic_version.split(".")]
            cur_version[-1] -= 1
            m.abs_plastic_version = str(cur_version)[1:-1].replace(", ", ".")
        self.report({"INFO"}, "ABS Plastic Materials were marked as outdated")
        return {"FINISHED"}
