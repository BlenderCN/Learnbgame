'''
Copyright (C) 2015 Diego Gangl
<diego@sinestesia.co>

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
import os

import bpy
from mathutils import Vector

from . import data
from . import vgroups


class OT_GenerateTrees(bpy.types.Operator):
    bl_idname = "mirage.generate_tree"
    bl_label = "Add Trees"
    bl_description = "Add trees to selected object"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1

    
    def execute(self, context):
        """ Add tree particle system to terrain mesh """
        
        settings = data.settings('tree')
        terrain = context.object

        if 'Slope' not in terrain.vertex_groups:
            self.report({'ERROR'}, 'Terrain has no Slope Vertex Group')
            return {'CANCELLED'}


        tree_group = bpy.data.groups[settings.src_mesh]

        if len(tree_group.objects) == 0:
            self.report({'ERROR'}, 'Tree group is empty')
            return {'CANCELLED'}

        tree_mesh = tree_group.objects[0]
        terrain_area = terrain.dimensions[0]**2
        tree_area = max(tree_mesh.dimensions[0] * tree_mesh.dimensions[1], 0.01)
        
        
        vgroups.generate_tree_density( terrain, 
                                       settings.max_slope, 
                                       settings.max_height / 100 )
        
        
        if 'Trees' in terrain.modifiers:
            modifier = terrain.modifiers['Trees']
        else:
            modifier = terrain.modifiers.new("Trees", 'PARTICLE_SYSTEM')
            
        system = modifier.particle_system
        particles = modifier.particle_system.settings
        
        system.name = 'Tree Distribution'
        particles.name = 'Tree Settings'
        
        if settings.lock_scale_to_terrain:
            if tree_area > terrain_area:
                settings.scale = terrain_area / (tree_area**2)
            else:
                settings.scale = 0.5 / (terrain_area / tree_area)

        particles.particle_size = settings.scale

    
        # Trees can live for many year---frames
        particles.lifetime = 9999.99
        particles.frame_start = 0
        particles.frame_end = 0


        # Distribution and density    
        particles.count = settings.density
        particles.render_type = 'GROUP'
        particles.dupli_group = tree_group
        particles.size_random = 0.25
        particles.use_group_pick_random = True
        particles.use_rotation_dupli = True
        particles.distribution = 'JIT'
        system.vertex_group_density = 'Tree Density'

        
        # Make them stand upright with a little variation
        particles.normal_factor = 0
        particles.tangent_factor = 0.1
        particles.physics_type = 'NO'
        particles.use_rotations = True
        particles.rotation_mode = 'OB_Z'
        particles.rotation_factor_random = 0.005
        particles.phase_factor_random = 2
        
        
        
        # Set display to circles to help with performance
        count = 0
        
        for tree in tree_group.objects:
            if tree.type == 'MESH':
                count += len(tree.data.vertices)
        
        
        if count > 250000 and settings.density >= 1000: 

            if particles.draw_method == 'RENDER':
                particles.draw_method = 'CROSS'
                particles.draw_size = 5
                
            data.errors['tree_performance'] = True
        else:    
            particles.draw_method = 'RENDER'
            data.errors['tree_performance'] = False

        return {"FINISHED"}
