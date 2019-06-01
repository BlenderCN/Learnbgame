# Nikita Akimov
# interplanety@interplanety.org

# --------------------------------------------------------------
# for older compatibility
# used for node groups version 1.4.1
# if there would no 1.4.1 nodegroups - all this file can be removed
# work with - node_node_group
# --------------------------------------------------------------


import bpy
import sys
from .NodeBase import NodeBase
from .NodeIO import *
from .NodeGIO import *
from .NodeShader import *
from .NodeCompositor import *


class NodeBaseShaderNodeGroup(NodeBase):
    @classmethod
    def node_to_json(cls, node):
        node_json = super(__class__, __class__).node_to_json(node)
        node_json['tree_type'] = bpy.context.area.spaces.active.tree_type
        node_json['nodes'] = []
        node_json['links'] = []
        node_json['GroupInput'] = []
        node_json['GroupOutput'] = []
        node_group_tree = node.node_tree
        node_json['name'] = node_group_tree.name
        # indexing
        node_group_tree_nodes = node_group_tree.nodes
        node_group_tree_node_indexed = []
        for current_node in node_group_tree_nodes:
            inputs = []
            for current_input in current_node.inputs:
                inputs.append(current_input)
            outputs = []
            for output in current_node.outputs:
                outputs.append(output)
            node_group_tree_node_indexed.append([current_node, inputs, outputs])
        # Nodes
        for current_node in node_group_tree_node_indexed:
            node_class = NodeBase
            if hasattr(sys.modules[__name__], 'NodeBase' + current_node[0].bl_idname):
                node_class = getattr(sys.modules[__name__], 'NodeBase' + current_node[0].bl_idname)
            current_node_json = node_class.node_to_json(current_node[0])
            for current_input in current_node[1]:
                io_name = 'IO' + current_input.bl_idname
                if current_node[0].bl_idname == 'NodeGroupInput' or current_node[0].bl_idname == 'NodeGroupOutput':
                    io_name = 'IO' + current_node[0].bl_idname
                io_class = IOCommon
                if hasattr(sys.modules[__name__], io_name):
                    io_class = getattr(sys.modules[__name__], io_name)
                current_node_json['inputs'].append(io_class.io_to_json(current_input))
            for output in current_node[2]:
                io_name = 'IO' + output.bl_idname
                if current_node[0].bl_idname == 'NodeGroupInput' or current_node[0].bl_idname == 'NodeGroupOutput':
                    io_name = 'IO' + current_node[0].bl_idname
                io_class = IOCommon
                if hasattr(sys.modules[__name__], io_name):
                    io_class = getattr(sys.modules[__name__], io_name)
                current_node_json['outputs'].append(io_class.io_to_json(output))
            node_json['nodes'].append(current_node_json)
        # GroupInputs
        for i, current_input in enumerate(node_group_tree.inputs):
            gio_class = GIOCommon
            if hasattr(sys.modules[__name__], 'GIO' + current_input.bl_socket_idname):
                gio_class = getattr(sys.modules[__name__], 'GIO' + current_input.bl_socket_idname)
            node_json['GroupInput'].append(gio_class.gio_to_json(current_input, node.inputs[i]))
        # GroupOutputs
        for output in node_group_tree.outputs:
            gio_class = GIOCommon
            if hasattr(sys.modules[__name__], 'GIO' + output.bl_socket_idname):
                gio_class = getattr(sys.modules[__name__], 'GIO' + output.bl_socket_idname)
            node_json['GroupOutput'].append(gio_class.gio_to_json(output))
        # Links
        for link in node_group_tree.links:
            from_node_index = 0
            from_node_output_index = 0
            to_node_index = 0
            to_node_input_index = 0
            node_index = 0
            for nodeData in node_group_tree_node_indexed:
                if link.from_node in nodeData:
                    from_node_index = node_index
                    if link.from_socket in nodeData[2]:
                        from_node_output_index = nodeData[2].index(link.from_socket)
                if link.to_node in nodeData:
                    to_node_index = node_index
                    if link.to_socket in nodeData[1]:
                        to_node_input_index = nodeData[1].index(link.to_socket)
                node_index += 1
            node_json['links'].append([from_node_index, from_node_output_index, to_node_index, to_node_input_index])
        return node_json

    @classmethod
    def json_to_node(cls, node_tree, node_json):
        current_node = super(__class__, __class__).json_to_node(node_tree, node_json)
        tree_type = node_json['tree_type'] if 'tree_type' in node_json else 'ShaderNodeTree'
        current_node.node_tree = bpy.data.node_groups.new(type=tree_type, name=node_json['name'])
        node_group_tree_node_indexed = []
        # GroupInputs
        for i, input_in_json in enumerate(node_json['GroupInput']):
            gio_class = GIOCommon
            if hasattr(sys.modules[__name__], 'GIO' + input_in_json['bl_type']):
                gio_class = getattr(sys.modules[__name__], 'GIO' + input_in_json['bl_type'])
            gio_class.json_to_gi(node_tree=current_node.node_tree,
                                 group_node=current_node,
                                 input_number=i,
                                 input_in_json=input_in_json)
        # GroupOutputs
        for output_in_json in node_json['GroupOutput']:
            gio_class = GIOCommon
            if hasattr(sys.modules[__name__], 'GIO' + output_in_json['bl_type']):
                gio_class = getattr(sys.modules[__name__], 'GIO' + output_in_json['bl_type'])
            gio_class.json_to_go(node_tree=current_node.node_tree,
                                 output_in_json=output_in_json)
        # Nodes
        for current_node_json in node_json['nodes']:
            node_class = NodeBase
            if hasattr(sys.modules[__name__], 'NodeBase' + current_node_json['bl_type']):
                node_class = getattr(sys.modules[__name__], 'NodeBase' + current_node_json['bl_type'])
            c_node = node_class.json_to_node(node_tree=current_node.node_tree, node_json=current_node_json)
            if c_node:
                # Node Inputs
                for input_number, nodeInputInJson in enumerate(current_node_json['inputs']):
                    if len(c_node.inputs) > input_number:
                        if nodeInputInJson:
                            io_class = IOCommon
                            if hasattr(sys.modules[__name__], 'IO' + nodeInputInJson['bl_type']):
                                io_class = getattr(sys.modules[__name__], 'IO' + nodeInputInJson['bl_type'])
                            if __class__.io_type_compatibility(c_node.inputs[input_number].bl_idname, nodeInputInJson['bl_type']):
                                io_class.json_to_i(node=c_node,
                                                   input_number=input_number,
                                                   input_in_json=nodeInputInJson)
                # Node Outputs
                for output_number, nodeOutputInJson in enumerate(current_node_json['outputs']):
                    if len(c_node.outputs) > output_number:
                        if nodeOutputInJson:
                            io_class = IOCommon
                            if hasattr(sys.modules[__name__], 'IO' + nodeOutputInJson['bl_type']):
                                io_class = getattr(sys.modules[__name__], 'IO' + nodeOutputInJson['bl_type'])
                            if __class__.io_type_compatibility(c_node.outputs[output_number].bl_idname, nodeOutputInJson['bl_type']):
                                io_class.json_to_o(node=c_node,
                                                   output_number=output_number,
                                                   output_in_json=nodeOutputInJson)
            node_group_tree_node_indexed.append(c_node)
        # Links
        for linkInJson in node_json['links']:
            # if nodes not None (may be None if node type is not exists - saved from future version of Blender
            if node_group_tree_node_indexed[linkInJson[0]] and node_group_tree_node_indexed[linkInJson[2]]:
                if linkInJson[1] <= len(node_group_tree_node_indexed[linkInJson[0]].outputs) - 1 and linkInJson[3] <= len(node_group_tree_node_indexed[linkInJson[2]].inputs) - 1:
                    from_output = node_group_tree_node_indexed[linkInJson[0]].outputs[linkInJson[1]]
                    to_input = node_group_tree_node_indexed[linkInJson[2]].inputs[linkInJson[3]]
                    current_node.node_tree.links.new(from_output, to_input)
        # Frames
        for node in current_node.node_tree.nodes:
            if node['parent_str']:
                parent_node = current_node.node_tree.nodes[node['parent_str']]
                node.parent = parent_node
                node.location += parent_node.location
        return current_node

    @staticmethod
    def io_type_compatibility(io_type_1, io_type_2):
        # for older compatibility SocketFloatFactor = SocketFloat (ex: MixRGB)
        compatible = ['NodeSocketFloat', 'NodeSocketFloatFactor']
        if io_type_1 == io_type_2 or (io_type_1 in compatible and io_type_2 in compatible):
            return True


class NodeBaseCompositorNodeGroup(NodeBaseShaderNodeGroup):
    pass