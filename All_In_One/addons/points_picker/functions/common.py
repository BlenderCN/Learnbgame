# Copyright (C) 2018 Christopher Gearhart
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
import platform
import itertools
import operator
import json
import traceback
import subprocess
import hashlib
from math import *

# Blender imports
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
from bpy.types import Object, Scene
props = bpy.props

# https://github.com/CGCookie/retopoflow
def bversion():
    """ return Blender version """
    bversion = '%03d.%03d.%03d' % (bpy.app.version[0], bpy.app.version[1], bpy.app.version[2])
    return bversion


def stopwatch(text:str, lastTime, precision:int=5):
    """From seconds to Days;Hours:Minutes;Seconds"""
    value = time.time()-lastTime

    valueD = (((value/365)/24)/60)
    Days = int(valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = round(valueS, precision)

    outputString = str(text) + ": " + str(Days) + ";" + str(Hours) + ":" + str(Minutes) + ";" + str(Seconds)
    print(outputString)
    return time.time()


def groupExists(name:str):
    """ check if group exists in blender's memory """
    return name in bpy.data.groups.keys()


def getItemByID(collection:bpy.types.CollectionProperty, id:int):
    """ get UIlist item from collection with given id """
    success = False
    for item in collection:
        if item.id == id:
            success = True
            break
    return item if success else None


def str_to_bool(s:str):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError  # evil ValueError that doesn't tell you what the wrong value was


def get_settings():
    """ get preferences for current addon """
    if not hasattr(get_settings, 'settings'):
        addons = bpy.context.user_preferences.addons
        folderpath = os.path.dirname(os.path.abspath(__file__))
        while folderpath:
            folderpath,foldername = os.path.split(folderpath)
            if foldername in {'common','functions','addons'}: continue
            if foldername in addons: break
        else:
            assert False, 'Could not find non-"lib" folder'
        if not addons[foldername].preferences: return None
        get_settings.settings = addons[foldername].preferences
    return get_settings.settings


# USE EXAMPLE: idfun=(lambda x: x.lower()) so that it ignores case
# https://www.peterbe.com/plog/uniqifiers-benchmark
def uniquify(seq:iter, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


# Not order preserving
def uniquify1(seq:iter):
    keys = {}
    for e in seq:
        keys[e] = 1
    return list(keys.keys())

def uniquify2(seq:list, innerType=list):
    return [innerType(x) for x in set(tuple(x) for x in seq)]


# efficient removal from list if unordered
def remove_item(ls:list, item):
    try:
        i = ls.index(item)
    except ValueError:
        return False
    ls[-1], ls[i] = ls[i], ls[-1]
    ls.pop()
    return True


def tag_redraw_areas(areaTypes:iter=["ALL"]):
    """ run tag_redraw for given area types """
    areaTypes = confirmList(areaTypes)
    for area in bpy.context.screen.areas:
        for areaType in areaTypes:
            if areaType == "ALL" or area.type == areaType:
                area.tag_redraw()


def disableRelationshipLines():
    """ disable relationship lines in VIEW_3D """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].show_relationship_lines = False


def drawBMesh(bm:bmesh, name:str="drawnBMesh"):
    """ create mesh and object from bmesh """
    # note: neither are linked to the scene, yet, so they won't show in the 3d view
    m = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, m)

    scn = bpy.context.scene   # grab a reference to the scene
    scn.objects.link(obj)     # link new object to scene
    scn.objects.active = obj  # make new object active
    obj.select = True         # make new object selected (does not deselect other objects)
    bm.to_mesh(m)             # push bmesh data into m
    return obj


def copyAnimationData(source:Object, target:Object):
    """ copy animation data from one object to another """
    if source.animation_data is None:
        return

    ad = source.animation_data

    properties = [p.identifier for p in ad.bl_rna.properties if not p.is_readonly]

    if target.animation_data is None:
        target.animation_data_create()
    ad2 = target.animation_data

    for prop in properties:
        setattr(ad2, prop, getattr(ad, prop))


class Suppressor(object):
    """ silence function and prevent exceptions """
    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self
    def __exit__(self, type, value, traceback):
        sys.stdout = self.stdout
        if type is not None:
            # Uncomment next line to do normal exception handling
            # raise
            pass
    def write(self, x):
        pass


def applyModifiers(obj:Object, only:list=None, exclude:list=["SMOKE"]):
    """ apply modifiers of types 'only' excluding 'exclude' types for object """
    select(obj, active=True, only=True)
    # apply modifiers
    for mod in obj.modifiers:
        if not (only is None or mod.type in only) or not (exclude is None or mod.type not in exclude) or not mod.show_viewport:
            continue
        try:
            with Suppressor():
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        except:
            mod.show_viewport = False


# code from https://stackoverflow.com/questions/1518522/python-most-common-element-in-a-list
def most_common(L:list):
    """ find the most common item in a list """
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def checkEqual(lst:list):
    """ verifies that all items in list are the same """
    return lst.count(lst[0]) == len(lst)


def vec_mult(v1:Vector, v2:Vector):
    """ componentwise multiplication for vectors """
    return Vector(e1 * e2 for e1, e2 in zip(v1, v2))


def vec_div(v1:Vector, v2:Vector):
    """ componentwise division for vectors """
    return Vector(e1 / e2 for e1, e2 in zip(v1, v2))


def vec_remainder(v1:Vector, v2:Vector):
    """ componentwise remainder for vectors """
    return Vector(e1 % e2 for e1, e2 in zip(v1, v2))


def vec_abs(v1:Vector):
    """ componentwise absolute value for vectors """
    return Vector(abs(e1) for e1 in v1)


def vec_conv(v1, innerType:type=int, outerType:type=Vector):
    """ convert type of items in iterable """
    return outerType([innerType(x) for x in v1])


def vec_round(v1:Vector, precision:int=0):
    """ round items in vector """
    return Vector(round(e1, precision) for e1 in v1)


def mean(lst:list):
    """ mean of a list """
    return sum(lst)/len(lst)


def cap(string:str, max_len:int):
    """ return string whose length does not exceed max_len """
    return string[:max_len] if len(string) > max_len else string


def rreplace(s:str, old:str, new:str, occurrence:int=1):
    """ replace limited occurences of 'old' with 'new' in string starting from end """
    li = s.rsplit(old, occurrence)
    return new.join(li)


def round_nearest(num:float, divisor:int):
    """ round to nearest multiple of 'divisor' """
    rem = num % divisor
    if rem > divisor / 2:
        return round_up(num, divisor)
    else:
        return round_down(num, divisor)


def round_up(num:float, divisor:int):
    """ round up to nearest multiple of 'divisor' """
    return num + divisor - (num % divisor)


def round_down(num:float, divisor:int):
    """ round down to nearest multiple of 'divisor' """
    return num - (num % divisor)


def hash_str(string:str):
    return hashlib.md5(string.encode()).hexdigest()


def confirmList(object):
    """ if single item passed, convert to list """
    if type(object) not in (list, tuple):
        object = [object]
    return object


def confirmIter(object):
    """ if single item passed, convert to list """
    try:
        iter(object)
    except TypeError:
        object = [object]
    return object


def insertKeyframes(objs, keyframeType:str, frame:int, if_needed:bool=False):
    """ insert key frames for given objects to given frames """
    objs = confirmIter(objs)
    options = set(["INSERTKEY_NEEDED"] if if_needed else [])
    for obj in objs:
        inserted = obj.keyframe_insert(data_path=keyframeType, frame=frame, options=options)


def setActiveScn(scn:Scene):
    """ set active scene in all screens """
    for screen in bpy.data.screens:
        screen.scene = scn


def setLayers(layers:iter, scn:Scene=None):
    """ set active layers of scn w/o 'dag ZERO' error """
    assert len(layers) == 20
    scn = scn or bpy.context.scene
    # update scene (prevents dag ZERO errors)
    scn.update()
    # set active layers of scn
    scn.layers = layers


def openLayer(layerNum:int, scn:Scene=None):
    scn = scn or bpy.context.scene
    layerList = [i == layerNum - 1 for i in range(20)]
    scn.layers = layerList
    return layerList


def deselectAll():
    for obj in bpy.context.selected_objects:
        if obj.select:
            obj.select = False


def selectAll(hidden:bool=False):
    for obj in bpy.context.scene.objects:
        if not obj.select and (not obj.hide or hidden):
            obj.select = True


def hide(objs):
    objs = confirmIter(objs)
    for obj in objs:
        obj.hide = True


def unhide(objs):
    objs = confirmIter(objs)
    for obj in objs:
        if obj.hide:
            obj.hide = False


def setActiveObj(obj:Object, scene:Scene=None):
    if obj is None:
        return
    assert type(obj) == Object
    scene = scene or bpy.context.scene
    scene.objects.active = obj


def select(objList, active:bool=False, deselect:bool=False, only:bool=False, scene:Scene=None):
    """ selects objs in list (deselects the rest if 'only') """
    # confirm objList is a list of objects
    objList = confirmIter(objList)
    # deselect all if selection is exclusive
    if only and not deselect:
        deselectAll()
    # select/deselect objects in list
    for obj in objList:
        if obj is not None:
            obj.select = not deselect
    # set active object
    if active:
        setActiveObj(objList[0], scene=scene)


# def deselect(objList, scene:Scene=None):
#     """ selects objs in list and deselects the rest """
#     # confirm objList is a list of objects
#     objList = confirmIter(objList)
#     # select/deselect objects in list
#     for obj in objList:
#         if obj is not None:
#             obj.select = False


def delete(objs):
    """ efficient deletion of objects """
    objs = confirmIter(objs)
    for obj in objs:
        if obj is None:
            continue
        bpy.data.objects.remove(obj, do_unlink=True)


def duplicate(obj:Object, linked:bool=False, link_to_scene:bool=False):
    """ efficient duplication of objects """
    copy = obj.copy()
    if not linked and copy.data:
        copy.data = copy.data.copy()
    copy.hide = False
    if link_to_scene:
        bpy.context.scene.objects.link(copy)
    return copy


def selectVerts(verts):
    verts= confirmIter(verts)
    for v in verts:
        v.select = True


def smoothBMFaces(faces):
    """ set given bmesh faces to smooth """
    faces = confirmIter(faces)
    for f in faces:
        f.smooth = True


def smoothMeshFaces(faces):
    """ set given Mesh faces to smooth """
    faces = confirmIter(faces)
    for f in faces:
        f.use_smooth = True


def checkEqual1(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

def checkEqual2(iterator):
   return len(set(iterator)) <= 1

def checkEqual3(lst):
   return lst[1:] == lst[:-1]
# The difference between the 3 versions are that:
#
# In checkEqual2 the content must be hashable.
# checkEqual1 and checkEqual2 can use any iterators, but checkEqual3 must take a sequence input, typically concrete containers like a list or tuple.
# checkEqual1 stops as soon as a difference is found.
# Since checkEqual1 contains more Python code, it is less efficient when many of the items are equal in the beginning.
# Since checkEqual2 and checkEqual3 always perform O(N) copying operations, they will take longer if most of your input will return False.
# checkEqual2 and checkEqual3 can't be easily changed to adopt to compare a is b instead of a == b.


def deepcopy(object):
    """ efficient way to deepcopy json loadable object """
    jsonObj = json.dumps(object)
    newObj = json.loads(jsonObj)
    return newObj


def changeContext(context, areaType:str):
    """ Changes current context and returns previous area type """
    lastAreaType = context.area.type
    context.area.type = areaType
    return lastAreaType


def getLibraryPath():
    """ returns full path to module directory """
    functionsPath = os.path.dirname(os.path.abspath(__file__))
    libraryPath = functionsPath[:-10]
    if not os.path.exists(libraryPath):
        raise NameError("Did not find addon from path {}".format(libraryPath))
    return libraryPath


# https://github.com/CGCookie/retopoflow
def showErrorMessage(message:str, wrap:int=80):
    if not message or wrap == 0:
        return
    lines = message.splitlines()
    nlines = []
    for line in lines:
        spc = len(line) - len(line.lstrip())
        while len(line) > wrap:
            i = line.rfind(' ', 0, wrap)
            if i == -1:
                nlines += [line[:wrap]]
                line = line[wrap:]
            else:
                nlines += [line[:i]]
                line = line[i+1:]
            if line:
                line = ' '*spc + line
        nlines += [line]
    lines = nlines

    def draw(self,context):
        for line in lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title="Error Message", icon="ERROR")
    return


def handle_exception(log_name:str, report_button_loc:str):
    errormsg = print_exception(log_name)
    # if max number of exceptions occur within threshold of time, abort!
    errorStr = "Something went wrong. Please start an error report with us so we can fix it! ('%(report_button_loc)s')" % locals()
    print('\n'*5)
    print('-'*100)
    print(errorStr)
    print('-'*100)
    print('\n'*5)
    showErrorMessage(errorStr, wrap=240)


def getExceptionMessage():
    exc_type, exc_obj, tb = sys.exc_info()

    errormsg = 'EXCEPTION (%s): %s\n' % (exc_type, exc_obj)
    etb = traceback.extract_tb(tb)
    pfilename = None
    for i, entry in enumerate(reversed(etb)):
        filename, lineno, funcname, line = entry
        if filename != pfilename:
            pfilename = filename
            errormsg += '         %s\n' % (filename)
        errormsg += '%03d %04d:%s() %s\n' % (i, lineno, funcname, line.strip())

    return errormsg


# http://stackoverflow.com/questions/14519177/python-exception-handling-line-number
def print_exception(txtName:str, showError:bool=False, errormsg=None):
    errormsg = getExceptionMessage() if errormsg is None else errormsg

    print(errormsg)

    # create a log file for error writing
    txt = bpy.data.texts.get(txtName)
    if txt is None:
        txt = bpy.data.texts.new(txtName)
    else:
        txt.clear()

    # write error to log text object
    txt.write(errormsg + '\n')

    if showError:
        showErrorMessage(errormsg, wrap=240)

    return errormsg


def updateProgressBars(printStatus:bool, cursorStatus:bool, cur_percent:float, old_percent:float, statusType:str, end:bool=False):
    """ print updated progress bar and update progress cursor """
    if printStatus:
        # print status to terminal
        if cur_percent - old_percent > 0.001 and (cur_percent < 1 or end):
            update_progress(statusType, cur_percent)
            if cursorStatus and ceil(cur_percent*100) != ceil(old_percent*100):
                wm = bpy.context.window_manager
                if cur_percent == 0:
                    wm.progress_begin(0, 100)
                elif cur_percent < 1:
                    wm.progress_update(floor(cur_percent*100))
                else:
                    wm.progress_end()
            old_percent = cur_percent
    return old_percent


def update_progress(job_title:str, progress:float):
    """ print updated progress bar """
    length = 20  # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 1))
    if progress >= 1:
        msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()


def apply_transform(obj:Object):
    """ efficiently apply object transformation """
    # select(obj, active=True, only=True)
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    loc, rot, scale = obj.matrix_world.decompose()
    obj.matrix_world = Matrix.Identity(4)
    m = obj.data
    s_mat_x = Matrix.Scale(scale.x, 4, Vector((1, 0, 0)))
    s_mat_y = Matrix.Scale(scale.y, 4, Vector((0, 1, 0)))
    s_mat_z = Matrix.Scale(scale.z, 4, Vector((0, 0, 1)))
    m.transform(s_mat_x * s_mat_y * s_mat_z)
    m.transform(rot.to_matrix().to_4x4())
    m.transform(Matrix.Translation(loc))


def parent_clear(objs, apply_transform=True):
    """ efficiently clear parent """
    # select(objs, active=True, only=True)
    # bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    objs = confirmIter(objs)
    if apply_transform:
        for obj in objs:
            obj.rotation_mode = "XYZ"
            loc, rot, scale = obj.matrix_world.decompose()
            obj.location = loc
            obj.rotation_euler = rot.to_euler()
            obj.scale = scale
    for obj in objs:
        obj.parent = None


def writeErrorToFile(error_report_path:str, error_log:str, addon_version:str, github_path:str):
    # write error to log text object
    error_report_dir = os.path.dirname(error_report_path)
    if not os.path.exists(error_report_dir):
        os.makedirs(error_report_dir)
    f = open(error_report_path, "w")
    f.write("\nPlease copy the following form and paste it into a new issue at " + github_path)
    f.write("\n\nDon't forget to include a description of your problem! The more information you provide (what you were trying to do, what action directly preceeded the error, etc.), the easier it will be for us to squash the bug.")
    f.write("\n\n### COPY EVERYTHING BELOW THIS LINE ###\n")
    f.write("\nDescription of the Problem:\n")
    f.write("\nBlender Version: " + bversion())
    f.write("\nAddon Version: " + addon_version)
    f.write("\nPlatform Info:")
    f.write("\n   system   = " + platform.system())
    f.write("\n   platform = " + platform.platform())
    f.write("\n   version  = " + platform.version())
    f.write("\n   python   = " + platform.python_version())
    f.write("\nError:")
    try:
        f.write("\n" + error_log)
    except KeyError:
        f.write(" No exception found")


def root_path():
    """ get root system directory """
    return os.path.abspath(os.sep)


def splitpath(path):
    print(os.path.splitpath(path))
    folders = []
    while 1:
        path, folder = os.path.split(path)
        if folder != "":
            folders.append(folder)
        else:
            if path != "": folders.append(path)
            break
    print(folders[::-1])
    return folders[::-1]

def apply_modifiers(obj, settings="PREVIEW"):
    m = obj.to_mesh(bpy.context.scene, True, "PREVIEW")
    obj.modifiers.clear()
    obj.data = m


def safeUnlink(obj, protect=True):
    scn = bpy.context.scene
    try:
        scn.objects.unlink(obj)
    except RuntimeError:
        pass
    obj.protected = protect
    obj.use_fake_user = True


def safeLink(obj, protect=False):
    scn = bpy.context.scene
    scn.objects.link(obj)
    obj.protected = protect
    obj.use_fake_user = False


def getBoundsBF(obj):
    """ brute force method for obtaining object bounding box """
    # initialize min and max
    min = Vector((math.inf, math.inf, math.inf))
    max = Vector((-math.inf, -math.inf, -math.inf))
    # calculate min and max verts
    for v in obj.data.vertices:
        if v.co.x > max.x:
            max.x = v.co.x
        elif v.co.x < min.x:
            min.x = v.co.x
        if v.co.y > max.y:
            max.y = v.co.y
        elif v.co.y < min.y:
            min.y = v.co.y
        if v.co.z > max.z:
            max.z = v.co.z
        elif v.co.z < min.z:
            min.z = v.co.z
    # set up bounding box list of coord lists
    bound_box = [list(min),
                 [min.x, min.y, min.z],
                 [min.x, min.y, max.z],
                 [min.x, max.y, max.z],
                 [min.x, max.y, min.z],
                 [max.x, min.y, min.z],
                 [max.y, min.y, max.z],
                 list(max),
                 [max.x, max.y, min.z]]
    return bound_box


def is_smoke(ob:Object):
    """ check if object is smoke domain """
    if ob is None:
        return False
    for mod in ob.modifiers:
        if mod.type == "SMOKE" and mod.domain_settings and mod.show_viewport:
            return True
    return False


def is_adaptive(ob):
    """ check if smoke domain object uses adaptive domain """
    if ob is None:
        return False
    for mod in ob.modifiers:
        if mod.type == "SMOKE" and mod.domain_settings and mod.domain_settings.use_adaptive_domain:
            return True
    return False


def bounds(obj, local:bool=False, use_adaptive_domain:bool=True):
    """
    returns object details with the following subattribute Vectors:

    .max : maximum value of object
    .min : minimum value of object
    .mid : midpoint value of object
    .dist: distance min to max

    """

    local_coords = getBoundsBF(obj) if is_smoke(obj) and is_adaptive(obj) and not use_adaptive_domain else obj.bound_box[:]
    om = obj.matrix_world

    if not local:
        worldify = lambda p: om * Vector(p[:])
        coords = [worldify(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])
    getMax = lambda i: max([co[i] for co in coords])
    getMin = lambda i: min([co[i] for co in coords])

    info = lambda: None
    info.max = Vector((getMax(0), getMax(1), getMax(2)))
    info.min = Vector((getMin(0), getMin(1), getMin(2)))
    info.mid = (info.min + info.max) / 2
    info.dist = info.max - info.min

    return info


def isUnique(lst:list):
    """ ensure all items in list are unique """
    return np.unique(lst).size == len(lst)


def getSaturationMatrix(s:float):
    """ returns saturation matrix from saturation value """
    sr = (1 - s) * 0.3086  # or 0.2125
    sg = (1 - s) * 0.6094  # or 0.7154
    sb = (1 - s) * 0.0820  # or 0.0721
    return Matrix(((sr + s, sr, sr), (sg, sg + s, sg), (sb, sb, sb + s)))


def gammaCorrect(rgba:list, val:float):
    """ camma correct color by value """
    r, g, b, a = rgba
    r = math.pow(r, val)
    g = math.pow(g, val)
    b = math.pow(b, val)
    return [r, g, b, a]


def setObjOrigin(obj, loc):
    """ set object origin """
    l, r, s = obj.matrix_world.decompose()
    l_mat = Matrix.Translation(l)
    r_mat = r.to_matrix().to_4x4()
    s_mat_x = Matrix.Scale(s.x, 4, Vector((1, 0, 0)))
    s_mat_y = Matrix.Scale(s.y, 4, Vector((0, 1, 0)))
    s_mat_z = Matrix.Scale(s.z, 4, Vector((0, 0, 1)))
    s_mat = s_mat_x * s_mat_y * s_mat_z
    m = obj.data
    m.transform(Matrix.Translation((obj.location-loc) * l_mat * r_mat * s_mat.inverted()))
    obj.location = loc


def transformToWorld(vec, mat, junk_bme=None):
    """ transfrom vector to world space from 'mat' matrix local space """
    # decompose matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    scale = mat.to_scale()[0]
    # apply rotation
    if rot != Euler((0, 0, 0), "XYZ"):
        junk_bme = bmesh.new() if junk_bme is None else junk_bme
        v1 = junk_bme.verts.new(vec)
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.x, 3, 'X'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.y, 3, 'Y'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.z, 3, 'Z'))
        vec = v1.co
    # apply scale
    vec = vec * scale
    # apply translation
    vec += loc
    return vec


def transformToLocal(vec, mat, junk_bme=None):
    """ transfrom vector to local space of 'mat' matrix """
    # decompose matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    scale = mat.to_scale()[0]
    # apply scale
    vec = vec / scale
    # apply rotation
    if rot != Euler((0, 0, 0), "XYZ"):
        junk_bme = bmesh.new() if junk_bme is None else junk_bme
        v1 = junk_bme.verts.new(vec)
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.z, 3, 'Z'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.y, 3, 'Y'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.x, 3, 'X'))
        vec = v1.co
    return vec
