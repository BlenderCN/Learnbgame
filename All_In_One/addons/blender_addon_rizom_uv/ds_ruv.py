# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy, math
from bpy.utils import register_class, unregister_class
from subprocess import Popen
from os import system, path, makedirs

def ds_ruv_get_export_path():

    _export_path = bpy.path.abspath('//') + bpy.context.preferences.addons[__package__].preferences.option_export_folder + '\\'

    if not path.exists(_export_path):
        makedirs(_export_path)

    return _export_path

def ds_ruv_filename(self, context):

    _object_name = bpy.context.active_object.name
    _export_path = ds_ruv_get_export_path()
    _export_file = _export_path + _object_name + '_ruv.fbx'

    if not bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()

    return _export_file

def ds_ruv_fbx_export(self, context):

    _export_file = ds_ruv_filename(self, context)

    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.export_scene.fbx(filepath=_export_file, use_selection=True, check_existing=False, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", ui_tab='MAIN', global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)

    return _export_file

class ds_ruv_fbx_export_execute(bpy.types.Operator):

    bl_idname = "ds_ruv.obj_export"
    bl_label = "Export FBX."

    def execute(self, context):

        _export_file = ds_ruv_fbx_export(self, context)

        return {'FINISHED'}

class ds_ruv_export(bpy.types.Operator):

    bl_idname = "ds_ruv.export"
    bl_label = "RizomUV"
    bl_description = "Export to RizomUV"

    def execute(self, context):

        _export_file = ds_ruv_fbx_export(self, context)

        Popen([bpy.context.preferences.addons[__package__].preferences.option_ruv_exe,_export_file])

        return {'FINISHED'}

class ds_ruv_import(bpy.types.Operator):

    bl_idname = "ds_ruv.import"
    bl_label = "RizomUV"
    bl_description = "Import from RizomUV"

    def execute(self, context):

        obj_selected = bpy.context.object
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.import_scene.fbx(filepath = ds_ruv_filename(self, context), axis_forward='-Z', axis_up='Y')

        obj_imported = bpy.context.selected_objects[0]

        obj_imported.select_set(True)
        obj_selected.select_set(True)
        bpy.context.view_layer.objects.active = obj_imported

        bpy.ops.object.join_uvs()

        obj_selected.select_set(False)
        
        bpy.ops.object.delete()

        bpy.context.view_layer.objects.active = obj_selected
        obj_selected.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}

classes = (
    ds_ruv_fbx_export_execute,
    ds_ruv_import,
    ds_ruv_export,
)

def register():

    for cls in classes:
        register_class(cls)

def unregister():

    for cls in reversed(classes):
        unregister_class(cls)


