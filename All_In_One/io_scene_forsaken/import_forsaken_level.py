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
import bmesh
from mathutils import Vector
from mathutils import Quaternion
from mathutils import Matrix

MXV_VERSION = 3
FX_VERSION  = 4
      
# -----------------------------------------------------------------------------
#  
def get_enum_type(enumTypes, num):
    for e in enumTypes[1]['items']:
        if e[3] == num:
            return e[0]
            
    return 'NONE'
 
# -----------------------------------------------------------------------------
#  
def quaternion_from_two_vectors(dir, up):
    from io_scene_forsaken import forsaken_utils
    
    vU1 = dir
    vU2 = up
    
    vU1.normalize()
    vU2.normalize()
    
    vAxis = vU1.cross(vU2)

    fAxisMag = forsaken_utils.min(math.sqrt(vAxis.x*vAxis.x+vAxis.y*vAxis.y+vAxis.z*vAxis.z), 1.0)
    fTheta = math.asin(fAxisMag)
    fTheta_C = math.pi - fTheta
    
    if vU1.dot(vU2) < 0.0:
        fTheta = fTheta_C
        fTheta_C = math.pi - fTheta
        
    fEpsilon = 1e-7

    if fTheta < fEpsilon:
        qRot = Quaternion()
        qRot.x = 0.0
        qRot.y = 0.0
        qRot.z = 0.0
        qRot.w = 1.0
        return qRot
        
    if fTheta_C < fEpsilon:
        vCP = vU1.cross(Vector((1.0, 0.0, 0.0)))
        
        fOpposite = vCP.x*vCP.x+vCP.y*vCP.y+vCP.z*vCP.z
        
        if fOpposite >= fEpsilon:
            vAxis = vCP
        else:
            vAxis = Vector((0.0, 1.0, 0.0))
            
    vAxis.normalize()
    
    qRot = Quaternion()
    s = math.sin(fTheta * 0.5)
    c = math.cos(fTheta * 0.5)
    
    qRot.x = vAxis.x * s
    qRot.y = vAxis.y * s
    qRot.z = vAxis.z * s
    qRot.w = c
    
    qRot.normalize()
    return qRot
    
# -----------------------------------------------------------------------------
#  
def quaternion_from_dir_and_up(dir, up):
    from io_scene_forsaken import forsaken_utils
    
    qDir = quaternion_from_two_vectors(dir, Vector((0.0, 1.0, 0.0)))
    vUpAxis = Vector((0.0, 0.0, 1.0)) * qDir.to_matrix()
    vUpAxis.normalize()
    qRot = quaternion_from_two_vectors(up, vUpAxis)
    qRot.rotate(qDir)
    qRot.normalize()
    
    return qRot
    
# -----------------------------------------------------------------------------
#
def load_fx(operator, context, filepath, global_matrix):
    with open(filepath, 'rb') as data:
        from io_scene_forsaken import forsaken_utils
        
        data.seek(0)
        
        # -----------------------------------------------------------------------------
        # verify file header and version
        magic = forsaken_utils.read32(data)
        version = forsaken_utils.read32(data)
        
        if magic != forsaken_utils.PROJECTX_MAGIC_ID:
            print('%s is not a valid PRJX file' % filepath)
            return
        
        if version != FX_VERSION:
            print('%s has invalid version number' % filepath)
            return
            
        nFX = forsaken_utils.read32(data)
        for i in range(0, nFX):
            type = forsaken_utils.read16(data)
            group = forsaken_utils.read16(data)
            color = forsaken_utils.read32(data)
            pos = Vector(global_matrix * forsaken_utils.readVector(data))
            dir = Vector(global_matrix * forsaken_utils.readVector(data))
            up = Vector(global_matrix * forsaken_utils.readVector(data))
            activeDelay = forsaken_utils.readFloat(data)
            inactiveDelay = forsaken_utils.readFloat(data)
            genType = forsaken_utils.read16(data)
            genDelay = forsaken_utils.readFloat(data)
            primary = forsaken_utils.read16(data)
            secondary = forsaken_utils.read16(data)
            sfxName = forsaken_utils.readString(data)
            volume = forsaken_utils.readFloat(data)
            speed = forsaken_utils.readFloat(data)
            sfxType = forsaken_utils.read16(data)
            
            pos.x = -pos.x
            
            dir.normalize()
            up.normalize()
            
            bpy.ops.mesh.primitive_cube_add(location=pos)
            obj = bpy.context.active_object
            obj.scale = (0.125, 0.125, 0.125)
            obj.show_name = True
            obj.show_axis = True
            obj.name = 'SpotFX.000'
            
            obj.actor = True
            obj.actorType = 'SPOTFX'
            obj.fxGen.genType = get_enum_type(bpy.types.GeneratePropertyGroup.genType, genType)
            obj.fxGen.genDelay = genDelay
            obj.fxActiveDelay = activeDelay
            obj.fxInactiveDelay = inactiveDelay
            obj.fxPrimaryID = get_enum_type(bpy.types.Object.fxPrimaryID, primary)
            obj.fxSecondaryID = get_enum_type(bpy.types.Object.fxSecondaryID, secondary)
            obj.fxSFX = sfxName
            obj.fxVolume = volume
            obj.fxSpeed = speed
            obj.fxType = get_enum_type(bpy.types.Object.fxType, type)
            obj.sfxType = get_enum_type(bpy.types.Object.sfxType, sfxType)
            obj.rotation_euler = quaternion_from_dir_and_up(dir, up).to_euler('XYZ')
            obj.rotation_euler.x = -obj.rotation_euler.x
    
# -----------------------------------------------------------------------------
#
def load_mxv(operator, context, filepath, global_matrix):
    with open(filepath, 'rb') as data:
        from io_scene_forsaken import forsaken_utils
        
        data.seek(0)
        
        # -----------------------------------------------------------------------------
        # verify file header and version
        magic = forsaken_utils.read32(data)
        version = forsaken_utils.read32(data)
        
        if magic != forsaken_utils.PROJECTX_MAGIC_ID:
            print('%s is not a valid PRJX file' % filepath)
            return
        
        if version != MXV_VERSION:
            print('%s has invalid version number' % filepath)
            return
            
        # -----------------------------------------------------------------------------
        # setup and read texture name list
        nTextures = forsaken_utils.read16(data)
        texFiles = [""] * nTextures
        
        for i in range(0, nTextures):
            texFiles[i] = forsaken_utils.readString(data)
            
        nGroups = forsaken_utils.read16(data)
        groupObjs = [None] * nGroups
        
        # -----------------------------------------------------------------------------
        # iterate groups
        for i in range(0, nGroups):
            nLists = forsaken_utils.read16(data)
            
            vertices = []
            coords = []
            colors = []
            indices = []
            indices2 = []
            textures = []
            images = []
            
            nTotalTris = 0;
            
            for j in range(0, nLists):
                forsaken_utils.read16(data)
                forsaken_utils.read16(data)
                
                nVerts = forsaken_utils.read16(data)
                
                # -----------------------------------------------------------------------------
                # read vertices
                for v in range(0, nVerts):
                    vPos = Vector(global_matrix * forsaken_utils.readVector(data))
                    vPos.x = -vPos.x
                    
                    vertices.append(vPos)
                    
                    forsaken_utils.read32(data)
                    
                    b = float(forsaken_utils.read8(data)) / 255.0
                    g = float(forsaken_utils.read8(data)) / 255.0
                    r = float(forsaken_utils.read8(data)) / 255.0
                    
                    colors.append((r, g, b))
                        
                    forsaken_utils.read8(data)
                    forsaken_utils.read32(data)
                    
                    coords.append((forsaken_utils.readFloat(data), 1.0 - forsaken_utils.readFloat(data)))
                    
                nTGroups = forsaken_utils.read16(data)
                nCurTris = 0

                # -----------------------------------------------------------------------------
                # read texture groups
                for t in range(0, nTGroups):
                    forsaken_utils.read16(data)
                    forsaken_utils.read16(data)
                    forsaken_utils.read16(data)
                    
                    nTexSlot = forsaken_utils.read16(data)
                    
                    nTris = forsaken_utils.read16(data)
                    
                    # -----------------------------------------------------------------------------
                    # read triangle indices
                    for tri in range(0, nTris):
                        v0 = forsaken_utils.read16(data) + nTotalTris
                        v1 = forsaken_utils.read16(data) + nTotalTris
                        v2 = forsaken_utils.read16(data) + nTotalTris
                        
                        textures.append(nTexSlot)
                        
                        indices.append((v2, v1, v0))
                        
                        indices2.append(v2)
                        indices2.append(v1)
                        indices2.append(v0)
                        
                        forsaken_utils.read16(data)
                        
                        forsaken_utils.readFloat(data)
                        forsaken_utils.readFloat(data)
                        forsaken_utils.readFloat(data)
                        
                        # we'll be merging indices for all texture groups into one list
                        nCurTris = max(max(max(nCurTris, v0), v1), v2);
                        
                nTotalTris = nCurTris+1;
                
            # -----------------------------------------------------------------------------
            # create mesh object
            mesh = bpy.data.meshes.new('mesh')
            mesh.from_pydata(vertices, [], indices)
            mesh.update(calc_edges=True)
            mesh.validate(clean_customdata=False)
            mesh.update()

            scene = bpy.context.scene
            
            # -----------------------------------------------------------------------------
            # create scene object
            obj = bpy.data.objects.new(os.path.basename(filepath), mesh)
            scene.objects.link(obj)
            scene.objects.active = obj
            obj.select = True
            
            # -----------------------------------------------------------------------------
            # create color layer and assign vertex colors
            mesh.vertex_colors.new()
            color_layer = mesh.vertex_colors["Col"]
            for poly in mesh.polygons:
                for vert, loop in zip(poly.vertices, poly.loop_indices):
                    color_layer.data[loop].color = colors[vert]
                    
            # -----------------------------------------------------------------------------
            # create uv textures
            uvtex = mesh.uv_textures.new()
            uvtex.name = "MXUV"
            
            mesh.uv_textures["MXUV"].active = True
            mesh.uv_textures["MXUV"].active_render = True
            
            # -----------------------------------------------------------------------------
            # fetch texture image files
            for t in range(0, nTextures):
                realpath = os.path.expanduser(os.path.dirname(os.path.realpath(filepath)) + '/Textures/' + texFiles[t])
                img = None
                
                try:
                    img = bpy.data.images.load(realpath)
                except:
                    print("Cannot load image %s" % realpath)
                    
                images.append(img)
                
            # -----------------------------------------------------------------------------
            # assign texture images to polygons
            for ii, f in enumerate(mesh.polygons):
                texID = textures[f.index]
                if texID >= len(images):
                    continue
                
                mesh.uv_textures.active.data[f.index].image = images[texID]
            
            # -----------------------------------------------------------------------------
            # assign UV coordinates to polygons
            scene.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.tris_convert_to_quads()

            bm = bmesh.from_edit_mesh(mesh)

            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()

            for f in bm.faces:
                for l in f.loops:
                    luv = l[uv_layer]
                    luv.uv = coords[l.vert.index]
                        
            bmesh.update_edit_mesh(mesh)
            bpy.ops.object.mode_set(mode='OBJECT')
            scene.objects.active = None
            obj.select = False
            obj.name = 'group%03d' % i
            groupObjs[i] = obj
            
        # skip
        forsaken_utils.read16(data)
        
        for i in range(0, nGroups):
            groupObjs[i].name = forsaken_utils.readString(data)
            forsaken_utils.readVector(data)
            forsaken_utils.readVector(data)
            
            nPortals = forsaken_utils.read16(data)
            for j in range(0, nPortals):
                nPoints = forsaken_utils.read16(data)
                vertices = []
                
                for v in range(0, nPoints):
                    vPos = Vector(global_matrix * forsaken_utils.readVector(data))
                    vPos.x = -vPos.x
                    
                nFaces = forsaken_utils.read16(data)
                totalTris = 0
                indices = []
                
                for f in range(0, nFaces):
                    type = forsaken_utils.read32(data)
                    normal = forsaken_utils.readVector(data)
                    d = forsaken_utils.readFloat(data)
                    
                    vCoords = [0.0] * 4 * 2
                    
                    for t in range(0, 4):
                        vCoords[t * 2 + 0] = forsaken_utils.readFloat(data)
                        vCoords[t * 2 + 1] = forsaken_utils.readFloat(data)
                        
                    vertCount = (type & 1) + 3
                    for vc in range(0, vertCount):
                        polyType = (type & 6)
                        x = 0.0
                        y = 0.0
                        z = 0.0
                        
                        if polyType == 0:
                            y = vCoords[vc * 2 + 0]
                            z = vCoords[vc * 2 + 1]
                            x = -(d + (y * normal.y + z * normal.z)) / normal.x
                            
                        elif polyType == 2:
                            x = vCoords[vc * 2 + 0]
                            z = vCoords[vc * 2 + 1]
                            y = -(d + (x * normal.x + z * normal.z)) / normal.y
                            
                        elif polyType == 4:
                            x = vCoords[vc * 2 + 0]
                            y = vCoords[vc * 2 + 1]
                            z = -(d + (x * normal.x + y * normal.y)) / normal.z
                            
                        portalVert = Vector(global_matrix * Vector((x, y, z)))
                        portalVert.x = -portalVert.x
                        
                        vertices.append(portalVert)
                        
                    for vc in range(0, (vertCount - 2)):
                        indices.append((totalTris + vc + 2, totalTris + vc + 1, totalTris))
                        
                    totalTris += vertCount
                        
                portalName = 'portal_%02d_%02d' % (i, j)
                me = bpy.data.meshes.new(portalName)
                ob = bpy.data.objects.new(portalName, me)
                bpy.context.scene.objects.link(ob)
                me.from_pydata(vertices, [], indices)
                me.update()
    
# -----------------------------------------------------------------------------
#
def load(operator, context, filepath, global_matrix):
    fileName = os.path.splitext(filepath)[0]
    load_mxv(operator, context, filepath, global_matrix)
    load_fx(operator, context, fileName + '.fx', global_matrix)
    
    return {'FINISHED'}
    