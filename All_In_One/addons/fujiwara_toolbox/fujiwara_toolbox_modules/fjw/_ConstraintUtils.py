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


class ConstraintUtils():
    def __init__(self,obj):
        self.obj = obj
        self.constraints = obj.constraints
    
    def add(self, name, type):
        constraint = self.constraints.new(type)
        if name != "":
            constraint.name = name
        return constraint

    def remove(self, constraint):
        self.constraints.remove(constraint)

    def remove_byname(self, name):
        if name not in self.constraints:
            return
        constraint = self.constraints[name]
        self.remove(constraint)

    def find(self, name):
        for constraint in self.constraints:
            if name in constraint.name:
                return constraint
        return None

    def find_list(self, name):
        result = []
        for constraint in self.constraints:
            if name in constraint.name:
                result.append(constraint)
        return result
        
    def find_bytype(self, type):
        for constraint in self.constraints:
            if type == constraint.type:
                return constraint
        return None

    def show(self, constraint):
        if constraint != None:
            constraint.mute = False

    def hide(self, mod):
        if constraint != None:
            constraint.mute = True

