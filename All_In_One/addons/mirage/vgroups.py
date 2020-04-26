'''
Copyright (C) 2015 Diego Gangl
diego@sinestesia.co

Created by Diego Gangl. This file is part of Mirage.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import random
import math

import bpy
import bmesh
from mathutils import Vector
from mathutils import Color

import numpy

from . import data
from . import utils

# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------


def get_bmesh_from_heightmap(obj, context):
    """ Duplicate heightmap terrain to get a bmesh, don't forget to delete """
    
    bpy.ops.object.duplicate()
    bpy.ops.object.modifier_apply(modifier='Heightmap')    
    
    bm = bmesh.new()
    bm.from_object(context.object, context.scene)    
    bm.verts.ensure_lookup_table()

    return bm


def get_vgroup(group_name, obj):
    """ Get vertex group or make it if it doesn't exist """

    if group_name in obj.vertex_groups:
        vgroup = obj.vertex_groups[group_name]
    else:
        vgroup = obj.vertex_groups.new(name=group_name)

    return vgroup


# --------------------------------------------------------------------------
# MAIN FUNCTIONS
# --------------------------------------------------------------------------

def generate_height(obj, bm, edge = None):
    """ Generate vertex group based on height for obj """
    
    height_group = get_vgroup('Height', obj)
        
    vertex_count = len(bm.verts)
    heights = numpy.zeros(vertex_count, dtype='float16')

    for v in bm.verts:
        heights[v.index] = v.co[2]
            
    normalized = heights / heights.max()

    for v in bm.verts:
        height_group.add( index = [v.index], 
                          weight = normalized[v.index],
                          type = 'REPLACE')            



def generate_slope(obj, bm):    
    """ Generate vertex group based on slope for obj """

    slope_group = get_vgroup('Slope', obj)

    straight = Vector((0,0,1))
    
    weights = numpy.zeros(len(bm.verts), dtype='float16')
    
    for vert in bm.verts:
        normal = vert.normal.normalized()        
        weights[vert.index] = 1 - straight.dot(normal)
            
    weights_avg = weights / weights.max()

    for index, weight in numpy.ndenumerate(weights_avg):
        slope_group.add( index = [index[0]],
                         weight = weight,
                         type = 'REPLACE' )



def generate_tree_density(obj, max_slope, max_height):
    """ Generate a tree density vgroup in the terrain object """
    
    terrain_edge = data.settings('terrain').edges
        
    slope_group = obj.vertex_groups['Slope']
    height_group = obj.vertex_groups['Height']
    
    tree_group = get_vgroup('Tree Density', obj)
        
    verts = len(obj.data.vertices)
    max_slope = math.degrees(max_slope) / 90

    for i in range(0,verts):
        
        weight = slope_group.weight(i)
        
        # Slight noise variation
        weight -= random.gauss(0.0,0.1)

        # Cut off by max slope
        if slope_group.weight(i) > max_slope:
            weight = 1.0
        elif slope_group.weight(i) > (max_slope - 0.2):
            weight = weight / max_slope
        
        
        # Cut off by max height
        if height_group.weight(i) > max_height:
            weight = 1.0
        elif height_group.weight(i) > (max_height - 0.2):
            weight = weight / max_height
            
        
        # Remove at sea level 
        if terrain_edge == 'ISLAND' and height_group.weight(i) < 0.25:
            weight = 1
        
                    
        # Invert
        weight = 1.0 - weight
        
        tree_group.add( index = [i], 
                        weight = weight,
                        type = 'REPLACE'
                      )


def generate_plateau(obj, bm, plateau):
    """ Mark vertex below on a plateau as 1 """

    plateau_group = get_vgroup('Plateau', obj)

    for v in bm.verts:
        if v.co[2] >= plateau:
            weight = 1
        else:
            weight = 0
            
        plateau_group.add( index = [v.index], 
                           weight = weight,
                           type = 'REPLACE')            


def generate_below_sea(obj, bm, sea_level):
    """ Mark vertex below sea level as 1 """
    
    below_group = get_vgroup('Below Sea', obj)
    
    for v in bm.verts:
        if v.co[2] > sea_level:
            weight = 0
        else:
            weight = 1
            
        below_group.add( index = [v.index], 
                         weight = weight,
                         type = 'REPLACE')            
    
    
    
    
    
def convert_to_color_group(obj, name):
    """ Convert a Weight vertex group to color """
    
    if name in obj.data.vertex_colors:
        group = obj.data.vertex_colors[name]
    else:
        group = obj.data.vertex_colors.new(name = name)
    
    source = obj.vertex_groups[name]
    polygons = obj.data.polygons

    inner_loop_index = 0
    
    for face in polygons:

        vertex_index = 0

        for index in face.loop_indices:
            
            weight = source.weight(face.vertices[vertex_index])
            vcolor = Color((weight, weight, weight))
            
            group.data[inner_loop_index].color = vcolor
            inner_loop_index += 1
            vertex_index += 1
            



                      
# --------------------------------------------------------------------------
# OPERATORS
# --------------------------------------------------------------------------


class MG_OT_MakeHeightVGroup(bpy.types.Operator):
    bl_idname = "mirage.make_vgroup_height"
    bl_label = "Vertex group by Height"
    bl_description = "Generate Vertex group by Height"
    bl_options = {"REGISTER", "UNDO"}
    
    
    @classmethod
    def poll(cls, context):
        return utils.is_selected_and_mesh(context)
    
    
    def execute(self, context):
        obj = context.object
        
        if 'Heightmap' in obj.modifiers:
            name = obj.name
            bm = get_bmesh_from_heightmap(obj, context)
        else:        
            bm = bmesh.new()
            bm.from_object(obj, context.scene)
            
        generate_height(obj, bm)
        convert_to_color_group(obj, 'Height')
        
        if 'Heightmap' in obj.modifiers:
            bpy.ops.object.delete()
            obj.select = False
            bpy.data.objects[name].select = True
        
        return {"FINISHED"}
        



class MG_OT_MakeSlopeVGroup(bpy.types.Operator):
    bl_idname = "mirage.make_vgroup_slope"
    bl_label = "Vertex group by Slope"
    bl_description = "Generate Vertex group by Slope"
    bl_options = {"REGISTER", "UNDO"}
    
    
    @classmethod
    def poll(cls, context):
        return utils.is_selected_and_mesh(context)
    
    
    def execute(self, context):
        obj = context.object
        
        if 'Heightmap' in obj.modifiers:
            name = obj.name
            bm = get_bmesh_from_heightmap(obj, context)
        else:        
            bm = bmesh.new()
            bm.from_object(obj, context.scene)
        
        generate_slope(obj, bm)
        convert_to_color_group(obj, 'Slope')

        if 'Heightmap' in obj.modifiers:
            bpy.ops.object.delete()
            obj.select = False
            bpy.data.objects[name].select = True
        
        return {"FINISHED"}




class MG_OT_MakeBelowSeaGroup(bpy.types.Operator):
    bl_idname = "mirage.make_vgroup_belowsea"
    bl_label = "Vertex group below the sea"
    bl_description = "Generate Vertex Group for vertices below sea level"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return utils.is_selected_and_mesh(context)
    
    def execute(self, context):
        obj = context.object
        sea_level = data.settings('terrain').sea_level

        if 'Heightmap' in obj.modifiers:
            name = obj.name
            bm = get_bmesh_from_heightmap(obj, context)
        else:        
            bm = bmesh.new()
            bm.from_object(obj, context.scene)

        generate_below_sea(obj, bm, sea_level)
        convert_to_color_group(obj, 'Below Sea')

        if 'Heightmap' in obj.modifiers:
            bpy.ops.object.delete()
            obj.select = False
            bpy.data.objects[name].select = True
    
        return {"FINISHED"}
        

class MG_OT_MakePlateauVGroup(bpy.types.Operator):
    bl_idname = "mirage.make_vgroup_plateau"
    bl_label = "Vertex group Plateau"
    bl_description = "Generate Vertex Group for vertices on a plateau"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return utils.is_selected_and_mesh(context)
    
    def execute(self, context):
        obj = context.object
        plateau_level = data.settings('terrain').plateau_level

        if 'Heightmap' in obj.modifiers:
            name = obj.name
            bm = get_bmesh_from_heightmap(obj, context)
        else:        
            bm = bmesh.new()
            bm.from_object(obj, context.scene)

        generate_plateau(obj, bm, plateau_level)
        convert_to_color_group(obj, 'Plateau')

        if 'Heightmap' in obj.modifiers:
            bpy.ops.object.delete()
            obj.select = False
            bpy.data.objects[name].select = True
    
        return {"FINISHED"}
        
