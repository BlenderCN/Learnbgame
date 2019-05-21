#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

The MakeHuman application uses predefined morph target files to distort
the humanoid model when physiological changes or changes to the pose are
applied by the user. The morph target files contain extreme mesh
deformations for individual joints and features which can used
proportionately to apply less extreme deformations and which can be
combined to provide a very wide range of options to the user of the
application.

This module contains a set of functions used by 3d artists during the
development cycle to create these extreme morph target files from
hand-crafted models.

"""

import bpy
import os
import sys
import math
import random
from mathutils import Vector, Quaternion, Matrix
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

from . import mh
from .error import MHError, handleMHError
from . import utils
from .utils import round, setObjectMode, invokeWithFileCheck, drawFileCheck, getMHBlenderDirectory
from . import import_obj
from .proxy import CProxy
from .symmetry_map import *

Epsilon = 1e-4
Comments = []

#----------------------------------------------------------
#   Settings
#----------------------------------------------------------

from . import mt

def setSettings(context):
    ob = context.object
    if len(ob.data.vertices) == mt.settings["alpha7"].nTotalVerts:
        print("Alpha 7 mesh detected")
        ob.MhMeshVersion = "alpha7"
    elif len(ob.data.vertices) == mt.settings["alpha8"].nTotalVerts:
        print("Alpha 8 mesh detected")
        ob.MhMeshVersion = "alpha8"
    else:
        print(("Unknown mesh version with %d verts" % len(ob.data.vertices)))
        ob.MhMeshVersion = ""


def getSettings(ob):
    return mt.settings[ob.MhMeshVersion]

#----------------------------------------------------------
#
#----------------------------------------------------------

def afterImport(context, filepath, deleteHelpers, useMaterials):
    ob = context.object
    ob.MhFilePath = filepath
    ob.MhDeleteHelpers = deleteHelpers
    ob.MhUseMaterials = useMaterials
    setSettings(context)
    settings = getSettings(ob)

    if ob.MhUseMaterials:
        addMaterial(ob, 0, "Body", (1,1,1), (0, settings.nTotalVerts))
        addMaterial(ob, 1, "Tongue", (0.5,0,0.5), settings.vertices["Tongue"])
        addMaterial(ob, 2, "Joints", (0,1,0), settings.vertices["Joints"])
        addMaterial(ob, 3, "Eyes", (0,1,1), settings.vertices["Eyes"])
        addMaterial(ob, 4, "EyeLashes", (1,0,1), settings.vertices["EyeLashes"])
        addMaterial(ob, 5, "LoTeeth", (0,0.5,0.5), settings.vertices["LoTeeth"])
        addMaterial(ob, 6, "UpTeeth", (0,0.5,1), settings.vertices["UpTeeth"])
        addMaterial(ob, 7, "Penis", (0.5,0,1), settings.vertices["Penis"])
        addMaterial(ob, 8, "Tights", (1,0,0), settings.vertices["Tights"])
        addMaterial(ob, 9, "Skirt", (0,0,1), settings.vertices["Skirt"])
        addMaterial(ob, 10, "Hair", (1,1,0), settings.vertices["Hair"])
        addMaterial(ob, 11, "Ground", (1,0.5,0.5), (settings.vertices["Hair"][1], settings.nTotalVerts))

    if ob.MhDeleteHelpers:
        affect = "Body"
    else:
        affect = "All"
    deleteIrrelevant(ob, affect)


def addMaterial(ob, index, name, color, verts):
    first,last = verts
    try:
        mat = bpy.data.materials[name]
    except KeyError:
        mat = bpy.data.materials.new(name=name)
    ob.data.materials.append(mat)
    if mat.name != name:
        print(("WARNING: duplicate material %s => %s" % (name, mat.name)))
    mat.diffuse_color = color
    for f in ob.data.polygons:
        vn = f.vertices[0]
        if vn >= first and vn < last:
            f.material_index = index


def loadAndApplyTarget(context):
    bodytype = context.scene.MhBodyType
    if bodytype == 'None':
        return
    trgpath = os.path.join(os.path.dirname(__file__), "../makeclothes/targets", bodytype + ".target")
    try:
        utils.loadTarget(trgpath, context)
        found = True
    except FileNotFoundError:
        found = False
    if not found:
        raise MHError("Target \"%s\" not found.\nPath \"%s\" does not seem to be the path to the MakeHuman program" % (trgpath, scn.MhProgramPath))

    ob = context.object
    props = {}
    for key in list(ob.keys()):
        props[key] = ob[key]
    applyTargets(context)
    for key in list(props.keys()):
        ob[key] = props[key]
    ob.name = bodytype.split("-")[1]
    ob.shape_key_add(name="Basis")
    ob["NTargets"] = 0


def makeBaseObj(context):
    mh.proxy = None
    ob = context.object
    if ob.type != 'MESH':
        return
    for mod in ob.modifiers:
        if mod.type == 'ARMATURE':
            mod.show_in_editmode = True
            mod.show_on_cage = True
        else:
            ob.modifiers.remove(mod)
    utils.removeShapeKeys(ob)
    ob.shape_key_add(name="Basis")
    ob["NTargets"] = 0
    ob.ProxyFile = ""
    ob.ObjFile =  ""
    ob.MhHuman = True


def unmakeBaseObj(ob):
    utils.removeShapeKeys(ob)
    try:
        del ob["NTargets"]
    except KeyError:
        pass
    ob.MhHuman = False


def deleteIrrelevant(ob, affect):
    settings = getSettings(ob)
    if ob.MhIrrelevantDeleted or settings is None:
        return
    if affect != 'All':
        nVerts = len(ob.data.vertices)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for n in range(nVerts):
            ob.data.vertices[n].select = False
        for first,last in settings.irrelevantVerts[affect]:
            for n in range(first, last):
                ob.data.vertices[n].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        ob.MhMeshVertsDeleted = True
        ob.MhIrrelevantDeleted = True
        ob.MhAffectOnly = affect
        print(("Deleted verts: %d -> %d" % (first, last)))
        print(("# Verts: %d -> %d" % (nVerts, len(ob.data.vertices))))

#----------------------------------------------------------
#   loadTargetFromMesh(context):
#----------------------------------------------------------

def getMeshes(context):
    ob = context.object
    scn = context.scene
    if not utils.isBaseOrTarget(ob):
        raise MHError("Active object %s is not a base object" % ob.name)
    trg = None
    for ob1 in scn.objects:
        if ob1.select and ob1.type == 'MESH' and ob1 != ob:
            trg = ob1
            break
    if not trg:
        raise MHError("Two meshes must be selected")
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob,trg,scn


def createNewMeshShape(ob, name, scn):
    scn.objects.active = ob
    skey = ob.shape_key_add(name=name, from_mix=False)
    ob.active_shape_key_index = utils.shapeKeyLen(ob) - 1
    skey.name = name
    skey.slider_min = -1.0
    skey.slider_max = 1.0
    skey.value = 1.0
    ob.show_only_shape_key = False
    ob.use_shape_key_edit_mode = True
    ob["NTargets"] += 1
    ob["FilePath"] = 0
    ob.SelectedOnly = False
    return skey

def applyArmature(context):
    ob = context.object
    scn = context.scene
    rig = ob.parent
    if rig is None or rig.type != 'ARMATURE':
        raise MHError("Parent of %s is not an armature" % ob)

    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True
    bpy.ops.object.duplicate()
    bpy.ops.object.shape_key_remove(all=True)
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Armature")
    statue = context.object
    statue.name = "Statue"
    statue.parent = None
    return ob,rig,statue

def checkRotationMatrix(mat):
    for n in range(3):
        vec = mat.col[n]
        if abs(vec.length-1) > 0.1:
            print(("No rot %d %f\n%s" % (n, vec.length, mat)))
            return True
    return False

def doSaveTarget(context, filepath):
    global Comments
    ob = context.object
    settings = getSettings(ob)
    if not utils.isTarget(ob):
        raise MHError("%s is not a target")
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.active_shape_key_index = ob["NTargets"]
    if not checkValid(ob):
        return
    saveAll = not ob.SelectedOnly
    skey = ob.active_shape_key
    if skey.name[0:6] == "Target":
        skey.name = utils.nameFromPath(filepath)
    verts = evalVertLocations(ob)

    (fname,ext) = os.path.splitext(filepath)
    filepath = fname + ".target"
    print(("Saving target %s to %s" % (ob, filepath)))
    if False and ob.MhMeshVertsDeleted and ob.MhAffectOnly != 'All':
        first,last = settings.affectedVerts[ob.MhAffectOnly]
        before,after = readLines(filepath, first,last)
        fp = open(filepath, "w", encoding="utf-8", newline="\n")
        for line in before:
            fp.write(line)
        if ob.MhMeshVertsDeleted:
            offset = settings.offsetVerts[ob.MhAffectOnly]
        else:
            offset = 0
        saveVerts(fp, ob, verts, saveAll, first, last, offset)
        for (vn, string) in after:
            fp.write("%d %s" % (vn, string))
    else:
        fp = open(filepath, "w", encoding="utf-8", newline="\n")
        if Comments == []:
            Comments = getDefaultComments()
        for line in Comments:
            fp.write(line)
        saveVerts(fp, ob, verts, saveAll, 0, len(verts), 0)
    fp.close()
    ob["FilePath"] = filepath


def getDefaultComments():
    filepath = os.path.join(getMHBlenderDirectory(), "make_target.notice")
    try:
        fp = open(filepath, "rU")
    except:
        print(("Could not open %s" % filepath))
        return []
    comments = []
    for line in fp:
        comments.append(line)
    return comments


def readLines(filepath, first, last):
    before = []
    after = []
    try:
        fp = open(filepath, "rU")
    except FileNotFoundError:
        return before,after
    for line in fp:
        words = line.split(None, 1)
        if len(words) >= 2:
            vn = int(words[0])
            if vn < first:
                before.append(line)
            elif vn >= last:
                after.append((vn, words[1]))
    fp.close()
    return before,after


def saveVerts(fp, ob, verts, saveAll, first, last, offs):
    for n in range(first, last):
        vco = verts[n-offs]
        bv = ob.data.vertices[n-offs]
        vec = vco - bv.co
        if vec.length > Epsilon and (saveAll or bv.select):
            fp.write("%d %s %s %s\n" % (n, round(vec[0]), round(vec[2]), round(-vec[1])))


def evalVertLocations(ob):
    verts = {}
    for v in ob.data.vertices:
        verts[v.index] = v.co.copy()

    for skey in ob.data.shape_keys.key_blocks:
        if (skey.name == "Basis" or
            (ob.MhZeroOtherTargets and skey != ob.active_shape_key)):
            print(("Skipped", skey.name))
            continue
        print(("Adding", skey.name))
        for n,v in enumerate(skey.data):
            bv = ob.data.vertices[n]
            vec = v.co - bv.co
            verts[n] += skey.value*vec
    return verts


#----------------------------------------------------------
#   Apply targets to mesh
#----------------------------------------------------------

def applyTargets(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    verts = evalVertLocations(ob)
    utils.removeShapeKeys(ob)
    for prop in list(ob.keys()):
        del ob[prop]
    for v in ob.data.vertices:
        v.co = verts[v.index]
    return


#----------------------------------------------------------
#   batch
#----------------------------------------------------------

def batchFitTargets(context, folder):
    global Comments
    print(("Batch", folder))
    for fname in os.listdir(folder):
        (root, ext) = os.path.splitext(fname)
        file = os.path.join(folder, fname)
        if os.path.isfile(file) and ext == ".target":
            print(file)
            _,Comments = utils.loadTarget(file, context)
            fitTarget(context)
            doSaveTarget(context, file)
            discardTarget(context)
        elif os.path.isdir(file):
            batchFitTargets(context, file)
    return

#----------------------------------------------------------
#   batch render
#----------------------------------------------------------

def batchRenderTargets(context, folder, opengl, outdir):
    global Comments
    print(("Batch render", folder))
    for fname in os.listdir(folder):
        (root, ext) = os.path.splitext(fname)
        file = os.path.join(folder, fname)
        if os.path.isfile(file) and ext == ".target":
            print(file)
            context.scene.render.filepath = os.path.join(outdir, root)
            _,Comments = utils.loadTarget(file, context)
            if opengl:
                bpy.ops.render.opengl(animation=True)
            else:
                bpy.ops.render.render(animation=True)
            discardTarget(context)
        elif os.path.isdir(file):
            batchRenderTargets(context, file, opengl, outdir)
    return

#----------------------------------------------------------
#   fitTarget(context):
#----------------------------------------------------------

def fitTarget(context):
    ob = context.object
    settings = getSettings(ob)
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene
    if not utils.isTarget(ob):
        return
    ob.active_shape_key_index = ob["NTargets"]
    if not checkValid(ob):
        return
    if not mh.proxy:
        path = ob.ProxyFile
        if path:
            print(("Rereading %s" % path))
            mh.proxy = CProxy()
            mh.proxy.read(path)
        else:
            raise MHError("Object %s has no associated mhclo file. Cannot fit" % ob.name)
            return
    if ob.MhAffectOnly != 'All':
        first,last = settings.affectedVerts[ob.MhAffectOnly]
        mh.proxy.update(ob.active_shape_key.data, ob.active_shape_key.data, skipBefore=first, skipAfter=last)
    else:
        mh.proxy.update(ob.active_shape_key.data, ob.active_shape_key.data)
    return

#----------------------------------------------------------
#   discardTarget(context):
#----------------------------------------------------------

def discardTarget(context):
    ob = context.object
    if not utils.isTarget(ob):
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.active_shape_key_index = ob["NTargets"]
    bpy.ops.object.shape_key_remove()
    ob["NTargets"] -= 1
    ob.active_shape_key_index = ob["NTargets"]
    checkValid(ob)
    return

def checkValid(ob):
    nShapes = utils.shapeKeyLen(ob)
    if nShapes != ob["NTargets"]+1:
        print(("Consistency problem:\n  %d shapes, %d targets" % (nShapes, ob["NTargets"])))
        return False
    return True



MTIsInited = False

def init():
    global MTIsInited





    #bpy.types.Object.MhTightsOnly = BoolProperty(default = False)
    #bpy.types.Object.MhSkirtOnly = BoolProperty(default = False)




    from . import settings
    settings.init()
    from . import import_obj
    import_obj.init()
    #from . import character
    #character.init()
    from . import convert
    convert.init()
    from . import pose
    pose.init()

    MTIsInited = True


def initBatch():
    global TargetSubPaths
    TargetSubPaths = []
    folder = os.path.realpath(os.path.expanduser(scn.MhTargetPath))
    for fname in os.listdir(folder):
        file = os.path.join(folder, fname)
        if os.path.isdir(file) and fname[0] != ".":
            TargetSubPaths.append(fname)
            setattr(bpy.types.Scene, "Mh%s" % fname, BoolProperty(name=fname))
            scn["Mh%s" % fname] = False
    return


def isInited(scn):
    return True
    try:
        TargetSubPaths
        scn.MhTargetPath
        return True
    except:
        return False




