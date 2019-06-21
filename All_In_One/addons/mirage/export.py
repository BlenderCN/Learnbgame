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

import os
import math
import csv
import io

import numpy

import bpy
import bmesh

from bpy.props import StringProperty, EnumProperty


from . import utils


# ---------------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------------

def generate_image(data, img, size):
    """ Write height data to image """
    
    # Every pixel is stored as RGBA
    data = numpy.repeat(data, 4)

    # Set alpha to 1.0
    data[3::4] = 1.0 
            
    img.use_fake_user = True
    img.pixels[:] = data.tolist()
    img.update()
        




# ---------------------------------------------------------------------------
# OPERATORS
# ---------------------------------------------------------------------------

class MG_OT_ExportVgroup(bpy.types.Operator):
    bl_idname = "mirage.export_vgroups"
    bl_label = "Export Vertex Group to Image"
    bl_description = "Export a vertex group to an image"
    bl_options = {"REGISTER"}

    selected_group = StringProperty(
                        name = 'Vertex Group',
                        description = 'Vertex group to use',
                    )
    
    
    @classmethod
    def poll(cls, context):
        if utils.is_selected_and_mesh(context):
            return (len(context.object.vertex_groups) > 0)
        else:
            return False


    def invoke(self, context, event):
        """ Show settings dialog """
        
        # Set a good default
        if  (self.selected_group == '' and 
            'Height' in context.object.vertex_groups):
            
            self.selected_group = 'Height'
                
        
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        """ Draw settings dialog """

        obj = context.object

        row = self.layout.row()       
        row.prop_search(self, 'selected_group', 
                        obj, 'vertex_groups', icon='GROUP_VERTEX')
        


    def execute(self, context):
        
        obj = context.object
        verts = len(obj.data.vertices)    
                
        data = numpy.zeros(verts)
        size = math.sqrt(verts)        
        name = self.selected_group + ' - Vertex Group'

        vgroup = obj.vertex_groups[self.selected_group]

        # Put vgroup data in a numpy array
        for v in range(0, verts):
            data[v] = vgroup.weight(v)            


        # Make new image
        img = bpy.data.images.new( name = name,
                                   width = size,
                                   height = size,
                                   alpha = False )                                 

        # Send to function
        generate_image(data, img, size)

        message = 'Exported group "{0}" to image'.format(self.selected_group)
        self.report({'INFO'}, message)            
        
        return {"FINISHED"}
        
        



class MG_OT_ExportHeightmap(bpy.types.Operator):
    bl_idname = "mirage.export_heightmap"
    bl_label = "Export Heightmap"
    bl_description = "Genereate a Heightmap image from this mesh"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return utils.is_selected_and_mesh(context)
    
    def execute(self, context):
        
        # Get mesh data
        bm = bmesh.new()
        bm.from_object(context.object, context.scene)
        
        # Figure out size from verts
        size = math.sqrt(len(bm.verts))

        # Sort vertices for modified meshes 
        bm.verts.sort(key=lambda v: v.co.y*int(size) + v.co.x)
        bm.verts.ensure_lookup_table()
               
        # Put vert data into a numpy array
        data = numpy.zeros( len(bm.verts), dtype='float16' )

        for i, vert in enumerate(bm.verts):
            data[i] = vert.co.z

        
        # Remap values to         
        data_bounds = [data.min(), data.max()]
        pixel_bounds = [0,1]
        
        data = numpy.interp(data, data_bounds, pixel_bounds)

        
        # Make new image
        img = bpy.data.images.new( name   = 'Heightmap',
                                   width  = size,
                                   height = size,
                                   alpha  = False )                                          

        img.colorspace_settings.name = 'Linear'

        # Send to function
        try:
            generate_image(data, img, size)
        except TypeError:
            self.report({'ERROR'}, 'Can\'t export this mesh as Heightmap')
            return {'CANCELLED'}



        self.report({'INFO'}, 'Generated heightmap')        
        return {"FINISHED"}
        


class MG_OT_ExportTerrainAsData(bpy.types.Operator):
    bl_idname = "mirage.export_terrain_as_data"
    bl_label = "Export Terrain as Data"
    bl_description = "Export the selected Terrain as a Python list"
    bl_options = {"REGISTER"}
    

    data_type = EnumProperty(
        name = "Type of data",
        description = 'Type of data to export the terrain to',
        items = ( 
                  ('HEIGHT_1D', 'List of Heights', ''),
                  ('HEIGHT_2D', '2D List of Heights', ''),
                ),
        default = 'HEIGHT_1D',
    )

    encoding = EnumProperty(
        name = "Encoding",
        description = 'Format to encode data in',
        items = ( 
                  ('PYTHON', 'Plain Python list', ''),
                  ('CSV', 'CSV', ''),
                ),
        default = 'PYTHON',
    )

    @classmethod
    def poll(cls, context):
        return utils.is_selected_and_mesh(context)


    def invoke(self, context, event):
        """ Show settings dialog """
        
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        """ Draw settings dialog """

        self.layout.separator()
        row = self.layout.row()       
        row.prop(self, 'data_type')
        row = self.layout.row()       
        row.prop(self, 'encoding')
        row = self.layout.row()       
        row.label('Note: This could take a while!', icon='TIME')
        self.layout.separator()



    def execute(self, context):
        """ Export terrain heights as data """

        obj         = context.object
        texts       = bpy.data.texts
        name        = obj.name + '_data.py' 
        verts       = obj.data.vertices
        obj_data    = None
        
        if self.data_type == 'HEIGHT_1D':
            obj_data    = []
            comment     = '# 1D Height List for Terrain "{}"'

            for vert in verts:
                obj_data.append(vert.co.z)


        elif self.data_type == 'HEIGHT_2D':
            size        = len(verts)
            obj_data    = numpy.zeros(size)
            side        = math.sqrt(size)
            comment     = '# 2D Height List for Terrain "{}"'

            for i, vert in enumerate(verts):
                obj_data[i] = vert.co.z

            try:
                obj_data = obj_data.reshape((side, side))
                obj_data = obj_data.tolist()
            except ValueError:
                self.report({'ERROR'}, 'Can\'t export this mesh as 2D list')
                return {'CANCELLED'}


        if self.encoding == 'PYTHON':
            comment     = comment.format(obj.name)
            comment    += '\n' + ('-' * 80) + '\n'
            obj_data    = comment + str(obj_data)

        elif self.encoding == 'CSV':
            csv_output  = io.StringIO(newline='')
            writer      = csv.writer(csv_output, lineterminator='\n')

            if self.data_type == 'HEIGHT_1D':
                for value in obj_data:
                    writer.writerow([value])    
            else:
                writer.writerows(obj_data)

            obj_data    = csv_output.getvalue()
            

        text_block  = texts.new(name)
        text_block.write(obj_data)

        self.report({'INFO'}, 'Exported to text "{}"'.format(text_block.name))
        return {'FINISHED'}
        
