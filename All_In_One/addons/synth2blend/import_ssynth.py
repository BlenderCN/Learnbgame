'''
Created on Jun 19, 2013

@author: imac
'''
# ***** BEGIN GPL LICENSE BLOCK *****
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

import os
import time
import struct
import bpy
import bmesh
import mathutils
from bpy_extras.io_utils import (ImportHelper, 
                                 axis_conversion,)

materialList = []
#===============================================================================
# create_CubeMesh
#===============================================================================
def create_CubeMesh(name, objColor, loc, rot, sca):
    #Define vertices, faces, edges
#     vertsC = [ [1, 1, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [1, 1, 1], [0, 1, 1], [0, 0, 1], [1, 0, 1] ]
#     facesC = [ [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7], [0, 4, 7], [0, 7, 1], [1, 7, 6], [1, 6, 2], [2, 6, 5], [2, 5, 3], [4, 0, 3], [4, 3, 5] ]
     
    #Define mesh and object
    mesh = bpy.data.meshes['cubePrimary']
    obj = bpy.data.objects.new(name, mesh)
        
    obj.color = objColor
    
    #Set location and scene of object
    obj.location = loc
    obj.dimensions = sca
    obj.rotation_euler = rot
    print(obj)
        
    #Create mesh
#     mesh.from_pydata(vertsC,[],facesC)
#     mesh.update(calc_edges=True)
    
    # Link object to scene and make active
    #bpy.context.scene.objects.link(obj)
    scn = bpy.context.scene
    scn.objects.link(obj)
    return obj


#===============================================================================
# create_sphere_mesh
#===============================================================================
def create_SphereMesh(name, radius, locat, objColor):

    # Create mesh and object
    mesh = bpy.data.curves['Primary']
    obj = bpy.data.objects.new(name, mesh)
    #obj.show_name = True
    obj.scale = (radius, radius, radius)
    obj.location = locat
    obj.color = objColor
         
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(obj)

    
    return obj
#===============================================================================
# createCubePrimitive
#===============================================================================

def createCubePrimitive(name):
    bpy.ops.mesh.primitive_cube_add()
    # Add a material slot to each object
    bpy.ops.object.material_slot_add() 
    ob = bpy.context.object
    ob.name = name
    #ob.show_name = True
    me = ob.data
    me.name = name
    return ob

#===============================================================================
# createSpherePrimitive
#===============================================================================
def createSpherePrimitive(name):
    bpy.ops.surface.primitive_nurbs_surface_sphere_add()
    # Add a material slot to each object
    bpy.ops.object.material_slot_add()
    ob = bpy.context.object
    ob.name = name
    #ob.show_name = True
    me = ob.data
    me.name = name
    return ob

#===============================================================================
# makeMatte
#===============================================================================
def makeMatte(name ):
    mat = bpy.data.materials.new(name)
    #mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 0.8
    #mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    #mat.alpha = alpha
    mat.ambient = 1
    mat.use_object_color = True
    return mat
 
def setMatte(ob, mat):
    me = ob.data
    me.materials.append(mat)
    
# Function to convert RGB to hex for groupong

#===============================================================================
# rgb_to_hex
#===============================================================================
def rgb_to_hex(r,g,b):
     
    flo = [ x * 255 for x in (r,g,b)]
         
    R,G,B = flo[0], flo[1], flo[2]
    hex = '#%02X%02X%02X' % (R,G,B)
    print(hex)

#===============================================================================
# load_ssynth_mesh
#===============================================================================
def load_ssynth_mesh(file, self):

# Load the .ssynth file
    objCount = 0
    
    createSpherePrimitive('Primary')
    createCubePrimitive('cubePrimary')
    
    makeMatte('SSmat')
    #read each line of the .ssynth file
    for line in file:
        if  objCount % 2500 == 0:
            print ("Import progress report: " + str(objCount) + " objects")
            args = line.split()
            argsIndex = 0
            colR = 1
            colB = 1
            colG = 1
        
        #begin sphere shape. here we import any spheres
        if args[argsIndex] == "s":
            argsIndex += 1
            cx = float(args[argsIndex])
            argsIndex += 1
            cy = float(args[argsIndex])
            argsIndex += 1
            cz = float(args[argsIndex])
            argsIndex += 1
            radius = float(args[argsIndex])
            argsIndex += 1
            
            colR = float(args[argsIndex])
            argsIndex += 1
            colG = float(args[argsIndex])
            argsIndex += 1
            colB = float(args[argsIndex])
            argsIndex += 1
            
            
            locat = (cx, cy, cz,)
            # Set the Alpha - maybe we can use this later
            alpha = 1.0
            bpy.context.object.color = (colR, colG, colB, alpha)
            objColor = bpy.context.object.color
            create_SphereMesh("Sphere", radius, locat, objColor)            
            # Find the active material
            bpy.context.object.active_material_index = 0
            # Add that material to the slot of each object
            bpy.context.object.active_material = bpy.data.materials["SSmat"]
        
        #begin box shape. here we import any boxes
        elif args[argsIndex] == "b":
            argsIndex += 1
            transMatrix = ((float(args[argsIndex + 0]),  float(args[argsIndex + 1]),  float(args[argsIndex + 2]),  float(args[argsIndex + 12])), 
                           (float(args[argsIndex + 4]),  float(args[argsIndex + 5]),  float(args[argsIndex + 6]),  float(args[argsIndex + 13])), 
                           (float(args[argsIndex + 8]),  float(args[argsIndex + 9]),  float(args[argsIndex + 10]), float(args[argsIndex + 14])), 
                           (float(args[argsIndex + 3]),  float(args[argsIndex + 7]),  float(args[argsIndex + 11]), float(args[argsIndex + 15])))
            
            #print (transMatrix)
            
            mat = mathutils.Matrix(transMatrix)
            #print(mat)
            
            loc, rot, sca = mat.decompose()
             
            #print(loc, rot, sca)
            loc = tuple(loc)
            sca = tuple(sca)
            rot = tuple(mat.to_euler())
            #print (loc, sca, rot)
                       
            argsIndex += 16

            colR = eval(args[argsIndex])
            argsIndex += 1
            colG = eval(args[argsIndex])
            argsIndex += 1
            colB = eval(args[argsIndex])
            argsIndex += 1
            alpha = 1.0
            
            
            bpy.context.object.color = (colR, colG, colB, alpha)
            objColor = bpy.context.object.color
            create_CubeMesh('cubePrimary', objColor, loc, rot, sca)
            objColor_group = (colR, colG, colB)
            print(objColor_group)
            color_Hex = rgb_to_hex(colR, colG, colB) 
            print(color_Hex)
            # Find the active material
            bpy.context.object.active_material_index = 0
            # Add that material to the slot of each object
            bpy.context.object.active_material = bpy.data.materials["SSmat"]
            materialList.append(color_Hex)
    
#     color_group = list(set(materialList))
    #print(materialList)   
            
    return {'FINISHED'}         
            
    file.close()        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
