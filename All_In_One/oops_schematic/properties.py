
import bpy


class OopsSchematicNodePropertyGroup(bpy.types.PropertyGroup):
    offset = bpy.props.BoolProperty(default=False)
    select = bpy.props.BoolProperty(default=False)
    position_x = bpy.props.FloatProperty(default=0.0)
    position_y = bpy.props.FloatProperty(default=0.0)


class OopsSchematicClick(bpy.types.PropertyGroup):
    x = bpy.props.FloatProperty(default=-1000.0)
    y = bpy.props.FloatProperty(default=-1000.0)


class OopsSchematicPropertyGroup(bpy.types.PropertyGroup):
    show = bpy.props.BoolProperty(default=False)
    select_3d_view = bpy.props.BoolProperty(name='3D View Select', default=False)
    tree_width = bpy.props.FloatProperty(name='Tree Width', default=1000.0)

    show_libraries = bpy.props.BoolProperty(name='Libraries', default=False)
    show_scenes = bpy.props.BoolProperty(name='Scenes', default=True)
    show_worlds = bpy.props.BoolProperty(name='Worlds', default=True)
    show_objects = bpy.props.BoolProperty(name='Objects', default=True)
    show_meshes = bpy.props.BoolProperty(name='Meshes', default=True)
    show_cameras = bpy.props.BoolProperty(name='Meshes', default=True)
    show_lamps = bpy.props.BoolProperty(name='Lamps', default=True)
    show_materials = bpy.props.BoolProperty(name='Materials', default=True)
    show_textures = bpy.props.BoolProperty(name='Textures', default=True)
    show_images = bpy.props.BoolProperty(name='Images', default=True)

    color_blend_file_nodes = bpy.props.FloatVectorProperty(
        name='Blend File', default=[0.0, 0.2, 0.6], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_libraries_nodes = bpy.props.FloatVectorProperty(
        name='Libraries', default=[0.6, 0.2, 0.0], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_scenes_nodes = bpy.props.FloatVectorProperty(
        name='Scenes', default=[0.2, 0.4, 0.6], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_worlds_nodes = bpy.props.FloatVectorProperty(
        name='Worlds', default=[0.2, 0.6, 0.4], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_objects_nodes = bpy.props.FloatVectorProperty(
        name='Objects', default=[0.6, 0.4, 0.2], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_meshes_nodes = bpy.props.FloatVectorProperty(
        name='Meshes', default=[0.6, 0.6, 0.6], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_cameras_nodes = bpy.props.FloatVectorProperty(
        name='Cameras', default=[0.3, 0.3, 0.6], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_lamps_nodes = bpy.props.FloatVectorProperty(
        name='Lamps', default=[0.6, 0.6, 0.0], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')
    color_materials_nodes = bpy.props.FloatVectorProperty(
        name='Materials', default=[0.6, 0.2, 0.2], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')

    color_textures_nodes = bpy.props.FloatVectorProperty(
        name='Textures', default=[0.2, 0.6, 0.2], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')

    color_images_nodes = bpy.props.FloatVectorProperty(
        name='Images', default=[0.6, 0.2, 0.6], min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR')

    curve_resolution = bpy.props.IntProperty(name='Curve Resolution', default=40,
        min=2, max=100, soft_min=2, soft_max=100)

    multi_click = bpy.props.CollectionProperty(type=OopsSchematicClick)
    move_offset_x = bpy.props.FloatProperty(default=0.0)
    move_offset_y = bpy.props.FloatProperty(default=0.0)
    grab_mode = bpy.props.BoolProperty(default=False)
    apply_location = bpy.props.BoolProperty(default=False)

    offset = bpy.props.BoolProperty(default=False)
    position_x = bpy.props.FloatProperty(default=0.0)
    position_y = bpy.props.FloatProperty(default=0.0)
