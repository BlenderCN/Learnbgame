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

from subprocess import Popen
from os import system, path, makedirs

def ds_zbc_get_export_path():

    _export_path = bpy.path.abspath('//') + bpy.context.user_preferences.addons[__package__].preferences.option_export_folder + '\\'

    if not path.exists(_export_path):
        makedirs(_export_path)

    return _export_path

def ds_zbc_obj_filename(self, context):

    _object_name = bpy.context.scene.objects.active.name
    _export_path = ds_zbc_get_export_path()
    _export_file = _export_path + _object_name + '.obj'

    if not bpy.context.user_preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()

    return _export_file

def ds_zbc_obj_export(self, context):

    _export_file = ds_zbc_obj_filename(self, context)

    bpy.ops.object.transform_apply( location=True, rotation = True, scale = True )
    
    bpy.ops.export_scene.obj(filepath=_export_file, use_selection=True, axis_forward='-Z', axis_up='Y', global_scale=1.0, keep_vertex_order=True)

    return _export_file

class ds_zbc_obj_export_execute(bpy.types.Operator):

    bl_idname = "ds_zbc.obj_export"
    bl_label = "Export OBJ."

    def execute(self, context):

        _export_file = ds_zbc_obj_export(self, context)

        return {'FINISHED'}

class ds_zbc_export(bpy.types.Operator):

    bl_idname = "ds_zbc.export"
    bl_label = "ZBrushCore (OBJ)"

    def execute(self, context):

        _export_file = ds_zbc_obj_export(self, context)

        Popen([bpy.context.user_preferences.addons[__package__].preferences.option_zbc_exe,_export_file])

        return {'FINISHED'}

class ds_zbc_import(bpy.types.Operator):

    bl_idname = "ds_zbc.import"
    bl_label = "ZBrushCore (OBJ)"

    def execute(self, context):

        obj_selected = bpy.context.object
        obj_selected_mesh = obj_selected.data
        
        bpy.ops.import_scene.obj(filepath = ds_zbc_obj_filename(self, context), axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl", use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=True, use_groups_as_vgroups=False, use_image_search=False, split_mode='OFF', global_clamp_size=0.0)
        obj_imported =  bpy.context.selected_objects[0]
        obj_imported_mesh =  obj_imported.data
        bpy.ops.object.transform_apply(location=False, rotation = True, scale = False )

        _selected_vertices=obj_selected_mesh.vertices
        _imported_vertices=obj_imported_mesh.vertices
        
        if len(_selected_vertices)==len(_imported_vertices):

            for _vertice in _selected_vertices:
                _vertice.co=_imported_vertices[_vertice.index].co
            
            bpy.ops.object.delete() 

            obj_selected.scale = (1.0, 1.0, 1.0)

            obj_selected.select = True
            bpy.ops.object.transform_apply(location=False, rotation = False, scale = True )
        
        return {'FINISHED'}

def ds_zbc_menu_func_export(self, context):
    self.layout.operator(ds_zbc_export.bl_idname)

def ds_zbc_menu_func_import(self, context):
    self.layout.operator(ds_zbc_import.bl_idname)

def ds_zbc_toolbar_btn_import(self, context):
    self.layout.operator('ds_zbc.import',text="ZBC",icon="IMPORT")

def ds_zbc_toolbar_btn_export(self, context):
    self.layout.operator('ds_zbc.export',text="ZBC",icon="EXPORT")

def register():

    from bpy.utils import register_class

    register_class(ds_zbc_obj_export_execute)

    register_class(ds_zbc_import)
    register_class(ds_zbc_export)

    if bpy.context.user_preferences.addons[__package__].preferences.option_display_type=='Buttons':
    
        bpy.types.INFO_HT_header.append(ds_zbc_toolbar_btn_export)
        bpy.types.INFO_HT_header.append(ds_zbc_toolbar_btn_import)

    bpy.types.INFO_MT_file_export.append(ds_zbc_menu_func_export)
    bpy.types.INFO_MT_file_import.append(ds_zbc_menu_func_import)

def unregister():

    from bpy.utils import unregister_class

    if bpy.context.user_preferences.addons[__package__].preferences.option_display_type=='Buttons':

        bpy.types.INFO_HT_header.remove(ds_zbc_toolbar_btn_import)
        bpy.types.INFO_HT_header.remove(ds_zbc_toolbar_btn_export)

    bpy.types.INFO_MT_file_import.remove(ds_zbc_menu_func_import)
    bpy.types.INFO_MT_file_export.remove(ds_zbc_menu_func_export)

    unregister_class(ds_zbc_obj_export_execute)

    unregister_class(ds_zbc_import)
    unregister_class(ds_zbc_export)


