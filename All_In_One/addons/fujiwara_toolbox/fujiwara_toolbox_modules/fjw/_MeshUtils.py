import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import subprocess
import shutil
import time
import copy
import random
from collections import OrderedDict
from mathutils import *

from .main import *


class MeshUtils():
    def __init__(self, obj):
        if obj.type != "MESH":
            return None

        self.object = obj
        self.vertices = obj.data.vertices

    def deselect(self):
        activate(self.object)
        mode("EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

    def selectall(self):
        activate(self.object)
        mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')


    def bmesh(self):
        data = self.object.data
        bm = bmesh.from_edit_mesh(data)
        return bm

    def update(self):
        bmesh.update_edit_mesh(self.object.data)

    def tolocal_cordinate(self, loc):
        return self.object.matrix_world.inverted() * loc

    def toworld_cordinate(self, loc):
        return self.object.matrix_world * self.object.matrix_basis.inverted() * loc

    def select_byaxis(self, axis="+X", world=False, basepoint=(0,0,0)):
        activate(self.object)
        mode("EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

        axs = 0
        direction = 1
        
        if "x" in axis or "X" in axis :
            axs = 0
        if "y" in axis or "Y" in axis :
            axs = 1
        if "z" in axis or "Z" in axis :
            axs = 2

        if "+" in axis:
            direction = 1
        if "-" in axis:
            direction = -1

        data = self.object.data
        bm = self.bmesh()
        bm.faces.active = None

        #選択リフレッシュ
        for v  in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False

        for face in bm.faces:
            for v in face.verts:
                co = v.co
                if world:
                    co = self.toworld_cordinate(co)
                if(co[axs] * direction < basepoint[axs]):
                    face.select = True
                    selectflag = True
                    continue
        for edge in bm.edges:
            for v in edge.verts:
                co = v.co
                if world:
                    co = self.toworld_cordinate(co)
                if(co[axs] * direction < basepoint[axs]):
                    edge.select = True
                    selectflag = True
                    continue
        for v in bm.verts:
                co = v.co
                if world:
                    co = self.toworld_cordinate(co)
                if(co[axs] * direction < basepoint[axs]):
                    v.select = True
                    selectflag = True
                    continue
        self.update()
        mode("OBJECT")
        
    def delete(self, deltype="FACE"):
        mode("EDIT")
        bpy.ops.mesh.delete(type=deltype)
        mode("OBJECT")
    def duplicate(self):
        mode("EDIT")
        bpy.ops.mesh.duplicate()
        mode("OBJECT")
    def separete(self):
        mode("EDIT")
        bpy.ops.mesh.separate(type='SELECTED')
        mode("OBJECT")
    def remove_doubles(self):
        mode("EDIT")
        bpy.ops.mesh.remove_doubles()
        mode("OBJECT")

class BmeshUtils():
    def __init__(self, obj):
        activate(obj)
        mode("EDIT")
        self.data = obj.data
        self.bm = bmesh.from_edit_mesh(obj.data)
    
    def select_all(self):
        for v in self.bm.verts:
            v.select = True
        for e in self.bm.edges:
            e.select = True
        for f in self.bm.faces:
            f.select = True
        self.bm.select_flush(True)

    def deselect_all(self):
        for v in self.bm.verts:
            v.select = False
        for e in self.bm.edges:
            e.select = False
        for f in self.bm.faces:
            f.select = False
        self.bm.select_flush(True)

    def select_flush(self):
        self.bm.select_flush(True)

    def update(self):
        bmesh.update_edit_mesh(self.data)