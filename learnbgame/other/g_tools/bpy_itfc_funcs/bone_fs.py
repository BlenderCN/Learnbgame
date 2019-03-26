# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls
from g_tools.gtls import defac,set_mode,set_ac,moderate
from mathutils import Vector,Euler,Quaternion,Matrix

#constants
INIT_BONE_PROPS = {"head":Vector((0,0,0)),"tail":Vector((0,1,0)),"roll":0}


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
    
    if parent:
        newbone.parent = parent
        
    prop_copy(newbone,props)
    set_mode(mode)
    set_ac(ac)
    return newbone

    
@defac
@moderate("EDIT")
def editbone_adjuster(obj = None,trans = (0,0,0),trans_head = (0,0,0),trans_tail = (0,0,0),roll = 0,envelope_distance = 0,head_radius = 0,tail_radius = 0,target_bone = ""):
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
    return original_data
    
def editbone_adjust(obj = None,trans = (0,0,0),trans_head = (0,0,0),trans_tail = (0,0,0),roll = 0,target_bone = "",envelope_distance = 0,head_radius = 0,tail_radius = 0,):
    props = "head,tail,roll,envelope_distance,head_radius,tail_radius".split(",")
    trans = Vector((trans))
    trans_head = Vector((trans_head))
    trans_tail = Vector((trans_tail))
    target_bone = target_bone
    editbone_adjuster(obj = obj,trans = trans,trans_head = trans_head, trans_tail = trans_tail,roll = roll,target_bone = target_bone,envelope_distance = envelope_distance,tail_radius = tail_radius,head_radius = head_radius,)
    