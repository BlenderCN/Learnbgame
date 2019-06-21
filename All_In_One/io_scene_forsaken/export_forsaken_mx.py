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
      
# -----------------------------------------------------------------------------
#  
def get_enum_type(enumTypes, enumStr):
    for e in enumTypes[1]['items']:
        if e[0] == enumStr:
            return e[3]
            
    return 0

# -----------------------------------------------------------------------------
#
def save_mx(context, filepath, use_selection, global_matrix=None, path_mode='AUTO'):
    with open(filepath, 'wb') as data:
        from io_scene_forsaken import forsaken_utils
        from mathutils import Vector
        
        try:
            if global_matrix is None:
                global_matrix = mathutils.Matrix()
                
            forsaken_utils.write32(data, forsaken_utils.PROJECTX_MAGIC_ID)
            forsaken_utils.write32(data, forsaken_utils.MX_VERSION)
            
            scene = context.scene
            
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode='OBJECT')
                
            orig_frame = scene.frame_current
            scene_frames = [orig_frame]
            
            for frame in scene_frames:
                scene.frame_set(frame, 0.0)
                if use_selection:
                    objects = context.selected_objects
                else:
                    objects = scene.objects
                    
            uniqueTextures = []
            spotFX = []
            
            validObjects = 0
            
            # -----------------------------------------------------------------------------
            # iterate objects for unique textures
            for i, ob_main in enumerate(objects):
                obs = [(ob_main, ob_main.matrix_world)]
                
                for ob, ob_mat in obs:
                    if ob.actor == True:
                        if ob.actorType == 'SPOTFX':
                            spotFX.append(ob)
                        
                        continue
                        
                    try:
                        mesh = ob.to_mesh(scene, True, 'PREVIEW')
                    except RuntimeError:
                        mesh = None

                    if mesh is None:
                        continue

                    faceuv = len(mesh.uv_textures) > 0

                    if faceuv:
                        uv_texture = mesh.uv_textures.active.data[:]
                        uv_layer = mesh.uv_layers.active.data[:]
                        
                    # -----------------------------------------------------------------------------
                    # iterate polygons
                    for i, f in enumerate(mesh.polygons):
                        if faceuv:
                            textureName = os.path.basename(uv_texture[f.index].image.filepath)
                        else:
                            textureName = "default"
                            
                        bMatches = False
                        
                        for tx in range(0, len(uniqueTextures)):
                            if uniqueTextures[tx] == textureName:
                                bMatches = True
                                break
                                
                        if bMatches == False:
                            uniqueTextures.append(textureName)
            
            # -----------------------------------------------------------------------------
            # write out unique textures
            forsaken_utils.write16(data, len(uniqueTextures))
            for i in range(0, len(uniqueTextures)):
                forsaken_utils.writeString(data, uniqueTextures[i])
                
            # -----------------------------------------------------------------------------
            # groups
            forsaken_utils.write16(data, len(objects) - len(spotFX))
            
            vertices = []
            tcoords_u = []
            tcoords_v = []
            colors = []
                
            for i, ob_main in enumerate(objects):
                obs = [(ob_main, ob_main.matrix_world)]
                
                scale = ob_main.matrix_world.decompose()[2]
                bInverted = (scale.x < 0 or scale.y < 0 or scale.z < 0)
                
                bStart = False
                
                for ob, ob_mat in obs:
                    if ob.actor == True:
                        continue
                    
                    try:
                        mesh = ob.to_mesh(scene, True, 'PREVIEW')
                    except RuntimeError:
                        mesh = None

                    if mesh is None:
                        continue
                        
                    if bStart == False:
                        # -----------------------------------------------------------------------------
                        # group list count (always 1 for now)
                        forsaken_utils.write16(data, 1)
                        forsaken_utils.write16(data, 0)
                        forsaken_utils.write16(data, 0)
                        bStart = True
                        
                    mesh.transform(global_matrix * ob_mat)
                    forsaken_utils.mesh_triangulate(mesh)
                    
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
                            
                    textureGroups = []
                    
                    for i, f in enumerate(mesh.polygons):
                        f_verts = f.vertices
                        
                        if faceuv:
                            textureName = os.path.basename(uv_texture[f.index].image.filepath)
                        else:
                            textureName = "default"
                            
                        bMatches = False
                        nTexSlot = 0
                        
                        for tx in range(0, len(uniqueTextures)):
                            if uniqueTextures[tx] == textureName:
                                bMatches = True
                                nTexSlot = tx
                                break
                                
                        if bMatches == True:
                            bExists = False
                            for tg in range(0, len(textureGroups)):
                                if textureGroups[tg] == nTexSlot:
                                    bExists = True
                                    break
                            
                            if bExists == False:
                                textureGroups.append(nTexSlot)
                    
                        if has_uv:
                            uv = active_uv_layer[i]
                            uv = uv.uv1, uv.uv2, uv.uv3, uv.uv4
                            
                        if has_vcol:
                            col = active_col_layer[i]
                            col = col.color1[:], col.color2[:], col.color3[:], col.color4[:]
                            
                        for j, vidx in enumerate(f_verts):
                            v = mesh_verts[vidx]
                            
                            if has_uv:
                                uvcoord = uv[j][0], uv[j][1]
                            else:
                                uvcoord = 0.0, 0.0
                                
                            if has_vcol:
                                color = col[j]
                                color = (int(color[0] * 255.0),
                                         int(color[1] * 255.0),
                                         int(color[2] * 255.0),
                                         )
                            else:
                                color = 255, 255, 255
                                
                            vertices.append(Vector(Vector(v.co[:])))
                            tcoords_u.append(uvcoord[0])
                            tcoords_v.append(uvcoord[1])
                            colors.append(color)
                            
                    forsaken_utils.write16(data, len(vertices))
                    
                    for v in range(0, len(vertices)):
                        vVertex = vertices[v]
                        vVertex.x = -vVertex.x
                        
                        forsaken_utils.writeVector(data, vVertex)
                        forsaken_utils.write32(data, 0)
                        forsaken_utils.write8(data, colors[v][2])
                        forsaken_utils.write8(data, colors[v][1])
                        forsaken_utils.write8(data, colors[v][0])
                        forsaken_utils.write8(data, 0xff)
                        forsaken_utils.write32(data, 0)
                        forsaken_utils.writeFloat(data, tcoords_u[v])
                        forsaken_utils.writeFloat(data, 1.0 - tcoords_v[v])
                        
                    forsaken_utils.mesh_triangulate(mesh)
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
                            
                    forsaken_utils.write16(data, len(textureGroups))
                    
                    for i, tg in enumerate(textureGroups):
                        forsaken_utils.write16(data, 0)
                        forsaken_utils.write16(data, 0)
                        forsaken_utils.write16(data, 0)
                        forsaken_utils.write16(data, tg)
                        
                        indices = []
                        polys = []
                        
                        for i, f in enumerate(mesh.polygons):
                            if faceuv:
                                textureName = os.path.basename(uv_texture[f.index].image.filepath)
                            else:
                                textureName = "default"
                                
                            bMatches = False
                            
                            for tx in range(0, len(uniqueTextures)):
                                if uniqueTextures[tx] == textureName:
                                    if textureGroups[tx] == tg:
                                        bMatches = True
                                        break
                                        
                            if bMatches == False:
                                continue
                                
                            polys.append(f)
                            
                            for j, loop in enumerate(f.loop_indices):
                                indices.append(loop)
                                
                        nTrisLen = len(indices)
                        nTrisLen /= 3
                        
                        forsaken_utils.write16(data, int(nTrisLen))
                        
                        for j in range(int(nTrisLen)):
                            if bInverted is not True:
                                forsaken_utils.write16(data, indices[j * 3 + 2])
                                forsaken_utils.write16(data, indices[j * 3 + 1])
                                forsaken_utils.write16(data, indices[j * 3 + 0])
                            else:
                                forsaken_utils.write16(data, indices[j * 3 + 0])
                                forsaken_utils.write16(data, indices[j * 3 + 1])
                                forsaken_utils.write16(data, indices[j * 3 + 2])
                            
                            forsaken_utils.write16(data, 0)
                            
                            normal = Vector(polys[j].normal)
                            forsaken_utils.writeVector(data, normal)
                            
            forsaken_utils.write16(data, 0) # mxa format
            forsaken_utils.write16(data, 0) # num animations
            
            if len(spotFX) != 0:
                forsaken_utils.write16(data, 1)
                forsaken_utils.write16(data, 0) # num firepoints
                forsaken_utils.write16(data, len(spotFX))
                for s, spotFX in enumerate(spotFX):
                    rotation = spotFX.rotation_euler.to_matrix()
        
                    direction = Vector(global_matrix * Vector(rotation * Vector((0.0, 1.0, 0.0))))
                    direction.normalize()
                    
                    upVector = Vector(global_matrix * Vector(rotation * Vector((0.0, 0.0, 1.0))))
                    upVector.normalize()
                    
                    forsaken_utils.write16(data, get_enum_type(bpy.types.Object.fxType, spotFX.fxType))
                    forsaken_utils.writeVector(data, Vector(global_matrix * Vector(spotFX.location)))
                    forsaken_utils.writeVector(data, direction)
                    forsaken_utils.writeVector(data, upVector)
                    forsaken_utils.writeFloat(data, spotFX.fxGen.genDelay)
                    forsaken_utils.writeFloat(data, spotFX.fxActiveDelay)
                    forsaken_utils.writeFloat(data, spotFX.fxInactiveDelay)
                    forsaken_utils.write16(data, get_enum_type(bpy.types.Object.fxPrimaryID, spotFX.fxPrimaryID))
                    forsaken_utils.write16(data, get_enum_type(bpy.types.Object.fxSecondaryID, spotFX.fxSecondaryID))
                    forsaken_utils.write8(data, int(spotFX.fxColor[2] * 255.0))
                    forsaken_utils.write8(data, int(spotFX.fxColor[1] * 255.0))
                    forsaken_utils.write8(data, int(spotFX.fxColor[0] * 255.0))
                    forsaken_utils.write8(data, 0xff)
                    forsaken_utils.writeString(data, spotFX.fxSFX)
                    forsaken_utils.writeFloat(data, spotFX.fxVolume)
                    forsaken_utils.writeFloat(data, spotFX.fxSpeed)
            else:
                forsaken_utils.write16(data, 0)
                
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
    
    save_mx(context, filepath, use_selection, global_matrix, path_mode)
    return {'FINISHED'}
    