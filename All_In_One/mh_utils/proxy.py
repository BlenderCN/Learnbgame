# ##### BEGIN GPL LICENSE BLOCK #####
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

import bpy
import os
import math
from mathutils import Vector

from . import mh

#
#    class CRefVert
#

class CRefVert:
    
    def __init__(self, index):
        self.index = index
        
    def __repr__(self):
        return ("<CRefVert %s\n    %s\n    %s>" % (self.verts, self.weights, self.offsets))
        
    def fromSingle(self, vn):
        self.verts = (vn,vn,vn)
        self.weights = (1,0,0)
        self.offsets = Vector((0,0,0))
        return self
        
    def fromTriple(self, verts, weights, offsets):
        self.verts = verts
        self.weights = weights
        self.offsets = Vector(offsets)
        return self
        
    def update(self, srcVerts, scales):
        rv0,rv1,rv2 = self.verts
        w0,w1,w2 = self.weights
        offset = [ self.offsets[n]*scales[n] for n in range(3) ]
        return w0*srcVerts[rv0].co + w1*srcVerts[rv1].co + w2*srcVerts[rv2].co + Vector(offset)

    def updateWeight(self, srcWeights):
        rv0,rv1,rv2 = self.verts
        w0,w1,w2 = self.weights        
        return w0*srcWeights[rv0] + w1*srcWeights[rv1] + w2*srcWeights[rv2]

#
#    class CProxy
#

class CProxy:
    def __init__(self):
        self.name = None
        self.obj_file = None
        self.refVerts = {}
        self.xScale = None
        self.yScale = None
        self.zScale = None
        self.firstVert = 0
        return
        
    def __repr__(self):
        return ("<CProxy %s %d\n  %s\n  x %s  y %s  z %s>" % 
            (self.name, self.firstVert, self.obj_file, self.xScale, self.yScale, self.zScale))

        
    def checkSanity(self, trgVerts):
        rlen = len(self.refVerts)
        mlen = len(trgVerts)
        first = self.firstVert
        if (first+rlen) != mlen:
            string = "Warning: %d refVerts != %d meshVerts" % (first+rlen, mlen)
            print(string)
            #raise NameError(string)
        return rlen,first


    def update(self, srcVerts, trgVerts, skipBefore=0, skipAfter=100000):
        rlen,first = self.checkSanity(trgVerts)

        s0 = getScale(self.xScale, srcVerts, 0)
        s2 = getScale(self.yScale, srcVerts, 2)
        s1 = getScale(self.zScale, srcVerts, 1)
        scales = (s0,s1,s2)

        for n in range(rlen):
            if n < skipBefore or n >= skipAfter:
                continue
            trgVerts[n+first].co = self.refVerts[n].update(srcVerts, scales)
        return s0


    def updateWeights(self, srcWeights):
        rlen = len(self.refVerts)
        trgWeights = {}
        for n,refVert in self.refVerts.items():
            trgWeights[n] = refVert.updateWeight(srcWeights)
        return trgWeights
        

    def read(self, filepath):
        realpath = os.path.realpath(os.path.expanduser(filepath))
        folder = os.path.dirname(realpath)
        try:
            tmpl = open(filepath, "rU")
        except:
            tmpl = None
        if tmpl == None:
            print("*** Cannot open %s" % realpath)
            return None

        status = 0
        doVerts = 1
        vn = 0
        scales = Vector((1.0, 1.0, 1.0))
        for line in tmpl:
            words= line.split()
            if len(words) == 0:
                pass
            elif words[0] == '#':
                status = 0
                if len(words) == 1:
                    pass
                elif words[1] == 'verts':
                    if len(words) > 2:
                        self.firstVert = int(words[2])                    
                    status = doVerts
                elif words[1] == 'name':
                    self.name = words[2]
                elif words[1] == 'r_scale':
                    self.xScale = self.yScale = self.zScale = scaleInfo(words)
                elif words[1] == 'x_scale':
                    self.xScale = scaleInfo(words)
                elif words[1] == 'y_scale':
                    self.yScale = scaleInfo(words)
                elif words[1] == 'z_scale':
                    self.zScale = scaleInfo(words)                
                elif words[1] == 'obj_file':
                    self.obj_file = os.path.join(folder, words[2])
                else:
                    pass
            elif status == doVerts:
                if len(words) == 1:
                    v = int(words[0])
                    self.refVerts[vn] = CRefVert(vn).fromSingle(v)
                else:                
                    v0 = int(words[0])
                    v1 = int(words[1])
                    v2 = int(words[2])
                    w0 = float(words[3])
                    w1 = float(words[4])
                    w2 = float(words[5])            
                    d0 = float(words[6])
                    d1 = float(words[7])
                    d2 = float(words[8])
                    self.refVerts[vn] = CRefVert(vn).fromTriple((v0,v1,v2), (w0,w1,w2), (d0,-d2,d1))
                vn += 1
        return


def scaleInfo(words):                
    v1 = int(words[2])
    v2 = int(words[3])
    den = float(words[4])
    return (v1, v2, den)


def getScale(info, verts, index):
    if info is None:
        return 1.0
    (vn1, vn2, den) = info
    if index > 0:
        num = abs(verts[vn1].co[index] - verts[vn2].co[index])
    else:
        v1 = verts[vn1].co
        v2 = verts[vn2].co
        dx = v1[0]-v2[0]
        dy = v1[1]-v2[1]
        dz = v1[2]-v2[2]
        num = math.sqrt(dx*dx + dy*dy + dz*dz)
    return num/den
    