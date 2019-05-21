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
import re
import shutil
from fujiwara_toolbox_modules.fjw import *
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
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

#import mypac.filewrap
#mypac.filewrap.debug = True


#http://blender.stackexchange.com/questions/717/is-it-possible-to-print-to-the-report-window-in-the-info-view
#info出力はself.report({"INFO"},str)で！

#http://matosus304.blog106.fc2.com/blog-entry-257.html

bl_info = {
    "name": "FJW AssetManager",
    "description": "アセット管理",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 68, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


#イメージ表示、無理だったので諦める。ファイルブラウザのサムネプレビューでいいじゃん。
#class showimg(bpy.types.Operator):
#    """show"""
#    bl_idname = "object.showimg"
#    bl_label = "showimg"
#    bl_options = {"REGISTER"}
#
#    def execute(self, context):
#            bpy.ops.texture.new();
#            tex = bpy.data.textures[len(bpy.data.textures)-1]
#            tex.name = "sysimg"
#            img = bpy.data.images.load(filepath="g:\\screen.png")
#            tex.type = "IMAGE"
##            tex = recast_type()
#            tex.image = img
##            b.template_preview(img)
##            b.template_image(tex, 'image', tex.image_user)
#
#
#def showimg_ui(self,context):
#    self.layout.template_image(tex, 'image', tex.image_user)
#
#

def group_exists(_directory, _filename, _group):
    _filepath = _directory + os.sep + _filename
    _groupname = _group
    result = False
    with bpy.data.libraries.load(_filepath, link=False, relative=True) as (data_from, data_to):
        if _groupname in data_from.groups:
            result = True
    return result

def auto_group_name(_directory, _filename):
    _groupname = os.path.splitext(os.path.basename(_filename))[0]
    if group_exists(_directory, _filename, _groupname):
        return _groupname
    elif group_exists(_directory, _filename, "MainGroup"):
        _groupname = "MainGroup"
        return _groupname
    return None

#assetdir = r"Z:\WORKSPACE\3D\Asset"
# assetdir = fujiwara_toolbox.conf.assetdir
assetdir = ""#initmylist内で初期化
dirtoopen = assetdir
mode = "link"
chrpostprocess = False

class AMFileBrowser(bpy.types.Operator):
    """Test File Browser"""
    bl_idname = "file.amfilebrowser"
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
        loadfunc(self)


        return {'FINISHED'}

    def invoke(self, context, event):
        global dirtoopen
        self.directory = dirtoopen
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def loadfunc(self):
    """
    選択ファイルのリンク、もしくはアペンド。
    あと、ディレクトリの履歴を追加する。
        
        
    リンク時、
    もし、ファイル名と同じ名前のグループ名があれば、それを普通にグループリンクする
    """
    for obj in bpy.data.objects:
        obj.select = False
        
    global mode
    islink = False
    if mode == "link":
        islink = True
    for obj in bpy.data.objects:
        obj.select = False
        
    for file in self.files:
        self.report({"INFO"},str(file))
        self.report({"INFO"},file.name)

        grouplink = False
        groupappend = False
        groupname = os.path.splitext(os.path.basename(file.name))[0]

        #対象ファイルの走査→グループアペンド、全アペンド、グループリンクの切り替え
        with bpy.data.libraries.load(self.directory + "\\" + file.name, link=islink, relative=True) as (data_from, data_to):
            if mode == "link" and groupname in data_from.groups:
                grouplink = True
                
            if mode == "append" and groupname in data_from.groups:
                groupappend = True

            if not grouplink and not groupappend:
                data_to.objects = data_from.objects
                print(data_to.objects)
        #非グループリンク
        if not grouplink:
            #append
            #グループアペンド
            if groupappend:
                append_group(self, self.directory, file.name)
            else:
                append_all(self, self.directory, file.name)
        #グループリンク
        if grouplink:
            link_group(self, self.directory, file.name)

    #ローカル化
    #bpy.ops.object.make_local(type='SELECT_OBJECT')
    self.report({"INFO"},self.filepath)

#        http://matosus304.blog106.fc2.com/blog-date-201406.html

    #カーソルに移動（buggy）        
    #if bpy.context.scene.AssetManager_settings.movetocursor_bool:
    #    c = bpy.context.space_data.cursor_location
    #    bpy.ops.transform.translate(value=(c[0], c[1], c[2]), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    #キャラ用ポストプロセス
    global chrpostprocess
    if chrpostprocess:
        #→maintools.py参照
        bpy.ops.object.myobject_823369()

    #履歴足す
    additem(self.directory)


def append_auto(self, _directory, _filename):
#    #自動で全部とグループを切り替える
    _filepath = _directory + os.sep + _filename
    _groupname = auto_group_name(_directory, _filename)

    if _groupname is not None:
        append_group(self, _directory, _filename, _groupname)
    else:
        append_all(self, _directory, _filename)

    #コンストレイントターゲットの設定かませとく
    bpy.ops.fujiwara_toolbox.set_camtracker_target()


def append_all(self, _directory, _filename):
    _filepath = _directory + os.sep + _filename
    with bpy.data.libraries.load(_filepath, link=False, relative=True) as (data_from, data_to):
        data_to.objects = data_from.objects

    for obj in data_to.objects:
        #カメラはスキップ。リンクしなければファイル終了時に消える。
        if obj.type == "CAMERA":
            continue
        if obj.parent != None:
            if obj.parent.type == "CAMERA":
                continue
        bpy.context.scene.objects.link(obj)
        obj.select = True


def append_group(self, _directory, _filename, _groupname):
    _filepath = _directory + os.sep + _filename + os.sep + "Group" + os.sep
    deselect()
    bpy.ops.wm.append(filepath=_filepath, filename=_groupname, directory=_filepath)
    if len(bpy.context.selected_objects) != 0:
        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
    
    if bpy.context.scene.objects.active is None:
        if self != None:
            self.report({"WARNING"},"アペンド失敗："+_groupname)
        return

    # グループ名が"MainGroup"だった場合ファイル名をグループ名にする
    if _groupname == "MainGroup":
        gname = os.path.splitext(os.path.basename(_filename))[0]
        for group in bpy.context.scene.objects.active.users_group:
            if "MainGroup" in group.name:
                group.name = gname
                break

def link_group(self, _directory, _filename):
    if self != None:
        self.report({"INFO"},"グループリンク")
    _groupname = auto_group_name(_directory, _filename)
    if _groupname is None:
        if self != None:
            self.report({"WARNING"},"グループなし")
        return

    _filepath = _directory + os.sep + _filename + os.sep + "Group" + os.sep
    bpy.ops.wm.link(filepath=_filepath, filename=_groupname, directory=_filepath)
    # グループ名が"MainGroup"だった場合ファイル名をオブジェクト名にする
    if _groupname == "MainGroup":
        gname = os.path.splitext(os.path.basename(_filename))[0]
        bpy.context.scene.objects.active.name = gname
    bpy.context.scene.objects.active.location = (0,0,0)



class browsercaller(bpy.types.Operator):
    bl_idname = "file.browsercaller"
    bl_label = "browse"
    dir = ""
    def execute(self, context):
        global dirtoopen
        dirtoopen = "Z:\\WORKSPACE\\3D\\Asset\\"
        bpy.ops.file.amfilebrowser("INVOKE_DEFAULT")
        return {"FINISHED"}





#ディレクトリ掘って動的にメニュー作成、っつーのはポップアップメニューでやったほうがいいかも？
#https://www.blender.org/api/blender_python_api_2_76b_release/bpy.types.WindowManager.html#bpy.types.WindowManager.popup_menu
#http://qiita.com/nutti/items/3f75f34adab99a805a35

#http://wiki.blender.org/index.php/Doc:JA/2.6/Manual/Interface/Buttons_and_Controls
#メニューボタンを使うべきっぽい
#http://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Interface
#→template_list
#http://blenderartists.org/forum/showthread.php?194518-How-to-use-template_list
#http://www.pasteall.org/15006/python




############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################


#http://www.pasteall.org/15006/python
#http://www.sinestesia.co/tutorials/making-uilists-in-blender/





#UIList(bpy_struct)
#Basic UIList Example¶
#https://www.blender.org/api/blender_python_api_2_65_5/bpy.types.UIList.html


#http://www.sinestesia.co/tutorials/making-uilists-in-blender/
import bpy.props as prop
 
 
class ListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """
 
    name = prop.StringProperty(name="Name",
           description="A name for this item",
           default="Untitled")
 
    random_prop = prop.StringProperty(name="Any other property you want",
           description="",
           default="")
           
    full_path = prop.StringProperty(name="full_path",
           description="A name for this item",
           default="Untitled")
 
 
class MY_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
 
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'
 
        layout.label(item.name)
        # Make sure your code supports all 3 layout types
#        if self.layout_type in {'DEFAULT', 'COMPACT'}:
#            layout.label(item.name, icon = custom_icon)
#
#        elif self.layout_type in {'GRID'}:
#            layout.alignment = 'CENTER'
#            layout.label("", icon = custom_icon)

#http://blender.stackexchange.com/questions/35007/how-can-i-add-a-checkbox-in-the-tools-ui
class AssetManagerSettings(PropertyGroup):
    movetocursor_bool = BoolProperty(name="3Dカーソルに移動",
        description="取り込み後3Dカーソルに移動する",
        default = False)

class LIST_OT_NewItem(bpy.types.Operator):
    """ Add a new item to the list """
 
    bl_idname = "my_list.new_item"
    bl_label = "Add a new item"
 
    def execute(self, context):
        context.scene.my_list.add()
 
        return{'FINISHED'}
 


class testbtn(bpy.types.Operator):
    """test"""
    bl_idname = "my_list.test"
    bl_label = "test list"
    
    def execute(self, context):
        self.report({"INFO"},context.scene.my_list[context.scene.list_index].name)
        
        return{'FINISHED'}

def additem(item):
    bpy.ops.my_list.new_item()
    listitem = bpy.context.scene.my_list[len(bpy.context.scene.my_list) - 1]
    listitem.full_path = item
    listitem.name = item.replace(assetdir,".")
    
    


diglevel = 3
dirlist = []
def getdirlist(self,dir):
    global dirlist
    global diglevel
    
    if not os.path.isfile(dir):
        if dir not in dirlist:
            if dir.replace(assetdir,"").count("\\") < diglevel:
                dirlist.append(dir)
                pathlist = os.listdir(dir)
                for path in pathlist:
                    getdirlist(self,dir + "\\" + path)
    

class initmylist(bpy.types.Operator):
    """initmylist"""
    bl_idname = "my_list.initmylist"
    bl_label = "initmylist"

    def execute(self, context):
        global assetdir
        assetdir = conf.get_pref().assetdir
        print("assetdir"+assetdir)
        #初期化
        list = context.scene.my_list
        for i in range(0, len(list)):
            list.remove(0)
        
        
        global dirlist
        dirlist = []
        getdirlist(self,assetdir)
        
        
        for dir in dirlist:
            additem(dir)
        
        #名前の省略処理
        repto = "　"
        for path in bpy.context.scene.my_list:
            #reptoは一回除去する
            reptargettext = path.name.replace(repto,"") + os.sep

            
            for target in bpy.context.scene.my_list:
                target.name = target.name.replace(reptargettext, repto)


        #自分のフォルダ
        models = os.path.dirname(bpy.data.filepath)
        additem(models)
        #各話フォルダ依存のmodels
        #additem("..\\..\\models")
        models = os.path.dirname(os.path.dirname(os.path.dirname(bpy.data.filepath))) + "\\models"
        additem(models)
        #シリーズフォルダ依存のmodels
        #additem("..\\..\\..\\..\\models")
        models = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(bpy.data.filepath))))) + "\\models"
        additem(models)

        
        return{'FINISHED'}



class digplus(bpy.types.Operator):
    """digplus"""
    bl_idname = "my_list.digplus"
    bl_label = "digplus"
    
    def execute(self, context):
        global diglevel
        diglevel = diglevel + 1
        bpy.ops.my_list.initmylist()
        return {"FINISHED"}

class digminus(bpy.types.Operator):
    """digminus"""
    bl_idname = "my_list.digminus"
    bl_label = "digminus"
    
    def execute(self, context):
        global diglevel
        diglevel = diglevel - 1
        if diglevel < 1:
            diglevel = 1
        bpy.ops.my_list.initmylist()
        return {"FINISHED"}









def setopentarget(self,context):
    dirtoopen = context.scene.my_list[context.scene.list_index].full_path
    self.filepath = context.scene.my_list[context.scene.list_index].full_path + os.sep
    self.directory = context.scene.my_list[context.scene.list_index].full_path




class FileBrowser_fjwAppend(bpy.types.Operator):
    """アペンド"""
    bl_idname = "file.fjw_append"
    bl_label = "Append"
    
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob = StringProperty(default="*.blend",options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        deselect()
        for file in self.files:
            append_auto(self, self.directory, file.name)

        return {'FINISHED'}

    def invoke(self, context, event):
        setopentarget(self,context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}




#class appendcall(bpy.types.Operator):
#    """appendcall"""
#    bl_idname = "my_list.appendcall"
#    bl_label = "appendcall"
    
#    def execute(self, context):
#        global mode
#        global dirtoopen
#        global chrpostprocess
#        mode = "append"
#        chrpostprocess = False
#        dirtoopen = context.scene.my_list[context.scene.list_index].full_path
#        bpy.ops.file.amfilebrowser("INVOKE_DEFAULT")
#        return {"FINISHED"}


class FileBrowser_fjwLink(bpy.types.Operator):
    """グループリンク"""
    bl_idname = "file.fjw_link"
    bl_label = "Link"
    
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob = StringProperty(default="*.blend",options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        deselect()
        for file in self.files:
            link_group(self, self.directory, file.name)

        return {'FINISHED'}

    def invoke(self, context, event):
        setopentarget(self,context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}





# class FileBrowser_fjwCharacterAppend(bpy.types.Operator):
#     """キャラアペンド"""
#     bl_idname = "file.fjw_characterappend"
#     bl_label = "キャラアペンド"
    
#     filename = bpy.props.StringProperty(subtype="FILE_NAME")
#     filepath = bpy.props.StringProperty(subtype="FILE_PATH")
#     directory = bpy.props.StringProperty(subtype="DIR_PATH")
#     files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
#     filter_glob = StringProperty(default="*.blend",options={'HIDDEN'})
    
#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):
#         deselect()
#         for file in self.files:
#             link_group(self, self.directory, file.name)


#         bpy.ops.object.myobject_823369()
#         return {'FINISHED'}

#     def invoke(self, context, event):
#         setopentarget(self,context)
#         context.window_manager.fileselect_add(self)
#         return {'RUNNING_MODAL'}


class FileBrowser_fjwCopyandLink(bpy.types.Operator):
    """.blendファイル位置に対象をコピーしてからリンクする"""
    bl_idname = "file.fjw_copyandlink"
    bl_label = "コピーしてリンク"
    
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob = StringProperty(default="*.blend",options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        if bpy.data.filepath == "":
            return False
        return True

    def execute(self, context):
        blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        blenddir = os.path.dirname(bpy.data.filepath)
        destdir = blenddir + os.sep + blendname + "_blendparts"

        if not os.path.exists(destdir):
            os.mkdir(destdir)

        deselect()
        for file in self.files:
            shutil.copy(self.directory + os.sep + file.name, destdir)
            link_group(self, destdir, file.name)

        return {'FINISHED'}

    def invoke(self, context, event):
        setopentarget(self,context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class open_folder(bpy.types.Operator):
    """open_folder"""
    bl_idname = "my_list.open_folder"
    bl_label = "open_folder"
    
    def execute(self, context):
        dir = context.scene.my_list[context.scene.list_index].full_path
        os.system("EXPLORER " + dir)

        return {"FINISHED"}


class open_linkedfolder(bpy.types.Operator):
    """オブジェクトにリンクされたファイルの場所を開く"""
    bl_idname = "object.fjw_openlinkedfolder"
    bl_label = "フォルダを開く"
    
    def execute(self, context):
        obj = active()
        if obj.type == "EMPTY":
            linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
            self.report({"INFO"},linkedpath)
            os.system("EXPLORER " + os.path.dirname(linkedpath)+os.sep)
            #os.system("EXPLORER " + linkedpath)
        return {"FINISHED"}

class open_linkedfile(bpy.types.Operator):
    """オブジェクトにリンクされたファイルを開く"""
    bl_idname = "object.fjw_openlinkedfile"
    bl_label = "ファイルを開く"
    
    def execute(self, context):
        obj = active()
        if obj.type == "EMPTY":
            linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
            self.report({"INFO"},linkedpath)
            #os.system("EXPLORER " + os.path.dirname(linkedpath)+os.sep)
            os.system("EXPLORER " + linkedpath)
        return {"FINISHED"}


#既にプロクシ作ってるヤツのリンクを更新するとプロクシが壊れる。危険なので封印。
#class link_reload(bpy.types.Operator):
#    """リンクを更新する"""
#    bl_idname = "object.fjw_linkreload"
#    bl_label = "リンクを更新"
    
#    def execute(self, context):
#        selection = get_selected_list()
#        for obj in selection:
#            if obj.type == "EMPTY":
#                #bpy.data.objects["川と橋"].dupli_group.library.reload()
#                if obj.dupli_group != None:
#                    obj.dupli_group.library.reload()

#        #obj = active()
#        #if obj.type == "EMPTY":
#        #    linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
#        #    self.report({"INFO"},linkedpath)
#        #    #os.system("EXPLORER " + os.path.dirname(linkedpath)+os.sep)
#        #    os.system("EXPLORER " + linkedpath)
#        return {"FINISHED"}

link_additional_group_groups = []
class link_additional_group(bpy.types.Operator):
    """グループを追加リンクする"""
    bl_idname = "object.fjw_link_additional_group"
    bl_label = "グループを追加リンクする"


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
        base = active()

        group = self.group_list
        _groupname = group
        _filepath = self.linkedpath + os.sep + "Group" + os.sep

        bpy.ops.wm.link(filepath=_filepath, filename=_groupname, directory=_filepath)
        linked = active()

        linked.location = base.location
        linked.rotation_euler = base.rotation_euler
        linked.rotation_quaternion = base.rotation_quaternion
        linked.scale = base.scale
        activate(base)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


        return {"FINISHED"}

    def invoke(self, context, event):
        global link_additional_group_groups
        link_additional_group_groups = []
        self.groups = []
        self.linkedpath = ""
        obj = active()
        if obj.type == "EMPTY":
            self.linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)


            with bpy.data.libraries.load(self.linkedpath, link=False, relative=True) as (data_from, data_to):
                for groupname in data_from.groups:
                    self.groups.append(groupname)
        link_additional_group_groups = self.groups
        return context.window_manager.invoke_props_dialog(self)


#メインパネル
class AssetManager(bpy.types.Panel):#メインパネル
    bl_label = "AssetManager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    movetocursor_bool = BoolProperty(name="カーソルに移動", description="取り込み後、3Dカーソルに移動する", default = False)

    @classmethod	
    def poll(cls, context):	
        pref = conf.get_pref()	
        return pref.asset_manager

    def draw(self, context):
#        l = self.layout
#        r = l.row()
#        b = r.box()

        layout = self.layout
        
        scene = context.scene


        #layout.prop(bpy.context.scene.AssetManager_settings, "movetocursor_bool", text="3Dカーソルに移動")
        row = layout.row(align=True)
        #row.operator('my_list.initmylist', text='INIT')
        row.operator('file.fjw_append')
        row.operator('file.fjw_link')
        # row.operator('file.fjw_characterappend')
        row = layout.row(align=True)
        row.operator('file.fjw_copyandlink')

        row = layout.row(align=True)
        row.operator('my_list.open_folder', text='フォルダを開く')


        row = layout.row()
        row.template_list("MY_UL_List", "The_List", scene, "my_list", scene, "list_index" , rows=20)
        
        row = layout.row()
        row.operator('my_list.digminus', text='-')
        row.operator('my_list.digplus', text='+')
 
        layout.label("ファイル名と同じグループ名があればグループリンクになる。")


        layout.label("リンクユーティリティ")
        row = layout.row(align=True)
        row.operator('object.fjw_openlinkedfolder')
        row.operator('object.fjw_openlinkedfile')
        row = layout.row(align=True)
        #既にプロクシ作ってるヤツのリンクを更新するとプロクシが壊れる。危険なので封印。
        #row.operator('object.fjw_linkreload')
        #row = layout.row(align=True)
        row.operator('object.fjw_link_additional_group')

#        row.operator('my_list.new_item', text='NEW')
#       draw内でデータ変更無理だってさ。
#        for i in range(0,10):
##            bpy.ops.my_list.new_item()
#            bpy.context.scene.my_list.add()
        


#        if scene.list_index >= 0 and len(scene.my_list) > 0:
#            item = scene.my_list[scene.list_index]
#
#            row = layout.row()
#            row.prop(item, "name")
#            row.prop(item, "random_property")

#        #ボタン同士をくっつける
#        b = b.column(align=True)
#
#        b.label(text="label
#        test\+tdsfasdfsadgadsfdsaghaefdsgfhsreyatfsesteset")
#        b.label(text="テスト")

        #ボタンリストのボタンを登録
#        lln = 0
#        for btn in ButtonList:
#            #テキストラベルの登録
#            if LabelList[lln] != "":
#                b.label(text=LabelList[lln])
#            lln+=1
#            #ボタンの登録
#            b.operator(btn)
#        b.operator("file.browsercaller")




#        sce= context.scene
#        b.template_list(sce, 'my_list', sce, 'my_list_index', rows= 3)
#        col = b.column(align=True)
#        col.operator('my_list.add', text="", icon="ZOOMIN")
#        col.operator('my_list.remove', text="", icon="ZOOMOUT")
#メモ：bpy.types.Panelからレイアウトのマニュアル探す





"""

template_image

https://www.blender.org/api/blender_python_api_2_65_5/bpy.types.UILayout.html?highlight=row#bpy.types.UILayout.template_image


Asset Flinger

objItem['icon'] = bpy.data.images.load(filepath = iconFile)




class TEXTURE_PT_preview(TextureButtonsPanel, Panel):
    bl_label = "Preview"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        slot = getattr(context, "texture_slot", None)
        idblock = context_tex_datablock(context)

        if idblock:
            layout.template_preview(tex, parent=idblock, slot=slot)
        else:
            layout.template_preview(tex, slot=slot)

        #Show Alpha Button for Brush Textures, see #29502
        if context.space_data.texture_context == 'BRUSH':
            layout.prop(tex, "use_preview_alpha")


Image.name Box gui how?

http://blenderartists.org/forum/archive/index.php/t-253094.html


Show image in panel

http://blender.stackexchange.com/questions/8642/show-image-in-panel



 How to add a texture to an object with Python in Blender 2.5 ?

http://blenderartists.org/forum/archive/index.php/t-178488.html

"""

from bpy.app.handlers import persistent

@persistent
def load_post_handler(dummy):
    bpy.app.handlers.scene_update_post.append(scene_update_post_handler)

@persistent
def scene_update_post_handler(dummy):
    bpy.app.handlers.scene_update_post.remove(scene_update_post_handler)
    bpy.ops.my_list.initmylist()


############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    # bpy.utils.register_class(ListItem)
    # bpy.utils.register_class(MY_UL_List)
    # bpy.utils.register_class(LIST_OT_NewItem)
    # bpy.utils.register_class(AssetManagerSettings)
#    bpy.utils.register_class(testbtn)
 
    bpy.types.Scene.my_list = prop.CollectionProperty(type = ListItem)
    bpy.types.Scene.list_index = prop.IntProperty(name = "Index for my_list", default = 0)
    bpy.types.Scene.AssetManager_settings = PointerProperty(type=AssetManagerSettings)
    
    bpy.app.handlers.load_post.append(load_post_handler)


def sub_unregistration():
    del bpy.types.Scene.my_list
    del bpy.types.Scene.list_index
    del bpy.types.Scene.AssetManager_settings
    
    bpy.utils.unregister_class(ListItem)
    bpy.utils.unregister_class(MY_UL_List)
    bpy.utils.unregister_class(LIST_OT_NewItem)
#    bpy.utils.unregister_class(testbtn)
 




def register():    #登録
    sub_registration()
    bpy.utils.register_module(__name__)
   


def unregister():    #登録解除
    sub_unregistration()
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()