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
    "name": "FJW PageUtils",
    "description": "ページ構成のためのユーティリティ。",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=",
    "category": "Learnbgame"
}

############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#メインパネル
class PageUtils(bpy.types.Panel):#メインパネル
    bl_label = "ページユーティリティ"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_category = "Relations"
    bl_category = "Fujiwara Tool Box"

    @classmethod
    def poll(cls, context):
        pref = conf.get_pref()
        return pref.pageutils

    def draw(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)

        layout = self.layout
        layout.operator("pageutils.popen",icon="FILE_FOLDER")
        layout.operator("pageutils.bgopen",icon="FILE_IMAGE")

        pref = conf.get_pref()

        if "page" in filename:
            layout.label("ページセットアップ")
            row = layout.row(align=True)
            row.operator("pageutils.deploy_pages",icon="IMGDISPLAY")
            layout.label("ページモード")
            row = layout.row(align=True)
            row.operator("pageutils.tocell",icon="FILE_FOLDER")
            row.operator("pageutils.tocell_newwindwow",icon="BLENDER")
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(bpy.context.scene, "newcell_name",text="")
            row.operator("pageutils.newcell",icon="NEW")
            row.operator("pageutils.newcell_copy",icon="GHOST")
            row = col.row(align=True)
            row.operator("pageutils.newcell_copy_browser",icon="GHOST")
            row = col.row(align=True)
            row.operator("pageutils.newcell_copyfromtemplate_browser")
            row = layout.row(align=True)
            col = layout.column(align=True)
            col.label("ページ:" + os.path.splitext(os.path.basename(dir))[0])
            row = col.row(align=True)
            #漫画のとじ順
            row.operator("pageutils.opennextpage",icon="REW")
            row.operator("pageutils.openprevpage",icon="FF")
            
        else:
            layout.label("コマモード")
            row = layout.row(align=True)
            row.label("ページ:" + os.path.splitext(os.path.basename(dir))[0])
            row.label("コマ:" + filename)
            layout = layout.column(align=True)
            layout.operator("pageutils.topage",icon="FILE_TICK")
            row = layout.row(align=True)
            row.operator("pageutils.opennextcell",icon="FRAME_PREV")
            row.operator("pageutils.openprevcell",icon="FRAME_NEXT")
            row = layout.row(align=True)
            row.label("テンプレート")
            row = layout.row(align=True)
            row.prop(bpy.context.scene, "template_name",text="")
            row = layout.row(align=True)
            row.operator("pageutils.saveastemplate")
        if pref.pageutils_show_load_ui:
            row = layout.row(align=True)
            row.prop(bpy.context.user_preferences.filepaths, "use_load_ui")


############################################################################################################################
#ユーティリティ関数
############################################################################################################################
def in_localview():
    if bpy.context.space_data.local_view == None:
        return False
    else:
        return True

def localview():
    if not fjw.in_localview():
        bpy.ops.view3d.localview()

def globalview():
    if fjw.in_localview():
        bpy.ops.view3d.localview()



def qq(str):
    return '"' + str + '"'


def render(renderpath, komarender=False):
        #レンダリング
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.context.scene.render.use_simplify = True
        #特にレベル変更はしない？
        bpy.context.scene.render.simplify_subdivision = 2
        bpy.context.scene.render.simplify_subdivision_render = 2
        bpy.context.scene.render.resolution_percentage = 10
        bpy.context.space_data.show_only_render = True

        #高過ぎる奴対策：レンダ解像度をプレビュー解像度にあわせる！
        for obj in bpy.data.objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               for mod in obj.modifiers:
                   if mod.type == "SUBSURF":
                       mod.render_levels = mod.levels

        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = False
        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
        bpy.context.scene.render.use_raytrace = True
        bpy.context.scene.render.use_textures = True
        bpy.context.scene.render.use_antialiasing = False


        bpy.data.scenes["Scene"].render.filepath = renderpath
        #bpy.ops.render.render(write_still=True)

        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.ops.view3d.viewnumpad(type='CAMERA')
        bpy.ops.render.opengl(write_still=True,view_context=False)

        #設定を見て、プレビューレンダなしならしない
        pref = fujiwara_toolbox.conf.get_pref()
        if komarender and pref.pageutils_cpurender:
            #プレビューレンダをバックグラウンドに投げとく
            #↓コレじゃダメ abspathが特にマズい
            blenderpath = sys.argv[0]
            #scrpath = sys.argv[0] + os.sep + "" + os.sep + "utils" + os.sep +
            #"pagerender.py"
            scrpath = fjw.get_dir(__file__) + "utils" + os.sep + "pagerender.py"
            cmdstr = fjw.qq(blenderpath) + " " + fjw.qq(bpy.data.filepath) + " -b " + " -P " + fjw.qq(scrpath)
            #cmdstr = qq(cmdstr)
            print("********************")
            print("__file__:" + __file__)
            print("scrpath:" + scrpath)
            print("cmdstr:" + cmdstr)
            print("********************")
            subprocess.Popen(cmdstr)

############################################################################################################################
############################################################################################################################
#各ボタンの実装
############################################################################################################################
############################################################################################################################
'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="pageutils.cls"
    bl_label = "ラベル"
    def execute(self,context):
        self.report({"INFO"},"")
        return {"FINISHED"}


'''





############################################################################################################################
#共通
############################################################################################################################
class popen(bpy.types.Operator):
    """親フォルダを開く"""
    bl_idname = "pageutils.popen"
    bl_label = "親フォルダを開く"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        os.system("EXPLORER " + dir)
        return {"FINISHED"}

class bgopen(bpy.types.Operator):
    """background.pngを開きます。"""
    bl_idname = "pageutils.bgopen"
    bl_label = "背景を開く"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        os.system("EXPLORER " + dir + os.sep + "background.png")
        return {"FINISHED"}


def zeropad(i):
    return str(i).zfill(3)

def files_key(file):
    file = re.sub("\d+", zeropad, file)
    return file

def sort_files(files):
    """filesを番号順にソートする。"""
    new_files = sorted(files, key=files_key)
    return new_files

############################################################################################################################
#ページモード
############################################################################################################################

def is_pagemode():
    filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    if "page" not in filename:
        return False
    print("page mode.")
    return True

def refresh_command(self):
    filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    if "page" not in filename:
        return {'CANCELLED'}
    #pageutils/img/を調べる
    dir = os.path.dirname(bpy.data.filepath)
    imgdir = dir + os.sep + "pageutils" + os.sep + "img" + os.sep
    files = os.listdir(imgdir)
    files = sort_files(files)

    #カメラの縦を1とした時の横方向の比率
    wr = bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y

    #カメラの設定
    camera = bpy.context.scene.camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2
    camera.location[0] = 0
    camera.location[1] = -2
    camera.location[2] = 0

    #bpy.context.space_data.lock_camera = False

    yoffset = 0
    for file in files:
        fname, ext = os.path.splitext(file)
        if ext != ".png":
            continue
        
        yoffset += 0.3
        #拡張子除去
        # fname = file.replace(".png","")

        #存在確認 あったらスキップ
        if fname in bpy.data.objects:
            obj = bpy.data.objects[fname]
            obj.location[0] = 0
            obj.location[2] = 0
            obj.show_wire = True
            continue

        self.report({"INFO"},file)
        #板追加
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        obj = bpy.context.scene.objects.active
        obj.name = fname
        obj.show_wire = True

        #UVマップ 変形する前に展開しておくべき
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        #bpy.ops.uv.smart_project()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        #板を立てる
        obj.rotation_euler[0] = 1.5708
        #上下も反転
        obj.rotation_euler[1] = 3.14159

        #比率をカメラに合わせる
        obj.scale[0] = wr
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        #比率が1以上＝横長
        if wr > 1:
            obj.scale = (1 / wr,1 / wr,1 / wr)
            #トランスフォームのアプライ
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


        obj.rotation_euler[1] = 3.14159
        #トランスフォームのアプライ
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        #オブジェクトに位置オフセットをつける
        obj.location[0] = 0
        obj.location[1] = yoffset
        obj.location[2] = 0

        #マテリアル関係
        matname = "コマ_" + fname
        mat = bpy.data.materials.new(name=matname)
        mat.use_transparency = True
        mat.alpha = 0
        mat.use_shadeless = True

        obj.data.materials.append(mat)


        #テクスチャ
        tex = bpy.data.textures.new(file, "IMAGE")
        fjw.load_img(imgdir + file)

        tex.image = fjw.load_img(imgdir + file)

        texture_slot = mat.texture_slots.add()
        texture_slot.texture = tex
        texture_slot.texture = tex
        texture_slot.use_map_alpha = True
        #obj.material_slots[0].material.texture_slots[0].texture = tex

        return True
    return False



class refresh(bpy.types.Operator):
    """コマ画像をスキャンして追加"""
    bl_idname = "pageutils.refresh"
    bl_label = "リフレッシュ"
    def execute(self,context):
        if is_pagemode():
            #ファイルの存在チェック
            # for img in bpy.data.images:
            #     path = bpy.path.abspath(img.filepath)
            #     if not os.path.exists(path):
            #         #ないのでオブジェクト消す
            dellist = []
            for obj in bpy.context.scene.objects:
                if obj.type != "MESH":
                    continue

                #blendファイルの無いものを削除
                #ないならimgも削除すべき
                self_dir = os.path.dirname(bpy.data.filepath)
                imgdir = self_dir + os.sep + "pageutils" + os.sep + "img" + os.sep
                blend_filepath = self_dir + os.sep + obj.name + ".blend"
                if not os.path.exists(blend_filepath):
                    dellist.append(obj)
                    img_path = imgdir + obj.name + ".png"
                    if os.path.exists(img_path):
                        os.remove(img_path)

                #imgのないものは削除
                print("MESH Object")
                for mat in obj.data.materials:
                    print(mat)
                    for tslot in mat.texture_slots:
                        if tslot is not None and tslot.texture is not None and tslot.texture.image is not None:
                            img = tslot.texture.image
                            path = img.filepath
                            print(path)
                            if not os.path.exists(path):
                                bpy.data.images.remove(img)
                                print("not exists:%s"%(path))
                                if obj not in dellist:
                                    dellist.append(obj)
                                    break

            print("dellist:")
            print(dellist)
            fjw.delete(dellist)

            for n in range(50):
                if not refresh_command(self):
                    break
            bpy.ops.file.make_paths_relative()
        return {"FINISHED"}
    def invoke(self, context, event):
        return {'RUNNING_MODAL'}



class deploy_pages(bpy.types.Operator):
    """このフォルダをテンプレートとして、上のフォルダ内にある画像をページフォルダとして展開します。\n既存のフォルダは無視されます。png以外はbackground.pngとしてコピーされません。"""
    bl_idname = "pageutils.deploy_pages"
    bl_label = "ページ展開"
    def execute(self,context):
        self_dir = os.path.dirname(bpy.data.filepath)
        parent_dir = os.path.dirname(self_dir)
        #self.report({"INFO"},parent_dir + ":" + self_dir )

        files = os.listdir(parent_dir)
        files = sort_files(files)

        folder_done = []
        img_done = []
        for file in files:
            name, ext = os.path.splitext(file)
            if re.search("bmp|jpg|jpeg|png", ext, re.IGNORECASE) is None:
                continue

            #ファイル名から連番を抽出 _は残しておく(見開きのため)
            name = re.sub(r"(?![0-9_]).","",name)
            #頭と尻に残った_を削除
            name = re.sub(r"^_+","",name)
            name = re.sub(r"_+$","",name)

            destdir = parent_dir + os.sep + name + os.sep

            #フォルダがあった場合はbackgroundだけコピーする
            flag_folder_exists = os.path.exists(destdir)

            if not flag_folder_exists:
                shutil.copytree(self_dir, destdir)
                folder_done.append(name)

            #background.pngのコピー
            if re.search("png", ext, re.IGNORECASE) is not None:
                pageimgpath = parent_dir + os.sep + file
                destbgimgpath = destdir + os.sep + "background.png"
                shutil.copy(pageimgpath, destbgimgpath)
                img_done.append(file)

        if len(folder_done) == 0:
            self.report({"INFO"},"新規作成フォルダはありません")
            self.report({"INFO"},",".join(img_done) + "をコピーしました")
        else:
            self.report({"INFO"},",".join(folder_done) + "を作成しました")
        return {"FINISHED"}

class tocell(bpy.types.Operator):
    """3Dビューで選択しているコマファイルを開く"""
    bl_idname = "pageutils.tocell"
    bl_label = "コマへ"
    def execute(self,context):
        #self.report({"INFO"},"")
        obj = bpy.context.scene.objects.active
        if obj.type != "MESH":
            self.report({"INFO"},"コマを選択してください")
            return {'CANCELLED'}

        dir = os.path.dirname(bpy.data.filepath)
        cellname = obj.name + ".blend"
        cellpath = dir + os.sep + cellname

        if not os.path.exists(cellpath):
            self.report({"INFO"},"ファイルが存在しません。")
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()

        obj.hide_render = True

        #レンダリング
        renderpath = dir + os.sep + "page.png"
        render(renderpath)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=cellpath)


        return {"FINISHED"}

class tocell_newwindwow(bpy.types.Operator):
    """新しいウィンドウでコマファイルを開く"""
    bl_idname = "pageutils.tocell_newwindwow"
    bl_label = "新窓でコマへ"
    def execute(self,context):
        obj = bpy.context.scene.objects.active
        if obj.type != "MESH":
            self.report({"INFO"},"コマを選択してください")
            return {'CANCELLED'}

        dir = os.path.dirname(bpy.data.filepath)
        cellname = obj.name + ".blend"
        cellpath = dir + os.sep + cellname

        if not os.path.exists(cellpath):
            self.report({"INFO"},"ファイルが存在しません。")
            return {'CANCELLED'}

        #bpy.ops.wm.open_mainfile(filepath=cellpath)
        subprocess.Popen("EXPLORER " + cellpath)

        return {"FINISHED"}

class newcell(bpy.types.Operator):
    """コマを新規作成　未登録のコマが既に存在した場合はそのコマを開く"""
    bl_idname = "pageutils.newcell"
    bl_label = "新規コマ"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        templatepath = fjw.get_resourcesdir() + "pageutils" + os.sep + "cell.blend"

        #保存
        bpy.ops.wm.save_mainfile()

        #ファイル名
        blendname = bpy.context.scene.newcell_name
        if blendname == "":
            for n in range(1,20):
                if str(n) not in bpy.data.objects:
                    blendname = str(n) + ".blend"
                    #存在しなければコピーする。
                    if not os.path.exists(dir + os.sep + blendname):
                        shutil.copyfile(templatepath, dir + os.sep + blendname)
                    break
        else:
            blendname += ".blend"
            #存在しなければコピーする。
            if not os.path.exists(dir + os.sep + blendname):
                shutil.copyfile(templatepath, dir + os.sep + blendname)


        #レンダリング
        #レンダ設定
        #renderpath = dir + os.sep + "pageutils" + os.sep + "page.png"
        renderpath = dir + os.sep + "page.png"
        render(renderpath)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=dir + os.sep + blendname)

        return {"FINISHED"}

def new_cell_copy(path):
    templatepath = path

    #保存
    bpy.ops.wm.save_mainfile()

    #ファイル名
    blendname = bpy.context.scene.newcell_name
    dir = os.path.dirname(bpy.data.filepath)

    if blendname == "":
        for n in range(1,20):
            if str(n) not in bpy.data.objects:
                blendname = str(n) + ".blend"
                #存在しなければコピーする。
                if not os.path.exists(dir + os.sep + blendname):
                    shutil.copyfile(templatepath, dir + os.sep + blendname)
                break
    else:
        blendname += ".blend"
        #存在しなければコピーする。
        if not os.path.exists(dir + os.sep + blendname):
            shutil.copyfile(templatepath, dir + os.sep + blendname)


    #レンダリング
    #レンダ設定
    #renderpath = dir + os.sep + "pageutils" + os.sep + "page.png"
    renderpath = dir + os.sep + "page.png"
    render(renderpath)


    #ページファイルを開く
    bpy.ops.wm.open_mainfile(filepath=dir + os.sep + blendname)
    

class newcell_copy(bpy.types.Operator):
    """コマをコピーして新規作成　未登録のコマが既に存在した場合はそのコマを開く"""
    bl_idname = "pageutils.newcell_copy"
    bl_label = "コピーして新規コマ"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        #templatepath = r"Z:\Google
        #Drive\C#\VS2015projects\3D作業セットアップ\3D作業セットアップ\bin\Debug\単ページ Z固定 レイ影
        #簡略化オン.blend"
        templatepath = dir + os.sep + bpy.context.scene.objects.active.name + ".blend"
        new_cell_copy(templatepath)

        return {"FINISHED"}

class newcell_copy_FileBrowser(bpy.types.Operator):
    """ファイルをコピーしてコマを作成"""
    bl_idname = "pageutils.newcell_copy_browser"
    bl_label = "ブラウザから選択"
    
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
#    http://blender.stackexchange.com/questions/30678/bpy-file-browser-get-selected-file-names
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(self.files) > 0:
            file = self.files[0]
            templatepath = self.directory + file.name
            new_cell_copy(templatepath)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.directory = os.path.dirname(bpy.data.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class necell_copyfromtemplate_FileBrowser(bpy.types.Operator):
    """テンプレートからコピーしてコマを作成"""
    bl_idname = "pageutils.newcell_copyfromtemplate_browser"
    bl_label = "テンプレートから選択"
    
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
#    http://blender.stackexchange.com/questions/30678/bpy-file-browser-get-selected-file-names
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(self.files) > 0:
            file = self.files[0]
            templatepath = self.directory + file.name
            new_cell_copy(templatepath)

        return {'FINISHED'}

    def invoke(self, context, event):
        pagesdir = os.path.dirname(os.path.dirname(bpy.data.filepath))
        templatedir = pagesdir + os.sep + "temlpates"
        self.directory = templatedir
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class openprevpage(bpy.types.Operator):
    """前のページを開く"""
    bl_idname = "pageutils.openprevpage"
    bl_label = "前のページを開く"
    def execute(self,context):
        selfdir = os.path.dirname(bpy.data.filepath)
        parentdir = os.path.dirname(selfdir)

        self.report({"INFO"},"parentdir:" + parentdir)

        #親フォルダ内のディレクトリリスト
        dirs = fjw.getdirs(parentdir)

        targetdir = ""
        for n in range(0, len(dirs)):
            self.report({"INFO"},dirs[n])
            if dirs[n] == os.path.splitext(os.path.basename(selfdir))[0]:
                if n > 0:
                    targetdir = dirs[n - 1]
                break
                    

        target = parentdir + os.sep + targetdir + os.sep + "page.blend"
        if not os.path.exists(target):
            self.report({"INFO"},"ページファイルが存在しません:" + target)
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()
        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)

        #self.report({"INFO"},"")
        return {"FINISHED"}


class opennextpage(bpy.types.Operator):
    """次のページを開く"""
    bl_idname = "pageutils.opennextpage"
    bl_label = "次のページを開く"
    def execute(self,context):
        selfdir = os.path.dirname(bpy.data.filepath)
        parentdir = os.path.dirname(selfdir)

        self.report({"INFO"},"parentdir:" + parentdir)

        #親フォルダ内のディレクトリリスト
        dirs = fjw.getdirs(parentdir)

        targetdir = ""
        for n in range(0, len(dirs)):
            self.report({"INFO"},dirs[n])
            if dirs[n] == os.path.splitext(os.path.basename(selfdir))[0]:
                if n < len(dirs) - 1:
                    targetdir = dirs[n + 1]
                break

        target = parentdir + os.sep + targetdir + os.sep + "page.blend"
        if not os.path.exists(target):
            self.report({"INFO"},"ページファイルが存在しません:" + target)
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()
        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)

        #self.report({"INFO"},"")
        return {"FINISHED"}


def get_paths(dir):
    files = os.listdir(dir)
    files = sort_files(files)
    result = []
    #ファイルのみ結果に追加し、そうでなければ再帰探索
    for file in files:
        path = dir + os.sep + file
        if not os.path.isdir(path):
            result.append(path)
        else:
            result.extend(get_paths(path))
    return result

def get_cellpaths(dir):
    #指定ディレクトリ以下の.blendファイルをすべて取得する
    paths = get_paths(dir)
    result = []

    for path in paths:
        #blendファイルのみ
        if re.search("\.blend", path) is None:
            continue
        #特定ファイルを除外
        if re.search("page\.blend|\.blend\d+", path) is not None:
            continue
        result.append(path)

    return result



def moveup_til_str_dir(path, str):
    #strのディレクトリまで上がる

    #ないならそのまま帰す
    if str not in path:
        return path

    path = os.path.dirname(path)
    if os.path.basename(path) == str:
        return path

    #合わなかったら再帰
    path = moveup_til_str_dir(path, str)
    return path

def get_cells():
    pages_str = (os.sep + "pages" + os.sep)

    if pages_str in bpy.data.filepath :
        #pagesフォルダがあるからそこから取得
        dir = moveup_til_str_dir(bpy.data.filepath,"pages")
        pass
    else:
        #pagesフォルダがパス内にない、ので自フォルダ
        dir = os.path.dirname(bpy.data.filepath)
        pass

    return get_cellpaths(dir)

def get_selfindex_and_cellfilepaths():
    files = get_cells()
    files = sort_files(files)
    selfpath = bpy.data.filepath
    print("get_selfindex_and_cellfilepaths")
    for index, file in enumerate(files):
        print("%s, %s" % (selfpath, file))
        if selfpath == file:
            return index, files
    return None, None

class openprevcell(bpy.types.Operator):
    """前のコマを開く"""
    bl_idname = "pageutils.openprevcell"
    bl_label = "前のコマ"
    def execute(self,context):
        selfindex, filepaths = get_selfindex_and_cellfilepaths()
        if selfindex <= 0:
            self.report({"INFO"},"ファイルが存在しません")
            return {'CANCELLED'}
        target = filepaths[selfindex - 1]

        bpy.context.space_data.lock_camera = False

        #保存
        bpy.ops.wm.save_mainfile()

        fjw.globalview()
        #レンダリング
        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        #レンダ設定
        renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"
        render(renderpath,True)

        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)
        return {"FINISHED"}

class opennextcell(bpy.types.Operator):
    """次のコマを開く"""
    bl_idname = "pageutils.opennextcell"
    bl_label = "次のコマ"
    def execute(self,context):
        selfindex, filepaths = get_selfindex_and_cellfilepaths()
        if selfindex >= len(filepaths) - 1:
            self.report({"INFO"},"ファイルが存在しません")
            return {'CANCELLED'}
        target = filepaths[selfindex + 1]

        bpy.context.space_data.lock_camera = False

        #保存
        bpy.ops.wm.save_mainfile()

        fjw.globalview()
        #レンダリング
        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        #レンダ設定
        renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"
        render(renderpath,True)

        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)
        return {"FINISHED"}

class SaveAsTemplate(bpy.types.Operator):
    """このコマをテンプレートフォルダに保存する"""
    bl_idname = "pageutils.saveastemplate"
    bl_label = "テンプレートとして保存"
    def execute(self,context):
        bpy.ops.wm.save_mainfile()
        pagesdir = os.path.dirname(os.path.dirname(bpy.data.filepath))
        templatedir = pagesdir + os.sep + "temlpates"
        
        if not os.path.exists(templatedir):
            os.mkdir(templatedir)

        blendname = bpy.context.scene.template_name
        templatepath = templatedir + os.sep + blendname + ".blend"

        if blendname == "":
            self.report({"INFO"},"ファイル名を入力してください。")

        # bpy.ops.wm.save_as_mainfile(filepath=templatepath,copy=True)
        shutil.copyfile(bpy.data.filepath, templatepath)

        self.report({"INFO"},templatepath)
        return {"FINISHED"}

############################################################################################################################
#コマモード
############################################################################################################################
class topage(bpy.types.Operator):
    """ページファイルを開く"""
    bl_idname = "pageutils.topage"
    bl_label = "ページ全体に戻る"
    def execute(self,context):
        if bpy.data.filepath == "":
            self.report({"INFO"},"一度も保存されていません")
            return {'CANCELLED'}
        #self.report({"INFO"},"")

        #カメラにキー入れる
        fjw.globalview()
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(bpy.data.objects["Camera"])
        bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')


        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        pname = "page.blend"
        ppath = dir + os.sep + pname

        #ページファイルの存在確認
        if not os.path.exists(ppath):
            self.report({"INFO"},"ページファイルが存在しません")
            return {'CANCELLED'}

        #キーフレーム対策
        #キーフレームオンだと、ツールでカメラ動かした時にトランスフォームが保存されないことがある
        for obj in bpy.data.objects:
            if obj.type == "CAMERA":
                fjw.deselect()
                obj.select = True
                try:
                    bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
                except :
                    pass



        bpy.context.space_data.lock_camera = False

        #保存
        bpy.ops.wm.save_mainfile()

        fjw.globalview()
        #レンダリング
        #レンダ設定
        renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"
        render(renderpath,True)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=ppath)

        return {"FINISHED"}

@persistent
def scene_update_pre(context):
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    bpy.ops.pageutils.refresh()
@persistent
def load_post(context):
    bpy.app.handlers.scene_update_pre.append(scene_update_pre)
@persistent
def save_pre(context):
    #カメラにキー入らんでどうしようもないからこれでいれる！！！→2017/11/26 Blender2.79で修正されているのを確認
    #カメラにキー入れる
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        if bpy.context.scene.camera != None:
            if not fjw.in_localview():
                current = fjw.active()
                current_mode = "OBJECT"
                if current != None:
                    current_mode = fjw.active().mode
                fjw.mode("OBJECT")
                selection = fjw.get_selected_list()
                fjw.deselect()
                fjw.activate(bpy.context.scene.camera)
                bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
                if current != None:
                    fjw.deselect()
                    fjw.select(selection)
                    fjw.activate(current)
                    fjw.mode(current_mode)


@persistent
def rendersize_auto_fitting(context):
    #背景にレンダサイズをあわせる

    pref = fujiwara_toolbox.conf.get_pref()
    if not pref.pageutils or not pref.pageutils_set_res_to_bgimg_onload:
        return
    
    print("bpy.data.filepath:"+bpy.data.filepath)
    if bpy.data.filepath == "":
        return
    
    basename = os.path.basename(bpy.data.filepath)
    name, ext = os.path.splitext(basename)
    
    m = re.fullmatch(r"page|\d+", name)
    if not m:
        return
    
    #背景にサイズをあわせる
    bpy.ops.object.set_resolution_to_bgimg()

    #ハンドラから除去しとく
    #冒頭でハンドラ除去したらそれ以降の処理が死ぬので注意
    #load_postは別に除去の必要ない
    # bpy.app.handlers.load_post.remove(rendersize_auto_fitting)
    

############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    bpy.app.handlers.load_post.append(load_post)
    bpy.types.Scene.newcell_name = bpy.props.StringProperty()
    bpy.types.Scene.template_name = bpy.props.StringProperty()
    bpy.app.handlers.save_pre.append(save_pre)
    bpy.app.handlers.load_post.append(rendersize_auto_fitting)
    pass

def sub_unregistration():
    pass


def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()