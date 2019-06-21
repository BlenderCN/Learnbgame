import bpy

def get_objects_in_scene(scene):
    if bpy.app.version >= (2, 80):
        return list(scene.collection.all_objects)
    else:
        return list(scene.objects)