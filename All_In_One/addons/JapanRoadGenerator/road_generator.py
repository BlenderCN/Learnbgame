"""参考: https://ja.wikipedia.org/wiki/%E9%81%93%E8%B7%AF%E6%A7%8B%E9%80%A0%E4%BB%A4"""

import mathutils
import math
import bpy
import bmesh

# 中央分離帯 median

"""道路構造令における道路の区分"""
road_type = {
    11: '第1種 第1級', 
    12: '第1種 第2級', 
    13: '第1種 第3級', 
    14: '第1種 第4級', 
    21: '第2種 第1級', 
    22: '第2種 第2級', 
    31: '第3種 第1級', 
    32: '第3種 第2級', 
    33: '第3種 第3級', 
    34: '第3種 第4級', 
    35: '第3種 第5級', 
    41: '第4種 第1級', 
    42: '第4種 第2級', 
    43: '第4種 第3級', 
    44: '第4種 第4級'
}

"""設計速度"""
design_speed = {
    11: (120), 
    12: (100), 
    13: (80), 
    14: (60), 
    21: (80), 
    22: (60), 
    31: (80), 
    32: (60), 
    33: (40, 50, 60), 
    34: (30, 40, 50), 
    35: (20, 30, 40), 
    41: (60), 
    42: (40, 50, 60), 
    43: (30, 40, 50), 
    44: (20, 30, 40)
}

"""最低設計速度"""
min_design_speed = {
    11: (100), 
    12: (80), 
    13: (60), 
    14: (50), 
    21: (60), 
    22: (40, 50), 
    31: (60), 
    32: (40, 50), 
    33: (30), 
    34: (20), 
    35: (), 
    41: (40, 50), 
    42: (30), 
    43: (20), 
    44: ()
}

"""道路幅員（規定値）"""
road_width = {
    11: 3.5, 
    12: 3.5, 
    13: 3.5, 
    14: 3.25, 
    21: 3.5, 
    22: 3.25, 
    31: 3.5, 
    32: 3.25, 
    33: 3.0, 
    34: 2.75, 
    35: 2.75, # 仮
    41: 3.25, 
    42: 3.0, 
    43: 3.0, 
    44: 3.0  # 仮
}

"""道路幅員（特例値）"""
road_width_exception = {
    11: 3.75, 
    12: 3.75, 
    21: 3.25, 
    32: 3.5, 
    41: 3.5
}

RAD2DEG = 360 / (math.pi * 2)

"""都市部の規格であるか"""
def is_urban(road_type):
    return road_type in (21, 22, 41, 42, 43, 44)

"""高速道路に使用可能な規格であるか"""
def is_highway(road_type):
    return road_type in (11, 12, 13, 21)

"""自動車専用道路であるか"""
def is_automobile_road(road_type):
    return road_type in (11, 12, 13, 14, 21, 22)

"""道路管理者。指定が間違っていたりない場合は私道となる"""
road_admin_national = 'national' # 国道
road_admin_prefectural = 'prefectural' # 都道府県道
road_admin_municipal = 'municipal' # 市町村道

"""第1種の最低計画交通量を取得。計画交通量は最低計画交通量以上、最高計画交通量未満となる"""
def get_min_design_daily_volume_type1(road_type, mountainous_area, highway):
    if road_type == 11:
        return 30000
    elif road_type == 12:
        if highway:
            return 30000 if mountainous_area else 10000
        else:
            return 20000
    elif road_type == 13:
        if highway:
            if mountainous_area:
                return 10000
        elif mountainous_area:
            return 20000
    return 0

"""第3種の最低計画交通量を取得。計画交通量は最低計画交通量以上、最高計画交通量未満となる"""
def get_min_design_daily_volume_type3(road_type, mountainous_area, road_admin):
    if road_type == 31:
        return 20000
    elif road_type == 32:
        if road_admin == road_admin_national:
            return 20000 if mountainous_area else 4000
        else:
            return 4000
    elif road_type == 33:
        if (road_admin == road_admin_national or road_admin == road_admin_prefectural) and mountainous_area:
            return 4000
        if road_admin == road_admin_municipal:
            return 4000 if mountainous_area else 1500
    elif road_type == 34 and road_admin == road_admin_municipal:
        return 500
    return 0

"""第4種の最低計画交通量を取得。計画交通量は最低計画交通量以上、最高計画交通量未満となる"""
def get_min_design_daily_volume_type4(road_type, road_admin):
    if road_type == 41:
        return 4000 if road_admin == road_admin_national else 10000
    elif road_type == 42 and road_admin in (road_admin_municipal, road_admin_prefectural):
        return 4000
    elif road_type == 43 and road_admin == road_admin_municipal:
        return 500
    return 0

#-----



"""第1種の最高計画交通量を取得。指定なしの場合は0を返す。get_road_type*には最低計画交通量を使用すること"""
def get_max_design_daily_volume_type1(road_type, mountainous_area, highway):
    if road_type == 12:
        if highway and not mountainous_area:
            return 30000
    elif road_type == 13:
        if highway:
            return 30000 if mountainous_area else 10000
        elif not mountainous_area:
            return 20000
    elif road_type == 14:
        return 10000 if highway else 20000
    return 0

"""第3種の最高計画交通量を取得。指定なしの場合は0を返す。get_road_type*には最低計画交通量を使用すること"""
def get_max_design_daily_volume_type3(road_type, mountainous_area, road_admin):
    if road_type == 32:
        if road_admin == road_admin_national and not mountainous_area:
            return 20000
    elif road_type == 33:
        if road_admin == road_admin_national:
            return 20000 if mountainous_area else 4000
        elif road_admin == (road_admin_municipal, road_admin_prefectural) and not mountainous_area:
            return 4000
    elif road_type == 34:
        if road_admin == (road_admin_prefectural, road_admin_national):
            return 4000
        elif road_admin == road_admin_municipal:
            return 4000 if mountainous_area else 1500
    elif road_type == 35:
        return 500
    return 0

"""第4種の最高計画交通量を取得。指定なしの場合は0を返す。get_road_type*には最低計画交通量を使用すること"""
def get_max_design_daily_volume_type4(road_type, road_admin):
    if road_type == 42:
        return 4000 if road_admin == road_admin_national else 10000
    elif road_type == 43:
        return 4000
    elif road_type == 44:
        return 500
    return 0

#-----



"""第1種の道路の区分を取得"""
def get_road_type1(highway, mountainous_area, design_daily_volume):
    if not highway:
        if mountainous_area:
            return 12 if design_daily_volume >= 30000 else 13 if design_daily_volume >= 10000 else 14
        else:
            return 11 if design_daily_volume >= 30000 else 12 if design_daily_volume >= 10000 else 13
    else:
        if mountainous_area:
            return 13 if design_daily_volume >= 20000 else 14
        else:
            return 12 if design_daily_volume >= 20000 else 13

"""第2種の道路の区分を取得"""
def get_road_type2(highway, inner_city):
    return 22 if not highway and inner_city else 21

"""第3種の道路の区分を取得"""
def get_road_type3(road_admin, mountainous_area, design_daily_volume):
    if road_admin == road_admin_national:
        if mountainous_area:
            return 32 if design_daily_volume >= 20000 else 33 if design_daily_volume >= 4000 else 34
        else:
            return 31 if design_daily_volume >= 20000 else 32 if design_daily_volume >= 4000 else 33
    elif road_admin == road_admin_prefectural:
        if mountainous_area:
            return 33 if design_daily_volume >= 4000 else 34
        else:
            return 32 if design_daily_volume >= 4000 else 33
    elif road_admin_municipal:
        if mountainous_area:
            return 33 if design_daily_volume >= 4000 else 34 if design_daily_volume >= 500 else 35
        else:
            return 32 if design_daily_volume >= 4000 else 33 if design_daily_volume >= 1500 else 34 if design_daily_volume >= 500 else 35

"""第4種の道路の区分を取得"""
def get_road_type4(road_admin, design_daily_volume):
    if road_admin == road_admin_national:
        return 41 if design_daily_volume >= 4000 else 42
    elif road_admin == road_admin_prefectural:
        return 41 if design_daily_volume >= 10000 else 42 if design_daily_volume >= 4000 else 43
    elif road_admin_municipal:
        return 41 if design_daily_volume >= 10000 else 42 if design_daily_volume >= 4000 else 43 if design_daily_volume >= 500 else 44





"""車線に使用する辺を生成する"""
def lanes_generate(ops, left_lanes, right_lanes, road_width, offset, invert):
    bpy.ops.object.mode_set(mode='EDIT')
    me = bpy.context.edit_object.data
    bm = bmesh.from_edit_mesh(me)

    edges = [e for e in bm.edges if e.select and not e.hide]

    lines = get_lines(edges)
    if len(lines) != 1:
        ops.report({"WARNING"}, "１つの線になるように辺を選択して下さい")
        return False

    vs = get_sorted_verts(lines[0])
    if invert:
        vs.reverse()

    vs_n = []

    rot_l = mathutils.Euler((0.0, 0.0, math.radians(90.0)), 'XYZ')
    rot_r = mathutils.Euler((0.0, 0.0, math.radians(-90.0)), 'XYZ')

    rot_c = None
    for n, v in enumerate(vs):
        v.select = False
        vb = None
        vf = None
        if n != 0:
            vb = vs[n - 1]
        if n != len(vs) - 1:
            vf = vs[n + 1]

        co_bn = None
        co_fn = None
        if vb != None:
            rot_b = (v.co - vb.co)
            rot_b.z = 0.0
            rot_b.normalize()
            co_bn = mathutils.Vector(rot_b)
            co_bn.rotate(rot_l)
            co_bn *= road_width / 2
        if vf != None:
            rot_f = (vf.co - v.co)
            rot_f.z = 0.0
            rot_f.normalize()
            co_fn = mathutils.Vector(rot_f)
            co_fn.rotate(rot_l)
            co_fn *= road_width / 2

        if n == 0:
            vs_n = vs_n + [v.co + co_fn]
        elif n == len(vs) - 1:
            vs_n = vs_n + [v.co + co_bn]
        else:
            vc = get_cross_point(vb.co + co_bn, v.co + co_bn, vf.co + co_fn, v.co + co_fn, False)
            vc.z = v.co.z
            vs_n = vs_n + [vc]

    vb = None

    for v in zip(vs_n):
        nv = bm.verts.new(v)

        if vb != None:
            bm.edges.new([vb, nv]).select = True

        vb = nv

    bmesh.update_edit_mesh(me)
    return True





"""道路を生成する"""# 交差点を生成する処理は別
def road_generate(ops, road_width, invert):
    bpy.ops.object.mode_set(mode='EDIT')
    me = bpy.context.edit_object.data
    bm = bmesh.from_edit_mesh(me)

    edges = [e for e in bm.edges if e.select and not e.hide]

    lines = get_lines(edges)
    if len(lines) != 1:
        ops.report({"WARNING"}, "１つの線になるように辺を選択して下さい")
        return False

    vs = get_sorted_verts(lines[0])
    if invert:
        vs.reverse()

    vs_l = []
    vs_r = []

    rot_l = mathutils.Euler((0.0, 0.0, math.radians(90.0)), 'XYZ')
    rot_r = mathutils.Euler((0.0, 0.0, math.radians(-90.0)), 'XYZ')

    rot_c = None
    for n, v in enumerate(vs):
        #v.select = False
        vb = None
        vf = None
        if n != 0:
            vb = vs[n - 1]
        if n != len(vs) - 1:
            vf = vs[n + 1]

        co_bl = None
        co_br = None
        co_fl = None
        co_fr = None
        if vb != None:
            rot_b = (v.co - vb.co)
            rot_b.z = 0.0
            rot_b.normalize()
            co_bl = mathutils.Vector(rot_b)
            co_bl.rotate(rot_l)
            co_bl *= road_width / 2
            co_br = mathutils.Vector(rot_b)
            co_br.rotate(rot_r)
            co_br *= road_width / 2
        if vf != None:
            rot_f = (vf.co - v.co)
            rot_f.z = 0.0
            rot_f.normalize()
            co_fl = mathutils.Vector(rot_f)
            co_fl.rotate(rot_l)
            co_fl *= road_width / 2
            co_fr = mathutils.Vector(rot_f)
            co_fr.rotate(rot_r)
            co_fr *= road_width / 2

        if n == 0:
            vs_l = vs_l + [v.co + co_fl]
            vs_r = vs_r + [v.co + co_fr]
        elif n == len(vs) - 1:
            vs_l = vs_l + [v.co + co_bl]
            vs_r = vs_r + [v.co + co_br]
        else:
            vc = get_cross_point(vb.co + co_bl, v.co + co_bl, vf.co + co_fl, v.co + co_fl, False)
            vc.z = v.co.z
            vs_l = vs_l + [vc]
            vc = get_cross_point(vb.co + co_br, v.co + co_br, vf.co + co_fr, v.co + co_fr, False)
            vc.z = v.co.z
            vs_r = vs_r + [vc]

    vb = None
    vbl = None
    vbr = None

    for v, vl, vr in zip(vs, vs_l, vs_r):
        vfl = bm.verts.new(vl)
        vfr = bm.verts.new(vr)

        if vb != None:
            bm.faces.new([vfl, vbl, vb, v]).select = True
            bm.faces.new([v, vb, vbr, vfr]).select = True

        vb = v
        vbl = vfl
        vbr = vfr

    bmesh.update_edit_mesh(me)
    bm.calc_tessface()
    bm.normal_update()
    return True

"""複数の繋がった辺を枝ごとに分ける（辺の向きは揃っていない）"""
def get_lines(edges):
    lines = []
    ec = edges
    a = False
    while len(ec) != 0:
        b = True
        ec2 = []
        for n, e in enumerate(ec):
            if len(lines) == 0:
                lines.extend([[ec[0]]])
            else:
                v = e.verts[0]
                n2 = 0
                l = None
                for line in lines:
                    for edge in line:
                        for v2 in edge.verts:
                            if v2 == v:
                                n2 += 1
                    l = line
                if n2 == 0:
                    v = e.verts[1]
                    for line in lines:
                        for edge in line:
                            for v2 in edge.verts:
                                if v2 == v:
                                    n2 += 1
                        l = line
                    if n2 == 0:
                        if a and b:
                            b = False
                            lines.extend([[e]])
                        else:
                            ec2.append(e)
                    elif n2 == 1:
                        b = False
                        for v2 in l[0].verts:
                            if v2 == v:
                                l.insert(0, e)
                                break
                        else:
                            l.append(e)
                    else:
                        lines.extend([[e]])
                elif n2 == 1:
                    b = False
                    for v2 in l[0].verts:
                        if v2 == v:
                            l.insert(0, e)
                            break
                    else:
                        l.append(e)
                else:
                    lines.extend([[e]])
        a = b
        ec = ec2
    return lines

"""複数の辺の頂点を揃えて返す"""
def get_sorted_verts(line):
    verts = []
    v = None
    for e in line:
        if v == None:
            for v2 in e.verts:
                a = 0
                for e2 in line:
                    for v3 in e2.verts:
                        if v2 == v3:
                            a += 1
                if a == 1:
                    v = v2
                    verts = verts + [v]
                    break
        for v2 in e.verts:
            if v2 != v:
                v = v2
                break
        verts = verts + [v]
    return verts

"""交点を求める（XY軸）"""
def get_cross_point(p1, p2, p3, p4, intersect):
    d = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x)
    if d == 0:
        return null
    u = ((p3.x - p1.x) * (p4.y - p3.y) - (p3.y - p1.y) * (p4.x - p3.x)) / d
    v = ((p3.x - p1.x) * (p2.y - p1.y) - (p3.y - p1.y) * (p2.x - p1.x)) / d
    if intersect:
        if u < 0.0 or u > 1.0:
            return null
        if v < 0.0 or v > 1.0:
            return null
    intersection = mathutils.Vector()
    intersection.x = p1.x + u * (p2.x - p1.x)
    intersection.y = p1.y + u * (p2.y - p1.y)
    return intersection
