
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *

import os

def OpenAllWMOGroups(rootName):
    i = 0
    group_list = []
    while True:
        groupName = rootName + "_" + str(i).zfill(3) + ".wmo"
        if(os.path.isfile(groupName) == False):
            break
        group = WMO_group_file()
        group.Read(open(groupName, 'rb'))
        group_list.append(group)
        i += 1

    return group_list

def read(filename):
    f = open(filename, "rb")
    
    # Check if file is WMO root or WMO group, or unknown
    f.seek(12)
    hdr = ChunkHeader()
    hdr.Read(f)
    f.seek(0)
    
    group_list = []
    
    if(hdr.Magic == "DHOM"):
        # root WMO
        root = WMO_root_file()
        root.Read(f)
        rootName = os.path.splitext(filename)[0]
        group_list.extend(OpenAllWMOGroups(rootName))
    elif(hdr.Magic == "PGOM"):
        # group WMO

        # load root WMO
        rootName = filename[:-8]
        root = WMO_root_file()
        root.Read(open(rootName + ".wmo", "rb"))
        #group_list.extend(OpenAllWMOGroups(rootName))
        group = WMO_group_file()
        group.Read(f)
        group_list.append(group)
    else:
        raise Exception("File seems to be corrupted")

    # load all materials in root file
    root.LoadMaterials(bpy.path.display_name_from_filepath(rootName), os.path.dirname(filename) + "\\")

    # load all lights
    root.LoadLights(bpy.path.display_name_from_filepath(rootName))

    # create meshes
    for i in range(len(group_list)):
        objName = bpy.path.display_name_from_filepath(group_list[i].filename)
        group_list[i].LoadObject(objName, root.materials, None, root.mogn)

