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

class openRenderedImageInUI(Operator):
    """Open rendered image"""                                                   # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render_farm.open_rendered_image"                                     # unique identifier for buttons and menu items to reference.
    bl_label = "Open Rendered Image"                                            # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    def execute(self, context):
        scn = bpy.context.scene
        try:
            if bpy.data.images.find(scn.rfc_nameAveragedImage) >= 0:
                # open rendered image in UV/Image_Editor
                changeContext(context, "IMAGE_EDITOR")
                for area in context.screen.areas:
                    if area.type == "IMAGE_EDITOR":
                        area.spaces.active.image = bpy.data.images[scn.rfc_nameAveragedImage]
            elif scn.rfc_nameAveragedImage != "":
                self.report({"ERROR"}, "Image could not be found: '{nameAveragedImage}'".format(nameAveragedImage=scn.rfc_nameAveragedImage))
                return{"CANCELLED"}
            else:
                self.report({"WARNING"}, "No rendered images could be found")
                return{"CANCELLED"}

            return{"FINISHED"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}


class openRenderedAnimationInUI(Operator):
    """Open rendered animation"""                                               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "render_farm.open_rendered_animation"                                 # unique identifier for buttons and menu items to reference.
    bl_label = "Open Rendered Animation"                                        # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.


    def execute(self, context):
        scn = bpy.context.scene
        try:
            # change contexts
            lastAreaType = changeContext(context, "CLIP_EDITOR")
            # opens first frame of image sequence (blender imports full sequence)
            openedFile = False
            for frame in bpy.props.rfc_animFrameRange:
                image_filename = "{fileName}_{frame}{extension}".format(fileName=getNameOutputFiles(), frame=str(frame).zfill(4), extension=scn.rfc_animExtension)
                if os.path.isfile(os.path.join(self.renderDumpFolder, image_filename)):
                    bpy.ops.clip.open(directory=self.renderDumpFolder, files=[{"name":image_filename}])
                    openedFile = image_filename
                    openedFrame = frame
                    break
            if openedFile:
                bpy.ops.clip.reload()
                bpy.data.movieclips[openedFile].frame_start = frame
            else:
                changeContext(context, lastAreaType)
                self.report({"ERROR"}, "Could not open rendered animation. View files in file browser in the following folder: '{path}'.".format(path=self.renderDumpFolder))

            return{"FINISHED"}
        except:
            render_farm_handle_exception()
            return{"CANCELLED"}

    def __init__(self):
        scn = bpy.context.scene
        self.rfc_frameRangesDict = buildFrameRangesString(scn.rfc_frameRanges)
        self.renderDumpFolder = getRenderDumpPath()[0]
