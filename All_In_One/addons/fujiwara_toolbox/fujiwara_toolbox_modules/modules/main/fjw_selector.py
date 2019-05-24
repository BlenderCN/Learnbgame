import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import shutil
import re
import subprocess

import unicodedata

from bpy.app.handlers import persistent

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )


bl_info = {
    "name": "FJW Selector",
    "description": "オブジェクト選択等の効率化ツール",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#メインパネル
class FJWSelector(bpy.types.Panel):#メインパネル
    bl_label = "セレクタ"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.fjwselector

    def draw(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)

        layout = self.layout
        layout = layout.column(align=True)
        # active.operator("",icon="", text="")
        active = layout.row(align=True)


        # if bpy.context.visible_objects.active == bpy.context.scene.camera:
        #     if bpy.context.visible_objects.active.select:
        #便利ツール
        if bpy.context.scene.camera is not None:
            active = layout.row(align=True)
            active.label("")
            box = layout.box()
            box.label("Camera Prop")
            cam = bpy.context.scene.camera.data
            split = box.split()
            active = split.column(align=True)
            if hasattr(bpy.context.scene, "ct_dz_camera_lens"):
                active.label("dolly zoom")
                active.prop(bpy.context.scene, "ct_dz_camera_lens")
            active = split.column(align=True)
            active.label("焦点距離")
            active.prop(cam, "lens")

            split = box.split()
            col = split.column(align=True)
            col.label(text="Shift:")
            col.prop(cam, "shift_x", text="X")
            col.prop(cam, "shift_y", text="Y")

            col = split.column(align=True)
            col.label(text="Clipping:")
            col.prop(cam, "clip_start", text="Start")
            col.prop(cam, "clip_end", text="End")
            active = box.row(align=True)
            active.operator("object.setshift_to_cursor")
            active.operator("object.border_fromfile")
            active = box.row(align=True)
            active.operator("fujiwara_toolbox.command_990292")
            active.operator("object.set_resolution_to_bgimg")
            

            boxlayout = box.column(align=True)
            active = boxlayout.row(align=True)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.camera_work", icon="CAMERA_DATA")
            active.operator("fjw_selector.camera_work_look_at")
            active.prop(bpy.context.space_data, "lock_camera", icon="CAMERA_DATA", text="")
            active.prop(bpy.context.space_data, "show_only_render", icon="RESTRICT_RENDER_OFF", text="")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.camerawork_turntable", icon="CAMERA_DATA",)
            active.operator("fjw_selector.camera_unlock", icon="CAMERA_DATA",)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.current_view_to_camera", icon="CAMERA_DATA",)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.non_camera_work")
            active.operator("fjw_selector.non_camera_work_top")
            active.operator("fjw_selector.non_camera_work_right")


        active = layout.row(align=True)
        active.label("セレクタ")
        active = layout.row(align=True)
        active.operator("fjw_selector.select_camera", icon="CAMERA_DATA")
        active.operator("fjw_selector.select_sun", icon="LAMP_SUN")
        # active = layout.row(align=True)
        # active.operator("fjw_selector.select_mapcontroller", icon="OUTLINER_OB_ARMATURE")
        # active = layout.row(align=True)
        # active.label("3Dカーソル選択")
        # active = layout.row(align=True)
        # active.operator("fjw_selector.select_object_nearest_to_cursor")

        if fjw.active() and fjw.active().type == "ARMATURE":
            active = layout.row(align=True)
            active.label("ポージング")
            active = layout.row(align=True)
            active.operator("fjw_selector.prepare_for_posing", icon="POSE_HLT")
            active = layout.row(align=True)
            active.operator("fjw_selector.reset_pose", icon="POSE_HLT")
            active = layout.row(align=True)
            active.label("ポーズ閲覧")
            active = layout.row(align=True)
            active.operator("fjw_selector.load_pose_lib", icon="FILESEL")
            active = layout.row(align=True)
            active.operator("fjw_selector.brouse_pose", icon="POSE_HLT")
            active = layout.row(align=True)
            active.operator("fjw_selector.brouse_pose_face",icon="BONE_DATA")
            active = layout.row(align=True)
            active.operator("fjw_selector.brouse_pose_hand_r",icon="BONE_DATA")
            active.operator("fjw_selector.brouse_pose_hand_l",icon="BONE_DATA")
            active = layout.row(align=True)
            active.operator("fjw_selector.brouse_pose_arm_r",icon="BONE_DATA")
            active.operator("fjw_selector.brouse_pose_body",icon="POSE_HLT")
            active.operator("fjw_selector.brouse_pose_arm_l",icon="BONE_DATA")
            active = layout.row(align=True)
            active.operator("fjw_selector.brouse_pose_under_body",icon="BONE_DATA")
            active = layout.row(align=True)
            active.operator("fujiwara_toolbox.rigify_ik_all")
            active.operator("fujiwara_toolbox.rigify_fk_all")
        active = layout.row(align=True)
        active.label("")
        active = layout.row(align=True)
        active.operator("fjw_selector.set_face_lamp", icon="LAMP_POINT")
        active.operator("fjw_selector.set_hemi_lamp", icon="LAMP_HEMI")
        active.operator("fujiwara_toolbox.command_96315", icon="LAMP_SUN")

        active = layout.row()
        active.label("3Dカーソル付近選択")

        active = layout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_all",icon="GROUP_BONE")
        active.operator("fjw_selector.select_bone_nearest_to_cursor",icon="BONE_DATA")

        # if fjw.active() and fjw.active().type == "ARMATURE":
        if fjw.active() and "MapController" not in fjw.active().name:
            active = layout.row(align=True)
            active.label("人体", icon="OUTLINER_OB_ARMATURE")
            box = layout.box()
            boxlayout = box.column(align=True)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_eyetarget")
            active = boxlayout.row(align=True)
            active.label("右")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_eyetop_r")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_eyetop_l")
            active.label("左")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_pupil_r")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_pupil_l")
            active.label("")
            # active = boxlayout.row(align=True)
            # active.label("")
            # active.operator("fjw_selector.select_bone_nearest_to_cursor_eyebottom_r")
            # active.label("")
            # active.operator("fjw_selector.select_bone_nearest_to_cursor_eyebottom_l")
            # active.label("")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_mouth")
            active.label("")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_mouthbase")
            # active = boxlayout.row(align=True)
            # active.operator("fjw_selector.select_bone_nearest_to_cursor_face")
            active = boxlayout.row(align=True)
            active.label("右")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_head")
            active.label("")
            active.label("左")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_shoulder_r")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_neck")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_shoulder_l")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_elbow_r")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_chest")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_elbow_l")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_hand_r")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_spine")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_hand_l")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_body_master")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_knee_r")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_knee_l")
            active.label("")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_foot_r")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_foot_l")
            active.label("")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_geometry")

        # if fjw.active() and fjw.active().type == "ARMATURE":
        if fjw.active() and "MapController" in fjw.active().name:
            active = layout.row(align=True)
            active.label("マップ", icon="OUTLINER_OB_ARMATURE")
            box = layout.box()
            boxlayout = box.column(align=True)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_top")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_north")
            active.label("")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_west")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_east")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_south")
            active.label("")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_bottom")




############################################################################################################################
#ユーティリティ関数
############################################################################################################################

############################################################################################################################
############################################################################################################################
#各ボタンの実装
############################################################################################################################
############################################################################################################################
'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="fjw_selector.cls"
    bl_label = "ラベル"
    def execute(self,context):
        self.report({"INFO"},"")
        return {"FINISHED"}
'''

class Dummy(bpy.types.Operator):
    """説明"""
    bl_idname="fjw_selector.dummy"
    bl_label = ""
    def execute(self,context):
        return {"FINISHED"}


class SelectCamera(bpy.types.Operator):
    """カメラを選択する"""
    bl_idname="fjw_selector.select_camera"
    bl_label = "カメラ"
    def execute(self,context):
        fjw.deselect()
        camera = bpy.context.scene.camera
        if camera is not None:
            fjw.activate(camera)
        return {"FINISHED"}

class SelectSun(bpy.types.Operator):
    """SUNを選択する"""
    bl_idname="fjw_selector.select_sun"
    bl_label = "SUN"
    def execute(self,context):
        fjw.deselect()
        sun = None
        for obj in bpy.context.visible_objects:
            if obj.type == "LAMP":
                if "Sun" in obj.name:
                    sun = obj
                    fjw.activate(sun)
                    break

        return {"FINISHED"}

class CameraWork(bpy.types.Operator):
    """カメラワークをする。"""
    bl_idname="fjw_selector.camera_work"
    bl_label = "カメラワーク"
    def execute(self,context):
        # bpy.ops.view3d.viewnumpad(type='CAMERA')
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.space_data.lock_camera = True
        return {"FINISHED"}

class CameraWorkLookAt(bpy.types.Operator):
    """カメラワークをする。"""
    bl_idname="fjw_selector.camera_work_look_at"
    bl_label = "Emptyで注視"

    lookobj = None

    def execute(self,context):
        # bpy.ops.view3d.viewnumpad(type='CAMERA')
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.space_data.lock_camera = True

        cam = bpy.context.scene.camera
        lockstate = (cam.lock_rotation[0], cam.lock_rotation[1], cam.lock_rotation[2])
        cam.lock_rotation = (True, True, True)
        cursor = bpy.context.space_data.cursor_location
        if CameraWorkLookAt.lookobj is None:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=cursor, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            CameraWorkLookAt.lookobj = fjw.active()
            CameraWorkLookAt.lookobj.name = "LookPoint"
        CameraWorkLookAt.lookobj.location = cursor

        bpy.ops.view3d.view_selected()
        cam.lock_rotation = lockstate
        return {"FINISHED"}

class CameraWorkTurntable(bpy.types.Operator):
    """カメラの動きをターンテーブルに制限する。"""
    bl_idname="fjw_selector.camerawork_turntable"
    bl_label = "ターンテーブル"
    def execute(self,context):
        cam = bpy.context.scene.camera
        cam.lock_location = (False, False, True)
        cam.lock_rotation = (True, True, False)
        return {"FINISHED"}

class CameraUnlock(bpy.types.Operator):
    """カメラのロックを解除する。"""
    bl_idname="fjw_selector.camera_unlock"
    bl_label = "アンロック"
    def execute(self,context):
        cam = bpy.context.scene.camera
        cam.lock_location = (False, False, False)
        cam.lock_rotation = (False, False, False)
        return {"FINISHED"}

class CurrentViewToCamera(bpy.types.Operator):
    """カメラワークをする。"""
    bl_idname="fjw_selector.current_view_to_camera"
    bl_label = "現在の視点を採用"
    def execute(self,context):
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        # bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.space_data.lock_camera = False
        bpy.ops.view3d.camera_to_view()
        return {"FINISHED"}


class NonCameraWork(bpy.types.Operator):
    """ノンカメラワークをする。"""
    bl_idname="fjw_selector.non_camera_work"
    bl_label = "ノンカメラワーク"
    def execute(self,context):
        # bpy.ops.view3d.viewnumpad(type='CAMERA')
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        bpy.context.space_data.region_3d.view_perspective = "ORTHO"
        bpy.context.space_data.lock_camera = False
        return {"FINISHED"}

class NonCameraWorkTop(bpy.types.Operator):
    """ノンカメラワークをする。"""
    bl_idname="fjw_selector.non_camera_work_top"
    bl_label = "↑"
    def execute(self,context):
        bpy.ops.view3d.viewnumpad(type='TOP')
        bpy.context.space_data.lock_camera = False
        return {"FINISHED"}

class NonCameraWorkRight(bpy.types.Operator):
    """ノンカメラワークをする。"""
    bl_idname="fjw_selector.non_camera_work_right"
    bl_label = "→"
    def execute(self,context):
        bpy.ops.view3d.viewnumpad(type='RIGHT')
        bpy.context.space_data.lock_camera = False
        return {"FINISHED"}



class SelectMapController(bpy.types.Operator):
    """マップコントローラ"""
    bl_idname="fjw_selector.select_mapcontroller"
    bl_label = "マップコントローラ"
    def execute(self,context):
        fjw.deselect()
        mc = None
        for obj in bpy.context.visible_objects:
            if obj.type == "ARMATURE":
                if "MapController" in obj.name:
                    mc = obj
                    fjw.activate(mc)
                    fjw.mode("POSE")
                    break
        return {"FINISHED"}




def select_object_nearest_to_cursor(objects, namepattern=".*"):
    name_re = re.compile(namepattern, re.IGNORECASE)

    fjw.deselect()
    kdu = fjw.KDTreeUtils()
    for obj in objects:
        #名前でフィルタリング
        if name_re.search(obj.name) is None:
            continue
        loc = fjw.get_world_co(obj)
        data = [obj]
        kdu.append_data(loc, data)
    #ターゲットがなければ終了
    if len(kdu.items) == 0:
        return

    kdu.construct_kd_tree()
    result_data = kdu.find(bpy.context.space_data.cursor_location)
    kdu.finish()
    fjw.mode("OBJECT")
    fjw.activate(result_data[0])
    

class SelectObjectNearestToCursor(bpy.types.Operator):
    """3Dカーソルに一番近いオブジェクトを選択する"""
    bl_idname="fjw_selector.select_object_nearest_to_cursor"
    bl_label = "オブジェクト"
    def execute(self,context):
        select_object_nearest_to_cursor(bpy.context.visible_objects)
        return {"FINISHED"}

# def select_bone_nearest_to_cursor(objects, namepattern=".*"):
#     name_re = re.compile(namepattern, re.IGNORECASE)

#     fjw.deselect()
#     kdu = fjw.KDTreeUtils()
#     for obj in objects:
#         if obj.type != "ARMATURE":
#             continue
#         armu = fjw.ArmatureUtils(obj)

#         for pbone in armu.pose_bones:
#             if name_re.search(pbone.name) is None:
#                 continue
#             loc = armu.get_pbone_world_co(pbone.head)
#             data = [obj, pbone.name]
#             kdu.append_data(loc, data)

#         #ジオメトリ用処理
#         if namepattern == "geometry":
#             #人体判定
#             if "neck" in armu.pose_bones:
#                 gbone = armu.GetGeometryBone()
#                 if gbone is not None:
#                     loc = armu.get_pbone_world_co(gbone.head)
#                     data = [obj, gbone.name]
#                     kdu.append_data(loc, data)
                
#     #ターゲットがなければ終了
#     if len(kdu.items) == 0:
#         return

#     kdu.construct_kd_tree()
#     result_data = kdu.find(bpy.context.space_data.cursor_location)
#     kdu.finish()

#     obj = result_data[0]
#     bonename = result_data[1]
#     armu = fjw.ArmatureUtils(obj)
#     fjw.activate(obj)
#     fjw.mode("POSE")
#     armu.deselect()
#     armu.activate(armu.posebone(bonename))

def select_bone_nearest_to_cursor(objects, namelist):
    if type(namelist) == str:
        namelist = [namelist]

    fjw.deselect()
    kdu = fjw.KDTreeUtils()
    for obj in objects:
        if obj.type != "ARMATURE":
            continue
        armu = fjw.ArmatureUtils(obj)

        for pbone in armu.pose_bones:
            if pbone.name not in namelist:
                continue
            loc = armu.get_pbone_world_co(pbone.head)
            data = [obj, pbone.name]
            kdu.append_data(loc, data)

        #ジオメトリ用処理
        if namelist[0] == "geometry":
            #人体判定
            if "neck" in armu.pose_bones:
                gbone = armu.GetGeometryBone()
                if gbone is not None:
                    loc = armu.get_pbone_world_co(gbone.head)
                    data = [obj, gbone.name]
                    kdu.append_data(loc, data)
                
    #ターゲットがなければ終了
    if len(kdu.items) == 0:
        return

    kdu.construct_kd_tree()
    result_data = kdu.find(bpy.context.space_data.cursor_location)
    kdu.finish()

    obj = result_data[0]
    bonename = result_data[1]
    armu = fjw.ArmatureUtils(obj)
    fjw.activate(obj)
    fjw.mode("POSE")
    armu.deselect()
    armu.activate(armu.posebone(bonename))



class SelectBoneNearestToCursor(bpy.types.Operator):
    """カーソルに一番近いボーンを選択する"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor"
    bl_label = "ボーン"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects)
        return {"FINISHED"}


class SelectBoneNearestToCursor_Top(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_top"
    bl_label = "天"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "天")
        return {"FINISHED"}

class SelectBoneNearestToCursor_Bottom(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_bottom"
    bl_label = "地"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "地")
        return {"FINISHED"}

class SelectBoneNearestToCursor_North(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_north"
    bl_label = "北"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "北")
        return {"FINISHED"}

class SelectBoneNearestToCursor_South(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_south"
    bl_label = "南"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "南")
        return {"FINISHED"}

class SelectBoneNearestToCursor_East(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_east"
    bl_label = "東"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "東")
        return {"FINISHED"}

class SelectBoneNearestToCursor_West(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_west"
    bl_label = "西"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "西")
        return {"FINISHED"}


class SelectBoneNearestToCursor_All(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_all"
    bl_label = "全ボーン"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects)
        bpy.ops.pose.select_all(action='SELECT')
        return {"FINISHED"}


class PrepareForPosing(bpy.types.Operator):
    """AO無効化、簡略化オン、カメラロック解除、レンダのみ表示オフ。"""
    bl_idname = "fjw_selector.prepare_for_posing"
    bl_label = "ポージング準備"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.context.space_data.show_only_render = False
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 1
        bpy.context.space_data.lock_camera = False
        #全部のAO無効化する
        for screen in bpy.data.screens:
            for area in screen.areas:
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.fx_settings.use_ssao = False
        return {"FINISHED"}

class ResetPose(bpy.types.Operator):
    """ポーズのリセット"""
    bl_idname = "fjw_selector.reset_pose"
    bl_label = "ポーズリセット"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        obj = fjw.active()
        if obj.type != "ARMATURE":
            return {"CANCELLED"}

        for pb in obj.pose.bones:
            pb.location = (0.0,0.0,0.0)
            pb.scale = (1,1,1)
            pb.rotation_euler = (0.0,0.0,0.0)
            pb.rotation_quaternion = (1.0,0.0,0.0,0.0)
        
        return {"FINISHED"}

class LoadPoseLib(bpy.types.Operator):
    """選択アーマチュアに、アセットライブラリのposelibフォルダ内のblendファイルからポーズライブラリを取得して設定する。既に同名ライブラリがある場合はそれを設定する。"""
    bl_idname = "fjw_selector.load_pose_lib"
    bl_label = "load Poselib"
    bl_options = {'REGISTER', 'UNDO'}

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    filter_glob = StringProperty(default="*.blend", options={"HIDDEN"})

    def invoke(self, context, event):
        assetdir = fujiwara_toolbox.conf.get_pref().assetdir
        poselibdir = assetdir + os.sep + "poselib"
        if not os.path.exists(poselibdir):
            self.report({"WARNING"}, "%sがありません！"%poselibdir)
            return {'CANCELLED'}

        self.directory = poselibdir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        blendname = os.path.splitext(self.filename)[0]
        self.report({"INFO"},blendname)

        poselib = None
        for action in bpy.data.actions:
            if blendname == action.name:
                if action.library == None:
                    poselib = action
                    break
        
        if poselib is None:
            _dataname = blendname
            _filename = self.filename
            _filepath = self.filepath
            with bpy.data.libraries.load(_filepath, link=False, relative=True) as (data_from, data_to):
                if _dataname in data_from.actions:
                    data_to.actions = [_dataname]
            if len(data_to.actions) != 0:
                poselib = data_to.actions[0]
        
        if poselib is not None:
            selection = fjw.get_selected_list()
            for obj in selection:
                if obj.type == "ARMATURE":
                    obj.pose_library = poselib
        return {"FINISHED"}



# class LoadPoseLib(bpy.types.Operator):
#     """選択アーマチュアに、アセットライブラリのposelibフォルダ内のblendファイルからポーズライブラリを取得して設定する。既に同名ライブラリがある場合はそれを設定する。"""
#     bl_idname = "fjw_selector.load_pose_lib"
#     bl_label = "load Poselib"
#     bl_options = {'REGISTER', 'UNDO'}

#     poselibdir = ""

#     def get_blend_list_callback(self,context):
#         items=[]
#         if LoadPoseLib.poselibdir == "":
#             assetdir = fujiwara_toolbox.conf.get_pref().assetdir
#             LoadPoseLib.poselibdir = assetdir + os.sep + "poselib"
#             LoadPoseLib.libexists = os.path.exists(LoadPoseLib.poselibdir)

#         if not LoadPoseLib.libexists:
#             return [("None","Pose Dir Not Found.","")]

#         files = os.listdir(LoadPoseLib.poselibdir)
#         if len(files) == 0:
#             return [("None","Blend FIle Not Found.","")]
        
#         items.append(("テスト","テスト",""))
#         items.append((u"テスト",u"テスト",""))

#         # import chardet
#         for filename in files:
#             # パスの日本語化うまくいってない！
#             #https://qiita.com/inoory/items/aafe79384dbfcc0802cf
#             #http://lab.hde.co.jp/2008/08/pythonunicodeencodeerror.html
#             #http://d.hatena.ne.jp/Cassiopeia/20070602/1180805345
#             filename = str(filename).encode("cp932").decode("utf-8", errors="replace").encode()
#             print(filename)

#             name,ext = os.path.splitext(filename)
#             if ext == ".blend":
#                 items.append((name,name,""))

#         return items

#     blend_list = EnumProperty(
#         name = "Blend List",               # 名称
#         description = "Blend List",        # 説明文
#         items = get_blend_list_callback)   # 項目リストを作成する関数

#     def invoke(self, context, event):
#         return context.window_manager.invoke_props_dialog(self)

#     def execute(self, context):
#         blendname = self.blend_list
#         self.report({"INFO"},blendname)

#         poselib = None
#         for action in bpy.data.actions:
#             if blendname == action.name:
#                 if action.library == None:
#                     poselib = action
#                     break
        
#         if poselib is None:
#             _dataname = blendname
#             _filename = blendname + ".blend"
#             _filepath = LoadPoseLib.poselibdir + os.sep + _filename
#             with bpy.data.libraries.load(_filepath, link=False, relative=True) as (data_from, data_to):
#                 if _dataname in data_from.actions:
#                     data_to.actions = [_dataname]
#             if len(data_to.actions) != 0:
#                 poselib = data_to.actions[0]
        
#         if poselib is not None:
#             selection = fjw.get_selected_list()
#             for obj in selection:
#                 if obj.type == "ARMATURE":
#                     obj.pose_library = poselib
#         return {"FINISHED"}


class BrousePose(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose"
    bl_label = "全身 / 選択部"
    def execute(self, context):
        armature = fjw.active()
        if armature.type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください。")
            return {"CANCELLED"}

        if armature.mode != "POSE":
            fjw.mode("POSE")
            bpy.ops.pose.select_all(action='SELECT')

        armu = fjw.ArmatureUtils(armature)
        geobone = armu.GetGeometryBone()
        if geobone is not None:
            geobone = armu.databone(geobone.name)
            geobone.select = False

        bpy.ops.poselib.browse_interactive("INVOKE_DEFAULT")
        return {"FINISHED"}

def select_pbones_bynamelist(namelist, obj):
    for pbone in obj.pose.bones:
        if pbone.name in namelist:
            pbone.bone.select = True

def brouse_pose_bynamelist(self, namelist):
    armature = fjw.active()
    if armature.type != "ARMATURE":
        self.report({"INFO"},"アーマチュアを選択してください。")
        return {"CANCELLED"}

    fjw.mode("POSE")

    bpy.ops.pose.select_all(action='DESELECT')
    select_pbones_bynamelist(namelist, armature)
    bpy.ops.fjw_selector.brouse_pose()

class BoursePoseFace(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_face"
    bl_label = "顔"
    def execute(self, context):
        namelist = ["master_eye.L", "brow.B.L", "brow.B.L.004", "lid.B.L", "lid.T.L", "master_eye.R", "brow.B.R", "brow.B.R.004", "lid.B.R", "lid.T.R", "ear.L", "ear.L.002", "ear.L.004", "ear.L.003", "ear.R", "ear.R.002", "ear.R.004", "ear.R.003", "jaw_master", "teeth.B", "tongue_master", "tongue", "chin", "chin.001", "chin.L", "chin.R", "jaw", "jaw.L.001", "jaw.R.001", "tongue.003", "tongue.001", "tongue.002", "teeth.T", "brow.T.L", "brow.T.L.001", "brow.T.L.003", "brow.T.L.002", "brow.B.L.002", "brow.B.L.003", "brow.B.L.001", "brow.T.R", "brow.T.R.001", "brow.T.R.003", "brow.T.R.002", "brow.B.R.002", "brow.B.R.003", "brow.B.R.001", "jaw.L", "jaw.R", "nose", "lip.B", "chin.002", "lips.L", "lip.B.L.001", "cheek.B.L.001", "lips.R", "lip.B.R.001", "cheek.B.R.001", "lip.T", "nose.005", "lip.T.R.001", "lip.T.L.001", "nose_master", "nose.002", "nose.001", "nose.003", "nose.004", "nose.L.001", "nose.R.001", "cheek.T.L.001", "cheek.T.R.001", "nose.R", "nose.L", "eyes", "eye.L", "lid.B.L.002", "lid.B.L.001", "lid.B.L.003", "lid.T.L.002", "lid.T.L.001", "lid.T.L.003", "eye.R", "lid.B.R.002", "lid.B.R.001", "lid.B.R.003", "lid.T.R.002", "lid.T.R.001", "lid.T.R.003"]
        brouse_pose_bynamelist(self,namelist)
        
        return {"FINISHED"}

class BoursePoseHandR(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_hand_r"
    bl_label = "右手"
    def execute(self, context):
        namelist = ["hand_ik.R", "palm.R", "f_index.01.R", "f_index.02.R", "tweak_f_index.02.R", "f_index.03.R", "tweak_f_index.03.R", "tweak_f_index.03.R.001", "tweak_f_index.01.R", "thumb.01.R", "thumb.02.R", "tweak_thumb.02.R", "thumb.03.R", "tweak_thumb.03.R", "tweak_thumb.03.R.001", "tweak_thumb.01.R", "f_middle.01.R", "f_middle.02.R", "tweak_f_middle.02.R", "f_middle.03.R", "tweak_f_middle.03.R", "tweak_f_middle.03.R.001", "tweak_f_middle.01.R", "f_ring.01.R", "f_ring.02.R", "tweak_f_ring.02.R", "f_ring.03.R", "tweak_f_ring.03.R", "tweak_f_ring.03.R.001", "tweak_f_ring.01.R", "f_pinky.01.R", "f_pinky.02.R", "tweak_f_pinky.02.R", "f_pinky.03.R", "tweak_f_pinky.03.R", "tweak_f_pinky.03.R.001", "tweak_f_pinky.01.R", ]
        brouse_pose_bynamelist(self,namelist)
        
        return {"FINISHED"}

class BoursePoseHandL(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_hand_l"
    bl_label = "左手"
    def execute(self, context):
        namelist = ["palm.L", "f_index.01.L", "f_index.02.L", "tweak_f_index.02.L", "f_index.03.L", "tweak_f_index.03.L", "tweak_f_index.03.L.001", "tweak_f_index.01.L", "thumb.01.L", "thumb.02.L", "tweak_thumb.02.L", "thumb.03.L", "tweak_thumb.03.L", "tweak_thumb.03.L.001", "tweak_thumb.01.L", "f_middle.01.L", "f_middle.02.L", "tweak_f_middle.02.L", "f_middle.03.L", "tweak_f_middle.03.L", "tweak_f_middle.03.L.001", "tweak_f_middle.01.L", "f_ring.01.L", "f_ring.02.L", "tweak_f_ring.02.L", "f_ring.03.L", "tweak_f_ring.03.L", "tweak_f_ring.03.L.001", "tweak_f_ring.01.L", "f_pinky.01.L", "f_pinky.02.L", "tweak_f_pinky.02.L", "f_pinky.03.L", "tweak_f_pinky.03.L", "tweak_f_pinky.03.L.001", "tweak_f_pinky.01.L", ]
        brouse_pose_bynamelist(self,namelist)

        return {"FINISHED"}

class BoursePoseBody(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_body"
    bl_label = "ボディ全体"
    def execute(self, context):
        namelist = ["torso", "chest", "tweak_spine.003", "ORG-spine.003", "breast.L", "ORG-breast.L", "breast.R", "ORG-breast.R", "shoulder.L", "ORG-shoulder.L", "shoulder.R", "ORG-shoulder.R", "neck", "tweak_spine.004", "ORG-spine.004", "head", "tweak_spine.005", "ORG-spine.005", "ORG-spine.006", "ORG-face", "ORG-lip.T.L", "ORG-lip.B.L", "ORG-ear.L", "ORG-ear.L.001", "ORG-ear.R", "ORG-ear.R.001", "ORG-lip.T.R", "ORG-lip.B.R", "ORG-forehead.L", "ORG-forehead.L.001", "ORG-forehead.L.002", "ORG-temple.L", "ORG-cheek.B.L", "ORG-forehead.R", "ORG-forehead.R.001", "ORG-forehead.R.002", "ORG-temple.R", "ORG-cheek.B.R", "ORG-cheek.T.L", "ORG-cheek.T.R", "ORG-brow.B.L", "ORG-lid.B.L", "ORG-lid.T.L", "ORG-brow.B.R", "ORG-lid.B.R", "ORG-lid.T.R", "ORG-ear.L.002", "ORG-ear.L.004", "ORG-ear.L.003", "ORG-ear.R.002", "ORG-ear.R.004", "ORG-ear.R.003", "ORG-tongue", "ORG-chin", "ORG-chin.001", "ORG-chin.L", "ORG-chin.R", "ORG-jaw", "ORG-jaw.L.001", "ORG-jaw.R.001", "ORG-tongue.001", "ORG-tongue.002", "ORG-teeth.B", "ORG-teeth.T", "ORG-brow.T.L", "ORG-brow.T.L.001", "ORG-brow.T.L.003", "ORG-brow.B.L.003", "ORG-brow.B.L.002", "ORG-brow.B.L.001", "ORG-brow.T.L.002", "ORG-brow.T.R", "ORG-brow.T.R.001", "ORG-brow.T.R.003", "ORG-brow.B.R.003", "ORG-brow.B.R.002", "ORG-brow.B.R.001", "ORG-brow.T.R.002", "ORG-jaw.L", "ORG-jaw.R", "ORG-nose", "ORG-lip.B.L.001", "ORG-cheek.B.L.001", "ORG-lip.B.R.001", "ORG-cheek.B.R.001", "ORG-lip.T.R.001", "ORG-lip.T.L.001", "ORG-nose.002", "ORG-nose.001", "ORG-nose.003", "ORG-nose.004", "ORG-nose.L.001", "ORG-nose.R.001", "ORG-cheek.T.L.001", "ORG-cheek.T.R.001", "ORG-nose.R", "ORG-nose.L", "hips", "tweak_spine.002", "ORG-spine.002", "tweak_spine", "ORG-spine", "ORG-pelvis.L", "ORG-pelvis.R", "tweak_spine.001", "ORG-spine.001", "upper_arm_fk.L", "forearm_fk.L", "hand_fk.L", "upper_arm_fk.R", "forearm_fk.R", "hand_fk.R", "thigh_fk.L", "shin_fk.L", "foot_fk.L", "thigh_fk.R", "shin_fk.R", "foot_fk.R", "ORG-lid.B.L.002", "ORG-lid.B.L.001", "ORG-lid.B.L.003", "ORG-lid.T.L.003", "ORG-lid.T.L.002", "ORG-lid.T.L.001", "ORG-eye.L", "ORG-lid.B.R.002", "ORG-lid.B.R.001", "ORG-lid.B.R.003", "ORG-lid.T.R.003", "ORG-lid.T.R.002", "ORG-lid.T.R.001", "ORG-eye.R", "foot_ik.L", "foot_heel_ik.L", "thigh_ik.L", "ORG-thigh.L", "thigh_parent.L", "thigh_tweak.L", "ORG-shin.L", "shin_tweak.L", "thigh_tweak.L.001", "ORG-foot.L", "ORG-heel.02.L", "foot_tweak.L", "toe.L", "ORG-toe.L", "shin_tweak.L.001", "foot_ik.R", "foot_heel_ik.R", "thigh_ik.R", "ORG-thigh.R", "thigh_parent.R", "thigh_tweak.R", "ORG-shin.R", "shin_tweak.R", "thigh_tweak.R.001", "ORG-foot.R", "ORG-heel.02.R", "foot_tweak.R", "toe.R", "ORG-toe.R", "shin_tweak.R.001", "hand_ik.L", "upper_arm_ik.L", "ORG-upper_arm.L", "upper_arm_parent.L", "upper_arm_tweak.L", "ORG-forearm.L", "forearm_tweak.L", "upper_arm_tweak.L.001", "ORG-hand.L", "hand_tweak.L", "forearm_tweak.L.001", "ORG-palm.01.L", "ORG-f_index.02.L", "ORG-f_index.03.L", "ORG-f_index.01.L", "ORG-thumb.02.L", "ORG-thumb.03.L", "ORG-thumb.01.L", "ORG-palm.02.L", "ORG-f_middle.02.L", "ORG-f_middle.03.L", "ORG-f_middle.01.L", "ORG-palm.03.L", "ORG-f_ring.02.L", "ORG-f_ring.03.L", "ORG-f_ring.01.L", "ORG-palm.04.L", "ORG-f_pinky.02.L", "ORG-f_pinky.03.L", "ORG-f_pinky.01.L", "hand_ik.R", "upper_arm_ik.R", "ORG-upper_arm.R", "upper_arm_parent.R", "upper_arm_tweak.R", "ORG-forearm.R", "forearm_tweak.R", "upper_arm_tweak.R.001", "ORG-hand.R", "hand_tweak.R", "forearm_tweak.R.001", "ORG-palm.01.R", "ORG-f_index.02.R", "ORG-f_index.03.R", "ORG-f_index.01.R", "ORG-thumb.02.R", "ORG-thumb.03.R", "ORG-thumb.01.R", "ORG-palm.02.R", "ORG-f_middle.02.R", "ORG-f_middle.03.R", "ORG-f_middle.01.R", "ORG-palm.03.R", "ORG-f_ring.02.R", "ORG-f_ring.03.R", "ORG-f_ring.01.R", "ORG-palm.04.R", "ORG-f_pinky.02.R", "ORG-f_pinky.03.R", "ORG-f_pinky.01.R", ]
        brouse_pose_bynamelist(self,namelist)

        return {"FINISHED"}

class BoursePoseArmR(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_arm_r"
    bl_label = "右腕"
    def execute(self, context):
        namelist = ["upper_arm_fk.R", "forearm_fk.R", "hand_fk.R", "hand_ik.R", "upper_arm_ik.R", "upper_arm_parent.R", "upper_arm_tweak.R", "forearm_tweak.R", "upper_arm_tweak.R.001", "hand_tweak.R", "forearm_tweak.R.001", ]
        brouse_pose_bynamelist(self,namelist)

        return {"FINISHED"}

class BoursePoseArmL(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_arm_l"
    bl_label = "左腕"
    def execute(self, context):
        namelist = ["upper_arm_fk.L", "forearm_fk.L", "hand_fk.L", "hand_ik.L", "upper_arm_ik.L", "upper_arm_parent.L", "upper_arm_tweak.L", "forearm_tweak.L", "upper_arm_tweak.L.001", "hand_tweak.L", "forearm_tweak.L.001", ]
        brouse_pose_bynamelist(self,namelist)

        return {"FINISHED"}

class BoursePoseUnderBody(bpy.types.Operator):
    """ポーズを閲覧する。非ポーズモードの場合、ポーズモードに入ってジオメトリ以外に適用する。ポーズモードの場合ジオメトリ以外の選択ボーンに適用する。"""
    bl_idname = "fjw_selector.brouse_pose_under_body"
    bl_label = "下半身"
    def execute(self, context):
        namelist = ["torso", "tweak_spine", "thigh_fk.L", "shin_fk.L", "foot_fk.L", "thigh_fk.R", "shin_fk.R", "foot_fk.R", "foot_ik.L", "foot_heel_ik.L", "thigh_ik.L", "thigh_tweak.L", "shin_tweak.L", "thigh_tweak.L.001", "foot_tweak.L", "toe.L", "shin_tweak.L.001", "foot_ik.R", "foot_heel_ik.R", "thigh_ik.R", "thigh_tweak.R", "shin_tweak.R", "thigh_tweak.R.001", "foot_tweak.R", "toe.R", "shin_tweak.R.001", ]
        brouse_pose_bynamelist(self,namelist)

        return {"FINISHED"}


class SetFaceLamp(bpy.types.Operator):
    """顔用ランプ設置"""
    bl_idname = "fjw_selector.set_face_lamp"
    bl_label = "顔用ランプ設置"
    def execute(self, context):
        fjw.mode("OBJECT")
        bpy.ops.object.lamp_add(type='POINT', radius=0.2, view_align=True, location=bpy.context.space_data.cursor_location, layers=bpy.context.scene.layers)
        bpy.context.object.data.use_specular = False
        bpy.context.object.data.distance = 0.2
        return {"FINISHED"}

class SetHemiLamp(bpy.types.Operator):
    """ヘミランプ設置"""
    bl_idname = "fjw_selector.set_hemi_lamp"
    bl_label = "ヘミランプ設置"
    def execute(self, context):
        fjw.mode("OBJECT")
        bpy.ops.object.lamp_add(type='HEMI', radius=0.2, view_align=True, location=bpy.context.space_data.cursor_location, layers=bpy.context.scene.layers)
        bpy.context.object.data.use_specular = False
        bpy.context.object.data.energy = 0.07
        return {"FINISHED"}

def show_projector():
    armature = fjw.active()
    armu = fjw.ArmatureUtils(armature)
    bone = armu.poseactive()
    #boneを親にしてるオブジェクトを取得
    target = None
    for obj in armature.children:
        if obj.parent_bone == bone.name:
            target = obj
            break
    #オブジェクトに視点をあわせる
    fjw.mode("OBJECT")
    fjw.deselect()
    fjw.activate(target)
    bpy.ops.view3d.viewnumpad(type="TOP", align_active=True)

    #そのオブジェクトを注視
    bpy.ops.view3d.view_selected(use_all_regions=False)

    #あらためてアーマチュアをアクティブに
    fjw.activate(armature)
    fjw.mode("POSE")

#人体ボーン選択
class SelectBoneNearestToCursor_Eyetarget(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetarget"
    bl_label = "視線"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["Eyetarget","eyetarget", "eyes"])
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyetopR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetop_r"
    bl_label = "眉毛"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["Projector_Eyebrow_R","eyetop_r", "lid.T.R.002"])
        show_projector()
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyetopL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetop_l"
    bl_label = "眉毛"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["Projector_Eyebrow_L","eyetop_l","lid.T.L.002"])
        show_projector()
        return {"FINISHED"}

class SelectBoneNearestToCursor_PupilR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_pupil_r"
    bl_label = "目"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["Projector_Eyelid_R","pupil_r", "master_eye.R"])
        show_projector()
        return {"FINISHED"}

class SelectBoneNearestToCursor_PupilL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_pupil_l"
    bl_label = "目"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["Projector_Eyelid_L","pupil_l", "master_eye.L"])
        show_projector()
        return {"FINISHED"}


class SelectBoneNearestToCursor_EyebottomR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyebottom_r"
    bl_label = "下"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["eyebottom_r","lid.B.R.002"])
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyebottomL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyebottom_l"
    bl_label = "下"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["eyebottom_l","lid.B.L.002"])
        return {"FINISHED"}


class SelectBoneNearestToCursor_Geometry(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_geometry"
    bl_label = "ジオメトリ"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "geometry")
        return {"FINISHED"}

class SelectBoneNearestToCursor_Mouth(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_mouth"
    bl_label = "口"
    def execute(self,context):
        namelist = ["Projector_Mouth" ,"teeth.B", "tongue", "chin.001", "tongue.001", "teeth.T", "DEF-forehead.L.002", "lip.B", "chin.002", "lips.L", "lip.B.L.001", "lips.R", "lip.B.R.001", "lip.T", "nose.005", "lip.T.R.001", "lip.T.L.001", ]
        # select_bone_nearest_to_cursor(bpy.context.visible_objects, "head")
        # bpy.ops.pose.select_all(action='DESELECT')
        # for bone in fjw.active().pose.bones:
        #     if bone.name in namelist:
        #         bone.bone.select = True
        select_bone_nearest_to_cursor(bpy.context.visible_objects, namelist)
        show_projector()
        return {"FINISHED"}

class SelectBoneNearestToCursor_MouthBase(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_mouthbase"
    bl_label = "口ベース"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["Mouth"])
        return {"FINISHED"}


class SelectBoneNearestToCursor_Face(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_face"
    bl_label = "顔"
    def execute(self,context):
        namelist = ["master_eye.L", "brow.B.L", "brow.B.L.004", "lid.B.L", "lid.T.L", "master_eye.R", "brow.B.R", "brow.B.R.004", "lid.B.R", "lid.T.R", "teeth.B", "tongue_master", "tongue", "chin.001", "tongue.001", "teeth.T", "brow.T.L", "brow.T.L.001", "brow.T.L.003", "brow.T.L.002", "brow.B.L.002", "brow.B.L.001", "brow.B.L.003", "brow.T.R", "brow.T.R.001", "brow.T.R.003", "brow.T.R.002", "brow.B.R.002", "brow.B.R.001", "brow.B.R.003", "nose", "lip.B", "chin.002", "lips.L", "lip.B.L.001", "cheek.B.L.001", "lips.R", "lip.B.R.001", "cheek.B.R.001", "lip.T", "nose.005", "lip.T.R.001", "lip.T.L.001", "nose_master", "nose.002", "nose.001", "nose.003", "nose.004", "nose.L.001", "nose.R.001", "cheek.T.L.001", "cheek.T.R.001", "nose.R", "nose.L", "lid.T.L.002", "lid.T.L.003", "lid.T.L.001", "lid.B.L.002", "lid.B.L.003", "lid.B.L.001", "lid.T.R.002", "lid.T.R.003", "lid.T.R.001", "lid.B.R.002", "lid.B.R.003", "lid.B.R.001", ]
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "head")
        bpy.ops.pose.select_all(action='DESELECT')
        for bone in fjw.active().pose.bones:
            if bone.name in namelist:
                bone.bone.select = True
        return {"FINISHED"}

class SelectBoneNearestToCursor_Head(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_head"
    bl_label = "頭"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "head")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Neck(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_neck"
    bl_label = "首"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "neck")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Chest(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_chest"
    bl_label = "胸"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "chest")
        return {"FINISHED"}
class SelectBoneNearestToCursor_BodyMaster(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_body_master"
    bl_label = "ボディ親"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["ボディ親","torso"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_Spine(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_spine"
    bl_label = "腰"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["spine","hips"])
        return {"FINISHED"}


#腕・脚
class SelectBoneNearestToCursor_ShoulderR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_shoulder_r"
    bl_label = "肩"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["肩\.R", "shoulder.R"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_ShoulderL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_shoulder_l"
    bl_label = "肩"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["肩\.L","shoulder.L"])
        return {"FINISHED"}

class SelectBoneNearestToCursor_ElbowR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_elbow_r"
    bl_label = "肘"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["肘\.R","upper_arm_ik.R"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_ElbowL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_elbow_l"
    bl_label = "肘"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["肘\.L","upper_arm_ik.L"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_HandR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_hand_r"
    bl_label = "手"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["腕\.R","hand_ik.R"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_HandL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_hand_l"
    bl_label = "手"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["腕\.L","hand_ik.L"])
        return {"FINISHED"}


class SelectBoneNearestToCursor_KneeR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_knee_r"
    bl_label = "膝"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["脚\.R","thigh_ik.R"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_KneeL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_knee_l"
    bl_label = "膝"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["脚\.L","thigh_ik.L"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_FootR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_foot_r"
    bl_label = "足"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["足\.R", "foot_ik.R"])
        return {"FINISHED"}
class SelectBoneNearestToCursor_FootL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_foot_l"
    bl_label = "足"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, ["足\.L", "foot_ik.L"])
        return {"FINISHED"}



############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    pass

def sub_unregistration():
    pass


def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)
    sub_unregistration()

if __name__ == "__main__":
    register()