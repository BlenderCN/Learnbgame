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

import bpy
import os
def composite_nodes_generate():
    opath = "/Enrich_requirements.blend\\NodeTree\\"
    nodname = "Vignette_E" #Append the Vignette Node
    dpath = os.path.join(os.path.dirname(__file__), "blend", "Enrich_requirements.blend")+"\\NodeTree"
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    vignette = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    vignette.node_tree = bpy.data.node_groups['Vignette_E']
    vignette.name = "Vignette_E"
    vignette.mute = True
    vignette.location = 2249.213, 476.31

    nodname = "Vibrance_E" #Append the Vibrance Node
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    vibrance = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    vibrance.node_tree = bpy.data.node_groups['Vibrance_E']
    vibrance.name = "Vibrance_E"
    vibrance.mute = True
    vibrance.location = 1028.655, 480.799

    nodname = "Temperature_E" #Append the temperature Node
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    temperature = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    temperature.node_tree = bpy.data.node_groups['Temperature_E']
    temperature.name = "Temperature_E"
    temperature.mute = True
    temperature.location = 808.655, 482.624

    nodname = "Sharp and Soften_E" #Append the Shapren and Soften Node_Group
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    sharpen_soften = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    sharpen_soften.node_tree = bpy.data.node_groups['Sharp and Soften_E']
    sharpen_soften.name = "Sharp and Soften_E"
    sharpen_soften.mute = True
    sharpen_soften.location = 1797.407, 480.799

    nodname = "Lens Effects_E" #Append the Shapren and Soften Node_Group
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    lens_effects = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    lens_effects.node_tree = bpy.data.node_groups['Lens Effects_E']
    lens_effects.name = "Lens Effects_E"
    lens_effects.mute = True
    lens_effects.location = 2029.213, 480.799

    nodname = "Bright/Contrast_E"
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    bright = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    bright.node_tree = bpy.data.node_groups['Bright/Contrast_E']
    bright.name = "Bright/Contrast_E"
    bright.mute = False
    bright.location = 394, 492

    nodname = "Colors_E"
    bpy.ops.wm.append(filepath=opath+nodname,filename=nodname,directory=dpath,link=False,autoselect=False, set_fake=False)
    colors = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
    colors.node_tree = bpy.data.node_groups['Colors_E']
    colors.name = "Colors_E"
    colors.mute = True
    colors.location = 571, 481

    node_check = True
    for node in bpy.context.scene.node_tree.nodes:
        if node.name != "Render Layers":
            node_check = True
        else:
            node_check = False
            break
    if node_check == True:
        bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")

    layer = bpy.context.scene.node_tree.nodes['Render Layers'] #Render Layers Node
    layer.location = -321, 542

    node_check = True
    for node in bpy.context.scene.node_tree.nodes:
        if node.name != "Composite":
            node_check = True
        else:
            node_check = False
            break
    if node_check == True:
        bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")

    out = bpy.context.scene.node_tree.nodes['Composite'] #Composite Node
    out.location = 2857.213, 505.0

    #link1 = layer.outputs[0].links[0] #Fix Linking
    #bpy.context.scene.node_tree.links.remove(link1)

    split = bpy.context.scene.node_tree.nodes.new("CompositorNodeSplitViewer") #Split View Node
    split.location = 3057.213, 505.0
    split.factor = 100

    color_bal =bpy.context.scene.node_tree.nodes.new("CompositorNodeColorBalance") #Color Balance Node
    color_bal.name = "Color Balance_E"
    color_bal.mute = True
    color_bal.location = 1271.025, 480.799

    mix = bpy.context.scene.node_tree.nodes.new("CompositorNodeMixRGB") #MixRGB Nodes
    mix.name = "Mix 1_E"
    mix.location = 155, 474
    mix.inputs[0].default_value = 0

    mix2 = bpy.context.scene.node_tree.nodes.new("CompositorNodeMixRGB")
    mix2.name = "Mix 2_E"
    mix2.location = 2691.213, 508.0
    mix2.inputs[0].default_value = 1.0

    crop = bpy.context.scene.node_tree.nodes.new("CompositorNodeCrop") #Crop Node
    crop.name = "Crop_E"
    crop.location = 2483.213, 519
    crop.relative = True
    crop.rel_min_x = 1
    crop.rel_min_y = 0
    crop.rel_min_y = 0
    crop.rel_max_y = 1

    try:
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                area.spaces.active.image = bpy.data.images['Viewer Node']
    except:
        pass

    #Node Links
    new_links = bpy.context.scene.node_tree.links.new
    new_links(out.inputs[0], mix2.outputs[0])
    new_links(mix2.inputs[2], crop.outputs[0])
    new_links(vibrance.inputs[0], temperature.outputs[0])
    new_links(color_bal.inputs[1], vibrance.outputs[0])
    new_links(sharpen_soften.inputs[0], color_bal.outputs[0])
    new_links(lens_effects.inputs[0], sharpen_soften.outputs[0])
    new_links(vignette.inputs[0], lens_effects.outputs[0])
    new_links(crop.inputs[0], vignette.outputs[0])
    new_links(split.inputs[0], layer.outputs[0])
    new_links(temperature.inputs[0], colors.outputs[0])
    new_links(bright.inputs[0], mix.outputs[0])
    new_links(colors.inputs[0], bright.outputs[0])
    new_links(colors.inputs[1], layer.outputs[2])
    new_links(mix.inputs[2], layer.outputs[0])
    new_links(split.inputs[1], mix2.outputs[0])
    enrich_props = bpy.context.scene.enrich_props
    enrich_props.gen_bool = True
