
import bpy

from . import generator


class FenceGeneratorAddFenceOperator(bpy.types.Operator):
    bl_idname = 'fence.add'
    bl_label = 'Fence'
    bl_description = 'Add Fence Mesh'
    bl_options = {'REGISTER', 'UNDO'}

    curve = bpy.props.StringProperty(name='Curve')
    curve_tilt = bpy.props.FloatProperty(
        name='Tilt',
        default=90.0
    )
    curve_random_tilt = bpy.props.FloatProperty(
        name='Random Tilt',
        default=0.0
    )
    segments_count = bpy.props.IntProperty(
        name='Count',
        default=1,
        min=1
    )

    # column properties
    column_material = bpy.props.StringProperty(name='Material')
    column_segments = bpy.props.IntProperty(
        name='Segments',
        default=4,
        min=3
    )
    column_radius = bpy.props.FloatProperty(
        name='Radius',
        default=0.1,
        min=0.001
    )
    column_height = bpy.props.FloatProperty(
        name='Height',
        default=1.5,
        min=0.001
    )
    column_random_height = bpy.props.FloatProperty(
        name='Random Height',
        default=0.0,
        min=0.0,
        max=1.0
    )
    column_offset_z = bpy.props.FloatProperty(
        name='Offset Z',
        default=0.0
    )
    column_rotate_z = bpy.props.FloatProperty(
        name='Rotate Z',
        default=0.0
    )

    # fence properties
    fence_material = bpy.props.StringProperty(name='Material')
    fence_height = bpy.props.FloatProperty(
        name='Height',
        default=1.25
    )
    fence_width = bpy.props.FloatProperty(
        name='Width',
        default=3.0
    )
    fence_random_width = bpy.props.FloatProperty(
        name='Random Width',
        default=0.0,
        min=0.0,
        max=1.0
    )
    fence_offset_x = bpy.props.FloatProperty(
        name='Offset X',
        default=0.0
    )
    fence_offset_z = bpy.props.FloatProperty(
        name='Offset Z',
        default=0.0
    )

    def draw(self, context):
        layout = self.layout

        # curve properties
        box = layout.box()
        box.label('Curve:')
        box.prop_search(self, 'curve', bpy.data, 'objects')
        box.prop(self, 'curve_tilt')
        box.prop(self, 'curve_random_tilt')

        # generation properties
        box = layout.box()
        box.label('Generation:')
        box.active = not self.curve
        box.prop(self, 'segments_count')

        # column properties
        box = layout.box()
        box.label('Column:')
        box.prop_search(self, 'column_material', bpy.data, 'materials')
        box.prop(self, 'column_segments')
        box.prop(self, 'column_radius')
        box.prop(self, 'column_height')
        box.prop(self, 'column_random_height')
        box.prop(self, 'column_offset_z')
        box.prop(self, 'column_rotate_z')

        # fence properties
        box = layout.box()
        box.label('Fence:')
        box.prop_search(self, 'fence_material', bpy.data, 'materials')
        box.prop(self, 'fence_height')
        box.prop(self, 'fence_width')
        box.prop(self, 'fence_random_width')
        box.prop(self, 'fence_offset_x')
        box.prop(self, 'fence_offset_z')

    def execute(self, context):
        generator.fence(self, context)
        return {'FINISHED'}
