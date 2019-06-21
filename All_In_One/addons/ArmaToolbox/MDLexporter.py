'''
Created on 21.02.2014

@author: hfrieden
'''

import bpy
import os
import math
import struct
import bmesh

def stripAddonPath(path):
    if path == "" or path == None: 
        return ""
    if os.path.isabs(path):
        p = os.path.splitdrive(path)
        return p[1][1:]
    elif path[0] == '\\':
        return path[1:]
    else:
        return path
    
    
def getMaterialInfo(face, obj):
    textureName = ""
    materialName = ""
    
    if face.material_index >= 0 and face.material_index < len(obj.material_slots):
        material = obj.material_slots[face.material_index].material
        texType = material.armaMatProps.texType;
    
        if texType == 'Texture':
            textureName = material.armaMatProps.texture;
            textureName = stripAddonPath(textureName);
        elif texType == 'Custom':
            textureName = material.armaMatProps.colorString;
        elif texType == 'Color':
            textureName = "#(argb,8,8,3)color({0:.3f},{1:.3f},{2:.3f},1.0,{3})".format( 
                material.armaMatProps.colorValue.r, 
                material.armaMatProps.colorValue.g, 
                material.armaMatProps.colorValue.b, 
                material.armaMatProps.colorType)

        materialName = stripAddonPath(material.armaMatProps.rvMat)
        
    
    return (materialName, textureName)

def lodKey(obj):
    if obj.armaObjProps.lod == "-1.0":
        return obj.armaObjProps.lodDistance
    else:
        return float(obj.armaObjProps.lod)

def convertWeight(weight):
    if weight > 1:
        weight = 1;
    value = round(255 - 254 * weight)
    
    if value == 255:
        value = 0
        
    #print("weight = ", weight, " value=",value)
    return value

def writeByte(filePtr, value):
    filePtr.write(struct.pack("B", value))

def writeSignature(filePtr, sig):
    filePtr.write(bytes(sig, "UTF-8"))

def writeULong(filePtr, value):
    filePtr.write(struct.pack("I", value))
    
def writeFloat(filePtr, value):
    filePtr.write(struct.pack("f", value))

def writeString(filePtr, value):
    data = value.encode('ASCII')
    packFormat = '<%ds' % (len(data) + 1)
    filePtr.write(struct.pack(packFormat, data))



###
## Export a single object as a LOD into the P3D file        
#
def writeNormals(filePtr, mesh, numberOfNormals):
    for v in range(0,numberOfNormals):
        writeFloat(filePtr, 0)
        writeFloat(filePtr, 1)
        writeFloat(filePtr, 0)
    
    #return v


def writeVertices(filePtr, mesh):
    for v in mesh.vertices:
        writeFloat(filePtr, v.co.x)
        writeFloat(filePtr, v.co.z)
        writeFloat(filePtr, v.co.y)
        writeULong(filePtr, 0)



def writeFaces(filePtr, obj, mesh):
    for idx,face in enumerate(mesh.polygons):
        if len(face.vertices) > 4:
            raise RuntimeError("Model " + obj.name + " contains n-gons and cannot be exported")
        materialName, textureName = getMaterialInfo(face, obj)
        writeULong(filePtr, len(face.vertices))

        # UV'S
        uvs = []
        for i1, loopindex in enumerate(face.loop_indices):
            meshloop = mesh.loops[i1]
            
            try:
                uv = mesh.uv_layers[0].data[loopindex].uv
            except IndexError:
                uv = [0,0]
            uvs.append([uv[0], uv[1]])

        for v in range(len(face.vertices)):
            writeULong(filePtr, face.vertices[v]) # vert id
            writeULong(filePtr, face.vertices[v]) # normal id
            uv = uvs[v]
            #print("u = ", uv[0], "v = ",uv[1])
            uv[1] = 1 - uv[1]
            writeFloat(filePtr, uv[0])
            writeFloat(filePtr, uv[1])
        
        if len(face.vertices) == 3:
            writeULong(filePtr, 0)
            writeULong(filePtr, 0)
            writeFloat(filePtr, 0.0)
            writeFloat(filePtr, 0.0)
        writeULong(filePtr, 0)
        writeString(filePtr, textureName)
        writeString(filePtr, materialName)


def proxyPathStrip(pathName):
    if len(pathName) > 3:
        if pathName[0].upper() == 'P' and pathName[1] == ':':
            pathName = pathName[2:]
    if pathName.find(".p3d") != -1:
        pathName = pathName[:-4]
    return pathName

def proxyIndex(index):
    return "%03d" % (index)

def writeNamedSelection(filePtr, obj, mesh, idx):
    name = obj.vertex_groups[idx].name
    writeByte(filePtr, 1) # Always active
    # Check the name for a proxy name
    if name in obj.armaObjProps.proxyArray:
        proxy = obj.armaObjProps.proxyArray[name]
        name = "proxy:" + proxyPathStrip(proxy.path) + "." + proxyIndex(proxy.index) 
    writeString(filePtr, name)
    writeULong(filePtr, len(mesh.vertices) + len(mesh.polygons))
    for vert in mesh.vertices:
        grps = [grp for grp in vert.groups if grp.group == idx]
        if len(grps) > 0: # Should only ever be 0 or 1
            weight = convertWeight(grps[0].weight)
            if weight < 0 or weight > 255:
                print("Illegal weight " , grps[0].weight, "in group " + name)
            writeByte(filePtr, weight)
        else:
            writeByte(filePtr, 0)
    
    for face in mesh.polygons:
        grps = [grp for vert in face.vertices for grp in mesh.vertices[vert].groups if grp.group == idx]
        if len(grps) == len(face.vertices):
            weight = 0
            for grpF in grps:
                weight += grpF.weight
            if (weight > 0):
                writeByte(filePtr, convertWeight(1))
            else:
                writeByte(filePtr, 0)
        else:
            writeByte(filePtr, 0)

def writeNamedSelections(filePtr, obj, mesh):
    for idx in range(len(obj.vertex_groups)):
        writeNamedSelection(filePtr, obj, mesh, idx)


def writeSharpEdges(filePtr, mesh):
    # First, gather the edges of the flat shaded faces.
    edges = [edge for face in mesh.polygons if not face.use_smooth for edge in face.edge_keys]
    edges = sorted(set(edges))
    # Gather the edges with the "sharp" flag set
    edges2 = [edge for edge in mesh.edges if edge.use_edge_sharp]
    # We need to go through the edges to find the doubles.
    for edge in edges2:
        v1 = edge.vertices[0]
        v2 = edge.vertices[1]
        if not (v1, v2) in edges and not (v2, v1) in edges:
            edges = edges + [(v1, v2)]
    
    if (len(edges) > 0): # Only write this if we have sharp edges
        writeByte(filePtr, 1)
        writeString(filePtr, '#SharpEdges#')
        writeULong(filePtr, len(edges) * 2 * 4)
        for edge in edges:
            writeULong(filePtr, edge[0])
            writeULong(filePtr, edge[1])



def writeMass(filePtr, obj, mesh):
    writeByte(filePtr, 1)
    writeString(filePtr, "#Mass#")
    totalVerts = len(mesh.vertices)
    writeULong(filePtr, totalVerts * 4)
    if (totalVerts > 0):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        weight_layer = bm.verts.layers.float['FHQWeights']
        
        for i in range(0, len(bm.verts)):
            f = bm.verts[i][weight_layer]
            writeFloat(filePtr, f)
    


def writeNamedProperty(filePtr, name, value):
    writeByte(filePtr, 1)
    writeString(filePtr, "#Property#")
    writeULong(filePtr, 128)
    filePtr.write(struct.pack("<64s", name.encode("ASCII")))
    filePtr.write(struct.pack("<64s", value.encode("ASCII")))

""" def writeUVSet(filePtr, layer, mesh, obj, totalUVs, idx):
    writeByte(filePtr, 1)
    writeString(filePtr, "#UVSet#")
    writeULong(filePtr, 4+totalUVs * 8)
    writeULong(filePtr, idx)
    # Write UV Pairs
    for i, face in enumerate(mesh.polygons):
        for vertIdx in range(0, len(face.vertices)):
            uvPair = [0,0]
            try:
                uvPair = [uvPair for 
                    uvPair in 
                    mesh.uv_layers[idx].data[face.index].uv[vertIdx]]
            except Exception as e:
                #print(e)
                pass
            writeFloat(filePtr, uvPair[0])
            writeFloat(filePtr, 1-uvPair[1]) """

def writeUVSet(filePtr, layer, mesh, obj, totalUVs, idx):
    writeByte(filePtr, 1)
    writeString(filePtr, "#UVSet#")
    writeULong(filePtr, 4+totalUVs * 8)
    writeULong(filePtr, idx)
    # Write UV Pairs
    for i, polygon in enumerate(mesh.polygons):
        for vertIdx, loopindex in enumerate(polygon.loop_indices):
            meshloop = mesh.loops[vertIdx]
            uv = mesh.uv_layers[idx].data[loopindex].uv
            uvPair = [uv[0],uv[1]]
            writeFloat(filePtr, uvPair[0])
            writeFloat(filePtr, 1-uvPair[1])

def checkMass(obj, lod, mesh):
    # Check if the LOD is a geometry or physx, and add a dummy selection
    # if it doesn't exist.
    dummyName = "__BLENDER__Dummy"
    for idx in range(len(obj.vertex_groups)):
        name = obj.vertex_groups[idx].name
        if name == dummyName:
            return
    vgrp = obj.vertex_groups.new(dummyName)
    for idx in range(0,len(mesh.vertices)):
        vgrp.add([idx],1,'ADD')


def export_lod(filePtr, obj, wm, idx):
    # Header
    writeSignature(filePtr, 'P3DM')
    writeULong(filePtr, 0x1C)
    writeULong(filePtr, 0x100)
    print("Write lod ",idx)
    wm.progress_update(idx*5)
    
    mesh = obj.data
    #mesh.calc_loop_triangles()
    
    lod = lodKey(obj)
    if lod < 0:
        lod = -lod
    
    #if lod == 1.000e+13 or lod == 4.000e+13:
    #    checkMass(obj, lod, mesh)

    numberOfNormals = 0
    for f in mesh.polygons:
        numberOfNormals = numberOfNormals + len(f.vertices)    
    
    print("Writing Vertices")    
    # Write number of vertices, normals, and faces
    writeULong(filePtr, len(mesh.vertices))         # Number of Vertices
    writeULong(filePtr, numberOfNormals)            # Number of Normals
    writeULong(filePtr, len(mesh.polygons))   # Number of Faces
    writeULong(filePtr, 0)                          # Unused Flags
    
    # Write vertices/Points
    writeVertices(filePtr, mesh)
    wm.progress_update(idx*5+1)
    
    print("Writing Normals")
    # Write normals
    # We can basically write whatever we like here since they are recalculated
    #normalOffsetInFile = filePtr.tell();
    writeNormals(filePtr, mesh, numberOfNormals)
    wm.progress_update(idx*5+2)
            
    print("Writing faces")
    # Write faces
    writeFaces(filePtr, obj, mesh)
    wm.progress_update(idx*5+3)


            
    # Done, now write Taggs
    writeSignature(filePtr, 'TAGG')
    print("taggs: Named selections")
    # Write named selections
    writeNamedSelections(filePtr, obj, mesh)
    print("taggs: sharp edges")
    # Write sharp edges. This isn't the most efficient, but I don't really see a better possibility
    writeSharpEdges(filePtr, mesh)
    wm.progress_update(idx*5+4)
    
    print("taggs: mass (if any)")
    # Write a mass selection if this is a Geometry or PhysX LOD
    if lod == 1.000e+13 or lod == 4.000e+13:
        writeMass(filePtr, obj, mesh)

    print("taggs: named props")
    # Write named properties
    for prop in obj.armaObjProps.namedProps:
        name = prop.name;
        value = prop.value;
        writeNamedProperty(filePtr, name, value)
    
    print("taggs: uvsets")
    # Write UVSets
    # First, count the number of polygon vertices
    totalUVs = 0
    for face in mesh.polygons:
        totalUVs = totalUVs + len(face.vertices)
    
    uvt = mesh.uv_layers
    for i,layer in enumerate(uvt):
        writeUVSet(filePtr, layer, mesh, obj, totalUVs, i)
    
        
    # Close off the LOD
    writeByte(filePtr, True)
    writeString(filePtr, '#EndOfFile#')
    writeULong(filePtr, 0)
    if lod == 1.000e4 or lod == 2.000e4:
        writeFloat(filePtr, lod+obj.armaObjProps.lodDistance)
    else:
        writeFloat(filePtr, lod)
    
    
# Export a couple of meshes to a P3D MLOD files    
def exportMDL(filePtr, selectedOnly):    
    if selectedOnly:
        objects = [obj
                    for obj in bpy.context.selected_objects
                        if obj.type == 'MESH' and obj.armaObjProps.isArmaObject
                  ] 
    else:
        objects = [obj
                   for obj in bpy.data.objects
       
                       if (selectedOnly == False or obj.selected == True)
                          and obj.type == 'MESH'
                          and obj.armaObjProps.isArmaObject
                  ]

    if len(objects) == 0:
        return False
    
    objects = sorted(objects, key=lodKey)

    # Make sure the object is in OBJECT mode, otherwise some of the functions might fail
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Write file header
    writeSignature(filePtr, 'MLOD')
    writeULong(filePtr, 0x101)
    writeULong(filePtr, len(objects))
    
    wm = bpy.context.window_manager
    total = len(objects) * 5
    wm.progress_begin(0, total)
    
    # For each object, export a LOD
    for idx, obj in enumerate(objects):
        export_lod(filePtr, obj, wm, idx)
        
    wm.progress_end()
        