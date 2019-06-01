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

class ArmatureUtils():
    def create(self, name, loc):
        bpy.ops.object.armature_add(view_align=False, enter_editmode=False, location=loc, layers=bpy.context.scene.layers)
        obj = active()
        obj.name = name
        self.armature = obj
        self.clear_bones()
        return obj
    
    def __init__(self, obj=None, name=None, loc=(0,0,0)):
        if obj == None:
            # 新規作成
            obj = self.create(name, loc)

        if obj.type != "ARMATURE":
            return None

        self.armature = obj
        self.pose_bones = self.armature.pose.bones
        self.data_bones = self.armature.data.bones
        self.edit_bones = self.armature.data.edit_bones
    
    @property
    def is_proxy(self):
        if self.armature.proxy is None:
            return False
        else:
            return True

    def findname(self, name):#該当するボーンの名前を返す
        for bone in self.armature.data.bones:
            if name in bone.name:
                return bone.name
        return None

    def is_selected(self, bone):
        databone = self.databone(bone.name)
        return databone.select

    def posebone(self, name):#名前のポーズボーンを返す
        return self.armature.pose.bones[name]
    def databone(self, name):
        return self.armature.data.bones[name]
    def editbone(self, name):
        return self.armature.data.edit_bones[name]

    def get_pbone_world_co(self, co):#ボーンのワールド座標を返す
        # loc = self.armature.matrix_world * self.armature.matrix_basis.inverted() * co
        loc = self.armature.matrix_world * co
        return loc

    # def world_to_local_co(self, co):
    #     return

    def dataactive(self):
        return self.armature.data.bones.active

    def poseactive(self):#アクティブボーンを返す
        return self.posebone(self.dataactive().name)

    def activate(self,bone):#アクティブボーンを設定する
        self.armature.data.bones.active = self.armature.data.bones[bone.name]
        pass

    def select(self,bones):
        selection = []
        for bone in bones:
            self.databone(bone.name).select = True
            selection.append(bone)

        return selection
        pass

    def select_all(self):
        selection = []
        for bone in self.armature.data.bones:
            bone.select = True
            selection.append(bone)

        return selection

    def get_selected_list(self):
        selection = []
        for bone in self.armature.data.bones:
            if bone.select:
                selection.append(bone)
        return selection

    def deselect(self):
        for bone in self.armature.data.bones:
            bone.select = False
        pass

    def clearTrans(self, bones):
        for bone in bones:
            pbone = self.posebone(bone.name)
            pbone.location = (0,0,0)
            pbone.rotation_euler.zero()
            qzero = pbone.rotation_euler.to_quaternion()
            pbone.rotation_quaternion = qzero
        pass


    def GetGeometryBone(self):
        geoname = self.findname("Geometry")

        if geoname == None:
            geoname = self.findname("geometry")

        if geoname == None:
            geoname = self.findname("geo")

        if geoname == None:
            geoname = self.findname("Root")

        if geoname == None:
            geoname = self.findname("root")

        if geoname == None:
            #head位置が0,0,0のものを探してやればいいのでは？
            for ebone in self.armature.data.bones:
                if ebone.head == Vector((0,0,0)):
                    geoname = ebone.name
                    break

        #それでもなければアクティブをジオメトリに使う
        if geoname == None:
            geoname = self.poseactive().name

        #それでもなければ0番をジオメトリに使う
        if geoname == None:
            geoname = self.self.armature.data.bones[0].name

        geo = self.posebone(geoname)
        return geo


    #ボーン作成まわり
    def add_bone(self, name, pos, vec):
        pos = Vector(pos)
        vec = Vector(vec)
        
        obj = active()
        mode("EDIT")
        bpy.ops.armature.select_all(action='DESELECT')
        bone = obj.data.edit_bones.new(name)
        bone.head = pos
        bone.tail = pos + vec
        return bone

    def remove_bone(self, ebone):
        mode("EDIT")
        self.armature.data.edit_bones.remove(ebone)
        return
    
    def clear_bones(self):
        mode("EDIT")
        for ebone in self.armature.data.edit_bones:
            self.armature.data.edit_bones.remove(ebone)
        return
