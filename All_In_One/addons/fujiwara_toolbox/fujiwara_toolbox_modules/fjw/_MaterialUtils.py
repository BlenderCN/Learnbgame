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



class MaterialUtils():
    def __init__(self, obj):
        self.obj = obj
    
    def set_active_mat(self, mat):
        """アクティブマテリアルを指定する。
        Arguments:
            :param mat:マテリアル名、もしくはマテリアル。
        Outputs:
            :return: アクティブマテリアル
        """
        if not mat:
            return None
        if type(mat) == bpy.types.Material:
            mat_name = mat.name
            if self.obj.material_slots.find(mat_name) == -1:
                self.obj.data.materials.append(mat)
        elif type(mat) == str:
            mat_name = mat
            
        i = self.obj.material_slots.find(mat_name)
        if i == -1:
            return
        self.obj.active_material_index = i
        return self.obj.active_material

    def add_new_mat(self, name):
        mat = bpy.data.materials.new(name)
        self.add(mat)

    def add(self, mat):
        self.obj.data.materials.append(mat)
        self.obj.active_material_index = len(self.obj.material_slots) - 1
        return mat

    def get_active_mat(self):
        return self.obj.active_material

    def find(self, name):
        """指定されたマテリアルをファイル内で検索する"""
        for mat in bpy.data.materials:
            if mat.name == name and not mat.is_library_indirect:
                return mat
        return None

    def mat(self, name):
        """指定された名前のマテリアルをアクティブマテリアルにし、取得する。
            なければ新規作成される。
        """
        mat = self.find(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        self.set_active_mat(mat)
        return mat

    def add_texture_slot(self):
        mat = self.get_active_mat()
        tslot = mat.texture_slots.add()
        return tslot

    def add_texture(self, filepath=None, 
        texture=None,
        uv_layer="", 
        blend_type = 'MIX',

        use_map_color_diffuse=True, 
        diffuse_color_factor = 1,
        use_map_alpha=True,
        alpha_factor = 1,

        use_map_normal = False,
        normal_factor = 1,
        use_normal_map = False,
        ):
        """アクティブマテリアルにテクスチャを追加する。
        Arguments:
            :param filepath: テクスチャのファイルパス
            :param etc: テクスチャスロット設定
        Returns:
            :return: テクスチャスロットを返す。
        """
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        mat = self.get_active_mat()
        if not mat:
            print("! no active material!")
            return None

        tslot = mat.texture_slots.add()
        tslot.texture = bpy.data.textures.new(name, "IMAGE")
        tslot.texture.image = bpy.data.images.load(filepath)

        tslot.uv_layer = uv_layer
        tslot.blend_type = blend_type

        tslot.use_map_color_diffuse=use_map_color_diffuse
        tslot.diffuse_color_factor = diffuse_color_factor
        tslot.use_map_alpha=use_map_alpha
        tslot.alpha_factor = alpha_factor

        tslot.use_map_normal = use_map_normal
        tslot.normal_factor = normal_factor
        tslot.use_normal_map = use_normal_map
        return tslot

    def setting(self, 
        diffuse_intensity = None,
        diffuse_color = None,
        specular_intensity = None,
        specular_color = None,
        use_transparency=None,
        alpha=None,
        use_shadeless = None,
        ):
        """アクティブマテリアルの設定をする。"""
        mat = self.get_active_mat()
        if not mat:
            return

        if diffuse_intensity:
            mat.diffuse_intensity = diffuse_intensity
        if diffuse_color:
            mat.diffuse_color = diffuse_color
        if specular_intensity:
            mat.specular_intensity = specular_intensity
        if specular_color:
            mat.specular_color = specular_color
        if use_transparency:
            mat.use_transparency=use_transparency
        if alpha:
            mat.alpha=alpha,
        if use_shadeless:
            mat.use_shadeless = use_shadeless

