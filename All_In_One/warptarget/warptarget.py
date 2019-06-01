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
import os
from bpy.props import *
import mathutils
import numpy

from mh_utils import mh
from mh_utils import utils
from mh_utils import character
from mh_utils import warp


Epsilon = 1e-4

theSettings = mh.CSettings("alpha7")


class CWarpCharacter:

    def __init__(self, name):
        self.character = character.CCharacter(name)
        self.verts = {}
        self.landmarks = {}
        self.landmarkVerts = {}


    def readVerts(self, context):                
        scn = context.scene

        base = os.path.join(scn.MhProgramPath, "data/3dobjs/base.obj")
        fp = open(base, "r")
        self.verts = {}
        n = 0
        for line in fp:
            words = line.split()
            if len(words) >= 4:
                if words[0] == "v":
                    self.verts[n] = mathutils.Vector( (float(words[1]),  float(words[2]),  float(words[3])) )
                    n += 1
        fp.close()                    
        
        prefix = os.path.join(scn.MhProgramPath, "data/targets/")
        ext = ".target"
        for (folder, file, value) in self.character.files:
            path = os.path.join(prefix, folder, file + ".target")
            try:
                print("File", path)
                fp = open(path, "rU")
            except:
                print("No such file", path)
                continue
            for line in fp:
                words = line.split()
                if len(words) >= 4:
                    n = int(words[0])
                    self.verts[n] += value*mathutils.Vector( (float(words[1]),  float(words[2]),  float(words[3])) )
            fp.close()  
            
        (self.landmarks, self.landmarkVerts) = warp.readLandMarks(context, self.verts)
                
    def readMorph(self, path):
        fp = open(path, "r")
        dx = {}
        for line in fp:
            words = line.split()
            if len(words) >= 4:
                n = int(words[0])
                dx[n] = mathutils.Vector( (float(words[1]),  float(words[2]),  float(words[3])) )
        fp.close()
        return dx

#----------------------------------------------------------
#   Load Character
#----------------------------------------------------------

class VIEW3D_OT_LoadSourceCharacterButton(bpy.types.Operator):
    bl_idname = "mh.load_source_character"
    bl_label = "Load Source Character"
    bl_options = {'UNDO'}

    def execute(self, context):
        theSourceCharacter.character.loadTargets(context)
        return{'FINISHED'}    
    

class VIEW3D_OT_LoadTargetCharacterButton(bpy.types.Operator):
    bl_idname = "mh.load_target_character"
    bl_label = "Load Target Character"
    bl_options = {'UNDO'}

    def execute(self, context):
        theTargetCharacter.character.loadTargets(context)
        return{'FINISHED'}    
    
    
class VIEW3D_OT_UpdateLandmarksButton(bpy.types.Operator):
    bl_idname = "mh.update_landmarks"
    bl_label = "Update Landmarks"
    bl_options = {'UNDO'}

    def execute(self, context):
        warp.updateLandmarks(context)
        return{'FINISHED'}    
    
       
#----------------------------------------------------------
#   Set Morph
#----------------------------------------------------------

def partitionTargetPath(path):
    (before, sep, after) = path.partition("/targets/")
    if sep:
        return (before+sep, after)
    (before, sep, after) = path.partition("\\targets\\")
    if sep:
        return (before+sep, after)
    return ("", path)        
        

class VIEW3D_OT_SetSourceMorphButton(bpy.types.Operator):
    bl_idname = "mh.set_source_morph"
    bl_label = "Set Source Morph"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for source target file", 
        maxlen= 1024, default= "")

    def execute(self, context):
        global theSourceCharacter
        scn = context.scene
        (scn.MhSourceMorphTopDir, scn.MhSourceMorphDir) = partitionTargetPath(os.path.dirname(self.properties.filepath))
        scn.MhSourceMorphFile = os.path.basename(self.properties.filepath)    
        theSourceCharacter = CWarpCharacter("Source")
        partOnly = (context.scene.MhWarpPart != 'All')
        theSourceCharacter.character.fromFilePath(context, scn.MhSourceMorphDir, True, include=partOnly)
        theSourceCharacter.character.fromFilePath(context, scn.MhSourceMorphFile, True, include=partOnly, folder=scn.MhSourceMorphDir)
        updateTargetMorph(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_UpdateTargetCharacterButton(bpy.types.Operator):
    bl_idname = "mh.update_target_character"
    bl_label = "Update Target Character"
    bl_options = {'UNDO'}

    def execute(self, context):
        theTargetCharacter.character.setCharacterProps(context)
        updateTargetMorph(context)
        return{'FINISHED'}    


def updateTargetMorph(context):
    scn = context.scene
    partOnly = (scn.MhWarpPart != 'All')
    scn.MhTargetMorphTopDir = scn.MhSourceMorphTopDir
    scn.MhTargetMorphDir = theTargetCharacter.character.fromFilePath(context, scn.MhSourceMorphDir, False, subdirs=scn.MhUseSubdirs)
    scn.MhTargetMorphFile = theTargetCharacter.character.fromFilePath(context, scn.MhSourceMorphFile, False, subdirs=True, include=partOnly, folder=scn.MhTargetMorphDir)

#----------------------------------------------------------
#   Warp morph
#----------------------------------------------------------

def addToMorph(dxs, x0):
    xlocs = {}
    for n in dxs.keys():
        xlocs[n] = dxs[n] + x0[n]
    return xlocs        


def subFromMorph(ylocs, y0):
    dys = {}
    for n in ylocs.keys():
        dys[n] = ylocs[n] - y0[n]
    return dys
    
    
def getVertexRange(locs, first, last):
    part = {}
    for n in locs.keys():
        if n in range(first,last):
            part[n] = locs[n]
    return part
    
    
def subRange(ylocs, y0, first, last):
    dys = {}
    for n in ylocs.keys():
        if n in range(first,last):
            try:
                dys[n] = ylocs[n] - y0[n]
            except KeyError:
                dys[n] = ylocs[n]
    return dys
    
    
def saveTarget(path, dxs, scn, first, last, active):
    print("Saving target %s" % path)
    folder = os.path.dirname(path)
    if not os.path.isdir(folder):
        print("Creating target folder %s" % folder)
        os.makedirs(folder)    
        
    before,after = readLines(path, first, last)
    print("RL", len(before), len(after), first, last)
    #halt
        
    fp = open(path, "w", encoding="utf-8", newline="\n")
    keys = list( dxs.keys() )
    keys.sort()
    
    for line in before:
        fp.write(line)
    for n in keys:
        if n >= first and n < last and (active == None or active[n]):
            dx = dxs[n]
            if dx.length > 1e-4:
                fp.write("%d %.4g %.4g %.4g\n" % (n, dx[0], dx[1], dx[2]))
    for line in after:
        fp.write(line)
    fp.close()
    return        


def readLines(filepath, first, last):
    before = []
    after = []
    try:
        fp = open(filepath, "rU")
    except FileNotFoundError:
        return before,after
    for line in fp:
        words = line.split()
        if len(words) >= 2:
            vn = int(words[0])
            if vn >= last:
                after.append(line)
            elif vn < first:
                before.append(line)
    fp.close()
    return before,after
    
    
def saveVerts(fp, ob, verts, saveAll, first, last, offs):
    for n in range(first, last):
        vco = verts[n-offs]
        bv = ob.data.vertices[n-offs]
        vec = vco - bv.co
        if vec.length > Epsilon and (saveAll or bv.select):
            fp.write("%d %.6f %.6f %.6f\n" % (n, vec[0], vec[2], -vec[1]))


def printVerts(string, verts, keys):
    print(string)
    for n in keys[0:6]:
        x = verts[n]
        print("  %d %.4g %.4g %.4g" % (n, x[0], x[1], x[2]))
        

def warpMorph(context):    
    scn = context.scene
    warpField = warp.CWarp(context)
    warpField.setupFromCharacters(context, theSourceCharacter, theTargetCharacter)
    srcPath = os.path.join(scn.MhSourceMorphTopDir, scn.MhSourceMorphDir, scn.MhSourceMorphFile)
    trgPath = os.path.join(scn.MhTargetMorphTopDir, scn.MhTargetMorphDir, scn.MhTargetMorphFile)
    if scn.MhWarpAllMorphsInDir:
        srcDir = os.path.dirname(srcPath)
        trgDir = os.path.dirname(trgPath)
        for file in os.listdir(srcDir):
            (fname, ext) = os.path.splitext(file)
            if ext == ".target":
                warpSingleMorph(os.path.join(srcDir, file), os.path.join(trgDir, file), warpField, scn)
    else:
        warpSingleMorph(srcPath, trgPath, warpField, scn)
    print("File(s) warped")        
        

def setActive(verts, scn):
    if scn.MhKeepActive:
        active = numpy.zeros(theSettings.nTotalVerts, bool)
        for n in verts.keys():
            active[n] = True
    else:
        return None
    return active
    
    
def warpSingleMorph(srcPath, trgPath, warpField, scn): 
    print("Warp %s -> %s" % (srcPath, trgPath))
    if scn.MhWarpPart == 'All':    
        dxs = theSourceCharacter.readMorph(srcPath)
        xlocs = addToMorph(dxs, theSourceCharacter.verts)
        ylocs = warpField.warpLocations(xlocs)
        dys = subFromMorph(ylocs, theTargetCharacter.verts)
        active = setActive(dxs, scn)
        saveTarget(trgPath, dys, scn, 0, theSettings.nTotalVerts, active)            
    else:
        first, last = theSettings.vertices[scn.MhWarpPart]
        print(scn.MhWarpPart, first, last)
        dxs = theSourceCharacter.readMorph(srcPath)
        active = setActive(dxs, scn)
        dyOld = theTargetCharacter.readMorph(trgPath)
        dyOldPart = getVertexRange(dyOld, first, last)
        basePart = getVertexRange(theTargetCharacter.verts, first, last)
        basePart = subRange(basePart, dyOldPart, first, last)

        xsPart = getVertexRange(theSourceCharacter.verts, first, last)
        ysPart = warpField.warpLocations(xsPart)
        dyNew = subRange(ysPart, basePart, first, last)
        saveTarget(trgPath, dyNew, scn, first, last, active)            
        


    """
    keys = list( dxs.keys() )
    keys.sort()
    printVerts("x0", theSourceCharacter.verts, keys)
    printVerts("y0", theTargetCharacter.verts, keys)
    printVerts("dx", dxs, keys)
    printVerts("xlocs", xlocs, keys)
    printVerts("ylocs", ylocs, keys)
    printVerts("dy", dys, keys)
    """
    return


class VIEW3D_OT_WarpMorphButton(bpy.types.Operator):
    bl_idname = "mh.warp_morph"
    bl_label = "Warp Morph(s)"
    bl_options = {'UNDO'}

    def execute(self, context):
        warpMorph(context)
        return{'FINISHED'}   

#----------------------------------------------------------
#   Initialization
#----------------------------------------------------------

def init():
    global theSourceCharacter, theTargetCharacter

    bpy.types.Scene.MhSourceMorphTopDir = StringProperty(
        name = "Source Top Directory",
        default = "")
        
    bpy.types.Scene.MhSourceMorphDir = StringProperty(
        name = "Source Directory",
        default = "")
        
    bpy.types.Scene.MhSourceMorphFile = StringProperty(
        name = "Source File",
        default = "")
        
    bpy.types.Scene.MhTargetMorphTopDir = StringProperty(
        name = "Target Top Directory",
        default = "")
        
    bpy.types.Scene.MhTargetMorphDir = StringProperty(
        name = "Target Directory",
        default = "")
        
    bpy.types.Scene.MhTargetMorphFile = StringProperty(
        name = "Target File",
        default = "")

    bpy.types.Scene.MhWarpAllMorphsInDir = BoolProperty(
        name = "Warp All Morphs In Directory",
        default = False)

    bpy.types.Scene.MhUseSubdirs = BoolProperty(
        name = "Use Subdirectories for tone and weight",
        default = True)
        
    bpy.types.Scene.MhKeepActive = BoolProperty(
        name = "Keep active verts",
        default = True)                

    bpy.types.Scene.MhWarpPart = EnumProperty(
            name="Warp part",
            description="Part of character to be warped",
            items=(('Skirt', 'Skirt', 'Skirt'),
                   ('Tights', 'Tights', 'Tights'),
                   ('All', 'All', 'All'),
                  ),
            default='All',
            )
  


    theSourceCharacter = CWarpCharacter("Source")
    theTargetCharacter = CWarpCharacter("Target")
    
    
