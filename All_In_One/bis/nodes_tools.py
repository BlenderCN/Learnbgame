# Nikita Akimov
# interplanety@interplanety.org

from .node_manager import NodeManager


class NodesTools:

    @staticmethod
    def active_node(context):
        # returns currently active node in NODE_EDITOR window
        selected_node = None
        subtype = NodeManager.get_subtype(context=context)
        if subtype == 'ShaderNodeTree':
            subtype2 = NodeManager.get_subtype2(context=context)
            if subtype2 == 'OBJECT':
                if context.active_object and context.active_object.active_material:
                    selected_node = context.active_object.active_material.node_tree.nodes.active
            elif subtype2 == 'WORLD':
                selected_node = context.scene.world.node_tree.nodes.active
        elif subtype == 'CompositorNodeTree':
            if context.screen.scene.use_nodes:
                selected_node = context.area.spaces.active.node_tree.nodes.active
        if selected_node and hasattr(context.space_data, 'path'):
            for i in range(len(context.space_data.path) - 1):
                selected_node = selected_node.node_tree.nodes.active
        return selected_node

    @staticmethod
    def add_input_to_node(node, input_type, input_name):
        # add input to node
        if node.node_tree:
            node.node_tree.inputs.new(input_type, input_name)

    @staticmethod
    def add_output_to_node(node, output_type, output_name):
        # add output to node
        if node.node_tree:
            node.node_tree.outputs.new(output_type, output_name)
