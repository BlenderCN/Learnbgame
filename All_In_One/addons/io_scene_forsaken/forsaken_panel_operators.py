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
# UV Texture Tilemap Tool Panel
#
#-----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
class ForsakenUVPanel(bpy.types.Panel):
    bl_label = "Forsaken Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Forsaken Tools"
    
    def draw(self, context):
        ob = context.active_object
        layout = self.layout
        
        if context.mode == 'EDIT_MESH':
            row = layout.row(align=True)
            row.prop(context.scene, "tile_x", text="Tile X")
            row.prop(context.scene, "tile_y", text="Tile Y")
            row = layout.row(align=True)
            row.prop(context.scene, "offset_x", text="Offset X")
            row.prop(context.scene, "offset_y", text="Offset Y")
            row = layout.row(align=True)
            row.prop(context.scene, "mirrorX", text="Mirror Tile X")
            row = layout.row(align=True)
            row.prop(context.scene, "mirrorY", text="Mirror Tile Y")
            row = layout.row(align=True)
            row.operator("object.forsaken_edit_uv", text="Align")
            row = layout.row(align=True)
            row.operator("object.forsaken_force_square_tile", text="Force Square Tile")
            row = layout.row(align=True)
            row.operator("object.forsaken_set_ignore_bsp", text="Ignore BSP")
            row.operator("object.forsaken_clear_ignore_bsp", text="Clear Ignore BSP")
            row = layout.row(align=True)
            row.operator("object.forsaken_set_transparent", text="Set Transparent")
            row.operator("object.forsaken_clear_transparent", text="Clear Transparent")
            row = layout.row()
            row.prop_search(context.scene, "curAnimInst", context.scene, "objects")
            row = layout.row(align=True)
            row.operator("object.forsaken_set_anim_inst", text="Set Face To Animation Instance")
            row = layout.row(align=True)
            row.operator("object.forsaken_subdivide", text="Subdivide")
        else:
            row = layout.row(align=True)
            row.operator("object.forsaken_auto_vertex_light", text="Build Vertex Lighting")
        
import bmesh
import math

# -----------------------------------------------------------------------------
#
bpy.types.Scene.tile_x      = bpy.props.IntProperty(name="Tile X", default=64)
bpy.types.Scene.tile_y      = bpy.props.IntProperty(name="Tile Y", default=64)
bpy.types.Scene.offset_x    = bpy.props.FloatProperty(name="Offset X", default=0)
bpy.types.Scene.offset_y    = bpy.props.FloatProperty(name="Offset Y", default=0)
bpy.types.Scene.mirrorX     = bpy.props.BoolProperty(name="Mirror X", default=False)
bpy.types.Scene.mirrorY     = bpy.props.BoolProperty(name="Mirror Y", default=False)
bpy.types.Scene.curAnimInst = bpy.props.StringProperty(name = "Anim Instance Object")

# -----------------------------------------------------------------------------
#
class ForsakenUVAlignOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_edit_uv"
    bl_label = "Forsaken Edit UV"
    
    def execute(self, context):
        obj = context.active_object
        me = obj.data
        objectLocation = context.active_object.location
        objectScale = context.active_object.scale
        
        fTX = float(context.scene.tile_x) / 256.0
        fTY = float(context.scene.tile_y) / 256.0
        
        fDX = 256.0 / float(context.scene.tile_x)
        fDY = 256.0 / float(context.scene.tile_y)
        
        fOX = fTX * context.scene.offset_x
        fOY = fTY * context.scene.offset_y
        
        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()
            for f in bm.faces:
                if f.select:
                    bpy.ops.uv.select_all(action='SELECT')
                    na = math.fabs(f.normal.x)
                    nb = math.fabs(f.normal.y)
                    nc = math.fabs(f.normal.z)
                    
                    bestAxis = -1
                    
                    if na >= nb and na >= nc:
                        bestAxis = 0
                    elif nb >= na and nb >= nc:
                        bestAxis = 1
                    else:
                        bestAxis = 2
                        
                    lowest = [10000.0, 10000.0]
                    highest = [-10000.0, -10000.0]
                    
                    for l in f.loops:
                        luv = l[uv_layer]
                        if luv.select:
                            if f.normal[bestAxis] < 0.0:
                                if bestAxis == 0:
                                    luv.uv.x = (l.vert.co.y + objectLocation[1] - math.fmod(objectLocation[1], 1.0)) * -1.0
                                    luv.uv.y = (l.vert.co.z + objectLocation[2] - math.fmod(objectLocation[2], 1.0))
                                elif bestAxis == 1:
                                    luv.uv.x = (l.vert.co.x + objectLocation[0] - math.fmod(objectLocation[0], 1.0))
                                    luv.uv.y = (l.vert.co.z + objectLocation[2] - math.fmod(objectLocation[2], 1.0))
                                else:
                                    luv.uv.x = (l.vert.co.x + objectLocation[0] - math.fmod(objectLocation[0], 1.0))
                                    luv.uv.y = (l.vert.co.y + objectLocation[1] - math.fmod(objectLocation[1], 1.0)) * -1.0
                            else:
                                if bestAxis == 0:
                                    luv.uv.x = (l.vert.co.y + objectLocation[1] - math.fmod(objectLocation[1], 1.0))
                                    luv.uv.y = (l.vert.co.z + objectLocation[2] - math.fmod(objectLocation[2], 1.0))
                                elif bestAxis == 1:
                                    luv.uv.x = (l.vert.co.x + objectLocation[0] - math.fmod(objectLocation[0], 1.0)) * -1.0
                                    luv.uv.y = (l.vert.co.z + objectLocation[2] - math.fmod(objectLocation[2], 1.0))
                                else:
                                    luv.uv.x = (l.vert.co.x + objectLocation[0] - math.fmod(objectLocation[0], 1.0))
                                    luv.uv.y = (l.vert.co.y + objectLocation[1] - math.fmod(objectLocation[1], 1.0))
                                    
                            if context.scene.mirrorX is True:
                                luv.uv.x = math.fmod(luv.uv.x, 2.0)
                            if context.scene.mirrorY is True:
                                luv.uv.y = math.fmod(luv.uv.y, 2.0)
                                
                            #print('modded: ', luv.uv.x, ' ', luv.uv.y)
                    
                    for l in f.loops:
                        luv = l[uv_layer]
                        if luv.select:
                        
                            luv.uv.x *= fTX
                            luv.uv.y *= fTY
                            
                            if luv.uv.x < lowest[0]:
                                lowest[0] = luv.uv.x
                            if luv.uv.y < lowest[1]:
                                lowest[1] = luv.uv.y
                                
                            if luv.uv.x > highest[0]:
                                highest[0] = luv.uv.x 
                            if luv.uv.y > highest[1]:
                                highest[1] = luv.uv.y 
                            
                            #print('new: ', luv.uv.x, ' ', luv.uv.y)
                            
                    print(lowest, ' ', highest)
                    
                    for l in f.loops:
                        luv = l[uv_layer]
                        if luv.select:
                            luv.uv.x -= lowest[0]
                            luv.uv.y -= lowest[1]
                            luv.uv.x += fOX
                            luv.uv.y += fOY
                            #print('new2: ', luv.uv.x, ' ', luv.uv.y)
                        
            #print(objectLocation)
        
        return {"FINISHED"}    

# -----------------------------------------------------------------------------
#
class ForsakenForceSquareTileOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_force_square_tile"
    bl_label = "Forsaken Force Square Tile"
    
    def execute(self, context):
        from mathutils import Vector
        
        obj = context.active_object
        me = obj.data    

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()
            for f in bm.faces:
                if f.select:
                    bpy.ops.uv.select_all(action='SELECT')
                    
                    bestAxis = -1
                    neg = False
                    crossProduct = Vector((0.0, 0.0, 0.0))
                    
                    for i, l in enumerate(f.loops):
                        luv = l[uv_layer]
                        if luv.select:
                            v1 = l.vert.co
                            v2 = f.loops[(i+1)%len(f.loops)].vert.co
                            
                            delta = v1 - v2
                            delta.normalize()
                            
                            cp = delta.cross(f.normal)
                            cp.normalize()
                            
                            na = math.fabs(cp.x)
                            nb = math.fabs(cp.y)
                            nc = math.fabs(cp.z)
                            
                            if na > nb and na > nc:
                                bestAxis = 0
                                neg = f.normal.x > 0.0
                            elif nb >= na and nb >= nc:
                                bestAxis = 1
                                neg = f.normal.x < 0.0
                            else:
                                bestAxis = 2
                                neg = (f.normal.x < 0.0)
                            
                            crossProduct = cp
                            break
                            
                    for i, l in enumerate(f.loops):
                        luv = l[uv_layer]
                        if luv.select:
                        
                            if i == 0:
                                if bestAxis == 0:
                                    if neg == True:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.0
                                    else:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.0
                                elif bestAxis == 1:
                                    if neg == True:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.25
                                    else:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.0
                                    
                                elif bestAxis == 2:
                                    if neg == True:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.25
                                    else:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.0
                                    
                            elif i == 1:
                                if bestAxis == 0:
                                    if neg == True:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.0
                                    else:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.0
                                elif bestAxis == 1:
                                    if neg == True:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.25
                                    else:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.0
                                    
                                elif bestAxis == 2:
                                    if neg == True:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.0
                                    else:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.25
                                    
                            elif i == 2:
                                if bestAxis == 0:
                                    if neg == True:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.25
                                    else:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.25
                                elif bestAxis == 1:
                                    if neg == True:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.0
                                    else:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.25
                                    
                                elif bestAxis == 2:
                                    if neg == True:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.0
                                    else:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.25
                                    
                            elif i == 3:
                                if bestAxis == 0:
                                    if neg == True:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.25
                                    else:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.25
                                elif bestAxis == 1:
                                    if neg == True:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.0
                                    else:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.25
                                    
                                elif bestAxis == 2:
                                    if neg == True:
                                        luv.uv.x = 0.25
                                        luv.uv.y = 0.25
                                    else:
                                        luv.uv.x = 0.0
                                        luv.uv.y = 0.0
                                    
                    
        return {"FINISHED"} 
        

# -----------------------------------------------------------------------------
#
class ForsakenSubdivideOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_subdivide"
    bl_label = "Forsaken Subdivide"
    
    def execute(self, context):
        from mathutils import Vector
        
        obj = context.active_object
        me = obj.data    
        bm = bmesh.from_edit_mesh(me)
        
        if context.mode == 'EDIT_MESH':
            edges = []

            for i in range(-100, 100):
                ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(i,0,0), plane_no=(-1,0,0))
                bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

            for i in range(-100, 100):
                ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,i,0), plane_no=(0,1,0))
                bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

            for i in range(-100, 100):
                ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,0,i), plane_no=(0,0,1))
                bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

            bmesh.update_edit_mesh(context.object.data)
            bm2 = bmesh.new()
            bm2.from_mesh(me) # or from_object(ob, scene)
            #...
            me2 = bpy.data.meshes.new("Sliced")
            bm2.to_mesh(me2)
                                    
                    
        return {"FINISHED"} 

# -----------------------------------------------------------------------------
#
class ForsakenAutoVertexLightOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_auto_vertex_light"
    bl_label = "Forsaken Auto Vertex Light"
    
    def execute(self, context):
        from mathutils import Vector
        from io_scene_forsaken import forsaken_utils
        
        object = context.active_object
        mesh = object.data
            
        if hasattr(mesh, "vertex_colors") is False:
            return {"FINISHED"}  
            
        if len(mesh.vertex_colors) == 0:
            mesh.vertex_colors.new()
        
        #print(len(mesh.vertex_colors))
        #print('mesh verts: ', len(mesh.vertices))
        
        color_layer = mesh.vertex_colors["Col"]
        
        lightTraceInfo = []
        
        # -----------------------------------------------------------------------------
        # iterate every vertex per polygon
        for poly in mesh.polygons:
        
            # -----------------------------------------------------------------------------
            # compute plane equation
            n1 = poly.normal
            vP1 = mesh.vertices[poly.vertices[0]].co
            pd1 = -vP1.dot(n1)
            
            for vert, loop in zip(poly.vertices, poly.loop_indices):
                v = mesh.vertices[vert]
                origin = Vector((v.co.x, v.co.y, v.co.z))
                color_layer.data[loop].color = (0.0, 0.0, 0.0)
                
                # -----------------------------------------------------------------------------
                # test against each light point
                for i, obj in enumerate(context.visible_objects):
                    if obj.actor != True:
                        continue
                    
                    if obj is object:
                        continue
                    
                    if obj.actorType != 'LIGHT':
                        continue
                    
                    # -----------------------------------------------------------------------------
                    # do a raycast from light position to vertex position
                    end = object.matrix_world.inverted() * obj.location
                    dir = (origin - end)
                    dist = math.sqrt(dir.dot(dir))
                    dir.normalize()
                    
                    result = object.ray_cast(end, dir, dist * 0.9) # nudge slightly away
                    
                    if (result[0] == False):
                        bValid = True
                        
                        if obj.rtLightBackfaceCulling == False:
                            # -----------------------------------------------------------------------------
                            # test other rooms to make sure that they're not obstructing the ray
                            dirTmp = object.matrix_world * dir
                            for i, obj2 in enumerate(context.visible_objects):
                                if obj2.actor == True:
                                    continue
                                
                                if obj2 is object:
                                    continue
                                    
                                end2 = obj2.matrix_world.inverted() * obj.location
                                result = obj2.ray_cast(end2, obj2.matrix_world.inverted() * dirTmp, dist * 0.9)
                                if result[0] == True:
                                    bValid = False
                                    break
                                
                        if bValid == False:
                            # it was obstructed by another room
                            continue
                            
                        if obj.rtLightAmbient == False:
                            lightTraceInfo.append(
                            {
                                "dist":     dist,
                                "obj":      obj,
                                "origin":   origin,
                                "end":      end,
                                "poly":     poly,
                                "loop":     loop
                            })
                        else:
                            if dist > obj.empty_draw_size:
                                continue
                                
                            color = color_layer.data[loop].color
                            
                            # if fully black, set the color, otherwise, mix it
                            if color[0] == 0.0 and color[1] == 0.0 and color[2] == 0.0:
                                color_layer.data[loop].color = (obj.rtLightColor[0], obj.rtLightColor[1], obj.rtLightColor[2])
                            else:
                                color_layer.data[loop].color[0] = (obj.rtLightColor[0] - color[0]) * 0.5 + color[0]
                                color_layer.data[loop].color[1] = (obj.rtLightColor[1] - color[1]) * 0.5 + color[1]
                                color_layer.data[loop].color[2] = (obj.rtLightColor[2] - color[2]) * 0.5 + color[2]
                            
                            for poly2 in mesh.polygons:
                                if poly2 is poly:
                                    continue
                                    
                                n2 = poly2.normal
                                
                                # -----------------------------------------------------------------------------
                                # determine center point for this polygon. getting the center from one of
                                # the triangles should be good enough
                                a = mesh.vertices[poly2.vertices[0]].co
                                b = mesh.vertices[poly2.vertices[1]].co
                                c = mesh.vertices[poly2.vertices[2]].co
                                
                                center = (a + b + c) / 3.0
                                    
                                # -----------------------------------------------------------------------------
                                # check for creases between polygons
                                for vert2, loop2 in zip(poly2.vertices, poly2.loop_indices):
                                    v2 = mesh.vertices[vert2]
                                    origin2 = Vector((v2.co.x, v2.co.y, v2.co.z))
                                    
                                    # -----------------------------------------------------------------------------
                                    # check if vertex is shared between the two polygons
                                    delta = origin2 - origin
                                    dist = math.sqrt(delta.dot(delta))
                                    if dist > 0.1:
                                        continue
                                    
                                    # center must be in front of the polygon
                                    if n1.dot(center) + pd1 < 0.0:
                                        continue
                                    
                                    # this edge forms a inward crease. determine occlusion power
                                    min = forsaken_utils.max(forsaken_utils.min(1.0 - obj.rtLightIntensity, 1.0), 0.0)
                                    
                                    d = n1.dot(n2)
                                    d = forsaken_utils.max(d, min)
                                    d = math.pow(d, 0.25 * obj.rtLightIntensity)
                                    d *= d
                                    d *= d
                                    
                                    # darken at this crease
                                    color_layer.data[loop].color[0] *= d
                                    color_layer.data[loop].color[1] *= d
                                    color_layer.data[loop].color[2] *= d
        
        for i, traceInfo in enumerate(lightTraceInfo):
            dist    = traceInfo["dist"]
            obj     = traceInfo["obj"]
            origin  = traceInfo["origin"]
            end     = traceInfo["end"]
            poly    = traceInfo["poly"]
            loop    = traceInfo["loop"]
            
            # -----------------------------------------------------------------------------
            # compute falloff
            dist /= obj.empty_draw_size
            if dist > 1.0:
                dist = 1.0
                
            dist = math.pow(dist, 0.25)
            dist = 1.0 - dist
            
            if dist < obj.rtLightFallOff:
                dist /= obj.rtLightFallOff
            else:
                dist = 1.0
                
            dir = (origin - end).normalized()
            normal = poly.normal
            
            # -----------------------------------------------------------------------------
            # compute lambert
            d = dir.dot(normal)
            lambert = 1.0 - forsaken_utils.max(d, 0.0)
            intensity = forsaken_utils.max(dist * (lambert * 1.0), 0.0)
            intensity = forsaken_utils.min(intensity * obj.rtLightIntensity, 1.0)
            
            if obj.rtLightMixBlend == False:
                color = [0.0, 0.0, 0.0]
                color[0] = obj.rtLightColor[0] * intensity
                color[1] = obj.rtLightColor[1] * intensity
                color[2] = obj.rtLightColor[2] * intensity
                    
                # -----------------------------------------------------------------------------
                # accumulate results
                color_layer.data[loop].color[0] = forsaken_utils.min(color_layer.data[loop].color[0] + color[0], 1.0)
                color_layer.data[loop].color[1] = forsaken_utils.min(color_layer.data[loop].color[1] + color[1], 1.0)
                color_layer.data[loop].color[2] = forsaken_utils.min(color_layer.data[loop].color[2] + color[2], 1.0)
            else:
                color = [0.0, 0.0, 0.0]
                color[0] = obj.rtLightColor[0]
                color[1] = obj.rtLightColor[1]
                color[2] = obj.rtLightColor[2]
                
                dstColor = color_layer.data[loop].color
                color_layer.data[loop].color[0] = (color[0] - dstColor[0]) * intensity + dstColor[0]
                color_layer.data[loop].color[1] = (color[1] - dstColor[1]) * intensity + dstColor[1]
                color_layer.data[loop].color[2] = (color[2] - dstColor[2]) * intensity + dstColor[2]
            
        mesh.update()
        return {"FINISHED"}  
        
# -----------------------------------------------------------------------------
#
class ForsakenSetIgnoreBSPOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_set_ignore_bsp"
    bl_label = "Forsaken Set Ignore BSP"
    
    def execute(self, context):
        obj = context.active_object
        me = obj.data

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            
            ignoreBspLayer = bm.faces.layers.int.get("ignore_bsp")
            if ignoreBspLayer is None is None:
                ignoreBspLayer = bm.faces.layers.int.new("ignore_bsp")
                
            for f in bm.faces:
                if f.select:
                    f[ignoreBspLayer] = 1
                
        
        me.update()
        return {"FINISHED"}  
              
# -----------------------------------------------------------------------------
#
class ForsakenClearIgnoreBSPOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_clear_ignore_bsp"
    bl_label = "Forsaken Clear Ignore BSP"
    
    def execute(self, context):
        obj = context.active_object
        me = obj.data

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            
            ignoreBspLayer = bm.faces.layers.int.get("ignore_bsp")
            if ignoreBspLayer is None is None:
                ignoreBspLayer = bm.faces.layers.int.new("ignore_bsp")
                
            for f in bm.faces:
                if f.select:
                    f[ignoreBspLayer] = 0
                
        
        me.update()
        return {"FINISHED"} 
            
# -----------------------------------------------------------------------------
#
class ForsakenSetTransparentOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_set_transparent"
    bl_label = "Forsaken Set Transparent"
    
    def execute(self, context):
        obj = context.active_object
        me = obj.data

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            
            transparentLayer = bm.faces.layers.int.get("transparent")
            if transparentLayer is None is None:
                transparentLayer = bm.faces.layers.int.new("transparent")
                
            for f in bm.faces:
                if f.select:
                    f[transparentLayer] = 1
                
        
        me.update()
        return {"FINISHED"}  
              
# -----------------------------------------------------------------------------
#
class ForsakenClearTransparentOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_clear_transparent"
    bl_label = "Forsaken Clear Transparent"
    
    def execute(self, context):
        obj = context.active_object
        me = obj.data

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            
            transparentLayer = bm.faces.layers.int.get("transparent")
            if transparentLayer is None is None:
                transparentLayer = bm.faces.layers.int.new("transparent")
                
            for f in bm.faces:
                if f.select:
                    f[transparentLayer] = 0
                
        
        me.update()
        return {"FINISHED"} 
         
# -----------------------------------------------------------------------------
#
class ForsakenSetAnimInstOperator(bpy.types.Operator):
    
    bl_idname = "object.forsaken_set_anim_inst"
    bl_label = "Forsaken Set Animation Instance"
    
    def execute(self, context):
        obj = context.active_object
        me = obj.data

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(me)
            
            animInstanceLayer = bm.faces.layers.string.get("animInstance")
            if animInstanceLayer is None is None:
                animInstanceLayer = bm.faces.layers.string.new("animInstance")
                
            for f in bm.faces:
                if f.select:
                    f[animInstanceLayer] = bytes(context.scene.curAnimInst, 'utf-8')
                
        
        me.update()
        return {"FINISHED"}  
          
# -----------------------------------------------------------------------------
#
class ForsakenFaceInfoPanel(bpy.types.Panel):
    bl_label = "Forsaken Face Info"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        # Only allow in edit mode for a selected mesh.
        return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH"

    def draw(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        face = bm.faces.active
        ignoreBspLayer = bm.faces.layers.int.get("ignore_bsp")
        if ignoreBspLayer is not None:
            row = self.layout.row()
            row.label("Ignore BSP")
            row.label(str(face[ignoreBspLayer]))
            
        transparentLayer = bm.faces.layers.int.get("transparent")
        if transparentLayer is not None:
            row = self.layout.row()
            row.label("Transparency")
            row.label(str(face[transparentLayer]))
            
        animInstanceLayer = bm.faces.layers.string.get("animInstance")
        if animInstanceLayer is not None:
            row = self.layout.row()
            row.label("Anim Instance Object")
            row.label(str(face[animInstanceLayer]))
            
        row = self.layout.row()
        row.label("Face index")
        row.label(str(face.index))
    
# -----------------------------------------------------------------------------
#     
def register():
    bpy.utils.unregister_class(ForsakenUVPanel)
    bpy.utils.register_class(ForsakenUVPanel)
    
    bpy.utils.unregister_class(ForsakenUVAlignOperator)
    bpy.utils.register_class(ForsakenUVAlignOperator)
    
    bpy.utils.unregister_class(ForsakenAutoVertexLightOperator)
    bpy.utils.register_class(ForsakenAutoVertexLightOperator)
    
    bpy.utils.unregister_class(ForsakenSetIgnoreBSPOperator)
    bpy.utils.register_class(ForsakenSetIgnoreBSPOperator)
    
    bpy.utils.unregister_class(ForsakenClearIgnoreBSPOperator)
    bpy.utils.register_class(ForsakenClearIgnoreBSPOperator)
    
    bpy.utils.unregister_class(ForsakenSetTransparentOperator)
    bpy.utils.register_class(ForsakenSetTransparentOperator)
    
    bpy.utils.unregister_class(ForsakenClearTransparentOperator)
    bpy.utils.register_class(ForsakenClearTransparentOperator)
    
    bpy.utils.unregister_class(ForsakenForceSquareTileOperator)
    bpy.utils.register_class(ForsakenForceSquareTileOperator)
    
    bpy.utils.unregister_class(ForsakenSubdivideOperator)
    bpy.utils.register_class(ForsakenSubdivideOperator)
    
    bpy.utils.unregister_class(ForsakenSetAnimInstOperator)
    bpy.utils.register_class(ForsakenSetAnimInstOperator)
    
    bpy.utils.unregister_class(ForsakenFaceInfoPanel)
    bpy.utils.register_class(ForsakenFaceInfoPanel)

# -----------------------------------------------------------------------------
#     
def unregister():
    bpy.utils.unregister_class(ForsakenUVPanel)
    bpy.utils.unregister_class(ForsakenUVAlignOperator)
    bpy.utils.unregister_class(ForsakenAutoVertexLightOperator)
    bpy.utils.unregister_class(ForsakenSetIgnoreBSPOperator)
    bpy.utils.unregister_class(ForsakenClearIgnoreBSPOperator)
    bpy.utils.unregister_class(ForsakenFaceInfoPanel)
    bpy.utils.unregister_class(ForsakenSetTransparentOperator)
    bpy.utils.unregister_class(ForsakenClearTransparentOperator)
    bpy.utils.unregister_class(ForsakenForceSquareTileOperator)
    bpy.utils.unregister_class(ForsakenSubdivideOperator)
    bpy.utils.unregister_class(ForsakenSetAnimInstOperator)
        