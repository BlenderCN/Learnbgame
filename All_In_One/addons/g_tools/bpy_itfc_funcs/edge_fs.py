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

#########################################################bmesh関連
#requires bmesh vertex
#returns first selected bmedge extending from vertex
#頂点の接続エッジリストを参照して、一番最初に当たる選択中のエッジを戻す
def first_sel_edge(vert):
    for edge in vert.link_edges:
        if edge.select == True:
            return edge


def get_next_edge(vert,current_edge,sel_only):
    for edge in vert.link_edges:
            if edge != current_edge:
                if sel_only:
                    if not edge.select:
                        continue
                return edge

#takes BMVERTS
def run_edge_length(bmvert,endverts,sel_only = False):
    lastvert = bmvert
    startedge = first_sel_edge(bmvert)

    nextedge = startedge
    connectedverts = []
    nextvert = lastvert
    linked = True
    while linked:
        lastvert = nextvert
        connectedverts.append(lastvert)
        nextvert = nextedge.other_vert(nextvert)
        if nextvert in endverts:
            connectedverts.append(nextvert)
            linked = False
        nextedge = get_next_edge(nextvert,nextedge,sel_only)
        if not nextedge:
            break
    return connectedverts