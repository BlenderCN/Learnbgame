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
from ..properties import (luxrender_node, luxrender_material_node, get_linked_node, check_node_export_material,
                          check_node_export_texture, check_node_get_paramset, ExportedVolumes)

from ..properties.texture import (
    import_paramset_to_blender_texture, shorten_name, refresh_preview
)
from ..export import ParamSet, process_filepath_data
from ..export.materials import (
    MaterialCounter, TextureCounter, ExportedMaterials, ExportedTextures, get_texture_from_scene
)

from ..outputs import LuxManager, LuxLog

from ..properties.node_sockets import *


class luxrender_texture_maker:
    def __init__(self, lux_context, root_name):
        def _impl(tex_variant, tex_type, tex_name, tex_params):
            nonlocal lux_context
            texture_name = '%s::%s' % (root_name, tex_name)

            with TextureCounter(texture_name):
                print('Exporting texture, variant: "%s", type: "%s", name: "%s"' % (tex_variant, tex_type, tex_name))

                ExportedTextures.texture(lux_context, texture_name, tex_variant, tex_type, tex_params)
                ExportedTextures.export_new(lux_context)

                return texture_name

        self.make_texture = _impl


def get_socket_paramsets(sockets, make_texture):
    params = ParamSet()

    for socket in sockets:
        if not hasattr(socket, 'get_paramset'):
            print('No get_paramset() for socket %s' % socket.bl_idname)
            continue

        if not socket.enabled:
            print('Disabled socket %s will not be exported' % socket.bl_idname)
            continue

        params.update(socket.get_paramset(make_texture))

    return params


# Material nodes alphabetical
@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_carpaint(luxrender_material_node):
    # Description string
    """Car paint material node"""
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'luxrender_material_carpaint_node'
    # Label for nice name display
    bl_label = 'Car Paint Material'
    # Icon identifier
    bl_icon = 'MATERIAL'
    bl_width_min = 200

    # Get menu items from old material editor properties
    for prop in luxrender_mat_carpaint.properties:
        if prop['attr'].startswith('name'):
            carpaint_items = prop['items']

    def change_is_preset(self, context):
        # Hide unused params when using presets
        self.inputs['Diffuse Color'].enabled = self.carpaint_presets == '-'
        self.inputs['Specular Color 1'].enabled = self.carpaint_presets == '-'
        self.inputs['Specular Color 2'].enabled = self.carpaint_presets == '-'
        self.inputs['Specular Color 3'].enabled = self.carpaint_presets == '-'
        self.inputs['M1'].enabled = self.carpaint_presets == '-'
        self.inputs['M2'].enabled = self.carpaint_presets == '-'
        self.inputs['M3'].enabled = self.carpaint_presets == '-'
        self.inputs['R1'].enabled = self.carpaint_presets == '-'
        self.inputs['R2'].enabled = self.carpaint_presets == '-'
        self.inputs['R3'].enabled = self.carpaint_presets == '-'

    # Definitions for non-socket properties
    carpaint_presets = bpy.props.EnumProperty(name='Car Paint Presets', description='Luxrender Carpaint Presets',
                                              items=carpaint_items, default='-', update=change_is_preset)

    # Definitions for sockets
    def init(self, context):
        self.inputs.new('luxrender_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('luxrender_TC_Ks1_socket', 'Specular Color 1')
        self.inputs.new('luxrender_TF_R1_socket', 'R1')
        self.inputs.new('luxrender_TF_M1_socket', 'M1')
        self.inputs.new('luxrender_TC_Ks2_socket', 'Specular Color 2')
        self.inputs.new('luxrender_TF_R2_socket', 'R2')
        self.inputs.new('luxrender_TF_M2_socket', 'M2')
        self.inputs.new('luxrender_TC_Ks3_socket', 'Specular Color 3')
        self.inputs.new('luxrender_TF_R3_socket', 'R3')
        self.inputs.new('luxrender_TF_M3_socket', 'M3')
        self.inputs.new('luxrender_TC_Ka_socket', 'Absorption Color')
        self.inputs.new('luxrender_TF_d_socket', 'Absorption Depth')
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    # Draw the non-socket properties
    def draw_buttons(self, context, layout):
        layout.prop(self, 'carpaint_presets')

    # Export routine for this node. This function stores code that LuxBlend will run when it exports materials.
    def export_material(self, make_material, make_texture):
        mat_type = 'carpaint'

        carpaint_params = ParamSet()
        # have to export the sockets, or else bump/normal mapping won't work when using a preset
        carpaint_params.update(get_socket_paramsets(self.inputs, make_texture))

        if self.carpaint_presets != '-':
            carpaint_params.add_string('name', self.carpaint_presets)

        return make_material(mat_type, self.name, carpaint_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_cloth(luxrender_material_node):
    """Cloth material node"""
    bl_idname = 'luxrender_material_cloth_node'
    bl_label = 'Cloth Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    for prop in luxrender_mat_cloth.properties:
        if prop['attr'].startswith('presetname'):
            cloth_items = prop['items']

    fabric_type = bpy.props.EnumProperty(name='Cloth Fabric', description='Luxrender Cloth Fabric', items=cloth_items,
                                         default='denim')
    repeat_u = bpy.props.FloatProperty(name='Repeat U', default=100.0)
    repeat_v = bpy.props.FloatProperty(name='Repeat V', default=100.0)


    def init(self, context):
        self.inputs.new('luxrender_TC_warp_Kd_socket', 'Warp Diffuse Color')
        self.inputs.new('luxrender_TC_warp_Ks_socket', 'Warp Specular Color')
        self.inputs.new('luxrender_TC_weft_Kd_socket', 'Weft Diffuse Color')
        self.inputs.new('luxrender_TC_weft_Ks_socket', 'Weft Specular Color')
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'fabric_type')
        layout.prop(self, 'repeat_u')
        layout.prop(self, 'repeat_v')

    def export_material(self, make_material, make_texture):
        mat_type = 'cloth'

        cloth_params = ParamSet()
        cloth_params.update(get_socket_paramsets(self.inputs, make_texture))

        cloth_params.add_string('presetname', self.fabric_type)
        cloth_params.add_float('repeat_u', self.repeat_u)
        cloth_params.add_float('repeat_v', self.repeat_v)

        return make_material(mat_type, self.name, cloth_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_doubleside(luxrender_material_node):
    """Doubel-sided material node"""
    bl_idname = 'luxrender_material_doubleside_node'
    bl_label = 'Double-Sided Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    usefrontforfront = bpy.props.BoolProperty(name='Use front for front',
                                              description='Use front side of front material for front side',
                                              default=True)
    usefrontforback = bpy.props.BoolProperty(name='Use front for back',
                                             description='Use front side of back material for back side', default=True)

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Front Material')
        self.inputs['Front Material'].name = 'Front Material'
        self.inputs.new('NodeSocketShader', 'Back Material')
        self.inputs['Back Material'].name = 'Back Material'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'usefrontforfront')
        layout.prop(self, 'usefrontforback')

    def export_material(self, make_material, make_texture):
        print('export node: doubleside')

        mat_type = 'doubleside'

        doubleside_params = ParamSet()

        def export_submat(socket):
            node = get_linked_node(socket)

            if not check_node_export_material(node):
                return None

            return node.export_material(make_material, make_texture)

        frontmat_name = export_submat(self.inputs[0])

        if self.inputs[1].is_linked:
            backmat_name = export_submat(self.inputs[1])
        else:
            backmat_name = export_submat(self.inputs[0])

        doubleside_params.add_string("frontnamedmaterial", frontmat_name)
        doubleside_params.add_string("backnamedmaterial", backmat_name)
        doubleside_params.add_bool('usefrontforfront', self.usefrontforfront)
        doubleside_params.add_bool('usefrontforback', self.usefrontforback)

        return make_material(mat_type, self.name, doubleside_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_glass(luxrender_material_node):
    """Glass material node"""
    bl_idname = 'luxrender_material_glass_node'
    bl_label = 'Glass Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    arch = bpy.props.BoolProperty(name='Architectural',
                                  description='Skips refraction during transmission, propagates alpha and shadow rays',
                                  default=False)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('luxrender_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('luxrender_TF_ior_socket', 'IOR')
        self.inputs.new('luxrender_TF_cauchyb_socket', 'Cauchy B')
        self.inputs.new('luxrender_TF_film_ior_socket', 'Film IOR')
        self.inputs.new('luxrender_TF_film_thick_socket', 'Film Thickness (nm)')
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'arch')

    def export_material(self, make_material, make_texture):
        mat_type = 'glass'

        glass_params = ParamSet()
        glass_params.update(get_socket_paramsets(self.inputs, make_texture))

        glass_params.add_bool('architectural', self.arch)

        return make_material(mat_type, self.name, glass_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_glass2(luxrender_material_node):
    """Glass2 material node"""
    bl_idname = 'luxrender_material_glass2_node'
    bl_label = 'Glass2 Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    arch = bpy.props.BoolProperty(name='Architectural',
                                  description='Skips refraction during transmission, propagates alpha and shadow rays',
                                  default=False)
    dispersion = bpy.props.BoolProperty(name='Dispersion',
                                        description='Enables chromatic dispersion, volume should have a sufficient \
                                        data for this', default=False)

    def init(self, context):
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'arch')
        layout.prop(self, 'dispersion')

    def export_material(self, make_material, make_texture):
        mat_type = 'glass2'

        glass2_params = ParamSet()

        glass2_params.add_bool('architectural', self.arch)
        glass2_params.add_bool('dispersion', self.dispersion)

        return make_material(mat_type, self.name, glass2_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_glossy(luxrender_material_node):
    """Glossy material node"""
    bl_idname = 'luxrender_material_glossy_node'
    bl_label = 'Glossy Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_use_ior(self, context):
        # # Specular/IOR representation switches
        self.inputs['Specular Color'].enabled = not self.use_ior
        self.inputs['IOR'].enabled = self.use_ior

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    multibounce = bpy.props.BoolProperty(name='Multibounce', description='Enable surface layer multibounce',
                                         default=False)
    use_ior = bpy.props.BoolProperty(name='Use IOR', description='Set specularity by IOR', default=False,
                                     update=change_use_ior)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('luxrender_TF_sigma_socket', 'Sigma')
        self.inputs.new('luxrender_TC_Ks_socket', 'Specular Color')
        self.inputs.new('luxrender_TF_ior_socket', 'IOR')
        self.inputs['IOR'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TC_Ka_socket', 'Absorption Color')
        self.inputs.new('luxrender_TF_d_socket', 'Absorption Depth (nm)')
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'multibounce')
        layout.prop(self, 'use_ior')
        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        mat_type = 'glossy'

        glossy_params = ParamSet()
        glossy_params.update(get_socket_paramsets(self.inputs, make_texture))

        glossy_params.add_bool('multibounce', self.multibounce)

        return make_material(mat_type, self.name, glossy_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_glossycoating(luxrender_material_node):
    """Glossy Coating material node"""
    bl_idname = 'luxrender_material_glossycoating_node'
    bl_label = 'Glossy Coating Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_use_ior(self, context):
        # # Specular/IOR representation switches
        self.inputs['Specular Color'].enabled = not self.use_ior
        self.inputs['IOR'].enabled = self.use_ior

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    multibounce = bpy.props.BoolProperty(name='Multibounce', description='Enable surface layer multibounce',
                                         default=False)
    use_ior = bpy.props.BoolProperty(name='Use IOR', description='Set specularity by IOR', default=False,
                                     update=change_use_ior)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Base Material')
        self.inputs.new('luxrender_TC_Ks_socket', 'Specular Color')
        self.inputs.new('luxrender_TF_ior_socket', 'IOR')
        self.inputs['IOR'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TC_Ka_socket', 'Absorption Color')
        self.inputs.new('luxrender_TF_d_socket', 'Absorption Depth (nm)')
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'multibounce')
        layout.prop(self, 'use_ior')
        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        mat_type = 'glossycoating'

        glossycoating_params = ParamSet()
        glossycoating_params.update(get_socket_paramsets(self.inputs, make_texture))

        glossycoating_params.add_bool('multibounce', self.multibounce)

        def export_submat(socket):
            node = get_linked_node(socket)

            if not check_node_export_material(node):
                return None

            return node.export_material(make_material, make_texture)

        basemat_name = export_submat(self.inputs[0])

        glossycoating_params.add_string("basematerial", basemat_name)

        return make_material(mat_type, self.name, glossycoating_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_glossytranslucent(luxrender_material_node):
    """Glossytranslucent material node"""
    bl_idname = 'luxrender_material_glossytranslucent_node'
    bl_label = 'Glossy Translucent Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_use_ior(self, context):
        # # Specular/IOR representation switches
        self.inputs['Specular Color'].enabled = not self.use_ior
        self.inputs['IOR'].enabled = self.use_ior

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    multibounce = bpy.props.BoolProperty(name='Multibounce', description='Enable surface layer multibounce',
                                         default=False)
    use_ior = bpy.props.BoolProperty(name='Use IOR', description='Set specularity by IOR', default=False,
                                     update=change_use_ior)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('luxrender_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('luxrender_TC_Ks_socket', 'Specular Color')
        self.inputs.new('luxrender_TF_ior_socket', 'IOR')
        self.inputs.new('luxrender_TC_Ka_socket', 'Absorption Color')
        self.inputs.new('luxrender_TF_d_socket', 'Absorption Depth (nm)')
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['IOR'].enabled = False  # initial state is disabled
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'multibounce')
        layout.prop(self, 'use_ior')
        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        mat_type = 'glossytranslucent'

        glossytranslucent_params = ParamSet()
        glossytranslucent_params.update(get_socket_paramsets(self.inputs, make_texture))

        glossytranslucent_params.add_bool('multibounce', self.multibounce)

        return make_material(mat_type, self.name, glossytranslucent_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_layered(luxrender_material_node):
    """Layered material node"""
    bl_idname = 'luxrender_material_layered_node'
    bl_label = 'Layered Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Material 1')
        self.inputs.new('luxrender_TF_OP1_socket', 'Opacity 1')
        self.inputs.new('NodeSocketShader', 'Material 2')
        self.inputs.new('luxrender_TF_OP2_socket', 'Opacity 2')
        self.inputs.new('NodeSocketShader', 'Material 3')
        self.inputs.new('luxrender_TF_OP3_socket', 'Opacity 3')
        self.inputs.new('NodeSocketShader', 'Material 4')
        self.inputs.new('luxrender_TF_OP4_socket', 'Opacity 4')

        self.outputs.new('NodeSocketShader', 'Surface')


    def export_material(self, make_material, make_texture):
        print('export node: layered')

        mat_type = 'layered'

        layered_params = ParamSet()
        layered_params.update(get_socket_paramsets([self.inputs[1]], make_texture))
        layered_params.update(get_socket_paramsets([self.inputs[3]], make_texture))
        layered_params.update(get_socket_paramsets([self.inputs[5]], make_texture))
        layered_params.update(get_socket_paramsets([self.inputs[7]], make_texture))

        def export_submat(socket):
            node = get_linked_node(socket)

            if not check_node_export_material(node):
                return None

            return node.export_material(make_material, make_texture)

        if self.inputs[0].is_linked:
            mat1_name = export_submat(self.inputs[0])
            layered_params.add_string("namedmaterial1", mat1_name)

        if self.inputs[2].is_linked:
            mat2_name = export_submat(self.inputs[2])
            layered_params.add_string("namedmaterial2", mat2_name)

        if self.inputs[4].is_linked:
            mat3_name = export_submat(self.inputs[4])
            layered_params.add_string("namedmaterial3", mat3_name)

        if self.inputs[6].is_linked:
            mat4_name = export_submat(self.inputs[6])
            layered_params.add_string("namedmaterial4", mat4_name)

        return make_material(mat_type, self.name, layered_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_matte(luxrender_material_node):
    """Matte material node"""
    bl_idname = 'luxrender_material_matte_node'
    bl_label = 'Matte Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('luxrender_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('luxrender_TF_sigma_socket', 'Sigma')
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    def export_material(self, make_material, make_texture):
        mat_type = 'matte'

        matte_params = ParamSet()
        matte_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, matte_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_mattetranslucent(luxrender_material_node):
    """Mattetranslucent material node"""
    bl_idname = 'luxrender_material_mattetranslucent_node'
    bl_label = 'Matte Translucent Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    energyconsrv = bpy.props.BoolProperty(name='Energy Conserving', default=True)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('luxrender_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('luxrender_TF_sigma_socket', 'Sigma')
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    def export_material(self, make_material, make_texture):
        mat_type = 'mattetranslucent'

        mattetranslucent_params = ParamSet()
        mattetranslucent_params.update(get_socket_paramsets(self.inputs, make_texture))
        mattetranslucent_params.add_bool('energyconserving', self.energyconsrv)

        return make_material(mat_type, self.name, mattetranslucent_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_metal(luxrender_material_node):
    """Metal material node"""
    bl_idname = 'luxrender_material_metal_node'
    bl_label = 'Metal Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    for prop in luxrender_mat_metal.properties:
        if prop['attr'].startswith('name'):
            metal_presets = prop['items']

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    metal_preset = bpy.props.EnumProperty(name='Preset', description='Luxrender Metal Preset', items=metal_presets,
                                          default='aluminium')

    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic roughness',
                                            default=False, update=change_use_anisotropy)
    metal_nkfile = bpy.props.StringProperty(name='Nk File', description='Nk file path', subtype='FILE_PATH')

    def init(self, context):
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'metal_preset')

        if self.metal_preset == 'nk':
            layout.prop(self, 'metal_nkfile')

        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        print('export node: metal')

        mat_type = 'metal'

        metal_params = ParamSet()
        metal_params.update(get_socket_paramsets(self.inputs, make_texture))

        if self.metal_preset == 'nk':  # use an NK data file
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(LuxManager.CurrentScene, self, self.metal_nkfile, metal_params, 'filename')
        else:
            # use a preset name
            metal_params.add_string('name', self.metal_preset)

        return make_material(mat_type, self.name, metal_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_metal2(luxrender_material_node):
    """Metal2 material node"""
    bl_idname = 'luxrender_material_metal2_node'
    bl_label = 'Metal2 Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    for prop in luxrender_mat_metal2.properties:
        if prop['attr'].startswith('metaltype'):
            metal2_types = prop['items']

    for prop in luxrender_mat_metal2.properties:
        if prop['attr'].startswith('preset'):
            metal2_presets = prop['items']

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

        # metal2_type = bpy.props.EnumProperty(name='Type', description='Luxrender Metal2 Type', items=metal2_types, default='preset')

    # metal2_preset = bpy.props.EnumProperty(name='Preset', description='Luxrender Metal2 Preset', items=metal2_presets, default='aluminium')
    # metal2_nkfile = bpy.props.StringProperty(name='Nk File', description='Nk file path', subtype='FILE_PATH')

    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('luxrender_fresnel_socket', 'IOR')
        self.inputs['IOR'].needs_link = True  # suppress inappropiate chooser
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        # layout.prop(self, 'metal2_type')
        # if self.metal2_type == 'preset':
        # layout.prop(self, 'metal2_preset')
        # if self.metal2_type == 'nk':
        # layout.prop(self, 'metal2_nkfile')
        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        mat_type = 'metal2'

        metal2_params = ParamSet()
        metal2_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, metal2_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_mirror(luxrender_material_node):
    """Mirror material node"""
    bl_idname = 'luxrender_material_mirror_node'
    bl_label = 'Mirror Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def init(self, context):
        self.inputs.new('luxrender_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('luxrender_TF_film_ior_socket', 'Film IOR')
        self.inputs.new('luxrender_TF_film_thick_socket', 'Film Thickness (nm)')
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    def export_material(self, make_material, make_texture):
        mat_type = 'mirror'

        mirror_params = ParamSet()
        mirror_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, mirror_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_mix(luxrender_material_node):
    """Mix material node"""
    bl_idname = 'luxrender_material_mix_node'
    bl_label = 'Mix Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def init(self, context):
        self.inputs.new('luxrender_TF_amount_socket', 'Mix Amount')
        self.inputs.new('NodeSocketShader', 'Material 1')
        self.inputs.new('NodeSocketShader', 'Material 2')

        self.outputs.new('NodeSocketShader', 'Surface')

    def export_material(self, make_material, make_texture):
        print('export node: mix')

        mat_type = 'mix'

        mix_params = ParamSet()
        mix_params.update(get_socket_paramsets([self.inputs[0]], make_texture))

        def export_submat(socket):
            node = get_linked_node(socket)

            if not check_node_export_material(node):
                return None

            return node.export_material(make_material, make_texture)

        mat1_name = export_submat(self.inputs[1])
        mat2_name = export_submat(self.inputs[2])

        mix_params.add_string("namedmaterial1", mat1_name)
        mix_params.add_string("namedmaterial2", mat2_name)

        return make_material(mat_type, self.name, mix_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_null(luxrender_material_node):
    """Null material node"""
    bl_idname = 'luxrender_material_null_node'
    bl_label = 'Null Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Surface')

    def export_material(self, make_material, make_texture):
        mat_type = 'null'

        null_params = ParamSet()

        return make_material(mat_type, self.name, null_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_roughglass(luxrender_material_node):
    """Rough Glass material node"""
    bl_idname = 'luxrender_material_roughglass_node'
    bl_label = 'Rough Glass Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)
    dispersion = bpy.props.BoolProperty(name='Dispersion',
                                        description='Enables chromatic dispersion, Cauchy B value should be none-zero',
                                        default=False)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('luxrender_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('luxrender_TF_ior_socket', 'IOR')
        self.inputs.new('luxrender_TF_cauchyb_socket', 'Cauchy B')
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_anisotropy')
        layout.prop(self, 'dispersion')

    def export_material(self, make_material, make_texture):
        mat_type = 'roughglass'

        roughglass_params = ParamSet()
        roughglass_params.update(get_socket_paramsets(self.inputs, make_texture))

        roughglass_params.add_bool('dispersion', self.dispersion)

        return make_material(mat_type, self.name, roughglass_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_scatter(luxrender_material_node):
    """Scatter material node"""
    bl_idname = 'luxrender_material_scatter_node'
    bl_label = 'Scatter Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('luxrender_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('luxrender_SC_asymmetry_socket', 'Asymmetry')

        self.outputs.new('NodeSocketShader', 'Surface')

    def export_material(self, make_material, make_texture):
        mat_type = 'scatter'

        scatter_params = ParamSet()
        scatter_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, scatter_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_shinymetal(luxrender_material_node):
    """Shiny metal material node"""
    bl_idname = 'luxrender_material_shinymetal_node'
    bl_label = 'Shiny Metal Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('luxrender_TC_Ks_socket', 'Specular Color')
        self.inputs.new('luxrender_TF_film_ior_socket', 'Film IOR')
        self.inputs.new('luxrender_TF_film_thick_socket', 'Film Thickness (nm)')
        self.inputs.new('luxrender_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('luxrender_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('luxrender_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        mat_type = 'shinymetal'

        shinymetal_params = ParamSet()
        shinymetal_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, shinymetal_params)


@LuxRenderAddon.addon_register_class
class luxrender_material_type_node_velvet(luxrender_material_node):
    """Velvet material node"""
    bl_idname = 'luxrender_material_velvet_node'
    bl_label = 'Velvet Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    advanced = bpy.props.BoolProperty(name='Advanced', description='Advanced Velvet Parameters', default=False)
    thickness = bpy.props.FloatProperty(name='Thickness', description='', default=0.1, subtype='NONE', min=-0.0,
                                        max=1.0, soft_min=-0.0, soft_max=1.0, precision=2)
    p1 = bpy.props.FloatProperty(name='p1', description='', default=-2.0, subtype='NONE', min=-100.0, max=100.0,
                                 soft_min=-100.0, soft_max=100.0, precision=2)
    p2 = bpy.props.FloatProperty(name='p2', description='', default=-10.0, subtype='NONE', min=-100.0, max=100.0,
                                 soft_min=-100.0, soft_max=100.0, precision=2)
    p3 = bpy.props.FloatProperty(name='p2', description='', default=-2.0, subtype='NONE', min=-100.0, max=100.0,
                                 soft_min=-100.0, soft_max=100.0, precision=2)

    def init(self, context):
        self.inputs.new('luxrender_TC_Kd_socket', 'Diffuse Color')

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'advanced')
        layout.prop(self, 'thickness')

        if self.advanced:
            layout.prop(self, 'p1')
            layout.prop(self, 'p2')
            layout.prop(self, 'p3')

    def export_material(self, make_material, make_texture):
        mat_type = 'velvet'

        velvet_params = ParamSet()
        velvet_params.update(get_socket_paramsets(self.inputs, make_texture))

        velvet_params.add_float('thickness', self.thickness)
        velvet_params.add_float('p1', self.p1)
        velvet_params.add_float('p2', self.p2)
        velvet_params.add_float('p3', self.p3)

        return make_material(mat_type, self.name, velvet_params)


@LuxRenderAddon.addon_register_class
class luxrender_volume_type_node_clear(luxrender_material_node):
    """Clear volume node"""
    bl_idname = 'luxrender_volume_clear_node'
    bl_label = 'Clear Volume'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('luxrender_fresnel_socket', 'IOR')
        self.inputs.new('luxrender_AC_absorption_socket', 'Absorption Color')

        self.outputs.new('NodeSocketShader', 'Volume')

    def export_volume(self, make_volume, make_texture):
        vol_type = 'clear'

        clear_params = ParamSet()
        clear_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_volume(self.name, vol_type, clear_params)


@LuxRenderAddon.addon_register_class
class luxrender_volume_type_node_homogeneous(luxrender_material_node):
    '''Homogeneous volume node'''
    bl_idname = 'luxrender_volume_homogeneous_node'
    bl_label = 'Homogeneous Volume'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('luxrender_fresnel_socket', 'IOR')
        self.inputs.new('luxrender_SC_absorption_socket', 'Absorption Color')
        self.inputs.new('luxrender_SC_color_socket', 'Scattering Color')
        self.inputs.new('luxrender_SC_asymmetry_socket', 'Asymmetry')

        self.outputs.new('NodeSocketShader', 'Volume')

    def export_volume(self, make_volume, make_texture):
        vol_type = 'homogeneous'

        homogeneous_params = ParamSet()
        homogeneous_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_volume(self.name, vol_type, homogeneous_params)


@LuxRenderAddon.addon_register_class
class luxrender_volume_type_node_heterogeneous(luxrender_material_node):
    """Heterogeneous volume node"""
    bl_idname = 'luxrender_volume_heterogeneous_node'
    bl_label = 'Heterogeneous Volume'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    stepsize = bpy.props.FloatProperty(name='Step Size', default=1.0, min=0.0, max=100.0, subtype='DISTANCE',
                                       unit='LENGTH', description='Length of ray marching steps, smaller values \
                                       resolve more detail, but are slower')

    def init(self, context):
        self.inputs.new('luxrender_fresnel_socket', 'IOR')
        self.inputs.new('luxrender_SC_absorption_socket', 'Absorption Color')
        self.inputs.new('luxrender_SC_color_socket', 'Scattering Color')
        self.inputs.new('luxrender_SC_asymmetry_socket', 'Asymmetry')

        self.outputs.new('NodeSocketShader', 'Volume')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'stepsize')

    def export_volume(self, make_volume, make_texture):
        vol_type = 'heterogeneous'

        heterogeneous_params = ParamSet()
        heterogeneous_params.update(get_socket_paramsets(self.inputs, make_texture))
        heterogeneous_params.add_float('stepsize', self.stepsize)

        return make_volume(self.name, vol_type, heterogeneous_params)


@LuxRenderAddon.addon_register_class
class luxrender_light_area_node(luxrender_material_node):
    """Area Light node"""
    bl_idname = 'luxrender_light_area_node'
    bl_label = 'Area Light'
    bl_icon = 'LAMP'
    bl_width_min = 160

    gain = bpy.props.FloatProperty(name='Gain', default=1.0, min=0.0, description='Scaling factor for light intensity')
    power = bpy.props.FloatProperty(name='Power (W)', default=100.0, min=0.0)
    efficacy = bpy.props.FloatProperty(name='Efficacy (lm/W)', default=17.0, min=0.0)
    iesname = bpy.props.StringProperty(name='IES Data', description='IES file path', subtype='FILE_PATH')
    importance = bpy.props.FloatProperty(name='Importance', default=1.0, min=0.0,
                                         description='Shadow ray and light path sampling weight')
    nsamples = bpy.props.IntProperty(name='Shadow Ray Count', default=1, min=1, max=64,
                                     description='Number of shadow samples per intersection')

    def init(self, context):
        self.inputs.new('luxrender_TC_L_socket', 'Light Color')

        self.outputs.new('NodeSocketShader', 'Emission')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'gain')
        layout.prop(self, 'power')
        layout.prop(self, 'efficacy')
        layout.prop(self, 'iesname')
        layout.prop(self, 'importance')
        layout.prop(self, 'nsamples')

    def export(self, make_texture):
        arealight_params = ParamSet()
        arealight_params.update(get_socket_paramsets(self.inputs, make_texture))
        arealight_params.add_float('gain', self.gain)
        arealight_params.add_float('power', self.power)
        arealight_params.add_float('efficacy', self.efficacy)

        if self.iesname:
            process_filepath_data(LuxManager.CurrentScene, self, self.iesname, arealight_params, 'iesname')

        arealight_params.add_float('importance', self.importance)
        arealight_params.add_integer('nsamples', self.nsamples)

        return 'area', arealight_params


@LuxRenderAddon.addon_register_class
class luxrender_material_output_node(luxrender_node):
    """Material output node"""
    bl_idname = 'luxrender_material_output_node'
    bl_label = 'Material Output'
    bl_icon = 'MATERIAL'
    bl_width_min = 120

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Surface')
        self.inputs.new('NodeSocketShader', 'Interior Volume')
        self.inputs.new('NodeSocketShader', 'Exterior Volume')
        self.inputs.new('NodeSocketShader', 'Emission')

    def export(self, scene, lux_context, material, mode='indirect'):

        print('Exporting node tree, mode: %s' % mode)

        surface_socket = self.inputs[0]  # perhaps by name?
        if not surface_socket.is_linked:
            return set()

        surface_node = surface_socket.links[0].from_node

        tree_name = material.luxrender_material.nodetree

        make_material = None
        if mode == 'indirect':
            # named material exporting
            def make_material_indirect(mat_type, mat_name, mat_params):
                nonlocal lux_context
                nonlocal surface_node
                nonlocal material

                if mat_name != surface_node.name:
                    material_name = '%s::%s' % (tree_name, mat_name)
                else:
                    # this is the root material, don't alter name
                    material_name = material.name

                print('Exporting material "%s", type: "%s", name: "%s"' % (material_name, mat_type, mat_name))
                mat_params.add_string('type', mat_type)

                # DistributedPath compositing. Don't forget these!
                if scene.luxrender_integrator.surfaceintegrator == 'distributedpath':
                    mat_params.update(material.luxrender_material.luxrender_mat_compositing.get_paramset())

                ExportedMaterials.makeNamedMaterial(lux_context, material_name, mat_params)
                ExportedMaterials.export_new_named(lux_context)

                return material_name

            make_material = make_material_indirect
        elif mode == 'direct':
            # direct material exporting
            def make_material_direct(mat_type, mat_name, mat_params):
                nonlocal lux_context
                lux_context.material(mat_type, mat_params)

                if mat_name != surface_node.name:
                    material_name = '%s::%s' % (tree_name, mat_name)
                else:
                    # this is the root material, don't alter name
                    material_name = material.name

                print('Exporting material "%s", type: "%s", name: "%s"' % (material_name, mat_type, mat_name))
                mat_params.add_string('type', mat_type)

                # DistributedPath compositing. Don't forget these!
                if scene.luxrender_integrator.surfaceintegrator == 'distributedpath':
                    mat_params.update(material.luxrender_material.luxrender_mat_compositing.get_paramset())

                ExportedMaterials.makeNamedMaterial(lux_context, material_name, mat_params)
                ExportedMaterials.export_new_named(lux_context)

                return material_name

            make_material = make_material_direct


        # texture exporting, only one way
        make_texture = luxrender_texture_maker(lux_context, tree_name).make_texture

        # start exporting that material...
        with MaterialCounter(material.name):
            if not (mode == 'indirect' and material.name in ExportedMaterials.exported_material_names):
                if check_node_export_material(surface_node):
                    surface_node.export_material(make_material=make_material, make_texture=make_texture)

        # Volumes exporting:
        int_vol_socket = self.inputs[1]
        if int_vol_socket.is_linked:
            int_vol_node = int_vol_socket.links[0].from_node

        ext_vol_socket = self.inputs[2]
        if ext_vol_socket.is_linked:
            ext_vol_node = ext_vol_socket.links[0].from_node

        def make_volume(vol_name, vol_type, vol_params):
            nonlocal lux_context
            vol_name = '%s::%s' % (tree_name, vol_name)
            volume_name = vol_name

            # # Here we look for redundant volume definitions caused by material used more than once
            if mode == 'indirect':
                if vol_name not in ExportedVolumes.vol_names:  # was not yet exported
                    print('Exporting volume, type: "%s", name: "%s"' % (vol_type, vol_name))
                    lux_context.makeNamedVolume(vol_name, vol_type, vol_params)
                    ExportedVolumes.list_exported_volumes(vol_name)  # mark as exported
            else:  # direct
                lux_context.makeNamedVolume(vol_name, vol_type, vol_params)

            return volume_name

        if int_vol_socket.is_linked:
            int_vol_node.export_volume(make_volume=make_volume, make_texture=make_texture)

        if ext_vol_socket.is_linked:
            ext_vol_node.export_volume(make_volume=make_volume, make_texture=make_texture)

        return set()
