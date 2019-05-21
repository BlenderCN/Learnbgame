bl_info = {
    "name": "Import SMD: Valve studiomodel source format",
    "author": "nemyax",
    "version": (0, 1, 20171130),
    "blender": (2, 7, 8),
    "location": "File > Import-Export",
    "description": "Import Valve studiomodel sources",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import os
import bmesh
import os.path
import mathutils as mu
import math
import re
import struct
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    IntProperty)
from bpy_extras.io_utils import (
    ExportHelper,
    ImportHelper,
    path_reference_mode)

###
### Import functions
###

### SMD reference import

def read_smd_mesh(path):
    i = "\s+(\d+)"
    w = "\s+(.+?)"
    a = "(.+?)"
    anim_re = re.compile("\s*skeleton.*")
    bone_re = re.compile("\s*(\d+)\s+\""+a+"\"\s+(.+)\s+.*")
    mesh_re = re.compile("\s*triangles.*")
    node_re = re.compile("\s*nodes.*")
    time_re = re.compile("\s*time"+i+".*")
    vert_re = re.compile("\s*(\d+)"+8*w+"\s+(.*)")
    xfrm_re = re.compile("\s*(\d+)"+6*"\s+(.+)"+"\s*")
    txtr_re = re.compile("\s*(\S+)\s*$")
    e_re = re.compile("\s*end\s*")
    fh = open(path, "r")
    smd_mesh = fh.readlines()
    fh.close()
    have_geom = False
    for l in smd_mesh:
        if mesh_re.match(l):
            have_geom = True
            break
    if not have_geom:
        return "The selected file has no geometry data.", {'CANCELLED'}
    skip_until(node_re, smd_mesh)
    hier = [(int(a),b,int(c)) for a, b, c in gather(bone_re, e_re, smd_mesh)]
    skip_until(time_re, smd_mesh)
    init = gather(xfrm_re, e_re, smd_mesh)
    arm_o = do_bones(smd_mesh, bone_re, e_re, hier, init)
    skip_until(mesh_re, smd_mesh)
    grp_set, mats, bm = do_mesh(smd_mesh, txtr_re, vert_re, e_re)
    bone_dict = dict([(a,b) for a, b, _ in hier])
    mesh = bpy.data.meshes.new("smd_mesh")
    mesh_o = bpy.data.objects.new("smd_mesh", mesh)
    vgs = mesh_o.vertex_groups
    remap_dict = {}
    for i in grp_set:
        vg = vgs.new(name=bone_dict[i])
        remap_dict[i] = vg.index
    remap_groups(bm, remap_dict)
    prep_mesh(mesh, bm)
    bm.free()
    arm_mod = mesh_o.modifiers.new(type='ARMATURE', name="smd_skeleton")
    arm_mod.object = arm_o
    bpy.context.scene.objects.link(mesh_o)
    bpy.context.scene.objects.active = mesh_o
    bpy.ops.object.mode_set(mode='EDIT')
    for m in mats:
        try:
            bmat = bpy.data.materials[m]
        except KeyError:
            bmat = bpy.data.materials.new(m)
        bpy.ops.object.material_slot_add()
        mesh_o.material_slots[-1].material = bmat
    bpy.ops.object.mode_set()
    return "Studiomodel imported successfully.", {'FINISHED'}

def prep_mesh(mesh, bm):
    sharp = set()
    n_data = bm.loops.layers.string.active
    bm.edges.ensure_lookup_table()
    for e in bm.edges:
        for v in e.verts:
            cs = set()
            for f in v.link_faces:
                if e in f.edges:
                    for c in f.loops:
                        if c.vert == v:
                            cs.add(c)
            if len(set([c[n_data] for c in cs])) > 1:
                sharp.add(e.index)
                break
    bm.to_mesh(mesh)
    for i in sharp:
        mesh.edges[i].use_edge_sharp = True
    mesh.show_edge_sharp = True
    mesh.update()

def remap_groups(bm, remap_dict):
    wd  = bm.verts.layers.deform.verify()
    for v in bm.verts:
        remapped = {}
        for g, w in v[wd].items():
            if g in remap_dict:
                remapped[remap_dict[g]] = w
            else:
                remapped[g] = w
        v[wd].clear()
        for r in remapped:
            v[wd][r] = remapped[r]

def parse_vert_without_weights(vert_data):
    geom = [float(a) for a in vert_data[1:9]]
    geom.append(((int(vert_data[0]),1.0),))
    return tuple(geom)

def parse_vert_with_weights(vert_data):
    geom = [float(a) for a in vert_data[1:9]]
    weights = []
    weight_data = list(re.findall("\S+", vert_data[9]))
    count = int(weight_data.pop(0))
    for _ in range(count):
        weights.append(
            (int(weight_data.pop(0)),float(weight_data.pop(0))))
    weights.sort()
    geom.append(tuple(weights))
    return tuple(geom)

def mk_index_dict(some_list):
    some_set = set(some_list)
    return dict(zip(list(some_set), range(len(some_set))))

def do_mesh(smd_mesh, tx_re, vert_re, e_re):
    bm  = bmesh.new()
    wd  = bm.verts.layers.deform.verify()
    uvs = bm.loops.layers.uv.verify()
    nd  = bm.loops.layers.string.verify()
    mats, verts = gather_multi((tx_re,vert_re), e_re, smd_mesh)
    mats = [m[0] for m in mats]
    mat_dict = mk_index_dict(mats)
    parse_fun = parse_vert_without_weights
    if verts[0][9] != "":
        parse_fun = parse_vert_with_weights
    for i in range(len(verts)):
        verts[i] = parse_fun(verts[i])
    grp_set = set()
    for m, i in zip(mats, range(len(mats))):
        i3 = i * 3
        vs = verts[i3:i3+3]
        f = bm.faces.new([bm.verts.new(a[:3]) for a in vs])
        f.material_index = mat_dict[m]
        for l, smdv in zip(f.loops, vs):
            l[uvs].uv = smdv[6:8]
            l[nd] = b"".join([struct.pack('<f', a) for a in smdv[3:6]])
            ws = dict(smdv[8])
            for a in ws:
                l.vert[wd][a] = ws[a]
                grp_set.add(a)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    mat_list = [m for m in mat_dict]
    mat_list.sort(key=lambda m: mat_dict[m])
    return grp_set, mat_list, bm
        
def do_bones(smd_mesh, j_re, e_re, hier, init):
    arm = bpy.data.armatures.new("smd")
    arm_o = bpy.data.objects.new("smd", arm)
    bpy.context.scene.objects.link(arm_o)
    bpy.context.scene.objects.active = arm_o
    bpy.ops.object.mode_set()
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = arm.edit_bones
    par_ref = {-1:None}
    for i, n, _ in hier:
        eb = ebs.new(n)
        eb.head = (0.0,0.0,0.0)
        eb.tail = (0.0,1.0,0.0)
        eb.length = 5.0
        par_ref[i] = eb
    mtx_dict = {}
    for a in init:
        t = [float(b) for b in a[1:4]]
        r = [float(b) for b in a[4:7]]
        mtx_dict[int(a[0])] = \
            mu.Matrix.Translation(t) * \
            mu.Euler(r).to_matrix().to_4x4()
    for i, n, p in hier:
        parent = par_ref[p]
        eb = ebs[n]
        eb.parent = parent
        eb.matrix = mtx_dict[i]
        p0 = p
        while p0 >= 0:
            eb.matrix = mtx_dict[p0] * eb.matrix
            p0 = hier[p0][2]
    bpy.ops.object.mode_set()
    smd_grp = arm_o.pose.bone_groups.new("smd")
    for pb in arm_o.pose.bones:
        pb.bone_group = smd_grp
    return arm_o

### animation import functions

def read_smd_anim(path):
    label = path.split(os.sep)[-1].split(".")[-2]
    ao = bpy.context.active_object
    if ao.type != 'ARMATURE':
        ao = ao.find_armature()
    skel = bone_tree_blender(ao)
    fh = open(path, "r")
    smd_anim = fh.readlines()
    fh.close()
    i = "\s+(\d+)"
    w = "\s+(.+?)"
    a = "(.+?)"
    anim_re = re.compile("\s*skeleton.*")
    bone_re = re.compile("\s*(\d+)\s+\""+a+"\"\s+(.+)\s+.*")
    node_re = re.compile("\s*nodes.*")
    time_re = re.compile("\s*time"+i+".*")
    xfrm_re = re.compile("\s*(\d+)"+6*"\s+(.+)"+"\s*")
    e_re = re.compile("\s*end\s*")
    hier = [(int(a),b,int(c)) for a, b, c in gather(bone_re, e_re, smd_anim)]
    smd_skel = bone_tree_smd(hier)
    if skel != smd_skel:
        return message("no_arm_match"), {'CANCELLED'}
    skip_until(anim_re, smd_anim)
    pblu = dict([(j[0],ao.pose.bones[j[1]]) for j in hier])
    seq_end, frames = do_frames(time_re, xfrm_re, e_re, smd_anim, pblu)
    channels = get_channels(pblu.values())
    sc = bpy.context.scene
    start_frame = sc.frame_current
    end_frame = start_frame + seq_end
    set_keys(channels, frames, start_frame)
    sc.timeline_markers.new(label + "_start", start_frame)
    sc.timeline_markers.new(label + "_end", end_frame)
    sc.frame_current = end_frame
    return "Animation imported successfully.", {'FINISHED'}

def do_frames(time_re, xfrm_re, e_re, smd_anim, pblu):
    result = {}
    mlu = {}
    for pb in pblu.values():
        par = pb.parent
        mtx = pb.bone.matrix_local
        if par:
            mlu[pb] = pb.bone.matrix_local.inverted() * par.bone.matrix_local
        else:
            mlu[pb] = pb.bone.matrix_local.inverted()
    i = None
    while smd_anim:
        l = smd_anim.pop(0)
        xfrm_m = xfrm_re.match(l)
        if xfrm_m:
            k = xfrm_m.groups()
            bone = pblu[int(k[0])]
            if bone not in result:
                result[bone] = [[] for _ in range(10)] # loc:3, quat:4, euler:3
            tx, ty, tz, rx, ry, rz = [float(a) for a in k[1:]]
            mtx = mu.Euler((rx, ry, rz)).to_matrix().to_4x4()
            mtx.translation = (tx,ty,tz)
            mtx = mlu[bone] * mtx
            xf = []
            xf.extend(mtx.translation[:])
            xf.extend(mtx.to_quaternion()[:])
            xf.extend(mtx.to_euler()[:])
            for j in range(10):
                result[bone][j].append((i,xf[j]))
            continue
        time_m = time_re.match(l)
        if time_m:
            i = int(time_m.group(1))
            continue
        e_m = e_re.match(l)
        if e_m:
            break
    return i, result

def get_channels(pbs):
    cf = float(bpy.context.scene.frame_current)
    result = {}
    l = "location"
    q = "rotation_quaternion"
    e = "rotation_euler"
    for pb in pbs:
        pb.keyframe_insert(l)
        pb.keyframe_insert(q)
        pb.keyframe_insert(e)
        entry = {l:{},q:{},e:{}}
        pbn = pb.name
        fc_re = re.compile("pose\.bones\[."+pbn+".\]\.("+l+"|"+q+"|"+e+")")
        for fc in pb.id_data.animation_data.action.fcurves:
            m = fc_re.match(fc.data_path)
            if m:
                key1 = m.group(1)
                key2 = fc.array_index
                entry[key1][key2] = fc.keyframe_points
        result[pb] = [
            entry[l][0],entry[l][1],entry[l][2],
            entry[q][0],entry[q][1],entry[q][2],entry[q][3],
            entry[e][0],entry[e][1],entry[e][2]]
    return result

def set_keys(channels, frames, f_start):
    for pb in frames:
        ch_list = channels[pb]
        key_lists = frames[pb]
        for ch, kl in zip(ch_list, key_lists):
            for fr, val in kl:
                ch.insert(fr + f_start, val)

### parsing and utility functions

def gather(regex, end_regex, ls):
    return gather_multi([regex], end_regex, ls)[0]
 
def gather_multi(regexes, end_regex, ls):
    result = [[] for _ in regexes]
    n = len(regexes)
    while ls:
        l = ls.pop(0)
        if end_regex.match(l):
            break
        for i in range(n):
            m = regexes[i].match(l)
            if m:
                result[i].append(m.groups())
                break
    return result

def skip_until(regex, ls):
    while ls:
        if regex.match(ls.pop(0)):
            break

def bone_tree_blender(ao):
    if "smd" in [g.name.lower() for g in ao.pose.bone_groups]:
        pbs = [b for b in ao.pose.bones
            if b.bone_group != None
            and b.bone_group.name.lower() == "smd"]
    else:
        pbs = ao.pose.bones[:]
    return btb(None, pbs)

def btb(b, bs): # recursive; shouldn't matter for poxy SMD skeletons
    ch = sorted([a for a in bs if a.parent == b], key=lambda x: x.name)
    return [[c.name, btb(c, bs)] for c in ch]

def bone_tree_smd(lst):
    return btm(-1, lst)

def btm(i, l):
    ch = sorted([a for a in l if a[2] == i], key=lambda x: x[1])
    return [[c[1], btm(c[0], l)] for c in ch]

###
### Operators and auxiliary functions
###

# Functions

def message(id, *details):
    if id == 'no_arm_match':
        return """The armature does not match the skeleton
in the file you are trying to import."""

# Operators

### Import UI

class ImportGSSMDMesh(bpy.types.Operator, ImportHelper):
    '''Load a reference SMD file'''
    bl_idname = "import_scene.gs_smd_mesh"
    bl_label = 'Import reference SMD'
    bl_options = {'PRESET'}
    filename_ext = ".smd"
    filter_glob = StringProperty(
            default="*.smd",
            options={'HIDDEN'})
    path_mode = path_reference_mode
    check_extension = True
    path_mode = path_reference_mode
    check_extension = True
    def execute(self, context):
        msg, res = read_smd_mesh(self.filepath)
        if res == {'CANCELLED'}:
            self.report({'ERROR'}, msg)
        print(msg)
        return res

class ImportGSSMDAnim(bpy.types.Operator, ImportHelper):
    '''Import a single SMD animation (start from the current frame)'''
    bl_idname = "import_scene.gs_smd_anim"
    bl_label = 'Import animation SMD'
    bl_options = {'PRESET'}
    filename_ext = ".smd"
    filter_glob = StringProperty(
            default="*.smd",
            options={'HIDDEN'})
    path_mode = path_reference_mode
    check_extension = True
    check_extension = True
    @classmethod
    def poll(cls, context):
        ao = bpy.context.active_object
        if ao:
            if ao.type == 'ARMATURE':
                return True
            elif ao.type == 'MESH':
                if ao.find_armature():
                    return True
        return False
    def execute(self, context):
        msg, res = read_smd_anim(self.filepath)
        if res == {'CANCELLED'}:
            self.report({'ERROR'}, msg)
        print(msg)
        return res

def menu_func_import_mesh(self, context):
    self.layout.operator(
        ImportGSSMDMesh.bl_idname, text="Studiomodel Mesh Source (.smd)")
def menu_func_import_anim(self, context):
    self.layout.operator(
        ImportGSSMDAnim.bl_idname, text="Studiomodel Animation Source (.smd)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import_mesh)
    bpy.types.INFO_MT_file_import.append(menu_func_import_anim)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_mesh)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_anim)

if __name__ == "__main__":
    register()
