# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Jens Verwiebe, Jason Clarke, Asbjørn Heid, Simon Wendsche
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

import bpy, os, math

from . import (create_luxcore_name_mat, create_luxcore_name, warning_classic_node, has_interior_volume,
               export_submat_luxcore, export_emission_luxcore)
from ..export.luxcore.utils import get_elem_key, is_lightgroup_opencl_compatible
from ..export.materials import TextureCounter
from ..export import get_expanded_file_name

from ..outputs.luxcore_api import set_prop_mat, set_prop_vol, set_prop_tex

from ..properties import (pbrtv3_node, pbrtv3_material_node, check_node_export_material)
from ..properties.node_sockets import *


class pbrtv3_texture_maker:
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


def add_common_sockets(node):
    """
    Add sockets shared by all material nodes
    """
    node.inputs.new('pbrtv3_TF_bump_socket', 'Bump')
    # PBRTv3Core only transparency property
    node.inputs.new('pbrtv3_transparency_socket', 'Opacity')

    node.outputs.new('NodeSocketShader', 'Surface')

def export_common_sockets(node, properties):
    """
    Call this function in export_luxcore() before setting any properties
    """
    bump = node.inputs['Bump'].export_luxcore(properties) # may be None!

    if 'Opacity' in node.inputs: # Compatibility with old node setups
        transparency = node.inputs['Opacity'].export_luxcore(properties)
    else:
        transparency = 1.0

    return bump, transparency

def set_common_properties(properties, luxcore_name, bump, transparency):
    """
    Call this function in export_luxcore() after setting the properties
    """
    if bump:
        set_prop_mat(properties, luxcore_name, 'bumptex', bump)
        
    if transparency != 1.0:
        set_prop_mat(properties, luxcore_name, 'transparency', transparency)


# Material nodes alphabetical
@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_carpaint(pbrtv3_material_node):
    # Description string
    """Car paint material node"""
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'pbrtv3_material_carpaint_node'
    # Label for nice name display
    bl_label = 'Car Paint Material'
    # Icon identifier
    bl_icon = 'MATERIAL'
    bl_width_min = 200

    # Get menu items from old material editor properties
    for prop in pbrtv3_mat_carpaint.properties:
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
        self.inputs.new('pbrtv3_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('pbrtv3_TC_Ks1_socket', 'Specular Color 1')
        self.inputs.new('pbrtv3_TF_R1_socket', 'R1')
        self.inputs.new('pbrtv3_TF_M1_socket', 'M1')
        self.inputs.new('pbrtv3_TC_Ks2_socket', 'Specular Color 2')
        self.inputs.new('pbrtv3_TF_R2_socket', 'R2')
        self.inputs.new('pbrtv3_TF_M2_socket', 'M2')
        self.inputs.new('pbrtv3_TC_Ks3_socket', 'Specular Color 3')
        self.inputs.new('pbrtv3_TF_R3_socket', 'R3')
        self.inputs.new('pbrtv3_TF_M3_socket', 'M3')
        self.inputs.new('pbrtv3_TC_Ka_socket', 'Absorption Color')
        self.inputs.new('pbrtv3_TF_d_socket', 'Absorption Depth')

        add_common_sockets(self)

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

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kd = self.inputs['Diffuse Color'].export_luxcore(properties)
        ks1 = self.inputs['Specular Color 1'].export_luxcore(properties)
        r1 = self.inputs['R1'].export_luxcore(properties)
        m1 = self.inputs['M1'].export_luxcore(properties)
        ks2 = self.inputs['Specular Color 2'].export_luxcore(properties)
        r2 = self.inputs['R2'].export_luxcore(properties)
        m2 = self.inputs['M2'].export_luxcore(properties)
        ks3 = self.inputs['Specular Color 3'].export_luxcore(properties)
        r3 = self.inputs['R3'].export_luxcore(properties)
        m3 = self.inputs['M3'].export_luxcore(properties)

        ka = self.inputs['Absorption Color'].export_luxcore(properties)
        d = self.inputs['Absorption Depth'].export_luxcore(properties)

        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'carpaint')

        if self.carpaint_presets == '-':
            # Manual settings
            set_prop_mat(properties, luxcore_name, 'kd', kd)
            set_prop_mat(properties, luxcore_name, 'ks1', ks1)
            set_prop_mat(properties, luxcore_name, 'ks2', ks2)
            set_prop_mat(properties, luxcore_name, 'ks3', ks3)
            set_prop_mat(properties, luxcore_name, 'm1', m1)
            set_prop_mat(properties, luxcore_name, 'm2', m2)
            set_prop_mat(properties, luxcore_name, 'm3', m3)
            set_prop_mat(properties, luxcore_name, 'r1', r1)
            set_prop_mat(properties, luxcore_name, 'r2', r2)
            set_prop_mat(properties, luxcore_name, 'r3', r3)
            set_prop_mat(properties, luxcore_name, 'ka', ka)
            set_prop_mat(properties, luxcore_name, 'd', d)
        else:
            # Preset
            set_prop_mat(properties, luxcore_name, 'preset', self.carpaint_presets)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_cloth(pbrtv3_material_node):
    """Cloth material node"""
    bl_idname = 'pbrtv3_material_cloth_node'
    bl_label = 'Cloth Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    for prop in pbrtv3_mat_cloth.properties:
        if prop['attr'].startswith('presetname'):
            cloth_items = prop['items']

    fabric_type = bpy.props.EnumProperty(name='Cloth Fabric', description='Luxrender Cloth Fabric', items=cloth_items,
                                         default='denim')
    repeat_u = bpy.props.FloatProperty(name='Repeat U', default=100.0)
    repeat_v = bpy.props.FloatProperty(name='Repeat V', default=100.0)


    def init(self, context):
        self.inputs.new('pbrtv3_TC_warp_Kd_socket', 'Warp Diffuse Color')
        self.inputs.new('pbrtv3_TC_warp_Ks_socket', 'Warp Specular Color')
        self.inputs.new('pbrtv3_TC_weft_Kd_socket', 'Weft Diffuse Color')
        self.inputs.new('pbrtv3_TC_weft_Ks_socket', 'Weft Specular Color')

        add_common_sockets(self)

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

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        warp_kd = self.inputs['Warp Diffuse Color'].export_luxcore(properties)
        warp_ks = self.inputs['Warp Specular Color'].export_luxcore(properties)
        weft_kd = self.inputs['Weft Diffuse Color'].export_luxcore(properties)
        weft_ks = self.inputs['Weft Specular Color'].export_luxcore(properties)
        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'cloth')
        set_prop_mat(properties, luxcore_name, 'preset', self.fabric_type)
        set_prop_mat(properties, luxcore_name, 'warp_kd', warp_kd)
        set_prop_mat(properties, luxcore_name, 'warp_ks', warp_ks)
        set_prop_mat(properties, luxcore_name, 'weft_kd', weft_kd)
        set_prop_mat(properties, luxcore_name, 'weft_ks', weft_ks)
        set_prop_mat(properties, luxcore_name, 'repeat_u', self.repeat_u)
        set_prop_mat(properties, luxcore_name, 'repeat_v', self.repeat_v)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_doubleside(pbrtv3_material_node):
    """Doubel-sided material node"""
    bl_idname = 'pbrtv3_material_doubleside_node'
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
        warning_classic_node(layout)

        layout.prop(self, 'usefrontforfront')
        layout.prop(self, 'usefrontforback')

    def export_material(self, make_material, make_texture):
        print('export node: doubleside')

        mat_type = 'doubleside'

        doubleside_params = ParamSet()

        def export_submat(socket):
            node = get_linked_node(socket)

            if node is None or not check_node_export_material(node):
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

    # TODO: add PBRTv3Core support once supported by PBRTv3Core


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_glass(pbrtv3_material_node):
    """Glass material node"""
    bl_idname = 'pbrtv3_material_glass_node'
    bl_label = 'Glass Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_advanced(self, context):
        self.inputs['Cauchy B'].enabled = self.advanced and self.dispersion # is also disabled/enabled by dispersion
        self.inputs['Film IOR'].enabled = self.advanced
        self.inputs['Film Thickness (nm)'].enabled = self.advanced

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    def change_dispersion(self, context):
        self.inputs['Cauchy B'].enabled = self.advanced and self.dispersion

    def change_rough(self, context):
        if self.use_anisotropy:
            self.inputs['U-Roughness'].enabled = self.rough
            self.inputs['V-Roughness'].enabled = self.rough
        else:
            self.inputs['Roughness'].enabled = self.rough

    def change_use_volume_ior(self, context):
        self.inputs['IOR'].enabled = not self.use_volume_ior

    advanced = bpy.props.BoolProperty(name='Advanced Options', description='Configure advanced options',
                                      default=False, update=change_advanced)
    architectural = bpy.props.BoolProperty(name='Architectural',
                                  description='Skips refraction during transmission, propagates alpha and shadow rays',
                                  default=False)
    rough = bpy.props.BoolProperty(name='Rough',
                                  description='Rough glass surface instead of a smooth one',
                                  default=False, update=change_rough)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic', description='Anisotropic Roughness, distorts the reflec'
                                                                            'tions (object has to be UV-unwrapped)',
                                            default=False, update=change_use_anisotropy)
    dispersion = bpy.props.BoolProperty(name='Dispersion',
                                        description='Enables chromatic dispersion, Cauchy B value should be none-zero',
                                        default=False, update=change_dispersion)
    use_volume_ior = bpy.props.BoolProperty(name='Use Volume IOR',
                                        description='Use the IOR setting of the interior volume (only works if an '
                                            'interior volume is set on the material output node)',
                                        default=False, update=change_use_volume_ior)

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('pbrtv3_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('pbrtv3_TF_ior_socket', 'IOR')

        # advanced options
        self.inputs.new('pbrtv3_TF_cauchyb_socket', 'Cauchy B')
        self.inputs['Cauchy B'].enabled = False
        self.inputs.new('pbrtv3_TF_film_ior_socket', 'Film IOR')
        self.inputs['Film IOR'].enabled = False
        self.inputs.new('pbrtv3_TF_film_thick_socket', 'Film Thickness (nm)')
        self.inputs['Film Thickness (nm)'].enabled = False

        # Rough options
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs['U-Roughness'].name = 'Roughness'
        self.inputs['Roughness'].enabled = False
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False

        add_common_sockets(self)

    def draw_buttons(self, context, layout):
        column = layout.row()
        column.enabled = not self.architectural
        column.prop(self, 'rough')

        if self.rough:
            column.prop(self, 'use_anisotropy')

        # Rough glass cannot be archglass
        row = layout.row()
        row.enabled = not self.rough
        row.prop(self, 'architectural')

        row = layout.row()
        row.enabled = has_interior_volume(self)
        row.prop(self, 'use_volume_ior')

        # None of the advanced options work in PBRTv3Core
        if not UsePBRTv3Core():
            layout.prop(self, 'advanced', toggle=True)

            if self.advanced:
                layout.prop(self, 'dispersion')

    def export_material(self, make_material, make_texture):
        if self.rough:
            # Export as roughglass
            mat_type = 'roughglass'

            roughglass_params = ParamSet()
            roughglass_params.update(get_socket_paramsets(self.inputs, make_texture))

            roughglass_params.add_bool('dispersion', self.dispersion)

            return make_material(mat_type, self.name, roughglass_params)
        elif has_interior_volume(self) and self.use_volume_ior:
            # Export as glass2
            mat_type = 'glass2'

            glass2_params = ParamSet()

            glass2_params.add_bool('architectural', self.architectural)
            glass2_params.add_bool('dispersion', self.dispersion)

            return make_material(mat_type, self.name, glass2_params)
        else:
            # Export as glass
            mat_type = 'glass'

            glass_params = ParamSet()
            glass_params.update(get_socket_paramsets(self.inputs, make_texture))

            glass_params.add_bool('architectural', self.architectural)

            return make_material(mat_type, self.name, glass_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        if self.rough:
            type = 'roughglass'
        elif self.architectural:
            type = 'archglass'
        else:
            type = 'glass'

        kt = self.inputs['Transmission Color'].export_luxcore(properties)
        kr = self.inputs['Reflection Color'].export_luxcore(properties)
        ior = self.inputs['IOR'].export_luxcore(properties)

        if self.use_anisotropy:
            u_roughness = self.inputs['U-Roughness'].export_luxcore(properties)
            v_roughness = self.inputs['V-Roughness'].export_luxcore(properties)
        else:
            u_roughness = v_roughness = self.inputs['Roughness'].export_luxcore(properties)

        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', type)
        set_prop_mat(properties, luxcore_name, 'kr', kr)
        set_prop_mat(properties, luxcore_name, 'kt', kt)

        if not (has_interior_volume(self) and self.use_volume_ior):
            set_prop_mat(properties, luxcore_name, 'interiorior', ior)

        if self.rough:
            set_prop_mat(properties, luxcore_name, 'uroughness', u_roughness)
            set_prop_mat(properties, luxcore_name, 'vroughness', v_roughness)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


# Deprecated, replaced by unified glass node
@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_glass2(pbrtv3_material_node):
    """Glass2 material node"""
    bl_idname = 'pbrtv3_material_glass2_node'
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
        self.inputs.new('pbrtv3_TF_bump_socket', 'Bump')

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

        layout.prop(self, 'arch')
        layout.prop(self, 'dispersion')

    def export_material(self, make_material, make_texture):
        mat_type = 'glass2'

        glass2_params = ParamSet()

        glass2_params.add_bool('architectural', self.arch)
        glass2_params.add_bool('dispersion', self.dispersion)

        return make_material(mat_type, self.name, glass2_params)


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_glossy(pbrtv3_material_node):
    """Glossy material node"""
    bl_idname = 'pbrtv3_material_glossy_node'
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

    def change_advanced(self, context):
        self.inputs['IOR'].enabled = self.advanced and self.use_ior
        self.inputs['Absorption Color'].enabled = self.advanced
        self.inputs['Absorption Depth (nm)'].enabled = self.advanced

    advanced = bpy.props.BoolProperty(name='Advanced Options', description='Configure advanced options',
                                         default=False, update=change_advanced)
    multibounce = bpy.props.BoolProperty(name='Multibounce', description='Enable surface layer multibounce',
                                         default=False)
    use_ior = bpy.props.BoolProperty(name='Use IOR', description='Set specularity by IOR', default=False,
                                     update=change_use_ior)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('pbrtv3_TF_sigma_socket', 'Sigma')
        if UsePBRTv3Core():
            self.inputs['Sigma'].enabled = False # not supported by PBRTv3Core
        self.inputs.new('pbrtv3_TC_Ks_socket', 'Specular Color')
        self.inputs.new('pbrtv3_TF_ior_socket', 'IOR')
        self.inputs['IOR'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TC_Ka_socket', 'Absorption Color')
        self.inputs['Absorption Color'].enabled = False
        self.inputs.new('pbrtv3_TF_d_socket', 'Absorption Depth (nm)')
        self.inputs['Absorption Depth (nm)'].enabled = False
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs['U-Roughness'].name = 'Roughness'

        add_common_sockets(self)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_anisotropy')
        layout.prop(self, 'advanced', toggle=True)

        if self.advanced:
            layout.prop(self, 'multibounce')
            layout.prop(self, 'use_ior')

    def export_material(self, make_material, make_texture):
        mat_type = 'glossy'

        glossy_params = ParamSet()
        glossy_params.update(get_socket_paramsets(self.inputs, make_texture))

        glossy_params.add_bool('multibounce', self.multibounce)

        return make_material(mat_type, self.name, glossy_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kd = self.inputs['Diffuse Color'].export_luxcore(properties)
        ks = self.inputs['Specular Color'].export_luxcore(properties)
        u_roughness = self.inputs[6].export_luxcore(properties)
        v_roughness = self.inputs[7].export_luxcore(properties) if self.use_anisotropy else u_roughness
        ka = self.inputs['Absorption Color'].export_luxcore(properties)
        d = self.inputs['Absorption Depth (nm)'].export_luxcore(properties)
        index = self.inputs['IOR'].export_luxcore(properties)
        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'glossy2')
        set_prop_mat(properties, luxcore_name, 'kd', kd)
        set_prop_mat(properties, luxcore_name, 'ks', ks)
        set_prop_mat(properties, luxcore_name, 'uroughness', u_roughness)
        set_prop_mat(properties, luxcore_name, 'vroughness', v_roughness)
        set_prop_mat(properties, luxcore_name, 'ka', ka)
        set_prop_mat(properties, luxcore_name, 'd', d)
        set_prop_mat(properties, luxcore_name, 'multibounce', self.multibounce)

        if self.use_ior:
            set_prop_mat(properties, luxcore_name, 'index', index)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_glossycoating(pbrtv3_material_node):
    """Glossy Coating material node"""
    bl_idname = 'pbrtv3_material_glossycoating_node'
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

    def change_advanced(self, context):
        self.inputs['IOR'].enabled = self.advanced and self.use_ior
        self.inputs['Absorption Color'].enabled = self.advanced
        self.inputs['Absorption Depth (nm)'].enabled = self.advanced

    advanced = bpy.props.BoolProperty(name='Advanced Options', description='Configure advanced options',
                                         default=False, update=change_advanced)
    multibounce = bpy.props.BoolProperty(name='Multibounce', description='Creates a fuzzy, dusty appearance',
                                         default=False)
    use_ior = bpy.props.BoolProperty(name='Use IOR', description='Set specularity by IOR instead of specular color',
                                     default=False, update=change_use_ior)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Base Material')
        self.inputs.new('pbrtv3_TC_Ks_socket', 'Specular Color')
        self.inputs.new('pbrtv3_TF_ior_socket', 'IOR')
        self.inputs['IOR'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TC_Ka_socket', 'Absorption Color')
        self.inputs['Absorption Color'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_d_socket', 'Absorption Depth (nm)')
        self.inputs['Absorption Depth (nm)'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs['U-Roughness'].name = 'Roughness'
        self.inputs.new('pbrtv3_TF_bump_socket', 'Bump')
        # Note: glossycoating does not support the .transparency attribute, thus no add_common_properties() call

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_anisotropy')
        layout.prop(self, 'advanced', toggle=True)

        if self.advanced:
            layout.prop(self, 'multibounce')
            layout.prop(self, 'use_ior')

        if not self.inputs['Base Material'].is_linked:
            icon = 'INFO' if UsePBRTv3Core() else 'ERROR' # In classic API, glossycoating will not export without base
            layout.label('Select a base material!', icon=icon)

    def export_material(self, make_material, make_texture):
        mat_type = 'glossycoating'

        glossycoating_params = ParamSet()
        glossycoating_params.update(get_socket_paramsets(self.inputs, make_texture))

        glossycoating_params.add_bool('multibounce', self.multibounce)

        def export_submat(socket):
            node = get_linked_node(socket)

            if node is None or not check_node_export_material(node):
                return None

            return node.export_material(make_material, make_texture)

        basemat_name = export_submat(self.inputs[0])

        glossycoating_params.add_string("basematerial", basemat_name)

        return make_material(mat_type, self.name, glossycoating_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        base = export_submat_luxcore(properties, self.inputs['Base Material'], luxcore_exporter)
        ks = self.inputs['Specular Color'].export_luxcore(properties)
        u_roughness = self.inputs[5].export_luxcore(properties)
        v_roughness = self.inputs[6].export_luxcore(properties) if self.use_anisotropy else u_roughness
        ka = self.inputs['Absorption Color'].export_luxcore(properties)
        d = self.inputs['Absorption Depth (nm)'].export_luxcore(properties)
        index = self.inputs['IOR'].export_luxcore(properties)
        bump = self.inputs['Bump'].export_luxcore(properties) # May be None

        set_prop_mat(properties, luxcore_name, 'type', 'glossycoating')
        set_prop_mat(properties, luxcore_name, 'base', base)
        set_prop_mat(properties, luxcore_name, 'ks', ks)
        set_prop_mat(properties, luxcore_name, 'uroughness', u_roughness)
        set_prop_mat(properties, luxcore_name, 'vroughness', v_roughness)
        set_prop_mat(properties, luxcore_name, 'ka', ka)
        set_prop_mat(properties, luxcore_name, 'd', d)
        set_prop_mat(properties, luxcore_name, 'multibounce', self.multibounce)

        if self.use_ior:
            set_prop_mat(properties, luxcore_name, 'index', index)

        if bump:
            set_prop_mat(properties, luxcore_name, 'bumptex', bump)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_glossytranslucent(pbrtv3_material_node):
    """Glossytranslucent material node"""
    bl_idname = 'pbrtv3_material_glossytranslucent_node'
    bl_label = 'Glossy Translucent Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def change_advanced(self, context):
        # Hide frontface inputs
        self.inputs['IOR'].enabled = self.advanced and self.use_ior
        self.inputs['Absorption Color'].enabled = self.advanced
        self.inputs['Absorption Depth (nm)'].enabled = self.advanced

        # Hide backface inputs
        self.inputs['BF IOR'].enabled = self.two_sided and self.use_ior_bf and self.advanced
        self.inputs['BF Absorption Color'].enabled = self.two_sided and self.advanced
        self.inputs['BF Absorption Depth (nm)'].enabled = self.two_sided and self.advanced

    def change_two_sided(self, context):
        self.inputs['BF Specular Color'].enabled = self.two_sided
        self.inputs['BF IOR'].enabled = self.two_sided and self.use_ior_bf and self.advanced
        self.inputs['BF Absorption Color'].enabled = self.two_sided and self.advanced
        self.inputs['BF Absorption Depth (nm)'].enabled = self.two_sided and self.advanced

        if self.use_anisotropy_bf:
            self.inputs['BF U-Roughness'].enabled = self.two_sided
        else:
            self.inputs['BF Roughness'].enabled = self.two_sided

        self.inputs['BF V-Roughness'].enabled = self.two_sided and self.use_anisotropy_bf

    def change_use_ior(self, context):
        # # Specular/IOR representation switches
        self.inputs['Specular Color'].enabled = not self.use_ior
        self.inputs['IOR'].enabled = self.use_ior

    def change_use_ior_bf(self, context):
        # # Specular/IOR representation switches
        self.inputs['BF Specular Color'].enabled = not self.use_ior_bf
        self.inputs['BF IOR'].enabled = self.use_ior_bf

    def change_use_anisotropy(self, context):
        try:
            self.inputs['Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'
        except:
            self.inputs['U-Roughness'].sync_vroughness = not self.use_anisotropy
            self.inputs['U-Roughness'].name = 'Roughness' if not self.use_anisotropy else 'U-Roughness'

        self.inputs['V-Roughness'].enabled = self.use_anisotropy

    def change_use_anisotropy_bf(self, context):
        try:
            self.inputs['BF Roughness'].sync_vroughness = not self.use_anisotropy_bf
            self.inputs['BF Roughness'].name = 'BF Roughness' if not self.use_anisotropy_bf else 'BF U-Roughness'
        except:
            self.inputs['BF U-Roughness'].sync_vroughness = not self.use_anisotropy_bf
            self.inputs['BF U-Roughness'].name = 'BF Roughness' if not self.use_anisotropy_bf else 'BF U-Roughness'

        self.inputs['BF V-Roughness'].enabled = self.use_anisotropy_bf

    advanced = bpy.props.BoolProperty(name='Advanced Options', description='Configure advanced options',
                                       default=False, update=change_advanced)
    two_sided = bpy.props.BoolProperty(name='Two Sided', description='Use different specular properties for the back',
                                       default=False, update=change_two_sided)

    multibounce = bpy.props.BoolProperty(name='Multibounce', description='Enable surface layer multibounce',
                                         default=False)
    use_ior = bpy.props.BoolProperty(name='Use IOR', description='Set specularity by IOR', default=False,
                                     update=change_use_ior)
    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    multibounce_bf = bpy.props.BoolProperty(name='BF Multibounce', description='Enable surface layer multibounce on backface',
                                         default=False)
    use_ior_bf = bpy.props.BoolProperty(name='BF Use IOR', description='Set specularity by IOR on backface', default=False,
                                     update=change_use_ior_bf)
    use_anisotropy_bf = bpy.props.BoolProperty(name='BF Anisotropic Roughness', description='Anisotropic Roughness on backface',
                                            default=False, update=change_use_anisotropy_bf)


    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('pbrtv3_TC_Kt_socket', 'Transmission Color')

        # Front
        self.inputs.new('pbrtv3_TC_Ks_socket', 'Specular Color')
        self.inputs.new('pbrtv3_TF_ior_socket', 'IOR')
        self.inputs['IOR'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TC_Ka_socket', 'Absorption Color')
        self.inputs['Absorption Color'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_d_socket', 'Absorption Depth (nm)')
        self.inputs['Absorption Depth (nm)'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs['U-Roughness'].name = 'Roughness'
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled

        # Back (not Classic API compatible due to wrong sockets), initially disabled
        self.inputs.new('pbrtv3_TC_Ks_socket', 'BF Specular Color')
        self.inputs['BF Specular Color'].enabled = False
        self.inputs.new('pbrtv3_TF_ior_socket', 'BF IOR')
        self.inputs['BF IOR'].enabled = False
        self.inputs.new('pbrtv3_TC_Ka_socket', 'BF Absorption Color')
        self.inputs['BF Absorption Color'].enabled = False
        self.inputs.new('pbrtv3_TF_d_socket', 'BF Absorption Depth (nm)')
        self.inputs['BF Absorption Depth (nm)'].enabled = False
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'BF U-Roughness')
        self.inputs['BF U-Roughness'].enabled = False
        self.inputs['BF U-Roughness'].name = 'BF Roughness'
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'BF V-Roughness')
        self.inputs['BF V-Roughness'].enabled = False

        add_common_sockets(self)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_anisotropy')
        layout.prop(self, 'advanced', toggle=True)

        if self.advanced:
            layout.prop(self, 'multibounce')
            layout.prop(self, 'use_ior')

        layout.separator()
        layout.prop(self, 'two_sided')

        if self.two_sided:
            layout.prop(self, 'use_anisotropy_bf')

            if self.advanced:
                layout.prop(self, 'multibounce_bf')
                layout.prop(self, 'use_ior_bf')

    def export_material(self, make_material, make_texture):
        mat_type = 'glossytranslucent'

        glossytranslucent_params = ParamSet()
        glossytranslucent_params.update(get_socket_paramsets(self.inputs, make_texture))

        glossytranslucent_params.add_bool('multibounce', self.multibounce)

        return make_material(mat_type, self.name, glossytranslucent_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kd = self.inputs['Diffuse Color'].export_luxcore(properties)
        kt = self.inputs['Transmission Color'].export_luxcore(properties)

        # Front
        ks = self.inputs['Specular Color'].export_luxcore(properties)
        u_roughness = self.inputs[6].export_luxcore(properties)
        v_roughness = self.inputs[7].export_luxcore(properties) if self.use_anisotropy else u_roughness
        ka = self.inputs['Absorption Color'].export_luxcore(properties)
        d = self.inputs['Absorption Depth (nm)'].export_luxcore(properties)
        index = self.inputs['IOR'].export_luxcore(properties)
        # Back
        ks_bf = self.inputs['BF Specular Color'].export_luxcore(properties) if self.two_sided else ks
        u_roughness_bf = self.inputs[12].export_luxcore(properties) if self.two_sided else u_roughness
        if self.two_sided:
            v_roughness_bf = self.inputs[13].export_luxcore(properties) if self.use_anisotropy_bf else u_roughness_bf
        else:
            v_roughness_bf = v_roughness
        ka_bf = self.inputs['BF Absorption Color'].export_luxcore(properties) if self.two_sided else ka
        d_bf = self.inputs['BF Absorption Depth (nm)'].export_luxcore(properties) if self.two_sided else d
        index_bf = self.inputs['BF IOR'].export_luxcore(properties) if self.two_sided else index

        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'glossytranslucent')
        set_prop_mat(properties, luxcore_name, 'kd', kd)
        set_prop_mat(properties, luxcore_name, 'kt', kt)

        # Front
        set_prop_mat(properties, luxcore_name, 'ks', ks)
        set_prop_mat(properties, luxcore_name, 'uroughness', u_roughness)
        set_prop_mat(properties, luxcore_name, 'vroughness', v_roughness)
        set_prop_mat(properties, luxcore_name, 'ka', ka)
        set_prop_mat(properties, luxcore_name, 'd', d)
        set_prop_mat(properties, luxcore_name, 'multibounce', self.multibounce)

        if self.use_ior:
            set_prop_mat(properties, luxcore_name, 'index', index)

        # Back
        set_prop_mat(properties, luxcore_name, 'ks_bf', ks_bf)
        set_prop_mat(properties, luxcore_name, 'uroughness_bf', u_roughness_bf)
        set_prop_mat(properties, luxcore_name, 'vroughness_bf', v_roughness_bf)
        set_prop_mat(properties, luxcore_name, 'ka_bf', ka_bf)
        set_prop_mat(properties, luxcore_name, 'd_bf', d_bf)
        set_prop_mat(properties, luxcore_name, 'multibounce_bf', self.multibounce_bf)

        if self.use_ior_bf:
            set_prop_mat(properties, luxcore_name, 'index_bf', index_bf)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_layered(pbrtv3_material_node):
    """Layered material node"""
    bl_idname = 'pbrtv3_material_layered_node'
    bl_label = 'Layered Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Material 1')
        self.inputs.new('pbrtv3_TF_OP1_socket', 'Opacity 1')
        self.inputs.new('NodeSocketShader', 'Material 2')
        self.inputs.new('pbrtv3_TF_OP2_socket', 'Opacity 2')
        self.inputs.new('NodeSocketShader', 'Material 3')
        self.inputs.new('pbrtv3_TF_OP3_socket', 'Opacity 3')
        self.inputs.new('NodeSocketShader', 'Material 4')
        self.inputs.new('pbrtv3_TF_OP4_socket', 'Opacity 4')

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

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

            if node is None or not check_node_export_material(node):
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


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_matte(pbrtv3_material_node):
    """Matte material node"""
    bl_idname = 'pbrtv3_material_matte_node'
    bl_label = 'Matte Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('pbrtv3_TF_sigma_socket', 'Sigma')

        add_common_sockets(self)

    def export_material(self, make_material, make_texture):
        mat_type = 'matte'

        matte_params = ParamSet()
        matte_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, matte_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kd = self.inputs[0].export_luxcore(properties)
        sigma = self.inputs[1].export_luxcore(properties)
        bump, transparency = export_common_sockets(self, properties)

        if sigma == 0:
            set_prop_mat(properties, luxcore_name, 'type', 'matte')
        else:
            set_prop_mat(properties, luxcore_name, 'type', 'roughmatte')
            set_prop_mat(properties, luxcore_name, 'sigma', sigma)

        set_prop_mat(properties, luxcore_name, 'kd', kd)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_mattetranslucent(pbrtv3_material_node):
    """Mattetranslucent material node"""
    bl_idname = 'pbrtv3_material_mattetranslucent_node'
    bl_label = 'Matte Translucent Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    energyconsrv = bpy.props.BoolProperty(name='Energy Conserving', default=True)

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('pbrtv3_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('pbrtv3_TF_sigma_socket', 'Sigma')

        add_common_sockets(self)

    def export_material(self, make_material, make_texture):
        mat_type = 'mattetranslucent'

        mattetranslucent_params = ParamSet()
        mattetranslucent_params.update(get_socket_paramsets(self.inputs, make_texture))
        mattetranslucent_params.add_bool('energyconserving', self.energyconsrv)

        return make_material(mat_type, self.name, mattetranslucent_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kr = self.inputs[0].export_luxcore(properties)
        kt = self.inputs[1].export_luxcore(properties)
        sigma = self.inputs[2].export_luxcore(properties)
        bump, transparency = export_common_sockets(self, properties)

        if sigma == 0:
            set_prop_mat(properties, luxcore_name, 'type', 'mattetranslucent')
        else:
            set_prop_mat(properties, luxcore_name, 'type', 'roughmattetranslucent')
            set_prop_mat(properties, luxcore_name, 'sigma', sigma)

        set_prop_mat(properties, luxcore_name, 'kr', kr)
        set_prop_mat(properties, luxcore_name, 'kt', kt)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


# Deprecated, replaced with metal2 node
@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_metal(pbrtv3_material_node):
    """Metal material node"""
    bl_idname = 'pbrtv3_material_metal_node'
    bl_label = 'Metal Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    for prop in pbrtv3_mat_metal.properties:
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
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

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
            process_filepath_data(PBRTv3Manager.CurrentScene, self, self.metal_nkfile, metal_params, 'filename')
        else:
            # use a preset name
            metal_params.add_string('name', self.metal_preset)

        return make_material(mat_type, self.name, metal_params)


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_metal2(pbrtv3_material_node):
    """Metal2 material node"""
    bl_idname = 'pbrtv3_material_metal2_node'
    bl_label = 'Metal Material'
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

    def change_input_type(self, context):
        self.inputs['Fresnel'].enabled = self.input_type == 'fresnel'
        self.inputs['Color'].enabled = self.input_type == 'color'

    input_type_items = [
        ('color', 'Color', 'Use custom color as input'),
        ('fresnel', 'Fresnel Texture', 'Use a fresnel texture as input')
    ]
    input_type = bpy.props.EnumProperty(name='Type', description='Input Type', items=input_type_items, default='color',
                                        update=change_input_type)

    use_anisotropy = bpy.props.BoolProperty(name='Anisotropic Roughness', description='Anisotropic Roughness',
                                            default=False, update=change_use_anisotropy)

    def init(self, context):
        self.inputs.new('pbrtv3_color_socket', 'Color')
        self.inputs.new('pbrtv3_fresnel_socket', 'Fresnel')
        self.inputs['Fresnel'].needs_link = True  # suppress inappropiate chooser
        self.inputs['Fresnel'].enabled = False
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs['U-Roughness'].name = 'Roughness'

        add_common_sockets(self)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_anisotropy')
        layout.prop(self, 'input_type', expand=True)

        if not UsePBRTv3Core() and self.input_type == 'color':
            layout.label('Classic only supports fresnel!', icon='ERROR')

    def export_material(self, make_material, make_texture):
        mat_type = 'metal2'

        metal2_params = ParamSet()
        metal2_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, metal2_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        if self.input_type == 'color':
            kr = self.inputs['Color'].export_luxcore(properties)

            # Implicitly create a fresnelcolor texture
            fresnel_texture = create_luxcore_name(self, suffix='fresnelcolor')
            set_prop_tex(properties, fresnel_texture, 'type', 'fresnelcolor')
            set_prop_tex(properties, fresnel_texture, 'kr', kr)
        else:
            if self.inputs['Fresnel'].is_linked:
                fresnel_texture = self.inputs['Fresnel'].export_luxcore(properties)
            else:
                print('Warning: Metal2 node "%s" is in fresnel mode, but no fresnel texture is connected' % self.name)
                # Use a black color to signal that nothing is connected, but PBRTv3Core is still able to render
                fresnel_texture = create_luxcore_name(self, suffix='fresnelcolor')
                set_prop_tex(properties, fresnel_texture, 'type', 'fresnelcolor')
                set_prop_tex(properties, fresnel_texture, 'kr', [0, 0, 0])

        u_roughness = self.inputs[2].export_luxcore(properties)
        v_roughness = self.inputs[3].export_luxcore(properties) if self.use_anisotropy else u_roughness

        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'metal2')
        set_prop_mat(properties, luxcore_name, 'uroughness', u_roughness)
        set_prop_mat(properties, luxcore_name, 'vroughness', v_roughness)
        set_prop_mat(properties, luxcore_name, 'fresnel', fresnel_texture)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_mirror(pbrtv3_material_node):
    """Mirror material node"""
    bl_idname = 'pbrtv3_material_mirror_node'
    bl_label = 'Mirror Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('pbrtv3_TF_film_ior_socket', 'Film IOR')
        self.inputs.new('pbrtv3_TF_film_thick_socket', 'Film Thickness (nm)')

        add_common_sockets(self)

    def export_material(self, make_material, make_texture):
        mat_type = 'mirror'

        mirror_params = ParamSet()
        mirror_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, mirror_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kr = self.inputs['Reflection Color'].export_luxcore(properties)
        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'mirror')
        set_prop_mat(properties, luxcore_name, 'kr', kr)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_mix(pbrtv3_material_node):
    """Mix material node"""
    bl_idname = 'pbrtv3_material_mix_node'
    bl_label = 'Mix Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('pbrtv3_TF_amount_socket', 'Mix Amount')
        self.inputs.new('NodeSocketShader', 'Material 1')
        self.inputs.new('NodeSocketShader', 'Material 2')

        add_common_sockets(self)

    def draw_buttons(self, context, layout):
        # OpenCL or CPU?
        enginesettings = context.scene.luxcore_enginesettings

        if UsePBRTv3Core() and (enginesettings.device == 'OCL' or enginesettings.device_preview == 'OCL'):
            mix_mats = [get_linked_node(self.inputs[1]), get_linked_node(self.inputs[2])]
            submats_have_bump = False
            for mat in mix_mats:
                if mat and 'Bump' in mat.inputs and mat.inputs['Bump'].is_linked:
                    submats_have_bump = True
                    break

            if submats_have_bump:
                layout.label('Bump on submats not supported by OpenCL engines!', icon='ERROR')
                layout.label('Use the bump slot of this node instead', icon='INFO')

    def export_material(self, make_material, make_texture):
        print('export node: mix')

        mat_type = 'mix'

        mix_params = ParamSet()
        mix_params.update(get_socket_paramsets([self.inputs[0]], make_texture))

        def export_submat(socket):
            node = get_linked_node(socket)

            if node is None or not check_node_export_material(node):
                return None

            return node.export_material(make_material, make_texture)

        mat1_name = export_submat(self.inputs[1])
        mat2_name = export_submat(self.inputs[2])

        mix_params.add_string("namedmaterial1", mat1_name)
        mix_params.add_string("namedmaterial2", mat2_name)

        return make_material(mat_type, self.name, mix_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        amount = self.inputs[0].export_luxcore(properties)
        mat1 = export_submat_luxcore(properties, self.inputs[1], luxcore_exporter)
        mat2 = export_submat_luxcore(properties, self.inputs[2], luxcore_exporter)
        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'mix')
        set_prop_mat(properties, luxcore_name, 'amount', amount)
        set_prop_mat(properties, luxcore_name, 'material1', mat1)
        set_prop_mat(properties, luxcore_name, 'material2', mat2)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_null(pbrtv3_material_node):
    """Null material node"""
    bl_idname = 'pbrtv3_material_null_node'
    bl_label = 'Transparent Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kt_socket', 'Transmission Color')
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        if not UsePBRTv3Core():
            layout.label('Color not supported in Classic API', icon='ERROR')

    def export_material(self, make_material, make_texture):
        mat_type = 'null'

        null_params = ParamSet()

        return make_material(mat_type, self.name, null_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        if 'Transmission Color' in self.inputs:
            transparency = self.inputs['Transmission Color'].export_luxcore(properties)
        else:
            transparency = 1.0

        set_prop_mat(properties, luxcore_name, 'type', 'null')

        if transparency != 1.0 and transparency != [1.0, 1.0, 1.0]:
            set_prop_mat(properties, luxcore_name, 'transparency', transparency)

        return luxcore_name


# Deprecated, replaced by unified glass node
@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_roughglass(pbrtv3_material_node):
    """Rough Glass material node"""
    bl_idname = 'pbrtv3_material_roughglass_node'
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
        self.inputs.new('pbrtv3_TC_Kt_socket', 'Transmission Color')
        self.inputs.new('pbrtv3_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('pbrtv3_TF_ior_socket', 'IOR')
        self.inputs.new('pbrtv3_TF_cauchyb_socket', 'Cauchy B')
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

        layout.prop(self, 'use_anisotropy')
        layout.prop(self, 'dispersion')

    def export_material(self, make_material, make_texture):
        mat_type = 'roughglass'

        roughglass_params = ParamSet()
        roughglass_params.update(get_socket_paramsets(self.inputs, make_texture))

        roughglass_params.add_bool('dispersion', self.dispersion)

        return make_material(mat_type, self.name, roughglass_params)


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_scatter(pbrtv3_material_node):
    """Scatter material node"""
    bl_idname = 'pbrtv3_material_scatter_node'
    bl_label = 'Scatter Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('pbrtv3_SC_asymmetry_socket', 'Asymmetry')

        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

    def export_material(self, make_material, make_texture):
        mat_type = 'scatter'

        scatter_params = ParamSet()
        scatter_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, scatter_params)


# Deprecated
@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_shinymetal(pbrtv3_material_node):
    """Shiny metal material node"""
    bl_idname = 'pbrtv3_material_shinymetal_node'
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
        self.inputs.new('pbrtv3_TC_Kr_socket', 'Reflection Color')
        self.inputs.new('pbrtv3_TC_Ks_socket', 'Specular Color')
        self.inputs.new('pbrtv3_TF_film_ior_socket', 'Film IOR')
        self.inputs.new('pbrtv3_TF_film_thick_socket', 'Film Thickness (nm)')
        self.inputs.new('pbrtv3_TF_uroughness_socket', 'U-Roughness')
        self.inputs.new('pbrtv3_TF_vroughness_socket', 'V-Roughness')
        self.inputs['V-Roughness'].enabled = False  # initial state is disabled
        self.inputs.new('pbrtv3_TF_bump_socket', 'Bump')

        self.inputs['U-Roughness'].name = 'Roughness'
        self.outputs.new('NodeSocketShader', 'Surface')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

        layout.prop(self, 'use_anisotropy')

    def export_material(self, make_material, make_texture):
        mat_type = 'shinymetal'

        shinymetal_params = ParamSet()
        shinymetal_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_material(mat_type, self.name, shinymetal_params)


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_velvet(pbrtv3_material_node):
    """Velvet material node"""
    bl_idname = 'pbrtv3_material_velvet_node'
    bl_label = 'Velvet Material'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    def update_advanced(self, context):
        self.inputs['p1'].enabled = self.advanced
        self.inputs['p2'].enabled = self.advanced
        self.inputs['p3'].enabled = self.advanced

    advanced = bpy.props.BoolProperty(name='Advanced Options', description='Advanced Velvet Parameters', default=False,
                                      update=update_advanced)

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kd_socket', 'Diffuse Color')
        self.inputs.new('pbrtv3_float_socket', 'Thickness')
        self.inputs['Thickness'].default_value = 0.1
        self.inputs.new('pbrtv3_float_socket', 'p1')
        self.inputs['p1'].enabled = False
        self.inputs['p1'].default_value = 2
        self.inputs.new('pbrtv3_float_socket', 'p2')
        self.inputs['p2'].enabled = False
        self.inputs['p2'].default_value = 10
        self.inputs.new('pbrtv3_float_socket', 'p3')
        self.inputs['p3'].enabled = False
        self.inputs['p3'].default_value = 2

        add_common_sockets(self)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'advanced', toggle=True)

    def export_material(self, make_material, make_texture):
        mat_type = 'velvet'

        velvet_params = ParamSet()
        velvet_params.update(get_socket_paramsets(self.inputs, make_texture))

        # Classic Lux does not support textured parameters here, so we just use the socket value
        velvet_params.add_float('thickness', self.inputs['Thickness'].default_value)
        velvet_params.add_float('p1', self.inputs['p1'].default_value)
        velvet_params.add_float('p2', self.inputs['p2'].default_value)
        velvet_params.add_float('p3', self.inputs['p3'].default_value)

        return make_material(mat_type, self.name, velvet_params)

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        luxcore_name = create_luxcore_name_mat(self, name)

        kd = self.inputs['Diffuse Color'].export_luxcore(properties)
        thickness = self.inputs['Thickness'].export_luxcore(properties)
        p1 = self.inputs['p1'].export_luxcore(properties)
        p2 = self.inputs['p2'].export_luxcore(properties)
        p3 = self.inputs['p3'].export_luxcore(properties)
        bump, transparency = export_common_sockets(self, properties)

        set_prop_mat(properties, luxcore_name, 'type', 'velvet')
        set_prop_mat(properties, luxcore_name, 'kd', kd)
        set_prop_mat(properties, luxcore_name, 'thickness', thickness)

        if self.advanced:
            set_prop_mat(properties, luxcore_name, 'p1', p1)
            set_prop_mat(properties, luxcore_name, 'p2', p2)
            set_prop_mat(properties, luxcore_name, 'p3', p3)

        set_common_properties(properties, luxcore_name, bump, transparency)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_light_area_node(pbrtv3_material_node):
    """Area Light node"""
    bl_idname = 'pbrtv3_light_area_node'
    bl_label = 'Light Emission'
    bl_icon = 'LAMP'
    bl_width_min = 160

    advanced = bpy.props.BoolProperty(name='Advanced Options', default=False)

    gain = bpy.props.FloatProperty(name='Gain', default=1.0, min=0.0, description='Multiplier for light intensity')
    power = bpy.props.FloatProperty(name='Power (W)', default=100.0, min=0.0)
    efficacy = bpy.props.FloatProperty(name='Efficacy (lm/W)', default=17.0, min=0.0)
    theta = bpy.props.FloatProperty(name='Spread Angle', default=math.radians(90), subtype='ANGLE', unit='ROTATION',
                                    min=0.0, soft_min=math.radians(5), max=math.radians(90),
                                    description='How directional the light is emitted, set as the half-angle of the light source. '
                                    'Default is 90°. Smaller values mean that more light is emitted in the direction '
                                    'of the light and less to the sides.')
    iesname = bpy.props.StringProperty(name='IES Data', description='IES file path', subtype='FILE_PATH')
    importance = bpy.props.FloatProperty(name='Importance', default=1.0, min=0.0,
                                         description='How often the light is sampled compared to other light sources. '
                                                     'Does not change the look but may have an impact on how quickly '
                                                     'the render cleans up.')
    nsamples = bpy.props.IntProperty(name='Shadow Ray Count', default=1, min=1, max=64,
                                     description='Number of shadow samples per bounce')
    luxcore_samples = bpy.props.IntProperty(name='Samples', default=-1, min=-1, max=64,
                                     description='Number of shadow samples per bounce (-1 = use global settings)')
    lightgroup = bpy.props.StringProperty(description='Lightgroup; leave blank to use default')

    def init(self, context):
        self.inputs.new('pbrtv3_TC_L_socket', 'Light Color')

        self.outputs.new('NodeSocketShader', 'Emission')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'gain')

        if UsePBRTv3Core():
            layout.prop_search(self, 'lightgroup', context.scene.pbrtv3_lightgroups, 'lightgroups',
                               'Lightgroup', icon='OUTLINER_OB_LAMP')

        layout.prop(self, 'advanced', toggle=True)

        if self.advanced:
            layout.prop(self, 'power')
            layout.prop(self, 'efficacy')

            if UsePBRTv3Core():
                layout.prop(self, 'theta')

            layout.prop(self, 'iesname')

            if UsePBRTv3Core():
                layout.prop(self, 'luxcore_samples')
            else:
                layout.prop(self, 'importance')
                layout.prop(self, 'nsamples')

    def export(self, make_texture):
        arealight_params = ParamSet()
        arealight_params.update(get_socket_paramsets(self.inputs, make_texture))
        #arealight_params.add_float('gain', self.gain)
        #arealight_params.add_float('power', self.power)
        #arealight_params.add_float('efficacy', self.efficacy)

        if self.iesname:
            process_filepath_data(PBRTv3Manager.CurrentScene, self, self.iesname, arealight_params, 'iesname')

        #arealight_params.add_float('importance', self.importance)
        arealight_params.add_integer('samples', self.nsamples)

        return 'area', arealight_params

    def export_luxcore(self, properties, luxcore_exporter, parent_luxcore_name, is_volume_emission=False):
        emission = self.inputs[0].export_luxcore(properties)

        set_prop = set_prop_vol if is_volume_emission else set_prop_mat

        set_prop(properties, parent_luxcore_name, 'emission', emission)
        set_prop(properties, parent_luxcore_name, 'emission.gain', [self.gain] * 3)
        set_prop(properties, parent_luxcore_name, 'emission.power', self.power)
        set_prop(properties, parent_luxcore_name, 'emission.efficency', self.efficacy)
        set_prop(properties, parent_luxcore_name, 'emission.samples', self.luxcore_samples)
        set_prop(properties, parent_luxcore_name, 'emission.theta', math.degrees(self.theta))

        # IES
        iesfile = self.iesname
        iesfile, basename = get_expanded_file_name(self, iesfile)
        if os.path.exists(iesfile):
            set_prop(properties, parent_luxcore_name, 'emission.iesfile', iesfile)

        # Lightgroup
        blender_scene = luxcore_exporter.blender_scene
        lightgroup_id = luxcore_exporter.lightgroup_cache.get_id(self.lightgroup, blender_scene, self)
        is_opencl_compatible = is_lightgroup_opencl_compatible(luxcore_exporter, lightgroup_id)

        if not blender_scene.pbrtv3_lightgroups.ignore and is_opencl_compatible:
            set_prop_mat(properties, parent_luxcore_name, 'emission.id', lightgroup_id)


@PBRTv3Addon.addon_register_class
class pbrtv3_material_type_node_datablock(pbrtv3_material_node):
    """Datablock material node"""
    bl_idname = 'pbrtv3_material_type_node_datablock'
    bl_label = 'Material Datablock'
    bl_icon = 'MATERIAL'
    bl_width_min = 160

    datablock_name = bpy.props.StringProperty(name='Datablock', description='A material from the scene')

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Surface')
        # add tex output

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'datablock_name', bpy.data, 'materials', text='')

    def export_luxcore(self, properties, luxcore_exporter, name=None):
        if self.datablock_name in bpy.data.materials:
            mat = bpy.data.materials[self.datablock_name]

            luxcore_exporter.convert_material(mat)
            exporter = luxcore_exporter.material_cache[get_elem_key(mat)]
            luxcore_name = exporter.luxcore_name
        else:
            luxcore_name = create_luxcore_name_mat(self, name)
            set_prop_mat(properties, luxcore_name, 'type', 'matte')
            set_prop_mat(properties, luxcore_name, 'kd', [0, 0, 0])

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_material_output_node(pbrtv3_node):
    """Material output node"""
    bl_idname = 'pbrtv3_material_output_node'
    bl_label = 'Material Output'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    interior_volume = bpy.props.StringProperty(description='Volume inside of the object with this material')
    exterior_volume = bpy.props.StringProperty(description='Volume outside of the object with this material')
    materialgroup = bpy.props.StringProperty(description='Materialgroup for Material ID pass; leave blank to use default')
    is_shadow_catcher = bpy.props.BoolProperty(name='Shadow Catcher', default=False, description=
        'Make material transparent where hit by light and opaque where shadowed (alpha transparency)')
    sc_onlyinfinitelights = bpy.props.BoolProperty(name='Only Infinite Lights', default=False, description=
        'Only consider infinite lights for this shadow catcher')
    advanced = bpy.props.BoolProperty(name='Advanced Options', default=False, description=
        'Show advanced material settings')
    samples = bpy.props.IntProperty(name='Samples', default=-1, min=-1, soft_max=16, max=256, description=
        'Material samples count (-1 = global default, size x size)')
    visibility_indirect_diffuse_enable = bpy.props.BoolProperty(name='Diffuse', default=True, description=
        'Enable material visibility for indirect rays')
    visibility_indirect_glossy_enable = bpy.props.BoolProperty(name='Glossy', default=True, description=
        'Enable material visibility for glossy rays')
    visibility_indirect_specular_enable = bpy.props.BoolProperty(name='Specular', default=True, description=
        'Enable material visibility for specular rays')

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Surface')
        self.inputs.new('NodeSocketShader', 'Emission')

    def draw_buttons(self, context, layout):
        layout.label('Volumes:')

        layout.prop_search(self, 'interior_volume', context.scene.pbrtv3_volumes, 'volumes', 'Interior',
                           icon='MOD_FLUIDSIM')

        default_interior = context.scene.pbrtv3_world.default_interior_volume
        if not self.interior_volume and default_interior:
            layout.label('Using default: "%s"' % default_interior, icon='INFO')

        layout.prop_search(self, 'exterior_volume', context.scene.pbrtv3_volumes, 'volumes', 'Exterior',
                           icon='MOD_FLUIDSIM')

        default_exterior = context.scene.pbrtv3_world.default_exterior_volume
        if not self.exterior_volume and default_exterior:
            layout.label('Using default: "%s"' % default_exterior, icon='INFO')

        if UsePBRTv3Core():
            layout.prop(self, 'is_shadow_catcher')
            if self.is_shadow_catcher:
                layout.prop(self, 'sc_onlyinfinitelights')
            layout.prop_search(self, 'materialgroup', context.scene.pbrtv3_materialgroups, 'materialgroups',
                               'MGroup', icon='IMASEL')

            layout.prop(self, 'advanced', toggle=True)

            if self.advanced:
                layout.label('Biased Path Settings:')
                column = layout.column()
                column.enabled = context.scene.luxcore_enginesettings.renderengine_type == 'TILEPATH'

                column.prop(self, 'samples')
                column.label('Visibility for indirect rays:')
                row = column.row()
                row.prop(self, 'visibility_indirect_diffuse_enable')
                row.prop(self, 'visibility_indirect_glossy_enable')
                row.prop(self, 'visibility_indirect_specular_enable')

    def export_luxcore(self, material, properties, blender_scene, luxcore_exporter, luxcore_name):
        # Note: volumes are exported in export/luxcore/materials.py (in "parent" function that calls this function)

        tree_name = material.pbrtv3_material.nodetree
        print('Converting material: %s (Nodetree: %s)' % (material.name, tree_name))

        # Export the material tree
        export_submat_luxcore(properties, self.inputs[0], luxcore_exporter, luxcore_name)

        # Export emission node if attached to this node
        export_emission_luxcore(properties, luxcore_exporter, self.inputs['Emission'], luxcore_name)

        # Material group
        materialgroup_name = self.materialgroup
        if materialgroup_name in blender_scene.pbrtv3_materialgroups.materialgroups:
            group = blender_scene.pbrtv3_materialgroups.materialgroups[materialgroup_name]

            set_prop_mat(properties, luxcore_name, 'id', group.id)

            if group.create_MATERIAL_ID_MASK and blender_scene.pbrtv3_channels.enable_aovs:
                luxcore_exporter.config_exporter.convert_channel('MATERIAL_ID_MASK', group.id)
            if group.create_BY_MATERIAL_ID and blender_scene.pbrtv3_channels.enable_aovs:
                luxcore_exporter.config_exporter.convert_channel('BY_MATERIAL_ID', group.id)

        # Export advanced PBRTv3Core material settings
        set_prop_mat(properties, luxcore_name, 'samples', self.samples)
        set_prop_mat(properties, luxcore_name, 'visibility.indirect.diffuse.enable',
                     self.visibility_indirect_diffuse_enable)
        set_prop_mat(properties, luxcore_name, 'visibility.indirect.glossy.enable',
                     self.visibility_indirect_glossy_enable)
        set_prop_mat(properties, luxcore_name, 'visibility.indirect.specular.enable',
                     self.visibility_indirect_specular_enable)

        # Shadow catcher
        set_prop_mat(properties, luxcore_name, 'shadowcatcher.enable', self.is_shadow_catcher)
        set_prop_mat(properties, luxcore_name, 'shadowcatcher.onlyinfinitelights', self.sc_onlyinfinitelights)

        return luxcore_name

    def export(self, scene, lux_context, material, mode='indirect'):

        print('Exporting node tree, mode: %s' % mode)

        surface_socket = self.inputs[0]  # perhaps by name?
        if not surface_socket.is_linked:
            return set()

        surface_node = surface_socket.links[0].from_node

        tree_name = material.pbrtv3_material.nodetree

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
                if scene.pbrtv3_integrator.surfaceintegrator == 'distributedpath':
                    mat_params.update(material.pbrtv3_material.pbrtv3_mat_compositing.get_paramset())

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
                if scene.pbrtv3_integrator.surfaceintegrator == 'distributedpath':
                    mat_params.update(material.pbrtv3_material.pbrtv3_mat_compositing.get_paramset())

                ExportedMaterials.makeNamedMaterial(lux_context, material_name, mat_params)
                ExportedMaterials.export_new_named(lux_context)

                return material_name

            make_material = make_material_direct


        # texture exporting, only one way
        make_texture = pbrtv3_texture_maker(lux_context, tree_name).make_texture

        # start exporting that material...
        with MaterialCounter(material.name):
            if not (mode == 'indirect' and material.name in ExportedMaterials.exported_material_names):
                if check_node_export_material(surface_node):
                    surface_node.export_material(make_material=make_material, make_texture=make_texture)

        # TODO: remove, volumes (with nodes) are now exported from their own output node
        '''
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
        '''

        return set()

