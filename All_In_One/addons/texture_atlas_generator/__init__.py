bl_info = {
    "name": "Texture Atlas Generator",
    "author": "Lukas Florea",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Texture",
    "description": "Generates a Texture Atlas from multi-material object",
    "warning": "",
    "wiki_url": "https://github.com/LuFlo/texture_atlas_generator/wiki",
    "tracker_url": "https://github.com/LuFlo/texture_atlas_generator/issues/new",
    "category": "Learnbgame",
}

from . import util

import bpy

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        FloatVectorProperty,
    )

class PerformGeneration(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_texture_atlas"
    bl_label = "Generate Texture Atlas"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    tag_image_size: IntProperty(
            attr="tag_image_size",
            name="Image size",
            default=512, min=64, max=4096,
            description="Width and height of texture atlas"
        )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        scene = context.scene
        util.generate_texture_atlas(scene.tag_image_size, scene.tag_tile_size)
        return {'FINISHED'}

class PropsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Texture atlas generator"
    bl_idname = "OBJECT_PT_props_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None

    def draw(self, context):
        layout = self.layout

        #obj = context.object

        row = layout.row()
        row.label(text="Settings", icon='PLUGIN')

        row = layout.row()

        col = row.column()
        col.label(text='Image size')
        col = row.column()
        col.prop(context.scene, "tag_image_size")

        row = layout.row()

        col = row.column()
        col.label(text='Tile size')
        col = row.column()
        col.prop(context.scene, "tag_tile_size")

        row = layout.row()
        row = layout.row()
        row.operator("object.generate_texture_atlas")


def register():
    bpy.utils.register_class(PropsPanel)
    bpy.utils.register_class(PerformGeneration)
    bpy.types.Scene.tag_image_size = IntProperty(
            attr="tag_image_size",
            name="",
            default=512, min=64, max=4096,
            description="Width and height of texture atlas"
        )
    bpy.types.Scene.tag_tile_size = IntProperty(
            attr="tag_tile_size",
            name="",
            default=64, min=8, max=512,
            description="Width and height of color tiles"
        )


def unregister():
    bpy.utils.unregister_class(PropsPanel)
    bpy.utils.unregister_class(PerformGeneration)


if __name__ == "__main__":
    register()
