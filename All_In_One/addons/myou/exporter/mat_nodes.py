
###
### This module converts a Material node tree into a JSON compatible
### representation to make it easy to export and use anywhere
###

import bpy
import json
from pprint import *
from array import array
from .util_convert import blender_matrix_to_gl

# To be overwritten by set(dir(output_node)) if present
common_attributes = {'__doc__', '__module__', '__slots__', 'bl_description',
'bl_height_default', 'bl_height_max', 'bl_height_min', 'bl_icon', 'bl_idname',
'bl_label', 'bl_rna', 'bl_static_type', 'bl_width_default', 'bl_width_max',
'bl_width_min', 'color', 'dimensions', 'draw_buttons', 'draw_buttons_ext',
'height', 'hide', 'input_template', 'inputs', 'internal_links',
'is_active_output', 'is_registered_node_type', 'label', 'location', 'mute',
'name', 'output_template', 'outputs', 'parent', 'poll', 'poll_instance',
'rna_type', 'select', 'shading_compatibility', 'show_options', 'show_preview',
'show_texture', 'socket_value_update', 'type', 'update', 'use_custom_color',
'width', 'width_hidden'}

converter_functions = {
    'Vector': list,
    'Euler': list,
    'Quaternion': list,
    'Color': list,
    'Matrix': blender_matrix_to_gl,
}

RAMP_SIZE = 256

def get_rgba_curve_hash(mapping, ramps):
    mapping.initialize()
    arr = array('B', [0]*RAMP_SIZE*4)
    # put pixels of the extremes to the extremes instead of in half a pixel
    pixel = 1/(RAMP_SIZE-1)
    pos = 0
    r,g,b,a = mapping.curves
    for i in range(RAMP_SIZE):
        i4 = i<<2
        arr[i4] = max(0, min(255, round(r.evaluate(pos)*255)))
        arr[i4+1] = max(0, min(255, round(g.evaluate(pos)*255)))
        arr[i4+2] = max(0, min(255, round(b.evaluate(pos)*255)))
        arr[i4+3] = max(0, min(255, round(a.evaluate(pos)*255)))
        pos += pixel
    ramp_hash = str(hash(arr.tobytes()))
    if ramp_hash not in ramps:
        ramps[ramp_hash] = arr.tolist() # json-compatible
    return ramp_hash

def get_xyz_curve_hash(mapping, ramps):
    # TODO: I think this is wrong because negative values are not represented
    mapping.initialize()
    arr = array('B', [0]*RAMP_SIZE*4)
    pixel = 1/RAMP_SIZE
    pos = pixel*0.5
    x,y,z = mapping.curves
    for i in range(RAMP_SIZE):
        i4 = i<<2
        pos2 = (pos)*2.0 - 1.0
        arr[i4] = max(0, min(255, round(((x.evaluate(pos2)))*255)))
        arr[i4+1] = max(0, min(255, round(((y.evaluate(pos2)))*255)))
        arr[i4+2] = max(0, min(255, round(((z.evaluate(pos2)))*255)))
        pos += pixel
    ramp_hash = str(hash(arr.tobytes()))
    if ramp_hash not in ramps:
        ramps[ramp_hash] = arr.tolist() # json-compatible
    return ramp_hash

def get_ramp_hash(ramp, ramps):
    arr = array('B', [0]*RAMP_SIZE*4)
    pixel = 1/RAMP_SIZE
    pos = pixel*0.5
    for i in range(RAMP_SIZE):
        i4 = i<<2
        r,g,b,a = ramp.evaluate(pos)
        arr[i4] = max(0, min(255, round(r*255)))
        arr[i4+1] = max(0, min(255, round(g*255)))
        arr[i4+2] = max(0, min(255, round(b*255)))
        arr[i4+3] = max(0, min(255, round(a*255)))
        pos += pixel
    ramp_hash = str(hash(arr.tobytes()))
    if ramp_hash not in ramps:
        ramps[ramp_hash] = arr.tolist() # json-compatible
    return ramp_hash


def unique_socket_name(socket):
    # If there's more than one socket with the same name,
    # each additional socket will have the index number
    sockets = socket.node.outputs if socket.is_output else socket.node.inputs
    idx = list(sockets).index(socket)
    name = socket.name
    if sockets[name] != sockets[idx]:
        name += '$'+str(idx)
    return name.replace(' ','_')

def export_node(node, ramps):
    out = {'type': node.type, 'inputs': {}}
    for input in node.inputs:
        inp = out['inputs'][unique_socket_name(input)] = {}
        socket_with_possible_value = input
        if input.links:
            link = input.links[0]
            while link and link.is_valid and link.from_node.type == 'REROUTE':
                links = link.from_node.inputs[0].links
                link = links[0] if links else None
            if link and link.is_valid:
                socket_with_possible_value = None
                inp['link'] = {
                    'node':link.from_node.name,
                    'socket':unique_socket_name(link.from_socket),
                }
                if link.from_node.type in ['VALUE','RGB']:
                    # This will make the input socket adopt the output of value/RGB nodes
                    socket_with_possible_value = link.from_socket
        if hasattr(socket_with_possible_value, 'default_value'):
            value = socket_with_possible_value.default_value
            if hasattr(value, '__iter__'):
                value = list(value)
            inp['value'] = value
            if 'link' in inp:
                del inp['link']
    properties = set(dir(node))-common_attributes
    if properties:
        out_props = out['properties'] = {}
    for prop in properties-{'node_tree'}:
        # Convert value to a JSON compatible type
        value = getattr(node, prop)
        value = getattr(value, 'name', value) # converts anything to its name
        if not isinstance(value, str) and hasattr(value, '__iter__'):
            value = list(value)
        converter_func = converter_functions.get(value.__class__.__name__, None)
        if converter_func:
            value = converter_func(value)
        if hasattr(value, 'bl_rna'):
            # print("Warning: No conversion possible for class",value.__class__.__name__)
            value = None
        out_props[prop] = value
        #print(' ', prop, repr(value))
    if node.type == 'GROUP':
        # we're embedding the group for now
        # (the better way is to have each group converted once)
        out_props['node_tree'] = export_nodes_of_group(node.node_tree, ramps)
    elif node.type == 'CURVE_RGB':
        out_props['ramp_name'] = get_rgba_curve_hash(node.mapping, ramps)
    elif node.type == 'CURVE_VEC':
        out_props['ramp_name'] = get_xyz_curve_hash(node.mapping, ramps)
    elif node.type == 'VALTORGB': # A.K.A. Color ramp
        out_props['ramp_name'] = get_ramp_hash(node.color_ramp, ramps)
    elif node.type == 'NORMAL':
        out['properties'] = {'normal': list(node.outputs['Normal'].default_value)}
    # pprint(out)
    return out

def export_nodes_of_group(node_tree, ramps):
    # if there is more than one output, the good one is last
    output_node = None
    nodes = {}
    for node in node_tree.nodes:
        if node.type == 'GROUP_OUTPUT':
            output_node = node
    for node in node_tree.nodes:
        if node.type != 'REROUTE':
            nodes[node.name] = export_node(node, ramps)
    tree = {'nodes': nodes, 'output_node_name': output_node.name if output_node else '',
            'group_name': node_tree.name,}
    return tree

OUTPUT_NODE_TYPE = {
    'BLENDER_RENDER': ['OUTPUT'],
    'BLENDER_GAME': ['OUTPUT'],
    'CYCLES': ['OUTPUT_MATERIAL', 'OUTPUT_WORLD'],
}
# TODO: Test if we can export blender internal from cycles
CROSS_COMPATIBLE_TYPES = ['OUTPUT_MATERIAL', 'OUTPUT_WORLD']

def make_nodeless_tree(mat):
    color = list(mat.diffuse_color)+[1.0]
    return {'material_name': 'Material',
     'nodes': {
        'Diffuse BSDF': {'inputs': {'Color': {'value': color},
                                    'Normal': {'value': [0.0, 0.0, 0.0]},
                                    'Roughness': {'value': 0.0}},
                         'type': 'BSDF_DIFFUSE'},
        'Material Output': {'inputs': {'Displacement': {'value': 0.0},
                                       'Surface': {'link': {'node': 'Diffuse '
                                                                    'BSDF',
                                                            'socket': 'BSDF'}},
                                       'Volume': {}},
                            'type': 'OUTPUT_MATERIAL'}},
     'output_node_name': 'Material Output',
     'ramps': {}}

def export_nodes_of_material(mat): # NOTE: mat can also be a world
    global common_attributes
    if not mat.use_nodes:
        return make_nodeless_tree(mat)
    # if there is more than one output, the good one is last
    output_node = None
    nodes = {}
    ramps = {}
    out_types = OUTPUT_NODE_TYPE[bpy.context.scene.render.engine]
    for node in mat.node_tree.nodes:
        if node.type in out_types:
            output_node = node
    # If we don't have output node of the selected render engine,
    # let's find one for other types
    if not output_node:
        for node in mat.node_tree.nodes:
            if node.type in CROSS_COMPATIBLE_TYPES:
                output_node = node
    if output_node:
        common_attributes = set(dir(output_node))
    for node in mat.node_tree.nodes:
        if node.type != 'REROUTE':
            nodes[node.name] = export_node(node, ramps)
    tree = {
        'material_name': mat.name,
        'nodes': nodes,
        'ramps': ramps,
        'output_node_name': output_node.name if output_node else ''
    }
    return tree

def is_blender_pbr_material(mat):
    # TODO: If a material doesn't have nodes, should it be detected
    # as cycles if most materials are cycles?
    if mat and mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type in ['OUTPUT_MATERIAL', 'OUTPUT_WORLD']:
                return True
    return False
