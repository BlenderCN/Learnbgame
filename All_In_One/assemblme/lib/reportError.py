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
import addon_utils
from bpy.props import StringProperty

# Addon imports
from ..functions import *

# define addon name (must match name in bl_info, replace spaces with underscores)
addon_name = "AssemblMe"

class SCENE_OT_report_error(bpy.types.Operator):
    """Report a bug via an automatically generated issue ticket"""              # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "{}.report_error".format(addon_name.lower().replace(" ", "_"))  # unique identifier for buttons and menu items to reference.
    bl_label = "Report Error"                                                   # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    def execute(self, context):
        # set up file paths
        libraryServersPath = os.path.join(get_addon_directory(), "error_log", self.txt_name)
        # write necessary debugging information to text file
        writeErrorToFile(libraryServersPath, bpy.data.texts[addon_name + " log"].as_string(), str(self.version)[1:-1], self.github_path)
        # open error report in UI with text editor
        lastType = changeContext(context, "TEXT_EDITOR")
        try:
            bpy.ops.text.open(filepath=libraryServersPath)
            bpy.context.space_data.show_word_wrap = True
            self.report({"INFO"}, "Opened '{txt_name}'".format(txt_name=self.txt_name))
            bpy.props.needsUpdating = True
        except:
            changeContext(context, lastType)
            self.report({"ERROR"}, "ERROR: Could not open '{txt_name}'. If the problem persists, try reinstalling the add-on.".format(txt_name=self.txt_name))
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        # get version and github_path
        for mod in addon_utils.modules():
            if mod.bl_info.get("name", "") == addon_name:
                self.version = mod.bl_info.get("version", "")
                self.github_path = mod.bl_info.get("tracker_url", "")
                break
        self.txt_name = addon_name + "_error_report.txt"

    #############################################

class SCENE_OT_close_report_error(bpy.types.Operator):
    """Deletes error report from blender's memory (still exists in file system)""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "{}.close_report_error".format(addon_name.lower().replace(" ", "_")) # unique identifier for buttons and menu items to reference.
    bl_label = "Close Report Error"                                             # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    def execute(self, context):
        txt = bpy.data.texts[addon_name + " log"]
        bpy.data.texts.remove(txt, do_unlink=True)
        return{"FINISHED"}

    #############################################
