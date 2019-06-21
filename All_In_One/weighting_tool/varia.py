"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract


"""

import bpy, os
from bpy.props import *
from . import io_json


def joinMeshes(context):
    scn = context.scene
    base = context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    clothes = []
    for ob in context.selected_objects:
        if ob != base and ob.type == 'MESH':
            clothes.append(ob)
            scn.objects.active = ob
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    print("Joining %s to %s" % (clothes, base))

    verts = []
    faces = []
    texfaces = []
    v0 = appendStuff(base, 0, verts, faces, texfaces)
    for clo in clothes:
        v0 = appendStuff(clo, v0, verts, faces, texfaces)
    me = bpy.data.meshes.new("NewBase")
    me.from_pydata(verts, [], faces)

    uvtex = me.uv_textures.new(name = "UVTex")
    for n,tf in enumerate(texfaces):
        print(n, tf)
        uvtex.data[n].uv = tf
    ob = bpy.data.objects.new("NewBase", me)
    scn.objects.link(ob)
    scn.objects.active = ob
    print("Meshes joined")


def appendStuff(ob, v0, verts, faces, texfaces):
    for v in ob.data.vertices:
        verts.append(v.co)
    for f in ob.data.polygons:
        face = []
        for vn in f.vertices:
            face.append(vn + v0)
        faces.append(face)
    v0 += len(ob.data.vertices)

    if ob.data.uv_textures:
        uvtex = ob.data.uv_textures[0]
        for f in ob.data.polygons:
            tf = uvtex.data[f.index].uv
            texfaces.append(tf)
    else:
        x0 = 0.99
        y0 = 0.99
        x1 = 1.0
        y1 = 1.0
        for f in ob.data.polygons:
            tf = ((x0,y0),(x0,y1),(x1,y0),(x1,y1))
            texfaces.append(tf)
    print("Done %s %d verts" % (ob.name, v0))
    return v0

class VIEW3D_OT_JoinMeshesButton(bpy.types.Operator):
    bl_idname = "mhw.join_meshes"
    bl_label = "Join meshes"
    bl_options = {'UNDO'}

    def execute(self, context):
        joinMeshes(context)
        return{'FINISHED'}

#
#   fixBaseFile():
#

the3dobjFolder = "C:/home/svn/data/3dobjs"

def baseFileGroups():
    fp = open(os.path.join(the3dobjFolder, "base0.obj"), "rU")
    grp = None
    grps = {}
    fn = 0
    for line in fp:
        words = line.split()
        if words[0] == "f":
            grps[fn] = grp
            fn += 1
        elif words[0] == "g":
            grp = words[1]
    fp.close()
    return grps

def fixBaseFile():
    grps = baseFileGroups()
    infp = open(os.path.join(the3dobjFolder, "base1.obj"), "rU")
    outfp = open(os.path.join(the3dobjFolder, "base2.obj"), "w")
    fn = 0
    grp = None
    for line in infp:
        words = line.split()
        if words[0] == "f":
            try:
                fgrp = grps[fn]
            except:
                fgrp = None
            if fgrp != grp:
                grp = fgrp
                outfp.write("g %s\n" % grp)
            fn += 1
        outfp.write(line)
    infp.close()
    outfp.close()
    print("Base file fixed")
    return

class VIEW3D_OT_FixBaseFileButton(bpy.types.Operator):
    bl_idname = "mhw.fix_base_file"
    bl_label = "Fix base file"

    def execute(self, context):
        fixBaseFile()
        return{'FINISHED'}





#
#   class VIEW3D_OT_LocalizeFilesButton(bpy.types.Operator):
#

def localizeFile(context, path):
    print("Localizing", path)
    ob = context.object
    lines = []

    fp = open(path, "r")
    for line in fp:
        words = line.split()
        vn = int(words[0])
        v = ob.data.vertices[vn]
        if v.select:
            lines.append(line)
        else:
            print(line)
    fp.close()

    fp = open(path, "w")
    for line in lines:
        fp.write(line)
    fp.close()

    return


def localizeFiles(context, path):
    print("Local files in ", path)
    folder = os.path.dirname(path)
    for file in os.listdir(folder):
        (fname, ext) = os.path.splitext(file)
        if ext == ".target":
            localizeFile(context, os.path.join(folder, file))


class VIEW3D_OT_LocalizeFilesButton(bpy.types.Operator):
    bl_idname = "mhw.localize_files"
    bl_label = "Localize Files"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        maxlen= 1024, default= "")

    def execute(self, context):
        print("Exec localize files")
        localizeFiles(context, self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#
#
#

class VIEW3D_OT_StatisticsButton(bpy.types.Operator):
    bl_idname = "mhw.statistics"
    bl_label = "Statistics"

    def execute(self, context):
        ob = context.object
        rig = ob.parent
        if ob.type == 'MESH':
            uvs = ob.data.uv_layers[0]
            print(
                "# Verts: %d\n" % len(ob.data.vertices) +
                "# Faces: %d\n" % len(ob.data.polygons) +
                "# UVs: %d %g\n" % (len(uvs.data), len(uvs.data)/2.0)
                )
        if rig and rig.type == 'ARMATURE':
            print(
                "# Bones: %d\n" % len(rig.data.bones)
                )
        return{'FINISHED'}

#
#
#

VertexNumbers = {}

VertexNumbers["hm08"] = {
    "Body"      : (0, 13380),
    "Tongue"    : (13380, 13606),
    "Joints"    : (13606, 14614),
    "Eyes"      : (14614, 14758),
    "EyeLashes" : (14758, 15008),
    "LoTeeth"   : (15008, 15076),
    "UpTeeth"   : (15076, 15144),
    "Penis"     : (15144, 15344),
    "Tights"    : (15344, 18018),
    "Skirt"     : (18018, 18738),
    "hair"      : (18738, 19166),
}


def transferVgroups(ob1, ob2):
    if len(ob1.vertex_groups) == 0:
        tmp = ob1
        ob1 = ob2
        ob2 = tmp
    print(ob1, ob1.vertex_groups)
    print(ob2, ob2.vertex_groups)
    if len(ob1.vertex_groups) == 0:
        raise NameError("%s has no vertex groups" % ob1)
    if len(ob2.vertex_groups) > 0:
        raise NameError("%s has vertex groups" % ob2)

    vgroups = {}
    for vg1 in ob1.vertex_groups:
        vg2 = ob2.vertex_groups.new(vg1.name)
        vgroups[vg1.index] = vg2
        if vg2.index != vg1.index:
            raise NameError("Oops %s %d %d" % (vg1.name, vg1.index, vg2.index))

    for v1 in ob1.data.vertices:
        vn2 = getVertex(v1.index)
        for g1 in v1.groups:
            vg2 = vgroups[g1.group]
            vg2.add([vn2], g1.weight, 'REPLACE')


def getVertex(vn1):
    vstruct1 = VertexNumbers["alpha8a"]
    for key in vstruct1:
        first1,last1 = vstruct1[key]
        if vn1 >= first1 and vn1 < last1:
            break

    vstruct2 = VertexNumbers["alpha8b"]
    first2,last2 = vstruct2[key]
    vn2 = vn1 - first1 + first2
    return vn2


def checkVgroupSanity():
    vstruct1 = VertexNumbers["alpha8a"]
    vstruct2 = VertexNumbers["alpha8b"]
    for key in vstruct1:
        first1,last1 = vstruct1[key]
        first2,last2 = vstruct2[key]
        nverts1 = last1-first1
        nverts2 = last2-first2
        if nverts1 == nverts2:
            print("    ", key)
        else:
            print("*** %s %d %d" % (key, nverts1, nverts2))



class VIEW3D_OT_TransferVgroupsButton(bpy.types.Operator):
    bl_idname = "mhw.transfer_vgroups"
    bl_label = "Transfer Vertex Groups"

    def execute(self, context):
        checkVgroupSanity()
        ob1 = context.object
        scn = context.scene
        for ob in scn.objects:
            if ob.type == 'MESH' and ob != ob1 and ob.select:
                ob2 = ob
                break
        transferVgroups(ob1, ob2)
        return{'FINISHED'}


class VIEW3D_OT_CheckVgroupsSanityButton(bpy.types.Operator):
    bl_idname = "mhw.check_vgroups_sanity"
    bl_label = "Check Vertex Group Sanity"

    def execute(self, context):
        checkVgroupSanity()
        return{'FINISHED'}


#
#
#

def createHairRig(ob):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE', action='ENABLE')
    bpy.ops.object.mode_set(mode='OBJECT')

    hairGroups = {}
    for vn in range(18722, 19150):
        hairGroups[vn] = 0

    bones = []
    vgroups = {}
    for f in ob.data.polygons:
        if f.select:
            terminals = []
            vgrp = vgroups[f.index] = []
            for vn1,vn2 in f.edge_keys:
                if vn1 not in vgrp:
                    vgrp.append(vn1)
                    hairGroups[vn1] += 1
                if vn2 not in vgrp:
                    vgrp.append(vn2)
                    hairGroups[vn2] += 1

                v1 = ob.data.vertices[vn1]
                v2 = ob.data.vertices[vn2]
                vec = v1.co - v2.co
                zrel = vec[2]/vec.length
                if zrel < 0.5:
                    mid = (v1.co+v2.co)/2
                    terminals.append((mid,vn1,vn2))
            if len(terminals) != 2:
                halt
            head,tail = terminals
            if head[0][2] < tail[0][2]:
                tail,head = terminals
            bones.append((f.index,head,tail))

    parents = {}
    for idx,head,tail in bones:
        parents[idx] = None
        for idx1,head1,tail1 in bones:
            vec = tail1[0]-head[0]
            if vec.length < 1e-5:
                parents[idx] = idx1

    head = []
    wlist = [ ("head", head) ]
    for vn,ngrps in hairGroups.items():
        if ngrps == 0:
            head.append((vn, 1.0))

    for key,vgrp in vgroups.items():
        weights = [(vn,1.0/hairGroups[vn]) for vn in vgrp]
        wlist.append( ("hair%d" % key, weights) )

    filepath = "/home/vgrp_hair_rig.json"
    io_json.saveJson(wlist, filepath, maxDepth=1)

    string = (
        "from .flags import *\n\n" +
        "Joints = [\n")

    for idx,head,tail in bones:
        if not parents[idx]:
            _,vn1,vn2 = head
            string += ("  ('hd%d', 'vl', ((0.5, %d), (0.5, %d))),\n" % (idx, vn1, vn2))
        _,vn1,vn2 = tail
        string += ("  ('tl%d', 'vl', ((0.5, %d), (0.5, %d))),\n" % (idx, vn1, vn2))

    string += ("]\n\nHeadsTails = {\n")
    for idx,_head,_tail in bones:
        if parents[idx]:
            string += ("  'hair%d' :  ('tl%d', 'tl%d'),\n" % (idx, parents[idx], idx))
        else:
            string += ("  'hair%d' :  ('hd%d', 'tl%d'),\n" % (idx, idx, idx))

    string += ("}\n\nArmature = {\n")
    for idx,head,tail in bones:
        if parents[idx]:
            string += ("  'hair%d' :     (0, 'hair%d', F_DEF+F_CON, L_HAIR),\n" % (idx, parents[idx]))
        else:
            string += ("  'hair%d' :     (0, 'head', F_DEF, L_HAIR),\n" % idx)

    string += ("}\n")

    filepath = "/home/rig_hair.py"
    fp = open(filepath, "w")
    fp.write(string)
    fp.close()


class VIEW3D_OT_createHairRigButton(bpy.types.Operator):
    bl_idname = "mhw.create_hair_rig"
    bl_label = "Create Hair Rig"

    def execute(self, context):
        createHairRig(context.object)
        return{'FINISHED'}
