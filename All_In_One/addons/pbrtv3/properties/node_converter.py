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

from math import radians

import bpy
import mathutils

from . import warning_luxcore_node, create_luxcore_name
from .. import PBRTv3Addon

from ..export import ParamSet, get_worldscale

from ..outputs.luxcore_api import UsePBRTv3Core, set_prop_tex

from ..properties import pbrtv3_texture_node, get_linked_node, check_node_export_texture
from ..properties.node_material import get_socket_paramsets
from ..properties.node_sockets import mapping_2d_socketname, mapping_3d_socketname
from ..properties.node_texture import variant_items, triple_variant_items


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_add(pbrtv3_texture_node):
    """Add texture node"""
    bl_idname = 'pbrtv3_texture_add_node'
    bl_label = 'Add'
    bl_icon = 'TEXTURE'

    variant = bpy.props.EnumProperty(name='Variant', items=variant_items, default='color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')

        si = self.inputs.keys()
        so = self.outputs.keys()
        if self.variant == 'color':
            if not 'Color 1' in si:  # If there aren't color inputs, create them
                self.inputs.new('pbrtv3_TC_tex1_socket', 'Color 1')
                self.inputs.new('pbrtv3_TC_tex2_socket', 'Color 2')

            if 'Float 1' in si:  # If there are float inputs, destory them
                self.inputs.remove(self.inputs['Float 1'])
                self.inputs.remove(self.inputs['Float 2'])

            if not 'Color' in so:  # If there is no color output, create it
                self.outputs.new('NodeSocketColor', 'Color')

            if 'Float' in so:  # If there is a float output, destroy it
                self.outputs.remove(self.outputs['Float'])
        if self.variant == 'float':
            if not 'Float 1' in si:
                self.inputs.new('pbrtv3_TF_tex1_socket', 'Float 1')
                self.inputs.new('pbrtv3_TF_tex2_socket', 'Float 2')

            if 'Color 1' in si:
                self.inputs.remove(self.inputs['Color 1'])
                self.inputs.remove(self.inputs['Color 2'])

            if not 'Float' in so:
                self.outputs.new('NodeSocketFloat', 'Float')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

    def export_texture(self, make_texture):
        addtex_params = ParamSet()
        addtex_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture(self.variant, 'add', self.name, addtex_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        tex1 = self.inputs[0].export_luxcore(properties)
        tex2 = self.inputs[1].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'add')
        set_prop_tex(properties, luxcore_name, 'texture1', tex1)
        set_prop_tex(properties, luxcore_name, 'texture2', tex2)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_bump_map(pbrtv3_texture_node):
    """Bump map texture node"""
    bl_idname = 'pbrtv3_texture_bump_map_node'
    bl_label = 'Bump Height'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    # TODO: change this to be a socket? Possible with classic API?
    bump_height = bpy.props.FloatProperty(name='Bump Height', description='Height of the bump map', default=.001,
                                          precision=6, subtype='DISTANCE', unit='LENGTH', step=.001)

    def calculate_bump_height(self):
        return self.bump_height * get_worldscale(as_scalematrix=False)

    def init(self, context):
        self.inputs.new('pbrtv3_TF_bump_socket', 'Float')
        self.outputs.new('NodeSocketFloat', 'Bump')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'bump_height')

    def export_texture(self, make_texture):
        if get_linked_node(self.inputs[0]).name in ( "Image Map Texture", "Classic Image Map Texture"):
            bumpmap_params = ParamSet() \
                .add_float('tex1', self.calculate_bump_height()) # Imagemaps need worldscale applied
        else:
            bumpmap_params = ParamSet() \
                .add_float('tex1', self.bump_height)

        tex_node = get_linked_node(self.inputs[0])

        if tex_node and check_node_export_texture(tex_node):
            bumpmap_name = tex_node.export_texture(make_texture)
            bumpmap_params.add_texture("tex2", bumpmap_name)

        return make_texture('float', 'scale', self.name, bumpmap_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        input = self.inputs[0].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'scale')
        set_prop_tex(properties, luxcore_name, 'texture1', input)
        set_prop_tex(properties, luxcore_name, 'texture2', self.calculate_bump_height())

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_mix(pbrtv3_texture_node):
    """Mix texture node"""
    bl_idname = 'pbrtv3_texture_mix_node'
    bl_label = 'Mix'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    variant = bpy.props.EnumProperty(name='Variant', items=triple_variant_items, default='color')

    def init(self, context):
        self.inputs.new('pbrtv3_TF_amount_socket', 'Mix Amount')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')

        si = self.inputs.keys()
        so = self.outputs.keys()

        if self.variant == 'color':
            if not 'Color 1' in si:
                self.inputs.new('pbrtv3_TC_tex1_socket', 'Color 1')
                self.inputs.new('pbrtv3_TC_tex2_socket', 'Color 2')

            if 'Float 1' in si:
                self.inputs.remove(self.inputs['Float 1'])
                self.inputs.remove(self.inputs['Float 2'])

            if 'IOR 1' in si:
                self.inputs.remove(self.inputs['IOR 1'])
                self.inputs.remove(self.inputs['IOR 2'])

            if not 'Color' in so:
                self.outputs.new('NodeSocketColor', 'Color')

            if 'Float' in so:
                self.outputs.remove(self.outputs['Float'])

            if 'Fresnel' in so:
                self.outputs.remove(self.outputs['Fresnel'])

        if self.variant == 'float':
            if not 'Float 1' in si:
                self.inputs.new('pbrtv3_TF_tex1_socket', 'Float 1')
                self.inputs.new('pbrtv3_TF_tex2_socket', 'Float 2')

            if 'Color 1' in si:
                self.inputs.remove(self.inputs['Color 1'])
                self.inputs.remove(self.inputs['Color 2'])

            if 'IOR 1' in si:
                self.inputs.remove(self.inputs['IOR 1'])
                self.inputs.remove(self.inputs['IOR 2'])

            if not 'Float' in so:
                self.outputs.new('NodeSocketFloat', 'Float')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

            if 'Fresnel' in so:
                self.outputs.remove(self.outputs['Fresnel'])

        if self.variant == 'fresnel':
            if not 'IOR 1' in si:
                self.inputs.new('pbrtv3_TFR_tex1_socket', 'IOR 1')
                self.inputs.new('pbrtv3_TFR_tex2_socket', 'IOR 2')

            if 'Color 1' in si:
                self.inputs.remove(self.inputs['Color 1'])
                self.inputs.remove(self.inputs['Color 2'])

            if 'Float 1' in si:
                self.inputs.remove(self.inputs['Float 1'])
                self.inputs.remove(self.inputs['Float 2'])

            if not 'Fresnel' in so:
                self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
                self.outputs['Fresnel'].needs_link = True

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

            if 'Float' in so:
                self.outputs.remove(self.outputs['Float'])

    def export_texture(self, make_texture):
        mix_params = ParamSet()
        mix_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture(self.variant, 'mix', self.name, mix_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        amount = self.inputs[0].export_luxcore(properties)
        tex1 = self.inputs[1].export_luxcore(properties)
        tex2 = self.inputs[2].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'mix')
        set_prop_tex(properties, luxcore_name, 'amount', amount)
        set_prop_tex(properties, luxcore_name, 'texture1', tex1)
        set_prop_tex(properties, luxcore_name, 'texture2', tex2)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_scale(pbrtv3_texture_node):
    """Scale texture node"""
    bl_idname = 'pbrtv3_texture_scale_node'
    bl_label = 'Scale'
    bl_icon = 'TEXTURE'

    variant = bpy.props.EnumProperty(name='Variant', items=variant_items, default='color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')

        si = self.inputs.keys()
        so = self.outputs.keys()

        if self.variant == 'color':
            if not 'Color 1' in si:
                self.inputs.new('pbrtv3_TC_tex1_socket', 'Color 1')
                self.inputs.new('pbrtv3_TC_tex2_socket', 'Color 2')

            if 'Float 1' in si:
                self.inputs.remove(self.inputs['Float 1'])
                self.inputs.remove(self.inputs['Float 2'])

            if not 'Color' in so:
                self.outputs.new('NodeSocketColor', 'Color')

            if 'Float' in so:
                self.outputs.remove(self.outputs['Float'])
        if self.variant == 'float':
            if not 'Float 1' in si:
                self.inputs.new('pbrtv3_TF_tex1_socket', 'Float 1')
                self.inputs.new('pbrtv3_TF_tex2_socket', 'Float 2')

            if 'Color 1' in si:
                self.inputs.remove(self.inputs['Color 1'])
                self.inputs.remove(self.inputs['Color 2'])

            if not 'Float' in so:
                self.outputs.new('NodeSocketFloat', 'Float')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

    def export_texture(self, make_texture):
        scale_params = ParamSet()
        scale_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture(self.variant, 'scale', self.name, scale_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        tex1 = self.inputs[0].export_luxcore(properties)
        tex2 = self.inputs[1].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'scale')
        set_prop_tex(properties, luxcore_name, 'texture1', tex1)
        set_prop_tex(properties, luxcore_name, 'texture2', tex2)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_subtract(pbrtv3_texture_node):
    """Subtract texture node"""
    bl_idname = 'pbrtv3_texture_subtract_node'
    bl_label = 'Subtract'
    bl_icon = 'TEXTURE'

    variant = bpy.props.EnumProperty(name='Variant', items=variant_items, default='color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')

        si = self.inputs.keys()
        so = self.outputs.keys()
        if self.variant == 'color':
            if not 'Color 1' in si:
                self.inputs.new('pbrtv3_TC_tex1_socket', 'Color 1')
                self.inputs.new('pbrtv3_TC_tex2_socket', 'Color 2')

            if 'Float 1' in si:
                self.inputs.remove(self.inputs['Float 1'])
                self.inputs.remove(self.inputs['Float 2'])

            if not 'Color' in so:
                self.outputs.new('NodeSocketColor', 'Color')

            if 'Float' in so:
                self.outputs.remove(self.outputs['Float'])

        if self.variant == 'float':
            if not 'Float 1' in si:
                self.inputs.new('pbrtv3_TF_tex1_socket', 'Float 1')
                self.inputs.new('pbrtv3_TF_tex2_socket', 'Float 2')

            if 'Color 1' in si:
                self.inputs.remove(self.inputs['Color 1'])
                self.inputs.remove(self.inputs['Color 2'])

            if not 'Float' in so:
                self.outputs.new('NodeSocketFloat', 'Float')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

    def export_texture(self, make_texture):
        subtract_params = ParamSet()
        subtract_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture(self.variant, 'subtract', self.name, subtract_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        tex1 = self.inputs[0].export_luxcore(properties)
        tex2 = self.inputs[1].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'subtract')
        set_prop_tex(properties, luxcore_name, 'texture1', tex1)
        set_prop_tex(properties, luxcore_name, 'texture2', tex2)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_colordepth(pbrtv3_texture_node):
    """Color at Depth node"""
    bl_idname = 'pbrtv3_texture_colordepth_node'
    bl_label = 'Color at Depth'
    bl_icon = 'TEXTURE'

    depth = bpy.props.FloatProperty(name='Depth', default=1.0, subtype='DISTANCE', unit='LENGTH')

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kt_socket', 'Transmission Color')
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'depth')

    def export_texture(self, make_texture):
        colordepth_params = ParamSet()
        colordepth_params.update(get_socket_paramsets(self.inputs, make_texture))
        colordepth_params.add_float('depth', self.depth)

        return make_texture('color', 'colordepth', self.name, colordepth_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        kt = self.inputs[0].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'colordepth')
        set_prop_tex(properties, luxcore_name, 'depth', self.depth)
        set_prop_tex(properties, luxcore_name, 'kt', kt)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_math(pbrtv3_texture_node):
    """Math node with several math operations"""
    bl_idname = 'pbrtv3_texture_math_node'
    bl_label = 'Math'
    bl_icon = 'TEXTURE'

    input_settings = {
        'default': {
            0: ['Value 1', True], # slot index: [name, enabled]
            1: ['Value 2', True],
            2: ['', False]
        },
        'abs': {
            0: ['Value', True],
            1: ['', False],
            2: ['', False]
        },
        'clamp': {
            0: ['Value', True],
            1: ['', False],
            2: ['', False]
        },
        'mix': {
            0: ['Amount', True],
            1: ['Value 1', True],
            2: ['Value 2', True]
        }
    }

    def change_mode(self, context):
        mode = self.mode if self.mode in self.input_settings else 'default'
        current_settings = self.input_settings[mode]

        for i in current_settings.keys():
            self.inputs[i].name = current_settings[i][0]
            self.inputs[i].enabled = current_settings[i][1]

    mode_items = [
        ('scale', 'Multiply', ''),
        ('add', 'Add', ''),
        ('subtract', 'Subtract', ''),
        ('mix', 'Mix', 'Mix between two values/textures according to the amount (0 = use first value, 1 = use second value'),
        ('clamp', 'Clamp', 'Clamp the input so it is between min and max values'),
        ('abs', 'Absolute', 'Take the absolute value (remove minus sign)'),
    ]
    mode = bpy.props.EnumProperty(name='Mode', items=mode_items, default='scale', update=change_mode)

    mode_clamp_min = bpy.props.FloatProperty(name='Min', description='', default=0)
    mode_clamp_max = bpy.props.FloatProperty(name='Max', description='', default=1)

    clamp_output = bpy.props.BoolProperty(name='Clamp', default=False, description='Limit the output value to 0..1 range')

    def init(self, context):
        self.inputs.new('pbrtv3_float_socket', 'Value 1')
        self.inputs.new('pbrtv3_float_socket', 'Value 2')
        self.inputs.new('pbrtv3_float_socket', 'Value 3') # for mix mode
        self.inputs[2].enabled = False

        self.outputs.new('NodeSocketFloat', 'Value')

    def draw_label(self):
        # Use the name of the selected operation as displayed node name
        for elem in self.mode_items:
            if self.mode in elem:
                return elem[1]

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        layout.prop(self, 'mode', text='')

        if self.mode != 'clamp':
            layout.prop(self, 'clamp_output')

        if self.mode == 'clamp':
            layout.prop(self, 'mode_clamp_min')
            layout.prop(self, 'mode_clamp_max')

    # TODO: classic export

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        slot_0 = self.inputs[0].export_luxcore(properties)
        slot_1 = self.inputs[1].export_luxcore(properties)
        slot_2 = self.inputs[2].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', self.mode)

        if self.mode == 'abs':
            set_prop_tex(properties, luxcore_name, 'texture', slot_0)
        elif self.mode == 'clamp':
            set_prop_tex(properties, luxcore_name, 'texture', slot_0)
            set_prop_tex(properties, luxcore_name, 'min', self.mode_clamp_min)
            set_prop_tex(properties, luxcore_name, 'max', self.mode_clamp_max)
        elif self.mode == 'mix':
            set_prop_tex(properties, luxcore_name, 'amount', slot_0)
            set_prop_tex(properties, luxcore_name, 'texture1', slot_1)
            set_prop_tex(properties, luxcore_name, 'texture2', slot_2)
        else:
            set_prop_tex(properties, luxcore_name, 'texture1', slot_0)
            set_prop_tex(properties, luxcore_name, 'texture2', slot_1)

        if self.clamp_output and self.mode != 'clamp':
            clamp_name = create_luxcore_name(self, suffix='clamp')
            set_prop_tex(properties, clamp_name, 'type', 'clamp')
            set_prop_tex(properties, clamp_name, 'texture', luxcore_name)
            set_prop_tex(properties, clamp_name, 'min', 0)
            set_prop_tex(properties, clamp_name, 'max', 1)
            luxcore_name = clamp_name

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_colormix(pbrtv3_texture_node):
    """ColorMix node with several mixing methods"""
    bl_idname = 'pbrtv3_texture_colormix_node'
    bl_label = 'ColorMix'
    bl_icon = 'TEXTURE'

    input_settings = {
        'default': {
            1: ['Color 1', True], # slot index: [name, enabled]
            2: ['Color 2', True]
        },
        'abs': {
            1: ['Color', True],
            2: ['', False]
        },
        'clamp': {
            1: ['Color', True],
            2: ['', False]
        },
        'mix': {
            1: ['Color 1', True],
            2: ['Color 2', True]
        }
    }

    def change_mode(self, context):
        mode = self.mode if self.mode in self.input_settings else 'default'
        current_settings = self.input_settings[mode]

        for i in current_settings.keys():
            self.inputs[i].name = current_settings[i][0]
            self.inputs[i].enabled = current_settings[i][1]

    mode_items = [
        ('scale', 'Multiply', ''),
        ('add', 'Add', ''),
        ('subtract', 'Subtract', ''),
        ('mix', 'Mix', 'Mix between two values/textures according to the amount (0 = use first value, 1 = use second value'),
        ('clamp', 'Clamp', 'Clamp the input so it is between min and max values'),
        ('abs', 'Absolute', 'Take the absolute value (remove minus sign)'),
    ]
    mode = bpy.props.EnumProperty(name='Mode', items=mode_items, default='mix', update=change_mode)

    mode_clamp_min = bpy.props.FloatProperty(name='Min', description='', default=0)
    mode_clamp_max = bpy.props.FloatProperty(name='Max', description='', default=1)

    clamp_output = bpy.props.BoolProperty(name='Clamp', default=False, description='Limit the output value to 0..1 range')

    def init(self, context):
        self.inputs.new('pbrtv3_TF_amount_socket', 'Fac')
        self.inputs[0].default_value = 1
        self.inputs.new('pbrtv3_color_socket', 'Color 1')
        self.inputs[1].default_value = (0.04, 0.04, 0.04)
        self.inputs.new('pbrtv3_color_socket', 'Color 2')
        self.inputs[2].default_value = (0.7, 0.7, 0.7)

        self.outputs.new('NodeSocketColor', 'Color')

    def draw_label(self):
        # Use the name of the selected operation as displayed node name
        for elem in self.mode_items:
            if self.mode in elem:
                return elem[1]

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        layout.prop(self, 'mode', text='')
        layout.prop(self, 'clamp_output')

        if self.mode == 'clamp':
            layout.prop(self, 'mode_clamp_min')
            layout.prop(self, 'mode_clamp_max')

    # TODO: classic export

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        slot_0 = self.inputs[0].export_luxcore(properties)
        slot_1 = self.inputs[1].export_luxcore(properties)
        slot_2 = self.inputs[2].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', self.mode)

        if self.mode == 'abs':
            set_prop_tex(properties, luxcore_name, 'texture', slot_1)
        elif self.mode == 'clamp':
            set_prop_tex(properties, luxcore_name, 'texture', slot_1)
            set_prop_tex(properties, luxcore_name, 'min', self.mode_clamp_min)
            set_prop_tex(properties, luxcore_name, 'max', self.mode_clamp_max)
        elif self.mode == 'mix':
            set_prop_tex(properties, luxcore_name, 'amount', slot_0)
            set_prop_tex(properties, luxcore_name, 'texture1', slot_1)
            set_prop_tex(properties, luxcore_name, 'texture2', slot_2)
        else:
            set_prop_tex(properties, luxcore_name, 'texture1', slot_1)
            set_prop_tex(properties, luxcore_name, 'texture2', slot_2)

        if self.clamp_output:
            clamp_name = create_luxcore_name(self, suffix='clamp')
            set_prop_tex(properties, clamp_name, 'type', 'clamp')
            set_prop_tex(properties, clamp_name, 'texture', luxcore_name)
            set_prop_tex(properties, clamp_name, 'min', 0)
            set_prop_tex(properties, clamp_name, 'max', 1)
            luxcore_name = clamp_name

        if slot_0 != 1 and self.mode != 'mix':
            mix_name = create_luxcore_name(self, suffix='mix')
            set_prop_tex(properties, mix_name, 'type', 'mix')
            set_prop_tex(properties, mix_name, 'amount', slot_0)
            set_prop_tex(properties, mix_name, 'texture1', slot_1)
            set_prop_tex(properties, mix_name, 'texture2', luxcore_name)
            luxcore_name = mix_name

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_colorinvert(pbrtv3_texture_node):
    """ColorInvert node"""
    bl_idname = 'pbrtv3_texture_colorinvert_node'
    bl_label = 'Invert'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.inputs.new('pbrtv3_TF_amount_socket', 'Fac')
        self.inputs[0].default_value = 1
        self.inputs.new('pbrtv3_color_socket', 'Color')
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

    # TODO: classic export

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        fac = self.inputs[0].export_luxcore(properties)
        tex = self.inputs[1].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'subtract')
        set_prop_tex(properties, luxcore_name, 'texture1', [1, 1, 1])
        set_prop_tex(properties, luxcore_name, 'texture2', tex)

        if fac != 1:
            mix_name = create_luxcore_name(self, suffix='mix')
            set_prop_tex(properties, mix_name, 'type', 'mix')
            set_prop_tex(properties, mix_name, 'amount', fac)
            set_prop_tex(properties, mix_name, 'texture1', tex)
            set_prop_tex(properties, mix_name, 'texture2', luxcore_name)
            luxcore_name = mix_name

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_hsv(pbrtv3_texture_node):
    """Color at Depth node"""
    bl_idname = 'pbrtv3_texture_hsv_node'
    bl_label = 'Hue Saturation Value'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.inputs.new('pbrtv3_color_socket', 'Color')
        self.inputs.new('pbrtv3_float_limited_0_1_socket', 'Hue')
        self.inputs.new('pbrtv3_float_limited_0_2_socket', 'Saturation')
        self.inputs.new('pbrtv3_float_limited_0_2_socket', 'Value')

        self.inputs['Hue'].default_value = 0.5
        self.inputs['Saturation'].default_value = 1
        self.inputs['Value'].default_value = 1

        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        tex = self.inputs[0].export_luxcore(properties)
        hue = self.inputs[1].export_luxcore(properties)
        sat = self.inputs[2].export_luxcore(properties)
        val = self.inputs[3].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'hsv')
        set_prop_tex(properties, luxcore_name, 'texture', tex)
        set_prop_tex(properties, luxcore_name, 'hue', hue)
        set_prop_tex(properties, luxcore_name, 'saturation', sat)
        set_prop_tex(properties, luxcore_name, 'value', val)

        return luxcore_name

@PBRTv3Addon.addon_register_class
class ColorRampItem(bpy.types.PropertyGroup):
    offset = bpy.props.FloatProperty(name='Offset', default=0.0, min=0, max=1)
    value = bpy.props.FloatVectorProperty(name='', min=0, soft_max=1, subtype='COLOR')

@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_band(pbrtv3_texture_node):
    """Band texture node"""
    bl_idname = 'pbrtv3_texture_band_node'
    bl_label = 'Band'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    def init(self, context):
        self.inputs.new('pbrtv3_TF_amount_socket', 'Amount')

        self.outputs.new('NodeSocketColor', 'Color')

        # Add inital items
        item_0 = self.items.add()
        item_0.offset = 0
        item_0.value = (0, 0, 0)

        item_1 = self.items.add()
        item_1.offset = 1
        item_1.value = (1, 1, 1)

    def update_add(self, context):
        if len(self.items) == 1:
            new_offset = 1
            new_value = (1, 1, 1)
        else:
            max = None

            for item in self.items:
                if max is None or item.offset > max.offset:
                    max = item

            new_offset = max.offset
            new_value = max.value

        new_item = self.items.add()
        new_item.offset = new_offset
        new_item.value = new_value

        self['add_item'] = False

    def update_remove(self, context):
        if len(self.items) > 1:
            self.items.remove(len(self.items) - 1)

        self['remove_item'] = False

    add_item = bpy.props.BoolProperty(name='Add', description='Add an offset', default=False, update=update_add)
    remove_item = bpy.props.BoolProperty(name='Remove', description='Remove last offset', default=False, update=update_remove)
    items = bpy.props.CollectionProperty(type=ColorRampItem)

    interpolation_items = [
        ('linear', 'Linear', ''),
        ('cubic', 'Cubic', ''),
        ('none', 'None', ''),
    ]
    interpolation = bpy.props.EnumProperty(name='Interpolation Type', items=interpolation_items, default='linear',
                                           description='How to interpolate between the offset points')

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)
        layout.label('IN DEVELOPMENT!', icon='ERROR')
        layout.label('Do not use in production!', icon='ERROR')

        layout.prop(self, 'interpolation', expand=True)

        for item in self.items:
            split = layout.split(align=True, percentage=0.7)
            split.prop(item, 'offset', slider=True)
            split.prop(item, 'value')

        row = layout.row(align=True)
        row.prop(self, 'add_item', icon='ZOOMIN')

        subrow = row.row(align=True)
        subrow.enabled = len(self.items) > 1
        subrow.prop(self, 'remove_item', icon='ZOOMOUT')

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        amount = self.inputs[0].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'band')
        set_prop_tex(properties, luxcore_name, 'interpolation', self.interpolation)
        set_prop_tex(properties, luxcore_name, 'amount', amount)

        for index, item in enumerate(self.items):
            set_prop_tex(properties, luxcore_name, 'offset%i' % index, item.offset)
            set_prop_tex(properties, luxcore_name, 'value%i' % index, list(item.value))

        return luxcore_name

'''
@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_colorramp(pbrtv3_texture_node):
    """Colorramp texture node"""
    bl_idname = 'pbrtv3_texture_colorramp_node'
    bl_label = 'ColorRamp'
    bl_icon = 'TEXTURE'
    bl_width_min = 260

    #TODO: wait for the colorramp property to be exposed by Blender API before releasing this into the wild!

    # TODO 2: refactor it...

    @classmethod
    def poll(cls, node_tree):
        return node_tree is not None

    def get_fake_texture(self):
        name = self.name

        if name not in bpy.data.textures:
            fake_texture = bpy.data.textures.new(name=name, type='NONE')
            # Set fake user so the texture is not deleted on Blender close
            fake_texture.use_fake_user = True
            fake_texture.use_color_ramp = True
            # Set alpha from default 0 to 1
            fake_texture.color_ramp.elements[0].color[3] = 1.0

        return bpy.data.textures[name]

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        si = self.inputs.keys()
        so = self.outputs.keys()

        if not 'Amount' in si:
            self.inputs.new('pbrtv3_TF_amount_socket', 'Amount')

        if not 'Color' in so:
            self.outputs.new('NodeSocketColor', 'Color')

        fake_texture = self.get_fake_texture()
        layout.template_color_ramp(fake_texture, "color_ramp", expand=True)
'''


@PBRTv3Addon.addon_register_class
class pbrtv3_manipulate_3d_mapping_node(pbrtv3_texture_node):
    """Manipulate 3D texture coordinates node"""
    bl_idname = 'pbrtv3_manipulate_3d_mapping_node'
    bl_label = 'Manipulate 3D Mapping'
    bl_icon = 'TEXTURE'
    bl_width_min = 260

    translate = bpy.props.FloatVectorProperty(name='Translate', subtype='TRANSLATION', description='Moves the texture')
    rotate = bpy.props.FloatVectorProperty(name='Rotate', unit='ROTATION', default=(0, 0, 0), subtype='EULER',
                                           description='Rotates the texture')
    scale = bpy.props.FloatVectorProperty(name='Scale', default=(1.0, 1.0, 1.0), subtype='XYZ',
                                          description='Scales the texture')
    uniform_scale = bpy.props.FloatProperty(name='', default=1.0,
                                            description='Scales the texture uniformly along all axis')
    use_uniform_scale = bpy.props.BoolProperty(name='Uniform', default=False,
                                               description='Use the same scale value for all axis')

    def init(self, context):
        self.inputs.new('pbrtv3_coordinate_socket', mapping_3d_socketname)
        self.outputs.new('pbrtv3_coordinate_socket', mapping_3d_socketname)

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        if UsePBRTv3Core():
            row = layout.row()

            row.column().prop(self, 'translate')
            row.column().prop(self, 'rotate')

            scale_column = row.column()
            if self.use_uniform_scale:
                scale_column.label(text='Scale:')
                scale_column.prop(self, 'uniform_scale')
            else:
                scale_column.prop(self, 'scale')

            scale_column.prop(self, 'use_uniform_scale')

    def export_luxcore(self, properties):
        mapping_type, input_mapping = self.inputs[0].export_luxcore(properties)

        # create a location matrix
        tex_loc = mathutils.Matrix.Translation((self.translate))

        # create an identitiy matrix
        tex_sca = mathutils.Matrix()
        tex_sca[0][0] = self.uniform_scale if self.use_uniform_scale else self.scale[0]  # X
        tex_sca[1][1] = self.uniform_scale if self.use_uniform_scale else self.scale[1]  # Y
        tex_sca[2][2] = self.uniform_scale if self.use_uniform_scale else self.scale[2]  # Z

        # create a rotation matrix
        tex_rot0 = mathutils.Matrix.Rotation(radians(self.rotate[0]), 4, 'X')
        tex_rot1 = mathutils.Matrix.Rotation(radians(self.rotate[1]), 4, 'Y')
        tex_rot2 = mathutils.Matrix.Rotation(radians(self.rotate[2]), 4, 'Z')
        tex_rot = tex_rot0 * tex_rot1 * tex_rot2

        # combine transformations
        transformation = tex_loc * tex_rot * tex_sca

        # Transform input matrix
        output_mapping = input_mapping * transformation

        return [mapping_type, output_mapping]


@PBRTv3Addon.addon_register_class
class pbrtv3_manipulate_2d_mapping_node(pbrtv3_texture_node):
    """Manipulate 2D texture coordinates node"""
    bl_idname = 'pbrtv3_manipulate_2d_mapping_node'
    bl_label = 'Manipulate 2D Mapping'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    uscale = bpy.props.FloatProperty(name='U', default=1.0, min=-10000.0, max=10000.0)
    vscale = bpy.props.FloatProperty(name='V', default=1.0, min=-10000.0, max=10000.0)
    udelta = bpy.props.FloatProperty(name='U', default=0.0, min=-10000.0, max=10000.0)
    vdelta = bpy.props.FloatProperty(name='V', default=0.0, min=-10000.0, max=10000.0)

    def init(self, context):
        self.inputs.new('pbrtv3_transform_socket', mapping_2d_socketname)
        self.outputs.new('pbrtv3_transform_socket', mapping_2d_socketname)

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        if UsePBRTv3Core():
            layout.label('Scale:')
            row = layout.row(align=True)
            row.prop(self, 'uscale')
            row.prop(self, 'vscale')
            layout.label('Offset:')
            row = layout.row(align=True)
            row.prop(self, 'udelta')
            row.prop(self, 'vdelta')

    def export_luxcore(self, properties):
        mapping_type, input_uvscale, input_uvdelta = self.inputs[0].export_luxcore(properties)

        uvscale = [self.uscale,
                   self.vscale]

        output_uvscale = [a * b for a, b in zip(input_uvscale, uvscale)]

        uvdelta = [self.udelta,
                   self.vdelta]

        output_uvdelta = [a + b for a, b in zip(input_uvdelta, uvdelta)]

        return [mapping_type, output_uvscale, output_uvdelta]