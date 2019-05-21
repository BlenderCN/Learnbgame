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
from .refreshServers import *
from ..functions import *

class sendAnimation(Operator):
    """Render animation on remote servers"""                                    # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render_farm.render_animation_on_servers"                             # unique identifier for buttons and menu items to reference.
    bl_label = "Render Animation"                                               # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if not have_internet():
            return False
        return True

    def modal(self, context, event):
        scn = context.scene

        try:
            if event.type in {"LEFT_SHIFT", "RIGHT_SHIFT"} and event.value == "PRESS":
                self.shift = True
            if event.type in {"LEFT_SHIFT", "RIGHT_SHIFT"} and event.value == "RELEASE":
                self.shift = False

            if event.type in {"ESC"} and event.value == "PRESS":
                if self.state[0] == 3:
                    self.renderCancelled = True
                    self.processes[0].kill()
                    setRenderStatus("animation", "Finishing...")
                    self.report({"INFO"}, "Render process cancelled. Fetching frames...")
                else:
                    self.report({"INFO"}, "Render process cancelled")
                    setRenderStatus("animation", "Cancelled")
                    self.cancel(context)
                    return{"CANCELLED"}

            elif event.type in {"P"} and self.shift and not self.processes[1]:
                if self.state[0] == 3:
                    self.report({"INFO"}, "Checking render status...")
                    self.processes[1] = getFrames(self.projectName, not self.statusChecked, self.expandedFrameRange)
                    self.state[1] = 4
                elif self.state[0] < 3:
                    self.report({"WARNING"}, "Files are still transferring - try again in a moment")

            if event.type == "TIMER":
                numIters = 1
                if self.processes[1]:
                    numIters += 1
                for i in range(numIters):
                    self.processes[i].poll()

                    if self.processes[i].returncode is not None:
                        # handle rsync error of no output files found on server
                        if self.state[i] == 4 and self.processes[i].returncode == 23:
                            if i == 1 and not self.statusChecked:
                                self.report({"WARNING"}, "No render files found - try again in a moment")
                                self.processes[1] = False
                                self.state[1] = -1
                                break
                            elif self.renderCancelled and not self.statusChecked:
                                self.report({"INFO"}, "Process cancelled - No output images found on host server")
                                setRenderStatus("animation", "Cancelled")
                                self.cancel(context)
                                return{"CANCELLED"}
                            elif not self.statusChecked:
                                self.report({"INFO"}, "No render files found on host server")
                                setRenderStatus("animation", "Complete!")
                                return{"FINISHED"}
                            else:
                                pass
                        # handle network connection error for checking status
                        elif i == 1 and self.processes[i].returncode == 12 and self.state[i] == 4:
                            self.report({"WARNING"}, "Network connection error")
                            break
                        # handle python not found on host error
                        elif self.processes[i].returncode == 127 and self.state[i] == 3:
                            self.report({"ERROR"}, "python and/or rsync not installed on host server")
                            setRenderStatus("animation", "ERROR")
                            self.cancel(context)
                            return{"CANCELLED"}
                        # handle unidentified errors
                        elif self.processes[i].returncode > 1:
                            setRenderStatus("animation", "ERROR")
                            self.errorSource = "Processes[{i}] at state {state}".format(i=i, state=str(self.state[i])) if self.state[i] != 3 else "blender_task"
                            handleError(self, self.errorSource, i)
                            setRenderStatus("animation", "ERROR")
                            self.cancel(context)
                            return{"CANCELLED"}

                        # handle and report errors for 'blender_task' process
                        elif self.processes[i].returncode == 1 and self.state[i] == 3 and self.processes[i].stderr:
                            handleBTError(self, i)

                        # if no errors, print process finished!
                        # print("Process {curState} finished! (return code: {returnCode})".format(curState=str(self.state[i]-1), returnCode=str(self.processes[i].returncode)))

                        # copy files to host server
                        if self.state[i] == 1:
                            self.processes[i] = copyFiles()
                            self.state[i] += 1
                            return{"PASS_THROUGH"}

                        # start render process from the defined start and end frames
                        elif self.state[i] == 2:
                            bpy.props.rfc_needsUpdating = False
                            self.processes[i] = renderFrames(str(self.expandedFrameRange), self.projectName)
                            setRenderStatus("animation", "Rendering...")
                            self.state[i] += 1
                            return{"PASS_THROUGH"}

                        # get rendered frames from remote servers and archive old render files
                        elif self.state[i] == 3:
                            if self.processes[1] and self.processes[1].returncode == None:
                                self.processes[1].kill()
                            self.state[0] += 1
                            self.processes[0] = getFrames(self.projectName, not self.statusChecked, self.expandedFrameRange)
                            if not self.renderCancelled:
                                setRenderStatus("animation", "Finishing...")
                            return{"PASS_THROUGH"}

                        elif self.state[i] == 4:
                            numCompleted = getNumRenderedFiles("animation", self.expandedFrameRange, getNameOutputFiles())
                            viewString = " - View rendered frames in render dump folder" if numCompleted > 0 else ""
                            self.report({"INFO"}, "Render completed for {numCompleted}/{numSent} frames{viewString}".format(numCompleted=numCompleted, numSent=len(bpy.props.rfc_animFrameRange), viewString=viewString))
                            scn.rfc_animPreviewAvailable = True
                            if i == 1:
                                self.processes[1] = False
                                self.statusChecked = True
                            elif self.renderCancelled:
                                setRenderStatus("animation", "Complete!")
                                self.cancel(context)
                                return{"CANCELLED"}
                            else:
                                setRenderStatus("animation", "Complete!")
                                return{"FINISHED"}
                        else:
                            self.report({"ERROR"}, "ERROR: Current state not recognized.")
                            setRenderStatus("animation", "ERROR")
                            self.cancel(context)
                            return{"CANCELLED"}

            return{"PASS_THROUGH"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}

    def execute(self, context):
        try:
            scn = context.scene

            # ensure no other render processes are running
            if getRenderStatus("image") in getRunningStatuses() or getRenderStatus("animation") in getRunningStatuses():
                self.report({"WARNING"}, "Render in progress...")
                return{"CANCELLED"}
            elif scn.rfc_availableServers == 0:
                serversRefreshed = refreshServers.refreshServersBlock()
                if not serversRefreshed:
                    self.report({"WARNING"}, "Servers could not be auto-refreshed. Try manual refreshing (Ctrl R).")
                    return{"CANCELLED"}

            print("\nRunning sendAnimation function...")

            # ensure the job won't break the script
            if not jobIsValid("animation", self):
                return{"CANCELLED"}

            # initializes self.rfc_frameRangesDict (returns reports error if frame range is invalid)
            if not setFrameRangesDict(self):
                setRenderStatus("animation", "ERROR")
                return{"CANCELLED"}
            # store expanded results in 'expandedFrameRange'
            self.expandedFrameRange = expandFrames(json.loads(self.rfc_frameRangesDict["string"]))
            # restrict length of frame range string to 50000 characters
            if len(str(self.expandedFrameRange)) > 75000:
                self.report({"ERROR"}, "ERROR: Frame range too large (maximum character count after conversion to ints list: 75000)")
                return{"CANCELLED"}

            # set the file extension and frame range for use with 'open animation' button
            scn.rfc_animExtension = scn.render.file_extension
            bpy.props.rfc_animFrameRange = self.expandedFrameRange

            # start initial render process
            self.state = [1, 0] # initializes state for modal
            if bpy.props.rfc_needsUpdating or bpy.props.rfc_lastServerGroup != scn.rfc_serverGroups:
                bpy.props.rfc_lastServerGroup = scn.rfc_serverGroups
                updateStatus = updateServerPrefs()
                if not updateStatus["valid"]:
                    self.report({"ERROR"}, updateStatus["errorMessage"])
                    return{"CANCELLED"}
            else:
                self.state[0] += 1
            try:
                bpy.ops.file.pack_all()
            except RuntimeError as rte:
                self.report({"ERROR"}, str(rte))
                return{"CANCELLED"}
            rd, rt = setRemoteSettings(scn)
            self.processes = [copyProjectFile(self.projectName, scn.rfc_compress), False]
            setRemoteSettings(scn, rd, rt)

            # create timer for modal
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, context.window)
            wm.modal_handler_add(self)

            setRenderStatus("animation", "Preparing files...")
            setRenderStatus("image", "None")

            return{"RUNNING_MODAL"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}

    def __init__(self):
        scn = bpy.context.scene

        # start initial render process
        self.stdout = None
        self.stderr = None
        self.shift = False
        self.renderCancelled = False
        self.numFailedFrames = 0
        self.startFrame = scn.frame_start
        self.endFrame = scn.frame_end
        self.numFrames = str(int(scn.frame_end) - int(scn.frame_start))
        self.statusChecked = False
        self.projectName = bashSafeName(bpy.path.display_name_from_filepath(bpy.data.filepath))

        # for testing purposes only (saves unsaved file)
        if self.projectName == "":
            self.projectName = "rf_unsaved_file"

    def cancel(self, context):
        print("process cancelled")
        cleanupCancelledRender(self, context, bpy.types.Scene.rfc_killPython)
