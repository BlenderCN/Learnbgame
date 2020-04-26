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
from bpy.types import Operator
from bpy.props import *

# Addon imports
from ..functions import *
from ..ui.cmlist_actions import *

class OBJECT_OT_duplicate_override(bpy.types.Operator):
    """Duplicate selected objects (Bricker object duplicates will baked)"""
    bl_idname = "object.duplicate"
    bl_label = "Duplicate Objects"
    bl_options = {"REGISTER", "INTERNAL"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        return True

    def execute(self, context):
        self.duplicate_objects()
        return {"FINISHED"}

    def invoke(self, context, event):
        self.duplicate_objects()
        return {"FINISHED"}

    ################################################
    # Initialization method

    def __init__(self):
        self.objects = bpy.context.selected_objects

    #############################################
    # class methods

    def duplicate_objects(self):
        scn = bpy.context.scene
        newBrickerObjs = []
        lockBools = (False, False, False)
        # set isBrick/isBrickifiedObject to False
        for obj in self.objects:
            obj0 = duplicate(obj, link_to_scene=True)
            deselect(obj)
            select(obj0)
            if not (obj0.isBrick or obj0.isBrickifiedObject):
                continue
            if obj0.isBrick:
                obj0.isBrick = False
                obj0.name = obj0.name[8:].split("__")[0]
            elif obj0.isBrickifiedObject:
                obj0.isBrickifiedObject = False
                cm = getItemByID(scn.cmlist, obj0.cmlist_id)
                n = getSourceName(cm)
                obj0.name = "%(n)s_bricks" % locals()
                obj0.lock_location = lockBools
                obj0.lock_rotation = lockBools
                obj0.lock_scale    = lockBools
            obj0.cmlist_id = -1
            newBrickerObjs.append(obj0)
        if len(newBrickerObjs) > 0:
            parent_clear(newBrickerObjs)


class OBJECT_OT_duplicate_move_override(bpy.types.Operator):
    """Duplicate and Move Object"""
    bl_idname = "object.duplicate_move"
    bl_label = "Duplicate and Move Object"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        bpy.ops.object.duplicate('INVOKE_DEFAULT')
        return bpy.ops.transform.translate('INVOKE_DEFAULT')


# def register():
#     bpy.utils.register_module(__name__)
#
# def unregister():
#     addon_updater_ops.unregister()
#
# if __name__ == "__main__":
#     register()
