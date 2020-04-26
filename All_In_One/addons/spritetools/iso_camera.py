import os
import bpy
from math import radians
from bpy.types import Panel, Operator

azimuth = {0: 's', 45: 'sw', 90: 'w', 135: 'nw', 180: 'n', 225: 'ne', 270: 'e', 315: 'se'}


def update_distance(self, context):
    camera = bpy.data.objects['_Camera']
    camera.location = (self.camera_distance, - self.camera_distance, camera.location.z)


class AddIsoCamera(Operator):

    bl_idname = 'sprite_tools.add_iso_camera'
    bl_label = 'Add Isometric Camera'
    bl_description = 'Add Isometric Camera to scene'

    def execute(self, context):
        # delete isometric camera if exists
        for obj in bpy.data.objects:
            if obj.name in ('_Camera', 'IsoCamera'):
                obj.select = True
            else:
                obj.select = False
        bpy.ops.object.delete()
        # add isometric camera
        bpy.ops.object.camera_add(
            location=(10, -10, 10),
            rotation=(radians(60), 0, radians(45))
        )
        camera = context.object
        camera.name = '_Camera'
        camera.data.type = 'ORTHO'
        # add follow camera path
        bpy.ops.curve.primitive_bezier_circle_add(
            location=(0, 0, 10)
        )
        camera_path = context.object
        camera_path.data.path_duration = 1
        camera_path.scale = (14, 14, 1)
        # assign path to camera
        camera.select = True
        camera_path.select = True
        context.scene.objects.active = camera_path
        bpy.ops.object.parent_set(type='FOLLOW')
        # set camera name and add to scene
        iso_camera = context.object
        iso_camera.name = 'IsoCamera'
        context.scene.camera = camera
        # set render output settings
        context.scene.render.resolution_x = 300
        context.scene.render.resolution_y = 300
        context.scene.render.resolution_percentage = 100
        context.scene.render.alpha_mode = 'TRANSPARENT'
        context.scene.render.image_settings.file_format = 'PNG'
        context.scene.render.image_settings.color_mode = 'RGBA'
        context.scene.render.image_settings.compression = 100
        # debug info
        self.report({'INFO'}, 'Isometric camera has been created!')
        return {'FINISHED'}


class RenderSprites(Operator):

    bl_idname = 'sprite_tools.render_sprites'
    bl_label = 'Render Sprites'
    bl_description = 'Render sprites to output directory'

    @classmethod
    def poll(cls, context):
        path = context.scene.render_path
        prefix = context.scene.render_prefix
        return path and os.path.isdir(path) and prefix

    def execute(self, context):
        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end
        frame_count = frame_end - frame_start + 1
        camera = bpy.data.objects['IsoCamera']
        path = context.scene.render_path
        prefix = context.scene.render_prefix
        for angle in range(0, 360, 45):
            for frame in range(1, frame_count + 1):
                frame_index = format(frame, '02d')
                bpy.context.scene.frame_current = frame + frame_start - 1
                direction = azimuth[angle]
                camera.rotation_euler.z = radians(angle)
                file_name = '{}_{}_{}.png'.format(prefix, direction, frame_index)
                context.scene.render.filepath = os.path.join(path, file_name)
                bpy.ops.render.render(write_still=True)
        self.report({'INFO'}, 'Sprites has been rendered!')
        return {'FINISHED'}


class IsoCamera(Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Isometric Camera'
    bl_context = 'objectmode'
    bl_category = 'Sprite Tools'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator('sprite_tools.add_iso_camera', text='Add Isometric Camera', icon='RENDER_STILL')

        if 'IsoCamera' in bpy.data.objects:
            row = layout.row()
            row.label(text='Position:')

            row = layout.row()
            split = row.split()
            column = split.column(align=True)
            obj = bpy.data.objects['IsoCamera']
            column.prop(obj, 'location', index=2, text='Height:')
            column.prop(context.scene, 'camera_distance', text='Distance:')

            row = layout.row()
            row.label(text='Lens:')

            row = layout.row()
            obj = bpy.data.objects['_Camera'].data
            row.prop(obj, 'ortho_scale', 'Orthographic Scale:')

            row = layout.row()
            row.label(text='Resolution:')

            row = layout.row()
            split = row.split()
            column = split.column(align=True)
            obj = context.scene.render
            column.prop(obj, 'resolution_x', index=0, text='X:')
            column.prop(obj, 'resolution_y', index=1, text='Y:')

            row = layout.row()
            row.label(text='Output:')

            row = layout.row()
            row.prop(context.scene, 'render_prefix', text='Prefix')

            row = layout.row()
            row.prop(context.scene, 'render_path')

            row = layout.row()
            obj = context.scene.render.image_settings
            row.prop(obj, 'compression', 'PNG Compression:')

            row = layout.row()
            row.label(text='Render:')

            row = layout.row()
            row.operator('sprite_tools.render_sprites', text='Render Sprites', icon='RENDER_ANIMATION')
