# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import random
import sys
import time
import os
import traceback
from os.path import join, dirname, abspath
from shutil import copyfile
from math import *

# Blender imports
import bpy
from bpy.props import *
props = bpy.props

# Addon imports
from .common import *


def getActiveContextInfo(ag_idx=None):
    scn = bpy.context.scene
    ag_idx = ag_idx or scn.aglist_index
    ag = scn.aglist[ag_idx]
    return scn, ag


def getRandomizedOrient(orient, random_amount):
    """ returns randomized orientation based on user settings """
    return orient + random.uniform(-random_amount, random_amount)


def getOffsetLocation(ag, loc):
    """ returns randomized location offset """
    X = loc.x + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.xLocOffset
    Y = loc.y + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.yLocOffset
    Z = loc.z + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.zLocOffset
    return (X, Y, Z)


def getOffsetRotation(ag, rot):
    """ returns randomized rotation offset """
    X = rot.x + (random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.xRotOffset)
    Y = rot.y + (random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.yRotOffset)
    Z = rot.z + (random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.zRotOffset)
    return (X, Y, Z)

# def toDegrees(degreeValue):
#     """ converts radians to degrees """
#     return (degreeValue*57.2958)


def getBuildSpeed(ag):
    """ calculates and returns build speed """
    return floor(ag.buildSpeed)


def getObjectVelocity(ag):
    """ calculates and returns brick velocity """
    frameVelocity = round(2**(10-ag.velocity))
    return frameVelocity


def getAnimLength(ag, objects_to_move, listZValues, layerHeight, invertBuild, skipEmptySelections):
    tempObjCount = 0
    numLayers = 0
    while len(objects_to_move) > tempObjCount:
        numObjs = len(getNewSelection(listZValues, layerHeight, invertBuild, skipEmptySelections))
        numLayers += 1 if numObjs > 0 or not skipEmptySelections else 0
        tempObjCount += numObjs
    return (numLayers - 1) * getBuildSpeed(ag) + getObjectVelocity(ag) + 1


def getFileNames(dir):
    """ list files in the given directory """
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and not f.startswith(".")]


def getPresetTuples(fileNames=None, transferDefaults=False):
    if not fileNames:
        # initialize presets path
        path = get_addon_preferences().presetsFilepath
        # set up presets folder and transfer default presets
        if not os.path.exists(path):
            os.makedirs(path)
        if transferDefaults:
            transferDefaultsToPresetsFolder(path)
        # get list of filenames in presets directory
        fileNames = getFileNames(path)
    # refresh preset names
    fileNames.sort()
    presetNames = [(fileNames[i][:-3], fileNames[i][:-3], "Select this preset!") for i in range(len(fileNames))]
    presetNames.append(("None", "None", "Don't use a preset"))
    return presetNames


def transferDefaultsToPresetsFolder(presetsPath):
    defaultPresetsPath = join(dirname(dirname(abspath(__file__))), "lib", "default_presets")
    fileNames = getFileNames(defaultPresetsPath)
    if not os.path.exists(presetsPath):
        os.mkdir(presetsPath)
    for fn in fileNames:
        dst = os.path.join(presetsPath, fn)
        backup_dst = os.path.join(presetsPath, "backups", fn)
        if os.path.isfile(dst):
            os.remove(dst)
        elif os.path.isfile(backup_dst):
            continue
        src = os.path.join(defaultPresetsPath, fn)
        copyfile(src, dst)


# def setOrientation(orientation):
#     """ sets transform orientation """
#     if orientation == "custom":
#         bpy.ops.transform.create_orientation(name="LEGO Build Custom Orientation", use_view=False, use=True, overwrite=True)
#     else:
#         bpy.ops.transform.select_orientation(orientation=orientation)


def getListZValues(ag, objects, rotXL=False, rotYL=False):
    """ returns list of dicts containing objects and ther z locations relative to layer orientation """
    # assemble list of dictionaries into 'listZValues'
    listZValues = []
    if not rotXL:
        rotXL = [getRandomizedOrient(ag.xOrient, ag.orientRandom) for i in range(len(objects))]
        rotYL = [getRandomizedOrient(ag.yOrient, ag.orientRandom) for i in range(len(objects))]
    for i,obj in enumerate(objects):
        l = obj.matrix_world.to_translation() if ag.useGlobal else obj.location
        rotX = rotXL[i]
        rotY = rotYL[i]
        zLoc = (l.z * cos(rotX) * cos(rotY)) + (l.x * sin(rotY)) + (l.y * -sin(rotX))
        listZValues.append({"loc":zLoc, "obj":obj})

    # sort list by "loc" key (relative z values)
    listZValues.sort(key=lambda x: x["loc"], reverse=not ag.invertBuild)

    # return list of dictionaries
    return listZValues, rotXL, rotYL


def getObjectsInBound(listZValues, z_lower_bound, invertBuild):
    """ select objects in bounds from listZValues """
    objsInBound = []
    # iterate through objects in listZValues (breaks when outside range)
    for i,lst in enumerate(listZValues):
        # set obj and z_loc
        obj = lst["obj"]
        z_loc = lst["loc"]
        # check if object is in bounding z value
        if z_loc >= z_lower_bound and not invertBuild or z_loc <= z_lower_bound and invertBuild:
            objsInBound.append(obj)
        # if not, break for loop and pop previous objects from listZValues
        else:
            for j in range(i):
                listZValues.pop(0)
            break
    return objsInBound


def getNewSelection(listZValues, layerHeight, invertBuild, skipEmptySelections):
    """ selects next layer of objects """
    # get new upper and lower bounds
    props.z_upper_bound = listZValues[0]["loc"] if skipEmptySelections or props.z_upper_bound is None else props.z_lower_bound
    props.z_lower_bound = props.z_upper_bound + layerHeight * (1 if invertBuild else -1)
    # select objects in bounds
    objsInBound = getObjectsInBound(listZValues, props.z_lower_bound, invertBuild)
    return objsInBound


def setBoundsForVisualizer(ag, listZValues):
    for i in range(len(listZValues)):
        obj = listZValues[i]["obj"]
        if not ag.meshOnly or obj.type == "MESH":
            props.objMinLoc = obj.location.copy()
            break
    for i in range(len(listZValues)-1,-1,-1):
        obj = listZValues[i]["obj"]
        if not ag.meshOnly or obj.type == "MESH":
            props.objMaxLoc = obj.location.copy()
            break


def layers(l):
    all = [False]*20
    if type(l) == int:
        all[l] = True
    elif type(l) == list:
        for l in lList:
            allL[l] = True
    elif l.lower() == "all":
        all = [True]*20
    elif l.lower() == "none":
        pass
    elif l.lower() == "active":
        all = list(bpy.context.scene.layers)
    else:
        sys.stderr.write("Argument passed to 'layers()' function not recognized")
    return all


def updateAnimPreset(self, context):
    scn = bpy.context.scene
    if scn.animPreset != "None":
        import importlib.util
        pathToFile = os.path.join(get_addon_preferences().presetsFilepath, scn.animPreset + ".py")
        if os.path.isfile(pathToFile):
            spec = importlib.util.spec_from_file_location(scn.animPreset + ".py", pathToFile)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.execute()
        else:
            badPreset = str(scn.animPreset)
            if badPreset in scn.assemblme_default_presets:
                errorString = "Preset '%(badPreset)s' could not be found. This is a default preset – try reinstalling the addon to restore it." % locals()
            else:
                errorString = "Preset '%(badPreset)s' could not be found." % locals()
            sys.stderr.write(errorString)
            print(errorString)
            presetNames = getPresetTuples()

            bpy.types.Scene.animPreset = EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=presetNames,
                update=updateAnimPreset,
                default="None")

            bpy.types.Scene.animPresetToDelete = EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=presetNames,
                default="None")
            scn.animPreset = "None"

    return None


def clearAnimation(objs):
    objs = confirmIter(objs)
    for obj in objs:
        obj.animation_data_clear()
    bpy.context.scene.update()


def createdWithUnsupportedVersion(ag):
    return ag.version[:3] != bpy.props.assemblme_version[:3]


def setInterpolation(objs, data_path, mode, idx):
    objs = confirmIter(objs)
    for obj in objs:
        if obj.animation_data is None:
            continue
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve is None or not fcurve.data_path.startswith(data_path):
                continue
            fcurve.keyframe_points[idx].interpolation = mode


def animateObjects(ag, objects_to_move, listZValues, curFrame, locInterpolationMode='LINEAR', rotInterpolationMode='LINEAR'):
    """ animates objects """

    # initialize variables for use in while loop
    objects_moved = []
    last_len_objects_moved = 0
    mult = 1 if ag.buildType == "ASSEMBLE" else -1
    inc  = 1 if ag.buildType == "ASSEMBLE" else 0
    velocity = getObjectVelocity(ag)
    insertLoc = ag.xLocOffset != 0 or ag.yLocOffset != 0 or ag.zLocOffset != 0 or ag.locationRandom != 0
    insertRot = ag.xRotOffset != 0 or ag.yRotOffset != 0 or ag.zRotOffset != 0 or ag.rotationRandom != 0
    layerHeight = ag.layerHeight
    invertBuild = ag.invertBuild
    skipEmptySelections = ag.skipEmptySelections
    kfIdxLoc = -1
    kfIdxRot = -1

    # insert first location keyframes
    if insertLoc:
        insertKeyframes(objects_to_move, "location", curFrame)
    # insert first rotation keyframes
    if insertRot:
        insertKeyframes(objects_to_move, "rotation_euler", curFrame)


    while len(objects_to_move) > len(objects_moved):
        # print status to terminal
        updateProgressBars(True, True, len(objects_moved) / len(objects_to_move), last_len_objects_moved / len(objects_to_move), "Animating Layers")
        last_len_objects_moved = len(objects_moved)

        # get next objects to animate
        newSelection = getNewSelection(listZValues, layerHeight, invertBuild, skipEmptySelections)
        objects_moved += newSelection

        # move selected objects and add keyframes
        kfIdxLoc = -1
        kfIdxRot = -1
        if len(newSelection) != 0:
            # insert location keyframes
            if insertLoc:
                insertKeyframes(newSelection, "location", curFrame)
                kfIdxLoc -= inc
            # insert rotation keyframes
            if insertRot:
                insertKeyframes(newSelection, "rotation_euler", curFrame)
                kfIdxRot -= inc

            # step curFrame backwards
            curFrame -= velocity * mult

            # move object and insert location keyframes
            if insertLoc:
                for obj in newSelection:
                    if ag.useGlobal:
                        obj.matrix_world.translation = getOffsetLocation(ag, obj.matrix_world.translation)
                    else:
                        obj.location = getOffsetLocation(ag, obj.location)
                insertKeyframes(newSelection, "location", curFrame, if_needed=True)
            # rotate object and insert rotation keyframes
            if insertRot:
                for obj in newSelection:
                    # if ag.useGlobal:
                    #     # TODO: Fix global rotation functionality
                    #     # NOTE: Solution 1 - currently limited to at most 360 degrees
                    #     xr, yr, zr = getOffsetRotation(ag, Vector((0,0,0)))
                    #     inv_mat = obj.matrix_world.inverted()
                    #     xAxis = mathutils_mult(inv_mat, Vector((1, 0, 0)))
                    #     yAxis = mathutils_mult(inv_mat, Vector((0, 1, 0)))
                    #     zAxis = mathutils_mult(inv_mat, Vector((0, 0, 1)))
                    #     xMat = Matrix.Rotation(xr, 4, xAxis)
                    #     yMat = Matrix.Rotation(yr, 4, yAxis)
                    #     zMat = Matrix.Rotation(zr, 4, zAxis)
                    #     obj.matrix_local = mathutils_mult(zMat, yMat, xMat, obj.matrix_local)
                    # else:
                    obj.rotation_euler = getOffsetRotation(ag, obj.rotation_euler)
                insertKeyframes(newSelection, "rotation_euler", curFrame, if_needed=True)

            # step curFrame forwards
            curFrame += (velocity - getBuildSpeed(ag)) * mult

        # handle case where 'ag.skipEmptySelections' == False and empty selection is grabbed
        elif not ag.skipEmptySelections:
            # skip frame if nothing selected
            curFrame -= getBuildSpeed(ag) * mult
        # handle case where 'ag.skipEmptySelections' == True and empty selection is grabbed
        else:
            os.stderr.write("Grabbed empty selection. This shouldn't happen!")

    curFrame -= (velocity - getBuildSpeed(ag)) * mult
    # insert final location keyframes
    if insertLoc:
        insertKeyframes(objects_to_move, "location", curFrame)
    # insert final rotation keyframes
    if insertRot:
        insertKeyframes(objects_to_move, "rotation_euler", curFrame)

    # set interpolation modes for moved objects
    setInterpolation(objects_moved, 'loc', locInterpolationMode, kfIdxLoc)
    setInterpolation(objects_moved, 'rot', rotInterpolationMode, kfIdxRot)

    updateProgressBars(True, True, 1, 0, "Animating Layers", end=True)

    return objects_moved, curFrame

def assemblme_handle_exception():
    handle_exception(log_name="AssemblMe_log", report_button_loc="AssemblMe > Animations > Report Error")
