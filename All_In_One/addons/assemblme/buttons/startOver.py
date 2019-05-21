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
props = bpy.props

# Addon imports
from ..functions import *

class ASSEMBLME_OT_start_over(bpy.types.Operator):
    """Clear animation from objects moved in last 'Create Build Animation' action""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.start_over"                                          # unique identifier for buttons and menu items to reference.
    bl_label = "Start Over"                                                     # display name in the interface.
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
        if ag.animated:
            return True
        return False

    def execute(self, context):
        try:
            self.startOver()
        except:
            assemblme_handle_exception()
        return{"FINISHED"}

    ###################################################
    # initialization method

    def __init__(self):
        self.origFrame = bpy.context.scene.frame_current

    ###################################################
    # class methods

    @timed_call("Time Elapsed")
    def startOver(self):
        # initialize vars
        scn, ag = getActiveContextInfo()

        # set current_frame to animation start frame
        all_ags_for_collection = [ag0 for ag0 in scn.aglist if ag0 == ag or (ag0.collection == ag.collection and ag0.animated)]
        all_ags_for_collection.sort(key=lambda x: x.time_created)
        # set frame to frameWithOrigLoc that was created first (all_ags_for_collection are sorted by time created)
        scn.frame_set(all_ags_for_collection[0].frameWithOrigLoc)

        # clear objMinLoc and objMaxLoc
        props.objMinLoc, props.objMaxLoc = 0, 0

        # clear animation data from all objects in 'AssemblMe_all_objects_moved' group/collection
        if ag.collection is not None:
            print("\nClearing animation data from " + str(len(ag.collection.objects)) + " objects.")
            clearAnimation(ag.collection.objects)

        # set current_frame to original current_frame
        scn.frame_set(self.origFrame)

        # set all animated groups as not animated
        for ag0 in all_ags_for_collection:
            ag0.animated = False
            ag0.time_created = float("inf")

    #############################################
