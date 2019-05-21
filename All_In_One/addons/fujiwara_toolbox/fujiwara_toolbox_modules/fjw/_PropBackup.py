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


class PropBackup():
    def __init__(self, obj):
        # バックアップの親オブジェクトを指定する
        self.obj = obj
        self.props = []

    def store(self, attr_name):
        # バックアップするプロパティ名を指定する
        val = getattr(self.obj, attr_name)
        self.props.append((attr_name, val))
    
    def copyto(self, dest_obj):
        # 別のオブジェクトにプロパティをコピーする
        for prop in self.props:
            setattr(dest_obj, prop[0], prop[1])

    def restore(self):
        # すべてのバックアップしたプロパティを復帰する
        for prop in self.props:
            setattr(self.obj, prop[0], prop[1])

class ObjectsPropBackups():
    def __init__(self, objects):
        self.backups = []
        for obj in objects:
            self.backups.append(PropBackup(obj))
    
    def store(self, attr_name):
        for bu in self.backups:
            bu.store(attr_name)
    
    def restore(self):
        for bu in self.backups:
            bu.restore()
