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

import bl_ui

from nodeitems_utils import NodeCategory, NodeItem

from ..nodes import MitsubaNodeTypes

space_node_editor = {}

data_source_items = [
    ('OBJECT', 'Object', 'OBJECT', 'OBJECT_DATA', 0),
    ('WORLD', 'World', 'WORLD', 'WORLD_DATA', 1),
]


def get_data_source_label_icon(data_type):
    for item in data_source_items:
        if item[0] == data_type:
            return item[1], item[3]

    return 'Object', 'OBJECT_DATA'


# Add shader type back to Node Editor header
def mts_nodetree_shader_type(self, context):
    snode = context.space_data

    if context.scene.render.engine == 'MITSUBA_RENDER' and snode.tree_type == 'MitsubaShaderNodeTree':
        data_source = space_node_editor.get(snode, 'OBJECT')
        label, icon = get_data_source_label_icon(data_source)

        self.layout.operator_menu_enum('node.mitsuba_node_tree_type', 'node_type', text=label, icon=icon)

bl_ui.space_node.NODE_HT_header.append(mts_nodetree_shader_type)


# Registered specially in init.py
class mitsuba_object_node_category(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MitsubaShaderNodeTree' and context.space_data.shader_type == 'OBJECT'


class mitsuba_world_node_category(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MitsubaShaderNodeTree' and context.space_data.shader_type == 'WORLD'


def gen_node_items(type_id, tree_type):
    items = []

    for nodetype in MitsubaNodeTypes.items():
        if nodetype.mitsuba_nodetype == type_id and tree_type in nodetype.shader_type_compat:
            items.append(NodeItem(nodetype.bl_idname))

    return items


mitsuba_shader_node_catagories = [
    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_INPUT", "Input", items=gen_node_items("INPUT", 'OBJECT')),
        # NodeItem("NodeGroupInput", poll=group_input_output_item_poll), ...maybe...

    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_OUTPUT", "Output", items=gen_node_items("OUTPUT", 'OBJECT')),
        # NodeItem("NodeGroupOutput", poll=group_input_output_item_poll),

    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_BSDF", "Bsdf", items=gen_node_items("BSDF", 'OBJECT')),
    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_TEXTURE", "Texture", items=gen_node_items("TEXTURE", 'OBJECT')),
    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_SUBSURFACE", "Subsurface", items=gen_node_items("SUBSURFACE", 'OBJECT')),
    # mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_MEDIUM", "Medium", items=gen_node_items("MEDIUM", 'OBJECT')),
    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_EMITTER", "Emitter", items=gen_node_items("EMITTER", 'OBJECT')),

    mitsuba_object_node_category("MITSUBA_SHADER_OBJECT_LAYOUT", "Layout", items=[
        NodeItem("NodeFrame"),
    ]),

    mitsuba_world_node_category("MITSUBA_SHADER_WORLD_INPUT", "Input", items=gen_node_items("INPUT", 'WORLD')),
    mitsuba_world_node_category("MITSUBA_SHADER_WORLD_OUTPUT", "Output", items=gen_node_items("OUTPUT", 'WORLD')),

    mitsuba_world_node_category("MITSUBA_SHADER_WORLD_ENVIRONMENT", "Environment", items=gen_node_items("ENVIRONMENT", 'WORLD')),

    mitsuba_world_node_category("MITSUBA_SHADER_WORLD_LAYOUT", "Layout", items=[
        NodeItem("NodeFrame"),
    ]),
]
