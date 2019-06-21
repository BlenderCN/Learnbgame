'''
Created on 09.03.2013

@author: hfrieden
'''

'''
Write the current object(s) into a BITxt file
'''

import bpy
import os
import math

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

def exportBITxt(file, ctrlFile, uvsetFile, selectedOnly = False, mergeLods = True):
    '''
    Export to file. 
    If selectedOnly is True, only selected objects will be exported. The default is 
    to export all ARMA flagged objects
    if mergeLods is true, then all lods of the same kind (for example, all
    geometry lods of 1.0) will be merged into a single lod in the output. The default is
    to merge lods. If set to False, then there might be duplciate LODs in the output file.
    '''
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

    # Objects now contains candidates. If we want to merge lods, sort them by LOD.
    if mergeLods:
        objects = sorted(objects, key=lodKey)
        
    # Debug
    #for obj in objects:
    #    print ("object " + obj.name + " has key " + str(lodKey(obj)))
    
    # Make sure the object is in OBJECT mode, otherwise some of the functions might fail
    bpy.ops.object.mode_set(mode='OBJECT');
    
    # Write the file. Starting with the header
    file.write(":header\nversion 1.0\nsharp edges\n\n")
    
    # Collect the object. When we want separated lods, flush the list after each iteration
    work_list = []
    lodIdx = 0
    previous_lod = -1000000000
    hasUVSets = 0
    for obj in objects:
        if previous_lod != lodKey(obj) or mergeLods == False:
            export_lod_list(file, work_list)
            if export_lod_uvsets(uvsetFile, work_list, lodIdx) == True:
                hasUVSets = hasUVSets + 1
            lodIdx = export_ctrl(ctrlFile, work_list, lodIdx)
            work_list = []
            previous_lod = lodKey(obj)
        work_list.append(obj)
        
    # need to flush whatever is left
    if len(work_list) != 0:
        export_lod_list(file, work_list)
        if export_lod_uvsets(uvsetFile, work_list, lodIdx) == True:
                hasUVSets = hasUVSets + 1
        lodIdx = export_ctrl(ctrlFile, work_list, lodIdx)
        
    file.write("\n:end")
    if hasUVSets > 0:
        uvsetFile.write("0")
        return True
    else:
        return False

def export_lod_uvsets(uvsetFile, list, lodIdx):
    flag = False
    if len(list) == 0:
        return flag
    
    uvsetFile.write(str(lodIdx) + "\n")

    for obj in list:
        mesh = obj.data      
        # Write the UVSets
        uvt = mesh.uv_layers
        if len(uvt)>1:
            flag = True
        uvsetFile.write(str(len(uvt)) + "\n")
        for uvset in range(0, len(uvt)):
            layer = uvt[uvset]
            uvsetFile.write(str(len(mesh.tessfaces)) + "\n")
            for i, face in enumerate(mesh.tessfaces):
                codeSnip = "faceIndex = %d;" % (i)
                uvArray = []
                for vertIdx in range(0,len(face.vertices)):
                    uvPair = [0,0]
                    try: 
                        uvPair = [uvPair for uvPair in mesh.tessface_uv_textures[uvset].data[face.index].uv[vertIdx]]
                    except:
                        pass
                    ##uvsetFile.write(str(uvPair[0]) + "\n" + str(uvPair[1]) + "\n")
                    uvArray = uvArray + [uvPair[0], 1-uvPair[1]]
                codeSnip = codeSnip + "faceArray = " + str(uvArray) + ";\n" 
                uvsetFile.write(codeSnip)
                    
    
    return flag

def export_ctrl(file, list, index):
    if len(list) == 0:
        return index
    
    #file.write(str(index) + "\n")
    #file.write("autocenter\n")
    #file.write("0\n")
    
    for obj in list:
        for prop in obj.armaObjProps.namedProps:
            file.write(str(index) + "\n")
            file.write(prop.name + "\n")
            file.write(prop.value + "\n")
    
    return index+1               
            
def export_lod_list(file, list):
    ''' export a list of objects with a common lod into the output file'''
    if len(list) == 0:
        return
    #print("debug: export_lod_list, list has " + str(len(list)) + " elements\n")
    #for obj in list:
    #    print ("debug: object " + obj.name)
        
    #print("debug: lod_list done\n")  
    
    # Write the lod header
    lod = lodKey(list[0])
    if lod < 0:
        lod = -lod
        
    file.write(":lod " + str(lod) + "\n")
    file.write(":object\n")
    # Since we merge these objects, we need to record an offset for each of them
    # so we can reference the right point in the vertex array
    base_index = 0
    bases = {}
    
    # :points
    file.write(":points\n")
    for obj in list:
        bases[obj] = base_index
        mesh = obj.data
        for vert in mesh.vertices:
            file.write("{0:.4f} {1:.4f} {2:.4f}\n".format(
                 vert.co.x * 1000.0, vert.co.y * 1000.0, vert.co.z * 1000.0))
            base_index = base_index + 1
            
    # :face's
    for obj in list:
        base = bases[obj]
        mesh = obj.data
        mesh.calc_tessface() # In case there's n-gons left
        #print("outputting faces, " + str(len(mesh.tessfaces)) + " to go")
        for face in mesh.tessfaces:
            file.write(":face\n")
            materialName, textureName = getMaterialInfo(face, obj)
            file.write("index ")
            verts = (face.vertices)
            for vertIdx in verts:
                file.write(str(1 + vertIdx + base)) # Indices in the text format are 1-based
                file.write(" ")
            
            file.write("\nuv ")
            for vertIdx in (range(len(face.vertices))):
                uvPair = [0,0]
                try: 
                    uvPair = [uvPair for uvPair in mesh.tessface_uv_textures.active.data[face.index].uv[vertIdx]]
                except:
                    pass
                
                if math.isnan(uvPair[0]) or math.isnan(uvPair[1]):
                    print("*** WARNING ***\nNaN uv coordinates for face in lod %d" % (lod))
                    uvPair[0] = 0.0;
                    uvPair[1] = 0.0;
                
                file.write ("{0:.4f} {1:.4f} ".format(uvPair[0], uvPair[1]))
            file.write("\n")
            
            if len(textureName) > 0:
                file.write("texture \"" + textureName + "\"\n")
            if len(materialName) > 0:
                file.write("material \"" + materialName + "\"\n")

                
        
    file.write("\n:edges\n")
    # Indices of the edge-list are zero-based... well doh
    for obj in list:
        base = bases[obj]
        mesh = obj.data
        mesh.calc_tessface() # Dunno if that is actually needed at all
        
        mesh = obj.data

        # Unfortunately, there does't seem to be a better way to do this.
        # First, gather the edges of the flat shaded faces.
        edges = [edge for face in mesh.tessfaces if not face.use_smooth for edge in face.edge_keys]
        edges = sorted(set(edges))
        
        # Gather the edges with the "sharp" flag set
        edges2 = [edge for edge in mesh.edges if edge.use_edge_sharp]
        
        # We need to go through the edges to find the doubles.
        for edge in edges2:
            v1 = edge.vertices[0]
            v2 = edge.vertices[1]
            if not (v1, v2) in edges and not (v2, v1) in edges:
                edges = edges + [(v1, v2)]
        
        # write them out, on a single line
        for edge in edges:
            file.write("{0} {1} ".format(edge[0]+base, edge[1]+base))
            
    file.write("\n");
    
    # :selection's
    # Selections are again one-based
    for obj in list:
        mesh = obj.data
        grpIndex = 0
        base = bases[obj]
        for group in obj.vertex_groups:
            name = group.name
            
            file.write(":selection \"" + group.name + "\"\n")
            
            for vert in mesh.vertices:
                inGroups = [grp for grp in vert.groups if grp.group == grpIndex]
                if len(inGroups) != 0:
                    # Can only have at most one group here that matches the index
                    file.write("{0} {1:.3f}\n".format(vert.index + base + 1, inGroups[0].weight))
            grpIndex = grpIndex + 1        
    
    # Mass
    # If this is a geometry LOD, write a mass
    if lod == 1.000e+13:
        totalMass = 0
        totalVerts = 0
        for obj in list:
            totalMass = totalMass + obj.armaObjProps.mass          
            totalVerts = totalVerts + len(obj.data.vertices)  
        
        perVertMass = totalMass / totalVerts
        file.write(":mass\n")    
        
        for obj in list:
            mesh = obj.data
            base = bases[obj]
            for vert in mesh.vertices:
                weight = 1.0 #FIXME: This is probably wrong
                file.write("{0:.3f} ".format(weight * perVertMass))

                 
        file.write("\n")