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
import os

# Blender imports
import bpy
props = bpy.props

# Addon imports
from .customize.undo_stack import *
from ..lib.caches import *
from ..functions import *


class BRICKER_OT_clear_cache(bpy.types.Operator):
    """Clear brick mesh and matrix cache (Model customizations will be lost)"""
    bl_idname = "bricker.clear_cache"
    bl_label = "Clear Cache"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        if not bpy.props.bricker_initialized:
            return False
        return True

    def execute(self, context):
        try:
            scn, cm, _ = getActiveContextInfo()
            self.undo_stack.iterateStates(cm)
            cm.matrixIsDirty = True
            self.clearCaches()
        except:
            bricker_handle_exception()

        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        self.undo_stack = UndoStack.get_instance()
        self.undo_stack.undo_push('clear_cache')

    #############################################
    # class methods

    @staticmethod
    def clearCache(cm, brick_mesh=True, light_matrix=True, deep_matrix=True):
        """clear caches for cmlist item"""
        # clear light brick mesh cache
        if brick_mesh:
            bricker_mesh_cache[cm.id] = None
        # clear light matrix cache
        if light_matrix:
            bricker_bfm_cache[cm.id] = None
        # clear deep matrix cache
        if deep_matrix:
            cm.BFMCache = ""

    @staticmethod
    def clearCaches(brick_mesh=True, light_matrix=True, deep_matrix=True):
        """clear all caches in cmlist"""
        scn = bpy.context.scene
        for cm in scn.cmlist:
            BRICKER_OT_clear_cache.clearCache(cm, brick_mesh=brick_mesh, light_matrix=light_matrix, deep_matrix=deep_matrix)
