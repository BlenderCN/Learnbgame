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


def refresh_preview(cls, context):

    if context.material is not None:
        context.material.preview_render_type = context.material.preview_render_type

    if context.texture is not None:
        context.texture.type = context.texture.type


def node_tree_selector_draw(layout, context, idtype):
    context_data = {'material': context.material, 'lamp': context.lamp, 'world': context.world}

    try:
        id_data = context_data[idtype]
        layout.prop_search(id_data.mitsuba_nodes, "nodetree", context.scene.mitsuba_nodegroups, idtype, icon='NODETREE')

    except:
        return False

    ntree = id_data.mitsuba_nodes.get_node_tree()

    if not ntree:
        layout.operator('node.new_mitsuba_node_tree', icon='NODETREE').idtype = idtype
        return False

    return True


def draw_node_properties_recursive(layout, context, ntree, node, input_name=''):

    layout.context_pointer_set("node", node)
    layout.context_pointer_set("nodetree", ntree)

    def draw_props(layout, node, input_name):
        if input_name and input_name in node.inputs:
            input_sockets = [node.inputs[input_name]]

        else:
            input_sockets = node.inputs

            if hasattr(node, 'draw_buttons'):
                split = layout.split(0.35)
                col = split.column()
                col = split.column()
                node.draw_buttons(context, col)

        for socket in input_sockets:
            if not socket.enabled:
                continue

            layout.context_pointer_set("socket", socket)

            input_node = socket.get_linked_node()

            if input_node:
                icon = 'DISCLOSURE_TRI_DOWN' if socket.ui_open \
                    else 'DISCLOSURE_TRI_RIGHT'

                split = layout.split(0.35)

                row = split.row()
                row.prop(socket, "ui_open", icon=icon, text='',
                        icon_only=True, emboss=False)
                row.label('%s:' % socket.name)

                split.operator_menu_enum("node.add_mtsnode_%s" % socket.bl_custom_type.lower(),
                    "node_type", text=input_node.bl_label, icon='DOT')

                if socket.ui_open:
                    draw_node_properties_recursive(layout, context, ntree,
                        input_node, '')

            else:
                split = layout.split(0.35)
                split.label('%s:' % socket.name)

                if socket.bl_static_type not in {'SHADER', 'CUSTOM'} and hasattr(socket, 'default_value'):
                    row = split.row(align=True)
                    row.prop(socket, 'default_value', text='')
                    row.operator_menu_enum("node.add_mtsnode_%s" % socket.bl_custom_type.lower(),
                        "node_type", text='', icon='DOT')

                else:
                    split.operator_menu_enum("node.add_mtsnode_%s" % socket.bl_custom_type.lower(),
                        "node_type", text='None', icon='DOT')

    draw_props(layout, node, input_name)


def panel_node_draw(layout, context, id_type, output_type, input_name):
    ntree = id_type.mitsuba_nodes.get_node_tree()

    if not ntree:
        return False

    node = ntree.find_node(output_type)

    if not node:
        return False

    else:
        node_input = node.get_input_socket(input_name)

        if node_input.type == 'VALUE' and 'default_value' not in dir(node_input):
            # Seems like we don't have extended custom nodes and sockets
            # draw custom node panels
            draw_node_properties_recursive(layout, context, ntree, node, input_name)

        else:
            # Seems we have extended custom nodes and sockets
            # use template_node_view and hope it works ;D
            # draw_node_properties_recursive(layout, context, ntree, node, input_name)
            layout.template_node_view(ntree, node, node_input)

    return True
