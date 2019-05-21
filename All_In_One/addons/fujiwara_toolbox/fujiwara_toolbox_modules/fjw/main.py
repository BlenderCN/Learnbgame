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
import random
from collections import OrderedDict
from mathutils import *

############################################################################################################################
############################################################################################################################
#ユーティリティ
############################################################################################################################
############################################################################################################################

import traceback
def print_exception():
    """
    except:で使う。
    """
    traceback.print_exc()

#ダブルクォーテーション
def qq(str):
    return '"' + str + '"'




def get_resourcesdir():
    scrdir = os.path.dirname(os.path.dirname(__file__))
    resourcesdir = scrdir + os.sep + "resources" + os.sep
    return resourcesdir

def getdirs(path):
    dirs = []
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path,item)):
            dirs.append(item)
    return dirs

def get_dir(path):
    dirlist = path.split(os.sep)

    result = ""
    for i in range(len(dirlist) - 1):
        result += dirlist[i] + os.sep
    return result

def get_root(obj):
    parent = obj.parent
    if parent == None:
        return obj
    return get_root(parent)

def get_world_co(obj):
    return obj.matrix_world * obj.matrix_basis.inverted() * obj.location

def cursor():
    return bpy.context.space_data.cursor_location
def set_cursor(pos):
    bpy.context.space_data.cursor_location = pos

def blendname():
    name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    return name

def blenddir():
    dir = os.path.dirname(bpy.data.filepath)
    return dir

def splitpath(basepath):
    """パスを分割する。
    dirname, name, extでうける"""
    if not basepath:
        return None, None, None
    dirname = os.path.dirname(basepath)
    basename = os.path.basename(basepath)
    name, ext = os.path.splitext(basename)
    return dirname, name, ext

# def group(name, objects):
#     group = None
#     for gr in bpy.data.groups:
#         if name == gr.name:
#             if gr.library is None:
#                 group = gr
#                 break
    
#     if group is None:
#         group = bpy.data.groups.new(name)

#     for ob in selection:
#         if ob.name not in group.objects:
#             group.objects.link(ob)

#     return group

def find(name):
    for obj in bpy.data.objects:
        if name in obj.name:
            return obj
    return None

def find_list(name,targetlist=None):
    if targetlist == None:
        targetlist = bpy.data.objects
    result = []
    for obj in targetlist:
        if name in obj.name:
            result.append(obj)
    return result

def find_child_bytype(parent,type):
    for obj in parent.children:
        if obj.type == type:
            return obj

    for obj in parent.children:
        result = find_child_bytype(obj,type)
        if result is not None:
            return result
    return None

def find_parent_bytype(obj,type):
    parent = obj.parent

    if parent is None:
        return None

    if parent.type == type:
        return parent
    
    return find_parent_bytype(parent, type)

def object(name):
    # nameのオブジェクトをdata返す
    #オブジェクトが突っ込まれたらそのままかえす
    if type(name) == bpy.types.Object:
        return name

    if name in bpy.context.scene.objects:
        return bpy.context.scene.objects[name]
    else:
        return None

def material(name, objects=None):
    targets = []
    if objects is None:
        targets = bpy.data.materials
    else:
        for obj in objects:
            if obj.type != "MESH":
                continue
            for mat in obj.data.materials:
                targets.append(mat)
    
    for mat in targets:
        if mat.name == name:
            return mat
    
    return None
        

def objects_filter(objects, type="", name=""):
    result = []
    for obj in objects:
        if type != "":
            if obj.type != type:
                continue
        if name != "":
            if obj.name != name:
                continue
        result.append(obj)
    return result


def in_localview():
    #bpy.data.screens[0].areas[1].spaces[0].local_view
    if bpy.context.space_data.local_view == None:
        return False
    else:
        return True

def localview():
    if not in_localview():
        bpy.ops.view3d.localview()

def globalview():
    if in_localview():
        bpy.ops.view3d.localview()

def add_mod(mod_type):
    result = None

    obj = active()

    if obj != None:
        bpy.ops.object.modifier_add(type=mod_type)

        result = getnewmod(obj)
    return result

def get_mod(mod_type):
    result = None

    obj = active()

    if obj != None:
       for mod in obj.modifiers:
           if mod.type == mod_type:
               result = mod
               return result
    return result


def is_in_visible_layer(obj):
    #表示レイヤーに含まれているか
    for index, value in enumerate(bpy.context.scene.layers):
        if value:
            if obj.layers[index]:
                return True
    return False

def layers_current_state():
    result = []
    for state in bpy.context.scene.layers:
        result.append(state)
    return result

def layers_showall():
    layers = [True for state in range(len(bpy.context.scene.layers))]
    bpy.context.scene.layers = layers

def layers_show_list(layers):
    bpy.context.scene.layers = layers

def another(obj, objects):
    # リストの中の別のオブジェクトを返す
    for other in objects:
        if other != obj:
            return other
    return None

def match(name, type="MESH"):
    result = None

    for obj in bpy.data.objects:
        if obj.type != type:
            continue
        if name in obj.name:
            result = obj
            break

    return result

def matches(name, type="MESH"):
    result = []

    for obj in bpy.data.objects:
        if obj.type != type:
            continue
        if name in obj.name:
            result.append(obj)
            continue
    return result

def getnewmod(obj):
    mods = obj.modifiers
    if len(mods) == 0:
        return None
    else:
        return mods[len(mods) - 1]

def removeall_mod():
    for obj in bpy.context.selected_objects:
       if obj.type == "MESH":
           bpy.context.scene.objects.active = obj
           for mod in obj.modifiers:
                bpy.ops.object.modifier_remove(modifier=mod.name)


"""
        #メッシュ以外除外
        if(reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:"+self.bl_idname)
            return {'CANCELLED'}

"""
def reject_notmesh():
    #メッシュ以外除外
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            obj.select = False
    if len(bpy.context.selected_objects) == 0:
        return False
    else:
        return True


def active_exists():
    if bpy.context.scene.objects.active == None:
        return False
    else:
        return True

def deselect():
    #選択リフレッシュ
    for obj in bpy.data.objects:
        obj.select = False


def select(objects):
    for obj in objects:
        if obj != None:
            obj.select = True

def delete(objects):
    if objects == None:
        return

    if len(objects) == 0:
        return

    if type(objects) == "list":
        if len(objects) == 0:
            return

    if type(objects) == bpy.types.Object:
        tmp = []
        tmp.append(objects)
        objects = tmp

    for obj in objects:
        bpy.data.objects.remove(obj,True)

    # deselect()

    # for obj in objects:
    #     obj.hide_select = False
    #     obj.select = True
    #     activate(obj)
    #     mode("OBJECT")

    # bpy.ops.object.delete(use_global=False)

def origin_floorize():
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
    return

def apply_mods():
    active = bpy.context.scene.objects.active
    #bpy.context.window_manager.progress_begin(0,len(bpy.context.selected_objects))
    #prog = 0
    for obj in bpy.context.selected_objects:
        #bpy.context.window_manager.progress_update(prog)
        #prog+=1
        if obj.type == "MESH":
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                mod.show_viewport = True

                #エラー出さないように個別処理
                if mod.type == "BOOLEAN":
                    if mod.object == None:
                        continue

                bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.scene.objects.active = active
    #bpy.context.window_manager.progress_end()
    return


def activate(obj):
    bpy.context.scene.objects.active = obj
    #あんまり意識しない形にするとマズいか？
    if obj is not None:
        obj.select = True
    return obj

def active():
    return bpy.context.scene.objects.active


def objectmode():
    if active() != None:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

def editmode():
    if active() != None:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

def mode(modeto=None):
    if active() != None:
        if modeto is not None:
            bpy.ops.object.mode_set(mode=modeto, toggle=False)

        return active().mode
    return None



#指定レイヤーをTrueにしたレイヤー群を返す。引数がなければ全部False。
def layers(put_layer=-1,put_visible_last=False,not_visible=False):
    ls = [False for i in range(20)]

    #対象レイヤーをオン
    if -1 < put_layer < 20:
        ls[put_layer] = True

    #最後のレイヤーをオンに
    if put_visible_last:
        lastlayer = 0
        for l in range(0,20):
            if bpy.context.scene.layers[l]:
                lastlayer = l

        ls[lastlayer] = True

    #配置レイヤーを自動的に表示する
    if not not_visible:
        for l in range(0,20):
            if ls[l]:
                bpy.context.scene.layers[l] = True

    return ls

def get_selected_list(type="ALL"):
    list = []
    # for obj in bpy.context.selected_objects:
    for obj in bpy.context.scene.objects:
        if obj.select:
            if type == "ALL":
                list.append(obj)
            else:
                if obj.type == type:
                    list.append(obj)
    return list

def get_selected_bone_names():
    obj = active()
    selected_bone_names = []
    for bone in obj.data.bones:
        if bone.select:
            selected_bone_names.append(bone.name)
    return selected_bone_names

def activate_bone(name):
    obj = active()
    obj.data.bones.active = obj.data.bones[name]

#指定名でプロクシを作成する
def make_proxy(name):
    obj = active()
    if obj.type != "EMPTY":
        #self.report({"INFO"},"リンクしたオブジェクトを指定して下さい。")
        return None

    #リンクデータのオブジェクト
    inlinkobjects = obj.dupli_group.objects

    if name not in inlinkobjects:
        return None

    #対象のオブジェクトがあった
    bpy.ops.object.proxy_make(object=name)
    pobj = active()
    obj.select = True

    #元オブジェクトを親子つける
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    bpy.ops.object.mode_set(mode='POSE', toggle=False)


    return pobj

def make_proxy_type(type):
    linkobj = active()
    result = []
    result.append(linkobj)
    for obj in linkobj.dupli_group.objects:
        if obj.type == type:
            bpy.ops.object.proxy_make(object=obj.name)
            active().name = obj.name + "_proxy"
            result.append(active())
            activate(linkobj)


    return result


def get_linkedfilename(obj):
    linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
    linkedfilename = os.path.splitext(os.path.basename(linkedpath))[0]
    return linkedfilename

def make_proxy_all():
    linkobj = active()
    result = []
    result.append(linkobj)

    mapmode = False
    if "MapController" in linkobj.dupli_group.objects:
        mapmode = True

    for obj in linkobj.dupli_group.objects:
        if obj.type == "ARMATURE" or obj.type == "EMPTY":
            if mapmode:
                if obj.type == "EMPTY":
                    continue
            proxyname = get_linkedfilename(linkobj) + "/" + obj.name + "_proxy"
            if proxyname not in bpy.data.objects:
                bpy.ops.object.proxy_make(object=obj.name)
                active().name = proxyname
                result.append(active())
                activate(linkobj)


    return result




#ノードツリーのインポート
#現状ノードツリーは同一ディレクトリに置くような運用してないので、使用すべきではない
#def link_nodetree(name):
#    if name not in bpy.data.node_groups:
#        dir = fujiwara_toolbox.conf.assetdir + os.sep + "ノード"

#        _dataname = name
#        _filename = name + ".blend"
#        _directory = dir + os.sep + _filename + os.sep + "NodeTree" + os.sep
#        _filepath = _directory + _filename
#        bpy.ops.wm.link(filepath=_filepath, filename=_dataname,
#        directory=_directory)
    
#    return bpy.data.node_groups[name]

def append_nodetree(name):
    #既にある場合はそれを使用する
    if name in bpy.data.node_groups:
        for ng in bpy.data.node_groups:
            if ng.library is not None:
                #リンクは使わない
                continue
            if name == ng.name:
                return ng

    # なかったのでアペンド
    dir = get_resourcesdir() + "nodes"

    _dataname = name
    _filename = name + ".blend"
    # _directory = dir + os.sep + _filename + os.sep + "NodeTree" + os.sep
    _filepath = dir + os.sep + _filename
    # bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)
    #↑これだと既にリンク済みのものがある場合、それをひっぱってしまう！自前実装！
    with bpy.data.libraries.load(_filepath, link=False, relative=True) as (data_from, data_to):
        if _dataname in data_from.node_groups:
            data_to.node_groups = [_dataname]
    if len(data_to.node_groups) != 0:
        print("appended node_group:"+data_to.node_groups[0].name)
        return data_to.node_groups[0]
    return None


def append_material(name):
    if name not in bpy.data.materials:
        dir = get_resourcesdir() + "materials"

        _dataname = name
        _filename = name + ".blend"
        _directory = dir + os.sep + _filename + os.sep + "Material" + os.sep
        _filepath = _directory + _filename
        bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)

    return bpy.data.materials[name]

def append_particlesetting(name):
    if name not in bpy.data.particles:
        dir =get_resourcesdir() + "パーティクル設定"

        _dataname = name
        _filename = name + ".blend"
        _directory = dir + os.sep + _filename + os.sep + "ParticleSettings" + os.sep
        _filepath = _directory + _filename
        bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)
    
    return bpy.data.particles[name]

def append_group(name):
    dir =get_resourcesdir()

    _dataname = name
    _filename = name + ".blend"
    _directory = dir + os.sep + _filename + os.sep + "Group" + os.sep
    _filepath = _directory + _filename
    bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)

def nodegroup_instance(basetree, group):
    node = basetree.nodes.new("ShaderNodeGroup")
    node.node_tree = group

    return node


def ismesh(obj):
    return obj.type == "MESH"

#リンクオブジェクトならパスを返す
def checkLink(obj):
    if obj.type != "EMPTY":
        return None

    ##リンクされてる側のオブジェクト
    #if obj.is_library_indirect:
    #    return None

    if not obj.is_duplicator:
        return None

    if obj.dupli_group is not None:
        if obj.dupli_group.library is not None:
            if obj.dupli_group.library is not None:
                if obj.dupli_group.library.filepath is not None:
                    return obj.dupli_group.library.filepath

    return None


def group(name, objects=None):
    group = None
    if objects is None:
        objects = get_selected_list()
    for gr in bpy.data.groups:
        if name == gr.name:
            if gr.library is None:
                group = gr
                break
    
    if group is None:
        group = bpy.data.groups.new(name)

    for ob in objects:
        if ob.name not in group.objects:
            group.objects.link(ob)

    return group

def ungroup(name, objects):
    for g in bpy.data.groups:
        if g.name == name and g.library is None:
            for obj in objects:
                if obj.name in g.objects:
                    g.objects.unlink(obj)
            break

#def TransferPose(src, dest):
#    if src.type == "ARMATURE" and dest.type == "ARMATURE":
#        #mode("OBJECT")
#        #activate(src)
#        #mode("POSE")
#        #bpy.ops.pose.select_all(action='SELECT')
#        #bpy.ops.pose.copy()
#        #mode("OBJECT")

#        #activate(dest)
#        #mode("POSE")
#        #bpy.ops.pose.select_all(action='SELECT')
#        #bpy.ops.pose.paste(flipped=False)
#        #bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')
#        #mode("OBJECT")

#        activate(dest)
#        mode("POSE")
#        bpy.ops.pose.select_all(action='SELECT')

#        count = len(src.pose.bones)
#        for i in range(count):
#            dest.pose.bones[i].location = src.pose.bones[i].location
#            dest.pose.bones[i].rotation_axis_angle =
#            src.pose.bones[i].rotation_axis_angle
#            dest.pose.bones[i].rotation_euler =
#            src.pose.bones[i].rotation_euler
#            dest.pose.bones[i].rotation_quaternion =
#            src.pose.bones[i].rotation_quaternion
#            dest.pose.bones[i].scale = src.pose.bones[i].scale

#        bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')
#        mode("OBJECT")

def framejump(frameto):
    bpy.ops.screen.frame_jump(end=False)
    bpy.ops.screen.frame_offset(delta=frameto - 1)


def get_freezed_mesh(obj):
    mesh = obj.to_mesh(bpy.context.scene, True, "PREVIEW")
    return mesh

#https://blender.stackexchange.com/questions/38016/stereoscopic-camera-how-to-see-objects-visible-only-from-the-right-and-left-cam
from bpy_extras.object_utils import world_to_camera_view

def checkLocationisinCameraView(loc, camera_extend=False):
    cam = bpy.context.scene.camera
    x, y, z = world_to_camera_view(bpy.context.scene, cam, loc)

    #奥行きでリジェクト
    if z < 0:
        return False

    min = 0.0
    max = 1.0
    if camera_extend:
        min = -1.0
        max = 2.0

    if (min <= x <= max and min <= y <= max):
        return True
    return False

def checkIfIsInCameraView(obj,freeze=True,camera_extend=False):
    #if obj.type != "MESH":
    #    return False
    #cam = bpy.context.scene.camera
    #if freeze:
    #    mesh = get_freezed_mesh(obj)
    #else:
    #    mesh = obj.data
    #for v in mesh.vertices:
    #    x, y, z = world_to_camera_view(bpy.context.scene, cam,
    #    obj.matrix_world * v.co)

    #    min = 0.0
    #    max = 1.0
    #    if camera_extend:
    #        min = -1.0
    #        max = 2.0

    #    if (min <= x <= max and min <= y <= max):
    #        return True
    #return False
    if obj.type != "MESH":
        return False
    if freeze:
        mesh = get_freezed_mesh(obj)
    else:
        mesh = obj.data
    for v in mesh.vertices:
        if checkLocationisinCameraView(obj.matrix_world * v.co):
            return True
    return False

def load_img(filepath):
    #別ディレクトリの同一ファイル名が処理できない！！
    # filename = os.path.basename(filepath)
    # if filename not in bpy.data.images:
    #     bpy.data.images.load(filepath)
    # return bpy.data.images[filename]
    return bpy.data.images.load(filepath)

def get_material(matname):
    if matname in bpy.data.materials:
        mat = bpy.data.materials[matname]
        if mat.library is None:
            return mat
    mat = bpy.data.materials.new(name=matname)
    mat.diffuse_color = (1, 1, 1)
    return mat
    





# class OnetimeHandler():
#     func = None
#     def __init__(self, func):
#         self.func = func
#         self.store()
    
#     def execute(self, context):
#         self.func()
#         bpy.app.handlers.scene_update_post.remove(self.execute)

#     def store(self):
#         bpy.app.handlers.scene_update_post.append(self.execute)

# OnetimeHandler_Func = None
# def OnetimeHandler(func):
#     global OnetimeHandler_Func
#     OnetimeHandler_Func = func
#     bpy.app.handlers.scene_update_post.append(OnetimeHandler_Exec)

# def OnetimeHandler_Exec(context):
#     global OnetimeHandler_Func
#     OnetimeHandler_Func()
#     bpy.app.handlers.scene_update_post.remove(OnetimeHandler_Exec)

def get_area(areatype):
    for area in bpy.context.screen.areas:
        if area.type == areatype:
            return area
    return None

def get_override(areatype):
    override = bpy.context.copy()
    override['area'] = get_area(areatype)
    return override




"""
テクスチャ列挙
の中のイメージ列挙
パック
"""

def pack_textures(mat):
    if not mat or mat.is_library_indirect:
        print("no mat.")
        return

    for i in range(len(mat.texture_slots)):
        tslot = mat.texture_slots[i]

        if not tslot or not tslot.texture or not tslot.texture.image:
            continue

        try:
            tslot.texture.image.pack()
            print("packed:%s"%str(tslot.texture.image))
        except:
            print("error:%s"%str(tslot.texture.image))
            pass
        

def random_color():
    return (random.random(), random.random(), random.random())


def get_random_from_array(array):
    i = random.randint(0, len(array)-1)
    return array[i]

def random_id(length, uppercase=False):
    """
    length桁のランダムIDを生成する。
    """
    #https://qiita.com/okkn/items/3aef4458ed2269a59d63
    small_alphabets = [chr(i) for i in range(97, 97+26)]
    large_alphabets = [chr(i) for i in range(65, 65+26)]
    numbers = [chr(i) for i in range(48, 48+10)]
    characters = []
    if uppercase:
        characters.extend(large_alphabets)
    else:
        characters.extend(small_alphabets)
    characters.extend(numbers)

    result = ""
    for i in range(length):
        result += get_random_from_array(characters)
    return result

def id(arg):
    """
    オブジェクトのユニークIDを生成・取得する。
    引数にオブジェクトを指定するとそのオブジェクトにIDを設定する。
    ID文字列を指定すると合致するオブジェクトを返す。
    """
    if not arg:
        print("! fjw.id():arg is None!")
        return None

    if type(arg) == str:
        for obj in bpy.context.scene.objects:
            if "fjwid" in obj:
                if obj["fjwid"] == arg:
                    return obj
    else:
        obj = arg
        if "fjwid" not in obj:
            obj["fjwid"] = random_id(16, True)
        return obj["fjwid"]

def duplicate(obj):
    deselect()
    activate(obj)
    bpy.ops.object.duplicate()
    return active()


class Transform():
    def __init__(self, obj, copy=True):
        location = obj.location
        rotation_euler = obj.rotation_euler
        rotation_quaternion = obj.rotation_quaternion
        scale = obj.scale
        if copy:
            location = location.copy()
            rotation_euler = rotation_euler.copy()
            rotation_quaternion = rotation_quaternion.copy()
            scale = scale.copy()

        self.location = location
        self.rotation_euler = rotation_euler
        self.rotation_quaternion = rotation_quaternion
        self.scale = scale

        if hasattr(obj, "head"):
            head = obj.head
            tail = obj.tail
            if copy:
                head = head.copy()
                tail = tail.copy()
            self.head = head
            self.tail = tail

        if hasattr(obj, "vector"):
            vector = obj.vector
            if copy:
                vector = vector.copy()
            self.vector = vector



class EditState:
    active_obj = None
    selected_objects = None
    obj_mode = None

    @classmethod
    def store(cls):
        """アクティブオブジェクト、選択とモードの状態を保存する"""
        cls.active_obj = active()
        cls.selected_objects = get_selected_list()
        if cls.active_obj is not None:
            cls.obj_mode = cls.active_obj.mode

    @classmethod
    def restore(cls):
        mode("OBJECT")
        deselect()
        if cls.active_obj is not None:
            activate(cls.active_obj)
            mode(cls.obj_mode)


def create_object(name, obj_type, data_type=None):
    scene = bpy.context.scene
    datalist = getattr(bpy.data, obj_type)
    if not data_type:
        data = datalist.new(name=name)
    else:
        data = datalist.new(name=name, type=data_type)
    obj = bpy.data.objects.new(name=name, object_data=data)
    scene.objects.link(obj)
    return obj

def append(filepath, func):
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to = func(data_from)
    return data_to

def dummy():
    return



