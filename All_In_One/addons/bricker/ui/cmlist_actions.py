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
from bpy.props import *
from bpy.types import UIList

# Addon imports
from ..functions import *
from .cmlist_utils import *


# ui list item actions
class CMLIST_OT_list_action(bpy.types.Operator):
    bl_idname = "cmlist.list_action"
    bl_label = "Brick Model List Action"

    ################################################
    # Blender Operator methods

    # @classmethod
    # def poll(self, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     scn = context.scene
    #     for cm in scn.cmlist:
    #         if cm.animated:
    #             return False
    #     return True

    def execute(self, context):
        try:
            scn = context.scene
            idx = scn.cmlist_index

            try:
                item = scn.cmlist[idx]
            except IndexError:
                pass

            if self.action == 'REMOVE' and len(scn.cmlist) > 0 and scn.cmlist_index >= 0:
                bpy.ops.ed.undo_push(message="Bricker: Remove Item")
                self.removeItem(idx)

            elif self.action == 'ADD':
                bpy.ops.ed.undo_push(message="Bricker: Remove Item")
                self.addItem()

            elif self.action == 'DOWN' and idx < len(scn.cmlist) - 1:
                self.moveDown(item)

            elif self.action == 'UP' and idx >= 1:
                self.moveUp(item)
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    ###################################################
    # class variables

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    #############################################
    # class methods

    @staticmethod
    def addItem():
        scn = bpy.context.scene
        active_object = bpy.context.active_object
        # if active object isn't on visible layer, don't set it as default source for new model
        if b280():
            if active_object and not isObjVisibleInViewport(active_object):
                active_object = None
        else:
            if active_object:
                objVisible = False
                for i in range(20):
                    if active_object.layers[i] and scn.layers[i]:
                        objVisible = True
                if not objVisible:
                    active_object = None
        # if active object already has a model or isn't on visible layer, don't set it as default source for new model
        # NOTE: active object may have been removed, so we need to re-check if none
        if active_object:
            for cm in scn.cmlist:
                if cm.source_obj is active_object:
                    active_object = None
                    break
        item = scn.cmlist.add()
        last_index = scn.cmlist_index
        scn.cmlist_index = len(scn.cmlist)-1
        if active_object and active_object.type == "MESH" and not active_object.name.startswith("Bricker_"):
            item.source_obj = active_object
            item.name = active_object.name
            item.version = bpy.props.bricker_version
            # get Bricker preferences
            prefs = get_addon_preferences()
            if prefs.brickHeightDefault == "ABSOLUTE":
                # set absolute brick height
                item.brickHeight = prefs.absoluteBrickHeight
            else:
                # set brick height based on model height
                source = item.source_obj
                if source:
                    source_details = bounds(source, use_adaptive_domain=False)
                    h = max(source_details.dist)
                    item.brickHeight = h / prefs.relativeBrickHeight

        else:
            item.source_obj = None
            item.name = "<New Model>"
        # get all existing IDs
        existingIDs = [cm.id for cm in scn.cmlist]
        i = max(existingIDs) + 1
        # protect against massive item IDs
        if i > 9999:
            i = 1
            while i in existingIDs:
                i += 1
        # set item ID to unique number
        item.id = i
        item.idx = len(scn.cmlist)-1
        item.startFrame = scn.frame_start
        item.stopFrame = scn.frame_end
        # create new matObj for current cmlist id
        createMatObjs(i)

    def removeItem(cls, idx):
        scn, cm, sn = getActiveContextInfo()
        n = cm.name
        if not cm.modelCreated and not cm.animated:
            for idx0 in range(idx + 1, len(scn.cmlist)):
                scn.cmlist[idx0].idx -= 1
            if len(scn.cmlist) - 1 == scn.cmlist_index:
                scn.cmlist_index -= 1
            # remove matObj for current cmlist id
            removeMatObjs(cm.id)
            scn.cmlist.remove(idx)
            if scn.cmlist_index == -1 and len(scn.cmlist) > 0:
                scn.cmlist_index = 0
        else:
            cls.report({"WARNING"}, 'Please delete the Brickified model before attempting to remove this item.' % locals())

    def moveDown(self, item):
        scn = bpy.context.scene
        scn.cmlist.move(scn.cmlist_index, scn.cmlist_index+1)
        scn.cmlist_index += 1
        self.updateIdxs(scn.cmlist)

    def moveUp(self, item):
        scn = bpy.context.scene
        scn.cmlist.move(scn.cmlist_index, scn.cmlist_index-1)
        scn.cmlist_index -= 1
        self.updateIdxs(scn.cmlist)

    def updateIdxs(self, cmlist):
        for i,cm in enumerate(cmlist):
            cm.idx = i

    #############################################


# copy settings from current index to all other indices
class CMLIST_OT_copy_settings_to_others(bpy.types.Operator):
    bl_idname = "cmlist.copy_settings_to_others"
    bl_label = "Copy Settings to Other Brick Models"
    bl_description = "Copies the settings from the current model to all other Brick Models"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.cmlist_index == -1:
            return False
        if len(scn.cmlist) == 1:
            return False
        return True

    def execute(self, context):
        try:
            scn, cm0, _ = getActiveContextInfo()
            for cm1 in scn.cmlist:
                if cm0 != cm1:
                    matchProperties(cm1, cm0, overrideIdx=cm1.idx)
        except:
            bricker_handle_exception()
        return{'FINISHED'}


# copy settings from current index to memory
class CMLIST_OT_copy_settings(bpy.types.Operator):
    bl_idname = "cmlist.copy_settings"
    bl_label = "Copy Settings from Current Brick Model"
    bl_description = "Stores the ID of the current model for pasting"

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.cmlist_index == -1:
            return False
        return True

    def execute(self, context):
        try:
            scn, cm, _ = getActiveContextInfo()
            scn.Bricker_copy_from_id = cm.id
        except:
            bricker_handle_exception()
        return{'FINISHED'}


# paste settings from index in memory to current index
class CMLIST_OT_paste_settings(bpy.types.Operator):
    bl_idname = "cmlist.paste_settings"
    bl_label = "Paste Settings to Current Brick Model"
    bl_description = "Pastes the settings from stored model ID to the current index"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.cmlist_index == -1:
            return False
        return True

    def execute(self, context):
        try:
            scn, cm0, _ = getActiveContextInfo()
            for cm1 in scn.cmlist:
                if cm0 != cm1 and cm1.id == scn.Bricker_copy_from_id:
                    matchProperties(cm0, cm1)
                    break
        except:
            bricker_handle_exception()
        return{'FINISHED'}


# select bricks from current model
class CMLIST_OT_select_bricks(bpy.types.Operator):
    bl_idname = "cmlist.select_bricks"
    bl_label = "Select All Bricks in Current Brick Model"
    bl_description = "Select all bricks in the current model"

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.cmlist_index == -1:
            return False
        cm = scn.cmlist[scn.cmlist_index]
        return cm.animated or cm.modelCreated

    deselect = BoolProperty(default=False)

    def execute(self, context):
        try:
            if self.deselect:
                deselect(self.bricks)
            else:
                select(self.bricks)
        except:
            bricker_handle_exception()
        return{'FINISHED'}

    def __init__(self):
        self.bricks = getBricks()


# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

class CMLIST_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        split = layout_split(layout, align=False, factor=0.9)
        split.prop(item, "name", text="", emboss=False, translate=False, icon='MOD_REMESH')

    def invoke(self, context, event):
        pass
