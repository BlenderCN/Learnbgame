# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Jens Verwiebe, Jason Clarke, Asbjørn Heid
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****

import re

import bpy

from ..extensions_framework import declarative_property_group

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom

from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
class luxrender_mat_node_editor(bpy.types.NodeTree):
    '''LuxRender Material Nodes'''

    bl_idname = 'luxrender_material_nodes'
    bl_label = 'LuxRender Material Nodes'
    bl_icon = 'MATERIAL'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'LUXRENDER_RENDER'
        # This function will set the current node tree to the one belonging
        # to the active material (code orignally from Matt Ebb's 3Delight exporter)

    @classmethod
    def get_from_context(cls, context):
        ob = context.active_object
        if ob and ob.type not in {'LAMP', 'CAMERA'}:
            ma = ob.active_material

            if ma is not None:
                nt_name = ma.luxrender_material.nodetree

                if nt_name:
                    return bpy.data.node_groups[ma.luxrender_material.nodetree], ma, ma
        # Uncomment if/when we make lamp nodes
        # elif ob and ob.type == 'LAMP':
        #     la = ob.data
        #     nt_name = la.luxrender_lamp.nodetree
        #     if nt_name:
        #         return bpy.data.node_groups[la.luxrender_lamp.nodetree], la, la

        return None, None, None

    # This block updates the preview, when socket links change
    def update(self):
        self.refresh = True

    def acknowledge_connection(self, context):
        while self.refresh:
            self.refresh = False
            break

    refresh = bpy.props.BoolProperty(name='Links Changed', default=False, update=acknowledge_connection)


# Registered specially in init.py
class luxrender_node_category(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'luxrender_material_nodes'


luxrender_node_catagories = [
    luxrender_node_category("LUX_INPUT", "Input", items=[
        NodeItem("luxrender_2d_coordinates_node"),
        NodeItem("luxrender_3d_coordinates_node"),
        NodeItem("luxrender_texture_blackbody_node"),
        NodeItem("luxrender_texture_gaussian_node"),
        NodeItem("luxrender_texture_glossyexponent_node"),
        NodeItem("luxrender_texture_tabulateddata_node"),
        NodeItem("luxrender_texture_constant_node"),  # value node
        NodeItem("luxrender_texture_hitpointcolor_node"),  # vertex color node
        NodeItem("luxrender_texture_hitpointgrey_node"),  # vertex mask node
        # NodeItem("NodeGroupInput", poll=group_input_output_item_poll), ...maybe...
    ]),

    luxrender_node_category("LUX_OUTPUT", "Output", items=[
        NodeItem("luxrender_material_output_node"),
        # NodeItem("NodeGroupOutput", poll=group_input_output_item_poll),
    ]),

    luxrender_node_category("LUX_MATERIAL", "Material", items=[
        NodeItem("luxrender_material_carpaint_node"),
        NodeItem("luxrender_material_cloth_node"),
        NodeItem("luxrender_material_glass_node"),
        NodeItem("luxrender_material_glass2_node"),
        NodeItem("luxrender_material_glossy_node"),
        NodeItem("luxrender_material_glossycoating_node"),
        NodeItem("luxrender_material_glossytranslucent_node"),
        NodeItem("luxrender_material_matte_node"),
        NodeItem("luxrender_material_mattetranslucent_node"),
        NodeItem("luxrender_material_metal_node"),
        NodeItem("luxrender_material_metal2_node"),
        NodeItem("luxrender_material_mirror_node"),
        NodeItem("luxrender_material_roughglass_node"),
        NodeItem("luxrender_material_scatter_node"),
        NodeItem("luxrender_material_shinymetal_node"),
        NodeItem("luxrender_material_velvet_node"),
        NodeItem("luxrender_material_null_node"),
        NodeItem("luxrender_material_mix_node"),
        NodeItem("luxrender_material_doubleside_node"),
        NodeItem("luxrender_material_layered_node"),
    ]),

    luxrender_node_category("LUX_TEXTURE", "Texture", items=[
        NodeItem("luxrender_texture_image_map_node"),
        NodeItem("luxrender_texture_normal_map_node"),
        NodeItem("luxrender_texture_blender_blend_node"),
        NodeItem("luxrender_texture_brick_node"),
        NodeItem("luxrender_texture_blender_clouds_node"),
        NodeItem("luxrender_texture_vol_cloud_node"),
        NodeItem("luxrender_texture_blender_distortednoise_node"),
        NodeItem("luxrender_texture_vol_exponential_node"),
        NodeItem("luxrender_texture_fbm_node"),
        NodeItem("luxrender_texture_harlequin_node"),
        NodeItem("luxrender_texture_blender_marble_node"),
        NodeItem("luxrender_texture_blender_musgrave_node"),
        NodeItem("luxrender_texture_blender_stucci_node"),
        NodeItem("luxrender_texture_vol_smoke_data_node"),
        NodeItem("luxrender_texture_uv_node"),
        NodeItem("luxrender_texture_windy_node"),
        NodeItem("luxrender_texture_blender_wood_node"),
        NodeItem("luxrender_texture_wrinkled_node"),
        NodeItem("luxrender_texture_blender_voronoi_node"),
    ]),

    luxrender_node_category("LUX_VOLUME", "Volume", items=[
        NodeItem("luxrender_volume_clear_node"),
        NodeItem("luxrender_volume_homogeneous_node"),
        NodeItem("luxrender_volume_heterogeneous_node"),
    ]),

    luxrender_node_category("LUX_LIGHT", "Light", items=[
        NodeItem("luxrender_light_area_node"),
    ]),

    luxrender_node_category("LUX_FRESNEL", "Fresnel Data", items=[
        NodeItem("luxrender_texture_cauchy_node"),
        NodeItem("luxrender_texture_fresnelcolor_node"),
        NodeItem("luxrender_texture_fresnelname_node"),
        NodeItem("luxrender_texture_sellmeier_node"),
    ]),

    luxrender_node_category("LUX_CONVERTER", "Converter", items=[
        NodeItem("luxrender_texture_add_node"),
        NodeItem("luxrender_texture_bump_map_node"),
        NodeItem("luxrender_texture_colordepth_node"),
        NodeItem("luxrender_texture_mix_node"),
        NodeItem("luxrender_texture_scale_node"),
        NodeItem("luxrender_texture_subtract_node"),
    ]),

    luxrender_node_category("LUX_LAYOUT", "Layout", items=[
        NodeItem("NodeFrame"),
        # NodeItem("NodeReroute") #not working yet
    ]),
]
