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


class ViewState():
    def store_current_viewstate(self):
        for obj in bpy.data.objects:
            self.viewstates.append([obj,obj.hide,obj.hide_render])

    def __init__(self):
        self.viewstates = []
        self.store_current_viewstate()
        pass

    def restore_viewstate(self):
        for viewstate in self.viewstates:
            obj = viewstate[0]
            obj.hide = viewstate[1]
            obj.hide_render = viewstate[2]

    def delete(self):
        del self.viewstates
