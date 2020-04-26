
import bpy
from . import selector


class StalkerImportObjectPreferences(bpy.types.AddonPreferences):
    bl_idname = 'io_scene_stalker_object'
    texture_folder = bpy.props.StringProperty(
        name='Textures',
        default='',
        subtype='DIR_PATH'
        )
    engine_shaders = bpy.props.StringProperty(
        name='Engine Shaders',
        default='',
        subtype='FILE_PATH',
        update=selector.update_create_shader_selector
        )
    compiler_shaders = bpy.props.StringProperty(
        name='Compiler Shaders',
        default='',
        subtype='FILE_PATH',
        update=selector.update_create_compiler_selector
        )
    game_materials = bpy.props.StringProperty(
        name='Game Materials',
        default='',
        subtype='FILE_PATH',
        update=selector.update_create_game_material_selector
        )

    def draw(self, context):
        self.layout.prop(self, 'texture_folder')
        self.layout.prop(self, 'engine_shaders')
        self.layout.prop(self, 'compiler_shaders')
        self.layout.prop(self, 'game_materials')
