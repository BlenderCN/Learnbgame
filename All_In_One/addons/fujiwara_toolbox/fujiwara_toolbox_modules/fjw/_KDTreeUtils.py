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


class KDTreeUtils():
    #https://docs.blender.org/api/blender_python_api_2_78c_release/mathutils.kdtree.html
    def __init__(self):
        self.items = []
        self.kd = None

    def append_data(self, co, item):
        self.items.append([co,item])

    def construct_kd_tree(self):
        self.kd = kdtree.KDTree(len(self.items))
        for index, value in enumerate(self.items):
            self.kd.insert(value[0], index)
        self.kd.balance()

    def get_item(self, index):
        print(self.items[index])
        return self.items[index][1]

    def find(self, co):
        kddata = self.kd.find(co)
        return self.get_item(kddata[1])

    def find_n(self, co, n):
        kddatas = self.kd.find_n(co, n)
        result = []
        for kddata in kddatas:
            result.append(self.get_item(kddata[1]))
        return result

    def find_range(self, co, radius):
        kddatas = self.kd.find_range(co, radius)
        result = []
        for kddata in kddatas:
            result.append(self.get_item(kddata[1]))
        return result
        
    def finish(self):
        self.kd = kdtree.KDTree(0)

