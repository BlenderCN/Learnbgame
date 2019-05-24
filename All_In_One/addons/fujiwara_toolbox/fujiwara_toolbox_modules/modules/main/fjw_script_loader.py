import bpy
import os
import re
import shutil
import sys
from collections import OrderedDict

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf

import random
from mathutils import *

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
    "category": "Learnbgame",
}

from bpy.app.handlers import persistent
@persistent
def sceneupdate_post_onetime_exectute(context):
    bpy.app.handlers.scene_update_post.remove(sceneupdate_post_onetime_exectute)
    print("::::sceneupdate_post_onetime_exectute called::::")

    if bpy.data.filepath == "":
        return

    #スクリプト探索
    selfdir = os.path.dirname(bpy.data.filepath)
    selfname = os.path.basename(bpy.data.filepath)

    scriptpath = ""
    files = os.listdir(selfdir)
    for file in files:
        if file == selfname + ".py":
            scriptpath = selfdir + os.sep + selfname + ".py"
            break

    if scriptpath == "":
        return

    print("execute:%s" % scriptpath)
    code = ""
    with open(file = scriptpath, encoding = "utf_8_sig") as f:
        code = f.read()
    os.remove(scriptpath)
    exec(code, globals(), locals())


    #実行スクリプト内では
    # override = fjw.get_override("VIEW_3D")
    # bpy.ops.fujiwara_toolbox.command_979047(override)
    #のように扱う

    print("::::sceneupdate_post_onetime_exectute end::::")

    return


# #メインパネル
# class MyaddonView3DPanel(bpy.types.Panel):#メインパネル
#     bl_label = "テストパネル"
#     bl_space_type = "VIEW_3D"
#     #bl_region_type = "UI"
#     bl_region_type = "TOOLS"
#     bl_category = "Fujiwara Tool Box"

#     def draw(self, context):
#         pass
#         # active = cols.column(align=True)
#         # active.label(text="クイック")
#         # active = active.row(align=True)
#         # active.operator("fujiwara_toolbox.command_490317",text="保存",icon="FILE_TICK")
#         # active.operator("fujiwara_toolbox.command_559881",text="保存して開き直す",icon="FILE_REFRESH")



# class framejump_15(bpy.types.Operator):
#     """フレーム移動　15"""
#     bl_idname = "fujiwara_toolbox.framejump_15"
#     bl_label = "15"
#     def execute(self, context):
#         bpy.ops.screen.frame_jump(end=False)
#         bpy.ops.screen.frame_offset(delta=14)
#         return {"FINISHED"}


# from bpy.app.handlers import persistent
# @persistent
# def scene_update_post_handler(dummy):
#     bpy.app.handlers.scene_update_post.remove(scene_update_post_handler)

#     pref = fujiwara_toolbox.conf.get_pref()
#     global assetdir
#     assetdir = pref.assetdir


############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    bpy.app.handlers.scene_update_post.append(sceneupdate_post_onetime_exectute)
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