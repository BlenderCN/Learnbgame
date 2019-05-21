# Nikita Akimov
# interplanety@interplanety.org

import bpy
import sys
from .addon import Addon
from .node_common import NodeCommon
from .node_shader_cycles import *
from .node_compositor import *


class NodeShaderNodeGroup(NodeCommon):

    @classmethod
    def node_to_json(cls, node):
        # enumerate nodes in group
        __class__.enumerate(node)
        return super(__class__, cls).node_to_json(node)

    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['tree_type'] = bpy.context.area.spaces.active.tree_type
        node_json['nodes'] = []
        node_json['links'] = []
        node_json['name'] = node.node_tree.name
        node_json['BIS_addon_version'] = Addon.current_version()
        # nodes in group
        for current_node in node.node_tree.nodes:
            node_class = NodeCommon
            if hasattr(sys.modules[__name__], 'Node' + current_node.bl_idname):
                node_class = getattr(sys.modules[__name__], 'Node' + current_node.bl_idname)
            current_node_json = node_class.node_to_json(current_node)
            node_json['nodes'].append(current_node_json)
        # links
        for link in node.node_tree.links:
            from_node = link.from_node['BIS_node_id']
            to_node = link.to_node['BIS_node_id']
            # for group nodes, reroute and group inputs/output nodes - by number, for other nodes - by identifier
            if link.from_node.type in ['GROUP', 'GROUP_INPUT', 'GROUP_OUTPUT', 'REROUTE']:
                from_output = link.from_node.outputs[:].index(link.from_socket)
            else:
                from_output = link.from_socket.identifier
            if link.to_node.type in ['GROUP', 'GROUP_INPUT', 'GROUP_OUTPUT', 'REROUTE']:
                to_input = link.to_node.inputs[:].index(link.to_socket)
            else:
                to_input = link.to_socket.identifier
            node_json['links'].append([from_node, from_output, to_node, to_input])
        return node_json

    @classmethod
    def _json_to_node_spec(cls, node, node_json):
        node['BIS_addon_version'] = node_json['BIS_addon_version'] if 'BIS_addon_version' in node_json else Addon.node_group_first_version
        # Nodes
        for current_node_in_json in node_json['nodes']:
            node_class = NodeCommon
            if hasattr(sys.modules[__name__], 'Node' + current_node_in_json['bl_idname']):
                node_class = getattr(sys.modules[__name__], 'Node' + current_node_in_json['bl_idname'])
            node_class.json_to_node(node_tree=node.node_tree, node_json=current_node_in_json)
        # links
        for link_json in node_json['links']:
            from_node = __class__._node_by_bis_id(node.node_tree, link_json[0])
            to_node = __class__._node_by_bis_id(node.node_tree, link_json[2])
            # for group nodes and group inputs/output nodes - by number, for other nodes - by identifier
            if isinstance(link_json[1], str):
                from_output = __class__.output_by_identifier(from_node, link_json[1])
            else:
                from_output = from_node.outputs[link_json[1]]
            if isinstance(link_json[3], str):
                to_input = __class__.input_by_identifier(to_node, link_json[3])
            else:
                to_input = to_node.inputs[link_json[3]]
            if from_output and to_input:
                node.node_tree.links.new(from_output, to_input)
        # Frames
        for c_node in node.node_tree.nodes:
            if c_node['parent_str']:
                parent_node = node.node_tree.nodes[c_node['parent_str']]
                c_node.parent = parent_node
                c_node.location += parent_node.location

    @staticmethod
    def enumerate(node, start=0):
        # enumerates all nodes in the group
        # don't enumerate node group itself - not to loose if it is already enumerated by parent node group
        for current_node in node.node_tree.nodes:
            start += 1
            current_node['BIS_node_id'] = start
        return start

    @staticmethod
    def _node_by_bis_id(node_tree, bis_node_id):
        rez = None
        for node in node_tree.nodes:
            if 'BIS_node_id' in node and node['BIS_node_id'] == bis_node_id:
                rez = node
        return rez


class NodeCompositorNodeGroup(NodeShaderNodeGroup):
    pass
