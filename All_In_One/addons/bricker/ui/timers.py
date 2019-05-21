"""
Copyright (C) 2019 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# System imports
# NONE!

# Blender imports
import bpy
from bpy.app.handlers import persistent

# Addon imports
from .app_handlers import brickerRunningBlockingOp
from ..buttons.customize.undo_stack import *
from ..functions import *
from ..buttons.customize.tools import *
from ..buttons.customize.undo_stack import *


# def isBrickerObjVisible(scn, cm, n):
#     if cm.modelCreated or cm.animated:
#         gn = "Bricker_%(n)s_bricks" % locals()
#         if collExists(gn) and len(bpy.data.collections[gn].objects) > 0:
#             obj = bpy.data.collections[gn].objects[0]
#         else:
#             obj = None
#     else:
#         obj = cm.source_obj
#     objVisible = isObjVisibleInViewport(obj)
#     return objVisible, obj


@persistent
def handle_selections(junk=None):
    if brickerRunningBlockingOp():
        return 0.5
    scn = bpy.context.scene
    obj = bpy.context.view_layer.objects.active if b280() else scn.objects.active
    # TODO: in b280, Check if active object (with active cmlist index) is no longer visible
    # curLayers = str(list(scn.layers))
    # # if scn.layers changes and active object is no longer visible, set scn.cmlist_index to -1
    # if scn.Bricker_last_layers != curLayers:
    #     scn.Bricker_last_layers = curLayers
    #     curObjVisible = False
    #     if scn.cmlist_index != -1:
    #         cm0, n0 = getActiveContextInfo()[1:]
    #         curObjVisible, _ = isObjVisible(scn, cm0, n0)
    #     if not curObjVisible or scn.cmlist_index == -1:
    #         setIndex = False
    #         for i, cm in enumerate(scn.cmlist):
    #             if i != scn.cmlist_index:
    #                 nextObjVisible, obj = isObjVisible(scn, cm, getSourceName(cm))
    #                 if nextObjVisible and hasattr(bpy.context, "active_object") and bpy.context.active_object == obj:
    #                     scn.cmlist_index = i
    #                     setIndex = True
    #                     break
    #         if not setIndex:
    #             scn.cmlist_index = -1
    # if scn.cmlist_index changes, select and make source or Brick Model active
    if scn.Bricker_last_cmlist_index != scn.cmlist_index and scn.cmlist_index != -1:
        scn.Bricker_last_cmlist_index = scn.cmlist_index
        cm, n = getActiveContextInfo()[1:]
        source = cm.source_obj
        if source and cm.version[:3] != "1_0":
            if cm.modelCreated:
                bricks = getBricks()
                if bricks and len(bricks) > 0:
                    select(bricks, active=True, only=True)
                    scn.Bricker_last_active_object_name = obj.name if obj is not None else ""
            elif cm.animated:
                cf = scn.frame_current
                if cf > cm.lastStopFrame:
                    cf = cm.lastStopFrame
                elif cf < cm.lastStartFrame:
                    cf = cm.lastStartFrame
                if b280():
                    cn = "Bricker_%(n)s_bricks_f_%(cf)s" % locals()
                    if len(bpy.data.collections[cn].objects) > 0:
                        select(list(bpy.data.collections[cn].objects), active=True, only=True)
                        scn.Bricker_last_active_object_name = obj.name if obj is not None else ""
                else:
                    g = bpy_collections().get("Bricker_%(n)s_bricks_f_%(cf)s" % locals())
                    if g is not None and len(g.objects) > 0:
                        select(list(g.objects), active=True, only=True)
                        scn.Bricker_last_active_object_name = bpy.context.active_object.name
                    else:
                        scn.objects.active = None
                        deselectAll()
                        scn.Bricker_last_active_object_name = ""
            else:
                select(source, active=True, only=True)
                scn.Bricker_last_active_object_name = source.name
        else:
            for i,cm0 in enumerate(scn.cmlist):
                if getSourceName(cm0) == scn.Bricker_active_object_name:
                    deselectAll()
                    break
    # if active object changes, open Brick Model settings for active object
    elif obj and scn.Bricker_last_active_object_name != obj.name and len(scn.cmlist) > 0 and (scn.cmlist_index == -1 or scn.cmlist[scn.cmlist_index].source_obj is not None) and obj.type == "MESH":
        scn.Bricker_last_active_object_name = obj.name
        beginningString = "Bricker_"
        if obj.name.startswith(beginningString):
            usingSource = False
            frameLoc = obj.name.rfind("_bricks")
            if frameLoc == -1:
                frameLoc = obj.name.rfind("_parent")
                if frameLoc == -1:
                    frameLoc = obj.name.rfind("__")
            if frameLoc != -1:
                scn.Bricker_active_object_name = obj.name[len(beginningString):frameLoc]
        else:
            usingSource = True
            scn.Bricker_active_object_name = obj.name
        for i,cm in enumerate(scn.cmlist):
            if createdWithUnsupportedVersion(cm) or getSourceName(cm) != scn.Bricker_active_object_name or (usingSource and cm.modelCreated):
                continue
            scn.cmlist_index = i
            scn.Bricker_last_cmlist_index = scn.cmlist_index
            if obj.isBrick:
                # adjust scn.active_brick_detail based on active brick
                x0, y0, z0 = strToList(getDictKey(obj.name))
                cm.activeKey = (x0, y0, z0)
            tag_redraw_areas("VIEW_3D")
            return 0.05
        # if no matching cmlist item found, set cmlist_index to -1
        scn.cmlist_index = -1
        tag_redraw_areas("VIEW_3D")
    return 0.05


@blender_version_wrapper('>=','2.80')
def handle_undo_stack():
    scn = bpy.context.scene
    undo_stack = UndoStack.get_instance()
    if hasattr(bpy.props, "bricker_updating_undo_state") and not undo_stack.isUpdating() and not brickerRunningBlockingOp() and scn.cmlist_index != -1:
        global python_undo_state
        cm = scn.cmlist[scn.cmlist_index]
        if cm.id not in python_undo_state:
            python_undo_state[cm.id] = 0
        # handle undo
        elif python_undo_state[cm.id] > cm.blender_undo_state:
            undo_stack.undo_pop()
            tag_redraw_areas("VIEW_3D")
        # handle redo
        elif python_undo_state[cm.id] < cm.blender_undo_state:
            undo_stack.redo_pop()
            tag_redraw_areas("VIEW_3D")
    return 0.02


@persistent
@blender_version_wrapper('>=','2.80')
def register_bricker_timers(scn):
    timer_fns = (handle_selections, handle_undo_stack, update_undo_state_in_background)
    for timer_fn in timer_fns:
        if not bpy.app.timers.is_registered(timer_fn):
            bpy.app.timers.register(timer_fn)
