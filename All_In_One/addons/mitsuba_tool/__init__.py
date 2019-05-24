#  __init__.py
#  date : 02/02/2017
# author: Laurent Boiron 
# 

# blender addon for mitsuba export

bl_info = {
    "name": "Mitsuba Tools",
    "description": "Tools for mitsuba",
    "author": "Laurent Boiron (INIRA/Graphdeco)",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "category": "Learnbgame",
    }

import bpy
from . import camera
from . import gen_lookat_params

def register():
    gen_lookat_params.register()
    camera.register()

def unregister():
    gen_lookat_params.unregister()
    camera.unregister()

if __name__ == "__main__":
    register()




