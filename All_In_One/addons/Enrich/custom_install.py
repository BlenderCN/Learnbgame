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

# Custom Installation File comes with Enrich Add-on by Akash Hamirwasia (Blender Skool)

import bpy
import os
def custom_install():
    enrich_props = bpy.context.scene.enrich_props
    path = os.path.join(os.path.dirname(__file__), "icon")
    sl = path.rfind("\\")
    path = path[:sl]+"\\"
    node_name = enrich_props.install_node_name
    if enrich_props.install_blend_name != "" and enrich_props.install_node_name != "" and enrich_props.install_cod_name != "":
        if not enrich_props.install_blend_name.endswith(".blend"): #Improve the values entered by the user
            enrich_props.install_blend_name = enrich_props.install_blend_name+".blend"
        if not enrich_props.install_node_name.endswith("Enrich"):
            enrich_props.install_node_name = enrich_props.install_node_name+" Enrich"

        try: #Start with the Code Generation
            file = open(path+enrich_props.install_cod_name+".py", 'w')
            file.write("import bpy\n")
            file.write("import os\n")
            file.write("def "+enrich_props.install_cod_name+"():\n")
            file.write("\tbpy.context.scene.use_nodes = True\n")
            file.write("\tenrich_props = bpy.context.scene.enrich_props\n")
            file.write("\tmat = bpy.context.scene\n")
            file.write("\tif mat.use_nodes == True:\n")
            file.write("\t\tnodes = mat.node_tree.nodes\n")
            file.write("\t\tfor node in nodes:\n")
            file.write("\t\t\tnodnam = node.name\n")
            file.write("\t\t\tif nodnam.endswith(\"Enrich\") == True:\n")
            file.write("\t\t\t\tbpy.context.scene.node_tree.nodes.remove(node)\n")
            file.write("\t\topath = \"/"+enrich_props.install_blend_name+"\\\\NodeTree\\\\\"\n")
            file.write("\t\tnodname = '"+node_name+"'\n")
            file.write("\t\tdpath = os.path.join(os.path.dirname(__file__), \"blend\")+ \"/"+enrich_props.install_blend_name+"\\\\NodeTree\"\n")
            file.write("\t\tbpy.ops.wm.link(filepath=opath,filename=nodname,directory=dpath,filemode=1,link=False,autoselect=False,active_layer=True,instance_groups=False,relative_path=True)\n")
            file.write("\t\tcustom_node = bpy.context.scene.node_tree.nodes.new(\"CompositorNodeGroup\")\n")
            file.write("\t\tcustom_node.node_tree = bpy.data.node_groups['"+node_name+"']\n")
            file.write("\t\tcustom_node.name = '"+enrich_props.install_node_name+"'\n\n")

            file.write("\t\tcustom_node.location = 155, 474\n")
            file.write("\t\tbright = bpy.context.scene.node_tree.nodes['Bright/Contrast']\n")
            file.write("\t\tvig = bpy.context.scene.node_tree.nodes['Vignette_E']\n")
            file.write("\t\tvig.node_tree.nodes['Ellipse Mask'].y = 0.5\n")
            file.write("\t\tvig.node_tree.nodes['Ellipse Mask'].x = 0.5\n")
            file.write("\t\tenrich_props.vig_location_y = 0.5\n")
            file.write("\t\tenrich_props.vig_location_x = 0.5\n")
            file.write("\t\tvig.inputs[2].default_value = 0.0\n")
            file.write("\t\tenrich_props.vig_opacity=0.0\n")
            file.write("\t\tmix = bpy.context.scene.node_tree.nodes['Mix 1_E']\n")
            file.write("\t\tnew_links = bpy.context.scene.node_tree.links.new\n")
            file.write("\t\tnew_links(custom_node.inputs[0], bright.outputs[0])\n")
            file.write("\t\tnew_links(mix.inputs[1], custom_node.outputs[0])\n")
            file.close()
            enrich_props.install_blend_bool = 2
        except:
            enrich_props.install_blend_bool = 1
