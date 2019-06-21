'''
Copyright (C) 2015 Pistiwique, Pitiwazou
 
Created by Pistiwique, Pitiwazou
 
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
 
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
 
import bpy, subprocess
from mathutils import Vector
from os.path import join
from ..function_utils.get_path import (get_directory,
                                       get_addon_path,
                                       )


#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def generate_thumbnail_asset(asset):
    """ Generate the thumbnails of the materials """
 
    AM = bpy.context.window_manager.asset_m
    addon_path = get_addon_path()
    thumbnail_directory = get_directory("icons")
    blend_dir = get_directory("blends")

    material = "object" if AM.material_render == False else ""
 
    if len([obj for obj in bpy.context.scene.objects if obj.select]) and AM.group_name:
        AM.add_subsurf=False
        AM.add_smooth=False
    
    subsurf = "add subsurf" if AM.add_subsurf else ""
    smooth = "add smooth" if AM.add_smooth else ""
    
    blend_thumbnailer = join(addon_path, 'blend_tools', 'asset', 'thumbnailer.blend')
    script_thumbnailer = join(addon_path, "background_tools", 'generate_assets_thumbnail.py')
 
    subprocess.Popen([bpy.app.binary_path, blend_thumbnailer, '-b', '--python', script_thumbnailer, asset, thumbnail_directory, subsurf, smooth, blend_dir, material, AM.thumb_ext])
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def active_snap(self, context):
    """ Toggle the setup for face snapping """
 
    AM = context.window_manager.asset_m
    if AM.snap_enabled:
        AM.snap_mod = bpy.context.scene.tool_settings.snap_element
        bpy.context.scene.tool_settings.snap_element = 'FACE'
        bpy.context.scene.tool_settings.use_snap_align_rotation = True
        bpy.context.scene.tool_settings.use_snap_project = True
 
    else:
        bpy.context.scene.tool_settings.snap_element = AM.snap_mod
        bpy.context.scene.tool_settings.use_snap = False
        AM.snap_mod = ""
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def import_mesh_from_asset_management():
    """ Import the selected asset """
 
    AM = bpy.context.window_manager.asset_m
 
    object_to_import = bpy.context.window_manager.AssetM_previews.rsplit(".", 1)[0]
 
    blendfile = join(get_directory("blends"), object_to_import + ".blend")
    source_files = [blendfile]
    scn = bpy.context.scene
    imported_list = list()
    
    with bpy.data.libraries.load(blendfile) as (data_from, data_to):
        object_list = [obj for obj in data_from.objects]
        data_to.objects = data_from.objects
        if data_from.groups:
            data_to.groups = data_from.groups
 
    bpy.ops.object.select_all(action='DESELECT')
 
    layers = [(obj, layer) for obj in data_from.objects for layer in range(0, 20) if obj.layers[layer]]
 
    for obj in bpy.data.objects:
        for data in object_list:
            if obj.name.startswith(data) and obj.name not in bpy.context.scene.objects:
                idx = object_list.index(data)
                scn.objects.link(obj)
                obj.select = True
 
                if not AM.active_layer:
                    obj.layers = [layer == layers[idx][1] for layer in range(20)]  
         
                else:
                    obj.layers = [layer == scn.active_layer for layer in range(20)]
                
                imported_list.append(obj)
    
    if hasattr(bpy.types, "OBJECT_OT_grouper_dupper_initialize"):
        selectedEmpties = [x for x in imported_list if x.dupli_group and x.type == 'EMPTY']
        if selectedEmpties:
            bpy.ops.object.grouper_dupper_initialize()
    
    if AM.existing_group:
        bpy.ops.object.clean_groups()
 
    if AM.existing_material:
        bpy.ops.material.link_to_base_names()
 
    bpy.context.scene.objects.active = imported_list[0]
 
    if not AM.active_layer:
        for item in layers:
            scn.layers[item[1]]=True
 
    if len(imported_list) == 1:
        imported_list[0].location = bpy.context.scene.cursor_location
 
    else:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        bpy.context.active_object.name = "main_tmp"
        main = bpy.data.objects["main_tmp"]
        main.draw_type = 'WIRE'
        for obj in imported_list:
            if not obj.parent:
                obj.parent = main
        bpy.ops.object.select_all(action='DESELECT')
        main.select=True
        main.location = bpy.context.scene.cursor_location
    
    del(imported_list[:])
    
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def preview_add_to_selection():
    """ Positioning the object on the selection """
 
    multi = False
    use_duplicate_mesh = bpy.context.user_preferences.edit.use_duplicate_mesh
 
    bpy.context.user_preferences.edit.use_duplicate_mesh = True
 
    if bpy.context.object:          
        if bpy.context.object.mode == 'OBJECT':
            if bpy.context.selected_objects:
                cursor_location = bpy.context.scene.cursor_location.copy()
                bpy.ops.view3d.snap_cursor_to_selected() 
                import_mesh_from_asset_management()
                bpy.context.scene.cursor_location = cursor_location
            else:
                import_mesh_from_asset_management()
            
            if bpy.context.active_object.name == "main_tmp":
                objects = bpy.context.active_object.children
                bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                bpy.ops.object.delete()
                if objects:
                    for obj in objects:
                        obj.select=True
                    bpy.context.scene.objects.active = objects[0]
 
        elif bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            obj_main = bpy.context.active_object
 
            selected_face = [f for f in obj_main.data.polygons if f.select]
 
            if selected_face:
                obj_list = []
                multi_list = []
                bpy.ops.object.select_all(action='DESELECT')
                obj_main.select=True
 
                bpy.ops.object.duplicate()
                bpy.context.active_object.name = "Dummy"
                obj = bpy.context.active_object
                bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
 
                copy_cursor = bpy.context.scene.cursor_location.copy()
 
                mat_world = obj.matrix_world
                up = Vector((0, 0, 1))
                mesh = obj.data
 
                for face in mesh.polygons:
                    if face.select:
                        loc = mat_world * Vector(face.center)
                        quat = face.normal.to_track_quat('Z', 'Y')
                        quat.rotate(mat_world)
 
                        import_mesh_from_asset_management()
 
                        bpy.context.object.matrix_world *= quat.to_matrix().to_4x4()
 
                        bpy.context.active_object.location = loc
                        
                        if bpy.context.active_object.name != "main_tmp":
                            obj_list.append(bpy.context.object.name)
 
                        if bpy.context.active_object.name == "main_tmp":
                            objects = bpy.context.active_object.children
                            multi_list.append(objects[0])
                            bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
                            bpy.ops.object.delete()
                        
                        else:
                            obj_list.append(bpy.context.object.name)
                            
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects["Dummy"].select=True
                bpy.ops.object.delete()
                
                if obj_list:
                    bpy.context.scene.objects.active = bpy.data.objects[obj_list[0]]
     
                    for obj in obj_list[1:]:
                        bpy.data.objects[obj].select=True
                        bpy.ops.object.make_links_data(type='OBDATA')
                        bpy.ops.object.make_links_data(type='MODIFIERS')
                        bpy.data.objects[obj].select=False
     
                    del(obj_list[:])
                
                    bpy.context.active_object.select=True
                
                if multi_list:
                    for obj in multi_list:
                        obj.select = True
                    bpy.context.scene.objects.active = multi_list[0]
                    del(multi_list[:])
                     
                bpy.context.scene.cursor_location = copy_cursor
                bpy.context.space_data.transform_orientation = 'LOCAL'
 
            else:
                bpy.ops.object.mode_set(mode='EDIT')
 
    else:
        import_mesh_from_asset_management()
        if bpy.context.active_object.name == "main_tmp":
            objects = bpy.context.active_object.children
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
            bpy.ops.object.delete()
            if objects:
                for obj in objects:
                    obj.select=True
                bpy.context.scene.objects.active = objects[0]
 
    bpy.context.user_preferences.edit.use_duplicate_mesh = use_duplicate_mesh
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def get_groups(asset):
    """ Return the groups list of the asset """
 
    if asset != "EMPTY":
        AM = bpy.context.window_manager.asset_m
        if not AM.groups_list:
            blendfile = join(get_directory("blends"), asset + ".blend") 
 
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                if data_from.groups:
                    for group in data_from.groups:
                        AM.groups_list.append(group)
                else:
                    AM.groups_list.append("empty")
 
            return AM.groups_list  
 
        else:
            return AM.groups_list
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def get_scripts(asset):
    """ Return the scripts list of the asset """
 
    if asset != "EMPTY":
        AM = bpy.context.window_manager.asset_m
        if not AM.script_list:
            blendfile = join(get_directory("blends"), asset + ".blend")
 
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                if data_from.texts:
                    for text in data_from.texts:
                        AM.script_list.append(text)
                else:
                    AM.script_list.append("empty")
 
            return AM.script_list
 
        else:
            return AM.script_list
