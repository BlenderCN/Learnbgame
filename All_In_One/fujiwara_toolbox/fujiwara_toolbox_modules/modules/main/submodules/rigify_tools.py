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


import random
from mathutils import *

# assetdir = fujiwara_toolbox.conf.assetdir
assetdir = ""

# class ChildInfo():
#     def __init__(self, obj):
#         self.obj = obj
#         self.parent_type = obj.parent_type
#         self.parent_bone = obj.parent_bone
#         self.print_info()

#     def print_info(self):
#         print("%s : %s, %s"%(self.obj.name, self.parent_type, self.parent_bone))

class RiggedObject():
    def __init__(self, obj, rig):
        self.obj = obj
        self.rig = rig
        self.rigname = rig.name
        self.parent_type = obj.parent_type
        self.parent_bone = obj.parent_bone
        self.hide = obj.hide
        obj.hide = False
        self.print_info()
        modu = fjw.Modutils(obj)
        arm = modu.find_bytype("ARMATURE")
        self.has_armature_mod = bool(arm)

    def set_parentinfo_from(self, rigged_object):
        self.parent_type = rigged_object.parent_type
        self.parent_bone = rigged_object.parent_bone
        self.has_armature_mod = rigged_object.has_armature_mod

    def get_rig(self):
        for obj in bpy.context.visible_objects:
            if obj.name == self.rigname:
                return obj
        return None

    def parent_clear(self):
        """
        ペアレントをクリアする。
        """
        fjw.deselect()
        fjw.activate(self.obj)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    def apply(self):
        """
        アーマチュア変形やボーン相対変形を適用する。
        ペアレントがクリアされている前提。
        """

        obj = self.obj

        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(obj)
        fjw.mode("OBJECT")

        #モディファイアの適用
        if obj.type == "MESH":
            modu = fjw.Modutils(obj)
            arm = modu.find_bytype("ARMATURE")
            modu.apply(arm)

        #トランスフォームの適用
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


    def reparent(self):
        """
        格納した情報に応じて再ペアレントする。
        """
        rig = self.get_rig()
        obj = self.obj

        modu = fjw.Modutils(self.obj)
        mod_arm = modu.find_bytype("ARMATURE")

        if  not self.has_armature_mod:
            fjw.mode("OBJECT")
            fjw.deselect()
            obj.select = True

            fjw.activate(rig)

            if self.parent_type == "OBJECT":
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            elif self.parent_type == "BONE":
                if self.parent_bone in rig.data.bones:
                    fjw.mode("POSE")

                    layerstates = []
                    for state in rig.data.layers:
                        layerstates.append(state)

                    rig.data.layers = [True for i in range(len(rig.data.layers))]

                    rig.data.bones.active = rig.data.bones[self.parent_bone]
                    bpy.ops.object.parent_set(type='BONE_RELATIVE')

                    rig.data.layers = layerstates
        else:
            #既存のアーマチュアmodを除去する
            mod_arms = modu.find_bytype_list("ARMATURE")
            for mod in mod_arms:
                modu.remove(mod)

            fjw.deselect()
            obj.select = True
            fjw.activate(rig)
            if "rigify_parenting" in obj:
                bpy.ops.object.parent_set(type=obj["rigify_parenting"])
            else:
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            fjw.activate(obj)
            modu.sort()
        pass
        self.obj.hide = self.hide

    def print_info(self):
        print("%s : %s, %s"%(self.obj.name, self.parent_type, self.parent_bone))

class RiggedObjects():
    def __init__(self, rig):
        self.rig = rig
        self.rigged_objects = []
        self.setup()

    def find_byname(self, name):
        for ro in self.rigged_objects:
            if ro.obj.name == name:
                return ro
        return None
    
    def set_parentinfo_from(self, rigged_objects):
        for ro in self.rigged_objects:
            src = rigged_objects.find_byname(ro.obj.name)
            ro.set_parentinfo_from(src)

    def setup(self):
        for child in self.rig.children:
            self.rigged_objects.append(RiggedObject(child,self.rig))
        
        #非childでもアーマチュアついてるものがある
        for obj in bpy.context.scene.objects:
            if obj in self.rigged_objects:
                continue
            if obj.type != "MESH":
                continue

            modu = fjw.Modutils(obj)
            mod_arm = modu.find_bytype("ARMATURE")
            if not mod_arm:
                continue

            if mod_arm.object == self.rig:
                self.rigged_objects.append(RiggedObject(obj, self.rig))


        return self.rigged_objects

    def reset_rig(self, rig):
        for robj in self.rigged_objects:
            robj.rig = rig

    def parent_clear(self):
        for robj in self.rigged_objects:
            robj.parent_clear()

    def apply(self):
        for robj in self.rigged_objects:
            robj.apply()

    def reparent(self):
        for robj in self.rigged_objects:
            robj.reparent()

class EditBoneData():
    def __init__(self, obj, edit_bone):
        # self.edit_bone = edit_bone
        self.obj = obj
        self.name = edit_bone.name
        #そのままコピーすると参照が入る！！
        self.head = (edit_bone.head.x,edit_bone.head.y,edit_bone.head.z)
        self.tail = (edit_bone.tail.x,edit_bone.tail.y,edit_bone.tail.z)
        self.roll = edit_bone.roll
        self.use_connect = edit_bone.use_connect
        self.use_deform = edit_bone.use_deform
        self.hide = edit_bone.hide
        if edit_bone.parent:
            self.has_parent = True
        else:
            self.has_parent = False
        if len(edit_bone.children) == 0:
            self.has_children = False
        else:
            self.has_children = True

    def set_pose_matrix(self):
        self.pose_matrix_head = self.__get_pose_matrix_head()
        self.pose_matrix_tail = self.__get_pose_matrix_tail()
    
    def __get_pose_matrix_head(self):
        pbone = self.obj.pose.bones[self.name]
        x = pbone.matrix[0][3]
        y = pbone.matrix[1][3]
        z = pbone.matrix[2][3]
        return Vector((x,y,z))

    def __get_pose_matrix_tail(self):
        pbone = self.obj.pose.bones[self.name]
        head = self.__get_pose_matrix_head()
        return head + pbone.vector

    def get_ebone(self):
        fjw.activate(self.obj)
        fjw.mode("EDIT")
        edit_bones = self.obj.data.edit_bones
        if self.name in edit_bones:
            ebone = edit_bones[self.name]
            return ebone
        return None

    def restore_info(self):
        ebone = self.get_ebone()
        if ebone:
            ebone.name = self.name
            ebone.use_deform = self.use_deform
            ebone.hide = self.hide
    
    def restore_info_from(self, fromdata):
        self.name = fromdata.name
        self.use_deform = fromdata.use_deform
        self.hide = fromdata.hide
        self.restore_info()

    def disconnect(self):
        ebone = self.get_ebone()
        ebone.use_connect = False
    
    def restore_connect(self):
        ebone = self.get_ebone()
        ebone.use_connect = self.use_connect

    def copy_shape(self, edit_bone_data, head=True, tail=True, roll=True):
        ebone = self.get_ebone()
        if ebone:
            if head:
                # ebone.head = edit_bone_data.head
                ebone.head = edit_bone_data.pose_matrix_head
            if tail:
                # ebone.tail = edit_bone_data.tail
                ebone.tail = edit_bone_data.pose_matrix_tail
            if roll:
                ebone.roll = edit_bone_data.roll
        self.obj.data.edit_bones.update()


class EditBonesData():
    def __init__(self, obj):
        self.obj = obj
        self.edit_bones = []
        self.setup()

        print("EditBonesData:%s, %d"%(self.obj.name, len(self.edit_bones)))

    def setup(self):
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(self.obj)
        fjw.mode("EDIT")
        for ebone in self.obj.data.edit_bones:
            self.edit_bones.append(EditBoneData(self.obj, ebone))
        
        fjw.mode("POSE")
        for ebdata in self.edit_bones:
            ebdata.set_pose_matrix()

    def get_ebone_byname(self, name):
        for ebone in self.edit_bones:
            if ebone.name == name:
                return ebone
        return None

    def restore_info_from(self, fromdata):
        """
        ボーン情報を指定オブジェクトから設定する。
        """
        for from_ebone in fromdata.edit_bones:
            ebone = self.get_ebone_byname(from_ebone.name)
            if ebone:
                ebone.restore_info_from(from_ebone)

    def __get_root_ebones(self, ebones):
        result = []
        for ebone in ebones:
            if not ebone.parent:
                result.append(ebone)
        return result

    def __get_ebone_children(self, ebone):
        result = []
        result.append(ebone.name)

        if len(ebone.children) == 0:
            return result

        for child in ebone.children:
            children_list = self.__get_ebone_children(child)
            result.extend(children_list)
        return result


    def get_treesort(self):
        """
        位置操作、ルートからやらないとめちゃくちゃになる。
        ので、ルートから子へとソートしたリストを作成する。
        結果はボーン名のリスト。
        """
        fjw.activate(self.obj)
        fjw.mode("EDIT")

        """
        階層順にやっていけば間違いない？
        途中で複数にわかれている場合どうするの？
        探索関数いるのでは？
        ていうかルートボーンだけ洗い出して、あとは
        get_childrenメソッドがあればいいのでは
        """
        ebones = self.obj.data.edit_bones
        roots = self.__get_root_ebones(ebones)


        result = []
        for root in roots:
            children_list = self.__get_ebone_children(root)
            result.extend(children_list)
        return result


class ArmatureTool():
    def __init__(self, obj):
        self.obj = obj
        self.name = obj.name
        self.groups = obj.users_group
        self.show_x_ray = obj.show_x_ray
        self.layers = []
        for state in obj.layers:
            self.layers.append(state)
        self.data_layers = []
        for state in obj.data.layers:
            self.data_layers.append(state)

        self.edit_bones_data = EditBonesData(obj)

    def reset_edit_bones(self):
        self.edit_bones_data = EditBonesData(self.obj)

    def restore_settings(self):
        self.obj.name = self.name
        for group in self.groups:
            fjw.group(group.name,[self.obj])
        self.obj.show_x_ray = self.show_x_ray
        self.obj.layers = self.layers

    def restore_settings_from(self, fromdata):
        self.name = fromdata.name
        self.groups = fromdata.groups
        self.show_x_ray = fromdata.show_x_ray
        self.layers = fromdata.layers
        self.restore_settings()

    def testprint(self):
        print("###test print###")
        print(self.name)
        print("%d bones"%(len(self.edit_bones_data.edit_bones)))
        # for ebone in self.edit_bones_data.edit_bones:
        #     print("self:"+ ebone.name)

    def show_all_layers(self):
        self.obj.data.layers = [True for i in range(len(self.obj.data.layers))]
    
    def restore_layers(self):
        self.obj.data.layers = self.data_layers
        

class Metarig(ArmatureTool):
    """
    ORG-は、子と分断されてたりする
    DEF-の、Head位置だけを反映すればいいのでは？
        子が接続しているボーンはHeadだけ反映、子がないor接続していないボーンはヘッドも反映する。
        Headが親側　Tailが子側
    """
    def __init__(self, obj):
        super().__init__(obj)

    def copy_shapes(self, edit_bones_data):
        """
        受け取ったデータのデータ通りにメタリグの形状を設定する。
        """

        fjw.activate(self.obj)
        fjw.mode("EDIT")

        for ebone in self.edit_bones_data.edit_bones:
            ebone.disconnect()

        #ORG-をコピー
        prefix="ORG-"
        for ebone in self.edit_bones_data.edit_bones:
            fixed_name = prefix + ebone.name
            src = edit_bones_data.get_ebone_byname(fixed_name)
            if src:
                ebone.copy_shape(src)
            else:
                print("not found:%s"%(fixed_name))
        #親のtailを子のheadにあわせる
        for ebone in self.edit_bones_data.edit_bones:
            if ebone.has_parent and ebone.use_connect:
                edit_bone = ebone.get_ebone()
                parent = edit_bone.parent
                parent.tail = edit_bone.head
        
        for ebone in self.edit_bones_data.edit_bones:
            ebone.restore_connect()


        fjw.mode("OBJECT")

class Rig(ArmatureTool):
    def __init__(self, rig):
        super().__init__(rig)
        self.rigged_objects = RiggedObjects(rig)

    def is_symmetry(self):
        armature = self.obj
        armu = fjw.ArmatureUtils(armature)
        for pbone in armu.pose_bones:
            if "_L" in pbone.name:
                lbone = pbone
                rname = pbone.name.replace("_L", "_R")
                if rname in armu.pose_bones:
                    rbone = armu.pose_bones[rname]
                    #微妙に誤差が出ることがあるので丸める
                    if round(rbone.head.x*100) != round((lbone.head.x * -1)*100):
                        # self.report({"INFO"}, "ボーンが左右非対称です。 %s, %s"%(rbone.name, lbone.name))
                        return False
        return True

    def apply_pose(self):
        """
        ポーズをデフォルトに設定する。トランスフォームも確定する。
        """
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(self.obj)
        fjw.mode("POSE")
        self.show_all_layers()
        bpy.ops.pose.reveal()
        for pbone in self.obj.pose.bones:
            pbone.bone.hide = False
            pbone.bone.select = True
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.visual_transform_apply()
        self.mute_constraints()
        fjw.mode("POSE")
        bpy.ops.pose.armature_apply()
        self.restore_layers()
        self.reset_edit_bones()
    
    def mute_constraints(self):
        pbones = self.obj.pose.bones
        for pbone in pbones:
            for c in pbone.constraints:
                c.mute = True
        self.obj.data.update_tag()
        fjw.mode("OBJECT")

class RigifyTools():
    def __init__(self):
        self.metarig = None
        self.rig = None

    def set_rig(self, rig):
        if rig:
            self.rig = Rig(rig)
    
    def set_metarig(self, metarig):
        if metarig:
            self.metarig = Metarig(metarig)


    def find_rig(self, rig=None):
        if rig:
            return rig
        
        rigname = ""
        win = bpy.context.window_manager
        if hasattr(win, "rigify_target_rig"):
            rigname = win.rigify_target_rig
        if rigname == "":
            rigname = "rig"

        for obj in bpy.context.scene.objects:
            if obj.type != "ARMATURE":
                continue
            if "rig_id" in obj.data and rigname == obj.name:
                return obj

        return None

    def find_metarig(self, metarig=None):
        if metarig:
            metarig.hide = False
            return metarig

        for obj in bpy.context.scene.objects:
            if obj.type != "ARMATURE":
                continue
            if "rig_id" not in obj.data and "rig" in obj.name:
                obj.hide = False
                return obj
        return None

    def is_symmetry(self, rig):
        rig = Rig(rig)
        return rig.is_symmetry()

    def gen_rig_and_reparent(self, metarig, unparent_at_rest=True):
        """
        genrigして再ペアレントする。
        """
        if metarig.type != "ARMATURE":
            return False

        layers_current = fjw.layers_current_state()
        fjw.layers_showall()

        objects_bu = fjw.ObjectsPropBackups(bpy.context.scene.objects)
        objects_bu.store("hide")
        for obj in bpy.context.scene.objects:
            obj.hide = False

        self.set_metarig(metarig)
        self.set_rig(self.find_rig())

        rig_old = None
        if self.rig:
            rig_old = self.rig
            if unparent_at_rest:
                self.rig.obj.data.pose_position = 'REST'
            self.rig.rigged_objects.parent_clear()
            rigdata = self.rig.obj.data
            fjw.delete([self.rig.obj])
            bpy.data.armatures.remove(rigdata)


        fjw.deselect()
        fjw.activate(metarig)
        bpy.ops.pose.rigify_generate()

        new_rig = Rig(fjw.active())
        if self.rig:
            new_rig.edit_bones_data.restore_info_from(self.rig.edit_bones_data)
            self.rig.rigged_objects.reset_rig(new_rig.obj)
        # bpy.ops.view3d.layers(nr=0, extend=False)
        if self.rig:
            self.rig.rigged_objects.reparent()
        # bpy.ops.view3d.layers(nr=0, extend=False)
        fjw.layers_show_list(layers_current)
        metarig.hide = True

        fjw.activate(new_rig.obj)
        fjw.mode("POSE")

        if rig_old:
            new_rig.restore_settings_from(rig_old)
        
        objects_bu.restore()

        return True

    def __rigify_fk2ik(self, rig):
        fjw.activate(rig)
        fjw.mode("POSE")
        bpy.ops.pose.select_all(action='SELECT')

        post_fix = ""
        for meth in inspect.getmembers(bpy.ops.pose):
            if "fk2ik" in meth[0]:
                post_fix = meth[0].split("_")[-1]
                break
        if post_fix != "":
            print("post_fix:%s"%post_fix)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_leg_fk2ik_'+ post_fix +'(thigh_fk="thigh_fk.L", shin_fk="shin_fk.L", foot_fk="foot_fk.L", mfoot_fk="MCH-foot_fk.L", thigh_ik="thigh_ik.L", shin_ik="MCH-thigh_ik.L", foot_ik="MCH-thigh_ik_target.L", mfoot_ik="MCH-thigh_ik_target.L")'
            print(evalstr)
            eval(evalstr)
            print(evalstr)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_leg_fk2ik_'+ post_fix +'(thigh_fk="thigh_fk.R", shin_fk="shin_fk.R", foot_fk="foot_fk.R", mfoot_fk="MCH-foot_fk.R", thigh_ik="thigh_ik.R", shin_ik="MCH-thigh_ik.R", foot_ik="MCH-thigh_ik_target.R", mfoot_ik="MCH-thigh_ik_target.R")'
            eval(evalstr)
            print(evalstr)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_arm_fk2ik_'+ post_fix +'(uarm_fk="upper_arm_fk.L", farm_fk="forearm_fk.L", hand_fk="hand_fk.L", uarm_ik="upper_arm_ik.L", farm_ik="MCH-upper_arm_ik.L", hand_ik="hand_ik.L")'
            eval(evalstr)
            print(evalstr)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_arm_fk2ik_'+ post_fix +'(uarm_fk="upper_arm_fk.R", farm_fk="forearm_fk.R", hand_fk="hand_fk.R", uarm_ik="upper_arm_ik.R", farm_ik="MCH-upper_arm_ik.R", hand_ik="hand_ik.R")'
            eval(evalstr)
            print(evalstr)

    def __rigify_ik2fk(self, rig):
        fjw.activate(rig)
        fjw.mode("POSE")
        bpy.ops.pose.select_all(action='SELECT')

        post_fix = ""
        for meth in inspect.getmembers(bpy.ops.pose):
            if "ik2fk" in meth[0]:
                post_fix = meth[0].split("_")[-1]
                break
        if post_fix != "":
            print("post_fix:%s"%post_fix)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_leg_ik2fk_'+ post_fix +'(thigh_fk="thigh_fk.L", shin_fk="shin_fk.L", foot_fk="foot_fk.L", mfoot_fk="MCH-foot_fk.L", thigh_ik="thigh_ik.L", shin_ik="MCH-thigh_ik.L", foot_ik="MCH-thigh_ik_target.L", mfoot_ik="MCH-thigh_ik_target.L")'
            print(evalstr)
            eval(evalstr)
            print(evalstr)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_leg_ik2fk_'+ post_fix +'(thigh_fk="thigh_fk.R", shin_fk="shin_fk.R", foot_fk="foot_fk.R", mfoot_fk="MCH-foot_fk.R", thigh_ik="thigh_ik.R", shin_ik="MCH-thigh_ik.R", foot_ik="MCH-thigh_ik_target.R", mfoot_ik="MCH-thigh_ik_target.R")'
            eval(evalstr)
            print(evalstr)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_arm_ik2fk_'+ post_fix +'(uarm_fk="upper_arm_fk.L", farm_fk="forearm_fk.L", hand_fk="hand_fk.L", uarm_ik="upper_arm_ik.L", farm_ik="MCH-upper_arm_ik.L", hand_ik="hand_ik.L")'
            eval(evalstr)
            print(evalstr)
            bpy.ops.pose.select_all(action='SELECT')
            evalstr = 'bpy.ops.pose.rigify_arm_ik2fk_'+ post_fix +'(uarm_fk="upper_arm_fk.R", farm_fk="forearm_fk.R", hand_fk="hand_fk.R", uarm_ik="upper_arm_ik.R", farm_ik="MCH-upper_arm_ik.R", hand_ik="hand_ik.R")'
            eval(evalstr)
            print(evalstr)


    def __rigify_ikfk_1(self, rig):
        for pb in rig.pose.bones:
            if "IK_FK" in pb:
                pb["IK_FK"] = 1

        for bn in rig.data.bones:
            bn.select = True
        
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0)

    def freeze_rig(self,rig):
        if rig.type != "ARMATURE":
            return False

        self.set_rig(rig)
        self.__rigify_fk2ik(rig)
        self.__rigify_ikfk_1(rig)
        self.rig.rigged_objects.apply()
        self.rig.rigged_objects.parent_clear()
        self.rig.apply_pose()
        self.rig.rigged_objects.reparent()
        fjw.mode("OBJECT")
        

    def metarig_shape_to_rig_shape(self,rig):
        if rig.type != "ARMATURE":
            return False

        layers_current = fjw.layers_current_state()
        fjw.layers_showall()

        self.set_rig(rig)
        self.set_metarig(self.find_metarig())

        if not self.metarig:
            print("Metarig not found.")
            return False

        self.rig.rigged_objects.parent_clear()    
        self.rig.rigged_objects.apply()
        self.metarig.copy_shapes(self.rig.edit_bones_data)
        self.rig.rigged_objects.reparent()
        fjw.layers_show_list(layers_current)


    def update_rig_proportion(self, rig):
        # self.freeze_rig(rig) #ポーズ形状から直接とってるのでもういらない
        self.metarig_shape_to_rig_shape(rig)
        metarig = self.find_metarig()
        fjw.activate(metarig)
        self.gen_rig_and_reparent(metarig, False)

