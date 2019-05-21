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
from fujiwara_toolbox_modules.fjw import JsonTools

# assetdir = fujiwara_toolbox.conf.assetdir
assetdir = ""

#コードtips
#
#bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
#mode (enum in [‘OBJECT’, ‘EDIT’, ‘POSE’, ‘SCULPT’, ‘VERTEX_PAINT’,
#‘WEIGHT_PAINT’, ‘TEXTURE_PAINT’, ‘PARTICLE_EDIT’], (optional)) – Mode
#
#obj = bpy.context.active_object
#bpy.context.scene.objects.active = obj
#
#for obj in bpy.context.selected_objects:
#
#for obj in bpy.data.objects:

#dir = os.path.dirname(bpy.data.filepath)


#self.report({"INFO"},"")



#import mypac.filewrap
#mypac.filewrap.debug = True


#http://blender.stackexchange.com/questions/717/is-it-possible-to-print-to-the-report-window-in-the-info-view
#info出力はself.report({"INFO"},str)で！

#http://matosus304.blog106.fc2.com/blog-entry-257.html
bl_info = {
    "name": "fjw.Myaddon",
    "description": "スクリプトの概要",
    "author": "作者名",
    "version": (1, 0),
    "blender": (2, 68, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=",
    "category": "Learnbgame"
}


from bpy.app.handlers import persistent

settings = {"test":""}

@persistent
def load_handler(context):
    test = settings

def dummy():
    pass


#外部スクリプト実行
#__file__が、関数が定義されてるスクリプトのパスを返すのでここで指定
def exec_externalutils(scriptname):
    #プレビューレンダをバックグラウンドに投げとく
    blenderpath = sys.argv[0]
    scrpath = fjw.get_dir(__file__) + "utils" + os.sep + scriptname
    cmdstr = fjw.qq(blenderpath) + " " + fjw.qq(bpy.data.filepath) + " -b " + " -P " + fjw.qq(scrpath)
    print("********************")
    print("__file__:" + __file__)
    print("scrpath:" + scrpath)
    print("cmdstr:" + cmdstr)
    print("********************")
    subprocess.Popen(cmdstr)
    pass



SelectedFile = ""
FileBrouserExecute = dummy

##############################################################
#ファイルセレクター
#
#FileBrouserExec(func)にファイルロード後に実行する関数を指定して開く
#SelectedFileにロードしたパスが入ってる。
#
##############################################################
#http://www.blender.org/documentation/blender_python_api_2_57_release/bpy.types.Operator.html#calling-a-file-selector
#Calling a File Selector
class FileBrouser(bpy.types.Operator):#ファイルセレクター
    """Test exporter which just writes hello world"""
    bl_idname = "file.selector"
    bl_label = "File Selector"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    #filepath =bpy.context.blend_data.filepath
    directory = bpy.props.StringProperty(subtype="DIR_PATH")#"c:\\"
    #あらかじめディレクトリ指定するの無理みたい

    @classmethod
    #optional
    def poll(cls, context):
        return context.object is not none

    def execute(self, context):
        print("execute")
        global SelectedFile
        SelectedFile = self.filepath
        FileBrouserExecute()



        #dbg
        #import mypac.filewrap
        #mypac.filewrap.debug = True
        #mypac.filewrap.dbg("")
        #mypac.filewrap.dbg("")
        #mypac.filewrap.dbg("self")
        #mypac.filewrap.dbg(self)
        #mypac.filewrap.dbg("self.filepath")
        #mypac.filewrap.dbg(self.filepath)
        #mypac.filewrap.dbg("self.directory")
        #mypac.filewrap.dbg(self.directory)

        print("execute おわり")
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
#        context.window_manager.fileselect_add(self,directory=bpy.context.blend_data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



# Register and add to the file selector
bpy.utils.register_class(FileBrouser)
#bpy.types.INFO_MT_file_export.append(menu_func)


# test call
#bpy.ops.file.selector('INVOKE_DEFAULT')


#ファイルブラウザに実行する関数を渡して開く
def FileBrouserExec(exefunc):
    print("FileBrouserExec")
    global FileBrouserExecute
    FileBrouserExecute = exefunc
    bpy.ops.file.selector('INVOKE_DEFAULT')
    return




############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#ui表示上の各種コンフィグを記述するクラス。ボタンリストに代替。
#これをリスト化すればいい！
#途中でこのコンフィグだけのやつ挟めばラベルとか挿入できる
"""
uicategory{}
みたいのを用意して[]をいれていく
uiitemlistには新規で作ったのを指定すればどんどんカテゴリわけされていく

label時に新規登録処理をしていきたい

label:[]的な感じ
"""

uicategories = OrderedDict()

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
    def __init__(self,label="",iscat=False):
        global uiitemList
        global uicategories
      
        if label != "":
            self.type = "label"
            self.label = label

            if iscat:
                #uicategoryに登録
                uicategories[label] = []
                uiitemList = uicategories[label]

        uiitemList.append(self)
    
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



dialog_uicat = ""
#http://blender.stackexchange.com/questions/6512/how-to-call-invoke-popup
class DialogPanel(bpy.types.Operator):
    """ダイアログ"""
    bl_idname = "object.dialog"
    bl_label = "ダイアログ"
    bl_options = {'REGISTER', 'UNDO'}


    def invoke(self, context, event):
        #メニューのペンディングに使えるぞ！？
        #return context.window_manager.invoke_props_dialog(self)
        return context.window_manager.invoke_popup(self,width=500) 


    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        self.report({"INFO"},"called")
        global uicategories
        global dialog_uicat
        uiitemList = uicategories[dialog_uicat]

        l = self.layout
        r = l.row()
        #b = r.box()
        b = r

        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        active = cols

        #ペンディング
        #active.label(text="")
        active = active.row(align=True)
        #active.label(text="")
        active.operator("fujiwara_toolbox.command_30808",icon="PINNED",text="")

        #縦並び
        #cols = b.column(align=True)
        #active = cols.column(align=True)

        for item in uiitemList:
            #スキップ処理
            if item.mode == "none":
                continue
            
            #if item.mode == "edit":
                ##編集モード以外飛ばす
                #if bpy.context.edit_object != None:
                #    continue
            
            #縦横
            if item.type == "fix":
                if item.direction == "vertical":
                    active = cols.column(align=True)
                if item.direction == "horizontal":
                    active = active.row(align=True)
                continue
            
            #描画
            if item.type == "label":
                if item.icon != "":
                    active.label(text=item.label, icon=item.icon)
                else:
                    active.label(text=item.label)
                active = cols.column(align=True)

            if item.type == "button":
                if item.icon != "":
                    active.operator(item.idname, icon=item.icon)
                else:
                    active.operator(item.idname)



#メインパネル
class MyaddonView3DPanel(bpy.types.Panel):#メインパネル
    bl_label = "メインパネル"
    bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    calltype = "PANEL"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.maintools

    def draw(self, context):
        l = self.layout
        r = l.row()
        #b = r.box()
        b = r

        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        active = cols

        #超よく使う
        active = cols.column(align=True)
        active.label(text="クイック")
        active = active.row(align=True)
        active.operator("fujiwara_toolbox.command_490317",text="保存",icon="FILE_TICK")
        active.operator("fujiwara_toolbox.command_559881",text="保存して開き直す",icon="FILE_REFRESH")
        # active.operator("fujiwara_toolbox.command_960554",text="BGレンダ")
        # active.operator("pageutils.topage",text="ページに戻る")
        #active.operator("fujiwara_toolbox.command_420416",text="+辺")
        active = cols.column(align=True)
        active = active.row(align=True)
        #roomtools
        active.operator("fujiwara_toolbox.command_288056",text="メイングループ化")#グループ化
        #maintools内
        # active.operator("fujiwara_toolbox.command_b424289a",text="Proxy")#プロクシ作成
        active.operator("fujiwara_toolbox.command_248120",text="Full Proxy")#プロクシ作成
        active.operator("fujiwara_toolbox.command_199238",text="Lamp Proxy")#Lamp Proxy
        active = cols.row(align=True)
        active.operator("fujiwara_toolbox.command_286013",text="複製を実体化")#複製を実体化
        active = cols.row(align=True)
        active.operator("fujiwara_toolbox.command_759926",icon="MESH_TORUS")
        active.operator("fujiwara_toolbox.command_700665",icon="MESH_ICOSPHERE")
        active.operator("fujiwara_toolbox.command_194057",icon="MESH_ICOSPHERE")
        active.operator("fujiwara_toolbox.command_286488",icon="MESH_ICOSPHERE")


        active = cols.row(align=True)
        active.label(text="")


        #ダイアログ呼び出し時は描画させたくない
        if self.calltype == "PANEL":
            active = cols.row(align=True)
            active.label(text="ペンディング",icon="PINNED")
            #クリアボタン
            active.operator("fujiwara_toolbox.command_114105",icon="UNPINNED",text="")
            active = cols.column(align=True)
            #ペンディングされたUIの描画
            for uicat in pendings:
                uiitemList = uicategories[uicat]
                for item in uiitemList:
                    #スキップ処理
                    if item.mode == "none":
                        continue
                    #if item.mode == "edit":
                        ##編集モード以外飛ばす
                        #if bpy.context.edit_object != None:
                        #    continue
                    #縦横
                    if item.type == "fix":
                        if item.direction == "vertical":
                            active = cols.column(align=True)
                        if item.direction == "horizontal":
                            active = active.row(align=True)
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

        active = cols.row(align=True)
        active.label(text="メイン")
        for uicat in uicategories:
            uiitemList = uicategories[uicat]
            for item in uiitemList:
                #スキップ処理
                if item.mode == "none":
                    continue
            
                #if item.mode == "edit":
                    ##編集モード以外飛ばす
                    #if bpy.context.edit_object != None:
                    #    continue
            
                #縦横
                #if item.type == "fix":
                    #if item.direction == "vertical":
                    #    active = cols.column(align=True)
                    #if item.direction == "horizontal":
                    #    active = active.row(align=True)
                    #continue
            
                #描画
                if item.type == "label":
                    #通常はvertical。horizontalは続くボタンは""を指定。
                    if item.direction == "vertical":
                        active = cols.column(align=True)
                    if item.direction == "horizontal":
                        active = cols.column(align=True)
                        active = active.row(align=True)

                    if item.icon != "":
                        if item.idname != "":
                            active.operator(item.idname, icon=item.icon)
                        else:
                            active.label(text=item.label, icon=item.icon)
                        
                    else:
                        if item.idname != "":
                            active.operator(item.idname)
                        #else:
                        #    active.label(text=item.label)
                #if item.type == "button":
                #    if item.icon != "":
                #        active.operator(item.idname, icon=item.icon)
                #    else:
                #        active.operator(item.idname)

#UIカテゴリの実行部を外部化。いろいろ処理できるように。
def uicategory_execute(self):
    global dialog_uicat
    dialog_uicat = self.bl_label
    bpy.ops.object.dialog("INVOKE_DEFAULT")

#ペンディング用リスト。カテゴリを登録していく
#pendings = ["簡略化"]
pendings = []

########################################
#ペンディング
########################################
class FUJIWARATOOLBOX_30808(bpy.types.Operator):#ペンディング
    """ペンディング"""
    bl_idname = "fujiwara_toolbox.command_30808"
    bl_label = "ペンディング"
    bl_options = {'REGISTER', 'UNDO'}
    icon = "PINNED"
    #ui自動登録はなし

    def execute(self, context):
        global dialog_uicat
        global pendings
        pendings.append(dialog_uicat)
        return {'FINISHED'}
########################################


########################################
#クリア
########################################
class FUJIWARATOOLBOX_114105(bpy.types.Operator):#クリア
    """クリア"""
    bl_idname = "fujiwara_toolbox.command_114105"
    bl_label = "クリア"
    bl_options = {'REGISTER', 'UNDO'}
    icon = "UNPINNED"

    #ui自動登録はなし

    def execute(self, context):
        global pendings
        pendings = []
        
        return {'FINISHED'}
########################################






"""
テンプレ

############################################################################################################################
uiitem("")
############################################################################################################################


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    mode="","edit","none","all"


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

"""


#リストへのアペンドは初期化処理内でやってるからこれだけでラベル追加できる。
############################################################################################################################
############################################################################################################################
################################################################################
#UIカテゴリ
########################################
#ファイル
########################################
class CATEGORYBUTTON_111115(bpy.types.Operator):#ファイル
    """ファイル"""
    bl_idname = "fujiwara_toolbox.categorybutton_111115"
    bl_label = "ファイル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("ファイル",True)
    uiitem.button(bl_idname,bl_label,icon="BLENDER",mode="")
    uiitem.direction = "vertical"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#保存
########################################
class FUJIWARATOOLBOX_490317(bpy.types.Operator):#保存
    """保存"""
    bl_idname = "fujiwara_toolbox.command_490317"
    bl_label = "保存"
    bl_options = {'REGISTER', 'UNDO'}
    
    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="all")

    def execute(self, context):
        try:
            print(bpy.ops.wm.save_mainfile())
            pass
        except  :
            pass
        
        return {'FINISHED'}
########################################

# ########################################
# #BGレンダ
# ########################################
# class FUJIWARATOOLBOX_960554(bpy.types.Operator):#BGレンダ
#     """BGレンダ"""
#     bl_idname = "fujiwara_toolbox.command_960554"
#     bl_label = "BGレンダ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")


#     def execute(self, context):
#         #エッジオフ
#         bpy.context.scene.render.use_edge_enhance = False

#         #メイン
#         blendfilepath = bpy.data.filepath
#         blendname = os.path.splitext(os.path.basename(blendfilepath))[0]
#         renderdir = os.path.dirname(blendfilepath) + os.sep + "tmp_render" + os.sep
#         binpath = bpy.app.binary_path
#         command = fjw.qq(binpath) + " -b " + fjw.qq(blendfilepath) + " -o " + fjw.qq(renderdir + blendname + "_") + " -F PNG -x 1 -f " + str(bpy.context.scene.frame_current)
#         self.report({"INFO"},command)
#         #os.system(command)
#         #subprocess.call(command, shell=True)
#         subprocess.Popen(command)

#         return {'FINISHED'}
# ########################################

# ########################################
# #+辺
# ########################################
# class FUJIWARATOOLBOX_420416(bpy.types.Operator):#+辺
#     """+辺"""
#     bl_idname = "fujiwara_toolbox.command_420416"
#     bl_label = "+辺"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")


#     def execute(self, context):
#         #エッジオフ
#         bpy.context.scene.render.use_edge_enhance = True

#         #メイン
#         blendfilepath = bpy.data.filepath
#         blendname = os.path.splitext(os.path.basename(blendfilepath))[0]
#         renderdir = os.path.dirname(blendfilepath) + os.sep + "tmp_render" + os.sep
#         binpath = bpy.app.binary_path
#         command = fjw.qq(binpath) + " -b " + fjw.qq(blendfilepath) + " -o " + fjw.qq(renderdir + blendname + "_") + " -F PNG -x 1 -f " + str(bpy.context.scene.frame_current)
#         self.report({"INFO"},command)
#         #os.system(command)
#         #subprocess.call(command, shell=True)
#         subprocess.Popen(command)
        
#         return {'FINISHED'}
# ########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#保存して閉じる
########################################
class FUJIWARATOOLBOX_669544(bpy.types.Operator):#保存して閉じる
    """保存して閉じる"""
    bl_idname = "fujiwara_toolbox.command_669544"
    bl_label = "保存して閉じる"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUIT",mode="all")

    def execute(self, context):
        try:
            bpy.ops.wm.save_mainfile()
            pass
        except  :
            pass
        bpy.ops.wm.quit_blender()
        #if bpy.ops.wm.save_mainfile() == {"FINISHED"}:
        #    bpy.ops.wm.quit_blender()
        #else:
        #    printf("ERROR")
        return {'FINISHED'}
########################################

########################################
#保存して開き直す
########################################
class FUJIWARATOOLBOX_559881(bpy.types.Operator):#保存して開き直す
    """保存して開き直す"""
    bl_idname = "fujiwara_toolbox.command_559881"
    bl_label = "保存して開き直す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="all")

    def execute(self, context):
        #try:
        #    bpy.ops.wm.save_mainfile()
        #    bpy.ops.wm.revert_mainfile(use_scripts=True)
        #    pass
        #except :
        #    pass
        #bpy.ops.wm.revert_mainfile(use_scripts=True)
        #if bpy.ops.wm.save_mainfile() == {"FINISHED"}:
        #    #bpy.ops.wm.revert_mainfile()
        #    pass
        #else:
        #    return {'CANCELLED'}

        bpy.ops.wm.save_mainfile()
        bpy.ops.wm.revert_mainfile("INVOKE_DEFAULT",use_scripts=True)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#親フォルダを開く
########################################
#bpy.ops.fujiwara_toolbox.open_parent_folder() #親フォルダを開く
class FUJIWARATOOLBOX_OPEN_PARENT_FOLDER(bpy.types.Operator):
    """このblendファイルがあるフォルダを開く。"""
    bl_idname = "fujiwara_toolbox.open_parent_folder"
    bl_label = "親フォルダを開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_FOLDER",mode="")

    def execute(self, context):
        dir = os.path.dirname(bpy.data.filepath)
        os.system("EXPLORER " + dir)
        return {'FINISHED'}
########################################







# ########################################
# #100倍とか
# ########################################
# class FUJIWARATOOLBOX_463064(bpy.types.Operator):#100倍
#     """100倍"""
#     bl_idname = "fujiwara_toolbox.command_463064"
#     bl_label = "100倍とか"
#     bl_options = {'REGISTER', 'UNDO'}


#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

    
#     def execute(self, context):
#         camera = bpy.context.scene.camera
#         camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
#         camera.rotation_euler[0] = 0.8746716380119324
#         camera.rotation_euler[1] = -2.7369874260330107e-06
#         camera.rotation_euler[2] = 2.5201363563537598
        
#         bpy.ops.transform.resize(value=(10000, 10000, 10000), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
#         bpy.ops.view3d.view_selected()
#         return {'FINISHED'}
# ########################################

# ########################################
# #0.01倍
# ########################################
# class FUJIWARATOOLBOX_159343(bpy.types.Operator):#0.01倍
#     """0.0001倍"""
#     bl_idname = "fujiwara_toolbox.command_159343"
#     bl_label = "0.01倍"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         camera = bpy.context.scene.camera
#         camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
#         camera.rotation_euler[0] = 0.8746716380119324
#         camera.rotation_euler[1] = -2.7369874260330107e-06
#         camera.rotation_euler[2] = 2.5201363563537598
        
#         bpy.ops.transform.resize(value=(0.01, 0.01,0.01), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
#         bpy.ops.view3d.view_selected()
        
#         return {'FINISHED'}
# ########################################

# ########################################
# #カメラだけ
# ########################################
# class FUJIWARATOOLBOX_607395(bpy.types.Operator):#カメラだけ
#     """カメラだけ"""
#     bl_idname = "fujiwara_toolbox.command_607395"
#     bl_label = "カメラだけ"
#     bl_options = {'REGISTER', 'UNDO'}


#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

    
#     def execute(self, context):
#         camera = bpy.context.scene.camera
#         camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
#         camera.rotation_euler[0] = 1
#         camera.rotation_euler[1] = 0
#         camera.rotation_euler[2] = -1
        
#         bpy.ops.view3d.view_selected()
        
#         return {'FINISHED'}
# ########################################

# ########################################
# #いろいろ処理
# ########################################
# class FUJIWARATOOLBOX_227575(bpy.types.Operator):#いろいろ処理
#     """いろいろ処理"""
#     bl_idname = "fujiwara_toolbox.command_227575"
#     bl_label = "いろいろ処理"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

    
#     def execute(self, context):
#         bpy.context.scene.camera.data.clip_end = 100000
        
#         camera = bpy.context.scene.camera
#         camera.location = (1.3641321659088135, 0.25500816106796265, 0.7163272500038147)
#         camera.rotation_euler[0] = 1
#         camera.rotation_euler[1] = 0
#         camera.rotation_euler[2] = -1
        
#         bpy.ops.view3d.view_selected()
#         return {'FINISHED'}
# ########################################




# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------

# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------



# ########################################
# #メモ設置
# ########################################
# class FUJIWARATOOLBOX_350101(bpy.types.Operator):#メモ設置
#     """メモ設置"""
#     bl_idname = "fujiwara_toolbox.command_350101"
#     bl_label = "メモ設置"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_EMPTY",mode="")

#     def execute(self, context):
#         bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1, view_align=False, location=bpy.context.space_data.cursor_location, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
#         obj = bpy.context.scene.objects.active
#         obj.rotation_euler[1] = 3.14159
#         obj.show_name = True
#         obj.show_x_ray = True
#         obj.name = "MEMO:"
#         obj.location[2] += 1

#         #右上レイヤーにまとめる
#         obj.layers[9] = True
#         obj.layers[0] = False
#         bpy.context.scene.layers[9] = True

#         #グループ化
#         if "MEMO" not in bpy.data.groups:
#             bpy.ops.group.create(name="MEMO")
#         else:
#             bpy.data.groups["MEMO"].objects.link(obj)
        
#         return {'FINISHED'}
# ########################################









# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------


# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------



# ########################################
# #カルテレンダ
# ########################################
# class FUJIWARATOOLBOX_317755(bpy.types.Operator):#カルテレンダ
#     """カルテレンダ"""
#     bl_idname = "fujiwara_toolbox.command_317755"
#     bl_label = "カルテレンダ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")
    
#     def execute(self, context):
#         #ジオメトリの選択
#         if "ジオメトリ" not in bpy.context.scene.objects.active.name:
#             self.report({"INFO"},"素体ジオメトリを指定してください")
#             return {'FINISHED'}
#         geo = bpy.context.scene.objects.active
        
        
#         #現状保存
#         bpy.ops.wm.save_mainfile()
        
        
#         #ゼロ位置に
#         bpy.ops.object.location_clear()
#         bpy.ops.object.rotation_clear()
        
#         #カメラ位置を設定
#         cam = bpy.context.scene.camera
# #        cam.data.lens = 100
        
# #        cam.location[0] = 0
# #        cam.location[1] = -7.66724
# #        cam.location[2] = 1.58621
# #        cam.rotation_euler[0] = -1.5708
# #        cam.rotation_euler[1] = 3.14159
# #        cam.rotation_euler[2] = 3.14159
# #        cam.rotation_mode = 'XYZ'
        
# #        cam.data.shift_x = 0
# #        cam.data.shift_y = -0.188
        
        
#         #レンダ準備
#         bpy.context.scene.render.use_shadows = False
#         bpy.context.scene.render.use_raytrace = False
#         bpy.context.scene.render.use_textures = True
#         bpy.context.scene.render.use_antialiasing = False
#         bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#         bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#         bpy.context.scene.render.layers["RenderLayer"].use_freestyle = False
#         bpy.context.scene.render.use_freestyle = False
#         bpy.context.scene.render.use_edge_enhance = False
#         bpy.context.scene.render.edge_threshold = 255
        
#         dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "")
# #        name = bpy.path.display_name_from_filepath(bpy.data.filepath)
#         pathbase = dir + os.sep + "render" + os.sep + "karte_"
        
#         #正面
#         geo.rotation_euler[0] = 0
#         geo.rotation_euler[1] = 0
#         geo.rotation_euler[2] = 0
#         bpy.context.scene.render.filepath = pathbase + "front.png"
#         bpy.ops.render.render(write_still=True)
        
        
        
#         #背面
#         geo.rotation_euler[2] = -3.14159
#         bpy.ops.object.location_clear()
#         bpy.context.scene.render.filepath = pathbase + "back.png"
#         bpy.ops.render.render(write_still=True)
        
#         #左側
#         #cam.data.shift_x = 0.125
#         geo.rotation_euler[2] = -1.5708 / 2
#         bpy.ops.object.location_clear()
#         bpy.context.scene.render.filepath = pathbase + "left.png"
#         bpy.ops.render.render(write_still=True)
        
        
#         #右側
#         #cam.data.shift_x = -0.125
#         geo.rotation_euler[2] = 1.5708 / 2
#         bpy.ops.object.location_clear()
#         bpy.context.scene.render.filepath = pathbase + "right.png"
#         bpy.ops.render.render(write_still=True)
        
        
# #        #トップ
# #        cam.data.shift_x = 0
# #        cam.data.shift_y = -0.125
# #        #現在の高さZとジオメトリまでの距離Yたせば同じ距離感の頭までの距離になるぞ。
# ##        cam.location[0] = 0
# #        cam.location[1] = (cam.location[2] + (cam.location[1] * -1)) * -1
# #        cam.location[2] = 0
# #        geo.rotation_euler[0] = 1.5708
# #        geo.rotation_euler[1] = 0
# #        geo.rotation_euler[2] = 0
# #        bpy.ops.object.location_clear()
# #        bpy.context.scene.render.filepath = pathbase + "top.png"
# #        bpy.ops.render.render(write_still=True)
        
        
        
        
#         #開きなおし
#         bpy.ops.wm.revert_mainfile(use_scripts=True)
        
#         return {'FINISHED'}
# ########################################


# ########################################
# #VRExport
# ########################################
# class FUJIWARATOOLBOX_871849(bpy.types.Operator):#VRExport
#     """VRExport"""
#     bl_idname = "fujiwara_toolbox.command_871849"
#     bl_label = "VRExport"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         #basepath = bpy.data.filepath

#         ##現状保存
#         #bpy.ops.wm.save_mainfile()

#         #deselect()

#         ##いらないものの削除
#         #delete(match("ConstructionArea"))
#         #delete(match("Grid_"))
        
#         #deselect()

#         #for obj in bpy.data.objects:
#         #    obj.hide = False

#         ##非表示レイヤー削除
#         ##レイヤー表示を反転して全選択削除してもどす？
#         ##オブジェクトが表示レイヤーをもってれば除外する
#         ##layers = bpy.context.scene.layers
#         ##dellist = []
#         ##for obj in bpy.data.objects:
#         ##    delflag = True
#         ##    for n in range(0,20):
#         ##        if obj.layers[n] == True:
#         ##            if layers[n] == True:
#         ##                delflag = False
#         ##                break
#         ##    if delflag:
#         ##        dellist.append(obj)

#         ##for n in range(0,20):
#         ##    bpy.context.scene.layers[n] = True

#         ##delete(dellist)
#         #for n in range(0,20):
#         #    bpy.context.scene.layers[n] = not bpy.context.scene.layers[n]
#         #bpy.ops.object.select_all(action='SELECT')
#         #delete(get_selected_list())
#         #for n in range(0,20):
#         #    bpy.context.scene.layers[n] = not bpy.context.scene.layers[n]
        

#         ##mod適用
#         #deselect()
#         #for obj in bpy.data.objects:
#         #    if obj.type == "MESH":
#         #        obj.select = True
#         #apply_mods()
#         #deselect()

#         #bpy.ops.object.select_all(action='SELECT')
#         #reject_notmesh()
#         #bpy.ops.object.transform_apply(location=True, rotation=True,
#         #scale=True)


#         #deselect()
#         #for obj in bpy.data.objects:
#         #    #テキストも重くなるのでいらない
#         #    if obj.type == "FONT":
#         #        obj.select = True

#         #    #非表示オブジェクト削除
#         #    if obj.type == "MESH":
#         #        if obj.draw_type == "WIRE" or obj.draw_type == "BOUNDS":
#         #            obj.select = True
#         #    #if obj.hide == True:
#         #    # obj.hide = False
#         #    # obj.select = True



#         #delete(get_selected_list())

#         #シェルでコピーしたほうがいいんじゃね？
#         #bpy.ops.wm.save_mainfile(filepath=fujiwara_toolbox.conf.maintools_vrexportpath)

#         #####

#         #非レンダオブジェクトを選択から除外
#         selection = fjw.get_selected_list()
#         for obj in selection:
#             if obj.hide_render:
#                 obj.select = False

#         bpy.context.scene.render.use_simplify = True
#         bpy.context.scene.render.simplify_subdivision = 2
#         #objで出す方がマシだ
#         bpy.ops.export_scene.obj(filepath= fujiwara_toolbox.conf.maintools_vrexportdir + os.sep + "VRRoom.obj", use_selection=True)


#         #出力フォルダを開く
#         os.system("EXPLORER " + fujiwara_toolbox.conf.maintools_vrexportdir)
#         ##time.sleep(5)
#         #bpy.ops.wm.open_mainfile(filepath=basepath)

#         return {'FINISHED'}
# ########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("リンクユーティリティ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#フォルダを開く
########################################
#bpy.ops.fujiwara_toolbox.open_linkedfolder() #フォルダを開く
class FUJIWARATOOLBOX_OPEN_LINKEDFOLDER(bpy.types.Operator):
    """リンク先ファイルのあるフォルダを開く"""
    bl_idname = "fujiwara_toolbox.open_linkedfolder"
    bl_label = "フォルダを開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()

        if obj.type != "EMPTY":
            self.report({"INFO"},"リンクオブジェクトを選択してください。")

        linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
        self.report({"INFO"},linkedpath)
        os.system("EXPLORER " + os.path.dirname(linkedpath)+os.sep)
        return {'FINISHED'}
########################################

########################################
#ファイルを開く
########################################
#bpy.ops.fujiwara_toolbox.open_linkedfile() #ファイルを開く
class FUJIWARATOOLBOX_OPEN_LINKEDFILE(bpy.types.Operator):
    """リンク先ファイルを開く"""
    bl_idname = "fujiwara_toolbox.open_linkedfile"
    bl_label = "ファイルを開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()

        if obj.type != "EMPTY":
            self.report({"INFO"},"リンクオブジェクトを選択してください。")

        linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
        self.report({"INFO"},linkedpath)
        os.system("EXPLORER " + linkedpath)
        return {'FINISHED'}
########################################

########################################
#グループを追加リンクする
########################################
#bpy.ops.fujiwara_toolbox.link_additional_group() #グループを追加リンクする
class FUJIWARATOOLBOX_LINK_ADDITIONAL_GROUP(bpy.types.Operator):
    """グループを追加リンクする"""
    bl_idname = "fujiwara_toolbox.link_additional_group"
    bl_label = "グループを追加リンクする"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    #http://qiita.com/nutti/items/9ec0a61d182350e44319
    groups = []
    linkedpath = ""
    def get_object_list_callback(scene, context):
        global link_additional_group_groups
        items = []
        # itemsに項目を追加する処理...
        for g in link_additional_group_groups:
            items.append((g,g,""))
        #items.append(("aswea","aswea",""))
        return items    

    group_list = EnumProperty(
        name = "Group List",               # 名称
        description = "Group List",        # 説明文
        items = get_object_list_callback)   # 項目リストを作成する関数



    def execute(self, context):
        #print(self.group_list)
        base = fjw.active()

        group = self.group_list
        _groupname = group
        _filepath = self.linkedpath + os.sep + "Group" + os.sep

        bpy.ops.wm.link(filepath=_filepath, filename=_groupname, directory=_filepath)
        linked = fjw.active()

        linked.location = base.location
        linked.rotation_euler = base.rotation_euler
        linked.rotation_quaternion = base.rotation_quaternion
        linked.scale = base.scale
        fjw.activate(base)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


        return {"FINISHED"}

    def invoke(self, context, event):
        global link_additional_group_groups
        link_additional_group_groups = []
        self.groups = []
        self.linkedpath = ""
        obj = fjw.active()
        if obj.type == "EMPTY":
            self.linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)


            with bpy.data.libraries.load(self.linkedpath, link=False, relative=True) as (data_from, data_to):
                for groupname in data_from.groups:
                    self.groups.append(groupname)
        link_additional_group_groups = self.groups
        return context.window_manager.invoke_props_dialog(self)
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ファイル差し替え
########################################
#bpy.ops.fujiwara_toolbox.replace_link_file() #ファイル差し替え
class FUJIWARATOOLBOX_REPLACE_LINK_FILE(bpy.types.Operator):
    """リンク先のファイルを差し替える。保存して開き直すまで反映されないので注意。"""
    bl_idname = "fujiwara_toolbox.replace_link_file"
    bl_label = "ファイル差し替え"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    @classmethod
    def poll(cls, context):
        obj = fjw.active()
        if obj is None:
            return {'CANCELLED'}
        if obj.type != "EMPTY":
            return {'CANCELLED'}
        if obj.dupli_group.library.filepath == "":
            return {'CANCELLED'}
        return True

    def invoke(self, context, event):
        if bpy.context.user_preferences.filepaths.save_version == 0:
            self.report({"WARNING"},"バージョン保存を有効にしてください：ユーザー設定 -> ファイル -> バージョンを保存")
            return {'CANCELLED'}
        bpy.ops.wm.save_mainfile()

        self.obj = fjw.active()
        self.directory = self.obj.dupli_group.library.filepath
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        basepath = self.obj.dupli_group.library.filepath
        self.obj.dupli_group.library.filepath = self.directory + self.files[0].name
        bpy.ops.file.make_paths_relative()
        self.report({"INFO"},"差し替えました。ファイルを保存して開き直してください。：" + basepath + " -> " + self.obj.dupli_group.library.filepath)
        return {'FINISHED'}
########################################


link_additional_group_groups = []
########################################
#グループ差し替え
########################################
#bpy.ops.fujiwara_toolbox.replace_link_group() #グループ差し替え
class FUJIWARATOOLBOX_REPLACE_LINK_GROUP(bpy.types.Operator):
    """リンク先のグループを差し替える。保存して開き直すまで反映されないので注意。"""
    bl_idname = "fujiwara_toolbox.replace_link_group"
    bl_label = "グループ差し替え"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    groups = []

    def get_object_list_callback(self, context):
        global link_additional_group_groups
        items = []
        # itemsに項目を追加する処理...
        for g in link_additional_group_groups:
            items.append((g,g,""))
        return items

    group_list = EnumProperty(
        name = "Group List",               # 名称
        description = "Group List",        # 説明文
        items = get_object_list_callback)   # 項目リストを作成する関数

    def invoke(self, context, event):
        if bpy.context.user_preferences.filepaths.save_version == 0:
            self.report({"WARNING"},"バージョン保存を有効にしてください：ユーザー設定 -> ファイル -> バージョンを保存")
            return {'CANCELLED'}
        bpy.ops.wm.save_mainfile()

        global link_additional_group_groups
        link_additional_group_groups = []
        linkedpath = ""
        obj = fjw.active()
        if obj.type != "EMPTY":
            return {'CANCELLED'}

        linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)

        with bpy.data.libraries.load(linkedpath, link=False, relative=True) as (data_from, data_to):
            for groupname in data_from.groups:
                link_additional_group_groups.append(groupname)

        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):
        obj = fjw.active()
        basename = obj.dupli_group.name
        groupname = self.group_list
        obj.dupli_group.name = groupname
        self.report({"INFO"},"差し替えました。ファイルを保存して開き直してください。：" + basename+ " -> " + groupname)
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("freezed.blend")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

class GetFreezedBlend():
    @classmethod
    def apply_mods(cls):
        apply_mod_list = ["SOLIDIFY", "BEVEL", "BOOLEAN"]
        ignore_name_list = ["裏ポリエッジ"]
        #modの適用
        for obj in bpy.context.visible_objects:
            modu = fjw.Modutils(obj)
            for mod in modu.mods:
                if mod.type in apply_mod_list:
                    if mod.name in ignore_name_list:
                        continue
                    modu.apply(mod)
    
    @classmethod
    def scale_images_half(cls):
        for img in bpy.data.images:
            w = img.size[0]
            h = img.size[1]
            try:
                img.scale(w/2,h/2)
                img.pack(as_png=True)
            except:
                pass

        # scale_name = "%d%%"%(tex_scale*100)
    
    @classmethod
    def saveas(cls, filepath, scale_str):
        blenddir = os.path.dirname(filepath)
        blendname = os.path.basename(filepath)
        name,ext = os.path.splitext(blendname)

        savepath = blenddir + os.sep + name + "_freezed_tex" + scale_str + ".blend"
        bpy.ops.wm.save_as_mainfile(filepath=savepath)

    

########################################
#_freezed.blend生成
########################################
#bpy.ops.fujiwara_toolbox.gen_freezed_blend() #_freezed.blend生成
class FUJIWARATOOLBOX_GEN_FREEZED_BLEND(bpy.types.Operator):
    """最低限のmodなどを適用した_freezed.blendファイルを生成する。テクスチャ解像度を変えたサブパターンが生成される。"""
    bl_idname = "fujiwara_toolbox.gen_freezed_blend"
    bl_label = "フリーズドモデル生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        basepath = bpy.data.filepath
        bpy.ops.wm.save_mainfile()
        
        GetFreezedBlend.apply_mods()
        bpy.ops.file.pack_all()
        GetFreezedBlend.saveas(basepath,"100")
        GetFreezedBlend.scale_images_half()
        GetFreezedBlend.saveas(basepath,"50")
        GetFreezedBlend.scale_images_half()
        GetFreezedBlend.saveas(basepath,"25")
        GetFreezedBlend.scale_images_half()
        GetFreezedBlend.saveas(basepath,"13")
        GetFreezedBlend.scale_images_half()

        bpy.ops.wm.open_mainfile(filepath=basepath)

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("tmp.fbx")
############################################################################################################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#インポート
########################################
class FUJIWARATOOLBOX_174609(bpy.types.Operator):#fbxインポート
    """fbxインポート"""
    bl_idname = "fujiwara_toolbox.command_174609"
    bl_label = "fbxインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.import_scene.fbx(filepath="tmp.fbx",automatic_bone_orientation=True)
        return {'FINISHED'}
########################################
########################################
#fbxエクスポート（選択メッシュ）
########################################
class FUJIWARATOOLBOX_87061(bpy.types.Operator):#fbxエクスポート（選択メッシュ）
    """fbxエクスポート（選択メッシュ）"""
    bl_idname = "fujiwara_toolbox.command_87061"
    bl_label = "fbxエクスポート（選択メッシュ）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                obj.select = False
        bpy.ops.export_scene.fbx(filepath="tmp.fbx",check_existing=False,use_selection=True)
        bpy.ops.object.delete()
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#3dcoatエクスポート
########################################
class FUJIWARATOOLBOX_822477(bpy.types.Operator):#3dcoatエクスポート
    """3dcoatエクスポート"""
    bl_idname = "fujiwara_toolbox.command_822477"
    bl_label = "3dcoatエクスポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #objじゃないとダメ
        #from blender
        #帰ってくるとき、原点がグローバル0になってしまうので、複製系は適用してしまう。
        bpy.context.scene.objects.active.select = True
        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if (mod.type == "MIRROR") or (mod.type == "ARRAY"):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        
        #名前、.001とかが事故るのでリネームする
        for obj in selected:
            obj.name = obj.name.replace(".","")
        
        #まずはトランスフォームを適用する
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        #100倍で出して0.01倍で取り込む。
        bpy.ops.export_scene.obj(filepath="tmp3dcoat.obj",check_existing=False,axis_forward='-Z', axis_up='Y',use_selection=True, global_scale=100.0, use_mesh_modifiers=False)
        
        #オリジナルを識別できるようにリネーム
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                obj.name = obj.name + "_3dcoatexported"
        
        
        
        return {'FINISHED'}
########################################


########################################
#3dcoatインポート
########################################
class FUJIWARATOOLBOX_189112(bpy.types.Operator):#3dcoatインポート
    """3dcoatインポート"""
    bl_idname = "fujiwara_toolbox.command_189112"
    bl_label = "3dcoatインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #3dcoat
        bpy.ops.import_scene.obj(filepath="tmp3dcoat.obj", axis_forward='-Z', axis_up='Y')
        #名前変える
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                #blenderに追加されたMESH名を除去する
                obj.name = obj.name.split("_")[0]
                obj.name = obj.name + "_3dcoatimported"
        
        #スケール調整
        for obj in bpy.context.selected_objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               obj.scale = (0.01,0.01,0.01)
               bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        #exportedのメッシュをimportedの内容にする
        for target in bpy.data.objects:
            if target.type == "MESH":
                if "_3dcoatexported" in target.name:
                    for source in bpy.context.selected_objects:
                        if source.name.replace("_3dcoatimported","") == target.name.replace("_3dcoatexported",""):
                            target.data = source.data.copy()
                            #ついでに原点を重心に
                            #bpy.context.scene.objects.active = target
                            #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS',
                            #center='MEDIAN')
                            #importedの削除
                            #bpy.context.scene.objects.active = source
                            #bpy.ops.object.delete(use_global=False)
        
        for target in bpy.data.objects:
            if target.type == "MESH":
                if "_3dcoatexported" in target.name:
                    #exportedの名前を消す
                    target.name = target.name.replace("_3dcoatexported","")
                    #ついでに原点を重心に
                    #bpy.context.scene.objects.active = target
                    #bpy.ops.object.transform_apply(location=True,
                    #rotation=True, scale=True)
                    #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS',
                    #center='MEDIAN')
        
        #importedを消す
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if "_3dcoatimported" in obj.name:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.delete(use_global=False)
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#posi.objエクスポート
########################################
class FUJIWARATOOLBOX_505642(bpy.types.Operator):#posi.objエクスポート
    """posi.objエクスポート"""
    bl_idname = "fujiwara_toolbox.command_505642"
    bl_label = "posi.objエクスポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.export_scene.obj(filepath="posi.obj",check_existing=False,use_selection=True)
        
        return {'FINISHED'}
########################################


########################################
#nega.objエクスポート
########################################
class FUJIWARATOOLBOX_896828(bpy.types.Operator):#nega.objエクスポート
    """nega.objエクスポート"""
    bl_idname = "fujiwara_toolbox.command_896828"
    bl_label = "nega.objエクスポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.export_scene.obj(filepath="nega.obj",check_existing=False,use_selection=True)
        
        return {'FINISHED'}
########################################


########################################
#posi.objインポート
########################################
class FUJIWARATOOLBOX_229893(bpy.types.Operator):#posi.objインポート
    """posi.objインポート"""
    bl_idname = "fujiwara_toolbox.command_229893"
    bl_label = "posi.objインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.import_scene.obj(filepath="posi.obj")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
############################################################################################################################
uiitem("便利")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#別のファイルからUIをロード
########################################
#bpy.ops.fujiwara_toolbox.load_ui_from_otherblendfile() #別のファイルからUIをロード
class FUJIWARATOOLBOX_LOAD_UI_FROM_OTHERBLENDFILE(bpy.types.Operator):
    """他のblendファイルからUIをロードする"""
    bl_idname = "fujiwara_toolbox.load_ui_from_otherblendfile"
    bl_label = "別のファイルからUIをロード"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filter_glob = StringProperty(default="*.blend", options={"HIDDEN"})
    
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        current_path = bpy.data.filepath
        current_load_ui = bpy.context.user_preferences.filepaths.use_load_ui
        if current_path == "":
            self.report({"WARN"}, str("ファイルが保存されていません！"))
            return {"CANCELLED"}

        if bpy.data.is_dirty:
            bpy.ops.wm.save_mainfile()

        bpy.context.user_preferences.filepaths.use_load_ui = True
        bpy.ops.wm.open_mainfile(filepath=self.filepath)
        bpy.context.user_preferences.filepaths.use_load_ui = False
        bpy.ops.wm.open_mainfile(filepath=current_path)
        bpy.context.user_preferences.filepaths.use_load_ui = current_load_ui

        return {'FINISHED'}
   
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
############################################################################################################################
uiitem(" ")
############################################################################################################################

########################################
#Blenderを再起動
########################################
#bpy.ops.fujiwara_toolbox.command_630782() #Blenderを再起動
class FUJIWARATOOLBOX_COMMAND_630782(bpy.types.Operator):
    """Blenderを再起動"""
    bl_idname = "fujiwara_toolbox.command_630782"
    bl_label = "Blenderを再起動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="BLENDER",mode="")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bpy.data.filepath == "":
            subprocess.Popen("blender")
        else:
            subprocess.Popen('blender "%s"'%bpy.data.filepath)
        bpy.ops.wm.quit_blender()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




################################################################################
#UIカテゴリ
########################################
#簡略化
########################################
class CATEGORYBUTTON_520749(bpy.types.Operator):#簡略化
    """簡略化"""
    bl_idname = "fujiwara_toolbox.categorybutton_520749"
    bl_label = "簡略化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("簡略化",True)
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")
    uiitem.direction = "vertical"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#オフ
########################################
class FUJIWARATOOLBOX_759926(bpy.types.Operator):#オフ
    """オフ"""
    bl_idname = "fujiwara_toolbox.command_759926"
    bl_label = "オフ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_TORUS",mode="")

    def execute(self, context):
        bpy.context.scene.render.use_simplify = False
        
        return {'FINISHED'}
########################################


########################################
#Subdiv 2
########################################
class FUJIWARATOOLBOX_700665(bpy.types.Operator):#Subdiv 2
    """Subdiv 2"""
    bl_idname = "fujiwara_toolbox.command_700665"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")

    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 2
        
        
        return {'FINISHED'}
########################################


########################################
#Subdiv 1
########################################
class FUJIWARATOOLBOX_194057(bpy.types.Operator):#Subdiv 1
    """Subdiv 1"""
    bl_idname = "fujiwara_toolbox.command_194057"
    bl_label = "1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")

    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 1
        
        return {'FINISHED'}
########################################



########################################
#Subdiv 0
########################################
class FUJIWARATOOLBOX_286488(bpy.types.Operator):#Subdiv 0
    """Subdiv 0"""
    bl_idname = "fujiwara_toolbox.command_286488"
    bl_label = "0"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_ICOSPHERE",mode="")

    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0
        
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#レンダ解像度化
########################################
class FUJIWARATOOLBOX_69698(bpy.types.Operator):#レンダ解像度化
    """レンダ解像度化"""
    bl_idname = "fujiwara_toolbox.command_69698"
    bl_label = "レンダ解像度化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj. modifiers:
                    if mod.type == "SUBSURF":
                        if mod.levels > mod.render_levels:
                            mod.render_levels = mod.levels
                        else:
                            mod.levels = mod.render_levels
        
        
        
        
        return {'FINISHED'}
########################################


















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#選択・操作
########################################
class CATEGORYBUTTON_200803(bpy.types.Operator):#選択・操作
    """選択・操作"""
    bl_idname = "fujiwara_toolbox.categorybutton_200803"
    bl_label = "選択・操作"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("選択・操作",True)
    uiitem.button(bl_idname,bl_label,icon="MOD_ARRAY",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#親子
########################################
class FUJIWARATOOLBOX_24259(bpy.types.Operator):#親子
    """親子"""
    bl_idname = "fujiwara_toolbox.command_24259"
    bl_label = "親子"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_ARRAY",mode="")

    def execute(self, context):
        objects = fjw.get_selected_list()
        targets = []
        for obj in objects:
            fjw.activate(obj)
            fjw.mode("OBJECT")
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            targets.extend(fjw.get_selected_list())

        targets.extend(objects)

        for obj in targets:
            obj.select = True

        #for obj in bpy.data.objects:
        #    obj.select = False
        #obj = bpy.context.scene.objects.active
        #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #obj.select = True
        return {'FINISHED'}
########################################

########################################
#親子→ローカルビュー
########################################
class FUJIWARATOOLBOX_96321(bpy.types.Operator):#親子→ローカルビュー
    """親子→ローカルビュー"""
    bl_idname = "fujiwara_toolbox.command_96321"
    bl_label = "親子→ローカルビュー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_ARRAY",mode="")

    def execute(self, context):
        #for obj in bpy.data.objects:
        #    obj.select = False
        #obj = bpy.context.scene.objects.active
        #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #obj.select = True
        bpy.ops.fujiwara_toolbox.command_24259()

        bpy.ops.view3d.localview()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#親子コピー
########################################
class FUJIWARATOOLBOX_55567(bpy.types.Operator):#親子コピー
    """親子コピー"""
    bl_idname = "fujiwara_toolbox.command_55567"
    bl_label = "親子コピー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="COPYDOWN",mode="")

    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_24259()
        bpy.ops.view3d.copybuffer()
        
        return {'FINISHED'}
########################################

########################################
#＆ペースト
########################################
class FUJIWARATOOLBOX_971178(bpy.types.Operator):#＆ペースト
    """＆ペースト"""
    bl_idname = "fujiwara_toolbox.command_971178"
    bl_label = "＆ペースト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_55567()
        bpy.ops.view3d.pastebuffer()


        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------





########################################
#親子削除
########################################
class FUJIWARATOOLBOX_975985(bpy.types.Operator):#親子削除
    """親子削除"""
    bl_idname = "fujiwara_toolbox.command_975985"
    bl_label = "親子削除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PANEL_CLOSE",mode="")

    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_24259()
        bpy.ops.object.delete(use_global=False)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#グループ
########################################
class FUJIWARATOOLBOX_764181(bpy.types.Operator):#グループ
    """グループ"""
    bl_idname = "fujiwara_toolbox.command_764181"
    bl_label = "グループ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="ROTATECOLLECTION",mode="")

    def execute(self, context):
        bpy.ops.object.select_grouped(type='GROUP')
        
        return {'FINISHED'}
########################################

########################################
#マテリアル未割り当て
########################################
class FUJIWARATOOLBOX_490584(bpy.types.Operator):#マテリアル未割り当て
    """マテリアル未割り当て"""
    bl_idname = "fujiwara_toolbox.command_490584"
    bl_label = "マテリアル未割り当て"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SOLID",mode="")

    def execute(self, context):
        for obj in bpy.data.objects:
            obj.select = False
        
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if obj.active_material == None:
                    obj.select = True
        
        
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------




########################################
#選択物のレイヤーだけ表示してコピー
########################################
class FUJIWARATOOLBOX_129690(bpy.types.Operator):#選択物のレイヤーだけ表示してコピー
    """選択物のレイヤーだけ表示してコピー"""
    bl_idname = "fujiwara_toolbox.command_129690"
    bl_label = "選択物のレイヤーだけ表示してコピー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #一旦全部非表示
        for n in range(0,20):
            bpy.context.scene.layers[n] = False
        
        #選択オブジェクトの表示を反映
        for obj in bpy.data.objects:
            if obj.select:
                for n in range(0,20):
                    if obj.layers[n]:
                        bpy.context.scene.layers[n] = True
        
        #選択解除
        for obj in bpy.data.objects:
            obj.select = False
        
        #全選択
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.view3d.copybuffer()
        
        return {'FINISHED'}
########################################




########################################
#なにかあるレイヤーだけを全表示
########################################
class FUJIWARATOOLBOX_124884(bpy.types.Operator):#なにかあるレイヤーだけを全表示
    """なにかあるレイヤーだけを全表示"""
    bl_idname = "fujiwara_toolbox.command_124884"
    bl_label = "なにかあるレイヤーだけを全表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #一旦全部非表示
        for n in range(0,20):
            bpy.context.scene.layers[n] = False
        
        #選択オブジェクトの表示を反映
        for obj in bpy.data.objects:
            for n in range(0,20):
                if obj.layers[n]:
                    bpy.context.scene.layers[n] = True
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#ペースト・表示
########################################
class FUJIWARATOOLBOX_47465(bpy.types.Operator):#ペースト・表示
    """ペースト・表示"""
    bl_idname = "fujiwara_toolbox.command_47465"
    bl_label = "ペースト・表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PASTEFLIPDOWN",mode="")

    def execute(self, context):
        bpy.ops.view3d.pastebuffer()
        for obj in bpy.data.objects:
            if obj.select:
                for n in range(0, 19):
                    if obj.layers[n] == True:
                        bpy.context.scene.layers[n] = True
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#カメラ範囲外を選択
########################################
class FUJIWARATOOLBOX_770418(bpy.types.Operator):#カメラ範囲外を選択
    """カメラ範囲外を選択"""
    bl_idname = "fujiwara_toolbox.command_770418"
    bl_label = "カメラ範囲外を選択"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        selection = fjw.get_selected_list()
        for obj in selection:
            if fjw.checkIfIsInCameraView(obj):
                obj.select = False

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#原点ツール
########################################
class CATEGORYBUTTON_421353(bpy.types.Operator):#原点ツール
    """原点ツール"""
    bl_idname = "fujiwara_toolbox.categorybutton_421353"
    bl_label = "原点ツール"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("原点ツール",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_EMPTY",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

############################################################################################################################
uiitem("原点移動")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#3Dカーソルに
########################################
#bpy.ops.fujiwara_toolbox.move_origin_cursor() #3Dカーソルに
class FUJIWARATOOLBOX_MOVE_ORIGIN_CURSOR(bpy.types.Operator):
    """原点を3Dカーソルに移動する。"""
    bl_idname = "fujiwara_toolbox.move_origin_cursor"
    bl_label = "3Dカーソルに"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}
########################################

########################################
#重心に
########################################
#bpy.ops.fujiwara_toolbox.move_origin_center_of_mass() #重心に
class FUJIWARATOOLBOX_MOVE_ORIGIN_CENTER_OF_MASS(bpy.types.Operator):
    """原点を重心に移動する。"""
    bl_idname = "fujiwara_toolbox.move_origin_center_of_mass"
    bl_label = "重心に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATAMODE",mode="")

    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#原点を下に（選択物）
########################################
class FUJIWARATOOLBOX_947695(bpy.types.Operator):#原点を下に（選択物）
    """原点を下に（選択物）"""
    bl_idname = "fujiwara_toolbox.command_947695"
    bl_label = "原点を下に（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="TRIA_DOWN_BAR",mode="")

    def execute(self, context):
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


########################################
#重心下に
########################################
class FUJIWARATOOLBOX_183554(bpy.types.Operator):#重心下に
    """重心下に"""
    bl_idname = "fujiwara_toolbox.command_183554"
    bl_label = "重心下に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="TRIA_DOWN_BAR",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        objlist = fjw.get_selected_list()
        fjw.deselect()
        
        for obj in objlist:
            bpy.context.scene.objects.active = obj
            obj.select = True
        
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
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
uiitem().vertical()
#---------------------------------------------



########################################
#原点X=0
########################################
class FUJIWARATOOLBOX_463922(bpy.types.Operator):#原点X=0
    """原点X=0"""
    bl_idname = "fujiwara_toolbox.command_463922"
    bl_label = "原点X=0"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_WIREFRAME",mode="")


    def execute(self, context):
        targets = fjw.get_selected_list()
        for obj in targets:
            fjw.deselect()
            fjw.activate(obj)
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.context.space_data.cursor_location[0] = 0
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        fjw.select(targets)
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#カーソルZを0に
########################################
class FUJIWARATOOLBOX_98727(bpy.types.Operator):#カーソルZを0に
    """カーソルZを0に"""
    bl_idname = "fujiwara_toolbox.command_98727"
    bl_label = "Zを0に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    def execute(self, context):
        bpy.context.space_data.cursor_location[2] = 0
        
        return {'FINISHED'}
########################################





########################################
#オブジェクトのZを0に
########################################
class FUJIWARATOOLBOX_109728(bpy.types.Operator):#オブジェクトのZを0に
    """オブジェクトのZを0に"""
    bl_idname = "fujiwara_toolbox.command_109728"
    bl_label = "Zを0に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATAMODE",mode="")
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.location[2] = 0
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#選択頂点を原点に
########################################
class FUJIWARATOOLBOX_753369(bpy.types.Operator):#選択頂点を原点に
    """選択頂点を原点に"""
    bl_idname = "fujiwara_toolbox.command_753369"
    bl_label = "選択頂点を原点に"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EDITMODE_HLT",mode="")

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

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

############################################################################################################################
uiitem("ピボット")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#カーソルに設置
########################################
class FUJIWARATOOLBOX_551555(bpy.types.Operator):#カーソルに設置
    """カーソルに設置"""
    bl_idname = "fujiwara_toolbox.command_551555"
    bl_label = "カーソルに設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CURSOR",mode="")

    def execute(self, context):
        loc = bpy.context.space_data.cursor_location
        if "原点ピボット" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            obj = bpy.context.scene.objects.active
            obj.name = "原点ピボット"
            obj.show_name = True
            obj.show_x_ray = True
            obj.empty_draw_type = 'ARROWS'
            obj.empty_draw_size = 0.5
        else:
            obj = bpy.data.objects["原点ピボット"]
            obj.hide = False
            obj.location = loc
        
        for tmp in bpy.context.selected_objects:
            tmp.select = False
        
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        return {'FINISHED'}
########################################

########################################
#オブジェクトに設置
########################################
class FUJIWARATOOLBOX_980669(bpy.types.Operator):#オブジェクトに設置
    """オブジェクトに設置"""
    bl_idname = "fujiwara_toolbox.command_980669"
    bl_label = "オブジェクトに設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATAMODE",mode="")

    def execute(self, context):
        loc = bpy.context.scene.objects.active.location
        bpy.context.space_data.cursor_location = loc
        if "原点ピボット" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            obj = bpy.context.scene.objects.active
            obj.name = "原点ピボット"
            obj.show_name = True
            obj.show_x_ray = True
            obj.empty_draw_type = 'ARROWS'
            obj.empty_draw_size = 0.5
        else:
            obj = bpy.data.objects["原点ピボット"]
            obj.hide = False
            obj.location = loc
        
        for tmp in bpy.context.selected_objects:
            tmp.select = False
        
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#オブジェクトをピボットに移動
########################################
class FUJIWARATOOLBOX_145460(bpy.types.Operator):#オブジェクトをピボットに移動
    """オブジェクトをピボットに移動"""
    bl_idname = "fujiwara_toolbox.command_145460"
    bl_label = "オブジェクトをピボットに移動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="NLA_PUSHDOWN",mode="")

    def execute(self, context):
        bpy.context.scene.objects.active.location = bpy.data.objects["原点ピボット"].location
        
        return {'FINISHED'}
########################################




########################################
#ピボットに原点を移動
########################################
class FUJIWARATOOLBOX_808575(bpy.types.Operator):#ピボットに原点を移動
    """ピボットに原点を移動"""
    bl_idname = "fujiwara_toolbox.command_808575"
    bl_label = "ピボットに原点を移動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EMPTY_DATA",mode="")

    def execute(self, context):
        bpy.context.space_data.cursor_location = bpy.data.objects["原点ピボット"].location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#スーパー視点
########################################
class CATEGORYBUTTON_413853(bpy.types.Operator):#スーパー視点
    """スーパー視点"""
    bl_idname = "fujiwara_toolbox.categorybutton_413853"
    bl_label = "スーパー視点"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("スーパー視点",True)
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_OFF",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################



def super_view(direction):
        base = fjw.active()

        target = base
        super = target
        #とりあえず最大50階層
        for n in range(0,50):
            if target.parent != None:
                target = target.parent
                super = target
            else:
                break

        fjw.activate(super)
        bpy.ops.view3d.viewnumpad(type=direction, align_active=True)
        fjw.activate(base)

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#
########################################
class FUJIWARATOOLBOX_202399a(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_202399a"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class FUJIWARATOOLBOX_202399b(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_202399b"
    bl_label = "上"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        super_view("TOP")
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class FUJIWARATOOLBOX_202399c(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_202399c"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        return {'FINISHED'}
########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#左
########################################
class FUJIWARATOOLBOX_248412d(bpy.types.Operator):#サイド
    """一番上の階層のオブジェクトに対してビューを設定"""
    bl_idname = "fujiwara_toolbox.command_248412d"
    bl_label = "左"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        super_view("LEFT")
        return {'FINISHED'}
########################################

########################################
#
########################################
class FUJIWARATOOLBOX_779140e(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_779140e"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class FUJIWARATOOLBOX_779140f(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_779140f"
    bl_label = "右"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        super_view("RIGHT")
        
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
class FUJIWARATOOLBOX_309675g(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_309675g"
    bl_label = "前"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        super_view("FRONT")
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class FUJIWARATOOLBOX_309675h(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_309675h"
    bl_label = "下"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        super_view("BOTTOM")
        
        return {'FINISHED'}
########################################

########################################
#
########################################
class FUJIWARATOOLBOX_309675i(bpy.types.Operator):#
    """"""
    bl_idname = "fujiwara_toolbox.command_309675i"
    bl_label = "後"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        super_view("BACK")
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#マテリアル
########################################
class CATEGORYBUTTON_798012(bpy.types.Operator):#マテリアル
    """マテリアル"""
    bl_idname = "fujiwara_toolbox.categorybutton_798012"
    bl_label = "マテリアル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("マテリアル",True)
    uiitem.button(bl_idname,bl_label,icon="SMOOTH",mode="")
    uiitem.direction = "vertical"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################


########################################
#モノクロ化
########################################
#bpy.ops.fujiwara_toolbox.make_materials_monochrome() #モノクロ化
class FUJIWARATOOLBOX_make_materials_monochrome(bpy.types.Operator):
    """選択オブジェクトのマテリアルをモノクロ化する"""
    bl_idname = "fujiwara_toolbox.make_materials_monochrome"
    bl_label = "モノクロ化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type == "MESH":
                for mat in obj.data.materials:
                    mat.diffuse_color.s = 0.0

        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#全て影なし
########################################
class FUJIWARATOOLBOX_134463(bpy.types.Operator):#全て影なし
    """全て影なし"""
    bl_idname = "fujiwara_toolbox.command_134463"
    bl_label = "全て影なし"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SOLID",mode="")

    def execute(self, context):
        for mat in bpy.data.materials:
            mat.use_shadeless = True
        for obj in bpy.data.objects:
            obj.show_wire = True
        bpy.context.space_data.show_floor = False
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        return {'FINISHED'}
########################################


########################################
#全て影あり
########################################
class FUJIWARATOOLBOX_594225(bpy.types.Operator):#全て影あり
    """全て影あり"""
    bl_idname = "fujiwara_toolbox.command_594225"
    bl_label = "全て影あり"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SMOOTH",mode="")

    def execute(self, context):
        for mat in bpy.data.materials:
            mat.use_shadeless = False
        for obj in bpy.data.objects:
            obj.show_wire = False
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#全てシングル化
########################################
class FUJIWARATOOLBOX_386533(bpy.types.Operator):#全てシングル化
    """全てシングル化"""
    bl_idname = "fujiwara_toolbox.command_386533"
    bl_label = "全てシングル化"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.make_single_user(type='ALL', object=False, obdata=False, material=True, texture=False, animation=False)
        
        return {'FINISHED'}
########################################


########################################
#透過無効化（選択物）
########################################
class FUJIWARATOOLBOX_867349(bpy.types.Operator):#透過無効化（選択物）
    """透過無効化（選択物）"""
    bl_idname = "fujiwara_toolbox.command_867349"
    bl_label = "透過無効化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for slot in obj.material_slots:
                mat = slot.material
                if "裏ポリエッジ" in mat.name:
                    continue
                mat.use_transparency = False
        
        
        return {'FINISHED'}
########################################
########################################
#有効化（選択物）
########################################
class FUJIWARATOOLBOX_748672(bpy.types.Operator):#有効化（選択物）
    """有効化（選択物）"""
    bl_idname = "fujiwara_toolbox.command_748672"
    bl_label = "有効化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for slot in obj.material_slots:
                mat = slot.material
                mat.use_transparency = True
                if "裏ポリエッジ" in mat.name:
                    mat.transparency_method = 'Z_TRANSPARENCY'
                else:
                    mat.transparency_method = 'RAYTRACE'

        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#Material Utils
########################################
class FUJIWARATOOLBOX_110074(bpy.types.Operator):#Material Utils
    """Materials Utilsの呼び出し"""
    bl_idname = "fujiwara_toolbox.command_110074"
    bl_label = "Materials Utils"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.wm.call_menu(name="VIEW3D_MT_master_material")
        return {'FINISHED'}
########################################

########################################
#無マテリアルに白を割り当て
########################################
class FUJIWARATOOLBOX_998634(bpy.types.Operator):#無マテリアルに白を割り当て
    """無マテリアルに白を割り当て"""
    bl_idname = "fujiwara_toolbox.command_998634"
    bl_label = "無マテリアルに白を割り当て"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
    #アサイン用マテリアルの作成
        #mat = bpy.data.materials.new(name="whitemat")
        #mat.diffuse_color=(1,1,1)
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                continue
            if len(obj.material_slots) == 0:
                matname = sbsname(obj.name)

                #既にあるマテリアルが外れてるだけだったらそれを返す
                if matname in bpy.data.materials:
                    mat = bpy.data.materials[matname]
                else:
                    #substance上で.が_に変換されて都合が悪いので除去しておく
                    mat = bpy.data.materials.new(name=matname)#substanceとの連携用にオブジェクト名でマテリアル作る
                    mat.diffuse_color = (1,1,1)
                #マテリアルスロットがゼロだった
                obj.data.materials.append(mat)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("ノード")
############################################################################################################################

########################################
#ベースセットアップ
########################################
class FUJIWARATOOLBOX_266402(bpy.types.Operator):#ベースセットアップ
    """ベースセットアップ"""
    bl_idname = "fujiwara_toolbox.command_266402"
    bl_label = "ベースセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        mat = fjw.active().active_material

        #既にノードがオンの場合データ消えるとマズいから警告だして終了する
        if mat.use_nodes:
            self.report({"WARNING"},"既にノードが設定されています")
            return {'CANCELLED'}

        mat.use_nodes = True
        mat.use_shadeless = True
        tree = mat.node_tree
        links = tree.links

        #ノードのクリア
        for node in tree.nodes:
            tree.nodes.remove(node)

        #マテリアルノード
        n_mat = tree.nodes.new("ShaderNodeMaterial")
        #自身のマテリアルを指定
        n_mat.material = mat
        n_mat.location = (0,200)

        #出力
        n_out = tree.nodes.new("ShaderNodeOutput")
        n_out.location = (500,200)


        #接続
        tree.links.new(n_mat.outputs["Color"], n_out.inputs["Color"])


        return {'FINISHED'}
########################################

#########################################
##モノクロ化
#########################################
#class FUJIWARATOOLBOX_324645(bpy.types.Operator):#モノクロ化
#    """モノクロ化"""
#    bl_idname = "fujiwara_toolbox.command_324645"
#    bl_label = "モノクロ化"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


####    def execute(self, context):
#        objects = get_selected_list()
#        for obj in objects:
#            if obj.type != "MESH":
#                continue
#            if len(obj.data.materials) == 0:
#                mat = bpy.data.materials.new(name="モノクロマテリアル")
#                obj.data.materials.append(mat)
#            for mat in obj.data.materials:
#                #既にノードがオンの場合データ消えるとマズいから警告だして終了する
#                #if mat.use_nodes:
#                # continue
#                #→破棄でいいや
#                #裏ポリはスキップ！！
#                if "裏ポリエッジ" in mat.name:
#                    continue
                
#                mat.use_nodes = True
#                mat.use_shadeless = True
#                tree = mat.node_tree
#                links = tree.links

#                #ノードのクリア
#                for node in tree.nodes:
#                    tree.nodes.remove(node)



#                ng_mono = nodegroup_instance(tree, append_nodetree("二値・グレー化"))
#                ng_beta = nodegroup_instance(tree, append_nodetree("ベタ影二値"))




#                #マテリアルノード
#                n_mat = tree.nodes.new("ShaderNodeMaterial")
#                #自身のマテリアルを指定
#                n_mat.material = mat
#                n_mat.location = (0,200)

#                #出力
#                n_out = tree.nodes.new("ShaderNodeOutput")
#                n_out.location = (500,200)


#                #接続
#                #マテリアル→グレー
#                tree.links.new(n_mat.outputs["Color"], ng_mono.inputs["グレー化"])
#                #マテリアル→ベタ影
#                tree.links.new(n_mat.outputs["Color"],
#                ng_beta.inputs["Color"])
#                #ベタ影→二値
#                tree.links.new(ng_beta.outputs["Color"],
#                ng_mono.inputs["二値化"])
                
#                #二値→アウトプット
#                tree.links.new(ng_mono.outputs["Color"],
#                n_out.inputs["Color"])

#                #アルファ
#                tree.links.new(n_mat.outputs["Alpha"], n_out.inputs["Alpha"])
#                pass
        
#        return {'FINISHED'}
#########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


def set_comicshader_auto(specular=1,shadow_color=(0,0,0,1)):
    objects = fjw.get_selected_list()
    for obj in objects:
        if obj.type != "MESH":
            continue
        if len(obj.data.materials) == 0:
            mat = bpy.data.materials.new(name="モノクロマテリアル")
            obj.data.materials.append(mat)
        for mat in obj.data.materials:
            #既にノードがオンの場合データ消えるとマズいから警告だして終了する
            #if mat.use_nodes:
            #    continue
            #→破棄でいいや
            #裏ポリはスキップ！！
            if "裏ポリエッジ" in mat.name:
                continue
            
            mat.use_shadeless = True
            ntu = fjw.NodetreeUtils(mat)
            ntu.activate()
            ntu.cleartree()

            ng_comic = ntu.group_instance(fjw.append_nodetree("漫画シェーダ"))
            #ノード設定
            # bpy.data.node_groups["Shader Nodetree"].nodes["Group"].inputs[2].default_value = 0
            ng_comic.inputs["Specular"].default_value = specular
            ng_comic.inputs["ShadowColor"].default_value = shadow_color

            #マテリアルノード
            n_mat = ntu.add("ShaderNodeMaterial","Material")
            #自身のマテリアルを指定
            n_mat.material = mat

            #出力
            n_out = ntu.add("ShaderNodeOutput","Output")

            #接続
            ntu.link(n_mat.outputs["Color"], ng_comic.inputs["Color"])
            ntu.link(n_mat.outputs["Normal"], ng_comic.inputs["Normal"])

            ntu.link(ng_comic.outputs["Color"], n_out.inputs["Color"])

            ntu.link(n_mat.outputs["Alpha"], n_out.inputs["Alpha"])


            pass
    fjw.select(objects)


########################################
#漫画シェーダ
########################################
class FUJIWARATOOLBOX_117769(bpy.types.Operator):#漫画シェーダ
    """漫画シェーダ"""
    bl_idname = "fujiwara_toolbox.command_117769"
    bl_label = "漫画シェーダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        set_comicshader_auto()
        return {'FINISHED'}
########################################



########################################
#スペキュラなし
########################################
#bpy.ops.fujiwara_toolbox.comic_shader_nospec() #スペキュラなし
class FUJIWARATOOLBOX_comic_shader_nospec(bpy.types.Operator):
    """スペキュラなしの漫画シェーダ。"""
    bl_idname = "fujiwara_toolbox.comic_shader_nospec"
    bl_label = "スペキュラなし"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        set_comicshader_auto(specular=0)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Cycles")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#Cyclesマテリアル化
########################################
#bpy.ops.fujiwara_toolbox.cycles_to_cycles_material() #Cyclesマテリアル化
class FUJIWARATOOLBOX_CYCLES_TO_CYCLES_MATERIAL(bpy.types.Operator):
    """通常マテリアルをCyclesマテリアルに変換する。テクスチャはbaseColorの同一ディレクトリから検索する。"""
    bl_idname = "fujiwara_toolbox.cycles_to_cycles_material"
    bl_label = "Cyclesマテリアル化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self,context):
        selection = fjw.get_selected_list()
        for obj in selection:
            if not hasattr(obj.data, "materials"):
                continue
            ctm = fjw.CyclesTexturedMaterial(obj.data.materials)
            ctm.execute()

        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
# ############################################################################################################################
# uiitem("Cycles")
# ############################################################################################################################
# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------
# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------
# ########################################
# #テクスチャ用ベースマテリアル作成
# ########################################
# #bpy.ops.fujiwara_toolbox.create_cycles_texturedbasemat() #テクスチャ用ベースマテリアル作成
# class FUJIWARATOOLBOX_CREATE_CYCLES_TEXTUREDBASEMAT(bpy.types.Operator):
#     """Cycles用のテクスチャマテリアルを作成する。"""
#     bl_idname = "fujiwara_toolbox.create_cycles_texturedbasemat"
#     bl_label = "テクスチャ用ベースマテリアル作成"
#     bl_options = {'REGISTER', 'UNDO'}
#     # bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     matname = StringProperty(
#         name="マテリアル名",
#         description="マテリアル名",
#         default="Matname",
#     )

#     resolution = EnumProperty(
#         name="解像度",
#         description="解像度",
#         items=[
#             ("256", "256", "256"),
#             ("512", "512", "512"),
#             ("1024", "1024", "1024"),
#             ("2048", "2048", "2048"),
#             ("4096", "4096", "4096"),
#         ],
#         default="2048"
#     )

#     # resolution = IntProperty(
#     #     name="解像度",
#     #     description="解像度",
#     #     default=2048,
#     #     min=0,
#     #     max=4096
#     # )

#     def image(self, name):
#         img = bpy.data.images.new(name, int(self.resolution), int(self.resolution))
#         self_dir = os.path.dirname(bpy.data.filepath)
#         img_dir = self_dir + os.sep + "TEXTURES" + os.sep + self.matname
#         if not os.path.exists(img_dir):
#             os.makedirs(img_dir)
#         img.filepath = img_dir + os.sep + name + ".png"
#         img.save()
#         return img
    
#     def image_node(self, node_builder, name):
#         img = self.image(name)
#         node = node_builder.node("ShaderNodeTexImage", True)
#         node.image = img
#         return node

#     def execute(self, context):
#         # self.matname = "プロパティで入力させる"
#         matname = self.matname
#         mat = bpy.data.materials.new(matname)
#         # 実際に作成された名前にする
#         self.matname = mat.name
#         obj = fjw.active()
#         obj.data.materials.append(mat)

#         nb = fjw._NodeUtils.NodeBuilder(mat)
#         nb.clear()
#         nb.node("ShaderNodeOutputMaterial")
#         shader_node = nb.node("ShaderNodeBsdfPrincipled")
#         nb.link(shader_node.outputs["BSDF"],nb.node("ShaderNodeOutputMaterial").inputs["Surface"])
#         img_color_node = self.image_node(nb, self.matname+"_TEXTURE")
#         img_normals_node = self.image_node(nb, self.matname+"_NORMALS")
#         img_roughness_node = self.image_node(nb, self.matname+"_ROUGHNESS")
#         nb.link(img_color_node.outputs["Color"], shader_node.inputs["Base Color"])
#         nb.link(img_normals_node.outputs["Color"], shader_node.inputs["Normal"])
#         nb.link(img_roughness_node.outputs["Color"], shader_node.inputs["Roughness"])
#         nb.layout()
#         bpy.ops.file.make_paths_relative()

#         return {'FINISHED'}

#     def invoke(self, context, event):
#         self.matname = fjw.active().name
#         return context.window_manager.invoke_props_dialog(self)

# ########################################
# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------
# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------
# ########################################
# #アクティブマテリアルの場所にエクスポート
# ########################################
# #bpy.ops.fujiwara_toolbox.export_obj_to_activematerial() #アクティブマテリアルの場所にエクスポート
# class FUJIWARATOOLBOX_EXPORT_OBJ_TO_ACTIVEMATERIAL(bpy.types.Operator):
#     """アクティブマテリアルのテクスチャフォルダにobjをエクスポートして、フォルダを開く。"""
#     bl_idname = "fujiwara_toolbox.export_obj_to_activematerial"
#     bl_label = "アクティブマテリアルの場所にエクスポート"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         obj = fjw.active()
#         fjw.main.deselect()
#         fjw.main.select([obj])
#         mat = obj.active_material
#         image_dir = ""
#         for node in mat.node_tree.nodes:
#             if node.bl_idname == "ShaderNodeTexImage":
#                 image_path = node.image.filepath
#                 image_dir = os.path.dirname(image_path)
#                 break
#         obj_path = image_dir + os.sep + mat.name + ".obj"
#         bpy.ops.export_scene.obj(filepath=bpy.path.abspath(obj_path), use_selection=False, use_mesh_modifiers=True)
#         subprocess.Popen("EXPLORER " + bpy.path.abspath(image_dir))

#         return {'FINISHED'}
# ########################################

# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------


############################################################################################################################
uiitem("ワールド")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def set_hdri(path):
    img = bpy.data.images.load(filepath=path)
    if bpy.context.scene.render.engine == 'CYCLES':
        world = bpy.context.scene.world
        ntu = fjw.NodetreeUtils(world)
        ntu.activate()
        ntu.cleartree()
        n_out = ntu.add("ShaderNodeOutputWorld", "Output World")

        n_bg = ntu.add("ShaderNodeBackground", "Background")
        n_env = ntu.add("ShaderNodeTexEnvironment", "Texture Enviroment")
        ntu.link(n_env.outputs["Color"], n_bg.inputs["Color"])
        ntu.link(n_bg.outputs["Background"], n_out.inputs["Surface"])
        n_bg.inputs["Strength"].default_value = 0.5

        n_texcoord = ntu.add("ShaderNodeTexCoord", "Texture Coordinates")
        n_map = ntu.add("ShaderNodeMapping", "Mapping")
        n_map.vector_type = "POINT"
        ntu.link(n_texcoord.outputs["Generated"], n_map.inputs["Vector"])
        ntu.link(n_map.outputs["Vector"], n_env.inputs["Vector"])

        n_env.image = img

        bpy.context.scene.render.layers.active.use_sky = True
        world.cycles.sample_as_light = True
        world.cycles.sample_map_resolution = img.size[0]
        bpy.context.scene.cycles.film_transparent = False

    if bpy.context.scene.render.engine == 'BLENDER_RENDER':
        tex = bpy.data.textures.new(os.path.basename(path), "IMAGE")
        tex.image = img
        bpy.context.scene.world.active_texture = tex
        tslot = bpy.context.scene.world.texture_slots[0]
        tslot.texture_coords = 'EQUIRECT'
        tslot.use_map_blend = False
        tslot.use_map_horizon = True

        bpy.context.scene.world.use_sky_real = True
        #重たくなるので保留→GLレンダだったら関係なかった！
        bpy.context.scene.world.light_settings.use_environment_light = True
        bpy.context.scene.world.light_settings.environment_energy = 0
        bpy.context.scene.world.light_settings.environment_color = 'SKY_TEXTURE'
        bpy.context.scene.world.light_settings.gather_method = 'APPROXIMATE'

        bpy.context.space_data.show_world = True
        bpy.context.space_data.fx_settings.use_ssao = False

        bpy.context.scene.render.alpha_mode = 'SKY'
        bpy.context.scene.render.layers["RenderLayer"].use_sky = True




########################################
#HDRI設定
########################################
#bpy.ops.fujiwara_toolbox.cycles_set_hdri() #HDRI設定
class FUJIWARATOOLBOX_CYCLES_SET_HDRI(bpy.types.Operator):
    """ファイルを読み込んでHDRIを設定する。Internalでは環境照明オンにしてないので手動でオンにすること。"""
    bl_idname = "fujiwara_toolbox.cycles_set_hdri"
    bl_label = "HDRI設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        self.directory = os.path.dirname(bpy.data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.filename == "":
            return {"CANCELLED"}
        path = os.path.normpath(self.directory + os.sep + self.filename)

        set_hdri(path)

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#アセットフォルダから設定
########################################
#bpy.ops.fujiwara_toolbox.cycles_set_hdri_from_assetdir() #アセットフォルダから設定
class FUJIWARATOOLBOX_CYCLES_SET_HDRI_FROM_ASSETDIR(bpy.types.Operator):
    """アセットディレクトリ/hdriからファイルを読み込んでHDRIマテリアルを設定する。"""
    bl_idname = "fujiwara_toolbox.cycles_set_hdri_from_assetdir"
    bl_label = "アセットフォルダから設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        self.directory = assetdir + os.sep + "hdri"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.filename == "":
            return {"CANCELLED"}
        path = os.path.normpath(self.directory + os.sep + self.filename)
        #自texturesに移動
        if bpy.data.filepath != "":
            selfdir = os.path.dirname(bpy.data.filepath)
            newtexdir = selfdir + os.sep + "textures"
            newtexpath = newtexdir + os.sep + self.filename
            if not os.path.exists(newtexdir):
                os.mkdir(newtexdir)
            shutil.copy(path, newtexpath)
            path = newtexpath
            
        set_hdri(path)

        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




################################################################################
#UIカテゴリ
########################################
#Render
########################################
class CATEGORYBUTTON_959029(bpy.types.Operator):#Render
    """Render"""
    bl_idname = "fujiwara_toolbox.categorybutton_959029"
    bl_label = "Render"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("Render",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_CAMERA",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("シーン設定")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
# ########################################
# #filmic
# ########################################
# #bpy.ops.fujiwara_toolbox.set_filmic() #filmic
# class FUJIWARATOOLBOX_SET_FILMIC(bpy.types.Operator):
#     """filmicをシーンに設定する。"""
#     bl_idname = "fujiwara_toolbox.set_filmic"
#     bl_label = "filmic"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         bpy.context.scene.view_settings.view_transform = 'Filmic'
#         bpy.context.scene.view_settings.look = 'Filmic - Base Contrast'
#         return {'FINISHED'}
# ########################################
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#ざっくりCyclesセットアップ
########################################
#bpy.ops.fujiwara_toolbox.easy_cycles_setup() #ざっくりCyclesセットアップ
class FUJIWARATOOLBOX_EASY_CYCLES_SETUP(bpy.types.Operator):
    """ざっくりとCycles用の設定をセットアップする。"""
    bl_idname = "fujiwara_toolbox.easy_cycles_setup"
    bl_label = "ざっくりCyclesセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.view_settings.view_transform = 'Filmic'
        bpy.context.scene.view_settings.look = 'Filmic - Base Contrast'
        bpy.context.scene.cycles.use_square_samples = True
        bpy.context.scene.cycles.samples = 10
        bpy.context.scene.cycles.preview_samples = 2
        bpy.context.scene.cycles.transparent_max_bounces = 8
        bpy.context.scene.cycles.transparent_min_bounces = 8
        bpy.context.scene.cycles.use_transparent_shadows = True
        bpy.context.scene.cycles.max_bounces = 8
        bpy.context.scene.cycles.min_bounces = 8
        bpy.context.scene.cycles.diffuse_bounces = 0
        bpy.context.scene.cycles.glossy_bounces = 1
        bpy.context.scene.cycles.transmission_bounces = 2
        bpy.context.scene.cycles.volume_bounces = 0

        return {'FINISHED'}
########################################

########################################
#ざっくりInternalセットアップ
########################################
#bpy.ops.fujiwara_toolbox.command_778778() #ざっくりInternalセットアップ
class FUJIWARATOOLBOX_COMMAND_778778(bpy.types.Operator):
    """ざっくりInternalセットアップ"""
    bl_idname = "fujiwara_toolbox.command_778778"
    bl_label = "ざっくりInternalセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.context.scene.render.use_textures = True
        bpy.context.scene.render.use_shadows = True
        bpy.context.scene.render.use_raytrace = True
        #ビューポートに反映されない…
        # bpy.context.scene.view_settings.view_transform = 'Filmic'

        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#############################################################################################################################
#uiitem("レンダ設定")
#############################################################################################################################

#########################################
##カメラ外を非レンダ化
#########################################
#class FUJIWARATOOLBOX_881058(bpy.types.Operator):#カメラ外を非レンダ化
#    """カメラ外を非レンダ化*テスト"""
#    bl_idname = "fujiwara_toolbox.command_881058"
#    bl_label = "カメラ外を非レンダ化*テスト"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


####    def execute(self, context):
#        for obj in get_selected_list():
#            if not checkLocationisinCameraView(obj.matrix_world *
#            obj.matrix_basis.inverted() * obj.location):
#                if "hide_render_basestate" not in obj:
#                    obj["hide_render_basestate"] = obj.hide_render
#                obj.hide_render = True
#                obj.hide = True


#        return {'FINISHED'}
#########################################


############################################################################################################################
uiitem("Cyclesレンダ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#Cycles・線画レンダ
########################################
#bpy.ops.fujiwara_toolbox.render_cycles_and_edge() #Cycles・線画レンダ
class FUJIWARATOOLBOX_RENDER_CYCLES_AND_EDGE(bpy.types.Operator):
    """Cycles・線画をレンダする。"""
    bl_idname = "fujiwara_toolbox.render_cycles_and_edge"
    bl_label = "Cycles・線画レンダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        starttime = time.time()
        self.report({"INFO"}, "アニメーション完了　{0:.2f}秒".format(time.time() - starttime))

        render_bu = fjw.PropBackup(bpy.context.scene.render)
        render_bu.store("engine")
        render_bu.store("filepath")
        dirname, name, ext = fjw.splitpath(bpy.data.filepath)
        render_dir = dirname + os.sep + "render"
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.filepath = render_dir + os.sep + name + "_cycles.png"
        # そのままレンダ
        bpy.ops.render.render(write_still=True)

        # エッジレンダ
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.context.scene.render.filepath = render_dir + os.sep + name + "_edge.png"

        # objects = bpy.context.scene.objects
        objects = bpy.data.objects
        obj_bu_list = []
        for obj in objects:
            obj_bu = fjw.PropBackup(obj)
            obj_bu.store("hide_render")
            obj_bu_list.append(obj_bu)

        # render_state_list = []
        # for obj in objects:
        #     render_state_list.append((obj, obj.hide_render))

        # パーティクルヘアの非表示
        for obj in objects:
            if obj.type == "MESH":
                if len(obj.particle_systems) != 0:
                    obj.hide_render = True

        # レンダレイヤ設定
        render_layer = bpy.context.scene.render.layers.active
        render_layer_bu = fjw.PropBackup(render_layer)
        render_layer_bu.store("use_zmask")
        render_layer_bu.store("invert_zmask")
        render_layer_bu.store("use_all_z")
        render_layer_bu.store("use_solid")
        render_layer_bu.store("use_halo")
        render_layer_bu.store("use_ztransp")
        render_layer_bu.store("use_sky")
        render_layer_bu.store("use_strand")
        render_layer_bu.store("use_freestyle")
        render_layer_bu.store("use_edge_enhance")
        render_layer.use_zmask = False
        render_layer.invert_zmask = False
        render_layer.use_all_z = False
        render_layer.use_solid = False
        render_layer.use_halo = False
        render_layer.use_ztransp = False
        render_layer.use_sky = False
        render_layer.use_strand = False
        render_layer.use_freestyle = False
        render_layer.use_edge_enhance = True

        bpy.ops.render.render(write_still=True)

        # リストア
        render_bu.restore()
        render_layer_bu.restore()
        for obj_bu in obj_bu_list:
            obj_bu.restore()

        endtime = time.time()
        self.report({"INFO"}, "レンダ完了　{0:.2f}秒".format(endtime - starttime))

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("OpenGLレンダ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#GLレンダのバックグラウンド実行は無理。

def active_gpbrush():
    return bpy.context.scene.tool_settings.gpencil_brushes.active

def gpline_change(gplayer, value):
    #linewidth =
    #bpy.context.scene.tool_settings.gpencil_brushes.active.line_width
    f = bpy.context.scene.frame_current

    if len(gplayer.frames) == 0:
        return

    for frame in gplayer.frames:
        if frame.frame_number == f:
            for stroke in frame.strokes:
                if hasattr(stroke,"line_width"):
                    stroke.line_width = value

    #gplayer.line_change = value
    #bpy.ops.gpencil.stroke_apply_thickness()
    #→これは結局stroke.line_widthに値が反映されてる




def render_opengl(filename,show_viewport=False):
    #設定取得
    show_only_render = bpy.context.space_data.show_only_render
    viewport_shade = bpy.context.space_data.viewport_shade
    use_ssao = bpy.context.space_data.fx_settings.use_ssao
    view_perspective = bpy.context.space_data.region_3d.view_perspective
    filepath = bpy.context.scene.render.filepath

    bpy.context.space_data.show_only_render = True
    bpy.context.space_data.viewport_shade = 'MATERIAL'
    bpy.context.space_data.fx_settings.use_ssao = False

    #カメラビュー
    bpy.context.space_data.region_3d.view_perspective = "CAMERA"
    #参考：bpy.data.screens[0].areas[1].spaces[0].local_view

    dir = os.path.dirname(bpy.data.filepath)
    renderdir = fjw.blenddir() + os.sep + "render" + os.sep 
    renderpath = renderdir + filename + ".png"
    bpy.context.scene.render.filepath = renderpath

    if show_viewport:
        bpy.ops.render.opengl("INVOKE_DEFAULT",view_context=True,write_still=True)
    else:
        bpy.ops.render.opengl(view_context=True,write_still=True)

    #設定リストア
    bpy.context.space_data.show_only_render = show_only_render
    bpy.context.space_data.viewport_shade = viewport_shade
    bpy.context.space_data.fx_settings.use_ssao = use_ssao
    bpy.context.space_data.region_3d.view_perspective = view_perspective
    bpy.context.scene.render.filepath = filepath


########################################
#GLレンダ
########################################
class FUJIWARATOOLBOX_GLRENDER(bpy.types.Operator):#GLレンダ
    """OpenGLレンダ。透過レンダと透過オブジェクト非表示レンダを生成。ドロップシャドウ無効。"""
    bl_idname = "fujiwara_toolbox.glrender"
    bl_label = "GLレンダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.mode("OBJECT")
        starttime = time.time()

        viewstate = fjw.ViewState()

        #再計算回避
        if bpy.context.scene.render.use_simplify:
            bpy.context.scene.render.use_simplify = False

        #ビューロック解除
        bpy.context.space_data.lock_camera = False

        #下書き非表示
        bpy.context.space_data.show_background_images = False

        #グリペンレイヤ
        if bpy.context.scene.grease_pencil is not None:
            gplayers = bpy.context.scene.grease_pencil.layers
            if "下書き" in gplayers:
                bpy.context.scene.grease_pencil.layers["下書き"].hide = True
            #gpcurrent = bpy.context.scene.grease_pencil.layers.active
            ##線幅
            for gplayer in gplayers:
                if not gplayer.hide:
                    gpline_change(gplayer, 20)

        #半透明非表示
        for obj in bpy.data.objects:
            if hasattr(obj.data, "materials"):
                for mat in obj.data.materials:
                    if "裏ポリエッジ" in mat.name:
                        continue
                    if mat.use_transparency:
                        obj.hide = True
                        break
        selfname = fjw.blendname()
        render_opengl(selfname + "_layerAll_OpenGL_B_NonTranpsarent")
        viewstate.restore_viewstate()
        del viewstate

        # render_opengl(selfname,True)
        render_opengl(selfname + "_layerAll_OpenGL_A_Main")

        endtime = time.time()
        self.report({"INFO"},"レンダ完了　{0:.2f}秒".format(endtime - starttime))


        return {'FINISHED'}
########################################







########################################
#GLレンダMASK
########################################
class FUJIWARATOOLBOX_171760(bpy.types.Operator):#GLレンダMASK
    """GLレンダMASK用"""
    bl_idname = "fujiwara_toolbox.command_171760"
    bl_label = "GLレンダMASK"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.mode("OBJECT")
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.viewport_shade = 'MATERIAL'

        #カメラビュー
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"

        #グリペンレイヤオフ
        gplayers = bpy.context.scene.grease_pencil.layers
        for gpl in gplayers:
            gpl.hide = True
        #if "下書き" in gplayers:
        #    bpy.context.scene.grease_pencil.layers["下書き"].hide = True

        #背景非表示
        for i in range(10,15):
            bpy.context.scene.layers[i] = False


        ##線幅
        for gplayer in gplayers:
            if not gplayer.hide:
                gpline_change(gplayer, 20)

        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        renderdir = dir + os.sep + "render" + os.sep 
        renderpath = renderdir + selfname + "_layerAll_OpenGLforMASK.png"
        bpy.context.scene.render.filepath = renderpath

        bpy.ops.render.opengl("INVOKE_DEFAULT",view_context=True,write_still=True)
        
        return {'FINISHED'}
########################################








########################################
#線幅を戻す
########################################
class FUJIWARATOOLBOX_347064(bpy.types.Operator):#線幅を戻す
    """線幅を戻す"""
    bl_idname = "fujiwara_toolbox.command_347064"
    bl_label = "線幅を戻す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        #線幅戻す
        gplayers = bpy.context.scene.grease_pencil.layers
        for gplayer in gplayers:
            if not gplayer.hide:
                gpline_change(gplayer, active_gpbrush().line_width)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("OpenGL　コンポジット素材レンダ")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def glcompomat_rendermain(identifier, baselayers=None, edge=True, color=True, mask=True, shadow=True):
        #現状取得
        viewstate = fjw.ViewState()
        show_world = bpy.context.space_data.show_world
        alpha_mode = bpy.context.scene.render.alpha_mode
        file_format = bpy.context.scene.render.image_settings.file_format
        lock_camera = bpy.context.space_data.lock_camera
        show_background_images = bpy.context.space_data.show_background_images
        use_simplify = bpy.context.scene.render.use_simplify
        filepath = bpy.context.scene.render.filepath
        use_sky_paper = bpy.context.scene.world.use_sky_paper
        horizon_color = bpy.context.scene.world.horizon_color


        ###############################
        bpy.context.scene.render.image_settings.file_format = 'PNG'

        #背景色
        bpy.context.space_data.show_world = False
        bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

        # 線画いらんかも
        # #線画パス設定
        # selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        # blenddir = os.path.dirname(bpy.data.filepath)
        # renderdir = blenddir + os.sep + "render" + os.sep 
        # renderedgepath = renderdir + selfname + "_%s_edge.png"%identifier
        # bpy.context.scene.render.filepath = renderedgepath

        # #バージョンバックアップ対策
        # save_version = bpy.context.user_preferences.filepaths.save_version
        # bpy.context.user_preferences.filepaths.save_version = 0
        # #セーブ
        # bpy.ops.wm.save_mainfile()
        # bpy.context.user_preferences.filepaths.save_version = save_version

        # #一番はじめにバックグラウンドの線画レンダ投げとく
        # if edge:
        #     exec_externalutils("renderedge.py")

        #再計算回避
        if bpy.context.scene.render.use_simplify:
            bpy.context.scene.render.use_simplify = False

        #Subsurfをあわせる
        for obj in bpy.data.objects:
            modu = fjw.Modutils(obj)
            sbslist = modu.find_bytype_list("SUBSURF")
            for sbs in sbslist:
                if sbs.levels < sbs.render_levels:
                    sbs.levels = sbs.render_levels

        #ビューロック解除
        bpy.context.space_data.lock_camera = False

        #下書き非表示
        bpy.context.space_data.show_background_images = False

        #グリペンレイヤ
        if bpy.context.scene.grease_pencil is not None:
            gplayers = bpy.context.scene.grease_pencil.layers
            if "下書き" in gplayers:
                bpy.context.scene.grease_pencil.layers["下書き"].hide = True
            #gpcurrent = bpy.context.scene.grease_pencil.layers.active
            ##線幅
            for gplayer in gplayers:
                if not gplayer.hide:
                    gpline_change(gplayer, 20)

        selfname = fjw.blendname()

        materials = bpy.data.materials
        material_states = fjw.MaterialStates(materials)

        #カラーパス
        if color:
            for mat in materials:
                mat.use_shadeless = True
            render_opengl(selfname + "_%s_OpenGL_Color"%identifier)

            #透過用下地
            transp_flag = False
            for obj in bpy.context.scene.objects:
                for i in range(20):
                    if bpy.context.scene.layers[i] and obj.layers:
                        try:
                            for mat in obj.data.materials:
                                if mat.use_transparency:
                                    transp_flag = True
                                    obj.hide = True
                                    break
                        except:
                            pass
            if transp_flag:
                render_opengl(selfname + "_%s_OpenGL_Transpback"%identifier)
                viewstate.restore_viewstate()

        #マスク
        if mask:
            for mat in bpy.data.materials:
                mat.use_transparency = False
            if baselayers:
                #マスク処理
                mask_except_true_layers(bpy.context.scene.layers)
                bpy.context.scene.layers = baselayers
            bpy.context.scene.world.use_sky_paper = True
            bpy.context.scene.world.horizon_color = (1, 1, 1)
            bpy.context.scene.render.alpha_mode = 'SKY'
            render_opengl(selfname + "_%s_OpenGL_Mask"%identifier)
            bpy.context.space_data.show_world = False
            bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

        #シャドウパス
        # layersstate = fjw.layers_current_state()
        # bpy.context.scene.layers = [True for i in range(20)]
        material_states.restore()
        if shadow:
            for mat in materials:
                mat.diffuse_color = (1, 1, 1)
                for i in range(len(mat.texture_slots)):
                    tslot = mat.texture_slots[i]
                    if not tslot:
                        continue
                    if tslot.use_map_color_diffuse:
                        mat.use_textures[i] = False
            if baselayers:
                bpy.context.scene.layers = baselayers
            render_opengl(selfname + "_%s_OpenGL_Shadow"%identifier)
            # bpy.context.scene.layers = layersstate


        #背景があった場合、背景だけをレンダリングする
        if show_world:
            bpy.context.space_data.show_world = True
            bpy.context.scene.render.alpha_mode = 'SKY'

            for obj in bpy.data.objects:
                obj.hide = True
            render_opengl(selfname + "_%s_OpenGL_Bgimg"%identifier)

        #原状復帰
        bpy.context.scene.render.filepath = filepath
        bpy.context.space_data.show_world = show_world
        bpy.context.scene.render.alpha_mode = alpha_mode
        bpy.context.scene.render.image_settings.file_format = file_format
        bpy.context.scene.world.use_sky_paper = use_sky_paper
        bpy.context.scene.world.horizon_color = horizon_color
        material_states.restore()
        viewstate.restore_viewstate()
        del viewstate
        bpy.context.space_data.lock_camera = lock_camera
        bpy.context.space_data.show_background_images = show_background_images
        if bpy.context.scene.render.use_simplify != use_simplify:
            bpy.context.scene.render.use_simplify = use_simplify

def get_objects_materials(objects):
    materials = []
    for obj in objects:
        if obj.type == "EMPTY":
            if obj.dupli_group:
                materials.extend(get_objects_materials(obj.dupli_group.objects))
            continue
        try:
            materials.extend(obj.data.materials)
        except:
            pass
    return materials

def get_layer_materials(layerindex):
    """指定レイヤーのオブジェクトのマテリアルを取得する"""
    materials = []
    for obj in bpy.context.scene.objects:
        if obj.layers[layerindex]:
            try:
                materials.extend(obj.data.materials)
            except:
                pass
            if obj.type == "EMPTY":
                if obj.dupli_group:
                    materials.extend(get_objects_materials(obj.dupli_group.objects))
    return materials

def mask_except_true_layers(layers):
    """Trueレイヤー以外のマテリアルをマスクする。"""
    for index, layerstate in enumerate(layers):
        if not layerstate:
            materials = get_layer_materials(index)
            for mat in materials:
                if not mat:
                    continue
                # mat.use_transparency = True
                # mat.alpha = 0.01
                # mat.specular_intensity = 0
                mat.diffuse_color = (1, 1, 1)
                mat.use_shadeless = True
                for i in range(len(mat.use_textures)):
                    mat.use_textures[i] = False
        else:
            materials = get_layer_materials(index)
            for mat in materials:
                if not mat:
                    continue
                mat.use_nodes = False
                # mat.diffuse_color = (255/255, 172/255, 172/255)
                mat.diffuse_color = (0,0,0)
                mat.use_shadeless = True
                for i in range(len(mat.use_textures)):
                    mat.use_textures[i] = False
            
                



########################################
#コンポ素材レンダ
########################################
#bpy.ops.fujiwara_toolbox.glrender_compomat() #コンポ素材レンダ
class FUJIWARATOOLBOX_GLRENDER_COMPOMAT(bpy.types.Operator):
    """保存してコンポジット素材のレンダ。カラー・影のGLレンダ、辺レンダ。"""
    bl_idname = "fujiwara_toolbox.glrender_compomat"
    bl_label = "コンポ素材レンダ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        starttime = time.time()

        bpy.context.scene.render.resolution_percentage = 100
        glcompomat_rendermain("layerAll", baselayers=None, edge=True, color=True, mask=False, shadow=True)
        time.sleep(3)
        bpy.ops.fujiwara_toolbox.glrender_compomat_chr() #キャラレイヤ

        endtime = time.time()
        self.report({"INFO"},"レンダ完了　{0:.2f}秒".format(endtime - starttime))
        bpy.ops.wm.save_mainfile()

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#キャラ
########################################
#bpy.ops.fujiwara_toolbox.glrender_compomat_chr() #キャラレイヤ
class FUJIWARATOOLBOX_GLRENDER_COMPOMAT_CHR(bpy.types.Operator):
    """キャラレイヤーをレンダする。レイヤー0-4。"""
    bl_idname = "fujiwara_toolbox.glrender_compomat_chr"
    bl_label = "キャラマスク"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        starttime = time.time()

        current_layers = fjw.layers_current_state()

        # layers = [True for i in range(20)]
        layers = fjw.layers_current_state()
       
        for i in range(5,20):
            layers[i] = False
        
        bpy.context.scene.layers = layers
        glcompomat_rendermain("layerAll", baselayers=current_layers, edge=False, color=False, mask=True, shadow=False)
        bpy.context.scene.layers = current_layers

        endtime = time.time()
        self.report({"INFO"},"レンダ完了　{0:.2f}秒".format(endtime - starttime))
        bpy.ops.wm.save_mainfile()
        return {'FINISHED'}
########################################

########################################
#前景
########################################
#bpy.ops.fujiwara_toolbox.glrender_compomat_front() #前景
class FUJIWARATOOLBOX_GLRENDER_COMPOMAT_FRONT(bpy.types.Operator):
    """前景レイヤーをレンダする。レイヤー5-9。"""
    bl_idname = "fujiwara_toolbox.glrender_compomat_front"
    bl_label = "前景マスク"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        starttime = time.time()

        current_layers = fjw.layers_current_state()

        layers = [True for i in range(20)]
        for i in range(0,5):
            layers[i] = False
        for i in range(10,20):
            layers[i] = False
        
        bpy.context.scene.layers = layers
        glcompomat_rendermain("layerAFront",current_layers, edge=False, color=False, mask=True, shadow=False)
        bpy.context.scene.layers = current_layers

        endtime = time.time()
        self.report({"INFO"},"レンダ完了　{0:.2f}秒".format(endtime - starttime))
        bpy.ops.wm.save_mainfile()
        return {'FINISHED'}
########################################

########################################
#背景
########################################
#bpy.ops.fujiwara_toolbox.glrender_compomat_back() #背景
class FUJIWARATOOLBOX_GLRENDER_COMPOMAT_BACK(bpy.types.Operator):
    """背景レイヤーをレンダする。レイヤー15-19。"""
    bl_idname = "fujiwara_toolbox.glrender_compomat_back"
    bl_label = "背景マスク"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        starttime = time.time()

        current_layers = fjw.layers_current_state()

        layers = [True for i in range(20)]
        for i in range(0,15):
            layers[i] = False
        
        bpy.context.scene.layers = layers
        glcompomat_rendermain("layerCBack",current_layers, edge=False, color=False, mask=True, shadow=False)
        bpy.context.scene.layers = current_layers

        endtime = time.time()
        self.report({"INFO"},"レンダ完了　{0:.2f}秒".format(endtime - starttime))
        bpy.ops.wm.save_mainfile()
        return {'FINISHED'}
########################################























#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

def construct_comiccomposit():
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_specular = True
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_shadow = True
    #bpy.context.scene.render.layers["RenderLayer"].use_pass_combined = True
    bpy.context.scene.render.use_textures = True
    bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
    bpy.context.scene.render.edge_threshold = 255

    #レンダーレイヤー設定
    rl = bpy.context.scene.render.layers[0]
    rl.use_pass_color = True
    rl.use_pass_specular = True
    rl.use_pass_diffuse = True
    rl.use_pass_shadow = True
    rl.use_edge_enhance = False


    ntree = fjw.NodetreeUtils(bpy.context.scene)
    ntree.activate()
    ntree.cleartree()

    nRenderLayers = fjw.NodeUtils(ntree.add("CompositorNodeRLayers","RenderLayers"))
    nCompositeOutput = fjw.NodeUtils(ntree.add("CompositorNodeComposite", "Composite"))
    ngComic = fjw.append_nodetree("漫画コンポジットモノクロ")
    ngiComic = fjw.NodeUtils(ntree.group_instance(ngComic))


    #接続
    ntree.link(nRenderLayers.output("Color"), ngiComic.input("Color"))
    ntree.link(nRenderLayers.output("Image"), ngiComic.input("Diffuse"))
    ntree.link(nRenderLayers.output("Specular"), ngiComic.input("Specular"))
    #ntree.link(nRenderLayers.output("Shadow"), ngiComic.input("Shadow"))

    ntree.link(ngiComic.output("Image"), nCompositeOutput.input("Image"))

    ntree.link(nRenderLayers.output("Alpha"), nCompositeOutput.input("Alpha"))
        

############################################################################################################################
uiitem("漫画コンポジット")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#コンポジット構築のみ
########################################
class FUJIWARATOOLBOX_505834(bpy.types.Operator):#コンポジット構築のみ
    """コンポジット構築のみ"""
    bl_idname = "fujiwara_toolbox.command_505834"
    bl_label = "コンポジット構築のみ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        construct_comiccomposit()
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#プレビュー
########################################
class FUJIWARATOOLBOX_258524(bpy.types.Operator):#プレビュー
    """ビューポートでプレビュー"""
    bl_idname = "fujiwara_toolbox.command_258524"
    bl_label = "プレビュー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        construct_comiccomposit()
        bpy.context.scene.render.resolution_percentage = 25
        #bpy.ops.wm.save_mainfile()
        bpy.ops.render.render("INVOKE_DEFAULT",use_viewport=True)
        #exec_externalutils("fullrender.py")
        
        return {'FINISHED'}
########################################

#########################################
##フルレンダ
#########################################
#class FUJIWARATOOLBOX_185402(bpy.types.Operator):#フルレンダ
#    """バックグラウンドでフルレンダ"""
#    bl_idname = "fujiwara_toolbox.command_185402"
#    bl_label = "フルレンダ"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


####    def execute(self, context):
#        construct_comiccomposit()
#        bpy.context.scene.render.resolution_percentage = 100
#        bpy.ops.wm.save_mainfile()
#        exec_externalutils("fullrender.py")

#        #bpy.ops.render.render("INVOKE_DEFAULT",use_viewport=True)

#        return {'FINISHED'}
#########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("RenderGroup")
############################################################################################################################








"""
レンダグループ
・割当
    単一のレンダグループに割り当てる
    RenderGroup.NNN
    既に割り当てられてる場合は一旦解除する
    グループ解除して毎回新規グループ割当、でいいのでは？→勝手にナンバリングされる

    bpy.ops.group.create(name="RenderGroup")

    グループ解除はグループのほうから辿ってリンク解除していったほうがいいかも


    ----------------------------------------
    カスタムプロパティにレンダグループを保持させる。
    obj["RenderGroup"] = グループ名
    アンリンク時にグループ名を除去する。
    プロパティないときのためにtryでやったほうがいいかも。


"""

def unlink_RenderGroup(self,objects):
    if objects == None:
        return

    if type(objects) == "list":
        if len(objects) == 0:
            return

    if type(objects) == bpy.types.Object:
        tmp = []
        tmp.append(objects)
        objects = tmp

    for group in bpy.data.groups:
        self.report({"INFO"},str(group))

        if "RenderGroup" not in group.name:
            continue

        #RenderGroupだった
        #該当オブジェクトを全てアンリンクする
        for obj in objects:
            if obj.name in group.objects:
                group.objects.unlink(obj)

                try:
                    obj["RenderGroup"] = ""
                    pass
                except :
                    pass
    pass
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#RenderGroup
########################################
class FUJIWARATOOLBOX_716795(bpy.types.Operator):#RenderGroup
    """RenderGroup"""
    bl_idname = "fujiwara_toolbox.command_716795"
    bl_label = "RenderGroup"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #カメラ・ランプを除外
        for obj in bpy.context.selected_objects:
            if obj.type == "CAMERA" or obj.type == "LAMP":
                obj.select = False

        objects = fjw.get_selected_list()
        unlink_RenderGroup(self,objects)
        bpy.ops.group.create(name="RenderGroup")

        #カスタムプロパティに保持
        groupname = ""
        for group in bpy.data.groups:
            if "RenderGroup" in group.name:
                if objects[0].name in group.objects:
                    groupname = group.name
                    break

        for obj in objects:
            obj["RenderGroup"] = groupname
        return {'FINISHED'}
########################################

########################################
#親子・連続指定用
########################################
class FUJIWARATOOLBOX_985143(bpy.types.Operator):#親子・連続指定用
    """親子・連続指定用"""
    bl_idname = "fujiwara_toolbox.command_985143"
    bl_label = "親子・連続指定用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_24259()
        bpy.ops.fujiwara_toolbox.command_716795()
        #隠す
        for obj in bpy.context.selected_objects:
            obj.hide = True

        fjw.deselect()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#プロパティから再構成
########################################
class FUJIWARATOOLBOX_880927(bpy.types.Operator):#プロパティから再構成
    """プロパティから再構成"""
    bl_idname = "fujiwara_toolbox.command_880927"
    bl_label = "プロパティから再構成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        targets = fjw.get_selected_list()
        #親子選択
        bpy.ops.fujiwara_toolbox.command_24259()
        for obj in targets:
            obj.select = True
        targets = fjw.get_selected_list()


        groupnames = set()
        for target in targets:
            try:
                groupnames.add(target["RenderGroup"])
                pass
            except  :
                pass

        for groupname in groupnames:
            fjw.deselect

            for obj in targets:
                try:
                    if obj["RenderGroup"] == groupname:
                        obj.select = True
                    pass
                except  :
                    pass
            #レンダグループ
            bpy.ops.fujiwara_toolbox.command_716795()
            pass

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#クリア
########################################
class FUJIWARATOOLBOX_275643(bpy.types.Operator):#クリア
    """クリア"""
    bl_idname = "fujiwara_toolbox.command_275643"
    bl_label = "クリア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        objects = fjw.get_selected_list()
        unlink_RenderGroup(self,objects)
        
        return {'FINISHED'}
########################################


########################################
#割り当て済みを隠す
########################################
class FUJIWARATOOLBOX_824105(bpy.types.Operator):#割り当て済みを隠す
    """割り当て済みを隠す"""
    bl_idname = "fujiwara_toolbox.command_824105"
    bl_label = "割り当て済みを隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VISIBLE_IPO_OFF",mode="")

    def execute(self, context):
        fjw.deselect()
        for group in bpy.data.groups:
            if "RenderGroup" in group.name:
                for obj in group.objects:
                    obj.hide = True

        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






################################################################################
#UIカテゴリ
########################################
#レイヤー
########################################
class CATEGORYBUTTON_845862(bpy.types.Operator):#レイヤー
    """レイヤー"""
    bl_idname = "fujiwara_toolbox.categorybutton_845862"
    bl_label = "レイヤー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("レイヤー",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

"""
    リンクのパスに該当文字列があったら、特定レイヤーに割り振る、というかんじ。
    5-9
    15-19
    は自由レイヤー領域ということで無視。
    ☆range（開始値,終了値+1）
LayerConstitution[""] = range(,)



    レイヤー順、
    エフェクト
    プロップ
    キャラ
    背景
    にほんとはしたい？
    
    レイヤー重ね順から考えてほんとは後ろからつめていきたい。
    後ろづめ機能いる。

    エフェクト、プロップ、キャラと同じレイヤーにしたい場合とわけたい場合
    背景、わけたい場合

    どうするか

    あーあとカテゴリ外、邪魔だからどけてる可能性もあるのか…


    選択物オートレイヤー！
    と、カテゴリで選択
"""

class LayerCategory():
    LayerConstitution = {}
    #LayerConstitution["エフェクト"] = range(0,5)
    #LayerConstitution["プロップ"] = range(0,5)
    #LayerConstitution["キャラ"] = range(0,5)
    #LayerConstitution["背景"] = range(10,15)
    LayerConstitution["エフェクト"] = [0]
    LayerConstitution["プロップ"] = [0]
    LayerConstitution["キャラ"] = [0]
    LayerConstitution["背景"] = range(10,15)

    LayerConstitution["非表示エフェクト"] = [15]
    LayerConstitution["非表示プロップ"] = [16]
    LayerConstitution["非表示キャラ"] = [17]
    LayerConstitution["非表示背景"] = [18]

    CategoryObjects = {}

    def __init__(self):
        for key in self.LayerConstitution.keys():
            self.CategoryObjects[key] = self.getObjects(key)
        return

    def isinCategory(self,obj, category):
        linkedpath = fjw.checkLink(obj)
        if linkedpath is None:
            return False
        if category in linkedpath:
            return True
        return False

    def getObjects(self,category):
        result = []
        for obj in bpy.data.objects:
            if self.isinCategory(obj, category):
                result.append(obj)
        return result

    def layerstoindexlist(self,layers):
        indexlist = []
        for i in range(0,20):
            if layers[i]:
                indexlist.append(i)
        return indexlist

    def layersfromIndexList(self,indexlist):
        layers = [False for i in range(20)]
        for i in indexlist:
            layers[i] = True
        return layers

    #リスト内に、対象レンジ内のアイテムがあるかチェック
    def checklistHasinrangeItem(self,list,targetrange):
        for item in list:
            if item in targetrange:
                return True
        return False

    def isValidLayer(self,obj,category,blendops=None):
        #自由レイヤー以外のカテゴリ外レイヤーにいたらFalse。
        #カテゴリレイヤーにいなくてもFalse

        objlayers = self.layerstoindexlist(obj.layers)

        incategory = False
        for i in objlayers:
            if i in self.LayerConstitution[category]:
                incategory = True
                break

        outofcategory = False
        #全レンジから適合カテゴリを除外したのがアウトレンジ
        outrange = []
        outrange.extend(range(0,5))
        outrange.extend(range(10,15))
        for i in self.LayerConstitution[category]:
            outrange.remove(i)

        for i in outrange:
            if i in objlayers:
                outofcategory = True

        if blendops is not None:
            if not incategory:
                blendops.report({"ERROR"},"カテゴリ範囲内に不在：" + category)
                blendops.report({"ERROR"},obj.name)
            elif outrange:
                blendops.report({"WARNING"},"カテゴリ範囲外に発見：" + category)
                blendops.report({"WARNING"},obj.name)

        return (incategory, outrange)

    def checkall(self, blendops):
        #チェックを走らせる
        for key in self.LayerConstitution.keys():
            for obj in self.CategoryObjects[key]:
                self.isValidLayer(obj, key, blendops)
    
    #オブジェクトが所属してるカテゴリを返す
    def get_category(self,obj):
        if fjw.checkLink(obj) == None:
            return None
        for key in self.LayerConstitution.keys():
            if self.isinCategory(obj,key):
                return key
        return None

    #オブジェクトをそのカテゴリに送る
    #レイヤーオフセットは引数で指定できるように、一応しておく
    def tocategory(self,obj,category,offset=0):
        objlayers = self.layerstoindexlist(obj.layers)

        if self.checklistHasinrangeItem(objlayers,self.LayerConstitution[category]):
            #既にレンジ内にレイヤーがある。のでキャンセル
            #と思ったけど、レンジ外は非表示にしとかないとめんどくさい
            for i in range(20):
                if i not in self.LayerConstitution[category]:
                    obj.layers[i] = False
            return

        index = self.LayerConstitution[category][0]

        if index + offset in self.LayerConstitution[category]:
            index = index + offset

        indexlist = [index]
        obj.layers = self.layersfromIndexList(indexlist)

    #レイヤー位置がマズいものを直す
    #選択物をいきなりカテゴライズしてしまえばそもそもカテゴリ内チェックする必要なかったのでは？
    #def correct(self,obj,category,blendops=None):
    #    incategory, outrange = self.isValidLayer(obj, category, blendops)
    #    if not incategory:
    #        self.tocategory(obj,category)
    #        pass
    #    pass

    def hideemptylayer(self):
        found = [False for i in range(20)]
        for obj in bpy.context.visible_objects:
            if obj.is_library_indirect:
                continue
            for i in range(20):
                if obj.layers[i]:
                    found[i] = True
        bpy.context.scene.layers = found

        pass

    def correct(self,targetlist):
        for obj in targetlist:
            for key in self.LayerConstitution.keys():
                if obj in self.CategoryObjects[key]:
                    self.tocategory(obj,key)

        #メッシュオブジェクト用。
        #特定文字列を検索してそれも指定カテゴリに送る
        meshlist = fjw.find_list("result", targetlist)
        for obj in meshlist:
            if obj.type == "MESH":
                self.tocategory(obj, "キャラ")
        
        self.hideemptylayer()



########################################
#構成チェック
########################################
class FUJIWARATOOLBOX_822286(bpy.types.Operator):#構成チェック
    """構成チェック"""
    bl_idname = "fujiwara_toolbox.command_822286"
    bl_label = "構成チェック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        lc = LayerCategory()
        lc.checkall(self)
        
        return {'FINISHED'}
########################################


########################################
#カテゴリに移動（選択物）
########################################
class FUJIWARATOOLBOX_630218(bpy.types.Operator):#カテゴリに移動（選択物）
    """カテゴリに移動（選択物）"""
    bl_idname = "fujiwara_toolbox.command_630218"
    bl_label = "カテゴリに移動（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        lc = LayerCategory()
        lc.correct(selection)
        
        return {'FINISHED'}
########################################



########################################
#カテゴリに移動（表示全部）
########################################
class FUJIWARATOOLBOX_113350(bpy.types.Operator):#カテゴリに移動（表示全部）
    """カテゴリに移動（表示全部）"""
    bl_idname = "fujiwara_toolbox.command_113350"
    bl_label = "カテゴリに移動（表示全部）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        lc = LayerCategory()
        lc.correct(bpy.context.visible_objects)
        
        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#キャラ手前
########################################
class FUJIWARATOOLBOX_748000(bpy.types.Operator):#キャラ手前
    """キャラ手前"""
    bl_idname = "fujiwara_toolbox.command_748000"
    bl_label = "手前"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")

    def execute(self, context):
        setlayer(0)
        
        return {'FINISHED'}
########################################

########################################
#キャラ
########################################
class FUJIWARATOOLBOX_547202(bpy.types.Operator):#キャラ
    """キャラ"""
    bl_idname = "fujiwara_toolbox.command_547202"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(1)
        
        return {'FINISHED'}
########################################

########################################
#キャラ
########################################
class FUJIWARATOOLBOX_892615(bpy.types.Operator):#キャラ
    """キャラ"""
    bl_idname = "fujiwara_toolbox.command_892615"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(2)
        
        return {'FINISHED'}
########################################

########################################
#キャラ
########################################
class FUJIWARATOOLBOX_60203(bpy.types.Operator):#キャラ
    """キャラ"""
    bl_idname = "fujiwara_toolbox.command_60203"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(3)
        
        return {'FINISHED'}
########################################

########################################
#キャラ奥
########################################
class FUJIWARATOOLBOX_951016(bpy.types.Operator):#キャラ奥
    """キャラ奥"""
    bl_idname = "fujiwara_toolbox.command_951016"
    bl_label = "奥"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(4)
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#背景手前
########################################
class FUJIWARATOOLBOX_977845(bpy.types.Operator):#背景手前
    """背景手前"""
    bl_idname = "fujiwara_toolbox.command_977845"
    bl_label = "手前"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")

    def execute(self, context):
        setlayer(15)
        
        return {'FINISHED'}
########################################

########################################
#背景
########################################
class FUJIWARATOOLBOX_782024(bpy.types.Operator):#背景
    """背景"""
    bl_idname = "fujiwara_toolbox.command_782024"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(16)
        
        return {'FINISHED'}
########################################

########################################
#背景
########################################
class FUJIWARATOOLBOX_288468(bpy.types.Operator):#背景
    """背景"""
    bl_idname = "fujiwara_toolbox.command_288468"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(17)
        
        return {'FINISHED'}
########################################

########################################
#背景
########################################
class FUJIWARATOOLBOX_546419(bpy.types.Operator):#背景
    """背景"""
    bl_idname = "fujiwara_toolbox.command_546419"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(18)
        
        return {'FINISHED'}
########################################

########################################
#背景奥
########################################
class FUJIWARATOOLBOX_844075(bpy.types.Operator):#背景奥
    """背景奥"""
    bl_idname = "fujiwara_toolbox.command_844075"
    bl_label = "奥"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(19)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ストック
########################################
class FUJIWARATOOLBOX_165238(bpy.types.Operator):#ストック
    """ストック"""
    bl_idname = "fujiwara_toolbox.command_165238"
    bl_label = "ストック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(15)
        bpy.context.scene.layers[15] = False

        
        return {'FINISHED'}
########################################

########################################
#2
########################################
class FUJIWARATOOLBOX_377137(bpy.types.Operator):#2
    """2"""
    bl_idname = "fujiwara_toolbox.command_377137"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(16)
        bpy.context.scene.layers[16] = False
        
        return {'FINISHED'}
########################################

########################################
#3
########################################
class FUJIWARATOOLBOX_21253(bpy.types.Operator):#3
    """3"""
    bl_idname = "fujiwara_toolbox.command_21253"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(17)
        bpy.context.scene.layers[17] = False

        return {'FINISHED'}
########################################

########################################
#4
########################################
class FUJIWARATOOLBOX_870290(bpy.types.Operator):#4
    """4"""
    bl_idname = "fujiwara_toolbox.command_870290"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(18)
        bpy.context.scene.layers[18] = False

        return {'FINISHED'}
########################################

########################################
#5
########################################
class FUJIWARATOOLBOX_255842(bpy.types.Operator):#5
    """5"""
    bl_idname = "fujiwara_toolbox.command_255842"
    bl_label = "5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        setlayer(19)
        bpy.context.scene.layers[19] = False
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("背景に移動してそのレイヤーを表示")
############################################################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#1
########################################
class FUJIWARATOOLBOX_720458(bpy.types.Operator):#1
    """1"""
    bl_idname = "fujiwara_toolbox.command_720458"
    bl_label = "1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")

    def execute(self, context):
        target = 10
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False

        

        
        return {'FINISHED'}
########################################

########################################
#2
########################################
class FUJIWARATOOLBOX_756530(bpy.types.Operator):#2
    """2"""
    bl_idname = "fujiwara_toolbox.command_756530"
    bl_label = "2"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        target = 11
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        
        return {'FINISHED'}
########################################

########################################
#3
########################################
class FUJIWARATOOLBOX_589552(bpy.types.Operator):#3
    """3"""
    bl_idname = "fujiwara_toolbox.command_589552"
    bl_label = "3"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        target = 12
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        return {'FINISHED'}
########################################

########################################
#4
########################################
class FUJIWARATOOLBOX_352073(bpy.types.Operator):#4
    """4"""
    bl_idname = "fujiwara_toolbox.command_352073"
    bl_label = "4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        target = 13
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        
        return {'FINISHED'}
########################################

########################################
#5
########################################
class FUJIWARATOOLBOX_283776(bpy.types.Operator):#5
    """5"""
    bl_idname = "fujiwara_toolbox.command_283776"
    bl_label = "5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        target = 14
        setlayer(target)

        bpy.context.scene.layers[target] = True

        for l in range(0,20):
            if l != target:
                bpy.context.scene.layers[l] = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("背景を別ファイルに分離")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#分離
########################################
class FUJIWARATOOLBOX_436578(bpy.types.Operator):#分離
    """分離"""
    bl_idname = "fujiwara_toolbox.command_436578"
    bl_label = "分離"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        basepath = bpy.data.filepath
        baselayers = []
        for i in range(20):
            baselayers.append(bpy.context.scene.layers[i])

        if "bg.blend" in basepath:
            self.report({"WARNING"},"背景ファイルです。")
            return {"CANCELLED"}


        #オリジナル保存
        dir = os.path.dirname(basepath) + os.sep + "orig"
        if not os.path.exists(dir):
            os.mkdir(dir)
        name = os.path.splitext(os.path.basename(basepath))[0]
        blendpath = dir + os.sep + name + ".blend"
        bpy.ops.wm.save_as_mainfile(filepath=blendpath,copy=True)





        #背景用ファイル
        dir = os.path.dirname(basepath)
        name = os.path.splitext(os.path.basename(basepath))[0]
        blendpath = dir + os.sep + name + "bg.blend"

        if os.path.exists(blendpath):
            self.report({"WARNING"},"既に分離されたファイルがあります。")
            return {"CANCELLED"}

        #背景だけ表示
        layers = [False for i in range(20)]
        for i in range(10,15):
            layers[i] = True

        bpy.context.scene.layers = layers
        bpy.ops.wm.save_as_mainfile(filepath=blendpath,copy=True)



        #背景消してオリジナル保存
        bpy.ops.object.select_all(action='SELECT')
        for obj in bpy.data.objects:
            if obj.type == "CAMERA":
                obj.select = False
        bpy.ops.object.delete(use_global=False)

        bpy.context.scene.layers = baselayers


        bpy.ops.wm.save_as_mainfile(filepath=basepath)


        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#本体を開く
########################################
class FUJIWARATOOLBOX_857359(bpy.types.Operator):#本体を開く
    """本体を開く"""
    bl_idname = "fujiwara_toolbox.command_857359"
    bl_label = "本体を開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        basepath = bpy.data.filepath
        if "bg.blend" not in basepath:
            self.report({"WARNING"},"本体ファイルです。")
            return {"CANCELLED"}

        blendpath = basepath.replace("bg.blend", ".blend")
        if not os.path.exists(blendpath):
            self.report({"WARNING"},"ファイルが存在しません。")
            return {"CANCELLED"}

        subprocess.Popen("EXPLORER " + blendpath)
        
        return {'FINISHED'}
########################################







########################################
#背景を開く
########################################
class FUJIWARATOOLBOX_348653(bpy.types.Operator):#背景を開く
    """背景を開く"""
    bl_idname = "fujiwara_toolbox.command_348653"
    bl_label = "背景を開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        basepath = bpy.data.filepath
        if "bg.blend" in basepath:
            self.report({"WARNING"},"背景ファイルです。")
            return {"CANCELLED"}

        blendpath = basepath.replace(".blend", "bg.blend")
        if not os.path.exists(blendpath):
            self.report({"WARNING"},"ファイルが存在しません。")
            return {"CANCELLED"}

        subprocess.Popen("EXPLORER " + blendpath)
        
        
        return {'FINISHED'}
########################################


















############################################################################################################################
#クイック中心
############################################################################################################################
########################################
#中点
########################################
class FUJIWARATOOLBOX_995874(bpy.types.Operator):#中点
    """変形中心を中点"""
    bl_idname = "fujiwara_toolbox.command_995874"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="none")

    def execute(self, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        #グリッドスナップ
        bpy.ops.fujiwara_toolbox.command_357169()
        
        return {'FINISHED'}
########################################

########################################
#それぞれの原点
########################################
#bpy.ops.fujiwara_toolbox.pivot_to_individual() #それぞれの原点
class FUJIWARATOOLBOX_PIVOT_TO_INDIVIDUAL(bpy.types.Operator):
    """それぞれの原点を中心にする"""
    bl_idname = "fujiwara_toolbox.pivot_to_individual"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        #グリッドスナップ
        bpy.ops.fujiwara_toolbox.command_357169()
        return {'FINISHED'}
########################################







########################################
#頂点に
########################################
class FUJIWARATOOLBOX_59910(bpy.types.Operator):#頂点に
    """3Dカーソルを設置して変形の中心に"""
    bl_idname = "fujiwara_toolbox.command_59910"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="none")
    
    def execute(self, context):
        #コンテキストに応じてカーソルを設置
        obj = bpy.context.scene.objects.active

#        if obj.type == "MESH":
#
#
#        if obj.data.is_editmode:
#            for vert in obj.data.vertices:
#                if vert.select:
#                    bpy.ops.view3d.snap_cursor_to_selected()
#                    break;
        ##スナップしないほうが便利
        #bpy.ops.view3d.snap_cursor_to_selected()
        bpy.context.space_data.pivot_point = 'CURSOR'
        
        #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
################################################################################
#UIカテゴリ
########################################
#素体
########################################
class CATEGORYBUTTON_861028(bpy.types.Operator):#素体
    """素体"""
    bl_idname = "fujiwara_toolbox.categorybutton_861028"
    bl_label = "素体"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("素体",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





############################################################################################################################
uiitem("素体")
############################################################################################################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#素体追加
########################################
class FUJIWARATOOLBOX_707900(bpy.types.Operator):#素体追加
    """素体追加"""
    bl_idname = "fujiwara_toolbox.command_707900"
    bl_label = "追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    def execute(self, context):
        import fjw.AssetManager
        fjw.AssetManager.mode = "append"
        fjw.AssetManager.dirtoopen = assetdir + "\\素体\\"
        bpy.ops.file.amfilebrowser("INVOKE_DEFAULT")
        
        

        return {'FINISHED'}
########################################


#置換用
class SPIFileBrowser(bpy.types.Operator):
    """Test File Browser"""
    bl_idname = "file.spifilerowser"
    bl_label = "アセット読み込み"

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
#    http://blender.stackexchange.com/questions/30678/bpy-file-browser-get-selected-file-names
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)


    @classmethod
    def poll(cls, context):
        return True



    #対象名群
    targetnames = []


    #dest
    dest = {}
    dest_objects = []
    dest_geo = None
    def setup_dest_objects(self):
        self.dest_objects = []

        #対象オブジェクトをソースリストに入れる。
        self.dest_geo = bpy.context.scene.objects.active
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        self.dest_objects.append(self.dest_geo)
        for obj in bpy.context.selected_objects:
            self.dest_objects.append(obj)

        #登録先の初期化
        self.dest = {}

        #オブジェクトの登録処理
        for targetname in self.targetnames:
            self.append_dest(targetname)


    def append_dest(self, name):
        for obj in self.dest_objects:
            if name in obj.name:
                self.dest[name] = obj
                break

        return

    #src
    src = {}
    src_objects = []

    #現在選択されているオブジェクトをそのまま処理するので注意
    def setup_src_objects(self):
        self.src_objects = []

        for obj in bpy.context.selected_objects:
            self.src_objects.append(obj)

        self.src = {}

        #オブジェクトの登録処理
        for targetname in self.targetnames:
            self.append_src(targetname)

    def append_src(self, name):
        for obj in self.src_objects:
            if name in obj.name:
                self.src[name] = obj
                break

    #位置・回転・ポーズの転送
    def transfer(self, targetname):
        if targetname not in self.src or targetname not in self.dest:
            return

        sobj = self.src[targetname]
        dobj = self.dest[targetname]

        if sobj is None or dobj is None:
            return

        sobj.location = dobj.location
        sobj.rotation_euler = dobj.rotation_euler

        self.report({"INFO"},"sobj:" + sobj.name + " dobj:" + dobj.name)

        if sobj.type == "ARMATURE" and dobj.type == "ARMATURE":
            #ポーズのコピー
            #ポーズのコピー
            fjw.mode("OBJECT")
            fjw.activate(dobj)
            fjw.mode("POSE")
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.copy()

            fjw.mode("OBJECT")
            fjw.activate(sobj)
            fjw.mode("POSE")
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.paste(flipped=False)


    def transfer_all(self):
        for targetname in self.targetnames:
            self.transfer(targetname)


    def get_geo(self):
        geo = None

        targets = []
        targets.append("Geometry")
        targets.append("geometry")
        targets.append("ジオメトリ")

        for target in targets:
            if target in self.src:
                geo = self.src[target]
                break

        #for obj in self.src_objects:
        #    if( "Geometry" in obj.name or
        #        "geometry"in obj.name or
        #        "ジオメトリ" in obj.name

        #        ):
        #        geo = obj
        #        break


        return geo

    def execute(self, context):
        self.targetnames = []
        self.targetnames.append("geo")
        self.targetnames.append("ジオメトリ")
        self.targetnames.append("素体アーマチュア")
        self.targetnames.append("ArmatureController")
        self.targetnames.append("手コントローラ右")
        self.targetnames.append("手コントローラ左")
        self.targetnames.append("右手")
        self.targetnames.append("左手")
        self.targetnames.append("右足")
        self.targetnames.append("左足")

        self.setup_dest_objects()


        for obj in self.dest:
            if obj == None:
                self.report({"INFO"},"不完全なモデルなので結果が異常な可能性があります。:src")

        fjw.deselect()

        #アペンドする
        for file in self.files:
            with bpy.data.libraries.load(self.directory + "\\" + file.name, link=False, relative=True) as (data_from, data_to):
                data_to.objects = data_from.objects
                print(data_to.objects)

            for obj in data_to.objects:
                if obj.type == "CAMERA":
                    continue
                if obj.type == "LAMP":
                    continue
                if obj.parent != None:
                    if obj.parent.type == "CAMERA":
                        continue
                bpy.context.scene.objects.link(obj)
                obj.select = True

        self.report({"INFO"},self.filepath)
        
        #アペンドしたオブジェクトをソースリストに入れる。
        self.setup_src_objects()

        for obj in self.src:
            if obj == None:
                self.report({"INFO"},"不完全なモデルなので結果が異常な可能性があります。:src")


        fjw.deselect()


        #アペンド終わったので適用していく。
        self.transfer_all()

        fjw.deselect()


        #destの削除
        for obj in self.dest_objects:
            obj.select = True
            bpy.context.scene.objects.active = obj
        bpy.ops.object.delete(use_global=False)

        #bpy.context.scene.objects.active = self.src["geo"]
        #self.src["geo"].select = True
        geo = self.get_geo()
        try:
            fjw.activate(geo)
            geo.select = True
            pass
        except:
            pass

        #無操作で更新
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

        ##デバッグ用レポート
        #self.report({"INFO"},"src")
        #for obj in self.src_objects:
        #    if obj == None:
        #        continue
        #    self.report({"INFO"},obj.name)
        #self.report({"INFO"},"dest")
        #for obj in self.dest_objects:
        #    if obj == None:
        #        continue
        #    self.report({"INFO"},obj.name)

        #ヘアトラッカ設定
        bpy.ops.fujiwara_toolbox.command_815238()

        return {'FINISHED'}

    def invoke(self, context, event):
        self.directory = assetdir + "\素体"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

bpy.utils.register_class(SPIFileBrowser)

########################################
#素体置換
########################################
class FUJIWARATOOLBOX_157507(bpy.types.Operator):#スワップ削除
    """素体置換"""
    bl_idname = "fujiwara_toolbox.command_157507"
    bl_label = "素体置換"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    def execute(self, context):
        geo = None
        for obj in bpy.context.selected_objects:
            if "ジオメトリ" in obj.name:
                geo = obj
                break

        #選択解除
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = geo

        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        
        bpy.ops.file.spifilerowser("INVOKE_DEFAULT")

        return {'FINISHED'}
########################################








class LPIFileBrowser(bpy.types.Operator):
    """Test File Browser"""
    bl_idname = "file.lpifilerowser"
    bl_label = "アセット読み込み"

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
#    http://blender.stackexchange.com/questions/30678/bpy-file-browser-get-selected-file-names
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        """
          ファイル名+ArmatureControllerのアクションをアペンドして、
          指定したジオメトリ内のArmatureControllerのアクションに設定、
          全ボーンを選択してポーズを適用
        """
        geo = bpy.context.scene.objects.active
        
        
        for obj in bpy.data.objects:
            obj.select = False
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        
        amcont = None
        for obj in bpy.context.selected_objects:
            if "ArmatureController" in obj.name:
                amcont = obj
                break
        
        
        #アクションをアペンドする
        
        actname = ""
        fname = ""
        for file in self.files:
            self.report({"INFO"},str(file))
            self.report({"INFO"},file.name)
            _directory = self.directory + os.sep + file.name + os.sep + "Action" + os.sep
            fname = file.name
            actname = file.name.replace(".blend", "") + "ArmatureController"
            _filename = actname
            _filepath = _directory + _filename
            self.report({"INFO"},_directory)
            self.report({"INFO"},_filename)
            self.report({"INFO"},_filepath)
            bpy.ops.wm.append(filepath=_filepath, filename=_filename, directory=_directory)

        self.report({"INFO"},self.filepath)
        
        #ポーズを適用する
        bpy.context.scene.objects.active = amcont
        amcont.pose_library = bpy.data.actions[actname]
        
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.poselib.apply_pose(pose_index=0)
        bpy.ops.pose.select_all(action='DESELECT')
        
        #もしテンポラリフォルダからの利用だったら、通常階層に移動する。
        if "テンポラリ" in self.directory:
            shutil.move(self.directory + fname,assetdir + r"\素体\ポージングプール" + os.sep + fname)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.directory = assetdir + r"\素体\ポージングプール"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

bpy.utils.register_class(LPIFileBrowser)

########################################
#Libポーズ適用
########################################
class FUJIWARATOOLBOX_940955(bpy.types.Operator):#Libポーズ適用
    """Libポーズ適用"""
    bl_idname = "fujiwara_toolbox.command_940955"
    bl_label = "Libポーズ適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    def execute(self, context):
        geo = None
        for obj in bpy.context.selected_objects:
            if "ジオメトリ" in obj.name:
                geo = obj
                break

        #選択解除
        for obj in bpy.data.objects:
           obj.select = False

        bpy.context.scene.objects.active = geo

        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        
        bpy.ops.file.lpifilerowser("INVOKE_DEFAULT")
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#素体抽出
########################################
class FUJIWARATOOLBOX_319683(bpy.types.Operator):#素体抽出
    """素体抽出"""
    bl_idname = "fujiwara_toolbox.command_319683"
    bl_label = "ポーズ抽出展開"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    def execute(self, context):
        if "ジオメトリ" not in bpy.context.scene.objects.active.name:
            self.report({"INFO"},"素体ジオメトリを指定してください")
            return {'FINISHED'}
        
        returnpath = bpy.data.filepath
        
        #現状保存→は、しないほうがいい。
#        bpy.ops.wm.save_mainfile()
        
        geo = bpy.context.scene.objects.active
        
        dir = assetdir + r"\素体\ポージングプール\テンポラリ"
        extractdir = dir
        
        dt = datetime.datetime.now()
        dtstr = dt.strftime("%Y%m%d%H%M%S")
        
        exstractpath = extractdir + os.sep + dtstr + ".blend"
        if not os.path.exists(extractdir):
            os.mkdir(extractdir)
        
        
        #選択解除
        for obj in bpy.data.objects:
           obj.select = False
        
        
        #素体ジオメトリ以下を選択
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        geo.select = True
        

        #ポーズライブラリを登録
        for obj in bpy.context.selected_objects:
            if "ArmatureController" in obj.name:
                bpy.context.scene.objects.active = obj
                
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.poselib.new()
                #ポーズライブラリ名を、日時＋ArmatureControllerに。
                obj.pose_library.name = dtstr + "ArmatureController"
                #ポーズ登録
                bpy.ops.poselib.pose_add(frame=1)
                
                break

        bpy.context.scene.objects.active = geo


        #オブジェクトリストに入れる
        objlist = []
        for obj in bpy.context.selected_objects:
            objlist.append(obj)
        
        
        
        #選択解除
        for obj in bpy.data.objects:
           obj.select = False
        
        #リストにないものを削除
        for obj in bpy.data.objects:
            if obj not in objlist:
                obj.select = True
        bpy.ops.object.delete(use_global=False)
        
        
        
        #表示を整える
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.viewport_shade = 'SOLID'
        
        #ポーズに出力
        bpy.ops.wm.save_mainfile(filepath=exstractpath)
        #開き直す
        bpy.ops.wm.open_mainfile(filepath=returnpath)
        
        
        
        
        
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ヘアトラッカ設定
########################################
class FUJIWARATOOLBOX_815238(bpy.types.Operator):#ヘアトラッカ設定
    """ヘアトラッカ設定"""
    bl_idname = "fujiwara_toolbox.command_815238"
    bl_label = "ヘアトラッカ設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                for bone in obj.pose.bones:
                    if "HairTrackTarget" in bone.name:
                        for constraint in bone.constraints:
                            if constraint.type == "COPY_LOCATION":
                                constraint.target = bpy.context.scene.camera

        return {'FINISHED'}
########################################


########################################
#カメラ目線
########################################
class FUJIWARATOOLBOX_68972(bpy.types.Operator):#カメラ目線
    """カメラ目線"""
    bl_idname = "fujiwara_toolbox.command_68972"
    bl_label = "カメラ目線"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #ヘアトラッカーがカメラと同じ位置なのを利用 ってあー3Dカーソルでもよかった？
        obj = fjw.active()
        if obj.type == "ARMATURE":
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            for bone in obj.pose.bones:
                if "EyeTarget" in bone.name:
                    obj.data.bones.active = obj.data.bones[bone.name]
                    cpyloc = None
                    for constraint in bone.constraints:
                        if constraint.type == "COPY_LOCATION":
                            cpyloc = constraint
                    if cpyloc == None:
                        bpy.ops.pose.constraint_add(type='COPY_LOCATION')
                        for constraint in bone.constraints:
                            if constraint.type == "COPY_LOCATION":
                                cpyloc = constraint
                    cpyloc.target = bpy.context.scene.camera
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#ランプ
########################################
class CATEGORYBUTTON_14843(bpy.types.Operator):#ランプ
    """ランプ"""
    bl_idname = "fujiwara_toolbox.categorybutton_14843"
    bl_label = "ランプ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("ランプ",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LAMP",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#SUN設置
########################################
class FUJIWARATOOLBOX_96315(bpy.types.Operator):#SUN設置
    """SUN設置。ドロップシャドウの見た目はゲームエンジンにて設定できる。"""
    bl_idname = "fujiwara_toolbox.command_96315"
    bl_label = "SUN設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="LAMP_SUN",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        loc = (-1, -1, 2)
        bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False, location=loc, layers=bpy.context.scene.layers)
        obj = bpy.context.scene.objects.active
        obj.layers = [False for i in range(20)]
        obj.rotation_euler[0] = 0.691299
        obj.rotation_euler[1] = 0
        obj.rotation_euler[2] = 0.487015
        obj.data.shadow_method = 'RAY_SHADOW'

        #カラーだとヤバそうだったのでなし。
        # obj.data.ge_shadow_buffer_type = 'VARIANCE'
        # obj.data.shadow_buffer_size = 4096
        # obj.data.shadow_buffer_bias = 0.1
        # obj.data.shadow_buffer_bleed_bias = 0.55

        obj.data.ge_shadow_buffer_type = 'VARIANCE'
        obj.data.shadow_buffer_size = 4096
        obj.data.shadow_buffer_bias = 0.001
        obj.data.shadow_buffer_bleed_bias = 0


        # obj.data.ge_shadow_buffer_type = "SIMPLE"
        # obj.data.shadow_buffer_size = 4096
        
        
        return {'FINISHED'}
########################################


########################################
#屋内用ロングランプ
########################################
class FUJIWARATOOLBOX_831406(bpy.types.Operator):#屋内用ロングランプ
    """屋内用ロングランプ"""
    bl_idname = "fujiwara_toolbox.command_831406"
    bl_label = "屋内用ロングランプ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        cursor = bpy.context.space_data.cursor_location
        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=cursor, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.data.distance = 500
        obj.data.shadow_method = 'RAY_SHADOW'
        obj.data.use_specular = False

        
        return {'FINISHED'}
########################################

########################################
#カメラにポイント設置
########################################
class FUJIWARATOOLBOX_47170(bpy.types.Operator):#カメラにポイント設置
    """カメラにポイント設置"""
    bl_idname = "fujiwara_toolbox.command_47170"
    bl_label = "カメラにポイント設置"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CAMERA_DATA",mode="")

    def execute(self, context):
        fjw.mode("OBJECT")
        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=bpy.context.scene.camera.location, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ボトムバックライト
########################################
class FUJIWARATOOLBOX_770473(bpy.types.Operator):#ボトムバックライト
    """ボトムバックライト"""
    bl_idname = "fujiwara_toolbox.command_770473"
    bl_label = "ボトムバックライト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        target = fjw.active()
        fjw.deselect()
        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=target.location, layers=target.layers)
        lamp = fjw.active()
        fjw.activate(target)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        fjw.deselect()
        fjw.activate(lamp)
        bpy.ops.object.transforms_to_deltas(mode='LOC')
        lamp.location = (0,0.35,-0.35)

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#環境照明
########################################
class FUJIWARATOOLBOX_648653(bpy.types.Operator):#環境照明
    """環境照明"""
    bl_idname = "fujiwara_toolbox.command_648653"
    bl_label = "環境照明"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.context.scene.world.light_settings.use_environment_light = True
        bpy.context.scene.world.light_settings.environment_energy = 0.1

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ライト正規化
########################################
class FUJIWARATOOLBOX_550719(bpy.types.Operator):#ライト正規化
    """ライト正規化　+アクティブオブジェクトのみドロップシャドウをつける"""
    bl_idname = "fujiwara_toolbox.command_550719"
    bl_label = "ライト正規化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type != "LAMP":
                obj.select = False
        
        count = len(bpy.context.selected_objects)
        power = 1 / count
        for obj in bpy.context.selected_objects:
            obj.data.energy = power
            obj.data.shadow_method = 'NOSHADOW'

        bpy.context.scene.objects.active.data.shadow_method = 'RAY_SHADOW'


        return {'FINISHED'}
########################################


########################################
#ランプ全レイヤ化
########################################
class FUJIWARATOOLBOX_682004(bpy.types.Operator):#ランプ全レイヤ化
    """ランプ全レイヤ化"""
    bl_idname = "fujiwara_toolbox.command_682004"
    bl_label = "ランプ全レイヤ化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        layers = bpy.context.scene.layers
        for obj in bpy.data.objects:
            if obj.type == "LAMP":
                for l in range(0,19):
                    if layers[l]:
                        obj.layers[l] = True



        return {'FINISHED'}
########################################



# ########################################
# #全ドロップシャドウオフ
# ########################################
# #bpy.ops.fjw.disable_all_dropshadow() #全ドロップシャドウオフ
# class FUJIWARATOOLBOX_disable_all_dropshadow(bpy.types.Operator):
#     """すべてのランプのドロップシャドウを無効化する"""
#     bl_idname = "fujiwara_toolbox.disable_all_dropshadow"
#     bl_label = "全ドロップシャドウオフ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         for lamp in bpy.data.lamps:
#             lamp.shadow_method = 'NOSHADOW'

#         return {'FINISHED'}
# ########################################











#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



# ################################################################################
# #UIカテゴリ
# ########################################
# #カスタムプロパティ
# ########################################
# class CATEGORYBUTTON_712442(bpy.types.Operator):#カスタムプロパティ
#     """カスタムプロパティ"""
#     bl_idname = "fujiwara_toolbox.categorybutton_712442"
#     bl_label = "カスタムプロパティ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem("カスタムプロパティ",True)
#     uiitem.button(bl_idname,bl_label,icon="",mode="")
#     uiitem.direction = "vertical"

#     def execute(self, context):
#         uicategory_execute(self)
#         return {'FINISHED'}
# ########################################
# ################################################################################








# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------

# ########################################
# #グループ情報を回収
# ########################################
# class FUJIWARATOOLBOX_454471(bpy.types.Operator):#グループ情報を回収
#     """グループ情報を回収"""
#     bl_idname = "fujiwara_toolbox.command_454471"
#     bl_label = "グループ情報を回収"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         #まず全部除去
#         for obj in bpy.data.objects:
#             if "Groups" in obj:
#                 del obj["Groups"]

#         for group in bpy.data.groups:
#             for obj in group.objects:
#                 prop = []
#                 #カスタムプロパティの確認
#                 if "Groups" in obj:
#                     prop = obj["Groups"]
#                 prop.append(group.name)

#                 obj["Groups"] = prop

#         return {'FINISHED'}
# ########################################

# ########################################
# #グループ再生
# ########################################
# class FUJIWARATOOLBOX_490616(bpy.types.Operator):#グループ再生
#     """グループ再生"""
#     bl_idname = "fujiwara_toolbox.command_490616"
#     bl_label = "グループ再生"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
        
#         return {'FINISHED'}
# ########################################









# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------


# ########################################
# #Trackto:CAMERA
# ########################################
# class FUJIWARATOOLBOX_372481(bpy.types.Operator):#Trackto:CAMERA
#     """カスタムプロパティでTrackto:CAMERAをもつものに-Yのカメラトラックをつける"""
#     bl_idname = "fujiwara_toolbox.command_372481"
#     bl_label = "Trackto:CAMERA"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         for obj in bpy.data.objects:
#             if "TrackTo" in obj:
#                 if obj["TrackTo"] == "CAMERA":
#                     con = obj.constraints.new('DAMPED_TRACK')
#                     con.track_axis = 'TRACK_NEGATIVE_Y'
#                     con.target = bpy.context.scene.camera
#                     pass

#         return {'FINISHED'}
# ########################################

# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------



































############################################################################################################################
#スナップ
############################################################################################################################
########################################
#グリッドスナップ
########################################
class FUJIWARATOOLBOX_357169(bpy.types.Operator):#グリッドスナップ
    """グリッドスナップ"""
    bl_idname = "fujiwara_toolbox.command_357169"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_GRID",mode="none")

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = False
        bpy.context.scene.tool_settings.snap_element = 'INCREMENT'
        bpy.context.scene.tool_settings.use_snap_grid_absolute = True
        
        return {'FINISHED'}
########################################

########################################
#面スナップ
########################################
class FUJIWARATOOLBOX_911158(bpy.types.Operator):#面スナップ
    """面スナップ"""
    bl_idname = "fujiwara_toolbox.command_911158"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_FACE",mode="none")

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'FACE'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        
        return {'FINISHED'}
########################################

########################################
#辺スナップ
########################################
class FUJIWARATOOLBOX_993743(bpy.types.Operator):#辺スナップ
    """辺スナップ"""
    bl_idname = "fujiwara_toolbox.command_993743"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'EDGE'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        
        return {'FINISHED'}
########################################


########################################
#頂点スナップ
########################################
class FUJIWARATOOLBOX_33358(bpy.types.Operator):#頂点スナップ
    """頂点スナップ"""
    bl_idname = "fujiwara_toolbox.command_33358"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_VERTEX",mode="none")

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        bpy.context.scene.tool_settings.use_snap_align_rotation = False
        bpy.context.scene.tool_settings.use_snap_project = True
        return {'FINISHED'}
########################################










#http://blenderartists.org/forum/showthread.php?337445-Add-on-rRMB-Menu
def SetLocalTransformRotation(context):

    context.space_data.use_pivot_point_align = False
    context.space_data.transform_orientation = 'LOCAL'
    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        empty_exists, source_empty = GetSourceEmpty(context)
  
        if amount_selected > 1:
        
            # bpy.ops.object.transform_apply works on all the selected objects,
            # but we
            # don't want that.
            #So deselect all first, and later reselect all again.
            original_selected_objects = bpy.context.selected_objects
            
            for i in bpy.context.selected_objects:
                i.select = False

            #Loop through all the objects which were previously selected
            for i in original_selected_objects:

                #Only set the object if the current object is not the active
                #object at the
                #same time
                if context.active_object != i:
                
                    i.select = True
                    
                    i.rotation_mode = 'QUATERNION'
                    
                    #Store the start rotation of the selected object
                    rotation_before = i.matrix_world.to_quaternion()
                    
                    #Remove any parents.  If an Object is a child of another
                    #object, the
                    #Local Transform orientation settings will be messed up
                    RemoveParent(context, i)

                    #Align the rotation of the selected object with the
                    #rotation of the active
                    #object
                    bpy.ops.transform.transform(mode='ALIGN')
                    
                    #Store the rotation of the selected object after it has
                    #been rotated
                    rotation_after = i.matrix_world.to_quaternion()
                    
                    #Calculate the difference in rotation from before to after
                    #the rotation
                    rotation_difference = rotation_before.rotation_difference(rotation_after)

                    #Rotate the object the opposite way as done with the ALIGN
                    #function
                    i.rotation_quaternion = rotation_difference.inverted()
                    
                    
                    obj = context.active_object 
                    context.scene.objects.active = i
                    obj.select = False
                    
                   
                    #Align the local rotation of all the selected objects with
                    #the global
                    #world orientation
                    bpy.ops.object.transform_apply(rotation = True)
                    
                    obj.select = True
                    context.scene.objects.active = obj
                    
                    #Set the roation of the selected object to the rotation of
                    #the active
                    #object
                    i.rotation_quaternion = context.active_object.matrix_world.to_quaternion()
                    
                    #Deselect again
                    i.select = False
                    
            #restore selected objects
            for i in original_selected_objects:
                i.select = True        

        if(amount_selected == 1) and (empty_exists == True) and IsMatrixRightHanded(source_empty.matrix_world):
        
            context.active_object.rotation_mode = 'QUATERNION' 
            
            #Store the start rotation of the selected object
            rotation_before = context.active_object.matrix_world.to_quaternion()
            
            RemoveParent(context, context.active_object)
   
            obj = context.active_object        
            source_empty.select = True 
            context.scene.objects.active = source_empty
            
            #Align the rotation of the selected object with the rotation of the
            #active
            #object
            bpy.ops.transform.transform(mode='ALIGN')
            
            #Set the Object to active
            source_empty.select = False
            context.scene.objects.active = obj 
            
            #Store the rotation of the selected object after it has been
            #rotated
            rotation_after = context.active_object.matrix_world.to_quaternion()
            
            #Calculate the difference in rotation from before to after the
            #rotation
            rotation_difference = rotation_before.rotation_difference(rotation_after)

            #Rotate the object the opposite way as done with the ALIGN function
            context.active_object.rotation_quaternion = rotation_difference.inverted()

            #Align the local rotation of the selected object with the global
            #world
            #orientation
            bpy.ops.object.transform_apply(rotation = True)

            #Set the rotation of the selected object to the rotation of the
            #active
            #object
            context.active_object.rotation_quaternion = source_empty.matrix_world.to_quaternion()


def GetSourceEmpty(context):

    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        if amount_selected == 1:
    
            #Check whether the active object has an empty
            name = "Empty." + context.active_object.name
            try:
                obj = bpy.data.objects[name]
            except KeyError:
                return False, bpy.ops.object
            else:        
                return True, obj
                
        if amount_selected > 1:
            return True, context.active_object
            
    else:
        return False, bpy.ops.object

def IsMatrixRightHanded(mat):

    x = mat.col[0].to_3d()
    y = mat.col[1].to_3d()
    z = mat.col[2].to_3d()
    check_vector = x.cross(y)
    
    #If the coordinate system is right handed, the angle between z and
    #check_vector
    #should be 0, but we will use 0.1 to take rounding errors into account
    angle = z.angle(check_vector)
    
    if angle <= 0.1:
        return True
    else:
        errorStorage.SetError(ErrorMessage.not_right_handed)
        return False

def RemoveParent(context, obj):

    #Remove any parents.  If an Object is a child of another object, the
    #Local Transform orientation settings will be messed up if it is changed
    active_obj = context.active_object
    bpy.context.scene.objects.active = obj
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.context.scene.objects.active = active_obj


class RAlignOrientationToSelection(bpy.types.Operator):
    '''Tooltip'''
    bl_description = "Align object's orientation to the selected elements."
    bl_idname = "object.ralign_orientation_to_selection"
    bl_label = "Align Orientation To Selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        obj_type = obj.type
        # return(obj and obj_type in {'MESH', 'CURVE', 'SURFACE', 'ARMATURE',
        # 'FONT',
        # 'LATTICE'} and context.mode == 'OBJECT')
        return(obj and obj_type in {'MESH'})

    def execute(self, context):

        selected = context.selected_objects
        obj = context.active_object
        objects = bpy.data.objects
        storeCursorX = context.space_data.cursor_location.x
        storeCursorY = context.space_data.cursor_location.y
        storeCursorZ = context.space_data.cursor_location.z

        #Create custom orientation
        bpy.context.space_data.transform_orientation = 'NORMAL'
        bpy.ops.transform.create_orientation(name="rOrientation", use=True, overwrite=True)
        bpy.ops.view3d.snap_cursor_to_selected()

        #Exit to Object Mode
        bpy.ops.object.editmode_toggle()

        #1st Layer visibility
        first_layer_was_off = False

        if bpy.context.scene.layers[0] != True:

            first_layer_was_off = True
            bpy.context.scene.layers[0] = True


        #Add empty aligned to the orientation
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        empty = context.selected_objects
        bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='rOrientation', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

        #Copy Rotation from empty
        obj.select = True
        SetLocalTransformRotation(context)

        #Delete empty
        bpy.ops.object.select_all(action='DESELECT')
        for obj in empty:
            obj.select = True
        bpy.ops.object.delete()

        #Restore state
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            obj.select = True
        bpy.context.scene.objects.active = obj
        context.space_data.cursor_location.x = storeCursorX
        context.space_data.cursor_location.y = storeCursorY
        context.space_data.cursor_location.z = storeCursorZ

        if first_layer_was_off:

            bpy.context.scene.layers[0] = False

        bpy.ops.object.editmode_toggle()

        return {'FINISHED'}















































#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#MOD
########################################
class CATEGORYBUTTON_812057(bpy.types.Operator):#MOD
    """MOD"""
    bl_idname = "fujiwara_toolbox.categorybutton_812057"
    bl_label = "MOD"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("MOD",True)
    uiitem.button(bl_idname,bl_label,icon="MODIFIER",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################










#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#適用（選択物）
########################################
class FUJIWARATOOLBOX_557231(bpy.types.Operator):#適用（選択物）
    """適用（選択物）。シェイプキーは削除される。"""
    bl_idname = "fujiwara_toolbox.command_557231"
    bl_label = "mod適用（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")

    def execute(self, context):
        #for obj in bpy.data.objects:
        #    if obj.select == True :
        #        bpy.context.scene.objects.active = obj
        #        for mod in obj.modifiers:
        #            try:
        #                bpy.ops.object.modifier_apply(modifier=mod.name)
        #            except:
        #                #ダメだったのでmod除去
        #                bpy.ops.object.modifier_remove(modifier=mod.name)
        for obj in fjw.get_selected_list():
            fjw.activate(obj)
            modu = fjw.Modutils(obj)
            for mod in obj.modifiers:
                if "裏ポリエッジ" in mod.name:
                    continue

                modu.apply(mod)

                # try:
                #     bpy.ops.object.modifier_apply(modifier=mod.name)
                # except:
                #     #ダメだったのでmod除去
                #     bpy.ops.object.modifier_remove(modifier=mod.name)        
        


        
        return {'FINISHED'}
########################################





########################################
#複製系だけ適用（選択物）
########################################
class FUJIWARATOOLBOX_661107(bpy.types.Operator):#複製系だけ適用（選択物）
    """複製系だけ適用（選択物）"""
    bl_idname = "fujiwara_toolbox.command_661107"
    bl_label = "複製系だけ適用（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")

    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if (mod.type == "MIRROR") or (mod.type == "ARRAY"):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        
        return {'FINISHED'}
########################################


########################################
#適用・隠す
########################################
class FUJIWARATOOLBOX_234815(bpy.types.Operator):#適用・隠す
    """適用・隠す"""
    bl_idname = "fujiwara_toolbox.command_234815"
    bl_label = "適用・隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if (obj.type == "MESH"):
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    #if (mod.type == "MIRROR")||(mod.type ==
                    #"SUBSURF")||(mod.type ==
                    #"SHRINKWRAP")||(mod.type == "ARRAY"):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                obj.hide = True
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#MODソート
########################################
#bpy.ops.fujiwara_toolbox.sort_mod() #MODソート
class FUJIWARATOOLBOX_SORT_MOD(bpy.types.Operator):
    """モディファイアの順番を整列する。"""
    bl_idname = "fujiwara_toolbox.sort_mod"
    bl_label = "MODソート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        selection = fjw.get_selected_list()
        active = fjw.active()
        for obj in selection:
            if obj.type == "MESH":
                fjw.activate(obj)
                modu = fjw.Modutils(obj)
                modu.sort()
        if active is not None:
            fjw.activate(active)

        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#厚み用拡縮適用
########################################
class FUJIWARATOOLBOX_474026(bpy.types.Operator):#厚み用拡縮適用
    """厚み用拡縮適用"""
    bl_idname = "fujiwara_toolbox.command_474026"
    bl_label = "厚み用拡縮適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        for obj in fjw.get_selected_list():
            if not fjw.ismesh(obj):
                continue

            for mod in obj.modifiers:
                if mod.type == "SOLIDIFY":
                    mod.thickness *= obj.scale[0]

            pass
        
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ミラー")
############################################################################################################################

########################################
#ミラー左右分離（選択物）
########################################
class FUJIWARATOOLBOX_757415(bpy.types.Operator):#ミラー左右分離（選択物）
    """ミラー左右分離（選択物）"""
    bl_idname = "fujiwara_toolbox.command_757415"
    bl_label = "ミラー左右分離（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_WIREFRAME",mode="")

    def execute(self, context):
        #編集時にfaceいじるにはbmeshを使う必要がある。
        #bmeshについてはこれ↓あと、TextEditorにサンプルコードというかテンプレがある。
        #http://blender.stackexchange.com/questions/2776/how-to-read-vertices-of-quad-faces-using-python-api
        #一応参考
        #http://blenderartists.org/forum/showthread.php?207542-Selecting-a-face-through-the-API&highlight=ow%20do%20I%20select/deselect%20vertices/edges/faces%20with%20python
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                #各種mod適用
                for mod in obj.modifiers:
                    if (mod.type == "MIRROR") or (mod.type == "ARRAY"):
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    if (mod.type == "MIRROR") or (mod.type == "SHRINKWRAP"):
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                
                #グローバル座標
                #http://blenderscripting.blogspot.jp/2013/03/world-coordinates-from-local-coordinates.html
                #om = obj.matrix_world
                
                
                bpy.ops.object.mode_set(mode = 'EDIT') 
                data = obj.data
                bm = bmesh.from_edit_mesh(data)
                bm.faces.active = None
                X = 0
                Y = 1
                Z = 2
                selectflag = False
                #選択リフレッシュ
                for v  in bm.verts:
                    v.select = False
                for e in bm.edges:
                    e.select = False
                for f in bm.faces:
                    f.select = False
                for face in bm.faces:
                    for v in face.verts:
                        if(v.co[X] < 0):
                            face.select = True
                            selectflag = True
                            continue
                for edge in bm.edges:
                    for v in edge.verts:
                        if(v.co[X] < 0):
                            edge.select = True
                            selectflag = True
                            continue
                for v in bm.verts:
                       if(v.co[X] < 0):
                           v.select = True
                           selectflag = True
                           continue
                bmesh.update_edit_mesh(data)
                if selectflag:
                    bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode = 'OBJECT')
        
        #↓先に原点を移動してしまうと、それを参照しているオブジェクトのミラーとかがズレてしまうので最後にやる。
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#X-でミラー化
########################################
class FUJIWARATOOLBOX_900279(bpy.types.Operator):#X-でミラー化
    """X-でミラー化"""
    bl_idname = "fujiwara_toolbox.command_900279"
    bl_label = "X-でミラー化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MIRROR",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            meshu = fjw.MeshUtils(obj)
            meshu.select_byaxis("-X")
            fjw.mode("EDIT")
            meshu.delete()
            
            modu = fjw.Modutils(obj)
            modu.add("Local Mirror", "MIRROR")
            modu.sort()

        return {'FINISHED'}
########################################

########################################
#X+でミラー化
########################################
class FUJIWARATOOLBOX_734909(bpy.types.Operator):#X+でミラー化
    """X+でミラー化"""
    bl_idname = "fujiwara_toolbox.command_734909"
    bl_label = "X+でミラー化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MIRROR",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            meshu = fjw.MeshUtils(obj)
            meshu.select_byaxis("+X")
            meshu.delete()
            
            modu = fjw.Modutils(obj)
            modu.add("Local Mirror", "MIRROR")
            modu.sort()
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#ペアレントミラー
########################################
class FUJIWARATOOLBOX_892110(bpy.types.Operator):#ペアレントミラー
    """ペアレントミラー"""
    bl_idname = "fujiwara_toolbox.command_892110"
    bl_label = "ペアレントミラー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MIRROR",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        #ミラー
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                modu = fjw.Modutils(obj)
                mod = modu.add("Parented Mirror",'MIRROR')

                ##片面化
                #meshu = MeshUtils(obj)
                #if obj.location[0] < 0:
                #    meshu.select_byaxis("-X",True,target.location)
                #else:
                #    meshu.select_byaxis("+X",True,target.location)
                #mode("EDIT")
                #meshu.delete()

        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        
        return {'FINISHED'}
########################################


########################################
#ターゲットミラー
########################################
class FUJIWARATOOLBOX_553492(bpy.types.Operator):#ターゲットミラー
    """ターゲットミラー"""
    bl_idname = "fujiwara_toolbox.command_553492"
    bl_label = "ターゲットミラー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        target = bpy.context.scene.objects.active
        #ミラー
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                if obj != target:
                    modu = fjw.Modutils(obj)
                    mod = modu.add("Target Mirror","MIRROR")
                    mod.mirror_object = target
                    modu.move_top(mod)

                    ##片面化
                    #meshu = MeshUtils(obj)
                    #if obj.location[0] < 0:
                    #    meshu.select_byaxis("-X",True,target.location)
                    #else:
                    #    meshu.select_byaxis("+X",True,target.location)
                    #mode("EDIT")
                    #meshu.delete()
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        return {'FINISHED'}
########################################


########################################
#P・Tミラー除去
########################################
class FUJIWARATOOLBOX_17104(bpy.types.Operator):#ターゲットミラー除去
    """P・Tミラー除去"""
    bl_idname = "fujiwara_toolbox.command_17104"
    bl_label = "P・Tミラー除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        for obj in fjw.get_selected_list():
            modu = fjw.Modutils(obj)
            modu.remove_byname("Target Mirror")
            modu.remove_byname("Parented Mirror")


        return {'FINISHED'}
########################################

########################################
#ミラー適用
########################################
class FUJIWARATOOLBOX_239793(bpy.types.Operator):#ミラー適用
    """ミラー適用"""
    bl_idname = "fujiwara_toolbox.command_239793"
    bl_label = "ミラー適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            for n in range(10):
                mod_mirr = modu.find_bytype("MIRROR")
                if mod_mirr == None:
                    break
                modu.apply(mod_mirr)
        
        return {'FINISHED'}
########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("ペアレントmod")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ペアレントラップ
########################################
class FUJIWARATOOLBOX_519944(bpy.types.Operator):#ペアレントラップ
    """ペアレントラップ"""
    bl_idname = "fujiwara_toolbox.command_519944"
    bl_label = "ペアレントラップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SHRINKWRAP",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        #ラップ
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.target = target
                mod.wrap_method = 'PROJECT'
                mod.use_positive_direction = True
                mod.use_negative_direction = True
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        
        
        return {'FINISHED'}
########################################



########################################
#ペアレント装甲
########################################
class FUJIWARATOOLBOX_907335(bpy.types.Operator):#ペアレント装甲
    """ペアレント装甲"""
    bl_idname = "fujiwara_toolbox.command_907335"
    bl_label = "ペアレント装甲"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                #拡縮の適用
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                #ラップ
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.target = target
                #厚み
                bpy.ops.object.modifier_add(type='SOLIDIFY')
                last = len(obj.modifiers) - 1
                mod = obj.modifiers[last]
                mod.thickness = -0.05
        
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def parent_mesh_deform(self, precision):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj != target:
                    #exists = False
                    ##メッシュデフォームがなかったらかける
                    #for mod in obj.modifiers:
                    #    if mod.type == "MESH_DEFORM":
                    #        exists = True
                    #        break
                    #if not exists:

                        mod_md = None
                        #存在したらそれを使う
                        for mod in obj.modifiers:
                            if mod.type == "MESH_DEFORM":
                                mod_md = mod

                        #まずはシュリンクラップの適用
                        for mod in obj.modifiers:
                            if mod.type == "SHRINKWRAP":
                                bpy.ops.object.modifier_apply(modifier=mod.name)
                        #メッシュデフォームかける
                        bpy.context.scene.objects.active = obj
                        if mod_md == None:
                            bpy.ops.object.modifier_add(type='MESH_DEFORM')
                            last = len(obj.modifiers) - 1
                            mod = obj.modifiers[last]
                            mod_md = mod
                            mod_n = last
                            #一番上にもっていく。mirrorより後。
                            for i in range(mod_n - 1, -1, -1):
                                if obj.modifiers[i].type == "MIRROR":
                                    break
                                else:
                                    bpy.ops.object.modifier_move_up(modifier=mod.name)

                        modu = fjw.Modutils(obj)
                        modu.sort()


                        #バインド
                        #精度6
                        mod_md.precision = precision
                        mod_md.object = target
                        bpy.ops.object.meshdeform_bind(modifier=mod_md.name)
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        



########################################
#ペアレントメッシュデフォーム
########################################
class FUJIWARATOOLBOX_449421(bpy.types.Operator):#ペアレントメッシュデフォーム
    """シュリンクラップは適用。"""
    bl_idname = "fujiwara_toolbox.command_449421"
    bl_label = "ペアレントメッシュデフォーム6"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MESHDEFORM",mode="")

    def execute(self, context):
        parent_mesh_deform(self, 6)
        return {'FINISHED'}
########################################
########################################
#5
########################################
class FUJIWARATOOLBOX_384891(bpy.types.Operator):#5
    """5"""
    bl_idname = "fujiwara_toolbox.command_384891"
    bl_label = "精度5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        parent_mesh_deform(self, 5)
        
        return {'FINISHED'}
########################################

########################################
#精度4
########################################
#bpy.ops.fujiwara_toolbox.parent_meshdeform_4() #精度4
class FUJIWARATOOLBOX_PARENT_MESHDEFORM_4(bpy.types.Operator):
    """ペアレントメッシュデフォーム"""
    bl_idname = "fujiwara_toolbox.parent_meshdeform_4"
    bl_label = "精度4"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        parent_mesh_deform(self, 4)
        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#バインド解除
########################################
class FUJIWARATOOLBOX_44204(bpy.types.Operator):#バインド解除
    """バインド解除"""
    bl_idname = "fujiwara_toolbox.command_44204"
    bl_label = "バインド解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MESH_DEFORM":
                        if mod.is_bound:
                            bpy.ops.object.meshdeform_bind(modifier=mod.name)
        
        return {'FINISHED'}
########################################



########################################
#デフォーム適用
########################################
class FUJIWARATOOLBOX_766913(bpy.types.Operator):#デフォーム適用
    """デフォーム適用"""
    bl_idname = "fujiwara_toolbox.command_766913"
    bl_label = "デフォーム適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")


    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                for mod in obj.modifiers:
                    if mod.type == "MESH_DEFORM":
                        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        return {'FINISHED'}
########################################









########################################
#全て再バインド
########################################
class FUJIWARATOOLBOX_860977(bpy.types.Operator):#全て再バインド
    """メッシュデフォーム全て再バインド"""
    bl_idname = "fujiwara_toolbox.command_860977"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    def execute(self, context):
        #for obj in bpy.context.selected_objects:
        #    if obj.type == "MESH":
        #        bpy.context.scene.objects.active = obj
        #        for mod in obj.modifiers:
        #            if mod.type == "MESH_DEFORM":
        #                if mod.is_bound:
        #                    bpy.ops.object.meshdeform_bind(modifier=mod.name)
        #                bpy.ops.object.meshdeform_bind(modifier=mod.name)
        for obj in fjw.get_selected_list("MESH"):
            fjw.deselect()
            fjw.activate(obj)
            for mod in obj.modifiers:
                if mod.type == "MESH_DEFORM":
                    if mod.is_bound:
                        bpy.ops.object.meshdeform_bind(modifier=mod.name)
                    bpy.ops.object.meshdeform_bind(modifier=mod.name)
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("サーフェスデフォーム")
############################################################################################################################

def get_wrappedsdef_objects():
    selection = fjw.get_selected_list()

    deformed_meshes = []

    armatures = []
    wrap_targets = []
    surface_deformer_meshes = []

    for obj in selection:
        if obj.type == "ARMATURE":
            armatures.append(obj)

    for armature in armatures:
        for child in armature.children:
            modu = fjw.Modutils(child)
            swrap = modu.find_bytype("SHRINKWRAP")
            if swrap is not None:
                surface_deformer_meshes.append(child)
            else:
                wrap_targets.append(child)
    
    for obj in selection:
        if (obj not in armatures) and (obj not in wrap_targets) and (obj not in surface_deformer_meshes):
            deformed_meshes.append(obj)

    return deformed_meshes, armatures, wrap_targets, surface_deformer_meshes

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def surface_deform_bind_all(obj, bound_state_flag):
    fjw.activate(obj)
    modu = fjw.Modutils(obj)
    mods = modu.find_bytype_list("SURFACE_DEFORM")
    for mod in mods:
        if mod.is_bound != bound_state_flag:
            bpy.ops.object.surfacedeform_bind(modifier=mod.name)

# ########################################
# #バインド
# ########################################
# #bpy.ops.fujiwara_toolbox.bind_wrapped_sdef() #バインド
# class FUJIWARATOOLBOX_BIND_WRAPPED_SDEF(bpy.types.Operator):
#     """シュリンクラップつきサーフェスデフォームをバインドする。既にある場合は再バインドされる。"""
#     bl_idname = "fujiwara_toolbox.bind_wrapped_sdef"
#     bl_label = "バインド"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         target = fjw.active()
#         target.select = False
#         selection = fjw.get_selected_list()

#         armature = None
#         if target.parent is not None and target.parent.type == "ARMATURE":
#             armature = target.parent

#         if armature is not None:
#             armature.data.pose_position = "REST"

#         for obj in selection:
#             modu = fjw.Modutils(obj)
#             m_sdef = modu.add("Surface Deform", "SURFACE_DEFORM")
#             m_sdef.target = target
#             modu.sort()
#             surface_deform_bind_all(obj, True)

#         if armature is not None:
#             armature.data.pose_position = "POSE"

#         return {'FINISHED'}
# ########################################
########################################
#バインド
########################################
#bpy.ops.fujiwara_toolbox.bind_sdef() #バインド
class FUJIWARATOOLBOX_BIND_SDEF(bpy.types.Operator):
    """サーフェスデフォームをバインドする。既にある場合は再バインドされる。"""
    bl_idname = "fujiwara_toolbox.bind_sdef"
    bl_label = "バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        target = fjw.active()
        target.select = False
        selection = fjw.get_selected_list()

        for obj in selection:
            modu = fjw.Modutils(obj)
            m_sdef = modu.add("Surface Deform", "SURFACE_DEFORM")
            m_sdef.target = target
            modu.sort()
            surface_deform_bind_all(obj, True)
            fjw.deselect()
            fjw.activate(target)
            obj.select = True
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


        return {'FINISHED'}
########################################


# ########################################
# #再バインド
# ########################################
# #bpy.ops.fujiwara_toolbox.rebind_sdef() #再バインド
# class FUJIWARATOOLBOX_REBIND_SDEF(bpy.types.Operator):
#     """再バインドする。"""
#     bl_idname = "fujiwara_toolbox.rebind_sdef"
#     bl_label = "再バインド"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         selection = fjw.get_selected_list()

#         for obj in selection:
#             modu = fjw.Modutils(obj)
#             m_sdefs = modu.find_bytype_list("SURFACE_DEFORM")

#             armatures = []
#             for m_sdef in m_sdefs:
#                 target = m_sdef.target
#                 self.report({"INFO"}, "target:"+target.name)
                
#                 if target.parent is not None and target.parent.type == "ARMATURE":
#                     armatures.append(target.parent)
            
#             surface_deform_bind_all(obj, False)

#             for armature in armatures:
#                 armature.data.pose_position = "REST"
#                 self.report({"INFO"}, "armature:"+armature.name)

#             surface_deform_bind_all(obj, True)

#             for armature in armatures:
#                 armature.data.pose_position = "POSE"
#                 self.report({"INFO"}, "armature:"+armature.name)
                
#             bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
#         return {'FINISHED'}
# ########################################
########################################
#再バインド
########################################
#bpy.ops.fujiwara_toolbox.rebind_sdef() #再バインド
class FUJIWARATOOLBOX_REBIND_SDEF(bpy.types.Operator):
    """再バインドする。"""
    bl_idname = "fujiwara_toolbox.rebind_sdef"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        selection = fjw.get_selected_list()

        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            for mod in obj.modifiers:
                if mod.type == "SURFACE_DEFORM":
                    if mod.is_bound:
                        bpy.ops.object.surfacedeform_bind(modifier=mod.name)
                    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
            # modu = fjw.Modutils(obj)
            # m_sdefs = modu.find_bytype_list("SURFACE_DEFORM")
            # surface_deform_bind_all(obj, False)
            # surface_deform_bind_all(obj, True)
        return {'FINISHED'}
########################################

########################################
#バインド解除
########################################
#bpy.ops.fujiwara_toolbox.surfacedeform_unbind() #バインド解除
class FUJIWARATOOLBOX_SURFACEDEFORM_UNBIND(bpy.types.Operator):
    """サーフェスデフォームのバインドを解除する。"""
    bl_idname = "fujiwara_toolbox.surfacedeform_unbind"
    bl_label = "バインド解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type == "MESH":
                fjw.activate(obj)
                modu = fjw.Modutils(obj)
                sd = modu.find_bytype("SURFACE_DEFORM")
                if sd is not None:
                    if sd.is_bound:
                        bpy.ops.object.surfacedeform_bind(modifier=sd.name)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("マルチ解像度サーフェスデフォーム")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

class MultiResSurfaceDeform():
    @classmethod
    def getMultiresNames(self, obj):
        """リスト表示用"""
        result = []
        modu = fjw.Modutils(obj)
        mods = modu.find_bytype_list("SURFACE_DEFORM")
        for mod in mods:
            if "Sdef_" not in mod.name:
                continue
            name = mod.name.split("_")[1]
            if name not in result:
                result.append(name)
        return result

    def __init__(self, obj, target):
        print("~~~~~~~~~~~~")
        self.obj = obj
        self.target = target
        print((obj, target))
        self.modu = fjw.Modutils(obj)
        self.subsurf = self.modu.find_bytype("SUBSURF")
        print(self.subsurf)
        self.levels = self.subsurf.levels

    def modname(self, level):
        # return "Sdef_" + self.target.name + "_" + level
        return "Sdef_%s_%d"%(self.target.name, level)

    def get_level(self, name):
        # nameの最後のlevelを得る
        return name.split("_")[-1]

    def sdef(self, level):
        # 探す
        m = None
        mods = self.modu.find_bytype_list("SURFACE_DEFORM")
        for mod in mods:
            # m_level = self.get_level(mod.name)
            # if m_level == level:
            if mod.name == self.modname(level):
                m = mod
                break
        # ないので作る
        if m is None:
            m = self.modu.add(self.modname(level), "SURFACE_DEFORM")
        m.target = self.target
        return m

    def store(self):
       self.render_bu = fjw.PropBackup(bpy.context.scene.render)
       self.render_bu.store("use_simplify")
       self.render_bu.store("simplify_subdivision")

    def restore(self):
        self.render_bu.restore()

    def bind(self):
        self.store()
        fjw.activate(self.obj)
        for level in range(self.levels+1):
            bpy.context.scene.render.use_simplify = True
            bpy.context.scene.render.simplify_subdivision = level
            # self.subsurf.levels = level
            sdef = self.sdef(level)
            if not sdef.is_bound:
                bpy.ops.object.surfacedeform_bind(modifier=sdef.name)
        self.restore()

    def remove(self):
        print("remove...")
        print("target:"+str(self.target))
        remove_list = []
        fjw.activate(self.obj)
        for level in range(self.levels+1):
            sdef = self.sdef(level)
            if sdef.target == self.target:
                print(sdef.name)
                remove_list.append(sdef)

        for mod in remove_list:
            self.modu.remove(mod)
        print("done.")

########################################
#アタッチ
########################################
#bpy.ops.fujiwara_toolbox.mutires_sdeform_attouch() #アタッチ
class FUJIWARATOOLBOX_MUTIRES_SDEFORM_ATTOUCH(bpy.types.Operator):
    """Subsurfのレベルごとにサーフェスデフォームを作成する。"""
    bl_idname = "fujiwara_toolbox.mutires_sdeform_attouch"
    bl_label = "アタッチ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        # アクティブ=ターゲット
        target = fjw.active()
        obj = fjw.another(target, fjw.get_selected_list())
        mrsfd = MultiResSurfaceDeform(obj, target)
        mrsfd.bind()
        return {'FINISHED'}
########################################

########################################
#再バインド
########################################
#bpy.ops.fujiwara_toolbox.mutires_sdeform_rebind() #再バインド
class FUJIWARATOOLBOX_MUTIRES_SDEFORM_REBIND(bpy.types.Operator):
    """すべてのマルチ解像度サーフェスデフォームを再バインドする。"""
    bl_idname = "fujiwara_toolbox.mutires_sdeform_rebind"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def enum_callback(scene, context):
        result = []

        obj = fjw.active()
        sdeftarget_names = MultiResSurfaceDeform.getMultiresNames(obj)

        for sdeftarget_name in sdeftarget_names:
            name = "target:"+sdeftarget_name
            label = sdeftarget_name
            description = ""
            result.append((name, label, description))
        return result

    targets = EnumProperty(
        name="マルチ解像度サーフェスデフォーム",
        description="ターゲット",
        items=enum_callback
    )

    def execute(self, context):
        self.report({"INFO"}, str(self.targets))
        target_name = self.targets.replace("target:", "")
        target = fjw.object(target_name)
        obj = fjw.active()
        mrsfd = MultiResSurfaceDeform(obj, target)
        mrsfd.bind()

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)
########################################

########################################
#除去
########################################
#bpy.ops.fujiwara_toolbox.mutires_sdeform_remove() #除去
class FUJIWARATOOLBOX_MUTIRES_SDEFORM_REMOVE(bpy.types.Operator):
    """指定したマルチ解像度サーフェスデフォームを除去する。"""
    bl_idname = "fujiwara_toolbox.mutires_sdeform_remove"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def enum_callback(scene, context):
        result = []

        obj = fjw.active()
        sdeftarget_names = MultiResSurfaceDeform.getMultiresNames(obj)

        for sdeftarget_name in sdeftarget_names:
            name = "target:"+sdeftarget_name
            label = sdeftarget_name
            description = ""
            result.append((name, label, description))
        return result

    targets = EnumProperty(
        name="マルチ解像度サーフェスデフォーム",
        description="ターゲット",
        items=enum_callback
    )

    def execute(self, context):
        self.report({"INFO"}, str(self.targets))
        target_name = self.targets.replace("target:", "")
        target = fjw.object(target_name)
        obj = fjw.active()
        mrsfd = MultiResSurfaceDeform(obj, target)
        mrsfd.remove()

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("ラティス")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ラティスを設定
########################################
#bpy.ops.fujiwara_toolbox.set_lattice() #ラティスを設定
class FUJIWARATOOLBOX_SET_LATTICE(bpy.types.Operator):
    """選択おブジェクにアクティブオブジェクトへのラティスモディファイアを設定する"""
    bl_idname = "fujiwara_toolbox.set_lattice"
    bl_label = "ラティスを設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        active = fjw.active()
        if active.type != "LATTICE":
            report({"WARNING"}, "ラティスを最後に選択してください")
            return {"CANCELLED"}

        selection = fjw.get_selected_list()
        for obj in selection:
            if obj == active:
                continue
            if obj.type != "MESH":
                continue

            modu = fjw.Modutils(obj)
            mlat = modu.add("Lattice", "LATTICE")
            mlat.object = active


        return {'FINISHED'}
########################################

########################################
#アーマチュア生成
########################################
#bpy.ops.fujiwara_toolbox.lattice_generate_armature() #アーマチュア生成
class FUJIWARATOOLBOX_LATTICE_GENERATE_ARMATURE(bpy.types.Operator):
    """ラティスの選択頂点をボーンにしたアーマチュアを生成する。"""
    bl_idname = "fujiwara_toolbox.lattice_generate_armature"
    bl_label = "アーマチュア生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        lattice = fjw.active()
        if lattice.type != "LATTICE":
            report({"WARNING"}, "ラティスを選択してください。")
            return {"CANCELLED"}

        parent = lattice.parent
        parent_type = lattice.parent_type
        parent_bone = lattice.parent_bone


        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(lattice)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


        fjw.mode("EDIT")
        lattice_points = []
        for index, p in enumerate(lattice.data.points):
            if p.select:
                print("p:%s"%str(p.co_deform))
                pos = Vector((p.co_deform.x * lattice.scale.x, p.co_deform.y * lattice.scale.y, p.co_deform.z * lattice.scale.z))
                lattice_points.append((index, Vector((pos.x, pos.y, pos.z))))

        fjw.mode("OBJECT")
        for data in lattice_points:
            index = data[0]
            p = data[1]
            vg = lattice.vertex_groups.new(name="bonefromlattice.%03d"%index)
            vg.add([index], 1, "ADD")

        # pos = (lattice.matrix_world[0][3], lattice.matrix_world[1][3], lattice.matrix_world[2][3])
        pos = lattice.location
        bpy.ops.object.armature_add(view_align=False, enter_editmode=False, location=pos, layers=lattice.layers)
        armature = fjw.active()
        armature.name = "Lattice Controller"
        armature.rotation_euler = lattice.rotation_euler
        armature.rotation_quaternion = lattice.rotation_quaternion
        armature.rotation_quaternion = lattice.rotation_quaternion
        armature.rotation_mode = lattice.rotation_mode
        fjw.mode("EDIT")
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.delete()

        edit_bones = armature.data.edit_bones
        for data in lattice_points:
            index = data[0]
            p = data[1]

            b = edit_bones.new("bonefromlattice.%03d"%index)
            b.head = p
            pc = Vector((p.x, p.y, p.z))
            # b.tail = p + pc
            b.tail = p + Vector((0, 0, 0.05))
        fjw.mode("OBJECT")

        fjw.deselect()
        lattice.select = True
        fjw.activate(armature)
        bpy.ops.object.parent_set(type='ARMATURE_NAME')

        if parent:
            fjw.deselect()
            armature.select = True
            fjw.activate(parent)

            if parent_type == "OBJECT":
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            if parent_type == "BONE":
                fjw.mode("POSE")

                layerstates = []
                for state in parent.data.layers:
                    layerstates.append(state)

                parent.data.layers = [True for i in range(len(parent.data.layers))]

                parent.data.bones.active = parent.data.bones[parent_bone]
                bpy.ops.object.parent_set(type='BONE_RELATIVE')

                parent.data.layers = layerstates

        return {'FINISHED'}
########################################

















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("その他")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#カーブにアタッチ
########################################
class FUJIWARATOOLBOX_531573(bpy.types.Operator):#カーブにアタッチ
    """カーブにアタッチ"""
    bl_idname = "fujiwara_toolbox.command_531573"
    bl_label = "カーブにアタッチ（シングル）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        curve = None
        mesh = None
        for obj in fjw.get_selected_list():
            if obj.type == "CURVE":
                curve = obj
            if obj.type == "MESH":
                mesh = obj

        #メッシュの拡縮適用
        fjw.deselect()
        fjw.activate(mesh)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


        #カーブをスプラインごとに分離する
        fjw.deselect()
        fjw.activate(curve)

        #カーブのベベルをゼロに
        curve.data.bevel_depth = 0

        #セパレートするごとにスプラインのインデックスかわってんじゃないの？
        splines = curve.data.splines
        for i in range(len(splines) - 1):
            fjw.mode("EDIT")
            spline = splines[1]

            #個別分離
            bpy.ops.curve.select_all(action='DESELECT')
            for point in spline.points:
                point.select = True
            if spline.type == "BEZIER":
                for bzp in spline.bezier_points:
                    bzp.select_control_point = True
            bpy.ops.curve.separate()
            fjw.mode("OBJECT")
            fjw.mode("EDIT")



        #mode("EDIT")
        #for index, spline in enumerate(curve.data.splines):
        #    #0番は残す
        #    if index == 0:
        #        continue

        #    #個別分離
        #    bpy.ops.curve.select_all(action='DESELECT')
        #    for point in spline.points:
        #        point.select = True
        #    if spline.type == "BEZIER":
        #        for bzp in spline.bezier_points:
        #            bzp.select_control_point = True
        #    bpy.ops.curve.separate()
        fjw.mode("OBJECT")
        curves = fjw.get_selected_list()

        #元オブジェクト名でグループ化
        fjw.group(curve.name)

        objs = []

        #あらかじめ複製を作成する
        for index, curve in enumerate(curves):
            #if index == 0:
            #    objs.append(mesh)
            #    continue
            fjw.deselect()
            fjw.activate(mesh)
            #リンク複製
            bpy.ops.object.duplicate(linked=True)
            objs.append(fjw.active())

        #オブジェクトを複製してアタッチしてく
        for index, curve in enumerate(curves):
            obj = objs[index]

            fjw.deselect()
            #トランスフォームをあわせる
            fjw.activate(obj)
            obj.location = curve.location
            obj.rotation_euler = curve.rotation_euler
            
            mod_arr = fjw.add_mod("ARRAY")
            mod_arr.fit_type = "FIT_CURVE"
            mod_arr.curve = curve

            mod_crv = fjw.add_mod("CURVE")
            mod_crv.object = curve

            #グループ・ペアレント
            fjw.group(mesh.name)

            fjw.activate(curve)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)



        return {'FINISHED'}
########################################

########################################
#オープンエッジの線画化
########################################
class FUJIWARATOOLBOX_141722(bpy.types.Operator):#オープンエッジの線画化
    """オープンエッジの線画化"""
    bl_idname = "fujiwara_toolbox.command_141722"
    bl_label = "オープンエッジの線画化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        fjw.deselect()

        for obj in selection:
            if obj.type != "MESH":
                continue
            #オープンエッジの分離
            fjw.activate(obj)
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')
            fjw.mode("OBJECT")

            target = None
            for tmp_target in fjw.get_selected_list():
                if tmp_target != obj:
                    target = tmp_target
            target.name = obj.name + "_openedgeline"

            fjw.deselect()

            #スキンで線画化
            fjw.activate(target)
            #モディファイアをすべて除去
            target.modifiers.clear()
            #マテリアルをすべて除去
            target.data.materials.clear()
            
            #黒マテリアルの割当
            mat = None
            if "主線黒" in bpy.data.materials:
                mat = bpy.data.materials["主線黒"]
            else:
                mat = bpy.data.materials.new(name="主線黒")
                mat.diffuse_color = (0, 0, 0)
                mat.use_shadeless = True
            target.data.materials.append(mat)

            #スキンモディファイア
            bpy.ops.object.modifier_add(type='SKIN')
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.skin_root_mark()
            ssize = 0.0025
            bpy.ops.transform.skin_resize(value=(ssize, ssize, ssize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            fjw.mode("OBJECT")

        return {'FINISHED'}
########################################


# ########################################
# #MOD整列
# ########################################
# class FUJIWARATOOLBOX_288910(bpy.types.Operator):#MOD整列
#     """MOD整列"""
#     bl_idname = "fujiwara_toolbox.command_288910"
#     bl_label = "MOD整列"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")


#     def execute(self, context):
#         for obj in fjw.get_selected_list():
#             if obj.type != "MESH":
#                 continue
    
#             modu = fjw.Modutils(obj)
#             modu.sort()
#         return {'FINISHED'}
# ########################################


########################################
#シームレスラップ
########################################
#bpy.ops.fujiwara_toolbox.setup_normalcopy_wrap() #シームレスラップ
class FUJIWARATOOLBOX_SETUP_NORMALCOPY_WRAP(bpy.types.Operator):
    """選択オブジェクトをターゲットとして、選択面に対して法線コピーで馴染むシュリンクラップをセットアップする。"""
    bl_idname = "fujiwara_toolbox.setup_normalcopy_wrap"
    bl_label = "シームレスラップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def set_weight_and_selectless(self, value):
        bpy.context.scene.tool_settings.vertex_group_weight = value
        bpy.ops.object.vertex_group_assign()
        bpy.ops.mesh.select_less(use_face_step=True)

    def has_vertex_group(self, obj):
        vg_index = obj.vertex_groups.find("Shrinkwrap")
        if vg_index == -1:
            return False
        return True

    def set_active_group(self, obj, name):
        vg_index = obj.vertex_groups.find(name)
        if vg_index == -1:
            gname = name
            obj.vertex_groups.new(name=gname)
            vg_index = obj.vertex_groups.find(name)
        obj.vertex_groups.active_index = vg_index

    def assign_weights(self, obj, name):
        self.set_active_group(obj,name)

        #頂点グループにアサイン
        bpy.ops.object.vertex_group_assign()
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset=0.01, segments=4, vertex_only=False)
        bpy.ops.object.vertex_group_assign()
        bpy.ops.object.vertex_group_select()
        self.set_weight_and_selectless(0)
        self.set_weight_and_selectless(0.2)
        self.set_weight_and_selectless(0.4)
        self.set_weight_and_selectless(0.6)
        self.set_weight_and_selectless(0.8)
        self.set_weight_and_selectless(1)

    def execute(self, context):
        active = fjw.active()
        target = None

        #ターゲットの取得
        for obj in fjw.get_selected_list():
            if obj != active:
                target = obj
                break

        fjw.mode("EDIT")
        #"Shrinkwrap"が存在しないければ自動アサインする
        if not self.has_vertex_group(active):
            self.assign_weights(active, "Shrinkwrap")
        else:
            self.set_active_group(active, "Shrinkwrap")
        fjw.mode("OBJECT")

        #モディファイアの設定
        modu = fjw.Modutils(active)
        sw = modu.find_bytype("SHRINKWRAP")
        if sw is None:
            sw = modu.add("Shrinkwrap", "SHRINKWRAP")
        sw.target = target
        sw.vertex_group = "Shrinkwrap"

        dt = modu.find_bytype("DATA_TRANSFER")
        if dt is None:
            dt = modu.add("DataTransfer", "DATA_TRANSFER")
        dt.object = target
        dt.use_loop_data = True
        dt.data_types_loops = {"CUSTOM_NORMAL"}
        dt.vertex_group = "Shrinkwrap"

        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(active)
        bpy.ops.object.shade_smooth()
        active.data.use_auto_smooth = True


        return {'FINISHED'}
########################################













#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




############################################################################################################################
uiitem("BoolToolカスタム")
############################################################################################################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#Differnce
########################################
class FUJIWARATOOLBOX_476244(bpy.types.Operator):#Differnce
    """Differnce"""
    bl_idname = "fujiwara_toolbox.command_476244"
    bl_label = "Differnce"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_BOOLEAN",mode="")

    def execute(self, context):
        bpy.ops.btool.boolean_diff()
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.context.active_object.select = False
        for obj in bpy.context.selected_objects:
            obj.hide_render = True
        
        
        return {'FINISHED'}
########################################


########################################
#Differnce→隠す
########################################
class FUJIWARATOOLBOX_691601(bpy.types.Operator):#Differnce→隠す
    """Differnce→隠す"""
    bl_idname = "fujiwara_toolbox.command_691601"
    bl_label = "Differnce→隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")
    
    def execute(self, context):
        bpy.ops.btool.boolean_diff()
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.context.active_object.select = False
        for obj in bpy.context.selected_objects:
            obj.hide_render = True
        bpy.ops.object.hide_view_set(unselected=False)
        
        return {'FINISHED'}
########################################


########################################
#Union(Direct)
########################################
class FUJIWARATOOLBOX_69194(bpy.types.Operator):#Union(Direct)
    """Union(Direct)"""
    bl_idname = "fujiwara_toolbox.command_69194"
    bl_label = "Union(Direct)"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_EDGESPLIT",mode="")

    def execute(self, context):
        bpy.ops.btool.boolean_union_direct()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#バウンド非表示
########################################
class FUJIWARATOOLBOX_757208(bpy.types.Operator):#バウンド非表示
    """バウンド非表示"""
    bl_idname = "fujiwara_toolbox.command_757208"
    bl_label = "バウンド非表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.draw_type == 'BOUNDS':
                obj.hide = True
        
        
        
        
        return {'FINISHED'}
########################################

########################################
#bool再計算
########################################
class FUJIWARATOOLBOX_6352(bpy.types.Operator):#bool再計算
    """bool再計算"""
    bl_idname = "fujiwara_toolbox.command_6352"
    bl_label = "bool再計算"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.object.select_all(action='DESELECT')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("便利")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#低subsurf化（選択物）
########################################
class FUJIWARATOOLBOX_962587(bpy.types.Operator):#低subsurf化（選択物）
    """低subsurf化（選択物）"""
    bl_idname = "fujiwara_toolbox.command_962587"
    bl_label = "低subsurf化（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            bpy.ops.object.shade_smooth()

            #自動スムーズはものによってかえたほうがいい
            #obj.data.use_auto_smooth = True
            #obj.data.auto_smooth_angle = 0.523599

            modu = fjw.Modutils(obj)
            subsurfs = modu.find_bytype_list("SUBSURF")

            for subsurf in subsurfs:
                subsurf.levels = 2
                subsurf.render_levels = 2

        fjw.select(selection)
        return {'FINISHED'}
########################################
























#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
################################################################################
#UIカテゴリ
########################################
#メッシュ
########################################
class CATEGORYBUTTON_813381(bpy.types.Operator):#メッシュ
    """メッシュ"""
    bl_idname = "fujiwara_toolbox.categorybutton_813381"
    bl_label = "メッシュ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("メッシュ",True)
    uiitem.button(bl_idname,bl_label,icon="MESH_DATA",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################







############################################################################################################################
uiitem("最高描画タイプ")
############################################################################################################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#バウンド
########################################
class FUJIWARATOOLBOX_630367(bpy.types.Operator):#バウンド
    """バウンド"""
    bl_idname = "fujiwara_toolbox.command_630367"
    bl_label = "バウンド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        objs = fjw.get_selected_list()

        for obj in objs:
            obj.draw_type = "BOUNDS"

        return {'FINISHED'}
########################################

########################################
#ワイヤー
########################################
class FUJIWARATOOLBOX_65984(bpy.types.Operator):#ワイヤー
    """ワイヤー"""
    bl_idname = "fujiwara_toolbox.command_65984"
    bl_label = "ワイヤー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        objs = fjw.get_selected_list()

        for obj in objs:
            obj.draw_type = "WIRE"
        
        return {'FINISHED'}
########################################

########################################
#ソリッド
########################################
#bpy.ops.fujiwara_toolbox.command_807675() #ソリッド
class FUJIWARATOOLBOX_COMMAND_807675(bpy.types.Operator):
    """ソリッド"""
    bl_idname = "fujiwara_toolbox.command_807675"
    bl_label = "ソリッド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        objs = fjw.get_selected_list()

        for obj in objs:
            obj.draw_type = "SOLID"
        return {'FINISHED'}
########################################

########################################
#テクスチャ
########################################
class FUJIWARATOOLBOX_691590(bpy.types.Operator):#テクスチャ
    """テクスチャ"""
    bl_idname = "fujiwara_toolbox.command_691590"
    bl_label = "テクスチャ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        objs = fjw.get_selected_list()

        for obj in objs:
            obj.draw_type = "TEXTURED"
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("UV")
############################################################################################################################
########################################
#スマートUV投影（各選択物）
########################################
class FUJIWARATOOLBOX_339338(bpy.types.Operator):#スマートUV投影（各選択物）
    """スマートUV投影（各選択物）"""
    bl_idname = "fujiwara_toolbox.command_339338"
    bl_label = "スマートUV投影（各選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        for obj in fjw.get_selected_list():
            fjw.activate(obj)
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.reset()
            bpy.ops.uv.smart_project()
            fjw.mode("OBJECT")
        return {'FINISHED'}
########################################






########################################
#ライトマップパック展開（各選択物）
########################################
class FUJIWARATOOLBOX_719855(bpy.types.Operator):#ライトマップパック展開（各選択物）
    """ライトマップパック展開（各選択物）"""
    bl_idname = "fujiwara_toolbox.command_719855"
    bl_label = "ライトマップパック展開（各選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        for obj in fjw.get_selected_list():
            fjw.activate(obj)
            bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=2048, PREF_BOX_DIV=12, PREF_MARGIN_DIV=0.1)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("メッシュ")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#境界クリース
########################################
class FUJIWARATOOLBOX_676177(bpy.types.Operator):#境界クリース
    """境界クリース"""
    bl_idname = "fujiwara_toolbox.command_676177"
    bl_label = "境界クリース"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.transform.edge_crease(value=1)
        
        return {'FINISHED'}
########################################

########################################
#弱クリース
########################################
#bpy.ops.fujiwara_toolbox.crease_04() #クリース0.4
class FUJIWARATOOLBOX_CREASE_04(bpy.types.Operator):
    """メッシュ全体に弱いクリースをかける。"""
    bl_idname = "fujiwara_toolbox.crease_04"
    bl_label = "弱クリース"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        current_mode = obj.mode
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.edge_crease(value=0.2)
        fjw.mode(current_mode)

        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#自動スムーズ
########################################
class FUJIWARATOOLBOX_31891(bpy.types.Operator):#自動スムーズ
    """自動スムーズ"""
    bl_idname = "fujiwara_toolbox.command_31891"
    bl_label = "自動スムーズ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.shade_smooth()

        for obj in fjw.get_selected_list("MESH"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = 0.523599


        
        return {'FINISHED'}
########################################

########################################
#スムーズのみ
########################################
#bpy.ops.fujiwara_toolbox.smooth_only() #スムーズのみ
class FUJIWARATOOLBOX_SMOOTH_ONLY(bpy.types.Operator):
    """自動スムーズオフの普通のスムーズを設定する。"""
    bl_idname = "fujiwara_toolbox.smooth_only"
    bl_label = "スムーズのみ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.shade_smooth()

        for obj in fjw.get_selected_list("MESH"):
            obj.data.use_auto_smooth = False
        return {'FINISHED'}
########################################

########################################
#フラット
########################################
#bpy.ops.fujiwara_toolbox.flat() #フラット
class FUJIWARATOOLBOX_FLAT(bpy.types.Operator):
    """フラットシェーディングの設定。"""
    bl_idname = "fujiwara_toolbox.flat"
    bl_label = "フラット"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.shade_flat()
        return {'FINISHED'}
########################################











#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#法線を反転
########################################
class FUJIWARATOOLBOX_795120(bpy.types.Operator):#法線を反転
    """法線を反転"""
    bl_idname = "fujiwara_toolbox.command_795120"
    bl_label = "法線を反転"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.flip_normals()
                bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#ペラポリ準備
########################################
class FUJIWARATOOLBOX_996345(bpy.types.Operator):#ペラポリ準備
    """ペラポリ準備"""
    bl_idname = "fujiwara_toolbox.command_996345"
    bl_label = "ペラポリ準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        obj = fjw.active()
        modu = fjw.Modutils(obj)
        
        mod = modu.add("Local Mirror", "MIRROR")
        mod.use_clip = True

        mod = modu.add("Solidify", "SOLIDIFY")
        mod.thickness = 0.005
        mod.use_even_offset = True


        return {'FINISHED'}
########################################
















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("メッシュアクション")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#複製分離
########################################
class FUJIWARATOOLBOX_635930(bpy.types.Operator):#複製分離
    """複製分離"""
    bl_idname = "fujiwara_toolbox.dup_and_part"
    bl_label = "複製分離"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_MESH",mode="edit")

    def execute(self, context):
        # baselist = []
        # for obj in bpy.data.objects:
        #     baselist.append(obj)
        
        # bpy.ops.mesh.duplicate(mode=1)
        # bpy.ops.mesh.separate(type='SELECTED')
        
        # bpy.ops.object.editmode_toggle()
        
        # for obj in bpy.data.objects:
        #     if obj not in baselist:
        #         #新しいオブジェクト
        #         bpy.context.scene.objects.active = obj
        #         bpy.ops.object.editmode_toggle()
        #         break
        active = fjw.active()
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        fjw.mode("OBJECT")
        
        for obj in fjw.get_selected_list():
            if obj != active:
                fjw.deselect()
                fjw.activate(obj)
                fjw.mode("EDIT")
                break

        return {'FINISHED'}
########################################

########################################
#ケージとして複製分離
########################################
#bpy.ops.fujiwara_toolbox.dup_as_cage() #ケージとして複製分離
class FUJIWARATOOLBOX_DUP_AS_CAGE(bpy.types.Operator):
    """ケージ用設定で複製分離する。"""
    bl_idname = "fujiwara_toolbox.dup_as_cage"
    bl_label = "ケージとして複製分離"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_MESH",mode="")

    def execute(self, context):
        basename = fjw.active().name
        bpy.ops.fujiwara_toolbox.dup_and_part()
        obj = fjw.active()
        obj.name = basename + "_cage"
        fjw.mode("OBJECT")
        obj.draw_type = 'WIRE'
        obj.hide_render = True

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#装甲化
########################################
class FUJIWARATOOLBOX_273555(bpy.types.Operator):#装甲化
    """装甲化"""
    bl_idname = "fujiwara_toolbox.command_273555"
    bl_label = "装甲化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="edit")

    def execute(self, context):
        
        
        baseobj = bpy.context.scene.objects.active
        ArmorPlate = None
        
        #複製切り出し
        baselist = []
        for obj in bpy.data.objects:
            baselist.append(obj)
        
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        
        bpy.ops.object.editmode_toggle()
        
        for obj in bpy.data.objects:
            if obj not in baselist:
                #新しいオブジェクト
                ArmorPlate = obj
        #        bpy.context.scene.objects.active = obj
        #        bpy.ops.object.editmode_toggle()
                break
        
        #装甲化
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                #拡縮の適用
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                #既存の装甲・ラップmodの除去
                for mod in obj.modifiers:
                    if mod.type == "SHRINKWRAP" or mod.type == "SOLIDIFY" or mod.type == "BOOLEAN" or mod.type == "BEVEL":
                        bpy.ops.object.modifier_remove(modifier=mod.name)
                

                #ラップ→ないほうがいい
                #bpy.ops.object.modifier_add(type='SHRINKWRAP')
                #last = len(obj.modifiers) - 1
                #mod = obj.modifiers[last]
                #mod = add_mod('SHRINKWRAP')
                #mod.target = target
                #厚み
                mod = fjw.add_mod('SOLIDIFY')
                mod.thickness = -0.05
                mod.use_even_offset = True
                mod.use_quality_normals = True
                
                mod = fjw.add_mod('BEVEL')
                mod.width = 0.01
                mod.offset_type = 'WIDTH'

                #エッジにクリースつける
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.transform.edge_crease(value=1)
                fjw.objectmode()

        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        #bpy.context.scene.objects.active = ArmorPlate
        #連続できるようにする
        bpy.context.scene.objects.active = target
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.tool_settings.mesh_select_mode = [False,False,True]

        return {'FINISHED'}
########################################

########################################
#装甲化（内側）
########################################
class FUJIWARATOOLBOX_338159(bpy.types.Operator):#装甲化（内側）
    """装甲化（内側）"""
    bl_idname = "fujiwara_toolbox.command_338159"
    bl_label = "装甲化（内側）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        baseobj = bpy.context.scene.objects.active
        ArmorPlate = None
        
        #複製切り出し
        baselist = []
        for obj in bpy.data.objects:
            baselist.append(obj)
        
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.separate(type='SELECTED')
        
        bpy.ops.object.editmode_toggle()
        
        for obj in bpy.data.objects:
            if obj not in baselist:
                #新しいオブジェクト
                ArmorPlate = obj
        #        bpy.context.scene.objects.active = obj
        #        bpy.ops.object.editmode_toggle()
                break
        
        #装甲化
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        target = bpy.context.scene.objects.active
        
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            if obj != target:
                #拡縮の適用
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                #既存の装甲・ラップmodの除去
                for mod in obj.modifiers:
                    if mod.type == "SHRINKWRAP" or mod.type == "SOLIDIFY" or mod.type == "BOOLEAN" or mod.type == "BEVEL":
                        bpy.ops.object.modifier_remove(modifier=mod.name)
                

                #ラップ→ないほうがいい
                #bpy.ops.object.modifier_add(type='SHRINKWRAP')
                #last = len(obj.modifiers) - 1
                #mod = obj.modifiers[last]
                #mod = add_mod('SHRINKWRAP')
                #mod.target = target
                #厚み
                mod = fjw.add_mod('SOLIDIFY')
                mod.thickness = 0.05
                #mod.use_even_offset = True
                mod.use_quality_normals = True
                
                mod = fjw.add_mod('BEVEL')
                mod.width = 0.01
                mod.offset_type = 'WIDTH'

                #エッジにクリースつける
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.transform.edge_crease(value=1)
                fjw.objectmode()

        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        
        #bpy.context.scene.objects.active = ArmorPlate
        #連続できるようにする
        bpy.context.scene.objects.active = target
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.tool_settings.mesh_select_mode = [False,False,True]
        
        return {'FINISHED'}
########################################


########################################
#厚み反転
########################################
class FUJIWARATOOLBOX_351222(bpy.types.Operator):#厚み反転
    """厚み反転"""
    bl_idname = "fujiwara_toolbox.command_351222"
    bl_label = "厚み反転"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        for obj in bpy.context.selected_objects:
            fjw.activate(obj)

            mod = fjw.get_mod('SOLIDIFY')
            if mod != None:
                mod.thickness *= -1

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------






########################################
#フチ厚み化
########################################
class FUJIWARATOOLBOX_813387(bpy.types.Operator):#フチ厚み化
    """フチ厚み化"""
    bl_idname = "fujiwara_toolbox.command_813387"
    bl_label = "フチ厚み化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SOLIDIFY",mode="edit")

    def execute(self, context):
        obj = bpy.context.scene.objects.active
        
        mod_solid = None
        found = False
        for mod in obj.modifiers:
            if mod.type == "SOLIDIFY":
                mod_solid = mod
                found = True
        
        if not found:
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            last = len(obj.modifiers) - 1
            mod = obj.modifiers[last]
            mod.thickness = -0.05
            mod_solid = mod
        
        mod_solid.use_flip_normals = True
        mod_solid.use_rim_only = True
        mod_solid.offset = 0

        
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        return {'FINISHED'}
########################################


########################################
#スキン化
########################################
class FUJIWARATOOLBOX_994469(bpy.types.Operator):#スキン化
    """スキン化"""
    bl_idname = "fujiwara_toolbox.command_994469"
    bl_label = "スキン化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_SKIN",mode="edit")

    def execute(self, context):
        bpy.ops.fujiwara_toolbox.dup_and_part()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.object.modifier_add(type='SKIN')
        bpy.ops.transform.skin_resize(value=(0.1, 0.1, 0.1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#x*-1
########################################
class FUJIWARATOOLBOX_467890(bpy.types.Operator):#x*-1
    """x*-1"""
    bl_idname = "fujiwara_toolbox.command_467890"
    bl_label = "x*-1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EMPTY_DATA",mode="")

    def execute(self, context):
#        if bpy.context.scene.objects.active.type == "EMPTY":
#            base = bpy.context.scene.objects.active
#            bpy.ops.object.duplicate()
#
#            obj = bpy.context.scene.objects.active
#            bpy.ops.object.constraint_add(type='COPY_LOCATION')
#            bpy.ops.object.constraint_add(type='COPY_ROTATION')
#
#            for constraint in obj.constraints:
#                if constraint.type == "COPY_LOCATION":
#                    constraint.invert_x = True
#                    constraint.target = base
#                if constraint.type == "COPY_ROTATION":
#                    constraint.invert_x = False
#                    constraint.invert_y = True
#                    constraint.invert_z = True
#                    constraint.target = base
        bpy.context.object.scale[0] = -1
        
        return {'FINISHED'}
########################################

########################################
#gMirror
########################################
class FUJIWARATOOLBOX_681921(bpy.types.Operator):#gMirror
    """グループ化してミラーにする"""
    bl_idname = "fujiwara_toolbox.command_681921"
    bl_label = "gMirror"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        import random
        groupname = "Group" + str(random.randrange(0,9999999999))
        bpy.ops.group.create(name=groupname)
        glayers = bpy.context.scene.objects.active.layers
        bpy.ops.object.group_instance_add(group=groupname, view_align=False, location=(0, 0, 0), layers=glayers)
        bpy.context.scene.objects.active.scale[0] = -1
        for obj in bpy.context.selected_objects:
            obj.select = False
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("オブジェクトモード")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#重複頂点を削除（選択物）
########################################
class FUJIWARATOOLBOX_559336(bpy.types.Operator):#重複頂点を削除（選択物）
    """重複頂点を削除（選択物）"""
    bl_idname = "fujiwara_toolbox.command_559336"
    bl_label = "重複頂点を削除（選択物）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            fjw.activate(obj)
            meshu = fjw.MeshUtils(obj)
            meshu.selectall()
            meshu.remove_doubles()
        fjw.mode("OBJECT")
        return {'FINISHED'}
########################################





#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






################################################################################
#UIカテゴリ
########################################
#トランスフォーム
########################################
class CATEGORYBUTTON_561346(bpy.types.Operator):#トランスフォーム
    """トランスフォーム"""
    bl_idname = "fujiwara_toolbox.categorybutton_561346"
    bl_label = "トランスフォーム"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("トランスフォーム",True)
    uiitem.button(bl_idname,bl_label,icon="MANIPUL",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





########################################
#面に回転をあわせる
########################################
class FUJIWARATOOLBOX_272822(bpy.types.Operator):#面に回転をあわせる
    """面に回転をあわせる"""
    bl_idname = "fujiwara_toolbox.command_272822"
    bl_label = "rRMB 面に回転をあわせる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SNAP_FACE",mode="edit")


    
    def execute(self, context):
        bpy.ops.object.ralign_orientation_to_selection()
#        bpy.ops.transform.create_orientation()
#        bpy.ops.object.editmode_toggle()
#        bpy.context.space_data.transform_orientation = 'Face'
#        bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), axis=(0,
#        0, 0), constraint_axis=(False, False, False),
#        constraint_orientation='Face', mirror=False, proportional='DISABLED',
#        proportional_edit_falloff='SMOOTH', proportional_size=1)
#        bpy.ops.object.transform_apply(location=False, rotation=True,
#        scale=True)
#        bpy.ops.transform.delete_orientation()
         
         
         
         
        return {'FINISHED'}
########################################

#########################################
##角度をきっちり
#########################################
#class FUJIWARATOOLBOX_908924(bpy.types.Operator):#角度をきっちり
#    """角度をきっちり"""
#    bl_idname = "fujiwara_toolbox.command_908924"
#    bl_label = "角度をきっちり"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
####    def execute(self, context):
#        rmode = bpy.context.object.rotation_mode
#        bpy.context.object.rotation_mode = 'XYZ'
#        obj = bpy.context.scene.objects.active
#        for n in range(0,3):
#            angle = math.degrees(obj.rotation_euler[n] )
#            if angle != 0:
#                if angle > 0:
#                    angle = angle - angle%90
#                else:
#                    angle = angle + angle%90
#            obj.rotation_euler[n] = math.radians(angle)
#
#        bpy.context.object.rotation_mode = rmode
#
#
#
#        return {'FINISHED'}
#########################################


############################################################################################################################
uiitem("複製反転")
############################################################################################################################

########################################
#ミラーリング
########################################
class FUJIWARATOOLBOX_698300(bpy.types.Operator):#ミラーリング
    """ミラーリング"""
    bl_idname = "fujiwara_toolbox.command_698300"
    bl_label = "ミラーリング"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = fjw.get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])
        use_pivot_point_align = bpy.context.space_data.use_pivot_point_align

        bpy.context.space_data.cursor_location = (0,0,0)
        bpy.context.space_data.pivot_point = 'CURSOR'

        #位置を反転→各オブジェクトごとにやらないと全体にかかる！
        #個別でやると今度は親子問題
        #bpy.context.space_data.use_pivot_point_align = True
        #for obj in selection:
        #    deselect()
        #    activate(obj)
        #    bpy.ops.transform.resize(value=(-1, -1, -1),
        #    constraint_axis=(True, False, False),
        #    constraint_orientation='GLOBAL', mirror=False,
        #    proportional='DISABLED', proportional_edit_falloff='SMOOTH',
        #    proportional_size=1, release_confirm=True)
        #原点は3Dカーソル使って移動する！！

        #各オブジェクトを編集モードで反転
        #編集リスト
        editable = ["MESH","ARMATURE","CURVE"]

        for obj in selection:
            if obj.type in editable:
                fjw.deselect()
                fjw.activate(obj)
                obj.active_shape_key_index = 0

                #bpy.ops.view3d.snap_cursor_to_selected()
                fjw.mode("EDIT")
                
                #select_allがタイプによって違う
                if obj.type == "MESH":
                    bpy.ops.mesh.select_all(action="SELECT")
                if obj.type == "ARMATURE":
                    bpy.ops.armature.select_all(action="SELECT")
                if obj.type == "CURVE":
                    bpy.ops.curve.select_all(action="SELECT")

                #反転
                bpy.ops.transform.resize(value=(-1, -1, -1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
                #法線反転
                if obj.type == "MESH":
                    bpy.ops.mesh.flip_normals()
                fjw.mode("OBJECT")

        #原点処理
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            bpy.ops.view3d.snap_cursor_to_selected()
            c = bpy.context.space_data.cursor_location
            bpy.context.space_data.cursor_location = (c[0] * -1,c[1],c[2])
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')



        fjw.select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        bpy.context.space_data.use_pivot_point_align = use_pivot_point_align



        #bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        #selection = get_selected_list()

        #current_pivot_point = bpy.context.space_data.pivot_point
        #current_cursor =
        #(bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])
        #use_pivot_point_align = bpy.context.space_data.use_pivot_point_align

        #bpy.context.space_data.cursor_location = (0,0,0)
        #bpy.context.space_data.pivot_point = 'CURSOR'

        ##位置を反転
        #bpy.context.space_data.use_pivot_point_align = True
        #bpy.ops.transform.resize(value=(-1, -1, -1), constraint_axis=(True,
        #False, False), constraint_orientation='GLOBAL', mirror=False,
        #proportional='DISABLED', proportional_edit_falloff='SMOOTH',
        #proportional_size=1, release_confirm=True)

        ##各オブジェクトを編集モードで反転
        ##編集リスト
        #editable = ["MESH","ARMATURE","CURVE"]

        #for obj in selection:
        #    if obj.type in editable:
        #        deselect()
        #        activate(obj)
        #        bpy.ops.view3d.snap_cursor_to_selected()
        #        mode("EDIT")
                
        #        #select_allがタイプによって違う
        #        if obj.type == "MESH":
        #            bpy.ops.mesh.select_all(action="SELECT")
        #        if obj.type == "ARMATURE":
        #            bpy.ops.armature.select_all(action="SELECT")
        #        if obj.type == "CURVE":
        #            bpy.ops.curve.select_all(action="SELECT")

        #        #反転
        #        bpy.ops.transform.resize(value=(-1, -1, -1),
        #        constraint_axis=(True, False, False),
        #        constraint_orientation='GLOBAL', mirror=False,
        #        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
        #        proportional_size=1, release_confirm=True)
        #        mode("OBJECT")
        #select(selection)

        ##ピボット戻す
        #bpy.context.space_data.pivot_point = current_pivot_point
        #bpy.context.space_data.cursor_location = current_cursor
        #bpy.context.space_data.use_pivot_point_align = use_pivot_point_align
        
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#グローバル X
########################################
class FUJIWARATOOLBOX_83454(bpy.types.Operator):#global X
    """グローバル X"""
    bl_idname = "fujiwara_toolbox.command_83454"
    bl_label = "global X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = fjw.get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = fjw.active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        fjw.deselect()
        fjw.select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.select(roots)
        fjw.activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[0] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.deselect()
        fjw.delete([empty])

        fjw.select(selection)


        #bpy.context.space_data.pivot_point = 'CURSOR'
        #bpy.context.space_data.cursor_location = (0,0,0)
        #bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        #bpy.ops.transform.resize(value=(-1, 1, 1), constraint_axis=(True,
        #False, False), constraint_orientation='GLOBAL', mirror=False,
        #proportional='DISABLED', proportional_edit_falloff='SMOOTH',
        #proportional_size=1, release_confirm=True)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#カーソル X
########################################
class FUJIWARATOOLBOX_334794(bpy.types.Operator):#カーソル X
    """カーソル X"""
    bl_idname = "fujiwara_toolbox.command_334794"
    bl_label = "カーソル X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = fjw.get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        #bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = fjw.active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        fjw.deselect()
        fjw.select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.select(roots)
        fjw.activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[0] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.deselect()
        fjw.delete([empty])

        fjw.select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################


########################################
#Y
########################################
class FUJIWARATOOLBOX_168959(bpy.types.Operator):#Y
    """Y"""
    bl_idname = "fujiwara_toolbox.command_168959"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = fjw.get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        #bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = fjw.active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        fjw.deselect()
        fjw.select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.select(roots)
        fjw.activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[1] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.deselect()
        fjw.delete([empty])

        fjw.select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################



########################################
#Z
########################################
class FUJIWARATOOLBOX_68739(bpy.types.Operator):#Z
    """Z"""
    bl_idname = "fujiwara_toolbox.command_68739"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        selection = fjw.get_selected_list()

        current_pivot_point = bpy.context.space_data.pivot_point
        current_cursor = (bpy.context.space_data.cursor_location[0],bpy.context.space_data.cursor_location[1],bpy.context.space_data.cursor_location[2])

        #bpy.context.space_data.cursor_location = (0,0,0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=bpy.context.space_data.cursor_location, layers=[True for i in range(20)])
        empty = fjw.active()


        #一回Emptyにペアレントして*-1、でトランスフォーム維持して解除
        #選択の中でのRootなオブジェクトを探す
        roots = []


        for obj in selection:
            #選択の中に親がいなければ暫定ルート。
            if obj.parent == None or obj.parent not in selection:
                roots.append(obj)

        fjw.deselect()
        fjw.select(roots)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.select(roots)
        fjw.activate(empty)
        empty.select = True
        #ペアレント
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #スケール-1
        empty.scale[2] = -1

        #親子解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        fjw.deselect()
        fjw.delete([empty])

        fjw.select(selection)

        #ピボット戻す
        bpy.context.space_data.pivot_point = current_pivot_point        
        bpy.context.space_data.cursor_location = current_cursor
        
        return {'FINISHED'}
########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("ランダム化")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#位置X
########################################
#bpy.ops.fujiwara_toolbox.randomize_loc_x() #位置X
class FUJIWARATOOLBOX_RANDOMIZE_LOC_X_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_loc_x_obj"
    bl_label = "位置X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        # bpy.ops.object.randomize_transform(loc=(0.06, 0, 0), rot=(0.00261799, 0, 0), scale_even=True, scale=(1.06, 1, 1))
        rnd = random.random()*10000
        value=1
        bpy.ops.object.randomize_transform(random_seed=rnd,loc=(value,0,0))
        return {'FINISHED'}
########################################

########################################
#Y
########################################
#bpy.ops.fujiwara_toolbox.randomize_loc_y() #Y
class FUJIWARATOOLBOX_RANDOMIZE_LOC_Y_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_loc_y_obj"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1
        bpy.ops.object.randomize_transform(random_seed=rnd,loc=(0,value,0))
        return {'FINISHED'}
########################################

########################################
#Z
########################################
#bpy.ops.fujiwara_toolbox.randomize_loc_z() #Z
class FUJIWARATOOLBOX_RANDOMIZE_LOC_Z_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_loc_z_obj"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1
        bpy.ops.object.randomize_transform(random_seed=rnd,loc=(0,0,value))
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#回転X
########################################
#bpy.ops.fujiwara_toolbox.randomize_rot_x() #回転X
class FUJIWARATOOLBOX_RANDOMIZE_ROT_X_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_rot_x_obj"
    bl_label = "回転X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=3.14159
        bpy.ops.object.randomize_transform(random_seed=rnd,rot=(value,0,0))
        return {'FINISHED'}
########################################

########################################
#Y
########################################
#bpy.ops.fujiwara_toolbox.randomize_rot_y() #Y
class FUJIWARATOOLBOX_RANDOMIZE_ROT_Y_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_rot_y_obj"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=3.14159
        bpy.ops.object.randomize_transform(random_seed=rnd,rot=(0,value,0))
        return {'FINISHED'}
########################################

########################################
#Z
########################################
#bpy.ops.fujiwara_toolbox.randomize_rot_z() #Z
class FUJIWARATOOLBOX_RANDOMIZE_ROT_Z_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_rot_z_obj"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=3.14159
        bpy.ops.object.randomize_transform(random_seed=rnd,rot=(0,0,value))
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#拡縮X
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_x() #拡縮X
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_X_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_x_obj"
    bl_label = "拡縮X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(value,0,0))
        return {'FINISHED'}
########################################

########################################
#Y
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_y() #Y
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_Y_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_y_obj"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(0,value,0))
        return {'FINISHED'}
########################################

########################################
#Z
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_z() #Z
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_Z_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_z_obj"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(0,0,value))
        return {'FINISHED'}
########################################

########################################
#全て
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_all() #全て
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_ALL_obj(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_all_obj"
    bl_label = "全て"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(value,value,value),scale_even=True)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------













#
#############################################################################################################################
##ドラフト
#############################################################################################################################
#########################################
##アウトプット
#########################################
#class FUJIWARATOOLBOX_879787(bpy.types.Operator):#アウトプット
#    """アウトプット"""
#    bl_idname = "fujiwara_toolbox.command_879787"
#    bl_label = "アウトプット"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("ドラフト");
#
#
####    def execute(self, context):
#        #http://python.civic-apps.com/date-format/
#        #bpy.context.scene.render.use_simplify = True
#        #bpy.context.scene.render.simplify_subdivision = 1
#        now = datetime.datetime.now()
#        nowstr = now.strftime("%Y%m%d%H%M%S")
#
#        bpy.ops.wm.save_mainfile(filepath="g:\\tmp\\log\\"+nowstr+".blend")
#        bpy.context.scene.render.resolution_percentage = 10
#        bpy.context.space_data.show_only_render = True
#        bpy.data.scenes["Scene"].render.filepath = "g:\\tmp\\tmp.png"
#        bpy.ops.render.opengl(animation=False, sequencer=False,
#        write_still=True, view_context=True)
#        bpy.data.scenes["Scene"].render.filepath =
#        "g:\\tmp\\log\\"+nowstr+".png"
#        bpy.ops.render.opengl(animation=False, sequencer=False,
#        write_still=True, view_context=True)
#        bpy.context.space_data.show_only_render = False
#        bpy.context.scene.render.resolution_percentage = 100
#        """
#        #そうだ！！GLレンダ！！！！
#        bpy.ops.wm.save_mainfile(filepath="c:\\tmp\\log\\"+nowstr+".blend")
#        bpy.context.scene.render.resolution_percentage = 10
#        bpy.context.scene.render.use_shadows = False
#        bpy.context.scene.render.use_raytrace = False
#        bpy.context.scene.render.use_textures = True
#        bpy.context.scene.render.use_antialiasing = False
#        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#        bpy.context.scene.render.use_freestyle = False
#        bpy.context.scene.render.use_edge_enhance = False
#        bpy.context.scene.render.edge_threshold = 255
#        bpy.data.scenes["Scene"].render.filepath = "c:\\tmp\\tmp.png"
#        bpy.ops.render.render(write_still=True)
##        bpy.data.scenes["Scene"].render.filepath =
##        "c:\\tmp\\log\\"+nowstr+".png"
##        bpy.ops.render.render(write_still=True)
#        """
#
#
#        return {'FINISHED'}
#########################################
#
#
#
#
#
#
#
#
#
#
#
#############################################################################################################################
##オリエンテーション
#############################################################################################################################
#########################################
##グローバル
#########################################
#class FUJIWARATOOLBOX_538468(bpy.types.Operator):#グローバル
#    """グローバル"""
#    bl_idname = "fujiwara_toolbox.command_538468"
#    bl_label = "グローバル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("オリエンテーション");
#
#
####    def execute(self, context):
#        bpy.context.space_data.transform_orientation = 'GLOBAL'
#
#        return {'FINISHED'}
#########################################
#
#########################################
##ローカル
#########################################
#class FUJIWARATOOLBOX_550536(bpy.types.Operator):#ローカル
#    """Sample Operator"""
#    bl_idname = "fujiwara_toolbox.command_550536"
#    bl_label = "ローカル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
####    def execute(self, context):
#        bpy.context.space_data.transform_orientation = 'LOCAL'
#
#        return {'FINISHED'}
#########################################
#
#########################################
##ノーマル
#########################################
#class FUJIWARATOOLBOX_265618(bpy.types.Operator):#ノーマル
#    """ノーマル"""
#    bl_idname = "fujiwara_toolbox.command_265618"
#    bl_label = "ノーマル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
####    def execute(self, context):
#        bpy.context.space_data.transform_orientation = 'NORMAL'
#
#        return {'FINISHED'}
#########################################


























#
#############################################################################################################################
##シーン
#############################################################################################################################
#########################################
##表示シーンを揃える
#########################################
#class FUJIWARATOOLBOX_708885(bpy.types.Operator):#表示シーンを揃える
#    """表示シーンを揃える"""
#    bl_idname = "fujiwara_toolbox.command_708885"
#    bl_label = "表示シーンを揃える"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("シーン");
#
#
####    def execute(self, context):
#        scene = bpy.context.scene
#        for screen in bpy.data.screens:
#            screen.scene = scene
#        return {'FINISHED'}
#########################################
#




































#
#
#
#############################################################################################################################
##スナップ
#############################################################################################################################
#
#########################################
##選択→3Dカーソル
#########################################
#class FUJIWARATOOLBOX_553638(bpy.types.Operator):#選択→3Dカーソル
#    """選択→3Dカーソル"""
#    bl_idname = "fujiwara_toolbox.command_553638"
#    bl_label = "選択→3Dカーソル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("スナップ");
#
#
####    def execute(self, context):
#        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
#
#        return {'FINISHED'}
#########################################
#
#
#########################################
##3Dカーソル→選択
#########################################
#class FUJIWARATOOLBOX_670764(bpy.types.Operator):#3Dカーソル→選択
#    """3Dカーソル→選択"""
#    bl_idname = "fujiwara_toolbox.command_670764"
#    bl_label = "3Dカーソル→選択"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
####    def execute(self, context):
#        bpy.ops.view3d.snap_cursor_to_selected()
#
#        return {'FINISHED'}
#########################################
#

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------















































################################################################################
#UIカテゴリ
########################################
#ペアレント
########################################
class CATEGORYBUTTON_445538(bpy.types.Operator):#ペアレント
    """ペアレント"""
    bl_idname = "fujiwara_toolbox.categorybutton_445538"
    bl_label = "ペアレント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("ペアレント",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#オブジェクト
########################################
class FUJIWARATOOLBOX_227300(bpy.types.Operator):#オブジェクト
    """オブジェクト"""
    bl_idname = "fujiwara_toolbox.command_227300"
    bl_label = "オブジェクト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################

########################################
#オブジェクト（Trans維持）
########################################
class FUJIWARATOOLBOX_413331(bpy.types.Operator):#オブジェクト（Trans維持）
    """オブジェクト（Trans維持）"""
    bl_idname = "fujiwara_toolbox.command_413331"
    bl_label = "Trans維持"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#ボーン相対
########################################
class FUJIWARATOOLBOX_454489(bpy.types.Operator):#ボーン相対
    """ボーン相対"""
    bl_idname = "fujiwara_toolbox.command_454489"
    bl_label = "ボーン相対"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="BONE_DATA",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='BONE_RELATIVE')
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################

########################################
#ボーン相対→隠す
########################################
class FUJIWARATOOLBOX_182276(bpy.types.Operator):#ボーン相対→隠す
    """ボーン相対→隠す"""
    bl_idname = "fujiwara_toolbox.command_182276"
    bl_label = "→隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='BONE_RELATIVE')
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH":
                obj.select = False
        bpy.ops.object.hide_view_set(unselected=False)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------




########################################
#自動のウェイトで
########################################
class FUJIWARATOOLBOX_214836(bpy.types.Operator):#自動のウェイトで
    """自動のウェイトで"""
    bl_idname = "fujiwara_toolbox.command_214836"
    bl_label = "自動のウェイトで"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        #アーマチュアを一番上にもってく
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                modslen = len(obj.modifiers)
                mod = obj.modifiers[modslen - 1]
                if mod.type == "ARMATURE":
                    for n in range(0,modslen):
                        bpy.ops.object.modifier_move_up(modifier=mod.name)
                    #mirrorはアーマチュアより上に。
                for mod in obj.modifiers:
                    if mod.type == "MIRROR":
                        for n in range(0,modslen):
                            bpy.ops.object.modifier_move_up(modifier=mod.   name)
        
        
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        return {'FINISHED'}
########################################


########################################
#自動のウェイトで→隠す
########################################
class FUJIWARATOOLBOX_214836a(bpy.types.Operator):#自動のウェイトで→隠す
    """自動のウェイトで→隠す"""
    bl_idname = "fujiwara_toolbox.command_214836a"
    bl_label = "→隠す"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="RESTRICT_VIEW_ON",mode="")

    def execute(self, context):
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH":
                obj.select = False
        bpy.ops.object.hide_view_set(unselected=False)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------







########################################
#クリア
########################################
class FUJIWARATOOLBOX_307216(bpy.types.Operator):#クリア
    """クリア"""
    bl_idname = "fujiwara_toolbox.command_307216"
    bl_label = "クリア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_LAMP",mode="")

    def execute(self, context):
        bpy.ops.object.parent_clear(type='CLEAR')
        
        return {'FINISHED'}
########################################

########################################
#クリア（Trans維持）
########################################
class FUJIWARATOOLBOX_855470(bpy.types.Operator):#クリア（Trans維持）
    """クリア（Trans維持）"""
    bl_idname = "fujiwara_toolbox.command_855470"
    bl_label = "Trans維持"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_DATA_LAMP",mode="")
    
    def execute(self, context):
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#
#
#############################################################################################################################
##トランスフォーム
#############################################################################################################################
#########################################
##X位置 0
#########################################
#class FUJIWARATOOLBOX_562777(bpy.types.Operator):#X位置 0
#    """トランスフォーム"""
#    bl_idname = "fujiwara_toolbox.command_562777"
#    bl_label = "X位置 0"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("トランスフォーム");
#
#
####    def execute(self, context):
#        obj = bpy.context.scene.objects.active
#        obj.location[0] = 0
#
#        return {'FINISHED'}
#########################################
#
#
#
#
#
#
#########################################
##回転X 90
#########################################
#class FUJIWARATOOLBOX_487092(bpy.types.Operator):#回転X 90
#    """回転X 90"""
#    bl_idname = "fujiwara_toolbox.command_487092"
#    bl_label = "回転X 90"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
####    def execute(self, context):
#        obj = bpy.context.scene.objects.active
#        obj.rotation_euler[0] = 1.5708
#
#        return {'FINISHED'}
#########################################
#
#
#
#
#########################################
##-X位置コピー
#########################################
#class FUJIWARATOOLBOX_589282(bpy.types.Operator):#-X位置コピー
#    """-X位置コピー"""
#    bl_idname = "fujiwara_toolbox.command_589282"
#    bl_label = "-X位置コピー"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
####    def execute(self, context):
#        source = bpy.context.selected_objects[0]
#        target = bpy.context.scene.objects.active
#        target.location[0] = source.location[0] * -1
#        target.location[1] = source.location[1]
#        target.location[2] = source.location[2]
#
#        return {'FINISHED'}
#########################################









#対象のレイヤーをセット
def setlayer(l):
    bpy.context.scene.layers[l] = True
    for obj in bpy.context.selected_objects:
        obj.layers[l] = True
        for layer_n in range(0,19):
            if(layer_n != l):
                obj.layers[layer_n] = False
    
    refreshlayer()
    
    return



#オブジェクトのないレイヤーを非表示にする
def refreshlayer():
    layers = [False] * 20
    
    #現在非表示なものは表示しない、準備
    current_layers = [False] * 20
    for l in range(0,20):
        current_layers[l] = bpy.context.scene.layers[l]
    
    for obj in bpy.data.objects:
        for l in range(0,19):
            if(obj.layers[l]):
                layers[l] = True
    
    
    #現在非表示なものを非表示に
    for l in range(0,19):
        if(current_layers[l] == False):
            layers[l] = False
    
    bpy.context.scene.layers = layers
    
    return






























































#
#
#
#############################################################################################################################
##レンダー設定
#############################################################################################################################
#########################################
##プレビュー
#########################################
#class FUJIWARATOOLBOX_913578(bpy.types.Operator):#プレビュー
#    """プレビュー"""
#    bl_idname = "fujiwara_toolbox.command_913578"
#    bl_label = "プレビュー"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("レンダー設定");
#
#
####    def execute(self, context):
#        bpy.context.scene.render.resolution_percentage = 10
#        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = True
#        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#        bpy.context.scene.render.use_textures = True
#        bpy.context.scene.render.use_shadows = True
#
#        return {'FINISHED'}
#########################################
#
#########################################
##フル
#########################################
#class FUJIWARATOOLBOX_852389(bpy.types.Operator):#フル
#    """フル"""
#    bl_idname = "fujiwara_toolbox.command_852389"
#    bl_label = "フル"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#
#
####    def execute(self, context):
#        bpy.context.scene.render.resolution_percentage = 100
#        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
#        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = True
#        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
#        bpy.context.scene.render.use_textures = True
#        bpy.context.scene.render.use_shadows = True
#
#        return {'FINISHED'}
#########################################






################################################################################
#UIカテゴリ
########################################
#アーマチュア
########################################
class CATEGORYBUTTON_446957(bpy.types.Operator):#アーマチュア
    """アーマチュア"""
    bl_idname = "fujiwara_toolbox.categorybutton_446957"
    bl_label = "アーマチュア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("アーマチュア",True)
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#スケール継承解除（選択ボーン）
########################################
class FUJIWARATOOLBOX_84927(bpy.types.Operator):#スケール継承解除（選択ボーン）
    """スケール継承解除（選択ボーン）"""
    bl_idname = "fujiwara_toolbox.command_84927"
    bl_label = "スケール継承解除（選択ボーン）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        bpy.context.object.data.draw_type = 'STICK'
        
        #スケール継承の解除
        for bone in bpy.context.object.data.bones:
            if(bone.select == True):
                bone.use_inherit_scale = False
        
        
        
        return {'FINISHED'}
########################################

########################################
#スケール継承有効（選択ボーン）
########################################
class FUJIWARATOOLBOX_516332(bpy.types.Operator):#スケール継承有効（選択ボーン）
    """スケール継承有効（選択ボーン）"""
    bl_idname = "fujiwara_toolbox.command_516332"
    bl_label = "スケール継承有効（選択ボーン）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        bpy.context.object.data.draw_type = 'STICK'
        
        #スケール継承の解除
        for bone in bpy.context.object.data.bones:
            if(bone.select == True):
                bone.use_inherit_scale = True
        
        
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#＜●＞コンストレイント
########################################
class FUJIWARATOOLBOX_618823(bpy.types.Operator):#＜●＞コンストレイント
    """＜●＞コンストレイント"""
    bl_idname = "fujiwara_toolbox.command_618823"
    bl_label = "コンストレイント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VISIBLE_IPO_ON",mode="")

    def execute(self, context):
        for bone in bpy.context.object.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                        constraint.mute = False
        
        return {'FINISHED'}
########################################

########################################
#＜＿＞コンストレイント
########################################
class FUJIWARATOOLBOX_898623(bpy.types.Operator):#＜＿＞コンストレイント
    """＜＿＞コンストレイント"""
    bl_idname = "fujiwara_toolbox.command_898623"
    bl_label = "コンストレイント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="VISIBLE_IPO_OFF",mode="")

    def execute(self, context):
        for bone in bpy.context.object.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                        constraint.mute = True
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#アーマチュアからスキンを作成
########################################
class FUJIWARATOOLBOX_742340(bpy.types.Operator):#アーマチュアからスキンを作成
    """アーマチュアからスキンを作成"""
    bl_idname = "fujiwara_toolbox.command_742340"
    bl_label = "アーマチュアからスキンを作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください")
            return {'CANCELLED'}

        armature_org = fjw.active()

        #############
        #アーマチュアからメッシュを生成
        #############

        #トランスフォームを反映するために複製して親子解除する
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        armature = fjw.active()
        bonedata = {}

        fjw.mode("POSE")

        #ポーズからとるとやっぱよくなかった。デフォルトから取るべき。
        armature.data.pose_position = 'REST'
        bones = armature.pose.bones
        #bones = armature.data.bones
        for bone in bones:
            bonedata[bone.name] = {"name":bone.name, "head":bone.head, "tail":bone.tail}

        fjw.mode("OBJECT")


        bpy.ops.object.add(type='MESH')
        obj = ob = bpy.context.object
        mesh = obj.data
        
        obj.location = armature.location
        obj.rotation_euler = armature.rotation_euler
        obj.scale = armature.scale

        #頂点・辺の生成
        for bname in bonedata:
            bdata = bonedata[bname]

            mesh.vertices.add(count=1)
            v0 = len(mesh.vertices) - 1
            v = mesh.vertices[v0]
            v.co = bdata["head"]

            mesh.vertices.add(count=1)
            v1 = len(mesh.vertices) - 1
            v = mesh.vertices[v1]
            v.co = bdata["tail"]

            mesh.edges.add(count=1)
            e = mesh.edges[len(mesh.edges) - 1]
            #辺の頂点指定は頂点のインデックス番号。
            e.vertices[0] = v0
            e.vertices[1] = v1

        #重複頂点を削除
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        #5mm
        bpy.ops.mesh.remove_doubles(threshold=0.005)
        fjw.mode("OBJECT")


        #複製したアーマチュアを削除
        fjw.delete([armature])

        fjw.deselect()
        fjw.activate(obj)
        obj.select = True

        #元アーマチュアにくくりつけておく
        fjw.activate(armature_org)
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')


        #スキン
        fjw.activate(obj)
        bpy.ops.object.modifier_add(type='SKIN')
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        skinsize = 0.03
        bpy.ops.transform.skin_resize(value=(skinsize, skinsize, skinsize), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.object.skin_root_mark()

        bpy.context.object.modifiers["Armature"].show_in_editmode = True

        obj.hide_render = True

        bpy.ops.object.modifier_add(type='SUBSURF')


        return {'FINISHED'}
########################################


########################################
#選択ボーン以外のウェイトを削除
########################################
class FUJIWARATOOLBOX_166889(bpy.types.Operator):#選択ボーン以外のウェイトを削除
    """選択ボーン以外のウェイトを削除"""
    bl_idname = "fujiwara_toolbox.command_166889"
    bl_label = "選択ボーン以外のウェイトを削除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):

        tmp = fjw.get_selected_list("ARMATURE")
        if tmp.count == 0:
            return {'CANCELLED'}
        armatures = tmp

        tmp = fjw.get_selected_list("MESH")
        if tmp.count == 0:
            return {'CANCELLED'}
        meshes = tmp

        #選択されているボーンのリストを取得する
        
        armature_data = {}
        for arm in armatures:
            data = {}
            fjw.activate(arm)
            fjw.mode("POSE")
            for posebone in arm.pose.bones:
                data[posebone.bone.name] = posebone.bone.select
            armature_data[arm.name] = data

        #http://blender.stackexchange.com/questions/24170/vertex-groups-and-bone-weights-programmatically
        #http://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-from-python
        for mesh in meshes:

            #ウェイト割当で使うインデックスのリストを作成
            #今回はどれも全割当なのではじめにつくっとく
            vxIdList = []
            for idx, val in enumerate(mesh.data.vertices):
                vxIdList.append(idx)


            for armdata_name in armature_data:
                for vg in mesh.vertex_groups:
                    armdata = armature_data[armdata_name]
                    if vg.name in armdata:
                        if armdata[vg.name] == False:
                            #非選択ボーンなのでウェイトをゼロにする
                            vg.add(vxIdList, 0, "REPLACE")

        
        return {'FINISHED'}
########################################

########################################
#ウェイトボーン相対
########################################
class FUJIWARATOOLBOX_273078(bpy.types.Operator):#ウェイトボーン相対
    """ウェイトボーン相対"""
    bl_idname = "fujiwara_toolbox.command_273078"
    bl_label = "ウェイトボーン相対"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        #からのグループで割当
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.parent_set(type='ARMATURE_NAME')


        tmp = fjw.get_selected_list("ARMATURE")
        if tmp.count == 0:
            return {'CANCELLED'}
        armatures = tmp

        tmp = fjw.get_selected_list("MESH")
        if tmp.count == 0:
            return {'CANCELLED'}
        meshes = tmp

        #選択されているボーンのリストを取得する
        
        armature_data = {}
        for arm in armatures:
            data = {}
            fjw.activate(arm)
            fjw.mode("POSE")

            #アクティブ以外のウェイトとかいらないから他を非選択に
            activeposebone = arm.data.bones.active
            for posebone in arm.pose.bones:
                posebone.bone.select = False
            activeposebone.select = True

            for posebone in arm.pose.bones:
                data[posebone.bone.name] = posebone.bone.select
            armature_data[arm.name] = data

        #http://blender.stackexchange.com/questions/24170/vertex-groups-and-bone-weights-programmatically
        #http://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-from-python
        for mesh in meshes:

            #ウェイト割当で使うインデックスのリストを作成
            #今回はどれも全割当なのではじめにつくっとく
            vxIdList = []
            for idx, val in enumerate(mesh.data.vertices):
                vxIdList.append(idx)


            for armdata_name in armature_data:
                for vg in mesh.vertex_groups:
                    armdata = armature_data[armdata_name]
                    if vg.name in armdata:
                        if armdata[vg.name] == False:
                            #非選択ボーンなのでウェイトをゼロにする
                            vg.add(vxIdList, 0, "REPLACE")
                        else:
                            #選択ボーンはウェイト1
                            vg.add(vxIdList, 1, "REPLACE")
        
        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("プロポーションエディット")
############################################################################################################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#準備
########################################
class FUJIWARATOOLBOX_964581(bpy.types.Operator):#準備
    """準備"""
    bl_idname = "fujiwara_toolbox.command_964581"
    bl_label = "準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        ######################################################
        #準備
        ######################################################
        """
        ・コンストレイントの非表示
        ・全ボーンローテーション初期化→なしで
        """
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        for bone in bpy.context.object.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                    constraint.mute = True
        
        
        bpy.ops.pose.select_all(action='SELECT')
        #bpy.ops.pose.rot_clear()
        bpy.context.space_data.transform_orientation = 'LOCAL'
        
        #空移動でアップデート
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}
########################################



#########################################
##ポーズミラーリング
#########################################
class FUJIWARATOOLBOX_314879(bpy.types.Operator):#ポーズミラーリング
    """選択ボーンのポーズをミラーリング"""
    bl_idname = "fujiwara_toolbox.command_314879"
    bl_label = "ポーズミラーリング"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.pose.copy()
        bpy.ops.pose.paste(flipped=True)

        return {'FINISHED'}
#########################################


def update_armaturesystem(self, context, mute_consraints):
    """
    シングルなアーマチュアとオブジェクトのペアではこれでよい、が、
    複数くくりつけてあるものをどうするかが問題。
    →childrenの中で、Armatureがついてる奴ピックアップすればいい！
    """
    #アーマチュアを選択して、あとは自動でやる
    if fjw.active().type != "ARMATURE":
        return


    armature = fjw.active()
    fjw.mode("OBJECT")
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    childrenall = fjw.get_selected_list()
    fjw.deselect()
    fjw.activate(armature)

    #ポーズが左右対称でない場合警告を出して終了する
    armu = fjw.ArmatureUtils(armature)
    for pbone in armu.pose_bones:
        if "_L" in pbone.name:
            lbone = pbone
            rname = pbone.name.replace("_L", "_R")
            if rname in armu.pose_bones:
                rbone = armu.pose_bones[rname]
                #微妙に誤差が出ることがあるので丸める
                if round(rbone.head.x*100) != round((lbone.head.x * -1)*100):
                    self.report({"INFO"}, "ボーンが左右非対称です。 %s, %s"%(rbone.name, lbone.name))
                    return



    #コンストレイントを無効にする
    fjw.activate(armature)
    fjw.mode("POSE")
    bpy.ops.pose.select_all(action='SELECT')
    if mute_consraints:
        for bone in armature.pose.bones:
            if(bpy.context.object.data.bones[bone.name].select == True):
                for constraint in bone.constraints:
                    constraint.mute = True

        
    fjw.mode("OBJECT")

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    fjw.deselect()


    targetobjects = []
    #アーマチュアmodがついている子をターゲットリストにいれる
    for obj in armature.children:
        if obj.type == "MESH":
            modu = fjw.Modutils(obj)
            arm = modu.find_bytype("ARMATURE")
            if arm != None:
                    targetobjects.append(obj)

    deformedobjects = []
    #!  armature.childrenの中にcageの子とか含まれてない！
    for obj in childrenall:
        fjw.activate(obj)
        #self.report({"INFO"},obj.name)
        modu = fjw.Modutils(obj)
        #アーマチュアついてないのでミラーとメッシュデフォーム適用する
        meshdeforms = modu.find_bytype_list("MESH_DEFORM")
        for mod in meshdeforms:
            self.report({"INFO"},obj.name + " has MeshDeform")
            #ミラー適用
            mrrs = modu.find_bytype_list("MIRROR")
            for mrr in mrrs:
                bpy.ops.object.modifier_apply(modifier=mrr.name)

            deformedobjects.append([obj, mod.object])
            bpy.ops.object.modifier_apply(modifier=mod.name)

    #deformedobjects = list(set(deformedobjects))

    #cages = []



    ##ターゲット群をペアレント解除する
    fjw.deselect()
    for obj in targetobjects:
        obj.hide = False
    fjw.select(targetobjects)
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    #for obj in targetobjects:
    #    bpy.context.scene.objects.active = obj
    #    obj.hide = False
    #    self.report({"INFO"},obj.name)
    #    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
    fjw.mode("OBJECT")

    mirrored_objects = []

    #オブジェクト側：mod適用
    for obj in targetobjects:
        fjw.activate(obj)
        modu = fjw.Modutils(obj)

        mrrs = modu.find_bytype_list("MIRROR")
        for mod in mrrs:
            mirrored_objects.append(obj)
            bpy.ops.object.modifier_remove(modifier=mod.name)

        arms = modu.find_bytype_list("ARMATURE")
        for mod in arms:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    #重複削除
    mirrored_objects = list(set(mirrored_objects))

    for obj in targetobjects:
        fjw.activate(obj)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        
    #アーマチュア側：デフォルトのポーズに適用
    fjw.activate(armature)
    fjw.mode("POSE")
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.armature_apply()
    fjw.mode("OBJECT")
    #OK
        
        
        
    #再リンク
    #全部選択解除
    fjw.deselect()
        
    #アーマチュアとオブジェクトを選択
    fjw.select(targetobjects)
    armature.select = True
        
    #アーマチュアをアクティブオブジェクトに
    fjw.activate(armature)
    #空のウェイトでペアレント
    bpy.ops.object.parent_set(type='ARMATURE_NAME', xmirror=False, keep_transform=False)
    #オブジェクト側：アーマチュアを一番上にもってく
    #しまった！mirrorはアーマチュアより上になきゃいけない！！

    #ミラーのつけなおし
    for obj in mirrored_objects:
        fjw.activate(obj)
        modu = fjw.Modutils(obj)
        mrr = modu.add("Mirror","MIRROR")
        mrr.mirror_object = armature

    #mod順整列
    for obj in targetobjects:
        modu = fjw.Modutils(obj)
        modu.sort()

        #activate(obj)
        #modu = Modutils(obj)

        #mods = modu.find_bytype_list("ARMATURE")
        #for mod in mods:
        #    modu.move_top(mod)
        #mods = modu.find_bytype_list("MIRROR")
        #for mod in mods:
        #    modu.move_top(mod)
    

    #コンストレイントを有効にする
    fjw.activate(armature)
    fjw.mode("POSE")
    bpy.ops.pose.select_all(action='SELECT')
    for bone in armature.pose.bones:
        if(armature.data.bones[bone.name].select == True):
            for constraint in bone.constraints:
                constraint.mute = False
    
    #メッシュデフォームのつけなおし
    for pair in deformedobjects:
        obj = pair[0]
        fjw.activate(obj)
        modu = fjw.Modutils(obj)
        mod = modu.add("MeshDeform","MESH_DEFORM")
        mod.object = pair[1]
        bpy.ops.object.meshdeform_bind(modifier=mod.name)
        modu.sort()


    #空移動でアップデート
    bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

########################################
#アップデート
########################################
class FUJIWARATOOLBOX_164873(bpy.types.Operator):#アップデート
    """アップデート"""
    bl_idname = "fujiwara_toolbox.command_164873"
    bl_label = "アップデート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        ######################################################
        #後処理
        ######################################################
        update_armaturesystem(self, context, True)

        return {'FINISHED'}
########################################

########################################
#アップデート(C有効)
########################################
class FUJIWARATOOLBOX_164873a(bpy.types.Operator):#アップデート(C有効)
    """アップデート(コンストレイント有効)"""
    bl_idname = "fujiwara_toolbox.command_164873a"
    bl_label = "アップデート(C有効)"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        ######################################################
        #後処理
        ######################################################
        update_armaturesystem(self, context, False)

        return {'FINISHED'}
########################################


#    def execute(self, context):
#        ######################################################
#        #後処理
#        ######################################################
        
#        """
#        シングルなアーマチュアとオブジェクトのペアではこれでよい、が、
#        複数くくりつけてあるものをどうするかが問題。
#        →childrenの中で、Armatureがついてる奴ピックアップすればいい！
#        """
#        #アーマチュアを選択して、あとは自動でやる
#        if bpy.context.scene.objects.active.type != "ARMATURE":
#            #self.report(type=‘WARNING’,message="アーマチュアを選択すること！")
#            return

#        armature = bpy.context.scene.objects.active


#        #コンストレイントを無効にする
#        bpy.context.scene.objects.active = armature
#        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.select_all(action='SELECT')
#        for bone in bpy.context.object.pose.bones:
#            if(bpy.context.object.data.bones[bone.name].select == True):
#                for constraint in bone.constraints:
#                    constraint.mute = True

        
#        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

#        bpy.ops.object.select_all(action='SELECT')
#        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True,
#        False, False), constraint_orientation='GLOBAL', mirror=False,
#        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
#        proportional_size=1, release_confirm=True)
#        bpy.ops.object.select_all(action='DESELECT')

#        targetobjects = []
#        #アーマチュアmodがついている子をターゲットリストにいれる
#        for obj in armature.children:
#            if obj.type == "MESH":
#                for mod in obj.modifiers:
#                    if mod.type == "ARMATURE":
#                        targetobjects.append(obj)
#                        break
        
#        #ターゲット群をペアレント解除する
#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            obj.hide = False
#            self.report({"INFO"},obj.name)
#            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
#        bpy.ops.object.mode_set(mode='OBJECT')

#        mirrored_objects = []

#        #オブジェクト側：アーマチュア適用
#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            for mod in obj.modifiers:
#                if mod.type == "MIRROR":
#                    #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
#                    #bpy.ops.object.modifier_apply(modifier=mod.name)
#                    mirrored_objects.append(obj)
#                    bpy.ops.object.modifier_remove(modifier=mod.name)
#                if mod.type == "ARMATURE":
#                    #適用する
#                    bpy.ops.object.modifier_apply(modifier=mod.name)
        
#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')


        
#        #アーマチュア側：デフォルトのポーズに適用
#        bpy.context.scene.objects.active = armature
#        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.select_all(action='SELECT')
#        bpy.ops.pose.armature_apply()
#        bpy.ops.object.mode_set(mode='OBJECT')
#        #OK
        
        
        
#        #再リンク
#        #全部選択解除
#        for obj in bpy.data.objects:
#            obj.select = False
        
        
#        #アーマチュアとオブジェクトを選択
#        armature.select = True
#        for obj in targetobjects:
#            obj.select = True
        
        
#        #アーマチュアをアクティブオブジェクトに
#        bpy.context.scene.objects.active = armature
#        #空のウェイトでペアレント
#        bpy.ops.object.parent_set(type='ARMATURE_NAME', xmirror=False,
#        keep_transform=False)
##        bpy.ops.object.parent_set(type='ARMATURE_AUTO', xmirror=False,
##        keep_transform=False)
#        #オブジェクト側：アーマチュアを一番上にもってく
#        #しまった！mirrorはアーマチュアより上になきゃいけない！！

#        #ミラーのつけなおし
#        for obj in mirrored_objects:
#            activate(obj)
#            bpy.ops.object.modifier_add(type='MIRROR')
#            mod = getnewmod(obj)
#            mod.mirror_object = armature

#        for obj in targetobjects:
#            bpy.context.scene.objects.active = obj
#            modslen = len(obj.modifiers)
#            mod = obj.modifiers[modslen - 1]
#            for n in range(0,modslen):
#                bpy.ops.object.modifier_move_up(modifier=mod.name)
#            #mirrorはアーマチュアより上に。
#            for mod in obj.modifiers:
#                if mod.type == "MIRROR":
#                    for n in range(0,modslen):
#                        bpy.ops.object.modifier_move_up(modifier=mod.name)
        
        
        
#        #コンストレイントを有効にする
#        bpy.context.scene.objects.active = armature
#        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.select_all(action='SELECT')
#        for bone in bpy.context.object.pose.bones:
#            if(bpy.context.object.data.bones[bone.name].select == True):
#                for constraint in bone.constraints:
#                    constraint.mute = False
        
#        #空移動でアップデート
#        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False,
#        False, False), constraint_orientation='LOCAL', mirror=False,
#        proportional='DISABLED', proportional_edit_falloff='SMOOTH',
#        proportional_size=1)

#        return {'FINISHED'}


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("ボーン生成")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#選択頂点からボーン生成
########################################
#bpy.ops.fjw.gen_bone_from_selected_vertices() #選択頂点からボーン生成
class FUJIWARATOOLBOX_gen_bone_from_selected_vertices(bpy.types.Operator):
    """アーマチュア→メッシュと選択してから実行。メッシュ内の選択頂点から、法線方向にボーンを生成する。"""
    bl_idname = "fujiwara_toolbox.gen_bone_from_selected_vertices"
    bl_label = "選択頂点からボーン生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        armature = None
        meshobj = None
        selection = fjw.get_selected_list()

        for obj in selection:
            if obj.type == "ARMATURE":
                armature = obj
            if obj.type == "MESH":
                meshobj = obj
        if armature is None:
            self.report({"INFO"},"ARMATUREを選択してください")
            return {'CANCELLED'}
        if meshobj is None:
            self.report({"INFO"},"MESHを選択してください")
            return {'CANCELLED'}

        meshu = fjw.MeshUtils(meshobj)
        fjw.mode("OBJECT")
        fjw.activate(armature)
        fjw.mode("EDIT")
        edit_bones = armature.data.edit_bones
        for v in meshu.vertices:
            if v.select:
                b = edit_bones.new("bonefromnormal")
                b.head = v.co
                b.tail = b.head + v.normal*0.1
                pass

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("アクションコンストレイント")
############################################################################################################################



########################################
#ワンタッチ生成
########################################
#bpy.ops.fjw.generate_action_constraint() #ワンタッチ生成
class FUJIWARATOOLBOX_generate_action_constraint(bpy.types.Operator):
    """現在のポーズからアクションコンストレイントを生成する。アクティブボーンのZscaleをターゲットとして設定する。"""
    bl_idname = "fujiwara_toolbox.generate_action_constraint"
    bl_label = "ワンタッチ生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "ARMATURE":
            self.report({"INFO"},"ARMATUREを選択してください")

        acu = fjw.ActionConstraintUtils(fjw.active())
        acu.auto_execute()

        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
"""
現在のポーズでポーズライブラリ作成
中割追加
アクティブなポーズライブラリでアクションコンストレイントを作成
"""
########################################
#PoseLib作成
########################################
#bpy.ops.fjw.make_poselib_with_current_pose() #PoseLib作成
class FUJIWARATOOLBOX_make_poselib_with_current_pose(bpy.types.Operator):
    """現在のポーズからアクションコンストレイント用のポーズライブラリを作成する。"""
    bl_idname = "fujiwara_toolbox.make_poselib_with_current_pose"
    bl_label = "PoseLib作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "ARMATURE":
            self.report({"INFO"},"ARMATUREを選択してください")

        acu = fjw.ActionConstraintUtils(fjw.active())
        acu.make_action()
        return {'FINISHED'}
########################################

########################################
#中間ポーズ設定
########################################
#bpy.ops.fjw.set_midpose_to_current_poselib() #中間ポーズ追加
class FUJIWARATOOLBOX_set_midpose_to_current_poselib(bpy.types.Operator):
    """アクティブなポーズライブラリの中間ポーズを設定する。"""
    bl_idname = "fujiwara_toolbox.set_midpose_to_current_poselib"
    bl_label = "中間ポーズ設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "ARMATURE":
                self.report({"INFO"},"ARMATUREを選択してください")
        acu = fjw.ActionConstraintUtils(fjw.active())
        acu.add_pose(acu.action_frame/2,"MidPose")
        return {'FINISHED'}
########################################

########################################
#終端ポーズ再設定
########################################
#bpy.ops.fjw.set_endpose_to_current_poselib() #終端ポーズ再設定
class FUJIWARATOOLBOX_set_endpose_to_current_poselib(bpy.types.Operator):
    """アクティブなポーズライブラリの終端ポーズを再設定する。"""
    bl_idname = "fujiwara_toolbox.set_endpose_to_current_poselib"
    bl_label = "終端ポーズ再設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "ARMATURE":
                self.report({"INFO"},"ARMATUREを選択してください")
        acu = fjw.ActionConstraintUtils(fjw.active())
        acu.add_pose(acu.action_frame,"EndPose")
        return {'FINISHED'}
########################################







########################################
#アクションコンストレイント作成
########################################
#bpy.ops.fjw.make_action_constraint_with_current_poselib() #アクションコンストレイント作成
class FUJIWARATOOLBOX_make_action_constraint_with_current_poselib(bpy.types.Operator):
    """アクティブなポーズライブラリで、アクティブボーンをターゲットにしたアクションコンストレイントを作成する。"""
    bl_idname = "fujiwara_toolbox.make_action_constraint_with_current_poselib"
    bl_label = "アクションコンストレイント作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "ARMATURE":
                self.report({"INFO"},"ARMATUREを選択してください")
        acu = fjw.ActionConstraintUtils(fjw.active())
        action = acu.armature.pose_library
        acu.set_action_constraint(action)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("プロクシ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#オリジナルを反映
########################################

def find_proxy(original):
    for obj in bpy.context.scene.objects:
        if obj.proxy is None:
            continue
        if obj.proxy == original:
            return obj
    return original

#bpy.ops.fujiwara_toolbox.bone_constraints_from_original() #オリジナルを反映
class FUJIWARATOOLBOX_BONE_CONSTRAINTS_FROM_ORIGINAL(bpy.types.Operator):
    """コンストレイントがないボーンにオリジナルのコンストレイントを反映する。"""
    bl_idname = "fujiwara_toolbox.bone_constraints_from_original"
    bl_label = "オリジナルを反映"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        armature = fjw.active()
        if armature is None or armature.type != "ARMATURE":
            return {'CANCELLED'}

        armu = fjw.ArmatureUtils(armature)
        if not armu.is_proxy:
            return {'CANCELLED'}

        prox_armu = armu
        orig_armu = fjw.ArmatureUtils(prox_armu.armature.proxy)

        for prox_pbone in prox_armu.pose_bones:
            if len(prox_pbone.constraints) != 0:
                continue
            orig_pbone = orig_armu.posebone(prox_pbone.name)
            if len(orig_pbone.constraints) == 0:
                continue
            #オリジナルにはコンストレイントがあるのにプロクシにない
            for orig_bone_constraint in orig_pbone.constraints:
                #各コンストレイントをコピーする。
                #http://www.yoheim.net/blog.php?q=20161002
                prox_constraint = prox_pbone.constraints.new(orig_bone_constraint.type)
                props = dir(orig_bone_constraint)
                for prop in props:
                    val = getattr(orig_bone_constraint, prop)
                    if type(val) == bpy.types.Object:
                        val = find_proxy(val)
                    try:
                        setattr(prox_constraint, prop, val)
                    except:
                        continue


        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Rigify")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
class ChildInfo:
    def __init__(self, obj):
        self.obj = obj
        self.parent_type = obj.parent_type
        self.parent_bone = obj.parent_bone
        self.print_info()

    def print_info(self):
        print("%s : %s, %s"%(self.obj.name, self.parent_type, self.parent_bone))

class BoneInfo:
    def __init__(self, bone):
        self.name = bone.name
        self.use_deform = bone.use_deform
        self.hide = bone.hide

import fujiwara_toolbox_modules.modules.main.submodules.rigify_tools as rigify_tools

########################################
#Genrigして再ペアレント
########################################
#bpy.ops.fujiwara_toolbox.genrig_reparent() #Genrigして再ペアレント
class FUJIWARATOOLBOX_GENRIG_REPARENT(bpy.types.Operator):
    """Generate Rigしてから、子オブジェクトを再び自動ウェイトでくくりつける。ボーン相対も反映する。Metarigは非表示にする。常に新規リグに差し替わる。
    ペアレントタイプはカスタムプロパティ"rigify_parenting"があればそれを優先する。
    """
    bl_idname = "fujiwara_toolbox.genrig_reparent"
    bl_label = "Genrigして再ペアレント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rt = rigify_tools.RigifyTools()
        rt.gen_rig_and_reparent(fjw.active())
        return {'FINISHED'}
########################################

########################################
#プロポーションアップデート
########################################
#bpy.ops.fujiwara_toolbox.update_rig_proportion() #プロポーションアップデート
class FUJIWARATOOLBOX_UPDATE_RIG_PROPORTION(bpy.types.Operator):
    """現在の形状をメタリグに反映し、再生する。関連オブジェクトは適宜再適用される。シェイプキーは削除される。"""
    bl_idname = "fujiwara_toolbox.update_rig_proportion"
    bl_label = "プロポーションアップデート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rt = rigify_tools.RigifyTools()
        # if not rt.is_symmetry(fjw.active()):
        #     self.report({"WARNING", "リグが非対称です。"})
        rt.update_rig_proportion(fjw.active())
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("Rigifyポージング")
############################################################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def set_rigify_ik_fk(value):
    obj = fjw.active()
    fjw.mode("POSE")
    for pb in obj.pose.bones:
        if "IK_FK" in pb:
            pb["IK_FK"] = value

    for bn in obj.data.bones:
        bn.select = True
    
    bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0)

#よくよく考えたらpost_fixってリンクしてるキャラ数分あるんじゃ
# import inspect
# def get_rigify_postfix():
#     post_fix = ""
#     for meth in inspect.getmembers(bpy.ops.pose):
#         if "fk2ik" in meth[0]:
#             post_fix = meth[0].split("_")[-1]
#             break
#     return post_fix

# def rigify_snap(rig, cmdstr):
#     """
#     cmdstr = "ik2fk" or "fk2ik"
#     """
#     post_fix = get_rigify_postfix()
#     opname = "bpy.ops.pose.rigify_arm_%s_%s"%(cmdstr, post_fix)
#     fjw.activate(rig)
#     fjw.mode("POSE")
#     bpy.ops.pose.select_all(action='SELECT')
#     return opname


# このへん作業中

# def set_rigify_ik2fk(rig):
#     opname = rigify_snap(rig, "ik2fk")
#     evalstr = opname +'(thigh_fk="thigh_fk.L", shin_fk="shin_fk.L", foot_fk="foot_fk.L", mfoot_fk="MCH-foot_fk.L", thigh_ik="thigh_ik.L", shin_ik="MCH-thigh_ik.L", foot_ik="MCH-thigh_ik_target.L", mfoot_ik="MCH-thigh_ik_target.L")'
#     eval(evalstr)
#     bpy.ops.pose.select_all(action='SELECT')
#     evalstr = opname +'(thigh_fk="thigh_fk.R", shin_fk="shin_fk.R", foot_fk="foot_fk.R", mfoot_fk="MCH-foot_fk.R", thigh_ik="thigh_ik.R", shin_ik="MCH-thigh_ik.R", foot_ik="MCH-thigh_ik_target.R", mfoot_ik="MCH-thigh_ik_target.R")'
#     eval(evalstr)
#     bpy.ops.pose.select_all(action='SELECT')
#     evalstr = opname +'(uarm_fk="upper_arm_fk.L", farm_fk="forearm_fk.L", hand_fk="hand_fk.L", uarm_ik="upper_arm_ik.L", farm_ik="MCH-upper_arm_ik.L", hand_ik="hand_ik.L")'
#     eval(evalstr)
#     bpy.ops.pose.select_all(action='SELECT')
#     evalstr = opname +'(uarm_fk="upper_arm_fk.R", farm_fk="forearm_fk.R", hand_fk="hand_fk.R", uarm_ik="upper_arm_ik.R", farm_ik="MCH-upper_arm_ik.R", hand_ik="hand_ik.R")'
#     eval(evalstr)

# def set_rigify_fk2ik(rig):
#     opname = rigify_snap(rig, "fk2ik")
#     evalstr = opname +'(thigh_fk="thigh_fk.L", shin_fk="shin_fk.L", foot_fk="foot_fk.L", mfoot_fk="MCH-foot_fk.L", thigh_ik="thigh_ik.L", shin_ik="MCH-thigh_ik.L", foot_ik="MCH-thigh_ik_target.L", mfoot_ik="MCH-thigh_ik_target.L")'
#     eval(evalstr)
#     bpy.ops.pose.select_all(action='SELECT')
#     evalstr = opname +'(thigh_fk="thigh_fk.R", shin_fk="shin_fk.R", foot_fk="foot_fk.R", mfoot_fk="MCH-foot_fk.R", thigh_ik="thigh_ik.R", shin_ik="MCH-thigh_ik.R", foot_ik="MCH-thigh_ik_target.R", mfoot_ik="MCH-thigh_ik_target.R")'
#     eval(evalstr)
#     bpy.ops.pose.select_all(action='SELECT')
#     evalstr = opname +'(uarm_fk="upper_arm_fk.L", farm_fk="forearm_fk.L", hand_fk="hand_fk.L", uarm_ik="upper_arm_ik.L", farm_ik="MCH-upper_arm_ik.L", hand_ik="hand_ik.L")'
#     eval(evalstr)
#     bpy.ops.pose.select_all(action='SELECT')
#     evalstr = opname +'(uarm_fk="upper_arm_fk.R", farm_fk="forearm_fk.R", hand_fk="hand_fk.R", uarm_ik="upper_arm_ik.R", farm_ik="MCH-upper_arm_ik.R", hand_ik="hand_ik.R")'
#     eval(evalstr)



########################################
#IK All
########################################
#bpy.ops.fujiwara_toolbox.rigify_ik_all() #IK All
class FUJIWARATOOLBOX_RIGIFY_IK_ALL(bpy.types.Operator):
    """全てのボーンのIK/FK値を0にする。"""
    bl_idname = "fujiwara_toolbox.rigify_ik_all"
    bl_label = "IK All"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj.type != "ARMATURE":
            return {"CANCELLED"}

        # set_rigify_ik2fk(obj)
        set_rigify_ik_fk(0)

        return {'FINISHED'}
########################################

########################################
#FK All
########################################
#bpy.ops.fujiwara_toolbox.rigify_fk_all() #FK All
class FUJIWARATOOLBOX_RIGIFY_FK_ALL(bpy.types.Operator):
    """全てのボーンのIK/FK値を1にする。"""
    bl_idname = "fujiwara_toolbox.rigify_fk_all"
    bl_label = "FK All"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj.type != "ARMATURE":
            return {"CANCELLED"}

        # set_rigify_fk2ik(obj)
        set_rigify_ik_fk(1)

        return {'FINISHED'}
########################################




#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#アーマチュアユーティリティ
########################################
class CATEGORYBUTTON_744202(bpy.types.Operator):#アーマチュアユーティリティ
    """アーマチュアユーティリティ"""
    bl_idname = "fujiwara_toolbox.categorybutton_744202"
    bl_label = "アーマチュアユーティリティ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("アーマチュアユーティリティ",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("便利")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#選択ボーン名一覧（ポーズモード）
########################################
#bpy.ops.fujiwara_toolbox.show_selected_pose_bones() #選択ボーン名一覧（ポーズモード）
class FUJIWARATOOLBOX_SHOW_SELECTED_POSE_BONES(bpy.types.Operator):
    """選択しているボーン名の一覧を表示する。ポーズモード。"""
    bl_idname = "fujiwara_toolbox.show_selected_pose_bones"
    bl_label = "選択ボーン名一覧（ポーズモード）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj.mode != "POSE":
            self.report({"WARNING"},"ポーズモードで実行してください。")
        
        result = []
        pbones = obj.pose.bones
        for pbone in pbones:
            if pbone.bone.select:
                result.append(pbone.name)

        result_str = "["
        for r in result:
            result_str += '"%s", '%r
        result_str += "]"
        self.report({"INFO"}, result_str)

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("素体システム用リネーマ")
############################################################################################################################






########################################
#ジオメトリ
########################################
class FUJIWARATOOLBOX_244616(bpy.types.Operator):#ジオメトリ
    """素体ジオメトリ"""
    bl_idname = "fujiwara_toolbox.command_244616"
    bl_label = "素体ジオメトリ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label

        return {'FINISHED'}
########################################

########################################
#素体アーマチュア
########################################
class FUJIWARATOOLBOX_589321(bpy.types.Operator):#素体アーマチュア
    """素体アーマチュア"""
    bl_idname = "fujiwara_toolbox.command_589321"
    bl_label = "素体アーマチュア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#ArmatureController
########################################
class FUJIWARATOOLBOX_573567(bpy.types.Operator):#ArmatureController
    """ArmatureController"""
    bl_idname = "fujiwara_toolbox.command_573567"
    bl_label = "ArmatureController"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#手コントローラ右
########################################
class FUJIWARATOOLBOX_285809(bpy.types.Operator):#手コントローラ右
    """手コントローラ右"""
    bl_idname = "fujiwara_toolbox.command_285809"
    bl_label = "手コントローラ右"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#手コントローラ左
########################################
class FUJIWARATOOLBOX_431070(bpy.types.Operator):#手コントローラ左
    """手コントローラ左"""
    bl_idname = "fujiwara_toolbox.command_431070"
    bl_label = "手コントローラ左"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#右手
########################################
class FUJIWARATOOLBOX_116809(bpy.types.Operator):#右手
    """右手"""
    bl_idname = "fujiwara_toolbox.command_116809"
    bl_label = "右手"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#左手
########################################
class FUJIWARATOOLBOX_694161(bpy.types.Operator):#左手
    """左手"""
    bl_idname = "fujiwara_toolbox.command_694161"
    bl_label = "左手"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#右足
########################################
class FUJIWARATOOLBOX_424374(bpy.types.Operator):#右足
    """右足"""
    bl_idname = "fujiwara_toolbox.command_424374"
    bl_label = "右足"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################

########################################
#左足
########################################
class FUJIWARATOOLBOX_372755(bpy.types.Operator):#左足
    """左足"""
    bl_idname = "fujiwara_toolbox.command_372755"
    bl_label = "左足"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.deselect()
        fjw.active().name = self.bl_label
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("標準ボーンリネーマ（Rigify準拠）")
############################################################################################################################



def bone_rename(bonename):
    arm = fjw.active()
    if arm.type != "ARMATURE":
        self.report({"INFO"},"アーマチュアを選択してください")
        return {'CANCELLED'}
    fjw.mode("EDIT")
    bone = arm.data.edit_bones.active
    bone.name = bonename



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#head
########################################
class FUJIWARATOOLBOX_851815(bpy.types.Operator):#head
    """head"""
    bl_idname = "fujiwara_toolbox.command_851815"
    bl_label = "head"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#neck
########################################
class FUJIWARATOOLBOX_862554(bpy.types.Operator):#neck
    """neck"""
    bl_idname = "fujiwara_toolbox.command_862554"
    bl_label = "neck"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#chest
########################################
class FUJIWARATOOLBOX_632665(bpy.types.Operator):#chest
    """chest"""
    bl_idname = "fujiwara_toolbox.command_632665"
    bl_label = "chest"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#spine
########################################
class FUJIWARATOOLBOX_886883(bpy.types.Operator):#spine
    """spine"""
    bl_idname = "fujiwara_toolbox.command_886883"
    bl_label = "spine"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#hips
########################################
class FUJIWARATOOLBOX_916888(bpy.types.Operator):#hips
    """hips"""
    bl_idname = "fujiwara_toolbox.command_916888"
    bl_label = "hips"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#root
########################################
class FUJIWARATOOLBOX_324118(bpy.types.Operator):#root
    """root"""
    bl_idname = "fujiwara_toolbox.command_324118"
    bl_label = "root"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#shoulder.R
########################################
class FUJIWARATOOLBOX_403000(bpy.types.Operator):#shoulder.R
    """shoulder.R"""
    bl_idname = "fujiwara_toolbox.command_403000"
    bl_label = "shoulder.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################


########################################
#shoulder.L
########################################
class FUJIWARATOOLBOX_779120(bpy.types.Operator):#shoulder.L
    """shoulder.L"""
    bl_idname = "fujiwara_toolbox.command_779120"
    bl_label = "shoulder.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#upper_arm.R
########################################
class FUJIWARATOOLBOX_148790(bpy.types.Operator):#upper_arm.R
    """upper_arm.R"""
    bl_idname = "fujiwara_toolbox.command_148790"
    bl_label = "upper_arm.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#upper_arm.L
########################################
class FUJIWARATOOLBOX_598468(bpy.types.Operator):#upper_arm.L
    """upper_arm.L"""
    bl_idname = "fujiwara_toolbox.command_598468"
    bl_label = "upper_arm.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#forearm.R
########################################
class FUJIWARATOOLBOX_148513(bpy.types.Operator):#forearm.R
    """forearm.R"""
    bl_idname = "fujiwara_toolbox.command_148513"
    bl_label = "forearm.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################


########################################
#forearm.L
########################################
class FUJIWARATOOLBOX_928612(bpy.types.Operator):#forearm.L
    """forearm.L"""
    bl_idname = "fujiwara_toolbox.command_928612"
    bl_label = "forearm.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#hand.R
########################################
class FUJIWARATOOLBOX_43548(bpy.types.Operator):#hand.R
    """hand.R"""
    bl_idname = "fujiwara_toolbox.command_43548"
    bl_label = "hand.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#hand.L
########################################
class FUJIWARATOOLBOX_862708(bpy.types.Operator):#hand.L
    """hand.L"""
    bl_idname = "fujiwara_toolbox.command_862708"
    bl_label = "hand.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------





#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#thigh.R
########################################
class FUJIWARATOOLBOX_474630(bpy.types.Operator):#thigh.R
    """thigh.R"""
    bl_idname = "fujiwara_toolbox.command_474630"
    bl_label = "thigh.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################
########################################
#thigh.L
########################################
class FUJIWARATOOLBOX_550261(bpy.types.Operator):#thigh.L
    """thigh.L"""
    bl_idname = "fujiwara_toolbox.command_550261"
    bl_label = "thigh.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#shin.R
########################################
class FUJIWARATOOLBOX_371561(bpy.types.Operator):#shin.R
    """shin.R"""
    bl_idname = "fujiwara_toolbox.command_371561"
    bl_label = "shin.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#shin.L
########################################
class FUJIWARATOOLBOX_348617(bpy.types.Operator):#shin.L
    """shin.L"""
    bl_idname = "fujiwara_toolbox.command_348617"
    bl_label = "shin.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#heel.R
########################################
class FUJIWARATOOLBOX_420903(bpy.types.Operator):#heel.R
    """heel.R"""
    bl_idname = "fujiwara_toolbox.command_420903"
    bl_label = "heel.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#heel.L
########################################
class FUJIWARATOOLBOX_559040(bpy.types.Operator):#heel.L
    """heel.L"""
    bl_idname = "fujiwara_toolbox.command_559040"
    bl_label = "heel.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#foot.R
########################################
class FUJIWARATOOLBOX_505403(bpy.types.Operator):#foot.R
    """foot.R"""
    bl_idname = "fujiwara_toolbox.command_505403"
    bl_label = "foot.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#foot.L
########################################
class FUJIWARATOOLBOX_120526(bpy.types.Operator):#foot.L
    """foot.L"""
    bl_idname = "fujiwara_toolbox.command_120526"
    bl_label = "foot.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#toe.R
########################################
class FUJIWARATOOLBOX_288663(bpy.types.Operator):#toe.R
    """toe.R"""
    bl_idname = "fujiwara_toolbox.command_288663"
    bl_label = "toe.R"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################

########################################
#toe.L
########################################
class FUJIWARATOOLBOX_135779(bpy.types.Operator):#toe.L
    """toe.L"""
    bl_idname = "fujiwara_toolbox.command_135779"
    bl_label = "toe.L"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bone_rename(self.bl_label)
        return {'FINISHED'}
########################################













#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("アーマチュア差し替え")
############################################################################################################################





########################################
#選択の形状をアクティブにあわせる
########################################
class FUJIWARATOOLBOX_729233(bpy.types.Operator):#選択の形状をアクティブにあわせる
    """選択の形状をアクティブにあわせる"""
    bl_idname = "fujiwara_toolbox.command_729233"
    bl_label = "選択の形状をアクティブにあわせる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        source_arm = fjw.active()
        target_arm = None

        for obj in bpy.context.selected_objects:
            if obj != source_arm:
                target_arm = obj
                break

        if source_arm == None or source_arm.type != "ARMATURE" or target_arm == None or target_arm.type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください")
            return {'CANCELLED'}


        source_arm.data.pose_position = "REST"
        target_arm.data.pose_position = "REST"

        #Xミラー解除
        target_arm.data.use_mirror_x = False


        #ペアレント解除→システムごと差し替えるからしないほうがいい
        #mode("OBJECT")
        #deselect()
        #activate(target_arm)
        #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        #位置あわせ
        target_arm.location = source_arm.location

        #target_arm.location[1] = source_arm.location[1]
        #target_arm.location[2] = source_arm.location[2]

        fjw.activate(target_arm)
        fjw.mode("EDIT")

        bone_names = []

        for bone in target_arm.data.edit_bones:
            ##デフォルト名はスルー。どう対応してるかわかったもんじゃないから
            #if "Bone." in bone.name:
            #    continue
            bone_names.append(bone.name)
            self.report({"INFO"},bone.name)



        #形状をあわせる
        #ボーンの接続を全て切る
        #mode("OBJECT")
        #activate(target_arm)
        #mode("EDIT")
        #for bone in target_arm.data.edit_bones:
        #    bone.use_connect = False


        #とりあえず数値をあらかじめ取得してみる
        fjw.mode("OBJECT")
        fjw.activate(source_arm)
        fjw.mode("EDIT")
        source_data = {}
        for bone in source_arm.data.edit_bones:
            source_data[bone.name] = [copy.deepcopy(bone.head),copy.deepcopy(bone.tail)]
            self.report({"INFO"},"src:" + bone.name)

        fjw.mode("OBJECT")
        fjw.activate(target_arm)
        fjw.mode("EDIT")
        for bone_name in bone_names:
            #mode("OBJECT")
            #mode("EDIT")
            if bone_name not in target_arm.data.edit_bones:
                continue
            if bone_name not in source_data:
                continue

            #選択解除
            bpy.ops.armature.select_all(action='DESELECT')

            ebone = target_arm.data.edit_bones[bone_name]
            target_arm.data.edit_bones.active = ebone

            ebone.head = source_data[bone_name][0]
            ebone.tail = source_data[bone_name][1]

            self.report({"INFO"},"move:" + ebone.name + " 予定地名:" + bone_name + " 予定地:" + str(source_data[bone_name][0]) + " 現在地:" + str(ebone.head))

        #Xミラー
        target_arm.data.use_mirror_x = True
        
        return {'FINISHED'}
########################################

########################################
#選択からアクティブへリターゲット
########################################
class FUJIWARATOOLBOX_546712(bpy.types.Operator):#選択からアクティブへリターゲット
    """選択からアクティブへリターゲット"""
    bl_idname = "fujiwara_toolbox.command_546712"
    bl_label = "選択からアクティブへリターゲット"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        source_arm = None
        target_arm = fjw.active()
        
        #隠れてるものがあるとまずい。
        fjw.mode("OBJECT")
        bpy.ops.object.hide_view_clear()


        for obj in bpy.context.selected_objects:
            if obj != target_arm:
                source_arm = obj
                break

        if source_arm == None or source_arm.type != "ARMATURE" or target_arm == None or target_arm.type != "ARMATURE":
            self.report({"INFO"},"アーマチュアを選択してください")
            return {'CANCELLED'}

        #ターゲットの子を全て削除
        fjw.deselect()
        fjw.activate(target_arm)
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        #メッシュだけ
        for obj in fjw.get_selected_list():
            if obj.type != "MESH":
                obj.select = False
        fjw.delete(fjw.get_selected_list())


        #ソースの子を取得
        fjw.deselect()
        fjw.activate(source_arm)
        bpy.ops.object.select_grouped(type='CHILDREN')
        
        #オブジェクトのペアレント状態を保存する
        source_children_data = {}
        for obj in fjw.get_selected_list():
            #ペアレントはsource_armにきまってんのでペアレントオブジェクトの情報はいらない
            source_children_data[obj.name] = {"name":obj.name,"parent_bone":obj.parent_bone, "parent_type":obj.parent_type}
            #self.report({"INFO"}, str(source_children_data[obj.name]))
        #ペアレント解除
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')



        #リターゲット
        #まずは通常ペアレントだけ
        self.report({"INFO"},str(source_children_data))
        for obj_data_name in source_children_data:
            obj_data = source_children_data[obj_data_name]
            fjw.deselect()
            #self.report({"INFO"},str(obj_data))
            obj = bpy.data.objects[obj_data["name"]]
            obj.select = True
            fjw.activate(target_arm)
            target_arm.select = True


            if obj_data["parent_type"] == "OBJECT":
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            if obj_data["parent_type"] == "BONE":
                fjw.mode("POSE")
                #アクティブボーンの設定
                bones = fjw.active().data.bones
                if obj_data["parent_bone"] not in bones:
                    continue
                bones.active = bones[obj_data["parent_bone"]]
                #ペアレントつける
                bpy.ops.object.parent_set(type='BONE_RELATIVE')


                #obj.parent_type = "BONE"
                #obj.parent_bone = obj_data["parent_bone"]

        #mod設定
        for obj_data_name in source_children_data:
            obj_data = source_children_data[obj_data_name]
            fjw.deselect()
            obj = bpy.data.objects[obj_data["name"]]
            fjw.activate(obj)
            for mod in obj.modifiers:
                if mod.type == "MIRROR":
                    if mod.mirror_object == source_arm:
                        mod.mirror_object = target_arm
                if mod.type == "ARMATURE":
                        mod.object = target_arm

        #ポーズオン
        target_arm.data.pose_position = "POSE"
        source_arm.data.pose_position = "POSE"



        return {'FINISHED'}
########################################















#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#BlenRigヘルパー
########################################
class CATEGORYBUTTON_456539(bpy.types.Operator):#BlenRigヘルパー
    """BlenRigヘルパー"""
    bl_idname = "fujiwara_toolbox.categorybutton_456539"
    bl_label = "BlenRigヘルパー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("BlenRigヘルパー",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("アーマチュア")
############################################################################################################################

#バインドするならTrue。しないならFalse。
def blenrig_mdbinding(objects, bound):
    if "BlenRig_mdef_cage" in bpy.data.objects:
        cage = bpy.data.objects["BlenRig_mdef_cage"]
        #関連バインドの解除→選択物のみ。負荷軽減。
        for obj in objects:
            if obj.type == "MESH":
                for mod in obj.modifiers:
                    if mod.type == "MESH_DEFORM":
                        if mod.object == cage:
                            #バインド変更
                            if mod.is_bound != bound:
                                fjw.activate(obj)
                                bpy.ops.object.meshdeform_bind(modifier=mod.name)

    pass

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#体型編集
########################################
class FUJIWARATOOLBOX_545067(bpy.types.Operator):#体型編集
    """体型編集"""
    bl_idname = "fujiwara_toolbox.command_545067"
    bl_label = "体型編集"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_ARMATURE",mode="")


    def execute(self, context):
        #バインド解除
        blenrig_mdbinding(fjw.get_selected_list(), False)

        bpy.context.scene.layers[10] = True
        bpy.context.scene.layers[11] = True

        rig = fjw.active()
        if rig.type != "ARMATURE":
            return {'CANCELLED'}


        #rig = None
        #for obj in bpy.data.objects:
        #    if "blenrig" in obj.name:
        #        rig = obj
        #rig = bpy.data.objects["biped_blenrig"]
        if rig != None:
            rig.show_x_ray = True
            fjw.activate(rig)
            fjw.mode("POSE")
            rig.data.reproportion = True

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#右側選択
########################################
class FUJIWARATOOLBOX_942054(bpy.types.Operator):#右側選択
    """右側選択"""
    bl_idname = "fujiwara_toolbox.command_942054"
    bl_label = "右側選択"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.select_pattern(pattern="*_R")

        return {'FINISHED'}
########################################






########################################
#ミラーリング
########################################
class FUJIWARATOOLBOX_734967(bpy.types.Operator):#ミラーリング
    """ミラーリング"""
    bl_idname = "fujiwara_toolbox.command_734967"
    bl_label = "ミラーリング"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.pose.copy()
        bpy.ops.pose.paste(flipped=True)

        return {'FINISHED'}
########################################

########################################
#左側選択
########################################
class FUJIWARATOOLBOX_384660(bpy.types.Operator):#左側選択
    """左側選択"""
    bl_idname = "fujiwara_toolbox.command_384660"
    bl_label = "左側選択"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.object.select_pattern(pattern="*_L")

        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#アクティブのグループのみ表示
########################################
class FUJIWARATOOLBOX_315193(bpy.types.Operator):#アクティブのグループのみ表示
    """アクティブのグループのみ表示"""
    bl_idname = "fujiwara_toolbox.command_315193"
    bl_label = "アクティブのグループのみ表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.pose.select_grouped(type='GROUP')
        bpy.ops.pose.select_all(action='INVERT')
        bpy.ops.pose.hide(unselected=False)

        return {'FINISHED'}
########################################


########################################
#全て表示
########################################
class FUJIWARATOOLBOX_705250(bpy.types.Operator):#全て表示
    """全て表示"""
    bl_idname = "fujiwara_toolbox.command_705250"
    bl_label = "全て表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.pose.reveal()

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#完了
########################################
class FUJIWARATOOLBOX_859280(bpy.types.Operator):#完了
    """完了"""
    bl_idname = "fujiwara_toolbox.command_859280"
    bl_label = "完了"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")


    def execute(self, context):
        current = fjw.active()
        fjw.mode("OBJECT")
        #armature = bpy.data.objects["biped_blenrig"]
        #cage = bpy.data.objects["BlenRig_mdef_cage"]
        #proxy = bpy.data.objects["BlenRig_proxy_model"]
        #armature = find("blenrig")
        if current.type != "ARMATURE":
            return {'CANCELLED'}
        armature = current
        cage = fjw.find("BlenRig_mdef_cage")
        proxy = fjw.find("BlenRig_proxy_model")

        ######################################################################
        #Childrenメッシュの下処理
        ######################################################################

        fjw.activate(armature)
        targetobjects = []
        targetobjects_data = {}
        #アーマチュアmodがついている子をターゲットリストにいれる
        for obj in armature.children:
            targetobjects.append(obj)
            targetobjects_data[obj.data] = {"name":obj.name,"parent_bone":obj.parent_bone, "parent_type":obj.parent_type, "armature":False}
            if obj.type == "MESH":
                if obj == cage or obj == proxy:
                    continue


                for mod in obj.modifiers:
                    if mod.type == "ARMATURE":
                        targetobjects_data[obj.data] = {"name":obj.name,"parent_bone":obj.parent_bone, "parent_type":obj.parent_type, "armature":True}
                        break

        #ターゲット群をペアレント解除する
        for obj in targetobjects:
            obj.hide = False
            fjw.deselect()
            fjw.activate(obj)
            self.report({"INFO"},obj.name)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        bpy.ops.object.mode_set(mode='OBJECT')
    

        mirrored_objects = []

        #オブジェクト側：アーマチュア適用
        for obj in targetobjects:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                if mod.type == "MIRROR":
                    mirrored_objects.append(obj)
                    #アーマチュアより上位にあるミラーを適用しないと齟齬がでたので仕方なくミラー適用
                    #bpy.ops.object.modifier_apply(modifier=mod.name)
                    #むしろミラー除去
                    bpy.ops.object.modifier_remove(modifier=mod.name)
                if mod.type == "ARMATURE":
                    #適用する
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                        pass
                    except  :
                        self.report({"INFO"},"mod適用エラー：" + obj.name + "/" + mod.name)
                        pass
        
        for obj in targetobjects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')



        #一旦Blenrigの処理へ

        ######################################################################
        #Blenrigパート
        ######################################################################
        #ケージのメッシュベイク
        if cage is not None:
            fjw.deselect()
            bpy.context.scene.layers[11] = True
            fjw.activate(cage)
            cage.select = True
            fjw.mode("OBJECT")
            bpy.ops.blenrig5.mesh_pose_baker()
            cage.select = False

        #プロクシのメッシュベイク
        if proxy is not None:
            fjw.deselect()
            bpy.context.scene.layers[1] = True
            fjw.activate(proxy)
            proxy.select = True
            fjw.mode("OBJECT")
            bpy.ops.blenrig5.mesh_pose_baker()

            bpy.context.scene.layers[1] = False

        #アーマチュアのベイク
        fjw.deselect()
        fjw.activate(armature)
        armature.select = True
        fjw.mode("POSE")
        bpy.ops.pose.reveal()
        bpy.ops.blenrig5.armature_baker()


        ######################################################################
        #Childrenメッシュの更新
        ######################################################################
        fjw.deselect()
        #アーマチュアとオブジェクトを選択

        #再ペアレント
        for obj_data_name in targetobjects_data:
            obj_data = targetobjects_data[obj_data_name]
            fjw.deselect()
            obj = bpy.data.objects[obj_data["name"]]
            obj.select = True
            fjw.activate(armature)
            armature.select = True


            if obj_data["parent_type"] == "OBJECT":
                if obj_data["armature"]:
                    bpy.ops.object.parent_set(type='ARMATURE_NAME')
                else:
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            if obj_data["parent_type"] == "BONE":
                fjw.activate(armature)
                fjw.mode("POSE")
                #アクティブボーンの設定
                bones = fjw.active().data.bones
                if obj_data["parent_bone"] not in bones:
                    continue
                bones.active = bones[obj_data["parent_bone"]]
                self.report({"INFO"},bones.active.basename)

                fjw.mode("POSE")
                self.report({"INFO"},"active:" + fjw.active().data.bones.active.basename)
                

                #オブジェクトレイヤーを全表示に
                current_objlayers = [True for i in range(32)]
                for i in range(32):
                    current_objlayers[i] = fjw.active().data.layers[i]
                #copy.deepcopy(active().data.layers)
                fjw.active().data.layers = [True for i in range(32)]


                #ペアレントつける
                bpy.ops.object.parent_set(type='BONE_RELATIVE')

                #オブジェクトレイヤーを戻す
                fjw.active().data.layers = current_objlayers


        ##空のウェイトでペアレント
        #armature.select = True
        ##select(targetobjects)
        #activate(armature)
        #bpy.ops.object.parent_set(type='ARMATURE_NAME', xmirror=False,
        #keep_transform=False)

        #アーマチュアを一番上に
        for obj in targetobjects:
            if obj.type == "MESH":
                fjw.activate(obj)
                modslen = len(obj.modifiers)
                if modslen > 0:
                    #一番新しい奴＝アーマチュア
                    mod = obj.modifiers[modslen - 1]
                    for n in range(0,modslen):
                        bpy.ops.object.modifier_move_up(modifier=mod.name)


        #ミラーのつけなおし
        for obj in mirrored_objects:
            if obj.type == "MESH":
                fjw.activate(obj)
                bpy.ops.object.modifier_add(type='MIRROR')
                mod = fjw.getnewmod(obj)
                mod.mirror_object = armature

        #ミラーは一番上に。
        for obj in mirrored_objects:
            if obj.type == "MESH":
                fjw.activate(obj)
                modslen = len(obj.modifiers)
                if modslen > 0:
                    mod = obj.modifiers[modslen - 1]
                    for n in range(0,modslen):
                        bpy.ops.object.modifier_move_up(modifier=mod.name)



        ######################################################################
        #Blenrigパート
        ######################################################################
        fjw.activate(armature)
        armature.data.reproportion = False

        #再バインド
        #blenrig_mdbinding(armature.children, True)
        fjw.activate(current)

        return {'FINISHED'}
########################################




########################################
#再バインド
########################################
class FUJIWARATOOLBOX_115485(bpy.types.Operator):#再バインド
    """再バインド"""
    bl_idname = "fujiwara_toolbox.command_115485"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        armature = bpy.data.objects["biped_blenrig"]
        blenrig_mdbinding(armature.children, True)
        
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



############################################################################################################################
uiitem("ケージ")
############################################################################################################################
"""
ケージ編集
ベイク
"""
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ケージスカルプト
########################################
class FUJIWARATOOLBOX_724488(bpy.types.Operator):#ケージスカルプト
    """ケージスカルプト。バインド操作は選択物のみ。"""
    bl_idname = "fujiwara_toolbox.command_724488"
    bl_label = "ケージスカルプト"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SCULPTMODE_HLT",mode="")


    def execute(self, context):
        #ケージレイヤの表示
        bpy.context.scene.layers[11] = True
        
        fjw.mode("OBJECT")
        cage = bpy.data.objects["BlenRig_mdef_cage"]
        cage.select = True

        #バインドは一番上につくので、subdiv0にする
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0

        #関連バインドの解除→洗濯物のみ。負荷軽減。
        blenrig_mdbinding(fjw.get_selected_list(),False)

        fjw.reject_notmesh()
        fjw.localview()

        bpy.context.scene.layers[11] = True
        fjw.activate(cage)
        cage.draw_type = "TEXTURED"
        fjw.mode("SCULPT")

        return {'FINISHED'}
########################################

########################################
#完了
########################################
class FUJIWARATOOLBOX_371121(bpy.types.Operator):#完了
    """完了"""
    bl_idname = "fujiwara_toolbox.command_371121"
    bl_label = "完了"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="")


    def execute(self, context):
        fjw.globalview()

        cage = bpy.data.objects["BlenRig_mdef_cage"]
        fjw.mode("OBJECT")
        fjw.activate(cage)
        fjw.mode("OBJECT")
        cage.draw_type = "WIRE"

        

        #関連再バインド
        blenrig_mdbinding(bpy.data.objects, True)
        fjw.activate(cage)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


















################################################################################
#UIカテゴリ
########################################
#VectorDisplacementモデル
########################################
class CATEGORYBUTTON_290440(bpy.types.Operator):#VectorDisplacementモデル
    """VectorDisplacementモデル"""
    bl_idname = "fujiwara_toolbox.categorybutton_290440"
    bl_label = "VectorDisplacementモデル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("VectorDisplacementモデル",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




########################################
#セミオートインポート・セットアップ
########################################
class FUJIWARATOOLBOX_475352(bpy.types.Operator):#セミオートインポート・セットアップ
    """マップはtexturesにいれること。設定は47番。"""
    bl_idname = "fujiwara_toolbox.command_475352"
    bl_label = "オートインポート・セットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #objのインポート
        import bpy
        import os
        import re
        
        
        for obj in bpy.data.objects:
            obj.select = False
        
        dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "")
        
        files = os.listdir(dir)
        for file in files:
            if re.search(r"meta", file) is not None: continue
            if re.search(r"(fbx)|(FBX)|(obj)|(OBJ)|(lwo)|(LWO)",file) is not None :
                loaded = False
                if re.search(r"(fbx)|(FBX)",file) is not None :
                    bpy.ops.import_scene.fbx(filepath=file)
                    loaded = True
                if re.search(r"(obj)|(OBJ)",file) is not None :
                    bpy.ops.import_scene.obj(filepath=file)
                    loaded = True
                if re.search(r"(lwo)|(LWO)",file) is not None :
                    bpy.ops.import_scene.lwo(filepath=file)
                    loaded = True
                if loaded is False : continue
                #グループ化
                groupname = os.path.splitext(os.path.basename(file))[0]
                bpy.ops.group.create(name=groupname)
        
        
        #テクスチャの読み込み
        #dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath),
        #"") + os.sep + "textures" + os.sep
        #やっぱtexturesめんどくさかった
        dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath), "") + os.sep
        
        files = os.listdir(dir)
        for file in files:
            print(dir + "\\" + file)
            if re.search(r"meta", file) is not None: continue
            if re.search(r"(exr)|(tif)|(tiff)|(jpg)|(png)",file) is not None :
                bpy.ops.image.open(filepath=dir + "\\" + file)
                img = bpy.data.images[file]
                bpy.ops.texture.new()
                #最後のテクスチャ
                lasttex = bpy.data.textures[len(bpy.data.textures) - 1]
                lasttex.name = file
                lasttex.image = img
                lasttex.use_clamp = False
        
        
        
        #modの準備
        for group in bpy.data.groups:
            for obj in group.objects:
                if obj.type == "MESH":
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_add(type='SUBSURF')
                    bpy.context.object.modifiers["Subsurf"].levels = 3
                    bpy.context.object.modifiers["Subsurf"].render_levels = 5
                    bpy.context.object.modifiers["Subsurf"].subdivision_type = 'CATMULL_CLARK'
                    bpy.ops.object.modifier_add(type='DISPLACE')
                    bpy.context.object.modifiers["Displace"].direction = 'RGB_TO_XYZ'
                    bpy.context.object.modifiers["Displace"].mid_level = 0
                    bpy.context.object.modifiers["Displace"].texture_coords = 'UV'
                    bpy.context.object.modifiers["Displace"].texture = bpy.data.textures[group.name + ".exr"]
                    bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')
                    bpy.context.object.modifiers["CorrectiveSmooth"].use_only_smooth = True
        
        
        return {'FINISHED'}
########################################

########################################
#多重解像度モデル化
########################################
class FUJIWARATOOLBOX_954427(bpy.types.Operator):#多重解像度モデル化
    """多重解像度モデル化"""
    bl_idname = "fujiwara_toolbox.command_954427"
    bl_label = "多重解像度モデル化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        targets = fjw.get_selected_list()
        for target in targets:
            bpy.context.scene.render.use_simplify = True
            bpy.context.scene.render.simplify_subdivision = 0
            fjw.deselect()
            fjw.activate(target)
            target.select = True
            #subdivレベルを得る
            div = 0
            for mod in target.modifiers:
                if mod.type == "SUBSURF":
                    if mod.render_levels > div:
                        mod.levels = mod.render_levels

                    div = mod.levels
            
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            newone = fjw.active()

            #mod削除
            for mod in newone.modifiers:
                bpy.ops.object.modifier_remove(modifier=mod.name)
            
            #多重解像度
            bpy.ops.object.modifier_add(type='MULTIRES')
            mod = fjw.getnewmod(newone)
            #分割
            for n in range(div):
                bpy.ops.object.multires_subdivide(modifier=mod.name)

            target.select = True
            bpy.context.scene.render.use_simplify = False
            #再形成
            bpy.ops.object.multires_reshape(modifier=mod.name)

            name = target.name
            #元のを削除
            fjw.deselect()
            target.select = True
            fjw.delete(fjw.get_selected_list())
            newone.name = name

        self.report({"INFO"},"完了")
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#物理
########################################
class CATEGORYBUTTON_984430(bpy.types.Operator):#物理
    """物理"""
    bl_idname = "fujiwara_toolbox.categorybutton_984430"
    bl_label = "物理"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("物理",True)
    uiitem.button(bl_idname,bl_label,icon="PHYSICS",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################




########################################
#ベイクリフレッシュ
########################################
class FUJIWARATOOLBOX_245059(bpy.types.Operator):#ベイクリフレッシュ
    """ベイクリフレッシュ"""
    bl_idname = "fujiwara_toolbox.command_245059"
    bl_label = "ベイクリフレッシュ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_REFRESH",mode="")

    def execute(self, context):
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0
        
        
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#Pin割当
########################################
class FUJIWARATOOLBOX_823626(bpy.types.Operator):#Pin割当
    """Pin割当"""
    bl_idname = "fujiwara_toolbox.command_823626"
    bl_label = "Pin割当"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="edit")

    def execute(self, context):
        obj = bpy.context.active_object
        if("Pin" not in obj.vertex_groups):
            bpy.ops.object.vertex_group_add()
            obj.vertex_groups[len(obj.vertex_groups) - 1].name = "Pin"
        
        
        obj.vertex_groups.active_index = obj.vertex_groups.find("Pin")
        bpy.ops.object.vertex_group_assign()
        
        
        
        
        
        return {'FINISHED'}
########################################

#########################################
##Total割当
#########################################
#class FUJIWARATOOLBOX_878504(bpy.types.Operator):#Total割当
#    """Total割当"""
#    bl_idname = "fujiwara_toolbox.command_878504"
#    bl_label = "Total割当"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
####    def execute(self, context):
#        for obj in bpy.context.selected_objects:
#            bpy.context.scene.objects.active = obj
#
#            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
#
#            if("Total" not in obj.vertex_groups):
#                bpy.ops.mesh.select_all(action='SELECT')
#                bpy.ops.object.vertex_group_add()
#                obj.vertex_groups[len(obj.vertex_groups)-1].name = "Total"
#
#
#            obj.vertex_groups.active_index = obj.vertex_groups.find("Total")
#            bpy.ops.object.vertex_group_assign()
#
#            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
#        return {'FINISHED'}
#########################################
















# ########################################
# #コリジョン用複製
# ########################################
# class FUJIWARATOOLBOX_205157(bpy.types.Operator):#コリジョン用複製
#     """コリジョン用複製"""
#     bl_idname = "fujiwara_toolbox.command_205157"
#     bl_label = "コリジョン用複製"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         source = bpy.context.scene.objects.active
#         bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
#         target = bpy.context.scene.objects.active
#         target.name = source.name + "_Collision"
#         target.draw_type = 'WIRE'
#         target.hide_render = True
#         #Armature以外削除
#         for mod in target.modifiers:
#             if mod.type != "ARMATURE":
#                 bpy.ops.object.modifier_remove(modifier=mod.name)
        
#         bpy.ops.object.modifier_add(type='SHRINKWRAP')
#         for mod in target.modifiers:
#             if mod.type == "SHRINKWRAP":
#                 mod.target = source
#                 mod.offset = 0.005
#                 mod.use_keep_above_surface = True
        
#         #コリジョン追加
#         bpy.ops.object.modifier_add(type='COLLISION')
        
        
#         return {'FINISHED'}
# ########################################

########################################
#サーフェスのオフセットを作成
########################################
class FUJIWARATOOLBOX_598876(bpy.types.Operator):#サーフェスのオフセットを作成
    """サーフェスのオフセットを作成"""
    bl_idname = "fujiwara_toolbox.command_598876"
    bl_label = "サーフェスのオフセットを作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        source = bpy.context.scene.objects.active
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        target = bpy.context.scene.objects.active
        target.name = source.name + "_SurfaceOffset"
        target.draw_type = 'TEXTURED'
        #Armature以外削除
        for mod in target.modifiers:
            if mod.type != "ARMATURE":
                bpy.ops.object.modifier_remove(modifier=mod.name)
        
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        for mod in target.modifiers:
            if mod.type == "SHRINKWRAP":
                mod.target = source
                mod.offset = 0.01
                mod.use_keep_above_surface = True
        
        
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("コリジョン")
############################################################################################################################
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#コリジョン化
########################################
#bpy.ops.fujiwara_toolbox.make_this_collision() #コリジョン化
class FUJIWARATOOLBOX_MAKE_THIS_COLLISION(bpy.types.Operator):
    """アクティブオブジェクトをコリジョン化する。"""
    bl_idname = "fujiwara_toolbox.make_this_collision"
    bl_label = "コリジョン化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_PHYSICS",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj.type != "MESH":
            return {'CANCELLED'} 
        
        fjw.mode("OBJECT")
        obj.hide_render = True
        obj.draw_type = "WIRE"
        modu = fjw.Modutils(obj)
        modu.add("Collision", "COLLISION")

        return {'FINISHED'}
########################################

########################################
#球コリジョン追加
########################################
#bpy.ops.fujiwara_toolbox.add_sphere_collision() #球コリジョン追加
class FUJIWARATOOLBOX_ADD_SPHERE_COLLISION(bpy.types.Operator):
    """球コリジョンを追加する"""
    bl_idname = "fujiwara_toolbox.add_sphere_collision"
    bl_label = "球コリジョン追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add(size=1, view_align=False, enter_editmode=False, location=fjw.cursor(), layers=bpy.context.scene.layers)
        bpy.ops.fujiwara_toolbox.make_this_collision() #コリジョン化

        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

# ############################################################################################################################
# uiitem("キャラ用")
# ############################################################################################################################

# ########################################
# #クロスを確定して髪準備
# ########################################
# class FUJIWARATOOLBOX_482428(bpy.types.Operator):#クロスを確定して髪準備
#     """クロスを確定して髪準備"""
#     bl_idname = "fujiwara_toolbox.command_482428"
#     bl_label = "クロスを確定して髪準備"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")


#     def execute(self, context):
#         selection = fjw.get_selected_list()
#         for obj in selection:
#             if obj.type == "MESH":
#                 fjw.deselect()
#                 fjw.activate(obj)
#                 mod_cloth = None
#                 for mod in obj.modifiers:
#                     if mod.type == "CLOTH":
#                         mod_cloth = mod
#                 if mod_cloth is None:
#                     continue

#                 #布適用
#                 bpy.ops.object.modifier_apply(modifier=mod_cloth.name)
                
#                 #パーティクル
#                 psetting = fjw.append_particlesetting("髪設定")
#                 bpy.context.object.hnMasterHairSystem = "髪設定"
#                 bpy.ops.particle.hairnet(meshKind="SHEET")


#         return {'FINISHED'}
# ########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#パーティクル
########################################
class CATEGORYBUTTON_947832(bpy.types.Operator):
    """パーティクル"""
    bl_idname = "fujiwara_toolbox.categorybutton_947832"
    bl_label = "パーティクル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("パーティクル",True)
    uiitem.button(bl_idname,bl_label,icon="PARTICLES",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("クイックシミュ")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
########################################
#メッシュ分割
########################################
#bpy.ops.fujiwara_toolbox.perticle_setup_mesh() #メッシュ分割
class FUJIWARATOOLBOX_PERTICLE_SETUP_MESH(bpy.types.Operator):
    """パーティクルシミュレーション用にメッシュを分割する"""
    bl_idname = "fujiwara_toolbox.perticle_setup_mesh"
    bl_label = "メッシュ分割"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EDITMODE_HLT",mode="")

    def execute(self, context):
        if not is_perticle_setup_executable(self):
            return {'CANCELLED'} 
        
        fjw.mode("EDIT")
        bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0)
        bpy.ops.mesh.poke()
        bpy.ops.mesh.tris_convert_to_quads()
        fjw.mode("OBJECT")

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def is_perticle_setup_executable(self):
    obj = fjw.active()
    if obj.type != "MESH":
        self.report({"INFO"},"メッシュオブジェクトを選択してください")
        return False
    fjw.mode("OBJECT")
    return True

def particle_setup_base(self):
    obj = fjw.active()
    
    # UV作成
    if "Particle_UV" in obj.data.uv_textures:
        particle_uv = obj.data.uv_textures["Particle_UV"]
    else:
        particle_uv = obj.data.uv_textures.new(name="Particle_UV")

    # パーティクル作成
    modu = fjw.Modutils(obj)
    pmod = modu.add("ParticleSystem","PARTICLE_SYSTEM")
    particle_system = pmod.particle_system
    particle_system.settings.render_type = "NONE"

    # Explode追加
    emod = modu.add("Explode", "EXPLODE")
    emod.use_edge_cut = True
    emod.particle_uv = particle_uv.name
    # protect
    # rna_type
    # show_alive
    # show_dead
    # show_expanded
    # show_in_editmode
    # show_on_cage
    # show_render
    # show_unborn
    # show_viewport
    # use_apply_on_spline
    # use_edge_cut
    # use_size
    # vertex_group

    smod = modu.add("Solidify", "SOLIDIFY")
    fjw.framejump(1)

    return (particle_system.settings, emod)

########################################
#崩壊
########################################
#bpy.ops.fujiwara_toolbox.perticle_setup_collaption() #崩壊
class FUJIWARATOOLBOX_PERTICLE_SETUP_COLLAPTION(bpy.types.Operator):
    """崩壊をセットアップ"""
    bl_idname = "fujiwara_toolbox.perticle_setup_collaption"
    bl_label = "崩壊"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PARTICLES",mode="")

    def execute(self, context):
        if not is_perticle_setup_executable(self):
            return {'CANCELLED'} 
        (psett, emod) = particle_setup_base(self)
        psett.normal_factor = 1.0
        psett.factor_random = 1.0
        psett.use_rotations = True
        psett.use_dynamic_rotation = True

        return {'FINISHED'}
########################################

########################################
#侵食
########################################
#bpy.ops.fujiwara_toolbox.perticle_setup_erosion() #侵食
class FUJIWARATOOLBOX_PERTICLE_SETUP_EROSION(bpy.types.Operator):
    """侵食"""
    bl_idname = "fujiwara_toolbox.perticle_setup_erosion"
    bl_label = "侵食"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PARTICLES",mode="")

    def execute(self, context):
        if not is_perticle_setup_executable(self):
            return {'CANCELLED'} 
        (psett, emod) = particle_setup_base(self)
        emod.show_alive = False

        return {'FINISHED'}
########################################

########################################
#破砕
########################################
#bpy.ops.fujiwara_toolbox.perticle_setup_crush() #破砕
class FUJIWARATOOLBOX_PERTICLE_SETUP_CRUSH(bpy.types.Operator):
    """破砕"""
    bl_idname = "fujiwara_toolbox.perticle_setup_crush"
    bl_label = "破砕"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="PARTICLES",mode="")

    def execute(self, context):
        if not is_perticle_setup_executable(self):
            return {'CANCELLED'} 
        (psett, emod) = particle_setup_base(self)
        psett.frame_start = 1
        psett.frame_end = 1
        psett.lifetime = 250
        psett.normal_factor = 0
        psett.factor_random = 0
        psett.use_rotations = True
        psett.use_dynamic_rotation = True
        psett.angular_velocity_factor = 1.0
        psett.effector_weights.gravity = 0
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#コンストレイント
########################################
class CATEGORYBUTTON_104280(bpy.types.Operator):
    """コンストレイント"""
    bl_idname = "fujiwara_toolbox.categorybutton_104280"
    bl_label = "コンストレイント"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("コンストレイント",True)
    uiitem.button(bl_idname,bl_label,icon="CONSTRAINT",mode="")
    uiitem.direction = "vertical"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("カメラトラッカ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def add_camtracker(axis, type="DAMPED_TRACK"):
    selection = fjw.get_selected_list()
    for obj in selection:
        cnstu = fjw.ConstraintUtils(obj)

        tracker = cnstu.find("FJW Camera Tracker")

        if tracker is None:
            tracker = cnstu.add("FJW Camera Tracker", type)
        
        tracker.track_axis = axis
        cam = bpy.context.scene.camera
        if cam is not None:
            tracker.target = cam
        correct_tracker_axis(obj)
    

########################################
#Z+
########################################
#bpy.ops.fujiwara_toolbox.set_camera_tracker_constraint_z() #Z+
class FUJIWARATOOLBOX_SET_CAMERA_TRACKER_CONSTRAINT_Z(bpy.types.Operator):
    """カメラをトラッキングするコンストレイントを追加する。"""
    bl_idname = "fujiwara_toolbox.set_camera_tracker_constraint_z"
    bl_label = "上面"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        add_camtracker("TRACK_Z")
        return {'FINISHED'}
########################################

########################################
#Y-
########################################
#bpy.ops.fujiwara_toolbox.set_camera_tracker_constraint_y() #Y-
class FUJIWARATOOLBOX_SET_CAMERA_TRACKER_CONSTRAINT_Y(bpy.types.Operator):
    """カメラをトラッキングするコンストレイントを追加する。"""
    bl_idname = "fujiwara_toolbox.set_camera_tracker_constraint_y"
    bl_label = "前面"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        add_camtracker("TRACK_NEGATIVE_Y")
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#軸固定　前面
########################################
#bpy.ops.fujiwara_toolbox.set_camera_tracker_constraint_yz() #軸固定　前面
class FUJIWARATOOLBOX_SET_CAMERA_TRACKER_CONSTRAINT_YZ(bpy.types.Operator):
    """軸固定トラックを設定する。Yを向けてZを固定する。"""
    bl_idname = "fujiwara_toolbox.set_camera_tracker_constraint_yz"
    bl_label = "軸固定　前面"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        add_camtracker("TRACK_NEGATIVE_Y", "LOCKED_TRACK")
        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ターゲットカメラ設定
########################################
#bpy.ops.fujiwara_toolbox.set_camtracker_target() #ターゲットカメラ設定
class FUJIWARATOOLBOX_SET_CAMTRACKER_TARGET(bpy.types.Operator):
    """カメラトラック用コンストレイントのターゲットを自動設定する。"""
    bl_idname = "fujiwara_toolbox.set_camtracker_target"
    bl_label = "ターゲットカメラ設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        cam = bpy.context.scene.camera
        if cam is None:
            return {'CANCELLED'}

        for obj in  bpy.context.visible_objects:
            cnstu = fjw.ConstraintUtils(obj)
            tracker = cnstu.find("FJW Camera Tracker")
            if tracker is not None:
                tracker.target = cam

            if obj.type == "ARMATURE":
                armu = fjw.ArmatureUtils(obj)
                for pbone in armu.pose_bones:
                    for bc in pbone.constraints:
                        if "FJW Camera Tracker" in bc.name:
                            bc.target = cam
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ターゲットトラッカ（カメラトラッカ併用）")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def correct_tracker_axis(obj):
    cnstru = fjw.ConstraintUtils(obj)
    ltracker = cnstru.find("FJW Target Tracker")
    if ltracker is None:
        return
    camtracker = cnstru.find("FJW Camera Tracker")

    if "Z" in camtracker.track_axis:
        ltracker.track_axis = ltracker.track_axis.replace("Z", "Y")
        ltracker.lock_axis = ltracker.lock_axis.replace("Y", "Z")
    if "Y" in camtracker.track_axis:
        ltracker.track_axis = ltracker.track_axis.replace("Y", "Z")
        ltracker.lock_axis = ltracker.lock_axis.replace("Z", "Y")
    
    

def set_target_tracker(positive=True):
    target = fjw.active()
    selection = fjw.get_selected_list()
    for obj in selection:
        if obj == target:
            continue

        cnstru = fjw.ConstraintUtils(obj)
        camtracker = cnstru.find("FJW Camera Tracker")

        if positive:
            track_axis = "TRACK_Z"
        else:
            track_axis = "TRACK_NEGATIVE_Z"
        lock_axis = "LOCK_Y"

        # if camtracker is not None:
        #     if camtracker.track_axis == "TRACK_Z":
        #         track_axis = track_axis.replace("Z", "Y")
        #         lock_axis = lock_axis.replace("Y", "Z")

        ltracker = cnstru.find("FJW Target Tracker")
        if ltracker is None:
            ltracker = cnstru.add("FJW Target Tracker","LOCKED_TRACK")
        ltracker.track_axis = track_axis
        ltracker.lock_axis = lock_axis
        ltracker.target = target

        correct_tracker_axis(obj)
    return

########################################
#上方向
########################################
#bpy.ops.fujiwara_toolbox.set_target_tracker_withcamtrack_top() #上方向
class FUJIWARATOOLBOX_SET_TARGET_TRACKER_WITHCAMTRACK_TOP(bpy.types.Operator):
    """アクティブオブジェクトをターゲットとして、カメラトラッカと併用するターゲットトラッカを設定する。"""
    bl_idname = "fujiwara_toolbox.set_target_tracker_withcamtrack_top"
    bl_label = "上方向"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        set_target_tracker(True)
        return {'FINISHED'}
########################################

########################################
#下方向
########################################
#bpy.ops.fujiwara_toolbox.set_target_tracker_withcamtrack_bottom() #下方向
class FUJIWARATOOLBOX_SET_TARGET_TRACKER_WITHCAMTRACK_BOTTOM(bpy.types.Operator):
    """アクティブオブジェクトをターゲットとして、カメラトラッカと併用するターゲットトラッカを設定する。"""
    bl_idname = "fujiwara_toolbox.set_target_tracker_withcamtrack_bottom"
    bl_label = "下方向"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        set_target_tracker(False)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






################################################################################
#UIカテゴリ
########################################
#MarvelousDesigner
########################################
class CATEGORYBUTTON_425599(bpy.types.Operator):#MarvelousDesigner
    """MarvelousDesigner"""
    bl_idname = "fujiwara_toolbox.categorybutton_425599"
    bl_label = "MarvelousDesigner"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("MarvelousDesigner",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

# import fujiwara_toolbox.modules.main.submodules.marvelousdesinger_utils
from fujiwara_toolbox_modules.modules.main.submodules.marvelousdesinger_utils import MarvelousDesingerUtils

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("オート")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#オートインポート
########################################
#bpy.ops.fujiwara_toolbox.mdresult_autoimport_only() #オートインポートのみ
class FUJIWARATOOLBOX_mdresult_autoimport_only(bpy.types.Operator):
    """オートインポート MarvelousDesigner7はデータが不正で読み込めないことがあるので注意。6.5推奨。"""
    bl_idname = "fujiwara_toolbox.mdresult_autoimport_only"
    bl_label = "オートインポート"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if "_MDWork" in bpy.data.filepath:
            self.report({"WARNING"}, str("_MDWork.blendでのインポートは無効です！元ファイルに戻ってください！"))
            return {"CANCELLED"}

        MarvelousDesingerUtils.mdresult_auto_import_main(self,context,False)
        return {'FINISHED'}
########################################

# ########################################
# #オートインポートしてアタッチ
# ########################################
# #bpy.ops.fujiwara_toolbox.mdresult_autoimport_and_attouch() #オートインポートしてアタッチ
# class FUJIWARATOOLBOX_MDRESULT_AUTOIMPORT_AND_ATTOUCH(bpy.types.Operator):
#     """漫画処理をアタッチする"""
#     bl_idname = "fujiwara_toolbox.mdresult_autoimport_and_attouch"
#     bl_label = "オートインポートしてアタッチ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         MarvelousDesingerUtils.mdresult_auto_import_main(self,context,True)
#         return {'FINISHED'}
# ########################################

# ########################################
# #オートインポートしてGLレンダ
# ########################################
# #bpy.ops.fujiwara_toolbox.mdresult_autoimport_and_glrender() #オートインポートしてGLレンダ
# class FUJIWARATOOLBOX_mdresult_autoimport_and_glrender(bpy.types.Operator):
#     """終了はしないでGLレンダする"""
#     bl_idname = "fujiwara_toolbox.mdresult_autoimport_and_glrender"
#     bl_label = "オートインポートしてGLレンダ"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         MarvelousDesingerUtils.mdresult_auto_import_main(self,context,True)
#         bpy.ops.fujiwara_toolbox.glrender()
#         return {'FINISHED'}
# ########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("MDWorkファイル")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#MD作業ファイル準備
########################################
class FUJIWARATOOLBOX_902822(bpy.types.Operator):#MD作業ファイル準備
    """Marvelous Designer作業用ファイル MDWork.blendを準備する。"""
    bl_idname = "fujiwara_toolbox.setup_mdwork_blend"
    bl_label = "MD作業ファイル準備"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.context.space_data.show_only_render = False
        bpy.ops.fujiwara_toolbox.command_700665()#subdiv2
        bpy.context.scene.layers = [True for i in range(20)]
        for obj in fjw.get_selected_list():
            fjw.get_root(obj).select = True
        selection = fjw.get_selected_list()
        fjw.deselect()
        fjw.select(selection)

        #選択オブジェクトを親子選択→反転削除
        bpy.ops.fujiwara_toolbox.command_24259()#親子選択
        #プロクシも選択
        for obj in bpy.context.scene.objects:
            if "proxy" in obj.name:
                obj.select = True
        bpy.ops.object.select_all(action='INVERT')
        if bpy.context.scene.camera:
            bpy.context.scene.camera.select = False
        selection = fjw.get_selected_list()
        fjw.delete(selection)
        MarvelousDesingerUtils.setup_mdwork_main(self,context)
        return {'FINISHED'}
########################################

########################################
#元を開く（別窓）
########################################
class FUJIWARATOOLBOX_179920(bpy.types.Operator):#元を開く（別窓）
    """元を開く（別窓）"""
    bl_idname = "fujiwara_toolbox.command_179920"
    bl_label = "元を開く（別窓）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        path = bpy.data.filepath.replace("_MDWork","")
        subprocess.Popen("EXPLORER " + path)
        return {'FINISHED'}
########################################


########################################
#戻る
########################################
class FUJIWARATOOLBOX_401078(bpy.types.Operator):#戻る
    """戻る"""
    bl_idname = "fujiwara_toolbox.return_from_mdwork"
    bl_label = "戻る"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="LOOP_BACK",mode="")


    def execute(self, context):
        if "_MDWork" in bpy.data.filepath:
            # path = bpy.data.filepath.replace("_MDWork","")
            # subprocess.Popen("EXPLORER " + path)
            # os.remove(bpy.data.filepath)
            # bpy.ops.wm.quit_blender()
            #終了しないでやってみる
            mdwork_path = bpy.data.filepath
            path = bpy.data.filepath.replace("_MDWork","")
            bpy.ops.wm.open_mainfile(filepath=path)

            os.remove(mdwork_path)

        return {'FINISHED'}
########################################

########################################
#終了
########################################
class FUJIWARATOOLBOX_628306(bpy.types.Operator):#終了
    """終了"""
    bl_idname = "fujiwara_toolbox.exit_mdwork"
    bl_label = "終了"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        if "_MDWork" in bpy.data.filepath:
            os.remove(bpy.data.filepath)
            bpy.ops.wm.quit_blender()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

# ########################################
# #選択物を全てシミュレート
# ########################################
# #bpy.ops.fujiwara_toolbox.md_sim_all() #全てシミュレート
# class FUJIWARATOOLBOX_MD_SIM_ALL(bpy.types.Operator):
#     """選択された全てのアバターをシミュレートさせる。通常はシミュレートして、ファイルを開き直す。MD作業ファイル上で実行すると、特に開き直さない。"""
#     bl_idname = "fujiwara_toolbox.md_sim_all"
#     bl_label = "選択物を全てシミュレート"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         back = False
#         if "_MDWork" not in bpy.data.filepath:
#             bpy.ops.fujiwara_toolbox.setup_mdwork_blend()
#             back = True

#         for obj in bpy.context.visible_objects:
#             obj.select = True
#         selection = fjw.get_selected_list()
#         MarvelousDesingerUtils.export_selected(True)
                
#         self.report({"INFO"},"シミュレート完了。")
#         if back:
#             bpy.ops.fujiwara_toolbox.return_from_mdwork()
#         return {'FINISHED'}
# ########################################

########################################
#エクスポート＆キュー
########################################
#bpy.ops.fujiwara_toolbox.md_exportonly() #エクスポートのみ
class FUJIWARATOOLBOX_MD_EXPORTONLY(bpy.types.Operator):
    """MarvelousDesignerでシミュレートするためのデータをエクスポートする。"""
    bl_idname = "fujiwara_toolbox.md_exportonly"
    bl_label = "エクスポート＆キュー"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        back = False
        if "_MDWork" not in bpy.data.filepath:
            bpy.ops.fujiwara_toolbox.setup_mdwork_blend()
            back = True

        for obj in bpy.context.visible_objects:
            obj.select = True
        selection = fjw.get_selected_list()
        MarvelousDesingerUtils.export_selected(False)

        self.report({"INFO"},"エクスポート完了。")
        if back:
            bpy.ops.fujiwara_toolbox.return_from_mdwork()

        self.report({"INFO"},"コマンド文字列をクリップボードにコピーしました。Marvelous Designerのスクリプト画面でペーストしてください。")
        bpy.context.window_manager.clipboard = 'exec("from fjwMDControl import *;run(mdsa)",globals(), locals())'
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("MD用オブジェクトセットアップ")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#衣装パスを追加
########################################
#bpy.ops.fujiwara_toolbox.add_garment_path() #衣装パスを追加
class FUJIWARATOOLBOX_MD_ADD_GARMENT_PATH(bpy.types.Operator):
    """リストに、衣装のパスを追加する。ルートオブジェクトが設定を保持する。"""
    bl_idname = "fujiwara_toolbox.md_add_garment_path"
    bl_label = "衣装パスを追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    """
    ファイルブラウザのフィルタ
    https://blender.stackexchange.com/questions/7890/add-a-filter-for-the-extension-of-a-file-in-the-file-browser
    https://blenderartists.org/forum/showthread.php?301263-Filter-filetype-on-open-select-dialog
    """

    filter_glob = StringProperty(default="*.zpac", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        self.directory = os.path.dirname(bpy.data.filepath)
        self.report({"INFO"}, "%s"%(self.directory))
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # self.report({"INFO"}, "%s, %s"%(self.directory,self.filename))
        if self.filename == "":
            return {"CANCELLED"}

        path = os.path.normpath(self.directory + os.sep + self.filename)
        path = bpy.path.relpath(path)

        active = fjw.active()
        if active is None:
            return {"CANCELLED"}

        #ルートにパス集めてもしかたない　リグとか再生成で消える
        # root = fjw.get_root(active)
        pathlist = []
        # if "md_garment_path_list" in root:
        #     pathlist = root["md_garment_path_list"]
        if "md_garment_path_list" in active:
             pathlist = active["md_garment_path_list"]

        if path not in pathlist:
            pathlist.append(path)

        # root["md_garment_path_list"] = pathlist
        active["md_garment_path_list"] = pathlist


        return {'FINISHED'}
########################################

########################################
#エクスポートIDを設定
########################################
#bpy.ops.fujiwara_toolbox.md_set_export_id() #エクスポートIDを設定
class FUJIWARATOOLBOX_MD_SET_EXPORT_ID(bpy.types.Operator):
    """選択オブジェクトのエクスポートIDを設定する。"""
    bl_idname = "fujiwara_toolbox.md_set_export_id"
    bl_label = "エクスポートIDを設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    export_id = IntProperty(
        name="Export ID",
        description="Export ID",
        default=0,
        min=0,
        max=255
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        active = fjw.active()
        #ルートにつけたらだめでしょ！
        # root = fjw.get_root(active)
        # root["md_export_id"] = self.export_id
        active["md_export_id"] = self.export_id
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("MD用オブジェクト運用設定")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#衣装インデックスの設定
########################################
#bpy.ops.fujiwara_toolbox.md_set_garment_index() #衣装インデックスの設定
class FUJIWARATOOLBOX_MD_SET_GARMENT_INDEX(bpy.types.Operator):
    """選択オブジェクトで実際に使用する衣装パスの番号を設定する。ルートオブジェクトが設定を保持する。"""
    bl_idname = "fujiwara_toolbox.md_set_garment_index"
    bl_label = "衣装インデックスの設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    garment_index = IntProperty(
        name="Garment Path Index",
        description="Garment Path Index",
        default=0,
        min=0,
        max=255
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        active = fjw.active()
        root = fjw.get_root(active)
        root["md_garment_index"] = self.garment_index
        return {'FINISHED'}
########################################

########################################
#エクスポート深度設定
########################################
#bpy.ops.fujiwara_toolbox.md_set_export_depth() #エクスポート深度設定
class FUJIWARATOOLBOX_MD_SET_EXPORT_DEPTH(bpy.types.Operator):
    """エクスポートIDの何番目までをエクスポートするか設定する。ルートオブジェクトが設定を保持する。"""
    bl_idname = "fujiwara_toolbox.md_set_export_depth"
    bl_label = "エクスポート深度設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    export_depth = IntProperty(
        name="Export Depth",
        description="Export Depth",
        default=0,
        min=0,
        max=255
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        active = fjw.active()
        root = fjw.get_root(active)
        root["md_export_depth"] = self.export_depth
        return {'FINISHED'}
########################################

########################################
#エクスポートID追加
########################################
#bpy.ops.fujiwara_toolbox.md_set_export_list() #エクスポート個別設定
class FUJIWARATOOLBOX_MD_SET_EXPORT_LIST(bpy.types.Operator):
    """エクスポートIDの何番をエクスポートするか設定する。ルートオブジェクトが設定を保持する。"""
    bl_idname = "fujiwara_toolbox.md_set_export_list"
    bl_label = "エクスポートID追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    export_depth = IntProperty(
        name="Export Depth",
        description="Export Depth",
        default=0,
        min=0,
        max=255
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        active = fjw.active()
        root = fjw.get_root(active)

        if "md_export_depth" in root:
            depth = root["md_export_depth"]
        else:
            depth = []
        if type(depth) != list:
            depth = [depth]
        if self.export_depth not in depth:
            depth.append(self.export_depth)
        
        root["md_export_depth"] = depth
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("設定消去など")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#選択物の設定を全て消去
########################################
#bpy.ops.fujiwara_toolbox.md_delete_all_settings() #選択物の設定を全て消去
class FUJIWARATOOLBOX_MD_DELETE_ALL_SETTINGS(bpy.types.Operator):
    """選択オブジェクトの設定を全て消去する。"""
    bl_idname = "fujiwara_toolbox.md_delete_all_settings"
    bl_label = "選択物の設定を全て消去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def delkey(self, obj, name):
        if name in obj:
            del obj[name]

    def execute(self, context):
        active = fjw.active()
        selection = fjw.get_selected_list()
        for obj in selection:
            root = fjw.get_root(obj)
            fjw.activate(root)
            bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
    
        selection = fjw.get_selected_list()
        for obj in selection:
            self.delkey(obj, "md_garment_path_list")
            self.delkey(obj, "md_export_id")
            self.delkey(obj, "md_garment_index")
            self.delkey(obj, "md_export_depth")

        return {'FINISHED'}
########################################

########################################
#キューをクリア
########################################
#bpy.ops.fujiwara_toolbox.md_clear_cuefolder() #キューをクリア
class FUJIWARATOOLBOX_MD_CLEAR_CUEFOLDER(bpy.types.Operator):
    """キューフォルダを空にする。"""
    bl_idname = "fujiwara_toolbox.md_clear_cuefolder"
    bl_label = "キューをクリア"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        MarvelousDesingerUtils.clear_cue_folder()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Marvelous Designer機能のためのセットアップ")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#使用スクリプトフォルダを開く
########################################
#bpy.ops.fujiwara_toolbox.open_md_script_folder() #使用スクリプトフォルダを開く
class FUJIWARATOOLBOX_OPEN_MD_SCRIPT_FOLDER(bpy.types.Operator):
    """このスクリプトをMarvelous Designerインストールディレクトリにコピーしてください。"""
    bl_idname = "fujiwara_toolbox.open_md_script_folder"
    bl_label = "使用スクリプトフォルダを開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        src_dir = os.path.dirname(fujiwara_toolbox.__file__)+ os.sep + "resources" + os.sep + "MarvelousDesignerResources"
        os.system("EXPLORER " + src_dir)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#テクスチャ
########################################
class CATEGORYBUTTON_81935(bpy.types.Operator):#Substance/テクスチャ
    """テクスチャ"""
    bl_idname = "fujiwara_toolbox.categorybutton_81935"
    bl_label = "テクスチャ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("テクスチャ",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#テクスチャ更新
########################################
#bpy.ops.fujiwara_toolbox.reload_images() #テクスチャ更新
class FUJIWARATOOLBOX_RELOAD_IMAGES(bpy.types.Operator):
    """テクスチャを再読み込みする"""
    bl_idname = "fujiwara_toolbox.reload_images"
    bl_label = "テクスチャ更新"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for img in bpy.data.images:
            img.reload()
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#ベイク用リメッシュ生成
########################################
#bpy.ops.fujiwara_toolbox.gen_remeshed_model() #ベイク用リメッシュ生成
class FUJIWARATOOLBOX_GEN_REMESHED_MODEL(bpy.types.Operator):
    """ベイク先用にリメッシュ・ポリゴン数削減・マテリアル除去したモデルを生成する。"""
    bl_idname = "fujiwara_toolbox.gen_remeshed_model"
    bl_label = "ベイク用リメッシュ生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        fjw.deselect()
        fjw.activate(obj)
        bpy.ops.object.duplicate()
        obj = fjw.active()
        modu = fjw.Modutils(obj)
        m = modu.add("Remesh", "REMESH")
        m.use_remove_disconnected = False
        m.mode = 'SMOOTH'
        m.octree_depth = 7
        m.use_smooth_shade = True
        m = modu.add("Decimate", "DECIMATE")
        m.ratio = 0.1

        obj.data.materials.clear()
        # for mod in modu.mods:
        #     modu.apply(mod)

        return {'FINISHED'}
########################################
########################################
#リンク切れテクスチャを削除
########################################
#bpy.ops.fujiwara_toolbox.disable_textures_img_not_found() #リンク切れテクスチャを無効化
class FUJIWARATOOLBOX_disable_textures_img_not_found(bpy.types.Operator):
    """リンク切れテクスチャを削除する。"""
    bl_idname = "fujiwara_toolbox.disable_textures_img_not_found"
    bl_label = "リンク切れテクスチャを削除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for texture in bpy.data.textures:
            image = texture.image
            if image is not None:
                if image.resolution == Vector((0,0)):
                    bpy.data.textures.remove(texture,True)

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("選択からアクティブにベイク")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
def sbsname(basename):
    return basename.replace(".","_")

#def use_textures(obj,flag):
#    for mat in obj.data.materials:
#        for index,use_texture in mat.use_textures:
#            mat.use_textures[index] = flag


tex_identifiers = {}

"""
tex_identifiers[""] = 
"""
tex_identifiers["color"] = "_baseColor|_color|_diffuse|_fullrender"
tex_identifiers["modelinfo"] = "_curvature|_ambient_occlusion"
tex_identifiers["alpha"] = "_Alpha"
tex_identifiers["height"] = "_Height|_Normal"
tex_identifiers["ao"] = "_AO|_ambient_occlusion"
tex_identifiers["metallic"] = "_metallic"
tex_identifiers["roughness"] = "_roughness"
tex_identifiers["shadow"] = "_Shadow"

tex_identifiers_all = ""
for tex_identifier in tex_identifiers:
    tex_identifiers_all += tex_identifiers[tex_identifier] + "|"



def remove_tex_identifier(name):
    global tex_identifiers_all
    name = re.sub(tex_identifiers_all,"",name,0,re.IGNORECASE)
    return name

def get_texname(filepath):
    name = os.path.basename(filepath)
    name,ext = os.path.splitext(name)
    name = remove_tex_identifier(name)
    return name

def saveall_dirtyimages():
    for img in bpy.data.images:
        if img.is_dirty:
            if img.filepath == "":
                dir = os.path.dirname(bpy.data.filepath)
                name = get_texname(img.name)
                imgdir = dir + os.sep + name + "_textures" + os.sep
                if not os.path.exists(imgdir):
                    os.makedirs(imgdir)
                img.filepath = imgdir + img.name
            img.save()


zero_transp_mat = None
def get_zero_transp_mat():
    global zero_transp_mat
    if zero_transp_mat is None:
        zero_transp_mat = bpy.data.materials.new("zero_transp_mat")
    zero_transp_mat.use_raytrace = False
    zero_transp_mat.use_transparency = True
    #完全にゼロだとターゲットがないといわれてしまう
    zero_transp_mat.alpha = 1e-009
    zero_transp_mat.specular_alpha = 1e-009
    return zero_transp_mat

#type:
#https://docs.blender.org/api/blender_python_api_2_78c_release/bpy.types.RenderSettings.html#bpy.types.RenderSettings.bake_type
def texture_bake(filepath, size, type, identifier):
    filename = os.path.basename(filepath)
    bakeobj = fjw.active()


    if filename in bpy.data.images:
        imgtobake = bpy.data.images[filename]
        imgtobake.scale(size,size)
    else:
        imgtobake = bpy.data.images.new(filename,size,size,True)

    #もしかしてここで一回imgを保存する必要がある？→正解！
    #imageはいじくる前にかならずsaveしないといけない！
    saveall_dirtyimages()

    #self.report({"INFO"},"image to bake:"+imgtobake.name)

    for uvface in bakeobj.data.uv_textures.active.data:
        uvface.image = imgtobake
    bakeobj.data.update()

    bpy.context.scene.render.bake_type = type
    bpy.context.scene.render.use_bake_selected_to_active = True
    bpy.context.scene.render.use_textures = True


    bpy.ops.object.bake_image()
    saveall_dirtyimages()




def bake_setup():
    #returns objname, bakedir
        
    bpy.ops.fujiwara_toolbox.command_998634()#無マテリアルに白を割り当て
    bakeobj = fjw.active()

    #複製されてることを考慮して一旦マテリアルを外す
    bakeobj.data.materials.clear()
    #ベイク先オブジェクトを透明にしておく
    bakeobj.data.materials.append(get_zero_transp_mat())

    objname = sbsname(bakeobj.name)
    bakedir = os.path.dirname(bpy.data.filepath) + os.sep + objname + "_textures" + os.sep

    #UV展開
    if len(bakeobj.data.uv_textures) == 0:
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        fjw.mode("OBJECT")

    return objname, bakedir

def bake_finish():
    #透明マテリアルのクリア
    fjw.active().data.materials.clear()

    bpy.ops.fujiwara_toolbox.substance_collect_textures()#テクスチャ回収

    fjw.deselect()
    fjw.active().select = True


def autobake(size,type,identifier):
    objname,bakedir = bake_setup()
    bakepath = bakedir + objname + "_" + identifier + ".png"
    texture_bake(bakepath,size,type,identifier)

def bake_ModelAppearance(size):
    bpy.context.scene.render.bake_distance = 0
    bpy.context.scene.render.bake_bias = 0.001
    bpy.context.scene.render.bake_margin = 16
    bpy.context.scene.render.use_bake_clear = True
    bpy.context.scene.render.use_bake_to_vertex_color = False
    bpy.context.scene.render.bake_quad_split = 'AUTO'

    autobake(size,"TEXTURE","baseColor")
    autobake(size,"DISPLACEMENT","Height")
    autobake(size,"NORMALS","Normal")

    bake_finish()

########################################
#512
########################################
#bpy.ops.fujiwara_toolbox.command_924014() #512
class FUJIWARATOOLBOX_COMMAND_924014(bpy.types.Operator):
    """512"""
    bl_idname = "fujiwara_toolbox.command_924014"
    bl_label = "512"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        res = 512
        tbaker = TextureBaker(fjw.active(),fjw.get_selected_list(),res,res)
        tbaker.bake("TEXTURE")
        tbaker.bake("NORMALS")
        tbaker.bake("DISPLACEMENT")

        return {'FINISHED'}
########################################

########################################
#1024
########################################
#bpy.ops.fujiwara_toolbox.command_933282() #1024
class FUJIWARATOOLBOX_COMMAND_933282(bpy.types.Operator):
    """1024"""
    bl_idname = "fujiwara_toolbox.command_933282"
    bl_label = "1024"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        res = 1024
        tbaker = TextureBaker(fjw.active(),fjw.get_selected_list(),res,res)
        tbaker.bake("TEXTURE")
        tbaker.bake("NORMALS")
        tbaker.bake("DISPLACEMENT")

        return {'FINISHED'}
########################################

########################################
#2048
########################################
class FUJIWARATOOLBOX_458089(bpy.types.Operator):#2048
    """2048*2048px"""
    bl_idname = "fujiwara_toolbox.command_458089"
    bl_label = "2048"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        # bake_ModelAppearance(2048)

        res = 1024*2
        tbaker = TextureBaker(fjw.active(),fjw.get_selected_list(),res,res)
        tbaker.bake("TEXTURE")
        tbaker.bake("NORMALS")
        tbaker.bake("DISPLACEMENT")

        return {'FINISHED'}
########################################

########################################
#4096
########################################
#bpy.ops.fujiwara_toolbox.command_264050() #4096
class FUJIWARATOOLBOX_264050(bpy.types.Operator):#4096
    """4096*4096px"""
    bl_idname = "fujiwara_toolbox.command_264050"
    bl_label = "4096"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        res = 1024*4
        tbaker = TextureBaker(fjw.active(),fjw.get_selected_list(),res,res)
        tbaker.bake("TEXTURE")
        tbaker.bake("NORMALS")
        tbaker.bake("DISPLACEMENT")
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

# ############################################################################################################################
# uiitem("アルファをベイク")
# ############################################################################################################################
# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------
# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------

# def bake_alpha(size):
#     bpy.context.scene.render.bake_distance = 0
#     bpy.context.scene.render.bake_bias = 0.001
#     bpy.context.scene.render.bake_margin = 16
#     bpy.context.scene.render.use_bake_clear = True
#     bpy.context.scene.render.use_bake_to_vertex_color = False
#     bpy.context.scene.render.bake_quad_split = 'AUTO'
    
#     #アルファの場合、透過マテリアルを設定しないといけないので
#     #auto bakeをそのまま使用できない
#     objname,bakedir = bake_setup()
#     bakepath = bakedir + objname + "_" + "Alpha" + ".png"

#     #透過マテリアルの割当
#     alphamat = fjw.get_material("alpha_zero")
#     alphamat.use_transparency = True
#     alphamat.alpha = 0

#     fjw.active().data.materials.append(alphamat)
#     texture_bake(bakepath,size,"ALPHA","Alpha")
#     fjw.active().data.materials.clear()

#     bpy.ops.fujiwara_toolbox.substance_collect_textures()#テクスチャ回収

# ########################################
# #2048
# ########################################
# #bpy.ops.fjw.bake_alpha_2048() #2048
# class FUJIWARATOOLBOX_bake_alpha_2048(bpy.types.Operator):
#     """選択物のアルファをアクティブにベイクする。2048px。"""
#     bl_idname = "fujiwara_toolbox.bake_alpha_2048"
#     bl_label = "2048"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         bake_alpha(2048)
#         return {'FINISHED'}
# ########################################

# ########################################
# #4096
# ########################################
# #bpy.ops.fjw.bake_alpha_4096() #4096
# class FUJIWARATOOLBOX_bake_alpha_4096(bpy.types.Operator):
#     """選択物のアルファをアクティブにベイクする。4096px。"""
#     bl_idname = "fujiwara_toolbox.bake_alpha_4096"
#     bl_label = "4096"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         bake_alpha(4096)
#         return {'FINISHED'}
# ########################################












#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("影をベイク")
############################################################################################################################
def set_sun_shadow(value):
    for lamp in bpy.data.lamps:
        if lamp.type == "SUN":
            lamp.use_shadow = value

def bake_shadow(size):
    bpy.context.scene.render.bake_distance = 0.001
    bpy.context.scene.render.bake_bias = 0.001
    bpy.context.scene.render.bake_margin = 16
    bpy.context.scene.render.use_bake_clear = True
    bpy.context.scene.render.use_bake_to_vertex_color = False
    bpy.context.scene.render.bake_quad_split = 'AUTO'

    set_sun_shadow(True)

    autobake(size,"SHADOW","Shadow")

    set_sun_shadow(False)

    bpy.ops.fujiwara_toolbox.substance_collect_textures()#テクスチャ回収
    fjw.deselect()
    fjw.active().select = True

    pass

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#512
########################################
#bpy.ops.fujiwara_toolbox.command_401784() #512
class FUJIWARATOOLBOX_401784(bpy.types.Operator):#512
    """512"""
    bl_idname = "fujiwara_toolbox.command_401784"
    bl_label = "512"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bake_shadow(512)
        return {'FINISHED'}
########################################

########################################
#1024
########################################
#bpy.ops.fujiwara_toolbox.command_442748() #1024
class FUJIWARATOOLBOX_442748(bpy.types.Operator):#1024
    """1024"""
    bl_idname = "fujiwara_toolbox.command_442748"
    bl_label = "1024"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bake_shadow(1024)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("フルレンダをベイク")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def bake_fullrender(size):
    bpy.context.scene.render.bake_distance = 0
    bpy.context.scene.render.bake_bias = 0.001
    bpy.context.scene.render.bake_margin = 16
    bpy.context.scene.render.use_bake_clear = True
    bpy.context.scene.render.use_bake_to_vertex_color = False
    bpy.context.scene.render.bake_quad_split = 'AUTO'
    autobake(size,"FULL","FullRender")
    bake_finish()


########################################
#2048
########################################
#bpy.ops.fjw.bake_fullrender_2048() #2048
class FUJIWARATOOLBOX_bake_fullrender_2048(bpy.types.Operator):
    """フルレンダをベイクする。"""
    bl_idname = "fujiwara_toolbox.bake_fullrender_2048"
    bl_label = "2048"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        size = 2048
        bake_fullrender(size)
        return {'FINISHED'}
########################################

########################################
#4096
########################################
#bpy.ops.fjw.bake_fullrender_4096() #4096
class FUJIWARATOOLBOX_bake_fullrender_4096(bpy.types.Operator):
    """フルレンダをベイクする。"""
    bl_idname = "fujiwara_toolbox.bake_fullrender_4096"
    bl_label = "4096"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        size = 4096
        bake_fullrender(size)
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("調整")
############################################################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
def settexdepth(value,objects):
    for obj in objects:
        for mat in obj.data.materials:
            for texture_slot in mat.texture_slots:
                if texture_slot is None:
                    continue
                if re.search("_Height", texture_slot.texture.name,re.IGNORECASE) is not None or re.search("_Normals", texture_slot.texture.name,re.IGNORECASE) is not None:
                    texture_slot.normal_factor = value


########################################
#デプス0.01
########################################
class FUJIWARATOOLBOX_819234(bpy.types.Operator):#デプス0.01
    """デプス0.01"""
    bl_idname = "fujiwara_toolbox.command_819234"
    bl_label = "デプス0.01"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        settexdepth(0.01,fjw.get_selected_list())
        
        return {'FINISHED'}
########################################

########################################
#デプス1
########################################
class FUJIWARATOOLBOX_73453(bpy.types.Operator):#デプス1
    """デプス1"""
    bl_idname = "fujiwara_toolbox.command_73453"
    bl_label = "1"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        settexdepth(1,fjw.get_selected_list())
        return {'FINISHED'}
########################################

########################################
#デプス5
########################################
class FUJIWARATOOLBOX_997104(bpy.types.Operator):#デプス5
    """デプス5"""
    bl_idname = "fujiwara_toolbox.command_997104"
    bl_label = "5"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        settexdepth(5,fjw.get_selected_list())
        
        return {'FINISHED'}
########################################






#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("プロジェクション")
############################################################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

from fujiwara_toolbox_modules.modules.main.submodules.projection_tools import ProjectionUtils, ProjectionTools, FaceSetupTools
    

########################################
#アクティブマテリアルに
########################################
#bpy.ops.fujiwara_toolbox.load_img_projector() #アクティブマテリアルに
class FUJIWARATOOLBOX_LOAD_IMG_PROJECTOR(bpy.types.Operator):
    """画像をロードしてUV投影する。オブジェクトモード時：アクティブマテリアルにテクスチャを追加していく。編集モード：選択メッシュに新規マテリアルとして割り当てる。"""
    bl_idname = "fujiwara_toolbox.load_img_projector"
    bl_label = "アクティブマテリアルに"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    # filter_glob = StringProperty(default="*.png", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        obj = fjw.active()
        if not obj or obj.type != "MESH":
            self.report({"INFO"}, "メッシュオブジェクトを選択してください。")
            return {"CANCCELED"}

        self.directory = os.path.dirname(bpy.data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        prju = ProjectionUtils(self.filepath)
        prju.execute()

        return {'FINISHED'}
########################################

########################################
#オブジェクトの全てのマテリアルに
########################################
#bpy.ops.fujiwara_toolbox.load_img_projector_to_allobjmat() #オブジェクトの全てのマテリアルに
class FUJIWARATOOLBOX_LOAD_IMG_PROJECTOR_TO_ALLOBJMAT(bpy.types.Operator):
    """選択マテリアルにプロジェクションテクスチャを追加する。"""
    bl_idname = "fujiwara_toolbox.load_img_projector_to_allobjmat"
    bl_label = "オブジェクトの全てのマテリアルに"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    # filter_glob = StringProperty(default="*.png", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        obj = fjw.active()
        if not obj or obj.type != "MESH":
            self.report({"INFO"}, "メッシュオブジェクトを選択してください。")
            return {"CANCCELED"}

        self.directory = os.path.dirname(bpy.data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        prju = ProjectionUtils(self.filepath)
        prju.execute(to_active_mat=False)

        return {'FINISHED'}
########################################








########################################
#アクティブカメラでプロジェクション
########################################
#bpy.ops.fujiwara_toolbox.projection_with_active_camera() #アクティブカメラでプロジェクション
class FUJIWARATOOLBOX_PROJECTION_WITH_ACTIVE_CAMERA(bpy.types.Operator):
    """画像をロードして、アクティブカメラでプロジェクションする。"""
    bl_idname = "fujiwara_toolbox.projection_with_active_camera"
    bl_label = "アクティブカメラでプロジェクション"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    # filter_glob = StringProperty(default="*.png", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        obj = fjw.active()
        if not obj or obj.type != "MESH":
            self.report({"INFO"}, "メッシュオブジェクトを選択してください。")
            return {"CANCCELED"}


        self.directory = os.path.dirname(bpy.data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        prju = ProjectionUtils(self.filepath)
        prju.execute(use_active_camera = True)
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#アクティブオブジェクトをプロジェクタとして追加
########################################
#bpy.ops.fujiwara_toolbox.set_activeobject_to_projector() #アクティブオブジェクトでプロジェクション
class FUJIWARATOOLBOX_SET_ACTIVEOBJECT_TO_PROJECTOR(bpy.types.Operator):
    """アクティブオブジェクトをプロジェクタとして追加。"""
    bl_idname = "fujiwara_toolbox.set_activeobject_to_projector"
    bl_label = "アクティブオブジェクトをプロジェクタとして追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        projector = fjw.active()
        projector.select = False
        selection = fjw.get_selected_list()

        filepath = projector.active_material.active_texture.image.filepath
        prju = ProjectionUtils(filepath)
        prju.set_projector_to_objects(projector, selection)
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("テクスチャ作業")
############################################################################################################################
from fujiwara_toolbox_modules.modules.main.submodules.texture_working_tools import TextureWorkingTools




# #---------------------------------------------
# uiitem().vertical()
# #---------------------------------------------
# #---------------------------------------------
# uiitem().horizontal()
# #---------------------------------------------

# ########################################
# #テクスチャ作業ファイル作成
# ########################################
# #bpy.ops.fujiwara_toolbox.make_texture_workfile() #テクスチャ作業ファイル作成
# class FUJIWARATOOLBOX_MAKE_TEXTURE_WORKFILE(bpy.types.Operator):
#     """テクスチャ作業ファイル作成"""
#     bl_idname = "fujiwara_toolbox.make_texture_workfile"
#     bl_label = "テクスチャ作業ファイル作成"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         TextureWorkingTools.make_texture_workingfile(fjw.active(), "projector")
#         return {'FINISHED'}
# ########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#UV書き出し
########################################
#bpy.ops.fujiwara_toolbox.fjw_texture_export_uvmap() #UV書き出し
class FUJIWARATOOLBOX_FJW_TEXTURE_EXPORT_UVMAP(bpy.types.Operator):
    """UVを書き出す。"""
    bl_idname = "fujiwara_toolbox.fjw_texture_export_uvmap"
    bl_label = "UV書き出し"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        # 書き出し先ファイルが既にあったらそれを開く、ってしないとダメでは
        TextureWorkingTools.fjw_texture_export_uvmap(fjw.active())
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
from fujiwara_toolbox_modules.modules.main.submodules.texture_baking_utils import TextureBaker

########################################
#ベイク
########################################
#bpy.ops.fujiwara_toolbox.fjw_bake() #ベイク
class FUJIWARATOOLBOX_FJW_BAKE(bpy.types.Operator):
    """テクスチャ、ノーマルをベイク"""
    bl_idname = "fujiwara_toolbox.fjw_bake"
    bl_label = "ベイク"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if "uv_map" not in bpy.context.scene.objects:
            self.report({"INFO"}, "対象ファイルが存在しません")
            return {"CANCELLED"}

        tex_obj = bpy.context.scene.objects["uv_map"]
        tex_obj.hide = False
        fjw.activate(tex_obj)

        res = 1024*2
        tbaker = TextureBaker(tex_obj,fjw.get_selected_list(),res,res)
        tbaker.bake("TEXTURE")
        tbaker.bake("NORMALS")
        # tbaker.bake("SPEC_INTENSITY")
        # tbaker.bake("SPEC_COLOR")
        tbaker.bake("DISPLACEMENT")
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#戻ってテクスチャ回収
########################################
#bpy.ops.fujiwara_toolbox.collect_fjw_texture() #戻ってテクスチャ回収
class FUJIWARATOOLBOX_COLLECT_FJW_TEXTURE(bpy.types.Operator):
    """元ファイルに戻ってテクスチャを回収する"""
    bl_idname = "fujiwara_toolbox.collect_fjw_texture"
    bl_label = "戻ってテクスチャ回収"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        TextureWorkingTools.return_to_basefile()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem(" ")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#既存テクスチャをアサイン
########################################
#bpy.ops.fujiwara_toolbox.assign_existing_textures() #既存テクスチャをアサイン
class FUJIWARATOOLBOX_ASSIGN_EXISTING_TEXTURES(bpy.types.Operator):
    """選択ファイル・フォルダのテクスチャをアサインする。"""
    bl_idname = "fujiwara_toolbox.assign_existing_textures"
    bl_label = "既存テクスチャをアサイン"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filter_glob = StringProperty(default="*.png", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        if bpy.data.filepath != "":
            self.directory = os.path.dirname(bpy.data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        extlist = [".png"]
        result_path_list = []
        print(self.directory)
        print(self.filepath)
        print(self.files)
        for file in self.files:
            # print(file)
            name, ext = os.path.splitext(file.name)
            if ext in extlist:
                path = self.directory + file.name
                result_path_list.append(path)

        tbaker = TextureBaker(fjw.active(), [])
        for path in result_path_list:
            tbaker.assign_image(path)

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


############################################################################################################################
uiitem("便利")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#アルファでメッシュをカットオフする
########################################
#bpy.ops.fujiwara_toolbox.cutoff_mesh_by_alpha() #アルファでメッシュをカットオフする
class FUJIWARATOOLBOX_CUTOFF_MESH_BY_ALPHA(bpy.types.Operator):
    """アサインされているテクスチャのアルファ値でメッシュを刈り込む。Subsurf推奨。"""
    bl_idname = "fujiwara_toolbox.cutoff_mesh_by_alpha"
    bl_label = "アルファでメッシュをカットオフする"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        #だめだったらどっかでとまるからデータ決め打ち
        obj = fjw.active()
        mat = obj.data.materials[0]
        tex = mat.texture_slots[0].texture

        vgu = fjw.VertexGroupUtils(obj)
        vg = vgu.get_group("TextureMask")

        modu = fjw.Modutils(obj)
        m = modu.add("VertexWeightMix", "VERTEX_WEIGHT_MIX")
        m.vertex_group_a = vg.name
        m.default_weight_a = 1
        m.mix_set = 'ALL'
        m.mask_texture = tex
        m.mask_tex_mapping = 'UV'
        m.mask_tex_use_channel = 'ALPHA'

        m = modu.add("Mask", "MASK")
        m.vertex_group = vg.name
        m.invert_vertex_group = True

        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






################################################################################
#UIカテゴリ
########################################
#Substance
########################################
class CATEGORYBUTTON_376537(bpy.types.Operator):
    """Substance"""
    bl_idname = "fujiwara_toolbox.categorybutton_376537"
    bl_label = "Substance"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("Substance",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Substance")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def substance_output(obj, copy_sbstemplate=True, show_explorer=True):
    """
    Substance用にobjをアウトプットする。
    出力ディレクトリと出力名を返す。
    """
    scrdir = os.path.dirname(__file__)
    sbssourcepath = fjw.get_resourcesdir() + "EMPTY.sbs"

    dir = os.path.dirname(bpy.data.filepath)
    name = sbsname(obj.name)
    # imgdir = dir + os.sep + "textures" + os.sep + name + "_textures" + os.sep
    imgdir = dir + os.sep + "textures" + os.sep + name + os.sep + "sbswork" + os.sep
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)

    if copy_sbstemplate:
        #sbsファイルのコピー あったらしない
        sbsdestpath = imgdir + name + ".sbs"
        if not os.path.exists(sbsdestpath):
            shutil.copyfile(sbssourcepath, sbsdestpath)
    fjw.deselect()
    fjw.activate(obj)
    if len(obj.data.uv_textures) == 0:
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        fjw.mode("OBJECT")

    bpy.ops.export_scene.obj(filepath=imgdir + name + ".obj",check_existing=False,use_selection=True,use_mesh_modifiers=True)
    #出力フォルダを開く
    if show_explorer:
        os.system("EXPLORER " + imgdir)
    
    return imgdir, name

########################################
#Substance Output
########################################
class FUJIWARATOOLBOX_596924(bpy.types.Operator):#Substance Output
    """Substance Output"""
    bl_idname = "fujiwara_toolbox.command_596924"
    bl_label = "Substance Output"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):

        fjw.reject_notmesh()
        for obj in fjw.get_selected_list():
            #substance上で.が_に変換されて都合が悪いので除去しておく
            #obj.name = obj.name.replace(".","")
            substance_output(obj)

        return {'FINISHED'}
########################################

########################################
#選択メッシュを分離してSubstance Output
########################################
class FUJIWARATOOLBOX_539212(bpy.types.Operator):#分離してSubstance Output
    """選択メッシュを分離してSubstance Output"""
    bl_idname = "fujiwara_toolbox.command_539212"
    bl_label = "分離してSubstance Output"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.deselect()
        bpy.ops.mesh.separate(type='SELECTED')
        fjw.mode("OBJECT")

        bpy.ops.fujiwara_toolbox.command_339338()#スマートUV投影（各選択物）

        for obj in fjw.get_selected_list():
            mat = bpy.data.materials.new(name=sbsname(obj.name))#substanceとの連携用にオブジェクト名でマテリアル作る
            mat.diffuse_color = (1,1,1)
            if len(obj.material_slots) == 0:
                obj.data.materials.append(mat)
            else:
                obj.material_slots[0].material = mat
        
        bpy.ops.fujiwara_toolbox.command_596924()#Substance Output

        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#テクスチャ回収
########################################
#bpy.ops.fujiwara_toolbox.substance_collect_textures() #テクスチャ回収
class FUJIWARATOOLBOX_SUBSTANCE_COLLECT_TEXTURES(bpy.types.Operator):
    """テクスチャ回収"""
    bl_idname = "fujiwara_toolbox.substance_collect_textures"
    bl_label = "テクスチャ回収"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def socket_name(self, tex_name):
        tex_name = tex_name.replace(".png", "")
        identifier = tex_name.split("_")[-1]
        dic = {
            "Metallic":["Metallic"],
            "Roughness":["Roughness"],
            "Normal":["Normal", "NORMALS"],
            "Base Color":["Base Color", "BaseColor", "TEXTURES"],
            "Displacement":["Height", "DISPLACEMENT"]
        }

        for key in dic:
            if identifier in dic[key]:
                return key
        return None

    def execute(self, context):
        self_dir = os.path.dirname(bpy.data.filepath)
        textures_dir = self_dir + os.path.sep + "textures"

        bpy.ops.fujiwara_toolbox.command_998634()#無マテリアルに白を割り当て

        for matname in os.listdir(textures_dir):
            matdir_path = textures_dir + os.path.sep + matname
            if not os.path.isdir(matdir_path):
                continue
            
            mat = fjw.material(matname, bpy.context.selected_objects)
            if mat is None:
                continue
            
            nb = fjw.NodeBuilder(mat)
            nb.clear()
            shader_node = nb.node("ShaderNodeBsdfPrincipled")
            nb.link(shader_node.outputs["BSDF"],nb.node("ShaderNodeOutputMaterial").inputs["Surface"])
            
            for file in os.listdir(matdir_path):
                filepath = matdir_path + os.sep + file
                if not os.path.isfile(filepath):
                    continue
                
                img_node = nb.node("ShaderNodeTexImage", True)
                img_node.image = bpy.data.images.load(filepath=filepath)
                socket = self.socket_name(file)
                if socket is not None:
                    if socket == "Base Color":
                        img_node.color_space = "COLOR"
                    else:
                        img_node.color_space = "NONE"
                    
                    if socket == "Displacement":
                        nb.link(img_node.outputs["Color"], nb.node("ShaderNodeOutputMaterial").inputs[socket])
                    else:
                        nb.link(img_node.outputs["Color"], shader_node.inputs[socket])

            nb.layout()

        return {'FINISHED'}
########################################






# ########################################
# #テクスチャ回収
# ########################################
# class FUJIWARATOOLBOX_358608(bpy.types.Operator):#テクスチャ回収
#     """テクスチャ回収"""
#     bl_idname = "fujiwara_toolbox.substance_collect_textures"
#     bl_label = "テクスチャ回収"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")


#     def execute(self, context):
#         global tex_identifiers
#         basedir = os.path.dirname(bpy.data.filepath)
#         texfiles = []

#         bpy.ops.fujiwara_toolbox.command_998634()#無マテリアルに白を割り当て

#         #テクスチャピックアップ
#         for dirpath, dirs, files in os.walk(basedir):
#             for file in files:
#                 name,ext = os.path.splitext(file)
#                 if re.search("bmp|png|jpg|jpeg", ext, re.IGNORECASE) is not None:
#                     texfiles.append(dirpath + os.sep + file)

#         images = []
#         for texfile in texfiles:
#             self.report({"INFO"},texfile)
#             #Substanceのモデル情報はスルー
#             if re.search(tex_identifiers["modelinfo"], texfile,re.IGNORECASE) is not None:
#             #if re.search("_curvature", texfile,re.IGNORECASE) is not None:
#                 continue
#             images.append(fjw.load_img(texfile))

#         #basecolor類がはじめになるように並べ替える
#         tmp = []
#         for image in images:
#             if re.search(tex_identifiers["color"], image.name,re.IGNORECASE) is not None:
#                 tmp.append(image)
#                 images.remove(image)
#         #残りを足す
#         tmp.extend(images)
#         images = tmp

#         new_mats = []
#         for image in images:
#             texname, ext = os.path.splitext(image.name)

#             #テクスチャが存在する場合は既にマテリアル設定とかしてるはずなのでスルー
#             if texname in bpy.data.textures:
#                 continue

#             tex = bpy.data.textures.new(texname, "IMAGE")
#             tex.image = image

            
#             if "_textures" in image.filepath:
#                 #1オブジェクト1マテリアルにしたい。フォルダ名から作る。
#                 imgdir = os.path.dirname(image.filepath)
#                 imgdirname = os.path.basename(imgdir)
#                 matname = imgdirname.replace("_textures", "")
#             else:
#                 #Substance的命名規則で名前を得る
#                 #matname = texname.split("_")[0]
#                 #identifier=最後の_hogeを除去したものが名前
#                 matname = re.sub("_[a-zA-Z]+$", "", texname)
                

#             mat = fjw.get_material(matname)
#             new_mats.append(mat)

#             if len(mat.texture_slots) >= 17:
#                 continue

#             texture_slot = mat.texture_slots.add()
#             texture_slot.texture = tex

#             if re.search(tex_identifiers["color"], tex.name,re.IGNORECASE) is not None:
#                 texture_slot.use_map_color_diffuse = True
#                 texture_slot.diffuse_color_factor = 1
#                 texture_slot.use_map_alpha = True
#                 texture_slot.blend_type = 'MULTIPLY'
#                 mat.use_transparency = True
#                 mat.alpha = 1
#             if re.search(tex_identifiers["alpha"], tex.name,re.IGNORECASE) is not None:
#                 texture_slot.use_map_color_diffuse = False
#                 texture_slot.use_map_alpha = True
#                 texture_slot.use_rgb_to_intensity = True
#                 texture_slot.alpha_factor = 1
#                 texture_slot.blend_type = 'MIX'
#                 mat.use_transparency = True
#                 mat.alpha = 0
#             if re.search(tex_identifiers["height"], tex.name,re.IGNORECASE) is not None:
#                 texture_slot.use_map_color_diffuse = False
#                 texture_slot.use_map_normal = True
#                 texture_slot.normal_factor = 0.01
#             if re.search(tex_identifiers["ao"], tex.name,re.IGNORECASE) is not None:
#                 texture_slot.use_map_color_diffuse = True
#                 texture_slot.diffuse_color_factor = 1
#                 texture_slot.blend_type = 'MULTIPLY'
#             if re.search(tex_identifiers["metallic"], tex.name,re.IGNORECASE) is not None:
#                 texture_slot.use_map_color_diffuse = False
#                 texture_slot.use_map_hardness = True
#                 texture_slot.hardness_factor = 1
#             if re.search(tex_identifiers["roughness"], tex.name,re.IGNORECASE) is not None:
#                 texture_slot.use_map_color_diffuse = False
#                 texture_slot.use_map_specular = True
#                 texture_slot.specular_factor = 1
#             if re.search(tex_identifiers["shadow"], tex.name,re.IGNORECASE) is not None:
#                 #作業中
#                 tex.image.use_alpha = False
#                 mat.use_transparency = True
#                 mat.alpha = 0
#                 texture_slot.blend_type = 'MIX'
#                 texture_slot.use_map_color_diffuse = True
#                 texture_slot.diffuse_color_factor = 1
#                 texture_slot.use_map_alpha = True
#                 texture_slot.alpha_factor = -1

#         ctm = fjw.CyclesTexturedMaterial(new_mats)
#         ctm.execute()


#         bpy.ops.file.make_paths_relative()
#         return {'FINISHED'}
# ########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Substanceクイックアサイン")
############################################################################################################################
sbsar_tex_size = ""

def substance_bake(bake_type, src_objfile):
    """
    baketype
        ambient-occlusion
        curvature
    """
    global sbsar_tex_size
    if sbsar_tex_size == "":
        sbsar_tex_size = "12"

    dest_dir = os.path.dirname(src_objfile) + os.sep + "src"
    dest_dir = os.path.normpath(dest_dir)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    pref = fujiwara_toolbox.conf.get_pref()
    toolkit_dir = pref.SubstanceAutomationToolkit_dir

    baker = os.path.normpath(toolkit_dir + os.sep + "sbsbaker.exe")
    cmdstr = '"%s" %s "%s" --output-path "%s" --output-size %s,%s'%(baker, bake_type, src_objfile, dest_dir, sbsar_tex_size, sbsar_tex_size)
    print(cmdstr)
    p = subprocess.Popen(cmdstr)
    p.wait()

def substance_render(sbsar, src_dir, name):
    pref = fujiwara_toolbox.conf.get_pref()
    toolkit_dir = pref.SubstanceAutomationToolkit_dir

    global sbsar_tex_size
    render = os.path.normpath(toolkit_dir + os.sep + "sbsrender.exe")
    dest_dir = os.path.dirname(src_dir)
    entries = '--set-entry ambient-occlusion@"%s"'%(os.path.normpath(src_dir+os.sep+name+"_ambient-occlusion.png"))
    entries += ' --set-entry curvature@"%s"'%(os.path.normpath(src_dir+os.sep+name+"_curvature.png"))
    entries += ' --set-entry normal-world-space@"%s"'%(os.path.normpath(src_dir+os.sep+name+"_normal-world-space.png"))
    entries += ' --set-entry position@"%s"'%(os.path.normpath(src_dir+os.sep+name+"_position.png"))
    entries += ' --set-entry uv-map@"%s"'%(os.path.normpath(src_dir+os.sep+name+"_uv-map.png"))
    entries += ' --set-entry world-space-direction@"%s"'%(os.path.normpath(src_dir+os.sep+name+"_world-space-direction.png"))
    if sbsar_tex_size != "":
        entries += ' --set-value $outputsize@%s,%s'%(sbsar_tex_size,sbsar_tex_size)
    cmdstr = '"%s" render --output-name="%s_{inputGraphUrl}_{outputNodeName}" %s --output-path "%s" "%s"'%(render, name, entries, dest_dir, sbsar)
    print(cmdstr)
    p = subprocess.Popen(cmdstr)
    p.wait()
    sbsar_tex_size = ""

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

from fujiwara_toolbox_modules.modules.main.submodules.substance_tools import SubstanceTools


def set_sbsar_to_active():
    obj = fjw.active()
    st = SubstanceTools(obj)
    st.clean_materials()

    st.export()
    maptype = "ambient-occlusion"
    if get_substance_settings(obj, maptype):
        st.bake(maptype)
    maptype = "curvature"
    if get_substance_settings(obj, maptype):
        st.bake(maptype)
    maptype = "normal-world-space"
    if get_substance_settings(obj, maptype):
        st.bake(maptype)
    maptype = "position"
    if get_substance_settings(obj, maptype):
        st.bake(maptype)
    maptype = "uv-map"
    if get_substance_settings(obj, maptype):
        st.bake(maptype)
    maptype = "world-space-direction"
    if get_substance_settings(obj, maptype):
        st.bake(maptype)
    st.render()
    st.material_setup()

########################################
#Load .sbsar
########################################
#bpy.ops.fujiwara_toolbox.load_sbsar() #Load .sbsar
class FUJIWARATOOLBOX_LOAD_SBSAR(bpy.types.Operator):
    """アセットライブラリフォルダからSubstanceアーカイブをロードする。"""
    bl_idname = "fujiwara_toolbox.load_sbsar"
    bl_label = "Load .sbsar"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILESEL",mode="")

    filter_glob = StringProperty(default="*.sbsar", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        sbsdir = assetdir + os.sep + "sbs"
        if not os.path.exists(sbsdir):
            self.report({"WARNING"}, "%sを作成してsbsarを設置してください。"%sbsdir)
            return {"CANCELLED"}

        self.directory = sbsdir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        print("set path")
        SubstanceTools.sbsar_path = self.filepath
        print("info()")
        SubstanceTools.info()
        return {'FINISHED'}
########################################

########################################
#親フォルダから
########################################
#bpy.ops.fujiwara_toolbox.loas_sbsar_from_current() #親フォルダから
class FUJIWARATOOLBOX_LOAS_SBSAR_FROM_CURRENT(bpy.types.Operator):
    """親フォルダからSubstanceアーカイブをロードする。"""
    bl_idname = "fujiwara_toolbox.loas_sbsar_from_current"
    bl_label = "親フォルダから"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILESEL",mode="")

    filter_glob = StringProperty(default="*.sbsar", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        sbsdir = os.path.dirname(bpy.data.filepath)
        if not os.path.exists(sbsdir):
            self.report({"WARNING"}, "%sを作成してsbsarを設置してください。"%sbsdir)
            return {"CANCELLED"}

        self.directory = sbsdir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        SubstanceTools.sbsar_path = self.filepath
        SubstanceTools.info()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#Substanceマテリアルを設定
########################################
#bpy.ops.fujiwara_toolbox.set_sbsar_to_active() #Substanceマテリアルを設定
class FUJIWARATOOLBOX_SET_SBSAR_TO_ACTIVE(bpy.types.Operator):
    """アクティブオブジェクトに、指定したグラフのマテリアルを設定する。アセットディレクトリ/sbs/にsbsarをおいておく。編集モード時は選択面に割り当てる。UVマップがない場合、選択部のみ展開される。"""
    bl_idname = "fujiwara_toolbox.set_sbsar_to_active"
    bl_label = "Substanceマテリアルを設定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATERIAL_DATA",mode="")

    def get_graph_list_callback(scene, context):
        items = []
        for g in SubstanceTools.graph_list:
            items.append((g,g,""))
        return items    

    graph_list = EnumProperty(
        name = "Graph List",               # 名称
        description = "Graph List",        # 説明文
        items = get_graph_list_callback)   # 項目リストを作成する関数

    def invoke(self, context, event):
        obj = fjw.active()

        if obj.mode != "EDIT":
            count = 0
            for mat in obj.data.materials:
                if not mat:
                    continue
                if "_sbsgen" in mat.name:
                    count+=1
            if count > 1:
                self.report({"WARNING"},"メッシュで割り当てた情報があります！やり直す場合はマテリアルを全て削除してください。")
                return {"CANCELLED"}

        pref = fujiwara_toolbox.conf.get_pref()
        toolkit_dir = pref.SubstanceAutomationToolkit_dir

        if not os.path.exists(toolkit_dir):
            self.report({"WARNING"}, "アドオン設定でSubstance Automation Toolkitのディレクトリを設定してください。")
            return {"CANCELLED"}

        if SubstanceTools.sbsar_path == "":
            self.report({"WARNING"}, ".sbsarがロードされていません。")
            return {"CANCELLED"}
            

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.graph_list == "":
            self.report({"WARNING"}, "グラフが未指定です。")
            return {"CANCELLED"}
        SubstanceTools.graph_url = self.graph_list

        obj = fjw.active()

        fjw.deselect()
        fjw.activate(obj)
        if obj.mode == "EDIT":
            #選択面のUV展開をチェック
            fjw.mode("OBJECT")

            base_obj = obj
            #0番だとベースマテリアルになってしまうのでマテリアルを追加
            if len(base_obj.data.materials) == 0:
                base_obj.data.materials.append(fjw.get_material(base_obj.name))

            has_uv = False
            for face in obj.data.polygons:
                if not face.select:
                    continue
                for v_index, loop_index in zip(face.vertices, face.loop_indices):
                    for uvl in obj.data.uv_layers:
                        uv_co = uvl.data[loop_index].uv
                        if uv_co.x != 0 or uv_co.y != 0:
                            #UVに所属している
                            has_uv = True
                            break
                    if has_uv:
                        break
                if has_uv:
                    break

            fjw.mode("EDIT")
            if not has_uv:
                bpy.ops.uv.smart_project()
            
            #複製する前にマテリアル割当
            bpy.ops.object.material_slot_add()
            bpy.ops.object.material_slot_assign()

            # bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

            fjw.mode("OBJECT")

            dup_obj = None

            for obj in fjw.get_selected_list():
                if obj != base_obj:
                    dup_obj = obj

            fjw.deselect()
            fjw.activate(dup_obj)

            set_sbsar_to_active()

            mat = dup_obj.data.materials[0]

            fjw.deselect()
            fjw.activate(base_obj)
            fjw.mode("EDIT")

            slot_last = len(base_obj.material_slots) - 1
            base_obj.material_slots[slot_last].material = mat
            fjw.mode("OBJECT")

            fjw.delete([dup_obj])

            fjw.activate(base_obj)

            pass
        else:
            set_sbsar_to_active()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#256
########################################
#bpy.ops.fujiwara_toolbox.set_sbsar_256() #256
class FUJIWARATOOLBOX_SET_SBSAR_256(bpy.types.Operator):
    """Substanceマテリアルを指定ピクセルで設定。"""
    bl_idname = "fujiwara_toolbox.set_sbsar_256"
    bl_label = "256"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATERIAL_DATA",mode="")

    def execute(self, context):
        SubstanceTools.tex_size = "8"
        bpy.ops.fujiwara_toolbox.set_sbsar_to_active("INVOKE_DEFAULT")
        return {'FINISHED'}
########################################

########################################
#512
########################################
#bpy.ops.fujiwara_toolbox.set_sbsar_512() #512
class FUJIWARATOOLBOX_SET_SBSAR_512(bpy.types.Operator):
    """Substanceマテリアルを指定ピクセルで設定。"""
    bl_idname = "fujiwara_toolbox.set_sbsar_512"
    bl_label = "512"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATERIAL_DATA",mode="")

    def execute(self, context):
        SubstanceTools.tex_size = "9"
        bpy.ops.fujiwara_toolbox.set_sbsar_to_active("INVOKE_DEFAULT")
        return {'FINISHED'}
########################################

########################################
#1024
########################################
#bpy.ops.fujiwara_toolbox.set_sbsar_1024() #1024
class FUJIWARATOOLBOX_SET_SBSAR_1024(bpy.types.Operator):
    """Substanceマテリアルを指定ピクセルで設定。"""
    bl_idname = "fujiwara_toolbox.set_sbsar_1024"
    bl_label = "1024"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATERIAL_DATA",mode="")

    def execute(self, context):
        SubstanceTools.tex_size = "10"
        bpy.ops.fujiwara_toolbox.set_sbsar_to_active("INVOKE_DEFAULT")
        return {'FINISHED'}
########################################

########################################
#2048
########################################
#bpy.ops.fujiwara_toolbox.set_sbsar_2048() #2048
class FUJIWARATOOLBOX_SET_SBSAR_2048(bpy.types.Operator):
    """Substanceマテリアルを指定ピクセルで設定。"""
    bl_idname = "fujiwara_toolbox.set_sbsar_2048"
    bl_label = "2048"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATERIAL_DATA",mode="")

    def execute(self, context):
        SubstanceTools.tex_size = "11"
        bpy.ops.fujiwara_toolbox.set_sbsar_to_active("INVOKE_DEFAULT")
        return {'FINISHED'}
########################################

#bakeはいくらでもいけるけどrenderは2Kまでしか出ない


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

"""
ambient-occlusion
curvature
normal-world-space
position
uv-map
world-space-direction
"""
def substance_settings(obj, maptype, state):
    if state:
        val = "True"
    else:
        val = "False"
    obj["substance_settings_"+maptype] = val

def get_substance_settings(obj, maptype):
    propname = "substance_settings_"+maptype
    if propname not in obj:
        if maptype == "ambient-occlusion":
            return True
        if maptype == "curvature":
            return True
        if maptype == "position":
            return True
        if maptype == "normal-world-space":
            return True
        return False

    val = obj[propname]
    if val == "True":
        return True
    return False

########################################
#AO
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_ao_on() #AO
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_AO_ON(bpy.types.Operator):
    """このオブジェクトのambient-occlusionをsbsarに渡す設定。デフォルトはオン。"""
    bl_idname = "fujiwara_toolbox.substance_setting_ao_on"
    bl_label = "AO"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "ambient-occlusion", True)
        return {'FINISHED'}
########################################

########################################
#curvature
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_curvature_on() #curvature
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_CURVATURE_ON(bpy.types.Operator):
    """このオブジェクトのcurvatureをsbsarに渡す設定。デフォルトはオン。"""
    bl_idname = "fujiwara_toolbox.substance_setting_curvature_on"
    bl_label = "curvature"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "curvature", True)
        return {'FINISHED'}
########################################

########################################
#normal
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_normal_on() #normal
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_NORMAL_ON(bpy.types.Operator):
    """このオブジェクトのnormalをsbsarに渡す設定。デフォルトはオン。"""
    bl_idname = "fujiwara_toolbox.substance_setting_normal_on"
    bl_label = "normal"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "normal", True)
        return {'FINISHED'}
########################################

########################################
#position
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_position_on() #position
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_POSITION_ON(bpy.types.Operator):
    """このオブジェクトのpositionをsbsarに渡す設定。デフォルトはオン。"""
    bl_idname = "fujiwara_toolbox.substance_setting_position_on"
    bl_label = "position"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "position", True)
        return {'FINISHED'}
########################################

########################################
#uv
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_uv_on() #uv
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_UV_ON(bpy.types.Operator):
    """このオブジェクトのuv-mapをsbsarに渡す設定。デフォルトはオフ。"""
    bl_idname = "fujiwara_toolbox.substance_setting_uv_on"
    bl_label = "uv"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "uv-map", True)
        return {'FINISHED'}
########################################

########################################
#direction
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_direction_on() #direction
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_DIRECTION_ON(bpy.types.Operator):
    """このオブジェクトのworld-space-directionをsbsarに渡す設定。デフォルトはオフ。"""
    bl_idname = "fujiwara_toolbox.substance_setting_direction_on"
    bl_label = "direction"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_HLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "world-space-direction", True)
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#AO
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_ao_off() #AO
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_AO_OFF(bpy.types.Operator):
    """このオブジェクトのambient-occlusionをsbsarに渡さない設定。デフォルトはオン。"""
    bl_idname = "fujiwara_toolbox.substance_setting_ao_off"
    bl_label = "AO"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "ambient-occlusion", False)
        return {'FINISHED'}
########################################

########################################
#curvature
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_curvature_off() #curvature
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_CURVATURE_OFF(bpy.types.Operator):
    """このオブジェクトのcurvatureをsbsarに渡さない設定。デフォルトはオン。"""
    bl_idname = "fujiwara_toolbox.substance_setting_curvature_off"
    bl_label = "curvature"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "curvature", False)
        return {'FINISHED'}
########################################

########################################
#normal
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_normal_off() #normal
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_NORMAL_OFF(bpy.types.Operator):
    """このオブジェクトのnormalをsbsarに渡さない設定。デフォルトはオフ。"""
    bl_idname = "fujiwara_toolbox.substance_setting_normal_off"
    bl_label = "normal"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "normal", False)
        return {'FINISHED'}
########################################

########################################
#position
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_position_off() #position
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_POSITION_OFF(bpy.types.Operator):
    """このオブジェクトのpositionをsbsarに渡さない設定。デフォルトはオフ。"""
    bl_idname = "fujiwara_toolbox.substance_setting_position_off"
    bl_label = "position"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "position", False)
        return {'FINISHED'}
########################################

########################################
#uv
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_uv_off() #uv
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_UV_OFF(bpy.types.Operator):
    """このオブジェクトのuv-mapをsbsarに渡さない設定。デフォルトはオフ。"""
    bl_idname = "fujiwara_toolbox.substance_setting_uv_off"
    bl_label = "uv"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "uv-map", False)
        return {'FINISHED'}
########################################

########################################
#direction
########################################
#bpy.ops.fujiwara_toolbox.substance_setting_direction_off() #direction
class FUJIWARATOOLBOX_SUBSTANCE_SETTING_DIRECTION_OFF(bpy.types.Operator):
    """このオブジェクトのworld-space-directionをsbsarに渡さない設定。デフォルトはオフ。"""
    bl_idname = "fujiwara_toolbox.substance_setting_direction_off"
    bl_label = "direction"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CHECKBOX_DEHLT",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            substance_settings(obj, "world-space-direction", False)
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("便利")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#スマートUV投影
########################################
#bpy.ops.fujiwara_toolbox.sbsutil_smart_uv_projection() #スマートUV投影
class FUJIWARATOOLBOX_SBSUTIL_SMART_UV_PROJECTION(bpy.types.Operator):
    """スマートUV投影を実行。"""
    bl_idname = "fujiwara_toolbox.sbsutil_smart_uv_projection"
    bl_label = "スマートUV投影"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.uv.smart_project()
        return {'FINISHED'}
########################################

########################################
#ライトマップパック
########################################
#bpy.ops.fujiwara_toolbox.sbsutil_lightmap_pack() #ライトマップパック
class FUJIWARATOOLBOX_SBSUTIL_LIGHTMAP_PACK(bpy.types.Operator):
    """ライトマップパックを実行。"""
    bl_idname = "fujiwara_toolbox.sbsutil_lightmap_pack"
    bl_label = "ライトマップパック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.uv.lightmap_pack()
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#クリーンアップ
########################################
#bpy.ops.fujiwara_toolbox.sbsutils_cleanup() #クリーンアップ
class FUJIWARATOOLBOX_SBSUTILS_CLEANUP(bpy.types.Operator):
    """選択オブジェクトとマテリアルフォルダをクリーンアップする"""
    bl_idname = "fujiwara_toolbox.sbsutils_cleanup"
    bl_label = "クリーンアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in fjw.get_selected_list():
            SubstanceTools.remove_not_used_materials(obj)
        SubstanceTools.clean_materials()
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



################################################################################
#UIカテゴリ
########################################
#髪ツール
########################################
class CATEGORYBUTTON_739344(bpy.types.Operator):#髪ツール
    """髪ツール"""
    bl_idname = "fujiwara_toolbox.categorybutton_739344"
    bl_label = "髪ツール"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("髪ツール",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("藤原用")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ケージセットアップ
########################################
#bpy.ops.fujiwara_toolbox.setup_uv_deform_cage() #ケージセットアップ
class FUJIWARATOOLBOX_SETUP_UV_DEFORM_CAGE(bpy.types.Operator):
    """選択オブジェクトを髪用ケージとしてセットアップする。"""
    bl_idname = "fujiwara_toolbox.setup_uv_deform_cage"
    bl_label = "ケージセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_LATTICE",mode="")

    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)

            if len(obj.data.uv_layers) == 0:
                bpy.context.scene.use_active_uv_for_shape = False
            else:
                bpy.context.scene.use_active_uv_for_shape = True
            bpy.ops.object.shape_from_uv()

            spu = fjw.ShapeKeyUtils(obj)
            if spu.find_key("Solid_Fix") is None:
                spu.set_value("Solid_Fix", 1.0)
            
            obj.hide_render = True
            obj.draw_type = "WIRE"

            modu = fjw.Modutils(obj)
            sld = modu.find_bytype("SOLIDIFY")
            if sld is None:
                sld = modu.add("Solidify", "SOLIDIFY")
                sld.thickness = 0.05
                sld.offset = 0

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ケージ操作")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

def is_hair_cage(obj):
    spu = fjw.ShapeKeyUtils(obj)
    sp_uv = spu.find_key("UV_Shape_key")
    if sp_uv:
        return True
    return False

def find_binders(target):
    """
        objをバインドターゲットにしているオブジェクトを検索する
    """
    result = []
    if is_hair_cage(target):
        result.append(target)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.library is None:
            modu = fjw.Modutils(obj)
            sd = modu.find_bytype("SURFACE_DEFORM")
            md = modu.find_bytype("MESH_DEFORM")
            if sd is None and md is None:
                continue
            print(obj)
            print("mod found")
            if sd is not None:
                print(sd.target)
                if sd.target == target:
                    result.append(obj)
            if md is not None:
                print(md.object)
                if md.object == target:
                    result.append(obj)
    print(result)
    return result


def get_hair_cage(obj):
    if is_hair_cage(obj):
        return obj
    
    if obj.parent:
        return get_hair_cage(obj.parent);
    return None

def hair_cage_to_flat(obj):
    if not is_hair_cage(obj):
        return

    fjw.activate(obj)
    #data.shape_keys = bpy.data.keys["Key.007"]みたいになってる
    #個別のシェイプキーは、
    #bpy.data.shape_keys["Key.007"].key_blocks["Flat"].mute = True
    #という形で、key_blocksに入っている
    shape_keys = obj.data.shape_keys
    shape_keys.eval_time = 10
  
    spu = fjw.ShapeKeyUtils(obj)
    spu.set_value_and_key("UV_Shape_key", 1, False)
    spu.set_value_and_key("Solid_Fix", 1, True)
    spu.set_active_key("UV_Shape_key")

def hair_cage_to_solid(obj):
    if not is_hair_cage(obj):
        return

    fjw.activate(obj)
    shape_keys = obj.data.shape_keys
    shape_keys.eval_time = 0
    
    spu = fjw.ShapeKeyUtils(obj)
    spu.set_value_and_key("UV_Shape_key", 1, True)
    spu.set_value_and_key("Solid_Fix", 1, False)
    spu.set_active_key("Solid_Fix")


########################################
#開きにする
########################################
class FUJIWARATOOLBOX_521395(bpy.types.Operator):#開きにする
    """開きにする"""
    bl_idname = "fujiwara_toolbox.command_521395"
    bl_label = "開きにする"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_PLANE",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type != "MESH":
                obj.select = False

        selection = fjw.get_selected_list()
        cage = get_hair_cage(fjw.active())
        if cage:
            selection.append(cage)
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            active = fjw.active()

            spu = fjw.ShapeKeyUtils(active)
            sp_uv = spu.find_key("UV_Shape_key")
            if sp_uv is None:
                continue

            fjw.activate(active)

            cage = get_hair_cage(obj)
            hair_cage_to_flat(cage)

            #アーマチュア非表示
            # modu = fjw.Modutils(fjw.active())
            # mod_armature = modu.find_bytype("ARMATURE")
            # modu.hide(mod_armature)

            # bpy.ops.view3d.viewnumpad(type="FRONT", align_active=True)
        
        
        return {'FINISHED'}
########################################

########################################
#立体化
########################################
class FUJIWARATOOLBOX_17323(bpy.types.Operator):#立体化
    """立体化"""
    bl_idname = "fujiwara_toolbox.command_17323"
    bl_label = "立体化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MESH_CUBE",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type != "MESH":
                obj.select = False
        selection = fjw.get_selected_list()
        cage = get_hair_cage(fjw.active())
        if cage:
            selection.append(cage)
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)

            binders = find_binders(obj)
            for binder in binders:
                hair_cage_to_solid(binder)
    
            #アーマチュア表示
            # modu = fjw.Modutils(active)
            # mod_armature = modu.find_bytype("ARMATURE")
            # modu.show(mod_armature)

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("メッシュ・サーフェスデフォーム")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#アクティブにバインド
########################################
#bpy.ops.fujiwara_toolbox.uv_deform_bind_to_active() #アクティブにバインド
class FUJIWARATOOLBOX_UV_DEFORM_BIND_TO_ACTIVE(bpy.types.Operator):
    """アクティブオブジェクトにサーフェスデフォームでバインドする。"""
    bl_idname = "fujiwara_toolbox.uv_deform_bind_to_active"
    bl_label = "アクティブにバインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MOD_MESHDEFORM",mode="")

    def execute(self, context):
        # bpy.ops.fujiwara_toolbox.bind_wrapped_sdef() #バインド
        active = fjw.active()
        selection = fjw.get_selected_list()
        # bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        # bpy.ops.fujiwara_toolbox.command_384891()#メッシュデフォーム　精度5
        # bpy.ops.fujiwara_toolbox.parent_meshdeform_4() #精度4
        bpy.ops.fujiwara_toolbox.bind_sdef() #バインド
        fjw.select(selection)
        active.select = False
        return {'FINISHED'}
########################################

########################################
#再バインド
########################################
#bpy.ops.fujiwara_toolbox.hair_rebind() #再バインド
class FUJIWARATOOLBOX_HAIR_REBIND(bpy.types.Operator):
    """選択オブジェクトのサーフェスデフォーム、メッシュデフォームを再バインドする。"""
    bl_idname = "fujiwara_toolbox.hair_rebind"
    bl_label = "再バインド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        # bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        selection = fjw.get_selected_list()
        bpy.ops.fujiwara_toolbox.command_860977()
        fjw.select(selection)
        bpy.ops.fujiwara_toolbox.rebind_sdef()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ケージの子を更新
########################################
#bpy.ops.fujiwara_toolbox.hair_update_cage_children() #ケージの子を更新
class FUJIWARATOOLBOX_HAIR_UPDATE_CAGE_CHILDREN(bpy.types.Operator):
    """このケージを対象にしたメッシュを再バインドする。"""
    bl_idname = "fujiwara_toolbox.hair_update_cage_children"
    bl_label = "ケージの子を更新"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        cage = fjw.active()
        if not is_hair_cage(cage):
            return {"CANCELLED"}

        fjw.deselect()
        hair_cage_to_flat(cage)

        binders = find_binders(cage)
        fjw.deselect()
        fjw.select(binders)
        bpy.ops.fujiwara_toolbox.hair_rebind()

        fjw.deselect()
        hair_cage_to_solid(cage)

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ランダム化")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#位置X
########################################
#bpy.ops.fujiwara_toolbox.randomize_loc_x() #位置X
class FUJIWARATOOLBOX_RANDOMIZE_LOC_X(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_loc_x"
    bl_label = "位置X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        # bpy.ops.object.randomize_transform(loc=(0.06, 0, 0), rot=(0.00261799, 0, 0), scale_even=True, scale=(1.06, 1, 1))
        rnd = random.random()*10000
        value=0.005
        bpy.ops.object.randomize_transform(random_seed=rnd,loc=(value,0,0))
        return {'FINISHED'}
########################################

########################################
#Y
########################################
#bpy.ops.fujiwara_toolbox.randomize_loc_y() #Y
class FUJIWARATOOLBOX_RANDOMIZE_LOC_Y(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_loc_y"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=0.005
        bpy.ops.object.randomize_transform(random_seed=rnd,loc=(0,value,0))
        return {'FINISHED'}
########################################

########################################
#Z
########################################
#bpy.ops.fujiwara_toolbox.randomize_loc_z() #Z
class FUJIWARATOOLBOX_RANDOMIZE_LOC_Z(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_loc_z"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=0.005
        bpy.ops.object.randomize_transform(random_seed=rnd,loc=(0,0,value))
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#回転X
########################################
#bpy.ops.fujiwara_toolbox.randomize_rot_x() #回転X
class FUJIWARATOOLBOX_RANDOMIZE_ROT_X(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_rot_x"
    bl_label = "回転X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=0.44663
        bpy.ops.object.randomize_transform(random_seed=rnd,rot=(value,0,0))
        return {'FINISHED'}
########################################

########################################
#Y
########################################
#bpy.ops.fujiwara_toolbox.randomize_rot_y() #Y
class FUJIWARATOOLBOX_RANDOMIZE_ROT_Y(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_rot_y"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=0.44663
        bpy.ops.object.randomize_transform(random_seed=rnd,rot=(0,value,0))
        return {'FINISHED'}
########################################

########################################
#Z
########################################
#bpy.ops.fujiwara_toolbox.randomize_rot_z() #Z
class FUJIWARATOOLBOX_RANDOMIZE_ROT_Z(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_rot_z"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=0.44663
        bpy.ops.object.randomize_transform(random_seed=rnd,rot=(0,0,value))
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#拡縮X
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_x() #拡縮X
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_X(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_x"
    bl_label = "拡縮X"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(value,0,0))
        return {'FINISHED'}
########################################

########################################
#Y
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_y() #Y
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_Y(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_y"
    bl_label = "Y"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(0,value,0))
        return {'FINISHED'}
########################################

########################################
#Z
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_z() #Z
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_Z(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_z"
    bl_label = "Z"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(0,0,value))
        return {'FINISHED'}
########################################

########################################
#全て
########################################
#bpy.ops.fujiwara_toolbox.randomize_scale_all() #全て
class FUJIWARATOOLBOX_RANDOMIZE_SCALE_ALL(bpy.types.Operator):
    """ランダム化"""
    bl_idname = "fujiwara_toolbox.randomize_scale_all"
    bl_label = "全て"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        rnd = random.random()*10000
        value=1.1
        bpy.ops.object.randomize_transform(random_seed=rnd,scale=(value,value,value),scale_even=True)
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

############################################################################################################################
uiitem("メッシュツール")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#複製分離してスキン線画化
########################################
#bpy.ops.fujiwara_toolbox.make_skin_line() #複製分離してスキン線画化
class FUJIWARATOOLBOX_MAKE_SKIN_LINE(bpy.types.Operator):
    """選択頂点を複製分離してスキンmodをかける。"""
    bl_idname = "fujiwara_toolbox.make_skin_line"
    bl_label = "複製分離してスキン線画化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        # bpy.ops.fujiwara_toolbox.dup_and_part()#複製分離
        fjw.mode("OBJECT")
        obj = fjw.active()
        fjw.deselect()
        fjw.select([obj])
        bpy.ops.object.duplicate()

        obj = fjw.active()
        obj.name = obj.name+"_Edge"
        fjw.deselect()
        fjw.select([obj])
        #シェイプキーの除去
        shu = fjw.ShapeKeyUtils(obj)
        shu.remove_all_keys()

        #subsurf以外のmodの適用
        modu = fjw.Modutils(obj)
        for mod in modu.mods:
            if mod.type != "SUBSURF":
                modu.apply(mod)
        
        #選択頂点以外の除去
        fjw.mode("EDIT")
        bpy.ops.mesh.duplicate(mode=1)
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        m = modu.add("Skin", "SKIN")
        bpy.ops.object.skin_root_mark()
        val = 0.05
        bpy.ops.transform.skin_resize(value=(val, val, val), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

        fjw.mode("OBJECT")
        #マテリアル初期化
        obj.data.materials.clear()
        blackmat = fjw.get_material("黒ベタ")
        blackmat.diffuse_color = (0,0,0)
        blackmat.use_shadeless = True
        obj.data.materials.append(blackmat)

        fjw.mode("EDIT")
            


        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("ベベル髪")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ベベル髪追加
########################################
#bpy.ops.fjw.append_bevel_hair() #ベベル髪追加
class FUJIWARATOOLBOX_append_bevel_hair(bpy.types.Operator):
    """ベベル髪オブジェクトを追加する。メッシュに変換するとテクスチャが見えるようになる。"""
    bl_idname = "fujiwara_toolbox.append_bevel_hair"
    bl_label = "ベベル髪追加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.append_group("ベベル髪")
        #ゼロ移動で更新させる
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("パーティクルヘア")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
########################################
#複製して新システム
########################################
#bpy.ops.fujiwara_toolbox.new_system_with_dup_settings() #複製して新システム
class FUJIWARATOOLBOX_NEW_SYSTEM_WITH_DUP_SETTINGS(bpy.types.Operator):
    """パーティクルシステムを複製して本数ゼロの新しいシステムを作る。"""
    bl_idname = "fujiwara_toolbox.new_system_with_dup_settings"
    bl_label = "複製して新システム"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.particle.duplicate_particle_system()
        psys = fjw.active().particle_systems.active
        psys.settings = psys.settings.copy()
        psys.settings.count = 0
        bpy.ops.particle.edited_clear()

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("パーティクルヘア合成")
############################################################################################################################

class CombineHair():
    def __init__(self, obj):
        self.org = obj
        self.setup()
        self.edit_hair_index = 0
    
    def cleanup(self, obj):
        #パーティクルヘアをすべて削除
        fjw.activate(obj)
        fjw.mode("OBJECT")

        for i in range(len(obj.particle_systems)):
            bpy.ops.object.particle_system_remove()

    def setup(self):
        fjw.deselect()
        fjw.activate(self.org)
        bpy.ops.object.duplicate()
        self.dup = fjw.active()
        fjw.deselect()
        fjw.activate(self.dup)
        self.cleanup(self.dup)

        # 生成物は次のレイヤーに送って、現在のレイヤーを非表示
        active_layer_index = 0
        for i, val in enumerate(self.org.layers):
            if val:
                active_layer_index = i
                break
        dup_layer_index = 0
        if active_layer_index < 19:
            dup_layer_index = active_layer_index + 1
        else:
            dup_layer_index = 19

        layers = [False for i in range(20)]
        layers[dup_layer_index] = True
        self.dup.layers = layers

        bpy.context.scene.layers[dup_layer_index] = True
        bpy.context.scene.layers[active_layer_index] = False
    
    def get_particle_systems(self, obj, physics_hair=True, non_physics_hair=True):
        # 対象になるパーティクルシステムを取得する
        result = []
        for ps in obj.particle_systems:
            if ps.settings.type != "HAIR":
                continue
            if physics_hair:
                if ps.use_hair_dynamics:
                    result.append(ps)
            if non_physics_hair:
                if not ps.use_hair_dynamics:
                    result.append(ps)
        return result
        
    def create_hair_system(self, obj, hair_count, src_psystem, use_hair_dynamics, hair_step):
        fjw.activate(obj)
        bpy.ops.object.particle_system_add()
        ps = obj.particle_systems[0]
        ps.name = "Combined Hair"
        ps.use_hair_dynamics = use_hair_dynamics

        ps.settings = src_psystem.settings.copy()
        ps.settings.count = hair_count
        ps.settings.hair_step = hair_step

        
    def copy_hair(self, src_pc):
        dest_psys = self.dup.particle_systems[0]
        for i in range(len(src_pc.particles)):
            src_particle = src_pc.particles[i]
            dest_particle = dest_psys.particles[self.edit_hair_index]
            print(len(src_particle.hair_keys))
            print(len(dest_particle.hair_keys))
            for j in range(len(src_particle.hair_keys)):
                dest_particle.hair_keys[j].co = src_particle.hair_keys[j].co

            self.edit_hair_index += 1
            
        pass

    def combine_hair(self, physics_hair=True, non_physics_hair=True, use_hair_dynamics=False):
        pss = self.get_particle_systems(self.org)

        # 髪の合計本数を取得
        total_count = 0
        for ps in pss:
            total_count += len(ps.particles)

        self.create_hair_system(self.dup, total_count, pss[0], use_hair_dynamics, len(pss[0].particles[0].hair_keys) - 1)
        fjw.mode("PARTICLE_EDIT")
        #Referrenced from HairNet.py
        bpy.context.scene.tool_settings.particle_edit.use_emitter_deflect = False
        bpy.context.scene.tool_settings.particle_edit.use_preserve_root = False
        bpy.context.scene.tool_settings.particle_edit.use_preserve_length = False
        bpy.ops.particle.disconnect_hair(all=True)
        bpy.ops.particle.connect_hair(all=True)

        for ps in pss:
            self.copy_hair(ps)

        fjw.mode("OBJECT")
        fjw.mode("PARTICLE_EDIT")

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
########################################
#すべてを合成
########################################
#bpy.ops.fujiwara_toolbox.combine_all_hair() #すべてを合成
class FUJIWARATOOLBOX_COMBINE_ALL_HAIR(bpy.types.Operator):
    """すべてのヘアーのParticleSystemを合成した、オブジェクトの複製を生成する。"""
    bl_idname = "fujiwara_toolbox.combine_all_hair"
    bl_label = "すべてを合成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj is None:
            return {"CANCELLED"}
        if obj.type != "MESH":
            return {"CANCELLED"}
        chair = CombineHair(fjw.active())
        chair.combine_hair()
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#非物理のみ
########################################
#bpy.ops.fujiwara_toolbox.combine_non_physics_hair() #非物理のみ
class FUJIWARATOOLBOX_COMBINE_NON_PHYSICS_HAIR(bpy.types.Operator):
    """ヘアダイナミクスが設定されてないもののみ合成する。"""
    bl_idname = "fujiwara_toolbox.combine_non_physics_hair"
    bl_label = "非物理のみ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj is None:
            return {"CANCELLED"}
        if obj.type != "MESH":
            return {"CANCELLED"}
        chair = CombineHair(fjw.active())
        chair.combine_hair(physics_hair=False, non_physics_hair=True)
        return {'FINISHED'}
########################################

########################################
#物理のみ
########################################
#bpy.ops.fujiwara_toolbox.combine_physics_hair() #物理のみ
class FUJIWARATOOLBOX_COMBINE_PHYSICS_HAIR(bpy.types.Operator):
    """ヘアダイナミクスが設定されてるもののみ合成する。"""
    bl_idname = "fujiwara_toolbox.combine_physics_hair"
    bl_label = "物理のみ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj is None:
            return {"CANCELLED"}
        if obj.type != "MESH":
            return {"CANCELLED"}
        chair = CombineHair(fjw.active())
        chair.combine_hair(physics_hair=True, non_physics_hair=False, use_hair_dynamics=True)
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("パーティクルヘア物理")
############################################################################################################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#複製して物理ヘアをはやす
########################################
#bpy.ops.fujiwara_toolbox.dup_and_genphyhair() #複製して物理ヘアをはやす
class FUJIWARATOOLBOX_DUP_AND_GENPHYHAIR(bpy.types.Operator):
    """選択面を別オブジェクトとして複製して、物理ヘアーをはやす"""
    bl_idname = "fujiwara_toolbox.dup_and_genphyhair"
    bl_label = "複製して物理ヘアをはやす"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def delete_all_particle_systems(self, obj):
        for i in range(len(obj.particle_systems)):
            bpy.ops.object.particle_system_remove()

    def get_base_particle_settings(self, obj):
        if len(obj.particle_systems) > 0:
            return obj.particle_systems[0].settings
        return None

    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        org = fjw.active()
        base_particle_settings = self.get_base_particle_settings(fjw.active())
        bpy.ops.fujiwara_toolbox.dup_and_part()
        fjw.mode("OBJECT")
        dup = fjw.active()
        dup.name = org.name + "_PartHair"
        fjw.deselect()
        fjw.activate(dup)
        self.delete_all_particle_systems(dup)
        bpy.ops.object.particle_system_add()
        psys = dup.particle_systems[0]
        if base_particle_settings is not None:
            pset = base_particle_settings.copy()
            psys.settings = pset
        psys.use_hair_dynamics = True

        bpy.ops.fujiwara_toolbox.adjust_hair("INVOKE_DEFAULT")

        return {'FINISHED'}

########################################

########################################
#ヘア調整
########################################
#bpy.ops.fujiwara_toolbox.adjust_hair() #ヘア調整
class FUJIWARATOOLBOX_ADJUST_HAIR(bpy.types.Operator):
    """パーティクルヘアを調整する"""
    bl_idname = "fujiwara_toolbox.adjust_hair"
    bl_label = "ヘア調整"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    count = IntProperty(
        name="Count",
        description="髪の量",
        default=10,
        min=0,
        max=500
    )

    hair_length = FloatProperty(
        name="Hair Length",
        description="髪の長さ",
        default = 0.25,
        min=0.0,
        max=2.0
    )

    clump_factor = FloatProperty(
        name="Clump Factor",
        description="集結",
        default=0,
        min=0.0,
        max=1.0
    )

    roughness_endpoint = FloatProperty(
        name="Roughness Endpoint",
        description="ラフネス終点",
        default=0.0,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        fjw.mode("OBJECT")
        obj = fjw.active()
        psys = obj.particle_systems[0]
        settings = psys.settings
        settings.count = self.count
        settings.hair_length = self.hair_length
        settings.clump_factor = self.clump_factor
        settings.roughness_endpoint = self.roughness_endpoint

        return {'FINISHED'}

    def invoke(self, context, event):
        if fjw.active() is None:
            return {"CANCELLED"}
        if len(fjw.active().particle_systems) == 0:
            return {"CANCELLED"}

        return context.window_manager.invoke_props_popup(self, event)
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


# class HairKeysData():
#     def __init__(self, hairkeys):
#         self.hairkeys = hairkeys
#         self.hairkeys_data = []
#         for hairkey in hairkeys:
#             co = hairkey.co
#             self.hairkeys_data.append((co[0], co[1], co[2]))
    
#     def store(self):
#         for i, hairkey in enumerate(self.hairkeys):
#             # print((hairkey.co, "<-", self.hairkeys_data[i]))
#             co = hairkey.co
#             if co.x == self.hairkeys_data[i][0] and co.y == self.hairkeys_data[i][1] and co.z == self.hairkeys_data[i][2]:
#                 print("==")
#             else:
#                 print("!=")
#             hairkey.co = self.hairkeys_data[i]

# class ParticleData():
#     def __init__(self, particle):
#         self.particle = particle
#         self.hairkeys_data = HairKeysData(particle.hair_keys)
    
#     def store(self):
#         self.hairkeys_data.store()

# class ParticleSystemData():
#     def __init__(self, particle_system):
#         self.particle_system = particle_system
#         self.particle_datas = []
#         for particle in particle_system.particles:
#             self.particle_datas.append(ParticleData(particle))

#     def store(self):
#         for particle_data in self.particle_datas:
#             particle_data.store()

"""
HairNetの機能を使ってやるほうが楽

モディファイアごとに実行
    セグメント数不一致
        セグメント数一致させる
        このフレームまで計算
    子設定をNoneに
    変換
    子設定を戻す

    パーティクルシステム除去

    変換メッシュを選択して
    obj.hnIsEmitter = True
    obj.hnMasterHairSystem = 元パーティクル
    bpy.ops.particle.hairnet(meshKind="FIBER")
    ヘアダイナミクスのプロパティまでは反映されてないから反映
    このフレームまで計算
    変換メッシュ削除
"""

########################################
#セグメント数FIX
########################################
#bpy.ops.fujiwara_toolbox.fix_hair_segments() #セグメント数FIX
class FUJIWARATOOLBOX_FIX_HAIR_SEGMENTS(bpy.types.Operator):
    """セグメント数を表示セグメント数と一致させる"""
    bl_idname = "fujiwara_toolbox.fix_hair_segments"
    bl_label = "セグメント数FIX"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj is None:
            return {"CANCELLED"}
        if obj.type != "MESH":
            return {"CANCELLED"}

        for psystem in obj.particle_systems:
            psett = psystem.settings
            segments = 2**psett.draw_step
            if psett.hair_step != segments:
                psett.hair_step = segments

        return {'FINISHED'}
########################################

class ApplyHairPhysicsParticleSystem:
    def __init__(self, obj, particle_system):
        self.obj = obj
        self.particle_system = particle_system
        self.settings = self.particle_system.settings
        # 残しとく必要もないか。
        # self.settings.id_data.use_fake_user = True
        self.store_settings()
    
    def get_modifier(self):
        for mod in self.obj.modifiers:
            if mod.type == "PARTICLE_SYSTEM":
                if mod.particle_system == self.particle_system:
                    return mod
        return None

    def convert(self):
        fjw.deselect()
        mod = self.get_modifier()
        fjw.activate(self.obj)
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.modifier_convert(modifier=mod.name)
        conv = fjw.active()

        # 原点をあわせる
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        return conv

    def activate(self):
        fjw.activate(self.obj)
        index = self.obj.particle_systems.find(self.particle_system.name)
        self.obj.particle_systems.active_index = index

    def remove(self):
        self.activate()
        bpy.ops.object.particle_system_remove()

    def bake(self):
        self.activate()
        fjw.mode("OBJECT")
        try:
            bpy.ops.ptcache.bake(bake=False)
        except:
            pass

    def fix_segments(self):
        segments = 2**self.settings.draw_step
        if self.settings.hair_step != segments:
            self.settings.hair_step = segments
            self.bake()

    def store_settings(self):
        self.particle_system_bu = fjw.PropBackup(self.particle_system)
        self.particle_system_bu.store("use_hair_dynamics")

        self.settings_bu = fjw.PropBackup(self.settings)
        self.settings_bu.store("child_type")
        # 物理設定(一部)
        self.settings_bu.store("mass")

    def restore_settings(self):
        self.particle_system_bu.restore()
        self.settings_bu.restore()

class HairNetControl:
    def __init__(self, obj):
        self.obj = obj

    def AddHairFrom(self, from_obj, particle_settings):
        self.obj.hnIsEmitter = True
        self.obj.hnMasterHairSystem = particle_settings.name
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(self.obj)
        fjw.mode("OBJECT")
        fjw.select([from_obj])
        print("add hair")
        bpy.ops.particle.hairnet("INVOKE_DEFAULT", meshKind="FIBER")

        # 追加されたパーティクルシステムを返す
        return self.obj.particle_systems.active

class HairPhysicsSetting:
    def __init__(self, psys_setting, cloth_setting):
        self.psys_settings_bu = fjw.PropBackup(psys_setting)
        self.psys_settings_bu.store("bending_random")

        self.cloth_settings_bu = fjw.PropBackup(cloth_setting)
        self.cloth_settings_bu.store("quality")
        self.cloth_settings_bu.store("mass")
        self.cloth_settings_bu.store("bending_stiffness")
        self.cloth_settings_bu.store("bending_damping")
        self.cloth_settings_bu.store("air_damping")
        self.cloth_settings_bu.store("internal_friction")
        self.cloth_settings_bu.store("density_target")
        self.cloth_settings_bu.store("density_strength")
        self.cloth_settings_bu.store("voxel_cell_size")
        self.cloth_settings_bu.store("pin_stiffness")
    
    def copyto(self, psys_setting, cloth_setting):
        self.psys_settings_bu.copyto(psys_setting)
        self.cloth_settings_bu.copyto(cloth_setting)

########################################
#物理演算を適用
########################################
#bpy.ops.fujiwara_toolbox.apply_hair_physics() #物理演算を適用
class FUJIWARATOOLBOX_APPLY_HAIR_PHYSICS(bpy.types.Operator):
    """オブジェクトのアクティブなパーティクルヘアの物理演算の結果を適用する。Addon:HairNet必須。"""
    bl_idname = "fujiwara_toolbox.apply_hair_physics"
    bl_label = "物理演算を適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    # 子ヘアーなしだと位置が異常になるという不具合あり。謎。

    def remove_particle_system_by_name(self, obj, name):
        fjw.activate(obj)
        current_index = obj.particle_systems.active_index
        index = obj.particle_systems.find(name)
        if index >= 0:
            obj.particle_systems.active_index = index
            bpy.ops.object.particle_system_remove()
            obj.particle_systems.active_index = current_index

    def execute(self, context):
        obj = fjw.active()
        if obj is None:
            return {"CANCELLED"}
        if obj.type != "MESH":
            return {"CANCELLED"}

        ahppss = []
        # for psys in obj.particle_systems:
        #     # ヘアダイナミクスオンのみ
        #     if psys.use_hair_dynamics:
        #         ahppss.append(ApplyHairPhysicsParticleSystem(obj, psys))
        # アクティブのみにする
        ahppss.append(ApplyHairPhysicsParticleSystem(obj, obj.particle_systems.active))

        for ahpps in ahppss:
            psys_basename = ahpps.particle_system.name
            # オリジナルの物理設定を取得する
            hps = HairPhysicsSetting(ahpps.particle_system.settings, ahpps.particle_system.cloth.settings)

            ahpps.fix_segments()
            ahpps.settings.child_type = 'NONE'
            conv = ahpps.convert()
            conv_name = conv.name
            ahpps.restore_settings()

            hnc = HairNetControl(obj)
            addedpsys = hnc.AddHairFrom(conv, ahpps.settings)
            added_ahpps = ApplyHairPhysicsParticleSystem(obj, addedpsys)
            added_ahpps.bake()
            fjw.delete([conv])
            ahpps.remove()
            self.remove_particle_system_by_name(obj, "HN"+conv_name)
            added_ahpps.particle_system.name = psys_basename
            added_ahpps.activate()

            fjw.mode("PARTICLE_EDIT")
            bpy.context.scene.tool_settings.particle_edit.use_emitter_deflect = False
            bpy.context.scene.tool_settings.particle_edit.use_preserve_root = False
            bpy.context.scene.tool_settings.particle_edit.use_preserve_length = False
            bpy.ops.particle.disconnect_hair(all=True)
            bpy.ops.particle.connect_hair(all=True)
            # これで編集を保存できる！
            bpy.ops.transform.translate()
            fjw.mode("OBJECT")

            # 物理設定をコピーしておく
            added_ahpps.particle_system.use_hair_dynamics = True
            hps.copyto(added_ahpps.particle_system.settings, added_ahpps.particle_system.cloth.settings)
            added_ahpps.particle_system.use_hair_dynamics = False
        
        bpy.ops.screen.frame_jump(end=False)


        return {'FINISHED'}
########################################










# ########################################
# #物理演算を適用
# ########################################
# #bpy.ops.fujiwara_toolbox.apply_hair_physics() #物理演算を適用
# class FUJIWARATOOLBOX_APPLY_HAIR_PHYSICS(bpy.types.Operator):
#     """オブジェクトのすべてのパーティクルヘアの物理演算の結果を適用する"""
#     bl_idname = "fujiwara_toolbox.apply_hair_physics"
#     bl_label = "物理演算を適用"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def get_selected_v_indexes(self, data):
#         indexes = []
#         for v in data.vertices:
#             if v.select:
#                 indexes.append(v.index)
#         return indexes

#     def get_edge(self, data, v):
#         # 所属してるエッジを返す
#         pass
    
#     # def get_other_side(self, data, )

#     def get_linked_v_indexes(self, data, root_index):
#         # ルートから順番に接続頂点のインデックスを返す？
#         pass

#     def execute(self, context):
        
#         # 一回メッシュに変換してからその座標をとればよかった！！！！！
#         # 変換後
#             # ルートの頂点が選択された状態になってる
#         # ルートとして回収
#         # 各ルートごとに接続頂点を選択して、選択内でまわせばいいのでは

#         obj = fjw.active()
#         if obj is None:
#             return {"CANCELLED"}
#         if obj.type != "MESH":
#             return {"CANCELLED"}

#         # パーティクルのステップ数がビューと一致してないとめんどくさい。
#         # 2^ビューのステップ数 == パーティクルのステップ

#         org = obj

#         particle_system_data = {}
#         for pmod in org.modifiers:
#             if pmod.type != "PARTICLE_SYSTEM":
#                 continue
#             fjw.deselect()
#             fjw.activate(org)
#             bpy.ops.view3d.snap_cursor_to_selected()

#             psys = pmod.particle_system
#             psys_index = org.particle_systems.find(psys.name)
#             p_settings_bu = fjw.PropBackup(psys.settings)
#             p_settings_bu.store("child_type")
#             psys.settings.child_type = "NONE"
#             bpy.ops.object.modifier_convert(modifier=pmod.name)
#             p_settings_bu.restore()

#             cmesh = fjw.active()
#             # 生成されたメッシュの原点、0,0,0になってる！
#             fjw.deselect()
#             fjw.activate(cmesh)
#             bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

#             fjw.mode("EDIT")

#             root_vertice_indexes = self.get_selected_v_indexes(cmesh.data)

#             for particle_index, rvi in enumerate(root_vertice_indexes):
#                 particle = psys.particles[particle_index]

#                 bpy.ops.mesh.select_all(action="DESELECT")
#                 cmesh.data.vertices[rvi].select = True
#                 bpy.ops.mesh.select_linked()

#                 linked_vertice_indexes = self.get_selected_v_indexes(cmesh.data)
#                 hair_keys = particle.hair_keys
#                 for hair_key_index, lvi in enumerate(linked_vertice_indexes):
#                     # if hair_key_index >= len(hair_keys):
#                     #     break
#                     # hair_keys[index].co = cmesh.data.vertices[lvi].co

#                     # 同じ値が入りまくってる
#                     co = cmesh.data.vertices[lvi].co
#                     particle_system_data[psys_index ,particle_index, hair_key_index] = (float(co.x), float(co.y), float(co.z))

#         # 回収したデータの反映
#         # print(particle_system_data)
#         for data in particle_system_data:
#             print(data, particle_system_data[data])
#         bpy.ops.screen.frame_jump(end=False)

#         for psys_index in range(len(org.particle_systems)):
#             fjw.mode("OBJECT")
#             # fjw.delete([cmesh])
#             fjw.activate(org)
#             org.particle_systems.active_index = psys_index
#             org.particle_systems.active.use_hair_dynamics = False
#             fjw.mode("PARTICLE_EDIT")
#             #Referrenced from HairNet.py
#             bpy.context.scene.tool_settings.particle_edit.use_emitter_deflect = False
#             bpy.context.scene.tool_settings.particle_edit.use_preserve_root = False
#             bpy.context.scene.tool_settings.particle_edit.use_preserve_length = False
#             bpy.ops.particle.disconnect_hair(all=True)
#             bpy.ops.particle.connect_hair(all=True)

#             for particle_index,particle in enumerate(psys.particles):
#                 for hair_key_index, hair_key in enumerate(particle.hair_keys):
#                     hair_key.co = particle_system_data[psys_index, particle_index, hair_key_index]

#             fjw.mode("OBJECT")


#         # print(bpy.data.objects["Icosphere"].particle_systems[0].particles[0].hair_keys[0].co)
#         # obj = fjw.active()
#         # if obj is None:
#         #     return {"CANCELLED"}
#         # if obj.type != "MESH":
#         #     return {"CANCELLED"}

#         # psys_datas = []
#         # for psys in obj.particle_systems:
#         #     psys_datas.append(ParticleSystemData(psys))

#         # bpy.ops.screen.frame_jump(end=False)

#         # # fjw.mode("PARTICLE_EDIT")
#         # # #Referrenced from HairNet.py
#         # # bpy.context.scene.tool_settings.particle_edit.use_emitter_deflect = False
#         # # bpy.context.scene.tool_settings.particle_edit.use_preserve_root = False
#         # # bpy.context.scene.tool_settings.particle_edit.use_preserve_length = False
#         # # bpy.ops.particle.disconnect_hair(all=True)
#         # # bpy.ops.particle.connect_hair(all=True)

#         # for psys_data in psys_datas:
#         #     psys_data.store()

#         # # fjw.mode("OBJECT")
#         # # fjw.mode("PARTICLE_EDIT")
#         # print(bpy.data.objects["Icosphere"].particle_systems[0].particles[0].hair_keys[0].co)

#         return {'FINISHED'}
# ########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
################################################################################
#UIカテゴリ
########################################
#顔ツール
########################################
class CATEGORYBUTTON_597362(bpy.types.Operator):
    """顔ツール"""
    bl_idname = "fujiwara_toolbox.categorybutton_597362"
    bl_label = "顔ツール"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("顔ツール",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#オートセットアップ
########################################
#bpy.ops.fujiwara_toolbox.auto_face_setup() #オートセットアップ
class FUJIWARATOOLBOX_AUTO_FACE_SETUP(bpy.types.Operator):
    """顔用メッシュを選択して実行する。"""
    bl_idname = "fujiwara_toolbox.auto_face_setup"
    bl_label = "オートセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filter_glob = StringProperty(default="*.json;*.png;*.psd;", options={"HIDDEN"})

    # filename = bpy.props.StringProperty(subtype="FILE_NAME")
    # filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    # directory = bpy.props.StringProperty(subtype="DIR_PATH")
    # files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    # def invoke(self, context, event):
    #     self.directory = os.path.dirname(bpy.data.filepath) + os.sep + "textures" + os.sep + "facetextures"
    #     context.window_manager.fileselect_add(self)
    #     return {'RUNNING_MODAL'}

    def execute(self, context):
        # obj = fjw.active()
        # if obj.type != "MESH":
        #     self.report({"WARNING"}, "メッシュオブジェクトを選択してください。")
        #     return {"CANCELLED"}
        #faceunitから取得する
        objects = bpy.context.scene.objects
        if "Faceunit" not in objects:
            self.report({"WARNING"}, "Faceunitが存在しません！")
            return {"CANCELLED"}
        faceunit = bpy.context.scene.objects["Faceunit"]
        # スケールの適用
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(faceunit)
        bpy.ops.fujiwara_toolbox.command_24259()#親子選択
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # カメラ用
        bpy.ops.object.scale_clear(clear_delta=False)

        face = None
        for obj in faceunit.children:
            if obj.name == "Face":
                face = obj
                break
        
        fjw.deselect()
        fjw.activate(face)

        bpy.ops.fujiwara_toolbox.proj_face_initialize() #顔初期化
        fjw.activate(obj)
        facetexdir = os.path.dirname(bpy.data.filepath) + os.sep + "textures" + os.sep + "facetextures"
        # bpy.ops.fujiwara_toolbox.load_from_json_with_activecamera(filename=self.filename, filepath=self.filepath, directory=self.directory) #アクティブカメラを基準にjsonからロード
        bpy.ops.fujiwara_toolbox.load_from_json_with_activecamera(directory=facetexdir) #アクティブカメラを基準にjsonからロード
        fjw.activate(obj)
        bpy.ops.fujiwara_toolbox.setup_face_from_camera() #顔セットアップ
        fjw.activate(obj)
        bpy.ops.fujiwara_toolbox.face_armature_setup() #アーマチュアセットアップ
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#顔初期化
########################################
#bpy.ops.fujiwara_toolbox.proj_face_initialize() #顔初期化
class FUJIWARATOOLBOX_PROJ_FACE_INITIALIZE(bpy.types.Operator):
    """プロジェクション顔を初期化する。全てのプロジェクタ、生成メッシュを除去し、マテリアルなども全て破棄する。"""
    bl_idname = "fujiwara_toolbox.proj_face_initialize"
    bl_label = "顔初期化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj.type != "MESH":
            self.report({"WARNING"}, "メッシュオブジェクトを選択してください。")
            return {"CANCELLED"}

        cam = bpy.context.scene.camera
        fst = FaceSetupTools(obj, cam)
        fst.initialize_all()
        return {'FINISHED'}
########################################

########################################
#アクティブカメラを基準にjsonからロード
########################################
#bpy.ops.fujiwara_toolbox.load_from_json_with_activecamera() #アクティブカメラを基準にjsonからロード
class FUJIWARATOOLBOX_LOAD_FROM_JSON_WITH_ACTIVECAMERA(bpy.types.Operator):
    """アクティブカメラを基準とした座標系でjsonからプロジェクタを読み込む。フォルダを指定すると自動ロード。"""
    bl_idname = "fujiwara_toolbox.load_from_json_with_activecamera"
    bl_label = "アクティブカメラを基準にjsonからロード"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    filter_glob = StringProperty(default="*.json;*.png;*.psd;", options={"HIDDEN"})

    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        self.directory = os.path.dirname(bpy.data.filepath) + os.sep + "textures" + os.sep + "facetextures"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        cam = bpy.context.scene.camera
        pt = ProjectionTools()
        pt.set_camera(cam)

        skinpath = ""

        jsonmode = True
        targetfiles = []
        if len(self.files) > 0 and self.files[0].name != "":
            for file in self.files:
                targetfiles.append(file.name)
        else:
            #ファイル指定ナシ＝jsonモード
            #よりも、オートモードにしたい！
            """
                自動読み込み条件
                ・jsonで読み込む？
                ・必ずフォトショからjsonを書き出すなら、png単体読み込みとかいらない。
                    フォルダ内のjsonを読みこんで、でいい。
                    そもそもjsonに分割数記述すべき！
                    ファイルパスも記述する。
            """
            files = os.listdir(self.directory)
            # extlist = [".json", ".png"]
            extlist = [".json"]
            for file in files:
                name, ext = os.path.splitext(file)
                if file == "skin.psd":
                    skinpath = self.directory + os.sep + file
                if ext in extlist:
                    targetfiles.append(file)

        fliplist = ["Eyebrow.json", "Eyelid.json", "Pupil.json"]
        for file in targetfiles:
            filepath = self.directory + os.sep + file
            name, ext = os.path.splitext(file)
            if ext == ".json":
                    obj = pt.load_img_with_camera(filepath)
            elif ext == ".png" or ext == ".psd":
                obj = pt.load_img_with_camera(filepath, tilenumber=1, use_json=False)

            if file in fliplist:
                dup = pt.flip_x_dup(obj)

        return {'FINISHED'}
########################################

########################################
#顔セットアップ
########################################
#bpy.ops.fujiwara_toolbox.setup_face_from_camera() #顔セットアップ
class FUJIWARATOOLBOX_SETUP_FACE_FROM_CAMERA(bpy.types.Operator):
    """アクティブカメラから選択メッシュを顔としてセットアップする。"""
    bl_idname = "fujiwara_toolbox.setup_face_from_camera"
    bl_label = "顔セットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        if obj.type != "MESH":
            self.report({"WARNING"}, "メッシュオブジェクトを選択してください。")
            return {"CANCELLED"}

        cam = bpy.context.scene.camera
        fst = FaceSetupTools(obj, cam)
        fst.facesetup()

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#アーマチュアセットアップ
########################################
#bpy.ops.fujiwara_toolbox.face_armature_setup() #アーマチュアセットアップ
class FUJIWARATOOLBOX_FACE_ARMATURE_SETUP(bpy.types.Operator):
    """アーマチュアを自動セットアップする"""
    bl_idname = "fujiwara_toolbox.face_armature_setup"
    bl_label = "アーマチュアセットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        face = fjw.active()
        armu = fjw.ArmatureUtils(None, "FaceAramature")
        armu.armature.show_x_ray = True
        cam = bpy.context.scene.camera

        #ルート
        pos = fjw.get_world_co(face)
        root_bone = armu.add_bone("root", pos, (0,0,0.1))

        #プロジェクタ
        for obj in cam.children:
            pos = fjw.get_world_co(obj)
            bone = armu.add_bone(obj.name, pos, (0,-0.03,0))
            bone.parent = root_bone
        fjw.mode("POSE")

        for obj in cam.children:
            fjw.mode("OBJECT")
            fjw.deselect()
            fjw.activate(obj)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            fjw.activate(armu.armature)
            fjw.mode("POSE")
            pbone = armu.posebone(obj.name)
            pbone.lock_location[1] = True
            armu.activate(pbone)
            bpy.ops.object.parent_set(type='BONE_RELATIVE')

            #マスク
            fjw.activate(obj)
            vgu = fjw.VertexGroupUtils(obj)
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            vgu.assign_weight(obj.name, 1)
            fjw.mode("OBJECT")

            modu = fjw.Modutils(obj)
            m = modu.add("Mask", "MASK")
            m.mode = "ARMATURE"
            m.armature = armu.armature

        #リグ部分
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(armu.armature)

        v_front = Vector((0,-0.1,0))*0.3
        offset = Vector((0,0.1,0))*0.1
        pos = self.set_3dcursor_with_mat(face, "Eyehole_R") + offset
        bone = armu.add_bone("Pupil_R", pos, v_front)
        bone.parent = armu.editbone("root")
        armu.editbone("Projector_Pupil_R").parent = bone

        pos = self.set_3dcursor_with_mat(face, "Eyehole_L") + offset
        bone = armu.add_bone("Pupil_L", pos, v_front)
        bone.parent = armu.editbone("root")
        armu.editbone("Projector_Pupil_L").parent = bone

        pos = self.set_3dcursor_with_mat(face, "Mouth") + offset
        bone = armu.add_bone("Mouth", pos, v_front)
        bone.parent = armu.editbone("root")
        armu.editbone("Projector_Mouth").parent = bone

        #視線
        fjw.mode("EDIT")
        pos = armu.editbone("Pupil_R").head - Vector((0, 0.5, 0))*0.1
        pos.x = 0
        eyetarget = armu.add_bone("Eyetarget", pos, v_front)
        eyetarget.parent = armu.editbone("root")

        pos = armu.editbone("Pupil_R").head - offset*2
        bone = armu.add_bone("Eyetarget_R", pos, v_front)
        bone.parent = eyetarget

        pos = armu.editbone("Pupil_L").head - offset*2
        bone = armu.add_bone("Eyetarget_L", pos, v_front)
        bone.parent = eyetarget

        #コンストレイント
        fjw.mode("POSE")

        pbone = armu.posebone("Pupil_R")
        c = pbone.constraints.new("DAMPED_TRACK")
        c.target = armu.armature
        c.subtarget = "Eyetarget_R"

        pbone = armu.posebone("Pupil_L")
        c = pbone.constraints.new("DAMPED_TRACK")
        c.target = armu.armature
        c.subtarget = "Eyetarget_L"


        #右目の反転
        bone = armu.posebone("Pupil_R")
        bone.scale.x = -1

        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(armu.armature)
        fjw.activate(bpy.context.scene.objects["Faceunit"])
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


        return {'FINISHED'}

    def set_3dcursor_with_mat(self, obj, matname):
        baseobj = fjw.active()
        mode = baseobj.mode

        fjw.mode("OBJECT")
        fjw.activate(obj)
        fjw.mode("EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')
        FaceSetupTools.select_mesh_by_material(obj, matname)
        bpy.ops.view3d.snap_cursor_to_selected()

        fjw.mode("OBJECT")
        fjw.activate(baseobj)
        fjw.mode(mode)
        return bpy.context.space_data.cursor_location

########################################











#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#オブジェクト生成
########################################
class CATEGORYBUTTON_335613(bpy.types.Operator):#オブジェクト生成
    """オブジェクト生成"""
    bl_idname = "fujiwara_toolbox.categorybutton_335613"
    bl_label = "オブジェクト生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("オブジェクト生成",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "horizontal"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#ランダム石生成
########################################
class FUJIWARATOOLBOX_104686(bpy.types.Operator):#ランダム石生成
    """ランダム石生成"""
    bl_idname = "fujiwara_toolbox.command_104686"
    bl_label = "ランダム石生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.mode("OBJECT")
        bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=fjw.cursor(), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        fjw.mode("EDIT")

        def rndv():
            rnd = random.randint(1,1000)
            print(rnd)
            bpy.ops.transform.vertex_random(normal=1,seed=rnd)

        bpy.ops.mesh.subdivide(number_cuts=3, smoothness=0)
        x = random.uniform(0.5,2)
        y = random.uniform(0.5,2)
        z = random.uniform(0.5,2)
        bpy.ops.transform.resize(value=(x,y,z), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)


        for i in range(random.randint(1,50)):
            rndv()

        #bpy.ops.mesh.vertices_smooth(factor=1, repeat=1)
        bpy.ops.mesh.looptools_relax(input='selected', interpolation='cubic', iterations='10', regular=True)
        fjw.mode("OBJECT")

        #自動スムーズ
        bpy.ops.fujiwara_toolbox.command_31891()


        
        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

################################################################################
#UIカテゴリ
########################################
#裏ポリエッジ
########################################
class CATEGORYBUTTON_524640(bpy.types.Operator):
    """裏ポリエッジ"""
    bl_idname = "fujiwara_toolbox.categorybutton_524640"
    bl_label = "裏ポリエッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("裏ポリエッジ",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = ""

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
################################################################################




############################################################################################################################
uiitem("便利")
############################################################################################################################
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#裏ポリ+ベベルエッジ
########################################
class FUJIWARATOOLBOX_972011(bpy.types.Operator):#裏ポリ+ベベルエッジ
    """裏ポリ+ベベルエッジ"""
    bl_idname = "fujiwara_toolbox.command_972011"
    bl_label = "裏ポリ+ベベルエッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_318722()
        bpy.ops.fujiwara_toolbox.command_60327()
        
        return {'FINISHED'}
########################################

########################################
#オノマトペ白フチ
########################################
class FUJIWARATOOLBOX_357209(bpy.types.Operator):#オノマトペ白フチ
    """オノマトペ白フチ"""
    bl_idname = "fujiwara_toolbox.command_357209"
    bl_label = "オノマトペ白フチ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_737497()
        bpy.ops.fujiwara_toolbox.command_788766()
        selection = fjw.get_selected_list()
        for obj in selection:
            mat = obj.material_slots[0].material
            mat.diffuse_color = (0,0,0)
            mat.use_shadeless = True

        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

########################################
#エッジ適用
########################################
class FUJIWARATOOLBOX_793633(bpy.types.Operator):#エッジ適用
    """エッジ適用"""
    bl_idname = "fujiwara_toolbox.command_793633"
    bl_label = "エッジ適用"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            
            mod = modu.find("ベベルエッジ")
            modu.apply(mod)

            mod = modu.find("裏ポリエッジ")
            modu.apply(mod)


        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






def urapolimat_index(obj):
    if bpy.context.scene.render.engine == 'CYCLES':
        mat = fjw.append_material("裏ポリエッジ_Cycles")
    if bpy.context.scene.render.engine == 'BLENDER_RENDER':
        mat = fjw.append_material("裏ポリエッジ")

    #デフォルトマテリアルの設置
    if len(obj.data.materials) == 0:
        dmat = bpy.data.materials.new("default")
        obj.data.materials.append(dmat)

    if mat.name not in obj.data.materials:
        obj.data.materials.append(mat)
    matindex = obj.data.materials.find(mat.name)
    return matindex

def urapoliwhitemat_index(obj):
    mat = fjw.append_material("裏ポリエッジ白")
    #デフォルトマテリアルの設置
    if len(obj.data.materials) == 0:
        dmat = bpy.data.materials.new("default")
        obj.data.materials.append(dmat)

    if mat.name not in obj.data.materials:
        obj.data.materials.append(mat)
    matindex = obj.data.materials.find(mat.name)
    return matindex

############################################################################################################################
uiitem("裏ポリエッジ")
############################################################################################################################
edgewidth = 0.001

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#裏ポリエッジ付加
########################################
class FUJIWARATOOLBOX_318722(bpy.types.Operator):#裏ポリエッジ付加
    """裏ポリエッジ付加"""
    bl_idname = "fujiwara_toolbox.command_318722"
    bl_label = "裏ポリエッジ付加"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()


        for obj in selection:
            if "裏ポリエッジ" not in obj.modifiers:
                modu = fjw.Modutils(obj)
                matindex = urapolimat_index(obj)

                mod = modu.find("裏ポリエッジ")
                if mod is None:
                    mod = modu.add("裏ポリエッジ", "SOLIDIFY")
                mod.thickness = edgewidth
                mod.offset = 1
                mod.vertex_group = "裏ポリウェイト"
                mod.thickness_vertex_group = 0.1
                mod.use_flip_normals = True
                mod.use_quality_normals = True
                # mod.material_offset = matindex
                # mod.material_offset_rim = matindex
                mod.material_offset = 999
                mod.material_offset_rim = 999
                modu.sort()
            pass
        
        return {'FINISHED'}
########################################

########################################
#裏ポリ白
########################################
class FUJIWARATOOLBOX_737497(bpy.types.Operator):#裏ポリ白
    """裏ポリ白"""
    bl_idname = "fujiwara_toolbox.command_737497"
    bl_label = "裏ポリ白"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()


        for obj in selection:
            if "裏ポリエッジ" not in obj.modifiers:
                modu = fjw.Modutils(obj)
                matindex = urapoliwhitemat_index(obj)

                mod = modu.find("裏ポリエッジ")
                if mod is None:
                    mod = modu.add("裏ポリエッジ", "SOLIDIFY")
                mod.thickness = edgewidth
                mod.offset = 1
                mod.vertex_group = "裏ポリウェイト"
                mod.thickness_vertex_group = 0.1
                mod.use_flip_normals = True
                mod.use_quality_normals = True
                mod.material_offset = matindex
                mod.material_offset_rim = matindex
                modu.sort()
            pass
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------
#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#指定Emptyで厚み制御
########################################
#bpy.ops.fujiwara_toolbox.set_thickness_driver_with_empty() #指定Emptyで厚み制御
class FUJIWARATOOLBOX_SetThicknessDriverwithEmpty(bpy.types.Operator):
    """アクティブなEmptyのZ Scaleを使用して厚さを制御できるようにする。ドライバ制御。"""
    bl_idname = "fujiwara_toolbox.set_thickness_driver_with_empty"
    bl_label = "指定Emptyで厚み制御"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "EMPTY":
            self.report({"INFO"},"EMPTYを選択してください")
            return {'CANCELLED'}

        target_obj = fjw.active()

        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type != "MESH":
                continue

            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")

            if mod is None:
                continue

            fcurve = mod.driver_add("thickness")
            driver = fcurve.driver

            variables = driver.variables
            varname = "empty_scale_z"
            if varname in variables:
                var = variables[varname]
            else:
                var = variables.new()
                var.name = varname
            var.type = "TRANSFORMS"
            target = var.targets[0]
            target.id = target_obj.id_data
            target.transform_type = 'SCALE_Z'
            target.transform_space = 'WORLD_SPACE'

            driver.expression = "empty_scale_z * 0.01"
            

        return {'FINISHED'}
########################################



def get_edge_control():
    empty = None
    for obj in bpy.context.visible_objects:
        if obj.type == "EMPTY":
            if "エッジ制御" in obj.name:
                empty = obj
                break
    if empty is None:
        empty = bpy.data.objects.new("エッジ制御",None)
        bpy.context.scene.objects.link(empty)
    loc = bpy.context.space_data.cursor_location
    ls = bpy.context.scene.layers
    empty.location = loc
    empty.layers = ls
    empty.show_x_ray = True
    empty.show_name = True
    empty.empty_draw_type = 'SINGLE_ARROW'
    empty.scale=(0.1,0.1,0.1)
    return empty




########################################
#Emptyで厚み制御（自動）
########################################
#bpy.ops.fjw.set_thickness_driver_with_empty_auto() #Emptyで厚み制御（自動）
class FUJIWARATOOLBOX_set_thickness_driver_with_empty_auto(bpy.types.Operator):
    """自動でEmptyを生成してそれで厚み制御する。"""
    bl_idname = "fujiwara_toolbox.set_thickness_driver_with_empty_auto"
    bl_label = "Emptyで厚み制御（自動）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        empty = get_edge_control()
        fjw.activate(empty)
        fjw.select(bpy.data.objects)
        bpy.ops.fujiwara_toolbox.set_thickness_driver_with_empty()
        fjw.deselect()
        fjw.activate(empty)

        return {'FINISHED'}
########################################







#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#頂点AOからウェイト作成
########################################
#bpy.ops.fjw.gen_weight_from_vertex_ao() #頂点AOからウェイト作成
class FUJIWARATOOLBOX_gen_weight_from_vertex_ao(bpy.types.Operator):
    """頂点カラーのアンビエントオクルージョンから厚みのウェイト用頂点グループを生成する。"""
    bl_idname = "fujiwara_toolbox.gen_weight_from_vertex_ao"
    bl_label = "頂点AOからウェイト作成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        colname = "裏ポリ用ウェイト"
        vertex_group_name = colname
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)

            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is None:
                continue

            if colname not in obj.data.vertex_colors:
                vcol = obj.data.vertex_colors.new(colname)
            else:
                vcol = obj.data.vertex_colors[colname]
            obj.data.vertex_colors.active = vcol
            #頂点AO
            bpy.ops.paint.vertex_color_dirt()

            vgu = fjw.VertexGroupUtils(obj)
            vertex_group = vgu.get_group(vertex_group_name)
            vertices = vgu.get_vertices()
            for v in vertices:
                weight_value = vcol.data[v.index].color.r
                vgu.set_weight(v.index, vertex_group_name, weight_value)

            #生成につかった頂点カラーは混乱の元なので消しとく
            obj.data.vertex_colors.remove(vcol)

            mod.vertex_group = vertex_group.name
            mod.thickness_vertex_group = 0.0001
            mod.invert_vertex_group = True

        return {'FINISHED'}
########################################

########################################
#反転
########################################
#bpy.ops.fjw.urapoly_weight_reverse() #反転
class FUJIWARATOOLBOX_urapoly_weight_reverse(bpy.types.Operator):
    """裏ポリエッジのウェイトを反転する。"""
    bl_idname = "fujiwara_toolbox.urapoly_weight_reverse"
    bl_label = "反転"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is None:
                continue
            
            if mod.invert_vertex_group:
                mod.invert_vertex_group = False
            else:
                mod.invert_vertex_group = True

        return {'FINISHED'}
########################################


########################################
#除去
########################################
#bpy.ops.fjw.urapoly_weight_remove() #除去
class FUJIWARATOOLBOX_urapoly_weight_remove(bpy.types.Operator):
    """裏ポリエッジのウェイトを除去する。"""
    bl_idname = "fujiwara_toolbox.urapoly_weight_remove"
    bl_label = "ウェイト除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is None:
                continue
            mod.vertex_group = ""
        return {'FINISHED'}
########################################














#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

#########################################
##1/2
#########################################
#class FUJIWARATOOLBOX_791523(bpy.types.Operator):#1/2
#    """1/2"""
#    bl_idname = "fujiwara_toolbox.command_791523"
#    bl_label = "1/2"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


####    def execute(self, context):
#        reject_notmesh()
#        selection = get_selected_list()

#        for obj in selection:
#            if "裏ポリエッジ" in obj.modifiers:
#                mod = obj.modifiers["裏ポリエッジ"]
#                mod.thickness *= 0.5

#        return {'FINISHED'}
#########################################


########################################
#1mm
########################################
class FUJIWARATOOLBOX_892991(bpy.types.Operator):#1mm
    """1mm"""
    bl_idname = "fujiwara_toolbox.command_892991"
    bl_label = "1mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.001
        
        return {'FINISHED'}
########################################
########################################
#2mm
########################################
class FUJIWARATOOLBOX_793908(bpy.types.Operator):#2mm
    """2mm"""
    bl_idname = "fujiwara_toolbox.command_793908"
    bl_label = "2mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.002
            mod = modu.find("ベベルエッジ")
            if mod is not None:
                mod.width = 0.002

        
        return {'FINISHED'}
########################################






########################################
#5mm
########################################
class FUJIWARATOOLBOX_401033(bpy.types.Operator):#5mm
    """5mm"""
    bl_idname = "fujiwara_toolbox.command_401033"
    bl_label = "5mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.005
            mod = modu.find("ベベルエッジ")
            if mod is not None:
                mod.width = 0.005
        
        return {'FINISHED'}
########################################



########################################
#1cm
########################################
class FUJIWARATOOLBOX_788766(bpy.types.Operator):#1cm
    """1cm"""
    bl_idname = "fujiwara_toolbox.command_788766"
    bl_label = "1cm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            modu = fjw.Modutils(obj)
            mod = modu.find("裏ポリエッジ")
            if mod is not None:
                mod.thickness = 0.01
            mod = modu.find("ベベルエッジ")
            if mod is not None:
                mod.width = 0.01
        
        return {'FINISHED'}
########################################







#########################################
##*2
#########################################
#class FUJIWARATOOLBOX_886958(bpy.types.Operator):#*2
#    """*2"""
#    bl_idname = "fujiwara_toolbox.command_886958"
#    bl_label = "*2"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


####    def execute(self, context):
#        reject_notmesh()
#        selection = get_selected_list()

#        for obj in selection:
#            if "裏ポリエッジ" in obj.modifiers:
#                mod = obj.modifiers["裏ポリエッジ"]
#                mod.thickness *= 2
        
#        return {'FINISHED'}
#########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#表示
########################################
class FUJIWARATOOLBOX_513603(bpy.types.Operator):#表示
    """表示"""
    bl_idname = "fujiwara_toolbox.command_513603"
    bl_label = "表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            fjw.activate(obj)
            if "裏ポリエッジ" in obj.modifiers:
                mod = obj.modifiers["裏ポリエッジ"]
                mod.show_viewport = True

        
        return {'FINISHED'}
########################################






########################################
#非表示
########################################
class FUJIWARATOOLBOX_14967(bpy.types.Operator):#非表示
    """非表示"""
    bl_idname = "fujiwara_toolbox.command_14967"
    bl_label = "非表示"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()

        for obj in selection:
            fjw.activate(obj)
            if "裏ポリエッジ" in obj.modifiers:
                mod = obj.modifiers["裏ポリエッジ"]
                mod.show_viewport = False
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




########################################
#除去
########################################
class FUJIWARATOOLBOX_290695(bpy.types.Operator):#除去
    """除去"""
    bl_idname = "fujiwara_toolbox.command_290695"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()


        for obj in selection:
            fjw.activate(obj)
            if "裏ポリエッジ" in obj.modifiers:
                bpy.ops.object.modifier_remove(modifier="裏ポリエッジ")


        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("ベベル")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ベベルエッジ
########################################
class FUJIWARATOOLBOX_60327(bpy.types.Operator):#ベベルエッジ
    """ベベルエッジ"""
    bl_idname = "fujiwara_toolbox.command_60327"
    bl_label = "ベベルエッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            mbevel = modu.find("ベベルエッジ")
            if mbevel is None:
                mbevel = modu.add("ベベルエッジ", "BEVEL")
            mbevel.width = 0.002
            mbevel.use_clamp_overlap = False
            mbevel.use_clamp_overlap = True
            mbevel.material = urapolimat_index(obj)
            mbevel.limit_method = 'ANGLE'
            modu.sort()
        
        return {'FINISHED'}
########################################


########################################
#除去
########################################
class FUJIWARATOOLBOX_312642(bpy.types.Operator):#除去
    """除去"""
    bl_idname = "fujiwara_toolbox.command_312642"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            modu.remove_byname("ベベルエッジ")
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


########################################
#Emptyで幅制御
########################################
#bpy.ops.fjw.set_width_driver_with_empty() #Emptyで幅制御
class FUJIWARATOOLBOX_set_width_driver_with_empty(bpy.types.Operator):
    """アクティブなEmptyのZ Scaleを使用して厚さを制御できるようにする。ドライバ制御。"""
    bl_idname = "fujiwara_toolbox.set_width_driver_with_empty"
    bl_label = "Emptyで幅制御"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active().type != "EMPTY":
            self.report({"INFO"},"EMPTYを選択してください")
            return {'CANCELLED'}

        target_obj = fjw.active()

        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type != "MESH":
                continue

            modu = fjw.Modutils(obj)
            mod = modu.find("ベベルエッジ")

            if mod is None:
                continue

            fcurve = mod.driver_add("width")
            driver = fcurve.driver

            variables = driver.variables
            varname = "empty_scale_z"
            if varname in variables:
                var = variables[varname]
            else:
                var = variables.new()
                var.name = varname
            var.type = "TRANSFORMS"
            target = var.targets[0]
            target.id = target_obj.id_data
            target.transform_type = 'SCALE_Z'
            target.transform_space = 'WORLD_SPACE'

            driver.expression = "empty_scale_z * 0.01"
        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("辺分離")
############################################################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#分離エッジ
########################################
class FUJIWARATOOLBOX_115887(bpy.types.Operator):#辺分離ソリッド
    """分離エッジ"""
    bl_idname = "fujiwara_toolbox.command_115887"
    bl_label = "分離エッジ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        fjw.reject_notmesh()
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            if modu.find("分離エッジ_EDGE_SPLIT") == None:
                msplit = modu.add("分離エッジ_EDGE_SPLIT","EDGE_SPLIT")
            if modu.find("分離エッジ_SOLIDIFY") == None:
                msolid = modu.add("分離エッジ_SOLIDIFY", "SOLIDIFY")
                msolid.thickness = 0.005
                msolid.offset = 1
                msolid.material_offset_rim = urapolimat_index(obj)
            modu.sort()

        return {'FINISHED'}
########################################

########################################
#除去
########################################
class FUJIWARATOOLBOX_693073(bpy.types.Operator):#除去
    """除去"""
    bl_idname = "fujiwara_toolbox.command_693073"
    bl_label = "除去"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            modu = fjw.Modutils(obj)
            modu.remove_byname("分離エッジ_EDGE_SPLIT")
            modu.remove_byname("分離エッジ_SOLIDIFY")
        return {'FINISHED'}
########################################










#---------------------------------------------
uiitem().vertical()
#---------------------------------------------




# ################################################################################
# #UIカテゴリ
# ########################################
# #テスト用
# ########################################
# class CATEGORYBUTTON_348479(bpy.types.Operator):
#     """テスト用"""
#     bl_idname = "fujiwara_toolbox.categorybutton_348479"
#     bl_label = "テスト用"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem("テスト用",True)
#     uiitem.button(bl_idname,bl_label,icon="",mode="")
#     uiitem.direction = "vertical"

#     def execute(self, context):
#         uicategory_execute(self)
#         return {'FINISHED'}
# ################################################################################




# ########################################
# #TEST
# ########################################
# #bpy.ops.fujiwara_toolbox.testfunc() #TEST
# class FUJIWARATOOLBOX_testfunc(bpy.types.Operator):
#     """テスト用"""
#     bl_idname = "fujiwara_toolbox.testfunc"
#     bl_label = "TEST"
#     bl_options = {'REGISTER', 'UNDO'}

#     uiitem = uiitem()
#     uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         #バックグラウンドGLレンダ
#         exec_externalutils("openglrender.py")
#         return {'FINISHED'}
# ########################################








#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


################################################################################
#UIカテゴリ
########################################
#その他
########################################
class CATEGORYBUTTON_207003(bpy.types.Operator):#その他
    """その他"""
    bl_idname = "fujiwara_toolbox.categorybutton_207003"
    bl_label = "その他"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("その他",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("Plane")
############################################################################################################################



########################################
#DPIを揃える
########################################
class FUJIWARATOOLBOX_718267(bpy.types.Operator):#DPIを揃える
    """DPIを揃える"""
    bl_idname = "fujiwara_toolbox.command_718267"
    bl_label = "DPIを揃える"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        fjw.reject_notmesh()
        obj_active = fjw.active()

        ##板ポリじゃない奴を除外
        #for obj in bpy.context.selected_objects:
        #    if obj.dimensions[1] != 0 and obj.dimensions[2] != 0:
        #        obj.select = False
        #板ポリじゃない＝眼孔
        #正面からの縦横比をあわせるべきでは？
        #modオフにすればよかった…

        targets = fjw.get_selected_list()

        X = 0
        Y = 1
        Z = 2

        width = 0
        height = 1

        base_density = 1

        #縦横比をあわせる
        scaletargets = []
        for target in targets:
            self.report({"INFO"},"target:" + target.name)

            #modオフ
            for mod in target.modifiers:
                mod.show_viewport = False


            V = Y
            #縦軸どっちか
            #でかい方を縦に
            if target.dimensions[Y] < target.dimensions[Z]:
                V = Z

            #イメージを取得して縦横ピクセルを得る
            img = None
            if len(target.material_slots) == 0:
                continue
            mat = target.material_slots[0].material
            
            if len(mat.texture_slots) == 0:
                continue
            if mat.texture_slots[0] == None:
                continue
            tex = mat.texture_slots[0].texture
            if tex == None:
                continue

            img = tex.image
            if img == None:
                continue

            #イメージのサイズ
            #img.size[width]
            #img.size[height]

            #横＝1でやる density=密度
            density = img.size[width] / target.dimensions[X]

            if target == obj_active:
                base_density = density

            self.report({"INFO"},target.name + str(target.dimensions[X]) + "|" + " img" + str(img.size[width]) + " density" + str(density))

            ox = target.dimensions[X]
            if V == Y:
                oy = img.size[height] / density
                oz = target.dimensions[Z]
            else:
                oy = target.dimensions[Y]
                oz = img.size[height] / density
            target.dimensions = (ox,oy,oz)

            if target != obj_active:
                scaletargets.append(target)
        #base_densityを元に各オブジェクトのサイズをあわせる
        for target in scaletargets:
            V = Y
            #縦軸どっちか
            #でかい方を縦に
            if target.dimensions[Y] < target.dimensions[Z]:
                V = Z
            #target.scale = obj_active.scale
            #↑これじゃだめ
            #イメージを取得して縦横ピクセルを得る
            mat = target.material_slots[0].material
            tex = mat.texture_slots[0].texture
            img = tex.image

            #横＝1でやる density=密度
            density = base_density

            ox = img.size[width] / density
            if V == Y:
                oy = img.size[height] / density
                oz = target.dimensions[Z]
            else:
                oy = target.dimensions[Y]
                oz = img.size[height] / density
            target.dimensions = (ox,oy,oz)



        for target in targets:
            #modオン
            for mod in target.modifiers:
                mod.show_viewport = True


        return {'FINISHED'}
########################################


############################################################################################################################
uiitem("開発ヘルパ")
############################################################################################################################

########################################
#アクティブタイプ取得
########################################
class FUJIWARATOOLBOX_468766(bpy.types.Operator):#アクティブタイプ取得
    """アクティブタイプ取得"""
    bl_idname = "fujiwara_toolbox.command_468766"
    bl_label = "アクティブタイプ取得"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        text = bpy.context.active_object.active_material.node_tree.nodes.active.bl_idname
        bpy.data.window_managers['WinMan'].clipboard = text
        
        return {'FINISHED'}
########################################






############################################################################################################################
uiitem("フィニッシング")
############################################################################################################################



########################################
#注意事項
########################################
class FUJIWARATOOLBOX_893322(bpy.types.Operator):#注意事項
    """バックアップを作ってから行うこと。他の3Dビューはとじること。"""
    bl_idname = "fujiwara_toolbox.command_893322"
    bl_label = "注意事項"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        
        return {'FINISHED'}
########################################


########################################
#nゴンチェック
########################################
class FUJIWARATOOLBOX_342881(bpy.types.Operator):#nゴンチェック
    """nゴンチェック"""
    bl_idname = "fujiwara_toolbox.command_342881"
    bl_label = "nゴンチェック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        fjw.reject_notmesh()
        selected = fjw.get_selected_list()

        targets = []
        for obj in selected:
            #if obj in ngon_ok:
            #    continue

            fjw.deselect()
            fjw.activate(obj)

                        #nゴンチェック
            flag_ngon = False
            polys = obj.data.polygons

            for poly in polys:
                if len(poly.vertices) > 4:
                    flag_ngon = True
                    break

            #ngonあった
            if flag_ngon:
                targets.append(obj)

        fjw.globalview()
        fjw.deselect()
        for target in targets:
            target.select = True

        fjw.localview()
        self.report({"INFO"},"これらのオブジェクトにNゴンが含まれているので簡略化オフでのルックを確認してください")

        return {'FINISHED'}
########################################

########################################
#モデル確定
########################################
class FUJIWARATOOLBOX_847775(bpy.types.Operator):#モデル確定
    """モデル確定"""
    bl_idname = "fujiwara_toolbox.command_847775"
    bl_label = "モデル確定"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        start = time.time()

        #subdiv0でbool非表示にしてから、オフ確定すればはやいはず
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 0

        fjw.reject_notmesh()
        bpy.ops.object.duplicates_make_real()
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)



        selected = fjw.get_selected_list()

        #ブーリアン非表示で負荷へらす
        for obj in selected:
            fjw.activate(obj)
            for mod in obj.modifiers:
                if mod.type == "BOOLEAN":
                    mod.show_viewport = False

        bpy.context.scene.render.use_simplify = False
        fjw.apply_mods()


        elapsed_time = time.time() - start
        self.report({"INFO"},("elapsed_time:{0}".format(elapsed_time / 60)) + "[min]")


        return {'FINISHED'}
########################################














########################################
#ポリゴン密度
########################################
class FUJIWARATOOLBOX_809008(bpy.types.Operator):#ポリゴン密度
    """ポリゴン密度"""
    bl_idname = "fujiwara_toolbox.command_809008"
    bl_label = "ポリゴン密度"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        obj = fjw.active()
        
        dim = obj.dimensions
        vol = dim.x * dim.y * dim.z

        polys = len(obj.data.polygons)
        for mod in obj.modifiers:
            if mod.type == "SUBSURF":
                a = 4 ** mod.levels
                polys *= a

        self.report({"INFO"}, obj.name + "面：" + str(polys) + " 密度：" + str(polys / vol))

        
        return {'FINISHED'}
########################################














############################################################################################################################
uiitem("FIX")
############################################################################################################################






########################################
#カメラとランプをレイヤ1に寄せる
########################################
class FUJIWARATOOLBOX_704935(bpy.types.Operator):#カメラとランプをレイヤ1に寄せる
    """カメラとランプをレイヤ1に寄せる"""
    bl_idname = "fujiwara_toolbox.command_704935"
    bl_label = "カメラとランプをレイヤ1に寄せる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.data.objects:
            if (obj.type == "CAMERA") or (obj.type == "LAMP"):
                for layer in obj.layers:
                    layer = False
                obj.layers[0] = True
        
        
        
        
        return {'FINISHED'}
########################################


############################################################################################################################
uiitem("ネームツール")
############################################################################################################################




def packimg():
    for img in bpy.data.images:
        if img != None:
            bpy.ops.image.pack({'edit_image': img},as_png=True)




########################################
#シングルユーザー化
########################################
class FUJIWARATOOLBOX_199389(bpy.types.Operator):#シングルユーザー化
    """シングルユーザー化"""
    bl_idname = "fujiwara_toolbox.command_199389"
    bl_label = "シングルユーザー化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=True, texture=True, animation=False)
        
        
        return {'FINISHED'}
########################################

########################################
#複製
########################################
class FUJIWARATOOLBOX_607832(bpy.types.Operator):#複製
    """複製"""
    bl_idname = "fujiwara_toolbox.command_607832"
    bl_label = "複製生成"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.duplicate()
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=True, texture=True, animation=False)
        obj = bpy.context.active_object
        img = bpy.data.images.new(name = "img",width = 400,height = 400,alpha = True)
        img.generated_color = (0, 0, 0, 0)
        obj.active_material.active_texture.image = img
        
        return {'FINISHED'}
########################################







########################################
#保存
########################################
class FUJIWARATOOLBOX_490317a(bpy.types.Operator):#保存
    """保存"""
    bl_idname = "fujiwara_toolbox.command_490317a"
    bl_label = "保存"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="FILE_TICK",mode="all")

    def execute(self, context):
        packimg()
        bpy.ops.wm.save_mainfile()
        self.report({"INFO"},"saved")
        return {'FINISHED'}
########################################

########################################
#保存して閉じる
########################################
class FUJIWARATOOLBOX_669544a(bpy.types.Operator):#保存して閉じる
    """保存して閉じる"""
    bl_idname = "fujiwara_toolbox.command_669544a"
    bl_label = "保存して閉じる"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="QUIT",mode="all")

    def execute(self, context):
        if bpy.ops.wm.save_mainfile() == {"FINISHED"}:
            packimg()
            bpy.ops.wm.quit_blender()
        else:
            printf("ERROR")
        return {'FINISHED'}
########################################


########################################
#レンダリングのみトグル
########################################
class FUJIWARATOOLBOX_489145(bpy.types.Operator):#レンダリングのみトグル
    """レンダリングのみトグル"""
    bl_idname = "fujiwara_toolbox.command_489145"
    bl_label = "レンダリングのみトグル"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SCENE",mode="")

    def execute(self, context):
        if bpy.context.space_data.show_only_render:
            bpy.context.space_data.show_only_render = False
        else:
            bpy.context.space_data.show_only_render = True
        
        
        
        return {'FINISHED'}
########################################






########################################
#オブジェクトモード
########################################
class FUJIWARATOOLBOX_334541(bpy.types.Operator):#オブジェクトモード
    """オブジェクトモード"""
    bl_idname = "fujiwara_toolbox.command_334541"
    bl_label = "オブジェクトモード"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        return {'FINISHED'}
########################################





########################################
#通常ペン
########################################
class FUJIWARATOOLBOX_878021(bpy.types.Operator):#通常ペン
    """通常ペン"""
    bl_idname = "fujiwara_toolbox.command_878021"
    bl_label = "通常ペン"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="IMAGE_ALPHA",mode="")

    def execute(self, context):
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        bpy.data.brushes["TexDraw"].color = (0, 0, 0)
        bpy.context.scene.tool_settings.unified_paint_settings.size = 1
        bpy.data.brushes["TexDraw"].strength = 1
        bpy.data.brushes["TexDraw"].use_pressure_strength = False
        bpy.data.brushes["TexDraw"].blend = 'MIX'
        
        return {'FINISHED'}
########################################


########################################
#消しゴム アルファ
########################################
class FUJIWARATOOLBOX_114451(bpy.types.Operator):#消しゴム アルファ
    """消しゴム　アルファ"""
    bl_idname = "fujiwara_toolbox.command_114451"
    bl_label = "消しゴム　アルファ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="SEQ_PREVIEW",mode="")

    def execute(self, context):
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        bpy.context.scene.tool_settings.unified_paint_settings.size = 20
        bpy.data.brushes["TexDraw"].blend = 'ERASE_ALPHA'
        
        return {'FINISHED'}
########################################



########################################
#消しゴム 白
########################################
class FUJIWARATOOLBOX_125921(bpy.types.Operator):#消しゴム 白
    """消しゴム　白"""
    bl_idname = "fujiwara_toolbox.command_125921"
    bl_label = "消しゴム　白"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="MATPLANE",mode="")

    def execute(self, context):
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        bpy.data.brushes["TexDraw"].color = (1, 1, 1)
        bpy.context.scene.tool_settings.unified_paint_settings.size = 20
        bpy.data.brushes["TexDraw"].blend = 'MIX'
        return {'FINISHED'}
########################################



########################################
#大ブラシ
########################################
class FUJIWARATOOLBOX_960402(bpy.types.Operator):#大ブラシ
    """大ブラシ"""
    bl_idname = "fujiwara_toolbox.command_960402"
    bl_label = "大ブラシ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="INLINK",mode="")

    def execute(self, context):
        bpy.context.scene.tool_settings.unified_paint_settings.size = 150
        
        return {'FINISHED'}
########################################















############################################################################################################################
uiitem("テキスト")
############################################################################################################################
#########################################
##新規テキスト
#########################################
#class FUJIWARATOOLBOX_816263(bpy.types.Operator):#新規テキスト
#    """新規テキスト"""
#    bl_idname = "fujiwara_toolbox.command_816263"
#    bl_label = "新規テキスト"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")

####    def execute(self, context):
#        bpy.ops.object.text_add(radius=1, view_align=False,
#        enter_editmode=False, location=bpy.context.space_data.cursor_location,
#        layers=layers(put_visible_last=True))
#        bpy.ops.fujiwara_toolbox.command_757107()
#        return {'FINISHED'}
#########################################



########################################
#ヘルパー起動
########################################
class FUJIWARATOOLBOX_757107(bpy.types.Operator):#ヘルパー起動
    """ヘルパー起動"""
    bl_idname = "fujiwara_toolbox.command_757107"
    bl_label = "ヘルパー起動"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="BLENDER")

    def execute(self, context):
        import bpy
        import os
        
        if bpy.data.filepath == "":
            return
        
        dir = os.path.dirname(bpy.data.filepath)
        exefile = "日本語入力ヘルパー.exe"
        exefullpath = dir + os.sep + exefile
        
        if not os.path.exists(exefullpath):
            self.report({"INFO"},"ヘルパーが存在しません。")
            return {'FINISHED'}
        
#        os.system(exefullpath)
        subprocess.Popen(exefullpath)
        
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



########################################
#日本語入力.txt
########################################
class FUJIWARATOOLBOX_542245(bpy.types.Operator):#日本語入力.txt
    """日本語入力.txt"""
    bl_idname = "fujiwara_toolbox.command_542245"
    bl_label = "日本語入力.txt"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_FONT",mode="")

    def execute(self, context):
        if fjw.active() == None or fjw.active().type != "FONT":
            self.report({"INFO"},"テキストオブジェクトを選択してください。")
            return {'FINISHED'}


        import bpy
        import os
        import codecs
        
        if bpy.data.filepath == "":
            self.report({"INFO"},"ファイルが保存されていません。")
            return {'FINISHED'}
        
        dir = os.path.dirname(bpy.data.filepath)
        txtfile = "日本語入力.txt"
        txtfullpath = dir + os.sep + txtfile
        
        if not os.path.exists(txtfullpath):
            self.report({"INFO"},"同じディレクトリに「日本語入力.txt」が見当たりません。")
            return {'FINISHED'}
        
        text = ""
        
        
        #f = open(txtfullpath)
        f = codecs.open(txtfullpath, "r", "utf-8")
        text = f.read()
        f.close()
        
        obj = bpy.context.active_object
        if obj.type != "FONT" or obj.select == False:
            bpy.ops.object.text_add()
        
        obj = bpy.context.active_object
        
        
        obj.data.body = text.replace(text[0],"")
        
        self.report({"INFO"},text)
        
        
        
        #テキストを消す
        f = codecs.open(txtfullpath, "w", "utf-8")
        f.write("")
        f.close()
        return {'FINISHED'}
########################################

########################################
#流し込み
########################################
class FUJIWARATOOLBOX_46615(bpy.types.Operator):#流し込み
    """流し込み"""
    bl_idname = "fujiwara_toolbox.command_46615"
    bl_label = "流し込み"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if fjw.active() == None or fjw.active().type != "FONT":
            self.report({"INFO"},"テキストオブジェクトを選択してください。")
            return {'FINISHED'}

        import bpy
        import os
        import codecs
        import re
        
        if bpy.data.filepath == "":
            self.report({"INFO"},"ファイルが保存されていません。")
            return {'FINISHED'}
        
        dir = os.path.dirname(bpy.data.filepath)
        txtfile = "日本語入力.txt"
        txtfullpath = dir + os.sep + txtfile
        
        if not os.path.exists(txtfullpath):
            self.report({"INFO"},"同じディレクトリに「日本語入力.txt」が見当たりません。")
            return {'FINISHED'}
        
        text = ""
        
        
        #f = open(txtfullpath)
        f = codecs.open(txtfullpath, "r", "utf-8")
        text = f.read()
        f.close()
        text = text.replace(text[0],"")

        obj = bpy.context.active_object
        if obj.type != "FONT" or obj.select == False:
            bpy.ops.object.text_add()
        

        obj = bpy.context.active_object
        base = obj
        
        #sep = "☆セパレータ☆"
        #texts = text.replace().split(sep)
        p = re.compile(r"\n{2,}")
        texts = p.split(text)

        #active().data.body = texts[0]

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        textobjs = []
        for text in texts:
            if text == "":
                continue

            fjw.deselect()
            obj = fjw.active()
            textobjs.append(obj)

            obj.data.body = text

            obj.select = True

            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            dup = fjw.active()
            fjw.deselect()

            dup.location[1] -= obj.dimensions[1] + obj.data.size

        fjw.deselect()
        fjw.delete(fjw.active())
        

        for textobj in textobjs:
            textobj.select = True
        
        fjw.activate(base)
        
        #テキストを消す
        f = codecs.open(txtfullpath, "w", "utf-8")
        f.write("")
        f.close()
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------






########################################
#編集
########################################
class FUJIWARATOOLBOX_665745(bpy.types.Operator):#編集
    """編集"""
    bl_idname = "fujiwara_toolbox.command_665745"
    bl_label = "編集"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="EDIT",mode="")

    def execute(self, context):
        if fjw.active() == None or fjw.active().type != "FONT":
            self.report({"INFO"},"テキストオブジェクトを選択してください。")
            return {'FINISHED'}

        import bpy
        import os
        import codecs
        
        if bpy.data.filepath == "":
            self.report({"INFO"},"ファイルが保存されていません。")
            return {'FINISHED'}
        
        dir = os.path.dirname(bpy.data.filepath)
        txtfile = "日本語入力.txt"
        txtfullpath = dir + os.sep + txtfile
        
        if not os.path.exists(txtfullpath):
            self.report({"INFO"},"同じディレクトリに「日本語入力.txt」が見当たりません。")
            return {'FINISHED'}
        
        
        
        obj = bpy.context.active_object
        if obj.type != "FONT":
            self.report({"INFO"},"非テキストオブジェクト。")
            return {'FINISHED'}
        
        text = obj.data.body
        
        #f = open(txtfullpath,"w")
        f = codecs.open(txtfullpath, "w", "utf-8")
        f.write(text)
        f.close()
        
        
        
        
        return {'FINISHED'}
########################################

########################################
#アクティブへまとめる
########################################
class FUJIWARATOOLBOX_352627(bpy.types.Operator):#アクティブへまとめる
    """アクティブへまとめる"""
    bl_idname = "fujiwara_toolbox.command_352627"
    bl_label = "アクティブへまとめる"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    def execute(self, context):
        obj = fjw.active()
        selected = fjw.get_selected_list()
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.1, view_align=False, location=obj.location, layers=obj.layers)
        empty = fjw.active()

        for slc in selected:
            slc.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)



        return {'FINISHED'}
########################################







############################################################################################################################
uiitem("画像ファイル")
############################################################################################################################


########################################
#外部エディタで編集
########################################
class FUJIWARATOOLBOX_381157(bpy.types.Operator):#外部エディタで編集
    """外部エディタで編集"""
    bl_idname = "fujiwara_toolbox.command_381157"
    bl_label = "外部エディタで編集"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
#        if len(bpy.context.selected_objects) > 20:
#            self.report({"INFO"},"多すぎ注意！！")
#            return {'FINISHED'}
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.active_material != None:
                    if obj.active_material.active_texture != None:
                        if obj.active_material.active_texture.image != None:
                            dir = os.path.dirname(bpy.data.filepath)
                            path = dir + os.sep + obj.active_material.active_texture.image.filepath.replace("//","")
                            bpy.ops.image.external_edit(filepath=path)
        
        
        
        return {'FINISHED'}
########################################

########################################
#選択リロード
########################################
class FUJIWARATOOLBOX_754499(bpy.types.Operator):#選択リロード
    """選択リロード"""
    bl_idname = "fujiwara_toolbox.command_754499"
    bl_label = "選択リロード"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if obj.active_material != None:
                    if obj.active_material.active_texture != None:
                        if obj.active_material.active_texture.image != None:
                            bpy.ops.image.reload({"edit_image":obj.active_material.active_texture.image})
        
        
        return {'FINISHED'}
########################################






########################################
#リロード・開く
########################################
class FUJIWARATOOLBOX_980757(bpy.types.Operator):#リロード・開く
    """リロード・開く"""
    bl_idname = "fujiwara_toolbox.command_980757"
    bl_label = "リロード・開く"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        bpy.ops.fujiwara_toolbox.command_754499()
        bpy.ops.fujiwara_toolbox.command_381157()
        
        return {'FINISHED'}
########################################









#########################################
##全てリロード
#########################################
#class FUJIWARATOOLBOX_821048(bpy.types.Operator):#全てリロード
#    """全てリロード"""
#    bl_idname = "fujiwara_toolbox.command_821048"
#    bl_label = "全てリロード"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
####    def execute(self, context):
#        for obj in bpy.data.objects:
#            if obj.type == "MESH":
#                if obj.active_material != None:
#                    if obj.active_material.active_texture != None:
#                        if obj.active_material.active_texture.image != None:
#                            bpy.ops.image.reload({"edit_image":obj.active_material.active_texture.image})
#
#
#        return {'FINISHED'}
#########################################














############################################################################################################################
uiitem("その他")
############################################################################################################################



########################################
#ビューロックトグル
########################################
class FUJIWARATOOLBOX_938626(bpy.types.Operator):#ビューロックトグル
    """ビューロックトグル"""
    bl_idname = "fujiwara_toolbox.command_938626"
    bl_label = "ロック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        if bpy.context.space_data.lock_camera:
            bpy.context.space_data.lock_camera = False
        else:
            bpy.context.space_data.lock_camera = True
        
        return {'FINISHED'}
########################################

########################################
#LSing
########################################
class FUJIWARATOOLBOX_985887(bpy.types.Operator):#LSing
    """オブジェクトを単一レイヤー化する"""
    bl_idname = "fujiwara_toolbox.command_985887"
    bl_label = "単レ化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    def execute(self, context):
        for obj in bpy.data.objects:
            for l in range(19,0,-1):
                    obj.layers[l] = False
        
        
        
        return {'FINISHED'}
########################################

########################################
#オブジェクトを統合（グルーピング）
########################################
class FUJIWARATOOLBOX_482619(bpy.types.Operator):#オブジェクトを統合（グルーピング）
    """オブジェクトを統合（グルーピング）"""
    bl_idname = "fujiwara_toolbox.command_482619"
    bl_label = "オブジェクトを統合（グルーピング）"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="OBJECT_DATA",mode="")

    def execute(self, context):
        mesh_exists = False
        #メッシュがあればグループ統合、そうじゃなければ普通に統合。
        for obj in fjw.get_selected_list():
            if obj.type == "MESH":
                mesh_exists = True

        if mesh_exists:
            fjw.reject_notmesh()
        
            target = fjw.active()
            for obj in bpy.context.selected_objects:
                fjw.activate(obj)
                fjw.mode("EDIT")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_assign_new()
                vgroup = obj.vertex_groups[len(obj.vertex_groups) - 1]
                vgroup.name = obj.name
                fjw.mode("OBJECT")

                #subsurf以外のmodは適用するべき？

            fjw.activate(target)

        bpy.ops.object.join()
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------







# ########################################
# #プロクシ作成
# ########################################
# class FUJIWARATOOLBOX_b424289a(bpy.types.Operator):#プロクシ作成
#     """プロクシ作成　自動キーフレームオン"""
#     bl_idname = "fujiwara_toolbox.command_b424289a"
#     bl_label = "プロクシ作成"
#     bl_options = {'REGISTER', 'UNDO'}

#     #uiitem = uiitem()
#     #uiitem.button(bl_idname,bl_label,icon="",mode="")

#     def execute(self, context):
#         #blenrig用プロクシの作成
#         fjw.make_proxy("biped_blenrig")
#         #roomtoolsのプロクシ作成（mapcontroller用）を実行
#         bpy.ops.fujiwara_toolbox.command_424289()

#         #make_proxy_all()

#         #プロクシ作るとキーフレームじゃないと保存されなかったりするので自動キーフレームうつ
#         bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        
#         #deselect()
#         #pobj.select = True




#         ##リンクデータのオブジェクト
#         #inlinkobjects = pobj.dupli_group.objects
        
#         #mp_name = ""
#         #for obj in inlinkobjects:
#         #    if "MapController" in obj.name:
#         #        mp_name = obj.name
#         #        break

#         #if mp_name == "":
#         #    self.report({"INFO"},"MapControllerがありません。")
#         #    return {'CANCELLED'}

#         #bpy.ops.object.proxy_make(object=mp_name)

#         #mapcontroller = active()
#         #map.select = True

#         #bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
#         #bpy.ops.object.mode_set(mode='POSE', toggle=False)


#         return {'FINISHED'}
# ########################################


def full_proxy(self):
        #プロクシ＝アニメつけるってことだからオート記録オンに
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        linkobj = fjw.active()
        loc = linkobj.location
        objects = fjw.make_proxy_all()
        for obj in objects:
            if obj.type == "ARMATURE":
                obj.show_x_ray = True
        fjw.deselect()

        bpy.context.space_data.cursor_location = loc
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        empty = fjw.active()
        empty.name = linkobj.name
        empty.rotation_euler = linkobj.rotation_euler

        fjw.select(objects)
        fjw.activate(empty)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        linked_objects = linkobj.dupli_group.objects
        #親子構造の反映
        for obj in objects:
            #プロクシ使う場合トランスフォームはロックした方が望ましい
            #Emptyは除外
            if obj.type != "EMPTY":
                obj.lock_location = (True,True,True)
                obj.lock_rotation = (True,True,True)
                obj.lock_scale = (True,True,True)

            basename = obj.name.replace("_proxy", "").replace(fjw.get_linkedfilename(linkobj) + "/", "")
            baseobj = None
            if basename in linked_objects:
                baseobj = linked_objects[basename]
            else:
                continue

            self.report({"INFO"},"basename" + basename)

            if baseobj.parent == None:
                continue
            
            targetname = fjw.get_linkedfilename(linkobj) + "/" + baseobj.parent.name + "_proxy"
            is_found = False
            for tmp in bpy.data.objects:
                if targetname == tmp.name:
                    is_found = True
            if not is_found:
                continue
            #if targetname not in objects:
            #    continue

            self.report({"INFO"},"targetname" + targetname)

            targetobj = bpy.data.objects[targetname]

            fjw.deselect()
            obj.select = True
            fjw.activate(targetobj)
            #親子=オブジェクト
            if baseobj.parent_type == "OBJECT":
                fjw.mode("OBJECT")
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                pass
            #親子=ボーン
            if baseobj.parent_type == "BONE":
                fjw.mode("POSE")
                targetbonename = baseobj.parent_bone

                #ターゲットのアーマチュアレイヤー全部表示しないとだめ
                baselayers = [True for i in range(32)]
                for i in range(32):
                    baselayers[i] = targetobj.data.layers[i]
                targetobj.data.layers = [True for i in range(32)]
                targetobj.data.bones.active = targetobj.data.bones[targetbonename]
                bpy.ops.object.parent_set(type='BONE_RELATIVE')
                #レイヤー表示を戻す
                targetobj.data.layers = baselayers
                fjw.mode("OBJECT")
                pass

########################################
#プロクシ作成（全）
########################################
class FUJIWARATOOLBOX_248120(bpy.types.Operator):#プロクシ作成（全）
    """グループに含まれるすべてのEmptyとArmatureから親子構造を維持したプロクシを作成する。"""
    bl_idname = "fujiwara_toolbox.command_248120"
    bl_label = "Full Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            fjw.activate(obj)
            full_proxy(self)

        return {'FINISHED'}
########################################


########################################
#Lamp Proxy
########################################
class FUJIWARATOOLBOX_199238(bpy.types.Operator):#Lamp Proxy
    """Lamp Proxy"""
    bl_idname = "fujiwara_toolbox.command_199238"
    bl_label = "Lamp Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        linkobj = fjw.active()
        loc = linkobj.location
        objects = fjw.make_proxy_type("LAMP")
        fjw.deselect()

        for obj in objects:
            if obj == linkobj:
                continue
            obj.layers = bpy.context.scene.layers

        bpy.context.space_data.cursor_location = loc
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=loc, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        empty = fjw.active()
        empty.name = linkobj.name + "_Lamps"
        empty.rotation_euler = linkobj.rotation_euler

        fjw.select(objects)
        linkobj.select = False
        fjw.activate(empty)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        return {'FINISHED'}
########################################























"""
オブジェクトID
    PARENTDATA_OBJECTID
ペアレントデータ
    PARENTDATA_DATA
"""

#すべてのペアレントデータを一旦削除する
def parentdata_deleteall():
    d = "PARENTDATA_OBJECTID"
    for obj in bpy.data.objects:
        if d in obj:
            del obj[d]
    pass

#すべてのオブジェクトにIDを割り当てる
def parentdata_identifyall():
    for obj in bpy.data.objects:
        obj["PARENTDATA_OBJECTID"] = str(random.randint(0,9999999))
    pass

#すべてのオブジェクトの親子情報を格納する
def parentdata_getparentdataall():
    for obj in bpy.data.objects:
        if obj.parent != None:
            obj["PARENTDATA_DATA"] = {"parent":obj.parent["PARENTDATA_OBJECTID"], "type":obj.parent_type, "bone":obj.parent_bone}
    pass


########################################
#ペアレントデータビルド
########################################
class FUJIWARATOOLBOX_95038(bpy.types.Operator):#ペアレントデータビルド
    """ペアレント情報をカスタムデータに格納する"""
    bl_idname = "fujiwara_toolbox.command_95038"
    bl_label = "ペアレントデータビルド"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        parentdata_deleteall()
        parentdata_identifyall()
        parentdata_getparentdataall()
        return {'FINISHED'}
########################################


#ペアレントデータから親子関係をビルドする
def parentdata_buildfromparentdata():
    fjw.mode("OBJECT")
    for obj in bpy.data.objects:
        fjw.deselect()

        #すでに親がある場合はスキップ
        if obj.parent != None:
            continue

        if "PARENTDATA_DATA" in obj:
            obj.select = True
            for target in bpy.data.objects:
                if "PARENTDATA_OBJECTID" in target:
                    if target["PARENTDATA_OBJECTID"] == obj["PARENTDATA_DATA"]["parent"]:
                        fjw.activate(target)
                        break
            
            if obj["PARENTDATA_DATA"]["type"] != "BONE":
                #維持してペアレント
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            else:
                #ボーン相対
                fjw.mode("POSE")
                #ターゲットのアーマチュアレイヤー全部表示しないとだめ
                baselayers = [True for i in range(32)]
                for i in range(32):
                    baselayers[i] = target.data.layers[i]
                target.data.layers = [True for i in range(32)]
                target.data.bones.active = target.data.bones[obj["PARENTDATA_DATA"]["bone"]]
                bpy.ops.object.parent_set(type='BONE_RELATIVE')
                #レイヤー表示を戻す
                target.data.layers = baselayers
                fjw.mode("OBJECT")

        pass

    pass

########################################
#ビルドフロムペアレントデータ
########################################
class FUJIWARATOOLBOX_349810(bpy.types.Operator):#ビルドフロムペアレントデータ
    """ペアレントデータから親子を構築する"""
    bl_idname = "fujiwara_toolbox.command_349810"
    bl_label = "ビルドフロムペアレントデータ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        parentdata_buildfromparentdata()
        return {'FINISHED'}
########################################



#
#
#↑これ、、すでにあった！！！
#
#


########################################
#複製を実体化
########################################
class FUJIWARATOOLBOX_286013(bpy.types.Operator):#複製を実体化
    """複製を実体化+ローカル化も。"""
    bl_idname = "fujiwara_toolbox.command_286013"
    bl_label = "複製を実体化+ローカル化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        selection = fjw.get_selected_list()

        #すべてオブジェクトモードに
        baseobj = fjw.active()
        for obj in bpy.data.objects:
            fjw.activate(obj)
            fjw.mode("OBJECT")
        fjw.activate(baseobj)
        fjw.deselect()
        fjw.select(selection)

        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
        #proxyあると落ちる→アーマチュアの除去処理必要
        #アーマチュア名_proxyで検索して該当を削除する
        deltarget = []
        for obj in selection:
            if obj.type == "ARMATURE":
                proxyname = obj.name + "_proxy"
                if proxyname in bpy.data.objects:
                    deltarget.append(bpy.data.objects[proxyname])
        fjw.delete(deltarget)
        fjw.select(selection)
        bpy.ops.object.make_local(type='SELECT_OBDATA_MATERIAL')

        return {'FINISHED'}
########################################




########################################
#AssetManager用キャラリンク後ポストプロセス
########################################
class FUJIWARATOOLBOX_823369(bpy.types.Operator):#AssetManager用キャラリンク後ポストプロセス
    """AssetManager用キャラリンク後ポストプロセス"""
    bl_idname = "fujiwara_toolbox.command_823369"
    bl_label = "AssetManager用キャラリンク後ポストプロセス"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    def execute(self, context):
        #複製を実体化
        bpy.ops.fujiwara_toolbox.command_286013()


        #オートキーフレームオン
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        #最大フレーム10
        bpy.context.scene.frame_end = 10

        #フレーム1
        bpy.ops.screen.frame_jump(end=False)
        
        #アーマチュアを全部キーフレーム入れる
        for obj in fjw.get_selected_list():
            if obj.type == "ARMATURE":
                fjw.activate(obj)
                fjw.mode("POSE")
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
                fjw.mode("OBJECT")


        #フレーム10に移動
        bpy.ops.screen.frame_jump(end=True)


        return {'FINISHED'}
########################################






#
#   ヘッダーボタン用
#
class MD_SETKEY(bpy.types.Operator):
    """キーフレーム挿入"""
    bl_idname = "fujiwara_toolbox.set_key"
    bl_label = "キーフレーム挿入"

    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            MarvelousDesingerUtils.setkey()
        return {"FINISHED"}


class MD_DELKEY(bpy.types.Operator):
    """キーフレーム削除"""
    bl_idname = "fujiwara_toolbox.del_key"
    bl_label = "キーフレーム削除"

    def execute(self, context):
        selection = fjw.get_selected_list()
        for obj in selection:
            fjw.deselect()
            fjw.activate(obj)
            MarvelousDesingerUtils.delkey()
        return {"FINISHED"}

class MD_export_active_body_mdavatar(bpy.types.Operator):
    """アバター出力"""
    bl_idname = "fujiwara_toolbox.export_active_body_mdavatar"
    bl_label = "アバター出力"

    def execute(self, context):
        MarvelousDesingerUtils.export_selected(False)
        return {"FINISHED"}

#アバター出力して、シミュレーションを走らせる
class MD_export_active_body_mdavatar_sim(bpy.types.Operator):
    """アバター出力"""
    bl_idname = "fujiwara_toolbox.export_mdavatar_uwsc"
    bl_label = "アバター出力して、uwsc経由でシミュレーションを走らせる"

    def execute(self, context):
        MarvelousDesingerUtils.export_selected(True)
        return {"FINISHED"}

class framejump_1(bpy.types.Operator):
    """フレーム移動　1"""
    bl_idname = "fujiwara_toolbox.framejump_1"
    bl_label = "1"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        #bpy.ops.screen.frame_offset(delta=-1)
        return {"FINISHED"}


class framejump_mdhalf(bpy.types.Operator):
    """フレーム移動　5"""
    bl_idname = "fujiwara_toolbox.framejump_mdhalf"
    bl_label = "5"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=MarvelousDesingerUtils.last_frame/2)
        return {"FINISHED"}

class framejump_mdlast(bpy.types.Operator):
    """フレーム移動　10"""
    bl_idname = "fujiwara_toolbox.framejump_mdlast"
    bl_label = "10"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=int(MarvelousDesingerUtils.last_frame - 1))
        return {"FINISHED"}

class framejump_15(bpy.types.Operator):
    """フレーム移動　15"""
    bl_idname = "fujiwara_toolbox.framejump_15"
    bl_label = "15"
    
    def execute(self, context):
        bpy.ops.screen.frame_jump(end=False)
        bpy.ops.screen.frame_offset(delta=14)
        return {"FINISHED"}


class DialogMain(bpy.types.Operator,MyaddonView3DPanel):
    """DialogMain"""
    bl_idname = "object.dialog_mainpanel"
    bl_label = "MainPanel"
    bl_options = {'REGISTER', 'UNDO'}

    calltype = "DIALOG"

    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self,width=500) 
    pass




























############################################################################################################################
uiitem("メモ：T/NパネルはF5で位置入替えできる")
############################################################################################################################




############################################################################################################################
# ボーンリネーマパネル
############################################################################################################################
bpy.types.Scene.fjw_bone_renamer_name = bpy.props.StringProperty()
class BoneRenamer(bpy.types.Panel):
    bl_label = "Bone Renamer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()

        if not pref.maintools:
            return pref.maintools

        active = fjw.active()
        if active is not None:
            if active.type == "ARMATURE" and active.mode == "EDIT":
                return True

        return False

    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene,"fjw_bone_renamer_name","")
        layout.operator("fujiwara_toolbox.rename_bones")
        layout.operator("fujiwara_toolbox.rename_bones_prefix")

        return
    
class FJW_RENAME_BONES(bpy.types.Operator):
    """選択ボーンをリネームする。自動で左右が付加される。"""
    bl_idname = "fujiwara_toolbox.rename_bones"
    bl_label = "リネーム"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        ・真ん中
        ・2個選択
        ・ボーン群
        """
        name = bpy.context.scene.fjw_bone_renamer_name
        armature = fjw.active()

        if armature is None or armature.type != "ARMATURE":
            self.report({"INFO"},"ボーンを選択してください")
            return {'CANCELLED'}

        self.report({"INFO"},name)

        armu = fjw.ArmatureUtils(armature)
        dbones = armu.data_bones
        active_dbone = armu.dataactive()
        selection = []

        for ebone in armu.edit_bones:
            if ebone.select:
                selection.append(ebone)

        centers = []
        left_sides = []
        right_sides = []

        for ebone in selection:
            if ebone.head.x == 0.0:
                centers.append(ebone)
                self.report({"INFO"},"%f"%(ebone.head.x))
                continue
            if ebone.head.x > 0.0:
                left_sides.append(ebone)
                self.report({"INFO"},"%f"%(ebone.head.x))
                continue
            if ebone.head.x < 0.0:
                right_sides.append(ebone)
                self.report({"INFO"},"%f"%(ebone.head.x))
                continue

        for ebone in centers:
            ebone.name = name
            self.report({"INFO"},"center "+ebone.name+" %f"%(ebone.head.x))
        for ebone in left_sides:
            ebone.name = name
            ebone.name = ebone.name + "_L"
            self.report({"INFO"},"left "+ebone.name+" %f"%(ebone.head.x))
        for ebone in right_sides:
            ebone.name = name
            ebone.name = ebone.name + "_R"
            self.report({"INFO"},"right "+ebone.name+" %f"%(ebone.head.x))

        return {'FINISHED'}

class FJW_RENAME_BONES_PREFIX(bpy.types.Operator):
    """プレフィックスを追加"""
    bl_idname = "fujiwara_toolbox.rename_bones_prefix"
    bl_label = "プレフィックス"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selection = []

        armature = fjw.active()
        armu = fjw.ArmatureUtils(armature)
        name = bpy.context.scene.fjw_bone_renamer_name
        for ebone in armu.edit_bones:
            if ebone.select:
                selection.append(ebone)
        for ebone in selection:
            ebone.name = name + "_" + ebone.name

        return {'FINISHED'}











#各メニューへの追加
#https://www.blender.org/api/blender_python_api_2_76b_release/info_tutorial_addon.html
def menu_func_VIEW3D_MT_object_apply(self, context):
#    self.layout.operator(,icon="")
    self.layout.operator("fujiwara_toolbox.command_557231",icon="FILE_TICK")
    self.layout.operator("fujiwara_toolbox.command_661107",icon="FILE_TICK")
    self.layout.operator("fujiwara_toolbox.command_234815",icon="RESTRICT_VIEW_ON")

#http://blender.stackexchange.com/questions/3393/add-custom-menu-at-specific-location-in-the-header
def menu_func_VIEW3D_HT_header(self, context):
    layout = self.layout
    #単レ化はいらない
    active = layout.row(align = True)
    #active.operator("fujiwara_toolbox.command_985887")

    pref = fujiwara_toolbox.conf.get_pref()

    if pref.snap_buttons:
        active = layout.row(align = True)
        #active.label(text="",icon="COLLAPSEMENU")
        active.operator("fujiwara_toolbox.command_357169",icon="SNAP_GRID")
        active.operator("fujiwara_toolbox.command_33358",icon="SNAP_VERTEX")
        #active.operator("fujiwara_toolbox.command_993743",icon="SNAP_EDGE")
        active.operator("fujiwara_toolbox.command_911158",icon="SNAP_FACE")

    if pref.pivot_buttons:
        active = layout.row(align = True)
        active.operator("fujiwara_toolbox.command_59910",icon="CURSOR")
        active.operator("fujiwara_toolbox.command_995874",icon="ROTATECENTER")
        active.operator("fujiwara_toolbox.pivot_to_individual",icon="ROTATECOLLECTION")

    if pref.view_buttons:
        active = layout.row(align = True)
        active.operator("screen.region_quadview",icon="OUTLINER_OB_LATTICE", text="")
        active.prop(bpy.context.space_data, "lock_camera", icon="CAMERA_DATA", text="")
        active.prop(bpy.context.space_data, "show_only_render", icon="RESTRICT_RENDER_OFF", text="")

    if pref.mdframe_buttons:
        active = layout.row(align = True)
        active.prop(bpy.context.tool_settings, "use_keyframe_insert_auto", icon="REC", text="")
        active.operator("fujiwara_toolbox.framejump_1",icon="REW", text="")
        active.operator("fujiwara_toolbox.framejump_mdhalf",icon="SPACE3", text="")
        active.operator("fujiwara_toolbox.framejump_mdlast",icon="FF", text="")
        #active.operator("fujiwara_toolbox.framejump_15",icon="TRIA_RIGHT_BAR", text="")
        active.operator("fujiwara_toolbox.set_key", icon="KEYINGSET", text="")
        active.operator("fujiwara_toolbox.del_key", icon="KEY_DEHLT", text="")
        active.operator("fujiwara_toolbox.md_exportonly", icon="EXPORT", text="")

    if pref.glrenderutils_buttons:
        active = layout.row(align = True)
        active.operator("fujiwara_toolbox.render_cycles_and_edge", text="Render",icon="RENDER_STILL")
        # active.operator("fujiwara_toolbox.glrender", text="GL",icon="RENDER_STILL")
        # active.operator("fujiwara_toolbox.glrender_compomat", text="Render",icon="RENDER_STILL")
        # active.operator("fujiwara_toolbox.command_171760", text="MASK")
        # active.operator("fujiwara_toolbox.command_242623", text="",icon="GREASEPENCIL")

    if pref.maintools_button:
        active = layout.row(align = True)
        active.operator("object.dialog_mainpanel", text="MAIN")

    if pref.localview_button:
        active = layout.row(align = True)
        active.operator("fujiwara_toolbox.command_96321", text="",icon="SOLO_ON")





from bpy.app.handlers import persistent
@persistent
def scene_update_post_handler(dummy):
    bpy.app.handlers.scene_update_post.remove(scene_update_post_handler)

    pref = fujiwara_toolbox.conf.get_pref()
    global assetdir
    assetdir = pref.assetdir


############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    #メニュー追加
    bpy.types.VIEW3D_MT_object_apply.append(menu_func_VIEW3D_MT_object_apply)
    bpy.types.VIEW3D_HT_header.append(menu_func_VIEW3D_HT_header)


    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.scene_update_post.append(scene_update_post_handler)
    pass

def sub_unregistration():
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func_VIEW3D_MT_object_apply)
    bpy.types.VIEW3D_HT_header.remove(menu_func_VIEW3D_HT_header)
    pass


def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)
    sub_unregistration()

if __name__ == "__main__":
    register()