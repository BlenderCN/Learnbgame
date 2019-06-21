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

import bpy
from bpy.utils import register_class, unregister_class
from subprocess import Popen
from os import system, path, makedirs

def ds_ic_fbx_export(self, context):

    _export_name = bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend','')
    _export_path = ds_ic_get_export_path()

    _export_file = _export_path + _export_name + '.fbx'

    if not bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()

    bpy.ops.export_scene.fbx(filepath=_export_file, check_existing=False, axis_forward='-Z', axis_up='Y', use_selection=False, object_types={'ARMATURE', 'MESH'}, add_leaf_bones=False, path_mode='COPY', embed_textures=True)
    
    return _export_file

class ds_ic_fbx_export_execute(bpy.types.Operator):

    bl_idname = "ds_ic.fbx_export"
    bl_label = "Export FBX."

    def execute(self, context):

        _export_file = ds_ic_fbx_export(self, context)

        return {'FINISHED'}

def ds_ic_get_export_path():

    _export_path = bpy.path.abspath('//') + bpy.context.preferences.addons[__package__].preferences.option_export_folder + '\\'

    if not path.exists(_export_path):
        makedirs(_export_path)

    return _export_path

def ds_ic_get_textures_path():

    _textures_path = bpy.path.abspath('//') + bpy.context.preferences.addons[__package__].preferences.option_textures_folder + '\\'

    if not path.exists(_textures_path):
        makedirs(_textures_path)

    return _textures_path

class ds_ic_import_base(bpy.types.Operator):

    bl_idname = "ds_ic.import_base"
    bl_label = "iClone Base Template (FBX)"

    def execute(self, context):

        _export_name = bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend','')
        _export_path = ds_ic_get_export_path()

        system('copy "' + bpy.context.preferences.addons[__package__].preferences.option_ic_templates_path + "Maya\FBX\CC3_Neutral_Maya_fbx\CC3_Neutral_Maya_fbx.fbxkey" + '" "' + _export_path + _export_name + '.fbxkey"')

        bpy.ops.import_scene.fbx(filepath = bpy.context.preferences.addons[__package__].preferences.option_ic_templates_path + "Maya\FBX\CC3_Neutral_Maya_fbx\CC3_Neutral_Maya_fbx.Fbx", axis_forward='-Z', axis_up='Y')

        return {'FINISHED'}

class ds_ic_import_female(bpy.types.Operator):

    bl_idname = "ds_ic.import_female"
    bl_label = "iClone Female Template (FBX)"

    def execute(self, context):

        _export_name = bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend','')
        _export_path = ds_ic_get_export_path()

        system('copy "' + bpy.context.preferences.addons[__package__].preferences.option_ic_templates_path + "Maya\FBX\CC3_Base Female_Maya_fbx\CC3_Base Female_Maya_fbx.fbxkey" + '" "' + _export_path + _export_name + '.fbxkey"')
        
        bpy.ops.import_scene.fbx(filepath = bpy.context.preferences.addons[__package__].preferences.option_ic_templates_path + "Maya\FBX\CC3_Base Female_Maya_fbx\CC3_Base Female_Maya_fbx.Fbx", axis_forward='-Z', axis_up='Y')

        return {'FINISHED'}

class ds_ic_import_male(bpy.types.Operator):

    bl_idname = "ds_ic.import_male"
    bl_label = "iClone Male Template (FBX)"

    def execute(self, context):

        _export_name = bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend','')
        _export_path = ds_ic_get_export_path()

        system('copy "' + bpy.context.preferences.addons[__package__].preferences.option_ic_templates_path + "Maya\FBX\CC3_Base Male_Maya_fbx\CC3_Base Male_Maya_fbx.fbxkey" + '" "' + _export_path + _export_name + '.fbxkey"')

        bpy.ops.import_scene.fbx(filepath = bpy.context.preferences.addons[__package__].preferences.option_ic_templates_path + "Maya\FBX\CC3_Base Male_Maya_fbx\CC3_Base Male_Maya_fbx.Fbx", axis_forward='-Z', axis_up='Y')

        return {'FINISHED'}

class ds_ic_export_3dx(bpy.types.Operator):

    bl_idname = "ds_ic.export_3dx"
    bl_label = "3DXchange (FBX)"

    def execute(self, context):

        export_file = ds_ic_fbx_export(self, context)

        Popen([bpy.context.preferences.addons[__package__].preferences.option_ic_3dx_exe, export_file])

        return {'FINISHED'}

class ds_ic_export_cc(bpy.types.Operator):

    bl_idname = "ds_ic.export_cc"
    bl_label = "Character Creator (FBX)"

    def execute(self, context):

        export_file = ds_ic_fbx_export(self, context)

        Popen([bpy.context.preferences.addons[__package__].preferences.option_ic_cc_exe, export_file])

        return {'FINISHED'}

class ds_ic_toggle(bpy.types.Operator):

    bl_idname = "ds_ic.toggle"
    bl_label = "iClone"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    def execute(self, context):

        if not bpy.context.preferences.addons[__package__].preferences.option_show_iclone_toggle_state:
            bpy.context.preferences.addons[__package__].preferences.option_show_iclone_toggle_state=True
        else:
            bpy.context.preferences.addons[__package__].preferences.option_show_iclone_toggle_state=False
        return {'FINISHED'}

classes = (
    ds_ic_fbx_export_execute,
    ds_ic_import_base,
    ds_ic_import_female,
    ds_ic_import_male,
    ds_ic_export_cc,
    ds_ic_export_3dx,
    ds_ic_toggle,
)

def register():

    for cls in classes:
        register_class(cls)

def unregister():

    for cls in reversed(classes):
        unregister_class(cls)
  