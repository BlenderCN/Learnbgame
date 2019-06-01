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

import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty

from .. import MitsubaAddon

from ..extensions_framework import declarative_property_group


@MitsubaAddon.addon_register_class
class mitsuba_named_item(PropertyGroup):
    name = StringProperty(name='Nodegroup Name', default='')


@MitsubaAddon.addon_register_class
class mitsuba_nodes(declarative_property_group):
    """
    Properties related to exporter and scene testing
    """

    ef_attach_to = ['Material', 'Lamp', 'World']

    def list_texture_nodes(self, context):
        enum_list = []

        ntree = self.get_node_tree()
        if ntree:
            for node in ntree.nodes:
                if node.mitsuba_nodetype == 'TEXTURE':
                    enum_list.append((node.name, node.name, node.name))

        if len(enum_list) == 0:
            enum_list = [('', 'No Textures Found!', '')]

        return enum_list

    def update_nodetree_connection(self, context):
        try:
            if self.prev_nodetree:
                bpy.data.node_groups[self.prev_nodetree].remove_connection(self.id_data)
                self.prev_nodetree = ''
                self.prev_name = ''

        except:
            pass

        try:
            if self.nodetree:
                bpy.data.node_groups[self.nodetree].append_connection(self.id_data)
                self.prev_nodetree = self.nodetree
                self.prev_name = self.id_data.name

        except:
            pass

        if self.nodetree != self.prev_nodetree:
            print('Something went wrong while connecting % to nodetree %s' % (self.id_data.name, self.nodetree))

    controls = []

    visibility = {}

    properties = [
        {
            'attr': 'nodetree',
            'type': 'string',
            'name': 'Node Tree',
            'description': 'Node tree',
            'default': '',
            'update': update_nodetree_connection,
        },
        {
            'attr': 'prev_nodetree',
            'type': 'string',
            'name': 'Previous Node Tree',
            'description': 'Previous Node tree',
            'default': '',
        },
        {
            'attr': 'prev_name',
            'type': 'string',
            'name': 'Previous Name',
            'description': 'Previous Name',
            'default': '',
        },
        {
            'type': 'enum',
            'attr': 'texture_node',
            'name': 'Texture Node',
            'items': list_texture_nodes,
        },
    ]

    def get_node_tree(self):
        if self.nodetree:
            try:
                return bpy.data.node_groups[self.nodetree]

            except:
                pass

        return None


@MitsubaAddon.addon_register_class
class mitsuba_nodegroups(declarative_property_group):
    """
    Properties related to exporter and scene testing
    """

    ef_attach_to = ['Scene']

    controls = []

    visibility = {}

    properties = [
        {
            'attr': 'material',
            'type': 'collection',
            'ptype': mitsuba_named_item,
            'name': 'Material NodeTree list',
        },
        {
            'attr': 'lamp',
            'type': 'collection',
            'ptype': mitsuba_named_item,
            'name': 'Lamp NodeTree list',
        },
        {
            'attr': 'world',
            'type': 'collection',
            'ptype': mitsuba_named_item,
            'name': 'World NodeTree list',
        },
        {
            'attr': 'medium',
            'type': 'collection',
            'ptype': mitsuba_named_item,
            'name': 'Medium NodeTree list',
        },
    ]

    def refresh(self):
        self.material.clear()
        self.lamp.clear()
        self.world.clear()
        self.medium.clear()

        for nodegroup in bpy.data.node_groups:
            if nodegroup is None or nodegroup.bl_idname != 'MitsubaShaderNodeTree':
                continue

            material = nodegroup.find_node('MtsNodeMaterialOutput')
            if material:
                self.material.add().name = nodegroup.name
                interior = material.inputs['Interior Medium'].get_linked_node()
                if interior and interior.bl_idname != 'MtsNodeMedium_reference':
                    self.medium.add().name = nodegroup.name

            if nodegroup.find_node('MtsNodeLampOutput'):
                self.lamp.add().name = nodegroup.name

            if nodegroup.find_node('MtsNodeWorldOutput'):
                self.world.add().name = nodegroup.name
