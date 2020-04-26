# -*- coding: utf-8 -*-
import bpy
import bmesh
from g_tools.nbf import *
from g_tools.gtls import defac,get_ac,set_ac,set_mode,moderate,get_sel_obj,get_sel_objs
from .. import gtls

#########################################################デコレーター/decorators
def basis_ensure(f):
    def basis_ensured(*args,obj = None,**kwargs):
        if obj.data.shape_keys == None:
            bss = obj.shape_key_add("Basis")
        res = f(*args,obj = obj,**kwargs)
        return res
    return basis_ensured
    
def check_keys(f):
    def checked(*args,obj = None,**kwargs):
        sks = obj.data.shape_keys
        if sks == None:
            bss = obj.shape_key_add(name = "Basis")
        return f(*args,obj = obj,**kwargs)
    return checked   

def sk_context(f):
    @basis_ensure
    def sk_contexted(*args,obj = None,keys = None,**kwargs):
        if obj == None:
            obj = get_ac()
        if keys == None:
            keys = obj.data.shape_keys.key_blocks
        res = f(*args,obj = obj,keys = keys,**kwargs)
        return res
    return sk_contexted
    
def bm_veferate(f):
    @defac
    def bm_vefed(bm,*args,verts = None,edges = None,faces = None,**kwargs):
        if verts == None:
            verts = bm.verts
        if edges == None:
            edges = bm.edges
        if faces == None:
            faces = bm.faces
        return f(bm,*args,verts = verts,edges = edges,faces = faces,**kwargs)
    return bm_vefed

@defac
def get_bm_data(coll,prop,obj = None,bm = None):
    if bm == None:
        bm = get_bmesh(obj = obj)
    res = filter(lambda i: getattr(i,prop),getattr(bm,coll))
    if bm == None:
        bm.free()
    return res
    
def state_preserve(coll,props):
    def state_preserver(f):
        def state_preserved(*args,**kwargs):
            __saved_states = map(lambda prop: save_states(coll,prop),props)
            res = f(*args,**kwargs)
            restore_states(coll,props,__saved_states )
            return res
        return state_preserved
    return state_preserver
    
def bm_install(f):
    def bm_installerated(obj = None,bm = None,*args,**kwargs):
        do_clean = False
        if bm == None:
            do_clean = True
            bm = get_bmesh(obj = obj)
        res = f(obj = obj,bm = bm,*args,**kwargs)
        if do_clean:
            bm.free()
        return res
    return bm_installerated

def mesherate(f):
    def mesherated(*args,obj = None,**kwargs):
        if obj == None:
            obj = bpy.context.scene.objects.active
        m = obj.to_mesh(scene = default_scene,settings = "PREVIEW",apply_modifiers = True)
        res = f(obj = (obj,m),*args,**kwargs)
        bpy.data.meshes.remove(m)
        return res
    return mesherated
    

#########################################################選択関連/selection
@defac
def sel_verts(targets,obj = None,state = True,all = False):
    """
    頂点の選択状態をstateに変更する
    :param targets: 頂点オブジェクトまたはインデックスを渡して選択状態をstateに変更する
    :param all: Trueだととりあえず頂点の選択状態ををstateに変更する
    :param obj: defac用
    :return: None
    """
    verts = obj.data.vertices
    if all:
        for v in verts:
            v.select = state
    elif len(targets) == 0:
        return
    elif type(targets[0]) == int:
        for vidx in targets:
            verts[v].select = state
    else:
        for v in targets:
            v.select = state

@defac
def sel_items(targets,obj = None,state = True,all = False,collection = "vertices"):
    """
    何かの選択状態をstateに変更する
    :param targets: 複数オブジェクトまたはインデックスを渡して選択状態をstateに変更する
    :param all: Trueだと、とりあえず複数オブジェクトの選択状態ををstateに変更する
    :param collection: リストのproperty名
    :param obj: defac用
    :return: None
    """
    coll = getattr(obj.data,collection)
    if all:
        targets = coll
    elif len(coll) == 0:
        return
    elif type(targets[0]) == int:
        for i in coll:
            coll[i].select = state
    else:
        for i in targets:
            i.select = state

@defac
def deselect_mesh_parts(obj = None):
    mesh = obj.data
    verts,edges,faces = (mesh.vertices,mesh.edges,mesh.polygons)
    zipped = tuple(zip(verts, edges, faces))
    original_states = tuple(map(lambda items: tuple(map(lambda i: i.select,items),zipped)))
    for items in zipped:
        for i in items:
            i.select = False
    return original_states

@defac
@moderate("OBJECT")
def selectorate(obj = None,selection_mode = "cross_loops",index_count = None,index_offset = None,index_step = None,index_part_type = 'v',check_dict = None,lattice_step_direction = 'u',lattice_limit = False,lattice_reverse = False,oper = None):
    lattice_dict = {"x":"u","y":"v","z":"w"}
    lattice_dict.update(revdict(lattice_dict))
    try:
        compatible_type = check_dict[selection_mode]
        if obj.type == compatible_type:
            pass
        else:
            errstr = "Incompatible selection mode and object type"
            if oper != None:
                oper.report({"INFO"},errstr)
            print(errstr)
            return
    except Exception as e:
    #except:
        print(str(e))
        pass 
    if selection_mode == "cross_loops":
        edge_fs.select_cross_loops(obj = obj,index_step = index_step)
    if selection_mode == "chain_loop":
        edge_fs.chain_loop_select(obj = obj)
    if selection_mode == "3d_cursor":
        pass
    if selection_mode == "lattice_loop":
        lattice_dir_select(lattice_dict[lattice_step_direction],sel_count = index_count,lattice_limit = lattice_limit,lattice_reverse = lattice_reverse,obj = obj,)
    if selection_mode == "dot":
        edge_fs.axis_dot_select(obj = obj)
    if selection_mode == "vector":
        edge_fs.select_cross_loops(obj = obj,index_step = index_step)
    if selection_mode == "index":
        idx_select(index_count, offset = index_offset, step = index_step, part_type = index_part_type,obj = obj,)
       
@defac
@moderate("OBJECT")
def set_lattice_resolution(reso,obj = None):
    obj.data.points_u,obj.data.points_v,obj.data.points_w = reso
    return (reso,obj)    
    
#########################################################bmesh関連/bmesh related
def get_bmesh(obj = None):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    return bm

@defac
def make_hull(do_link=False, name="hull_obj",obj = None):

    tobj = gtls.make_obj(do_link=do_link, obj_name=name, obj_type="MESH")
    bm = get_bmesh(obj=obj)

    mesh = obj.data
    verts = bm.verts
    opres = bmesh.ops.convex_hull(bm, input=verts)

    bm.to_mesh(tobj.data)
    bm.free()

@bm_install
@defac
def get_separated_parts(obj =  None,bm = None):
    objs = bpy.context.scene.objects
    mesh = obj.data
    verts = mesh.vertices
    
    vidxs = range(len(verts))
    
    emem = {}
    vmem = {}
    rem = {v:1 for v in vidxs}
    
    def fnc(es,vmem = None,emem = None,rem = None,res = None):
        if res == None:
            res = []
        for e in es:    
            eidx = e.index
            if try_key(emem,eidx):continue
                
            for v in e.verts:
                vidx = v.index
                try:
                    vmem[vidx]
                    continue
                except:
                    vmem[vidx] = 1
                    res.append(vidx)
                    es = v.link_edges
                    fnc(es,vmem = vmem,emem = emem,rem = rem,res = res)
        return res
    
    vs = list(bm.verts)
    res = []
    
    #using a dictionary to keep track of ungrouped vertices,
    #iterate over all vertices until edges are found for all vertices
    #will probably break if there are floating vertices
    while len(rem) > 0:
        for i in rem:
            es = vs[i].link_edges
            break
        r = fnc(es,vmem = vmem, emem = emem, rem = rem)
        res.append(r)
        for vidx in r:
            rem.pop(vidx)
        
    return res

@bm_install
@defac
def find_doubles_bm(obj=None, bm=None, to_mesh=True, dist=0.0001):
    res = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=dist)
    if to_mesh:
        mesh = obj.data
        bm.to_mesh(mesh)
    return res

@bm_install
@defac
def remove_doubles_bm(obj=None, bm=None, to_mesh=True, dist=0.0001):
    res = bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    dissolve_verts = bm.verts[1:-1]
    # for x in range(len(dissolve_verts)-1,0,-15):
    # dissolve_verts.pop(x)
    # res = bmesh.ops.dissolve_verts(bm,verts = dissolve_verts)
    if to_mesh:
        mesh = obj.data
        bm.to_mesh(mesh)
    return res

@defac
def map_boundary_verts(obj=None, bm=None):
    do_clean = False
    if bm == None:
        do_clean = True
        bm = get_bmesh(obj=obj)
    vidxmap = tmap(lambda v: v.is_boundary, bm.verts)
    if do_clean:
        bm.free()
    return vidxmap

@defac
def get_boundary_verts(obj=None, bm=None):
    do_clean = False
    if bm == None:
        do_clean = True
        bm = get_bmesh(obj=obj)
    vidxmap = map_boundary_verts(obj=obj, bm=bm)
    vidxs = tuple(compress(rlen(bm.verts), vidxmap))
    if do_clean:
        bm.free()
    return vidxs

@defac
def bm_map(obj=None, bm=None, prop="is_manifold"):
    do_clean = False
    if bm == None:
        do_clean = True
        bm = get_bmesh(obj=obj)
    vidxmap = tmap(lambda v: v.is_boundary, bm.verts)
    if do_clean:
        bm.free()
    return vidxmap

@defac
def bm_filter(obj=None, bm=None, prop="is_manifold"):
    do_clean = False
    if bm == None:
        do_clean = True
        bm = get_bmesh(obj=obj)
    vidxmap = bm_map(obj=obj, bm=bm, prop=prop)
    vidxs = tuple(compress(rlen(bm.verts), vidxmap))
    if do_clean:
        bm.free()
    return vidxs

@defac
def get_nmf_verts(obj=None, bm=None):
    return bm_filter(obj=obj, bm=bm, prop="is_manifold")

@defac
@moderate("OBJECT")
@bm_install
def bool_cut_select(obj = None,bm = None):
    nmf = get_nmf_verts()
    
    print(nmf)
    mesh = obj.data
    verts = mesh.vertices
    
    bmverts = list(bm.verts)
    
    for i in nmf:
        v = bmverts[i]
        if len(v.link_edges) < 3:
            v.select = True
    
    bm.to_mesh(obj.data)
    bm.free()
        

#########################################################シェープキー（つまりモーフ）関連/shape key related

@defac
@sk_context
def basis_swap(obj = None,keys = None,oper = None):
    return basis_swap_isolate(obj = obj,keys = keys)
        

def basis_swap_isolate(obj = None,keys = None):
    bss = keys[0].data
    askindex = obj.active_shape_key_index
    ask = keys[askindex].data
    for v1,v2 in zip(bss,ask):
        v1.co = v2.co
    for i in range(1,len(keys)):
        obj.shape_key_remove(keys[1])
        
@defac
def determine_vertex_data_source(obj = None,target_shape_key_index = 0, use_active_shape_key = False):
    mesh = obj.data
    verts = mesh.vertices
    keys = get_keys(obj=obj)

    if use_active_shape_key == True:
        if obj.active_shape_key == None:
            obj.active_shape_key_index = 0
        choice = obj.active_shape_key.data
    elif target_shape_key_index > 0:
        choice = keys[target_shape_key_index].data
    else:
        choice = verts

    return choice

@defac
def get_keys(obj = None,basis_name = "Basis"):
    if obj.data.shape_keys == None:
        bss = obj.shape_key_add(name = basis_name)
    keys = obj.data.shape_keys.key_blocks
    return keys

@defac
def choose_verts(obj=None, type="mesh"):
    mesh = bpy.data.objects[obj.name].data.name
    verts = bpy.data.meshes[mesh].vertices
    sks = obj.data.shape_keys
    if sks == None:
        bss = obj.shape_key_add(name="Basis")
    keys = skeys.key_blocks

    if type == "basis":
        res = keys[0]
    elif type == "active":
        res = obj.active_shape_key
    else:
        res = verts

    return res

@defac
def apply_blends(group = True,
                all = True,
                blendval = 0,
                set_basis_active_key = False,
                set_active_group = False,
                obj = None):
    ct = bpy.context
    scn = ct.scene
    data = bpy.data
    objs = scn.objects
    obj = objs.active
    mods = obj.modifiers
    keys = obj.data.shape_keys.key_blocks

    #newkey = obj.shape_key_add(name = "temp",from_mix = True)
    askidx = obj.active_shape_key_index
    obj.active_shape_key_index = len(keys)
    asgidx = obj.vertex_groups.active_index

    shapevals = []
    shapenames = []
    for m in mods:
        if m.type == "ARMATURE":
            mod = m
            armshow = m.show_viewport
            if armshow == True:
                m.show_viewport = False

    for k in keys:
        shapevals.append(k.value)
        shapenames.append(k.name)
        k.value = blendval
    keys2 = keys[:][::-1]
    if not group:
        if all:
            r = range(len(keys)-1)
        else:
            r = range(askidx,askidx+1)
        for kidx in r:
            k = keys[kidx]
            val = k.value
            if set_basis_active_key:
                k.relative_key = keys[askidx]
            if k.relative_key != keys[0]:
                k.value = 1
                newkey = obj.shape_key_add(name = "temp",from_mix = True)
                for coord in range(len(newkey.data)):
                    k.data[coord].co = newkey.data[coord].co
                k.relative_key = keys[0]
            k.value = shapevals[kidx]
            obj.shape_key_remove(key = keys[len(keys) - 1])

    else:
        dupliobj = gtls.dupli_obj()
        dupliobj.data = obj.data.copy()
        duplikeys = dupliobj.data.shape_keys.key_blocks
        c=len(keys)-1
        for k in keys2:
            if set_active_group:
                k.vertex_group = obj.vertex_groups[asgidx].name
            if k.vertex_group != "":
                duplikeys[c].value = 1
                newkey = dupliobj.shape_key_add(name = "temp",from_mix = True)
                cv = 0
                for v in k.data:
                    v.co = newkey.data[cv].co
                    cv+=1
                duplikeys[c].value = 0
                k.vertex_group = ""
            c-=1
        c = 0
        for k in keys:
            k.value = shapevals[c]
            c+=1

        objs.unlink(dupliobj)
    obj.active_shape_key_index = askidx
    mod.show_viewport = armshow

@defac
def create_modified_duplicate2(apply_count = 0,obj_name = "modified",mesh_mod_clear = False,shape_apply = True,obj = None):
    ac = set_ac(obj)
    modified = obj.copy()
    if mesh_mod_clear:
        rem_types = ["MIRROR"]
        for m in modified.modifiers[:][::-1]:
            if (not m.show_viewport) or (m.type in rem_types):
                print(m)
                modified.modifiers.remove(m)
    if shape_apply:
        bpy.ops.object.shape_key_add(from_mix=True)
        for kidx,k in enumerate(modified.data.shape_keys.key_blocks[-1].data):
            modified.data.vertices[kidx].co = k.co
    modified.name = obj_name
    modmesh = modified.data.name
    modmeshdup = bpy.data.meshes[modmesh].copy()
    modified.data = modmeshdup
    modkeys = None
    try:
        modkeys = modified.data.shape_keys.key_blocks
    except:
        pass

    modmods = modified.modifiers
    bpy.context.scene.objects.link(modified)
    bpy.context.scene.objects.active = modified
    bpy.context.scene.update()
    oselect = obj.select
    modified.select = True
    obj.select = False
    bpy.context.scene.objects.active = modified

    if modkeys:
        bpy.ops.object.shape_key_remove(all=True)

    nummods = len(modmods)
    for m in range(nummods):
        '''
        #if apply_count > 0:
            #if m > apply_count:
                #break
        '''
        bpy.ops.object.modifier_apply(apply_as='DATA',modifier = modmods[0].name)
    obj.select = oselect
    set_ac(ac)
    return modified

#########################################################パーツ関連
@defac
def mesh_part_separate(obj = None,invert = False):

    parts = get_separated_parts(obj = obj)
    nobjs = tuple(gtls.dupli_obj(obj = obj) for i in parts)
    nobj_bms = tuple(get_bmesh(obj = o) for o in nobjs)

    for bmidx,bm in enumerate(nobj_bms):
        bmverts = tuple(bm.verts)
        for pidx,part in enumerate(parts):
            if cnegate(pidx == bmidx,condition = invert):
                continue
            else:
                for vidx in part:
                    bm.verts.remove(bmverts[vidx])

    for o,bm in zip(nobjs,nobj_bms):
        bm.to_mesh(o.data)
        bm.free()

    return nobjs

########################################################頂点グループつまりウェイト像関連/vertex group related
def get_vertex_weights(v):
    return tuple((g.group,g.weight) for g in v.groups)

def clear_vertex_weights(v,vgroups):
    """
    :param v: 頂点オブジェクト
    :param vgroups: 頂点グループのiterable
    :return:　無し
    """
    mvgs = (vgroups[g.group] for g in v.groups)
    for g in mvgs:
        g.remove([v.index])
    return None

@defac
def parts_to_vgroups(obj = None,parts = None,vg_name = "part_group_"):
    if parts == None:
        parts = get_separated_parts(obj = obj)
    vgroups = obj.vertex_groups
    vgs = tuple(vgroups.new(vg_name + str(p[0])) for p in enumerate(parts))
    
    for part,vg in zip(parts,vgs):
        vg.add(part,1,"ADD")
    
    return vgs


def weight_replace(weight_data,vidx,obj,do_clear):
    """
    :param weight_data: (頂点グループインデックス、ウェイト)を複数格納するiterable
    :param vidx: 頂点インデックス
    :param obj: データの対象となるオブジェクト
    :return: 無し
    """
    verts = obj.data.vertices
    vgroups = obj.vertex_groups
    v = verts[vidx]
    if do_clear:
        clear_vertex_weights(v,vgroups)
    for gidx,w in weight_data:
        vg = vgroups[gidx]
        vgname = vg.name
        side_data = check_side(vgname)
        if side_data != None:
            opposite_name = side_data[3]
            try:
                vg = vgroups[opposite_name]
            except:
                continue
        vg.add([vidx],w,"ADD")
        if not do_clear:
            vg.add([vidx], w, "REPLACE")


def weight_copy(v1, v2_idx, vgroups = None):
    """
    :param v1: 情報源となる頂点オブジェクト
    :param v2_idx: ウェイトを貰う頂点のインデックス
    :param vgs: オブジェクトの頂点グループリスト
    :return:
    """
    vgs = tuple(vgroups[g.group] for g in v1.groups)
    ws = tuple(g.weight for g in v1.groups)
    for g, w in zip(vgs, ws):
        g.add([v2_idx], w, "ADD")

@defac
def clean_vertex_groups(obj = None):
    mesh = obj.data
    verts = mesh.vertices
    edges = mesh.edges
    faces = mesh.polygons
    vgroups = obj.vertex_groups
    vgroupdict = {}
    c=0
    for v in verts:
        for g in v.groups:
            vgn = vgroups[g.group].name
            try:
                vgroupdict[vgn].append(c)
            except:
                vgroupdict.update({vgn:[c]})
        c+=1

    for g in vgroups:
        vgn = g.name
        try:
            q = (vgn,len(vgroupdict[vgn]))
        except Exception as e:
            vgroups.remove(g)

#########################################################鏡像関連/mirroring related
@defac
def find_mirror(cutoff=.001, precision = 4, scale=1, target_shape_key_index = 0, use_active_shape_key=False, prec=4, obj=None):
    mesh = obj.data
    verts = mesh.vertices
    keys = get_keys(obj = obj)

    selvertsR = []
    selvertsL = []
    mid = []

    vcodictL = {}
    vcodictR = {}

    vertsx = determine_vertex_data_source(obj=obj, target_shape_key_index=target_shape_key_index,
                                          use_active_shape_key=use_active_shape_key)

    for vidx, v in enumerate(vertsx):
        vco = roundtuple(tuple(v.co), precision = precision, scale=scale)
        absx = abs(vco[0])
        if absx < cutoff:
            mid.append(vidx)
        elif v.co[0] > 0:
            if verts[vidx].select == True:
                selvertsL.append((vco, vidx))
            try:
                vcodictL[vco].append(vidx)
            except:
                vcodictL.update({vco: [vidx]})
        elif v.co[0] < 0:
            vco = (absx,*vco[1::])
            #vco = roundtuple(tuple((abs(v.co[0]),*v.co[1::])), precision = precision, scale=scale)
            if verts[vidx].select == True:
                selvertsR.append((vco, vidx))
            try:
                vcodictR[vco].append(vidx)
            except:
                vcodictR.update({vco: [vidx]})

    return selvertsL, vcodictL, selvertsR, vcodictR, mid

@defac
def find_mirror_selected(precision=4, scale=1, target_shape_key_index = 0, use_active_shape_key=False, obj=None):
    mesh = obj.data
    verts = mesh.vertices
    keys = get_keys(obj=obj)

    vertsx = determine_vertex_data_source(obj = obj,target_shape_key_index = target_shape_key_index, use_active_shape_key=use_active_shape_key)

    coords = (v.co for v in vertsx)
    vcodict = get_rounded_vector_dict(coords, precision=precision, scale=scale)

    selstates = (v.select for v in verts)
    vrange = range(len(verts))

    selverts = tuple(compress(vrange, selstates))
    selvertsx = (vertsx[vidx] for vidx in selverts)

    m_r_coords = (roundtuple(tuple((-(v.co[0]), *v.co[1::])), precision=precision, scale=scale) for v in selvertsx)

    def vcodict_check(vco,vcodict = None,verts = None):
        try:
            matches = (verts[vidx] for vidx in vcodict[vco])
            return tmap(get_vertex_weights, matches)
        except:
            pass
        return ()


    vcodict_check2 = partial(vcodict_check,vcodict = vcodict,verts = verts)
    res = tmap(vcodict_check2, m_r_coords)

    return res, selverts

@defac
def mirror_selector(mirror_verts, mirror_dict, obj=None):
    mode = set_mode('OBJECT')
    mesh = obj.data
    verts = mesh.vertices
    errs = []
    for v in mirror_verts:
        vco, vindex = v
        try:
            for vert in mirror_dict[vco]:
                verts[vert].select = True
        except Exception as e:
            errs.append((e, vindex))
    set_mode(mode)
    return errs

@defac
def mirror_sel(vdata=None, cutoff=.001, type="both", extend=True, precision=4, scale=1, target_shape_key_index = 0, use_active_shape_key=False,
               obj=None):
    mode = set_mode('OBJECT')
    if vdata == None:
        vdata = find_mirror(cutoff = cutoff, precision = precision, scale = scale,target_shape_key_index = target_shape_key_index ,use_active_shape_key=use_active_shape_key,obj = obj)
    selvertsL, vcodictL, selvertsR, vcodictR, mid = vdata

    tdict = {"l>r": ((selvertsL, vcodictR),), "l<r": ((selvertsR, vcodictL),),
             "both": ((selvertsL, vcodictR), (selvertsR, vcodictL),)}

    if extend == False:
        deselect_mesh_parts(obj = obj)

    for vs, vdict in tdict[type]:
        mirror_selector(vs, vdict, obj=obj)

    set_mode(mode)
    return vdata

@defac
def mirror_weights(mirror_verts, mirror_dict, obj=None, vgroups=None,selected_only = True):
    mesh = bpy.data.objects[obj.name].data.name
    verts = bpy.data.meshes[mesh].vertices
    vgroups = obj.vertex_groups

    errs = []
    for v in mirror_verts:
        vco, vidx = v
        vert1 = verts[vidx]
        if selected_only:
            if not vert1.select:
                continue
        try:
            for mvidx in mirror_dict[vco]:
                mvert = verts[mvidx]
                mvgs = tuple(vgroups[g.group] for g in mvert.groups)
                for g in mvgs:
                    g.remove([mvidx])
                weight_copy(vert1, mvidx, vgroups=vgroups)
        except Exception as e:
            print(str(e))
            errs.append((e, vidx))
    return errs

@defac
def send_mirror_weights_exec(vdata=None, cutoff=.001, type="both", scale=1, target_shape_key_index=0, use_active_shape_key=False,
                             precision=4, obj=None, selected_only = True):
    mode = set_mode('OBJECT')
    if vdata == None:
        vdata = find_mirror(target_shape_key_index = target_shape_key_index ,use_active_shape_key=use_active_shape_key,obj = obj,precision=precision, scale=scale)
    selvertsL, vcodictL, selvertsR, vcodictR = vdata

    vgroups = obj.vertex_groups

    tdict = {"l>r": ((selvertsL, vcodictR),), "l<r": ((selvertsR, vcodictL),),
             "both": ((selvertsL, vcodictR), (selvertsR, vcodictL),)}
    for vs, vdict in tdict[type]:
        mirror_weights(vs, vdict, obj=obj, vgroups=vgroups, selected_only = selected_only)

    set_mode(mode)
    return vdata

@defac
def mirror_weights_exec(vdata=None, precision=4, scale=1, target_shape_key_index=0, use_active_shape_key=False,obj=None,do_clear = True,oper = None):
    locs = dict(locals())
    locs.pop("vdata")
    locs.pop("do_clear")

    mode = set_mode('OBJECT')
    if vdata == None:
        match_data, selverts = find_mirror_selected(target_shape_key_index = target_shape_key_index ,use_active_shape_key=use_active_shape_key,obj = obj,precision=precision, scale=scale)

    vgroups = obj.vertex_groups

    no_matches = []
    for vmatches, vidx in zip(match_data, selverts):
        if len(vmatches) == 0:
            no_matches.append(vidx)
            continue
        match_weight_data = vmatches[0]
        weight_replace(match_weight_data, vidx, obj, do_clear)

    rep_msg = "Found no match for " + str(len(no_matches)) + " verts"
    oper.report({"INFO"},rep_msg)

    set_mode(mode)
    return match_data, selverts, no_matches


#########################################################その他
@bm_install
@defac
def first_weld(obj=None, bm=None):
    mesh = obj.data
    verts = mesh.vertices

    parts = get_separated_parts(obj=obj)
    for p in range(1, len(parts)):
        verts[parts[p - 1][1]].co = verts[parts[p][0]].co

    return bm


def get_model_weights_dict(m1):
    vg1 = m1.vertex_groups
    v1 = objs["1"].data.vertices
    vdicts1 = [{} for v in v1]
    for v in range(len(v1)):
        vert1 = v1[v]
        grps = vert1.groups
        for g in range(len(grps)):
            g1 = vert1.groups[g]
            gr1 = g1.group
            w1 = g1.weight
            vdicts1[v].update({gr1:w1})
    
    return vdicts1

    