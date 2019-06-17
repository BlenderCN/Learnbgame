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
 
 
import bpy, sys
from os import remove
from os.path import join, isfile

if __name__ == '__main__':
    material = sys.argv[5]
    source_file = sys.argv[6]
    blendfile = sys.argv[7]
    pack = sys.argv[8]
    
    
    directory = join(source_file, "Material")
    
    with bpy.data.libraries.load(source_file) as (data_from, data_to):
        bpy.ops.wm.append(filename = material, directory = directory)
        
    bpy.data.objects["_Sphere"].active_material = bpy.data.materials[material]
    
    if pack:
        bpy.ops.file.pack_all()
    
    bpy.ops.wm.save_mainfile()
    
    to_delete = blendfile.split(".blend")[0] + ".blend1"
    if isfile(to_delete):
        remove(to_delete)
    
    bpy.ops.wm.quit_blender()
    