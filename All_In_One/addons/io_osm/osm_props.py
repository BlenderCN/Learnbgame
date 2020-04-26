import bpy

class OSM_Tag(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name")
    value = bpy.props.StringProperty(name="Value")
    priority = bpy.props.IntProperty(name="Priority",
                                    description="To priorise tags with same name and value in different materials.",
                                    default=0,
                                    min=0)
    mandatory = bpy.props.BoolProperty(name="Mandatory",
                                    description="Will only be applied if the object has this tag also.",
                                    default=False)


class OSM_Scene(bpy.types.PropertyGroup):
    traffic_direction = bpy.props.EnumProperty(name="Traffic direction",
                                                default='right',
                                                items=[('right','right hand','right hand'),('left','left hand','left hand')])

    offset_step = bpy.props.FloatProperty(name="Z-Sorting offset",
                                            default=0.001,
                                            min=0.01,
                                            max=0.1,
                                            precision=4)

    file = bpy.props.StringProperty(name="File",default='')

    geo_bounds_lat = bpy.props.FloatVectorProperty(name='Bounds Latitude',
                                                default=(0.0,0.0),
                                                size=2)

    geo_bounds_lon = bpy.props.FloatVectorProperty(name='Bounds Longtitude',
                                                default=(0.0,0.0),
                                                size=2)

class OSM_Material(bpy.types.PropertyGroup):
    base_type = bpy.props.EnumProperty(name="Base type",
                                        default='building',
                                        items=[('building','building','building'),('trafficway','trafficway','All kinds of traffic ways.'),('area','area','Flat area.'),('barrier','barrier','All kinds of walls, fences or other barriers.')])

    tags = bpy.props.CollectionProperty(name="Tags",type=OSM_Tag)

    building_part = bpy.props.EnumProperty(name="Part",
                                            description="Building part",
                                            default="facade",
                                            items=[('facade','facade','Material will be used for facades.'),('basement','basement','Material will be used for basement.'),('flat_roof','flat roof','Material will create a flat roof.'),('sloped_roof','sloped roof','Matrerial will create a sloped roof.')])

    building_levels = bpy.props.IntProperty(name="Number of levels in texture",
                                            description="Number of building/roof levels the texture has.",
                                            default=1,
                                            min=1,
                                            max=100)

    building_level_height = bpy.props.FloatProperty(name="Level height",
                                            description="Height of one building/roof level.",
                                            default=5.0,
                                            min=0.0,
                                            max=100.0)

    building_default_levels = bpy.props.IntProperty(name="Default number of levels",
                                            description="Number of building levels when no height information is present.",
                                            default=3,
                                            min=1,
                                            max=100)

    trafficway_sort = bpy.props.IntProperty(name="Z-Sorting index",
                                    description="Higher values will make the road be positioned below roads with lower values.",
                                    default=0,
                                    min=0,
                                    max=100)

    lanes = bpy.props.IntProperty(name="Number of lanes",
                                    description="Number of lanes of the road.",
                                    default=2,
                                    min=1,
                                    max=10)

    lane_width = bpy.props.FloatProperty(name="Lane width",
                                    description="Width of one lane.",
                                    default=3.0,
                                    min=0.0,
                                    max=100.0)

    barrier_width = bpy.props.FloatProperty(name="Barrier width",
                                    description="Width of the barrier.",
                                    default=0.0,
                                    max=100.0)
                                    

class OSM_Object(bpy.types.PropertyGroup):
    id = bpy.props.StringProperty(name="ID")
    name = bpy.props.StringProperty(name="Name")
    tags = bpy.props.CollectionProperty(name="Tags",type=OSM_Tag)

class OSM_Group(bpy.types.PropertyGroup):
    tags = bpy.props.CollectionProperty(name="Tags",type=OSM_Tag)

def register_props():
    bpy.utils.register_class(OSM_Tag)
    bpy.utils.register_class(OSM_Scene)
    bpy.utils.register_class(OSM_Material)
    bpy.utils.register_class(OSM_Group)
    bpy.utils.register_class(OSM_Object)

    bpy.types.Scene.osm = bpy.props.PointerProperty(name="OSM",type=OSM_Scene)
    bpy.types.Material.osm = bpy.props.PointerProperty(name="OSM",type=OSM_Material)
    bpy.types.Group.osm = bpy.props.PointerProperty(name="OSM",type=OSM_Group)
    bpy.types.Object.osm = bpy.props.PointerProperty(name="OSM",type=OSM_Object)

def unregister_props():
    bpy.utils.unregister_class(OSM_Tag)
    bpy.utils.unregister_class(OSM_Scene)
    bpy.utils.unregister_class(OSM_Material)
    bpy.utils.unregister_class(OSM_Group)
    bpy.utils.unregister_class(OSM_Object)