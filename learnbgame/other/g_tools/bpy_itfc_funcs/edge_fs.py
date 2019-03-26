# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from . import gtls
from g_tools.gtls import defac,defac2,moderate,set_ac,set_mode

@defac
def get_selected_edge_vec(obj = None):
    edges = obj.data.edges
    s_edge = andmap(lambda e: e.select,edges)
    return get_edge_vec(e)