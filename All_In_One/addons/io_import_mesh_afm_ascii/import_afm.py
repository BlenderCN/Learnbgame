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


import bpy

# Constants, for testing.
ZOOM_RES = 1e4
XY_SPREAD = 2e-3

# assumes a square matrix of Z values
def CreateMeshUsingMatrix(VertIndices, Verts):

    Faces = []
    dims = len(VertIndices)
    print(dims)

    # going to use current row and next row all the way down
    for row in range(dims-1):
        #now take row and row+1
        for col in range(dims-1):
            #we generate faces clockwise from 4 Verts
            val1 = VertIndices[row][col]
            val2 = VertIndices[row][col+1]
            val3 = VertIndices[row+1][col+1]
            val4 = VertIndices[row+1][col]
            face = [val1, val2, val3, val4]
            Faces.append(face)
        

    ## TAKEN FROM USER    ValterVB 
    # create new mesh structure
    mesh = bpy.data.meshes.new("Relief")
    mesh.from_pydata(Verts, [], Faces)
    mesh.update()
    new_object = bpy.data.objects.new("Ascii Data", mesh)
    new_object.data = mesh
    scene = bpy.context.scene
    scene.objects.link(new_object)
    scene.objects.active = new_object
    new_object.select = True
    ## / TAKEN FROM USER


# i am assuming the input data is 256*256
def startASCIIimport(filename):
    
    VertIndices = []
    heightMatrix = []

    # Deals with opening the file and taking data line by line.
    f = open(filename, 'rU')
    for m in f:
        if m[0] != "#":
            xCol = m.split()
            floatVals = []
            for val in xCol:
                floatVals.append(float(val)*ZOOM_RES)
            heightMatrix.append(floatVals)
    # We have all important data in a usable structure now, close the file
    f.close()

    # this supposes that X, Y separation are going to be the same.
    xy_val = []
    for i in range(256): xy_val.append(i*XY_SPREAD)

    # Generates the (x,y,height) matrix, no need for Vector(...) 
    yVal = 0
    vertNum = 0
    rawVertCollection = []
    for height_x in heightMatrix:
        xVal = 0
        vertRow = []
        for item in height_x:
            t_vertice = (xy_val[xVal], -xy_val[yVal], heightMatrix[yVal][xVal])
            rawVertCollection.append(t_vertice)
            vertRow.append(vertNum)
            xVal+=1
            vertNum+=1
        yVal+=1
        VertIndices.append(vertRow)

    # done here, lets make a mesh! 
    CreateMeshUsingMatrix(VertIndices, rawVertCollection)



# package manages registering




