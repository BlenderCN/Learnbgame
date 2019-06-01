from enum import Enum

prim_props = "ndp_props"

class PrimType(Enum):
    Unknown = 0
    Plane = 1
    Box = 2
    Circle = 4
    UvSphere = 8
    IcoSphere = 16
    Cylinder = 32
    Cone = 64
    # Torus = 128

class CustomProperty(Enum):
    prim_type = 0

    divisions = 1

    size = 4

    is_ndp = 7

    fill_type = 8

    calculate_uvs = 9

    radius = 10

    size_policy = 12