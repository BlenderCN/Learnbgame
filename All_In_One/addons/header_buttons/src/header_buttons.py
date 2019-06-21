#----------------------------------------------------------------------
# header_buttons.py
#----------------------------------------------------------------------
# This file contains the generated PrintHello Operators 
# alongside with the add_header methods that adds each operator
# to the layout.  
#----------------------------------------------------------------------
# File generated on 2017-12-26 00:29:13
#----------------------------------------------------------------------

import bpy
import os
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                        )

#----------------------------------------------------
# Use console_writing in case its addon is installed
#          Otherwise print to the terminal
#----------------------------------------------------
try:
    from console_scripts.utils import console_writer
    console_script_is_installed=True
except ImportError:
    print("console_scripts addon wasn't found, ensure correct name of the addon if it's registered!")
    console_script_is_installed=False

def custom_print(str):
    if "console_write_operator" in dir(bpy.ops.console)
        # the exposed Blender operator
        # case of console_scripts registered
        bpy.ops.console.console_write_operator(myString=str)
    elif console_script_is_installed==True:
        # the python method
        # case of console_scripts existent but not registered
        # or console_scripts has just been removed
        console_writer.console_write(str)
    else:
        print(str)

# To support different operator labels we create a PrintHello operator per space


class PrintHello_VIEW_3D(Operator):
    bl_idname = "wm.printhello1"
    bl_label = "Print Hello from VIEW_3D"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_TIMELINE(Operator):
    bl_idname = "wm.printhello2"
    bl_label = "Print Hello from TIMELINE"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_GRAPH_EDITOR(Operator):
    bl_idname = "wm.printhello3"
    bl_label = "Print Hello from GRAPH_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_DOPESHEET_EDITOR(Operator):
    bl_idname = "wm.printhello4"
    bl_label = "Print Hello from DOPESHEET_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_NLA_EDITOR(Operator):
    bl_idname = "wm.printhello5"
    bl_label = "Print Hello from NLA_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_IMAGE_EDITOR(Operator):
    bl_idname = "wm.printhello6"
    bl_label = "Print Hello from IMAGE_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_SEQUENCE_EDITOR(Operator):
    bl_idname = "wm.printhello7"
    bl_label = "Print Hello from SEQUENCE_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_CLIP_EDITOR(Operator):
    bl_idname = "wm.printhello8"
    bl_label = "Print Hello from CLIP_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_TEXT_EDITOR(Operator):
    bl_idname = "wm.printhello9"
    bl_label = "Print Hello from TEXT_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_NODE_EDITOR(Operator):
    bl_idname = "wm.printhello10"
    bl_label = "Print Hello from NODE_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_LOGIC_EDITOR(Operator):
    bl_idname = "wm.printhello11"
    bl_label = "Print Hello from LOGIC_EDITOR"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_PROPERTIES(Operator):
    bl_idname = "wm.printhello12"
    bl_label = "Print Hello from PROPERTIES"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_OUTLINER(Operator):
    bl_idname = "wm.printhello13"
    bl_label = "Print Hello from OUTLINER"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_USER_PREFERENCES(Operator):
    bl_idname = "wm.printhello14"
    bl_label = "Print Hello from USER_PREFERENCES"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_INFO(Operator):
    bl_idname = "wm.printhello15"
    bl_label = "Print Hello from INFO"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_FILE_BROWSER(Operator):
    bl_idname = "wm.printhello16"
    bl_label = "Print Hello from FILE_BROWSER"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}


class PrintHello_CONSOLE(Operator):
    bl_idname = "wm.printhello17"
    bl_label = "Print Hello from CONSOLE"

    def execute(self, context):
        custom_print("{space: " + GetSpace(context) + ", region: HEADER}")
        return {'FINISHED'}

def GetSpaceAndRegion(context):
    return "{space: " + GetSpace(context) + ", region: " + GetRegion(context) + "}"

def GetSpace(context):
    return context.space_data.type

# the context will return the default region rather than the region of the object, which we'll need to always overwrite ourselves except when working with the properties editor, as the "window" region will be the default & only-useable region.
def GetRegion(context):
    return context.region.type

# PrintHello operator per space
def add_to_header_1(self, context):
    self.layout.operator("wm.printhello1", icon = "PLUGIN")

def add_to_header_2(self, context):
    self.layout.operator("wm.printhello2", icon = "PLUGIN")

def add_to_header_3(self, context):
    self.layout.operator("wm.printhello3", icon = "PLUGIN")

def add_to_header_4(self, context):
    self.layout.operator("wm.printhello4", icon = "PLUGIN")

def add_to_header_5(self, context):
    self.layout.operator("wm.printhello5", icon = "PLUGIN")

def add_to_header_6(self, context):
    self.layout.operator("wm.printhello6", icon = "PLUGIN")

def add_to_header_7(self, context):
    self.layout.operator("wm.printhello7", icon = "PLUGIN")

def add_to_header_8(self, context):
    self.layout.operator("wm.printhello8", icon = "PLUGIN")

def add_to_header_9(self, context):
    self.layout.operator("wm.printhello9", icon = "PLUGIN")

def add_to_header_10(self, context):
    self.layout.operator("wm.printhello10", icon = "PLUGIN")

def add_to_header_11(self, context):
    self.layout.operator("wm.printhello11", icon = "PLUGIN")

def add_to_header_12(self, context):
    self.layout.operator("wm.printhello12", icon = "PLUGIN")

def add_to_header_13(self, context):
    self.layout.operator("wm.printhello13", icon = "PLUGIN")

def add_to_header_14(self, context):
    self.layout.operator("wm.printhello14", icon = "PLUGIN")

def add_to_header_15(self, context):
    self.layout.operator("wm.printhello15", icon = "PLUGIN")

def add_to_header_16(self, context):
    self.layout.operator("wm.printhello16", icon = "PLUGIN")

def add_to_header_17(self, context):
    self.layout.operator("wm.printhello17", icon = "PLUGIN")


