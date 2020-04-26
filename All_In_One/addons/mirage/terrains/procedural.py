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

import math
import time
import multiprocessing as mp
import queue
import platform

import numpy

import bpy
import bmesh

from mathutils import Vector

from . import generator
from . import benchmark
from .. import data
from .. import vgroups
from .. import utils


# ---------------------------------------------------------------------------
# INTERNAL FLAGS
# ---------------------------------------------------------------------------

flags = {
           'cancel'    : False,
           'complete'  : False,
           'error'     : False,
        }



# ---------------------------------------------------------------------------
# OPERATORS
# ---------------------------------------------------------------------------

class MG_OT_GenerationCancel(bpy.types.Operator):
    bl_idname = "mirage.cancel_terrain_generation"
    bl_label = "Cancel Terrain Generation"
    bl_description = "Cancel current procedural terrain generation"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        progress = data.settings('terrain').progress

        return (progress > 0)


    def execute(self, context):

        flags['cancel'] = True

        return {'FINISHED'}



class MG_OT_GenerateTerrain(bpy.types.Operator):
    bl_idname = "mirage.generate_terrain"
    bl_label = "Generate Terrain"
    bl_description = "Generate a terrain"
    bl_options = {'REGISTER'}

    points  = None
    pool    = None
    manager = None


    def make_ocean(self):
        """ Create the ocean mesh """
        
        settings = data.settings('terrain')
        size     = settings.size / 100
        offset   = size / 1.35 # Magic number

        bm = bmesh.new()
        bmesh.ops.create_grid(bm, 
                              x_segments    = 1, 
                              y_segments    = 1, 
                              size          = 1,
                             ) 


        mesh_data           = bpy.data.meshes.new('Ocean Mesh')
        obj                 = bpy.data.objects.new("Ocean", mesh_data)  

        bm.to_mesh(mesh_data)
        bm.normal_update()
        
        ocean               = obj.modifiers.new(name='Ocean Sim',type='OCEAN')
        obj.location        = Vector((-offset, offset, 0.15))
        obj.scale           = Vector((1.3,1.3,1.3))
        obj.name            = 'Ocean'
        ocean.spatial_size  = size
        
        ocean.repeat_x      = 1
        ocean.repeat_y      = 1
        ocean.resolution    = 12
        ocean.size          = 2
        ocean.spatial_size  = 20
        
        ocean.choppiness     = 2.0
        ocean.wave_scale     = 0.2
        ocean.wave_scale_min = 0.01

        bpy.context.scene.objects.link(obj)


    def make_object(self, points):
        """ Make the terrain object. Last step of generation """

        settings = data.settings('terrain')
        
        # Add Mesh
        if settings.detail_level == 'custom':
            detail = settings.detail_custom
        else:
            detail = 2**int(settings.detail_level)

        real_size = math.sqrt(settings.size) / 2
        bm = bmesh.new()
        

        # Generate Grid
        bmesh.ops.create_grid(bm, 
                              x_segments = detail, 
                              y_segments = detail, 
                              size = real_size,
                             ) 


        mesh_data = bpy.data.meshes.new('Terrain Mesh')

        # Create mesh and object
        utils.set_heights(bm, points, mesh_data)


        obj = bpy.data.objects.new("Terrain", mesh_data)  
           


        # Build vertex groups
        vgroups.generate_height(obj, bm, settings.edges)
        vgroups.generate_slope(obj, bm)
        vgroups.generate_below_sea(obj, bm, 0)
        vgroups.generate_plateau(obj, bm, settings.plateau_level)
        vgroups.convert_to_color_group(obj, 'Height')
        vgroups.convert_to_color_group(obj, 'Slope')
        vgroups.convert_to_color_group(obj, 'Below Sea')
        vgroups.convert_to_color_group(obj, 'Plateau')


        # Write some useful properties
        obj.mirage.generator = 'PROCEDURAL'
        obj.mirage.seed = settings.seed


        # Add to scene        
        bpy.context.scene.objects.link(obj)

        # Time it took to generate
        print('[MIRAGE] Terrain Linked in {0}'.format(benchmark.stop()))
        benchmark.reset()

        # Ocean
        if settings.edges == 'ISLAND' and 'Ocean' not in bpy.context.scene.objects:
            self.make_ocean()

        # Finish        
        bm.free()
        settings.progress = 0


    def on_complete(self, result):
        """ Completion callback for terrain generation process """

        settings            = data.settings('terrain')

        self.points         = result[1]
        settings.seed       = result[0]
        settings.progress   = 100

        # Tag for redraw and give it a sec to update
        utils.force_redraw()
        time.sleep(1)

        print('[MIRAGE] Terrain Generated in {0}'.format(benchmark.stop()))
        
        flags['complete'] = True
        self.make_object(self.points)
        

    def on_error(self, exception):
        """ Error callback for terrain generation process """
        
        print('[MIRAGE] There was an error: ', str(exception))

        flags['error'] = True



    def modal(self, context, event):
        """ Modal is used exclusively to poll progress """
        
        settings = data.settings('terrain')

        if flags['cancel'] or flags['error']:
            print('Stopping terrain generation')
            self.pool.terminate()
            self.manager.shutdown()            
            settings.progress = 0
            utils.force_redraw()

        if flags['cancel']:
            self.report({'WARNING'}, 'Terrain generation cancelled')
            flags['cancel'] = False
            return {"CANCELLED"}

        if flags['error']:
            self.report({'ERROR'}, 'Terrain generation Failed!')
            flags['error'] = False
            return {"CANCELLED"}


        if not flags['complete']:        
            return {'PASS_THROUGH'}
        else:
            self.manager.shutdown()            
            self.pool.join()

            flags['complete'] = False
            return {"FINISHED"}


    def invoke(self, context, event):
        """ Generate heightmap, terrain mesh and vertex groups """
        
        settings = data.settings('terrain')
        win = False

        benchmark.start()
        win = (platform.system() == 'Windows')

        # Multiprocessing & Blender don't work together on Windows
        if win:

            seed, points = generator.process_terrain()
            self.on_complete((seed, points))

            return {"FINISHED"}
            
       
        try:
            self.pool = mp.Pool(processes=1)
            self.manager = mp.Manager()

        except OSError:
            self.report({'WARNING'}, 'Not enough memory! Try restarting Blender.')
            return {'CANCELLED'}

        
        self.pool.apply_async( generator.process_terrain, 
                               args = (),
                               callback = self.on_complete,
                               error_callback = self.on_error)

        self.pool.close()
        settings.progress = 0.1
        
        context.window_manager.modal_handler_add(self)                
        return {"RUNNING_MODAL"}
