
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *

import os

def write(filepath, WMOid, ambient, use_ambient, fill_water, skybox_path, source_doodads, source_fog):
    f = open(filepath, "wb")
    root_filename = filepath

    m2_file = M2File()
    
    base_name = os.path.splitext(filepath)[0]
    
    portal_count = 0
    for ob in bpy.data.objects:
        if(ob.type == "MESH"):
            obj_mesh = ob.data
            if(obj_mesh.WowPortalPlane.Enabled):
                obj_mesh.WowPortalPlane.PortalID = portal_count
                portal_count+=1
    
    iObj = 0
    for i in range(len(bpy.data.objects)):
    #for iObj in range(len(bpy.context.selected_objects)):

        # check if object is mesh
        """"if (not isinstance(bpy.context.selected_objects[iObj].data, bpy.types.Mesh)):
            continue
        
        # check if object is portal
        if(bpy.context.selected_objects[iObj].data.WowPortalPlane.Enabled):
            continue"""
        
        if (not isinstance(bpy.data.objects[i].data, bpy.types.Mesh)):
            continue
        
        # check if object is portal
        if(bpy.data.objects[i].data.WowPortalPlane.Enabled):
            continue
        
        #check if object is root source
        if(bpy.data.objects[i].data.WowWMORoot.IsRoot):
            continue
        
        print("Export group "+bpy.data.objects[i].name)
        group_filename = base_name + "_" + str(iObj).zfill(3) + ".wmo"
        group_file = open(group_filename, "wb")

        # write group file
        wmo_group = WMO_group_file()
        #wmo_group.Save(group_file, bpy.context.selected_objects[iObj], wmo_root, iObj)
        wmo_group.Save(group_file, bpy.data.objects[i], wmo_root, iObj, source_doodads)
        iObj+=1
        
    # write root file
    print("Export root file") 
    wmo_root.Save(f, WMOid, ambient, use_ambient, fill_water, skybox_path, source_doodads, source_fog)
    return
