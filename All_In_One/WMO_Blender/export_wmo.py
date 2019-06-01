
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *

import os

def write(filepath):
    f = open(filepath, "wb")
    root_filename = filepath

    wmo_root = WMO_root_file()

    base_name = os.path.splitext(filepath)[0]

    for iObj in range(len(bpy.context.selected_objects)):

        # check if object is mesh
        if (not isinstance(bpy.context.selected_objects[iObj].data, bpy.types.Mesh)):
            continue

        group_filename = base_name + "_" + str(iObj).zfill(3) + ".wmo"
        group_file = open(group_filename, "wb")

        # write group file
        wmo_group = WMO_group_file()
        wmo_group.Save(group_file, bpy.context.selected_objects[iObj], wmo_root)

    # write root file
    wmo_root.Save(f)
    return
