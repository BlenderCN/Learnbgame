# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Matti 'Menithal' Lahtinen

import bpy
import os
import hifi_tools

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
)

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty
)
import hifi_tools.files.fst.writer as FSTWriter
from hifi_tools.utils.bones import find_armatures


class HifiBoneOperator(bpy.types.Operator):
    bl_idname = "hifi_warn.bone_count"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label("Avatar Successfully Exported: ")
        row = layout.row()
        row.label(text="Warning:", icon="QUESTION")
        row = layout.row()
        row.label(
            "You may have issues with the avatars pose not being streamed with")
        row = layout.row()
        row.label("So many bones.")
        row = layout.row()
        row.label("Try combining some if you have issues in HiFi.")


class HifiExportErrorOperator(bpy.types.Operator):
    bl_idname = "hifi_error.export"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Warning:", icon="ERROR")
        row = layout.row()
        row.label("Avatar Export Failed. Please Check the console logs")


class HifiExportErrorNoArmatureOperator(bpy.types.Operator):
    bl_idname = "hifi_error_no_armature.export"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Warning:", icon="ERROR")
        row = layout.row()
        row.label("Avatar Export Failed. Please have 1 armature on selected")


class HifiExportSucccessOperator(bpy.types.Operator):
    bl_idname = "hifi_success.export"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Success:", icon="FILE_TICK")
        row = layout.row()
        row.label("Avatar Export Successful.")


class FSTWriterOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "export_avatar.hifi_fbx_fst"
    bl_label = "Export Hifi Avatar"
    bl_options = {'UNDO'}

    directory = StringProperty()
    filename_ext = ".fst"

    # TODO: instead create a new directory instead of a file.

    filter_glob = StringProperty(default="*.fst", options={'HIDDEN'})
    selected_only = BoolProperty(
        default=False, name="Selected Only", description="Selected Only")

    #anim_graph_url = StringProperty(default="", name="Animation JSON Url",
    #                                description="Avatar Animation JSON absolute url path")

    script = StringProperty(default="", name="Avatar Script Path",
                            description="Avatar Script absolute url path, Script that is run on avatar")

    flow = BoolProperty(default=False, name="Add Flow Script",
                        description="Adds flow script template as an additional Avatar script")

    embed = BoolProperty(default=False, name="Embed Textures",
                         description="Embed Textures to Exported Model. Turn this off if you are having issues of Textures  not showing correctly in elsewhere.")

    bake = BoolProperty(default=False, name="Oven Bake (Experimental)",
                        description="Use the HiFi Oven Tool to bake")

    ipfs = BoolProperty(default=False, name="Yes, Upload to IPFS",
                        description="Upload files to the \n InterPlanetary File System Blockchain via a Gateway")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_only")
       #layout.prop(self, "flow")
        layout.prop(self, "embed")

        oven_tool = context.user_preferences.addons[hifi_tools.__name__].preferences.oventool
        
        #layout.prop(self, "anim_graph_url")
        layout.prop(self, "script")

        enabled_ipfs = len(
            context.user_preferences.addons[hifi_tools.__name__].preferences.gateway_token) > 0

        if (oven_tool is not None and "oven" in oven_tool):
            layout.prop(self, "bake")

        if enabled_ipfs:
            
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row.label(
                text="Warning: Anything you put into the ipfs is public for anyone", icon="ERROR")

            row = layout.row()
            row.label(
                "with the url to see / download and will be impossible to remove after ")

            row = layout.row()
            row.label("being distributed to ipfs, unless links of it are forgotten.")

            row = layout.row()
            row.label("Distribution may take a while. You may need to refresh the page after a few minutes.")

            row = layout.row()
            row.label(
                "Do you want to upload assets to IPFS? ")

            layout.prop(self, "ipfs")
        


    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        preferences = bpy.context.user_preferences.addons[hifi_tools.__name__].preferences

        if self.bake and (preferences.oventool is None or "oven" not in preferences.oventool):
            raise Exception(
                "Please set the oven path for the plugin. eg <pathToHighFidelity>/oven.exe")

        to_export = None

        if self.selected_only:
            to_export = list(bpy.context.selected_objects)
        else:
            to_export = list(bpy.data.objects)

        print(to_export)
        
        self.scale = 1  # Add scene scale here

        armatures = find_armatures(to_export)
        if len(armatures) > 1 or len(armatures) == 0:
            bpy.ops.hifi_error_no_armature.export('INVOKE_DEFAULT')
            return {'CANCELLED'}

        val = FSTWriter.fst_export(self, to_export)

        if val == {'FINISHED'}:
            if len(armatures[0].data.edit_bones) > 100:
                bpy.ops.hifi_warn.bone_count('INVOKE_DEFAULT')
            else:
                bpy.ops.hifi_success.export('INVOKE_DEFAULT')
            return {'FINISHED'}
        else:
            bpy.ops.hifi_error.export('INVOKE_DEFAULT')
            return val
