import bpy
import bmesh
import struct
import json
from . import materials, entities, meshes, light_data


def write(report, dir, filepath, scene):
    objects = scene.objects
    blender_objects = [o for o in objects if not o.parent and o.type in {"MESH", "EMPTY", "LIGHT"}]
    blender_objects = sorted(blender_objects, key=lambda x: x.name, reverse=False)
    
    root = list()
    for blender_object in blender_objects:
        root.append(entities.entity_path(blender_object))
    level_file = open(filepath, 'w')
    level_file.write(json.dumps(root))
    level_file.close()
    report({'INFO'}, "Wrote: " + filepath)
    report({'INFO'}, "Wrote level " + scene.name)

    entities.write(report, dir, objects)

    return {'FINISHED'}
