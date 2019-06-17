__reload_order_index__ = 0

import bpy


def update_group_object(self, context):
    """Reset object if type is wrong"""
    if bpy.data.objects[self.object].type != 'MESH':
        self.object = ''

    return None


def update_order(self, context):
    """Update the order of LOD levels when distances change"""
    group = bpy.data.groups[context.scene.lod_group]
    index = 0
    while index < len(group.lod) - 1:
        if group.lod[index].distance > group.lod[index + 1].distance:
            group.lod.move(index, index + 1)
            index = 0
        else:
            index += 1

    return None


class PropertyLODGroup(bpy.types.PropertyGroup):
    object = bpy.props.StringProperty(
        update=update_group_object,
        description="LOD object")
    distance = bpy.props.FloatProperty(
        min=0.0,
        update=update_order,
        description="LOD distance")


class PropertyLODObject(bpy.types.PropertyGroup):
    group = bpy.props.StringProperty(
        name='LOD Group',
        description="Group to use the LODs from"
    )
    use_active_camera = bpy.props.BoolProperty(
        default=True,
        name='Use Active Camera',
        description="Use the active camera as offset object"
    )
    offset = bpy.props.StringProperty(
        name='Offset Object',
        description="Object to calculate distance to"
    )

    use_mesh = bpy.props.BoolProperty(
        default=True,
        name='Use Meshes',
        description="Copy mesh from LOD object"
    )
    use_modifiers = bpy.props.BoolProperty(
        default=True,
        name='Use Modifiers',
        description="Copy modifiers from LOD object"
    )
    use_constraints = bpy.props.BoolProperty(
        default=True,
        name='Use Constraints',
        description="Copy constraints from LOD object"
    )

    use_frustum = bpy.props.BoolProperty(
        default=False,
        name='Use Frustum',
        description="Use a different LOD when the object is not visible to the camera"
    )
    frustum_level = bpy.props.IntProperty(
        default=1, min=1,
        name='Frustum Level',
        description="Level when the object is not visible to the camera"
    )
    frustum_radius = bpy.props.FloatProperty(
        default=0.0, min=0.0,
        name='Custom Radius',
        description="If not 0, override the bounding sphere of the object; radius is scaled proportionally "
                    "to the largest axis of the scale of the object"
    )

    viewport_active = bpy.props.BoolProperty(
        default=True,
        name='Update Viewport',
        description="Whether the LOD is updated in the viewport"
    )
    viewport_level = bpy.props.IntProperty(
        default=1, min=1,
        name='Viewport Level',
        description="Constant level when viewport LOD is disabled"
    )

    render_active = bpy.props.BoolProperty(
        default=True,
        name='Update Render',
        description="Whether the LOD is updated during rendering"
    )
    render_level = bpy.props.IntProperty(
        default=1, min=1,
        name='Render Level',
        description="Constant level when render LOD is disabled"
    )


def register():
    # Create properties.
    bpy.types.Group.lod = bpy.props.CollectionProperty(type=PropertyLODGroup)
    bpy.types.Object.lod = bpy.props.PointerProperty(type=PropertyLODObject)
    bpy.types.Scene.lod_group = bpy.props.StringProperty(description="Group to alter the LOD settings for")


def unregister():
    # Delete properties.
    del bpy.types.Group.lod
    del bpy.types.Object.lod
    del bpy.types.Scene.lod_group
