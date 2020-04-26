import bpy
import sys
import inspect
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

from .main import *
from ._NodeUtils import *


class CyclesTexturedMaterial():
    def __init__(self, materials):
        self.materials = materials

    def imagetex_node(self, ntu, path):
        node = ntu.add("ShaderNodeTexImage", "Texture Image")
        node.image = bpy.data.images.load(filepath=path)
        return node

    def add_tex(self, ntu, connect_from, path, connect_to):
        n_tex = self.imagetex_node(ntu,path)
        ntu.link(connect_from, n_tex.inputs["Vector"])
        ntu.link(n_tex.outputs["Color"], connect_to)
        return n_tex

    def find_from_list(self, strlist, target):
        for obj in strlist:
            if target in obj:
                return obj
        return None

    def execute(self):
        for mat in self.materials:
            print("### CyclesTexturedMaterial")
            ntu = NodetreeUtils(mat)
            ntu.activate()
            ntu.cleartree()

            n_out = ntu.add("ShaderNodeOutputMaterial", "Output Material")
            n_texcoord = ntu.add("ShaderNodeTexCoord", "Texture Coordinates")
            n_map = ntu.add("ShaderNodeMapping", "Mapping")
            n_map.vector_type = "POINT"
            ntu.link(n_texcoord.outputs["UV"], n_map.inputs["Vector"])

            n_prncpl = ntu.add("ShaderNodeBsdfPrincipled", "Principled BSDF")
            ntu.link(n_prncpl.outputs["BSDF"], n_out.inputs["Surface"])
            n_prncpl.inputs["Base Color"].default_value = (mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, 1)

            n_mix = ntu.add("ShaderNodeMixRGB", "Mix")
            n_mix.blend_type = "OVERLAY"
            n_mix.inputs[0].default_value = 1.0
            n_mix.inputs[2].default_value = (0.5,0.5,0.5,1)
            ntu.link(n_mix.outputs[0], n_prncpl.inputs["Base Color"])

            # n_rgb = ntu.add("ShaderNodeRGB", "RGB")
            # n_rgb.outputs[0].default_value = (0.5,0.5,0.5,1)
            # ntu.link(n_rgb.outputs[0], n_mix.inputs[2])


            n_norm = ntu.add("ShaderNodeNormalMap", "Normal Map")
            ntu.link(n_norm.outputs["Normal"], n_prncpl.inputs["Normal"])

            texpath = ""
            #テクスチャ関係
            for tslot in mat.texture_slots:
                if tslot is not None and tslot.texture is not None and tslot.texture.image is not None:
                    img = tslot.texture.image
                    if "_basecolor" in img.filepath:
                        texpath = bpy.path.abspath(img.filepath)
            
            if texpath != "":
                texname = os.path.splitext(os.path.basename(texpath))[0]
                texid = texname.replace("_basecolor", "")
                texdir = os.path.dirname(texpath)
                print(texpath)
                print(texdir)

                files = os.listdir(texdir)
                print(str(files))
                texlist = []
                for file in files:
                    if texid in file:
                        texlist.append(file)
                
                #basecolor
                identifier = "_basecolor" 
                texfilename = self.find_from_list(texlist, texid + identifier)
                if texfilename is not None:
                    path = os.path.normpath(texdir + os.sep + texfilename)
                    n_tex = self.add_tex(ntu, n_map.outputs["Vector"], path, n_mix.inputs[1])
                    n_tex.color_space = "COLOR"
                #metallic
                identifier = "_metallic" 
                texfilename = self.find_from_list(texlist, texid + identifier)
                if texfilename is not None:
                    path = os.path.normpath(texdir + os.sep + texfilename)
                    n_tex = self.add_tex(ntu, n_map.outputs["Vector"], path, n_prncpl.inputs["Metallic"])
                    n_tex.color_space = "NONE"
                #normal
                identifier = "_normal" 
                texfilename = self.find_from_list(texlist, texid + identifier)
                if texfilename is not None:
                    path = os.path.normpath(texdir + os.sep + texfilename)
                    n_tex = self.add_tex(ntu, n_map.outputs["Vector"], path, n_norm.inputs["Color"])
                    n_tex.color_space = "NONE"
                #roughness
                identifier = "_roughness" 
                texfilename = self.find_from_list(texlist, texid + identifier)
                if texfilename is not None:
                    path = os.path.normpath(texdir + os.sep + texfilename)
                    n_tex = self.add_tex(ntu, n_map.outputs["Vector"], path, n_prncpl.inputs["Roughness"])
                    n_tex.color_space = "NONE"
                #height
                identifier = "_height" 
                texfilename = self.find_from_list(texlist, texid + identifier)
                if texfilename is not None:
                    path = os.path.normpath(texdir + os.sep + texfilename)
                    n_tex = self.add_tex(ntu, n_map.outputs["Vector"], path, n_out.inputs["Displacement"])
                    n_tex.color_space = "NONE"

                n_prncpl.location = (ntu.posx, ntu.posy)
                ntu.posx += 200
                n_out.location = (ntu.posx, ntu.posy)
            
            #レンダラがcyclesじゃなかったらノードをオフにしておく
            if bpy.context.scene.render.engine != 'CYCLES':
                mat.use_nodes = False
