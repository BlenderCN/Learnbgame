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

"""
Abstract

The MakeHuman application uses predefined morph target files to distort
the humanoid model when physiological changes or changes to the pose are
applied by the user. The morph target files contain extreme mesh
deformations for individual joints and features which can used
proportionately to apply less extreme deformations and which can be
combined to provide a very wide range of options to the user of the
application.

This module contains a set of functions used by 3d artists during the
development cycle to create these extreme morph target files from
hand-crafted models.

"""

import bpy
import os
import mathutils
import math
from bpy.props import *

from . import mh
from . import utils

numpy = utils.getNumpy("Warping")
    
#----------------------------------------------------------
#   class CWarp
#----------------------------------------------------------

class CWarp:
    def __init__(self, context):
        self.name = "undefined"
        self.n = 0
        self.x = {}
        self.y = {}
        self.w = {}       
        self.H = None
        self.s2 = {}
        self.lamb = 0
        self.zMin = 1e6
        scn = context.scene
        self.stiffness = scn.MhStiffness
            
        
    def setup(self, xverts, yverts):
        self.n = len(xverts)
        n = self.n
        
        for i in range(n):
            self.x[i] = xverts[i].copy()
            
        for k in range(3):
            self.w[k] = numpy.arange(n, dtype=float)
            for i in range(n):
                self.w[k][i] = 0.1

            self.y[k] = numpy.arange(n, dtype=float)
            for i in range(n):
                self.y[k][i] = yverts[i][k]

        for i in range(n):
            mindist = 1e6
            vxi = xverts[i]
            for j in range(n):
                if i != j:
                    vec = vxi - xverts[j]
                    if vec.length < mindist:                        
                        mindist = vec.length
                        if mindist < 1e-3:
                            print("  ", mindist, i, j)
            self.s2[i] = (mindist*mindist)

        self.H = numpy.identity(n, float)
        for i in range(n):
            xi = xverts[i]
            for j in range(n):
                self.H[i][j] = self.rbf(j, xi)
        
        self.HT = self.H.transpose()
        self.HTH = numpy.dot(self.HT, self.H)    
        print("Warp set up: %d points" % n)

        self.solve(0)
        self.solve(1)
        self.solve(2)
        return
    
        uc,zc = numpy.linalg.eig(HH)
        self.u = uc.real
        self.z = zc.real
        return
    
    
    def setupFromObject(self, mask, context):
        self.name = mask.name
        self.n = len(mask.data.vertices)
        xverts = {}
        for v in mask.data.vertices:
            xverts[v.index] = v.co.copy()
        yverts = self.getShapeSumVerts(mask)

        for i in range(self.n):
            if yverts[i][2] < self.zMin:
                self.zMin = yverts[i][2]

        self.setup(xverts, yverts)
        return
        
        
    def setupFromCharacters(self, context, srcChar, trgChar):
        srcChar.readVerts(context)
        trgChar.readVerts(context)
        self.setup(srcChar.landmarkVerts, trgChar.landmarkVerts)
        
        
    def getShapeSumVerts(self, ob):
        verts = {}
        basis = ob.data.shape_keys.key_blocks[0]
        nverts = len(ob.data.vertices)
        for n in range(nverts):
            verts[n] = basis.data[n].co.copy()
        for skey in ob.data.shape_keys.key_blocks[1:]:
            for v in ob.data.vertices:
                vn = v.index
                verts[vn] += skey.data[vn].co - v.co
        return verts


    def solve(self, index):        
        A = self.HTH + self.lamb * numpy.identity(self.n, float) 
        b = numpy.dot(self.HT, self.y[index])
        self.w[index] = numpy.linalg.solve(A, b)
        e = self.y[index] - numpy.dot(self.H, self.w[index])
        ee = numpy.dot(e.transpose(), e)
        print("Solved for index %d: Error %g" % (index, math.sqrt(ee)))
        #print(self.w[index])
        return

        """
        eta = 0
        ee = 0
        wAw = 0
        ngamma = 0
        for i in range(self.n):
            ui = self.u[i]
            zi = self.z[i]
            zi2 = numpy.dot(zi.transpose(),zi)
            uil = ui + self.lamb
            eta += ui/(uil*uil)
            ee += self.lamb*self.lamb*zi2/(uil*uil)
            wAw += ui*zi2/(uil*uil*uil)
            ngamma += self.lamb/uil
        gcv = self.n*ee/(ngamma*ngamma)
        self.lamb = eta/ngamma * ee/wAw
        print("GCV", gcv, "Lambda", self.lamb)            
        
        return gcv
        """
        
    def rbf(self, vn, x):
        vec = x - self.x[vn]
        vec2 = vec.dot(vec)
        return math.sqrt(vec2 + self.s2[vn])
        r = math.sqrt(vec2)
        return math.exp(-self.stiffness*r)
        
        
    def warpLoc(self, x):
        y = mathutils.Vector((0,0,0))
        f = {}        
        for i in range(self.n):
            f[i] = self.rbf(i, x)
        for k in range(3):
            w = self.w[k]
            for i in range(self.n):
                y[k] += w[i]*f[i]
            """                
            for k in range(3):
                y[k] += w[self.n+k]*x[k]
            y[k] += w[self.n+3]
            """
        return y    
        
        
    def warpLocations(self, xlocs):
        ylocs = {}
        for n in xlocs.keys():
            ylocs[n] = self.warpLoc(xlocs[n])
        return ylocs
        
        
    def warpMesh(self, mask, base):
        xverts = self.getShapeSumVerts(base)
        skey = base.shape_key_add(name=self.name, from_mix=False) 
        blocks = base.data.shape_keys.key_blocks
        nKeys = len(blocks)
        base.active_shape_key_index = nKeys-1
        skey.value = 1.0
        basis = blocks[0]
        n = len(base.data.vertices)
        nwarped = 0
        for i in range(n):
            if i%1000 == 0:
                print(i)
            x = xverts[i]
            if x[2] > self.zMin:
                x0 = basis.data[i].co
                xest = self.warpLoc(x0)
                skey.data[i].co = xest - x + x0
                nwarped += 1
        print("%d vertices warped" % nwarped)                
           

def readLandMarks(context, verts):       
    scn = context.scene
    enum = scn.MhLandmarks
    file = enum.lower() + ".lmk"
    path = os.path.join( scn.MhProgramPath, "data/landmarks", file)
    print("Load", path)
    landmarks = {}
    locs = {}
    n = 0
    fp = open(path, "r")
    for line in fp:
        words = line.split()    
        if len(words) > 0:
            m = int(words[0])
            landmarks[n] = m
            locs[n] = verts[m]
            n += 1
    fp.close()
    print("   ...done")       
    return (landmarks, locs)
    
    
def updateLandmarks(context):
    scn = context.scene
    enums = []
    path = os.path.join( scn.MhProgramPath, "data/landmarks")
    for file in os.listdir(path):
        (fname, ext) = os.path.splitext(file)
        if ext == ".lmk":
            name = fname.capitalize()
            enums.append((name,name,name))

    if not enums:
        print("No enums found")
        return
        
    default= scn.MhLandmarks            
    bpy.types.Scene.MhLandmarks = EnumProperty(
        items = enums,
        name = "Landmarks",
        default = scn.MhLandmarks)
    print("Landmarks updated")        
        
        
def init():
    bpy.types.Scene.MhLandmarks = EnumProperty(
        items = [('Body', 'Body', 'Body'), ('Face', 'Face', 'Face')],
        name = "Landmarks",
        default = 'Face')
        
    bpy.types.Scene.MhStiffness = FloatProperty(
        name="Stiffness",
        default = 0.06)

    bpy.types.Scene.MhLambda = FloatProperty(
        name="Lambda",
        default = 0.0)

    bpy.types.Scene.MhIterations = IntProperty(
        name="Iterations",
        default = 1)
        

       
        