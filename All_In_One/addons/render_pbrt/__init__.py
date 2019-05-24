bl_info = {
    "name": "PBRTv3 Exporter",
    "category": "Learnbgame",
}

import sys
import os

currDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(currDir)

import pbrt

def register():
    pbrt.register()

def unregister():
    pbrt.unregister()
