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


class PearRayLightProperties(PropertyGroup):
    color_type = EnumProperty(
        name="Light Color Type",
        description="Light Color Type",
        items=enums.enum_flat_color_type,
        default='COLOR'
    )

    color_temp = FloatProperty(
        name="Light Color Temperature",
        description="Light Blackbody Color Temperature",
        min=0, soft_max=100000.00, default=5500, step=100
    )

    color_temp_type = EnumProperty(
        name="Light Color Temperature Type",
        description="Light Blackbody Color Temperature Type",
        items=enums.enum_temp_type,
        default='LUM'
    )

    color_temp_factor = FloatProperty(
        name="Light Color Temperature Normalization Factor",
        description="Light Blackbody Color Temperature  Normalization Factor",
        min=0, soft_max=100000.00, default=1, step=100
    )

    # Point and Area Light
    camera_visible = BoolProperty(
        name="Camera Visible",
        description="Will be visible by the camera",
        default=False
    )

    # Point Light
    point_radius = FloatProperty(
        name="Sphere radius",
        description="Sphere radius of point light",
        min=0.00001, soft_max=100.00, default=0.1
    )