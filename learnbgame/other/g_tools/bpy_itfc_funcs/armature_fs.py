# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls
from . import bone_fs
from g_tools.gtls import defac,set_mode,set_ac,moderate

@defac
def envelope_armature_settings(env_dist = .25,head_radius = 0,tail_radius = 0,obj = None):
    prop_dict = kwargize(head_radius = head_radius,tail_radius = tail_radius,envelope_distance = env_dist)
    ac = set_ac(obj)
    mode = set_mode("EDIT")
    ebones = obj.data.edit_bones
    tmap(lambda b: prop_copy(b,prop_dict),ebones)
    set_mode(mode)
    set_ac(ac)