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
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165


import os
import bpy
from mathutils import Vector, Matrix
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

#------------------------------------------------------------------------
#   General
#------------------------------------------------------------------------

class Eye:
    def createMiddle(self, prefix, mfile):
        nmarkers = []
        for marker in mfile.markers:
            if marker.startswith(prefix):
                if marker.endswith("up"):
                    up = marker
                elif marker.endswith("down"):
                    down = marker
                elif marker.endswith("left"):
                    left = marker
                elif marker.endswith("right"):
                    right = marker
                else:
                    nmarkers.append(marker)
            else:
                nmarkers.append(marker)

        if not (up and down and left and right):
            return

        middle = prefix + "middle"
        nmarkers.append(middle)
        mfile.markers = nmarkers

        for fdata in mfile.fdatas:
            rup = fdata.markers[up]
            rdown = fdata.markers[down]
            rleft = fdata.markers[left]
            rright = fdata.markers[right]
            rmiddle = (rup + rdown + rleft + rright)/4
            fdata.markers[middle] = rmiddle
            del fdata.markers[up]
            del fdata.markers[down]
            del fdata.markers[left]
            del fdata.markers[right]


class FrameData:
    def __init__(self, frame, time):
        self.frame = frame
        self.time = time
        self.markers = {}


class MarkerFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.info = {}
        self.markers = []
        self.restpos = {}
        self.fdatas = []
        self.leftEye = Eye()
        self.rightEye = Eye()


    def load(self, filepath):
        raise NonImplementedError("Load")


    def setup(self, scn):
        self.firstFrame, self.lastFrame = scn.MpFrameStart, scn.MpFrameEnd
        self.scale = scn.MpScale
        self.delta = Vector((0,scn.MpDeltaY,0))


    def build(self, scn):
        fname = os.path.splitext(os.path.basename(self.filepath))[0]
        amt = bpy.data.armatures.new(fname)
        rig = bpy.data.objects.new(fname, amt)
        scn.objects.link(rig)
        scn.objects.active = rig

        #self.leftEye.createMiddle("l_eye_", self)
        #self.rightEye.createMiddle("r_eye_", self)

        bpy.ops.object.mode_set(mode='EDIT')
        fdata = self.fdatas[0]
        restloc = {}
        for marker in self.markers:
            eb = amt.edit_bones.new(marker)
            restloc[marker] = eb.head = fdata.markers[marker]
            eb.tail = eb.head + self.delta

        bpy.ops.object.mode_set(mode='POSE')
        for fdata in self.fdatas:
            scn.frame_set(fdata.frame)
            if fdata.frame % 10 == 0:
                print(fdata.frame)
            for marker,loc in fdata.markers.items():
                pb = rig.pose.bones[marker]
                gmat = Matrix.Translation(loc)
                pmat = getPoseMatrix(gmat, pb)
                insertLocation(pb, pmat)

        return rig

#------------------------------------------------------------------------
#   Utils
#------------------------------------------------------------------------

def getPoseMatrix(gmat, pb):
    restInv = pb.bone.matrix_local.inverted()
    if pb.parent:
        parInv = pb.parent.matrix.inverted()
        parRest = pb.parent.bone.matrix_local
        return restInv * (parRest * (parInv * gmat))
    else:
        return restInv * gmat


def getGlobalMatrix(mat, pb):
    gmat = pb.bone.matrix_local * mat
    if pb.parent:
        parMat = pb.parent.matrix
        parRest = pb.parent.bone.matrix_local
        return parMat * (parRest.inverted() * gmat)
    else:
        return gmat


def insertLocation(pb, mat):
    pb.location = mat.to_translation()
    pb.keyframe_insert("location", group=pb.name)


def insertRotation(pb, mat):
    q = mat.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", group=pb.name)
    else:
        pb.rotation_euler = q.to_euler(pb.rotation_mode)
        pb.keyframe_insert("rotation_euler", group=pb.name)

#------------------------------------------------------------------------
#   TRC
#------------------------------------------------------------------------

class TrcFile(MarkerFile):

    def __init__(self, filepath):
        if os.path.splitext(filepath)[1].lower() != ".trc":
            filepath += ".trc"
        MarkerFile.__init__(self, filepath)


    def load(self, scn):
        self.setup(scn)
        status = 0
        try:
            with open(self.filepath, "rU") as fp:
                for line in fp:
                    words = line.split()
                    if len(words) == 0:
                        pass
                    elif words[0] == "PathFileType":
                        pass
                    elif words[0] == "DataRate":
                        keys = words
                        status = 1
                    elif words[0] == "Frame#":
                        self.markers = [marker.lower() for marker in words[2:]]
                        print(self.markers)
                        status = 2
                    elif status == 1:
                        for n,word in enumerate(words):
                            self.info[keys[n]] = word
                            status = 0
                    elif status == 2:
                        status = 3
                    elif status == 3:
                        fdata = FrameData(int(words[0]), float(words[1]))
                        if fdata.frame < self.firstFrame:
                            continue
                        self.fdatas.append(fdata)
                        for n,marker in enumerate(self.markers):
                            try:
                                fdata.markers[marker] = self.scale*Vector((float(words[3*n+2]), -float(words[3*n+4]), float(words[3*n+3])))
                            except IndexError:
                                print(len(words))
                                print(len(self.markers), (len(words)-2)/3.0 )
                                print("Skip", marker, n)
                                halt
                        if fdata.frame > self.lastFrame:
                            return
        except IOError:
            pass

#------------------------------------------------------------------------
#   TXT
#------------------------------------------------------------------------

class TxtFile(MarkerFile):

    def __init__(self, filepath):
        if os.path.splitext(filepath)[1].lower() != ".txt":
            filepath += ".txt"
        MarkerFile.__init__(self, filepath)


    def load(self, scn):
        self.setup(scn)
        status = 0
        try:
            with open(self.filepath, "rU") as fp:
                for line in fp:
                    words = line.split()
                    if len(words) == 0:
                        pass
                    elif words[0] == "Field":
                        self.parseMarkers(words[2:])
                        status = 1
                    elif status == 1:
                        fdata = FrameData(int(words[0]), float(words[1]))
                        if fdata.frame < self.firstFrame:
                            continue
                        self.fdatas.append(fdata)
                        for n,marker in enumerate(self.markers):
                            try:
                                mdata = self.scale*Vector((float(words[3*n+2]), float(words[3*n+3]), float(words[3*n+4])))
                            except IndexError:
                                print(len(words))
                                print(len(self.markers), (len(words)-2)/3.0 )
                                print("Skip", marker, n)
                                halt
                            fdata.markers[marker] = mdata
                        if fdata.frame > self.lastFrame:
                            return
        except IOError:
            pass

    def parseMarkers(self, words):
        self.markers = []
        nmarkers = int(len(words)/3)
        for n in range(nmarkers):
            self.markers.append(words[3*n].split(":")[1])


#------------------------------------------------------------------------
#   Buttons
#------------------------------------------------------------------------

class VIEW3D_OT_LoadTrcFileButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mp.load_trc_file"
    bl_label = "Load TRC File"
    bl_options = {'UNDO'}

    filename_ext = ".trc"
    filter_glob = StringProperty(default="*.trc", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the TRC file", maxlen=1024, default="")

    def execute(self, context):
        trc = TrcFile(self.filepath)
        trc.load(context.scene)
        trc.build(context.scene)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_LoadTxtFileButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mp.load_txt_file"
    bl_label = "Load TXT File"
    bl_options = {'UNDO'}

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the TXT file", maxlen=1024, default="")

    def execute(self, context):
        txt = TxtFile(self.filepath)
        txt.load(context.scene)
        txt.build(context.scene)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}




def init():
    bpy.types.Scene.MpFrameStart = IntProperty(
        name="Frame Start",
        description="First frame",
        default=1)

    bpy.types.Scene.MpFrameEnd = IntProperty(
        name="Frame End",
        description="Last frame",
        default=250)

    bpy.types.Scene.MpScale = FloatProperty(
        name="Scale",
        description="Scale",
        default=0.01)

    bpy.types.Scene.MpDeltaY = FloatProperty(
        name="Delta Y",
        description="Tail offset in Y direction",
        default=0.1)

