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
from bpy_extras.io_utils import ImportHelper
from bpy.props import *
from mathutils import Vector
from collections import OrderedDict

import makewalk
from makewalk.utils import findBoneFCurve

from . import io_json

#------------------------------------------------------------------------
#   Save facerig
#------------------------------------------------------------------------

def getRigAndMesh(context):
    ob = context.object
    if ob.type == 'MESH':
        return ob.parent, ob
    elif ob.type == 'ARMATURE':
        for child in ob.children:
            if child.type == 'MESH':
                return ob, child
    raise RuntimeError("An armature and a mesh must be selected")


def getNewUuid():
    import sys
    if sys.platform == 'win32':
        # Avoid error message in blender by using a version without ctypes
        import makeclothes
        from makeclothes import uuid4 as uuid
    else:
        import uuid
    return str(uuid.uuid4())


def sortDict(dict):
    dlist = list(dict.items())
    dlist.sort()
    ndict = OrderedDict()
    for key,val in dlist:
        ndict[key] = val
    return ndict


def saveFaceRig(context, filepath):
    if os.path.splitext(filepath)[1] != ".json":
        filepath += ".json"

    rig,ob = getRigAndMesh(context)

    markers = {}
    for v in ob.data.vertices:
        for bone in rig.data.bones:
            vec = bone.head_local - v.co
            if vec.length < 1e-3:
                markers[bone.name.lower()] = [(v.index, 1.0)]
                break

    weights = {}
    vgroups = {}
    for vgrp in ob.vertex_groups:
        vgroups[vgrp.index] = vgrp
        weights[vgrp.name.lower()] = []
    for v in ob.data.vertices:
        for g in v.groups:
            vgrp = vgroups[g.group]
            weights[vgrp.name.lower()].append((v.index, g.weight))
    for vname in list(weights):
        try:
            markers[vname]
        except KeyError:
            del weights[vname]

    struct = OrderedDict()
    struct["name"] = rig.name.lower()
    struct["uuid"] = getNewUuid()
    struct["markers"] = sortDict(markers)
    struct["vertex_groups"] = sortDict(weights)
    io_json.saveJson(struct, filepath, maxDepth=1)


class VIEW3D_OT_SaveFaceRigButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mp.save_facerig"
    bl_label = "Save Face Rig"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath the JSON file", maxlen=1024, default="")

    def execute(self, context):
        print("Saving face rig %s" % self.filepath)
        saveFaceRig(context, self.filepath)
        print("Face rig %s saved" % self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#------------------------------------------------------------------------
#   Load facerig
#------------------------------------------------------------------------

def putBoneOnLayer(n):
    return (n*[False] + [True] + (31-n)*[False])


def loadFaceRig(context, filepath):
    rig,ob = getRigAndMesh(context)
    scn = context.scene
    scn.objects.active = rig
    struct = io_json.loadJson(filepath)

    # Create new bones

    bpy.ops.object.mode_set(mode='EDIT')
    parent = rig.data.edit_bones["DEF-head"]
    for bname,locs in struct["markers"].items():
        eb = rig.data.edit_bones.new(bname)
        eb.parent = parent
        eb.layers = putBoneOnLayer(8)
        loc = Vector((0,0,0))
        for vn,w in locs:
            loc += w * ob.data.vertices[vn].co
        eb.head = loc
        eb.tail = loc + Vector((0,0.1,0))

    # Control jaw with chin and eye with

    jaw = rig.data.edit_bones["jaw"]
    djaw = rig.data.edit_bones["DEF-jaw"]
    chin = rig.data.edit_bones["m_chin"]
    jaw.layers = putBoneOnLayer(15)
    jaw.tail = chin.head
    djaw.tail = chin.head

    leye = rig.data.edit_bones["eye.L"]
    reye = rig.data.edit_bones["eye.R"]
    head = rig.data.edit_bones["head"]
    leye.parent = head
    reye.parent = head

    bpy.ops.object.mode_set(mode='POSE')

    pjaw = rig.pose.bones["jaw"]
    pjaw.custom_shape = None
    cns = pjaw.constraints.new('STRETCH_TO')
    cns.target = rig
    cns.subtarget = chin.name
    cns.rest_length = pjaw.length

    pleye = rig.pose.bones["eye.L"]
    pleye.custom_shape = None
    cns = pleye.constraints.new('IK')
    cns.target = rig
    cns.subtarget = "l_eye"
    cns.chain_count = 1

    preye = rig.pose.bones["eye.R"]
    preye.custom_shape = None
    cns = preye.constraints.new('IK')
    cns.target = rig
    cns.subtarget = "r_eye"
    cns.chain_count = 1

    bpy.ops.object.mode_set(mode='OBJECT')
    rig.data.layers = putBoneOnLayer(8)

    # Modify weights

    sumWeights = {}
    for v in ob.data.vertices:
        sumWeights[v.index] = 0
    for vname,weights in struct["vertex_groups"].items():
        try:
            vgrp = ob.vertex_groups[vname]
        except KeyError:
            ob.vertex_groups.new(vname)
        for vn,w in weights:
            sumWeights[vn] += w

    for vn,w in sumWeights.items():
        if w > 1e-4:
            v = ob.data.vertices[vn]
            wsum = 0
            for g in v.groups:
                wsum += g.weight
            if wsum > 0:
                factor = (1-w)/wsum
                for g in v.groups:
                    g.weight *= factor

    for vname,weights in struct["vertex_groups"].items():
        for vn,w in weights:
            vgrp = ob.vertex_groups[vname]
            vgrp.add([vn], w, 'REPLACE')


class VIEW3D_OT_LoadFaceRigButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mp.load_facerig"
    bl_label = "Load Face Rig"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath the JSON file", maxlen=1024, default="")

    def execute(self, context):
        print("Loading face rig %s" % self.filepath)
        loadFaceRig(context, self.filepath)
        print("Face rig %s loaded" % self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#------------------------------------------------------------------------
#   Transfer face animation
#------------------------------------------------------------------------

def transferFaceAnim(src, trg, scn, markers, replacements):

    # Get scale

    minvec = Vector((1e6, 1e6, 1e6))
    maxvec = Vector((-1e6, -1e6, -1e6))
    minbones = ["","",""]
    maxbones = ["","",""]
    for bone in src.data.bones:
        try:
            trg.data.bones[bone.name]
        except KeyError:
            continue
        head = bone.head_local
        vec = head - minvec
        for n in range(3):
            if vec[n] < 0:
                minvec[n] = head[n]
                minbones[n] = bone.name
        vec = head - maxvec
        for n in range(3):
            if vec[n] > 0:
                maxvec[n] = head[n]
                maxbones[n] = bone.name

    scale = Vector((1,1,1))
    svec = maxvec - minvec
    for n in range(3):
        minbone = trg.data.bones[minbones[n]]
        maxbone = trg.data.bones[maxbones[n]]
        tvec = maxbone.head_local - minbone.head_local
        scale[n] = tvec[n]/svec[n]

    # Copy and scale F-curves

    sact = src.animation_data.action
    tact = bpy.data.actions.new(trg.name + "Action")
    if not trg.animation_data:
        trg.animation_data_create()
    trg.animation_data.action = tact

    for tmarker in markers:
        try:
            trg.data.bones[tmarker]
        except KeyError:
            print("Did not find target bone %s" % tmarker)
            continue
        try:
            smarkers = replacements[tmarker]
        except KeyError:
            smarkers = [tmarker]
        if not isinstance(smarkers, list):
            smarkers = [smarkers]

        for index in range(3):
            sfcus = []
            for smarker in smarkers:
                try:
                    pb = src.pose.bones[smarker]
                    sfcu = findBoneFCurve(pb, src, index, mode='location')
                    sfcus.append(sfcu)
                except KeyError:
                    print("Did not find source marker %s" % smarker)
                    continue

            if len(sfcus) == 0:
                continue
            else:
                sfcu = sfcus[0]

            s = scale[sfcu.array_index]
            tpath = 'pose.bones["%s"].location' % tmarker
            tfcu = tact.fcurves.new(tpath, index=index, action_group=tmarker)
            n = len(sfcu.keyframe_points)
            tfcu.keyframe_points.add(count=n)
            for i in range(n):
                t,y = sfcu.keyframe_points[i].co
                tfcu.keyframe_points[i].co = (t, s*y)

            if len(sfcus) > 10:
                factor = 1.0/len(sfcus)
                for kp in tfcu.keyframe_points:
                    t = kp.co[0]
                    y = 0.0
                    for sfcu in sfcus:
                        y += sfcu.evaluate(t)
                    kp.co[1] = factor*y




def loadTransfer(filepath):
    tstruct = io_json.loadJson(filepath)
    try:
        baseset = tstruct["baseset"]
    except KeyError:
        return None,None
    folder = os.path.dirname(filepath)
    basepath = os.path.join(folder, baseset)
    if os.path.splitext(basepath)[1] != ".json":
        basepath += ".json"
    bstruct = io_json.loadJson(basepath)
    return bstruct["markers"], tstruct["replacements"]


class VIEW3D_OT_TransferFaceAnimButton(bpy.types.Operator):
    bl_idname = "mp.transfer_face_anim"
    bl_label = "Transfer Face Animation"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="Transfer File", description="Filepath to the transfer JSON file", maxlen=1024, default="")

    def execute(self, context):
        src = context.object
        scn = context.scene
        markers,replacements = loadTransfer(self.filepath)
        for trg in scn.objects:
            if trg.select and trg != src and trg.type == 'ARMATURE':
                transferFaceAnim(src, trg, scn, markers, replacements)
        print("Face animation transferred")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#------------------------------------------------------------------------
#   Average F-curves
#------------------------------------------------------------------------

'''
def findFCurve(path, index, fcurves):
    for fcu in fcurves:
        if (fcu.data_path == path and
            fcu.array_index == index):
            return fcu
    print('F-curve "%s" not found.' % path)
    return None


def findBoneFCurve(pb, rig, index, mode='rotation'):
    if mode == 'rotation':
        if pb.rotation_mode == 'QUATERNION':
            mode = "rotation_quaternion"
        else:
            mode = "rotation_euler"
    path = 'pose.bones["%s"].%s' % (pb.name, mode)

    if rig.animation_data is None:
        return None
    action = rig.animation_data.action
    if action is None:
        return None
    return findFCurve(path, index, action.fcurves)
'''

def isVisible(pb, rig):
    for n,layer in enumerate(pb.bone.layers):
        if layer and rig.data.layers[n]:
            return True
    return False


def averageFCurves(context):
    rig = context.object
    trg = context.active_pose_bone
    srcs = []
    for src in rig.pose.bones:
        if (src.bone.select and
            src != trg and
            isVisible(src, rig)):
            srcs.append(src)

    if trg is None or srcs == []:
        print("At least two bones must be selected")
        return

    print(trg)
    print(srcs)

    for index in range(3):
        scurves = []
        for src in srcs:
            scu = findBoneFCurve(src, rig, index, mode='location')
            print(scu.data_path, scu.array_index)
            if scu is None:
                print("Bone %s has no location F-curve with index %d. Skipping." % (src.name, index))
            else:
                scurves.append(scu)

        tcu = findBoneFCurve(trg, rig, index, mode='location')
        if tcu is None:
            act = rig.animation_data.action
            data_path = 'pose.bones["%s"].location' % trg.name
            tcu = act.fcurves.new(data_path, index=index, action_group=trg.name)
            scu = scurves[0]
            n = len(scu.keyframe_points)
            tcu.keyframe_points.add(count=n)
            for n,kp in enumerate(tcu.keyframe_points):
                kp.co = scu.keyframe_points[n].co

        ncurves = len(scurves)
        print(tcu.data_path, tcu.array_index)

        for kp in tcu.keyframe_points:
            t = kp.co[0]
            xsum = 0.0
            for scu in scurves:
                xsum += scu.evaluate(t)
            kp.co[1] = xsum/ncurves


class VIEW3D_OT_AverageFCurvesButton(bpy.types.Operator):
    bl_idname = "mp.average_fcurves"
    bl_label = "Average F-curves"
    bl_options = {'UNDO'}

    def execute(self, context):
        averageFCurves(context)
        print("F-curves averaged")
        return{'FINISHED'}

