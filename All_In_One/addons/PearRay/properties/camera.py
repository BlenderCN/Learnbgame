import bpy

from bpy.types import PropertyGroup
from bpy.props import FloatProperty


class PearRayCameraProperties(PropertyGroup):
    zoom = FloatProperty(
        name="Zoom",
        description="Zoom factor",
        min=0.0001, max=1000.00, default=1.0
    )
    fstop = FloatProperty(
        name="FStop",
        description="Focus point for Depth of Field."
                    "(zero disables DOF rendering)",
        min=0.0, max=1000.0, default=0.0
    )
    apertureRadius = FloatProperty(
        name="Aperture Radius",
        description="Similar to a real camera's aperture effect over focal blur (though not "
                    "in physical units and independant of focal length). "
                    "Increase to get more blur",
        min=0.01, max=1.00, default=0.50
    )