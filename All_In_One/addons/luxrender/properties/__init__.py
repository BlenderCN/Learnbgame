# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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

import bpy


class luxrender_node(bpy.types.Node):
    # This node is only for the Lux node-tree
    @classmethod
    def poll(cls, tree):
        return tree.bl_idname == 'luxrender_material_nodes'


class luxrender_texture_node(luxrender_node):
    pass


class luxrender_material_node(luxrender_node):
    pass


# # For eliminating redundant volume definitions
class ExportedVolumes(object):
    vol_names = []

    @staticmethod
    def list_exported_volumes(name):
        if name not in ExportedVolumes.vol_names:
            ExportedVolumes.vol_names.append(name)

    @staticmethod
    def reset_vol_list():
        ExportedVolumes.vol_names = []


def find_node(material, nodetype):
    #print('find_node: ', material, nodetype)
    if not (material and material.luxrender_material and material.luxrender_material.nodetree):
        return None

    nodetree = material.luxrender_material.nodetree
    #print('nodetree: ', nodetree)

    if not nodetree:
        return None

    ntree = bpy.data.node_groups[nodetree]
    #print('ntree: ', ntree)

    for node in ntree.nodes:
        #nt = getattr(node, "type", None)
        nt = getattr(node, "bl_idname", None)
        #print('node: ', node, nt, node.__class__.__name__)
        #print(dir(node))

        if nt == nodetype:
            return node

    return None


def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input

    return None


def get_linked_node(socket):
    if not socket.is_linked:
        return None
    return socket.links[0].from_node


def check_node_export_material(node):
    if not hasattr(node, 'export_material'):
        print('No export_material() for node: ' + node.bl_idname)
        return False
    return True


def check_node_export_texture(node):
    if not hasattr(node, 'export_texture'):
        print('No export_texture() for node: ' + node.bl_idname)
        return False
    return True


def check_node_get_paramset(node):
    if not hasattr(node, 'get_paramset'):
        print('No get_paramset() for node: ' + node.bl_idname)
        return False
    return True
