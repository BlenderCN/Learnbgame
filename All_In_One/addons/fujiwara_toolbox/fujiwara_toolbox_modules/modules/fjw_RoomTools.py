import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import mathutils
import subprocess
import shutil
import webbrowser


import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf


bl_info = {
    "name": "FJW Room Tools",
    "description": "藤原佑介が作った部屋作成ツールです",
    "author": "藤原佑介",
    "version": (0, 4),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=",
    "category": "Learnbgame"
}

"""
作業ログ
2016/07/18　v0.1 公開
2016/07/19　屋根ツール、部屋の階設定、ヘルプ機能
2016/07/20　v0.2 穴あけペアレントを元オブジェクトからバウンドに変更「バウンドで穴を追加」
2016/07/21　v0.3 グリッドツール、モデリングツール、マップセットアップツールなど
2016/07/28　v0.4 グリッドの回転、移動を実装
"""





############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#ui表示上の各種コンフィグを記述するクラス。ボタンリストに代替。
#これをリスト化すればいい！
#途中でこのコンフィグだけのやつ挟めばラベルとか挿入できる
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
    #ボタンをはなしたいとき
    def vertical_sep(self):
        self.type = "fix"
        self.direction = "vertical_sep"
        return
    
    def horizontal_sep(self):
        self.type = "fix"
        self.direction = "horizontal_sep"
        return

    def group(self):
        self.type = "group"
        return



#メインパネル
class RoomToolsView3DPanel(bpy.types.Panel):#メインパネル
    bl_label = "Room Tools"
    bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    @classmethod
    def poll(cls, context):
        pref = conf.get_pref()
        return pref.roomtools

    def draw(self, context):
        l = self.layout
        r = l.row()
        #b = r.box()
        b = r

        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        basecols = cols
        active = cols

        for item in uiitemList:
            #スキップ処理
            if item.mode == "none":
                continue
            
            if item.mode == "edit":
                #編集モード以外飛ばす
                if bpy.context.edit_object != None:
                    continue
            #いまんとこ妙
            ##グループ化
            #if item.type == "group":
            #    cols = basecols.box()
            #    basecols.label(text=" ")
            #縦横
            if item.type == "fix":
                if item.direction == "vertical":
                    active = cols.column(align=True)
                if item.direction == "horizontal":
                    active = active.row(align=True)
                if item.direction == "vertical_sep":
                    active = cols.column(align=False)
                if item.direction == "horizontal_sep":
                    active = active.row(align=False)
                continue
            
            #描画
            if item.type == "label":
                if item.icon != "":
                    active.label(text=item.label, icon=item.icon)
                else:
                    active.label(text=item.label)
            if item.type == "button":
                if item.icon != "":
                    active.operator(item.idname, icon=item.icon)
                else:
                    active.operator(item.idname)




############################################################################################################################
uiitem("形成ツール")
############################################################################################################################


#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------
############################################################################################################################
uiitem("便利ツール")
############################################################################################################################

########################################
#
########################################
class FUJIWARATOOLBOX_35263(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_35263"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/bian-litsuru")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#メモ設置
########################################
class FUJIWARATOOLBOX_350101r(bpy.types.Operator):#メモ設置
    """メモ設置"""
    bl_idname = "fujiwara_toolbox.command_350101r"
    bl_label = "メモ設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_EMPTY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, view_align=False, location=bpy.context.space_data.cursor_location, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.rotation_euler[1] = 3.14159
        obj.show_name = True
        obj.show_x_ray = True
        obj.name = "MEMO:"
        obj.location[2] += 1

        #右上レイヤーにまとめる
        obj.layers[9] = True
        obj.layers[0] = False
        bpy.context.scene.layers[9] = True

        #グループ化
        if "MEMO" not in bpy.data.groups:
            bpy.ops.group.create(name="MEMO")
        else:
            bpy.data.groups["MEMO"].objects.link(obj)
        
        return {'FINISHED'}
########################################

########################################
#カメラライン
########################################
class FUJIWARATOOLBOX_242082(bpy.types.Operator):#カメラライン
    """カメラライン"""
    bl_idname = "fujiwara_toolbox.command_242082"
    bl_label = "カメラライン"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_EMPTY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, view_align=False, location=bpy.context.space_data.cursor_location, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.rotation_euler[1] = 3.14159
        obj.show_name = True
        obj.show_x_ray = True
        obj.name = "MEMO:カメラライン"
        obj.location[2] += 1
        obj.rotation_euler[0] = -1.5708
        obj.empty_draw_size = 25



        #右上レイヤーにまとめる
        obj.layers[9] = True
        obj.layers[0] = False
        bpy.context.scene.layers[9] = True

        #グループ化
        if "MEMO" not in bpy.data.groups:
            bpy.ops.group.create(name="MEMO")
        else:
            bpy.data.groups["MEMO"].objects.link(obj)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------









#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("グリッドツール").icon = "GRID"
############################################################################################################################
def place_grid(target):
    obj = target
    fjw.deselect()

    if obj == None:
        bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=fjw.layers(0))
        obj = fjw.active()

    obj.name = "Grid_Notready"
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    #表示・レンダ設定
    obj.hide_render = True
    obj.hide_select = False
    obj.draw_type = 'WIRE'

    obj.select = True

    #適当な角に原点設定
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_all(action='DESELECT')

    data = obj.data
    bm = bmesh.from_edit_mesh(data)
    #選択リフレッシュ
    for v  in bm.verts:
        v.select = False
    for e in bm.edges:
        e.select = False
    for f in bm.faces:
        f.select = False

    #bm.verts[0].select = True
    #なんかエラーでるから無理やり
    for v  in bm.verts:
        v.select = True
        break
    bmesh.update_edit_mesh(data)

    #頂点選択
    bpy.context.scene.tool_settings.mesh_select_mode = [True,False,False]

    bpy.ops.view3d.snap_cursor_to_selected()    

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    #位置ゼロ
    bpy.ops.object.location_clear()


    #ロック
    obj.lock_scale[0] = True
    obj.lock_scale[1] = True
    obj.lock_scale[2] = True
    obj.lock_rotation[0] = True
    obj.lock_rotation[1] = True
    obj.lock_rotation[2] = True
    obj.lock_location[1] = True
    obj.lock_location[2] = True
    obj.lock_location[0] = True
    obj.lock_location[2] = False



    #サイズ設定、、をする前にモディファイアをとらないといけない！
    fjw.removeall_mod()
    obj.dimensions = (grid_unit,grid_unit,0)
    

    return obj

grid_unit = 1
griddirection = 2

ShakuScale = 3 * 10 / 33
#尺とかメートルの単位をチェックしてunitきりかえる
def update_grid_unit():
    global grid_unit
    global ShakuScale
    grid = fjw.match("Grid")
    for obj in bpy.data.objects:
        if "Grid_Metre" in obj.name:
            grid_unit = 1

            break
    for obj in bpy.data.objects:
        if "Grid_Shaku" in obj.name:
            grid_unit = ShakuScale
            break

    X = 0
    Y = 1
    Z = 2
    if grid != None:
        griddirection = Z

        if grid.rotation_euler[X] != 0:
            griddirection = X

        if grid.rotation_euler[Y] != 0:
            griddirection = Y

    return

array_count = 60

#グリッド生成後処理
def place_grid_post(target):
    update_grid_unit()
    grid = target
    bpy.context.scene.objects.active = grid
    grid.select = True
    
    #サイズ設定、、をする前にモディファイアをとらないといけない！
    fjw.removeall_mod()
    grid.dimensions = (grid_unit,grid_unit,0)
    
    
    grid.dimensions = (grid_unit,grid_unit,0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    global array_count
    #配列mod
    bpy.ops.object.modifier_add(type='ARRAY')
    mod = fjw.getnewmod(grid)
    mod.count = array_count
    mod.relative_offset_displace[0] = 1

    bpy.ops.object.modifier_add(type='ARRAY')
    mod = fjw.getnewmod(grid)
    mod.count = array_count
    mod.relative_offset_displace[0] = 0
    mod.relative_offset_displace[1] = 1

    #ミラーmod
    bpy.ops.object.modifier_add(type='MIRROR')
    mod = fjw.getnewmod(grid)
    mod.use_y = True

    fjw.deselect()
    grid.hide_select = True
    return

########################################
#
########################################
class FUJIWARATOOLBOX_86777(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_86777"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/guriddotsuru")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#メートルグリッド
########################################
class FUJIWARATOOLBOX_919744(bpy.types.Operator):#メートルグリッド
    """メートルグリッドを設置します。既に存在する場合は再設置しなおします。"""
    bl_idname = "fujiwara_toolbox.command_919744"
    bl_label = "m"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="GRID",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.objectmode()
        fjw.deselect()
        fjw.delete(fjw.matches("Grid_"))

        global grid_unit

        name = "Grid_Metre"
        grid = place_grid(fjw.match(name))
        grid.name = name
        place_grid_post(grid)

        #name = "Grid_Metre_X"
        #grid = place_grid(match(name))
        #grid.name = name
        #place_grid_post(grid)
        #grid.rotation_euler[0] = 1.5708


        #name = "Grid_Metre_Y"
        #grid = place_grid(match(name))
        #grid.name = name
        #place_grid_post(grid)
        #grid.rotation_euler[0] = 1.5708
        #grid.rotation_euler[2] = 1.5708

        return {'FINISHED'}
########################################

########################################
#尺グリッド
########################################
class FUJIWARATOOLBOX_770596(bpy.types.Operator):#尺グリッド
    """尺グリッドを設置"""
    bl_idname = "fujiwara_toolbox.command_770596"
    bl_label = "尺"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="GRID",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.objectmode()
        fjw.deselect()
        fjw.delete(fjw.matches("Grid_"))


        global grid_unit

        name = "Grid_Shaku"
        grid = place_grid(fjw.match(name))
        grid.name = name
        place_grid_post(grid)
        
        return {'FINISHED'}
########################################









########################################
#撤去
########################################
class FUJIWARATOOLBOX_341962(bpy.types.Operator):#撤去
    """撤去"""
    bl_idname = "fujiwara_toolbox.command_341962"
    bl_label = "撤去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="X",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        grid = fjw.match("Grid_")

        if grid == None:
            self.report({"INFO"},"グリッドがありません")
            return {'CANCELLED'}


        fjw.deselect()
        
        grid.hide_select = False
        grid.select = True

        bpy.ops.object.delete(use_global=False)

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------










#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
def scale_grid(target,div):
    grid = target
    if grid == None:
        return False

    scale = 1 / div
    grid.scale = (scale,scale,scale)


    #配列数をスケールにあわせて変える
    global array_count
    for mod in grid.modifiers:
        if mod.type == "ARRAY":
            mod.count = array_count * div


    return True






########################################
#1/1
########################################
class FUJIWARATOOLBOX_56651(bpy.types.Operator):#1/1
    """1/1"""
    bl_idname = "fujiwara_toolbox.command_56651"
    bl_label = "1/1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if scale_grid(fjw.match("Grid_"),1) == False:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}
        return {'FINISHED'}
########################################

########################################
#1/2
########################################
class FUJIWARATOOLBOX_465473(bpy.types.Operator):#1/2
    """1/2"""
    bl_idname = "fujiwara_toolbox.command_465473"
    bl_label = "1/2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if scale_grid(fjw.match("Grid_"),2) == False:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}
        
        return {'FINISHED'}
########################################

########################################
#1/3
########################################
class FUJIWARATOOLBOX_238380(bpy.types.Operator):#1/3
    """1/3"""
    bl_idname = "fujiwara_toolbox.command_238380"
    bl_label = "1/3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if scale_grid(fjw.match("Grid_"),3) == False:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}
        
        return {'FINISHED'}
########################################

########################################
#1/4
########################################
class FUJIWARATOOLBOX_101409(bpy.types.Operator):#1/4
    """1/4"""
    bl_idname = "fujiwara_toolbox.command_101409"
    bl_label = "1/4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if scale_grid(fjw.match("Grid_"),4) == False:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}
        
        return {'FINISHED'}
########################################

########################################
#1/8
########################################
class FUJIWARATOOLBOX_238024(bpy.types.Operator):#1/8
    """1/8"""
    bl_idname = "fujiwara_toolbox.command_238024"
    bl_label = "1/8"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if scale_grid(fjw.match("Grid_"),8) == False:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#グリッドサイズキューブ設置
########################################
class FUJIWARATOOLBOX_565778(bpy.types.Operator):#グリッドサイズ化
    """グリッドサイズのキューブを設置して頂点スナップをきかせる"""
    bl_idname = "fujiwara_toolbox.command_565778"
    bl_label = "キューブ設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="ROTATE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        global grid_unit
        grid = fjw.match("Grid_")
        if grid == None:
            self.report({"INFO"},"グリッドを設置してください")
            return {'CANCELLED'}


        if fjw.active() != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        pos = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])
        bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=pos, layers=fjw.layers(-1,True,False))

        


        gridscale = grid.scale[0]

        update_grid_unit()
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        obj = fjw.active()
        obj.dimensions = (grid_unit * gridscale,grid_unit * gridscale,grid_unit * gridscale)

            #適当な角に原点設定
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')

        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        #選択リフレッシュ
        for v  in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False

        #bm.verts[0].select = True
        #なんかエラーでるから無理やり
        for v  in bm.verts:
            v.select = True
            break
        bmesh.update_edit_mesh(data)

        #頂点選択
        bpy.context.scene.tool_settings.mesh_select_mode = [True,False,False]

        bpy.ops.view3d.snap_cursor_to_selected()    

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


        #for obj in bpy.context.selected_objects:
        #   if obj.type == "MESH":
        #       obj.dimensions =
        #       (grid_unit*gridscale,grid_unit*gridscale,grid_unit*gridscale)
        #       #obj.dimensions =
        #       (grid_unit*2*gridscale,grid_unit*2*gridscale,grid_unit*2*gridscale)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        #頂点スナップ
        bpy.ops.fujiwara_toolbox.command_33358rt()

        bpy.context.space_data.cursor_location = pos
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)


        return {'FINISHED'}
########################################



########################################
#床面積
########################################
class FUJIWARATOOLBOX_929148(bpy.types.Operator):#床面積
    """インフォメーションでアクティブオブジェクトの床面積を表示します"""
    bl_idname = "fujiwara_toolbox.command_929148"
    bl_label = "床面積"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="INFO",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        area = 0.0
        for obj in bpy.context.selected_objects:
            fjw.activate(obj)

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='DESELECT')

            data = obj.data
            bm = bmesh.from_edit_mesh(data)
            #選択リフレッシュ
            for v  in bm.verts:
                v.select = False
            for e in bm.edges:
                e.select = False
            for f in bm.faces:
                f.select = False

            for f in bm.faces:
                #self.report({"INFO"},str(f.normal))
                #self.report({"INFO"},str(f.calc_area()))
                if f.normal.z == 1.0:
                    #self.report({"INFO"},"上向き")
                    #self.report({"INFO"},str(f.calc_area()))
                    area += f.calc_area() * obj.scale[0] * obj.scale[1]
            

            bmesh.update_edit_mesh(data)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        
        global ShakuScale
        self.report({"INFO"},str(math.floor(area * 100) / 100) + "㎡ / " + str(math.floor(area / ShakuScale / ShakuScale * 10 / 2) / 10) + "畳")
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#Z平面
########################################
class FUJIWARATOOLBOX_751440(bpy.types.Operator):#Z平面
    """グリッドをXY平面にする"""
    bl_idname = "fujiwara_toolbox.command_751440"
    bl_label = "XY平面"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        grid = fjw.match("Grid_")
        if grid == None:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}

        grid.rotation_euler = (0,0,0)

        update_grid_unit()
        return {'FINISHED'}
########################################

########################################
#Y平面
########################################
class FUJIWARATOOLBOX_469634(bpy.types.Operator):#Y平面
    """グリッドをXZ平面にする"""
    bl_idname = "fujiwara_toolbox.command_469634"
    bl_label = "XZ平面"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        grid = fjw.match("Grid_")
        if grid == None:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}

        grid.rotation_euler = (1.5708,0,0)

        update_grid_unit()
        
        return {'FINISHED'}
########################################

########################################
#X平面
########################################
class FUJIWARATOOLBOX_403843(bpy.types.Operator):#X平面
    """グリッドをYZ平面にする"""
    bl_idname = "fujiwara_toolbox.command_403843"
    bl_label = "YZ平面"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        grid = fjw.match("Grid_")
        if grid == None:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}

        grid.rotation_euler = (1.5708,0,1.5708)

        update_grid_unit()
        
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#カーソル位置に移動
########################################
class FUJIWARATOOLBOX_692152(bpy.types.Operator):#カーソルの高さに移動
    """グリッドをカーソルの位置に移動します"""
    bl_idname = "fujiwara_toolbox.command_692152"
    bl_label = "カーソルの位置に移動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        grid = fjw.match("Grid_")
        if grid == None:
            self.report({"WARNING"},"グリッドを設置してください")
            return {'CANCELLED'}

        #grid.location[2] = bpy.context.space_data.cursor_location[2]
        global grid_unit
        c = bpy.context.space_data.cursor_location
        #grid.location =
        #(c[0]//grid_unit*grid_unit,c[1]//grid_unit*grid_unit,c[2]//grid_unit*grid_unit)
        #↓Z位置はカーソルからそのままとらないと非常に不便！
        grid.location = (c[0] // grid_unit * grid_unit,c[1] // grid_unit * grid_unit,c[2])
        #位置をグリッドで割る あまりなしで を、グリッドでかければいい！



        return {'FINISHED'}
########################################
















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("モデリングツール").icon = "MESH_DATA"
############################################################################################################################
########################################
#
########################################
class FUJIWARATOOLBOX_530530(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_530530"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/moderingutsuru")
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#頂点スナップ
########################################
class FUJIWARATOOLBOX_33358rt(bpy.types.Operator):#頂点スナップ
    """頂点スナップ"""
    bl_idname = "fujiwara_toolbox.command_33358rt"
    bl_label = "頂点スナップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_VERTEX",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        return {'FINISHED'}
########################################

########################################
#グリッドスナップ
########################################
class FUJIWARATOOLBOX_357169rt(bpy.types.Operator):#グリッドスナップ
    """blenderのデフォルトっぽい設定"""
    bl_idname = "fujiwara_toolbox.command_357169rt"
    bl_label = "デフォルト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_GRID",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = False
        bpy.context.scene.tool_settings.snap_element = 'INCREMENT'
        bpy.context.scene.tool_settings.use_snap_grid_absolute = True
        
        return {'FINISHED'}
########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#グリッドローカルビュー
########################################
class FUJIWARATOOLBOX_921750(bpy.types.Operator):#グリッドローカルビュー
    """グリッドつきのローカルビュー"""
    bl_idname = "fujiwara_toolbox.command_921750"
    bl_label = "グリッドローカルビュー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="GRID",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        grid = fjw.match("Grid_")
        if grid == None:
            self.report({"WARNING"},"グリッドがありません")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        grid.hide_select = False
        grid.select = True

        bpy.ops.view3d.localview()
        grid.select = False
        bpy.ops.view3d.view_selected(use_all_regions=False)

        grid.hide_select = True
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#頂点EDIT
########################################
class FUJIWARATOOLBOX_964808(bpy.types.Operator):#頂点EDIT
    """サクッと編集モードに入って頂点選択モードにする。"""
    bl_idname = "fujiwara_toolbox.command_964808"
    bl_label = "頂点EDIT"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VERTEXSEL",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.context.scene.tool_settings.mesh_select_mode = [True,False,False]
        return {'FINISHED'}
########################################



########################################
#面EDIT
########################################
class FUJIWARATOOLBOX_462141(bpy.types.Operator):#面EDIT
    """サクッと編集モードに入って面選択モードにする。頂点スナップオン。"""
    bl_idname = "fujiwara_toolbox.command_462141"
    bl_label = "面EDIT"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FACESEL",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.context.scene.tool_settings.mesh_select_mode = [False,False,True]
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.space_data.use_occlude_geometry = False

        return {'FINISHED'}
########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#選択頂点を原点に
########################################
class FUJIWARATOOLBOX_753369rt(bpy.types.Operator):#選択頂点を原点に
    """選択頂点を原点に設定します。（実は面とか辺でも大丈夫）"""
    bl_idname = "fujiwara_toolbox.command_753369rt"
    bl_label = "選択頂点を原点に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="LOOPSEL",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        if obj.mode != "EDIT":
            self.report({"INFO"},"編集モードで押して下さい")
            return {'CANCELLED'}
        
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#原点を下に（選択物）
########################################
class FUJIWARATOOLBOX_947695rt(bpy.types.Operator):#原点を下に（選択物）
    """選択物それぞれの原点をそのオブジェクトの一番下に移動する。トランスフォームは適用されます。"""
    bl_idname = "fujiwara_toolbox.command_947695rt"
    bl_label = "原点を下に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="TRIA_DOWN_BAR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        objlist = []
        for obj in bpy.context.selected_objects:
            objlist.append(obj)
        
        for obj in bpy.context.selected_objects:
            obj.select = False
        
        for obj in objlist:
            bpy.context.scene.objects.active = obj
            obj.select = True
        
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bottom = 1000
            for v in obj.data.vertices:
                if v.co.z < bottom:
                    bottom = v.co.z
            bpy.context.space_data.cursor_location[2] = bottom
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.select = False
        
        for obj in objlist:
            obj.select = True
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#カーソルZを0に
########################################
class FUJIWARATOOLBOX_98727rt(bpy.types.Operator):#カーソルZを0に
    """カーソルZを0に"""
    bl_idname = "fujiwara_toolbox.command_98727rt"
    bl_label = "Zを0に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.space_data.cursor_location[2] = 0
        
        return {'FINISHED'}
########################################





########################################
#オブジェクトのZを0に
########################################
class FUJIWARATOOLBOX_109728rt(bpy.types.Operator):#オブジェクトのZを0に
    """オブジェクトのZを0に"""
    bl_idname = "fujiwara_toolbox.command_109728rt"
    bl_label = "Zを0に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATAMODE",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.location[2] = 0
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
























############################################################################################################################
uiitem("　")
uiitem("生成ツール")
############################################################################################################################


#---------------------------------------------
uiitem().group()
#---------------------------------------------

#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("床ツール").icon = "NLA_PUSHDOWN"
############################################################################################################################


########################################
#ヘルプ
########################################
class FUJIWARATOOLBOX_286574(bpy.types.Operator):#ヘルプ
    """ヘルプ"""
    bl_idname = "fujiwara_toolbox.command_286574"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/chuangtsuru")
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






########################################
#建築エリア設置
########################################
class FUJIWARATOOLBOX_778347(bpy.types.Operator):#建築エリア設置
    """建築エリア設置"""
    bl_idname = "fujiwara_toolbox.command_778347"
    bl_label = "建築エリア設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "ConstructionArea" in bpy.data.objects:
            self.report({"INFO"},"設置済みです")
            return {'CANCELLED'}

        if fjw.active() != None:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


        bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=fjw.layers(0))
        obj = bpy.context.scene.objects.active
        obj.scale = (25,25,25)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        mod = fjw.getnewmod(obj)
        mod.thickness = 0.5
        obj.draw_type = 'WIRE'
        obj.hide_select = True
        obj.hide_render = True
        obj.name = "ConstructionArea"
        fjw.deselect()
        
        return {'FINISHED'}
########################################

########################################
#床面化（選択物）
########################################
class FUJIWARATOOLBOX_456812(bpy.types.Operator):#床面化（選択物）
    """床面化（選択物）"""
    bl_idname = "fujiwara_toolbox.command_456812"
    bl_label = "床面化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_PLANE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        if "ConstructionArea" not in bpy.data.objects:
            self.report({"WARNING"},"建築エリアを設置してください")
            return {'CANCELLED'}
        ConstructionArea = bpy.data.objects["ConstructionArea"]

        bpy.ops.object.mode_set(mode = 'OBJECT')

        #統合していくベース
        boolbase = bpy.context.scene.objects.active
        boolbase.select = True
        boolbase.name = "Floor"

        #その前に重心原点とかにしないと位置ゼロ時めんどい
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                #位置ゼロにしないとめんどい
                obj.location[2] = 0


        #まずはトランスフォームを適用しないとboolに失敗することがある
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


        #modも全部適用
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               for mod in obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier=mod.name)

        boolbase.select = False
        bpy.context.scene.objects.active = boolbase
        #統合処理
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                #位置ゼロにしないとめんどい
                #obj.location[2] = 0
                bpy.ops.object.modifier_add(type='BOOLEAN')
                mod = fjw.getnewmod(boolbase)
                mod.operation = 'UNION'
                mod.object = obj
                bpy.ops.object.modifier_apply(modifier=mod.name)

        #統合が終わったら他のを削除
        bpy.ops.object.delete(use_global=False)

        boolbase.select = True
        #トランスフォームを適用
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        #基準床と統合
        bpy.ops.object.modifier_add(type='BOOLEAN')
        mod = fjw.getnewmod(boolbase)
        mod.operation = 'INTERSECT'
        mod.object = ConstructionArea
        bpy.ops.object.modifier_apply(modifier=mod.name)


        #z位置がゼロじゃない頂点を全て削除
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        #選択リフレッシュ
        for v  in bm.verts:
        	v.select = False
        for e in bm.edges:
        	e.select = False
        for f in bm.faces:
        	f.select = False
        for v in bm.verts:
            if(v.co.z < -0.05):
                v.select = True

        bmesh.update_edit_mesh(data)
        bpy.ops.mesh.delete(type='VERT')

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.context.scene.objects.active.name = "room_" + bpy.context.scene.objects.active.name
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')


        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("部屋ツール").icon = "OUTLINER_OB_LATTICE"
############################################################################################################################
########################################
#
########################################
class FUJIWARATOOLBOX_544707(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_544707"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/bu-wutsuru")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
def make_room():
    floor = bpy.context.scene.objects.active
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    ##トランスフォームの適用
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    #リンク複製
    bpy.ops.object.duplicate_move_linked(OBJECT_OT_duplicate={"linked":True, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

    obj = bpy.context.scene.objects.active

    obj.name = "Room_base"

    #厚み
    bpy.ops.object.modifier_add(type='SOLIDIFY')

    mod = fjw.getnewmod(obj)
    mod.thickness = -2.4
    mod.use_rim = True
    mod.use_rim_only = True

    #見やすくする
    obj.draw_type = 'WIRE'

    #親子づけ
    bpy.context.scene.objects.active = floor
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    fjw.deselect()
    bpy.context.scene.objects.active = obj
    obj.select = True


########################################
#Make Room
########################################
class FUJIWARATOOLBOX_295847(bpy.types.Operator):#Make Room
    """床メッシュから部屋を生成"""
    bl_idname = "fujiwara_toolbox.command_295847"
    bl_label = "部屋生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        targets = fjw.get_selected_list()

        generated = []

        for target in targets:
            fjw.deselect()
            target.select = True
            fjw.activate(target)
            make_room()
            generated.extend(fjw.get_selected_list())
        
        fjw.deselect()

        fjw.select(generated)

        return {'FINISHED'}
########################################

def apply_room(self):
    for obj in bpy.data.objects:
        obj.select = False

    obj = bpy.context.scene.objects.active
    obj.select = True

    if "Room_base" not in obj.name:
        self.report({"WARNING"},"生成した部屋を選択してください")
        return False
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    obj.draw_type = 'TEXTURED'

    #シングルユーザ化
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)

    #modの適用
    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)

    #厚みだけつける
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    mod = fjw.getnewmod(fjw.active())
    mod.thickness = -0.01


    #トランスフォームの適用
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    #編集モードに入って各面を切り出す
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    data = obj.data
    bm = bmesh.from_edit_mesh(data)

    #選択リフレッシュ
    for f in bm.faces:
        f.select = False

    #各面を切り出す
    for f in bm.faces:
        f.select = True
        #曲面は同一面ということで。
        bpy.ops.mesh.faces_select_linked_flat(sharpness=0.523599)
        bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    #現在選択されてるのが切り出したオブジェクト
    gens = []
    for obj in bpy.context.selected_objects:
        obj.name = "RoomTools_Generated"
        gens.append(obj)

    for obj in bpy.data.objects:
        obj.select = False

    obj = bpy.context.scene.objects.active
    obj.select = True
    bpy.ops.object.delete(use_global=False)

    for gen in gens:
        gen.select = True

    #原点設定
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')



    #原点を下に
    objlist = []
    for obj in bpy.context.selected_objects:
        objlist.append(obj)
        
    for obj in bpy.context.selected_objects:
        obj.select = False
        
    for obj in objlist:
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bottom = 1000
        for v in obj.data.vertices:
            if v.co.z < bottom:
                bottom = v.co.z
        bpy.context.space_data.cursor_location[2] = bottom
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        obj.select = False
        
    for obj in objlist:
        obj.select = True

    return True

########################################
#Apply Room
########################################
class FUJIWARATOOLBOX_851083(bpy.types.Operator):#Apply Room
    """Apply Room"""
    bl_idname = "fujiwara_toolbox.command_851083"
    bl_label = "適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        targets = fjw.get_selected_list()
        for target in targets:
            fjw.deselect()
            fjw.activate(target)
            target.select = True
            if not apply_room(self):
                return {'CANCELLED'}

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#壁をマージ
########################################
class FUJIWARATOOLBOX_899191(bpy.types.Operator):#壁をマージ
    """壁・フチなどメッシュオブジェクトをマージ（結合）します"""
    bl_idname = "fujiwara_toolbox.command_899191"
    bl_label = "壁・フチをマージ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        #結合する
        bpy.ops.object.join()

        obj = bpy.context.scene.objects.active

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}
########################################







########################################
#フチ生成
########################################
class FUJIWARATOOLBOX_736006(bpy.types.Operator):#フチ生成
    """フチ生成"""
    bl_idname = "fujiwara_toolbox.command_736006"
    bl_label = "フチ生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 


        targets = []
        for obj in bpy.context.selected_objects:
            targets.append(obj)


        results = []
        for target in targets:
            #選択リフレッシュ
            for obj in bpy.data.objects:
                obj.select = False
            obj = target
            bpy.context.scene.objects.active = obj
            obj.select = True

            #複製
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            dup = bpy.context.active_object
            #モディファイアを全部とっぱらう
            for mod in dup.modifiers:
                bpy.ops.object.modifier_remove(modifier=mod.name)


            results.append(dup)
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            mod = fjw.getnewmod(dup)
            dup.dimensions[2] = 0.1
            #bpy.ops.object.transform_apply(location=False, rotation=False,
            #scale=True)
            mod.thickness = 0.02

            #親子づけ
            dup.select = True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            
        #選択リフレッシュ
        for obj in bpy.data.objects:
            obj.select = False

        for obj in results:
            obj.select = True

        fjw.group("rims")

        return {'FINISHED'}
########################################


########################################
#床を壁の上の階に
########################################
class FUJIWARATOOLBOX_404091(bpy.types.Operator):#床を壁の上の階に
    """床を選択した壁の上の階に移動する。対象がない場合は地上に。"""
    bl_idname = "fujiwara_toolbox.command_404091"
    bl_label = "選択物の上の階に移動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="TRIA_UP",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        room = None
        for obj in bpy.context.selected_objects:
            if "room_" in obj.name:
                room = obj
        
        if room == None:
            self.report({"WARNING"},"部屋の床を選択してください")
            return {'CANCELLED'}
        
        target = None
        for obj in bpy.context.selected_objects:
            if obj != room:
                target = obj

        #対象がない場合は0に
        if target == None:
            room.location[2] = 0
            return {'FINISHED'}
        room.location[2] = target.location[2]
        room.location[2] += target.dimensions[2]



        return {'FINISHED'}
########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("バウンド穴あけツール").icon = "MOD_BOOLEAN"
############################################################################################################################
########################################
#
########################################
class FUJIWARATOOLBOX_675998(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_675998"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/baundo-xueaketsuru")
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

def makehole(self,direction):
    base = bpy.context.scene.objects.active
    X = 0
    Y = 1
    Z = 2
    strdir = ["X","Y","Z"]

    #direction = Y

    targets = []

    base.select = False

    if len(bpy.context.selected_objects) == 0:
        self.report({"WARNING"},"対象がありません")
        return {'CANCELLED'}

    for obj in bpy.context.selected_objects:
        targets.append(obj)


    #選択リフレッシュ
    for obj in bpy.data.objects:
        obj.select = False

    #バウンド位置取得のために一時的に複製
    base.select = True
    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
    dup = bpy.context.active_object
    dup.select = True
    #原点をバウンドの中心に移動
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    #バウンド用立方体を追加
    bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=dup.location, layers=dup.layers)
    bound = bpy.context.active_object
    bound.name = "BoundHole_" + strdir[direction]

    #表示・レンダ設定
    bound.hide_render = True
    bound.draw_type = 'WIRE'


    #サイズ・回転あわせ
    bound.dimensions = base.dimensions
    bound.rotation_euler = base.rotation_euler

    #選択リフレッシュ
    for obj in bpy.data.objects:
        obj.select = False

    #複製の削除
    dup.select = True
    bpy.context.scene.objects.active = dup

    bpy.ops.object.delete(use_global=False)


    #direction方向に伸ばす
    bound.dimensions[direction] = 5

    bound.select = True
    #トランスフォームのアプライ
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


    #baseに親子づけ
    #bound.select = True
    #bpy.context.scene.objects.active = base
    #bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    #boundに親子づけたほうがよい
    base.select = True
    bpy.context.scene.objects.active = bound
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    #選択リフレッシュ
    for obj in bpy.data.objects:
        obj.select = False


    #ターゲット群に穴あけ
    for obj in targets:
        bpy.context.scene.objects.active = obj
        if obj.type == "MESH":
            bpy.ops.object.modifier_add(type='BOOLEAN')
            mod = fjw.getnewmod(obj)
            mod.operation = 'DIFFERENCE'
            mod.object = bound

    #選択リフレッシュ
    for obj in bpy.data.objects:
        obj.select = False

    #元のを選択して終わる。
    base.select = True
    bpy.context.scene.objects.active = base

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#X方向
########################################
class FUJIWARATOOLBOX_363285(bpy.types.Operator):#X方向
    """選択オブジェクトに対して、アクティブオブジェクト（最後に選択したオブジェクト）のローカル方向へ穴あけ"""
    bl_idname = "fujiwara_toolbox.command_363285"
    bl_label = "X方向"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        X = 0
        Y = 1
        Z = 2

        makehole(self,X)
        
        return {'FINISHED'}
########################################






########################################
#Y方向
########################################
class FUJIWARATOOLBOX_598811(bpy.types.Operator):#Y方向
    """選択オブジェクトに対して、アクティブオブジェクト（最後に選択したオブジェクト）のローカル方向へ穴あけ"""
    bl_idname = "fujiwara_toolbox.command_598811"
    bl_label = "Y方向"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        X = 0
        Y = 1
        Z = 2

        makehole(self,Y)

        return {'FINISHED'}
########################################


########################################
#Z方向
########################################
class FUJIWARATOOLBOX_709032(bpy.types.Operator):#Z方向
    """選択オブジェクトに対して、アクティブオブジェクト（最後に選択したオブジェクト）のローカル方向へ穴あけ"""
    bl_idname = "fujiwara_toolbox.command_709032"
    bl_label = "Z方向"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        X = 0
        Y = 1
        Z = 2

        makehole(self,Z)
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#アクティブなバウンドで穴を追加
########################################
class FUJIWARATOOLBOX_4695(bpy.types.Operator):#バウンドで穴を追加
    """バウンドで穴を追加"""
    bl_idname = "fujiwara_toolbox.command_4695"
    bl_label = "バウンドで穴を追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_BOOLEAN",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
        
        bound = fjw.active()
        bound.select = False

        #ターゲット群に穴あけ
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj.type == "MESH":
                bpy.ops.object.modifier_add(type='BOOLEAN')
                mod = fjw.getnewmod(obj)
                mod.operation = 'DIFFERENCE'
                mod.object = bound


        return {'FINISHED'}
########################################








########################################
#バウンドからフチ作成
########################################
class FUJIWARATOOLBOX_916367(bpy.types.Operator):#バウンドからフチ作成
    """バウンドからフチ作成"""
    bl_idname = "fujiwara_toolbox.command_916367"
    bl_label = "バウンドからフチ作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if not fjw.active_exists():
            self.report({"WARNING"},"アクティブオブジェクトが存在しません")
            return {'CANCELLED'}


        bound = bpy.context.scene.objects.active
        if bound.type != "MESH" or "BoundHole" not in bound.name:
            self.report({"WARNING"},"生成したバウンドを選択してください")
            return {'CANCELLED'}

        if bound.children[0] == None:
            self.report({"WARNING"},"バウンドの対象がありません")
            return {'CANCELLED'}


        target = bound.children[0]

        X = 0
        Y = 1
        Z = 2

        direction = 0
        if "_X" in bound.name:
            direction = 0
        if "_Y" in bound.name:
            direction = 1
        if "_Z" in bound.name:
            direction = 2

        
        #選択リフレッシュ
        for obj in bpy.data.objects:
            obj.select = False

        bound.select = True
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        rim = bpy.context.active_object
        rim.name = "BoundRim"

        #表示・レンダ設定
        rim.hide_render = False
        rim.draw_type = 'TEXTURED'


        #サイズは親にあわせる
        rim.dimensions[direction] = target.dimensions[direction]
 
        #選択リフレッシュ
        for obj in bpy.data.objects:
            obj.select = False
        #バウンドにつける
        rim.select = True
        bpy.context.scene.objects.active = bound
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        #選択リフレッシュ
        for obj in bpy.data.objects:
            obj.select = False

        rim.select = True
        bpy.context.scene.objects.active = rim






        #direction方向の面を消す

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        data = rim.data
        bm = bmesh.from_edit_mesh(data)
        #選択リフレッシュ
        for v  in bm.verts:
        	v.select = False
        for e in bm.edges:
        	e.select = False
        for f in bm.faces:
        	f.select = False

        #特定の特徴を持つものを選択
        #normalがdirection方向のものを選択
        dirnormal = mathutils.Vector((0.0, 0.0, 0.0))
        dirnormal[direction] = 1.0

        for f in bm.faces:
            if f.normal == dirnormal or f.normal == dirnormal * -1:
                f.select = True

        bmesh.update_edit_mesh(data)
        bpy.ops.mesh.delete(type='FACE')

        #選択リフレッシュ
        for obj in bpy.data.objects:
           obj.select = False
        #フチをつける
        bpy.context.scene.objects.active = rim
        rim.select = True
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        fjw.getnewmod(rim).thickness = -0.05
        rim.scale[direction] += 0.005




        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#X+フチ
########################################
class FUJIWARATOOLBOX_786035(bpy.types.Operator):#X+フチ
    """X+フチ"""
    bl_idname = "fujiwara_toolbox.command_786035"
    bl_label = "X+フチ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        X = 0
        Y = 1
        Z = 2

        makehole(self,X)
        base = bpy.context.active_object
        bound = base.parent
        

        #選択リフレッシュ
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = bound
        bound.select = True
        #バウンドからフチ作成
        bpy.ops.fujiwara_toolbox.command_916367()



        return {'FINISHED'}
########################################


########################################
#Y+フチ
########################################
class FUJIWARATOOLBOX_689631(bpy.types.Operator):#Y+フチ
    """Y+フチ"""
    bl_idname = "fujiwara_toolbox.command_689631"
    bl_label = "Y+フチ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        X = 0
        Y = 1
        Z = 2

        makehole(self,Y)
        base = bpy.context.active_object
        bound = base.parent
        

        #選択リフレッシュ
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = bound
        bound.select = True
        #バウンドからフチ作成
        bpy.ops.fujiwara_toolbox.command_916367()
        
        return {'FINISHED'}
########################################

########################################
#Z+フチ
########################################
class FUJIWARATOOLBOX_917716(bpy.types.Operator):#Z+フチ
    """Z+フチ"""
    bl_idname = "fujiwara_toolbox.command_917716"
    bl_label = "Z+フチ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}
 
        X = 0
        Y = 1
        Z = 2

        makehole(self,Z)
        base = bpy.context.active_object
        bound = base.parent

       

        #選択リフレッシュ
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = bound
        bound.select = True
        #バウンドからフチ作成
        bpy.ops.fujiwara_toolbox.command_916367()
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#選択物の穴をクリア
########################################
class FUJIWARATOOLBOX_120963(bpy.types.Operator):#選択物の穴をクリア
    """選択物からブールモディファイアを取り除きます"""
    bl_idname = "fujiwara_toolbox.command_120963"
    bl_label = "選択物の穴をクリア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="X",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               for mod in obj.modifiers:
                   if mod.type == "BOOLEAN":
                       bpy.ops.object.modifier_remove(modifier=mod.name)
        
        return {'FINISHED'}
########################################
















#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("屋根ツール").icon = "TRIA_UP"
############################################################################################################################

########################################
#
########################################
class FUJIWARATOOLBOX_318882(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_318882"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/wu-gentsuru")
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
roofbase = None

########################################
#基部指定
########################################
class FUJIWARATOOLBOX_722997(bpy.types.Operator):#基部指定
    """基部指定"""
    bl_idname = "fujiwara_toolbox.command_722997"
    bl_label = "屋根の基部を指定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        obj = bpy.context.scene.objects.active
        global roofbase
        roofbase = obj
        
        self.report({"INFO"},obj.name + "を屋根の基部に指定しました")
        return {'FINISHED'}
########################################



########################################
#選択した壁に屋根を設置
########################################
class FUJIWARATOOLBOX_832778(bpy.types.Operator):#選択した壁に屋根を設置
    """選択した壁に屋根を設置"""
    bl_idname = "fujiwara_toolbox.command_832778"
    bl_label = "選択した壁に屋根を設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        global roofbase
       #メッシュ以外除外
        if(fjw.reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:" + self.bl_idname)
            return {'CANCELLED'}

        if roofbase == None:
            self.report({"WARNING"},"屋根の基部が未指定です:" + self.bl_idname)
            return {'CANCELLED'}

        #ターゲットの確保
        targets = []
        for obj in bpy.context.selected_objects:
            targets.append(obj)

        #ターゲットを複製してバウンド化
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        dup = bpy.context.active_object
        bpy.ops.object.join()
        #親子付を一回解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


        #原点をバウンドの中心に移動
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        #原点を下に
        fjw.origin_floorize()



        fjw.deselect()


        #屋根を基部から複製する
        bpy.context.scene.objects.active = roofbase
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        roofbase.select = True

        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        dup_roofbase = bpy.context.active_object

        #モディファイア・トランスフォームの適用
        fjw.apply_mods()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


        fjw.deselect()

        dup_roofbase.select = True
        #原点をバウンドの中心に移動
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        #原点を下に
        fjw.origin_floorize()

        

        #位置
        dup_roofbase.location = dup.location
        dup_roofbase.location.z += dup.dimensions.z
        #サイズ
        dup_roofbase.dimensions = (dup.dimensions.x,dup.dimensions.y,dup_roofbase.dimensions.z)
        #dup_roofbase.dimensions.y = dup.dimensions.y
        #self.report({"INFO"},"dup"+str(dup.dimensions))
        #self.report({"INFO"},"dup_roofbase"+str(dup_roofbase.dimensions))

        #dupの削除
        fjw.deselect()
        fjw.activate(dup)
        dup.select = True
        bpy.ops.object.delete(use_global=False)

        fjw.deselect()
        #部屋の床があれば親子づけ
        wall = targets[0]
        bpy.context.scene.objects.active = wall
        wall.select = True
        bpy.ops.object.select_grouped(type='PARENT')

        room = None
        for obj in bpy.context.selected_objects:
            if "room" in obj.name:
                room = obj

        #ないのでここで終わり
        if room == None:
            return {'FINISHED'}

        fjw.deselect()
        fjw.activate(room)
        dup_roofbase.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        fjw.deselect()
        fjw.activate(dup_roofbase)

        return {'FINISHED'}
########################################














uiitem("　")
#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal_sep()
#---------------------------------------------

############################################################################################################################
uiitem("マップセットアップツール")
############################################################################################################################

########################################
#
########################################
class FUJIWARATOOLBOX_824647(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_824647"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang/mappusettoapputsuru")
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
"""
メモ
MapControllerの作成
↑手動で配置よりも、なければ作成のほうがいいな



グルーピング
天北　
西　東
地南ランプ
"""


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def get_map_controller():
    active = fjw.active()
    mc = None
    for obj in bpy.context.scene.objects:
        if "MapController" == obj.name:
            if obj.library is None:
                mc = obj
    if mc is None:
        #なかったのでマップコントローラを追加する
        bpy.ops.object.armature_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=fjw.layers(0))
        mc = fjw.active()
        mc.name = "MapController"
        mc.data.bones[0].name = "Geometry"
    fjw.activate(active)
    return mc

########################################
#コントローラの追加
########################################
class FUJIWARATOOLBOX_660859(bpy.types.Operator):#コントローラの追加
    """プロキシで使うための選択オブジェクトをくくりつけるコントローラを作成する"""
    bl_idname = "fujiwara_toolbox.command_660859"
    bl_label = "コントローラの追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if bpy.context.scene.objects.active == None:
            self.report({"INFO"},"アクティブオブジェクトがありません。")
            return {'CANCELLED'}
    
        mc = get_map_controller()

        #ターゲットを確保
        target_active = fjw.active()

        targets = []
        selection = fjw.get_selected_list()
        for obj in selection:
            if obj == mc:
                continue
            #親があるものを除外
            if obj.parent != None:
                #parentがありかつ、それがmcではない
                #mcがもともとなかった場合はNoneと比べるわけで、!=Noneは確かだからOK.
                #アクティブオブジェクトは除外しない
                if obj.parent != mc and obj != target_active:
                    obj.select = False
                    continue
            targets.append(obj)

        mc = get_map_controller()
        mc.select = False
        mc.show_x_ray = True
        mc.draw_type = 'WIRE'
        mc.hide = False

        #くくりつける対象のボーンの存在確認
        if target_active.name not in mc.data.bones:
            #なかった
            #カーソル設置
            fjw.deselect()
            fjw.activate(target_active)
            target_active.select = True
            bpy.ops.view3d.snap_cursor_to_selected()

            bpy.context.scene.objects.active = mc
            fjw.mode("EDIT")

            #bpy.ops.armature.bone_primitive_add()

            #ここが問題 プリミティブ追加してもそれがアクティブボーンになるわけじゃない
            #bone = mc.data.bones.active
            #https://blenderartists.org/forum/showthread.php?382277-creating-armature-from-script

            #これもやっぱだめ！生成が使いづらすぎる。
            #bone = mc.data.edit_bones.new(target_active.name)
            #self.report({"INFO"},"これ"+mc.name + "/" +bone.name)

            #リスト作って新規の確認したほうがマシ
            already = []
            for b in mc.data.bones:
                already.append(b.name)

            bpy.ops.armature.bone_primitive_add()

            #一回なんかしらしとかないと骨リストが更新されない
            fjw.mode("OBJECT")
            fjw.mode("EDIT")
            
            bone = None
            for b in mc.data.bones:
                self.report({"INFO"},b.name)

                if b.name not in already:
                    bone = b
                    break

            bone.name = target_active.name

            #一回なんかしらしとかないと骨リストが更新されない
            fjw.mode("OBJECT")
            fjw.mode("EDIT")

            #ジオメトリ用にくくりつける
            mc.data.edit_bones[target_active.name].select = True
            bone_geo = mc.data.edit_bones[0]
            bone_geo.tail.z = -1

            mc.data.edit_bones.active = bone_geo
            #bone_geo.select = True
            bpy.ops.armature.parent_set(type='OFFSET')

            #アクティブとかを戻す
            mc.data.bones.active = bone
            mc.data.edit_bones.active = mc.data.edit_bones[target_active.name]
            mc.data.edit_bones[0].select = False
            mc.data.bones[0].select = False
            self.report({"INFO"},str(mc.data.bones.active))

            #ロールをZ軸の回転に合わせる
            mc.data.edit_bones[target_active.name].roll = target_active.rotation_euler[2]

        #一回ターゲットの親子をトランスフォーム維持して解除しないと位置ズレを起こす
        fjw.deselect()
        for obj in targets:
            obj.select = True
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')



        bpy.context.scene.objects.active = mc
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        mc.data.bones.active = mc.data.bones[target_active.name]



        for obj in targets:
            obj.select = True

        bpy.ops.object.parent_set(type='BONE_RELATIVE')


        return {'FINISHED'}
########################################


########################################
#個別に
########################################
class FUJIWARATOOLBOX_914007(bpy.types.Operator):#個別に
    """個別に"""
    bl_idname = "fujiwara_toolbox.command_914007"
    bl_label = "個別に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        selection = fjw.get_selected_list()

        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            bpy.ops.fujiwara_toolbox.command_660859()


        return {'FINISHED'}
########################################







#########################################
##→隠す
#########################################
#class FUJIWARATOOLBOX_333315(bpy.types.Operator):#→隠す
#    """→隠す"""
#    bl_idname = "fujiwara_toolbox.command_333315"
#    bl_label = "→隠す"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")

#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.ops.fujiwara_toolbox.command_660859()
#        bpy.context.active_object.select = False
#        for obj in bpy.context.selected_objects:
#            obj.hide_render = True
#        bpy.ops.object.hide_view_set(unselected=False)


#        return {'FINISHED'}
#########################################


########################################
#子を隠す
########################################
class FUJIWARATOOLBOX_910973(bpy.types.Operator):#子を隠す
    """子を隠す"""
    bl_idname = "fujiwara_toolbox.command_910973"
    bl_label = "子を隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        if "MapController" in bpy.data.objects:
            mc = bpy.data.objects["MapController"]
            fjw.activate(mc)
            fjw.mode("OBJECT")

            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            for obj in fjw.get_selected_list():
                obj.hide = True


        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def get_mapgeo(name):
    mapgeo = None
    mgname = "mapgeo_" + name
    flag_geoexists = False

    for obj in bpy.data.objects:
        if obj.name == mgname and obj.library is None:
            mapgeo = obj
            fjw.activate(mapgeo)
            flag_geoexists = True
    else:
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.3, view_align=False, location=bpy.context.space_data.cursor_location, layers=fjw.layers(0))
        mapgeo = fjw.active()
        mapgeo.name = mgname
    mapgeo.show_x_ray = True
    mapgeo.hide = False
    return mapgeo, flag_geoexists

def maputil_ungroup_target(target):
    selection = fjw.get_selected_list()
    fjw.ungroup(target, selection)

def maputil_ungroup():
    active = fjw.active()
    print("maputil_ungroup")
    print(active)
    maputil_ungroup_target('天')
    maputil_ungroup_target('地')
    maputil_ungroup_target('北')
    maputil_ungroup_target('南')
    maputil_ungroup_target('西')
    maputil_ungroup_target('東')
    maputil_ungroup_target('床上')
    fjw.activate(active)

def maputil_group(name):
    active = fjw.active()
    selection = fjw.get_selected_list()
    fjw.group(name, selection)

    #emptyがなければ作成してペアレントつけて、さらにそのemptyをコントローラに紐付ける
    pos = active
    print("pos")
    print(pos)
    bpy.ops.view3d.snap_cursor_to_selected()

    targets = []
    for obj in bpy.context.selected_objects:
        if obj.name == "MapController":
            continue
        targets.append(obj)


    mapgeo, flag_geoexists = get_mapgeo(name)

    for target in targets:
        target.select = True

    #レイヤーをまとめる。
    tolayern = 0

    if name == "天":
        tolayern = 4
    if name == "地":
        tolayern = 14
    if name == "北":
        tolayern = 2
    if name == "南":
        tolayern = 12
    if name == "西":
        tolayern = 11
    if name == "東":
        tolayern = 13
    if name == "床上":
        tolayern = 10

    bpy.context.scene.layers[tolayern] = True

    for obj in bpy.context.selected_objects:
        obj.layers[tolayern] = True
        for l in range(0,20):
            if l != tolayern:
                obj.layers[l] = False

    #親子付処理
    children = []
    selection = fjw.get_selected_list()
    for obj in selection:
        pass
        #親がない
        if obj.parent == None:
            children.append(obj)
            continue
        #親が選択内になければよい
        if obj.parent not in selection:
            children.append(obj)
            continue

    fjw.deselect()
    fjw.select(children)

    print("###parenting")
    print(pos)
    #元のアクティブオブジェクトは除外しない
    pos.select = True

    #mapgeoに親子づけ
    print("mapgeo")
    print(mapgeo)
    fjw.activate(mapgeo)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    for obj in bpy.data.objects:
        obj.select = False

    mapgeo.hide = False
    mapgeo.select = True

    #ジオメトリが既に存在してた時はコントローラの追加はしないでおく
    if not flag_geoexists:
        bpy.ops.fujiwara_toolbox.command_660859() #コントローラの追加

    fjw.mode("OBJECT")
    bpy.context.scene.layers[tolayern] = False
    fjw.activate(active)

########################################
#
########################################
class FUJIWARATOOLBOX_998900(bpy.types.Operator):#
    """　"""
    bl_idname = "fujiwara_toolbox.command_998900"
    bl_label = "　"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################

########################################
#北
########################################
class FUJIWARATOOLBOX_359173(bpy.types.Operator):#北
    """北"""
    bl_idname = "fujiwara_toolbox.command_359173"
    bl_label = "北"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="北")
        
        return {'FINISHED'}
########################################

########################################
#天
########################################
class FUJIWARATOOLBOX_328016(bpy.types.Operator):#天
    """天"""
    bl_idname = "fujiwara_toolbox.command_328016"
    bl_label = "天"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="天")

        return {'FINISHED'}
########################################





#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#西
########################################
class FUJIWARATOOLBOX_787053(bpy.types.Operator):#西
    """西"""
    bl_idname = "fujiwara_toolbox.command_787053"
    bl_label = "西"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="西")
        
        return {'FINISHED'}
########################################

########################################
# 解除
########################################
class FUJIWARATOOLBOX_826128(bpy.types.Operator):#
    """ """
    bl_idname = "fujiwara_toolbox.command_826128"
    bl_label = "解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #アーマチュアを除外
        for obj in bpy.context.selected_objects:
            if obj.type == "ARMATURE":
                obj.select = False

        targets = []
        for obj in bpy.context.selected_objects:
            targets.append(obj)


        maputil_ungroup()
        
        #マップジオメトリのリスト
        mapgeos = []
        mgname = "mapgeo_" + "天"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])
        mgname = "mapgeo_" + "地"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])
        mgname = "mapgeo_" + "北"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])
        mgname = "mapgeo_" + "南"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])
        mgname = "mapgeo_" + "東"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])
        mgname = "mapgeo_" + "西"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])
        mgname = "mapgeo_" + "床上"
        if mgname in bpy.data.objects:
            mapgeos.append(bpy.data.objects[mgname])


        for target in targets:
            for obj in bpy.data.objects:
                obj.select = False
            bpy.context.scene.objects.active = target
            target.select = True

            #ターゲットが既にマップジオメトリにくくりつけられている
            if target.parent in mapgeos:
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')




        return {'FINISHED'}
########################################

########################################
#東
########################################
class FUJIWARATOOLBOX_292140(bpy.types.Operator):#東
    """東"""
    bl_idname = "fujiwara_toolbox.command_292140"
    bl_label = "東"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="東")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#
########################################
class FUJIWARATOOLBOX_618798(bpy.types.Operator):#
    """ """
    bl_idname = "fujiwara_toolbox.command_618798"
    bl_label = "床上"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="床上")
        
        return {'FINISHED'}
########################################


########################################
#南
########################################
class FUJIWARATOOLBOX_291348(bpy.types.Operator):#南
    """南"""
    bl_idname = "fujiwara_toolbox.command_291348"
    bl_label = "南"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="南")
        
        return {'FINISHED'}
########################################

########################################
#地
########################################
class FUJIWARATOOLBOX_93549(bpy.types.Operator):#地
    """地"""
    bl_idname = "fujiwara_toolbox.command_93549"
    bl_label = "地"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        maputil_ungroup()
        maputil_group(name="地")
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#メイングループ化
########################################
class FUJIWARATOOLBOX_288056(bpy.types.Operator):#ファイル名でグループ化
    """選択物をMainGroupにグループ化する。カメラは除外される。選択物がない場合は全てのオブジェクトを自動でグループ化する"""
    bl_idname = "fujiwara_toolbox.command_288056"
    bl_label = "メイングループ化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.group("MainGroup")

        return {'FINISHED'}
########################################


########################################
#プロクシ作成
########################################
class FUJIWARATOOLBOX_424289(bpy.types.Operator):#プロクシ作成
    """プロクシ作成"""
    bl_idname = "fujiwara_toolbox.command_424289"
    bl_label = "プロクシ作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        map = fjw.active()

        if map.type != "EMPTY":
            self.report({"INFO"},"リンクしたオブジェクトを指定して下さい。")
            return {'CANCELLED'}


        fjw.deselect()
        map.select = True

        #リンクデータのオブジェクト
        inlinkobjects = map.dupli_group.objects
        
        mp_name = ""
        for obj in inlinkobjects:
            if "MapController" in obj.name:
                mp_name = obj.name
                break

        if mp_name == "":
            self.report({"INFO"},"MapControllerがありません。")
            return {'CANCELLED'}

        bpy.ops.object.proxy_make(object=mp_name)

        mapcontroller = fjw.active()
        map.select = True

        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        mapcontroller.show_x_ray = True


        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("イージーデコツール（α）")
############################################################################################################################
"""

スイープツール
・選択辺の複製分離→カーブにする。拡縮適用。←しないと、ベベルがおかしくなる
・選択オブジェクトをベベルオブジェクトに。


イージーデコツール
グリペンから生成したカーブ
・スキンつけ、細くする　メッシュ変換・スキン。
・太く　細く
・デシメーション    全選択→チェッカー選択解除→ディゾルブで一段階デシメーションできる。
        オブジェクトモードだったら勝手にやってオブジェクトモードに戻る。、編集モードだったら選択内容に対して実行する。



"""


########################################
#イージーデコ
########################################
class FUJIWARATOOLBOX_741025(bpy.types.Operator):#イージーデコ
    """イージーデコ"""
    bl_idname = "fujiwara_toolbox.command_741025"
    bl_label = "イージーデコ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.deselect()
        #グリースペンシルのアクティブレイヤーから変換してデコる。
        #gp = bpy.context.scene.grease_pencil
        #gp_layer = gp.layers.active
        #ってそもそもアクティブレイヤー取得する必要なくないか？変換して削除すればそれでいいのでは
        bpy.ops.gpencil.convert(type='POLY', use_timing_data=True)
        bpy.ops.gpencil.layer_remove()



        #デコ処理
        for obj in fjw.get_selected_list():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            fjw.activate(obj)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            if obj.type == "CURVE":
                bpy.ops.object.convert(target='MESH')

            if obj.type != "MESH":
                continue

            mod_exists = False
            for mod in obj.modifiers:
                if mod.type == "SKIN":
                    mod_exists = True
                    break

            if mod_exists:
                continue

            bpy.ops.object.modifier_add(type='SUBSURF')
            for mod in obj.modifiers:
                if mod.type == "SUBSURF":
                    mod.levels = 2
                    mod.render_levels = 4


            bpy.ops.object.modifier_add(type='SKIN')
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            skinsize = 0.01
            bpy.ops.transform.skin_resize(value=(skinsize, skinsize, skinsize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            #入りヌキ無理かな…
            #obj.data.vertices[0].select = True
            #obj.data.vertices[len(obj.data.vertices)-1].select = True
            #skinsize = 0.001
            #bpy.ops.transform.skin_resize(value=(skinsize, skinsize,
            #skinsize), constraint_axis=(False, False, False),
            #constraint_orientation='GLOBAL', mirror=False,
            #proportional='DISABLED', proportional_edit_falloff='SMOOTH',
            #proportional_size=1)
            #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)





        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#細く
########################################
class FUJIWARATOOLBOX_117841(bpy.types.Operator):#細く
    """細く"""
    bl_idname = "fujiwara_toolbox.command_117841"
    bl_label = "細く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.reject_notmesh()
        for obj in fjw.get_selected_list():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            fjw.activate(obj)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            skinsize = 0.5
            bpy.ops.transform.skin_resize(value=(skinsize, skinsize, skinsize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        return {'FINISHED'}
########################################


########################################
#太く
########################################
class FUJIWARATOOLBOX_961850(bpy.types.Operator):#太く
    """太く"""
    bl_idname = "fujiwara_toolbox.command_961850"
    bl_label = "太く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.reject_notmesh()
        for obj in fjw.get_selected_list():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            fjw.activate(obj)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.select_all(action='SELECT')
            skinsize = 2
            bpy.ops.transform.skin_resize(value=(skinsize, skinsize, skinsize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#デシメーション
########################################
class FUJIWARATOOLBOX_352656(bpy.types.Operator):#デシメーション
    """デシメーション"""
    bl_idname = "fujiwara_toolbox.command_352656"
    bl_label = "デシメーション"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        fjw.reject_notmesh()
        for obj in fjw.get_selected_list():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            fjw.activate(obj)

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.context.scene.tool_settings.mesh_select_mode = [True,False,False]
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.select_nth()
            bpy.ops.mesh.dissolve_verts()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#垂直ミラー
########################################
class FUJIWARATOOLBOX_501038(bpy.types.Operator):#垂直ミラー
    """カーソル位置を中心に垂直ミラー"""
    bl_idname = "fujiwara_toolbox.command_501038"
    bl_label = "垂直ミラー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        for obj in fjw.get_selected_list():
            fjw.activate(obj)
            bpy.ops.object.modifier_add(type='MIRROR')
            mod = fjw.getnewmod(obj)
            mod.use_z = True



        
        return {'FINISHED'}
########################################

########################################
#水平ミラー
########################################
class FUJIWARATOOLBOX_566394(bpy.types.Operator):#水平ミラー
    """水平ミラー"""
    bl_idname = "fujiwara_toolbox.command_566394"
    bl_label = "水平ミラー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        for obj in fjw.get_selected_list():
            fjw.activate(obj)
            bpy.ops.object.modifier_add(type='MIRROR')
            mod = fjw.getnewmod(obj)
            mod.use_y = True
        
        return {'FINISHED'}
########################################





















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem(" ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical_sep()
#---------------------------------------------
########################################
#ヘルプ
########################################
class FUJIWARATOOLBOX_588048(bpy.types.Operator):#ヘルプ
    """ヘルプ"""
    bl_idname = "fujiwara_toolbox.command_588048"
    bl_label = "インデックス"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUESTION",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        webbrowser.open("https://sites.google.com/site/ghostbrain3dex/home/room-tools/roomtoolsno-shii-fang")
        return {'FINISHED'}
########################################















#def RoomToolsView3Dheader(self, context):
#    layout = self.layout
#    row = layout.row(align = True)
#    row.operator("fujiwara_toolbox.command_288056",text="グループ化")
#    row.operator("fujiwara_toolbox.command_424289",text="プロクシ作成")

############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    #bpy.types.VIEW3D_HT_header.append(RoomToolsView3Dheader)
    pass
def sub_unregistration():
    pass

def register():    #登録
    bpy.utils.register_module(__name__)
    #bpy.types.VIEW3D_HT_header.remove(RoomToolsView3Dheader)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()