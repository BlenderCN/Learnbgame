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
import inspect

# import bpy.mathutils.Vector as Vector
from mathutils import Vector

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
from fujiwara_toolbox_modules.fjw import JsonTools

import random
from mathutils import *

"""
MarvelousDesignerまわりの仕様
カスタムプロパティを使用してコントロールする。

基本設定
md_garment_path_list   ["pathA", "pathB", "pathC"]ってかんじでカスタムプロパティに打ち込む。
                        追加はコマンドから行った方がよさそう。ファイルブラウザで。
md_export_id int このパーツのエクスポートID　このプロパティがあったらアバターとして出力する

運用設定
md_garment_index    パスリストの何番目の衣装を使うか。なければ-1として扱う。
                    ない場合はリンク先フォルダの同名.zpacを使う。
md_export_depth     intかintのlist
                    IDのどのレベルまでエクスポートするか。
                    listだった場合は該当レベルを個別に有効にする。
                    なければ0。
こっちの値、作業ファイル準備時に反映しなければならない！

カスタムプロパティはいずれのオブジェクトにつけてもいい。
MDObjectにわたされたオブジェクト群の中で検索する。
"""

def get_mddatadir(add_sep=True):
    # mdtemp_dir = r"C:" + os.sep + "fjw_mdtemp"
    mdtemp_dir = r"C:\fjwmdtemp"
    if not os.path.exists(mdtemp_dir):
        os.makedirs(mdtemp_dir)
    if add_sep:
        mdtemp_dir += os.sep
    return mdtemp_dir


class MDCode():
    codename = "mdcode"

    def __init__(self):
        """Marvelous Designerに食わせるコードを生成するクラス"""
        pass
    
    def get_existingfile(self):
        dir_path = get_mddatadir()
        if not os.path.exists(dir_path):
            return None

        files = os.listdir(dir_path)
        for file in files:
            name, ext = os.path.splitext(file)
            if ext != ".py":
                continue
            if self.codename not in name:
                continue
            return dir_path + os.sep + file
        return None

    # initialcode = "import fjwMDControl.MD as MD\n"
    initialcode = ""

    def create(self):
        # self.code_path = get_mddatadir() + self.codename + fjw.random_id(16) + ".py"
        self.code_path = get_mddatadir() + self.codename + ".py"
        f = open(self.code_path, "w")
        f.write(self.initialcode)
        return f

    def open(self, mode="a"):
        self.code_path = self.get_existingfile()
        print(self.code_path)
        if self.code_path is None:
            return self.create()
        return open(self.code_path, mode)
        
    def addline(self, avatar_path, cloth_path):
        f = self.open()
        output_path = os.path.splitext(avatar_path)[0] + ".obj"
        # f.write('MD.simulate("%s", "%s", "%s")\n'%(avatar_path, cloth_path, output_path))
        f.write('%s,%s,%s\n'%(avatar_path, cloth_path, output_path))
        f.close()

    def removeline(self, searchword):
        newdata = ""
        f = self.open("r")
        lines = f.readlines()
        for line in lines:
            if searchword in line:
                continue
            newdata += line
        f.close()
        f = self.open("w")
        f.write(newdata)
        f.close()

class MDJson():
    def __init__(self):
        self.jsonpath = get_mddatadir() + "mddata.json"
        self.jsondata = JsonTools(self.jsonpath)
    
    def add_fileentry(self, obj_name):
        """エクスポートしたファイルと、エクスポート元のファイルを対応させるエントリ"""
        entry_name = self.new_entryname()
        # self.jsondata.val("fileentry/%s/%s"%(bpy.data.filepath, obj.name), entry_name)
        self.jsondata.val("entry/%s/filepath"%entry_name, bpy.data.filepath.replace("_MDWork",""))
        self.jsondata.val("entry/%s/obj"%entry_name, obj_name)
        self.jsondata.save()
        return entry_name
    
    def get_entry_name(self, obj):
        """ファイルパスとobjからエントリの名前を得る"""
        # entry_name = self.jsondata.val("fileentry/%s/%s"%(bpy.data.filepath, obj.name))
        dic = self.jsondata.dictionary
        for entry_name in dic["entry"]:
            if dic["entry"]["filepath"] == bpy.data.filepath:
                if dic["entry"]["obj"] == obj.name:
                    return entry_name
        return None
    
    def remove_entry(self, name):
        dic = self.jsondata.dictionary
        dellist = []
        if "entry" in dic:
            for entry_name in dic["entry"]:
                if entry_name == name:
                    dellist.append(entry_name)
        for todel in dellist:
            dic["entry"].pop(todel)
        self.jsondata.save()
    
    @classmethod
    def new_entryname(self):
        return fjw.random_id(8)
    
    def get_thisfile_entries(self):
        """このBlendファイルに関連するエントリ名を返す"""
        result = []
        dic = self.jsondata.dictionary
        if "entry" in dic:
            for entry_name in dic["entry"]:
                if bpy.data.filepath == dic["entry"][entry_name]["filepath"]:
                    result.append(entry_name)
        return result

class MarvelousDesignerScriptUtils():
    """
    出力されたディレクトリからworkdirにデータをコピーしてシミュレーションさせる。
    MD側では単に、与えられたデータをシミュレーションするだけでいいのでpython2いらないかも。
    終了を待ってからBlenderで結果を移動させればいい。
    """
    workdir = r"C:\mdwork_temp"

    @classmethod
    def istodo(cls):
        pref = fujiwara_toolbox.conf.get_pref()
        if pref.use_md7script:
            return True
        else:
            return False
    
    @classmethod
    def get_mdexepath(cls):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.MarvelousDesigner_path

    def __init__(self, mdobj):
        if not self.istodo():
            return
        self.mdobj = mdobj

        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        pass

    def __copyfile(self, src_path, dest_path):
        if not self.istodo():
            return
        if not os.path.exists(src_path):
            print("COPY:'%s' not found."%src_path)
            return
        
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        shutil.copy(src_path, dest_path)
    
    def copy_to_workdir_as_newname(self, src_path, new_name):
        if not self.istodo():
            return
        print("copy_to_workdir_as_newname:%s"%new_name)
        filename = os.path.basename(src_path)
        name, ext = os.path.splitext(filename)
        dest_path = self.workdir + os.sep + new_name + ext
        self.__copyfile(src_path, dest_path)

    def senddata_to_workdir(self):
        if not self.istodo():
            return
        toolpath, avatar_path, animation_path, garment_path, result_path = self.mdobj.get_sim_path()
        self.copy_to_workdir_as_newname(avatar_path, "avatar")
        self.copy_to_workdir_as_newname(animation_path, "animation")
        self.copy_to_workdir_as_newname(garment_path, "garment")

        code_path = os.path.dirname(os.path.dirname(__file__)) + os.sep + "utils" + os.sep + "mdsimcode.py"
        self.copy_to_workdir_as_newname(code_path, "mdsimcode")
        pass

    def getdata_from_workdir(self):
        if not self.istodo():
            return
        pass
    
    def execute(self):
        if not self.istodo():
            return
        pass


class MDObject():
    """
        MarvelousDesignerエクスポート用のデータ。
    """

    def __init__(self, mdname, objects, garment_path=""):
        """
            エクスポートオブジェクトの名前
            オブジェクトのリスト
        """
        self.mdname = mdname
        self.objects = objects
        # if export_dir == "MDData":
        #     blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        #     self.__set_export_dir(get_mddatadir() + os.sep + blendname.replace("_MDWork", "") + os.sep + mdname)
        # else:
        #     self.export_dir = export_dir
        self.export_dir = get_mddatadir()

        if garment_path == "":
            self.garment_path = self.get_garment_path()
        else:
            self.garment_path = garment_path

    def has_obj(self, obj):
        if obj in self.objects:
            return True
        return False

    def get_garment_path(self):
        garment_list = self.__get_prop_from_objects("md_garment_path_list")
        garment_index = self.__get_prop_from_objects("md_garment_index")
        if garment_list is None:
            #デフォルトパスをリンクから取得してみる
            linked_path = self.__get_prop_from_objects("linked_path")
            if linked_path is not None:
                linked_dir = os.path.dirname(linked_path)
                garment_path = linked_dir + os.sep + self.mdname + ".zpac"
                if not os.path.exists(garment_path):
                    return ""
                return garment_path
            else:
                return ""
        else:
            if garment_index is None:
                garment_index = 0
            if garment_index >= len(garment_list):
                garment_index = 0
            return garment_list[garment_index]

    def get_export_objects(self):
        index_list = self.__get_export_index_list()
        objects = self.__filter_objects("MESH")
        result = []
        for obj in objects:
            if "md_export_id" in obj:
                if obj["md_export_id"] in index_list:
                    result.append(obj)

        #もしresultが空なら、次はBodyを検索する。
        if len(result) == 0:
            for obj in objects:
                if "Body" in obj.name:
                    result.append(obj)

        #なければ、選択オブジェクトのうちメッシュオブジェクトをそのまま採用する。
        if len(result) == 0:
            # result.extend(objects)
            for obj in objects:
                if obj.type == "MESH":
                    result.append(obj)
        

        return result

    # def export_obj(self, dirpath, animation=True):
    #     """
    #         .obj+.mddを出力
    #     """
    #     self.__export_setup(dirpath)
    #     #obj出力
    #     bpy.ops.export_scene.obj(filepath= self.export_dir + os.sep + self.mdname + ".obj", use_selection=True)
    #     if animation:
    #         #PointCache出力
    #         bpy.ops.export_shape.mdd(filepath= self.export_dir + os.sep + self.mdname + ".mdd", fps=6,frame_start=1,frame_end=10)
    
    def export_abc(self, dirpath, name):
        current_fps = bpy.context.scene.render.fps
        bpy.context.scene.render.fps = MarvelousDesingerUtils.fps
        self.__export_setup(dirpath)
        # path = os.path.normpath(self.export_dir + os.sep + self.mdname + ".abc")
        path = os.path.normpath(self.export_dir + os.sep + name + ".abc")
        print("export abc:%s"%path)
        bpy.ops.wm.alembic_export(filepath=path, start=1, end=(MarvelousDesingerUtils.last_frame + 1), selected=True, visible_layers_only=True, flatten=True, apply_subdiv=True, compression_type='OGAWA', as_background_job=False)
        bpy.context.scene.render.fps = current_fps

    def export_to_mddata(self):
        mdj = MDJson()
        entry_name = mdj.add_fileentry(self.mdname)
        self.export_abc(self.export_dir, entry_name)
        # 衣装データをコピーしておく
        garment_path = self.get_garment_path()
        if garment_path == "":
            # 衣装パスが設定されていないなら出力すべきではない。
            return
        garment_name, garment_ext = os.path.splitext(os.path.basename(garment_path))
        # garment_pathを絶対パス化しないといけない
        if garment_path.find("//") == 0:
            # 相対パスである
            garment_path = bpy.path.abspath(garment_path)
        shutil.copy(garment_path, get_mddatadir()+ entry_name + garment_ext)
        # self.export_mdscript()
        mdcode = MDCode()
        entry_path = self.export_dir + entry_name
        mdcode.addline(entry_path + ".abc", entry_path + ".zpac")

    def open_export_dir(self):
        os.system("EXPLORER " + self.export_dir)

    def get_sim_path(self):
        toolpath = fujiwara_toolbox.__path__[0] + os.sep + "tools" + os.sep + "mdcontrol" + os.sep + "mdcontrol.py"
        avatar_path = os.path.normpath(self.export_dir + os.sep + self.mdname + ".abc")
        animation_path = "none"
        garment_path = os.path.normpath(self.get_garment_path())
        result_path = os.path.normpath(self.export_dir + os.sep + "result.obj")
        return toolpath, avatar_path, animation_path, garment_path, result_path

    def export_mdscript(self):
        toolpath, avatar_path, animation_path, garment_path, result_path = self.get_sim_path()

        data = ""
        # data += 'avatar_path="%s"\n'%avatar_path
        # data += 'garment_path="%s"\n'%garment_path
        # data += 'result_path="%s"\n'%result_path
        data += 'mddatafiles.append((avatar_path, garment_path, result_path))\n'
        data += 'mdsa.clear_console()\n'
        data += 'mdsa.initialize() \n'
        data += 'mdsa.set_open_option(unit="m", fps=5)\n'
        data += 'mdsa.set_save_option(unit="m", fps=5, unified =False)\n'
        data += 'mdsa.set_garment_file_path("%s")\n'%garment_path
        data += 'mdsa.set_animation_file_path("%s")\n'%avatar_path #abcなので。
        data += 'mdsa.set_simulation_options(obj_type=0, simulation_quality=0, simulation_delay_time=0)n'
        data += 'mdsa.set_save_file_path("%s")\n'%result_path
        data += 'mdsa.process(auto_save_zprj_file=False)\n'
        data += '\n'
        
        datafilepath = os.path.normpath(self.export_dir + os.sep + self.mdname + "_mdscript.py")
        
        f = open(datafilepath, "w")
        f.write(data)
        f.close()


    def md_sim(self):
        """
            アバター .obj
            アニメーション .mdd
            衣装ファイル.zpac
            リザルトパス
        """
        (toolpath, avatar_path, animation_path, garment_path, result_path) = self.get_sim_path()
        # toolpath = os.path.basename(fjw.__file__) + os.sep + "tools" + os.sep + "mdcontrol" + os.sep + "mdcontrol.py"

        mdexe = MarvelousDesignerScriptUtils.get_mdexepath()
        if MarvelousDesignerScriptUtils.istodo():
            if not os.path.exists(mdexe):
                print("'%s' not found."%mdexe)
                return False
            # ファイルのコピー
            print("MarvelousDesignerScriptUtils.istodo")
            mdscr_utils = MarvelousDesignerScriptUtils(self)
            mdscr_utils.senddata_to_workdir()

            script_path = MarvelousDesignerScriptUtils.workdir + os.sep + "mdsimcode.py"

            # MarvelousDesignerを起動
            cmdstr = '"%s" "%s"'%(mdexe, script_path)
            print(cmdstr)
            p = subprocess.Popen(cmdstr)
            p.wait()
        else:
            cmdstr = 'python "%s" "%s" "%s" "%s" "%s"'%(toolpath, avatar_path, animation_path, garment_path, result_path)
            print(cmdstr)
            p = subprocess.Popen(cmdstr)
            p.wait(5*60)
            print("mdsim done.")
        return

    def __set_export_dir(self, dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        self.export_dir = dirpath

    def __filter_objects(self, object_type):
        result = []
        for obj in self.objects:
            if obj.type == object_type:
                result.append(obj)
        return result

    def __export_setup(self, dirpath):
        fjw.deselect()
        fjw.select(self.get_export_objects())
        self.__simplify(2)
        for obj in self.objects:
            self.__disable_backsurface_edge(obj)
        #フレーム1に移動
        bpy.ops.screen.frame_jump(end=False)

    def __simplify(self, level):
        #簡略化2
        if not bpy.context.scene.render.use_simplify:
            bpy.context.scene.render.use_simplify = True
        if bpy.context.scene.render.simplify_subdivision != level:
            bpy.context.scene.render.simplify_subdivision = level

    def __disable_backsurface_edge(self, obj):
        #裏ポリエッジオフ
        for mod in obj.modifiers:
            if "裏ポリエッジ" in mod.name:
                mod.show_viewport = False
                mod.show_render = False

    def __get_prop_from_objects(self, propname):
        result = None
        for obj in self.objects:
            if propname in obj:
                result = obj[propname]
                break
        return result

    def __get_export_index_list(self):
        export_index_list = [0]
        export_depth = self.__get_prop_from_objects("md_export_depth")
        if export_depth is None:
            export_index_list = [0]
        else:
            if type(export_depth) == list:
                export_index_list = export_depth
            if type(export_depth) == int:
                export_index_list = []
                for i in range(export_depth):
                    export_index_list.append(i)
        return export_index_list

class MDObjectManager():
    def __init__(self):
        self.mdobjects = []

    def is_already_registerd(self, obj):
        for mdo in self.mdobjects:
            if mdo.has_obj(obj):
                return True
        return False

    def find_mdobj_by_object(self, obj):
        for mdo in self.mdobjects:
            if mdo.has_obj(obj):
                return mdo
        return None

    def get_avatar_objects_from_its_root(self, child_object):
        """
            オブジェクトからルートオブジェクトを取得して、
            mdobjectsに格納する。
        """
        fjw.deselect()
        root = fjw.get_root(child_object)

        mdobj = self.find_mdobj_by_object(root)
        if mdobj is not None:
            return mdobj

        fjw.activate(root)
        rootname = re.sub("\.\d+", "", root.name)
        bpy.ops.fujiwara_toolbox.command_24259()#親子選択
        selection = fjw.get_selected_list()

        #selectionの中にMESHオブジェクトがなかったら除外する
        mesh_found = False
        for obj in selection:
            if obj.type == "MESH":
                mesh_found = True
        if not mesh_found:
            return None

        mdobj = MDObject(rootname, selection)
        self.mdobjects.append(mdobj)

        return mdobj        

    def export_mdavatar(self, objects, run_simulate=False):
        self.mdobjects = []
        for obj in objects:
            mdobj = self.get_avatar_objects_from_its_root(obj)

        for mdobj in self.mdobjects:
            mdobj.export_to_mddata()

        # if run_simulate:
        #     for mdobj in self.mdobjects:
        #         mdobj.md_sim()

    def export_active_body_mdavatar(self, run_simulate=False):
        active = fjw.active()
        self.export_mdavatar([active], run_simulate)

    def export_selected_mdavatar(self, run_simulate=False):
        selection = fjw.get_selected_list()
        self.export_mdavatar(selection, run_simulate)

    #なんか危険な予感がする。リンクオブジェクトとか。
    # def export_all_mdavatar(self, run_simulate=False):
    #     self.export_mdavatar(bpy.context.scene.objects, run_simulate)

class MarvelousDesingerUtils():
    last_frame = 10
    fps = 5

    def __init__(self):
        self.mddata_dir = self.get_mddatadir()

    @classmethod
    def clear_cue_folder(cls):
        mdtemp_dir = get_mddatadir(False)
        files = os.listdir(mdtemp_dir)
        for file in files:
            filepath = mdtemp_dir + os.sep + file
            os.remove(filepath)


    @classmethod
    def export_active(self, run_simulate=False):
        mdmanager = MDObjectManager()
        mdmanager.export_active_body_mdavatar(run_simulate)

    @classmethod
    def export_selected(self, run_simulate=False):
        mdmanager = MDObjectManager()
        mdmanager.export_selected_mdavatar(run_simulate)

    @classmethod
    def setkey(cls):
        if fjw.active().type == "ARMATURE":
            fjw.mode("POSE")
        if fjw.active().mode == "OBJECT":
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
        if fjw.active().mode == "POSE":
            #MarvelousDesigner用
            aau = fjw.ArmatureActionUtils(fjw.active())
            aau.set_action("mdwork")
            frame = bpy.context.scene.frame_current
            aau.store_pose(frame, "mdpose_"+str(frame))

            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')

    @classmethod
    def delkey(cls):
        if fjw.active().type == "ARMATURE":
            fjw.mode("POSE")
        if fjw.active().mode == "OBJECT":
            bpy.ops.anim.keyframe_delete_v3d()
        if fjw.active().mode == "POSE":
            #MarvelousDesigner用
            aau = fjw.ArmatureActionUtils(fjw.active())
            aau.set_action("mdwork")
            frame = bpy.context.scene.frame_current
            aau.delete_pose("mdpose_"+str(frame))        

            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.anim.keyframe_delete_v3d()

    @classmethod
    def armature_autokey(cls):
        """
        アーマチュアのキーをオートで入れる
        """
        if fjw.active().type != "ARMATURE":
            return

        fjw.mode("POSE")

        #アーマチュアのキーをオートで入れる
        if bpy.context.scene.frame_current == cls.last_frame:
            rootname = fjw.get_root(fjw.active()).name

            fjw.active().location = Vector((0,0,0))

            cls.setkey()

            #フレーム10なら微調整じゃないのでオートフレーム。
            armu = fjw.ArmatureUtils(fjw.active())
            geo = armu.GetGeometryBone()
            armu.clearTrans([geo])

            cls.setkey()

            fjw.framejump(1)
            selection = armu.select_all()
            armu.clearTrans(selection)

            cls.setkey()

            #選択にズーム
            bpy.ops.view3d.view_selected(use_all_regions=False)
            fjw.framejump(cls.last_frame)

    @classmethod
    def delete_imported_files(cls, path):
        mddata_dir = get_mddatadir()
        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)
        files = os.listdir(mddata_dir)
        for file in files:
            if name in file:
                filepath = mddata_dir + file
                os.remove(filepath)
        mdj = MDJson()
        mdj.remove_entry(name)
        mdc = MDCode()
        mdc.removeline(name)


    @classmethod
    def import_mdresult(cls,resultpath, attouch_fjwset=False):
        if not os.path.exists(resultpath):
            return

        current = fjw.active()

        loc = Vector((0,0,0))
        qrot = Quaternion((0,0,0,0))
        scale = Vector((1,1,1))

        bonemode = False
        # ↓微妙なのでやめる
        # #もしボーンが選択されていたらそのボーンにトランスフォームをあわせる
        # if current is not None and current.mode == "POSE":
        #     armu = fjw.ArmatureUtils(current)
        #     pbone = armu.poseactive()
        #     armu.get_pbone_world_co(pbone.head)
        #     loc = armu.get_pbone_world_co(pbone.head)
        #     qrot = pbone.rotation_quaternion
        #     scale = pbone.scale
        #     print("loc:%s"%str(loc))
        #     print("qrot:%s"%str(qrot))
        #     print("scale:%s"%str(scale))

        #     #boneはYupなので入れ替え
        #     # qrot = Quaternion((qrot.w, qrot.x, qrot.z * -1, qrot.y))
        #     bonemode = True
        print("bonemode:%s"%str(bonemode))

        fjw.mode("OBJECT")

        fname, ext = os.path.splitext(resultpath)
        if ext == ".obj":
            bpy.ops.import_scene.obj(filepath=resultpath)
        if ext == ".abc":
            bpy.ops.wm.alembic_import(filepath=resultpath, as_background_job=False)
            selection = fjw.get_selected_list()
            for obj in selection:
                obj.name = "result"

        #透過を無効にしておく
        selection = fjw.get_selected_list()
        for obj in selection:
            for mat in obj.data.materials:
                mat.use_transparency = False


        #インポート後処理
        #回転を適用
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        selection = fjw.get_selected_list()
        for obj in selection:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
                # #服はエッジ出ない方がいい 裏ポリで十分
                # for slot in obj.material_slots:
                #     mat = slot.material
                #     mat.use_transparency = True
                #     mat.transparency_method = 'RAYTRACE'

                obj.location = loc
                if bonemode:
                    obj.rotation_quaternion = obj.rotation_quaternion * qrot
                    obj.rotation_euler = obj.rotation_quaternion.to_euler()
                    obj.scale = scale
        
                #読み先にレイヤーをそろえる
                if current is not None:
                    obj.layers = current.layers
        
        if attouch_fjwset:
            bpy.ops.fujiwara_toolbox.command_318722()#裏ポリエッジ付加
            # bpy.ops.fujiwara_toolbox.set_thickness_driver_with_empty_auto() #指定Emptyで厚み制御

        cls.delete_imported_files(resultpath)


    @classmethod
    def __find_root_armature(cls, start_obj):
        """start_objから親を辿っていって、アーマチュアがなければそれを返す"""
        p = start_obj.parent
        if not p:
            return None

        result = cls.__find_root_armature(p)

        if not result:
            if start_obj.type == "ARMATURE":
                result = start_obj
        
        return result


    @classmethod
    def mdresult_auto_import_main(cls, self, context, attouch_fjwset=False):
        import_ext = ".obj"


        #存在確認
        # blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        # dir_path = get_mddatadir() + blendname + os.sep
        dir_path = get_mddatadir()
        self.report({"INFO"},dir_path)

        if not os.path.exists(dir_path):
            self.report({"INFO"},"キャンセルされました。")
            # bpy.ops.wm.quit_blender()
            return {'CANCELLED'}

        #既存のリザルトを処分
        fjw.deselect()
        dellist = []
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH" and "result" in obj.name:
                dellist.append(obj)
        fjw.delete(dellist)

        root_objects = []
        for obj in bpy.context.scene.objects:
            if obj.parent is None:
                root_objects.append(obj)

        mdj = MDJson()
        entries = mdj.get_thisfile_entries()
        # files = os.listdir(dir_path)
        # for file in files:
        files = []
        for entry in entries:
            file = entry + import_ext
            # 対応するファイルが実際にあるかをチェックしないとだめ！
            filepath = dir_path + file
            if not os.path.exists(filepath):
                continue
            files.append(file)

        for file in files:
            self.report({"INFO"},file)
            print("MDResult found:"+file)
            # targetname = file
            # dirname = os.path.basename(os.path.dirname(file))
            targetname = file

            # rootobjでの設置だとルートがないとおかしなことになる
            # dupli_groupの名前でみて、同一名のもののアーマチュアを探して、
            # vislble_objects内のそのデータと同一のプロクシないしアーマチュア、のジオメトリを指定すればいいのでは

            #グループ名だと全部"MainGroup"だからマッチしない！
            #グループの親ファイルパスの名前を見る！！

            #複製子除去
            # targetname = re.sub(r"\.\d+", "", targetname)
            print("basename:%s, targetname:%s"%(file, targetname))

            #fileと同名のdupli_groupを検索
            dupli_group = None
            for group in bpy.data.groups:
                # gname = re.sub(r"\.\d+", "", group.name)
                if group.name == "MainGroup":
                    if group.library is not None:
                        g_filepath = group.library.filepath
                        g_filename = os.path.basename(g_filepath)
                        gname,ext = os.path.splitext(g_filename)
                    else:
                        gname = group.name
                else:
                    gname = group.name

                if targetname == gname:
                    dupli_group = group
                    break

            if not dupli_group:
                print("!targetname not in bpy.data.groups!:%s"%targetname)
            else:
                print("*targetname found*:%s"%targetname)

            if dupli_group:
                dgroup = dupli_group
                #Bodyが参照しているアーマチュアのデータを取得
                target_armature = None
                #この検索問題　名前Bodyじゃない可能性がある　まずカスタムプロパティで探すべき
                #普通に全てのアーマチュアがシーン上のアーマチュアと一致したらそれ採用でいいのでは？
                # for obj in dgroup.objects:

                for scene_amature in bpy.context.visible_objects:
                    if scene_amature.type != "ARMATURE":
                        continue
                    linked_object = scene_amature.proxy_group
                    if linked_object:
                        #グループが一致
                        if linked_object.dupli_group == dupli_group:
                            #ルートアーマチュアを採用する
                            target_armature = cls.__find_root_armature(scene_amature)
                            break

                # if "Body" in dgroup.objects:
                #     Body = dgroup.objects["Body"]
                #     modu = fjw.Modutils(Body)
                #     armt = modu.find("Armature")

                #     if armt is not None:
                #         armature = armt.object
                #         if armature is not None:
                #             armature_data = armature.data
                #             for scene_amature in bpy.context.visible_objects:
                #                 if scene_amature.type != "ARMATURE":
                #                     continue
                #                 if scene_amature.data != armature_data:
                #                     continue
                #                 #同一のアーマチュアデータを発見したのでこいつを使用する
                #                 target_armature = scene_amature
                #                 break

                if not target_armature:
                    print("!target_armature not found!")

                if target_armature is not None:
                    print("target_armature:%s"%target_armature)
                    arm = target_armature
                    print("MDImport Step 0")
                    fjw.mode("OBJECT")
                    fjw.deselect()
                    fjw.activate(arm)
                    print("MDImport Step 1")
                    fjw.mode("POSE")
                    armu = fjw.ArmatureUtils(arm)
                    geo = armu.GetGeometryBone()
                    armu.activate(geo)
                    print("MDImport Step 2")
                    fjw.mode("POSE")

                    self.report({"INFO"},dir_path + file)
                    print("MDImport Selecting GeoBone:" + dir_path + file)

            #インポート
            # mdresultpath = dir_path + file + os.sep + "result" + import_ext
            mdresultpath = dir_path + file
            MarvelousDesingerUtils.import_mdresult(mdresultpath, attouch_fjwset)
            print("MDImport Import MDResult:"+mdresultpath)

        fjw.mode("OBJECT")
        for obj in bpy.context.visible_objects:
            if "result" in obj.name:
                obj.select = True

                #テクスチャのパック
                cls.__pack_img_of_obj(obj)

        # if attouch_fjwset:
        #     bpy.ops.fujiwara_toolbox.comic_shader_nospec()

    
    @classmethod
    def __pack_img_of_obj(cls, obj):
        print("pack img of:%s"%obj.name)
        for mat in obj.data.materials:
            fjw.pack_textures(mat)
        pass

    @classmethod
    def __get_prop(cls, obj, name):
        """
        カスタムプロパティを取得する。
        なければNone
        """
        if name in obj:
            return obj[name]
        return None

    @classmethod
    def setup_mdwork_main(cls, self,context):
        if "_MDWork" not in bpy.data.filepath:
            fjw.framejump(cls.last_frame)
            dir = os.path.dirname(bpy.data.filepath)
            name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
            blend_md = dir + os.sep + name + "_MDWork.blend"
            bpy.ops.wm.save_as_mainfile(filepath=blend_md)

            bpy.context.scene.layers[0] = True
            for i in range(19):
                bpy.context.scene.layers[i + 1] = False
            for i in range(5):
                bpy.context.scene.layers[i] = True

            #ポーズだけついてるやつをポーズライブラリに登録する
            for armature_proxy in bpy.context.visible_objects:
                if armature_proxy.type != "ARMATURE":
                    continue
                if "_proxy" not in armature_proxy.name:
                    continue
                fjw.deselect()
                fjw.activate(armature_proxy)
                fjw.mode("POSE")
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.fujiwara_toolbox.set_key()
                fjw.mode("OBJECT")

            fjw.mode("OBJECT")
            bpy.ops.object.select_all(action='SELECT')

            bpy.ops.file.make_paths_absolute()
            selection = fjw.get_selected_list()
            for obj in selection:
                md_garment_path_list = cls.__get_prop(obj, "md_garment_path_list")
                md_export_id = cls.__get_prop(obj, "md_export_id")
                md_garment_index = cls.__get_prop(obj, "md_garment_index")
                md_export_depth = cls.__get_prop(obj, "md_export_depth")

                # obj.dupli_group.library.filepath
                link_path = ""
                if obj.dupli_group is not None and obj.dupli_group.library is not None:
                    link_path = obj.dupli_group.library.filepath
                if link_path == "" or link_path is None:
                    continue

                fjw.deselect()
                fjw.activate(obj)
                bpy.ops.object.duplicates_make_real(use_base_parent=True,use_hierarchy=True)
                realized_objects = fjw.get_selected_list()
                for robj in realized_objects:
                    robj["linked_path"] = link_path

                    root = fjw.get_root(robj)
                    if md_garment_path_list is not None:
                        root["md_garment_path_list"] = md_garment_path_list
                    if md_export_id is not None:
                        root["md_export_id"] = md_export_id
                    if md_garment_index is not None:
                        root["md_garment_index"] = md_garment_index
                    if md_export_depth is not None:
                        root["md_export_depth"] = md_export_depth

                    #garment_pathを絶対パス化する
                    if "md_garment_path_list" in robj:
                        pathlist_base = robj["md_garment_path_list"]

                        print("*"*15)
                        print("* make garment path to abs")
                        print("*"*15)
                        lib_dir = os.path.dirname(link_path)
                        pathlist_new = []
                        for garment_path in pathlist_base:
                            new_path = bpy.path.abspath(garment_path, start=lib_dir)
                            pathlist_new.append(new_path)
                            print(new_path)
                        robj["md_garment_path_list"] = pathlist_new
                        print("*"*15)


            #proxyの処理
            #同一のアーマチュアデータを使っているものを探してポーズライブラリを設定する。
            for armature_proxy in bpy.data.objects:
                if armature_proxy.type != "ARMATURE":
                    continue
                if "_proxy" not in armature_proxy.name:
                    continue


                for armature in bpy.data.objects:
                    if armature.type != "ARMATURE":
                        continue
                    if armature == armature_proxy:
                        continue

                    if armature.data == armature_proxy.data:
                        #同一データを使用している
                        #のでポーズライブラリの設定をコピーする
                        armature.pose_library = armature_proxy.pose_library

                        #回収したポーズライブラリを反映する
                        fjw.mode("OBJECT")
                        fjw.activate(armature)
                        
                        if fjw.active() is not None:
                            aau = fjw.ArmatureActionUtils(armature)
                            armu = fjw.ArmatureUtils(armature)
                            
                            fjw.active().hide = False
                            fjw.mode("POSE")
                            poselist = aau.get_poselist()
                            if poselist is not None:
                                for pose in aau.get_poselist():
                                    frame = int(str(pose.name).replace("mdpose_",""))
                                    fjw.framejump(frame)

                                    #ジオメトリはゼロ位置にする
                                    geo = armu.GetGeometryBone()
                                    armu.clearTrans([geo])
                                    bpy.ops.pose.select_all(action='SELECT')
                                    armu.databone(geo.name).select = False
                                    aau.apply_pose(pose.name)
                            #1フレームではデフォルトポーズに
                            fjw.mode("POSE")
                            fjw.framejump(1)
                            bpy.ops.pose.select_all(action='SELECT')
                            bpy.ops.pose.transforms_clear()

            #proxyの全削除
            fjw.mode("OBJECT")
            prxs = fjw.find_list("_proxy")
            fjw.delete(prxs)

            # bpy.app.handlers.scene_update_post.append(process_proxy)
            bpy.context.space_data.show_only_render = False


