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
import mathutils
import math
import re

COB_VERSION  = 2

SFX_KEYS = { 1000 : "acidpool", 0 : "airbubb1", 1001 : "aircond1", 1002 : "aircond2", 1003 : "aircond3", 1004 : "airmoeng", 1005 : "airpress", 1006 : "ammodump", 1007 : "areahum1", 1008 : "avatreng", 1009 : "bikeengn", 1 : "bikexpl", 1010 : "boathorn", 2 : "boo", 1011 : "boteng", 3 : "captflag", 4 : "cheer", 1012 : "compamb1", 1013 : "compamb2", 1014 : "compamb3", 1015 : "compamb4", 5 : "compsel", 6 : "compwrk", 1016 : "cranemov", 7 : "cryspkup", 1018 : "crysthum", 8 : "dripwat01", 8 : "dripwat02", 8 : "dripwat03", 8 : "dripwat04", 8 : "dripwat05", 1150 : "elecbzt", 1019 : "elecexpl", 1152 : "elechumh", 9 : "elecspk01", 9 : "elecspk02", 9 : "elecspk03", 10 : "electhrb", 1020 : "eled1mov", 1021 : "eled1stp", 1022 : "eled1str", 1023 : "eled2mov", 1024 : "eled2stp", 1025 : "eled2str", 1026 : "eled3mov", 1027 : "eled3stp", 1028 : "eled3str", 1029 : "eled4mov", 1030 : "eled4stp", 1031 : "eled4str", 1032 : "emergency", 11 : "enemisln", 12 : "enempuls", 13 : "enemspwn", 14 : "enemsuss", 15 : "enmspin01", 15 : "enmspin02", 15 : "enmspin03", 17 : "explosion_mushroom01", 17 : "explosion_mushroom02", 17 : "explosion_mushroom03", 17 : "explosion_mushroom04", 17 : "explosion_mushroom05", 1033 : "ffdorcls", 1034 : "ffdorcns", 1035 : "ffdoropn", 1036 : "ffield1", 1037 : "ffield2", 1038 : "ffield3", 22 : "firembls", 1151 : "firesbrn", 23 : "firesh2", 1039 : "fireup01", 1039 : "fireup02", 1039 : "fireup03", 1039 : "fireup04", 1040 : "flaphits", 1041 : "fmorfbro", 24 : "fmorfchh", 25 : "fmorfdie", 1042 : "fmorfhdr", 26 : "fmorfhit", 1043 : "fmorfmov", 27 : "fmorfpai", 1044 : "fmorfsro", 1045 : "forkleng", 1047 : "frklften", 1046 : "frklftgo", 1156 : "gasleak", 1048 : "gearturn", 1049 : "geekengn", 1050 : "geiger", 28 : "genrammo", 1051 : "glassexp", 1052 : "gndoorcl", 1053 : "gndoorop", 1054 : "gndoorst", 29 : "goldpkup", 1055 : "grateop1", 30 : "gravgfld", 1056 : "grsldstp", 1057 : "grsldstr", 1058 : "gtretmov", 1059 : "gtretstp", 1060 : "gtretstr", 31 : "guts01", 31 : "guts02", 31 : "guts03", 31 : "guts04", 1061 : "hmetslam", 1062 : "hollwam1", 32 : "holochng", 33 : "hullbump", 203 : "hullhit01", 203 : "hullhit02", 203 : "hullhit03", 203 : "hullhit04", 1063 : "huntreng", 16 : "impact_generic_explosion", 34 : "incoming", 1064 : "indshum1", 1065 : "indshum2", 1066 : "indshum3", 1067 : "indshum4", 1068 : "intaler1", 1069 : "keypadpr", 1070 : "largefan", 35 : "laser2c", 36 : "laserbm", 1071 : "lavaloop", 1072 : "legzfoot", 1073 : "leviteng", 1074 : "lift1lp", 1075 : "lift1stp", 1076 : "lift1str", 1077 : "litesh01", 1077 : "litesh02", 1077 : "litesh03", 1077 : "litesh04", 1149 : "longrumb", 37 : "loseflag", 1078 : "machamb1", 1079 : "mainhumh", 1080 : "mainhuml", 1081 : "maxeng", 201 : "menuclearui", 202 : "menustackdown", 200 : "menuswooshside", 38 : "menuwsh", 39 : "message", 1082 : "metateng", 1083 : "methinge", 1084 : "metpexpl", 40 : "mfrln", 41 : "minelay", 1085 : "mineleng", 1086 : "mineseng", 42 : "mnacthum", 43 : "movesel", 44 : "mslaun2", 45 : "mslhitwl", 46 : "mslhitwt", 1087 : "mtrtspin", 1088 : "mtscrape", 1089 : "nearwatr", 47 : "negative", 48 : "nitrogo", 49 : "orbit_pulsar_fire", 50 : "photon2", 999 : "pickup", 51 : "pinemove", 52 : "pkupmisc", 53 : "pkupshld", 54 : "playergn", 1090 : "potexp", 55 : "pulsfire", 1091 : "pumpamb1", 1092 : "pumpamb2", 56 : "pyroloop", 57 : "pyrostop", 58 : "pyrostrt", 59 : "quantexp", 60 : "respawn", 61 : "restartp", 1093 : "rockfall", 1094 : "rockht01", 1094 : "rockht02", 1094 : "rockht03", 1094 : "rockht04", 1095 : "roomtone1", 1096 : "rumble1", 1097 : "safedial", 62 : "scattln", 63 : "scrchang", 64 : "secret", 65 : "select", 1098 : "sfindamb", 1099 : "shadeeng", 66 : "shieldht", 67 : "shipamb", 1100 : "shipcrk1", 1101 : "shipcrk2", 68 : "shldknck", 1153 : "shrphmt04", 1154 : "shrplrk", 1148 : "shrtrumb", 1155 : "shteammbm", 1102 : "shtlidle", 1103 : "siren01", 1104 : "siren02", 1105 : "siren03", 1106 : "siren04", 1107 : "siren05", 1108 : "smallfan", 1109 : "smallfn2", 1110 : "smallfn3", 1111 : "smallfn4", 1112 : "smkdorcl", 1113 : "smkdorop", 69 : "sonar", 1114 : "spshappr", 1115 : "spshland", 70 : "stakdown", 71 : "stakmove", 72 : "steammcn", 73 : "stmantof", 74 : "stmanton", 1116 : "stndrmov", 1117 : "stndrstp", 1118 : "stndrstr", 1119 : "stnswitch", 1120 : "stnswtch", 1121 : "subgenlp", 1122 : "subgenst", 1123 : "subgstop", 75 : "submerge", 1124 : "suppreng", 76 : "surface", 77 : "sussammo", 78 : "sussgnf3", 79 : "sussimp01", 79 : "sussimp02", 79 : "sussimp03", 79 : "sussimp04", 80 : "sussric01", 80 : "sussric02", 80 : "sussric03", 80 : "sussric04", 1125 : "swarmeng", 1126 : "switch01", 1127 : "switch02", 1128 : "switch03", 1129 : "switch04", 1130 : "switch05", 1131 : "switch06", 1132 : "switch07", 1133 : "switch08", 1134 : "tankeng", 1135 : "tcovercl", 1136 : "tcoverop", 81 : "teleport", 1137 : "thermal", 1138 : "throbamb", 1139 : "thrstbrn", 82 : "tilesel", 83 : "titanexp", 84 : "titanln", 1140 : "torchbrn", 85 : "tpfire2", 1141 : "trainmov", 86 : "trojfire", 87 : "trojpup", 1142 : "tubertat", 88 : "unwatamb", 89 : "uwtsnd01", 90 : "vdu_off", 91 : "vdu_on", 92 : "vidtext", 1143 : "wallfall", 93 : "watrdrai", 94 : "watrfill", 95 : "weapload", 96 : "weapslct", 1144 : "windesol", 1145 : "windhol1", 1146 : "windhol2", 1147 : "windhol3", 97 : "xtralife", 86 : "trojax_fire", 82 : "transpulse_fire", 87 : "trojax_charge", 79 : "suss_impact04", 79 : "suss_impact03", 79 : "suss_impact01", 79 : "suss_impact02", 71 : "stackmove", 78 : "suss_fire", 44 : "mug_fire", 35 : "laser", 15 : "enemy_spin", 14 : "enemysuss_fire", 12 : "enemy_pulsar", 5 : "compselect" }

# -----------------------------------------------------------------------------
#
def object_is_zone(obj):
    return obj.get('collisionzone') is not None

# -----------------------------------------------------------------------------
#
def object_is_model(obj):
    ext = os.path.splitext(obj.name)
    if ext is None:
        return False
        
    if len(ext) == 1:
        ext = ext[0]
    else:
        ext = ext[1]
    
    if ext != ".mx":
        return ext == ".MX"
        
    return True
  
# -----------------------------------------------------------------------------
#  
def object_is_rotation_point(obj):
    return obj.empty_draw_type == 'SPHERE'
    
# -----------------------------------------------------------------------------
#
def model_to_index(obj, modelNames):
    name = os.path.splitext(obj.name)
    if name is None:
        return -1
        
    name = name[0]
    if name not in modelNames:
        return -1
        
    return modelNames[name]

# -----------------------------------------------------------------------------
#
def compute_mesh_bounds(mesh):
    from mathutils import Vector
    
    inf = 1.192092896e-07
    min = Vector((inf, inf, inf))
    max = Vector((-inf, -inf, -inf))
    
    for i, v in enumerate(mesh.vertices):
        lowx  = min.x;
        lowy  = min.y;
        lowz  = min.z;
        hix   = max.x;
        hiy   = max.y;
        hiz   = max.z;
        
        vec = Vector(v.co[:])
        vec.x = -vec.x
        
        if vec.x < lowx: lowx = vec.x
        if vec.y < lowy: lowy = vec.y
        if vec.z < lowz: lowz = vec.z
        if vec.x > hix:  hix  = vec.x
        if vec.y > hiy:  hiy  = vec.y
        if vec.z > hiz:  hiz  = vec.z
        
        min = Vector((lowx, lowy, lowz))
        max = Vector((hix, hiy, hiz))
        
    return { "min": min, "max": max }

# -----------------------------------------------------------------------------
#
def compute_bounds_center(bounds):
    from mathutils import Vector
    
    min = bounds['min']
    max = bounds['max']
    
    return Vector((
        (min.x + max.x) * 0.5,
        (min.y + max.y) * 0.5,
        (min.z + max.z) * 0.5
        ))
  
# -----------------------------------------------------------------------------
#      
def compute_bounds_halfsize(bounds):
    from mathutils import Vector
    
    min = bounds['min']
    max = bounds['max']
    
    return Vector((
        (max.x - min.x) * 0.5,
        (max.y - min.y) * 0.5,
        (max.z - min.z) * 0.5
        ))
           
# -----------------------------------------------------------------------------
# 
def gather_children(object, objects):
    children = []
    
    for i, childObj in enumerate(objects):
        if childObj.name == object.name:
            continue
            
        if childObj.parent is None:
            continue
            
        if childObj.parent.name == object.name:
            if object_is_zone(childObj):
                continue
                
            children.append(childObj)
            
    return children
         
# -----------------------------------------------------------------------------
# 
def gather_zones(object, objects):
    zones = []
    
    for i, childObj in enumerate(objects):
        if childObj.name == object.name:
            continue
            
        if childObj.parent is None:
            continue

        # must be a child object
        if childObj.parent.name == object.name:
            if object_is_zone(childObj):
                zones.append(childObj)
                
    return zones
         
# -----------------------------------------------------------------------------
# 
def gather_parent_rotation_spheres(object):
    parents = []
    obj = object.parent
    
    while obj is not None and object_is_rotation_point(obj):
        parents.append(obj)
        obj = obj.parent
        
    return parents
        
# -----------------------------------------------------------------------------
# 
def get_desired_channel_keyframe(channel, frameAt):
    desiredKeyPoint = channel.keyframe_points[0]
    
    for keyPt in channel.keyframe_points:
        if keyPt.co[0] <= frameAt:
            desiredKeyPoint = keyPt
            
    return desiredKeyPoint
     
# -----------------------------------------------------------------------------
# 
def setup_keyframe_list(channels):  
    uniqueFrames = []
    for c in channels:
        for i in range(len(c.keyframe_points)):
            frame = c.keyframe_points[i].co[0]
            if frame not in uniqueFrames:
                uniqueFrames.append(frame)
                    
    uniqueFrames.sort()
    #print(uniqueFrames)
    
    keys = [{}] * len(uniqueFrames)
    
    for i, key in enumerate(keys):
        keys[i] = { "frame": uniqueFrames[i], "data": [0.0] * len(channels) }
        for ic, c in enumerate(channels):
            keys[i]['data'][ic] = get_desired_channel_keyframe(c, uniqueFrames[i]).co[1]
            
    return keys

# -----------------------------------------------------------------------------
# 
def add_location_keyframes(object, group, translations, global_matrix):
    from mathutils import Vector
    from mathutils import Euler
    
    c1 = group.channels[0]
    c2 = group.channels[1]
    c3 = group.channels[2]
    
    totalTime = 0.0
    type = 0
    
    objPos = object.location
    prevPosition = objPos

    keys = setup_keyframe_list([c1, c2, c3]) 
    #print(len(keys))
    #print(keys)
    
    for key in keys:
        x = key['data'][0]
        y = key['data'][1]
        z = key['data'][2]
        
        vec = Vector((x, y, z))
        vec = Vector(global_matrix * vec)
        
        start = key['frame']
        translations.append(
        {
            "start": totalTime / 60.0,
            "duration": (start - totalTime) / 60.0,
            "type": type,
            "vector": vec - prevPosition,
            "local": 0
        })
        
        totalTime = start
        prevPosition = vec
        
# -----------------------------------------------------------------------------
# 
def add_rotation_keyframe(object, group, translations, pivot, global_matrix):
    from mathutils import Vector
    from mathutils import Euler
    
    c1 = group.channels[0] # x
    c2 = group.channels[1] # y
    c3 = group.channels[2] # z
    
    totalTime = 0.0
    type = 1
    
    prevX = 0.0
    prevY = 0.0
    prevZ = 0.0
    keys = setup_keyframe_list([c1, c2, c3]) 
    #print(len(keys))
    #print(keys)
    
    # be sure to offset by the first frame's rotation
    for key in keys:
        if key['frame'] == 1.0:
            prevX = key['data'][0]
            prevY = key['data'][1]
            prevZ = key['data'][2]
            break

    for key in keys:
        x = key['data'][0]
        y = key['data'][1]
        z = key['data'][2]
        
        rot = Euler((x - prevX, y - prevY, z - prevZ))
        
        #rotDelta = rot
        #rotDelta.x -= prevRotation.x
        #rotDelta.y -= prevRotation.y
        #rotDelta.z -= prevRotation.z
        
        quat = rot.to_quaternion()
        axisAngle = quat.to_axis_angle()
        angle = -axisAngle[1]
        axis = axisAngle[0]
        
        start = key['frame']
        
        axis = Vector(global_matrix * axis)
        axis.normalize()
        axis.z = -axis.z
        
        translations.append(
        {
            "start": totalTime / 60.0,
            "duration": (start - totalTime) / 60.0,
            "type": type,
            "axis": axis,
            "angle": angle,
            "origin": Vector(global_matrix * pivot),
            "local": 0
        })
        
        prevX = x
        prevY = y
        prevZ = z
        totalTime = start
     
# -----------------------------------------------------------------------------
#   
def add_property_keyframe(object, translations, global_matrix):
    from mathutils import Vector
    from mathutils import Euler
    
    if object.animation_data is None or object.animation_data.action is None or object.animation_data.action.fcurves is None:
        return
        
    type = 3    # TRANS_PROPERTY
    totalTime = 0.0
    
    for curve in object.animation_data.action.fcurves:
        #print(curve.data_path)
        if curve.data_path == "[\"property_state\"]":
            for key in curve.keyframe_points:
                start = key.co[0]
                
                translations.append(
                {
                    "start": totalTime / 60.0,
                    "duration": (start - totalTime) / 60.0,
                    "type": type,
                    "propType": 0,  # PROP_STATE
                    "value": int(key.co[1])
                })
                totalTime = start
        elif curve.data_path == "[\"sfx\"]":
            for key in curve.keyframe_points:
                start = key.co[0]
                value = int(key.co[1])
                
                if value >= 0:
                    sfxName = SFX_KEYS[value]
                    
                    if sfxName != None:
                        translations.append(
                        {
                            "start": totalTime / 60.0,
                            "duration": (start - totalTime) / 60.0,
                            "type": type,
                            "propType": 1,  # PROP_SFX
                            "value": sfxName
                        })
                totalTime = start
        
# -----------------------------------------------------------------------------
#
def save_cob_children(context, f, object, objects, modelNames, global_matrix):
    from io_scene_forsaken import forsaken_utils
    from mathutils import Vector
    from mathutils import Euler
    
    if object_is_rotation_point(object):
        children = gather_children(object, objects)
        for i, child in enumerate(children):
            save_cob_children(context, f, child, objects, modelNames, global_matrix)
            
        return

    scene = context.scene
    
    rotSpheres = gather_parent_rotation_spheres(object)
    #print(len(rotSpheres))
    
    translations = []
    #print('nGroups: ', len(object.animation_data.action.groups))
    
    if object.animation_data is not None and object.animation_data.action is not None:
        for g in object.animation_data.action.groups :
            nChannels = len(g.channels)

            #print('data_path: ', g.channels[0].data_path)
            
            if nChannels == 0:
                continue
            
            if g.channels[0].data_path.endswith('location'):
                add_location_keyframes(object, g, translations, global_matrix)
                    
            elif g.channels[0].data_path.endswith('rotation_euler'):
                add_rotation_keyframe(object, g, translations, Vector((0.0, 0.0, 0.0)), global_matrix)
                
    for rotS in rotSpheres:
        if rotS.animation_data is None:
            continue
            
        for g in rotS.animation_data.action.groups :
            nChannels = len(g.channels)
            
            if nChannels == 0:
                continue
                
            if g.channels[0].data_path.endswith('rotation_euler'):
                add_rotation_keyframe(rotS, g, translations, rotS.location, global_matrix)
                
    add_property_keyframe(object, translations, global_matrix)

    # -----------------------------------------------------------------------------
    # write mapped model index
    #print(object.name)
    forsaken_utils.write16(f, model_to_index(object, modelNames))
    forsaken_utils.write16(f, len(translations))
    
    #print('num trans: ', len(translations))
    
    from operator import itemgetter
    newlist = sorted(translations, key=itemgetter('start')) 
    
    for i, trans in enumerate(newlist):
        #print('trans: ', trans)
        
        type = trans["type"]
        
        forsaken_utils.write16(f, type)
        forsaken_utils.writeFloat(f, trans["start"])
        forsaken_utils.writeFloat(f, trans["duration"])
        
        if type == 0:
            vec = trans["vector"]
            vec.x = -vec.x
            forsaken_utils.writeVector(f, vec)
            forsaken_utils.write16(f, trans["local"])
        elif type == 1:
            axis = trans["axis"]
            forsaken_utils.writeVector(f, axis)
            org = trans["origin"]
            org.x = -org.x
            forsaken_utils.writeVector(f, org)
            forsaken_utils.writeFloat(f, math.degrees(trans["angle"]))
            forsaken_utils.write16(f, trans["local"])
        elif type == 3:
            forsaken_utils.write16(f, trans["propType"])
            
            if trans["propType"] == 0:
                forsaken_utils.write16(f, trans["value"])
            elif trans["propType"] == 1:
                forsaken_utils.writeString(f, trans["value"])
    
    # -----------------------------------------------------------------------------
    # gather objects to serve as zones
    validZones = gather_zones(object, objects)
    
    forsaken_utils.write16(f, len(validZones))
    
    # -----------------------------------------------------------------------------
    # iterate and write out zones
    for i, zone, in enumerate(validZones):
        forsaken_utils.write16(f, zone.get("zonetype", 0))
        forsaken_utils.write16(f, zone.get("sensitive", 0))
        forsaken_utils.writeFloat(f, zone.get("damage", 0.0))
        
        mesh = zone.to_mesh(scene, True, 'PREVIEW')
        mesh.transform(global_matrix * zone.matrix_world)
        
        bounds      = compute_mesh_bounds(mesh)
        center      = compute_bounds_center(bounds)
        halfsize    = compute_bounds_halfsize(bounds)
        
        forsaken_utils.writeVector(f, center)
        forsaken_utils.writeVector(f, halfsize)
        
        # sphere types don't have complicated collision data
        if zone.get("zonetype", 0) == 0:
            continue
            
        # -----------------------------------------------------------------------------
        # write out a plane for every polygon
        forsaken_utils.write16(f, len(mesh.polygons))
        for p, poly in enumerate(mesh.polygons):
            if len(poly.vertices) < 3:
                forsaken_utils.writeVector(f, Vector((0.0, 0.0, 1.0)))
                forsaken_utils.writeFloat(f, 0.0)
            else:
                p1 = Vector(mesh.vertices[poly.vertices[0]].co)
                p2 = Vector(mesh.vertices[poly.vertices[1]].co)
                p3 = Vector(mesh.vertices[poly.vertices[2]].co)
                
                p1.x = -p1.x
                p2.x = -p2.x
                p3.x = -p3.x
                
                normal = mathutils.geometry.normal([p3, p2, p1])
                d = -p1.dot(normal)
                
                forsaken_utils.writeVector(f, normal)
                forsaken_utils.writeFloat(f, d)
            
            forsaken_utils.write16(f, zone.get("sensitive", 0))
            forsaken_utils.writeFloat(f, zone.get("damage", 0.0))
            
    # -----------------------------------------------------------------------------
    # collect child objects
    children = gather_children(object, objects)
    forsaken_utils.write16(f, len(children))
    
    # -----------------------------------------------------------------------------
    # recurse children
    for i, child in enumerate(children):
        save_cob_children(context, f, child, objects, modelNames, global_matrix)

# -----------------------------------------------------------------------------
#
def save_cob(context, filepath, use_selection, global_matrix=None, path_mode='AUTO'):
    with open(filepath, 'wb') as data:
        from io_scene_forsaken import forsaken_utils
        from mathutils import Vector
        
        try:
            if global_matrix is None:
                global_matrix = mathutils.Matrix()
                
            forsaken_utils.write32(data, forsaken_utils.PROJECTX_MAGIC_ID)
            forsaken_utils.write32(data, COB_VERSION)
            
            scene = context.scene
            
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode='OBJECT')
                
            orig_frame = scene.frame_current
            scene_frames = [orig_frame]
            
            modelNames = {}
            modelFiles = []
            nModelIndex = 0
            
            for frame in scene_frames:
                scene.frame_set(frame, 0.0)
                if use_selection:
                    objects = context.selected_objects
                else:
                    objects = scene.objects
                    
            # -----------------------------------------------------------------------------
            # determine how many unique models are in use. model is determined by
            # the object's name (which should also end in .mx)
            for i, obj in enumerate(objects):
                if object_is_zone(obj):
                    continue
                    
                if object_is_model(obj) == False:
                    continue
                    
                name = os.path.splitext(obj.name)[0]
                
                # -----------------------------------------------------------------------------
                # add unique model file name to list and map a model index to it but
                # ignore if it exists already
                if name not in modelNames:
                    modelNames[name] = nModelIndex
                    nModelIndex = nModelIndex + 1
                    modelFiles.append(obj.name)

            forsaken_utils.write16(data, len(modelFiles))
            
            # -----------------------------------------------------------------------------
            # write out model file names
            for i, modelFile in enumerate(modelFiles):
                forsaken_utils.writeString(data, modelFile)
                
            # -----------------------------------------------------------------------------
            # recurse children from root object(s)
            for i, obj in enumerate(objects):
                if obj.parent is None:
                    save_cob_children(context, data, obj, objects, modelNames, global_matrix)
                    break
                    
        except RuntimeError:
            data.close()

# -----------------------------------------------------------------------------
#
def save(context,
         filepath,
         *,
         use_selection=True,
         global_matrix=None,
         path_mode='AUTO'
         ):
    from io_scene_forsaken import forsaken_utils
    
    save_cob(context, filepath, use_selection, global_matrix, path_mode)
    return {'FINISHED'}
    