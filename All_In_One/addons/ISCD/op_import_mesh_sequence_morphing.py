import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import colorsys
import numpy as np
import os
import sys

from . import msh

class import_mesh_sequence_morphing(bpy.types.Operator, ExportHelper):
    """Imports a morphing sequence"""
    bl_idname = "iscd.import_mesh_sequence_morphing"
    bl_label  = "Imports a sequence of .mesh files"

    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"

    @classmethod
    def poll(cls, context):
        return (
            context.mode=="OBJECT"
        )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob','check_existing'))
        err = importSequence(self, context, **keywords)
        if err:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}
def importSequence(operator, context, filepath):
    print(filepath)
    dotMesh = msh.Mesh(filepath)

    tris = [t.tolist()[:-1] for t in dotMesh.tris]
    verts = [t.tolist()[:-1] for t in dotMesh.verts]

    mesh_name = "basis"
    mesh = bpy.data.meshes.new(name=mesh_name)
    mesh.from_pydata(verts, [], tris)
    mesh.validate()
    mesh.update()
    del verts, tris
    scene = context.scene
    obj = bpy.data.objects.new(mesh.name, mesh)
    bpy.ops.object.select_all(action='DESELECT')
    scene.objects.link(obj)
    scene.objects.active = obj
    scene.update()

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()

    path = "/".join(filepath.split("/")[:-1])
    root = (filepath.split("/")[-1]).split(".")[0]

    files = [f for f in os.listdir(path) if ".mesh" in f and root in f]
    files.sort(key=lambda x:int(x.split(".")[-2]))

    for f in files[1:]:
        print(f)
        dotMesh = msh.Mesh(os.path.join(path, f))
        tris = [t.tolist()[:-1] for t in dotMesh.tris]
        verts = [t.tolist()[:-1] for t in dotMesh.verts]
        for basis in bpy.context.scene.objects:
            basis.select=True
            if basis.type == "MESH":
                shapeKey = basis.shape_key_add(from_mix=False)
                shapeKey.name = "1"
                for vert, newV in zip(basis.data.vertices, verts):
                    shapeKey.data[vert.index].co = newV
            basis.select=False

    for basis in bpy.context.scene.objects:
        if basis.type == "MESH":
            nb = len(files)
            scene = bpy.context.scene
            scene.frame_start = 1
            scene.frame_end   = 1 + nb * 3

            for i in range(nb):
                for j,key in enumerate(basis.data.shape_keys.key_blocks):
                    if i == j:
                        key.value = 1
                    else:
                        key.value = 0
                    key.keyframe_insert("value", frame=1 + 3*i)
    return 0

def import_sequence_func(self, context):
    self.layout.operator("iscd.import_mesh_sequence_morphing", text="Imports a .mesh sequence")
def register():
    bpy.utils.register_class(import_mesh_sequence_morphing)
    bpy.types.INFO_MT_file_import.append(import_sequence_func)
def unregister():
    bpy.utils.unregister_class(import_mesh_sequence_morphing)
    bpy.types.INFO_MT_file_import.remove(import_sequence_func)
