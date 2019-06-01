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
import struct
from mathutils import Vector

PROJECTX_MAGIC_ID   = 0x584A5250

# -----------------------------------------------------------------------------
#
def max(a, b):
    if a > b :
        return a
    return b

# -----------------------------------------------------------------------------
#
def min(a, b):
    if a < b :
        return a
    return b

# -----------------------------------------------------------------------------
#
def read32(data):
    result = read8(data)
    result += read8(data) * 256
    result += read8(data) * 65536
    result += read8(data) * 16777216
    return result

# -----------------------------------------------------------------------------
#
def read16(data):
    result = read8(data)
    result += (read8(data) * 256)
    return result

# -----------------------------------------------------------------------------
#
def read8(data):
    val = data.read(1)
    return int.from_bytes(val, byteorder='little')

# -----------------------------------------------------------------------------
#
def readFloat(data):
    return struct.unpack('f', data.read(4))[0]
    
# -----------------------------------------------------------------------------
#
def readVector(data):
    return Vector((readFloat(data), readFloat(data), readFloat(data)))

# -----------------------------------------------------------------------------
#
def readString(data):
    string = ""
    while 1:
        c = read8(data)
        if c == 0:
            break
            
        string += str(chr(c))
        
    return string
    
# -----------------------------------------------------------------------------
#
def write8(data, val):
    data.write(struct.pack("B", val))
    
# -----------------------------------------------------------------------------
#
def write16(data, val):
    write8(data, (val & 0xff))
    write8(data, ((val >> 8) & 0xff))
    
# -----------------------------------------------------------------------------
#
def write32(data, val):
    write8(data, val & 0xff);
    write8(data, (val >> 8) & 0xff);
    write8(data, (val >> 16) & 0xff);
    write8(data, (val >> 24) & 0xff);

# -----------------------------------------------------------------------------
#  
def writeFloat(data, val):
    data.write(struct.pack('f', val))

# -----------------------------------------------------------------------------
#  
def writeString(data, str):
    strLen = len(str)
    
    for i in range(0, strLen):
        write8(data, ord(str[i]))
        
    write8(data, 0)
   
# -----------------------------------------------------------------------------
#   
def writeVector(data, vec):
    writeFloat(data, vec.x)
    writeFloat(data, vec.y)
    writeFloat(data, vec.z)

# -----------------------------------------------------------------------------
#
def mesh_triangulate(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

MX_VERSION  = 2
MXA_VERSION = 2

# -----------------------------------------------------------------------------
#
def load_mx(filepath, global_matrix):
    with open(filepath, 'rb') as data:
    
        data.seek(0)
        
        # -----------------------------------------------------------------------------
        # verify file header and version
        magic = read32(data)
        version = read32(data)
        
        if magic != PROJECTX_MAGIC_ID:
            return None
        
        if version != MX_VERSION:
            return None
        
        # -----------------------------------------------------------------------------
        # setup and read texture name list
        nTextures = read16(data)
        texFiles = [""] * nTextures
        
        for i in range(0, nTextures):
            texFiles[i] = readString(data)
            
        nGroups = read16(data)
        
        vertices = []
        coords = []
        colors = []
        indices = []
        indices2 = []
        textures = []
        images = []
        
        nTotalTris = 0;
        
        # -----------------------------------------------------------------------------
        # iterate groups
        for i in range(0, nGroups):
            nLists = read16(data)
            
            for j in range(0, nLists):
                read16(data)
                read16(data)
                
                nVerts = read16(data)
                
                # -----------------------------------------------------------------------------
                # read vertices
                for v in range(0, nVerts):
                    vPos = Vector(global_matrix * readVector(data))
                    
                    vertices.append(vPos)
                    
                    read32(data)
                    
                    b = float(read8(data)) / 255.0
                    g = float(read8(data)) / 255.0
                    r = float(read8(data)) / 255.0
                    
                    colors.append((r, g, b))
                        
                    read8(data)
                    read32(data)
                    
                    coords.append((readFloat(data), 1.0 - readFloat(data)))
                    
                nTGroups = read16(data)
                nCurTris = 0
                
                # -----------------------------------------------------------------------------
                # read texture groups
                for t in range(0, nTGroups):
                    read16(data)
                    read16(data)
                    read16(data)
                    
                    nTexSlot = read16(data)
                    
                    nTris = read16(data)
                    
                    # -----------------------------------------------------------------------------
                    # read triangle indices
                    for tri in range(0, nTris):
                        v2 = read16(data) + nTotalTris
                        v1 = read16(data) + nTotalTris
                        v0 = read16(data) + nTotalTris
                        
                        textures.append(nTexSlot)
                        
                        indices.append((v2, v1, v0))
                        
                        indices2.append(v2)
                        indices2.append(v1)
                        indices2.append(v0)
                        
                        read16(data)
                        
                        readFloat(data)
                        readFloat(data)
                        readFloat(data)
                        
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
        for i in range(0, nTextures):
            realpath = os.path.expanduser(os.path.dirname(os.path.realpath(filepath)) + '/Textures/' + texFiles[i])
            try:
                img = bpy.data.images.load(realpath)
            except:
                raise NameError("Cannot load image %s" % realpath)
                
            images.append(img)
        
        # -----------------------------------------------------------------------------
        # assign texture images to polygons
        for i, f in enumerate(mesh.polygons):
            texID = textures[f.index]
            if texID >= len(images):
                continue
            
            mesh.uv_textures.active.data[f.index].image = images[texID]
        
        # -----------------------------------------------------------------------------
        # assign UV coordinates to polygons
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(mesh)

        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()

        for f in bm.faces:
            for l in f.loops:
                luv = l[uv_layer]
                luv.uv = coords[l.vert.index]
                    

        bmesh.update_edit_mesh(mesh)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return obj
        