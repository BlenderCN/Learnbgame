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
from bpy.props import *

Visemes = {

    "AH" : [
        ("lips_mid_height_upper",0.40),
        ("mouth_open", 0.70),
        ],

    "EE" : [
        ("lips_mid_height_upper", 0.60),
        ("lips_mid_height_lower", 0.60),
        ("mouth_corner_depth", 0.20),
        ("mouth_open", 0.05),
        ],

    "EH" : [
        ("lips_mid_height_upper", 0.50),
        ("lips_mid_height_lower", 0.60),
        ("mouth_open", 0.25),
        ],

    "ETC" : [
        ("lips_part", 1.0),
        ],

    "F" : [
        ("lips_part", 1.0),
        ("lips_in_lower", 0.6),
        ("mouth_narrow", 0.20),
        ("lips_mid_height_lower", 0.30),
        ],

    "G" : [
        ("tongue_back_height", 1.0),
        ("mouth_open", 0.20),
        ("lips_mid_height_upper", 0.50),
        ("lips_mid_height_lower", 0.50),
        ],

    "IH" : [
        ("mouth_open", 0.10),
        ("lips_mid_height_upper", 0.50),
        ("lips_mid_height_lower", 0.70),
        ],

    "L" : [
        ("tongue_height", 1.0),
        ("tongue_depth", 1.0),
        ("mouth_open", 0.20),
        ("lips_mid_height_upper", 0.50),
        ("lips_mid_height_lower", 0.50),
        ],

    "O" : [
        ("mouth_open", 0.80),
        ("mouth_narrow", 0.90),
        ],

    "OO" : [
        ("mouth_open", 0.40),
        ("mouth_narrow", 1.0),
        ],

    "R" : [
        ("mouth_narrow", 0.50),
        ("lips_mid_height_upper", 0.20),
        ("lips_mid_height_lower", 0.20),
        ],

    "S" : [
        ("lips_mid_height_upper", 0.50),
        ("lips_mid_height_lower", 0.70),
        ],

    "SH" : [
        ("mouth_narrow", 0.80),
        ("lips_mid_height_upper", 1.0),
        ("lips_mid_height_lower", 1.0),
        ],

    "TH" : [
        ("tongue_height", 0.60),
        ("tongue_width", 1.0),
        ("tongue_depth", 1.0),
        ("mouth_open", 0.20),
        ("lips_mid_height_upper", 0.50),
        ("lips_mid_height_lower", 0.50),
        ],
}


def hasVisemes(ob):
    if (ob.type != 'MESH' or
        ob.data.shape_keys is None):
        return False
    print(ob)
    try:
        ob.data.shape_keys.key_blocks["mouth_narrow.L"]
        return True
    except KeyError:
        return False


class VIEW3D_OT_ClearVisemesButton(bpy.types.Operator):
    bl_idname = "mp.clear_visemes"
    bl_label = "Clear"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        for key in Visemes.keys():
            rig["MP"+key] = 0.0
        return{'FINISHED'}


"""
      Driver AVERAGE
        DriverVariable PBrows TRANSFORMS
          Target foo OBJECT
             transform_type 'LOC_Z' ;
             bone_target 'PBrows' ;
             transform_space 'LOCAL_SPACE' ;
          end Target
        end DriverVariable
        show_debug_info True ;
      end Driver
      FModifier GENERATOR
        active False ;
        use_additive False ;
        coefficients Array 0 -4 ;
        show_expanded True ;
        mode 'POLYNOMIAL' ;
        mute False ;
        poly_order 1 ;
      end FModifier
"""

def assignDrivers(rig, ob):
    fcurves = {}
    skeys = ob.data.shape_keys
    for vis,vals in Visemes.items():
        for key,val in vals:
            addDriver(skeys, rig, vis, key+".L", val, fcurves)
            addDriver(skeys, rig, vis, key+".R", val, fcurves)
            addDriver(skeys, rig, vis, key, val, fcurves)


def addDriver(skeys, rig, vis, name, val, fcurves):
    try:
        skey = skeys.key_blocks[name]
    except KeyError:
        return
    try:
        fcu = fcurves[name]
    except KeyError:
        fcu = None
    addScriptedDriver(fcu, skeys, rig, vis, name, val, fcurves)


def addScriptedDriver(fcu, skeys, rig, vis, name, val, fcurves):
    if fcu is None:
        fcu = fcurves[name] = skeys.driver_add('key_blocks["%s"].value' % name)
        drv = fcu.driver
        drv.type = 'SCRIPTED'
        drv.expression = ""
        drv.show_debug_info = True
        if len(fcu.modifiers) > 0:
            fmod = fcu.modifiers[0]
            fcu.modifiers.remove(fmod)
    else:
        drv = fcu.driver
        drv.expression += " + "

    var = drv.variables.new()
    var.name = vis
    var.type = 'SINGLE_PROP'
    trg = var.targets[0]
    trg.id_type = 'OBJECT'
    trg.id = rig
    trg.data_path = "MP%s" % vis
    drv.expression += "%.3f*%s" % (val, vis)


class VIEW3D_OT_CreateVisemeDriversButton(bpy.types.Operator):
    bl_idname = "mp.create_viseme_drivers"
    bl_label = "Create Drivers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        if rig.MPVisemeDriversAssigned:
            halt
            return{'FINISHED'}
        for ob in rig.children:
            if hasVisemes(ob):
                assignDrivers(rig, ob)
        rig.MPVisemeDriversAssigned = True
        return{'FINISHED'}


def init():

    bpy.types.Object.MPVisemeDriversAssigned = BoolProperty(default=False)

    for key in Visemes.keys():

        prop = FloatProperty(
            name=key,
            description="Viseme %s" % key,
            min=0.0, max=1.0)

        setattr(bpy.types.Object, "MP"+key, prop)