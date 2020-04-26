# Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import bpy

class Profile(bpy.types.RenderEngine):
    bl_idname = 'VERGE3D'
    bl_label = 'Verge3D / Internal'
    bl_use_preview = False

    bl_use_shading_nodes = False
    bl_use_shading_nodes_custom = False
    bl_use_native_node_tree = True

from bl_ui import (
    properties_scene,
    properties_object,
    properties_material,
    properties_data_armature,
    properties_data_bone,
    properties_data_camera,
    properties_data_curve,
    properties_data_empty,
    properties_data_lamp,
    properties_data_mesh,
    properties_data_modifier
)

def t(name):
    """Return blender type by name"""
    if hasattr(bpy.types, name):
        return getattr(bpy.types, name)
    else:
        return None

def get_compat_props_types():
    """
    get Blender panel types
    search for name in console bpy.types.***
    """
    types = [
        # object data - cameras, lamps etc
        t('DATA_PT_camera'),
        t('DATA_PT_camera_display'),
        t('DATA_PT_camera_dof'),
        t('DATA_PT_context_camera'),
        t('DATA_PT_context_lamp'),
        t('DATA_PT_context_mesh'),
        t('DATA_PT_curve_texture_space'),
        t('DATA_PT_customdata'),
        t('DATA_PT_custom_props_arm'),
        t('DATA_PT_custom_props_camera'),
        t('DATA_PT_custom_props_curve'),
        t('DATA_PT_custom_props_lamp'),
        t('DATA_PT_custom_props_mesh'),
        t('DATA_PT_custom_props_metaball'),
        t('DATA_PT_lamp'),
        t('DATA_PT_lens'),
        t('DATA_PT_preview'),
        t('DATA_PT_shape_keys'),
        t('DATA_PT_spot'),
        t('DATA_PT_uv_texture'),
        t('DATA_PT_vertex_colors'),
        t('DATA_PT_vertex_groups'),

        t('MATERIAL_PT_context_material'),
        t('MATERIAL_PT_custom_props'),
        t('MATERIAL_PT_diffuse'),
        t('MATERIAL_PT_mirror'),
        t('MATERIAL_PT_preview'),
        t('MATERIAL_PT_specular'),
        t('MATERIAL_PT_shading'),
        t('MATERIAL_PT_shadow'),

        t('PARTICLE_MT_specials'),

        t('TEXTURE_MT_envmap_specials'),
        t('TEXTURE_MT_specials'),
        t('TEXTURE_PT_context_texture'),
        t('TEXTURE_PT_custom_props'),
        t('TEXTURE_PT_envmap'),
        t('TEXTURE_PT_image'),
        t('TEXTURE_PT_image_mapping'),
        t('TEXTURE_PT_image_sampling'),
        t('TEXTURE_PT_influence'),
        t('TEXTURE_PT_mapping'),
        t('TEXTURE_PT_preview'),

        t('RENDER_PT_dimensions'),
        t('RENDER_PT_shading'),

        t('SCENE_PT_color_management'),
        t('SCENE_PT_custom_props'),
        t('SCENE_PT_scene'),

        t('WORLD_PT_context_world'),
        t('WORLD_PT_custom_props'),
        t('WORLD_PT_environment_lighting'),
        t('WORLD_PT_mist'),
        t('WORLD_PT_preview'),
        t('WORLD_PT_world')
    ]

    # remove None types
    types = [x for x in types if x != None]

    return types

def register():
    bpy.utils.register_class(Profile)

    for prop in get_compat_props_types():
        prop.COMPAT_ENGINES.add(Profile.bl_idname)

def unregister():
    bpy.utils.unregister_class(Profile)

    for prop in get_compat_props_types():
        prop.COMPAT_ENGINES.remove(Profile.bl_idname)
