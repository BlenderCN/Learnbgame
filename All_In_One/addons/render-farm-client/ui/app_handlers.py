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

# System imports
import sys
import math

# Blender imports
import bpy
from bpy.app.handlers import persistent
from bpy.props import *

# Addon imports
from ..functions import *


@persistent
def refresh_servers(scn):
    updateStatus = updateServerPrefs()
    if not updateStatus["valid"]:
        sys.stderr.write(updateStatus["errorMessage"] + "\n")
        sys.stderr.flush()


@persistent
def verify_render_status_on_load(dummy):
    scn = bpy.context.scene
    replaceStatuses = ["Preparing files...", "Rendering...", "Finishing...", "ERROR", "Cancelled"]
    scn.rfc_imageRenderStatus = "None" if scn.rfc_imageRenderStatus in replaceStatuses else scn.rfc_imageRenderStatus
    scn.rfc_animRenderStatus = "None" if scn.rfc_animRenderStatus in replaceStatuses else scn.rfc_animRenderStatus
