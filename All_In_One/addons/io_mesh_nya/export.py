#	
#	Copyright (C) 2018 Team Motorway
#	
#	This file is part of Project Motorway source code.
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#	
# <pep8 compliant>
#
# 1.1
import os
import time
import struct
import math

import bpy
import bpy_extras.io_utils
import mathutils
import random

from array import *
from collections import namedtuple
from mathutils import Vector
from random import randint

mesh_vao_start = 0
mesh_vbo_start = 0

file_size_offset = 0

# DEBUG: dump a certain object to the console (useful for undocumented stuff)
def dump( obj ):
    for attr in dir( obj ):
        if hasattr( obj, attr ):
            print( "obj.%s = %s" % ( attr, getattr( obj, attr ) ) )

def mesh_triangulate( me ):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh( me )
    bmesh.ops.triangulate( bm, faces = bm.faces )
    bm.to_mesh( me )
    bm.free()

def write_bloc_size( file, offset, bloc_start ):
    current_position = file.tell()
    file.seek( offset, 0 )
    file.write( struct.pack( 'I', ( current_position - bloc_start ) ) )
    file.seek( current_position, 0 )
 
def write_bloc_offset( file, offset ):
    current_position = file.tell()
    file.seek( offset, 0 )
    file.write( struct.pack( 'I', current_position ) )
    file.seek( current_position, 0 )
 
#==========================================================
#   write_entity_count
#       Write an integer to a certain offset
#
#       Parameters:
#           file: current file stream
#           offset: offset to write to
#           count: stuff to write
#==========================================================
def write_entity_count( file, offset, count ):
    current_position = file.tell()
    file.seek( offset, 0 )
    file.write( struct.pack( 'I', count ) )
    file.seek( current_position, 0 )
 
#==========================================================
#   write_padding
#       Write padding to align file content (16 byte aligned)
#
#       Parameters:
#           file: current file stream
#==========================================================
def write_padding( file ):	
    while file.tell() % 16 != 0:
        file.write( struct.pack( 'B', 0xFF ) )

#==========================================================
#   write_header
#       Write file header
#
#       Parameters:
#           file: current file stream
#           version: current file version (set in the init script file)
#==========================================================
def write_header( file, version ):
    global file_size_offset 

    # File Version
    file.write( bytes( version ) )

    # File Size
    file_size_offset = file.tell()
    file.write( struct.pack( 'I', 0 ) )
    
    # Buffer strides
    # 1100; has uvmap and normals
    file.write( struct.pack( 'I', 3 ) )
    write_padding( file )

def write_bounding_sphere( file, object ):
    file.write( struct.pack( 'f', object.location.x ) )
    file.write( struct.pack( 'f', object.location.y ) )
    file.write( struct.pack( 'f', object.location.z ) )  
 
    sphereRadius = object.dimensions.x
    sphereRadius = max( sphereRadius, object.dimensions.y )
    sphereRadius = max( sphereRadius, object.dimensions.z )
    
    file.write( struct.pack( 'f', sphereRadius ) )   

def write_bounding_box( file, object ):
    file.write( struct.pack( 'f', object.location.x ) )
    file.write( struct.pack( 'f', object.location.z ) )
    file.write( struct.pack( 'f', object.location.y ) )  
    file.write( struct.pack( 'f', object.dimensions.x ) )
    file.write( struct.pack( 'f', object.dimensions.z ) )
    file.write( struct.pack( 'f', object.dimensions.y ) )
    
def write_mesh( file, global_matrix, create_convex_collider, path ):
    global mesh_vao_start
    global mesh_vbo_start

    vbo = array( 'f' )
    ibo = array( 'I' )
    
    indice = 0
    indice_tracking = 0

    file.write( bytearray( 'GEOM', 'utf-8' ) )
    submesh_size_offset = file.tell()
    file.write( struct.pack( 'I', 0 ) )

    vbo_size_offset = file.tell()
    file.write( struct.pack( 'I', 0 ) )

    ibo_size_offset = file.tell()
    file.write( struct.pack( 'I', 0 ) )

    mesh_list = []
    submesh_start_offset = file.tell()
    for obj in bpy.context.scene.objects:
        meshHash = hash( obj.name ) % ( 10 ** 8 )

        if meshHash in mesh_list:
            continue

        mesh_list.append( meshHash )
        
        if obj.name == '__Collider__':
            # Ignore this mesh if the collider export is not required
            if not create_convex_collider:
                continue
            
            mesh = obj.to_mesh( bpy.context.scene, True, 'PREVIEW', calc_tessface=True )
            transform_matrix = global_matrix * obj.matrix_world
            mesh.transform( transform_matrix ) # pretransform the model since blender matrices are a total mess to deal with in the app

            mesh_triangulate( mesh )
            mesh.calc_tessface()
            
            hull_vertices = array( 'f' )
            
            for face in mesh.polygons:
                for loop_index in face.loop_indices:
                    vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]

                    hull_vertices.append( vertex.co.x )
                    hull_vertices.append( vertex.co.y )
                    hull_vertices.append( vertex.co.z )
                    
            convex_collider_stream = open( path + ".hull", 'w+b' )
            convex_collider_stream.write( struct.pack( 'I', len( hull_vertices ) ) )
            for scalar in hull_vertices:
                convex_collider_stream.write( struct.pack( 'f', scalar )  )
                    
            convex_collider_stream.close()
            
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        if obj.type == 'MESH':
            mesh = obj.to_mesh( bpy.context.scene, True, 'PREVIEW', calc_tessface=True )
            transform_matrix = global_matrix * obj.matrix_world
            mesh.transform( transform_matrix ) # pretransform the model since blender matrices are a total mess to deal with in the app

            mesh_triangulate( mesh )
            mesh.calc_tessface()
            # mesh.calc_tangents()
            # mesh.flip_normals()

            lod = 0
            
            if '__LOD1__' in obj.name:
                lod = 1
            elif '__LOD2__' in obj.name:
                lod = 2
            elif '__LOD3__' in obj.name:
                lod = 3
                
            print( "DEBUG > LOD = %i" % ( lod ) )
            
            file.write( struct.pack( 'I', meshHash ) )
            file.write( bytearray( obj.name, 'utf-8' ) )
            file.write( struct.pack( 'B', 0x0 ) )
            file.write( struct.pack( 'I', int( len( ibo ) ) ) )
            indiceOffset = file.tell()
            file.write( struct.pack( 'I', 0 ) )
            write_bounding_sphere( file, obj )
            write_bounding_box( file, obj )
            file.write( struct.pack( 'I', lod ) )
            write_padding( file )
            
            indice_tracking = 0
            for face in mesh.polygons:
                for loop_index in face.loop_indices:
                    ibo.append( indice )

                    vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]

                    vbo.append( vertex.co.x )
                    vbo.append( vertex.co.y )
                    vbo.append( vertex.co.z )

                    vbo.append( vertex.normal.x )
                    vbo.append( vertex.normal.y )
                    vbo.append( vertex.normal.z )

                    vbo.append( mesh.uv_layers.active.data[loop_index].uv[0] )
                    vbo.append( mesh.uv_layers.active.data[loop_index].uv[1] )

                    indice += 1
                    indice_tracking += 1
   
            write_entity_count( file, indiceOffset, indice_tracking )

    write_bloc_size( file, submesh_size_offset, submesh_start_offset )

    mesh_vbo_start = file.tell()
    for x in vbo:
        file.write( struct.pack( 'f', x ) )    
    write_bloc_size( file, vbo_size_offset, mesh_vbo_start )

    mesh_vao_start = file.tell()
    for x in ibo:
        file.write( struct.pack( 'I', x ) )    
    write_bloc_size( file, ibo_size_offset, mesh_vao_start )
 
#==========================================================
# Blender Save Function
#==========================================================
def save( filepath, create_convex_collider, global_matrix, version ):
    # Open file stream
    file = open( filepath, 'w+b' )
	
    write_header( file, version )
    
    bpy.ops.object.select_all( action = 'SELECT' )
    bpy.ops.object.origin_set( type = 'ORIGIN_GEOMETRY' )
    write_mesh( file, global_matrix, True, filepath )

    # Write file size (end offset - 0)
    global file_size_offset
    write_bloc_size( file, file_size_offset, 0 )

    # Close the file stream
    file.close()
    return {'FINISHED'}