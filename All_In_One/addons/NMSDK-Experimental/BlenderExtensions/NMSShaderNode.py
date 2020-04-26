# Code inspired by https://blender.stackexchange.com/a/99003

# Heavy WIP!!!

import bpy
from bpy.props import BoolProperty  # noqa pylint: disable=import-error, no-name-in-module
from nodeitems_utils import (NodeItem, register_node_categories,  # noqa pylint: disable=import-error, no-name-in-module
                             unregister_node_categories)
from nodeitems_builtins import ShaderNewNodeCategory  # noqa pylint: disable=import-error, no-name-in-module


FLAGS = [('_F01_DIFFUSEMAP', 'Diffuse Map', 'Diffuse Map'),
         ('_F03_NORMALMAP', 'Normal Map', 'Normal Map'),
         ('_F21_VERTEXCOLOUR', 'Vertex Colour', 'Vertex Colour'),
         ('_F25_ROUGHNESS_MASK', 'Roughness Mask', 'Roughness Mask')]


class NMSShader(bpy.types.NodeCustomGroup):

    bl_name = 'NMSShader'
    bl_label = "No Man's Sky Uber Shader"

    # TODO: Not needed?
    # Return the list of valid operators
    def operators(self, context):
        _ = context.space_data.edit_tree
        list = [('_F01_DIFFUSEMAP', 'Diffuse Map', 'Diffuse Map'),
                ('_F03_NORMALMAP', 'Normal Map', 'Normal Map'),
                ('_F21_VERTEXCOLOUR', 'Vertex Colour', 'Vertex Colour'),
                ('_F25_ROUGHNESS_MASK', 'Roughness Mask', 'Roughness Mask')]
        return list

    # Manage the internal nodes to perform the chained operation - clear all
    # the nodes and build from scratch each time.
    def __nodetree_setup__(self):
        principled_BSDF = self.node_tree.nodes['Principled BSDF']

        if self.F01_DIFFUSEMAP_choice:
            diffuse_texture = self._add_diffuse_texture_choice()
            if self.F21_VERTEXCOLOUR_choice:
                self._add_vertex_colour_nodes()
            else:
                self._remove_vertex_colour_nodes()
                # Relink the texture input and BSDF shader
                self.node_tree.links.new(
                    principled_BSDF.inputs['Base Color'],
                    diffuse_texture.outputs['Color'])
        else:
            self._remove_diffuse_texture_choice()

    def _add_diffuse_texture_choice(self):
        # If the node already exists simply return it
        diffuse_texture = self.node_tree.nodes.get('Texture Image - Diffuse')
        if diffuse_texture:
            return diffuse_texture
        # Otherwise add it
        diffuse_texture = self.node_tree.nodes.new(type='ShaderNodeTexImage')
        diffuse_texture.name = diffuse_texture.label = 'Texture Image - Diffuse'  # noqa
        diffuse_texture.location = (-200, 300)
        return diffuse_texture

    def _remove_diffuse_texture_choice(self):
        # If the node doesn't exist don't do anything
        diffuse_texture = self.node_tree.nodes.get('Texture Image - Diffuse')
        if not diffuse_texture:
            return
        # Otherwise remove it
        for output in diffuse_texture.outputs:
            for link in output.links:
                self.node_tree.links.remove(link)
        self.node_tree.nodes.remove(diffuse_texture)

    def _add_vertex_colour_nodes(self):
        diffuse_texture = self.node_tree.nodes['Texture Image - Diffuse']
        principled_BSDF = self.node_tree.nodes['Principled BSDF']

        col_attribute = self.node_tree.nodes.new(type='ShaderNodeAttribute')
        col_attribute.attribute_name = 'Col'
        col_attribute.name = 'VertexColourAttribute'
        mix_colour = self.node_tree.nodes.new(type='ShaderNodeMixRGB')
        mix_colour.name = 'VertexColourMixer'
        self.node_tree.links.new(mix_colour.inputs['Color1'],
                                 diffuse_texture.outputs['Color'])
        self.node_tree.links.new(mix_colour.inputs['Color2'],
                                 col_attribute.outputs['Color'])
        self.node_tree.links.new(
            principled_BSDF.inputs['Base Color'],
            mix_colour.outputs['Color'])

    def _remove_vertex_colour_nodes(self):
        col_attribute = self.node_tree.nodes.get('VertexColourAttribute')
        mix_colour = self.node_tree.nodes.get('VertexColourMixer')
        if col_attribute or mix_colour:
            self.node_tree.nodes.remove(col_attribute)
            self.node_tree.nodes.remove(mix_colour)

    # A choice has changed
    def update_nodes(self, context):
        self.__nodetree_setup__()

    # The node properties - Operator (Add, Subtract, etc.) and number of input
    # sockets
    F01_DIFFUSEMAP_choice = BoolProperty(
        name='Has diffuse map',
        description='Whether material has a diffuse map.',
        default=False,
        update=update_nodes)
    F03_NORMALMAP_choice = BoolProperty(
        name='Has normal map',
        description='Whether material has a normal map.',
        default=False,
        update=update_nodes)
    F21_VERTEXCOLOUR_choice = BoolProperty(
        name='Has vertex colour data',
        description='Whether the material has vertex colour data.',
        default=False,
        update=update_nodes)
    F25_ROUGHNESS_MASK_choice = BoolProperty(
        name='Has roughness mask',
        description='Whether material has a roughness mask.',
        default=False,
        update=update_nodes)

    # Setup the node - setup the node tree and add the group Input and Output
    # nodes
    def init(self, context):
        self.node_tree = bpy.data.node_groups.new(self.bl_name,
                                                  'ShaderNodeTree')
        if hasattr(self.node_tree, 'is_hidden'):
            self.node_tree.is_hidden = True

        self.node_tree.nodes.new('NodeGroupOutput')

        principled_BSDF = self.node_tree.nodes.new(
            type='ShaderNodeBsdfPrincipled')
        principled_BSDF.location = (200, 150)
        principled_BSDF.inputs['Roughness'].default_value = 1.0

        self.node_tree.outputs.new("NodeSocketShader", "Value")

        self.node_tree.links.new(
            self.node_tree.nodes['Group Output'].inputs[0],
            principled_BSDF.outputs['BSDF'])

    # Draw the node components
    def draw_buttons(self, context, layout):
        row = layout.row()
        row.prop(self, 'F01_DIFFUSEMAP_choice', text='Diffuse Map')
        row = layout.row()
        row.prop(self, 'F03_NORMALMAP_choice', text='Normal Map')
        row = layout.row()
        row.prop(self, 'F21_VERTEXCOLOUR_choice', text='Vertex Colour')
        row = layout.row()
        row.prop(self, 'F25_ROUGHNESS_MASK_choice', text='Roughness Mask')

    # Copy
    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    # Free (when node is deleted)
    def free(self):
        bpy.data.node_groups.remove(self.node_tree, do_unlink=True)


def register():
    bpy.utils.register_class(NMSShader)
    newcatlist = [ShaderNewNodeCategory("SH_NEW_CUSTOM", "NMS Shader",
                                        items=[NodeItem("NMSShader")])]
    register_node_categories("NMS_SHADER", newcatlist)


def unregister():
    unregister_node_categories("NMS_SHADER")
    bpy.utils.unregister_class(NMSShader)
