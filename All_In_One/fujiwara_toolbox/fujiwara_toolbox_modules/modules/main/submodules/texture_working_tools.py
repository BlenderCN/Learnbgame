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

from fujiwara_toolbox_modules.fjw import JsonTools
from fujiwara_toolbox_modules.modules.main.submodules.texture_baking_utils import TextureBaker


# 仕様考え直し
class TextureWorkingTools():
    @classmethod
    def get_exist_filepath(cls, obj, exportname):
        fjw_id = fjw.id(obj)
        basefilepath = bpy.data.filepath
        dirname, name, ext = fjw.splitpath(basefilepath)
        fjw_dir = dirname + os.sep + "fjw" + os.sep + name + os.sep + fjw_id
        if ".blend" not in exportname:
            exportname = exportname + ".blend"
        expname, expext = os.path.splitext(exportname)
        fjw_path = fjw_dir + os.sep + exportname

        if os.path.exists(fjw_path):
            return fjw_path
        return None

    @classmethod
    def make_texture_workingfile(cls, obj, exportname):
        """
            テクスチャ作業用の作業ファイルを作る。
            
        arguments:
            オブジェクト
            
        outputs:
            最終的にどうなるのか
                fjw_work/元blendファイル名/ユニークID/作業タイプ.blend
                metadata.json
                    textures/元blendファイル/ID/作業タイプ
                    テクスチャ出力先
            この後
                選択オブジェクトとターゲット以外削除なりなんなりする
            
        """
        
        # 前準備
        #     別ファイルに移動するから現状を保存する
        bpy.ops.wm.save_as_mainfile()
        # 必要な情報
        #     元ファイルパス
        basefilepath = bpy.data.filepath
        dirname, name, ext = fjw.splitpath(basefilepath)

        fjw_id = fjw.id(obj)

        fjw_dir = dirname + os.sep + "fjw" + os.sep + name + os.sep + fjw_id
        if ".blend" not in exportname:
            exportname = exportname + ".blend"
        expname, expext = os.path.splitext(exportname)
        fjw_path = fjw_dir + os.sep + exportname
        jsonpath = fjw_dir + os.sep + expname + ".json"

        bpy.context.scene["texture_working_obj"] = fjw_id

        #まずはそのまま保存
        bpy.ops.wm.save_as_mainfile()
        
        # if os.path.exists(fjw_path):
        #     # 既に存在する場合は破棄すべき！作り直し。
        #     shutil.rmtree(fjw_dir)
        # なんもしなければそのまま新規になるのでは？？


        if not os.path.exists(fjw_dir):
            os.makedirs(fjw_dir)
        texture_export_dir = dirname + os.sep + "textures" + os.sep + name + os.sep + fjw_id
        if not os.path.exists(texture_export_dir):
            os.makedirs(texture_export_dir)

        #作業ファイル保存
        bpy.ops.wm.save_as_mainfile(filepath=fjw_path)

        #json保存
        #相対パス化
        json = JsonTools()
        json.val("fjw_id", fjw_id)
        json.val("basepath", bpy.path.relpath(basefilepath))
        json.val("texture_export_dir", bpy.path.relpath(texture_export_dir))
        json.save(jsonpath)
        return json

    @classmethod
    def get_exported_image_paths(cls):
        """生成されたテクスチャの絶対パスのリストを返す"""
        dirname,name,ext = fjw.splitpath(bpy.data.filepath)

        image_paths = []
        # nameと同じ名前のオブジェクト
        if name in bpy.context.scene.objects:
            obj = bpy.context.scene.objects[name]
            fjw_id = fjw.id(obj)

            tex_dir = dirname + os.sep + "textures" + os.sep + fjw_id
            if not os.path.exists(tex_dir):
                print("!no tex dir.")
                return None
            
            files = os.listdir(tex_dir)
            for file in files:
                image_paths.append(tex_dir + os.sep + file)
        
            return image_paths
        return None

    @classmethod
    def get_json(cls):
        """現在のファイルと同名のjsonデータを取得する"""
        dirname, name, ext = fjw.splitpath(bpy.data.filepath)
        jsonpath = dirname + os.sep + name + ".json"
        if not os.path.exists(jsonpath):
            return None
        json = JsonTools(filepath=jsonpath)
        return json

    @classmethod
    def fjw_texture_export_uvmap(cls, obj):
        """
            アクティブオブジェクトのアクティブUVマップ書き出してテクスチャ作業をする。
            
        arguments:
            オブジェクト
            
        outputs:
            アクティブUV画像を書き出し
            作業ディレクトリ/textures/uv名.png
            jsonにテクスチャパスを保存する？いらないかも
            
        既にblendファイルが存在する場合はそのblendファイルを開いて完了したい。
        
        """
        
        if obj.type != "MESH":
            return

        export_name = "uv_map"
        path = cls.get_exist_filepath(obj, export_name)
        if path:
            #既に存在するのでそれを開く
            bpy.ops.wm.open_mainfile(filepath=path)
            return

        fjw.activate(obj)

        # UVをチェック
        if len(obj.data.uv_layers) == 0:
            # なければUVを作成
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()

        uv_layer = obj.data.uv_layers.active

        # テクスチャ作業ファイル作成
        json = cls.make_texture_workingfile(obj, export_name)
        # if not json:
        #     return

        dirname = os.path.dirname(bpy.data.filepath)
        basename = os.path.basename(bpy.data.filepath)
        name, ext = os.path.splitext(basename)
        print("filepath:%s"%bpy.data.filepath)

        # UVテクスチャ出力先
        uv_dir = dirname + os.sep + "textures"
        if not os.path.exists(uv_dir):
            os.makedirs(uv_dir)
        uv_path = uv_dir + os.sep + name + ".png"
        print("uv_path:%s"%uv_path)
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.export_layout(filepath=uv_path, check_existing=False, export_all=False, modified=False, mode='PNG', size=(1024, 1024), opacity=0.25, tessellated=False)
        fjw.mode("OBJECT")


        dellist = []
        for delobj in bpy.context.scene.objects:
            if delobj != obj:
                dellist.append(delobj)

        # 全オブジェクトを削除してUVテクスチャの読み込み
        fjw.delete(dellist)
        bpy.ops.mesh.primitive_plane_add(radius=1, calc_uvs=True, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        plane = fjw.active()
        plane.name = name

        mat = bpy.data.materials.new("uv_map")
        img = bpy.data.images.load(uv_path)
        # mat.use_shadeless = True
        # tslot = mat.texture_slots.add()
        # tex = bpy.data.textures.new("uv_map", "IMAGE")
        # tex.image = img
        # tslot.texture = tex

        plane.data.materials.append(mat)

        # 背景画像として追加
        # https://blender.stackexchange.com/questions/6101/poll-failed-context-incorrect-example-bpy-ops-view3d-background-image-add/6105#6105
        bpy.context.space_data.show_background_images = True
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space_data = area.spaces.active
                bg = space_data.background_images.new()
                bg.image = img
                bg.size = 2
                bg.draw_depth = "FRONT"
                bg.view_axis = "TOP"
                break

        #SUN追加
        bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False, location=(0, 0, 1), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

        bpy.ops.wm.save_as_mainfile()

    @classmethod
    def return_to_basefile(cls):
        json = cls.get_json()
        image_paths = cls.get_exported_image_paths()
        basepath = json.val("basepath")
        fjw_id = json.val("fjw_id")

        #テクスチャ画像を本来あるべき場所にコピー
        texture_export_dir = json.val("texture_export_dir")
        texture_export_dir = bpy.path.abspath(texture_export_dir)

        copied_list = []
        for image_path in image_paths:
            if os.path.exists(image_path):
                copied = shutil.copy(image_path, texture_export_dir)
                copied_list.append(copied)
        
        #ベースパスを開く
        bpy.ops.wm.open_mainfile(filepath=bpy.path.abspath(basepath))

        #対象オブジェクトを取得
        obj = fjw.id(fjw_id)
        print("return_to_basefile:obj:%s"%str(obj))

        #テクスチャ割当
        tbaker = TextureBaker(obj)
        for copied in copied_list:
            tbaker.assign_image(copied)




