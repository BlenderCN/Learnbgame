"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Export

"""

import bpy
import os
from collections import OrderedDict
from . import io_json

#
#    exportVertexGroups(filePath)
#    class VIEW3D_OT_ExportVertexGroupsButton(bpy.types.Operator):
#

def sortVertexGroups(ob):
    rig = ob.parent
    if True or not rig:
        return ob.vertex_groups

    roots = []
    for bone in rig.data.bones:
        if not bone.parent:
            roots.append(bone)

    vgroups = []
    for root in roots:
        vgroups += sortBoneVGroups(root, ob)
    return vgroups


def sortBoneVGroups(bone, ob):
    try:
        vgroups = [ob.vertex_groups[bone.name]]
    except KeyError:
        vgroups = []
    for child in bone.children:
        vgroups += sortBoneVGroups(child, ob)
    return vgroups


def exportVertexGroups(context):
    scn = context.scene
    exportAllVerts = not scn.MhxExportSelectedOnly
    ob = context.object
    me = ob.data
    vgroups = sortVertexGroups(ob)
    filePath = scn.MhxVertexGroupFile

    list = []
    for vg in vgroups:
        index = vg.index
        weights = []
        list.append((vg.name, weights))
        for v in me.vertices:
            if exportAllVerts or v.select:
                for grp in v.groups:
                    if grp.group == index and grp.weight > 0.005:
                        weights.append((v.index, grp.weight))

    fileName = os.path.expanduser(filePath)
    io_json.saveJson(list, fileName, maxDepth=1)
    """
    fp = open(fileName, "w")
        exportList(context, weights, vg.name, fp)
    fp.close()
    """
    print("Vertex groups exported to %s" % fileName)
    return

class VIEW3D_OT_ExportVertexGroupsButton(bpy.types.Operator):
    bl_idname = "mhw.export_vertex_groups"
    bl_label = "Export vertex groups"
    bl_options = {'UNDO'}

    def execute(self, context):
        exportVertexGroups(context)
        return{'FINISHED'}


def exportLeftRight(context):
    scn = context.scene
    filePath = scn.MhxVertexGroupFile
    fileName = os.path.expanduser(filePath)
    fp = open(fileName, "w")
    ob = context.object
    eps = 0.07
    left = []
    right = []
    for v in ob.data.vertices:
        if v.co[0] > eps:
            left.append((v.index, 1.0))
        elif v.co[0] < -eps:
            right.append((v.index, 1.0))
        else:
            w = (v.co[0] + eps)/(2*eps)
            left.append((v.index, w))
            right.append((v.index, 1-w))
    exportList(context, left, "Left", fp)
    exportList(context, right, "Right", fp)
    fp.close()
    print("Left-right vertex groups exported to %s" % fileName)
    return


class VIEW3D_OT_ExportLeftRightButton(bpy.types.Operator):
    bl_idname = "mhw.export_left_right"
    bl_label = "Export Left/Right Vertex Groups"
    bl_options = {'UNDO'}

    def execute(self, context):
        exportLeftRight(context)
        return{'FINISHED'}


class VIEW3D_OT_ExportCustomShapesButton(bpy.types.Operator):
    bl_idname = "mhw.export_custom_shapes"
    bl_label = "Export Custom Shapes"
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = context.scene
        structs = OrderedDict()
        objects = []
        for ob in scn.objects:
            if ob.type == 'MESH' and ob.select:
                objects.append((ob.name,ob))
        objects.sort()
        for _,ob in objects:
            struct = structs[ob.name] = OrderedDict()
            struct["verts"] = [tuple(v.co) for v in ob.data.vertices]
            struct["edges"] = [tuple(e.vertices) for e in ob.data.edges]
        filepath = os.path.expanduser(scn.MhxVertexGroupFile)
        io_json.saveJson(structs, filepath, maxDepth=0)
        print(filepath, "saved")
        return{'FINISHED'}


#
#    exportSumGroups(context):
#    exportListAsVertexGroup(weights, name, fp):
#    class VIEW3D_OT_ExportSumGroupsButton(bpy.types.Operator):
#

def exportSumGroups(context):
    filePath = context.scene.MhxVertexGroupFile
    fileName = os.path.expanduser(filePath)
    fp = open(fileName, "w")
    ob = context.object
    me = ob.data
    for name in ['UpArm', 'LoArm', 'UpLeg']:
        for suffix in ['_L', '_R']:
            weights = {}
            for n in range(1,4):
                vg = ob.vertex_groups["%s%d%s" % (name, n, suffix)]
                index = vg.index
                for v in me.vertices:
                    for grp in v.groups:
                        if grp.group == index:
                            try:
                                w = weights[v.index]
                            except:
                                w = 0
                            weights[v.index] = grp.weight + w
                # ob.vertex_groups.remove(vg)
            exportList(context, weights.items(), name+'3'+suffix, fp)
    fp.close()
    return

def exportList(context, weights, name, fp):
    print("EL", name)
    if len(weights) == 0:
        return
    scn = context.scene
    offset = scn.MhxVertexOffset
    if scn.MhxExportAsWeightFile:
        if len(weights) > 0:
            fp.write("\n# weights %s\n" % name)
            for (vn,w) in weights:
                if w > 0.005:
                    fp.write("  %d %.3g\n" % (vn+offset, w))
    else:
        fp.write("\n  VertexGroup %s\n" % name)
        for (vn,w) in weights:
            if w > 0.005:
                fp.write("    wv %d %.3g ;\n" % (vn+offset, w))
        fp.write("  end VertexGroup %s\n" % name)
    return

class VIEW3D_OT_ExportSumGroupsButton(bpy.types.Operator):
    bl_idname = "mhw.export_sum_groups"
    bl_label = "Export sum groups"
    bl_options = {'UNDO'}

    def execute(self, context):
        exportSumGroups(context)
        return{'FINISHED'}

#
#    exportShapeKeys(filePath)
#    class VIEW3D_OT_ExportShapeKeysButton(bpy.types.Operator):
#

def exportShapeKeys(context):
    scn = context.scene
    filePath = context.scene.MhxVertexGroupFile
    fileName = os.path.expanduser(filePath)
    fp = open(fileName, "w")
    ob = context.object
    me = ob.data
    lr = "Sym"
    for skey in me.shape_keys.key_blocks:
        name = skey.name.replace(' ','_')
        if name == "Basis":
            continue
        print(name)
        fp.write("  ShapeKey %s %s True\n" % (name, lr))
        fp.write("    slider_min %.2f ;\n" % skey.slider_min)
        fp.write("    slider_max %.2f ;\n" % skey.slider_max)
        for (n,pt) in enumerate(skey.data):
           vert = me.vertices[n]
           dv = pt.co - vert.co
           if dv.length > scn.MhxEpsilon:
               fp.write("    sv %d %.4f %.4f %.4f ;\n" %(n, dv[0], dv[1], dv[2]))
        fp.write("  end ShapeKey\n")
        print(skey)
    fp.close()
    print("Shape keys exported to %s" % fileName)
    return

class VIEW3D_OT_ExportShapeKeysButton(bpy.types.Operator):
    bl_idname = "mhw.export_shapekeys"
    bl_label = "Export shapekeys"
    bl_options = {'UNDO'}

    def execute(self, context):
        exportShapeKeys(context)
        return{'FINISHED'}

#
#   listVertPairs(context):
#   class VIEW3D_OT_ListVertPairsButton(bpy.types.Operator):
#

def listVertPairs(context):
    scn = context.scene
    filePath = scn.MhxVertexGroupFile
    fileName = os.path.expanduser(filePath)
    print("Open %s" % fileName)
    fp = open(fileName, "w")
    ob = context.object
    verts = []
    for v in ob.data.vertices:
        if v.select:
            verts.append((v.co[2], v.index))
    verts.sort()
    nmax = int(len(verts)/2)
    fp.write("Pairs = (\n")
    for n in range(nmax):
        (z1, vn1) = verts[2*n]
        (z2, vn2) = verts[2*n+1]
        v1 = ob.data.vertices[vn1]
        v2 = ob.data.vertices[vn2]
        x1 = v1.co[0]
        y1 = v1.co[1]
        x2 = v2.co[0]
        y2 = v2.co[1]
        print("%d (%.4f %.4f %.4f)" % (v1.index, x1,y1,z1))
        print("%d (%.4f %.4f %.4f)\n" % (v2.index, x2,y2,z2))
        if ((abs(z1-z2) > scn.MhxEpsilon) or
            (abs(x1+x2) > scn.MhxEpsilon) or
            (abs(y1-y2) > scn.MhxEpsilon)):
            raise NameError("Verts %d and %d not a pair:\n  %s\n  %s\n" % (v1.index, v2.index, v1.co, v2.co))
        if x1 > x2:
            fp.write("    (%d, %d),\n" % (v1.index, v2.index))
        else:
            fp.write("    (%d, %d),\n" % (v2.index, v1.index))
    fp.write(")\n")
    fp.close()
    print("Wrote %s" % fileName)
    return

class VIEW3D_OT_ListVertPairsButton(bpy.types.Operator):
    bl_idname = "mhw.list_vert_pairs"
    bl_label = "List vert pairs"
    bl_options = {'UNDO'}

    def execute(self, context):
        listVertPairs(context)
        return{'FINISHED'}

#