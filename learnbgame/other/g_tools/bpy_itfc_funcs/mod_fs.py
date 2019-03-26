# -*- coding: utf-8 -*-
import bpy
from .. import gtls
from g_tools.gtls import defac,defac2,set_mode,set_ac
from g_tools.nbf import *

@defac
def make_point_arm_mod(name,obj = None,sobj = None):
    mod = make_mod(name,"ARMATURE",obj = obj,)
    props = {"use_vertex_groups":False,"use_bone_envelopes":True,"object":sobj,"show_in_editmode":True,"use_apply_on_spline":True}
    prop_copy(mod,props)
    return mod
    
@defac
def make_mod(name,type,obj = None):
    return obj.modifiers.new(name = name,type = type)
    