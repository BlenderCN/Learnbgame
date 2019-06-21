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

import bpy
import bmesh

from bpy.props import StringProperty

from .. import data
from .. import vgroups


class MG_OT_SelectHeightmap(bpy.types.Operator):
    bl_idname = "mirage.select_heightmap"
    bl_label = "Select Heightmap"
    bl_description = "Open the filebrowser to select a heightmap file"
    bl_options = {"REGISTER"}
    
    filepath = StringProperty(subtype="FILE_PATH")

    filename_ext = ".png"

    filter_glob = StringProperty(
        default="*.png;*.jpg;*.bmp",
        options={'HIDDEN'}
    )
    
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
        
    def execute(self, context):
        global heightmap_name
        
        settings = data.settings('terrain')
    
        # Try to load the image
        try:
            bpy.data.images.load(self.filepath)
        except RuntimeError:
            data.errors['heightmap_file'] = True
            return
        
        # Add it to a texture
        try:
            texture = bpy.data.textures['Heightmap Texture']
        except KeyError:
            texture = bpy.data.textures.new(name='Heightmap Texture', type='IMAGE')
        
        # Add icon to heightmap list
        if self.filepath not in data.heightmap_icons.paths:
            data.heightmap_icons.paths.append(self.filepath)
            data.heightmap_count += 1

        # No errors if we got this far            
        data.errors['heightmap_file'] = False        
            
        settings.heightmap_filepath = self.filepath
        settings.heightmap_list = self.filepath
        
        return {"FINISHED"}
        
        

            
class MG_OT_MapToTerrain(bpy.types.Operator):
    bl_idname = "mirage.map_to_terrain"
    bl_label = "Generate terrain from Heightmap file"
    bl_description = "Generate a terrain from a heightmap"
    bl_options = {"REGISTER"}
    
    
    
    @classmethod
    def poll(cls, context):
        return (data.settings('terrain').heightmap_filepath != '')

    
    def execute(self, context):
        """ Create Terrain mesh from heightmap """
        
        settings    = data.settings('terrain')
        self.detail = settings.heightmap_detail
        
                
        print('\nMirage: Making Terrain from Heightmap' + ('-'*70))        
        print('Adding Grid')
        
        bpy.ops.mesh.primitive_grid_add(
                                    x_subdivisions = self.detail,
                                    y_subdivisions = self.detail,
                                    radius = math.sqrt(settings.size) / 2
                                       )
                             

        texture = bpy.data.textures['Heightmap Texture']          
        image_name = bpy.path.basename(settings.heightmap_filepath)
        image = bpy.data.images[image_name]
        texture.image = image

        obj = context.object

        print('UV Unwraping')
        # This is the kind of thing that makes me hate context
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.unwrap()
        bpy.ops.object.mode_set(mode='OBJECT')            

        # Set up terrain and modifier
        obj.name = 'Terrain'
        displace = obj.modifiers.new(name='Heightmap',type='DISPLACE')
        displace.texture = texture
        displace.direction = 'Z'
        displace.texture_coords = 'UV'
        displace.strength = settings.heightmap_strength 

        # Shade smooth
        obj.select = True
        context.scene.objects.active = obj
        bpy.ops.object.shade_smooth()

        # Making Vgroups here:
        # 1. Duplicate
        # 2. Apply the modifier
        # 3. Build some vgroups from that
        # 4. Delete temp duplicate
        
       
        print('Generating Vertex group')
        bm = vgroups.get_bmesh_from_heightmap(obj, context)
        
        vgroups.generate_height(obj, bm)
        vgroups.generate_slope(obj, bm)
        vgroups.convert_to_color_group(obj, 'Height')
        vgroups.convert_to_color_group(obj, 'Slope')
                
        bpy.ops.object.delete()
        obj.select = False

        return {"FINISHED"}
