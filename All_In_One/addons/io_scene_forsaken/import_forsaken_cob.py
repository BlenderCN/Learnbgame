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
import math
import ctypes
from mathutils import Vector
from mathutils import Matrix

COB_VERSION  = 2
    
# -----------------------------------------------------------------------------
#
def set_parent(obj, parentObj):
    if parentObj is not None:
        obj.select = True
        parentObj.select = True
        bpy.context.scene.objects.active = parentObj
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        parentObj.select = False
        obj.select = False
           
# -----------------------------------------------------------------------------
#
def origin_to_key(origin):
    return (round(origin.x, 4), round(origin.y, 4), round(origin.z, 4))
               
# -----------------------------------------------------------------------------
#
def read_component(data, global_matrix, mxFiles, translationNodes):
    from io_scene_forsaken import forsaken_utils
    
    nModelID = forsaken_utils.read16(data)
    translationNodes['model'] = nModelID
    
    bpy.context.scene.frame_set(0.0)
    nTrans = forsaken_utils.read16(data)
    
    transData = []
    
    #print('start')
    # -----------------------------------------------------------------------------
    # read translations
    if nTrans > 0:
        for i in range(0, nTrans):
            type = forsaken_utils.read16(data)
            start = forsaken_utils.readFloat(data)
            duration = forsaken_utils.readFloat(data)
            
            start *= 60.0
            duration *= 60.0
            
            if type == 0:
                #print(i, 'type 0: ', start, ' ', duration)

                transLocation = Vector(global_matrix * forsaken_utils.readVector(data))
                #print('loc: ', transLocation)
                bLocal = (forsaken_utils.read16(data) != 0)
                
                transData.append(
                {
                    "type": type,
                    "start": start,
                    "duration": duration,
                    "transLocation": transLocation,
                    "bLocal": bLocal
                })
                
            elif type == 1:
                #print(i, 'type 1: ', start, ' ', duration)
                axis = Vector(global_matrix * forsaken_utils.readVector(data))
                axis.normalize()
                origin = Vector(global_matrix * forsaken_utils.readVector(data))
                angle = math.radians(forsaken_utils.readFloat(data))
                #print('angle: ', angle)
                bLocal = (forsaken_utils.read16(data) != 0)
                #print('origin: ', origin)
                
                key = origin_to_key(origin)
                
                transData.append(
                {
                    "type": type,
                    "start": start,
                    "duration": duration,
                    "axis": axis,
                    "origin": origin,
                    "originKey": key,
                    "angle": -angle,
                    "bLocal": bLocal
                })
                
            elif type == 3:
                propType = forsaken_utils.read16(data)
                if propType == 1:
                    forsaken_utils.readString(data)
                else:
                    forsaken_utils.read16(data)
    
    translationNodes['transData'] = transData
    
    nZones = forsaken_utils.read16(data)
                  
    # -----------------------------------------------------------------------------
    # read collision zones
    if nZones > 0:
        for i in range(0, nZones):
            type = forsaken_utils.read16(data)

            forsaken_utils.read16(data)
            forsaken_utils.readFloat(data)
            forsaken_utils.readVector(data)
            forsaken_utils.readVector(data)
            
            if type != 0:
                nSides = forsaken_utils.read16(data)
                for j in range(0, nSides):
                    forsaken_utils.readVector(data)
                    forsaken_utils.readFloat(data)
                    forsaken_utils.read16(data)
                    forsaken_utils.readFloat(data)
        
    #obj.select = False
    
    children = []
    translationNodes['children'] = children
    
    nChildren = forsaken_utils.read16(data)
    if nChildren > 0:
        for i in range(0, nChildren):
            transNodes = {}
            read_component(data, global_matrix, mxFiles, transNodes)
            children.append(transNodes)
                  
# -----------------------------------------------------------------------------
#      
def create_objects(translationNodes, global_matrix, mxFiles):
    from io_scene_forsaken import forsaken_utils
    
    nModelID = translationNodes['model']
    
    if ctypes.c_short(nModelID).value <= -1:
        scene = bpy.context.scene
        obj = bpy.data.objects.new('object', None)
        scene.objects.link(obj)
        scene.objects.active = obj
        obj.select = True
    else:
        try:
            obj = forsaken_utils.load_mx(mxFiles[nModelID], global_matrix)
        except:
            raise NameError("Cannot load mx file %s" % mxFiles[nModelID])
            obj = None
            
    translationNodes['object'] = obj
    
    bpy.context.scene.frame_set(0.0)
    bpy.ops.anim.keyframe_insert(type='Location')
    bpy.ops.anim.keyframe_insert(type='Rotation')
    #obj.keyframe_insert('rotation_euler')
    #obj.keyframe_insert('location')
    
    children = translationNodes['children']
    for child in children:
        create_objects(child, global_matrix, mxFiles)
       
# -----------------------------------------------------------------------------
#             
def create_hierarchy(translationNodes, parentObj):
    from io_scene_forsaken import forsaken_utils
    
    obj = translationNodes['object']
    transData = translationNodes['transData']
    
    emptyOriginDicts = {}
    
    for trans in transData:
        type = trans['type']
        
        if type != 1:
            continue
            
        origin = trans['origin']
        key = origin_to_key(origin)
        emptyOriginDicts[key] = { 'origin': origin }
        
    curEOD = None
    
    for i, eod in emptyOriginDicts.items():
        origin = eod['origin']
        if origin.x == 0.0 and origin.y == 0.0 and origin.z == 0.0:
            eod['object'] = None
            continue
        
        bpy.context.scene.cursor_location = origin
        bpy.ops.object.empty_add(type='SPHERE')
        empty = bpy.context.active_object
        empty.empty_draw_size = 0.125
        eod['object'] = empty
        
        bpy.context.scene.frame_set(0.0)
        #empty.keyframe_insert('rotation_euler')
        #empty.keyframe_insert('location')
        #bpy.ops.anim.keyframe_insert(type='Location')
        bpy.ops.anim.keyframe_insert(type='Rotation')
        
        if curEOD is not None:
            set_parent(empty, curEOD)
        elif parentObj is not None:
            set_parent(empty, parentObj)
        
        curEOD = empty
        
    translationNodes['eodObjects'] = emptyOriginDicts
        
    if curEOD is not None:
        parentObj = curEOD
    
    if parentObj is not None:
        set_parent(obj, parentObj)
        
    children = translationNodes['children']
    for child in children:
        create_hierarchy(child, obj)
        
# -----------------------------------------------------------------------------
#      
def create_keyframes(translationNodes, global_matrix):
    from io_scene_forsaken import forsaken_utils
    
    obj = translationNodes['object']
    transData = translationNodes['transData']
    emptyOriginDicts = translationNodes['eodObjects']
    
    curEOD = None
    
    for i, trans in enumerate(transData):
        type = trans['type']
        start = trans['start']
        duration = trans['duration']
        
        frameEnd = bpy.data.scenes['Scene'].frame_end
        bpy.data.scenes['Scene'].frame_end = forsaken_utils.max(start + duration, frameEnd)
        
        if type == 0:
            bpy.context.scene.objects.active = obj
            obj.select = True
            bpy.context.scene.frame_set(start + duration)
            obj.location = obj.location + trans['transLocation']
            #obj.keyframe_insert('location')
            bpy.ops.anim.keyframe_insert(type='Location')
        elif type == 1:
            obj.select = False
            eod = emptyOriginDicts[trans['originKey']]
            otherObj = eod['object']
            if otherObj is None:
                otherObj = obj
            else:
                curEOD = otherObj
                
            otherObj.select = True
            bpy.context.scene.frame_set(start + duration)
            
            axis = trans['axis']
            if trans['bLocal'] == True:
                axis = Vector(otherObj.rotation_euler.to_matrix() * axis)
                axis.normalize()
                    
            rotMtx = Matrix.Rotation(trans['angle'], 4, axis)

            otherObj.rotation_euler.rotate(rotMtx)
            #otherObj.keyframe_insert('rotation_euler')
            bpy.ops.anim.keyframe_insert(type='Rotation')
            otherObj.select = False
            obj.select = True
            
    fcurves = obj.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
    
    children = translationNodes['children']
    for child in children:
        create_keyframes(child, global_matrix)
                
# -----------------------------------------------------------------------------
#
def load(operator, context, filepath, global_matrix):
    with open(filepath, 'rb') as data:
        from io_scene_forsaken import forsaken_utils
    
        data.seek(0)
        print(filepath)
        # -----------------------------------------------------------------------------
        # verify file header and version
        magic = forsaken_utils.read32(data)
        version = forsaken_utils.read32(data)
        
        if magic != forsaken_utils.PROJECTX_MAGIC_ID:
            print('%s is not a valid PRJX file' % filepath)
            return {'CANCELLED'}
        
        if version != COB_VERSION:
            print('%s has invalid version number' % filepath)
            return {'CANCELLED'}
            
        nModels = forsaken_utils.read16(data)
        mxFiles = [""] * nModels
        
        for i in range(0, nModels):
            mxFiles[i] = os.path.dirname(os.path.realpath(filepath)) + '/Models/' + forsaken_utils.readString(data)
            
        translationNodes = {}
        bpy.data.scenes['Scene'].frame_end = 1
        
        read_component(data, global_matrix, mxFiles, translationNodes)
        
        create_objects(translationNodes, global_matrix, mxFiles)
        create_hierarchy(translationNodes, None)
        create_keyframes(translationNodes, global_matrix)
        
        return {'FINISHED'}
    