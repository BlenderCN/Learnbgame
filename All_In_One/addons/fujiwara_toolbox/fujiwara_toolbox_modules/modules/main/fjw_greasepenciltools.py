import bpy
import os
import re
import math

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf

bl_info = {
    "name": "FJW GreasePencilTools",
    "author": "GhostBrain3dex",
    "version": (1.0),
    "blender": (2, 77, 0),
    'location': '',
    "description": "GreasePencilTools",
    "category": "Object",
}



uiitemList = []
class uiitem():
    type = "button"
    idname = ""
    label = ""
    icon = ""
    mode = ""
    #ボタンの表示方向
    direction = ""
    
    #宣言時自動登録
    def __init__(self,label=""):
        global uiitemList
        uiitemList.append(self)
        
        if label != "":
            self.type = "label"
            self.label = label
    
    #簡易セットアップ
    def button(self,idname,label,icon,mode):
        self.idname = idname
        self.label = label
        self.icon = icon
        self.mode = mode
        return

    #フィックス用
    def vertical(self):
        self.type = "fix"
        self.direction = "vertical"
        return
    
    def horizontal(self):
        self.type = "fix"
        self.direction = "horizontal"
        return



class GreasePencilToolsPanel(bpy.types.Panel):
    bl_label = "グリペンユーティリティ"
    bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Grease Pencil"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.greasepenciltools

    def draw(self, context):
        l = self.layout
        r = l.row()
        #b = r.box()
        b = r
    


        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        active = cols

        for item in uiitemList:
            #スキップ処理
            if item.mode == "none":
                continue
            
            if item.mode == "edit":
                #編集モード以外飛ばす
                if bpy.context.edit_object != None:
                    continue
            
            #縦横
            if item.type == "fix":
                if item.direction == "vertical":
                    active = cols.column(align=True)
                if item.direction == "horizontal":
                    active = active.row(align=True)
                continue
            
            #描画
            if item.type == "label":
                active.label(text=item.label)
            if item.type == "button":
                if item.icon != "":
                    active.operator(item.idname, icon=item.icon)
                else:
                    active.operator(item.idname)










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
# ############################################################################################################################
# uiitem("準備")
# ############################################################################################################################
# ########################################
# #セットアップ
# ########################################
# class FUJIWARATOOLBOX_242623(bpy.types.Operator):#セットアップ
#     """漫画描画セットアップ"""
#     bl_idname = "fujiwara_toolbox.command_242623"
#     bl_label = "セットアップ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")


#     ###################################
#     #処理部分
#     ###################################
#     def execute(self, context):
#         #ツール設定
#         #bpy.context.space_data.show_backface_culling = True
#         bpy.context.scene.tool_settings.use_gpencil_additive_drawing = True
#         bpy.context.scene.tool_settings.use_gpencil_continuous_drawing = True
#         bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
#         bpy.context.space_data.show_only_render = True
#         bpy.context.space_data.viewport_shade = 'MATERIAL'
#         bpy.context.space_data.lock_camera = False
#         bpy.context.space_data.region_3d.view_perspective = "CAMERA"
#         bpy.context.scene.render.resolution_percentage = 100

#         if bpy.context.scene.render.use_simplify:
#             #bpy.context.scene.render.use_simplify = False
#             if bpy.context.scene.render.simplify_subdivision < 2:
#                 bpy.context.scene.render.simplify_subdivision = 2

 


#         #ブラシ準備
#         brushname = "漫画ブラシ"
#         gpencil_brushes = bpy.context.scene.tool_settings.gpencil_brushes

#         if brushname not in gpencil_brushes:
#             gpencil_brushes.new(brushname,True)
#         cbrush = gpencil_brushes[brushname]
#         cbrush.line_width = 3
#         cbrush.use_strength_pressure = False
#         cbrush.pen_smooth_factor = 0.1

#         #グリースペンシルデータブロック
#         grease_pencil = bpy.context.scene.grease_pencil
#         if grease_pencil is None:
#             bpy.ops.gpencil.data_add()
#         grease_pencil = bpy.context.scene.grease_pencil

#         #レイヤー
#         gplayers = grease_pencil.layers
#         layername = "ペン入れ"
#         if layername not in gplayers:
#             gplayers.new(layername)
#             gplayer = gplayers[layername]
#             gplayers.active = gplayer
#             #レイヤー設定
#             gplayer.show_x_ray = False
#             gppenlayer = gplayer
#             gplayers.active = gppenlayer


#         layername = "背景"
#         if layername not in gplayers:
#             gplayers.new(layername)
#             gplayer = gplayers[layername]
#             #レイヤー設定
#             gplayer.show_x_ray = False
#             gplayer.tint_factor = 1
#             gplayer.line_change = 10

#         layername = "オノマトペ"
#         if layername not in gplayers:
#             gplayers.new(layername)
#             gplayer = gplayers[layername]
#             #レイヤー設定
#             gplayer.show_x_ray = False

#         layername = "下書き"
#         if layername not in gplayers:
#             gplayers.new(layername)
#             gplayer = gplayers[layername]
#             #レイヤー設定
#             gplayer.show_x_ray = False
#             gplayer.opacity = 0.2
#             gplayer.tint_color = (0, 0.35567, 1)
#             gplayer.tint_factor = 1
#             gplayer.line_change = 10
#             gpshitagakilayer = gplayer
#             gplayers.active = gpshitagakilayer



#         #パレット
#         #パレット生成のためのドロー
#         bpy.ops.gpencil.draw(mode='DRAW',wait_for_input=False)
#         palette = grease_pencil.palettes.active
#         pmain = palette
#         pmain.name = "漫画パレット"
        
#         colors = pmain.colors

#         cname = "メイン"
#         if cname not in colors:
#             col = colors.new()
#             col.name = cname
#             col.color = (0,0,0)
#             col.alpha = 1
#             col.fill_color = (1,1,1)
#             col.fill_alpha = 0
#             colors.active = col

#         cactive = colors.active

#         cname = "ホワイト"
#         if cname not in colors:
#             col = colors.new()
#             col.name = cname
#             col.color = (1,1,1)
#             col.alpha = 1
#             col.fill_color = (1,1,1)
#             col.fill_alpha = 0
        
#         cname = "白消し"
#         if cname not in colors:
#             col = colors.new()
#             col.name = cname
#             col.color = (1,1,1)
#             col.alpha = 1
#             col.fill_color = (1,1,1)
#             col.fill_alpha = 1

#         cname = "ベタ塗り"
#         if cname not in colors:
#             col = colors.new()
#             col.name = cname
#             col.color = (0,0,0)
#             col.alpha = 1
#             col.fill_color = (0,0,0)
#             col.fill_alpha = 1

#         cname = "黒フチ白地"
#         if cname not in colors:
#             col = colors.new()
#             col.name = cname
#             col.color = (0,0,0)
#             col.fill_alpha = 1

#         cname = "白フチ黒地"
#         if cname not in colors:
#             col = colors.new()
#             col.name = cname
#             col.color = (1,1,1)
#             col.fill_color = (0,0,0)
#             col.fill_alpha = 1

#         colors.active = cactive


#         #bpy.ops.gpencil.palette_add()

#         ##メイン 白消し 黒フチ白地
#         #palettes = grease_pencil.palettes
#         #pmainname = "メイン"
#         #if pmainname not in palettes:
#         #    palettes.new("メイン")
#         #pmain = palettes[pmainname]


#         #pwhitename = "白消し"
#         #pborderedwhitename = "黒フチ白地"

#         #パネル設定周り

#         #areas = bpy.context.screen.areas
#         #for area in areas:
#         #    if area.type == "VIEW_3D":
#         #        spaces = area.spaces
#         #        for space in spaces:
#         #            if space.type == "VIEW_3D":
#         #→bpy.context.space_dataでアクセスできた…

#         #        #regions = area.regions
#         #        #for region in regions:
#         #        # #'TOOLS''TOOL_PROPS'
#         #        # if region

#         #線幅を戻す
#         bpy.ops.fujiwara_toolbox.command_347064()
#         #下書き表示
#         gplayers = bpy.context.scene.grease_pencil.layers
#         if "下書き" in gplayers:
#             bpy.context.scene.grease_pencil.layers["下書き"].hide = False


#         #SSAO設定
#         bpy.context.space_data.fx_settings.use_ssao = True
#         ssao = bpy.context.space_data.fx_settings.ssao
#         ssao.color = (0.0, 0.0, 0.0)
#         ssao.factor = 0.5
#         ssao.distance_max = 0.1



#         #グリペン描画開始
#         bpy.ops.gpencil.draw("INVOKE_DEFAULT",mode='DRAW')

#         return {'FINISHED'}
# ########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

############################################################################################################################
uiitem("パンケーキモデル生成")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def curve_to_pancake(obj, dim_z_div = 4, color=(1,1,1)):
    fjw.activate(obj)
    mat = bpy.data.materials.new("Pancake Mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)

    # obj.data.dimensions = '2D'
    obj.data.splines[0].use_cyclic_u = True
    bpy.ops.object.convert(target='MESH')
    fjw.mode("EDIT")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_face_add()
    fjw.mode("OBJECT")
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

    dim_x, dim_y, dim_z = obj.dimensions
    dim_z = math.sqrt(dim_x*dim_x + dim_y*dim_y) / dim_z_div

    modu = fjw.Modutils(obj)
    m = modu.add("Solidify", "SOLIDIFY")
    m.thickness = dim_z
    m.offset = 0
    modu.apply(m)

    m = modu.add("Decimate", "DECIMATE")
    m.decimate_type = "DISSOLVE"
    m.angle_limit = 0.0872665
    modu.apply(m)

    m = modu.add("Remesh", "REMESH")
    m.mode = 'SMOOTH'
    m.octree_depth = 4
    m.use_smooth_shade = True
    m.use_remove_disconnected = False
    modu.apply(m)

    m = modu.add("Laplacian Smooth", "LAPLACIANSMOOTH")
    m.iterations = 2
    m.lambda_factor = 1
    modu.apply(m)

    m = modu.add("Remesh", "REMESH")
    m.mode = 'SMOOTH'
    m.octree_depth = 4
    m.use_smooth_shade = True
    modu.apply(m)

    m = modu.add("Subsurf", "SUBSURF")
    m.levels = 2
    bpy.context.scene.render.use_simplify = False

def extract_stroke_to_new_layer():
    gp_data = bpy.context.gpencil_data
    gp_data.use_stroke_edit_mode = True
    strokes = gp_data.layers.active.active_frame.strokes

    if len(strokes) == 0:
        return None, None

    stroke = strokes[0]
    bpy.ops.gpencil.select_all(action='DESELECT')
    color = stroke.color.color
    fill_color = stroke.color.fill_color
    for point in stroke.points:
        point.select = True
    bpy.ops.gpencil.move_to_layer(layer='__CREATE__')
    return color, fill_color

def gen_pancake_all_strokes(dim_z_div):
        fjw.deselect()
        color = (1,1,1)
        while color:
            color, fill_color = extract_stroke_to_new_layer()
            if fill_color:
                bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)
                bpy.ops.gpencil.layer_remove()
                selection = fjw.get_selected_list()
                for obj in selection:
                    curve_to_pancake(obj, dim_z_div, fill_color)
                    fjw.deselect()
        bpy.ops.gpencil.layer_remove()
    

def gen_pancake(dim_z_div=4):
    gen_pancake_all_strokes(dim_z_div)
    if bpy.context.gpencil_data:
        bpy.context.gpencil_data.use_stroke_edit_mode = False

########################################
#薄め
########################################
#bpy.ops.fujiwara_toolbox.gen_pancake_thin() #薄め
class FUJIWARATOOLBOX_GEN_PANCAKE_THIN(bpy.types.Operator):
    """うす～いパンケーキを生成する。"""
    bl_idname = "fujiwara_toolbox.gen_pancake_thin"
    bl_label = "薄め"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        gen_pancake(8)
        return {'FINISHED'}
########################################


########################################
#ふつう
########################################
#bpy.ops.fujiwara_toolbox.gen_pancake_mid() #ふつう
class FUJIWARATOOLBOX_GEN_PANCAKE_MID(bpy.types.Operator):
    """ふつうのパンケーキを生成する。"""
    bl_idname = "fujiwara_toolbox.gen_pancake_mid"
    bl_label = "ふつう"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        gen_pancake(4)
        return {'FINISHED'}
########################################

########################################
#厚め
########################################
#bpy.ops.fujiwara_toolbox.gen_pancake_thick() #厚め
class FUJIWARATOOLBOX_GEN_PANCAKE_THICK(bpy.types.Operator):
    """あつめのパンケーキを生成する。"""
    bl_idname = "fujiwara_toolbox.gen_pancake_thick"
    bl_label = "厚め"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        gen_pancake(2)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ベベルカーブ化")
############################################################################################################################

def curve_set_bevel(obj, depth = 0.2, color=(1,1,1)):
    fjw.activate(obj)
    mat = bpy.data.materials.new("Bevel Mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)

    obj.data.bevel_depth = depth
    obj.data.bevel_resolution = 4
    obj.data.fill_mode = "FULL"

    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

def gen_bevelcurve_all_strokes(depth):
        fjw.deselect()
        color = (1,1,1)
        while color:
            color, fill_color = extract_stroke_to_new_layer()
            if color:
                bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)
                bpy.ops.gpencil.layer_remove()
                selection = fjw.get_selected_list()
                for obj in selection:
                    curve_set_bevel(obj, depth, color)
                    fjw.deselect()
        bpy.ops.gpencil.layer_remove()
    

def gen_bevelcurve(depth=0.2):
    gen_bevelcurve_all_strokes(depth)
    if bpy.context.gpencil_data:
        bpy.context.gpencil_data.use_stroke_edit_mode = False


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#細め
########################################
#bpy.ops.fujiwara_toolbox.gen_bevelcurve_thin() #細め
class FUJIWARATOOLBOX_GEN_BEVELCURVE_THIN(bpy.types.Operator):
    """細いベベルカーブを生成する"""
    bl_idname = "fujiwara_toolbox.gen_bevelcurve_thin"
    bl_label = "細め"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        gen_bevelcurve(0.05)
        return {'FINISHED'}
########################################

########################################
#ふつう
########################################
#bpy.ops.fujiwara_toolbox.gen_bevelcurve_mid() #ふつう
class FUJIWARATOOLBOX_GEN_BEVELCURVE_MID(bpy.types.Operator):
    """ふつうのベベルカーブを生成する"""
    bl_idname = "fujiwara_toolbox.gen_bevelcurve_mid"
    bl_label = "ふつう"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        gen_bevelcurve(0.2)
        return {'FINISHED'}
########################################

########################################
#太め
########################################
#bpy.ops.fujiwara_toolbox.gen_bevelcurve_thick() #太め
class FUJIWARATOOLBOX_GEN_BEVELCURVE_THICK(bpy.types.Operator):
    """太いベベルカーブを生成する"""
    bl_idname = "fujiwara_toolbox.gen_bevelcurve_thick"
    bl_label = "太め"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        gen_bevelcurve(0.4)
        return {'FINISHED'}
########################################


































#########################################
##細く
#########################################
#class FUJIWARATOOLBOX_148957(bpy.types.Operator):#細く
#    """細く"""
#    bl_idname = "fujiwara_toolbox.command_148957"
#    bl_label = "細く"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.scene.grease_pencil.layers.active.line_change = -20
#        bpy.ops.gpencil.stroke_apply_thickness()
#        #GLレンダ
#        bpy.ops.fujiwara_toolbox.command_979047()

#        return {'FINISHED'}
#########################################







#########################################
##太く
#########################################
#class FUJIWARATOOLBOX_279333(bpy.types.Operator):#太く
#    """太く"""
#    bl_idname = "fujiwara_toolbox.command_279333"
#    bl_label = "太く"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.scene.grease_pencil.layers.active.line_change = 20
#        bpy.ops.gpencil.stroke_apply_thickness()
#        #GLレンダ
#        bpy.ops.fujiwara_toolbox.command_979047()
        
#        return {'FINISHED'}
#########################################








"""
def sub_registration():
    pass

def sub_unregistration():
    pass
"""
def sub_registration():
    #bpy.types.DATA_PT_lens.append(fjw.greasepenciltools_ui)
    pass

def sub_unregistration():
    #bpy.types.DATA_PT_lens.remove(fjw.greasepenciltools_ui)
    pass


def register():
    bpy.utils.register_module(__name__)
    sub_registration()
    


def unregister():
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()

