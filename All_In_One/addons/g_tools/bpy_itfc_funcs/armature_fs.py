# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls
from . import bone_fs
from g_tools.gtls import defac,get_ac,set_ac,set_mode,moderate


@moderate("EDIT")    
@defac
def lowerize_bone_names(obj = None):
    ebones = obj.data.edit_bones
    orig_names = tuple(e.name for e in ebones)
    passmap(lambda b: setattrate(b,name=b.name.lower()),ebones)
    return orig_names
    
@defac
def symmetrize_armature(obj = None,cutoff = .001,scale = .5):
    ac = set_ac(obj)
    mode = set_mode("EDIT")
    ebones = obj.data.edit_bones
    bones = obj
    
    
    xcos = tuple(b.head[0] for b in ebones)    
    l = tuple(ebones[i] for i in get_side(coords = xcos))
    r = tuple(ebones[i] for i in get_side(coords = xcos,cmp_func = lambda x,y: x<y))
    
    n_r = mirror_arm_side(bones = l,side_tag = "_R",scale = scale)
    n_l = mirror_arm_side(bones = r,side_tag = "_L",scale = scale)
    
    for b in r:
        b.name += "_R"
    for b in l:
        b.name += "_L"
    
    res_r = (tuple(b.name for b in r),tuple(b.name for b in n_r))
    res_l = (tuple(b.name for b in l),tuple(b.name for b in n_l))
    
    set_mode(mode)
    set_ac(ac)
    
    return res_r,res_l

@defac
def envelope_armature_settings(envelope_distance = .25,envelope_weight = 1.0,head_radius = 0,tail_radius = 0,obj = None):
    prop_dict = kwargize(head_radius = head_radius,tail_radius = tail_radius,envelope_distance = envelope_distance,envelope_weight = envelope_weight)
    ac = set_ac(obj)
    mode = set_mode("EDIT")
    ebones = obj.data.edit_bones
    tmap(lambda b: prop_copy(b,prop_dict),ebones)
    set_mode(mode)
    set_ac(ac)