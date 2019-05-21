# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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

import os
import json
import bpy
import math
from collections import OrderedDict

from bpy.props import *
from mathutils import *
from .drivers import *
from .utils import *
from .error import *

#------------------------------------------------------------------------
#   Bone drivers
#------------------------------------------------------------------------

def addBoneDrivers(rig, prefix, poses):
    initRnaProperties(rig)
    for prop in poses.keys():
        pname = prefix+prop
        rig[pname] = 0.0
        rig["_RNA_UI"][pname] = {"min":0.0, "max":1.0}

    bdrivers = {}
    for pose,bones in poses.items():
        for bname,quat in bones.items():
            try:
                bdriver = bdrivers[bname]
            except KeyError:
                bdriver = bdrivers[bname] = [[],[],[],[]]
            for n in range(4):
                bdriver[n].append((prefix+pose, quat[n]))

    zeroQuat = ("1", "0", "0", "0")
    for bname,data in bdrivers.items():
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            pb = None
        if pb is None:
            bname = bname.replace(".","_")
            try:
                pb = rig.pose.bones[bname]
            except KeyError:
                print("Warning: Bone %s missing" % bname)
        if pb:
            addDrivers(rig, pb, "rotation_quaternion", data, zeroQuat)

#------------------------------------------------------------------------
#   Animation
#------------------------------------------------------------------------

def equal(x,y):
    return ((x[0]==y[0]) and (x[1]==y[1]) and (x[2]==y[2]) and (x[3]==y[3]))


def getCorrections(rig):
    corr = {}
    flipmat = Matrix.Rotation(math.pi/2, 3, 'X') * Matrix.Rotation(0, 3, 'X')
    for bone in rig.data.bones:
        loc,rot,scale = bone.matrix_local.decompose()
        rmat = rot.to_matrix()
        #corr[bone.name] = flipmat.inverted() * rmat
        corr[bone.name] = rmat
    return corr


theFacePoses = {}

def buildExpressions(mhSkel, rig, scn, cfg):
    global theFacePoses

    if "expressions" not in mhSkel.keys():
        return
    if "levator03.L" not in rig.data.bones.keys():
        print("Cannot add expressions to rig without face bones. Ignored.")
        return
    if "levator03.L" in rig.data.bones.keys():
        prefix = ""
    else:
        prefix = "DEF-"

    mhExprs = mhSkel["expressions"]
    if "face-poseunits" not in mhExprs.keys():
        return
    corr = getCorrections(rig)

    mhExpr = mhExprs["face-poseunits"]
    mhJson = mhExpr["json"]
    poses = OrderedDict()
    poseIndex = {}
    for n,name in enumerate(mhJson["framemapping"]):
        poseIndex[n] = poses[name] = {}

    buildBvh(mhExpr["bvh"], poseIndex, corr)
    for key,value in poses.items():
        theFacePoses[key] = value

    if not cfg.useFaceRigDrivers:
        print("Don't use face rig drivers")
        return
        
    addBoneDrivers(rig, "Mfa", poses)
    rig.MhxFaceRigDrivers = True

    #print("Expressions:")
    enames = list(mhExprs.keys())
    enames.sort()
    string = "&".join([ename for ename in enames if ename != "face-poseunits"])
    rig.MhxExpressions = string

    for ename in enames:
        if ename == "face-poseunits":
            continue
        #print("  ", ename)
        units = mhExprs[ename]["unit_poses"]
        rig["Mhu"+ename] = "&".join(["%s:%.4f" % (unit,uval)
            for unit,uval in units.items()])


def buildAnimation(mhSkel, rig, scn, offset, cfg):
    if "animation" not in mhSkel.keys():
        return
    if "lowerleg02.L" not in rig.data.bones.keys():
        print("Can only add animation to default rig. Ignored.")
        return

    mhAnims = mhSkel["animation"]
    corr = getCorrections(rig)

    poses = OrderedDict()
    locations = {}
    roots = {}
    root = None
    anims = list(mhAnims.items())
    anims.sort()
    for aname,mhAnim in anims:
        mhBvh = mhAnim["bvh"]
        frames = mhBvh["frames"]
        poseIndex = dict([(n,{}) for n in range(len(frames))])
        buildBvh(mhBvh, poseIndex, corr)
        poses[aname] = poseIndex[0]
        if "locations" in mhBvh.keys():
            locations[aname] = Vector(mhBvh["locations"][0]) + offset
            root = roots[aname] = mhBvh["joints"][0]
        else:
            roots[aname] = None

    if poses == {}:
        return

    if rig.animation_data:
        rig.animation_data.action = None
    string = "rest:None/(0,0,0)|"

    print("Poses:")
    for n,data in enumerate(poses.items()):
        aname,pose = data
        string += "&" + addFrame(rig, aname, n+2, pose, roots, locations)

    rig.MhxPoses = string


def addFrame(rig, aname, frame, pose, roots, locations):
    rstring = ""
    for pb in rig.pose.bones:
        if pb.name in pose.keys():
            quat = tuple(pose[pb.name])
            rstring += "%s/%s;" % (pb.name, quat)

    root = roots[aname]
    lstring = ""
    if root and root in rig.pose.bones.keys():
        rloc = tuple(zup(locations[aname]))
    else:
        rloc = (0,0,0)
    lstring = "%s/%s" % (root, rloc)

    return "%s:%s|%s" % (aname, lstring, rstring[:-1])


def buildBvh(mhBvh, poseIndex, corr):
    joints = mhBvh["joints"]
    #channels = mhBvh["channels"]
    frames = mhBvh["frames"]
    nJoints = len(joints)
    nFrames = len(frames)

    d2r = math.pi/180
    for m,frame in enumerate(frames):
        pose = poseIndex[m]
        for n,vec in enumerate(frame):
            x,y,z = vec
            euler = Euler((x*d2r, y*d2r, z*d2r), 'ZYX') # ZYX   # XZY
            quat = euler.to_quaternion()
            if abs(quat.to_axis_angle()[1]) > 1e-4:
                joint = joints[n]
                if joint in corr.keys():
                    cmat = corr[joint]
                    qmat = cmat.inverted() * euler.to_matrix() * cmat
                    pose[joint] = qmat.to_quaternion()

#------------------------------------------------------------------------
#   Add Face Rig
#------------------------------------------------------------------------

class VIEW3D_OT_AddFaceRigDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.add_facerig_drivers"
    bl_label = "Add Facerig Drivers"
    bl_description = "Control face rig with rig properties."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxFaceRig and not rig.MhxFaceRigDrivers)

    def execute(self, context):
        global theFacePoses
        rig = context.object
        addBoneDrivers(rig, "Mfa", theFacePoses)
        rig.MhxFaceRigDrivers = True
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Remove Face Rig
#------------------------------------------------------------------------

def removeBoneDrivers(rig, prefix, poses):
    bnames = {}
    for pose,bones in poses.items():
        prop = prefix+pose
        del rig[prop]
        for bname in bones.keys():
            bnames[bname] = True
    for bname in bnames:
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            continue
        pb.driver_remove("rotation_quaternion")


class VIEW3D_OT_RemoveFaceRigDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.remove_facerig_drivers"
    bl_label = "Remove Facerig Drivers"
    bl_description = "Remove rig property control of face rig."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers)

    def execute(self, context):
        global theFacePoses
        rig = context.object
        removeBoneDrivers(rig, "Mfa", theFacePoses)
        rig.MhxFaceRigDrivers = False
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Set expression
#------------------------------------------------------------------------

class VIEW3D_OT_SetExpressionButton(bpy.types.Operator):
    bl_idname = "mhx2.set_expression"
    bl_label = "Set Expression"
    bl_description = "Set expression"
    bl_options = {'UNDO'}

    units = StringProperty()

    def execute(self, context):
        from .drivers import resetProps, autoKeyProp
        rig = context.object
        scn = context.scene
        units = self.units.split("&")
        resetProps(rig, "Mfa", scn)
        for unit in units:
            key,value = unit.split(":")
            key = "Mfa"+key
            rig[key] = float(value)*rig.MhxExprStrength
            autoKeyProp(rig, key, scn)
        updateScene(context)
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Pose rig
#------------------------------------------------------------------------

class VIEW3D_OT_SetPoseButton(bpy.types.Operator):
    bl_idname = "mhx2.set_pose"
    bl_label = "Set Pose"
    bl_description = "Set pose"
    bl_options = {'UNDO'}

    string = StringProperty()

    def execute(self, context):
        rig = context.object
        scn = context.scene

        for pb in rig.pose.bones:
            pb.rotation_quaternion = (1,0,0,0)
            pb.location = (0,0,0)

        lstring,rstring = self.string.split("|",1)
        bname,loc = lstring.split("/",1)
        if bname == "None":
            root = None
        else:
            root = rig.pose.bones[bname]
            root.location = eval(loc)

        if rstring:
            for rword in rstring.split(";"):
                bname,rot = rword.split("/",1)
                pb = rig.pose.bones[bname]
                pb.rotation_quaternion = eval(rot)

        if scn.tool_settings.use_keyframe_insert_auto:
            if root:
                root.keyframe_insert("location")
            for pb in rig.pose.bones:
                pb.keyframe_insert("rotation_quaternion")
        return{'FINISHED'}

