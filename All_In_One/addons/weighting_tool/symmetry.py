"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Vertex groups

"""

import bpy
from bpy.props import *
import math

#----------------------------------------------------------
#   setupVertexPairs(ob):
#----------------------------------------------------------

def setupVertexPairs(context):
    ob = context.object
    scn = context.scene
    verts = []
    for v in ob.data.vertices:
        x = v.co[0]
        y = v.co[1]
        z = v.co[2]
        verts.append((z,y,x,v.index))
    verts.sort()
    lverts = {}
    rverts = {}
    mverts = {}
    nmax = len(verts)
    notfound = []
    for n,data in enumerate(verts):
        (z,y,x,vn) = data
        n1 = n - 20
        n2 = n + 20
        if n1 < 0: n1 = 0
        if n2 >= nmax: n2 = nmax
        vmir = findVert(verts[n1:n2], vn, -x, y, z, notfound, scn)
        if vmir < 0:
            mverts[vn] = vn
        elif x > scn.MhxEpsilon:
            rverts[vn] = vmir
        elif x < -scn.MhxEpsilon:
            lverts[vn] = vmir
        else:
            mverts[vn] = vmir
    if notfound:
        print("Did not find mirror image for vertices:")
        for data in notfound:
            print("  %d at (%.4f %.4f %.4f) mindist %.4f" % tuple(data))
    print("Left-right-mid", len(lverts.keys()), len(rverts.keys()), len(mverts.keys()))
    return (lverts, rverts, mverts)

def findVert(verts, v, x, y, z, notfound, scn):
    mindist = 1e6
    for (z1,y1,x1,v1) in verts:
        dx = x-x1
        dy = y-y1
        dz = z-z1
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < scn.MhxEpsilon:
            return v1
        if dist < mindist:
            mindist = dist
    if abs(x) > scn.MhxEpsilon:
        notfound.append((v, x, y, z, mindist))
    return -1

#
#    symmetrizeWeights(context):
#    class VIEW3D_OT_SymmetrizeWeightsButton(bpy.types.Operator):
#

def symmetrizeWeights(context, left2right):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene

    left = {}
    left01 = {}
    left02 = {}
    leftIndex = {}
    left01Index = {}
    left02Index = {}
    right = {}
    right01 = {}
    right02 = {}
    rightIndex = {}
    right01Index = {}
    right02Index = {}
    symm = {}
    symmIndex = {}
    for vgrp in ob.vertex_groups:
        if vgrp.name[-2:] in ['_L', '.L', '_l', '.l']:
            nameStripped = vgrp.name[:-2]
            left[nameStripped] = vgrp
            leftIndex[vgrp.index] = nameStripped
        elif vgrp.name[-2:] in ['_R', '.R', '_r', '.r']:
            nameStripped = vgrp.name[:-2]
            right[nameStripped] = vgrp
            rightIndex[vgrp.index] = nameStripped
        elif vgrp.name[-4:].lower() == 'left':
            nameStripped = vgrp.name[:-4]
            left[nameStripped] = vgrp
            leftIndex[vgrp.index] = nameStripped
        elif vgrp.name[-5:].lower() == 'right':
            nameStripped = vgrp.name[:-5]
            right[nameStripped] = vgrp
            rightIndex[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.L.01', '.l.01']:
            nameStripped = vgrp.name[:-5]
            left01[nameStripped] = vgrp
            left01Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.R.01', '.r.01']:
            nameStripped = vgrp.name[:-5]
            right01[nameStripped] = vgrp
            right01Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.L.02', '.l.02']:
            nameStripped = vgrp.name[:-5]
            left02[nameStripped] = vgrp
            left02Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.R.02', '.r.02']:
            nameStripped = vgrp.name[:-5]
            right02[nameStripped] = vgrp
            right02Index[vgrp.index] = nameStripped
        else:
            symm[vgrp.name] = vgrp
            symmIndex[vgrp.index] = vgrp.name

    printGroups('Left', left, leftIndex, ob.vertex_groups)
    printGroups('Right', right, rightIndex, ob.vertex_groups)
    printGroups('Left01', left01, left01Index, ob.vertex_groups)
    printGroups('Right01', right01, right01Index, ob.vertex_groups)
    printGroups('Left02', left02, left02Index, ob.vertex_groups)
    printGroups('Right02', right02, right02Index, ob.vertex_groups)
    printGroups('Symm', symm, symmIndex, ob.vertex_groups)

    (lverts, rverts, mverts) = setupVertexPairs(context)
    if left2right:
        factor = 1
        fleft = left
        fright = right
        groups = list(right.values()) + list(right01.values()) + list(right02.values())
        cleanGroups(ob.data, groups)
        grpinfo1 = [(leftIndex, right),(left01Index, right01),(left02Index, right02)]
        grpinfo2 = [(rightIndex, left),(right01Index, left01),(right02Index, left02),(symmIndex, symm)]
    else:
        factor = -1
        fleft = right
        fright = left
        tmp = rverts
        rverts = lverts
        lverts = tmp
        groups = list(left.values()) + list(left01.values()) + list(left02.values())
        cleanGroups(ob.data, groups)
        grpinfo1 = [(rightIndex, left),(right01Index, left01),(right02Index, left02)]
        grpinfo2 = [(leftIndex, right),(left01Index, right01),(left02Index, right02),(symmIndex, symm)]

    for (vn, rvn) in rverts.items():
        symmetrizeVertWeightsSide(ob, vn, rvn, grpinfo1)

    for (vn, rvn) in mverts.items():
        symmetrizeVertWeightsSide(ob, vn, rvn, grpinfo1)

    for (vn, rvn) in lverts.items():
        symmetrizeVertWeightsSide(ob, vn, rvn, grpinfo1)

    for (vn, rvn) in rverts.items():
        symmetrizeVertWeightsSide(ob, vn, rvn, grpinfo2)

    return len(rverts)


def symmetrizeVertWeightsSide(ob, vn, rvn, grpinfo):
    v = ob.data.vertices[vn]
    v.select = True
    rv = ob.data.vertices[rvn]
    #print(v.index, rv.index)
    #for rgrp in rv.groups:
    #    rgrp.weight = 0
    for grp in v.groups:
        rgrp = None
        for (indices, groups) in grpinfo:
            try:
                name = indices[grp.group]
                rgrp = groups[name]
            except:
                pass
        if rgrp:
            #print("  ", name, grp.group, rgrp.name, rgrp.index, v.index, rv.index, grp.weight)
            rgrp.add([rv.index], grp.weight, 'REPLACE')


def printGroups(name, groups, indices, vgroups):
    print(name)
    for (nameStripped, grp) in groups.items():
        print("  ", nameStripped, grp.name, indices[grp.index])
    return

def cleanGroups(me, groups):
    for grp in groups:
        print(grp)
        for v in me.vertices:
            grp.remove([v.index])
    return

class VIEW3D_OT_SymmetrizeWeightsButton(bpy.types.Operator):
    bl_idname = "mhw.symmetrize_weights"
    bl_label = "Symmetrize weights"
    bl_options = {'UNDO'}
    left2right = BoolProperty()

    def execute(self, context):
        import bpy
        n = symmetrizeWeights(context, self.left2right)
        print("Weights symmetrized, %d vertices" % n)
        return{'FINISHED'}

#
#    cleanRight(context, doRight):
#    class VIEW3D_OT_CleanRightButton(bpy.types.Operator):
#

def cleanRight(context, doRight):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    (lverts, rverts, mverts) = setupVertexPairs(context)
    for vgrp in ob.vertex_groups:
        if doRight:
            if vgrp.name[-2:] in ['_L', '.L', '_l', '.l']:
                for (vn, rvn) in rverts.items():
                    vgrp.remove([rvn])
        else:
            if vgrp.name[-2:] in ['_R', '.R', '_r', '.r']:
                for (vn, rvn) in rverts.items():
                    vgrp.remove([vn])
    return

class VIEW3D_OT_CleanRightButton(bpy.types.Operator):
    bl_idname = "mhw.clean_right"
    bl_label = "Clean right"
    bl_options = {'UNDO'}
    doRight = BoolProperty()

    def execute(self, context):
        cleanRight(context, self.doRight)
        return{'FINISHED'}

#
#    symmetrizeShapes(context, left2right):
#    class VIEW3D_OT_SymmetrizeShapesButton(bpy.types.Operator):
#

def symmetrizeShapes(context, left2right):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene
    (lverts, rverts, mverts) = setupVertexPairs(context)
    if not left2right:
        rverts = lverts

    for key in ob.data.shape_keys.key_blocks:
        print(key.name)
        for rvn in rverts.values():
            rv = ob.data.vertices[rvn]
            key.data[rv.index].co = rv.co

        for v in ob.data.vertices:
            try:
                rvn = rverts[v.index]
            except:
                rvn = None
            if rvn:
                lco = key.data[v.index].co
                rco = lco.copy()
                rco[0] = -rco[0]
                key.data[rvn].co = rco

    return len(rverts)

class VIEW3D_OT_SymmetrizeShapesButton(bpy.types.Operator):
    bl_idname = "mhw.symmetrize_shapes"
    bl_label = "Symmetrize shapes"
    bl_options = {'UNDO'}
    left2right = BoolProperty()

    def execute(self, context):
        n = symmetrizeShapes(context, self.left2right)
        print("Shapes symmetrized, %d vertices" % n)
        return{'FINISHED'}


def symmetrizeVerts(context, left2right):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene
    (lverts, rverts, mverts) = setupVertexPairs(context)
    if not left2right:
        rverts = lverts

    for v in ob.data.vertices:
        try:
            rvn = rverts[v.index]
        except KeyError:
            rvn = None
        if rvn:
            rco = v.co.copy()
            rco[0] = -rco[0]
            print(rvn, ob.data.vertices[rvn].co, rco)
            ob.data.vertices[rvn].co = rco
            print("   ", ob.data.vertices[rvn].co)

    return len(rverts)


class VIEW3D_OT_SymmetrizeVertsButton(bpy.types.Operator):
    bl_idname = "mhw.symmetrize_verts"
    bl_label = "Symmetrize verts"
    bl_options = {'UNDO'}
    left2right = BoolProperty()

    def execute(self, context):
        n = symmetrizeVerts(context, self.left2right)
        print("Verts symmetrized, %d vertices" % n)
        return{'FINISHED'}

#
#    shapekeyFromObject(ob, targ):
#    class VIEW3D_OT_ShapeKeysFromObjectsButton(bpy.types.Operator):
#

def shapekeyFromObject(ob, targ):
    verts = ob.data.vertices
    tverts = targ.data.vertices
    print("Create shapekey %s" % targ.name)
    print(len(verts), len(tverts))
    if len(verts) != len(tverts):
        print("%s and %s do not have the same number of vertices" % (ob, targ))
        return
    if not ob.data.shape_keys:
        ob.shape_key_add(name='Basis', from_mix=False)
    skey = ob.shape_key_add(name=targ.name, from_mix=False)
    for n,v in enumerate(verts):
        vt = tverts[n].co
        pt = skey.data[n].co
        pt[0] = vt[0]
        pt[1] = vt[1]
        pt[2] = vt[2]
    print("Shape %s created" % skey)
    return

class VIEW3D_OT_ShapeKeysFromObjectsButton(bpy.types.Operator):
    bl_idname = "mhw.shapekeys_from_objects"
    bl_label = "Shapes from objects"
    bl_options = {'UNDO'}

    def execute(self, context):
        import bpy
        ob = context.object
        for targ in context.scene.objects:
            if targ.type == 'MESH' and targ.select and targ != ob:
                shapekeyFromObject(ob, targ)
        print("Shapekeys created for %s" % ob)
        return{'FINISHED'}

#
#
#


def symmetrizeSelection(context, left2right):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene
    (lverts, rverts, mverts) = setupVertexPairs(context)
    if not left2right:
        rverts = lverts
    for (vn, rvn) in rverts.items():
        v = ob.data.vertices[vn]
        rv = ob.data.vertices[rvn]
        rv.select = v.select
    return


class VIEW3D_OT_SymmetrizeSelectionButton(bpy.types.Operator):
    bl_idname = "mhw.symmetrize_selection"
    bl_label = "Symmetrize Selection"
    bl_options = {'UNDO'}
    left2right = BoolProperty()

    def execute(self, context):
        symmetrizeSelection(context, self.left2right)
        print("Selection symmetrized")
        return{'FINISHED'}

