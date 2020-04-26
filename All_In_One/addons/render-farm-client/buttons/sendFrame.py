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

class sendFrame(Operator):
    """Render current frame on remote servers"""                                # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render_farm.render_frame_on_servers"                                 # unique identifier for buttons and menu items to reference.
    bl_label = "Render Current Frame"                                           # display name in the interface.
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

            if event.type in {"ESC"} and event.value == "PRESS" and not self.processes[1]:
                if self.state[0] == 3:
                    self.renderCancelled = True
                    self.processes[0].kill()
                    setRenderStatus("image", "Finishing...")
                    self.report({"INFO"}, "Render process cancelled. Fetching frames...")
                else:
                    self.report({"INFO"}, "Render process cancelled")
                    setRenderStatus("image", "Cancelled")
                    self.cancel(context)
                    return{"CANCELLED"}

            elif event.type in {"P"} and self.shift and not self.processes[1]:
                if self.state[0] == 3:
                    self.report({"INFO"}, "Preparing render preview...")
                    self.processes[1] = getFrames(self.projectName, True)
                    self.state[1] = 4
                elif self.state[0] < 3:
                    self.report({"WARNING"}, "Files are still transferring - try again in a moment")


            if event.type == "TIMER":
                numIters = 1
                if self.processes[1]:
                    numIters += 1
                for i in range(numIters):
                    self.processes[i].poll()

                    if self.processes[i].returncode != None:
                        # handle rsync error of no output files found on server
                        if self.state[i] in [4, 5] and self.processes[i].returncode == 23:
                            if i == 1 and not self.previewed:
                                self.report({"WARNING"}, "No render files found - try again in a moment")
                                self.processes[1] = False
                                self.state[1] = -1
                                break
                            elif self.renderCancelled and not self.previewed:
                                self.report({"INFO"}, "Process cancelled - No output images found on host server")
                                setRenderStatus("image", "Cancelled")
                                self.cancel(context)
                                return{"CANCELLED"}
                            elif not self.previewed:
                                self.report({"INFO"}, "No render files found on host server")
                                return{"FINISHED"}
                            else:
                                pass
                        # handle network connection error for checking status
                        elif i == 1 and self.processes[i].returncode == 12 and self.state[i] == 4:
                            self.report({"WARNING"}, "Network connection error")
                            self.processes[1] = False
                            self.state[1] = -1
                            break
                        # handle python not found on host error
                        elif self.processes[i].returncode == 127 and self.state[i] == 3:
                            self.report({"ERROR"}, "python and/or rsync not installed on host server")
                            setRenderStatus("image", "ERROR")
                            self.cancel(context)
                            return{"CANCELLED"}
                        # handle unidentified errors
                        elif self.processes[i].returncode > 1:
                            setRenderStatus("image", "ERROR")
                            self.errorSource = "Processes[{i}] at state {state}".format(i=i, state=str(self.state[i])) if self.state[i] != 3 else "blender_task"
                            handleError(self, self.errorSource, i)
                            setRenderStatus("image", "ERROR")
                            self.cancel(context)
                            return{"CANCELLED"}

                        # handle and report errors for 'blender_task' process
                        elif self.processes[i].returncode == 1 and self.state[i] == 3:
                            handleBTError(self, i)

                        # if no errors, print process finished!
                        # print("Process {curState} finished! (return code: {returnCode})".format(curState=str(self.state[i]-1), returnCode=str(self.processes[i].returncode)))

                        # copy files to host server
                        if self.state[i] == 1:
                            self.processes[i] = copyFiles()
                            self.state[i] += 1
                            return{"PASS_THROUGH"}

                        # start render process at current frame
                        elif self.state[i] == 2:
                            bpy.props.rfc_needsUpdating = False
                            jobsPerFrame = scn.rfc_maxSamples // self.sampleSize
                            self.processes[i] = renderFrames(str([scn.rfc_imFrame]), self.projectName, jobsPerFrame)
                            self.state[i] += 1
                            setRenderStatus("image", "Rendering...")
                            return{"PASS_THROUGH"}

                        # get rendered frames from remote servers and archive old render files
                        elif self.state[i] == 3:
                            if self.processes[1] and self.processes[1].returncode == None:
                                self.processes[1].kill()
                            self.state[i] += 1
                            self.processes[0] = getFrames(self.projectName, True)
                            if not self.renderCancelled:
                                setRenderStatus("image", "Finishing...")
                            return{"PASS_THROUGH"}

                        # average the rendered frames if there are new frames to average
                        elif self.state[i] == 4:
                            # only average if there are new frames to average
                            numRenderedFiles = getNumRenderedFiles("image", [scn.rfc_imFrame], None)
                            if numRenderedFiles > 0:
                                averaged = True
                                aveName = averageFrames(self, scn.rfc_nameImOutputFiles)
                                if aveName != None:
                                    scn.rfc_nameAveragedImage = aveName
                                else:
                                    averaged = False
                            else:
                                averaged = False
                            # calculate number of samples represented in averaged image
                            self.numSamples = self.sampleSize * self.avDict["numFrames"]
                            if i == 0:
                                setRenderStatus("image", "Complete!")
                                if bpy.data.images.find(scn.rfc_nameAveragedImage) >= 0:
                                    # open rendered image in any open 'IMAGE_EDITOR' windows
                                    for area in context.screen.areas:
                                        if area.type == "IMAGE_EDITOR":
                                            area.spaces.active.image = bpy.data.images[scn.rfc_nameAveragedImage]
                                            break
                                self.report({"INFO"}, "Render completed at {num} samples! View the rendered image in your UV/Image_Editor".format(num=str(self.numSamples)))
                            elif self.numSamples == 0:
                                self.report({"INFO"}, "No render preview available (0 samples)")
                                self.previewed = True
                                self.processes[1] = False
                            else:
                                if bpy.data.images.find(scn.rfc_nameAveragedImage) >= 0:
                                    # open preview image in UV/Image_Editor
                                    changeContext(context, "IMAGE_EDITOR")
                                    for area in context.screen.areas:
                                        if area.type == "IMAGE_EDITOR":
                                            area.spaces.active.image = bpy.data.images[scn.rfc_nameAveragedImage]
                                            self.previewed = True
                                            break
                                self.processes[1] = False
                                previewString = "Render preview loaded ({num} samples)".format(num=str(self.numSamples))
                                self.report({"INFO"}, previewString)
                            scn.rfc_imagePreviewAvailable = True
                            if i == 0:
                                if self.renderCancelled:
                                    setRenderStatus("image", "Cancelled")
                                    self.cancel(context)
                                    return{"CANCELLED"}
                                else:
                                    return{"FINISHED"}
                        else:
                            self.report({"ERROR"}, "ERROR: Current state not recognized.")
                            setRenderStatus("image", "ERROR")
                            self.cancel(context)
                            return{"CANCELLED"}

            return{"PASS_THROUGH"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}

    def execute(self, context):
        try:
            scn = context.scene
            if scn.render.engine != "CYCLES":
                self.report({"INFO"}, "Rendering on local machine (switch to cycles to render current frame on remote servers).")
                context.area.type = "IMAGE_EDITOR"
                bpy.ops.render.render(use_viewport=True)
                context.area.spaces.active.image = bpy.data.images["Render Result"]
                return{"FINISHED"}

            # ensure no other render processes are running
            if getRenderStatus("image") in getRunningStatuses() or getRenderStatus("animation") in getRunningStatuses():
                self.report({"WARNING"}, "Render in progress...")
                return{"CANCELLED"}
            elif scn.rfc_availableServers == 0:
                serversRefreshed = refreshServers.refreshServersBlock()
                if not serversRefreshed:
                    self.report({"WARNING"}, "Servers could not be auto-refreshed. Try manual refreshing (Ctrl R).")
                    return{"CANCELLED"}

            # ensure the job won't break the script
            if not jobIsValid("image", self):
                return{"CANCELLED"}

            print("\nRunning sendFrame function...")
            self.state = [1, 0]  # initializes state for modal
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
            scn.rfc_nameImOutputFiles = getNameOutputFiles()

            # create timer for modal
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, context.window)
            wm.modal_handler_add(self)

            setRenderStatus("image", "Preparing files...")
            setRenderStatus("animation", "None")

            return{"RUNNING_MODAL"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}

    def __init__(self):
        scn = bpy.context.scene

        # set the file extension for use with 'open image' button
        scn.rfc_imExtension = scn.render.file_extension

        # Store current sample size for use in computing render results
        self.sampleSize = scn.rfc_samplesPerFrame

        # start initial render process
        self.stdout = None
        self.stderr = None
        self.shift = False
        self.renderCancelled = False
        self.numSuccessFrames = 0
        self.finishedFrames = 0
        self.previewed = False
        self.numSamples = 0
        self.avDict = {"array":False, "numFrames":0}
        self.averageIm = None
        scn.rfc_imFrame = scn.frame_current
        self.projectName = bashSafeName(bpy.path.display_name_from_filepath(bpy.data.filepath))

        # for testing purposes only (saves unsaved file)
        if self.projectName == "":
            self.projectName = "rf_unsaved_file"


    def cancel(self, context):
        print("process cancelled")
        cleanupCancelledRender(self, context, bpy.types.Scene.rfc_killPython)
