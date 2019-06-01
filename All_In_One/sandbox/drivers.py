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
from struct import pack, unpack
import bpy
from bpy.props import *
from mathutils import Vector

MHDir = "/home/svn/"

def addDriver(rig, rna, path, bprop, props, expr="x"):
    fcu = rna.driver_add(path)
    drv = fcu.driver
    drv.type = 'SCRIPTED'
    n = 1
    addDriverVar("x", bprop, drv, rig)
    for prop,val in props:
        addDriverVar("x%d" % n, prop, drv, rig)
        expr += "+%.3f*x%d" % (val, n)
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


def assignExpressionDrivers(rig, ob):
    drivers = {}
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if True or skey.name[0:3] == "Mhs":
            drivers[skey.name] = (skey,[])
        rig["Mhs"+skey.name] = 0.0

    if drivers == {}:
        return

    mhmDir = os.path.join(MHDir, "data/expressions")
    for file in os.listdir(mhmDir):
        fname,ext = os.path.splitext(file)
        if ext == ".mhm":
            prop = "Mht" + fname
            rig[prop] = 0.0
            filepath = os.path.join(mhmDir, file)
            with open(filepath, "rU") as fp:
                for line in fp:
                    words = line.split()
                    if len(words) > 0 and words[0] == "expression":
                        key = words[1]
                        val = float(words[2])
                        drivers[key][1].append((prop,val))

    for skey,props in drivers.values():
        addDriver(rig, skey, "value", "Mhs"+skey.name, props)


def hasExpressions(ob):
    if (ob.type != 'MESH' or
        ob.data.shape_keys is None):
        return False
    for skey in ob.data.shape_keys.key_blocks:
        print(skey)
        #if skey.name[0:3] == "Mhs":
        if skey.name != "Basis":
            return True
    print("NON")
    return False


class VIEW3D_OT_CreateExpressionDriverButton(bpy.types.Operator):
    bl_idname = "mp.create_expression_drivers"
    bl_label = "Create Expression Drivers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        for ob in rig.children:
            if hasExpressions(ob):
                assignExpressionDrivers(rig, ob)
        rig.MPVisemeDriversAssigned = True
        return{'FINISHED'}


def resetExpressionKeys(rig):
    for key in rig.keys():
        if key[0:3] in ["Mhs", "Mht"]:
            rig[key] = 0.0


class VIEW3D_OT_PinExpressionKeyButton(bpy.types.Operator):
    bl_idname = "mp.pin_expression_key"
    bl_label = "Pin Expression Key"
    bl_options = {'UNDO'}

    key = StringProperty()

    def execute(self, context):
        rig = context.object
        resetExpressionKeys(rig)
        rig[self.key] = 1.0
        return{'FINISHED'}


class VIEW3D_OT_ResetExpressionKeysButton(bpy.types.Operator):
    bl_idname = "mp.reset_expression_keys"
    bl_label = "Reset Expression Keys"
    bl_options = {'UNDO'}

    def execute(self, context):
        resetExpressionKeys(context.object)
        return{'FINISHED'}

#
#
#

def getArmature(ob):
    if ob is None or ob.type != 'MESH':
        return None
    for mod in ob.modifiers:
        if mod.type == 'ARMATURE':
            return mod.object
    return None


class VIEW3D_OT_CreateHideDriverButton(bpy.types.Operator):
    bl_idname = "mp.create_hide_drivers"
    bl_label = "Create Hide Drivers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        scn = context.scene
        if not rig:
            return{'FINISHED'}

        for ob in scn.objects:
            if rig == getArmature(ob):
                prop = "Mhh%s" % ob.name
                rig[prop] = False
                addDriver(rig, ob, "hide", prop, [])
                addDriver(rig, ob, "hide_render", prop, [])
                for mod in ob.modifiers:
                    if mod.type == 'MASK':
                        cloname = mod.vertex_group.split("_",1)[1]
                        mprop = prop[:-4] + cloname
                        print(mprop)
                        addDriver(rig, mod, "show_viewport", mprop, [], expr = "not(x)")
                        addDriver(rig, mod, "show_render", mprop, [], expr = "not(x)")
        return{'FINISHED'}
