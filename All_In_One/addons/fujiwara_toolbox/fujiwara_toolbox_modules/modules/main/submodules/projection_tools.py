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
import json

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



class ProjectionUtils():
    def __init__(self, filepath):
        self.filepath = filepath

    def __add_new_mat(self, obj):
        mat = bpy.data.materials.new("Projection Mat")
        obj.data.materials.append(mat)
        obj.active_material_index = len(obj.material_slots) - 1
        return mat

    @classmethod
    def set_active_mat(self, obj, mat_name):
        i = obj.material_slots.find(mat_name)
        if i == -1:
            return
        obj.active_material_index = i

    def __get_active_mat(self, obj):
        if not obj:
            return None

        if not obj.active_material:
            self.__add_new_mat(obj)
        
        return obj.active_material

    def __make_projector(self, name, baseobj):
        """
        プロジェクタ名はテクスチャ名を使うといいかも。
        """
        #オブジェクト作成
        # pos = (baseobj.location[0], baseobj.location[1] - 1, baseobj.location[2])
        pos = baseobj.location
        bpy.ops.mesh.primitive_plane_add(radius=1, calc_uvs=True, view_align=False, enter_editmode=False, location=pos, layers=baseobj.layers)
        projector = fjw.active()
        projector.name = "UVProjector_"+name
        projector.data.uv_textures[0].name = projector.name
        projector.hide_render = True

        #コンストレイント
        c = projector.constraints.new("DAMPED_TRACK")
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.target = baseobj

        #マテリアル
        projector.data.materials.append(baseobj.active_material)

        return projector

    def __add_texture_to_mat(self, mat, filepath, projector):
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        tslot = mat.texture_slots.add()
        tslot.texture = bpy.data.textures.new(name, "IMAGE")
        tslot.texture.image = bpy.data.images.load(filepath)

        tslot.uv_layer = projector.name
        tslot.blend_type = "MULTIPLY"

    @classmethod
    def set_uv_projection(self, obj, projector):
        obj.data.uv_textures.new(projector.name)

        modu = fjw.Modutils(obj)
        m = modu.add(projector.name, "UV_PROJECT")
        print(projector.name)
        m.uv_layer = projector.name
        m.projectors[0].object = projector

    def execute(self, use_active_camera = False, to_active_mat = True):
        filename = os.path.basename(self.filepath)
        name, ext = os.path.splitext(filename)

        obj = fjw.active()
        current_mode = obj.mode

        if current_mode == "OBJECT":
            mat = self.__get_active_mat(obj)
        elif current_mode == "EDIT":
            self.__add_new_mat(obj)
            mat = self.__get_active_mat(obj)
            bpy.ops.object.material_slot_assign()

        fjw.mode("OBJECT")

        active_camera = bpy.context.scene.camera
        if active_camera and use_active_camera:
            projector = active_camera
        else:
            projector = self.__make_projector(name, obj)

        if to_active_mat:
            self.__add_texture_to_mat(mat, self.filepath, projector)
        else:
            for mat in obj.data.materials:
                self.__add_texture_to_mat(mat, self.filepath, projector)
        self.set_uv_projection(obj, projector)

        projector.parent = obj
    
    def set_projector_to_objects(self, projector, objects, to_active_mat = False):
        for obj in objects:
            # if to_active_mat:
            #     self.__add_texture_to_mat(mat, self.filepath, projector)
            # else:
            #     for mat in obj.data.materials:
            #         self.__add_texture_to_mat(mat, self.filepath, projector)
            self.set_uv_projection(obj, projector)
        


class ProjectionTools():
    def __init__(self):
        pass

    def set_camera(self, camera):
        self.camera = camera
        self.camera_state = fjw.ObjectState(camera)

    def new_projection_mat(self, name):
        matname = name
        mat = bpy.data.materials.new(matname)
        mat.use_shadeless = True
        mat.diffuse_color = (1, 1, 1)
        return mat

    def load_texture(self, mat, filepath, uv_name):
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        tslot = mat.texture_slots.add()
        tslot.texture = bpy.data.textures.new(name, "IMAGE")
        tslot.texture.image = bpy.data.images.load(filepath)

        tslot.uv_layer = uv_name
        tslot.blend_type = "MULTIPLY"

        #透過まわり
        mat.use_transparency = True
        mat.alpha = 1
        tslot.use_map_alpha = True

        return tslot.texture

    def get_texture_path(self, filepath):
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)

        if ext == ".png" or ext == ".psd":
            return filepath

        texture_path = dirname + os.sep + name + ".png"
        if not os.path.exists(texture_path):
            # texture_path = dirname + os.sep + name + os.sep + name + ".png"
            texdir = dirname + os.sep + name
            files = os.listdir(texdir)
            if len(files) == 0:
                print("texture_path not found:%s"%texture_path)
                return None
            
            texture_path = texdir + os.sep + files[0]

            if not os.path.exists(texture_path):
                print("texture_path not found:%s"%texture_path)
                return None
        return texture_path
    
    def load_json(self, filepath):
        f = open(filepath)
        data = f.read()
        f.close()
        result = json.loads(data)
        return result
    
    def make_plane(self, parent, filepath):
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)

        texture_path = self.get_texture_path(filepath)
        if not texture_path:
            return None

        #とりあえずplaneを用意して画像をロード。計算がめんどくなるので半径0.5＝直径1に。→プロジェクションでダメだった！！1でやらないと見た目があわない！
        bpy.ops.mesh.primitive_plane_add(radius=1, calc_uvs=True, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        plane = fjw.active()
        plane.name = "Projector_" + name
        plane.layers = parent.layers
        plane.data.uv_textures[0].name = plane.name

        mat = self.new_projection_mat(plane.name)
        texture = self.load_texture(mat, texture_path, plane.name)
        plane.data.materials.append(mat)
        return plane

    def load_png_with_camera(self, filepath):
        pass

    def load_img_with_camera(self, filepath, tilenumber=1, use_json=True):
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        
        fjw.deselect()
        plane = self.make_plane(self.camera, filepath)
        if not plane:
            return None
        plane.hide_render = True

        if use_json:
            ############json依存ここから
            j = self.load_json(filepath)
            doc_size = [j["document"]["width"], j["document"]["height"]]
            layer_size = [j["layer"]["width"],j["layer"]["height"]]
            layer_pos = Vector(j["layer"]["posmid"])
            tilenumber = j["tile"]

            camscale = self.camera.data.ortho_scale

            #レイヤー座標
            #layer_posを中心を0とした、-0.5～0.5の範囲に変換する
            layer_pos[0] = (layer_pos[0] / doc_size[0] - 0.5)
            layer_pos[1] = (layer_pos[1] / doc_size[1] - 0.5)*-1 #座標逆！！

            #*カメラスケール
            layer_pos *= camscale
            print(layer_pos)
            plane.location = (layer_pos[0], layer_pos[1], 0)

            zpos = (0.5 + len(self.camera.children)*0.1)*-1
            plane.location[2] = zpos*0.1

            #レイヤースケール
            #ドキュメントにおけるレイヤーの大きさ割合を算出
            layer_scale = Vector([1,1])
            layer_scale[0] = layer_size[0] / doc_size[0]
            layer_scale[1] = layer_size[1] / doc_size[1]
            #*カメラスケール
            layer_scale *= camscale
            #8*8分割画像なのでさらに8倍
            layer_scale *= tilenumber
            plane.scale = (layer_scale[0], layer_scale[1], 1)
            ############json依存ここまで
        else:
            camscale = self.camera.data.ortho_scale
            plane.scale = (camscale,camscale,camscale)

        #位置オフセット
        if tilenumber != 1:
            offset = Vector([0,0])
            offset[0] = plane.scale[0]/2 - plane.scale[0]/tilenumber/2
            offset[1] = plane.scale[1]/2 - plane.scale[0]/tilenumber/2
            plane.location[0] += offset[0]
            plane.location[1] -= offset[1]

        if use_json:
            plane.scale *= 0.5

        #カメラを移動させてプロジェクタを子にする
        self.camera_state.store_transform()

        self.camera.location = (0,0,0)
        self.camera.rotation_euler = (0,0,0)
        plane.parent = self.camera

        self.camera_state.restore_transform()

        return plane

    def dup(self, obj):
        fjw.mode("OBJECT")
        fjw.deselect()
        obj.select = True
        bpy.ops.object.duplicate()
        selection = fjw.get_selected_list()
        return selection[0]

    def flip_x(self, obj):
        obj.scale.x *= -1
        obj.location.x *= -1

    def fix_uvname(self, obj):
        obj.data.uv_textures[0].name = obj.name
        for mat in obj.data.materials:
            for tslot in mat.texture_slots:
                if not tslot:
                    continue
                tslot.uv_layer = obj.name

    def flip_x_dup(self, obj):
        name = obj.name
        if obj.location.x < 0:
            baseside = "_R"
            flipside = "_L"
        else:
            baseside = "_L"
            flipside = "_R"

        dup = self.dup(obj)
        self.flip_x(dup)

        obj.name = name + baseside
        dup.name = name + flipside

        bpy.ops.object.make_single_user(object=True, obdata=True, material=True, texture=True, animation=False)
        self.fix_uvname(obj)
        self.fix_uvname(dup)

        return dup


class FaceSetupTools():
    def __init__(self, faceobj, camera):
        self.camera = camera
        self.face = faceobj
        #プロジェクションで使用するマテリアルのリスト
        self.materials = {}

    def getmat_with_name(self, name):
        if name in self.materials:
            return self.materials[name]
        return None

        #やっぱだめこれ
        # obj = fjw.active()
        # if name in obj.data.materials:
        #     return obj.data.materials[name]
        # else:
        #     print("mat not found:%s"%name)
        #     mat = bpy.data.materials.new(name)
        #     print("mat created.")
        #     obj.data.materials.append(mat)
        # return mat

    def get_material(self, name):
        #オブジェクトからの取得じゃなくて顔システムからの取得なことに注意
        #これが割当失敗の原因では？ちゃんと変数に保持できてないのでは。
        #→オブジェクトのマテリアルでやる
        mat = self.getmat_with_name(name)
        if not mat:
            #マテリアルがリストにないので新規作成
            mat = bpy.data.materials.new(name)
            self.materials[name] = mat
        print("material:%s"%str(mat))
        return mat

        # mat = self.getmat_with_name(name)
        # return mat

    def assign_material_to_mesh(self, mat):
        obj = fjw.active()
        mode = obj.mode
        if mat.name not in obj.data.materials:
            obj.data.materials.append(mat)
        index = obj.material_slots.find(mat.name)
        obj.active_material_index = index
        fjw.mode("EDIT")
        bpy.ops.object.material_slot_assign()
        fjw.mode(mode)

    @classmethod
    def select_mesh_by_material(self, obj, matname):
        fjw.mode("EDIT")
        index = obj.material_slots.find(matname)
        obj.active_material_index = index
        bpy.ops.object.material_slot_select()


    #matにテクスチャを設定する
    #透過あり・なし、テクスチャの透過あり・なし
    def set_texture_to_mat(self, mat, image, uv_name, use_color=True, use_alpha_factor=True, use_img_alpha=True):
        #別に読み込んで設定変える
        if not use_img_alpha:
            image = bpy.data.images.load(image.filepath)
            image.use_alpha = False

        tslot = mat.texture_slots.add()
        texture = bpy.data.textures.new(uv_name, "IMAGE")
        tslot.texture = texture
        tslot.texture.image = image

        tslot.uv_layer = uv_name
        tslot.blend_type = "MULTIPLY"

        tslot.use_map_color_diffuse = use_color
        tslot.diffuse_color_factor = 1

        tslot.use_map_alpha = use_alpha_factor
        tslot.alpha_factor = 1
        return tslot

    #_noalphaを取得する
    def get_noalpha(self, image):
        filepath = image.filepath
        filedir = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)

        path_noalpha = filedir + os.sep + name + "_noalpha" + ext
        if not os.path.exists(path_noalpha):
            return None
        
        image = bpy.data.images.load(path_noalpha)
        return image

    def mesh_dup(self, vertex_group=""):
        base = fjw.active()
        mode = base.mode

        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.mode("EDIT")

        if vertex_group != "":
            self.mesh_deselect()
            self.select_by_vertex_group(vertex_group)

        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        fjw.mode("OBJECT")
        for obj in fjw.get_selected_list():
            if obj != base:
                fjw.activate(obj)
                fjw.mode("EDIT")
                break
        dup = fjw.active()
        dup.data.materials.clear()
        self.clear_mods()
        # dup.parent = base
        return dup

    def mesh_dup_and_solidify(self, thickness, offset, use_rim_only=False, use_flip_normals=False):
        dup = self.mesh_dup()
        modu = fjw.Modutils(dup)
        m = modu.add("Solidify", "SOLIDIFY")
        m.thickness = thickness
        m.offset = offset
        m.use_rim_only = use_rim_only
        m.use_flip_normals = use_flip_normals
        return dup

    def get_projector(self, name, find=False):
        #nameのクリーンアップ
        name = re.sub(r"\.\d+", "", name)

        # カメラの子からプロジェクタを取得する
        for obj in self.camera.children:
            if name == obj.name:
                return obj
            if find:
                if name in obj.name:
                    return obj
        print("get_projector:%s not found."%name)
        return None

    def get_projector_image(self, projector_name, find=False):
        proj = self.get_projector(projector_name, find)
        if not proj:
            print("!:no proj.")
            return None
        img = proj.data.materials[0].texture_slots[0].texture.image
        return img

    #いろいろマテリアル設定と肌テクスチャの割当
    def facemat_basesetup(self, mat):
        mat.use_transparency = True
        mat.use_shadeless = True
        mat.diffuse_color = (1, 1, 1)

    def facemat_skinsetup(self, mat):
        img = self.get_projector_image("Projector_Skin")
        if not img:
            print("!:no img.")
            return
        tslot = self.set_texture_to_mat(mat, img, "Skin")
        self.tslot_setting(tslot, True, False)
        tslot = self.add_projectorimage_to_mat(mat, "Shadow")
        self.tslot_setting(tslot, True, False)
        tslot = self.add_projectorimage_to_mat(mat, "Cheek")
        self.tslot_setting(tslot, True, False)

    def clear_mods(self):
        obj = fjw.active()
        modu = fjw.Modutils(obj)
        for m in modu.mods:
            if m.type != "MIRROR" and m.type != "SUBSURF":
                modu.remove(m)

    def set_projection(self, projector_name, mat, find=False):
        """
        projectorを受け取ってmatのプロジェクタにする。
        """
        obj = fjw.active()
        mode = obj.mode
        fjw.mode("OBJECT")
        proj = self.get_projector(projector_name, find)
        if not proj:
            print("!:no proj:%s"%projector_name)
            #プロジェクタがなければキャンセル
            fjw.mode(mode)
            return
        ProjectionUtils.set_uv_projection(obj, proj)
        fjw.mode(mode)
        pass


    def mesh_select_all(self):
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')

    def mesh_deselect(self):
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')
    
    def mesh_invertselection(self):
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='INVERT')

    def select_by_vertex_group(self, name):
        fjw.mode("EDIT")
        #頂点グループで選択する
        obj = fjw.active()
        if name not in obj.vertex_groups:
            return False
        
        vg = obj.vertex_groups[name]
        vgi = obj.vertex_groups.find(name)
        obj.vertex_groups.active_index = vgi
        bpy.ops.object.vertex_group_select()
        return True

    def deselect_by_axis(self, axis):
        #指定した軸を選択解除する
        d = 0
        if "x" in axis:
            d = 0
        elif "y" in axis:
            d = 1
        elif "z" in axis:
            d = 2
        s = 1
        if "-" in axis:
            s = -1

        obj = fjw.active()
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        for v in bm.verts:
            if v.co[d] * s > 0:
                v.select = False
        bm.select_flush(False)

    def face_cleanup(self):
        #生成した目とかいろいろ除去
        #UV除去
        #マテリアル除去
        #モディファイア除去
        return

    def assign_material_by_vetexgroup(self, vertex_group, mat, deselect_axis=""):
        obj = fjw.active()
        mode = obj.mode
        fjw.mode("EDIT")
        self.mesh_deselect()
        self.select_by_vertex_group(vertex_group)
        if deselect_axis != "":
            self.deselect_by_axis(deselect_axis)
        self.assign_material_to_mesh(mat)
        fjw.mode(mode)

    def tslot_setting(self, tslot, use_map_color_diffuse, use_map_alpha, invert=False, use_rgb_to_intensity=False):
        if not tslot:
            print("!:no slot.")
            return
        tslot.use_map_color_diffuse = use_map_color_diffuse
        tslot.use_map_alpha = use_map_alpha
        tslot.invert = invert
        tslot.use_rgb_to_intensity = use_rgb_to_intensity

    def add_projectorimage_to_mat(self, mat, projector_name):
        prj = self.get_projector(projector_name, True)
        if not prj:
            print("!:no prj.")
            return
        img = self.get_projector_image(prj.name)
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        return tslot

    def attouch_uraporiedge(self):
        fjw.deselect()
        fjw.activate(self.face)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.fujiwara_toolbox.command_318722()

    def facesetup(self):
        """
        ミラーモディファイアの適用
        マテリアル割当←割り当てる前にマテリアルを作っとく必要がある
        目・眉頂点グループを左右別に割り当てる
        眼球用メッシュ分離→厚みマイナスつけてフチのみにする＝へこます
        
        まつげ用メッシュ複製分離→まつげ用マテリアルを割り当て

        ・頂点グループ
        Eye, Mouth, Eyebrow
        """
        fjw.deselect()
        fjw.activate(self.face)

        modu = fjw.Modutils(self.face)
        mod_mirror = modu.find_bytype("MIRROR")
        if mod_mirror:
            modu.apply(mod_mirror)
        vgu = fjw.VertexGroupUtils(self.face)


        ########################################
        # メッシュセットアップ
        ########################################
        #鼻線画
        fjw.mode("EDIT")
        self.mesh_deselect()
        bpy.context.scene.tool_settings.mesh_select_mode = [True, False, False]
        self.select_by_vertex_group("Nose")
        bpy.ops.fujiwara_toolbox.make_skin_line()
        bpy.ops.transform.skin_resize(value=(0.0526974, 0.0526974, 0.0526974), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.0295401)
        bpy.ops.mesh.subdivide(smoothness=0)
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(self.face)


        #プロジェクション設定
        #肌
        mat = self.get_material("Skin")
        self.set_projection("Shadow", mat, find=True)
        self.set_projection("Cheek", mat, find=True)
        self.assign_material_to_mesh(mat)

        #まつげテクスチャをつかった目の穴
        mat = self.get_material("Eyehole_R")
        self.set_projection("Eyelid_R", mat, find=True)
        self.assign_material_by_vetexgroup("Eye", mat, "x")

        mat = self.get_material("Eyehole_L")
        self.set_projection("Eyelid_L", mat, find=True)
        self.assign_material_by_vetexgroup("Eye", mat, "-x")

        #口
        mat = self.get_material("Mouth")
        self.set_projection("Mouth", mat, find=True)
        self.assign_material_by_vetexgroup("Mouth", mat)

        #まゆげ
        #選択したら複製する
        eyebrow = self.mesh_dup("Eyebrow")
        eyebrow.location[1] -= 0.001
        eyebrow.name = "Eyebrow"

        mat = self.get_material("Eyebrow_R")
        self.set_projection("Eyebrow_R", mat, find=True)
        self.assign_material_by_vetexgroup("Eyebrow", mat, "x")

        mat = self.get_material("Eyebrow_L")
        self.set_projection("Eyebrow_L", mat, find=True)
        self.assign_material_by_vetexgroup("Eyebrow", mat, "-x")
        
        #目
        fjw.mode("OBJECT")
        fjw.activate(self.face)
        fjw.mode("EDIT")
        eye = self.mesh_dup("Eye")
        eye.location[1] += 0.001
        eye.name = "Eye"
        
        mat = self.get_material("Eye_R")
        self.set_projection("Pupil_R", mat, find=True)
        self.assign_material_by_vetexgroup("Eye", mat, "x")

        mat = self.get_material("Eye_L")
        self.set_projection("Pupil_L", mat, find=True)
        self.assign_material_by_vetexgroup("Eye", mat, "-x")

        #外周をすこし後ろに
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.transform.translate(value=(0, 0.001, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True, use_accurate=False)


        #まつげ　Z処理的に、厚み付じゃだめ。座標をズラす。
        fjw.mode("OBJECT")
        fjw.activate(self.face)
        fjw.mode("EDIT")
        eyelid = self.mesh_dup("Eye")
        eyelid.location[1] -= 0.001
        eyelid.name = "Eyelid"

        mat = self.get_material("Eyelid_R")
        self.set_projection("Eyelid_R", mat, find=True)
        self.assign_material_by_vetexgroup("Eye", mat, "x")

        mat = self.get_material("Eyelid_L")
        self.set_projection("Eyelid_L", mat, find=True)
        self.assign_material_by_vetexgroup("Eye", mat, "-x")

        #外周の拡張
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.fujiwara_toolbox.command_357169()
        bpy.ops.fujiwara_toolbox.pivot_to_individual()
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.resize(value=(1.66677, 1.66677, 1.66677), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

        fjw.mode("OBJECT")
        fjw.activate(self.face)
        fjw.mode("OBJECT")

        ########################################
        # マテリアルセットアップ
        ########################################
        mat = self.get_material("Skin")
        self.facemat_basesetup(mat)
        self.facemat_skinsetup(mat)

        mat = self.get_material("Eyehole_R")
        self.facemat_basesetup(mat)
        self.facemat_skinsetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, "Eyelid_R")
        self.tslot_setting(tslot, False, True)

        mat = self.get_material("Eyehole_L")
        self.facemat_basesetup(mat)
        self.facemat_skinsetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, "Eyelid_L")
        self.tslot_setting(tslot, False, True)

        mat = self.get_material("Mouth")
        self.facemat_basesetup(mat)
        self.facemat_skinsetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, mat.name)
        self.tslot_setting(tslot, True, True)

        mat = self.get_material("Eyebrow_R")
        # self.facemat_basesetup(mat)
        # tslot = self.add_projectorimage_to_mat(mat, mat.name)
        # self.tslot_setting(tslot, True, True)
        self.facemat_basesetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, mat.name)
        prj = self.get_projector(mat.name, True)
        img = self.get_projector_image(prj.name)
        img = self.get_noalpha(img)
        #アルファ
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, False, True, True, True)
        #カラー
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, True, False)

        mat = self.get_material("Eyebrow_L")
        # self.facemat_basesetup(mat)
        # tslot = self.add_projectorimage_to_mat(mat, mat.name)
        # self.tslot_setting(tslot, True, True)
        self.facemat_basesetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, mat.name)
        prj = self.get_projector(mat.name, True)
        img = self.get_projector_image(prj.name)
        img = self.get_noalpha(img)
        #アルファ
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, False, True, True, True)
        #カラー
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, True, False)

        mat = self.get_material("Eye_R")
        self.facemat_basesetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, "Pupil_R")
        self.tslot_setting(tslot, True, False)

        mat = self.get_material("Eye_L")
        self.facemat_basesetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, "Pupil_L")
        self.tslot_setting(tslot, True, False)

        mat = self.get_material("Eyelid_R")
        self.facemat_basesetup(mat)
        tslot = self.add_projectorimage_to_mat(mat, mat.name)
        prj = self.get_projector(mat.name, True)
        img = self.get_projector_image(prj.name)
        img = self.get_noalpha(img)
        #アルファ
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, False, True, True, True)
        #カラー
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, True, False)

        mat = self.get_material("Eyelid_L")
        self.facemat_basesetup(mat)
        prj = self.get_projector(mat.name, True)
        img = self.get_projector_image(prj.name)
        img = self.get_noalpha(img)
        #アルファ
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, False, True, True, True)
        #カラー
        tslot = self.set_texture_to_mat(mat, img, prj.name)
        self.tslot_setting(tslot, True, False)

        #仕上げに拡縮を適用して裏ポリエッジをつける
        self.attouch_uraporiedge()
        # bpy.ops.fujiwara_toolbox.command_793908()#2mm

    def clear_texture(self, texture):
        if not texture:
            return
        img = texture.image
        if img:
            bpy.data.images.remove(img)
        bpy.data.textures.remove(texture)
        return

    def clear_material(self, material):
        if not material:
            return
        for tslot in material.texture_slots:
            if not tslot:
                continue
            if not tslot.texture:
                continue
            self.clear_texture(tslot.texture)
        bpy.data.materials.remove(material)

    def clear_uv(self, data):
        # for uv in data.uv_textures:
        #     data.uv_textures.remove(uv)
        for i in range(len(data.uv_textures)):
            data.uv_textures.remove(data.uv_textures[0])

    def clear_object(self, obj, mod=True):
        self.clear_uv(obj.data)
        for mat in obj.data.materials:
            self.clear_material(mat)
        obj.data.materials.clear()
        if mod:
            obj.modifiers.clear()

    def clear_face(self):
        self.clear_object(self.face, False)
        modu = fjw.Modutils(self.face)
        for mod in modu.mods:
            if mod.type == "MIRROR":
                modu.apply(mod)
                continue
            
            if mod.type == "SUBSURF":
                continue
            
            if "裏ポリ" in mod.name:
                continue

            modu.remove(mod)

        return
    
    def remove_object(self, obj):
        if obj.type == "MESH":
            self.clear_object(obj)
        bpy.data.objects.remove(obj)

    def initialize_all(self):
        dellist = ["Eye", "Eyebrow", "Eyelid"]
        for obj in self.face.parent.children:
            if obj.name in dellist:
                self.remove_object(obj)

        self.clear_face()

        for obj in self.camera.children:
            self.remove_object(obj)

        if "FaceAramature" in bpy.context.scene.objects:
            facearmature = bpy.context.scene.objects["FaceAramature"]
            for obj in facearmature.children:
                self.remove_object(obj)
            self.remove_object(facearmature)
            

