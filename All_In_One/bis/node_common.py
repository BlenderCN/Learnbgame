# Nikita Akimov
# interplanety@interplanety.org

# Base Node classes

import sys
import bpy
from . import cfg
from .JsonEx import JsonEx
from .node_io import *


# Node
class NodeCommon:
    @classmethod
    def node_to_json(cls, node):
        # base node specification
        node_json = {
            'type': node.type,
            'bl_idname': node.bl_idname,
            'name': node.name,
            'label': node.label,
            'hide': node.hide,
            'location': JsonEx.vector2_to_json(node.location),
            'width': node.width,
            'height': node.height,
            'use_custom_color': node.use_custom_color,
            'color': JsonEx.color_to_json(node.color),
            'parent': node.parent.name if node.parent else '',
            'inputs': [],
            'outputs': [],
            'BIS_node_id': node['BIS_node_id'] if 'BIS_node_id' in node else None
        }
        # node inputs
        for c_input in node.inputs:
            io_name = 'NodeIO' + c_input.bl_idname
            io_class = NodeIOCommon
            if hasattr(sys.modules[__name__], io_name):
                io_class = getattr(sys.modules[__name__], io_name)
            node_json['inputs'].append(io_class.input_to_json(c_input))
        # node outputs
        for c_output in node.outputs:
            io_name = 'NodeIO' + c_output.bl_idname
            io_class = NodeIOCommon
            if hasattr(sys.modules[__name__], io_name):
                io_class = getattr(sys.modules[__name__], io_name)
            node_json['outputs'].append(io_class.output_to_json(c_output))
        # for current node specification
        cls._node_to_json_spec(node_json, node)
        return node_json

    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        # extend to current node data
        pass

    @classmethod
    def json_to_node(cls, node_tree, node_json):
        current_node = None
        try:
            # current node type may not exists - if node saved from future version of Blender
            current_node = node_tree.nodes.new(type=node_json['bl_idname'])
            if current_node.type == 'GROUP':
                tree_type = node_json['tree_type'] if 'tree_type' in node_json else 'ShaderNodeTree'
                current_node.node_tree = bpy.data.node_groups.new(type=tree_type, name=node_json['name'])
        except Exception as exception:
            if cfg.show_debug_err:
                print(repr(exception))
        if current_node:
            # base node specification
            current_node.name = node_json['name']
            current_node.label = node_json['label']
            current_node.hide = node_json['hide']
            JsonEx.vector2_from_json(current_node.location, node_json['location'])
            current_node.width = node_json['width']
            current_node.height = node_json['height']
            current_node.use_custom_color = node_json['use_custom_color']
            JsonEx.color_from_json(current_node.color, node_json['color'])
            current_node['parent_str'] = node_json['parent'] if 'parent' in node_json else ''
            current_node['BIS_node_id'] = node_json['BIS_node_id'] if 'BIS_node_id' in node_json else None
            # node inputs
            for input_number, input_json in enumerate(node_json['inputs']):
                if current_node.type == 'GROUP':
                    # for group - generate new input
                    current_node.node_tree.inputs.new(type=input_json['bl_idname'], name=input_json['name'])     # NodeSocketInterfaceXXX
                    current_input = current_node.inputs[-1]   # NodeSocketXXX
                else:
                    # for other nodes - use existed input
                    if current_node.bl_idname in ['NodeGroupInput', 'NodeGroupOutput']:
                        # for group inputs/outputs - by number
                        current_input = current_node.inputs[input_number]
                    else:
                        # for other nodes - by identifier
                        current_input = __class__.input_by_identifier(current_node, input_json['identifier'])
                if current_input:
                    io_class = NodeIOCommon
                    if hasattr(sys.modules[__name__], 'NodeIO' + input_json['bl_idname']):
                        io_class = getattr(sys.modules[__name__], 'NodeIO' + input_json['bl_idname'])
                    io_class.json_to_i(node_input=current_input, input_json=input_json)
            # node outputs
            for output_number, output_json in enumerate(node_json['outputs']):
                if current_node.type == 'GROUP':
                    # for group - generate new output
                    current_node.node_tree.outputs.new(type=output_json['bl_idname'], name=output_json['name'])     # NodeSocketInterfaceXXX
                    current_output = current_node.outputs[-1]   # NodeSocketXXX
                else:
                    # for other nodes - use existed input
                    if current_node.bl_idname in ['NodeGroupInput', 'NodeGroupOutput']:
                        # for group inputs/outputs - by number
                        current_output = current_node.outputs[output_number]
                    else:
                        # for other nodes - by identifier
                        current_output = __class__.output_by_identifier(current_node, output_json['identifier'])
                if current_output:
                    io_class = NodeIOCommon
                    if hasattr(sys.modules[__name__], 'NodeIO' + output_json['bl_idname']):
                        io_class = getattr(sys.modules[__name__], 'NodeIO' + output_json['bl_idname'])
                    io_class.json_to_o(node_output=current_output, output_json=output_json)
            # for current node specification
            cls._json_to_node_spec(current_node, node_json)
        return current_node

    @classmethod
    def _json_to_node_spec(cls, node, node_json):
        # extend to current node data
        pass

    @classmethod
    def input_by_identifier(cls, node, identifier):
        # returns input by its identifier
        rez = None
        if identifier:
            input_with_identifier = [node_input for node_input in node.inputs[:] if node_input.identifier == identifier]
            if input_with_identifier:
                rez = input_with_identifier[0]
        return rez

    @classmethod
    def output_by_identifier(cls, node, identifier):
        # returns output by its identifier
        rez = None
        if identifier:
            output_with_identifier = [node_output for node_output in node.outputs[:] if node_output.identifier == identifier]
            if output_with_identifier:
                rez = output_with_identifier[0]
        return rez


# Node TextureMapping
class TMCommon:
    @classmethod
    def tm_to_json(cls, tm):
        return {
            'vector_type': tm.vector_type,
            'translation': JsonEx.vector3_to_json(tm.translation),
            'rotation': JsonEx.vector3_to_json(tm.rotation),
            'scale': JsonEx.vector3_to_json(tm.scale),
            'min': JsonEx.vector3_to_json(tm.min),
            'max': JsonEx.vector3_to_json(tm.max),
            'use_min': tm.use_min,
            'use_max': tm.use_max,
            'mapping_x': tm.mapping_x,
            'mapping_y': tm.mapping_y,
            'mapping_z': tm.mapping_z,
            'mapping': tm.mapping
        }

    @classmethod
    def json_to_tm(cls, node, tm_in_json):
        node.texture_mapping.vector_type = tm_in_json['vector_type']
        JsonEx.vector3_from_json(node.texture_mapping.translation, tm_in_json['translation'])
        JsonEx.vector3_from_json(node.texture_mapping.rotation, tm_in_json['rotation'])
        JsonEx.vector3_from_json(node.texture_mapping.scale, tm_in_json['scale'])
        JsonEx.vector3_from_json(node.texture_mapping.min, tm_in_json['min'])
        JsonEx.vector3_from_json(node.texture_mapping.max, tm_in_json['max'])
        node.texture_mapping.use_min = tm_in_json['use_min']
        node.texture_mapping.use_max = tm_in_json['use_max']
        node.texture_mapping.mapping_x = tm_in_json['mapping_x']
        node.texture_mapping.mapping_y = tm_in_json['mapping_y']
        node.texture_mapping.mapping_z = tm_in_json['mapping_z']
        node.texture_mapping.mapping = tm_in_json['mapping']


# Node ImageUser
class IUCommon:
    @classmethod
    def iu_to_json(cls, iu):
        return {
            'use_auto_refresh': iu.use_auto_refresh,
            'frame_current': iu.frame_current,
            'use_cyclic': iu.use_cyclic,
            'frame_duration': iu.frame_duration,
            'frame_offset': iu.frame_offset,
            'frame_start': iu.frame_start,
            'fields_per_frame': iu.fields_per_frame
        }

    @classmethod
    def json_to_iu(cls, node, iu_in_json):
        node.image_user.use_auto_refresh = iu_in_json['use_auto_refresh']
        node.image_user.frame_current = iu_in_json['frame_current']
        node.image_user.use_cyclic = iu_in_json['use_cyclic']
        node.image_user.frame_duration = iu_in_json['frame_duration']
        node.image_user.frame_offset = iu_in_json['frame_offset']
        node.image_user.frame_start = iu_in_json['frame_start']
        node.image_user.fields_per_frame = iu_in_json['fields_per_frame']


# Node ColorMapping
class CMCommon:
    @classmethod
    def cm_to_json(cls, cm):
        return {
            'use_color_ramp': cm.use_color_ramp,
            'brightness': cm.brightness,
            'contrast': cm.contrast,
            'saturation': cm.saturation,
            'blend_type': cm.blend_type,
            'blend_color': JsonEx.color_to_json(cm.blend_color),
            'blend_factor': cm.blend_factor,
            'color_ramp': NodeColorRamp.cr_to_json(cm.color_ramp)
        }

    @classmethod
    def json_to_cm(cls, node, cm_in_json):
        node.color_mapping.use_color_ramp = cm_in_json['use_color_ramp']
        node.color_mapping.brightness = cm_in_json['brightness']
        node.color_mapping.contrast = cm_in_json['contrast']
        node.color_mapping.saturation = cm_in_json['saturation']
        node.color_mapping.blend_type = cm_in_json['blend_type']
        JsonEx.color_from_json(node.color_mapping.blend_color, cm_in_json['blend_color'])
        node.color_mapping.blend_factor = cm_in_json['blend_factor']
        NodeColorRamp.json_to_cr(node.color_mapping.color_ramp, cm_in_json['color_ramp'])


# Node ColorRamp
class NodeColorRamp:
    @classmethod
    def cr_to_json(cls, cr):
        rez = {
            'interpolation': cr.interpolation,
            'hue_interpolation': cr.hue_interpolation,
            'color_mode': cr.color_mode,
            'elements': []
        }
        for element in cr.elements:
            rez['elements'].append({
                'color': JsonEx.prop_array_to_json(element.color),
                'alpha': element.alpha,
                'position': element.position
            })
        return rez

    @classmethod
    def json_to_cr(cls, color_ramp, cr_in_json):
        color_ramp.interpolation = cr_in_json['interpolation']
        color_ramp.hue_interpolation = cr_in_json['hue_interpolation']
        color_ramp.color_mode = cr_in_json['color_mode']
        for i, element in enumerate(cr_in_json['elements']):
            if len(color_ramp.elements) <= i:
                color_ramp.elements.new(element['position'])
            color_ramp.elements[i].position = element['position']
            color_ramp.elements[i].alpha = element['alpha']
            JsonEx.prop_array_from_json(color_ramp.elements[i].color, element['color'])


# do not use next classes, use them from bl_types_conversion !!!

# Node Curve Mapping (mapping)
class CurveMapping:
    @classmethod
    def cum_to_json(cls, cum):
        rez = {
            'use_clip': cum.use_clip,
            'clip_min_x': cum.clip_min_x,
            'clip_min_y': cum.clip_min_y,
            'clip_max_x': cum.clip_max_x,
            'clip_max_y': cum.clip_max_y,
            'black_level': JsonEx.color_to_json(cum.black_level),
            'white_level': JsonEx.color_to_json(cum.white_level),
            'curves': []
        }
        for curveMap in cum.curves:
            rez['curves'].append(CurveMap.cm_to_json(curveMap))
        return rez

    @classmethod
    def json_to_cum(cls, cum, cum_in_json):
        cum.use_clip = cum_in_json['use_clip']
        cum.clip_min_x = cum_in_json['clip_min_x']
        cum.clip_min_y = cum_in_json['clip_min_y']
        cum.clip_max_x = cum_in_json['clip_max_x']
        cum.clip_max_y = cum_in_json['clip_max_y']
        JsonEx.color_from_json(cum.black_level, cum_in_json['black_level'])
        JsonEx.color_from_json(cum.white_level, cum_in_json['white_level'])
        for i, curve in enumerate(cum_in_json['curves']):
            CurveMap.json_to_cm(cum.curves[i], curve)
        cum.update()


# CurveMap (curve)
class CurveMap:
    @classmethod
    def cm_to_json(cls, cm):
        rez = {
            'extend': cm.extend,
            'points': []
        }
        for point in cm.points:
            rez['points'].append(CurveMapPoint.cmp_to_json(point))
        return rez

    @classmethod
    def json_to_cm(cls, cm, cm_in_json):
        cm.extend = cm_in_json['extend']
        for i, point in enumerate(cm_in_json['points']):
            if len(cm.points) <= i:
                cm.points.new(point['location'][0], point['location'][1])
            CurveMapPoint.json_to_cmp(cm.points[i], point)


# CurveMapPoint
class CurveMapPoint:
    @classmethod
    def cmp_to_json(cls, cmp):
        return {
            'location': JsonEx.vector2_to_json(cmp.location),
            'handle_type': cmp.handle_type,
            'select': cmp.select
        }

    @classmethod
    def json_to_cmp(cls, cmp, cmp_in_json):
        JsonEx.vector2_from_json(cmp.location, cmp_in_json['location'])
        cmp.handle_type = cmp_in_json['handle_type']
        cmp.select = cmp_in_json['select']
