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

# Addon imports
from ..functions import *


class BRICKER_OT_uv_unwrap(bpy.types.Operator):
    """ Create Smart UV Project for bricks """
    bl_idname = "bricker.uv_unwrap"
    bl_label = "Create Smart UV Project for Bricks"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        return True

    def execute(self, context):
        bricks = getBricks()
        select(bricks[0], active=True, only=True)
        bpy.ops.uv.smart_project()
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        pass

    #############################################
    # class methods


    #############################################
