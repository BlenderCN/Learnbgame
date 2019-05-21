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
from math import pi, sqrt
from mathutils import *
from . import utils, load, simplify, props, action
#from .target_rigs import rig_mhx
from .utils import MocapError

#
#   normalizeRotCurves(scn, rig, fcurves, frames)
#

        
def normalizeRotCurves(scn, rig, fcurves, frames):        
    hasQuat = {}
    for fcu in fcurves:
        (name, mode) = utils.fCurveIdentity(fcu)
        if mode == 'rotation_quaternion':
            hasQuat[name] = rig.pose.bones[name]

    for frame in frames:
        scn.frame_set(frame)
        for (name, pb) in hasQuat.items():
            pb.rotation_quaternion.normalize()
            pb.keyframe_insert("rotation_quaternion", group=name)  
    return            

#
#   loopFCurves(context):
#   loopFCurve(fcu, minTime, maxTime, scn):
#   class VIEW3D_OT_McpLoopFCurvesButton(bpy.types.Operator):
#

def loopFCurves(context):
    scn = context.scene
    rig = context.object
    act = utils.getAction(rig)
    if not act:
        return
    (fcurves, minTime, maxTime) = simplify.getActionFCurves(act, False, True, scn)
    if not fcurves:
        return

    frames = utils.activeFrames(rig)
    normalizeRotCurves(scn, rig, fcurves, frames)

    hasLocation = {}
    for fcu in fcurves:
        (name, mode) = utils.fCurveIdentity(fcu)
        if utils.isRotation(mode) and scn.McpLoopRot:
            loopFCurve(fcu, minTime, maxTime, scn)

    if scn.McpLoopLoc:
        if scn.McpLoopInPlace:
            for pb in utils.ikBoneList(rig):
                scn.frame_set(minTime)
                head0 = pb.head.copy()
                scn.frame_set(maxTime)
                head1 = pb.head.copy()
                offs = (head1-head0)/(maxTime-minTime)
                if not scn.McpLoopZInPlace:
                    offs[2] = 0
                print("Loc", pb.name, offs)

                restMat = pb.bone.matrix_local.to_3x3()
                restInv = restMat.inverted()
                #if pb.parent:
                #    parRest = pb.parent.bone.matrix_local.to_3x3()
                #    restInv = restInv * parRest

                for frame in frames:
                    scn.frame_set(frame)    
                    head = pb.head.copy() - (frame-minTime)*offs
                    diff = head - pb.bone.head_local
                    #if pb.parent:
                    #    parMat = pb.parent.matrix.to_3x3()                        
                    #    diff = parMat.inverted() * diff                        
                    pb.location = restInv * diff                    
                    pb.keyframe_insert("location", group=pb.name)  
                # pb.matrix_basis = pb.bone.matrix_local.inverted() * par.bone.matrix_local * par.matrix.inverted() * pb.matrix

        for fcu in fcurves:
            (name, mode) = utils.fCurveIdentity(fcu)
            if utils.isLocation(mode):
                loopFCurve(fcu, minTime, maxTime, scn)
    print("F-curves looped")                
    return
    
    
    
def loopFCurve(fcu, t0, tn, scn):
    delta = scn.McpLoopBlendRange
    
    v0 = fcu.evaluate(t0)
    vn = fcu.evaluate(tn)
    fcu.keyframe_points.insert(frame=t0, value=v0)
    fcu.keyframe_points.insert(frame=tn, value=vn)
    (mode, upper, lower, diff) = simplify.getFCurveLimits(fcu) 
    if mode == 'location': 
        dv = vn-v0        
    else:
        dv = 0.0
        
    newpoints = []
    for dt in range(delta):
        eps = 0.5*(1-dt/delta)

        t1 = t0+dt
        v1 = fcu.evaluate(t1)
        tm = tn+dt
        vm = fcu.evaluate(tm) - dv
        if (v1 > upper) and (vm < lower):
            vm += diff
        elif (v1 < lower) and (vm > upper):
            vm -= diff
        pt1 = (t1, (eps*vm + (1-eps)*v1))
        
        t1 = t0-dt
        v1 = fcu.evaluate(t1) + dv
        tm = tn-dt
        vm = fcu.evaluate(tm)
        if (v1 > upper) and (vm < lower):
            v1 -= diff
        elif (v1 < lower) and (vm > upper):
            v1 += diff
        ptm = (tm, eps*v1 + (1-eps)*vm)
        
        #print("  ", pt1,ptm)
        newpoints.extend([pt1,ptm])
        
    newpoints.sort()
    for (t,v) in newpoints: 
        fcu.keyframe_points.insert(frame=t, value=v)
    return

class VIEW3D_OT_McpLoopFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.loop_fcurves"
    bl_label = "Loop F-curves"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            loopFCurves(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    
    
#    
#   repeatFCurves(context, nRepeats):
#

def repeatFCurves(context, nRepeats):
    act = utils.getAction(context.object)
    if not act:
        return
    (fcurves, minTime, maxTime) = simplify.getActionFCurves(act, False, True, context.scene)
    if not fcurves:
        return
    dt0 = maxTime-minTime
    for fcu in fcurves:
        (name, mode) = utils.fCurveIdentity(fcu)
        dy0 = fcu.evaluate(maxTime) - fcu.evaluate(minTime)
        points = []
        for kp in fcu.keyframe_points:
            t = kp.co[0]
            if t >= minTime and t < maxTime:
                points.append((t, kp.co[1]))
        for n in range(1,nRepeats):
            dt = n*dt0
            dy = n*dy0
            for (t,y) in points:
                fcu.keyframe_points.insert(t+dt, y+dy, options={'FAST'})
    print("F-curves repeated %d times" % nRepeats)
    return
                
class VIEW3D_OT_McpRepeatFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.repeat_fcurves"
    bl_label = "Repeat F-curves"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            repeatFCurves(context, context.scene.McpRepeatNumber)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    
    

#
#   stitchActions(context):
#

def stitchActions(context):
    action.listAllActions(context)
    scn = context.scene
    rig = context.object
    act1 = action.getAction(scn.McpFirstAction)
    act2 = action.getAction(scn.McpSecondAction)
    frame1 = scn.McpFirstEndFrame
    frame2 = scn.McpSecondStartFrame
    delta = scn.McpLoopBlendRange

    if not rig.animation_data:
        pb = context.active_posebone
        pb.keyframe_insert("location", group=pb.name)
        rig.animation_data.action = None

    actionTarget = scn.McpActionTarget
    print("Acttar", actionTarget)
    if actionTarget == "Stitch new":
        act2 = utils.copyAction(act2, scn.McpOutputActionName)
    elif actionTarget == "Prepend second":
        act2.name = scn.McpOutputActionName

    shift = frame1 - frame2 + 2*delta
    translateFCurves(act2.fcurves, shift)

    for fcu2 in act2.fcurves:
        fcu1 = utils.findFCurve(fcu2.data_path, fcu2.array_index, act1.fcurves)
        for kp1 in fcu1.keyframe_points:
            t = kp1.co[0]
            y1 = kp1.co[1]
            if t <= frame1 - delta:
                y = y1
            elif t <= frame1 + delta:
                y2 = fcu2.evaluate(t+shift)
                eps = (t - frame1 + delta)/(2*delta)
                y = y1*(1-eps) + y2*eps
            else:
                break
            fcu2.keyframe_points.insert(t, y, options={'FAST'})
        for kp2 in fcu2.keyframe_points:
            t = kp2.co[0] - shift
            if t >= frame1 + delta:
                fcu2.keyframe_points.insert(t, kp2.co[1], options={'FAST'})

    rig.animation_data.action = action.getAction(scn.McpOutputActionName)
    utils.setInterpolation(rig)
    return        


def translateFCurves(fcurves, dt):
    for fcu in fcurves:
        if dt > 0:
            kpts = list(fcu.keyframe_points)
            kpts.reverse()
            for kp in kpts:
                kp.co[0] += dt
        elif dt < 0:                
            for kp in fcu.keyframe_points:
                kp.co[0] += dt
    return
   
    
class VIEW3D_OT_McpStitchActionsButton(bpy.types.Operator):
    bl_idname = "mcp.stitch_actions"
    bl_label = "Stitch Actions"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            stitchActions(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    
    
    
#
#   shiftBoneFCurves(context):
#   class VIEW3D_OT_McpShiftBoneFCurvesButton(bpy.types.Operator):
#

def shiftBoneFCurves(context):
    frame = context.scene.frame_current
    rig = context.object
    act = utils.getAction(rig)
    if not act:
        return
    (origLoc, origRot, touchedLoc, touchedRot) = setupOrigAndTouched(context, act, frame)
    touchBones(rig, frame, touchedLoc, touchedRot)    
    for fcu in act.fcurves:
        (name, mode) = utils.fCurveIdentity(fcu)
        try:
            if utils.isRotation(mode):
                dy = fcu.evaluate(frame) - origRot[fcu.array_index][fcu.data_path]
            elif  utils.isLocation(mode):
                dy = fcu.evaluate(frame) - origLoc[fcu.array_index][fcu.data_path]
        except:
            continue     
        for kp in fcu.keyframe_points:
            if kp.co[0] != frame:
                kp.co[1] += dy
    return
    
def setupOrigAndTouched(context, act, frame):
    origLoc = utils.quadDict()
    origRot = utils.quadDict()
    touchedLoc = {}
    touchedRot = {}
    for fcu in act.fcurves:
        (name, mode) = utils.fCurveIdentity(fcu)
        for pb in context.selected_pose_bones:
            if pb.name == name:
                #kp = fcu.keyframe_points[frame]
                y = fcu.evaluate(frame)
                if utils.isRotation(mode):
                    origRot[fcu.array_index][fcu.data_path] = y
                    touchedRot[pb.name] = True
                elif utils.isLocation(mode):
                    origLoc[fcu.array_index][fcu.data_path] = y
                    touchedLoc[pb.name] = True
    return (origLoc, origRot, touchedLoc, touchedRot)                    

def touchBones(rig, frame, touchedLoc, touchedRot):
    for name in touchedRot.keys():
        pb = rig.pose.bones[name]
        utils.insertRotationKeyFrame(pb, frame)
    for name in touchedLoc.keys():
        pb = rig.pose.bones[name]
        pb.keyframe_insert("location", frame=frame, group=pb.name)
    return        

class VIEW3D_OT_McpShiftBoneFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.shift_bone"
    bl_label = "Shift Bone F-curves"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            shiftBoneFCurves(context)
            print("Bones shifted")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    
        
