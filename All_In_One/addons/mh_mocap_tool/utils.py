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
from math import sin, cos, atan, pi
from mathutils import *

from . import mcp

#
#   printMat3(string, mat)
#

def printMat3(string, mat, pad=""):
    if not mat:
        print("%s None" % string)
        return
    print("%s " % string)
    mc = "%s  [" % pad
    for m in range(3):
        s = mc
        for n in range(3):
            s += " %6.3f" % mat[m][n]
        print(s+"]")
 
def printMat4(string, mat, pad=""):
    if not mat:
        print("%s None" % string)
        return
    print("%s%s " % (pad, string))
    mc = "%s  [" % pad
    for m in range(4):
        s = mc
        for n in range(4):
            s += " %6.3f" % mat[m][n]
        print(s+"]")
 
#
#  quadDict():
#

def quadDict():
    return {
        0: {},
        1: {},
        2: {},
        3: {},
    }
    

#
#   nameOrNone(string):
#

def nameOrNone(string):
    if string == "None":
        return None
    else:
        return string
        
#
#   getRoll(bone):
#

def getRoll(bone):
    return getRollMat(bone.matrix_local)
    
    
def getRollMat(mat):  
    quat = mat.to_3x3().to_quaternion()
    if abs(quat.w) < 1e-4:
        roll = pi
    else:
        roll = -2*atan(quat.y/quat.w)
    return roll
    
#
#   getBone(name, rig):        
#

def getBone(name, rig): 
    try:
        return rig.pose.bones[rig[name]]
    except:
        pass
    #print(rig["MhxRigType"])
    try:
        mhxRig = rig["MhxRigType"]
    except:
        return None    
    if mhxRig in ["MHX", "Game", "Rorkimaru"]:
        try:
            return rig.pose.bones[name]
        except:
            return None
    elif mhxRig == "Rigify":
        print("Not yet")
    return None     
    
#
#   ikBoneList(rig):
#
 
def ikBoneList(rig):
    list = []
    for name in ['Root', 'Wrist_L', 'Wrist_R', 'LegIK_L', 'LegIK_R']:
        bone = getBone(name, rig)
        if bone:
            list.append(bone)
    return list
    
#
#   getAction(ob):
#

def getAction(ob):
    try:
        return ob.animation_data.action
    except:
        print("%s has no action" % ob)
        return None

#
#   deleteAction(act):    
#

def deleteAction(act):    
    act.use_fake_user = False
    if act.users == 0:
        bpy.data.actions.remove(act)
    else:
        print("%s has %d users" % (act, act.users))
        
#
#   copyAction(act1, name):
#

def copyAction(act1, name):
    act2 = bpy.data.actions.new(name)
    for fcu1 in act1.fcurves:
        fcu2 = act2.fcurves.new(fcu1.data_path, fcu1.array_index)
        for kp1 in fcu1.keyframe_points:
            fcu2.keyframe_points.insert(kp1.co[0], kp1.co[1], options={'FAST'})
    return act2            
        
#
#   activeFrames(ob):
#

def activeFrames(ob):
    active = {}
    if ob.animation_data is None:
        return []
    action = ob.animation_data.action
    if action is None:
        return []
    for fcu in action.fcurves:
        for kp in fcu.keyframe_points:
            active[kp.co[0]] = True
    frames = list(active.keys())
    frames.sort()
    return frames

#
#   fCurveIdentity(fcu):
#

def fCurveIdentity(fcu):
    words = fcu.data_path.split('"')
    if len(words) < 2:
        return (None, None)
    name = words[1]
    words = fcu.data_path.split('.')
    mode = words[-1]
    return (name, mode)

#
#   findFCurve(path, index, fcurves):
#

def findFCurve(path, index, fcurves):
    for fcu in fcurves:
        if (fcu.data_path == path and
            fcu.array_index == index):
            return fcu
    return None            
    
#
#   isRotation(mode):
#   isLocation(mode):
#

def isRotation(mode):
    return (mode[0:3] == 'rot')
    
def isLocation(mode):
    return (mode[0:3] == 'loc')
    

#
#    setRotation(pb, mat, frame, group):
#

def setRotation(pb, rot, frame, group):
    if pb.rotation_mode == 'QUATERNION':
        try:
            quat = rot.to_quaternion()
        except:
            quat = rot
        pb.rotation_quaternion = quat
        pb.keyframe_insert('rotation_quaternion', frame=frame, group=group)
    else:
        try:
            euler = rot.to_euler(pb.rotation_mode)
        except:
            euler = rot
        pb.rotation_euler = euler
        pb.keyframe_insert('rotation_euler', frame=frame, group=group)

#
#    setInterpolation(rig):
#

def setInterpolation(rig):
    if not rig.animation_data:
        return
    act = rig.animation_data.action
    if not act:
        return
    for fcu in act.fcurves:
        for pt in fcu.keyframe_points:
            pt.interpolation = 'LINEAR'
        fcu.extrapolation = 'CONSTANT'
    return

#
#   insertRotationKeyFrame(pb, frame):    
#

def insertRotationKeyFrame(pb, frame):    
    rotMode = pb.rotation_mode
    grp = pb.name
    if rotMode == "QUATERNION":
        pb.keyframe_insert("rotation_quaternion", frame=frame, group=grp)
    elif rotMode == "AXIS_ANGLE":
        pb.keyframe_insert("rotation_axis_angle", frame=frame, group=grp)
    else:
        pb.keyframe_insert("rotation_euler", frame=frame, group=grp)

#
#
#

class MocapError(Exception):
    def __init__(self, value):
        self.value = value
        print("*** Mocap error ***\n%s" % value)
        mcp.errorLines = value.split("\n")
    def __str__(self):
        return repr(self.value)
  
class ErrorOperator(bpy.types.Operator):
    bl_idname = "mcp.error"
    bl_label = "Mocap error"

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        for line in mcp.errorLines:
            self.layout.label(line)
#
#
#

import os
import imp
import sys

def initModules():
    basePath = os.path.realpath(".")
    print("Path", basePath) 
    mcp.targetRigs = initModulesPath(basePath, "target_rigs")
    mcp.sourceRigs = initModulesPath(basePath, "source_rigs")
    return

def initModulesPath(basePath, subPath):
    path = os.path.join(basePath, subPath)
    rignames = []
    for relpath in os.listdir:
        (modname, ext) = os.path.splitext(relpath)
        if ext == ".py":
            file = os.path.join(path, relpath)
            print("Import %s" % modname)
            fp, pathname, description = imp.find_module(modname)
            try:
                imp.load_module(modname, fp, pathname, description)
            finally:
                if fp:
                    fp.close()
        rignames.append(modname)
    return rignames        

   