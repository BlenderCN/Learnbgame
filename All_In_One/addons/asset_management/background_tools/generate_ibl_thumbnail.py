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
    IBL_dir = sys.argv[5]
    ibl_list_name = sys.argv[6].split(";")
    thumbnail_dir = sys.argv[7]
    thumb_ext = sys.argv[8]
 
    current_dir_path = dirname(abspath(__file__))
    addon_dir = basename(split(current_dir_path)[-2])
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[addon_dir].preferences
     
    # thumbnails resolution
    ref = int(addon_prefs.thumbnails_resolution)
        
    settings = bpy.context.scene.render.image_settings
    
    settings.file_format = 'PNG' if thumb_ext == '.png' else 'JPEG'
    settings.color_mode = 'RGBA' if thumb_ext == '.png' else 'RGB'
    settings.color_depth = '8'
    
    for thumb in ibl_list_name:
        img = bpy.data.images.load(join(IBL_dir, thumb))
        coef = img.size[1] / ref
        img.scale(img.size[0]/coef, ref)
        img.save_render(join(thumbnail_dir, thumb.rsplit(".", 1)[0] + thumb_ext))
    
    bpy.ops.wm.quit_blender()