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

from bpy.app.handlers import persistent

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf

bl_info = {
    "name": "FJW",
    "description": "",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}



#メインパネル
class FJWBillboadDrawer(bpy.types.Panel):#メインパネル
    bl_label = "描画ツール"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.draw_tools

    def draw(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)

        layout = self.layout
        layout = layout.column(align=True)

        active = layout.row(align=True)
        active.label("加筆用カーブ")
        active = layout.row(align=True)
        active.operator("fjw_billboard_drawer.curve_black",icon="NONE")
        active.operator("fjw_billboard_drawer.curve_white",icon="NONE")
        active = layout.row(align=True)
        active.label("ユーティリティ")
        active = layout.row(align=True)
        active.operator("fjw_billboard_drawer.dissolve_active_spline",icon="NONE")

        active = layout.row(align=True)
        active.label("ビルボード描画")
        active = layout.row(align=True)
        # active.operator("fjw_billboard_drawer.add_bd128")
        # active.operator("fjw_billboard_drawer.add_bd256")
        active.operator("fjw_billboard_drawer.add_bd512",icon="IMAGE_DATA")
        active.operator("fjw_billboard_drawer.add_bd1024",icon="IMAGE_DATA")
        active = layout.row(align=True)
        active.operator("fjw_billboard_drawer.draw_brush",icon="GREASEPENCIL")
        active.operator("fjw_billboard_drawer.erase_brush",icon="TEXTURE_SHADED")
        active = layout.row(align=True)
        active.operator("fjw_billboard_drawer.save_images", icon="FILE_TICK")


'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="fjw_billboard_drawer.cls"
    bl_label = "ラベル"
    def execute(self,context):
        self.report({"INFO"},"")
        return {"FINISHED"}
'''

#ビルボード生成
def make_buillboard(width, height):
    loc = bpy.context.space_data.cursor_location
    bpy.ops.mesh.primitive_plane_add(radius=1, view_align=True, location=loc, layers=bpy.context.scene.layers)
    billboard = fjw.active()
    billboard.name = "ビルボード描画"

    fjw.mode("EDIT")
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    fjw.mode("OBJECT")

    mat = bpy.data.materials.new("ビルボード描画")
    mat.use_shadeless = True
    mat.use_transparency = True
    mat.alpha = 0.0
    mat.use_cast_shadows = False
    mat.use_shadows = False
    tslot = mat.texture_slots.add()
    tslot.use_map_alpha = True
    tex = bpy.data.textures.new("ビルボード描画","IMAGE")
    img = bpy.data.images.new("ビルボード描画", width, height, alpha=True)
    img.generated_color = (0,0,0,0)
    tex.image = img
    tslot.texture = tex
    billboard.data.materials.append(mat)

    scale = 1024*2
    dim_x = width/scale
    dim_y = height/scale

    billboard.scale.x = dim_x / 2
    billboard.scale.y = dim_y / 2
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.context.space_data.viewport_shade = 'MATERIAL'

    return billboard



class ADD_BILLBOARD_128(bpy.types.Operator):
    """128*128のドロー用ビルボードを作成する"""
    bl_idname="fjw_billboard_drawer.add_bd128"
    bl_label = "128"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        make_buillboard(128,128)
        return {"FINISHED"}

class ADD_BILLBOARD_256(bpy.types.Operator):
    """256*256のドロー用ビルボードを作成する"""
    bl_idname="fjw_billboard_drawer.add_bd256"
    bl_label = "256"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        make_buillboard(256,256)
        return {"FINISHED"}

class ADD_BILLBOARD_512(bpy.types.Operator):
    """512*512のドロー用ビルボードを作成する"""
    bl_idname="fjw_billboard_drawer.add_bd512"
    bl_label = "512"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        make_buillboard(512,512)
        return {"FINISHED"}

class ADD_BILLBOARD_1024(bpy.types.Operator):
    """1024*1024のドロー用ビルボードを作成する"""
    bl_idname="fjw_billboard_drawer.add_bd1024"
    bl_label = "1024"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        make_buillboard(1024,1024)
        return {"FINISHED"}


def get_brush(brush_name):
    if brush_name not in bpy.data.brushes:
        brush = bpy.data.brushes.new(brush_name, mode="TEXTURE_PAINT")
    else:
        brush = bpy.data.brushes[brush_name]
    return brush

class DRAW_BRUSH(bpy.types.Operator):
    """描画ブラシ"""
    bl_idname="fjw_billboard_drawer.draw_brush"
    bl_label = "描き"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        fjw.mode("TEXTURE_PAINT")

        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_size = False
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_strength = False
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_color = False

        brush = get_brush("描画ブラシ")
        brush.color = (0,0,0)
        brush.size = 3
        brush.use_pressure_size = True
        brush.use_pressure_strength = False
        brush.strength = 1
        brush.blend = 'MIX'

        bpy.context.scene.tool_settings.image_paint.brush = brush

        fjw.active().show_wire = True

        return {"FINISHED"}

class ERASE_BRUSH(bpy.types.Operator):
    """消去ブラシ"""
    bl_idname="fjw_billboard_drawer.erase_brush"
    bl_label = "消し"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        fjw.mode("TEXTURE_PAINT")

        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_size = False
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_strength = False
        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_color = False

        brush = get_brush("消去ブラシ")
        brush.size = 15
        brush.use_pressure_size = True
        brush.use_pressure_strength = False
        brush.strength = 1
        brush.blend = 'ERASE_ALPHA'

        bpy.context.scene.tool_settings.image_paint.brush = brush

        fjw.active().show_wire = True
        return {"FINISHED"}

class SAVE_IMAGES(bpy.types.Operator):
    """画像保存"""
    bl_idname="fjw_billboard_drawer.save_images"
    bl_label = "保存"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        for img in bpy.data.images:
            if img.is_dirty:
                img.pack(as_png=True)

        for obj in bpy.context.visible_objects:
            obj.show_wire = False

        fjw.mode("OBJECT")
        return {"FINISHED"}


def add_drawing_curve(name, color, bvel_depth):
    bpy.context.scene.tool_settings.curve_paint_settings.curve_type = 'POLY'
    bpy.context.scene.tool_settings.curve_paint_settings.use_pressure_radius = True
    bpy.context.scene.tool_settings.curve_paint_settings.radius_min = 0
    bpy.context.scene.tool_settings.curve_paint_settings.radius_max = 1
    bpy.context.scene.tool_settings.curve_paint_settings.depth_mode = 'SURFACE'
    bpy.context.scene.tool_settings.curve_paint_settings.surface_offset = 1
    bpy.context.scene.tool_settings.curve_paint_settings.use_offset_absolute = False
    bpy.context.scene.tool_settings.curve_paint_settings.use_stroke_endpoints = False

    for obj in bpy.context.visible_objects:
        if name in obj.name:
            return obj

    bpy.ops.curve.primitive_bezier_curve_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=bpy.context.scene.layers)
    curve = fjw.active().data
    fjw.active().name = name
    curve.fill_mode = "FULL"
    curve.bevel_depth = bvel_depth

    curve.show_handles = False
    curve.show_normal_face = False

    mat = bpy.data.materials.new(name)
    mat.use_shadeless = True
    mat.diffuse_color = color
    mat.use_cast_shadows = False
    curve.materials.append(mat)

    fjw.mode("EDIT")
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.dissolve_verts()
    fjw.mode("OBJECT")

    return fjw.active()

class CURVE_BLACK(bpy.types.Operator):
    """加筆用の黒カーブ"""
    bl_idname="fjw_billboard_drawer.curve_black"
    bl_label = "黒カーブ"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        if bpy.context.scene.render.use_simplify:
            bpy.context.scene.render.use_simplify = False
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.lock_camera = False

        fjw.mode("OBJECT")
        curve_obj = add_drawing_curve("加筆カーブ黒", (0,0,0), 0.001)
        fjw.activate(curve_obj)
        fjw.mode("EDIT")
        return {"FINISHED"}

class CURVE_WHITE(bpy.types.Operator):
    """加筆用の白カーブ"""
    bl_idname="fjw_billboard_drawer.curve_white"
    bl_label = "白カーブ"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        if bpy.context.scene.render.use_simplify:
            bpy.context.scene.render.use_simplify = False
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.lock_camera = False

        fjw.mode("OBJECT")
        curve_obj = add_drawing_curve("加筆カーブ白", (1,1,1), 0.003)
        fjw.activate(curve_obj)
        fjw.mode("EDIT")
        return {"FINISHED"}

class DISSOLVE_ACTIVE_SPLINE(bpy.types.Operator):
    """アクティブスプラインの頂点数を半分に溶解する。"""
    bl_idname="fjw_billboard_drawer.dissolve_active_spline"
    bl_label = "半分に溶解"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self,context):
        obj = fjw.active()
        if obj is None or obj.type != "CURVE" or obj.mode != "EDIT":
            return {"CANCELLED"}

        curve = obj.data
        spline = curve.splines.active
        if spline is None:
            return {"CANCELLED"}

        for p in spline.points:
            p.select = False

        #交互に選択
        select = False
        for p in spline.points:
            p.select = select
            select = not select

        spline.points[0].select = False
        spline.points[-1].select = False
        bpy.ops.curve.dissolve_verts()

        for p in spline.points:
            p.select = True
        curve.splines.active = spline

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