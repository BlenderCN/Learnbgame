# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
#

import os

# Blender Libs
import bpy, bl_operators
from bpy.props import CollectionProperty, StringProperty
from bpy.types import OperatorFileListElement
from bpy_extras.io_utils import ImportHelper
from bpy_extras.image_utils import load_image

# PBRTv3 Libs
from .. import PBRTv3Addon


def find_node_editor(nodetree_type):
    """
    Find out which space(s) of Blender's UI are a node editor that is not set to display the nodetree_type
    """
    node_editor = None

    if bpy.context.screen:
        for area in bpy.context.screen.areas:
            if area.type == 'NODE_EDITOR':
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        if space.tree_type == nodetree_type:
                            return None
                        else:
                            node_editor = space

    return node_editor


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_import_multiple_imagenodes(bpy.types.Operator, ImportHelper):
    """"""
    bl_idname = "luxrender.import_multiple_imagenodes"
    bl_label = "Import Multiple Images"
    bl_description = "Import multiple imagemaps into the node editor at once"

    files = CollectionProperty(name="File Path", type=OperatorFileListElement)
    directory = StringProperty(subtype='DIR_PATH')
    filter_glob = StringProperty(
        default="*.jpg;*.jpeg;*.png;*.tga;*.tif;*.tiff",
        options={'HIDDEN'}
    )
    filename_ext = ""  # required by ImportHelper

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRTv3_RENDER' and hasattr(context.space_data, "node_tree")

    def execute(self, context):
        location = context.space_data.cursor_location

        for file_elem in self.files:
            print("Importing image:", file_elem.name)
            filepath = os.path.join(self.directory, file_elem.name)

            image = load_image(filepath, check_existing=True)

            if image is None:
                print("Failed to load image:", filepath)
                continue

            nodetree = context.space_data.node_tree
            node = nodetree.nodes.new('pbrtv3_texture_blender_image_map_node')
            node.image_name = image.name
            node.location = location
            # Nodes are spawned in a vertical column
            location.y -= 290

        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_add_material_nodetree(bpy.types.Operator):
    """"""
    bl_idname = "luxrender.add_material_nodetree"
    bl_label = "Use Material Nodes"
    bl_description = "Add a PBRTv3 node tree linked to this material"

    # idtype = StringProperty(name="ID Type", default="material")

    def execute(self, context):
        # idtype = self.properties.idtype
        idtype = 'material'
        context_data = {'material': context.material, 'lamp': context.lamp}
        idblock = context_data[idtype]

        nt = bpy.data.node_groups.new(idblock.name, type='pbrtv3_material_nodes')
        nt.use_fake_user = True
        idblock.pbrtv3_material.nodetree = nt.name

        ctx_mat = context.material.pbrtv3_material

        # Get the mat type set in editor, todo: find a more iterative way to get context
        node_type = 'pbrtv3_material_%s_node' % ctx_mat.type

        # Some nodes were merged during the introduction of PBRTv3Core node support
        if ctx_mat.type in ['glass2', 'roughglass']:
            node_type = 'pbrtv3_material_glass_node'
        elif ctx_mat.type == 'metal':
            node_type = 'pbrtv3_material_metal2_node'

        if ctx_mat.type == 'matte':
            editor_type = ctx_mat.pbrtv3_mat_matte
        if ctx_mat.type == 'mattetranslucent':
            editor_type = ctx_mat.pbrtv3_mat_mattetranslucent
        if ctx_mat.type == 'glossy':
            editor_type = ctx_mat.pbrtv3_mat_glossy
        if ctx_mat.type == 'glossycoating':
            editor_type = ctx_mat.pbrtv3_mat_glossycoating
        if ctx_mat.type == 'glossytranslucent':
            editor_type = ctx_mat.pbrtv3_mat_glossytranslucent
        if ctx_mat.type == 'glass':
            editor_type = ctx_mat.pbrtv3_mat_glass
        if ctx_mat.type == 'glass2':
            editor_type = ctx_mat.pbrtv3_mat_glass2
        if ctx_mat.type == 'roughglass':
            editor_type = ctx_mat.pbrtv3_mat_roughglass
        if ctx_mat.type == 'mirror':
            editor_type = ctx_mat.pbrtv3_mat_mirror
        if ctx_mat.type == 'carpaint':
            editor_type = ctx_mat.pbrtv3_mat_carpaint
        if ctx_mat.type == 'metal':
            editor_type = ctx_mat.pbrtv3_mat_metal
        if ctx_mat.type == 'metal2':
            editor_type = ctx_mat.pbrtv3_mat_metal2
        if ctx_mat.type == 'velvet':
            editor_type = ctx_mat.pbrtv3_mat_velvet
        if ctx_mat.type == 'cloth':
            editor_type = ctx_mat.pbrtv3_mat_cloth
        if ctx_mat.type == 'scatter':
            editor_type = ctx_mat.pbrtv3_mat_scatter
        if ctx_mat.type == 'mix':
            editor_type = ctx_mat.pbrtv3_mat_mix
        if ctx_mat.type == 'layered':
            editor_type = ctx_mat.pbrtv3_mat_layered
        if ctx_mat.type == 'null':
            editor_type = ctx_mat.pbrtv3_mat_null

        # handling for not existent shinymetal node, just hack atm.
        if ctx_mat.type == 'shinymetal':
            editor_type = ctx_mat.pbrtv3_mat_metal2
            node_type = 'pbrtv3_material_metal2_node'

        if idtype == 'material':
            shader = nt.nodes.new(node_type)  # create also matnode from editor type
            shader.location = 250, 400

            if ctx_mat.type == 'roughglass':
                shader.rough = True

            sh_out = nt.nodes.new('pbrtv3_material_output_node')
            sh_out.interior_volume = ctx_mat.Interior_volume
            sh_out.exterior_volume = ctx_mat.Exterior_volume
            sh_out.location = 500, 400

            nt.links.new(shader.outputs[0], sh_out.inputs[0])

            # Get material settings ( color )
            if 'Absorption Color' in shader.inputs:
                shader.inputs['Absorption Color'].color = editor_type.Ka_color
            if 'Diffuse Color' in shader.inputs:
                shader.inputs['Diffuse Color'].color = editor_type.Kd_color
            if 'Reflection Color' in shader.inputs and hasattr(editor_type, 'Kr_color'):
                shader.inputs['Reflection Color'].color = editor_type.Kr_color
            if 'Specular Color' in shader.inputs:
                shader.inputs['Specular Color'].color = editor_type.Ks_color
            if 'Specular Color 1' in shader.inputs:
                shader.inputs['Specular Color 1'].color = editor_type.Ks1_color
            if 'Specular Color 2' in shader.inputs:
                shader.inputs['Specular Color 2'].color = editor_type.Ks2_color
            if 'Specular Color 3' in shader.inputs:
                shader.inputs['Specular Color 3'].color = editor_type.Ks3_color
            if 'Transmission Color' in shader.inputs and hasattr(editor_type, 'Kt_color'):
                shader.inputs['Transmission Color'].color = editor_type.Kt_color
            if 'Warp Diffuse Color' in shader.inputs:
                shader.inputs['Warp Diffuse Color'].color = editor_type.warp_Kd_color
            if 'Warp Specular Color' in shader.inputs:
                shader.inputs['Warp Specular Color'].color = editor_type.warp_Ks_color
            if 'Weft Diffuse Color' in shader.inputs:
                shader.inputs['Weft Diffuse Color'].color = editor_type.weft_Kd_color
            if 'Weft Specular Color' in shader.inputs:
                shader.inputs['Weft Specular Color'].color = editor_type.weft_Ks_color
            if 'Backface Absorption Color' in shader.inputs:
                shader.inputs['Backface Absorption Color'].color = editor_type.backface_Ka_color
            if 'Backface Specular Color' in shader.inputs:
                shader.inputs['Backface Specular Color'].color = editor_type.backface_Ks_color

            # Get various material settings ( float )
            if 'Mix Amount' in shader.inputs:
                shader.inputs['Mix Amount'].amount = editor_type.amount_floatvalue

            if 'Cauchy B' in shader.inputs and hasattr(editor_type, 'cauchyb_floatvalue'):
                shader.inputs['Cauchy B'].cauchyb = editor_type.cauchyb_floatvalue

            if 'Film IOR' in shader.inputs and hasattr(editor_type, 'filmindex_floatvalue'):
                shader.inputs['Film IOR'].filmindex = editor_type.filmindex_floatvalue

            if 'Film Thickness (nm)' in shader.inputs and hasattr(editor_type, 'film_floatvalue'):
                shader.inputs['Film Thickness (nm)'].film = editor_type.film_floatvalue

            if 'IOR' in shader.inputs and hasattr(shader.inputs['IOR'], 'index') and hasattr(editor_type, 'index_floatvalue'):
                shader.inputs['IOR'].index = editor_type.index_floatvalue  # not fresnel IOR

            if 'U-Roughness' in shader.inputs:
                if hasattr(editor_type, 'uroughness_floatvalue'):
                    shader.inputs['U-Roughness'].uroughness = editor_type.uroughness_floatvalue

            if 'V-Roughness' in shader.inputs:
                if hasattr(editor_type, 'vroughness_floatvalue'):
                    shader.inputs['V-Roughness'].vroughness = editor_type.vroughness_floatvalue

            if 'Sigma' in shader.inputs:
                shader.inputs['Sigma'].sigma = editor_type.sigma_floatvalue

            # non-socket parameters ( bool )
            if hasattr(shader, 'use_ior'):
                shader.use_ior = editor_type.useior

            if hasattr(shader, 'multibounce'):
                shader.multibounce = editor_type.multibounce

            if hasattr(shader, 'use_anisotropy'):
                if hasattr(editor_type, 'anisotropic'):
                    shader.use_anisotropy = editor_type.anisotropic

            if hasattr(shader, 'dispersion'):
                if hasattr(editor_type, 'dispersion'):
                    shader.dispersion = editor_type.dispersion

            if hasattr(shader, 'arch'):
                shader.arch = editor_type.architectural

            # non-socket parameters ( other )
            # velvet
            if hasattr(shader, 'thickness'):
                shader.thickness = editor_type.thickness

            if hasattr(shader, 'p1'):
                shader.p1 = editor_type.p1

            if hasattr(shader, 'p2'):
                shader.p2 = editor_type.p2

            if hasattr(shader, 'p3'):
                shader.p3 = editor_type.p3

            # metal 1
            if hasattr(shader, 'metal_preset'):
                shader.metal_preset = editor_type.name

            if hasattr(shader, 'metal_nkfile'):
                shader.metal_nkfile = editor_type.filename

        #else:
        #   nt.nodes.new('OutputLightShaderNode')

        # Try to find a node editor already set to material nodes
        node_editor = find_node_editor('pbrtv3_material_nodes')

        if node_editor:
            # No node editor set to volume nodes, set the last one
            node_editor.tree_type = 'pbrtv3_material_nodes'

        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_add_volume_nodetree(bpy.types.Operator):
    """"""
    bl_idname = "luxrender.add_volume_nodetree"
    bl_label = "Use Volume Nodes"
    bl_description = "Add a PBRTv3 node tree linked to this volume"

    def execute(self, context):
        current_vol_ind = context.scene.pbrtv3_volumes.volumes_index
        current_vol = context.scene.pbrtv3_volumes.volumes[current_vol_ind]

        nt = bpy.data.node_groups.new(current_vol.name, type='pbrtv3_volume_nodes_a')
        nt.use_fake_user = True
        current_vol.nodetree = nt.name

        # Volume output
        sh_out = nt.nodes.new('pbrtv3_volume_output_node')
        sh_out.location = 500, 400

        # Volume node (use volume type, i.e. clear/homogeneous/heterogeneous)
        vol_node_type = 'pbrtv3_volume_%s_node' % current_vol.type
        volume_node = nt.nodes.new(vol_node_type)
        volume_node.location = 250, 480
        nt.links.new(volume_node.outputs[0], sh_out.inputs[0])

        # Copy settings
        volume_node.inputs['IOR'].fresnel = current_vol.fresnel_fresnelvalue

        # Color at depth node
        colordepth_node = nt.nodes.new('pbrtv3_texture_colordepth_node')
        colordepth_node.location = 50, 480
        colordepth_node.depth = current_vol.depth
        nt.links.new(colordepth_node.outputs[0], volume_node.inputs[1])

        absorption_color = current_vol.sigma_a_color if current_vol.type in ['homogeneous', 'heterogeneous'] else (
            current_vol.absorption_color)

        if current_vol.absorption_scale == 1:
            colordepth_node.inputs[0].color = absorption_color
        else:
            # Value node (to be able to copy scaled colors)
            absorption_color_value_node = nt.nodes.new('pbrtv3_texture_constant_node')
            absorption_color_value_node.location = -150, 480
            absorption_color_value_node.color = absorption_color
            absorption_color_value_node.col_mult = current_vol.absorption_scale
            nt.links.new(absorption_color_value_node.outputs[0], colordepth_node.inputs[0])

        if current_vol.type in ['homogeneous', 'heterogeneous']:
            # Scattering color
            if current_vol.scattering_scale == 1:
                volume_node.inputs[2].color = current_vol.sigma_s_color
            else:
                # Value node (to be able to copy scaled colors)
                scattering_color_value_node = nt.nodes.new('pbrtv3_texture_constant_node')
                scattering_color_value_node.location = -150, 280
                scattering_color_value_node.color = current_vol.sigma_s_color
                scattering_color_value_node.col_mult = current_vol.scattering_scale
                nt.links.new(scattering_color_value_node.outputs[0], volume_node.inputs[2])

            if current_vol.type == 'heterogeneous':
                volume_node.stepsize = current_vol.stepsize

        # Try to find a node editor already set to volume nodes
        node_editor = find_node_editor('pbrtv3_volume_nodes_a')

        if node_editor:
            # No node editor set to volume nodes, set the last one
            node_editor.tree_type = 'pbrtv3_volume_nodes_a'

        return {'FINISHED'}