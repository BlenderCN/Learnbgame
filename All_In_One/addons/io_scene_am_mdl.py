bl_info = {
    "name": "Animation:Master Model",
    "author": "nemyax",
    "version": (0, 4, 20151003),
    "blender": (2, 7, 6),
    "location": "File > Import-Export",
    "description": "Export Animation:Master .mdl",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

### CP info
# Edges represent spline CPs. CP-related information is stored
# in the bmesh edge collection's string layer, as follows:
#  edge[cp_info][0:4]    successor CP index as a LE signed int ('<i')
#  edge[cp_info][4:8]    predecessor CP index as a LE signed int ('<i')
#  edge[cp_info][8:12]   "core" vertex index as a LE signed int ('<i')
#  edge[cp_info][12]     whether the spline loops after this CP
#  edge[cp_info][13]     whether this CP starts the spline
# All CP indexes are 0-based, Blender style, and incremented only
# during MDL formatting.

import bpy
import bmesh
import math
import mathutils as mu
import struct
import random
import os.path
from bpy.props import (
    StringProperty,
    BoolProperty)
from bpy_extras.io_utils import (
    ExportHelper,
    ImportHelper,
    path_reference_mode)

def compat(major, minor, rev):
    v = bpy.app.version
    return v[0] >= major and v[1] >= minor and v[2] >= rev

def correct():
    return mu.Matrix((
        (-1.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 1.0)))

def do_export(filepath, opts):
    if bpy.context.mode == 'EDIT_MESH':
        bpy.ops.object.mode_set()
        bpy.ops.object.mode_set(mode='EDIT') # make sure edits are applied
    obj = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(obj.data, use_shape_key=True)
    contents = build_mdl(obj, bm, opts)
    f = open(filepath, 'w')
    f.write(contents)
    msg = "File \"" + filepath + "\" written successfully."
    if opts["shapes"]:
        maybe_shapes(bm, filepath)
    bm.free()
    result = {'FINISHED'}
    return (msg, result)

def build_mdl(obj, bm, opts):
    fluff1 = "ProductVersion=17\nRelease=17.0 PC\n{}{}{}{}".format(
        tag("POSTEFFECTS"),
        tag("IMAGES"),
        tag("SOUNDS"),
        tag("MATERIALS"))
    fluff2 = "{}{}".format(
        tag("ACTIONS"),
        tag("CHOREOGRAPHIES"))
    models = tag("MODEL", format_obj(obj, prep(obj, bm, opts), opts))
    contents = tag(
        "MODELFILE",
        fluff1 + tag("OBJECTS", models) + fluff2)
    return contents

def format_obj(obj, bm, opts):
    mat_grps = opts["mat_grps"]
    mesh = do_splines(bm)
    mesh += do_patches(bm)
    fluff1 = "Name=Decal1\nTranslate=0.0 0.0\nScale=100.0 100.0\n"
    fluff2 = "Name=Stamp1\n"
    decals = tag(
        "DECAL",
        fluff1 + tag(
            "DECALIMAGES") + tag(
                "STAMPS",
                tag("STAMP", fluff2 + do_uvs(bm))))
    arm_o = obj.find_armature()
    bone_part = do_bones(obj, bm, arm_o) if arm_o else ""
    excl_groups = exclude_groups(arm_o) if arm_o else []
    gr_part = do_groups(obj, bm, excl_groups, opts)
    return tag("MESH", mesh) + tag("DECALS", decals) + gr_part + bone_part

def recreate(bm):
    [bm.faces.remove(f) for f in bm.faces if len(f.edges) < 3 or len(f.verts) > 5]
    [bm.edges.remove(e) for e in bm.edges if not e.link_faces[:]]
    [bm.verts.remove(v) for v in bm.verts if not v.link_edges[:]]
    for seq in [bm.verts, bm.faces, bm.edges]: seq.index_update()
    if compat(2, 73, 0):
        for seq in [bm.verts, bm.faces, bm.edges]: seq.ensure_lookup_table()
    return bm

def validate(bm, mtx0):
    bm = recreate(bm)
    cp_info = bm.edges.layers.string.verify() # see "CP info" note above
    for e in bm.edges:
        e[cp_info] = bytes(14)
    bm.faces.layers.int.verify()
    bm.verts.layers.int.verify()
    bm.loops.layers.int.new("cp")
    bm.loops.layers.int.new("flip")
    bm.transform(correct())
    return bm

def set_succ(e, cp_info, val):
    bstr = e[cp_info]
    e[cp_info] = struct.pack("<i", val) + bstr[4:]

def set_pred(e, cp_info, val):
    bstr = e[cp_info]
    e[cp_info] = bstr[:4] + struct.pack("<i", val) + bstr[8:]

def set_vert(e, cp_info, val):
    bstr = e[cp_info]
    e[cp_info] = bstr[:8] + struct.pack("<i", val) + bstr[12:]

def set_loop(e, cp_info, val):
    bstr = e[cp_info]
    e[cp_info] = bstr[:12] + struct.pack("b", val) + bstr[13:]

def set_init(e, cp_info, val):
    bstr = e[cp_info]
    e[cp_info] = bstr[:13] + struct.pack("b", val)

def get_succ(e, cp_info):
    return struct.unpack('<i', e[cp_info][:4])[0]

def get_pred(e, cp_info):
    return struct.unpack('<i', e[cp_info][4:8])[0]

def get_vert(e, cp_info):
    return struct.unpack('<i', e[cp_info][8:12])[0]

def get_loop(e, cp_info):
    return e[cp_info][12]

def get_init(e, cp_info):
    return e[cp_info][13]

def prep(obj, bm, opts):
    whiskers = opts["whiskers"]
    bm = validate(bm, obj.matrix_world)
    link_cp  = bm.verts.layers.int.active
    es = bm.edges[:]
    while es:
        e = es.pop(0)
        if e.tag:
            continue
        e.tag = True
        pred_v = e.verts[0]
        succ_v = e.verts[1]
        is_open, bm = walk_forward(succ_v, e, bm, whiskers)
        if is_open:
            bm = walk_backward(pred_v, e, bm, whiskers)
    for f in bm.faces:
        bm = do_face(f, bm)
    for v in bm.verts:
        fan = fanout(v, bm)
        if fan:
            # v[link_cp] = fan[0]
            v[link_cp] = min(fan)
        else:
            v[link_cp] = -1
    return bm

def min_cp(f, bm):
    link_cp = bm.verts.layers.int.active
    ls = f.loops[:]
    result = ls.pop()
    for l in ls:
        if l.vert[link_cp] < result.vert[link_cp]:
            result = l
    return result

def do_face(f, bm):
    cp_info = bm.edges.layers.string.active
    cp      = bm.loops.layers.int.get("cp")
    flip    = bm.loops.layers.int.get("flip")
    fls     = bm.faces.layers.int.active
    if compat(2, 73, 0):
        bm.edges.ensure_lookup_table()
    ls = f.loops[:]
    nls = len(ls)
    for l in ls:
        pl = l.link_loop_prev
        ple = pl.edge
        plen = get_succ(ple, cp_info)
        if l.vert in bm.edges[plen].verts:
            l[cp] = plen
        else:
            l[flip] = 1
            l[cp] = ple.index
    return bm

def walk_forward(v, e, bm, whiskers):
    start = e
    cp_info = bm.edges.layers.string.active
    while True:
        e.tag = True # tag means CP's taken; prevents spline branching
        set_vert(e, cp_info, e.other_vert(v).index)
        old_e = e
        old_v = v
        e = next_e(v, e)
        if e == start:
            set_succ(old_e, cp_info, e.index)
            set_pred(e, cp_info, old_e.index)
            set_loop(old_e, cp_info, True) # full circle
            set_init(start, cp_info, True)
            return (False, bm)
        if not e:
            v0 = old_e.other_vert(v)
            pt0 = v0.co
            pt1 = v.co
            pt2 = pt1 + pt1 - pt0
            v2  = bm.verts.new(pt2, v)
            ne1 = bm.edges.new((v, v2))
            ne1.tag = True
            ne1[cp_info] = bytes(14)
            bm.verts.index_update()
            bm.edges.index_update()
            ne1i = ne1.index
            set_succ(old_e, cp_info, ne1i)
            set_succ(ne1, cp_info, -1) # dead end
            set_pred(ne1, cp_info, old_e.index)
            set_vert(ne1, cp_info, v.index)
            if whiskers:
                v3  = bm.verts.new(pt2, v)
                ne2 = bm.edges.new((v2, v3))
                ne2[cp_info] = bytes(14)
                bm.verts.index_update()
                bm.edges.index_update()
                ne2.tag = True
                set_succ(ne1, cp_info, ne2.index) # override
                set_succ(ne2, cp_info, -1)  # dead end
                set_pred(ne2, cp_info, ne1i)
                set_vert(ne2, cp_info, v2.index)
            return (True, bm)
        v = e.other_vert(v)
        set_succ(old_e, cp_info, e.index)
        set_pred(e, cp_info, old_e.index)

def walk_backward(v, e, bm, whiskers):
    cp_info = bm.edges.layers.string.active
    while True:
        set_vert(e, cp_info, v.index)
        old_e = e
        e.tag = True
        e = next_e(v, e)
        if not e:
            if whiskers:
                v0 = old_e.other_vert(v)
                pt0 = v0.co
                pt1 = v.co
                pt2 = pt1 + pt1 - pt0
                v2 = bm.verts.new(pt2, v)
                ne = bm.edges.new((v, v2))
                ne[cp_info] = bytes(13)
                bm.verts.index_update()
                bm.edges.index_update()
                ne.tag = True
                set_succ(ne, cp_info, old_e.index)
                set_pred(ne, cp_info, -1)
                set_vert(ne, cp_info, v2.index)
                set_pred(old_e, cp_info, ne.index)
                set_init(ne, cp_info, True)
                return bm
            else:
                set_pred(old_e, cp_info, -1)
                set_init(old_e, cp_info, True)
                return bm
        v = e.other_vert(v)
        set_succ(e, cp_info, old_e.index)
        set_pred(old_e, cp_info, e.index)
    
def next_e(v, e):
    all_es = v.link_edges[:]
    all_fs = v.link_faces[:]
    fs = e.link_faces[:]
    tne = len(all_es)
    tnf = len(all_fs)
    nf = len(fs)
    if tnf == 4 and tne == 4:
        return [e0 for e0 in all_es if
            e0 not in fs[0].edges and
            e0 not in fs[1].edges][0]
    elif tnf == 3 and tne == 4 and \
        not [e for e in all_es if not e.link_faces]:
        if nf == 2:
            return [e0 for e0 in all_es if
                len(e0.link_faces[:]) == 1 and
                not e0 in fs[0].edges and
                not e0 in fs[1].edges][0]
        elif nf == 1:
            return [e0 for e0 in all_es if
                len(e0.link_faces[:]) == 2 and
                not e0 in fs[0].edges][0]
    elif not fs and tne == 4:
        return [e0 for e0 in all_es if
            len(e0.link_faces[:]) == 2][0]
    elif tnf == 2 and tne == 3 and nf == 1:
        return [e0 for e0 in all_es if len(e0.link_faces) == 1 and e0 != e][0]
    elif tnf == 2 and tne == 4 and nf == 1:
        lr = [e0 for e0 in all_es if len(e0.link_faces[:]) > 1]
        es = [e0 for e0 in all_es if e0 not in fs[0].edges]
        if lr:
            return [e0 for e0 in es if e0 not in lr][0]
        else:
            es0 = [e0 for e0 in es if not e0.tag]
            if es0:
                return es0[0]
    elif tne == 2 and tnf > 1:
        if all_es[0] == e:
            result = all_es[1]
        else:
            result = all_es[0]
        if not result.tag:
            return result

def do_splines(bm):
    cp_info = bm.edges.layers.string.active
    starters = [e for e in bm.edges if get_init(e, cp_info)]
    result = ""
    for s in starters:
        result += do_spline(s.index, bm)
    return result

def do_spline(s, bm):
    cp_info = bm.edges.layers.string.active
    link_cp  = bm.verts.layers.int.active
    if compat(2, 73, 0):
        bm.edges.ensure_lookup_table()
    result = ""
    e = bm.edges[s]
    while s >= 0:
        next_s = get_succ(e, cp_info)
        closed_loop = get_loop(e, cp_info)
        magic = 1 + closed_loop * 4 # also tried 262145 instead of 1
        other = fused_with(e, bm)
        v = bm.verts[get_vert(e, cp_info)]
        ei = e.index
        if other != None and v[link_cp] != ei:
            result += "{} 1 {} {} . .\n".format(
                magic, ei + 1, other + 1)
        else:
            x, y, z = v.co
            result += "{} 0 {} {:.6f} {:.6f} {:.6f} . .\n".format(
                magic, ei + 1, x, y, z)
        if closed_loop:
            break
        s = next_s
        e = bm.edges[s]
    return tag("SPLINE", result)

def fanout(v, bm):
    cp_info = bm.edges.layers.string.active
    vi = v.index
    return [e.index for e in v.link_edges if get_vert(e, cp_info) == vi]

def fused_with(e, bm):
    if compat(2, 73, 0):
        bm.verts.ensure_lookup_table()
    cp_info = bm.edges.layers.string.active
    vi = get_vert(e, cp_info)
    v = bm.verts[vi]
    es = fanout(v, bm)
    if len(es) > 1:
        return (es * 2)[es.index(e.index) + 1]

def do_patches(bm):
    patches = ""
    cp = bm.loops.layers.int.get("cp")
    flip = bm.loops.layers.int.get("flip")
    normals = ""
    ns = set()
    for f in bm.faces:
        for l in f.loops:
            ns.add(l.calc_normal()[:])
    ns = list(ns)
    for f in bm.faces:
        edges = []
        normals0 = []
        bits = [int(len(f.verts) == 5)]
        fl_bit = 8
        l = min_cp(f, bm)
        for _ in range(max(4, len(f.edges[:]))):
            edges.append(l[cp] + 1)
            bits.append(l[flip] * fl_bit)
            fl_bit *= 2
            normals0.append(ns.index(l.calc_normal()[:]))
            l = l.link_loop_prev
        entry = "{} ".format(sum(bits[:5]))
        for val in edges + normals0:
            entry += str(val) + " "
        entry += "0\n"
        patches += entry
    for (x, y, z) in ns:
        normals += "{:.6f} {:.6f} {:.6f}\n".format(x, y, z)
    return tag("PATCHES", patches) + tag("NORMALS", normals)

def do_uvs(bm):
    result = ""
    uv   = bm.loops.layers.uv.verify()
    cp   = bm.loops.layers.int.active
    link_cp  = bm.verts.layers.int.active
    for f in bm.faces:
        ls = f.loops
        nc = len(ls)
        cps = []
        start_l = min_cp(f, bm)
        l = start_l
        for _ in ls:
            cps.append(l.vert[link_cp] + 1)
            l = l.link_loop_prev
        uvs = []
        l = start_l
        for _ in ls:
            l0 = l.link_loop_prev
            cur_x, cur_y = l[uv].uv
            cur = mu.Vector((cur_x, 1.0 - cur_y, 0.0))
            nxt_x, nxt_y = l0[uv].uv
            nxt = mu.Vector((nxt_x, 1.0 - nxt_y, 0.0)) - cur
            nxt1 = cur + nxt * 0.333
            nxt2 = cur + nxt * 0.666
            for el in (cur[:], nxt1[:], nxt2[:]):
                uvs.extend(el[:])
            l = l0
        if nc == 3:
            cps += [cps[0]]
            uvs += uvs[:3] * 3
        elif nc == 5:
            cps.pop()
        entry = str((len(ls) == 5) * 5)
        for p in cps:
            entry += " "
            entry += str(p)
        for i in uvs:
            entry += " {:.6f}".format(i)
        entry += "\n"
        result += entry
    return tag("DATA", result)

def tag(label, s=""):
    return "<{0}>\n{1}</{0}>\n".format(label, s)

###
### Bone export
###

def maybe_bones(obj, bm):
    arm_o = obj.find_armature()
    if arm_o:
        return do_bones(obj, bm, arm_o)
    else:
        return ""

def do_bones(obj, bm, arm_o):
    result = ""
    arm = arm_o.data
    bones = arm.bones
    bm, lookup = group_weights(obj, tag_weights(norm_weights(bm)), arm)
    rolls = get_rolls(arm_o)
    for root in [b for b in bones if not b.parent]:
        result += do_bone(root, lookup, rolls, bm)
    return tag("BONES", result)

def get_rolls(obj):
    init_active = bpy.context.active_object
    init_mode = bpy.context.mode
    bpy.ops.object.mode_set()
    bpy.context.scene.objects.active = obj
    result = {}
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in obj.data.edit_bones:
        result[eb.name] = eb.roll
    bpy.ops.object.mode_set()
    bpy.context.scene.objects.active = init_active
    if init_mode == 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')
    return result

def do_bone(b, lookup, rolls, bm):
    name = b.name
    wts = bm.verts.layers.deform.active
    cp_info = bm.edges.layers.string.active
    result = "<SEGMENT>\nName={}\n".format(name)
    if name in lookup:
        gi, cps = lookup[name]
        if cps["abs"]:
            att = ""
            for cp in cps["abs"]:
                att += "{}\n".format(cp + 1)
            result += tag("NONSKINNEDCPS", att)
        if cps["rel"]:
            if compat(2, 73, 0):
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
            wtd = ""
            for cp in cps["rel"]:
                vi = get_vert(bm.edges[cp], cp_info)
                wtd += "{} {}\n".format(cp + 1, bm.verts[vi][wts][gi])
            result += tag("WEIGHTEDCPS", wtd)
    cmtx = correct()
    s = cmtx * b.head_local
    e = cmtx * b.tail_local
    rc = random.randint(0, 255)
    gc = random.randint(0, 255)
    bc = random.randint(0, 255)
    roll = rolls[name]
    quat = mu.Euler((0.0, 0.0, roll)).to_quaternion()
    quat.rotate((e - s).to_track_quat('Z', 'Y'))
    qw, qx, qy, qz = quat
    result += "BoneColor={} {} {} 255\n".format(rc, gc, bc)
    result += "Start={} {} {}\n".format(s[0], s[1], s[2])
    result += "End={} {} {}\n".format(e[0], e[1], e[2])
    result += "Length={}\n".format(b.length)
    result += "Rotate={} {} {} {}\n".format(qx, qy, qz, qw) # w is last in A:M
    if b.parent and b.use_connect:
        result += "Chained=TRUE\n"
    for ch in b.children:
        result += do_bone(ch, lookup, rolls, bm)
    result += "</SEGMENT>\n"
    return result

def tag_weights(bm):
    cp_info = bm.edges.layers.string.active
    wt_tags = bm.verts.layers.string.verify()
    if compat(2, 73, 0):
        bm.verts.ensure_lookup_table()
    for e in bm.edges:
        core_vi = get_vert(e, cp_info)
        bm.verts[core_vi][wt_tags] += struct.pack("<i", e.index)
    return bm

def norm_weights(bm):
    wts = bm.verts.layers.deform.active
    for v in bm.verts:
        total = sum(v[wts].values())
        if total:
            r = 1.0 / total
            for k in v[wts].keys():
                v[wts][k] = v[wts][k] * r
    return bm

def group_weights(obj, bm, arm):
    vgs = obj.vertex_groups
    wts = bm.verts.layers.deform.active
    wt_tags = bm.verts.layers.string.active
    temp = {}
    for a in range(len(vgs)):
        temp[a] = {"rel":[],"abs":[]}
    attached = set()
    for v in [a for a in bm.verts if a[wt_tags]]:
        tag_bin = v[wt_tags]
        fmt = "<{}i".format(len(tag_bin) // 4)
        cp = min(list(struct.unpack(fmt, tag_bin)))
        for g in v[wts].keys():
            kw = "rel" if cp in attached else "abs"
            attached.add(cp)
            temp[g][kw].append(cp)
    result = {}
    for a in temp:
        result[vgs[a].name] = (a,temp[a])
    return bm, result

###
### CP group export
###

def exclude_groups(arm_o):
    return [b.name for b in arm_o.data.bones]

def do_groups(obj, bm, excl_groups, opts):
    gs = bm.verts.layers.deform.verify()
    cp_info = bm.edges.layers.string.active
    link_cp = bm.verts.layers.int.active
    cpgs = {}
    cp_lookup = {}
    for v in bm.verts:
        vi = v.index
        cp_lookup[vi] = [e for e in v.link_edges
            if get_vert(e, cp_info) == vi]
    mat_map = map_mats(obj) if opts["mat_grps"] else {}
    for k in mat_map:
        gn = mat_map[k]
        es = []
        for f in [a for a in bm.faces if a.material_index == k]:
            [es.extend(cp_lookup[v.index]) for v in f.verts]
        if es:
            cpgs[gn] = list(set(es))
    excl_groups.extend(mat_map.values())
    for vg in obj.vertex_groups:
        name = vg.name
        if name not in excl_groups:
            idx = vg.index
            cpgs[name] = []
            for v in bm.verts:
                if idx in v[gs]:
                    cpgs[name].extend(cp_lookup[v.index])
    result = ""
    for g in cpgs:
        cp_str = "".join(["{}\n".format(e.index + 1) for e in cpgs[g]])
        result += tag(
            "GROUP",
            "Name={}\n{}".format(g, tag("CPS", cp_str)))
    return tag("GROUPS", result)

def map_mats(obj):
    result = {}
    mss = obj.material_slots
    for msi in range(len(mss)):
        ms = mss[msi]
        mat = ms.material
        if mat:
            result[msi] = mat.name
    return result

###
### Shape key export
###

def maybe_shapes(bm, mdl_path):
    shapes = {}
    cp_info = bm.edges.layers.string.active
    link_cp = bm.verts.layers.int.active
    ks = bm.verts.layers.shape.items()
    if not ks:
        return
    cmtx = correct()
    for name, li in ks:
        shapes[name] = [cmtx * v[li] for v in bm.verts]
    result = {}
    if compat(2, 73, 0):
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
    for s in shapes:
        diff = []
        for v, m_xyz in zip(bm.verts, shapes[s]):
            cp = v[link_cp]
            if cp >= 0:
                r = bm.edges[cp]
                while True:
                    if get_init(r, cp_info):
                        break
                    r = bm.edges[get_pred(r, cp_info)]
                delta = m_xyz - v.co
                if delta.magnitude > 0.000001:
                    diff.append((cp,r.index,delta))
        if diff:
            result[s] = diff
    write_actions(result, mdl_path)

def write_actions(sd, mdl_path):
    dir, mdl = os.path.split(mdl_path)
    base = "".join(mdl.split(".")[:-1])
    for a in sd:
        for bad_char in "\\/:*?\"<>|":
            a = a.replace(bad_char, "")
        act_name = base + "-" + a + ".act"
        act_path = os.path.join(dir, act_name)
        contents = format_action(a, sd[a], base)
        f = open(act_path, 'w')
        f.write(contents)
        f.close()
        print("File \"" + act_path + "\" written successfully.")

def format_action(name, data, model):
    coords = ""
    for (cp, r, xyz) in data:
        coords += "{} {} 0 {:.6f} {:.6f} {:.6f}\n".format(
            cp + 1, r + 1, xyz.x, xyz.y, xyz.z)
    fluff1 = "ProductVersion=17\nRelease=17.0 PC\n"
    fluff2 = "DefaultModel={}\n".format(model)
    return tag("ACTIONFILE",
        fluff1 + tag("ACTIONS",
            tag("ACTION",
                fluff2 + tag("SPLINECONTAINERSHORTCUT",
                    tag("COMPACTMUSCLECHANNELS", coords)))))

###
### A:M-friendly mesh tools
###

def am_copy():
    sel = [o for o in bpy.context.selected_objects if
        o.type == 'MESH']
    for o in sel:
        bpy.ops.object.mode_set()
        bpy.ops.object.select_all(action='DESELECT')
        o.select = True
        bpy.context.scene.objects.active = o
        bpy.ops.object.duplicate()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bevel(offset=0.001)
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.edge_collapse()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=5, type='GREATER')
        ### hatching
        bpy.ops.mesh.bevel(offset=10.0, offset_type='PERCENT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.dissolve_faces()
        bpy.ops.mesh.hatch_face()
        ### end hatching
        bpy.ops.mesh.vertices_smooth(repeat=10)
        bpy.ops.object.mode_set()
    return {'FINISHED'}

def hatch(fi, bm):
    if compat(2, 73, 0):
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
    f = bm.faces[fi]
    vs = [v.index for v in f.verts if
        len(v.link_edges) == 3 and
        v.is_manifold]
    if vs and len(vs) >= 2:
        vs = vs[1:] + [vs[0]] # turn ccw - usually needed
        if len(vs) % 2:
            vs.pop()
        l = len(vs)
        a = l // 2
        b = l // 4
        c = a - b
        vs1 = vs[:a]
        vs2 = vs[a:]
        fsts1 = vs1[:b]
        fsts2 = vs2[:b]
        fsts2.reverse()
        snds1 = vs1[b:]
        snds2 = vs2[b:]
        snds2.reverse()
        es = []
        conn0 = [snds2]
        for p in zip(fsts1, fsts2):
            v1 = bm.verts[p[0]]
            v2 = bm.verts[p[1]]
            data = bmesh.ops.connect_verts(bm, verts=[v1, v2])
            e = data['edges'][0]
            data0 = bmesh.ops.bisect_edges(bm, edges=[e], cuts=c)
            new_vs = [v.index for v in data0['geom_split'] if
                v in bm.verts]
            new_vs0 = []
            l = fsts1
            while new_vs:
                if compat(2, 73, 0):
                    bm.faces.ensure_lookup_table()
                    bm.verts.ensure_lookup_table()
                nxt = [v for v in new_vs if
                    bm.verts[v].link_edges[0].
                        other_vert(bm.verts[v]).index in l or
                    bm.verts[v].link_edges[1].
                        other_vert(bm.verts[v]).index in l][0]
                new_vs0.append(nxt)
                l = [new_vs.pop(new_vs.index(nxt))]
            conn0.append(new_vs0)
        conn0.append(snds1)
        conn1 = []
        for i in range(c):
            conn1.append([])
            for n in range(len(conn0)):
                conn1[-1].append(conn0[n][i])
        for l in conn1:
            v1 = l.pop()
            while l:
                v2 = l.pop()
                vl = [bm.verts[v1], bm.verts[v2]]
                bmesh.ops.connect_verts(bm, verts=vl)
                v1 = v2
        for l in conn0[1:-1]:
            for v in l:
                for f in bm.verts[v].link_faces:
                    f.select = True
        bm.verts.index_update()
        bm.faces.index_update()
        bm.edges.index_update()
    return bm

###
### Ops
###

class AMMesh(bpy.types.Operator):
    '''Make an Animation:Master-ready copy of a mesh.'''
    bl_idname = "mesh.am_mesh"
    bl_label = 'Make A:M-Friendly Copy'
    bl_options = {'PRESET'}
    def execute(self, context):
        return am_copy()

class HatchFace(bpy.types.Operator):
    '''Cut a hatch pattern of edges across a face.'''
    bl_idname = "mesh.hatch_face"
    bl_label = 'Hatch Face'
    bl_options = {'PRESET'}
    def execute(self, context):
        bpy.ops.object.mode_set()
        bpy.ops.object.mode_set(mode='EDIT')
        m = context.active_object.data
        bm = bmesh.from_edit_mesh(m)
        sel = [f.index for f in bm.faces if f.select]
        for f in bm.faces:
            f.select = False
        for i in sel:
            bm = hatch(i, bm)
            bmesh.update_edit_mesh(m)
        return {'FINISHED'}

###
### UI
###

class ExportAMMdl(bpy.types.Operator, ExportHelper):
    '''Save an Animation:Master Model File'''
    bl_idname = "export_scene.am_mdl"
    bl_label = 'Export MDL'
    bl_options = {'PRESET'}
    filename_ext = ".mdl"
    filter_glob = StringProperty(
        default="*.mdl",
        options={'HIDDEN'})
    path_mode = path_reference_mode
    check_extension = True
    path_mode = path_reference_mode
    whiskers = BoolProperty(
        name="Add tails",
        default=True,
        description="Add tails where patches end or splines become discontinuous")
    shapes = BoolProperty(
        name="Export shape keys",
        default=True,
        description="Write an action file for every existing shape key")
    mat_grps = BoolProperty(
        name="Group CPs by material",
        default=True,
        description="Include CP groups based on materials assigned to faces")
    def execute(self, context):
        opts = {
            "whiskers":self.whiskers,
            "shapes":self.shapes,
            "mat_grps":self.mat_grps}
        msg, result = do_export(self.filepath, opts)
        if result == {'CANCELLED'}:
            self.report({'ERROR'}, msg)
        print(msg)
        return result

class MaybeExportAMMdl(bpy.types.Operator):
    '''Export the active mesh as an Animation:Master Model File'''
    bl_idname = "export_scene.maybe_am_mdl"
    bl_label = 'Export MDL'
    def invoke(self, context, event):
        obj = bpy.context.active_object
        if not obj:
            msg = "No active object; nothing to export.\n"
            msg += "Select a mesh object and try again."
            print(msg)
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}
        if obj.type != "MESH":
            msg = "The active object is not a mesh; cannot export.\n"
            msg += "Select a mesh object and try again."
            print(msg)
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}
        return bpy.ops.export_scene.am_mdl('INVOKE_DEFAULT')

class AMFriendlyTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = "VIEW3D_PT_AMFriendly"
    bl_label = "A:M Middleman"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        col = self.layout.column()
        col.operator("mesh.am_mesh")
        if context.mode == 'EDIT_MESH' \
            and context.tool_settings.mesh_select_mode[2]:
            col.operator("mesh.hatch_face")

def menu_func_export_mdl(self, context):
    self.layout.operator(
        MaybeExportAMMdl.bl_idname, text="Animation:Master Model (.mdl)")

def register():
    bpy.utils.register_class(MaybeExportAMMdl)
    bpy.utils.register_class(ExportAMMdl)
    bpy.utils.register_class(AMMesh)
    bpy.utils.register_class(HatchFace)
    bpy.utils.register_class(AMFriendlyTools)
    bpy.types.INFO_MT_file_export.append(menu_func_export_mdl)

def unregister():
    bpy.utils.unregister_class(MaybeExportAMMdl)
    bpy.utils.unregister_class(ExportAMMdl)
    bpy.utils.unregister_class(AMMesh)
    bpy.utils.unregister_class(HatchFace)
    bpy.utils.unregister_class(AMFriendlyTools)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_mdl)

if __name__ == "__main__":
    register()
