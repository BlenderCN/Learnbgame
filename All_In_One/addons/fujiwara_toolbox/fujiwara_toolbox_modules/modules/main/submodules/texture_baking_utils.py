import bpy
#パス関連のユーティリティ
#http://xwave.exblog.jp/7155003
import os.path
import os
import re
import bmesh
import datetime
import subprocess
import shutil
import time
import copy
import sys
import mathutils
from collections import OrderedDict
import inspect

# import bpy.mathutils.Vector as Vector
from mathutils import Vector

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf


import random
from mathutils import *

# assetdir = fujiwara_toolbox.conf.assetdir
assetdir = ""


class TextureBaker():
    """
        テクスチャベイカー
        
    
    """

    baketypes = ['FULL', 'AO', 'SHADOW', 'NORMALS', 'TEXTURE', 'DISPLACEMENT', 'DERIVATIVE', 'VERTEX_COLORS', 'EMIT', 'ALPHA', 'MIRROR_INTENSITY', 'MIRROR_COLOR', 'SPEC_INTENSITY', 'SPEC_COLOR']

    def __init__(self, obj, from_objects, width=1024, height=1024, texture_dir=None):
        """
            obj: ベイク先オブジェクト
            width: テクスチャ幅
            height: テクスチャ高さ
        """
        self.obj = obj
        self.from_objects = from_objects
        self.width = width
        self.height = height

        fjw_id = fjw.id(self.obj)
        # self.texture_dir = os.path.dirname(bpy.data.filepath) + os.sep + "textures" + os.sep + fjw_id + os.sep
        # if not os.path.exists(self.texture_dir):
        #     os.makedirs(self.texture_dir)
        if texture_dir:
            self.texture_dir = texture_dir
        else:
            dirname = os.path.dirname(bpy.data.filepath)
            self.texture_dir = dirname + os.sep

        uvu = fjw.UVUtils(self.obj)
        if uvu.is_empty():
            fjw.activate(self.obj)
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            # bpy.ops.uv.smart_project()
            bpy.ops.uv.lightmap_pack()
            fjw.mode("OBJECT")

    def get_identifier(self, name):
        # identifiers = name.split("_")
        # if len(identifiers) == 1:
        #     return None
        # return identifiers[-1]
        # _区切りの入ったidentifierだと問題
        for baketype in self.baketypes:
            if baketype in name:
                return baketype
        return None

    def get_bakemat(self):
        """
            アクティブマテリアルをベイク用マテリアルとして取得する。なければ作成する。
        """
        matu = fjw.MaterialUtils(self.obj)
        mat = matu.get_active_mat()
        if not mat:
            mat = matu.mat(fjw.id(self.obj))

        mat.use_transparency = True
        mat.alpha = 0
        return mat

    def create_baketex(self, name, baketype):
        # テクスチャデータを作成する。
        # タイプがノーマルだったら
        # bpy.data.textures["Texture"].use_normal_map = True
        tex = bpy.data.textures.new(name, "IMAGE")

        if baketype == "normals":
            tex.use_normal_map = True

        return tex

    def tslot_setup(self, texture, baketype, tslot=None):
        # テクスチャスロットを新しくわりあて
        # テクスチャスロットにテクスチャを設定
        # テクスチャスロットをベイクタイプに応じた設定をする
        matu = fjw.MaterialUtils(self.obj)
        if not tslot:
            tslot = matu.add_texture_slot()
        tslot.texture = texture

        uvu = fjw.UVUtils(self.obj)
        uv = uvu.uv()
        tslot.uv_layer = uv.name

        tslot.use_map_color_diffuse = False

        if baketype == "TEXTURE":
            tslot.use_map_color_diffuse = True
            tslot.use_map_alpha = True
            tslot.use_stencil = True
            pass
        elif baketype == "NORMALS":
            tslot.texture.use_normal_map = True
            tslot.use_map_normal = True

            pass
        elif baketype == "ALPHA":
            tslot.use_map_alpha = True
            tslot.use_rgb_to_intensity = True
            tslot.use_stencil = True

            pass
        elif baketype == "SPEC_INTENSITY":
            tslot.use_map_specular = True

            pass
        elif baketype == "SPEC_COLOR":
            tslot.use_map_color_spec = True

            pass
        # elif baketype == "displacement":
        #     pass
        return tslot

    def set_tslots_state(self, state):
        mat = self.obj.active_material
        for i in range(len(mat.use_textures)):
            mat.use_textures[i] = state

    def get_baketex(self, baketype):
        """アクティブマテリアル（なければ作成）からbaketypeに合致する設定のテクスチャを取得する。
        なければ作成する。
        """
        mat = self.get_bakemat()
        
        for tslot in mat.texture_slots:
            if not tslot:
                continue
            if not tslot.texture:
                continue
            tex = tslot.texture
            if tex.type != "IMAGE":
                continue
            identifier = self.get_identifier(tex.name)
            if identifier == baketype:
                return tex
            
        #ベイク用テクスチャの作成
        # テクスチャ名どうする？
        texture_name = self.obj.name + "_" + baketype
        # ゼロから作ってベイクする場合そもそもイメージの保存パスがない。
        image = bpy.data.images.new(texture_name, self.width, self.height)
        image.use_alpha = True
        # テクスチャの生成はめんどくさいので関数化したい
        # めんどいのはスロット設定では？
        # あーでもタイプに応じた設定ある。ノーマル。
        # ノーマルのチェックってどこデータ？→texture
        tex = self.create_baketex(texture_name, baketype)
        # imageはこっちで指定のがよい
        tex.image = image
        self.tslot_setup(tex, baketype)
        return tex

    def get_bakeimage(self, baketype):
        """
            baketypeのイメージを取得する。
            ベイク先オブジェクトのマテリアルからbaketypeのテクスチャ、からイメージを取得する。
            マテリアルがなければマテリアルを作成。テクスチャがなければテクスチャを作成。
        """
        tex = self.get_baketex(baketype)
        return tex.image
    
    def assign_uv_face(self, image):
        """
            ベイク用のimageをuv_faceに割り当てる。
        """
        uvu = fjw.UVUtils(self.obj)
        uv = uvu.uv()

        for uvface in uv.data:
            uvface.image = image
        self.obj.data.update()

    def reassign_image_filepath(self, img):
        """imageのfilepathを再設定し、違った場合は新しいイメージを返す"""
        name = img.name + ".png"
        imgdir = self.texture_dir
        filepath = imgdir + os.sep + name

        if img.filepath == "":
            img.filepath = filepath
            return img

        if img.filepath != filepath:
            img_name = img.name
            bpy.data.images.remove(img)
            img = bpy.data.images.new(img_name, self.width, self.height)
            img.use_alpha = True
            img.filepath = filepath

        return img

    def save_dirtyimages(self):
        for mat in self.obj.data.materials:
            for tslot in mat.texture_slots:
                if tslot:
                    if tslot.texture:
                        if tslot.texture.image:
                            img = tslot.texture.image
                            if img.is_dirty:
                                img.save()

    def bake(self, baketype):
        """
        arguments:
            ベイクタイプ
            baketypes = ['FULL', 'AO', 'SHADOW', 'NORMALS', 'TEXTURE', 'DISPLACEMENT', 'DERIVATIVE', 'VERTEX_COLORS', 'EMIT', 'ALPHA', 'MIRROR_INTENSITY', 'MIRROR_COLOR', 'SPEC_INTENSITY', 'SPEC_COLOR']
            ベイク元オブジェクト群
        """
        fjw.deselect()
        fjw.activate(self.obj)
        bpy.ops.object.shade_smooth() #ソリッドだとガタガタになる
        fjw.select(self.from_objects)

        img = self.get_bakeimage(baketype)
        img = self.reassign_image_filepath(img)
        tex = self.get_baketex(baketype)
        tex.image = img
        self.save_dirtyimages()
        self.assign_uv_face(img)

        self.set_tslots_state(False)
        render = bpy.context.scene.render
        render.bake_type = baketype
        render.use_bake_to_vertex_color = False
        render.use_bake_selected_to_active = True
        render.use_textures = True
        render.use_bake_normalize = False
        render.bake_margin = 14
        bpy.context.scene.render.bake_distance = 0.2
        bpy.context.scene.render.bake_bias = 0.0001
        bpy.ops.object.bake_image()
        self.set_tslots_state(True)

        self.save_dirtyimages()
        bpy.ops.file.make_paths_relative()

        
    def assign_image(self, image_path):
        """ベイクの代わりに既にベイクしたイメージを割り当てる。"""
        fjw.deselect()
        fjw.activate(self.obj)
        bpy.ops.object.shade_smooth()

        # イメージ取得。既にロードされてたらそれを使うべき。
        image = None
        for img in bpy.data.images:
            if img.is_library_indirect:
                continue
            if bpy.path.abspath(img.filepath) == bpy.path.abspath(image_path):
                return img
        if not image:
            # 相対パス化。
            image = bpy.data.images.load(filepath=bpy.path.relpath(image_path))

        dirname, name, ext = fjw.splitpath(image_path)
        textype = self.get_identifier(name)
        tex = self.get_baketex(textype)
        tex.image = image



