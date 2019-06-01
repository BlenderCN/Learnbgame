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


class UVUtils():
    # アクティブUVレイヤーを取得とか簡単にしたい
    def __init__(self, obj):
        self.obj = obj
        pass
    
    def is_empty(self):
        if len(self.obj.data.uv_textures) == 0:
            return True
        else:
            return False

    def active(self):
        return self.obj.data.uv_textures.active
    
    def activate(self, name):
        index = self.obj.data.uv_textures.find(name)
        if index != -1:
            self.obj.data.uv_textures.active_index = index
        else:
            self.new(name)
        return self.active()

    def new(self, name="UVMap"):
        return self.obj.data.uv_textures.new(name)

    def find(self, name):
        if name in self.obj.data.uv_textures:
            return self.obj.data.uv_textures[name]
        return None


    def uv(self, name=None):
        """
        ざっくりアクセス関数
        引数が空＝アクティブを返す
        引数が名前
            検索してそれをアクティブにし、返す
        ない場合は新規作成
        """
        if self.is_empty():
            # 新規作成して返す
            if name:
                return self.new(name)
            else:
                return self.new()
        
        if not name:
            return self.active()
        
        uv = self.find(name)
        if uv:
            return self.activate(uv)
        
        return self.new(name)

