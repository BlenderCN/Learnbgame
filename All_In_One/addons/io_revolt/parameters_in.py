"""
Name:    parameters_in
Purpose: Importing cars using the parameters.txt file

Description:
Imports entire cars using the carinfo module.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(carinfo)
    imp.reload(prm_in)

import os
import bpy
import bmesh
from mathutils import Vector
from . import common
from . import carinfo
from . import prm_in

from .common import *


def import_file(filepath, scene):
    """
    Imports a parameters.txt file and loads car body and wheels.
    """

    PARAMETERS[filepath] = carinfo.read_parameters(filepath)

    # Imports the car with all supported files
    import_car(scene, PARAMETERS[filepath], filepath)

    # Removes parameters from dict so they can be reloaded next time
    PARAMETERS.pop(filepath)


def import_car(scene, params, filepath):
    body = params["model"][params["body"]["modelnum"]]
    body_loc = to_blender_coord(params["body"]["offset"])
    wheel0loc = to_blender_coord(params["wheel"][0]["offset1"])
    wheel1loc = to_blender_coord(params["wheel"][1]["offset1"])
    wheel2loc = to_blender_coord(params["wheel"][2]["offset1"])
    wheel3loc = to_blender_coord(params["wheel"][3]["offset1"])

    folder = os.sep.join(filepath.split(os.sep)[:-1])

    # Checks if the wheel models exist
    wheel0_modelnum = int(params["wheel"][0]["modelnum"])
    if wheel0_modelnum >= 0:
        wheel0 = params["model"][wheel0_modelnum]
        if wheel0.split(os.sep)[-1] in os.listdir(folder):
                wheel0path = os.sep.join([folder, wheel0.split(os.sep)[-1]])
    else:
        wheel0 = None

    wheel1_modelnum = int(params["wheel"][1]["modelnum"])
    if wheel1_modelnum >= 0:
        wheel1 = params["model"][wheel1_modelnum]
        if wheel1.split(os.sep)[-1] in os.listdir(folder):
                wheel1path = os.sep.join([folder, wheel1.split(os.sep)[-1]])
    else:
        wheel1 = None

    wheel2_modelnum = int(params["wheel"][2]["modelnum"])
    if wheel2_modelnum >= 0:
        wheel2 = params["model"][wheel2_modelnum]
        if wheel2.split(os.sep)[-1] in os.listdir(folder):
                wheel2path = os.sep.join([folder, wheel2.split(os.sep)[-1]])
    else:
        wheel2 = None

    wheel3_modelnum = int(params["wheel"][3]["modelnum"])
    if wheel3_modelnum >= 0:
        wheel3 = params["model"][wheel3_modelnum]
        if wheel3.split(os.sep)[-1] in os.listdir(folder):
                wheel3path = os.sep.join([folder, wheel3.split(os.sep)[-1]])
    else:
        wheel3 = None

    # Checks if the body is in the same folder
    if body.split(os.sep)[-1] in os.listdir(folder):
        bodypath = os.sep.join([folder, body.split(os.sep)[-1]])

    # Creates the car body and sets the offset
    body_obj = prm_in.import_file(bodypath, scene)
    body_obj.location = body_loc

    # Creates the wheel objects or an empty if the wheel file is not present
    if wheel0:
        wheel = prm_in.import_file(wheel0path, scene)
    else:
        wheel = bpy.data.objects.new("wheel 0", None)
        scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
    wheel.location = wheel0loc
    wheel.parent = body_obj

    if wheel1:
        wheel = prm_in.import_file(wheel1path, scene)
    else:
        wheel = bpy.data.objects.new("wheel 1", None)
        scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
    wheel.location = wheel1loc
    wheel.parent = body_obj

    if wheel2:
        wheel = prm_in.import_file(wheel2path, scene)
    else:
        wheel = bpy.data.objects.new("wheel 2", None)
        scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
    wheel.location = wheel2loc
    wheel.parent = body_obj

    if wheel3:
        wheel = prm_in.import_file(wheel3path, scene)
    else:
        wheel = bpy.data.objects.new("wheel 3", None)
        scene.objects.link(wheel)
        wheel.empty_draw_type = "SPHERE"
        wheel.empty_draw_size = 0.1
    wheel.location = wheel3loc
    wheel.parent = body_obj
