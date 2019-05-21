# pylint: disable=C0103
from os import path

import bpy

from .ui import collapsible, xprop
from .utils import with_auto_property


def get_preferences():
    return bpy.context.preferences.addons['io_scene_xray'].preferences


def PropSDKVersion():
    return bpy.props.EnumProperty(
        name='SDK Version',
        items=(('soc', 'SoC', ''), ('cscop', 'CS/CoP', ''))
    )


def PropObjectMotionsImport():
    return bpy.props.BoolProperty(
        name='Import Motions',
        description='Import embedded motions as actions',
        default=True
    )


def PropObjectMeshSplitByMaterials():
    return bpy.props.BoolProperty(
        name='Split Mesh By Materials',
        description='Import each surface (material) as separate set of faces',
        default=False
    )


def PropObjectMotionsExport():
    return bpy.props.BoolProperty(
        name='Export Motions',
        description='Export armatures actions as embedded motions',
        default=True
    )


def PropObjectTextureNamesFromPath():
    return bpy.props.BoolProperty(
        name='Texture Names From Image Paths',
        description='Generate texture names from image paths ' \
                    + '(by subtract <gamedata/textures> prefix and <file-extension> suffix)',
        default=True
    )


def PropObjectBonesCustomShapes():
    return bpy.props.BoolProperty(
        name='Custom Shapes For Bones',
        description='Use custom shapes for imported bones',
        default=True
    )


def PropAnmCameraAnimation():
    return bpy.props.BoolProperty(
        name='Create Linked Camera',
        description='Create animated camera object (linked to "empty"-object)',
        default=True
    )


def PropUseExportPaths():
    return bpy.props.BoolProperty(
        name='Use Export Paths',
        description='Append the Object.ExportPath to the export directory for each object',
        default=True
    )


__AUTO_PROPS__ = [
    'gamedata_folder',
    'textures_folder',
    'gamemtl_file',
    'eshader_file',
    'cshader_file',
]


def update_menu_func(self, context):
    from . import plugin
    plugin.append_menu_func()


class _ExplicitPathOp(bpy.types.Operator):
    bl_idname = 'io_scene_xray.explicit_path'
    bl_label = 'Make Explicit'
    bl_description = 'Make this path explicit using the automatically calculated value'

    path: bpy.props.StringProperty()

    def execute(self, _context):
        prefs = get_preferences()
        value = getattr(prefs, with_auto_property.build_auto_id(self.path))
        setattr(prefs, self.path, value)
        return {'FINISHED'}

class PluginPreferences(bpy.types.AddonPreferences):
    bl_idname = 'io_scene_xray'

    gamedata_folder: bpy.props.StringProperty(name='Gamedata Folder', default='\\gamedata',
                                              description='Path to the \'gamedata\' directory',
                                              subtype='DIR_PATH')

    textures_folder: bpy.props.StringProperty(name='Textures Folder', default='\\textures',
                                              description='Path to the \'gamedata/textures\' directory',
                                              subtype='DIR_PATH')

    gamemtl_file: bpy.props.StringProperty(name='GameMtl File', default='\\gamemtl.xr',
                                           description='Path to the \'gamemtl.xr\' file',
                                           subtype='FILE_PATH')

    eshader_file: bpy.props.StringProperty(name='EShader File', default='\\shaders.xr',
                                           description="Path to the \'shaders.xr\' file",
                                           subtype='FILE_PATH')

    cshader_file: bpy.props.StringProperty(name='CShader File', default='\\shaders_xrlc.xr',
                                           description='Path to the \'shaders_xrlc.xr\' file',
                                           subtype='FILE_PATH')

    expert_mode: bpy.props.BoolProperty(name='Expert Mode', description='Show additional properties/controls')
    compact_menus: bpy.props.BoolProperty(name='Compact Import/Export Menus', update=update_menu_func)
    sdk_version: PropSDKVersion()
    object_motions_import: PropObjectMotionsImport()
    object_motions_export: PropObjectMotionsExport()
    object_mesh_split_by_mat: PropObjectMeshSplitByMaterials()
    object_texture_names_from_path: PropObjectTextureNamesFromPath()
    object_bones_custom_shapes: PropObjectBonesCustomShapes()
    anm_create_camera: PropAnmCameraAnimation()

    objects_folder: bpy.props.StringProperty(
        name='Objects Folder',
        default='',
        description='Path to the \'rawdata/objects\' directory',
        subtype='DIR_PATH'
    )

    def draw(self, _context):
        layout = self.layout

        layout.prop(self, 'gamedata_folder')
        layout.prop(self, 'textures_folder')
        layout.prop(self, 'gamemtl_file')
        layout.prop(self, 'eshader_file')
        layout.prop(self, 'cshader_file')
        layout.prop(self, 'objects_folder')

        _, box = collapsible.draw(layout, 'plugin_prefs:defaults', 'Defaults', style='tree')
        if box:
            row = box.row()
            row.label(text='SDK Version:')
            row.prop(self, 'sdk_version', expand=True)

            _, box_n = collapsible.draw(box, 'plugin_prefs:defaults.object', 'Object', style='tree')
            if box_n:
                box_n.prop(self, 'object_motions_import')
                box_n.prop(self, 'object_motions_export')
                box_n.prop(self, 'object_texture_names_from_path')
                box_n.prop(self, 'object_mesh_split_by_mat')
                box_n.prop(self, 'object_bones_custom_shapes')

            _, box_n = collapsible.draw(box, 'plugin_prefs:defaults.anm', 'Animation', style='tree')
            if box_n:
                box_n.prop(self, 'anm_create_camera')

        layout.prop(self, 'expert_mode')
        layout.prop(self, 'compact_menus')
