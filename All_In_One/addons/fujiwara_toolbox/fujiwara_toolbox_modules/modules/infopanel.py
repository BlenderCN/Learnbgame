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

import webbrowser

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
    "category": "Learnbgame"
}



#メインパネル
class Infopanel(bpy.types.Panel):#メインパネル
    bl_label = "Information"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    # @classmethod
    # def poll(cls, context):
    #     pref = fujiwara_toolbox.conf.get_pref()
    #     return pref

    def draw(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)

        layout = self.layout
        layout = layout.column(align=True)
        # active.operator("",icon="", text="")
        active = layout.row(align=True)
        # active.label("")
        active.operator("fujiwara_toolbox.update_fujiwaratoolbox",icon="FILE_REFRESH")
        active = layout.row(align=True)
        active.label("Links", icon="INFO")
        active = layout.row(align=True)
        active.operator("fujiwara_toolbox.open_fujiwara_twitter")
        active.operator("fujiwara_toolbox.open_github")
        active.operator("fujiwara_toolbox.open_scarapbox")


'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="fjw_selector.cls"
    bl_label = "ラベル"
    def execute(self,context):
        self.report({"INFO"},"")
        return {"FINISHED"}
'''

class UpdateFujiwaraToolbox(bpy.types.Operator):
    """Fujiwara Toolboxをアップデートする"""
    bl_idname = "fujiwara_toolbox.update_fujiwaratoolbox"
    bl_label = "アップデート"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dlu = fjw.DownloadUtils()
        dlfilepath = dlu.download("https://github.com/YusukeFujiwara/fujiwara_toolbox/archive/master.zip", "fujiwara_toolbox-master.zip")
        bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=dlfilepath)
        dlu.del_temp()
        self.report({"INFO"}, str("アップデート完了しました。"))
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
class OpenFujiwaraTwitter(bpy.types.Operator):
    """藤原佑介のtwitterを開く"""
    bl_idname = "fujiwara_toolbox.open_fujiwara_twitter"
    bl_label = "twitter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        webbrowser.open("https://twitter.com/GhostBrain3dex")
        return {'FINISHED'}

class OpenGithub(bpy.types.Operator):
    """Fujiwara Toolboxのgithubを開く"""
    bl_idname = "fujiwara_toolbox.open_github"
    bl_label = "GitHub"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        webbrowser.open("https://github.com/YusukeFujiwara/fujiwara_toolbox")
        return {'FINISHED'}

class OpenScrapbox(bpy.types.Operator):
    """Fujiwara ToolboxのScrapboxを開く"""
    bl_idname = "fujiwara_toolbox.open_scarapbox"
    bl_label = "Scrapbox"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        webbrowser.open("https://scrapbox.io/fujiwaratoolbox/")
        return {'FINISHED'}

class OpenDiscord(bpy.types.Operator):
    """Discordサーバー「Blender作業部屋」を開く"""
    bl_idname = "fujiwara_toolbox.open_discord"
    bl_label = "Blender作業部屋"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        webbrowser.open("https://discord.gg/KfWawfQ")
        return {'FINISHED'}

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