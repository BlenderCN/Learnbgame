#
# Copyright(C) 2017-2018 Samuel Villarreal
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import os
import bpy
from enum import Enum
from bpy.props import FloatVectorProperty, StringProperty, PointerProperty

#-----------------------------------------------------------------------------
#
# Texture Animation Defs
#
#-----------------------------------------------------------------------------
 
animState = [
    ("STATE_STOP", "Off", "", 0),
    ("STATE_GO", "On", "", 1)
    ]
    
bpy.types.Object.animState              = bpy.props.EnumProperty(items = animState, name = "Anim State", default = "STATE_GO")
bpy.types.Object.animationCommands      = bpy.props.StringProperty(name = "Animation Command Object")
bpy.types.Object.animationDefs          = bpy.props.StringProperty(name = "Animation Definition Object")
bpy.types.Object.animationTexture       = bpy.props.StringProperty(name = "Animated Texture")
bpy.types.Object.animTextureWidth       = bpy.props.FloatProperty(name = "Anim Texture Width", default = 256.0)
bpy.types.Object.animTextureHeight      = bpy.props.FloatProperty(name = "Anim Texture Height", default = 256.0)

# -----------------------------------------------------------------------------
# 
class AnimDefPropertyGroup(bpy.types.PropertyGroup):
    animDefStartX   = bpy.props.FloatProperty(name = "UV Start X")
    animDefStartY   = bpy.props.FloatProperty(name = "UV Start Y")
    animDefEndX     = bpy.props.FloatProperty(name = "UV End X")
    animDefEndY     = bpy.props.FloatProperty(name = "UV End Y")

bpy.utils.register_class(AnimDefPropertyGroup)
 
# -----------------------------------------------------------------------------
# 
class UL_AnimDefProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        row.prop(item, "animDefStartX")
        row = layout.row()
        row.prop(item, "animDefStartY")
        row = layout.row()
        row.prop(item, "animDefEndX")
        row = layout.row()
        row.prop(item, "animDefEndY")
    
# -----------------------------------------------------------------------------
# 
class AnimDefPropertyList(bpy.types.PropertyGroup):
    defs = bpy.props.CollectionProperty(type=AnimDefPropertyGroup, name="Anim Defs")
    index = bpy.props.IntProperty(name = "Active Index", default = -1)
    
bpy.utils.register_class(AnimDefPropertyList)
        
# -----------------------------------------------------------------------------
#
class AddAnimDefOperator(bpy.types.Operator):
    bl_idname = "object.anim_def_add"
    bl_label = "Add Anim Def Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.animDefs.defs.add()
        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveAnimDefOperator(bpy.types.Operator):
    bl_idname = "object.anim_def_remove"
    bl_label = "Remove Anim Def Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            ad = obj.animDefs
            if ad.index >= 0 and ad.index < len(ad.defs):
                ad.defs.remove(ad.index)
                ad.index -= 1
        return {'FINISHED'}
        
#-----------------------------------------------------------------------------
#
# Texture Animation Commands
#
#-----------------------------------------------------------------------------

animCommandsNames = [
    ("CMD_BASE", "Nothing", "", 32768),
    ("CMD_DURATION", "Duration", "", 32769),
    ("CMD_NEXTDURATION", "Next Duration", "", 32770),
    ("CMD_LOOPINIT", "Loop Init", "", 32771),
    ("CMD_LOOPEND", "Loop End", "", 32772),
    ("CMD_FRAME", "Frame", "", 32773),
    ("CMD_END", "End", "", 65535)
    ]
     
# -----------------------------------------------------------------------------
# 
class ForsakenAnimCommandPropertyGroup(bpy.types.PropertyGroup):
    command     = bpy.props.EnumProperty(items = animCommandsNames, name = "Command")
    param       = bpy.props.StringProperty(name="Param")

bpy.utils.register_class(ForsakenAnimCommandPropertyGroup)
 
# -----------------------------------------------------------------------------
# 
class UL_ForsakenAnimCommandProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        row.prop(item, "command")
        row = layout.row()
        row.prop(item, "param")
         
# -----------------------------------------------------------------------------
# 
class ForsakenAnimCommandList(bpy.types.PropertyGroup):
    commands = bpy.props.CollectionProperty(type = ForsakenAnimCommandPropertyGroup, name="Anim Commands")
    index = bpy.props.IntProperty(name = "Active Index", default = -1)

bpy.utils.register_class(ForsakenAnimCommandList)

# -----------------------------------------------------------------------------
#
class AddForsakenAnimCommandOperator(bpy.types.Operator):
    bl_idname = "object.forsaken_anim_cmds_add"
    bl_label = "Add Anim Def Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.forsakenAnimCmds.commands.add()
        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveForsakenAnimCommandOperator(bpy.types.Operator):
    bl_idname = "object.forsaken_anim_cmds_remove"
    bl_label = "Remove Anim Def Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            ad = obj.forsakenAnimCmds
            if ad.index >= 0 and ad.index < len(ad.commands):
                ad.commands.remove(ad.index)
                ad.index -= 1
        return {'FINISHED'}

# -----------------------------------------------------------------------------
#
def register():
    bpy.utils.unregister_class(UL_ForsakenAnimCommandProperties)
    bpy.utils.unregister_class(UL_AnimDefProperties)
    bpy.utils.unregister_class(AddAnimDefOperator)
    bpy.utils.unregister_class(RemoveAnimDefOperator)
    bpy.utils.unregister_class(AddForsakenAnimCommandOperator)
    bpy.utils.unregister_class(RemoveForsakenAnimCommandOperator)

    bpy.utils.register_class(UL_ForsakenAnimCommandProperties)
    bpy.utils.register_class(UL_AnimDefProperties)
    bpy.utils.register_class(AddAnimDefOperator)
    bpy.utils.register_class(RemoveAnimDefOperator)
    bpy.utils.register_class(AddForsakenAnimCommandOperator)
    bpy.utils.register_class(RemoveForsakenAnimCommandOperator)
    
    bpy.types.Object.animDefs           = bpy.props.PointerProperty(type=AnimDefPropertyList)
    bpy.types.Object.forsakenAnimCmds   = bpy.props.PointerProperty(type=ForsakenAnimCommandList)
    
# -----------------------------------------------------------------------------
#
def unregister():
    bpy.utils.unregister_class(UL_ForsakenAnimCommandProperties)
    bpy.utils.unregister_class(UL_AnimDefProperties)
    bpy.utils.unregister_class(AddAnimDefOperator)
    bpy.utils.unregister_class(RemoveAnimDefOperator)
    bpy.utils.unregister_class(AddForsakenAnimCommandOperator)
    bpy.utils.unregister_class(RemoveForsakenAnimCommandOperator)
    