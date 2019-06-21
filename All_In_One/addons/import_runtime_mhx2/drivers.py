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
import bpy
from bpy.props import *
from mathutils import *
from .utils import *

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def addDrivers(rig, rna, path, data, exprs):
    fcurves = rna.driver_add(path)
    for idx,fcu in enumerate(fcurves):
        if idx > 0:
            addScriptedDriver(fcu, rig, None, data[idx], exprs[idx], True)


def addDriver(rig, rna, path, bprop, data=[], expr="", extendExpression=True):
    fcu = rna.driver_add(path)
    addScriptedDriver(fcu, rig, bprop, data, expr, extendExpression)


def addScriptedDriver(fcu, rig, bprop, data, expr, extendExpression):
    drv = fcu.driver
    drv.type = 'SCRIPTED'
    n = 1
    if bprop is not None:
        addDriverVar("x", bprop, drv, rig)
    for prop,val in data:
        addDriverVar("x%d" % n, prop, drv, rig)
        if not extendExpression:
            pass
        elif val == 1:
            expr += " + x%d" % n
        elif val > 0.0006:
            expr += " + %.3f*x%d" % (val, n)
        elif val < -0.0006:
            expr += " - %.3f*x%d" % (-val, n)
        n += 1
    drv.expression = expr

    if len(fcu.modifiers) > 0:
        fmod = fcu.modifiers[0]
        fcu.modifiers.remove(fmod)


def addDriverVar(vname, prop, drv, rig):
    var = drv.variables.new()
    var.name = vname
    var.type = 'SINGLE_PROP'
    trg = var.targets[0]
    trg.id_type = 'OBJECT'
    trg.id = rig
    trg.data_path = '["%s"]' % prop


def initRnaProperties(rig):
    try:
        rig["_RNA_UI"]
    except KeyError:
        rig["_RNA_UI"] = {}


def deleteRigProperty(rig, prop):
    try:
        del rig[prop]
    except KeyError:
        pass
    try:
        del rig["_RNA_UI"][prop]
    except KeyError:
        pass

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def addBoneShapeDrivers(rig, human, boneDrivers, proxies=[], proxyTypes=[]):
    print("Setting up bone-shape drivers")

    if human:
        for sname,data in boneDrivers.items():
            addBoneShapeDriver(rig, human, sname, data)

    for mhGeo,ob in proxies:
        mhProxy = mhGeo["proxy"]
        if mhProxy["type"] in proxyTypes:
            for sname,data in boneDrivers.items():
                addBoneShapeDriver(rig, ob, sname, data)


def addBoneShapeDriver(rig, ob, sname, data):
    # 'nose_wrinkle' : ('p_brow_mid', 'LOC_Z', pos, 0, 1)
    bname,channel,coeffs,_min,_max = data
    try:
        rig.pose.bones[bname]
        useLR = False
    except KeyError:
        rig.pose.bones[bname+".L"]
        useLR = True

    fac = coeffs[1]/rig.MhxScale

    if channel == 'LOC_X':
        rsign = -1
    else:
        rsign = 1

    if useLR:
        addBoneShapeDriver1(rig, ob, sname+"_left", bname+".L", data, fac)
        addBoneShapeDriver1(rig, ob, sname+"_right", bname+".R", data, fac*rsign)
    else:
        addBoneShapeDriver1(rig, ob, sname, bname, data, fac)


def addBoneShapeDriver1(rig, ob, sname, bname, data, fac):
    try:
        skey = ob.data.shape_keys.key_blocks[sname]
    except KeyError:
        #print("%s has no such shape_key: %s" % (ob.name, sname))
        return

    _bname,channel,_coeffs,smin,smax = data
    fcu = skey.driver_add("value")
    drv = fcu.driver
    drv.type = 'AVERAGE'

    var = drv.variables.new()
    var.type = 'TRANSFORMS'

    trg = var.targets[0]
    trg.id = rig
    trg.bone_target = bname
    trg.transform_type = channel
    trg.transform_space = 'LOCAL_SPACE'

    fmod = fcu.modifiers[0]
    fmod.coefficients[0] = 0
    fmod.coefficients[1] = fac

    fmod = fcu.modifiers.new('LIMITS')
    fmod.use_min_y = True
    fmod.min_y = smin
    fmod.use_max_y = True
    fmod.max_y = smax

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def getRigMeshes(context):
    if context.object.type == 'ARMATURE':
        rig = context.object
        meshes = []
        for ob in context.scene.objects:
            if ob.parent == rig and ob.type == 'MESH':
                meshes.append(ob)
        return rig,meshes

    elif context.object.type == 'MESH':
        ob = context.object
        rig = ob.parent
        if rig and rig.type == 'ARMATURE':
            return rig,[ob]

    return None,[]


def getBoneName(fcu):
    return fcu.data_path.split('"')[1]

#------------------------------------------------------------------------
#   User interface
#------------------------------------------------------------------------

def resetProps(rig, prefix, scn):
    for key in rig.keys():
        if key[0:3] == prefix:
            rig[key] = 0.0
            autoKeyProp(rig, key, scn)


def autoKeyProp(rig, key, scn):
    if scn.tool_settings.use_keyframe_insert_auto:
        rig.keyframe_insert('["%s"]' % key, frame=scn.frame_current)


class VIEW3D_OT_PinPropButton(bpy.types.Operator):
    bl_idname = "mhx2.pin_prop"
    bl_label = ""
    bl_description = "Pin property"
    bl_options = {'UNDO'}

    key = StringProperty()
    prefix = StringProperty()

    def execute(self, context):
        rig = getArmature(context.object)
        scn = context.scene
        if rig:
            resetProps(rig, self.prefix, scn)
            rig[self.key] = 1.0
            autoKeyProp(rig, self.key, scn)
            updateScene(context)
        return{'FINISHED'}


class VIEW3D_OT_ResetPropsButton(bpy.types.Operator):
    bl_idname = "mhx2.reset_props"
    bl_label = "Reset Props"
    bl_description = ""
    bl_options = {'UNDO'}

    prefix = StringProperty()

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            resetProps(rig, self.prefix, context.scene)
            updateScene(context)
        return{'FINISHED'}
