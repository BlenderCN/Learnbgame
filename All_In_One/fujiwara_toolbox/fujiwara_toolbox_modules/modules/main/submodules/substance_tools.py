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


class SubstanceTools():
    """
    9   512
    10  1024
    11  2048
    12  4096
    """
    defalut_tex_size = ""
    tex_size = defalut_tex_size
    toolkit_dir = ""

    self_dir = ""
    blend_name = ""
    sbs_generated_dir = ""

    sbsar_path = ""
    graph_list = []
    graph_url = ""

    def base_init(self):
        if self.toolkit_dir == "":
            pref = fujiwara_toolbox.conf.get_pref()
            self.toolkit_dir = pref.SubstanceAutomationToolkit_dir

        self.self_dir = os.path.dirname(bpy.data.filepath)
        self.blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        self.sbs_generated_dir = os.path.normpath(self.self_dir + os.sep + "textures" + os.sep + self.blend_name + "_sbs_generated")

    def __init__(self, obj):
        self.base_init()

        self.obj = obj
        self.obj_name = obj.name.replace(".","_")

        self.sbsarname = os.path.splitext(os.path.basename(self.sbsar_path))[0]

        self.random_id = '{0:04d}'.format(int(random.random()*10000))

        self.matname = os.path.normpath(self.obj_name + "_" + self.sbsarname + "_" + self.random_id + "_sbsgen")
        self.matdir = os.path.normpath(self.sbs_generated_dir + os.sep + self.matname)

        self.src_dir = self.matdir + os.sep + "src"
        self.src_obj_path = os.path.normpath(self.src_dir + os.sep + self.obj_name + ".obj")

        

    def export(self):
        fjw.deselect()
        fjw.activate(self.obj)
        if len(self.obj.data.uv_textures) == 0:
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()
            fjw.mode("OBJECT")
        if not os.path.exists(self.src_dir):
            os.makedirs(self.src_dir)
        bpy.ops.export_scene.obj(filepath=self.src_obj_path,check_existing=False,use_selection=True,use_mesh_modifiers=False)

    def bake(self, bake_type):
        if not os.path.exists(self.src_dir):
            os.makedirs(self.src_dir)
        baker = os.path.normpath(self.toolkit_dir + os.sep + "sbsbaker.exe")
        cmdstr = '"%s" %s "%s" --output-path "%s"'%(baker, bake_type, self.src_obj_path, self.src_dir)
        if self.tex_size != "":
            cmdstr += ' --output-size %s,%s'%(self.tex_size, self.tex_size)
        print(cmdstr)
        p = subprocess.Popen(cmdstr)
        p.wait()

    @classmethod
    def info(self):
        print("*"*50)
        self.base_init(self)
        self.graph_list = []
        render = os.path.normpath(self.toolkit_dir + os.sep + "sbsrender.exe")
        cmdstr = '"%s" info "%s"'%(render, self.sbsar_path)
        print(cmdstr)
        p = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # p.wait()
        stdout_data, stderr_data = p.communicate()
        text = stdout_data.decode().replace("\r", "\n")
        lines = text.split("\n")
        for l in lines:
            if "pkg:" not in l:
                continue
            l = l.replace("GRAPH-URL pkg://", "")
            if "/" in l:
                continue
            # l = l.replace("GRAPH-URL", "")
            self.graph_list.append(l)
        print("*"*50)

    def render(self):
        render = os.path.normpath(self.toolkit_dir + os.sep + "sbsrender.exe")
        entries = '--set-entry ambient-occlusion@"%s"'%(os.path.normpath(self.src_dir+os.sep+self.obj_name+"_ambient-occlusion.png"))
        entries += ' --set-entry curvature@"%s"'%(os.path.normpath(self.src_dir+os.sep+self.obj_name+"_curvature.png"))
        entries += ' --set-entry normal-world-space@"%s"'%(os.path.normpath(self.src_dir+os.sep+self.obj_name+"_normal-world-space.png"))
        entries += ' --set-entry position@"%s"'%(os.path.normpath(self.src_dir+os.sep+self.obj_name+"_position.png"))
        entries += ' --set-entry uv-map@"%s"'%(os.path.normpath(self.src_dir+os.sep+self.obj_name+"_uv-map.png"))
        entries += ' --set-entry world-space-direction@"%s"'%(os.path.normpath(self.src_dir+os.sep+self.obj_name+"_world-space-direction.png"))
        if self.tex_size != "":
            entries += ' --set-value $outputsize@%s,%s'%(self.tex_size,self.tex_size)
        if self.graph_url != "":
            entries += ' --input-graph "%s"'%self.graph_url
        cmdstr = '"%s" render --output-name="%s_{inputGraphUrl}_{outputNodeName}" %s --output-path "%s" "%s"'%(render, self.obj_name, entries, self.matdir, self.sbsar_path)
        print(cmdstr)
        p = subprocess.Popen(cmdstr)
        p.wait()
        self.tex_size = self.defalut_tex_size

    tex_identifiers = {}
    tex_identifiers_all = ""
        
    @classmethod
    def __setup_texidentifiers(cls):
        if cls.tex_identifiers_all == "":
            cls.tex_identifiers["color"] = "_baseColor|_color|_diffuse|_fullrender"
            cls.tex_identifiers["modelinfo"] = "_curvature|_ambient_occlusion|_ambient-occlusion"
            cls.tex_identifiers["alpha"] = "_Alpha"
            cls.tex_identifiers["height"] = "_Height|_Normal"
            cls.tex_identifiers["ao"] = "_AO|_ambient_occlusion|_ambient-occlusion"
            cls.tex_identifiers["metallic"] = "_metallic"
            cls.tex_identifiers["roughness"] = "_roughness"
            cls.tex_identifiers["diffuse"] = "_diffuse"
            cls.tex_identifiers["glossiness"] = "_glossiness"
            cls.tex_identifiers["normal"] = "_normal"
            cls.tex_identifiers["specular"] = "_specular"
            cls.tex_identifiers_all = ""
            for tex_identifier in cls.tex_identifiers:
                cls.tex_identifiers_all += cls.tex_identifiers[tex_identifier] + "|"

    @classmethod
    def __texid_match(cls, text, targetid):
        cls.__setup_texidentifiers()
        if re.search(cls.tex_identifiers[targetid], text,re.IGNORECASE) is not None:
            return True
        return False

    def __clear_materials(self):
        self.obj.data.materials.clear()


    #テクスチャ回収
    def material_setup(self):
        self.__clear_materials()
        files = os.listdir(self.matdir)
        mat = fjw.get_material(self.matname)
        mat["sbsid"] = self.matname
        mat.diffuse_color = (0.214035, 0.214035, 0.214035)

        print("material_setup")
        print(self.matname)

        sortedfile = []
        for file in files:
            print(file)
            if ".png" not in file:
                continue
            if self.__texid_match(file, "color"):
                sortedfile.append(file)
                break
        for file in files:
            if ".png" not in file:
                continue
            if file not in sortedfile:
                sortedfile.append(file)
        
        for file in sortedfile:
            if ".png" not in file:
                continue
            img = fjw.load_img(self.matdir + os.sep + file)
            bpy.ops.file.make_paths_relative()

            tex = bpy.data.textures.new(file, "IMAGE")
            tex.image = img

            texture_slot = mat.texture_slots.add()
            texture_slot.texture = tex

            #タイプ別セットアップ
            #PBR
            if self.__texid_match(file, "color"):
                texture_slot.use_map_color_diffuse = True
                texture_slot.diffuse_color_factor = 1
                texture_slot.use_rgb_to_intensity = False
                texture_slot.blend_type = 'SCREEN'
                # texture_slot.use_map_alpha = True
                # mat.use_transparency = True
                # mat.alpha = 1
            if self.__texid_match(file, "alpha"):
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_alpha = True
                texture_slot.use_rgb_to_intensity = True
                texture_slot.alpha_factor = 1
                texture_slot.blend_type = 'MIX'
                mat.use_transparency = True
                mat.alpha = 0
            if self.__texid_match(file, "normal"):
                texture_slot.texture.use_normal_map = True
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_normal = True
                texture_slot.normal_factor = 0.1
            if self.__texid_match(file, "height"):
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_normal = True
                texture_slot.normal_factor = 0.1
            if self.__texid_match(file, "ao"):
                texture_slot.use_map_color_diffuse = True
                texture_slot.diffuse_color_factor = 1
                texture_slot.blend_type = 'MULTIPLY'
            # if self.__texid_match(file, "metallic"):
            #     texture_slot.use_map_color_diffuse = False
            #     texture_slot.use_map_hardness = True
            #     texture_slot.hardness_factor = 1
            # if self.__texid_match(file, "roughness"):
            #     texture_slot.use_map_color_diffuse = False
            #     texture_slot.use_map_specular = True
            #     texture_slot.specular_factor = 1
            # if self.__texid_match(file, "shadow"):
            #     tex.image.use_alpha = False
            #     mat.use_transparency = True
            #     mat.alpha = 0
            #     texture_slot.blend_type = 'MIX'
            #     texture_slot.use_map_color_diffuse = True
            #     texture_slot.diffuse_color_factor = 1
            #     texture_slot.use_map_alpha = True
            #     texture_slot.alpha_factor = -1
            #LEGACY
            if self.__texid_match(file, "glossiness"):
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_color_spec = True

            if self.__texid_match(file, "specular"):
                texture_slot.use_map_color_diffuse = False
                texture_slot.use_map_specular = True


        self.obj.data.materials.append(mat)
        ctm = fjw.CyclesTexturedMaterial([mat])
        ctm.execute()
                   
            

    #リンクのないマテリアルのディレクトリを削除
    #マテリアルが存在しないディレクトリを削除、のほうがいい
    @classmethod
    def clean_materials(self):
        self.base_init(self)
        if not os.path.exists(self.sbs_generated_dir):
            return
        files = os.listdir(self.sbs_generated_dir)

        for file in files:
            if file in bpy.data.materials:
                continue

            found = False
            for mat in bpy.data.materials:
                if mat.library:
                    continue
                    
                if "sbsid" not in mat:
                    continue

                if file == mat["sbsid"]:
                    found = True
                    break

            if not found:
                shutil.rmtree(self.sbs_generated_dir + os.sep + file)

        # dellist = []
        # for mat in bpy.data.materials:
        #     if mat.library is not None:
        #         continue
        #     if "_sbsgen" not in mat.name:
        #         continue
        #     if mat.users == 0:
        #         dellist.append(mat)
        
        # for mat in dellist:
        #     gendir = SubstanceTools.sbs_generated_dir
        #     matpath = gendir + os.sep + mat.name
        #     if os.path.exists(matpath):
        #         shutil.rmtree(matpath)
        #     bpy.data.materials.remove(mat)

    @classmethod
    def remove_not_used_materials(self, obj):
        if obj.type != "MESH":
            return
        current = fjw.active()
        fjw.activate(obj)
        fjw.mode("OBJECT")
        used_indexes = []
        for face in obj.data.polygons:
            i = face.material_index
            if i not in used_indexes:
                used_indexes.append(i)
        print("used_indexes:"+str(used_indexes))

        used_materials = []
        for i in used_indexes:
            if i >= len(obj.material_slots):
                continue
            mat = obj.material_slots[i].material
            if mat not in used_materials:
                used_materials.append(mat)
        print(used_materials)
        
        delmats = []
        for m in range(len(used_materials)):
            for i in range(len(obj.material_slots)):
                mslot = obj.material_slots[i]
                print("mslot:"+str(mslot.material))
                print("in:"+str(mslot.material in used_materials))
                if mslot.material and mslot.material not in used_materials:
                    print("remove:"+str(i)+" "+str(mslot.material))
                    obj.active_material_index = i
                    bpy.ops.object.material_slot_remove()
                    delmats.append(mslot.material)
                    break
        for mat in delmats:
            if mat.users == 0:
                bpy.data.materials.remove(mat)

        fjw.activate(current)
