# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; eimcp.r version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See mcp.
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
from bpy.props import EnumProperty, StringProperty

from . import mcp
from . import utils
from .utils import MocapError

#
#   Select or delete action
#   Delete button really deletes action. Handle with care.
#
#   listAllActions(context):
#   findActionNumber(name):
#   class VIEW3D_OT_McpUpdateActionListButton(bpy.types.Operator):
#

def listAllActions(context):
    scn = context.scene
    try:
        doFilter = scn.McpFilterActions
        filter = context.object.name
        if len(filter) > 4:
            filter = filter[0:4]
            flen = 4
        else:
            flen = len(filter)
    except:
        doFilter = False
        
    mcp.actions = []     
    for act in bpy.data.actions:
        name = act.name
        if (not doFilter) or (name[0:flen] == filter):
            mcp.actions.append((name, name, name))
    bpy.types.Scene.McpActions = EnumProperty(
        items = mcp.actions,
        name = "Actions")  
    bpy.types.Scene.McpFirstAction = EnumProperty(
        items = mcp.actions,
        name = "First action")  
    bpy.types.Scene.McpSecondAction = EnumProperty(
        items = mcp.actions,
        name = "Second action")  
    print("Actions declared")
    return


def findActionNumber(name):
    for n,enum in enumerate(mcp.actions):
        (name1, name2, name3) = enum        
        if name == name1:
            return n
    raise MocapError("Unrecognized action %s" % name)


class VIEW3D_OT_McpUpdateActionListButton(bpy.types.Operator):
    bl_idname = "mcp.update_action_list"
    bl_label = "Update Action List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        listAllActions(context)
        return{'FINISHED'}    

#
#   deleteAction(context):
#   class VIEW3D_OT_McpDeleteButton(bpy.types.Operator):
#

def deleteAction(context):
    listAllActions(context)
    scn = context.scene
    try:
        act = bpy.data.actions[scn.McpActions]
    except KeyError:
        act = None
    if not act:     
        raise MocapError("Did not find action %s" % scn.McpActions)
    print('Delete action', act)    
    act.use_fake_user = False
    if act.users == 0:
        print("Deleting", act)
        n = findActionNumber(act.name)
        mcp.actions.pop(n)
        bpy.data.actions.remove(act)
        print('Action', act, 'deleted')
        listAllActions(context)
        #del act
    else:
        raise MocapError("Cannot delete. Action %s has %d users." % (act.name, act.users))


class VIEW3D_OT_McpDeleteButton(bpy.types.Operator):
    bl_idname = "mcp.delete"
    bl_label = "Delete Action"
    bl_options = {'UNDO'}
    answer = StringProperty(default="")

    #@classmethod
    #def poll(cls, context):
    #    return context.scene.McpReallyDelete

    def execute(self, context):
        mcp.utilityString = "?"
        if self.answer == "":
            mcp.utilityString = "Really delete action?"
            mcp.utilityConfirm = self.bl_idname
        elif self.answer == "yes":
            mcp.utilityConfirm = ""
            try:
                deleteAction(context)
            except MocapError:
                bpy.ops.mcp.error('INVOKE_DEFAULT')
        else:
            mcp.utilityConfirm = ""
        return{'FINISHED'}    

#
#   deleteHash():
#   class VIEW3D_OT_McpDeleteHashButton(bpy.types.Operator):
#

def deleteHash():
    for act in bpy.data.actions:
        if act.name[0] == '#':
            utils.deleteAction(act)
    return 

    
class VIEW3D_OT_McpDeleteHashButton(bpy.types.Operator):
    bl_idname = "mcp.delete_hash"
    bl_label = "Delete Hash Actions"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            deleteHash()
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    

#
#   setCurrentAction(context, prop):
#   class VIEW3D_OT_McpSetCurrentActionButton(bpy.types.Operator):
#

def setCurrentAction(context, prop):
    listAllActions(context)
    name = getattr(context.scene, prop)
    act = getAction(name)
    context.object.animation_data.action = act
    print("Action set to %s" % act)
    return


def getAction(name):
    try:
        return bpy.data.actions[name]
    except KeyError:
        pass
    raise MocapError("Did not find action %s" % name)
        
    
class VIEW3D_OT_McpSetCurrentActionButton(bpy.types.Operator):
    bl_idname = "mcp.set_current_action"
    bl_label = "Set Current Action"
    bl_options = {'UNDO'}
    prop = StringProperty()

    def execute(self, context):
        try:
            setCurrentAction(context, self.prop)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}    

