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
    scene_name = sys.argv[5]
    filepath = sys.argv[6]
    pack = sys.argv[7]
    lib_type = sys.argv[8]
    material = sys.argv[9]
    text_file = sys.argv[10]
    world_name = sys.argv[11]
    ibl_path = sys.argv[12]

# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
    
    def assets_clear_world():
        """ Retaining only the selected object and the active scene before adding in the library """

        scene = bpy.data.scenes[scene_name]
        layers = [i for i in range(20) if scene.layers[i]]
        
        # recovering the selected objects list and their children
        objs = set()
     
        def add_obj(obj):
            objs.add(obj)
     
            for child in obj.children:
                add_obj(child)
     
        for obj in scene.objects:
            if obj.select:
                add_obj(obj)
        
        
        # activates all the layers
        for i in range(20):
            scene.layers[i] = True
        
        # before cleaning the objects are prepared
        for obj in scene.objects:
            obj.hide_select = False
            obj.hide = False
            if obj in objs:
                obj.select = True
     
        bpy.ops.object.select_all(action = 'INVERT')
        
        bpy.ops.group.objects_remove_all()
         
        bpy.ops.object.delete()
        
        bpy.ops.object.select_all(action = 'SELECT')
        
        for i in range(20):
            if i not in layers:
                scene.layers[i] = False
        
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
    
    # clean the unused scenes
    for scn in bpy.data.scenes:
        if scn.name != scene_name:
            bpy.data.scenes.remove(scn, do_unlink = True)
    
    # clean the worlds
    if lib_type == 'assets':
        for world in bpy.data.worlds:
            if world.users:
                world.user_clear()
            bpy.data.worlds.remove(world)
        
        assets_clear_world()
    
    if ibl_path and world_name:
        environment = ""
        for node in bpy.data.worlds[world_name].node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT':
                environment = node.name
                
        bpy.data.worlds[world_name].node_tree.nodes[environment].image.filepath = ibl_path
       
    for images in bpy.data.images:
        if not images.packed_file:
            if not isfile(bpy.path.abspath(images.filepath)):
                images.user_clear()
                bpy.data.images.remove(images)
    
    if pack:
        bpy.ops.file.pack_all()
    bpy.ops.wm.save_mainfile(filepath = filepath)
    
    blendfile = basename(split(filepath)[-1])
    path = filepath.split(blendfile)[0]
    
    if isfile(text_file):
        remove(text_file)
    
    if isfile(join(path, blendfile.split(".blend")[0] + ".blend1")):
        remove(join(path, blendfile.split(".blend")[0] + ".blend1"))
     
    bpy.ops.wm.quit_blender()