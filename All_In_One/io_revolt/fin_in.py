"""
Name:    fin_in
Purpose: Imports Re-Volt instance files (.fin)

Description:
Imports Instance files.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(rvstruct)

import bpy
import bmesh
import mathutils

from . import common
from . import rvstruct
from . import prm_in

from .rvstruct import Instances, Vector
from .common import *
from mathutils import Color


def import_file(filepath, scene):
    props = scene.revolt

    with open(filepath, 'rb') as file:
        filename = os.path.basename(filepath)
        fin = Instances(file)
        dprint("Imported FIN file.")

    for instance in fin.instances:
        import_instance(filepath, scene, instance)


def import_instance(filepath, scene, instance):
    folder = os.sep.join(filepath.split(os.sep)[:-1])

    prm_fname = "{}.prm".format(instance.name).lower()

    # Searches for files that are longer than 8 chars
    if not prm_fname in os.listdir(folder):
        for f in os.listdir(folder):
            if f.startswith(instance.name.lower()) and ".prm" in f:
                prm_fname = f
                break

    if prm_fname in [ob.name for ob in scene.objects]:
        dprint("Found already existing instance: {}".format(prm_fname))
        data = scene.objects[prm_fname].data

        # Creates a duplicate object and links it to the scene
        instance_obj = bpy.data.objects.new(name=prm_fname, object_data=data)
        scene.objects.link(instance_obj)

    elif prm_fname in os.listdir(folder):
        dprint("Found prm in dir.")
        prm_path = os.path.join(folder, prm_fname)
        # Creates the object and links it to the scene
        instance_obj = prm_in.import_file(prm_path, scene)

    else:
        print("Could not find instance {} at {}".format(prm_fname, folder))
        # Creates an empty object instead
        instance_obj = bpy.data.objects.new("prm_fname", None)
        scene.objects.link(instance_obj)
        instance_obj.empty_draw_type = "SPHERE"

    instance_obj.matrix_world = to_trans_matrix(instance.or_matrix)
    instance_obj.location = to_blender_coord(instance.position)

    instance_obj.revolt.is_instance = True
    instance_obj.revolt.fin_col = [(128+c)/255 for c in instance.color]
    envcol = (*instance.env_color.color, 255-instance.env_color.alpha)
    instance_obj.revolt.fin_envcol = [c/255 for c in envcol]
    instance_obj.revolt.fin_priority = instance.priority

    flag = instance.flag
    instance_obj.revolt.fin_model_rgb = bool(flag & FIN_SET_MODEL_RGB)
    instance_obj.revolt.fin_env = bool(flag & FIN_ENV)
    instance_obj.revolt.fin_hide = bool(flag & FIN_HIDE)
    instance_obj.revolt.fin_no_mirror = bool(flag & FIN_NO_MIRROR)
    instance_obj.revolt.fin_no_lights = bool(flag & FIN_NO_LIGHTS)
    instance_obj.revolt.fin_no_cam_coll = bool(flag & FIN_NO_OBJECT_COLLISION)
    instance_obj.revolt.fin_no_obj_coll = bool(flag & FIN_NO_CAMERA_COLLISION)


