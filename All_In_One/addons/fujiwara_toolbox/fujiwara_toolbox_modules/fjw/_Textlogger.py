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


class Textlogger():
    text_data = None
    @classmethod
    def log(cls, text):
        if not cls.text_data:
            cls.text_data = bpy.data.texts.new("fjw_log")
        cls.text_data.write(text+"\n")
      
