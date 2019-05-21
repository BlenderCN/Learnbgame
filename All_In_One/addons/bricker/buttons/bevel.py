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

# system imports
import time
import bmesh
import os
import math

# Blender imports
import bpy
from bpy.types import Object
from mathutils import Matrix, Vector
props = bpy.props

# Addon imports
from ..functions import *


class BRICKER_OT_bevel(bpy.types.Operator):
    """Bevel brick edges and corners for added realism"""
    bl_idname = "bricker.bevel"
    bl_label = "Bevel Bricks"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        try:
            scn, cm, n = getActiveContextInfo()
        except IndexError:
            return False
        if cm.modelCreated or cm.animated:
            return True
        return False

    def execute(self, context):
        try:
            cm = getActiveContextInfo()[1]
            # set bevel action to add or remove
            try:
                testBrick = getBricks()[0]
                testBrick.modifiers[testBrick.name + '_bvl']
                action = "REMOVE" if cm.bevelAdded else "ADD"
            except:
                action = "ADD"
            # get bricks to bevel
            bricks = getBricks()
            # create or remove bevel
            BRICKER_OT_bevel.runBevelAction(bricks, cm, action, setBevel=True)
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    #############################################
    # class methods

    @staticmethod
    def runBevelAction(bricks, cm, action="ADD", setBevel=False):
        """ chooses whether to add or remove bevel """
        if action == "REMOVE":
            BRICKER_OT_bevel.removeBevelMods(bricks)
            cm.bevelAdded = False
        elif action == "ADD":
            BRICKER_OT_bevel.createBevelMods(cm, bricks)
            cm.bevelAdded = True

    @classmethod
    def removeBevelMods(self, objs):
        """ removes bevel modifier 'obj.name + "_bvl"' for objects in 'objs' """
        objs = confirmIter(objs)
        for obj in objs:
            bvlMod = obj.modifiers.get(obj.name + "_bvl")
            if bvlMod is None:
                continue
            obj.modifiers.remove(bvlMod)

    @classmethod
    def createBevelMods(self, cm, objs):
        """ runs 'createBevelMod' on objects in 'objs' """
        # get objs to bevel
        objs = confirmIter(objs)
        # initialize vars
        segments = cm.bevelSegments
        profile = cm.bevelProfile
        show_render = cm.bevelShowRender
        show_viewport = cm.bevelShowViewport
        show_in_editmode = cm.bevelShowEditmode
        # create bevel modifiers for each object
        for obj in objs:
            self.createBevelMod(obj=obj, width=cm.bevelWidth * cm.brickHeight, segments=segments, profile=profile, limitMethod="VGROUP", vertexGroup=obj.name + "_bvl", offsetType='WIDTH', angleLimit=1.55334, show_render=show_render, show_viewport=show_viewport, show_in_editmode=show_in_editmode)

    @classmethod
    def createBevelMod(self, obj:Object, width:float=1, segments:int=1, profile:float=0.5, onlyVerts:bool=False, limitMethod:str='NONE', angleLimit:float=0.523599, vertexGroup:str=None, offsetType:str='OFFSET', show_render:bool=True, show_viewport:bool=True, show_in_editmode:bool=True):
        """ create bevel modifier for 'obj' with given parameters """
        dMod = obj.modifiers.get(obj.name + '_bvl')
        if not dMod:
            dMod = obj.modifiers.new(obj.name + '_bvl', 'BEVEL')
            eMod = obj.modifiers.get('Edge Split')
            if eMod:
                obj.modifiers.remove(eMod)
                addEdgeSplitMod(obj)
        # only update values if necessary (prevents multiple updates to mesh)
        if dMod.use_only_vertices != onlyVerts:
            dMod.use_only_vertices = onlyVerts
        if dMod.width != width:
            dMod.width = width
        if dMod.segments != segments:
            dMod.segments = segments
        if dMod.profile != profile:
            dMod.profile = profile
        if dMod.limit_method != limitMethod:
            dMod.limit_method = limitMethod
        if vertexGroup and dMod.vertex_group != vertexGroup:
            try:
                dMod.vertex_group = vertexGroup
            except Exception as e:
                print("[Bricker]", e)
                dMod.limit_method = "ANGLE"
        if dMod.angle_limit != angleLimit:
            dMod.angle_limit = angleLimit
        if dMod.offset_type != offsetType:
            dMod.offset_type = offsetType
        # update visibility of bevel modifier
        if dMod.show_render != show_render:
            dMod.show_render = show_render
        if dMod.show_viewport != show_viewport:
            dMod.show_viewport = show_viewport
        if dMod.show_in_editmode != show_in_editmode:
            dMod.show_in_editmode = show_in_editmode


    #############################################
