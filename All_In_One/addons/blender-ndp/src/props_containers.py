import bpy
from . enums import PrimType, CustomProperty, prim_props

def _init_prim_types():
        enum_items = []
        for prim_type in PrimType:
            enum_items.append(
                (
                    prim_type.name.upper(),
                    prim_type.name,
                    "Non-destructive {}".format(prim_type.name),
                    prim_type.value
                ))
        return enum_items
prim_types = _init_prim_types()

def _init_size_policy(container, context):
    options = [('DEFAULT', "Default", "Default (blender) size behavior.", "", 0)]
    if container._is_radius_based():
        options.append(('AXIS_SCALE', "Per-Axis Size", "XYZ scale.", "", 1))
    if container._is_torus():
        options.append((
            'EXTERIOR_INTERIOR',
            "Exterior/Interior",
            "Use the exterior/interior radii for torus dimensions.",
            "",
            2))
    return options

class PropertiesContainer(bpy.types.PropertyGroup):
    #ndp marker:
    is_ndp : bpy.props.BoolProperty(default=False)
    #prim type:
    prim_type : bpy.props.EnumProperty(
        items = prim_types,
        name = "Type")
    #divisions are also used as segments and rings for sphere,
    #vertices for circle, etc
    divisions : bpy.props.IntVectorProperty(
        min=0, size=3, default=(0,0,0))
    #axis_based_size
    size : bpy.props.FloatVectorProperty(
        size=3, default=(1,1,1))
    #(radius, radius2 for cones, toruses, etc):
    radius : bpy.props.FloatVectorProperty(size=2, default=(1, 0))
    #fill type for caps on circle, cylinder, cone
    fill_type : bpy.props.EnumProperty(
        items = [
            ('NGONS', "Ngon", "Use ngon."),
            ('TRIANGLE_FAN', "Triangle Fan", "Use Triangle Fans"),
            ('NOTHING', "Nothing", "Don't fill at all."),
            ],
        name = "Caps Fill Type")
    
    calculate_uvs : bpy.props.BoolProperty(
        name="Calculate UVs",
        default=True)


    size_policy : bpy.props.EnumProperty(
        items = _init_size_policy,
        name = "Size Policy")
    
    def has_size_policy(self):
        return self._is_radius_based()

    def _is_radius_based(self):
        result = (self.prim_type == PrimType.Circle.name.upper())
        result |= (self.prim_type == PrimType.UvSphere.name.upper())
        result |= (self.prim_type == PrimType.IcoSphere.name.upper())
        result |= (self.prim_type == PrimType.Cylinder.name.upper())
        result |= (self.prim_type == PrimType.Cone.name.upper())
        # result |= (self.prim_type == PrimType.Torus.name.upper())
        return result

    def _is_torus(self):
        # result = (self.prim_type == PrimType.Torus.name.upper())
        # return result
        return False

#cache class for the scene, where the last used NDP initial values are cached
class InitialPropertiesCacheContainer(bpy.types.PropertyGroup):
    plane : bpy.props.PointerProperty(type = PropertiesContainer)
    box : bpy.props.PointerProperty(type = PropertiesContainer)
    circle : bpy.props.PointerProperty(type = PropertiesContainer)
    uvsphere : bpy.props.PointerProperty(type = PropertiesContainer)
    icosphere : bpy.props.PointerProperty(type = PropertiesContainer)
    cylinder : bpy.props.PointerProperty(type = PropertiesContainer)
    cone : bpy.props.PointerProperty(type = PropertiesContainer)

def get_properties_cache(context):
    scene = context.scene
    cache = scene.ndp_cache_initial
    try:
        if cache.plane.prim_type != 'PLANE':
            raise Exception("NDP cache was not found.")
        
        return cache
    except:
        # print("Initializing NDP Cache...")
        pass
    
    for prim_type in PrimType:
        if (prim_type == PrimType.Unknown):
            continue
        setattr(getattr(cache, prim_type.name.lower()), "prim_type", prim_type.name.upper())
    
    cache.plane.size = (2,2,2)

    cache.box.size = (2,2,2)

    cache.circle.divisions[0] = 32
    setattr(cache.circle, 'fill_type', 'NOTHING')

    cache.uvsphere.divisions[0] = 32
    cache.uvsphere.divisions[1] = 16

    cache.icosphere.divisions[0] = 2

    cache.cylinder.divisions[0] = 32
    cache.cylinder.size[2] = 2
    
    cache.cone.divisions[0] = 32
    cache.cone.size[2] = 2

    return cache