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

def readMesh(filename, objName):
    def line_to_triplet(line):
        #convert a line of text in to an xyz float
        line_split = line.split(',')
        return float(line_split[0]), float(line_split[1]), float(line_split[2])

    vertices = []
    coords = {}
    index_tot = 0
    ifaces = []

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

    #find the : and remove up to and including it
    data = data[data.index(':') + 1:data.index('}')]
    
    #split up at ']],[[' and itterate
    for face in data.split(']],[['):
        #strip '[[[' or ']]]' if present
        ta = face.find('[[[')
        tb = face.find(']]]')
        if ta > -1:
            ta = 3
        else:
            ta = 0
            
        if tb == -1:
            tb = len(face)
            
        face = face[ta:tb]
        
        #create a temporary list to store this particular face's indices
        fi = []
        
        # split the face string by '],[' to get an array of vertices for this face, and itterate
        for vert in face.split('],['):
            # get the index for this vertex (in the unique list)
            index = coords.get(vert)
            
            # if the vertex wasn't in the vertex list, add it and get it's index
            if index is None:
                index = coords[vert] = index_tot
                index_tot += 1
                split_vert = vert.split(',')
                vertices.append(line_to_triplet(vert))

            # add the index to the face
            fi.append(index)
            
        #add the face to the list of faces
        ifaces.append(fi)
        
    mesh = bpy.data.meshes.new(objName)
    mesh.from_pydata(vertices, [], ifaces)

    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False

    mesh.update()
    mesh.validate()

    nobj = bpy.data.objects.new(objName, mesh)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj


def read(filepath):
    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    mesh = readMesh(filepath, objName)
