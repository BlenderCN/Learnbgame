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

#import mypac.filewrap
#mypac.filewrap.debug = True

from fujiwara_toolbox_modules import fjw, conf


#http://blender.stackexchange.com/questions/717/is-it-possible-to-print-to-the-report-window-in-the-info-view
#info出力はself.report({"INFO"},str)で！

#http://matosus304.blog106.fc2.com/blog-entry-257.html


bl_info = {
    "name": "FJW GroupExtract",
    "description": "オブジェクトをグループ化して別ファイル化、してリンク。",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=",
    "category": "Learnbgame",
}


from bpy.app.handlers import persistent

settings = {
    "basepath":"",
    "extractpath":"",
    "groupname":"",
    "mode":"none"
    }


@persistent
def scene_update_pre(context):
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    test = settings
    bpy.context.scene.group_extract_name = ""
#    bpy.ops.group_extract.loadfunc('INVOKE_DEFAULT')
#    bpy.ops.group_extract.loadfunc('EXEC_DEFAULT')
    bpy.ops.group_extract.loadfunc()


#@persistent
#def returntobase(context):
#    global settings
#    bpy.ops.wm.open_mainfile(filepath=settings["basepath"])

#ロード直後はコンテキストがない問題
#http://blender.stackexchange.com/questions/5813/is-it-possible-to-execute-an-add-on-when-choosing-new-to-open-the-default-file
class groupextract_loadfunc(bpy.types.Operator):
    """ロード時の実実行関数"""
    bl_idname = "group_extract.loadfunc"
    bl_label = "ロード時の実実行関数"
    bl_options = {'REGISTER', 'UNDO'} #?

    def execute(self, context):
        #extract実行開始直後で、新しいファイルを開いた状態
        global settings
        if settings["mode"] == "extract start":
            settings["mode"] == "extract in targetfile"
            #ペーストがコンテキストエラー起こすのでアペンドで処理する。
            #アペンドもエラー起こすからコピーしたファイルでグループ以外を削除。
            for layer in bpy.context.scene.layers:
                layer = True
            for obj in bpy.data.objects:
                obj.hide = False
                obj.hide_select = False
                obj.select = True
            groupname = settings["groupname"]
            
            for group in bpy.data.groups:
                if group.name == groupname:
                    for obj in bpy.data.objects:
                        if obj.name in group.objects:
                            obj.select = False
            #削除
            bpy.ops.object.delete(use_global=False)
            #保存
            bpy.ops.wm.save_as_mainfile()
            settings["mode"] == "extract complete"
            
            #自動で戻る
            #あとここをどうにかすれば！！
#            settings["mode"] = "return to base"
#           ↓落ちる
#            bpy.ops.wm.open_mainfile(filepath=settings["basepath"])
#    
        #戻ってきた
        if settings["mode"] == "return to base":
            bpy.ops.object.delete(use_global=False)
#            
#            bpy.context.space_data.cursor_location[0] = 0
#            bpy.context.space_data.cursor_location[1] = 0
#            bpy.context.space_data.cursor_location[2] = 0
#
            #リンクする
            targetblendpath = settings["extractpath"]
            _directory = targetblendpath + os.sep + "Group" + os.sep
            _filename = settings["groupname"]
            _filepath = _directory +  _filename
            bpy.ops.wm.link(filepath=_filepath, filename=_filename, directory=_directory);
            bpy.ops.file.make_paths_relative();
            #でかいエンプティが邪魔だから縮める
            for obj in bpy.context.selected_objects:
                if obj.type == "EMPTY":
                    obj.empty_draw_size = 0.1
    
            settings["mode"] = "none"
            
            bpy.ops.wm.save_as_mainfile()

#            settings["mode"] == "none"
#            #グループ消去
#            bpy.ops.object.delete(use_global=False)
    
        return {'FINISHED'}

    def invoke(self, context, event):
#        return context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}









class extract(bpy.types.Operator):
    """選択オブジェクトを別ファイルに切り出してグループリンクする。"""
    bl_idname="group_extract.extract"
    bl_label = "Extract"
    
    def execute(self,context):
#        self.report({"INFO"}, context.scene.group_extract_name)
        context.scene.group_extract_name
        dir = os.path.dirname(bpy.data.filepath)
        group = bpy.context.scene.group_extract_name
#        ファイル名_parts
        extractdir = dir + os.sep +os.path.splitext(os.path.basename(bpy.data.filepath))[0] + "_blendparts"
        exstractpath = extractdir + os.sep + group + ".blend"
        if not os.path.exists(extractdir):
            os.mkdir(extractdir)
        
        if group == "":
            self.report({"ERROR"}, "無効なグループ名")
            return {"FINISHED"}
        
        if bpy.data.filepath == "":
            self.report({"ERROR"}, "ファイルが一度も保存されていません！")
            return {"FINISHED"}
        
        #存在確認 あったらしない
        if os.path.exists(exstractpath):
            self.report({"ERROR"}, "既にファイルがあります。")
            return {"FINISHED"}

        bpy.context.space_data.cursor_location[0] = 0
        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0

        
        #エクストラクト実行
        settings["basepath"] = bpy.data.filepath
        settings["extractpath"] = exstractpath
        settings["groupname"] = group
        settings["mode"] = "extract start"
        bpy.ops.group.create(name=settings["groupname"])
        bpy.ops.wm.save_mainfile()
        bpy.ops.wm.save_mainfile(filepath=settings["extractpath"])
        bpy.ops.wm.open_mainfile(filepath=settings["extractpath"])
#        bpy.ops.view3d.copybuffer()
#        bpy.ops.object.delete(use_global=False)
#        bpy.ops.wm.read_homefile()
        
        return {"FINISHED"}


#class extracttomodels(bpy.types.Operator):
#    """../../models/に切り出す"""
#    bl_idname="group_extract.extracttomodels"
#    bl_label = "models/にExtract"
#    
#    def execute(self,context):
##        self.report({"INFO"}, context.scene.group_extract_name)
#        context.scene.group_extract_name
#        dir = os.path.dirname(bpy.data.filepath)
#        group = bpy.context.scene.group_extract_name
#        extractdir = dir;# + os.sep + "blend_parts"
#        extractdir = os.path.dirname(extractdir)
#        extractdir = os.path.dirname(extractdir) + os.sep + "models" + os.sep
#        exstractpath = extractdir + os.sep + group + ".blend"
#        if not os.path.exists(extractdir):
#            os.mkdir(extractdir)
#        
#        if group == "":
#            self.report({"ERROR"}, "無効なグループ名")
#            return {"FINISHED"}
#        
#        if bpy.data.filepath == "":
#            self.report({"ERROR"}, "ファイルが一度も保存されていません！")
#            return {"FINISHED"}
#        
#        #存在確認 あったらしない
#        if os.path.exists(exstractpath):
#            self.report({"ERROR"}, "既にファイルがあります。")
#            return {"FINISHED"}
#
#        bpy.context.space_data.cursor_location[0] = 0
#        bpy.context.space_data.cursor_location[1] = 0
#        bpy.context.space_data.cursor_location[2] = 0
#
#        #エクストラクト実行
#        settings["basepath"] = bpy.data.filepath
#        settings["extractpath"] = exstractpath
#        settings["groupname"] = group
#        settings["mode"] = "extract start"
#        bpy.ops.group.create(name=settings["groupname"])
#        bpy.ops.wm.save_mainfile()
#        bpy.ops.wm.save_mainfile(filepath=settings["extractpath"])
#        bpy.ops.wm.open_mainfile(filepath=settings["extractpath"])
##        bpy.ops.view3d.copybuffer()
##        bpy.ops.object.delete(use_global=False)
##        bpy.ops.wm.read_homefile()
#        
#        return {"FINISHED"}

class extracttomodels(bpy.types.Operator):
    """../../../../models/に切り出す"""
    bl_idname="group_extract.extracttomodels"
    bl_label = "models/にExtract"
    
    def execute(self,context):
#        self.report({"INFO"}, context.scene.group_extract_name)
        context.scene.group_extract_name
        dir = os.path.dirname(bpy.data.filepath)
        group = bpy.context.scene.group_extract_name
        extractdir = dir;# + os.sep + "blend_parts"
        extractdir = os.path.dirname(extractdir)
        extractdir = os.path.dirname(extractdir)
        extractdir = os.path.dirname(extractdir)
        extractdir = os.path.dirname(extractdir) + os.sep + "models" + os.sep
        exstractpath = extractdir + os.sep + group + ".blend"
        if not os.path.exists(extractdir):
            os.mkdir(extractdir)
        
        if group == "":
            self.report({"ERROR"}, "無効なグループ名")
            return {"FINISHED"}
        
        if bpy.data.filepath == "":
            self.report({"ERROR"}, "ファイルが一度も保存されていません！")
            return {"FINISHED"}
        
        #存在確認 あったらしない
        if os.path.exists(exstractpath):
            self.report({"ERROR"}, "既にファイルがあります。")
            return {"FINISHED"}

        bpy.context.space_data.cursor_location[0] = 0
        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0

        #エクストラクト実行
        settings["basepath"] = bpy.data.filepath
        settings["extractpath"] = exstractpath
        settings["groupname"] = group
        settings["mode"] = "extract start"
        bpy.ops.group.create(name=settings["groupname"])
        bpy.ops.wm.save_mainfile()
        bpy.ops.wm.save_mainfile(filepath=settings["extractpath"])
        bpy.ops.wm.open_mainfile(filepath=settings["extractpath"])
#        bpy.ops.view3d.copybuffer()
#        bpy.ops.object.delete(use_global=False)
#        bpy.ops.wm.read_homefile()
        
        return {"FINISHED"}




class returntobase(bpy.types.Operator):
    """returntobase"""
    bl_idname="group_extract.returntobase"
    bl_label = "戻ってリンクする"
    
    def execute(self,context):
        settings["mode"] = "return to base"
        bpy.ops.wm.save_mainfile()
        bpy.ops.wm.open_mainfile(filepath=settings["basepath"])
        return {"FINISHED"}



class regroup(bpy.types.Operator):
    """ファイル名で（再）グループ化"""
    bl_idname="group_extract.regroup"
    bl_label = "ファイル名でグループ化"
    def execute(self,context):
        #ほぼ全オブジェクトを選択
#        for obj in bpy.data.objects:
#            if obj.type != "LAMP" or obj.type != "CAMERA":
#                obj.select = True
#            else:
#                obj.select = False
        #選択オブジェクトのみ。いろいろ除外
        for obj in bpy.data.objects:
            #if obj.type == "LAMP" or obj.type == "CAMERA":
            if obj.type == "CAMERA":
                obj.select = False
        
        #最低限メッシュは必ずグループにいれないと、SHRINKWRAPなんかの対象のが非表示で外れてたりすると死ぬほどめんどくさいことになる
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                obj.select = True
        #アーマチュアもいらないのはない
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                obj.select = True
        #Emptyは保留
        
        groupname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        if groupname in bpy.data.groups:
            #グループ化してた
            bpy.context.scene.objects.active = bpy.data.groups[groupname].objects[0]
            bpy.ops.group.objects_add_active(group=groupname)
        else:
            #してなかった
            bpy.ops.group.create(name=groupname)
        
        return {"FINISHED"}



############################################################################################################################
############################################################################################################################
#パネル部分　メインパネル登録
############################################################################################################################
############################################################################################################################

#メインパネル
class GroupExtract(bpy.types.Panel):#メインパネル
    bl_label = "Group Extract"
    bl_space_type = "VIEW_3D"
#    bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    @classmethod
    def poll(cls, context):
        pref = conf.get_pref()
        return pref.group_extract

    def draw(self, context):
        layout = self.layout
        if settings["mode"] == "none":
            layout.label("Group Name")
            layout.prop(bpy.context.scene, "group_extract_name",text="")
            layout.operator("group_extract.extract",icon="FILE_BLEND")
            layout.operator("group_extract.extracttomodels",icon="OBJECT_DATA")
            layout.operator("group_extract.regroup")

        if settings["mode"] == "extract start":
            layout.operator("group_extract.returntobase",icon="LINK_BLEND")

#        layout.label("basepath:"+settings["basepath"])
#        layout.label("extractpath:"+settings["extractpath"])
#        layout.label("groupname:"+settings["groupname"])
#        layout.label("mode:"+settings["mode"])
        






#ロード後実行のためのクッション

@persistent
def load_post(context):

    bpy.app.handlers.scene_update_pre.append(scene_update_pre)


############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    bpy.types.Scene.group_extract_name = bpy.props.StringProperty()
    bpy.app.handlers.load_post.append(load_post)
    pass

def sub_unregistration():
    bpy.app.handlers.load_post.remove(load_post) 
    pass

def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()


def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()