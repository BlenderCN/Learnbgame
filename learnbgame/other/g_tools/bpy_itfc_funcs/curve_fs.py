# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from . import armature_fs
from . import bone_fs
from . import mod_fs
from .. import gtls
from g_tools.gtls import defac

@defac
def curve_to_armature(obj = None,arm = None,set_bone_envelopes = True,create_mod = True,bone_scale = .5):
    if arm == None:
        arm = gtls.make_obj(type = "ARMATURE",name = "arm_to_curve_" + obj.name)
    
    splines = tuple(s.bezier_points if s.type == "BEZIER" else s.points for s in obj.data.splines)
    res = tuple(map(lambda verts: tuple(map(lambda v: bone_fs.make_bone(scale = bone_scale,obj = arm,loc = v.co[0:3]),verts)),splines))
    
    if create_mod:
        mod = mod_fs.make_point_arm_mod("Curve_to_Armature",obj = obj,sobj = arm)
   
    if set_bone_envelopes:
        bone_fs.set_minimum_envelopes(obj = arm)
        
    return arm