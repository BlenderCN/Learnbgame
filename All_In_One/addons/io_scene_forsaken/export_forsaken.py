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
import bmesh
import mathutils
import bpy_extras.io_utils

from progress_report import ProgressReport, ProgressReportSubstep

# -----------------------------------------------------------------------------
#
def name_compat(name):
    if name is None:
        return 'None'
    else:
        return name
      
# -----------------------------------------------------------------------------
#  
def get_enum_type(enumTypes, enumStr):
    for e in enumTypes[1]['items']:
        if e[0] == enumStr:
            return e[3]
            
    return 0

# -----------------------------------------------------------------------------
#
def object_is_actor(obj):
    return obj.actor == True

# -----------------------------------------------------------------------------
#    
def get_group_axis(groupObj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    if groupObj.get("orientation") is None:
        axis = EXPORT_GLOBAL_MATRIX * Vector((0.0, 0.0, 1.0))
        axis.normalize()
        return axis
        
    vectors = groupObj["orientation"].split(" ")
    
    axis = EXPORT_GLOBAL_MATRIX * Vector((float(vectors[0]), float(vectors[1]), float(vectors[2])))
    axis.normalize()
    return axis
    
# -----------------------------------------------------------------------------
#    
def get_group_water(groupObj):
    if groupObj.get("water") is None:
        return 0
        
    if groupObj["water"] == 1:
        return 1
        
    return 0
  
# -----------------------------------------------------------------------------
#      
def get_sound_distance_scale(groupObj):
    if groupObj.get("sounddistancescale") is None:
        return 1.0
        
    return groupObj["sounddistancescale"]

# -----------------------------------------------------------------------------
#
def parse_pickup(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    fw('pickup\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    genType %i\n'           % get_enum_type(bpy.types.Object.pickupGenType, obj.pickupGenType))
    fw('    regenType %i\n'         % get_enum_type(bpy.types.Object.pickupRegenType, obj.pickupRegenType))
    fw('    type %i\n'              % get_enum_type(bpy.types.Object.pickupType, obj.pickupType))
    fw('    waitTime %f\n'          % obj.pickupWaitTime)
    fw('    generationDelay %f\n'   % obj.pickupGenDelay)
    fw('    lifeSpan %f\n'          % obj.pickupLifeSpan)
    parse_triggerMod(fw, obj.pickupTriggerMod, 0)
    fw('}\n\n')
     
# -----------------------------------------------------------------------------
#
def get_network_flags(obj):
    bit = 0
    
    for i in range(31):
        if obj.get("pathNetwork{0}".format(i+1)) is None:
            continue
            
        if obj["pathNetwork{0}".format(i+1)] == True:
            bit = bit | (1 << i)
            
    return bit
    
# -----------------------------------------------------------------------------
#
def parse_rtlight(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    type = get_enum_type(bpy.types.Object.rtLightType, obj.rtLightType)
    
    rotation = obj.rotation_euler.to_matrix()
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('rtlight\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    type %i\n'              % type)
    fw('    range %f\n'             % obj.rtLightRange)
    fw('    red %f\n'               % obj.rtLightColor[0])
    fw('    green %f\n'             % obj.rtLightColor[1])
    fw('    blue %f\n'              % obj.rtLightColor[2])
    fw('    genType %i\n'           % get_enum_type(bpy.types.Object.rtLightGenType, obj.rtLightGenType))
    fw('    generationDelay %f\n'   % obj.rtLightGenDelay)
    
    if type == 0:
        fw('    onType %i\n'        % get_enum_type(bpy.types.Object.rtLightOnType, obj.rtLightOnType))
        fw('    offType %i\n'       % get_enum_type(bpy.types.Object.rtLightOffType, obj.rtLightOffType))
        fw('    onTime %f\n'        % obj.rtLightOnTime)
        fw('    offTime %f\n'       % obj.rtLightOffTime)
    elif type == 1:
        fw('    pulseType %i\n'     % get_enum_type(bpy.types.Object.rtLightPulseType, obj.rtLightPulseType))
        fw('    onTime %f\n'        % obj.rtLightOnTime)
        fw('    stayOnTime %f\n'    % obj.rtLightStayOnTime)
        fw('    offTime %f\n'       % obj.rtLightOffTime)
        fw('    stayOffTime %f\n'   % obj.rtLightStayOffTime)
    elif type == 2:
        fw('    stayOnChance %f\n'  % obj.rtLightStayOnChance)
        fw('    stayOffChance %f\n' % obj.rtLightStayOffChance)
        fw('    stayOnTime %f\n'    % obj.rtLightStayOnTime)
        fw('    stayOffTime %f\n'   % obj.rtLightStayOffTime)
    elif type == 3:
        fw('    cone %f\n'          % obj.rtLightCone)
        fw('    rotationPeriod %f\n'% obj.rtLightRotationPeriod)
        fw('    direction %f %f %f\n'   % direction[:])
        fw('    upVector %f %f %f\n'    % upVector[:])
    
    fw('}\n\n')

# -----------------------------------------------------------------------------
#
def parse_bgobject(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    type = get_enum_type(bpy.types.Object.bgoType, obj.bgoType)
    rotation = obj.rotation_euler.to_matrix()
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('bgobject\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('    type %i\n'              % type)
    fw('    cobFile \"%s\"\n'       % obj.bgoCOBFile)
    if type == 1:
        fw('    requirePickup %i\n' % obj.get("requirepickup", -1))
        
        openedBy = 0
        if obj.bgoPlayerBump:
            openedBy |= 1
        if obj.bgoPlayerShot:
            openedBy |= 2
        if obj.bgoEnemyBump:
            openedBy |= 4
        if obj.bgoEnemyShot:
            openedBy |= 8
            
        fw('    openedBy %i\n'      % openedBy)
        fw('    locked %i\n'        % obj.bgoDoorLocked)
        fw('    doorSFXType %i\n'   % get_enum_type(bpy.types.Object.bgoDoorSfxType, obj.bgoDoorSfxType))
        fw('    requirePickup %i\n' % get_enum_type(bpy.types.Object.bgoRequiredPickup, obj.bgoRequiredPickup))
        parse_triggerMod(fw, obj.zoneAreaPII, 0)
        parse_triggerMod(fw, obj.zoneAreaPEN, 1)
        parse_triggerMod(fw, obj.zoneAreaPEX, 2)
        parse_triggerMod(fw, obj.zoneAreaPSH, 3)
    elif type == 2:
        fw('    genType %i\n'       % get_enum_type(bpy.types.Object.bgoGenType, obj.bgoGenType))
        fw('    delay %f\n'         % obj.bgoGenDelay)
    elif type == 3:
        parse_triggerMod(fw, obj.bgoShotEvent, 0)
        parse_triggerMod(fw, obj.bgoBumpEvent, 1)
        parse_triggerMod(fw, obj.bgoEndEvent, 2)
        openedBy = 0
        if obj.bgoPlayerBump:
            openedBy |= 1
        if obj.bgoPlayerShot:
            openedBy |= 2
        if obj.bgoEnemyBump:
            openedBy |= 4
        if obj.bgoEnemyShot:
            openedBy |= 8
            
        fw('    openedBy %i\n'      % openedBy)
        fw('    destroyAtEnd %i\n'  % obj.bgoDestroyAtEnd)
        fw('    intervals %i\n'     % obj.bgoIntervals)
        fw('    damagePerInterval %f\n' % obj.bgoDamagePerInterval)
    elif type == 4:
        parse_triggerMod(fw, obj.bgoShotEvent, 0)
        parse_triggerMod(fw, obj.bgoBumpEvent, 1)
        parse_triggerMod(fw, obj.bgoEndEvent, 2)
        fw('    genType %i\n'       % get_enum_type(bpy.types.Object.bgoGenType, obj.bgoGenType))
        fw('    delay %f\n'         % obj.bgoGenDelay)
        fw('    destroyAtEnd %i\n'  % obj.bgoDestroyAtEnd)
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_triggerVar(fw, obj):
    fw('trigger_variables %i\n' % len(obj.trigVariables.variables))
    fw('{\n')
    for var in obj.trigVariables.variables:
        fw('    { ')
        fw('name \"%s\" ' % var.variable)
        fw('initialValue %i ' % var.initialValue)
        fw(' }\n')
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_trigger(fw, obj):
    fw('trigger\n')
    fw('{\n')
    fw('    name \"%s\"\n' % obj.name)
    fw('    variable \"%s\"\n' % obj.trigger.variable)
    fw('    compare %i\n' % get_enum_type(bpy.types.TriggersPropertyGroup.compare, obj.trigger.compare))
    fw('    value %i\n' % obj.trigger.value)
    fw('    conditions %i {' % len(obj.trigger.conditions))
    for cond in obj.trigger.conditions:
        fw(' \"%s\"' % cond.conditionName)
    fw(' }\n')
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_condition(fw, obj):
    fw('condition\n')
    fw('{\n')
    fw('    name \"%s\"\n' % obj.name)
    fw('    triggers %i {' % len(obj.triggerCondition.triggers))
    for trig in obj.triggerCondition.triggers:
        fw(' \"%s\"' % trig.triggerName)
    fw(' }\n')
    fw('    events %i\n' % len(obj.triggerCondition.events))
    fw('    {\n')
    for ev in obj.triggerCondition.events:
        fw('        {')
        fw(' event %i' % get_enum_type(bpy.types.TriggerEventPropertyGroup.event, ev.event))
        fw(' param1 \"%s\"' % ev.value1)
        fw(' }\n')
    fw('    }\n')
    fw('}\n\n')
     
# -----------------------------------------------------------------------------
#
def parse_triggerMod(fw, triggerMod, typeSlot):
    fw('    triggerMod %i ' % typeSlot)
    fw('%i\n' % len(triggerMod.trigger_mods))
    fw('    {\n')
    for mod in triggerMod.trigger_mods:
        fw('        {')
        fw(' variable \"%s\"' % mod.variable)
        fw(' value %i' % mod.value)
        fw(' delay %f' % mod.delay)
        fw(' operand %i' % get_enum_type(bpy.types.TriggerModPropertyGroup.operand, mod.operand))
        fw(' }\n')
    fw('    }\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_zoneAreas(fw, obj, scene, matrix):
    from mathutils import Vector
    from io_scene_forsaken import forsaken_utils
    
    try:
        mesh = obj.to_mesh(scene, True, 'PREVIEW')
    except RuntimeError:
        mesh = None

    if mesh is None:
        return
        
    mesh.transform(matrix * obj.matrix_world)
    #forsaken_utils.mesh_triangulate(mesh)
    if not mesh.tessfaces and mesh.polygons:
        mesh.calc_tessface()
        
    fw('zoneArea\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    origin %f %f %f\n'      % Vector(matrix * Vector(obj.location))[:])
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    type %i\n'              % get_enum_type(bpy.types.Object.zoneAreaType, obj.zoneAreaType))
    fw('    genType %i\n'           % get_enum_type(bpy.types.GeneratePropertyGroup.genType, obj.zoneAreaGen.genType))
    fw('    genDelay %f\n'          % obj.zoneAreaGen.genDelay)
    fw('    playerPrimary %i\n'     % get_enum_type(bpy.types.Object.zoneAreaPrimaryPlayer, obj.zoneAreaPrimaryPlayer))
    fw('    playerSecondary %i\n'   % get_enum_type(bpy.types.Object.zoneAreaSecondaryPlayer, obj.zoneAreaSecondaryPlayer))
    fw('    enemyPrimary %i\n'      % get_enum_type(bpy.types.Object.zoneAreaPrimaryNME, obj.zoneAreaPrimaryNME))
    fw('    enemySecondary %i\n'    % get_enum_type(bpy.types.Object.zoneAreaSecondaryNME, obj.zoneAreaSecondaryNME))
    
    fw('    geometry %i\n' % len(mesh.polygons))
    fw('    {');
    for i, f in enumerate(mesh.polygons):
        f_verts = f.vertices
        
        fw('\n        %i ' % len(f_verts))
        fw('\n        {');
        
        for j, vidx in enumerate(f_verts):
            v = mesh.vertices[vidx]  
            fw('\n            %.6f %.6f %.6f ' % v.co[:])
        fw('\n        }\n')
        
    fw('\n    }\n')
    
    parse_triggerMod(fw, obj.zoneAreaPII, 0)
    parse_triggerMod(fw, obj.zoneAreaPEN, 1)
    parse_triggerMod(fw, obj.zoneAreaPEX, 2)
    parse_triggerMod(fw, obj.zoneAreaPSH, 3)
    parse_triggerMod(fw, obj.zoneAreaEII, 4)
    parse_triggerMod(fw, obj.zoneAreaEEN, 5)
    parse_triggerMod(fw, obj.zoneAreaEEX, 6)
    parse_triggerMod(fw, obj.zoneAreaESH, 7)
    
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_pathNode(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    flags = 0
    if obj.pathFlagDecision == True:
        flags = flags | (1 << 0)
    if obj.pathFlagDropMines == True:
        flags = flags | (1 << 1)
    if obj.pathFlagDisabled == True:
        flags = flags | (1 << 5)
    if obj.pathFlagSnapToBGObj == True:
        flags = flags | (1 << 6)
    
    fw('pathNode\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    radius %f\n'            % obj.pathRadius)
    fw('    netMask %i\n'           % get_network_flags(obj))
    fw('    pathFlags %i\n'         % flags)
    fw('    links %i {'             % len(obj.pathLinkList.links))
    
    for pl in obj.pathLinkList.links:
        fw(' \"%s\"' % pl.linkName)
    fw(' }\n')
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_enemy(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    rotation = obj.rotation_euler.to_matrix()
    
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('enemy\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('    dropPickup %i\n'        % get_enum_type(bpy.types.Object.nmeDropPickup, obj.nmeDropPickup))
    fw('    nmeType %i\n'           % get_enum_type(bpy.types.Object.nmeType, obj.nmeType))
    fw('    nmeNetwork %i\n'        % get_network_flags(obj))
    fw('    formationLink \"%s\"\n' % obj.nmeFormationTarget)
    fw('    genType %i\n'           % get_enum_type(bpy.types.GeneratePropertyGroup.genType, obj.enemyGen.genType))
    fw('    genDelay %f\n'          % obj.enemyGen.genDelay)
    parse_triggerMod(fw, obj.pickupTriggerMod, 0)
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_playerStart(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    rotation = obj.rotation_euler.to_matrix()
    
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('playerStart\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_restartPoint(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    rotation = obj.rotation_euler.to_matrix()
    
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('restartPoint\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('}\n\n')
      
# -----------------------------------------------------------------------------
#
def parse_water(fw, obj, EXPORT_GLOBAL_MATRIX, scene):
    from mathutils import Vector
    
    try:
        mesh = obj.to_mesh(scene, True, 'PREVIEW')
    except RuntimeError:
        mesh = None
        
    if mesh is None:
        return
        
    has_uv = bool(mesh.tessface_uv_textures)
    
    if has_uv:
        active_uv_layer = mesh.tessface_uv_textures.active
        if not active_uv_layer:
            has_uv = False
        else:
            active_uv_layer = active_uv_layer.data
                    
    if has_uv == False:
        return
        
    mesh.transform(EXPORT_GLOBAL_MATRIX * obj.matrix_world)
    uv_texture = mesh.uv_textures.active.data[:]
    uv = active_uv_layer[0]
    uv = uv.uv1, uv.uv2, uv.uv3, uv.uv4
    
    sizeX = 0.0
    sizeY = 0.0
    
    maxX = -100000.0
    minX =  100000.0
    maxY = -100000.0
    minY =  100000.0
    
    for i in range(len(mesh.vertices)):
        vert = mesh.vertices[i].co
        
        if vert.x > maxX:
            maxX = vert.x
        if vert.x < minX:
            minX = vert.x
        if vert.y > maxY:
            maxY = vert.y
        if vert.y < minY:
            minY = vert.y
            
    sizeX = maxX - minX
    sizeY = maxY - minY
    
    minU =  100000.0
    maxU = -100000.0
    minV =  100000.0
    maxV = -100000.0
    
    for i in range(4):
        uvcoord = uv[i][0], uv[i][1]
        if uvcoord[0] > maxU:
            maxU = uvcoord[0]
        if uvcoord[0] < minU:
            minU = uvcoord[0]
        if uvcoord[1] > maxV:
            maxV = uvcoord[1]
        if uvcoord[1] < minV:
            minV = uvcoord[1]
                
    fw('water\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    waterTexture \"%s\"\n'  % obj.watTexture)
    fw('    sizeX %f\n'             % sizeX)
    fw('    sizeY %f\n'             % sizeY)
    fw('    sizeU1 %f\n'            % minU)
    fw('    sizeV1 %f\n'            % (1.0 - minV))
    fw('    sizeU2 %f\n'            % maxU)
    fw('    sizeV2 %f\n'            % (1.0 - maxV))
    fw('    red %f\n'               % obj.watColor[0])
    fw('    green %f\n'             % obj.watColor[1])
    fw('    blue %f\n'              % obj.watColor[2])
    fw('    watMaxLevel %f\n'       % obj.watMaxLevel)
    fw('    watMinLevel %f\n'       % obj.watMinLevel)
    fw('    watFillRate %f\n'       % obj.watFillRate)
    fw('    watDrainRate %f\n'      % obj.watDrainRate)
    fw('    watDensity %f\n'        % obj.watDensity)
    fw('    watMaxWaveSize %f\n'    % obj.watMaxWaveSize)
    fw('    watDamage %f\n'         % obj.watDamage)
    
    parse_triggerMod(fw, obj.zoneAreaPII, 0)
    parse_triggerMod(fw, obj.zoneAreaPEN, 1)
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_spotfx(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    rotation = obj.rotation_euler.to_matrix()
    
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('spotFx\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('    genType %i\n'           % get_enum_type(bpy.types.GeneratePropertyGroup.genType, obj.fxGen.genType))
    fw('    genDelay %f\n'          % obj.fxGen.genDelay)
    fw('    red %f\n'               % obj.fxColor[0])
    fw('    green %f\n'             % obj.fxColor[1])
    fw('    blue %f\n'              % obj.fxColor[2])
    fw('    activeDelay %f\n'       % obj.fxActiveDelay)
    fw('    inactiveDelay %f\n'     % obj.fxInactiveDelay)
    fw('    primaryID %i\n'         % get_enum_type(bpy.types.Object.fxPrimaryID, obj.fxPrimaryID))
    fw('    secondaryID %i\n'       % get_enum_type(bpy.types.Object.fxSecondaryID, obj.fxSecondaryID))
    fw('    SFX \"%s\"\n'           % obj.fxSFX)
    fw('    volume %f\n'            % obj.fxVolume)
    fw('    speed %f\n'             % obj.fxSpeed)
    fw('    type %i\n'              % get_enum_type(bpy.types.Object.fxType, obj.fxType))
    fw('    sfxType %i\n'           % get_enum_type(bpy.types.Object.sfxType, obj.sfxType))
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parseExtForce(fw, obj, scene, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    from io_scene_forsaken import forsaken_utils
    
    try:
        mesh = obj.to_mesh(scene, True, 'PREVIEW')
    except RuntimeError:
        mesh = None

    if mesh is None:
        return
        
    mesh.transform(EXPORT_GLOBAL_MATRIX * obj.matrix_world)
    #forsaken_utils.mesh_triangulate(mesh)
    if not mesh.tessfaces and mesh.polygons:
        mesh.calc_tessface()
        
    rotation = obj.rotation_euler.to_matrix()
    
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    iActive = 0
    if obj.efActive == True:
        iActive = 1
        
    fw('extForce\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    type %i\n'              % get_enum_type(bpy.types.Object.zoneAreaType, obj.zoneAreaType))
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('    forceType %i\n'         % get_enum_type(bpy.types.Object.efType, obj.efType))
    fw('    minForce %f\n'          % obj.efMinForce)
    fw('    maxForce %f\n'          % obj.efMaxForce)
    fw('    range %f\n'             % obj.efRange)
    fw('    active %i\n'            % iActive)
    
    fw('    geometry %i\n'          % len(mesh.polygons))
    fw('    {');
    for i, f in enumerate(mesh.polygons):
        f_verts = f.vertices
        
        fw('\n        %i ' % len(f_verts))
        fw('\n        {');
        
        for j, vidx in enumerate(f_verts):
            v = mesh.vertices[vidx]  
            fw('\n            %.6f %.6f %.6f ' % v.co[:])
        fw('\n        }\n')
        
    fw('\n    }\n')
    
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_camera(fw, obj, EXPORT_GLOBAL_MATRIX):
    from mathutils import Vector
    
    rotation = obj.rotation_euler.to_matrix()
    
    direction = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 1.0, 0.0))))
    direction.normalize()
    
    upVector = Vector(EXPORT_GLOBAL_MATRIX * Vector(rotation * Vector((0.0, 0.0, 1.0))))
    upVector.normalize()
    
    fw('camera\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    origin %f %f %f\n'      % Vector(EXPORT_GLOBAL_MATRIX * Vector(obj.location))[:])
    fw('    direction %f %f %f\n'   % direction[:])
    fw('    upVector %f %f %f\n'    % upVector[:])
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_animDef(fw, obj):

    fw('animDef\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    defs %i\n'              % len(obj.animDefs.defs))
    fw('    {\n')
    for ad in obj.animDefs.defs:
        fw('        {')
        fw(' %f' % (ad.animDefStartX / obj.animTextureWidth))
        fw(' %f' % (ad.animDefStartY / obj.animTextureHeight))
        fw(' %f' % (ad.animDefEndX / obj.animTextureWidth))
        fw(' %f' % (ad.animDefEndY / obj.animTextureHeight))
        fw(' }\n')
    fw('    }\n')
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_animCmds(fw, obj):

    fw('animCmds\n')
    fw('{\n')
    fw('    name \"%s\"\n'          % obj.name)
    fw('    group \"%s\"\n'         % obj.levelGroup)
    fw('    cmds %i\n'              % len(obj.forsakenAnimCmds.commands))
    fw('    {\n')
    for ac in obj.forsakenAnimCmds.commands:
        fw('        {')
        fw(' %i' % get_enum_type(bpy.types.ForsakenAnimCommandPropertyGroup.command, ac.command))
        fw(' \"%s\"' % ac.param)
        fw(' }\n')
    fw('    }\n')
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_animInst(fw, obj):

    fw('animInst\n')
    fw('{\n')
    fw('    name \"%s\"\n'              % obj.name)
    fw('    group \"%s\"\n'             % obj.levelGroup)
    fw('    animationCommands \"%s\"\n' % obj.animationCommands)
    fw('    animationDefs \"%s\"\n'     % obj.animationDefs)
    fw('    animationTexture \"%s\"\n'  % obj.animationTexture)
    fw('    animState %i\n'             % get_enum_type(bpy.types.Object.animState, obj.animState))
    fw('}\n\n')
    
# -----------------------------------------------------------------------------
#
def parse_actor(fw, obj, EXPORT_GLOBAL_MATRIX, scene):
    if obj.actorType == 'PICKUP':
        parse_pickup(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'RTLIGHT':
        parse_rtlight(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'BGOBJECT':
        parse_bgobject(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'TRIGGERVAR':
        parse_triggerVar(fw, obj)
    elif obj.actorType == 'TRIGGER':
        parse_trigger(fw, obj)
    elif obj.actorType == 'TRIGGERCONDITION':
        parse_condition(fw, obj)
    elif obj.actorType == 'ZONEAREA':
        parse_zoneAreas(fw, obj, scene, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'PATHNODE':
        parse_pathNode(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'ENEMY':
        parse_enemy(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'PLAYERSTART':
        parse_playerStart(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'RESTARTPOINT':
        parse_restartPoint(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'WATER':
        parse_water(fw, obj, EXPORT_GLOBAL_MATRIX, scene)
    elif obj.actorType == 'SPOTFX':
        parse_spotfx(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'EXTFORCE':
        parseExtForce(fw, obj, scene, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'CAMERA':
        parse_camera(fw, obj, EXPORT_GLOBAL_MATRIX)
    elif obj.actorType == 'ANIMCOMMAND':
        parse_animCmds(fw, obj)
    elif obj.actorType == 'ANIMDEF':
        parse_animDef(fw, obj)
    elif obj.actorType == 'ANIMINST':
        parse_animInst(fw, obj)
        
# -----------------------------------------------------------------------------
# Function to write out the text file      
def write_file(filepath, objects, scene,
               EXPORT_GLOBAL_MATRIX=None,
               EXPORT_PATH_MODE='AUTO',
               progress=ProgressReport(),
               ):
    from io_scene_forsaken import forsaken_utils
               
    if EXPORT_GLOBAL_MATRIX is None:
        EXPORT_GLOBAL_MATRIX = mathutils.Matrix()
        
    # -----------------------------------------------------------------------------
    # create a new file
    file = open(filepath, "w", encoding="utf8", newline="\n")
    fw = file.write
    
    fw('// Generated Forsaken Level Data for Kex Engine\n')
    fw('// DO NOT MODIFY!\n\n')
    
    # -----------------------------------------------------------------------------
    # iterate each scene object
    for i, ob_main in enumerate(objects):
        if ob_main.parent and ob_main.parent.dupli_type in {'VERTS', 'FACES'}:
            continue
            
        obs = [(ob_main, ob_main.matrix_world)]

        # -----------------------------------------------------------------------------
        # iterate every mesh
        for ob, ob_mat in obs:
            
            if object_is_actor(ob):
                parse_actor(fw, ob, EXPORT_GLOBAL_MATRIX, scene)
                continue
                
            name1 = ob.name
            name2 = ob.data.name
            #if name1 == name2:
            #    obnamestring = name_compat(name1)
            #else:
            #    obnamestring = '%s_%s' % (name_compat(name1), name_compat(name2))
            obnamestring = name_compat(name1)
                
            # -----------------------------------------------------------------------------
            # set the name of this group
            fw('group \"%s\"' % obnamestring)
            fw(' // %i\n' % i)
            
            axis = get_group_axis(ob, EXPORT_GLOBAL_MATRIX)
            
            fw('orientation %.6f %.6f %.6f\n'   % axis[:])
            fw('waterType %i\n'                 % get_enum_type(bpy.types.Object.groupWaterType, ob.groupWaterType))
            fw('soundDistanceScale %f\n'        % ob.groupSoundDistScale);
            fw('caustics_red %f\n'              % ob.groupCausticColor[0])
            fw('caustics_green %f\n'            % ob.groupCausticColor[1])
            fw('caustics_blue %f\n'             % ob.groupCausticColor[2])
                                
            try:
                mesh = ob.to_mesh(scene, True, 'PREVIEW')
            except RuntimeError:
                mesh = None

            if mesh is None:
                continue
                
            #print('processing group ', ob.name)

            mesh.transform(EXPORT_GLOBAL_MATRIX * ob_mat)
            #forsaken_utils.mesh_triangulate(mesh)
            
            if not mesh.tessfaces and mesh.polygons:
                mesh.calc_tessface()
            
            faceuv = len(mesh.uv_textures) > 0
            has_materials = len(mesh.materials) > 0
            
            if faceuv:
                uv_texture = mesh.uv_textures.active.data[:]
                uv_layer = mesh.uv_layers.active.data[:]
                
            mesh_verts = mesh.vertices
            
            has_uv = bool(mesh.tessface_uv_textures)
            has_vcol = bool(mesh.tessface_vertex_colors)
            
            use_uv_coords = True
            
            # -----------------------------------------------------------------------------
            # get uv layer
            if has_uv:
                active_uv_layer = mesh.tessface_uv_textures.active
                if not active_uv_layer:
                    has_uv = False
                else:
                    active_uv_layer = active_uv_layer.data
                    
            # -----------------------------------------------------------------------------
            # get color layer
            if has_vcol:
                active_col_layer = mesh.tessface_vertex_colors.active
                if not active_col_layer:
                    has_vcol = False
                else:
                    active_col_layer = active_col_layer.data
                    
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
                scene.objects.active = ob
                me = ob.data
                ob.select = True
                bpy.ops.object.mode_set(mode='EDIT')
                
                bm = bmesh.from_edit_mesh(me)
                bm.faces.ensure_lookup_table()
                
                ignoreBspLayer = bm.faces.layers.int.get("ignore_bsp")
                transparentLayer = bm.faces.layers.int.get("transparent")
                animInstanceLayer = bm.faces.layers.string.get("animInstance")
                    
                # -----------------------------------------------------------------------------
                # iterate polygons
                for i, f in enumerate(mesh.polygons):
                    f_verts = f.vertices
                    
                    bFixFace = False
                    
                    # for some bizzare reason, quads referencing vertex indexes of zero results in
                    # the UV and color indexes being in the incorrect order. this will check for this
                    # bug and correct it when writing out the face information
                    for j, vidx in enumerate(f_verts):
                        # check only if zero vertex index is the 3rd or 4th indice
                        if vidx == 0 and j >= 2 and len(f_verts) >= 4:
                            bFixFace = True
                            break
                            
                    if uv_texture[f.index].image is None or has_uv == False:
                        continue
                    
                    if has_uv:
                        uv = active_uv_layer[i]
                        uv = uv.uv1, uv.uv2, uv.uv3, uv.uv4
                        
                    if has_vcol:
                        col = active_col_layer[i]
                        col = col.color1[:], col.color2[:], col.color3[:], col.color4[:]
                        
                    # -----------------------------------------------------------------------------
                    # write out a new face block
                    fw('face %i ' % len(f_verts))
                    fw('\"%s\" ' % uv_texture[f.index].image.filepath)
                    
                    if ignoreBspLayer is not None or transparentLayer is not None or animInstanceLayer is not None:
                        bmf = bm.faces[f.index]
                        if ignoreBspLayer is None:
                            fw('0 ')
                        else:
                            fw('%i ' % bmf[ignoreBspLayer])
                        
                        if transparentLayer is None:
                            fw('0 ')
                        else:
                            fw('%i ' % bmf[transparentLayer])
                            
                        if animInstanceLayer is None:
                            fw('\"\" ')
                        else:
                            fw('\"%s\" ' % bmf[animInstanceLayer].decode("utf-8"))
                    else:
                        fw('0 0 \"\"')
                        
                    fw(' // %i\n' % f.index)
                    fw('{');
                    
                    for j, vidx in enumerate(f_verts):
                        v = mesh_verts[vidx]
                        idx = j
                        
                        if bFixFace:
                            # offset the index to fix the bizzare bug
                            idx = (j + 2) % len(f_verts)
                        
                        if has_uv:
                            uvcoord = uv[idx][0], uv[idx][1]
                        else:
                            uvcoord = 0.0, 0.0
                            
                        if has_vcol:
                            color = col[idx]
                            color = (int(color[0] * 255.0),
                                     int(color[1] * 255.0),
                                     int(color[2] * 255.0),
                                     )
                        else:
                            color = 255, 255, 255
                            
                        fw('\n    %.6f %.6f %.6f ' % v.co[:])
                        fw('%.6f ' % uvcoord[0])
                        fw('%.6f ' % uvcoord[1])
                        fw('%u ' % color[0])
                        fw('%u ' % color[1])
                        fw('%u ' % color[2])
                        fw('// %i' % f_verts[idx])
                        
                    fw('\n}\n\n')
                    
                bpy.ops.object.mode_set(mode='OBJECT')
                ob.select = False
                    
            except RuntimeError:
                file.close()
                return
        
    file.close()    

# -----------------------------------------------------------------------------
# Main file writing function
def _write(context, filepath,
           EXPORT_SEL_ONLY,  # ok
           EXPORT_GLOBAL_MATRIX,
           EXPORT_PATH_MODE,  # Not used
           ):

    with ProgressReport(context.window_manager) as progress:
        base_name, ext = os.path.splitext(filepath)
        context_name = [base_name, '', '', ext]  # Base name, scene name, frame number, extension

        scene = context.scene

        # Exit edit mode before exporting, so current object states are exported properly.
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        orig_frame = scene.frame_current

        scene_frames = [orig_frame]  # Dont export an animation.

        # Loop through all frames in the scene and export.
        progress.enter_substeps(len(scene_frames))
        for frame in scene_frames:
        
            scene.frame_set(frame, 0.0)
            if EXPORT_SEL_ONLY:
                objects = context.selected_objects
            else:
                objects = scene.objects

            full_path = ''.join(context_name)

            progress.enter_substeps(1)
            write_file(full_path, objects, scene,
                       EXPORT_GLOBAL_MATRIX,
                       EXPORT_PATH_MODE,
                       progress,
                       )
            progress.leave_substeps()

        scene.frame_set(orig_frame, 0.0)
        progress.leave_substeps()

# -----------------------------------------------------------------------------
# Callback from Blender
def save(context,
         filepath,
         *,
         use_selection=True,
         global_matrix=None,
         path_mode='AUTO'
         ):

    _write(context, filepath,
           EXPORT_SEL_ONLY=use_selection,
           EXPORT_GLOBAL_MATRIX=global_matrix,
           EXPORT_PATH_MODE=path_mode,
           )

    return {'FINISHED'}
