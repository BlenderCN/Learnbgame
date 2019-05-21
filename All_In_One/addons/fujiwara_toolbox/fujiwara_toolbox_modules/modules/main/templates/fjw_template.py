import bpy
import sys
import inspect
#パス関連のユーティリティ
#http://xwave.exblog.jp/7155003
import os.path
import os
import bmesh
import datetime
import math
import subprocess
import shutil
import time
import copy
from collections import OrderedDict

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf


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


#アドオンごとに固有値を設定すること
addon_idname_postfix = "_template"
addon_panel_name = "Template"

############################################################################################################################
#メインパネル クラス名変更すること。
############################################################################################################################
class TemplateView3DPanel(bpy.types.Panel):#メインパネル
    bl_label = addon_panel_name
    bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    def draw(self, context):
        l = self.layout
        r = l.row()
        #b = r.box()
        b = r

        #ボタン同士をくっつける
        #縦並び
        cols = b.column(align=True)
        active = cols

        active = active.row(align=True)
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
    bl_idname = "object.dialog"+addon_idname_postfix
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





#UIカテゴリの実行部を外部化。いろいろ処理できるように。
def uicategory_execute(self):
    global dialog_uicat
    dialog_uicat = self.bl_label
    eval('bpy.ops.object.dialog'+addon_idname_postfix+'("INVOKE_DEFAULT")')
    



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

    ###################################
    #処理部分
    ###################################
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
    icon="UNPINNED"

    #ui自動登録はなし

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        global pendings
        pendings = []
        
        return {'FINISHED'}
########################################


############################################################################################################################
############################################################################################################################
#メインパート
############################################################################################################################
############################################################################################################################

################################################################################
#UIカテゴリ
########################################
#test
########################################
class CATEGORYBUTTON_323329(bpy.types.Operator):#test
    """test"""
    bl_idname = "fujiwara_toolbox.categorybutton_323329"
    bl_label = "test"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem("test",True)
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    uiitem.direction = "vertical"

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        uicategory_execute(self)
        return {'FINISHED'}
########################################
################################################################################



########################################
#dummy
########################################
class FUJIWARATOOLBOX_794868(bpy.types.Operator):#dummy
    """dummy"""
    bl_idname = "fujiwara_toolbox.command_794868"
    bl_label = "dummy"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        
        return {'FINISHED'}
########################################























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