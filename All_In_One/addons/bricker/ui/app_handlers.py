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
from bpy.app.handlers import persistent
from mathutils import Vector, Euler

# Addon imports
from ..functions import *
from ..lib.bricksDict import lightToDeepCache, deepToLightCache, getDictKey
from ..lib.caches import bricker_bfm_cache
from ..buttons.customize.tools import *
from ..buttons.customize.undo_stack import *


def brickerRunningBlockingOp():
    wm = bpy.context.window_manager
    return hasattr(wm, "Bricker_runningBlockingOperation") and wm.Bricker_runningBlockingOperation


@persistent
def handle_animation(scn):
    for i, cm in enumerate(scn.cmlist):
        if not cm.animated:
            continue
        n = getSourceName(cm)
        for cf in range(cm.lastStartFrame, cm.lastStopFrame + 1):
            curBricks = bpy_collections().get("Bricker_%(n)s_bricks_f_%(cf)s" % locals())
            if curBricks is None:
                continue
            adjusted_frame_current = getAnimAdjustedFrame(scn.frame_current, cm.lastStartFrame, cm.lastStopFrame)
            onCurF = adjusted_frame_current == cf
            if b280():
                # hide bricks from view and render unless on current frame
                if curBricks.hide_render == onCurF:
                    curBricks.hide_render = not onCurF
                if curBricks.hide_viewport == onCurF:
                    curBricks.hide_viewport = not onCurF
                if hasattr(bpy.context, "active_object"):
                    obj = bpy.context.active_object
                    if obj and obj.name.startswith("Bricker_%(n)s_bricks" % locals()) and onCurF:
                        select(curBricks.objects, active=True)
            else:
                for brick in curBricks.objects:
                    # hide bricks from view and render unless on current frame
                    if onCurF:
                        unhide(brick)
                    else:
                        hide(brick)
                    if hasattr(bpy.context, "active_object") and bpy.context.active_object and bpy.context.active_object.name.startswith("Bricker_%(n)s_bricks" % locals()) and onCurF:
                        select(brick, active=True)
                    # prevent bricks from being selected on frame change
                    else:
                        deselect(brick)


@blender_version_wrapper('<=','2.79')
def isObjVisible(scn, cm, n):
    objVisible = False
    if cm.modelCreated or cm.animated:
        g = bpy_collections().get("Bricker_%(n)s_bricks" % locals())
        if g is not None and len(g.objects) > 0:
            obj = g.objects[0]
        else:
            obj = None
    else:
        obj = cm.source_obj
    if obj:
        objVisible = False
        for i in range(20):
            if obj.layers[i] and scn.layers[i]:
                objVisible = True
    return objVisible, obj


def find_3dview_space():
    # Find 3D_View window and its scren space
    area = None
    for a in bpy.data.window_managers[0].windows[0].screen.areas:
        if a.type == 'VIEW_3D':
            area = a
            break

    if area:
        space = area.spaces[0]
    else:
        space = bpy.context.space_data

    return space


# clear light cache before file load
@persistent
def clear_bfm_cache(dummy):
    for key in bricker_bfm_cache.keys():
        bricker_bfm_cache[key] = None


# pull dicts from deep cache to light cache on load
@persistent
def reset_undo_stack(scene):
    # reset undo stack
    undo_stack = UndoStack.get_instance(reset=True)


@persistent
def handle_loading_to_light_cache(dummy):
    deepToLightCache(bricker_bfm_cache)
    # verify caches loaded properly
    for scn in bpy.data.scenes:
        for cm in scn.cmlist:
            if not (cm.modelCreated or cm.animated):
                continue
            # reset undo states
            cm.blender_undo_state = 0
            python_undo_state[cm.id] = 0
            # load bricksDict
            bricksDict = getBricksDict(cm)
            if bricksDict is None:
                cm.matrixLost = True
                cm.matrixIsDirty = True


# push dicts from light cache to deep cache on save
@persistent
def handle_storing_to_deep_cache(dummy):
    lightToDeepCache(bricker_bfm_cache)


# send parent object to scene for linking scene in other file
@persistent
def safe_link_parent(dummy):
    for scn in bpy.data.scenes:
        for cm in scn.cmlist:
            if cm.parent_obj is not None and (cm.modelCreated or cm.animated) and not cm.exposeParent:
                safeLink(cm.parent_obj)


# send parent object to scene for linking scene in other file
@persistent
def safe_unlink_parent(dummy):
    for scn in bpy.data.scenes:
        for cm in scn.cmlist:
            p = cm.parent_obj
            if p is not None and (cm.modelCreated or cm.animated) and not cm.exposeParent:
                safeUnlink(p)


# @persistent
# def undo_bricksDict_changes(scene):
#     scn = bpy.context.scene
#     if scn.cmlist_index == -1:
#         return
#     undo_stack = UndoStack.get_instance()
#     global python_undo_state
#     cm = scn.cmlist[scn.cmlist_index]
#     if cm.id not in python_undo_state:
#         python_undo_state[cm.id] = 0
#     # handle undo
#     if python_undo_state[cm.id] > cm.blender_undo_state:
#         self.undo_stack.undo_pop()
#
#
# bpy.app.handlers.undo_pre.append(undo_bricksDict_changes)
#
#
# @persistent
# def redo_bricksDict_changes(scene):
#     scn = bpy.context.scene
#     if scn.cmlist_index == -1:
#         return
#     undo_stack = UndoStack.get_instance()
#     global python_undo_state
#     cm = scn.cmlist[scn.cmlist_index]
#     if cm.id not in python_undo_state:
#         python_undo_state[cm.id] = 0
#     # handle redo
#     elif python_undo_state[cm.id] < cm.blender_undo_state:
#         self.undo_stack.redo_pop()
#
#
# bpy.app.handlers.redo_pre.append(redo_bricksDict_changes)


@persistent
def handle_upconversion(dummy):
    # remove storage scene
    sto_scn = bpy.data.scenes.get("Bricker_storage (DO NOT MODIFY)")
    if sto_scn is not None:
        for obj in sto_scn.objects:
            obj.use_fake_user = True
        bpy.data.scenes.remove(sto_scn)
    for scn in bpy.data.scenes:
        # update cmlist indices to reflect updates to Bricker
        for cm in scn.cmlist:
            if createdWithUnsupportedVersion(cm):
                # normalize cm.version
                cm.version = cm.version.replace(", ", ".")
                # convert from v1_0 to v1_1
                if int(cm.version[2]) < 1:
                    cm.brickWidth = 2 if cm.maxBrickScale2 > 1 else 1
                    cm.brickDepth = cm.maxBrickScale2
                # convert from v1_2 to v1_3
                if int(cm.version[2]) < 3:
                    if cm.colorSnapAmount == 0:
                        cm.colorSnapAmount = 0.001
                    for obj in bpy.data.objects:
                        if obj.name.startswith("Rebrickr"):
                            obj.name = obj.name.replace("Rebrickr", "Bricker")
                    for scn in bpy.data.scenes:
                        if scn.name.startswith("Rebrickr"):
                            scn.name = scn.name.replace("Rebrickr", "Bricker")
                    for coll in bpy_collections():
                        if coll.name.startswith("Rebrickr"):
                            coll.name = coll.name.replace("Rebrickr", "Bricker")
                # convert from v1_3 to v1_4
                if int(cm.version[2]) < 4:
                    # update "_frame_" to "_f_" in brick and group names
                    n = cm.source_name
                    Bricker_bricks_cn = "Bricker_%(n)s_bricks" % locals()
                    if cm.animated:
                        for i in range(cm.lastStartFrame, cm.lastStopFrame + 1):
                            Bricker_bricks_curF_cn = Bricker_bricks_cn + "_frame_" + str(i)
                            bColl = bpy_collections().get(Bricker_bricks_curF_cn)
                            if bColl is not None:
                                bColl.name = rreplace(bColl.name, "frame", "f")
                                for obj in bColl.objects:
                                    obj.name = rreplace(obj.name, "combined_frame" if "combined_frame" in obj.name else "frame", "f")
                    elif cm.modelCreated:
                        bColl = bpy_collections().get(Bricker_bricks_cn)
                        if bColl is not None:
                            for obj in bColl.objects:
                                if obj.name.endswith("_combined"):
                                    obj.name = obj.name[:-9]
                    # remove old storage scene
                    sto_scn_old = bpy.data.scenes.get("Bricker_storage (DO NOT RENAME)")
                    if sto_scn_old is not None:
                        for obj in sto_scn_old.objects:
                            if obj.name.startswith("Bricker_refLogo"):
                                bpy.data.objects.remove(obj, do_unlink=True)
                            else:
                                obj.use_fake_user = True
                        bpy.data.scenes.remove(sto_scn_old)
                    # create "Bricker_cm.id_mats" object for each cmlist idx
                    createMatObjs(cm.id)
                    # update names of Bricker source objects
                    old_source = bpy.data.objects.get(cm.source_name + " (DO NOT RENAME)")
                    if old_source is not None:
                        old_source.name = cm.source_name
                    # transfer dist offset values to new prop locations
                    if cm.distOffsetX != -1:
                        cm.distOffset = (cm.distOffsetX, cm.distOffsetY, cm.distOffsetZ)
                # convert from v1_4 to v1_5
                if int(cm.version[2]) < 5:
                    cm.logoType = cm.logoDetail
                    cm.matrixIsDirty = True
                    cm.matrixLost = True
                    remove_colls = list()
                    for coll in bpy_collections():
                        if coll.name.startswith("Bricker_") and (coll.name.endswith("_parent") or coll.name.endswith("_dupes")):
                            remove_colls.append(coll)
                    for coll in remove_colls:
                        bpy_collections().remove(coll)
                # convert from v1_5 to v1_6
                if int(cm.version[2]) < 6:
                    for cm in scn.cmlist:
                        cm.zStep = getZStep(cm)
                    if cm.source_obj is None: cm.source_obj = bpy.data.objects.get(cm.source_name)
                    if cm.parent_obj is None: cm.parent_obj = bpy.data.objects.get(cm.parent_name)
                    n = getSourceName(cm)
                    if cm.animated:
                        coll = BRICKER_OT_brickify.finishAnimation(cm)
                    else:
                        coll = bpy_collections().get("Bricker_%(n)s_bricks" % locals())
                    if cm.collection is None: cm.collection = coll
                    dup = bpy.data.objects.get(n + "_duplicate")
                    if dup is not None: dup.name = n + "__dup__"
            # ensure parent object has no users
            if cm.parent_obj is not None:
                # TODO: replace with this line when the function is fixed in 2.8
                cm.parent_obj.user_clear()
                cm.parent_obj.use_fake_user = True
                # for coll in cm.parent_obj.users_collection:
                #     coll.objects.unlink(cm.parent_obj)
