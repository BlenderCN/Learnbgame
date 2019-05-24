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

import bpy
from enum import Enum
from bpy.props import FloatVectorProperty, StringProperty, PointerProperty

# -----------------------------------------------------------------------------
#
bl_info = {
    "name": "Forsaken tools",
    "author": "Samuel 'Kaiser' Villarreal",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Import-Export Forsaken model data, Import Forsaken model data",
    "warning": "",
    "category": "Learnbgame",
}
  
# -----------------------------------------------------------------------------
#
if "bpy" in locals():
    import importlib
    if "forsaken_object_panel" in locals():
        importlib.reload(forsaken_object_panel)
    if "forsaken_utils" in locals():
        importlib.reload(forsaken_utils)
    if "export_forsaken" in locals():
        importlib.reload(export_forsaken)
    if "import_forsaken_mx" in locals():
        importlib.reload(import_forsaken_mx)
    if "export_forsaken_mx" in locals():
        importlib.reload(export_forsaken_mx)
    if "import_forsaken_cob" in locals():
        importlib.reload(import_forsaken_cob)
    if "export_forsaken_cob" in locals():
        importlib.reload(export_forsaken_cob)
    if "import_forsaken_level" in locals():
        importlib.reload(import_forsaken_level)
    if "forsaken_panel_operators" in locals():
        importlib.reload(forsaken_panel_operators)
    if "forsaken_import_export" in locals():
        importlib.reload(forsaken_import_export)
    if "forsaken_texture_anims" in locals():
        importlib.reload(forsaken_texture_anims)
        
import os
import bpy
from bpy.props import (
        CollectionProperty,
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        )
        
#-----------------------------------------------------------------------------
#
# Common Enums
#
#-----------------------------------------------------------------------------

actorTypes = [
    ("PICKUP", "Pickup", "", 1),
    ("RTLIGHT", "Real Time Light", "", 2),
    ("BGOBJECT", "BG Object", "", 3),
    ("TRIGGERVAR", "Trigger Variable", "", 4),
    ("TRIGGER", "Trigger", "", 5),
    ("TRIGGERCONDITION", "Trigger Condition", "", 6),
    ("ZONEAREA", "Zone Area", "", 7),
    ("PATHNODE", "Path Node", "", 8),
    ("ENEMY", "Enemy", "", 9),
    ("PLAYERSTART", "Player Start", "", 10),
    ("LIGHT", "Light", "", 11),
    ("RESTARTPOINT", "Restart Point", "", 12),
    ("WATER", "Water", "", 13),
    ("SPOTFX", "Spot Fx", "", 14),
    ("EXTFORCE", "External Force", "", 15),
    ("CAMERA", "Camera", "", 16),
    ("ANIMCOMMAND", "Animation Command", "", 17),
    ("ANIMDEF", "Animation Definition", "", 18),
    ("ANIMINST", "Animation Instance", "", 19)
    ]

genTypes = [
    ("GT_INITIALIZED", "Initialized", "", 0),
    ("GT_TIME", "Timed", "", 1),
    ("GT_TRIGGER", "Triggered", "", 2),
    ]

regenTypes = [
    ("REGENTYPE_RANDOM", "Random", "", 0),
    ("REGENTYPE_CONST", "Constant", "", 1),
    ("REGENTYPE_ONCEONLY", "Once Only", "", 2),
    ]
    
waterTypes = [
    ("WATERSTATE_NOWATER", "No Water", "", 0),
    ("WATERSTATE_SOMEWATER", "Some Water", "", 1),
    ("WATERSTATE_ALLWATER", "All Water", "", 2),
    ]
    
#-----------------------------------------------------------------------------
#
# Common Actor Properties
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
bpy.types.Object.actor                  = bpy.props.BoolProperty(name = "Is Actor")
bpy.types.Object.actorType              = bpy.props.EnumProperty(items = actorTypes, name = "ActorType")
bpy.types.Object.levelGroup             = bpy.props.StringProperty(name = "Group Name")
bpy.types.Object.groupWaterType         = bpy.props.EnumProperty(items = waterTypes, name = "WATERSTATE_NOWATER")
bpy.types.Object.groupCausticColor      = bpy.props.FloatVectorProperty(name = "Caustic Color", subtype='COLOR', default=[1.0,1.0,1.0])
bpy.types.Object.groupSoundDistScale    = bpy.props.FloatProperty(name = "Sound Distance Scale", default = 1.0)

#-----------------------------------------------------------------------------
#
# Trigger Mods
#
#-----------------------------------------------------------------------------
 
# -----------------------------------------------------------------------------
# 
triggerModOp = [
    ("SET", "Set", "", 0),
    ("RESET", "Reset", "", 1),
    ("INCREMENT", "Increment", "", 2),
    ("DECREMENT", "Decrement", "", 3),
    ("OR", "Or", "", 4),
    ("AND", "And", "", 5),
    ("XOR", "Xor", "", 6),
    ("MULTIPLY", "Mult", "", 7),
    ("DIVIDE", "Div", "", 8),
    ("RANDOM", "Random", "", 9),
    ("SETFLAG", "SetFlag", "", 10),
    ("CLEARFLAG", "ClearFlag", "", 11),
    ]
     
# -----------------------------------------------------------------------------
# 
class TriggerModPropertyGroup(bpy.types.PropertyGroup):
    variable    = bpy.props.StringProperty(name="Variable")
    operand     = bpy.props.EnumProperty(items = triggerModOp, name = "Operand")
    value       = bpy.props.IntProperty(name = "Value")
    delay       = bpy.props.FloatProperty(name = "Delay")

bpy.utils.register_class(TriggerModPropertyGroup)
     
# -----------------------------------------------------------------------------
# 
class GeneratePropertyGroup(bpy.types.PropertyGroup):
    genType         = bpy.props.EnumProperty(items = genTypes, name = "Gen Type")
    genDelay        = bpy.props.FloatProperty(name = "Gen Delay")
    
bpy.utils.register_class(GeneratePropertyGroup)
 
# -----------------------------------------------------------------------------
# 
class UL_TriggerModProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        row.prop(item, "variable")
        row = layout.row()
        row.prop(item, "operand")
        row = layout.row()
        row.prop(item, "value")
        row = layout.row()
        row.prop(item, "delay")
         
# -----------------------------------------------------------------------------
# 
class TriggerModList(bpy.types.PropertyGroup):
    trigger_mods = bpy.props.CollectionProperty(type = TriggerModPropertyGroup)
    index = bpy.props.IntProperty(name = "Active Index", default = -1)

#-----------------------------------------------------------------------------
#
# Path Nodes
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
bpy.types.Object.pathRadius             = bpy.props.FloatProperty(name = "Radius", default = 70.0)
bpy.types.Object.pathFlagDecision       = bpy.props.BoolProperty(name = "Decision", default = True)
bpy.types.Object.pathFlagDropMines      = bpy.props.BoolProperty(name = "Drop Mines", default = False)
bpy.types.Object.pathFlagDisabled       = bpy.props.BoolProperty(name = "Disabled", default = False)
bpy.types.Object.pathFlagSnapToBGObj    = bpy.props.BoolProperty(name = "Snap To BG Objects", default = False)
bpy.types.Object.pathNetwork1           = bpy.props.BoolProperty(name = "Network 1", default = False)
bpy.types.Object.pathNetwork2           = bpy.props.BoolProperty(name = "Network 2", default = False)
bpy.types.Object.pathNetwork3           = bpy.props.BoolProperty(name = "Network 3", default = False)
bpy.types.Object.pathNetwork4           = bpy.props.BoolProperty(name = "Network 4", default = False)
bpy.types.Object.pathNetwork5           = bpy.props.BoolProperty(name = "Network 5", default = False)
bpy.types.Object.pathNetwork6           = bpy.props.BoolProperty(name = "Network 6", default = False)
bpy.types.Object.pathNetwork7           = bpy.props.BoolProperty(name = "Network 7", default = False)
bpy.types.Object.pathNetwork8           = bpy.props.BoolProperty(name = "Network 8", default = False)
bpy.types.Object.pathNetwork9           = bpy.props.BoolProperty(name = "Network 9", default = False)
bpy.types.Object.pathNetwork10          = bpy.props.BoolProperty(name = "Network 10", default = False)
bpy.types.Object.pathNetwork11          = bpy.props.BoolProperty(name = "Network 11", default = False)
bpy.types.Object.pathNetwork12          = bpy.props.BoolProperty(name = "Network 12", default = False)
bpy.types.Object.pathNetwork13          = bpy.props.BoolProperty(name = "Network 13", default = False)
bpy.types.Object.pathNetwork14          = bpy.props.BoolProperty(name = "Network 14", default = False)
bpy.types.Object.pathNetwork15          = bpy.props.BoolProperty(name = "Network 15", default = False)
bpy.types.Object.pathNetwork16          = bpy.props.BoolProperty(name = "Network 16", default = False)
bpy.types.Object.pathNetwork17          = bpy.props.BoolProperty(name = "Network 17", default = False)
bpy.types.Object.pathNetwork18          = bpy.props.BoolProperty(name = "Network 18", default = False)
bpy.types.Object.pathNetwork19          = bpy.props.BoolProperty(name = "Network 19", default = False)
bpy.types.Object.pathNetwork20          = bpy.props.BoolProperty(name = "Network 20", default = False)
bpy.types.Object.pathNetwork21          = bpy.props.BoolProperty(name = "Network 21", default = False)
bpy.types.Object.pathNetwork22          = bpy.props.BoolProperty(name = "Network 22", default = False)
bpy.types.Object.pathNetwork23          = bpy.props.BoolProperty(name = "Network 23", default = False)
bpy.types.Object.pathNetwork24          = bpy.props.BoolProperty(name = "Network 24", default = False)
bpy.types.Object.pathNetwork25          = bpy.props.BoolProperty(name = "Network 25", default = False)
bpy.types.Object.pathNetwork26          = bpy.props.BoolProperty(name = "Network 26", default = False)
bpy.types.Object.pathNetwork27          = bpy.props.BoolProperty(name = "Network 27", default = False)
bpy.types.Object.pathNetwork28          = bpy.props.BoolProperty(name = "Network 28", default = False)
bpy.types.Object.pathNetwork29          = bpy.props.BoolProperty(name = "Network 29", default = False)
bpy.types.Object.pathNetwork30          = bpy.props.BoolProperty(name = "Network 30", default = False)
bpy.types.Object.pathNetwork31          = bpy.props.BoolProperty(name = "Network 31", default = False)
bpy.types.Object.pathFlags              = bpy.props.IntProperty(name = "Flags", default = 1)

# -----------------------------------------------------------------------------
# 
class PathLinkPropertyGroup(bpy.types.PropertyGroup):
    linkName = bpy.props.StringProperty(name="Link")
    
bpy.utils.register_class(PathLinkPropertyGroup)
    
# -----------------------------------------------------------------------------
# 
class PathLinkPropertyList(bpy.types.PropertyGroup):
    links = bpy.props.CollectionProperty(type=PathLinkPropertyGroup)
    index = bpy.props.IntProperty(name = "Active Index", default = -1)
    
bpy.utils.register_class(PathLinkPropertyList)

# -----------------------------------------------------------------------------
# 
class UL_PathLinkProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        row.prop_search(item, "linkName", context.scene, "objects")
    
# -----------------------------------------------------------------------------
#
class AddPathNodeLinkOperator(bpy.types.Operator):
    bl_idname = "object.path_link_add"
    bl_label = "Add Event Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.pathLinkList.links.add()
        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemovePathNodeLinkOperator(bpy.types.Operator):
    bl_idname = "object.path_link_remove"
    bl_label = "Remove Event Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            pl = obj.pathLinkList
            if pl.index >= 0 and pl.index < len(pl.links):
                pl.links.remove(pl.index)
                pl.index -= 1
        return {'FINISHED'}

#-----------------------------------------------------------------------------
#
# Pickup Actors
#
#-----------------------------------------------------------------------------

pickupTypes = [
    ("None", "None", "", -1),
    ("Trojax", "Trojax", "", 0),
    ("PyroliteRifle", "PyroliteRifle", "", 1),
    ("TranspulseCannon", "TranspulseCannon", "", 2),
    ("SussGun", "SussGun", "", 3),
    ("BeamLaser", "BeamLaser", "", 4),
    ("MugMissile", "MugMissile", "", 5),
    ("MugMissiles", "MugMissiles", "", 6),
    ("HeatseekerMissile", "HeatseekerMissile", "", 7),
    ("HeatseekerMissilePack", "HeatseekerMissilePack", "", 8),
    ("ThiefMissile", "ThiefMissile", "", 9),
    ("ScatterMissile", "ScatterMissile", "", 10),
    ("GravgonMissile", "GravgonMissile", "", 11),
    ("RocketLauncher", "RocketLauncher", "", 12),
    ("TitanStarMissile", "TitanStarMissile", "", 13),
    ("PurgeMinePack", "PurgeMinePack", "", 14),
    ("PineMinePack", "PineMinePack", "", 15),
    ("QuantumMinePack", "QuantumMinePack", "", 16),
    ("SpiderMinePack", "SpiderMinePack", "", 17),
    ("ParasiteMine", "ParasiteMine", "", 18),
    ("Flare", "Flare", "", 19    ),
    ("GeneralAmmo", "GeneralAmmo", "", 20),
    ("PyroliteFuel", "PyroliteFuel", "", 21),
    ("SussGunAmmo", "SussGunAmmo", "", 22),
    ("PowerPod", "PowerPod", "", 23),
    ("Shield", "Shield", "", 24    ),
    ("Invulnerability", "Invulnerability", "", 25),
    ("ExtraLife", "ExtraLife", "", 26),
    ("TargetingComputer", "TargetingComputer", "", 27),
    ("SmokeStreamer", "SmokeStreamer", "", 28),
    ("Nitro", "Nitro", "", 29),
    ("Goggles", "Goggles", "", 30),
    ("GoldBars", "GoldBars", "", 31),
    ("StealthMantle", "StealthMantle", "", 32),
    ("Crystal", "Crystal", "", 33    ),
    ("OrbitPulsar", "OrbitPulsar", "", 34),
    ("GoldenPowerPod", "GoldenPowerPod", "", 35),
    ("DNA", "DNA", "", 36),
    ("Key", "Key", "", 37),
    ("Bomb", "Bomb", "", 38),
    ("GoldenIdol", "GoldenIdol", "", 39),
    ("StablizerCrystal", "StablizerCrystal", "", 100),
    ("ComputerCapsule", "ComputerCapsule", "", 101),
    ("Black Hole Gun Part 1", "Black Hole Gun Part 1", "", 102),
    ("Black Hole Gun Part 2", "Black Hole Gun Part 2", "", 103),
    ("Black Hole Gun Part 3", "Black Hole Gun Part 3", "", 104),
    ("Black Hole Gun Part 4", "Black Hole Gun Part 4", "", 105)
    ]
    
# -----------------------------------------------------------------------------
#
bpy.types.Object.pickupType             = bpy.props.EnumProperty(items = pickupTypes, name = "Pickup Type")
bpy.types.Object.pickupGenType          = bpy.props.EnumProperty(items = genTypes, name = "Gen Type")
bpy.types.Object.pickupRegenType        = bpy.props.EnumProperty(items = regenTypes, name = "Regen Type")
bpy.types.Object.pickupWaitTime         = bpy.props.FloatProperty(name = "Wait Time")
bpy.types.Object.pickupGenDelay         = bpy.props.FloatProperty(name = "Gen Delay")
bpy.types.Object.pickupLifeSpan         = bpy.props.FloatProperty(name = "Life Span")

# -----------------------------------------------------------------------------
#
class AddPickupTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pickup_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.pickupTriggerMod.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemovePickupTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pickup_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.pickupTriggerMod
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
 
#-----------------------------------------------------------------------------
#
# Real Time Lights
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
rtLightTypes = [
    ("LIGHT_FIXED", "Fixed", "", 0),
    ("LIGHT_PULSING", "Pulsing", "", 1),
    ("LIGHT_FLICKERING", "Flickering", "", 2),    
    ("LIGHT_SPOT", "Spot", "", 3),
    ]
    
rtLightPulseTypes = [
    ("PULSE_BLINK", "Blink", "", 0),
    ("PULSE_RAMP", "Ramp", "", 1),
    ("PULSE_HALFWAVE", "Halfwave", "", 2),    
    ("PULSE_WAVE", "Wave", "", 3),
    ]
    
bpy.types.Object.rtLightType            = bpy.props.EnumProperty(items = rtLightTypes, name = "RTLight Type")
bpy.types.Object.rtLightRange           = bpy.props.FloatProperty(name = "Range")
bpy.types.Object.rtLightGenDelay        = bpy.props.FloatProperty(name = "Gen Delay")
bpy.types.Object.rtLightOnType          = bpy.props.EnumProperty(items = rtLightPulseTypes, name = "On Type")
bpy.types.Object.rtLightOffType         = bpy.props.EnumProperty(items = rtLightPulseTypes, name = "Off Type")
bpy.types.Object.rtLightGenType         = bpy.props.EnumProperty(items = genTypes, name = "Gen Type")
bpy.types.Object.rtLightPulseType       = bpy.props.EnumProperty(items = rtLightPulseTypes, name = "Pulse Type")
bpy.types.Object.rtLightOnTime          = bpy.props.FloatProperty(name = "On Time")
bpy.types.Object.rtLightOffTime         = bpy.props.FloatProperty(name = "Off Time")
bpy.types.Object.rtLightStayOnChance    = bpy.props.FloatProperty(name = "Stay On Chance")
bpy.types.Object.rtLightStayOffChance   = bpy.props.FloatProperty(name = "Stay Off Chance")
bpy.types.Object.rtLightStayOnTime      = bpy.props.FloatProperty(name = "Stay On Time")
bpy.types.Object.rtLightStayOffTime     = bpy.props.FloatProperty(name = "Stay Off Time")
bpy.types.Object.rtLightColor           = bpy.props.FloatVectorProperty(name = "Light Color", subtype='COLOR', default=[1.0,1.0,1.0])
bpy.types.Object.rtLightCone            = bpy.props.FloatProperty(name = "Cone")
bpy.types.Object.rtLightRotationPeriod  = bpy.props.FloatProperty(name = "Rotation Period")
bpy.types.Object.rtLightFallOff         = bpy.props.FloatProperty(name = "Falloff", default=0.5)
bpy.types.Object.rtLightIntensity       = bpy.props.FloatProperty(name = "Intensity", default=1.0)
bpy.types.Object.rtLightBackfaceCulling = bpy.props.BoolProperty(name = "Backface Culling", default=False)
bpy.types.Object.rtLightAmbient         = bpy.props.BoolProperty(name = "Ambient", default=False)
bpy.types.Object.rtLightMixBlend        = bpy.props.BoolProperty(name = "Mix Blending", default=False)
 
#-----------------------------------------------------------------------------
#
# BG Objects
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
bgObjectTypes = [
    ("BGOTYPE_STATIC", "Static", "", 0),
    ("BGOTYPE_DOOR", "Door", "", 1),
    ("BGOTYPE_ANIM_LOOPING", "Looping Anim", "", 2),
    ("BGOTYPE_ANIM_MULTISTEP", "Multistep Anim", "", 3),
    ("BGOTYPE_ANIM_ONEOFF", "One Off Anim", "", 4),
    ("BGOTYPE_SEQUENCES", "Sequences (not implemented)", "", 5),
    ]
    
# -----------------------------------------------------------------------------
#
bgDoorSfxTypes = [
    ("DORSFX0", "Generic", "", 0),
    ("DORSFX1", "Stone", "", 1),
    ("DORSFX2", "Large Mechanical", "", 2),
    ("DORSFX3", "Lift", "", 3),
    ("DORSFX4", "Small Mechanical", "", 4),
    ("DORSFX5", "Elevator1", "", 5),
    ("DORSFX6", "Elevator2", "", 6),
    ("DORSFX7", "Elevator3", "", 7),
    ("DORSFX8", "Elevator4", "", 8)
    ]
    
bpy.types.Object.bgoType                = bpy.props.EnumProperty(items = bgObjectTypes, name = "BGO Type")
bpy.types.Object.bgoCOBFile             = bpy.props.StringProperty(name = ".COB file", default = "unknown.cob")
bpy.types.Object.bgoPlayerBump          = bpy.props.BoolProperty(name = "Player Bump")
bpy.types.Object.bgoPlayerShot          = bpy.props.BoolProperty(name = "Player Shot")
bpy.types.Object.bgoEnemyBump           = bpy.props.BoolProperty(name = "Enemy Bump")
bpy.types.Object.bgoEnemyShot           = bpy.props.BoolProperty(name = "Enemy Shot")
bpy.types.Object.bgoDoorLocked          = bpy.props.BoolProperty(name = "Door Locked")
bpy.types.Object.bgoDestroyAtEnd        = bpy.props.BoolProperty(name = "Destroy At End")
bpy.types.Object.bgoGenType             = bpy.props.EnumProperty(items = genTypes, name = "Gen Type")
bpy.types.Object.bgoGenDelay            = bpy.props.FloatProperty(name = "Gen Delay")
bpy.types.Object.bgoRequiredPickup      = bpy.props.EnumProperty(items = pickupTypes, name = "Required Pickup", default = "None")
bpy.types.Object.bgoDoorSfxType         = bpy.props.EnumProperty(items = bgDoorSfxTypes, name = "Door SFX Type", default = "DORSFX0")
bpy.types.Object.bgoIntervals           = bpy.props.IntProperty(name = "Intervals", default = 1)
bpy.types.Object.bgoDamagePerInterval   = bpy.props.FloatProperty(name = "Damage Per Interval", default = 1024.0)

# -----------------------------------------------------------------------------
#
class AddBGOBumpTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.bgo_bump_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.bgoBumpEvent.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveBGOBumpTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.bgo_bump_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.bgoBumpEvent
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
# -----------------------------------------------------------------------------
#
class AddBGOShotTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.bgo_shot_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.bgoShotEvent.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveBGOShotTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.bgo_shot_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.bgoShotEvent
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
# -----------------------------------------------------------------------------
#
class AddBGOEndTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.bgo_end_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.bgoEndEvent.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveBGOEndTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.bgo_end_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.bgoEndEvent
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
  
#-----------------------------------------------------------------------------
#
# Area Zones
#
#-----------------------------------------------------------------------------

zoneType = [
    ("ZONE_SPHERE", "Sphere", "", 0),
    ("ZONE_BOX", "Box", "", 1),
    ("ZONE_POLYGON", "Polygon", "", 2),
    ]
    
bpy.types.Object.zoneAreaType           = bpy.props.EnumProperty(items = zoneType, name = "Zone Type", default = 'ZONE_POLYGON')
 
# -----------------------------------------------------------------------------
# 
primaryWeaponTypes = [
    ("NONE", "None", "", -1),
    ("PULSAR", "Pulsar", "", 0),
    ("TROJAX", "Trojax", "", 1),
    ("PYROLITE_RIFLE", "Pyrolite", "", 2),
    ("TRANSPULSE_CANNON", "Transpulse", "", 3),
    ("SUSS_GUN", "SussGun", "", 4),
    ("LASER", "Laser", "", 5),
    ("ORBITPULSAR", "Orbit Pulsar", "", 6),
    ("NME_BULLET1", "Enemy Bullet", "", 7),
    ("NME_PULSAR", "Enemy Pulsar", "", 8),
    ("NME_TROJAX", "Enemy Trojax", "", 9),
    ("NME_PYROLITE", "Enemy Prolite", "", 10),
    ("NME_TRANSPULSE", "Enemy Transpulse", "", 11),
    ("NME_SUSS_GUN", "Enemy SussGun", "", 12),
    ("NME_LASER", "Enemy Laser", "", 13),
    ("NME_LIGHTNING", "Enemy Lightning", "", 14),
    ("FLAMES", "Flames", "", 15),
    ("NME_POWERLASER", "Enemy Powerlaser", "", 16),
    ("NME_RAMQAN", "Enemy Ramqan Pulsar", "", 17)
    ]
    
# -----------------------------------------------------------------------------
# 
secondaryWeaponTypes = [
    ("NONE", "None", "", -1),
    ("MUGMISSILE", "Mug", "", 0),
    ("SOLARISMISSILE", "Solaris", "", 1),
    ("THIEFMISSILE", "Thief Missile (unused)", "", 2),
    ("SCATTERMISSILE", "Scatter", "", 3),
    ("GRAVGONMISSILE", "Gravgon", "", 4),
    ("MULTIPLEMISSILE", "MRFL", "", 5),
    ("TITANSTARMISSILE", "Titan", "", 6),
    ("PURGEMINE", "Purge Mine", "", 7),
    ("PINEMINE", "Pine Mine", "", 8),
    ("QUANTUMMINE", "Quantum Mine", "", 9),
    ("SPIDERMINE", "Spider Mine (unused)", "", 10),
    ("PINEMISSILE", "Pine Missile", "", 11),
    ("TITANSTARSHRAPNEL", "Titan Shrapnel", "", 12),
    ("ENEMYSPIRALMISSILE", "Spiral Missile", "", 13),
    ("ENEMYHOMINGMISSILE", "Homing Missile", "", 14),
    ("ENEMYBLUEHOMINGMISSILE", "Blue Homing Missile", "", 15),
    ("ENEMYFIREBALL", "Fireball", "", 16),
    ("ENEMYTENTACLE", "Tentacle", "", 17),
    ("ENEMYDEPTHCHARGE", "Depth Charge", "", 18),
    ("QUANTUMMINE_DN", "Dreadnaught Quantum Mine", "", 20)
    ]
    
bpy.types.Object.zoneAreaPrimaryPlayer      = bpy.props.EnumProperty(items = primaryWeaponTypes, name = "Player Primary", default = 'NONE')
bpy.types.Object.zoneAreaSecondaryPlayer    = bpy.props.EnumProperty(items = secondaryWeaponTypes, name = "Player Secondary", default = 'NONE')
bpy.types.Object.zoneAreaPrimaryNME         = bpy.props.EnumProperty(items = primaryWeaponTypes, name = "Enemy Primary", default = 'NONE')
bpy.types.Object.zoneAreaSecondaryNME       = bpy.props.EnumProperty(items = secondaryWeaponTypes, name = "Enemy Secondary", default = 'NONE')
    
#
# *MOANS*
#

# -----------------------------------------------------------------------------
#
class AddZAPIITriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pii_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaPII.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAPIITriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pii_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaPII
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}

# -----------------------------------------------------------------------------
#
class AddZAPENTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pen_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaPEN.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAPENTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pen_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaPEN
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
# -----------------------------------------------------------------------------
#
class AddZAPEXTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pex_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaPEX.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAPEXTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.pex_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaPEX
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
        # -----------------------------------------------------------------------------
#
class AddZAPSHTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.psh_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaPSH.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAPSHTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.psh_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaPSH
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}     
# -----------------------------------------------------------------------------
#
class AddZAEIITriggerModOperator(bpy.types.Operator):
    bl_idname = "object.eii_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaEII.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAEIITriggerModOperator(bpy.types.Operator):
    bl_idname = "object.eii_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaEII
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}

# -----------------------------------------------------------------------------
#
class AddZAEENTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.een_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaEEN.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAEENTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.een_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaEEN
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
# -----------------------------------------------------------------------------
#
class AddZAEEXTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.eex_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaEEX.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAEEXTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.eex_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaEEX
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
# -----------------------------------------------------------------------------
#
class AddZAESHTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.esh_triggermod_add"
    bl_label = "Add Trigger Mod Operator"

    def execute(self, context):
        print(self.as_keywords())
        obj = context.object
        if obj is not None:
            obj.zoneAreaESH.trigger_mods.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveZAESHTriggerModOperator(bpy.types.Operator):
    bl_idname = "object.esh_triggermod_remove"
    bl_label = "Remove Trigger Mod Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            mods = obj.zoneAreaESH
            if mods.index >= 0 and mods.index < len(mods.trigger_mods):
                mods.trigger_mods.remove(mods.index)
                mods.index -= 1

        return {'FINISHED'}
        
#-----------------------------------------------------------------------------
#
# Trigger Events
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
triggerEvents = [
    ("PICKUP", "Pickup", "", 0),
    ("ENEMY", "Enemy", "", 1),
    ("OPENDOOR", "Open Door", "", 2),
    ("CLOSEDOOR", "Close Door", "", 3),
    ("LOCKDOOR", "Lock Door", "", 4),
    ("UNLOCKDOOR", "Unlock Door", "", 5),
    ("STARTBGOANIM", "Start BGO Anim", "", 6),
    ("STOPBGOANIM", "Stop BGO Anim", "", 7),
    ("STARTTEXANIM", "Start Texture Anim", "", 8),
    ("STOPTEXANIM", "Stop Texture Anim", "", 9),
    ("STARTEXTFORCE", "Start External Force", "", 10),
    ("STOPEXTFORCE", "Stop External Force", "", 11),
    ("ENABLETELEPORT", "Enable Teleport", "", 12),
    ("DISABLETELEPORT", "Disable Teleport", "", 13),
    ("WATERFILL", "Water Fill", "", 14),
    ("WATERDRAIN", "Water Drain", "", 15),
    ("STARTSPOTFX", "Start Spot FX", "", 16),
    ("STOPSPOTFX", "Stop Spot FX", "", 17),
    ("SHOWMESSAGE", "Show Message", "", 18),
    ("LIGHTENABLE", "Light Enable", "", 19),
    ("LIGHTDISABLE", "Light Disable", "", 20),
    ("TRIGGERAREAENABLE", "Trigger Area Enable", "", 21),
    ("TRIGGERAREADISABLE", "Trigger Area Disable", "", 22),
    ("CAMERAENABLE", "Camera Enable", "", 23),
    ("CAMERADISABLE", "Camera Disable", "", 24),
    ("NODEENABLE", "Path Node Enable", "", 25),
    ("NODEDISABLE", "Path Node Disable", "", 26),
    ("SETENEMYANIMSEQ", "Set Enemy Animation Sequence", "", 27),
    ("SETLEVELEND", "Set Level End", "", 28)
    ]
     
# -----------------------------------------------------------------------------
# 
class TriggerEventPropertyGroup(bpy.types.PropertyGroup):
    event   = bpy.props.EnumProperty(items = triggerEvents, name = "Event")
    value1  = bpy.props.StringProperty(name = "Param 1")
    value2  = bpy.props.StringProperty(name = "Param 2")
    value3  = bpy.props.StringProperty(name = "Param 3")
    value4  = bpy.props.StringProperty(name = "Param 4")
    
bpy.utils.register_class(TriggerEventPropertyGroup)
 
# -----------------------------------------------------------------------------
# 
class UL_TriggerEventProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        row.prop(item, "event")
        split = layout.split()
        col = split.column()
        row = col.row()
        row.prop(item, "value1")
        #row = col.row()
        #row.prop(item, "value2")
        #row = col.row()
        #row.prop(item, "value3")
        #row = col.row()
        #row.prop(item, "value4")
         
# -----------------------------------------------------------------------------
# 
class TriggerEventList(bpy.types.PropertyGroup):
    events = bpy.props.CollectionProperty(type = TriggerEventPropertyGroup, name = "Events")
    index = bpy.props.IntProperty(name = "Active Index", default = -1)
    
# -----------------------------------------------------------------------------
#
class AddTriggerEventOperator(bpy.types.Operator):
    bl_idname = "object.trig_events_add"
    bl_label = "Add Event Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.triggerCondition.events.add()
        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveTriggerEventOperator(bpy.types.Operator):
    bl_idname = "object.trig_events_remove"
    bl_label = "Remove Event Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            cond = obj.triggerCondition
            if cond.evIndex >= 0 and cond.evIndex < len(cond.events):
                cond.events.remove(cond.evIndex)
                cond.evIndex -= 1
        return {'FINISHED'}
 
#-----------------------------------------------------------------------------
#
# Trigger Variables
#
#-----------------------------------------------------------------------------
     
# -----------------------------------------------------------------------------
# 
class TriggerVarPropertyGroup(bpy.types.PropertyGroup):
    variable        = bpy.props.StringProperty(name = "Variable Name")
    initialValue    = bpy.props.IntProperty(name = "Initial Value")

bpy.utils.register_class(TriggerVarPropertyGroup)

# -----------------------------------------------------------------------------
#
class UL_TriggerVarProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        row.prop(item, "variable")
        row = layout.row()
        row.prop(item, "initialValue")
 
# -----------------------------------------------------------------------------
#    
class TriggerVarList(bpy.types.PropertyGroup):
    variables   = bpy.props.CollectionProperty(type = TriggerVarPropertyGroup, name = "Variables")
    index       = bpy.props.IntProperty(name = "Active Index", default = -1)
    
# -----------------------------------------------------------------------------
#
class AddTriggerVarOperator(bpy.types.Operator):
    bl_idname = "object.trig_variables_add"
    bl_label = "Add Condition Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.trigVariables.variables.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveTriggerVarOperator(bpy.types.Operator):
    bl_idname = "object.trig_variables_remove"
    bl_label = "Remove Condition Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            cond = obj.trigVariables
            if cond.index >= 0 and cond.index < len(cond.variables):
                cond.variables.remove(cond.index)
                cond.index -= 1

        return {'FINISHED'}
        
#-----------------------------------------------------------------------------
#
# Triggers
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
triggerTypes = [
    ("EQUAL", "Equal", "", 0),
    ("NOTEQUAL", "Not Equal", "", 1),
    ("LESS", "Less", "", 2),
    ("GREATER", "Greater", "", 3),
    ("LESSEQUAL", "LessEqual", "", 4),
    ("GREATEREQUAL", "GreaterEqual", "", 5),
    ("FLAGCOUNT", "FlagCount", "", 6),
    ("FLAGTEST", "FlagTest", "", 7),
    ]
    
# -----------------------------------------------------------------------------
#   
class TriggerConditionTargetList(bpy.types.PropertyGroup):
    conditionName = bpy.props.StringProperty(name = "Condition Object")
    
bpy.utils.register_class(TriggerConditionTargetList)
         
# -----------------------------------------------------------------------------
# 
class UL_ConditionNameProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        layout.prop_search(item, "conditionName", context.scene, "objects")
        
# -----------------------------------------------------------------------------
#
class AddConditionNameOperator(bpy.types.Operator):
    bl_idname = "object.cond_name_add"
    bl_label = "Add Condition Name Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.trigger.conditions.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveConditionNameOperator(bpy.types.Operator):
    bl_idname = "object.cond_name_remove"
    bl_label = "Remove Condition Name Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            trig = obj.trigger
            if trig.condIndex >= 0 and trig.condIndex < len(trig.conditions):
                trig.conditions.remove(trig.condIndex)
                trig.index -= 1

        return {'FINISHED'}
        
# -----------------------------------------------------------------------------
#    
class TriggersPropertyGroup(bpy.types.PropertyGroup):
    variable    = bpy.props.StringProperty(name = "Variable")
    compare     = bpy.props.EnumProperty(items = triggerTypes, name = "Compare")
    value       = bpy.props.IntProperty(name = "Value")
    conditions  = bpy.props.CollectionProperty(type = TriggerConditionTargetList, name = "Conditions")
    condIndex   = bpy.props.IntProperty(name = "Active Index", default = -1)
    
#-----------------------------------------------------------------------------
#
# Trigger Condition
#
#-----------------------------------------------------------------------------
   
# -----------------------------------------------------------------------------
#   
class TriggerConditionNameList(bpy.types.PropertyGroup):
    triggerName = bpy.props.StringProperty(name = "Trigger Object")
    
bpy.utils.register_class(TriggerConditionNameList)
    
# -----------------------------------------------------------------------------
#
class AddTriggerNameOperator(bpy.types.Operator):
    bl_idname = "object.trig_name_add"
    bl_label = "Add Trigger Name Operator"

    def execute(self, context):
        obj = context.object
        if obj is not None:
            obj.triggerCondition.triggers.add()

        return {'FINISHED'}
       
# -----------------------------------------------------------------------------
# 
class RemoveTriggerNameOperator(bpy.types.Operator):
    bl_idname = "object.trig_name_remove"
    bl_label = "Remove Trigger Name Operator"

    def execute(self, context):
        obj = context.object

        if obj is not None:
            cond = obj.triggerCondition
            if cond.trigIndex >= 0 and cond.trigIndex < len(cond.triggers):
                cond.triggers.remove(cond.trigIndex)
                cond.index -= 1

        return {'FINISHED'}
         
# -----------------------------------------------------------------------------
# 
class UL_TriggerNameProperties(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        layout.prop_search(item, "triggerName", context.scene, "objects")
         
# -----------------------------------------------------------------------------
# 
class TriggerConditionList(bpy.types.PropertyGroup):
    triggers    = bpy.props.CollectionProperty(type = TriggerConditionNameList, name = "Triggers")
    events      = bpy.props.CollectionProperty(type = TriggerEventPropertyGroup, name = "Events")
    trigIndex   = bpy.props.IntProperty(name = "Active Index", default = -1)
    evIndex     = bpy.props.IntProperty(name = "Active Index", default = -1)
       
#-----------------------------------------------------------------------------
#
# Enemies
#
#-----------------------------------------------------------------------------

enemyTypes = [
    ("BeamTurret", "BeamTurret", "", 0),
    ("DuelTurret", "DuelTurret", "", 1),
    ("PulseTurret", "PulseTurret", "", 2),
    ("MissileTurret", "MissileTurret", "", 3),
    ("SnubTurret", "SnubTurret", "", 4),
    ("LazerBot", "LazerBot", "", 5),
    ("SnubBot", "SnubBot", "", 6),
    ("AirMoble", "AirMoble", "", 7),
    ("AmmoDump", "AmmoDump", "", 8),
    ("LeviTank", "LeviTank", "", 9),
    ("Max", "Max", "", 10),
    ("Mekton", "Mekton", "", 11),
    ("Boss_Nukecrane", "Boss_Nukecrane", "", 12),
    ("Supressor", "Supressor", "", 13),
    ("MineSweeper", "MineSweeper", "", 14),
    ("Swarm", "Swarm", "", 15),
    ("Shade", "Shade", "", 16),
    ("MineLayer", "MineLayer", "", 17),
    ("Hunter", "Hunter", "", 18),
    ("Legz", "Legz", "", 19),
    ("GuardBot", "GuardBot", "", 20),
    ("Boss_Metatank", "Boss_Metatank", "", 21),
    ("Boss_BigGeek", "Boss_BigGeek", "", 22),
    ("Boss_Avatar", "Boss_Avatar", "", 23),
    ("Boss_FleshMorph", "Boss_FleshMorph", "", 24),
    ("Boss_Exogenon", "Boss_Exogenon", "", 25),
    ("Bike_Lokasenna", "Bike_Lokasenna", "", 26),
    ("Bike_Beard", "Bike_Beard", "", 27),
    ("Bike_LAJay", "Bike_LAJay", "", 28),
    ("Bike_ExCop", "Bike_ExCop", "", 29),
    ("Bike_RexHardy", "Bike_RexHardy", "", 30),
    ("Bike_Foetoid", "Bike_Foetoid", "", 31),
    ("Bike_NimSoo", "Bike_NimSoo", "", 32),
    ("Bike_Nutta", "Bike_Nutta", "", 33),
    ("Bike_Sceptre", "Bike_Sceptre", "", 34),
    ("Bike_Jo", "Bike_Jo", "", 35),
    ("Bike_CuvelClark", "Bike_CuvelClark", "", 36),
    ("Bike_HK5", "Bike_HK5", "", 37),
    ("Bike_Nubia", "Bike_Nubia", "", 38),
    ("Bike_Mofisto", "Bike_Mofisto", "", 39),
    ("Bike_Cerbero", "Bike_Cerbero", "", 40),
    ("Bike_Slick", "Bike_Slick", "", 41),
    ("LEADER_Swarm", "LEADER_Swarm", "", 42),
    ("LEADER_Hunter", "LEADER_Hunter", "", 43),
    ("LEADER_Mekton", "LEADER_Mekton", "", 44),
    ("LEADER_SnubBot", "LEADER_SnubBot", "", 45),
    ("LEADER_Legz", "LEADER_Legz", "", 46),
    ("LEADER_Shade", "LEADER_Shade", "", 47),
    ("LEADER_Supressor", "LEADER_Supressor", "", 48),
    ("LEADER_LeviTank", "LEADER_LeviTank", "", 49),
    ("LEADER_LazerBot", "LEADER_LazerBot", "", 50),
    ("LEADER_Max", "LEADER_Max", "", 51),
    ("LEADER_AirMoble", "LEADER_AirMoble", "", 52),
    ("Fodder1", "Fodder1", "", 53),
    ("Boss_LittleGeek", "Boss_LittleGeek", "", 54),
    ("Bike_FlyGirl", "Bike_FlyGirl", "", 55),
    ("Manmech (N64)", "Manmech (N64)", "", 100),
    ("Cargo Drone (N64)", "Cargo Drone (N64)", "", 101),
    ("Ramqan (N64)", "Ramqan (N64)", "", 102),
    ("Shield Turret (N64)", "Shield Turret (N64)", "", 103),
    ("Maldroid (N64)", "Maldroid (N64)", "", 104),
    ("Enforcer (N64)", "Enforcer (N64)", "", 105),
    ("Dreadnaught2 (N64)", "Dreadnaught 2 (N64)", "", 106),
    ("Dreadnaught (N64)", "Dreadnaught (N64)", "", 107),
    ("Ghost (N64)", "Ghost (N64)", "", 108)
    ]
    
bpy.types.Object.nmeDropPickup          = bpy.props.EnumProperty(items = pickupTypes, name = "Drop Pickup Type", default = "None")
bpy.types.Object.nmeType                = bpy.props.EnumProperty(items = enemyTypes, name = "Enemy Type")
bpy.types.Object.nmeFormationTarget     = bpy.props.StringProperty(name = "Formation Target")

#-----------------------------------------------------------------------------
#
# Water
#
#-----------------------------------------------------------------------------

bpy.types.Object.watColor               = bpy.props.FloatVectorProperty(name = "Color", subtype='COLOR', default=[1.0,1.0,1.0])
bpy.types.Object.watMaxLevel            = bpy.props.FloatProperty(name = "Max Level", default = 0.0)
bpy.types.Object.watMinLevel            = bpy.props.FloatProperty(name = "Min Level", default = 0.0)
bpy.types.Object.watFillRate            = bpy.props.FloatProperty(name = "Fill Rate", default = 2.13)
bpy.types.Object.watDrainRate           = bpy.props.FloatProperty(name = "Drain Rate", default = 2.13)
bpy.types.Object.watDensity             = bpy.props.FloatProperty(name = "Density", default = 0.0)
bpy.types.Object.watMaxWaveSize         = bpy.props.FloatProperty(name = "Max Wave Size", default = 0.0)
bpy.types.Object.watDamage              = bpy.props.FloatProperty(name = "Damage Per Sec", default = 0.0)
bpy.types.Object.watTexture             = bpy.props.StringProperty(name = "Water Texture")

#-----------------------------------------------------------------------------
#
# SpotFX
#
#-----------------------------------------------------------------------------

spotFxTypes = [
    ("Smoke", "Smoke", "", 0),
    ("Steam", "Steam", "", 1),
    ("Sparks", "Sparks", "", 2),
    ("Nmetrail", "Nmetrail", "", 3),
    ("Nmeglow", "Nmeglow", "", 4),
    ("Nmevaportrail", "Nmevaportrail", "", 5),
    ("Flame", "Flame", "", 6),
    ("Explosion", "Explosion", "", 7),
    ("Fireprimary", "Fireprimary", "", 8),
    ("Firesecondary", "Firesecondary", "", 9),
    ("Electricbeams", "Electricbeams", "", 10),
    ("Gravgontrail", "Gravgontrail", "", 11),
    ("Firewall", "Firewall", "", 12),
    ("Gravitysparks", "Gravitysparks", "", 13),
    ("Shrapnel", "Shrapnel", "", 14),
    ("Bubbles", "Bubbles", "", 15),
    ("Drip", "Drip", "", 16),
    ("Soundfx", "Soundfx", "", 17),
    ("Beardafterburner", "Beardafterburner", "", 18),
    ("Borgafterburner", "Borgafterburner", "", 19),
    ("Excopafterburner", "Excopafterburner", "", 20),
    ("Truckerafterburner", "Truckerafterburner", "", 21),
    ("Nubiaafterburner", "Nubiaafterburner", "", 22),
    ("Cerberoafterburner", "Cerberoafterburner", "", 23),
    ("Foetidafterburner", "Foetidafterburner", "", 24),
    ("Foetidsmallafterburner", "Foetidsmallafterburner", "", 25),
    ("Hk5afterburner", "Hk5afterburner", "", 26),
    ("Japbirdafterburner", "Japbirdafterburner", "", 27),
    ("Joafterburner", "Joafterburner", "", 28),
    ("Josmallafterburner", "Josmallafterburner", "", 29),
    ("Lajayafterburner", "Lajayafterburner", "", 30),
    ("Mofistoafterburner", "Mofistoafterburner", "", 31),
    ("Nutterafterburner", "Nutterafterburner", "", 32),
    ("Rhesusafterburner", "Rhesusafterburner", "", 33),
    ("Sharkafterburner", "Sharkafterburner", "", 34),
    ("Slickafterburner", "Slickafterburner", "", 35)
    ]
    
sfxType = [
    ("SFX_TYPE_NORMAL", "Normal", "", 0),
    ("SFX_TYPE_NOPAN", "No Panning", "", 1),
    ("SFX_TYPE_TAUNT", "Taunt", "", 2),
    ]
    
bpy.types.Object.fxColor                = bpy.props.FloatVectorProperty(name = "Color", subtype='COLOR', default=[1.0,1.0,1.0])
bpy.types.Object.fxActiveDelay          = bpy.props.FloatProperty(name = "Active Delay", default = 0.0)
bpy.types.Object.fxInactiveDelay        = bpy.props.FloatProperty(name = "Inactive Delay", default = 0.0)
bpy.types.Object.fxPrimaryID            = bpy.props.EnumProperty(items = primaryWeaponTypes, name = "Primary ID", default = "NONE")
bpy.types.Object.fxSecondaryID          = bpy.props.EnumProperty(items = secondaryWeaponTypes, name = "Secondary ID", default = "NONE")
bpy.types.Object.fxSFX                  = bpy.props.StringProperty(name = "SFX Name")
bpy.types.Object.fxVolume               = bpy.props.FloatProperty(name = "SFX Volume", default = 1.0)
bpy.types.Object.fxSpeed                = bpy.props.FloatProperty(name = "Speed", default = 0.0)
bpy.types.Object.fxType                 = bpy.props.EnumProperty(items = spotFxTypes, name = "SpotFX Type")
bpy.types.Object.sfxType                = bpy.props.EnumProperty(items = sfxType, name = "SFX Type")

#-----------------------------------------------------------------------------
#
# External Forces
#
#-----------------------------------------------------------------------------

forceTypes = [
    ("TYPE_MOVE", "Move", "", 0),
    ("TYPE_SHIELD", "Shield", "", 1),
    ("TYPE_SHAKE", "Shake", "", 2),
    ]
    
bpy.types.Object.efType                 = bpy.props.EnumProperty(items = forceTypes, name = "Force Type")
bpy.types.Object.efMinForce             = bpy.props.FloatProperty(name = "Min Force", default = 1.0)
bpy.types.Object.efMaxForce             = bpy.props.FloatProperty(name = "Max Force", default = 1.0)
bpy.types.Object.efRange                = bpy.props.FloatProperty(name = "Range", default = 1024.0)
bpy.types.Object.efActive               = bpy.props.BoolProperty(name = "Active", default=True)

from . import forsaken_texture_anims
from . import forsaken_import_export
from . import forsaken_panel_operators
                
#-----------------------------------------------------------------------------
#
# Object Panel
#
#-----------------------------------------------------------------------------
   
# -----------------------------------------------------------------------------
#
class ForsakenObjectPanel(bpy.types.Panel):
    bl_label = "Forsaken Object Properties"
    bl_idname = "OBJECT_PT_ForsakenObjectProp"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        from . import forsaken_object_panel
        forsaken_object_panel.draw(self, context)

#-----------------------------------------------------------------------------
#
# Initialization/Registration
#
#-----------------------------------------------------------------------------
           
# -----------------------------------------------------------------------------
#
def register():
    bpy.utils.register_module(__name__)
    
    forsaken_panel_operators.register()
    forsaken_texture_anims.register()
    
    bpy.utils.unregister_class(ForsakenObjectPanel)
    bpy.utils.unregister_class(UL_TriggerModProperties)
    
    bpy.utils.unregister_class(UL_TriggerEventProperties)
    bpy.utils.unregister_class(UL_ConditionNameProperties)
    bpy.utils.unregister_class(UL_TriggerVarProperties)
    bpy.utils.unregister_class(UL_TriggerNameProperties)
    bpy.utils.unregister_class(UL_PathLinkProperties)
    bpy.utils.unregister_class(AddPickupTriggerModOperator)
    bpy.utils.unregister_class(RemovePickupTriggerModOperator)
    bpy.utils.unregister_class(AddTriggerVarOperator)
    bpy.utils.unregister_class(RemoveTriggerVarOperator)
    bpy.utils.unregister_class(AddTriggerNameOperator)
    bpy.utils.unregister_class(RemoveTriggerNameOperator)
    bpy.utils.unregister_class(AddTriggerEventOperator)
    bpy.utils.unregister_class(RemoveTriggerEventOperator)
    bpy.utils.unregister_class(AddConditionNameOperator)
    bpy.utils.unregister_class(RemoveConditionNameOperator)
    
    bpy.utils.unregister_class(AddZAPIITriggerModOperator)
    bpy.utils.unregister_class(AddZAPENTriggerModOperator)
    bpy.utils.unregister_class(AddZAPEXTriggerModOperator)
    bpy.utils.unregister_class(AddZAPSHTriggerModOperator)
    bpy.utils.unregister_class(AddZAEIITriggerModOperator)
    bpy.utils.unregister_class(AddZAEENTriggerModOperator)
    bpy.utils.unregister_class(AddZAEEXTriggerModOperator)
    bpy.utils.unregister_class(AddZAESHTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPIITriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPENTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPEXTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPSHTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAEIITriggerModOperator)
    bpy.utils.unregister_class(RemoveZAEENTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAEEXTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAESHTriggerModOperator)
    bpy.utils.unregister_class(AddBGOBumpTriggerModOperator)
    bpy.utils.unregister_class(RemoveBGOBumpTriggerModOperator)
    bpy.utils.unregister_class(AddBGOShotTriggerModOperator)
    bpy.utils.unregister_class(RemoveBGOShotTriggerModOperator)
    bpy.utils.unregister_class(AddBGOEndTriggerModOperator)
    bpy.utils.unregister_class(RemoveBGOEndTriggerModOperator)
    bpy.utils.unregister_class(AddPathNodeLinkOperator)
    bpy.utils.unregister_class(RemovePathNodeLinkOperator)
    
    bpy.utils.register_class(ForsakenObjectPanel)
    bpy.utils.register_class(UL_TriggerModProperties)
    
    bpy.utils.register_class(UL_TriggerEventProperties)
    bpy.utils.register_class(UL_ConditionNameProperties)
    bpy.utils.register_class(UL_TriggerVarProperties)
    bpy.utils.register_class(UL_TriggerNameProperties)
    bpy.utils.register_class(UL_PathLinkProperties)
    bpy.utils.register_class(AddPickupTriggerModOperator)
    bpy.utils.register_class(RemovePickupTriggerModOperator)
    bpy.utils.register_class(AddTriggerVarOperator)
    bpy.utils.register_class(RemoveTriggerVarOperator)
    bpy.utils.register_class(AddTriggerNameOperator)
    bpy.utils.register_class(RemoveTriggerNameOperator)
    bpy.utils.register_class(AddTriggerEventOperator)
    bpy.utils.register_class(RemoveTriggerEventOperator)
    bpy.utils.register_class(AddConditionNameOperator)
    bpy.utils.register_class(RemoveConditionNameOperator)
    
    bpy.utils.register_class(AddZAPIITriggerModOperator)
    bpy.utils.register_class(AddZAPENTriggerModOperator)
    bpy.utils.register_class(AddZAPEXTriggerModOperator)
    bpy.utils.register_class(AddZAPSHTriggerModOperator)
    bpy.utils.register_class(AddZAEIITriggerModOperator)
    bpy.utils.register_class(AddZAEENTriggerModOperator)
    bpy.utils.register_class(AddZAEEXTriggerModOperator)
    bpy.utils.register_class(AddZAESHTriggerModOperator)
    bpy.utils.register_class(RemoveZAPIITriggerModOperator)
    bpy.utils.register_class(RemoveZAPENTriggerModOperator)
    bpy.utils.register_class(RemoveZAPEXTriggerModOperator)
    bpy.utils.register_class(RemoveZAPSHTriggerModOperator)
    bpy.utils.register_class(RemoveZAEIITriggerModOperator)
    bpy.utils.register_class(RemoveZAEENTriggerModOperator)
    bpy.utils.register_class(RemoveZAEEXTriggerModOperator)
    bpy.utils.register_class(RemoveZAESHTriggerModOperator)
    bpy.utils.register_class(AddBGOBumpTriggerModOperator)
    bpy.utils.register_class(RemoveBGOBumpTriggerModOperator)
    bpy.utils.register_class(AddBGOShotTriggerModOperator)
    bpy.utils.register_class(RemoveBGOShotTriggerModOperator)
    bpy.utils.register_class(AddBGOEndTriggerModOperator)
    bpy.utils.register_class(RemoveBGOEndTriggerModOperator)
    bpy.utils.register_class(AddPathNodeLinkOperator)
    bpy.utils.register_class(RemovePathNodeLinkOperator)
    
    forsaken_import_export.register()
    
    bpy.types.Object.pickupTriggerMod   = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.trigVariables      = bpy.props.PointerProperty(type=TriggerVarList)
    bpy.types.Object.trigger            = bpy.props.PointerProperty(type=TriggersPropertyGroup)
    bpy.types.Object.triggerCondition   = bpy.props.PointerProperty(type=TriggerConditionList)
    bpy.types.Object.zoneAreaGen        = bpy.props.PointerProperty(type=GeneratePropertyGroup)
    bpy.types.Object.pathLinkList       = bpy.props.PointerProperty(type=PathLinkPropertyList)
    
    bpy.types.Object.zoneAreaPII        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaPEN        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaPEX        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaPSH        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaEII        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaEEN        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaEEX        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.zoneAreaESH        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.bgoShotEvent       = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.bgoBumpEvent       = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.bgoEndEvent        = bpy.props.PointerProperty(type=TriggerModList)
    bpy.types.Object.enemyGen           = bpy.props.PointerProperty(type=GeneratePropertyGroup)
    bpy.types.Object.fxGen              = bpy.props.PointerProperty(type=GeneratePropertyGroup)
    
# -----------------------------------------------------------------------------
#
def unregister():
    bpy.utils.unregister_module(__name__)
    
    forsaken_panel_operators.unregister()
    forsaken_texture_anims.unregister()
    
    bpy.utils.unregister_class(ForsakenObjectPanel)
    bpy.utils.unregister_class(UL_TriggerModProperties)
    bpy.utils.unregister_class(UL_AnimDefProperties)
    bpy.utils.unregister_class(UL_TriggerEventProperties)
    bpy.utils.unregister_class(UL_ConditionNameProperties)
    bpy.utils.unregister_class(UL_TriggerVarProperties)
    bpy.utils.unregister_class(UL_TriggerNameProperties)
    bpy.utils.unregister_class(UL_PathLinkProperties)
    bpy.utils.unregister_class(AddPickupTriggerModOperator)
    bpy.utils.unregister_class(RemovePickupTriggerModOperator)
    bpy.utils.unregister_class(AddTriggerVarOperator)
    bpy.utils.unregister_class(RemoveTriggerVarOperator)
    bpy.utils.unregister_class(AddTriggerNameOperator)
    bpy.utils.unregister_class(RemoveTriggerNameOperator)
    bpy.utils.unregister_class(AddTriggerEventOperator)
    bpy.utils.unregister_class(RemoveTriggerEventOperator)
    bpy.utils.unregister_class(AddConditionNameOperator)
    bpy.utils.unregister_class(RemoveConditionNameOperator)
    
    bpy.utils.unregister_class(AddZAPIITriggerModOperator)
    bpy.utils.unregister_class(AddZAPENTriggerModOperator)
    bpy.utils.unregister_class(AddZAPEXTriggerModOperator)
    bpy.utils.unregister_class(AddZAPSHTriggerModOperator)
    bpy.utils.unregister_class(AddZAEIITriggerModOperator)
    bpy.utils.unregister_class(AddZAEENTriggerModOperator)
    bpy.utils.unregister_class(AddZAEEXTriggerModOperator)
    bpy.utils.unregister_class(AddZAESHTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPIITriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPENTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPEXTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAPSHTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAEIITriggerModOperator)
    bpy.utils.unregister_class(RemoveZAEENTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAEEXTriggerModOperator)
    bpy.utils.unregister_class(RemoveZAESHTriggerModOperator)
    bpy.utils.unregister_class(AddBGOBumpTriggerModOperator)
    bpy.utils.unregister_class(RemoveBGOBumpTriggerModOperator)
    bpy.utils.unregister_class(AddBGOShotTriggerModOperator)
    bpy.utils.unregister_class(RemoveBGOShotTriggerModOperator)
    bpy.utils.unregister_class(AddBGOEndTriggerModOperator)
    bpy.utils.unregister_class(RemoveBGOEndTriggerModOperator)
    bpy.utils.unregister_class(AddPathNodeLinkOperator)
    bpy.utils.unregister_class(RemovePathNodeLinkOperator)
    
    forsaken_import_export.Unregister()

# -----------------------------------------------------------------------------
#
if __name__ == "__main__":
    register()
