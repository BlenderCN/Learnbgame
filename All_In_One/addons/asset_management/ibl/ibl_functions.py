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
 
import bpy, subprocess
from os import listdir
from os.path import join, isfile
from ..function_utils.get_path import (get_addon_path,
                                       get_directory,
                                       get_library_path,
                                       )
 
 
def check_existing_IBL_Tool(world):
    """ Check if the AM_IBL_Worl setup exist """
 
    if world in bpy.data.worlds:
        return True
    return False

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def update_projection(sef, context):
    AM = bpy.context.window_manager.asset_m
    IBL_world = bpy.data.worlds["AM_IBL_WORLD"]
    nodes = IBL_world.node_tree.nodes
    nodes['Environment'].projection = AM.projection
    nodes['Reflexion'].projection = AM.projection
     
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def setup_node_editor():
    """ Setup the node editor """
 
    bpy.context.area.type = 'NODE_EDITOR'
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.space_data.tree_type = 'ShaderNodeTree'
    bpy.context.space_data.shader_type = 'WORLD'
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def get_ibl_from_thumbnail(ibl, dir):
    """ Get the ibl full path from the selected preview """
 
    extentions = (".hdr", ".exr", ".jpg", ".jpeg", ".png", ".tif")
    ibl_name = [f for f in listdir(dir) if f.endswith(extentions) and f.rsplit(".", 1)[0] == ibl.rsplit(".", 1)[0]]
 
    return ibl_name[0]

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def generate_thumbnail_ibl(thumbnail_directory):
    """ Generate the thumbnails of the IBL """
    
    AM = bpy.context.window_manager.asset_m
    addon_path = get_addon_path()
    IBL_dir = get_directory("IBL")
    thumb_list = ";".join(AM.ibl_to_thumb)
    script_thumbnailer = join(addon_path, "background_tools", 'generate_ibl_thumbnail.py')
    blend_thumbnailer = join(addon_path, 'blend_tools', 'asset', 'thumbnailer.blend')
    subprocess.Popen([bpy.app.binary_path, blend_thumbnailer, '-b', '--python', script_thumbnailer, IBL_dir, thumb_list, thumbnail_directory, AM.thumb_ext])
     
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def import_ibl_from_asset_management():
    """ Import and setup ibl """
 
    WM = bpy.context.window_manager
    AM = WM.asset_m
    addon_path = get_addon_path()
    library_path = get_library_path()
    ibl_node_group = "AM_IBL_Tool"
    blur_node_group = "ImageBlur"
    directory_path = get_directory("IBL")
 
    setup_node_editor()
 
    if not check_existing_IBL_Tool("AM_IBL_WORLD"):
        blendfile = join(addon_path, "blend_tools", "IBL", "IBL_Tool.blend")
        directory = join(blendfile, "NodeTree")
 
        IBL_world = bpy.data.worlds.new("AM_IBL_WORLD")
        IBL_world.use_nodes = True
        bpy.context.scene.world = IBL_world
        nodes = IBL_world.node_tree.nodes
 
        nodes.remove(nodes["Background"])
 
        with bpy.data.libraries.load(blendfile) as (data_from, data_to):
            if data_from.node_groups:
                bpy.ops.wm.append(filename=ibl_node_group, directory=directory)
                bpy.ops.wm.append(filename=blur_node_group, directory=directory)
 
        tex_coord_node = nodes.new("ShaderNodeTexCoord")
        tex_coord_node.location = -810, 260
 
        mapping_node = nodes.new("ShaderNodeMapping")
        mapping_node.location = -560, 280
 
        blur_node = nodes.new("ShaderNodeGroup")
        blur_node.location = -140, 200
        blur_node.name = blur_node_group
        blur_node.node_tree = bpy.data.node_groups[blur_node_group]
 
 
        env_node = nodes.new("ShaderNodeTexEnvironment")
        env_node.location = 100, 360
        env_node.name = "Environment"
        
        reflexion_node = nodes.new("ShaderNodeTexEnvironment")
        reflexion_node.location = 100, 120
        reflexion_node.name = "Reflexion"
        
        ibl_name = get_ibl_from_thumbnail(WM.AssetM_previews, directory_path)
        img = bpy.data.images.load(join(directory_path, ibl_name))
        env_node.image = img
        reflexion_node.image = img
 
        ibl_node = nodes.new("ShaderNodeGroup")
        ibl_node.location = 320, 300
        ibl_node.name = ibl_node_group
        ibl_node.node_tree = bpy.data.node_groups[ibl_node_group]
 
        output_node = nodes["World Output"]
        output_node.location = 550, 300
 
        tree = IBL_world.node_tree
        tree.links.new(tex_coord_node.outputs[3], mapping_node.inputs[0])
        tree.links.new(mapping_node.outputs[0], blur_node.inputs[0])
        tree.links.new(mapping_node.outputs[0], env_node.inputs[0])
        tree.links.new(blur_node.outputs[0], reflexion_node.inputs[0])
        tree.links.new(env_node.outputs[0], ibl_node.inputs[1])
        tree.links.new(reflexion_node.outputs[0], ibl_node.inputs[6])
        tree.links.new(ibl_node.outputs[0], output_node.inputs[0])
 
    else:
        IBL_world = bpy.data.worlds["AM_IBL_WORLD"]
        IBL_world.use_nodes = True
        bpy.context.scene.world = IBL_world
        nodes = IBL_world.node_tree.nodes
        ibl_name = get_ibl_from_thumbnail(WM.AssetM_previews, directory_path)
        
        if not "Reflexion" in IBL_world.node_tree.nodes:
            reflexion_node = nodes.new("ShaderNodeTexEnvironment")
            reflexion_node.location = 100, 120
            reflexion_node.name = "Reflexion"
            
            tree = IBL_world.node_tree
            tree.links.new(nodes['Mapping'].outputs[0], nodes['Environment'].inputs[0])
            tree.links.new(nodes['ImageBlur'].outputs[0], reflexion_node.inputs[0])
            tree.links.new(reflexion_node.outputs[0], nodes['AM_IBL_Tool'].inputs[6])
            
        
        if ibl_name in bpy.data.images:
            nodes["Environment"].image = bpy.data.images[ibl_name]
            nodes["Reflexion"].image = bpy.data.images[ibl_name]
        else:
            img = bpy.data.images.load(join(directory_path, ibl_name))
            nodes["Environment"].image = img
            nodes["Reflexion"].image = img
    
    if isfile(join(directory_path, WM.AssetM_previews.rsplit(".", 1)[0] + "_settings")):
        bpy.ops.wm.load_ibl_settings()
        
    else:  
        nodes['Mapping'].rotation = (0.0, 0.0, 0.0)
        AM.projection = 'EQUIRECTANGULAR'
        nodes['ImageBlur'].inputs[1].default_value = 0.0
        IBL_world.cycles_visibility.camera = True
        bpy.context.scene.cycles.film_transparent = False
        nodes['AM_IBL_Tool'].inputs[0].default_value = 1.0
        nodes['AM_IBL_Tool'].inputs[2].default_value = 1.0
        nodes['AM_IBL_Tool'].inputs[3].default_value = 1.0
        nodes['AM_IBL_Tool'].inputs[4].default_value = (0.5, 0.5, 0.5, 1.0)
        nodes['AM_IBL_Tool'].inputs[5].default_value = 0.5
        nodes['AM_IBL_Tool'].inputs[7].default_value = 1.0
        nodes['AM_IBL_Tool'].inputs[8].default_value = 1.0
        nodes['AM_IBL_Tool'].inputs[9].default_value = (0.5, 0.5, 0.5, 1.0)
        nodes['AM_IBL_Tool'].inputs[10].default_value = 0.5
        
        
    bpy.context.area.type = 'VIEW_3D'
    cycles = bpy.context.scene.cycles
    if cycles.sample_clamp_direct == 0 and cycles.sample_clamp_indirect == 0:
        bpy.context.scene.cycles.sample_clamp_direct = 3
        bpy.context.scene.cycles.sample_clamp_indirect = 3