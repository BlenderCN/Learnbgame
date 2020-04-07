# <pep8 compliant>
# 27eaf1d60b06083a8bc5e86aab56fd86cad77cc4
# ----------------------------------------------------------
# Author: Fofight
# ----------------------------------------------------------


bl_info = {
    'name': 'Learnbgame',
    'description': 'Learn by game',
    'author': 'Fofight',
    'license': 'GPL',
    'version': (1, 1, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Tools > Learnbgame',
    'warning': '',
    'wiki_url': 'https://github.com/BlenderCN/Learnbgame/wiki',
    'tracker_url': 'https://github.com/BlenderCN/Learnbgame/issues',
    'link': 'https://github.com/BlenderCN/Learnbgame',
    'support': 'COMMUNITY',
    'category': 'Add Mesh'
    }
##########################Import Module############################

import os
import random
import sys
import time
import datetime

try :
    import openbabel
    import pybel
except:
    pass

import json
import math
from math import sqrt,pi,radians, sin, cos, tan, asin, degrees

import bgl,blf
import subprocess
import bpy

from math import acos

from mathutils import Vector,Matrix

from . import poqbdb
from . import spaceship_generator
from . import spacestation
from .book import Book
from .shelf import Shelf
#from .ch_trees import gui
from .grove import Grove_Operator
from .LearnbgamEngine import learnbgamEditor

def register():
    pass




def unregister():
    pass




if __name__ == "__main__":

    register()
