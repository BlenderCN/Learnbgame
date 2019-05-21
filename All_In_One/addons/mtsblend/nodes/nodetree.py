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

import math

import bpy

from bpy.types import NodeTree, Material, Lamp, World
from bpy.props import BoolProperty, CollectionProperty

from .. import MitsubaAddon
from ..nodes import MitsubaNodeManager, MitsubaNodeTypes
from ..properties.node import mitsuba_named_item
from ..ui.space_node import space_node_editor


def find_item(collection, name):
    for i in range(len(collection)):
        if collection[i].name == name:
            return i

    return -1


def get_item(collection, name):
    for item in collection:
        if item.name == name:
            return item

    return None


def remove_item(collection, name):
    target = find_item(collection, name)

    if target != -1:
        collection.remove(target)
        return True

    return False


def set_lamp_type(lamp, lamp_type):
    if bpy.data.lamps[lamp].type != lamp_type:
        bpy.data.lamps[lamp].type = lamp_type

    return bpy.data.lamps[lamp]


def update_lamp(emitter, lamp_name):
    if emitter.bl_idname == 'MtsNodeEmitter_area':
        lamp = set_lamp_type(lamp_name, 'AREA')
        lamp.size = emitter.width

        if emitter.shape == 'rectangle':
            lamp.size_y = emitter.height
            lamp.shape = 'RECTANGLE'

        else:
            lamp.shape = 'SQUARE'

    elif emitter.bl_idname == 'MtsNodeEmitter_point':
        lamp = set_lamp_type(lamp_name, 'POINT')
        lamp.shadow_soft_size = emitter.size

    elif emitter.bl_idname == 'MtsNodeEmitter_spot':
        lamp = set_lamp_type(lamp_name, 'SPOT')
        lamp.spot_size = emitter.cutoffAngle * math.pi * 2.0 / 180.0
        lamp.spot_blend = emitter.spotBlend
        lamp.show_cone = emitter.showCone

    elif emitter.bl_idname == 'MtsNodeEmitter_directional':
        set_lamp_type(lamp_name, 'SUN')

    elif emitter.bl_idname == 'MtsNodeEmitter_collimated':
        set_lamp_type(lamp_name, 'HEMI')


@MitsubaAddon.addon_register_class
class MitsubaShaderNodeTree(NodeTree):
    '''Mitsuba Shader Node Tree'''

    bl_idname = 'MitsubaShaderNodeTree'
    bl_label = 'Mitsuba Shader'
    bl_icon = 'MATERIAL'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MITSUBA_RENDER'

    #This function will set the current node tree to the one belonging to the active material (code orignally from Matt Ebb's 3Delight exporter)
    @classmethod
    def get_from_context(cls, context):
        snode = context.space_data
        data_source = space_node_editor.get(snode, 'OBJECT')

        if data_source == 'OBJECT':
            ob = context.active_object

            if ob and ob.type not in {'LAMP', 'CAMERA'}:
                mat = ob.active_material

                if mat is not None:
                    nt_name = mat.mitsuba_nodes.nodetree

                    if nt_name:
                        return bpy.data.node_groups[nt_name], mat, mat

            elif ob and ob.type == 'LAMP':
                la = ob.data
                nt_name = la.mitsuba_nodes.nodetree

                if nt_name:
                    return bpy.data.node_groups[nt_name], la, la

        else:
            wo = context.scene.world
            nt_name = wo.mitsuba_nodes.nodetree

            if nt_name:
                return bpy.data.node_groups[nt_name], wo, wo

        return None, None, None

    def new_node_from_dict(self, params, socket=None):
        try:
            nt = MitsubaNodeTypes.plugin_nodes[params['type']]
            node = self.nodes.new(nt.bl_idname)
            node.set_from_dict(self, params)

            if socket is not None:
                for out_sock in node.outputs:
                    if out_sock.bl_custom_type == socket.bl_custom_type:
                        self.links.new(out_sock, socket)
                        break

            return node

        except:
            print("Failed new_node_from_dict:")
            print(params)

        return None

    # This block updates the preview, when socket links change
    def update(self):
        self.refresh = True

    def update_context(self, context):
        if len(self.linked_lamps) > 0:
            node = self.find_node('MtsNodeLampOutput')
            emitter = node.inputs['Lamp'].get_linked_node()
            if emitter:
                for lamp in self.linked_lamps:
                    if lamp.name in bpy.data.lamps:
                        update_lamp(emitter, lamp.name)

                    else:
                        remove_item(self.linked_lamps, lamp.name)

    def acknowledge_connection(self, context):
        while self.refresh:
            if not MitsubaNodeManager.locked:
                self.update_context(context)

            self.refresh = False
            break

    refresh = BoolProperty(name='Links Changed', default=False, update=acknowledge_connection)

    linked_materials = CollectionProperty(type=mitsuba_named_item, name='Linked Materials')
    linked_lamps = CollectionProperty(type=mitsuba_named_item, name='Linked Lamps')
    linked_data = CollectionProperty(type=mitsuba_named_item, name='Linked Data')

    def get_linked_list(self, id_data):
        if isinstance(id_data, Material):
            return getattr(self, 'linked_materials')

        elif isinstance(id_data, Lamp):
            return getattr(self, 'linked_lamps')

        else:
            return getattr(self, 'linked_data')

    def append_connection(self, id_data):
        linked_list = self.get_linked_list(id_data)
        name = id_data.name

        if get_item(linked_list, name):
            print('%s already connected with %s...' % (name, self.name))
            return

        print('%s connected to %s...' % (name, self.name))
        linked_list.add().name = name

    def remove_connection(self, id_data):
        linked_list = self.get_linked_list(id_data)
        name = id_data.mitsuba_nodes.prev_name

        if not remove_item(linked_list, name):
            print('%s not found connected to %s...' % (name, self.name))
            return

        print('%s removed from %s...' % (name, self.name))

    def find_node(self, nodetype):
        for node in self.nodes:
            nt = getattr(node, "bl_idname", None)

            if nt == nodetype:
                return node

        return None

    def get_nodetree_dict(self, export_ctx, id_data):
        output_node = None
        params = {}

        if isinstance(id_data, Material) or isinstance(id_data, NodeTree):
            output_node = self.find_node('MtsNodeMaterialOutput')
            export_id = self

        elif isinstance(id_data, Lamp):
            output_node = self.find_node('MtsNodeLampOutput')
            export_id = id_data

        elif isinstance(id_data, World):
            output_node = self.find_node('MtsNodeWorldOutput')
            export_id = id_data

        if output_node:
            params = output_node.get_output_dict(export_ctx, export_id)

        return params

    def unlink(self, socket):
        if self.links and socket.is_linked:
            link = next((l for l in self.links if l.to_socket == socket), None)
            self.links.remove(link)
