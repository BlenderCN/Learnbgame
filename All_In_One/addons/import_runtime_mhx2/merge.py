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
from .error import *
from .utils import *

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def deleteHiddenVerts(human, clo):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    grpname = getDeleteName(clo)
    try:
        vgrp = human.vertex_groups[grpname]
    except KeyError:
        print("Did not find vertex group %s" % grpname)
        return

    for v in human.data.vertices:
        for g in v.groups:
            if g.group == vgrp.index:
                v.select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    human.vertex_groups.remove(vgrp)


def renameShapekeys(ob):
    if ob.data.shape_keys:
        pname = getProxyName(ob)
        for skey in ob.data.shape_keys.key_blocks:
            if skey.name != "Basis":
                skey.name = "%s:%s" % (pname, skey.name)


def mergeSelectedObjects(context):
    scn = context.scene
    clothes = []
    human = None
    for ob in context.selected_objects:
        if ob.type == 'MESH':
            if isBody(ob):
                human = ob
            else:
                clothes.append(ob)

    if human:
        reallySelect(human, scn)
        return mergeObjects(human, clothes)
    else:
        raise MhxError("Cannot merge.\nNo human found among\nselected objects.")

    matnums = []
    return matnums


def selectBoundaries(ob):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    vertpairs = dict([(vn,[]) for vn in range(len(ob.data.vertices))])
    for f in ob.data.polygons:
        for vn1,vn2 in f.edge_keys:
            vertpairs[vn1].append(vn2)

    select = []
    for vn,vlist in vertpairs.items():
        vlist.sort()
        while vlist:
            if len(vlist) == 1:
                select += [vn, vlist[0]]
                vlist = []
            elif vlist[0] == vlist[1]:
                vlist = vlist[2:]
            else:
                select += [vn, vlist[0]]
                vlist = vlist[1:]

    for vn in select:
        ob.data.vertices[vn].select = True


def mergeObjects(human, clothes):
    print("Merge %s to %s" % ([clo.name for clo in clothes], human.name))

    rname = getRigName(human)
    cnames = []
    for clo in clothes:
        if getRigName(clo) == rname:
            cnames.append(getProxyName(clo))

    delMods = []
    for mod in human.modifiers:
        if mod.type == 'MASK':
            mod.show_viewport = False
            vgname = getVGProxyName(mod.vertex_group)
            if vgname in cnames:
                delMods.append(mod)

    for mod in delMods:
        human.modifiers.remove(mod)

    for clo in clothes:
        deleteHiddenVerts(human, clo)
        #renameShapekeys(clo)

    firstCloVert = len(human.data.vertices)
    bpy.ops.object.join()
    selectBoundaries(human)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles(threshold=1e-3*human.MhxScale)
    bpy.ops.object.mode_set(mode='OBJECT')
    lastCloVert = len(human.data.vertices)

    for vgrp in human.vertex_groups:
        if isDeleteVGroup(vgrp):
            print(vgrp)
            #for vn in range(firstCloVert, lastCloVert):
            #    vgrp.add([vn], 1.0, 'REPLACE')

    for mod in human.modifiers:
        if mod.type == 'MASK':
            mod.show_viewport = True

    return []


def changeMaterial(human, mn):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    uvfaces = {}
    n = 0
    uvlayer = human.data.uv_layers[0]
    for f in human.data.polygons:
        nverts = len(f.vertices)
        if f.material_index == mn:
            f.select = True
            uvs = [tuple(uvlayer.data[n+k].uv) for k in range(nverts)]
            uvfaces[f.index] = uvs
        n += nverts

    human.data.uv_textures.active_index = 0
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.uv_texture_remove()
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

    uvlayer = human.data.uv_layers[0]
    n = 0
    for f in human.data.polygons:
        nverts = len(f.vertices)
        if f.select:
            f.material_index = 0
            uvs = uvfaces[f.index]
            for k in range(nverts):
                uvlayer.data[n+k].uv = uvs[k]
        n += nverts

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def mergeBodyParts(human, proxies, scn, proxyTypes=[]):
    clothes = []
    for ob in scn.objects:
        ob.select = False
    human.select = True
    reallySelect(human, scn)
    for mhGeo,ob in proxies:
        if mhGeo["proxy"]["type"] in proxyTypes:
            clothes.append(ob)
            ob.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    matnums = mergeObjects(human, clothes)
    for mn in matnums:
        changeMaterial(human, mn)


class VIEW3D_OT_MergeObjectsButton(bpy.types.Operator):
    bl_idname = "mhx2.merge_objects"
    bl_label = "Merge Selected To Human"
    bl_description = "Merge selected objects to active seamlessly"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob and ob.type == 'MESH')

    def execute(self, context):
        try:
            matnums = mergeSelectedObjects(context)
            human = context.object
            for mn in matnums:
                changeMaterial(human, mn)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

