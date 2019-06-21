'''
Created on May 28, 2017

@author: hfrieden

Import ASC DEM files

'''
import struct
import bpy
import bmesh
import os.path as path
import ArmaToolbox

def expectKeyword(line, word):
    pair = line.split()
    kw = pair[0].strip().decode("utf-8")
    val = pair[1].strip().decode("utf-8")
    
    #print ("kw = ", kw, "val = ", val)
    
    if kw == word:
        return float(val)
    else:
        return -1

def vertIdx(x,y,ncols, nrows):
    return y*ncols + x

def importASC(context, fileName):
    filePtr = open(fileName, "rb")
    objName = path.basename(fileName).split(".")[0]
    
    # This isn't very flexible (yet). No idea if there can be comments in ASC DEM files
    # expect the ncols/nrows etc at the beginning
    
    line = filePtr.readline()
    ncols = int(expectKeyword(line, "ncols"))
    if ncols == -1:
        return -1
    
    line = filePtr.readline()
    nrows = int(expectKeyword(line, "nrows"))
    if nrows == -1:
        return -1


    
    line = filePtr.readline()
    xllcorner = expectKeyword(line, "xllcorner")
    if xllcorner == -1:
        return -1


    line = filePtr.readline()
    yllcorner = expectKeyword(line, "yllcorner")
    if yllcorner == -1:
        return -1   
    
    line = filePtr.readline()
    cellsize = expectKeyword(line, "cellsize")
    if cellsize == -1:
        return -1
    
    line = filePtr.readline()
    nodata = expectKeyword(line, "NODATA_value")
    
    #print("debug: size = " , nrows, "x", ncols, " cellsize ", cellsize , "corner at ", xllcorner, ",", yllcorner)
    
    # read the height field data
    verts = []
    for y in range(0,nrows):
        line = filePtr.readline()
        line = line.decode("utf-8")
        vals = line.split(" ")
        for x in range(0,ncols):
            f = float(vals [x])
            point = [(x*cellsize)/100,((nrows-1-y)*cellsize/100), f/100]
            verts.append (point)
    
    filePtr.close()
    
    faces = []
    # Create the triangulation
    for y in range(0,nrows-1):
        for x in range(0,ncols-1):
            idx1 = vertIdx(x,y,ncols,nrows)
            idx2 = vertIdx(x+1,y,ncols,nrows)
            idx3 = vertIdx(x,y+1, ncols, nrows)
            idx4 = vertIdx(x+1,y+1, ncols, nrows)
            face1 = [idx3, idx2, idx1]
            face2 = [idx2, idx3, idx4]
            faces.append(face1)
            faces.append(face2)
      
    numFaces = len(faces)  
    # Create the mesh.
    mymesh = bpy.data.meshes.new(name="heightfield")
    mymesh.from_pydata(verts, [], faces) 

    mymesh.update(True)

    obj = bpy.data.objects.new(objName, mymesh)
    
    scn = bpy.context.scene
    scn.objects.link(obj)
    scn.objects.active = obj   
    
    xext = (ncols * cellsize)/100;
    yext = (nrows * cellsize)/100;
    
    # Unmap the polygon flat   
    mymesh.uv_textures.new(name="Terrain")
    layer = mymesh.uv_layers[-1]
    index = 0
    for f in mymesh.polygons:
        f.use_smooth = True
        for vIdx in f.vertices:
            v = mymesh.vertices[vIdx]
            x = v.co[0]
            y = v.co[1]
            
            layer.data[index].uv = [x/xext, y/yext] 
            index += 1

    
    obj.armaHFProps.isHeightfield = True
    obj.armaHFProps.cellSize = cellsize
    obj.armaHFProps.northing = xllcorner
    obj.armaHFProps.easting = yllcorner
    obj.armaHFProps.undefVal = nodata    
    
        
    return 0