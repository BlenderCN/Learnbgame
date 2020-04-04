bl_info = {
    "name": "New Object",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import sys

def register():

    argv = sys.argv
    argv = argv[argv.index("--") + 1:] 
    bpy.ops.import_mesh.ply(filepath=argv[0] + "/meshed-poisson.ply")
    
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            modDec = obj.modifiers.new("Decimate", type = "DECIMATE")
            bpy.context.scene.update()
            #len(obj.data.vertices) 

            while modDec.face_count >= 20000:
                modDec.ratio *= 0.5
                bpy.context.scene.update()
                
                
    bpy.ops.export_mesh.ply(filepath= argv[0] + "/decimated.ply", use_normals=False, use_uv_coords=False)


def unregister():
    pass


if __name__ == "__main__":
    register()
