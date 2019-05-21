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
props = bpy.props

# Addon imports
from ..functions import *

class ASSEMBLME_OT_refresh_anim_length(bpy.types.Operator):
    """Refreshes the box in UI with build animation length"""                   # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.refresh_anim_length"                                 # unique identifier for buttons and menu items to reference.
    bl_label = "Refresh Build Animation Length"                                 # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        ag = scn.aglist[scn.aglist_index]
        if ag.collection is None:
            return False
        return True

    def execute(self, context):
        try:
            # set up variables
            scn, ag = getActiveContextInfo()

            if ag.collection:
                # if objects in ag.collection, populate objects_to_move with them
                self.objects_to_move = ag.collection.objects
                # set current_frame to animation start frame
                self.origFrame = scn.frame_current
                bpy.context.scene.frame_set(ag.frameWithOrigLoc)
            else:
                # else, populate objects_to_move with selected_objects
                self.objects_to_move = context.selected_objects

            # populate self.listZValues
            self.listZValues,_,_ = getListZValues(ag, self.objects_to_move)

            # set props.objMinLoc and props.objMaxLoc
            setBoundsForVisualizer(ag, self.listZValues)

            # calculate how many frames the animation will last (depletes self.listZValues)
            ag.animLength = getAnimLength(ag, self.objects_to_move, self.listZValues, ag.layerHeight, ag.invertBuild, ag.skipEmptySelections)

            if ag.collection:
                # set current_frame to original current_frame
                bpy.context.scene.frame_set(self.origFrame)

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None
        except:
            assemblme_handle_exception()

        return{"FINISHED"}

    #############################################
