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
import mathutils
import math
from bpy.props import *

from mh_utils import mh
from mh_utils import utils
from mh_utils import proxy
from mh_utils import character
from mh_utils import warp
from mh_utils import import_obj

Epsilon = 1e-4

#----------------------------------------------------------
#   Base character
#----------------------------------------------------------

class VIEW3D_OT_CreateBaseCharacterButton(bpy.types.Operator):
    bl_idname = "mh.create_base_character"
    bl_label = "Create Base Character"
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = context.scene
        try:
            base = getBaseChar(context)
        except:
            base = None
        if base:
            scn.objects.unlink(base)
            
        char = character.CCharacter("Base")
        char.setCharacterProps(context)
        char.updateFiles(scn)
        char.loadTargets(context)
        
        base = char.object
        layers = 20*[False]
        layers[1] = True
        base.layers = layers
        base["MhStatus"] = "Base"
        
        scn = context.scene
        scn.layers[0] = True
        scn.layers[1] = True
        scn.objects.active = base
        scn["MhBaseChar"] = base.name

        return{'FINISHED'}    

#----------------------------------------------------------
#   Generate mask
#----------------------------------------------------------

def generateMask(context):
    scn = context.scene
    base = getBaseChar(context)
    try:
        mask = getMask(context)
    except:
        mask = None
    if mask:
        scn.objects.unlink(mask)
    
    # Load proxy
    maskProxy = proxy.CProxy()
    userpath = os.path.expanduser(os.path.dirname(__file__))
    filepath = os.path.join(userpath, "mask.mhclo")
    print("Proxy", filepath)
    maskProxy.read(filepath)

    # Create mask object
    mask = import_obj.importObj(maskProxy.obj_file, context)
    print(mask)
    layers = 20*[False]
    layers[0] = True
    mask.layers = layers
    mask.draw_type = 'WIRE'
    mask.show_x_ray = True        
    scn["MhMask"] = mask.name
    mask["MhStatus"] = "Mask"
    scn.objects.active = mask

    # Load targets      
    n = 1
    for baseKey in base.data.shape_keys.key_blocks[1:]:
        maskKey = mask.shape_key_add(name=baseKey.name, from_mix=False)
        maskKey.value = baseKey.value
        mask.active_shape_key_index = n
        maskProxy.update(baseKey.data, maskKey.data)
        n += 1
        
    skey = mask.shape_key_add(name="Shape", from_mix=False)
    skey.value = 1.0
    mask.use_shape_key_edit_mode = True
    mask.active_shape_key_index = n
    mask["MhMaskObjFile"] = maskProxy.obj_file


class VIEW3D_OT_GenerateMaskButton(bpy.types.Operator):
    bl_idname = "mh.generate_mask"
    bl_label = "Generate Mask"
    bl_options = {'UNDO'}

    def execute(self, context):
        generateMask(context)
        print("Mask imported")
        return{'FINISHED'}          

#----------------------------------------------------------
#   Generate face
#----------------------------------------------------------

def generateFace(context):
    mask = getMask(context)
    base = getBaseChar(context)
    warpField = warp.CWarp(context)
    warpField.setupFromObject(mask, context)
    #createTestFace(context, warpField, mask)
    warpField.warpMesh(mask, base)
    scn = context.scene
    scn.objects.active = base


def createTestFace(context, warpField, mask):
    scn = context.scene
    scn.objects.active = mask
    bpy.ops.object.duplicate()
    ob = context.object
    ob.name = "Test"
    utils.removeShapeKeys(ob)
    ob.layers[2] = True
    ob.layers[0] = False
    print(ob)
    for v in mask.data.vertices:
        v1 = ob.data.vertices[v.index]
        v1.co = warpField.warpLoc(v.co)
        #utils.printVec("X%d" % v.index, v.co)
        #utils.printVec("Y%d" % v1.index, v1.co)

    
class VIEW3D_OT_GenerateFaceButton(bpy.types.Operator):
    bl_idname = "mh.generate_face"
    bl_label = "Generate Face"
    bl_options = {'UNDO'}
    delete = BoolProperty()

    def execute(self, context):
        generateFace(context)
        print("Face generated")
        return{'FINISHED'}    

#----------------------------------------------------------
#   Save face as
#----------------------------------------------------------

class VIEW3D_OT_SaveFaceButton(bpy.types.Operator):
    bl_idname = "mh.save_face"
    bl_label = "Save Face"
    bl_options = {'UNDO'}

    def execute(self, context):
        path = context.object.MhMaskFilePath
        if mh.Confirm:
            mh.Confirm = None
            doSaveTarget(context, path, False)
        else:
            mh.Confirm = "mh.save_face"
            mh.ConfirmString = "Overwrite target file?"
            mh.ConfirmString2 = ' "%s?"' % os.path.basename(path)
        return{'FINISHED'}    


class VIEW3D_OT_SaveFaceAsButton(bpy.types.Operator):
    bl_idname = "mh.save_face_as"
    bl_label = "Save Face As"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for target file", 
        maxlen= 1024, default= "")

    def execute(self, context):
        doSaveTarget(context, self.properties.filepath, True)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def doSaveTarget(context, filepath, saveas):    
    mask = getMask(context)
    base = getBaseChar(context)
    (fname,ext) = os.path.splitext(filepath)
    filepath = fname + ".target"
    fp = open(filepath, "w", encoding="utf-8", newline="\n")  
    skey = base.data.shape_keys.key_blocks[-1]
    if skey.name == "Shape":
        skey.name = os.path.basename(fname)
    print("Saving target %s to %s" % (skey.name, filepath))
    for v in base.data.vertices:
        vn = v.index
        vec = skey.data[vn].co - v.co
        if vec.length > Epsilon:
            fp.write("%d %.4f %.4f %.4f\n" % (vn, vec[0], vec[2], -vec[1]))
    fp.close()    
    base["MhMaskFilePath"] = filepath
    print("Target saved")
    return

#----------------------------------------------------------
#   Utilities
#----------------------------------------------------------

class VIEW3D_OT_MakeMaskButton(bpy.types.Operator):
    bl_idname = "mh.make_mask"
    bl_label = "Make Mask"
    bl_options = {'UNDO'}

    def execute(self, context):
        ob = context.object
        the.Mask.object = ob
        ob.shape_key_add(name="Basis")
        ob.shape_key_add(name="Target")
        ob.shape_key_add(name="Shape")
        ob.active_shape_key_index = 2
        return {'FINISHED'}


def getMask(context):
    scn = context.scene
    print("Look for mask", scn.MhMask)
    mask = None
    for ob in scn.objects:
        if ob.name == scn.MhMask:
            return ob
        if ob.MhStatus == 'Mask':
            mask = ob
    if mask:
        return mask
    raise NameError("Did not find mask")            
    

def getBaseChar(context):
    scn = context.scene
    print("Look for base", scn.MhBaseChar)
    base = None
    for ob in scn.objects:
        if ob.name == scn.MhBaseChar:
            return ob
        if ob.MhStatus == 'Base':
            base = ob
    if base:
        return base
    raise NameError("Did not find base charact")            
    

class VIEW3D_OT_SkipButton(bpy.types.Operator):
    bl_idname = "mh.skip"
    bl_label = "No"
    bl_options = {'UNDO'}

    def execute(self, context):
        utils.skipConfirm()
        return{'FINISHED'}            

#----------------------------------------------------------
#   Init
#----------------------------------------------------------

def init():
    bpy.types.Object.MhStatus = StringProperty(default = "")
    bpy.types.Object.MhMaskFilePath = StringProperty(default = "")
    bpy.types.Scene.MhMask = StringProperty(default = "")
    bpy.types.Scene.MhBaseChar = StringProperty(default = "")
    return  
    
