# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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
from ..outputs.luxcore_api import ToValidPBRTv3CoreName, UsePBRTv3Core, set_prop_mat, set_prop_vol


class pbrtv3_node(bpy.types.Node):
    # This node is only for the Lux node-tree
    @classmethod
    def poll(cls, tree):
        return tree.bl_idname in ['pbrtv3_material_nodes', 'pbrtv3_volume_nodes_a']


class pbrtv3_texture_node(pbrtv3_node):
    pass


class pbrtv3_material_node(pbrtv3_node):
    pass


# For eliminating redundant volume definitions
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
    if not (material and material.pbrtv3_material and material.pbrtv3_material.nodetree):
        return None

    nodetree_name = material.pbrtv3_material.nodetree

    if not nodetree_name or nodetree_name not in bpy.data.node_groups:
        return None

    ntree = bpy.data.node_groups[nodetree_name]

    return find_node_in_nodetree(ntree, nodetype)


def find_node_in_volume(volume, nodetype):
    """
    Volume version of find_node()
    """
    if not (volume and volume.nodetree):
        return None

    nodetree_name = volume.nodetree

    if not nodetree_name:
        return None

    ntree = bpy.data.node_groups[nodetree_name]

    return find_node_in_nodetree(ntree, nodetype)


def find_node_in_nodetree(nodetree, nodetype):
    for node in nodetree.nodes:
        nt = getattr(node, "bl_idname", None)

        if nt == nodetype:
            return node


def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input

    return None


def get_linked_node(socket):
    if not socket.is_linked:
        return None
    return socket.links[0].from_node


def has_interior_volume(node):
    mat_output_node = find_node_in_nodetree(node.id_data, 'pbrtv3_material_output_node')
    if mat_output_node and mat_output_node.interior_volume:
        return True
    else:
        return False


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

# PBRTv3Core node UI functions (e.g. warning labels)

def warning_luxcore_node(layout):
    """
    Show a warning label if API mode is Classic (this node only works in PBRTv3Core mode)
    """
    if not UsePBRTv3Core():
        layout.label('No Classic support!', icon='ERROR')

def warning_classic_node(layout):
    """
    Show a warning label if API mode is PBRTv3Core (this node only works in Classic mode)
    """
    if UsePBRTv3Core():
        layout.label('No PBRTv3Core support!', icon='ERROR')

# PBRTv3Core node export functions

def create_luxcore_name(node, suffix=None, name=None):
    """
    Construct a unique name for the node to be used in the PBRTv3Core scene definitions.
    Note: node can also be a socket or anything else with an "id_data" attribute that points to the parent nodetree
    """
    if name is not None:
        # We got passed a valid PBRTv3Core name for the first node in the nodetree.
        # Use it without changes so switching from non-node to node materials works during viewport renders.
        return name

    name = node.name

    nodetree = node.id_data
    name_parts = [name, nodetree.name]

    if nodetree.library:
        name_parts.append(nodetree.library.name)

    if suffix:
        name_parts.append(suffix)

    return ToValidPBRTv3CoreName('_'.join(name_parts))

def create_luxcore_name_mat(node, name=None):
    return create_luxcore_name(node, 'mat', name)

def create_luxcore_name_vol(node, name=None):
    return create_luxcore_name(node, 'vol', name)

def export_fallback_material(properties, socket, name):
    # Black matte material
    luxcore_name = create_luxcore_name_mat(socket, name)
    set_prop_mat(properties, luxcore_name, 'type', 'matte')
    set_prop_mat(properties, luxcore_name, 'kd', [0, 0, 0])
    return luxcore_name

def export_fallback_volume(properties, socket, name):
    # Black clear volume
    luxcore_name = create_luxcore_name_vol(socket, name)
    set_prop_vol(properties, luxcore_name, 'type', 'clear')
    set_prop_vol(properties, luxcore_name, 'absorption', [100, 100, 100])
    return luxcore_name

def export_submat_luxcore(properties, socket, luxcore_exporter, name=None):
    """
    NodeSocketShader sockets cannot export themselves, so this function does it
    """
    node = get_linked_node(socket)

    if node is None:
        # Use a black material if socket is not linked
        print('WARNING: Unlinked material socket! Using a black material as fallback.')
        submat_name = export_fallback_material(properties, socket, name)
    else:
        submat_name = node.export_luxcore(properties, luxcore_exporter, name)

    return submat_name

def export_volume_luxcore(properties, socket, name=None):
    """
    NodeSocketShader sockets cannot export themselves, so this function does it
    """
    node = get_linked_node(socket)

    if node is None:
        # Use a black volume if socket is not linked
        print('WARNING: Unlinked volume socket! Using a black volume as fallback.')
        volume_name = export_fallback_volume(properties, socket, name)
    else:
        volume_name = node.export_luxcore(properties, name)

    return volume_name

def export_emission_luxcore(properties, luxcore_exporter, socket, parent_luxcore_name, is_volume_emission=False):
    """
    NodeSocketShader sockets cannot export themselves, so this function does it
    """
    node = get_linked_node(socket)

    if node is not None:
        node.export_luxcore(properties, luxcore_exporter, parent_luxcore_name, is_volume_emission)