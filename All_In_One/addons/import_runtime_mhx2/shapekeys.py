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
from mathutils import Vector

from .drivers import *
from .utils import zup2

#------------------------------------------------------------------------
#   Setup shapekeys
#------------------------------------------------------------------------

def addShapeKeys(human, filename, mhHuman, proxies=[], proxyTypes=[]):
    from .load_json import loadJsonRelative
    from .proxy import proxifyTargets

    print("Setting up shapekeys")
    struct = loadJsonRelative(filename)
    scales = getScales(human, struct["bounding_box"], mhHuman)
    if human:
        addTargets(human, struct["targets"], scales)
        human.MhxHasFaceShapes = True

    for mhGeo,ob in proxies:
        mhProxy = mhGeo["proxy"]
        if mhProxy["type"] in proxyTypes:
            ptargets = proxifyTargets(mhProxy, struct["targets"])
            addTargets(ob, ptargets, scales)
            ob.MhxHasFaceShapes = True


def addTargets(ob, targets, scales):
    targets = list(targets.items())
    targets.sort()
    if not ob.data.shape_keys:
        basic = ob.shape_key_add("Basis")
    else:
        basic = ob.data.shape_keys.key_blocks[0]

    for tname,data in targets:
        skey = ob.shape_key_add(tname)
        skey.value = 0
        skey.slider_min = -0.5
        skey.slider_max = 1.5
        for v in ob.data.vertices:
            skey.data[v.index].co = v.co
        nVerts = len(ob.data.vertices)
        for vn,delta in data[:nVerts]:
            if vn >= nVerts:
                break
            skey.data[vn].co += zup2(delta, scales)


def getScales(human, struct, mhHuman):
    scale = mhHuman["scale"]
    scales = Vector((scale,scale,scale))
    if mhHuman:
        verts = mhHuman["seed_mesh"]["vertices"]
        for comp,idx,idx1 in [("x",0,0), ("y",1,2), ("z",2,1)]:
            vn1,vn2,s0 = struct[comp]
            co1 = verts[vn1]
            co2 = verts[vn2]
            scales[idx1] = abs((co2[idx] - co1[idx])/s0*scale)
    else:
        verts = human.data.vertices
        for comp,idx in [("x",0), ("z",1), ("y",2)]:
            vn1,vn2,s0 = struct[comp]
            co1 = verts[vn1].co
            co2 = verts[vn2].co
            scales[idx] = abs((co2[idx] - co1[idx])/s0*scale)
    return scales


class VIEW3D_OT_AddShapekeysButton(bpy.types.Operator):
    bl_idname = "mhx2.add_shapekeys"
    bl_label = "Add Shapekeys"
    bl_description = "Add shapekeys"
    bl_options = {'UNDO'}

    filename = StringProperty()

    @classmethod
    def poll(self, context):
        ob = context.object
        return ob and ob.MhxHuman and ob.MhxSeedMesh and not ob.MhxHasFaceShapes

    def execute(self, context):
        ob = context.object
        addShapeKeys(ob, self.filename, getMhHuman())
        ob.MhxHasFaceShapes = True
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Setup and remove drivers
#------------------------------------------------------------------------

def addShapeKeyDriversToAll(rig, meshes, prefix):
    if rig is None:
        print("No rig. Cannot add drivers")
        return
    success = False
    for ob in meshes:
        if hasShapekeys(ob):
            addShapekeyDrivers(rig, ob, prefix)
            success = True
    if success:
        if prefix == "Mhf":
            rig.MhxFaceShapeDrivers = True
        else:
            rig.MhxOtherShapeDrivers = True
        print("Shapekey drivers added")
    else:
        print("No meshes with shapekeys")


def addShapekeyDrivers(rig, ob, prefix):
    facenames = ["brow", "chee", "lips", "nose", "tong", "mout"]
    if not ob.data.shape_keys:
        return
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name == "Basis":
            continue
        if prefix == "Mhf" and skey.name[0:4] not in facenames:
            continue
        if prefix == "Mho" and skey.name[0:4] in facenames:
            continue
        sname = getShapekeyName(skey, prefix)
        rig[sname] = 0.0
        try:
            rnaUI = rig["_RNA_UI"]
        except KeyError:
            rnaUI = rig["_RNA_UI"] = {}
        rig["_RNA_UI"][sname] = {"min":skey.slider_min, "max":skey.slider_max}
        addDriver(rig, skey, "value", sname, [], "x", False)


def getShapekeyName(skey, prefix):
    if skey.name[0:3] == prefix:
        return skey.name
    else:
        return prefix+skey.name


def hasShapekeys(ob):
    if ob is None:
        return False
    if (ob.type != 'MESH' or
        ob.data.shape_keys is None):
        return False
    for skey in ob.data.shape_keys.key_blocks:
        if skey.name != "Basis":
            return True
    return False


class VIEW3D_OT_AddFaceShapeDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.add_face_shape_drivers"
    bl_label = "Add Face Shape Drivers"
    bl_description = "Control facial shapes with rig properties. For file linking."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                rig.type == 'ARMATURE' and
                not rig.MhxFaceShapeDrivers and
                not rig.MhxFacePanel
               )

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        initRnaProperties(rig)
        addShapeKeyDriversToAll(rig, meshes, "Mhf")
        return{'FINISHED'}


class VIEW3D_OT_AddOtherShapeDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.add_other_shape_drivers"
    bl_label = "Add Other Shape Drivers"
    bl_description = "Control other shapes with rig properties. For file linking."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                rig.type == 'ARMATURE' and
                not rig.MhxOtherShapeDrivers
               )

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        initRnaProperties(rig)
        addShapeKeyDriversToAll(rig, meshes, "Mho")
        return{'FINISHED'}


def removeShapekeyDrivers(ob, rig, prefix):
    if not ob.data.shape_keys:
        return
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name != "Basis" and skey.name[0:3] != prefix:
            sname = getShapekeyName(skey, prefix)
            skey.driver_remove("value")
            deleteRigProperty(rig, sname)


class VIEW3D_OT_MhxRemoveFaceDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.remove_face_shape_drivers"
    bl_label = "Remove Face Shape Drivers"
    bl_description = "Remove ability to control facial shapekeys from rig property"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxFaceShapeDrivers)

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        for ob in meshes:
            removeShapekeyDrivers(ob, rig, "Mhf")
        rig.MhxFaceShapeDrivers = False
        return{'FINISHED'}


class VIEW3D_OT_MhxRemoveOtherDriverButton(bpy.types.Operator):
    bl_idname = "mhx2.remove_other_shape_drivers"
    bl_label = "Remove Other Shape Drivers"
    bl_description = "Remove ability to control other shapekeys from rig property"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxOtherShapeDrivers)

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        for ob in meshes:
            removeShapekeyDrivers(ob, rig, "Mho")
        rig.MhxOtherShapeDrivers = False
        return{'FINISHED'}
