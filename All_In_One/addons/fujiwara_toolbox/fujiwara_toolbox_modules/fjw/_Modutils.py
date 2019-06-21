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

class Modutils():
    def __init__(self, obj):
        self.object = obj
        self.mods = obj.modifiers
        pass

    def add(self,name,mod_type):
        return self.mods.new(name, mod_type)

    def remove_byname(self,name):
        mod = self.find(name)
        if mod != None:
            self.object.modifiers.remove(mod)
    
    def remove(self, mod):
        if mod != None:
            self.object.modifiers.remove(mod)

    def apply(self, mod):
        if mod != None:
            activate(self.object)
            print("apply:%s"%mod.name)
            try:
                #ほんとはシェイプキー残しときたかったけど、無理。うまくいかない。全部除去したほうがいい。
                shape_keys = self.object.data.shape_keys
                if shape_keys and len(shape_keys.key_blocks) > 0:
                    self.object.active_shape_key_index = 0
                    bpy.ops.object.shape_key_remove(all=True)

                # #シェイプキーが一つだけだったら削除しちゃう
                # if len(shape_keys.key_blocks) == 1:
                #     bpy.ops.object.shape_key_remove(all=False)

                # print("try1")
                bpy.ops.object.modifier_apply(modifier=mod.name)
                # print("success!")
            except:
                import traceback
                traceback.print_exc()
                pass
                # try:
                #     # print("try2")
                #     shape_keys = self.object.data.shape_keys
                #     if shape_keys and len(shape_keys.key_blocks) > 0:
                #         mod_name = mod.name
                #         bpy.ops.object.modifier_apply(apply_as='SHAPE',modifier=mod.name)
                #         #アクティブをかえないといけない
                #         #該当シェイプキーの検索
                #         for i in range(len(shape_keys.key_blocks)):
                #             key = shape_keys.key_blocks[i]
                #             if key.name == mod_name:
                #                 self.object.active_shape_key_index = i
                #                 bpy.ops.object.shape_key_move(type='TOP')
                #                 self.object.active_shape_key_index = 0
                #                 break
                #         for i in range(len(shape_keys.key_blocks)):
                #             key = shape_keys.key_blocks[i]
                #             if key.name == "Basis":
                #                 self.object.active_shape_key_index = i
                #                 bpy.ops.object.shape_key_remove(all=False)
                #                 break
                #         self.object.active_shape_key_index = 0
                #         self.object.active_shape_key.name = "Basis"
                #         # self.object.active_shape_key_index = len(shape_keys.key_blocks) - 1
                #         # bpy.ops.object.shape_key_move(type='TOP')
                #         # self.object.active_shape_key_index = 0
                #         # bpy.ops.object.shape_key_remove(all=False)
                #         # self.object.active_shape_key.name = "Basis"
                #         # print("success!")
                # except:
                #     print("Failed:%s"%mod.name)
                #     pass


    def find(self,name):
        for mod in self.mods:
            if name in mod.name:
                return mod
        return None

    def find_list(self,name):
        result = []
        for mod in self.mods:
            if name in mod.name:
                result.append(mod)
        return result
    
    def find_bytype(self, mod_type):
        for mod in self.mods:
            if mod_type == mod.type:
                return mod
        return None

    def find_bytype_list(self, type):
        result = []
        for mod in self.mods:
            if type == mod.type:
                result.append(mod)
        return result

    def move_up(self,mod):
        if mod != None:
            activate(self.object)
            bpy.ops.object.modifier_move_up(modifier=mod.name)

    def move_down(self,mod):
        if mod != None:
            activate(self.object)
            bpy.ops.object.modifier_move_down(modifier=mod.name)

    def move_top(self, mod):
        if mod == None:
            return

        activate(self.object)
        last = len(self.object.modifiers) - 1
        mod_md = mod
        mod_n = last
        for i in range(mod_n - 1, -1, -1):
            bpy.ops.object.modifier_move_up(modifier=mod.name)

    def move_bottom(self, mod):
        if mod == None:
            return

        activate(self.object)
        last = len(self.object.modifiers) - 1
        modi = self.object.modifiers.find(mod.name)

        for i in range(modi,last):
            bpy.ops.object.modifier_move_down(modifier=mod.name)

    def show(self, mod):
        if mod != None:
            mod.show_viewport = True
            mod.show_render = True

    def hide(self, mod):
        if mod != None:
            mod.show_viewport = False
            mod.show_render = False

    def get_last(self):
        lastindex = len(self.object.modifiers) - 1
        lastmod = self.object.modifiers[lastindex]
        return lastmod

    def indexof(self, mod):
        index = self.object.modifiers.find(mod)
        return index

    def getbyindex(self, index):
        if index < len(self.object.modifiers):
            return self.object.modifiers[index]
        else:
            return None

    def sort(self):
        #後にやる方が上にくる
        modlist = self.find_bytype_list("MESH_DEFORM")
        for mod in modlist:
            self.move_top(mod)
        modlist = self.find_bytype_list("SURFACE_DEFORM")
        for mod in modlist:
            self.move_top(mod)
        modlist = self.find_bytype_list("ARMATURE")
        for mod in modlist:
            self.move_top(mod)
        modlist = self.find_bytype_list("MIRROR")
        for mod in modlist:
            self.move_top(mod)
        self.move_top(self.find("Parented Mirror"))
        self.move_top(self.find("Target Mirror"))


        self.move_bottom(self.find("分離エッジ_EDGE_SPLIT"))
        self.move_bottom(self.find("分離エッジ_SOLIDIFY"))
        self.move_bottom(self.find("裏ポリエッジ"))

        pass

    def func(self):
        pass
