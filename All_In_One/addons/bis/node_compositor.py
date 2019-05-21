# Nikita Akimov
# interplanety@interplanety.org

# Compositing nodes description

import bpy
import os
from .node_common import NodeCommon, CurveMapping, NodeColorRamp
from .bl_types_conversion import BLbpy_prop_collection, BLbpy_prop_array, BLColor, BLScene


class NodeCompositorNodeBlur(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['aspect_correction'] = node.aspect_correction
        node_json['factor'] = node.factor
        node_json['factor_x'] = node.factor_x
        node_json['factor_y'] = node.factor_y
        node_json['filter_type'] = node.filter_type
        if hasattr(node, 'mute'):
            node_json['mute'] = node.mute
        node_json['size_x'] = node.size_x
        node_json['size_y'] = node.size_y
        node_json['use_bokeh'] = node.use_bokeh
        node_json['use_extended_bounds'] = node.use_extended_bounds
        node_json['use_gamma_correction'] = node.use_gamma_correction
        node_json['use_relative'] = node.use_relative
        node_json['use_variable_size'] = node.use_variable_size

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.aspect_correction = node_in_json['aspect_correction']
        node.factor = node_in_json['factor']
        node.factor_x = node_in_json['factor_x']
        node.factor_y = node_in_json['factor_y']
        node.filter_type = node_in_json['filter_type']
        if 'mute' in node_in_json and hasattr(node, 'mute'):
            node.mute = node_in_json['mute']
        node.size_x = node_in_json['size_x']
        node.size_y = node_in_json['size_y']
        node.use_bokeh = node_in_json['use_bokeh']
        node.use_extended_bounds = node_in_json['use_extended_bounds']
        node.use_gamma_correction = node_in_json['use_gamma_correction']
        node.use_relative = node_in_json['use_relative']
        node.use_variable_size = node_in_json['use_variable_size']


class NodeCompositorNodeImage(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['frame_duration'] = node.frame_duration
        node_json['frame_offset'] = node.frame_offset
        node_json['frame_start'] = node.frame_start
        node_json['image'] = ''
        node_json['image_source'] = ''
        if node.image:
            node_json['image'] = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), node.image.filepath.replace('//', '')))
            node_json['image_source'] = node.image.source
        node_json['use_auto_refresh'] = node.use_auto_refresh
        node_json['use_cyclic'] = node.use_cyclic

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.frame_duration = node_in_json['frame_duration']
        node.frame_offset = node_in_json['frame_offset']
        node.frame_start = node_in_json['frame_start']
        if node_in_json['image']:
            if os.path.exists(node_in_json['image']) and os.path.isfile(node_in_json['image']):
                if os.path.basename(node_in_json['image']) in bpy.data.images:
                    bpy.data.images[os.path.basename(node_in_json['image'])].reload()
                else:
                    bpy.data.images.load(node_in_json['image'], check_existing=True)
            if os.path.basename(node_in_json['image']) in bpy.data.images:
                node.image = bpy.data.images[os.path.basename(node_in_json['image'])]
                node.image.source = node_in_json['image_source']
        node.use_auto_refresh = node_in_json['use_auto_refresh']
        node.use_cyclic = node_in_json['use_cyclic']


class NodeCompositorNodeBokehImage(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['angle'] = node.angle
        node_json['catadioptric'] = node.catadioptric
        node_json['flaps'] = node.flaps
        node_json['rounding'] = node.rounding
        node_json['shift'] = node.shift

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.angle = node_in_json['angle']
        node.catadioptric = node_in_json['catadioptric']
        node.flaps = node_in_json['flaps']
        node.rounding = node_in_json['rounding']
        node.shift = node_in_json['shift']


class NodeCompositorNodeMask(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mask'] = ''
        if node.mask:
            node_json['mask'] = node.mask.name
        node_json['motion_blur_samples'] = node.motion_blur_samples
        node_json['motion_blur_shutter'] = node.motion_blur_shutter
        node_json['size_source'] = node.size_source
        node_json['size_x'] = node.size_x
        node_json['size_y'] = node.size_y
        if hasattr(node, 'use_antialiasing'):
            node_json['use_antialiasing'] = node.use_antialiasing
        node_json['use_feather'] = node.use_feather
        node_json['use_motion_blur'] = node.use_motion_blur

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['mask']:
            if node_in_json['mask'] in bpy.data.masks:
                node.mask = bpy.data.masks[node_in_json['mask']]
        node.motion_blur_samples = node_in_json['motion_blur_samples']
        node.motion_blur_shutter = node_in_json['motion_blur_shutter']
        node.size_source = node_in_json['size_source']
        node.size_x = node_in_json['size_x']
        node.size_y = node_in_json['size_y']
        if 'use_antialiasing' in node_in_json and hasattr(node, 'use_antialiasing'):
            node.use_antialiasing = node_in_json['use_antialiasing']
        node.use_feather = node_in_json['use_feather']
        node.use_motion_blur = node_in_json['use_motion_blur']


class NodeCompositorNodeMovieClip(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['clip'] = ''
        if node.clip:
            node_json['clip'] = node.clip.name

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['clip']:
            if node_in_json['clip'] in bpy.data.movieclips:
                node.clip = bpy.data.movieclips[node_in_json['clip']]


class NodeCompositorNodeColor(NodeCommon):
    pass


class NodeCompositorNodeRGB(NodeCommon):
    pass


class NodeCompositorNodeValue(NodeCommon):
    pass


class NodeCompositorNodeTexture(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['texture'] = ''
        if node.texture:
            node_json['texture'] = node.texture.name

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['texture']:
            if node_in_json['texture'] in bpy.data.textures:
                node.texture = bpy.data.textures[node_in_json['texture']]


class NodeCompositorNodeTime(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['curve'] = CurveMapping.cum_to_json(node.curve)
        node_json['frame_end'] = node.frame_end
        node_json['frame_start'] = node.frame_start

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        CurveMapping.json_to_cum(node.curve, node_in_json['curve'])
        node.frame_end = node_in_json['frame_end']
        node.frame_start = node_in_json['frame_start']


class NodeCompositorNodeTrackPos(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['clip'] = ''
        if node.clip:
            node_json['clip'] = node.clip.name
        node_json['frame_relative'] = node.frame_relative
        node_json['position'] = node.position
        node_json['track_name'] = node.track_name
        node_json['tracking_object'] = node.tracking_object

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['clip']:
            if node_in_json['clip'] in bpy.data.movieclips:
                node.clip = bpy.data.movieclips[node_in_json['clip']]
        node.frame_relative = node_in_json['frame_relative']
        node.position = node_in_json['position']
        node.track_name = node_in_json['track_name']
        node.tracking_object = node_in_json['tracking_object']


class NodeCompositorNodeComposite(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_alpha'] = node.use_alpha

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_alpha = node_in_json['use_alpha']


class NodeCompositorNodeOutputFile(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['active_input_index'] = node.active_input_index
        node_json['base_path'] = node.base_path
        node_json['file_slots'] = BLbpy_prop_collection.to_json(node.file_slots)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.active_input_index = node_in_json['active_input_index']
        node.base_path = node_in_json['base_path']
        BLbpy_prop_collection.from_json(node, node.file_slots, node_in_json['file_slots'])


class NodeCompositorNodeLevels(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['channel'] = node.channel

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.channel = node_in_json['channel']


class NodeCompositorNodeSplitViewer(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['axis'] = node.axis
        node_json['factor'] = node.factor

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.axis = node_in_json['axis']
        node.factor = node_in_json['factor']


class NodeCompositorNodeViewer(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['center_x'] = node.center_x
        node_json['center_y'] = node.center_y
        node_json['tile_order'] = node.tile_order
        node_json['use_alpha'] = node.use_alpha

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.center_x = node_in_json['center_x']
        node.center_y = node_in_json['center_y']
        node.tile_order = node_in_json['tile_order']
        node.use_alpha = node_in_json['use_alpha']


class NodeCompositorNodeAlphaOver(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['premul'] = node.premul
        node_json['use_premultiply'] = node.use_premultiply

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.premul = node_in_json['premul']
        node.use_premultiply = node_in_json['use_premultiply']


class NodeCompositorNodeBrightContrast(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_premultiply'] = node.use_premultiply

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_premultiply = node_in_json['use_premultiply']


class NodeCompositorNodeColorBalance(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['correction_method'] = node.correction_method
        node_json['gain'] = BLColor.to_json(node.gain)
        node_json['gamma'] = BLColor.to_json(node.gamma)
        node_json['lift'] = BLColor.to_json(node.lift)
        node_json['offset'] = BLColor.to_json(node.offset)
        node_json['offset_basis'] = node.offset_basis
        node_json['power'] = BLColor.to_json(node.power)
        node_json['slope'] = BLColor.to_json(node.slope)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.correction_method = node_in_json['correction_method']
        BLColor.from_json(node.gain, node_in_json['gain'])
        BLColor.from_json(node.gamma, node_in_json['gamma'])
        BLColor.from_json(node.lift, node_in_json['lift'])
        BLColor.from_json(node.offset, node_in_json['offset'])
        node.offset_basis = node_in_json['offset_basis']
        BLColor.from_json(node.power, node_in_json['power'])
        BLColor.from_json(node.slope, node_in_json['slope'])


class NodeCompositorNodeColorCorrection(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['red'] = node.red
        node_json['green'] = node.green
        node_json['blue'] = node.blue
        node_json['highlights_contrast'] = node.highlights_contrast
        node_json['highlights_gain'] = node.highlights_gain
        node_json['highlights_gamma'] = node.highlights_gamma
        node_json['highlights_lift'] = node.highlights_lift
        node_json['highlights_saturation'] = node.highlights_saturation
        node_json['master_contrast'] = node.master_contrast
        node_json['master_gain'] = node.master_gain
        node_json['master_gamma'] = node.master_gamma
        node_json['master_lift'] = node.master_lift
        node_json['master_saturation'] = node.master_saturation
        node_json['midtones_contrast'] = node.midtones_contrast
        node_json['midtones_gain'] = node.midtones_gain
        node_json['midtones_gamma'] = node.midtones_gamma
        node_json['midtones_lift'] = node.midtones_lift
        node_json['midtones_saturation'] = node.midtones_saturation
        node_json['midtones_start'] = node.midtones_start
        node_json['midtones_end'] = node.midtones_end
        node_json['shadows_contrast'] = node.shadows_contrast
        node_json['shadows_gain'] = node.shadows_gain
        node_json['shadows_gamma'] = node.shadows_gamma
        node_json['shadows_lift'] = node.shadows_lift
        node_json['shadows_saturation'] = node.shadows_saturation

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.red = node_in_json['red']
        node.green = node_in_json['green']
        node.blue = node_in_json['blue']
        node.highlights_contrast = node_in_json['highlights_contrast']
        node.highlights_gain = node_in_json['highlights_gain']
        node.highlights_gamma = node_in_json['highlights_gamma']
        node.highlights_lift = node_in_json['highlights_lift']
        node.highlights_saturation = node_in_json['highlights_saturation']
        node.master_contrast = node_in_json['master_contrast']
        node.master_gain = node_in_json['master_gain']
        node.master_gamma = node_in_json['master_gamma']
        node.master_lift = node_in_json['master_lift']
        node.master_saturation = node_in_json['master_saturation']
        node.midtones_contrast = node_in_json['midtones_contrast']
        node.midtones_gain = node_in_json['midtones_gain']
        node.midtones_gamma = node_in_json['midtones_gamma']
        node.midtones_lift = node_in_json['midtones_lift']
        node.midtones_saturation = node_in_json['midtones_saturation']
        node.midtones_start = node_in_json['midtones_start']
        node.midtones_end = node_in_json['midtones_end']
        node.shadows_contrast = node_in_json['shadows_contrast']
        node.shadows_gain = node_in_json['shadows_gain']
        node.shadows_gamma = node_in_json['shadows_gamma']
        node.shadows_lift = node_in_json['shadows_lift']
        node.shadows_saturation = node_in_json['shadows_saturation']


class NodeCompositorNodeGamma(NodeCommon):
    pass


class NodeCompositorNodeHueCorrect(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mapping'] = CurveMapping.cum_to_json(node.mapping)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        CurveMapping.json_to_cum(node.mapping, node_in_json['mapping'])


class NodeCompositorNodeHueSat(NodeCommon):
    pass


class NodeCompositorNodeInvert(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['invert_alpha'] = node.invert_alpha
        node_json['invert_rgb'] = node.invert_rgb

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.invert_alpha = node_in_json['invert_alpha']
        node.invert_rgb = node_in_json['invert_rgb']


class NodeCompositorNodeMixRGB(NodeCommon):
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


class NodeCompositorNodeCurveRGB(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mapping'] = CurveMapping.cum_to_json(node.mapping)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        CurveMapping.json_to_cum(node.mapping, node_in_json['mapping'])


class NodeCompositorNodeTonemap(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['adaptation'] = node.adaptation
        node_json['contrast'] = node.contrast
        node_json['correction'] = node.correction
        node_json['gamma'] = node.gamma
        node_json['intensity'] = node.intensity
        node_json['key'] = node.key
        node_json['offset'] = node.offset
        node_json['tonemap_type'] = node.tonemap_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.adaptation = node_in_json['adaptation']
        node.contrast = node_in_json['contrast']
        node.correction = node_in_json['correction']
        node.gamma = node_in_json['gamma']
        node.intensity = node_in_json['intensity']
        node.key = node_in_json['key']
        node.offset = node_in_json['offset']
        node.tonemap_type = node_in_json['tonemap_type']


class NodeCompositorNodeZcombine(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_alpha'] = node.use_alpha
        node_json['use_antialias_z'] = node.use_antialias_z

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_alpha = node_in_json['use_alpha']
        node.use_antialias_z = node_in_json['use_antialias_z']


class NodeCompositorNodePremulKey(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mapping'] = node.mapping

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.mapping = node_in_json['mapping']


class NodeCompositorNodeValToRGB(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['color_ramp'] = NodeColorRamp.cr_to_json(node.color_ramp)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        NodeColorRamp.json_to_cr(node.color_ramp, node_in_json['color_ramp'])


class NodeCompositorNodeCombHSVA(NodeCommon):
    pass


class NodeCompositorNodeCombRGBA(NodeCommon):
    pass


class NodeCompositorNodeCombYCCA(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mode'] = node.mode

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.mode = node_in_json['mode']


class NodeCompositorNodeCombYUVA(NodeCommon):
    pass


class NodeCompositorNodeIDMask(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['index'] = node.index
        node_json['use_antialiasing'] = node.use_antialiasing

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.index = node_in_json['index']
        node.use_antialiasing = node_in_json['use_antialiasing']


class NodeCompositorNodeMath(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['operation'] = node.operation
        node_json['use_clamp'] = node.use_clamp

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.operation = node_in_json['operation']
        node.use_clamp = node_in_json['use_clamp']


class NodeCompositorNodeRGBToBW(NodeCommon):
    pass


class NodeCompositorNodeSepHSVA(NodeCommon):
    pass


class NodeCompositorNodeSepRGBA(NodeCommon):
    pass


class NodeCompositorNodeSepYCCA(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mode'] = node.mode

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.mode = node_in_json['mode']


class NodeCompositorNodeSepYUVA(NodeCommon):
    pass


class NodeCompositorNodeSetAlpha(NodeCommon):
    pass


class NodeCompositorNodeSwitchView(NodeCommon):
    pass


class NodeCompositorNodeBilateralblur(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['iterations'] = node.iterations
        node_json['sigma_color'] = node.sigma_color
        node_json['sigma_space'] = node.sigma_space

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.iterations = node_in_json['iterations']
        node.sigma_color = node_in_json['sigma_color']
        node.sigma_space = node_in_json['sigma_space']


class NodeCompositorNodeBokehBlur(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['blur_max'] = node.blur_max
        node_json['use_extended_bounds'] = node.use_extended_bounds
        node_json['use_variable_size'] = node.use_variable_size

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.blur_max = node_in_json['blur_max']
        node.use_extended_bounds = node_in_json['use_extended_bounds']
        node.use_variable_size = node_in_json['use_variable_size']


class NodeCompositorNodeDefocus(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['angle'] = node.angle
        node_json['blur_max'] = node.blur_max
        node_json['bokeh'] = node.bokeh
        node_json['f_stop'] = node.f_stop
        if node.scene:
            node_json['scene'] = BLScene.to_json(instance=node.scene)
        node_json['threshold'] = node.threshold
        node_json['use_gamma_correction'] = node.use_gamma_correction
        node_json['use_preview'] = node.use_preview
        node_json['use_zbuffer'] = node.use_zbuffer
        node_json['z_scale'] = node.z_scale

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.angle = node_in_json['angle']
        node.blur_max = node_in_json['blur_max']
        node.bokeh = node_in_json['bokeh']
        node.f_stop = node_in_json['f_stop']
        if 'scene' in node_in_json and node_in_json['scene']:
            BLScene.from_json(instance=node, json=node_in_json['scene'])
        node.threshold = node_in_json['threshold']
        node.use_gamma_correction = node_in_json['use_gamma_correction']
        node.use_preview = node_in_json['use_preview']
        node.use_zbuffer = node_in_json['use_zbuffer']
        node.z_scale = node_in_json['z_scale']


class NodeCompositorNodeDespeckle(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['threshold'] = node.threshold
        node_json['threshold_neighbor'] = node.threshold_neighbor

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.threshold = node_in_json['threshold']
        node.threshold_neighbor = node_in_json['threshold_neighbor']


class NodeCompositorNodeDilateErode(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['distance'] = node.distance
        node_json['edge'] = node.edge
        node_json['falloff'] = node.falloff
        node_json['mode'] = node.mode

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.distance = node_in_json['distance']
        node.edge = node_in_json['edge']
        node.falloff = node_in_json['falloff']
        node.mode = node_in_json['mode']


class NodeCompositorNodeDBlur(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['angle'] = node.angle
        node_json['center_x'] = node.center_x
        node_json['center_y'] = node.center_y
        node_json['distance'] = node.distance
        node_json['iterations'] = node.iterations
        node_json['spin'] = node.spin
        node_json['use_wrap'] = node.use_wrap
        node_json['zoom'] = node.zoom

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.angle = node_in_json['angle']
        node.center_x = node_in_json['center_x']
        node.center_y = node_in_json['center_y']
        node.distance = node_in_json['distance']
        node.iterations = node_in_json['iterations']
        node.spin = node_in_json['spin']
        node.use_wrap = node_in_json['use_wrap']
        node.zoom = node_in_json['zoom']


class NodeCompositorNodeFilter(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['filter_type'] = node.filter_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.filter_type = node_in_json['filter_type']


class NodeCompositorNodeGlare(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['angle_offset'] = node.angle_offset
        node_json['color_modulation'] = node.color_modulation
        node_json['fade'] = node.fade
        node_json['glare_type'] = node.glare_type
        node_json['iterations'] = node.iterations
        node_json['mix'] = node.mix
        node_json['quality'] = node.quality
        node_json['size'] = node.size
        node_json['streaks'] = node.streaks
        node_json['threshold'] = node.threshold
        node_json['use_rotate_45'] = node.use_rotate_45

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.angle_offset = node_in_json['angle_offset']
        node.color_modulation = node_in_json['color_modulation']
        node.fade = node_in_json['fade']
        node.glare_type = node_in_json['glare_type']
        node.iterations = node_in_json['iterations']
        node.mix = node_in_json['mix']
        node.quality = node_in_json['quality']
        node.size = node_in_json['size']
        node.streaks = node_in_json['streaks']
        node.threshold = node_in_json['threshold']
        node.use_rotate_45 = node_in_json['use_rotate_45']


class NodeCompositorNodeInpaint(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['distance'] = node.distance

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.distance = node_in_json['distance']


class NodeCompositorNodePixelate(NodeCommon):
    pass


class NodeCompositorNodeSunBeams(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['ray_length'] = node.ray_length
        node_json['source'] = BLbpy_prop_array.to_json(node.source)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.ray_length = node_in_json['ray_length']
        BLbpy_prop_array.from_json(node.source, node_in_json['source'])


class NodeCompositorNodeVecBlur(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['factor'] = node.factor
        node_json['samples'] = node.samples
        node_json['speed_max'] = node.speed_max
        node_json['speed_min'] = node.speed_min
        node_json['use_curved'] = node.use_curved

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.factor = node_in_json['factor']
        node.samples = node_in_json['samples']
        node.speed_max = node_in_json['speed_max']
        node.speed_min = node_in_json['speed_min']
        node.use_curved = node_in_json['use_curved']


class NodeCompositorNodeMapRange(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_clamp'] = node.use_clamp

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_clamp = node_in_json['use_clamp']


class NodeCompositorNodeMapValue(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['max'] = BLbpy_prop_array.to_json(node.max)
        node_json['min'] = BLbpy_prop_array.to_json(node.min)
        node_json['offset'] = BLbpy_prop_array.to_json(node.offset)
        node_json['size'] = BLbpy_prop_array.to_json(node.size)
        node_json['use_max'] = node.use_max
        node_json['use_min'] = node.use_min

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        BLbpy_prop_array.from_json(node.max, node_in_json['max'])
        BLbpy_prop_array.from_json(node.min, node_in_json['min'])
        BLbpy_prop_array.from_json(node.offset, node_in_json['offset'])
        BLbpy_prop_array.from_json(node.size, node_in_json['size'])
        node.use_max = node_in_json['use_max']
        node.use_min = node_in_json['use_min']


class NodeCompositorNodeNormal(NodeCommon):
    pass


class NodeCompositorNodeNormalize(NodeCommon):
    pass


class NodeCompositorNodeCurveVec(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mapping'] = CurveMapping.cum_to_json(node.mapping)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        CurveMapping.json_to_cum(node.mapping, node_in_json['mapping'])


class NodeCompositorNodeEllipseMask(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['mask_type'] = node.mask_type
        node_json['width'] = node.width
        node_json['height'] = node.height
        node_json['x'] = node.x
        node_json['y'] = node.y
        node_json['rotation'] = node.rotation

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.mask_type = node_in_json['mask_type']
        node.width = node_in_json['width']
        node.height = node_in_json['height']
        node.x = node_in_json['x']
        node.y = node_in_json['y']
        node.rotation = node_in_json['rotation']


class NodeCompositorNodeBoxMask(NodeCompositorNodeEllipseMask):
    pass


class NodeCompositorNodeChannelMatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['color_space'] = node.color_space
        node_json['limit_channel'] = node.limit_channel
        node_json['limit_max'] = node.limit_max
        node_json['limit_min'] = node.limit_min
        node_json['limit_method'] = node.limit_method
        node_json['matte_channel'] = node.matte_channel

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.color_space = node_in_json['color_space']
        node.limit_channel = node_in_json['limit_channel']
        node.limit_max = node_in_json['limit_max']
        node.limit_min = node_in_json['limit_min']
        node.limit_method = node_in_json['limit_method']
        node.matte_channel = node_in_json['matte_channel']


class NodeCompositorNodeChromaMatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['gain'] = node.gain
        node_json['lift'] = node.lift
        node_json['shadow_adjust'] = node.shadow_adjust
        node_json['threshold'] = node.threshold
        node_json['tolerance'] = node.tolerance

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.gain = node_in_json['gain']
        node.lift = node_in_json['lift']
        node.shadow_adjust = node_in_json['shadow_adjust']
        node.threshold = node_in_json['threshold']
        node.tolerance = node_in_json['tolerance']


class NodeCompositorNodeColorMatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['color_hue'] = node.color_hue
        node_json['color_saturation'] = node.color_saturation
        node_json['color_value'] = node.color_value

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.color_hue = node_in_json['color_hue']
        node.color_saturation = node_in_json['color_saturation']
        node.color_value = node_in_json['color_value']


class NodeCompositorNodeColorSpill(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['channel'] = node.channel
        node_json['limit_channel'] = node.limit_channel
        node_json['limit_method'] = node.limit_method
        node_json['ratio'] = node.ratio
        node_json['unspill_blue'] = node.unspill_blue
        node_json['unspill_green'] = node.unspill_green
        node_json['unspill_red'] = node.unspill_red
        node_json['use_unspill'] = node.use_unspill

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.channel = node_in_json['channel']
        node.limit_channel = node_in_json['limit_channel']
        node.limit_method = node_in_json['limit_method']
        node.ratio = node_in_json['ratio']
        node.unspill_blue = node_in_json['unspill_blue']
        node.unspill_green = node_in_json['unspill_green']
        node.unspill_red = node_in_json['unspill_red']
        node.use_unspill = node_in_json['use_unspill']


class NodeCompositorNodeCryptomatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        if hasattr(node, 'add'):
            node_json['add'] = BLColor.to_json(node.add)
        if hasattr(node, 'matte_id'):
            node_json['matte_id'] = node.matte_id
        if hasattr(node, 'remove'):
            node_json['remove'] = BLColor.to_json(node.remove)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if 'add' in node_in_json and hasattr(node, 'add'):
            BLColor.from_json(node.add, node_in_json['add'])
        if 'matte_id' in node_in_json and hasattr(node, 'matte_id'):
            node.matte_id = node_in_json['matte_id']
        if 'remove' in node_in_json and hasattr(node, 'remove'):
            BLColor.from_json(node.remove, node_in_json['remove'])


class NodeCompositorNodeDiffMatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['falloff'] = node.falloff
        node_json['tolerance'] = node.tolerance

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.falloff = node_in_json['falloff']
        node.tolerance = node_in_json['tolerance']


class NodeCompositorNodeDistanceMatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['channel'] = node.channel
        node_json['falloff'] = node.falloff
        node_json['tolerance'] = node.tolerance

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.channel = node_in_json['channel']
        node.falloff = node_in_json['falloff']
        node.tolerance = node_in_json['tolerance']


class NodeCompositorNodeDoubleEdgeMask(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['edge_mode'] = node.edge_mode
        node_json['inner_mode'] = node.inner_mode

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.edge_mode = node_in_json['edge_mode']
        node.inner_mode = node_in_json['inner_mode']


class NodeCompositorNodeKeying(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['blur_post'] = node.blur_post
        node_json['blur_pre'] = node.blur_pre
        node_json['clip_black'] = node.clip_black
        node_json['clip_white'] = node.clip_white
        node_json['despill_balance'] = node.despill_balance
        node_json['despill_factor'] = node.despill_factor
        node_json['dilate_distance'] = node.dilate_distance
        node_json['edge_kernel_radius'] = node.edge_kernel_radius
        node_json['edge_kernel_tolerance'] = node.edge_kernel_tolerance
        node_json['feather_distance'] = node.feather_distance
        node_json['feather_falloff'] = node.feather_falloff
        node_json['screen_balance'] = node.screen_balance

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.blur_post = node_in_json['blur_post']
        node.blur_pre = node_in_json['blur_pre']
        node.clip_black = node_in_json['clip_black']
        node.clip_white = node_in_json['clip_white']
        node.despill_balance = node_in_json['despill_balance']
        node.despill_factor = node_in_json['despill_factor']
        node.dilate_distance = node_in_json['dilate_distance']
        node.edge_kernel_radius = node_in_json['edge_kernel_radius']
        node.edge_kernel_tolerance = node_in_json['edge_kernel_tolerance']
        node.feather_distance = node_in_json['feather_distance']
        node.feather_falloff = node_in_json['feather_falloff']
        node.screen_balance = node_in_json['screen_balance']


class NodeCompositorNodeKeyingScreen(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['clip'] = ''
        if node.clip:
            node_json['clip'] = node.clip.name
        node_json['tracking_object'] = node.tracking_object

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['clip']:
            if node_in_json['clip'] in bpy.data.movieclips:
                node.clip = bpy.data.movieclips[node_in_json['clip']]
        node.tracking_object = node_in_json['tracking_object']


class NodeCompositorNodeLumaMatte(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['limit_max'] = node.limit_max
        node_json['limit_min'] = node.limit_min

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.limit_max = node_in_json['limit_max']
        node.limit_min = node_in_json['limit_min']


class NodeCompositorNodeCornerPin(NodeCommon):
    pass


class NodeCompositorNodeCrop(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['max_x'] = node.max_x
        node_json['max_y'] = node.max_y
        node_json['min_x'] = node.min_x
        node_json['min_y'] = node.min_y
        node_json['rel_max_x'] = node.rel_max_x
        node_json['rel_max_y'] = node.rel_max_y
        node_json['rel_min_x'] = node.rel_min_x
        node_json['rel_min_y'] = node.rel_min_y
        node_json['relative'] = node.relative
        node_json['use_crop_size'] = node.use_crop_size

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.max_x = node_in_json['max_x']
        node.max_y = node_in_json['max_y']
        node.min_x = node_in_json['min_x']
        node.min_y = node_in_json['min_y']
        node.rel_max_x = node_in_json['rel_max_x']
        node.rel_max_y = node_in_json['rel_max_y']
        node.rel_min_x = node_in_json['rel_min_x']
        node.rel_min_y = node_in_json['rel_min_y']
        node.relative = node_in_json['relative']
        node.use_crop_size = node_in_json['use_crop_size']


class NodeCompositorNodeDisplace(NodeCommon):
    pass


class NodeCompositorNodeFlip(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['axis'] = node.axis

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.axis = node_in_json['axis']


class NodeCompositorNodeLensdist(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_fit'] = node.use_fit
        node_json['use_jitter'] = node.use_jitter
        node_json['use_projector'] = node.use_projector

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_fit = node_in_json['use_fit']
        node.use_jitter = node_in_json['use_jitter']
        node.use_projector = node_in_json['use_projector']


class NodeCompositorNodeMapUV(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['alpha'] = node.alpha

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.alpha = node_in_json['alpha']


class NodeCompositorNodeMovieDistortion(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['clip'] = ''
        if node.clip:
            node_json['clip'] = node.clip.name
        node_json['distortion_type'] = node.distortion_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['clip']:
            if node_in_json['clip'] in bpy.data.movieclips:
                node.clip = bpy.data.movieclips[node_in_json['clip']]
        node.distortion_type = node_in_json['distortion_type']


class NodeCompositorNodePlaneTrackDeform(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['clip'] = ''
        if node.clip:
            node_json['clip'] = node.clip.name
        node_json['tracking_object'] = node.tracking_object
        node_json['motion_blur_samples'] = node.motion_blur_samples
        node_json['motion_blur_shutter'] = node.motion_blur_shutter
        node_json['plane_track_name'] = node.plane_track_name
        node_json['use_motion_blur'] = node.use_motion_blur

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['clip']:
            if node_in_json['clip'] in bpy.data.movieclips:
                node.clip = bpy.data.movieclips[node_in_json['clip']]
        node.tracking_object = node_in_json['tracking_object']
        node.motion_blur_samples = node_in_json['motion_blur_samples']
        node.motion_blur_shutter = node_in_json['motion_blur_shutter']
        node.plane_track_name = node_in_json['plane_track_name']
        node.use_motion_blur = node_in_json['use_motion_blur']


class NodeCompositorNodeRotate(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['filter_type'] = node.filter_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.filter_type = node_in_json['filter_type']


class NodeCompositorNodeScale(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['frame_method'] = node.frame_method
        node_json['offset_x'] = node.offset_x
        node_json['offset_y'] = node.offset_y
        node_json['space'] = node.space

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.frame_method = node_in_json['frame_method']
        node.offset_x = node_in_json['offset_x']
        node.offset_y = node_in_json['offset_y']
        node.space = node_in_json['space']


class NodeCompositorNodeStabilize(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['clip'] = ''
        if node.clip:
            node_json['clip'] = node.clip.name
        node_json['filter_type'] = node.filter_type
        node_json['invert'] = node.invert

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if node_in_json['clip']:
            if node_in_json['clip'] in bpy.data.movieclips:
                node.clip = bpy.data.movieclips[node_in_json['clip']]
        node.filter_type = node_in_json['filter_type']
        node.invert = node_in_json['invert']


class NodeCompositorNodeTransform(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['filter_type'] = node.filter_type

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.filter_type = node_in_json['filter_type']


class NodeCompositorNodeTranslate(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['use_relative'] = node.use_relative
        node_json['wrap_axis'] = node.wrap_axis

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.use_relative = node_in_json['use_relative']
        node.wrap_axis = node_in_json['wrap_axis']


class NodeCompositorNodeSwitch(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        node_json['check'] = node.check

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        node.check = node_in_json['check']


class NodeCompositorNodeRLayers(NodeCommon):
    @classmethod
    def _node_to_json_spec(cls, node_json, node):
        if hasattr(node, 'layer'):
            node_json['layer'] = node.layer
        if hasattr(node, 'scene') and node.scene:
            node_json['scene'] = BLScene.to_json(instance=node.scene)

    @classmethod
    def _json_to_node_spec(cls, node, node_in_json):
        if 'layer' in node_in_json and hasattr(node, 'layer'):
            node.layer = node_in_json['layer']
        if 'scene' in node_in_json and hasattr(node, 'scene'):
            BLScene.from_json(instance=node, json=node_in_json['scene'])
