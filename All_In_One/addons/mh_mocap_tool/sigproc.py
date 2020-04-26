#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

#
# Implementation of the multi-resolution filtering algorithm in
#
# A. Bruderlin and L. Williams, Motion signal processing, SIGGRAPH 95 
# http://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Papers/BRUDRLIN.PDF
#


import bpy
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty, EnumProperty
from . import utils, simplify
from . import mcp
from .utils import MocapError


#
#   class CFilterData:
#

class CFilterData:
    def __init__(self):
        self.object = ""
        self.Gs = {}
        self.Ls = {}
        self.fb = 0
        self.m = 0

mcp.filterData = {}

#
#   calcFilters(context):
#

def calcFilters(context):
    rig = context.object
    scn = context.scene
    act = utils.getAction(rig)
    if not act:
        return
    (fcurves, minTime, maxTime) = simplify.getActionFCurves(act, False, False, scn)
    if not fcurves:
        return            

    try:
        fd = mcp.filterData[rig.name]
    except:
        fd = CFilterData()
        mcp.filterData[rig.name] = fd
    fd.Gs = {}
    fd.Ls = {}

    tmin = 100000
    tmax = -100000
    for fcu in fcurves:
        (points, before, after) = simplify.splitFCurvePoints(fcu, minTime, maxTime)
        pt0 = points[0]
        ptn = points[-1]
        t0 = int(pt0.co[0])
        tn = int(ptn.co[0]) 
        if t0 < tmin: tmin = t0
        if tn > tmax: tmax = tn

    m = tmax - tmin + 1
    m1 = m
    fb = 0
    while m1 > 1:
        fb += 1
        m1 = m1 >> 1
    fd.m = m    
    fd.fb = fb

    a = 3/8
    b = 1/4
    c = 1/16
    for fcu in fcurves:
        Gk = {}
        for n in range(m):
            Gk[n] = fcu.evaluate(n + t0)
        G = {}
        G[0] = Gk
        p = 1
        for k in range(fb):
            Gl = {}
            #if 2*p >= m-2*p:
            #    print("Bug %d %d" % (m,p))
            for n in range(0,m):
                np = n+p
                n2p = n+2*p
                nq = n-p
                n2q = n-2*p
                if np >= m: np = m-1                    
                if n2p >= m: n2p = m-1                    
                if nq < 0: nq = 0
                if n2q < 0: n2q = 0
                Gl[n] = a*Gk[n] + b*(Gk[nq] + Gk[np]) + c*(Gk[n2q] + Gk[n2p])
            p *= 2
            Gk = Gl
            G[k+1] = Gl

        L = {}
        Gl = G[0]
        for k in range(fb):
            Lk = {} 
            Gk = Gl
            Gl = G[k+1]
            for n in range(m):
                Lk[n] = Gk[n] - Gl[n]
            L[k] = Lk

        key = "%s_%d" % (fcu.data_path, fcu.array_index)
        fd.Gs[key] = G
        fd.Ls[key] = L

    for k in range(fb-1):
        prop = "s_%d" % k
        rig[prop] = 1.0
    return

#
#   reconstructAction(context):
#

def reconstructAction(context):
    rig = context.object
    scn = context.scene
    act = utils.getAction(rig)
    if not act:
        return
    (fcurves, minTime, maxTime) = simplify.getActionFCurves(act, False, False, scn)

    fd = mcp.filterData[rig.name]
    s = {}
    for k in range(fd.fb-1):
        s[k] = rig["s_%d" % k]

    nact = bpy.data.actions.new(act.name)
    
    for fcu in fcurves:
        path = fcu.data_path
        index = fcu.array_index
        grp = fcu.group.name
        key = "%s_%d" % (path, index)
        G = fd.Gs[key]
        L = fd.Ls[key]

        Gk = G[fd.fb]
        x = {}
        for n in range(fd.m):
            x[n] = Gk[n]
        for k in range(fd.fb-1):
            sk = s[k]
            Lk = L[k]    
            for n in range(fd.m):
                x[n] += sk*Lk[n]

        nfcu = nact.fcurves.new(path, index, grp)
        for n in range(fd.m):
            nfcu.keyframe_points.insert(frame=n, value=x[n])

    rig.animation_data.action = nact
    utils.setInterpolation(rig)
    return


########################################################################
#
#   Buttons
#

class VIEW3D_OT_CalcFiltersButton(bpy.types.Operator):
    bl_idname = "mcp.calc_filters"
    bl_label = "Calculate Filters"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            calcFilters(context)
            print("Filters calculated")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    


class VIEW3D_OT_DiscardFiltersButton(bpy.types.Operator):
    bl_idname = "mcp.discard_filters"
    bl_label = "Discard Filters"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        try:
            del mcp.filterData[rig.name]
        except:
            pass
        return{'FINISHED'}    


class VIEW3D_OT_ReconstructActionButton(bpy.types.Operator):
    bl_idname = "mcp.reconstruct_action"
    bl_label = "Reconstruct Action"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            reconstructAction(context)
            print("F-curves reconstructed")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    

