import bpy
from . import convert


def export(report, filename):
    file = open(filename, 'w')
    armature = next(obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE')

    skeleton = convert.from_armature_to_skeleton(armature)
    mesh = next(obj for obj in bpy.context.selected_objects if obj.type == 'MESH')

    sls_mesh = convert.from_mesh_to_sls_mesh(mesh)

    file.write(skeleton.to_sls())
    file.write(sls_mesh.to_sls())
    file.close()