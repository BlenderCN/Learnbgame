import bpy

from bpy.types import (
        PropertyGroup,
        )

from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        IntVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        EnumProperty,
        PointerProperty,
        CollectionProperty,
        )

from . import enums


class PearRaySceneProperties(PropertyGroup):
    beautiful_prc = BoolProperty(
        name="Beautiful PRC",
        description="Export the prc in a beautiful way. (Just using tabs :P)",
        default=False
    )
    keep_prc = BoolProperty(
        name="Keep PRC",
        description="Keep generated prc file after rendering",
        default=False
    )
    linear_rgb = BoolProperty(
        name="Use linear sRGB",
        description="Return output in linear sRGB",
        default=False
    )
    debug_mode = EnumProperty(
        name="Debug Mode",
        description="Render in debug mode",
        items=enums.enum_debug_mode,
        default='NORMAL_BOTH'
        )
    max_ray_depth = IntProperty(
        name="Max Ray Depth",
        description="Maximum ray depth",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=8
        )
    integrator = EnumProperty(
        name="Integrator",
        description="Integrator to be used",
        items=enums.enum_integrator_mode,
        default='BIDIRECT'
        )
    render_tile_mode = EnumProperty(
        name="Tile Mode",
        description="Tiling Mode to be used while rendering",
        items=enums.enum_tile_mode,
        default='LINEAR'
        )
    sampler_aa_mode = EnumProperty(
        name="AA Sampler Mode",
        description="AA sampling technique",
        items=enums.enum_sampler_mode,
        default='MULTI_JITTER'
        )
    sampler_max_aa_samples = IntProperty(
        name="Max AA Samples",
        description="Maximum AA samples",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=4
        )
    sampler_lens_mode = EnumProperty(
        name="Lens Sampler Mode",
        description="Lens sampling technique",
        items=enums.enum_sampler_mode,
        default='MULTI_JITTER'
        )
    sampler_max_lens_samples = IntProperty(
        name="Max Lens Samples",
        description="Maximum Lens samples",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=1
        )
    sampler_time_mode = EnumProperty(
        name="Time Sampler Mode",
        description="Time sampling technique",
        items=enums.enum_sampler_mode,
        default='MULTI_JITTER'
        )
    sampler_max_time_samples = IntProperty(
        name="Max Time Samples",
        description="Maximum Time samples",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=1
        )
    sampler_time_mapping_mode = EnumProperty(
        name="Time Mapping Mode",
        description="Time Mapping Mode",
        items=enums.enum_time_mapping_mode,
        default='CENTER'
        )
    sampler_time_scale = FloatProperty(
        name="Time Scale",
        description="Time Scale",
        min=0,
        soft_min=0.001,
        soft_max=1000,
        default=1
        )
    sampler_spectral_mode = EnumProperty(
        name="Spectral Sampler Mode",
        description="Spectral sampling technique",
        items=enums.enum_sampler_mode,
        default='MULTI_JITTER'
        )
    sampler_max_spectral_samples = IntProperty(
        name="Max Spectral Samples",
        description="Maximum Spectral samples",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=1
        )
    max_diffuse_bounces = IntProperty(
        name="Max Diffuse Bounces",
        description="Maximum diffuse bounces",
        min=0,
        soft_max=4096,
        subtype="UNSIGNED",
        default=2
        )
    max_light_samples = IntProperty(
        name="Max Light Samples",
        description="Maximum light samples",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=2
        )
    max_light_depth = IntProperty(
        name="Max Light Depth",
        description="Maximum light depth",
        min=1,
        soft_max=4096,
        subtype="UNSIGNED",
        default=2
        )
    photon_count = IntProperty(
        name="Photons",
        description="Amount of photons emitted per pass into scene",
        min=1,
        soft_max=1000000000,
        step=100,
        subtype="UNSIGNED",
        default=200000
        )
    photon_passes = IntProperty(
        name="Max Passes",
        description="Maximum count of passes",
        min=1,
        soft_max=1000000000,
        subtype="UNSIGNED",
        default=50
        )
    photon_gather_radius = FloatProperty(
        name="Gather Radius",
        description="Maximum radius of gathering",
        min=0.0001, soft_max=1000.0, default=0.1
        )
    photon_max_gather_count = IntProperty(
        name="Max Gather Count",
        description="Maximum amount of photons used for estimating radiance",
        min=1,
        soft_max=1000000000,
        step=100,
        subtype="UNSIGNED",
        default=1000
        )
    photon_gathering_mode = EnumProperty(
        name="Gathering Mode",
        description="Gathering mode used for estimating radiance",
        items=enums.enum_photon_gathering_mode,
        default='SPHERE'
        )
    photon_squeeze = FloatProperty(
        name="Squeeze Factor",
        description="Squeeze factor to press sphere/dome into a disk",
        min=0.0, max=100, default=0.0,
        subtype="PERCENTAGE"
        )
    photon_ratio = FloatProperty(
        name="Contract Ratio",
        description="Ratio of radius contraction",
        min=1, max=100, default=20,
        subtype="PERCENTAGE"
        )
    ao_use_materials = BoolProperty(
        name="Use BxDF",
        description="Use BxDF sampling in AO",
        default=False
    )
