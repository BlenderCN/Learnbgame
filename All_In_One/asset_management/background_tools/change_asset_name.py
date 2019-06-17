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
 
if __name__ == '__main__':
    target = sys.argv[5]
    new_name = sys.argv[6]
    filepath = sys.argv[7]
    type = sys.argv[8]
    
    if type == 'assets':
        bpy.data.objects[target].name = new_name
    elif type == 'materials':
        bpy.data.materials[target].name = new_name
    elif type == 'scenes':
        bpy.context.scene.name = new_name
    
    bpy.ops.wm.save_mainfile(filepath = filepath)
             
    bpy.ops.wm.quit_blender()