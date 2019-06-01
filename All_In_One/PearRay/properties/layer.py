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


class PearRaySceneRenderLayerProperties(PropertyGroup):
    aov_t = BoolProperty(
        name="Time",
        description="Deliver T (time) values as an extra file",
        default=False
    )
    aov_q = BoolProperty(
        name="Quality",
        description="Deliver quality (error) values as an extra file",
        default=False
    )
    aov_samples = BoolProperty(
        name="Samples",
        description="Deliver samples values as an extra file",
        default=False
    )

    aov_p = BoolProperty(
        name="Position",
        description="Deliver P (position) values as an extra file",
        default=False
    )
    aov_ng = BoolProperty(
        name="Ng",
        description="Deliver Ng (geometric normal) values as an extra file",
        default=False
    )
    aov_nx = BoolProperty(
        name="Nx",
        description="Deliver Nx (tangent) values as an extra file",
        default=False
    )
    aov_ny = BoolProperty(
        name="Ny",
        description="Deliver Ny (bitangent/binormal) values as an extra file",
        default=False
    )
    aov_v = BoolProperty(
        name="V",
        description="Deliver V (view) values as an extra file",
        default=False
    )
    aov_dpdu = BoolProperty(
        name="dPdU",
        description="Deliver dPdU values as an extra file",
        default=False
    )
    aov_dpdv = BoolProperty(
        name="dPdV",
        description="Deliver dPdV values as an extra file",
        default=False
    )
    aov_dpdw = BoolProperty(
        name="dPdW",
        description="Deliver dPdW values as an extra file",
        default=False
    )
    aov_dpdx = BoolProperty(
        name="dPdX",
        description="Deliver dPdY values as an extra file",
        default=False
    )
    aov_dpdy = BoolProperty(
        name="dPdY",
        description="Deliver dPdY values as an extra file",
        default=False
    )
    aov_dpdz = BoolProperty(
        name="dPdZ",
        description="Deliver dPdZ values as an extra file",
        default=False
    )

    raw_spectral = BoolProperty(
        name="Raw Spectral",
        description="Deliver raw spectral values",
        default=False
    )