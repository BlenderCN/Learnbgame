# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from . import armature_fs
from . import bone_fs
from . import mod_fs
from . import lattice_fs
from .. import gtls
from g_tools.gtls import defac,get_ac,set_ac,set_mode,moderate,get_sel_obj,get_sel_objs


@defac
def get_splines(obj=None):
    return obj.data.splines


@defac
def set_spline_props(prop, val, spline_range=None, obj=None, ):
    spls = get_splines(obj=obj)
    if spline_range:
        spls = map(lambda sidx: spls[sidx], range(*spline_range))
    original_data = tmap(lambda s: getattr(s, prop), spls)
    any(map(lambda s: attrmap(s, prop, val)), spls)
    return original_data


@defac
def set_radii(val, sidx=0, obj=None, ):
    verts = obj.data.splines[sidx].points
    original_data = tmap(lambda v: getattr(v, "radius"), verts)
    attrmap(verts, "radius", val)
    return original_data


@defac
def set_tilt(val, sidx=0, obj=None, ):
    verts = obj.data.splines[sidx].points
    original_data = tmap(lambda v: getattr(v, "tilt"), verts)
    attrmap(verts, "tilt", val)
    return original_data


@defac
def clear_radii(obj=None, sidx=0):
    return set_radii(1, obj=obj)


@defac
def clear_tilt(obj=None, sidx=0):
    return set_tilt(0, obj=obj)


@defac
def set_radii_all(val, obj=None, ):
    return set_spline_props("radius", val, obj=obj, )


@defac
def set_tilt_all(val, obj=None, ):
    return set_spline_props("tilt", val, obj=obj, )


@defac
def poly_convert(obj=None):
    c = obj
    anymap(lambda spl: setattr(spl, "resolution_u", 1), c.splines)
    anymap(lambda spl: setattr(spl, "order_u", 1), c.splines)
    c.type = "POLY"


@defac
def poly_convert_all(obj=None):
    return set_spline_props("type", "POLY", obj=obj)

def get_curve_dist(verts = None,obj = None,i = None):
    if obj:
        verts = obj.data.splines[0].points
    if i == None:
        i = len(verts)
    coords = tuple(v.co.xyz for v in verts[0:i])
    return reduce(lambda x,y: [y,x[1]+(x[0] - y).length],([coords[0],0],*coords))[1]

@defac
def make_curve_lattice(obj = None,reso = None,use_outside = True,scale = None,do_parent = True,add_group = None):
    if reso == None:
        reso = (2,2,2)
    nlat = gtls.make_obj(obj_type = "LATTICE",obj_name = "New_Cv_Lattice")
    if do_parent:
        object_parent(obj = obj,sobj = nlat)
    dist = get_curve_dist(obj = obj)
    bev_dist = get_curve_dist(obj = obj.data.bevel_object)
    nlat.scale[0] = dist
    nlat.location[0] = dist*.5
    lattice_fs.set_lattice_resolution(reso,obj = nlat)
    nlat.data.use_outside = use_outside
    nlat.scale[1] = bev_dist
    return nlat

def  unpack_splines(objs):
    try:
        l = len(objs)
    except:
        objs = (objs,)
    vs = tuple(rec_unmap(map(lambda v: v,unpack(map(lambda s: s.points,unpack(map(lambda o: o.data.splines,objs)))))))
    return vs

@defac
def symmetrize_spline(obj = None,mirror_func = None):
    pts = unpack_splines(obj = obj)
    c = obj.data
    spls = c.splines
    lenspls = len(spls)
    rlenspls = tuple(range(lenspls))
    spl_types = tuple(map(lambda s:c.splines.new(type = spls[s].type),rlenspls))
    spl_points = tuple(map(lambda s:s.points,spls))
    spl_lens = tuple(map(lambda collidx:len(spl_points[collidx]),rlenspls))
    nspls = tuple(map(lambda s:c.splines.new(type = spls[s].type),range(lenspls)))

    new_spline_points = tuple(map(lambda sidx: nspls[sidx].points.add(spl_lens[sidx]-1),rlenspls))
    new_spline_points = tuple(map(lambda sidx:
        tuple(map(lambda vidx: setattr(nspls[sidx].points[vidx],"co",spls[sidx].points[vidx].co),
        range(spl_lens[sidx]))),
        rlenspls))

    all(map(lambda sidx: prop_copy(nspls[sidx],spls[sidx],),rlenspls))

    if mirror_func == None:
        def mirror_func(nspls,spls):
            for s in nspls:
                for v in s.points:
                    v.co[0] = v.co[0] *-1
    mirror_func(nspls,spls)
    return nspls

@defac
def curve_to_armature(obj = None,base_name = "Bone",make_new_arm = True,arm = None,do_armature = True,scale = .5,do_symmetrize = False,obj_trans_copy = True,bone_props = None,root_bone = None,use_apply_on_spline = False,align_bones = False,do_bone_parent = True):
    if bone_props == None:
        bone_props = {}
    if make_new_arm:
        arm = gtls.make_arm(name = "arm_to_curve_" + obj.name)
    else:
        if arm == None:
            arm = get_sel_obj()


    for i in rlen(arm.layers):
        arm.layers[i] = True
    arm.data.draw_type = "STICK"
    mods = obj.modifiers
    splines = tuple(s.bezier_points if s.type == "BEZIER" else s.points for s in obj.data.splines)

    ac = set_ac(arm)
    res = tuple(map(lambda verts: tuple(map(lambda v: bone_fs.make_bone(name = base_name+str(verts[0]),scale = scale,obj = arm,loc = v.co[0:3],props = bone_props),verts[1])),enumerate(splines)))
    res = unpack(res)
    res = list(b.name for b in res)
    res.sort()

    #rootボーンが指定された場合、チュープルの前に置いとく
    if root_bone == None:
        bone_names = res
    else:
        bone_names = (root_bone,*res)

    if do_armature:
        mod = mods.new(name = "Curve_to_Armature",type = "ARMATURE")
        props = {"use_vertex_groups":not use_apply_on_spline,"use_bone_envelopes":use_apply_on_spline,"object":arm,"show_in_editmode":True,"use_apply_on_spline":use_apply_on_spline,}
        prop_copy(mod,props)

    if do_symmetrize:
        armature_fs.symmetrize_armature(obj = arm)
        curve_fs.symmetrize_spline(obj = obj)

    if obj_trans_copy:
        bone_fs.bone_trans(obj.matrix_world,bone_names = bone_names,obj = arm,scale = scale)

    mode = set_mode("EDIT")
    ebones = arm.data.edit_bones
    c = 0
    for s in rlen(splines):
        c+=0
        ls = len(splines[s])
        if do_bone_parent:
            bone_fs.ordered_bone_parent(bone_names[c:(c+ls)],obj = arm)
        if align_bones:
            for b in range(ls-1):
                b1 = ebones[bone_names[c]]
                b2 = ebones[bone_names[c+1]]
                b1.tail = b2.head
                c+=1
        c+=1
    set_mode(mode)
    set_ac(ac)

    return arm


def init_curve(cobj,curve_type = "n",scale = 1,point_count = 5):
    typedict = {'b':"BEZIER",'n':"NURBS",'p':"POLY"}
    curvetype = typedict[curve_type]
    c = cobj.data
    c.dimensions = "3D"
    ns = c.splines.new(type = curvetype)
    ns.use_endpoint_u = True
    
    vec = None
    if curvetype == "POLY":
        vec = Vector((0,0,0))
    elif curvetype == "NURBS":
        vec = Vector((0,0,0,1))
        
    ns.points[0].co = vec.copy()
    for x in range(1,point_count):
        ns.points.add(1)
        vec[0] = x*scale
        ns.points[-1].co = vec.copy()
    del vec
    
def make_minimum_curve():
    new_curve = make_init_curve()
    new_curve.data.resolution_u = 1
    new_curve.data.splines[0].order_u = 2
    return new_curve
    
def init_curve_bez(c,point_count = 3):
    c.dimensions = "3D"
    ns = c.splines.new(type = "BEZIER")
    ns.bezier_points[-1].handle_left = Vector((+0.3904115,0,0))
    ns.bezier_points[-1].handle_right = Vector((-0.3904115,-0,0))
    for x in range(1,point_count):
        vec = Vector((-x,0,0))
        ns.bezier_points.add(1)
        np = ns.bezier_points[-1]
        np.co = vec
        np.handle_left = Vector((-x+0.3904115,0,0))
        np.handle_right = Vector((-x-0.3904115,-0,0))
    
def make_init_curve(type = "n",name = "init_curve"):
    nc = make_curve()
    if type == "b":
        init_curve_bez(nc)
    else:
        init_curve(nc)
    nc.name = name
    return nc
    
def make_init_bev(type = "n",name = "init_curve",point_count = 3):
    type = type.lower()
    nc = make_curve()
    if type == "b":
        init_curve_bez(nc,point_count = point_count)
    else:
        init_curve(nc,point_count = point_count)
    verts = nc.data.splines[0].points
    #mid_idx = int(point_count/2)
    #cos = tuple(x-mid_idx for x in rlen(verts))
    pc = point_count - 1
    pcts = tuple(x/pc for x in rlen(verts))
    cos = tuple(lerp(-.5,.5,x) for x in pcts)
    passmap(lambda vidx: setattrate(verts[vidx],co = (cos[vidx],0,0,1)),rlen(verts))
    nc.name = name
    return nc
    
    
def make_bevel_curve(split_bevel=True, curve_type="n", bevel_curve_type="p", use_existing_bevel=False,
                bevel_obj_name="Bevel_curve"):
    objs = bpy.context.scene.objects
    curve_type_dict = {"NURBS": "NURBS", "POLY": "POLY", "BEZIER": "BEZIER", "n": "NURBS", "p": "POLY",
                       "b": "BEZIER"}
    nc = gtls.make_obj(type="CURVE", name="Basis_curve")
    prop_dict = {"data.dimensions": "3D", "data.use_uv_as_generated": True, "data.use_stretch": True,
                 "data.use_deform_bounds": True}
    nc.data.dimensions = "3D"
    nc.data.use_uv_as_generated = True
    nc.data.use_stretch = True
    nc.data.use_deform_bounds = True
    nspl = nc.data.splines.new(type=curve_type_dict[curve_type])
    nspl.use_endpoint_u = True
    nc.location = bpy.context.scene.cursor_location
    set_ac(nc)
    nc.select = True
    nspl.points.add(4)
    for x in range(5):
        nspl.points[x].co = (x, 0, 0, 1)
    nspl.order_u = 5

    if use_existing_bevel:
        nc2 = objs[bevel_obj_name]
    else:
        nc2 = gtls.make_obj(type="CURVE", name="Bevel_curve")
    nc2.data.dimensions = "3D"
    nc2.data.use_uv_as_generated = True
    nc2.data.use_stretch = True
    nc2.data.use_deform_bounds = True
    nspl2 = nc2.data.splines.new(type=curve_type_dict[bevel_curve_type])
    nspl2.use_endpoint_u = True
    if split_bevel:
        nspl2.points.add(1)
        nspl3 = nc2.data.splines.new(type="POLY")
        nspl3.use_endpoint_u = True
        nspl3.points.add(1)
        for x in range(2):
            nspl2.points[x].co = (x, -x, 0, 1)
        for x in range(2):
            nspl3.points[x].co = (-x, -x, 0, 1)
    else:
        nspl2.points.add(2)
        for x in range(3):
            nspl2.points[x].co = (x - 1, -abs(1 - x), 0, 1)
    nc.data.bevel_object = nc2

    return (nc, nc2)
    

def simple_hair_curve(split_bevel = True,curve_type = "n",bevel_curve_type = "p",use_existing_bevel = False,bevel_obj_name = "Bevel_curve",use_cyclic_u = True,use_fill_caps = True,zero_last_radius = True):
    objs = bpy.context.scene.objects
    curve_type_dict = {"NURBS":"NURBS","POLY":"POLY","BEZIER":"BEZIER","n":"NURBS","p":"POLY","b":"BEZIER"}
    nc = gtls.make_obj(type = "CURVE",name = "Basis_curve")
    prop_dict = {"data.dimensions":"3D","data.use_uv_as_generated":True,"data.use_stretch":True,"data.use_deform_bounds":True}
    nc.data.dimensions = "3D"
    nc.data.use_uv_as_generated = True
    nc.data.use_stretch = True
    nc.data.use_deform_bounds = True
    nc.data.use_fill_caps = use_fill_caps
    nspl = nc.data.splines.new(type = curve_type_dict[curve_type])
    nspl.use_endpoint_u = True
    nc.location = bpy.context.scene.cursor_location
    set_ac(nc)
    nc.select = True
    nspl.points.add(4)
    for x in range(5):
        nspl.points[x].co = (x,0,0,1)
    nspl.order_u = 5
    
    if use_existing_bevel:
        nc2 = objs[bevel_obj_name]
    else:
        nc2 = gtls.make_obj(type = "CURVE",name = "Bevel_curve")
    nc2.data.dimensions = "3D"
    nc2.data.use_uv_as_generated = True
    nc2.data.use_stretch = True
    nc2.data.use_deform_bounds = True
    nspl2 = nc2.data.splines.new(type = curve_type_dict[bevel_curve_type])
    nspl2.use_endpoint_u = True
    if split_bevel:
        nspl2.points.add(1)
        nspl3 = nc2.data.splines.new(type = "POLY")
        nspl3.use_endpoint_u = True
        nspl3.points.add(1)
        for x in range(2):
            nspl2.points[x].co = (x,-x,0,1)
        for x in range(2):
            nspl3.points[x].co = (-x,-x,0,1)
    else:
        nspl2.points.add(2)
        for x in range(3):
            nspl2.points[x].co = (x-1,-abs(1-x),0,1)
    nc.data.bevel_object = nc2
    
    if zero_last_radius:
        for s in nc.data.splines:
            s.points[-1].radius = 0
    
    for s in nc2.data.splines:
        s.use_cyclic_u = use_cyclic_u
    
    return(nc,nc2)
