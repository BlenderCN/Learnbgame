
from . import m2_format
from .m2_format import *

from . import m2_file
from .m2_file import *

import os

def OpenAllSkinFiles(rootName):
    i = 0
    skin_list = []
    while True:
        skinName = rootName + str(i).zfill(2) + ".skin"
        if(os.path.isfile(skinName) == False):
            break
        skin = M2SkinFile()
        skin.read(open(skinName, 'rb'))
        skin_list.append(skin)
        i += 1

    return skin_list

def read(filename):
    f = open(filename, "rb")
    skin_list = []

    # root WMO
    root = M2File()
    root.read(f)
    rootName = os.path.splitext(filename)[0]
    skin_list.extend(OpenAllSkinFiles(rootName))

    # load all materials in root file
    #root.LoadMaterials(bpy.path.display_name_from_filepath(rootName), os.path.dirname(filename) + "\\")

    # load all lights
    #root.LoadLights(bpy.path.display_name_from_filepath(rootName))
    #root.LoadPortals(bpy.path.display_name_from_filepath(rootName))

    # create meshes
    skin_list[0].draw_submesh(root)
    

