# Nikita Akimov
# interplanety@interplanety.org

# -------------------------------------------------------------------------------
# Experimental. For use - enable in cfg.py
# -------------------------------------------------------------------------------

import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from bpy.types import Node
from bpy.props import FloatProperty
from bpy.utils import register_class, unregister_class


# node Constants
class ShaderNodeBISConstants(Node):
    bl_idname = 'ShaderNodeBISConstants'
    bl_label = 'BIS Contstants'
    bl_icon = 'INFO'

    # def update_value(self, context):
    #     self.outputs['PI'].default_value = self.pi
    #     self.update()
    #
    # pi = FloatProperty(
    #     default=3.14159265,
    #     update=lambda self, context: self.update_value(self, context)
    # )

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'PI')
        self.outputs['PI'].default_value = 3.14159265

    def update(self):
        # huck to update linked node - on update event check node links and update default_value of the linked node
        if self.outputs['PI']and self.outputs['PI'].is_linked:
            for node_input in self.outputs['PI'].links:
                if node_input.is_valid:
                    node_input.to_socket.node.inputs[node_input.to_socket.name].default_value = self.outputs['PI'].default_value

    # def draw_buttons(self, context, layout):
    #     layout.prop(self, 'pi', text='')

    def draw_label(self):
        return 'Constants'

    @classmethod
    def poll(cls, node_tree):
        return node_tree.bl_idname in ['ShaderNodeTree']


# node category
class ShaderNodeBISCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type in ['ShaderNodeTree']


node_categories = [
    ShaderNodeBISCategory('BIS Nodes', 'BIS Nodes', items=[
        NodeItem('ShaderNodeBISConstants'),
    ]),
]


def register():
    register_class(ShaderNodeBISConstants)
    register_node_categories('BIS_NODES', node_categories)


def unregister():
    unregister_node_categories('BIS_NODES')
    unregister_class(ShaderNodeBISConstants)
