# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

"""
This script imports JSON format files to Blender.

The JSON Ngon format is very simple; 
Examine a basic file to make sense of it (create a cube in blender and use the JSON export function!

Usage:
Execute this script from the "File->Import" menu and choose a Raw file to
open.

Notes:
Generates the standard verts and faces lists, but without duplicate
verts. Only *exact* duplicates are removed, there is no way to specify a
tolerance.
"""

import bpy
import os
import json
from math import pi
from mathutils import Euler,Quaternion
from math import radians

def createEmpty(passedName):
    try:
        ob = bpy.data.objects.new(passedName, None)
        bpy.context.scene.objects.link(ob)
    except:
        ob = None
    return ob

def readJSON(filename, objName):
    # Open the input file
    filehandle = open(filename, "rb")

    # read in each line, convert from bytes to UTF-8, remove whitespace, \r and \n characters
    lines = []
    for line in filehandle.readlines():
        lines.append(line.decode("utf-8").replace(" ", "").replace("\r","").replace("\n",""))

    # close the file now we're done with it
    filehandle.close()

    # create a single string by joining with nothing
    data = "".join(lines);

    jsonObject = json.loads(data)

    parentObj = createEmpty("Anyland Thing")
    for item in jsonObject['p']:
        
        try:
            objNumber = item['b']
        except:
            objNumber = 1
        
        px = item['s'][0]['p'][0]
        py = item['s'][0]['p'][1]
        pz = item['s'][0]['p'][2]
        sx = item['s'][0]['s'][0]
        sy = item['s'][0]['s'][1]
        sz = item['s'][0]['s'][2]
        rx = item['s'][0]['r'][0]
        ry = item['s'][0]['r'][1]
        rz = item['s'][0]['r'][2]

        color1 = item['s'][0]['c'][0]
        color2 = item['s'][0]['c'][1]
        color3 = item['s'][0]['c'][2]

        loadObj(objNumber,sx,sy,sz,px,py,pz,rx,ry,rz,color1,color2,color3, parentObj)
    pass


def loadObj(objNumber,sx,sy,sz,px,py,pz,rx,ry,rz,r,g,b,parentObj):
    # load object
    file_loc = os.path.dirname(os.path.abspath(__file__)) + '\\baseShapes\\' + str(objNumber) + '.obj'

    imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
    obj = bpy.context.selected_objects[0] ####<--Fix
    obj.scale = (sx,sy,sz)
    obj.rotation_mode = 'ZXY'
    obj.rotation_euler = (radians(rx), radians(ry*-1), radians(rz*-1))
    obj.location = (px*-1, py, pz) # left hand co-ordinates to right hand co-ordinates
    obj.active_material.diffuse_color = (r,g,b)
    obj.parent = parentObj

def read(filepath):
    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    readJSON(filepath, objName)
