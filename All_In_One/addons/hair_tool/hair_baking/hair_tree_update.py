# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy


tree_node_inputs_cache = {}
'''It contains [NodeTreeName]{LinkId-hash: link_node_to_hash}'''

def get_socket_current_state(socket): #for inputs only....
    ''' Get socket linked state, linked input node, linked input socket'''
    if socket.is_linked:
        return (socket.is_linked, socket.links[0].from_node, socket.links[0].from_socket)
    return socket.is_linked
    #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].is_linked  - give socket node
    #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].node  - give socket node
    #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].links[0].
    #bpy.data.node_groups['NodeTree'].nodes['Input Texture'].outputs['R'].links[0].to_node, from_node, to_socket, from_socket etc.


def get_node_hash(node):  # cos it works with undo (unlinke hash(node))
    """Id of socket used for  data_cache"""
    return hash(node.id_data.name + node.name)


def get_link_hash(link):
    """Id of socket used for  data_cache"""
    return hash(link.id_data.name + link.to_node.name + link.to_socket.identifier)


#DONE: remove duplicates from nodes_for_update
#DONE: better compare old links to  new links...
#TODO: make sure to init input nodes (do this in input node itself - eg. check if cache exist...)

def ht_node_tree_update(NodeTree):
    '''Takes blender NodeTree type for updating.'''
    print('Runig ht - node tree update!   !')
    global tree_node_inputs_cache
    nodes_for_update = set()
    node_tree_name = NodeTree.name
    current_link_ids = [get_link_hash(link) for link in NodeTree.links]
    if node_tree_name not in tree_node_inputs_cache:
        nodes_for_update = set([node for node in NodeTree.nodes])
        tree_node_inputs_cache[node_tree_name]={}
    else:
        #find removed/added links compared to cached links
        map_node_id_to_node = { get_node_hash(node): node for node in NodeTree.nodes}
        map_link_id_to_link = { get_link_hash(link): link for link in NodeTree.links}

        cached_link_ids = list(tree_node_inputs_cache[node_tree_name].keys())
        current_links_set = set(current_link_ids)
        cached_links_set = set(cached_link_ids)
        added_links_ids = [link_id  for link_id in current_links_set - cached_links_set ]
        removed_links_ids = [link_id  for link_id in cached_links_set - current_links_set ]
        for added_link_id in added_links_ids:
            added_link = map_link_id_to_link[added_link_id]
            nodes_for_update.add(added_link.to_node)
        for removed_link_id in removed_links_ids:
            node_id = tree_node_inputs_cache[node_tree_name][removed_link_id]
            if node_id in map_node_id_to_node.keys(): #else node was probably also removed with link, so no need to update
                nodes_for_update.add(map_node_id_to_node[node_id])
        tree_node_inputs_cache[node_tree_name].clear()
    #cache current node tree
    for i,link in enumerate(NodeTree.links):
        link_id = current_link_ids[i]
        to_node_id = get_node_hash(link.to_node)
        tree_node_inputs_cache[node_tree_name][link_id] = to_node_id
    #execute modified nodes
    inputNodes = set()
    for node in nodes_for_update: 
        if node.bl_idname == 'InputTexture':
            inputNodes.add(node)
    nodes_for_update.difference(inputNodes) #input nodes should be always cached in theory
    for node in nodes_for_update:
        node.execute_node(bpy.context)    
