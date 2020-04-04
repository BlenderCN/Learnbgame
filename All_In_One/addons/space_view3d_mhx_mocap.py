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

"""
Abstract
Tool for loading bvh files onto the MHX rig in Blender 2.5x
Version 0.6

Place the script in the .blender/scripts/addons dir
Activate the script in the "Add-Ons" tab (user preferences).
Access from UI panel (N-key) when MHX rig is active.

Alternatively, run the script in the script editor (Alt-P), and access from UI panel.
"""

bl_info = {
    "name": "MHX Mocap",
    "author": "Thomas Larsson",
    "version": "0.8",
    "blender": (2, 5, 8),
    "api": 38726,
    "location": "View3D > Properties > MHX Mocap",
    "description": "Mocap tool for MHX rig",
    "warning": "",
    'wiki_url': 'http://sites.google.com/site/makehumandocs/blender-export-and-mhx/mocap-tool',
    "category": "Learnbgame",
}

"""
Properties:
Scale:    
    for BVH import. Choose scale so that the vertical distance between hands and feet
    are the same for MHX and BVH rigs.
    Good values are: CMU: 0.6, Accad: 0.1
Start frame:    
    for BVH import
Rot90:    
    for BVH import. Rotate armature 90 degrees, so Z points up.
Simplify FCurves:    
    Include FCurve simplifcation.
Max loc error:    
    Max error allowed for simplification of location FCurves
Max rot error:    
    Max error allowed for simplification of rotation FCurves

Buttons:
Load BVH file (.bvh): 
    Load bvh file with Z up
Silence constraints:
    Turn off constraints that may conflict with mocap data.
Retarget selected to MHX: 
    Retarget actions of selected BVH rigs to the active MHX rig.
Simplify FCurves:
    Simplifiy FCurves of active action, allowing max errors specified above.
Load, retarget, simplify:
    Load bvh file, retarget the action to the active MHX rig, and simplify FCurves.
Batch run:
    Load all bvh files in the given directory, whose name start with the
    given prefix, and create actions (with simplified FCurves) for the active MHX rig.
"""

import bpy, os, mathutils, math, time
from math import sin, cos
from mathutils import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

###################################################################################
#    BVH importer. 
#    The importer that comes with Blender had memory leaks which led to instability.
#    It also creates a weird skeleton from CMU data, with hands theat start at the wrist
#    and ends at the elbow.
#

#
#    class CNode:
#

class CNode:
    def __init__(self, words, parent):
        name = words[1]
        for word in words[2:]:
            name += ' '+word
        
        self.name = name
        self.parent = parent
        self.children = []
        self.head = Vector((0,0,0))
        self.offset = Vector((0,0,0))
        if parent:
            parent.children.append(self)
        self.channels = []
        self.matrix = None
        self.inverse = None
        return

    def __repr__(self):
        return "CNode %s" % (self.name)

    def display(self, pad):
        vec = self.offset
        if vec.length < Epsilon:
            c = '*'
        else:
            c = ' '
        print("%s%s%10s (%8.3f %8.3f %8.3f)" % (c, pad, self.name, vec[0], vec[1], vec[2]))
        for child in self.children:
            child.display(pad+"  ")
        return

    def build(self, amt, orig, parent):
        self.head = orig + self.offset
        if not self.children:
            return self.head
        
        zero = (self.offset.length < Epsilon)
        eb = amt.edit_bones.new(self.name)        
        if parent:
            eb.parent = parent
        eb.head = self.head
        tails = Vector((0,0,0))
        for child in self.children:
            tails += child.build(amt, self.head, eb)
        n = len(self.children)
        eb.tail = tails/n
        #self.matrix = eb.matrix.rotation_part()
        (loc, rot, scale) = eb.matrix.decompose()
        self.matrix = rot.to_matrix()
        self.inverse = self.matrix.copy()
        self.inverse.invert()        
        if zero:
            return eb.tail
        else:        
            return eb.head

#
#    readBvhFile(context, filepath, scn, scan):
#    Custom importer
#

Location = 1
Rotation = 2
Hierarchy = 1
Motion = 2
Frames = 3

Deg2Rad = math.pi/180
Epsilon = 1e-5

def readBvhFile(context, filepath, scn, scan):
    global theTarget
    ensureInited(context)
    scale = scn['MhxBvhScale']
    startFrame = scn['MhxStartFrame']
    endFrame = scn['MhxEndFrame']
    rot90 = scn['MhxRot90Anim']
    subsample = scn['MhxSubsample']
    defaultSS = scn['MhxDefaultSS']
    print(filepath)
    fileName = os.path.realpath(os.path.expanduser(filepath))
    (shortName, ext) = os.path.splitext(fileName)
    if ext.lower() != ".bvh":
        raise NameError("Not a bvh file: " + fileName)
    print( "Loading BVH file "+ fileName )

    trgRig = context.object
    bpy.ops.object.mode_set(mode='POSE')
    trgPbones = trgRig.pose.bones

    time1 = time.clock()
    level = 0
    nErrors = 0
    scn = context.scene
            
    fp = open(fileName, "rU")
    print( "Reading skeleton" )
    lineNo = 0
    for line in fp: 
        words= line.split()
        lineNo += 1
        if len(words) == 0:
            continue
        key = words[0].upper()
        if key == 'HIERARCHY':
            status = Hierarchy
        elif key == 'MOTION':
            if level != 0:
                raise NameError("Tokenizer out of kilter %d" % level)    
            if scan:
                return root
            guessTargetArmature(trgRig)
            amt = bpy.data.armatures.new("BvhAmt")
            rig = bpy.data.objects.new("BvhRig", amt)
            scn.objects.link(rig)
            scn.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='EDIT')
            root.build(amt, Vector((0,0,0)), None)
            #root.display('')
            bpy.ops.object.mode_set(mode='OBJECT')
            status = Motion
            print("Reading motion")
        elif status == Hierarchy:
            if key == 'ROOT':    
                node = CNode(words, None)
                root = node
                nodes = [root]
            elif key == 'JOINT':
                node = CNode(words, node)
                nodes.append(node)
            elif key == 'OFFSET':
                (x,y,z) = (float(words[1]), float(words[2]), float(words[3]))
                if rot90:                    
                    node.offset = scale*Vector((x,-z,y))
                else:
                    node.offset = scale*Vector((x,y,z))
            elif key == 'END':
                node = CNode(words, node)
            elif key == 'CHANNELS':
                oldmode = None
                for word in words[2:]:
                    if rot90:
                        (index, mode, sign) = channelZup(word)
                    else:
                        (index, mode, sign) = channelYup(word)
                    if mode != oldmode:
                        indices = []
                        node.channels.append((mode, indices))
                        oldmode = mode
                    indices.append((index, sign))
            elif key == '{':
                level += 1
            elif key == '}':
                level -= 1
                node = node.parent
            else:
                raise NameError("Did not expect %s" % words[0])
        elif status == Motion:
            if key == 'FRAMES:':
                nFrames = int(words[1])
            elif key == 'FRAME' and words[1].upper() == 'TIME:':
                frameTime = float(words[2])
                frameFactor = int(1.0/(25*frameTime) + 0.49)
                if defaultSS:
                    subsample = frameFactor
                status = Frames
                frame = 0
                frameno = 1

                findSrcArmature(context, rig)
                bpy.ops.object.mode_set(mode='POSE')
                pbones = rig.pose.bones
                for pb in pbones:
                    #try:
                    #    trgName = theArmature[pb.name.lower()]
                    #    pb.rotation_mode = trgPbones[trgName].rotation_mode
                    #except:
                    pb.rotation_mode = 'QUATERNION'
        elif status == Frames:
            if (frame >= startFrame and
                frame <= endFrame and
                frame % subsample == 0):
                addFrame(words, frameno, nodes, pbones, scale)
                if frameno % 200 == 0:
                    print(frame)
                frameno += 1
            frame += 1

    fp.close()
    setInterpolation(rig)
    time2 = time.clock()
    print("Bvh file loaded in %.3f s" % (time2-time1))
    return rig

#
#    addFrame(words, frame, nodes, pbones, scale):
#

def addFrame(words, frame, nodes, pbones, scale):
    m = 0
    first = True
    for node in nodes:
        name = node.name
        try:
            pb = pbones[name]
        except:
            pb = None
        if pb:
            for (mode, indices) in node.channels:
                if mode == Location:
                    vec = Vector((0,0,0))
                    for (index, sign) in indices:
                        vec[index] = sign*float(words[m])
                        m += 1
                    if first:
                        pb.location = node.inverse * (scale * vec - node.head)
                        for n in range(3):
                            pb.keyframe_insert('location', index=n, frame=frame, group=name)
                    first = False
                elif mode == Rotation:
                    mats = []
                    for (axis, sign) in indices:
                        angle = sign*float(words[m])*Deg2Rad
                        mats.append(Matrix.Rotation(angle, 3, axis))
                        m += 1
                    mat = node.inverse * mats[0] * mats[1] * mats[2] * node.matrix
                    setRotation(pb, mat, frame, name)

    return

#
#    channelYup(word):
#    channelZup(word):
#

def channelYup(word):
    if word == 'Xrotation':
        return ('X', Rotation, +1)
    elif word == 'Yrotation':
        return ('Y', Rotation, +1)
    elif word == 'Zrotation':
        return ('Z', Rotation, +1)
    elif word == 'Xposition':
        return (0, Location, +1)
    elif word == 'Yposition':
        return (1, Location, +1)
    elif word == 'Zposition':
        return (2, Location, +1)

def channelZup(word):
    if word == 'Xrotation':
        return ('X', Rotation, +1)
    elif word == 'Yrotation':
        return ('Z', Rotation, +1)
    elif word == 'Zrotation':
        return ('Y', Rotation, -1)
    elif word == 'Xposition':
        return (0, Location, +1)
    elif word == 'Yposition':
        return (2, Location, +1)
    elif word == 'Zposition':
        return (1, Location, -1)

#
#     end Bvh importer
###################################################################################

###################################################################################
#
#    Supported source armatures

#
#    OsuArmature
#    www.accad.osu.edu/research/mocap/mocap_data.htm
#

OsuArmature = {
    'hips' : 'Root',
    'tospine' : 'Spine1',
    'spine' : 'Spine2',
    'spine1' : 'Spine3', 
    'neck' : 'Neck', 
    'head' : 'Head', 

    'leftshoulder' : 'Clavicle_L',
    'leftarm' : 'UpArm_L', 
    'leftforearm' : 'LoArm_L',
    'lefthand' : 'Hand_L', 

    'rightshoulder' : 'Clavicle_R',
    'rightarm' : 'UpArm_R', 
    'rightforearm' : 'LoArm_R',
    'righthand' : 'Hand_R',

    'leftupleg' : 'UpLeg_L', 
    'leftleg' : 'LoLeg_L', 
    'leftfoot' : 'Foot_L', 
    'lefttoebase' : 'Toe_L',

    'rightupleg' : 'UpLeg_R',
    'rightleg' : 'LoLeg_R', 
    'rightfoot' : 'Foot_R', 
    'righttoebase' : 'Toe_R',
}

#
#    MBArmature
#

MBArmature = {
    'hips' : 'Root', 
    'lowerback' : 'Spine1',
    'spine' : 'Spine2', 
    'spine1' : 'Spine3',
    'neck' : 'Neck',
    'neck1' : 'Head', 
    'head' : None,

    'leftshoulder' : 'Clavicle_L',
    'leftarm' : 'UpArm_L', 
    'leftforearm' : 'LoArm_L',
    'lefthand' : 'Hand_L',
    'lefthandindex1' : None,
    'leftfingerbase' : None,
    'lfingers' : None,
    'lthumb' : None, 

    'rightshoulder' : 'Clavicle_R', 
    'rightarm' : 'UpArm_R', 
    'rightforearm' : 'LoArm_R',
    'righthand' : 'Hand_R',
    'righthandindex1' : None,
    'rightfingerbase' : None,
    'rfingers' : None,
    'rthumb' : None, 

    'lhipjoint' : 'Hip_L', 
    'leftupleg' : 'UpLeg_L',
    'leftleg' : 'LoLeg_L', 
    'leftfoot' : 'Foot_L', 
    'lefttoebase' : 'Toe_L',

    'rhipjoint' : 'Hip_R', 
    'rightupleg' : 'UpLeg_R',
    'rightleg' : 'LoLeg_R', 
    'rightfoot' : 'Foot_R', 
    'righttoebase' : 'Toe_R',
}

#
#    MegaArmature
#

MegaArmature = {
    'hip' : 'Root', 
    'abdomen' : 'Spine1',
    'chest' : 'Spine3',
    'neck' : 'Neck',
    'head' : 'Head', 
    'left eye' : None,
    'right eye' : None,

    'left collar' : 'Clavicle_L',
    'left shoulder' : 'UpArm_L', 
    'left forearm' : 'LoArm_L',
    'left hand' : 'Hand_L',
    'left thumb 1' : None, 
    'left thumb 2' : None, 
    'left thumb 3' : None, 
    'left index 1' : None, 
    'left index 2' : None, 
    'left index 3' : None, 
    'left mid 1' : None, 
    'left mid 2' : None, 
    'left mid 3' : None, 
    'left ring 1' : None, 
    'left ring 2' : None, 
    'left ring 3' : None, 
    'left pinky 1' : None, 
    'left pinky 2' : None, 
    'left pinky 3' : None, 

    'right collar' : 'Clavicle_R',
    'right shoulder' : 'UpArm_R', 
    'right forearm' : 'LoArm_R',
    'right hand' : 'Hand_R',
    'right thumb 1' : None, 
    'right thumb 2' : None, 
    'right thumb 3' : None, 
    'right index 1' : None, 
    'right index 2' : None, 
    'right index 3' : None, 
    'right mid 1' : None, 
    'right mid 2' : None, 
    'right mid 3' : None, 
    'right ring 1' : None, 
    'right ring 2' : None, 
    'right ring 3' : None, 
    'right pinky 1' : None, 
    'right pinky 2' : None, 
    'right pinky 3' : None, 

    'left thigh' : 'UpLeg_L',
    'left shin' : 'LoLeg_L', 
    'left foot' : 'Foot_L', 
    'left toe' : 'Toe_L',

    'right thigh' : 'UpLeg_R',
    'right shin' : 'LoLeg_R', 
    'right foot' : 'Foot_R', 
    'right toe' : 'Toe_R',
}

HDMArmature = {
    'hip' : 'Root',
    'lhipjoint' : 'Hip_L',
    'lfemur' : 'UpLeg_L',
    'ltibia' : 'LoLeg_L',
    'lfoot' : 'Foot_L',
    'ltoes' : 'Toe_L',
    'rhipjoint' : 'Hip_R',
    'rfemur' : 'UpLeg_R',
    'rtibia' : 'LoLeg_R',
    'rfoot' : 'Foot_R',
    'rtoes' : 'Toe_R',
    'lowerback' : 'Spine1',
    'upperback' : 'Spine2',
    'thorax' : 'Spine3',
    'lowerneck' : 'LowerNeck',
    'upperneck' : 'Neck',
    'head' : 'Head',
    'lclavicle' : 'Clavicle_L',
    'lhumerus' : 'UpArm_L',
    'lradius' : 'LoArm_L',
    'lwrist' : 'Hand0_L',
    'lhand' : 'Hand_L',
    'lfingers' : None,
    'lthumb' : 'Finger1_L',
    'rclavicle' : 'Clavicle_R',
    'rhumerus' : 'UpArm_R',
    'rradius' : 'LoArm_R',
    'rwrist' : 'Hand0_R',
    'rhand' : 'Hand_R',
    'rfingers' : None,
    'rthumb' : 'Finger1_R',
}

EyesArmature = {
    'hips' : 'Root',
    'lefthip' : 'UpLeg_L',
    'leftknee' : 'LoLeg_L',
    'leftankle' : 'Foot_L',
    'righthip' : 'UpLeg_R',
    'rightknee' : 'LoLeg_R',
    'rightankle' : 'Foot_R',
    'chest' : 'Spine1',
    'chest2' : 'Spine2',
    'cs_bvh' : 'Spine3',
    'leftcollar' : 'Clavicle_L',
    'leftshoulder' : 'UpArm_L',
    'leftelbow' : 'LoArm_L',
    'leftwrist' : 'Hand_L',
    'rightcollar' : 'Clavicle_R',
    'rightshoulder' : 'UpArm_R',
    'rightelbow' : 'LoArm_R',
    'rightwrist' : 'Hand_R',
    'neck' : 'Neck',
    'head' : 'Head',
}

MaxArmature = {
    'hips' : 'Root',

    'lhipjoint' : 'Hip_L',
    'lefthip' : 'UpLeg_L',
    'leftknee' : 'LoLeg_L',
    'leftankle' : 'Foot_L',
    'lefttoe' : 'Toe_L',

    'rhipjoint' : 'Hip_R',
    'righthip' : 'UpLeg_R',
    'rightknee' : 'LoLeg_R',
    'rightankle' : 'Foot_R',
    'righttoe' : 'Toe_R',

    'lowerback' : 'Spine1',
    'chest' : 'Spine2',
    'chest2' : 'Spine3',
    'lowerneck' : 'LowerNeck',
    'neck' : 'Neck',
    'head' : 'Head',

    'leftcollar' : 'Clavicle_L',
    'leftshoulder' : 'UpArm_L',
    'leftelbow' : 'LoArm_L',
    'leftwrist' : 'Hand_L',
    'lhand' : None,
    'lfingers' : None,
    'lthumb' : None,

    'rightcollar' : 'Clavicle_R',
    'rightshoulder' : 'UpArm_R',
    'rightelbow' : 'LoArm_R',
    'rightwrist' : 'Hand_R',
    'rhand' : None,
    'rfingers' : None,
    'rthumb' : None,
}

DazArmature = {
    'hip' : 'Root', 
    'abdomen' : 'Spine1',

    'chest' : 'Spine3',
    'neck' : 'Neck',
    'head' : 'Head', 
    'lefteye' : None,
    'righteye' : None,
    'figurehair' : None,

    'lcollar' : 'Clavicle_L',
    'lshldr' : 'UpArm_L', 
    'lforearm' : 'LoArm_L',
    'lhand' : 'Hand_L',
    'lthumb1' : None, 
    'lthumb2' : None, 
    'lthumb3' : None, 
    'lindex1' : None, 
    'lindex2' : None, 
    'lindex3' : None, 
    'lmid1' : None, 
    'lmid2' : None, 
    'lmid3' : None, 
    'lring1' : None, 
    'lring2' : None, 
    'lring3' : None, 
    'lpinky1' : None, 
    'lpinky2' : None, 
    'lpinky3' : None, 

    'rcollar' : 'Clavicle_R',
    'rshldr' : 'UpArm_R', 
    'rforearm' : 'LoArm_R',
    'rhand' : 'Hand_R',
    'rthumb1' : None, 
    'rthumb2' : None, 
    'rthumb3' : None, 
    'rindex1' : None, 
    'rindex2' : None, 
    'rindex3' : None, 
    'rmid1' : None, 
    'rmid2' : None, 
    'rmid3' : None, 
    'rring1' : None, 
    'rring2' : None, 
    'rring3' : None, 
    'rpinky1' : None, 
    'rpinky2' : None, 
    'rpinky3' : None, 

    'lbuttock' : 'Hip_L',
    'lthigh' : 'UpLeg_L',
    'lshin' : 'LoLeg_L', 
    'lfoot' : 'Foot_L', 
    'ltoe' : 'Toe_L',

    'rbuttock' : 'Hip_R',
    'rthigh' : 'UpLeg_R',
    'rshin' : 'LoLeg_R', 
    'rfoot' : 'Foot_R', 
    'rtoe' : 'Toe_R',
}

theArmatures = {
    'MB' : MBArmature, 
    'Accad' : OsuArmature,
    'Mega' : MegaArmature,
    'HDM' : HDMArmature,
    '3dsMax' : MaxArmature,
    'Eyes' : EyesArmature,
    'Daz' : DazArmature,
}

theArmatureList = [ 'Accad', 'MB', 'Mega', 'HDM', 'Eyes', 'Daz', '3dsMax' ]

MBFixes = {
    'UpLeg_L' : ( Matrix.Rotation(0.4, 3, 'Y') * Matrix.Rotation(-0.45, 3, 'Z'), 0),
    'UpLeg_R' : ( Matrix.Rotation(-0.4, 3, 'Y') * Matrix.Rotation(0.45, 3, 'Z'), 0),
    'LoLeg_L' : ( Matrix.Rotation(-0.2, 3, 'Y'), 0),
    'LoLeg_R' : ( Matrix.Rotation(0.2, 3, 'Y'), 0),
    'Foot_L'  : ( Matrix.Rotation(-0.3, 3, 'Z'), 0),
    'Foot_R'  : ( Matrix.Rotation(0.3, 3, 'Z'), 0),
    #'UpArm_L' : ( Matrix.Rotation(0.1, 3, 'X'), 0),
    #'UpArm_R' : ( Matrix.Rotation(0.1, 3, 'X'), 0),
}

HDMFixes = {
    'UpLeg_L' : ( Matrix.Rotation(0.4, 3, 'Y') * Matrix.Rotation(-0.45, 3, 'Z'), 0),
    'UpLeg_R' : ( Matrix.Rotation(-0.4, 3, 'Y') * Matrix.Rotation(0.45, 3, 'Z'), 0),
    'LoLeg_L' : ( Matrix.Rotation(-0.4, 3, 'Y'), 0),
    'LoLeg_R' : ( Matrix.Rotation(0.4, 3, 'Y'), 0),
    'UpArm_L' : ( Matrix.Rotation(0.1, 3, 'X'), 0),
    'UpArm_R' : ( Matrix.Rotation(0.1, 3, 'X'), 0),
}

OsuFixes = {}

MegaFixes = {}

MaxFixes = {
    'UpLeg_L' : ( Matrix.Rotation(0.4, 3, 'Y') * Matrix.Rotation(-0.45, 3, 'Z'), 0),
    'UpLeg_R' : ( Matrix.Rotation(-0.4, 3, 'Y') * Matrix.Rotation(0.45, 3, 'Z'), 0),
    'LoLeg_L' : ( Matrix.Rotation(-0.3, 3, 'Y'), 0),
    'LoLeg_R' : ( Matrix.Rotation(0.3, 3, 'Y'), 0),
    #'Foot_L'  : ( Matrix.Rotation(-0.3, 3, 'Z'), 0),
    #'Foot_R'  : ( Matrix.Rotation(0.3, 3, 'Z'), 0),

    'UpArm_L' :  (Matrix.Rotation(1.57, 3, 'Z'), 1.57),
    'LoArm_L' :  (None, 1.57),
    'Hand_L'  :  (None, 1.57),
    'UpArm_R' :  (Matrix.Rotation(-1.57, 3, 'Z'), -1.57),
    'LoArm_R' :  (None, -1.57),
    'Hand_R'  :  (None, -1.57),
}

EyesFixes = {
    'Head2' : (Matrix.Rotation(0.2, 3, 'X'), 0),
    'Spine2' : (Matrix.Rotation(0.3, 3, 'X'), 0),
    'UpArm_L' :  (Matrix.Rotation(1.57, 3, 'Z')*Matrix.Rotation(-0.1, 3, 'X'), 1.57),
    'LoArm_L' :  (None, 1.57),
    'Hand_L' :  (None, 1.57),
    'UpArm_R' :  (Matrix.Rotation(-1.57, 3, 'Z')*Matrix.Rotation(-0.1, 3, 'X'), -1.57),
    'LoArm_R' :  (None, -1.57),
    'Hand_R' :  (None, -1.57),
}

DazFixes = {}

theFixesList = {
    'MB'  : MBFixes,
    'Accad' : OsuFixes,
    'Mega' : MegaFixes,
    'HDM' : HDMFixes,
    '3dsMax': MaxFixes,
    'Eyes': EyesFixes,
    'Daz' : DazFixes,
}

#
#    end supported source armatures
###################################################################################
#
#    Mhx rig
#

MhxFkBoneList = [
    'Root', 'Hips', 'Pelvis', 'Spine1', 'Spine2', 'Spine3', #'Shoulders', 
    'LowerNeck', 'Neck', 'Head', 'Sternum',
    'Clavicle_L', 'ShoulderEnd_L', 'Shoulder_L', 
    'UpArm_L', 'LoArm_L', 'Hand0_L', 'Hand_L',
    'Clavicle_R', 'ShoulderEnd_R', 'Shoulder_R', 
    'UpArm_R', 'LoArm_R', 'Hand0_R', 'Hand_R',
    'Hip_L', 'LegLoc_L', 'UpLeg_L', 'LoLeg_L', 'Foot_L', 'Toe_L', 'LegFK_L',
    'Hip_R', 'LegLoc_R', 'UpLeg_R', 'LoLeg_R', 'Foot_R', 'Toe_R', 'LegFK_R',
]

F_Rev = 1
F_LR = 2

#
#    theIkParent
#    bone : (realParent, fakeParent, copyRot, reverse)
#

MhxIkParents = {
    'Elbow_L' : (None, 'UpArm_L', None, False),
    'ElbowPT_L' : ('Clavicle_L', 'UpArm_L', None, False),
    'Wrist_L' : (None, 'LoArm_L', 'Hand_L', False),
    'LegIK_L' : (None, 'Toe_L', 'LegFK_L', False),
    'KneePT_L' : ('Hips', 'UpLeg_L', None, False),
    'ToeRev_L' : ('LegIK_L', 'Foot_L', 'Toe_L', True),
    'FootRev_L' : ('ToeRev_L', 'LoLeg_L', 'Foot_L', True),
    'Ankle_L' : ('FootRev_L', 'LoLeg_L', None, False),

    'Elbow_R' : (None, 'UpArm_R', None, False),
    'ElbowPT_R' : ('Clavicle_R', 'UpArm_R', None, False),
    'Wrist_R' : (None, 'LoArm_R', 'Hand_R', False),
    'LegIK_R' : (None, 'Toe_R', 'LegFK_R', False),
    'KneePT_R' : ('Hips', 'UpLeg_R', None, False),
    'ToeRev_R' : ('LegIK_R', 'Foot_R', 'Toe_R', True),
    'FootRev_R' : ('ToeRev_R', 'LoLeg_R', 'Foot_R', True),
    'Ankle_R' : ('FootRev_R', 'LoLeg_R', None, False),
}

MhxIkBoneList = [
    'Elbow_L', 'ElbowPT_L', 'Wrist_L',
    'LegIK_L', 'KneePT_L', # 'ToeRev_L', 'FootRev_L', 'Ankle_L',

    'Elbow_R', 'ElbowPT_R', 'Wrist_R',
    'LegIK_R', 'KneePT_R', # 'ToeRev_R', 'FootRev_R', 'Ankle_R',
]



MhxGlobalBoneList = [
    'Root', 
]

###################################################################################
#
#    Other supported target armatures
#
#    If you want to use the mocap tool for your own armature, it should suffice to 
#    modify this section (down to getParentName()).
#

T_MHX = 1
T_Rorkimaru = 2
T_Game = 3
T_Custom = 4
theTarget = 0
theArmature = None

RorkimaruBones = [
    ('Root',        'Root'),
    ('Spine1',        'Spine1'),
    ('Spine2',        'Spine3'),
    ('Neck',        'Neck'),
    ('Head',        'Head'),

    ('Clavicle_L',    'Clavicle_L'),
    ('UpArm_L',        'UpArm_L'),
    ('LoArm_L',        'LoArm_L'),
    ('Hand_L',        'Hand_L'),

    ('Clavicle_R',    'Clavicle_R'),
    ('UpArm_R',        'UpArm_R'),
    ('LoArm_R',        'LoArm_R'),
    ('Hand_R',        'Hand_R'),

    ('UpLeg_L',        'UpLeg_L'),
    ('LoLeg_L',        'LoLeg_L'),
    ('Foot_L',        'Foot_L'),
    ('Toe_L',        'Toe_L'),

    ('UpLeg_R',        'UpLeg_R'),
    ('LoLeg_R',        'LoLeg_R'),
    ('Foot_R',        'Foot_R'),
    ('Toe_R',        'Toe_R'),
]

GameBones = [
    ('Root',        'Root'),
    ('Spine1',        'Spine1'),
    ('Spine2',        'Spine2'),
    ('Spine3',        'Spine3'),
    ('Neck',        'Neck'),
    ('Head',        'Head'),

    ('Clavicle_L',    'Clavicle_L'),
    ('UpArm_L',        'UpArm_L'),
    ('LoArm_L',        'LoArm_L'),
    ('Hand_L',        'Hand_L'),

    ('Clavicle_R',    'Clavicle_R'),
    ('UpArm_R',        'UpArm_R'),
    ('LoArm_R',        'LoArm_R'),
    ('Hand_R',        'Hand_R'),

    ('UpLeg_L',        'UpLeg_L'),
    ('LoLeg_L',        'LoLeg_L'),
    ('Foot_L',        'Foot_L'),
    ('Toe_L',        'Toe_L'),

    ('UpLeg_R',        'UpLeg_R'),
    ('LoLeg_R',        'LoLeg_R'),
    ('Foot_R',        'Foot_R'),
    ('Toe_R',        'Toe_R'),
]

GameIkParents = {
    'Wrist_L' : (None, 'LoArm_L', 'Hand_L', False),
    'Ankle_L' : (None, 'LoLeg_L', None, False),
    'Wrist_R' : (None, 'LoArm_R', 'Hand_R', False),
    'Ankle_R' : (None, 'LoLeg_R', None, False),
}

GameIkBoneList = [ 'Wrist_L', 'Wrist_R', 'Ankle_L', 'Ankle_R' ]


#    bone : (realParent, fakeParent, copyRot, reverse)


#
#
#

GameNames = {
    'MasterFloor' :    None,
    'MasterFloorInv' :    None,
    'RootInv' :        'Root',
    'HipsInv' :        'Root',
    'Hips' :        'Root',
    'Spine3Inv' :    'Spine3',
}

RorkimaruNames = {
    'MasterFloor' :    None,
    'MasterFloorInv' :    None,
    'RootInv' :        'Root',
    'HipsInv' :        'Root',
    'Hips' :        'Root',
    'Spine2Inv' :    'Spine2',
    'Spine3' :        'Spine2',
}

#
#    getTrgBone(b):
#    getSrcBone(b):
#    getParentName(b):
#

def getTrgBone(b):
    if theTarget == T_MHX:
        return b
    else:
        try:
            return theTrgBone[b]
        except:
            return None
            
def getSrcBone(b):
    if theTarget == T_MHX:
        return b
    else:
        try:
            return theSrcBone[b]
        except:
            return None            

def getParentName(b):
    if b == None:
        return None
    elif theTarget == T_MHX:
        if b == 'MasterFloor':
            return None
        else:
            return b
    elif theTarget == T_Rorkimaru:
        try:
            return RorkimaruNames[b]
        except:
            return b
    elif theTarget == T_Game:
        try:
            return GameNames[b]
        except:
            return b
    else:
        return b

#
#    guessTargetArmature(trgRig):
#    setupTargetArmature():
#    testTargetRig(bones, rigBones):
#

def guessTargetArmature(trgRig):
    global theTarget, theFkBoneList, theIkBoneList, theGlobalBoneList, theIkParents
    global theSrcBone, theTrgBone, theParents, theTargetRolls, theTargetMats
    bones = trgRig.data.bones.keys()
    try:
        custom = trgRig['MhxTargetRig']
    except:
        custom = False
    if custom:
        theTarget = T_Custom
        name = "Custom %s" % trgRig.name
    elif 'KneePT_L' in bones:
        theTarget = T_MHX
        name = "MHX"
    elif testTargetRig(bones, GameBones):
        theTarget = T_Game
        name = "Game"
    elif testTargetRig(bones, RorkimaruBones):
        theTarget = T_Rorkimaru
        name = "Rorkimaru"
    else:
        print("Bones", bones)
        raise NameError("Did not recognize target armature")

    print("Target armature %s" % name)
    theParents = {}
    theTargetRolls = {}
    theTargetMats = {}

    if theTarget == T_MHX:
        theFkBoneList = MhxFkBoneList
        theIkBoneList = MhxIkBoneList
        theGlobalBoneList = MhxGlobalBoneList
        theIkParents = MhxIkParents
        for bone in trgRig.data.bones:
            try:
                roll = bone['Roll']
            except:
                roll = 0
            if abs(roll) > 0.1:
                theTargetRolls[bone.name] = roll
    else:
        theFkBoneList = []
        theGlobalBoneList = []

        theTrgBone = {}
        theSrcBone = {}
        if theTarget == T_Custom:
            (bones, theParents, theTargetRolls, theTargetMats, theIkBoneList, theIkParents) = makeTargetAssoc(trgRig)
        elif theTarget == T_Rorkimaru:
            bones = RorkimaruBones
            theIkBoneList = GameIkBoneList
            theIkParents = GameIkParents
        elif theTarget == T_Game:
            bones = GameBones
            theIkBoneList = GameIkBoneList
            theIkParents = GameIkParents
        else:
            raise NameError("Unknown target %s" % theTarget)
        for (trg,src) in bones:
            theFkBoneList.append(trg)
            theSrcBone[trg] = src
            theTrgBone[src] = trg
            if src in MhxGlobalBoneList:
                theGlobalBoneList.append(trg)
    return


def testTargetRig(bones, rigBones):
    for (b, mb) in rigBones:
        if b not in bones:
            print("Fail", b, mb)
            return False
    return True

#    end supported target armatures
###################################################################################

#            
#    class CEditBone():
#

class CEditBone():
    def __init__(self, bone):
        self.name = bone.name
        self.head = bone.head.copy()
        self.tail = bone.tail.copy()
        self.roll = bone.roll
        if bone.parent:
            self.parent = getParentName(bone.parent.name)
        else:
            self.parent = None
        if self.parent:
            self.use_connect = bone.use_connect
        else:
            self.use_connect = False
        #self.matrix = bone.matrix.copy().rotation_part()
        (loc, rot, scale) = bone.matrix.decompose()
        self.matrix = rot.to_matrix()
        self.inverse = self.matrix.copy()
        self.inverse.invert()

    def __repr__(self):
        return ("%s p %s\n  h %s\n  t %s\n" % (self.name, self.parent, self.head, self.tail))

#
#    renameBones(bones00, rig00, action):
#

def renameBones(bones00, rig00, action):
    bones90 = {}
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = rig00.data.edit_bones
    setbones = []
    for bone00 in bones00:
        name00 = bone00.name
        lname = name00.lower()
        try:
            name90 = theArmature[lname]
        except:
            name90 = theArmature[lname.replace(' ','_')]
        eb = ebones[name00]
        if name90:
            eb.name = name90
            bones90[name90] = CEditBone(eb)
            grp = action.groups[name00]
            grp.name = name90

            setbones.append((eb, name90))
        else:
            eb.name = '_' + name00
    for (eb, name) in setbones:
        eb.name = name
    #createExtraBones(ebones, bones90)
    bpy.ops.object.mode_set(mode='POSE')
    return

#
#    createExtraBones(ebones, bones90):
#

def createExtraBones(ebones, bones90):
    for suffix in ['_L', '_R']:
        try:
            foot = ebones['Foot'+suffix]
        except:
            foot = None
        try:
            toe = ebones['Toe'+suffix]
        except:
            toe = None

        if not toe:
            nameSrc = 'Toe'+suffix
            toe = ebones.new(name=nameSrc)
            toe.head = foot.tail
            toe.tail = toe.head - Vector((0, 0.5*foot.length, 0))
            toe.parent = foot
            bones90[nameSrc] = CEditBone(toe)
            
        nameSrc = 'Leg'+suffix
        eb = ebones.new(name=nameSrc)
        eb.head = 2*toe.head - toe.tail
        eb.tail = 4*toe.head - 3*toe.tail
        eb.parent = toe
        bones90[nameSrc] = CEditBone(eb)

        nameSrc = 'Ankle'+suffix
        eb = ebones.new(name=nameSrc)
        eb.head = foot.head
        eb.tail = 2*foot.head - foot.tail
        eb.parent = ebones['LoLeg'+suffix]
        bones90[nameSrc] = CEditBone(eb)
    return

#
#    makeVectorDict(ob, channels):
#

def makeVectorDict(ob, channels):
    fcuDict = {}
    for fcu in ob.animation_data.action.fcurves:
        words = fcu.data_path.split('"')
        if words[2] in channels:
            name = words[1]
            try:
                x = fcuDict[name]
            except:
                fcuDict[name] = []
            fcuDict[name].append((fcu.array_index, fcu))

    vecDict = {}
    for name in fcuDict.keys():
        fcuDict[name].sort()        
        (index, fcu) = fcuDict[name][0]
        m = len(fcu.keyframe_points)
        for (index, fcu) in fcuDict[name]:
            if len(fcu.keyframe_points) != m:
                raise NameError("Not all F-Curves for %s have the same length" % name)
        vectors = []
        for kp in range(m):
            vectors.append([])
        for (index, fcu) in fcuDict[name]:            
            n = 0
            for kp in fcu.keyframe_points:
                vectors[n].append(kp.co[1])
                n += 1
        vecDict[name] = vectors
    return vecDict
            
    
#
#    renameBvhRig(rig00, filepath):
#

def renameBvhRig(rig00, filepath):
    base = os.path.basename(filepath)
    (filename, ext) = os.path.splitext(base)
    print("File", filename, len(filename))
    if len(filename) > 12:
        words = filename.split('_')
        if len(words) == 1:
            words = filename.split('-')
        name = 'Y_'
        if len(words) > 1:
            words = words[1:]
        for word in words:
            name += word
    else:
        name = 'Y_' + filename
    print("Name", name)

    rig00.name = name
    action = rig00.animation_data.action
    action.name = name

    bones00 = []
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig00.data.edit_bones:
        bones00.append( CEditBone(bone) )
    bpy.ops.object.mode_set(mode='POSE')

    return (rig00, bones00, action)

#
#    copyAnglesIK():
#

def copyAnglesIK(context):
    trgRig = context.object
    guessTargetArmature(trgRig)
    trgAnimations = createTargetAnimation(context, trgRig)
    insertAnimation(context, trgRig, trgAnimations, theFkBoneList)
    onoff = toggleLimitConstraints(trgRig)
    setLimitConstraints(trgRig, 0.0)
    poseTrgIkBones(context, trgRig, trgAnimations)
    setInterpolation(trgRig)
    if onoff == 'OFF':
        setLimitConstraints(trgRig, 1.0)
    else:
        setLimitConstraints(trgRig, 0.0)
    return
    
#
#    guessSrcArmature(rig):
#    setArmature(rig)
#

def guessSrcArmature(rig):
    global theArmatures
    bestMisses = 1000
    misses = {}
    bones = rig.data.bones
    for name in theArmatureList:
        amt = theArmatures[name]
        nMisses = 0
        for bone in bones:
            try:
                amt[bone.name.lower()]
            except:
                nMisses += 1
        misses[name] = nMisses
        if nMisses < bestMisses:
            best = amt
            bestName = name
            bestMisses = nMisses
    if bestMisses > 0:
        for bone in bones:
            print("'%s'" % bone.name)
        for (name, n) in misses.items():
            print(name, n)
        raise NameError('Did not find matching armature. nMisses = %d' % bestMisses)
    return (best, bestName)

def findSrcArmature(context, rig):
    global theArmature, theArmatures
    if useCustomSrcRig(context):
        (theArmature, name, fixes) = buildSrcArmature(context, rig)
        theArmatures[name] = theArmature
        theFixesList[name] = fixes
    else:
        (theArmature, name) = guessSrcArmature(rig)
    rig['MhxArmature'] = name
    print("Using matching armature %s." % name)
    return

def setArmature(rig):
    global theArmature, theArmatures
    try:
        name = rig['MhxArmature']
    except:
        raise NameError("No armature set")
    theArmature = theArmatures[name]
    print("Set armature %s" % name)
    return
    
#
#    importAndRename(context, filepath):
#

def importAndRename(context, filepath):
    trgRig = context.object
    rig = readBvhFile(context, filepath, context.scene, False)
    (rig00, bones00, action) =  renameBvhRig(rig, filepath)
    findSrcArmature(context, rig00)
    renameBones(bones00, rig00, action)
    setInterpolation(rig00)
    rescaleRig(context.scene, trgRig, rig00, action)
    return (rig00, action)

#
#    rescaleRig(scn, trgRig, srcRig, action):
#

def rescaleRig(scn, trgRig, srcRig, action):
    if not scn['MhxAutoScale']:
        return
    upleg = getTrgBone('UpLeg_L')
    trgScale = trgRig.data.bones[upleg].length
    srcScale = srcRig.data.bones['UpLeg_L'].length
    scale = trgScale/srcScale
    print("Rescale %s with factor %f" % (scn.objects.active, scale))
    scn['MhxBvhScale'] = scale
    
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = srcRig.data.edit_bones
    for eb in ebones:
        oldlen = eb.length
        eb.head *= scale
        eb.tail *= scale
    bpy.ops.object.mode_set(mode='POSE')
    for fcu in action.fcurves:
        words = fcu.data_path.split('.')
        if words[-1] == 'location':
            for kp in fcu.keyframe_points:
                kp.co[1] *= scale
    return

#
#    class CAnimData():
#


class CAnimData():
    def __init__(self, name):
        self.nFrames = 0
        self.parent = None

        self.headRest = None
        self.vecRest = None
        self.tailRest = None
        self.roll = 0
        self.offsetRest = None
        self.matrixRest = None
        self.inverseRest = None

        self.heads = {}
        self.quats = {}
        self.matrices = {}
        self.name = name

    def __repr__(self):
        return "<CAnimData n %s p %s f %d>" % (self.name, self.parent, self.nFrames)

        
#
#    createSourceAnimation(context, rig):
#    createTargetAnimation(context, rig):
#    createAnimData(name, animations, ebones, isTarget):
#

def createSourceAnimation(context, rig):
    context.scene.objects.active = rig
    animations = {}
    for name in MhxFkBoneList:
        createAnimData(name, animations, rig.data.bones, False)
    return animations

def createTargetAnimation(context, rig):
    context.scene.objects.active = rig
    animations = {}
    for name in theFkBoneList+theIkBoneList:
        createAnimData(name, animations, rig.data.bones, True)
    return animations

def createAnimData(name, animations, bones, isTarget):
    try:
        b = bones[name]
    except:
        return
    anim = CAnimData(name)
    animations[name] = anim
    anim.headRest = b.head_local.copy()
    anim.tailRest = b.tail_local.copy()
    anim.vecRest = anim.tailRest - anim.headRest
    try:
        anim.roll = b['Roll']
    except:
        anim.roll = 0

    if isTarget and theTarget == T_Custom:
        anim.parent = theParents[name]
    elif b.parent:
        if isTarget:
            anim.parent = getParentName(b.parent.name)
        else:
            anim.parent = b.parent.name
    else:
        anim.parent = None

    if anim.parent:
        try:
            animPar = animations[anim.parent]
        except:
            animPar = None
    else:
        animPar = None

    #print("AD", isTarget, anim.name, anim.parent, animPar)

    if animPar:
        anim.offsetRest = anim.headRest - animPar.headRest
    else:
        anim.offsetRest = Vector((0,0,0))    

    (loc, rot, scale) = b.matrix_local.decompose()
    anim.matrixRest = rot.to_matrix()
    anim.inverseRest = anim.matrixRest.copy()
    anim.inverseRest.invert()
    return

#
#    insertAnimation(context, rig, animations, boneList):
#    insertAnimRoot(root, animations, nFrames, locs, rots):
#    insertAnimChild(name, animations, nFrames, rots):
#

def insertAnimation(context, rig, animations, boneList):
    context.scene.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    locs = makeVectorDict(rig, ['].location'])
    rots = makeVectorDict(rig, ['].rotation_quaternion', '].rotation_euler'])
    try:
        root = 'Root'
        nFrames = len(locs[root])
    except:
        root = getTrgBone('Root')
        nFrames = len(locs[root])
    insertAnimRoot(root, animations, nFrames, locs[root], rots[root])
    bones = rig.data.bones
    for nameSrc in boneList:
        try:
            bones[nameSrc]
            success = (nameSrc != root)
        except:
            success = False
        if success:
            try:
                rot = rots[nameSrc]
            except:
                rot = None
            insertAnimChild(nameSrc, animations, nFrames, rot)

def insertAnimRoot(root, animations, nFrames, locs, rots):
    anim = animations[root]
    if nFrames < 0:
        nFrames = len(locs)
    anim.nFrames = nFrames
    for frame in range(anim.nFrames):
        quat = Quaternion(rots[frame])
        anim.quats[frame] = quat
        matrix = anim.matrixRest * quat.to_matrix() * anim.inverseRest
        anim.matrices[frame] = matrix
        anim.heads[frame] =  anim.matrixRest * Vector(locs[frame]) + anim.headRest
    return

def insertAnimChildLoc(nameIK, name, animations, locs):
    animIK = animations[nameIK]
    anim = animations[name]
    animPar = animations[anim.parent]
    animIK.nFrames = anim.nFrames
    for frame in range(anim.nFrames):
        parmat = animPar.matrices[frame]
        animIK.heads[frame] = animPar.heads[frame] + anim.offsetRest * parmat
    return

def insertAnimChild(name, animations, nFrames, rots):
    try:
        anim = animations[name]
    except:
        return None
    if nFrames < 0:
        nFrames = len(rots)
    par = anim.parent
    #print("iAC", name, par)
    if par[0:3] == 'Dfm':
        par = par[3:]        
    try:
        animPar = animations[par]
    except:
        animPar = None
    if not animPar:
        raise NameError("Could not guess parent %s -> %s" % (name, par))

    anim.nFrames = nFrames
    quat = Quaternion()
    quat.identity()
    for frame in range(anim.nFrames):
        parmat = animPar.matrices[frame]
        if rots:
            try:
                quat = Quaternion(rots[frame])
            except:
                quat = Euler(rots[frame]).to_quaternion()
        anim.quats[frame] = quat
        locmat = anim.matrixRest * quat.to_matrix() * anim.inverseRest
        matrix = parmat * locmat
        anim.matrices[frame] = matrix
        anim.heads[frame] = animPar.heads[frame] + parmat*anim.offsetRest
    return anim
            
#
#    poseTrgFkBones(context, trgRig, srcAnimations, trgAnimations, srcFixes)
#

def poseTrgFkBones(context, trgRig, srcAnimations, trgAnimations, srcFixes):
    context.scene.objects.active = trgRig
    bpy.ops.object.mode_set(mode='POSE')
    pbones = trgRig.pose.bones
    
    nameSrc = 'Root'
    nameTrg = getTrgBone(nameSrc)
    insertLocationKeyFrames(nameTrg, pbones[nameTrg], srcAnimations[nameSrc], trgAnimations[nameTrg])
    for nameTrg in theFkBoneList:
        nameSrc = getSrcBone(nameTrg)
        trgRoll = safeGet(nameTrg, theTargetRolls)
        trgFix = safeGet(nameTrg, theTargetMats)
        try:
            pb = pbones[nameTrg]
            animSrc = srcAnimations[nameSrc]
            animTrg =  trgAnimations[nameTrg]
            success = True
        except:
            success = False
        if not success:
            pass
        elif (nameTrg in theGlobalBoneList) or (not pb.bone.use_inherit_rotation):
            print("global", pb)
            insertGlobalRotationKeyFrames(nameTrg, pb, animSrc, animTrg, trgRoll, trgFix)
        else:
            try:
                srcFix = srcFixes[nameSrc]
            except:
                srcFix = None
            if srcFix or trgFix:
                fixAndInsertLocalRotationKeyFrames(nameTrg, pb, animSrc, animTrg, srcFix, trgRoll, trgFix)
            else:
                insertLocalRotationKeyFrames(nameTrg, pb, animSrc, animTrg, trgRoll)

    insertAnimation(context, trgRig, trgAnimations, theFkBoneList)
    setInterpolation(trgRig)
    return

#
#    safeGet(name, struct):
#

def safeGet(name, struct):
    try:
        return struct[name]
    except:
        return None

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
        for n in range(4):
            pb.keyframe_insert('rotation_quaternion', index=n, frame=frame, group=group)
    else:
        try:
            euler = rot.to_euler(pb.rotation_mode)
        except:
            euler = rot
        pb.rotation_euler = euler
        for n in range(3):
            pb.keyframe_insert('rotation_euler', index=n, frame=frame, group=group)


#
#    insertLocationKeyFrames(name, pb, animSrc, animTrg):
#    insertGlobalRotationKeyFrames(name, pb, animSrc, animTrg, trgRoll, trgFix):
#

def insertLocationKeyFrames(name, pb, animSrc, animTrg):
    locs = []
    for frame in range(animSrc.nFrames):
        loc0 = animSrc.heads[frame] - animTrg.headRest
        loc = animTrg.inverseRest * loc0 
        locs.append(loc)
        pb.location = loc
        for n in range(3):
            pb.keyframe_insert('location', index=n, frame=frame, group=name)    
    return locs

def insertIKLocationKeyFrames(nameIK, name, pb, animations):
    pb.bone.select = True
    animIK = animations[nameIK]
    anim = animations[name]
    if animIK.parent:
        animPar = animations[animIK.parent]
    else:
        animPar = None
    locs = []
    for frame in range(anim.nFrames):        
        if animPar:
            loc0 = animPar.heads[frame] + animPar.matrices[frame]*animIK.offsetRest
            offset = anim.heads[frame] - loc0
            mat = animPar.matrices[frame] * animIK.matrixRest
            loc = offset*mat.invert()
        else:
            offset = anim.heads[frame] - animIK.headRest
            loc = offset * animIK.inverseRest
        pb.location = loc
        for n in range(3):
            pb.keyframe_insert('location', index=n, frame=frame, group=nameIK)    
    return


def insertGlobalRotationKeyFrames(name, pb, animSrc, animTrg, trgRoll, trgFix):
    rots = []
    animTrg.nFrames = animSrc.nFrames
    for frame in range(animSrc.nFrames):
        mat90 = animSrc.matrices[frame]
        animTrg.matrices[frame] = mat90
        matMhx = animTrg.inverseRest * mat90 * animTrg.matrixRest
        rot = matMhx.to_quaternion()
        rots.append(rot)
        setRotation(pb, rot, frame, name)
    return rots

def insertLocalRotationKeyFrames(name, pb, animSrc, animTrg, trgRoll):
    animTrg.nFrames = animSrc.nFrames
    for frame in range(animSrc.nFrames):
        rot = animSrc.quats[frame]
        rollRot(rot, trgRoll)
        animTrg.quats[frame] = rot
        setRotation(pb, rot, frame, name)
    return

def fixAndInsertLocalRotationKeyFrames(name, pb, animSrc, animTrg, srcFix, trgRoll, trgFix):
    (fixMat, srcRoll) = srcFix
    animTrg.nFrames = animSrc.nFrames
    for frame in range(animSrc.nFrames):
        matSrc = animSrc.quats[frame].to_matrix()
        if fixMat:
            matMhx = fixMat * matSrc
        else:
            matMhx = matSrc
        if trgFix:
            matTrg = trgFix * matMhx
        else:
            matTrg = matMhx
        rot = matMhx.to_quaternion()
        rollRot(rot, srcRoll)
        rollRot(rot, trgRoll)
        animTrg.quats[frame] = rot
        setRotation(pb, rot, frame, name)
    return



#
#    rollRot(rot, roll):
#

def rollRot(rot, roll):
    if not roll:
        return
    x = rot.x
    z = rot.z
    rot.x = x*cos(roll) - z*sin(roll)
    rot.z = x*sin(roll) + z*cos(roll)
    return

#
#    poseTrgIkBones(context, trgRig, trgAnimations)
#

def poseTrgIkBones(context, trgRig, trgAnimations):
    bpy.ops.object.mode_set(mode='POSE')
    pbones = trgRig.pose.bones

    for name in theIkBoneList:        
        (realPar, fakePar, copyRot, reverse) = theIkParents[name]
        pb = pbones[name]
        pb.bone.select = True
        if copyRot:
            animCopy = trgAnimations[copyRot]
        else:
            animCopy = None
        if reverse:    
            insertReverseIkKeyFrames(name, pb, trgAnimations[name],  trgAnimations[realPar], animCopy)
        elif realPar:
            insertParentedIkKeyFrames(name, pb, trgAnimations[name],  trgAnimations[realPar], trgAnimations[fakePar], animCopy)
        else:
            insertRootIkKeyFrames(name, pb, trgAnimations[name], trgAnimations[fakePar], animCopy)
    return
    
#
#    insertParentedIkKeyFrames(name, pb, anim, animReal, animFake, animCopy):
#

def insertParentedIkKeyFrames(name, pb, anim, animReal, animFake, animCopy):
    offsetFake = anim.headRest - animFake.headRest
    offsetReal = anim.headRest - animReal.headRest
    if animCopy:
        roll = anim.roll - animCopy.roll
    else:
        roll = 0
    for frame in range(animFake.nFrames):        
        locAbs = animFake.heads[frame] + animFake.matrices[frame]*offsetFake
        headAbs = animReal.heads[frame] + animReal.matrices[frame]*offsetReal
        #debugPrintVecVec(locAbs, headAbs)
        offset = locAbs - headAbs
        mat = animReal.matrices[frame] * anim.matrixRest
        if pb.bone.use_local_location:
            loc = mat.inverted() * offset
            pb.location = loc
        else:
            pb.location = offset
        anim.heads[frame] = locAbs
        for n in range(3):
            pb.keyframe_insert('location', index=n, frame=frame, group=name)    

        if animCopy:
            mat = mat * animCopy.inverseRest * animCopy.matrices[frame]
        anim.matrices[frame] = mat
        matMhx = anim.inverseRest * mat * anim.matrixRest
        rot = matMhx.to_quaternion()
        #rollRot(rot, roll)
        setRotation(pb, rot, frame, name)
    return

#
#    insertReverseIkKeyFrames(name, pb, anim, animReal, animCopy):
#
    
def vecString(vec):
    return "%.3f %.3f %.3f" % (vec[0], vec[1], vec[2])

def insertReverseIkKeyFrames(name, pb, anim, animReal, animCopy):
    offsetCopy = anim.headRest - animCopy.headRest
    offsetReal = anim.headRest - animReal.headRest
    rotX = Matrix.Rotation(math.pi, 3, 'X')
    #print("*** %s %s %s" % (name, vecString(animCopy.headRest), vecString(offsetCopy)))
    for frame in range(animCopy.nFrames):        
        locAbs = animCopy.heads[frame] + animCopy.matrices[frame]*offsetCopy
        headAbs = animReal.heads[frame] + animReal.matrices[frame]*offsetReal
        offset = locAbs - headAbs
        mat = animReal.matrices[frame] * anim.matrixRest
        if pb.bone.use_local_location:
            inv = mat.copy()
            inv.invert()
            loc = offset*inv
            pb.location = loc
        else:
            pb.location = offset
        anim.heads[frame] = locAbs
        for n in range(3):
            pb.keyframe_insert('location', index=n, frame=frame, group=name)    

        mat = mat * animCopy.inverseRest * animCopy.matrices[frame]
        anim.matrices[frame] = mat
        matMhx = rotX * anim.inverseRest * mat * anim.matrixRest * rotX
        rot = matMhx.to_quaternion()
        setRotation(pb, rot, frame, name)
    return

#
#    insertRootIkKeyFrames(name, pb, anim, animFake, animCopy):
#

def insertRootIkKeyFrames(name, pb, anim, animFake, animCopy):
    locs = []
    offsetFake = anim.headRest - animFake.headRest
    if animCopy:
        roll = anim.roll - animCopy.roll
    else:
        roll = 0
    for frame in range(animFake.nFrames):        
        locAbs = animFake.heads[frame] + animFake.matrices[frame]*offsetFake
        offset = locAbs - anim.headRest
        if pb.bone.use_local_location:
            loc = anim.inverseRest * offset
            pb.location = loc
        else:
            pb.location = offset
        anim.heads[frame] = locAbs
        for n in range(3):
            pb.keyframe_insert('location', index=n, frame=frame, group=name)    

        mat = anim.matrixRest
        if animCopy:
            mat = mat * animCopy.inverseRest * animCopy.matrices[frame] 
        anim.matrices[frame] = mat
        matMhx = anim.inverseRest * mat * anim.matrixRest
        rot = matMhx.to_quaternion()
        #rollRot(rot, roll)
        setRotation(pb, rot, frame, name)
    return


#
#    retargetMhxRig(context, srcRig, trgRig):
#

def retargetMhxRig(context, srcRig, trgRig):
    scn = context.scene
    setArmature(srcRig)
    print("Retarget %s --> %s" % (srcRig, trgRig))
    if trgRig.animation_data:
        trgRig.animation_data.action = None

    trgAnimations = createTargetAnimation(context, trgRig)
    srcAnimations = createSourceAnimation(context, srcRig)
    insertAnimation(context, srcRig, srcAnimations, MhxFkBoneList)
    onoff = toggleLimitConstraints(trgRig)
    setLimitConstraints(trgRig, 0.0)
    if scn['MhxApplyFixes']:
        srcFixes = theFixesList[srcRig['MhxArmature']]
    else:
        srcFixes = None
    #debugOpen()
    poseTrgFkBones(context, trgRig, srcAnimations, trgAnimations, srcFixes)
    poseTrgIkBones(context, trgRig, trgAnimations)
    #debugClose()
    setInterpolation(trgRig)
    if onoff == 'OFF':
        setLimitConstraints(trgRig, 1.0)
    else:
        setLimitConstraints(trgRig, 0.0)

    trgRig.animation_data.action.name = trgRig.name[:4] + srcRig.name[2:]
    print("Retargeted %s --> %s" % (srcRig, trgRig))
    return

#
#    deleteRig(context, rig00, action, prefix):
#

def deleteRig(context, rig00, action, prefix):
    context.scene.objects.unlink(rig00)
    if rig00.users == 0:
        bpy.data.objects.remove(rig00)
        #del rig00
    if bpy.data.actions:
        for act in bpy.data.actions:
            if act.name[0:2] == prefix:
                act.use_fake_user = False
                if act.users == 0:
                    bpy.data.actions.remove(act)
                    del act
    return

#
#    simplifyFCurves(context, rig, useVisible, useMarkers):
#

def simplifyFCurves(context, rig, useVisible, useMarkers):
    scn = context.scene
    if not scn.MhxDoSimplify:
        return
    print("WARNING: F-curve simplification turned off")
    return
    try:
        act = rig.animation_data.action
    except:
        act = None
    if not act:
        print("No action to simplify")
        return

    if useVisible:
        fcurves = []
        for fcu in act.fcurves:
            if not fcu.hide:
                fcurves.append(fcu)
                #print(fcu.data_path, fcu.array_index)
    else:
        fcurves = act.fcurves

    if useMarkers:
        (minTime, maxTime) = getMarkedTime(scn)        
        if minTime == None:    
            print("Need two selected markers")
            return
    else:
        (minTime, maxTime) = ('All', 0)

    curveInfo = []
    for fcu in fcurves:
        info = simplifyFCurve(fcu, act, scn.MhxErrorLoc, scn.MhxErrorRot, minTime, maxTime)
        curveInfo.append(info)
    for fcu in fcurves:
        act.fcurves.remove(fcu)
    for info in curveInfo:
        createNewFCurve(act, info)            
        
    setInterpolation(rig)
    print("Curves simplified")
    return

#
#    simplifyFCurve(fcu, act, maxErrLoc, maxErrRot, minTime, maxTime):
#

def simplifyFCurve(fcu, act, maxErrLoc, maxErrRot, minTime, maxTime):
    words = fcu.data_path.split('.')
    if words[-1] == 'location':
        maxErr = maxErrLoc
    elif words[-1] == 'rotation_quaternion':
        maxErr = maxErrRot * math.pi/180
    elif words[-1] == 'rotation_euler':
        maxErr = maxErrRot * math.pi/180
    else:
        raise NameError("Unknown FCurve type %s" % words[-1])

    if minTime == 'All':
        points = fcu.keyframe_points
        before = []
        after = []
    else:
        points = []
        before = []
        after = []
        for pt in fcu.keyframe_points:
            t = pt.co[0]
            if t < minTime:
                before.append(pt.co)
            elif t > maxTime:
                after.append(pt.co)
            else:
                points.append(pt)

    nPoints = len(points)
    if nPoints <= 2:
        return
    keeps = []
    new = [0, nPoints-1]
    while new:
        keeps += new
        keeps.sort()
        new = iterateFCurves(points, keeps, maxErr)
    newVerts = before
    for n in keeps:
        newVerts.append(points[n].co)
    newVerts += after
    return((fcu.data_path, fcu.array_index, fcu.group.name, newVerts))
    
def createNewFCurve(act, info):
    (path, index, grp, newVerts) = info
    print(path, index)
    nfcu = act.fcurves.new(path, index, grp)
    print(nfcu, nfcu.keyframe_points)
    for co in newVerts:
        t = co[0]
        try:
            dt = t - int(t)
        except:
            dt = 0.5
        if abs(dt) > 1e-5:
            pass
            # print(path, co, dt)
        else:
            print("  ", co)
            nfcu.keyframe_points.insert(frame=co[0], value=co[1])
    return

#
#    getMarkedTime(scn):
#

def getMarkedTime(scn):
    markers = []
    for mrk in scn.timeline_markers:
        if mrk.select:
            markers.append(mrk.frame)
    markers.sort()
    if len(markers) >= 2:
        return (markers[0], markers[-1])
    else:
        return (None, None)

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
#    plantKeys(context)
#    plantFCurves(fcurves, first, last):
#

def plantKeys(context):
    rig = context.object
    scn = context.scene
    if not rig.animation_data:
        print("Cannot plant: no animation data")
        return
    act = rig.animation_data.action
    if not act:
        print("Cannot plant: no action")
        return
    bone = rig.data.bones.active
    if not bone:
        print("Cannot plant: no active bone")
        return

    (first, last) = getMarkedTime(scn)
    if first == None:
        print("Cannot plant: need two selected time markers")
        return

    pb = rig.pose.bones[bone.name]
    locPath = 'pose.bones["%s"].location' % bone.name
    if pb.rotation_mode == 'QUATERNION':
        rotPath = 'pose.bones["%s"].rotation_quaternion' % bone.name
        pbRot = pb.rotation_quaternion
    else:
        rotPath = 'pose.bones["%s"].rotation_euler' % bone.name
        pbRot = pb.rotation_euler
    rots = []
    locs = []
    for fcu in act.fcurves:
        if fcu.data_path == locPath:
            locs.append(fcu)
        if fcu.data_path == rotPath:
            rots.append(fcu)

    useCrnt = scn['MhxPlantCurrent']
    if scn['MhxPlantLoc']:
        plantFCurves(locs, first, last, useCrnt, pb.location)
    if scn['MhxPlantRot']:
        plantFCurves(rots, first, last, useCrnt, pbRot)
    return

def plantFCurves(fcurves, first, last, useCrnt, values):
    for fcu in fcurves:
        print("Plant", fcu.data_path, fcu.array_index)
        kpts = fcu.keyframe_points
        sum = 0.0
        dellist = []
        firstx = first - 1e-4
        lastx = last + 1e-4
        print("Btw", firstx, lastx)
        for kp in kpts:
            (x,y) = kp.co
            if x > firstx and x < lastx:
                dellist.append(kp)
                sum += y
        nterms = len(dellist)
        if nterms == 0:
            return
        if useCrnt:
            ave = values[fcu.array_index]
            print("Current", ave)
        else:
            ave = sum/nterms
        for kp in dellist:
            kp.co[1] = ave
        kpts.insert(first, ave, options='FAST')
        kpts.insert(last, ave)
    return

#
#    iterateFCurves(points, keeps, maxErr):
#

def iterateFCurves(points, keeps, maxErr):
    new = []
    for edge in range(len(keeps)-1):
        n0 = keeps[edge]
        n1 = keeps[edge+1]
        (x0, y0) = points[n0].co
        (x1, y1) = points[n1].co
        if x1 > x0:
            dxdn = (x1-x0)/(n1-n0)
            dydx = (y1-y0)/(x1-x0)
            err = 0
            for n in range(n0+1, n1):
                (x, y) = points[n].co
                xn = n0 + dxdn*(n-n0)
                yn = y0 + dydx*(xn-x0)
                if abs(y-yn) > err:
                    err = abs(y-yn)
                    worst = n
            if err > maxErr:
                new.append(worst)
    return new
        
#
#    togglePoleTargets(trgRig):
#    toggleIKLimits(trgRig):
#    toggleLimitConstraints(trgRig):
#    setLimitConstraints(trgRig, inf):
#

def togglePoleTargets(trgRig):
    bones = trgRig.data.bones
    pbones = trgRig.pose.bones
    if bones['ElbowPT_L'].hide:
        hide = False
        poletar = trgRig
        res = 'ON'
        trgRig.MhxTogglePoleTargets = True
    else:
        hide = True
        poletar = None
        res = 'OFF'
        trgRig.MhxTogglePoleTargets = False
    for suffix in ['_L', '_R']:
        for name in ['ElbowPT', 'ElbowLinkPT', 'Elbow', 'KneePT', 'KneeLinkPT', 'Knee']:
            try:
                bones[name+suffix].hide = hide
            except:
                pass
        cns = pbones['LoArm'+suffix].constraints['ArmIK']
        cns = pbones['LoLeg'+suffix].constraints['LegIK']
        cns.pole_target = poletar
    return res

def toggleIKLimits(trgRig):
    pbones = trgRig.pose.bones
    if pbones['UpLeg_L'].use_ik_limit_x:
        use = False
        res = 'OFF'
        trgRig.MhxToggleIkLimits = False
    else:
        use = True
        res = 'ON'
        trgRig.MhxToggleIkLimits = True
    for suffix in ['_L', '_R']:
        for name in ['UpArm', 'LoArm', 'UpLeg', 'LoLeg']:
            pb = pbones[name+suffix]
            pb.use_ik_limit_x = use
            pb.use_ik_limit_y = use
            pb.use_ik_limit_z = use
    return res

def toggleLimitConstraints(trgRig):
    pbones = trgRig.pose.bones
    first = True
    trgRig.MhxToggleLimitConstraints = False
    for pb in pbones:
        if onUserLayer(pb.bone.layers):
            for cns in pb.constraints:
                if (cns.type == 'LIMIT_LOCATION' or
                    cns.type == 'LIMIT_ROTATION' or
                    cns.type == 'LIMIT_DISTANCE' or
                    cns.type == 'LIMIT_SCALE'):
                    if first:
                        first = False
                        if cns.influence > 0.5:
                            inf = 0.0
                            res = 'OFF'
                        else:
                            inf = 1.0
                            res = 'ON'
                            trgRig.MhxToggleLimitConstraints = True
                    cns.influence = inf
    if first:
        return 'NOT FOUND'
    return res

def onUserLayer(layers):
    for n in [0,1,2,3,4,5,6,7, 9,10,11,12,13]:
        if layers[n]:
            return True
    return False

def setLimitConstraints(trgRig, inf):
    pbones = trgRig.pose.bones
    for pb in pbones:
        if onUserLayer(pb.bone.layers):
            for cns in pb.constraints:
                if (cns.type == 'LIMIT_LOCATION' or
                    cns.type == 'LIMIT_ROTATION' or
                    cns.type == 'LIMIT_DISTANCE' or
                    cns.type == 'LIMIT_SCALE'):
                    cns.influence = inf
    return

#
#    silenceConstraints(rig):
#

def silenceConstraints(rig):
    for pb in rig.pose.bones:
        pb.lock_location = (False, False, False)
        pb.lock_rotation = (False, False, False)
        pb.lock_scale = (False, False, False)
        for cns in pb.constraints:
            if cns.type == 'CHILD_OF':
                cns.influence = 0.0
            elif False and (cns.type == 'LIMIT_LOCATION' or
                cns.type == 'LIMIT_ROTATION' or
                cns.type == 'LIMIT_DISTANCE' or
                cns.type == 'LIMIT_SCALE'):
                cns.influence = 0.0
    return

###################################################################################    
#    User interface
#
#    getBvh(mhx)
#    initInterface(context)
#

def getBvh(mhx):
    for (bvh, mhx1) in theArmature.items():
        if mhx == mhx1:
            return bvh
    return None

def initInterface(context):
    bpy.types.Scene.MhxBvhScale = FloatProperty(
        name="Scale", 
        description="Scale the BVH by this value", 
        min=0.0001, max=1000000.0, 
        soft_min=0.001, soft_max=100.0,
        default=0.65)

    bpy.types.Scene.MhxAutoScale = BoolProperty(
        name="Auto scale",
        description="Rescale skeleton to match target",
        default=True)

    bpy.types.Scene.MhxStartFrame = IntProperty(
        name="Start Frame", 
        description="Starting frame for the animation",
        default=1)

    bpy.types.Scene.MhxEndFrame = IntProperty(
        name="Last Frame", 
        description="Last frame for the animation",
        default=32000)

    bpy.types.Scene.MhxSubsample = IntProperty(
        name="Subsample", 
        description="Sample only every n:th frame",
        default=1)

    bpy.types.Scene.MhxDefaultSS = BoolProperty(
        name="Use default subsample",
        default=True)

    bpy.types.Scene.MhxRot90Anim = BoolProperty(
        name="Rotate 90 deg", 
        description="Rotate 90 degress so Z points up",
        default=True)

    bpy.types.Scene.MhxDoSimplify = BoolProperty(
        name="Simplify FCurves", 
        description="Simplify FCurves",
        default=True)

    bpy.types.Scene.MhxSimplifyVisible = BoolProperty(
        name="Only visible", 
        description="Simplify only visible F-curves",
        default=False)

    bpy.types.Scene.MhxSimplifyMarkers = BoolProperty(
        name="Only between markers", 
        description="Simplify only between markers",
        default=False)

    bpy.types.Scene.MhxApplyFixes = BoolProperty(
        name="Apply found fixes", 
        description="Apply found fixes",
        default=True)

    bpy.types.Scene.MhxPlantCurrent = BoolProperty(
        name="Use current", 
        description="Plant at current",
        default=True)

    bpy.types.Scene.MhxPlantLoc = BoolProperty(
        name="Loc", 
        description="Plant location keys",
        default=True)

    bpy.types.Scene.MhxPlantRot = BoolProperty(
        name="Rot", 
        description="Plant rotation keys",
        default=False)

    bpy.types.Scene.MhxErrorLoc = FloatProperty(
        name="Max loc error", 
        description="Max error for location FCurves when doing simplification",
        min=0.001,
        default=0.01)

    bpy.types.Scene.MhxErrorRot = FloatProperty(
        name="Max rot error", 
        description="Max error for rotation (degrees) FCurves when doing simplification",
        min=0.001,
        default=0.1)

    bpy.types.Scene.MhxDirectory = StringProperty(
        name="Directory", 
        description="Directory", 
        maxlen=1024,
        default='')

    bpy.types.Scene.MhxReallyDelete = BoolProperty(
        name="Really delete action", 
        description="Delete button deletes action permanently",
        default=False)

    bpy.types.Scene.MhxPrefix = StringProperty(
        name="Prefix", 
        description="Prefix", 
        maxlen=1024,
        default='')

    bpy.types.Scene.MhxActions = EnumProperty(
        items = [],
        name = "Actions")

    scn = context.scene
    if scn:
        scn['MhxPlantCurrent'] = True
        scn['MhxPlantLoc'] = True
        scn['MhxBvhScale'] = 0.65
        scn['MhxAutoScale'] = True
        scn['MhxStartFrame'] = 1
        scn['MhxEndFrame'] = 32000
        scn['MhxSubsample'] = 1
        scn['MhxDefaultSS'] = True
        scn['MhxRot90Anim'] = True
        scn['MhxDoSimplify'] = True
        scn['MhxSimplifyVisible'] = False
        scn['MhxSimplifyMarkers'] = False
        scn['MhxApplyFixes'] = True

        scn['MhxPlantLoc'] = True
        scn['MhxPlantRot'] = False
        scn['MhxErrorLoc'] = 0.01
        scn['MhxErrorRot'] = 0.1

        scn['MhxPrefix'] = "Female1_A"
        scn['MhxDirectory'] = "~/makehuman/bvh/Female1_bvh"
        scn['MhxReallyDelete'] = False
        listAllActions(context)
    else:
        print("Warning - no scene - scene properties not set")

    bpy.types.Object.MhxArmature = StringProperty()
    
    bpy.types.Object.MhxTogglePoleTargets = BoolProperty(default=True)
    bpy.types.Object.MhxToggleIkLimits = BoolProperty(default=False)
    bpy.types.Object.MhxToggleLimitConstraints = BoolProperty(default=True)


    '''
    for mhx in theFkBoneList:
        bpy.types.Scene.StringProperty(
            attr=mhx, 
            name=mhx, 
            description="Bvh bone corresponding to %s" % mhx, 

            default = ''
        )
        bvh = getBvh(mhx)
        if bvh:
            scn[mhx] = bvh
    '''

    loadDefaults(context)
    return

#
#    ensureInited(context):
#

def ensureInited(context):
    try:
        context.scene['MhxBvhScale']
        inited = True
    except:
        inited = False
    if not inited:
        initInterface(context)

#
#    saveDefaults(context):
#    loadDefaults(context):
#

def saveDefaults(context):
    if not context.scene:
        return
    filename = os.path.realpath(os.path.expanduser("~/makehuman/mhx_defaults.txt"))
    try:

        fp = open(filename, "w")
    except:
        print("Unable to open %s for writing" % filename)
        return
    for (key,value) in context.scene.items():
        if key[:3] == 'Mhx':
            fp.write("%s %s\n" % (key, value))
    fp.close()
    return

def loadDefaults(context):
    if not context.scene:
        return
    filename = os.path.realpath(os.path.expanduser("~/makehuman/mhx_defaults.txt"))
    try:
        fp = open(filename, "r")
    except:
        print("Unable to open %s for reading" % filename)
        return
    for line in fp:
        words = line.split()
        try:
            val = eval(words[1])
        except:
            val = words[1]
        context.scene[words[0]] = val
    fp.close()
    return

#
#    makeMhxRig(ob)
#

def makeMhxRig(ob):
        try:
            test = ob['MhxRig']
        except:
            test = False
        if not test:
            return

#
#    class Bvh2MhxPanel(bpy.types.Panel):
#

class Bvh2MhxPanel(bpy.types.Panel):
    bl_label = "Bvh to Mhx"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        layout.label("The old mocap tool has been deprecated.")
        layout.label("Use the new one instead.")
        layout.label("Copy the folder mh_mocap_tool from")
        layout.label("MH/importers/mhx to Blender addons folder")
        layout.label("and enable MH Mocap tool add-on")
        
        scn = context.scene
        ob = context.object
                
        layout.operator("mhx.mocap_init_interface")
        layout.operator("mhx.mocap_save_defaults")
        layout.operator("mhx.mocap_copy_angles_fk_ik")

        layout.separator()
        layout.label('Load')
        layout.prop(scn, "MhxBvhScale")
        layout.prop(scn, "MhxAutoScale")
        layout.prop(scn, "MhxStartFrame")
        layout.prop(scn, "MhxEndFrame")
        layout.prop(scn, "MhxSubsample")
        layout.prop(scn, "MhxDefaultSS")
        layout.prop(scn, "MhxRot90Anim")
        layout.prop(scn, "MhxDoSimplify")
        layout.prop(scn, "MhxApplyFixes")
        layout.operator("mhx.mocap_load_bvh")
        layout.operator("mhx.mocap_retarget_mhx")
        layout.separator()
        layout.operator("mhx.mocap_load_retarget_simplify")

        layout.separator()
        layout.label('Toggle')
        row = layout.row()
        row.operator("mhx.mocap_toggle_pole_targets")
        row.prop(ob, "MhxTogglePoleTargets")
        row = layout.row()
        row.operator("mhx.mocap_toggle_ik_limits")
        row.prop(ob, "MhxToggleIkLimits")
        row = layout.row()
        row.operator("mhx.mocap_toggle_limit_constraints")
        row.prop(ob, "MhxToggleLimitConstraints")

        layout.separator()
        layout.label('Plant')
        row = layout.row()
        row.prop(scn, "MhxPlantLoc")
        row.prop(scn, "MhxPlantRot")
        layout.prop(scn, "MhxPlantCurrent")
        layout.operator("mhx.mocap_plant")

        layout.separator()
        layout.label('Simplify')
        layout.prop(scn, "MhxErrorLoc")
        layout.prop(scn, "MhxErrorRot")
        layout.prop(scn, "MhxSimplifyVisible")
        layout.prop(scn, "MhxSimplifyMarkers")
        layout.operator("mhx.mocap_simplify_fcurves")

        layout.separator()
        layout.label('Batch conversion')
        layout.prop(scn, "MhxDirectory")
        layout.prop(scn, "MhxPrefix")
        layout.operator("mhx.mocap_batch")

        layout.separator()
        layout.label('Manage actions')
        layout.prop_menu_enum(scn, "MhxActions")
        layout.operator("mhx.mocap_update_action_list")
        layout.prop(scn, "MhxReallyDelete")
        layout.operator("mhx.mocap_delete")
        return

#
#    class VIEW3D_OT_MhxLoadBvhButton(bpy.types.Operator, ImportHelper):
#

class VIEW3D_OT_MhxLoadBvhButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.mocap_load_bvh"
    bl_label = "Load BVH file (.bvh)"

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        import bpy, os
        importAndRename(context, self.properties.filepath)
        print("%s imported" % self.properties.filepath)
        return{'FINISHED'}    

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}    

#
#    class VIEW3D_OT_MhxRetargetMhxButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxRetargetMhxButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_retarget_mhx"
    bl_label = "Retarget selected to MHX"

    def execute(self, context):
        trgRig = context.object
        guessTargetArmature(trgRig)
        for srcRig in context.selected_objects:
            if srcRig != trgRig:
                retargetMhxRig(context, srcRig, trgRig)
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxSimplifyFCurvesButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxSimplifyFCurvesButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_simplify_fcurves"
    bl_label = "Simplify FCurves"

    def execute(self, context):
        scn = context.scene
        simplifyFCurves(context, context.object, scn.MhxSimplifyVisible, scn.MhxSimplifyMarkers)
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxSilenceConstraintsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxSilenceConstraintsButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_silence_constraints"
    bl_label = "Silence constraints"

    def execute(self, context):
        silenceConstraints(context.object)
        print("Constraints silenced")
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxTogglePoleTargetsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxTogglePoleTargetsButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_toggle_pole_targets"
    bl_label = "Toggle pole targets"

    def execute(self, context):
        import bpy
        res = togglePoleTargets(context.object)
        print("Pole targets toggled", res)
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxToggleIKLimitsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxToggleIKLimitsButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_toggle_ik_limits"
    bl_label = "Toggle IK limits"

    def execute(self, context):
        import bpy
        res = toggleIKLimits(context.object)
        print("IK limits toggled", res)
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxToggleLimitConstraintsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxToggleLimitConstraintsButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_toggle_limit_constraints"
    bl_label = "Toggle Limit constraints"

    def execute(self, context):
        import bpy
        res = toggleLimitConstraints(context.object)
        print("Limit constraints toggled", res)
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxInitInterfaceButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxInitInterfaceButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_init_interface"
    bl_label = "Initialize"


    def execute(self, context):
        import bpy
        initInterface(context)
        print("Interface initialized")
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxSaveDefaultsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxSaveDefaultsButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_save_defaults"
    bl_label = "Save defaults"

    def execute(self, context):
        saveDefaults(context)
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxPlantButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxPlantButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_plant"
    bl_label = "Plant"

    def execute(self, context):
        import bpy
        plantKeys(context)
        print("Keys planted")
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxCopyAnglesIKButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxCopyAnglesIKButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_copy_angles_fk_ik"
    bl_label = "Angles  --> IK"

    def execute(self, context):
        import bpy
        copyAnglesIK(context)
        print("Angles copied")
        return{'FINISHED'}    

#
#    loadRetargetSimplify(context, filepath):
#    class VIEW3D_OT_MhxLoadRetargetSimplify(bpy.types.Operator):
#

def loadRetargetSimplify(context, filepath):
    print("Load and retarget %s" % filepath)
    time1 = time.clock()
    trgRig = context.object
    (srcRig, action) = importAndRename(context, filepath)
    retargetMhxRig(context, srcRig, trgRig)
    if context.scene['MhxDoSimplify']:
        simplifyFCurves(context, trgRig, False, False)
    deleteRig(context, srcRig, action, 'Y_')
    time2 = time.clock()
    print("%s finished in %.3f s" % (filepath, time2-time1))
    return

class VIEW3D_OT_MhxLoadRetargetSimplifyButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.mocap_load_retarget_simplify"
    bl_label = "Load, retarget, simplify"


    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        import bpy, os, mathutils

        loadRetargetSimplify(context, self.properties.filepath)
        return{'FINISHED'}    

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}    

#
#    readDirectory(directory, prefix):
#    class VIEW3D_OT_MhxBatchButton(bpy.types.Operator):
#

def readDirectory(directory, prefix):
    realdir = os.path.realpath(os.path.expanduser(directory))
    files = os.listdir(realdir)
    n = len(prefix)
    paths = []
    for fileName in files:
        (name, ext) = os.path.splitext(fileName)
        if name[:n] == prefix and ext == '.bvh':
            paths.append("%s/%s" % (realdir, fileName))
    return paths

class VIEW3D_OT_MhxBatchButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_batch"
    bl_label = "Batch run"

    def execute(self, context):
        import bpy, os, mathutils
        paths = readDirectory(context.scene['MhxDirectory'], context.scene['MhxPrefix'])
        trgRig = context.object
        for filepath in paths:
            context.scene.objects.active = trgRig
            loadRetargetSimplify(context, filepath)
        return{'FINISHED'}    


#
#    Select or delete action
#   Delete button really deletes action. Handle with care.
#
#    listAllActions(context):
#    findAction(name):
#    class VIEW3D_OT_MhxSelectButton(bpy.types.Operator):
#    class VIEW3D_OT_MhxDeleteButton(bpy.types.Operator):
#

def listAllActions(context):
    global theActions
    theActions = [] 
    for act in bpy.data.actions:
        name = act.name
        theActions.append((name, name, name))
    bpy.types.Scene.MhxActions = EnumProperty(
        items = theActions,
        name = "Actions")
    return

def findAction(name):
    global theActions
    for n,action in enumerate(theActions):
        (name1, name2, name3) = action        
        if name == name1:
            return n
    raise NameError("Unrecognized action %s" % name)

class VIEW3D_OT_MhxUpdateActionListButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_update_action_list"
    bl_label = "Update action list"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        listAllActions(context)
        return{'FINISHED'}    

class VIEW3D_OT_MhxDeleteButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_delete"
    bl_label = "Delete action"

    @classmethod
    def poll(cls, context):
        return context.scene.MhxReallyDelete

    def execute(self, context):
        global theActions
        listAllActions(context)
        scn = context.scene
        name = scn.MhxActions        
        print('Delete action', name)    
        try:
            act = bpy.data.actions[name]
        except:
            act = None
        if act:
            act.use_fake_user = False
            if act.users == 0:
                print("Deleting", act)
                n = findAction(name)
                theActions.pop(n)
                bpy.data.actions.remove(act)
                print('Action', act, 'deleted')
                listAllActions(context)
                #del act
            else:
                print("Cannot delete. %s has %d users." % (act, act.users))

        return{'FINISHED'}    

###############################################################################
#
#    Source armatures
#
###############################################################################

theSourceProps = []

#
#    defaultEnums():
#    setSourceProp(scn, prop, mhx, enums):
#    makeSourceBoneList(scn, root):
#

def defaultEnums():
    global TargetBoneNames
    enums = [('None','None','None')]
    for bn in TargetBoneNames:
        if not bn:
            continue
        (mhx, text) = bn
        enum = (mhx, text, mhx)
        enums.append(enum)
    return enums

def setSourceProp(scn, prop, mhx, enums):
    scn[prop] = 0
    n = 0
    for (mhx1, text1, mhx2) in enums:
        if mhx == mhx1: 
            scn[prop] = n
            return
        n += 1
    return

def makeSourceBoneList(scn, root):
    enums = defaultEnums()
    props = []
    makeSourceNodes(scn, root, enums, props)
    for prop in props:
        name = prop[2:].lower()
        mhx = guessSourceBone(name)
        setSourceProp(scn, prop, mhx, enums)
    return (props, enums)

#
#    makeSourceNodes(scn, node, enums, props):
#    defineSourceProp(name, enums):
#

def makeSourceNodes(scn, node, enums, props):
    if not node.children:
        return
    prop = defineSourceProp(node.name, enums)
    props.append(prop)
    for child in node.children:
        makeSourceNodes(scn, child, enums, props)
    return

def defineSourceProp(name, enums):
    qname = name.replace(' ','_')
    expr = 'bpy.types.Scene.S_%s = EnumProperty(items = enums, name = "%s")' % (qname, name)
    exec(expr)
    return 'S_'+qname

#
#    guessSourceBone(name):
#

def guessSourceBone(name):
    for amtname in theArmatureList:
        amt = theArmatures[amtname]
        try:
            mhx = amt[name]
            return mhx
        except:
            pass
    return ''

#
#    useCustomSrcRig(context):
#

def useCustomSrcRig(context):
    if theSourceProps:
        try:
            guess = context.scene.MhxGuessSrcRig
        except:
            guess = True
        return not guess
    return False

#
#    buildSrcArmature(context, rig):
#

def buildSrcArmature(context, rig):
    amt = {}
    used = {}
    scn = context.scene
    for prop in theSourceProps:
        name = prop[2:].lower()
        (mhx1, text, mhx2) = theSourceEnums[scn[prop]]
        if mhx1 == 'None':
            amt[name] = None
            continue
        amt[name] = mhx1
        try:
            user = used[mhx1]
        except:
            user = None
        if user:
            raise NameError("Source bones %s and %s both assigned to %s" % (user, name, mhx1))
        used[mhx1] = name
    fixes = createCustomFixes(scn['MhxSrcLegBentOut'], scn['MhxSrcLegRoll'], scn['MhxSrcArmBentDown'], scn['MhxSrcArmRoll'])
    return (amt, "MySource", fixes)

#
#    createCustomFixes(bendLeg, rollLeg, bendArm, rollArm):
#

def createCustomFixes(bendLeg, rollLeg, bendArm, rollArm):
    fixMats = {}
    eps = 4
    if abs(bendLeg) > eps or abs(rollLeg) > eps:        
        bendLeg *= Deg2Rad
        fixMats['UpLeg_L'] = (Matrix.Rotation(-bendLeg, 3, 'Z'), rollLeg*Deg2Rad)
        fixMats['UpLeg_R'] = (Matrix.Rotation(bendLeg, 3, 'Z'), -rollLeg*Deg2Rad)
        if abs(rollLeg) > eps:
            rollLeg *= Deg2Rad
            fixMats['LoLeg_L'] = (None, rollLeg)
            fixMats['LoLeg_R'] = (None, -rollLeg)
        
    if abs(bendArm) > eps or abs(rollArm) > eps:        
        bendArm *= Deg2Rad
        fixMats['UpArm_L'] = (Matrix.Rotation(bendArm, 3, 'Z'), rollArm*Deg2Rad)
        fixMats['UpArm_R'] = (Matrix.Rotation(-bendArm, 3, 'Z'), -rollArm*Deg2Rad)
        if abs(rollArm) > eps:
            rollArm *= Deg2Rad
            fixMats['LoArm_L'] = (None, rollArm)
            fixMats['Hand_L'] = (None, rollArm)
            fixMats['LoArm_R'] = (None, -rollArm)
            fixMats['Hand_R'] = (None, -rollArm)        
    return fixMats

#
#    ensureSourceInited(context):
#

def ensureSourceInited(context):
    scn = context.scene
    try:
        scn.MhxGuessSrcRig
        return
    except:
        pass
    expr = 'bpy.types.Scene.MhxGuessSrcRig = BoolProperty(name = "Guess source rig")'
    exec(expr)    
    scn.MhxGuessSrcRig = False
    return

#
#    class VIEW3D_OT_MhxScanBvhButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxScanBvhButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_scan_bvh"
    bl_label = "Scan bvh file"
    bl_options = {'REGISTER'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        global theSourceProps, theSourceEnums
        scn = context.scene
        root = readBvhFile(context, self.filepath, scn, True)
        (theSourceProps, theSourceEnums) = makeSourceBoneList(scn, root)
        scn['MhxSrcArmBentDown'] = 0.0
        scn['MhxSrcArmRoll'] = 0.0
        scn['MhxSrcLegBentOut'] = 0.0
        scn['MhxSrcLegRoll'] = 0.0
        ensureSourceInited(context)
        return{'FINISHED'}    

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}    

#
#    saveSourceBones(context, path):
#    loadSourceBones(context, path):
#    class VIEW3D_OT_MhxLoadSaveSourceBonesButton(bpy.types.Operator, ImportHelper):
#

def saveSourceBones(context, path):
    global theSourceProps, theSourceEnums
    scn = context.scene
    fp = open(path, "w")
    fp.write("Settings\n")
    for prop in ['MhxSrcArmBentDown','MhxSrcArmRoll','MhxSrcLegBentOut','MhxSrcLegRoll']:
        fp.write("%s %s\n" % (prop, scn[prop]))
    fp.write("Bones\n")
    for prop in theSourceProps:
        (mhx1, text, mhx2) = theSourceEnums[scn[prop]]
        fp.write("%s %s\n" % (prop, mhx1))
    fp.close()
    return
        
def loadSourceBones(context, path):
    global theSourceProps, theSourceEnums
    scn = context.scene
    theSourceEnums = defaultEnums()
    theSourceProps = []
    fp = open(path, "rU")
    status = 0
    for line in fp:
        words = line.split()
        if len(words) == 1:

            status = words[0]
        elif status == 'Settings':
            prop = words[0]
            value = float(words[1])
            scn[prop] = value
        elif status == 'Bones':
            prop = words[0]
            theSourceProps.append(prop)
            mhx = words[1]
            setSourceProp(scn, prop, mhx, theSourceEnums)
            print(prop, scn[prop], mhx)
    fp.close()
    
    for prop in theSourceProps:
        defineSourceProp(prop[2:], theSourceEnums)
    return
        
class VIEW3D_OT_MhxLoadSaveSourceBonesButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.mocap_load_save_source_bones"
    bl_label = "Load/save source bones"

    loadSave = bpy.props.StringProperty()
    filename_ext = ".txt"
    #filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        ensureSourceInited(context)
        if self.loadSave == 'save':
            saveSourceBones(context, self.properties.filepath)
        else:
            loadSourceBones(context, self.properties.filepath)
        return{'FINISHED'}    

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}    

#        
#    class MhxSourceBonesPanel(bpy.types.Panel):
#

class MhxSourceBonesPanel(bpy.types.Panel):
    bl_label = "Source armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def draw(self, context):
        global theSourceProps
        layout = self.layout
        scn = context.scene
        rig = context.object
        if theSourceProps:
            layout.operator("mhx.mocap_scan_bvh", text="Rescan bvh file")    
        else:
            layout.operator("mhx.mocap_scan_bvh", text="Scan bvh file")    
        layout.operator("mhx.mocap_load_save_source_bones", text='Load source bones').loadSave = 'load'        
        layout.operator("mhx.mocap_load_save_source_bones", text='Save source bones').loadSave = 'save'        
        if not theSourceProps:
            return
        layout.separator()
        layout.prop(scn, 'MhxGuessSrcRig')
        layout.label("Arms")
        row = layout.row()
        row.prop(scn, '["MhxSrcArmBentDown"]', text='Down')
        row.prop(scn, '["MhxSrcArmRoll"]', text='Roll')
        layout.label("Legs")
        row = layout.row()
        row.prop(scn, '["MhxSrcLegBentOut"]', text='Out')
        row.prop(scn, '["MhxSrcLegRoll"]', text='Roll')
        for prop in theSourceProps:
            layout.prop_menu_enum(scn, prop)


###############################################################################
#
#    Target armatures
#
###############################################################################

#    (mhx bone, text)

TargetBoneNames = [
    ('Root',        'Root bone'),
    ('Spine1',        'Lower spine'),
    ('Spine2',        'Middle spine'),
    ('Spine3',        'Upper spine'),
    ('Neck',        'Neck'),
    ('Head',        'Head'),
    None,
    ('Clavicle_L',    'L clavicle'),
    ('UpArm_L',        'L upper arm'),
    ('LoArm_L',        'L forearm'),
    ('Hand_L',        'L hand'),
    None,
    ('Clavicle_R',    'R clavicle'),
    ('UpArm_R',        'R upper arm'),
    ('LoArm_R',        'R forearm'),
    ('Hand_R',        'R hand'),
    None,
    ('Hips',        'Hips'),
    None,
    ('Hip_L',        'L hip'),
    ('UpLeg_L',        'L thigh'),
    ('LoLeg_L',        'L shin'),
    ('Foot_L',        'L foot'),
    ('Toe_L',        'L toes'),
    None,
    ('Hip_R',        'R hip'),
    ('UpLeg_R',        'R thigh'),
    ('LoLeg_R',        'R shin'),
    ('Foot_R',        'R foot'),
    ('Toe_R',        'R toes'),
]

#    (mhx bone, text, fakeparent, copyRot)

TargetIkBoneNames = [ 
    ('Wrist_L',     'L wrist', 'LoArm_L', 'Hand_L'),
    ('ElbowPT_L',     'L elbow', 'UpArm_L', None),
    ('Ankle_L',     'L ankle', 'LoLeg_L', 'Foot_L'),
    ('KneePT_L',     'L knee', 'UpLeg_L', None),

    ('Wrist_R',     'R wrist', 'LoArm_R', 'Hand_R'),
    ('ElbowPT_R',     'R elbow', 'UpArm_R', None),
    ('Ankle_R',        'R ankle', 'LoLeg_R', 'Foot_R'),
    ('KneePT_R',     'R knee', 'UpLeg_R', None),
]

#
#    initTargetCharacter(rig):
#    class VIEW3D_OT_MhxInitTargetCharacterButton(bpy.types.Operator):
#    class VIEW3D_OT_MhxUnInitTargetCharacterButton(bpy.types.Operator):
#

def initTargetCharacter(rig):
    for bn in TargetBoneNames+TargetIkBoneNames:
        if not bn:
            continue
        try:
            (mhx, text) = bn
        except:
            (mhx, text, fakepar, copyrot) = bn
        rig[mhx] = mhx
    rig['MhxTargetRig'] = True
    rig['MhxArmBentDown'] = 0.0
    rig['MhxLegBentOut'] = 0.0
    return
    
class VIEW3D_OT_MhxInitTargetCharacterButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_init_target_character"
    bl_label = "Initialize target character"
    bl_options = {'REGISTER'}

    def execute(self, context):
        initTargetCharacter(context.object)
        print("Target character initialized")
        return{'FINISHED'}    

class VIEW3D_OT_MhxUnInitTargetCharacterButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_uninit_target_character"
    bl_label = "Uninitialize"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.object['MhxTargetRig'] = False
        print("Target character uninitialized")
        return{'FINISHED'}    

#
#    assocTargetBones(rig, names, xtraAssoc):
#

def assocTargetBones(rig, names, xtraAssoc):
    boneAssoc = []
    for bn in names:
        if not bn:
            continue
        try:
            (mhx, text) = bn
        except:
            (mhx, text, fakePar, copyRot) = bn
        bone = rig[mhx]
        if bone != '':
            try:
                rig.data.bones[bone]
                exists = True
            except:
                exists = False
            if exists:
                boneAssoc.append((bone, mhx))
            else:
                raise NameError("Bone %s does not exist in armature %s" % (bone, rig.name))

    parAssoc = {}
    assoc = boneAssoc+xtraAssoc
    for (bname, mhx) in boneAssoc:
        bone = rig.data.bones[bname] 
        (par, stop) = realBone(bone.parent, rig, 0, assoc)
        while not stop:
            (par, stop) = realBone(par.parent, rig, 0, assoc)
        if par:
            parAssoc[bname] = par.name
        else:
            parAssoc[bname] = None

    rolls = {}
    try:
        bpy.ops.object.mode_set(mode='EDIT')    
        (bname, mhx) = boneAssoc[0]
        rig.data.edit_bones[bname]
        edit = True
    except:
        edit = False
    if edit:
        for (bname, mhx) in boneAssoc:
            eb = rig.data.edit_bones[bname]
            rolls[bname] = eb.roll
        bpy.ops.object.mode_set(mode='POSE')    
        for (bname, mhx) in boneAssoc:
            bone = rig.data.bones[bname]
            bone['Roll'] = rolls[bname]
    else:
        for (bname, mhx) in boneAssoc:
            bone = rig.data.bones[bname]
            try:
                rolls[bname] = bone['Roll']
            except:
                raise NameError("Associations must be made in rig source file")

    pb = rig.pose.bones[rig['Root']]
    pb.lock_location = (False,False,False)


    return (boneAssoc, parAssoc, rolls)

#
#    findFakeParent(mhx, boneAssoc):
#

def findFakeParent(mhx, boneAssoc):
    for (mhx1, text, fakeMhx, copyMhx) in TargetIkBoneNames:
        if mhx == mhx1:
            fakePar = assocKey(fakeMhx, boneAssoc)
            copyRot = assocKey(copyMhx, boneAssoc)
            return (fakePar, copyRot)
    raise NameError("Did not find fake parent %s" % mhx)

#
#    makeTargetAssoc(rig):
#

def makeTargetAssoc(rig):
    (boneAssoc, parAssoc, rolls) = assocTargetBones(rig, TargetBoneNames, [])
    (ikBoneAssoc, ikParAssoc, ikRolls) = assocTargetBones(rig, TargetIkBoneNames, boneAssoc)

    ikBones = []
    ikParents = {}
    for (bone, mhx) in ikBoneAssoc:
        ikBones.append(bone)
        (fakePar, copyRot) = findFakeParent(mhx, boneAssoc)
        # bone : (realParent, fakeParent, copyRot, reverse)
        par = ikParAssoc[bone]
        ikParents[bone] = (par, fakePar, copyRot, False)
        parAssoc[bone] = par

    fixMats = createCustomFixes(rig['MhxLegBentOut'], 0, rig['MhxArmBentDown'], 0)

    print("Associations:")    
    print("            Bone :       Mhx bone         Parent  Roll")
    for (bname, mhx) in boneAssoc:
        roll = rolls[bname]
        print("  %14s : %14s %14s %5d" % (bname, mhx, parAssoc[bname], roll/Deg2Rad))
    print("IK bones:")
    print("            Bone :       Mhx bone    Real parent    Fake parent       Copy rot")
    for (bname, mhx) in ikBoneAssoc:
        (par, fakePar, copyRot, reverse) = ikParents[bname]
        print("  %14s : %14s %14s %14s %14s" % (bname, mhx, par, fakePar, copyRot))
    return (boneAssoc, parAssoc, rolls, fixMats, ikBones, ikParents)

#
#    assocValue(name, assoc):
#    assocKey(name, assoc):
#
    
def assocValue(name, assoc):
    for (key, value) in assoc:
        if key == name:
            return value
    return None

def assocKey(name, assoc):
    for (key, value) in assoc:
        if value == name:
            return key
    return None

#
#    realBone(bone, rig, n, assoc):
#

def realBone(bone, rig, n, assoc):
    if not bone:
        return (None, True)
    if assocValue(bone.name, assoc):
        return (bone, True)
    if n > 5:
        print("Real bone overflow:", bone)
        return (bone, True)

    pb = rig.pose.bones[bone.name]
    for cns in pb.constraints:
        if (((cns.type == 'COPY_ROTATION' and cns.use_x and cns.use_z) or
             (cns.type == 'COPY_TRANSFORMS')) and
            (cns.influence > 0.6) and
            (cns.target == rig)):
            rb = rig.data.bones[cns.subtarget]
            return realBone(rb, rig, n+1, assoc)
    return (bone, False)

class VIEW3D_OT_MhxMakeTargetAssocButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_make_assoc"
    bl_label = "Make target associations"
    bl_options = {'REGISTER'}

    def execute(self, context):
        makeTargetAssoc(context.object)
        print("Associations made")
        return{'FINISHED'}    

#
#
#

def unrollAll(context):
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = context.object.data.edit_bones
    for eb in ebones:
        eb.roll = 0
    bpy.ops.object.mode_set(mode='POSE')
    return

class VIEW3D_OT_MhxUnrollAllButton(bpy.types.Operator):
    bl_idname = "mhx.mocap_unroll_all"
    bl_label = "Unroll all"
    bl_options = {'REGISTER'}

    def execute(self, context):
        unrollAll(context)
        print("Associations made")
        return{'FINISHED'}    

#
#    saveTargetBones(context, path):
#    loadTargetBones(context, path):
#    class VIEW3D_OT_MhxLoadSaveTargetBonesButton(bpy.types.Operator, ImportHelper):
#

def saveTargetBones(context, path):
    rig = context.object
    fp = open(path, "w")
    for bn in TargetBoneNames+TargetIkBoneNames:
        if not bn:
            continue
        try:
            (mhx, text) = bn
        except:
            (mhx, text, fakepar, copyrot) = bn
        bone = rig[mhx]
        if bone == '':
            fp.write("%s %s\n" % (mhx, '-'))
        else:
            fp.write("%s %s\n" % (mhx, bone))
    fp.close()
    return
        
def loadTargetBones(context, path):
    rig = context.object
    fp = open(path, "rU")
    for line in fp:
        words = line.split()
        try:
            mhx = words[0]
            bone = words[1]
        except:
            mhx = None
        if mhx:
            if bone == '-':
                bone = ''
            rig[mhx] = bone
    fp.close()
    return
        
class VIEW3D_OT_MhxLoadSaveTargetBonesButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.mocap_load_save_target_bones"
    bl_label = "Load/save target bones"

    loadSave = bpy.props.StringProperty()
    filename_ext = ".txt"
    #filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        if self.loadSave == 'save':
            saveTargetBones(context, self.properties.filepath)
        else:
            loadTargetBones(context, self.properties.filepath)
        return{'FINISHED'}    

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}    

#        
#    class MhxTargetBonesPanel(bpy.types.Panel):
#

class MhxTargetBonesPanel(bpy.types.Panel):
    bl_label = "Target armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        rig = context.object
        try:
            inited = rig['MhxTargetRig']
        except:
            inited = False

        if not inited:
            layout.operator("mhx.mocap_init_target_character", text='Initialize target character')
            return

        layout.operator("mhx.mocap_init_target_character", text='Reinitialize target character')        
        layout.operator("mhx.mocap_uninit_target_character")        
        layout.operator("mhx.mocap_load_save_target_bones", text='Load target bones').loadSave = 'load'        
        layout.operator("mhx.mocap_load_save_target_bones", text='Save target bones').loadSave = 'save'        
        layout.operator("mhx.mocap_make_assoc")        
        layout.operator("mhx.mocap_unroll_all")        
        #layout.prop(rig, '["MhxArmBentDown"]', text='Arm bent down')
        #layout.prop(rig, '["MhxLegBentOut"]', text='Leg bent out')

        layout.label("FK bones")
        for bn in TargetBoneNames:
            if bn:
                (mhx, text) = bn
                layout.prop(rig, '["%s"]' % mhx, text=text)
            else:
                layout.separator()
        layout.label("IK bones")
        for (mhx, text, fakePar, copyRot) in TargetIkBoneNames:
            layout.prop(rig, '["%s"]' % mhx, text=text)
        return

#
#    Debugging
#
"""
def debugOpen():
    global theDbgFp
    theDbgFp = open("/home/thomas/myblends/debug.txt", "w")

def debugClose():
    global theDbgFp
    theDbgFp.close()

def debugPrint(string):
    global theDbgFp
    theDbgFp.write("%s\n" % string)

def debugPrintVec(vec):
    global theDbgFp
    theDbgFp.write("(%.3f %.3f %.3f)\n" % (vec[0], vec[1], vec[2]))

def debugPrintVecVec(vec1, vec2):
    global theDbgFp
    theDbgFp.write("(%.3f %.3f %.3f) (%.3f %.3f %.3f)\n" %
        (vec1[0], vec1[1], vec1[2], vec2[0], vec2[1], vec2[2]))
"""
#
#    init and register
#

initInterface(bpy.context)

def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()

#readBvhFile(context, filepath, scale, startFrame, rot90, 1)
#readBvhFile(bpy.context, '/home/thomas/makehuman/bvh/Male1_bvh/Male1_A5_PickUpBox.bvh', 1.0, 1, False)
#readBvhFile(bpy.context, '/home/thomas/makehuman/bvh/cmu/10/10_03.bvh', 1.0, 1, False)
