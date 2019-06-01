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
from bpy.props import *

# Addon imports
from ..functions import *

class ASSEMBLME_OT_create_build_animation(bpy.types.Operator):
    """Select objects layer by layer and shift by given values"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.create_build_animation"                              # unique identifier for buttons and menu items to reference.
    bl_label = "Create Build Animation"                                         # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def execute(self, context):
        try:
            scn, ag = getActiveContextInfo()
            all_ags_for_collection = [ag0 for ag0 in scn.aglist if ag0 == ag or (ag0.collection == ag.collection and ag0.animated)]
            all_ags_for_collection.sort(key=lambda x: x.time_created)
            # ensure operation can run
            if not self.isValid(scn, ag):
                return {"CANCELLED"}
            # set frame to frameWithOrigLoc that was created first (all_ags_for_collection are sorted by time created)
            scn.frame_set(all_ags_for_collection[0].frameWithOrigLoc)
            # clear animation data from all objects in ag.collection
            clearAnimation(ag.collection.objects)
            # create current animation (and recreate any others for this collection that were cleared)
            for ag0 in all_ags_for_collection:
                self.createAnim(scn, ag0)
            # set current_frame to original current_frame
            scn.frame_set(self.origFrame)
        except:
            assemblme_handle_exception()
            return{"CANCELLED"}
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn, ag = getActiveContextInfo()
        self.objects_to_move = [obj for obj in ag.collection.objects if not ag.meshOnly or obj.type == "MESH"]
        self.origFrame = scn.frame_current

    ###################################################
    # class variables

    # NONE!

    ###################################################
    # class methods

    @timed_call("Time Elapsed")
    def createAnim(self, scn, ag):
        print("\ncreating build animation...")

        # initialize vars
        action = "UPDATE" if ag.animated else "CREATE"
        ag.lastLayerVelocity = getObjectVelocity(ag)
        if action == "CREATE":
            ag.time_created = time.time()

        # set current_frame to a frame where the animation is in it's initial state (if creating, this was done in 'execute')
        scn.frame_set(ag.frameWithOrigLoc if action == "UPDATE" else ag.firstFrame)

        ### BEGIN ANIMATION GENERATION ###
        # populate self.listZValues
        self.listZValues,rotXL,rotYL = getListZValues(ag, self.objects_to_move)

        # set props.objMinLoc and props.objMaxLoc
        setBoundsForVisualizer(ag, self.listZValues)

        # calculate how many frames the animation will last
        ag.animLength = getAnimLength(ag, self.objects_to_move, self.listZValues.copy(), ag.layerHeight, ag.invertBuild, ag.skipEmptySelections)

        # set first frame to animate from
        self.curFrame = ag.firstFrame + (ag.animLength if ag.buildType == "ASSEMBLE" else 0)

        # set frameWithOrigLoc for 'Start Over' operation
        ag.frameWithOrigLoc = self.curFrame

        # reset upper and lower bound values
        props.z_upper_bound = None
        props.z_lower_bound = None

        # animate the objects
        objects_moved, lastFrame = animateObjects(ag, self.objects_to_move, self.listZValues, self.curFrame, ag.locInterpolationMode, ag.rotInterpolationMode)

        # handle case where no object was ever selected (e.g. only camera passed to function).
        if action == "CREATE" and ag.frameWithOrigLoc == lastFrame:
            warningMsg = "No valid objects selected!"
            if ag.meshOnly:
                warningMsg += " (Non-mesh objects ignored – see advanced settings)"
            self.report({"WARNING"}, warningMsg)
            return{"FINISHED"}

        # reset upper and lower bound values
        props.z_upper_bound = None
        props.z_lower_bound = None

        # define animation start and end frames
        ag.animBoundsStart = ag.firstFrame if ag.buildType == "ASSEMBLE" else ag.firstFrame
        ag.animBoundsEnd   = ag.frameWithOrigLoc if ag.buildType == "ASSEMBLE" else lastFrame

        # disable relationship lines and mark as animated
        if action == "CREATE":
            disableRelationshipLines()
            ag.animated = True

    def isValid(self, scn, ag):
        if ag.collection is None:
            self.report({"WARNING"}, "No collection name specified" if b280() else "No group name specified")
            return False
        if len(ag.collection.objects) == 0:
            self.report({"WARNING"}, "Collection contains no objects!" if b280() else "Group contains no objects!")
            return False
        # check if this would overlap with other animations
        other_anim_ags = [ag0 for ag0 in scn.aglist if ag0 != ag and ag0.collection == ag.collection and ag0.animated]
        for ag1 in other_anim_ags:
            if ag1.animBoundsStart <= ag.firstFrame and ag.firstFrame <= ag1.animBoundsEnd:
                self.report({"WARNING"}, "Animation overlaps with another AssemblMe aninmation for this collection")
                return False
        # make sure no objects in this collection are part of another AssemblMe animation
        for i in range(len(scn.aglist)):
            c = scn.aglist[i].collection
            if i == scn.aglist_index or not scn.aglist[i].animated or c.name == ag.collection.name:
                continue
            for obj in self.objects_to_move:
                users_collection = obj.users_collection if b280() else obj.users_group
                if c in users_collection:
                    self.report({"ERROR"}, "Some objects in this collection are part of another AssemblMe animation")
                    return False
        return True

    #############################################
