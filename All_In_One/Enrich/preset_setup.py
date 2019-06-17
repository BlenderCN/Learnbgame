# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#File of Enrich add-on by Akash Hamirwasia (Blender Skool)
#Preset Setup File designed for all presets to use similar code. Makes it fast and efficient

import bpy
import os

def preset_setup(preset_name, blend_name):  #Name of Node and Blend file name is passed as arguments
    bpy.context.scene.use_nodes = True
    enrich_props = bpy.context.scene.enrich_props
    mat = bpy.context.scene
    in_node = ""
    if mat.use_nodes == True:
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodnam = node.name
            if nodnam.endswith("Enrich") == True:
                in_node = node.inputs[0].links[0].from_node.name
                bpy.context.scene.node_tree.nodes.remove(node)
        if in_node == "":
            in_node = "Render Layers"

        preset_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
        try:  #Try to select preset node if already loaded in Blender
            preset_node.node_tree = bpy.data.node_groups[preset_name]
        except: #Otherwise append the node
            opath = "/"+blend_name+"\\NodeTree\\"
            nodname = preset_name
            dpath = os.path.join(os.path.dirname(__file__), "blend")+"/"+blend_name+"\\NodeTree"
            bpy.ops.wm.link(filepath=opath,filename=nodname,directory=dpath,filemode=1,link=False,autoselect=False,active_layer=True,instance_groups=False,relative_path=True)
            preset_node.node_tree = bpy.data.node_groups[preset_name] #Set the NodeGroup
        if preset_name.endswith(" Enrich"):
            preset_node.name = preset_name
        else:
            preset_node.name = preset_name+" Enrich"  #Fixing the Name of node, needed above for changing of presets

        preset_node.location = -81, 481
        #bright = bpy.context.scene.node_tree.nodes['Bright/Contrast']
        vig = bpy.context.scene.node_tree.nodes['Vignette_E']
        vig.node_tree.nodes['Ellipse Mask'].y = 0.5   #Default values setup and fixing the links
        vig.node_tree.nodes['Ellipse Mask'].x = 0.5
        enrich_props.vig_location_y = 0.5
        enrich_props.vig_location_x = 0.5
        vig.inputs[2].default_value = 0.0
        enrich_props.vig_opacity=0.0
        mix = bpy.context.scene.node_tree.nodes['Mix 1_E']
        new_links = bpy.context.scene.node_tree.links.new
        new_links(preset_node.inputs[0], bpy.context.scene.node_tree.nodes[in_node].outputs[0])
        new_links(mix.inputs[1], preset_node.outputs[0])
