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



class ObjectState():
    def __init__(self, obj):
        self.obj = obj

    def store_transform(self):
        self.location = copy.copy(self.obj.location)
        self.scale = copy.copy(self.obj.scale)
        self.rotation_mode = self.obj.rotation_mode
        self.rotation_euler = copy.copy(self.obj.rotation_euler)
        self.rotation_quaternion = copy.copy(self.obj.rotation_quaternion)

    def restore_transform(self):
        self.obj.location = self.location
        self.obj.scale = self.scale
        # self.obj.rotation_mode = self.rotation_mode
        self.obj.rotation_euler = self.rotation_euler
        self.obj.rotation_quaternion = self.rotation_quaternion
  