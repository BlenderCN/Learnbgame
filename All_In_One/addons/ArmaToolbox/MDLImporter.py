'''
Created on 06.12.2013

@author: hfrieden

Import an Arma 2/Arma 3 unbinarized MDL file

'''
import struct
import bpy
import bmesh
import os.path as path
import ArmaToolbox
import ArmaTools

def getLayerMask(layer):
    res = [False, False, False, False, False,
           False, False, False, False, False,
           False, False, False, False, False,
           False, False, False, False, False]
    res[layer % 20] = True
    return res

# Datatype reading
def readULong(filePtr):
    return struct.unpack("i", filePtr.read(4))[0]

def readSignature(filePtr):
    return filePtr.read(4)

def readFloat(filePtr):
    return struct.unpack("f", filePtr.read(4))[0]

def readChar(filePtr):
    return struct.unpack("c", filePtr.read(1))[0]

def readByte(filePtr):
    return struct.unpack("b", filePtr.read(1))[0]

def readString(filePtr):
    res = b''
    t = True
    while t:
        a = filePtr.read(1)
        if a != b'\000':
            res = res + a
        else:
            t = False
    
    return res.decode("utf-8")

def makeLodName(fileName, lodLevel):
    lodName = path.basename(fileName)
    lodName = lodName.split(".")[0]
    lodName = "{0}.{1}".format(lodName, lodLevel)
    return lodName

def maybeAddEdgeSplit(obj):
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = 3.1415927

    #modifier = obj.modifiers.get("FHQ_ARMA_Toolbox_EdgeSplit")
    #if modifier is None:
    #    modifier = obj.modifiers.new("FHQ_ARMA_Toolbox_EdgeSplit",
    #             type='EDGE_SPLIT')
    #    
    #    modifier.show_expanded = False
    #    modifier.use_edge_angle = False # Want only sharp edges
    #    modifier.use_edge_sharp = True

    #obj.data.show_edge_sharp = True

def correctedResolution(r):
    res = int(r)
   
    if (r < 1000):
        return r #res
    
    values ={
        10000000000000 : 'G',
        3000000000000000 : 'RD',
        #11010 : 'SV2',
        8000000000000000 : 'VCG',
        10000 : 'S1',
        14000000000000000 : 'VPFG',
        17000000000000000 : 'SP',
        #10010 : 'S2',
        12000000000000000 : 'VCFG',
        20000000000000000 : 'SVVG',
        1200 : 'VC',
        9000000000000000 : 'VCFG',
        15000000000000000 : 'VGG',
        13000000000000000 : 'VPG',
        18000000000000000 : 'SVVC',
        1000000000000000 : 'M',
        1100 : 'P',
        21000000000000000 : 'WRL',
        4000000000000000 : 'PTH',
        40000000000000 : 'GPX',
        7000000000000000 : 'FG',
        10000000000000000 : 'VC',
        6000000000000000 : 'VG',
        1000 : 'GN',
        16000000000000000 : 'VGFG',
        20000000000000 : 'GB',
        19000000000000000 : 'SVVP',
        2000000000000000 : 'LC',
        11000 : 'SV1',
        20000 : 'ED',
        5000000000000000 : 'HP',
        11000000000000000 : 'VCG', 
    }
    error = 1000000000000000000000
    value = -1
    for n in values:
        x = abs(n-res)
        if x < error:
            error = x
            value = n
    return value

def resolutionName(r):
    res = int(r)
   
    if (r < 1000):
        return str(res)
    
    values ={
        1.000e+3:'View Gunner',
        1.100e+3:'View Pilot',
        1.200e+3:'View Cargo',
        1.000e+4:'Stencil Shadow',
        2.000e+4:'Edit',
        #1.001e+4:'Stencil Shadow 2',
        1.100e+4:'Shadow Volume',
        #1.101e+4:'Shadow Volume 2',
        1.000e+13:'Geometry',
        1.000e+15:'Memory',
        2.000e+15:'Land Contact',
        3.000e+15:'Roadway',
        4.000e+15:'Paths',
        5.000e+15:'Hit Points',
        6.000e+15:'View Geometry',
        7.000e+15:'Fire Geometry',
        8.000e+15:'View Cargo Geometry',
        9.000e+15:'View Cargo Fire Geometry',
        1.000e+16:'View Commander',
        1.100e+16:'View Commander Geometry',
        1.200e+16:'View Commander Fire Geometry',
        1.300e+16:'View Pilot Geometry',
        1.400e+16:'View Pilot Fire Geometry',
        1.500e+16:'View Gunner Geometry',
        1.600e+16:'View Gunner Fire Geometry',
        1.700e+16:'Sub Parts',
        1.800e+16:'Cargo View shadow volume',
        1.900e+16:'Pilot View shadow volume',
        2.000e+16:'Gunner View shadow volume',
        2.100e+16:'Wreckage',
        2.000e+13:'Geometry Buoyancy',
        4.000e+13:'Geometry PhysX'
    }
    error = 1000000000000000000000
    value = -1
    for n in values:
        x = abs(n-res)
        if x < error:
            error = x
            value = n
    ret = values.get(value, "?")
    if value == 1.000e+4 or value == 2.000e+4:
        ret = ret + " " + str(r-value)
    
    return ret

def decodeWeight(b):
    if  b == 0:
        return  0.0
    elif b == 2:
        return 1.0
    elif b > 2:
        return 1.0 - round( (b-2) / 2.55555 )*0.01
    elif b < 0:
        return -round( b / 2.55555 ) * 0.01
    else:
        # print ("decodeWeight(",b,") returns 1.0 as else case")
        return 1.0 #TODO: Correct?

def loadLOD(context, filePtr, objectName, materialData, layerFlag, lodnr):
    global objectLayers
    meshName = objectName
    weightArray = []
    # Check for P3DM signature
    sig = readSignature(filePtr)
    if sig != b'P3DM':
        return -1
    
    # Read major and minor version
    major = readULong(filePtr)
    minor = readULong(filePtr)
    if major != 0x1c:
        print("Unknown major version {0}".format(major))
        return -1
    if minor != 0x100:
        print("Unknown minor version {0}".fomrat(minor))
        return -1
    
    numPoints   = readULong(filePtr)
    numNormals  = readULong(filePtr)
    numFaces    = readULong(filePtr)
    print("read lod")
    dummyFlags  = readULong(filePtr)
    
    # Read the Points. Points are XYZTriples followed by an ULONG flags word
    verts = []
    for i in range(0, numPoints):
        point = struct.unpack("fffi", filePtr.read(16))
        pnt = [point[0],  point[2], point[1]]
        verts.append(pnt)
    
    print("normals...")    
    normals = []
    for i in range(0, numNormals):
        normal = struct.unpack("fff", filePtr.read(12))
        nrm = [normal[0], normal[1], normal[2]]
        normals.append(normal)
    

    faceData = []
    faces = []
    print("faces...")
    # Start reading and adding faces
    for i in range(0, numFaces):
        numSides = readULong(filePtr)
        # Vertex table
        vIdx = []
        nrmIdx = []
        uvs = []
        for n in range(0, 4):
            vtable = struct.unpack("iiff", filePtr.read(16))
            if n<numSides:
                vIdx.append(vtable[0])
                nrmIdx.append(vtable[1])
                uvs.append( [vtable[2], vtable[3]])
        faceFlags = readULong(filePtr)
        textureName = readString(filePtr)
        materialName = readString(filePtr)
        faceData.append(
            (numSides, nrmIdx, uvs, faceFlags, textureName, materialName)
        )
        faces.append(vIdx)
        # Handle the material if it doesn't exists yet
        if len(textureName) > 0 or  len(materialName)>0:
            try:
                materialData[(textureName, materialName)]
            except:
                # Need to create a new material for this
                #mat =  bpy.data.materials.new("Arma Material")
                mat = bpy.data.materials.new(path.basename(textureName) + " :: " + path.basename(materialName))
                mat.armaMatProps.colorString = textureName
                mat.armaMatProps.rvMat   = materialName
                if len(textureName) > 0 and textureName[0] == '#':
                    mat.armaMatProps.texType = 'Custom'
                    mat.armaMatProps.colorString = textureName
                else:
                    mat.armaMatProps.texType = 'Texture'
                    mat.armaMatProps.texture = textureName
                    mat.armaMatProps.colorString = ""
                    
                materialData[(textureName, materialName)] = mat
            
    
    if readSignature(filePtr) != b'TAGG':
        print("No tagg signature")
        return -1;
    
    # Create the mesh. Doing it here makes the named selections
    # easier to read.
    mymesh = bpy.data.meshes.new(name=meshName)
    mymesh.from_pydata(verts, [], faces) 

    mymesh.update(calc_edges = True)

    obj = bpy.data.objects.new(meshName, mymesh)
    
    # TODO: Maybe add a "logical Collection" option that
    # Collects all geometries, shadows, custom etc in a collection.

    scn = bpy.context.scene

    coll = bpy.data.collections.new(meshName)
    context.scene.collection.children.link(coll)
    coll.objects.link(obj)
    
    #NEIN! coll.hide_viewport = True
    #scn.objects.link(obj)
    #scn.objects.active = obj   
    
    print("taggs")    
    loop = True
    sharpEdges = None
    weight = None
    while loop:
        active = readChar(filePtr)
        tagName = readString(filePtr)
        
        numBytes = readULong(filePtr)
        
        #print ("tagg: ",tagName, " size ", numBytes)
        
        if active == b'\000':
            if numBytes != 0:
                filePtr.seek(numBytes, 1)
        else:
            if tagName == "#EndOfFile#":
                loop = False
            elif tagName == "#SharpEdges#":
                # Read Sharp Edges
                sharpEdges = []
                for i in range(0,numBytes,8):
                    n1 = readULong(filePtr)
                    n2 = readULong(filePtr)
                    sharpEdges.append([n1, n2])
                #print (sharpEdges)
            elif tagName == "#Property#":
                # Read named property
                propName  = struct.unpack("64s", filePtr.read(64))[0].decode("utf-8")
                propValue = struct.unpack("64s", filePtr.read(64))[0].decode("utf-8")
                item = obj.armaObjProps.namedProps.add()
                item.name=propName;
                item.value=propValue
            elif tagName == "#UVSet#":
                id = readULong(filePtr)
                layerName = "UVSet " + str(id)
                #print("adding UV set " + layerName)
                mymesh.uv_layers.new(name=layerName)
                layer = mymesh.uv_layers[-1]
                index = 0
                for faceIdx in range(0,numFaces):
                    n = faceData[faceIdx][0]
                    for x in range(0,n):
                        u = readFloat(filePtr)
                        v = readFloat(filePtr)
                        layer.data[index].uv = [u,1 - v]
                        index += 1
            elif tagName == "#Mass#":
                weightArray = []
                weight = 0;
                for idx in range (0,numPoints):
                    f = readFloat(filePtr)
                    weightArray.append(f)
                    weight += f
            elif tagName[0] == '#':
                # System tag we don't read
                filePtr.seek(numBytes, 1)
            else:
                # Named Selection
                # Add a vertex group
                # First, check the tagName for a proxy
                newVGrp = True
                if len(tagName) > 5:
                    if tagName[:6] == "proxy:":
                        newVGrp = False
                        vgrp = obj.vertex_groups.new(name = "@@armaproxy")
                        prp = obj.armaObjProps.proxyArray
                        prx = tagName.split(":")[1]
                        if prx.find(".") != -1:
                            a = prx.split(".")
                            prx = a[0]
                            idx = a[-1]
                            if len(idx) == 0:
                                idx = "1"
                        else:
                            idx = "1"
                        n = prp.add()
                        n.name = vgrp.name
                        n.index = int(idx)
                        n.path = "P:" + prx
                        tagName = "@@armyproxy"
                
                if newVGrp == True:    
                    vgrp = obj.vertex_groups.new(name = tagName)
                for i in range(0, numPoints):
                    b = readByte(filePtr)
                    w = decodeWeight(b)
                    if (w>0):
                        vgrp.add([i],float(w),'REPLACE')
                    #print("b = ",b,"w = ", w)
                for i in range(0, numFaces):
                    b = readByte(filePtr)
                    w = decodeWeight(b)
                #    print("b = ",b,"w = ", w)
                #    if w== 1.0:
                #        pPoly = obj.data.polygons[i]
                #        for n in range(0,len(pPoly.vertices)):
                #            idx = pPoly.vertices[n]
                #            vgrp.add([idx], w, 'REPLACE')
                #filePtr.seek(numFaces, 1)
    
    # Done with the taggs, only the resolution is left to read
    resolution = readFloat(filePtr)  
    #meshName = meshName + "." + resolutionName(resolution)      
    meshName = resolutionName(resolution)
    mymesh.name = meshName
    obj.name = meshName
    coll.name = meshName

    print("materials...")
    indexData = {}
    # Set up materials
    for faceIdx in range(0,numFaces):
        fd = faceData[faceIdx] 

        textureName = fd[4]
        materialName = fd[5]

        try:
            mat = materialData[(textureName, materialName)]
            # Add the material if it isn't in
            if mat.name not in mymesh.materials:
                mymesh.materials.append(mat)
                thisMatIndex = len(mymesh.materials)-1
                indexData[mat] = thisMatIndex
                #print("added new material at " + str(thisMatIndex))
            else:
                thisMatIndex = indexData [mat]
                #print("old material " + str(thisMatIndex))
                
            mymesh.polygons[faceIdx].material_index = thisMatIndex
        except:
            pass
        
        
    print("sharp edges")
    # Set sharp edges
    if sharpEdges is not None:
        for edge in mymesh.edges:
            v1 = edge.vertices[0]
            v2 = edge.vertices[1]
            if [v1,v2] in sharpEdges:
                mymesh.edges[edge.index].use_edge_sharp = True
            elif [v2,v1] in sharpEdges:
                mymesh.edges[edge.index].use_edge_sharp = True
    #for pair in sharpEdges:
    #    p1 = pair[0]
    #    p2 = pair[1]
    #    edge = mymesh.edges.get([mymesh.vertices[p1], mymesh.vertices[p2]])
    #    print("edge = ", edge)
    #    #if edge != None:
    #    #    edge.use_edge_sharp = True

    # TODO: This causes faces with the same vertices but different normals to
    # be discarded. Don't want that
    #mymesh.validate()
    print("Normal calculation")
    mymesh.calc_normals()
    for poly in mymesh.polygons:
        poly.use_smooth = True

    print("Add edge split")
    maybeAddEdgeSplit(obj)
    scn.update()
    obj.select_set(True)
    
    #if layerFlag == True:
    #    # Move to layer
    #    objectLayers = getLayerMask(lodnr)
    #    bpy.ops.object.move_to_layer(layers=objectLayers)

    hasSet = False
    oldres = resolution
    resolution = correctedResolution(resolution)
    offset = oldres - resolution
    obj.armaObjProps.isArmaObject = True
    if resolution <= 1000:
        obj.armaObjProps.lodDistance = resolution
        hasSet = True
    else:
        obj.armaObjProps.lodDistance = offset #0.0

    print("set LOD type")    
    # Set the right LOD type
    lodPresets = ArmaToolbox.lodPresets
    
    for n in lodPresets:
        if float(n[0]) == resolution:
            obj.armaObjProps.lod = n[0]
            hasSet = True
             
    if hasSet == False:
        print("Error: unknown lod %f" % (resolution))
        print("resolution %d" % (correctedResolution(resolution)))

    print("weight")
    if weight is not None:
        obj.armaObjProps.mass = weight
    
    if len(weightArray) > 0:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        
        weight_layer = bm.verts.layers.float.new('FHQWeights')
        weight_layer = bm.verts.layers.float['FHQWeights']
        print(weight_layer)
        for i in range(0,len(weightArray)):    
            bm.verts[i][weight_layer] = weightArray[i]
        
        bm.to_mesh(obj.data)
    
    obj.select_set(False)
    
    if obj.armaObjProps.lod == '1.000e+13' or obj.armaObjProps.lod == '4.000e+13':
        ArmaTools.attemptFixMassLod (obj)

    print("done reading lod")
    return 0

# Main Import Routine
def importMDL(context, fileName, layerFlag):
    global objectLayers
    objectLayers = [True, False, False, False, False,
               False, False, False, False, False,
               False, False, False, False, False,
               False, False, False, False, False]
    currentLayer = 0
    
    filePtr = open(fileName, "rb")
    
    objName = path.basename(fileName).split(".")[0]

    # This is used to collect combinations of texture and rvmat
    # in order to generate Materials
    materialData = {}

    # Read the header
    sig = readSignature(filePtr)
    version = readULong(filePtr)
    numLods = readULong(filePtr)
    
    print ("Signature = {0}, version={1}, numLods = {2}".format(sig, version, numLods))
    
    if version != 257 or sig != b'MLOD':
        return -1
    
    # Start loading lods
    for i in range(0,numLods):
        if loadLOD(context, filePtr, objName, materialData, layerFlag, i) != 0:
            return -2

    filePtr.close()

    return 0
