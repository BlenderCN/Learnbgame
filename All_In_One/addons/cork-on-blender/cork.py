import bpy

from .exceptions import *


def has_triangulate_modifier(ob):
    """if there is an existent modifier, that's all we need"""
    for modifier in ob.modifiers:
        if modifier.type == 'TRIANGULATE' and \
           modifier.show_render:
               return True


def create_triangulate_modifier(ob):
    """if there is no triangulate modifier creates a new one"""
    if not has_triangulate_modifier(ob):
        return ob.modifiers.new('Cork Triangulation', 'TRIANGULATE')
    else:
        return None


def delete_triangulate_modifier(ob, modifier):
    """remove previously created modifier"""
    if modifier:
        ob.modifiers.remove(modifier)


def slice_out(context, cork, method, base, plane):
    import os
    import subprocess
    import tempfile
    import shutil

    try:
        dirpath = tempfile.mkdtemp()
    except Exception as E:
        raise InvalidTemporaryDir(E)

    scene = context.scene
    active = scene.objects.active

    filepath_base = os.path.join(dirpath, 'base.off')
    filepath_plane = os.path.join(dirpath, 'plane.off')
    filepath_result = os.path.join(dirpath, 'result.off')

    try:
        bpy.ops.import_mesh.off.poll()
    except AttributeError:
        raise ImportOffsetException()

    # export base
    print("Exporting file \"{0}\"".format(filepath_base))
    scene.objects.active = base
    if bpy.ops.export_mesh.off.poll():
        modifier = create_triangulate_modifier(base)
        bpy.ops.export_mesh.off(filepath=filepath_base)
        delete_triangulate_modifier(base, modifier)
    else:
        scene.objects.active = active
        raise ExportMeshException(base, filepath_base)

    # export plane to OFF
    print("Exporting file \"{0}\"".format(filepath_plane))
    scene.objects.active = plane
    if bpy.ops.export_mesh.off.poll():
        modifier = create_triangulate_modifier(plane)
        bpy.ops.export_mesh.off(filepath=filepath_plane)
        delete_triangulate_modifier(plane, modifier)
    else:
        scene.objects.active = active
        raise ExportMeshException(plane, filepath_plane)

    # call cork with arguments
    print("{0} {1} {2} {3} {4}".format(cork, method, filepath_base, filepath_plane, filepath_result))
    try:
        subprocess.call((cork, method, filepath_base, filepath_plane, filepath_result))
    except Exception as error:
        raise error

    # import resulting OFF mesh
    print("Importing file \"{0}\"".format(filepath_result))
    if bpy.ops.import_mesh.off.poll():
        bpy.ops.import_mesh.off(filepath=filepath_result)
    else:
        scene.objects.active = active
        raise ImportMeshException(filepath_result)

    # move object to a new layer
    result = [obj for obj in context.selected_objects if obj not in (base, plane)][0]
    result.layers[1] = True
    result.select = False

    print("Object \"{0}\" created successfully".format(result.name))

    # restore previous status
    scene.objects.active = active

    # cleanup temporary folder
    shutil.rmtree(dirpath)

