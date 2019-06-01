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
        
# -----------------------------------------------------------------------------
# 
def draw(self, context):
    if bpy.context.scene.objects.active is None:
        return
        
    if len(context.selected_objects) == 0:
        return
    
    layout = self.layout
    obj = context.object
    
    row = layout.row()
    row.prop(obj, "actor")
    
    if obj.actor:
        row = layout.row()
        row.prop(obj, "actorType")
        row = layout.row()
        row.prop(obj, "levelGroup")
            
        if obj.actorType == 'PICKUP':
            row = layout.row()
            row.prop(obj, "pickupType")
            row = layout.row()
            row.prop(obj, "pickupGenType")
            row = layout.row()
            row.prop(obj, "pickupRegenType")
            row = layout.row()
            row.prop(obj, "pickupWaitTime")
            row = layout.row()
            row.prop(obj, "pickupGenDelay")
            row = layout.row()
            row.prop(obj, "pickupLifeSpan")
            box = layout.box()
            row = box.row()
            
            mods = obj.pickupTriggerMod
            
            row.template_list('UL_TriggerModProperties', "TriggerModList", mods, "trigger_mods", mods, "index", type='DEFAULT')
            row = box.row()
            row.operator("object.pickup_triggermod_add", text="Add Trigger Mod", icon='ZOOMIN')
            row.operator("object.pickup_triggermod_remove", text="Remove Selected", icon='X', emboss=True)
            
        elif obj.actorType == 'TRIGGERVAR':
            row = layout.row()
            row.prop(obj, "trigVarInitialValue")
            box = layout.box()
            row = box.row()
            
            vars = obj.trigVariables
            
            row.template_list('UL_TriggerVarProperties', "TriggerVariables", vars, "variables", vars, "index", type='DEFAULT')
            row = box.row()
            row.operator("object.trig_variables_add", text="Add Variable", icon='ZOOMIN')
            row.operator("object.trig_variables_remove", text="Remove Selected", icon='X', emboss=True)
            
        elif obj.actorType == 'TRIGGER':
            row = layout.row()
            trigger = obj.trigger
            row.prop(trigger, "variable")
            row = layout.row()
            row.prop(trigger, "compare")
            row = layout.row()
            row.prop(trigger, "value")
            
            row = layout.row()
            row.template_list('UL_ConditionNameProperties', "Conditions", trigger, "conditions", trigger, "condIndex", type='DEFAULT')
            row = layout.row()
            row.operator("object.cond_name_add", text="Add Condition", icon='ZOOMIN')
            row.operator("object.cond_name_remove", text="Remove Selected", icon='X', emboss=True)
            
        elif obj.actorType == 'TRIGGERCONDITION':
            cond = obj.triggerCondition
            row = layout.row()
            row.template_list('UL_TriggerNameProperties', "TriggerNames", cond, "triggers", cond, "trigIndex", type='DEFAULT')
            row = layout.row()
            row.operator("object.trig_name_add", text="Add Trigger", icon='ZOOMIN')
            row.operator("object.trig_name_remove", text="Remove Selected", icon='X', emboss=True)
            
            row = layout.row()
            row.template_list('UL_TriggerEventProperties', "Events", cond, "events", cond, "evIndex", type='DEFAULT')
            row = layout.row()
            row.operator("object.trig_events_add", text="Add Event", icon='ZOOMIN')
            row.operator("object.trig_events_remove", text="Remove Selected", icon='X', emboss=True)
            
        elif obj.actorType == 'PATHNODE':
            row = layout.row()
            row.prop(obj, "pathRadius")
            row = layout.row()
            row.prop(obj, "pathFlagDecision")
            row = layout.row()
            row.prop(obj, "pathFlagDropMines")
            row = layout.row()
            row.prop(obj, "pathFlagDisabled")
            row = layout.row()
            row.prop(obj, "pathFlagSnapToBGObj")
            row = layout.row()
            row.template_list('UL_PathLinkProperties', "Path Links", obj.pathLinkList, "links", obj.pathLinkList, "index", type='DEFAULT')
            row = layout.row()
            row.operator("object.path_link_add", text="Add Link", icon='ZOOMIN')
            row.operator("object.path_link_remove", text="Remove Selected", icon='X', emboss=True)
            
            box = layout.box()
            row = box.row()
            row.prop(obj, "pathNetwork1")
            row.prop(obj, "pathNetwork2")
            row.prop(obj, "pathNetwork3")
            row = box.row()
            row.prop(obj, "pathNetwork4")
            row.prop(obj, "pathNetwork5")
            row.prop(obj, "pathNetwork6")
            row = box.row()
            row.prop(obj, "pathNetwork7")
            row.prop(obj, "pathNetwork8")
            row.prop(obj, "pathNetwork9")
            row = box.row()
            row.prop(obj, "pathNetwork10")
            row.prop(obj, "pathNetwork11")
            row.prop(obj, "pathNetwork12")
            row = box.row()
            row.prop(obj, "pathNetwork13")
            row.prop(obj, "pathNetwork14")
            row.prop(obj, "pathNetwork15")
            row = box.row()
            row.prop(obj, "pathNetwork16")
            row.prop(obj, "pathNetwork17")
            row.prop(obj, "pathNetwork18")
            row = box.row()
            row.prop(obj, "pathNetwork19")
            row.prop(obj, "pathNetwork20")
            row.prop(obj, "pathNetwork21")
            row = box.row()
            row.prop(obj, "pathNetwork22")
            row.prop(obj, "pathNetwork23")
            row.prop(obj, "pathNetwork24")
            row = box.row()
            row.prop(obj, "pathNetwork25")
            row.prop(obj, "pathNetwork26")
            row.prop(obj, "pathNetwork27")
            row = box.row()
            row.prop(obj, "pathNetwork28")
            row.prop(obj, "pathNetwork29")
            row.prop(obj, "pathNetwork30")
            row = box.row()
            row.prop(obj, "pathNetwork31")
            
        elif obj.actorType == 'ENEMY':
            row = layout.row()
            row.prop(obj, "nmeDropPickup")
            row = layout.row()
            row.prop(obj, "nmeType")
            row = layout.row()
            row.prop_search(obj, "nmeFormationTarget", context.scene, "objects")
            row = layout.row()
            row.prop(obj.enemyGen, "genType")
            row = layout.row()
            row.prop(obj.enemyGen, "genDelay")
            
            mods = obj.pickupTriggerMod
            row = layout.row()
            row.template_list('UL_TriggerModProperties', "TriggerModList", mods, "trigger_mods", mods, "index", type='DEFAULT')
            row = layout.row()
            row.operator("object.pickup_triggermod_add", text="Add Trigger Mod", icon='ZOOMIN')
            row.operator("object.pickup_triggermod_remove", text="Remove Selected", icon='X', emboss=True)
            
            box = layout.box()
            row = box.row()
            row.prop(obj, "pathNetwork1")
            row.prop(obj, "pathNetwork2")
            row.prop(obj, "pathNetwork3")
            row = box.row()
            row.prop(obj, "pathNetwork4")
            row.prop(obj, "pathNetwork5")
            row.prop(obj, "pathNetwork6")
            row = box.row()
            row.prop(obj, "pathNetwork7")
            row.prop(obj, "pathNetwork8")
            row.prop(obj, "pathNetwork9")
            row = box.row()
            row.prop(obj, "pathNetwork10")
            row.prop(obj, "pathNetwork11")
            row.prop(obj, "pathNetwork12")
            row = box.row()
            row.prop(obj, "pathNetwork13")
            row.prop(obj, "pathNetwork14")
            row.prop(obj, "pathNetwork15")
            row = box.row()
            row.prop(obj, "pathNetwork16")
            row.prop(obj, "pathNetwork17")
            row.prop(obj, "pathNetwork18")
            row = box.row()
            row.prop(obj, "pathNetwork19")
            row.prop(obj, "pathNetwork20")
            row.prop(obj, "pathNetwork21")
            row = box.row()
            row.prop(obj, "pathNetwork22")
            row.prop(obj, "pathNetwork23")
            row.prop(obj, "pathNetwork24")
            row = box.row()
            row.prop(obj, "pathNetwork25")
            row.prop(obj, "pathNetwork26")
            row.prop(obj, "pathNetwork27")
            row = box.row()
            row.prop(obj, "pathNetwork28")
            row.prop(obj, "pathNetwork29")
            row.prop(obj, "pathNetwork30")
            row = box.row()
            row.prop(obj, "pathNetwork31")
            
        elif obj.actorType == 'RTLIGHT':
            row = layout.row()
            row.prop(obj, "rtLightType")
            
            row = layout.row()
            row.prop(obj, "rtLightRange")
            row = layout.row()
            row.prop(obj, "rtLightGenType")
            row = layout.row()
            row.prop(obj, "rtLightGenDelay")
            box = layout.box()
            row = box.row()
            row.prop(obj, "rtLightColor")
            
            if obj.rtLightType == 'LIGHT_FIXED':
                row = layout.row()
                row.prop(obj, "rtLightOnType")
                row = layout.row()
                row.prop(obj, "rtLightOffType")
                row = layout.row()
                row.prop(obj, "rtLightOnTime")
                row = layout.row()
                row.prop(obj, "rtLightOffTime")
                
            elif obj.rtLightType == 'LIGHT_FLICKERING':
                row = layout.row()
                row.prop(obj, "rtLightStayOnChance")
                row = layout.row()
                row.prop(obj, "rtLightStayOffChance")
                row = layout.row()
                row.prop(obj, "rtLightStayOnTime")
                row = layout.row()
                row.prop(obj, "rtLightStayOffTime")
                
            elif obj.rtLightType == 'LIGHT_PULSING':
                row = layout.row()
                row.prop(obj, "rtLightPulseType")
                row = layout.row()
                row.prop(obj, "rtLightOnTime")
                row = layout.row()
                row.prop(obj, "rtLightStayOnTime")
                row = layout.row()
                row.prop(obj, "rtLightOffTime")
                row = layout.row()
                row.prop(obj, "rtLightStayOffTime")
                
            elif obj.rtLightType == 'LIGHT_SPOT':
                row = layout.row()
                row.prop(obj, "rtLightCone")
                row = layout.row()
                row.prop(obj, "rtLightRotationPeriod")
                
        elif obj.actorType == 'LIGHT':
            box = layout.box()
            row = box.row()
            row.prop(obj, "rtLightColor")
            row = layout.row()
            row.prop(obj, "rtLightFallOff")
            row = layout.row()
            row.prop(obj, "rtLightIntensity")
            row = layout.row()
            row.prop(obj, "rtLightMixBlend")
            row = layout.row()
            row.prop(obj, "rtLightBackfaceCulling")
            row = layout.row()
            row.prop(obj, "rtLightAmbient")
                
        elif obj.actorType == 'BGOBJECT':
            row = layout.row()
            row.prop(obj, "bgoType")
            row = layout.row()
            row.prop(obj, "bgoCOBFile")
                
            if obj.bgoType == 'BGOTYPE_DOOR':
                row = layout.row()
                row.prop(obj, "bgoPlayerBump")
                row = layout.row()
                row.prop(obj, "bgoPlayerShot")
                row = layout.row()
                row.prop(obj, "bgoEnemyBump")
                row = layout.row()
                row.prop(obj, "bgoEnemyShot")
                row = layout.row()
                row.prop(obj, "bgoDoorLocked")
                row = layout.row()
                row.prop(obj, "bgoRequiredPickup")
                row = layout.row()
                row.prop(obj, "bgoDoorSfxType")
                box = layout.box()
            
                for mod in [{ "name": 'Open', "prop": obj.zoneAreaPII, "add": 'object.pii_triggermod_add', "rem": 'object.pii_triggermod_remove' },
                            { "name": 'Close', "prop": obj.zoneAreaPEN, "add": 'object.pen_triggermod_add', "rem": 'object.pen_triggermod_remove' },
                            { "name": 'Shot', "prop": obj.zoneAreaPEX, "add": 'object.pex_triggermod_add', "rem": 'object.pex_triggermod_remove' },
                            { "name": 'Bump', "prop": obj.zoneAreaPSH, "add": 'object.psh_triggermod_add', "rem": 'object.psh_triggermod_remove' }
                            ]:
                    row = box.row()
                    row.label(text=mod['name'])
                    row = box.row()
                    row.template_list('UL_TriggerModProperties', " ", mod['prop'], "trigger_mods", mod['prop'], "index", type='DEFAULT')
                    row = box.row()
                    row.operator(mod['add'], text="Add Trigger Mod", icon='ZOOMIN')
                    row.operator(mod['rem'], text="Remove Selected", icon='X', emboss=True)
                    
            if obj.bgoType == 'BGOTYPE_ANIM_ONEOFF':
                row = layout.row()
                row.prop(obj, "bgoDestroyAtEnd")
                row = layout.row()
                row.prop(obj, "bgoGenType")
                row = layout.row()
                row.prop(obj, "bgoGenDelay")
                box = layout.box()
            
                for mod in [{ "name": 'Player Shoots', "prop": obj.bgoShotEvent, "add": 'object.bgo_shot_triggermod_add', "rem": 'object.bgo_shot_triggermod_remove' },
                            { "name": 'Player Bump', "prop": obj.bgoBumpEvent, "add": 'object.bgo_bump_triggermod_add', "rem": 'object.bgo_bump_triggermod_remove' },
                            { "name": 'Anim Finishes', "prop": obj.bgoEndEvent, "add": 'object.bgo_end_triggermod_add', "rem": 'object.bgo_end_triggermod_remove' }
                            ]:
                    row = box.row()
                    row.label(text=mod['name'])
                    row = box.row()
                    row.template_list('UL_TriggerModProperties', " ", mod['prop'], "trigger_mods", mod['prop'], "index", type='DEFAULT')
                    row = box.row()
                    row.operator(mod['add'], text="Add Trigger Mod", icon='ZOOMIN')
                    row.operator(mod['rem'], text="Remove Selected", icon='X', emboss=True)
                    
            if obj.bgoType == 'BGOTYPE_ANIM_MULTISTEP':
                row = layout.row()
                row.prop(obj, "bgoPlayerBump")
                row = layout.row()
                row.prop(obj, "bgoPlayerShot")
                row = layout.row()
                row.prop(obj, "bgoEnemyBump")
                row = layout.row()
                row.prop(obj, "bgoEnemyShot")
                row = layout.row()
                row.prop(obj, "bgoDestroyAtEnd")
                row = layout.row()
                row.prop(obj, "bgoIntervals")
                row = layout.row()
                row.prop(obj, "bgoDamagePerInterval")
                box = layout.box()
            
                for mod in [{ "name": 'Player Shoots', "prop": obj.bgoShotEvent, "add": 'object.bgo_shot_triggermod_add', "rem": 'object.bgo_shot_triggermod_remove' },
                            { "name": 'Player Bump', "prop": obj.bgoBumpEvent, "add": 'object.bgo_bump_triggermod_add', "rem": 'object.bgo_bump_triggermod_remove' },
                            { "name": 'Anim Finishes', "prop": obj.bgoEndEvent, "add": 'object.bgo_end_triggermod_add', "rem": 'object.bgo_end_triggermod_remove' }
                            ]:
                    row = box.row()
                    row.label(text=mod['name'])
                    row = box.row()
                    row.template_list('UL_TriggerModProperties', " ", mod['prop'], "trigger_mods", mod['prop'], "index", type='DEFAULT')
                    row = box.row()
                    row.operator(mod['add'], text="Add Trigger Mod", icon='ZOOMIN')
                    row.operator(mod['rem'], text="Remove Selected", icon='X', emboss=True)
                
                
        elif obj.actorType == 'ZONEAREA':
            row = layout.row()
            row.prop(obj, "zoneAreaType")
            row = layout.row()
            row.prop(obj.zoneAreaGen, "genType")
            row = layout.row()
            row.prop(obj.zoneAreaGen, "genDelay")
            row = layout.row()
            row.prop(obj, "zoneAreaPrimaryPlayer")
            row = layout.row()
            row.prop(obj, "zoneAreaSecondaryPlayer")
            row = layout.row()
            row.prop(obj, "zoneAreaPrimaryNME")
            row = layout.row()
            row.prop(obj, "zoneAreaSecondaryNME")
            
            box = layout.box()
            
            for mod in [{ "name": 'Player Is In', "prop": obj.zoneAreaPII, "add": 'object.pii_triggermod_add', "rem": 'object.pii_triggermod_remove' },
                        { "name": 'Player Enters', "prop": obj.zoneAreaPEN, "add": 'object.pen_triggermod_add', "rem": 'object.pen_triggermod_remove' },
                        { "name": 'Player Exits', "prop": obj.zoneAreaPEX, "add": 'object.pex_triggermod_add', "rem": 'object.pex_triggermod_remove' },
                        { "name": 'Player Shoots', "prop": obj.zoneAreaPSH, "add": 'object.psh_triggermod_add', "rem": 'object.psh_triggermod_remove' },
                        { "name": 'Enemy Is In', "prop": obj.zoneAreaEII, "add": 'object.eii_triggermod_add', "rem": 'object.eii_triggermod_remove' },
                        { "name": 'Enemy Enters', "prop": obj.zoneAreaEEN, "add": 'object.een_triggermod_add', "rem": 'object.een_triggermod_remove' },
                        { "name": 'Enemy Exits', "prop": obj.zoneAreaEEX, "add": 'object.eex_triggermod_add', "rem": 'object.eex_triggermod_remove' },
                        { "name": 'Enemy Shoots', "prop": obj.zoneAreaESH, "add": 'object.esh_triggermod_add', "rem": 'object.esh_triggermod_remove' }
                        ]:
                row = box.row()
                row.label(text=mod['name'])
                row = box.row()
                row.template_list('UL_TriggerModProperties', " ", mod['prop'], "trigger_mods", mod['prop'], "index", type='DEFAULT')
                row = box.row()
                row.operator(mod['add'], text="Add Trigger Mod", icon='ZOOMIN')
                row.operator(mod['rem'], text="Remove Selected", icon='X', emboss=True)
                
        elif obj.actorType == 'WATER':
            row = layout.row()
            row.prop(obj, "watTexture")
            row = layout.row()
            row.prop(obj, "watColor")
            row = layout.row()
            row.prop(obj, "watMaxLevel")
            row = layout.row()
            row.prop(obj, "watMinLevel")
            row = layout.row()
            row.prop(obj, "watFillRate")
            row = layout.row()
            row.prop(obj, "watDrainRate")
            row = layout.row()
            row.prop(obj, "watDensity")
            row = layout.row()
            row.prop(obj, "watMaxWaveSize")
            row = layout.row()
            row.prop(obj, "watDamage")
            box = layout.box()
            
            for mod in [{ "name": 'On Fill', "prop": obj.zoneAreaPII, "add": 'object.pii_triggermod_add', "rem": 'object.pii_triggermod_remove' },
                        { "name": 'On Drain', "prop": obj.zoneAreaPEN, "add": 'object.pen_triggermod_add', "rem": 'object.pen_triggermod_remove' }
                        ]:
                row = box.row()
                row.label(text=mod['name'])
                row = box.row()
                row.template_list('UL_TriggerModProperties', " ", mod['prop'], "trigger_mods", mod['prop'], "index", type='DEFAULT')
                row = box.row()
                row.operator(mod['add'], text="Add Trigger Mod", icon='ZOOMIN')
                row.operator(mod['rem'], text="Remove Selected", icon='X', emboss=True)
                
        elif obj.actorType == 'SPOTFX':
            row = layout.row()
            row.prop(obj.fxGen, "genType")
            row = layout.row()
            row.prop(obj.fxGen, "genDelay")
            row = layout.row()
            row.prop(obj, "fxColor")
            row = layout.row()
            row.prop(obj, "fxActiveDelay")
            row = layout.row()
            row.prop(obj, "fxInactiveDelay")
            row = layout.row()
            row.prop(obj, "fxPrimaryID")
            row = layout.row()
            row.prop(obj, "fxSecondaryID")
            row = layout.row()
            row.prop(obj, "fxSFX")
            row = layout.row()
            row.prop(obj, "fxVolume")
            row = layout.row()
            row.prop(obj, "fxSpeed")
            row = layout.row()
            row.prop(obj, "fxType")
            row = layout.row()
            row.prop(obj, "sfxType")
            
        elif obj.actorType == 'EXTFORCE':
            row = layout.row()
            row.prop(obj, "zoneAreaType")
            row = layout.row()
            row.prop(obj, "efType")
            row = layout.row()
            row.prop(obj, "efMinForce")
            row = layout.row()
            row.prop(obj, "efMaxForce")
            row = layout.row()
            row.prop(obj, "efRange")
            row = layout.row()
            row.prop(obj, "efActive")
            
        elif obj.actorType == 'ANIMDEF':
            defs = obj.animDefs
            row = layout.row()
            row.prop(obj, "animTextureWidth")
            row = layout.row()
            row.prop(obj, "animTextureHeight")
            
            box = layout.box()
            row = box.row()
            
            row.template_list('UL_AnimDefProperties', "Anim Definitions", defs, "defs", defs, "index", type='DEFAULT')
            row = box.row()
            row.operator("object.anim_def_add", text="Add Anim Definition", icon='ZOOMIN')
            row.operator("object.anim_def_remove", text="Remove Selected", icon='X', emboss=True)
            
        elif obj.actorType == 'ANIMCOMMAND':
            ac = obj.forsakenAnimCmds
            box = layout.box()
            row = box.row()
            
            row.template_list('UL_ForsakenAnimCommandProperties', "Anim Commands", ac, "commands", ac, "index", type='DEFAULT')
            row = box.row()
            row.operator("object.forsaken_anim_cmds_add", text="Add Anim Command", icon='ZOOMIN')
            row.operator("object.forsaken_anim_cmds_remove", text="Remove Selected", icon='X', emboss=True)
            
        elif obj.actorType == 'ANIMINST':
            row = layout.row()
            row.prop(obj, "animState")
            row = layout.row()
            row.prop(obj, "animationTexture")
            row = layout.row()
            row.prop_search(obj, "animationCommands", context.scene, "objects")
            row = layout.row()
            row.prop_search(obj, "animationDefs", context.scene, "objects")
    else:
        row = layout.row()
        row.prop(obj, "groupWaterType")
        row = layout.row()
        row.prop(obj, "groupCausticColor")
        row = layout.row()
        row.prop(obj, "groupSoundDistScale")
