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

import bpy
from math import pi
from mathutils import *

try:
    bpy.usingMakeHuman
    usingMakeHuman = True
except:
    usingMakeHuman = False
    
if usingMakeHuman:

    import log
    from log import message, debug

else:    
    def message(string):
        print(string)

    def debug(string):
        print(string)
    

nodes = {}
data = {}
takes = {}
root = None
idnum = 1000
idstruct = {}
allNodes = {}

templates = {}


#------------------------------------------------------------------
#   Coordinate system conversion
#   The FBX file always uses the Y up convention.
#   
#------------------------------------------------------------------


def b2fZup(vec):
    global settings
    return settings.scale * Vector((vec[0], vec[2], -vec[1]))

def f2bZup(vec):
    global settings
    return settings.scale * Vector((vec[0], -vec[2], vec[1]))
    
def b2fEulerZup(eu):
    return Vector((eu[0], eu[2], -eu[1]))

def f2bEulerZup(eu):
    return Vector((eu[0], -eu[2], eu[1]))
    
def b2fRot4Zup(mat):
    return b2fGlobRot * mat
    
def f2bRot4Zup(mat):
    return f2bGlobRot * mat
    return mat
    
  
def b2fYup(vec):
    global settings
    return settings.scale * Vector(vec)

def f2bYup(vec):
    global settings
    return settings.scale * Vector(vec)

def b2fEulerYup(eu):
    return eu

def f2bEulerYup(eu):
    return eu

def b2fRot4Yup(mat):
    return mat
    
def f2bRot4Yup(mat):
    return mat


# string : (fIndex, bIndex, factor)

BTransIndexZup = {
    "d|X" : (0, 0, 1),
    "d|Y" : (1, 2, -1),
    "d|Z" : (2, 1, 1),
}

BRotIndexZup = {
    "d|X" : (0, 0, 1),
    "d|Y" : (1, 2, -1),
    "d|Z" : (2, 1, 1),
}

# bIndex : (string, fIndex, factor)

FRotChannelZup = {
    0 : ("d|X", 0, 1),
    1 : ("d|Z", 2, 1),
    2 : ("d|Y", 1, -1),
}

FTransChannelZup = {
    0 : ("d|X", 0, 1),
    1 : ("d|Z", 2, 1),
    2 : ("d|Y", 1, -1),
}

BTransIndexYup = {
    "d|X" : (0, 0, 1),
    "d|Y" : (1, 1, 1),
    "d|Z" : (2, 2, 1),
}

BRotIndexYup = {
    "d|X" : (0, 0, 1),
    "d|Y" : (1, 1, 1),
    "d|Z" : (2, 2, 1),
}

FRotChannelYup = {
    0 : ("d|X", 0, 1),
    1 : ("d|Y", 1, 1),
    2 : ("d|Z", 2, 1),
}

FTransChannelYup = {
    0 : ("d|X", 0, 1),
    1 : ("d|Y", 1, 1),
    2 : ("d|Z", 2, 1),
}


def setCsysChangers():
    global b2f, f2b, b2fEuler, f2bEuler, b2fRot4, f2bRot4 
    global f2bGlobRot, b2fGlobRot
    global BTransIndex, BRotIndex, FRotChannel, FTransChannel
   
    if settings.zUp:
        message("Coordinate system Z up")
        f2bGlobRot = Matrix.Rotation(pi/2, 4, 'X')
        b2fGlobRot = Matrix.Rotation(-pi/2, 4, 'X')

        b2f = b2fZup
        f2b = f2bZup
        b2fEuler = b2fEulerZup
        f2bEuler = f2bEulerZup
        b2fRot4 = b2fRot4Zup
        f2bRot4 = f2bRot4Zup
        
        BTransIndex = BTransIndexZup
        BRotIndex = BRotIndexZup
        FRotChannel = FRotChannelZup
        FTransChannel = FTransChannelZup
        
    else:
        message("Coordinate system Y up")
        b2f = b2fYup
        f2b = f2bYup
        b2fEuler = b2fEulerYup
        f2bEuler = f2bEulerYup
        b2fRot4 = b2fRot4Yup
        f2bRot4 = f2bRot4Yup

        BTransIndex = BTransIndexYup
        BRotIndex = BRotIndexYup
        FRotChannel = FRotChannelYup
        FTransChannel = FTransChannelYup
        

#------------------------------------------------------------------
#   Settings
#------------------------------------------------------------------


class Settings:
    def __init__(self):
        self.createNewScene = False
        self.writeAllNodes = True
        self.includePropertyTemplates = True
        self.makeSceneNode = False
        self.selectedOnly = True
        self.lockChildren = True
        self.zUp = False
        self.normals = False    
        self.scale = 1.0
        self.encoding = 'utf-8'
    
    def maya(self):
        self.zUp = False
        self.boneAxis = 0
        self.minBoneLength = 1.0
        self.mirrorFix = False
        self.useIkEffectors = True
        setCsysChangers()
       
    def maya2Blender(self):
        self.zUp = True
        self.boneAxis = 0
        self.minBoneLength = 1.0
        self.mirrorFix = True
        self.useIkEffectors = True
        setCsysChangers()
       
    def blender(self):
        self.zUp = True
        self.boneAxis = 1
        self.minBoneLength = 1.0
        self.mirrorFix = False
        self.useIkEffectors = False
        setCsysChangers()
              
            
settings = Settings()
setCsysChangers()
settings.maya()



