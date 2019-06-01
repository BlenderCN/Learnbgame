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


class MaterialStates():
    class MaterialState():
        def __init__(self, mat):
            self.material = mat
            self.use_nodes = mat.use_nodes
            self.diffuse_color = (mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b)
            self.specular_color = (mat.specular_color.r, mat.specular_color.g, mat.specular_color.b)
            self.diffuse_intensity = mat.diffuse_intensity
            self.specular_intensity = mat.specular_intensity
            self.specular_hardness = mat.specular_hardness
            self.use_shadeless = mat.use_shadeless
            self.use_transparency = mat.use_transparency
            self.transparency_method = mat.transparency_method
            self.alpha = mat.alpha

            self.use_textures = []
            for state in mat.use_textures:
                self.use_textures.append(state)
        
        def restore(self):
            mat = self.material


            mat.use_nodes = self.use_nodes
            mat.diffuse_color = self.diffuse_color
            mat.specular_color = self.specular_color
            mat.diffuse_intensity = self.diffuse_intensity
            mat.specular_intensity = self.specular_intensity
            mat.specular_hardness = self.specular_hardness
            mat.use_shadeless = self.use_shadeless
            mat.use_transparency = self.use_transparency
            mat.transparency_method = self.transparency_method
            mat.alpha = self.alpha
            for index, state in enumerate(self.use_textures):
                mat.use_textures[index] = state



    def __init__(self, material_list):
        self.materials = []

        for mat in material_list:
            if not mat:
                continue
            self.materials.append(MaterialStates.MaterialState(mat))
        
    def restore(self):
        for matstate in self.materials:
            matstate.restore()

