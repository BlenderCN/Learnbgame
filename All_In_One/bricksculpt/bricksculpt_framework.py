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

# System imports
# NONE!

# Blender imports
import bpy
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

# Addon imports
from ....lib.bricksDict.functions import *
from ....functions.common.blender import *


def get_quadview_index(context, x, y):
    for area in context.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        is_quadview = len(area.spaces.active.region_quadviews) == 0
        i = -1
        for region in area.regions:
            if region.type == 'WINDOW':
                i += 1
                if (x >= region.x and
                    y >= region.y and
                    x < region.width + region.x and
                    y < region.height + region.y):

                    return (area.spaces.active, None if is_quadview else i)
    return (None, None)


class bricksculpt_framework:
    """ modal framework for the paintbrush tool """

    ################################################
    # Blender Operator methods

    def modal(self, context, event):
        try:
            # commit changes on 'ret' key press
            if (event.type == "RET" or (event.type == "ESC" and self.layerSolod is None)) and event.value == "PRESS":
                bpy.context.window.cursor_set("DEFAULT")
                self.cancel(context)
                self.commitChanges()
                return{"FINISHED"}

            # block undo action
            if event.type == "Z" and (event.ctrl or event.oskey):
                return {"RUNNING_MODAL"}

            # switch mode
            if not self.left_click and event.value == "PRESS":
                if event.type == "D" and self.mode != "DRAW":
                    self.mode = "DRAW"
                    self.addedBricks = []
                    tag_redraw_areas("VIEW_3D")
                elif event.type == "M" and self.mode != "MERGE/SPLIT":
                    self.mode = "MERGE/SPLIT"
                    self.addedBricks = []
                    tag_redraw_areas("VIEW_3D")
                elif event.type == "P" and self.mode != "PAINT":
                    self.mode = "PAINT"
                    tag_redraw_areas("VIEW_3D")

            # check if function key pressed
            if event.type in ("LEFT_CTRL", "RIGHT_CTRL") and event.value == "PRESS":
                if self.layerSolod is not None:
                    self.ctrlClickTime = time.time()
                    self.possibleCtrlDisable = True
                    return {"RUNNING_MODAL"}
                else:
                    self.layerSolod = -1
            # if mouse moves, don't disable solo layer
            if event.type == "MOUSEMOVE":
                self.possibleCtrlDisable = False
            # clear solo layer if escape/quick ctrl pressed
            if (self.layerSolod is not None and
                ((event.type == "ESC" and event.value == "PRESS") or
                 (event.type in ("LEFT_CTRL", "RIGHT_CTRL") and event.value == "RELEASE" and (time.time() - self.ctrlClickTime < 0.2)))):
                self.unSoloLayer()
                self.layerSolod = None
                self.possibleCtrlDisable = False
                return {"RUNNING_MODAL"}

            # check if left_click is pressed
            if event.type == "LEFTMOUSE":
                if event.value == "PRESS":
                    self.left_click = True
                    # block left_click if not in 3D viewport
                    space, i = get_quadview_index(context, event.mouse_x, event.mouse_y)
                    if space is None:
                        return {"RUNNING_MODAL"}
                elif event.value == "RELEASE":
                    self.left_click = False
                    self.releaseTime = time.time()
                    # clear bricks added from delete's auto update
                    self.addedBricksFromDelete = []

            # cast ray to calculate mouse position and travel
            if event.type in ('MOUSEMOVE', 'LEFT_CTRL', 'RIGHT_CTRL') or self.left_click:
                scn, cm, n = getActiveContextInfo()
                self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
                self.mouseTravel = abs(self.mouse.x - self.lastMouse.x) + abs(self.mouse.y - self.lastMouse.y)
                self.hover_scene(context, self.mouse.x, self.mouse.y, n, update_header=self.left_click)
                # self.update_ui_mouse_pos()
                # run solo layer functionality
                if event.ctrl and (not self.left_click or event.type in ("LEFT_CTRL", "RIGHT_CTRL")) and not (self.possibleCtrlDisable and time.time() - self.ctrlClickTime < 0.2) and self.mouseTravel > 10 and time.time() > self.releaseTime + 0.75:
                    if len(self.hiddenBricks) > 0:
                        self.unSoloLayer()
                        self.hover_scene(context, self.mouse.x, self.mouse.y, n, update_header=self.left_click)
                    if self.obj is not None:
                        self.lastMouse = self.mouse
                        curKey = getDictKey(self.obj.name)
                        curLoc = getDictLoc(self.bricksDict, curKey)
                        objSize = self.bricksDict[curKey]["size"]
                        self.layerSolod = self.soloLayer(cm, curKey, curLoc, objSize)
                elif self.obj is None:
                    bpy.context.window.cursor_set("DEFAULT")
                    return {"RUNNING_MODAL"}
                else:
                    bpy.context.window.cursor_set("PAINT_BRUSH")

            # draw/remove bricks on left_click & drag
            if self.left_click and (event.type == 'LEFTMOUSE' or (event.type == "MOUSEMOVE" and (not event.alt or self.mouseTravel > 5))):
                # determine which action (if any) to run at current mouse position
                addBrick = not (event.alt or event.shift or self.obj.name in self.keysToMergeOnRelease) and self.mode == "DRAW"
                removeBrick = self.mode == "DRAW" and (event.alt or event.shift) and self.mouseTravel > 10
                changeMaterial = self.obj.name not in self.addedBricks and self.mode == "PAINT"
                splitBrick = self.mode == "MERGE/SPLIT" and (event.alt or event.shift)
                mergeBrick = self.obj.name not in self.addedBricks and self.mode == "MERGE/SPLIT" and not event.alt
                # get key/loc/size of brick at mouse position
                if addBrick or removeBrick or changeMaterial or splitBrick or mergeBrick:
                    self.lastMouse = self.mouse
                    curKey = getDictKey(self.obj.name)
                    curLoc = getDictLoc(self.bricksDict, curKey)
                    objSize = self.bricksDict[curKey]["size"]
                # add brick next to existing brick
                if addBrick and self.bricksDict[curKey]["name"] not in self.addedBricks:
                    self.addBrick(cm, n, curKey, curLoc, objSize)
                # remove existing brick
                elif removeBrick:
                    self.removeBrick(cm, n, event, curKey, curLoc, objSize)
                # change material
                elif changeMaterial and self.bricksDict[curKey]["mat_name"] != self.matName:
                    self.changeMaterial(cm, n, curKey, curLoc, objSize)
                # split current brick
                elif splitBrick:
                    self.splitBrick(cm, event, curKey, curLoc, objSize)
                # add current brick to 'self.keysToMerge'
                elif mergeBrick:
                    self.mergeBrick(cm, n, curKey, curLoc, objSize, mode=self.mode, state="DRAG")
                return {"RUNNING_MODAL"}

            # clean up after splitting bricks
            if event.type in ("LEFT_ALT", "RIGHT_ALT", "LEFT_SHIFT", "RIGHT_SHIFT") and event.value == "RELEASE" and self.mode == "MERGE/SPLIT":
                deselectAll()

            # merge bricks in 'self.keysToMerge'
            if event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.mode in ("DRAW", "MERGE/SPLIT"):
                scn, cm, n = getActiveContextInfo()
                self.mergeBrick(cm, n, mode=self.mode, state="RELEASE")

            return {"PASS_THROUGH" if event.type.startswith("NUMPAD") or event.type in ("Z", "TRACKPADZOOM", "TRACKPADPAN", "MOUSEMOVE", "NDOF_BUTTON_PANZOOM", "INBETWEEN_MOUSEMOVE", "MOUSEROTATE", "WHEELUPMOUSE", "WHEELDOWNMOUSE", "WHEELINMOUSE", "WHEELOUTMOUSE") else "RUNNING_MODAL"}
        except:
            bpy.context.window.cursor_set("DEFAULT")
            self.cancel(context)
            bricker_handle_exception()
            return {"CANCELLED"}

    ###################################################
    # class variables

    BrickSculptInstalled = True
    BrickSculptLoaded = True

    #############################################
    # class methods

    # from CG Cookie's retopoflow plugin
    def hover_scene(self, context, x, y, source_name, update_header=True):
        """ casts ray through point x,y and sets self.obj if obj intersected """
        scn = context.scene
        self.region = context.region
        self.r3d = context.space_data.region_3d
        # TODO: Use custom view layer with only current model instead?
        if b280(): view_layer = bpy.context.window.view_layer
        rv3d = context.region_data
        if rv3d is None:
            return None
        coord = x, y
        ray_max = 1000000  # changed from 10000 to 1000000 to increase accuracy
        view_vector = region_2d_to_vector_3d(self.region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(self.region, rv3d, coord)
        ray_target = ray_origin + (view_vector * ray_max)

        if b280():
            result, loc, normal, idx, obj, mx = scn.ray_cast(view_layer, ray_origin, ray_target)
        else:
            result, loc, normal, idx, obj, mx = scn.ray_cast(ray_origin, ray_target)

        if result and obj.name.startswith('Bricker_' + source_name):
            self.obj = obj
            self.loc = loc
            self.normal = normal
        else:
            self.obj = None
            self.loc = None
            self.normal = None
            if b280():
                context.area.header_text_set(text=None)
            else:
                context.area.header_text_set()

    def cancel(self, context):
        if b280():
            context.area.header_text_set(text=None)
        else:
            context.area.header_text_set()
        bpy.props.running_bricksculpt_tool = False
        self.ui_end()

    ##########################
