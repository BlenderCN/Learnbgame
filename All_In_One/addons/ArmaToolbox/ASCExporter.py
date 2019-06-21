'''
Created on May 29, 2017

@author: hfrieden
Export ASC DEM files

'''

import struct
import bpy
import bmesh
import os.path as path
import ArmaToolbox
from math import sqrt

def vertIdx(x,y,ncols, nrows):
    return y*ncols + x

def exportASC(context, fileName):
    filePtr = open(fileName, "wt")
    obj = context.object
    props = obj.armaHFProps
    
    # dump Header
    verts = len(obj.data.vertices)
    rowcols = sqrt(verts)
    
    filePtr.write("ncols         " + str(rowcols) + "\n")
    filePtr.write("nrows         " + str(rowcols) + "\n")
    filePtr.write("xllcorner     " + str(props.northing) + "\n")
    filePtr.write("yllcorner     " + str(props.easting) + "\n")
    filePtr.write("cellsize      " + str(props.cellSize) + "\n")
    filePtr.write("NODATA_value  " + str(props.undefVal) + "\n")
    
    # dump the heightfield. One line contains one row of vertices
    row = rowcols
    for v in obj.data.vertices:
        filePtr.write("{:.4f}".format(v.co[2] * 100))
        row -= 1
        if row == 0:
            filePtr.write("\n")
            row = rowcols 
        else:
            filePtr.write(" ")
        
    
    filePtr.close()
    