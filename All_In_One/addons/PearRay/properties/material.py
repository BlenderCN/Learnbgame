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


class PearRayMaterialProperties(PropertyGroup):
    bsdf = EnumProperty(
        name="BSDF",
        description="BSDF type",
        items=enums.enum_material_bsdf,
        default='COOK_TORRANCE'
    )

    cast_shadows = BoolProperty(
        name="Cast Shadows",
        description="Cast Shadows",
        default=True
    )

    cast_self_shadows = BoolProperty(
        name="Cast Self Shadows",
        description="Cast shadows on himself",
        default=True
    )

    is_camera_visible = BoolProperty(
        name="Camera Visible",
        description="Is visible through the camera",
        default=True
    )

    is_shadeable = BoolProperty(
        name="Shadeable",
        description="Will be shaded",
        default=True
    )

    # Emission
    emission_color_type = EnumProperty(
        name="Emission Color Type",
        description="Emission Color Type",
        items=enums.enum_color_type,
        default='COLOR'
    )
    emission_color = FloatVectorProperty(
        name="Emission Color",
        description="Emission Color",
        default=(0,0,0),
        subtype="COLOR",
        soft_max=1,
    )
    emission_color_temp = FloatProperty(
        name="Emission Color Temperature",
        description="Emission Blackbody Color Temperature",
        min=0, soft_max=100000.00, default=5500, step=100
    )
    emission_color_temp_type = EnumProperty(
        name="Emission Color Temperature Type",
        description="Emission Blackbody Color Temperature Type",
        items=enums.enum_temp_type,
        default='LUM'
    )
    emission_color_temp_factor = FloatProperty(
        name="Emission Color Temperature Normalization Factor",
        description="Emission Blackbody Color Temperature Normalization Factor",
        min=0, soft_max=100000.00, default=1, step=100
    )
    emission_color_tex_slot = IntProperty(
        name="Texture Slot",
        description="Used Texture Slot",
        min=0, soft_max=100000, default=0
    )

    # Diffuse
    diffuse_color_type = EnumProperty(
        name="Diffuse Color Type",
        description="Diffuse Color Type",
        items=enums.enum_color_type,
        default='COLOR'
    )
    diffuse_color_temp = FloatProperty(
        name="Diffuse Color Temperature",
        description="Diffuse Blackbody Color Temperature",
        min=0, soft_max=100000.00, default=1000, step=100
    )
    diffuse_color_temp_type = EnumProperty(
        name="Diffuse Color Temperature Type",
        description="Diffuse Blackbody Color Temperature Type",
        items=enums.enum_temp_type,
        default='LUM'
    )
    diffuse_color_temp_factor = FloatProperty(
        name="Diffuse Color Temperature Normalization Factor",
        description="Diffuse Blackbody Color Temperature Normalization Factor",
        min=0, soft_max=100000.00, default=1, step=100
    )
    diffuse_color_tex_slot = IntProperty(
        name="Texture Slot",
        description="Used Texture Slot",
        min=0, soft_max=100000, default=0
    )

    # Specular
    specular_color_type = EnumProperty(
        name="Specular Color Type",
        description="Specular Color Type",
        items=enums.enum_color_type,
        default='COLOR'
    )
    specular_color_temp = FloatProperty(
        name="Specular Color Temperature",
        description="Specular Blackbody Color Temperature",
        min=0, soft_max=100000.00, default=1000, step=100
    )
    specular_color_temp_type = EnumProperty(
        name="Specular Color Temperature Type",
        description="Specular Blackbody Color Temperature Type",
        items=enums.enum_temp_type,
        default='LUM'
    )
    specular_color_temp_factor = FloatProperty(
        name="Specular Color Temperature Normalization Factor",
        description="Specular Blackbody Color Temperature Normalization Factor",
        min=0, soft_max=100000.00, default=1, step=100
    )
    specular_color_tex_slot = IntProperty(
        name="Texture Slot",
        description="Used Texture Slot",
        min=0, soft_max=100000, default=0
    )
    specular_ior_color = FloatVectorProperty(
        name="Specular Index of Refraction",
        description="Specular Index of Refraction",
        default=(1.55,1.55,1.55),
        subtype="COLOR",
        soft_min=1,
        soft_max=3,
    )
    specular_ior_value = FloatProperty(
        name="Specular Index of Refraction",
        description="Specular Index of Refraction",
        default=1.55,
        soft_min=1,
        soft_max=3,
    )
    specular_ior_type = EnumProperty(
        name="Specular Index of Refraction Type",
        description="Specular Index of Refraction Type",
        items=enums.enum_ior_type,
        default='VALUE'
    )

    # Ward
    spec_roughness_x = FloatProperty(
        name="Roughness X",
        description="Roughness to tangent direction",
        min=0, soft_max=1.00, default=0.50
    )
    spec_roughness_y = FloatProperty(
        name="Roughness Y",
        description="Roughness to binormal direction",
        min=0, soft_max=1.00, default=0.50
    )
    reflectivity = FloatProperty(
        name="Reflectivity",
        description="Reflectivity of material",
        min=0, soft_max=1.00, default=0.50
    )

    # CookTorrance
    ct_fresnel_mode = EnumProperty(
        name="Fresnel Mode",
        description="Fresnel Mode",
        items=enums.enum_material_ct_fresnel_mode,
        default='DIELECTRIC'
    )

    ct_distribution_mode = EnumProperty(
        name="Distribution Mode",
        description="Distribution Mode",
        items=enums.enum_material_ct_distribution_mode,
        default='GGX'
    )

    ct_geometry_mode = EnumProperty(
        name="Geometry Mode",
        description="Geometry Mode",
        items=enums.enum_material_ct_geometry_mode,
        default='COOK_TORRANCE'
    )

    # Grid
    grid_first_material = None
    grid_second_material = None
    grid_count = IntProperty(
        name="Grid Count",
        description="Grid Count",
        min=1, soft_max=100000, default=10
    )
    grid_tile_uv = BoolProperty(
        name="Tile UV",
        description="Tile the UV coordinates",
        default=True
    )

    # Glass
    glass_is_thin = BoolProperty(
        name="Thin",
        description="Disables total reflections",
        default=False
    )
