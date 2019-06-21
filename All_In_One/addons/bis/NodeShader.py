# Nikita Akimov
# interplanety@interplanety.org

# --------------------------------------------------------------
# for older compatibility
# used for node groups version 1.4.1
# if there would no 1.4.1 nodegroups - all this file can be removed
# work in - node_shader_cycles
# --------------------------------------------------------------

import bpy
import os
from .JsonEx import JsonEx
from .NodeBase import NodeBase, TMCommon, IUCommon, CMCommon, CurveMapping, NodeColorRamp
from .TextManager import TextManager


class NodeBaseShaderNodeBsdfGlossy(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['distribution'] = node.distribution

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.distribution = node_in_json['distribution']


class NodeBaseShaderNodeBsdfAnisotropic(NodeBaseShaderNodeBsdfGlossy):
    pass


class NodeBaseShaderNodeBsdfGlass(NodeBaseShaderNodeBsdfGlossy):
    pass


class NodeBaseShaderNodeBsdfRefraction(NodeBaseShaderNodeBsdfGlossy):
    pass


class NodeBaseShaderNodeAttribute(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['attribute_name'] = node.attribute_name

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.attribute_name = node_in_json['attribute_name']


class NodeBaseShaderNodeTangent(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['direction_type'] = node.direction_type
        node_json['axis'] = node.axis
        node_json['uv_map'] = node.uv_map

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.direction_type = node_in_json['direction_type']
        node.axis = node_in_json['axis']
        node.uv_map = node_in_json['uv_map']


class NodeBaseShaderNodeUVMap(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['from_dupli'] = node.from_dupli
        node_json['uv_map'] = node.uv_map

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.from_dupli = node_in_json['from_dupli']
        node.uv_map = node_in_json['uv_map']


class NodeBaseShaderNodeTexCoord(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['object'] = ''
        if node.object:
            node_json['object'] = node.object.name
        node_json['from_dupli'] = node.from_dupli

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['object']:
            if node_in_json['object'] in bpy.data.objects:
                node.object = bpy.data.objects[node_in_json['object']]
        node.from_dupli = node_in_json['from_dupli']


class NodeBaseShaderNodeTexPointDensity(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['object'] = ''
        node_json['particle_system'] = ''
        if node.object:
            node_json['object'] = node.object.name
            if node.particle_system:
                node_json['particle_system'] = node.particle_system.name
        node_json['point_source'] = node.point_source
        node_json['resolution'] = node.resolution
        node_json['radius'] = node.radius
        node_json['space'] = node.space
        node_json['interpolation'] = node.interpolation
        node_json['particle_color_source'] = node.particle_color_source
        node_json['vertex_color_source'] = node.vertex_color_source
        node_json['vertex_attribute_name'] = node.vertex_attribute_name

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['object']:
            if node_in_json['object'] in bpy.data.objects:
                node.object = bpy.data.objects[node_in_json['object']]
                if node_in_json['particle_system']:
                    if node_in_json['particle_system'] in bpy.data.objects[node_in_json['object']].particle_systems:
                        node.particle_system = bpy.data.objects[node_in_json['object']].particle_systems[node_in_json['particle_system']]
        node.point_source = node_in_json['point_source']
        node.resolution = node_in_json['resolution']
        node.radius = node_in_json['radius']
        node.space = node_in_json['space']
        node.interpolation = node_in_json['interpolation']
        node.particle_color_source = node_in_json['particle_color_source']
        node.vertex_color_source = node_in_json['vertex_color_source']
        node.vertex_attribute_name = node_in_json['vertex_attribute_name']


class NodeBaseShaderNodeTexEnvironment(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['image'] = ''
        node_json['image_source'] = ''
        if node.image:
            node_json['image'] = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), node.image.filepath.replace('//', '')))
            node_json['image_source'] = node.image.source
        node_json['color_space'] = node.color_space
        node_json['projection'] = node.projection
        node_json['interpolation'] = node.interpolation
        node_json['texture_mapping'] = TMCommon.tm_to_json(node.texture_mapping)
        node_json['image_user'] = IUCommon.iu_to_json(node.image_user)
        node_json['color_mapping'] = CMCommon.cm_to_json(node.color_mapping)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['image']:
            if os.path.exists(node_in_json['image']) and os.path.isfile(node_in_json['image']):
                if os.path.basename(node_in_json['image']) in bpy.data.images:
                    bpy.data.images[os.path.basename(node_in_json['image'])].reload()
                else:
                    bpy.data.images.load(node_in_json['image'], check_existing=True)
            if os.path.basename(node_in_json['image']) in bpy.data.images:
                node.image = bpy.data.images[os.path.basename(node_in_json['image'])]
                node.image.source = node_in_json['image_source']
        node.color_space = node_in_json['color_space']
        node.projection = node_in_json['projection']
        node.interpolation = node_in_json['interpolation']
        TMCommon.json_to_tm(node, node_in_json['texture_mapping'])
        IUCommon.json_to_iu(node, node_in_json['image_user'])
        CMCommon.json_to_cm(node, node_in_json['color_mapping'])


class NodeBaseShaderNodeTexImage(NodeBaseShaderNodeTexEnvironment):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['projection_blend'] = node.projection_blend
        node_json['extension'] = node.extension

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.projection_blend = node_in_json['projection_blend']
        node.extension = node_in_json['extension']


class NodeBaseShaderNodeTexChecker(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['texture_mapping'] = TMCommon.tm_to_json(node.texture_mapping)
        node_json['color_mapping'] = CMCommon.cm_to_json(node.color_mapping)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        TMCommon.json_to_tm(node, node_in_json['texture_mapping'])
        CMCommon.json_to_cm(node, node_in_json['color_mapping'])


class NodeBaseShaderNodeTexBrick(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['offset_frequency'] = node.offset_frequency
        node_json['squash_frequency'] = node.squash_frequency
        node_json['offset'] = node.offset
        node_json['squash'] = node.squash

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.offset_frequency = node_in_json['offset_frequency']
        node.squash_frequency = node_in_json['squash_frequency']
        node.offset = node_in_json['offset']
        node.squash = node_in_json['squash']


class NodeBaseShaderNodeTexGradient(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['gradient_type'] = node.gradient_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.gradient_type = node_in_json['gradient_type']


class NodeBaseShaderNodeTexMagic(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['turbulence_depth'] = node.turbulence_depth

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.turbulence_depth = node_in_json['turbulence_depth']


class NodeBaseShaderNodeTexMusgrave(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['musgrave_type'] = node.musgrave_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.musgrave_type = node_in_json['musgrave_type']


class NodeBaseShaderNodeTexVoronoi(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['coloring'] = node.coloring

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.coloring = node_in_json['coloring']


class NodeBaseShaderNodeTexWave(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['wave_type'] = node.wave_type
        node_json['wave_profile'] = node.wave_profile

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.wave_type = node_in_json['wave_type']
        node.wave_profile = node_in_json['wave_profile']


class NodeBaseShaderNodeTexSky(NodeBaseShaderNodeTexChecker):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['sky_type'] = node.sky_type
        node_json['sun_direction'] = JsonEx.vector3_to_json(node.sun_direction)
        node_json['turbidity'] = node.turbidity
        node_json['ground_albedo'] = node.ground_albedo

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.sky_type = node_in_json['sky_type']
        JsonEx.vector3_from_json(node.sun_direction, node_in_json['sun_direction'])
        node.turbidity = node_in_json['turbidity']
        node.ground_albedo = node_in_json['ground_albedo']


class NodeBaseShaderNodeTexNoise(NodeBaseShaderNodeTexChecker):
    pass


class NodeBaseShaderNodeWireframe(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_pixel_size'] = node.use_pixel_size

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_pixel_size = node_in_json['use_pixel_size']


class NodeBaseShaderNodeBsdfHair(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['component'] = node.component

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.component = node_in_json['component']


class NodeBaseShaderNodeBsdfToon(NodeBaseShaderNodeBsdfHair):
    pass


class NodeBaseShaderNodeSubsurfaceScattering(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['falloff'] = node.falloff

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.falloff = node_in_json['falloff']


class NodeBaseShaderNodeMixRGB(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['blend_type'] = node.blend_type
        node_json['use_alpha'] = node.use_alpha
        node_json['use_clamp'] = node.use_clamp

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.blend_type = node_in_json['blend_type']
        node.use_alpha = node_in_json['use_alpha']
        node.use_clamp = node_in_json['use_clamp']


class NodeBaseShaderNodeBrightContrast(NodeBase):
    pass


class NodeBaseShaderNodeGamma(NodeBase):
    pass


class NodeBaseShaderNodeHueSaturation(NodeBase):
    pass


class NodeBaseShaderNodeInvert(NodeBase):
    pass


class NodeBaseShaderNodeLightFalloff(NodeBase):
    pass


class NodeBaseShaderNodeBlackbody(NodeBase):
    pass


class NodeBaseShaderNodeCombineHSV(NodeBase):
    pass


class NodeBaseShaderNodeSeparateHSV(NodeBase):
    pass


class NodeBaseShaderNodeCombineRGB(NodeBase):
    pass


class NodeBaseShaderNodeSeparateRGB(NodeBase):
    pass


class NodeBaseShaderNodeCombineXYZ(NodeBase):
    pass


class NodeBaseShaderNodeSeparateXYZ(NodeBase):
    pass


class NodeBaseShaderNodeRGBToBW(NodeBase):
    pass


class NodeBaseShaderNodeWavelength(NodeBase):
    pass


class NodeBaseShaderNodeRGBCurve(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mapping'] = CurveMapping.cum_to_json(node.mapping)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        CurveMapping.json_to_cum(node.mapping, node_in_json['mapping'])


class NodeBaseShaderNodeVectorCurve(NodeBaseShaderNodeRGBCurve):
    pass


class NodeBaseShaderNodeBump(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['invert'] = node.invert

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.invert = node_in_json['invert']


class NodeBaseShaderNodeVectorTransform(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['vector_type'] = node.vector_type
        node_json['convert_from'] = node.convert_from
        node_json['convert_to'] = node.convert_to

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.vector_type = node_in_json['vector_type']
        node.convert_from = node_in_json['convert_from']
        node.convert_to = node_in_json['convert_to']


class NodeBaseShaderNodeValToRGB(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['color_ramp'] = NodeColorRamp.cr_to_json(node.color_ramp)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        NodeColorRamp.json_to_cr(node.color_ramp, node_in_json['color_ramp'])


class NodeBaseShaderNodeMapping(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['vector_type'] = node.vector_type
        node_json['translation'] = JsonEx.vector3_to_json(node.translation)
        node_json['rotation'] = JsonEx.vector3_to_json(node.rotation)
        node_json['scale'] = JsonEx.vector3_to_json(node.scale)
        node_json['min'] = JsonEx.vector3_to_json(node.min)
        node_json['max'] = JsonEx.vector3_to_json(node.max)
        node_json['use_min'] = node.use_min
        node_json['use_max'] = node.use_max

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.vector_type = node_in_json['vector_type']
        JsonEx.vector3_from_json(node.translation, node_in_json['translation'])
        JsonEx.vector3_from_json(node.rotation, node_in_json['rotation'])
        JsonEx.vector3_from_json(node.scale, node_in_json['scale'])
        JsonEx.vector3_from_json(node.min, node_in_json['min'])
        JsonEx.vector3_from_json(node.max, node_in_json['max'])
        node.use_min = node_in_json['use_min']
        node.use_max = node_in_json['use_max']


class NodeBaseShaderNodeMath(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['operation'] = node.operation
        node_json['use_clamp'] = node.use_clamp

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.operation = node_in_json['operation']
        node.use_clamp = node_in_json['use_clamp']


class NodeBaseShaderNodeVectorMath(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['operation'] = node.operation

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.operation = node_in_json['operation']


class NodeBaseShaderNodeScript(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['script'] = ''
        node_json['mode'] = node.mode
        if node.mode == 'INTERNAL':
            if node.script:
                node_json['script'] = node.script.name
                rez = TextManager.to_bis(bpy.data.texts[node.script.name])
                if rez['stat'] == 'OK':
                    bis_linked_item = {
                        'storage': TextManager.storage_type(),
                        'id': rez['data']['id']
                    }
                    node_json['bis_linked_item'] = bis_linked_item
        else:
            node_json['filepath'] = ''
            if node.filepath:
                if node.filepath[:2] == '//':
                    node_json['filepath'] = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), node.filepath[2:]))
                else:
                    node_json['filepath'] = os.path.abspath(node.filepath)
        node_json['use_auto_update'] = node.use_auto_update

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.mode = node_in_json['mode']
        if node.mode == 'INTERNAL':
            if node_in_json['bis_linked_item']:
                TextManager.from_bis(node_in_json['bis_linked_item']['id'])
            if node_in_json['script']:
                if node_in_json['script'] in bpy.data.texts:
                    node.script = bpy.data.texts[node_in_json['script']]
        else:
            if node_in_json['filepath']:
                if os.path.exists(node_in_json['filepath']) and os.path.isfile(node_in_json['filepath']):
                    node.filepath = node_in_json['filepath']
        node.use_auto_update = node_in_json['use_auto_update']
        node.update()


class NodeBaseShaderNodeMixShader(NodeBase):
    pass


class NodeBaseNodeGroupInput(NodeBase):
    pass


class NodeBaseNodeGroupOutput(NodeBase):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['is_active_output'] = node.is_active_output

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if 'is_active_output' in node_in_json:
            node.is_active_output = node_in_json['is_active_output']
