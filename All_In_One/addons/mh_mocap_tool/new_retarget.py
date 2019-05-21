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



import bpy, os, mathutils, math, time
from math import sin, cos
from mathutils import *
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

from . import utils, props, source, target, toggle, load, simplify
#from .target_rigs import rig_mhx
from . import mcp
from .utils import MocapError

Deg2Rad = math.pi/180
D = 180/math.pi
    
#
#   class CBoneData:
#

class CBoneData:
    def __init__(self, srcBone, trgBone):
        self.name = srcBone.name
        self.parent = None        
        self.srcMatrices = {}        
        self.srcPoseBone = srcBone        
        self.trgPoseBone = trgBone
        self.trgRestMat = None
        self.trgRestInv = None
        self.trgBakeMat = None
        self.trgBakeInv = None
        self.trgOffset = None
        self.rotOffset = None
        self.rotOffsInv = None
        self.rollMat = None
        self.rollInv = None
        return
        
#class CMatrixGroup:
#    def __init__(self, srcMat, frame):
#        self.frame = frame
#        self.srcMatrix = srcMat.copy()
#        return
#        
#    def __repr__(self):
#        return "<CMat %d %s>" % (self.frame, self.srcMatrix)
        
        
class CAnimation:
    def __init__(self, srcRig, trgRig):
        self.srcRig = srcRig
        self.trgRig = trgRig
        self.boneDatas = {}
        self.boneDataList = []
        return

#
#
#

KeepRotationOffset = ["Root", "Pelvis", "Hips", "Hip_L", "Hip_R"]
ClavBones = ["Clavicle_L", "Clavicle_R"]
SpineBones = ["Spine1", "Spine2", "Spine3", "Neck", "Head"]
#FootBones = []
#IgnoreBones = []
FootBones = ["Foot_L", "Foot_R", "Toe_L", "Toe_R"]
IgnoreBones = ["Toe_L", "Toe_R"]

#
#
#


def setTranslation(mat, loc):
    for m in range(3):
        mat[m][3] = loc[m][3]


def setTranslationVec(mat, loc):
    for m in range(3):
        mat[m][3] = loc[m]


def setRotation(mat, rot):
    for m in range(3):
        for n in range(3):
            mat[m][n] = rot[m][n]
        
        
def keepRollOnly(mat):
    for n in range(4):
        mat[1][n] = 0
        mat[n][1] = 0
        mat[3][n] = 0
        mat[n][3] = 0
    mat[1][1] = 1
            
#
#   retargetFkBone(boneData, frame):
#

def retargetFkBone(boneData, frame):
    srcBone = boneData.srcPoseBone
    trgBone = boneData.trgPoseBone
    name = srcBone.name
    srcMatrix = boneData.srcMatrices[frame]
    srcRot = srcMatrix  #* srcData.rig.matrix_world
    bakeMat = srcMatrix

    # Set translation offset
    parent = boneData.parent
    if parent:
        #print(name, parent.name)
        parMat = parent.srcMatrices[frame]
        parInv = parMat.inverted()
        loc = parMat * boneData.trgOffset
        setTranslation(bakeMat, loc)
        bakeMat = parInv * bakeMat

        if parent.rollMat:
            #roll = utils.getRollMat(parent.rollMat)
            #print("ParRoll", name, parent.name, roll*D)
            bakeRot = parent.rollInv * bakeMat
            setRotation(bakeMat, bakeRot)
        elif parent.rotOffsInv:
            bakeRot = parent.rotOffsInv * bakeMat
            setRotation(bakeMat, bakeRot)

        parRest = parent.trgRestMat
        bakeMat = parRest * bakeMat
    else:
        parMat = None
        parRotInv = None
        
    # Set rotation offset        
    if boneData.rotOffset:
        rot = boneData.rotOffset
        if parent and parent.rotOffsInv:
            rot = rot * parent.rotOffsInv        
        bakeRot = bakeMat * rot
        setRotation(bakeMat, bakeRot)
    else:
        rot = None
        
    trgMat = boneData.trgRestInv * bakeMat

    if boneData.rollMat:
        #roll = utils.getRollMat(boneData.rollMat)
        #print("SelfRoll", name, roll*D)
        trgRot = trgMat * boneData.rollMat
        setRotation(trgMat, trgRot)
        #utils.printMat4(" Trg2", trgMat, "  ")
        #halt

    trgBone.matrix_basis = trgMat
    if 0 and trgBone.name == "Hip_L":
        print(name)
        utils.printMat4(" PM", parMat, "  ")
        utils.printMat4(" PR", parent.rotOffsInv, "  ")
        utils.printMat4(" RO", boneData.rotOffset, "  ")
        utils.printMat4(" BR", bakeRot, "  ")
        utils.printMat4(" BM", bakeMat, "  ")
        utils.printMat4(" Trg", trgMat, "  ")
        #halt
    
    if trgBone.name in IgnoreBones:
        trgBone.rotation_quaternion = (1,0,0,0)
    
    utils.insertRotationKeyFrame(trgBone, frame)
    if not boneData.parent:
        trgBone.keyframe_insert("location", frame=frame, group=trgBone.name)
    return        
   
#
#   collectSrcMats(anim, frames, scn):
#

def hideObjects(scn, rig):
    objects = []
    for ob in scn.objects:
        if ob != rig:
            objects.append((ob, list(ob.layers)))
            ob.layers = 20*[False]
    return objects
    
    
def unhideObjects(objects):
    for (ob,layers) in objects:
        ob.layers = layers
    return
    
    
def collectSrcMats(anim, frames, scn):
    objects = hideObjects(scn, anim.srcRig)
    try:            
        for frame in frames:
            scn.frame_set(frame)
            if frame % 100 == 0:
                print("Collect", int(frame))
            for boneData in anim.boneDataList:
                boneData.srcMatrices[frame] = boneData.srcPoseBone.matrix.copy()
    finally:
        unhideObjects(objects)
    return                

#
#   retargetMatrices(anim, frames, first, doFK, doIK, scn):
#

def retargetMatrices(anim, frames, first, doFK, doIK, scn):
    for frame in frames:
        if frame % 100 == 0:
            print("Retarget", int(frame))
        if doFK:
            for boneData in anim.boneDataList:
                retargetFkBone(boneData, frame)
        else:
            scn.frame_set(frame)
        if doIK:
            retargetIkBones(anim.trgRig, frame, first) 
            first = False
    return                
  
#
#   setupFkBones(srcRig, trgRig, boneAssoc, parAssoc, anim, scn):
#
    
def getParent(parName, parAssoc, trgRig, anim):
    if not parName:
        return None
    try:
        trgParent = trgRig.pose.bones[parName]
    except KeyError:
        return None
    try:
        anim.boneDatas[trgParent.name]        
        return trgParent
    except        :
        pass
    return getParent(parAssoc[trgParent.name], parAssoc, trgRig, anim)
    
    
def setupFkBones(srcRig, trgRig, boneAssoc, parAssoc, anim, scn):
    keepOffsets = KeepRotationOffset + FootBones
    keepOffsInverts = []
    if scn.McpUseSpineOffset:
        keepOffsets += SpineBones
        keepOffsInverts += SpineBones
    if scn.McpUseClavOffset:
        keepOffsets += ClavBones
        keepOffsInverts += ClavBones
        
    for (trgName, srcName) in boneAssoc:
        try:
            trgBone = trgRig.pose.bones[trgName]
            srcBone = srcRig.pose.bones[srcName]
        except:
            print("  -", trgName, srcName)
            continue
        boneData = CBoneData(srcBone, trgBone)
        anim.boneDatas[trgName] = boneData   
        anim.boneDataList.append(boneData)
        boneData.trgRestMat = trgBone.bone.matrix_local

        boneData.trgRestInv = trgBone.bone.matrix_local.inverted()
        boneData.trgBakeMat = boneData.trgRestMat  

        trgParent = None        
        if trgBone.parent:  #trgBone.bone.use_inherit_rotation:
            trgParent = getParent(parAssoc[trgName], parAssoc, trgRig, anim)
            if trgParent:
                boneData.parent = anim.boneDatas[trgParent.name]
                parRest = boneData.parent.trgRestMat
                parRestInv = boneData.parent.trgRestInv
                offs = trgBone.bone.head_local - trgParent.bone.head_local
                boneData.trgOffset = parRestInv * Matrix.Translation(offs) * parRest
                boneData.trgBakeMat = parRestInv * boneData.trgRestMat
                #print(trgName, trgParent.name)


        trgRoll = utils.getRoll(trgBone.bone)
        srcRoll = source.getSourceRoll(srcName) * Deg2Rad
        diff = srcRoll - trgRoll

        if srcName in keepOffsets:        
            offs = trgBone.bone.matrix_local*srcBone.bone.matrix_local.inverted()
            boneData.rotOffset = boneData.trgRestInv * offs * boneData.trgRestMat
            if trgName in keepOffsInverts:
                boneData.rotOffsInv = boneData.rotOffset.inverted()                        
        elif abs(diff) > 0.02:            
            boneData.rollMat = Matrix.Rotation(diff, 4, 'Y') 
            boneData.rollInv = boneData.rollMat.inverted()
        
        boneData.trgBakeInv = boneData.trgBakeMat.inverted()   
    return


#
#    retargetMhxRig(context, srcRig, trgRig, doFK, doIK):
#

def clearPose():    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.loc_clear()


def setupMhxAnimation(scn, srcRig, trgRig):
    clearPose()

    source.ensureSourceInited(scn)
    source.setArmature(srcRig, scn)
    target.ensureTargetInited(scn)
    print("Retarget %s --> %s" % (srcRig, trgRig))
    if trgRig.animation_data:
        trgRig.animation_data.action = None

    anim = CAnimation(srcRig, trgRig)
    (boneAssoc, parAssoc, rolls) = target.getTargetArmature(trgRig, scn)
    #(boneAssoc, ikBoneAssoc, parAssoc, rolls, mats, ikBones, ikParents) = target.makeTargetAssoc(trgRig, scn)
    setupFkBones(srcRig, trgRig, boneAssoc, parAssoc, anim, scn)
    return anim
    

def retargetMhxRig(context, srcRig, trgRig, doFK, doIK):
    scn = context.scene
    if doFK:
        anim = setupMhxAnimation(scn, srcRig, trgRig)
    else:
        anim = CAnimation(srcRig, trgRig)
    frames = utils.activeFrames(srcRig)

    scn.objects.active = trgRig
    scn.update()

    try:
        scn.frame_current = frames[0]
    except:
        raise MocapError("No frames found.")
    oldData = changeTargetData(trgRig, anim)
    clearPose()
    frameBlock = frames[0:100]
    index = 0
    first = True
    try:
        while frameBlock:
            if doFK:
                collectSrcMats(anim, frameBlock, scn)
            retargetMatrices(anim, frameBlock, first, doFK, doIK, scn)
            index += 100
            first = False
            frameBlock = frames[index:index+100]
            
        scn.frame_current = frames[0]
    finally:                
        restoreTargetData(trgRig, oldData)
            
    utils.setInterpolation(trgRig)
    if doFK:
        act = trgRig.animation_data.action
        act.name = trgRig.name[:4] + srcRig.name[2:]
        act.use_fake_user = True
        print("Retargeted %s --> %s" % (srcRig, trgRig))
    else:
        print("IK retargeted %s" % trgRig)
    return

#
#   changeTargetData(rig, anim):    
#   restoreTargetData(rig, data):
#
    
def changeTargetData(rig, anim):    
    tempProps = [
        ("MhaRotationLimits", 0.0),
        ("MhaArmIk_L", 0.0),
        ("MhaArmIk_R", 0.0),
        ("MhaLegIk_L", 0.0),
        ("MhaLegIk_R", 0.0),
        ("MhaSpineIk", 0),
        ("MhaSpineInvert", 0),
        ("MhaElbowPlant_L", 0),
        ("MhaElbowPlant_R", 0),
        ]

    props = []
    for (key, value) in tempProps:
        try:
            props.append((key, rig[key]))
            rig[key] = value
        except KeyError:
            pass

    permProps = [
        ("MhaElbowFollowsShoulder", 0),
        ("MhaElbowFollowsWrist", 0),
        ("MhaKneeFollowsHip", 0),
        ("MhaKneeFollowsFoot", 0),
        ("MhaArmHinge", 0),
        ]

    for (key, value) in permProps:
        rig[key+"_L"] = value
        rig[key+"_R"] = value
 
    layers = list(rig.data.layers)
    rig.data.layers = 32*[True]
    locks = []
    for pb in rig.pose.bones:
        constraints = []
        for cns in pb.constraints:
            if cns.type in ['LIMIT_ROTATION', 'LIMIT_SCALE']:
                constraints.append( (cns, cns.mute) )
                cns.mute = True
            elif cns.type == 'LIMIT_DISTANCE':
                cns.mute = True
        locks.append( (pb, list(pb.lock_location), list(pb.lock_rotation), list(pb.lock_scale), constraints) )
        pb.lock_location = [False, False, False]
        pb.lock_rotation = [False, False, False]
        pb.lock_scale = [False, False, False]
        
    norotBones = []    
    """
    if mcp.target == 'MHX':
        for (name, parent) in [("UpLegRot_L", "Hip_L"), ("UpLegRot_R", "Hip_R")]:
            try:
                anim.boneDatas[parent]
                isPermanent = True
            except:
                isPermanent = False
            b = rig.data.bones[name]
            if not isPermanent:
                norotBones.append(b)
            b.use_inherit_rotation = False
    """
    return (props, layers, locks, norotBones)

    
def restoreTargetData(rig, data):
    (props, rig.data.layers, locks, norotBones) = data
    
    for (key,value) in props:
        rig[key] = value

    for b in norotBones:
        b.use_inherit_rotation = True
    
    for lock in locks:
        (pb, lockLoc, lockRot, lockScale, constraints) = lock
        pb.lock_location = lockLoc
        pb.lock_rotation = lockRot
        pb.lock_scale = lockScale
        for (cns, mute) in constraints:
            cns.mute = mute
            
    return        
        

#########################################
#
#   FK-IK snapping. 
#
#########################################

def updateScene():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def getPoseMatrix(mat, pb):
    restInv = pb.bone.matrix_local.inverted()
    if pb.parent:
        parInv = pb.parent.matrix.inverted()
        parRest = pb.parent.bone.matrix_local
        return restInv * (parRest * (parInv * mat))
    else:
        return restInv * mat

        
def getGlobalMatrix(mat, pb):
    gmat = pb.bone.matrix_local * mat
    if pb.parent:
        parMat = pb.parent.matrix
        parRest = pb.parent.bone.matrix_local
        return parMat * (parRest.inverted() * gmat)
    else:
        return gmat


def matchPoseTranslation(pb, fkPb, frame):
    mat = getPoseMatrix(fkPb.matrix, pb)
    insertLocation(pb, mat, frame)
    

def insertLocation(pb, mat, frame):    
    pb.location = mat.to_translation()
    pb.keyframe_insert("location", frame=frame, group=pb.name)


def matchPoseRotation(pb, fkPb, frame):
    mat = getPoseMatrix(fkPb.matrix, pb)
    insertRotation(pb, mat, frame)
    

def insertRotation(pb, mat, frame):    
    q = mat.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", frame=frame, group=pb.name)
    else:
        pb.rotation_euler = q.to_euler(pb.rotation_mode)
        pb.keyframe_insert("rotation_euler", frame=frame, group=pb.name)


def matchPoseLocRot(pb, fkPb, frame):
    mat = getPoseMatrix(fkPb.matrix, pb)
    insertLocation(pb, mat, frame)
    insertRotation(pb, mat, frame)


def makePlanar(pb, rig, frame):
    master = rig.pose.bones["MasterFloor"]
    mmat = master.matrix.to_3x3()
    pmat = pb.parent.matrix.to_3x3()
    phead = pb.parent.matrix.to_translation()
    ptail = phead + pmat.col[1]*pb.parent.bone.length
    
    zmaster = mmat.col[2]
    yvec = pmat.col[1].copy()
    proj = zmaster.dot(yvec)
    ymax = 0
    ymin = -0.5
    if proj > ymax:
        proj = ymax
    elif proj < 2*ymin:
        proj = 0
    elif proj < ymin:
        proj = 2*ymin-proj
    yvec -= proj*zmaster    
    yvec.normalize()
    xvec = pmat.col[0].normalized()
    zvec = xvec.cross(yvec)
    head = ptail - yvec*pb.bone.length
    
    nmat = Matrix()
    for i in range(3):
        nmat[i][0] = xvec[i]
        nmat[i][1] = yvec[i]
        nmat[i][2] = zvec[i]
        nmat[i][3] = head[i]
    mat = getPoseMatrix(nmat, pb)
    insertRotation(pb, mat, frame)
    insertLocation(pb, mat, frame)  
    

def matchPoseReverse(pb, fkPb, frame):
    updateScene()
    mat = getPoseMatrix(fkPb.matrix, pb)
    mat = mat * Matrix.Rotation(math.pi, 4, 'Z')
    mat[1][3] -= pb.bone.length
    pb.matrix_basis = mat
    insertLocation(pb, mat, frame)
    insertRotation(pb, mat, frame)
    

def matchPoseScale(pb, fkPb, frame):
    mat = getPoseMatrix(fkPb.matrix, pb)
    pb.scale = mat.to_scale()
    #pb.keyframe_insert("scale", frame=frame, group=pb.name)


def ik2fkArm(rig, ikBones, fkBones, suffix, frame):
    (uparmIk, loarmIk, elbow, elbowPt, wrist) = ikBones
    (uparmFk, loarmFk, elbowPtFk, handFk) = fkBones
    matchPoseLocRot(wrist, handFk, frame)
    matchPoseTranslation(elbow, elbowPtFk, frame)
    matchPoseTranslation(elbowPt, elbowPtFk, frame)
    return


def ik2fkLeg(rig, ikBones, fkBones, legIkToAnkle, suffix, frame, first):
    (uplegIk, lolegIk, kneePt, ankleIk, legIk, legFk, footIk, toeIk) = ikBones
    (uplegFk, lolegFk, kneePtFk, footFk, toeFk) = fkBones

    makePlanar(legFk, rig, frame)
    updateScene()
    #halt
    matchPoseLocRot(legIk, legFk, frame)
    matchPoseReverse(toeIk, toeFk, frame)
    matchPoseReverse(footIk, footFk, frame)
    matchPoseTranslation(kneePt, kneePtFk, frame)
    if True or legIkToAnkle or first:
        matchPoseTranslation(ankleIk, footFk, frame)
    #halt
    return
   
   
def retargetIkBones(rig, frame, first):
    if mcp.target == 'MHX':
        lArmIkBones = getSnapBones(rig, "ArmIK", "_L")
        lArmFkBones = getSnapBones(rig, "ArmFK", "_L")
        rArmIkBones = getSnapBones(rig, "ArmIK", "_R")
        rArmFkBones = getSnapBones(rig, "ArmFK", "_R")
        lLegIkBones = getSnapBones(rig, "LegIK", "_L")
        lLegFkBones = getSnapBones(rig, "LegFK", "_L")
        rLegIkBones = getSnapBones(rig, "LegIK", "_R")
        rLegFkBones = getSnapBones(rig, "LegFK", "_R")

        ik2fkArm(rig, lArmIkBones, lArmFkBones, "_L", frame)
        ik2fkArm(rig, rArmIkBones, rArmFkBones, "_R", frame)
        ik2fkLeg(rig, lLegIkBones, lLegFkBones, rig["MhaLegIkToAnkle_L"], "_L", frame, first)
        ik2fkLeg(rig, rLegIkBones, rLegFkBones, rig["MhaLegIkToAnkle_R"], "_R", frame, first)
    else:
        for (ik,fk) in mcp.ikBones:
            ikPb = rig.pose.bones[ik]
            fkPb = rig.pose.bones[fk]
            matchPoseTranslation(ikPb, fkPb, frame)  
            matchPoseRotation(ikPb, fkPb, frame)          
    return        
        
#
#
#

SnapBones = {
    "ArmFK" : ["UpArm", "LoArm", "ElbowPTFK", "Hand"],
    "ArmIK" : ["UpArmIK", "LoArmIK", "Elbow", "ElbowPT", "Wrist"],
    "LegFK" : ["UpLeg", "LoLeg", "KneePTFK", "Foot", "Toe"],
    "LegIK" : ["UpLegIK", "LoLegIK", "KneePT", "Ankle", "LegIK", "LegFK", "FootRev", "ToeRev"],
}

def getSnapBones(rig, key, suffix):
    names = SnapBones[key]
    pbones = []
    for name in names:
        pb = rig.pose.bones[name+suffix]
        pbones.append(pb)
    return tuple(pbones)

#
#    loadRetargetSimplify(context, filepath):
#

def loadRetargetSimplify(context, filepath):
    print("Load and retarget %s" % filepath)
    time1 = time.clock()
    scn = context.scene
    (srcRig, trgRig) = load.readBvhFile(context, filepath, scn, False)
    load.renameAndRescaleBvh(context, srcRig, trgRig)
    retargetMhxRig(context, srcRig, trgRig, True, scn.McpRetargetIK)
    scn = context.scene
    if scn.McpDoSimplify:
        simplify.simplifyFCurves(context, trgRig, False, False)
    if scn.McpRescale:
        simplify.rescaleFCurves(context, trgRig, scn.McpRescaleFactor)
    load.deleteSourceRig(context, srcRig, 'Y_')
    time2 = time.clock()
    print("%s finished in %.3f s" % (filepath, time2-time1))
    return


########################################################################
#
#   Buttons
#

class VIEW3D_OT_NewRetargetMhxButton(bpy.types.Operator):
    bl_idname = "mcp.new_retarget_mhx"
    bl_label = "Retarget Selected To Active"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            trgRig = context.object
            scn = context.scene
            target.getTargetArmature(trgRig, scn)
            for srcRig in context.selected_objects:
                if srcRig != trgRig:
                    retargetMhxRig(context, srcRig, trgRig, True, scn.McpRetargetIK)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    


class VIEW3D_OT_RetargetIKButton(bpy.types.Operator):
    bl_idname = "mcp.retarget_ik"
    bl_label = "Retarget IK Bones"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            rig = context.object
            scn = context.scene
            target.getTargetArmature(rig, scn)
            retargetMhxRig(context, rig, rig, False, True)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    


class VIEW3D_OT_LoadAndRetargetButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_and_retarget"
    bl_label = "Load And Retarget"
    bl_options = {'UNDO'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        try:
            loadRetargetSimplify(context, self.properties.filepath)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}    

