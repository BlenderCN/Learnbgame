"""This module a set of useful node groups."""
import sys

import bpy


epsilon = sys.float_info.min


def node_group(name):
    """Simple decorator for caching node_groups"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            group = bpy.data.node_groups.get(name)

            if group:
                return group

            return func(*args, **kwargs)

        return wrapper
    return decorator


@node_group('Unlit BSDF')
def unlit_bsdf():
    group = bpy.data.node_groups.new(type='ShaderNodeTree', name='Unlit BSDF')
    group.inputs.new('NodeSocketColor', 'Color')
    group.outputs.new('NodeSocketShader', 'Shader')

    # Group input node
    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = 0, 0

    # Emission node
    emission_node = group.nodes.new('ShaderNodeEmission')
    emission_node.location = 200, 0

    # Group output node
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = 400, 0

    # Make links
    group.links.new(input_node.outputs[0], emission_node.inputs[0])
    group.links.new(emission_node.outputs[0], output_node.inputs[0])

    return group


@node_group('Lightmapped BSDF')
def lightmapped_bsdf():
    group = bpy.data.node_groups.new(type='ShaderNodeTree', name='Lightmapped BSDF')
    group.inputs.new('NodeSocketColor', 'Color')
    group.outputs.new('NodeSocketShader', 'Shader')

    # Group input node
    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = 0, 0

    # Emission node
    emission_node = group.nodes.new('ShaderNodeEmission')
    emission_node.location = 200, 0

    # Group output node
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = 400, 0

    # Make links
    group.links.new(input_node.outputs[0], emission_node.inputs[0])
    group.links.new(emission_node.outputs[0], output_node.inputs[0])

    return group


@node_group('Unlit Alpha Mask BSDF')
def unlit_alpha_mask_bsdf():
    group = bpy.data.node_groups.new(type='ShaderNodeTree', name='Unlit Alpha Mask BSDF')
    group.inputs.new('NodeSocketColor', 'Color')
    group.outputs.new('NodeSocketShader', 'Shader')

    # Group input node
    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = 0, 0

    # Create a color input node
    color_node = group.nodes.new('ShaderNodeRGB')
    color_node.label = 'Transparent Color'
    color_node.outputs[0].default_value = 0.346704, 0.104616, 0.0865, 1
    color_node.location = 0, -150

    # Create a subtraction node
    subtract_node = group.nodes.new('ShaderNodeVectorMath')
    subtract_node.operation = 'SUBTRACT'
    subtract_node.location = 200, 0

    # Create non-zero node
    non_zero_node = group.nodes.new('ShaderNodeGroup')
    non_zero_node.node_tree = non_zero()
    non_zero_node.location = 400, 0

    # Create a transparent shader
    transparent_node = group.nodes.new('ShaderNodeBsdfTransparent')
    transparent_node.location = 400, -200

    # Add an emission shader
    emission_node = group.nodes.new('ShaderNodeEmission')
    emission_node.location = 400, -350

    # Add a mix shader
    mix_node = group.nodes.new('ShaderNodeMixShader')
    mix_node.location = 600, 0

    # Group output node
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = 800, 0

    # Make links
    group.links.new(input_node.outputs[0], subtract_node.inputs[0])
    group.links.new(input_node.outputs[0], emission_node.inputs[0])
    group.links.new(color_node.outputs[0], subtract_node.inputs[1])
    group.links.new(subtract_node.outputs[0], non_zero_node.inputs[0])
    group.links.new(non_zero_node.outputs[0], mix_node.inputs[0])
    group.links.new(transparent_node.outputs[0], mix_node.inputs[1])
    group.links.new(emission_node.outputs[0], mix_node.inputs[2])
    group.links.new(mix_node.outputs[0], output_node.inputs[0])

    return group


@node_group('Scalar Multiply')
def scalar_multiply():
    group = bpy.data.node_groups.new(type='ShaderNodeTree', name='Scalar Multiply')
    group.inputs.new('NodeSocketVector', 'Vector')
    group.inputs.new('NodeSocketFloat', 'Scalar')

    # Group input node
    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = 0, 0

    # Separate XZY
    separate_xyz_node = group.nodes.new(type='ShaderNodeSeparateXYZ')
    separate_xyz_node.location = 200, 0

    # X-component multiplication
    multiply_x_component_node = group.nodes.new(type='ShaderNodeMath')
    multiply_x_component_node.operation = 'MULTIPLY'
    multiply_x_component_node.name = 'Multiply X-Component'
    multiply_x_component_node.location = 400, 0

    # Y-component multiplication
    multiply_y_component_node = group.nodes.new(type='ShaderNodeMath')
    multiply_y_component_node.operation = 'MULTIPLY'
    multiply_y_component_node.name = 'Multiply Y-Component'
    multiply_y_component_node.location = 400, -200

    # Z-component multiplication
    multiply_z_component_node = group.nodes.new(type='ShaderNodeMath')
    multiply_z_component_node.operation = 'MULTIPLY'
    multiply_z_component_node.name = 'Multiply Z-Component'
    multiply_z_component_node.location = 400, -400

    # Combine XYZ
    combine_xyz_node = group.nodes.new(type='ShaderNodeCombineXYZ')
    combine_xyz_node.location = 600, 0

    # Group output node
    group.outputs.new('NodeSocketVector', 'Vector')
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = 800, 0

    # Make links
    group.links.new(input_node.outputs['Vector'], separate_xyz_node.inputs[0])
    group.links.new(separate_xyz_node.outputs[0], multiply_x_component_node.inputs[0])
    group.links.new(input_node.outputs['Scalar'], multiply_x_component_node.inputs[1])
    group.links.new(separate_xyz_node.outputs[1], multiply_y_component_node.inputs[0])
    group.links.new(input_node.outputs['Scalar'], multiply_y_component_node.inputs[1])
    group.links.new(separate_xyz_node.outputs[1], multiply_z_component_node.inputs[0])
    group.links.new(input_node.outputs['Scalar'], multiply_z_component_node.inputs[1])
    group.links.new(multiply_x_component_node.outputs[0], combine_xyz_node.inputs[0])
    group.links.new(multiply_y_component_node.outputs[0], combine_xyz_node.inputs[1])
    group.links.new(multiply_z_component_node.outputs[0], combine_xyz_node.inputs[2])
    group.links.new(combine_xyz_node.outputs[0], output_node.inputs['Vector'])

    return group


@node_group('Non-Zero')
def non_zero():
    group = bpy.data.node_groups.new(type='ShaderNodeTree', name='Non-Zero')
    group.inputs.new('NodeSocketFloat', 'Value')
    group.inputs.new('NodeSocketFloat', 'Value')

    # Group input node
    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = 0, 0

    # Add an abs node
    abs_node = group.nodes.new('ShaderNodeMath')
    abs_node.operation = 'ABSOLUTE'
    abs_node.inputs[1].default_value = 0.0
    abs_node.location = 200, 0

    # Create an epsilon value node
    epsilon_node = group.nodes.new('ShaderNodeValue')
    epsilon_node.outputs[0].default_value = epsilon
    epsilon_node.label = 'Epsilon'
    epsilon_node.location = 200, -200

    # Add an add node
    add_node = group.nodes.new('ShaderNodeMath')
    add_node.operation = 'ADD'
    add_node.location = 400, 0

    # Add a divide node
    divide_node = group.nodes.new('ShaderNodeMath')
    divide_node.operation = 'DIVIDE'
    divide_node.location = 600, 0

    # Group output node
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = 800, 0

    # Make links
    group.links.new(input_node.outputs[0], abs_node.inputs[0])
    group.links.new(abs_node.outputs[0], add_node.inputs[0])
    group.links.new(abs_node.outputs[0], divide_node.inputs[0])
    group.links.new(epsilon_node.outputs[0], add_node.inputs[1])
    group.links.new(add_node.outputs[0], divide_node.inputs[1])
    group.links.new(divide_node.outputs[0], output_node.inputs[0])

    return group