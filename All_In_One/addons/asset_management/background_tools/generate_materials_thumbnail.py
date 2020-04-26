'''
Copyright (C) 2015 Pistiwique, Pitiwazou
 
Created by Pistiwique, Pitiwazou
 
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
 
 
import bpy
import sys
from os.path import join, dirname, abspath, basename, split

if __name__ == '__main__':
    source_file = sys.argv[5]
    materials = sys.argv[6].split(";") if ";" in sys.argv[6] else [sys.argv[6]]
    category_path = sys.argv[7]
    thumb_ext = sys.argv[8]
    
    print(materials)
    
    current_dir_path = dirname(abspath(__file__))
    addon_dir = basename(split(current_dir_path)[-2])
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[addon_dir].preferences
    icon_path = join(category_path, "icons")
     
    # thumbnails resolution
    bpy.context.scene.render.resolution_x = int(addon_prefs.thumbnails_resolution)
    bpy.context.scene.render.resolution_y = int(addon_prefs.thumbnails_resolution)
    
    # Render Type
    if bpy.context.user_preferences.system.compute_device_type == 'CUDA' and addon_prefs.render_type == 'GPU':
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.render.tile_x = 256
        bpy.context.scene.render.tile_y = 256
     
    else:
        bpy.context.scene.cycles.device = 'CPU'
        bpy.context.scene.render.tile_x = 32
        bpy.context.scene.render.tile_y = 32
    
     
    bpy.context.scene.cycles.samples = addon_prefs.samples_value
    
    with bpy.data.libraries.load(source_file) as (data_from, data_to):
        if data_from.materials:
            directory = join(source_file, "Material")
            for mat in materials:
                bpy.ops.wm.append(filename = mat, directory = directory)
    
    for mat in materials:    
        bpy.context.active_object.active_material = bpy.data.materials[mat]
        
        bpy.ops.render.render()
        
        bpy.data.images["Render Result"].save_render(filepath = join(icon_path, mat + thumb_ext))
    
    bpy.ops.wm.quit_blender()