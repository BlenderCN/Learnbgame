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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
from bpy.props import *
from math import pi, sqrt
from mathutils import *
from . import utils, load, simplify, props, action
#from .target_rigs import rig_mhx
from . import mcp
from .utils import MocapError

########################################################################
#
#   startEdit(context):
#   class VIEW3D_OT_McpStartEditButton(bpy.types.Operator):
#

def getUndoAction(rig):
    try:
        name = rig["McpUndoAction"]
        return bpy.data.actions[name]
    except:
        return None

def startEdit(context):
    rig = context.object
    if getUndoAction(rig):
        raise MocapError("Action already being edited. Undo or confirm edit first")
    act = utils.getAction(rig)
    if not act:
        return
    aname = act.name        
    act.name = '#'+aname
    nact = bpy.data.actions.new(aname)
    rig.animation_data.action = nact
    rig["McpUndoAction"] = act.name
    rig["McpActionName"] = aname

    mcp.editLoc = utils.quadDict()
    mcp.editRot = utils.quadDict()

    for fcu in act.fcurves:
        (name, mode) = utils.fCurveIdentity(fcu)
        nfcu = nact.fcurves.new(fcu.data_path, index=fcu.array_index, action_group=name)
        n = len(fcu.keyframe_points)
        nfcu.keyframe_points.add(count=n)
        for i in range(n):
            nfcu.keyframe_points[i].co = fcu.keyframe_points[i].co
    utils.setInterpolation(rig)        
    print("Action editing started")
    return nact       

class VIEW3D_OT_McpStartEditButton(bpy.types.Operator):
    bl_idname = "mcp.start_edit"
    bl_label = "Start Edit"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            startEdit(context)
            setKeyMap(context, "mcp.insert_locrot", True)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    

def setKeyMap(context, idname, doAdd):
    km = context.window_manager.keyconfigs.active.keymaps['3D View']
    if doAdd:
        km.keymap_items.new(idname, 'SPACE', 'PRESS')
    else:
        try:
            item = km.keymap_items[idname]        
        except KeyError:
            return
        km.keymap_items.remove(item)
    return        
 
#
#   undoEdit(context):
#   class VIEW3D_OT_McpUndoEditButton(bpy.types.Operator):
#

def undoEdit(context):
    rig = context.object
    oact = getUndoAction(rig)
    if not oact:
        raise MocapError("No action to undo")
    rig["McpUndoAction"] = ""
    mcp.editLoc = None
    mcp.editRot = None
    rig["McpActionName"] = ""
    act = rig.animation_data.action
    act.name = "#Delete"
    oact.name = rig["McpActionName"] 
    rig.animation_data.action = oact
    utils.deleteAction(act)
    print("Action changes undone")
    return

class VIEW3D_OT_McpUndoEditButton(bpy.types.Operator):
    bl_idname = "mcp.undo_edit"
    bl_label = "Undo Edit"
    bl_options = {'UNDO'}
    answer = StringProperty(default="")

    def execute(self, context):
        mcp.editString = "?"
        if self.answer == "":
            mcp.editString = "Really undo editing?"
            mcp.editConfirm = self.bl_idname
        elif self.answer == "yes":
            mcp.editConfirm = ""
            setKeyMap(context, "mcp.insert_locrot", False)
            try:
                undoEdit(context)
            except MocapError:
                bpy.ops.mcp.error('INVOKE_DEFAULT')
        else:
            mcp.editConfirm = ""
        return{'FINISHED'} 
        
#
#   getActionPair(context):
#

def getActionPair(context):
    rig = context.object
    oact = getUndoAction(rig)
    if not oact:
        raise MocapError("No action is currently being edited")
        return None
    try:
        mcp.editLoc
        mcp.editRot
    except:
        mcp.editLoc = utils.quadDict()
        mcp.editRot = utils.quadDict()
    act = utils.getAction(rig)
    if act:
        return (act, oact)
    else:
        return None

#
#   confirmEdit(context):
#   class VIEW3D_OT_McpConfirmEditButton(bpy.types.Operator):
#

def confirmEdit(context):
    rig = context.object
    pair = getActionPair(context)
    if not pair:
        return
    (act, oact) = pair

    for fcu in act.fcurves:
        ofcu = utils.findFCurve(fcu.data_path, fcu.array_index, oact.fcurves)
        if not ofcu:
            continue
        (name,mode) =  utils.fCurveIdentity(fcu)
        if utils.isRotation(mode):
            try:
                edit = mcp.editRot[fcu.array_index][name]
            except:
                continue
            displaceFCurve(fcu, ofcu, edit)
        elif  utils.isLocation(mode):
            try:
                edit = mcp.editLoc[fcu.array_index][name]
            except:
                continue
            displaceFCurve(fcu, ofcu, edit)

    rig["McpUndoAction"] = ""
    rig["McpActionName"] = ""
    mcp.editLoc = None
    mcp.editRot = None
    utils.deleteAction(oact)
    print("Action changed")
    return                
            
class VIEW3D_OT_McpConfirmEditButton(bpy.types.Operator):
    bl_idname = "mcp.confirm_edit"
    bl_label = "Confirm Edit"
    bl_options = {'UNDO'}

    def execute(self, context):
        setKeyMap(context, "mcp.insert_locrot", False)
        try:
            confirmEdit(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'} 

#
#   setEditDict(editDict, frame, name, channel, index):
#   insertKey(context, useLoc, useRot):
#   class VIEW3D_OT_McpInsertLocButton(bpy.types.Operator):
#   class VIEW3D_OT_McpInsertRotButton(bpy.types.Operator):
#   class VIEW3D_OT_McpInsertLocRotButton(bpy.types.Operator):
#

def setEditDict(editDict, frame, name, channel, n):
    for index in range(n):        
        try:
            editDict[index][name]
        except:
            editDict[index][name] = {}
        edit = editDict[index][name]
        edit[frame] = channel[index]
    return        

def insertKey(context, useLoc, useRot):
    rig = context.object
    pair = getActionPair(context)
    if not pair:
        raise MocapError("No action is currently being edited")
    (act, oact) = pair
    
    pb = bpy.context.active_pose_bone
    frame = context.scene.frame_current    
    for pb in rig.pose.bones:
        if not pb.bone.select:
            continue
        if useLoc:
            setEditDict(mcp.editLoc, frame, pb.name, pb.location, 3)
        if useRot:        
            if pb.rotation_mode == 'QUATERNION':
                setEditDict(mcp.editRot, frame, pb.name, pb.rotation_quaternion, 4)
            else:
                setEditDict(mcp.editRot, frame, pb.name, pb.rotation_euler, 3)
        for fcu in act.fcurves:
            ofcu = utils.findFCurve(fcu.data_path, fcu.array_index, oact.fcurves)
            if not ofcu:
                continue
            (name,mode) =  utils.fCurveIdentity(fcu)
            if name == pb.name:
                if utils.isRotation(mode) and useRot:
                    displaceFCurve(fcu, ofcu, mcp.editRot[fcu.array_index][name])
                if  utils.isLocation(mode) and useLoc:
                    displaceFCurve(fcu, ofcu, mcp.editLoc[fcu.array_index][name])
    return                

class VIEW3D_OT_McpInsertLocButton(bpy.types.Operator):
    bl_idname = "mcp.insert_loc"
    bl_label = "Loc"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            insertKey(context, True, False)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'} 
        
class VIEW3D_OT_McpInsertRotButton(bpy.types.Operator):
    bl_idname = "mcp.insert_rot"
    bl_label = "Rot"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            insertKey(context, False, True)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'} 
        
class VIEW3D_OT_McpInsertLocRotButton(bpy.types.Operator):
    bl_idname = "mcp.insert_locrot"
    bl_label = "LocRot"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            insertKey(context, True, True)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'} 
        
#
#   displaceFCurve(fcu, ofcu, edits):       
#   setupCatmullRom(kpoints, modified): 
#   evalCatmullRom(t, fcn):
#
        
def displaceFCurve(fcu, ofcu, edits):        
    modified = []
    editList = list(edits.items())
    editList.sort()
    for (t,y) in editList:
        dy = y - ofcu.evaluate(t)
        modified.append((t,dy))
        
    if len(modified) >= 1:
        kp = fcu.keyframe_points[0].co
        t0 = int(kp[0])
        (t1,y1) = modified[0]
        kp = fcu.keyframe_points[-1].co
        tn = int(kp[0])
        (tn_1,yn_1) = modified[-1]
        modified = [(t0, y1)] + modified
        modified.append( (tn, yn_1) )
        fcn = setupCatmullRom(modified)            
        for kp in fcu.keyframe_points:
            t = kp.co[0]
            y = ofcu.evaluate(t)
            dy = evalCatmullRom(t, fcn)
            kp.co[1] = y+dy
    return
    
                        
def setupCatmullRom(points): 
    points.sort()
    n = len(points)-1
    fcn = []
    tension = 0.5
    
    # First interval
    (t0,y0) = points[0]
    (t1,y1) = points[1]
    (t2,y2) = points[2]
    if t1-t0 < 0.5:
        t0 = t1-1
    d = y0
    a = y1
    c = 3*d + tension*(y1-y0)
    b = 3*a - tension*(y2-y0)
    tfac = 1.0/(t1-t0)
    fcn.append((t0, t1, tfac, (a,b,c,d)))
    
    # Inner intervals
    for i in range(1,n-1):
        (t_1,y_1) = points[i-1]
        (t0,y0) = points[i]
        (t1,y1) = points[i+1]
        (t2,y2) = points[i+2]
        d = y0
        a = y1
        c = 3*d + tension*(y1-y_1)
        b = 3*a - tension*(y2-y0)
        tfac = 1.0/(t1-t0)
        fcn.append((t0, t1, tfac, (a,b,c,d)))
        
    # Last interval
    (t_1,y_1) = points[n-2]
    (t0,y0) = points[n-1]
    (t1,y1) = points[n]
    if t1-t0 < 0.5:
        t1 = t0+1
    d = y0
    a = y1
    c = 3*d + tension*(y1-y_1)
    b = 3*a - tension*(y1-y0)
    tfac = 1.0/(t1-t0)
    fcn.append((t0, t1, tfac, (a,b,c,d)))

    return fcn  
    
def evalCatmullRom(t, fcn):
    (t0, t1, tfac, params) = fcn[0]
    if t < t0:
        return evalCRInterval(t, t0, t1, tfac, params)
    for (t0, t1, tfac, params) in fcn:
        if t >= t0 and t < t1:
            return evalCRInterval(t, t0, t1, tfac, params)
    return evalCRInterval(t, t0, t1, tfac, params)

def evalCRInterval(t, t0, t1, tfac, params):
    (a,b,c,d) = params
    x = tfac*(t-t0)
    x1 = 1-x
    f = x*x*(a*x + b*x1) + x1*x1*(c*x+d*x1)
    return f

