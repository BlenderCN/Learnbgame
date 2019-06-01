# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls
from g_tools.gtls import defac,get_ac,set_ac,set_mode,moderate
from mathutils import Vector,Euler,Quaternion,Matrix

#constants
INIT_BONE_PROPS = {"head":Vector((0,0,0)),"tail":Vector((0,1,0)),"roll":0}


#########################################################ボーン選択・フィルタリング/bone selection and filtering
@defac
def get_active_bone(obj = None):
    return obj.data.bones.active
    
@defac
def get_pactbone(obj = None):
    return obj.pose.bones[get_active_bone(obj = obj).name]
    
@defac
def get_sel_bones(obj = None):
    bones = obj.data.bones
    return tuple(b for b in bones if b.select)

@defac
def get_sel_bone(obj = None):
    bones  = obj.data.bones
    actbone = bones.active
    return tuple(b for b in get_sel_bones(obj = obj) if b.name != get_active_bone(obj = obj).name)

@defac
def filter_bones_by_tag(bnlist,target_parent = 3,tag = r"親",is_indexed = True,count_relevant = 0,obj = None):
    targets = []
    if is_indexed:
        rgxer = r"(" + tag + r"\d+)"
    else:
        rgxer = "(" + tag + ")"
    for i in range(len(bnlist)):
        b = bnlist[i]
        if not (len(b.name) > 2):
            continue
        if re.search(rgxer,b.name[(len(tag)+int(is_indexed))+count_relevant::]):
            targets.append(b)
    return targets

@defac
def gather_by_tag(target_parent = -1,tag = r"親",is_indexed = True,count_relevant = 0,obj = None):
    """
    ボーン名の最後に付いてるタグによってボーンを選択する
    """
    targets = []
    bones = obj.data.bones
    bnlist = tuple(b.name for b in bones)
    if is_indexed:
        rgxer = r"(" + tag + r"\d+)"
    else:
        rgxer = "(" + tag + ")"
    for i in range(len(bnlist)):
        bname = bnlist[i]
        if not (len(bname) > 2):
            continue
        index_in_name = -(len(tag)+int(is_indexed)+count_relevant)
        if re.search(rgxer,bname[index_in_name::]):
            targets.append(bname)
    return targets
    
@defac
def select_by_tag(target_parent = -1,tag = r"親",is_indexed = True,count_relevant = 0,obj = None):
    locs = dict(locals())
    targets = gather_by_tag(**locs)

    print(targets)

    bones = obj.data.bones
    for b in targets:
        bones[b].select = True
        
    return targets
    
#########################################################ボーンの作成など/bone making
def init_new_bone(ebones):
    newbone = ebones.new(name = "temp")
    newbone.head = Vector((0,0,0))
    newbone.tail = Vector((0,1,0))
    newbone.roll = 0
    return newbone
    
@defac
def make_bone(name = "Bone",obj = None,autoswitch = True,loc = None,dir = None,scale = .05,parent = None,props = {}):
    if loc == None:
        loc = (0,0,0)
    if dir == None:
        dir = (0,1,0)
    if autoswitch:
        ac = set_ac(obj)
        mode = set_mode("EDIT")
        
    ebones = obj.data.edit_bones
    newbone = init_new_bone(ebones)
    newbone.name = name
    
    newbone.head = loc
    newbone.tail = Vector(loc) + Vector(dir)*scale
    
    if parent != None:
        newbone.parent = parent
        
    prop_copy(newbone,props)
    if autoswitch:
        set_mode(mode)
        set_ac(ac)
    return newbone

@moderate("EDIT")    
@defac
def set_root(obj = None,bname = ""):
    if bname == "":
        bones = obj.data.bones
        bname = bones.active.name
    ebones = obj.data.edit_bones
    root = ebones[bname]
    root.parent = None
    for bn in ebones:
        if bn.parent == None:
            bn.parent = root
    
    
@moderate("EDIT")    
@defac
def make_root(obj = None,name = "全ての親"):
    root = make_bone(name = name)
    set_root(obj = obj,bname = root.name)
    return root
    
#########################################################ボーンのプロパティー変更/bone property changing
@defac
def set_minimum_envelopes(obj = None):
    ac = set_ac(obj)
    mode = set_mode("EDIT")
    for b in obj.data.edit_bones:
        b.envelope_distance = 0
        b.head_radius = .0001
        b.tail_radius = .0001
    set_mode(mode)
    set_ac(ac)

def bone_exists(bname,bones):
    try:
        b = bones[bname]
    except:
        return 0
    return 1

@defac
def ordered_bone_parent(bone_names,obj = None):
    ac = set_ac(obj)
    mode = set_mode("EDIT")
    ebones = obj.data.edit_bones
    if bone_names[0] != None:
        ebones[bone_names[1]].parent = ebones[bone_names[0]]
    if len(bone_names) > 2:
        for b in range(2,len(bone_names)):
            bname,parent_name = (bone_names[b],bone_names[b-1])
            ebones[bname].parent = ebones[parent_name]
            
    set_mode(mode)
    set_ac(ac)
    
    
    
@defac
@moderate("EDIT")
def editbone_adjuster(obj = None,trans = (0,0,0),trans_head = (0,0,0),trans_tail = (0,0,0),roll = 0,envelope_distance = 0,envelope_weight = 1,head_radius = 0,tail_radius = 0,target_bone = "",selected_only = False):
    bones = obj.data.bones
    ebones = obj.data.edit_bones
    if target_bone == "":
        target_bone = bones.active.name
    eactbn = ebones[target_bone]
    original_data = (eactbn.head.copy(),eactbn.tail.copy(),eactbn.roll)
    eactbn.head += trans_head + trans
    eactbn.tail += trans_tail + trans
    eactbn.roll += roll
    eactbn.head_radius += head_radius
    eactbn.tail_radius += tail_radius
    eactbn.envelope_distance += envelope_distance
    eactbn.envelope_weight += envelope_weight
    return original_data
    
def editbone_adjust(obj = None,trans = (0,0,0),trans_head = (0,0,0),trans_tail = (0,0,0),roll = 0,target_bone = "",envelope_distance = 0,envelope_weight = 1,head_radius = 0,tail_radius = 0,selected_only = False):
    props = "head,tail,roll,envelope_distance,head_radius,tail_radius".split(",")
    trans = Vector((trans))
    trans_head = Vector((trans_head))
    trans_tail = Vector((trans_tail))
    target_bone = target_bone
    editbone_adjuster(obj = obj,trans = trans,trans_head = trans_head, trans_tail = trans_tail,roll = roll,target_bone = target_bone,envelope_distance = envelope_distance,envelope_weight = envelope_weight,tail_radius = tail_radius,head_radius = head_radius,selected_only = selected_only)
    
@defac
def bone_trans(matrix,obj = None,bone_names = None,scale = .5):
    ac = set_ac(obj)
    mode = set_mode("EDIT")
    ebones = obj.data.edit_bones
    if bone_names:
        target_bones = tuple(ebones[bn] for bn in bone_names)
    else:
        target_bones = tuple(ebones)
    m3 = matrix.to_3x3()
    mt = matrix.to_translation()
    anymap(lambda b: b.head.rotate(matrix),target_bones)
    anymap(lambda b: b.tail.rotate(matrix),target_bones)
    anymap(lambda b: setattr(b,"head",mt+b.head),target_bones)
    anymap(lambda b: setattr(b,"tail",Vector((0,1,0))*scale+b.head),target_bones)
    set_mode(mode)
    set_ac(ac)
