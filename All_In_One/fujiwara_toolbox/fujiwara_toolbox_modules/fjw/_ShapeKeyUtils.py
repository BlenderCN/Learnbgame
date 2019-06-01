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



class ShapeKeyUtils():
    def __init__(self, obj):
        self.obj = obj
        if obj.data.shape_keys is None:
            obj.shape_key_add(name="Basis")
        self.shape_keys = obj.data.shape_keys
        self.key_blocks = obj.data.shape_keys.key_blocks

    def get_key_block(self, name):
        if name not in self.key_blocks:
            self.obj.shape_key_add(name=name)
        return self.key_blocks[name]

    def add_key(self, name):
        return self.get_key_block(name)
    
    def find_key(self, name):
        if name not in self.key_blocks:
            return None
        return self.key_blocks[name]

    def set_mute(self, name, state):
        kb = self.get_key_block(name)
        if kb is None:
            return False
        kb.mute = state
        return True

    def set_value(self, name, value):
        kb = self.get_key_block(name)
        if kb is None:
            return False
        kb.value = value
        return True
    
    def set_value_and_key(self, name, value, mute):
        self.set_value(name, value)
        self.set_mute(name, mute)

    def get_key_index(self, name):
        return self.key_blocks.find(name)

    def set_active_key(self, name):
        index = self.get_key_index(name)
        self.obj.active_shape_key_index = index

    def remove_all_keys(self):
        for kb in self.key_blocks:
            self.obj.shape_key_remove(kb)
    