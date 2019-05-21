import bpy
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper
from shutil import copyfile

import numpy as np
from . import msh
import gzip
import struct
import shutil

from functools import partial
import multiprocessing

import argparse

C = bpy.context
D = bpy.data

def writeBobj(outFile, verts, tris):
    #Write a .bobj file
    with gzip.open(outFile, "wb") as f:
        string = struct.pack("i", len(verts))
        f.write(string)
        for v in verts:
            string=struct.pack("fff", v[0], v[1], v[2])
            f.write(string)
        string = struct.pack("i", len(verts))
        f.write(string)
        for n in verts:
            string=struct.pack("fff", n[0], n[1], n[2])
            f.write(string)
        string = struct.pack("i", len(tris))
        f.write(string)
        for t in tris:
            string=struct.pack("iii", t[0], t[1], t[2])
            f.write(string)
    return 0;


class import_mesh_sequence_fluids(bpy.types.Operator, ImportHelper):
    bl_idname = "iscd.import_mesh_sequence_fluids"
    bl_label  = "Import results from a fluids simulation"
    bl_options = {"REGISTER", "UNDO"}

    start  = bpy.props.IntProperty( name="startFrame", description="starting frame", default=0, min=0, max=5000)
    end    = bpy.props.IntProperty( name="endFrame",   description="ending   frame", default=10, min=1, max=5001)

    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )

    def execute(self, context):
        self.directory = os.path.dirname(self.properties.filepath)

        print(self.start, self.end, self.directory)

        # 0 - Argument parsing
        case = (self.properties.filepath.split("/")[-1]).split(".")[0]

        files = [f for f in os.listdir(self.directory) if case in f and ".mesh" in f]
        files.sort(key=lambda x: int(x.split(".")[1]))
        print(files)

        path = os.path.join(self.directory, "blendercache")
        ind = 0
        path += str(ind).zfill(3)
        while os.path.exists(path):
            ind+=1
            path = path[:-3] + str(ind).zfill(3)
        os.mkdir(path)

        # 3 - Loop on the data files
        for i, f in enumerate(files):

            #Get the info
            print(i, f)
            mesh = msh.Mesh(os.path.join(self.directory, f))
            filename = os.path.join(path, "fluidsurface_final_"   + str(self.start + i).zfill(4) + ".bobj.gz")
            writeBobj(filename, mesh.verts[:,:3], mesh.tris[:,:3])

        # 4 - Create the blender smulation object
        def add_simulation(path_to_bobj):
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.editmode_toggle()
            bpy.context.active_object.name = path_to_bobj.split("/")[-1]
            bpy.ops.object.modifier_add(type='FLUID_SIMULATION')
            bpy.context.object.modifiers["Fluidsim"].settings.type = 'DOMAIN'
            bpy.context.object.modifiers["Fluidsim"].settings.viewport_display_mode = 'FINAL'
            bpy.context.object.modifiers["Fluidsim"].settings.filepath = path_to_bobj
        add_simulation(path)


        """Parallel implementation
        pool      = multiprocessing.Pool(15)
        SETTINGS = []
        for i,v in enumerate(values):
        settings = {
            "index": i,
            "value": v,
            "path":  path,

        }
        pool.map(runThread, [[i,v,path] for i,v in enumerate(values)])
        """

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(import_mesh_sequence_fluids)

def unregister() :
    bpy.utils.unregister_class(import_mesh_sequence_fluids)
