# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

from bpy.types import Node

from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


class mitsuba_output_node(mitsuba_node):
    bl_width_min = 160
    mitsuba_nodetype = 'OUTPUT'


@MitsubaNodeTypes.register
class MtsNodeMaterialOutput(mitsuba_output_node, Node):
    '''Material output node'''
    bl_idname = 'MtsNodeMaterialOutput'
    bl_label = 'Material Output'
    bl_icon = 'MATERIAL'
    bl_width_min = 120
    shader_type_compat = {'OBJECT'}
    plugin_types = {'material_output'}

    def update(self):
        if 'Subsurface' in self.inputs and 'Interior Medium' in self.inputs:
            self.inputs['Interior Medium'].enabled = not self.inputs['Subsurface'].is_linked
            self.inputs['Subsurface'].enabled = not self.inputs['Interior Medium'].is_linked

    custom_inputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
        {'type': 'MtsSocketSubsurface', 'name': 'Subsurface'},
        {'type': 'MtsSocketMedium', 'name': 'Interior Medium'},
        {'type': 'MtsSocketMedium', 'name': 'Exterior Medium'},
        {'type': 'MtsSocketEmitter', 'name': 'Emitter'},
    ]

    def get_output_dict(self, export_ctx, material):
        mat_params = {}

        # start exporting that material...
        bsdf_node = self.inputs['Bsdf'].get_linked_node()

        if bsdf_node:
            mat_params.update({'bsdf': bsdf_node.get_bsdf_dict(export_ctx)})

        # export subsurface...
        subsurface_node = self.inputs['Subsurface'].get_linked_node()

        if subsurface_node:
            mat_params.update({'subsurface': subsurface_node.get_subsurface_dict(export_ctx)})

        # export interior medium...
        interior_node = self.inputs['Interior Medium'].get_linked_node()

        if interior_node and not subsurface_node:
            mat_params.update({'interior': interior_node.get_medium_dict(export_ctx)})

        # export emitter...
        emitter_node = self.inputs['Emitter'].get_linked_node()

        if emitter_node:
            mat_params.update({'emitter': emitter_node.get_emitter_dict(export_ctx)})

        return mat_params


@MitsubaNodeTypes.register
class MtsNodeLampOutput(mitsuba_output_node, Node):
    '''Lamp output node'''
    bl_idname = 'MtsNodeLampOutput'
    bl_label = 'Lamp Output'
    bl_icon = 'LAMP'
    bl_width_min = 120
    shader_type_compat = {'OBJECT'}
    plugin_types = {'lamp_output'}

    custom_inputs = [
        {'type': 'MtsSocketLamp', 'name': 'Lamp'},
        {'type': 'MtsSocketMedium', 'name': 'Exterior Medium'},
    ]

    def get_output_dict(self, export_ctx, lamp):
        lamp_params = {}

        lamp_node = self.inputs['Lamp'].get_linked_node()

        if lamp_node:
            lamp_params = lamp_node.get_lamp_dict(export_ctx)

        return lamp_params


@MitsubaNodeTypes.register
class MtsNodeWorldOutput(mitsuba_output_node, Node):
    '''World output node'''
    bl_idname = 'MtsNodeWorldOutput'
    bl_label = 'World Output'
    bl_icon = 'WORLD'
    bl_width_min = 120
    shader_type_compat = {'WORLD'}
    plugin_types = {'world_output'}

    custom_inputs = [
        {'type': 'MtsSocketEnvironment', 'name': 'Environment'},
        {'type': 'MtsSocketMedium', 'name': 'Exterior Medium'},
    ]

    def get_output_dict(self, export_ctx, world):
        world_params = {}

        world_node = self.inputs['Environment'].get_linked_node()

        if world_node:
            world_params = world_node.get_environment_dict(export_ctx)

        return world_params
