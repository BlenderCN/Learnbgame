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
import os
import numpy as np
from math import *

# Blender imports
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
from bpy.types import Object, Scene#, CollectionProperty
try:
    from bpy.types import ViewLayer
except ImportError:
    ViewLayer = None

# module imports
from .python_utils import confirmIter, confirmList
from .wrappers import blender_version_wrapper


#################### PREFERENCES ####################


@blender_version_wrapper("<=", "2.79")
def get_preferences(ctx=None):
    return (ctx if ctx else bpy.context).user_preferences
@blender_version_wrapper(">=", "2.80")
def get_preferences(ctx=None):
    return (ctx if ctx else bpy.context).preferences


def get_addon_preferences():
    """ get preferences for current addon """
    if not hasattr(get_addon_preferences, 'prefs'):
        folderpath, foldername = os.path.split(get_addon_directory())
        if not addons[foldername].preferences: return None
        get_addon_preferences.prefs = addons[foldername].preferences
    return get_addon_preferences.prefs


#################### OBJECTS ####################


def delete(objs, remove_meshes:bool=False):
    """ efficient deletion of objects """
    objs = confirmIter(objs)
    for obj in objs:
        if obj is None:
            continue
        if remove_meshes: m = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if remove_meshes and m is not None: bpy.data.meshes.remove(m)


def duplicate(obj:Object, linked:bool=False, link_to_scene:bool=False):
    """ efficient duplication of objects """
    copy = obj.copy()
    if not linked and copy.data:
        copy.data = copy.data.copy()
    unhide(copy, render=False)
    if link_to_scene:
        link_object(copy)
    return copy


@blender_version_wrapper('<=','2.79')
def setActiveObj(obj:Object, scene:Scene=None):
    if obj is None:
        return
    assert type(obj) == Object
    scene = scene or bpy.context.scene
    scene.objects.active = obj
@blender_version_wrapper('>=','2.80')
def setActiveObj(obj:Object, view_layer:ViewLayer=None):
    if obj is None:
        return
    assert type(obj) == Object
    view_layer = view_layer or bpy.context.view_layer
    view_layer.objects.active = obj


@blender_version_wrapper('<=','2.79')
def select(objList, active:bool=False, only:bool=False):
    """ selects objs in list (deselects the rest if 'only') """
    # confirm objList is a list of objects
    objList = confirmIter(objList)
    # deselect all if selection is exclusive
    if only: deselectAll()
    # select objects in list
    for obj in objList:
        if obj is not None and not obj.select:
            obj.select = True
    # set active object
    if active: setActiveObj(objList[0])
@blender_version_wrapper('>=','2.80')
def select(objList, active:bool=False, only:bool=False):
    """ selects objs in list (deselects the rest if 'only') """
    # confirm objList is a list of objects
    objList = confirmIter(objList)
    # deselect all if selection is exclusive
    if only: deselectAll()
    # select objects in list
    for obj in objList:
        if obj is not None and not obj.select_get():
            obj.select_set(True)
    # set active object
    if active: setActiveObj(objList[0])


def selectAll():
    """ selects all objs in scene """
    select(bpy.context.scene.objects)


def selectVerts(vertList, only:bool=False):
    """ selects verts in list and deselects the rest """
    # confirm vertList is a list of vertices
    vertList = confirmList(vertList)
    # deselect all if selection is exclusive
    if only: deselectAll()
    # select vertices in list
    for v in vertList:
        if v is not None and not v.select:
            v.select = True


@blender_version_wrapper('<=','2.79')
def deselect(objList):
    """ deselects objs in list """
    # confirm objList is a list of objects
    objList = confirmList(objList)
    # select/deselect objects in list
    for obj in objList:
        if obj is not None and obj.select:
            obj.select = False
@blender_version_wrapper('>=','2.80')
def deselect(objList):
    """ deselects objs in list """
    # confirm objList is a list of objects
    objList = confirmList(objList)
    # select/deselect objects in list
    for obj in objList:
        if obj is not None and obj.select_get():
            obj.select_set(False)


@blender_version_wrapper('<=','2.79')
def deselectAll():
    """ deselects all objs in scene """
    for obj in bpy.context.selected_objects:
        if obj.select:
            obj.select = False
@blender_version_wrapper('>=','2.80')
def deselectAll():
    """ deselects all objs in scene """
    try:
        selected_objects = bpy.context.selected_objects
    except AttributeError:
        selected_objects = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]
    deselect(selected_objects)


@blender_version_wrapper('<=','2.79')
def hide(obj:Object, viewport:bool=True, render:bool=True):
    if obj.hide and viewport:
        obj.hide = True
    if obj.hide_render and render:
        obj.hide_viewport = True
@blender_version_wrapper('>=','2.80')
def hide(obj:Object, viewport:bool=True, render:bool=True):
    if obj.hide_viewport and viewport:
        obj.hide_viewport = True
    if obj.hide_render and render:
        obj.hide_viewport = True


@blender_version_wrapper('<=','2.79')
def unhide(obj:Object, viewport:bool=True, render:bool=True):
    if obj.hide and viewport:
        obj.hide = False
    if obj.hide_render and render:
        obj.hide_render= False
@blender_version_wrapper('>=','2.80')
def unhide(obj:Object, viewport:bool=True, render:bool=True):
    if obj.hide_viewport and viewport:
        obj.hide_viewport = False
    if obj.hide_render and render:
        obj.hide_render= False


@blender_version_wrapper('>=','2.80')
def isObjVisibleInViewport(obj:Object):
    if obj is None: return False
    objVisible = not obj.hide_viewport
    if objVisible:
        for cn in obj.users_collection:
            if cn.hide_viewport:
                objVisible = False
                break
    return objVisible


@blender_version_wrapper('<=','2.79')
def link_object(o:Object):
    bpy.context.scene.objects.link(o)
@blender_version_wrapper('>=','2.80')
def link_object(o:Object):
    bpy.context.scene.collection.objects.link(o)


@blender_version_wrapper('<=','2.79')
def unlink_object(o:Object):
    bpy.context.scene.objects.unlink(o)
@blender_version_wrapper('>=','2.80')
def unlink_object(o:Object):
    for coll in o.users_collection:
        coll.objects.unlink(o)


@blender_version_wrapper('<=','2.79')
def safeLink(obj:Object, protect:bool=False):
    scn = bpy.context.scene
    link_object(obj)
    obj.protected = protect
    obj.use_fake_user = False
@blender_version_wrapper('>=','2.80')
def safeLink(obj:Object, protect:bool=False, collections=None):
    collections = collections or [scn.collection]
    for coll in collections:
        try:
            coll.objects.link(obj)
        except RuntimeError:
            continue
    obj.protected = protect
    obj.use_fake_user = False


def safeUnlink(obj:Object, protect:bool=True):
    scn = bpy.context.scene
    try:
        unlink_object(obj)
    except RuntimeError:
        pass
    obj.protected = protect
    obj.use_fake_user = True


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


def insertKeyframes(objs, keyframeType:str, frame:int, if_needed:bool=False):
    """ insert key frames for given objects to given frames """
    objs = confirmIter(objs)
    options = set(["INSERTKEY_NEEDED"] if if_needed else [])
    for obj in objs:
        inserted = obj.keyframe_insert(data_path=keyframeType, frame=frame, options=options)


def apply_modifiers(obj:Object, settings:str="PREVIEW"):
    """ apply modifiers to object """
    m = obj.to_mesh(bpy.context.scene, True, "PREVIEW")
    obj.modifiers.clear()
    obj.data = m


def is_smoke(ob:Object):
    """ check if object is smoke domain """
    if ob is None:
        return False
    for mod in ob.modifiers:
        if mod.type == "SMOKE" and mod.domain_settings and mod.show_viewport:
            return True
    return False


def is_adaptive(ob:Object):
    """ check if smoke domain object uses adaptive domain """
    if ob is None:
        return False
    for mod in ob.modifiers:
        if mod.type == "SMOKE" and mod.domain_settings and mod.domain_settings.use_adaptive_domain:
            return True
    return False


#################### VIEWPORT ####################


def tag_redraw_areas(areaTypes:iter=["ALL"]):
    """ run tag_redraw for given area types """
    areaTypes = confirmList(areaTypes)
    for area in bpy.context.screen.areas:
        for areaType in areaTypes:
            if areaType == "ALL" or area.type == areaType:
                area.tag_redraw()


def tag_redraw_viewport_in_all_screens():
    """redraw the 3D viewport in all screens (bypasses bpy.context.screen)"""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


@blender_version_wrapper("<=", "2.79")
def disableRelationshipLines():
    """ disable relationship lines in VIEW_3D """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].show_relationship_lines = False
@blender_version_wrapper(">=", "2.80")
def disableRelationshipLines():
    """ disable relationship lines in VIEW_3D """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].overlay.show_relationship_lines = False


def setActiveScn(scn:Scene):
    """ set active scene in all screens """
    for screen in bpy.data.screens:
        screen.scene = scn


def changeContext(context, areaType:str):
    """ Changes current context and returns previous area type """
    lastAreaType = context.area.type
    context.area.type = areaType
    return lastAreaType


@blender_version_wrapper('<=','2.79')
def setLayers(layers:iter, scn:Scene=None):
    """ set active layers of scn w/o 'dag ZERO' error """
    assert len(layers) == 20
    scn = scn or bpy.context.scene
    # update scene (prevents dag ZERO errors)
    scn.update()
    # set active layers of scn
    scn.layers = layers


@blender_version_wrapper('<=','2.79')
def openLayer(layerNum:int, scn:Scene=None):
    scn = scn or bpy.context.scene
    layerList = [i == layerNum - 1 for i in range(20)]
    scn.layers = layerList
    return layerList


#################### MESHES ####################


def drawBMesh(bm:bmesh, name:str="drawnBMesh"):
    """ create mesh and object from bmesh """
    # note: neither are linked to the scene, yet, so they won't show in the 3d view
    m = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, m)

    link_object(obj)          # link new object to scene
    select(obj, active=True)  # select new object and make active (does not deselect other objects)
    bm.to_mesh(m)             # push bmesh data into m
    return obj


def smoothBMFaces(faces:iter):
    """ set given bmesh faces to smooth """
    faces = confirmIter(faces)
    for f in faces:
        f.smooth = True


def smoothMeshFaces(faces:iter):
    """ set given Mesh faces to smooth """
    faces = confirmIter(faces)
    for f in faces:
        f.use_smooth = True


#################### OTHER ####################


def getItemByID(collection:bpy.types.CollectionProperty, id:int):
    """ get UIlist item from collection with given id """
    success = False
    for item in collection:
        if item.id == id:
            success = True
            break
    return item if success else None
