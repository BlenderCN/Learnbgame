# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls
from g_tools.gtls import defac,defac2,moderate,set_ac,set_mode

@moderate("OBJECT")
@defac
def set_lattice_resolution(reso,obj = None):
    obj.data.points_u,obj.data.points_v,obj.data.points_w = reso
    return (reso,obj)