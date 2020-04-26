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
from os.path import join, isfile, basename, split
from os import remove
 
 
if __name__ == '__main__':
    filepath = sys.argv[5]
    
    data_list = ['libraries','objects',
                 'meshes', 'curves',
                 'texts', 'metaballs',
                 'lamps', 'cameras',
                 'fonts', 'lattices',
                 'armatures', 'materials',
                 'textures', 'images',
                 'node_groups', 'grease_pencil',
                 'actions', 'speakers',
                 'movieclips', 'sounds', 
                 'groups',
                 ] 
     
    for data in data_list:
        target_coll = eval("bpy.data." + data)
        for item in target_coll:
            if item and item.users == 0:
                target_coll.remove(item)
     
    for group in bpy.data.groups:
        if len(group.objects) == 0:
            bpy.data.groups.remove(group)
    
    for obj in bpy.data.objects:
        if "." in obj.name:
            obj.name = "_".join(obj.name.split("."))
    
    bpy.ops.wm.save_mainfile(filepath = filepath)
    
    blendfile = basename(split(filepath)[-1])
    path = filepath.split(blendfile)[0]
    
    if isfile(join(path, blendfile.split(".blend")[0] + ".blend1")):
        remove(join(path, blendfile.split(".blend")[0] + ".blend1"))
 
    bpy.ops.wm.quit_blender()
    