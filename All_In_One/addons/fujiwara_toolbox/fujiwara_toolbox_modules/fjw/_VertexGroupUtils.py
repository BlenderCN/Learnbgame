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



class VertexGroupUtils():
    #https://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-from-python
    def __init__(self, obj):
        self.obj = obj
        activate(obj)
        mode("OBJECT")
        pass

    def select_allverts(self):
        bpy.ops.mesh.select_all(action='SELECT')

    def get_group(self,name):
        if name not in self.obj.vertex_groups:
            vg = self.obj.vertex_groups.new(name)
        else:
            vg = self.obj.vertex_groups[name]

        return vg

    def get_vertices(self):
        return self.obj.data.vertices

    def set_weight(self,index,group_name, weight):
        vg = self.get_group(group_name)
        vg.add([index],weight,"REPLACE")

    #追加分
    def has_vertex_group(self):
        vg_index = self.obj.vertex_groups.find("Shrinkwrap")
        if vg_index == -1:
            return False
        return True

    def set_active_group(self, name):
        if name in self.obj.vertex_groups:
            vg = self.obj.vertex_groups[name]
        else:
            vg = self.obj.vertex_groups.new(name=name)
        vgi = self.obj.vertex_groups.find(name)
        #これだと設定できない　インデックスでやるべき
        # self.obj.vertex_groups.active = vg
        self.obj.vertex_groups.active_index = vgi

    def assign_weight(self, name, weight):
        self.set_active_group(name)
        bpy.context.scene.tool_settings.vertex_group_weight = weight
        bpy.ops.object.vertex_group_assign()

    def select_mesh(self, name):
        #頂点グループで選択する
        if name not in self.obj.vertex_groups:
            return False
        vg = self.obj.vertex_groups[name]
        self.obj.vertex_groups.active = vg
        bpy.ops.object.vertex_group_select()
        return True

