# Copyright (C) 2018 Christopher Gearhart
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
import bpy
import io
import json
import os
import subprocess
import time

from bpy.types import Operator
from bpy.props import *
from ..functions import *

class listMissingFrames(Operator):
    """List the output files missing from the render dump folder"""             # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render_farm.list_frames"                                       # unique identifier for buttons and menu items to reference.
    bl_label = "List Missing Frames"                                            # display name in the interface.
    bl_options = {"REGISTER"}                                                   # enable undo for the operator.

    def execute(self, context):
        try:
            scn = context.scene
            # initializes self.rfc_frameRangesDict (returns False if frame range invalid)
            if not setFrameRangesDict(self):
                return{"FINISHED"}
            # list all missing files from start frame to end frame in render dump folder
            missingFrames = listMissingFiles(getNameOutputFiles(), self.rfc_frameRangesDict["string"])
            self.report({"INFO"}, "Missing frames: %(missingFrames)s" % locals() if len(missingFrames) > 0 else "All frames accounted for!")
            return{"FINISHED"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}


class setToMissingFrames(Operator):
    """Set frame range to frames missing from the render dump folder"""         # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render_farm.set_to_missing_frames"                             # unique identifier for buttons and menu items to reference.
    bl_label = "Set to Missing Frames"                                          # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    def execute(self, context):
        try:
            scn = context.scene
            # initializes self.rfc_frameRangesDict (returns False if frame range invalid)
            if not setFrameRangesDict(self):
                return{"FINISHED"}
            # list all missing files from start frame to end frame in render dump location
            scn.rfc_frameRanges = listMissingFiles(getNameOutputFiles(), self.rfc_frameRangesDict["string"])
            return{"FINISHED"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}
