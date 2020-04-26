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

from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty

from .. import MitsubaAddon

from ..nodes import MitsubaNodeTypes, MitsubaSocketTypes
from ..nodes.sockets import mitsuba_socket_definitions

from ..export.materials import blender_material_to_dict
from ..export.lamps import blender_lamp_to_nodes

from ..ui.space_node import space_node_editor, data_source_items


@MitsubaAddon.addon_register_class
class NODE_OT_mitsuba_node_tree_type(Operator):
    ''''''
    bl_idname = "node.mitsuba_node_tree_type"
    bl_label = "Mitsuba Nodetree Type"
    bl_description = "Mitsuba node tree type"

    node_type = EnumProperty(name="NodeTree Type",
        description='NodeTree type',
        items=data_source_items,
        default='OBJECT'
    )

    def execute(self, context):
        space_node_editor[context.space_data] = self.properties.node_type

        return {'FINISHED'}


@MitsubaAddon.addon_register_class
class NODE_OT_new_mitsuba_node_tree(Operator):
    ''''''
    bl_idname = "node.new_mitsuba_node_tree"
    bl_label = "Add Mitsuba Nodetree"
    bl_description = "Add a Mitsuba node tree"

    idtype = StringProperty(name="ID Type", default="material")

    def execute(self, context):
        idtype = self.properties.idtype
        context_data = {'material': context.material, 'lamp': context.lamp, 'world': context.world}
        idblock = context_data[idtype]

        ntree = bpy.data.node_groups.new(idblock.name, type='MitsubaShaderNodeTree')
        ntree.use_fake_user = True
        idblock.mitsuba_nodes.nodetree = ntree.name

        if idtype == 'material':
            sh_out = ntree.nodes.new('MtsNodeMaterialOutput')
            sh_out.location = 500, 400

            params = blender_material_to_dict(None, idblock)

            if params:
                if 'bsdf' in params:
                    shader = ntree.new_node_from_dict(params['bsdf'])

                    if shader:
                        shader.location = 200, 570

                        if 'Bsdf' in shader.outputs:
                            ntree.links.new(shader.outputs['Bsdf'], sh_out.inputs['Bsdf'])

                        if 'Emitter' in shader.outputs:
                            ntree.links.new(shader.outputs['Emitter'], sh_out.inputs['Emitter'])

        elif idtype == 'lamp':
            sh_out = ntree.nodes.new('MtsNodeLampOutput')
            sh_out.location = 500, 400

            shader = blender_lamp_to_nodes(ntree, idblock)

            if shader:
                shader.location = 200, 570
                ntree.links.new(shader.outputs['Lamp'], sh_out.inputs['Lamp'])

        elif idtype == 'world':
            sh_out = ntree.nodes.new('MtsNodeWorldOutput')
            sh_out.location = 500, 400

            shader = ntree.nodes.new('MtsNodeEnvironment_constant')
            shader.location = 200, 570

            ntree.links.new(shader.outputs['Environment'], sh_out.inputs['Environment'])

        return {'FINISHED'}


def get_type_items(cls, context):
    items = []
    category = ''

    for nodetype in MitsubaNodeTypes.items():
        if nodetype.mitsuba_nodetype != category:
            category = nodetype.mitsuba_nodetype

            if items and not items[len(items) - 1][0]:
                items[len(items) - 1] = ('', category.title(), '')

            else:
                items.append(('', category.title(), ''))

        compat_socks = []

        for output_socket in nodetype.custom_outputs:
            output_type = MitsubaSocketTypes.get(output_socket['type'])

            if output_type and output_type.bl_custom_type == cls.input_type:
                compat_socks.append(output_socket['name'])

        if compat_socks:
            if len(compat_socks) > 1:
                items.append(('', nodetype.bl_label,
                        ''))

                for sock in compat_socks:
                    items.append(('%s:%s' % (nodetype.bl_idname, sock), '            %s' % sock,
                            nodetype.bl_label))

            else:
                items.append(('%s:%s' % (nodetype.bl_idname, compat_socks[0]), nodetype.bl_label,
                        nodetype.bl_label))

    if items and not items[-1][0]:
        del items[-1]

    items.append(('', 'Link', ''))
    items.append(('REMOVE', 'Remove',
                    'Remove the node connected to this socket'))
    items.append(('DISCONNECT', 'Disconnect',
                    'Disconnect the node connected to this socket'))

    return items


def add_mtsnode_execute(cls, context):
    action = cls.properties.node_type
    if action == 'DEFAULT':
        return {'CANCELLED'}

    ntree = context.nodetree
    node = context.node
    socket = context.socket
    input_node = socket.get_linked_node()

    if action == 'REMOVE':
        ntree.nodes.remove(input_node)
        return {'FINISHED'}

    if action == 'DISCONNECT':
        ntree.unlink(socket)
        return {'FINISHED'}

    (new_type, output_socket) = action.split(':', 1)

    # add a new node to existing socket
    if input_node is None:
        newnode = ntree.nodes.new(new_type)
        newnode.location = node.location
        newnode.location[0] -= 300
        newnode.selected = False

        ntree.links.new(newnode.outputs[output_socket], socket)

    # replace input node with a new one
    else:
        newnode = ntree.nodes.new(new_type)
        ntree.links.new(newnode.outputs[output_socket], socket)
        newnode.location = input_node.location

        ntree.nodes.remove(input_node)

    return {'FINISHED'}


def create_node_operator(operator_type, params):
    '''
    For generating cycles-style ui menus to add new nodes,
    connected to a given input socket.
    '''
    MitsubaAddon.addon_register_class(type(
        'NODE_OT_add_mtsnode_%s' % operator_type.lower(),
        (Operator, ),
        {
            'bl_idname': 'node.add_mtsnode_%s' % operator_type.lower(),
            'bl_label': '%s socket' % params['label'],
            'bl_description': '%s socket' % params['description'],
            'input_type': StringProperty(
                default=operator_type,
            ),
            'get_type_items': get_type_items,
            'node_type': EnumProperty(name="Node Type",
                description='Node type to add to this socket',
                items=get_type_items),
            'execute': add_mtsnode_execute,
        }
    ))

for socket_type, socket_params in mitsuba_socket_definitions.items():
    create_node_operator(socket_type, socket_params)
