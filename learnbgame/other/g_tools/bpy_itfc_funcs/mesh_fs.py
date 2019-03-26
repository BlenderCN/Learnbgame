# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls

def get_bmesh(obj = None):
    mesh = bpy.data.objects[obj.name].data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    return bm
    